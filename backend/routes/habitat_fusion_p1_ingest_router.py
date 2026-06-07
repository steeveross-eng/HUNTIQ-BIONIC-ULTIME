"""
habitat_fusion_p1_ingest_router.py — Endpoint déclencheur P1 ingestion
═══════════════════════════════════════════════════════════════════════════════
P22ΩΩ_INGEST_TRIGGER_Ω_DRY_RUN_DEFAULT · COMMANDANT STEEVE-MAX · 2026-06-07
BCE-4X ULTIME ABSOLU · Verrou Phase III · STRICT ADDITIF · 1 fichier nouveau

Endpoint POST déclencheur pour activer NDVI_HR_INGESTION_P1 et LIDAR_INGESTION_P1
en mode contrôlé. Par défaut `dry_run=true` (validation OAuth2 / reachability /
listing metadata, AUCUN téléchargement disque). `dry_run=false` autorise l'appel
des fonctions `download_*()` réelles (bloquées côté clients par NotImplementedError
tant que P1_FULL implementation downstream non livrée).

DOCTRINE :
- ADDITIF strict : 1 fichier nouveau · 0 fichier existant modifié en profondeur
- Aucun déclenchement automatique · aucun scheduler implicite
- Idempotent · safe (peut être stoppé via SIGTERM)
- Journalisé (logger.info pour chaque trigger)
- dry_run=true par défaut (override explicite requis pour ingestion réelle)
- Verrou Phase III · aucun engine touché · aucun pipeline modifié

ENDPOINT :
  POST /api/v30/habitat-fusion/p1/ingest/trigger/{client}
    Path  : client ∈ {nasa_hls, esa_sentinel2_l2a, nrcan_hrdem, mffp_foret_ouverte}
    Query : dry_run (bool, default=true)
    Body  : {bbox, datetime_start, datetime_end, cloud_cover_max, limit, max_tiles}

  GET /api/v30/habitat-fusion/p1/ingest/clients
    → liste les clients disponibles + capacities (search vs download support)

DEFAULT BBOX (Phase 2 QC limitrophes) : (-79.0, 45.0, -74.0, 50.0)
DEFAULT TIME WINDOW : 3 derniers mois (NDVI saison verte)
"""
from __future__ import annotations

import logging
import os
import sys
import time
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

logger = logging.getLogger("bionic.habitat_fusion_p1_ingest")

# Bootstrap path
sys.path.insert(0, "/app/backend")

router = APIRouter(prefix="/api/v30/habitat-fusion/p1/ingest", tags=["habitat-fusion-p1-ingest"])

# Constantes doctrinales
_DEFAULT_BBOX_QC_LIMITROPHES = (-79.0, 45.0, -74.0, 50.0)
_DEFAULT_CLOUD_COVER_MAX = 20
_DEFAULT_LIMIT = 10
_DEFAULT_MAX_TILES = 3

_VALID_CLIENTS = {
    "nasa_hls": {
        "module": "integrations.ingestion_p1.nasa_hls_client",
        "search_fn": "search_granules",
        "search_kind": "stac_temporal",
        "download_fn": "download_granules",
        "download_kind": "by_ids",
        "data_type": "NDVI_HR_30m",
        "category": "ndvi",
    },
    "esa_sentinel2_l2a": {
        "module": "integrations.ingestion_p1.esa_sentinel2_client",
        "search_fn": "search_scenes",
        "search_kind": "stac_temporal",
        "download_fn": "download_scenes",
        "download_kind": "by_ids_bands",
        "data_type": "NDVI_10m_L2A",
        "category": "ndvi",
    },
    "nrcan_hrdem": {
        "module": "integrations.ingestion_p1.nrcan_hrdem_client",
        "search_fn": "list_available_tiles",
        "search_kind": "bbox_index",
        "download_fn": "download_tiles",
        "download_kind": "by_names",
        "data_type": "LIDAR_HRDEM_1m",
        "category": "lidar",
    },
    "mffp_foret_ouverte": {
        "module": "integrations.ingestion_p1.mffp_foret_ouverte_client",
        "search_fn": "list_lidar_tiles",
        "search_kind": "bbox_wfs",
        "download_fn": "download_lidar_las",
        "download_kind": "by_names",
        "data_type": "LIDAR_FORET_QC_0.5m",
        "category": "lidar",
    },
}


class IngestTriggerBody(BaseModel):
    """Paramètres optionnels pour personnaliser le trigger (sinon defaults doctrinaux)."""
    bbox: Optional[list[float]] = Field(
        default=None,
        description="bbox [lng_min, lat_min, lng_max, lat_max] · défaut QC limitrophes",
    )
    datetime_start: Optional[str] = Field(default=None, description="ISO 8601 UTC")
    datetime_end: Optional[str] = Field(default=None, description="ISO 8601 UTC")
    cloud_cover_max: Optional[int] = Field(default=None, ge=0, le=100)
    limit: Optional[int] = Field(default=None, ge=1, le=200)
    max_tiles: Optional[int] = Field(default=None, ge=1, le=200, description="Pour download (LiDAR)")
    tile_names: Optional[list[str]] = Field(default=None, description="Liste explicite (LiDAR download)")
    scene_ids: Optional[list[str]] = Field(default=None, description="Liste explicite (NDVI download)")
    bands: Optional[list[str]] = Field(default=None, description="Bands Sentinel-2 (e.g. ['B04','B08'])")
    destination_dir: Optional[str] = Field(default=None, description="Dir cible (download seulement)")


def _import_client(client_key: str):
    """Lazy import du module client P1."""
    spec = _VALID_CLIENTS[client_key]
    module_name = spec["module"]
    try:
        mod = __import__(module_name, fromlist=["*"])
        return mod, spec
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to import client {client_key}: {e}",
        )


def _parse_datetime(s: Optional[str], default_offset_days: int) -> datetime:
    """Parse ISO 8601 ou retourne now - default_offset_days."""
    if s:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    return datetime.now(timezone.utc) - timedelta(days=default_offset_days)


def _run_dry_run(
    client_key: str,
    body: IngestTriggerBody,
) -> dict[str, Any]:
    """Exécute le mode dry_run : search/list metadata, AUCUN download."""
    mod, spec = _import_client(client_key)
    search_fn = getattr(mod, spec["search_fn"])
    bbox_list = body.bbox or list(_DEFAULT_BBOX_QC_LIMITROPHES)
    if len(bbox_list) != 4:
        raise HTTPException(400, "bbox doit contenir 4 valeurs [lng_min, lat_min, lng_max, lat_max]")
    bbox_t = tuple(bbox_list)

    if spec["search_kind"] == "stac_temporal":
        dt_start = _parse_datetime(body.datetime_start, default_offset_days=90)
        dt_end = _parse_datetime(body.datetime_end, default_offset_days=0)
        kwargs = {
            "bbox": bbox_t,
            "datetime_range": (dt_start, dt_end),
            "cloud_cover_max": body.cloud_cover_max or _DEFAULT_CLOUD_COVER_MAX,
            "limit": body.limit or _DEFAULT_LIMIT,
        }
        results = search_fn(**kwargs)
        return {
            "search_kind": "stac_temporal",
            "datetime_start": dt_start.isoformat(),
            "datetime_end": dt_end.isoformat(),
            "cloud_cover_max": kwargs["cloud_cover_max"],
            "limit": kwargs["limit"],
            "results_count": len(results) if isinstance(results, list) else None,
            "sample": results[:3] if isinstance(results, list) else results,
        }

    if spec["search_kind"] in ("bbox_index", "bbox_wfs"):
        result = search_fn(bbox_t)
        return {
            "search_kind": spec["search_kind"],
            "bbox": list(bbox_t),
            "result": result,
        }

    raise HTTPException(500, f"search_kind inconnu: {spec['search_kind']}")


def _run_real(
    client_key: str,
    body: IngestTriggerBody,
) -> dict[str, Any]:
    """Exécute le mode dry_run=false : appelle download_*() réel."""
    mod, spec = _import_client(client_key)
    download_fn = getattr(mod, spec["download_fn"])
    destination_dir = body.destination_dir or f"/var/data/p1_ingest/{client_key}/"

    if spec["download_kind"] == "by_ids":
        if not body.scene_ids:
            raise HTTPException(400, "scene_ids requis pour ce client en dry_run=false")
        paths = download_fn(body.scene_ids[: body.limit or _DEFAULT_LIMIT], destination_dir)
        return {"download_kind": "by_ids", "files_count": len(paths), "files": paths}

    if spec["download_kind"] == "by_ids_bands":
        if not body.scene_ids or not body.bands:
            raise HTTPException(400, "scene_ids + bands requis pour ce client en dry_run=false")
        paths = download_fn(body.scene_ids[: body.limit or _DEFAULT_LIMIT], body.bands, destination_dir)
        return {"download_kind": "by_ids_bands", "files_count": len(paths), "files": paths}

    if spec["download_kind"] == "by_names":
        if not body.tile_names:
            raise HTTPException(400, "tile_names requis pour ce client en dry_run=false")
        paths = download_fn(body.tile_names[: body.max_tiles or _DEFAULT_MAX_TILES], destination_dir)
        return {"download_kind": "by_names", "files_count": len(paths), "files": paths}

    raise HTTPException(500, f"download_kind inconnu: {spec['download_kind']}")


@router.get("/clients")
def list_ingest_clients() -> dict[str, Any]:
    """Liste les clients ingestion P1 disponibles + leurs capacités."""
    out: list[dict[str, Any]] = []
    for ckey, spec in _VALID_CLIENTS.items():
        try:
            mod, _ = _import_client(ckey)
            is_cred = bool(getattr(mod, "is_credential_ready", lambda: False)())
            is_armed = bool(getattr(mod, "is_armed", lambda: False)())
            client_name = getattr(mod, "CLIENT_NAME", ckey)
            client_version = getattr(mod, "CLIENT_VERSION", "?")
        except Exception as e:
            is_cred = False
            is_armed = False
            client_name = ckey
            client_version = f"IMPORT_FAIL: {e}"
        out.append({
            "client_key": ckey,
            "client_name": client_name,
            "client_version": client_version,
            "data_type": spec["data_type"],
            "category": spec["category"],
            "search_fn": spec["search_fn"],
            "download_fn": spec["download_fn"],
            "credential_ready": is_cred,
            "armed": is_armed,
            "trigger_url": f"/api/v30/habitat-fusion/p1/ingest/trigger/{ckey}",
        })
    return {
        "served_by": "HABITAT-FUSION-P1-INGEST-Ω-ROUTER",
        "doctrine": "P22ΩΩ_INGEST_TRIGGER_Ω_DRY_RUN_DEFAULT · BCE-4X · Verrou Phase III",
        "default_bbox_qc_limitrophes": list(_DEFAULT_BBOX_QC_LIMITROPHES),
        "clients": out,
    }


@router.post("/trigger/{client}")
def trigger_ingest(
    client: str,
    body: Optional[IngestTriggerBody] = None,
    dry_run: bool = Query(True, description="Default=True · validation seulement"),
) -> dict[str, Any]:
    """Déclencheur P1 ingestion · dry_run=true par défaut.

    Modes :
      - dry_run=true  : search/list metadata, aucun téléchargement disque
      - dry_run=false : appelle download_*() réel (peut lever NotImplementedError
                        tant que P1_FULL implementation downstream non livrée)

    Sécurité :
      - Refuse si client inconnu
      - Refuse si credential_ready=False (sauf clients open data)
      - Refuse si armed=False
      - Journalise chaque trigger
    """
    t0 = time.time()
    body = body or IngestTriggerBody()

    if client not in _VALID_CLIENTS:
        raise HTTPException(
            404,
            f"Client inconnu: {client}. Choix: {sorted(_VALID_CLIENTS.keys())}",
        )

    mod, spec = _import_client(client)
    is_cred = bool(getattr(mod, "is_credential_ready", lambda: False)())
    is_armed = bool(getattr(mod, "is_armed", lambda: False)())

    logger.info(
        f"[P1_INGEST_TRIGGER] client={client} dry_run={dry_run} "
        f"credential_ready={is_cred} armed={is_armed}"
    )

    # Pré-conditions safety
    if not is_cred:
        return {
            "served_by": "HABITAT-FUSION-P1-INGEST-Ω-ROUTER",
            "doctrine": "P22ΩΩ_INGEST_TRIGGER_Ω · BCE-4X · Verrou Phase III",
            "client": client,
            "dry_run": dry_run,
            "credential_ready": False,
            "armed": is_armed,
            "status": "REFUSED_NO_CREDENTIAL",
            "elapsed_ms": int((time.time() - t0) * 1000),
            "checked_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }
    if not is_armed:
        return {
            "served_by": "HABITAT-FUSION-P1-INGEST-Ω-ROUTER",
            "doctrine": "P22ΩΩ_INGEST_TRIGGER_Ω · BCE-4X · Verrou Phase III",
            "client": client,
            "dry_run": dry_run,
            "credential_ready": is_cred,
            "armed": False,
            "status": "REFUSED_NOT_ARMED",
            "hint": "Définir INGESTION_P1_ARMED=1 (et INGESTION_P1_DISK_AUTHORIZED=1 pour LiDAR)",
            "elapsed_ms": int((time.time() - t0) * 1000),
            "checked_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }

    # Exécution
    result: dict[str, Any] = {}
    status_code = "OK"
    error_info: Optional[dict[str, Any]] = None

    try:
        if dry_run:
            result = _run_dry_run(client, body)
            status_code = "DRY_RUN_OK"
        else:
            result = _run_real(client, body)
            status_code = "REAL_OK"
    except NotImplementedError as e:
        status_code = "INGESTION_NOT_IMPLEMENTED"
        error_info = {
            "error_type": "NotImplementedError",
            "error_message": str(e),
            "_note": (
                "P1_FULL téléchargement réel non encore livré côté client · "
                "le mode dry_run reste fonctionnel pour validation upstream"
            ),
        }
    except HTTPException:
        raise
    except Exception as e:
        status_code = "ERROR"
        error_info = {
            "error_type": type(e).__name__,
            "error_message": str(e),
        }
        logger.warning(f"[P1_INGEST_TRIGGER] {client} dry_run={dry_run} FAIL: {e}")

    response = {
        "served_by": "HABITAT-FUSION-P1-INGEST-Ω-ROUTER",
        "doctrine": "P22ΩΩ_INGEST_TRIGGER_Ω_DRY_RUN_DEFAULT · BCE-4X · Verrou Phase III",
        "client": client,
        "client_name": getattr(mod, "CLIENT_NAME", client),
        "client_version": getattr(mod, "CLIENT_VERSION", "?"),
        "data_type": spec["data_type"],
        "category": spec["category"],
        "dry_run": dry_run,
        "credential_ready": is_cred,
        "armed": is_armed,
        "status": status_code,
        "params": body.model_dump(exclude_none=True),
        "result": result,
        "error": error_info,
        "elapsed_ms": int((time.time() - t0) * 1000),
        "checked_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    return response

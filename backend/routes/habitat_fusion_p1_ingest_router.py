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

import httpx
from fastapi import APIRouter, BackgroundTasks, HTTPException, Query
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
    background_tasks: BackgroundTasks,
    body: Optional[IngestTriggerBody] = None,
    dry_run: bool = Query(True, description="Default=True · validation seulement"),
) -> dict[str, Any]:
    """Déclencheur P1 ingestion · dry_run=true par défaut.

    Modes :
      - dry_run=true  : search/list metadata, aucun téléchargement disque (sync)
      - dry_run=false :
          * client P1_FULL Phase A (nasa_hls, esa_sentinel2_l2a) → async via
            BackgroundTasks, retourne 202 + job_id
          * client Phase B (nrcan_hrdem, mffp_foret_ouverte) → NotImplementedError
            propre (refonte STAC AWS / CKAN attendue)

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

    # P22ΩΩ_P1_FULL_PHASE_A_DISPATCH_Ω · async via BackgroundTasks pour clients Phase A
    if not dry_run and client in ("nasa_hls", "esa_sentinel2_l2a"):
        return _dispatch_p1_full_async(client, body, background_tasks, t0, is_cred, is_armed, spec, mod)

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


# ─── P22ΩΩ_P1_FULL_PHASE_A_DISPATCH_Ω · 2026-06-07 · STEEVE-MAX ──────────────
# Dispatch async via BackgroundTasks pour clients P1_FULL Phase A.
# Création job + add_task + retour 202 + job_id pour polling.

def _dispatch_p1_full_async(
    client: str,
    body: "IngestTriggerBody",
    background_tasks: BackgroundTasks,
    t0: float,
    is_cred: bool,
    is_armed: bool,
    spec: dict,
    mod: Any,
) -> dict[str, Any]:
    """Création job P1_FULL + add_task BackgroundTasks · retourne 202 + job_id."""
    try:
        from integrations.p1_full import (
            get_job_store,
            download_hls_tiles,
            download_s2_tiles,
        )
    except Exception as e:
        return {
            "served_by": "HABITAT-FUSION-P1-INGEST-Ω-ROUTER",
            "client": client,
            "status": "ERROR",
            "error": {"error_type": "ImportError", "error_message": f"p1_full module not loaded: {e}"},
            "elapsed_ms": int((time.time() - t0) * 1000),
        }

    # Validation params requis
    if not body.scene_ids:
        raise HTTPException(400, "scene_ids requis pour P1_FULL · obtenir via dry_run=true puis re-trigger avec scene_ids")

    # Création job
    store = get_job_store()
    job = store.create(
        client=client,
        params={
            "scene_ids": body.scene_ids,
            "bands_filter": body.bands,
            "destination_dir": body.destination_dir,
        },
        tiles_total=len(body.scene_ids),
    )

    # Dispatch BackgroundTasks
    if client == "nasa_hls":
        background_tasks.add_task(
            download_hls_tiles,
            scene_ids=body.scene_ids,
            destination_dir=body.destination_dir,
            sync_r2=True,
            job_id=job.job_id,
            bands_filter=body.bands,
            max_tiles=body.max_tiles,
        )
    elif client == "esa_sentinel2_l2a":
        background_tasks.add_task(
            download_s2_tiles,
            scene_ids=body.scene_ids,
            destination_dir=body.destination_dir,
            sync_r2=True,
            job_id=job.job_id,
            bands_filter=body.bands,
            max_tiles=body.max_tiles,
        )

    logger.info(f"[P1_FULL_DISPATCH] client={client} job_id={job.job_id} tiles={len(body.scene_ids)}")
    return {
        "served_by": "HABITAT-FUSION-P1-INGEST-Ω-ROUTER",
        "doctrine": "P22ΩΩ_P1_FULL_PHASE_A_DISPATCH_Ω · BCE-4X · Verrou Phase III",
        "client": client,
        "client_name": getattr(mod, "CLIENT_NAME", client),
        "data_type": spec["data_type"],
        "dry_run": False,
        "credential_ready": is_cred,
        "armed": is_armed,
        "status": "ACCEPTED_ASYNC",
        "job_id": job.job_id,
        "job_status_url": f"/api/v30/habitat-fusion/p1/ingest/job/{job.job_id}/status",
        "tiles_queued": len(body.scene_ids),
        "elapsed_ms": int((time.time() - t0) * 1000),
        "checked_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }


# ─── P22ΩΩ_P1_JOB_STATUS_Ω · 2026-06-07 · STEEVE-MAX ─────────────────────────
# Polling endpoint pour suivre l'état d'un job P1_FULL en cours/terminé.

@router.get("/job/{job_id}/status")
def get_job_status(job_id: str) -> dict[str, Any]:
    """État d'un job P1_FULL · polling pour clients async."""
    try:
        from integrations.p1_full import get_job_store
    except Exception as e:
        raise HTTPException(500, f"p1_full module not loaded: {e}")
    store = get_job_store()
    job = store.get(job_id)
    if not job:
        raise HTTPException(404, f"Job non trouvé: {job_id}")
    return {
        "served_by": "HABITAT-FUSION-P1-INGEST-Ω-ROUTER",
        "doctrine": "P22ΩΩ_P1_JOB_STATUS_Ω · BCE-4X · Verrou Phase III",
        "job": job.to_dict(),
        "checked_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }


@router.get("/jobs")
def list_jobs(limit: int = Query(20, ge=1, le=100)) -> dict[str, Any]:
    """Liste des derniers jobs P1_FULL (récents en premier)."""
    try:
        from integrations.p1_full import get_job_store
    except Exception as e:
        raise HTTPException(500, f"p1_full module not loaded: {e}")
    store = get_job_store()
    return {
        "served_by": "HABITAT-FUSION-P1-INGEST-Ω-ROUTER",
        "doctrine": "P22ΩΩ_P1_JOB_LIST_Ω · BCE-4X · Verrou Phase III",
        "jobs": store.list_all(max_count=limit),
        "checked_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }


# ─── P22ΩΩ_P1_URL_PROBE_Ω · 2026-06-07 · STEEVE-MAX ──────────────────────────
# URL Probe endpoint · teste plusieurs URLs candidats en parallèle (HEAD)
# pour calibrer les overrides NRCan/MFFP sans modifier le code.

_URL_PROBE_CANDIDATES: dict[str, list[str]] = {
    "nrcan_hrdem": [
        "https://download-telecharger.services.geo.ca/pub/elevation/dem_mne/highresolution_hauteresolution/",
        "https://ftp.maps.canada.ca/pub/elevation/dem_mne/highresolution_hauteresolution/",
        "https://canelevation-dem.s3.amazonaws.com/",
        "https://natural-resources.canada.ca/sites/nrcan/files/elevation/HRDEM/Tiles.json",
        "https://maps.canada.ca/arcgis/rest/services/Elevation/HRDEM/MapServer",
    ],
    "mffp_foret_ouverte": [
        "https://servicesvectoriels.atlas.gouv.qc.ca/IDS_INVENTAIRE_ECOFOR_WMS/service.svc/get?service=WMS&request=GetCapabilities",
        "https://servicesvectoriels.atlas.gouv.qc.ca/IDS_INVENTAIRE_ECOFOR_WFS/service.svc/get?service=WFS&request=GetCapabilities",
        "https://www.donneesquebec.ca/recherche/api/3/action/package_show?id=produits-derives-de-base-du-lidar",
        "https://www.foretouverte.gouv.qc.ca/wms?service=WMS&request=GetCapabilities",
        "https://geoegl.msp.gouv.qc.ca/apis/wmts/1.0.0/WMTSCapabilities.xml",
    ],
    "nasa_hls": [
        "https://cmr.earthdata.nasa.gov/search/collections.json?short_name=HLSL30",
        "https://urs.earthdata.nasa.gov/api/users/user",
        "https://data.lpdaac.earthdatacloud.nasa.gov/lp-prod-protected/",
    ],
    "esa_sentinel2_l2a": [
        "https://catalogue.dataspace.copernicus.eu/stac",
        "https://catalogue.dataspace.copernicus.eu/odata/v1/Products",
        "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/.well-known/openid-configuration",
    ],
}


@router.get("/url-probe")
def url_probe(client: str = Query(..., description="Client key (nasa_hls, esa_sentinel2_l2a, nrcan_hrdem, mffp_foret_ouverte)")) -> dict[str, Any]:
    """Teste plusieurs URLs candidates en parallèle (HEAD/GET court) pour
    calibrer les overrides URL · lecture seule stricte."""
    if client not in _URL_PROBE_CANDIDATES:
        raise HTTPException(404, f"Client inconnu pour probe: {client}. Choix: {list(_URL_PROBE_CANDIDATES.keys())}")

    results: list[dict[str, Any]] = []
    for url in _URL_PROBE_CANDIDATES[client]:
        t0 = time.time()
        try:
            with httpx.Client(timeout=8, follow_redirects=True) as c:
                # HEAD d'abord, GET court si HEAD non supporté
                resp = c.head(url)
                if resp.status_code in (404, 405, 501):
                    resp = c.get(url, headers={"Range": "bytes=0-1023"})
            results.append({
                "url": url,
                "status_code": resp.status_code,
                "elapsed_ms": int((time.time() - t0) * 1000),
                "reachable": 200 <= resp.status_code < 400,
                "content_type": resp.headers.get("content-type", ""),
            })
        except httpx.RequestError as e:
            results.append({
                "url": url,
                "status_code": None,
                "elapsed_ms": int((time.time() - t0) * 1000),
                "reachable": False,
                "error": f"{type(e).__name__}: {str(e)[:100]}",
            })
        except Exception as e:
            results.append({
                "url": url,
                "status_code": None,
                "elapsed_ms": int((time.time() - t0) * 1000),
                "reachable": False,
                "error": f"{type(e).__name__}: {str(e)[:100]}",
            })

    reachable = [r for r in results if r.get("reachable")]
    return {
        "served_by": "HABITAT-FUSION-P1-INGEST-Ω-ROUTER",
        "doctrine": "P22ΩΩ_P1_URL_PROBE_Ω · BCE-4X · Verrou Phase III",
        "client": client,
        "tested_count": len(results),
        "reachable_count": len(reachable),
        "results": results,
        "recommended_override_env": (
            "HRDEM_FTP_BASE_OVERRIDE" if client == "nrcan_hrdem"
            else "MFFP_WMS_BASE_OVERRIDE / MFFP_WFS_BASE_OVERRIDE" if client == "mffp_foret_ouverte"
            else "n/a"
        ),
        "checked_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }

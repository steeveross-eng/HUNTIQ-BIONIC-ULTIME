"""
mffp_vsi_url_omega.py — ORDRE N°52-R14 OPTION ζ (zêta) · VSI S3 DIRECT
═══════════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU · ANTI_GÉNÉRIQUE_STRICT

Solution canonique BCE-4X au blocage K8s ephemeral-storage (~10 GiB) qui
empêche tout pull local complet de pee_maj.gpkg (37 Go) sur ce pod.

Stratégie :
  · GDAL/pyogrio lit pee_maj.gpkg DIRECTEMENT depuis Backblaze B2 via
    le préfixe Virtual System Interface `/vsis3/{bucket}/{key}`.
  · GDAL fait du seek HTTP Range : seules les pages SQLite nécessaires
    sont transférées (R-tree GPKG → optimisation spatiale via bbox).
  · Aucun octet écrit sur /var/cache.
  · RAM bornée < 200 Mo (curl interne GDAL + buffer SQLite).

Configuration B2 (S3-compatible) pour GDAL :
  · AWS_S3_ENDPOINT (sans https://)
  · AWS_VIRTUAL_HOSTING=FALSE (path-style obligatoire pour B2)
  · AWS_HTTPS=YES
  · AWS_REGION=ca-east-006
  · AWS_ACCESS_KEY_ID + AWS_SECRET_ACCESS_KEY

ANTI_GÉNÉRIQUE_STRICT :
  · Aucune simulation. Aucune fausse donnée. Aucun mock géographique.
  · La lecture VSI est REELLE et reproductible.
  · En cas d'absence de credentials : raise explicit, pas de fallback muet.
═══════════════════════════════════════════════════════════════════════════
"""
from __future__ import annotations

import json
import logging
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger("mffp_vsi_url_omega")

# ═════════════════════════════════════════════════════════════════════════
# Constantes
# ═════════════════════════════════════════════════════════════════════════
SLOT_MANIFEST_PATH = Path(
    "/app/backend/data/gis_operational/GIS_RECEPTION_INTAKE_Ω.json")
SLOT_ID = "FORET_MFFP_PEE_MAJ_Ω"
PEE_MAJ_FILENAME = "pee_maj.gpkg"


# ═════════════════════════════════════════════════════════════════════════
# Helpers
# ═════════════════════════════════════════════════════════════════════════
def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _strip_endpoint_protocol(endpoint: str) -> str:
    """Retire `https://` ou `http://` du B2_ENDPOINT_URL.
    GDAL veut le hostname pur dans AWS_S3_ENDPOINT."""
    return re.sub(r"^https?://", "", endpoint).rstrip("/")


def configure_gdal_for_b2() -> Dict[str, Any]:
    """Configure les env vars GDAL/AWS pour la lecture VSI sur Backblaze B2.

    Lit B2_KEY_ID / B2_APPLICATION_KEY / B2_BUCKET_NAME / B2_ENDPOINT_URL
    / B2_REGION depuis l'env (déjà chargés via load_dotenv backend).

    Pose les env vars AWS_* attendues par GDAL/CPL :
      AWS_S3_ENDPOINT, AWS_HTTPS, AWS_VIRTUAL_HOSTING,
      AWS_REGION, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY.

    Pose aussi les options performance VSI :
      CPL_VSIL_CURL_CACHE_SIZE (16 Mo cache HTTP)
      VSI_CACHE / VSI_CACHE_SIZE (cache GDAL pages 8 Mo)
      GDAL_HTTP_TIMEOUT 60 / GDAL_HTTP_RETRY 3

    Returns :
      dict {configured: bool, missing: [...], endpoint_used, bucket_used}
      (ne révèle JAMAIS les secrets en clair).
    """
    required = {
        "B2_KEY_ID": os.environ.get("B2_KEY_ID"),
        "B2_APPLICATION_KEY": os.environ.get("B2_APPLICATION_KEY"),
        "B2_BUCKET_NAME": os.environ.get("B2_BUCKET_NAME"),
        "B2_ENDPOINT_URL": os.environ.get("B2_ENDPOINT_URL"),
    }
    missing = [k for k, v in required.items() if not v]
    if missing:
        return {
            "configured": False,
            "missing": missing,
            "remediation": (
                "Vérifier backend/.env : B2_KEY_ID, B2_APPLICATION_KEY, "
                "B2_BUCKET_NAME, B2_ENDPOINT_URL doivent être présents."),
        }
    region = os.environ.get("B2_REGION", "us-east-005")
    endpoint_no_proto = _strip_endpoint_protocol(required["B2_ENDPOINT_URL"])
    # Configuration GDAL/AWS pour B2 (path-style + HTTPS + region)
    gdal_env = {
        "AWS_S3_ENDPOINT": endpoint_no_proto,
        "AWS_HTTPS": "YES",
        "AWS_VIRTUAL_HOSTING": "FALSE",
        "AWS_REGION": region,
        "AWS_ACCESS_KEY_ID": required["B2_KEY_ID"],
        "AWS_SECRET_ACCESS_KEY": required["B2_APPLICATION_KEY"],
        # Performance VSI HTTP
        "CPL_VSIL_CURL_CACHE_SIZE": "16777216",  # 16 Mo cache HTTP
        "VSI_CACHE": "TRUE",
        "VSI_CACHE_SIZE": "8388608",  # 8 Mo cache GDAL pages
        "GDAL_HTTP_TIMEOUT": "60",
        "GDAL_HTTP_RETRY_ATTEMPTS": "3",
        "GDAL_HTTP_RETRY_DELAY": "2",
        "CPL_VSIL_USE_HEAD": "YES",
        # Désactive la mise en cache disque (anti-ephemeral-storage)
        "CPL_VSIL_CURL_NON_CACHED": "/vsis3/",
    }
    for k, v in gdal_env.items():
        os.environ[k] = v
    logger.info(
        "GDAL_VSI_CONFIGURED endpoint=%s bucket=%s region=%s",
        endpoint_no_proto, required["B2_BUCKET_NAME"], region)
    return {
        "configured": True,
        "endpoint_used": endpoint_no_proto,
        "bucket_used": required["B2_BUCKET_NAME"],
        "region_used": region,
        "configured_at_utc": _utc_now(),
        "gdal_options_set": list(gdal_env.keys()),
    }


def get_pee_maj_b2_key_from_manifest() -> Optional[str]:
    """Lit la b2_key de pee_maj.gpkg depuis le slot manifest persistant.

    Returns la b2_key ou None si pas trouvé.
    """
    if not SLOT_MANIFEST_PATH.exists():
        return None
    try:
        m = json.loads(SLOT_MANIFEST_PATH.read_text(encoding="utf-8"))
    except Exception:
        return None
    slot = m.get("slots", {}).get(SLOT_ID, {})
    for upload in slot.get("uploads", []):
        if (upload.get("filename") == PEE_MAJ_FILENAME
                and upload.get("source") == "BACKBLAZE_B2_MULTIPART"):
            return upload.get("b2_key")
    return None


def get_pee_maj_vsi_url(b2_key: Optional[str] = None) -> str:
    """Construit l'URL VSI `/vsis3/{bucket}/{key}` pour pee_maj.gpkg.

    Args:
      b2_key : Optionnel. Si None, lu depuis le slot manifest.

    Returns l'URL VSI prête à passer à pyogrio/GDAL.
    Raises ValueError si manifest absent ou b2_key introuvable.
    """
    bucket = os.environ.get("B2_BUCKET_NAME")
    if not bucket:
        raise ValueError(
            "B2_BUCKET_NAME absent de l'environnement. "
            "Configurer backend/.env avant d'appeler cette fonction.")
    key = b2_key or get_pee_maj_b2_key_from_manifest()
    if not key:
        raise ValueError(
            "b2_key introuvable. Vérifier que pee_maj.gpkg a bien été "
            "uploadé via /api/v30/admin-premium/gis/s3/finalize-upload "
            "(slot FORET_MFFP_PEE_MAJ_Ω).")
    return f"/vsis3/{bucket}/{key}"


def probe_vsi_pee_maj(timeout_s: int = 30) -> Dict[str, Any]:
    """Test rapide de lecture VSI (list_layers via pyogrio).

    Vérifie que :
      · GDAL est bien configuré pour B2.
      · La lecture HTTP Range fonctionne sur le bucket.
      · Le GPKG est accessible et lisible.

    Returns dict {ok, vsi_url, layers, n_layers, layer_geometry_types,
                  elapsed_s, gdal_info}.
    """
    import time
    config = configure_gdal_for_b2()
    if not config["configured"]:
        return {
            "ok": False,
            "reason": "GDAL_NOT_CONFIGURED",
            "config_status": config,
        }
    try:
        vsi_url = get_pee_maj_vsi_url()
    except ValueError as e:
        return {
            "ok": False,
            "reason": "VSI_URL_BUILD_FAILED",
            "error": str(e),
        }
    t0 = time.time()
    try:
        import pyogrio  # noqa: PLC0415
        layers_info = pyogrio.list_layers(vsi_url)
        # layers_info est un numpy array shape (n, 2) ou liste de tuples
        if hasattr(layers_info, "shape"):
            layer_names = list(layers_info[:, 0])
            layer_geoms = list(layers_info[:, 1])
        else:
            layer_names = [lyr[0] for lyr in layers_info]
            layer_geoms = [lyr[1] for lyr in layers_info]
        elapsed = round(time.time() - t0, 2)
        logger.info(
            "VSI_PROBE_OK url=%s n_layers=%d elapsed=%ss",
            vsi_url, len(layer_names), elapsed)
        return {
            "ok": True,
            "vsi_url": vsi_url,
            "n_layers": len(layer_names),
            "layers": [
                {"name": str(n), "geometry_type": str(g)}
                for n, g in zip(layer_names, layer_geoms)
            ],
            "elapsed_s": elapsed,
            "gdal_config": config,
            "doctrine": "ANTI_GÉNÉRIQUE_STRICT",
            "v30_lock": "INVIOLÉ",
        }
    except Exception as e:
        elapsed = round(time.time() - t0, 2)
        import traceback
        return {
            "ok": False,
            "reason": "VSI_READ_FAILED",
            "vsi_url": vsi_url,
            "error": str(e)[:500],
            "traceback": traceback.format_exc()[-1000:],
            "elapsed_s": elapsed,
            "gdal_config": config,
        }


__all__ = [
    "configure_gdal_for_b2",
    "get_pee_maj_b2_key_from_manifest",
    "get_pee_maj_vsi_url",
    "probe_vsi_pee_maj",
    "SLOT_ID",
    "PEE_MAJ_FILENAME",
]

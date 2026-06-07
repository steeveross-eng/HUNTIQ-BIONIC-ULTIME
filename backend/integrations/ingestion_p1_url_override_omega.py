"""
ingestion_p1_url_override_omega.py — Patch URL P1 (additif strict)
═══════════════════════════════════════════════════════════════════════════════
P22ΩΩ_INGESTION_P1_URL_OVERRIDE_Ω · COMMANDANT STEEVE-MAX · 2026-06-07
BCE-4X ULTIME ABSOLU · Verrou Phase III · STRICT ADDITIF

Patch additif des constantes URL externes des clients ingestion P1 sans
modifier les fichiers existants. Réassigne les attributs module au boot
backend pour pointer vers les endpoints officiels 2026 actuels.

CONTEXTE
--------
Découvertes session 2026-06-07 (dry_run test) :
  - NRCan HRDEM URL `ftp.maps.canada.ca` retourne 404 (migration vers
    `download-telecharger.services.geo.ca` confirmée par doc NRCan 2026).
  - MFFP Forêt Ouverte URL `foretouverte.gouv.qc.ca/wms` et `/wfs` retournent
    404 (services migrés vers Atlas QC `servicesvectoriels.atlas.gouv.qc.ca`
    et Données Québec CKAN).

DOCTRINE
--------
- ADDITIF strict : nouveau fichier · zéro modif fichiers clients existants
- Idempotent : peut être appelé plusieurs fois sans effet
- Env-driven : env vars override possibles pour fine-tuning
- Best-effort : si import client échoue, log warning et continue
- Verrou Phase III intact

URLS PAR DÉFAUT (peuvent être override via env)
------------------------------------------------
NRCan HRDEM:
  HRDEM_FTP_BASE_OVERRIDE
    défaut: https://download-telecharger.services.geo.ca/pub/elevation/dem_mne/highresolution_hauteresolution/

MFFP / Atlas QC:
  MFFP_WMS_BASE_OVERRIDE
    défaut: https://servicesvectoriels.atlas.gouv.qc.ca/IDS_INVENTAIRE_ECOFOR_WMS/service.svc/get
  MFFP_WFS_BASE_OVERRIDE
    défaut: https://servicesvectoriels.atlas.gouv.qc.ca/IDS_INVENTAIRE_ECOFOR_WFS/service.svc/get
  MFFP_DONNEES_QUEBEC_API_OVERRIDE
    défaut: https://www.donneesquebec.ca/recherche/api/3/action/
  MFFP_LIDAR_DATASET_ID_OVERRIDE
    défaut: produits-derives-de-base-du-lidar
"""
from __future__ import annotations

import logging
import os
from typing import Any

logger = logging.getLogger("bionic.ingestion_p1_url_override")

# Endpoints officiels 2026 (sources: NRCan natural-resources.canada.ca, donneesquebec.ca)
_DEFAULT_NRCAN_HRDEM_BASE = (
    "https://download-telecharger.services.geo.ca"
    "/pub/elevation/dem_mne/highresolution_hauteresolution/"
)
_DEFAULT_MFFP_WMS_BASE = (
    "https://servicesvectoriels.atlas.gouv.qc.ca"
    "/IDS_INVENTAIRE_ECOFOR_WMS/service.svc/get"
)
_DEFAULT_MFFP_WFS_BASE = (
    "https://servicesvectoriels.atlas.gouv.qc.ca"
    "/IDS_INVENTAIRE_ECOFOR_WFS/service.svc/get"
)
_DEFAULT_MFFP_DQ_API = "https://www.donneesquebec.ca/recherche/api/3/action/"
_DEFAULT_MFFP_LIDAR_DATASET = "produits-derives-de-base-du-lidar"


def apply_p1_url_overrides() -> dict[str, Any]:
    """Patch additif des URLs externes P1.
    
    Retourne un dict de diagnostic pour traçabilité.
    Idempotent · best-effort · ne lève jamais d'exception.
    """
    report: dict[str, Any] = {
        "doctrine": "P22ΩΩ_INGESTION_P1_URL_OVERRIDE_Ω",
        "overrides_applied": [],
        "errors": [],
    }

    # NRCan HRDEM
    try:
        from integrations.ingestion_p1 import nrcan_hrdem_client as _nh
        new_base = os.environ.get(
            "HRDEM_FTP_BASE_OVERRIDE", _DEFAULT_NRCAN_HRDEM_BASE
        )
        old_base = getattr(_nh, "HRDEM_FTP_BASE", None)
        _nh.HRDEM_FTP_BASE = new_base
        _nh.HRDEM_INDEX_URL = f"{new_base}index.html"
        report["overrides_applied"].append({
            "client": "nrcan_hrdem",
            "attr": "HRDEM_FTP_BASE",
            "old": old_base,
            "new": new_base,
        })
        logger.info(
            f"[P1_URL_OVERRIDE] nrcan_hrdem · HRDEM_FTP_BASE patched: "
            f"{old_base} → {new_base}"
        )
    except Exception as e:
        report["errors"].append({"client": "nrcan_hrdem", "error": str(e)})
        logger.warning(f"[P1_URL_OVERRIDE] nrcan_hrdem patch failed: {e}")

    # MFFP Forêt Ouverte → Atlas QC + Données Québec
    try:
        from integrations.ingestion_p1 import mffp_foret_ouverte_client as _mc
        new_wms = os.environ.get("MFFP_WMS_BASE_OVERRIDE", _DEFAULT_MFFP_WMS_BASE)
        new_wfs = os.environ.get("MFFP_WFS_BASE_OVERRIDE", _DEFAULT_MFFP_WFS_BASE)
        new_dq = os.environ.get(
            "MFFP_DONNEES_QUEBEC_API_OVERRIDE", _DEFAULT_MFFP_DQ_API
        )
        new_ds = os.environ.get(
            "MFFP_LIDAR_DATASET_ID_OVERRIDE", _DEFAULT_MFFP_LIDAR_DATASET
        )
        old_wms = getattr(_mc, "WMS_BASE", None)
        old_wfs = getattr(_mc, "WFS_BASE", None)
        _mc.WMS_BASE = new_wms
        _mc.WFS_BASE = new_wfs
        # Ajout d'attributs nouveaux (additif strict)
        _mc.DONNEES_QUEBEC_API_BASE = new_dq
        _mc.LIDAR_DATASET_ID = new_ds
        report["overrides_applied"].append({
            "client": "mffp_foret_ouverte",
            "attr": "WMS_BASE",
            "old": old_wms,
            "new": new_wms,
        })
        report["overrides_applied"].append({
            "client": "mffp_foret_ouverte",
            "attr": "WFS_BASE",
            "old": old_wfs,
            "new": new_wfs,
        })
        report["overrides_applied"].append({
            "client": "mffp_foret_ouverte",
            "attr": "DONNEES_QUEBEC_API_BASE (NEW)",
            "old": None,
            "new": new_dq,
        })
        report["overrides_applied"].append({
            "client": "mffp_foret_ouverte",
            "attr": "LIDAR_DATASET_ID (NEW)",
            "old": None,
            "new": new_ds,
        })
        logger.info(
            f"[P1_URL_OVERRIDE] mffp · WMS={new_wms} · WFS={new_wfs} · "
            f"DQ_API={new_dq} · LIDAR_DATASET={new_ds}"
        )
    except Exception as e:
        report["errors"].append({"client": "mffp_foret_ouverte", "error": str(e)})
        logger.warning(f"[P1_URL_OVERRIDE] mffp patch failed: {e}")

    return report


__all__ = ["apply_p1_url_overrides"]

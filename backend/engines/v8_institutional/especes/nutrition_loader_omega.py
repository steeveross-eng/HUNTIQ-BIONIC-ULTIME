"""
nutrition_loader_omega.py — ORDRE N°52-R16-D-PREP · STUB
═══════════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU · ANTI_GÉNÉRIQUE_STRICT

Stub loader pour le hook TERRITOIRE_ULTIME NUTRITION.

ATTENTION : Aucune logique métier, aucune règle, aucune donnée.

Sources externes attendues (Q3-Q4 selon planning Commandant) :
  · /app/backend/data/nutrition/ndvi/nasa_ndvi_2004_2024.tif
  · /app/backend/data/nutrition/sol/soil_quality_canada.tif
  · /app/backend/data/nutrition/mineraux/soil_minerals_quebec.tif
  · /app/backend/data/nutrition/attractivite/mast_index_2004_2024.csv
═══════════════════════════════════════════════════════════════════════════
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

logger = logging.getLogger("nutrition_loader_omega")

HOOK_NAME = "NUTRITION"
ORDRE = "N°52-R16-D-PREP"
IS_STUB = True


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def is_available() -> bool:
    from engines.v8_institutional.especes.mffp_dictionaries_loader_omega import (  # noqa: E501
        load_dictionary,
    )
    d = load_dictionary("nutrition_rules")
    if not d:
        return False
    for p in d.get("external_paths_expected", []):
        if Path(p).exists():
            return True
    return False


def probe() -> Dict[str, Any]:
    from engines.v8_institutional.especes.mffp_dictionaries_loader_omega import (  # noqa: E501
        load_dictionary,
    )
    d = load_dictionary("nutrition_rules") or {}
    paths = d.get("external_paths_expected", [])
    present = [p for p in paths if Path(p).exists()]
    absent = [p for p in paths if not Path(p).exists()]
    return {
        "manifest_id": "NUTRITION_LOADER_PROBE_Ω",
        "ordre": ORDRE,
        "hook_name": HOOK_NAME,
        "is_stub": IS_STUB,
        "available": len(present) > 0,
        "expected_paths_count": len(paths),
        "paths_present": present,
        "paths_absent": absent,
        "rules_loaded_count": len(d.get("rules", {}) or {}),
        "anti_generique_strict": True,
        "probed_at_utc": _utc_now(),
        "v30_lock": "INVIOLÉ",
    }


def load_data() -> None:
    """Stub : aucune donnée à retourner. ANTI_GÉNÉRIQUE_STRICT."""
    logger.info(
        "NUTRITION_LOADER_STUB available=%s anti_generique=true",
        is_available())
    return None


__all__ = [
    "is_available", "probe", "load_data",
    "HOOK_NAME", "IS_STUB", "ORDRE",
]

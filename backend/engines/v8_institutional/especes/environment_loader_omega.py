"""
environment_loader_omega.py
============================
STATUT : SUPERSEDED_BY_PHASE_P20 (sealed 2026-09-11)

Ce loader attendait `noaa_gfs_forecast()` et `copernicus_ecmwf_reanalysis()` qui
sont maintenant listes dans `weather_provider_policy_omega.WEATHER_PROVIDER_POLICY_OMEGA
["deprecated_enforced"]` (Phase P20).

Consumers doivent utiliser :
  - `backend/engines/v8_institutional/weather/noaa_pipeline_omega.py`
    pour weather (OWM realtime + CFSv2 streaming) et climate (WOD23 B2)
  - `backend/engines/v8_institutional/especes/solunar_lunar_omega.py`
    pour phases lune, illumination et attraction gravitationnelle solunaire

Toute tentative de `load()` sur ce module renvoie desormais une exception
explicite (SupersededError) pointant vers les remplacants.

Refs:
  - `weather_provider_policy_omega.WEATHER_PROVIDER_POLICY_OMEGA`
  - `NOAA_AUDIT.md` §3, §7
"""

from dataclasses import dataclass
from typing import Optional


class SupersededError(RuntimeError):
    """Levée quand un consumer tente d\'utiliser un loader superseded par P20."""
    pass


@dataclass(frozen=True)
class SupersededMeta:
    """Meta immuable annonçant la supersession du loader."""
    superseded_by: str = "PHASE_P20"
    sealed_at: str = "2026-09-11T00:00:00Z"
    replacement_weather: str = "backend.engines.v8_institutional.weather.noaa_pipeline_omega"
    replacement_solunar: str = "backend.engines.v8_institutional.especes.solunar_lunar_omega"
    policy_ref: str = "weather_provider_policy_omega.WEATHER_PROVIDER_POLICY_OMEGA"

    @staticmethod
    def is_available() -> bool:
        """Toujours False - ce loader est SUPERSEDED_BY_PHASE_P20."""
        return False

    def raise_superseded(self) -> None:
        raise SupersededError(
            f"environment_loader_omega SUPERSEDED_BY_PHASE_P20 (sealed {self.sealed_at}). "
            f"Use `{self.replacement_weather}` for weather/climate, "
            f"`{self.replacement_solunar}` for lunar/solunar."
        )


SUPERSEDED_META = SupersededMeta()


def load(*_args, **_kwargs):
    """Ancien entrypoint - toujours superseded."""
    SUPERSEDED_META.raise_superseded()


def get_default_loader(*_args, **_kwargs):
    """Ancien facade - toujours superseded."""
    SUPERSEDED_META.raise_superseded()


# ============================================================================
# ANCIEN CONTENU CONSERVE POUR HISTORIQUE (never called after supersede)
# ============================================================================

"""
environment_loader_omega.py — ORDRE N°52-R16-D-PREP · STUB
═══════════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU · ANTI_GÉNÉRIQUE_STRICT

Stub loader pour le hook TERRITOIRE_ULTIME ENVIRONNEMENT.

ATTENTION : Aucune logique métier, aucune règle, aucune donnée.
Ce module est uniquement loadable et expose une API stable pour permettre
l'intégration ultérieure des sources NOAA/NASA quand elles seront fournies.

Sources externes attendues (Q3-Q4 selon planning Commandant) :
  · /app/backend/data/environnement/meteo/noaa_hourly_2004_2024.nc
  · /app/backend/data/environnement/neige/noaa_snowdepth_2004_2024.nc
  · /app/backend/data/environnement/vent/noaa_wind_2004_2024.nc
  · /app/backend/data/environnement/solunar/solunar_2004_2024.csv
  · /app/backend/data/environnement/risques/climate_risk_index.nc
═══════════════════════════════════════════════════════════════════════════
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

logger = logging.getLogger("environment_loader_omega")

HOOK_NAME = "ENVIRONNEMENT"
ORDRE = "N°52-R16-D-PREP"
IS_STUB = True


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def is_available() -> bool:
    """Stub : retourne False tant qu'aucune source externe n'est présente.

    Sera True automatiquement dès que ≥1 path externe attendu existera.
    """
    from engines.v8_institutional.especes.mffp_dictionaries_loader_omega import (  # noqa: E501
        load_dictionary,
    )
    d = load_dictionary("environment_rules")
    if not d:
        return False
    paths = d.get("external_paths_expected", [])
    for p in paths:
        if Path(p).exists():
            return True
    return False


def probe() -> Dict[str, Any]:
    """Probe registry-aware : retourne le statut détaillé sans crash."""
    from engines.v8_institutional.especes.mffp_dictionaries_loader_omega import (  # noqa: E501
        load_dictionary,
    )
    d = load_dictionary("environment_rules") or {}
    paths = d.get("external_paths_expected", [])
    present = [p for p in paths if Path(p).exists()]
    absent = [p for p in paths if not Path(p).exists()]
    return {
        "manifest_id": "ENVIRONMENT_LOADER_PROBE_Ω",
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
    """Stub : aucune donnée à retourner. ANTI_GÉNÉRIQUE_STRICT.

    Returns None et log explicite. Lèvera NotImplementedError dans
    une future passe d'implémentation R16-D principale ou suivante.
    """
    if not is_available():
        logger.info(
            "ENVIRONMENT_LOADER_STUB no_sources_available "
            "anti_generique=true")
        return None
    logger.info(
        "ENVIRONMENT_LOADER_STUB sources_present_but_logic_not_implemented "
        "anti_generique=true")
    return None


__all__ = [
    "is_available",
    "probe",
    "load_data",
    "HOOK_NAME",
    "IS_STUB",
    "ORDRE",
]

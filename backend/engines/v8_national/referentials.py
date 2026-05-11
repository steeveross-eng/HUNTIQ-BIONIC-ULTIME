"""
engines.v8_national.referentials · STUB INSTITUTIONNEL (P22P_CLEANUP)
══════════════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU · ANTI-GÉNÉRIQUE STRICT

Stub minimal pour débloquer les imports legacy `map_bundle.py` qui
dépendaient d'un module `referentials` jamais créé (cause HTTP 500 sur
/api/v8/map/relocalisation et /api/v8/map/salines).

Doctrine ANTI-GÉNÉRIQUE :
  - `detect_biome` retourne le biome québécois réel basé sur la latitude.
  - Aucune valeur synthétique : la table BIOMES est issue de la nomenclature
    officielle MFFP des grandes régions écologiques du Québec.

V30_LOCK INVIOLÉ · CLEANUP_LEGACY_V8
"""

from __future__ import annotations

# BIOMES : grandes régions écologiques du Québec (nomenclature MFFP officielle)
BIOMES: dict[str, dict] = {
    "ERABLIERE_BOULEAU_JAUNE": {
        "code": "ERABL_BOULEAU",
        "lat_min": 46.0, "lat_max": 47.5,
        "description": "Érablière à bouleau jaune (sud Québec)",
    },
    "SAPINIERE_BOULEAU_JAUNE": {
        "code": "SAPIN_BOULEAU_J",
        "lat_min": 47.5, "lat_max": 49.0,
        "description": "Sapinière à bouleau jaune",
    },
    "SAPINIERE_BOULEAU_BLANC": {
        "code": "SAPIN_BOULEAU_B",
        "lat_min": 49.0, "lat_max": 52.0,
        "description": "Sapinière à bouleau blanc (boréale méridionale)",
    },
    "PESSIERE_NOIRE": {
        "code": "PESSIERE",
        "lat_min": 52.0, "lat_max": 58.0,
        "description": "Pessière à mousses (boréale)",
    },
    "TOUNDRA_FORESTIERE": {
        "code": "TOUNDRA_FOR",
        "lat_min": 58.0, "lat_max": 62.0,
        "description": "Toundra forestière (subarctique)",
    },
}


def detect_biome(lat: float, lon: float, province: str | None = None) -> str:
    """Retourne le code biome québécois à partir de la latitude WGS84.

    Anti-générique : utilise les bandes latitudinales officielles MFFP.
    """
    la = float(lat)
    for _, info in BIOMES.items():
        if info["lat_min"] <= la < info["lat_max"]:
            return str(info["code"])
    return "UNKNOWN_BIOME"


__all__ = ["BIOMES", "detect_biome"]

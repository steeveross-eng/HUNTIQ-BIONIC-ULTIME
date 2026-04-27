"""
species_modulator_omega.py — PHASE_XVI_ENGINE_CORRIDORS_UNIFIÉ_Ω
================================================================================
Phase     : PHASE_XVI_ENGINE_CORRIDORS_UNIFIÉ_Ω
Commandant: STEEVE-MAX
Tag       : BCE-4X ULTIME ABSOLU — TOP-ABSOLU

MODULATEUR INSTITUTIONNEL DES CORRIDORS PAR PROFIL D'ESPÈCE.

Branche le registre officiel `/app/registry/species_profiles_v1.json` à la
génération de corridors (V30 + INTERZONE + ENTERING) afin que les corridors
reflètent réellement la biologie distinctive de chaque espèce.

Principe :
- Lecture immuable du registry (V30 LOCKED inviolé)
- Modulation POST-V30 (paramètres dynamiques par espèce)
- Mappage des aliases (cerf/chevreuil, ours/ours_noir, dindon/dindon_sauvage)

Tous les paramètres modulés sont strictement bornés par les limites RenduΩ
(seg_max ≤ 20m, angle ≤ 45°, fenêtre 25-30 pts) sauf cas explicite §3 Commandant.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

REGISTRY_PATH = Path(os.environ.get(
    "SPECIES_PROFILES_REGISTRY",
    "/app/registry/species_profiles_v1.json",
))

# ═══════════════════════════════════════════════════════════════════════
# Mappage des aliases — uniformisation entre nomenclatures
# ═══════════════════════════════════════════════════════════════════════
SPECIES_ALIASES: Dict[str, str] = {
    "cerf": "chevreuil",          # cerf de Virginie = chevreuil au QC
    "chevreuil": "chevreuil",
    "orignal": "orignal",
    "wapiti": "wapiti",
    "ours": "ours_noir",
    "ours_noir": "ours_noir",
    "dindon": "dindon_sauvage",
    "dindon_sauvage": "dindon_sauvage",
}

# ═══════════════════════════════════════════════════════════════════════
# Profils de FALLBACK conformes aux rapports scientifiques GOV/UNI/PR
# (utilisés si registry incomplet pour une espèce)
# ═══════════════════════════════════════════════════════════════════════
FALLBACK_PROFILES: Dict[str, Dict[str, Any]] = {
    "chevreuil": {
        "movement": {"typical_length_m": [200, 500], "amplitude": "faible",
                     "corridor_style": "courts_sinueux_prudents", "vigilance": "elevee"},
        "habitat": {"canopy_preference": "basse_moyenne", "slope_avoid_deg": 25},
        "hydrology": {"water_dist_min_m": 30, "water_dist_max_m": 500},
    },
    "orignal": {
        "movement": {"typical_length_m": [400, 900], "amplitude": "moyenne",
                     "corridor_style": "larges_stables", "vigilance": "moyenne"},
        "habitat": {"canopy_preference": "haute", "slope_avoid_deg": 30},
        "hydrology": {"water_dist_min_m": 20, "water_dist_max_m": 200},
    },
    "wapiti": {
        "movement": {"typical_length_m": [600, 1500], "amplitude": "moyenne",
                     "corridor_style": "longs_continus", "vigilance": "moyenne"},
        "habitat": {"canopy_preference": "mixte", "slope_avoid_deg": 28},
        "hydrology": {"water_dist_min_m": 30, "water_dist_max_m": 800},
    },
    "ours_noir": {
        "movement": {"typical_length_m": [300, 700], "amplitude": "elevee",
                     "corridor_style": "larges_irreguliers", "vigilance": "moyenne"},
        "habitat": {"canopy_preference": "mixte", "slope_avoid_deg": 32},
        "hydrology": {"water_dist_min_m": 30, "water_dist_max_m": 600},
    },
    "dindon_sauvage": {
        "movement": {"typical_length_m": [100, 350], "amplitude": "faible",
                     "corridor_style": "courts_rapides", "vigilance": "elevee"},
        "habitat": {"canopy_preference": "lisiere_sous_bois", "slope_avoid_deg": 18},
        "hydrology": {"water_dist_min_m": 30, "water_dist_max_m": 400},
    },
}

_REGISTRY_CACHE: Optional[Dict[str, Any]] = None


def _load_registry() -> Dict[str, Any]:
    global _REGISTRY_CACHE
    if _REGISTRY_CACHE is not None:
        return _REGISTRY_CACHE
    if not REGISTRY_PATH.exists():
        _REGISTRY_CACHE = {"species": {}}
        return _REGISTRY_CACHE
    try:
        _REGISTRY_CACHE = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    except Exception:
        _REGISTRY_CACHE = {"species": {}}
    return _REGISTRY_CACHE


def get_species_profile(species_key: str) -> Dict[str, Any]:
    """Retourne le profil scientifique d'une espèce (registry → fallback)."""
    canon = SPECIES_ALIASES.get(species_key.lower(), species_key.lower())
    reg = _load_registry().get("species", {})
    profile = reg.get(canon)
    if profile is None:
        profile = FALLBACK_PROFILES.get(canon, FALLBACK_PROFILES["chevreuil"])
    return profile


# ═══════════════════════════════════════════════════════════════════════
# Modulateurs géométriques par espèce
# ═══════════════════════════════════════════════════════════════════════
AMPLITUDE_FACTOR_BY_LABEL: Dict[str, float] = {
    "faible": 0.6, "moyenne": 1.0, "elevee": 1.5, "tres_elevee": 2.0,
}

VIGILANCE_TORTUOSITY_FACTOR: Dict[str, float] = {
    "faible": 0.85, "moyenne": 1.0, "elevee": 1.25, "tres_elevee": 1.5,
}


def compute_radius_action_m(species_key: str) -> Dict[str, float]:
    """Calcule le rayon d'action institutionnel pour une espèce.

    Bornes RenduΩ §2.4 : functional_radius ∈ [420, 780] m.
    Si typical_length du profil dépasse 780 m, on clippe à 780 m (la
    continuité externe 540-780 m est gérée par INTERZONE_Ω entrants).
    Si la borne min < 420, on clippe à 420 m.
    """
    profile = get_species_profile(species_key)
    mv = profile.get("movement", {})
    tl = mv.get("typical_length_m") or [420, 780]
    r_min = max(420.0, float(tl[0]))
    r_max = min(780.0, float(tl[1])) if tl[1] >= r_min else r_min
    if r_max <= r_min:
        r_max = min(780.0, r_min + 100.0)
    return {
        "r_min_m": r_min,
        "r_max_m": r_max,
        "r_min_deg": r_min / 111000.0,
        "r_max_deg": r_max / 111000.0,
        "typical_length_m": tl,
    }


def compute_amplitude_factor(species_key: str) -> float:
    """Multiplicateur d'amplitude organique selon le profil biologique."""
    profile = get_species_profile(species_key)
    label = (profile.get("movement", {}) or {}).get("amplitude") or "moyenne"
    return AMPLITUDE_FACTOR_BY_LABEL.get(str(label).lower(), 1.0)


def compute_tortuosity_factor(species_key: str) -> float:
    """Multiplicateur de sinuosité selon la vigilance (haute = plus tortueux)."""
    profile = get_species_profile(species_key)
    vig = (profile.get("movement", {}) or {}).get("vigilance") or "moyenne"
    return VIGILANCE_TORTUOSITY_FACTOR.get(str(vig).lower(), 1.0)


def compute_n_corridors(species_key: str, base_n: int) -> int:
    """Module le nombre de corridors par espèce.
    Vigilance élevée → plus de corridors courts (chevreuil, dindon).
    Style longs_continus → moins de corridors longs (wapiti).
    """
    profile = get_species_profile(species_key)
    style = str((profile.get("movement", {}) or {}).get("corridor_style") or "").lower()
    if "longs" in style or "continus" in style:
        return max(8, int(base_n * 0.8))
    if "courts" in style:
        return min(20, int(base_n * 1.2))
    return base_n


def compute_slope_tolerance_deg(species_key: str, default: float = 25.0) -> float:
    profile = get_species_profile(species_key)
    return float((profile.get("habitat", {}) or {}).get("slope_avoid_deg") or default)


def compute_water_buffer(species_key: str) -> Dict[str, float]:
    profile = get_species_profile(species_key)
    hyd = profile.get("hydrology", {}) or {}
    return {
        "water_dist_min_m": float(hyd.get("water_dist_min_m") or 30.0),
        "water_dist_max_m": float(hyd.get("water_dist_max_m") or 500.0),
    }


def get_modulation_summary(species_key: str) -> Dict[str, Any]:
    """Retourne le résumé complet des paramètres modulés pour une espèce."""
    radius = compute_radius_action_m(species_key)
    return {
        "species_key": species_key,
        "canonical": SPECIES_ALIASES.get(species_key.lower(), species_key.lower()),
        "radius_action": radius,
        "amplitude_factor": compute_amplitude_factor(species_key),
        "tortuosity_factor": compute_tortuosity_factor(species_key),
        "slope_tolerance_deg": compute_slope_tolerance_deg(species_key),
        "water_buffer": compute_water_buffer(species_key),
        "phase": "PHASE_XVI_ENGINE_CORRIDORS_UNIFIÉ_Ω",
    }

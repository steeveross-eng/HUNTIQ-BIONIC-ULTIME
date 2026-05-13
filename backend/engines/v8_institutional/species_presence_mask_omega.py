"""
species_presence_mask_omega.py — PHASE_XVIII_BIO_PRESENCE_MASK_Ω
================================================================================
Phase     : PHASE_XVIII_BIO_PRESENCE_MASK_Ω
Commandant: STEEVE-MAX
Tag       : BCE-4X ULTIME ABSOLU — TOP-ABSOLU

MASQUE DE PRÉSENCE/ABSENCE par espèce et par TERRITOIRE.

Empêche la génération et le rendu de corridors pour les espèces écologiquement
absentes (ex. wapiti hors aire de présence naturelle au Bas-Saint-Laurent).

═════════════════════════════════════════════════════════════════════════
SOURCES BIOLOGIQUES (registre institutionnel)
═════════════════════════════════════════════════════════════════════════

Références :
  - MFFP Québec — Cartes de répartition officielles 2023-2024
  - SEPAQ — Plans directeurs par région faunique
  - Atlas des mammifères du Québec (Prescott, Richard 2013)
  - iNaturalist / eBird observations vérifiées
  - BIONIC OS — Registre territorial V30

Règle de fallback : si un territoire n'est pas dans le registre, on suppose
présence universelle (PRESENT) pour éviter des faux-négatifs silencieux.
"""
from __future__ import annotations

import math
import os
from typing import Any, Dict, List, Optional, Tuple

PHASE_TAG = "PHASE_XVIII_BIO_PRESENCE_MASK"
PHASE_NAME = "PHASE_XVIII_BIO_PRESENCE_MASK_Ω"

# Mode ENFORCE (par défaut actif pour P0)
ENFORCE_MODE = os.environ.get("XVIII_BIO_PRESENCE_ENFORCE", "1") == "1"

PRESENT = "PRESENT"
ABSENT = "ABSENT"

# ═══════════════════════════════════════════════════════════════════════
# Registre institutionnel des zones de présence par espèce
# ═══════════════════════════════════════════════════════════════════════
# Chaque zone est un rectangle (lat_min, lat_max, lng_min, lng_max) OU un
# cercle (lat, lng, radius_km). Aucune zone = ABSENT dans ce registre.
# Le registre couvre le Québec principalement. Pour d'autres régions, on
# peut étendre ultérieurement.

SPECIES_PRESENCE_REGISTRY: Dict[str, Dict[str, Any]] = {
    "orignal": {
        "common_name": "Alces alces",
        "status_quebec": "ABONDANT — présent sur 97 % du territoire forestier",
        "source": "MFFP 2024 — Inventaires aériens ZEC + Plans de gestion",
        "rectangles": [
            # Québec forestier (sauf îles Madeleine et extrême sud urbain)
            (45.0, 62.0, -79.8, -57.0),
        ],
    },
    "chevreuil": {
        "common_name": "Odocoileus virginianus",
        "status_quebec": "PRÉSENT (densité variable nord-sud)",
        "source": "MFFP 2024 — Réseau Cerf sud du Québec + colonisation nord",
        "rectangles": [
            # Cerf : colonisé jusqu'à latitude ~50°N, présent Bas-Saint-Laurent
            (44.5, 50.5, -79.8, -59.0),
        ],
    },
    "wapiti": {
        "common_name": "Cervus canadensis",
        "status_quebec": ("ABSENT NATUREL — seules petites populations introduites "
                          "en Mauricie / Outaouais (Seigneurie du Triton, Portneuf)"),
        "source": "MFFP 2024 — Programme Wapiti Québec, zones introduites uniquement",
        "rectangles": [
            # Seigneurie du Triton (Mauricie) et Portneuf seulement
            (46.5, 47.9, -74.5, -72.0),   # Mauricie intro
            (46.3, 47.0, -72.0, -71.4),   # Portneuf
            (45.3, 46.5, -76.0, -74.2),   # Outaouais / Papineau-Labelle
        ],
    },
    "ours_noir": {
        "common_name": "Ursus americanus",
        "status_quebec": "PRÉSENT sur tout le Québec forestier",
        "source": "MFFP 2024 — Plan de gestion ours noir",
        "rectangles": [
            (45.0, 60.0, -79.8, -57.0),
        ],
    },
    "dindon_sauvage": {
        "common_name": "Meleagris gallopavo",
        "status_quebec": ("SUD DU QUÉBEC UNIQUEMENT — aire naturelle limitée à "
                          "Estrie, Montérégie, Outaouais, sud Laurentides et "
                          "Bas-Saint-Laurent sud (Témiscouata)"),
        "source": "MFFP 2024 — Programme Dindon + colonisation nord 2020-2024",
        "rectangles": [
            # Sud du Québec seulement (limite nord ~47°N)
            (44.9, 47.0, -79.8, -66.5),
        ],
    },
    # P22Ω_COYOTE_REGISTRY_DECISION (2026-05-13 · COMMANDANT STEEVE-MAX)
    "coyote": {
        "common_name": "Canis latrans",
        "status_quebec": ("PRÉSENT — implanté sur tout le Québec méridional "
                          "et progression continue vers le nord (Saguenay, BSL, "
                          "Côte-Nord). Hybridation avec loup de l'Est documentée."),
        "source": "MFFP 2024 — Plan de gestion coyote + Atlas mammifères Québec 2023",
        "rectangles": [
            # Québec méridional + ceinture forestière (jusqu'à 52°N estimé)
            (44.5, 52.0, -79.8, -57.0),
        ],
    },
}

# Aliases d'espèce pour matcher la nomenclature frontend/backend
SPECIES_ALIASES = {
    "orignal": "orignal",
    "cerf": "chevreuil",
    "chevreuil": "chevreuil",
    "wapiti": "wapiti",
    "ours": "ours_noir",
    "ours_noir": "ours_noir",
    "dindon": "dindon_sauvage",
    "dindon_sauvage": "dindon_sauvage",
    # P22Ω_COYOTE_REGISTRY_DECISION (2026-05-13)
    "coyote": "coyote",
    "canis_latrans": "coyote",
}


# ═══════════════════════════════════════════════════════════════════════
# API publique
# ═══════════════════════════════════════════════════════════════════════
def _canonical(species: str) -> str:
    return SPECIES_ALIASES.get((species or "").lower().strip(), (species or "").lower().strip())


def _in_rectangle(lat: float, lng: float, rect: Tuple[float, float, float, float]) -> bool:
    la_min, la_max, lo_min, lo_max = rect
    return la_min <= lat <= la_max and lo_min <= lng <= lo_max


def get_species_presence(lat: float, lng: float, species: str) -> Dict[str, Any]:
    """Retourne {status: PRESENT|ABSENT, source, reason, canonical, common_name}."""
    canon = _canonical(species)
    entry = SPECIES_PRESENCE_REGISTRY.get(canon)
    if not entry:
        return {
            "status": PRESENT,
            "canonical": canon,
            "species_input": species,
            "common_name": None,
            "source": "FALLBACK — espèce non enregistrée, présence assumée",
            "reason": "unknown_species_assumed_present",
            "rectangles_count": 0,
        }
    rects = entry.get("rectangles") or []
    in_any = any(_in_rectangle(lat, lng, r) for r in rects)
    return {
        "status": PRESENT if in_any else ABSENT,
        "canonical": canon,
        "species_input": species,
        "common_name": entry.get("common_name"),
        "source": entry.get("source"),
        "status_quebec": entry.get("status_quebec"),
        "rectangles_tested": len(rects),
        "reason": ("in_natural_range" if in_any else "outside_natural_range"),
    }


def get_species_presence_mask(lat: float, lng: float) -> Dict[str, Any]:
    """Masque pour TOUTES les espèces officielles à ce territoire (lat, lng)."""
    mask = {}
    for canon in ("chevreuil", "orignal", "wapiti", "ours_noir", "dindon_sauvage", "coyote"):
        mask[canon] = get_species_presence(lat, lng, canon)
    return {
        "phase": PHASE_NAME,
        "subphase": PHASE_TAG,
        "enforce_mode": ENFORCE_MODE,
        "territoire": {"lat": lat, "lng": lng},
        "mask": mask,
        "summary": {
            "PRESENT": [k for k, v in mask.items() if v["status"] == PRESENT],
            "ABSENT": [k for k, v in mask.items() if v["status"] == ABSENT],
        },
    }


# ═══════════════════════════════════════════════════════════════════════
# Application au bundle TERRITOIRE
# ═══════════════════════════════════════════════════════════════════════
def apply_presence_mask_to_bundle(bundle: Dict[str, Any],
                                    species: str,
                                    lat: Optional[float] = None,
                                    lng: Optional[float] = None) -> Dict[str, Any]:
    """Si l'espèce est ABSENTE du territoire → vide les corridors et tronque
    le pipeline TERRITOIRE. Sinon pipeline inchangé.

    IMPORTANT : Ce filtre est appliqué AVANT tout le pipeline V30 → XIX →
    XVIII-VITAUX afin de (1) économiser le calcul, (2) garantir l'absence
    totale de corridors pour l'espèce absente.
    """
    if not isinstance(bundle, dict):
        return bundle

    if lat is None:
        lat = (bundle.get("waypoint") or {}).get("lat")
    if lng is None:
        lng = (bundle.get("waypoint") or {}).get("lng") or (bundle.get("waypoint") or {}).get("lon")
    if lat is None or lng is None:
        bundle["bio_presence_mask_applied"] = False
        bundle["bio_presence_mask_error"] = "waypoint_missing"
        return bundle

    presence = get_species_presence(float(lat), float(lng), species)
    corridors_before = len(bundle.get("corridors") or [])

    if ENFORCE_MODE and presence["status"] == ABSENT:
        # ═══════════════════════════════════════════════════════════════════
        # PHASE-C R1 — PURGE COMPLÈTE INSTITUTIONNELLE DES ARTEFACTS ABSENT
        # ═══════════════════════════════════════════════════════════════════
        # Doctrine BCE-4X : si l'espèce n'est pas présente sur le territoire
        # (registre MFFP+SEPAQ+Atlas), AUCUN artefact dépendant de l'espèce
        # ne doit être émis : ni corridors, ni affuts, ni hotspots (qui sont
        # dérivés des affuts), ni salines (calculées par bio_species), ni
        # contamination/contamination_v2 (zones de pression d'odeur), ni
        # données sensorielles vent/odeurs/son spécifiques à l'espèce.
        # Les couches d'infrastructure écologique du territoire (zones,
        # hydat, terrain, habitats_critiques) sont préservées pour l'audit
        # global du territoire (visibilité opérationnelle).
        # ═══════════════════════════════════════════════════════════════════
        purge_counts = {
            "corridors": corridors_before,
            "affuts": len(bundle.get("affuts") or []),
            "hotspots": len(bundle.get("hotspots") or []),
            "salines": len(bundle.get("salines") or []),
            "contamination": len(bundle.get("contamination") or []),
            "contamination_zones": len(bundle.get("contamination_zones") or []),
            "wind_vectors": len(bundle.get("wind_vectors") or []),
        }
        bundle["corridors"] = []
        bundle["corridors_rejected_bio_presence_mask"] = [
            {"reason": "species_absent_from_territory",
             "canonical": presence["canonical"],
             "source": presence.get("source")}
        ]
        bundle["affuts"] = []
        bundle["affuts_rejected_bio_presence_mask_count"] = purge_counts["affuts"]
        # PHASE-C R1 (P0) — purge des artefacts dépendants de l'espèce
        bundle["hotspots"] = []
        bundle["hotspots_rejected_bio_presence_mask_count"] = purge_counts["hotspots"]
        bundle["salines"] = []
        bundle["salines_rejected_bio_presence_mask_count"] = purge_counts["salines"]
        bundle["contamination"] = []
        bundle["contamination_zones"] = []
        bundle["contamination_rejected_bio_presence_mask_count"] = purge_counts["contamination"]
        # contamination_v2 (dict) : neutralisation institutionnelle (préserve la
        # forme du dict pour les consommateurs UI mais vide les zones).
        cv2 = bundle.get("contamination_v2")
        if isinstance(cv2, dict):
            bundle["contamination_v2"] = {
                **cv2,
                "polygons": [],
                "zones": [],
                "active": False,
                "bio_presence_mask_purged": True,
            }
        cv2_heatmap = bundle.get("contamination_v2_heatmap")
        if isinstance(cv2_heatmap, dict):
            bundle["contamination_v2_heatmap"] = {
                **cv2_heatmap,
                "points": [],
                "bio_presence_mask_purged": True,
            }
        # wind_vectors : neutralisation des vecteurs visuels (le vent météo
        # reste consultable via sensoriel_vent_odeurs comme source de vérité).
        bundle["wind_vectors"] = []
        bundle["wind_vectors_rejected_bio_presence_mask_count"] = purge_counts["wind_vectors"]
        # ENGINE_SON / sensoriel_vent_odeurs : marquer comme inactif (le score
        # olfactif/sonore n'a pas de sens pour une espèce ABSENT).
        svo = bundle.get("sensoriel_vent_odeurs")
        if isinstance(svo, dict):
            bundle["sensoriel_vent_odeurs"] = {
                **svo,
                "active": False,
                "bio_presence_mask_purged": True,
                "score": 0.0,
            }
        bundle["bio_presence_mask_halt"] = True
        bundle["bio_presence_mask_purge_counts"] = purge_counts
    else:
        bundle["bio_presence_mask_halt"] = False

    bundle["bio_presence_mask_applied"] = True
    bundle["bio_presence_mask_stats"] = {
        "phase": PHASE_NAME,
        "subphase": PHASE_TAG,
        "enforce_mode": ENFORCE_MODE,
        "species_input": species,
        "canonical": presence["canonical"],
        "common_name": presence.get("common_name"),
        "territoire_lat_lng": [lat, lng],
        "presence_status": presence["status"],
        "presence_source": presence.get("source"),
        "presence_reason": presence.get("reason"),
        "corridors_v30_count_avant_filtre_presence": corridors_before,
        "corridors_v30_count_apres_filtre_presence": len(bundle.get("corridors") or []),
        "rectangles_tested": presence.get("rectangles_tested"),
    }
    return bundle


def get_registry_audit() -> Dict[str, Any]:
    """Audit institutionnel du registre (lecture seule)."""
    return {
        "phase": PHASE_NAME,
        "subphase": PHASE_TAG,
        "enforce_mode": ENFORCE_MODE,
        "species_count": len(SPECIES_PRESENCE_REGISTRY),
        "species_list": list(SPECIES_PRESENCE_REGISTRY.keys()),
        "registry": {
            k: {
                "common_name": v.get("common_name"),
                "status_quebec": v.get("status_quebec"),
                "source": v.get("source"),
                "rectangles_count": len(v.get("rectangles") or []),
            }
            for k, v in SPECIES_PRESENCE_REGISTRY.items()
        },
        "rule": "Si species_presence_mask[espèce] = ABSENT → corridors = [] + halt pipeline.",
    }

"""
P22M_DENSIFICATION_VITALE_X3_Ω · Module institutionnel de densification ×3
══════════════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU · ANTI-GÉNÉRIQUE STRICT

Objectif :
  - Tripler les points d'ancrage ORGANIC (alim, repos, rut, thermique, humide)
    en générant 2 nœuds satellites jittered autour de chaque nœud original.
  - Augmenter la granularité du réseau pour amplifier la fusion veineuse Ω.
  - Réduire les discontinuités dans la zone fonctionnelle 600 m ± 30 %.
  - Préserver les types et scores doctrinaux (anti-générique).

Stratégie biologique :
  - Pour chaque nœud "alimentation" / "repos" / "rut" / "thermique" / "humide" :
    générer 2 satellites à un rayon ∈ [40m, 75m] (zone biologique cohérente).
  - Angles séparés de 120° pour assurer une vraie densification surfacique.
  - Score satellite = 0.85 × score parent (cohérence hiérarchique).
  - Type satellite = type parent (préservation biologique stricte).
  - source_id satellite = "{parent_id}_dnsf{1|2}" (traçabilité).
  - Salines / hotspots : NON densifiés (ressources institutionnelles uniques).

V30_LOCK INVIOLÉ · FUSION ADD-ONLY · ENGINE EXTERNE
"""

from __future__ import annotations

import math
from typing import Any

# Constantes doctrinales
DENSIFY_FACTOR = 3                   # x3 : 1 nœud parent → 3 nœuds (parent + 2 satellites)
SATELLITE_RADIUS_MIN_M = 40.0        # rayon minimal jitter (m)
SATELLITE_RADIUS_MAX_M = 75.0        # rayon maximal jitter (m)
SATELLITE_SCORE_RATIO = 0.85         # satellite hérite 85% du score parent
DENSIFIABLE_TYPES = {"alimentation", "repos", "rut", "thermique", "humide"}
NON_DENSIFIABLE_TYPES = {"saline", "hotspot", "refuge"}  # ressources uniques


def _offset_lat_lon(lat: float, lon: float, distance_m: float, bearing_deg: float
                    ) -> tuple[float, float]:
    """Calcule lat/lon décalé de `distance_m` à un angle `bearing_deg` depuis (lat,lon).

    Approximation flat-earth valide pour les distances < 1km au Québec
    (±0.5% d'erreur, suffisamment précis pour anchor satellites).
    """
    cos_lat = max(0.5, math.cos(math.radians(lat)))
    bearing_rad = math.radians(bearing_deg)
    dlat_m = distance_m * math.cos(bearing_rad)
    dlon_m = distance_m * math.sin(bearing_rad)
    new_lat = lat + (dlat_m / 111000.0)
    new_lon = lon + (dlon_m / (111000.0 * cos_lat))
    return (new_lat, new_lon)


def _deterministic_seed(node: dict) -> int:
    """Seed déterministe basé sur l'ID source — garantit la reproductibilité.

    Aucun random.random() — toute génération doit être déterministe (anti-régression).
    """
    sid = str(node.get("source_id", ""))
    # Hash simple : somme ordinale des caractères + lat/lon entiers
    h = sum(ord(c) for c in sid)
    h += int(abs(float(node.get("lat", 0)) * 1000)) % 1000
    h += int(abs(float(node.get("lon", 0)) * 1000)) % 1000
    return h


def densify_vital_nodes_x3(nodes: list[dict]) -> list[dict]:
    """Densifie les nœuds vitaux ×3 — chaque node éligible génère 2 satellites.

    INPUT  : list[dict] de nœuds avec {type, lat, lon, score, source_id, source, ...}
    OUTPUT : list[dict] (parents préservés + 2 satellites par node éligible)

    Salines / hotspots / refuges restent inchangés (ressources institutionnelles uniques).

    Doctrine biologique :
      - Satellite radius ∈ [40m, 75m] (zone fonctionnelle)
      - Angles séparés de 120° pour étaler le réseau
      - Score = 0.85 × score parent
      - Préservation stricte du type (alim → alim, repos → repos, etc.)
    """
    if not nodes:
        return list(nodes)

    out: list[dict] = []
    densified_count = 0
    preserved_count = 0

    for node in nodes:
        # Toujours préserver le parent
        parent = dict(node)
        parent["_p22m_role"] = "PARENT"
        out.append(parent)

        ntype = (node.get("type") or "").lower()
        if ntype not in DENSIFIABLE_TYPES:
            preserved_count += 1
            continue

        seed = _deterministic_seed(node)
        # Rayon dans [40m, 75m] (déterministe via seed)
        radius_jitter = SATELLITE_RADIUS_MIN_M + ((seed * 7) % 36)  # ∈ [40, 75]
        # Angle base entre [0°, 120°] (déterministe)
        bearing_base = (seed * 31) % 360

        # Génération de (DENSIFY_FACTOR - 1) = 2 satellites séparés de 120°
        for k in range(1, DENSIFY_FACTOR):
            bearing = (bearing_base + 120.0 * k) % 360.0
            sat_lat, sat_lon = _offset_lat_lon(
                float(node["lat"]), float(node["lon"]),
                radius_jitter, bearing,
            )
            sat = dict(node)
            sat["lat"] = sat_lat
            sat["lon"] = sat_lon
            sat["score"] = float(node.get("score", 50)) * SATELLITE_SCORE_RATIO
            sat["source_id"] = f"{node.get('source_id', 'unknown')}_dnsf{k}"
            sat["_p22m_role"] = "SATELLITE"
            sat["_p22m_parent_id"] = node.get("source_id")
            sat["_p22m_bearing_deg"] = bearing
            sat["_p22m_radius_m"] = radius_jitter
            out.append(sat)

        densified_count += 1

    # Tag global pour traçabilité institutionnelle
    out_with_meta = out
    return out_with_meta


def densification_summary(original_nodes: list[dict],
                          densified_nodes: list[dict]) -> dict[str, Any]:
    """Synthèse statistique de la densification."""
    n_orig = len(original_nodes)
    n_dense = len(densified_nodes)
    by_type: dict[str, int] = {}
    for n in densified_nodes:
        t = (n.get("type") or "unknown").lower()
        by_type[t] = by_type.get(t, 0) + 1
    n_satellites = sum(1 for n in densified_nodes
                       if n.get("_p22m_role") == "SATELLITE")
    return {
        "n_nodes_before": n_orig,
        "n_nodes_after": n_dense,
        "n_satellites_generated": n_satellites,
        "densification_factor": (n_dense / n_orig) if n_orig > 0 else 0.0,
        "by_type": by_type,
        "doctrine": "P22M_DENSIFICATION_VITALE_X3_Ω",
        "satellite_radius_range_m": [SATELLITE_RADIUS_MIN_M, SATELLITE_RADIUS_MAX_M],
        "satellite_score_ratio": SATELLITE_SCORE_RATIO,
    }

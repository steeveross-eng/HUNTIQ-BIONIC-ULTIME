"""
ENGINE 05 — VENT
PILIER: BIO-SYSTEME
SOURCES FUSIONNEES: weather_v3, wse_wiv_engine, hunt_orchestrator.vent_odeurs
OPTIMISATIONS PRESERVEES: Open-Meteo temps reel, dispersion olfactive, wind impact vector

PHASE-C R2 (PHASE_TERRITOIRE_Ω_AUDIT_PHASE_C_VENT_RECONCILIATION) :
  - source canonique de vérité : `sensoriel_vent_odeurs.wind_deg` (ENGINE_VENT V20)
  - wind_vectors est un dérivé visuel (éventail 8 vecteurs centrés sur la vérité)
  - chaque vecteur expose : `axis_offset_deg`, `is_central`, `parent_truth_deg`

PHASE-E FIX C1 (ordre Commandant STEEVE-MAX 2026-04-28 · BCE-4X ULTIME ABSOLU) :
  - Convention OMM/Open-Meteo : `wind_deg` = direction FROM (origine du vent).
  - Alignement institutionnel sur `engine_sensoriel_vent_odeurs_omega.cone_axis`
    (= wind_deg + 180° = downwind propagation).
  - Les vecteurs visuels (`compute_wind_vectors`) et le cône de propagation
    olfactive (`compute_scent_cone`) pointent désormais vers la direction
    SOUS-VENT (downwind) : `wind_deg + 180°`.
  - `parent_truth_deg` (vérité brute météo) reste exposé en convention FROM
    pour traçabilité institutionnelle.
"""
import math

# Convention OMM/WMO — wind_deg est l'origine du vent ("FROM").
# Pour obtenir la direction de propagation des odeurs/sons (downwind), on inverse de 180°.
WIND_DOWNWIND_OFFSET_DEG = 180.0
WIND_CONVENTION_DOC = (
    "OMM/WMO: wind_deg = FROM. downwind = (wind_deg + 180) % 360. "
    "Aligné sur engine_sensoriel_vent_odeurs_omega.cone_axis_deg."
)


def _downwind_deg(wind_deg: float) -> float:
    """Convertit wind_deg (FROM, météo) en direction de propagation (TO, downwind)."""
    return (float(wind_deg) + WIND_DOWNWIND_OFFSET_DEG) % 360.0


def compute_wind_vectors(lat, lon, wind_deg, wind_speed_kmh, n_vectors=8,
                         radius_km=1, step_deg=15):
    """Vecteurs visuels du vent — orientés DOWNWIND (alignés sur engine_sensoriel).

    `wind_deg` est interprété en convention OMM "FROM". Les vecteurs visuels
    pointent vers où le vent propage les odeurs (`wind_deg + 180°`).
    """
    vectors = []
    cos_lat = max(0.5, math.cos(math.radians(lat)))
    central_index = n_vectors // 2
    downwind_axis = _downwind_deg(wind_deg)
    parent_truth_from = round(float(wind_deg) % 360.0, 1)
    for i in range(n_vectors):
        offset = (i - central_index) * step_deg
        angle = downwind_axis + offset
        rad = math.radians(angle)
        dist = radius_km / 111.0 * (0.3 + i * 0.1)
        end_lat = lat + math.cos(rad) * dist
        end_lon = lon + math.sin(rad) * dist / cos_lat
        decay = max(0.1, 1.0 - (abs(i - central_index) / n_vectors))
        vectors.append({
            "id": f"wind_v8_{i}",
            "start": {"lat": round(lat, 6), "lng": round(lon, 6)},
            "end": {"lat": round(end_lat, 6), "lng": round(end_lon, 6)},
            "direction_deg": round(angle % 360, 1),
            "speed_kmh": round(wind_speed_kmh * decay, 1),
            "decay": round(decay, 2),
            # PHASE-C R2 — annotations institutionnelles de réconciliation
            "axis_offset_deg": offset,
            "is_central": (i == central_index),
            # PHASE-E FIX C1 — convention OMM "FROM" préservée pour traçabilité
            "parent_truth_deg": parent_truth_from,
            "parent_truth_convention": "FROM",
            "downwind_axis_deg": round(downwind_axis, 1),
            "parent_truth_speed_kmh": round(wind_speed_kmh, 1),
            "source": "engine_vent.compute_wind_vectors (PHASE-E FIX C1, downwind aligned)",
        })
    return vectors


def compute_scent_cone(lat, lon, wind_deg, wind_speed_kmh, cone_angle=30, reach_m=500):
    """Cône olfactif — projeté DOWNWIND (alignement OMM/sensoriel).

    `wind_deg` est interprété en convention OMM "FROM". Le cône de propagation
    olfactive pointe vers `wind_deg + 180°` (downwind), aligné sur
    `engine_sensoriel_vent_odeurs_omega.cone_axis_deg`.
    """
    cos_lat = max(0.5, math.cos(math.radians(lat)))
    reach_deg = reach_m / 111320
    downwind_axis = _downwind_deg(wind_deg)
    left_rad = math.radians(downwind_axis - cone_angle / 2)
    right_rad = math.radians(downwind_axis + cone_angle / 2)
    return {
        "origin": {"lat": lat, "lng": lon},
        # PHASE-E FIX C1 — `direction_deg` = axe DOWNWIND (TO) ; `parent_truth_from`
        # conserve la valeur OMM brute pour audit/traçabilité institutionnelle.
        "direction_deg": round(downwind_axis, 1),
        "parent_truth_from_deg": round(float(wind_deg) % 360.0, 1),
        "convention": "downwind_TO (aligned on engine_sensoriel_vent_odeurs.cone_axis_deg)",
        "cone_angle": cone_angle,
        "reach_m": reach_m,
        "polygon": [
            [lat, lon],
            [round(lat + math.cos(left_rad) * reach_deg, 6),
             round(lon + math.sin(left_rad) * reach_deg / cos_lat, 6)],
            [round(lat + math.cos(right_rad) * reach_deg, 6),
             round(lon + math.sin(right_rad) * reach_deg / cos_lat, 6)],
            [lat, lon],
        ],
        "source": "engine_vent.compute_scent_cone (PHASE-E FIX C1, downwind aligned)",
    }

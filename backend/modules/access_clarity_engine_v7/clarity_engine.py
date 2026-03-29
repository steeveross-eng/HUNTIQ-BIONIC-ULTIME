"""
clarity_engine.py — Moteur de guidance optimale access_clarity_engine_v7
PROTOCOLE BIONIC GOLDEN | BCE-4X | STEEVE-MAX
Branche: STEEVE-MAX-x3200-V6-CORE

Pipeline complet:
  1. Recoit les coordonnees brutes depuis hunt_orchestrator/access_engine
  2. Applique suppression zigzags
  3. Lissage Douglas-Peucker (reduction bruit grille)
  4. Interpolation naturelle Catmull-Rom (courbes humaines)
  5. Score TCS complet (Terrain Clarity Score 0->100)
  6. Auto-correction des acces non naturels
  7. Metadonnees de rendu visuel (bleu-clair optimise)

Modele optimal d'acces forestier Quebec:
  - Sentiers reels prioritaires (x0.1)
  - Bordures ruisseaux = corridors naturels
  - Clairieres = zones de transition
  - Foret ouverte = praticable
  - Foret dense = penalise
  - Zones humides = eviter
"""
import logging
import math

from .smoother import smooth_full_pipeline
from .scorer import compute_tcs

logger = logging.getLogger("access_clarity_engine_v7")

# Rendu visuel GOLDEN — bleu-clair optimise
CLARITY_RENDER = {
    "color_primary": "#4FC3F7",
    "color_secondary": "#0288D1",
    "color_trail": "#26A69A",
    "color_terrain": "#4FC3F7",
    "color_fallback": "#FFD700",
    "weight": 3.5,
    "opacity": 0.90,
    "glow_color": "rgba(79, 195, 247, 0.25)",
    "glow_radius": 6,
}

# Seuils auto-correction
MIN_ACCEPTABLE_TCS = 25
MIN_SMOOTHNESS = 30


def apply_clarity(
    access_data: dict,
    terrain_context: dict = None,
) -> dict:
    """
    Applique le pipeline de clarte v7 sur les donnees d'acces existantes.

    access_data: sortie de hunt_orchestrator.access_engine.compute_access_route
    terrain_context: donnees supplementaires (LIDAR, vegetation, hydro)

    Retourne access_data enrichi avec:
    - coords lissees
    - tcs (Terrain Clarity Score)
    - render (metadonnees visuelles)
    - clarity_applied: True
    """
    if terrain_context is None:
        terrain_context = {}

    coords = access_data.get("coords", [])
    if len(coords) < 2:
        access_data["clarity_applied"] = False
        access_data["tcs"] = {"score": 0, "grade": "F", "components": {}, "summary": "Aucun chemin"}
        return access_data

    # Phase 1-3: Pipeline de lissage complet
    smoothed = smooth_full_pipeline(
        coords,
        dp_tolerance=0.00003,
        zigzag_angle_threshold=115.0,
        interp_points=2,
    )

    # Garantir que premier et dernier points sont preserves
    if smoothed and coords:
        first_orig = coords[0]
        last_orig = coords[-1]
        if isinstance(smoothed[0], dict):
            smoothed[0] = {"lat": first_orig["lat"], "lng": first_orig["lng"]}
            smoothed[-1] = {"lat": last_orig["lat"], "lng": last_orig["lng"]}

    # Phase 4: Score TCS
    tcs_input = {**access_data, "coords": smoothed}
    tcs = compute_tcs(tcs_input, terrain_context)

    # Phase 5: Auto-correction si TCS trop bas
    if tcs["score"] < MIN_ACCEPTABLE_TCS and len(smoothed) >= 3:
        logger.info(f"clarity_v7: TCS={tcs['score']} < {MIN_ACCEPTABLE_TCS}, auto-correction activee")
        smoothed = _auto_correct(smoothed, coords)
        tcs_input_corrected = {**access_data, "coords": smoothed}
        tcs = compute_tcs(tcs_input_corrected, terrain_context)

    # Phase 6: Determiner le rendu visuel
    render = _compute_render_style(access_data, tcs)

    # Recalculer la distance apres lissage
    smoothed_distance = _compute_distance(smoothed)

    # Mettre a jour les donnees d'acces
    access_data["coords"] = smoothed
    access_data["coords_count"] = len(smoothed)
    access_data["distance_m"] = round(smoothed_distance)
    access_data["tcs"] = tcs
    access_data["render"] = render
    access_data["clarity_applied"] = True
    access_data["engine"] = "access_clarity_engine_v7"

    logger.info(
        f"clarity_v7: TCS={tcs['score']}/{tcs['grade']}, "
        f"pts={len(smoothed)}, dist={smoothed_distance:.0f}m, "
        f"algo={access_data.get('routing_algo', '?')}"
    )

    return access_data


def _auto_correct(smoothed: list, original: list) -> list:
    """
    Auto-correction: si le lissage a degrade le chemin,
    revenir aux coords originales avec un lissage plus doux.
    """
    return smooth_full_pipeline(
        original,
        dp_tolerance=0.00005,
        zigzag_angle_threshold=135.0,
        interp_points=1,
    )


def _compute_render_style(access_data: dict, tcs: dict) -> dict:
    """
    Determiner le style de rendu visuel base sur le TCS et le type de route.
    """
    routing_algo = access_data.get("routing_algo", "")
    trail_type = access_data.get("trail_type", "")
    grade = tcs.get("grade", "F")

    # Couleur principale basee sur le grade TCS
    if grade in ("S", "A"):
        color = CLARITY_RENDER["color_trail"]
        dash = None
        label = "Acces optimal v7"
    elif grade == "B":
        color = CLARITY_RENDER["color_primary"]
        dash = None
        label = "Acces clair v7"
    elif grade == "C":
        color = CLARITY_RENDER["color_secondary"]
        dash = "8, 5"
        label = "Acces modere v7"
    else:
        color = CLARITY_RENDER["color_fallback"]
        dash = "6, 8, 2, 8"
        label = "Acces faible v7"

    # Override pour sentiers reels
    if trail_type in ("sentier_reel", "trail") or routing_algo in ("a_star", "dijkstra"):
        color = CLARITY_RENDER["color_trail"]
        dash = None
        label = "Sentier reel v7"

    return {
        "color": color,
        "weight": CLARITY_RENDER["weight"],
        "opacity": CLARITY_RENDER["opacity"],
        "dash_array": dash,
        "glow": CLARITY_RENDER["glow_color"],
        "glow_radius": CLARITY_RENDER["glow_radius"],
        "label": label,
        "tcs_badge": f"TCS {tcs['score']:.0f} ({grade})",
    }


def _compute_distance(coords: list) -> float:
    """Distance totale d'une liste de coordonnees."""
    total = 0
    for i in range(len(coords) - 1):
        total += _haversine_coord(coords[i], coords[i + 1])
    return total


def _haversine_coord(c1, c2) -> float:
    if isinstance(c1, dict):
        lat1, lng1 = c1["lat"], c1["lng"]
        lat2, lng2 = c2["lat"], c2["lng"]
    else:
        lng1, lat1 = c1[0], c1[1]
        lng2, lat2 = c2[0], c2[1]

    R = 6371000
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlng / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

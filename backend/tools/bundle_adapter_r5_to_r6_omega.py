"""
bundle_adapter_r5_to_r6_omega.py — Adaptateur fan-out R5 → 7 enfants R6
═══════════════════════════════════════════════════════════════════════
P22ΩΩ_PHASE3_BUNDLE_SEED_H3R5_BETA2_SIGMA_TAU_Ω · STEEVE-MAX · 2026-02-19

⚠️  STATUT : SQUELETTE READY-TO-RUN · INERTE TANT QUE COMMANDANT N'A PAS
            VALIDÉ L'ACTIVATION VIA `COMMANDE_OPERATIONNELLE_BETA2_ST_ACTIVATION_Ω.md`.

DOCTRINE
--------
Transforme un bundle V20 calculé pour une cellule H3 R5 (parent) en un bundle
adapté pour chacune de ses 7 cellules H3 R6 (enfants), via :
  1. Décalage géométrique (offset (Δlat, Δlng)) sur toutes les coordonnées
     (corridors, zones, affûts, salines, hotspots).
  2. Variations déterministes mineures (hash R6 cell ID) pour éviter
     l'aspect "tuile copiée-collée".
  3. Re-stamp métadonnées (center_lat, center_lng, h3_cell).

⚠️ Phase III Lock préservé : ne modifie PAS V20 · transformation purement
   post-pipeline sur la sortie déjà calculée.

USAGE INTÉGRATION (worker β2-ΣΤ) :
    from tools.bundle_adapter_r5_to_r6_omega import adapt_bundle_to_r6_child

    seed_bundle = await v20_territoire_bundle(r5_lat, r5_lng, species, m, h, ...)
    for r6_child_id in h3.cell_to_children(r5_h3, 6):
        r6_bundle = adapt_bundle_to_r6_child(seed_bundle, r6_child_id)
        upload_to_r2(r6_bundle, f"v1/{species}/{r6_cell}/m{m}_h{h}.json.gz")
"""
import copy
import hashlib
import math
from typing import Any

try:
    import h3
except ImportError:
    raise SystemExit("Missing h3 dependency")

DOCTRINE = "P22ΩΩ_PHASE3_BUNDLE_SEED_H3R5_BETA2_SIGMA_TAU_Ω"

# Champs du bundle qui contiennent des coordonnées géographiques [lat, lng]
GEOMETRY_FIELDS = {
    "corridors": ("path", "coords", "coordinates"),
    "zones": ("polygon", "coords", "boundary", "coordinates"),
    "affuts": ("position", "lat_lng", "coords"),
    "salines": ("position", "lat_lng", "coords"),
    "hotspots": ("position", "lat_lng", "coords", "center"),
    "wind_vectors": ("position", "coords"),
}

# Champs métadata à re-stamp avec le centre R6 enfant
METADATA_FIELDS_TO_REWRITE = ("center_lat", "center_lng", "lat", "lon", "lng", "h3_cell")

# Jitter doctrinal pour variations déterministes (gardé minimal)
WIND_JITTER_DEG_MAX = 2.0      # ±2° max
SCORE_JITTER_PCT_MAX = 1.5     # ±1.5% max


def _hash_jitter(r6_cell_id: str) -> float:
    """Retourne un nombre dans [-0.5, 0.5] déterministe pour la cellule R6."""
    h = int(hashlib.sha256(r6_cell_id.encode()).hexdigest()[:8], 16)
    return (h % 1000) / 1000.0 - 0.5


def _offset_coords(coords: Any, dlat: float, dlng: float) -> Any:
    """Applique récursivement (dlat, dlng) à toute structure de coordonnées."""
    if coords is None:
        return None
    if isinstance(coords, (list, tuple)) and len(coords) == 2 \
            and all(isinstance(x, (int, float)) for x in coords):
        # Probablement [lat, lng]
        return [coords[0] + dlat, coords[1] + dlng]
    if isinstance(coords, list):
        return [_offset_coords(c, dlat, dlng) for c in coords]
    if isinstance(coords, dict):
        # Format {"lat": ..., "lng": ...} ou similaire
        out = {}
        for k, v in coords.items():
            if k in ("lat", "latitude"):
                out[k] = v + dlat
            elif k in ("lng", "lon", "longitude"):
                out[k] = v + dlng
            else:
                out[k] = _offset_coords(v, dlat, dlng)
        return out
    return coords  # int/float/str inchangé


def adapt_bundle_to_r6_child(
    seed_bundle: dict,
    r6_cell_id: str,
) -> dict:
    """Adapte un bundle V20 R5 vers une cellule R6 enfant.

    Garanties doctrinales :
    - Conservation stricte du nombre de corridors / zones / affûts
    - Conservation des scores macro (±1.5%)
    - Cohérence visuelle inter-R6 préservée par offset géométrique
    """
    if not isinstance(seed_bundle, dict):
        raise ValueError("seed_bundle doit être un dict")

    # 1) Centre R6 enfant
    r6_lat, r6_lng = h3.cell_to_latlng(r6_cell_id)

    # 2) Centre R5 parent (depuis le bundle source)
    r5_lat = seed_bundle.get("center_lat") or seed_bundle.get("lat") or 0.0
    r5_lng = seed_bundle.get("center_lng") or seed_bundle.get("lon") or 0.0

    dlat = r6_lat - r5_lat
    dlng = r6_lng - r5_lng

    # 3) Deep copy du bundle pour mutation safe
    adapted = copy.deepcopy(seed_bundle)

    # 4) Offset géométrique sur tous les champs identifiés
    for top_key, sub_keys in GEOMETRY_FIELDS.items():
        elements = adapted.get(top_key)
        if not isinstance(elements, list):
            continue
        for elem in elements:
            if not isinstance(elem, dict):
                continue
            for sub_key in sub_keys:
                if sub_key in elem:
                    elem[sub_key] = _offset_coords(elem[sub_key], dlat, dlng)

    # 5) Re-stamp métadata
    for k in METADATA_FIELDS_TO_REWRITE:
        if k in adapted:
            if k in ("center_lat", "lat"):
                adapted[k] = r6_lat
            elif k in ("center_lng", "lon", "lng"):
                adapted[k] = r6_lng
            elif k == "h3_cell":
                adapted[k] = r6_cell_id

    # 6) Jitter déterministe (anti "tuile copiée-collée")
    jitter = _hash_jitter(r6_cell_id)
    if "wind_deg" in adapted and isinstance(adapted["wind_deg"], (int, float)):
        adapted["wind_deg"] = (adapted["wind_deg"] + jitter * 2 * WIND_JITTER_DEG_MAX) % 360
    if "score_global" in adapted and isinstance(adapted["score_global"], (int, float)):
        adapted["score_global"] = max(
            0.0, min(100.0, adapted["score_global"] * (1 + jitter * SCORE_JITTER_PCT_MAX / 50))
        )

    # 7) Stamp doctrinal β2-ΣΤ
    adapted["_seed_r5_parent"] = h3.cell_to_parent(r6_cell_id, 5)
    adapted["_adapter_doctrine"] = DOCTRINE
    adapted["_fan_out_jitter"] = round(jitter, 4)

    return adapted


# ─────────────────────────────────────────────────────────────────────
# Tests unitaires intégrés (à exécuter post-activation Commandant)
# ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Mini-test de sanité
    fake_seed = {
        "center_lat": 46.5,
        "center_lng": -74.0,
        "wind_deg": 225.0,
        "score_global": 75.0,
        "corridors": [
            {"id": "C1", "path": [[46.50, -74.00], [46.51, -74.01], [46.52, -74.02]]},
        ],
        "zones": [
            {"id": "Z1", "polygon": [[46.51, -74.01], [46.52, -74.01], [46.52, -74.02]]},
        ],
        "affuts": [
            {"id": "A1", "position": [46.515, -74.015]},
        ],
        "salines": [
            {"id": "S1", "position": {"lat": 46.518, "lng": -74.012}},
        ],
        "hotspots": [
            {"id": "H1", "position": [46.520, -74.020]},
        ],
    }

    test_r5_h3 = h3.latlng_to_cell(46.5, -74.0, 5)
    children = h3.cell_to_children(test_r5_h3, 6)
    print(f"Test R5 parent : {test_r5_h3}")
    print(f"Enfants R6 : {len(children)}")
    for r6_id in children:
        adapted = adapt_bundle_to_r6_child(fake_seed, r6_id)
        r6_lat, r6_lng = h3.cell_to_latlng(r6_id)
        print(f"\n  R6 {r6_id} @ ({r6_lat:.4f}, {r6_lng:.4f})")
        print(f"    1er corridor pt 0 : {adapted['corridors'][0]['path'][0]}")
        print(f"    affut position    : {adapted['affuts'][0]['position']}")
        print(f"    wind_deg jittered : {adapted['wind_deg']:.2f}")
        print(f"    score_global      : {adapted['score_global']:.2f}")
        print(f"    _fan_out_jitter   : {adapted['_fan_out_jitter']}")

"""
P22Σ_V3_TERRITORY_CONTINUOUS_FUSION_VEINEUSE_Ω · Pytest neutre
═══════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU · ANTI-GÉNÉRIQUE STRICT

Validation doctrinale du module de fusion veineuse locale :
  - Distance fusion ≤ 18m (médiane 15-20m doctrinal)
  - Overlap ratio ≥ 30% pour fusion
  - Niveaux d'intensité 0-4 (FAIBLE → EXTRÊME)
  - Path averaging géométrique (28 pts cible RENDU-Ω)
  - Union-Find clustering
  - Summary statistique cohérent

Naming : aucune chaîne BCE_4X_EXCLUDED_KEYWORDS dans le nom de fichier
ni dans les noms de fonctions de test.
"""

import sys
from pathlib import Path

# Bootstrap : assurer le path /app/backend au front du sys.path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engines.post_smoothing.corridors_fusion_omega import (
    FUSION_DISTANCE_M,
    FUSION_OVERLAP_RATIO_MIN,
    _enrich_intensity,
    _haversine_m,
    _path_average,
    _path_overlap_ratio,
    fuse_corridors_by_species,
    fusion_summary,
)


def test_constants_doctrinal():
    """Vérifie les constantes doctrinales 18m / 30%."""
    assert FUSION_DISTANCE_M == 18.0  # médiane 15-20m doctrinal
    assert FUSION_OVERLAP_RATIO_MIN == 0.30


def test_haversine_zero_for_same_point():
    """Haversine retourne 0 pour 2 points identiques."""
    p = [48.206657, -68.382422]
    assert _haversine_m(p, p) < 1e-6


def test_haversine_consistency_18m_distance():
    """À ~18m de distance, doit retourner ~18m (±2m tolerance)."""
    p1 = [48.206657, -68.382422]
    # Approx 18m vers le nord (1 deg lat ≈ 111000 m)
    p2 = [48.206657 + (18.0 / 111000.0), -68.382422]
    d = _haversine_m(p1, p2)
    assert 17.0 <= d <= 19.0


def test_path_overlap_ratio_full_match():
    """Deux paths identiques → ratio = 1.0."""
    path = [[48.20, -68.38], [48.21, -68.38], [48.22, -68.38]]
    r = _path_overlap_ratio(path, path, max_dist_m=20.0)
    assert r == 1.0


def test_path_overlap_ratio_no_match():
    """Deux paths à >>18m de distance → ratio = 0.0."""
    a = [[48.20, -68.38], [48.21, -68.38]]
    b = [[48.50, -68.50], [48.51, -68.50]]  # ~30 km away
    r = _path_overlap_ratio(a, b, max_dist_m=18.0)
    assert r == 0.0


def test_path_average_resamples_to_28_points():
    """_path_average produit toujours 28 points pour ≥2 paths."""
    p1 = [[48.20, -68.38], [48.22, -68.38], [48.24, -68.38]]
    p2 = [[48.21, -68.38], [48.23, -68.38], [48.25, -68.38]]
    avg = _path_average([p1, p2])
    assert len(avg) == 28
    # Le path moyen doit être entre p1 et p2
    assert 48.20 <= avg[0][0] <= 48.21


def test_enrich_intensity_extreme_level():
    """fusion_count ≥ 4 → niveau 4 (EXTRÊME)."""
    c = {"hierarchy": "veine_principale"}
    enriched = _enrich_intensity(c, fusion_count=5)
    assert enriched["intensity_level"] == 4
    assert enriched["intensity_label"] == "EXTRÊME"


def test_enrich_intensity_levels_mapping():
    """Mapping fusion_count → intensity_level."""
    # fusion_count=2-3 → niveau 3
    e2 = _enrich_intensity({"hierarchy": "capillaire"}, fusion_count=2)
    assert e2["intensity_level"] == 3

    # fusion_count=1 + principale → niveau 2
    e_p = _enrich_intensity({"hierarchy": "veine_principale"}, fusion_count=1)
    assert e_p["intensity_level"] == 2

    # fusion_count=1 + secondaire → niveau 1
    e_s = _enrich_intensity({"hierarchy": "veine_secondaire"}, fusion_count=1)
    assert e_s["intensity_level"] == 1

    # fusion_count=1 + capillaire → niveau 0
    e_c = _enrich_intensity({"hierarchy": "capillaire"}, fusion_count=1)
    assert e_c["intensity_level"] == 0


def test_fuse_no_fusion_isolated():
    """Routes éloignées (>>18m) → aucune fusion."""
    c1 = {"id": "c1", "hierarchy": "capillaire",
          "path": [[48.20, -68.38], [48.21, -68.38]]}
    c2 = {"id": "c2", "hierarchy": "capillaire",
          "path": [[49.50, -69.50], [49.51, -69.50]]}  # ~140km away
    out = fuse_corridors_by_species([c1, c2])
    assert len(out) == 2
    # Aucun fusion_count > 1
    for c in out:
        assert c.get("fusion_count", 1) == 1


def test_fuse_real_fusion_proximity():
    """Deux routes superposées → fusion en 1 veine principale."""
    # Path identique → overlap ratio = 1.0 (≥30%)
    base_path = [[48.20 + i * 0.0001, -68.38] for i in range(20)]
    c1 = {"id": "c1", "hierarchy": "capillaire", "path": list(base_path)}
    c2 = {"id": "c2", "hierarchy": "capillaire", "path": list(base_path)}
    out = fuse_corridors_by_species([c1, c2])
    assert len(out) == 1
    assert out[0]["fusion_count"] == 2
    assert out[0]["hierarchy"] == "veine_principale"  # promu
    assert out[0]["intensity_level"] == 3  # fusion_count=2 → niveau 3
    assert "c2" in out[0]["merged_ids"]


def test_fuse_extreme_4_clusters():
    """4 routes fusionnées → niveau 4 EXTRÊME."""
    base_path = [[48.20 + i * 0.0001, -68.38] for i in range(20)]
    cs = [
        {"id": f"c{i}", "hierarchy": "capillaire", "path": list(base_path)}
        for i in range(4)
    ]
    out = fuse_corridors_by_species(cs)
    assert len(out) == 1
    assert out[0]["fusion_count"] == 4
    assert out[0]["intensity_level"] == 4  # ≥ 4 → EXTRÊME
    assert out[0]["intensity_label"] == "EXTRÊME"


def test_fusion_summary_distribution():
    """Summary statistique cohérent."""
    base_path = [[48.20 + i * 0.0001, -68.38] for i in range(20)]
    c1 = {"id": "c1", "hierarchy": "capillaire", "path": list(base_path)}
    c2 = {"id": "c2", "hierarchy": "capillaire", "path": list(base_path)}
    c3 = {"id": "c3", "hierarchy": "capillaire",
          "path": [[49.5, -69.5], [49.51, -69.5]]}  # isolé

    fused = fuse_corridors_by_species([c1, c2, c3])
    s = fusion_summary(fused)
    assert s["n_corridors_after_fusion"] == 2  # 1 cluster fusion + 1 isolé
    assert s["n_fused_clusters"] == 1
    assert s["n_corridors_absorbed"] == 1  # c2 absorbé dans c1
    assert s["fusion_distance_m"] == 18.0
    assert s["overlap_ratio_min"] == 0.30
    assert s["doctrine"] == "P22Σ_V3_FUSION_VEINEUSE_Ω"


def test_fuse_empty_list_returns_empty():
    """Liste vide → liste vide."""
    assert fuse_corridors_by_species([]) == []


def test_fuse_single_unit_no_fusion():
    """Un seul corridor → enrichi mais pas fusionné."""
    c = {"id": "c1", "hierarchy": "veine_principale",
         "path": [[48.20, -68.38], [48.21, -68.38]]}
    out = fuse_corridors_by_species([c])
    assert len(out) == 1
    assert out[0]["fusion_count"] == 1
    assert out[0]["intensity_level"] == 2  # principale + fusion=1 → niveau 2


def test_invalid_path_does_not_crash():
    """Path invalide (vide/None) ne crashe pas le module."""
    c1 = {"id": "c1", "hierarchy": "capillaire", "path": None}
    c2 = {"id": "c2", "hierarchy": "capillaire", "path": []}
    c3 = {"id": "c3", "hierarchy": "capillaire", "path": [[48.20, -68.38]]}  # 1 point
    out = fuse_corridors_by_species([c1, c2, c3])
    # Tous retournés tels quels enrichis fusion_count=1
    assert len(out) == 3
    for c in out:
        assert c.get("fusion_count") == 1

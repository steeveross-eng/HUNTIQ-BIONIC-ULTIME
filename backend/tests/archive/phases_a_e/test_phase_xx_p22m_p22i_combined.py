"""
P22M+P22I COMBINED · Pytest neutre
═══════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU · ANTI-GÉNÉRIQUE STRICT

Validation doctrinale :
  - Densification ×3 : 1 nœud parent → 3 nœuds (parent + 2 satellites)
  - Salines/hotspots/refuges NON densifiés
  - Satellites : type identique, score ×0.85, source_id = "{parent}_dnsf{1|2}"
  - Rayon ∈ [40m, 75m], angles séparés de 120°
  - Reproductibilité : déterministe (pas de random)
  - Chained corridors : sequences canoniques par espèce, multi-nœuds
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engines.post_smoothing.anchor_densifier_omega import (
    DENSIFIABLE_TYPES,
    DENSIFY_FACTOR,
    SATELLITE_RADIUS_MAX_M,
    SATELLITE_RADIUS_MIN_M,
    SATELLITE_SCORE_RATIO,
    densification_summary,
    densify_vital_nodes_x3,
)
from engines.post_smoothing.chained_corridors_omega import (
    SPECIES_CHAIN_SEQUENCES,
    chain_corridors_for_species,
    chained_summary,
)


# ═══════════════════ P22M DENSIFIER TESTS ═══════════════════

def test_densify_constants_doctrinal():
    """Vérifie les constantes doctrinales x3."""
    assert DENSIFY_FACTOR == 3
    assert SATELLITE_RADIUS_MIN_M == 40.0
    assert SATELLITE_RADIUS_MAX_M == 75.0
    assert SATELLITE_SCORE_RATIO == 0.85
    assert "alimentation" in DENSIFIABLE_TYPES
    assert "saline" not in DENSIFIABLE_TYPES


def test_densify_empty_list():
    """Liste vide → liste vide."""
    assert densify_vital_nodes_x3([]) == []


def test_densify_alimentation_x3():
    """Un nœud alimentation → 3 nœuds (1 parent + 2 satellites)."""
    n = {"type": "alimentation", "lat": 48.20, "lon": -68.38,
         "score": 80, "source_id": "zone_alim_001"}
    out = densify_vital_nodes_x3([n])
    assert len(out) == 3
    parents = [x for x in out if x.get("_p22m_role") == "PARENT"]
    sats = [x for x in out if x.get("_p22m_role") == "SATELLITE"]
    assert len(parents) == 1
    assert len(sats) == 2
    # Satellites héritent du type
    for s in sats:
        assert s["type"] == "alimentation"
        # Score 85% du parent
        assert abs(s["score"] - 80 * 0.85) < 0.01
        # source_id dérivé
        assert s["source_id"].startswith("zone_alim_001_dnsf")


def test_densify_saline_not_densified():
    """Saline NON densifiée (ressource institutionnelle unique)."""
    n = {"type": "saline", "lat": 48.20, "lon": -68.38,
         "score": 90, "source_id": "saline_001"}
    out = densify_vital_nodes_x3([n])
    assert len(out) == 1
    assert out[0]["_p22m_role"] == "PARENT"


def test_densify_hotspot_not_densified():
    """Hotspot NON densifié."""
    n = {"type": "hotspot", "lat": 48.20, "lon": -68.38,
         "score": 75, "source_id": "hotspot_001"}
    out = densify_vital_nodes_x3([n])
    assert len(out) == 1


def test_densify_satellite_radius_in_range():
    """Satellites dans [40m, 75m] de leur parent."""
    import math
    n = {"type": "rut", "lat": 48.20, "lon": -68.38,
         "score": 70, "source_id": "zone_rut_005"}
    out = densify_vital_nodes_x3([n])
    parent = next(x for x in out if x.get("_p22m_role") == "PARENT")
    sats = [x for x in out if x.get("_p22m_role") == "SATELLITE"]
    for s in sats:
        # Distance haversine
        lat1, lon1 = parent["lat"], parent["lon"]
        lat2, lon2 = s["lat"], s["lon"]
        R = 6371000.0
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlam = math.radians(lon2 - lon1)
        a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2) ** 2
        d = 2 * R * math.asin(math.sqrt(a))
        assert 40.0 - 1.0 <= d <= 75.0 + 1.0


def test_densify_deterministic_reproducible():
    """Même input → même output (déterministe)."""
    n = {"type": "thermique", "lat": 48.20, "lon": -68.38,
         "score": 60, "source_id": "zone_th_007"}
    out1 = densify_vital_nodes_x3([n])
    out2 = densify_vital_nodes_x3([n])
    assert out1[1]["lat"] == out2[1]["lat"]
    assert out1[1]["lon"] == out2[1]["lon"]


def test_densify_summary_factor_3():
    """Summary : densification factor ≈ 3 pour types éligibles uniquement."""
    nodes = [
        {"type": "alimentation", "lat": 48.20, "lon": -68.38, "score": 80, "source_id": "a1"},
        {"type": "repos", "lat": 48.21, "lon": -68.38, "score": 70, "source_id": "r1"},
        {"type": "saline", "lat": 48.22, "lon": -68.38, "score": 90, "source_id": "s1"},
    ]
    out = densify_vital_nodes_x3(nodes)
    s = densification_summary(nodes, out)
    # 2 alim/repos × 3 + 1 saline × 1 = 7
    assert s["n_nodes_after"] == 7
    assert s["n_satellites_generated"] == 4  # 2 satellites × 2 nodes éligibles
    assert s["doctrine"] == "P22M_DENSIFICATION_VITALE_X3_Ω"


# ═══════════════════ P22I CHAINED CORRIDORS TESTS ═══════════════════

def test_chain_sequences_doctrinal():
    """Vérifie les séquences canoniques par espèce."""
    assert ["alimentation", "repos", "rut"] in SPECIES_CHAIN_SEQUENCES["chevreuil"]
    assert ["alimentation", "humide", "repos", "thermique"] in SPECIES_CHAIN_SEQUENCES["orignal"]
    assert "wapiti" in SPECIES_CHAIN_SEQUENCES


def test_chain_no_input_returns_empty():
    """Liste vide → liste vide."""
    out = chain_corridors_for_species([], "chevreuil")
    assert out == []


def test_chain_atomic_routes_preserved():
    """Chains préservent les routes atomiques d'origine."""
    cs = [
        {"id": "network_000", "node_from": {"type": "alimentation"},
         "node_to": {"type": "repos"},
         "path": [[48.20, -68.38], [48.21, -68.38], [48.22, -68.38]],
         "score": 60},
    ]
    out = chain_corridors_for_species(cs, "dindon_sauvage")
    # 1 atomique préservé, pas de chain (séquence requiert 3+ types)
    assert any(c.get("id") == "network_000" for c in out)


def test_chain_real_3_node_sequence():
    """3 nœuds alim→repos→rut générent 1 chain."""
    cs = [
        {"id": "network_000",
         "node_from": {"type": "alimentation", "source_id": "n_alim"},
         "node_to": {"type": "repos", "source_id": "n_repos"},
         "path": [[48.20, -68.38], [48.21, -68.38], [48.215, -68.38]],
         "score": 70},
        {"id": "network_001",
         "node_from": {"type": "repos", "source_id": "n_repos"},
         "node_to": {"type": "rut", "source_id": "n_rut"},
         "path": [[48.215, -68.38], [48.22, -68.38], [48.225, -68.38]],
         "score": 65},
    ]
    out = chain_corridors_for_species(cs, "chevreuil")
    chains = [c for c in out if c.get("_p22i_role") == "CHAINED_CORRIDOR"]
    assert len(chains) >= 1
    chain = chains[0]
    assert chain["intensity_level"] == 3
    assert chain["intensity_label"] == "ÉLEVÉ"
    assert chain["hierarchy"] == "veine_principale"
    assert "network_000" in chain["_p22i_source_corridor_ids"]
    assert "network_001" in chain["_p22i_source_corridor_ids"]


def test_chain_missing_transition_skipped():
    """Si une transition manque, la chain est sautée (anti-générique)."""
    cs = [
        {"id": "network_000",
         "node_from": {"type": "alimentation", "source_id": "n_alim"},
         "node_to": {"type": "repos", "source_id": "n_repos"},
         "path": [[48.20, -68.38], [48.21, -68.38]],
         "score": 70},
        # Aucune connexion repos→rut
    ]
    out = chain_corridors_for_species(cs, "chevreuil")
    chains = [c for c in out if c.get("_p22i_role") == "CHAINED_CORRIDOR"]
    # 1 corridor seul → impossible de former une chain ≥ 3 nodes
    assert len(chains) == 0


def test_chain_summary():
    """Summary chained_summary."""
    cs = [
        {"id": "network_000",
         "node_from": {"type": "alimentation", "source_id": "n_alim"},
         "node_to": {"type": "repos", "source_id": "n_repos"},
         "path": [[48.20, -68.38], [48.205, -68.38], [48.21, -68.38]],
         "score": 70},
        {"id": "network_001",
         "node_from": {"type": "repos", "source_id": "n_repos"},
         "node_to": {"type": "rut", "source_id": "n_rut"},
         "path": [[48.21, -68.38], [48.215, -68.38], [48.22, -68.38]],
         "score": 65},
    ]
    out = chain_corridors_for_species(cs, "chevreuil")
    s = chained_summary(cs, out)
    assert s["n_atomic_corridors"] == 2
    assert s["n_chained_corridors"] >= 1
    assert s["doctrine"] == "P22I_MULTI_ANCHOR_CHAINED_CORRIDORS_Ω"


def test_chain_unknown_species_returns_atomic_only():
    """Espèce inconnue → corridors atomiques inchangés."""
    cs = [{"id": "network_000",
           "node_from": {"type": "alimentation"}, "node_to": {"type": "repos"},
           "path": [[48.20, -68.38]], "score": 60}]
    out = chain_corridors_for_species(cs, "espece_xenomorphe")
    assert len(out) == len(cs)
    assert all(c.get("_p22i_role") != "CHAINED_CORRIDOR" for c in out)

"""
Tests X200-P1-EXTERNAL-INFLOW — ENGINE_RÉSEAU_VEINEUX_Ω
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path("/app/backend")))

import pytest

from engines.reseau_veineux_omega.external_inflow import (
    EXTERNAL_INFLOW_ENABLED,
    EXPECTED_TOKEN,
    HIERARCHY_5_LEVELS_COMMANDANT,
    ENTRY_NODES_MIN, ENTRY_NODES_MAX,
    EXTERNAL_RING_MIN_M, EXTERNAL_RING_MAX_M,
    FUSION_MAX_DISTANCE_M, FUSION_WIDTH_MULTIPLIER,
    DIRECTIONAL_WEIGHTS,
    is_external_inflow_authorized,
    generate_entry_nodes,
    trace_organic_path,
    find_nearest_vital_zone,
    fuse_external_internal,
    classify_corridor_commandant,
    external_inflow_status,
    _haversine_m,
)


# ═══════════════════════════════════════════════════════════════════════
# X200-P1-ACTIVATION — FLAG ON + DOUBLE-VERROU
# ═══════════════════════════════════════════════════════════════════════
def test_flag_on_after_activation():
    """X200-P1-ACTIVATION : flag activé par ordre du Commandant."""
    assert EXTERNAL_INFLOW_ENABLED is True


def test_authorization_granted_with_env_and_token(monkeypatch):
    monkeypatch.setenv("P1_ACTIVATION_AUTHORIZED_BY_COMMANDANT", "true")
    monkeypatch.setenv("P1_COMMANDANT_TOKEN", "STEEVE-MAX-P1-EXTERNAL-INFLOW")
    a = is_external_inflow_authorized()
    assert a["authorized"] is True
    assert a["env_ok"] is True
    assert a["token_ok"] is True


def test_authorization_denied_wrong_token(monkeypatch):
    monkeypatch.setenv("P1_ACTIVATION_AUTHORIZED_BY_COMMANDANT", "true")
    monkeypatch.setenv("P1_COMMANDANT_TOKEN", "WRONG")
    a = is_external_inflow_authorized()
    assert a["authorized"] is False
    assert a["token_ok"] is False


def test_token_required():
    assert EXPECTED_TOKEN == "STEEVE-MAX-P1-EXTERNAL-INFLOW"


# ═══════════════════════════════════════════════════════════════════════
# CONTRAT RENDUΩ (§5.5) — VERSION COMMANDANT
# ═══════════════════════════════════════════════════════════════════════
def test_hierarchy_5_levels_commandant_exact():
    assert len(HIERARCHY_5_LEVELS_COMMANDANT) == 5
    expected = [
        ("CRITIQUE", "#CC0000", 6, 6),
        ("MAJEUR",   "#FF0000", 4, 5),
        ("FORT",     "#FF8C00", 3, 4),
        ("MODERE",   "#FFD700", 2, 3),
        ("FAIBLE",   "#BFBFBF", 1, 2),
    ]
    for i, (level, color, largeur, weight) in enumerate(expected):
        h = HIERARCHY_5_LEVELS_COMMANDANT[i]
        assert h["level"] == level
        assert h["color"] == color
        assert h["largeur_m"] == largeur
        assert h["weight"] == weight


def test_classify_commandant_thresholds():
    assert classify_corridor_commandant(90)["level"] == "CRITIQUE"
    assert classify_corridor_commandant(75)["level"] == "MAJEUR"
    assert classify_corridor_commandant(60)["level"] == "FORT"
    assert classify_corridor_commandant(35)["level"] == "MODERE"
    assert classify_corridor_commandant(10)["level"] == "FAIBLE"


# ═══════════════════════════════════════════════════════════════════════
# SECTION 1 — ENTRY NODES
# ═══════════════════════════════════════════════════════════════════════
def test_entry_nodes_count_clamped_min():
    nodes = generate_entry_nodes(48.2, -68.4, count=5)
    assert len(nodes) == ENTRY_NODES_MIN


def test_entry_nodes_count_clamped_max():
    nodes = generate_entry_nodes(48.2, -68.4, count=50)
    assert len(nodes) == ENTRY_NODES_MAX


def test_entry_nodes_uniform_angular_distribution():
    nodes = generate_entry_nodes(48.2, -68.4, count=24)
    expected_step = 360.0 / 24
    for i in range(len(nodes) - 1):
        delta = nodes[i + 1]["bearing_deg"] - nodes[i]["bearing_deg"]
        assert abs(delta - expected_step) < 0.01


def test_entry_nodes_on_external_ring():
    center = [48.206657, -68.382422]
    nodes = generate_entry_nodes(center[0], center[1], count=16)
    for n in nodes:
        dist = _haversine_m(center, [n["lat"], n["lng"]])
        assert EXTERNAL_RING_MIN_M - 10 <= dist <= EXTERNAL_RING_MAX_M + 10, \
            f"Node {n['id']} off-ring: {dist:.1f}m"


def test_entry_node_weight_in_range():
    nodes = generate_entry_nodes(48.2, -68.4, count=12)
    for n in nodes:
        assert 0.0 <= n["weight"] <= 1.0


def test_directional_weights_sum_to_1():
    total = sum(DIRECTIONAL_WEIGHTS.values())
    assert abs(total - 1.0) < 0.001, f"sum={total}"


def test_directional_weights_spec():
    """Pondération §5.2 : hydro 40%, slope 25%, forest 20%, vital 15%."""
    assert DIRECTIONAL_WEIGHTS["hydro"] == 0.40
    assert DIRECTIONAL_WEIGHTS["slope"] == 0.25
    assert DIRECTIONAL_WEIGHTS["forest_cover"] == 0.20
    assert DIRECTIONAL_WEIGHTS["vital_zones"] == 0.15


# ═══════════════════════════════════════════════════════════════════════
# SECTION 2 — TRAÇAGE ORGANIQUE
# ═══════════════════════════════════════════════════════════════════════
def test_trace_organic_path_endpoints():
    entry = {"lat": 48.21, "lng": -68.39, "id": "ext_0"}
    target = {"lat": 48.206657, "lng": -68.382422, "type": "salines"}
    path = trace_organic_path(entry, target)
    assert len(path) == 28
    # Départ ≈ entry, arrivée ≈ target
    assert abs(path[0][0] - entry["lat"]) < 1e-4
    assert abs(path[-1][0] - target["lat"]) < 1e-4


def test_trace_organic_path_is_curved():
    """Le path doit avoir une courbure (pas une droite entre entry et target)."""
    entry = {"lat": 48.21, "lng": -68.39}
    target = {"lat": 48.20, "lng": -68.37, "type": "salines"}
    path = trace_organic_path(entry, target)
    # Distance réelle du path vs distance directe
    direct = _haversine_m([entry["lat"], entry["lng"]], [target["lat"], target["lng"]])
    path_len = sum(_haversine_m(path[i], path[i + 1]) for i in range(len(path) - 1))
    assert path_len > direct  # courbure = path plus long que droite


def test_find_nearest_vital_zone():
    entry = {"lat": 48.21, "lng": -68.39}
    zones = [
        {"type": "salines", "lat": 48.25, "lng": -68.40, "score": 90},
        {"type": "repos",   "lat": 48.21, "lng": -68.391, "score": 60},
    ]
    target = find_nearest_vital_zone(entry, zones)
    # Repos plus proche devrait gagner malgré score plus bas (distance dominante)
    assert target["type"] == "repos"


def test_find_nearest_vital_zone_none_when_empty():
    assert find_nearest_vital_zone({"lat": 48, "lng": -68}, []) is None


# ═══════════════════════════════════════════════════════════════════════
# SECTION 2.2 — FUSION
# ═══════════════════════════════════════════════════════════════════════
def test_fusion_detects_contact_under_75m():
    external = [{
        "id": "ext_0", "largeur_m": 3,
        "path": [[48.2068, -68.3822], [48.2067, -68.3823]],
    }]
    internal = [{
        "id": "int_0", "largeur_m": 2,
        "path": [[48.2067, -68.3823], [48.2066, -68.3824]],  # contact direct
    }]
    result = fuse_external_internal(external, internal)
    assert result["fusions_detected"] == 1
    assert result["fusion_points"][0]["width_multiplier"] == FUSION_WIDTH_MULTIPLIER
    assert result["fusion_points"][0]["new_width_m"] == 4.5  # max(3,2)*1.5


def test_fusion_ignores_beyond_75m():
    external = [{"id": "ext_0", "largeur_m": 3, "path": [[48.22, -68.39]]}]
    internal = [{"id": "int_0", "largeur_m": 2, "path": [[48.20, -68.40]]}]  # >2km
    result = fuse_external_internal(external, internal)
    assert result["fusions_detected"] == 0


def test_fusion_threshold_is_75m():
    from engines.reseau_veineux_omega.external_inflow import FUSION_MAX_DISTANCE_M
    assert FUSION_MAX_DISTANCE_M == 75


def test_fusion_width_multiplier_is_1_5():
    from engines.reseau_veineux_omega.external_inflow import FUSION_WIDTH_MULTIPLIER
    assert FUSION_WIDTH_MULTIPLIER == 1.5


# ═══════════════════════════════════════════════════════════════════════
# DIAGRAMME CONCEPTUEL — validation §5.1 à §5.4
# ═══════════════════════════════════════════════════════════════════════
def test_diagram_constants():
    from engines.reseau_veineux_omega.external_inflow import (
        INNER_RADIUS_NOMINAL_M, INNER_RADIUS_TOLERANCE_PCT,
    )
    assert INNER_RADIUS_NOMINAL_M == 600
    assert INNER_RADIUS_TOLERANCE_PCT == 0.30
    assert EXTERNAL_RING_MIN_M == 700
    assert EXTERNAL_RING_MAX_M == 800
    assert ENTRY_NODES_MIN == 12
    assert ENTRY_NODES_MAX == 24


def test_status_contract_read_only():
    s = external_inflow_status()
    assert s["smoother_touched"] is False
    assert s["rendu_modified"] is False
    # authorized dépend des env vars runtime ; on vérifie seulement la structure
    assert "authorization" in s
    assert "diagram_spec" in s


# ═══════════════════════════════════════════════════════════════════════
# INTÉGRATION END-TO-END (lecture seule)
# ═══════════════════════════════════════════════════════════════════════
def test_end_to_end_preview():
    """Scénario complet : 16 entry_nodes → tracés vers 2 zones → fusion."""
    center = [48.206657, -68.382422]
    vital_zones = [
        {"type": "salines", "lat": 48.2067, "lng": -68.3824, "score": 90},
        {"type": "repos",   "lat": 48.2068, "lng": -68.3823, "score": 70},
    ]
    nodes = generate_entry_nodes(center[0], center[1], count=16,
                                  terrain_signals={"vital_zones": vital_zones})
    assert len(nodes) == 16
    # Chaque node doit tracer vers la zone la plus probable
    external_paths = []
    for n in nodes:
        t = find_nearest_vital_zone(n, vital_zones)
        assert t is not None
        external_paths.append({
            "id": f"ext_{n['index']:02d}", "largeur_m": 3,
            "path": trace_organic_path(n, t),
        })
    assert len(external_paths) == 16
    # Chaque path atteint effectivement la zone (dernier point proche)
    for ep in external_paths:
        last = ep["path"][-1]
        # Distance dernier point à l'une des zones vitales ≤ 5m
        min_d = min(_haversine_m(last, [z["lat"], z["lng"]]) for z in vital_zones)
        assert min_d < 5, f"Path {ep['id']} n'atteint pas la zone: {min_d:.1f}m"

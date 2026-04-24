"""
tests/test_veineux_omega_xii_supra.py
=====================================
PHASE_XII_SUPRA_CORRIDORS_VEINEUX_Ω_ULTIME
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, "/app/backend")
os.environ.setdefault("VEINEUX_OMEGA_AUTHORIZED_BY_COMMANDANT", "true")
os.environ.setdefault("VEINEUX_OMEGA_COMMANDANT_TOKEN", "STEEVE-MAX-XII-VEINEUX-EXPLICIT")

from engines.post_smoothing import veineux_omega as vo  # noqa: E402


def _mk_corridor(cid, path, species="orignal"):
    return {"id": cid, "path": path, "species": species}


def test_triple_verrou_veineux_authorized():
    auth = vo.is_veineux_authorized()
    assert auth["authorized"] is True


def test_catmullrom_exact_endpoints():
    # Un chemin simple de 3 points droits en V → CatmullRom doit garder p0 et p(-1)
    p = [[48.20, -68.38], [48.21, -68.37], [48.22, -68.36]]
    out = vo._catmullrom_path(p, n_out=28)
    assert out[0] == [48.20, -68.38]
    assert out[-1] == [48.22, -68.36]
    assert len(out) == 28


def test_resample_uniform_n_points():
    p = [[0.0, 0.0], [1.0, 0.0], [2.0, 0.0], [3.0, 0.0]]
    out = vo._resample_uniform_n(p, 28)
    assert len(out) == 28


def test_full_pipeline_produces_25_30_points_and_low_seg():
    """Un corridor V30 avec long segment produit un output conforme X150."""
    # Long chemin 1200m N-S avec cassure
    path = [
        [48.200, -68.380],
        [48.205, -68.380],  # ~555m N
        [48.207, -68.375],  # ~700m NE
        [48.208, -68.378],  # 200m
    ]
    out = vo._process_single_corridor(
        _mk_corridor("c1", path), water_points=[], contam_zones=[], bundle_species="orignal"
    )
    assert out is not None
    assert 25 <= len(out["path"]) <= 30
    assert out["veineux_metrics"]["max_segment_m"] <= vo.MAX_SEGMENT_M + 0.5
    assert out["species"] == "orignal"


def test_radial_convergence_removes_excess():
    # 5 corridors convergent vers (48.206657, -68.382422) → 5 - 3 = 2 à retirer
    conv = [48.206657, -68.382422]
    corrs = [
        _mk_corridor(f"cR{i}", [[conv[0], conv[1]], [48.210 + i * 0.001, -68.380]])
        for i in range(5)
    ]
    ids_remove = vo._detect_radial_convergence(corrs)
    assert len(ids_remove) == 2


def test_water_avoidance_pushes_points_out():
    # Corridor passant à 5m d'un point d'eau → doit être décalé
    water = [{"lat": 48.20500, "lng": -68.38000}]
    path = [
        [48.20495, -68.38020],
        [48.20500, -68.38010],  # très proche eau
        [48.20500, -68.38005],
        [48.20510, -68.38000],
    ]
    out = vo._avoid_water_points(path, water, buffer_m=25.0)
    moved = [(a != b) for (a, b) in zip(out, path)]
    assert any(moved)


def test_apply_veineux_omega_to_bundle_sets_flag():
    bundle = {
        "corridors": [
            _mk_corridor("cX",
                         [[48.200, -68.380], [48.210, -68.370], [48.220, -68.360]]),
        ],
        "terrain_signals": {"water_points": []},
        "species": "orignal",
    }
    out = vo.apply_veineux_omega_to_bundle(bundle)
    assert out["veineux_omega_applied_at_bundle"] is True
    assert out["veineux_omega_stats"]["input"] == 1
    assert out["veineux_omega_stats"]["output"] == 1
    c = out["corridors"][0]
    assert c.get("veineux_omega_applied") is True
    assert 25 <= len(c["path"]) <= 30


def test_veineux_respects_species_per_corridor():
    bundle = {
        "corridors": [_mk_corridor("c1",
                                   [[48.20, -68.38], [48.21, -68.37]], species="cerf")],
        "species": "orignal",
    }
    out = vo.apply_veineux_omega_to_bundle(bundle)
    assert out["corridors"][0]["species"] == "cerf"


def test_final_budget_never_exceeded():
    """Même avec un corridor de 3 km, la longueur finale ≤ FINAL_LEN_BUDGET + marge."""
    long_path = [[48.200 + i * 0.002, -68.380] for i in range(15)]  # ~3.3 km
    out = vo._process_single_corridor(
        _mk_corridor("long", long_path), water_points=[], contam_zones=[], bundle_species="orignal"
    )
    assert out is not None
    assert out["veineux_metrics"]["length_m"] <= vo.FINAL_LEN_BUDGET_M + 2.0


def test_v30_not_modified():
    """V30 LOCKED : le hook ne doit pas altérer le hash du registre."""
    from engines.v8_institutional import registry_lock_omega as r
    before = r._registry_hash()
    _ = vo.apply_veineux_omega_to_bundle({
        "corridors": [_mk_corridor("c1", [[48.20, -68.38], [48.21, -68.37]])],
    })
    after = r._registry_hash()
    assert before == after

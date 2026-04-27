"""
test_phase_xvii_ecological_omega.py — PHASE_XVII_SUPRA_ENGINE_CORRIDORS_ECOLOGIQUE_Ω
====================================================================================
Tests d'activation institutionnelle de l'orchestrateur écologique unifié.

Ces tests CERTIFIENT :
  1. Les 6 heatmaps réelles sont présentes et samplables
  2. Le sampling lat/lng → valeur fonctionne (nearest-neighbor)
  3. La règle §3 "30% externe" est appliquée (au moins une extrémité)
  4. La règle §4 "≥ 2 zones vitales" est appliquée
  5. Le pipeline bundle complet retourne des stats enrichies V2
  6. Le mode ENFORCE filtre effectivement les corridors non conformes
  7. Les 5 espèces officielles produisent toutes des corridors validés

Lancement: cd /app/backend && python -m pytest tests/test_phase_xvii_ecological_omega.py -v
"""
import os
import sys
import asyncio
import pytest

sys.path.insert(0, "/app/backend")

OFFICIAL_LAT = 48.206657
OFFICIAL_LNG = -68.382422


# ───────────────────────────────────────────────────────────────────────
# Fixtures
# ───────────────────────────────────────────────────────────────────────
@pytest.fixture(autouse=True)
def reset_cache():
    """Purge le cache disque + LRU + cache heatmaps avant chaque test.
    
    Désactive aussi XIX-P1 ENFORCE pour ne pas filtrer les corridors V30
    avant validation écologique XVII (test isolé).
    """
    pkl = "/app/backend/cache/territoire_bundle.pkl"
    if os.path.exists(pkl):
        os.remove(pkl)
    from engines.v8_institutional import v20_performance_bundle as vp
    vp._CACHE.clear()
    from engines.v8_institutional.ecological_orchestrator_omega import reset_heatmap_cache
    reset_heatmap_cache()
    # XIX-P1 désactivé pour ne pas interférer avec les tests XVII isolés
    import engines.v8_institutional.origine_externe_filter_omega as xix
    _saved_enforce = xix.ENFORCE_MODE
    xix.ENFORCE_MODE = False
    # XIX-P2 désactivé — pas de modification du path en isolation XVII
    import engines.v8_institutional.origine_externe_inversion_omega as xix2
    _saved_xix2 = xix2.ENFORCE_MODE
    xix2.ENFORCE_MODE = False
    yield
    xix.ENFORCE_MODE = _saved_enforce
    xix2.ENFORCE_MODE = _saved_xix2


# ───────────────────────────────────────────────────────────────────────
# 1. Heatmaps disponibles
# ───────────────────────────────────────────────────────────────────────
def test_heatmaps_all_available():
    from engines.v8_institutional.ecological_orchestrator_omega import get_heatmaps_status
    s = get_heatmaps_status()
    assert s["all_available"] is True, f"Heatmaps manquantes: {s['sources']}"
    assert s["fallback_mode"] is False
    for key, info in s["sources"].items():
        assert info["present"], f"{key} manquant: {info['path']}"
        assert info["size_bytes"] > 1000, f"{key} trop petit: {info['size_bytes']}"


# ───────────────────────────────────────────────────────────────────────
# 2. Sampling
# ───────────────────────────────────────────────────────────────────────
def test_heatmap_sampling_at_anchor_returns_value():
    from engines.v8_institutional.ecological_orchestrator_omega import (
        _load_heatmap, _sample_heatmap_at,
    )
    hm = _load_heatmap("nasa_ndvi")
    assert hm is not None
    v = _sample_heatmap_at(hm, OFFICIAL_LAT, OFFICIAL_LNG)
    assert v is not None
    assert 0.0 <= v <= 1.0


def test_heatmap_sampling_outside_grid_returns_none():
    from engines.v8_institutional.ecological_orchestrator_omega import (
        _load_heatmap, _sample_heatmap_at,
    )
    hm = _load_heatmap("noaa_neige")
    v = _sample_heatmap_at(hm, OFFICIAL_LAT + 0.5, OFFICIAL_LNG + 0.5)
    assert v is None


# ───────────────────────────────────────────────────────────────────────
# 3. Règle §3 — couronne externe 30%
# ───────────────────────────────────────────────────────────────────────
def test_external_ring_radius_30pct():
    from engines.v8_institutional.ecological_orchestrator_omega import (
        compute_external_ring_radius, EXTERNAL_RING_FRACTION,
    )
    assert EXTERNAL_RING_FRACTION == 0.30
    r_in, r_out = compute_external_ring_radius(780.0)
    assert abs(r_in - 546.0) < 0.01
    assert r_out == 780.0


def test_path_rejected_when_no_extremity_in_ring():
    """Un trajet 100%-interne (origine ET fin sous 546m) DOIT être rejeté."""
    from engines.v8_institutional.ecological_orchestrator_omega import (
        synthesize_ecological_layers_for_corridor,
    )
    waypoint = {"lat": OFFICIAL_LAT, "lng": OFFICIAL_LNG}
    # corridor entièrement interne (~ 100m du waypoint)
    corridor = {"path": [
        [OFFICIAL_LAT + 0.0005, OFFICIAL_LNG + 0.0005],
        [OFFICIAL_LAT + 0.0008, OFFICIAL_LNG + 0.0008],
        [OFFICIAL_LAT + 0.001,  OFFICIAL_LNG + 0.001],
    ]}
    out = synthesize_ecological_layers_for_corridor(
        corridor, species="orignal", waypoint=waypoint,
        bundle_zones=[], bundle_salines=[], r_max_m=780.0,
    )
    assert out["valid"] is False
    # peut échouer pour zones vitales OU pour ring — les 2 sont blocants
    assert out["reason"].startswith("fail_"), out["reason"]


def test_path_accepted_when_endpoint_in_ring_with_zones():
    """Un trajet avec extrémité dans la couronne + 2 zones DOIT passer."""
    from engines.v8_institutional.ecological_orchestrator_omega import (
        synthesize_ecological_layers_for_corridor,
    )
    waypoint = {"lat": OFFICIAL_LAT, "lng": OFFICIAL_LNG}
    # corridor partant du centre vers ~ 700m (path[-1] dans la couronne)
    corridor = {"path": [
        [OFFICIAL_LAT + 0.001, OFFICIAL_LNG + 0.001],
        [OFFICIAL_LAT + 0.003, OFFICIAL_LNG + 0.003],
        [OFFICIAL_LAT + 0.0055, OFFICIAL_LNG + 0.0055],  # ~ 800m du wp
    ]}
    # 2 zones vitales proches du path
    zones = [
        {"polygon": [
            [OFFICIAL_LAT + 0.0028, OFFICIAL_LNG + 0.0028],
            [OFFICIAL_LAT + 0.0032, OFFICIAL_LNG + 0.0028],
            [OFFICIAL_LAT + 0.0032, OFFICIAL_LNG + 0.0032],
            [OFFICIAL_LAT + 0.0028, OFFICIAL_LNG + 0.0032],
        ], "type": "alimentation"},
        {"polygon": [
            [OFFICIAL_LAT + 0.005, OFFICIAL_LNG + 0.005],
            [OFFICIAL_LAT + 0.006, OFFICIAL_LNG + 0.005],
            [OFFICIAL_LAT + 0.006, OFFICIAL_LNG + 0.006],
            [OFFICIAL_LAT + 0.005, OFFICIAL_LNG + 0.006],
        ], "type": "rut"},
    ]
    out = synthesize_ecological_layers_for_corridor(
        corridor, species="orignal", waypoint=waypoint,
        bundle_zones=zones, bundle_salines=[], r_max_m=780.0,
    )
    assert out["metrics"]["endpoint_in_external_ring_30pct"] is True, out["metrics"]
    assert out["metrics"]["zones_touched"] >= 2, out["metrics"]
    assert out["valid"] is True, out


# ───────────────────────────────────────────────────────────────────────
# 4. Pipeline bundle complet — toutes espèces officielles
# ───────────────────────────────────────────────────────────────────────
@pytest.mark.parametrize("species", ["orignal", "chevreuil", "wapiti", "ours", "dindon"])
def test_bundle_pipeline_phase_xvii_per_species(species):
    """Pour CHACUNE des 5 espèces, le bundle doit fournir des stats V2."""
    from fastapi import Response
    from engines.v8_institutional.v20_performance_bundle import v20_territoire_bundle

    async def go():
        r = Response()
        return await v20_territoire_bundle(
            response=r, lat=OFFICIAL_LAT, lon=OFFICIAL_LNG, species=species,
            month=10, hour=14, wind_deg=225.0, wind_speed=15.0,
        )

    bundle = asyncio.run(go())
    stats = bundle.get("ecological_orchestrator_stats") or {}
    # Stats V2 obligatoires
    assert "total_input" in stats, stats
    assert "total_output" in stats
    assert "rejected_reasons" in stats
    assert "enforce_mode" in stats
    assert stats["enforce_mode"] is True
    # Heatmaps lues
    assert stats["heatmaps_status"]["all_available"] is True
    # Au moins 1 corridor passant pour chaque espèce
    assert stats["passing_consensus"] >= 1, (
        f"{species}: 0 corridors valides — règles trop strictes ? rej={stats.get('rejected_reasons')}"
    )
    # Tous les corridors output ont leur consensus
    for c in bundle.get("corridors") or []:
        eco = c.get("ecological_consensus") or {}
        assert eco.get("valid") is True
        cs = (eco.get("consensus") or {}).get("consensus_score")
        assert cs is not None and cs >= 50, (species, c.get("id"), cs)


# ───────────────────────────────────────────────────────────────────────
# 5. Endpoint observabilité
# ───────────────────────────────────────────────────────────────────────
def test_endpoint_ecological_orchestrator_returns_v2_stats():
    from fastapi.testclient import TestClient
    # NOTE : le serveur global est lourd ; on monte juste le router
    from fastapi import FastAPI
    from routes.ecological_orchestrator_router import router as r
    app = FastAPI()
    app.include_router(r)
    c = TestClient(app)
    resp = c.get("/api/v30/corridors/ecological-orchestrator?species=orignal&month=10&hour=14")
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["phase"] == "PHASE_XVII_SUPRA_ENGINE_CORRIDORS_ECOLOGIQUE_Ω"
    assert data["heatmaps_status"]["all_available"] is True
    assert data["external_ring_fraction"] == 0.30
    assert "stats" in data
    assert data["stats"]["enforce_mode"] is True

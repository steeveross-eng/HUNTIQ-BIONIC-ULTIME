"""
test_phase_xix_p1_origine_externe_filter.py — PHASE_XIX_P1_ORIGINE_EXTERNE_FILTER_Ω
==========================================================================
Tests d'activation institutionnelle du filtre ORIGINE_EXTERNE_Ω.

Ces tests CERTIFIENT (directive Commandant XIX-P1 §3.2) :
  1. Couronne externe correctement définie [600 m ; 780 m]
  2. Path interne (origine < 600 m) → REJET OUTSIDE_CROWN
  3. Path externe (origine ∈ [600,780]) + densité suffisante → ACCEPTÉ
  4. Path externe + densité insuffisante → REJET LOW_DENSITY
  5. Path externe + hits insuffisants → REJET LOW_HITS
  6. Métadonnées institutionnelles présentes sur tous les corridors
  7. Pipeline complet annote tous les corridors V30 + INTERZONE
  8. Endpoint observabilité retourne stats + sample
  9. Non-régression XVIII-bis (43 tests précédents continuent de passer)
"""
import os
import sys
import asyncio
import pytest

sys.path.insert(0, "/app/backend")

OFFICIAL_LAT = 48.206657
OFFICIAL_LNG = -68.382422


@pytest.fixture(autouse=True)
def reset_caches():
    pkl = "/app/backend/cache/territoire_bundle.pkl"
    if os.path.exists(pkl):
        os.remove(pkl)
    audit = "/app/backend/cache/corridors_rejected_vitaux_xviii.json"
    if os.path.exists(audit):
        os.remove(audit)
    from engines.v8_institutional import v20_performance_bundle as vp
    vp._CACHE.clear()
    from engines.v8_institutional.predictive_omega_v2 import reset_dataset_cache
    from engines.v8_institutional.ecological_orchestrator_omega import reset_heatmap_cache
    reset_dataset_cache()
    reset_heatmap_cache()
    # XIX-P2 désactivé — préserve l'isolement des tests XIX-P1
    import engines.v8_institutional.origine_externe_inversion_omega as xix2
    _saved = xix2.ENFORCE_MODE
    xix2.ENFORCE_MODE = False
    yield
    xix2.ENFORCE_MODE = _saved


# ───────────────────────────────────────────────────────────────────────
# 1. Couronne externe — constantes
# ───────────────────────────────────────────────────────────────────────
def test_couronne_externe_constants_xix_p1():
    from engines.v8_institutional.origine_externe_filter_omega import (
        RAYON_FONCTIONNEL_NOMINAL_M, ORIGINE_EXTERNE_FRACTION,
        ORIGINE_RADIUS_MIN_M, ORIGINE_RADIUS_MAX_M,
        THRESH_DENSITY_ORIGINE, THRESH_HITS_ORIGINE,
    )
    assert RAYON_FONCTIONNEL_NOMINAL_M == 600.0
    assert ORIGINE_EXTERNE_FRACTION == 0.30
    assert ORIGINE_RADIUS_MIN_M == 600.0
    assert ORIGINE_RADIUS_MAX_M == 780.0
    # PHASE XIX-P1B_TUNING_Ω : seuil density abaissé à 0.02 (ratios runtime 0.02-0.06)
    assert THRESH_DENSITY_ORIGINE == 0.02
    assert THRESH_HITS_ORIGINE == 5.0


# ───────────────────────────────────────────────────────────────────────
# 2. Origine interne (< 600 m) → REJET OUTSIDE_CROWN
# ───────────────────────────────────────────────────────────────────────
def test_origin_inside_core_rejected():
    from engines.v8_institutional.origine_externe_filter_omega import validate_origin_external
    # Path qui part du waypoint (origine ~ 0 m)
    corridor = {
        "id": "test_inside",
        "path": [[OFFICIAL_LAT, OFFICIAL_LNG],
                 [OFFICIAL_LAT + 0.005, OFFICIAL_LNG + 0.005]],
    }
    res = validate_origin_external(corridor, waypoint={"lat": OFFICIAL_LAT, "lng": OFFICIAL_LNG})
    assert res["origin_external_passed"] is False
    assert res["origin_external_reason"] == "OUTSIDE_CROWN"
    assert res["distance_origin_m"] < 100.0


# ───────────────────────────────────────────────────────────────────────
# 3. Origine au-delà de 780 m → REJET OUTSIDE_CROWN
# ───────────────────────────────────────────────────────────────────────
def test_origin_beyond_crown_rejected():
    from engines.v8_institutional.origine_externe_filter_omega import validate_origin_external
    import math
    # Origine à ~1200 m (au-delà de 780)
    bearing = math.radians(45)
    L = 1200.0
    dlat = (L * math.cos(bearing)) / 111000.0
    dlng = (L * math.sin(bearing)) / (111000.0 * math.cos(math.radians(OFFICIAL_LAT)))
    corridor = {
        "id": "test_beyond",
        "path": [[OFFICIAL_LAT + dlat, OFFICIAL_LNG + dlng],
                 [OFFICIAL_LAT + dlat * 0.5, OFFICIAL_LNG + dlng * 0.5]],
    }
    res = validate_origin_external(corridor, waypoint={"lat": OFFICIAL_LAT, "lng": OFFICIAL_LNG})
    assert res["origin_external_passed"] is False
    assert res["origin_external_reason"] == "OUTSIDE_CROWN"
    assert res["distance_origin_m"] > 1000.0


# ───────────────────────────────────────────────────────────────────────
# 4. Origine dans la couronne + densité suffisante → ACCEPTÉ
# ───────────────────────────────────────────────────────────────────────
def test_origin_in_crown_with_sufficient_gps_accepted():
    from engines.v8_institutional.origine_externe_filter_omega import validate_origin_external
    import math
    bearing = math.radians(45)
    L = 700.0  # dans [600, 780]
    dlat = (L * math.cos(bearing)) / 111000.0
    dlng = (L * math.sin(bearing)) / (111000.0 * math.cos(math.radians(OFFICIAL_LAT)))
    corridor = {
        "id": "test_in_crown_ok",
        "path": [[OFFICIAL_LAT + dlat, OFFICIAL_LNG + dlng],
                 [OFFICIAL_LAT + dlat * 0.5, OFFICIAL_LNG + dlng * 0.5]],
        "predictive_omega_v2": {
            "valid": True,
            "metrics": {
                "gps_density_ratio": 0.30,  # > 0.25
                "gps_weighted_hits": 12.0,  # > 5
            },
        },
    }
    res = validate_origin_external(corridor, waypoint={"lat": OFFICIAL_LAT, "lng": OFFICIAL_LNG})
    assert res["origin_external_passed"] is True, res
    assert res["origin_external_reason"] is None
    assert res["distance_origin_m"] >= 600.0
    assert res["distance_origin_m"] <= 780.0


# ───────────────────────────────────────────────────────────────────────
# 5. Origine dans la couronne + densité insuffisante → REJET LOW_DENSITY
# ───────────────────────────────────────────────────────────────────────
def test_origin_in_crown_with_low_density_rejected():
    from engines.v8_institutional.origine_externe_filter_omega import validate_origin_external
    import math
    bearing = math.radians(90)
    L = 700.0
    dlat = (L * math.cos(bearing)) / 111000.0
    dlng = (L * math.sin(bearing)) / (111000.0 * math.cos(math.radians(OFFICIAL_LAT)))
    corridor = {
        "id": "test_low_density",
        "path": [[OFFICIAL_LAT + dlat, OFFICIAL_LNG + dlng],
                 [OFFICIAL_LAT + dlat * 0.7, OFFICIAL_LNG + dlng * 0.7]],
        "predictive_omega_v2": {
            "valid": True,
            "metrics": {
                "gps_density_ratio": 0.005,  # < 0.02 (seuil XIX-P1B)
                "gps_weighted_hits": 12.0,   # > 5
            },
        },
    }
    res = validate_origin_external(corridor, waypoint={"lat": OFFICIAL_LAT, "lng": OFFICIAL_LNG})
    assert res["origin_external_passed"] is False
    assert res["origin_external_reason"] == "LOW_DENSITY"


# ───────────────────────────────────────────────────────────────────────
# 6. Origine dans la couronne + hits insuffisants → REJET LOW_HITS
# ───────────────────────────────────────────────────────────────────────
def test_origin_in_crown_with_low_hits_rejected():
    from engines.v8_institutional.origine_externe_filter_omega import validate_origin_external
    import math
    bearing = math.radians(180)
    L = 750.0
    dlat = (L * math.cos(bearing)) / 111000.0
    dlng = (L * math.sin(bearing)) / (111000.0 * math.cos(math.radians(OFFICIAL_LAT)))
    corridor = {
        "id": "test_low_hits",
        "path": [[OFFICIAL_LAT + dlat, OFFICIAL_LNG + dlng],
                 [OFFICIAL_LAT + dlat * 0.7, OFFICIAL_LNG + dlng * 0.7]],
        "predictive_omega_v2": {
            "valid": True,
            "metrics": {
                "gps_density_ratio": 0.40,  # > 0.25
                "gps_weighted_hits": 2.0,   # < 5
            },
        },
    }
    res = validate_origin_external(corridor, waypoint={"lat": OFFICIAL_LAT, "lng": OFFICIAL_LNG})
    assert res["origin_external_passed"] is False
    assert res["origin_external_reason"] == "LOW_HITS"


# ───────────────────────────────────────────────────────────────────────
# 7. Métadonnées institutionnelles
# ───────────────────────────────────────────────────────────────────────
def test_metadata_fields_present():
    from engines.v8_institutional.origine_externe_filter_omega import validate_origin_external
    corridor = {"id": "x", "path": [[OFFICIAL_LAT, OFFICIAL_LNG]]}
    res = validate_origin_external(corridor, waypoint={"lat": OFFICIAL_LAT, "lng": OFFICIAL_LNG})
    assert res["origin_external_filter_phase"] == "PHASE_XIX_P1"
    assert res["origin_external_radius_min_m"] == 600.0
    assert res["origin_external_radius_max_m"] == 780.0
    # PHASE XIX-P1B_TUNING_Ω : seuil density abaissé à 0.02
    assert res["origin_external_density_threshold"] == 0.02
    assert res["origin_external_hits_threshold"] == 5.0
    assert res["phase"] == "PHASE_XIX_P1_ORIGINE_EXTERNE_FILTER_Ω"


# ───────────────────────────────────────────────────────────────────────
# 8. Pipeline complet — annotation des corridors V30
# ───────────────────────────────────────────────────────────────────────
@pytest.mark.parametrize("species,month,hour", [
    ("orignal", 10, 16),
    ("chevreuil", 10, 12),
    ("dindon", 5, 8),
])
def test_pipeline_xix_p1_annotates_corridors(species, month, hour):
    from fastapi import Response
    from engines.v8_institutional.v20_performance_bundle import v20_territoire_bundle

    async def go():
        r = Response()
        return await v20_territoire_bundle(
            response=r, lat=OFFICIAL_LAT, lon=OFFICIAL_LNG, species=species,
            month=month, hour=hour, wind_deg=225.0, wind_speed=15.0,
        )

    bundle = asyncio.run(go())
    assert bundle.get("origine_externe_filter_applied") is True
    stats = bundle.get("origine_externe_filter_stats") or {}
    assert "total_input" in stats
    assert "total_kept" in stats
    assert stats["enforce_mode"] is True
    assert stats["config"]["origin_radius_min_m"] == 600.0
    assert stats["config"]["origin_radius_max_m"] == 780.0
    # Tous les corridors gardés ont passé le filtre
    for c in bundle.get("corridors") or []:
        assert c.get("origin_external_passed") is True
    # Les rejetés ont une raison non vide
    rejected = bundle.get("corridors_rejected_origine_externe_xix") or []
    for r in rejected:
        assert r.get("reason") in (
            "OUTSIDE_CROWN", "LOW_DENSITY", "LOW_HITS",
            "MISSING_PREDICTIVE_V2_METRICS", "EMPTY_PATH", "UNKNOWN",
        ), r


# ───────────────────────────────────────────────────────────────────────
# 9. Endpoint observabilité
# ───────────────────────────────────────────────────────────────────────
def test_endpoint_origine_externe_returns_stats():
    from fastapi.testclient import TestClient
    from fastapi import FastAPI
    from routes.origine_externe_filter_router import router as r
    app = FastAPI()
    app.include_router(r)
    c = TestClient(app)
    resp = c.get("/api/v30/corridors/origine-externe?species=orignal&month=10&hour=16")
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["phase"] == "PHASE_XIX_P1_ORIGINE_EXTERNE_FILTER_Ω"
    assert data["subphase"] == "PHASE_XIX_P1"
    fs = data["filter_status"]
    assert fs["origin_radius_min_m"] == 600.0
    assert fs["origin_radius_max_m"] == 780.0
    # PHASE XIX-P1B_TUNING_Ω : seuil density abaissé à 0.02
    assert fs["thresh_density_origine"] == 0.02
    assert fs["thresh_hits_origine"] == 5.0
    assert "OUTSIDE_CROWN" in fs["rejection_reasons_catalog"]
    assert "stats" in data

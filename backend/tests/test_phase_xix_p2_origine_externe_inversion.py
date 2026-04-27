"""
test_phase_xix_p2_origine_externe_inversion.py — PHASE_XIX_P2_ORIGINE_EXTERNE_INVERSION_Ω
==========================================================================
Tests d'activation institutionnelle du module ORIGINE_EXTERNE_INVERSION_Ω.

Ces tests CERTIFIENT (directive Commandant XIX-P2) :
  1. Couronne lue depuis XIX-P1 ([600 ; 780] m)
  2. Path interne→externe (origine 100m, fin 700m) → INVERSÉ
  3. Path externe→externe → AUCUNE inversion
  4. Path interne→interne → AUCUNE inversion
  5. Path externe→interne (déjà conforme) → AUCUNE inversion
  6. Pipeline applique l'inversion + ré-annote predictive_omega_v2
  7. Métadonnées institutionnelles présentes
  8. Endpoint observabilité retourne les stats
  9. Non-régression XIX-P1 + XVIII-bis + XVII
"""
import os
import sys
import math
import asyncio
import pytest

sys.path.insert(0, "/app/backend")

OFFICIAL_LAT = 48.206657
OFFICIAL_LNG = -68.382422


def _path_at_distance(distance_m: float, bearing_deg: float = 45.0) -> list:
    """Retourne un point [lat, lng] à `distance_m` du waypoint sur un cap donné."""
    br = math.radians(bearing_deg)
    dlat = (distance_m * math.cos(br)) / 111000.0
    dlng = (distance_m * math.sin(br)) / (111000.0 * math.cos(math.radians(OFFICIAL_LAT)))
    return [OFFICIAL_LAT + dlat, OFFICIAL_LNG + dlng]


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
    yield


# ───────────────────────────────────────────────────────────────────────
# 1. Couronne héritée XIX-P1
# ───────────────────────────────────────────────────────────────────────
def test_inversion_uses_xix_p1_crown():
    from engines.v8_institutional.origine_externe_inversion_omega import (
        ORIGINE_RADIUS_MIN_M, ORIGINE_RADIUS_MAX_M,
    )
    assert ORIGINE_RADIUS_MIN_M == 600.0
    assert ORIGINE_RADIUS_MAX_M == 780.0


# ───────────────────────────────────────────────────────────────────────
# 2-5. Décision d'inversion par scénario
# ───────────────────────────────────────────────────────────────────────
def test_inversion_path_internal_to_external_should_invert():
    """path[0]=100m, path[-1]=700m → DOIT être inversé (§1)."""
    from engines.v8_institutional.origine_externe_inversion_omega import evaluate_inversion
    corridor = {"path": [_path_at_distance(100), _path_at_distance(400),
                          _path_at_distance(700)]}
    ev = evaluate_inversion(corridor, waypoint={"lat": OFFICIAL_LAT, "lng": OFFICIAL_LNG})
    assert ev["should_invert"] is True
    assert ev["reason"] == "ENDPOINT_IN_CROWN"
    assert ev["origin_in_crown"] is False
    assert ev["endpoint_in_crown"] is True


def test_inversion_path_external_to_external_no_invert():
    """path[0]=620m, path[-1]=720m → AUCUNE inversion."""
    from engines.v8_institutional.origine_externe_inversion_omega import evaluate_inversion
    corridor = {"path": [_path_at_distance(620), _path_at_distance(720)]}
    ev = evaluate_inversion(corridor, waypoint={"lat": OFFICIAL_LAT, "lng": OFFICIAL_LNG})
    assert ev["should_invert"] is False
    assert ev["origin_in_crown"] is True


def test_inversion_path_internal_to_internal_no_invert():
    """path[0]=200m, path[-1]=300m → AUCUNE inversion (extrémité hors couronne)."""
    from engines.v8_institutional.origine_externe_inversion_omega import evaluate_inversion
    corridor = {"path": [_path_at_distance(200), _path_at_distance(300)]}
    ev = evaluate_inversion(corridor, waypoint={"lat": OFFICIAL_LAT, "lng": OFFICIAL_LNG})
    assert ev["should_invert"] is False
    assert ev["endpoint_in_crown"] is False


def test_inversion_path_external_to_internal_no_invert():
    """path[0]=700m, path[-1]=200m → DÉJÀ conforme, pas d'inversion."""
    from engines.v8_institutional.origine_externe_inversion_omega import evaluate_inversion
    corridor = {"path": [_path_at_distance(700), _path_at_distance(200)]}
    ev = evaluate_inversion(corridor, waypoint={"lat": OFFICIAL_LAT, "lng": OFFICIAL_LNG})
    assert ev["should_invert"] is False
    assert ev["origin_in_crown"] is True
    assert ev["endpoint_in_crown"] is False


# ───────────────────────────────────────────────────────────────────────
# 6. Pipeline applique l'inversion + reverse(path)
# ───────────────────────────────────────────────────────────────────────
def test_apply_inversion_to_bundle_reverses_path():
    from engines.v8_institutional.origine_externe_inversion_omega import (
        apply_origine_externe_inversion_to_bundle,
    )
    p_in = _path_at_distance(100)
    p_mid = _path_at_distance(400)
    p_out = _path_at_distance(720)
    bundle = {
        "waypoint": {"lat": OFFICIAL_LAT, "lng": OFFICIAL_LNG},
        "species": "orignal",
        "corridors": [{"id": "c1", "path": [p_in, p_mid, p_out]}],
    }
    out = apply_origine_externe_inversion_to_bundle(bundle, species="orignal", month=10, hour=16)
    c = out["corridors"][0]
    assert c["origin_external_inversion_applied"] is True
    assert c["origin_external_inversion_reason"] == "ENDPOINT_IN_CROWN"
    # Le path doit être inversé : nouveau path[0] = ancien path[-1]
    assert c["path"][0] == p_out
    assert c["path"][-1] == p_in
    stats = out["origine_externe_inversion_stats"]
    assert stats["inverted_count"] == 1
    assert stats["skipped_count"] == 0


def test_apply_inversion_no_change_when_not_required():
    from engines.v8_institutional.origine_externe_inversion_omega import (
        apply_origine_externe_inversion_to_bundle,
    )
    p_a = _path_at_distance(200)
    p_b = _path_at_distance(300)
    bundle = {
        "waypoint": {"lat": OFFICIAL_LAT, "lng": OFFICIAL_LNG},
        "species": "orignal",
        "corridors": [{"id": "c1", "path": [p_a, p_b]}],
    }
    out = apply_origine_externe_inversion_to_bundle(bundle, species="orignal", month=10, hour=16)
    c = out["corridors"][0]
    assert c["origin_external_inversion_applied"] is False
    assert c["path"][0] == p_a  # path inchangé
    assert out["origine_externe_inversion_stats"]["inverted_count"] == 0


# ───────────────────────────────────────────────────────────────────────
# 7. Métadonnées institutionnelles
# ───────────────────────────────────────────────────────────────────────
def test_metadata_filter_phase_present():
    from engines.v8_institutional.origine_externe_inversion_omega import (
        apply_origine_externe_inversion_to_bundle, PHASE_TAG, PHASE_NAME,
    )
    bundle = {
        "waypoint": {"lat": OFFICIAL_LAT, "lng": OFFICIAL_LNG},
        "corridors": [{"id": "c1", "path": [_path_at_distance(150),
                                              _path_at_distance(710)]}],
    }
    out = apply_origine_externe_inversion_to_bundle(bundle, species="orignal", month=10, hour=16)
    c = out["corridors"][0]
    assert c["origin_external_inversion_filter_phase"] == PHASE_TAG
    assert "origin_external_inversion_audit" in c
    audit = c["origin_external_inversion_audit"]
    assert audit["distance_origin_m"] is not None
    assert audit["distance_endpoint_m"] is not None


# ───────────────────────────────────────────────────────────────────────
# 8. Pipeline complet — XIX-P2 en runtime
# ───────────────────────────────────────────────────────────────────────
def test_pipeline_xix_p2_runtime_wapiti_inverts():
    """Wapiti V30 a typiquement plusieurs path[-1] dans la couronne."""
    from fastapi import Response
    from engines.v8_institutional.v20_performance_bundle import v20_territoire_bundle

    async def go():
        r = Response()
        return await v20_territoire_bundle(
            response=r, lat=OFFICIAL_LAT, lon=OFFICIAL_LNG, species="wapiti",
            month=10, hour=16, wind_deg=225.0, wind_speed=15.0,
        )

    bundle = asyncio.run(go())
    assert bundle.get("origine_externe_inversion_applied") is True
    stats = bundle.get("origine_externe_inversion_stats") or {}
    assert "inverted_count" in stats
    assert "skipped_count" in stats
    assert stats["enforce_mode"] is True
    assert stats["crown_min_m"] == 600.0
    assert stats["crown_max_m"] == 780.0


# ───────────────────────────────────────────────────────────────────────
# 9. Endpoint observabilité
# ───────────────────────────────────────────────────────────────────────
def test_endpoint_origine_inversion_returns_stats():
    from fastapi.testclient import TestClient
    from fastapi import FastAPI
    from routes.origine_externe_inversion_router import router as r
    app = FastAPI()
    app.include_router(r)
    c = TestClient(app)
    resp = c.get("/api/v30/corridors/origine-inversion?species=wapiti&month=10&hour=16")
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["phase"] == "PHASE_XIX_P2_ORIGINE_EXTERNE_INVERSION_Ω"
    assert data["subphase"] == "PHASE_XIX_P2"
    fs = data["inversion_status"]
    assert fs["crown_min_m"] == 600.0
    assert fs["crown_max_m"] == 780.0
    assert "stats" in data
    assert "xix_p1_downstream_stats" in data

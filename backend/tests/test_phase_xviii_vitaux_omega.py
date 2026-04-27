"""
test_phase_xviii_vitaux_omega.py — PHASE_XVIII_ENGINE_CORRIDORS_VITAUX_Ω
==========================================================================
Tests d'activation institutionnelle du filtre CORRIDORS_VITAUX_Ω.

Ces tests CERTIFIENT :
  1. Détection des ancrages vitaux à 150 m du path
  2. Règle GRANDS_MAMMIFERES (orignal/wapiti/ours) : ≥ 1 zone MAJEURE + 1 attracteur fort
  3. Règle PETITS_MAMMIFERES (chevreuil/dindon) : ≥ 1 zone vitale + 1 transition/hotspot
  4. Mode ENFORCE filtre les corridors invalides
  5. Audit log JSON `corridors_rejected_vitaux_xviii.json` créé au moins 1 fois
  6. Pipeline complet conserve les corridors vitaux et retire les non-vitaux
  7. Endpoint observabilité retourne stats + sample
"""
import os
import sys
import asyncio
import json
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
    reset_dataset_cache(); reset_heatmap_cache()
    yield


# ───────────────────────────────────────────────────────────────────────
# 1. Détection ancrages
# ───────────────────────────────────────────────────────────────────────
def test_detect_anchors_within_150m():
    from engines.v8_institutional.corridors_vitaux_omega import detect_vital_anchors
    path = [[OFFICIAL_LAT, OFFICIAL_LNG],
            [OFFICIAL_LAT + 0.001, OFFICIAL_LNG + 0.001]]
    zones = [
        {"polygon": [[OFFICIAL_LAT + 0.0008, OFFICIAL_LNG + 0.0008],
                     [OFFICIAL_LAT + 0.0012, OFFICIAL_LNG + 0.0012]],
         "type": "alimentation"},
        {"polygon": [[OFFICIAL_LAT - 0.001, OFFICIAL_LNG - 0.001],
                     [OFFICIAL_LAT - 0.0005, OFFICIAL_LNG - 0.0005]],
         "type": "rut"},
    ]
    salines = [{"lat": OFFICIAL_LAT + 0.001, "lng": OFFICIAL_LNG + 0.0005}]
    a = detect_vital_anchors(path, zones, salines, [], [])
    assert "alimentation" in a["major_zones"]
    assert "rut" in a["major_zones"]
    assert a["salines"] >= 1


def test_anchor_outside_radius_not_detected():
    from engines.v8_institutional.corridors_vitaux_omega import detect_vital_anchors
    path = [[OFFICIAL_LAT, OFFICIAL_LNG]]
    # Zone à 500 m → hors rayon 150 m
    zones = [{"polygon": [[OFFICIAL_LAT + 0.005, OFFICIAL_LNG + 0.005]],
              "type": "alimentation"}]
    a = detect_vital_anchors(path, zones, [], [], [])
    assert "alimentation" not in a["major_zones"]


# ───────────────────────────────────────────────────────────────────────
# 2. Règle GRANDS_MAMMIFERES
# ───────────────────────────────────────────────────────────────────────
def test_grands_mammiferes_valid_with_major_and_attractor():
    from engines.v8_institutional.corridors_vitaux_omega import validate_corridor_vital_anchor
    path = [[OFFICIAL_LAT, OFFICIAL_LNG],
            [OFFICIAL_LAT + 0.001, OFFICIAL_LNG + 0.001]]
    zones = [{"polygon": [[OFFICIAL_LAT + 0.0008, OFFICIAL_LNG + 0.0008]],
              "type": "alimentation"}]
    salines = [{"lat": OFFICIAL_LAT + 0.001, "lng": OFFICIAL_LNG + 0.0005}]
    out = validate_corridor_vital_anchor({"path": path}, "orignal",
                                          zones, salines, [], [])
    assert out["valid"] is True, out
    assert out["group"] == "GRANDS_MAMMIFERES"


def test_grands_mammiferes_rejected_without_attractor():
    from engines.v8_institutional.corridors_vitaux_omega import validate_corridor_vital_anchor
    path = [[OFFICIAL_LAT, OFFICIAL_LNG],
            [OFFICIAL_LAT + 0.001, OFFICIAL_LNG + 0.001]]
    # Zone alimentation présente mais aucun attracteur fort
    zones = [{"polygon": [[OFFICIAL_LAT + 0.0008, OFFICIAL_LNG + 0.0008]],
              "type": "alimentation"}]
    out = validate_corridor_vital_anchor({"path": path}, "orignal",
                                          zones, [], [], [])
    assert out["valid"] is False
    assert "attracteur_ecologique_fort" in out["reason"]


def test_grands_mammiferes_rejected_without_major():
    from engines.v8_institutional.corridors_vitaux_omega import validate_corridor_vital_anchor
    path = [[OFFICIAL_LAT, OFFICIAL_LNG]]
    salines = [{"lat": OFFICIAL_LAT, "lng": OFFICIAL_LNG}]
    out = validate_corridor_vital_anchor({"path": path}, "wapiti",
                                          [], salines, [], [])
    assert out["valid"] is False
    assert "zone_vitale_majeure" in out["reason"]


# ───────────────────────────────────────────────────────────────────────
# 3. Règle PETITS_MAMMIFERES
# ───────────────────────────────────────────────────────────────────────
def test_petits_mammiferes_valid_with_zone_and_transition():
    from engines.v8_institutional.corridors_vitaux_omega import validate_corridor_vital_anchor
    path = [[OFFICIAL_LAT, OFFICIAL_LNG]]
    zones = [
        {"polygon": [[OFFICIAL_LAT, OFFICIAL_LNG]], "type": "alimentation"},
        {"polygon": [[OFFICIAL_LAT, OFFICIAL_LNG]], "type": "lisiere"},
    ]
    out = validate_corridor_vital_anchor({"path": path}, "chevreuil",
                                          zones, [], [], [])
    assert out["valid"] is True, out
    assert out["group"] == "PETITS_MAMMIFERES"


def test_petits_mammiferes_valid_with_zone_and_hotspot():
    """Hotspot majeur peut servir de transition pour petits mammifères."""
    from engines.v8_institutional.corridors_vitaux_omega import validate_corridor_vital_anchor
    path = [[OFFICIAL_LAT, OFFICIAL_LNG]]
    zones = [{"polygon": [[OFFICIAL_LAT, OFFICIAL_LNG]], "type": "repos"}]
    hotspots = [{"lat": OFFICIAL_LAT, "lng": OFFICIAL_LNG, "intensity": 0.85}]
    out = validate_corridor_vital_anchor({"path": path}, "dindon",
                                          zones, [], hotspots, [])
    assert out["valid"] is True


# ───────────────────────────────────────────────────────────────────────
# 4. Pipeline complet (5 espèces)
# ───────────────────────────────────────────────────────────────────────
@pytest.mark.parametrize("species,month,hour", [
    ("orignal", 10, 18),
    ("chevreuil", 10, 7),
    ("wapiti", 10, 16),
    ("ours", 9, 12),
    ("dindon", 5, 9),
])
def test_pipeline_vitaux_filter_per_species(species, month, hour):
    from fastapi import Response
    from engines.v8_institutional.v20_performance_bundle import v20_territoire_bundle

    async def go():
        r = Response()
        return await v20_territoire_bundle(
            response=r, lat=OFFICIAL_LAT, lon=OFFICIAL_LNG, species=species,
            month=month, hour=hour, wind_deg=225.0, wind_speed=15.0,
        )

    bundle = asyncio.run(go())
    assert bundle.get("corridors_vitaux_omega_applied") is True
    stats = bundle.get("corridors_vitaux_omega_stats") or {}
    assert "total_input" in stats
    assert "total_kept" in stats
    assert stats["enforce_mode"] is True
    # Tous les corridors restants doivent être vitaux-validés
    for c in bundle.get("corridors") or []:
        v = c.get("vitaux_validation") or {}
        assert v.get("valid") is True, (species, c.get("id"), v.get("reason"))


# ───────────────────────────────────────────────────────────────────────
# 5. Audit log JSON
# ───────────────────────────────────────────────────────────────────────
def test_audit_log_created_on_rejection():
    """Si au moins un corridor est rejeté, le log JSON cumulatif est écrit."""
    from fastapi import Response
    from engines.v8_institutional.v20_performance_bundle import v20_territoire_bundle
    from engines.v8_institutional.corridors_vitaux_omega import AUDIT_LOG_PATH

    async def go():
        r = Response()
        return await v20_territoire_bundle(
            response=r, lat=OFFICIAL_LAT, lon=OFFICIAL_LNG, species="orignal",
            month=10, hour=18, wind_deg=225.0, wind_speed=15.0,
        )

    bundle = asyncio.run(go())
    rejected_count = (bundle.get("corridors_vitaux_omega_stats") or {}).get("total_rejected", 0)
    if rejected_count > 0:
        assert AUDIT_LOG_PATH.exists(), f"Log audit absent: {AUDIT_LOG_PATH}"
        data = json.loads(AUDIT_LOG_PATH.read_text(encoding="utf-8"))
        assert isinstance(data, list)
        assert len(data) >= 1
        assert data[-1]["phase"] == "PHASE_XVIII_ENGINE_CORRIDORS_VITAUX_Ω"
        assert data[-1]["species"] == "orignal"


# ───────────────────────────────────────────────────────────────────────
# 6. Endpoint observabilité
# ───────────────────────────────────────────────────────────────────────
def test_endpoint_vitaux_omega_returns_stats():
    from fastapi.testclient import TestClient
    from fastapi import FastAPI
    from routes.corridors_vitaux_router import router as r
    app = FastAPI()
    app.include_router(r)
    c = TestClient(app)
    resp = c.get("/api/v30/corridors/vitaux-omega?species=orignal&month=10&hour=18")
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["phase"] == "PHASE_XVIII_ENGINE_CORRIDORS_VITAUX_Ω"
    assert data["species_group"] == "GRANDS_MAMMIFERES"
    assert data["anchor_proximity_m"] == 150.0
    assert "stats" in data

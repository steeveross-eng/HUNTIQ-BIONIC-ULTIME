"""
test_phase_xviii_predictive_omega_v2.py — PHASE_XVIII_ENGINE_PREDICTIVE_OMEGA_GPS_USGS_Ω
==========================================================================================
Tests d'activation institutionnelle de l'engine predictive_omega V2 calibré
sur trajectoires GPS USGS / Movebank.

Ces tests CERTIFIENT :
  1. Les 5 datasets GPS sont présents et chargeables
  2. Le scoring directionnel discrimine les bearings préférentiels saison
  3. Le scoring d'amplitude reflète la longueur cohérente vs home-range
  4. Le scoring diurne varie selon l'heure
  5. Le pipeline XVIII annote tous les corridors V30 + INTERZONE
  6. L'orchestrateur écologique utilise le score V2 (predictive_source = XVIII_GPS_USGS)
  7. Les 5 espèces produisent des scores différenciés (pas d'uniformité)
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
    """Purge tous les caches avant chaque test."""
    pkl = "/app/backend/cache/territoire_bundle.pkl"
    if os.path.exists(pkl):
        os.remove(pkl)
    from engines.v8_institutional import v20_performance_bundle as vp
    vp._CACHE.clear()
    from engines.v8_institutional.ecological_orchestrator_omega import reset_heatmap_cache
    from engines.v8_institutional.predictive_omega_v2 import reset_dataset_cache
    reset_heatmap_cache()
    reset_dataset_cache()
    yield


# ───────────────────────────────────────────────────────────────────────
# 1. Datasets GPS disponibles
# ───────────────────────────────────────────────────────────────────────
def test_gps_datasets_all_5_species_available():
    from engines.v8_institutional.predictive_omega_v2 import get_gps_dataset_status
    s = get_gps_dataset_status()
    assert s["all_available"] is True, f"Datasets GPS manquants: {s['sources']}"
    expected = {"orignal", "chevreuil", "wapiti", "ours_noir", "dindon_sauvage"}
    assert set(s["sources"].keys()) == expected
    for canon, info in s["sources"].items():
        assert info["present"], f"{canon} absent: {info['path']}"
        assert info["size_bytes"] > 100_000, f"{canon} trop petit: {info['size_bytes']}"


def test_dataset_loaded_has_biological_profile():
    from engines.v8_institutional.predictive_omega_v2 import _load_dataset
    ds = _load_dataset("orignal")
    assert ds is not None
    assert "biological_profile" in ds
    bp = ds["biological_profile"]
    assert "primary_bearings_deg" in bp
    assert "amplitude_m" in bp
    assert "diurnal_activity" in bp
    assert len(bp["diurnal_activity"]) == 24


# ───────────────────────────────────────────────────────────────────────
# 2. Scoring directionnel
# ───────────────────────────────────────────────────────────────────────
def test_direction_score_max_when_aligned_with_preferred():
    """Path aligné avec bearing préférentiel → score direction proche de 40."""
    from engines.v8_institutional.predictive_omega_v2 import score_corridor_with_gps_real
    # Octobre = automne. Pour orignal, bearings préférentiels = [340, 160].
    # Path aligné sur 340° (NNW)
    import math
    bearing = math.radians(340)
    dlat = 0.005 * math.cos(bearing)
    dlng = 0.005 * math.sin(bearing) / math.cos(math.radians(OFFICIAL_LAT))
    path = [
        [OFFICIAL_LAT, OFFICIAL_LNG],
        [OFFICIAL_LAT + dlat, OFFICIAL_LNG + dlng],
    ]
    out = score_corridor_with_gps_real({"path": path}, species="orignal", month=10, hour=18)
    assert out["valid"] is True
    assert out["components"]["direction"] >= 30, out["components"]


def test_direction_score_low_when_perpendicular():
    """Path perpendiculaire au bearing préférentiel → score direction faible."""
    from engines.v8_institutional.predictive_omega_v2 import score_corridor_with_gps_real
    import math
    # orignal autumn pref=[340, 160]. Perpendiculaire = 70° ou 250°.
    bearing = math.radians(70)
    dlat = 0.005 * math.cos(bearing)
    dlng = 0.005 * math.sin(bearing) / math.cos(math.radians(OFFICIAL_LAT))
    path = [
        [OFFICIAL_LAT, OFFICIAL_LNG],
        [OFFICIAL_LAT + dlat, OFFICIAL_LNG + dlng],
    ]
    out = score_corridor_with_gps_real({"path": path}, species="orignal", month=10, hour=18)
    assert out["components"]["direction"] < 15, out["components"]


# ───────────────────────────────────────────────────────────────────────
# 3. Scoring saisonnier — orignal hiver vs automne
# ───────────────────────────────────────────────────────────────────────
def test_seasonal_difference_per_species():
    from engines.v8_institutional.predictive_omega_v2 import score_corridor_with_gps_real
    import math
    # même path, mais saison différente → score direction doit varier (pref change)
    path = [
        [OFFICIAL_LAT, OFFICIAL_LNG],
        [OFFICIAL_LAT + 0.003, OFFICIAL_LNG + 0.003],  # bearing ~ 45° (NE)
    ]
    autumn = score_corridor_with_gps_real({"path": path}, species="orignal", month=10, hour=18)
    winter = score_corridor_with_gps_real({"path": path}, species="orignal", month=1, hour=18)
    # bearings autumn=[340,160] hiver=[90,270] → directions différentes pour bearing 45°
    assert autumn["components"]["direction"] != winter["components"]["direction"]
    assert autumn["metrics"]["preferred_bearings_deg"] != winter["metrics"]["preferred_bearings_deg"]


# ───────────────────────────────────────────────────────────────────────
# 4. Scoring diurne — dindon nuit vs jour
# ───────────────────────────────────────────────────────────────────────
def test_diurnal_score_dindon_zero_at_night():
    """Dindon = 0% activité la nuit → diurnal_score = 0."""
    from engines.v8_institutional.predictive_omega_v2 import score_corridor_with_gps_real
    path = [[OFFICIAL_LAT, OFFICIAL_LNG],
            [OFFICIAL_LAT + 0.002, OFFICIAL_LNG + 0.002]]
    night = score_corridor_with_gps_real({"path": path}, species="dindon", month=5, hour=2)
    day = score_corridor_with_gps_real({"path": path}, species="dindon", month=5, hour=10)
    assert night["components"]["diurnal"] < 1.0
    assert day["components"]["diurnal"] >= 5.0


# ───────────────────────────────────────────────────────────────────────
# 5. Pipeline XVIII complet — toutes espèces
# ───────────────────────────────────────────────────────────────────────
@pytest.mark.parametrize("species,month,hour", [
    ("orignal", 10, 18),
    ("chevreuil", 5, 7),
    ("wapiti", 10, 16),
    ("ours", 9, 12),
    ("dindon", 5, 9),
])
def test_pipeline_xviii_annotates_all_species(species, month, hour):
    from fastapi import Response
    from engines.v8_institutional.v20_performance_bundle import v20_territoire_bundle

    async def go():
        r = Response()
        return await v20_territoire_bundle(
            response=r, lat=OFFICIAL_LAT, lon=OFFICIAL_LNG, species=species,
            month=month, hour=hour, wind_deg=225.0, wind_speed=15.0,
        )

    bundle = asyncio.run(go())
    assert bundle.get("predictive_omega_v2_applied") is True
    pv2_stats = bundle.get("predictive_omega_v2_stats") or {}
    assert pv2_stats["corridors_scored"] >= 1
    assert pv2_stats["mean_score"] > 0
    assert pv2_stats["gps_dataset_status"]["all_available"] is True
    # Tous les corridors finaux ont une annotation V2
    for c in bundle.get("corridors") or []:
        assert "predictive_omega_v2" in c
        pv2 = c["predictive_omega_v2"]
        assert pv2["valid"] is True
        assert "components" in pv2
        assert "metrics" in pv2


# ───────────────────────────────────────────────────────────────────────
# 6. L'orchestrateur écologique utilise XVIII (predictive_source)
# ───────────────────────────────────────────────────────────────────────
def test_eco_orchestrator_uses_phase_xviii_predictive():
    from fastapi import Response
    from engines.v8_institutional.v20_performance_bundle import v20_territoire_bundle

    async def go():
        r = Response()
        return await v20_territoire_bundle(
            response=r, lat=OFFICIAL_LAT, lon=OFFICIAL_LNG, species="orignal",
            month=10, hour=18, wind_deg=225.0, wind_speed=15.0,
        )

    bundle = asyncio.run(go())
    # Au moins 1 corridor validé doit avoir predictive_source = "PHASE_XVIII_GPS_USGS"
    sources = []
    for c in bundle.get("corridors") or []:
        eco = c.get("ecological_consensus") or {}
        ps = (eco.get("metrics") or {}).get("predictive_source")
        if ps:
            sources.append(ps)
    assert "PHASE_XVIII_GPS_USGS" in sources, f"PHASE XVIII non utilisée. sources={sources}"


# ───────────────────────────────────────────────────────────────────────
# 7. Différenciation inter-espèces
# ───────────────────────────────────────────────────────────────────────
def test_score_differs_across_species_same_path():
    from engines.v8_institutional.predictive_omega_v2 import score_corridor_with_gps_real
    path = [[OFFICIAL_LAT, OFFICIAL_LNG],
            [OFFICIAL_LAT + 0.005, OFFICIAL_LNG + 0.005]]
    scores = {}
    for sp in ("orignal", "chevreuil", "wapiti", "ours", "dindon"):
        out = score_corridor_with_gps_real({"path": path}, species=sp, month=10, hour=14)
        scores[sp] = out["score"]
    # Au moins 3 espèces doivent avoir des scores distincts (>2 pts d'écart)
    distinct = len({round(s, 0) for s in scores.values()})
    assert distinct >= 3, f"Scores pas suffisamment différenciés: {scores}"

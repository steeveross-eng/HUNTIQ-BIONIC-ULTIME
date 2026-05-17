"""
test_phase_supra_bio_nutrition.py — PHASE_SUPRA_BIO_NUTRITION_Ω
═══════════════════════════════════════════════════════════════════════════
Phase     : PHASE_SUPRA_BIO_NUTRITION_Ω + PHASE_TERRITOIRE_Ω_ULTIME
Commandant: STEEVE-MAX
Tag       : BCE-4X ULTIME ABSOLU — TOP-ABSOLU

Tests d'intégration des 12 nouveaux engines SUPRA-BIO-NUTRITION_Ω :
  NUTRITION (5) : sol_nutriments, forage_qualite, carence, recettes_salines, champs_nourriciers
  THERMIQUE (2) : canopee_thermique, microclimat_advanced
  COMPORTEMENT (2) : trophic_behavior, social_structure
  PHYSIOLOGIE (1) : sante_physio
  SYNTHÈSE (2) : nutritional_attractiveness, optimisation_habitat

Doctrine : V30 LOCKED · aucune modification des engines existants · tous en AVAL.
"""


# ════════════════════════════════════════════════════════════════════════════
# NUTRITION (5 engines)
# ════════════════════════════════════════════════════════════════════════════
def test_sol_nutriments_returns_institutional_schema():
    from engines.v8_institutional.engine_sol_nutriments_omega import compute_sol_nutriments
    r = compute_sol_nutriments({"texture": "humifere", "drainage": 0.7})
    assert r["engine"] == "ENGINE_SOL_NUTRIMENTS_Ω"
    assert r["level"] == "BIOLOGIE"
    assert 0.0 <= r["fertility_index"] <= 1.0
    assert "nutrients_ratio" in r


def test_forage_quality_season_detection():
    from engines.v8_institutional.engine_forage_qualite_omega import compute_forage_quality
    r = compute_forage_quality([{"type": "foret_feuillus"}], month=10)
    assert r["season"] == "fall"
    assert r["forage_quality_index"] >= 0.80


def test_carence_nutritionnelle_per_species():
    from engines.v8_institutional.engine_carence_nutritionnelle_omega import compute_carence
    sol = {"nutrients_ratio": {"Na": 0.3, "Ca": 0.5, "P": 0.8, "Mg": 0.5, "K": 0.6}}
    fg = {"forage_quality_index": 0.6}
    r = compute_carence("orignal", sol, fg)
    assert r["species"] == "orignal"
    assert r["carence_risk"] in ("FAIBLE", "MODÉRÉ", "ÉLEVÉ")


def test_recettes_salines_orignal_boost():
    from engines.v8_institutional.engine_recettes_salines_omega import compute_recettes
    r = compute_recettes("orignal", {"deficits_vs_needs": {"Na": 0.3}, "carence_risk": "MODÉRÉ"})
    assert len(r["recipes"]) >= 1
    assert all("priority_boost" in rec for rec in r["recipes"])


def test_champs_nourriciers_agricole():
    from engines.v8_institutional.engine_champs_nourriciers_omega import compute_champs_nourriciers
    zones = [{"type": "agricole", "crop": "mais", "lat": 48.2, "lng": -68.3}]
    r = compute_champs_nourriciers(zones, species="chevreuil", month=10)
    assert r["fields_count"] == 1
    assert r["mean_attractiveness"] > 0.8


# ════════════════════════════════════════════════════════════════════════════
# THERMIQUE (2 engines)
# ════════════════════════════════════════════════════════════════════════════
def test_canopee_thermique_day_vs_night():
    from engines.v8_institutional.engine_canopee_thermique_omega import compute_canopee_thermique
    day = compute_canopee_thermique({"terrain": {"canopy": 0.8}}, hour=12)
    night = compute_canopee_thermique({"terrain": {"canopy": 0.8}}, hour=23)
    assert day["thermal_buffer_c"] > 0
    assert night["thermal_buffer_c"] < 0


def test_microclimat_advanced_agrege_4_sources():
    from engines.v8_institutional.engine_microclimat_advanced_omega import compute_microclimat_advanced
    r = compute_microclimat_advanced(
        {"terrain": {"slope_deg": 5, "elevation": 250}},
        {"thermal_buffer_c": 2.0},
        {"pression": 1012},
        {"humidity_ratio": 0.6},
        hour=10, month=10,
    )
    assert "local_temperature_c" in r
    assert "local_stability_index" in r


# ════════════════════════════════════════════════════════════════════════════
# COMPORTEMENT (2 engines)
# ════════════════════════════════════════════════════════════════════════════
def test_trophic_behavior_dawn_peak():
    from engines.v8_institutional.engine_trophic_behavior_omega import compute_trophic
    r = compute_trophic("chevreuil", hour=6)
    assert r["activity_window"] == "dawn"
    assert r["activity_score"] >= 0.9


def test_social_structure_rut_detection():
    from engines.v8_institutional.engine_social_structure_omega import compute_social
    r = compute_social("wapiti", month=10)
    assert r["in_rut_period"] is True
    r2 = compute_social("wapiti", month=3)
    assert r2["in_rut_period"] is False


# ════════════════════════════════════════════════════════════════════════════
# PHYSIOLOGIE (1 engine)
# ════════════════════════════════════════════════════════════════════════════
def test_sante_physio_composite_0_1():
    from engines.v8_institutional.engine_sante_physio_omega import compute_sante_physio
    r = compute_sante_physio(
        "orignal",
        {"forage_quality_index": 0.85},
        {"total_deficit_score": 0.2},
        stress_anthropique=0.2,
        microclimat={"local_stability_index": 0.7},
    )
    assert 0.0 <= r["health_index_0_1"] <= 1.0
    assert r["health_band"] in ("EXCELLENT", "BON", "MOYEN", "CRITIQUE")


# ════════════════════════════════════════════════════════════════════════════
# SYNTHÈSE (2 engines)
# ════════════════════════════════════════════════════════════════════════════
def test_nutritional_attractiveness_composite():
    from engines.v8_institutional.engine_nutritional_attractiveness_omega import compute_nutritional_attractiveness
    r = compute_nutritional_attractiveness(
        "orignal",
        {"forage_quality_index": 0.8},
        {"mean_attractiveness": 0.5},
        {"fertility_index": 0.7},
        {"recipes": [{"priority_boost": 0.3}]},
        {"health_index_0_1": 0.75},
    )
    assert r["attractiveness_band"] in ("ULTIME", "ÉLEVÉE", "MODÉRÉE", "FAIBLE")
    assert 0.0 <= r["attractiveness_score_0_1"] <= 1.0


def test_optimisation_habitat_ultime_band():
    from engines.v8_institutional.engine_optimisation_habitat_omega import compute_optimisation_habitat
    r = compute_optimisation_habitat(
        "orignal",
        {"attractiveness_score_0_1": 0.90},
        {"foraging_pressure_index": 0.8},
        {"group_avg_size": 1.2, "in_rut_period": True},
        {"health_index_0_1": 0.85},
        {"local_stability_index": 0.75},
        {"mean_transition": 0.8},
    )
    assert r["habitat_band"] in ("ULTIME", "HAUT", "STANDARD", "LIMITÉ")
    assert "recommendation" in r


# ════════════════════════════════════════════════════════════════════════════
# V30 INVIOLATION — vérifier que les nouveaux engines n'impactent pas V30
# ════════════════════════════════════════════════════════════════════════════
def test_v30_lock_sha256_after_supra_bio_nutrition():
    import hashlib
    REGISTRY_LOCK_SHA = "fb765b94cc1fd4216c4afa4c0fb72bc1fd8e18fc26b6955db8157b42a26ecb0c"
    ENGINE_IA_SHA = "bcb1e3a6a92304a171978ee7b6be2151e7035c84d8ffc1690839d993be9e39d3"
    for path, expected in [
        ("/app/backend/engines/v8_institutional/registry_lock_omega.py", REGISTRY_LOCK_SHA),
        ("/app/backend/engines/v8_institutional/engine_ia_corridors_omega.py", ENGINE_IA_SHA),
    ]:
        with open(path, "rb") as f:
            actual = hashlib.sha256(f.read()).hexdigest()
        assert actual == expected, f"V30 mutation détectée sur {path}"

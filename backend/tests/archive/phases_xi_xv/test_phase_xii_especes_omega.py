"""tests/test_phase_xii_especes_omega.py — Tests régression PHASE_XII_ESPECES_Ω.
Commandant STEEVE-MAX · BCE-4X ULTIME ABSOLU.
"""
import sys
sys.path.insert(0, "/app/backend")

from engines.v8_institutional.especes.engine_especes_omega import (
    ENGINES_ESPECES_Ω, list_especes, execute_pipeline_stage, get_lock_signature,
)


def test_5_engines_loaded():
    assert len(ENGINES_ESPECES_Ω) == 5, "Doit charger exactement 5 engines"
    assert set(ENGINES_ESPECES_Ω.keys()) == {
        "CHEVREUIL", "ORIGNAL", "OURS_NOIR", "WAPITI", "DINDON_SAUVAGE",
    }, "espece_ids attendus"


def test_bce4x_compliance_all_species():
    """Chaque espèce doit avoir GOV+UNI+PR + au moins 1 DOI."""
    especes = list_especes()
    for e in especes:
        assert e["bce4x_compliant"], f"{e['espece_id']} non conforme: {e['bce4x_errors']}"
        assert "GOV" in e["sources_types"], f"{e['espece_id']} manque source GOV"
        assert "UNI" in e["sources_types"], f"{e['espece_id']} manque source UNI"
        assert "PR" in e["sources_types"], f"{e['espece_id']} manque source PR"
        assert e["sources_count"] >= 6, f"{e['espece_id']} <6 sources"


def test_no_vulgarisation_no_opinion():
    """Aucun label legacy interdit ne doit apparaître dans les profils."""
    forbidden = ["BON", "EXCELLENT", "MOYEN", "MEDIOCRE"]
    for esp_id, (profile, _) in ENGINES_ESPECES_Ω.items():
        text = " ".join(profile.dimensions_scientifiques + profile.sorties_territoire)
        for f in forbidden:
            assert f not in text.upper().split(), f"Label interdit '{f}' dans {esp_id}"


def test_pipeline_stage_executes():
    env = {"temperature_c": 25.0, "snow_depth_cm": 30.0,
           "routes_density": 1.0, "urbanisation_pct": 10.0,
           "agriculture_pct": 20.0, "forest_patches_count": 10,
           "largest_patch_index": 60.0, "edge_density": 80.0}
    out = execute_pipeline_stage(env)
    assert out["stage"] == "ENGINE_ESPECES_Ω"
    assert out["species_processed"] == 5
    assert out["phase"] == "PHASE_XII_ESPECES_Ω"
    assert out["doctrine"] == "BCE-4X_ULTIME_ABSOLU"
    for esp_id in ENGINES_ESPECES_Ω.keys():
        r = out["results_per_species"][esp_id]
        assert "error" not in r, f"{esp_id} a échoué: {r.get('error')}"
        assert r["engine_marker"].startswith("ENGINE_ESPECE_")
        assert r["doctrine"] == "BCE-4X_ULTIME_ABSOLU"


def test_thermal_threshold_orignal_strictest():
    """L'orignal doit avoir le seuil thermique le plus strict (le plus bas)."""
    seuils = {}
    for esp_id, (profile, _) in ENGINES_ESPECES_Ω.items():
        for s in profile.seuils:
            if s.metric == "thermique_stress":
                seuils[esp_id] = s.valeur
    assert "ORIGNAL" in seuils
    if "CHEVREUIL" in seuils and "WAPITI" in seuils:
        assert seuils["ORIGNAL"] < seuils["CHEVREUIL"], "ORIGNAL doit être plus strict que CHEVREUIL (15.5 < 27)"
        assert seuils["ORIGNAL"] < seuils["WAPITI"], "ORIGNAL doit être plus strict que WAPITI (15.5 < 22.5)"


def test_lock_signature_stable():
    sig1 = get_lock_signature()
    sig2 = get_lock_signature()
    assert sig1["SHA_REGISTRY_LOCK_ESPECES_Ω"] == sig2["SHA_REGISTRY_LOCK_ESPECES_Ω"], "Signature non déterministe"
    assert sig1["VERSION_ESPECES_Ω"] == "LOCKED"
    assert sig1["CONFORMITE_BCE4X_ESPECES_Ω"] == 100
    assert len(sig1["SHA_REGISTRY_LOCK_ESPECES_Ω"]) == 64


def test_palette_styles_distinct():
    """Chaque espèce doit avoir une couleur primaire distincte."""
    colors = []
    for esp_id, (profile, _) in ENGINES_ESPECES_Ω.items():
        colors.append(profile.style_palette["color_primary"])
    assert len(set(colors)) == 5, f"Couleurs primaires non distinctes: {colors}"


if __name__ == "__main__":
    test_5_engines_loaded()
    test_bce4x_compliance_all_species()
    test_no_vulgarisation_no_opinion()
    test_pipeline_stage_executes()
    test_thermal_threshold_orignal_strictest()
    test_lock_signature_stable()
    test_palette_styles_distinct()
    print("OK: 7/7 tests PHASE_XII_ESPECES_Ω passing")

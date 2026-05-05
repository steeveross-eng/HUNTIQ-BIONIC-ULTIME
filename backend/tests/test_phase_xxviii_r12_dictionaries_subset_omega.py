"""
Phase XXVIII · ORDRE N°52-R12 — Tests dictionnaires PROPOSÉS + subset
══════════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU · ANTI_GÉNÉRIQUE_STRICT

Valide :
  · 4 dictionnaires PROPOSÉS chargeables (status=PROPOSÉ)
  · Cohérence interne (pas de valeurs aberrantes)
  · Loader API
  · Subset proposal builder (bbox + commande ogr2ogr)
  · Subset execute → NotImplementedError (anti-pod-restart)
  · Plan minimal R12 enrichi avec dicts par couche
"""
from __future__ import annotations

import importlib

import pytest


@pytest.fixture()
def loader():
    return importlib.import_module(
        "engines.v8_institutional.especes.mffp_dictionaries_loader_omega")


@pytest.fixture()
def specs():
    return importlib.import_module(
        "engines.v8_institutional.especes.mffp_phase3_specs_omega")


@pytest.fixture()
def subset_extractor():
    return importlib.import_module(
        "engines.v8_institutional.especes.mffp_subset_extractor_omega")


def test_r12_four_dictionaries_loadable(loader):
    """Les 4 dictionnaires P0 sont chargeables."""
    expected = {
        "structure_classification_rules", "cl_dens_to_pct",
        "classes_age", "ty_couv_to_forest_binary",
    }
    assert set(loader.DICTIONARY_FILES.keys()) == expected
    for name in expected:
        d = loader.load_dictionary(name)
        assert d is not None
        assert d.get("status") == "PROPOSÉ"
        assert d.get("ordre") == "N°52-R12"


def test_r12_cl_dens_pct_canonical_values(loader):
    """Les midpoints CL_DENS sont conformes aux intervalles MFFP officiels."""
    d = loader.load_dictionary("cl_dens_to_pct")
    m = d["mapping"]
    # A : ]80,100] → midpoint 90
    assert m["A"]["pct_canopy_midpoint"] == 90
    # B : ]60,80] → midpoint 70
    assert m["B"]["pct_canopy_midpoint"] == 70
    # C : ]40,60] → midpoint 50
    assert m["C"]["pct_canopy_midpoint"] == 50
    # D : ]25,40] → midpoint 32 (pas exactement 32.5)
    assert m["D"]["pct_canopy_midpoint"] == 32
    # E : [10,25] → midpoint 17 (pas 17.5)
    assert m["E"]["pct_canopy_midpoint"] == 17
    # Cohérence : tous les midpoints sont dans leur intervalle
    for code, vals in m.items():
        lo, hi = vals["interval_official_pct"]
        assert lo <= vals["pct_canopy_midpoint"] <= hi, (
            f"midpoint {code} hors intervalle")


def test_r12_classes_age_eight_raster_class_ids(loader):
    """8 classes raster (6 régulières + 2 inéquiennes JIN/JIR=7, VIN/VIR=8)."""
    d = loader.load_dictionary("classes_age")
    raster_ids = set()
    for cl in d["regular_age_classes"].values():
        raster_ids.add(cl["raster_class_id"])
    for cl in d["inequienne_age_classes"].values():
        raster_ids.add(cl["raster_class_id"])
    assert raster_ids == {1, 2, 3, 4, 5, 6, 7, 8}
    # JIN et JIR fusionnés en 7
    assert d["inequienne_age_classes"]["JIN"]["raster_class_id"] == 7
    assert d["inequienne_age_classes"]["JIR"]["raster_class_id"] == 7
    # VIN et VIR fusionnés en 8
    assert d["inequienne_age_classes"]["VIN"]["raster_class_id"] == 8
    assert d["inequienne_age_classes"]["VIR"]["raster_class_id"] == 8


def test_r12_ty_couv_forest_binary_complete(loader):
    """Codes forêt majeurs présents (FE, FR, RE, RN, MS) + non-forêt (EAU, AGR)."""
    d = loader.load_dictionary("ty_couv_to_forest_binary")
    forest = d["forest_codes"]
    assert "FE" in forest and forest["FE"]["binary"] == 1
    assert "RE" in forest and forest["RE"]["binary"] == 1
    assert "MS" in forest and forest["MS"]["binary"] == 1
    non_forest = d["non_forest_codes"]
    assert "EAU" in non_forest and non_forest["EAU"]["binary"] == 0
    assert "AGR" in non_forest and non_forest["AGR"]["binary"] == 0
    # Codes ambigus signalés explicitement
    assert "BR" in d["ambiguous_codes_default_decision"]
    assert "AL" in d["non_forest_codes"]
    # Fallback unknown = 0 (anti-sur-estimation)
    assert d["fallback_unknown_code"]["binary"] == 0


def test_r12_structure_rules_decision_tree_complete(loader):
    """Arbre décision structure : 3 steps + fallback."""
    d = loader.load_dictionary("structure_classification_rules")
    dt = d["decision_tree"]
    assert "step_1_check_inequienne" in dt
    assert "step_2_check_recrue" in dt
    assert "step_3_check_haut_dens" in dt
    # 7 raster_class_ids définis
    overview = d["raster_class_ids_overview"]
    assert set(overview.keys()) == {"1", "2", "3", "4", "5", "6", "7"}


def test_r12_loader_api_complete(loader):
    """API loader expose les fonctions clés."""
    assert callable(loader.load_dictionary)
    assert callable(loader.load_all_dictionaries)
    assert callable(loader.get_dictionary_status)
    assert callable(loader.all_proposed_dictionaries_status)
    assert callable(loader.all_validated_for_p0)
    assert callable(loader.list_validation_blockers)


def test_r12_all_dicts_status_proposed_initially(loader):
    """Initialement, tous les statuts sont PROPOSÉ."""
    statuses = loader.all_proposed_dictionaries_status()
    for name, status in statuses.items():
        assert status == "PROPOSÉ", f"{name} status={status}"
    # all_validated_for_p0 doit être False car tous PROPOSÉ
    assert loader.all_validated_for_p0() is False


def test_r12_validation_blockers_listed(loader):
    """Tous les dicts non-validés sont listés comme bloquants."""
    blockers = loader.list_validation_blockers()
    assert len(blockers) == 4  # tous initialement PROPOSÉ
    for b in blockers:
        assert b["status"] == "PROPOSÉ"
        assert "validation_required_by_commandant" in b


def test_r12_subset_proposal_returns_complete_payload(subset_extractor):
    """build_subset_proposal retourne un payload complet sans exécution."""
    p = subset_extractor.build_subset_proposal(target_size_mb=100)
    assert p["status"] == "PROPOSAL_ONLY_NOT_EXECUTED"
    assert p["target_size_mb"] == 100
    assert "bbox_proposed" in p
    bbox = p["bbox_proposed"]
    assert bbox["xmin"] == 560000
    assert bbox["xmax"] == 670000
    assert bbox["label"] == "Estrie_Cantons_Est_Quebec_meridional"
    assert "ogr2ogr_command_template" in p
    assert "EPSG:32198" in p["ogr2ogr_command_template"]
    assert "pyogrio_python_snippet" in p
    assert "import pyogrio" in p["pyogrio_python_snippet"]


def test_r12_subset_execute_raises_not_implemented(subset_extractor):
    """Mode exécution lève NotImplementedError (anti-pod-restart)."""
    with pytest.raises(NotImplementedError) as excinfo:
        subset_extractor.execute_subset_extraction()
    assert "ANTI_GÉNÉRIQUE_STRICT" in str(excinfo.value)


def test_r12_minimal_plan_enriched_with_dicts(specs):
    """PHASE3_MINIMAL_PLAN inclut désormais les dicts par couche P0."""
    plan = specs.PHASE3_MINIMAL_PLAN
    assert plan["ordre"] == "N°52-R11_R12_UPDATED"
    for step in plan["implementation_order_recommended"]:
        # Chaque étape P0 doit lister les dicts utilisés
        assert "dictionaries_proposed_used" in step
        assert "fields_used_pee_maj_gpkg" in step
        assert "subset_validation_tests" in step
        assert len(step["dictionaries_proposed_used"]) >= 1
        assert len(step["subset_validation_tests"]) >= 3


def test_r12_subset_default_bbox_in_quebec(subset_extractor):
    """La bbox par défaut est dans des coordonnées Québec EPSG:32198 plausibles."""
    bbox = subset_extractor.DEFAULT_SUBSET_BBOX_EPSG_32198
    # EPSG:32198 (NAD83 Québec Lambert) : Estrie/Cantons-Est typiquement
    # x ~ 500-700 km, y ~ 100-300 km depuis l'origine
    assert 500000 < bbox["xmin"] < 700000
    assert 500000 < bbox["xmax"] < 700000
    assert 100000 < bbox["ymin"] < 300000
    assert 100000 < bbox["ymax"] < 300000
    assert bbox["xmax"] > bbox["xmin"]
    assert bbox["ymax"] > bbox["ymin"]
    assert bbox["approximate_area_km2"] > 1000

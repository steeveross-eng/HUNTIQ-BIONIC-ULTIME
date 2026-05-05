"""
Phase XXVIII · ORDRE N°52-R11 — Tests specs PHASE_3 R8
══════════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU · ANTI_GÉNÉRIQUE_STRICT

Valide :
  · 8 couches MFFP dérivées spécifiées
  · 8 squelettes de fonctions (NotImplementedError forcé)
  · Plan minimal 4 couches P0 critiques (44h dev)
  · Constantes EPSG:32198 + résolutions cohérentes
"""
from __future__ import annotations

import importlib

import pytest


@pytest.fixture()
def mod():
    return importlib.import_module(
        "engines.v8_institutional.especes.mffp_phase3_specs_omega")


def test_r11_eight_layers_specified(mod):
    """Les 8 couches MFFP attendues sont définies."""
    expected = {
        "MFFP_STRUCTURE", "MFFP_DENSITY", "MFFP_AGE",
        "MFFP_FRAGMENTATION", "MFFP_PRODUCTIVITY", "MFFP_HABITAT",
        "MFFP_CONNECTIVITY", "MFFP_CONTINUITY",
    }
    assert set(mod.MFFP_LAYERS_SPECS.keys()) == expected


def test_r11_each_layer_has_complete_spec(mod):
    """Chaque spec contient les champs canoniques."""
    required_keys = {
        "label", "priority", "description",
        "inputs_required", "outputs", "key_parameters",
        "algorithmic_suggestions", "scientific_references",
        "performance_notes", "complexity",
    }
    for layer_id, spec in mod.MFFP_LAYERS_SPECS.items():
        missing = required_keys - set(spec.keys())
        assert not missing, f"{layer_id} manque {missing}"
        # Valider les sous-clés outputs
        out = spec["outputs"]
        assert "format" in out
        assert "epsg" in out
        assert out["epsg"] == 32198
        assert "filename" in out


def test_r11_target_epsg_is_quebec(mod):
    """EPSG cible = 32198 (NAD83 Québec) confirmé par Commandant."""
    assert mod.TARGET_EPSG == 32198


def test_r11_eight_skeleton_functions_exist(mod):
    """Les 8 fonctions skeletons sont exportées."""
    funcs = {
        "compute_mffp_structure", "compute_mffp_density",
        "compute_mffp_age", "compute_mffp_fragmentation",
        "compute_mffp_productivity", "compute_mffp_habitat",
        "compute_mffp_connectivity", "compute_mffp_continuity",
    }
    assert funcs.issubset(set(mod.__all__))
    for fname in funcs:
        assert callable(getattr(mod, fname))


def test_r11_skeletons_raise_not_implemented_anti_generic(mod):
    """Toutes les fonctions skeletons lèvent NotImplementedError
    (preuve ANTI_GÉNÉRIQUE_STRICT — aucune simulation tolérée)."""
    funcs_to_test = [
        ("compute_mffp_structure", ("/tmp/x.gpkg", {})),
        ("compute_mffp_density", ("/tmp/x.gpkg", {"A": 90})),
        ("compute_mffp_age", ("/tmp/x.gpkg", {"10": (0, 20)},
                              ["JIN", "JIR"])),
        ("compute_mffp_fragmentation", ("/tmp/binary.tif",)),
        ("compute_mffp_productivity", ("/tmp/x.gpkg", {})),
        ("compute_mffp_habitat", ("/tmp/x.gpkg", {}, ["chevreuil"])),
        ("compute_mffp_connectivity",
         ("/tmp/x.gpkg", "/tmp/struct.tif", "/tmp/hab.tif", {})),
        ("compute_mffp_continuity", ("/tmp/x.gpkg", {})),
    ]
    for fname, args in funcs_to_test:
        fn = getattr(mod, fname)
        with pytest.raises(NotImplementedError) as excinfo:
            fn(*args)
        assert "ANTI_GÉNÉRIQUE_STRICT" in str(excinfo.value)


def test_r11_minimal_plan_four_critical_layers(mod):
    """Le plan minimal liste exactement 4 couches P0 critiques."""
    plan = mod.PHASE3_MINIMAL_PLAN
    assert len(plan["priority_layers_4_critical"]) == 4
    expected_p0 = {
        "MFFP_STRUCTURE", "MFFP_DENSITY", "MFFP_AGE",
        "MFFP_FRAGMENTATION",
    }
    assert set(plan["priority_layers_4_critical"]) == expected_p0


def test_r11_minimal_plan_implementation_order(mod):
    """Ordre d'implémentation : LOW → HIGH (gradual)."""
    order = mod.PHASE3_MINIMAL_PLAN["implementation_order_recommended"]
    complexities = [step["complexity"] for step in order]
    # Ordre attendu : LOW, LOW, MEDIUM, HIGH
    assert complexities == ["LOW", "LOW", "MEDIUM", "HIGH"]


def test_r11_total_effort_44h_p0(mod):
    """Total effort 4 couches P0 = 44h (4+4+12+24)."""
    total = mod.PHASE3_MINIMAL_PLAN[
        "estimated_total_effort_hours_4_critical_layers"]
    assert total == 44


def test_r11_p0_layers_priority_marker(mod):
    """Toutes les couches P0 ont la marque P0_CRITICAL_FOR_R9."""
    p0_layers = ["MFFP_STRUCTURE", "MFFP_DENSITY", "MFFP_AGE",
                 "MFFP_FRAGMENTATION"]
    for layer in p0_layers:
        spec = mod.MFFP_LAYERS_SPECS[layer]
        assert "P0_CRITICAL_FOR_R9" in spec["priority"]


def test_r11_dependencies_listed(mod):
    """Dépendances Python + dictionnaires Commandant listés."""
    deps = mod.PHASE3_MINIMAL_PLAN["technical_dependencies"]
    assert "python_modules" in deps
    assert "system_libraries" in deps
    assert "dictionaries_required_from_commandant" in deps
    py_mods = deps["python_modules"]
    assert any("geopandas" in m for m in py_mods)
    assert any("rasterio" in m for m in py_mods)
    assert any("scipy" in m for m in py_mods)


def test_r11_resolution_constants_canonical(mod):
    """Résolutions canoniques validées (100m default, 250m fragmentation)."""
    assert mod.RESOLUTION_DEFAULT_M == 100
    assert mod.RESOLUTION_FRAGMENTATION_M == 250
    assert mod.RESOLUTION_CLASSES_AGE_M == 250


def test_r11_derivatives_output_root_in_app_ext4(mod):
    """Sortie persistante sur /app ext4 (durable)."""
    assert mod.DERIVATIVES_OUTPUT_ROOT.startswith("/app/")

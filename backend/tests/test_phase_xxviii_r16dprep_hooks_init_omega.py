"""
Phase XXVIII · ORDRE N°52-R16-D-PREP — Tests stubs hooks TERRITOIRE_ULTIME
══════════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU · ANTI_GÉNÉRIQUE_STRICT

Valide :
  · 4 modules loaders stubs (environment, nutrition, comportement, predictif)
  · 4 dicts JSON valides STUB_INITIALIZATION
  · all_validated_for_r16dprep()
  · registry update (regles_territoires_canonical contient loader_module)
  · No business logic (rules dict empty, load_data returns None)
  · V30 INVIOLÉ respected (string présent dans tous les outputs)
"""
from __future__ import annotations

import importlib
import json
from pathlib import Path

import pytest


@pytest.fixture()
def loader():
    import engines.v8_institutional.especes.mffp_dictionaries_loader_omega as m
    importlib.reload(m)
    return m


@pytest.fixture()
def env_loader():
    import engines.v8_institutional.especes.environment_loader_omega as m
    importlib.reload(m)
    return m


@pytest.fixture()
def nut_loader():
    import engines.v8_institutional.especes.nutrition_loader_omega as m
    importlib.reload(m)
    return m


@pytest.fixture()
def comp_loader():
    import engines.v8_institutional.especes.comportement_loader_omega as m
    importlib.reload(m)
    return m


@pytest.fixture()
def pred_loader():
    import engines.v8_institutional.especes.predictif_loader_omega as m
    importlib.reload(m)
    return m


# ═════════════════════════════════════════════════════════════════════════
# 1. modules_loadable
# ═════════════════════════════════════════════════════════════════════════
def test_environment_loader_module_loadable(env_loader):
    assert env_loader.HOOK_NAME == "ENVIRONNEMENT"
    assert env_loader.IS_STUB is True
    assert env_loader.ORDRE == "N°52-R16-D-PREP"
    assert "is_available" in env_loader.__all__
    assert "probe" in env_loader.__all__
    assert "load_data" in env_loader.__all__


def test_nutrition_loader_module_loadable(nut_loader):
    assert nut_loader.HOOK_NAME == "NUTRITION"
    assert nut_loader.IS_STUB is True
    assert nut_loader.ORDRE == "N°52-R16-D-PREP"


def test_comportement_loader_module_loadable(comp_loader):
    assert comp_loader.HOOK_NAME == "COMPORTEMENT"
    assert comp_loader.IS_STUB is True


def test_predictif_loader_module_loadable(pred_loader):
    assert pred_loader.HOOK_NAME == "PREDICTIF"
    assert pred_loader.IS_STUB is True


# ═════════════════════════════════════════════════════════════════════════
# 2. dictionaries_valid (4 stubs JSON valides)
# ═════════════════════════════════════════════════════════════════════════
@pytest.mark.parametrize("dict_name,hook_name", [
    ("environment_rules", "ENVIRONNEMENT"),
    ("nutrition_rules", "NUTRITION"),
    ("comportement_rules", "COMPORTEMENT"),
    ("predictif_rules", "PREDICTIF"),
])
def test_stub_dict_loadable_and_valid(loader, dict_name, hook_name):
    d = loader.load_dictionary(dict_name)
    assert d is not None
    assert d["status"] == "VALIDÉ"
    assert d["mode"] == "STUB_INITIALIZATION"
    assert d["is_stub"] is True
    assert d["ordre"] == "N°52-R16-D-PREP"
    assert d["v30_lock"] == "INVIOLÉ"
    # No logic present
    assert d["rules"] == {}
    # Anti-générique strict acknowledged
    assert d["anti_generique_strict"]["verifiable"] is True
    # External paths expected (non-empty list)
    paths = d["external_paths_expected"]
    assert isinstance(paths, list)
    assert len(paths) >= 1


# ═════════════════════════════════════════════════════════════════════════
# 3. registry_updated (regles_territoires_canonical pointe vers loaders)
# ═════════════════════════════════════════════════════════════════════════
def test_registry_canonical_points_to_loader_modules(loader):
    d = loader.load_dictionary("regles_territoires_canonical")
    hooks = d["territoire_ultime_hooks"]["hooks_specs"]
    expected_loaders = {
        "ENVIRONNEMENT": "environment_loader_omega",
        "NUTRITION": "nutrition_loader_omega",
        "COMPORTEMENT": "comportement_loader_omega",
        "PREDICTIF": "predictif_loader_omega",
    }
    for hook, expected_suffix in expected_loaders.items():
        assert hook in hooks
        spec = hooks[hook]
        assert "loader_module" in spec
        assert expected_suffix in spec["loader_module"]
        assert spec.get("is_stub_initialized_R16D_PREP") is True
        assert "rules_dictionary" in spec


def test_loader_all_validated_for_r16dprep(loader):
    """all_validated_for_r16dprep returns True (4 stubs présents et VALIDÉ)."""
    assert loader.all_validated_for_r16dprep() is True


def test_loader_dictionary_files_includes_4_stubs(loader):
    expected_stub_keys = {
        "environment_rules", "nutrition_rules",
        "comportement_rules", "predictif_rules",
    }
    assert expected_stub_keys.issubset(set(loader.DICTIONARY_FILES.keys()))


# ═════════════════════════════════════════════════════════════════════════
# 4. no_logic_present (rules empty, load_data returns None)
# ═════════════════════════════════════════════════════════════════════════
@pytest.mark.parametrize("loader_fixture", [
    "env_loader", "nut_loader", "comp_loader", "pred_loader"])
def test_load_data_returns_none_anti_generique(loader_fixture, request):
    mod = request.getfixturevalue(loader_fixture)
    result = mod.load_data()
    # ANTI_GÉNÉRIQUE_STRICT : aucune donnée fabriquée
    assert result is None


def test_environment_is_available_returns_false_when_paths_absent(
        env_loader, monkeypatch, tmp_path):
    """is_available retourne False car paths externes attendus absents."""
    # Les paths /app/backend/data/environnement/... ne sont jamais présents
    # sur ce pod (Q3-Q4 attendu)
    assert env_loader.is_available() is False


def test_environment_is_available_true_when_at_least_one_path_present(
        env_loader, loader, tmp_path, monkeypatch):
    """is_available retourne True dès qu'≥1 path externe existe.

    Démontre que la connection automatique fonctionne : dès que le
    Commandant fournira une source, l'outil la détectera sans modif code.
    """
    # Créer un faux path qui existe
    fake_path = tmp_path / "noaa_hourly.nc"
    fake_path.write_bytes(b"fake")
    # Override le dict pour pointer vers ce faux path
    fake_dict = {
        "external_paths_expected": [str(fake_path)],
        "rules": {},
    }
    monkeypatch.setattr(loader, "load_dictionary",
                         lambda name: fake_dict)
    # Re-importer env_loader pour rafraîchir le cache
    import engines.v8_institutional.especes.environment_loader_omega as eml
    importlib.reload(eml)
    monkeypatch.setattr(
        eml, "load_dictionary",
        lambda name: fake_dict, raising=False)
    # Patch directement la fonction `load_dictionary` utilisée par env_loader
    import engines.v8_institutional.especes.mffp_dictionaries_loader_omega as ml
    monkeypatch.setattr(ml, "load_dictionary",
                         lambda name: fake_dict)
    importlib.reload(eml)
    # Re-fetch is_available
    assert eml.is_available() is True


# ═════════════════════════════════════════════════════════════════════════
# 5. probe() retourne structure stable
# ═════════════════════════════════════════════════════════════════════════
@pytest.mark.parametrize("loader_fixture,expected_hook", [
    ("env_loader", "ENVIRONNEMENT"),
    ("nut_loader", "NUTRITION"),
    ("comp_loader", "COMPORTEMENT"),
    ("pred_loader", "PREDICTIF"),
])
def test_probe_returns_stable_structure(
        loader_fixture, expected_hook, request):
    mod = request.getfixturevalue(loader_fixture)
    p = mod.probe()
    for k in ("manifest_id", "ordre", "hook_name", "is_stub",
              "available", "expected_paths_count",
              "paths_present", "paths_absent",
              "anti_generique_strict", "v30_lock"):
        assert k in p
    assert p["hook_name"] == expected_hook
    assert p["is_stub"] is True
    assert p["v30_lock"] == "INVIOLÉ"
    assert p["anti_generique_strict"] is True


# ═════════════════════════════════════════════════════════════════════════
# 6. v30_inviole_respected
# ═════════════════════════════════════════════════════════════════════════
@pytest.mark.parametrize("dict_name", [
    "environment_rules", "nutrition_rules",
    "comportement_rules", "predictif_rules",
])
def test_dict_v30_inviole_present(loader, dict_name):
    d = loader.load_dictionary(dict_name)
    assert d["v30_lock"] == "INVIOLÉ"


# ═════════════════════════════════════════════════════════════════════════
# 7. R9_RECALC_STATE : r16dprep_status présent
# ═════════════════════════════════════════════════════════════════════════
def test_r9_state_has_r16dprep_status_field():
    state_p = Path("/app/backend/data/territoire/R9_RECALC_STATE.json")
    if not state_p.exists():
        pytest.skip("R9_RECALC_STATE.json absent (pipeline jamais lancé)")
    s = json.loads(state_p.read_text(encoding="utf-8"))
    assert s.get("r16dprep_status") == "READY_FOR_R16D"
    assert "r16dprep_hooks_initialized" in s
    assert len(s["r16dprep_hooks_initialized"]) == 6
    assert "r16dprep_stub_loaders_created" in s
    assert len(s["r16dprep_stub_loaders_created"]) == 4
    # Le status global précédent doit être préservé (FUSION ADD-ONLY)
    assert s.get("status") in (
        "OK_REAL_PARTIAL_R16C", "OK_REAL_PARTIAL_R16B",
        "OK_REAL_PARTIAL_R16A", "OK_REAL_PARTIAL_R16B_WITH_FAILURES",
        "OK_WITH_STUBS")

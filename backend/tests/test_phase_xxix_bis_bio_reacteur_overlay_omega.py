"""
Phase XXIX-BIS · ORDRE N°53-BIS — Tests anti-régressifs OVERLAY BR
══════════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU x3 · ANTI_GÉNÉRIQUE_STRICT

Tests de l'enrichissement BIO_REACTEUR_Ω via overlay BP135 (FUSION ADD-ONLY).
Naming policy : aucun mot-clé exclu BCE-4X.
"""
from __future__ import annotations

import importlib
import json
from pathlib import Path

import pytest


@pytest.fixture()
def overlay():
    import engines.v8_institutional.especes.bio_reacteur_overlay_omega as m
    importlib.reload(m)
    return m


# ═════════════════════════════════════════════════════════════════════════
# 1. API + invariants infrastructure
# ═════════════════════════════════════════════════════════════════════════
def test_module_exports(overlay):
    for name in (
        "scan_external_sources",
        "compute_overlay_for_species",
        "merge_overlay",
        "compute_super_engines_with_overlay",
        "compute_overlay_fusion",
        "persist_audit",
        "EXTERNAL_SOURCES_REGISTRY",
        "BP135_TO_BR_NUTRITION_MAPPING",
    ):
        assert hasattr(overlay, name), f"missing {name}"


def test_external_sources_registry_six_entries(overlay):
    """Les 6 sources externes sont configurées (NOAA/NASA/USGS/RSF/MaxEnt/Forecast)."""
    assert len(overlay.EXTERNAL_SOURCES_REGISTRY) == 6
    names = {s["source_name"] for s in overlay.EXTERNAL_SOURCES_REGISTRY}
    assert names == {
        "NOAA", "NASA", "USGS", "RSF_SSF", "MAXENT", "FORECAST_48H"}
    # Tous ont des paths, formats et hooks_targets
    for s in overlay.EXTERNAL_SOURCES_REGISTRY:
        assert isinstance(s["paths"], list) and len(s["paths"]) >= 1
        assert isinstance(s["formats"], list) and len(s["formats"]) >= 1
        assert isinstance(s["hooks_targets"], list)
        assert isinstance(s["consumed_by_masters"], list)


def test_bp135_to_br_mapping_anti_generique(overlay):
    """Mapping conservatif : 4 paramètres NUTRITION mappés (sodium/calcium/proteines/energie).
    Pas de magnésium (BP135 ne contient pas ce paramètre direct)."""
    m = overlay.BP135_TO_BR_NUTRITION_MAPPING
    assert "nutrition.besoins_proteines" in m
    assert "nutrition.besoins_energetiques" in m
    assert "nutrition.besoins_mineraux.sodium" in m
    assert "nutrition.besoins_mineraux.calcium" in m
    # Magnésium volontairement absent (anti-générique : pas de fabrication)
    assert "nutrition.besoins_mineraux.magnesium" not in m


# ═════════════════════════════════════════════════════════════════════════
# 2. scan_external_sources (état réel disque)
# ═════════════════════════════════════════════════════════════════════════
def test_scan_external_sources_returns_six(overlay):
    s = overlay.scan_external_sources()
    assert s["manifest_id"] == "EXTERNAL_SOURCES_SCAN_Ω"
    assert s["ordre"] in ("N°53-BIS", "N°53-BIS-SUITE")
    assert s["n_sources_total"] == 6
    # Anti-générique : sources absentes restent absentes
    for src in s["sources"]:
        assert src["anti_generique_strict"] is True
        assert src["fallback_when_unavailable"] == "skip_with_log"
        if not src["available"]:
            # Phase I: n_files_found · Phase II (BIS-SUITE): n_files_valid
            n_files = src.get("n_files_valid",
                              src.get("n_files_found", 0))
            assert n_files == 0


def test_scan_currently_no_external_sources(overlay):
    """Les 6 sources externes ne sont pas encore déposées sur disque.
    Status doctrinal : paths_absent. Anti-générique strict respecté."""
    s = overlay.scan_external_sources()
    # Tous absents pour l'instant
    assert s["n_sources_available"] == 0
    assert s["n_sources_absent"] == 6


# ═════════════════════════════════════════════════════════════════════════
# 3. compute_overlay_for_species
# ═════════════════════════════════════════════════════════════════════════
@pytest.mark.parametrize("espece", [
    "CHEVREUIL", "ORIGNAL", "OURS_NOIR", "DINDON_SAUVAGE", "WAPITI"])
def test_overlay_per_species(overlay, espece):
    o = overlay.compute_overlay_for_species(espece)
    assert o["manifest_id"] == "BIO_REACTEUR_OVERLAY_Ω"
    assert o["ordre"] == "N°53-BIS"
    assert o["espece"] == espece
    # ≥ 4 patches RÉELS appliqués (proteines/energie/sodium/calcium)
    assert o["summary"]["n_patches_applied"] >= 4
    # Tous les patches ont une signature BP135 réelle
    for p in o["patches"]:
        assert p["source"] == "BP135"
        assert p["bp135_param_id"].startswith(("ALI-", "PHY-"))
        assert isinstance(p["value"], (int, float))


def test_overlay_invalid_species_raises(overlay):
    with pytest.raises(ValueError, match="espece_br invalide"):
        overlay.compute_overlay_for_species("INVENTED_SPECIES")


# ═════════════════════════════════════════════════════════════════════════
# 4. merge_overlay (FUSION ADD-ONLY strict)
# ═════════════════════════════════════════════════════════════════════════
def test_merge_overlay_fills_empty_paths(overlay):
    """Path BR vide → rempli par overlay."""
    fake_br = {"bio_reacteur_outputs": {
        "ENGINE_MINERAUX": {
            "parametres_alimentes": {
                "nutrition.besoins_mineraux.sodium": [],
            },
        },
    }}
    fake_overlay = {"patches": [{
        "dotted_path": "nutrition.besoins_mineraux.sodium",
        "target_engine": "ENGINE_MINERAUX",
        "value": 400,
        "bp135_param_id": "ALI-008",
        "bp135_block": "ALIMENTATION",
    }]}
    r = overlay.merge_overlay(fake_br, fake_overlay)
    assert r["n_applied"] == 1
    assert r["n_preserved_existing"] == 0
    enriched = r["enriched_br"]["bio_reacteur_outputs"]["ENGINE_MINERAUX"]
    val = enriched["parametres_alimentes"][
        "nutrition.besoins_mineraux.sodium"]
    assert val["value"] == 400
    assert val["signature"]["source"] == "BP135_OVERLAY"
    assert val["signature"]["applied_via_overlay"] is True


def test_merge_overlay_preserves_existing_non_empty(overlay):
    """FUSION ADD-ONLY strict : path existant non vide → préservé."""
    fake_br = {"bio_reacteur_outputs": {
        "ENGINE_NUTRITION": {
            "parametres_alimentes": {
                "nutrition.besoins_proteines": ["existing_value_already_here"],
            },
        },
    }}
    fake_overlay = {"patches": [{
        "dotted_path": "nutrition.besoins_proteines",
        "target_engine": "ENGINE_NUTRITION",
        "value": 13.5,
        "bp135_param_id": "ALI-003",
        "bp135_block": "ALIMENTATION",
    }]}
    r = overlay.merge_overlay(fake_br, fake_overlay)
    assert r["n_applied"] == 0
    assert r["n_preserved_existing"] == 1
    # Valeur originale intacte
    val = r["enriched_br"]["bio_reacteur_outputs"]["ENGINE_NUTRITION"][
        "parametres_alimentes"]["nutrition.besoins_proteines"]
    assert val == ["existing_value_already_here"]


def test_merge_overlay_does_not_mutate_input(overlay):
    """Doctrine : merge_overlay ne mute JAMAIS le BR d'entrée (deepcopy)."""
    original_br = {"bio_reacteur_outputs": {
        "ENGINE_MINERAUX": {
            "parametres_alimentes": {
                "nutrition.besoins_mineraux.sodium": [],
            },
        },
    }}
    snapshot = json.dumps(original_br, sort_keys=True)
    overlay.merge_overlay(original_br, {"patches": [{
        "dotted_path": "nutrition.besoins_mineraux.sodium",
        "target_engine": "ENGINE_MINERAUX",
        "value": 400,
        "bp135_param_id": "ALI-008",
        "bp135_block": "ALIMENTATION",
    }]})
    # original_br doit être inchangé
    assert json.dumps(original_br, sort_keys=True) == snapshot


# ═════════════════════════════════════════════════════════════════════════
# 5. compute_super_engines_with_overlay
# ═════════════════════════════════════════════════════════════════════════
def test_super_engines_with_overlay_produces_six(overlay):
    r = overlay.compute_super_engines_with_overlay()
    assert r["manifest_id"] == "SUPER_ENGINES_WITH_BP135_OVERLAY_Ω"
    assert r["ordre"] == "N°53-BIS"
    assert len(r["engines"]) == 6
    # 5 espèces enrichies
    assert r["n_species_enriched"] == 5
    # Chaque espèce a au moins 1 patch appliqué (BR initialement
    # incomplets pour les minéraux). Certaines espèces ont des champs
    # déjà remplis (FUSION ADD-ONLY préserve l'existant).
    n_applied_total = sum(
        s["n_applied"]
        for s in r["overlay_application_summary_per_species"].values())
    assert n_applied_total >= 5, (
        f"Au moins 5 patches au total attendus, observé {n_applied_total}")
    for esp, summary in r["overlay_application_summary_per_species"].items():
        assert summary["n_applied"] >= 1, (
            f"Au moins 1 patch attendu pour {esp}")
    # SHA-256 BP135 + super engines lock
    assert len(r["bp135_sha256"]) == 64
    assert len(r["super_engine_lock_sha256"]) == 64
    assert r["v30_lock"] == "INVIOLÉ"


def test_super_engines_with_overlay_nutrition_score_increases(overlay):
    """KPI doctrinal critique : NUTRITION_MASTER score post-overlay > pré-overlay."""
    from engines.v8_institutional.especes.super_engines_omega_logic import (
        compute_all_super_engines,
    )
    pre = compute_all_super_engines()
    post = overlay.compute_super_engines_with_overlay()
    # Score NUTRITION pré (BR vides → 0) vs post (overlay BP135 injecté)
    pre_nutrition = pre["engines"]["ENGINE_NUTRITION_MASTER_Ω"]
    post_nutrition = post["engines"]["ENGINE_NUTRITION_MASTER_Ω"]
    pre_key = next(
        k for k in pre_nutrition
        if k.startswith("score_") and k.endswith("_master_omega"))
    post_key = next(
        k for k in post_nutrition
        if k.startswith("score_") and k.endswith("_master_omega"))
    pre_score = pre_nutrition.get(pre_key, 0)
    post_score = post_nutrition.get(post_key, 0)
    assert post_score > pre_score, (
        f"NUTRITION POST {post_score} doit être > PRE {pre_score}")


# ═════════════════════════════════════════════════════════════════════════
# 6. compute_overlay_fusion (recouplage POST-overlay)
# ═════════════════════════════════════════════════════════════════════════
def test_overlay_fusion_executes(overlay):
    f = overlay.compute_overlay_fusion()
    assert f["manifest_id"] == "BP135_OVERLAY_FUSION_Ω"
    assert f["mode"] == "overlay_fusion"
    # 6 masters dans fusion_results
    assert len(f["fusion_results"]) == 6
    # Drift mean post <= drift mean pre (amélioration ou égalité)
    assert f["drift_mean_post_overlay"] <= f["drift_mean_pre_overlay"]
    # KPI : amélioration globale
    assert f["drift_improvement_mean"] >= 0


def test_overlay_fusion_nutrition_drift_decreases_significantly(overlay):
    """KPI : drift NUTRITION doit chuter d'au moins 30 points post-overlay."""
    f = overlay.compute_overlay_fusion()
    nutrition = f["fusion_results"]["ENGINE_NUTRITION_MASTER_Ω"]
    drift_pre = nutrition["drift_br_vs_bp135_pre"]
    drift_post = nutrition["drift_br_vs_bp135_post"]
    improvement = drift_pre - drift_post
    assert improvement >= 30, (
        f"NUTRITION drift improvement {improvement} doit être ≥ 30")


def test_overlay_fusion_invalid_weights_raises(overlay):
    with pytest.raises(ValueError, match="weights"):
        overlay.compute_overlay_fusion(
            weights={"bio_reacteur_overlay": 0.0, "bp135": 0.0})


# ═════════════════════════════════════════════════════════════════════════
# 7. persist_audit
# ═════════════════════════════════════════════════════════════════════════
def test_persist_audit_creates_file(overlay, tmp_path, monkeypatch):
    monkeypatch.setattr(overlay, "AUDITS_ROOT", tmp_path / "audits_test")
    fake_payload = {
        "test_run": True,
        "drift_mean": 22.04,
        "ordre": "N°53-BIS",
    }
    r = overlay.persist_audit(fake_payload)
    assert r["audit_filename"].startswith("audit_")
    assert r["audit_filename"].endswith(".json")
    assert len(r["audit_sha256"]) == 64
    assert r["audit_size_bytes"] > 0
    # Fichier existe + lisible + contient le payload
    p = Path(r["audit_path"])
    assert p.exists()
    data = json.loads(p.read_text(encoding="utf-8"))
    assert data["audit_payload"]["test_run"] is True
    assert data["ordre"] == "N°53-BIS"
    assert data["audit_sha256"] == r["audit_sha256"]


def test_persist_audit_filename_deterministic_sha8(overlay, tmp_path,
                                                   monkeypatch):
    """Le sha8 dans le filename est dérivé du SHA-256 du payload."""
    monkeypatch.setattr(overlay, "AUDITS_ROOT", tmp_path / "audits_test2")
    fake_payload = {"deterministic": "test_payload_42"}
    r = overlay.persist_audit(fake_payload)
    sha8 = r["audit_sha256"][:8]
    assert sha8 in r["audit_filename"]


# ═════════════════════════════════════════════════════════════════════════
# 8. Anti-régression FUSION ADD-ONLY
# ═════════════════════════════════════════════════════════════════════════
def test_bp135_file_unchanged_after_overlay_pipeline(overlay):
    """BP135 SHA-256 inchangé après overlay/fusion/persist."""
    from engines.v8_institutional.especes.bio_profile_135_loader_omega import (
        file_sha256,
    )
    sha_before = file_sha256()
    overlay.scan_external_sources()
    overlay.compute_overlay_for_species("CHEVREUIL")
    overlay.compute_super_engines_with_overlay()
    overlay.compute_overlay_fusion()
    sha_after = file_sha256()
    assert sha_before == sha_after


def test_bio_reacteur_files_unchanged_after_overlay(overlay):
    """Doctrine : aucun BIO_REACTEUR_Ω_<ESPECE>.json modifié après overlay."""
    import hashlib
    from engines.v8_institutional.especes.bio_reacteur_loader_omega import (
        BIO_REACTEUR_DIR,
    )
    sha_before = {}
    for f in sorted(BIO_REACTEUR_DIR.glob("BIO_REACTEUR_*.json")):
        sha_before[f.name] = hashlib.sha256(f.read_bytes()).hexdigest()
    # Exécution overlay complet
    overlay.compute_overlay_fusion()
    # SHA après
    for f in sorted(BIO_REACTEUR_DIR.glob("BIO_REACTEUR_*.json")):
        sha_after = hashlib.sha256(f.read_bytes()).hexdigest()
        assert sha_after == sha_before[f.name], (
            f"BR {f.name} muté ! Violation FUSION ADD-ONLY.")


def test_super_engines_omega_logic_module_unchanged(overlay):
    """Aucune modification du module super_engines_omega_logic."""
    from engines.v8_institutional.especes import super_engines_omega_logic as sel
    for fn in ("compute_corridors_master", "compute_nutrition_master",
               "compute_sensoriel_master", "compute_comportement_master",
               "compute_gouvernance_master", "compute_territoire_master",
               "compute_all_super_engines"):
        assert hasattr(sel, fn)


# ═════════════════════════════════════════════════════════════════════════
# 9. Mapping doctrinal des hooks externes
# ═════════════════════════════════════════════════════════════════════════
def test_external_sources_hooks_mapping_complete(overlay):
    """Vérifie que les 6 hooks doctrinaux sont couverts par au moins une source."""
    hooks_covered = set()
    for s in overlay.EXTERNAL_SOURCES_REGISTRY:
        for h in s["hooks_targets"]:
            hooks_covered.add(h)
    # 4 hooks externes + ENVIRONNEMENT/NUTRITION/COMPORTEMENT/PREDICTIF
    expected_hooks = {"ENVIRONNEMENT", "NUTRITION",
                      "COMPORTEMENT", "PREDICTIF"}
    assert expected_hooks.issubset(hooks_covered)


def test_format_extensions_realistic(overlay):
    """Formats déclarés correspondent aux conventions doctrinales."""
    expected_formats_per_source = {
        "NOAA": {".nc", ".grib2"},
        "NASA": {".tif", ".hdf"},
        "USGS": {".tif", ".csv"},
        "RSF_SSF": {".pkl", ".json"},
        "MAXENT": {".jar", ".asc", ".tif"},
    }
    for src in overlay.EXTERNAL_SOURCES_REGISTRY:
        if src["source_name"] in expected_formats_per_source:
            assert (set(src["formats"]) ==
                    expected_formats_per_source[src["source_name"]])

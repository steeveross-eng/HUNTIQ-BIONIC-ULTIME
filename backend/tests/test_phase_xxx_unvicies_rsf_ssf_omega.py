"""test_phase_xxx_unvicies_rsf_ssf_omega.py
═══════════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU x3 · ANTI_GÉNÉRIQUE_STRICT

Tests pytest neutres pour RSF_SSF_VALIDATE_Ω + HOOK_ACTIVATE_Ω.

NAMING POLICY STRICTE : aucun mot-clé exclu BCE-4X.
Aucun appel HTTP réel exécuté ici (probes RÉELS via curl séparément).
═══════════════════════════════════════════════════════════════════════════
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path("/app/backend")))


# ═════════════════════════════════════════════════════════════════════════
# Section 1 — Module structure + GBIF taxon registry
# ═════════════════════════════════════════════════════════════════════════
def test_rsf_ssf_module_imports():
    """Module rsf_ssf_omega doit exposer signatures requises."""
    from engines.v8_institutional.especes import rsf_ssf_omega
    assert hasattr(rsf_ssf_omega, "validate_rsf_ssf_per_species")
    assert hasattr(rsf_ssf_omega, "activate_rsf_ssf_hook")
    assert hasattr(rsf_ssf_omega, "get_rsf_ssf_hook_status")


def test_gbif_taxon_keys_5_species_complete():
    """5 espèces BP135 avec taxon keys GBIF vérifiés LIVE."""
    from engines.v8_institutional.especes.rsf_ssf_omega import (
        GBIF_TAXON_KEYS_BP135,
    )
    expected = {"cerf", "orignal", "ours", "dindon", "wapiti"}
    assert set(GBIF_TAXON_KEYS_BP135.keys()) == expected
    # Taxon keys vérifiés LIVE
    assert GBIF_TAXON_KEYS_BP135["cerf"]["taxon_key"] == 2440965
    assert GBIF_TAXON_KEYS_BP135["orignal"]["taxon_key"] == 2440940
    assert GBIF_TAXON_KEYS_BP135["ours"]["taxon_key"] == 2433407
    assert GBIF_TAXON_KEYS_BP135["dindon"]["taxon_key"] == 9606290
    assert GBIF_TAXON_KEYS_BP135["wapiti"]["taxon_key"] == 8600904


def test_wapiti_doctrinal_note_documented():
    """Wapiti doctrinal note (non natif Québec) DOIT être documentée."""
    from engines.v8_institutional.especes.rsf_ssf_omega import (
        GBIF_TAXON_KEYS_BP135,
    )
    wapiti = GBIF_TAXON_KEYS_BP135["wapiti"]
    assert "doctrinal_note" in wapiti
    note = wapiti["doctrinal_note"].lower()
    assert "non natif" in note or "réintroduction" in note
    assert "anti-générique" in note


def test_quebec_bbox_correct():
    """Bbox Québec 46-49°N × -73 à -69°W (5 sites BP135)."""
    from engines.v8_institutional.especes.rsf_ssf_omega import (
        QUEBEC_BBOX,
    )
    assert QUEBEC_BBOX["lat_min"] == 46.0
    assert QUEBEC_BBOX["lat_max"] == 49.0
    assert QUEBEC_BBOX["lon_min"] == -73.0
    assert QUEBEC_BBOX["lon_max"] == -69.0


def test_validation_paths_under_pipelines():
    """Persistance dans /app/backend/data/pipelines/rsf_ssf/."""
    from engines.v8_institutional.especes.rsf_ssf_omega import (
        RSF_SSF_VALIDATION_PATH, RSF_SSF_HOOK_ACTIVATION_PATH,
    )
    assert "data/pipelines/rsf_ssf" in str(
        RSF_SSF_VALIDATION_PATH)
    assert "data/pipelines/rsf_ssf" in str(
        RSF_SSF_HOOK_ACTIVATION_PATH)


# ═════════════════════════════════════════════════════════════════════════
# Section 2 — Pivot doctrinal anti-générique
# ═════════════════════════════════════════════════════════════════════════
def test_pivot_doctrinal_documented_in_module():
    """Pivot RSF/SSF→MaxEnt-lite documenté avec citations."""
    src = Path(
        "/app/backend/engines/v8_institutional/especes/"
        "rsf_ssf_omega.py").read_text(encoding="utf-8")
    # Citations authentiques RSF/SSF (qu'on NE peut PAS faire)
    assert "Manly" in src
    assert "Boyce" in src
    assert "Avgar" in src
    # Citations pivot MaxEnt-lite (ce qu'on FAIT honnêtement)
    assert "Phillips" in src
    assert "Elith" in src
    assert "10.1016/j.ecolmodel.2005.03.026" in src
    assert "10.1111/j.1472-4642.2010.00725.x" in src
    # Pivot explicite documenté
    assert "MAXENT_LITE_GBIF" in src
    assert "presence-only" in src.lower()


def test_pivot_doctrinal_in_validate_payload_explicit():
    """Le payload VALIDATE expose pivot doctrinal explicit."""
    from engines.v8_institutional.especes.rsf_ssf_omega import (
        validate_rsf_ssf_per_species,
    )
    from engines.v8_institutional.especes import (
        pipeline_guardrails_omega, rsf_ssf_omega,
    )
    original_fetch = (
        rsf_ssf_omega._fetch_gbif_presence_for_species)
    original_enforced = (
        pipeline_guardrails_omega.is_guardrails_enforced)
    try:
        pipeline_guardrails_omega.is_guardrails_enforced = (
            lambda: True)

        def mock_fetch(taxon_key, bbox, limit=300, timeout_s=20):
            return {
                "url": "mock", "http_status": 200,
                "elapsed_ms": 10.0, "valid": True,
                "count_total_gbif": 100,
                "n_occurrences_extracted": 50,
                "centroid_lat_lon": {
                    "lat": 47.0, "lon": -71.0},
                "variance_lat_lon": {
                    "var_lat": 0.5, "var_lon": 0.5,
                    "std_lat_deg": 0.7, "std_lon_deg": 0.7},
                "bbox_extracted": {
                    "lat_min": 46.0, "lat_max": 48.0,
                    "lon_min": -72.0, "lon_max": -70.0},
                "first_year": 2020, "last_year": 2025,
                "occurrences_sample_first_5": [],
            }
        rsf_ssf_omega._fetch_gbif_presence_for_species = mock_fetch

        result = validate_rsf_ssf_per_species(
            species_to_taxon={"cerf": 2440965},
            persist=False,
        )
        assert "pivot_doctrinal_anti_generique" in result
        pivot = result["pivot_doctrinal_anti_generique"]
        assert pivot["this_is_NOT_authentic_rsf_ssf"] is True
        assert "Phillips" in str(
            pivot["scientific_references_primary"])
        assert "Manly" in str(
            pivot["scientific_references_authentic_rsf_ssf_blocked"])
        assert (result["provider_logical"] == "RSF_SSF")
        assert (result["provider_physical"] == "MAXENT_LITE_GBIF")
    finally:
        pipeline_guardrails_omega.is_guardrails_enforced = (
            original_enforced)
        rsf_ssf_omega._fetch_gbif_presence_for_species = (
            original_fetch)


def test_outputs_partially_unblocked_4_outputs_listed():
    """4 outputs partiels listés (Phillips 2006 envelope)."""
    from engines.v8_institutional.especes.rsf_ssf_omega import (
        validate_rsf_ssf_per_species,
    )
    from engines.v8_institutional.especes import (
        pipeline_guardrails_omega, rsf_ssf_omega,
    )
    original_fetch = (
        rsf_ssf_omega._fetch_gbif_presence_for_species)
    original_enforced = (
        pipeline_guardrails_omega.is_guardrails_enforced)
    try:
        pipeline_guardrails_omega.is_guardrails_enforced = (
            lambda: True)

        def mock_fetch(taxon_key, bbox, limit=300, timeout_s=20):
            return {
                "valid": False, "n_occurrences": 0,
                "reason": "no_occurrences_in_bbox",
                "http_status": 200,
            }
        rsf_ssf_omega._fetch_gbif_presence_for_species = mock_fetch

        result = validate_rsf_ssf_per_species(
            species_to_taxon={"wapiti": 8600904},
            persist=False,
        )
        assert "outputs_partially_unblocked_via_this_hook" in result
        unblocked = result[
            "outputs_partially_unblocked_via_this_hook"]
        assert len(unblocked) == 4
        assert any(
            "envelope_phillips_2006" in o for o in unblocked)
        assert any("niche_breadth" in o for o in unblocked)
        # Outputs encore deferred
        assert ("outputs_still_deferred_authentic_rsf_ssf_required"
                in result)
        deferred = result[
            "outputs_still_deferred_authentic_rsf_ssf_required"]
        assert any("avgar_2016" in o.lower() for o in deferred)
        assert any("manly_2002" in o.lower() for o in deferred)
    finally:
        pipeline_guardrails_omega.is_guardrails_enforced = (
            original_enforced)
        rsf_ssf_omega._fetch_gbif_presence_for_species = (
            original_fetch)


# ═════════════════════════════════════════════════════════════════════════
# Section 3 — Helpers de calcul
# ═════════════════════════════════════════════════════════════════════════
def test_haversine_km_basic():
    """Distance Haversine cohérente (Québec→Montréal ≈ 230km)."""
    from engines.v8_institutional.especes.rsf_ssf_omega import (
        _haversine_km,
    )
    # Québec (46.81, -71.21) → Montréal (45.50, -73.57)
    d = _haversine_km(46.81, -71.21, 45.50, -73.57)
    assert 220 < d < 250  # 230km approx


def test_envelope_index_at_centroid_returns_max():
    """Envelope au centroid exact = score 100 (Phillips 2006)."""
    from engines.v8_institutional.especes.rsf_ssf_omega import (
        _compute_envelope_index_per_site,
    )
    res = _compute_envelope_index_per_site(
        site_lat=47.0, site_lon=-71.0,
        species_centroid_lat=47.0, species_centroid_lon=-71.0,
        species_std_lat=0.5, species_std_lon=0.5,
    )
    assert res["habitat_suitability_envelope"] == 100.0
    assert res["distance_to_centroid_km"] == 0.0


def test_envelope_index_far_away_returns_low_score():
    """Envelope loin du centroid (5σ) → score très bas."""
    from engines.v8_institutional.especes.rsf_ssf_omega import (
        _compute_envelope_index_per_site,
    )
    res = _compute_envelope_index_per_site(
        site_lat=50.0, site_lon=-71.0,
        species_centroid_lat=47.0, species_centroid_lon=-71.0,
        species_std_lat=0.5, species_std_lon=0.5,
    )
    # 5σ → exp(-(5)^2/2) ≈ 3.7e-6 → score ≈ 0
    assert res["habitat_suitability_envelope"] < 1.0


def test_envelope_index_protects_against_zero_std():
    """Si std=0, floor 0.05 appliqué (anti-divbyzero)."""
    from engines.v8_institutional.especes.rsf_ssf_omega import (
        _compute_envelope_index_per_site,
    )
    res = _compute_envelope_index_per_site(
        site_lat=47.1, site_lon=-71.0,
        species_centroid_lat=47.0, species_centroid_lon=-71.0,
        species_std_lat=0.0, species_std_lon=0.0,
    )
    # Pas de crash, score doit être valide ∈ [0, 100]
    assert 0.0 <= res["habitat_suitability_envelope"] <= 100.0


# ═════════════════════════════════════════════════════════════════════════
# Section 4 — Anti-générique : Wapiti deferred + manifest fabriqué
# ═════════════════════════════════════════════════════════════════════════
def test_wapiti_deferred_when_zero_occurrences():
    """Wapiti n=0 GBIF → DEFERRED honnête (pas fabrication)."""
    from engines.v8_institutional.especes.rsf_ssf_omega import (
        validate_rsf_ssf_per_species,
    )
    from engines.v8_institutional.especes import (
        pipeline_guardrails_omega, rsf_ssf_omega,
    )
    original_fetch = (
        rsf_ssf_omega._fetch_gbif_presence_for_species)
    original_enforced = (
        pipeline_guardrails_omega.is_guardrails_enforced)
    try:
        pipeline_guardrails_omega.is_guardrails_enforced = (
            lambda: True)

        def mock_fetch(taxon_key, bbox, limit=300, timeout_s=20):
            return {
                "valid": False, "n_occurrences": 0,
                "count_total_gbif": 0,
                "reason": "no_occurrences_in_bbox",
                "http_status": 200,
                "elapsed_ms": 10.0,
            }
        rsf_ssf_omega._fetch_gbif_presence_for_species = mock_fetch

        result = validate_rsf_ssf_per_species(
            species_to_taxon={"wapiti": 8600904},
            persist=False,
        )
        wapiti = result["species_results"]["wapiti"]
        assert wapiti["envelope_per_bp135_site"] is None
        assert "deferred_doctrinal" in wapiti
        deferred = wapiti["deferred_doctrinal"]
        assert "anti-générique" in deferred["reason"]
        assert (result["n_species_deferred"] == 1)
        assert result["valid"] is False
    finally:
        pipeline_guardrails_omega.is_guardrails_enforced = (
            original_enforced)
        rsf_ssf_omega._fetch_gbif_presence_for_species = (
            original_fetch)


def test_activate_rejects_fabricated_manifest_sha256():
    """SHA fabriqué (64 zéros) doit être REJETÉ."""
    from engines.v8_institutional.especes.rsf_ssf_omega import (
        activate_rsf_ssf_hook,
    )
    from engines.v8_institutional.especes import (
        pipeline_guardrails_omega,
    )
    original = pipeline_guardrails_omega.is_guardrails_enforced
    try:
        pipeline_guardrails_omega.is_guardrails_enforced = (
            lambda: True)
        result = activate_rsf_ssf_hook(
            manifest_sha256="0" * 64,
            reason="test_fabricated_manifest_rejection",
            persist=False,
        )
        assert result["activated"] is False
        assert result["verdict"] == (
            "RSF_SSF_HOOK_REJECTED_MANIFEST_NOT_FOUND_OR_INVALID")
        assert result["anti_generique_strict"] is True
        assert result["v30_lock"] == "INVIOLÉ"
    finally:
        pipeline_guardrails_omega.is_guardrails_enforced = original


def test_find_validated_manifest_returns_none_for_unknown():
    """SHA inconnu → None."""
    from engines.v8_institutional.especes.rsf_ssf_omega import (
        _find_validated_rsf_ssf_manifest,
    )
    result = _find_validated_rsf_ssf_manifest("z" * 64)
    assert result is None


def test_get_status_returns_valid_dict():
    """get_rsf_ssf_hook_status retourne dict valide."""
    from engines.v8_institutional.especes.rsf_ssf_omega import (
        get_rsf_ssf_hook_status,
    )
    status = get_rsf_ssf_hook_status()
    assert "manifest_id" in status
    assert "current_status" in status
    assert "v30_lock" in status
    assert status["v30_lock"] == "INVIOLÉ"
    assert status["current_status"] in (
        "NOT_ACTIVATED", "ACTIVATED_OPERATIONAL")


# ═════════════════════════════════════════════════════════════════════════
# Section 5 — Guardrails enforcement
# ═════════════════════════════════════════════════════════════════════════
def test_validate_requires_guardrails_enforced():
    """Sans guardrails ENFORCED, lève GuardrailsNotEnforced."""
    from engines.v8_institutional.especes import (
        rsf_ssf_omega, pipeline_guardrails_omega,
    )
    original = pipeline_guardrails_omega.is_guardrails_enforced
    try:
        pipeline_guardrails_omega.is_guardrails_enforced = (
            lambda: False)
        with pytest.raises(
                pipeline_guardrails_omega.GuardrailsNotEnforcedError):
            rsf_ssf_omega.validate_rsf_ssf_per_species(persist=False)
    finally:
        pipeline_guardrails_omega.is_guardrails_enforced = original


def test_activate_requires_guardrails_enforced():
    """Sans guardrails ENFORCED, hook_activate lève également."""
    from engines.v8_institutional.especes import (
        rsf_ssf_omega, pipeline_guardrails_omega,
    )
    original = pipeline_guardrails_omega.is_guardrails_enforced
    try:
        pipeline_guardrails_omega.is_guardrails_enforced = (
            lambda: False)
        with pytest.raises(
                pipeline_guardrails_omega.GuardrailsNotEnforcedError):
            rsf_ssf_omega.activate_rsf_ssf_hook(
                manifest_sha256="x" * 64, persist=False)
    finally:
        pipeline_guardrails_omega.is_guardrails_enforced = original


# ═════════════════════════════════════════════════════════════════════════
# Section 6 — Anti-régression V30_LOCK
# ═════════════════════════════════════════════════════════════════════════
def test_module_does_not_import_super_engines_logic():
    """Anti-régression doctrinale : NO_ENGINE_RECOMPUTE_TRIGGERED."""
    src = Path(
        "/app/backend/engines/v8_institutional/especes/"
        "rsf_ssf_omega.py").read_text(encoding="utf-8")
    assert "super_engines_omega_logic" not in src


def test_v30_lock_bp135_sha256_unchanged_after_import():
    """BP135 SHA-256 ne doit JAMAIS changer après import."""
    bp135_path = Path(
        "/app/backend/data/registry_docs/bio_profile_omega_135/"
        "BIO_PROFILE_OMEGA_135_OFFICIAL.json")
    if not bp135_path.exists():
        pytest.skip("BP135 official non présent")
    import hashlib
    sha_before = hashlib.sha256(
        bp135_path.read_bytes()).hexdigest()
    from engines.v8_institutional.especes import rsf_ssf_omega  # noqa: F401
    sha_after = hashlib.sha256(
        bp135_path.read_bytes()).hexdigest()
    assert sha_before == sha_after


def test_validate_persists_in_dedicated_pipeline_directory():
    """Persistance dans data/pipelines/rsf_ssf/ (V30_LOCK)."""
    from engines.v8_institutional.especes.rsf_ssf_omega import (
        RSF_SSF_ROOT, RSF_SSF_VALIDATION_PATH,
    )
    assert "pipelines/rsf_ssf" in str(RSF_SSF_ROOT)
    assert "registry_docs" not in str(RSF_SSF_ROOT)
    assert str(RSF_SSF_VALIDATION_PATH).startswith(
        str(RSF_SSF_ROOT))

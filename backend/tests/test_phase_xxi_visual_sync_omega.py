"""test_phase_xxi_visual_sync_omega — P21 canonical visual sync.

COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU · ANTI-GÉNÉRIQUE STRICT.
Neutral filename — no excluded keyword.
"""
from __future__ import annotations



def test_module_import_omega():
    from engines.v8_institutional.especes import (
        canonical_visual_sync_omega as mod,
    )
    assert hasattr(mod, "validate_layer_consistency")
    assert hasattr(mod, "compute_visual_signature")
    assert hasattr(mod, "get_canonical_visual_sync_status")
    assert mod.MIN_ACTIVE_LAYERS_PER_WAYPOINT == 7
    assert mod.FOCUS_MODE_DIM_OPACITY == 20
    assert mod.FOCUS_MODE_FOCUSED_OPACITY == 100
    assert len(mod.CANONICAL_LAYER_CATALOG) == 18


def test_validation_below_minimum_omega():
    from engines.v8_institutional.especes.canonical_visual_sync_omega import (
        validate_layer_consistency,
    )
    res = validate_layer_consistency(
        active_layer_ids=["zones", "corridors"])
    assert res["verdict"] == "FAIL_BELOW_MINIMUM_7_LAYERS"
    assert res["is_valid_doctrinal"] is False
    assert res["components"]["n_active_canonical"] == 2
    assert res["components"]["meets_minimum_7_layers"] is False


def test_validation_unknown_id_warned_omega():
    from engines.v8_institutional.especes.canonical_visual_sync_omega import (
        validate_layer_consistency,
    )
    res = validate_layer_consistency(active_layer_ids=[
        "zones", "corridors", "affuts", "salines", "hotspots",
        "vent", "contamination", "pigeon_layer",  # unknown
    ])
    assert res["verdict"] == "WARN_UNKNOWN_IDS_PRESENT"
    assert res["is_valid_doctrinal"] is True
    assert "pigeon_layer" in res["components"]["unknown_ids"]


def test_validation_all_valid_omega():
    from engines.v8_institutional.especes.canonical_visual_sync_omega import (
        validate_layer_consistency,
    )
    res = validate_layer_consistency(active_layer_ids=[
        "zones", "corridors", "affuts", "salines", "hotspots",
        "vent", "contamination",
    ])
    assert res["verdict"] == "VALID_CONSISTENT_DOCTRINAL"
    assert res["is_valid_doctrinal"] is True
    assert (res["components"]["bio_omega_present_count"] == 5)


def test_validation_bio_omega_incomplete_omega():
    from engines.v8_institutional.especes.canonical_visual_sync_omega import (
        validate_layer_consistency,
    )
    # 7 layers but missing salines+hotspots
    res = validate_layer_consistency(active_layer_ids=[
        "zones", "corridors", "affuts",
        "vent", "contamination", "sensoriel", "ndvi_overlay",
    ])
    assert res["verdict"] == "WARN_BIO_OMEGA_INCOMPLETE"
    assert "salines" in res["components"]["bio_omega_missing"]
    assert "hotspots" in res["components"]["bio_omega_missing"]


def test_visual_signature_deterministic_omega():
    from engines.v8_institutional.especes.canonical_visual_sync_omega import (
        compute_visual_signature,
    )
    sig1 = compute_visual_signature(
        active_layer_ids=["zones", "corridors", "affuts"],
        opacity_map={"zones": 80, "corridors": 60})
    sig2 = compute_visual_signature(
        active_layer_ids=["affuts", "corridors", "zones"],  # diff order
        opacity_map={"corridors": 60, "zones": 80})
    # Same set + same opacities → same SHA (sorted internally)
    assert sig1["visual_sha256"] == sig2["visual_sha256"]
    assert len(sig1["visual_sha256"]) == 64
    assert sig1["n_active_layers"] == 3
    assert sig1["n_opacity_overrides"] == 2


def test_visual_signature_changes_on_opacity_omega():
    from engines.v8_institutional.especes.canonical_visual_sync_omega import (
        compute_visual_signature,
    )
    sig1 = compute_visual_signature(
        active_layer_ids=["zones"], opacity_map={"zones": 80})
    sig2 = compute_visual_signature(
        active_layer_ids=["zones"], opacity_map={"zones": 50})
    assert sig1["visual_sha256"] != sig2["visual_sha256"]


def test_canonical_visual_sync_status_omega():
    from engines.v8_institutional.especes.canonical_visual_sync_omega import (
        get_canonical_visual_sync_status,
    )
    payload = get_canonical_visual_sync_status(
        active_layer_ids=["zones", "corridors", "affuts",
                           "salines", "hotspots", "vent",
                           "contamination"],
        opacity_map={"zones": 80})
    assert payload["ordre"] == "P21_CANONICAL_VISUAL_LOCK_Ω"
    assert payload["v30_lock"] == "INVIOLÉ"
    assert payload["minimum_layers_per_waypoint"] == 7
    assert payload["n_canonical_layers"] == 18
    assert payload["focus_mode"]["enabled"] is True
    assert payload["focus_mode"]["dim_non_focused_pct"] == 20
    assert (payload["ux_lock"]["collapse_duplicate_panels"]
            == "PERMANENT")
    assert (payload["ux_lock"]["enforce_no_mini_panels"]
            == "PERMANENT")
    assert (payload["footer_cryptographic"][
        "canonical_footer_indicator"] == "ENFORCED")
    assert payload["validation"]["is_valid_doctrinal"] is True
    assert "visual_sha256" in payload["visual_signature"]

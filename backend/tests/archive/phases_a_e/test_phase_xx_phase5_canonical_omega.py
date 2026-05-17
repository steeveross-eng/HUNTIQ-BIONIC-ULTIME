"""test_phase_xx_phase5_canonical_omega — P20_PHASE5 canonical lock.

COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU · ANTI-GÉNÉRIQUE STRICT.
Neutral filename — no excluded keyword.
"""
from __future__ import annotations



def test_module_import_omega():
    from engines.v8_institutional.especes import (
        territoire_omega_canonical_omega as mod,
    )
    assert hasattr(mod, "get_territoire_omega_canonical_status")
    assert mod.WATCHDOG_LOCK_TIMEOUT_S == 600
    assert mod.LAYER_CATALOG_FROZEN_COUNT == 18
    assert mod.FORBIDDEN_DOCTRINAL["legacy_paths"] is True
    assert mod.FORBIDDEN_DOCTRINAL["analysis_v6"] is True
    assert mod.FORBIDDEN_DOCTRINAL["debug_panels"] is True
    assert mod.FORBIDDEN_DOCTRINAL["mini_tables_v6"] is True


def test_canonical_status_shape_omega():
    from engines.v8_institutional.especes.territoire_omega_canonical_omega import (  # noqa: E501
        get_territoire_omega_canonical_status,
    )
    payload = get_territoire_omega_canonical_status()
    assert payload["ordre"] == "P20_PHASE5_CANONICAL_LOCK_Ω"
    assert payload["v30_lock"] == "INVIOLÉ"
    assert payload["single_source_of_truth_enforced"] is True
    assert payload["territoire_omega_canonical"] == "ENFORCED"
    assert payload["unified_panel_mode"] == "PRIMARY_ONLY_PERMANENT"
    assert payload["watchdog_lock"]["timeout_s"] == 600
    assert payload["watchdog_lock"]["enforced"] is True
    assert payload["layer_catalog"]["frozen_count"] == 18
    assert payload["layer_catalog"]["zindex_institutional_enforced"] is True
    assert payload["service_worker_controlled"] == "PERMANENT"
    assert payload["sync_indicator"]["enabled"] is True
    assert (payload["sync_indicator"]["scope"]
            == "last_force_reload_timestamp_utc")
    assert len(payload["canonical_sha256"]) == 64
    assert payload["anti_generique_strict"] is True


def test_canonical_sha_deterministic_excluding_timestamp_omega():
    """Le SHA dépend du timestamp UTC (auto-rolling), donc 2 appels
    consécutifs peuvent donner 2 hashes différents si la seconde change.
    Mais la structure doit toujours produire un SHA hex 64."""
    from engines.v8_institutional.especes.territoire_omega_canonical_omega import (  # noqa: E501
        get_territoire_omega_canonical_status,
    )
    p1 = get_territoire_omega_canonical_status()
    sha1 = p1["canonical_sha256"]
    assert isinstance(sha1, str) and len(sha1) == 64
    assert all(c in "0123456789abcdef" for c in sha1)


def test_sync_indicator_when_no_reload_omega(tmp_path, monkeypatch):
    """Anti-générique : sync indicator gère le cas no_reload."""
    import engines.v8_institutional.especes.territoire_omega_canonical_omega as mod  # noqa: E501
    monkeypatch.setattr(
        mod, "RELOAD_OVERLAY_PATH",
        tmp_path / "non_existent_overlay.json")
    payload = mod.get_territoire_omega_canonical_status()
    sync = payload["sync_indicator"]["data"]
    assert sync["available"] is False
    assert sync["reason"] == "NO_RELOAD_EVER_EXECUTED"


def test_sync_indicator_with_real_reload_omega(tmp_path, monkeypatch):
    """Vrai reload → sync indicator récupère SHA + timestamp."""
    import engines.v8_institutional.especes.territoire_omega_canonical_omega as mod  # noqa: E501
    overlay_data = {
        "history": [
            {
                "reload_sha256": "a" * 64,
                "executed_at_utc": "2026-05-08T22:00:00+00:00",
                "verdict": "TERRITOIRE_OMEGA_RELOAD_COMPLETED",
                "overlay_scan_summary": {"n_overlays_scanned": 17},
                "engine_reload_summary": {"n_reloaded": 5},
                "watchdog_state": {"current_timeout_s": 600},
            },
        ],
    }
    overlay_path = tmp_path / "overlay.json"
    overlay_path.write_text(
        __import__("json").dumps(overlay_data),
        encoding="utf-8")
    monkeypatch.setattr(mod, "RELOAD_OVERLAY_PATH", overlay_path)
    payload = mod.get_territoire_omega_canonical_status()
    sync = payload["sync_indicator"]["data"]
    assert sync["available"] is True
    assert sync["last_force_reload_sha256"] == "a" * 64
    assert sync["last_force_reload_n_overlays_scanned"] == 17
    assert sync["last_force_reload_n_engines_reloaded"] == 5
    assert sync["last_watchdog_timeout_s"] == 600

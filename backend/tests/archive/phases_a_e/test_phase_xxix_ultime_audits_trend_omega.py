"""
Phase XXIX-ULTIME · ORDRE N°53-BIS-SUITE-ULTIME — Tests anti-régressifs
══════════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU x3 · ANTI_GÉNÉRIQUE_STRICT

Tests :
  · list_audits_trend (série temporelle, 30 points max, stats agrégés)
  · watch_and_recompute_if_hooks_activated (transition detection)
  · Activation effective (deposit fichier valide → flip available=True)
  · Détection anomalies sur dépôts physiques
  · V30_LOCK INVIOLÉ post-activation

Naming policy : aucun mot-clé exclu BCE-4X.
"""
from __future__ import annotations

import importlib
import json
import time
from pathlib import Path

import pytest


@pytest.fixture()
def overlay():
    import engines.v8_institutional.especes.bio_reacteur_overlay_omega as m
    importlib.reload(m)
    return m


# ═════════════════════════════════════════════════════════════════════════
# 1. list_audits_trend
# ═════════════════════════════════════════════════════════════════════════
def test_audits_trend_empty_when_no_audits(
        overlay, tmp_path, monkeypatch):
    monkeypatch.setattr(overlay, "AUDITS_ROOT", tmp_path / "empty_trend")
    r = overlay.list_audits_trend()
    assert r["manifest_id"] == "AUDITS_TREND_Ω"
    assert r["ordre"] == "N°53-BIS-SUITE-ULTIME"
    assert r["n_points_returned"] == 0
    assert r["points"] == []


def test_audits_trend_returns_required_fields(
        overlay, tmp_path, monkeypatch):
    monkeypatch.setattr(overlay, "AUDITS_ROOT", tmp_path / "trend_fields")
    # Créer 3 audits via persist_audit
    for i in range(3):
        overlay.persist_audit({
            "audit_type": "test_trend",
            "drift_max_post_overlay": 50.0 - i * 5,
            "drift_mean_post_overlay": 25.0 - i * 2,
            "score_global_fusion_post_overlay": 50.0 + i * 2,
            "bp135_sha256": "fd9374c3" + "0" * 56,
        })
        time.sleep(0.01)
    r = overlay.list_audits_trend()
    assert r["n_points_returned"] == 3
    # Chaque point a les champs strictement requis Commandant
    for p in r["points"]:
        for field in ("timestamp_utc", "drift_max", "drift_mean",
                      "score_global_fusion", "sha256"):
            assert field in p, f"missing {field}"
        assert len(p["sha256"]) == 64
    # Tri chronologique ascendant
    timestamps = [p["timestamp_utc"] for p in r["points"]]
    assert timestamps == sorted(timestamps)


def test_audits_trend_chronological_order(
        overlay, tmp_path, monkeypatch):
    """La série doit être chronologique ASCENDANTE (ancien → récent)."""
    monkeypatch.setattr(overlay, "AUDITS_ROOT",
                        tmp_path / "trend_chrono")
    for i in range(4):
        overlay.persist_audit({
            "audit_type": "chrono_test",
            "drift_max_post_overlay": 10 + i,
            "drift_mean_post_overlay": 5,
            "score_global_fusion_post_overlay": 50,
        })
        time.sleep(0.05)
    r = overlay.list_audits_trend()
    # Ordre chronologique : drift_max augmente (10, 11, 12, 13)
    drifts = [p["drift_max"] for p in r["points"]]
    assert drifts == sorted(drifts)
    assert r["time_series_order"] == "chronological_ascending"


def test_audits_trend_limit_respected(overlay, tmp_path, monkeypatch):
    """limit=N → max N points retournés (les plus récents)."""
    monkeypatch.setattr(overlay, "AUDITS_ROOT",
                        tmp_path / "trend_limit")
    for i in range(10):
        overlay.persist_audit({
            "audit_type": "limit_test",
            "drift_max_post_overlay": 10 + i,
            "drift_mean_post_overlay": 5,
            "score_global_fusion_post_overlay": 50,
        })
        time.sleep(0.01)
    r = overlay.list_audits_trend(limit=5)
    assert r["n_points_returned"] == 5
    assert r["limit_requested"] == 5
    # Les 5 derniers (les plus récents) → drift_max [15..19] (les plus
    # grands)
    drifts = [p["drift_max"] for p in r["points"]]
    assert min(drifts) >= 14


def test_audits_trend_aggregated_stats(overlay, tmp_path, monkeypatch):
    monkeypatch.setattr(overlay, "AUDITS_ROOT", tmp_path / "trend_stats")
    overlay.persist_audit({
        "audit_type": "stats", "drift_max_post_overlay": 10,
        "drift_mean_post_overlay": 5, "score_global_fusion_post_overlay": 50})
    time.sleep(0.01)
    overlay.persist_audit({
        "audit_type": "stats", "drift_max_post_overlay": 30,
        "drift_mean_post_overlay": 15, "score_global_fusion_post_overlay": 60})
    r = overlay.list_audits_trend()
    stats = r["aggregated_stats"]
    assert stats["n_points"] == 2
    # drift_max stats
    assert stats["drift_max"]["min"] == 10
    assert stats["drift_max"]["max"] == 30
    assert stats["drift_max"]["first"] == 10
    assert stats["drift_max"]["last"] == 30
    assert stats["drift_max"]["delta_first_to_last"] == 20.0
    # score stats
    assert stats["score_global_fusion"]["delta_first_to_last"] == 10.0


def test_audits_trend_filter_audit_type(overlay, tmp_path, monkeypatch):
    monkeypatch.setattr(overlay, "AUDITS_ROOT",
                        tmp_path / "trend_filter")
    overlay.persist_audit({"audit_type": "type_alpha",
                           "drift_max_post_overlay": 10,
                           "drift_mean_post_overlay": 5,
                           "score_global_fusion_post_overlay": 50})
    overlay.persist_audit({"audit_type": "type_beta",
                           "drift_max_post_overlay": 20,
                           "drift_mean_post_overlay": 10,
                           "score_global_fusion_post_overlay": 55})
    r = overlay.list_audits_trend(audit_type="alpha")
    assert r["n_points_returned"] == 1


# ═════════════════════════════════════════════════════════════════════════
# 2. watch_and_recompute_if_hooks_activated
# ═════════════════════════════════════════════════════════════════════════
def test_watcher_no_transition_no_recompute(overlay, tmp_path, monkeypatch):
    """Premier appel sans état précédent : aucune transition (sources tout absentes)
    → pas de recompute auto."""
    monkeypatch.setattr(overlay, "AUDITS_ROOT", tmp_path / "watcher_a")
    monkeypatch.setattr(
        overlay, "HOOKS_WATCHER_STATE_PATH",
        tmp_path / "watcher_a" / "_hooks_state.json")
    r = overlay.watch_and_recompute_if_hooks_activated(force=False)
    assert r["manifest_id"] == "HOOKS_WATCHER_RECOMPUTE_Ω"
    assert r["recompute_triggered"] is False
    assert r["recompute_audit"] is None
    assert r["n_transitions"] == 0


def test_watcher_force_triggers_recompute(overlay, tmp_path, monkeypatch):
    """force=True → recompute exécuté même sans transition."""
    monkeypatch.setattr(overlay, "AUDITS_ROOT", tmp_path / "watcher_force")
    monkeypatch.setattr(
        overlay, "HOOKS_WATCHER_STATE_PATH",
        tmp_path / "watcher_force" / "_hooks_state.json")
    r = overlay.watch_and_recompute_if_hooks_activated(force=True)
    assert r["recompute_triggered"] is True
    assert r["recompute_audit"] is not None
    assert r["recompute_audit"]["manifest_id"] == "RECOMPUTE_DRIFT_AUDIT_Ω"
    assert r["force_requested"] is True


def test_watcher_persists_state(overlay, tmp_path, monkeypatch):
    """Le watcher persiste l'état pour comparaison ultérieure."""
    state_path = tmp_path / "watcher_persist" / "_hooks_state.json"
    monkeypatch.setattr(overlay, "AUDITS_ROOT",
                        tmp_path / "watcher_persist")
    monkeypatch.setattr(overlay, "HOOKS_WATCHER_STATE_PATH", state_path)
    overlay.watch_and_recompute_if_hooks_activated(force=False)
    assert state_path.exists()
    state = json.loads(state_path.read_text(encoding="utf-8"))
    assert "source_states" in state
    assert "last_scan_at_utc" in state
    assert len(state["source_states"]) == 6


def test_watcher_detects_source_activation_transition(
        overlay, tmp_path, monkeypatch):
    """Simule un dépôt physique d'une source : transition détectée +
    recompute déclenché automatiquement."""
    audits_dir = tmp_path / "watcher_transition"
    state_path = audits_dir / "_hooks_state.json"
    monkeypatch.setattr(overlay, "AUDITS_ROOT", audits_dir)
    monkeypatch.setattr(overlay, "HOOKS_WATCHER_STATE_PATH", state_path)

    # 1er appel : tout absent → state initial
    r1 = overlay.watch_and_recompute_if_hooks_activated(force=False)
    assert r1["recompute_triggered"] is False

    # Simulation : on injecte une fausse source disponible dans le registry
    fake_data_dir = tmp_path / "fake_external"
    fake_data_dir.mkdir()
    valid_file = fake_data_dir / "valid.nc"
    valid_file.write_bytes(b"\x89HDF\r\n\x1a\n")

    fake_registry = [{
        "source_name": "NOAA_FAKE_TEST",
        "paths": [fake_data_dir],
        "expected_subpath_glob": "*",
        "formats": [".nc", ".grib2"],
        "hooks_targets": ["ENVIRONNEMENT"],
        "consumed_by_masters": ["SENSORIEL_MASTER_Ω"],
    }]
    monkeypatch.setattr(
        overlay, "EXTERNAL_SOURCES_REGISTRY", fake_registry)

    # 2e appel : source devenue disponible → transition + recompute
    r2 = overlay.watch_and_recompute_if_hooks_activated(force=False)
    transitions = r2["transitions_detected"]
    activation_transitions = [
        t for t in transitions
        if t["transition"] == "PATHS_ABSENT_TO_AVAILABLE"]
    assert len(activation_transitions) == 1
    assert (activation_transitions[0]["source"]
            == "NOAA_FAKE_TEST")
    assert r2["recompute_triggered"] is True
    assert r2["recompute_audit"] is not None


def test_watcher_anomaly_kept_unavailable(
        overlay, tmp_path, monkeypatch):
    """Source avec fichier zero_size → anomalie + available=False
    → aucune transition vers AVAILABLE."""
    audits_dir = tmp_path / "watcher_anomaly"
    state_path = audits_dir / "_hooks_state.json"
    monkeypatch.setattr(overlay, "AUDITS_ROOT", audits_dir)
    monkeypatch.setattr(overlay, "HOOKS_WATCHER_STATE_PATH", state_path)

    fake_data_dir = tmp_path / "fake_anomaly_dir"
    fake_data_dir.mkdir()
    (fake_data_dir / "empty.nc").touch()  # zero_size

    fake_registry = [{
        "source_name": "NOAA_ANOMALY_TEST",
        "paths": [fake_data_dir],
        "expected_subpath_glob": "*",
        "formats": [".nc"],
        "hooks_targets": ["ENVIRONNEMENT"],
        "consumed_by_masters": ["SENSORIEL_MASTER_Ω"],
    }]
    monkeypatch.setattr(
        overlay, "EXTERNAL_SOURCES_REGISTRY", fake_registry)

    r = overlay.watch_and_recompute_if_hooks_activated(force=False)
    # Pas de transition vers AVAILABLE car anomalie présente
    assert r["recompute_triggered"] is False
    state = r["current_state"]["NOAA_ANOMALY_TEST"]
    assert state["available"] is False
    assert state["n_files_anomalies"] == 1


# ═════════════════════════════════════════════════════════════════════════
# 3. V30_LOCK INVIOLÉ
# ═════════════════════════════════════════════════════════════════════════
def test_v30_lock_inviolate_after_watcher(overlay, tmp_path, monkeypatch):
    """SHA-256 BP135 + BR files inchangés après watcher (avec recompute)."""
    import hashlib
    from engines.v8_institutional.especes.bio_profile_135_loader_omega import (
        file_sha256,
    )
    from engines.v8_institutional.especes.bio_reacteur_loader_omega import (
        BIO_REACTEUR_DIR,
    )
    monkeypatch.setattr(overlay, "AUDITS_ROOT", tmp_path / "watcher_v30")
    monkeypatch.setattr(
        overlay, "HOOKS_WATCHER_STATE_PATH",
        tmp_path / "watcher_v30" / "_hooks_state.json")
    bp_before = file_sha256()
    br_before = {
        f.name: hashlib.sha256(f.read_bytes()).hexdigest()
        for f in BIO_REACTEUR_DIR.glob("BIO_REACTEUR_*.json")
    }
    overlay.watch_and_recompute_if_hooks_activated(force=True)
    bp_after = file_sha256()
    br_after = {
        f.name: hashlib.sha256(f.read_bytes()).hexdigest()
        for f in BIO_REACTEUR_DIR.glob("BIO_REACTEUR_*.json")
    }
    assert bp_before == bp_after
    assert br_before == br_after


def test_module_exports_phase_iii(overlay):
    for name in ("list_audits_trend",
                 "watch_and_recompute_if_hooks_activated",
                 "HOOKS_WATCHER_STATE_PATH"):
        assert hasattr(overlay, name)


# ═════════════════════════════════════════════════════════════════════════
# 4. Cohérence audits-trend ↔ audits-list
# ═════════════════════════════════════════════════════════════════════════
def test_audits_trend_consistent_with_audits_list(
        overlay, tmp_path, monkeypatch):
    """Cohérence stricte : chaque point trend correspond à un audit list."""
    monkeypatch.setattr(overlay, "AUDITS_ROOT",
                        tmp_path / "consistency")
    for i in range(3):
        overlay.persist_audit({
            "audit_type": "consistency_test",
            "drift_max_post_overlay": 10 + i,
            "drift_mean_post_overlay": 5,
            "score_global_fusion_post_overlay": 50,
        })
        time.sleep(0.01)
    list_r = overlay.list_audits()
    trend_r = overlay.list_audits_trend()
    # Mêmes nombres
    assert trend_r["n_points_returned"] == list_r["total"]
    # Chaque sha256 trend ∈ list audits sha256
    list_shas = {a["sha256"] for a in list_r["audits"]}
    trend_shas = {p["sha256"] for p in trend_r["points"]}
    assert trend_shas == list_shas

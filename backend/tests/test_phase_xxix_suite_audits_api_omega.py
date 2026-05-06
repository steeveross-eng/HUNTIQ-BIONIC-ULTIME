"""
Phase XXIX-SUITE · ORDRE N°53-BIS-SUITE — Tests anti-régressifs Phase II
══════════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU x3 · ANTI_GÉNÉRIQUE_STRICT

Tests :
  · Activation hooks externes (registry étendu sous-paths Commandant)
  · Détection d'anomalies (zero_size, format_unexpected, unreadable)
  · recompute_with_drift_audit (BEFORE/AFTER persisté)
  · API audits-list (champs obligatoires, pagination, filtres)
  · V30_LOCK INVIOLÉ post-exécution
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
# 1. Registry étendu (sous-paths exacts du Commandant)
# ═════════════════════════════════════════════════════════════════════════
def test_registry_has_expected_subpath_glob_per_source(overlay):
    """Chaque source doit déclarer son `expected_subpath_glob` doctrinal."""
    expected = {
        "NOAA": "2025/*",
        "NASA": "ndvi/*",
        "USGS": "soil/*",
    }
    by_name = {s["source_name"]: s
               for s in overlay.EXTERNAL_SOURCES_REGISTRY}
    for name, glob in expected.items():
        assert by_name[name]["expected_subpath_glob"] == glob


def test_registry_per_species_aware_for_models(overlay):
    """RSF_SSF et MAXENT sont per-species-aware (5 paths espèces)."""
    by_name = {s["source_name"]: s
               for s in overlay.EXTERNAL_SOURCES_REGISTRY}
    # RSF_SSF : 10 paths (5 RSF + 5 SSF)
    assert by_name["RSF_SSF"]["per_species_aware"] is True
    assert len(by_name["RSF_SSF"]["paths"]) == 10
    # MAXENT : 5 paths (1 par espèce)
    assert by_name["MAXENT"]["per_species_aware"] is True
    assert len(by_name["MAXENT"]["paths"]) == 5


def test_registry_paths_match_commandant_directive(overlay):
    """Les paths configurés correspondent strictement aux paths Commandant."""
    by_name = {s["source_name"]: s
               for s in overlay.EXTERNAL_SOURCES_REGISTRY}
    assert str(by_name["NOAA"]["paths"][0]) == "/data/external/noaa"
    assert str(by_name["NASA"]["paths"][0]) == "/data/external/nasa"
    assert str(by_name["USGS"]["paths"][0]) == "/data/external/usgs"
    assert str(by_name["FORECAST_48H"]["paths"][0]) == \
        "/streams/forecast48h"
    # RSF/SSF per species
    rsf_paths = [str(p) for p in by_name["RSF_SSF"]["paths"]]
    assert "/models/rsf/chevreuil" in rsf_paths
    assert "/models/ssf/wapiti" in rsf_paths
    # MAXENT per species
    maxent_paths = [str(p) for p in by_name["MAXENT"]["paths"]]
    assert "/models/maxent/orignal" in maxent_paths


# ═════════════════════════════════════════════════════════════════════════
# 2. Détection d'anomalies
# ═════════════════════════════════════════════════════════════════════════
def test_anomaly_zero_size_file(overlay, tmp_path):
    """Fichier de taille 0 → anomalie `zero_size`."""
    f = tmp_path / "test.tif"
    f.touch()  # taille 0
    anomalies = overlay._detect_file_anomalies(f, [".tif"])
    assert "zero_size" in anomalies


def test_anomaly_format_unexpected(overlay, tmp_path):
    """Extension non listée → anomalie `format_unexpected`."""
    f = tmp_path / "test.exe"
    f.write_bytes(b"\x00\x01\x02")
    anomalies = overlay._detect_file_anomalies(f, [".tif", ".hdf"])
    assert "format_unexpected" in anomalies


def test_no_anomaly_valid_file(overlay, tmp_path):
    f = tmp_path / "test.tif"
    f.write_bytes(b"\x49\x49\x2A\x00")  # TIFF magic bytes
    anomalies = overlay._detect_file_anomalies(f, [".tif"])
    assert anomalies == []


def test_scan_detects_anomalies_when_files_present(
        overlay, tmp_path, monkeypatch):
    """Scan signale anomalies + available=False si fichiers anormaux."""
    fake_path = tmp_path / "fake_external_noaa"
    fake_path.mkdir()
    (fake_path / "empty.nc").touch()  # zero_size
    (fake_path / "valid.nc").write_bytes(b"\x89HDF\r\n")
    fake_registry = [{
        "source_name": "NOAA_TEST",
        "paths": [fake_path],
        "expected_subpath_glob": "*",
        "formats": [".nc", ".grib2"],
        "hooks_targets": ["ENVIRONNEMENT"],
        "consumed_by_masters": ["SENSORIEL_MASTER_Ω"],
    }]
    monkeypatch.setattr(
        overlay, "EXTERNAL_SOURCES_REGISTRY", fake_registry)
    s = overlay.scan_external_sources()
    src = s["sources"][0]
    assert src["n_files_anomalies"] == 1
    assert src["n_files_valid"] == 1
    # Doctrine stricte : anomalies présentes → available=False
    assert src["available"] is False
    assert s["n_anomalies_total"] == 1


def test_scan_all_absent_currently(overlay):
    """Sources Commandant : aucune actuellement déposée → 6/6 absent."""
    s = overlay.scan_external_sources()
    assert s["n_sources_total"] == 6
    assert s["n_sources_available"] == 0
    assert s["n_sources_absent"] == 6
    assert s["n_anomalies_total"] == 0
    assert s["ordre"] == "N°53-BIS-SUITE"


# ═════════════════════════════════════════════════════════════════════════
# 3. recompute_with_drift_audit
# ═════════════════════════════════════════════════════════════════════════
def test_recompute_produces_before_after_snapshots(overlay, tmp_path,
                                                   monkeypatch):
    monkeypatch.setattr(overlay, "AUDITS_ROOT",
                        tmp_path / "audits_recompute")
    r = overlay.recompute_with_drift_audit(
        reason="pytest_recompute", persist=True)
    assert r["manifest_id"] == "RECOMPUTE_DRIFT_AUDIT_Ω"
    assert r["ordre"] == "N°53-BIS-SUITE"
    assert r["audit_type"] == "recompute_with_drift_before_after"
    assert r["reason"] == "pytest_recompute"
    # Snapshots
    for ks in ("drift_max", "drift_mean", "score_global_fusion"):
        assert ks in r["before"]
        assert ks in r["after"]
        assert ks in r["deltas"]
    # Snapshot timestamps
    assert "snapshot_at_utc" in r["before"]
    assert "snapshot_at_utc" in r["after"]
    # Bp135 SHA-256 inviolé
    assert len(r["bp135_sha256"]) == 64
    # Persistance
    assert r["audit_persisted"] is not None
    assert Path(r["audit_persisted"]["audit_path"]).exists()


def test_recompute_drift_mean_improves(overlay, tmp_path, monkeypatch):
    """KPI : drift_mean après overlay <= drift_mean avant overlay."""
    monkeypatch.setattr(overlay, "AUDITS_ROOT",
                        tmp_path / "audits_kpi")
    r = overlay.recompute_with_drift_audit(persist=True)
    # delta drift_mean = before - after >= 0 (amélioration)
    assert r["deltas"]["drift_mean"] >= 0
    assert r["improvement_drift_mean"] == r["deltas"]["drift_mean"]


def test_recompute_no_persist_when_persist_false(overlay, tmp_path,
                                                 monkeypatch):
    monkeypatch.setattr(overlay, "AUDITS_ROOT",
                        tmp_path / "audits_no_persist")
    r = overlay.recompute_with_drift_audit(persist=False)
    assert "audit_persisted" not in r
    # Aucun fichier créé
    audits_dir = tmp_path / "audits_no_persist"
    assert (
        not audits_dir.exists()
        or not any(audits_dir.glob("audit_*.json")))


def test_recompute_includes_external_sources_state(overlay, tmp_path,
                                                   monkeypatch):
    monkeypatch.setattr(overlay, "AUDITS_ROOT",
                        tmp_path / "audits_state")
    r = overlay.recompute_with_drift_audit(persist=True)
    state = r["external_sources_state"]
    for ks in ("n_total", "n_available", "n_absent"):
        assert ks in state
    assert state["n_total"] == 6


# ═════════════════════════════════════════════════════════════════════════
# 4. list_audits (API helper)
# ═════════════════════════════════════════════════════════════════════════
def test_list_audits_empty_when_dir_empty(overlay, tmp_path, monkeypatch):
    monkeypatch.setattr(overlay, "AUDITS_ROOT", tmp_path / "empty_audits")
    r = overlay.list_audits()
    assert r["total"] == 0
    assert r["audits"] == []
    assert r["manifest_id"] == "AUDITS_LIST_Ω"


def test_list_audits_returns_required_fields(overlay, tmp_path, monkeypatch):
    audits_dir = tmp_path / "audits_with_data"
    monkeypatch.setattr(overlay, "AUDITS_ROOT", audits_dir)
    # Créer un audit via persist + recompute
    overlay.recompute_with_drift_audit(reason="t1", persist=True)
    overlay.recompute_with_drift_audit(reason="t2", persist=True)
    r = overlay.list_audits()
    assert r["total"] == 2
    for record in r["audits"]:
        # Champs obligatoires (Commandant)
        for ks in ("audit_id", "timestamp_utc", "sha256",
                   "drift_max", "drift_mean", "score_global_fusion",
                   "bp135_sha256"):
            assert ks in record, f"missing {ks}"
        assert record["audit_id"].startswith("audit_")
        assert len(record["sha256"]) == 64
        assert len(record["bp135_sha256"]) == 64


def test_list_audits_pagination(overlay, tmp_path, monkeypatch):
    audits_dir = tmp_path / "audits_pag"
    monkeypatch.setattr(overlay, "AUDITS_ROOT", audits_dir)
    # Créer 5 audits
    for i in range(5):
        overlay.persist_audit({"audit_type": "test", "test_n": i,
                               "drift_max_post_overlay": 10 + i,
                               "drift_mean_post_overlay": 5 + i,
                               "score_global_fusion_post_overlay": 50})
    # Page 1 / page_size 2
    r1 = overlay.list_audits(page=1, page_size=2)
    assert r1["total"] == 5
    assert r1["n_returned"] == 2
    assert len(r1["audits"]) == 2
    # Page 2 / page_size 2
    r2 = overlay.list_audits(page=2, page_size=2)
    assert r2["n_returned"] == 2
    # Page 3 / page_size 2 (le dernier)
    r3 = overlay.list_audits(page=3, page_size=2)
    assert r3["n_returned"] == 1


def test_list_audits_filter_drift_max(overlay, tmp_path, monkeypatch):
    audits_dir = tmp_path / "audits_filter_d"
    monkeypatch.setattr(overlay, "AUDITS_ROOT", audits_dir)
    for drift_v in (5, 10, 25, 50, 80):
        overlay.persist_audit({"audit_type": "test",
                               "drift_max_post_overlay": drift_v,
                               "drift_mean_post_overlay": drift_v / 2,
                               "score_global_fusion_post_overlay": 50})
    # Filtre drift_max entre 20 et 60 → 25 et 50 → 2 résultats
    r = overlay.list_audits(drift_max_min=20, drift_max_max=60)
    assert r["total"] == 2
    for rec in r["audits"]:
        assert 20 <= rec["drift_max"] <= 60


def test_list_audits_filter_audit_type(overlay, tmp_path, monkeypatch):
    audits_dir = tmp_path / "audits_filter_t"
    monkeypatch.setattr(overlay, "AUDITS_ROOT", audits_dir)
    overlay.persist_audit(
        {"audit_type": "recompute_with_drift_before_after",
         "drift_max_post_overlay": 10,
         "drift_mean_post_overlay": 5,
         "score_global_fusion_post_overlay": 50})
    overlay.persist_audit(
        {"audit_type": "manual_inspection",
         "drift_max_post_overlay": 10,
         "drift_mean_post_overlay": 5,
         "score_global_fusion_post_overlay": 50})
    r = overlay.list_audits(audit_type="recompute")
    assert r["total"] == 1
    assert "recompute" in r["audits"][0]["audit_type"]


def test_list_audits_consistent_with_disk_files(
        overlay, tmp_path, monkeypatch):
    """API ↔ fichiers disque : cohérence stricte (chaque audit_id = 1 file)."""
    audits_dir = tmp_path / "audits_consistency"
    monkeypatch.setattr(overlay, "AUDITS_ROOT", audits_dir)
    for i in range(3):
        overlay.persist_audit({"audit_type": "test", "n": i,
                               "drift_max_post_overlay": 10,
                               "drift_mean_post_overlay": 5,
                               "score_global_fusion_post_overlay": 50})
    r = overlay.list_audits()
    # Pour chaque audit retourné par l'API, le fichier existe sur disque
    for rec in r["audits"]:
        f = audits_dir / rec["filename"]
        assert f.exists()
        # Le SHA-256 affiché dans l'API matche le SHA-256 stocké
        data = json.loads(f.read_text(encoding="utf-8"))
        assert data["audit_sha256"] == rec["sha256"]


# ═════════════════════════════════════════════════════════════════════════
# 5. V30_LOCK INVIOLÉ post-exécution complète
# ═════════════════════════════════════════════════════════════════════════
def test_v30_lock_inviolate_after_recompute(overlay, tmp_path, monkeypatch):
    """SHA-256 BP135 + BR files inchangés après recompute."""
    import hashlib
    from engines.v8_institutional.especes.bio_profile_135_loader_omega import (
        file_sha256,
    )
    from engines.v8_institutional.especes.bio_reacteur_loader_omega import (
        BIO_REACTEUR_DIR,
    )
    monkeypatch.setattr(overlay, "AUDITS_ROOT",
                        tmp_path / "audits_v30")
    bp_before = file_sha256()
    br_before = {
        f.name: hashlib.sha256(f.read_bytes()).hexdigest()
        for f in BIO_REACTEUR_DIR.glob("BIO_REACTEUR_*.json")
    }
    overlay.recompute_with_drift_audit(persist=True)
    bp_after = file_sha256()
    br_after = {
        f.name: hashlib.sha256(f.read_bytes()).hexdigest()
        for f in BIO_REACTEUR_DIR.glob("BIO_REACTEUR_*.json")
    }
    assert bp_before == bp_after
    assert br_before == br_after


def test_module_exports_phase_ii(overlay):
    for name in ("recompute_with_drift_audit", "list_audits",
                 "ESPECES_FOR_MODELS"):
        assert hasattr(overlay, name)

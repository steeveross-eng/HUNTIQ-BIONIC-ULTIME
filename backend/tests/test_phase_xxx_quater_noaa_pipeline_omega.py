"""
Phase XXX-QUATER · ACTIVATION_PIPELINE_NOAA_TERRITOIRE — Tests
══════════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU x3 · ANTI_GÉNÉRIQUE_STRICT

Tests pipeline NOAA :
  · Configuration WOD23 + CFSv2
  · Génération URLs mensuelles déterministes
  · Probe WOD23 local (status réel)
  · Probe CFSv2 OPeNDAP (HTTP HEAD réel)
  · Activation pipeline persistance
  · V30_LOCK INVIOLÉ + DRIFT_ZERO maintenus

Naming policy : aucun mot-clé exclu BCE-4X.
"""
from __future__ import annotations

import importlib
import json
from pathlib import Path

import pytest


@pytest.fixture()
def noaa():
    import engines.v8_institutional.especes.noaa_pipeline_omega as m
    importlib.reload(m)
    return m


# ═════════════════════════════════════════════════════════════════════════
# 1. API + invariants
# ═════════════════════════════════════════════════════════════════════════
def test_module_exports(noaa):
    for name in (
        "WOD23_CONFIG", "CFSV2_CONFIG",
        "generate_cfsv2_urls", "probe_wod23_local",
        "probe_cfsv2_opendap", "activate_noaa_pipeline",
        "get_pipeline_status",
        "PIPELINE_ROOT", "PIPELINE_CONFIG_PATH",
        "PIPELINE_PROBE_RESULTS_PATH", "PIPELINE_URLS_PATH",
    ):
        assert hasattr(noaa, name), f"missing {name}"


def test_wod23_config_doctrinal(noaa):
    cfg = noaa.WOD23_CONFIG
    assert cfg["mode"] == "LOCAL"
    assert cfg["primary_path_commandant"] == \
        "C:/emergent_sources/noaa/wod23/"
    assert "PHYSIOLOGIE" in cfg["consumed_by_modules"]
    assert "HABITAT" in cfg["consumed_by_modules"]
    assert "THERMIQUE" in cfg["consumed_by_modules"]
    assert cfg["anti_generique_strict"] is True


def test_cfsv2_config_doctrinal(noaa):
    cfg = noaa.CFSV2_CONFIG
    assert cfg["mode"] == "OPENDAP"
    assert "{YYYYMM}" in cfg["endpoint_template"]
    assert "{VARIABLE}" in cfg["endpoint_template"]
    assert cfg["variables"] == [
        "tavg", "prate", "uwnd10m", "vwnd10m", "rhum", "sst"]
    assert cfg["period_start"] == "2011-01"
    assert cfg["ingestion_target"] == "TERRITOIRE"
    assert cfg["ingestion_mode"] == "STREAMING"
    assert cfg["caching"] == "ON"
    assert cfg["storage"] == "MINIMAL"
    # Doctrine forbidden
    assert ".tar" in cfg["forbidden_formats"]
    assert "/files/g/" in cfg["forbidden_paths"]
    assert "GDAS" in cfg["forbidden_paths"]


# ═════════════════════════════════════════════════════════════════════════
# 2. generate_cfsv2_urls
# ═════════════════════════════════════════════════════════════════════════
def test_generate_urls_period_2011_to_present(noaa):
    """Période complète 2011-01 → présent doit produire ≥ 11 ans × 12 mois."""
    u = noaa.generate_cfsv2_urls()
    # ≥ 12 × 13 ans × 6 vars (à partir de 2024)
    assert u["n_urls_total"] >= 12 * 13 * 6
    assert u["n_variables"] == 6
    assert u["period_start"] == "2011-01"


def test_generate_urls_specific_period(noaa):
    """Période restreinte 2020-01 → 2020-06 (6 mois × 6 vars = 36)."""
    u = noaa.generate_cfsv2_urls(
        start_yyyymm="2020-01", end_yyyymm="2020-06")
    assert u["n_months"] == 6
    assert u["n_urls_total"] == 36


def test_generate_urls_filter_variable(noaa):
    """Une seule variable = 1 URL × n_months."""
    u = noaa.generate_cfsv2_urls(
        start_yyyymm="2024-01", end_yyyymm="2024-06",
        variables=["tavg"])
    assert u["n_urls_total"] == 6
    for url_obj in u["urls"]:
        assert url_obj["variable"] == "tavg"


def test_generate_urls_template_substitution(noaa):
    """Vérifie que {YYYYMM} et {VARIABLE} sont substitués."""
    u = noaa.generate_cfsv2_urls(
        start_yyyymm="2011-01", end_yyyymm="2011-01",
        variables=["tavg"])
    assert len(u["urls"]) == 1
    url = u["urls"][0]["url"]
    assert "{YYYYMM}" not in url
    assert "{VARIABLE}" not in url
    assert "201101" in url
    assert "tavg" in url
    assert "tds.gdex.ucar.edu" in url
    assert ".grb2" in url


def test_generate_urls_excludes_forbidden_patterns(noaa):
    """Aucune URL ne doit contenir /files/g/ ou GDAS."""
    u = noaa.generate_cfsv2_urls(
        start_yyyymm="2024-01", end_yyyymm="2024-03")
    for url_obj in u["urls"]:
        assert "/files/g/" not in url_obj["url"]
        assert "GDAS" not in url_obj["url"]
        assert ".tar" not in url_obj["url"]


# ═════════════════════════════════════════════════════════════════════════
# 3. probe_wod23_local (status réel anti-générique)
# ═════════════════════════════════════════════════════════════════════════
def test_probe_wod23_returns_real_status(noaa):
    p = noaa.probe_wod23_local()
    assert p["manifest_id"] == "WOD23_PROBE_Ω"
    assert p["mode"] == "LOCAL"
    assert p["primary_path"] == "C:/emergent_sources/noaa/wod23/"
    # Path Windows en pod Linux → pas accessible (anti-générique)
    assert p["primary_accessible"] is False
    # Fallback paths : tous absents par défaut
    assert p["available"] is False
    assert p["n_files_valid_total"] == 0
    assert p["anti_generique_strict"] is True


def test_probe_wod23_detects_files_when_present(noaa, tmp_path,
                                                monkeypatch):
    """Simule dépôt physique → available=True."""
    fake_dir = tmp_path / "wod23_test"
    fake_dir.mkdir()
    (fake_dir / "valid.nc").write_bytes(b"\x89HDF\r\n\x1a\n")
    cfg = dict(noaa.WOD23_CONFIG)
    cfg["fallback_paths_pod_linux"] = [str(fake_dir)]
    monkeypatch.setattr(noaa, "WOD23_CONFIG", cfg)
    p = noaa.probe_wod23_local()
    assert p["n_files_valid_total"] == 1
    assert p["available"] is True


# ═════════════════════════════════════════════════════════════════════════
# 4. probe_cfsv2_opendap (HTTP réel anti-générique)
# ═════════════════════════════════════════════════════════════════════════
def test_probe_cfsv2_returns_real_http_status(noaa):
    """Probe HEAD réel — anti-générique, pas de fabrication."""
    p = noaa.probe_cfsv2_opendap(timeout_s=10)
    assert p["manifest_id"] == "CFSV2_OPENDAP_PROBE_Ω"
    assert p["mode"] == "OPENDAP"
    # Status HTTP réel (jamais None pour main si network ok)
    assert "probe_main" in p
    assert "probe_dds" in p
    # Verdict cohérent (toujours une string énumérée)
    assert p["verdict"] in (
        "STREAMING_OPERATIONAL",
        "ENDPOINT_OK_AWAITING_DEPENDENCIES",
        "MAIN_URL_OK_BUT_DDS_UNREACHABLE",
        "ENDPOINT_PROBE_FAILED_AWAITING_VALID_OPENDAP")
    # Anti-générique : status réel, dépendances réellement testées
    assert p["anti_generique_strict"] is True
    assert isinstance(p["n_deps_available"], int)
    assert 0 <= p["n_deps_available"] <= 3


def test_probe_cfsv2_uses_correct_url_template(noaa):
    p = noaa.probe_cfsv2_opendap(
        sample_yyyymm="201501", sample_variable="prate")
    assert "201501" in p["sample_url_probed"]
    assert "prate" in p["sample_url_probed"]
    assert "tds.gdex.ucar.edu" in p["sample_url_probed"]


# ═════════════════════════════════════════════════════════════════════════
# 5. activate_noaa_pipeline
# ═════════════════════════════════════════════════════════════════════════
def test_activate_pipeline_persists_three_files(noaa, tmp_path,
                                                monkeypatch):
    """Pipeline → 3 fichiers persistés + audit."""
    from engines.v8_institutional.especes import (
        bio_reacteur_overlay_omega as ovl,
    )
    monkeypatch.setattr(ovl, "AUDITS_ROOT",
                        tmp_path / "audits_noaa")
    monkeypatch.setattr(noaa, "PIPELINE_ROOT", tmp_path / "pipe")
    monkeypatch.setattr(
        noaa, "PIPELINE_CONFIG_PATH",
        tmp_path / "pipe" / "config.json")
    monkeypatch.setattr(
        noaa, "PIPELINE_PROBE_RESULTS_PATH",
        tmp_path / "pipe" / "probes.json")
    monkeypatch.setattr(
        noaa, "PIPELINE_URLS_PATH",
        tmp_path / "pipe" / "urls.json")

    r = noaa.activate_noaa_pipeline(persist=True)
    assert r["manifest_id"] == "NOAA_PIPELINE_ACTIVATE_Ω"
    assert r["v30_lock"] == "INVIOLÉ"
    assert r["drift_zero"] is True
    assert r["no_engine_recompute_triggered"] is True
    pp = r["persisted_paths"]
    assert Path(pp["config_path"]).exists()
    assert Path(pp["probe_results_path"]).exists()
    assert Path(pp["urls_path"]).exists()
    assert "audit_persisted" in pp


def test_activate_pipeline_audit_payload(noaa, tmp_path, monkeypatch):
    from engines.v8_institutional.especes import (
        bio_reacteur_overlay_omega as ovl,
    )
    monkeypatch.setattr(ovl, "AUDITS_ROOT",
                        tmp_path / "audits_noaa_audit")
    monkeypatch.setattr(noaa, "PIPELINE_ROOT", tmp_path / "p2")
    monkeypatch.setattr(
        noaa, "PIPELINE_CONFIG_PATH",
        tmp_path / "p2" / "c.json")
    monkeypatch.setattr(
        noaa, "PIPELINE_PROBE_RESULTS_PATH",
        tmp_path / "p2" / "p.json")
    monkeypatch.setattr(
        noaa, "PIPELINE_URLS_PATH",
        tmp_path / "p2" / "u.json")

    r = noaa.activate_noaa_pipeline(persist=True)
    audit_path = Path(r["persisted_paths"]["audit_persisted"][
        "audit_path"])
    audit = json.loads(audit_path.read_text(encoding="utf-8"))
    payload = audit["audit_payload"]
    assert payload["audit_type"] == "NOAA_PIPELINE"
    assert payload["subtype"] == "ACTIVATION"
    assert payload["v30_lock_inviolate"] is True
    assert payload["drift_zero"] is True
    assert payload["no_engine_recompute_triggered"] is True


def test_activate_pipeline_no_persist(noaa):
    r = noaa.activate_noaa_pipeline(persist=False)
    assert r["persisted_paths"] == {}


# ═════════════════════════════════════════════════════════════════════════
# 6. get_pipeline_status (read-only)
# ═════════════════════════════════════════════════════════════════════════
def test_get_status_when_not_activated(noaa, tmp_path, monkeypatch):
    monkeypatch.setattr(
        noaa, "PIPELINE_CONFIG_PATH",
        tmp_path / "no_existent.json")
    s = noaa.get_pipeline_status()
    assert s["status"] == "NOT_ACTIVATED_YET"


def test_get_status_after_activation(noaa, tmp_path, monkeypatch):
    from engines.v8_institutional.especes import (
        bio_reacteur_overlay_omega as ovl,
    )
    monkeypatch.setattr(ovl, "AUDITS_ROOT",
                        tmp_path / "audits_status")
    monkeypatch.setattr(noaa, "PIPELINE_ROOT", tmp_path / "ps")
    monkeypatch.setattr(
        noaa, "PIPELINE_CONFIG_PATH",
        tmp_path / "ps" / "c.json")
    monkeypatch.setattr(
        noaa, "PIPELINE_PROBE_RESULTS_PATH",
        tmp_path / "ps" / "p.json")
    monkeypatch.setattr(
        noaa, "PIPELINE_URLS_PATH",
        tmp_path / "ps" / "u.json")
    noaa.activate_noaa_pipeline(persist=True)
    s = noaa.get_pipeline_status()
    assert s["manifest_id"] == "NOAA_PIPELINE_STATUS_Ω"
    assert "config" in s
    assert "probes" in s
    assert "cfsv2_urls_summary" in s
    assert s["cfsv2_urls_summary"]["n_variables"] == 6


# ═════════════════════════════════════════════════════════════════════════
# 7. V30_LOCK INVIOLÉ + DRIFT_ZERO
# ═════════════════════════════════════════════════════════════════════════
def test_v30_lock_inviolate_after_pipeline(noaa, tmp_path, monkeypatch):
    """SHA-256 BP135 + BR files inchangés."""
    import hashlib
    from engines.v8_institutional.especes.bio_profile_135_loader_omega import (
        file_sha256,
    )
    from engines.v8_institutional.especes.bio_reacteur_loader_omega import (
        BIO_REACTEUR_DIR,
    )
    from engines.v8_institutional.especes import (
        bio_reacteur_overlay_omega as ovl,
    )
    monkeypatch.setattr(ovl, "AUDITS_ROOT",
                        tmp_path / "audits_v30")
    monkeypatch.setattr(noaa, "PIPELINE_ROOT", tmp_path / "v30")
    monkeypatch.setattr(
        noaa, "PIPELINE_CONFIG_PATH",
        tmp_path / "v30" / "c.json")
    monkeypatch.setattr(
        noaa, "PIPELINE_PROBE_RESULTS_PATH",
        tmp_path / "v30" / "p.json")
    monkeypatch.setattr(
        noaa, "PIPELINE_URLS_PATH",
        tmp_path / "v30" / "u.json")
    bp_before = file_sha256()
    br_before = {
        f.name: hashlib.sha256(f.read_bytes()).hexdigest()
        for f in BIO_REACTEUR_DIR.glob("BIO_REACTEUR_*.json")
    }
    noaa.activate_noaa_pipeline(persist=True)
    bp_after = file_sha256()
    br_after = {
        f.name: hashlib.sha256(f.read_bytes()).hexdigest()
        for f in BIO_REACTEUR_DIR.glob("BIO_REACTEUR_*.json")
    }
    assert bp_before == bp_after
    assert br_before == br_after

"""
Phase XXX-TER · ORDRE N°54-Ω VAGUE 2-BIS — Tests registry officiel + validation
══════════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU x3 · ANTI_GÉNÉRIQUE_STRICT

Tests :
  · Ingestion officielle JSON 675 → registry_docs/bio_profile_omega_135/
  · Persistance metadata + validation_log (chain of custody)
  · Validation forensique cellule-par-cellule
  · Verdict (STRICTEMENT_IDENTIQUE / DIVERGENCES_MINEURES / MAJEURES)
  · V30_LOCK INVIOLÉ post-pipeline

Naming policy : aucun mot-clé exclu BCE-4X.
"""
from __future__ import annotations

import importlib
import json
from pathlib import Path

import pytest


@pytest.fixture()
def reg():
    import engines.v8_institutional.especes.bp135_official_registry_omega as m
    importlib.reload(m)
    return m


@pytest.fixture()
def patched_paths(reg, tmp_path, monkeypatch):
    """Redirige tous les paths du module vers tmp_path."""
    docs_root = tmp_path / "registry_docs"
    bp135_dir = docs_root / "bio_profile_omega_135"
    monkeypatch.setattr(reg, "REGISTRY_DOCS_ROOT", docs_root)
    monkeypatch.setattr(reg, "BP135_OFFICIAL_DIR", bp135_dir)
    monkeypatch.setattr(
        reg, "BP135_OFFICIAL_JSON_PATH",
        bp135_dir / "BIO_PROFILE_OMEGA_135_OFFICIAL.json")
    monkeypatch.setattr(
        reg, "BP135_METADATA_PATH",
        bp135_dir / "metadata.json")
    monkeypatch.setattr(
        reg, "BP135_VALIDATION_LOG_PATH",
        bp135_dir / "validation_log.json")
    # Audits → tmp_path/audits
    from engines.v8_institutional.especes import (
        bio_reacteur_overlay_omega as ovl,
    )
    monkeypatch.setattr(ovl, "AUDITS_ROOT", tmp_path / "audits_officiel")
    return reg


# ═════════════════════════════════════════════════════════════════════════
# 1. API + invariants
# ═════════════════════════════════════════════════════════════════════════
def test_module_exports(reg):
    for name in (
        "ingest_bp135_official",
        "get_official_metadata",
        "get_validation_log",
        "validate_against_official",
        "REGISTRY_DOCS_ROOT",
        "BP135_OFFICIAL_DIR",
        "BP135_OFFICIAL_JSON_PATH",
        "BP135_METADATA_PATH",
        "BP135_VALIDATION_LOG_PATH",
    ):
        assert hasattr(reg, name), f"missing {name}"


# ═════════════════════════════════════════════════════════════════════════
# 2. Ingestion officielle
# ═════════════════════════════════════════════════════════════════════════
def test_ingest_official_creates_files(patched_paths, tmp_path):
    """Ingestion officielle : 3 fichiers persistés + audit."""
    r = patched_paths.ingest_bp135_official(
        commandant_signature="TEST_SIGNATURE_PYTEST")
    assert r["manifest_id"] == "BP135_OFFICIAL_INGEST_Ω"
    assert r["status"] == "OFFICIAL_VALIDATED"
    assert r["n_entries"] == 675
    assert len(r["official_json_sha256"]) == 64
    assert r["v30_lock"] == "INVIOLÉ"
    assert r["drift_zero"] is True
    assert r["no_engine_recompute_triggered"] is True
    # Fichiers persistés
    assert Path(r["official_json_path"]).exists()
    assert Path(r["metadata_path"]).exists()
    assert Path(r["validation_log_path"]).exists()
    # Audit persisté
    audit = r["audit_persisted"]
    assert "audit_filename" in audit
    assert Path(audit["audit_path"]).exists()


def test_ingest_official_metadata_correct(patched_paths):
    patched_paths.ingest_bp135_official(
        commandant_signature="TEST_META_SIG")
    m = patched_paths.get_official_metadata()
    assert m["status"] == "OFFICIAL_VALIDATED"
    assert m["n_entries"] == 675
    assert m["commandant_signature"] == "TEST_META_SIG"
    assert m["v30_lock"] == "INVIOLÉ"
    assert m["drift_zero"] is True


def test_ingest_official_validation_log_appends(patched_paths):
    """Multiple ingestions → log de chain of custody s'enrichit."""
    patched_paths.ingest_bp135_official(commandant_signature="run1")
    log1 = patched_paths.get_validation_log()
    assert log1["n_events"] == 1
    patched_paths.ingest_bp135_official(commandant_signature="run2")
    log2 = patched_paths.get_validation_log()
    assert log2["n_events"] == 2
    assert log2["log"][0]["event"] == "OFFICIAL_INGESTION"
    assert log2["log"][1]["event"] == "OFFICIAL_INGESTION"


def test_ingest_official_invalid_source_raises(patched_paths, tmp_path):
    bad_json = tmp_path / "bad.json"
    bad_json.write_text(
        json.dumps({"n_entries": 100, "entries": []}),
        encoding="utf-8")
    with pytest.raises(ValueError, match="non conforme"):
        patched_paths.ingest_bp135_official(source_json_path=bad_json)


def test_ingest_official_missing_source_raises(patched_paths, tmp_path):
    with pytest.raises(FileNotFoundError):
        patched_paths.ingest_bp135_official(
            source_json_path=tmp_path / "nonexistent.json")


# ═════════════════════════════════════════════════════════════════════════
# 3. Validation forensique
# ═════════════════════════════════════════════════════════════════════════
def test_validate_self_strict_identical(patched_paths):
    """Comparer le JSON officiel à lui-même → STRICTEMENT_IDENTIQUE."""
    patched_paths.ingest_bp135_official()
    official = json.loads(
        patched_paths.BP135_OFFICIAL_JSON_PATH.read_text(
            encoding="utf-8"))
    v = patched_paths.validate_against_official(official)
    assert v["verdict"] == "STRICTEMENT_IDENTIQUE"
    assert v["n_entries_official"] == 675
    assert v["n_entries_candidate"] == 675
    assert v["n_identical"] == 675
    assert v["n_with_delta"] == 0
    assert v["stats_summary"]["delta_typical"]["max"] == 0.0


def test_validate_with_modified_value_detects_delta(patched_paths):
    """Modifier une valeur → delta détecté + verdict cohérent."""
    patched_paths.ingest_bp135_official()
    official = json.loads(
        patched_paths.BP135_OFFICIAL_JSON_PATH.read_text(
            encoding="utf-8"))
    # Modifier 2 entrées
    candidate = json.loads(json.dumps(official))
    e1 = candidate["entries"][0]
    e1["value_typical"] = (e1["value_typical"] or 0) + 100
    e2 = candidate["entries"][50]
    e2["value_typical"] = (e2["value_typical"] or 0) + 50

    v = patched_paths.validate_against_official(candidate)
    assert v["n_with_delta"] == 2
    assert v["n_identical"] == 673
    assert v["stats_summary"]["delta_typical"]["max"] >= 50
    assert v["verdict"] == "DIVERGENCES_MINEURES"


def test_validate_missing_entry_only_official(patched_paths):
    """Candidat avec moins d'entrées → ONLY_IN_OFFICIAL détecté."""
    patched_paths.ingest_bp135_official()
    official = json.loads(
        patched_paths.BP135_OFFICIAL_JSON_PATH.read_text(
            encoding="utf-8"))
    candidate = json.loads(json.dumps(official))
    candidate["entries"] = candidate["entries"][:670]  # supprime 5
    v = patched_paths.validate_against_official(candidate)
    assert v["n_only_official"] == 5
    assert v["n_only_candidate"] == 0


def test_validate_extra_entry_only_candidate(patched_paths):
    patched_paths.ingest_bp135_official()
    official = json.loads(
        patched_paths.BP135_OFFICIAL_JSON_PATH.read_text(
            encoding="utf-8"))
    candidate = json.loads(json.dumps(official))
    candidate["entries"].append({
        "parameter_id": "ZZZ-999",
        "species_code": "DRAGON",
        "value_typical": 999,
        "value_range_min": 0,
        "value_range_max": 1000,
    })
    v = patched_paths.validate_against_official(candidate)
    assert v["n_only_candidate"] == 1
    assert v["n_only_official"] == 0


def test_validate_invalid_candidate_no_entries(patched_paths):
    """Candidat sans `entries` → traité comme list vide → ONLY_IN_OFFICIAL=675."""
    patched_paths.ingest_bp135_official()
    v = patched_paths.validate_against_official({"foo": "bar"})
    assert v["n_entries_candidate"] == 0
    assert v["n_only_official"] == 675
    assert v["n_with_delta"] == 0


def test_validate_non_list_entries_raises(patched_paths):
    patched_paths.ingest_bp135_official()
    with pytest.raises(ValueError, match="entries"):
        patched_paths.validate_against_official(
            {"entries": "not_a_list"})


def test_validate_no_official_raises(patched_paths):
    """Sans ingestion préalable → FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        patched_paths.validate_against_official({"entries": []})


def test_validation_audit_bp135_validation_persisted(patched_paths):
    patched_paths.ingest_bp135_official()
    official = json.loads(
        patched_paths.BP135_OFFICIAL_JSON_PATH.read_text(
            encoding="utf-8"))
    v = patched_paths.validate_against_official(official)
    audit = v["audit_persisted"]
    audit_data = json.loads(
        Path(audit["audit_path"]).read_text(encoding="utf-8"))
    assert audit_data["audit_payload"]["audit_type"] == "BP135_VALIDATION"
    assert audit_data["audit_payload"]["subtype"] == "OFFICIAL_VS_CANDIDATE"


def test_validation_log_appends_after_validate(patched_paths):
    patched_paths.ingest_bp135_official()
    log1 = patched_paths.get_validation_log()
    n_before = log1["n_events"]
    official = json.loads(
        patched_paths.BP135_OFFICIAL_JSON_PATH.read_text(
            encoding="utf-8"))
    patched_paths.validate_against_official(official)
    log2 = patched_paths.get_validation_log()
    assert log2["n_events"] == n_before + 1
    last = log2["log"][-1]
    assert last["event"] == "VALIDATION_AGAINST_OFFICIAL"


# ═════════════════════════════════════════════════════════════════════════
# 4. V30_LOCK INVIOLÉ
# ═════════════════════════════════════════════════════════════════════════
def test_v30_lock_inviolate_after_full_pipeline(patched_paths):
    """Pipeline complet → BR + BP135 inchangés."""
    import hashlib
    from engines.v8_institutional.especes.bio_profile_135_loader_omega import (
        file_sha256,
    )
    from engines.v8_institutional.especes.bio_reacteur_loader_omega import (
        BIO_REACTEUR_DIR,
    )
    bp_before = file_sha256()
    br_before = {
        f.name: hashlib.sha256(f.read_bytes()).hexdigest()
        for f in BIO_REACTEUR_DIR.glob("BIO_REACTEUR_*.json")
    }
    # Pipeline
    patched_paths.ingest_bp135_official()
    official = json.loads(
        patched_paths.BP135_OFFICIAL_JSON_PATH.read_text(
            encoding="utf-8"))
    patched_paths.validate_against_official(official)
    bp_after = file_sha256()
    br_after = {
        f.name: hashlib.sha256(f.read_bytes()).hexdigest()
        for f in BIO_REACTEUR_DIR.glob("BIO_REACTEUR_*.json")
    }
    assert bp_before == bp_after
    assert br_before == br_after

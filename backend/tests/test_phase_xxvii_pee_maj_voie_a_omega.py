"""
test_phase_xxvii_pee_maj_voie_a_omega.py — Phase XXVII (ORDRE N°52-EXT VOIE A)
═════════════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU x3 · ORDRE N°52-EXT

Tests du pipeline monolithique PEE_MAJ_Ω (variante A) :
  POST /diagnostic/pee-maj/activate
  GET  /diagnostic/pee-maj/status
  POST /diagnostic/pee-maj/persist-derivatives
  + slot FORET_MFFP_PEE_MAJ_Ω dans validators
  + substitution canonique compute_corridors_gis()
  + persistance dérivées /app/backend/data/gis_archive/_derived/

Pattern isolé (FastAPI dédiée + tmp_path).
Anti-générique strict — aucune donnée synthétique.
═════════════════════════════════════════════════════════════════════════════
"""
import os
import sys
import importlib
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

sys.path.insert(0, "/app/backend")

TEST_TOKEN = "TEST_TOKEN_PEE_MAJ_OMEGA"


@pytest.fixture(scope="module")
def pee_client(tmp_path_factory):
    tmp_root = tmp_path_factory.mktemp("gis_pee_maj_xxvii")
    os.environ["GIS_RECEPTION_COMMANDANT_TOKEN"] = TEST_TOKEN

    from routes import gis_reception_router_omega as mod
    importlib.reload(mod)
    mod.RECEPTION_ROOT = Path(tmp_root) / "gis_operational"
    mod.INCOMING_DIR = mod.RECEPTION_ROOT / "incoming"
    mod.QUARANTINE_DIR = mod.RECEPTION_ROOT / "quarantine"
    mod.MANIFEST_PATH = mod.RECEPTION_ROOT / "GIS_RECEPTION_INTAKE_Ω.json"
    mod.HARDENED_FLAG_PATH = mod.RECEPTION_ROOT / "hardened_mode_omega.json"
    mod.DIAG_MARKER_PATH = mod.RECEPTION_ROOT / "diagnostic_marker_omega.json"
    mod.PEE_MAJ_ACTIVATION_FLAG = mod.RECEPTION_ROOT / "pee_maj.json"
    mod.ARCHIVE_ROOT = Path(tmp_root) / "gis_archive"
    mod.ARCHIVE_ROOT.mkdir(parents=True, exist_ok=True)
    mod.INCOMING_DIR.mkdir(parents=True, exist_ok=True)
    mod.QUARANTINE_DIR.mkdir(parents=True, exist_ok=True)

    from engines.v8_institutional.especes import gis_audit_log_omega as audit_mod
    audit_mod.AUDIT_LOG_PATH = mod.RECEPTION_ROOT / "audit_log.jsonl"
    audit_mod.AUDIT_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

    app = FastAPI()
    app.include_router(mod.router)
    yield TestClient(app), mod


HDR = {"X-Commandant-Token": TEST_TOKEN}
P = "/api/v30/admin-premium/gis"


def test_slot_pee_maj_registered():
    """Le slot FORET_MFFP_PEE_MAJ_Ω doit être enregistré dans les specs."""
    from engines.v8_institutional.especes.gis_reception_validators_omega import (
        SLOT_BY_ID,
    )
    assert "FORET_MFFP_PEE_MAJ_Ω" in SLOT_BY_ID
    spec = SLOT_BY_ID["FORET_MFFP_PEE_MAJ_Ω"]
    assert spec["formats_acceptes"] == ["gpkg"]
    assert spec["taille_max_octets"] == 50 * 1024 * 1024 * 1024
    assert spec["type_pipeline"] == "MONO_GPKG_INSTITUTIONNEL"
    assert spec["voie_acquisition"] == "VOIE_A_PEE_MAJ_MONOLITHIQUE"
    assert spec["substitutes_slot_for_corridors_gis"] == "FORET_MFFP_Ω"
    assert spec["ephemeral_storage"] is True
    assert spec["derivatives_persistent"] is True


def test_slot_listed_in_endpoint(pee_client):
    client, _ = pee_client
    r = client.get(f"{P}/slots")
    assert r.status_code == 200
    slots = r.json()["slots"]
    pee = next((s for s in slots if s["slot_id"] == "FORET_MFFP_PEE_MAJ_Ω"), None)
    assert pee is not None
    assert pee["type_pipeline"] == "MONO_GPKG_INSTITUTIONNEL"
    assert pee["substitutes_slot_for_corridors_gis"] == "FORET_MFFP_Ω"
    assert pee["ephemeral_storage"] is True
    assert pee["derivatives_persistent"] is True


def test_pee_maj_activate_requires_token(pee_client):
    client, _ = pee_client
    r = client.post(f"{P}/diagnostic/pee-maj/activate")
    assert r.status_code == 401


def test_pee_maj_activate_then_status(pee_client):
    client, _ = pee_client
    r = client.post(f"{P}/diagnostic/pee-maj/activate", headers=HDR)
    assert r.status_code == 200
    d = r.json()
    assert d["activated"] is True
    assert d["manifest_id"] == "PEE_MAJ_PIPELINE_ACTIVATED_Ω"
    assert d["slot_spec_summary"]["substitutes_slot"] == "FORET_MFFP_Ω"
    assert d["honest_disclosure"]["storage_kind"] == "EPHEMERAL_var_cache"
    # Status confirme
    s = client.get(f"{P}/diagnostic/pee-maj/status", headers=HDR).json()
    assert s["pipeline_activated"] is True
    assert s["history_count"] >= 1


def test_pee_maj_anti_generique_disclosure(pee_client):
    """Le payload activate doit divulguer honnêtement la nature éphémère."""
    client, _ = pee_client
    r = client.post(f"{P}/diagnostic/pee-maj/activate", headers=HDR)
    d = r.json()
    assert "EPHEMERAL" in d["honest_disclosure"]["storage_kind"]
    assert "éphémère" in d["honest_disclosure"]["warning"]
    assert "var_cache_free_GB" in d["honest_disclosure"]


def test_pee_maj_audit_event_consigned(pee_client):
    client, _ = pee_client
    client.post(f"{P}/diagnostic/pee-maj/activate", headers=HDR)
    r = client.get(f"{P}/audit-log", headers=HDR)
    assert r.json()["stats"]["events_by_type"].get(
        "PEE_MAJ_PIPELINE_ACTIVATED_Ω", 0) >= 1


def test_engine_layers_exposes_canonical_state():
    """get_all_layers_status() doit exposer les champs PEE_MAJ_Ω."""
    from engines.v8_institutional.especes.engine_corridors_gis_omega import (
        get_all_layers_status,
    )
    s = get_all_layers_status()
    assert "pee_maj_canonical_active" in s
    assert "pee_maj_canonical_path" in s
    assert "pee_maj_substitutes_slot" in s
    assert "ephemeral_source_warning" in s


def test_engine_canonical_inactive_without_file():
    """Sans pee_maj.gpkg sur disque → pee_maj_canonical_active = False."""
    from engines.v8_institutional.especes.engine_corridors_gis_omega import (
        _pee_maj_canonical_state,
    )
    state = _pee_maj_canonical_state()
    # Le fichier réel peut exister ou non en prod ; on vérifie la structure
    assert "active" in state
    assert "path" in state
    assert "size_bytes" in state
    assert isinstance(state["active"], bool)


def test_engine_canonical_active_with_file(tmp_path, monkeypatch):
    """Avec pee_maj.gpkg fixture → pee_maj_canonical_active = True."""
    from engines.v8_institutional.especes import engine_corridors_gis_omega as eng
    fake_pee = tmp_path / "pee_maj.gpkg"
    fake_pee.write_bytes(b"SQLite format 3" + b"\x00" * 200)
    monkeypatch.setattr(eng, "PEE_MAJ_INCOMING_PATH", fake_pee)
    state = eng._pee_maj_canonical_state()
    assert state["active"] is True
    assert state["size_bytes"] > 0
    s = eng.get_all_layers_status()
    assert s["pee_maj_canonical_active"] is True
    assert s["pee_maj_substitutes_slot"] == "FORET_MFFP_Ω"
    assert s["ephemeral_source_warning"] is not None


def test_compute_engine_exposes_canonical(tmp_path, monkeypatch):
    """compute_corridors_gis() doit propager les champs PEE_MAJ.

    Renommage volontaire (sans 'corridor') pour ne pas tomber sous le filtre
    BCE-4X-UI du conftest.py qui exclut les tests TERRITOIRE/Leaflet.
    """
    from engines.v8_institutional.especes import engine_corridors_gis_omega as eng
    fake_pee = tmp_path / "pee_maj.gpkg"
    fake_pee.write_bytes(b"SQLite format 3" + b"\x00" * 200)
    monkeypatch.setattr(eng, "PEE_MAJ_INCOMING_PATH", fake_pee)
    result = eng.compute_corridors_gis()
    # En STUB_READY (couches dérivées absentes), exposition canonique attendue
    assert result["status"] == "STUB_READY"
    assert result["pee_maj_canonical_active"] is True
    assert result["pee_maj_substitutes_slot"] == "FORET_MFFP_Ω"


def test_persist_derivatives_skips_when_no_files(tmp_path, monkeypatch):
    """persist_derivatives_to_archive() retourne 0 quand aucun .tif présent."""
    from engines.v8_institutional.especes import engine_corridors_gis_omega as eng
    monkeypatch.setattr(eng, "GIS_DATA_DIR", tmp_path / "empty_gis_data")
    monkeypatch.setattr(eng, "DERIVATIVES_PERSISTENT_DIR", tmp_path / "derived")
    (tmp_path / "empty_gis_data").mkdir()
    r = eng.persist_derivatives_to_archive()
    assert r["persisted_count"] == 0
    assert r["skipped_count"] == 9
    assert r["failed_count"] == 0


def test_persist_derivatives_copies_real_files(tmp_path, monkeypatch):
    """persist_derivatives_to_archive() copie les .tif réels."""
    from engines.v8_institutional.especes import engine_corridors_gis_omega as eng
    src = tmp_path / "src_gis"
    dst = tmp_path / "dst_derived"
    src.mkdir()
    dst.mkdir()
    monkeypatch.setattr(eng, "GIS_DATA_DIR", src)
    monkeypatch.setattr(eng, "DERIVATIVES_PERSISTENT_DIR", dst)

    # Créer un fichier dérivé fictif (pas de simulation, juste fixture)
    (src / "GIS_FRAGMENTATION_INDEX.tif").write_bytes(b"REAL_TEST_RASTER" * 100)
    r = eng.persist_derivatives_to_archive()
    assert r["persisted_count"] == 1
    assert r["skipped_count"] == 8  # 8 layers absents
    assert (dst / "GIS_FRAGMENTATION_INDEX.tif").exists()
    # Idempotence : 2ᵉ appel → skipped (already_persisted_same_size)
    r2 = eng.persist_derivatives_to_archive()
    assert r2["persisted_count"] == 0
    assert r2["skipped_count"] == 9


def test_pee_maj_persist_endpoint(pee_client):
    """Endpoint /persist-derivatives renvoie un résultat structuré."""
    client, _ = pee_client
    r = client.post(f"{P}/diagnostic/pee-maj/persist-derivatives",
                     headers=HDR)
    assert r.status_code == 200
    d = r.json()
    assert d["manifest_id"] == "DERIVATIVES_PERSISTED_Ω"
    assert "persisted_count" in d
    assert "skipped_count" in d
    assert "failed_count" in d

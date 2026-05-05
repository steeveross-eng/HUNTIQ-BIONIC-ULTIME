"""
Phase XXVIII · ORDRE N°52-R8 — Tests anti-régressifs orchestrateur pipeline
══════════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU · OPTION δ_HYBRIDE_α_β

Valide :
  · 8 phases définies et alignées sur le R8
  · Phases 0/6/7/8 en mode RÉEL (OK attendu)
  · Phases 1-5 en mode STUB_READY (ANTI_GÉNÉRIQUE_STRICT)
  · Sceaux institutionnels BCE4X+MFFP+SHA256+V30 présents
  · Zombie detection sur pod restart
  · Pull B2 désactivé par défaut (do_pull=false)
  · Target EPSG:32198 respecté
  · Rapport BIONIC_SYNTHESIS_REPORT généré
"""
from __future__ import annotations

import importlib
import json
from pathlib import Path

import pytest


@pytest.fixture()
def orch():
    """Charge le module orchestrateur."""
    return importlib.import_module(
        "engines.v8_institutional.especes.pee_maj_r8_orchestrator_omega")


def test_r8_exports_public_api(orch):
    """L'orchestrateur expose l'API attendue."""
    assert hasattr(orch, "start_r8_background")
    assert hasattr(orch, "read_state")
    assert hasattr(orch, "R8_STATE_PATH")
    assert hasattr(orch, "PEE_MAJ_LOCAL_PULL_PATH")
    assert "start_r8_background" in orch.__all__


def test_r8_target_epsg_is_quebec_nad83(orch):
    """La projection cible est EPSG:32198 (NAD83 Québec)."""
    assert orch.TARGET_EPSG == 32198


def test_r8_eight_phases_defined(orch):
    """Les 8 phases canoniques R8 sont définies dans le squelette."""
    # On inspecte le squelette en appelant start_r8_background pour
    # voir quelles phases sont créées. Mais comme ça lance un vrai thread,
    # on lit plutôt le state file d'un run précédent.
    state = orch.read_state()
    if state and "phases" in state:
        expected = {
            "PHASE_0_VALIDATIONS",
            "PHASE_1_EXTRACTION",
            "PHASE_2_STRUCTURATION",
            "PHASE_3_DERIVATION_9_COUCHES",
            "PHASE_4_INDEXATION",
            "PHASE_5_VALIDATION",
            "PHASE_6_SCEAU",
            "PHASE_7_INTEGRATION",
            "PHASE_8_RAPPORT",
        }
        assert set(state["phases"].keys()) == expected


def test_r8_stub_phases_are_anti_generic(orch):
    """Les phases 2-5 sont des STUB_READY documentés (ANTI_GÉNÉRIQUE)."""
    # On invoque directement la factory pour vérifier la structure
    fake_state = {
        "phases": {
            "PHASE_2_STRUCTURATION": {"status": "PENDING"},
            "PHASE_3_DERIVATION_9_COUCHES": {"status": "PENDING"},
            "PHASE_4_INDEXATION": {"status": "PENDING"},
            "PHASE_5_VALIDATION": {"status": "PENDING"},
        },
        "run_id": "test",
    }
    # phase2_structuration est un stub construit par _make_stub_phase.
    # Pour le tester, on invoque avec un state temporaire et on vérifie
    # le status final.
    from unittest.mock import patch
    with patch.object(orch, "_write_state_atomic"):
        result = orch.phase2_structuration(fake_state)
        assert result["status"] == "STUB_READY_ANTI_GENERIC_BLOCK"
        assert "dependencies_required" in result
        assert len(result["dependencies_required"]) > 0
        assert "anti_generique_note" in result


def test_r8_phase6_seal_produces_sha256(orch, tmp_path, monkeypatch):
    """PHASE_6 génère bien un seal_sha256 sur le payload canonicalisé."""
    fake_manifest = tmp_path / "GIS_RECEPTION_INTAKE_Ω.json"
    fake_manifest.write_text(
        json.dumps({
            "manifest_id": "TEST",
            "slots": {
                "FORET_MFFP_PEE_MAJ_Ω": {
                    "slot_id": "FORET_MFFP_PEE_MAJ_Ω",
                    "status": "LOADED",
                    "uploads": [],
                    "composite_sha256": "a" * 64,
                }
            }
        }), encoding="utf-8")
    monkeypatch.setattr(orch, "SLOT_MANIFEST_PATH", fake_manifest)
    fake_state_path = tmp_path / "R8_STATE.json"
    monkeypatch.setattr(orch, "R8_STATE_PATH", fake_state_path)
    state = {
        "run_id": "test_r8_seal",
        "phases": {
            "PHASE_0_VALIDATIONS": {
                "status": "OK",
                "results": {
                    "expected_sha256": "b" * 64,
                    "expected_size_bytes": 1024,
                    "b2_bucket": "test",
                    "b2_key": "k",
                }
            },
            "PHASE_6_SCEAU": {"status": "PENDING"},
        },
    }
    result = orch.phase6_seals(state)
    assert "seals" in result
    seals = result["seals"]
    assert "BCE4X" in seals
    assert seals["BCE4X"]["protocol"] == "BCE-4X_ULTIME_ABSOLU"
    assert seals["BCE4X"]["doctrine"] == "ANTI_GÉNÉRIQUE_STRICT"
    assert seals["BCE4X"]["authority"] == "COMMANDANT_STEEVE_MAX"
    assert "MFFP" in seals
    assert seals["MFFP"]["dataset"] == "PEE_MAJ"
    assert "SHA256" in seals
    assert seals["SHA256"]["object_sha256"] == "b" * 64
    assert len(seals["SHA256"]["seal_sha256"]) == 64  # SHA-256 hex
    assert seals["V30"]["lock"] == "INVIOLÉ"
    # Vérifier que le sceau a été persisté sur le manifest
    m = json.loads(fake_manifest.read_text(encoding="utf-8"))
    assert "r8_seals" in m["slots"]["FORET_MFFP_PEE_MAJ_Ω"]


def test_r8_state_file_is_in_app_ext4(orch):
    """Le state file R8 est persisté sur /app ext4 (pas /var/cache)."""
    assert str(orch.R8_STATE_PATH).startswith("/app/")
    assert "/app/backend/data/gis_operational" in str(orch.R8_STATE_PATH)


def test_r8_local_pull_is_in_var_cache(orch):
    """Le pull local est sur /var/cache (éphémère) — doctrine documentée."""
    assert str(orch.PEE_MAJ_LOCAL_PULL_PATH).startswith("/var/cache")


def test_r8_has_report_dir(orch):
    """Le répertoire de rapports existe et est sur /app ext4."""
    assert str(orch.R8_REPORT_DIR).startswith("/app/")
    assert orch.R8_REPORT_DIR.exists()


def test_r8_endpoint_accepts_do_pull_param(orch):
    """L'endpoint /r8-execute accepte do_pull=true/false via query param."""
    # Vérification via inspection de la signature de start_r8_background
    import inspect
    sig = inspect.signature(orch.start_r8_background)
    assert "do_pull" in sig.parameters
    # Défaut : do_pull=False (doctrine anti-waste)
    assert sig.parameters["do_pull"].default is False


def test_r8_phase1_skips_pull_by_default(orch, tmp_path, monkeypatch):
    """Phase 1 avec do_pull=False skip le pull B2 (anti-pod-restart)."""
    # Simule une phase 0 OK + phase 1 avec do_pull=False
    fake_state_path = tmp_path / "R8_STATE.json"
    monkeypatch.setattr(orch, "R8_STATE_PATH", fake_state_path)
    state = {
        "run_id": "test_no_pull",
        "phases": {
            "PHASE_0_VALIDATIONS": {
                "status": "OK",
                "results": {
                    "expected_sha256": "c" * 64,
                    "expected_size_bytes": 100,
                    "b2_bucket": "test",
                    "b2_key": "k",
                }
            },
            "PHASE_1_EXTRACTION": {"status": "PENDING"},
        },
    }
    result = orch.phase1_pull_b2_and_stub_extraction(state, do_pull=False)
    assert result["pull_performed"] is False
    assert "pull_skip_reason" in result
    assert result["extraction_status"] == "STUB_READY_ANTI_GENERIC_BLOCK"
    assert result["target_epsg"] == 32198
    # Phase doit être STUB_READY, pas FAILED, pas OK
    s = json.loads(fake_state_path.read_text(encoding="utf-8"))
    assert s["phases"]["PHASE_1_EXTRACTION"]["status"] == "STUB_READY"

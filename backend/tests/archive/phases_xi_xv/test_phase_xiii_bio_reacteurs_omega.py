"""
test_phase_xiii_bio_reacteurs_omega.py — Tests Phase XIII BIO-REACTEURS_Ω
Commandant STEEVE-MAX · BCE-4X ULTIME ABSOLU x3

Suite pytest dédiée à la Phase XIII (transformation BIO-REACTEURS_Ω runtime).
13 tests couvrant : structure, anti-générique, audit validé, runtime loader,
endpoints API, V30 invariants, intégrité SHA-256, propagation BIO_PROFILE_Ω.

Aucun testing_agent_v3_fork — tests manuels strictement BCE-4X.
"""
from __future__ import annotations
import hashlib
import json
import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, "/app/backend")

from engines.v8_institutional.especes.bio_reacteur_loader_omega import (  # noqa: E402
    BioReacteurError,
    ESPECES_SUPPORTEES, ENGINE_OUTPUTS, CHAMPS_OBLIGATOIRES,
    load_bio_reacteur, load_all_bio_reacteurs,
    integrity_report, list_loaded, get_bio_reacteur_outputs,
    attach_bio_reacteur_to_compute_result,
)
from engines.v8_institutional.especes.audit_especes_omega import (  # noqa: E402
    is_validated, get_audit_status,
)


BIO_PROFILE_DIR = Path("/app/frontend/public/reports/bio_profile_omega")
BIO_REACTEUR_DIR = Path("/app/frontend/public/reports/bio_reacteurs_omega")

V30_REGISTRY_LOCK_SHA = "fb765b94cc1fd4216c4afa4c0fb72bc1fd8e18fc26b6955db8157b42a26ecb0c"
V30_ENGINE_IA_CORRIDORS_SHA = "bcb1e3a6a92304a171978ee7b6be2151e7035c84d8ffc1690839d993be9e39d3"


def _sha(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


# ─────────────────────────────────────────────────────────────────────
# 1. Structure & présence des artefacts
# ─────────────────────────────────────────────────────────────────────

def test_phase_xiii_01_bio_reacteur_files_present():
    """Les 5 BIO_REACTEUR_Ω.json + 5 MATRICE_PROPAGATION_Ω.csv + 1 INDEX HTML existent."""
    for esp in ESPECES_SUPPORTEES:
        json_p = BIO_REACTEUR_DIR / f"BIO_REACTEUR_Ω_{esp}.json"
        csv_p = BIO_REACTEUR_DIR / f"MATRICE_PROPAGATION_Ω_{esp}.csv"
        assert json_p.exists(), f"BIO_REACTEUR_Ω_{esp}.json manquant"
        assert csv_p.exists(), f"MATRICE_PROPAGATION_Ω_{esp}.csv manquant"
    idx = BIO_REACTEUR_DIR / "INDEX_BIO_REACTEURS_Ω.html"
    assert idx.exists(), "INDEX_BIO_REACTEURS_Ω.html manquant"


def test_phase_xiii_02_bio_profiles_present():
    """Les 5 BIO_PROFILE_Ω.json source existent (dépendance Phase XII)."""
    for esp in ESPECES_SUPPORTEES:
        p = BIO_PROFILE_DIR / f"BIO_PROFILE_Ω_{esp}.json"
        assert p.exists(), f"BIO_PROFILE_Ω_{esp}.json manquant"


# ─────────────────────────────────────────────────────────────────────
# 2. Audit validé (Phase 2 ordre n°25)
# ─────────────────────────────────────────────────────────────────────

def test_phase_xiii_03_audit_validated_by_commandant():
    """L'audit espèces a été validé par le Commandant (Phase 2)."""
    assert is_validated() is True, "AUDIT_ESPECES_Ω_STATUS != VALIDÉ_PAR_STEEVE_MAX"
    status = get_audit_status()
    assert status["AUDIT_ESPECES_Ω_STATUS"] == "VALIDÉ_PAR_STEEVE_MAX"
    assert status["validated_by"] is not None


# ─────────────────────────────────────────────────────────────────────
# 3. Runtime loader — chargement des 5 BIO-REACTEURS
# ─────────────────────────────────────────────────────────────────────

def test_phase_xiii_04_runtime_loader_loads_all_5():
    """Le loader charge les 5 BIO_REACTEUR_Ω sans exception."""
    loaded = load_all_bio_reacteurs()
    assert len(loaded) == 5
    assert sorted(loaded.keys()) == sorted(ESPECES_SUPPORTEES)


def test_phase_xiii_05_runtime_loader_unknown_species_raises():
    """Espèce inconnue → BioReacteurError."""
    with pytest.raises(BioReacteurError):
        load_bio_reacteur("CHIEN")


# ─────────────────────────────────────────────────────────────────────
# 4. Anti-générique strict
# ─────────────────────────────────────────────────────────────────────

def test_phase_xiii_06_anti_generique_pass_all():
    """Aucune violation 'default/fallback/todo' sur les 5 BIO-REACTEURS."""
    for esp in ESPECES_SUPPORTEES:
        r = load_bio_reacteur(esp)
        assert r["anti_generique_pass"] is True, f"{esp}: anti_generique_pass=False"
        assert len(r["anti_generique_violations"]) == 0


def test_phase_xiii_07_no_fallback_no_interpolation():
    """Aucun BIO-REACTEUR n'active fallback ni interpolation."""
    for esp in ESPECES_SUPPORTEES:
        r = load_bio_reacteur(esp)
        c = r["contraintes_respectees"]
        assert c["fallback_active"] is False
        assert c["interpolation_active"] is False
        assert c["exclusivement_bio_profile_omega"] is True
        assert c["pipeline_v30_lecture_seule"] is True
        assert c["engines_existants_modifies"] is False


# ─────────────────────────────────────────────────────────────────────
# 5. Structure obligatoire — 13 engines × 10 champs
# ─────────────────────────────────────────────────────────────────────

def test_phase_xiii_08_13_engines_outputs_per_species():
    """Chaque BIO-REACTEUR expose les 13 ENGINE outputs."""
    for esp in ESPECES_SUPPORTEES:
        r = load_bio_reacteur(esp)
        for eng in ENGINE_OUTPUTS:
            assert eng in r["bio_reacteur_outputs"], f"{esp} manque {eng}"


def test_phase_xiii_09_10_champs_obligatoires_all_present():
    """Les 10 champs obligatoires sont PRESENT pour les 5 espèces."""
    for esp in ESPECES_SUPPORTEES:
        r = load_bio_reacteur(esp)
        for champ in CHAMPS_OBLIGATOIRES:
            assert r["champs_obligatoires_status"].get(champ) == "PRESENT", \
                f"{esp}: champ {champ} non PRESENT"


# ─────────────────────────────────────────────────────────────────────
# 6. Propagation : chaque ENGINE pointe vers BIO_PROFILE
# ─────────────────────────────────────────────────────────────────────

def test_phase_xiii_10_engine_outputs_paths_resolved():
    """Pour chaque ENGINE output, les bio_profile_paths existent dans le BIO_PROFILE."""
    for esp in ESPECES_SUPPORTEES:
        r = load_bio_reacteur(esp)
        bp_path = BIO_PROFILE_DIR / f"BIO_PROFILE_Ω_{esp}.json"
        with open(bp_path) as f:
            bp = json.load(f)
        for eng_name, eng_def in r["bio_reacteur_outputs"].items():
            assert "bio_profile_paths" in eng_def
            assert len(eng_def["bio_profile_paths"]) > 0
            for path in eng_def["bio_profile_paths"]:
                # Path doit pouvoir être navigué dans le BIO_PROFILE
                cur = bp
                for key in path.split("."):
                    assert isinstance(cur, dict) and key in cur, \
                        f"{esp}/{eng_name}: path '{path}' introuvable dans BIO_PROFILE_Ω"
                    cur = cur[key]


# ─────────────────────────────────────────────────────────────────────
# 7. Intégrité runtime — SHA-256 alignement
# ─────────────────────────────────────────────────────────────────────

def test_phase_xiii_11_integrity_report_all_pass():
    """Le rapport d'intégrité runtime renvoie all_pass=True."""
    rep = integrity_report()
    assert rep["all_pass"] is True
    assert rep["espece_count"] == 5
    for r in rep["espece_reports"]:
        assert r["load_status"] == "OK"
        assert r["source_bio_profile_match"] is True
        assert r["anti_generique_pass"] is True
        assert r["engines_count"] == 13


# ─────────────────────────────────────────────────────────────────────
# 8. V30 invariant — verrou cryptographique
# ─────────────────────────────────────────────────────────────────────

def test_phase_xiii_12_v30_locked_intact():
    """SHA-256 V30 (registry_lock + engine_ia_corridors) inchangés."""
    v30 = Path("/app/backend/engines/v8_institutional")
    assert _sha(v30 / "registry_lock_omega.py") == V30_REGISTRY_LOCK_SHA
    assert _sha(v30 / "engine_ia_corridors_omega.py") == V30_ENGINE_IA_CORRIDORS_SHA


# ─────────────────────────────────────────────────────────────────────
# 9. attach_bio_reacteur_to_compute_result — décoration aval
# ─────────────────────────────────────────────────────────────────────

def test_phase_xiii_13_attach_decorates_compute_result():
    """attach_bio_reacteur_to_compute_result enrichit un dict sans corrompre les clés."""
    fake_result = {
        "engine_marker": "ENGINE_ESPECE_CHEVREUIL_Ω",
        "espece_id": "CHEVREUIL",
        "layers_omega": {"X": 1},
        "scores_omega": {"score": 50.0},
    }
    out = attach_bio_reacteur_to_compute_result(fake_result, "CHEVREUIL")
    assert "bio_reacteur" in out
    assert out["bio_reacteur"]["reacteur_id"] == "BIO_REACTEUR_Ω_CHEVREUIL"
    assert out["bio_reacteur"]["activation_status_bio_reacteur"] == "ACTIF_BIO_REACTEUR_Ω"
    assert out["bio_reacteur"]["engines_count"] == 13
    assert out["bio_reacteur"]["anti_generique_pass"] is True
    # Les clés originales doivent être préservées
    assert out["engine_marker"] == "ENGINE_ESPECE_CHEVREUIL_Ω"
    assert out["scores_omega"]["score"] == 50.0

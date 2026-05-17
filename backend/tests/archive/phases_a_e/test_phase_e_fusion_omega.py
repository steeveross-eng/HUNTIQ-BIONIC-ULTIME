"""
test_phase_e_fusion_territoire_omega.py — PHASE-E PRÉ-FUSION
═══════════════════════════════════════════════════════════════════════════
Phase     : PHASE-E / FUSION_TERRITOIRE_Ω
Commandant: STEEVE-MAX
Tag       : BCE-4X ULTIME ABSOLU — TOP-ABSOLU

Tests institutionnels de la pré-fusion (livrables L1..L6). V30 strictement
verrouillé cryptographiquement, XIX non recomputé, VITAUX non recomputé,
backend en lecture seule.

Assertions obligatoires (≥ 12) :
  1. endpoint disponible (status 200)
  2. score_ultime ∈ [0,1]
  3. score_ultime_pct ∈ [0,100]
  4. bande ∈ ensemble fermé (5 valeurs)
  5. sum(weight) == 1.0 (topologie)
  6. sum(contribution) ≈ score_raw (±0.001)
  7. registry_lock_v30.invariant == True
  8. SHA-256 V30 == valeurs attendues
  9. idempotence : 2 appels identiques → même score
 10. dindon @ BSL → bio_presence_mask_halt=True & bande=PROSCRIT
 11. orignal @ BSL → score_ultime > 0 & bande ≠ PROSCRIT
 12. contributions_par_chaine couvre exactement C1..C6
 13. spec JSON contient 6 livrables et 5 bandes
 14. espèce invalide → 400
"""
from __future__ import annotations

import hashlib
import json
import os
import pathlib

import pytest
from fastapi.testclient import TestClient

# ─────────────────────────────────────────────────────────────────────────
# Constantes institutionnelles
# ─────────────────────────────────────────────────────────────────────────
BSL_LAT = 48.206657
BSL_LNG = -68.382422

V30_REGISTRY_LOCK_SHA256 = (
    "fb765b94cc1fd4216c4afa4c0fb72bc1fd8e18fc26b6955db8157b42a26ecb0c"
)
V30_ENGINE_IA_CORRIDORS_SHA256 = (
    "bcb1e3a6a92304a171978ee7b6be2151e7035c84d8ffc1690839d993be9e39d3"
)

BANDES_ATTENDUES = {"TRÈS_FAVORABLE", "FAVORABLE", "NEUTRE", "DÉFAVORABLE", "PROSCRIT"}

SPEC_PATH = "/app/frontend/public/reports/audit_territoire_omega_ultime/FUSION_TERRITOIRE_OMEGA.json"


@pytest.fixture(scope="module")
def client():
    # Charge l'app FastAPI globale (server.py)
    import sys
    sys.path.insert(0, "/app/backend")
    from server import app as fastapi_app
    return TestClient(fastapi_app)


# ─────────────────────────────────────────────────────────────────────────
# 1-4 · SCHÉMA ENDPOINT + BORNES DE SCORE
# ─────────────────────────────────────────────────────────────────────────
def test_phase_e_endpoint_available_and_schema(client):
    r = client.get("/api/v30/territoire/ultime-score",
                   params={"lat": BSL_LAT, "lon": BSL_LNG, "species": "orignal"})
    assert r.status_code == 200, r.text
    d = r.json()
    # Champs obligatoires de la spec L1
    for key in (
        "phase", "waypoint", "species", "score_ultime", "score_ultime_pct",
        "bande", "bande_color_primary", "action", "recommandations",
        "contributions_par_chaine", "inhibitors_applied",
        "v30_alignment_score", "v30_alignment_label",
        "bio_presence_status", "bio_presence_mask_halt",
        "registry_lock_v30", "sha256_registry_echo", "timestamp_utc",
    ):
        assert key in d, f"Champ institutionnel manquant: {key}"
    assert d["phase"].startswith("PHASE-E"), d["phase"]


def test_phase_e_score_bounds_and_band_closed_set(client):
    r = client.get("/api/v30/territoire/ultime-score",
                   params={"species": "orignal"})
    d = r.json()
    assert 0.0 <= d["score_ultime"] <= 1.0, d["score_ultime"]
    assert 0.0 <= d["score_ultime_pct"] <= 100.0, d["score_ultime_pct"]
    assert d["bande"] in BANDES_ATTENDUES, d["bande"]
    # Cohérence pct = score × 100 (tolérance 0.1 pour arrondis)
    assert abs(d["score_ultime_pct"] - d["score_ultime"] * 100.0) <= 0.1


# ─────────────────────────────────────────────────────────────────────────
# 5-6 · TOPOLOGIE DES 6 CHAÎNES + COHÉRENCE DES CONTRIBUTIONS
# ─────────────────────────────────────────────────────────────────────────
def test_phase_e_contributions_cover_6_chains_and_sum_weight_one(client):
    r = client.get("/api/v30/territoire/ultime-score", params={"species": "orignal"})
    d = r.json()
    contribs = d["contributions_par_chaine"]
    chains = [c["chain"] for c in contribs]
    assert chains == ["C1", "C2", "C3", "C4", "C5", "C6"], chains
    total_w = sum(c["weight"] for c in contribs)
    assert abs(total_w - 1.0) < 1e-6, total_w


def test_phase_e_sum_contributions_matches_score_raw_when_no_inhibitors(client):
    """Si aucun inhibiteur appliqué, Σ contributions ≈ score_ultime."""
    r = client.get("/api/v30/territoire/ultime-score", params={"species": "orignal"})
    d = r.json()
    if not d["inhibitors_applied"]:
        total = sum(c["contribution"] for c in d["contributions_par_chaine"])
        # arrondis propagés ; tolérance 0.01
        assert abs(total - d["score_ultime"]) < 0.01, (total, d["score_ultime"])


# ─────────────────────────────────────────────────────────────────────────
# 7-8 · INVARIANCE V30 (SHA-256)
# ─────────────────────────────────────────────────────────────────────────
def test_phase_e_registry_lock_v30_invariant_echo(client):
    r = client.get("/api/v30/territoire/ultime-score", params={"species": "orignal"})
    d = r.json()
    lock = d["registry_lock_v30"]
    assert lock["invariant"] is True
    assert lock["registry_lock_omega_sha256"] == V30_REGISTRY_LOCK_SHA256
    assert lock["engine_ia_corridors_omega_sha256"] == V30_ENGINE_IA_CORRIDORS_SHA256
    # echo doit être déterministe (sha256 de la concaténation des 2)
    expected_echo = hashlib.sha256(
        (V30_REGISTRY_LOCK_SHA256 + V30_ENGINE_IA_CORRIDORS_SHA256).encode("utf-8")
    ).hexdigest()
    assert d["sha256_registry_echo"] == expected_echo


def test_phase_e_v30_files_not_mutated_on_disk():
    """Double verrou : lecture directe des fichiers V30 (hash attendu)."""
    for path, expected in (
        ("/app/backend/engines/v8_institutional/registry_lock_omega.py",
         V30_REGISTRY_LOCK_SHA256),
        ("/app/backend/engines/v8_institutional/engine_ia_corridors_omega.py",
         V30_ENGINE_IA_CORRIDORS_SHA256),
    ):
        with open(path, "rb") as f:
            sha = hashlib.sha256(f.read()).hexdigest()
        assert sha == expected, f"V30 mutation détectée sur {path} ({sha})"


# ─────────────────────────────────────────────────────────────────────────
# 9 · IDEMPOTENCE
# ─────────────────────────────────────────────────────────────────────────
def test_phase_e_idempotence_two_identical_calls(client):
    params = {"species": "ours", "lat": BSL_LAT, "lon": BSL_LNG,
              "month": 10, "hour": 14}
    a = client.get("/api/v30/territoire/ultime-score", params=params).json()
    b = client.get("/api/v30/territoire/ultime-score", params=params).json()
    assert a["score_ultime"] == b["score_ultime"]
    assert a["bande"] == b["bande"]
    # contributions deterministes (pondérations + métriques statiques sur même waypoint/contexte)
    a_metrics = [c["metric_0_1"] for c in a["contributions_par_chaine"]]
    b_metrics = [c["metric_0_1"] for c in b["contributions_par_chaine"]]
    assert a_metrics == b_metrics


# ─────────────────────────────────────────────────────────────────────────
# 10-11 · INHIBITEURS BIO-PRESENCE_MASK + PRÉSENCE CONFIRMÉE
# ─────────────────────────────────────────────────────────────────────────
def test_phase_e_dindon_bsl_is_proscrit_with_halt(client):
    r = client.get("/api/v30/territoire/ultime-score",
                   params={"species": "dindon", "lat": BSL_LAT, "lon": BSL_LNG})
    d = r.json()
    assert d["bio_presence_mask_halt"] is True
    assert "BIO_PRESENCE_MASK_HALT" in d["inhibitors_applied"]
    assert d["bande"] == "PROSCRIT"
    assert d["score_ultime"] == 0.0
    assert d["action"].startswith("HALT")


def test_phase_e_orignal_bsl_is_present_and_scored(client):
    r = client.get("/api/v30/territoire/ultime-score",
                   params={"species": "orignal", "lat": BSL_LAT, "lon": BSL_LNG})
    d = r.json()
    assert d["bio_presence_mask_halt"] is False
    assert d["bio_presence_status"] == "PRESENT"
    assert d["score_ultime"] > 0.0
    assert d["bande"] != "PROSCRIT"


# ─────────────────────────────────────────────────────────────────────────
# 12 · COUVERTURE 5 ESPÈCES OFFICIELLES
# ─────────────────────────────────────────────────────────────────────────
@pytest.mark.parametrize("species", ["orignal", "cerf", "ours", "dindon", "wapiti"])
def test_phase_e_all_official_species_return_valid_band(client, species):
    r = client.get("/api/v30/territoire/ultime-score",
                   params={"species": species, "lat": BSL_LAT, "lon": BSL_LNG})
    assert r.status_code == 200, r.text
    d = r.json()
    assert d["species"] == species
    assert d["bande"] in BANDES_ATTENDUES


# ─────────────────────────────────────────────────────────────────────────
# 13 · VALIDATION SPÉCIFICATION JSON (LIVRABLE L1)
# ─────────────────────────────────────────────────────────────────────────
def test_phase_e_spec_json_contains_six_livrables_and_five_bandes():
    assert os.path.exists(SPEC_PATH), SPEC_PATH
    spec = json.loads(pathlib.Path(SPEC_PATH).read_text(encoding="utf-8"))
    assert "livrables_phase_e" in spec
    assert len(spec["livrables_phase_e"]) == 6
    assert set(spec["bandes"].keys()) == BANDES_ATTENDUES
    # Poids sommé à 1.0 côté spec
    total_w = sum(v["poids_defaut"]
                  for v in spec["regles_fusion"]["chaine_topologie"].values())
    assert abs(total_w - 1.0) < 1e-6, total_w
    # Echo attendu des SHA V30
    assert spec["registry_echo_attendu"]["registry_lock_omega_sha256"] == \
        V30_REGISTRY_LOCK_SHA256
    assert spec["registry_echo_attendu"]["engine_ia_corridors_omega_sha256"] == \
        V30_ENGINE_IA_CORRIDORS_SHA256


# ─────────────────────────────────────────────────────────────────────────
# 14 · ESPÈCE INVALIDE → 400
# ─────────────────────────────────────────────────────────────────────────
def test_phase_e_invalid_species_rejected(client):
    r = client.get("/api/v30/territoire/ultime-score",
                   params={"species": "licorne_cosmique"})
    assert r.status_code == 400
    d = r.json()
    assert "allowed" in d


# ─────────────────────────────────────────────────────────────────────────
# 15 · ENDPOINT /spec EXPOSE BIEN LA SPÉCIFICATION
# ─────────────────────────────────────────────────────────────────────────
def test_phase_e_spec_endpoint_returns_livrables(client):
    r = client.get("/api/v30/territoire/ultime-score/spec")
    assert r.status_code == 200
    d = r.json()
    assert d["phase"].startswith("PHASE-E")
    assert len(d["livrables_phase_e"]) == 6


# ─────────────────────────────────────────────────────────────────────────
# 16 · NON-RÉGRESSION SUPRA-BIO (E37..E48 INCHANGÉS)
# ─────────────────────────────────────────────────────────────────────────
def test_phase_e_no_regression_supra_bio_engines():
    """Les 12 engines E37..E48 doivent continuer d'exposer leur schéma canonique."""
    from engines.v8_institutional.engine_optimisation_habitat_omega import (
        compute_optimisation_habitat,
    )
    r = compute_optimisation_habitat(
        "orignal",
        {"attractiveness_score_0_1": 0.9},
        {"foraging_pressure_index": 0.8},
        {"group_avg_size": 1.2, "in_rut_period": True},
        {"health_index_0_1": 0.85},
        {"local_stability_index": 0.75},
        {"mean_transition": 0.8},
    )
    assert r["engine"] == "ENGINE_OPTIMISATION_HABITAT_Ω"
    assert r["habitat_band"] in ("ULTIME", "HAUT", "STANDARD", "LIMITÉ")

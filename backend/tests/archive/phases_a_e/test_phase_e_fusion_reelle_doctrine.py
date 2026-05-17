"""
test_phase_e_fusion_reelle_doctrine.py — PHASE-E DOCTRINE PERMANENTE 50%
═══════════════════════════════════════════════════════════════════════════
Phase     : PHASE-E / FUSION_TERRITOIRE_Ω (DOCTRINE PERMANENTE 50%)
Commandant: STEEVE-MAX
Tag       : BCE-4X ULTIME ABSOLU — TOP-ABSOLU

Tests des 5 articles de la doctrine permanente :
  1. Seuils permanents (score≥0.50, v30≥50)
  2. Dérogation BIO temporaire (paramètre bio_derogation)
  3. Refermeture automatique post-fusion
  4. V30 LOCKED (invariance SHA-256)
  5. Rapport HTML obligatoire ou fusion annulée

Aucun testing_agent_v3_fork. Validation manuelle.
"""
from __future__ import annotations

import hashlib
import os
import pathlib

import pytest
from fastapi.testclient import TestClient

BSL_LAT = 48.206657
BSL_LNG = -68.382422
REPORT_DIR = "/app/frontend/public/reports/audit_territoire_omega_ultime"
REPORT_REELLE = f"{REPORT_DIR}/RAPPORT_PHASE-E_FUSION_TERRITOIRE_Ω_RÉELLE.html"

V30_REGISTRY_LOCK_SHA256 = (
    "fb765b94cc1fd4216c4afa4c0fb72bc1fd8e18fc26b6955db8157b42a26ecb0c"
)
V30_ENGINE_IA_CORRIDORS_SHA256 = (
    "bcb1e3a6a92304a171978ee7b6be2151e7035c84d8ffc1690839d993be9e39d3"
)


@pytest.fixture(scope="module")
def client():
    import sys
    sys.path.insert(0, "/app/backend")
    from server import app as fastapi_app
    return TestClient(fastapi_app)


# ─────────────────────────────────────────────────────────────────────────
# Article 1 — Seuils permanents (score≥0.50, v30≥50)
# ─────────────────────────────────────────────────────────────────────────
def test_doctrine_thresholds_exposed_in_payload(client):
    r = client.get("/api/v30/territoire/ultime-score", params={"species": "orignal"})
    assert r.status_code == 200, r.text
    d = r.json()
    th = d["doctrine_thresholds"]
    assert th["score_min_fusion"] == 0.50
    assert th["v30_min_fusion"] == 50.0
    assert d["doctrine_version"].startswith("PHASE-E_DOCTRINE_PERMANENTE_50PCT")


def test_orignal_present_is_fusionnable_with_50pct_doctrine(client):
    r = client.get("/api/v30/territoire/ultime-score", params={"species": "orignal"})
    d = r.json()
    # Avec V30 conforme et bio présent, orignal doit être fusionnable
    if d["v30_alignment_score"] >= 50.0:
        assert d["fusionnable"] is True


# ─────────────────────────────────────────────────────────────────────────
# Article 2 — Dérogation BIO temporaire (dindon/wapiti fusionnables)
# ─────────────────────────────────────────────────────────────────────────
def test_dindon_blocked_without_derogation(client):
    r = client.get("/api/v30/territoire/ultime-score", params={"species": "dindon"})
    d = r.json()
    assert d["bio_presence_mask_halt"] is True
    assert d["bio_presence_mask_halt_natural"] is True
    assert d["bio_derogation_active"] is False
    assert d["score_ultime"] == 0.0
    assert d["bande"] == "PROSCRIT"
    assert d["fusionnable"] is False
    assert "BIO_PRESENCE_MASK_HALT" in d["inhibitors_applied"]


def test_dindon_fusionnable_with_derogation(client):
    r = client.get("/api/v30/territoire/ultime-score",
                   params={"species": "dindon", "bio_derogation": "true"})
    d = r.json()
    assert d["bio_presence_mask_halt_natural"] is True   # nature : absent
    assert d["bio_presence_mask_halt"] is False          # effectif : levé
    assert d["bio_derogation_active"] is True
    assert "BIO_DEROGATION_TEMPORAIRE_PHASE_E" in d["inhibitors_applied"]
    assert "BIO_PRESENCE_MASK_HALT" not in d["inhibitors_applied"]
    assert d["score_ultime"] > 0.0


def test_wapiti_fusionnable_with_derogation(client):
    r = client.get("/api/v30/territoire/ultime-score",
                   params={"species": "wapiti", "bio_derogation": "true"})
    d = r.json()
    assert d["bio_derogation_active"] is True
    assert d["score_ultime"] > 0.0


# ─────────────────────────────────────────────────────────────────────────
# Article 3 — Refermeture automatique du masque BIO post-fusion
# ─────────────────────────────────────────────────────────────────────────
def test_fusion_execute_closes_bio_mask_post_fusion(client):
    r = client.post("/api/v30/territoire/fusion-execute")
    assert r.status_code == 200, r.text
    d = r.json()
    assert d["fusion_canceled"] is False
    # Pendant la fusion : dindon/wapiti doivent avoir bio_halt_eff=False
    fwd = {p["species"]: p for p in d["fusion_with_derogation"]}
    assert fwd["dindon"]["bio_presence_mask_halt"] is False
    assert fwd["wapiti"]["bio_presence_mask_halt"] is False
    # Post-fusion : refermeture automatique → bio_halt_eff=True à nouveau
    post = {p["species"]: p for p in d["post_fusion_snapshot"]}
    assert post["dindon"]["bio_presence_mask_halt"] is True
    assert post["wapiti"]["bio_presence_mask_halt"] is True
    assert post["dindon"]["bio_derogation_active"] is False
    assert post["wapiti"]["bio_derogation_active"] is False
    assert post["dindon"]["score_ultime"] == 0.0
    assert post["wapiti"]["score_ultime"] == 0.0


def test_derogation_does_not_persist_after_call(client):
    """Aucune persistance — un appel sans dérogation après fusion-execute
    redonne le HALT naturel."""
    client.post("/api/v30/territoire/fusion-execute")
    r = client.get("/api/v30/territoire/ultime-score",
                   params={"species": "dindon"})
    d = r.json()
    assert d["bio_presence_mask_halt"] is True
    assert d["bio_derogation_active"] is False


# ─────────────────────────────────────────────────────────────────────────
# Article 4 — V30 LOCKED, XIX/VITAUX non recomputés
# ─────────────────────────────────────────────────────────────────────────
def test_v30_invariant_during_real_fusion(client):
    r = client.post("/api/v30/territoire/fusion-execute")
    d = r.json()
    lock = d["registry_lock_v30"]
    assert lock["invariant"] is True
    assert lock["registry_lock_omega_sha256"] == V30_REGISTRY_LOCK_SHA256
    assert lock["engine_ia_corridors_omega_sha256"] == V30_ENGINE_IA_CORRIDORS_SHA256
    expected_echo = hashlib.sha256(
        (V30_REGISTRY_LOCK_SHA256 + V30_ENGINE_IA_CORRIDORS_SHA256).encode("utf-8")
    ).hexdigest()
    assert d["sha256_registry_echo"] == expected_echo
    assert d["v30_locked"] is True
    assert d["xix_recomputed"] is False
    assert d["vitaux_recomputed"] is False


def test_v30_files_not_mutated_on_disk():
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
# Article 5 — Rapport HTML obligatoire ou fusion annulée
# ─────────────────────────────────────────────────────────────────────────
def test_report_published_after_fusion_execute(client):
    # purge éventuelle
    if os.path.exists(REPORT_REELLE):
        os.remove(REPORT_REELLE)
    r = client.post("/api/v30/territoire/fusion-execute")
    d = r.json()
    assert d["report"]["status"] == "PUBLISHED"
    assert d["fusion_canceled"] is False
    assert os.path.exists(REPORT_REELLE)
    content = pathlib.Path(REPORT_REELLE).read_text(encoding="utf-8")
    assert "PHASE-E" in content
    assert "FUSION TERRITOIRE" in content
    assert "Article" in content
    assert "STEEVE-MAX" in content
    # SHA-256 retourné concorde
    sha_disk = hashlib.sha256(content.encode("utf-8")).hexdigest()
    assert d["report"]["sha256"] == sha_disk


def test_doctrine_articles_in_response(client):
    r = client.post("/api/v30/territoire/fusion-execute")
    d = r.json()
    art = d["doctrine_articles"]
    assert art["article_1_seuils_permanents"]["score_min_fusion"] == 0.50
    assert art["article_1_seuils_permanents"]["v30_min_fusion"] == 50.0
    assert art["article_2_derogation_bio_temporaire"] is True
    assert art["article_3_refermeture_automatique"] is True
    assert art["article_4_v30_locked"] is True
    assert art["article_5_rapport_obligatoire"] is True


# ─────────────────────────────────────────────────────────────────────────
# Spec JSON mise à jour V2
# ─────────────────────────────────────────────────────────────────────────
def test_spec_v2_doctrine_permanente_published():
    import json
    spec_path = f"{REPORT_DIR}/FUSION_TERRITOIRE_OMEGA.json"
    spec = json.loads(pathlib.Path(spec_path).read_text(encoding="utf-8"))
    assert "doctrine_articles" in spec
    art = spec["doctrine_articles"]
    assert art["article_1_seuils_permanents"]["score_min_fusion"] == 0.50
    assert art["article_1_seuils_permanents"]["v30_min_fusion"] == 50.0
    assert "article_2_derogation_bio_temporaire" in art
    assert "article_3_refermeture_automatique" in art
    assert "article_5_rapport_obligatoire" in art


# ─────────────────────────────────────────────────────────────────────────
# Couverture toutes espèces (5/5) avec dérogation
# ─────────────────────────────────────────────────────────────────────────
@pytest.mark.parametrize("sp", ["orignal", "cerf", "ours", "dindon", "wapiti"])
def test_all_species_have_score_with_derogation(client, sp):
    r = client.get("/api/v30/territoire/ultime-score",
                   params={"species": sp, "bio_derogation": "true"})
    d = r.json()
    assert r.status_code == 200
    assert d["score_ultime"] > 0.0
    assert d["bande"] != "PROSCRIT"


# ─────────────────────────────────────────────────────────────────────────
# Idempotence et invariants doctrinaux
# ─────────────────────────────────────────────────────────────────────────
def test_idempotence_with_derogation(client):
    params = {"species": "wapiti", "bio_derogation": "true"}
    a = client.get("/api/v30/territoire/ultime-score", params=params).json()
    b = client.get("/api/v30/territoire/ultime-score", params=params).json()
    assert a["score_ultime"] == b["score_ultime"]
    assert a["bande"] == b["bande"]


def test_fusion_execute_returns_consistent_counts(client):
    r = client.post("/api/v30/territoire/fusion-execute")
    d = r.json()
    fusionnable = [p for p in d["fusion_with_derogation"] if p.get("fusionnable")]
    assert len(fusionnable) == d["fusionnable_count"]
    assert {p["species"] for p in fusionnable} == set(d["fusionnable_species"])

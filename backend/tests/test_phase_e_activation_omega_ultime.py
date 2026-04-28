"""
test_phase_e_activation_territoire_ultime.py — ACTIVATION PRODUCTION TERRITOIRE_Ω_ULTIME
═══════════════════════════════════════════════════════════════════════════════════════
Phase     : ACTIVATION PRODUCTION (post-fusion réelle PHASE-E)
Commandant: STEEVE-MAX
Tag       : BCE-4X ULTIME ABSOLU — TOP-ABSOLU

Tests d'activation institutionnelle :
  1. Endpoint /api/v30/territoire/ultime-score actif et conforme.
  2. Endpoint POST /api/v30/territoire/fusion-execute opérationnel.
  3. Pipeline 6 niveaux (48 engines) consommé via fusion_territoire_omega.
  4. 6 chaînes institutionnelles couvertes (C1..C6 · Σ poids = 1.00).
  5. Toutes les 5 espèces officielles fournissent un score ULTIME en
     conditions production (avec et sans dérogation).
  6. Doctrine permanente 50% appliquée.
  7. V30 LOCKED + invariance SHA-256 inchangée post-activation.
  8. Page démo HUD frontend accessible (build production).
  9. HUD intégré dans MonTerritoireBionic (regex source).
 10. Spec V2 + livrables (acte de validation, rapport activation) publiés.
"""
from __future__ import annotations

import hashlib
import os
import pathlib
import re

import pytest
from fastapi.testclient import TestClient

REPORT_DIR = "/app/frontend/public/reports/audit_territoire_omega_ultime"
V30_REGISTRY_LOCK_SHA256 = (
    "fb765b94cc1fd4216c4afa4c0fb72bc1fd8e18fc26b6955db8157b42a26ecb0c"
)
V30_ENGINE_IA_CORRIDORS_SHA256 = (
    "bcb1e3a6a92304a171978ee7b6be2151e7035c84d8ffc1690839d993be9e39d3"
)
ALL_SPECIES = ("orignal", "cerf", "ours", "dindon", "wapiti")


@pytest.fixture(scope="module")
def client():
    import sys
    sys.path.insert(0, "/app/backend")
    from server import app as fastapi_app
    return TestClient(fastapi_app)


# 1. Endpoint actif
def test_activation_endpoint_actif(client):
    r = client.get("/api/v30/territoire/ultime-score", params={"species": "orignal"})
    assert r.status_code == 200
    d = r.json()
    assert d["phase"].startswith("PHASE-E")
    assert d["doctrine_version"].startswith("PHASE-E_DOCTRINE_PERMANENTE_50PCT")


# 2. Fusion-execute opérationnel
def test_activation_fusion_execute_operationnel(client):
    r = client.post("/api/v30/territoire/fusion-execute")
    assert r.status_code == 200
    d = r.json()
    assert d["fusion_canceled"] is False
    assert d["report"]["status"] == "PUBLISHED"
    assert d["fusionnable_count"] >= 1


# 3. Pipeline 6 niveaux consommé
def test_activation_pipeline_consomme_les_48_engines():
    """Vérifie que fusion_territoire_omega importe les engines clés des 6 niveaux."""
    p = "/app/backend/engines/v8_institutional/fusion_territoire_omega.py"
    src = pathlib.Path(p).read_text(encoding="utf-8")
    expected = [
        "species_presence_mask_omega",          # BIOLOGIE (E26)
        "v30_corridors_status",                  # FUSION (E03)
        "engine_sol_nutriments_omega",           # E37
        "engine_forage_qualite_omega",           # E38
        "engine_carence_nutritionnelle_omega",   # E39
        "engine_recettes_salines_omega",         # E40
        "engine_champs_nourriciers_omega",       # E41
        "engine_canopee_thermique_omega",        # E42
        "engine_microclimat_advanced_omega",     # E43
        "engine_trophic_behavior_omega",         # E44
        "engine_social_structure_omega",         # E45
        "engine_sante_physio_omega",             # E46
        "engine_nutritional_attractiveness_omega",  # E47
        "engine_optimisation_habitat_omega",     # E48
    ]
    for mod in expected:
        assert mod in src, f"Engine {mod} non consommé par PHASE-E"


# 4. 6 chaînes Σ=1.00
def test_activation_6_chaines_somme_un(client):
    r = client.get("/api/v30/territoire/ultime-score", params={"species": "orignal"})
    contribs = r.json()["contributions_par_chaine"]
    chains = [c["chain"] for c in contribs]
    assert chains == ["C1", "C2", "C3", "C4", "C5", "C6"]
    total = sum(c["weight"] for c in contribs)
    assert abs(total - 1.0) < 1e-6


# 5. Toutes les 5 espèces actives
@pytest.mark.parametrize("sp", ALL_SPECIES)
def test_activation_5_especes_actives(client, sp):
    r = client.get("/api/v30/territoire/ultime-score", params={"species": sp})
    assert r.status_code == 200
    d = r.json()
    assert d["species"] == sp
    assert 0.0 <= d["score_ultime"] <= 1.0
    assert d["bande"] in {"TRÈS_FAVORABLE", "FAVORABLE", "NEUTRE",
                          "DÉFAVORABLE", "PROSCRIT"}


@pytest.mark.parametrize("sp", ALL_SPECIES)
def test_activation_5_especes_avec_derogation_fusionnables(client, sp):
    r = client.get("/api/v30/territoire/ultime-score",
                   params={"species": sp, "bio_derogation": "true"})
    assert r.status_code == 200
    d = r.json()
    assert d["score_ultime"] > 0.0


# 6. Doctrine permanente 50%
def test_activation_doctrine_permanente_50_appliquee(client):
    r = client.get("/api/v30/territoire/ultime-score", params={"species": "orignal"})
    th = r.json()["doctrine_thresholds"]
    assert th["score_min_fusion"] == 0.50
    assert th["v30_min_fusion"] == 50.0


# 7. V30 LOCKED inchangé post-activation
def test_activation_v30_inchange_post_activation():
    for path, expected in (
        ("/app/backend/engines/v8_institutional/registry_lock_omega.py",
         V30_REGISTRY_LOCK_SHA256),
        ("/app/backend/engines/v8_institutional/engine_ia_corridors_omega.py",
         V30_ENGINE_IA_CORRIDORS_SHA256),
    ):
        with open(path, "rb") as f:
            sha = hashlib.sha256(f.read()).hexdigest()
        assert sha == expected, f"V30 mutation post-activation : {path} ({sha})"


# 8. Spec V2 publiée
def test_activation_spec_v2_publiee():
    p = f"{REPORT_DIR}/FUSION_TERRITOIRE_OMEGA.json"
    assert os.path.exists(p)
    import json
    spec = json.loads(pathlib.Path(p).read_text(encoding="utf-8"))
    assert "doctrine_articles" in spec
    assert spec["doctrine_articles"]["article_1_seuils_permanents"]["score_min_fusion"] == 0.50


# 9. HUD intégré dans MonTerritoireBionic
def test_activation_hud_integre_dans_carte_vivante():
    p = "/app/frontend/src/components/territoire/MonTerritoireBionic.jsx"
    src = pathlib.Path(p).read_text(encoding="utf-8")
    assert "import HudTerritoireUltime" in src
    assert "<HudTerritoireUltime" in src
    assert 'data-testid="hud-ultime-prod-wrapper"' in src


# 10. Acte de validation institutionnelle scellé
def test_activation_acte_validation_institutionnelle_scelle():
    p = f"{REPORT_DIR}/ACTE_VALIDATION_INSTITUTIONNELLE_TERRITOIRE_OMEGA.json"
    assert os.path.exists(p)
    import json
    acte = json.loads(pathlib.Path(p).read_text(encoding="utf-8"))
    assert acte["v30_invariance_au_sceau"]["invariant"] is True


# 11. Vérification structurelle scellée
def test_activation_verification_structurelle_disponible():
    p = f"{REPORT_DIR}/VERIFICATION_STRUCTURELLE_TERRITOIRE_OMEGA.json"
    assert os.path.exists(p)
    import json
    v = json.loads(pathlib.Path(p).read_text(encoding="utf-8"))
    assert v["engines_count_total"] == 48
    assert v["topology_invariant_sum_1"] is True


# 12. JSON activation TERRITOIRE_Ω_ULTIME_ACTIF publié (Article 2)
def test_activation_json_actif_publie():
    p = f"{REPORT_DIR}/TERRITOIRE_Ω_ULTIME_ACTIF.json"
    assert os.path.exists(p), f"livrable Article 2 manquant : {p}"
    import json
    d = json.loads(pathlib.Path(p).read_text(encoding="utf-8"))
    assert d.get("status") == "ACTIF"


# 13. Rapport HTML activation publié (Article 2)
def test_activation_rapport_html_publie():
    p = f"{REPORT_DIR}/RAPPORT_TERRITOIRE_Ω_ULTIME_ACTIVATION.html"
    assert os.path.exists(p), f"rapport activation HTML manquant : {p}"
    txt = pathlib.Path(p).read_text(encoding="utf-8")
    assert "ACTIVATION" in txt
    assert "TERRITOIRE" in txt
    assert "STEEVE-MAX" in txt

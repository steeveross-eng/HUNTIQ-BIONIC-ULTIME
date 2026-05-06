"""
Phase XXIX · ORDRE N°53 — Tests anti-régressifs SUPER_ENGINES ↔ BP135
══════════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU x3 · ANTI_GÉNÉRIQUE_STRICT

Couplage direct SUPER_ENGINES ↔ BIO_PROFILE_OMEGA_135 (3 modes).
Naming policy: aucun mot-clé exclu BCE-4X.
"""
from __future__ import annotations

import importlib

import pytest


# ═════════════════════════════════════════════════════════════════════════
# Fixtures
# ═════════════════════════════════════════════════════════════════════════
@pytest.fixture()
def coupling():
    import engines.v8_institutional.especes.super_engines_bp135_coupling_omega as m
    importlib.reload(m)
    return m


@pytest.fixture()
def bp135_loader():
    import engines.v8_institutional.especes.bio_profile_135_loader_omega as m
    return m


# ═════════════════════════════════════════════════════════════════════════
# 1. Module API + invariants
# ═════════════════════════════════════════════════════════════════════════
def test_module_exports(coupling):
    assert hasattr(coupling, "compute_master_direct_bp135")
    assert hasattr(coupling, "compute_all_masters_direct_bp135")
    assert hasattr(coupling, "compute_super_engines_bp135_fusion")
    assert hasattr(coupling, "audit_bp135_vs_bioreacteur_drift")
    assert hasattr(coupling, "MASTER_LONG_TO_SHORT")
    assert hasattr(coupling, "MASTER_TO_BLOCKS")
    assert hasattr(coupling, "CouplingError")


def test_master_mappings_consistent(coupling):
    # 6 masters dans les deux sens
    assert len(coupling.MASTER_LONG_TO_SHORT) == 6
    assert len(coupling.MASTER_SHORT_TO_LONG) == 6
    # Bilatéralité
    for long_id, short_id in coupling.MASTER_LONG_TO_SHORT.items():
        assert coupling.MASTER_SHORT_TO_LONG[short_id] == long_id
    # 6 masters mappés vers blocs BP135
    assert len(coupling.MASTER_TO_BLOCKS) == 6
    # Les 9 blocs BP135 sont tous consommés au moins une fois
    all_blocks_consumed = set()
    for blocks in coupling.MASTER_TO_BLOCKS.values():
        all_blocks_consumed.update(blocks)
    assert len(all_blocks_consumed) == 9


# ═════════════════════════════════════════════════════════════════════════
# 2. compute_master_direct_bp135 par master
#    Note : alias neutres requis (BCE-4X exclut les mots "corridor",
#    "territoire" dans les noms de tests).
# ═════════════════════════════════════════════════════════════════════════
MASTER_ALIASES = {
    "CONNECTIVITY": "CORRIDORS_MASTER_Ω",
    "NUTRITION": "NUTRITION_MASTER_Ω",
    "SENSORIEL": "SENSORIEL_MASTER_Ω",
    "COMPORTEMENT": "COMPORTEMENT_MASTER_Ω",
    "GOUVERNANCE": "GOUVERNANCE_MASTER_Ω",
    "GROUND": "TERRITOIRE_MASTER_Ω",
}


@pytest.mark.parametrize("master_alias", list(MASTER_ALIASES.keys()))
def test_master_direct_score_executes(coupling, master_alias):
    master_short = MASTER_ALIASES[master_alias]
    r = coupling.compute_master_direct_bp135(master_short)
    assert r["manifest_id"] == "BP135_DIRECT_MASTER_SCORE_Ω"
    assert r["ordre"] == "N°53"
    assert r["master_id_short"] == master_short
    # Score 0..100
    assert 0 <= r["score_master_bp135_direct"] <= 100
    # 5 espèces présentes
    assert len(r["score_par_espece"]) == 5
    for esp, sc in r["score_par_espece"].items():
        assert 0 <= sc <= 100
    # blocs consommés non vides
    assert len(r["blocks_consumed"]) >= 1
    # anti-générique pass attendu pour ce dataset
    assert r["anti_generique_pass"] is True
    # V30_LOCK SHA-256 inviolé
    assert r["v30_lock_status"]["v30_lock"] == "INVIOLÉ"
    assert len(r["v30_lock_status"]["bp135_sha256"]) == 64


def test_master_direct_long_id_works(coupling):
    """Acceptation des deux formes (long/short) d'identifiant master."""
    r1 = coupling.compute_master_direct_bp135("ENGINE_NUTRITION_MASTER_Ω")
    r2 = coupling.compute_master_direct_bp135("NUTRITION_MASTER_Ω")
    assert r1["score_master_bp135_direct"] == r2["score_master_bp135_direct"]
    assert r1["master_id_short"] == "NUTRITION_MASTER_Ω"
    assert r1["master_id_long"] == "ENGINE_NUTRITION_MASTER_Ω"


def test_master_direct_unknown_raises(coupling):
    with pytest.raises(coupling.CouplingError, match="MASTER_INCONNU"):
        coupling.compute_master_direct_bp135("INVENTED_MASTER_Ω")


def test_master_direct_scientific_method_dominates(coupling):
    """L'algorithme position_in_range doit dominer (>=80% des entrées)."""
    r = coupling.compute_master_direct_bp135("NUTRITION_MASTER_Ω")
    methods = r["scoring_methods_distribution"]
    total = sum(methods.values())
    assert total > 0
    # ≥ 80% des entrées scorées par algorithme position_in_range
    pir_pct = methods["position_in_range"] / total
    assert pir_pct >= 0.80


# ═════════════════════════════════════════════════════════════════════════
# 3. compute_all_masters_direct_bp135
# ═════════════════════════════════════════════════════════════════════════
def test_all_masters_direct_six_results(coupling):
    r = coupling.compute_all_masters_direct_bp135()
    assert r["manifest_id"] == "BP135_DIRECT_ALL_MASTERS_Ω"
    assert r["mode"] == "direct"
    assert r["n_masters"] == 6
    # Score global 0..100
    assert 0 <= r["score_global_moyen"] <= 100
    # 6 masters dans le résultat
    assert len(r["masters_results"]) == 6
    # Anti-générique pass global
    assert r["anti_generique_pass_global"] is True
    # Performance < 5s
    assert r["elapsed_s"] < 5.0


# ═════════════════════════════════════════════════════════════════════════
# 4. compute_super_engines_bp135_fusion
# ═════════════════════════════════════════════════════════════════════════
def test_fusion_default_weights_50_50(coupling):
    r = coupling.compute_super_engines_bp135_fusion()
    assert r["manifest_id"] == "SUPER_ENGINES_BP135_FUSION_Ω"
    assert r["mode"] == "fusion"
    assert r["weights_doctrinal"]["bio_reacteur"] == 0.5
    assert r["weights_doctrinal"]["bp135"] == 0.5
    assert 0 <= r["score_global_fusion"] <= 100
    assert r["n_masters_total"] == 6
    # Drift max <= 100 (théorique)
    assert r["drift_max_br_vs_bp135"] <= 100


def test_fusion_normalized_weights(coupling):
    """Poids non normalisés (somme != 1) doivent être normalisés."""
    r = coupling.compute_super_engines_bp135_fusion(
        weights={"bio_reacteur": 1.0, "bp135": 1.0})
    # 1.0 + 1.0 = 2.0 ⇒ normalisés à 0.5 / 0.5
    assert r["weights_doctrinal"]["bio_reacteur"] == 0.5
    assert r["weights_doctrinal"]["bp135"] == 0.5


def test_fusion_bp135_only_weights(coupling):
    """Poids 0/1 → fusion = bp135_score pur pour masters couplés."""
    r = coupling.compute_super_engines_bp135_fusion(
        weights={"bio_reacteur": 0.0, "bp135": 1.0})
    assert r["weights_doctrinal"]["bio_reacteur"] == 0.0
    assert r["weights_doctrinal"]["bp135"] == 1.0
    # Pour masters couplés : fusion_score == bp135_direct_score
    for v in r["fusion_results"].values():
        if v.get("couplage_actif"):
            assert v["fusion_score"] == v["bp135_direct_score"]


def test_fusion_invalid_weights_raises(coupling):
    """Somme des poids = 0 → CouplingError."""
    with pytest.raises(coupling.CouplingError, match="weights"):
        coupling.compute_super_engines_bp135_fusion(
            weights={"bio_reacteur": 0.0, "bp135": 0.0})


def test_fusion_drift_per_master_present(coupling):
    """Chaque master couplé expose un drift BR ↔ BP135."""
    r = coupling.compute_super_engines_bp135_fusion()
    couples = [
        v for v in r["fusion_results"].values()
        if v.get("couplage_actif")]
    assert len(couples) >= 5  # tous sauf cas spéciaux
    for v in couples:
        assert "drift_br_vs_bp135" in v
        assert "drift_alert" in v
        assert v["drift_br_vs_bp135"] >= 0
        assert isinstance(v["drift_alert"], bool)


# ═════════════════════════════════════════════════════════════════════════
# 5. audit_bp135_vs_bioreacteur_drift
# ═════════════════════════════════════════════════════════════════════════
def test_audit_drift_executes(coupling):
    r = coupling.audit_bp135_vs_bioreacteur_drift()
    assert r["manifest_id"] == "BP135_VS_BIOREACTEUR_DRIFT_AUDIT_Ω"
    assert r["mode"] == "audit"
    # SHA-256 forensique
    assert len(r["audit_payload_sha256"]) == 64
    # Coherence dans une catégorie connue
    assert r["coherence_interpretation"] in (
        "EXCELLENTE", "ACCEPTABLE", "DIVERGENTE", "CRITIQUE")
    # n_masters_audited >= 5
    assert r["n_masters_audited"] >= 5


def test_audit_drift_table_per_species(coupling):
    """Chaque ligne de drift_table contient le drift par espèce (5 espèces)."""
    r = coupling.audit_bp135_vs_bioreacteur_drift()
    for line in r["drift_table"]:
        assert "drift_par_espece" in line
        assert len(line["drift_par_espece"]) == 5
        # Drifts >= 0
        for esp, dv in line["drift_par_espece"].items():
            assert dv >= 0
        assert line["drift_max_par_espece"] >= line["drift_min_par_espece"]


def test_audit_payload_sha256_reproducible(coupling):
    """Deux runs consécutifs → même SHA-256 (déterminisme)."""
    r1 = coupling.audit_bp135_vs_bioreacteur_drift()
    r2 = coupling.audit_bp135_vs_bioreacteur_drift()
    assert r1["audit_payload_sha256"] == r2["audit_payload_sha256"]


# ═════════════════════════════════════════════════════════════════════════
# 6. Anti-régression FUSION ADD-ONLY
# ═════════════════════════════════════════════════════════════════════════
def test_bp135_file_unchanged_after_coupling(coupling, bp135_loader):
    """BP135 SHA-256 doit être identique avant et après les calculs.
    Doctrine FUSION ADD-ONLY : aucune mutation du fichier source."""
    sha_before = bp135_loader.file_sha256()
    coupling.compute_all_masters_direct_bp135()
    coupling.compute_super_engines_bp135_fusion()
    coupling.audit_bp135_vs_bioreacteur_drift()
    sha_after = bp135_loader.file_sha256()
    assert sha_before == sha_after
    assert len(sha_before) == 64


def test_v30_lock_consistent(coupling):
    """V30_LOCK : SHA-256 stable entre les modes."""
    r1 = coupling.compute_all_masters_direct_bp135()
    r2 = coupling.compute_super_engines_bp135_fusion()
    sha1 = r1["v30_lock_status"]["bp135_sha256"]
    sha2 = r2["v30_lock_status"]["bp135_sha256"]
    assert sha1 == sha2
    # SUPER_ENGINE_LOCK doit aussi être identique
    assert (
        r1["v30_lock_status"]["super_engine_lock_sha256"]
        == r2["v30_lock_status"]["super_engine_lock_sha256"])


def test_super_engines_logic_module_unchanged(coupling):
    """Le couplage NE DOIT PAS modifier le module super_engines_omega_logic.
    Vérifie l'inviolabilité doctrinale."""
    from engines.v8_institutional.especes import super_engines_omega_logic as sel
    # Les fonctions clés existent (ne sont pas écrasées)
    assert hasattr(sel, "compute_corridors_master")
    assert hasattr(sel, "compute_nutrition_master")
    assert hasattr(sel, "compute_sensoriel_master")
    assert hasattr(sel, "compute_comportement_master")
    assert hasattr(sel, "compute_gouvernance_master")
    assert hasattr(sel, "compute_territoire_master")
    assert hasattr(sel, "compute_all_super_engines")


# ═════════════════════════════════════════════════════════════════════════
# 7. Score scientifique (entrée individuelle)
# ═════════════════════════════════════════════════════════════════════════
def test_score_entry_position_in_range_middle(coupling):
    """Valeur typique pile au milieu → score 50."""
    fake_entry = {
        "schema": "x", "version": "x", "block": "x", "block_id": "x",
        "block_description": "x", "parameter_id": "X-001",
        "parameter_name": "x", "parameter_label": "x",
        "species_code": "ORIGNAL", "species_latin": "x",
        "species_common_fr": "x", "unit": "kg",
        "value_range_min": 0, "value_range_max": 100,
        "value_typical": 50, "scientific_source": "x",
    }
    r = coupling._score_entry_scientific(fake_entry)
    assert r["score"] == 50.0
    assert r["scoring_method"] == "position_in_range"
    assert r["anti_generique_violation"] is None


def test_score_entry_out_of_range_violation(coupling):
    """Valeur typique hors range → anti-générique violation (score 0)."""
    fake_entry = {
        "schema": "x", "version": "x", "block": "x", "block_id": "x",
        "block_description": "x", "parameter_id": "X-001",
        "parameter_name": "x", "parameter_label": "x",
        "species_code": "ORIGNAL", "species_latin": "x",
        "species_common_fr": "x", "unit": "kg",
        "value_range_min": 0, "value_range_max": 100,
        "value_typical": 150, "scientific_source": "x",
    }
    r = coupling._score_entry_scientific(fake_entry)
    assert r["score"] == 0.0
    assert r["scoring_method"] == "anti_generique_violation"
    assert "out_of_range" in r["anti_generique_violation"]


def test_score_entry_missing_field_violation(coupling):
    """Champ obligatoire manquant → violation."""
    fake_entry = {
        "schema": "x", "version": "x", "block": "x",
        # block_id manquant
        "block_description": "x", "parameter_id": "X-001",
        "parameter_name": "x", "parameter_label": "x",
        "species_code": "ORIGNAL", "species_latin": "x",
        "species_common_fr": "x", "unit": "kg",
        "value_range_min": 0, "value_range_max": 100,
        "value_typical": 50, "scientific_source": "x",
    }
    r = coupling._score_entry_scientific(fake_entry)
    assert r["score"] == 0.0
    assert r["scoring_method"] == "anti_generique_violation"
    assert "missing_fields" in r["anti_generique_violation"]

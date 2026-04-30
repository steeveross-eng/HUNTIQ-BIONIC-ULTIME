"""
test_phase_xviii_bio_profile_135_omega.py — PHASE XVIII · BIO_PROFILE_Ω_135
═══════════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU x3 · ORDRE N°38

Couverture pytest : ingestion + normalisation + cross-ref BIO_PROFILE_Ω_135.
14 tests minimum.
═══════════════════════════════════════════════════════════════════════════
"""
from __future__ import annotations
import pytest

from engines.v8_institutional.especes.bio_profile_135_loader_omega import (
    load_bio_profile_135, file_sha256, validate_entries, index_entries,
    normalize_dataset, compute_block_score_for_master, get_entries_for_species,
    REQUIRED_FIELDS, ESPECES_135, BLOCS_135, BLOCK_TO_MASTER,
    BioProfile135Error,
)


# ─── INGESTION ────────────────────────────────────────────────────────

def test_bp135_load_returns_dict():
    d = load_bio_profile_135()
    assert isinstance(d, dict)
    assert d["statistics"]["total_entries"] == 675


def test_bp135_total_entries_675():
    d = load_bio_profile_135()
    assert len(d["entries"]) == 675


def test_bp135_9_blocks_15_params_each():
    d = load_bio_profile_135()
    assert len(d["blocks_summary"]) == 9
    for b in d["blocks_summary"]:
        assert b["parameter_count"] == 15


def test_bp135_5_species_canoniques():
    d = load_bio_profile_135()
    species_codes = {s["code"] for s in d["species"]}
    assert species_codes == set(ESPECES_135)


def test_bp135_file_sha256_stable_64_chars():
    s1 = file_sha256()
    s2 = file_sha256()
    assert s1 == s2
    assert len(s1) == 64


# ─── NORMALISATION ────────────────────────────────────────────────────

def test_bp135_validate_entries_no_missing_fields():
    val = validate_entries()
    assert val["total_entries"] == 675
    # Tolère 0 manquant (les 16 champs obligatoires doivent tous être présents)
    assert val["all_required_fields_present"] is True


def test_bp135_normalize_dataset_structure():
    n = normalize_dataset()
    assert n["manifest_id"] == "BIO_PROFILE_Ω_135_NORMALISÉ"
    assert n["totaux"]["total_entries"] == 675
    assert n["totaux"]["total_blocks"] == 9
    assert "completeness_par_bloc_espece" in n
    # Chaque bloc x espèce doit avoir 15 entries
    for bloc in BLOCS_135:
        for esp in ESPECES_135:
            cell = n["completeness_par_bloc_espece"][bloc][esp]
            assert cell["entries_count"] == 15


def test_bp135_index_entries_partition_675():
    idx = index_entries()
    total_block = sum(len(v) for v in idx["by_block"].values())
    total_species = sum(len(v) for v in idx["by_species"].values())
    assert total_block == 675
    assert total_species == 675


# ─── CROSS-REF + MASTERS ──────────────────────────────────────────────

def test_bp135_block_to_master_coverage():
    """Les 9 blocs doivent être tous mappés vers un master."""
    assert len(BLOCK_TO_MASTER) == 9
    # 6 masters distincts
    masters = set(BLOCK_TO_MASTER.values())
    assert masters == {"NUTRITION_MASTER_Ω", "CORRIDORS_MASTER_Ω",
                        "SENSORIEL_MASTER_Ω", "COMPORTEMENT_MASTER_Ω",
                        "GOUVERNANCE_MASTER_Ω", "TERRITOIRE_MASTER_Ω"}


@pytest.mark.parametrize("master_alias", [
    ("NUTRI", "NUTRITION_MASTER_Ω"),
    ("CORR_M", "CORRIDORS_MASTER_Ω"),
    ("SENSO", "SENSORIEL_MASTER_Ω"),
    ("COMPO", "COMPORTEMENT_MASTER_Ω"),
    ("GOUV", "GOUVERNANCE_MASTER_Ω"),
    ("TERR_M", "TERRITOIRE_MASTER_Ω"),
])
def test_bp135_score_for_each_super_master(master_alias):
    _, master = master_alias
    out = compute_block_score_for_master(master)
    assert out["master_id"] == master
    assert out["blocs_count"] >= 1
    assert 0.0 <= out["score_master_recalcule"] <= 100.0
    assert set(out["score_par_espece"].keys()) == set(ESPECES_135)


# ─── ENTRIES PAR ESPECE ───────────────────────────────────────────────

@pytest.mark.parametrize("espece", ESPECES_135)
def test_bp135_get_entries_per_espece_135(espece):
    entries = get_entries_for_species(espece)
    assert len(entries) == 135  # 9 blocs × 15 paramètres


def test_bp135_get_entries_invalid_espece_raises():
    with pytest.raises(BioProfile135Error, match="ESPECE_INCONNUE"):
        get_entries_for_species("CARIBOU")


def test_bp135_get_entries_filtered_by_block():
    entries = get_entries_for_species("ORIGNAL", block="MORPHOLOGIE")
    assert len(entries) == 15
    assert all(e["block"] == "MORPHOLOGIE" for e in entries)

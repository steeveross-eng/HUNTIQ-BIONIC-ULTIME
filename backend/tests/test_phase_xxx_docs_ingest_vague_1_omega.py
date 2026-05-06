"""
Phase XXX · ORDRE N°54-Ω VAGUE 1 — Tests anti-régressifs ingestion docs
══════════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU x3 · ANTI_GÉNÉRIQUE_STRICT

Tests de l'ingestion documentaire VAGUE 1 (5 rapports scientifiques) :
  · Parse .docx (paragraphes + tables)
  · Extraction sections GOV/UNI/PR
  · Extraction DOI (anti-générique)
  · Normalisation tableaux maîtres
  · Persistance registry_science + registry_master_tables
  · SHA-256 longitudinal
  · AUCUN recalcul moteur (V30_LOCK INVIOLÉ)

Naming policy : aucun mot-clé exclu BCE-4X.
"""
from __future__ import annotations

import importlib
import json
from pathlib import Path

import pytest


@pytest.fixture()
def docs_ingest():
    import engines.v8_institutional.especes.docs_ingest_omega as m
    importlib.reload(m)
    return m


# ═════════════════════════════════════════════════════════════════════════
# 1. API + invariants
# ═════════════════════════════════════════════════════════════════════════
def test_module_exports(docs_ingest):
    for name in (
        "parse_docx", "extract_sections_gov_uni_pr", "extract_dois",
        "resolve_dois_http_200", "normalize_master_tables",
        "ingest_species_doc", "ingest_all_species_vague_1",
        "list_registry_science", "get_master_table",
        "ESPECES_VAGUE_1", "SOURCE_CATEGORIES",
    ):
        assert hasattr(docs_ingest, name), f"missing {name}"


def test_especes_vague_1(docs_ingest):
    assert sorted(docs_ingest.ESPECES_VAGUE_1) == sorted([
        "chevreuil", "dindon", "orignal", "ours_noir", "wapiti",
    ])


def test_source_categories(docs_ingest):
    assert docs_ingest.SOURCE_CATEGORIES == ("GOV", "UNI", "PR")


# ═════════════════════════════════════════════════════════════════════════
# 2. extract_dois (anti-générique strict)
# ═════════════════════════════════════════════════════════════════════════
def test_extract_dois_real_pattern(docs_ingest):
    text = (
        "Référence: doi.org/10.1371/journal.pone.0325656 "
        "et autre 10.1234/abc-456 dans le texte.")
    dois = docs_ingest.extract_dois(text)
    assert "10.1371/journal.pone.0325656" in dois
    assert "10.1234/abc-456" in dois


def test_extract_dois_empty_text_returns_empty(docs_ingest):
    """Anti-générique : aucun texte = aucune DOI fabriquée."""
    dois = docs_ingest.extract_dois("Aucun lien dans ce texte.")
    assert dois == []


def test_extract_dois_no_duplicates(docs_ingest):
    text = "10.1234/abc et 10.1234/abc et 10.1234/ABC"
    dois = docs_ingest.extract_dois(text)
    # Les variantes de casse sont déduplicates par lowercase
    assert len(dois) == 1


# ═════════════════════════════════════════════════════════════════════════
# 3. parse_docx
# ═════════════════════════════════════════════════════════════════════════
def test_parse_docx_chevreuil(docs_ingest):
    p = docs_ingest.DOCS_SCIENCE_ROOT / "chevreuil.docx"
    assert p.exists(), f"docx absent: {p}"
    d = docs_ingest.parse_docx(p)
    assert d["paragraphs_unique"] > 100
    assert d["n_tables"] > 5
    assert all(isinstance(p_, str) for p_ in d["paragraphs"])


def test_parse_docx_invalid_path_raises(docs_ingest, tmp_path):
    with pytest.raises(FileNotFoundError):
        docs_ingest.parse_docx(tmp_path / "non_existent.docx")


# ═════════════════════════════════════════════════════════════════════════
# 4. extract_sections_gov_uni_pr
# ═════════════════════════════════════════════════════════════════════════
def test_extract_sections_three_categories(docs_ingest):
    p = docs_ingest.DOCS_SCIENCE_ROOT / "chevreuil.docx"
    d = docs_ingest.parse_docx(p)
    sections = docs_ingest.extract_sections_gov_uni_pr(d["paragraphs"])
    assert set(sections.keys()) == {"GOV", "UNI", "PR"}
    # Chaque section a au moins 5 paragraphes (rapport substantiel)
    for cat, paras in sections.items():
        assert len(paras) >= 5, f"section {cat} trop courte"


# ═════════════════════════════════════════════════════════════════════════
# 5. normalize_master_tables
# ═════════════════════════════════════════════════════════════════════════
def test_normalize_master_tables_categorizes(docs_ingest):
    p = docs_ingest.DOCS_SCIENCE_ROOT / "chevreuil.docx"
    d = docs_ingest.parse_docx(p)
    nt = docs_ingest.normalize_master_tables(d["tables"])
    assert nt["n_tables_total"] > 0
    # Le rapport CHEVREUIL contient au moins 1 table fiche-ligne
    assert nt["n_fiche_ligne"] >= 1


# ═════════════════════════════════════════════════════════════════════════
# 6. ingest_species_doc
# ═════════════════════════════════════════════════════════════════════════
@pytest.mark.parametrize("sp", [
    "chevreuil", "dindon", "orignal", "ours_noir", "wapiti"])
def test_ingest_species_complete(docs_ingest, tmp_path, sp):
    """Pipeline complet par espèce → registry persisté."""
    reg = tmp_path / "registry_science"
    mt = tmp_path / "registry_master"
    r = docs_ingest.ingest_species_doc(
        species_code=sp,
        registry_root=reg,
        master_tables_root=mt,
        resolve_dois=False,
    )
    assert r["manifest_id"] == "DOC_INGEST_SPECIES_Ω"
    assert r["ordre"] == "N°54-Ω-VAGUE-1"
    assert r["species"] == sp
    assert len(r["docx_sha256"]) == 64
    # Sections présentes
    sec = r["n_paragraphs_per_section"]
    assert sec["GOV"] > 0
    assert sec["UNI"] > 0
    # all_categories_present : True si les 3 sections non vides
    if sec["PR"] > 0:
        assert r["all_categories_present"] is True
    # Fichiers persistés
    species_dir = reg / sp
    assert species_dir.exists()
    for fname in ("paragraphs.json", "sections.json",
                  "dois.json", "master_tables.json", "sha256.txt"):
        assert (species_dir / fname).exists()
    # Master table consolidé
    mtp = mt / f"{sp}_master_table.json"
    assert mtp.exists()
    mt_data = json.loads(mtp.read_text(encoding="utf-8"))
    assert mt_data["species"] == sp
    assert mt_data["docx_sha256"] == r["docx_sha256"]
    # SHA-256 cohérent (5 fichiers)
    assert len(r["registry_files_sha256"]) == 5


def test_ingest_species_invalid_raises(docs_ingest):
    with pytest.raises(ValueError, match="Espèce non valide"):
        docs_ingest.ingest_species_doc("invented_species")


def test_ingest_no_engine_recompute_doctrinal(docs_ingest, tmp_path):
    """Doctrine : ingestion ne touche JAMAIS BR/BP135/super_engines."""
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
    docs_ingest.ingest_species_doc(
        "chevreuil",
        registry_root=tmp_path / "rs",
        master_tables_root=tmp_path / "rmt",
    )
    bp_after = file_sha256()
    br_after = {
        f.name: hashlib.sha256(f.read_bytes()).hexdigest()
        for f in BIO_REACTEUR_DIR.glob("BIO_REACTEUR_*.json")
    }
    assert bp_before == bp_after
    assert br_before == br_after


# ═════════════════════════════════════════════════════════════════════════
# 7. ingest_all_species_vague_1
# ═════════════════════════════════════════════════════════════════════════
def test_vague_1_complete_5_species(docs_ingest, tmp_path, monkeypatch):
    """Pipeline VAGUE 1 → 5 espèces succedeed + audit persisté."""
    from engines.v8_institutional.especes import (
        bio_reacteur_overlay_omega as ovl,
    )
    monkeypatch.setattr(ovl, "AUDITS_ROOT", tmp_path / "audits_v1")
    monkeypatch.setattr(
        docs_ingest, "REGISTRY_SCIENCE_ROOT",
        tmp_path / "rs_v1")
    monkeypatch.setattr(
        docs_ingest, "REGISTRY_MASTER_TABLES_ROOT",
        tmp_path / "rmt_v1")
    r = docs_ingest.ingest_all_species_vague_1()
    assert r["manifest_id"] == "DOC_INGEST_VAGUE_1_Ω"
    assert r["ordre"] == "N°54-Ω-VAGUE-1"
    assert r["n_species_total"] == 5
    assert r["n_species_succeeded"] == 5
    assert r["n_species_failed"] == 0
    assert r["delta_docs_count"] >= 30  # ≥ 6 fichiers × 5 espèces
    assert r["no_engine_recompute_triggered"] is True
    assert r["vague_2_pending"] is True
    # Audit persisté
    ap = r["audit_persisted"]
    assert Path(ap["audit_path"]).exists()
    audit_data = json.loads(
        Path(ap["audit_path"]).read_text(encoding="utf-8"))
    assert audit_data["audit_payload"]["audit_type"] == "DOC_INGEST"
    assert audit_data["audit_payload"]["subtype"] == "SCIENCE_VAGUE_1"


def test_vague_1_subset(docs_ingest, tmp_path, monkeypatch):
    """species_subset → ingestion partielle ciblée."""
    from engines.v8_institutional.especes import (
        bio_reacteur_overlay_omega as ovl,
    )
    monkeypatch.setattr(ovl, "AUDITS_ROOT", tmp_path / "audits_sub")
    monkeypatch.setattr(
        docs_ingest, "REGISTRY_SCIENCE_ROOT",
        tmp_path / "rs_sub")
    monkeypatch.setattr(
        docs_ingest, "REGISTRY_MASTER_TABLES_ROOT",
        tmp_path / "rmt_sub")
    r = docs_ingest.ingest_all_species_vague_1(
        species_subset=["chevreuil", "wapiti"])
    assert r["n_species_total"] == 2
    assert r["n_species_succeeded"] == 2
    assert sorted(r["species_succeeded"]) == ["chevreuil", "wapiti"]


def test_vague_1_invalid_species_subset_raises(docs_ingest):
    with pytest.raises(ValueError, match="Espèces invalides"):
        docs_ingest.ingest_all_species_vague_1(
            species_subset=["chevreuil", "invented"])


# ═════════════════════════════════════════════════════════════════════════
# 8. list_registry_science + get_master_table
# ═════════════════════════════════════════════════════════════════════════
def test_list_registry_science_empty_when_no_dir(
        docs_ingest, tmp_path, monkeypatch):
    monkeypatch.setattr(
        docs_ingest, "REGISTRY_SCIENCE_ROOT", tmp_path / "empty")
    r = docs_ingest.list_registry_science()
    assert r["n_species"] == 0
    assert r["species"] == []


def test_list_registry_after_ingestion(docs_ingest, tmp_path, monkeypatch):
    from engines.v8_institutional.especes import (
        bio_reacteur_overlay_omega as ovl,
    )
    monkeypatch.setattr(ovl, "AUDITS_ROOT", tmp_path / "audits_lr")
    monkeypatch.setattr(
        docs_ingest, "REGISTRY_SCIENCE_ROOT",
        tmp_path / "rs_lr")
    monkeypatch.setattr(
        docs_ingest, "REGISTRY_MASTER_TABLES_ROOT",
        tmp_path / "rmt_lr")
    docs_ingest.ingest_all_species_vague_1(
        species_subset=["chevreuil", "wapiti"])
    r = docs_ingest.list_registry_science()
    assert r["n_species"] == 2
    species_names = {s["species"] for s in r["species"]}
    assert species_names == {"chevreuil", "wapiti"}


def test_get_master_table_after_ingestion(
        docs_ingest, tmp_path, monkeypatch):
    from engines.v8_institutional.especes import (
        bio_reacteur_overlay_omega as ovl,
    )
    monkeypatch.setattr(ovl, "AUDITS_ROOT", tmp_path / "audits_gmt")
    monkeypatch.setattr(
        docs_ingest, "REGISTRY_SCIENCE_ROOT",
        tmp_path / "rs_gmt")
    monkeypatch.setattr(
        docs_ingest, "REGISTRY_MASTER_TABLES_ROOT",
        tmp_path / "rmt_gmt")
    docs_ingest.ingest_all_species_vague_1(species_subset=["orignal"])
    mt = docs_ingest.get_master_table("orignal")
    assert mt["species"] == "orignal"
    assert mt["ordre"] == "N°54-Ω-VAGUE-1"
    assert "validation_BCE_4X" in mt
    assert "tables_GOV" in mt
    assert "tables_UNI" in mt
    assert "tables_PR" in mt
    assert "dois" in mt


def test_get_master_table_missing_raises(docs_ingest, tmp_path,
                                         monkeypatch):
    monkeypatch.setattr(
        docs_ingest, "REGISTRY_MASTER_TABLES_ROOT",
        tmp_path / "rmt_missing")
    with pytest.raises(FileNotFoundError):
        docs_ingest.get_master_table("chevreuil")

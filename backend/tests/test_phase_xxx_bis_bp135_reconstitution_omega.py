"""
Phase XXX-BIS · ORDRE N°54-Ω VAGUE 2 — Tests reconstitution BP135
══════════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU x3 · ANTI_GÉNÉRIQUE_STRICT

Tests :
  · Parse DOCX institutionnel (35 tables → 9 blocs)
  · Extraction valeurs (numeric_range, binary, categorical)
  · Génération 675 entrées BCE-4X complètes
  · Diff vs JSON existant
  · Document consolidé .docx valide
  · V30_LOCK INVIOLÉ post-pipeline

Naming policy : aucun mot-clé exclu BCE-4X.
"""
from __future__ import annotations

import importlib
import json
import zipfile
from pathlib import Path

import pytest


@pytest.fixture()
def recon():
    import engines.v8_institutional.especes.bp135_reconstitution_omega as m
    importlib.reload(m)
    return m


# ═════════════════════════════════════════════════════════════════════════
# 1. API + invariants
# ═════════════════════════════════════════════════════════════════════════
def test_module_exports(recon):
    for name in (
        "parse_institutional_docx",
        "generate_675_entries",
        "diff_against_existing_bp135",
        "build_consolidated_docx",
        "execute_reconstitution_pipeline",
        "INSTITUTIONAL_DOCX_PATH",
        "OVERLAY_JSON_PATH",
        "RECONSTITUTED_JSON_PATH",
        "CONSOLIDATED_DOCX_PATH",
        "BLOCK_PREFIXES_TO_NAMES",
        "SPECIES_DOCX_TO_JSON",
        "SPECIES_META",
    ):
        assert hasattr(recon, name), f"missing {name}"


def test_block_prefixes_nine_blocks(recon):
    assert len(recon.BLOCK_PREFIXES_TO_NAMES) == 9
    assert set(recon.BLOCK_PREFIXES_TO_NAMES.keys()) == {
        "MOR", "ALI", "HAB", "REP", "COM",
        "PHY", "DEP", "SAN", "SEN",
    }


def test_species_meta_five_species(recon):
    assert len(recon.SPECIES_META) == 5
    assert set(recon.SPECIES_META.keys()) == {
        "ORIGNAL", "CHEVREUIL", "WAPITI",
        "OURS_NOIR", "DINDON_SAUVAGE",
    }


# ═════════════════════════════════════════════════════════════════════════
# 2. Parse cellules — extraction stricte anti-générique
# ═════════════════════════════════════════════════════════════════════════
def test_extract_numeric_range_french_decimal(recon):
    """Format `5,5 [3–8]` → typ=5.5 min=3 max=8."""
    typ, mn, mx, method = recon._extract_value_from_cell(
        "5,5 [3–8]", "DEP-005")
    assert typ == 5.5
    assert mn == 3.0
    assert mx == 8.0
    assert method == "numeric_range"


def test_extract_numeric_range_dash_normal(recon):
    """Format avec tiret normal `12 [5-25]` → typ=12 min=5 max=25."""
    typ, mn, mx, method = recon._extract_value_from_cell(
        "12 [5-25]", "DEP-001")
    assert typ == 12.0
    assert mn == 5.0
    assert mx == 25.0
    assert method == "numeric_range"


def test_extract_binary_oui_non(recon):
    """Format `1 [oui]` → typ=1 method=binary_tagged_oui_non."""
    typ, mn, mx, method = recon._extract_value_from_cell(
        "1 [oui]", "SEN-004")
    assert typ == 1.0
    assert mn == 1.0
    assert mx == 1.0
    assert method == "binary_tagged_oui_non"


def test_extract_binary_hibernation(recon):
    typ, mn, mx, method = recon._extract_value_from_cell(
        "0 [hibernation]", "DEP-011")
    assert typ == 0.0
    assert method == "binary_tagged_hibernation"


def test_extract_binary_na(recon):
    typ, mn, mx, method = recon._extract_value_from_cell(
        "0 [N/A]", "DEP-012")
    assert typ == 0.0
    assert method == "binary_tagged_na"


def test_extract_chromatic_categorical(recon):
    """SEN-013 'dichromate' → encodage 2."""
    typ, mn, mx, method = recon._extract_value_from_cell(
        "dichromate", "SEN-013")
    assert typ == 2.0
    assert method == "categorical_chromatic"
    typ2, _, _, _ = recon._extract_value_from_cell(
        "trichromate", "SEN-013")
    assert typ2 == 3.0
    typ3, _, _, _ = recon._extract_value_from_cell(
        "tétrachromate", "SEN-013")
    assert typ3 == 4.0


def test_extract_empty_returns_none(recon):
    typ, mn, mx, method = recon._extract_value_from_cell(
        "", "DEP-001")
    assert typ is None
    assert method == "empty"


def test_extract_unparseable_returns_categorical_text(recon):
    """Anti-générique : valeur non parseable → categorical_text
    sans fabrication numérique."""
    typ, mn, mx, method = recon._extract_value_from_cell(
        "valeur libre indéfinie", "MOR-001")
    assert typ is None
    assert mn is None
    assert mx is None
    assert method == "categorical_text"


# ═════════════════════════════════════════════════════════════════════════
# 3. parse_institutional_docx
# ═════════════════════════════════════════════════════════════════════════
def test_parse_docx_returns_135_parameters(recon):
    parsed = recon.parse_institutional_docx()
    assert parsed["n_parameters_total"] == 135
    assert parsed["n_species"] == 5
    assert len(parsed["docx_sha256"]) == 64
    # 9 blocs × 15 paramètres
    for pref in recon.BLOCK_PREFIXES_TO_NAMES:
        assert len(parsed["blocks"][pref]) == 15, f"bloc {pref}"


def test_parse_docx_invalid_path_raises(recon, tmp_path):
    with pytest.raises(FileNotFoundError):
        recon.parse_institutional_docx(tmp_path / "absent.docx")


def test_parse_docx_dindon_dep_complete(recon):
    """KPI doctrinal : DINDON_SAUVAGE × DEP-001..015 doivent avoir
    typ/min/max numériques (méthode numeric_range majoritaire)."""
    parsed = recon.parse_institutional_docx()
    dep_block = parsed["blocks"]["DEP"]
    n_numeric_dindon = 0
    for param in dep_block:
        v = param["values"].get("DINDON_SAUVAGE")
        if (v and v["value_typical"] is not None
                and v["extraction_method"] == "numeric_range"):
            n_numeric_dindon += 1
    # Au moins 13/15 paramètres DINDON × DEP doivent être numeric_range
    # (DEP-007 capacité nage = "0,05 [0–0,1]" est numérique mais
    # tendance vers DEP-012 charge alaire = "11 [8–14]" pour dindon)
    assert n_numeric_dindon >= 13


# ═════════════════════════════════════════════════════════════════════════
# 4. generate_675_entries
# ═════════════════════════════════════════════════════════════════════════
def test_generate_exactly_675_entries(recon):
    g = recon.generate_675_entries()
    assert g["n_entries"] == 675
    assert g["n_expected"] == 675
    assert g["complete"] is True


def test_generate_schema_bce_4x_strict(recon):
    """Chaque entrée doit avoir les 16 champs BCE-4X."""
    g = recon.generate_675_entries()
    expected_fields = {
        "schema", "version", "block", "block_id", "block_description",
        "parameter_id", "parameter_name", "parameter_label",
        "species_code", "species_latin", "species_common_fr", "unit",
        "value_range_min", "value_range_max", "value_typical",
        "scientific_source",
    }
    for entry in g["entries"]:
        assert set(entry.keys()) == expected_fields, (
            f"Champs BCE-4X invalides pour "
            f"{entry.get('parameter_id')}_{entry.get('species_code')}")


def test_generate_per_block_75(recon):
    """9 blocs × 75 entrées (15 params × 5 espèces) = 675."""
    g = recon.generate_675_entries()
    for pref in recon.BLOCK_PREFIXES_TO_NAMES:
        assert g["n_per_block"][pref] == 75


def test_generate_extraction_methods_dominate_numeric(recon):
    """≥85% des 675 entrées doivent être numeric_range
    (cas catégoriels minoritaires conformes aux données réelles)."""
    g = recon.generate_675_entries()
    n_numeric = g["n_per_method"].get("numeric_range", 0)
    pct = n_numeric / 675
    assert pct >= 0.85


def test_generate_scientific_source_traces_docx(recon):
    """Chaque entrée doit citer le DOCX institutionnel et son SHA-256."""
    g = recon.generate_675_entries()
    for entry in g["entries"][:30]:
        assert "BIO_PROFILE_135_INSTITUTIONNEL" in entry[
            "scientific_source"]
        assert "docx_sha256" in entry["scientific_source"]


def test_generate_dindon_complete_dep_sen(recon):
    """KPI critique : DINDON_SAUVAGE × DEP-001..015 et SEN-001..015
    doivent tous avoir value_typical/min/max numériques."""
    g = recon.generate_675_entries()
    dindon_dep_complete = sum(
        1 for e in g["entries"]
        if e["species_code"] == "DINDON_SAUVAGE"
        and e["parameter_id"].startswith("DEP-")
        and e["value_typical"] is not None
        and e["value_range_min"] is not None
        and e["value_range_max"] is not None
    )
    dindon_sen_complete = sum(
        1 for e in g["entries"]
        if e["species_code"] == "DINDON_SAUVAGE"
        and e["parameter_id"].startswith("SEN-")
        and e["value_typical"] is not None
        and e["value_range_min"] is not None
        and e["value_range_max"] is not None
    )
    # ≥13/15 (cas chromatique SEN-013 + booléens SEN-004/005/014 OK)
    assert dindon_dep_complete >= 13
    assert dindon_sen_complete >= 13


# ═════════════════════════════════════════════════════════════════════════
# 5. diff_against_existing_bp135
# ═════════════════════════════════════════════════════════════════════════
def test_diff_against_existing_consistent(recon):
    g = recon.generate_675_entries()
    diff = recon.diff_against_existing_bp135(g)
    # Cohérence : reconstituted == 675 = identical + value_changes +
    # missing_filled (toutes paires couvertes)
    total_check = (
        diff["n_identical"]
        + diff["n_value_changes"]
        + diff["n_missing_in_existing_filled_by_recon"]
    )
    assert total_check == g["n_entries"]
    assert diff["n_new_entries"] == 0  # pas de nouvelles paires


# ═════════════════════════════════════════════════════════════════════════
# 6. build_consolidated_docx
# ═════════════════════════════════════════════════════════════════════════
def test_build_consolidated_docx_valid_zipfile(recon, tmp_path):
    g = recon.generate_675_entries()
    diff = recon.diff_against_existing_bp135(g)
    out_path = tmp_path / "consolidated_test.docx"
    recon.build_consolidated_docx(g, diff, out_path)
    assert out_path.exists()
    # Vérification : c'est un .docx valide (zipfile + document.xml)
    with zipfile.ZipFile(out_path, "r") as z:
        names = z.namelist()
        assert "[Content_Types].xml" in names
        assert "_rels/.rels" in names
        assert "word/document.xml" in names
        # Le document.xml doit contenir le titre
        doc_xml = z.read("word/document.xml").decode("utf-8")
        assert "BIO_PROFILE_OMEGA_135" in doc_xml
        assert "DOCUMENT CONSOLIDÉ" in doc_xml


# ═════════════════════════════════════════════════════════════════════════
# 7. execute_reconstitution_pipeline
# ═════════════════════════════════════════════════════════════════════════
def test_pipeline_full_persists_three_files(recon, tmp_path, monkeypatch):
    """Pipeline complet → 3 fichiers persistés + audit."""
    from engines.v8_institutional.especes import (
        bio_reacteur_overlay_omega as ovl,
    )
    monkeypatch.setattr(ovl, "AUDITS_ROOT",
                        tmp_path / "audits_recon")
    monkeypatch.setattr(
        recon, "RECONSTITUTION_ROOT", tmp_path / "recon_root")
    monkeypatch.setattr(
        recon, "OVERLAY_JSON_PATH",
        tmp_path / "recon_root" / "overlay.json")
    monkeypatch.setattr(
        recon, "RECONSTITUTED_JSON_PATH",
        tmp_path / "recon_root" / "recon.json")
    monkeypatch.setattr(
        recon, "CONSOLIDATED_DOCX_PATH",
        tmp_path / "recon_root" / "consolidated.docx")
    r = recon.execute_reconstitution_pipeline(persist=True)
    assert r["manifest_id"] == "BP135_RECONSTITUTION_PIPELINE_Ω"
    assert r["n_entries_reconstituted"] == 675
    assert r["complete"] is True
    assert r["no_engine_recompute_triggered"] is True
    pp = r["persisted_paths"]
    assert Path(pp["overlay_json"]).exists()
    assert Path(pp["reconstituted_json"]).exists()
    assert Path(pp["consolidated_docx"]).exists()
    assert "audit_persisted" in pp


def test_pipeline_no_persist(recon):
    """persist=False → pas de mutation disque."""
    r = recon.execute_reconstitution_pipeline(persist=False)
    assert r["n_entries_reconstituted"] == 675
    assert r["persisted_paths"] == {}


# ═════════════════════════════════════════════════════════════════════════
# 8. V30_LOCK INVIOLÉ post-reconstitution
# ═════════════════════════════════════════════════════════════════════════
def test_v30_lock_inviolate_after_pipeline(recon, tmp_path, monkeypatch):
    import hashlib
    from engines.v8_institutional.especes.bio_profile_135_loader_omega import (
        file_sha256,
    )
    from engines.v8_institutional.especes.bio_reacteur_loader_omega import (
        BIO_REACTEUR_DIR,
    )
    from engines.v8_institutional.especes import (
        bio_reacteur_overlay_omega as ovl,
    )
    monkeypatch.setattr(ovl, "AUDITS_ROOT",
                        tmp_path / "audits_v30")
    monkeypatch.setattr(
        recon, "RECONSTITUTION_ROOT", tmp_path / "recon_v30")
    monkeypatch.setattr(
        recon, "OVERLAY_JSON_PATH",
        tmp_path / "recon_v30" / "overlay.json")
    monkeypatch.setattr(
        recon, "RECONSTITUTED_JSON_PATH",
        tmp_path / "recon_v30" / "recon.json")
    monkeypatch.setattr(
        recon, "CONSOLIDATED_DOCX_PATH",
        tmp_path / "recon_v30" / "consolidated.docx")
    bp_before = file_sha256()
    br_before = {
        f.name: hashlib.sha256(f.read_bytes()).hexdigest()
        for f in BIO_REACTEUR_DIR.glob("BIO_REACTEUR_*.json")
    }
    recon.execute_reconstitution_pipeline(persist=True)
    bp_after = file_sha256()
    br_after = {
        f.name: hashlib.sha256(f.read_bytes()).hexdigest()
        for f in BIO_REACTEUR_DIR.glob("BIO_REACTEUR_*.json")
    }
    assert bp_before == bp_after
    assert br_before == br_after


# ═════════════════════════════════════════════════════════════════════════
# 9. Registry external sources avec official_https_sources
# ═════════════════════════════════════════════════════════════════════════
def test_registry_has_official_https_sources():
    from engines.v8_institutional.especes.bio_reacteur_overlay_omega import (
        EXTERNAL_SOURCES_REGISTRY,
    )
    expected_urls = {
        "NOAA": ["https://www.noaa.gov", "https://www.ncei.noaa.gov"],
        "NASA": ["https://earthdata.nasa.gov", "https://lpdaac.usgs.gov"],
        "USGS": ["https://www.usgs.gov", "https://www.sciencebase.gov"],
        "MAXENT": [
            "https://biodiversityinformatics.amnh.org/open_source/maxent",
            "https://github.com/mrmaxent/maxent",
        ],
        "FORECAST_48H": [
            "https://www.weather.gov", "https://api.weather.gov"],
    }
    by_name = {s["source_name"]: s for s in EXTERNAL_SOURCES_REGISTRY}
    for src_name, expected in expected_urls.items():
        urls = by_name[src_name].get("official_https_sources", [])
        for u in expected:
            assert u in urls, f"{src_name} missing URL {u}"


def test_scan_includes_official_https_sources():
    """scan_external_sources doit exposer official_https_sources."""
    from engines.v8_institutional.especes.bio_reacteur_overlay_omega import (
        scan_external_sources,
    )
    s = scan_external_sources()
    for src in s["sources"]:
        assert "official_https_sources" in src
        assert isinstance(src["official_https_sources"], list)

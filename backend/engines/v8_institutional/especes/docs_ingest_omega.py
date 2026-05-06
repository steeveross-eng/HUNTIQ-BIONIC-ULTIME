"""
docs_ingest_omega.py — ORDRE N°54-Ω VAGUE 1
═══════════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU x3 · ANTI_GÉNÉRIQUE_STRICT

INGESTION DOCUMENTAIRE INSTITUTIONNELLE — VAGUE 1 (5 ESPÈCES)
  · Extraction GOV / UNI / PR à partir des rapports scientifiques DOCX
  · Extraction DOI (regex + résolution HTTP 200 facultative)
  · Normalisation tableaux maîtres
  · Persistance registry_science/<espece>/ + registry_master_tables/
  · SHA-256 persisté (audit longitudinal)

GARDE-FOUS DOCTRINAUX :
  · AUCUN recalcul moteur (super_engines / BR / BP135)
  · AUCUN flip available=True (hooks externes restent en attente)
  · Read-only sur les .docx (lecture stricte)
  · Anti-générique : aucune fabrication de DOI
═══════════════════════════════════════════════════════════════════════════
"""
from __future__ import annotations

import hashlib
import json
import logging
import re
import time
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from xml.etree import ElementTree as ET

logger = logging.getLogger("docs_ingest_omega")

# ═════════════════════════════════════════════════════════════════════════
# Constantes doctrinales
# ═════════════════════════════════════════════════════════════════════════
DOCS_SCIENCE_ROOT = Path("/app/backend/data/docs/science")
REGISTRY_SCIENCE_ROOT = Path("/app/backend/data/registry_science")
REGISTRY_MASTER_TABLES_ROOT = Path(
    "/app/backend/data/registry_master_tables")

WORDPROCESSING_NS = (
    "http://schemas.openxmlformats.org/wordprocessingml/2006/main")
NS = {"w": WORDPROCESSING_NS}

ESPECES_VAGUE_1 = [
    "chevreuil", "dindon", "orignal", "ours_noir", "wapiti",
]

SOURCE_CATEGORIES = ("GOV", "UNI", "PR")

# Regex DOI standard (10.NNNN[.NNN]/.+)
RE_DOI = re.compile(
    r"\b(10\.\d{4,9}/[-._;()/:A-Z0-9]+)", re.IGNORECASE)

# Markers de sections (multi-format pour robustesse)
SECTION_MARKERS = {
    "GOV": [
        re.compile(r"^\s*2\.1\s+GOV\b", re.I),
        re.compile(r"SECTION\s+GOV", re.I),
    ],
    "UNI": [
        re.compile(r"^\s*2\.2\s+UNI\b", re.I),
        re.compile(r"SECTION\s+UNI", re.I),
    ],
    "PR": [
        re.compile(r"^\s*2\.3\s+PR\b", re.I),
        re.compile(r"SECTION\s+PR", re.I),
    ],
}


# ═════════════════════════════════════════════════════════════════════════
# 1. Lecture .docx (paragraphes + tableaux)
# ═════════════════════════════════════════════════════════════════════════
def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _para_text(p_elem: ET.Element) -> str:
    """Concatène tous les <w:t> d'un paragraphe."""
    return "".join(
        t.text or ""
        for t in p_elem.iter(f"{{{WORDPROCESSING_NS}}}t"))


def parse_docx(docx_path: Path) -> Dict[str, Any]:
    """Lit un .docx et retourne {paragraphs, tables}.

    paragraphs : liste de strings (texte non vide uniquement)
    tables     : liste de listes de listes (lignes × cellules)
    """
    if not docx_path.exists():
        raise FileNotFoundError(f"docx introuvable : {docx_path}")
    with zipfile.ZipFile(docx_path, "r") as z:
        xml_str = z.read("word/document.xml").decode("utf-8")
    root = ET.fromstring(xml_str)
    body = root.find(f"{{{WORDPROCESSING_NS}}}body")
    if body is None:
        return {"paragraphs": [], "tables": []}

    paragraphs: List[str] = []
    tables: List[List[List[str]]] = []
    p_tag = f"{{{WORDPROCESSING_NS}}}p"
    tbl_tag = f"{{{WORDPROCESSING_NS}}}tbl"
    tr_tag = f"{{{WORDPROCESSING_NS}}}tr"
    tc_tag = f"{{{WORDPROCESSING_NS}}}tc"

    for child in body.iter():
        if child.tag == p_tag:
            txt = _para_text(child).strip()
            if txt:
                paragraphs.append(txt)
        elif child.tag == tbl_tag:
            rows = []
            for tr in child.iter(tr_tag):
                cells = []
                for tc in tr.iter(tc_tag):
                    cell_text = " ".join(
                        _para_text(p).strip()
                        for p in tc.iter(p_tag)
                        if _para_text(p).strip()
                    )
                    cells.append(cell_text)
                if cells:
                    rows.append(cells)
            if rows:
                tables.append(rows)

    # Dédupliquer les paragraphes qui apparaissent dans les tables
    # (les tables font partie du body : leurs <w:p> sont aussi capturés)
    table_paragraphs = set()
    for tbl in tables:
        for row in tbl:
            for cell in row:
                for line in cell.split(" "):
                    if line.strip():
                        table_paragraphs.add(line.strip())

    paragraphs_unique = [
        p for p in paragraphs if p not in table_paragraphs]

    return {
        "paragraphs": paragraphs_unique,
        "paragraphs_total": len(paragraphs),
        "paragraphs_unique": len(paragraphs_unique),
        "tables": tables,
        "n_tables": len(tables),
    }


# ═════════════════════════════════════════════════════════════════════════
# 2. Extraction sections GOV / UNI / PR
# ═════════════════════════════════════════════════════════════════════════
def extract_sections_gov_uni_pr(
    paragraphs: List[str],
) -> Dict[str, List[str]]:
    """Découpe la liste de paragraphes en sections GOV / UNI / PR.

    La section courante reste active jusqu'à ce qu'un autre marqueur
    soit rencontré.
    """
    sections: Dict[str, List[str]] = {
        "GOV": [], "UNI": [], "PR": [],
    }
    current = None
    for p in paragraphs:
        for cat, patterns in SECTION_MARKERS.items():
            if any(rx.search(p) for rx in patterns):
                current = cat
                break
        if current and not _is_section_marker(p):
            sections[current].append(p)
    return sections


def _is_section_marker(p: str) -> bool:
    for patterns in SECTION_MARKERS.values():
        if any(rx.search(p) for rx in patterns):
            return True
    return False


# ═════════════════════════════════════════════════════════════════════════
# 3. Extraction DOI (anti-générique — DOI réels uniquement)
# ═════════════════════════════════════════════════════════════════════════
def extract_dois(text_or_paragraphs: Any) -> List[str]:
    """Extrait toutes les DOI uniques (10.NNNN/...) trouvées dans le texte.

    Anti-générique : ne fabrique JAMAIS de DOI. Si aucune trouvée → liste vide.
    """
    if isinstance(text_or_paragraphs, list):
        text = "\n".join(text_or_paragraphs)
    else:
        text = str(text_or_paragraphs)
    matches = RE_DOI.findall(text)
    # Normalisation (lowercase + suppression caractères de fin parasitaires)
    seen = set()
    out: List[str] = []
    for m in matches:
        doi = m.strip().rstrip(".,;:)")
        doi_low = doi.lower()
        if doi_low not in seen:
            seen.add(doi_low)
            out.append(doi)
    return out


def resolve_dois_http_200(
    dois: List[str], timeout_s: int = 5,
    max_check: int = 20,
) -> Dict[str, Any]:
    """Tente de résoudre chaque DOI via https://doi.org/<doi>.

    Anti-générique strict :
      · http_status retourné réellement (pas de fabrication)
      · timeout / network error → status_code=None + reason="network_error"
      · Limite max_check pour éviter blocage en CI

    Returns:
      {dois_total, dois_checked, dois_http_200, dois_http_other,
       dois_network_error, results_per_doi}
    """
    import urllib.request
    import urllib.error
    results: List[Dict[str, Any]] = []
    n_200 = 0
    n_other = 0
    n_network_err = 0
    checked = dois[:max_check]
    for doi in checked:
        url = f"https://doi.org/{doi}"
        record = {
            "doi": doi, "url": url,
            "http_status": None, "reason": None,
        }
        try:
            req = urllib.request.Request(
                url, method="HEAD",
                headers={"User-Agent": "BCE-4X-DOC-INGEST/1.0"})
            with urllib.request.urlopen(req, timeout=timeout_s) as resp:
                record["http_status"] = resp.status
                if resp.status == 200:
                    n_200 += 1
                else:
                    n_other += 1
        except urllib.error.HTTPError as e:
            record["http_status"] = e.code
            record["reason"] = f"http_error_{e.code}"
            n_other += 1
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            record["reason"] = f"network_error::{str(e)[:60]}"
            n_network_err += 1
        results.append(record)
    return {
        "dois_total": len(dois),
        "dois_checked": len(checked),
        "dois_http_200": n_200,
        "dois_http_other": n_other,
        "dois_network_error": n_network_err,
        "results_per_doi": results,
        "anti_generique_strict": True,
        "max_check_applied": max_check,
        "timeout_s": timeout_s,
    }


# ═════════════════════════════════════════════════════════════════════════
# 4. Normalisation tableaux maîtres
# ═════════════════════════════════════════════════════════════════════════
def normalize_master_tables(
    tables: List[List[List[str]]],
) -> Dict[str, Any]:
    """Normalise les tableaux extraits en structure institutionnelle.

    Détection automatique :
      · Tables Institution/Titre/Année/Portée/Lien → GOV/PR
      · Tables Auteurs/Titre/Année/Revue/DOI       → UNI
      · Tables Champ/Valeur                         → fiche_ligne_*
    """
    by_category = {"GOV": [], "UNI": [], "PR": [], "FICHE_LIGNE": [],
                   "AUTRES": []}
    raw_tables = []

    for idx, tbl in enumerate(tables):
        if not tbl:
            continue
        header = [c.strip() for c in tbl[0]]
        rows = [[c.strip() for c in row] for row in tbl[1:]]
        record = {
            "table_index": idx,
            "header": header,
            "rows": rows,
            "n_rows": len(rows),
        }
        raw_tables.append(record)

        header_lower = [h.lower() for h in header]
        if (
            "institution" in header_lower
            and "titre" in " ".join(header_lower).lower()
            and any("lien" in h or "référence" in h for h in header_lower)
        ):
            # Heuristique : GOV (Institution / Titre / Lien)
            by_category["GOV"].append(record)
        elif (
            "auteurs" in header_lower
            and any("doi" in h for h in header_lower)
        ):
            by_category["UNI"].append(record)
        elif "organisation" in header_lower:
            by_category["PR"].append(record)
        elif (
            len(header) == 2
            and header_lower[0] in ("champ", "field")
        ):
            # Fiche ligne (Champ/Valeur)
            data = {row[0]: row[1] for row in rows if len(row) >= 2}
            by_category["FICHE_LIGNE"].append({
                "table_index": idx,
                "fiche_data": data,
                "n_fields": len(data),
            })
        elif (
            "catégorie" in header_lower
            or "categorie" in header_lower
        ):
            # Tableau de conformité
            by_category["AUTRES"].append(record)
        else:
            by_category["AUTRES"].append(record)

    return {
        "n_tables_total": len(raw_tables),
        "n_gov": len(by_category["GOV"]),
        "n_uni": len(by_category["UNI"]),
        "n_pr": len(by_category["PR"]),
        "n_fiche_ligne": len(by_category["FICHE_LIGNE"]),
        "n_autres": len(by_category["AUTRES"]),
        "by_category": by_category,
        "raw_tables": raw_tables,
    }


# ═════════════════════════════════════════════════════════════════════════
# 5. Pipeline d'ingestion par espèce
# ═════════════════════════════════════════════════════════════════════════
def ingest_species_doc(
    species_code: str,
    docs_root: Optional[Path] = None,
    registry_root: Optional[Path] = None,
    master_tables_root: Optional[Path] = None,
    resolve_dois: bool = False,
) -> Dict[str, Any]:
    """Pipeline complet d'ingestion pour une espèce de la VAGUE 1.

    Étapes :
      1. Lecture .docx (paragraphes + tables)
      2. Extraction sections GOV / UNI / PR
      3. Extraction DOI (+ résolution HTTP optionnelle)
      4. Normalisation tableaux maîtres
      5. Persistance dans registry_science/<espece>/ +
         registry_master_tables/<espece>_master_table.json
      6. Hash SHA-256 (du .docx + des registries persistés)

    AUCUN recalcul moteur. Read-only sur le .docx.
    """
    if species_code not in ESPECES_VAGUE_1:
        raise ValueError(
            f"Espèce non valide pour VAGUE 1: {species_code}. "
            f"Attendues: {ESPECES_VAGUE_1}")

    docs_root = docs_root or DOCS_SCIENCE_ROOT
    registry_root = registry_root or REGISTRY_SCIENCE_ROOT
    master_tables_root = (
        master_tables_root or REGISTRY_MASTER_TABLES_ROOT)

    docx_path = docs_root / f"{species_code}.docx"
    if not docx_path.exists():
        raise FileNotFoundError(
            f".docx absent pour {species_code} : {docx_path}")

    t0 = time.time()
    docx_sha256 = _file_sha256(docx_path)
    parsed = parse_docx(docx_path)
    sections = extract_sections_gov_uni_pr(parsed["paragraphs"])
    full_text = "\n".join(parsed["paragraphs"])
    dois = extract_dois(full_text + "\n" +
                        json.dumps(parsed["tables"], default=str))

    doi_resolution = None
    if resolve_dois and dois:
        doi_resolution = resolve_dois_http_200(dois)

    master_tables = normalize_master_tables(parsed["tables"])

    # Persistance
    out_species_dir = registry_root / species_code
    out_species_dir.mkdir(parents=True, exist_ok=True)
    paragraphs_file = out_species_dir / "paragraphs.json"
    sections_file = out_species_dir / "sections.json"
    dois_file = out_species_dir / "dois.json"
    tables_file = out_species_dir / "master_tables.json"
    sha256_file = out_species_dir / "sha256.txt"

    paragraphs_file.write_text(
        json.dumps({
            "species": species_code,
            "ordre": "N°54-Ω-VAGUE-1",
            "ingested_at_utc": _utc_now(),
            "n_paragraphs": len(parsed["paragraphs"]),
            "paragraphs": parsed["paragraphs"],
        }, ensure_ascii=False, indent=2),
        encoding="utf-8")
    sections_file.write_text(
        json.dumps({
            "species": species_code,
            "ordre": "N°54-Ω-VAGUE-1",
            "n_paragraphs_per_section": {
                k: len(v) for k, v in sections.items()
            },
            "sections": sections,
        }, ensure_ascii=False, indent=2),
        encoding="utf-8")
    dois_file.write_text(
        json.dumps({
            "species": species_code,
            "ordre": "N°54-Ω-VAGUE-1",
            "n_dois": len(dois),
            "dois": dois,
            "resolution": doi_resolution,
            "anti_generique_strict": True,
        }, ensure_ascii=False, indent=2),
        encoding="utf-8")
    tables_file.write_text(
        json.dumps({
            "species": species_code,
            "ordre": "N°54-Ω-VAGUE-1",
            "summary": {
                k: v for k, v in master_tables.items()
                if k.startswith("n_")
            },
            "master_tables": master_tables,
        }, ensure_ascii=False, indent=2),
        encoding="utf-8")

    # Tableau maître consolidé (registry_master_tables)
    master_tables_root.mkdir(parents=True, exist_ok=True)
    master_table_path = (
        master_tables_root / f"{species_code}_master_table.json")
    master_table_payload = {
        "species": species_code,
        "ordre": "N°54-Ω-VAGUE-1",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "ingested_at_utc": _utc_now(),
        "docx_source": str(docx_path),
        "docx_sha256": docx_sha256,
        "validation_BCE_4X": {
            "sources_categories_required": list(SOURCE_CATEGORIES),
            "n_paragraphs_per_section": {
                k: len(v) for k, v in sections.items()
            },
            "all_categories_present": all(
                len(sections[c]) > 0 for c in SOURCE_CATEGORIES),
        },
        "n_dois_extracted": len(dois),
        "dois": dois,
        "tables_summary": {
            k: v for k, v in master_tables.items()
            if k.startswith("n_")
        },
        "tables_GOV": master_tables["by_category"]["GOV"],
        "tables_UNI": master_tables["by_category"]["UNI"],
        "tables_PR": master_tables["by_category"]["PR"],
    }
    master_table_path.write_text(
        json.dumps(master_table_payload, ensure_ascii=False, indent=2),
        encoding="utf-8")

    # SHA-256 des fichiers persistés (audit longitudinal)
    persisted_files = {
        "paragraphs.json": _file_sha256(paragraphs_file),
        "sections.json": _file_sha256(sections_file),
        "dois.json": _file_sha256(dois_file),
        "master_tables.json": _file_sha256(tables_file),
        "master_table_consolidated.json": _file_sha256(
            master_table_path),
    }
    sha256_file.write_text(
        json.dumps({
            "species": species_code,
            "ordre": "N°54-Ω-VAGUE-1",
            "docx_source_sha256": docx_sha256,
            "registry_files_sha256": persisted_files,
            "computed_at_utc": _utc_now(),
        }, ensure_ascii=False, indent=2),
        encoding="utf-8")

    return {
        "manifest_id": "DOC_INGEST_SPECIES_Ω",
        "ordre": "N°54-Ω-VAGUE-1",
        "species": species_code,
        "docx_source": str(docx_path),
        "docx_sha256": docx_sha256,
        "n_paragraphs": len(parsed["paragraphs"]),
        "n_paragraphs_per_section": {
            k: len(v) for k, v in sections.items()
        },
        "n_dois_extracted": len(dois),
        "doi_resolution": doi_resolution,
        "tables_summary": {
            k: v for k, v in master_tables.items()
            if k.startswith("n_")
        },
        "registry_files_sha256": persisted_files,
        "registry_dir": str(out_species_dir),
        "master_table_path": str(master_table_path),
        "all_categories_present": all(
            len(sections[c]) > 0 for c in SOURCE_CATEGORIES),
        "elapsed_s": round(time.time() - t0, 3),
        "computed_at_utc": _utc_now(),
        "v30_lock": "INVIOLÉ",
    }


# ═════════════════════════════════════════════════════════════════════════
# 6. Pipeline VAGUE 1 (5 espèces)
# ═════════════════════════════════════════════════════════════════════════
def ingest_all_species_vague_1(
    species_subset: Optional[List[str]] = None,
    resolve_dois: bool = False,
) -> Dict[str, Any]:
    """Exécute l'ingestion documentaire VAGUE 1 sur les 5 espèces.

    AUCUN recalcul moteur. Persistance complète + audit DOC_INGEST.
    """
    species_to_process = species_subset or ESPECES_VAGUE_1
    invalid = [s for s in species_to_process if s not in ESPECES_VAGUE_1]
    if invalid:
        raise ValueError(
            f"Espèces invalides : {invalid}. "
            f"Valides : {ESPECES_VAGUE_1}")

    t0 = time.time()
    results: Dict[str, Any] = {}
    success: List[str] = []
    failed: List[Dict[str, Any]] = []
    for sp in species_to_process:
        try:
            r = ingest_species_doc(sp, resolve_dois=resolve_dois)
            results[sp] = r
            success.append(sp)
        except Exception as e:
            failed.append({
                "species": sp,
                "error": str(e)[:300],
            })

    # Hash agrégé doc-level + registry-level
    docs_sha256_combined = {}
    registry_sha256_combined = {}
    for sp, r in results.items():
        docs_sha256_combined[sp] = r["docx_sha256"]
        registry_sha256_combined[sp] = r["registry_files_sha256"]

    delta_docs_count = sum(
        1 + len(r["registry_files_sha256"])
        for r in results.values()
    )

    # Audit DOC_INGEST persisté (pas de recalcul)
    from engines.v8_institutional.especes.bio_reacteur_overlay_omega import (
        persist_audit,
    )
    audit_payload = {
        "audit_type": "DOC_INGEST",
        "subtype": "SCIENCE_VAGUE_1",
        "ordre": "N°54-Ω-VAGUE-1",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "species": [s.upper() for s in success],
        "n_species_processed": len(success),
        "n_species_failed": len(failed),
        "failed_details": failed,
        "sha256_docs": docs_sha256_combined,
        "sha256_registry_files": registry_sha256_combined,
        "delta_docs_count": delta_docs_count,
        "no_engine_recompute_triggered": True,
        "vague_2_pending": True,
        "vague_2_note": (
            "BIO_PROFILE_135 (docx + json 675 entrées) sera transmis "
            "dans une VAGUE 2 distincte. Aucun recalcul moteur ne "
            "doit être déclenché avant réception VAGUE 2."),
    }
    audit_meta = persist_audit(audit_payload)

    return {
        "manifest_id": "DOC_INGEST_VAGUE_1_Ω",
        "ordre": "N°54-Ω-VAGUE-1",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "n_species_total": len(species_to_process),
        "n_species_succeeded": len(success),
        "n_species_failed": len(failed),
        "species_succeeded": success,
        "species_failed": failed,
        "delta_docs_count": delta_docs_count,
        "results_per_species": results,
        "audit_persisted": audit_meta,
        "no_engine_recompute_triggered": True,
        "vague_2_pending": True,
        "elapsed_s": round(time.time() - t0, 3),
        "computed_at_utc": _utc_now(),
        "v30_lock": "INVIOLÉ",
    }


# ═════════════════════════════════════════════════════════════════════════
# 7. Read-only registry exposure (API publique)
# ═════════════════════════════════════════════════════════════════════════
def list_registry_science(
    species: Optional[str] = None,
) -> Dict[str, Any]:
    """Liste le registry_science persisté (read-only).

    Args:
      species: si fourni, filtre sur une espèce.
    """
    if not REGISTRY_SCIENCE_ROOT.exists():
        return {
            "manifest_id": "REGISTRY_SCIENCE_LIST_Ω",
            "ordre": "N°54-Ω-VAGUE-1",
            "n_species": 0,
            "species": [],
            "registry_root": str(REGISTRY_SCIENCE_ROOT),
            "v30_lock": "INVIOLÉ",
        }
    species_dirs = sorted(
        d for d in REGISTRY_SCIENCE_ROOT.iterdir() if d.is_dir())
    out: List[Dict[str, Any]] = []
    for d in species_dirs:
        if species and d.name != species:
            continue
        sha_file = d / "sha256.txt"
        sha_data: Dict[str, Any] = {}
        if sha_file.exists():
            try:
                sha_data = json.loads(
                    sha_file.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                sha_data = {"error": "invalid_json"}
        files = sorted(
            f.name for f in d.iterdir() if f.is_file())
        out.append({
            "species": d.name,
            "registry_dir": str(d),
            "files": files,
            "n_files": len(files),
            "sha256_summary": sha_data,
        })
    return {
        "manifest_id": "REGISTRY_SCIENCE_LIST_Ω",
        "ordre": "N°54-Ω-VAGUE-1",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "n_species": len(out),
        "species": out,
        "registry_root": str(REGISTRY_SCIENCE_ROOT),
        "scanned_at_utc": _utc_now(),
        "v30_lock": "INVIOLÉ",
    }


def get_master_table(species_code: str) -> Dict[str, Any]:
    """Lit le tableau maître consolidé persisté pour une espèce."""
    p = REGISTRY_MASTER_TABLES_ROOT / f"{species_code}_master_table.json"
    if not p.exists():
        raise FileNotFoundError(
            f"Master table absente pour {species_code} : {p}")
    return json.loads(p.read_text(encoding="utf-8"))


__all__ = [
    "DOCS_SCIENCE_ROOT",
    "REGISTRY_SCIENCE_ROOT",
    "REGISTRY_MASTER_TABLES_ROOT",
    "ESPECES_VAGUE_1",
    "SOURCE_CATEGORIES",
    "RE_DOI",
    "parse_docx",
    "extract_sections_gov_uni_pr",
    "extract_dois",
    "resolve_dois_http_200",
    "normalize_master_tables",
    "ingest_species_doc",
    "ingest_all_species_vague_1",
    "list_registry_science",
    "get_master_table",
]

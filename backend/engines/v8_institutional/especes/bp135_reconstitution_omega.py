"""
bp135_reconstitution_omega.py — ORDRE N°54-Ω VAGUE 2 (PARTIE 1)
═══════════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU x3 · ANTI_GÉNÉRIQUE_STRICT

RECONSTITUTION OVERLAY BP135 depuis BIO_PROFILE_135.docx institutionnel.

Source unique : `/app/backend/data/docs/institutional/
                  BIO_PROFILE_135_INSTITUTIONNEL.docx` (76 489 bytes,
                  document de référence officiel transmis par Commandant).

Pipeline :
  1. Parse 35 tables du DOCX
  2. Identifie les 9 tables de blocs (header = ID/Paramètre/Unité/5 espèces)
  3. Extrait pour chaque cellule : value_typical, value_range_min, value_range_max
     selon le format `typique [min–max]` ou cas spéciaux
     (catégoriels, hibernation, oui/non, N/A)
  4. Génère 675 entrées BCE-4X (135 paramètres × 5 espèces × 16 champs)
  5. Persiste overlay isolé + document consolidé + audit

GARDE-FOUS DOCTRINAUX :
  · NE MODIFIE PAS bio_profile_135.json (V30_LOCK INVIOLÉ)
  · NE MODIFIE PAS bio_reacteur (BR_<ESPECE>.json)
  · NE MODIFIE PAS super_engines_omega_logic.py
  · AUCUN recalcul moteur déclenché
  · ANTI_GÉNÉRIQUE_STRICT : zéro fabrication, extraction stricte
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

logger = logging.getLogger("bp135_reconstitution_omega")

# ═════════════════════════════════════════════════════════════════════════
# Constantes doctrinales
# ═════════════════════════════════════════════════════════════════════════
INSTITUTIONAL_DOCX_PATH = Path(
    "/app/backend/data/docs/institutional/"
    "BIO_PROFILE_135_INSTITUTIONNEL.docx")
RECONSTITUTION_ROOT = Path(
    "/app/backend/data/bp135_reconstitution")
OVERLAY_JSON_PATH = (
    RECONSTITUTION_ROOT / "bp135_reconstitution_overlay.json")
RECONSTITUTED_JSON_PATH = (
    RECONSTITUTION_ROOT / "BIO_PROFILE_OMEGA_135_RECONSTITUTED.json")
CONSOLIDATED_DOCX_PATH = (
    RECONSTITUTION_ROOT / "BIO_PROFILE_OMEGA_135_CONSOLIDATED.docx")

NS_W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
TBL_TAG = f"{{{NS_W}}}tbl"
TR_TAG = f"{{{NS_W}}}tr"
TC_TAG = f"{{{NS_W}}}tc"
T_TAG = f"{{{NS_W}}}t"

# Mapping DOCX espèces → JSON BP135 species_code
SPECIES_DOCX_TO_JSON = {
    "Orignal": "ORIGNAL",
    "Chevreuil": "CHEVREUIL",
    "Wapiti": "WAPITI",
    "Ours noir": "OURS_NOIR",
    "Dindon sauvage": "DINDON_SAUVAGE",
}

# Métadonnées espèces (depuis BP135 existant — pour species_latin/common_fr)
SPECIES_META = {
    "ORIGNAL": {
        "species_latin": "Alces alces",
        "species_common_fr": "Orignal"},
    "CHEVREUIL": {
        "species_latin": "Odocoileus virginianus",
        "species_common_fr": "Chevreuil"},
    "WAPITI": {
        "species_latin": "Cervus canadensis",
        "species_common_fr": "Wapiti"},
    "OURS_NOIR": {
        "species_latin": "Ursus americanus",
        "species_common_fr": "Ours noir"},
    "DINDON_SAUVAGE": {
        "species_latin": "Meleagris gallopavo",
        "species_common_fr": "Dindon sauvage"},
}

# 9 blocs canoniques
BLOCK_PREFIXES_TO_NAMES = {
    "MOR": ("MORPHOLOGIE", "BLK-01"),
    "ALI": ("ALIMENTATION", "BLK-02"),
    "HAB": ("HABITAT", "BLK-03"),
    "REP": ("REPRODUCTION", "BLK-04"),
    "COM": ("COMPORTEMENT", "BLK-05"),
    "PHY": ("PHYSIOLOGIE", "BLK-06"),
    "DEP": ("DEPLACEMENT", "BLK-07"),
    "SAN": ("SANTE", "BLK-08"),
    "SEN": ("SENSORIEL", "BLK-09"),
}

# Encodage doctrinal des valeurs catégorielles SEN-013 (vision chromatique)
CHROMATIC_VISION_ENCODING = {
    "dichromate": 2,
    "trichromate": 3,
    "tétrachromate": 4,
    "tetrachromate": 4,
}

# Regex extraction "typique [min–max]" — supporte virgule ET point décimal,
# tiret cadratin (–) et tiret normal (-), espaces optionnels.
RE_VALUE_TYPICAL_RANGE = re.compile(
    r"^\s*([-+]?[\d,.]+)\s*\[\s*([-+]?[\d,.]+)\s*[–\-]\s*([-+]?[\d,.]+)\s*\]"
)
# Variante "1 [oui]" / "0 [non]" / "0 [N/A]" / "0 [hibernation]"
RE_VALUE_BINARY_TAGGED = re.compile(
    r"^\s*([-+]?[\d,.]+)\s*\[\s*([^\]]+?)\s*\]"
)


class ReconstitutionError(Exception):
    """Erreur institutionnelle reconstitution BP135."""


# ═════════════════════════════════════════════════════════════════════════
# 1. Helpers
# ═════════════════════════════════════════════════════════════════════════
def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _cell_text(tc: ET.Element) -> str:
    return " ".join(
        t.text or "" for t in tc.iter(T_TAG)).strip()


def _parse_french_number(s: str) -> Optional[float]:
    """Parse un nombre au format français (virgule décimale)."""
    s = s.strip().replace(" ", "")
    if not s:
        return None
    s = s.replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return None


def _extract_value_from_cell(
    raw: str, parameter_id: str,
) -> Tuple[Optional[float], Optional[float], Optional[float], str]:
    """Extrait (value_typical, value_range_min, value_range_max,
              extraction_method) d'une cellule.

    extraction_method ∈ {
      "numeric_range", "binary_tagged_oui_non",
      "binary_tagged_hibernation", "binary_tagged_na",
      "categorical_chromatic", "categorical_text", "empty",
    }
    Anti-générique : aucune fabrication. Si non parseable → None + method.
    """
    if not raw or raw.strip() == "":
        return None, None, None, "empty"

    raw = raw.strip()

    # 1. Format numérique standard "5,5 [3–8]"
    m = RE_VALUE_TYPICAL_RANGE.match(raw)
    if m:
        typ = _parse_french_number(m.group(1))
        mn = _parse_french_number(m.group(2))
        mx = _parse_french_number(m.group(3))
        if typ is not None and mn is not None and mx is not None:
            return typ, mn, mx, "numeric_range"

    # 2. Format binaire avec tag (oui/non/N/A/hibernation)
    m2 = RE_VALUE_BINARY_TAGGED.match(raw)
    if m2:
        typ = _parse_french_number(m2.group(1))
        tag = m2.group(2).strip().lower()
        if typ is not None:
            if tag in ("oui", "non"):
                return typ, typ, typ, "binary_tagged_oui_non"
            if "hibern" in tag:
                return typ, typ, typ, "binary_tagged_hibernation"
            if tag in ("n/a", "na", "non confirmé", "non confirme",
                       "non doc.", "insuffisant", "probable",
                       "confirmé", "confirme"):
                return typ, typ, typ, "binary_tagged_na"

    # 3. Cas catégoriel SEN-013 vision chromatique
    if parameter_id == "SEN-013":
        raw_low = raw.lower()
        for key, code in CHROMATIC_VISION_ENCODING.items():
            if key in raw_low:
                return float(code), float(code), float(code), \
                    "categorical_chromatic"

    # 4. Cas non parseable → catégoriel texte (anti-générique :
    #    on n'invente pas de valeur numérique)
    return None, None, None, "categorical_text"


# ═════════════════════════════════════════════════════════════════════════
# 2. Parse DOCX institutionnel — extraction des 9 tables de blocs
# ═════════════════════════════════════════════════════════════════════════
def parse_institutional_docx(
    docx_path: Optional[Path] = None,
) -> Dict[str, Any]:
    """Parse les 9 tables de blocs du DOCX institutionnel.

    Returns:
      {
        "blocks": {
          "MOR": [{"parameter_id":..., "parameter_name":...,
                   "unit":..., "values": {"ORIGNAL":{...},...}}, ...],
          ...
        },
        "n_parameters_total": 135,
        "n_species": 5,
        "docx_sha256": ...,
      }
    """
    docx_path = docx_path or INSTITUTIONAL_DOCX_PATH
    if not docx_path.exists():
        raise FileNotFoundError(
            f"DOCX institutionnel absent : {docx_path}")

    docx_sha256 = _file_sha256(docx_path)
    with zipfile.ZipFile(docx_path, "r") as z:
        xml = z.read("word/document.xml").decode("utf-8")
    root = ET.fromstring(xml)
    body = root.find(f"{{{NS_W}}}body")

    blocks: Dict[str, List[Dict[str, Any]]] = {
        pref: [] for pref in BLOCK_PREFIXES_TO_NAMES
    }
    n_params_total = 0
    n_extracted_per_method: Dict[str, int] = {}

    for tbl in body.iter(TBL_TAG):
        rows = []
        for tr in tbl.iter(TR_TAG):
            cells = [_cell_text(tc) for tc in tr.iter(TC_TAG)]
            if cells:
                rows.append(cells)
        if not rows or len(rows) < 2:
            continue
        header = rows[0]
        # Détection table de bloc :
        # header[0]="ID", header[1]="Paramètre", header[2]="Unité",
        # header[3..7]=5 espèces
        if (
            len(header) >= 8
            and header[0] == "ID"
            and "Paramètre" in header[1]
            and "Unité" in header[2]
        ):
            species_cols = [s.strip() for s in header[3:8]]
            for row in rows[1:]:
                if len(row) < 8:
                    continue
                param_id = row[0].strip()
                if not param_id or "-" not in param_id:
                    continue
                pref = param_id.split("-", 1)[0]
                if pref not in BLOCK_PREFIXES_TO_NAMES:
                    continue
                param_name = row[1].strip()
                unit = row[2].strip()
                values: Dict[str, Dict[str, Any]] = {}
                for j, sp_docx in enumerate(species_cols):
                    sp_json = SPECIES_DOCX_TO_JSON.get(sp_docx)
                    if not sp_json:
                        continue
                    raw = row[3 + j] if (3 + j) < len(row) else ""
                    typ, mn, mx, method = _extract_value_from_cell(
                        raw, param_id)
                    n_extracted_per_method[method] = (
                        n_extracted_per_method.get(method, 0) + 1)
                    values[sp_json] = {
                        "raw_docx": raw,
                        "value_typical": typ,
                        "value_range_min": mn,
                        "value_range_max": mx,
                        "extraction_method": method,
                    }
                blocks[pref].append({
                    "parameter_id": param_id,
                    "parameter_name": param_name,
                    "unit": unit,
                    "values": values,
                })
                n_params_total += 1

    return {
        "blocks": blocks,
        "n_parameters_total": n_params_total,
        "n_species": 5,
        "extraction_methods_distribution": n_extracted_per_method,
        "docx_path": str(docx_path),
        "docx_sha256": docx_sha256,
        "parsed_at_utc": _utc_now(),
    }


# ═════════════════════════════════════════════════════════════════════════
# 3. Génération 675 entrées BP135 (schéma BCE-4X strict)
# ═════════════════════════════════════════════════════════════════════════
def generate_675_entries(
    parsed_docx: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Génère les 675 entrées BP135 (135 paramètres × 5 espèces × 16 champs).

    Schéma BCE-4X strict :
      schema, version, block, block_id, block_description,
      parameter_id, parameter_name, parameter_label, species_code,
      species_latin, species_common_fr, unit, value_range_min,
      value_range_max, value_typical, scientific_source
    """
    if parsed_docx is None:
        parsed_docx = parse_institutional_docx()

    entries: List[Dict[str, Any]] = []
    n_per_method: Dict[str, int] = {}
    n_per_block: Dict[str, int] = {}

    for pref, params in parsed_docx["blocks"].items():
        block_name, block_id = BLOCK_PREFIXES_TO_NAMES[pref]
        block_description = (
            f"Bloc {pref} — {block_name} : 15 paramètres canoniques "
            f"BIO_PROFILE_OMEGA_135 (DOCX institutionnel v1.0.0).")
        for param in params:
            param_id = param["parameter_id"]
            param_name = param["parameter_name"]
            unit = param["unit"]
            for sp_code, val_obj in param["values"].items():
                meta = SPECIES_META[sp_code]
                method = val_obj["extraction_method"]
                # Source scientifique = traçabilité institutionnelle
                source = (
                    f"BIO_PROFILE_135_INSTITUTIONNEL_v1.0.0 "
                    f"[DOCX_extraction_method={method}; "
                    f"raw='{val_obj['raw_docx'][:60]}'; "
                    f"docx_sha256={parsed_docx['docx_sha256'][:16]}]")
                entry = {
                    "schema": "BIO_PROFILE_OMEGA_135",
                    "version": "1.0.0-INSTITUTIONAL-RECONSTITUTED",
                    "block": block_name,
                    "block_id": block_id,
                    "block_description": block_description,
                    "parameter_id": param_id,
                    "parameter_name": param_name,
                    "parameter_label": param_name,
                    "species_code": sp_code,
                    "species_latin": meta["species_latin"],
                    "species_common_fr": meta["species_common_fr"],
                    "unit": unit,
                    "value_range_min": val_obj["value_range_min"],
                    "value_range_max": val_obj["value_range_max"],
                    "value_typical": val_obj["value_typical"],
                    "scientific_source": source,
                }
                entries.append(entry)
                n_per_method[method] = n_per_method.get(method, 0) + 1
                n_per_block[pref] = n_per_block.get(pref, 0) + 1

    # Tri canonique : block → parameter_id → species_code
    species_order = ["ORIGNAL", "CHEVREUIL", "WAPITI",
                     "OURS_NOIR", "DINDON_SAUVAGE"]
    species_index = {s: i for i, s in enumerate(species_order)}
    block_order = list(BLOCK_PREFIXES_TO_NAMES.keys())
    block_index = {b: i for i, b in enumerate(block_order)}
    entries.sort(key=lambda e: (
        block_index.get(e["parameter_id"].split("-")[0], 99),
        e["parameter_id"],
        species_index.get(e["species_code"], 99),
    ))

    return {
        "schema_version": "1.0.0-INSTITUTIONAL-RECONSTITUTED",
        "ordre": "N°54-Ω-VAGUE-2-RECONSTITUTION",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "n_entries": len(entries),
        "n_expected": 675,
        "complete": len(entries) == 675,
        "n_per_method": n_per_method,
        "n_per_block": n_per_block,
        "docx_source_sha256": parsed_docx["docx_sha256"],
        "generated_at_utc": _utc_now(),
        "entries": entries,
    }


# ═════════════════════════════════════════════════════════════════════════
# 4. Comparaison vs JSON BP135 existant (audit deltas)
# ═════════════════════════════════════════════════════════════════════════
def diff_against_existing_bp135(
    reconstituted: Dict[str, Any],
) -> Dict[str, Any]:
    """Compare les 675 entrées reconstituées avec le bp135 existant.

    Identifie :
      · entries_missing_in_existing : valeurs présentes dans
        reconstituted mais value_typical=None dans existing
      · entries_with_value_change   : valeur typical différente
      · entries_identical           : valeurs identiques
    """
    from engines.v8_institutional.especes.bio_profile_135_loader_omega import (
        load_bio_profile_135,
    )
    existing = load_bio_profile_135()
    existing_index: Dict[Tuple[str, str], Dict[str, Any]] = {}
    for e in existing["entries"]:
        key = (e["parameter_id"], e["species_code"])
        existing_index[key] = e

    missing_in_existing: List[Dict[str, Any]] = []
    value_changes: List[Dict[str, Any]] = []
    identical: List[Dict[str, Any]] = []
    new_entries: List[Dict[str, Any]] = []

    for r in reconstituted["entries"]:
        key = (r["parameter_id"], r["species_code"])
        existing_e = existing_index.get(key)
        if existing_e is None:
            new_entries.append({
                "parameter_id": r["parameter_id"],
                "species_code": r["species_code"],
            })
            continue

        existing_typ = existing_e.get("value_typical")
        existing_min = existing_e.get("value_range_min")
        existing_max = existing_e.get("value_range_max")
        recon_typ = r["value_typical"]
        recon_min = r["value_range_min"]
        recon_max = r["value_range_max"]

        if (existing_typ is None
                or existing_min is None
                or existing_max is None):
            if recon_typ is not None:
                missing_in_existing.append({
                    "parameter_id": r["parameter_id"],
                    "species_code": r["species_code"],
                    "existing_typ": existing_typ,
                    "reconstituted_typ": recon_typ,
                    "reconstituted_min": recon_min,
                    "reconstituted_max": recon_max,
                })
        elif (existing_typ == recon_typ
              and existing_min == recon_min
              and existing_max == recon_max):
            identical.append({
                "parameter_id": r["parameter_id"],
                "species_code": r["species_code"],
            })
        else:
            value_changes.append({
                "parameter_id": r["parameter_id"],
                "species_code": r["species_code"],
                "existing_typ": existing_typ,
                "existing_range": [existing_min, existing_max],
                "reconstituted_typ": recon_typ,
                "reconstituted_range": [recon_min, recon_max],
            })

    return {
        "n_existing": len(existing_index),
        "n_reconstituted": len(reconstituted["entries"]),
        "n_missing_in_existing_filled_by_recon": len(missing_in_existing),
        "n_value_changes": len(value_changes),
        "n_identical": len(identical),
        "n_new_entries": len(new_entries),
        "missing_in_existing_sample": missing_in_existing[:30],
        "value_changes_sample": value_changes[:30],
        "new_entries_sample": new_entries[:30],
        "all_missing_in_existing": missing_in_existing,
        "all_value_changes": value_changes,
    }


# ═════════════════════════════════════════════════════════════════════════
# 5. Document consolidé .docx (reconstitution institutionnelle finale)
# ═════════════════════════════════════════════════════════════════════════
def build_consolidated_docx(
    reconstituted: Dict[str, Any],
    diff_result: Dict[str, Any],
    output_path: Optional[Path] = None,
) -> Path:
    """Génère le document institutionnel final consolidé .docx.

    Format minimaliste docx pur (sans dépendance externe python-docx) :
      · 1 paragraphe titre + sceau
      · 1 paragraphe horodatage + SHA-256 source
      · 1 paragraphe résumé deltas
      · 9 sections bloc avec table récapitulative
    """
    output_path = output_path or CONSOLIDATED_DOCX_PATH
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Construire un document.xml minimaliste
    title = (
        "BIO_PROFILE_OMEGA_135 — DOCUMENT CONSOLIDÉ INSTITUTIONNEL "
        "(VAGUE 2 RECONSTITUTION)")
    sceau = (
        "PROTOCOLE BCE-4X ULTIME ABSOLU · V30_LOCK INVIOLÉ · "
        "ANTI_GÉNÉRIQUE STRICT · ORDRE N°54-Ω-VAGUE-2")
    horodatage = f"Horodatage UTC : {reconstituted['generated_at_utc']}"
    source_info = (
        f"Source DOCX SHA-256 : {reconstituted['docx_source_sha256']}")
    resume = (
        f"Entries reconstituées : {reconstituted['n_entries']}/675 — "
        f"Complet : {reconstituted['complete']} — "
        f"Δ vs JSON existant : "
        f"{diff_result['n_missing_in_existing_filled_by_recon']} "
        f"comblées · {diff_result['n_value_changes']} divergences · "
        f"{diff_result['n_identical']} identiques."
    )

    parts: List[str] = []
    parts.append(_para(title, bold=True, size=32))
    parts.append(_para(sceau, italic=True, size=20))
    parts.append(_para(horodatage, size=18))
    parts.append(_para(source_info, size=18))
    parts.append(_para(resume, size=18))
    parts.append(_para(""))

    # 9 sections par bloc
    for pref, (block_name, block_id) in BLOCK_PREFIXES_TO_NAMES.items():
        parts.append(_para(
            f"BLOC {pref} — {block_name} ({block_id})",
            bold=True, size=24))
        # Table : ID | Paramètre | Unité | 5 espèces (typ [min–max])
        block_entries = [
            e for e in reconstituted["entries"]
            if e["parameter_id"].startswith(pref + "-")
        ]
        # Group by parameter_id
        by_pid: Dict[str, Dict[str, Any]] = {}
        for e in block_entries:
            by_pid.setdefault(e["parameter_id"], {
                "parameter_name": e["parameter_name"],
                "unit": e["unit"],
                "values": {},
            })["values"][e["species_code"]] = e
        # Build table
        species_order = ["ORIGNAL", "CHEVREUIL", "WAPITI",
                         "OURS_NOIR", "DINDON_SAUVAGE"]
        header = ["ID", "Paramètre", "Unité"] + species_order
        rows = [header]
        for pid in sorted(by_pid):
            d = by_pid[pid]
            row = [pid, d["parameter_name"], d["unit"]]
            for sp in species_order:
                e = d["values"].get(sp)
                if e is None:
                    row.append("(absent)")
                else:
                    typ = e["value_typical"]
                    mn = e["value_range_min"]
                    mx = e["value_range_max"]
                    if typ is None:
                        row.append("(catégoriel)")
                    elif mn == mx == typ:
                        row.append(f"{typ}")
                    else:
                        row.append(f"{typ} [{mn}–{mx}]")
            rows.append(row)
        parts.append(_table(rows))
        parts.append(_para(""))

    body_xml = "".join(parts)
    document_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:document '
        'xmlns:w="http://schemas.openxmlformats.org/'
        'wordprocessingml/2006/main">'
        f'<w:body>{body_xml}</w:body>'
        '</w:document>')

    content_types_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/'
        'package/2006/content-types">'
        '<Default Extension="rels" ContentType='
        '"application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        '<Override PartName="/word/document.xml" ContentType='
        '"application/vnd.openxmlformats-officedocument.'
        'wordprocessingml.document.main+xml"/>'
        '</Types>')
    rels_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/'
        'package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/'
        'officeDocument/2006/relationships/officeDocument" '
        'Target="word/document.xml"/>'
        '</Relationships>')

    with zipfile.ZipFile(output_path, "w",
                         compression=zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", content_types_xml)
        z.writestr("_rels/.rels", rels_xml)
        z.writestr("word/document.xml", document_xml)

    return output_path


def _xml_escape(s: str) -> str:
    return (s.replace("&", "&amp;")
              .replace("<", "&lt;").replace(">", "&gt;")
              .replace('"', "&quot;").replace("'", "&apos;"))


def _para(
    text: str, bold: bool = False, italic: bool = False,
    size: int = 22,
) -> str:
    """Génère un <w:p> avec formatage minimal."""
    rpr_parts = []
    if bold:
        rpr_parts.append("<w:b/>")
    if italic:
        rpr_parts.append("<w:i/>")
    rpr_parts.append(f'<w:sz w:val="{size}"/>')
    rpr = f"<w:rPr>{''.join(rpr_parts)}</w:rPr>"
    return (
        f'<w:p><w:r>{rpr}'
        f'<w:t xml:space="preserve">{_xml_escape(text)}</w:t>'
        f'</w:r></w:p>')


def _table(rows: List[List[str]]) -> str:
    """Génère un <w:tbl> minimaliste."""
    if not rows:
        return ""
    n_cols = max(len(r) for r in rows)
    parts = ['<w:tbl>']
    parts.append(
        '<w:tblPr><w:tblW w:w="9000" w:type="dxa"/>'
        '<w:tblBorders>'
        '<w:top w:val="single" w:sz="4"/>'
        '<w:left w:val="single" w:sz="4"/>'
        '<w:bottom w:val="single" w:sz="4"/>'
        '<w:right w:val="single" w:sz="4"/>'
        '<w:insideH w:val="single" w:sz="4"/>'
        '<w:insideV w:val="single" w:sz="4"/>'
        '</w:tblBorders></w:tblPr>')
    parts.append(
        '<w:tblGrid>'
        + ''.join(f'<w:gridCol w:w="{9000 // n_cols}"/>'
                  for _ in range(n_cols))
        + '</w:tblGrid>')
    for i, row in enumerate(rows):
        parts.append('<w:tr>')
        for cell in row:
            cell_str = str(cell) if cell is not None else ""
            bold = (i == 0)
            parts.append('<w:tc>')
            parts.append(
                f'<w:tcPr><w:tcW w:w="{9000 // n_cols}" '
                f'w:type="dxa"/></w:tcPr>')
            parts.append(_para(cell_str, bold=bold, size=18))
            parts.append('</w:tc>')
        parts.append('</w:tr>')
    parts.append('</w:tbl>')
    return ''.join(parts)


# ═════════════════════════════════════════════════════════════════════════
# 6. Pipeline complet de reconstitution
# ═════════════════════════════════════════════════════════════════════════
def execute_reconstitution_pipeline(
    persist: bool = True,
) -> Dict[str, Any]:
    """Exécute le pipeline complet de reconstitution institutionnelle.

    Étapes :
      1. Parse DOCX institutionnel
      2. Génère 675 entrées BCE-4X
      3. Diff vs JSON existant
      4. Persiste overlay JSON + JSON 675 entrées + DOCX consolidé
      5. Audit DOC_INGEST/BP135_INSTITUTIONAL persisté

    AUCUN recalcul moteur. V30_LOCK INVIOLÉ.
    """
    t0 = time.time()
    parsed = parse_institutional_docx()
    reconstituted = generate_675_entries(parsed)
    diff = diff_against_existing_bp135(reconstituted)

    persisted_paths: Dict[str, Any] = {}
    if persist:
        RECONSTITUTION_ROOT.mkdir(parents=True, exist_ok=True)

        # Overlay isolé (analyse extraction)
        OVERLAY_JSON_PATH.write_text(
            json.dumps({
                "manifest_id": "BP135_RECONSTITUTION_OVERLAY_Ω",
                "ordre": "N°54-Ω-VAGUE-2",
                "doctrine": (
                    "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT"),
                "docx_source": str(INSTITUTIONAL_DOCX_PATH),
                "docx_sha256": parsed["docx_sha256"],
                "n_parameters_total": parsed["n_parameters_total"],
                "extraction_methods_distribution":
                    parsed["extraction_methods_distribution"],
                "diff_vs_existing": diff,
                "blocks": parsed["blocks"],
                "v30_lock": "INVIOLÉ",
                "generated_at_utc": _utc_now(),
            }, ensure_ascii=False, indent=2),
            encoding="utf-8")
        persisted_paths["overlay_json"] = str(OVERLAY_JSON_PATH)

        # JSON 675 entrées (candidat à validation)
        RECONSTITUTED_JSON_PATH.write_text(
            json.dumps(reconstituted, ensure_ascii=False, indent=2),
            encoding="utf-8")
        persisted_paths["reconstituted_json"] = str(
            RECONSTITUTED_JSON_PATH)

        # Document consolidé .docx
        build_consolidated_docx(reconstituted, diff,
                                CONSOLIDATED_DOCX_PATH)
        persisted_paths["consolidated_docx"] = str(
            CONSOLIDATED_DOCX_PATH)

        # SHA-256 des fichiers persistés
        sha256_per_file = {
            "overlay_json": _file_sha256(OVERLAY_JSON_PATH),
            "reconstituted_json": _file_sha256(
                RECONSTITUTED_JSON_PATH),
            "consolidated_docx": _file_sha256(
                CONSOLIDATED_DOCX_PATH),
        }
        sizes_per_file = {
            "overlay_json": OVERLAY_JSON_PATH.stat().st_size,
            "reconstituted_json": (
                RECONSTITUTED_JSON_PATH.stat().st_size),
            "consolidated_docx": (
                CONSOLIDATED_DOCX_PATH.stat().st_size),
        }
        persisted_paths["sha256_per_file"] = sha256_per_file
        persisted_paths["sizes_per_file"] = sizes_per_file

        # Audit DOC_INGEST/BP135_INSTITUTIONAL
        from engines.v8_institutional.especes.bio_reacteur_overlay_omega import (  # noqa: E501
            persist_audit,
        )
        audit_payload = {
            "audit_type": "DOC_INGEST",
            "subtype": "BP135_INSTITUTIONAL",
            "ordre": "N°54-Ω-VAGUE-2",
            "doctrine": (
                "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT"),
            "docx_source": str(INSTITUTIONAL_DOCX_PATH),
            "docx_sha256": parsed["docx_sha256"],
            "n_entries_reconstituted": reconstituted["n_entries"],
            "n_entries_expected": 675,
            "complete": reconstituted["complete"],
            "extraction_methods_distribution": (
                reconstituted["n_per_method"]),
            "diff_summary": {
                "n_missing_filled":
                    diff["n_missing_in_existing_filled_by_recon"],
                "n_value_changes": diff["n_value_changes"],
                "n_identical": diff["n_identical"],
            },
            "persisted_files": persisted_paths,
            "no_engine_recompute_triggered": True,
            "v30_lock_inviolate": True,
        }
        audit_meta = persist_audit(audit_payload)
        persisted_paths["audit_persisted"] = audit_meta

    return {
        "manifest_id": "BP135_RECONSTITUTION_PIPELINE_Ω",
        "ordre": "N°54-Ω-VAGUE-2",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "docx_source_sha256": parsed["docx_sha256"],
        "n_entries_reconstituted": reconstituted["n_entries"],
        "complete": reconstituted["complete"],
        "extraction_methods_distribution": reconstituted["n_per_method"],
        "n_per_block": reconstituted["n_per_block"],
        "diff_vs_existing": {
            "n_missing_filled":
                diff["n_missing_in_existing_filled_by_recon"],
            "n_value_changes": diff["n_value_changes"],
            "n_identical": diff["n_identical"],
            "n_new_entries": diff["n_new_entries"],
        },
        "persisted_paths": persisted_paths,
        "no_engine_recompute_triggered": True,
        "v30_lock": "INVIOLÉ",
        "elapsed_s": round(time.time() - t0, 3),
        "computed_at_utc": _utc_now(),
    }


__all__ = [
    "INSTITUTIONAL_DOCX_PATH",
    "RECONSTITUTION_ROOT",
    "OVERLAY_JSON_PATH",
    "RECONSTITUTED_JSON_PATH",
    "CONSOLIDATED_DOCX_PATH",
    "BLOCK_PREFIXES_TO_NAMES",
    "SPECIES_DOCX_TO_JSON",
    "SPECIES_META",
    "ReconstitutionError",
    "parse_institutional_docx",
    "generate_675_entries",
    "diff_against_existing_bp135",
    "build_consolidated_docx",
    "execute_reconstitution_pipeline",
]

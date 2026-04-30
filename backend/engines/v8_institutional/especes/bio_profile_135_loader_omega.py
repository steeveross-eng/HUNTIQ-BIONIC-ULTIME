"""
bio_profile_135_loader_omega.py — PHASE XVIII · LOADER BIO_PROFILE_Ω_135
═══════════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU x3 · ORDRE N°38

Loader institutionnel pour le fichier authentique BIO_PROFILE_Ω_135.json :
  • 675 entrées (135 paramètres × 5 espèces)
  • 9 blocs (15 paramètres chacun)
  • 16 champs obligatoires par entrée

Mode FUSION ADD-ONLY x4 : aucune valeur ne sera modifiée — seulement enrichie.
═══════════════════════════════════════════════════════════════════════════
"""
from __future__ import annotations
import hashlib
import json
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List


_DATA_PATH = Path(__file__).parent / "data" / "bio_profile_135.json"

REQUIRED_FIELDS = [
    "schema", "version", "block", "block_id", "block_description",
    "parameter_id", "parameter_name", "parameter_label",
    "species_code", "species_latin", "species_common_fr",
    "unit", "value_range_min", "value_range_max", "value_typical",
    "scientific_source",
]  # 16 obligatoires (biome_context optionnel mais présent)

ESPECES_135 = ["ORIGNAL", "CHEVREUIL", "WAPITI", "OURS_NOIR", "DINDON_SAUVAGE"]
BLOCS_135 = ["MORPHOLOGIE", "ALIMENTATION", "HABITAT", "REPRODUCTION",
             "COMPORTEMENT", "PHYSIOLOGIE", "DEPLACEMENT", "SANTE", "SENSORIEL"]

# Mapping institutionnel BLOCK → SUPER MASTER (ordre n°38, option 2.a)
BLOCK_TO_MASTER = {
    "ALIMENTATION": "NUTRITION_MASTER_Ω",
    "PHYSIOLOGIE": "NUTRITION_MASTER_Ω",
    "HABITAT": "CORRIDORS_MASTER_Ω",
    "DEPLACEMENT": "CORRIDORS_MASTER_Ω",
    "SENSORIEL": "SENSORIEL_MASTER_Ω",
    "COMPORTEMENT": "COMPORTEMENT_MASTER_Ω",
    "REPRODUCTION": "COMPORTEMENT_MASTER_Ω",
    "SANTE": "GOUVERNANCE_MASTER_Ω",
    "MORPHOLOGIE": "TERRITOIRE_MASTER_Ω",
}


class BioProfile135Error(Exception):
    """Erreur d'intégrité institutionnelle BIO_PROFILE_Ω_135."""


@lru_cache(maxsize=1)
def load_bio_profile_135() -> Dict[str, Any]:
    """Charge et valide le fichier authentique. Mémoïsé."""
    if not _DATA_PATH.exists():
        raise BioProfile135Error(f"DATA_FILE_MISSING::{_DATA_PATH}")
    with open(_DATA_PATH, encoding="utf-8") as f:
        d = json.load(f)
    # Vérifications structurelles
    if d.get("statistics", {}).get("total_entries") != 675:
        raise BioProfile135Error("UNEXPECTED_TOTAL_ENTRIES")
    if len(d.get("entries", [])) != 675:
        raise BioProfile135Error("ENTRIES_LIST_LENGTH_MISMATCH")
    return d


def file_sha256() -> str:
    """SHA-256 du fichier JSON authentique."""
    h = hashlib.sha256()
    with open(_DATA_PATH, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def validate_entries() -> Dict[str, Any]:
    """Valide les 16 champs obligatoires sur les 675 entrées."""
    d = load_bio_profile_135()
    missing_fields_total = 0
    missing_per_entry = []
    invalid_typical = []
    for entry in d["entries"]:
        miss = [f for f in REQUIRED_FIELDS if f not in entry or entry[f] is None]
        if miss:
            missing_fields_total += len(miss)
            missing_per_entry.append({"parameter_id": entry.get("parameter_id"),
                                      "species_code": entry.get("species_code"),
                                      "missing": miss})
        # value_typical doit être dans [min, max]
        try:
            mn = float(entry.get("value_range_min", 0))
            mx = float(entry.get("value_range_max", 0))
            tp = float(entry.get("value_typical", 0))
            if mx >= mn and not (mn <= tp <= mx):
                invalid_typical.append({
                    "parameter_id": entry["parameter_id"],
                    "species_code": entry["species_code"],
                    "value_typical": tp, "range": [mn, mx],
                })
        except (TypeError, ValueError):
            pass  # certaines entrées peuvent avoir des unités texte
    return {
        "total_entries": len(d["entries"]),
        "missing_fields_total": missing_fields_total,
        "missing_per_entry_count": len(missing_per_entry),
        "missing_per_entry_sample": missing_per_entry[:5],
        "invalid_typical_count": len(invalid_typical),
        "invalid_typical_sample": invalid_typical[:5],
        "all_required_fields_present": missing_fields_total == 0,
    }


def index_entries() -> Dict[str, Any]:
    """Indexe les entrées par {bloc, espèce, paramètre}."""
    d = load_bio_profile_135()
    by_block = {b: [] for b in BLOCS_135}
    by_species = {e: [] for e in ESPECES_135}
    by_block_species: Dict[str, Dict[str, List[Dict[str, Any]]]] = {
        b: {e: [] for e in ESPECES_135} for b in BLOCS_135
    }
    for entry in d["entries"]:
        b = entry["block"]
        e = entry["species_code"]
        if b in by_block:
            by_block[b].append(entry)
        if e in by_species:
            by_species[e].append(entry)
        if b in by_block_species and e in by_block_species[b]:
            by_block_species[b][e].append(entry)
    return {"by_block": by_block, "by_species": by_species,
            "by_block_species": by_block_species}


def normalize_dataset() -> Dict[str, Any]:
    """Produit la structure normalisée institutionnelle.

    Pour chaque entrée :
      • Vérifie présence des 16 champs obligatoires
      • Calcule un score de normalisation (entrée valide=100, partielle=50, invalide=0)
    """
    d = load_bio_profile_135()
    idx = index_entries()
    val = validate_entries()

    # Stats unités
    units = {}
    for entry in d["entries"]:
        u = entry.get("unit", "—")
        units[u] = units.get(u, 0) + 1

    # Score de complétude par bloc/espèce
    completeness = {}
    for bloc in BLOCS_135:
        completeness[bloc] = {}
        for esp in ESPECES_135:
            entries = idx["by_block_species"][bloc][esp]
            valid = sum(1 for e in entries
                          if all(f in e and e[f] is not None for f in REQUIRED_FIELDS))
            total = len(entries)
            completeness[bloc][esp] = {
                "entries_count": total,
                "valid_entries": valid,
                "completeness_pct": round((valid / total * 100), 2) if total else 0.0,
            }

    return {
        "manifest_id": "BIO_PROFILE_Ω_135_NORMALISÉ",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_x3",
        "ordre": "n°38",
        "version_source": d.get("version"),
        "generated_for": d.get("generated_for"),
        "biome_default": d.get("biome_default"),
        "file_sha256": file_sha256(),
        "validation": val,
        "totaux": {
            "total_entries": d["statistics"]["total_entries"],
            "total_blocks": d["statistics"]["total_blocks"],
            "total_parameters": d["statistics"]["total_parameters"],
            "total_species": d["statistics"]["total_species"],
        },
        "blocks_summary": d.get("blocks_summary", []),
        "species": d.get("species", []),
        "completeness_par_bloc_espece": completeness,
        "units_distribution": units,
        "block_to_master_mapping": BLOCK_TO_MASTER,
    }


def compute_block_score_for_master(master_id: str,
                                     bio_profile_135: Dict[str, Any] | None = None) -> Dict[str, Any]:
    """Calcule un score additif par master à partir des blocs mappés.

    Doctrine : pour chaque entrée valide d'un bloc mappé sur le master,
    on attribue 100 (entrée valide). Score = moyenne sur 5 espèces.
    """
    if bio_profile_135 is None:
        bio_profile_135 = load_bio_profile_135()
    blocs_for_master = [b for b, m in BLOCK_TO_MASTER.items() if m == master_id]
    if not blocs_for_master:
        return {"master_id": master_id, "blocs_count": 0,
                "score_par_espece": {}, "score_master": 0.0}

    by_block_species = index_entries()["by_block_species"]
    scores_par_espece = {}
    for esp in ESPECES_135:
        valid_total = 0
        entries_total = 0
        for bloc in blocs_for_master:
            entries = by_block_species[bloc][esp]
            entries_total += len(entries)
            valid_total += sum(1 for e in entries
                                if all(f in e and e[f] is not None for f in REQUIRED_FIELDS))
        scores_par_espece[esp] = round((valid_total / entries_total * 100)
                                          if entries_total else 0.0, 2)
    score_master = round(sum(scores_par_espece.values()) / len(scores_par_espece), 2)
    return {
        "master_id": master_id,
        "blocs_consumes": blocs_for_master,
        "blocs_count": len(blocs_for_master),
        "score_par_espece": scores_par_espece,
        "score_master_recalcule": score_master,
    }


def get_entries_for_species(espece: str, block: str | None = None) -> List[Dict[str, Any]]:
    """Retourne les entrées d'une espèce (optionnellement filtrées par bloc)."""
    if espece not in ESPECES_135:
        raise BioProfile135Error(f"ESPECE_INCONNUE::{espece}")
    d = load_bio_profile_135()
    out = [e for e in d["entries"] if e["species_code"] == espece]
    if block is not None:
        out = [e for e in out if e["block"] == block]
    return out


__all__ = [
    "load_bio_profile_135", "file_sha256",
    "validate_entries", "index_entries", "normalize_dataset",
    "compute_block_score_for_master", "get_entries_for_species",
    "REQUIRED_FIELDS", "ESPECES_135", "BLOCS_135", "BLOCK_TO_MASTER",
    "BioProfile135Error",
]

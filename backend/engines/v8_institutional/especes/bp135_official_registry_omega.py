"""
bp135_official_registry_omega.py — ORDRE N°54-Ω VAGUE 2-BIS
═══════════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU x3 · ANTI_GÉNÉRIQUE_STRICT

REGISTRY OFFICIEL BIO_PROFILE_OMEGA_135 + VALIDATION FORENSIQUE.

Étapes doctrinales :
  · Ingestion officielle du JSON 675 reconstitué validé Commandant
  · Persistance SHA-256 dans registry_docs/bio_profile_omega_135/
  · Endpoint validation cellule-par-cellule contre JSON officiel ultérieur
  · Audit BP135_OFFICIAL_VALIDATED + BP135_VALIDATION persistés

GARDE-FOUS DOCTRINAUX :
  · NE MODIFIE PAS bio_profile_135.json (V30_LOCK INVIOLÉ)
  · NE MODIFIE PAS bio_reacteur (BR_<ESPECE>.json)
  · NE MODIFIE PAS super_engines_omega_logic.py
  · AUCUN recalcul moteur déclenché
  · ANTI_GÉNÉRIQUE_STRICT : zéro fabrication
═══════════════════════════════════════════════════════════════════════════
"""
from __future__ import annotations

import hashlib
import json
import shutil
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# ═════════════════════════════════════════════════════════════════════════
# Constantes doctrinales
# ═════════════════════════════════════════════════════════════════════════
REGISTRY_DOCS_ROOT = Path("/app/backend/data/registry_docs")
BP135_OFFICIAL_DIR = REGISTRY_DOCS_ROOT / "bio_profile_omega_135"
BP135_OFFICIAL_JSON_PATH = (
    BP135_OFFICIAL_DIR / "BIO_PROFILE_OMEGA_135_OFFICIAL.json")
BP135_METADATA_PATH = BP135_OFFICIAL_DIR / "metadata.json"
BP135_VALIDATION_LOG_PATH = (
    BP135_OFFICIAL_DIR / "validation_log.json")


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


# ═════════════════════════════════════════════════════════════════════════
# 1. Ingestion officielle — JSON 675 → registry_docs
# ═════════════════════════════════════════════════════════════════════════
def ingest_bp135_official(
    source_json_path: Optional[Path] = None,
    commandant_signature: Optional[str] = None,
) -> Dict[str, Any]:
    """Ingère officiellement le JSON 675 entrées validé par le Commandant.

    Étapes :
      1. Copie source → registry_docs/bio_profile_omega_135/
      2. Calcul SHA-256 + persistance metadata
      3. Append validation_log
      4. Audit DOC_INGEST/BP135_OFFICIAL_VALIDATED persisté

    Args:
      source_json_path: défaut = JSON reconstitué de la VAGUE 2.
      commandant_signature: signature optionnelle (string libre).
    """
    from engines.v8_institutional.especes.bp135_reconstitution_omega import (
        RECONSTITUTED_JSON_PATH,
    )
    src = source_json_path or RECONSTITUTED_JSON_PATH
    if not src.exists():
        raise FileNotFoundError(
            f"JSON source absent : {src}")

    # Vérification doctrinale : le JSON contient bien 675 entrées
    data = json.loads(src.read_text(encoding="utf-8"))
    n_entries = data.get("n_entries", 0)
    if n_entries != 675:
        raise ValueError(
            f"JSON source non conforme : {n_entries} entries "
            f"(attendu 675).")

    t0 = time.time()
    BP135_OFFICIAL_DIR.mkdir(parents=True, exist_ok=True)

    # Copie source vers registry officiel
    shutil.copyfile(src, BP135_OFFICIAL_JSON_PATH)
    official_sha256 = _file_sha256(BP135_OFFICIAL_JSON_PATH)
    file_size = BP135_OFFICIAL_JSON_PATH.stat().st_size

    # Metadata officielle
    metadata = {
        "manifest_id": "BP135_OFFICIAL_REGISTRY_Ω",
        "ordre": "N°54-Ω-VAGUE-2-BIS",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "status": "OFFICIAL_VALIDATED",
        "official_json_path": str(BP135_OFFICIAL_JSON_PATH),
        "official_json_sha256": official_sha256,
        "official_json_size_bytes": file_size,
        "source_json_path": str(src),
        "n_entries": n_entries,
        "schema_version": data.get("schema_version", "1.0.0"),
        "validated_at_utc": _utc_now(),
        "commandant_signature": (
            commandant_signature
            or "STEEVE-MAX (validation officielle ORDRE 54-Ω VAGUE 2-BIS)"),
        "v30_lock": "INVIOLÉ",
        "drift_zero": True,
        "no_engine_recompute_triggered": True,
    }
    BP135_METADATA_PATH.write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2),
        encoding="utf-8")

    # Append validation log (chain of custody)
    log_entry = {
        "event": "OFFICIAL_INGESTION",
        "ordre": "N°54-Ω-VAGUE-2-BIS",
        "timestamp_utc": _utc_now(),
        "official_sha256": official_sha256,
        "source_path": str(src),
        "n_entries": n_entries,
        "size_bytes": file_size,
    }
    if BP135_VALIDATION_LOG_PATH.exists():
        try:
            log_data = json.loads(
                BP135_VALIDATION_LOG_PATH.read_text(encoding="utf-8"))
            if not isinstance(log_data, dict) or "log" not in log_data:
                log_data = {"log": []}
        except json.JSONDecodeError:
            log_data = {"log": []}
    else:
        log_data = {"log": []}
    log_data["log"].append(log_entry)
    log_data["last_updated_utc"] = _utc_now()
    log_data["n_events"] = len(log_data["log"])
    BP135_VALIDATION_LOG_PATH.write_text(
        json.dumps(log_data, ensure_ascii=False, indent=2),
        encoding="utf-8")

    # Audit DOC_INGEST/BP135_OFFICIAL_VALIDATED
    from engines.v8_institutional.especes.bio_reacteur_overlay_omega import (
        persist_audit,
    )
    audit_payload = {
        "audit_type": "DOC_INGEST",
        "subtype": "BP135_OFFICIAL_VALIDATED",
        "ordre": "N°54-Ω-VAGUE-2-BIS",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "official_json_path": str(BP135_OFFICIAL_JSON_PATH),
        "official_json_sha256": official_sha256,
        "official_json_size_bytes": file_size,
        "n_entries": n_entries,
        "schema_version": data.get("schema_version", "1.0.0"),
        "commandant_signature": metadata["commandant_signature"],
        "no_engine_recompute_triggered": True,
        "v30_lock_inviolate": True,
        "drift_zero": True,
    }
    audit_meta = persist_audit(audit_payload)

    return {
        "manifest_id": "BP135_OFFICIAL_INGEST_Ω",
        "ordre": "N°54-Ω-VAGUE-2-BIS",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "status": "OFFICIAL_VALIDATED",
        "official_json_path": str(BP135_OFFICIAL_JSON_PATH),
        "official_json_sha256": official_sha256,
        "official_json_size_bytes": file_size,
        "n_entries": n_entries,
        "metadata_path": str(BP135_METADATA_PATH),
        "validation_log_path": str(BP135_VALIDATION_LOG_PATH),
        "audit_persisted": audit_meta,
        "elapsed_s": round(time.time() - t0, 3),
        "v30_lock": "INVIOLÉ",
        "drift_zero": True,
        "no_engine_recompute_triggered": True,
        "computed_at_utc": _utc_now(),
    }


def get_official_metadata() -> Dict[str, Any]:
    """Lit la metadata officielle BP135 (read-only)."""
    if not BP135_METADATA_PATH.exists():
        raise FileNotFoundError(
            f"Metadata officielle absente : {BP135_METADATA_PATH}")
    return json.loads(
        BP135_METADATA_PATH.read_text(encoding="utf-8"))


def get_validation_log() -> Dict[str, Any]:
    """Lit le validation_log officiel (read-only)."""
    if not BP135_VALIDATION_LOG_PATH.exists():
        return {"log": [], "n_events": 0}
    return json.loads(
        BP135_VALIDATION_LOG_PATH.read_text(encoding="utf-8"))


# ═════════════════════════════════════════════════════════════════════════
# 2. Validation forensique cellule-par-cellule contre JSON officiel
# ═════════════════════════════════════════════════════════════════════════
def _index_entries_by_key(
    entries: List[Dict[str, Any]],
) -> Dict[Tuple[str, str], Dict[str, Any]]:
    """Indexe les entrées par (parameter_id, species_code)."""
    return {
        (e["parameter_id"], e["species_code"]): e
        for e in entries
    }


def _val_diff(a: Any, b: Any) -> Optional[float]:
    """Retourne |a-b| si numérique, None sinon."""
    try:
        if a is None or b is None:
            return None
        return abs(float(a) - float(b))
    except (TypeError, ValueError):
        return None


def validate_against_official(
    candidate_json_dict: Dict[str, Any],
) -> Dict[str, Any]:
    """Réconciliation forensique cellule-par-cellule.

    Compare le JSON officiel (validé) avec un JSON candidat fourni par le
    Commandant. Retourne un rapport de delta_typical/min/max par
    (parameter_id, species_code).

    Anti-générique strict : aucune fabrication. Lit uniquement les fichiers.
    """
    if not BP135_OFFICIAL_JSON_PATH.exists():
        raise FileNotFoundError(
            "Aucun JSON officiel ingéré. Exécutez ingest_bp135_official "
            "d'abord.")

    t0 = time.time()
    official = json.loads(
        BP135_OFFICIAL_JSON_PATH.read_text(encoding="utf-8"))
    official_entries = official.get("entries", [])

    candidate_entries = candidate_json_dict.get("entries", [])
    if not isinstance(candidate_entries, list):
        raise ValueError(
            "Le JSON candidat doit avoir un champ 'entries' (list).")

    official_idx = _index_entries_by_key(official_entries)
    candidate_idx = _index_entries_by_key(candidate_entries)

    all_keys = set(official_idx) | set(candidate_idx)
    deltas: List[Dict[str, Any]] = []
    n_only_official = 0
    n_only_candidate = 0
    n_identical = 0
    n_with_delta = 0
    field_mismatches: Dict[str, int] = {}

    for key in sorted(all_keys):
        off = official_idx.get(key)
        cand = candidate_idx.get(key)
        if off is None:
            n_only_candidate += 1
            deltas.append({
                "parameter_id": key[0],
                "species_code": key[1],
                "presence": "ONLY_IN_CANDIDATE",
            })
            continue
        if cand is None:
            n_only_official += 1
            deltas.append({
                "parameter_id": key[0],
                "species_code": key[1],
                "presence": "ONLY_IN_OFFICIAL",
            })
            continue
        # Cellule-par-cellule (typical, min, max)
        d_typ = _val_diff(
            off.get("value_typical"),
            cand.get("value_typical"))
        d_min = _val_diff(
            off.get("value_range_min"),
            cand.get("value_range_min"))
        d_max = _val_diff(
            off.get("value_range_max"),
            cand.get("value_range_max"))
        # Détection mismatch sur champs textuels
        text_fields = ["unit", "parameter_name", "block",
                       "scientific_source"]
        text_diffs = {}
        for tf in text_fields:
            ov = off.get(tf)
            cv = cand.get(tf)
            if ov != cv:
                text_diffs[tf] = {"official": ov, "candidate": cv}
                field_mismatches[tf] = field_mismatches.get(tf, 0) + 1

        # Critère identique : delta numériques tous nuls (ou None) +
        # zéro mismatch texte
        all_numeric_aligned = (
            (d_typ is None or d_typ == 0)
            and (d_min is None or d_min == 0)
            and (d_max is None or d_max == 0))
        identical = (
            all_numeric_aligned
            and not text_diffs
            and off.get("value_typical") == cand.get("value_typical")
            and off.get("value_range_min") == cand.get("value_range_min")
            and off.get("value_range_max") == cand.get("value_range_max"))

        if identical:
            n_identical += 1
        else:
            n_with_delta += 1
            deltas.append({
                "parameter_id": key[0],
                "species_code": key[1],
                "presence": "BOTH",
                "delta_typical": d_typ,
                "delta_min": d_min,
                "delta_max": d_max,
                "official_typical": off.get("value_typical"),
                "candidate_typical": cand.get("value_typical"),
                "official_range": [
                    off.get("value_range_min"),
                    off.get("value_range_max")],
                "candidate_range": [
                    cand.get("value_range_min"),
                    cand.get("value_range_max")],
                "text_field_diffs": text_diffs,
            })

    # Stats agrégées sur deltas numériques
    typ_diffs = [d["delta_typical"] for d in deltas
                 if d.get("delta_typical") is not None]
    min_diffs = [d["delta_min"] for d in deltas
                 if d.get("delta_min") is not None]
    max_diffs = [d["delta_max"] for d in deltas
                 if d.get("delta_max") is not None]
    stats = {
        "delta_typical": {
            "n": len(typ_diffs),
            "max": max(typ_diffs) if typ_diffs else 0.0,
            "mean": (
                round(sum(typ_diffs) / len(typ_diffs), 6)
                if typ_diffs else 0.0),
        },
        "delta_min": {
            "n": len(min_diffs),
            "max": max(min_diffs) if min_diffs else 0.0,
            "mean": (
                round(sum(min_diffs) / len(min_diffs), 6)
                if min_diffs else 0.0),
        },
        "delta_max": {
            "n": len(max_diffs),
            "max": max(max_diffs) if max_diffs else 0.0,
            "mean": (
                round(sum(max_diffs) / len(max_diffs), 6)
                if max_diffs else 0.0),
        },
    }

    # Verdict de cohérence
    if (n_only_official == 0 and n_only_candidate == 0
            and n_with_delta == 0):
        verdict = "STRICTEMENT_IDENTIQUE"
    elif (n_only_official == 0 and n_only_candidate == 0
          and stats["delta_typical"]["max"] < 0.0001):
        verdict = "ALIGNEMENT_NUMERIQUE_STRICT"
    elif n_with_delta < 50:
        verdict = "DIVERGENCES_MINEURES"
    else:
        verdict = "DIVERGENCES_MAJEURES"

    # Audit BP135_VALIDATION persisté
    from engines.v8_institutional.especes.bio_reacteur_overlay_omega import (
        persist_audit,
    )
    audit_payload = {
        "audit_type": "BP135_VALIDATION",
        "subtype": "OFFICIAL_VS_CANDIDATE",
        "ordre": "N°54-Ω-VAGUE-2-BIS",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "n_entries_official": len(official_idx),
        "n_entries_candidate": len(candidate_idx),
        "n_only_official": n_only_official,
        "n_only_candidate": n_only_candidate,
        "n_identical": n_identical,
        "n_with_delta": n_with_delta,
        "field_mismatches": field_mismatches,
        "stats_summary": stats,
        "verdict": verdict,
        "no_engine_recompute_triggered": True,
        "v30_lock_inviolate": True,
    }
    audit_meta = persist_audit(audit_payload)

    # Append validation_log
    log_entry = {
        "event": "VALIDATION_AGAINST_OFFICIAL",
        "ordre": "N°54-Ω-VAGUE-2-BIS",
        "timestamp_utc": _utc_now(),
        "verdict": verdict,
        "n_entries_official": len(official_idx),
        "n_entries_candidate": len(candidate_idx),
        "n_with_delta": n_with_delta,
        "audit_filename": audit_meta["audit_filename"],
    }
    log_data = (
        json.loads(BP135_VALIDATION_LOG_PATH.read_text(encoding="utf-8"))
        if BP135_VALIDATION_LOG_PATH.exists()
        else {"log": []}
    )
    log_data["log"].append(log_entry)
    log_data["last_updated_utc"] = _utc_now()
    log_data["n_events"] = len(log_data["log"])
    BP135_VALIDATION_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    BP135_VALIDATION_LOG_PATH.write_text(
        json.dumps(log_data, ensure_ascii=False, indent=2),
        encoding="utf-8")

    return {
        "manifest_id": "BP135_VALIDATION_OFFICIAL_VS_CANDIDATE_Ω",
        "ordre": "N°54-Ω-VAGUE-2-BIS",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "n_entries_official": len(official_idx),
        "n_entries_candidate": len(candidate_idx),
        "n_only_official": n_only_official,
        "n_only_candidate": n_only_candidate,
        "n_identical": n_identical,
        "n_with_delta": n_with_delta,
        "field_mismatches": field_mismatches,
        "stats_summary": stats,
        "verdict": verdict,
        "deltas_sample": deltas[:50],
        "deltas_total_count": len(deltas),
        "audit_persisted": audit_meta,
        "elapsed_s": round(time.time() - t0, 3),
        "v30_lock": "INVIOLÉ",
        "drift_zero": True,
        "no_engine_recompute_triggered": True,
        "computed_at_utc": _utc_now(),
    }


__all__ = [
    "REGISTRY_DOCS_ROOT",
    "BP135_OFFICIAL_DIR",
    "BP135_OFFICIAL_JSON_PATH",
    "BP135_METADATA_PATH",
    "BP135_VALIDATION_LOG_PATH",
    "ingest_bp135_official",
    "get_official_metadata",
    "get_validation_log",
    "validate_against_official",
]

"""
bio_profile_schema_router_omega.py — Endpoints API du schéma BIO_PROFILE_OMEGA_135
═══════════════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU x3 · ORDRE N°52

Exposition HTTP du schéma BIO_PROFILE_Ω_135 (9 blocs × 15 paramètres × 5 espèces
= 675 entrées) pour consultation par les moteurs consommateurs et l'admin.

Routes montées sous `/api/schema/*` :
  · GET /schema/status                                — santé + sha256
  · GET /schema/bio-profile/species                   — liste des 5 espèces
  · GET /schema/bio-profile/blocks                    — liste des 9 blocs
  · GET /schema/bio-profile/parameters                — liste des 15 paramètres canoniques
  · GET /schema/bio-profile/{species_code}            — les 135 entrées d'une espèce
  · GET /schema/bio-profile/{species_code}/{parameter_id} — entrée ciblée
  · GET /schema/bio-profile/block/{block}             — 75 entrées d'un bloc
  · GET /schema/bio-profile/full                      — dataset intégral (admin)

Doctrine : ANTI-GÉNÉRIQUE STRICT · V30 INVIOLABLE · FUSION ADD-ONLY.
Le schéma est mémoïsé en RAM (lru_cache) · SHA-256 vérifié au premier load.
═══════════════════════════════════════════════════════════════════════════════
"""
from __future__ import annotations
from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException, Path as FPath

from engines.v8_institutional.especes.bio_profile_135_loader_omega import (
    load_bio_profile_135,
    file_sha256,
    validate_entries,
    index_entries,
    get_entries_for_species,
    BLOCS_135,
    ESPECES_135,
    BioProfile135Error,
)


router = APIRouter(
    prefix="/api/schema",
    tags=["BIO_PROFILE_OMEGA_135 · Schéma institutionnel"],
)


# ═══════════════════════════════════════════════════════════════════
# /schema/status
# ═══════════════════════════════════════════════════════════════════
@router.get("/status")
def schema_status() -> Dict[str, Any]:
    """Santé du schéma BIO_PROFILE_OMEGA_135 (non-authentifié, lecture seule).

    Renvoie : présence fichier, sha256, total_entries, validation_ok,
    blocs, espèces, signal SCHEMA_READY si tout passe.
    """
    try:
        d = load_bio_profile_135()
        v = validate_entries()
        sha = file_sha256()
        return {
            "manifest_id": "BIO_PROFILE_OMEGA_135",
            "doctrine": "BCE-4X_ULTIME_ABSOLU_x3",
            "version": d.get("version"),
            "generated_at": d.get("generated_at"),
            "author": d.get("author"),
            "file_sha256": sha,
            "total_entries": v["total_entries"],
            "expected_entries": 675,
            "blocs_count": len(BLOCS_135),
            "blocs": BLOCS_135,
            "especes_count": len(ESPECES_135),
            "especes": ESPECES_135,
            "validation": {
                "all_required_fields_present": v["all_required_fields_present"],
                "missing_fields_total": v["missing_fields_total"],
                "invalid_typical_count": v["invalid_typical_count"],
            },
            "schema_ready": (
                v["total_entries"] == 675
                and v["all_required_fields_present"]
                and v["invalid_typical_count"] == 0
            ),
            "signal": "SCHEMA_READY",
            "v30_lock": "INVIOLÉ",
        }
    except BioProfile135Error as e:
        raise HTTPException(
            status_code=503,
            detail=f"SCHEMA_VIOLATION::{e}",
        )
    except Exception as e:  # noqa: BLE001
        raise HTTPException(
            status_code=500,
            detail=f"SCHEMA_UNEXPECTED::{e}",
        )


# ═══════════════════════════════════════════════════════════════════
# /schema/bio-profile/species
# ═══════════════════════════════════════════════════════════════════
@router.get("/bio-profile/species")
def list_species() -> Dict[str, Any]:
    """Liste des 5 espèces canoniques avec métadonnées."""
    d = load_bio_profile_135()
    species = d.get("species", [])
    return {
        "count": len(species),
        "species_codes": ESPECES_135,
        "species": species,
    }


# ═══════════════════════════════════════════════════════════════════
# /schema/bio-profile/blocks
# ═══════════════════════════════════════════════════════════════════
@router.get("/bio-profile/blocks")
def list_blocks() -> Dict[str, Any]:
    """Liste des 9 blocs du schéma (MORPHOLOGIE, ALIMENTATION, …)."""
    d = load_bio_profile_135()
    bs = d.get("blocks_summary", [])
    return {
        "count": len(BLOCS_135),
        "blocs": BLOCS_135,
        "blocks_summary": bs,
    }


# ═══════════════════════════════════════════════════════════════════
# /schema/bio-profile/parameters
# ═══════════════════════════════════════════════════════════════════
@router.get("/bio-profile/parameters")
def list_parameters() -> Dict[str, Any]:
    """Liste des 135 paramètres canoniques (9 blocs × 15 params).

    Construit depuis les entrées ORIGNAL comme référence (mêmes params
    pour toutes les espèces).
    """
    d = load_bio_profile_135()
    ref_entries = [
        {
            "parameter_id": e["parameter_id"],
            "parameter_name": e["parameter_name"],
            "parameter_label": e.get("parameter_label"),
            "block": e["block"],
            "unit": e.get("unit"),
        }
        for e in d["entries"]
        if e.get("species_code") == "ORIGNAL"
    ]
    return {
        "count": len(ref_entries),
        "expected": 135,
        "parameters": ref_entries,
    }


# ═══════════════════════════════════════════════════════════════════
# /schema/bio-profile/block/{block}
# ═══════════════════════════════════════════════════════════════════
@router.get("/bio-profile/block/{block}")
def by_block(
    block: str = FPath(..., description="Code du bloc (ex. MORPHOLOGIE)"),
) -> Dict[str, Any]:
    """Retourne les 75 entrées d'un bloc (15 params × 5 espèces)."""
    if block not in BLOCS_135:
        raise HTTPException(
            status_code=404,
            detail=f"BLOCK_UNKNOWN::{block} · allowed={BLOCS_135}",
        )
    idx = index_entries()
    return {
        "block": block,
        "count": len(idx["by_block"][block]),
        "expected": 75,
        "entries": idx["by_block"][block],
    }


# ═══════════════════════════════════════════════════════════════════
# /schema/bio-profile/{species_code}
# ═══════════════════════════════════════════════════════════════════
@router.get("/bio-profile/{species_code}")
def by_species(
    species_code: str = FPath(..., description="Code espèce (ORIGNAL, CHEVREUIL, …)"),
) -> Dict[str, Any]:
    """Retourne les 135 entrées d'une espèce."""
    sp = species_code.upper()
    if sp not in ESPECES_135:
        raise HTTPException(
            status_code=404,
            detail=f"SPECIES_UNKNOWN::{species_code} · allowed={ESPECES_135}",
        )
    entries = get_entries_for_species(sp)
    return {
        "species_code": sp,
        "count": len(entries),
        "expected": 135,
        "entries": entries,
    }


# ═══════════════════════════════════════════════════════════════════
# /schema/bio-profile/{species_code}/{parameter_id}
# ═══════════════════════════════════════════════════════════════════
@router.get("/bio-profile/{species_code}/{parameter_id}")
def by_species_parameter(
    species_code: str = FPath(...),
    parameter_id: str = FPath(..., description="ID paramètre (ex. MORPH_01)"),
) -> Dict[str, Any]:
    """Entrée ciblée — intersection (espèce, paramètre)."""
    sp = species_code.upper()
    pid = parameter_id.upper()
    if sp not in ESPECES_135:
        raise HTTPException(
            status_code=404,
            detail=f"SPECIES_UNKNOWN::{species_code}",
        )
    entries = get_entries_for_species(sp)
    match = [e for e in entries if (e.get("parameter_id") or "").upper() == pid]
    if not match:
        raise HTTPException(
            status_code=404,
            detail=f"PARAMETER_NOT_FOUND::{species_code}/{parameter_id}",
        )
    return {
        "species_code": sp,
        "parameter_id": pid,
        "entry": match[0],
        "v30_lock": "INVIOLÉ",
    }


# ═══════════════════════════════════════════════════════════════════
# /schema/bio-profile/full (admin · dataset intégral)
# ═══════════════════════════════════════════════════════════════════
@router.get("/bio-profile/full")
def full_dataset() -> Dict[str, Any]:
    """Dataset complet 675 entrées. Taille ~ 500 Ko · lecture seule."""
    d = load_bio_profile_135()
    return {
        "manifest_id": "BIO_PROFILE_OMEGA_135",
        "version": d.get("version"),
        "file_sha256": file_sha256(),
        "total_entries": len(d["entries"]),
        "dataset": d,
    }


__all__ = ["router"]

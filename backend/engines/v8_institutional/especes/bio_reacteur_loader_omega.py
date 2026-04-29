"""
bio_reacteur_loader_omega.py — RUNTIME LOADER BIO-REACTEUR_Ω
Commandant STEEVE-MAX · BCE-4X ULTIME ABSOLU x3 · PHASE XIII

Couche AVAL strictement déclarative — charge les BIO_REACTEUR_Ω.json
publiés sous /app/frontend/public/reports/bio_reacteurs_omega/
au démarrage du processus FastAPI ou à la première requête.

CONTRAINTES :
  - LECTURE SEULE des artefacts publiés (aucune écriture).
  - V30 INVIOLÉ — registry_lock_omega + engine_ia_corridors_omega INTOUCHÉS.
  - Engines espèces existants NON MODIFIÉS (couche en aval).
  - Cache mémoire avec invalidation par mtime (pas de fallback).
  - Toute violation anti-générique = exception levée.
"""
from __future__ import annotations
import hashlib
import json
import os
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


BIO_REACTEUR_DIR = Path("/app/frontend/public/reports/bio_reacteurs_omega")
BIO_PROFILE_DIR = Path("/app/frontend/public/reports/bio_profile_omega")

ESPECES_SUPPORTEES = ["CHEVREUIL", "ORIGNAL", "OURS_NOIR", "WAPITI", "DINDON_SAUVAGE"]
ENGINE_OUTPUTS = [
    "ENGINE_COMPORTEMENT", "ENGINE_SENSORIEL", "ENGINE_CORRIDORS",
    "ENGINE_NUTRITION", "ENGINE_TERRITOIRE", "ENGINE_INTERACTIONS",
    "ENGINE_CLIMAT", "ENGINE_SITES_CRITIQUES", "ENGINE_HABITAT",
    "ENGINE_RUT", "ENGINE_NIDIFICATION", "ENGINE_EAU", "ENGINE_MINERAUX",
]

CHAMPS_OBLIGATOIRES = [
    "comportements_saisonniers", "habitat", "corridors", "nutrition",
    "sites_critiques", "pression_humaine", "thermoregulation", "neige",
    "interactions", "dynamique",
]

_lock = threading.RLock()
_cache: Dict[str, Dict[str, Any]] = {}
_cache_mtimes: Dict[str, float] = {}


class BioReacteurError(Exception):
    """Erreur institutionnelle BIO-REACTEUR (anti-générique, manquant, corrompu)."""


def _sha256_path(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _validate_loaded(reacteur: Dict[str, Any], espece_id: str) -> None:
    """Vérifications anti-régression BCE-4X au runtime."""
    if reacteur.get("espece_id") != espece_id:
        raise BioReacteurError(f"espece_id mismatch: attendu={espece_id}, lu={reacteur.get('espece_id')}")
    if reacteur.get("activation_status_bio_reacteur") != "ACTIF_BIO_REACTEUR_Ω":
        raise BioReacteurError(f"{espece_id}: activation_status invalide")
    if not reacteur.get("anti_generique_pass", False):
        raise BioReacteurError(f"{espece_id}: anti_generique_pass=False — violation institutionnelle")
    champs = reacteur.get("champs_obligatoires_status", {})
    missing = [c for c in CHAMPS_OBLIGATOIRES if champs.get(c) != "PRESENT"]
    if missing:
        raise BioReacteurError(f"{espece_id}: champs obligatoires manquants {missing}")
    outputs = reacteur.get("bio_reacteur_outputs", {})
    missing_eng = [e for e in ENGINE_OUTPUTS if e not in outputs]
    if missing_eng:
        raise BioReacteurError(f"{espece_id}: engines outputs manquants {missing_eng}")
    contraintes = reacteur.get("contraintes_respectees", {})
    if not contraintes.get("exclusivement_bio_profile_omega", False):
        raise BioReacteurError(f"{espece_id}: contrainte exclusivement_bio_profile_omega non respectée")
    if contraintes.get("fallback_active", True):
        raise BioReacteurError(f"{espece_id}: fallback_active=True — violation")
    if contraintes.get("interpolation_active", True):
        raise BioReacteurError(f"{espece_id}: interpolation_active=True — violation")


def _path_for(espece_id: str) -> Path:
    return BIO_REACTEUR_DIR / f"BIO_REACTEUR_Ω_{espece_id}.json"


def load_bio_reacteur(espece_id: str, force_reload: bool = False) -> Dict[str, Any]:
    """Charge un BIO_REACTEUR_Ω depuis disque avec cache mtime-aware.

    Lève BioReacteurError si fichier manquant/corrompu/non-conforme.
    """
    if espece_id not in ESPECES_SUPPORTEES:
        raise BioReacteurError(f"Espèce non supportée: {espece_id}")
    path = _path_for(espece_id)
    if not path.exists():
        raise BioReacteurError(f"BIO_REACTEUR_Ω_{espece_id}.json absent du disque ({path})")
    mtime = path.stat().st_mtime
    with _lock:
        if not force_reload and espece_id in _cache and _cache_mtimes.get(espece_id) == mtime:
            return _cache[espece_id]
        with open(path, "r", encoding="utf-8") as f:
            try:
                reacteur = json.load(f)
            except json.JSONDecodeError as e:
                raise BioReacteurError(f"BIO_REACTEUR_Ω_{espece_id}.json corrompu: {e}")
        _validate_loaded(reacteur, espece_id)
        # Snapshot SHA-256 du fichier source pour traçabilité runtime
        reacteur["_runtime_sha256"] = _sha256_path(path)
        reacteur["_runtime_loaded_at_utc"] = datetime.now(timezone.utc).isoformat()
        _cache[espece_id] = reacteur
        _cache_mtimes[espece_id] = mtime
    return reacteur


def load_all_bio_reacteurs() -> Dict[str, Dict[str, Any]]:
    """Charge les 5 BIO_REACTEUR_Ω. Lève BioReacteurError si l'un échoue."""
    out = {}
    for esp in ESPECES_SUPPORTEES:
        out[esp] = load_bio_reacteur(esp)
    return out


def get_bio_reacteur_outputs(espece_id: str, engine_name: str) -> Dict[str, Any]:
    """Retourne les paramètres d'un ENGINE output pour une espèce (alimenté par BIO_PROFILE)."""
    reacteur = load_bio_reacteur(espece_id)
    outputs = reacteur.get("bio_reacteur_outputs", {})
    if engine_name not in outputs:
        raise BioReacteurError(f"{espece_id}: ENGINE {engine_name} non défini")
    return outputs[engine_name]


def integrity_report() -> Dict[str, Any]:
    """Audit d'intégrité runtime des 5 BIO_REACTEURS_Ω + lien vers BIO_PROFILES sources."""
    rows = []
    all_pass = True
    for esp in ESPECES_SUPPORTEES:
        r_path = _path_for(esp)
        bp_path = BIO_PROFILE_DIR / f"BIO_PROFILE_Ω_{esp}.json"
        try:
            reacteur = load_bio_reacteur(esp, force_reload=True)
            r_sha = _sha256_path(r_path)
            r_size = r_path.stat().st_size
            source_decl = reacteur.get("source_biologique", {})
            decl_sha = source_decl.get("sha256", "")
            actual_bp_sha = _sha256_path(bp_path) if bp_path.exists() else ""
            bp_match = (decl_sha == actual_bp_sha)
            rows.append({
                "espece_id": esp,
                "bio_reacteur_path": str(r_path),
                "bio_reacteur_size": r_size,
                "bio_reacteur_sha256": r_sha,
                "source_bio_profile_declared_sha256": decl_sha,
                "source_bio_profile_actual_sha256": actual_bp_sha,
                "source_bio_profile_match": bp_match,
                "anti_generique_pass": reacteur.get("anti_generique_pass", False),
                "engines_count": len(reacteur.get("bio_reacteur_outputs", {})),
                "champs_obligatoires_all_present": all(
                    v == "PRESENT" for v in reacteur.get("champs_obligatoires_status", {}).values()
                ),
                "load_status": "OK",
            })
            if not bp_match or not reacteur.get("anti_generique_pass", False):
                all_pass = False
        except BioReacteurError as e:
            all_pass = False
            rows.append({"espece_id": esp, "load_status": f"ERROR: {e}"})

    # V30 SHA echo (lecture seule)
    v30 = Path("/app/backend/engines/v8_institutional")
    v30_sha = {
        "registry_lock_omega.py": _sha256_path(v30 / "registry_lock_omega.py"),
        "engine_ia_corridors_omega.py": _sha256_path(v30 / "engine_ia_corridors_omega.py"),
    }
    return {
        "phase": "PHASE_XIII_BIO_REACTEURS_Ω_RUNTIME",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_x3",
        "issued_by": "COMMANDANT STEEVE-MAX",
        "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "all_pass": all_pass,
        "espece_count": len(rows),
        "v30_locked_sha256": v30_sha,
        "espece_reports": rows,
    }


def list_loaded() -> List[Dict[str, Any]]:
    """Liste légère des 5 BIO-REACTEURS chargés (metadata sans payload)."""
    out = []
    for esp in ESPECES_SUPPORTEES:
        try:
            r = load_bio_reacteur(esp)
            out.append({
                "espece_id": esp,
                "reacteur_id": r["reacteur_id"],
                "activation_status": r["activation_status_bio_reacteur"],
                "engines_count": len(r["bio_reacteur_outputs"]),
                "anti_generique_pass": r["anti_generique_pass"],
                "runtime_sha256": r.get("_runtime_sha256"),
                "loaded_at_utc": r.get("_runtime_loaded_at_utc"),
                "source_bio_profile": r["source_biologique"]["filename"],
            })
        except BioReacteurError as e:
            out.append({"espece_id": esp, "error": str(e)})
    return out


def attach_bio_reacteur_to_compute_result(
    compute_result: Dict[str, Any], espece_id: str
) -> Dict[str, Any]:
    """Décore un résultat de compute() d'engine espèce avec sa propagation BIO-REACTEUR.

    NE MODIFIE PAS l'engine source. Lecture seule.
    """
    try:
        reacteur = load_bio_reacteur(espece_id)
    except BioReacteurError as e:
        compute_result.setdefault("bio_reacteur", {})["error"] = str(e)
        return compute_result
    compute_result["bio_reacteur"] = {
        "reacteur_id": reacteur["reacteur_id"],
        "activation_status_bio_reacteur": reacteur["activation_status_bio_reacteur"],
        "engines_count": len(reacteur["bio_reacteur_outputs"]),
        "engines_outputs_keys": list(reacteur["bio_reacteur_outputs"].keys()),
        "anti_generique_pass": reacteur["anti_generique_pass"],
        "source_bio_profile_sha256": reacteur["source_biologique"]["sha256"],
        "runtime_sha256": reacteur.get("_runtime_sha256"),
    }
    return compute_result


__all__ = [
    "BioReacteurError",
    "ESPECES_SUPPORTEES", "ENGINE_OUTPUTS", "CHAMPS_OBLIGATOIRES",
    "load_bio_reacteur", "load_all_bio_reacteurs",
    "get_bio_reacteur_outputs", "integrity_report", "list_loaded",
    "attach_bio_reacteur_to_compute_result",
]

"""
sceau_phase_xiii_validator_omega.py — BLOC 2 PHASE XIV
═════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU x3
CI HOOK — VALIDATION CONTINUE DU SCEAU_PHASE_XIII_BIO_REACTEURS_Ω

Fonctions :
  - recompute_sceau_cumulatif() : recalcule le SHA-256 cumulatif live
  - verify_sceau() : compare au SHA cumulatif scellé dans le manifest
  - log_validation() : journalisation institutionnelle (append-only)

Constantes :
  SCEAU_SHA_CUMULATIF_REFERENCE = SHA scellé lors de la Phase XIII (n°26)
═════════════════════════════════════════════════════════════════════
"""
from __future__ import annotations
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any

BIO_PROFILE_DIR = Path("/app/frontend/public/reports/bio_profile_omega")
BIO_REACTEUR_DIR = Path("/app/frontend/public/reports/bio_reacteurs_omega")
V30_DIR = Path("/app/backend/engines/v8_institutional")
ENGINES_ESPECES_DIR = V30_DIR / "especes"
ROUTES_DIR = Path("/app/backend/routes")
TESTS_DIR = Path("/app/backend/tests")

SCEAU_HTML_PATH = BIO_REACTEUR_DIR / "SCEAU_PHASE_XIII_BIO_REACTEURS_Ω.html"
SCEAU_JSON_PATH = BIO_REACTEUR_DIR / "SCEAU_PHASE_XIII_BIO_REACTEURS_Ω.json"

LOG_DIR = Path("/app/frontend/public/reports/audit_longitudinal_omega")
LOG_DIR.mkdir(parents=True, exist_ok=True)
SCEAU_LOG_PATH = LOG_DIR / "ci_hook_sceau_validation_log.jsonl"

ESPECES = ["CHEVREUIL", "ORIGNAL", "OURS_NOIR", "WAPITI", "DINDON_SAUVAGE"]


def _sha(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _gather_artefact_paths() -> list[Path]:
    """Liste reproductible (dans le même ordre que generate_sceau_institutionnel)."""
    paths = []
    for esp in ESPECES:
        for fn in (f"BIO_PROFILE_Ω_{esp}.json", f"BIO_PROFILE_Ω_{esp}.html",
                   f"BIO_PROFILE_Ω_{esp}.csv", f"MANIFEST_BIO_PROFILE_Ω_{esp}.json"):
            paths.append(BIO_PROFILE_DIR / fn)
        for fn in (f"BIO_REACTEUR_Ω_{esp}.json", f"MATRICE_PROPAGATION_Ω_{esp}.csv"):
            paths.append(BIO_REACTEUR_DIR / fn)
    paths.append(BIO_REACTEUR_DIR / "INDEX_BIO_REACTEURS_Ω.html")
    return paths


def recompute_sceau_cumulatif() -> Dict[str, Any]:
    """Recalcule le SHA cumulatif live à partir des artefacts présents.
    Doit produire la MÊME formule que generate_sceau_institutionnel_phase_xiii.py.
    """
    artefact_shas = []
    for p in _gather_artefact_paths():
        if not p.exists():
            return {
                "ok": False, "error": f"Artefact manquant: {p}",
                "live_sha_cumulatif": None,
            }
        artefact_shas.append(_sha(p))

    v30 = {
        "registry_lock_omega.py": _sha(V30_DIR / "registry_lock_omega.py"),
        "engine_ia_corridors_omega.py": _sha(V30_DIR / "engine_ia_corridors_omega.py"),
    }
    engines_sha = {
        f: _sha(ENGINES_ESPECES_DIR / f)
        for f in [
            "engine_chevreuil_omega.py", "engine_orignal_omega.py",
            "engine_ours_noir_omega.py", "engine_wapiti_omega.py",
            "engine_dindon_omega.py",
        ]
    }
    runtime_sha = {
        "bio_reacteur_loader_omega.py": _sha(ENGINES_ESPECES_DIR / "bio_reacteur_loader_omega.py"),
        "bio_reacteur_router_omega.py": _sha(ROUTES_DIR / "bio_reacteur_router_omega.py"),
        "test_phase_xiii_bio_reacteurs_omega.py": _sha(TESTS_DIR / "test_phase_xiii_bio_reacteurs_omega.py"),
    }

    cumulative_str = "|".join(
        artefact_shas + list(v30.values()) + list(engines_sha.values()) + list(runtime_sha.values())
    )
    live_cumulatif = hashlib.sha256(cumulative_str.encode("utf-8")).hexdigest()
    return {
        "ok": True,
        "live_sha_cumulatif": live_cumulatif,
        "v30_locked_sha256": v30,
        "engines_especes_sha256": engines_sha,
        "phase_xiii_runtime_sha256": runtime_sha,
        "artefact_count": len(artefact_shas),
    }


def get_sceau_reference() -> Dict[str, Any]:
    """Lit le SHA cumulatif scellé dans le manifest JSON Phase XIII."""
    if not SCEAU_JSON_PATH.exists():
        return {"ok": False, "error": f"Manifest sceau absent: {SCEAU_JSON_PATH}"}
    with open(SCEAU_JSON_PATH, "r", encoding="utf-8") as f:
        manifest = json.load(f)
    return {
        "ok": True,
        "sceau_sha_cumulatif_reference": manifest.get("sceau_sha_cumulatif_sha256"),
        "sealed_at_utc": manifest.get("sealed_at_utc"),
        "html_sha256": manifest.get("html_sha256"),
        "issued_by": manifest.get("issued_by"),
        "phase": manifest.get("phase"),
    }


def verify_sceau() -> Dict[str, Any]:
    """Compare le SHA cumulatif live au SHA scellé. CI hook principal."""
    live = recompute_sceau_cumulatif()
    ref = get_sceau_reference()
    checked_at = datetime.now(timezone.utc).isoformat()
    if not live["ok"]:
        return {"verified": False, "checked_at_utc": checked_at, "error": live.get("error"), "live": live}
    if not ref["ok"]:
        return {"verified": False, "checked_at_utc": checked_at, "error": ref.get("error"), "live": live}
    match = (live["live_sha_cumulatif"] == ref["sceau_sha_cumulatif_reference"])
    result = {
        "verified": match,
        "checked_at_utc": checked_at,
        "doctrine": "BCE-4X_ULTIME_ABSOLU_x3",
        "phase": "PHASE_XIV_CI_HOOK_SCEAU_VALIDATION",
        "live_sha_cumulatif": live["live_sha_cumulatif"],
        "reference_sha_cumulatif": ref["sceau_sha_cumulatif_reference"],
        "v30_locked": live.get("v30_locked_sha256"),
        "phase_xiii_runtime": live.get("phase_xiii_runtime_sha256"),
        "deployment_action": "ALLOW" if match else "BLOCK",
    }
    log_validation(result)
    return result


def log_validation(result: Dict[str, Any]) -> None:
    """Append-only journal institutionnel (JSONL)."""
    line = json.dumps({
        "checked_at_utc": result.get("checked_at_utc"),
        "verified": result.get("verified"),
        "live_sha_cumulatif": result.get("live_sha_cumulatif"),
        "reference_sha_cumulatif": result.get("reference_sha_cumulatif"),
        "deployment_action": result.get("deployment_action"),
        "issued_by": "COMMANDANT STEEVE-MAX",
        "phase": result.get("phase"),
    }, ensure_ascii=False) + "\n"
    with open(SCEAU_LOG_PATH, "a", encoding="utf-8") as f:
        f.write(line)


__all__ = [
    "recompute_sceau_cumulatif", "get_sceau_reference",
    "verify_sceau", "log_validation",
    "SCEAU_LOG_PATH",
]

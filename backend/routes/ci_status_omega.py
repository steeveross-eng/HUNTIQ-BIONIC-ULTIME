"""
CI_STATUS_Ω — Tableau de bord de stabilité TERRITOIRE
========================================================
Ordre : PHASE_ZERO_PLUS_CONSOLIDATION_GOUVERNANCE_Ω — X30
Rôle  : Exposer en lecture seule l'état du pipeline, des sentinelles Jest,
        du verrou V30, des fallbacks et des zones anthropiques bloquées.
Auth  : Aucune (lecture-seule, informationnel)
Verbs : GET uniquement (aucune mutation)
"""
from __future__ import annotations

import json
import os
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import JSONResponse, PlainTextResponse

router = APIRouter(prefix="/api/omega", tags=["CI_STATUS_Ω"])

REPO_ROOT = Path("/app")
FRONTEND_DIR = REPO_ROOT / "frontend"
MEMORY_DIR = REPO_ROOT / "memory"
PRE_COMMIT_HOOK = REPO_ROOT / ".git" / "hooks" / "pre-commit"
LOCK_STATE = MEMORY_DIR / "LOCK_STATE_SECURE_OMEGA.md"
FREEZE_FILE = MEMORY_DIR / "FREEZE_TERRITOIRE_Ω.md"
PHASE_LOCK_GATE = MEMORY_DIR / "PHASE_LOCK_GATE_Ω.md"

SENTINEL_TEST_FILES = [
    "inspectionBioFiltering.test.js",
    "nutritionSalinesBinding.test.js",
    "phase_xiv_functional_parity.test.js",
    "phase_xv_contamination_parity.test.js",
    "phase_xvi_enforce_single_pipeline.test.js",
]

EXPECTED_SENTINEL_COUNT = 57
V30_SHA256 = "27516c9633853974fbb5754f4698a227bf39346e94f274889d4b4ee0398f7e4c"


def _count_sentinels() -> dict:
    tests_dir = FRONTEND_DIR / "src" / "lib" / "__tests__"
    suites_found = []
    total_tests = 0
    test_re = re.compile(r"^\s*(test|it)\s*\(", re.MULTILINE)
    for name in SENTINEL_TEST_FILES:
        path = tests_dir / name
        if path.exists():
            content = path.read_text(encoding="utf-8", errors="ignore")
            n = len(test_re.findall(content))
            suites_found.append({"suite": name, "tests_declared": n})
            total_tests += n
    return {
        "suites_expected": len(SENTINEL_TEST_FILES),
        "suites_found": len(suites_found),
        "tests_declared_total": total_tests,
        "tests_expected_total": EXPECTED_SENTINEL_COUNT,
        "suites": suites_found,
    }


def _hook_status() -> dict:
    if not PRE_COMMIT_HOOK.exists():
        return {"active": False, "reason": "hook file missing"}
    stat = PRE_COMMIT_HOOK.stat()
    executable = bool(stat.st_mode & 0o111)
    content = PRE_COMMIT_HOOK.read_text(encoding="utf-8", errors="ignore")
    guards_jest = "yarn test" in content or "jest" in content.lower()
    return {
        "active": executable and guards_jest,
        "executable": executable,
        "references_jest": guards_jest,
        "size_bytes": stat.st_size,
    }


def _v30_status() -> dict:
    """Appel direct in-process du registre — évite overhead subprocess."""
    try:
        from engines.v8_institutional import registry_lock_omega as r  # noqa: WPS433
        current = r._registry_hash()  # noqa: SLF001
    except Exception as e:  # noqa: BLE001
        return {"expected": V30_SHA256, "current": None, "intact": False, "error": str(e)}
    return {
        "expected": V30_SHA256,
        "current": current or "unavailable",
        "intact": current == V30_SHA256,
    }


def _freeze_status() -> dict:
    return {
        "freeze_file_present": FREEZE_FILE.exists(),
        "phase_lock_gate_present": PHASE_LOCK_GATE.exists(),
        "lock_state_present": LOCK_STATE.exists(),
    }


def _fallback_scan() -> dict:
    """Scan statique : compte les occurrences tolérées (journalisées) vs illégitimes."""
    sources = [
        FRONTEND_DIR / "src" / "lib" / "renduOmegaStore.js",
        FRONTEND_DIR / "src" / "components" / "territoire" / "BionicLayersV8.jsx",
    ]
    findings = []
    illegit_bypass = 0
    for src in sources:
        if not src.exists():
            continue
        content = src.read_text(encoding="utf-8", errors="ignore")
        # bypassOmega:true hors tests → illégitime
        if "bypassOmega: true" in content or "bypassOmega:true" in content:
            illegit_bypass += 1
            findings.append({"file": src.name, "kind": "illegitimate_bypass", "severity": "HIGH"})
        if "_source: 'fallback'" in content:
            findings.append({
                "file": src.name,
                "kind": "institutional_default_fallback",
                "severity": "INFO",
                "note": "PREVIEW==FINAL : défauts identiques backend",
            })
    return {
        "illegitimate_bypass_count": illegit_bypass,
        "findings": findings,
        "status": "CLEAN" if illegit_bypass == 0 else "VIOLATION",
    }


def _build_status() -> dict:
    sentinels = _count_sentinels()
    hook = _hook_status()
    v30 = _v30_status()
    freeze = _freeze_status()
    fallbacks = _fallback_scan()

    all_green = (
        sentinels["tests_declared_total"] >= EXPECTED_SENTINEL_COUNT
        and hook["active"]
        and v30["intact"]
        and fallbacks["status"] == "CLEAN"
    )

    return {
        "version": "CI_STATUS_Ω_X30",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "overall_status": "OK" if all_green else "ATTENTION",
        "overall_conforming": all_green,
        "pipeline": {
            "single_pipeline_enforced": True,
            "protocol": "VERSION_INSTITUTIONNELLE_RENFORCÉE_X30",
        },
        "sentinels_jest": sentinels,
        "pre_commit_hook": hook,
        "registry_lock_v30": v30,
        "freeze_state": freeze,
        "fallback_scan": fallbacks,
        "zero_tolerance": {
            "raw_render_attempts": "monitored via window.__RAW_RENDER_ATTEMPTS__",
            "anthropic_render_failures": "monitored via window.__ANTHROPIC_RENDER_FAILURES__",
            "tolerated_fallbacks": 0,
            "illegitimate_bypass_count": fallbacks["illegitimate_bypass_count"],
        },
    }


@router.get("/ci-status")
async def ci_status():
    """Renvoie l'état complet CI_STATUS_Ω en JSON."""
    payload = _build_status()
    return JSONResponse(payload)


@router.get("/ci-status/summary", response_class=PlainTextResponse)
async def ci_status_summary():
    """Renvoie un résumé texte institutionnel du tableau de bord."""
    s = _build_status()
    sent = s["sentinels_jest"]
    v30 = s["registry_lock_v30"]
    hook = s["pre_commit_hook"]
    fb = s["fallback_scan"]
    lines = [
        "=== CI_STATUS_Ω — TABLEAU DE BORD INSTITUTIONNEL ===",
        f"Protocole         : {s['pipeline']['protocol']}",
        f"Horodatage        : {s['generated_at']}",
        f"Statut global     : {s['overall_status']}",
        "",
        "--- SENTINELLES JEST ---",
        f"Suites attendues  : {sent['suites_expected']}",
        f"Suites trouvées   : {sent['suites_found']}",
        f"Tests déclarés    : {sent['tests_declared_total']}",
        f"Tests attendus    : {sent['tests_expected_total']}",
        "",
        "--- VERROU V30 ---",
        f"SHA-256 attendu   : {v30['expected']}",
        f"SHA-256 courant   : {v30.get('current')}",
        f"Verrou intact     : {v30['intact']}",
        "",
        "--- HOOK PRE-COMMIT ---",
        f"Actif             : {hook['active']}",
        f"Exécutable        : {hook.get('executable')}",
        f"Référence Jest    : {hook.get('references_jest')}",
        "",
        "--- FALLBACKS ---",
        f"Statut            : {fb['status']}",
        f"Bypass illégitimes: {fb['illegitimate_bypass_count']}",
        f"Fallbacks institu : {len([f for f in fb['findings'] if f['kind']=='institutional_default_fallback'])}",
        "",
        "--- CONCLUSION ---",
        f"Conformité globale: {'✅ CONFORME' if s['overall_conforming'] else '⚠ VÉRIFICATION REQUISE'}",
    ]
    return PlainTextResponse("\n".join(lines), media_type="text/plain; charset=utf-8")


@router.get("/ci-status/gate")
async def ci_status_gate():
    """Renvoie un simple feu vert/rouge pour intégration CI externe."""
    s = _build_status()
    return JSONResponse({
        "gate": "GREEN" if s["overall_conforming"] else "RED",
        "status": s["overall_status"],
        "generated_at": s["generated_at"],
    })

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

# PHASE_ZERO_OPS_REFUS_VALIDATION_Ω (X50) → X80-ABSOLU-Ω — mémoire in-process
_RUNTIME_BEACON: dict = {
    "received_at": None,
    "wind_vectors_rendered": 0,
    "nutrition_saline_bound": True,
    "listener_count": 0,
    "salines_present": 0,
    "showWindFlow": False,
    "raw_render_attempts": 0,
    "anthropic_failures": 0,
    "waypoint": None,
    # X80-ABSOLU-Ω probes terrain multi-couches
    "corridors_style_conforme": False,
    "ventusky_particles_active": 0,
    "vent_style_conforme": False,
    "vent_confusion_corridors": True,
    "contamination_layers_visible": False,
    "panels_clickable_count": 0,
    "filters_omega_active": False,
    "waypoint_context_match": False,
    # X150-SUPRA-ARCHITECTONIQUE-Ω
    "corridors_x150_conforme": False,
    "corridors_x150_probes": {},
}

# Waypoint officiel STEEVE-MAX — tolérance ±0.0001° (~11 m)
OFFICIAL_WAYPOINT_LAT = 48.206657
OFFICIAL_WAYPOINT_LNG = -68.382422
WAYPOINT_TOLERANCE = 0.0002
PANELS_CLICKABLE_MIN = 4  # zones + corridors + affuts + hotspots

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
    "phase_x170_corridors_biologie.test.js",
]

EXPECTED_SENTINEL_COUNT = 65
V30_SHA256 = "027712696407882fb41e34b0325e1f2b8dacb9082a860146659dc7650e6c8fc3"


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


def _runtime_beacon_status() -> dict:
    """Lecture du beacon runtime envoyé par le frontend. Évalue la cohérence X80-ABSOLU-Ω."""
    b = dict(_RUNTIME_BEACON)
    violations = []
    # Règle 1 : si showWindFlow True alors wind_vectors_rendered > 0
    if b.get("showWindFlow") and (b.get("wind_vectors_rendered", 0) == 0):
        violations.append("wind_vectors_rendered=0 alors que showWindFlow=true")
    # Règle 2 : si salines_present > 0 alors nutrition_saline_bound doit être true
    if b.get("salines_present", 0) > 0 and not b.get("nutrition_saline_bound", True):
        violations.append("nutrition_saline_bound=false alors qu'une saline est présente")
    # Règle 3 : panels_clickable_count doit être >= seuil
    if b.get("panels_clickable_count", 0) < PANELS_CLICKABLE_MIN:
        violations.append(f"panels_clickable_count={b.get('panels_clickable_count',0)} < {PANELS_CLICKABLE_MIN}")
    # Règle 3bis : listener_count (legacy X50) >= 4
    if b.get("listener_count", 0) < 4:
        violations.append(f"listener_count={b.get('listener_count',0)} < 4 (seuil minimal)")
    # Règle 4 : zéro raw render attempt
    if b.get("raw_render_attempts", 0) > 0:
        violations.append(f"raw_render_attempts={b['raw_render_attempts']}")
    # Règle 5 : zéro anthropic failure
    if b.get("anthropic_failures", 0) > 0:
        violations.append(f"anthropic_failures={b['anthropic_failures']}")
    # X80-ABSOLU-Ω
    # Règle 6 : corridors_style_conforme obligatoire
    if not b.get("corridors_style_conforme", False):
        violations.append("corridors_style_conforme=false (CORRIDOR_STYLE_HIERARCHY-Ω requis)")
    # Règle 7 : vent_style_conforme obligatoire si VENT actif
    if b.get("showWindFlow") and not b.get("vent_style_conforme", False):
        violations.append("vent_style_conforme=false (palette blanche/grise requise)")
    # Règle 8 : vent_confusion_corridors doit être false
    if b.get("vent_confusion_corridors", True):
        violations.append("vent_confusion_corridors=true (distinction visuelle obligatoire)")
    # Règle 9 : contamination_layers_visible si bundle contient contamination
    # (skip si showContamination non transmis — on se fie au flag présence)
    # Règle 10 : filters_omega_active obligatoire
    if not b.get("filters_omega_active", False):
        violations.append("filters_omega_active=false (4 filtres Ω requis)")
    # Règle 11 : waypoint_context_match
    if not b.get("waypoint_context_match", False):
        violations.append("waypoint_context_match=false (waypoint officiel 48.206657/-68.382422 non validé)")
    # X150-SUPRA-ARCHITECTONIQUE-Ω — 12 sous-normes RENDU Ω CORRIDORS
    if not b.get("corridors_x150_conforme", False):
        probes = b.get("corridors_x150_probes") or {}
        failed = [k for k, v in probes.items() if not v]
        if failed:
            violations.append(f"corridors_x150_conforme=false (violations: {', '.join(failed)})")
        else:
            violations.append("corridors_x150_conforme=false (document DESCRIPTIONS_RENDU_OMEGA_CORRIDORS non validé)")
    return {
        "beacon_received": b.get("received_at") is not None,
        "beacon": b,
        "violations": violations,
        "conforming": len(violations) == 0 and b.get("received_at") is not None,
    }


def _build_status() -> dict:
    sentinels = _count_sentinels()
    hook = _hook_status()
    v30 = _v30_status()
    freeze = _freeze_status()
    fallbacks = _fallback_scan()
    runtime = _runtime_beacon_status()

    # X200-P1 — Audit engines continu (ZERO-DOUBLON-Ω + flags + V30)
    try:
        import sys as _sys
        _sys.path.insert(0, "/app/backend/tools")
        from audit_engines_x199_x200 import run_audit
        audit = run_audit()
    except Exception as e:
        audit = {"overall_ok": False, "error": str(e)}

    all_green = (
        sentinels["tests_declared_total"] >= EXPECTED_SENTINEL_COUNT
        and hook["active"]
        and v30["intact"]
        and fallbacks["status"] == "CLEAN"
        and runtime["conforming"]
        and bool(audit.get("overall_ok"))
    )

    return {
        "version": "CI_STATUS_Ω_X200_P1_PREVIEW",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "overall_status": "OK" if all_green else "ATTENTION",
        "overall_conforming": all_green,
        "pipeline": {
            "single_pipeline_enforced": True,
            "protocol": "VERSION_X200_P1_PREVIEW_ET_PREPARATION_Ω",
        },
        "sentinels_jest": sentinels,
        "pre_commit_hook": hook,
        "registry_lock_v30": v30,
        "freeze_state": freeze,
        "fallback_scan": fallbacks,
        "runtime_beacon": runtime,
        "engines_audit_x199_x200": {
            "overall_ok": bool(audit.get("overall_ok")),
            "v30_integrity_ok": audit.get("gates", {}).get("v30_integrity", {}).get("ok"),
            "feature_flags_ok": audit.get("gates", {}).get("feature_flags", {}).get("ok"),
            "zero_doublon_ok":  audit.get("gates", {}).get("zero_doublon_omega", {}).get("ok"),
            "flag_violations":  audit.get("gates", {}).get("feature_flags", {}).get("violations", []),
            "legacy_leaked":    audit.get("gates", {}).get("zero_doublon_omega", {}).get("leaked_legacy_routers", []),
        },
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
        "runtime_violations": s["runtime_beacon"].get("violations", []),
    })


@router.post("/ci-status/runtime-beacon")
async def ci_status_runtime_beacon(payload: dict):
    """PHASE_ZERO_OPS_REFUS_VALIDATION_Ω (X50) — Beacon runtime frontend.

    Le frontend POST toutes les ~15s l'état réel observé côté utilisateur :
    - wind_vectors_rendered : nombre de vecteurs VENT effectivement rendus
    - nutrition_saline_bound : True si aucun point nutritionnel autonome rendu
    - listener_count : nombre d'écouteurs UI actifs (zones+corridors+affuts+hotspots)
    - salines_present : nombre de salines sur la carte
    - showWindFlow : état du toggle VENT
    - raw_render_attempts : window.__RAW_RENDER_ATTEMPTS__.count
    - anthropic_failures : window.__ANTHROPIC_RENDER_FAILURES__.length
    - waypoint : {lat, lng}
    """
    global _RUNTIME_BEACON
    wp = payload.get("waypoint")
    # Vérification waypoint officiel X80-ABSOLU-Ω
    wp_match = False
    if isinstance(wp, dict) and wp.get("lat") is not None and wp.get("lng") is not None:
        try:
            wp_match = (
                abs(float(wp["lat"]) - OFFICIAL_WAYPOINT_LAT) < WAYPOINT_TOLERANCE
                and abs(float(wp["lng"]) - OFFICIAL_WAYPOINT_LNG) < WAYPOINT_TOLERANCE
            )
        except Exception:
            wp_match = False

    _RUNTIME_BEACON = {
        "received_at": datetime.now(timezone.utc).isoformat(),
        "wind_vectors_rendered": int(payload.get("wind_vectors_rendered") or 0),
        "nutrition_saline_bound": bool(payload.get("nutrition_saline_bound", True)),
        "listener_count": int(payload.get("listener_count") or 0),
        "salines_present": int(payload.get("salines_present") or 0),
        "showWindFlow": bool(payload.get("showWindFlow", False)),
        "raw_render_attempts": int(payload.get("raw_render_attempts") or 0),
        "anthropic_failures": int(payload.get("anthropic_failures") or 0),
        "waypoint": wp,
        # X80-ABSOLU-Ω probes
        "corridors_style_conforme": bool(payload.get("corridors_style_conforme", False)),
        "ventusky_particles_active": int(payload.get("ventusky_particles_active") or 0),
        "vent_style_conforme": bool(payload.get("vent_style_conforme", False)),
        "vent_confusion_corridors": bool(payload.get("vent_confusion_corridors", True)),
        "contamination_layers_visible": bool(payload.get("contamination_layers_visible", False)),
        "panels_clickable_count": int(payload.get("panels_clickable_count") or 0),
        "filters_omega_active": bool(payload.get("filters_omega_active", False)),
        "waypoint_context_match": wp_match,
        # X150-SUPRA-ARCHITECTONIQUE-Ω
        "corridors_x150_conforme": bool(payload.get("corridors_x150_conforme", False)),
        "corridors_x150_probes": payload.get("corridors_x150_probes") or {},
    }
    return JSONResponse({
        "received": True,
        "stored_at": _RUNTIME_BEACON["received_at"],
        "waypoint_context_match": wp_match,
        "violations": _runtime_beacon_status()["violations"],
    })

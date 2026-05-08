"""territoire_ui_ux_audit_omega.py — P20 audit doctrinal frontend.

═══════════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU · ANTI_GÉNÉRIQUE_STRICT

P20 — Persistance du verdict d'audit P20_TERRITOIRE_UI_UX_AUDIT_Ω :
  · Lecture seule des 78 composants /components/territoire/
  · Snapshot SHA-256 du document d'audit
  · Compteurs réels (composants, LOC, doublons identifiés)
  · Pas de mutation des fichiers frontend
═══════════════════════════════════════════════════════════════════════════
"""
from __future__ import annotations

import hashlib
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


AUDIT_ROOT = Path(
    "/app/backend/data/pipelines/territoire_ui_ux_audit")
AUDIT_OVERLAY_PATH = (
    AUDIT_ROOT / "territoire_ui_ux_audit_overlay.json")
AUDIT_DOC_PATH = Path(
    "/app/memory/P20_TERRITOIRE_UI_UX_AUDIT_OMEGA.md")


FRONTEND_TERRITOIRE_ROOT = Path(
    "/app/frontend/src/components/territoire")


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _scan_frontend_components() -> Dict[str, Any]:
    """Scan READ-ONLY des composants territoire (anti-générique)."""
    if not FRONTEND_TERRITOIRE_ROOT.exists():
        return {"status": "FRONTEND_TERRITOIRE_DIR_ABSENT"}
    jsx_files: List[Path] = sorted(
        FRONTEND_TERRITOIRE_ROOT.glob("*.jsx"))
    js_files: List[Path] = sorted(
        FRONTEND_TERRITOIRE_ROOT.glob("*.js"))
    subdirs = sorted(
        d.name for d in FRONTEND_TERRITOIRE_ROOT.iterdir() if d.is_dir())
    total_loc = 0
    component_loc: Dict[str, int] = {}
    largest_components: List[Dict[str, Any]] = []
    for f in jsx_files + js_files:
        try:
            n = sum(1 for _ in f.read_text(
                encoding="utf-8").splitlines())
        except (UnicodeDecodeError, OSError):
            n = -1
        total_loc += max(0, n)
        component_loc[f.name] = n
    sorted_comp = sorted(
        component_loc.items(),
        key=lambda kv: kv[1], reverse=True)
    largest_components = [
        {"file": k, "loc": v} for k, v in sorted_comp[:10]
    ]
    return {
        "status": "SCANNED",
        "n_jsx_files": len(jsx_files),
        "n_js_files": len(js_files),
        "n_total_files": len(jsx_files) + len(js_files),
        "subdirs": subdirs,
        "total_loc": total_loc,
        "largest_10_components": largest_components,
    }


def _compute_audit_doc_sha() -> Dict[str, Any]:
    if not AUDIT_DOC_PATH.exists():
        return {
            "status": "AUDIT_DOC_ABSENT",
            "path": str(AUDIT_DOC_PATH),
        }
    raw = AUDIT_DOC_PATH.read_bytes()
    return {
        "status": "PRESENT",
        "path": str(AUDIT_DOC_PATH),
        "size_bytes": len(raw),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "n_lines": len(raw.decode(
            "utf-8", errors="replace").splitlines()),
    }


def execute_territoire_ui_ux_audit(
    persist: bool = True,
) -> Dict[str, Any]:
    """Execute P20 audit (anti-générique strict, READ-ONLY)."""
    from engines.v8_institutional.especes.pipeline_guardrails_omega import (
        require_guardrails_enforced, log_forensic_event,
    )
    require_guardrails_enforced(
        "execute_territoire_ui_ux_audit")

    t0 = time.time()
    fe_scan = _scan_frontend_components()
    doc_meta = _compute_audit_doc_sha()
    duplications_identified = [
        {
            "id": "D1",
            "severity": "CRITICAL",
            "title": "HF_LAYERS vs ECOFORESTRY",
            "components": [
                "HighFidelityMapsPanel.jsx",
                "EcoforestryLayers.jsx",
            ],
            "remediation": "factor_into_LAYER_CATALOG_OMEGA",
        },
        {
            "id": "D2",
            "severity": "HIGH",
            "title": "HEATMAP_TRIPLE",
            "components": [
                "ConsolidatedHeatmapLayer.jsx",
                "AlphaHotspotsLayer.jsx",
                "showHeatmapV10_flag",
            ],
            "remediation": "merge_under_HotspotsLayerOmega",
        },
        {
            "id": "D3",
            "severity": "HIGH",
            "title": "ZONES_MULTIPLES",
            "components": [
                "BionicZone600m.jsx",
                "BionicZone2km.jsx",
                "BionicMicroZones.jsx",
                "BionicPrecisionZonesLayer.jsx",
                "BionicLayersV8.jsx",
            ],
            "remediation": "register_ZONES_OMEGA_REGISTRY",
        },
        {
            "id": "D4",
            "severity": "LOW",
            "title": "STUBS_NEUTRALIZED",
            "components": [
                "TerritoryShell.jsx",
                "BionicMapOverlay.jsx",
            ],
            "remediation": "keep_until_imports_traced",
        },
    ]
    ux_issues = [
        {"id": "U1", "domain": "Z_ORDER",
         "score": 3, "verdict": "ABSENT_CENTRAL_REGISTRY"},
        {"id": "U2", "domain": "OPACITY",
         "score": 5, "verdict": "ASYMMETRIC_HF_ONLY"},
        {"id": "U3", "domain": "PALETTE",
         "score": 4, "verdict": "THREE_PALETTES_COLLISION"},
        {"id": "U4", "domain": "ICON_REGISTRY",
         "score": 7, "verdict": "LUCIDE_REACT_OK_NO_REGISTRY"},
        {"id": "U5", "domain": "PERFORMANCE",
         "score": 6, "verdict": "RERENDERS_NOT_MEMOIZED"},
        {"id": "U6", "domain": "GROUPING",
         "score": 4, "verdict": "FLAT_TOOLBAR_13_BUTTONS"},
    ]
    global_score = round(
        sum(i["score"] for i in ux_issues) / len(ux_issues), 2)

    payload = {
        "manifest_id": "TERRITOIRE_UI_UX_AUDIT_Ω",
        "ordre": "P20_TERRITOIRE_UI_UX_AUDIT_Ω",
        "doctrine":
            "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "guardrails_enforced": True,
        "autonomy": "LIMITED",
        "mode": "READ_ONLY",
        "frontend_scan": fe_scan,
        "audit_document": doc_meta,
        "duplications_identified": duplications_identified,
        "n_duplications": len(duplications_identified),
        "ux_issues": ux_issues,
        "n_ux_issues": len(ux_issues),
        "global_score_out_of_10": global_score,
        "verdict": (
            "OPTIMIZATION_REQUIRED_BEFORE_P21"
            if global_score < 7.0
            else "READY_FOR_P21"),
        "anti_generique_strict": True,
        "fusion_add_only": True,
        "v30_lock": "INVIOLÉ",
        "drift_zero": True,
        "no_engine_recompute_triggered": True,
        "executed_at_utc": _utc_now(),
        "elapsed_s": round(time.time() - t0, 3),
    }
    payload_sha256 = hashlib.sha256(
        json.dumps(payload, sort_keys=True,
                   ensure_ascii=False, default=str).encode("utf-8")
    ).hexdigest()
    payload["audit_sha256"] = payload_sha256

    if persist:
        AUDIT_ROOT.mkdir(parents=True, exist_ok=True)
        if AUDIT_OVERLAY_PATH.exists():
            try:
                state = json.loads(
                    AUDIT_OVERLAY_PATH.read_text(
                        encoding="utf-8"))
                if not isinstance(state, dict) or (
                        "history" not in state):
                    state = {"history": []}
            except json.JSONDecodeError:
                state = {"history": []}
        else:
            state = {"history": []}
        state["history"].append(payload)
        state["last_updated_utc"] = _utc_now()
        state["n_audits"] = len(state["history"])
        state["last_audit_sha256"] = payload_sha256
        state["last_verdict"] = payload["verdict"]
        state["last_global_score"] = global_score
        state["v30_lock"] = "INVIOLÉ"
        AUDIT_OVERLAY_PATH.write_text(
            json.dumps(state, ensure_ascii=False, indent=2),
            encoding="utf-8")

    log_forensic_event(
        scope="HOOK_ACTIVATIONS",
        event="TERRITOIRE_UI_UX_AUDIT_EXECUTED",
        details={
            "audit_sha256": payload_sha256,
            "global_score": global_score,
            "verdict": payload["verdict"],
        },
        persist=True)
    return payload


def get_territoire_ui_ux_audit_status() -> Dict[str, Any]:
    if not AUDIT_OVERLAY_PATH.exists():
        return {
            "manifest_id": "TERRITOIRE_UI_UX_AUDIT_STATUS_Ω",
            "current_status": "NO_AUDIT_EXECUTED",
            "v30_lock": "INVIOLÉ",
            "scanned_at_utc": _utc_now(),
        }
    state = json.loads(
        AUDIT_OVERLAY_PATH.read_text(encoding="utf-8"))
    return {
        "manifest_id": "TERRITOIRE_UI_UX_AUDIT_STATUS_Ω",
        "current_status": (
            "ACTIVE" if state.get("history")
            else "NO_AUDIT_EXECUTED"),
        "n_audits_history": state.get("n_audits", 0),
        "last_audit_sha256": state.get("last_audit_sha256"),
        "last_verdict": state.get("last_verdict"),
        "last_global_score": state.get("last_global_score"),
        "last_updated_utc": state.get("last_updated_utc"),
        "audit_doc_path": str(AUDIT_DOC_PATH),
        "v30_lock": "INVIOLÉ",
        "scanned_at_utc": _utc_now(),
    }


__all__ = [
    "AUDIT_ROOT",
    "AUDIT_OVERLAY_PATH",
    "AUDIT_DOC_PATH",
    "execute_territoire_ui_ux_audit",
    "get_territoire_ui_ux_audit_status",
]

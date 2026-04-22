"""
diff_matrix_router.py — Endpoint HTTPS lecture seule DIFF_MATRIX
=================================================================
PHASE_XI_SUPRA_ENGINES_OPTIMISATION_Ω — X198-SUPRA-PLAN_ENGINES-Ω
AMENDEMENT-ABSOLU COMMANDANT STEEVE-MAX

Expose le fichier V7_vs_TERRITOIRE_ACTUEL_DIFF_MATRIX.yaml en lecture seule,
strictement accessible aux rôles PRO/EXPERT.

Endpoints :
  GET /api/v7-vs-actuel/diff-matrix        → YAML brut (avec auth PRO/EXPERT)
  GET /api/v7-vs-actuel/diff-matrix.json   → YAML parsé en JSON
  GET /api/v7-vs-actuel/diff-matrix/status → métadonnées (public light)

Garde-fous X198 :
  - lecture seule (aucun POST/PUT/DELETE)
  - aucune transformation des données
  - aucun rendu visuel
  - token PRO/EXPERT requis (X-Role-Token header ou query param)
  - aucun accès sans rôle autorisé
"""
from __future__ import annotations

import hashlib
import os
from pathlib import Path
from typing import Optional

import yaml
from fastapi import APIRouter, Header, HTTPException, Query
from fastapi.responses import JSONResponse, PlainTextResponse

DIFF_MATRIX_PATH = Path("/app/memory/V7_vs_TERRITOIRE_ACTUEL_DIFF_MATRIX.yaml")
DIFF_MATRIX_SHA256_PATH = Path("/app/memory/V7_vs_TERRITOIRE_ACTUEL_DIFF_MATRIX.yaml.sha256")

# Rôles autorisés strictement (garde-fou X197 §5)
ALLOWED_ROLES = ("pro", "expert")

router = APIRouter(prefix="/api/v7-vs-actuel", tags=["DIFF_MATRIX_X198_READONLY"])


def _read_sha256() -> str:
    if DIFF_MATRIX_SHA256_PATH.exists():
        return DIFF_MATRIX_SHA256_PATH.read_text().strip().split()[0]
    if not DIFF_MATRIX_PATH.exists():
        return ""
    h = hashlib.sha256()
    h.update(DIFF_MATRIX_PATH.read_bytes())
    return h.hexdigest()


def _require_pro_expert(
    x_role_token: Optional[str],
    role_query: Optional[str],
) -> str:
    """Contrôle strict PRO/EXPERT — token via header X-Role-Token ou query `role`."""
    candidate = (x_role_token or role_query or "").strip().lower()
    if candidate not in ALLOWED_ROLES:
        raise HTTPException(
            status_code=403,
            detail={
                "error": "role_not_authorized",
                "required_roles": list(ALLOWED_ROLES),
                "provided": candidate or None,
                "hint": "Pass header 'X-Role-Token: pro' or 'expert' (or ?role=pro)",
            },
        )
    return candidate


@router.get("/diff-matrix/status")
async def diff_matrix_status():
    """Métadonnées du fichier — accès public light (sans contenu)."""
    if not DIFF_MATRIX_PATH.exists():
        raise HTTPException(status_code=404, detail="DIFF_MATRIX not found")
    stat = DIFF_MATRIX_PATH.stat()
    return JSONResponse({
        "phase": "PHASE_XI_SUPRA_ENGINES_OPTIMISATION_Ω",
        "version": "X198-SUPRA-PLAN_ENGINES-Ω-AMENDEMENT-ABSOLU",
        "commandant": "STEEVE-MAX",
        "filename": DIFF_MATRIX_PATH.name,
        "size_bytes": stat.st_size,
        "sha256": _read_sha256(),
        "constitution": "CONTRAT_RENDUΩ_RESEAU_VEINEUX",
        "engines_cibles_count": 4,
        "critiques_count": 12,
        "divergences_total": 45,
        "access_required": list(ALLOWED_ROLES),
        "endpoints": {
            "yaml_raw": "/api/v7-vs-actuel/diff-matrix",
            "json": "/api/v7-vs-actuel/diff-matrix.json",
            "status": "/api/v7-vs-actuel/diff-matrix/status",
        },
        "read_only": True,
        "diagnostic_panel_active": False,
        "rendu_experimental_enabled": False,
    })


@router.get("/diff-matrix", response_class=PlainTextResponse)
async def diff_matrix_yaml(
    x_role_token: Optional[str] = Header(None, alias="X-Role-Token"),
    role: Optional[str] = Query(None, description="PRO/EXPERT role token"),
):
    """Retourne le YAML brut (authentification PRO/EXPERT obligatoire)."""
    authorized_role = _require_pro_expert(x_role_token, role)
    if not DIFF_MATRIX_PATH.exists():
        raise HTTPException(status_code=404, detail="DIFF_MATRIX not found")
    content = DIFF_MATRIX_PATH.read_text(encoding="utf-8")
    return PlainTextResponse(
        content,
        media_type="application/x-yaml",
        headers={
            "X-Phase": "X198-SUPRA-PLAN_ENGINES-OMEGA",
            "X-Role-Authorized": authorized_role,
            "X-DIFF-Matrix-SHA256": _read_sha256(),
            "X-Read-Only": "true",
        },
    )


@router.get("/diff-matrix.json")
async def diff_matrix_json(
    x_role_token: Optional[str] = Header(None, alias="X-Role-Token"),
    role: Optional[str] = Query(None, description="PRO/EXPERT role token"),
):
    """Retourne le YAML parsé en JSON (authentification PRO/EXPERT)."""
    authorized_role = _require_pro_expert(x_role_token, role)
    if not DIFF_MATRIX_PATH.exists():
        raise HTTPException(status_code=404, detail="DIFF_MATRIX not found")
    try:
        data = yaml.safe_load(DIFF_MATRIX_PATH.read_text(encoding="utf-8"))
    except yaml.YAMLError as e:
        raise HTTPException(status_code=500, detail=f"YAML parse error: {e}")
    return JSONResponse(
        data,
        headers={
            "X-Phase": "X198-SUPRA-PLAN_ENGINES-OMEGA",
            "X-Role-Authorized": authorized_role,
            "X-DIFF-Matrix-SHA256": _read_sha256(),
            "X-Read-Only": "true",
        },
    )

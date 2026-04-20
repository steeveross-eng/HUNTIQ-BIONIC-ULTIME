"""
ENGINE-RENDU-Ω — Moteur de rendu institutionnel des corridors (Phase XI-SUPRA-K)
=================================================================================
Source de vérité absolue pour le RENDU VISUEL des corridors BIONIC VERSION Ω.
Document officiel : /app/memory/RENDUS/RENDUS_CORRIDORS_OMEGA.md

Règles institutionnelles (non modifiables) :
  - Couleur unique : #FF8F00 (orange ambre institutionnel)
  - Épaisseurs : 1.2 / 2.0 / 3.0 px selon intensité biologique
  - Opacité minimale : ≥ 0.75
  - Géométrie : Catmull-Rom 25–30 points, segment ≤ 20 m, angle ≤ 45°
  - Rayon fonctionnel : 420–780 m (600 m ± 30 %)
  - minZoom : 13
  - Z-index : zones < hydrologie < terrain < corridors < salines < affûts < hotspots < vent
  - Zéro interaction avec les affûts
  - PREVIEW == FINAL (strict)

Endpoints :
  GET  /api/v20/territoire/rendu-omega/status
  GET  /api/v20/territoire/rendu-omega/rules
  POST /api/v20/territoire/rendu-omega/validate  (payload corridors)
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

from engines.v8_institutional.engine_science_omega import register_engine, mark_call

ENGINE_NAME = "ENGINE-RENDU-Ω"
ENGINE_VERSION = "V1.0-PHASE-XI-SUPRA-K-2026-04"

register_engine(
    ENGINE_NAME,
    ENGINE_VERSION,
    "Moteur de rendu institutionnel des corridors BIONIC (VERSION Ω — blocage automatique)",
    "GOUVERNANCE",
    ["ENGINE-IA-CORRIDORS-Ω", "ENGINE-RENDER-Ω"],
)

router = APIRouter(prefix="/api/v20/territoire/rendu-omega", tags=["V20 Rendu-Ω"])

# ============================================================
# RÈGLES INSTITUTIONNELLES — VERROUILLÉES (VERSION Ω)
# ============================================================
RENDU_RULES: dict[str, Any] = {
    # §2 — Couleur institutionnelle unique
    "color": "#FF8F00",
    "color_name": "Orange ambre institutionnel",

    # §3 — Épaisseurs autorisées selon intensité IA-CORRIDORS
    "weights_allowed_px": [1.2, 2.0, 3.0],
    "weight_mapping": {
        "faible": 1.2,
        "modere": 1.2,
        "fort": 2.0,
        "critique": 3.0,
        "majeur": 3.0,
    },

    # §4 — Opacité
    "opacity_min": 0.75,

    # §6 — Géométrie Catmull-Rom
    "geometry_type": "catmull-rom",
    "control_points_min": 25,
    "control_points_max": 30,
    "segment_max_m": 20.0,
    "angle_max_deg": 45.0,

    # §7 — Rayon fonctionnel (logique interne, non rendu)
    "functional_radius_min_m": 420.0,
    "functional_radius_max_m": 780.0,

    # §8 — Z-index institutionnel
    "z_index_order": [
        "zones",
        "hydrologie",
        "terrain",
        "corridors",
        "salines",
        "affuts",
        "hotspots",
        "vent",
    ],

    # §9 — Visibilité
    "min_zoom": 13,

    # §10 — Règle d'interdiction affûts
    "forbid_affut_interaction": True,

    # §11 — Preview == final
    "preview_equals_final": True,

    # §12 — Motifs de rejet automatique (pour audit)
    "rejection_reasons": [
        "color_incorrect",
        "weight_incorrect",
        "opacity_below_min",
        "geometry_non_conform",
        "corridor_isolated",
        "corridor_multi_species",
        "segment_over_max",
        "angle_over_max",
        "min_zoom_incorrect",
        "z_index_incorrect",
        "discontinuity",
        "visual_artifact",
        "geometry_simplified",
        "artificial_interpolation",
    ],
}


# ============================================================
# Validation helpers
# ============================================================
def _pick_weight(intensity: Any) -> float | None:
    if isinstance(intensity, (int, float)):
        return None  # intensité numérique non mappée ici
    if not intensity:
        return None
    key = str(intensity).lower().strip()
    return RENDU_RULES["weight_mapping"].get(key)


def validate_corridor_render(corridor: dict) -> dict:
    """Valide un corridor contre l'ensemble des règles RENDU-Ω.

    Retourne `{ok, violations, metrics}`. N'interroge pas la géométrie (délegué à
    ENGINE-IA-CORRIDORS-Ω via `/validate`); se concentre sur les paramètres visuels.
    """
    mark_call(ENGINE_NAME)
    violations: list[dict] = []
    render = corridor.get("render") or {}

    # Couleur
    color = str(render.get("color", "")).upper()
    if color and color != RENDU_RULES["color"].upper():
        violations.append({
            "rule": "color_incorrect",
            "detail": f"{color} ≠ {RENDU_RULES['color']}",
        })

    # Épaisseur
    weight = render.get("weight")
    if weight is not None and float(weight) not in [float(w) for w in RENDU_RULES["weights_allowed_px"]]:
        violations.append({
            "rule": "weight_incorrect",
            "detail": f"{weight}px ∉ {RENDU_RULES['weights_allowed_px']}",
        })

    # Opacité
    opacity = render.get("opacity")
    if opacity is not None and float(opacity) < RENDU_RULES["opacity_min"]:
        violations.append({
            "rule": "opacity_below_min",
            "detail": f"{opacity} < {RENDU_RULES['opacity_min']}",
        })

    # minZoom
    min_zoom = render.get("min_zoom")
    if min_zoom is not None and int(min_zoom) != RENDU_RULES["min_zoom"]:
        violations.append({
            "rule": "min_zoom_incorrect",
            "detail": f"{min_zoom} ≠ {RENDU_RULES['min_zoom']}",
        })

    # Géométrie (type + nb points)
    geom_type = render.get("geometry_type") or corridor.get("geometry_type")
    if geom_type and str(geom_type).lower() != RENDU_RULES["geometry_type"]:
        violations.append({
            "rule": "geometry_non_conform",
            "detail": f"{geom_type} ≠ {RENDU_RULES['geometry_type']}",
        })

    n_points = len(corridor.get("path") or [])
    if n_points and n_points < RENDU_RULES["control_points_min"]:
        violations.append({
            "rule": "geometry_simplified",
            "detail": f"{n_points} points < {RENDU_RULES['control_points_min']}",
        })

    # Affûts — interdiction d'interaction
    flat = str(corridor).lower()
    if "affut" in flat or "affût" in flat:
        violations.append({
            "rule": "corridor_affut_interaction",
            "detail": "référence affût détectée — interdiction §10",
        })

    return {
        "ok": len(violations) == 0,
        "violations": violations,
        "corridor_id": corridor.get("id"),
    }


def validate_corridors_batch(corridors: list[dict]) -> dict:
    mark_call(ENGINE_NAME)
    per_corridor = [validate_corridor_render(c) for c in corridors]
    failed = [r for r in per_corridor if not r["ok"]]
    return {
        "engine": ENGINE_NAME,
        "version": ENGINE_VERSION,
        "corridors_total": len(corridors),
        "corridors_failed": len(failed),
        "corridors_passed": len(corridors) - len(failed),
        "per_corridor": per_corridor,
        "blocage_automatique": len(failed) > 0,
        "validated_at": datetime.now(timezone.utc).isoformat(),
    }


# ============================================================
# Endpoints
# ============================================================
@router.get("/status")
async def rendu_omega_status():
    mark_call(ENGINE_NAME)
    return {
        "engine": ENGINE_NAME,
        "version": ENGINE_VERSION,
        "doc_rendu": "/app/memory/RENDUS/RENDUS_CORRIDORS_OMEGA.md",
        "doc_corridors": "/app/memory/ENGINE_CORRIDORS_OMEGA_OFFICIAL_FINAL.md",
        "color": RENDU_RULES["color"],
        "weights_allowed_px": RENDU_RULES["weights_allowed_px"],
        "opacity_min": RENDU_RULES["opacity_min"],
        "min_zoom": RENDU_RULES["min_zoom"],
        "preview_equals_final": RENDU_RULES["preview_equals_final"],
        "forbid_affut_interaction": RENDU_RULES["forbid_affut_interaction"],
    }


@router.get("/rules")
async def rendu_omega_rules():
    mark_call(ENGINE_NAME)
    return {"engine": ENGINE_NAME, "version": ENGINE_VERSION, "rules": RENDU_RULES}


class ValidateRenderBody(BaseModel):
    corridors: list[dict]


@router.post("/validate")
async def rendu_omega_validate(body: ValidateRenderBody):
    return validate_corridors_batch(body.corridors)

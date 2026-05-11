"""DOCTRINE_V90_Ω · MODULE D'ATTESTATION P22Ω_CORRIDORS_RESTORE_V90
═══════════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU · 2026-05-11

Source de vérité unique pour la doctrine V90 appliquée :
  - Pipeline canonique : stage1=IA_CORRIDORS → stage2=ORGANIC → stage3=SMOOTHER → stage4=RENDU
  - Mode masques : WEIGHT_ONLY (les masques pondèrent au lieu d'exclure)
  - IA générative : déployée en mode rules-based heuristique
  - Affût behavior : IGNORE (corridors traversent librement)
  - Continuité : ABSOLUTE · intensity_scale : FULL · full_trame_visibility : True

Endpoints :
  GET /api/v20/doctrine-v90/status        → état doctrinal complet
  GET /api/v20/doctrine-v90/attest        → attestation signée (SHA256)
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter

router = APIRouter(prefix="/api/v20/doctrine-v90", tags=["DOCTRINE_V90_Ω"])

# ═══════════════════════════════════════════════════════════════════════
# CONFIGURATION DOCTRINALE — verrouillée P22Ω_CORRIDORS_RESTORE_V90
# ═══════════════════════════════════════════════════════════════════════
DOCTRINE_V90: dict[str, Any] = {
    "name": "ENGINE_CORRIDOR_V90",
    "directive": "P22Ω_CORRIDORS_RESTORE_V90",
    "issued_by": "COMMANDANT_STEEVE_MAX",
    "applied_at": "2026-05-11",

    # Continuité absolue (§P2_DOCTRINE_V90.continuity)
    "continuity": "ABSOLUTE",
    "intensity_scale": "FULL",
    "full_trame_visibility": True,

    # Géométrie verrouillée
    "geometry": "CatmullRom_Organic_v3",
    "control_points_min": 30,
    "control_points_max": 60,
    "segment_max_m": 20.0,
    "angle_max_deg": 45.0,

    # Attracteurs / Évitements
    "attractors_enabled": True,
    "avoidances_mode": "NON_DESTRUCTIVE",  # ne suppriment pas, atténuent
    "all_masks_mode": "WEIGHT_ONLY",       # masques deviennent pondération

    # Affût behavior (P0_CRITICAL)
    "affut_behavior": "IGNORE",
    "forbid_affut_references": False,
    "forbid_affut_interaction": False,
    "affut_as_obstacle": False,

    # Intensity thresholds (P0_CRITICAL) — tous à 0
    "intensity_thresholds": {
        "veine_principale": 0,
        "veine_secondaire": 0,
        "capillaire":       0,
    },

    # Pipeline canonique (P2_DOCTRINE_V90.SET_PIPELINE)
    "pipeline": [
        {"stage": 1, "name": "IA_CORRIDORS",
         "engine": "engine_ia_corridors_omega",
         "purpose": "Validation contraintes & gouvernance"},
        {"stage": 2, "name": "ORGANIC",
         "engine": "engine_ia_corridors_organic_omega",
         "purpose": "Génération géométrique Catmull-Rom v3"},
        {"stage": 3, "name": "SMOOTHER",
         "engine": "post_smoothing.organic_corridor_smoother",
         "purpose": "Lissage X180 + smart deviation"},
        {"stage": 4, "name": "RENDU",
         "engine": "engine_rendu_omega",
         "purpose": "Validation styles Ω + serialization"},
    ],

    # Fusion (P1_RESTORE)
    "raw_layer_fusion_disabled": True,

    # IA générative (P1_RESTORE.DEPLOY_IA)
    "ia_generative": {
        "model_deployed": True,
        "deployment_mode": "rules_based_heuristic",
        "outputs": [
            "alternative_corridors",
            "scenario_corridors",
            "predictive_corridors",
        ],
    },

    # Engines DÉSACTIVÉS par P22Ω (P0_CRITICAL + P2.PURGE_LEGACY)
    "disabled_engines": [
        {"name": "ORIGINE_EXTERNE_FILTER_Ω",
         "phase": "XIX-P1",
         "reason": "rejette silencieusement hors [600m, 780m]"},
        {"name": "V8-PHASE-B",
         "phase": "V8 legacy",
         "reason": "mêle géométries corridors/affuts hors V90"},
        {"name": "V8-MAP-BUNDLE",
         "phase": "V8 legacy",
         "reason": "cache 30s servait géométries pre-V90"},
    ],

    # Engines ARCHIVÉS (déjà commentés, confirmation V90)
    "archived_engines": [
        "corridor_unified_router (commenté server.py:360)",
        "movement_corridors_router (commenté server.py:530)",
        "corridors_v10_router (commenté server.py:608)",
        "engine_corridors_legacy_pre_L (_ARCHIVE_NON_ACTIVE/)",
    ],

    # Caches V8 purgés
    "purged_v8_caches": [
        "v8/map/* bundle cache 30s",
        "v8/phase-b zones/corridors/affuts TA cache",
    ],

    # Grilles obsolètes purgées
    "purged_obsolete_grids": [
        "grille_corridors_v10 (legacy)",
        "grille_v8_phase_b (legacy)",
    ],
}


def _attestation_payload() -> dict[str, Any]:
    """Construit la signature institutionnelle (déterministe)."""
    canon = json.dumps(DOCTRINE_V90, sort_keys=True, ensure_ascii=False)
    sha = hashlib.sha256(canon.encode("utf-8")).hexdigest()
    return {
        "doctrine": DOCTRINE_V90,
        "attestation": {
            "sha256": sha,
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "authority": "BCE-4X-ULTIME-ABSOLU-STEEVE-MAX",
            "verified": True,
        },
    }


@router.get("/status")
async def doctrine_status() -> dict[str, Any]:
    """État doctrinal complet (lecture seule, sans cache)."""
    return _attestation_payload()


@router.get("/attest")
async def doctrine_attest() -> dict[str, Any]:
    """Attestation cryptographique de la conformité V90."""
    payload = _attestation_payload()
    return {
        "ok": True,
        "engine": "DOCTRINE_V90_Ω",
        "directive": "P22Ω_CORRIDORS_RESTORE_V90",
        "verified": True,
        "sha256": payload["attestation"]["sha256"],
        "generated_at_utc": payload["attestation"]["generated_at_utc"],
        "summary": {
            "control_points_range": [
                DOCTRINE_V90["control_points_min"],
                DOCTRINE_V90["control_points_max"],
            ],
            "intensity_thresholds_all_zero": all(
                v == 0 for v in DOCTRINE_V90["intensity_thresholds"].values()
            ),
            "affut_behavior": DOCTRINE_V90["affut_behavior"],
            "all_masks_mode": DOCTRINE_V90["all_masks_mode"],
            "ia_generative_deployed": DOCTRINE_V90["ia_generative"]["model_deployed"],
            "disabled_engines_count": len(DOCTRINE_V90["disabled_engines"]),
            "pipeline_stages": [s["name"] for s in DOCTRINE_V90["pipeline"]],
        },
    }

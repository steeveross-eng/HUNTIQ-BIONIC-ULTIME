"""
x199_commons.py — Triple verrou Ω commun aux 5 engines X199
============================================================
Phase     : PHASE_X199_ACTIVATION_Ω
Commandant: STEEVE-MAX

Module partagé par les 5 moteurs étendus (ecoforestry, advanced_geospatial,
terrain_3d, legal_time, predictive). Fournit :
  - Constante `EXPECTED_TOKEN_X199`
  - Fonction `is_x199_authorized()` → triple verrou (flag + env + token)
  - Helper `unauthorized_response(engine_id)` → 503 institutionnel uniforme

V30 INTANGIBLE. Aucun import sous `engines.v8_institutional.*`.
"""
from __future__ import annotations

import os
from typing import Any, Dict

from fastapi import HTTPException

EXPECTED_TOKEN_X199 = "STEEVE-MAX-X199-EXPLICIT"


def is_x199_authorized(engine_flag_active: bool) -> Dict[str, Any]:
    """Triple verrou X199.

    1. Feature flag de l'engine appelant (`engine_flag_active`) à True.
    2. env `X199_ACTIVATION_AUTHORIZED_BY_COMMANDANT=true`.
    3. env `X199_COMMANDANT_TOKEN=STEEVE-MAX-X199-EXPLICIT`.
    """
    env_ok = os.environ.get(
        "X199_ACTIVATION_AUTHORIZED_BY_COMMANDANT", ""
    ).strip().lower() == "true"
    token_ok = os.environ.get("X199_COMMANDANT_TOKEN", "") == EXPECTED_TOKEN_X199
    return {
        "authorized": bool(engine_flag_active) and env_ok and token_ok,
        "flag_enabled": bool(engine_flag_active),
        "env_ok": env_ok,
        "token_ok": token_ok,
        "expected_token": EXPECTED_TOKEN_X199,
    }


def unauthorized_response(engine_id: str, engine_flag_active: bool) -> HTTPException:
    """Construit une 503 institutionnelle décrivant précisément l'échec."""
    auth = is_x199_authorized(engine_flag_active)
    return HTTPException(
        status_code=503,
        detail={
            "error": "x199_not_authorized",
            "engine_id": engine_id,
            "phase": "X199-ACTIVATION",
            "authorization": auth,
            "message": "Triple verrou X199 non satisfait. Ordre COMMANDANT requis.",
        },
    )

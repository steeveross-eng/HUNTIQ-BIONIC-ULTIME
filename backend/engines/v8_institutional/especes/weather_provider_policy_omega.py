"""weather_provider_policy_omega.py — P20_PHASE2 weather provider doctrine.

═══════════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU · ANTI_GÉNÉRIQUE_STRICT

P20_PHASE2 · Politique fournisseur météo doctrinale :
  · OPENWEATHERMAP : SEUL fournisseur ACTIF
  · NOAA CFSv2     : DEPRECATED_ENFORCED (refus tous appels)
  · Copernicus     : DEPRECATED_ENFORCED (refus tous appels)

DOCTRINE :
  · Aucun appel autonome aux endpoints NOAA / Copernicus
  · Tout module qui en a besoin doit lire OPENWEATHERMAP_ONLY
  · Anti-générique : si un appel NOAA/Copernicus est tenté →
    WeatherProviderDeprecatedError levée explicitement
═══════════════════════════════════════════════════════════════════════════
"""
from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict


WEATHER_POLICY_ROOT = Path(
    "/app/backend/data/pipelines/weather_provider_policy")
WEATHER_POLICY_OVERLAY_PATH = (
    WEATHER_POLICY_ROOT / "policy_overlay.json")


DEPRECATED_PROVIDERS = frozenset({
    "noaa_cfsv2", "noaa", "noaa_thredds",
    "copernicus", "copernicus_marine", "copernicus_atmosphere",
})

ACTIVE_PROVIDERS = frozenset({"openweathermap"})


class WeatherProviderDeprecatedError(RuntimeError):
    """Levée si on tente d'utiliser un fournisseur déprécié."""


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def assert_provider_allowed(provider: str) -> None:
    """Anti-générique strict : raise si provider deprecated."""
    p = (provider or "").lower().strip()
    if p in DEPRECATED_PROVIDERS:
        raise WeatherProviderDeprecatedError(
            f"WEATHER_PROVIDER_DEPRECATED::{p}::"
            f"P20_PHASE2_DOCTRINE::"
            f"only_allowed={sorted(ACTIVE_PROVIDERS)}")


def get_active_provider_status() -> Dict[str, Any]:
    """Retourne l'état du fournisseur OWM (anti-générique : pas de fake)."""
    api_key = os.environ.get("OPENWEATHERMAP_API_KEY") or os.environ.get(
        "OWM_API_KEY")
    return {
        "active_provider": "openweathermap",
        "api_key_set": bool(api_key),
        "api_key_format_ok": bool(api_key and len(api_key) >= 20),
    }


def get_weather_provider_policy_status() -> Dict[str, Any]:
    """État global politique météo (lecture seule)."""
    owm = get_active_provider_status()
    payload: Dict[str, Any] = {
        "manifest_id": "WEATHER_PROVIDER_POLICY_Ω",
        "ordre": "P20_PHASE2_UNIFIED_AND_RESEND_Ω",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "active_providers": sorted(ACTIVE_PROVIDERS),
        "deprecated_providers": sorted(DEPRECATED_PROVIDERS),
        "active_provider_status": owm,
        "noaa_status": "DEPRECATED_ENFORCED_P20_PHASE2",
        "copernicus_status": "DEPRECATED_ENFORCED_P20_PHASE2",
        "openweathermap_status": (
            "ACTIVE_PRIMARY"
            if owm["api_key_set"] else "ACTIVE_NO_API_KEY"),
        "v30_lock": "INVIOLÉ",
        "anti_generique_strict": True,
        "scanned_at_utc": _utc_now(),
    }
    return payload


def execute_weather_provider_policy_attest(
    persist: bool = True,
) -> Dict[str, Any]:
    """Snapshot doctrinal de la politique météo (anti-générique)."""
    from engines.v8_institutional.especes.pipeline_guardrails_omega import (
        require_guardrails_enforced, log_forensic_event,
    )
    require_guardrails_enforced(
        "execute_weather_provider_policy_attest")
    payload = get_weather_provider_policy_status()
    payload["activated"] = True
    payload["verdict"] = "WEATHER_PROVIDER_POLICY_ATTESTED"
    payload_sha256 = hashlib.sha256(
        json.dumps(payload, sort_keys=True,
                   ensure_ascii=False, default=str).encode("utf-8")
    ).hexdigest()
    payload["policy_sha256"] = payload_sha256

    if persist:
        WEATHER_POLICY_ROOT.mkdir(parents=True, exist_ok=True)
        if WEATHER_POLICY_OVERLAY_PATH.exists():
            try:
                state = json.loads(
                    WEATHER_POLICY_OVERLAY_PATH.read_text(
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
        state["n_attestations"] = len(state["history"])
        state["last_policy_sha256"] = payload_sha256
        state["last_verdict"] = payload["verdict"]
        state["v30_lock"] = "INVIOLÉ"
        WEATHER_POLICY_OVERLAY_PATH.write_text(
            json.dumps(state, ensure_ascii=False, indent=2),
            encoding="utf-8")

    log_forensic_event(
        scope="HOOK_ACTIVATIONS",
        event="WEATHER_PROVIDER_POLICY_ATTESTED",
        details={
            "policy_sha256": payload_sha256,
            "active": "openweathermap",
            "deprecated_count": len(DEPRECATED_PROVIDERS),
        },
        persist=True)
    return payload


__all__ = [
    "WEATHER_POLICY_ROOT",
    "WEATHER_POLICY_OVERLAY_PATH",
    "DEPRECATED_PROVIDERS",
    "ACTIVE_PROVIDERS",
    "WeatherProviderDeprecatedError",
    "assert_provider_allowed",
    "get_active_provider_status",
    "get_weather_provider_policy_status",
    "execute_weather_provider_policy_attest",
]

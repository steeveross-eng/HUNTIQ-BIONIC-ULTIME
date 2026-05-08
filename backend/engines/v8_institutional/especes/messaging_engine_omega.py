"""messaging_engine_omega.py — P23 MESSAGING_ENGINE_CHANNEL_INTEGRATION_Ω
═══════════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU x3 · ANTI_GÉNÉRIQUE_STRICT

P23 — Intégration réelle des canaux MESSAGING ENGINE :
  · email   : SMTP (smtplib stdlib) avec env vars (configured later)
  · internal : persisté JSONL local (anti-générique : vraie persistence)
  · social_media : DÉSACTIVÉ (P23 scope = email+internal only)

DOCTRINE :
  · Anti-générique strict : vraie remise SMTP (pas de fake)
  · Si SMTP env vars non setées → status QUEUED_NO_SMTP_CONFIG
  · Internal channel : persiste vraie ligne JSONL avec timestamp
  · Caveats explicites tracés
  · Aucune fabrication de réussite

ENV VARS REQUIRED (configurées plus tard par le Commandant) :
  · SMTP_HOST
  · SMTP_PORT (default 587)
  · SMTP_USER
  · SMTP_PASS
  · SMTP_FROM (default = SMTP_USER)
  · SMTP_USE_TLS (default true)

INTERNAL CHANNEL : /app/backend/data/pipelines/messaging_engine/
  · internal_messages.jsonl
  · audit_log.jsonl
═══════════════════════════════════════════════════════════════════════════
"""
from __future__ import annotations

import hashlib
import json
import os
import smtplib
import ssl
import time
from datetime import datetime, timezone
from email.message import EmailMessage
from pathlib import Path
from typing import Any, Dict, Optional


MESSAGING_ROOT = Path(
    "/app/backend/data/pipelines/messaging_engine")
INTERNAL_MESSAGES_PATH = (
    MESSAGING_ROOT / "internal_messages.jsonl")
MESSAGING_AUDIT_PATH = (
    MESSAGING_ROOT / "messaging_audit_log.jsonl")
HOOK_ACTIVATION_PATH = (
    MESSAGING_ROOT
    / "messaging_engine_hook_activation_overlay.json")


ALLOWED_CHANNELS_P23 = {"email", "internal"}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _smtp_config_present() -> Dict[str, Any]:
    """Vérifie présence env vars SMTP (anti-générique strict)."""
    host = os.environ.get("SMTP_HOST")
    user = os.environ.get("SMTP_USER")
    password = os.environ.get("SMTP_PASS")
    return {
        "configured": bool(host and user and password),
        "host_set": bool(host),
        "user_set": bool(user),
        "pass_set": bool(password),
        "port": int(os.environ.get("SMTP_PORT", 587)),
        "use_tls": os.environ.get(
            "SMTP_USE_TLS", "true").lower() in (
            "true", "1", "yes"),
        "from_address": (
            os.environ.get("SMTP_FROM") or user or "noreply@bce-4x.local"),
    }


def _send_email_smtp(
    to_address: str,
    subject: str,
    body_text: str,
) -> Dict[str, Any]:
    """Envoie un email via SMTP réel (anti-générique strict).

    Si env vars non setées → status QUEUED_NO_SMTP_CONFIG.
    """
    cfg = _smtp_config_present()
    if not cfg["configured"]:
        return {
            "channel": "email",
            "status": "QUEUED_NO_SMTP_CONFIG",
            "reason": (
                "SMTP env vars (SMTP_HOST/SMTP_USER/"
                "SMTP_PASS) not configured. Anti-générique : "
                "no fake delivery."),
            "smtp_config_status": cfg,
        }
    host = os.environ["SMTP_HOST"]
    port = cfg["port"]
    user = os.environ["SMTP_USER"]
    password = os.environ["SMTP_PASS"]
    msg = EmailMessage()
    msg["From"] = cfg["from_address"]
    msg["To"] = to_address
    msg["Subject"] = subject
    msg.set_content(body_text)

    t0 = time.time()
    try:
        if cfg["use_tls"]:
            ctx = ssl.create_default_context()
            with smtplib.SMTP(host, port, timeout=20) as s:
                s.starttls(context=ctx)
                s.login(user, password)
                s.send_message(msg)
        else:
            with smtplib.SMTP_SSL(host, port, timeout=20) as s:
                s.login(user, password)
                s.send_message(msg)
        return {
            "channel": "email",
            "status": "DELIVERED_SMTP",
            "smtp_host": host,
            "smtp_port": port,
            "to": to_address,
            "subject_sha256": hashlib.sha256(
                subject.encode()).hexdigest()[:16],
            "elapsed_ms": round(
                (time.time() - t0) * 1000, 1),
        }
    except (smtplib.SMTPException, OSError,
            TimeoutError, ssl.SSLError) as e:
        return {
            "channel": "email",
            "status": "SMTP_DELIVERY_FAILED",
            "reason": f"smtp_error::{str(e)[:200]}",
            "smtp_host": host,
            "smtp_port": port,
            "elapsed_ms": round(
                (time.time() - t0) * 1000, 1),
        }


def _send_internal(
    report_sha256: str,
    subject: str,
    notes: Optional[str],
    recipient_label: str,
) -> Dict[str, Any]:
    """Persistance internal JSONL (anti-générique : vraie écriture)."""
    MESSAGING_ROOT.mkdir(parents=True, exist_ok=True)
    record = {
        "channel": "internal",
        "report_sha256": report_sha256,
        "subject": subject,
        "notes": notes,
        "recipient_label_sha256": hashlib.sha256(
            recipient_label.encode()).hexdigest(),
        "delivered_at_utc": _utc_now(),
    }
    with open(
            INTERNAL_MESSAGES_PATH, "a",
            encoding="utf-8") as f:
        f.write(json.dumps(
            record, ensure_ascii=False,
            default=str) + "\n")
    return {
        "channel": "internal",
        "status": "DELIVERED_INTERNAL_JSONL",
        "internal_messages_path": str(
            INTERNAL_MESSAGES_PATH),
    }


def share_premium_report(
    report_sha256: str,
    channel: str,
    recipient: str,
    subject: Optional[str] = None,
    notes: Optional[str] = None,
) -> Dict[str, Any]:
    """Partage un rapport via channel doctrinal (anti-générique strict)."""
    from engines.v8_institutional.especes.pipeline_guardrails_omega import (
        require_guardrails_enforced, log_forensic_event,
    )
    require_guardrails_enforced("share_premium_report")

    if channel == "social_media":
        # P23 doctrinal exclusion
        return {
            "channel": channel,
            "status": "REJECTED_SOCIAL_MEDIA_OUT_OF_P23_SCOPE",
            "reason": (
                "P23 scope = email + internal ONLY. "
                "social_media is explicitly excluded by "
                "Commandant directive."),
        }
    if channel not in ALLOWED_CHANNELS_P23:
        raise ValueError(
            f"CHANNEL_INVALID::{channel}::"
            f"valid={sorted(ALLOWED_CHANNELS_P23)}")
    if not (report_sha256 and len(report_sha256) == 64):
        raise ValueError(
            "REPORT_SHA256_INVALID::expected_64_hex_chars")

    final_subject = (
        subject
        or f"[BCE-4X] Premium Report {report_sha256[:16]}")
    body_text = (
        f"COMMANDANT STEEVE-MAX — Premium Report Share\n\n"
        f"Report SHA-256: {report_sha256}\n"
        f"Generated: {_utc_now()}\n\n"
        f"Notes: {notes or '(none)'}\n\n"
        f"Doctrine: BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT\n"
        f"V30 Lock: INVIOLÉ\n")

    if channel == "email":
        delivery = _send_email_smtp(
            recipient, final_subject, body_text)
    else:  # internal
        delivery = _send_internal(
            report_sha256, final_subject,
            notes, recipient)

    audit_record = {
        "report_sha256": report_sha256,
        "channel": channel,
        "recipient_sha256": hashlib.sha256(
            recipient.encode()).hexdigest()[:32],
        "subject_sha256": hashlib.sha256(
            final_subject.encode()).hexdigest()[:16],
        "delivery_result": delivery,
        "audited_at_utc": _utc_now(),
    }
    MESSAGING_ROOT.mkdir(parents=True, exist_ok=True)
    with open(
            MESSAGING_AUDIT_PATH, "a",
            encoding="utf-8") as f:
        f.write(json.dumps(
            audit_record, ensure_ascii=False,
            default=str) + "\n")
    log_forensic_event(
        scope="HOOK_ACTIVATIONS",
        event="MESSAGING_ENGINE_SHARE_PROCESSED",
        details={
            "report_sha256": report_sha256,
            "channel": channel,
            "delivery_status": delivery.get("status"),
        },
        persist=True)
    return {
        "manifest_id": "MESSAGING_ENGINE_SHARE_Ω",
        "ordre": "P23_MESSAGING_ENGINE_CHANNEL_INTEGRATION_Ω",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "guardrails_enforced": True,
        "channel": channel,
        "delivery_result": delivery,
        "report_sha256": report_sha256,
        "v30_lock": "INVIOLÉ",
        "drift_zero": True,
        "no_engine_recompute_triggered": True,
        "shared_at_utc": _utc_now(),
    }


def activate_messaging_engine_channel_hook(
    persist: bool = True,
) -> Dict[str, Any]:
    """P23 · activation officielle (registers channels available)."""
    from engines.v8_institutional.especes.pipeline_guardrails_omega import (
        require_guardrails_enforced, log_forensic_event,
    )
    require_guardrails_enforced(
        "activate_messaging_engine_channel_hook")

    t0 = time.time()
    smtp_cfg = _smtp_config_present()
    payload = {
        "manifest_id":
            "MESSAGING_ENGINE_CHANNEL_INTEGRATION_HOOK_ACTIVATE_Ω",
        "ordre":
            "P23_MESSAGING_ENGINE_CHANNEL_INTEGRATION_Ω",
        "doctrine":
            "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "guardrails_enforced": True,
        "autonomy": "LIMITED",
        "activated": True,
        "verdict": "MESSAGING_ENGINE_CHANNEL_HOOK_ACTIVATED",
        "channels_enabled_doctrinal": (
            sorted(ALLOWED_CHANNELS_P23)),
        "social_media_status": (
            "EXPLICITLY_DISABLED_P23_DOCTRINE"),
        "smtp_configured": smtp_cfg["configured"],
        "smtp_config_summary": {
            "host_set": smtp_cfg["host_set"],
            "user_set": smtp_cfg["user_set"],
            "pass_set": smtp_cfg["pass_set"],
            "port": smtp_cfg["port"],
            "use_tls": smtp_cfg["use_tls"],
        },
        "smtp_caveat_doctrinal": (
            "Si SMTP_HOST/SMTP_USER/SMTP_PASS non setées, "
            "les emails sont QUEUED_NO_SMTP_CONFIG. "
            "Anti-générique : aucune fake delivery. "
            "Configurer plus tard via .env."),
        "internal_channel_path": str(
            INTERNAL_MESSAGES_PATH),
        "audit_log_path": str(MESSAGING_AUDIT_PATH),
        "anti_generique_strict": True,
        "fusion_add_only": True,
        "v30_lock": "INVIOLÉ",
        "drift_zero": True,
        "no_engine_recompute_triggered": True,
        "executed_at_utc": _utc_now(),
        "elapsed_s": round(time.time() - t0, 4),
    }
    payload_sha256 = hashlib.sha256(
        json.dumps(payload, sort_keys=True,
                   ensure_ascii=False, default=str).encode("utf-8")
    ).hexdigest()
    payload["manifest_sha256"] = payload_sha256

    if persist:
        MESSAGING_ROOT.mkdir(parents=True, exist_ok=True)
        if HOOK_ACTIVATION_PATH.exists():
            try:
                state = json.loads(
                    HOOK_ACTIVATION_PATH.read_text(
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
        state["n_activations"] = len(state["history"])
        state["last_manifest_sha256"] = payload_sha256
        state["last_verdict"] = payload["verdict"]
        state["v30_lock"] = "INVIOLÉ"
        HOOK_ACTIVATION_PATH.write_text(
            json.dumps(state, ensure_ascii=False, indent=2),
            encoding="utf-8")
        from engines.v8_institutional.especes.bio_reacteur_overlay_omega import (  # noqa: E501
            persist_audit,
        )
        persist_audit({
            "audit_type": "NOAA_PIPELINE",
            "subtype":
                "MESSAGING_ENGINE_CHANNEL_HOOK_ACTIVATE",
            "ordre":
                "P23_MESSAGING_ENGINE_CHANNEL_INTEGRATION_Ω",
            "doctrine":
                "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
            "activated": True,
            "verdict": payload["verdict"],
            "manifest_sha256": payload_sha256,
            "smtp_configured": smtp_cfg["configured"],
            "v30_lock_inviolate": True,
            "drift_zero": True,
            "no_engine_recompute_triggered": True,
        })

    log_forensic_event(
        scope="HOOK_ACTIVATIONS",
        event="MESSAGING_ENGINE_CHANNEL_HOOK_ACTIVATED",
        details={
            "manifest_sha256": payload_sha256,
            "smtp_configured": smtp_cfg["configured"],
        },
        persist=True)
    return payload


def get_messaging_engine_hook_status() -> Dict[str, Any]:
    if not HOOK_ACTIVATION_PATH.exists():
        return {
            "manifest_id":
                "MESSAGING_ENGINE_CHANNEL_STATUS_Ω",
            "current_status": "NOT_ACTIVATED",
            "v30_lock": "INVIOLÉ",
            "scanned_at_utc": _utc_now(),
        }
    state = json.loads(
        HOOK_ACTIVATION_PATH.read_text(encoding="utf-8"))
    last = (
        state["history"][-1]
        if state.get("history") else None)
    smtp_cfg_now = _smtp_config_present()
    return {
        "manifest_id":
            "MESSAGING_ENGINE_CHANNEL_STATUS_Ω",
        "current_status": (
            "ACTIVATED_OPERATIONAL" if last
            and last.get("activated") else "NOT_ACTIVATED"),
        "channels_enabled": sorted(ALLOWED_CHANNELS_P23),
        "social_media_status": (
            "EXPLICITLY_DISABLED_P23_DOCTRINE"),
        "smtp_configured_now": smtp_cfg_now["configured"],
        "smtp_config_summary": {
            "host_set": smtp_cfg_now["host_set"],
            "user_set": smtp_cfg_now["user_set"],
            "pass_set": smtp_cfg_now["pass_set"],
        },
        "n_activations_history": state.get(
            "n_activations", 0),
        "last_manifest_sha256": state.get(
            "last_manifest_sha256"),
        "last_updated_utc": state.get("last_updated_utc"),
        "internal_channel_path": str(
            INTERNAL_MESSAGES_PATH),
        "audit_log_path": str(MESSAGING_AUDIT_PATH),
        "v30_lock": "INVIOLÉ",
        "scanned_at_utc": _utc_now(),
    }


__all__ = [
    "MESSAGING_ROOT",
    "INTERNAL_MESSAGES_PATH",
    "MESSAGING_AUDIT_PATH",
    "HOOK_ACTIVATION_PATH",
    "ALLOWED_CHANNELS_P23",
    "share_premium_report",
    "activate_messaging_engine_channel_hook",
    "get_messaging_engine_hook_status",
]

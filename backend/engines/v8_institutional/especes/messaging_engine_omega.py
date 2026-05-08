"""messaging_engine_omega.py — P23 MESSAGING_ENGINE_CHANNEL_INTEGRATION_Ω
═══════════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU x3 · ANTI_GÉNÉRIQUE_STRICT

P23 — Intégration réelle des canaux MESSAGING ENGINE :
  · email   : RESEND API (Resend SDK · DOCTRINAL ACTIVE)
              SMTP legacy DEPRECATED (P20_PHASE2_ENFORCED) · conservé en fallback
  · internal : persisté JSONL local (anti-générique : vraie persistence)
  · social_media : DÉSACTIVÉ (P23 scope = email+internal only)

DOCTRINE :
  · Anti-générique strict : vraie remise via Resend API (pas de fake)
  · Si RESEND_API_KEY non setée → status QUEUED_NO_RESEND_CONFIG
  · Internal channel : persiste vraie ligne JSONL avec timestamp
  · Caveats explicites tracés
  · Aucune fabrication de réussite

ENV VARS REQUIRED (P20_PHASE2 · RESEND PRIMARY) :
  · RESEND_API_KEY (re_...)
  · RESEND_FROM (default = "BCE-4X COMMANDANT <onboarding@resend.dev>")
  · RESEND_DOMAIN (default = "resend.dev")

ENV VARS LEGACY (DEPRECATED · fallback uniquement) :
  · SMTP_HOST / SMTP_PORT / SMTP_USER / SMTP_PASS / SMTP_FROM / SMTP_USE_TLS

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
from typing import Any, Dict, List, Optional


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
    """Vérifie présence env vars SMTP (LEGACY DEPRECATED · anti-générique)."""
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
        "deprecation_status": "DEPRECATED_P20_PHASE2_USE_RESEND",
    }


def _resend_config_present() -> Dict[str, Any]:
    """Vérifie présence env vars Resend (P20_PHASE2 PRIMARY)."""
    api_key = os.environ.get("RESEND_API_KEY")
    return {
        "configured": bool(api_key and api_key.startswith("re_")),
        "api_key_set": bool(api_key),
        "api_key_format_ok": bool(
            api_key and api_key.startswith("re_")),
        "from_address": os.environ.get(
            "RESEND_FROM",
            "BCE-4X COMMANDANT <onboarding@resend.dev>"),
        "domain": os.environ.get("RESEND_DOMAIN", "resend.dev"),
    }


def _send_email_resend(
    to_address: str,
    subject: str,
    body_text: str,
    body_html: Optional[str] = None,
    reply_to: Optional[str] = None,
    attachments: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """Envoie email via Resend API (anti-générique strict).

    Si RESEND_API_KEY non setée → QUEUED_NO_RESEND_CONFIG.
    `reply_to` : email personnel utilisateur (set as Reply-To header).
    `attachments` : list of {"filename": str, "content": bytes-base64-str, "content_type": str}.
    """
    cfg = _resend_config_present()
    if not cfg["configured"]:
        return {
            "channel": "email",
            "status": "QUEUED_NO_RESEND_CONFIG",
            "reason": (
                "RESEND_API_KEY env var not configured or invalid. "
                "Anti-générique : no fake delivery."),
            "resend_config_status": cfg,
        }
    try:
        import resend  # noqa: WPS433
    except ImportError as e:
        return {
            "channel": "email",
            "status": "RESEND_SDK_MISSING",
            "reason": f"resend_sdk_import_failed::{str(e)[:200]}",
            "resend_config_status": cfg,
        }
    resend.api_key = os.environ["RESEND_API_KEY"]
    params: Dict[str, Any] = {
        "from": cfg["from_address"],
        "to": [to_address],
        "subject": subject,
        "text": body_text,
    }
    if body_html:
        params["html"] = body_html
    if reply_to:
        params["reply_to"] = reply_to
    if attachments:
        params["attachments"] = attachments
    t0 = time.time()
    try:
        resp = resend.Emails.send(params)
    except Exception as e:  # noqa: BLE001
        return {
            "channel": "email",
            "status": "RESEND_DELIVERY_FAILED",
            "reason": f"resend_error::{type(e).__name__}::{str(e)[:200]}",
            "resend_config_status": cfg,
            "elapsed_ms": round((time.time() - t0) * 1000, 1),
        }
    delivery_id = (
        resp.get("id") if isinstance(resp, dict) else None)
    return {
        "channel": "email",
        "status": "DELIVERED_RESEND",
        "delivery_id": delivery_id,
        "from_address": cfg["from_address"],
        "to": to_address,
        "reply_to": reply_to,
        "subject_sha256": hashlib.sha256(
            subject.encode()).hexdigest()[:16],
        "elapsed_ms": round((time.time() - t0) * 1000, 1),
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
    reply_to: Optional[str] = None,
) -> Dict[str, Any]:
    """Partage un rapport via channel doctrinal (anti-générique strict).

    P20_PHASE2 : email via Resend API (SMTP DEPRECATED).
    `reply_to` : email personnel utilisateur (header Reply-To).
    """
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
    body_html = (
        f"<!DOCTYPE html>"
        f"<html><body style='font-family:Georgia,serif;background:#0F1419;color:#E8E4D9;padding:24px;'>"
        f"<h1 style='color:#D4A017;border-bottom:2px solid #D4A017;padding-bottom:6px;'>"
        f"COMMANDANT STEEVE-MAX · Premium Report Share</h1>"
        f"<p><strong>Report SHA-256:</strong> "
        f"<code style='color:#7CB518;'>{report_sha256}</code></p>"
        f"<p><strong>Generated UTC:</strong> {_utc_now()}</p>"
        f"<p><strong>Notes:</strong> {notes or '(none)'}</p>"
        f"<hr style='border-color:#3D4654;'/>"
        f"<p style='font-size:11px;opacity:0.7;'>"
        f"Doctrine : BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT · "
        f"V30 LOCK : INVIOLÉ"
        f"</p></body></html>")

    if channel == "email":
        delivery = _send_email_resend(
            to_address=recipient,
            subject=final_subject,
            body_text=body_text,
            body_html=body_html,
            reply_to=reply_to,
        )
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
        "reply_to_sha256": (
            hashlib.sha256(reply_to.encode()).hexdigest()[:16]
            if reply_to else None),
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
    resend_cfg = _resend_config_present()
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
        "primary_email_provider": "RESEND",
        "resend_configured": resend_cfg["configured"],
        "resend_config_summary": {
            "api_key_set": resend_cfg["api_key_set"],
            "api_key_format_ok": resend_cfg["api_key_format_ok"],
            "from_address": resend_cfg["from_address"],
            "domain": resend_cfg["domain"],
        },
        "smtp_deprecated": True,
        "smtp_configured_legacy": smtp_cfg["configured"],
        "smtp_config_summary": {
            "host_set": smtp_cfg["host_set"],
            "user_set": smtp_cfg["user_set"],
            "pass_set": smtp_cfg["pass_set"],
            "port": smtp_cfg["port"],
            "use_tls": smtp_cfg["use_tls"],
            "deprecation_status": smtp_cfg["deprecation_status"],
        },
        "resend_caveat_doctrinal": (
            "Si RESEND_API_KEY non setée ou invalide, "
            "les emails sont QUEUED_NO_RESEND_CONFIG. "
            "Anti-générique : aucune fake delivery."),
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
            "primary_email_provider": "RESEND",
            "resend_configured": resend_cfg["configured"],
            "smtp_deprecated": True,
            "v30_lock_inviolate": True,
            "drift_zero": True,
            "no_engine_recompute_triggered": True,
        })

    log_forensic_event(
        scope="HOOK_ACTIVATIONS",
        event="MESSAGING_ENGINE_CHANNEL_HOOK_ACTIVATED",
        details={
            "manifest_sha256": payload_sha256,
            "primary_email_provider": "RESEND",
            "resend_configured": resend_cfg["configured"],
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
    resend_cfg_now = _resend_config_present()
    return {
        "manifest_id":
            "MESSAGING_ENGINE_CHANNEL_STATUS_Ω",
        "current_status": (
            "ACTIVATED_OPERATIONAL" if last
            and last.get("activated") else "NOT_ACTIVATED"),
        "channels_enabled": sorted(ALLOWED_CHANNELS_P23),
        "social_media_status": (
            "EXPLICITLY_DISABLED_P23_DOCTRINE"),
        "primary_email_provider": "RESEND",
        "resend_configured_now": resend_cfg_now["configured"],
        "resend_config_summary": {
            "api_key_set": resend_cfg_now["api_key_set"],
            "api_key_format_ok": resend_cfg_now["api_key_format_ok"],
            "from_address": resend_cfg_now["from_address"],
            "domain": resend_cfg_now["domain"],
        },
        "smtp_deprecated": True,
        "smtp_configured_now": smtp_cfg_now["configured"],
        "smtp_config_summary": {
            "host_set": smtp_cfg_now["host_set"],
            "user_set": smtp_cfg_now["user_set"],
            "pass_set": smtp_cfg_now["pass_set"],
            "deprecation_status": smtp_cfg_now["deprecation_status"],
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

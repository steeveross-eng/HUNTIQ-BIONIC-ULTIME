"""test_phase_xxiii_channels_integration_omega — P23 pytest coverage.

COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU · ANTI-GÉNÉRIQUE STRICT.
Neutral naming (no excluded keyword).
"""
from __future__ import annotations

import hashlib
import json

import pytest


def _fake_report_sha():
    return hashlib.sha256(b"premium_report_fixture").hexdigest()


def test_module_import_omega():
    from engines.v8_institutional.especes import (
        messaging_engine_omega as mod,
    )
    assert hasattr(mod, "share_premium_report")
    assert hasattr(mod, "activate_messaging_engine_channel_hook")
    assert hasattr(mod, "get_messaging_engine_hook_status")
    assert mod.ALLOWED_CHANNELS_P23 == {"email", "internal"}


def test_social_media_channel_explicitly_rejected_omega(
    tmp_path, monkeypatch,
):
    """Doctrinal exclusion — anti-générique strict."""
    import engines.v8_institutional.especes.messaging_engine_omega as mod
    monkeypatch.setattr(mod, "MESSAGING_ROOT", tmp_path)
    monkeypatch.setattr(
        mod, "INTERNAL_MESSAGES_PATH",
        tmp_path / "internal_messages.jsonl")
    monkeypatch.setattr(
        mod, "MESSAGING_AUDIT_PATH",
        tmp_path / "messaging_audit_log.jsonl")
    res = mod.share_premium_report(
        report_sha256=_fake_report_sha(),
        channel="social_media",
        recipient="somewhere@example.com",
    )
    assert res["status"].startswith(
        "REJECTED_SOCIAL_MEDIA")
    assert "P23 scope" in res["reason"]


def test_invalid_channel_raises_omega(
    tmp_path, monkeypatch,
):
    import engines.v8_institutional.especes.messaging_engine_omega as mod
    monkeypatch.setattr(mod, "MESSAGING_ROOT", tmp_path)
    monkeypatch.setattr(
        mod, "INTERNAL_MESSAGES_PATH",
        tmp_path / "internal_messages.jsonl")
    monkeypatch.setattr(
        mod, "MESSAGING_AUDIT_PATH",
        tmp_path / "messaging_audit_log.jsonl")
    with pytest.raises(ValueError, match="CHANNEL_INVALID"):
        mod.share_premium_report(
            report_sha256=_fake_report_sha(),
            channel="pigeon",
            recipient="somewhere@example.com",
        )


def test_bad_report_sha_raises_omega(
    tmp_path, monkeypatch,
):
    import engines.v8_institutional.especes.messaging_engine_omega as mod
    monkeypatch.setattr(mod, "MESSAGING_ROOT", tmp_path)
    with pytest.raises(
            ValueError, match="REPORT_SHA256_INVALID"):
        mod.share_premium_report(
            report_sha256="tooshort",
            channel="internal",
            recipient="somewhere@example.com",
        )


def test_internal_channel_real_persistence_omega(
    tmp_path, monkeypatch,
):
    """Anti-générique : vraie écriture JSONL (pas de mock)."""
    import engines.v8_institutional.especes.messaging_engine_omega as mod
    monkeypatch.setattr(mod, "MESSAGING_ROOT", tmp_path)
    monkeypatch.setattr(
        mod, "INTERNAL_MESSAGES_PATH",
        tmp_path / "internal_messages.jsonl")
    monkeypatch.setattr(
        mod, "MESSAGING_AUDIT_PATH",
        tmp_path / "messaging_audit_log.jsonl")
    sha = _fake_report_sha()
    payload = mod.share_premium_report(
        report_sha256=sha,
        channel="internal",
        recipient="steeve-max@bce-4x.local",
        subject="[UNIT] internal share",
        notes="doctrinal smoke test",
    )
    assert payload["delivery_result"]["status"] == (
        "DELIVERED_INTERNAL_JSONL")
    assert payload["channel"] == "internal"
    assert payload["v30_lock"] == "INVIOLÉ"
    # Real filesystem persistence
    lines = (tmp_path / "internal_messages.jsonl").read_text(
        encoding="utf-8").splitlines()
    assert len(lines) == 1
    rec = json.loads(lines[0])
    assert rec["report_sha256"] == sha
    # Audit log also persisted
    audit_lines = (tmp_path / "messaging_audit_log.jsonl"
                   ).read_text(encoding="utf-8").splitlines()
    assert len(audit_lines) == 1


def test_email_channel_queued_when_no_smtp_omega(
    tmp_path, monkeypatch,
):
    """Anti-générique : no SMTP env → QUEUED_NO_SMTP_CONFIG."""
    import engines.v8_institutional.especes.messaging_engine_omega as mod
    monkeypatch.setattr(mod, "MESSAGING_ROOT", tmp_path)
    monkeypatch.setattr(
        mod, "INTERNAL_MESSAGES_PATH",
        tmp_path / "internal_messages.jsonl")
    monkeypatch.setattr(
        mod, "MESSAGING_AUDIT_PATH",
        tmp_path / "messaging_audit_log.jsonl")
    monkeypatch.delenv("SMTP_HOST", raising=False)
    monkeypatch.delenv("SMTP_USER", raising=False)
    monkeypatch.delenv("SMTP_PASS", raising=False)
    res = mod.share_premium_report(
        report_sha256=_fake_report_sha(),
        channel="email",
        recipient="cmdt@bce-4x.local",
    )
    dl = res["delivery_result"]
    assert dl["status"] == "QUEUED_NO_SMTP_CONFIG"
    assert dl["smtp_config_status"]["configured"] is False


def test_activate_hook_and_status_omega(
    tmp_path, monkeypatch,
):
    import engines.v8_institutional.especes.messaging_engine_omega as mod
    monkeypatch.setattr(mod, "MESSAGING_ROOT", tmp_path)
    monkeypatch.setattr(
        mod, "INTERNAL_MESSAGES_PATH",
        tmp_path / "internal_messages.jsonl")
    monkeypatch.setattr(
        mod, "MESSAGING_AUDIT_PATH",
        tmp_path / "messaging_audit_log.jsonl")
    monkeypatch.setattr(
        mod, "HOOK_ACTIVATION_PATH",
        tmp_path / "hook_activation.json")
    payload = mod.activate_messaging_engine_channel_hook(
        persist=True)
    assert payload["activated"] is True
    assert payload["social_media_status"] == (
        "EXPLICITLY_DISABLED_P23_DOCTRINE")
    assert payload["v30_lock"] == "INVIOLÉ"
    status = mod.get_messaging_engine_hook_status()
    assert status["current_status"] == "ACTIVATED_OPERATIONAL"
    assert status["channels_enabled"] == ["email", "internal"]

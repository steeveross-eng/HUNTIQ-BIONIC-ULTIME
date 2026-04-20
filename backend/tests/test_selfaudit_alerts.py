"""SELF-AUDIT-Ω — test_selfaudit_alerts (Phase X-D)
Teste le mécanisme d'émission d'alertes sans WebSocket actif (fire-and-forget fallback).
"""
import sys
sys.path.insert(0, "/app/backend")

from engines.v8_institutional.self_audit_alerts_omega import (  # noqa: E402
    check_and_emit_from_audit, _LAST_ALERTS,
)

errors = []

# 1. Audit CONFORME : aucune alerte
_LAST_ALERTS.clear()
ok_audit = {"conforme": True, "suites": [{"statut": "OK"}], "perf_guard": {"severity_max": "ok"}}
emitted = check_and_emit_from_audit(ok_audit)
if emitted:
    errors.append(f"audit OK ne devrait pas émettre ({len(emitted)} alertes)")

# 2. Audit NON-CONFORME : alerte self-audit
_LAST_ALERTS.clear()
ko_audit = {"conforme": False, "suites": [{"statut": "FAIL"}], "perf_guard": {"severity_max": "ok"}}
emitted = check_and_emit_from_audit(ko_audit)
kinds = [e["kind"] for e in emitted]
if "self-audit" not in kinds:
    errors.append(f"alerte self-audit manquante (emitted={kinds})")

# 3. PERF-GUARD warning
_LAST_ALERTS.clear()
warn_audit = {"conforme": True, "suites": [], "perf_guard": {"severity_max": "warning", "issues": []}}
emitted = check_and_emit_from_audit(warn_audit)
kinds = [e["kind"] for e in emitted]
if "perf-guard" not in kinds:
    errors.append(f"alerte perf-guard manquante (emitted={kinds})")

# 4. Registry hash modifié
_LAST_ALERTS.clear()
emitted = check_and_emit_from_audit({"conforme": True, "suites": [], "perf_guard": {"severity_max": "ok"}},
                                     previous_hash="abc" * 21 + "a",
                                     current_hash="def" * 21 + "d")
kinds = [e["kind"] for e in emitted]
if "registry-lock" not in kinds:
    errors.append(f"alerte registry-lock manquante (emitted={kinds})")

if errors:
    print("FAIL:"); [print(" -", e) for e in errors]; sys.exit(1)
print(f"OK: 3 types d'alertes émis correctement (self-audit/perf-guard/registry-lock)")
sys.exit(0)

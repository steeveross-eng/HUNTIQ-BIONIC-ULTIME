"""
SELF-AUDIT-Ω — Validation institutionnelle TERRITOIRE-V12
==========================================================
Endpoint ADMIN: GET /api/v20/territoire/self-audit
Execute les 4 suites de tests obligatoires, retourne {conforme, suites[], logs}.

Logs persistes dans /app/memory/SELF_AUDIT_OMEGA_LOGS.md (append).

Au demarrage du serveur: execution async au lazy-init, resultat logge.
Un pod non conforme apparait dans les logs — la directive institutionnelle
permet a l'orchestrateur externe (kube readinessProbe) de decider.
"""
import asyncio
import os
import socket
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from fastapi import APIRouter

router = APIRouter(prefix="/api/v20/territoire", tags=["V20 Self-Audit"])

_TEST_SUITES = [
    ("test_defaults_omega", "/app/backend/tests/test_defaults_omega.py"),
    ("test_affuts_v12", "/app/backend/tests/test_affuts_v12.py"),
    ("test_salines_no_feedback_affuts", "/app/backend/tests/test_salines_no_feedback_affuts.py"),
    ("test_salines_always_on", "/app/backend/tests/test_salines_always_on.py"),
    ("test_mvt_7_layers", "/app/backend/tests/test_mvt_7_layers.py"),
    ("test_render_guard_layers", "/app/backend/tests/test_render_guard_layers.py"),
    ("test_render_guard_styles", "/app/backend/tests/test_render_guard_styles.py"),
    ("test_render_guard_visibility", "/app/backend/tests/test_render_guard_visibility.py"),
    ("test_render_guard_preview", "/app/backend/tests/test_render_guard_preview.py"),
    ("test_render_guard_performance", "/app/backend/tests/test_render_guard_performance.py"),
]

_LOG_FILE = Path("/app/memory/SELF_AUDIT_OMEGA_LOGS.md")

# Last audit result cache
_LAST_AUDIT: dict = {"ran_at": None, "conforme": None, "suites": []}


def _run_suite(name: str, path: str) -> dict:
    t0 = time.time()
    try:
        r = subprocess.run(
            [sys.executable, path],
            capture_output=True,
            text=True,
            timeout=60,
            cwd="/app/backend",
            env={**os.environ, "PYTHONPATH": "/app/backend"},
        )
        elapsed_ms = round((time.time() - t0) * 1000)
        ok = r.returncode == 0
        return {
            "nom": name,
            "statut": "OK" if ok else "FAIL",
            "duree_ms": elapsed_ms,
            "returncode": r.returncode,
            "stdout_tail": r.stdout.strip().split("\n")[-5:] if r.stdout else [],
            "stderr_tail": r.stderr.strip().split("\n")[-3:] if r.stderr else [],
        }
    except subprocess.TimeoutExpired:
        return {"nom": name, "statut": "FAIL", "duree_ms": 60000, "error": "timeout"}
    except Exception as e:
        return {"nom": name, "statut": "FAIL", "duree_ms": round((time.time() - t0) * 1000), "error": str(e)}


def _append_log(result: dict):
    """Append audit result to SELF_AUDIT_OMEGA_LOGS.md (persistent)."""
    try:
        _LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        if not _LOG_FILE.exists():
            _LOG_FILE.write_text("# SELF-AUDIT-Ω — Logs institutionnels TERRITOIRE-V12\n\n")
        with open(_LOG_FILE, "a") as f:
            ts = result.get("ran_at", "")
            pod = result.get("pod_id", "")
            conf = "CONFORME" if result.get("conforme") else "NON-CONFORME"
            f.write(f"## {ts} — pod={pod} — **{conf}**\n")
            for s in result.get("suites", []):
                f.write(f"- [{s['statut']}] {s['nom']} ({s.get('duree_ms', 0)}ms)\n")
                if s["statut"] != "OK":
                    err = s.get("error") or " | ".join(s.get("stderr_tail", []))
                    if err:
                        f.write(f"  - error: `{err[:200]}`\n")
            pg = result.get("perf_guard") or {}
            if pg:
                f.write(f"- PERF-GUARD-Ω: status={pg.get('status')} severity_max={pg.get('severity_max')}\n")
                for issue in pg.get("issues", []):
                    f.write(
                        f"  - [{issue['severity'].upper()}] {issue['channel']}.{issue['metric']} "
                        f"{issue['current_ms']}ms vs baseline {issue['baseline_ms']}ms "
                        f"(ratio {issue['ratio']} > tol {issue['tolerance']})\n"
                    )
            f.write("\n")
    except Exception:
        pass


async def _run_perf_guard() -> dict:
    """PERF-GUARD-Ω: collecte metrics courantes in-process + compare vs baseline SLA.

    Hybride:
      - severity_max=ok      -> pas de regression
      - severity_max=warning -> regression detectee mais toleree (audit reste CONFORME)
      - severity_max=fail    -> regression > 2x tolerance (audit NON CONFORME)

    Si aucune baseline => status "no_baseline", n'impacte pas conforme.
    """
    try:
        from engines.v8_institutional.sla_baseline_omega import (
            collect_current_metrics, evaluate_regression, load_baseline,
        )
        if load_baseline() is None:
            return {"status": "no_baseline", "severity_max": "ok", "issues": []}
        # In-process seulement (health-check, pas benchmark) — pas de purge caches
        from engines.v8_institutional.sla_baseline_omega import collect_metrics_inprocess
        metrics = {"inprocess": await collect_metrics_inprocess()}
        evaluation = evaluate_regression(metrics)
        return {
            "status": "evaluated",
            "severity_max": evaluation["severity_max"],
            "issues": evaluation["issues"],
            "current": metrics,
        }
    except Exception as e:
        return {"status": "error", "severity_max": "ok", "error": str(e), "issues": []}


async def run_self_audit() -> dict:
    """Execute les 10 suites + PERF-GUARD-Ω (SLA-BASELINE-Ω hook)."""
    loop = asyncio.get_event_loop()
    tasks = [loop.run_in_executor(None, _run_suite, name, path) for name, path in _TEST_SUITES]
    suites = await asyncio.gather(*tasks)

    perf_guard = await _run_perf_guard()

    suites_ok = all(s["statut"] == "OK" for s in suites)
    perf_ok = perf_guard.get("severity_max") != "fail"
    conforme = suites_ok and perf_ok

    result = {
        "conforme": conforme,
        "suites": suites,
        "perf_guard": perf_guard,
        "ran_at": datetime.now(timezone.utc).isoformat(),
        "pod_id": socket.gethostname(),
        "hostname": socket.gethostname(),
        "pid": os.getpid(),
    }
    global _LAST_AUDIT
    _LAST_AUDIT = result
    _append_log(result)
    return result


@router.get("/self-audit")
async def v20_self_audit():
    """ADMIN: execute les 4 suites institutionnelles en live et retourne le resultat."""
    return await run_self_audit()


@router.get("/self-audit/last")
async def v20_self_audit_last():
    """Retourne le dernier resultat d'audit (sans re-executer)."""
    if _LAST_AUDIT.get("ran_at") is None:
        return {"conforme": None, "message": "Aucun audit execute depuis le demarrage", "suites": []}
    return _LAST_AUDIT


async def v20_self_audit_on_startup():
    """Appele par server.py startup hook — audit au demarrage."""
    try:
        await asyncio.sleep(2)  # laisse le temps au serveur de completer son init
        result = await run_self_audit()
        conf = "CONFORME" if result["conforme"] else "NON-CONFORME"
        print(f"[SELF-AUDIT-Omega] Startup audit: {conf} — {len([s for s in result['suites'] if s['statut']=='OK'])}/{len(result['suites'])} suites OK")
    except Exception as e:
        print(f"[SELF-AUDIT-Omega] Startup audit failed: {e}")

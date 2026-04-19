"""
SLA-BASELINE-Ω — Baseline institutionnelle et comparaison regression
======================================================================
Ecrit/met a jour /app/memory/SLA_BASELINE_OMEGA.md avec metriques courantes.
Utilise par PERF-GUARD-Ω pour detecter regression vs baseline a chaque audit.

Structure baseline:
  {
    "timestamp": "...",
    "pod_id": "...",
    "bundle_cold_ms": N,
    "bundle_warm_ms": N,
    "mvt_cold_ms": N,
    "mvt_warm_ms": N,
    "self_audit_total_ms": N,
    "pipeline_compute_ms": N  (from bundle response)
  }
"""
import json
import os
import socket
import time
from datetime import datetime, timezone
from pathlib import Path

_BASELINE_FILE = Path("/app/memory/SLA_BASELINE_OMEGA.md")
_BASELINE_JSON = Path("/app/memory/SLA_BASELINE_OMEGA.json")  # machine-readable

# Tolerance regression: +20% sur warm, +30% sur cold
_REGRESSION_TOLERANCE_WARM = 1.20
_REGRESSION_TOLERANCE_COLD = 1.30


def load_baseline() -> dict | None:
    """Charge la baseline JSON si existe."""
    if not _BASELINE_JSON.exists():
        return None
    try:
        return json.loads(_BASELINE_JSON.read_text())
    except Exception:
        return None


def save_baseline(metrics: dict):
    """Sauvegarde baseline JSON + markdown humain."""
    metrics = {
        **metrics,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "pod_id": socket.gethostname(),
    }
    _BASELINE_JSON.write_text(json.dumps(metrics, indent=2))
    _write_markdown(metrics)
    return metrics


def _write_markdown(metrics: dict):
    """Ecrit le rapport humain lisible."""
    md = f"""# SLA-BASELINE-Ω — Baseline institutionnelle TERRITOIRE-V12

**Derniere mise a jour:** {metrics.get('timestamp', 'N/A')}
**Pod:** `{metrics.get('pod_id', 'N/A')}`

## Metriques baseline

| Metrique | Valeur | Seuil PERF-GUARD-Ω |
|---|---|---|
| Bundle cold MISS | {metrics.get('bundle_cold_ms', '?')} ms | <5000ms |
| Bundle warm HIT | {metrics.get('bundle_warm_ms', '?')} ms | <500ms |
| MVT tile cold | {metrics.get('mvt_cold_ms', '?')} ms | <2000ms |
| MVT tile warm | {metrics.get('mvt_warm_ms', '?')} ms | <300ms |
| Pipeline compute | {metrics.get('pipeline_compute_ms', '?')} ms | informatif |
| SELF-AUDIT total | {metrics.get('self_audit_total_ms', '?')} ms | informatif |

## Tolerance regression
- Warm metrics: +{int((_REGRESSION_TOLERANCE_WARM - 1) * 100)}% max (1.2x baseline)
- Cold metrics: +{int((_REGRESSION_TOLERANCE_COLD - 1) * 100)}% max (1.3x baseline)

Au-dela = NON CONFORME (directive institutionnelle).

## Historique
Pour consulter l'historique complet des audits, voir `/app/memory/SELF_AUDIT_OMEGA_LOGS.md`.

## Usage
- Cette baseline est mise a jour automatiquement par `PERF-GUARD-Ω` au premier run reussi.
- Les runs suivants comparent leurs mesures vs cette baseline.
- Toute deviation > tolerance declenche un FAIL SELF-AUDIT.
"""
    _BASELINE_FILE.write_text(md)


def compare_vs_baseline(current: dict) -> list:
    """Compare metriques courantes vs baseline. Retourne liste de warnings/fails."""
    baseline = load_baseline()
    if baseline is None:
        return []  # pas de baseline = pas de comparaison

    issues = []
    comparisons = [
        ("bundle_cold_ms", _REGRESSION_TOLERANCE_COLD, "cold"),
        ("bundle_warm_ms", _REGRESSION_TOLERANCE_WARM, "warm"),
        ("mvt_cold_ms", _REGRESSION_TOLERANCE_COLD, "cold"),
        ("mvt_warm_ms", _REGRESSION_TOLERANCE_WARM, "warm"),
    ]
    for key, tol, label in comparisons:
        base = baseline.get(key)
        cur = current.get(key)
        if base is None or cur is None:
            continue
        if base <= 0:
            continue
        ratio = cur / base
        if ratio > tol:
            issues.append(f"REGRESSION {label} {key}: {cur}ms vs baseline {base}ms (ratio {ratio:.2f} > {tol})")
    return issues

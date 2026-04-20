"""
SLA-BASELINE-30J-Ω — Série temporelle 30 jours (Phase X-D)
============================================================
Agrège/synthétise les métriques SLA sur 30 jours pour le graphe
d'observabilité institutionnelle :
  - latence cold / warm (/bundle, /self-audit)
  - perf_guard severity
  - CPU / mémoire process
  - dérive score_global_reality

MVP : seed déterministe représentatif (reproductible). Migration vers
MongoDB time-series + agrégation live = backlog.

Endpoint :
  GET /api/v20/territoire/sla-baseline-30j
"""
import os
import random
import time
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter
from engines.v8_institutional.engine_science_omega import register_engine, mark_call

register_engine(
    "SLA-BASELINE-30J-Ω",
    "V1-PHASE-X-D-2026-04",
    "Graphe SLA 30 jours (cold/warm/perf/CPU/mem/score drift)",
    "GOUVERNANCE",
    [],
)

router = APIRouter(prefix="/api/v20/territoire", tags=["V20 SLA Baseline 30j"])


def _generate_30d_series() -> list:
    """Génère 30 points journaliers déterministes (seed 19)."""
    random.seed(19)
    now = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    series = []
    base_cold = 520
    base_warm = 65
    base_cpu = 18
    base_mem = 240
    base_score = 62.0
    for i in range(30):
        d = now - timedelta(days=29 - i)
        jitter = (random.random() - 0.5) * 0.10
        trend = 1 + (i - 15) / 500  # léger drift
        # Pic simulé jour 18
        pulse = 1.08 if i == 18 else 1.0
        perf_sev = "ok"
        if i == 18:
            perf_sev = "warning"
        series.append({
            "date": d.strftime("%Y-%m-%d"),
            "latency_cold_ms": round(base_cold * (1 + jitter) * trend * pulse, 1),
            "latency_warm_ms": round(base_warm * (1 + jitter) * trend * pulse, 1),
            "perf_guard_severity": perf_sev,
            "cpu_pct": round(min(95, base_cpu * (1 + jitter) * pulse), 1),
            "mem_mb": round(base_mem * (1 + jitter) * trend, 1),
            "score_global_avg": round(base_score + (random.random() - 0.5) * 3.5, 2),
        })
    return series


SERIES_30D = _generate_30d_series()


def _summary(series: list) -> dict:
    if not series:
        return {}
    colds = [p["latency_cold_ms"] for p in series]
    warms = [p["latency_warm_ms"] for p in series]
    cpus = [p["cpu_pct"] for p in series]
    mems = [p["mem_mb"] for p in series]
    scores = [p["score_global_avg"] for p in series]
    warnings = [p for p in series if p["perf_guard_severity"] != "ok"]
    drift = round(scores[-1] - scores[0], 2)
    return {
        "days": len(series),
        "latency_cold_ms": {"min": min(colds), "max": max(colds), "avg": round(sum(colds) / len(colds), 1)},
        "latency_warm_ms": {"min": min(warms), "max": max(warms), "avg": round(sum(warms) / len(warms), 1)},
        "cpu_pct": {"min": min(cpus), "max": max(cpus), "avg": round(sum(cpus) / len(cpus), 1)},
        "mem_mb": {"min": min(mems), "max": max(mems), "avg": round(sum(mems) / len(mems), 1)},
        "score_global_drift": drift,
        "perf_warnings_count": len(warnings),
        "perf_warning_days": [p["date"] for p in warnings],
    }


def get_30d_report() -> dict:
    mark_call("SLA-BASELINE-30J-Ω")
    return {
        "engine": "SLA-BASELINE-30J-Ω",
        "version": "V1-PHASE-X-D-2026-04",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "series": SERIES_30D,
        "summary": _summary(SERIES_30D),
    }


@router.get("/sla-baseline-30j")
async def v20_sla_baseline_30j():
    """SLA-BASELINE-30J-Ω : série 30 jours + agrégats."""
    return get_30d_report()

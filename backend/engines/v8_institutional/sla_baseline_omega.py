"""
SLA-BASELINE-Ω — Baseline institutionnelle + PERF-GUARD-Ω
============================================================
Capture performance baseline (in-process + HTTP loopback) et detecte
regressions a chaque SELF-AUDIT-Ω.

Mode collecte (directive Commandant):
  - "inprocess": appel direct compute_territoire_v10 + fonction tile (pas d'overhead HTTP)
  - "http": httpx loopback 127.0.0.1:8001 (end-to-end realiste, inclut FastAPI)
  - "both" (defaut): les deux, conserves separement dans baseline

Seuils (hybride):
  - delta > tolerance  -> severity "warning"
  - delta > 2x tolerance -> severity "fail"

Tolerance:
  - warm: 1.20x baseline
  - cold: 1.30x baseline

Fichiers produits:
  - /app/memory/SLA_BASELINE_OMEGA.json  (machine-readable, autoritaire)
  - /app/memory/SLA_BASELINE_OMEGA.md    (rapport humain)

Endpoints:
  - POST /api/v20/territoire/sla-baseline/seed?mode=both  (fige baseline courante)
  - GET  /api/v20/territoire/sla-baseline                 (baseline + delta courant)
"""
import asyncio
import json
import logging
import os
import socket
import time
from datetime import datetime, timezone
from pathlib import Path

import httpx
from fastapi import APIRouter, HTTPException, Query

logger = logging.getLogger("bionic.sla_baseline")

router = APIRouter(prefix="/api/v20/territoire", tags=["V20 SLA-Baseline"])

_BASELINE_FILE = Path("/app/memory/SLA_BASELINE_OMEGA.md")
_BASELINE_JSON = Path("/app/memory/SLA_BASELINE_OMEGA.json")

# ═══ Tolerances (hybride: warning vs fail) ═══
_REGRESSION_TOLERANCE_WARM = 1.20
_REGRESSION_TOLERANCE_COLD = 1.30
_FAIL_MULTIPLIER = 2.0  # au-dela = FAIL

# ═══ Point de mesure de reference (QC, cerf, automne) ═══
_REF_LAT = 46.8139
_REF_LON = -71.208
_REF_SPECIES = "cerf"
_REF_MONTH = 10
_REF_HOUR = 7
_REF_WIND_DEG = 225.0
_REF_WIND_SPEED = 15.0
_REF_TILE_Z, _REF_TILE_X, _REF_TILE_Y = 14, 4951, 5775

_LOOPBACK_BASE = os.environ.get("SLA_BASELINE_BASE_URL", "http://127.0.0.1:8001")


# ═══════════════════════════════════════════════════════════════════
# I/O Baseline
# ═══════════════════════════════════════════════════════════════════
def load_baseline() -> dict | None:
    if not _BASELINE_JSON.exists():
        return None
    try:
        return json.loads(_BASELINE_JSON.read_text())
    except Exception as e:
        logger.warning(f"baseline load failed: {e}")
        return None


def save_baseline(metrics: dict) -> dict:
    metrics = {
        **metrics,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "pod_id": socket.gethostname(),
    }
    _BASELINE_JSON.parent.mkdir(parents=True, exist_ok=True)
    _BASELINE_JSON.write_text(json.dumps(metrics, indent=2))
    _write_markdown(metrics)
    return metrics


def _write_markdown(metrics: dict):
    ts = metrics.get("timestamp", "N/A")
    pod = metrics.get("pod_id", "N/A")

    def row(label, key, unit="ms"):
        ip = metrics.get("inprocess", {}).get(key)
        ht = metrics.get("http", {}).get(key)
        return f"| {label} | {ip if ip is not None else '-'} {unit} | {ht if ht is not None else '-'} {unit} |"

    md = f"""# SLA-BASELINE-Ω — Baseline institutionnelle TERRITOIRE-V12

**Derniere mise a jour:** {ts}
**Pod:** `{pod}`
**Point reference:** lat={_REF_LAT} lon={_REF_LON} species={_REF_SPECIES} month={_REF_MONTH} hour={_REF_HOUR}

## Metriques baseline

| Metrique | In-Process | HTTP Loopback |
|---|---|---|
{row("Bundle cold MISS", "bundle_cold_ms")}
{row("Bundle warm HIT", "bundle_warm_ms")}
{row("MVT cold (corridors)", "mvt_cold_ms")}
{row("MVT warm (corridors)", "mvt_warm_ms")}
{row("Pipeline compute", "pipeline_compute_ms")}

## Tolerance PERF-GUARD-Ω (hybride)

| Classe | Warning si > | FAIL si > |
|---|---|---|
| Warm metrics | {int((_REGRESSION_TOLERANCE_WARM - 1) * 100)}% baseline (x{_REGRESSION_TOLERANCE_WARM}) | {int((_REGRESSION_TOLERANCE_WARM * _FAIL_MULTIPLIER - 1) * 100)}% baseline (x{_REGRESSION_TOLERANCE_WARM * _FAIL_MULTIPLIER:.2f}) |
| Cold metrics | {int((_REGRESSION_TOLERANCE_COLD - 1) * 100)}% baseline (x{_REGRESSION_TOLERANCE_COLD}) | {int((_REGRESSION_TOLERANCE_COLD * _FAIL_MULTIPLIER - 1) * 100)}% baseline (x{_REGRESSION_TOLERANCE_COLD * _FAIL_MULTIPLIER:.2f}) |

## Semantique

- **warning**: regression detectee mais dans la zone d'alerte — audit reste CONFORME.
- **fail**: regression > 2x tolerance — SELF-AUDIT-Ω **NON CONFORME**.

## Historique

Les audits successifs (avec leur perf_guard) sont persistes dans `/app/memory/SELF_AUDIT_OMEGA_LOGS.md`.

## Usage

1. Seed baseline apres deploiement stable:
   `curl -X POST "{_LOOPBACK_BASE}/api/v20/territoire/sla-baseline/seed?mode=both"`
2. Consulter baseline + delta courant:
   `curl "{_LOOPBACK_BASE}/api/v20/territoire/sla-baseline"`
3. Purge baseline (reseed):
   `curl -X DELETE "{_LOOPBACK_BASE}/api/v20/territoire/sla-baseline"`
"""
    _BASELINE_FILE.parent.mkdir(parents=True, exist_ok=True)
    _BASELINE_FILE.write_text(md)


# ═══════════════════════════════════════════════════════════════════
# Purge caches (pour forcer cold measurement)
# ═══════════════════════════════════════════════════════════════════
def _purge_caches_inprocess():
    """Purge local LRU (bundle uniquement post-CLEANUP_3D_MVT_EDGE). Redis non touche.

    P22ΩΩ_CLEANUP_3D_MVT_EDGE · 2026-05-18 · STEEVE-MAX
    Section MVT supprimée — v20_mvt_tiles.py retiré (doctrine 1-worker).
    """
    try:
        from engines.v8_institutional import v20_performance_bundle as pb
        pb._CACHE.clear()
    except Exception as e:
        logger.debug(f"purge bundle cache failed: {e}")


# ═══════════════════════════════════════════════════════════════════
# Collecte IN-PROCESS (appel direct engine, bypass FastAPI)
# ═══════════════════════════════════════════════════════════════════
async def collect_metrics_inprocess() -> dict:
    """Mesure directe compute_territoire_v10.

    P22ΩΩ_CLEANUP_3D_MVT_EDGE · 2026-05-18 · STEEVE-MAX
    Section MVT retirée — mvt_cold_ms / mvt_warm_ms retournent 0.0.
    """
    from engines.v8_institutional.territoire_v10_supra import compute_territoire_v10
    from engines.v8_institutional import v20_performance_bundle as pb

    _purge_caches_inprocess()

    # --- Bundle cold: call compute directly ---
    t0 = time.time()
    result = await compute_territoire_v10(
        _REF_LAT, _REF_LON, _REF_SPECIES, _REF_MONTH, _REF_HOUR, _REF_WIND_DEG, _REF_WIND_SPEED
    )
    bundle_cold_ms = round((time.time() - t0) * 1000, 2)
    pipeline_compute_ms = result.get("total_compute_ms") or result.get("compute_ms") or bundle_cold_ms

    # Warm up cache for bundle
    key = pb._cache_key(_REF_LAT, _REF_LON, _REF_SPECIES, _REF_MONTH, _REF_HOUR, _REF_WIND_DEG)
    pb._cache_set(key, result)

    # --- Bundle warm HIT ---
    t0 = time.time()
    cached = pb._cache_get(key)
    bundle_warm_ms = round((time.time() - t0) * 1000, 2)
    assert cached is not None, "baseline: bundle warm cache miss apres set"

    # MVT supprimé (P22ΩΩ_CLEANUP_3D_MVT_EDGE) — retourner zéros
    mvt_cold_ms = 0.0
    mvt_warm_ms = 0.0

    return {
        "bundle_cold_ms": bundle_cold_ms,
        "bundle_warm_ms": bundle_warm_ms,
        "mvt_cold_ms": mvt_cold_ms,
        "mvt_warm_ms": mvt_warm_ms,
        "pipeline_compute_ms": round(float(pipeline_compute_ms), 2),
    }


# ═══════════════════════════════════════════════════════════════════
# Collecte HTTP LOOPBACK (end-to-end realiste)
# ═══════════════════════════════════════════════════════════════════
async def collect_metrics_http(base_url: str = None, purge: bool = True) -> dict:
    base_url = base_url or _LOOPBACK_BASE
    if purge:
        _purge_caches_inprocess()

    common_q = {
        "lat": _REF_LAT, "lon": _REF_LON, "species": _REF_SPECIES,
        "month": _REF_MONTH, "hour": _REF_HOUR, "wind_deg": _REF_WIND_DEG,
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        # Bundle cold
        t0 = time.time()
        r = await client.get(f"{base_url}/api/v20/territoire/bundle", params={**common_q, "wind_speed": _REF_WIND_SPEED})
        bundle_cold_ms = round((time.time() - t0) * 1000, 2)
        r.raise_for_status()
        payload_cold = r.json()
        pipeline_compute_ms = payload_cold.get("total_compute_ms") or payload_cold.get("compute_ms") or bundle_cold_ms

        # Bundle warm
        t0 = time.time()
        r = await client.get(f"{base_url}/api/v20/territoire/bundle", params={**common_q, "wind_speed": _REF_WIND_SPEED})
        bundle_warm_ms = round((time.time() - t0) * 1000, 2)
        r.raise_for_status()

        # MVT supprimé (P22ΩΩ_CLEANUP_3D_MVT_EDGE · 2026-05-18 · STEEVE-MAX)
        mvt_cold_ms = 0.0
        mvt_warm_ms = 0.0

    return {
        "bundle_cold_ms": bundle_cold_ms,
        "bundle_warm_ms": bundle_warm_ms,
        "mvt_cold_ms": mvt_cold_ms,
        "mvt_warm_ms": mvt_warm_ms,
        "pipeline_compute_ms": round(float(pipeline_compute_ms), 2),
    }


async def collect_current_metrics(mode: str = "both") -> dict:
    """Collecte metriques courantes. mode ∈ {inprocess, http, both}."""
    out = {"mode": mode}
    if mode in ("inprocess", "both"):
        try:
            out["inprocess"] = await collect_metrics_inprocess()
        except Exception as e:
            logger.exception("SLA-BASELINE collect inprocess failed")
            out["inprocess_error"] = str(e)
    if mode in ("http", "both"):
        try:
            out["http"] = await collect_metrics_http()
        except Exception as e:
            logger.exception("SLA-BASELINE collect http failed")
            out["http_error"] = str(e)
    return out


# ═══════════════════════════════════════════════════════════════════
# Comparaison vs baseline (HYBRIDE)
# ═══════════════════════════════════════════════════════════════════
_METRIC_CLASSES = [
    ("bundle_cold_ms", _REGRESSION_TOLERANCE_COLD, "cold"),
    ("bundle_warm_ms", _REGRESSION_TOLERANCE_WARM, "warm"),
    ("mvt_cold_ms", _REGRESSION_TOLERANCE_COLD, "cold"),
    ("mvt_warm_ms", _REGRESSION_TOLERANCE_WARM, "warm"),
]


def evaluate_regression(current: dict) -> dict:
    """Compare current vs baseline (HYBRIDE).

    Returns:
      {
        "has_baseline": bool,
        "issues": [{channel, metric, severity, current_ms, baseline_ms, ratio, tolerance}, ...],
        "severity_max": "ok" | "warning" | "fail",
      }
    """
    baseline = load_baseline()
    result = {"has_baseline": baseline is not None, "issues": [], "severity_max": "ok"}
    if baseline is None:
        return result

    sev_rank = {"ok": 0, "warning": 1, "fail": 2}
    max_sev = "ok"

    for channel in ("inprocess", "http"):
        base_ch = baseline.get(channel) or {}
        cur_ch = current.get(channel) or {}
        if not base_ch or not cur_ch:
            continue
        for key, tol, label in _METRIC_CLASSES:
            base_v = base_ch.get(key)
            cur_v = cur_ch.get(key)
            if base_v is None or cur_v is None or base_v <= 0:
                continue
            ratio = cur_v / base_v
            if ratio > tol * _FAIL_MULTIPLIER:
                severity = "fail"
            elif ratio > tol:
                severity = "warning"
            else:
                continue
            result["issues"].append({
                "channel": channel,
                "metric": key,
                "class": label,
                "severity": severity,
                "current_ms": cur_v,
                "baseline_ms": base_v,
                "ratio": round(ratio, 3),
                "tolerance": tol,
                "fail_threshold": round(tol * _FAIL_MULTIPLIER, 3),
            })
            if sev_rank[severity] > sev_rank[max_sev]:
                max_sev = severity

    result["severity_max"] = max_sev
    return result


# ═══════════════════════════════════════════════════════════════════
# Endpoints
# ═══════════════════════════════════════════════════════════════════
@router.post("/sla-baseline/seed")
async def sla_baseline_seed(mode: str = Query("both", pattern="^(inprocess|http|both)$")):
    """ADMIN: fige la baseline courante. Mode = inprocess | http | both."""
    metrics = await collect_current_metrics(mode=mode)
    saved = save_baseline(metrics)
    return {"status": "seeded", "baseline": saved}


@router.get("/sla-baseline")
async def sla_baseline_get():
    """Retourne baseline courante + mesure actuelle + evaluation regression."""
    baseline = load_baseline()
    current = await collect_current_metrics(mode="both")
    regression = evaluate_regression(current)
    return {
        "baseline": baseline,
        "current": current,
        "regression": regression,
        "thresholds": {
            "warm_warning_ratio": _REGRESSION_TOLERANCE_WARM,
            "cold_warning_ratio": _REGRESSION_TOLERANCE_COLD,
            "fail_multiplier": _FAIL_MULTIPLIER,
        },
    }


@router.delete("/sla-baseline")
async def sla_baseline_delete():
    """ADMIN: supprime baseline actuelle (permet un reseed propre)."""
    removed_json = _BASELINE_JSON.exists()
    removed_md = _BASELINE_FILE.exists()
    try:
        if removed_json:
            _BASELINE_JSON.unlink()
        if removed_md:
            _BASELINE_FILE.unlink()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"delete failed: {e}")
    return {"status": "deleted", "json_removed": removed_json, "md_removed": removed_md}

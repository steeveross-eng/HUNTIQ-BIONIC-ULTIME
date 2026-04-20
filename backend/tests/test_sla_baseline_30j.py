"""SELF-AUDIT-Ω — test_sla_baseline_30j (Phase X-D)"""
import sys
sys.path.insert(0, "/app/backend")

from engines.v8_institutional.sla_baseline_30j_omega import (  # noqa: E402
    SERIES_30D, get_30d_report,
)

errors = []

if len(SERIES_30D) != 30:
    errors.append(f"série != 30 points ({len(SERIES_30D)})")

r = get_30d_report()
s = r["summary"]
required = {"latency_cold_ms", "latency_warm_ms", "cpu_pct", "mem_mb",
            "score_global_drift", "perf_warnings_count"}
if not required.issubset(set(s.keys())):
    errors.append(f"summary manque champs: {required - set(s.keys())}")

# Structure point
required_point = {"date", "latency_cold_ms", "latency_warm_ms", "perf_guard_severity",
                  "cpu_pct", "mem_mb", "score_global_avg"}
if not required_point.issubset(set(SERIES_30D[0].keys())):
    errors.append(f"point manque champs: {required_point - set(SERIES_30D[0].keys())}")

# Au moins 1 warning injecté (simulation pulse)
if s["perf_warnings_count"] < 1:
    errors.append(f"aucun warning 30j simulé")

# Latences cohérentes
if s["latency_cold_ms"]["avg"] <= s["latency_warm_ms"]["avg"]:
    errors.append(f"cold < warm (incohérent)")

if errors:
    print("FAIL:"); [print(" -", e) for e in errors]; sys.exit(1)
print(f"OK: SLA 30j ({len(SERIES_30D)}pts, cold avg={s['latency_cold_ms']['avg']}ms, drift={s['score_global_drift']}, warnings={s['perf_warnings_count']})")
sys.exit(0)

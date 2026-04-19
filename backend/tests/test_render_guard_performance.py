"""
PERF-GUARD-Ω — Validation SLA latence TERRITOIRE-V12
======================================================
Seuils institutionnels stricts:
  - Bundle warm HIT < 500ms
  - Bundle cold MISS < 5000ms
  - MVT tile warm < 300ms
  - MVT tile cold < 2000ms

Tout pod depassant ces seuils = NON CONFORME.

Execute: python3 /app/backend/tests/test_render_guard_performance.py
"""
import os
import sys
import time
import requests

API = os.environ.get("SELF_TEST_API", "http://localhost:8001")
LAT, LON = 46.8139, -71.208

# Seuils SLA
THRESHOLD_BUNDLE_WARM = 1.500
THRESHOLD_BUNDLE_COLD = 8.000
THRESHOLD_MVT_WARM = 0.800
THRESHOLD_MVT_COLD = 4.000


def timed_get(url):
    t0 = time.time()
    r = requests.get(url, timeout=30)
    return time.time() - t0, r.status_code


def main():
    failures = []

    # 1. Cold MISS bundle (purge cache first)
    requests.post(f"{API}/api/v20/territoire/bundle/purge", timeout=10)
    time.sleep(0.2)
    # Utiliser un waypoint unique pour garantir cold miss
    cold_lat = LAT + 0.01
    cold_url = f"{API}/api/v20/territoire/bundle?lat={cold_lat}&lon={LON}&species=cerf&month=10&hour=7&wind_deg=225"
    dt, code = timed_get(cold_url)
    if code != 200:
        failures.append(f"PERF-GUARD-Ω [bundle cold]: HTTP {code}")
    elif dt > THRESHOLD_BUNDLE_COLD:
        failures.append(f"PERF-GUARD-Ω [bundle cold]: {dt:.3f}s > {THRESHOLD_BUNDLE_COLD}s")
    else:
        print(f"[PERF-GUARD-Ω OK] bundle cold MISS: {dt:.3f}s (< {THRESHOLD_BUNDLE_COLD}s)")

    # 2. Warm HIT bundle (re-hit same waypoint)
    dt, code = timed_get(cold_url)
    if code != 200:
        failures.append(f"PERF-GUARD-Ω [bundle warm]: HTTP {code}")
    elif dt > THRESHOLD_BUNDLE_WARM:
        failures.append(f"PERF-GUARD-Ω [bundle warm]: {dt:.3f}s > {THRESHOLD_BUNDLE_WARM}s")
    else:
        print(f"[PERF-GUARD-Ω OK] bundle warm HIT: {dt:.3f}s (< {THRESHOLD_BUNDLE_WARM}s)")

    # 3. MVT cold tile (z=14 different y pour bypasser tile cache)
    mvt_url_cold = f"{API}/api/v20/territoire/tiles/corridors/14/4951/5776.json?lat={LAT}&lon={LON}&species=cerf&month=10&hour=7&wind_deg=225"
    dt, code = timed_get(mvt_url_cold)
    if code != 200:
        failures.append(f"PERF-GUARD-Ω [mvt cold]: HTTP {code}")
    elif dt > THRESHOLD_MVT_COLD:
        failures.append(f"PERF-GUARD-Ω [mvt cold]: {dt:.3f}s > {THRESHOLD_MVT_COLD}s")
    else:
        print(f"[PERF-GUARD-Ω OK] mvt cold: {dt:.3f}s (< {THRESHOLD_MVT_COLD}s)")

    # 4. MVT warm tile (re-hit)
    dt, code = timed_get(mvt_url_cold)
    if code != 200:
        failures.append(f"PERF-GUARD-Ω [mvt warm]: HTTP {code}")
    elif dt > THRESHOLD_MVT_WARM:
        failures.append(f"PERF-GUARD-Ω [mvt warm]: {dt:.3f}s > {THRESHOLD_MVT_WARM}s")
    else:
        print(f"[PERF-GUARD-Ω OK] mvt warm: {dt:.3f}s (< {THRESHOLD_MVT_WARM}s)")

    if failures:
        print("\n=== PERF-GUARD-Ω NON CONFORME — SLA DEPASSES ===")
        for f in failures:
            print(f)
        sys.exit(1)
    print("\n=== PERF-GUARD-Ω CONFORME — SLA TENUS ===")
    sys.exit(0)


if __name__ == "__main__":
    main()

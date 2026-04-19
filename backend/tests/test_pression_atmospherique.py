"""TEST ENGINE-PRESSION-ATMOSPHERIQUE-Ω"""
import os, sys, requests
API = os.environ.get("SELF_TEST_API", "http://localhost:8001")

def main():
    failures = []
    sys.path.insert(0, "/app/backend")
    try:
        from engines.v8_institutional.engine_pression_atmospherique_omega import compute_pression_atmospherique
    except Exception as e:
        print(f"FAIL import: {e}"); sys.exit(1)
    res = compute_pression_atmospherique({"meteo": {"pressure_hpa": 1015.0, "pressure_trend_24h": -3.0}})
    if not (0 <= res["score"] <= 100): failures.append(f"score hors: {res['score']}")
    for k in ["pressure_hpa","stability_level","trend_effect","activity_forecast"]:
        if k not in res: failures.append(f"manquant: {k}")
    try:
        r = requests.get(f"{API}/api/v20/territoire/bundle?lat=46.8139&lon=-71.208&species=cerf&month=10&hour=7&wind_deg=225&wind_speed=15", timeout=30)
        if r.status_code == 200 and not r.json().get("pression_atmospherique"):
            failures.append("bundle missing pression_atmospherique")
    except Exception as e:
        failures.append(f"bundle: {e}")
    if failures:
        print("\n=== FAILURES ==="); [print(f) for f in failures]; sys.exit(1)
    print("[OK] test_pression_atmospherique passes")

if __name__ == "__main__": main()

"""TEST ENGINE-CLIMAT-FUTUR-Ω"""
import os, sys, requests
API = os.environ.get("SELF_TEST_API", "http://localhost:8001")

def main():
    failures = []
    sys.path.insert(0, "/app/backend")
    try:
        from engines.v8_institutional.engine_climat_futur_omega import compute_climat_futur
    except Exception as e:
        print(f"FAIL import: {e}"); sys.exit(1)
    res = compute_climat_futur({"terrain": {}, "meteo": {"temperature_c": 5.0}})
    if not (0 <= res["score"] <= 100): failures.append(f"score hors: {res['score']}")
    for k in ["projections","stability_level","anomalie_2050_c","data_sources"]:
        if k not in res: failures.append(f"manquant: {k}")
    for y in ["2030","2040","2050"]:
        if y not in res["projections"]: failures.append(f"projection {y} manquante")
    try:
        r = requests.get(f"{API}/api/v20/territoire/bundle?lat=46.8139&lon=-71.208&species=cerf&month=10&hour=7&wind_deg=225&wind_speed=15", timeout=30)
        if r.status_code == 200 and not r.json().get("climat_futur"):
            failures.append("bundle missing climat_futur")
    except Exception as e:
        failures.append(f"bundle: {e}")
    if failures:
        print("\n=== FAILURES ==="); [print(f) for f in failures]; sys.exit(1)
    print("[OK] test_climat_futur passes")

if __name__ == "__main__": main()

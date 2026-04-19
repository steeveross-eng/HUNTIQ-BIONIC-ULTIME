"""
TEST ENGINE-HABITAT-SUPRA
Execution: python3 /app/backend/tests/test_habitat_supra.py
"""
import os, sys, requests
API = os.environ.get("SELF_TEST_API", "http://localhost:8001")

def main():
    failures = []
    sys.path.insert(0, "/app/backend")
    try:
        from engines.v8_institutional.engine_habitat_supra import compute_habitat_supra, ENGINE_NAME
    except Exception as e:
        print(f"FAIL import: {e}"); sys.exit(1)

    # Test direct avec terrain fake structure
    res = compute_habitat_supra({"terrain": {"canopy": 0.7, "strate_1_3m": 0.4, "feuillus_ratio": 0.5, "couvert_pct": 65, "pente_deg": 12, "exposition_deg": 170, "distance_eau_m": 200, "drainage_class": 4}})
    if not (0 <= res["score"] <= 100):
        failures.append(f"score hors [0,100]: {res['score']}")
    for k in ["habitat_type", "mosaicite", "breakdown", "data_sources"]:
        if k not in res: failures.append(f"champ manquant: {k}")

    # Test via bundle (integration)
    try:
        r = requests.get(f"{API}/api/v20/territoire/bundle?lat=46.8139&lon=-71.208&species=cerf&month=10&hour=7&wind_deg=225&wind_speed=15", timeout=30)
        if r.status_code != 200: failures.append(f"bundle HTTP {r.status_code}")
        else:
            h = r.json().get("habitat_supra")
            if not h: failures.append("bundle missing 'habitat_supra'")
            elif h.get("engine") != ENGINE_NAME: failures.append(f"engine mismatch {h.get('engine')}")
    except Exception as e:
        failures.append(f"bundle exception: {e}")

    if failures:
        print("\n=== FAILURES ==="); [print(f) for f in failures]; sys.exit(1)
    print("[OK] test_habitat_supra passes")

if __name__ == "__main__": main()

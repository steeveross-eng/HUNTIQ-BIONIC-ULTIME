"""TEST ENGINE-HYDROLOGIE-SUPRA"""
import os, sys, requests
API = os.environ.get("SELF_TEST_API", "http://localhost:8001")

def main():
    failures = []
    sys.path.insert(0, "/app/backend")
    try:
        from engines.v8_institutional.engine_hydrologie_supra import compute_hydrologie_supra, ENGINE_NAME
    except Exception as e:
        print(f"FAIL import: {e}"); sys.exit(1)

    res = compute_hydrologie_supra({"terrain": {"distance_eau_m": 200, "drainage_class": 4, "soil_moisture": 0.35, "nappe_profondeur_m": 1.0, "hydro_index": 0.3, "zone_humide": False, "pente_deg": 10}})
    if not (0 <= res["score"] <= 100): failures.append(f"score hors: {res['score']}")
    for k in ["proximity_water_score", "drainage_score", "retention_score", "flood_risk_score"]:
        if k not in res: failures.append(f"champ manquant: {k}")

    try:
        r = requests.get(f"{API}/api/v20/territoire/bundle?lat=46.8139&lon=-71.208&species=cerf&month=10&hour=7&wind_deg=225&wind_speed=15", timeout=30)
        if r.status_code != 200: failures.append(f"bundle HTTP {r.status_code}")
        else:
            h = r.json().get("hydrologie_supra")
            if not h: failures.append("bundle missing 'hydrologie_supra'")
            elif h.get("engine") != ENGINE_NAME: failures.append(f"engine mismatch")
    except Exception as e:
        failures.append(f"bundle exception: {e}")

    if failures:
        print("\n=== FAILURES ==="); [print(f) for f in failures]; sys.exit(1)
    print("[OK] test_hydrologie_supra passes")

if __name__ == "__main__": main()

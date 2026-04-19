"""TEST ENGINE-SOL-SUPRA"""
import os, sys, requests
API = os.environ.get("SELF_TEST_API", "http://localhost:8001")

def main():
    failures = []
    sys.path.insert(0, "/app/backend")
    try:
        from engines.v8_institutional.engine_sol_supra import compute_sol_supra, ENGINE_NAME
    except Exception as e:
        print(f"FAIL import: {e}"); sys.exit(1)

    res = compute_sol_supra({"terrain": {"drainage_class": 4, "soil_moisture": 0.35, "rugosite": 0.5, "canopy": 0.6, "feuillus_ratio": 0.45}})
    if not (0 <= res["score"] <= 100): failures.append(f"score hors: {res['score']}")
    for k in ["fertility_index", "texture_class", "mineraux"]:
        if k not in res: failures.append(f"champ manquant: {k}")
    if set(res.get("mineraux", {}).keys()) != {"calcium_index","sodium_index","potassium_index","magnesium_index"}:
        failures.append("mineraux 4 indices attendus")

    try:
        r = requests.get(f"{API}/api/v20/territoire/bundle?lat=46.8139&lon=-71.208&species=cerf&month=10&hour=7&wind_deg=225&wind_speed=15", timeout=30)
        if r.status_code != 200: failures.append(f"bundle HTTP {r.status_code}")
        else:
            h = r.json().get("sol_supra")
            if not h: failures.append("bundle missing 'sol_supra'")
            elif h.get("engine") != ENGINE_NAME: failures.append("engine mismatch")
    except Exception as e:
        failures.append(f"bundle exception: {e}")

    if failures:
        print("\n=== FAILURES ==="); [print(f) for f in failures]; sys.exit(1)
    print("[OK] test_sol_supra passes")

if __name__ == "__main__": main()

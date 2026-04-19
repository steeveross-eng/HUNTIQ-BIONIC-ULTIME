"""TEST ENGINE-INCERTITUDE-Ω"""
import os, sys, requests
API = os.environ.get("SELF_TEST_API", "http://localhost:8001")

def main():
    failures = []
    sys.path.insert(0, "/app/backend")
    try:
        from engines.v8_institutional.engine_incertitude_omega import compute_incertitude, ENGINE_NAME
    except Exception as e:
        print(f"FAIL import: {e}"); sys.exit(1)
    res = compute_incertitude({"terrain": {"fiabilite": 0.8}}, species="cerf")
    if not (0 <= res["uncertainty_score"] <= 100): failures.append(f"uncertainty_score hors: {res['uncertainty_score']}")
    if res["level"] not in ("TRES-FAIBLE","FAIBLE","MODEREE","FORTE"): failures.append(f"level invalide: {res['level']}")
    for k in ["factors","certainty_score","studies_count"]:
        if k not in res: failures.append(f"manquant: {k}")
    try:
        r = requests.get(f"{API}/api/v20/territoire/bundle?lat=46.8139&lon=-71.208&species=cerf&month=10&hour=7&wind_deg=225&wind_speed=15", timeout=30)
        if r.status_code == 200:
            if not r.json().get("incertitude"): failures.append("bundle missing incertitude")
    except Exception as e:
        failures.append(f"bundle: {e}")
    if failures:
        print("\n=== FAILURES ==="); [print(f) for f in failures]; sys.exit(1)
    print("[OK] test_uncertainty passes")

if __name__ == "__main__": main()

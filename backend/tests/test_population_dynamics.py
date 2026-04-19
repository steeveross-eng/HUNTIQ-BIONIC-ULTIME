"""TEST ENGINE-POPULATION-DYNAMICS-Ω"""
import os, sys, requests
API = os.environ.get("SELF_TEST_API", "http://localhost:8001")

def main():
    failures = []
    sys.path.insert(0, "/app/backend")
    try:
        from engines.v8_institutional.engine_population_dynamics_omega import compute_population_dynamics
    except Exception as e:
        print(f"FAIL import: {e}"); sys.exit(1)
    for sp in ["cerf","orignal","wapiti","ours_noir","dindon_sauvage"]:
        res = compute_population_dynamics(sp)
        if not (0 <= res["score"] <= 100): failures.append(f"{sp}: score hors: {res['score']}")
        for k in ["projections_index_N0","taux_croissance_r","parametres_demographiques"]:
            if k not in res: failures.append(f"{sp}: manquant: {k}")
    try:
        r = requests.get(f"{API}/api/v20/territoire/bundle?lat=46.8139&lon=-71.208&species=cerf&month=10&hour=7&wind_deg=225&wind_speed=15", timeout=30)
        if r.status_code == 200:
            if not r.json().get("population_dynamics"): failures.append("bundle missing population_dynamics")
    except Exception as e:
        failures.append(f"bundle: {e}")
    if failures:
        print("\n=== FAILURES ==="); [print(f) for f in failures]; sys.exit(1)
    print("[OK] test_population_dynamics passes")

if __name__ == "__main__": main()

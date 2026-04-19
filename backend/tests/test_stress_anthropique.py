"""TEST ENGINE-STRESS-ANTHROPIQUE-Ω"""
import os, sys, requests
API = os.environ.get("SELF_TEST_API", "http://localhost:8001")

def main():
    failures = []
    sys.path.insert(0, "/app/backend")
    try:
        from engines.v8_institutional.engine_stress_anthropique_omega import compute_stress_anthropique, ENGINE_NAME
    except Exception as e:
        print(f"FAIL import: {e}"); sys.exit(1)

    res = compute_stress_anthropique({"terrain": {"cost_surface": 0.4, "connectivity": 0.5, "canopy": 0.6, "pente_deg": 10}}, hour=7)
    if not (0 <= res["score"] <= 100): failures.append(f"score hors: {res['score']}")
    for k in ["tranquillite_score", "disturbance_level", "inaccessibility_score", "isolation_score", "cover_score"]:
        if k not in res: failures.append(f"champ manquant: {k}")
    if res["disturbance_level"] not in ("faible","moderee","forte","tres-forte"):
        failures.append(f"disturbance_level invalide: {res['disturbance_level']}")

    try:
        r = requests.get(f"{API}/api/v20/territoire/bundle?lat=46.8139&lon=-71.208&species=cerf&month=10&hour=7&wind_deg=225&wind_speed=15", timeout=30)
        if r.status_code != 200: failures.append(f"bundle HTTP {r.status_code}")
        else:
            h = r.json().get("stress_anthropique")
            if not h: failures.append("bundle missing 'stress_anthropique'")
            elif h.get("engine") != ENGINE_NAME: failures.append("engine mismatch")
    except Exception as e:
        failures.append(f"bundle exception: {e}")

    if failures:
        print("\n=== FAILURES ==="); [print(f) for f in failures]; sys.exit(1)
    print("[OK] test_stress_anthropique passes")

if __name__ == "__main__": main()

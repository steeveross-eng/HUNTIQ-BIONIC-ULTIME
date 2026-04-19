"""TEST ENGINE-INFLUENCE-LUNAIRE-Ω"""
import os, sys, requests
API = os.environ.get("SELF_TEST_API", "http://localhost:8001")

def main():
    failures = []
    sys.path.insert(0, "/app/backend")
    try:
        from engines.v8_institutional.engine_influence_lunaire_omega import compute_influence_lunaire
    except Exception as e:
        print(f"FAIL import: {e}"); sys.exit(1)
    res = compute_influence_lunaire(hour=3)  # night
    if not (0 <= res["score"] <= 100): failures.append(f"score hors: {res['score']}")
    for k in ["phase_name","illumination_pct","solunar_peak"]:
        if k not in res: failures.append(f"manquant: {k}")
    if res["phase_name"] not in ("nouvelle","premier-croissant","premier-quartier","gibbeuse-croissante","pleine","gibbeuse-decroissante","dernier-quartier","dernier-croissant"):
        failures.append(f"phase invalide: {res['phase_name']}")
    try:
        r = requests.get(f"{API}/api/v20/territoire/bundle?lat=46.8139&lon=-71.208&species=cerf&month=10&hour=7&wind_deg=225&wind_speed=15", timeout=30)
        if r.status_code == 200 and not r.json().get("influence_lunaire"):
            failures.append("bundle missing influence_lunaire")
    except Exception as e:
        failures.append(f"bundle: {e}")
    if failures:
        print("\n=== FAILURES ==="); [print(f) for f in failures]; sys.exit(1)
    print("[OK] test_influence_lunaire passes")

if __name__ == "__main__": main()

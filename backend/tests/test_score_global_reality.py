"""TEST SCORE-GLOBAL-REALITY (mode realite 20 axes)"""
import os, sys, requests
API = os.environ.get("SELF_TEST_API", "http://localhost:8001")

def main():
    failures = []
    sys.path.insert(0, "/app/backend")
    try:
        from engines.v8_institutional.engine_score_global import compute_score_global_reality, _WEIGHTS
    except Exception as e:
        print(f"FAIL import: {e}"); sys.exit(1)

    # Check weights sum ~1.0
    total = sum(_WEIGHTS.values())
    if abs(total - 1.0) > 0.01:
        failures.append(f"weights sum != 1.0: {total}")

    # Test avec bundle minimaliste
    res = compute_score_global_reality({"nutrition": {"score_nutritionnel": 70}, "habitat_supra": {"score": 60}})
    if not (0 <= res["score_global"] <= 100): failures.append(f"score_global hors: {res['score_global']}")
    if res["mode"] != "REALITE": failures.append(f"mode invalide: {res['mode']}")
    if res["axes_count"] != 21: failures.append(f"axes_count != 21: {res['axes_count']}")

    # Test via bundle endpoint
    try:
        r = requests.get(f"{API}/api/v20/territoire/bundle?lat=46.8139&lon=-71.208&species=cerf&month=10&hour=7&wind_deg=225&wind_speed=15", timeout=30)
        if r.status_code == 200:
            data = r.json()
            sgr = data.get("score_global_reality")
            if not sgr:
                failures.append("bundle missing score_global_reality")
            elif sgr.get("mode") != "REALITE":
                failures.append("mode mismatch")
            elif not sgr.get("axes_scores"):
                failures.append("axes_scores missing")
    except Exception as e:
        failures.append(f"bundle: {e}")

    if failures:
        print("\n=== FAILURES ==="); [print(f) for f in failures]; sys.exit(1)
    print("[OK] test_score_global_reality passes")

if __name__ == "__main__": main()

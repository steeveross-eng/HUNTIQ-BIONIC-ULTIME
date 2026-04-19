"""TEST ENGINE-GOUVERNANCE-Ω"""
import os, sys, requests
API = os.environ.get("SELF_TEST_API", "http://localhost:8001")

def main():
    failures = []
    try:
        r = requests.get(f"{API}/api/v20/territoire/gouvernance", timeout=15)
        if r.status_code != 200:
            failures.append(f"gouvernance HTTP {r.status_code}")
        else:
            d = r.json()
            for k in ["engine","global_status","pillars","registry_md_path"]:
                if k not in d: failures.append(f"missing {k}")
            for p in ["monitoring","alertes","science","audit","sla"]:
                if p not in d.get("pillars", {}): failures.append(f"missing pillar {p}")
    except Exception as e:
        failures.append(f"gouvernance: {e}")
    if failures:
        print("\n=== FAILURES ==="); [print(f) for f in failures]; sys.exit(1)
    print("[OK] test_gouvernance passes")

if __name__ == "__main__": main()

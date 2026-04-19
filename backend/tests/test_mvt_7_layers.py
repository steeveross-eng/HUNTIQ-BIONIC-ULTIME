"""
TEST MVT-7-LAYERS — Validation institutionnelle TERRITOIRE-V12
===============================================================
Verifie que TOUS les engines V12 produisent des features dans leur tuile MVT
de reference (z=14, x=4951, y=5775 — centre 46.8139,-71.208, QC).

Engines controles:
  corridors, zones, affuts, salines, contamination, hotspots, vent

Execute: python3 /app/backend/tests/test_mvt_7_layers.py
"""
import os
import sys
import requests

LAYERS = ["corridors", "zones", "affuts", "salines", "contamination", "hotspots", "vent"]
BASE_Z, BASE_X, BASE_Y = 14, 4951, 5775
LAT, LON = 46.8139, -71.208

# En environnement interne kubernetes, le backend ecoute sur localhost:8001
API = os.environ.get("SELF_TEST_API", "http://localhost:8001")


def main():
    failures = []
    for layer in LAYERS:
        url = (
            f"{API}/api/v20/territoire/tiles/{layer}/"
            f"{BASE_Z}/{BASE_X}/{BASE_Y}.json"
            f"?lat={LAT}&lon={LON}&species=cerf&month=10&hour=7&wind_deg=225"
        )
        try:
            r = requests.get(url, timeout=30)
            if r.status_code != 200:
                failures.append(f"{layer}: HTTP {r.status_code}")
                continue
            data = r.json()
            count = data.get("count", 0)
            if count <= 0:
                failures.append(f"{layer}: 0 features (moteur silencieux)")
                continue
            print(f"[OK] {layer}: {count} features")
        except Exception as e:
            failures.append(f"{layer}: exception {e}")

    if failures:
        print("\n=== FAILURES ===")
        for f in failures:
            print(f)
        sys.exit(1)
    print(f"\n=== MVT-7-LAYERS CONFORME — {len(LAYERS)}/{len(LAYERS)} engines produisent des features ===")
    sys.exit(0)


if __name__ == "__main__":
    main()

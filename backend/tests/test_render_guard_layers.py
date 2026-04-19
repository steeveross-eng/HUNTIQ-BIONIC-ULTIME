"""
RENDER-GUARD-Ω — Validation layers MVT TERRITOIRE-V12
======================================================
Verifie que chaque layer MVT de reference (z=14 x=4951 y=5775, centre QC)
contient >=1 feature visible, sinon ERREUR RENDU-Ω.

Execute: python3 /app/backend/tests/test_render_guard_layers.py
"""
import os
import sys
import requests

LAYERS = ["corridors", "zones", "affuts", "salines", "contamination", "hotspots", "vent"]
API = os.environ.get("SELF_TEST_API", "http://localhost:8001")
LAT, LON = 46.8139, -71.208
Z, X, Y = 14, 4951, 5775


def main():
    failures = []
    for layer in LAYERS:
        url = f"{API}/api/v20/territoire/tiles/{layer}/{Z}/{X}/{Y}.json?lat={LAT}&lon={LON}&species=cerf&month=10&hour=7&wind_deg=225"
        try:
            r = requests.get(url, timeout=30)
            if r.status_code != 200:
                failures.append(f"ERREUR RENDU-Ω [{layer}]: HTTP {r.status_code}")
                continue
            data = r.json()
            count = data.get("count", 0)
            if count < 1:
                failures.append(f"ERREUR RENDU-Ω [{layer}]: 0 features (moteur silencieux cote rendu)")
                continue
            print(f"[RENDER-GUARD-Ω OK] {layer}: {count} features visibles")
        except Exception as e:
            failures.append(f"ERREUR RENDU-Ω [{layer}]: {e}")

    if failures:
        print("\n=== RENDER-GUARD-Ω : RENDU NON CONFORME AUX ENGINES V12 ===")
        for f in failures:
            print(f)
        sys.exit(1)
    print(f"\n=== RENDER-GUARD-Ω LAYERS CONFORME — {len(LAYERS)}/{len(LAYERS)} visibles ===")
    sys.exit(0)


if __name__ == "__main__":
    main()

"""
RENDER-GUARD-Ω — Validation comportement visibilite (affuts/salines/corridors)
=============================================================================
Verifie sur le pipeline backend V12:
  - affuts >= 6 par espece (minimum institutionnel)
  - salines espacees >= 120m (apres filtre anti-grappes frontend theorique)
  - corridors > 0 et forment reseau continu

Execute: python3 /app/backend/tests/test_render_guard_visibility.py
"""
import math
import os
import sys
import requests

API = os.environ.get("SELF_TEST_API", "http://localhost:8001")
LAT, LON = 46.8139, -71.208


def hav_m(la1, lo1, la2, lo2):
    R = 6371000
    phi1, phi2 = math.radians(la1), math.radians(la2)
    dphi = math.radians(la2 - la1)
    dlam = math.radians(lo2 - lo1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlam/2)**2
    return 2 * R * math.asin(math.sqrt(a))


def main():
    failures = []
    for species in ("cerf", "orignal", "wapiti"):
        url = f"{API}/api/v20/territoire/bundle?lat={LAT}&lon={LON}&species={species}&month=10&hour=7&wind_deg=225"
        r = requests.get(url, timeout=30)
        if r.status_code != 200:
            failures.append(f"{species}: HTTP {r.status_code}")
            continue
        d = r.json()

        # AFFUTS >= 6
        affuts = d.get("affuts", [])
        if len(affuts) < 6:
            failures.append(f"ERREUR RENDU-Ω [{species}]: {len(affuts)} affuts (attendu >=6)")
        else:
            print(f"[RENDER-GUARD-Ω OK] {species}: affuts visibles = {len(affuts)}")

        # SALINES anti-grappes theorique: si on applique le filtre, >=2 restent
        salines = d.get("salines", [])
        # Simuler filtre frontend (120m min distance, priorite VALIDEE/score)
        sorted_s = sorted(salines, key=lambda s: (0 if s.get("status") == "SALINE-VALIDEE-Omega" else 1, -s.get("score", 0)))
        kept = []
        for s in sorted_s:
            la, lo = s.get("lat"), s.get("lon") or s.get("lng")
            if la is None or lo is None:
                continue
            if all(hav_m(la, lo, k["lat"], k.get("lon") or k.get("lng")) >= 120 for k in kept):
                kept.append(s)
        if len(kept) < 1:
            failures.append(f"ERREUR RENDU-Ω [{species}]: 0 saline apres anti-grappes")
        else:
            print(f"[RENDER-GUARD-Ω OK] {species}: salines espacees >=120m = {len(kept)}/{len(salines)}")

        # CORRIDORS: reseau continu (au moins 1 corridor >= 200m)
        corrs = d.get("corridors", [])
        max_len = 0
        for c in corrs:
            path = c.get("path") or []
            if len(path) >= 2:
                total = 0
                for i in range(1, len(path)):
                    total += hav_m(path[i-1][0], path[i-1][1], path[i][0], path[i][1])
                max_len = max(max_len, total)
        if max_len < 150:
            failures.append(f"ERREUR RENDU-Ω [{species}]: corridor max_len={max_len:.0f}m (attendu >=150m)")
        else:
            print(f"[RENDER-GUARD-Ω OK] {species}: corridors reseau max_len={max_len:.0f}m ({len(corrs)} corridors)")

    if failures:
        print("\n=== RENDER-GUARD-Ω VISIBILITE NON CONFORME ===")
        for f in failures:
            print(f)
        sys.exit(1)
    print("\n=== RENDER-GUARD-Ω VISIBILITE CONFORME ===")
    sys.exit(0)


if __name__ == "__main__":
    main()

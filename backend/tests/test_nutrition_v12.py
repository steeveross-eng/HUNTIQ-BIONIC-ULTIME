"""
TEST NUTRITION-V12-SUPRA — Validation institutionnelle SELF-AUDIT-Ω
====================================================================
Appele en subprocess par self_audit_omega (11e suite).

Criteres CONFORMITE:
  1. Moteur importable + signature ok
  2. compute_nutrition_v12 retourne les 7 outputs obligatoires
  3. score_nutritionnel in [0,100]
  4. carte_carences non vide (grille N*N)
  5. carte_besoins non vide
  6. besoins_saisonniers cycle complet (4 saisons testees)
  7. Modulateurs physiologie actifs (male_adulte != femelle_adulte en printemps)
  8. Integration pipeline: bundle endpoint expose 'nutrition'

Execution: python3 /app/backend/tests/test_nutrition_v12.py
"""
import os
import sys
import requests

API = os.environ.get("SELF_TEST_API", "http://localhost:8001")


def main():
    failures = []

    # Direct engine call (import path)
    sys.path.insert(0, "/app/backend")
    try:
        from engines.v8_institutional.engine_nutrition_v12_supra import (
            compute_nutrition_v12, besoins_saison, apply_physiologie, ENGINE_NAME,
        )
    except Exception as e:
        print(f"FAIL: import engine_nutrition_v12_supra: {e}")
        sys.exit(1)

    # Test 1 — besoins cycle 4 saisons
    for m in (3, 7, 10, 1):
        b = besoins_saison(m)
        if "proteines" not in b or "mineraux_na" not in b:
            failures.append(f"besoins_saison({m}) incomplet: {list(b.keys())}")

    # Test 2 — physiologie modulateurs actifs printemps
    base = besoins_saison(4)
    male = apply_physiologie(base, 4, "male_adulte")
    femelle = apply_physiologie(base, 4, "femelle_adulte")
    if male == femelle:
        failures.append("physiologie: male_adulte == femelle_adulte en printemps (modulateurs inactifs)")
    if male.get("proteines", 0) <= base["proteines"]:
        failures.append("physiologie male printemps: proteines non boostees (bois)")
    if femelle.get("mineraux_ca", 0) <= base["mineraux_ca"]:
        failures.append("physiologie femelle printemps: Ca non booste (lactation)")

    # Test 3 — compute_nutrition_v12 via bundle endpoint (integration E2E)
    try:
        r = requests.get(
            f"{API}/api/v20/territoire/bundle"
            f"?lat=46.8139&lon=-71.208&species=cerf&month=10&hour=7&wind_deg=225",
            timeout=30,
        )
        if r.status_code != 200:
            failures.append(f"bundle HTTP {r.status_code}")
        else:
            data = r.json()
            nutri = data.get("nutrition")
            if not nutri:
                failures.append("bundle missing 'nutrition' field")
            else:
                # Verify 7 outputs
                required = [
                    "score_nutritionnel", "carte_carences", "carte_besoins",
                    "zones_alimentation", "attractivite_salines",
                    "influence_corridors", "influence_hotspots",
                ]
                for f in required:
                    if f not in nutri:
                        failures.append(f"nutrition output manquant: {f}")
                # Score range
                sc = nutri.get("score_nutritionnel", -1)
                if not (0 <= sc <= 100):
                    failures.append(f"score_nutritionnel hors [0,100]: {sc}")
                # Cartes non vides
                if len(nutri.get("carte_carences", [])) < 4:
                    failures.append(f"carte_carences trop courte: {len(nutri.get('carte_carences', []))}")
                if len(nutri.get("carte_besoins", [])) < 4:
                    failures.append(f"carte_besoins trop courte: {len(nutri.get('carte_besoins', []))}")
                # Engine name match
                if nutri.get("engine") != ENGINE_NAME:
                    failures.append(f"engine mismatch: {nutri.get('engine')} vs {ENGINE_NAME}")
                else:
                    print(f"[OK] bundle.nutrition: score={sc}, engine={nutri.get('engine')}")
    except Exception as e:
        failures.append(f"bundle exception: {e}")

    # Test 4 — MVT tile nutrition
    try:
        r = requests.get(
            f"{API}/api/v20/territoire/tiles/nutrition/14/4951/5775.json"
            f"?lat=46.8139&lon=-71.208&species=cerf&month=10&hour=7&wind_deg=225",
            timeout=30,
        )
        if r.status_code != 200:
            failures.append(f"MVT nutrition HTTP {r.status_code}")
        else:
            data = r.json()
            if data.get("count", 0) <= 0:
                failures.append("MVT nutrition 0 features (moteur silencieux)")
            else:
                print(f"[OK] MVT nutrition: {data['count']} features")
    except Exception as e:
        failures.append(f"MVT nutrition exception: {e}")

    if failures:
        print("\n=== FAILURES ===")
        for f in failures:
            print(f)
        sys.exit(1)

    print("[OK] test_nutrition_v12: 4 checks passes")


if __name__ == "__main__":
    main()

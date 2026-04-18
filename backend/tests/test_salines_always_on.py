"""
TEST ALWAYS-ON-Omega — SALINES toujours >=1 pour TOUTES especes
Execute: python3 /app/backend/tests/test_salines_always_on.py
"""
import asyncio
import sys
import os

sys.path.insert(0, "/app/backend")


async def test_always_on():
    from engines.v8_institutional.territoire_v10_supra import compute_territoire_v10

    species_list = ["cerf", "orignal", "wapiti"]
    lat, lon = 46.8139, -71.208
    failures = []

    for species in species_list:
        result = await compute_territoire_v10(lat, lon, species, month=10, hour=7, wind_deg=225)
        salines = result.get("salines", [])
        n = len(salines)
        if n < 1:
            failures.append(f"ECHEC: {species} produit {n} salines (attendu >=1)")
            continue
        # Verifier enrichissement V11 present
        v11 = salines[0]
        required_v11 = ["score_bio_global", "score_terrain", "score_nutrition",
                        "score_reseau", "score_accoutumance", "statut_institutionnel"]
        missing = [k for k in required_v11 if k not in v11]
        if missing:
            failures.append(f"ECHEC: {species} champs V11 manquants: {missing}")
            continue
        # Verifier statuts valides
        valid_statuts = {"conforme", "a_optimiser", "non_conforme", "interdite"}
        if v11.get("statut_institutionnel") not in valid_statuts:
            failures.append(f"ECHEC: {species} statut invalide: {v11.get('statut_institutionnel')}")
            continue
        print(f"[OK] {species}: {n} salines, statut={v11['statut_institutionnel']}, bio={v11['score_bio_global']}, nutri={v11['score_nutrition']}")

    if failures:
        print("\n=== FAILURES ===")
        for f in failures:
            print(f)
        sys.exit(1)
    print("\n=== ALL TESTS PASS — ALWAYS-ON-Omega GUARANTEE VALIDEE ===")
    sys.exit(0)


if __name__ == "__main__":
    asyncio.run(test_always_on())

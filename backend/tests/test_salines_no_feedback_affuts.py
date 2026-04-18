"""
TEST SALINES-NO-FEEDBACK-AFFUTS — INTERDICTION FORMELLE V12
============================================================
Directive Commandant STEEVE-MAX: Les salines doivent rester 100% autonomes
du positionnement des affuts. Toute penalite/bonus base sur distance saline
→ affut est INTERDIT (violerait la chasse a l'arc/arbalete, distance ethique 40m).

Verifications:
  1. Aucun champ distance_affut_* dans les salines output
  2. Aucune alerte "Affut trop proche" dans alertes_reseau
  3. Aucune alerte "Affut proche" dans alertes_reseau
  4. Le score_reseau est identique si on passe [] affuts ou une liste d'affuts artificiels
  5. Les salines restent presentes (ALWAYS-ON-Omega, >=1 par espece)

Execute: python3 /app/backend/tests/test_salines_no_feedback_affuts.py
"""
import asyncio
import sys
sys.path.insert(0, "/app/backend")


async def test_no_feedback():
    from engines.v8_institutional.territoire_v10_supra import compute_territoire_v10
    from engines.v8_institutional.engine_salines_v11_supra import enrich_salines_v11_supra

    lat, lon = 46.8139, -71.208
    failures = []

    # 1. Test par pipeline complet (territoire V20) pour cerf/orignal/wapiti
    for species in ["cerf", "orignal", "wapiti"]:
        result = await compute_territoire_v10(lat, lon, species, month=10, hour=7, wind_deg=225)
        salines = result.get("salines", [])
        if not salines:
            failures.append(f"{species}: aucune saline (ALWAYS-ON viole)")
            continue

        for i, s in enumerate(salines):
            # Verification 1: aucun champ distance_affut_*
            for k in s.keys():
                kl = str(k).lower()
                if "distance_affut" in kl or "distance_hunter" in kl or "affut_penalty" in kl:
                    failures.append(f"{species}[{i}]: champ interdit present: {k}")

            # Verification 2/3: aucune alerte affut
            alertes = s.get("alertes_reseau", []) or []
            for alerte in alertes:
                al = str(alerte).lower()
                if "affut" in al:
                    failures.append(f"{species}[{i}]: alerte affut interdite: '{alerte}'")

            # Verification 5: nutrient_target_profile doit etre present (autonomie bio preservee)
            if "nutrient_target_profile" not in s:
                failures.append(f"{species}[{i}]: nutrient_target_profile manquant")

    # 4. Test invariance: score_reseau identique avec affuts=[] ou affuts injectes
    # On construit un territoire minimal et on compare
    test_saline = {
        "lat": lat + 0.001, "lon": lon + 0.001,
        "score": 60.0, "status": "SALINE-VALIDEE-Omega",
        "eau_distance_m": 60, "eau_conforme": True,
        "corridor_distance_m": 70, "corridor_conforme": True,
        "source": "SALINES-Omega-INSTITUTIONNEL", "recalcul_annuel": False,
    }
    terrain = {"pente_deg": 8, "canopy": 0.5, "drainage_class": 3, "hydro_index": 0.4, "distance_habitation_m": 500}
    corridors = [{"type": "extreme", "intensity": 90, "path": [[lat, lon], [lat+0.001, lon+0.001]]}]
    contamination = []
    affuts_vides = []
    affuts_proches = [
        {"lat": lat + 0.001 + 0.0001, "lng": lon + 0.001 + 0.0001, "type": "FIXE_PERMANENT"},  # <50m
        {"lat": lat + 0.001 + 0.0003, "lng": lon + 0.001 + 0.0002, "type": "TEMPORAIRE"},  # ~80m
    ]

    enriched_empty = enrich_salines_v11_supra([dict(test_saline)], terrain, corridors, affuts_vides, contamination, "cerf", 10)
    enriched_with_affuts = enrich_salines_v11_supra([dict(test_saline)], terrain, corridors, affuts_proches, contamination, "cerf", 10)

    sre = enriched_empty[0].get("score_reseau")
    srwa = enriched_with_affuts[0].get("score_reseau")
    if sre != srwa:
        failures.append(f"INVARIANCE VIOLEE: score_reseau change selon affuts ({sre} != {srwa})")

    # Verifier aussi score global V11 identique
    sge = enriched_empty[0].get("score_global_v11")
    sgwa = enriched_with_affuts[0].get("score_global_v11")
    if sge != sgwa:
        failures.append(f"INVARIANCE VIOLEE: score_global_v11 change selon affuts ({sge} != {sgwa})")

    if failures:
        print("\n=== FAILURES — INTERDICTION VIOLEE ===")
        for f in failures:
            print(f)
        sys.exit(1)

    print("[OK] Aucun champ distance_affut_* dans les salines")
    print("[OK] Aucune alerte 'affut' dans alertes_reseau")
    print("[OK] nutrient_target_profile preserve (autonomie bio)")
    print(f"[OK] INVARIANCE affuts: score_reseau={sre} (affuts=[]) == {srwa} (affuts injects)")
    print(f"[OK] INVARIANCE affuts: score_global_v11={sge} invariant")
    print("\n=== SALINES-V12-FEEDBACK-AFFUTS INTERDICTION — CONFORME ===")
    print("=== AUTONOMIE BIOLOGIQUE DES SALINES VALIDEE ===")
    sys.exit(0)


if __name__ == "__main__":
    asyncio.run(test_no_feedback())

"""
TEST AFFUTS-V12 — REGLE 30-80m CORRIDORS MAJEURS + REPOSITIONNEMENT AUTO
========================================================================
Verifie que TOUS les affuts respectent:
  - distance_corridor >= 30m
  - distance_corridor <= 80m
  - classe_corridor_cible in {extreme, majeur}
  - score_affut_v12 > 0
  - affut_repositionne boolean
  - source = "AFFUTS-Omega-V12"
  - ZERO dep SALINES (fields distance_saline_m absent dans output V12)

Execute: python3 /app/backend/tests/test_affuts_v12.py
"""
import asyncio
import sys
sys.path.insert(0, "/app/backend")


async def test_affuts_v12():
    from engines.v8_institutional.territoire_v10_supra import compute_territoire_v10

    species_list = ["cerf", "orignal", "wapiti"]
    lat, lon = 46.8139, -71.208
    failures = []
    repositions_log = []

    for species in species_list:
        result = await compute_territoire_v10(lat, lon, species, month=10, hour=7, wind_deg=225)
        affuts = result.get("affuts", [])
        if not affuts:
            failures.append(f"{species}: aucun affut genere")
            continue

        for idx, a in enumerate(affuts):
            # Source V12
            if a.get("source") != "AFFUTS-Omega-V12":
                failures.append(f"{species}[{idx}]: source != AFFUTS-Omega-V12 ({a.get('source')})")

            # Distance 30-80m
            d = a.get("distance_corridor_m", 0)
            if not (30 <= d <= 80):
                failures.append(f"{species}[{idx}]: distance {d}m HORS PLAGE 30-80m")

            # Classe corridor cible
            classe = a.get("classe_corridor_cible")
            if classe not in ("extreme", "majeur"):
                failures.append(f"{species}[{idx}]: classe_corridor_cible={classe} (attendu extreme/majeur)")

            # Score V12
            score_v12 = a.get("score_affut_v12", 0)
            if score_v12 <= 0:
                failures.append(f"{species}[{idx}]: score_affut_v12={score_v12} (attendu >0)")

            # Reposition log
            if a.get("affut_repositionne"):
                repositions_log.append({
                    "species": species,
                    "idx": idx,
                    "type": a.get("type"),
                    "ancienne_position": a.get("ancienne_position"),
                    "nouvelle_position": a.get("nouvelle_position"),
                    "distance_finale_m": d,
                    "justification": a.get("justification"),
                })

            # ZERO dep salines (V12 ne doit pas avoir ce champ)
            if "distance_saline_m" in a:
                failures.append(f"{species}[{idx}]: contient distance_saline_m (residu V11, refactor incomplet)")

            # Obligatoires V12
            for f in ("affut_repositionne", "score_distance_corridor", "justification", "recommandation", "distance_corridor"):
                if f not in a:
                    failures.append(f"{species}[{idx}]: champ V12 manquant: {f}")

        print(f"[{species}] affuts={len(affuts)} (repositionnes={sum(1 for a in affuts if a.get('affut_repositionne'))})")

    # Ecrire log repositionnements
    with open("/app/memory/AFFUTS_V12_REPOSITIONNES.md", "w") as f:
        f.write("# AFFUTS V12 — LOGS REPOSITIONNEMENTS AUTOMATIQUES\n\n")
        f.write(f"**Execution:** {__file__}\n")
        f.write(f"**Total repositions:** {len(repositions_log)}\n\n")
        if not repositions_log:
            f.write("Aucun affut n'a necessite de repositionnement automatique dans ce test.\n")
            f.write("Les algorithmes de placement V12 generent deja les affuts dans la plage 30-80m par construction.\n")
        else:
            for r in repositions_log:
                f.write(f"## {r['species']} affut #{r['idx']} ({r['type']})\n")
                f.write(f"- Ancienne position: {r['ancienne_position']}\n")
                f.write(f"- Nouvelle position: {r['nouvelle_position']}\n")
                f.write(f"- Distance finale: {r['distance_finale_m']}m\n")
                f.write(f"- Justification: {r['justification']}\n\n")

    if failures:
        print("\n=== FAILURES ===")
        for f in failures:
            print(f)
        sys.exit(1)
    print(f"\n=== AFFUTS-V12 CONFORME — TOUS AFFUTS DANS 30-80m, ZERO DEP SALINES ===")
    print(f"Log repositionnements: /app/memory/AFFUTS_V12_REPOSITIONNES.md ({len(repositions_log)} entrees)")
    sys.exit(0)


if __name__ == "__main__":
    asyncio.run(test_affuts_v12())

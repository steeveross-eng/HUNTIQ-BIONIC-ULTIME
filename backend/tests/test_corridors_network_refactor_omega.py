"""
Phase XI-SUPRA-N — TEST ANTI-RÉGRESSION CORRIDORS NETWORK REFACTOR Ω
=====================================================================
Valide que :
  1. Les corridors sont générés entre zones vitales (node_from/node_to présents)
  2. Aucun générateur radial (origines multiples, pas toutes identiques)
  3. Chaque corridor a un attractivity_score ≥ 10
  4. Hiérarchie diversifiée (pas 100% veine_principale)
  5. Différentiation espèce (sinuosity chevreuil ≥ 1.80)
  6. Tolérance segment ≤ 20 m respectée
  7. version == Ω-NETWORK_LOCKED
"""
import asyncio
import sys

sys.path.insert(0, "/app/backend")

from engines.v8_institutional.engine_ia_corridors_organic_omega import (  # noqa: E402
    generate_organic_corridors, validate_organic, SPECIES_BEHAVIOR, ENGINE_VERSION, ORGANIC_CONFIG,
)

errors: list[str] = []

# 1. Version Ω-NETWORK_LOCKED
if "NETWORK_LOCKED" not in ENGINE_VERSION:
    errors.append(f"ENGINE_VERSION doit contenir NETWORK_LOCKED: {ENGINE_VERSION}")

# 2. Configuration BLOC 5 (seuils hiérarchie recalibrés)
h = ORGANIC_CONFIG["hierarchy"]
if h["veine_principale"]["min_intensity"] < 75:
    errors.append(f"veine_principale.min_intensity < 75 (BLOC 5)")
if h["veine_secondaire"]["min_intensity"] < 50:
    errors.append(f"veine_secondaire.min_intensity < 50 (BLOC 5)")

# 3. Différentiation espèce (BLOC 6)
if SPECIES_BEHAVIOR["chevreuil"]["sinuosity"] < 1.80:
    errors.append(f"chevreuil sinuosity < 1.80 (BLOC 6.1): {SPECIES_BEHAVIOR['chevreuil']['sinuosity']}")
if SPECIES_BEHAVIOR["ours_noir"]["n_corridors"] < 12:
    errors.append(f"ours_noir n_corridors < 12 (BLOC 6.4): {SPECIES_BEHAVIOR['ours_noir']['n_corridors']}")
if SPECIES_BEHAVIOR["orignal"]["hydro_dep"] < 0.90:
    errors.append(f"orignal hydro_dep < 0.90 (BLOC 6.2): {SPECIES_BEHAVIOR['orignal']['hydro_dep']}")

# 4. Test live pipeline
async def test_pipeline():
    bundle = await generate_organic_corridors(45.10, -72.80, "chevreuil")
    corridors = bundle.get("corridors", [])
    if len(corridors) < 5:
        errors.append(f"Moins de 5 corridors générés: {len(corridors)}")

    # BLOC 1 : Pas de générateur radial
    origins = {tuple(c["path"][0]) for c in corridors if c.get("path")}
    if len(origins) < 2 and len(corridors) >= 4:
        errors.append(f"ERREUR_RADIAL_GENERATOR: {len(origins)} origine(s) pour {len(corridors)} corridors")

    # BLOC 2 : chaque corridor a node_from/node_to
    for c in corridors:
        if not c.get("node_from") or not c.get("node_to"):
            errors.append(f"Corridor {c.get('id')} sans node_from/node_to (BLOC 2)")
            break

    # BLOC 3 : attractivity_score ≥ 10
    for c in corridors:
        if c.get("attractivity_score", 0) < 10:
            errors.append(f"Corridor {c.get('id')} attractivity_score < 10 (BLOC 3)")
            break

    # BLOC 5 : hiérarchie diversifiée
    hier_set = {c.get("hierarchy") for c in corridors}
    if len(corridors) >= 5 and len(hier_set) == 1:
        errors.append(f"ERREUR_HIERARCHIE_Ω: tous en {hier_set} ({len(corridors)} corridors)")

    # Validation officielle
    v = validate_organic(bundle)
    if not v["conforme"]:
        errors.append(f"validate_organic non conforme: {len(v['violations'])} violations")
        for viol in v["violations"][:3]:
            errors.append(f"  - {viol}")
    return len(corridors), v["hierarchy_distribution"]

try:
    n_corr, distrib = asyncio.run(test_pipeline())
except Exception as e:
    errors.append(f"Pipeline exception: {e}")
    n_corr = 0
    distrib = {}

if errors:
    print("FAIL: Phase N CORRIDORS NETWORK REFACTOR non conforme:")
    for e in errors:
        print(f"  - {e}")
    sys.exit(1)

print(f"OK: ENGINE-IA-CORRIDORS-ORGANIC-Ω Phase N (v{ENGINE_VERSION[:24]}…)")
print(f"    {n_corr} corridors réseau, hiérarchie={distrib}, 0 violation")
sys.exit(0)

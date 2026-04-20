"""SELF-AUDIT-Ω — test_species_weighting_profiles (Phase X)"""
import sys
sys.path.insert(0, "/app/backend")

from engines.v8_institutional.species_weighting_profiles import (  # noqa: E402
    SPECIES_WEIGHTS, get_species_weights,
)

errors = []
expected = {"orignal", "chevreuil", "wapiti", "ours_noir", "dindon_sauvage"}
if set(SPECIES_WEIGHTS.keys()) != expected:
    errors.append(f"espèces attendues {expected} trouvées {set(SPECIES_WEIGHTS.keys())}")

for sp in expected:
    w = get_species_weights(sp)
    if not w:
        errors.append(f"{sp}: aucun poids retourné")
        continue
    total = round(sum(w.values()), 3)
    if abs(total - 1.0) > 0.01:
        errors.append(f"{sp}: renormalisation incorrecte total={total}")

# Aliases
for alias, canon in [("cerf", "chevreuil"), ("moose", "orignal"), ("bear", "ours_noir"), ("turkey", "dindon_sauvage")]:
    if get_species_weights(alias) is None:
        errors.append(f"alias '{alias}' -> '{canon}' non résolu")

if errors:
    print("FAIL:"); [print(" -", e) for e in errors]; sys.exit(1)
print(f"OK: 5 profils espèces renormalisés, {len(expected)} alias résolus")
sys.exit(0)

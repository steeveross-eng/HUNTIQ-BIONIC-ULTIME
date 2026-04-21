"""
SELF-AUDIT-Ω — test_ia_corridors_organic (Phase XI-SUPRA-M)
============================================================
Valide ENGINE-IA-CORRIDORS-ORGANIC-Ω :
  - Import OK
  - Config ORGANIC verrouillée (points 60-120, thickness 1.2-3.0, rayon 420-780,
    hierarchy 3 niveaux, render_modes x3)
  - 5 espèces supportées avec profils behavior complets
  - Validation de bundle ORGANIC (violations détectées sur corridors dégénérés)
  - Baseline TERRITOIRE_OMEGA_STABLE scellable
"""
import sys

sys.path.insert(0, "/app/backend")

from engines.v8_institutional.engine_ia_corridors_organic_omega import (  # noqa: E402
    ENGINE_NAME, ENGINE_VERSION, ORGANIC_CONFIG, SPECIES_BEHAVIOR,
    IA_ADVANCED_STATUS, validate_organic, seal_baseline_stable, get_baseline_stable,
)

errors: list[str] = []

# 1. Identité engine
if ENGINE_NAME != "ENGINE-IA-CORRIDORS-ORGANIC-Ω":
    errors.append(f"ENGINE_NAME invalide: {ENGINE_NAME}")
if "XI-SUPRA-" not in ENGINE_VERSION:
    errors.append(f"ENGINE_VERSION doit contenir XI-SUPRA-*: {ENGINE_VERSION}")

# 2. Config verrouillée (Phase N — l'invariant prioritaire est segment ≤ 20 m)
expected = {
    "functional_radius_min_m": 420.0,
    "functional_radius_max_m": 780.0,
    "segment_max_m": 20.0,
    "angle_max_deg": 45.0,
    "thickness_min_px": 1.2,
    "thickness_max_px": 3.0,
    "interconnect_threshold_m": 50.0,
    "slope_reroute_deg": 35.0,
    "water_min_dist_m": 20.0,
}
for k, v in expected.items():
    if ORGANIC_CONFIG.get(k) != v:
        errors.append(f"ORGANIC_CONFIG.{k} = {ORGANIC_CONFIG.get(k)} ≠ {v}")

# 3. Hiérarchie 3 niveaux
hierarchy = ORGANIC_CONFIG.get("hierarchy", {})
for lvl in ["veine_principale", "veine_secondaire", "capillaire"]:
    if lvl not in hierarchy:
        errors.append(f"hierarchy manquant: {lvl}")

# 4. Render modes x3
modes = ORGANIC_CONFIG.get("render_modes_enabled", [])
for m in ["density_mode", "heat_mode", "veine_animale_mode"]:
    if m not in modes:
        errors.append(f"render_mode manquant: {m}")

# 5. Gradient couleurs
grad = ORGANIC_CONFIG.get("gradient_colors")
if grad != ["#FF8F00", "#FF9F00"]:
    errors.append(f"gradient_colors invalide: {grad}")

# 6. Species behavior (5 espèces avec paramètres complets)
required_species = {"chevreuil", "orignal", "wapiti", "ours_noir", "dindon_sauvage"}
missing_sp = required_species - set(SPECIES_BEHAVIOR.keys())
if missing_sp:
    errors.append(f"espèces manquantes: {missing_sp}")

required_params = {"prudence", "amplitude", "vitesse", "ouverture_preferee",
                   "hydro_dep", "couvert_pref", "sinuosity", "n_corridors"}
for sp, profile in SPECIES_BEHAVIOR.items():
    missing_p = required_params - set(profile.keys())
    if missing_p:
        errors.append(f"{sp}: paramètres manquants {missing_p}")

# 7. IA avancée — schémas prêts
for k in ["ia_predictive", "ia_generative", "ia_adaptative"]:
    if not IA_ADVANCED_STATUS.get(k, {}).get("ready_schema"):
        errors.append(f"{k}.ready_schema != True")

# 8. Validation détecte corridors dégénérés (Phase N : 1 pt → points_below_min avec min=30)
bad_bundle = {"corridors": [{"id": "bad", "path": [[45.0, -72.8]], "hierarchy": "veine_principale"}]}
v = validate_organic(bad_bundle)
if v["conforme"]:
    errors.append("validate_organic a accepté un corridor à 1 point")
rules_hit = {vv["rule"] for vv in v["violations"]}
if "points_below_min" not in rules_hit:
    errors.append("points_below_min non détecté sur corridor à 1 point")
if "thickness_profile_missing" not in rules_hit:
    errors.append("thickness_profile_missing non détecté")
if "species_profile_missing" not in rules_hit:
    errors.append("species_profile_missing non détecté")

# 9. Baseline — cycle seal/get (utilise un bundle synthétique minimal)
synthetic_bundle = {
    "waypoint": {"lat": 45.10, "lon": -72.80, "species": "chevreuil"},
    "corridors_count": 1,
    "hierarchy_counts": {"veine_principale": 1, "veine_secondaire": 0, "capillaire": 0, "connector": 0},
    "fused_behavioral_probability": {"fused_score": 0.5},
}
sealed = seal_baseline_stable(synthetic_bundle)
if not sealed.get("sha256") or len(sealed["sha256"]) != 64:
    errors.append("sha256 baseline invalide")
get_b = get_baseline_stable()
if not get_b.get("sealed"):
    errors.append("get_baseline_stable() sealed != True après seal")
if get_b.get("sha256") != sealed.get("sha256"):
    errors.append("get_baseline_stable sha256 ≠ sealed sha256")

if errors:
    print("FAIL: IA-CORRIDORS-ORGANIC-Ω non conforme:")
    for e in errors:
        print(f"  - {e}")
    sys.exit(1)

print(f"OK: ENGINE-IA-CORRIDORS-ORGANIC-Ω (v{ENGINE_VERSION})")
print(f"    {len(SPECIES_BEHAVIOR)} espèces, hiérarchie 3 niveaux, 3 modes render, baseline sha={sealed['sha256'][:16]}…")
sys.exit(0)

"""SELF-AUDIT-Ω — test_contamination_propagation (Phase X-C)
Valide que contamination_v2 propage son impact dans habitat/population/stress.
"""
import sys
sys.path.insert(0, "/app/backend")

from engines.v8_institutional.engine_habitat_supra import compute_habitat_supra  # noqa: E402
from engines.v8_institutional.engine_population_dynamics_omega import compute_population_dynamics  # noqa: E402
from engines.v8_institutional.engine_stress_anthropique_omega import compute_stress_anthropique  # noqa: E402

errors = []
terrain = {"canopy": 0.6, "strate_1_3m": 0.4, "feuillus_ratio": 0.5, "couvert_pct": 65,
           "pente_deg": 12, "exposition_deg": 180, "distance_eau_m": 200,
           "drainage_class": 3, "cost_surface": 0.5, "connectivity": 0.5}
cv2_high = {"cwd_risk": "ELEVE", "distance_nearest_cwd_km": 5.0, "score": 20}
cv2_none = None

# HABITAT
h_none = compute_habitat_supra(terrain, contamination_v2=cv2_none)
h_high = compute_habitat_supra(terrain, contamination_v2=cv2_high)
if h_high["score"] >= h_none["score"]:
    errors.append(f"habitat: pas de malus appliqué (none={h_none['score']} high={h_high['score']})")
if not h_high.get("contamination_v2_impact"):
    errors.append("habitat: contamination_v2_impact absent")

# POPULATION
p_none = compute_population_dynamics("chevreuil", contamination_v2=cv2_none)
p_high = compute_population_dynamics("chevreuil", contamination_v2=cv2_high)
if p_high["parametres_demographiques"]["mortalite"] <= p_none["parametres_demographiques"]["mortalite"]:
    errors.append(f"population: mortalité non augmentée")
if p_high["taux_croissance_r"] >= p_none["taux_croissance_r"]:
    errors.append("population: taux croissance non abaissé")

# STRESS
s_none = compute_stress_anthropique(terrain, hour=12, contamination_v2=cv2_none)
s_high = compute_stress_anthropique(terrain, hour=12, contamination_v2=cv2_high)
if s_high["tranquillite_score"] >= s_none["tranquillite_score"]:
    errors.append(f"stress: tranquillité non abaissée (none={s_none['tranquillite_score']} high={s_high['tranquillite_score']})")
if not s_high.get("contamination_v2_impact"):
    errors.append("stress: contamination_v2_impact absent")

if errors:
    print("FAIL:"); [print(" -", e) for e in errors]; sys.exit(1)
print(f"OK: propagation contamination_v2 (habitat Δ={round(h_none['score']-h_high['score'],1)}, pop Δmort=+{round(p_high['parametres_demographiques']['mortalite']-p_none['parametres_demographiques']['mortalite'],3)}, stress Δtranq={round(s_none['tranquillite_score']-s_high['tranquillite_score'],1)})")
sys.exit(0)

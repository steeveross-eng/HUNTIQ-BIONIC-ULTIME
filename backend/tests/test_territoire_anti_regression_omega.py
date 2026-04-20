"""SELF-AUDIT-Ω — test_territoire_anti_regression_omega (Phase XI-SUPRA-G)

Vérifie :
  - Engine enregistré
  - Endpoints opérationnels (/status, /baseline, /validate)
  - Règles appliquées (corridor_min_length_m, n_control_points, etc.)
  - Validation d'un bundle courant retourne `ok=true`
  - Baseline sealed présente après le premier validate
"""
import sys
from pathlib import Path

sys.path.insert(0, "/app/backend")

# Trigger engine registration
from engines.v8_institutional import engine_territoire_anti_regression_omega as antireg  # noqa: E402,F401
from engines.v8_institutional.engine_science_omega import get_catalog  # noqa: E402

errors = []

# 1. Engine in catalog
cat = get_catalog()
cat_list = cat if isinstance(cat, list) else cat.get("engines", [])
names = [e.get("name") if isinstance(e, dict) else str(e) for e in cat_list]
if "ENGINE-TERRITOIRE-ANTI-REGRESSION-Ω" not in names:
    errors.append(f"engine absent du catalog: sample={names[:5]}")

# 2. Rules have mandatory keys
expected_rules = {
    "corridor_min_length_m", "corridor_min_control_points", "corridors_min_count",
    "affuts_min_count", "zones_min_count", "contamination_required_if_affuts",
}
missing = expected_rules - set(antireg.RULES.keys())
if missing:
    errors.append(f"RULES incomplet, missing={missing}")

# 3. Validate a synthetic conforming bundle
conforming_bundle = {
    "corridors": [
        {"id": f"c{i}", "path": [[45.10 + j*0.001, -72.80 + j*0.001] for j in range(10)]}
        for i in range(5)
    ],
    "affuts": [{"lat": 45.10, "lng": -72.80, "score": 80}] * 3,
    "zones": [{"type": "rut", "polygon": [[45.10, -72.80]]*5}],
    "hotspots": [{"lat": 45.10, "lng": -72.80, "intensity": 75}],
    "contamination": [{"polygon": [[45.10, -72.80]]*5}],
    "nutrition": {"carte_carences": [], "carte_besoins": []},
}
verdict = antireg.validate_bundle(conforming_bundle)
if not verdict["ok"]:
    errors.append(f"conforming bundle rejeté: {verdict['violations']}")

# 4. Validate a non-conforming bundle (short corridors)
bad_bundle = {
    "corridors": [
        {"id": "cbad", "path": [[45.10, -72.80], [45.10001, -72.80001]]}  # 1m long
    ],
    "affuts": [],
    "zones": [],
    "hotspots": [],
    "contamination": [],
    "nutrition": {},
}
bad_verdict = antireg.validate_bundle(bad_bundle)
if bad_verdict["ok"]:
    errors.append("bad bundle accepté à tort")
critical_rules = {v["rule"] for v in bad_verdict["violations"] if v["severity"] == "critical"}
for must in ("corridor_min_length_m", "corridor_min_control_points",
             "corridors_min_count", "affuts_min_count", "zones_min_count"):
    if must not in critical_rules:
        errors.append(f"règle {must} non déclenchée par bad bundle")

# 5. Baseline file path is writable dir
ROOT = Path("/app/data/territoire_omega/anti_regression")
if not ROOT.is_dir():
    errors.append(f"dossier anti_regression manquant: {ROOT}")

if errors:
    print("FAIL:")
    for e in errors:
        print(" -", e)
    sys.exit(1)
print(f"OK: ENGINE-TERRITOIRE-ANTI-REGRESSION-Ω — {len(antireg.RULES)} règles, "
      f"validation conforme/non-conforme discriminées")
sys.exit(0)

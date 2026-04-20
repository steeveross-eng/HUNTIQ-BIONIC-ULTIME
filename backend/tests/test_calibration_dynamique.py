"""SELF-AUDIT-Ω — test_calibration_dynamique (Phase X)"""
import sys
sys.path.insert(0, "/app/backend")

from engines.v8_institutional.engine_calibration_dynamique_omega import (  # noqa: E402
    Observation, ingest_observation, get_calibration_status, get_dynamic_weights,
)

errors = []

# Ingestion observations fictives
for src in ["camera-reconyx", "gps-cellulaire", "pin", "recolte"]:
    ingest_observation(Observation(source_type=src, lat=45.5, lon=-72.5, species="chevreuil", confidence=0.85))

st = get_calibration_status()
if st["observations_count"] < 4:
    errors.append(f"ingestion fail: {st['observations_count']}/4")
if not st["weight_adjustments"]:
    errors.append("aucun ajustement calculé")

base = {"hotspots": 0.06, "nutrition": 0.10, "habitat": 0.08, "connectivite": 0.06, "stress_anthropique": 0.08, "population": 0.06, "comportement_bio": 0.06, "ia_vision": 0.02}
dyn = get_dynamic_weights(base)
total = round(sum(dyn.values()), 3)
if abs(total - 1.0) > 0.05:
    errors.append(f"renorm incorrecte: total={total}")

if errors:
    print("FAIL:"); [print(" -", e) for e in errors]; sys.exit(1)
print(f"OK: calibration dynamique ({st['observations_count']} obs, {len(st['weight_adjustments'])} axes ajustés, total poids={total})")
sys.exit(0)

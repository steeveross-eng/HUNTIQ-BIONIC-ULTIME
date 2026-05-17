"""SELF-AUDIT-Ω — test_render_hydat (Phase XI-SUPRA)"""
import sys
from pathlib import Path
sys.path.insert(0, "/app/backend")

from engines.v8_institutional.engine_render_omega import LAYERS_REQUIRED, SYMBOLOGY  # noqa: E402
from engines.v8_institutional.federal_datasets_omega import HYDAT_STATIONS  # noqa: E402

errors = []
hyd = next((l for l in LAYERS_REQUIRED if l["id"] == "stations_hydat"), None)
if not hyd:
    errors.append("couche stations_hydat absente")
elif hyd["symbology"] != "point-lightblue":
    errors.append(f"stations_hydat symbology != point-lightblue ({hyd['symbology']})")

if SYMBOLOGY.get("point-lightblue", {}).get("color") != "#4FC3F7":
    errors.append("point-lightblue != #4FC3F7")

if len(HYDAT_STATIONS) < 200:
    errors.append(f"HYDAT < 200 stations")

bl = Path("/app/frontend/src/components/territoire/BionicLayersV8.jsx").read_text()
if "hydat_nearby" not in bl:
    errors.append("hydat_nearby non consommé par renderer")

if errors:
    print("FAIL:"); [print(" -", e) for e in errors]; sys.exit(1)
print(f"OK: couche HYDAT conforme ({len(HYDAT_STATIONS)} stations, point-lightblue #4FC3F7)")
sys.exit(0)

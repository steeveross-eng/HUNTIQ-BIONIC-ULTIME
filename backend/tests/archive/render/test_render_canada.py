"""SELF-AUDIT-Ω — test_render_canada (Phase XI-SUPRA)"""
import sys
from pathlib import Path
sys.path.insert(0, "/app/backend")

from engines.v8_institutional.engine_render_omega import LAYERS_REQUIRED  # noqa: E402
from engines.v8_institutional.engine_canada_omega import PROVINCES  # noqa: E402

errors = []
canada = next((l for l in LAYERS_REQUIRED if l["id"] == "zones_fauniques_canada"), None)
if not canada:
    errors.append("couche zones_fauniques_canada absente")
elif canada["zoom_min"] != 0:
    errors.append(f"canada zoom_min!=0 ({canada['zoom_min']}) — doit être macro-visible")

if len(PROVINCES) < 13:
    errors.append(f"PROVINCES < 13 ({len(PROVINCES)})")

bl = Path("/app/frontend/src/components/territoire/BionicLayersV8.jsx").read_text()
if "canada_zones_summary" not in bl:
    errors.append("canada_zones_summary non consommé par renderer")

if errors:
    print("FAIL:"); [print(" -", e) for e in errors]; sys.exit(1)
print(f"OK: couche Canada-Ω conforme ({len(PROVINCES)} provinces macro-visibles)")
sys.exit(0)

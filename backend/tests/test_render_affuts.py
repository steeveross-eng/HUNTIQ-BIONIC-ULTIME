"""SELF-AUDIT-Ω — test_render_affuts (Phase XI-SUPRA)"""
import sys
from pathlib import Path
sys.path.insert(0, "/app/backend")

from engines.v8_institutional.engine_render_omega import LAYERS_REQUIRED, ZOOM_RULES  # noqa: E402

errors = []
aff = next((l for l in LAYERS_REQUIRED if l["id"] == "affuts"), None)
if not aff:
    errors.append("couche affuts absente")
elif aff["zoom_min"] < 16:
    errors.append(f"affuts zoom_min={aff['zoom_min']} (attendu >=16)")

if "affuts" not in ZOOM_RULES.get("detail", {}).get("layers", []):
    errors.append("affuts pas dans zoom detail")

bl = Path("/app/frontend/src/components/territoire/BionicLayersV8.jsx").read_text()
if "showAffuts" not in bl or "affuts" not in bl:
    errors.append("affuts non rendus dans BionicLayersV8")

if errors:
    print("FAIL:"); [print(" -", e) for e in errors]; sys.exit(1)
print(f"OK: couche affuts conforme (zoom_min={aff['zoom_min']}, détail OK)")
sys.exit(0)

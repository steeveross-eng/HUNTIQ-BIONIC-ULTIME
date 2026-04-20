"""SELF-AUDIT-Ω — test_render_corridors (Phase XI-SUPRA)
Vérifie présence de la couche corridors dans render-config + BionicLayersV8.
"""
import sys
from pathlib import Path
sys.path.insert(0, "/app/backend")

from engines.v8_institutional.engine_render_omega import get_render_config, LAYERS_REQUIRED  # noqa: E402

errors = []
cfg = get_render_config()

if len(LAYERS_REQUIRED) < 14:
    errors.append(f"Layers requis < 14 ({len(LAYERS_REQUIRED)})")

ids = {l["id"] for l in LAYERS_REQUIRED}
if "corridors" not in ids:
    errors.append("corridors absent du registre LAYERS_REQUIRED")

bl = Path("/app/frontend/src/components/territoire/BionicLayersV8.jsx").read_text()
for marker in ["corridors", "showCorridors"]:
    if marker not in bl:
        errors.append(f"marker absent du renderer: {marker}")

if errors:
    print("FAIL:"); [print(" -", e) for e in errors]; sys.exit(1)
print(f"OK: couche corridors conforme ({len(LAYERS_REQUIRED)} couches totales enregistrées)")
sys.exit(0)

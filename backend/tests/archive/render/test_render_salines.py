"""SELF-AUDIT-Ω — test_render_salines (Phase XI-SUPRA)"""
import sys
from pathlib import Path
sys.path.insert(0, "/app/backend")

from engines.v8_institutional.engine_render_omega import LAYERS_REQUIRED, SYMBOLOGY  # noqa: E402

errors = []
sal = next((l for l in LAYERS_REQUIRED if l["id"] == "salines"), None)
if not sal:
    errors.append("couche salines absente")
elif sal["symbology"] != "square-blue":
    errors.append(f"salines symbology != square-blue ({sal['symbology']})")

if SYMBOLOGY.get("square-blue", {}).get("color") != "#1565C0":
    errors.append(f"square-blue color différent (attendu #1565C0)")

bl = Path("/app/frontend/src/components/territoire/BionicLayersV8.jsx").read_text()
if "salines" not in bl:
    errors.append("salines absent du renderer")

if errors:
    print("FAIL:"); [print(" -", e) for e in errors]; sys.exit(1)
print(f"OK: couche salines conforme (square-blue {SYMBOLOGY['square-blue']['color']})")
sys.exit(0)

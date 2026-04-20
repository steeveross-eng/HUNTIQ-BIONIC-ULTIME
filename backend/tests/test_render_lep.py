"""SELF-AUDIT-Ω — test_render_lep (Phase XI-SUPRA)"""
import sys
from pathlib import Path
sys.path.insert(0, "/app/backend")

from engines.v8_institutional.engine_render_omega import LAYERS_REQUIRED, SYMBOLOGY  # noqa: E402
from engines.v8_institutional.federal_datasets_omega import LEP_HABITATS  # noqa: E402

errors = []
lep = next((l for l in LAYERS_REQUIRED if l["id"] == "habitats_lep"), None)
if not lep:
    errors.append("couche habitats_lep absente")
elif lep["symbology"] != "polygon-violet":
    errors.append(f"habitats_lep symbology != polygon-violet ({lep['symbology']})")

if SYMBOLOGY.get("polygon-violet", {}).get("color") != "#8E24AA":
    errors.append("polygon-violet color différent de #8E24AA")

if len(LEP_HABITATS) < 100:
    errors.append(f"LEP < 100 habitats")

bl = Path("/app/frontend/src/components/territoire/BionicLayersV8.jsx").read_text()
if "lep_nearby" not in bl:
    errors.append("lep_nearby non consommé par renderer")

if errors:
    print("FAIL:"); [print(" -", e) for e in errors]; sys.exit(1)
print(f"OK: couche LEP conforme ({len(LEP_HABITATS)} habitats, violet #8E24AA)")
sys.exit(0)

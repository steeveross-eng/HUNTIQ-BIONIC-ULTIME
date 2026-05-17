"""SELF-AUDIT-Ω — test_render_contamination (Phase XI-SUPRA)
Valide la couche contamination_v2 (heatmap + zones MDC).
"""
import sys
from pathlib import Path
sys.path.insert(0, "/app/backend")

from engines.v8_institutional.engine_render_omega import LAYERS_REQUIRED, SYMBOLOGY, validate_render_payload  # noqa: E402

errors = []
cv2 = next((l for l in LAYERS_REQUIRED if l["id"] == "contamination_v2"), None)
if not cv2:
    errors.append("couche contamination_v2 absente")

if not SYMBOLOGY.get("heatmap-institutional"):
    errors.append("symbologie heatmap-institutional absente")

# Validation payload simulé
fake_bundle = {l["bundle_key"]: [] for l in LAYERS_REQUIRED}
res = validate_render_payload(fake_bundle)
if not res["conforme"]:
    errors.append(f"payload full-keys non conforme: {res['missing']}")

# Payload manquant contamination_v2_heatmap
fake_bundle2 = {l["bundle_key"]: [] for l in LAYERS_REQUIRED if l["id"] != "contamination_v2"}
res2 = validate_render_payload(fake_bundle2)
if res2["conforme"]:
    errors.append("validation ne détecte pas l'absence de contamination_v2")

bl = Path("/app/frontend/src/components/territoire/BionicLayersV8.jsx").read_text()
if "contamination_v2_heatmap" not in bl:
    errors.append("contamination_v2_heatmap non rendu")

if errors:
    print("FAIL:"); [print(" -", e) for e in errors]; sys.exit(1)
print(f"OK: couche contamination_v2 conforme (heatmap + validation 14/14)")
sys.exit(0)

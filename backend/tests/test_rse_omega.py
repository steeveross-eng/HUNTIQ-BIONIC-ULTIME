"""
TEST RSE-Ω — Validation RENDER-SPEC-OMEGA SUPRA-EXTENDED
=========================================================
12e suite SELF-AUDIT-Ω. Verifie:
  1. Config centralisee RSE_LAYERS_CONFIG accessible (8 layers)
  2. Backend MVT /tiles/nutrition sert features non vides (gap GAP#1 resolu cote serveur)
  3. Bundle expose 'nutrition' conforme
  4. RenderGuardOmega.js + InstitutionalPopup.js presents (front-side hooks prets)
  5. NUTRITION_SEVERITY_COLORS exportes

Execution: python3 /app/backend/tests/test_rse_omega.py
"""
import os
import re
import sys
import requests

API = os.environ.get("SELF_TEST_API", "http://localhost:8001")
FRONT_CFG = "/app/frontend/src/config/territoire_defaults.js"
FRONT_GUARD = "/app/frontend/src/components/territoire/RenderGuardOmega.js"
FRONT_POPUP = "/app/frontend/src/components/territoire/InstitutionalPopup.js"
FRONT_RENDERER = "/app/frontend/src/components/territoire/BionicLayersV8.jsx"

REQUIRED_LAYERS = ["contamination", "zones", "corridors", "nutrition", "salines", "hotspots", "affuts", "vent"]


def main():
    failures = []

    # Test 1 — Config centralisee RSE_LAYERS_CONFIG
    try:
        with open(FRONT_CFG) as f:
            cfg_src = f.read()
        if "RSE_LAYERS_CONFIG" not in cfg_src:
            failures.append("RSE_LAYERS_CONFIG missing in territoire_defaults.js")
        for lyr in REQUIRED_LAYERS:
            if re.search(rf"\b{lyr}\s*:", cfg_src) is None:
                failures.append(f"layer '{lyr}' missing in RSE_LAYERS_CONFIG")
        if "NUTRITION_SEVERITY_COLORS" not in cfg_src:
            failures.append("NUTRITION_SEVERITY_COLORS missing in territoire_defaults.js")
    except Exception as e:
        failures.append(f"config read failed: {e}")

    # Test 2 — RenderGuard + Popup present
    for path, sig in [
        (FRONT_GUARD, "validateElement"),
        (FRONT_POPUP, "buildInstitutionalPopup"),
    ]:
        try:
            with open(path) as f:
                src = f.read()
            if sig not in src:
                failures.append(f"{os.path.basename(path)} missing signature '{sig}'")
        except Exception as e:
            failures.append(f"{os.path.basename(path)} read failed: {e}")

    # Test 3 — Renderer wires showNutrition + logRenderCycle
    try:
        with open(FRONT_RENDERER) as f:
            r_src = f.read()
        if "showNutrition" not in r_src:
            failures.append("BionicLayersV8 missing 'showNutrition' prop")
        if "logRenderCycle" not in r_src:
            failures.append("BionicLayersV8 missing 'logRenderCycle' call")
        if "validateElement" not in r_src:
            failures.append("BionicLayersV8 missing 'validateElement' call")
    except Exception as e:
        failures.append(f"renderer read failed: {e}")

    # Test 4 — Backend MVT nutrition serves features
    try:
        r = requests.get(
            f"{API}/api/v20/territoire/tiles/nutrition/14/4951/5775.json"
            f"?lat=46.8139&lon=-71.208&species=cerf&month=10&hour=7&wind_deg=225",
            timeout=30,
        )
        if r.status_code != 200:
            failures.append(f"MVT nutrition HTTP {r.status_code}")
        elif r.json().get("count", 0) <= 0:
            failures.append("MVT nutrition 0 features")
    except Exception as e:
        failures.append(f"MVT nutrition exception: {e}")

    # Test 5 — Bundle exposes nutrition
    try:
        r = requests.get(
            f"{API}/api/v20/territoire/bundle"
            f"?lat=46.8139&lon=-71.208&species=cerf&month=10&hour=7&wind_deg=225&wind_speed=15",
            timeout=30,
        )
        if r.status_code != 200:
            failures.append(f"bundle HTTP {r.status_code}")
        else:
            data = r.json()
            if not data.get("nutrition"):
                failures.append("bundle missing 'nutrition'")
    except Exception as e:
        failures.append(f"bundle exception: {e}")

    if failures:
        print("\n=== FAILURES ===")
        for f in failures:
            print(f)
        sys.exit(1)

    print("[OK] test_rse_omega: 5 checks passes")


if __name__ == "__main__":
    main()

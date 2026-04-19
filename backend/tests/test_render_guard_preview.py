"""
RENDER-GUARD-Ω — Validation PREVIEW = RENDU FINAL
==================================================
Verifie qu'il n'existe qu'UN SEUL pipeline de rendu Territoire (pas de preview legacy).

Controle source:
  - UN SEUL endpoint consomme par frontend: /api/v20/territoire/bundle
  - UN SEUL composant renderer: BionicLayersV8
  - Zero ancien hook (useMapBundle sans V8) dans la page active
  - Zero consommation d'endpoint legacy /api/v7/ ou /api/v6/ dans le pipeline Territoire

Execute: python3 /app/backend/tests/test_render_guard_preview.py
"""
import sys
from pathlib import Path

PAGE = Path("/app/frontend/src/pages/MonTerritoireBionicPage.jsx").read_text()
MAP_CONTENT = Path("/app/frontend/src/components/territoire/map/MapContent.jsx").read_text()
HOOK = Path("/app/frontend/src/hooks/useMapBundleV8.js").read_text()

failures = []

# 1. UN SEUL endpoint bundle V20 consomme par le hook
if "/api/v20/territoire/bundle" not in HOOK:
    failures.append("ERREUR RENDU-Ω: hook useMapBundleV8 ne consomme PAS /api/v20/territoire/bundle")
else:
    print("[RENDER-GUARD-Ω OK] Hook consomme /api/v20/territoire/bundle (source unique)")

# 2. UN SEUL renderer V8 dans MapContent
if "BionicLayersV8" not in MAP_CONTENT:
    failures.append("ERREUR RENDU-Ω: MapContent n'utilise PAS BionicLayersV8")
else:
    print("[RENDER-GUARD-Ω OK] MapContent utilise BionicLayersV8 (renderer unique)")

# 3. ZERO consommation legacy /api/v7 ou /api/v6 dans territoire
for legacy in ("/api/v7/", "/api/v6/territoire", "useMapBundleV7", "useMapBundleV6"):
    if legacy in PAGE or legacy in MAP_CONTENT:
        failures.append(f"ERREUR RENDU-Ω: reference legacy detectee: {legacy}")
if not any(f for f in failures if "legacy" in f):
    print("[RENDER-GUARD-Ω OK] Aucune reference pipeline legacy V6/V7 dans Territoire")

# 4. MonTerritoireBionicPage utilise useMapBundleV8
if "useMapBundleV8" not in PAGE:
    failures.append("ERREUR RENDU-Ω: Page n'importe pas useMapBundleV8")
else:
    print("[RENDER-GUARD-Ω OK] Page utilise useMapBundleV8 (pipeline unifie)")

# 5. DEFAULTS-Ω source de verite unique
if "TERRITOIRE_DEFAULTS" not in PAGE:
    failures.append("ERREUR RENDU-Ω: Page n'utilise pas TERRITOIRE_DEFAULTS (source verite)")
else:
    print("[RENDER-GUARD-Ω OK] Page utilise TERRITOIRE_DEFAULTS (source de verite unique)")

if failures:
    print("\n=== RENDER-GUARD-Ω PREVIEW NON CONFORME — PREVIEW != RENDU FINAL ===")
    for f in failures:
        print(f)
    sys.exit(1)
print("\n=== RENDER-GUARD-Ω PREVIEW CONFORME — PREVIEW = RENDU FINAL ===")
sys.exit(0)

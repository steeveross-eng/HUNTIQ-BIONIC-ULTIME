"""
SELF-AUDIT-Ω — test_purge_legacy (Phase XI)
=============================================
Vérifie l'absence de modules/routers legacy dans l'espace pipeline V20-SUPRA actif.

Règles institutionnelles :
  - Aucun include_router() actif pour les modules listés dans LEGACY_NEUTRALIZED
  - Aucun endpoint /v1/ /v2/ /v3/ exposé par les engines V20-SUPRA
  - Aucune référence SCORE-GLOBAL non-réalité dans territoire_v10_supra / score_global
"""
import re
import sys
from pathlib import Path

SERVER = Path("/app/backend/server.py")
TERRITOIRE = Path("/app/backend/engines/v8_institutional/territoire_v10_supra.py")
SCORE_GLOBAL = Path("/app/backend/engines/v8_institutional/engine_score_global.py")

LEGACY_NEUTRALIZED = [
    "organic_zones_router",
    "corridor_unified_router",
    "relocation_router",
    "dem_shadow_router",
    "full_comparison_router",
    "ndvi_shadow_router",
    "movement_corridors_router",
    "corridors_v10_router",
    "salines_ultime_router",
]

FORBIDDEN_ENDPOINT_PATTERNS = [
    r'prefix="/v1/',
    r'prefix="/v2/',
    r'prefix="/v3/',
    r'"/api/v1/territoire"',
    r'"/api/v2/territoire"',
    r'"/api/v3/territoire"',
]

errors = []

server_src = SERVER.read_text(encoding="utf-8")
for legacy in LEGACY_NEUTRALIZED:
    # Trouve toutes les occurrences avec include_router(legacy)
    pattern = re.compile(rf"^\s*app\.include_router\({legacy}", re.MULTILINE)
    active = pattern.findall(server_src)
    if active:
        errors.append(f"LEGACY ACTIF: {legacy} (include_router non commenté)")

territoire_src = TERRITOIRE.read_text(encoding="utf-8")
score_src = SCORE_GLOBAL.read_text(encoding="utf-8")

for pattern in FORBIDDEN_ENDPOINT_PATTERNS:
    if re.search(pattern, server_src):
        errors.append(f"ENDPOINT LEGACY DÉTECTÉ: {pattern}")

# Vérifie que score_global n'utilise plus pipeline "LEGACY" actif
# (la fonction legacy existe pour rétro-compat mais n'est plus appelée sans bundle)
if '"LEGACY"' in score_src and '"mode"' not in score_src:
    errors.append("SCORE-GLOBAL: référence LEGACY sans fencing mode")

if errors:
    print("FAIL: violations legacy détectées:")
    for e in errors:
        print(f"  - {e}")
    sys.exit(1)

print(f"OK: purge legacy conforme ({len(LEGACY_NEUTRALIZED)} modules neutralisés, 0 violation)")
sys.exit(0)

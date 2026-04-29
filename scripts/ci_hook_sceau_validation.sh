#!/usr/bin/env bash
# ═════════════════════════════════════════════════════════════════════
# ci_hook_sceau_validation.sh — BLOC 2 PHASE XIV
# COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU x3
#
# Hook de validation du SCEAU_PHASE_XIII_BIO_REACTEURS_Ω
# Exit 0 = ALLOW (sceau intact)
# Exit 1 = BLOCK (sceau corrompu) — déploiement BLOQUÉ
# ═════════════════════════════════════════════════════════════════════
set -euo pipefail

PYTHONPATH=/app/backend python3 - <<'PY'
import sys
sys.path.insert(0, "/app/backend")
from engines.v8_institutional.especes.sceau_phase_xiii_validator_omega import verify_sceau

result = verify_sceau()
verified = result.get("verified", False)
action = result.get("deployment_action", "BLOCK")
print("═══ CI HOOK · SCEAU_PHASE_XIII_BIO_REACTEURS_Ω ═══")
print(f"  doctrine       : {result.get('doctrine')}")
print(f"  phase          : {result.get('phase')}")
print(f"  checked_at_utc : {result.get('checked_at_utc')}")
print(f"  live SHA       : {result.get('live_sha_cumulatif')}")
print(f"  ref  SHA       : {result.get('reference_sha_cumulatif')}")
print(f"  verified       : {verified}")
print(f"  action         : {action}")
if not verified:
    print("\n✗ SCEAU CORROMPU — DÉPLOIEMENT BLOQUÉ")
    sys.exit(1)
print("\n✓ SCEAU INTACT — DÉPLOIEMENT AUTORISÉ")
sys.exit(0)
PY

#!/usr/bin/env bash
# panic_stop_xvb_omega.sh — PHASE XV.b Pre-flight check
# COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU x3 · ORDRE N°30
#
# Doit être exécuté AVANT toute opération XV.b.
# Exit 0 = XV.b authorized · Exit 1 = PANIC_STOP_Ω (XV.b denied)
set -euo pipefail

PYTHONPATH=/app/backend python3 <<'PYEOF'
import json, sys
with open("/app/frontend/public/reports/audit_master_omega/PROTECTIONS_MAXIMALES_Ω.json") as f:
    m = json.load(f)
auth = m.get("xvb_authorization")
panic = m["blocs"]["BLOC_3_MODE_PANIC_STOP_Ω"]["panic_stop_active"]
all_pass = m.get("all_blocs_passed")
gen_at = m.get("generated_at_utc")
print("═══ PHASE_XV.b PRE-FLIGHT CHECK · BCE-4X ULTIME ABSOLU x3 ═══")
print(f"  xvb_authorization  : {auth}")
print(f"  panic_stop_active  : {panic}")
print(f"  all_blocs_passed   : {all_pass}")
print(f"  generated_at_utc   : {gen_at}")
if auth != "GRANTED" or panic or not all_pass:
    print("\n✗ PANIC_STOP_Ω · XV.b DÉNIÉ")
    sys.exit(1)
print("\n✓ XV.b AUTORISÉ · vous pouvez procéder")
sys.exit(0)
PYEOF

#!/usr/bin/env bash
# panic_stop_xvb_omega.sh — PHASE XV.b Pre-flight check (Combiné)
# COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU x3 · ORDRES N°30 + N°31
#
# 1) Vérifie l'autorisation PROTECTIONS_MAXIMALES_Ω
# 2) Vérifie l'intégrité FREEZE_PRE_XVb_Ω
# Exit 0 = XV.b authorized · Exit 1 = PANIC_STOP_Ω
set -euo pipefail

echo "═══ PHASE_XV.b PANIC_STOP — DOUBLE VERIFICATION ═══"
echo ""
echo "── Étape 1/2 : PROTECTIONS_MAXIMALES_Ω (Ordre n°30) ──"
PYTHONPATH=/app/backend python3 <<'PYEOF1'
import json, sys
with open("/app/frontend/public/reports/audit_master_omega/PROTECTIONS_MAXIMALES_Ω.json") as f:
    m = json.load(f)
auth = m.get("xvb_authorization")
panic = m["blocs"]["BLOC_3_MODE_PANIC_STOP_Ω"]["panic_stop_active"]
all_pass = m.get("all_blocs_passed")
gen_at = m.get("generated_at_utc")
print(f"  xvb_authorization  : {auth}")
print(f"  panic_stop_active  : {panic}")
print(f"  all_blocs_passed   : {all_pass}")
print(f"  generated_at_utc   : {gen_at}")
if auth != "GRANTED" or panic or not all_pass:
    print("✗ PROTECTIONS_MAXIMALES_Ω · DENIED")
    sys.exit(1)
print("✓ PROTECTIONS_MAXIMALES_Ω · OK")
PYEOF1

echo ""
echo "── Étape 2/2 : FREEZE_PRE_XVb_Ω (Ordre n°31) ──"
bash /app/scripts/verify_freeze_pre_xvb_omega.sh

echo ""
echo "═══ ✓ PANIC_STOP CHECK COMPLET — XV.b AUTORISÉ ═══"
exit 0

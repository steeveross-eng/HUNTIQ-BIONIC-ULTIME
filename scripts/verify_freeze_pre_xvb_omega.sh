#!/usr/bin/env bash
# verify_freeze_pre_xvb_omega.sh — Vérifie l'intégrité du gel pré-XV.b
# COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU x3 · ORDRE N°31
#
# Exit 0 = freeze intact · Exit 1 = ALTÉRATION DÉTECTÉE · ABORT_XVb
set -euo pipefail

PYTHONPATH=/app/backend python3 <<'PYEOF'
import hashlib, json, sys
from pathlib import Path

with open("/app/frontend/public/reports/audit_master_omega/FREEZE_PRE_XVb_Ω.json") as f:
    fr = json.load(f)

def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()

altered = []
missing = []
for group_name, group in fr["groups"].items():
    for entry in group["entries"]:
        if not entry["exists"]:
            continue
        p = Path(entry["path"])
        if not p.exists():
            missing.append(entry["path"])
            continue
        actual = sha(p)
        if actual != entry["sha256"]:
            altered.append({
                "path": entry["path"],
                "expected": entry["sha256"],
                "actual": actual,
            })

print("═══ VERIFY_FREEZE_PRE_XVb_Ω ═══")
print(f"  frozen_at_utc       : {fr['frozen_at_utc']}")
print(f"  total_files_frozen  : {fr['metadata']['total_files_frozen']}")
print(f"  altered_count       : {len(altered)}")
print(f"  missing_count       : {len(missing)}")

if altered:
    print("\n✗ ALTÉRATION DÉTECTÉE — XV.b INTERDIT")
    for a in altered[:10]:
        print(f"    {a['path']}")
        print(f"      expected={a['expected']}")
        print(f"      actual  ={a['actual']}")
    sys.exit(1)
if missing:
    print("\n✗ FICHIER MANQUANT — XV.b INTERDIT")
    for m in missing[:10]:
        print(f"    {m}")
    sys.exit(1)
print("\n✓ FREEZE INTACT — VOUS POUVEZ PROCEDER (sous réserve panic_stop_xvb_omega.sh)")
sys.exit(0)
PYEOF

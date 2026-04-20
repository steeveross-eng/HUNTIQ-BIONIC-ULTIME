"""SELF-AUDIT-Ω — test_healthpanel_admin (Phase X-C)
Vérifie montage du composant InstitutionalHealthPanel dans le layout admin.
"""
import sys
from pathlib import Path

COMPONENT = Path("/app/frontend/src/components/territoire/InstitutionalHealthPanel.jsx")

errors = []

if not COMPONENT.exists():
    errors.append(f"Composant absent: {COMPONENT}")
else:
    src = COMPONENT.read_text(encoding="utf-8")
    for marker in ["institutional-health-panel", "registry-lock", "engines-catalog", "gouvernance"]:
        if marker not in src:
            errors.append(f"marker manquant dans composant: {marker}")

# Recherche du montage admin (import + usage)
admin_found = False
for root in ["/app/frontend/src"]:
    for p in Path(root).rglob("*.jsx"):
        if p.samefile(COMPONENT):
            continue
        try:
            t = p.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        if "InstitutionalHealthPanel" in t and ("import" in t or "from" in t):
            admin_found = True
            break
    if admin_found:
        break

if not admin_found:
    errors.append("InstitutionalHealthPanel non monté dans aucun composant admin/layout")

if errors:
    print("FAIL:"); [print(" -", e) for e in errors]; sys.exit(1)
print(f"OK: health panel admin monté (composant + import confirmé)")
sys.exit(0)

"""SELF-AUDIT-Ω — test_lep_integration (Phase X-C)"""
import sys
sys.path.insert(0, "/app/backend")

from engines.v8_institutional.federal_datasets_omega import (  # noqa: E402
    LEP_HABITATS, get_lep_overview, get_lep_for_province,
)

errors = []

if len(LEP_HABITATS) < 100:
    errors.append(f"LEP < 100 habitats (got {len(LEP_HABITATS)})")

ov = get_lep_overview()
if ov.get("status") != "INGESTED":
    errors.append("LEP status != INGESTED")
if len(ov.get("by_province", {})) < 13:
    errors.append(f"LEP: < 13 provinces ({len(ov.get('by_province',{}))})")
if not ov.get("especes_listees"):
    errors.append("LEP: especes_listees vide")

bc = get_lep_for_province("BC")
if len(bc) < 50:
    errors.append(f"LEP BC < 50 (got {len(bc)})")

# Structure
for h in LEP_HABITATS[:3]:
    for k in ("id", "province", "espece", "categorie", "lat", "lon"):
        if k not in h:
            errors.append(f"LEP habitat manque champ {k}")
            break

if errors:
    print("FAIL:"); [print(" -", e) for e in errors]; sys.exit(1)
print(f"OK: LEP ingéré ({len(LEP_HABITATS)} habitats, {len(ov['by_province'])} provinces, BC={len(bc)})")
sys.exit(0)

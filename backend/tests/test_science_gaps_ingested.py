"""SELF-AUDIT-Ω — test_science_gaps_ingested (Phase X)"""
import sys
sys.path.insert(0, "/app/backend")

from engines.v8_institutional.science_gaps_datasets import (  # noqa: E402
    get_all_gaps, MFFP_FORESTIER, IRDA_CA_NA, CWD_HEATMAP, MFFP_PRESSION_CHASSE,
)

errors = []
data = get_all_gaps()

if data["gaps_ingested"] != 4:
    errors.append(f"gaps_ingested != 4 (got {data['gaps_ingested']})")

for key, ds in [("mffp_forestier", MFFP_FORESTIER), ("irda_ca_na", IRDA_CA_NA),
                 ("cwd_heatmap", CWD_HEATMAP), ("mffp_pression_chasse", MFFP_PRESSION_CHASSE)]:
    if ds.get("status") != "INGESTED":
        errors.append(f"{key}: status != INGESTED")
    if not ds.get("source"):
        errors.append(f"{key}: source manquante")

# Coverage regions
if len(MFFP_FORESTIER["regions"]) < 5:
    errors.append(f"MFFP_FORESTIER: <5 régions ({len(MFFP_FORESTIER['regions'])})")
if len(IRDA_CA_NA["mrc"]) < 3:
    errors.append(f"IRDA: <3 MRC")
if len(CWD_HEATMAP["zones"]) < 2:
    errors.append(f"CWD: <2 zones")
if len(MFFP_PRESSION_CHASSE["regions"]) < 5:
    errors.append(f"MFFP_PRESSION: <5 régions")

if errors:
    print("FAIL:"); [print(" -", e) for e in errors]; sys.exit(1)
print(f"OK: 4 gaps ingérés (MFFP forestier {len(MFFP_FORESTIER['regions'])} régions, IRDA {len(IRDA_CA_NA['mrc'])} MRC, CWD {len(CWD_HEATMAP['zones'])} zones, pression {len(MFFP_PRESSION_CHASSE['regions'])} régions)")
sys.exit(0)

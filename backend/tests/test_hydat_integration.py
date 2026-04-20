"""SELF-AUDIT-Ω — test_hydat_integration (Phase X-C)"""
import sys
sys.path.insert(0, "/app/backend")

from engines.v8_institutional.federal_datasets_omega import (  # noqa: E402
    HYDAT_STATIONS, get_hydat_overview, get_hydat_for_province,
)
from engines.v8_institutional.engine_risques_hydro_omega import compute_risques_hydro  # noqa: E402

errors = []

if len(HYDAT_STATIONS) < 200:
    errors.append(f"HYDAT < 200 stations ({len(HYDAT_STATIONS)})")

ov = get_hydat_overview()
if ov.get("status") != "INGESTED":
    errors.append("HYDAT status != INGESTED")
if len(ov.get("by_province", {})) < 13:
    errors.append(f"HYDAT: < 13 provinces")

bc = get_hydat_for_province("BC", limit=100)
if len(bc) < 50:
    errors.append(f"HYDAT BC < 50 (got {len(bc)})")

# ENGINE-RISQUES-HYDRO-Ω
r = compute_risques_hydro()
if r["stations_total"] != len(HYDAT_STATIONS):
    errors.append(f"risques-hydro total mismatch")
if "risque_inondation" not in r or "risque_etiage" not in r or "risque_qualite_eau" not in r:
    errors.append("risques-hydro: métriques manquantes")

# Structure station
for s in HYDAT_STATIONS[:3]:
    for k in ("station_id", "province", "lat", "lon", "debit_m3s", "niveau_m", "qualite_classe"):
        if k not in s:
            errors.append(f"HYDAT station manque champ {k}")
            break

if errors:
    print("FAIL:"); [print(" -", e) for e in errors]; sys.exit(1)
print(f"OK: HYDAT ingéré ({len(HYDAT_STATIONS)} stations) + RISQUES-HYDRO (inond={r['risque_inondation']['pct']}%, etiage={r['risque_etiage']['pct']}%)")
sys.exit(0)

"""SELF-AUDIT-Ω — test_ia_corridors_omega (Phase XI-SUPRA-H)

Vérifie ENGINE CORRIDORS VERSION Ω / IA-CORRIDORS :
  - Engine enregistré
  - CONSTRAINTS officielles (segment_max_m=20, angle_max_deg=45, rayon 420-780)
  - Validation d'un corridor conforme → ok
  - Validation d'un corridor non-conforme (segment > 20m) → violation détectée
  - Validation d'un corridor avec angle > 45° → violation détectée
  - Validation d'un corridor avec référence 'affut' → violation détectée
  - Validate-live sur le bundle courant : TOUS les corridors doivent passer
"""
import asyncio
import sys

sys.path.insert(0, "/app/backend")

from engines.v8_institutional import engine_ia_corridors_omega as iac  # noqa: E402,F401
from engines.v8_institutional.engine_science_omega import get_catalog  # noqa: E402

errors = []

# 1. Engine in catalog
cat = get_catalog()
cat_list = cat if isinstance(cat, list) else cat.get("engines", [])
names = [e.get("name") if isinstance(e, dict) else str(e) for e in cat_list]
if "ENGINE-IA-CORRIDORS-Ω" not in names:
    errors.append(f"engine absent catalog: sample={names[:5]}")

# 2. CONSTRAINTS officielles
expected = {
    "segment_max_m": 20.0,
    "angle_max_deg": 45.0,
    "functional_radius_min_m": 420.0,
    "functional_radius_max_m": 780.0,
}
for k, v in expected.items():
    if iac.CONSTRAINTS.get(k) != v:
        errors.append(f"CONSTRAINTS[{k}] = {iac.CONSTRAINTS.get(k)} ≠ {v}")

# 3. Corridor conforme : polyline Catmull-Rom serpentine 500m
import math
lat0, lon0 = 45.10, -72.80
path = []
R = 500 / 111000.0  # 500m en degrés
for i in range(60):
    t = i / 59
    # courbe sinusoïdale fluide
    lat = lat0 + R * t * math.cos(math.radians(45))
    lon = lon0 + R * t * math.sin(math.radians(45)) + 0.00005 * math.sin(t * 6.28)
    path.append([round(lat, 6), round(lon, 6)])
good = {
    "id": "corr_good",
    "species_profile": "chevreuil",
    "path": path,
}
res_good = iac.validate_corridors([good], {"lat": lat0, "lon": lon0})
if not res_good["ok"]:
    errors.append(f"conforming rejected: {res_good['per_corridor']}")

# 4. Corridor avec segment > 20m
path_bad = [[lat0, lon0], [lat0 + 0.001, lon0 + 0.001], [lat0 + 0.005, lon0 + 0.005],
            [lat0 + 0.006, lon0 + 0.006], [lat0 + 0.007, lon0 + 0.007]]
bad_seg = {"id": "cbad", "species_profile": "chevreuil", "path": path_bad}
res_bs = iac.validate_corridors([bad_seg], {"lat": lat0, "lon": lon0})
if res_bs["ok"]:
    errors.append("corridor segment>20m accepté à tort")

# 5. Corridor avec angle > 45° (zigzag brutal)
path_zig = []
for i in range(10):
    t = i / 9
    lat = lat0 + 0.001 * t
    lon = lon0 + 0.001 * t + (0.0003 if i % 2 else -0.0003)
    path_zig.append([round(lat, 6), round(lon, 6)])
bad_ang = {"id": "cang", "species_profile": "chevreuil", "path": path_zig}
res_ba = iac.validate_corridors([bad_ang], {"lat": lat0, "lon": lon0})
if res_ba["ok"]:
    errors.append("corridor angle>45° accepté à tort")

# 6. Corridor avec référence affut
bad_affut = {
    "id": "c_af", "species_profile": "cerf", "path": path,
    "linked_affut": "affut_123",  # référence interdite
}
res_af = iac.validate_corridors([bad_affut], {"lat": lat0, "lon": lon0})
if res_af["ok"]:
    errors.append("corridor avec ref affut accepté à tort")

# 7. Validate-live contre le bundle réel
async def live_check():
    from engines.v8_institutional.territoire_v10_supra import compute_territoire_v10
    bundle = await compute_territoire_v10(45.10, -72.80, "chevreuil",
                                          month=10, hour=7, wind_deg=225, wind_speed=15)
    return iac.validate_corridors(bundle.get("corridors", []), {"lat": 45.10, "lon": -72.80})

live = asyncio.run(live_check())
if not live["ok"]:
    fails_summary = []
    for r in live["per_corridor"]:
        if not r["ok"]:
            rules = [v["rule"] for v in r["violations"]]
            fails_summary.append(f"{r['metrics'].get('id')}:{rules}")
    errors.append(f"bundle live: {live['corridors_failed']}/{live['corridors_total']} corridors fail "
                  f"{fails_summary[:3]}")

if errors:
    print("FAIL:")
    for e in errors:
        print(" -", e)
    sys.exit(1)
print(f"OK: ENGINE-IA-CORRIDORS-Ω — {len(iac.CONSTRAINTS)} contraintes, "
      f"validations positive/négative discriminées, bundle live conforme")
sys.exit(0)

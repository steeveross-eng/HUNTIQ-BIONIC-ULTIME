#!/bin/bash
# P22Ω_CORRIDORS_ZONES_STABILISATION
# Flags: --lock-v30 --flush-lru --rehydrate-cache --validate-corridors --validate-zones --no-fallback --force-hit --finalize
# COMMANDANT STEEVE-MAX · 2026-05-13
set -u
API=$(grep REACT_APP_BACKEND_URL /app/frontend/.env | cut -d= -f2)
echo "═══════════════════════════════════════════════════════════════════════"
echo "P22Ω_CORRIDORS_ZONES_STABILISATION — DÉMARRAGE"
echo "API=$API"
echo "WAYPOINT BSL=(48.206657,-68.382422)  SPECIES=chevreuil"
echo "═══════════════════════════════════════════════════════════════════════"

LAT=48.206657
LON=-68.382422
SPECIES=chevreuil
MONTH=10
HOUR=7
WIND_DEG=225
WIND_SPEED=15

# ═══ [1/8] --lock-v30 : Vérification verrou V30 ═══
echo ""
echo "▶ [1/8] --lock-v30 (vérification doctrine V30 scellée)"
SMOOTHER_STATUS=$(curl -s "$API/api/v20/territoire/corridors-organic/smoother-status")
V30_LOCK=$(echo "$SMOOTHER_STATUS" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('engine_v30_locked'))")
NON_REGR=$(echo "$SMOOTHER_STATUS" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('non_regression_guaranteed'))")
echo "    engine_v30_locked        = $V30_LOCK"
echo "    non_regression_guaranteed = $NON_REGR"

# ═══ [2/8] --flush-lru : Purge bundle + smoother ═══
echo ""
echo "▶ [2/8] --flush-lru (purge LRU bundle + smoother)"
PURGE_BUNDLE=$(curl -s -X POST "$API/api/v20/territoire/bundle/purge")
PURGE_SMOOTHER=$(curl -s -X POST "$API/api/v20/territoire/corridors-organic/purge")
echo "    bundle.purge   = $PURGE_BUNDLE"
echo "    smoother.purge = $PURGE_SMOOTHER"

# ═══ [3/8] --rehydrate-cache : Calcul MISS BSL/Chevreuil ═══
echo ""
echo "▶ [3/8] --rehydrate-cache (premier appel = MISS, calcul complet)"
T0=$(date +%s.%N)
BUNDLE_MISS=$(curl -s "$API/api/v20/territoire/bundle?lat=$LAT&lon=$LON&species=$SPECIES&month=$MONTH&hour=$HOUR&wind_deg=$WIND_DEG&wind_speed=$WIND_SPEED")
T1=$(date +%s.%N)
ELAPSED_MISS=$(python3 -c "print(f'{$T1 - $T0:.2f}')")
echo "    bundle MISS rehydraté en ${ELAPSED_MISS}s"

# Extraction métriques MISS
echo "$BUNDLE_MISS" > /tmp/bundle_miss.json
CACHE_MISS=$(python3 -c "import json; d=json.load(open('/tmp/bundle_miss.json')); print(d.get('cache'))")
N_CORRIDORS_MISS=$(python3 -c "import json; d=json.load(open('/tmp/bundle_miss.json')); print(len(d.get('corridors',[])))")
echo "    cache       = $CACHE_MISS"
echo "    corridors   = $N_CORRIDORS_MISS"

# Smoother POST direct
T0=$(date +%s.%N)
SMOOTHER_MISS=$(curl -s -X POST "$API/api/v20/territoire/corridors-organic/generate" \
    -H "Content-Type: application/json" \
    -d "{\"lat\":$LAT,\"lon\":$LON,\"species\":\"$SPECIES\",\"month\":$MONTH,\"hour\":$HOUR,\"wind_deg\":$WIND_DEG,\"wind_speed\":$WIND_SPEED,\"anchor_mode\":\"TERRITORY_CONTINUOUS\"}")
T1=$(date +%s.%N)
ELAPSED_SM_MISS=$(python3 -c "print(f'{$T1 - $T0:.2f}')")
echo "    smoother MISS rehydraté en ${ELAPSED_SM_MISS}s"
echo "$SMOOTHER_MISS" > /tmp/smoother_miss.json

# ═══ [4/8] --validate-corridors ═══
echo ""
echo "▶ [4/8] --validate-corridors"
python3 <<EOF
import json
d = json.load(open('/tmp/bundle_miss.json'))
corridors = d.get('corridors', [])
hier = {}
for c in corridors:
    h = c.get('hierarchy') or c.get('subnet_role') or 'unknown'
    hier[h] = hier.get(h, 0) + 1
print(f"    n_corridors      = {len(corridors)}")
print(f"    hierarchy        = {hier}")
v5 = d.get('p22sigma_v5_bundle_rewire', {})
print(f"    v5_rewire_applied = {v5.get('applied')}")
print(f"    v5_hierarchy      = {v5.get('hierarchy_counts')}")
print(f"    v5_engine         = {v5.get('engine')}")
print(f"    cap_doctrine      = {v5.get('cap_global_doctrine')}")
EOF

# ═══ [5/8] --validate-zones ═══
echo ""
echo "▶ [5/8] --validate-zones"
python3 <<EOF
import json
d = json.load(open('/tmp/bundle_miss.json'))
zones = d.get('zones', [])
ztypes = {}
for z in zones:
    t = z.get('type') or z.get('kind') or 'unknown'
    ztypes[t] = ztypes.get(t, 0) + 1
print(f"    n_zones      = {len(zones)}")
print(f"    types        = {ztypes}")
print(f"    n_affuts     = {len(d.get('affuts',[]))}")
print(f"    n_hotspots   = {len(d.get('hotspots',[]))}")
print(f"    n_salines    = {len(d.get('salines',[]))}")
print(f"    esi_omega    = {d.get('esi_omega')}")
EOF

# ═══ [6/8] --no-fallback ═══
echo ""
echo "▶ [6/8] --no-fallback (vérifie absence fallback V10_SUPRA_LEGACY)"
python3 <<EOF
import json
d = json.load(open('/tmp/bundle_miss.json'))
v5 = d.get('p22sigma_v5_bundle_rewire', {})
applied = v5.get('applied') is True
fallback = v5.get('fallback')
if applied and not fallback:
    print(f"    ✓ V5 REWIRE ACTIF — pas de fallback V10")
    print(f"    status = NO_FALLBACK_OK")
else:
    print(f"    ✗ V5 NON ACTIF — fallback détecté: {fallback}")
    print(f"    status = FALLBACK_DETECTED")
EOF

# ═══ [7/8] --force-hit ═══
echo ""
echo "▶ [7/8] --force-hit (re-query, doit retourner cache=HIT)"
T0=$(date +%s.%N)
BUNDLE_HIT=$(curl -s "$API/api/v20/territoire/bundle?lat=$LAT&lon=$LON&species=$SPECIES&month=$MONTH&hour=$HOUR&wind_deg=$WIND_DEG&wind_speed=$WIND_SPEED")
T1=$(date +%s.%N)
ELAPSED_HIT=$(python3 -c "print(f'{($T1 - $T0)*1000:.1f}')")
echo "    bundle re-query en ${ELAPSED_HIT}ms"
echo "$BUNDLE_HIT" > /tmp/bundle_hit.json
python3 <<EOF
import json
d = json.load(open('/tmp/bundle_hit.json'))
print(f"    cache         = {d.get('cache')}")
print(f"    cache_age_sec = {d.get('cache_age_sec')}")
print(f"    served_ms     = {d.get('served_ms')}")
print(f"    n_corridors   = {len(d.get('corridors',[]))}")
EOF

# Smoother HIT
T0=$(date +%s.%N)
SMOOTHER_HIT=$(curl -s -X POST "$API/api/v20/territoire/corridors-organic/generate" \
    -H "Content-Type: application/json" \
    -d "{\"lat\":$LAT,\"lon\":$LON,\"species\":\"$SPECIES\",\"month\":$MONTH,\"hour\":$HOUR,\"wind_deg\":$WIND_DEG,\"wind_speed\":$WIND_SPEED,\"anchor_mode\":\"TERRITORY_CONTINUOUS\"}")
T1=$(date +%s.%N)
ELAPSED_SM_HIT=$(python3 -c "print(f'{($T1 - $T0)*1000:.1f}')")
echo "    smoother re-query en ${ELAPSED_SM_HIT}ms"
echo "$SMOOTHER_HIT" > /tmp/smoother_hit.json
python3 <<EOF
import json
d = json.load(open('/tmp/smoother_hit.json'))
print(f"    smoother.cache       = {d.get('cache')}")
print(f"    smoother.n_corridors = {len(d.get('corridors',[]))}")
EOF

# ═══ [8/8] --finalize ═══
echo ""
echo "▶ [8/8] --finalize (statistiques globales)"
STATS_BUNDLE=$(curl -s "$API/api/v20/territoire/bundle/stats")
STATS_SMOOTHER=$(curl -s "$API/api/v20/territoire/corridors-organic/cache-stats")
echo "$STATS_BUNDLE" > /tmp/stats_bundle.json
echo "$STATS_SMOOTHER" > /tmp/stats_smoother.json
python3 <<EOF
import json
sb = json.load(open('/tmp/stats_bundle.json'))
ss = json.load(open('/tmp/stats_smoother.json'))
print(f"    bundle.size       = {sb.get('cache_size')}/{sb.get('cache_max')}")
print(f"    bundle.hits       = {sb.get('hits')}")
print(f"    bundle.misses     = {sb.get('misses')}")
print(f"    bundle.hit_ratio  = {sb.get('hit_ratio_pct')}%")
print(f"    smoother.size     = {ss.get('size')}/{ss.get('max')}")
print(f"    smoother.ttl_sec  = {ss.get('ttl_sec')}")
EOF

echo ""
echo "═══════════════════════════════════════════════════════════════════════"
echo "P22Ω_CORRIDORS_ZONES_STABILISATION — TERMINÉ"
echo "═══════════════════════════════════════════════════════════════════════"

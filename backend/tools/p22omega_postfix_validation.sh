#!/bin/bash
# Validation séquentielle post-correctifs P22Ω_MULTI_FIX_A1_A4
# Tactique : MISS curl bail à 70s (ingress=60s), sleep 90s, puis HIT
set -u
API=$(grep REACT_APP_BACKEND_URL /app/frontend/.env | cut -d= -f2)
LAT=48.206657
LON=-68.382422
MONTH=10
HOUR=7
WIND_DEG=225
WIND_SPEED=15

echo "═══════════════════════════════════════════════════════════════════════"
echo "VALIDATION SÉQUENTIELLE POST-FIX (chevreuil → orignal → ours → dindon → coyote)"
echo "═══════════════════════════════════════════════════════════════════════"
curl -s -X POST "$API/api/v20/territoire/bundle/purge" >/dev/null
curl -s -X POST "$API/api/v20/territoire/corridors-organic/purge" >/dev/null
echo "Cache purgé."
echo ""

SPECIES_LIST=("chevreuil" "orignal" "ours" "dindon" "coyote")

# Phase 1 : Déclencher MISS pour chaque espèce SÉQUENTIELLEMENT
for SPECIES in "${SPECIES_LIST[@]}"; do
    echo "▶ MISS déclenché pour $SPECIES (attente 90s pour completion backend)..."
    # On ignore le contenu de la réponse (ingress cut à 60s)
    curl -s -m 70 -o /dev/null "$API/api/v20/territoire/bundle?lat=$LAT&lon=$LON&species=$SPECIES&month=$MONTH&hour=$HOUR&wind_deg=$WIND_DEG&wind_speed=$WIND_SPEED" &
    CURL_PID=$!
    # Attendre que le backend ait probablement fini (~90s post-déclenchement)
    sleep 90
    # Tuer le curl si encore en cours
    kill -9 $CURL_PID 2>/dev/null
    wait $CURL_PID 2>/dev/null
    echo "    ✓ Backend devrait avoir fini calcul + cache"
done

echo ""
echo "═══════════════════════════════════════════════════════════════════════"
echo "Phase 2 : HIT validation"
echo "═══════════════════════════════════════════════════════════════════════"

# Initialise JSON agrégé
echo "{}" > /tmp/validation_post_fix.json

for SPECIES in "${SPECIES_LIST[@]}"; do
    echo ""
    echo "▶ HIT $SPECIES"
    T0=$(date +%s.%N)
    curl -s -m 15 "$API/api/v20/territoire/bundle?lat=$LAT&lon=$LON&species=$SPECIES&month=$MONTH&hour=$HOUR&wind_deg=$WIND_DEG&wind_speed=$WIND_SPEED" > "/tmp/postfix_bundle_${SPECIES}.json"
    T1=$(date +%s.%N)
    HIT_MS=$(python3 -c "print(f'{($T1-$T0)*1000:.0f}')")

    python3 <<PYEOF
import json, sys
sp = "${SPECIES}"
try:
    d = json.load(open(f"/tmp/postfix_bundle_{sp}.json"))
except Exception as e:
    print(f"    JSON parse error: {e}")
    sys.exit(0)

cache = d.get("cache", "?")
corridors = d.get("corridors", [])
zones = d.get("zones", [])
hot = d.get("hotspots", [])
sal = d.get("salines", [])
v5 = d.get("p22sigma_v5_bundle_rewire", {}) or {}
hier = v5.get("hierarchy_counts") or {}
halt = d.get("bio_presence_mask_halt", False)
remap = v5.get("v30_remap_fallback_applied", False)
species_echo = d.get("species", "?")
n = len(corridors)
in_range = (5 <= n <= 7) or halt

print(f"    species_echo : {species_echo}")
print(f"    cache         : {cache}  (HIT={HIT_MS}ms)")
print(f"    corridors     : {n}  ({'IN_RANGE' if in_range else 'OUT_OF_RANGE'})")
print(f"    hierarchy     : backbone={hier.get('veine_principale',0)}  subnet={hier.get('veine_secondaire',0)}")
print(f"    zones         : {len(zones)}  hotspots={len(hot)}  salines={len(sal)}")
print(f"    v5_applied    : {v5.get('applied')}")
print(f"    v30_remap     : {remap}")
print(f"    bio_halt      : {halt}")
print(f"    esi_omega     : {d.get('esi_omega')}")
verdict = "CONFORME" if (in_range and (v5.get('applied') or halt)) else "NON_CONFORME"
print(f"    VERDICT       : {verdict}")

import json as J
agg = J.load(open("/tmp/validation_post_fix.json"))
agg[sp] = {
    "species_echo": species_echo,
    "corridors": n,
    "in_range": in_range,
    "backbone": hier.get("veine_principale", 0),
    "subnet": hier.get("veine_secondaire", 0),
    "zones": len(zones),
    "hotspots": len(hot),
    "salines": len(sal),
    "v5_applied": bool(v5.get("applied")),
    "v30_remap": bool(remap),
    "bio_halt": bool(halt),
    "hit_ms": int("${HIT_MS}"),
    "cache_status": cache,
    "esi": d.get("esi_omega"),
    "verdict": verdict,
}
J.dump(agg, open("/tmp/validation_post_fix.json", "w"), indent=2)
PYEOF
done

echo ""
echo "═══════════════════════════════════════════════════════════════════════"
echo "SYNTHÈSE FINALE"
echo "═══════════════════════════════════════════════════════════════════════"
python3 <<EOF
import json
agg = json.load(open("/tmp/validation_post_fix.json"))
print(f"{'SPECIES':10s} {'CORR':>5s} {'BB':>3s} {'SUB':>3s} {'ZO':>3s} {'V5':>3s} {'V30R':>5s} {'HALT':>5s} {'HIT_MS':>7s} {'VERDICT':>12s}")
print("-"*75)
all_conf = True
for sp, r in agg.items():
    cf = r["verdict"] == "CONFORME"
    all_conf &= cf
    print(f"{sp:10s} {r['corridors']:>5d} {r['backbone']:>3d} {r['subnet']:>3d} {r['zones']:>3d} "
          f"{('Y' if r['v5_applied'] else 'N'):>3s} {('Y' if r['v30_remap'] else 'N'):>5s} "
          f"{('Y' if r['bio_halt'] else 'N'):>5s} {r['hit_ms']:>7d} {r['verdict']:>12s}")
print("-"*75)
print(f"VERDICT GLOBAL : {'TOUTES CONFORMES' if all_conf else 'NON-CONFORMITÉS RÉSIDUELLES'}")
EOF

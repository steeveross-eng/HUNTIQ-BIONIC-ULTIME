#!/bin/bash
# P22Ω_TERRITOIRE_VALIDATION_MULTI_ESPECES_X1000
# Flags: --validate-chevreuil --validate-orignal --validate-ours --validate-dindon --validate-coyote
#        --exclude-wapiti --confirm-visual --finalize
# COMMANDANT STEEVE-MAX · 2026-05-13
set -u
API=$(grep REACT_APP_BACKEND_URL /app/frontend/.env | cut -d= -f2)
LAT=48.206657
LON=-68.382422
MONTH=10
HOUR=7
WIND_DEG=225
WIND_SPEED=15

echo "═══════════════════════════════════════════════════════════════════════"
echo "P22Ω_TERRITOIRE_VALIDATION_MULTI_ESPECES_X1000"
echo "API=$API"
echo "WAYPOINT BSL=($LAT,$LON)  MONTH=$MONTH HOUR=$HOUR"
echo "EXCLUDED: wapiti"
echo "═══════════════════════════════════════════════════════════════════════"

# Purge avant pour MISS contrôlé sur toutes les espèces
echo ""
echo "▶ PRÉPARATION : purge LRU bundle + smoother"
curl -s -X POST "$API/api/v20/territoire/bundle/purge" >/dev/null
curl -s -X POST "$API/api/v20/territoire/corridors-organic/purge" >/dev/null
echo "    Purgé."

SPECIES_LIST=("chevreuil" "orignal" "ours" "dindon" "coyote")

# Initialisation du JSON agrégé
echo "{}" > /tmp/multi_species_results.json

for SPECIES in "${SPECIES_LIST[@]}"; do
    echo ""
    echo "═══════════════════════════════════════════════════════════════════════"
    echo "▶ VALIDATION ESPÈCE : $SPECIES"
    echo "═══════════════════════════════════════════════════════════════════════"

    # ═══ Pass 1 : MISS (calcul complet) ═══
    T0=$(date +%s.%N)
    curl -s -m 90 "$API/api/v20/territoire/bundle?lat=$LAT&lon=$LON&species=$SPECIES&month=$MONTH&hour=$HOUR&wind_deg=$WIND_DEG&wind_speed=$WIND_SPEED" \
        > "/tmp/bundle_${SPECIES}.json"
    T1=$(date +%s.%N)
    MISS_S=$(python3 -c "print(f'{$T1-$T0:.2f}')")
    echo "    MISS bundle = ${MISS_S}s"

    # ═══ Pass 2 : HIT (re-query) ═══
    T0=$(date +%s.%N)
    curl -s -m 30 -o "/tmp/bundle_${SPECIES}_hit.json" \
        "$API/api/v20/territoire/bundle?lat=$LAT&lon=$LON&species=$SPECIES&month=$MONTH&hour=$HOUR&wind_deg=$WIND_DEG&wind_speed=$WIND_SPEED"
    T1=$(date +%s.%N)
    HIT_MS=$(python3 -c "print(f'{($T1-$T0)*1000:.1f}')")
    echo "    HIT bundle  = ${HIT_MS}ms"

    # ═══ Smoother direct ═══
    T0=$(date +%s.%N)
    curl -s -m 60 -X POST "$API/api/v20/territoire/corridors-organic/generate" \
        -H "Content-Type: application/json" \
        -d "{\"lat\":$LAT,\"lon\":$LON,\"species\":\"$SPECIES\",\"month\":$MONTH,\"hour\":$HOUR,\"wind_deg\":$WIND_DEG,\"wind_speed\":$WIND_SPEED,\"anchor_mode\":\"TERRITORY_CONTINUOUS\"}" \
        > "/tmp/smoother_${SPECIES}.json"
    T1=$(date +%s.%N)
    SM_S=$(python3 -c "print(f'{$T1-$T0:.2f}')")
    echo "    smoother    = ${SM_S}s"

    # ═══ Analyse JSON ═══
    python3 <<PYEOF
import json
sp = "${SPECIES}"
miss = json.load(open(f"/tmp/bundle_{sp}.json"))
hit  = json.load(open(f"/tmp/bundle_{sp}_hit.json"))
sm   = json.load(open(f"/tmp/smoother_{sp}.json"))

# Bundle MISS
corridors = miss.get("corridors", [])
zones     = miss.get("zones", [])
hotspots  = miss.get("hotspots", [])
salines   = miss.get("salines", [])
affuts    = miss.get("affuts", [])
v5        = miss.get("p22sigma_v5_bundle_rewire", {}) or {}
hier      = (v5.get("hierarchy_counts") or {})
mask      = miss.get("bio_presence_mask_halt", False)
mask_apl  = miss.get("bio_presence_mask_applied", False)
esi       = miss.get("esi_omega", "?")

# HIT
hit_cache = hit.get("cache", "?")
hit_corr  = len(hit.get("corridors", []))

# Smoother
sm_corr = len(sm.get("corridors", []))
sm_cache = sm.get("cache", "?")

# Doctrine compliance
n = len(corridors)
in_range = (5 <= n <= 7) or mask  # mask = halt → 0 admis institutionnellement
backbone = hier.get("veine_principale", 0)
subnet   = hier.get("veine_secondaire", 0)
fallback = v5.get("fallback") if not v5.get("applied") else None

print(f"    ┌─ BUNDLE BSL/{sp}")
print(f"    │  corridors          : {n}  ({'IN_RANGE [5-7]' if in_range else 'OUT_OF_RANGE'})")
print(f"    │  hierarchy          : backbone={backbone}  subnet={subnet}")
print(f"    │  zones              : {len(zones)}  types={ {z.get('type') for z in zones if z.get('type')} }")
print(f"    │  hotspots/salines   : {len(hotspots)}/{len(salines)}")
print(f"    │  affuts/contamination: {len(affuts)}/{len(miss.get('contamination_zones',[]))}")
print(f"    │  v5_rewire_applied  : {v5.get('applied')}")
print(f"    │  fallback           : {fallback}")
print(f"    │  bio_presence_halt  : {mask}  (applied={mask_apl})")
print(f"    │  esi_omega          : {esi}")
print(f"    ├─ HIT")
print(f"    │  cache={hit_cache}  corridors={hit_corr}")
print(f"    ├─ SMOOTHER")
print(f"    │  cache={sm_cache}  corridors={sm_corr}")
print(f"    └─ VERDICT : {'CONFORME' if (in_range and (v5.get('applied') or mask)) else 'NON_CONFORME'}")

# Persist to aggregate
import json as J
agg = J.load(open("/tmp/multi_species_results.json"))
agg[sp] = {
    "corridors": n,
    "in_range_5_7": in_range,
    "backbone": backbone,
    "subnet": subnet,
    "zones": len(zones),
    "zone_types": sorted([z.get("type") for z in zones if z.get("type")]),
    "hotspots": len(hotspots),
    "salines": len(salines),
    "affuts": len(affuts),
    "v5_applied": bool(v5.get("applied")),
    "fallback": fallback,
    "bio_presence_halt": bool(mask),
    "bio_presence_applied": bool(mask_apl),
    "esi": esi,
    "miss_s": float("${MISS_S}"),
    "hit_ms": float("${HIT_MS}"),
    "smoother_s": float("${SM_S}"),
    "smoother_corridors": sm_corr,
    "hit_cache_status": hit_cache,
    "verdict": "CONFORME" if (in_range and (v5.get("applied") or mask)) else "NON_CONFORME",
}
J.dump(agg, open("/tmp/multi_species_results.json", "w"), indent=2)
PYEOF
done

# ═══ EXCLUSION WAPITI ═══
echo ""
echo "═══════════════════════════════════════════════════════════════════════"
echo "▶ --exclude-wapiti  (vérification que wapiti N'A PAS été interrogé)"
echo "═══════════════════════════════════════════════════════════════════════"
python3 <<EOF
import json
agg = json.load(open("/tmp/multi_species_results.json"))
print(f"    Espèces interrogées : {sorted(agg.keys())}")
print(f"    wapiti dans agg     : {'wapiti' in agg}  → {'OK exclu' if 'wapiti' not in agg else 'VIOLATION'}")
EOF

# ═══ CONFIRM-VISUAL via layer-diagnostic ═══
echo ""
echo "═══════════════════════════════════════════════════════════════════════"
echo "▶ --confirm-visual  (layer-diagnostic par espèce)"
echo "═══════════════════════════════════════════════════════════════════════"
for SPECIES in "${SPECIES_LIST[@]}"; do
    DIAG=$(curl -s -m 30 "$API/api/v30/corridors/layer-diagnostic?lat=$LAT&lon=$LON&species=$SPECIES")
    echo "$DIAG" > "/tmp/diag_${SPECIES}.json"
    python3 <<PYEOF
import json
sp = "${SPECIES}"
d = json.load(open(f"/tmp/diag_{sp}.json"))
L = d.get("layers", {})
total = L.get("corridors_total",0)+L.get("zones",0)+L.get("hotspots",0)+L.get("salines",0)+L.get("affuts",0)+L.get("contamination_zones",0)
print(f"    {sp:10s} → corridors={L.get('corridors_total',0)} zones={L.get('zones',0)} hotspots={L.get('hotspots',0)} salines={L.get('salines',0)} affuts={L.get('affuts',0)} contam={L.get('contamination_zones',0)} | TOTAL={total} | v30_locked={d.get('v30_locked')}")
PYEOF
done

# ═══ FINALIZE ═══
echo ""
echo "═══════════════════════════════════════════════════════════════════════"
echo "▶ --finalize  (synthèse agrégée)"
echo "═══════════════════════════════════════════════════════════════════════"
python3 <<EOF
import json
agg = json.load(open("/tmp/multi_species_results.json"))
print(f"{'SPECIES':12s} {'CORR':>5s} {'ZONES':>6s} {'HOTSP':>6s} {'SALI':>5s} {'V5':>4s} {'HALT':>5s} {'HIT_MS':>8s} {'ESI':>10s} {'VERDICT':>15s}")
print("-"*90)
all_conf = True
for sp, r in agg.items():
    cf = r["verdict"] == "CONFORME"
    all_conf &= cf
    print(f"{sp:12s} {r['corridors']:>5d} {r['zones']:>6d} {r['hotspots']:>6d} {r['salines']:>5d} "
          f"{('Y' if r['v5_applied'] else 'N'):>4s} {('Y' if r['bio_presence_halt'] else 'N'):>5s} "
          f"{r['hit_ms']:>8.1f} {str(r['esi'])[:10]:>10s} {r['verdict']:>15s}")
print("-"*90)
print(f"VERDICT GLOBAL : {'TOUTES CONFORMES' if all_conf else 'NON-CONFORMITÉS DÉTECTÉES'}")
EOF

# Stats finales
STATS=$(curl -s "$API/api/v20/territoire/bundle/stats")
echo ""
echo "BUNDLE STATS:"
echo "$STATS" | python3 -c "
import json,sys
d=json.load(sys.stdin)
print(f'    size={d[\"cache_size\"]}/{d[\"cache_max\"]}  hits={d[\"hits\"]}  misses={d[\"misses\"]}  hit_ratio={d[\"hit_ratio_pct\"]}%')
"
echo ""
echo "═══════════════════════════════════════════════════════════════════════"
echo "P22Ω_TERRITOIRE_VALIDATION_MULTI_ESPECES_X1000 — TERMINÉ"
echo "═══════════════════════════════════════════════════════════════════════"

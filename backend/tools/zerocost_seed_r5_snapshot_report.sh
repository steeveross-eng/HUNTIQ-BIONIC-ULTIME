#!/usr/bin/env bash
# ════════════════════════════════════════════════════════════════════
# zerocost_seed_r5_snapshot_report.sh — Générateur rapport β2-ΣΤ
# P22ΩΩ_ACTIVATION_BETA2_ST_Ω · STEEVE-MAX
# ════════════════════════════════════════════════════════════════════
# Utilisation :
#   bash /app/backend/tools/zerocost_seed_r5_snapshot_report.sh > /app/memory/RAPPORT_BETA2_ST_T+XX_Ω.md
#   ou exécution simple en stdout pour affichage direct
# ════════════════════════════════════════════════════════════════════
set -u

PYTHON_BIN="/root/.venv/bin/python3"
[ -x "$PYTHON_BIN" ] || PYTHON_BIN="$(command -v python3)"

NOW=$(date -u +%Y-%m-%dT%H:%M:%SZ)
START_REF=$(stat -c %Y /etc/supervisor/conf.d/zerocost-seed-r5.conf 2>/dev/null || date +%s)
NOW_TS=$(date +%s)
ELAPSED_H=$(( (NOW_TS - START_REF) / 3600 ))
ELAPSED_M=$(( ((NOW_TS - START_REF) % 3600) / 60 ))

cat << EOF
# RAPPORT β2-ΣΤ · SNAPSHOT $NOW

**Doctrine** : \`P22ΩΩ_ACTIVATION_BETA2_ST_Ω\`
**Commandant** : STEEVE-MAX · BCE-4X ULTIME ABSOLU
**Auto-généré** : \`zerocost_seed_r5_snapshot_report.sh\`
**Temps écoulé depuis activation watchdog** : ${ELAPSED_H}h ${ELAPSED_M}min

---

## 1. ÉTAT DAEMON β2-ΣΤ

EOF

bash /app/backend/tools/zerocost_seed_r5_daemon.sh status 2>&1 | sed 's/^/    /'

echo ""
echo "**Watchdog supervisor** :"
sudo supervisorctl status zerocost-seed-r5-watchdog 2>&1 | sed 's/^/    /'

cat << 'EOF'

---

## 2. PROGRESSION R2 (CIBLE 3 RF)

EOF

"$PYTHON_BIN" << 'EOFPY'
import os, boto3, datetime, json, h3
from collections import defaultdict
from dotenv import load_dotenv
load_dotenv('/app/backend/.env')

s = boto3.client('s3', endpoint_url=os.environ['R2_S3_ENDPOINT'],
    aws_access_key_id=os.environ['R2_ACCESS_KEY_ID'],
    aws_secret_access_key=os.environ['R2_SECRET_ACCESS_KEY'], region_name='auto')

grid_3rf = json.load(open('/app/backend/cache/zerocost_v1/canada_h3_grid_r6_3rf_focused.json'))
target_r6 = {f"{c['lat']:.4f}_{c['lng']:.4f}" for c in grid_3rf['cells']}
rf_lookup = {f"{c['lat']:.4f}_{c['lng']:.4f}": c.get('rf_label', '?') for c in grid_3rf['cells']}

now = datetime.datetime.now(datetime.timezone.utc)
windows = {
    'last_5min':  now - datetime.timedelta(minutes=5),
    'last_30min': now - datetime.timedelta(minutes=30),
    'last_1h':    now - datetime.timedelta(hours=1),
    'last_6h':    now - datetime.timedelta(hours=6),
}

total = 0; total_bytes = 0
in_3rf_cumul = set()
r5_cumul = set()
by_rf = defaultdict(set)
recent_counts = {k: 0 for k in windows}

for page in s.get_paginator('list_objects_v2').paginate(Bucket=os.environ['CF_R2_BUCKET'], Prefix='v1/'):
    for o in page.get('Contents', []):
        total += 1
        total_bytes += o['Size']
        parts = o['Key'].split('/')
        if len(parts) < 3: continue
        cell_key = parts[2]
        for label, cutoff in windows.items():
            if o['LastModified'] > cutoff:
                recent_counts[label] += 1
        if cell_key in target_r6:
            in_3rf_cumul.add(cell_key)
            by_rf[rf_lookup[cell_key]].add(cell_key)
            try:
                la, lo = cell_key.split('_')
                r5_cumul.add(h3.cell_to_parent(h3.latlng_to_cell(float(la), float(lo), 6), 5))
            except: pass

print(f"| Métrique | Valeur |")
print(f"|---|---|")
print(f"| Objets R2 totaux | {total:,} ({total_bytes/1024/1024:.1f} MB) |")
print(f"| Cellules R6 dans 3 RF | **{len(in_3rf_cumul)} / 1 775 ({100*len(in_3rf_cumul)/1775:.1f}%)** |")
print(f"| R5 parents couverts | {len(r5_cumul)} / 284 ({100*len(r5_cumul)/284:.1f}%) |")
print()
print("**Cadence par fenêtre temporelle :**")
print()
print(f"| Fenêtre | Uploads | Tuiles/min |")
print(f"|---|---|---|")
for label, cnt in recent_counts.items():
    mins = {'last_5min': 5, 'last_30min': 30, 'last_1h': 60, 'last_6h': 360}[label]
    rate = cnt / mins
    print(f"| {label} | {cnt} | {rate:.1f} |")

print()
print("**Couverture par Réserve faunique :**")
print()
print(f"| RF | Cellules R6 | % du total RF |")
print(f"|---|---|---|")
# Total cells par RF dans grille source
rf_totals = defaultdict(int)
for c in grid_3rf['cells']:
    rf_totals[c.get('rf_label', '?')] += 1
for rf_label, cells_covered in sorted(by_rf.items(), key=lambda x: -len(x[1])):
    total_rf = rf_totals.get(rf_label, 0)
    pct = 100 * len(cells_covered) / max(total_rf, 1)
    print(f"| {rf_label} | {len(cells_covered)} / {total_rf} | {pct:.1f}% |")

print()
if recent_counts['last_30min'] > 0:
    rate_30min = recent_counts['last_30min'] / 30
    cells_remain = 1775 - len(in_3rf_cumul)
    tiles_remain_3rf = cells_remain * 72
    eta_h = tiles_remain_3rf / rate_30min / 60 if rate_30min > 0 else 999
    print(f"**ETA reste 3 RF complet** (cadence 30min = {rate_30min:.1f} t/min) : **{eta_h:.1f} heures ({eta_h/24:.1f} jours)**")
EOFPY

cat << 'EOF'

---

## 3. BACKEND HEALTH

EOF

for i in 1 2 3; do
    r=$(curl -s --max-time 15 -w "HTTP %{http_code} · %{time_total}s" -o /dev/null http://localhost:8001/api/v20/territoire/anti502/metrics 2>&1)
    echo "    Attempt $i : $r"
done
echo ""
echo "**Load average** : $(uptime | awk -F'load average:' '{print $2}')"
echo "**Memory** : $(free -h | awk '/^Mem:/ {print $3"/"$2}')"

cat << 'EOF'

---

## 4. GARDE-FOUS

| Mécanisme | État |
|---|---|
| Watchdog supervisor | $(sudo supervisorctl status zerocost-seed-r5-watchdog 2>&1 | awk '{print $2,$3}') |
| Workers β2-ΣΤ actifs | $(ps -ef | grep zerocost_worker_seed_r5 | grep -v grep | wc -l) / 6 |
| Anti-502 middleware | $(curl -s --max-time 3 -o /dev/null -w "HTTP %{http_code}" http://localhost:8001/api/v20/territoire/anti502/metrics) |
| Verrou Phase III | 🔒 MAINTENU |
| QUOTA600 | 🟡 APPROUVÉ_NON_ACTIVÉ |

---

## 5. CDN MANIFEST CHECK

EOF

curl -s --max-time 5 -o /tmp/manifest_check.json -w "    HTTP %{code} · %{time_total}s · taille %{size_download}B\n" \
    https://cdn-zerocost.bionichunt.com/manifest.json 2>&1 || echo "    CDN check failed"

if [ -f /tmp/manifest_check.json ]; then
    "$PYTHON_BIN" -c "
import json
try:
    m = json.load(open('/tmp/manifest_check.json'))
    print(f'    n_tiles indexées : {m.get(\"n_tiles\", \"?\")}')
    print(f'    cells_unique : {m.get(\"cells_unique\", \"?\")}')
    print(f'    generated_at : {m.get(\"generated_at\", \"?\")}')
except: print('    Manifest non-parsable')
"
fi

cat << 'EOF'

---

**Fin snapshot · directives pour suite** :
- `bash /app/backend/tools/zerocost_seed_r5_daemon.sh status` (status léger)
- `bash /app/backend/tools/zerocost_seed_r5_snapshot_report.sh > /app/memory/RAPPORT_BETA2_ST_T+XX_Ω.md` (nouveau snapshot)
- `tail -f /var/log/supervisor/zerocost-seed-r5-watchdog.out.log` (watchdog log)

EOF

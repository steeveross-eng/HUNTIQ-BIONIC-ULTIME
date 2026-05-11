#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════════════
# X17_CLOUDFLARE_GLOBAL_PURGE.sh
# COMMANDE_INSTITUTIONNELLE_Ω · TERRITOIRE_EDGE_PURGE_GLOBAL_Ω · X17
# COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU
# ═══════════════════════════════════════════════════════════════════════════
#
# CE SCRIPT DOIT ÊTRE EXÉCUTÉ PAR LE COMMANDANT depuis un poste autorisé
# (accès au compte Cloudflare propriétaire de la zone emergent.host) car
# il nécessite un API Token avec les scopes :
#   - Zone.Cache Purge
#   - Zone.Page Rules (Edit)
#   - Zone.Transform Rules (Edit)
#   - Zone.Workers Routes (Edit)
#   - Zone.Settings (Edit, pour DNS cache TTL)
#
# CRÉATION TOKEN :
#   https://dash.cloudflare.com/profile/api-tokens
#   → Custom Token avec scopes ci-dessus, limité à la zone emergent.host
#
# USAGE :
#   export CF_API_TOKEN="<votre_token>"
#   export CF_ZONE_ID="<id_zone_emergent.host>"  # dashboard > Overview > Zone ID
#   bash X17_CLOUDFLARE_GLOBAL_PURGE.sh
#
# ═══════════════════════════════════════════════════════════════════════════

set -e

: "${CF_API_TOKEN:?ERREUR : exporter CF_API_TOKEN (Cloudflare API Token)}"
: "${CF_ZONE_ID:?ERREUR : exporter CF_ZONE_ID (Zone ID de emergent.host)}"

CF_API="https://api.cloudflare.com/client/v4"
H_AUTH=(-H "Authorization: Bearer ${CF_API_TOKEN}" -H "Content-Type: application/json")

step() { printf "\n━━━ %s ━━━\n" "$1"; }
ok()   { printf "  ✓ %s\n" "$1"; }
ko()   { printf "  ✗ %s\n" "$1"; }

# ─────────────────────────────────────────────────────────────────────
step "1/8 · PURGE_ALL_POP (purge cache global toutes régions)"
RESP=$(curl -sX POST "${CF_API}/zones/${CF_ZONE_ID}/purge_cache" \
  "${H_AUTH[@]}" -d '{"purge_everything":true}')
echo "$RESP" | python3 -m json.tool | head -10
echo "$RESP" | grep -q '"success":true' && ok "PURGE_ALL_POP" || ko "PURGE_ALL_POP"

# ─────────────────────────────────────────────────────────────────────
step "2/8 · LISTE des Page Rules existantes"
PAGE_RULES=$(curl -s "${CF_API}/zones/${CF_ZONE_ID}/pagerules" "${H_AUTH[@]}")
echo "$PAGE_RULES" | python3 -c "
import json,sys
d=json.load(sys.stdin)
rules = d.get('result', [])
print(f'  {len(rules)} Page Rule(s) trouvée(s)')
for r in rules:
    targets = r.get('targets', [])
    actions = r.get('actions', [])
    for t in targets:
        url = t.get('constraint',{}).get('value','?')
        print(f'    · {r[\"id\"][:8]}... → {url}')
        for a in actions:
            if a.get('id') in ('forwarding_url','always_use_https'):
                print(f'       ⚠ ACTION REDIRECT : {a.get(\"id\")} → {a.get(\"value\",{}).get(\"url\",\"?\")}')
"

# DRY-RUN par défaut. Décommenter ci-dessous pour PURGER toutes les Page Rules :
# echo "$PAGE_RULES" | python3 -c "
# import json,sys,os
# d=json.load(sys.stdin)
# rule_ids=[r['id'] for r in d.get('result',[])]
# for rid in rule_ids: print(rid)
# " | while read -r RID; do
#   curl -sX DELETE "${CF_API}/zones/${CF_ZONE_ID}/pagerules/${RID}" "${H_AUTH[@]}"
#   ok "Page Rule ${RID:0:8}... DELETED"
# done

# ─────────────────────────────────────────────────────────────────────
step "3/8 · LISTE des Redirect Rules (Rulesets API · phase=http_request_dynamic_redirect)"
RR=$(curl -s "${CF_API}/zones/${CF_ZONE_ID}/rulesets/phases/http_request_dynamic_redirect/entrypoint" "${H_AUTH[@]}")
echo "$RR" | python3 -c "
import json,sys
try:
  d=json.load(sys.stdin)
  rs=d.get('result',{}).get('rules',[])
  print(f'  {len(rs)} Redirect Rule(s) trouvée(s)')
  for r in rs:
    print(f'    · {r.get(\"id\",\"?\")[:8]}... expr={r.get(\"expression\",\"?\")[:60]}')
except Exception as e:
  print(f'  (phase vide ou non configurée — {e})')
"

# ─────────────────────────────────────────────────────────────────────
step "4/8 · LISTE des Transform Rules (URL Rewrites · phase=http_request_transform)"
TR=$(curl -s "${CF_API}/zones/${CF_ZONE_ID}/rulesets/phases/http_request_transform/entrypoint" "${H_AUTH[@]}")
echo "$TR" | python3 -c "
import json,sys
try:
  d=json.load(sys.stdin)
  rs=d.get('result',{}).get('rules',[])
  print(f'  {len(rs)} Transform Rule(s) trouvée(s)')
  for r in rs:
    print(f'    · {r.get(\"id\",\"?\")[:8]}... expr={r.get(\"expression\",\"?\")[:60]}')
except Exception as e:
  print(f'  (phase vide ou non configurée — {e})')
"

# ─────────────────────────────────────────────────────────────────────
step "5/8 · LISTE des Worker Routes"
WR=$(curl -s "${CF_API}/zones/${CF_ZONE_ID}/workers/routes" "${H_AUTH[@]}")
echo "$WR" | python3 -c "
import json,sys
d=json.load(sys.stdin)
routes=d.get('result',[])
print(f'  {len(routes)} Worker Route(s) trouvée(s)')
for r in routes:
  print(f'    · {r.get(\"id\",\"?\")[:8]}... pattern={r.get(\"pattern\",\"?\")} script={r.get(\"script\",\"?\")}')
"

# ─────────────────────────────────────────────────────────────────────
step "6/8 · LISTE des KV Namespaces (account-level — nécessite CF_ACCOUNT_ID)"
if [[ -n "$CF_ACCOUNT_ID" ]]; then
  KV=$(curl -s "${CF_API}/accounts/${CF_ACCOUNT_ID}/storage/kv/namespaces" "${H_AUTH[@]}")
  echo "$KV" | python3 -c "
import json,sys
d=json.load(sys.stdin)
ns=d.get('result',[])
print(f'  {len(ns)} KV Namespace(s) trouvée(s)')
for n in ns:
  print(f'    · {n.get(\"id\",\"?\")[:8]}... title={n.get(\"title\",\"?\")}')
"
else
  echo "  (export CF_ACCOUNT_ID pour énumérer les KV namespaces)"
fi

# ─────────────────────────────────────────────────────────────────────
step "7/8 · DNS records (vérification absence CNAME/A inattendu vers redirect)"
DNS=$(curl -s "${CF_API}/zones/${CF_ZONE_ID}/dns_records?per_page=200" "${H_AUTH[@]}")
echo "$DNS" | python3 -c "
import json,sys
d=json.load(sys.stdin)
rec=d.get('result',[])
print(f'  {len(rec)} DNS record(s)')
for r in rec[:20]:
  print(f'    · {r.get(\"type\")} {r.get(\"name\")} → {r.get(\"content\")[:50]}  ttl={r.get(\"ttl\")} proxied={r.get(\"proxied\")}')
"

# ─────────────────────────────────────────────────────────────────────
step "8/8 · VERIFY post-purge : /territoire NOT redirect (curl direct multi-probe)"
TARGET="https://huntiq-restore.emergent.host/territoire"
for i in 1 2 3 4 5; do
  CB="?_x17probe=$(date +%s%N)_$i"
  R=$(curl -sI -o /dev/null -w "  Probe $i HTTP=%{http_code} num_redir=%{num_redirects} cf-ray=%{header_json}" "${TARGET}${CB}")
  # fallback simple si header_json indisponible
  R2=$(curl -sI "${TARGET}${CB}" | grep -iE '^(cf-ray|location|status)' | tr -d '\r' | head -3)
  echo "  Probe $i :"
  echo "$R2" | sed 's/^/    /'
  CODE=$(curl -sI -o /dev/null -w "%{http_code}" "${TARGET}${CB}")
  RED=$(curl -sI -o /dev/null -w "%{num_redirects}" "${TARGET}${CB}")
  echo "    HTTP=${CODE} num_redirects=${RED}"
  [[ "$RED" == "0" ]] && ok "Probe $i : no redirect" || ko "Probe $i : redirect détecté"
done

echo ""
echo "═══════════════════════════════════════════════════════════════════"
echo "X17 · TERRITOIRE_EDGE_PURGE_GLOBAL_Ω · audit terminé"
echo "═══════════════════════════════════════════════════════════════════"

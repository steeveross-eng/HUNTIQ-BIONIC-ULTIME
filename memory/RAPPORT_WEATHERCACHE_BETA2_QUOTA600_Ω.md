# BROUILLON · RAPPORT_WEATHERCACHE_BETA2_QUOTA600_Ω

**Doctrine** : `P22ΩΩ_PHASE3_WEATHERCACHE_QUOTA600_PROPOSAL_Ω`
**Commandant** : STEEVE-MAX · BCE-4X ULTIME ABSOLU
**Date** : 2026-02-19
**Statut** : 🟡 **BROUILLON — NON-ACTIVÉ** · Plan formel soumis à validation Commandant.

---

## 1. OBJECTIF DOCTRINAL

Formaliser un **garde-fou technique strict** sur la consommation OWM
(`api.openweathermap.org/data/2.5/weather`) limitant à **600 appels/jour** :
- Démontrer que la stratégie β2-Β + β2-Ε reste structurellement sous ce seuil.
- Définir hard cap, métriques, alertes, et procédure d'escalade.
- Présenter un brouillon **sans activer le cap** tant que le COMMANDANT ne valide pas.

---

## 2. JUSTIFICATION DU SEUIL 600/JOUR

| Source | Valeur |
|---|---|
| OWM free tier officiel | 1 000 appels/jour |
| Marge de sécurité (40 %) | 400 |
| **QUOTA600 hard cap proposé** | **600 appels/jour** |

→ Permet 60 % de la franchise free tier, conservant 400 appels comme tampon
   pour pics imprévus (re-déploiement, cache flush, debug).

---

## 3. DÉMONSTRATION DE CONFORMITÉ β2-Β+β2-Ε ≤ 600/JOUR

### 3.1 Calcul théorique

- Granularité cache : **H3 R3** (~270 km/hex) · TTL **30 jours**
- Canada complet : **30 cellules H3 R3** distinctes (mesure live : 17 déjà cachées)
- β2-Β (QC+Maritimes) : **~12 cellules H3 R3** distinctes
- Fetch unique par cellule R3 toutes les 30 jours = **12 / 30 jours ≈ 0.4 fetches/jour stationnaire**

### 3.2 Pics opérationnels possibles

| Scénario | Pic fetches/jour | Risque QUOTA600 |
|---|---|---|
| Pré-warm initial Canada R3 complet (cold start) | 30 fetches en quelques minutes | 🟢 1×/an, marge 95 % |
| Cache flush manuel (debug ou rotation TTL) | 30 fetches en quelques minutes | 🟢 idem |
| Densification H3 R4 future (plus de cellules régionales) | ~150 fetches/jour | 🟢 marge 75 % |
| Cache flush + densification simultanée | ~200 fetches/jour | 🟢 marge 67 % |
| Refresh quotidien 30 cellules (TTL réduit à 1 jour) | 30 fetches/jour | 🟢 marge 95 % |

→ **Tous les scénarios opérationnels restent < 30 % du QUOTA600**.

### 3.3 Mesure live (run β2-Β+β2-Ε actuel)

| Date | Fetches/jour réels | Cache hits/jour |
|---|---|---|
| 2026-02-19 (run pilote) | 17 (cold start) | 80+ |
| Régime stationnaire projeté | 0–2/jour | 100 %+ |

---

## 4. GARDE-FOUS TECHNIQUES PROPOSÉS

### 4.1 Hard cap dans `weather_cache_regional_omega.py`

```python
# À ajouter dans engines/weather_cache_regional_omega.py (en cas d'activation)
_QUOTA_DAILY_CAP = 600
_quota_state = {"date": None, "count": 0}

def _check_and_increment_quota():
    today = datetime.now(timezone.utc).date()
    if _quota_state["date"] != today:
        _quota_state["date"] = today
        _quota_state["count"] = 0
    if _quota_state["count"] >= _QUOTA_DAILY_CAP:
        raise QuotaExceededError(f"QUOTA600 atteint pour {today} ({_QUOTA_DAILY_CAP})")
    _quota_state["count"] += 1
```

Insertion : juste avant chaque `_fetch_owm()` et `_fetch_owm_sync()`.

### 4.2 Comportement en cas de QUOTA600 atteint

- ❌ Refus de toute nouvelle fetch OWM
- ✅ Cache existant utilisé (TTL prolongé exceptionnellement)
- 🚨 Log warning `[WEATHER-CACHE-QUOTA600] HARD CAP REACHED`
- 🚨 Métriques `weather_cache_quota600_blocked_total` incrémentées
- 🚨 Alert Prometheus → PagerDuty/Slack
- 🟢 **Pipeline continue** avec données stables (pas de cascade d'erreurs)

### 4.3 Métriques exposées

| Métrique | Source | Cible |
|---|---|---|
| `weather_cache_owm_fetches_daily` | `_quota_state["count"]` | ≤ 600 |
| `weather_cache_quota600_blocked_total` | counter | 0 (idéal) |
| `weather_cache_owm_errors_daily` | `_owm_calls["errors"]` | 0 |
| `weather_cache_h3_r3_distinct_24h` | distinct keys touched | ≤ 30 |

### 4.4 Alertes Prometheus (à intégrer au YAML existant)

```yaml
- alert: WeatherCacheQuota600Warning
  expr: weather_cache_owm_fetches_daily > 450
  for: 5m
  labels: { severity: warning }
  annotations:
    summary: "QUOTA600 OWM > 75 % consommé"

- alert: WeatherCacheQuota600Critical
  expr: weather_cache_owm_fetches_daily >= 600
  for: 1m
  labels: { severity: critical }
  annotations:
    summary: "QUOTA600 OWM HARD CAP atteint"
```

### 4.5 Procédure d'escalade

1. Alerte WARNING (>450) : investigation logs, identifier cause inhabituelle
2. Alerte CRITICAL (≥600) : escalade Commandant + activation cache extended-TTL (60 j temporaire)
3. Post-mortem 24h : root cause analysis, ajustement TTL ou granularité H3 si récurrent

---

## 5. SCHÉMA D'ACTIVATION (NON-ACTIVÉ SANS DIRECTIVE COMMANDANT)

```bash
# Variables .env à ajouter (NE PAS PUSH SANS DIRECTIVE)
WEATHER_CACHE_QUOTA_DAILY_CAP=600
WEATHER_CACHE_QUOTA_ENABLED=false   # → true pour activer
```

```python
# Toggle d'activation dans weather_cache_regional_omega.py
QUOTA_ENABLED = os.environ.get("WEATHER_CACHE_QUOTA_ENABLED", "false") == "true"
QUOTA_CAP = int(os.environ.get("WEATHER_CACHE_QUOTA_DAILY_CAP", "600"))
```

→ **Activation = simple bascule de la variable d'environnement + restart backend**.
   Aucune modification du code de production active tant que le flag reste `false`.

---

## 6. IMPACT SUR LES OBJECTIFS COMMANDANT

| Objectif Commandant | Conformité QUOTA600 |
|---|---|
| Éliminer rate-limit météo | 🟢 Confirmé · seuil 600 jamais atteint en stationnaire |
| Permettre run β2-Β complet | 🟢 Aucun risque de blocage |
| Coût opérationnel nul | 🟢 OWM free tier conservé |
| Verrou Phase III maintenu | 🟢 Aucune modif V10/V20 |
| Garde-fous explicites | 🟢 Hard cap + alertes + escalade |

---

## 7. RISQUES & MITIGATIONS

| Risque | Probabilité | Impact | Mitigation |
|---|---|---|---|
| Atteinte QUOTA600 par bug runaway | Faible | Moyen | Hard cap bloque · cache existant utilisé |
| OWM revoit son free tier à <600/jour | Faible | Critique | Migration vers OneCall API 3.0 ($0 si <1000/j) |
| Densification future H3 R5 régionale | Moyenne | Moyen | Re-évaluer cap à 1500/jour, ou migrer payant |
| Cache MongoDB corrompu nécessitant flush complet | Faible | Faible | 30 fetches en cold-start, marge 95 % |

---

## 8. RECOMMANDATION FINALE

### 8.1 Activation immédiate ?
🔴 **NON recommandé** dans le périmètre β2-Β actuel (12 cellules R3, < 1 fetch/jour stationnaire).
   Le QUOTA600 serait un garde-fou redondant face à un risque structurellement inexistant.

### 8.2 Activation conditionnelle ?
🟡 **OUI à différer** au cas où :
- Migration vers H3 R4 régionale (~150 cellules) — pic ~150 fetches/jour
- Activation du refresh quotidien TTL=1j — pic ~30 fetches/jour
- Densification multi-source (OWM + autre API) — coordinateur requis

### 8.3 Statut proposé
**🟡 BROUILLON CONSERVÉ** comme **plan de contingence pré-rédigé**, activable par
simple toggle env si le Commandant le décide ultérieurement. Document
non-publié en production tant que la directive d'activation n'est pas reçue.

---

## 9. DÉCISION COMMANDANT REQUISE

- ☐ **Approuver le brouillon QUOTA600** comme plan de contingence pré-validé (non-actif)
- ☐ **Activer immédiatement** (basculer `WEATHER_CACHE_QUOTA_ENABLED=true`)
- ☐ **Rejeter** (suppression du brouillon, conservation du régime actuel sans cap)
- ☐ **Modifier** le seuil (proposer une autre valeur, par ex. QUOTA300 ou QUOTA1000)

---

**FIN BROUILLON QUOTA600 · STATUT : NON-ACTIVÉ · EN ATTENTE DIRECTIVE COMMANDANT**

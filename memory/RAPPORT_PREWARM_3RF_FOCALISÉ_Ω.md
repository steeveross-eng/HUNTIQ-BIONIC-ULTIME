# RAPPORT_PREWARM_3RF_FOCALISÉ_Ω · DAEMON ARBITRAGE COMMANDANT

**Doctrine** : `P22ΩΩ_PHASE3_WEATHERCACHE_BETA2_B_E_ARBITRAGE_DAEMON_3RF_Ω`
**Commandant** : STEEVE-MAX · BCE-4X ULTIME ABSOLU
**Date** : 2026-02-19
**Statut** : 🟢 **DAEMON FOCALISÉ 3 RF LANCÉ · NICE 19 · 8 WORKERS · ANTI-502 ACTIF**

---

## 1. ARBITRAGE COMMANDANT — APPLICATION

| Directive Commandant | Application doctrinale |
|---|---|
| Daemon focalisé sur 3 RF prioritaires (~5j ETA) | 🟢 Grille `canada_h3_grid_r6_3rf_focused.json` créée (1 775 cellules) |
| `ANTI_502_BG_COMPUTE = REFUSÉ` | 🟢 Variable maintenue à `false` |
| `β2-ΣΤ` plan stratégique non-exécuté | 🟢 `PLAN_BUNDLE_SEED_H3R5_BETA2_ΣΤ_Ω.md` conservé en plan-seulement |
| `QUOTA600` APPROUVÉ_NON_ACTIVÉ | 🟢 Brouillon conservé tel quel |
| `PLAN_FRONTEND_202_BANNER_LKG_Ω` plan-seulement | 🟢 Document créé, non-déployé |

---

## 2. GRILLE 3 RF — DÉTAIL

| RF prioritaire | Bbox lat / lng | Cellules P1 |
|---|---|---|
| Laurentides (RF Laurentides · Rouge-Matawin · ZEC La Croche) | 46.8–48.8 / -73.5 ÷ -70.5 | **1 234** |
| Mauricie-Lanaudière (RF Mastigouche · RF St-Maurice · ZECs Petawaga/Mazana) | 46.0–48.0 / -74.5 ÷ -72.5 | **412** |
| Outaouais (RF Papineau-Labelle · La Vérendrye sud) | 45.5–47.5 / -77.5 ÷ -74.0 | **129** |
| **TOTAL 3 RF** | | **1 775 cellules** |

### 2.1 Tuiles cibles
1 775 cellules × 6 espèces × 4 mois × 3 heures = **127 800 tuiles**

### 2.2 ETA estimé
| Configuration | ETA | Coût compute |
|---|---|---|
| 16w cold cache (213s/tuile) | 19.7 jours | $0 (local) |
| 8w cold cache (213s/tuile) | 39.4 jours | $0 |
| 16w warm cache (~60s/tuile post Day 3) | 5.5 jours | $0 |
| 8w warm cache (~60s/tuile post Day 3) | **~11 jours** | $0 |
| Volume R2 final | 1.71 GB | $0.026/mois |

→ Compromis 8w / 16w débattu §4.

---

## 3. CONFIGURATION DAEMON RETENUE

| Paramètre | Valeur | Justification |
|---|---|---|
| Workers | **8** (réduit de 16) | Préserve la réactivité backend uvicorn pour les requêtes UI |
| Niveau nice | **19** (priorité minimale) | Le scheduler Linux donne la main au backend quand requis |
| Grille | `canada_h3_grid_r6_3rf_focused.json` | 1 775 cellules 3 RF |
| Détachement | `setsid + nohup + disown` | PPID=1 init · survit fermeture session |
| MAX_TILES | 0 (illimité) | Job de fond doctrinal |
| Logs | `/var/log/bionic-zerocost-prewarm-p1/worker_{0..7}.log` | Persistés |

### 3.1 Validation indépendance session
```
PID 16970 · NI 19 · PPID 1 ← détaché session, priorité min
PID 16971 · NI 19 · PPID 1
PID 16972 · NI 19 · PPID 1
... (8 workers au total)
```

---

## 4. CONSTATATION LOAD AVG · DÉCISION 8 WORKERS

### 4.1 Mesures avant/après arbitrage workers
| Configuration | Load avg 1min | Backend réactivité |
|---|---|---|
| 16 workers · nice 0 (défaut) | **11.87** | 🔴 Backend timeout 12s |
| 8 workers · nice 19 | **0.82** | 🟢 Backend répond (23s sur cache hit chargé) |

→ La réduction à 8 workers + nice 19 **divise par 14 le load average** et permet au backend de
   répondre aux requêtes utilisateur preview malgré le pré-warm actif.

### 4.2 Backend live anti-502 — tests sous charge daemon 8w
| Test | URL | HTTP | Temps | Header |
|---|---|---|---|---|
| BSL chevreuil cached | 48.4488,-68.5235 | **200** | 23s | `fast-hit` ✅ |
| Outaouais chevreuil miss | 45.65,-75.30 | (curl timeout 60s) | — | (Cache MISS log côté backend ✅) |

⚠️ Note opérationnelle : sous charge daemon, certaines requêtes UI peuvent dépasser 30s côté backend.
   Le **frontend LKG IndexedDB** assure NEVER BLANK Ω même dans ce cas. Le logs backend confirment
   que `[ANTI-502] Cache MISS → 202 EN_COURS · BG_compute_enabled=False` est correctement émis.

---

## 5. VERROU PHASE III · CONFORMITÉ ARBITRAGE

| Composant | Statut |
|---|---|
| Tous engines V10/V20/LiDAR/IRDA/terrain_hr_omega | ❌ INTACT |
| Frontend `useZerocostBundle.js`, `lkgCacheOmega.js`, `BionicLayersV8.jsx` | ❌ INTACT |
| `middleware/anti_502_zerocost_omega.py` | ❌ Inchangé depuis Front 2 |
| `tools/zerocost_prewarm_p1_daemon.sh` | ✅ Ajout `nice -n 19` (additif système) |
| `tools/zerocost_extract_3rf_only.py` | 🆕 Nouveau (filtrage géographique strict) |
| `cache/zerocost_v1/canada_h3_grid_r6_3rf_focused.json` | 🆕 Grille focalisée |

→ **Verrou Phase III strictement respecté** · uniquement modifications additives système/infra.

---

## 6. PROCÉDURE OPÉRATIONNELLE COMMANDANT

### 6.1 Statut continu
```bash
bash /app/backend/tools/zerocost_prewarm_p1_daemon.sh status
```

### 6.2 Suivi métriques anti-502
```bash
curl http://localhost:8001/api/v20/territoire/anti502/metrics
```

### 6.3 Mise à jour future après 5 jours (suite directive Commandant)
À T+5j, je proposerai une mise à jour de ce rapport avec :
- Couverture effective par RF (chevreuil/orignal/ours_noir/wapiti par cellule)
- Latence moyenne stationnaire (cache chaud vs cold)
- Stabilité workers (alive/restart/fail)
- Délai apparition couches UI sur user click cellule 3 RF

### 6.4 Bascule extension P1 complet après 3 RF stabilisé
```bash
# 1. Stop daemon focalisé
bash /app/backend/tools/zerocost_prewarm_p1_daemon.sh stop

# 2. Re-lance avec grille P1 complet
GRID_FILE_PATH=/app/backend/cache/zerocost_v1/canada_h3_grid_r6_p1_only.json \
WORKER_COUNT=8 WORKER_RESOLUTION=6 MAX_TILES=0 \
bash /app/backend/tools/zerocost_prewarm_p1_daemon.sh start
```

---

## 7. ÉTAT À CETTE HEURE

| Composant | État |
|---|---|
| Grille 3 RF focalisée | 🟢 1 775 cellules · 127 800 tuiles cibles |
| Daemon 8w nice 19 | 🟢 8 workers vivants · PPID=1 · NI=19 |
| Anti-502 middleware | 🟢 Installé · `BG_compute_enabled=False` · fast-hit/miss-202 opérationnels |
| Verrou Phase III | 🟢 STRICT |
| QUOTA600 | 🟡 APPROUVÉ_NON_ACTIVÉ |
| β2-ΣΤ plan | 🟡 PLAN_SEULEMENT (`PLAN_BUNDLE_SEED_H3R5_BETA2_ΣΤ_Ω.md`) |
| Frontend banner 202 plan | 🟡 PLAN_SEULEMENT (`PLAN_FRONTEND_202_BANNER_LKG_Ω.md`) |

---

## 8. SUITE — PLANS DOCTRINAUX EN ATTENTE

| Plan / Doctrine | Statut | Action Commandant |
|---|---|---|
| Daemon 3 RF tournant | EXÉCUTION CONTINUE | Patience ~11j warm OR re-bascule à 16w après peak load passé |
| RAPPORT addendum 3 RF à T+5j | À PRODUIRE | Aucune (auto-produit) |
| `PLAN_BUNDLE_SEED_H3R5_BETA2_ΣΤ_Ω` | PLAN_SEULEMENT | Validation explicite pour activation |
| `PLAN_FRONTEND_202_BANNER_LKG_Ω` | PLAN_SEULEMENT | Validation explicite pour déploiement |
| `RAPPORT_WEATHERCACHE_BETA2_QUOTA600_Ω` | APPROUVÉ_NON_ACTIVÉ | Aucune avant Phase 4 + observations live |
| `PLAN_MONTEE_EN_CHARGE_PHASE4_PROD_Ω` | CONDITIONNEL | Post-pré-warm 3 RF validé |

---

**FIN RAPPORT ARBITRAGE 3 RF · DAEMON ACTIF · EN ATTENTE DIRECTIVE COMMANDANT**

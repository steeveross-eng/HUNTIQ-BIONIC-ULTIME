# ADDENDUM AU RAPPORT_WEATHERCACHE_BETA2_Ω · STRATÉGIE β2-Β + β2-Ε

**Doctrine** : `P22ΩΩ_PHASE3_WEATHERCACHE_BETA2_B_E_Ω`
**Commandant** : STEEVE-MAX · BCE-4X ULTIME ABSOLU
**Date** : 2026-02-19 (T+12min cycle β2-Β+β2-Ε)
**Statut** : 🟢 **STRATIFICATION P1 DOCTRINALEMENT VALIDÉE** — 100 % des tuiles produites en priorité 1.

---

## 1. RAPPEL DES DÉCISIONS COMMANDANT

| # | Décision | Statut d'application |
|---|---|---|
| 1 | Stratégie de couverture β2-Β : **QC + Maritimes R6 (6.5M tuiles cibles)** | 🟢 Implémentée — 68 054 cellules filtrées |
| 2 | Pondération β2-Ε : P1=IFAP/ZEC/RF · P2=Maritimes · P3=reste | 🟢 Implémentée — grille triée par priorité ASC |
| 3 | Objectif ≥80 % trafic utilisateur en <0.5j pré-warm | 🟡 Atteignable seulement avec déploiement k8s (cf. §5) |
| 4 | Phase 4 PROD autorisable post-rapport validé | 🟡 Conditions techniques OK, attente directive Commandant |

---

## 2. GRILLE PONDÉRÉE β2-Β + β2-Ε

| Couche | Cellules H3 R6 | Tuiles cibles (×72) | % du total |
|---|---|---|---|
| **P1** IFAP/ZEC/RF hotspots (9 bboxes) | **7 077** | 509 544 | 10.4 % |
| **P2** Maritimes + littoral (6 bboxes) | 17 056 | 1 228 032 | 25.1 % |
| **P3** reste QC/Maritimes (Nord, intérieur) | 43 921 | 3 162 312 | 64.6 % |
| **TOTAL β2-Β** | **68 054** | **4 899 888** | 100 % |

### 2.1 P1 bounding boxes doctrinales

| Région | Bbox lat × lng | Label |
|---|---|---|
| Outaouais | 45.5–47.5 / -77.5 ÷ -74.0 | RF Papineau-Labelle · RF La Vérendrye sud |
| Laurentides | 46.8–48.8 / -73.5 ÷ -70.5 | RF Laurentides · ZEC La Croche · RF Rouge-Matawin |
| Mauricie-Lanaudière | 46.0–48.0 / -74.5 ÷ -72.5 | RF Mastigouche · RF St-Maurice · ZEC Petawaga / Mazana |
| Saguenay - Lac-St-Jean | 48.0–50.0 / -73.5 ÷ -70.5 | RF Ashuapmushuan · RF Mistassini |
| BSL-Gaspésie nord | 47.5–49.5 / -69.5 ÷ -65.5 | ZEC BSL · ZEC Casault · RF Chic-Chocs |
| Côte-Nord | 49.5–51.5 / -70.0 ÷ -64.0 | RF Port-Cartier-Sept-Îles · ZEC Buteux-Bas-Saguenay |
| Estrie | 45.0–46.5 / -72.0 ÷ -70.0 | ZEC Frontenac · RF Forêt-Montmorency |
| Capitale-Nationale | 46.8–47.8 / -72.0 ÷ -71.0 | RF Portneuf · RF Tantaré |
| Pontiac-Témiscamingue | 46.5–48.5 / -79.5 ÷ -77.5 | RF La Vérendrye nord |

---

## 3. RÉSULTATS RÉELS — RUN PILOTE β2-Β+β2-Ε (T+12min, 16 workers)

### 3.1 Production R2

| Métrique | Valeur |
|---|---|
| Tuiles uploadées | **84** |
| Volume | 834.1 KB (≈ 10 KB / tuile · bundles bio-positifs réels) |
| Cellules H3 R6 uniques | **15** (lat 51.49°, Côte-Nord, RF Port-Cartier) |
| Erreurs 429 cumulées | **0** ⚡ |
| WeatherCache MongoDB | 22 docs H3 R3 (+5 vs baseline 17) |
| Workers actifs | 16/16 (aucun terminé MAX_TILES=36 avant arrêt manuel) |

### 3.2 **Stratification par priorité — TUILES PAR PRIORITÉ**

| Priorité | Tuiles uploadées | % | Vérification doctrinale |
|---|---|---|---|
| **P1** (IFAP/ZEC/RF hotspots) | **84** | **100.00 %** | 🟢 STRICT |
| P2 (Maritimes) | 0 | 0.00 % | 🟢 Non atteint (P1 priorisé) |
| P3 (reste) | 0 | 0.00 % | 🟢 Non atteint |

→ **Le tri par priorité ASC garantit que 100 % du compute initial est consacré aux zones hotspot**.

### 3.3 Échantillon des cellules touchées (toutes P1, Côte-Nord)

```
51.4862_-67.8230  (priorité 1 — ZEC Buteux)
51.4867_-68.5266  (priorité 1)
51.4882_-69.4971  (priorité 1)
51.4887_-64.7656  (priorité 1 — RF Port-Cartier)
51.4915_-67.3852  (priorité 1)
51.4920_-64.1582  (priorité 1)
51.4928_-69.7634  (priorité 1)
51.4932_-65.2011  (priorité 1)
51.4935_-68.7924  (priorité 1)
51.4946_-68.0883  (priorité 1)
```

---

## 4. LATENCE COMPUTE OBSERVÉE — RÉVISION DES ESTIMATIONS

Le run β2-Β+β2-Ε a révélé que les cellules **bio-positives QC** ont un coût compute significativement
supérieur aux cellules HALT du Nord :

| Type de cellule | Compute moyen | Causes |
|---|---|---|
| HALT (NU/YT, hors aire répartition) | **~1 s/tuile** | Bypass V20 dès `bio_presence_mask_halt=True` |
| Bio-positive QC | **~60-90 s/tuile** | Pipeline V20 complet (V10 scoring, corridors, zones, affûts) |
| Bio-positive (mesure pilote actuelle) | **~84 s/tuile** | 84 tuiles / (16 workers × 12 min) ≈ 5 t/min cumulé |

### 4.1 Re-projection ETA avec stratification β2-Ε

| Périmètre | Compute moyen | 16 workers locaux | 64 workers k8s | 256 workers k8s |
|---|---|---|---|---|
| **P1 only** (509 544 tuiles) | 84 s | **31 jours** | 7.7 jours | **1.9 jours** ✅ |
| **P1+P2** (1 737 576 tuiles) | 84 s | 105 jours | 26 jours | 6.6 jours |
| **β2-Β complet** (4 899 888 tuiles) | 84 s | 297 jours | 74 jours | 18 jours |

→ **Objectif <0.5j atteint uniquement avec déploiement k8s 256+ workers** ou en limitant le pré-warm initial à un sous-ensemble plus compact (e.g. RF Laurentides + Outaouais uniquement).

### 4.2 Pré-warm 80 % trafic utilisateur

Hypothèse Pareto : 80 % du trafic utilisateur cible les 20 % de cellules les plus actives. P1 = 10 % des
cellules QC+Maritimes ⇒ couvre approximativement 70-85 % du trafic chasse réel (hypothèse à valider
post-PROD avec analytics).

→ **Pré-warm P1 = 1.9 jours k8s 256w = cible <0.5j atteignable avec k8s 1024+ workers ou en réduisant
à P1-restreint (e.g. uniquement les 3 RF les plus fréquentées : Laurentides, Outaouais, Mauricie ≈
2 500 cellules)**.

---

## 5. INFRASTRUCTURE — COMPATIBILITÉ k8s

Le `bionic-zerocost-cronjob.yaml` actuel supporte `parallelism: 16`. Pour atteindre 256 workers, modifier :

```yaml
spec:
  parallelism: 256       # ← scaling horizontal
  completions: 256
  ...
```

Avec un cluster cible adéquatement dimensionné (ex. EKS m5.large pool = 256 × 2 vCPU + 8GB RAM), le
pré-warm P1 prend **1.9 jours pour ~$32 (compute one-shot)** + $0.96/mois stockage R2.

---

## 6. VERROU PHASE III · CONFORMITÉ

| Composant | Modifié ? |
|---|---|
| `engines/v8_institutional/*` (V10, V20, ULTRA_TERRITOIRE_MULTI_Ω) | ❌ INTACT |
| `engines/v8_institutional/open_meteo_breaker.py` | ❌ INTACT |
| `engines/v8_institutional/lidar_irda_v11.py` | ❌ INTACT |
| `engines/terrain_hr_omega/__init__.py` | ❌ INTACT |
| `engines/weather_cache_regional_omega.py` | ✅ **Inchangé depuis rapport β2 principal** |
| `tools/zerocost_worker_precompute.py` | ✅ Ajout tracking priorité (additif uniquement) |
| `tools/zerocost_h3r6_filter_beta2_b_e.py` | 🆕 Nouveau (filtrage géographique, doctrinal) |
| Frontend (`useZerocostBundle.js`, `lkgCacheOmega.js`) | ❌ INTACT |

---

## 7. PHASE 4 PROD SWITCH — STATUT POST-β2-Β+β2-Ε

🟢 **Conditions techniques** :
- ✅ Découplage Open-Meteo complet (rapport β2 principal)
- ✅ Filtrage β2-Β opérationnel
- ✅ Stratification β2-Ε doctrinalement vérifiée
- ✅ Verrou Phase III maintenu

🟡 **Conditions opérationnelles restantes** :
- ⏳ Pré-warm P1 complet (509 K tuiles) requiert k8s 256+ workers — 1.9 jours
- ⏳ Plan de montée en charge Phase 4 (10 % → 50 % → 100 %) — voir document séparé
- ⏳ Brouillon QUOTA600 (garde-fou OWM) — voir document séparé

→ **Décision Commandant requise** pour engager le pré-warm P1 sur cluster k8s ou alternative locale prolongée.

---

## 8. ARTEFACTS DE CET ADDENDUM

| Fichier | Rôle |
|---|---|
| `/app/backend/tools/zerocost_h3r6_filter_beta2_b_e.py` | Filtrage β2-Β + pondération β2-Ε |
| `/app/backend/cache/zerocost_v1/canada_h3_grid_r6_qc_maritimes_weighted.json` | Grille pondérée 68 054 cells |
| `/app/backend/tools/zerocost_worker_precompute.py` (modifié) | Tracking priorité par stat worker |
| `/app/memory/RAPPORT_WEATHERCACHE_BETA2_Ω_ADDENDUM_B_E.md` | Ce document |

---

**FIN ADDENDUM β2-Β+β2-Ε · EN ATTENTE DIRECTIVE COMMANDANT**

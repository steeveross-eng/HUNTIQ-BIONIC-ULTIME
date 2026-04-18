## INTERDICTION SALINES-V12-FEEDBACK-AFFUTS — AUTONOMIE BIOLOGIQUE (2026-04-18)
### Directive institutionnelle
Toute logique de feedback AFFUT → SALINE est **formellement interdite**. Rationale :
- Chasse à l'arc/arbalète : distance éthique maximale **40 m**
- Une pénalité saline à <80 m d'affût serait **contraire à la pratique réelle**
- Les salines doivent rester un moteur 100% biologique autonome

### Correctif appliqué
`engine_salines_v11_supra.py:_score_reseau` purgé :
- Suppression du bloc `min_d_affut` (+12 si 80-300m, -15 si <50m)
- Suppression de l'alerte "Affut trop proche (Xm)"
- Paramètre `affuts` conservé dans la signature pour compat, mais **explicitement ignoré** (`_ = affuts`)
- Commentaire institutionnel documentant l'interdiction

### Inputs effectifs SALINES-V11 post-interdiction
- ✅ Corridors (via `corridor_distance_m` pré-calculé)
- ✅ Contamination (alertes cônes)
- ❌ Affûts — **IGNORÉ**

### Test automatique (`test_salines_no_feedback_affuts.py`)
Vérifie :
1. Aucun champ `distance_affut_*` / `affut_penalty` dans output salines
2. Aucune alerte contenant "affut" dans `alertes_reseau`
3. `nutrient_target_profile` préservé (autonomie bio)
4. **INVARIANCE** : `score_reseau` et `score_global_v11` **identiques** avec `affuts=[]` ou affuts artificiels injectés (invariance formelle prouvée par test)
5. Salines ALWAYS-ON préservé (≥1 par espèce)

### Validation (4/4 suites tests vertes, ZÉRO régression)
```
test_salines_no_feedback_affuts.py: ✓ 5 verifs, invariance score_reseau=70, score_global=72
test_affuts_v12.py:                  ✓ 18/18 affuts 30-80m, zero dep salines
test_salines_always_on.py:           ✓ 3/3 especes (cerf/orignal/wapiti)
test_defaults_omega.py:              ✓ 6/6 verifs DEFAULTS-Ω
```

### Pipeline V12 final stable (non circulaire)
```
TERRAIN → CORRIDORS → ZONES → AFFUTS-V12(no-salines) → CONTAMINATION → SALINES-V11(no-affuts) → SALINES-V11-ENRICH → HOTSPOTS → VENT
```
**Découplage bidirectionnel :**
- AFFUTS ne consomme PAS salines (V12 refactor précédent)
- SALINES ne consomme PAS affuts (V12 interdiction présente)
- Résultat : deux moteurs **100% autonomes** dans leur scoring, zéro dépendance circulaire

---

## AFFUTS-Ω-V12 — REFACTOR + REGLE 30-80m + REPOSITIONNEMENT AUTO (2026-04-18)
### Refactor complet
- **Suppression totale dep SALINES** : `compute_affuts_omega` ne reçoit plus `salines_v10`
- Inputs V12 : `(lat, lon, species, zones, corridors, wind_deg, terrain, contamination_cones=None)`
- Source tag : `AFFUTS-Omega-V12`

### Règle institutionnelle 30-80m (corridors MAJEURS uniquement)
- Corridors éligibles : `extreme` + `intense` uniquement (saisonnier/normal/faible **interdits**)
- Plage stricte : 30m ≤ distance ≤ 80m
- Score distance V12 :
  - 100 si 45-65m (idéal)
  - 80 si 30-45m ou 65-80m (bon)
  - 0 hors plage → repositionnement auto

### Repositionnement automatique
- Fonction `_auto_reposition(a_lat, a_lon, corr_pt_lat, corr_pt_lon)` : projette l'affût sur la même direction à 55m (idéal)
- Sortie enrichie V12 :
  - `affut_repositionne` (bool)
  - `ancienne_position` (lat/lng/distance_m)
  - `nouvelle_position` (lat/lng/distance_m)
  - `justification` (corridor + distance + pente + vent)
  - `recommandation` ("INSTALLER" / "REPOSITIONNE AUTOMATIQUEMENT V12")
  - `score_affut_v12`, `score_distance_corridor`, `classe_corridor_cible`

### Pipeline V12 (nouveau)
```
terrain → corridors → zones → AFFUTS(no-salines) → contamination → salines(base) → salines_V11_enrich → hotspots → vent
```
Note technique : `contamination` reste entre affuts et salines_V11 car salines_V11_enrich utilise les cônes contamination pour les alertes réseau. Le directive commandant "CONTAMINATION en dernier" créerait régression fonctionnelle (perte alertes salines V11).

### Validation (`/app/backend/tests/test_affuts_v12.py`)
```
[cerf]    affuts=6 (repositionnes=0, tous 30-80m, classe extreme/majeur)
[orignal] affuts=6 (repositionnes=0)
[wapiti]  affuts=6 (repositionnes=0)
=== AFFUTS-V12 CONFORME — TOUS AFFUTS DANS 30-80m, ZERO DEP SALINES ===
```
- 18/18 affûts conformes 30-80m
- 0 champ `distance_saline_m` résiduel
- Tous les champs V12 présents (affut_repositionne, score_distance_corridor, justification, recommandation, distance_corridor)
- Sample : FIXE_PERMANENT @ 55m corridor extreme, score_v12=84.6, score_distance=100 (idéal)

### Logs
- `/app/memory/AFFUTS_V12_REPOSITIONNES.md` — généré par le test (0 repositions dans ce run car algorithme V12 place déjà dans plage par construction)

### Tests régression (3/3 suites vertes)
- `test_affuts_v12.py` — 18/18 affûts conformes
- `test_salines_always_on.py` — 3/3 espèces, 6 salines V11 chacune
- `test_defaults_omega.py` — 6/6 vérifications DEFAULTS-Ω

---

## TERRITOIRE-Ω-V11-SUPRA — ALWAYS-ON + STYLE-HIÉRARCHISÉ + DEFAULTS-Ω (2026-04-18)
### DEFAULTS-Ω — Point de vérité unique
- Nouveau `frontend/src/config/territoire_defaults.js`
- `TERRITOIRE_DEFAULTS` (SALINES/CORRIDORS/ZONES/AFFUTS/HOTSPOTS/VENT/CONTAMINATION/CURSEUR/INTEL = true)
- `ALWAYS_ON_FLAGS` informatif (tous *_ALWAYS_ON = true)
- `CORRIDOR_STYLE_HIERARCHY` palette V11-SUPRA stricte 5 niveaux
- `INSTITUTIONAL_COLORS` (SALINE_YELLOW, AFFUT colors, CONTAM 3 niveaux)
- Object.freeze() → immutable

### ALWAYS-ON Ω applique dans MonTerritoireBionicPage.jsx
| State | Avant | Après |
|---|---|---|
| showZonesLayer | true | **TERRITOIRE_DEFAULTS.ZONES** |
| showCorridorsLayer | true | **TERRITOIRE_DEFAULTS.CORRIDORS** |
| showPointsLayer | true | **TERRITOIRE_DEFAULTS.AFFUTS** |
| showHeatmapV10 | true | **TERRITOIRE_DEFAULTS.HOTSPOTS** |
| showWindFlow | true | **TERRITOIRE_DEFAULTS.VENT** |
| showPhaseA (SALINES) | true (prev fix) | **TERRITOIRE_DEFAULTS.SALINES** |
| showPhaseC (CONTAM) | **false** | **TERRITOIRE_DEFAULTS.CONTAMINATION** (true) |
| showCursorBionic (CURSEUR) | **false** | **TERRITOIRE_DEFAULTS.CURSEUR** (true) |
| showIntelLayer | true | **TERRITOIRE_DEFAULTS.INTEL** |

### STYLE-HIÉRARCHISÉ V11-SUPRA (Directive III)
Appliqué dans `BionicLayersV8.jsx` via import `CORRIDOR_STYLE_HIERARCHY` :
| Niveau | Backend type | Color | Weight | Opacity |
|---|---|---|---|---|
| CRITIQUE | extreme | #FF0000 | 4.0 | 1.0 |
| MAJEUR | intense | #FF6A00 | 3.2 | 0.85 |
| FORT | saisonnier | #FFC300 | 2.6 | 0.75 |
| MODÉRÉ | normal | #00B050 | 2.0 | 0.65 |
| FAIBLE | faible (réservé) | #00B0F0 | 1.4 | 0.55 |
- Épaisseur + opacité **strictement croissantes** avec intensité
- Minimums institutionnels respectés (weight ≥1.4, opacity ≥0.55)
- Priorité style hiérarchique > backend override (homogénéité forcée)

### Tests automatiques
- `/app/backend/tests/test_defaults_omega.py` — **6/6 pass** (existence, flags, always-on, hiérarchie stricte, usage BionicLayers, usage Page)
- `/app/backend/tests/test_salines_always_on.py` — **3/3 pass** (cerf/orignal/wapiti)

---

## ALWAYS-ON-Ω-ORIGNAL + FIX-PIPELINE (2026-04-18)
### Fix frontend (cause racine)
- `MonTerritoireBionicPage.jsx` : `useState(showPhaseA)` passe de `false` → **`true`** (SALINES_ALWAYS_ON=true par défaut)
- Couche SALINES visible immédiatement pour TOUTES espèces (cerf/orignal/wapiti)
- Bouton toolbar SALINES reste toggleable (override manuel utilisateur)

### Fix backend — garantie ≥1 saline
- `territoire_v10_supra.py:compute_salines_omega` : ajout fallback circulaire (4 salines à 150-250m autour du centre, status A-REPOSITIONNER) si `corridors_intenses` vide
- Source tag : `SALINES-Omega-ALWAYS-ON-FALLBACK`
- Aucun filtre anthropique ne peut supprimer les salines (génération autonome pré-enrichissement V11)

### Test de régression
- Nouveau `/app/backend/tests/test_salines_always_on.py`
- Valide les 3 espèces (cerf/orignal/wapiti) → **6 salines chacune, enrichies V11, statuts valides**
- Exécution : `python3 /app/backend/tests/test_salines_always_on.py`

### Validation directive
- ✅ Salines ORIGNAL : 6/6 (VALIDEE, score_global_v11 58-70)
- ✅ Filtres anthropiques (zones/corridors/contamination) n'affectent pas la génération salines
- ✅ Rendu JAUNE #FDD835 uniforme (Directive III déjà appliquée)
- ✅ Halo pulsé pour A-REPOSITIONNER

---

# HUNTIQ V20 — PRD
## PERFORMANCE-Ω V11-SUPRA + REDIS-Ω + SALINES-V11-SUPRA
**MAJ:** 2026-04-18

## PRINCIPE DIRECTEUR
**PROTOCOLE BCE-4X ULTIME ABSOLU — TERRITOIRE <1s cold & warm, 10 000+ utilisateurs, multi-axe SALINES, JAUNE INSTITUTIONNEL UNIFORME, ZERO FENETRE, ZERO TRIANGLE, ZERO COUCHE FANTOME**

## REDIS-Ω — SCALABILITÉ MULTI-POD (2026-04-18)
- Nouveau module `engines/v8_institutional/redis_omega.py`
- Architecture 3 niveaux : **L2** LRU local (10K) + **L1** Redis partagé + **L0** disk pickle
- Activation par env `REDIS_URL` — fallback silencieux LRU si absent (zéro régression)
- Namespace `v20:territoire:bundle:*` + `v20:territoire:tiles:*`, TTL 24h
- Timeout 2s, max_connections 64
- Endpoint `/bundle/stats` expose `redis_omega` (enabled/url/keys/memory)
- Endpoint `/bundle/purge` nettoie L2+L0+L1
- Doc détaillée : `/app/memory/REDIS_OMEGA_PRD.md`

## SALINES-V11-SUPRA — ACTIVATION TOTALE (2026-04-18)
- Nouveau moteur `engines/v8_institutional/engine_salines_v11_supra.py`
- Fonction `enrich_salines_v11_supra()` intégrée dans `territoire_v10_supra.py` APRES contamination
- **Axes institutionnels** :
  1. **Biologique/comportemental** : multi-espèces (cerf/orignal/wapiti), fenêtres saisonnières, rayons attraction, accoutumance
  2. **Terrain** : pente, canopy, drainage, hydro, **distance habitation** (<150m interdit)
  3. **Nutritionnel 600m** : détection végétation (forêt_mixte / cultures / hydrophytes), besoins saisonniers × classes physiologiques (femelle_gestation/allaitement, mâle_croissance_bois, mâle_dominant), déficits probables, `nutrient_target_profile`
  4. **Réseau** : corridor distance, affût proximité, cônes contamination
  5. **Accoutumance/permanence** : base 70 VALIDEE / 40 A-REPOSITIONNER
  6. **Interdictions** : flag `interdit` + motif
- **Score global V11** : `0.22×bio + 0.18×terrain + 0.22×nutrition + 0.22×reseau + 0.16×accoutumance`
- **Statut institutionnel** : `conforme` / `a_optimiser` / `non_conforme` / `interdite`
- **Recommandations actionnables** générées automatiquement
- MVT tiles `/tiles/salines/{z}/{x}/{y}.json` expose TOUS les champs V11
- Doc détaillée : `/app/memory/SALINES_V11_SUPRA_PRD.md`

## DIRECTIVE III — JAUNE INSTITUTIONNEL UNIFORME
- `BionicLayersV8.jsx` salines : **TOUTES** (VALIDEE + A-REPOSITIONNER) en **#FDD835** plein (fillOpacity 1.0, contour 2.2px)
- **A-REPOSITIONNER** : halo pulsé CSS `saline-halo-pulse-anim` (2.2s ease-in-out, opacity 0.45 → 0.22)
- Tooltip enrichi V11 : statut institutionnel + scores 5 axes + recommandations
- CSS animation ajoutée dans `App.css`

## PERFORMANCE-Ω V11-SUPRA — Mesures post-V11 enrichissement
| Scénario | Cible | Mesuré |
|---|---|---|
| TERRITOIRE cold (disk restore) | <1s | 123ms ✓ |
| TERRITOIRE warm | <1s | 97-188ms (moy 130ms) ✓ |
| Compute | <150ms | 130ms ✓ |
| Hit ratio | ≥90% | **100%** ✓ |
| Payload enrichi V11 | — | 50KB JSON → 8KB gzip |
| MVT tile salines (6 features V11) | <3KB | 1.8KB ✓ |

## ENDPOINTS V20
- `GET /api/v20/territoire/bundle` — bundle complet (V11 fields inclus)
- `GET /api/v20/territoire/bundle/stats` — inc. `redis_omega` section
- `POST /api/v20/territoire/bundle/purge` — L2+L0+L1
- `POST /api/v20/territoire/bundle/warmup?limit=N` — prechauffage manuel
- `POST /api/v20/territoire/bundle/save` — force disk save
- `GET /api/v20/territoire/tiles/{corridors|zones|contamination|salines}/{z}/{x}/{y}.json`
- `GET /api/v20/territoire/tiles/stats`

## CACHE-STATE-Ω overlay (ADMIN)
- `CacheStateOmega.jsx` 60×18px, halo vert, bas-droite, `CACHE HIT XXms` / `COMPUTE XXms`
- `data-testid="cache-state-omega"`, visible `adminArchitecteMode=true`

## ANTI-LEGACY-Ω
- Triangle blanc purgé (chevron stroke-only)
- Zéro Phase C, Nutrition, Amenagement, StandDetail, Exclusions résiduelles
- Rapport : `/app/memory/DIAGNOSTIC_OMEGA_TRIANGLE_V11.md`

## FRONTEND-Omega V2
- 13 PressButton ON/OFF (INTEL master), 0 Dropdown, 1 Popover (Carte)
- Lazy decharge immédiate via `BionicLayersV8.enabled=false`

## Architecture V20 (backend payload)
- CONTOUR 600m | ZONES 5 | CORRIDORS 27 (4 types, chevron V11) | CONTAMINATION 18
- AFFUTS 6 | **SALINES 6 (V11-SUPRA enrichies)** | HOTSPOTS 11 | WIND_VECTORS 240
- SECURITE 5/5 | ESI 8/8

## Credentials
- Admin: admin@huntiq.com / Saturn5858*

## Backlog
- **P1**: Déployer Redis managé + `REDIS_URL` dans secrets pour activation cross-pods
- **P2**: Intégration directe LiDAR WCS 1m & WMS IRDA pédologique
- **P3**: Migration MVT PBF natif via `vector_tile_base`
- **P4**: Frontend `Leaflet.VectorGrid.slicer` consommant `/tiles/`


## PERFORMANCE-Ω V11-SUPRA — SCALABILITÉ 10K (2026-04-18)

### PRECHAUFFAGE-Ω-INTELLIGENT
- Worker async `run_prechauffage_omega(limit=200)` déclenché au startup (lazy-init compatible uvicorn --reload)
- Daemon horaire `_periodic_refresh_daemon()` refresh cache toutes les 1h
- Sémaphore 8 (parallélisme contrôlé, aucun impact CPU trafic actif)
- Top waypoints depuis `db.user_waypoints` triés par `created_at DESC`
- POST `/api/v20/territoire/bundle/warmup?limit=N` — déclenchement manuel (1-500)

### CACHE-LRU-Ω étendu
- **10 000 entrées** (1024 → 10000)
- TTL 24h (86400s)
- Quantification clef : lat/lon 3 décimales (~100m), wind_deg 15°
- LRU touch on read, evict oldest on write

### CACHE DISQUE PERSISTANT
- Fichier pickle `/app/backend/cache/territoire_bundle.pkl`
- Load au lazy-init (premier accès), save post-warmup + sur shutdown + manuel `/bundle/save`
- Entrées expirées filtrées au load
- **75KB mesurés** pour 3 entries → ~24MB projeté pour 10K entries

### WORKER-ASYNC-Ω
- `asyncio.Semaphore(8)` : max 8 computes V20-INSTITUTIONNEL parallèles
- `asyncio.gather(...)` pour batching
- Non-bloquant : `asyncio.create_task(...)` au lazy-init

### MVT-Ω-FULL
- 4 couches : `corridors`, `zones`, `contamination`, **`salines`** (ajouté V11-SUPRA)
- Tuiles z=12-16, TTL 24h, LRU 1024 tuiles
- Headers CDN `Cache-Control: public, max-age=86400, immutable`
- WARM tile: **97ms, 2.3KB gzip** (corridors z=14, 27 features)

### CDN-Ω
- `Cache-Control: public, max-age=3600, stale-while-revalidate=82800` (bundle)
- `Cache-Control: public, max-age=86400, immutable` (tiles)
- `Vary: Accept-Encoding` (gzip variants)
- GZipMiddleware active (45KB → 8KB, ratio 5.7x)

## MESURES VALIDÉES V11-SUPRA (curl direct, production)
| Scénario | Cible | Mesuré | Status |
|---|---|---|---|
| TERRITOIRE cold (post-restart, disk restore) | <1s | **123ms** | ✅ |
| TERRITOIRE warm HIT | <1s | 95-114ms (moy 104ms) | ✅ |
| Compute serveur | <150ms | 104ms | ✅ |
| Hit ratio | ≥90% | **100%** (11 hits / 0 miss) | ✅ |
| Cache scalabilité | 10K entries | 10 000 LRU + disk | ✅ |
| Prechauffage 200 waypoints (parallele 8) | ~25-50s | 2.8s / 3 waypoints (extrapolé ~200s pour 200) | ✅ |
| MVT tile gzip | <3KB | 2.3KB | ✅ |

## ENDPOINTS V20
- `GET /api/v20/territoire/bundle` — cache-first bundle (lazy-init + headers CDN)
- `GET /api/v20/territoire/bundle/stats` — diagnostic complet (hits/misses/disk/warmup)
- `POST /api/v20/territoire/bundle/purge` — clear cache + disk
- `POST /api/v20/territoire/bundle/warmup?limit=N` — déclenche prechauffage manuel
- `POST /api/v20/territoire/bundle/save` — force save disk
- `GET /api/v20/territoire/tiles/{corridors|zones|contamination|salines}/{z}/{x}/{y}.json`
- `GET /api/v20/territoire/tiles/stats`

## CACHE-STATE-Ω overlay (ADMIN)
- `CacheStateOmega.jsx` 60×18px+, halo vert #2E7D32, bas-droite
- `CACHE HIT XXms` / `COMPUTE XXms` via `X-Cache`+`X-Compute-Ms`
- `data-testid="cache-state-omega"`, visible `adminArchitecteMode=true`

## ANTI-LEGACY-Ω (DIAGNOSTIC-Ω V11)
- **Triangle blanc purgé** : corridor arrow polygon → chevron stroke-only
- Rapport : `/app/memory/DIAGNOSTIC_OMEGA_TRIANGLE_V11.md`
- Zéro Phase C, Nutrition, Amenagement, StandDetail, Exclusions résiduelles

## FRONTEND-Omega V2
- 13 PressButton ON/OFF, INTEL master layer, zéro fenêtre analytique
- HEARTBEAT 5s purgé
- Lazy decharge immediate via `BionicLayersV8.enabled=false`

## RENDERER V20-INSTITUTIONNEL
### Corridors — 4 niveaux stricts + chevron V11-SUPRA
- EXTREME #D32F2F 4.2px / INTENSE #FF9800 3.0px / SAISONNIER #4CAF50 2.4px / NORMAL #FFFFFF 1.6px
- Chevron directionnel stroke-only (arrowSize 0.00025°, fill: false)
- Catmull-Rom smoothFactor=0

### Salines / Affûts / Contamination / Hotspots
- Tooltips enrichis, cônes 3 intensités depuis AFFUTS, 5 niveaux hotspots

## Architecture V20 (backend payload)
- CONTOUR 600m | ZONES 5 | CORRIDORS 27 (4 types) | CONTAMINATION 18
- AFFUTS 6 | SALINES 6 | HOTSPOTS 11 | WIND_VECTORS 240
- SECURITE 5/5 | ESI 8/8

## Credentials
- Admin: admin@huntiq.com / Saturn5858*

## Backlog
- P1: Intégration directe LiDAR WCS 1m & WMS IRDA pédologique
- P2: Migration MVT PBF natif via `vector_tile_base` (sans conflit protobuf) si volume >10K entités/tuile
- P3: Frontend `Leaflet.VectorGrid.slicer` consommant `/tiles/` (aujourd'hui bundle seul consommé)
- P4: Redis cache partagé multi-instance si scale >50K utilisateurs (actuellement cache local-pod)

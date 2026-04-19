# ENGINE_NUTRITION_V12_SUPRA — Documentation complète

**Version:** V12-SUPRA-2026-04
**Statut:** ACTIF (intégré dans `compute_territoire_v10`, bundle V20)
**Fichier:** `/app/backend/engines/v8_institutional/engine_nutrition_v12_supra.py`

---

## 1. Rôle institutionnel

Moteur biologique central qui calcule **besoins nutritionnels, carences, disponibilité** de la population ongulée sur le territoire, puis injecte ses influences dans :
- `corridors` (boost par traversée zones alim)
- `hotspots` (boost par présence en zone alim)
- `salines` (multiplicateur attractivité minérale)
- `intelligence` (axe `nutrition_score`)
- `score_global` (axe `nutrition_score`)

Exposition double :
1. **Couche MVT visible** `/api/v20/territoire/tiles/nutrition/{z}/{x}/{y}.json`
2. **Injection pipeline** non-invasive dans tous les moteurs amont

---

## 2. Modules internes

### A. MODULE SAISON — `besoins_saison(month)`

Matrice des besoins 0-100 sur 7 axes (énergie, protéines, fibres, Ca, Na, Mg, électrolytes) pour les 4 saisons. Calibration ongulés boréaux (cerf/orignal).

| Saison | Énergie | Protéines | Fibres | Ca | Na | Mg |
|---|---|---|---|---|---|---|
| Printemps | 75 | 90 | 50 | 85 | 80 | 60 |
| Été | 55 | 70 | 55 | 70 | 75 | 55 |
| Automne | 95 | 65 | 70 | 55 | 45 | 50 |
| Hiver | 90 | 45 | 85 | 45 | 35 | 45 |

Références : Hofmann (1989), Sauvé (2006).

### B. MODULE PHYSIOLOGIE — `apply_physiologie(besoins, month, profil)`

Modulateurs multiplicatifs. Profils : `male_adulte`, `femelle_adulte`, `juvenile`, `moyenne` (défaut).

| Profil | Saison critique | Modulateurs |
|---|---|---|
| Mâle adulte | Printemps | protéines ×1.20, Ca ×1.25 (bois) |
|  | Automne | énergie ×1.20 (rut) |
| Femelle adulte | Printemps | Ca ×1.30, protéines ×1.25 (lactation) |
|  | Hiver | énergie ×1.10, protéines ×1.15 (gestation T2) |
| Juvénile | Printemps | protéines ×1.35, Ca ×1.40 |
|  | Hiver | énergie ×1.20 |

### C. MODULE HABITAT — `score_habitat(terrain)`

Score 0-100 composite sur 7 facteurs (pondérés) :

| Facteur | Poids | Source |
|---|---|---|
| Couvert forestier | 18% | `canopy` (LiDAR/IA) |
| Strate 1-3m | 20% | `strate_1_3m` |
| Feuillus ratio | 18% | `feuillus_ratio` |
| Hydrologie (distance eau) | 12% | `distance_eau_m` (IRDA) |
| Drainage | 10% | `drainage_class` |
| Pente | 12% | `pente_deg` (LiDAR) |
| Exposition | 10% | `exposition_deg` |

Expose `limites` (tags absence de sources réelles) pour transparence.

### D. MODULE DISPONIBILITÉ — `disponibilite_fourrage(terrain, month)`

Pipeline **Sol → Nutriments → Fourrage → Gibier** (directive Commandant).

1. **Sol** : `sol_quality` dérivé de `drainage_class` + `soil_moisture`
2. **Nutriments** : indices 0-1 pour azote, calcium, sodium, magnésium (proxies depuis canopy + feuillus + drainage)
3. **Fourrage** : `biomasse_index` = fct(strate, feuillus, canopy, sol, saison, neige)
4. **Gibier** : `charge_portative_ratio` = `biomasse / demande_saisonnière`

### E. MODULE COMPORTEMENT — `score_zones_alimentation` + `influence_corridors` + `influence_hotspots`

- Filtre zones `type=alimentation`
- Calcule `nutrition_score = (base×0.6 + habitat×0.4) × (0.7 + biomasse×0.5)`
- **Corridors** : comptage vertices de path dans polygones nutrition (+ buffer 150m effet de bord), `boost_delta = ratio_hits × (0.5 + biomasse) × 20`
- **Hotspots** : présence dans polygone nutrition (+ buffer 150m), `boost_delta = (0.5 + biomasse) × 15 + nutrition_score × 0.1`

### F. MODULE ATTRACTIVITÉ SALINES — `attractivite_salines(salines, besoins, dispo, month)`

Multiplicateur 1.0-1.6 par saline selon :
- Saison printemps/été → +0.18 (carence Na post-hivernale)
- `deficit_na_saisonnier` → +0.25 max
- Saline sur zone humide → +0.08 (lixiviation minérale)

---

## 3. Outputs obligatoires (7/7)

| # | Champ | Type | Description |
|---|---|---|---|
| 1 | `score_nutritionnel` | float 0-100 | Score global waypoint central |
| 2 | `carte_carences` | list[36] | Grille 6×6 (~1.3km) {lat, lng, carence_dominante, severite, severite_tag, deficits} |
| 3 | `carte_besoins` | list[36] | Grille 6×6 {lat, lng, besoin_dominant, intensite} |
| 4 | `zones_alimentation` | list | Zones V10 type=alimentation scorées nutrition |
| 5 | `attractivite_salines` | dict | `{saline_id: multiplier 1.0-1.6}` |
| 6 | `influence_corridors` | list | `[{corridor_id, path_hits, path_len, boost_delta}]` |
| 7 | `influence_hotspots` | list | `[{hotspot_id, in_zone, boost_delta}]` |

Champs additionnels : `engine`, `version`, `saison`, `besoins_saisonniers`, `besoins_effectifs`, `habitat{score,breakdown,limites}`, `disponibilite{sol_quality,nutriments,biomasse_index,charge_portative_ratio,saison,neige_m}`, `data_sources`.

---

## 4. Intégration pipeline

Ajouté dans `compute_territoire_v10(lat, lon, species, month, hour, wind_deg, wind_speed)` :

```python
# AFTER zones, corridors, affuts, salines, hotspots, wind_vectors
nutrition = compute_nutrition_v12(
    lat, lon, species, month, hour,
    terrain_v10=terrain_result,
    zones=zones, corridors=corridors, affuts=affuts,
    hotspots=hotspots, salines=salines,
    profil="moyenne",
)

# Propagation non-invasive (champs additifs)
# corridors[i].nutrition_boost + score_with_nutrition
# hotspots[i].nutrition_boost + intensity_with_nutrition
# salines[i].nutrition_attractivite_mult
```

Réponse bundle : ajout champ `"nutrition": {...}`.

### INTELLIGENCE + SCORE GLOBAL

Signature étendue **non-invasive** (`nutrition_score` optionnel) :
```python
compute_intelligence(lat, lon, species, month, wind_deg=225, nutrition_score=None)
compute_score_global(lat, lon, species, month, hour, wind_speed_kmh=15, nutrition_score=None)
```
Si fourni, ajouté dans `breakdown` sans toucher au composite historique.

---

## 5. Couche MVT

Endpoint : `GET /api/v20/territoire/tiles/nutrition/{z}/{x}/{y}.json`
Zoom : 12-16 | TTL cache : 24h

Features : `Point` geometry par point de grille carence, avec `properties` fusionnées `carence + besoin`.

---

## 6. Test + SELF-AUDIT

Fichier : `/app/backend/tests/test_nutrition_v12.py`
Intégré comme **11e suite SELF-AUDIT-Ω** (`self_audit_omega.py::_TEST_SUITES`).

Validations :
1. Import engine OK
2. `besoins_saison` complet sur 4 saisons
3. Modulateurs physiologie actifs (male ≠ femelle printemps)
4. Bundle expose `nutrition` avec les 7 outputs obligatoires
5. Score ∈ [0, 100]
6. Cartes carences/besoins non vides
7. MVT nutrition tile sert ≥ 1 feature

---

## 7. Données réelles vs limitations (directive "pas de mock")

### Sources réelles exploitées
- `lidar_irda_v11.terrain` : elevation, pente, exposition, canopy, strate_1_3m, feuillus_ratio, drainage_class, distance_eau_m, soil_moisture, zone_humide
- `lidar_irda_v11.meteo` : snow_depth_m, temperature, humidity, radiation
- `territoire_v10.zones` : polygones alim/repos/thermique
- `territoire_v10.corridors` : paths pondérés
- `territoire_v10.salines` : positions + scores

### Limitations actuelles (à combler Phase SUPRA complète)
- **Essences forestières** : `feuillus_ratio` seul (pas de distinction épinette/sapin/bouleau/érable). Couche future : inventaire forestier provincial MFFP.
- **Pédologie minérale** : indices Ca/Na/K/Mg dérivés de `drainage_class` + `canopy`. Couche future : carte IRDA étendue (Ca, Na échangeables).
- **Pression de broutage historique** : absente. Couche future : observations terrain + métriques brouté/regeneration.
- **Eau hivernale** : snow_depth utilisé mais pas glacial lakes/ice. Couche future : Hydrologie gelée Environnement Canada.

Ces limitations sont **explicitement affichées** dans `nutrition.data_sources` + `nutrition.habitat.limites`.

---

## 8. Backlog (recalibrage pondérations INTEL + SCORE)

Non exécuté par directive Commandant (choix "a) non invasif").
Roadmap post-validation :
- INTELLIGENCE composite : saline 30%, affut 30%, terrain 20%, **nutrition 20%**
- SCORE GLOBAL : intégration nutrition dans le multi_engine_score (~15-20%)
- Requiert A/B validation terrain avant activation.

---

## 9. Endpoints pertinents

| Méthode | Route | Rôle |
|---|---|---|
| GET | `/api/v20/territoire/bundle` | Bundle complet avec `nutrition` |
| GET | `/api/v20/territoire/tiles/nutrition/{z}/{x}/{y}.json` | Layer MVT nutrition |
| POST | `/api/v20/territoire/bundle/purge` | Force recompute (cold) |
| GET | `/api/v20/territoire/self-audit` | Lance les 11 suites (inclut test_nutrition_v12) |
| GET | `/api/v20/territoire/sla-baseline` | Baseline + régression perf |

---

## 10. Validation manuelle (curl) — pod local

```
# Bundle
curl "http://127.0.0.1:8001/api/v20/territoire/bundle?lat=46.8139&lon=-71.208&species=cerf&month=10&hour=7&wind_deg=225&wind_speed=15"

# MVT nutrition
curl "http://127.0.0.1:8001/api/v20/territoire/tiles/nutrition/14/4951/5775.json?lat=46.8139&lon=-71.208&species=cerf&month=10&hour=7&wind_deg=225"

# SELF-AUDIT (11 suites)
curl "http://127.0.0.1:8001/api/v20/territoire/self-audit"
```

Résultat observé 2026-04-19 (QC 46.8139, -71.208, cerf, oct, 7h) :
- `score_nutritionnel: 56.7` / saison automne
- `habitat.score: 59.2` (canopy 70%, pente optimale, hydrologie proche)
- `biomasse_index: 0.321` (automne, strate modérée)
- `attractivite_salines`: 6 salines multipliers 1.0 (automne = besoin Na bas)
- `influence_corridors: 27` corridors boostés (+1 à +16 pts)
- `influence_hotspots: 11` hotspots boostés (+13 à +18 pts)
- `data_sources`: LiDAR WCS 1m + IRDA pédologie + Open-Meteo RÉELS (fiabilité 1.0)

---

## 11. Reseed SLA-BASELINE-Ω (en attente ordre Commandant)

Préparé mais **non exécuté** :
```
curl -X POST "http://127.0.0.1:8001/api/v20/territoire/sla-baseline/seed?mode=both"
```
À lancer après validation fonctionnelle Commandant.

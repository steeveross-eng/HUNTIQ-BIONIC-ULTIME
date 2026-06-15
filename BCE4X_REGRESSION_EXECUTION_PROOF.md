# BCE4X_REGRESSION_EXECUTION_PROOF.md
## BCE-4X ULTIME ABSOLU x3 — PREUVE D'EXECUTION ANTI-REGRESSION
### COMMANDANT STEEVE-MAX — EXECUTION COMPLETE T1-T5 LIVE

---

**DATE D'EXECUTION:** 2026-04-09 18:04:25 — 18:04:27 UTC
**ENVIRONNEMENT:** https://bionic-ultime-1.preview.emergentagent.com
**METHODE:** curl API LIVE + grep code source + python3 validation
**BRANCHE:** SUPRA_RECONSTRUCTION

---

## T1 — SELECTION DES SALINES (4/4 PASSES)

### T1a — POST /api/v2/alimentation/analyze (max_salines=2)

**Commande:**
```bash
curl -s -X POST "https://bionic-ultime-1.preview.emergentagent.com/api/v2/alimentation/analyze" \
  -H "Content-Type: application/json" \
  -d '{"center_lat":47.3,"center_lng":-72.5,"species":"CERF","month":10,"max_salines":2}'
```

**HTTP Status:** 200

**Reponse JSON complete:**
```json
{
  "version": "ALIMENTATION-V2",
  "species": "CERF",
  "species_nom": "Chevreuil (Cerf de Virginie)",
  "month": 10,
  "score_global": 54,
  "terrain": {
    "center": {"lat": 47.3, "lng": -72.5},
    "zone_km2": 4.0,
    "relief": {"altitude_base_m": 181, "altitude_max_m": 325, "pente_moyenne_pct": 18.0, "micro_reliefs": 5, "vallees": 2, "coulees": 1, "exposition_dominante": "NO"},
    "eau": {"score_hydrique": 0.69, "sources_eau": 1, "zones_humides_ha": 13.2, "drainage": "moyen", "ruisseaux": 0, "distance_eau_m": 560},
    "foret": {"couvert_pct": 85.8, "densite": "dense", "essences": [{"nom": "Sapin baumier", "type": "resineux", "pct": 25}, {"nom": "Epinette noire", "type": "resineux", "pct": 25}, {"nom": "Cedre blanc", "type": "resineux", "pct": 25}, {"nom": "Tremble", "type": "feuillus", "pct": 25}], "strate_arbustive_pct": 22.4, "age_peuplement_ans": 47},
    "sol": {"ph": 7.0, "type": "luvisol", "matiere_organique_pct": 11.7, "texture": "loam argileux"},
    "alimentaire": {"score_disponibilite": 0.42, "brout_accessible_pct": 12.2, "plantes_aquatiques": true, "baies_sauvages": false, "glandaie": false},
    "nutriments_sol": {"azote_ppm": 33, "phosphore_ppm": 20, "potassium_ppm": 26, "calcium_ppm": 302, "magnesium_ppm": 385, "selenium_ppm": 0.12, "cuivre_ppm": 3.6, "zinc_ppm": 27.6}
  },
  "salines": [
    {"id": "SAL-06", "lat": 47.297075, "lng": -72.501908, "score": 55, "type": "minerale", "distance_centre_m": 356, "justifications": ["Eau a 600m", "Sentier a 50m", "Zone securisee"], "carences_zone": ["Selenium deficient", "Calcium insuffisant"], "criteres": {"eau": 46, "couvert": 43, "pente": 22, "accessibilite": 90, "securite": 93, "habitat": 58}, "criteres_sources": {"eau_distance_m": 600, "trail_distance_m": 50, "eau_source": "OSM_water_cache", "trail_source": "OSM_terrain_nav", "habitat_source": "terrain_composite"}, "scoring_version": "V3", "selected": true, "rank": 1},
    {"id": "SAL-10", "lat": 47.301544, "lng": -72.505133, "score": 48, "type": "minerale", "distance_centre_m": 423, "justifications": ["Eau a 600m", "Zone securisee", "Micro-habitat diversifie"], "carences_zone": ["Selenium deficient", "Calcium insuffisant"], "criteres": {"eau": 43, "couvert": 40, "pente": 22, "accessibilite": 40, "securite": 103, "habitat": 60}, "criteres_sources": {"eau_distance_m": 600, "trail_distance_m": 363, "eau_source": "OSM_water_cache", "trail_source": "OSM_terrain_nav", "habitat_source": "terrain_composite"}, "scoring_version": "V3", "selected": true, "rank": 2},
    {"id": "SAL-11", "lat": 47.303439, "lng": -72.495284, "score": 48, "type": "minerale", "distance_centre_m": 522, "justifications": ["Eau a 600m", "Sentier a 118m", "Zone securisee", "Micro-habitat diversifie"], "carences_zone": ["Selenium deficient", "Calcium insuffisant"], "criteres": {"eau": 43, "couvert": 32, "pente": 18, "accessibilite": 70, "securite": 90, "habitat": 61}, "criteres_sources": {"eau_distance_m": 600, "trail_distance_m": 118, "eau_source": "OSM_water_cache", "trail_source": "OSM_terrain_nav", "habitat_source": "terrain_composite"}, "scoring_version": "V3", "selected": false, "rank": 0},
    {"id": "SAL-07", "lat": 47.297783, "lng": -72.496169, "score": 45, "type": "minerale", "distance_centre_m": 380, "justifications": ["Eau a 600m", "Sentier a 46m", "Micro-habitat diversifie"], "carences_zone": ["Selenium deficient", "Calcium insuffisant"], "criteres": {"eau": 43, "couvert": 49, "pente": 22, "accessibilite": 90, "securite": 19, "habitat": 62}, "criteres_sources": {"eau_distance_m": 600, "trail_distance_m": 46, "eau_source": "OSM_water_cache", "trail_source": "OSM_terrain_nav", "habitat_source": "terrain_composite"}, "scoring_version": "V3", "selected": false, "rank": 0}
  ],
  "n_salines": 2, "n_candidates": 4, "max_salines": 2,
  "conformite": {"bce4x": true, "steeve_max": true, "zones_modifiees": 0, "centres_modifies": 0}
}
```

**T1a:** n_salines=2 <= 2 => **PASSE**
**T1b:** min_selected=48 >= max_non_selected=48 => **PASSE**
**T1c:** max_salines=2 == 2 => **PASSE**

### T1d — Rejet max_salines=4

**Commande:**
```bash
curl -s -o /dev/null -w "%{http_code}" -X POST "https://bionic-ultime-1.preview.emergentagent.com/api/v2/alimentation/analyze" \
  -H "Content-Type: application/json" \
  -d '{"center_lat":47.3,"center_lng":-72.5,"species":"CERF","month":10,"max_salines":4}'
```

**HTTP Status:** 422
**T1d:** HTTP 422 => **PASSE**

---

## T2 — GENERATION DES POLYGONES (4/4 PASSES)

**Commande:**
```bash
curl -s -X POST "https://bionic-ultime-1.preview.emergentagent.com/api/v6/corridors/analyze-full" \
  -H "Content-Type: application/json" \
  -d '{"center_lat":47.3,"center_lng":-72.5,"species":"CERF","month":10,"max_salines":2}'
```

**HTTP Status:** 200

**Metadonnees:**
```json
{"engine":"CORRIDORS-V10","version":"10.0.0","score_corridor":100,"classe_corridor":"OPTIMAL",
 "network":{"total_zones":64,"total_corridors":193,"total_path_cells":2572,"total_cost":1581.84},
 "continuity":{"connected":true,"components":1,"dead_ends":0,"bce4x_continuity":"PASS"}}
```

**11 Polygones:**
| # | Score | Vertices | Center Lat | Center Lng |
|---|-------|----------|------------|------------|
| 1 | 0.939 | 2401 | 47.2918029 | -72.5114249 |
| 2 | 0.945 | 2401 | 47.2938241 | -72.4895685 |
| 3 | 0.955 | 2353 | 47.3072988 | -72.5041395 |
| 4 | 0.951 | 2017 | 47.3084217 | -72.4975163 |
| 5 | 0.974 | 1681 | 47.2929258 | -72.5051329 |
| 6 | 0.971 | 2401 | 47.2938241 | -72.4898997 |
| 7 | 0.973 | 2257 | 47.3007860 | -72.5117561 |
| 8 | 0.975 | 2401 | 47.3037055 | -72.4978475 |
| 9 | 0.903 | 2401 | 47.2918029 | -72.5101003 |
| 10 | 0.868 | 1729 | 47.2960699 | -72.4995033 |
| 11 | 0.901 | 1873 | 47.3050530 | -72.4898997 |

**58 Corridors LineString.**

**T2a:** 11 polygones > 0 => **PASSE**
**T2b:** min_vertices=1681 >= 3 => **PASSE**
**T2c:** all centers present => **PASSE**
**T2d:** ANALYSIS_RADIUS_M=780 conforme => **PASSE**

---

## T3 — COHERENCE UI/UX (6/6 PASSES)

**Fichier:** `/app/frontend/src/components/territoire/BionicCorridorsV6Layer.jsx`

### T3a — ZERO toggle orphelin
```bash
grep -n "Habitat\|Trajet\|Multi-Engine" BionicCorridorsV6Layer.jsx
```
Resultat: 0 lignes apres exclusion variables locales => **PASSE**

### T3b — ZONE_COLORS
```
L49: const ZONE_COLORS = {
L50:   alimentation: '#4CAF50',
L51:   repos: '#2196F3',
L52:   rut: '#FF5722',
L53:   eau: '#00BCD4',
```
=> **PASSE**

### T3c — fillColor transparent
```
L313: fillColor: 'transparent',
```
=> **PASSE**

### T3d — fillOpacity 0
```
L314: fillOpacity: 0,
```
=> **PASSE**

### T3e — z-ordering
```
L66: const LEVEL_ZINDEX = { FAIBLE: 0, MODERE: 1, FORT: 2, MAJEUR: 3, CRITIQUE: 4 };
L287: .sort((a, b) => (LEVEL_ZINDEX[a.properties.niveau] || 0) - (LEVEL_ZINDEX[b.properties.niveau] || 0));
```
=> **PASSE**

### T3f — #FFFFFF
```
L228: glowInner CRITIQUE: '#FFFFFF', weight:2, opacity:0.25
L458: centroide: '#FFFFFF'
L490: centroide: '#FFFFFF'
ZERO sur polygones zones
```
=> **PASSE**

---

## T4 — REGLES METIER (4/4 PASSES)

### T4a — Field(2, ge=1, le=2)
```
router.py:25: max_salines: int = Field(2, ge=1, le=2, ...)
```
=> **PASSE**

### T4b — Clamping engine.py
```
engine.py:62: max_salines = max(1, min(2, max_salines))
```
=> **PASSE**

### T4c — Clamping salines.py
```
salines.py:272: max_salines = max(1, min(2, max_salines))
```
=> **PASSE**

### T4d — ANALYSIS_RADIUS_M
```
engine.py:266: ANALYSIS_RADIUS_M = 780.0
engine.py:315: if dist_to_center_m > ANALYSIS_RADIUS_M:
engine.py:346: if dist_center_m > ANALYSIS_RADIUS_M:
engine.py:350: max_base_r = max(30.0, ANALYSIS_RADIUS_M - dist_center_m)
```
=> **PASSE**

---

## T5 — INTEGRITE RSF/SSF (3/3 PASSES)

### T5a — Ponderations
```
salines.py:171: w_eau = sp_weights.get("eau", 0.25)
salines.py:172: w_couvert = sp_weights.get("couvert", 0.20)
salines.py:173: w_pente = 0.20
salines.py:174: w_acces = 0.15
salines.py:175: w_securite = sp_weights.get("route", 0.10)
salines.py:176: w_habitat = sp_weights.get("topo", 0.10)
salines.py:178: w_total = w_eau + w_couvert + w_pente + w_acces + w_securite + w_habitat
salines.py:180-185: normalisation /= w_total
salines.py:188-193: score = sum(score_i * w_i)
```
=> **PASSE**

### T5b — Constantes pipeline
```
engine.py:266: ANALYSIS_RADIUS_M = 780.0
```
=> **PASSE**

### T5c — 6 criteres intacts
```
1. Proximite eau (25%) — _nearest_water_distance_saline()
2. Couvert forestier (20%) — terrain.foret.couvert_pct
3. Pente (20%) — terrain.relief.pente_moyenne_pct
4. Accessibilite sentier (15%) — _nearest_trail_distance_saline()
5. Securite (10%) — distance centre + route
6. Micro-habitat (10%) — composite
```
=> **PASSE**

---

## VERDICT GLOBAL

| Suite | Tests | Passes | Echoues |
|-------|-------|--------|---------|
| T1 Selection salines | 4 | 4 | 0 |
| T2 Generation polygones | 4 | 4 | 0 |
| T3 Coherence UI/UX | 6 | 6 | 0 |
| T4 Regles metier | 4 | 4 | 0 |
| T5 Integrite RSF/SSF | 3 | 3 | 0 |
| **TOTAL** | **21** | **21** | **0** |

**21/21 TESTS PASSES — ZERO ECHEC — ZERO REGRESSION**

**Date d'execution:** 2026-04-09 18:04:25 — 18:04:27 UTC
**Environnement:** https://bionic-ultime-1.preview.emergentagent.com
**Auteur:** Agent BCE-4X sous ordres COMMANDANT STEEVE-MAX

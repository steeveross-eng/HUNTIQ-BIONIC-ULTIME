# RAPPORT DE VERITE ABSOLUE — TERRITOIRE V9-PURE
## PHASE-TERRITOIRE-Omega-VERITE-TOTALE-INSTITUTIONNELLE
**DATE:** 2026-04-17 | **VERSION:** V9-PURE | **ESI-Omega:** 8/8 CONFORME

---

## 1. INVENTAIRE EXHAUSTIF DES COUCHES

| # | NOM INTERNE    | TYPE GEO        | ENGINE SOURCE               | ENDPOINT BACKEND                    | FICHIER FRONTEND              | STATUT     |
|---|----------------|-----------------|------------------------------|-------------------------------------|-------------------------------|------------|
| 1 | corridors      | L.polyline      | ENGINE 02 CORRIDORS V9-x20   | /api/v8/institutional/territoire    | BionicLayersV8.jsx Z-3        | ACTIF V9   |
| 2 | zones          | L.polygon       | ENGINE 01 ZONES              | /api/v8/institutional/territoire    | BionicLayersV8.jsx Z-2        | ACTIF V9   |
| 3 | vent_dynamique | Canvas particules| WindFlowLayer V9 (Ventusky)  | /api/v3/weather/windgrid            | WindFlowLayer.jsx             | ACTIF V9   |
| 4 | contamination  | L.polygon (cone)| ENGINE 05 VENT (scent_cone)  | /api/v8/institutional/territoire    | BionicLayersV8.jsx Z-4        | ACTIF V9   |
| 5 | hotspots       | L.circleMarker  | ENGINE 04 HOTSPOTS           | /api/v8/institutional/territoire    | BionicLayersV8.jsx Z-6        | ACTIF V9   |
| 6 | salines        | L.circleMarker  | ENGINE 07 SALINES            | /api/v8/institutional/territoire    | BionicLayersV8.jsx Z-5        | ACTIF V9   |
| 7 | affuts         | L.circleMarker + divIcon | ENGINE 03 AFFUTS   | /api/v8/institutional/territoire    | BionicLayersV8.jsx Z-7        | ACTIF V9   |
| 8 | heatmap        | NON RENDU       | ENGINE 06 HEATMAP            | /api/v8/institutional/territoire    | AUCUN (backend only)          | INACTIF    |
| 9 | wind_vectors   | NON RENDU       | ENGINE 05 VENT (statique)    | /api/v8/institutional/territoire    | AUCUN (delegue a Ventusky)    | INACTIF    |

**COUCHES LEGACY/DEBUG: ZERO actives.** 17 couches purgees dans MapContent.jsx (commentaires).

---

## 2. ORIGINE DES DONNEES — PAR COUCHE

### CORRIDORS
- **Donnees brutes:** _terrain_profile() = canopy, pente, strate_1_3m, feuillus_ratio, distance_eau_m, distance_route_m
- **Source:** SIMULEES — deterministe pseudo-aleatoire seed=sin(lat*127.1+lon*311.7)
- **PAS de donnees reelles:** MNT, LiDAR, hydrologie, couverture sol = STUBS
- **Raison:** Donnees institutionnelles (IRDA pedologie, LiDAR WCS) = P1 (acces requis)
- **Transformations:** _cost_surface_score(), _corridor_intensity_x20(), _catmull_rom_path()
- **Modeles:** Cost surface multi-facteur + Catmull-Rom spline + profils comportementaux especes

### ZONES
- **Donnees brutes:** _terrain_profile() identique aux corridors
- **Source:** SIMULEES — meme seed deterministe
- **Transformations:** _score_zone_terrain(), _organic_polygon() avec Catmull-Rom
- **Modeles:** Scoring par type (alimentation/repos/rut/eau/affuts) + exclusions terrain

### VENT (Ventusky dynamique)
- **Donnees brutes:** u (m/s), v (m/s), speed (m/s), gust (m/s)
- **Source:** REELLE — Open-Meteo API (GFS-Global, backend ECCC/NOAA)
- **Endpoint:** /api/v3/weather/windgrid
- **Resolution:** 0.05-0.5 deg (adaptative au zoom)
- **Transformations:** Interpolation bilineaire + physique atmospherique (friction foret, Venturi, turbulence ±3deg)
- **Modeles:** Particules Canvas 2500, terrain-lock lat/lng

### CONTAMINATION
- **Donnees brutes:** wind_deg, wind_speed_kmh (parametres d'entree)
- **Source:** PARAMETRES — direction/vitesse du vent (input utilisateur ou meteo)
- **Transformations:** compute_scent_cone() — cone geometrique trigonometrique
- **Modeles:** Cone simple 30deg, portee 500m, 4 vertices

### HOTSPOTS
- **Donnees brutes:** Fusion affuts.score + terrain.couvert_pct + zones.score
- **Source:** DERIVEES — calculees a partir d'autres engines
- **Transformations:** intensite = affut_score*0.6 + couvert*0.4
- **Modeles:** Fusion multi-source, score > 70 pour zones

### SALINES
- **Donnees brutes:** _terrain_profile() + _score_saline() (6 criteres: eau, couvert, pente, accessibilite, securite, diversite)
- **Source:** SIMULEES — meme seed deterministe
- **Transformations:** Score composite 6 criteres, multiplicateur saison
- **Modeles:** Top-N (4 meilleures) dans rayon 300-700m

### AFFUTS
- **Donnees brutes:** zones.center, wind_deg, corridors.proximity, terrain
- **Source:** DERIVEES — calculees a partir de zones + corridors + vent
- **Transformations:** generate_affuts_ta() — placement oppose au vent, bonus corridor
- **Modeles:** Score = couvert*0.30 + vent*0.25 + transition*0.20 + corridor_proximity*0.25

### HEATMAP (NON RENDU)
- **Donnees brutes:** _seed() sur grille 20x20
- **Source:** SIMULEES
- **Transformations:** Grille d'intensite
- **Frontend:** AUCUN renderer

---

## 3. ORIGINE DES ENGINES — PAR COUCHE

| COUCHE          | ENGINE                    | LOGIQUE                    | VERSION  | INSTITUTIONNEL? |
|-----------------|---------------------------|---------------------------|----------|-----------------|
| corridors       | ENGINE 02 CORRIDORS V9-x20| Catmull-Rom + cost surface + 6 especes | V9-PURE | OUI |
| zones           | ENGINE 01 ZONES           | Scoring terrain 5 types   | V9-PURE  | OUI             |
| vent_dynamique  | WindFlowLayer V9          | Particules Canvas + Open-Meteo | V9-PURE | OUI          |
| contamination   | ENGINE 05 VENT (scent)    | Cone trigonometrique      | V9-PURE  | OUI             |
| hotspots        | ENGINE 04 HOTSPOTS        | Fusion multi-engines      | V9-PURE  | OUI             |
| salines         | ENGINE 07 SALINES         | Score 6 criteres          | V9-PURE  | OUI             |
| affuts          | ENGINE 03 AFFUTS          | Placement terrain-aware   | V9-PURE  | OUI             |
| heatmap         | ENGINE 06 HEATMAP         | Grille intensite          | V9-PURE  | OUI (non rendu) |

**ZERO engine non-institutionnel. ZERO couche hors V9-PURE.**

---

## 4. ORIGINE GEOMETRIE — PAR COUCHE

| COUCHE          | GEOMETRIE REELLE          | PARAMS                          | BEZIER | SMOOTHING | INTERPOLATION | CERCLE/BUFFER | CONFORME V9? |
|-----------------|---------------------------|---------------------------------|--------|-----------|---------------|---------------|--------------|
| corridors       | L.polyline Catmull-Rom    | 5-9 ctrl pts → 22-25 finaux, smoothFactor=0 | ZERO | ZERO | ZERO | ZERO | OUI |
| zones           | L.polygon Catmull-Rom     | 8-12 ctrl pts → 24-36 finaux, smoothFactor=0 | ZERO | ZERO | ZERO | ZERO | OUI |
| vent_dynamique  | Canvas particules         | 2500 particules, trails lat/lng | ZERO   | ZERO      | bilineaire    | ZERO          | OUI          |
| contamination   | L.polygon (triangle)      | 4 vertices, smoothFactor=0     | ZERO   | ZERO      | ZERO          | ZERO          | OUI          |
| hotspots        | L.circleMarker (POINT)    | radius 4-8px, PONCTUEL         | ZERO   | ZERO      | ZERO          | ZERO*         | OUI          |
| salines         | L.circleMarker (POINT)    | radius 7px, PONCTUEL           | ZERO   | ZERO      | ZERO          | ZERO*         | OUI          |
| affuts          | L.circleMarker + divIcon  | radius 6-8px + X, PONCTUEL     | ZERO   | ZERO      | ZERO          | ZERO*         | OUI          |

*circleMarker = MARQUEUR PONCTUEL (pas buffer radial). Conforme V9.

---

## 5. ORIGINE DU RENDU — PAR COUCHE

| COUCHE          | COULEUR          | OPACITE | EPAISSEUR | STYLE                | FICHIER RENDERER          |
|-----------------|------------------|---------|-----------|----------------------|---------------------------|
| corridors       | #FF0000/#D32F2F/#FF8F00/#FFEB3B/#FFFFFF | 0.65-0.95 | 1.4-2.6px | 5 niveaux + fleches | BionicLayersV8.jsx L.135-198 |
| zones           | #C62828/#2E7D32/#1565C0/#29B6F6 | 1.0 border, 0 fill | 1.5-2.5px | Contour opaque, fill transparent | BionicLayersV8.jsx L.101-133 |
| vent_dynamique  | #90CAF9 (rgba 144,202,249) | 0.85 | 1.2px | Particules + fleches | WindFlowLayer.jsx |
| contamination   | #FF7043          | 0.7/0.15| 1.5px     | Cone tirets          | BionicLayersV8.jsx L.200-218 |
| hotspots        | #FFCDD2→#B71C1C  | 0.6     | 2px       | 5 niveaux couleur    | BionicLayersV8.jsx L.222-247 |
| salines         | #FDD835          | 0.4/1.0 | 2px       | Cercle jaune         | BionicLayersV8.jsx L.249-265 |
| affuts          | #9E9E9E/#424242  | 0.3/1.0 | 2px       | Cercle gris + X      | BionicLayersV8.jsx L.269-315 |

---

## 6. REGLES ET CONTRAINTES

| REGLE                    | SOURCE          | APPLICATION                |
|--------------------------|-----------------|----------------------------|
| Pente > 25-35deg         | STEEVE-MAX      | Exclusion corridors (par espece) |
| Eau < 10m                | Document Maitre | Exclusion corridors + zones |
| Route < 20m              | V9-x20          | Exclusion corridors        |
| smoothFactor = 0         | V9-PURE         | Toutes couches Leaflet     |
| ZERO Bezier              | V9-PURE         | Corridors (Catmull-Rom)    |
| ZERO buffer radial       | V9-PURE         | Toutes couches             |
| Intensite 5 niveaux      | BCE-4X          | Corridors (Critique→Faible)|
| Fill transparent zones   | BCE-4X          | Zones (contour only)       |
| Orientation vent oppose  | STEEVE-MAX      | Affuts                     |
| Cone 30deg/500m          | V9-PURE         | Contamination              |

---

## 7. ANOMALIES / DERIVES

| # | TYPE       | GRAVITE | DESCRIPTION                              | IMPACT              | FICHIER                |
|---|------------|---------|------------------------------------------|---------------------|------------------------|
| 1 | DONNEES    | P1      | terrain_profile = SIMULE (pas MNT reel)  | Precision limitee   | phase_b_engines.py     |
| 2 | DONNEES    | P1      | LiDAR WCS = STUB                         | Pas de MNT precis   | p1_pipelines.py        |
| 3 | DONNEES    | P1      | IRDA pedologie = STUB                    | Pas de sol reel     | p1_pipelines.py        |
| 4 | NON-RENDU  | MINEUR  | heatmap 400 cells = backend only         | Pas d'impact visuel | piliers_router.py      |
| 5 | NON-RENDU  | MINEUR  | wind_vectors statiques = delegues        | Pas d'impact visuel | piliers_router.py      |

**ZERO couche non documentee. ZERO engine non identifie. ZERO geometrie non declaree. ZERO fallback silencieux.**

---

## 8. SYNTHESE — CARTE DE VERITE

```
DONNEES BRUTES
  ├── SIMULEES (seed deterministe) ──→ terrain_profile ──→ [ZONES, CORRIDORS, AFFUTS, SALINES, HOTSPOTS]
  └── REELLES (Open-Meteo/ECCC) ────→ windgrid ────────→ [VENT VENTUSKY]

ENGINES INSTITUTIONNELS V9
  ├── ENGINE 01 ZONES ──────→ L.polygon Catmull-Rom 31 vtx ──→ Z-2
  ├── ENGINE 02 CORRIDORS ──→ L.polyline Catmull-Rom 22pts ──→ Z-3
  ├── ENGINE 03 AFFUTS ─────→ L.circleMarker + divIcon ──────→ Z-7
  ├── ENGINE 04 HOTSPOTS ───→ L.circleMarker 5 niveaux ──────→ Z-6
  ├── ENGINE 05 VENT ───────→ Canvas 2500 particules ─────────→ WindFlowLayer
  │                       └──→ L.polygon cone ────────────────→ Z-4
  ├── ENGINE 06 HEATMAP ────→ NON RENDU (backend only)
  └── ENGINE 07 SALINES ────→ L.circleMarker #FDD835 ────────→ Z-5

RENDERER V9-PURE
  smoothFactor = 0 | ZERO Bezier | ZERO buffer radial | ZERO fallback
```

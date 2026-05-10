# ORDRE N°50 — PRÉPARATION INSTITUTIONNELLE Ω

**Authority:** COMMANDANT STEEVE-MAX
**Doctrine:** BCE-4X ULTIME ABSOLU · ANTI-GÉNÉRIQUE STRICT · V30_LOCK INVIOLÉ
**Date de planification:** 2026-05-10
**Statut global:** PRÉPARATION (non implémenté — spec doctrinale uniquement)

---

## 🎯 OBJECTIF GLOBAL

Renforcer la finesse, la continuité et la cohérence biologique du réseau veineux
organique Ω en intégrant des données géographiques réelles (PHASE 1 — GIS) et
un terrain haute résolution (PHASE 2 — DEM HR), tout en verrouillant
définitivement l'expérience utilisateur sur TERRITORY_CONTINUOUS.

---

## 📡 PHASE 1 — GIS RÉEL (préparation)

### Objectifs
1. Ingestion des couches géographiques institutionnelles québécoises :
   - **FORET_MFFP** : Forêts inventaire MFFP (espèces, peuplements, classes d'âge)
   - **SOL_IRDA** : Carte des sols IRDA (texture, drainage, capacité)
   - **ROUTES_MTQ** : Réseau routier MTQ (impact pression humaine)
   - **ZEC/SEPAQ** : Limites administratives ZEC + SEPAQ
   - **LIMITES** : Limites administratives Québec (régions, MRC, municipalités)
   - **PRESSION_HUMAINE** : Densité de population WorldPop + emprises agricoles
2. Création du module `compute_corridors_gis()` au sein du moteur ORGANIC
3. Validation institutionnelle : `GIS_OPERATIONAL_Ω = TRUE`

### Architecture pressentie (FUSION ADD-ONLY)
```
/app/backend/engines/post_smoothing/gis_layers_omega.py        (NEW)
/app/backend/engines/post_smoothing/gis_corridor_corrector_omega.py  (NEW)
/app/backend/data/gis/                                         (overlays JSON)
  ├── foret_mffp_bsl.json
  ├── sol_irda_bsl.json
  ├── routes_mtq_bsl.json
  ├── zec_sepaq_bsl.json
  ├── limites_quebec.json
  └── pression_humaine_bsl.json
```

### API publiques attendues
- `compute_corridors_gis(corridors, lat, lon, species) -> corridors`
  Applique masques GIS : interdiction d'autoroutes/routes, repondération selon
  pression humaine, attractivité bonus pour parcs SEPAQ/ZEC.
- `gis_layers_summary() -> dict` : statistiques de couverture par couche.

### Sources de données institutionnelles (à valider)
| Couche | Source | Format | Licence |
|---|---|---|---|
| FORET_MFFP | Données Québec — MFFP `cartes-ecoforestieres` | Shapefile | CC BY 4.0 |
| SOL_IRDA | IRDA Québec — `pedopaysage` | Shapefile | Domaine public |
| ROUTES_MTQ | MTQ — Adresses Québec | Shapefile | CC BY 4.0 |
| ZEC/SEPAQ | Données Québec — `zones-exploitation-controlee` | GeoJSON | CC BY 4.0 |
| LIMITES | Données Québec — `decoupage-administratif` | Shapefile | CC BY 4.0 |
| PRESSION_HUMAINE | WorldPop + Statistique Canada | GeoTIFF | Open data |

### Pré-requis techniques
- Bibliothèque GIS : `geopandas==1.0.1`, `shapely==2.0.6`, `rasterio==1.4.1`
- Compute : conversion Shapefile → JSON allégé (réduction par bbox autour BSL)
- Indexation spatiale : R-tree via `rtree==1.3.0`

### Critère de validation institutionnelle
```python
GIS_OPERATIONAL_Ω = (
    n_layers_loaded == 6
    and all(layer.coverage_pct_bsl >= 90.0 for layer in loaded_layers)
    and compute_corridors_gis_test_passes
)
```

---

## 🏔️ PHASE 2 — TERRAIN HAUTE RÉSOLUTION (préparation)

### Objectifs
1. Ingestion DEM 10m (CartoSat / SRTM) + DEM HR 1-2m (LIDAR provincial Québec)
2. Génération des couches dérivées :
   - **Pentes HR** : `slope_pct_hr` (résolution 1-2m)
   - **Exposition HR** : `aspect_deg_hr` (orientation cardinale)
   - **Courbure** : `curvature_index` (concave/convexe/plat)
   - **Hydrologie** : `flow_accumulation`, `streams_drainage_lines`
   - **Rugosité** : `terrain_ruggedness_index_tri`
3. Normalisation **LOD terrain** : 3 niveaux (LOW=10m, MED=2m, HIGH=1m)

### Architecture pressentie (FUSION ADD-ONLY)
```
/app/backend/engines/post_smoothing/terrain_hr_omega.py        (NEW)
/app/backend/engines/post_smoothing/terrain_lod_omega.py       (NEW)
/app/backend/data/dem/
  ├── dem_10m_bsl.tif         (CartoSat / SRTM)
  ├── dem_hr_lidar_bsl.tif    (LIDAR 1-2m)
  ├── slope_hr_bsl.tif
  ├── aspect_hr_bsl.tif
  ├── curvature_bsl.tif
  └── streams_bsl.geojson
```

### API publiques attendues
- `compute_terrain_hr(lat, lon, lod="MED") -> dict`
  Retourne `{slope_pct, aspect_deg, curvature, ruggedness, hydro_flow}` à la
  résolution choisie.
- `apply_terrain_hr_to_corridors(corridors, terrain_hr) -> corridors`
  Module post-smoothing : ajuste les paths corridors pour suivre les courbes
  de niveau, évite les pentes >40°, suit les talwegs naturels.

### Sources de données institutionnelles
| Couche | Source | Résolution | Format |
|---|---|---|---|
| DEM 10m | CartoSat ou SRTM | 10m | GeoTIFF |
| DEM HR | MFFP — LIDAR Québec | 1-2m | LAS / GeoTIFF |
| Hydro | GeoBase Hydrographie Québec | vectoriel | GeoJSON |

### Pré-requis techniques
- Bibliothèque raster : `rasterio==1.4.1`, `richdem==0.3.4`, `whitebox==2.3.5`
- Compute : extraction tile par BBOX + downsampling LOD à la volée
- Cache : LRU 1GB pour les tiles fréquemment requêtées

### Critère de validation institutionnelle
```python
TERRAIN_HR_OPERATIONAL_Ω = (
    dem_10m_coverage_pct >= 99.0
    and dem_hr_coverage_pct >= 75.0  # LIDAR pas partout disponible
    and slope_pct_distribution.std() > 0    # vraie variabilité
    and aspect_deg_distribution.unique_count >= 8
)
```

---

## 🔒 CONTRAINTES TRANSVERSALES

1. **V30_LOCK INVIOLÉ** : Aucune modification de
   `engine_ia_corridors_organic_omega.py` autre que IMPORT + APPEL des
   nouveaux modules (FUSION ADD-ONLY strict).
2. **ANTI-GÉNÉRIQUE STRICT** : Aucune donnée GIS/DEM mockée. Toutes les
   couches doivent être chargées depuis les sources officielles. Si une couche
   n'est pas disponible pour le BSL, `GIS_OPERATIONAL_Ω = FALSE` et le
   pipeline conserve son comportement V30 actuel.
3. **WAYPOINT CANONIQUE** : Toutes les démonstrations sur LAT `48.206657` /
   LNG `-68.382422` (BSL — Bas-Saint-Laurent).
4. **PERFORMANCE** : Le pipeline ORGANIC ne doit pas dépasser **5 s** par
   espèce au total avec GIS + DEM HR activés (latence Cloudflare comprise).
   Si la cible est dépassée, fallback automatique sur LOD=MED puis LOD=LOW.
5. **PYTEST NEUTRE** : Tous les tests pytest doivent éviter les mots-clés BCE-4X
   exclus (`territoire`, `corridor`) dans les noms de fonctions et fichiers.

---

## 📋 SÉQUENCE D'EXÉCUTION RECOMMANDÉE

| Phase | Module | Priorité | Statut |
|---|---|---|---|
| 1.1 | Téléchargement et conversion FORET_MFFP / SOL_IRDA | 🔴 P0 | NOT STARTED |
| 1.2 | Module `gis_layers_omega.py` (loader + R-tree index) | 🔴 P0 | NOT STARTED |
| 1.3 | Module `gis_corridor_corrector_omega.py` (masques + ajustements) | 🔴 P0 | NOT STARTED |
| 1.4 | Pytest neutre `test_phase_xx_gis_omega.py` | 🔴 P0 | NOT STARTED |
| 1.5 | Validation `GIS_OPERATIONAL_Ω = TRUE` | 🔴 P0 | NOT STARTED |
| 2.1 | Téléchargement et conversion DEM 10m + LIDAR HR | 🟡 P1 | NOT STARTED |
| 2.2 | Module `terrain_hr_omega.py` (extraction tile + downsampling) | 🟡 P1 | NOT STARTED |
| 2.3 | Module `terrain_lod_omega.py` (LOD switching) | 🟡 P1 | NOT STARTED |
| 2.4 | Module `apply_terrain_hr_to_corridors` (post-smoothing) | 🟡 P1 | NOT STARTED |
| 2.5 | Pytest neutre `test_phase_xx_terrain_hr.py` | 🟡 P1 | NOT STARTED |
| 2.6 | Validation `TERRAIN_HR_OPERATIONAL_Ω = TRUE` | 🟡 P1 | NOT STARTED |

---

## ⚠️ RISQUES IDENTIFIÉS

1. **Volumétrie données** : LIDAR HR Québec représente plusieurs To de raw.
   Mitigation : extraction par BBOX (zone BSL ~50km × 50km), conversion
   downsampled GeoTIFF.
2. **Disponibilité LIDAR** : Couverture LIDAR HR partielle au Québec.
   Mitigation : fallback DEM 10m systématique si HR absent.
3. **Performance Cloudflare** : Issue P22J persistante. L'ajout de couches GIS
   pourrait aggraver la latence.
   Mitigation : pré-cache JSON allégé en `/app/backend/data/`, indexation R-tree.
4. **Licences sources** : Vérifier compatibilité licences Données Québec /
   MFFP avec usage commercial (si déploiement public PRD).
   Mitigation : documenter lic dans `LICENSES.md` du projet.

---

**STATUT** : 📋 PLANIFICATION DOCTRINALE PRÊTE — Attente activation par
COMMANDANT STEEVE-MAX pour démarrer PHASE 1.

**Signé** : AGENT INSTITUTIONNEL Ω · BCE-4X ULTIME ABSOLU

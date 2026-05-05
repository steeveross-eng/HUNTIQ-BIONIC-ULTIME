# MFFP_PHASE_3 — Spécifications des 8 couches dérivées (ORDRE N°52-R11)

**COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU · ANTI_GÉNÉRIQUE_STRICT**

Ce document fournit le **gabarit canonique** des 8 couches MFFP dérivées
qui débloqueront le recalcul R9 (corridors / hotspots / affuts / salines /
zones_vitales / zones_passage / zones_rut / zones_repos / zones_alimentation).

- Source : `pee_maj.gpkg` (37,3 Go · slot `FORET_MFFP_PEE_MAJ_Ω`)
- Projection cible : EPSG:32198 (NAD83 / Québec Lambert)
- Persistance : `/app/backend/data/gis_archive/derivatives/`
- Module Python : `backend/engines/v8_institutional/especes/mffp_phase3_specs_omega.py`
- Endpoint REST : `GET /api/v30/admin-premium/gis/diagnostic/pee-maj/phase3-specs`

---

## Champs canoniques attendus dans `pee_maj.gpkg`

| Champ | Type | Description | Domaine |
|---|---|---|---|
| `GEOMETRY` | (Multi)Polygon | Géométrie polygone | EPSG:32198 |
| `POLY_ID` | int | Identifiant unique | — |
| `ESS_DOMI` | str(3) | Essence dominante | ERS, BOP, EPB, … |
| `ESS_CODOMI` | str(3) | Essence codominante | optionnel |
| `GR_ESS` | str(1) | Groupe essences | R, F, M |
| `CL_AGE` | str | Classe d'âge | 10, 30, 50, 70, 90, 120, JIN, JIR, VIN, VIR |
| `CL_HAUT` | int | Classe hauteur | 1=>22m … 5=4-7m |
| `CL_DENS` | str | Classe densité | A=>80%, B=60-80%, C=40-60%, D=25-40%, E=10-25% |
| `TY_COUV` | str | Type couverture | FE, FR, FM, RE, RN, … |
| `TYPE_ECO` | str | Type écologique | FE32, RS28, MS22, … |
| `ORIGINE` | str | Origine peuplement | CHT, CT, BR, FR, … |
| `AN_ORIGINE` | int | Année d'origine | YYYY |
| `PERTURB` | str | Type perturbation | CO, EL, … |
| `AN_PERTURB` | int | Année perturbation | YYYY |
| `IND_QUAL` | str | Indice qualité station | optionnel |
| `SUPERFICIE` | float | Superficie | m² ou ha |

---

## Tableau synthèse des 8 couches MFFP dérivées

| Couche | Priorité | Format | Résolution | Complexité | Effort dev |
|---|---|---|---|---|---|
| **MFFP_DENSITY** | P0 | GeoTIFF uint8 | 100m | LOW | 4h |
| **MFFP_AGE** | P0 | GeoTIFF uint8 | 250m | LOW | 4h |
| **MFFP_STRUCTURE** | P0 | GeoTIFF uint8 | 100m | MEDIUM | 12h |
| **MFFP_FRAGMENTATION** | P0 | GeoTIFF float32 | 250m | HIGH | 24h |
| **MFFP_PRODUCTIVITY** | P1 | GeoTIFF float32 | 100m | MEDIUM | 16h |
| **MFFP_HABITAT** | P1 | GeoTIFF uint8 (5 bandes) | 250m | HIGH | 24h |
| **MFFP_CONNECTIVITY** | P2 | GeoPackage MultiPolygon | — | HIGH | 32h |
| **MFFP_CONTINUITY** | P2 | GeoTIFF uint8 | 100m | MEDIUM | 12h |

**Total effort 4 couches P0 critiques (déblocage R9) : ~44 h dev.**
**Total effort 8 couches : ~128 h dev.**

---

## Spécifications détaillées par couche

### 1. MFFP_DENSITY (P0 · LOW · 4h)

**Description** : Pourcentage de couverture canopée par cellule.

**Inputs** :
- Champs : `CL_DENS`, `GR_ESS`, `CL_HAUT`
- Dictionnaire : `cl_dens_to_pct.json` → `{"A":90, "B":70, "C":50, "D":32, "E":15}`

**Sortie** : `MFFP_COUVERT_FORESTIER_DENSITY.tif` (uint8, 0-100, 100m)

**Algorithme** :
1. `geopandas.read_file(pee_maj.gpkg)` + reproject EPSG:32198
2. `df['pct_canopy'] = df['CL_DENS'].map(cl_dens_to_pct)`
3. Correction : `pct *= 1.05 if GR_ESS=='R' else 1.0`
4. `rasterio.features.rasterize(geom, value=pct_canopy, …)`

**Références** : Coops et al. (2007), MFFP Normes inventaire (2018).

---

### 2. MFFP_AGE (P0 · LOW · 4h)

**Description** : Classes d'âge des peuplements.

**Inputs** : `CL_AGE`, `AN_ORIGINE`

**Sortie** : `MFFP_CLASSES_AGE.tif` (uint8, 1-8, 250m)

| Classe | Domaine |
|---|---|
| 1 | 0-20 ans |
| 2 | 20-40 ans |
| 3 | 40-60 ans |
| 4 | 60-80 ans |
| 5 | 80-100 ans |
| 6 | 100+ ans |
| 7 | JEUNE_INEQUIENNE (`JIN`/`JIR`) |
| 8 | VIEILLE_INEQUIENNE (`VIN`/`VIR`) |

**Référence** : MFFP Manuel d'aménagement forestier durable (2016) ch. 4.

---

### 3. MFFP_STRUCTURE (P0 · MEDIUM · 12h)

**Description** : Structure verticale et horizontale du peuplement.

**Inputs** : `CL_HAUT`, `CL_DENS`, `CL_AGE`, `GR_ESS`, `TY_COUV`, `TYPE_ECO`

**Dictionnaire requis Commandant** : `structure_classification_rules.json`

**Sortie** : `MFFP_STRUCTURE.tif` (uint8, 1-7, 100m)

| Classe | Description |
|---|---|
| 1 | REGULIERE_MONOSTRATE |
| 2 | REGULIERE_BISTRATE |
| 3 | IRREGULIERE_ETAGEE |
| 4 | IRREGULIERE_JARDINEE |
| 5 | INEQUIENNE_JEUNE |
| 6 | INEQUIENNE_VIEILLE |
| 7 | RECRUE_OUVERT |

**Algorithme** : Arbre de décision MFFP CL_AGE × CL_HAUT × CL_DENS.

---

### 4. MFFP_FRAGMENTATION (P0 · HIGH · 24h)

**Description** : Indice fragmentation forestière (Dickson 2017).

**Inputs** :
- Champs : `TY_COUV`, `GR_ESS`, `CL_DENS`
- Layer prérequis : `GIS_COUVERT_FORESTIER_BINARY.tif` (rasterisation préalable)

**Sortie** : `MFFP_FRAGMENTATION_INDEX.tif` (float32, 0.0-1.0, 250m)

**Algorithme Dickson 2017** :
- `Pf` = proportion forêt dans fenêtre 5×5 (50m × 50m)
- `Pff` = proportion adjacences forêt-forêt
- `FRAG_INDEX = Pff / max(Pf, eps)` (1.0 = forêt continue, 0.0 = fragmenté)

**Référence** : Dickson, Roemer, Boyce (2017) FEM 405:85-94.

---

### 5. MFFP_PRODUCTIVITY (P1 · MEDIUM · 16h)

**Description** : Productivité forestière (m³/ha équivalent).

**Inputs** : `CL_AGE`, `ESS_DOMI`, `IND_QUAL`, `TYPE_ECO`

**Dictionnaire requis** : `tables_rendement_mffp.json`

**Sortie** : `MFFP_PRODUCTIVITE.tif` (float32, 0-500, 100m)

**Algorithme** : Lookup trilinéaire `tables[ESS_DOMI][CL_AGE][IND_QUAL]`.

---

### 6. MFFP_HABITAT (P1 · HIGH · 24h · 5 espèces)

**Description** : Habitat brut multi-espèces (5 bandes raster).

**Inputs** : `ESS_DOMI`, `GR_ESS`, `CL_AGE`, `CL_DENS`, `TY_COUV`, `TYPE_ECO`

**Dictionnaire requis** : `habitat_preferences_par_espece.json`

**Sortie** : `MFFP_HABITAT_BRUT.tif` (uint8 5 bandes, 0-100, 250m)

| Bande | Espèce |
|---|---|
| 1 | chevreuil_brut |
| 2 | orignal_brut |
| 3 | ours_noir_brut |
| 4 | dindon_brut |
| 5 | wapiti_brut |

**Références** : MFFP Outils évaluation habitat (2010), Drolet et al. (1999), Crête & Courtois (1997).

---

### 7. MFFP_CONNECTIVITY (P2 · HIGH · 32h)

**Description** : Polygones d'écorégions (clustering DBSCAN).

**Inputs** : `ESS_DOMI`, `CL_AGE`, `CL_DENS`, `TYPE_ECO`, `TY_COUV`

**Dépendances** : `MFFP_STRUCTURE`, `MFFP_HABITAT`

**Sortie** : `MFFP_CONNECTIVITE.gpkg` (MultiPolygon avec attributs cluster_id, ecoregion_code, habitat_score_mean, fragmentation_score, area_ha)

**Indice** : IIC index Saura & Pascual-Hortal (2007).

---

### 8. MFFP_CONTINUITY (P2 · MEDIUM · 12h)

**Description** : Continuité forestière historique.

**Inputs** : `AN_ORIGINE`, `ORIGINE`, `PERTURB`, `AN_PERTURB`, `CL_AGE`

**Dictionnaire requis** : `perturbation_severity.json`

**Sortie** : `MFFP_CONTINUITE.tif` (uint8, 1-5, 100m)

| Classe | Description |
|---|---|
| 1 | RECENT_<40ANS |
| 2 | INTERMEDIAIRE_40-80ANS |
| 3 | ANCIEN_80-150ANS |
| 4 | VIEILLES_FORETS_>150ANS |
| 5 | PERTURBE_RECEMMENT |

---

## Plan minimal d'implémentation (déblocage R9 prioritaire)

### Ordre recommandé des 4 couches critiques P0

| Étape | Couche | Complexité | Effort | Note |
|---|---|---|---|---|
| 1 | `MFFP_DENSITY` | LOW | 4h | Mapping direct simple |
| 2 | `MFFP_AGE` | LOW | 4h | Bins MFFP standard |
| 3 | `MFFP_STRUCTURE` | MEDIUM | 12h | Arbre décision |
| 4 | `MFFP_FRAGMENTATION` | HIGH | 24h | Convolutions Dickson 2017 |

**Total : ~44 h dev pour débloquer R9.**

### Dépendances techniques

**Modules Python** :
```
geopandas>=0.14
fiona>=1.9 OU pyogrio>=0.8
rasterio>=1.3
pyproj>=3.6
shapely>=2.0
scipy>=1.11  (ndimage pour fragmentation)
numpy>=1.26
```

**Bibliothèques système** :
- GDAL >= 3.7
- GEOS >= 3.11
- PROJ >= 9.2

**Dictionnaires Commandant à fournir** (4 critiques) :
1. `structure_classification_rules.json`
2. `cl_dens_to_pct.json` (validation valeurs A/B/C/D/E)
3. `classes_age.json` (validation bornes MFFP)
4. `ty_couv_to_forest_binary.json`

**Subset validation** : 100 Mo de `pee_maj.gpkg` couvrant ≥ 5 écorégions.

---

## Fonctions Python — squelettes (NotImplementedError)

Toutes les fonctions sont définies dans :
`/app/backend/engines/v8_institutional/especes/mffp_phase3_specs_omega.py`

```python
from engines.v8_institutional.especes.mffp_phase3_specs_omega import (
    compute_mffp_structure,
    compute_mffp_density,
    compute_mffp_age,
    compute_mffp_fragmentation,
    compute_mffp_productivity,
    compute_mffp_habitat,
    compute_mffp_connectivity,
    compute_mffp_continuity,
)
```

Chaque fonction lève **`NotImplementedError`** avec message explicite tant
que les dictionnaires métier + subset de validation ne sont pas fournis
par le Commandant. **Aucune simulation n'est tolérée.**

---

## Modules AMPLIFICATEURS (phases ultérieures)

À intégrer après stabilisation des 8 couches de base :
- **LiDAR** : raffinement densité + hauteur réelle vs CL_HAUT
- **GEM** : Global Ecological Model integration
- **Carte 2D/3D** : visualisation immersive territoire

Ces modules viendront enrichir les 8 couches existantes ; ils ne se
substituent pas aux dictionnaires MFFP_CODES, aux spécifications
algorithmiques ni au subset de validation.

---

## Validation protocol par couche (5 étapes obligatoires)

1. **Tests unitaires pytest** avec subset 100 Mo
2. **Comparaison statistique** avec layers MFFP officielles (si disponibles)
3. **Validation visuelle** sur 3-5 écorégions
4. **Signature SHA-256** + sceaux BCE-4X (déjà implémentés en R8 PHASE_6)
5. **Documentation institutionnelle** (PRD.md + audit_log.jsonl)

---

**V30 LOCK INVIOLÉ · FUSION ADD-ONLY · ANTI_GÉNÉRIQUE_STRICT**

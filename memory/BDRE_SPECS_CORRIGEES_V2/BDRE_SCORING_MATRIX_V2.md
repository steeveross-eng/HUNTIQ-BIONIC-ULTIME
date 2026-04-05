# BDRE — MATRICE DE SCORING DES SOURCES V2
## BCE-4X GOLDEN V6+ | Directive STEEVE-MAX
## Date: 2026-04-06
## Corrections: Aucune requise (document conforme)

---

## HISTORIQUE DES CORRECTIONS

| Correction | Description | Statut |
|------------|-------------|--------|
| Aucune | Document conforme selon BDRE_CONFORMITY_REPORT.md | CONFORME |

---

## 1. METHODOLOGIE DE SCORING

Chaque source est evaluee sur 5 criteres (0.0 -> 1.0).
Le score global = moyenne ponderee selon les poids BCE-4X.

| Critere | Poids | Description |
|---------|-------|-------------|
| Couverture (COV) | 0.30 | % de la zone couverte par la source |
| Fraicheur (FRA) | 0.15 | Age des donnees vs TTL |
| Precision (PRE) | 0.25 | Resolution / exactitude geographique |
| Completude (COM) | 0.20 | % de types de donnees presents vs attendus |
| Coherence (COH) | 0.10 | Absence de contradictions internes |

```
SCORE = COV*0.30 + FRA*0.15 + PRE*0.25 + COM*0.20 + COH*0.10
```

---

## 2. SEUILS DE DECISION

| Score | Classification | Action |
|-------|---------------|--------|
| 0.80 -- 1.00 | FIABLE | Utiliser comme source primaire |
| 0.60 -- 0.79 | ACCEPTABLE | Utiliser avec enrichissement |
| 0.40 -- 0.59 | DEGRADE | Declencher fallback niveau 2 |
| 0.20 -- 0.39 | DEFICIENT | Declencher fallback niveau 3 |
| 0.00 -- 0.19 | INUTILISABLE | Declencher fallback niveau 4 + alerte |

---

## 3. SCORING ACTUEL DES SOURCES (TERRITOIRE 48.19, -68.39)

### 3.1 Sources externes

| Source | COV | FRA | PRE | COM | COH | SCORE | Classification |
|--------|-----|-----|-----|-----|-----|-------|-------|
| SRC-01 Overpass (trails) | 0.10 | 1.00 | 0.70 | 0.05 | 0.80 | **0.31** | DEFICIENT |
| SRC-02 Overpass (eau) | 0.60 | 1.00 | 0.80 | 0.70 | 0.90 | **0.73** | ACCEPTABLE |
| SRC-03 Access Engine V6 | 0.00 | 1.00 | 0.00 | 0.00 | 1.00 | **0.25** | DEFICIENT |
| SRC-04 Foret Ouverte | N/A | N/A | N/A | N/A | N/A | N/A | NON CONNECTE |
| SRC-05 VGO | N/A | N/A | N/A | N/A | N/A | N/A | NON CONNECTE |
| SRC-06 DEM/SRTM | N/A | N/A | N/A | N/A | N/A | N/A | NON CONNECTE |
| SRC-07 Meteo | 0.90 | 0.95 | 0.60 | 0.80 | 0.90 | **0.81** | FIABLE |
| SRC-08 GPS Tracks | 0.00 | N/A | 0.00 | 0.00 | N/A | **0.00** | NON DISPONIBLE |

### 3.2 Sources internes

| Source | COV | FRA | PRE | COM | COH | SCORE | Classification |
|--------|-----|-----|-----|-----|-----|-------|-------|
| INT-01 TERRAIN_COSTS | 1.00 | 1.00 | 0.90 | 0.90 | 1.00 | **0.96** | FIABLE |
| INT-02 HUMAN_TRAJET_COSTS | 1.00 | 1.00 | 0.90 | 0.90 | 1.00 | **0.96** | FIABLE |
| INT-03 LAYER_TO_TERRAIN | 0.40 | 1.00 | 0.50 | 0.30 | 0.90 | **0.50** | DEGRADE |
| INT-04 Ecological DB V8 | 0.90 | 0.90 | 0.85 | 0.90 | 0.95 | **0.90** | FIABLE |
| INT-05 Species Rules | 0.95 | 0.95 | 0.90 | 0.95 | 1.00 | **0.95** | FIABLE |
| INT-06 Water Exclusion | 0.80 | 1.00 | 0.85 | 0.80 | 0.95 | **0.85** | FIABLE |
| INT-07 OSM_HIGHWAY_TO_TERRAIN | 1.00 | 1.00 | 0.80 | 0.85 | 1.00 | **0.91** | FIABLE |
| INT-08 ROAD_COSTS | 0.90 | 1.00 | 0.85 | 0.80 | 1.00 | **0.90** | FIABLE |

---

## 4. ANALYSE DES DEFICIENCES

### SRC-01 Overpass (trails) -- SCORE: 0.31 DEFICIENT
```
COV = 0.10 : 5 ways / ~50 sentiers visibles sur satellite = 10% couverture
FRA = 1.00 : Cache du jour
PRE = 0.70 : Noeuds precis mais ways tres generiques (unclassified)
COM = 0.05 : 0 path, 0 footway, 0 track — 1 seul type (unclassified)
COH = 0.80 : Pas de contradictions mais graphe deconnecte (2 composantes)
```
**Cause**: Zone forestiere isolee, couverture OSM minimale.

### SRC-03 Access Engine V6 -- SCORE: 0.25 DEFICIENT
```
COV = 0.00 : 0 noeuds, 0 aretes — couverture NULLE
FRA = 1.00 : Cache du jour
PRE = 0.00 : Aucune donnee
COM = 0.00 : Aucune donnee
COH = 1.00 : Pas de contradictions (rien a contredire)
```
**Cause**: Requete Overpass retourne VIDE pour cette zone.

### INT-03 LAYER_TO_TERRAIN -- SCORE: 0.50 DEGRADE
```
COV = 0.40 : Couvre 10 types/23 de HUMAN_TRAJET_COSTS = 43%
FRA = 1.00 : Hardcoded, toujours actuel
PRE = 0.50 : Mapping approximatif (habitats->mature_forest generique)
COM = 0.30 : 17 types HUMAN_TRAJET_COSTS jamais utilises (valley, agriculture, etc.)
COH = 0.90 : Coherent en interne
```
**Cause**: Mapping conceptuel (zones comportementales -> terrain), pas reel.

---

## 5. MATRICE DE FALLBACK PAR SCORE

| Score source primaire | Action BDRE | Source de remplacement |
|---|---|---|
| 0.80+ | Utiliser directement | N/A |
| 0.60-0.79 | Enrichir avec source secondaire | ENGINE_OSM_LITE + INT-06 |
| 0.40-0.59 | Fallback niveau 2 | Waterway bank routing + topographie |
| 0.20-0.39 | Fallback niveau 3 | Corridor A* HUMAN_TRAJET_COSTS |
| 0.00-0.19 | Fallback niveau 4 + ALERTE | GPS tracks si dispo, sinon estimation enrichie |

---

## 6. SCORING PAR AFFUT (TERRITOIRE ACTUEL)

| Affut | Source primaire | Score | Fallback declenche | Source finale |
|---|---|---|---|---|
| MOBILE 38.9 | SRC-01 (Overpass trails) | 0.31 | OUI -- Niveau 3 | Corridor A* (serait) |
| MOBILE 29.8 | SRC-01 (Overpass trails) | 0.31 | OUI -- Niveau 3 | Corridor A* (serait) |
| MOBILE 12a | SRC-01 (Overpass trails) | 0.31 | OUI -- Niveau 3 | Corridor A* (serait) |
| MOBILE 12b | SRC-01 (Overpass trails) | 0.31 | OUI -- Niveau 3 | Corridor A* (serait) |

**ACTUELLEMENT**: Tous en fallback "estimation" (3 points ligne droite) car le BDRE n'est pas encore implemente.

**APRES BDRE**: Les 4 affuts utiliseraient le pipeline hybride:
- Level 1 (waterway bank): Si waterways <200m de l'affut -> route via berges
- Level 3 (corridor A*): Pathfinder HUMAN_TRAJET_COSTS avec evitement foret/eau

---

**STATUT: MATRICE DE SCORING V2 COMPLETE — AUCUNE CORRECTION REQUISE**
**EN ATTENTE VALIDATION STEEVE-MAX**

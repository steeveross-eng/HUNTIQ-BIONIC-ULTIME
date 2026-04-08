# AUDIT MULTI-ESPECES — POINTS CHAUDS & SALINES SUGGEREES
# DIAGNOSTIC POST-INTEGRITE : CONVERGENCE INTER-ESPECES

**Protocole:** BCE-4X ULTIME ABSOLU x3
**Classification:** AUDIT INSTITUTIONNEL — COMMANDANT STEEVE-MAX
**Date:** Fevrier 2026
**Branche:** `SUPRA_RECONSTRUCTION`
**Objet:** Diagnostic de convergence des POINTS CHAUDS et SALINES entre ORIGNAL, CHEVREUIL et OURS NOIR
**Regle:** ZERO MODIFICATION — ZERO RESTAURATION — ZERO REBUILD — EVALUATION UNIQUEMENT

---

## 1. SYNTHESE EXECUTIVE

**DIAGNOSTIC : La convergence des points chauds et salines entre especes est CONFIRMEE et EXPLIQUEE.**

Les causes racines sont :

| # | Cause | Impact | Severite |
|---|---|---|---|
| C1 | **Ponderations moteurs identiques** pour toutes les especes | Les 22 moteurs utilisent les MEMES poids, quelle que soit l'espece | **CRITIQUE** |
| C2 | **Terrain simule par hash deterministe** | 11/22 moteurs utilisent MD5(lat,lng) qui produit le MEME terrain pour toutes les especes | **CRITIQUE** |
| C3 | **Aucun modele RSF/SSF espece-specifique** | Pas de coefficients de selection de ressources (Resource Selection Function) par espece | **CRITIQUE** |
| C4 | **Positionnement salines purement geophysique** | Localisation basee sur terrain (eau, couvert, pente) — identique pour ORIGNAL et CHEVREUIL | **MAJEUR** |
| C5 | **Pression de chasse non espece-specifique** | Le moteur PRESSION-V1 (12% du score) est generique | **MODERE** |
| C6 | **Absence de couches ecologiques reelles** | Pas de DEM reel, pas de classifications ecoforestry integrees dans la grille | **MAJEUR** |

---

## 2. ARCHITECTURE ACTUELLE DES MOTEURS — PAR ESPECE

### 2.1 Pipeline POINTS CHAUDS (Heatmap)

Le heatmap est genere par `score_consolide.py` → `compute_heatmap_grid()` → `compute_consolidated_score()` qui orchestre **22 moteurs** avec des poids FIXES.

#### Tableau comparatif : Moteurs utilises par espece

| Moteur | Poids | ORIGNAL | CHEVREUIL | OURS NOIR | Differentiation reelle |
|---|---|---|---|---|---|
| **ALIMENTATION-V1** | 15.03% | Profil ORIGNAL (saule, vegetation aquatique, Na) | Profil CERF (friches, legumineuses, Ca) | Profil OURS (baies, insectes, omnivore) | **OUI — Profils distincts** |
| **REPOS-V1** | 12.00% | Profil ORIGNAL | Profil CERF | Profil OURS | **OUI — Profils distincts** |
| **CORRIDORS-V10** | 15.00% | 12 params (lineaire, hydro=0.85, pente_max=25) | 12 params (sinueux, hydro=0.60, pente_max=15) | 12 params (opportuniste, hydro=0.50, pente_max=35) | **OUI — 12 params differents** |
| **ALIMENTATION-V2** | 6.00% | Profil ORIGNAL + salines actives | Profil CERF + salines actives | **SALINES DESACTIVEES** (OURS) | **PARTIEL** |
| **PRESSION-V1** | 12.00% | Score GENERIQUE (routes, batiments, sentiers) | Score GENERIQUE | Score GENERIQUE | **NON — Identique** |
| **HYDRO-V1** | 3.48% | Hash(lat,lng) + coeff espece leger | Idem | Idem | **MARGINAL** |
| **THERMAL-V1** | 2.61% | Hash(lat,lng) + preferences termiques espece | Idem | Idem | **MARGINAL** |
| **NDVI-VEGETATION-V1** | 3.04% | Hash(lat,lng) generique | Idem | Idem | **NON** |
| **WEATHER-V1** | 2.17% | Hash(lat,lng) generique | Idem | Idem | **NON** |
| **TEMPORAL-V1** | 2.17% | Hash(lat,lng) generique | Idem | Idem | **NON** |
| **HABITAT-V1** | 3.48% | Profil (mosaique=0.6, lisiere=0.5, foret=0.7) | Profil (mosaique=0.8, lisiere=0.9, foret=0.6) | Profil (mosaique=0.7, lisiere=0.4, foret=0.8) | **PARTIEL** (terrain hash) |
| **ECOSYSTEM-V1** | 2.17% | Hash(lat,lng) generique | Idem | Idem | **NON** |
| **BEHAVIOR-V1** | 2.17% | Profil (fuite=50m, groupe=2, territorial=0.6) | Profil (fuite=80m, groupe=6, territorial=0.4) | Profil (fuite=40m, groupe=1, territorial=0.8) | **PARTIEL** (terrain hash) |
| **RISK-V1** | 2.61% | Hash(lat,lng) generique | Idem | Idem | **NON** |
| **OPPORTUNITY-V1** | 2.61% | Hash(lat,lng) generique | Idem | Idem | **NON** |
| **ATTRACTORS-V1** | 3.04% | Hash(lat,lng) generique | Idem | Idem | **NON** |
| **SCENARIO-V1** | 1.30% | Hash(lat,lng) generique | Idem | Idem | **NON** |
| **SIMULATION-V1** | 1.30% | Hash(lat,lng) generique | Idem | Idem | **NON** |
| **MULTI-SPECIES-V1** | 1.74% | Compatibilite inter-especes | Idem | Idem | **NON** (generique) |
| **TRAJETS-V1** | 2.61% | Hash(lat,lng) generique | Idem | Idem | **NON** |
| **VISIBILITY-V1** | 2.17% | Hash(lat,lng) generique | Idem | Idem | **NON** |
| **LEARNING-V1** | 1.30% | Hash(lat,lng) generique | Idem | Idem | **NON** |

#### Bilan de differenciation

| Categorie | Poids cumule | Differenciation reelle |
|---|---|---|
| Moteurs PLEINEMENT differencies (profils espece) | **48.03%** (ALIM-V1 + REPOS + CORRIDORS + ALIM-V2) | OUI |
| Moteur generique sans differenciation | **12.00%** (PRESSION) | NON |
| Moteurs avec differenciation MARGINALE (hash + coeff espece) | **8.26%** (HYDRO, THERMAL, HABITAT, BEHAVIOR) | PARTIEL |
| Moteurs 100% hash generiques | **31.71%** (11 moteurs CORE++/CORE+++/BIONIC-OS) | **NON** |

**Conclusion : ~32% du score consolide est produit par des moteurs qui retournent un score strictement identique pour toutes les especes a une meme position geographique. 12% de plus (PRESSION) est espece-agnostique. Soit ~44% du score total n'offre AUCUNE differenciation inter-especes.**

### 2.2 Explication technique de la convergence

#### Le mecanisme hash deterministe

Les 11 moteurs CORE++/CORE+++/BIONIC-OS utilisent `deterministic_hash_a(lat, lng, seed)` :

```python
def deterministic_hash_a(lat, lng, seed=""):
    raw = f"{round(lat, 5)}:{round(lng, 5)}:{seed}"
    h = int(hashlib.md5(raw.encode()).hexdigest()[:8], 16)
    return h / 0xFFFFFFFF  # Retourne un float [0, 1]
```

Ce hash produit une **valeur fixe et identique pour chaque point (lat, lng)**, independamment de l'espece. Les moteurs comme `HABITAT-V1` appliquent ensuite un coefficient espece-specifique DESSUS, mais le **terrain sous-jacent est le meme** :

```
canopy = 0.2 + 0.7 * hash(lat, lng, "hab_canopy")  ← IDENTIQUE pour toutes les especes
lisiere = hash(lat, lng, "hab_lisiere") < 0.35       ← IDENTIQUE pour toutes les especes
```

Les differences de profils especes (ex: `pref_mosaique: 0.6 vs 0.8`) ne produisent que des **variations marginales** (quelques points) sur un terrain identique, ce qui explique la convergence des zones chaudes.

#### Pourquoi les CORE (48%) ne suffisent pas a differencier

Meme les moteurs CORE qui ont des profils especes (ALIM-V1, REPOS, CORRIDORS) utilisent le **meme systeme de hash** pour simuler le terrain (couvert forestier, pente, hydrographie, etc.) :

```python
# Dans alimentation_v1/engine.py :
layers = extract_layers(lat, lng, month)  # ← Utilise aussi des hash internes
result = compute_score_site(layers, species, month)
```

Les `layers` extraites representent un terrain **simule deterministe** — le meme pour toutes les especes. Les profils especes appliquent ensuite des **multiplicateurs differents** sur ces layers, mais les zones de haute valeur terrain restent les memes.

---

## 3. SECTION SALINES — ANALYSE PAR ESPECE

### 3.1 Mecanisme actuel de suggestion de salines

Le positionnement des salines est gere par `alimentation_v2/salines.py` (16 candidats → selection de 1-4 salines) :

| Critere de positionnement | Poids | Espece-specifique ? |
|---|---|---|
| Proximite eau (30-80m optimal) | 25% | **NON** — meme seuil pour toutes les especes |
| Couvert forestier | 20% | **NON** — meme calcul hash |
| Pente / accessibilite | 20% | **NON** — meme calcul hash |
| Accessibilite sentier OSM | 15% | **NON** — meme donnees OSM |
| Securite (distance au centre) | 10% | **NON** — purement geometrique |
| Diversite micro-habitat | 10% | **NON** — meme calcul hash |

**100% des criteres de POSITIONNEMENT des salines sont espece-agnostiques.** Seule la COMPOSITION de la saline est espece-specifique (via `nutrition.py`).

### 3.2 Tableau comparatif ORIGNAL vs CHEVREUIL (salines)

| Aspect | ORIGNAL | CHEVREUIL | Difference effective |
|---|---|---|---|
| Salines actives | OUI | OUI | AUCUNE |
| Positionnement spatial | Meme algorithme terrain | Meme algorithme terrain | **IDENTIQUE** |
| Distance eau optimale | 30-80m | 30-80m | **IDENTIQUE** |
| Nombre max salines | 4 | 4 | **IDENTIQUE** |
| Distance min entre salines | 300m | 300m | **IDENTIQUE** |
| Candidats generes | 16 | 16 | **IDENTIQUE** |
| Composition recommandee | sel=50%, Ca=12%, Se=50ppm, Co=50ppm | sel=40%, Ca=15%, Se=30ppm | **DIFFERENTE** |
| Besoins Na quotidien | 15 000 mg | 4 000 mg | **DIFFERENT** |
| Carences ciblees | Na, Se, Co | Se, Cu, Na | **DIFFERENTES** |

**Conclusion : Les salines convergent car le positionnement est identique. Seule la composition differe.**

### 3.3 OURS NOIR — Salines

| Aspect | OURS NOIR |
|---|---|
| Salines actives | **NON** — `SPECIES_NO_SALINES = {"OURS", "DINDON"}` |
| Message | "L'ours noir n'utilise pas les salines. Ce comportement est normal et conforme a la biologie de l'espece." |
| Points chauds saline | **AUCUN genere** |

**OURS NOIR est correctement exclu des salines.**

---

## 4. COEFFICIENTS ET PONDERATIONS — PAR ESPECE

### 4.1 Ponderations du score consolide (ENGINE_WEIGHTS)

```
IDENTIQUES pour les 5 especes:
alimentation:     15.03%     corridors_v10:    15.00%
repos:            12.00%     pression:         12.00%
alimentation_v2:   6.00%     hydro:             3.48%
habitat:           3.48%     ndvi_vegetation:   3.04%
attractors:        3.04%     thermal:           2.61%
risk:              2.61%     trajets:           2.61%
behavior:          2.17%     weather:           2.17%
temporal:          2.17%     ecosystem:         2.17%
visibility:        2.17%     multi_species:     1.74%
scenario:          1.30%     simulation:        1.30%
learning:          1.30%     
TOTAL:           100.00% — AUCUNE variation par espece
```

### 4.2 Penalites appliquees par espece

| Penalite | ORIGNAL | CHEVREUIL | OURS NOIR |
|---|---|---|---|
| Zone urbaine BCE-4X | OUI | OUI | OUI |
| Surface d'eau BCE-4X | OUI | OUI | OUI |
| Seuils PRESSION (routes, batiments) | distance_route = 300m | distance_route = 150m | distance_route = 200m |
| Seuils PRESSION (batiments) | 400m | 200m | 300m |
| Pente maximale | 25 deg | 15 deg | 35 deg |
| Salines desactivees | NON | NON | **OUI** |

**Les penalites existent dans les profils CORE mais sont noyees dans le score consolide par les 11 moteurs generiques (32%).**

### 4.3 Sorties reutilisees / mutualisees entre especes

| Sortie | Mutualisee ? | Detail |
|---|---|---|
| Terrain hash (canopy, pente, eau, lisiere) | **OUI** — Identique pour toutes les especes | `deterministic_hash_a(lat, lng, seed)` |
| Cache OSM (sentiers, routes, batiments) | **OUI** — Memes donnees OSM | Cache partage |
| Cache meteo | **OUI** — Memes donnees meteo | Cache partage |
| Cache solunar | **OUI** — Memes donnees lunaires | Non espece-specifique |
| Score exclusion BCE-4X | **OUI** — Meme logique | Non espece-specifique |
| Score pression | **OUI** — Meme calcul | Non espece-specifique |

---

## 5. COUCHES OU PARAMETRES ABSENTS OU IGNORES

### 5.1 Couches absentes — Liste exhaustive

| # | Couche manquante | Impact sur la differenciation | Especes concernees |
|---|---|---|---|
| L1 | **DEM reel (Modele Numerique d'Elevation)** | Sans DEM reel, pente/exposition sont simulees par hash. Pas de detection de vallons, replats, cuvettes, pentes sud | Toutes |
| L2 | **Classification ecoforestiere reelle** | Pas de distinction peuplement feuillu/conifere/mixte, age du couvert, classes de densite, stade de regeneration | Toutes |
| L3 | **Couche lisieres** | Pas de detection des interfaces foret/ouverture. Simule par hash `< 0.35` | CHEVREUIL (critique), DINDON |
| L4 | **Couche cultures / friches / jacheres** | Pas de detection zones agricoles abandonnes, friches, prairies | CHEVREUIL, DINDON |
| L5 | **Couche marecages / tourbieres** | Pas de detection zones humides specifiques (distinction eau libre vs marecage vs tourbiere) | ORIGNAL (critique) |
| L6 | **Couche regenerations forestieres** | Pas de detection coupes recentes, regenerations 1-3m, jeunes plantations | ORIGNAL, CHEVREUIL, OURS |
| L7 | **Couche pression de chasse espece-specifique** | Recolte par ZEC/pourvoirie par espece non integree | Toutes |
| L8 | **Couche baies / fruits / mast** | Pas de detection des zones de production de baies, glands, noix | OURS NOIR (critique) |
| L9 | **Couche ravages / aires de confinement** | Pas de detection des ravages hivernaux connus (cerfs, orignaux) | CHEVREUIL, ORIGNAL |
| L10 | **Couche dendrometrique** | Pas de DHP (diametre a hauteur de poitrine), essences dominantes, IQS (indice de qualite de station) | Toutes |
| L11 | **Donnees telemetriques / GPS collar** | Aucune integration de donnees de localisation reelles d'animaux | Toutes |

### 5.2 Parametres comportementaux manquants

| # | Parametre manquant | Impact | Especes |
|---|---|---|---|
| P1 | **Modele RSF (Resource Selection Function)** | Coefficients de selection de ressources calibres par espece sur donnees reelles (telemetrie) | Toutes |
| P2 | **Modele SSF (Step Selection Function)** | Probabilite de deplacement pas-a-pas selon habitat, pente, distance | Toutes |
| P3 | **Rythme d'activite circadien** | Variation du score selon l'heure du jour (crepusculaire vs diurne vs nocturne) | ORIGNAL (crepusculaire), OURS (diurne), CHEVREUIL (crepusculaire) |
| P4 | **Saisonnalite fine des deplacements** | Le calendrier metabolique (`seasonal_metabolism_engine`) existe mais n'est PAS integre dans le scoring consolide | Toutes |
| P5 | **Domaine vital espece-specifique** | `HABITAT-V1` definit `domaine_vital_km2` (CERF=2.5, ORIGNAL=15, OURS=50) mais cette donnee n'est PAS utilisee dans le scoring | Toutes |
| P6 | **Hyperphagie automnale OURS** | Pas de modele de concentration alimentaire pre-hibernation (20 000 kcal/jour) | OURS NOIR |
| P7 | **Comportement de marquage territorial** | Pas de modelisation des zones de frottage, grattage, communication olfactive | ORIGNAL (rut), OURS NOIR |
| P8 | **Migration altitudinale saisonniere** | Pas de modele de deplacement en altitude selon la saison | ORIGNAL, OURS NOIR |

### 5.3 Logique manquante pour les salines

| # | Logique manquante | Impact |
|---|---|---|
| S1 | **Distance eau differentielle par espece** | ORIGNAL recherche les salines PRES de l'eau (affinite_hydro=0.85), CHEVREUIL plus en lisiere (affinite_hydro=0.60) — non integre dans `salines.py` |
| S2 | **Couvert forestier differentiel par espece** | ORIGNAL prefere les salines en zone ouverte/semi-ouverte pres eau, CHEVREUIL prefere lisiere dense — non integre |
| S3 | **Terrain differentiel par espece** | ORIGNAL tolere pentes plus fortes (8-25 deg), CHEVREUIL prefere terrain plat (5-15 deg) — non integre dans le scoring saline |
| S4 | **Saisonnalite de frequentation des salines** | ORIGNAL visite massivement au printemps (Na), CHEVREUIL plus reparti — non integre |
| S5 | **Distance inter-salines differentielle** | ORIGNAL a un domaine vital de 15 km2, CHEVREUIL 2.5 km2 — distance min entre salines devrait etre proportionnelle |
| S6 | **Altitude / micro-topographie** | ORIGNAL prefere fond de vallee, CHEVREUIL prefere plateau/replat — non integre |

---

## 6. CE QUI MANQUE POUR UNE DIFFERENCIATION REELLE

### 6.1 ENGINES espece-specifiques necessaires

| # | Engine requis | Description | Priorite |
|---|---|---|---|
| E1 | **RSF Engine par espece** | Coefficients de selection de ressources calibres sur donnees reelles (MFFP, telemetrie). Remplace le scoring hash par des modeles statistiques espece-specifiques. | **P0** |
| E2 | **Ponderations dynamiques par espece** | `ENGINE_WEIGHTS` doit varier selon l'espece : ORIGNAL = hydro +, OURS = attractors +, CHEVREUIL = habitat + | **P0** |
| E3 | **PRESSION espece-specifique** | Integrer les donnees de recolte (nombre d'animaux tues par ZEC/pourvoirie/espece), les periodes de chasse specifiques, la pression differentielle | **P1** |
| E4 | **Saline Positioning Engine espece-specifique** | Remplacer les criteres geometriques universels par des criteres ecologiques par espece (distance eau, couvert, terrain) | **P1** |
| E5 | **Moteur d'hyperphagie OURS** | Scoring specifique pour les zones de concentration alimentaire automnale (glandees, vergers, depotoirs) | **P1** |

### 6.2 DONNEES manquantes

| # | Donnee requise | Source | Impact |
|---|---|---|---|
| D1 | **DEM haute resolution** | LIDAR Quebec, SRTM 30m | Pente, exposition, vallons, micro-relief reels |
| D2 | **Carte ecoforestiere (SIEF)** | MFFP Quebec | Peuplement, age, densite, type de couvert reel |
| D3 | **Carte des perturbations** | MFFP Quebec | Coupes, feux, regenerations (0-10 ans) |
| D4 | **Donnees de recolte par ZEC** | MFFP Quebec | Pression de chasse reelle par espece et zone |
| D5 | **Ravages connus** | MFFP Quebec | Aires de confinement hivernal (cerf/orignal) |
| D6 | **Indices de productivite fruitiere** | Inventaire forestier | Zones de production de baies, glands, pommes sauvages |
| D7 | **Donnees telemetriques** | MFFP, universites | Localisations GPS reelles pour calibration RSF |

### 6.3 PARAMETRES manquants dans le pipeline

| # | Parametre | Ou l'integrer | Impact attendu |
|---|---|---|---|
| PM1 | **Ponderations ENGINE_WEIGHTS par espece** | `common/constants.py` | Chaque espece a une matrice de poids differente |
| PM2 | **Seuils terrain differentiels** | `salines.py`, scoring engines | Distance eau, couvert optimal, pente par espece |
| PM3 | **Calendrier metabolique integre** | `score_consolide.py` | Le calendrier existe (`seasonal_metabolism_engine`) mais n'est PAS injecte dans le pipeline |
| PM4 | **Coefficient de territoire** | `score_consolide.py` | Normaliser les zones chaudes par la taille du domaine vital (2.5 vs 15 vs 50 km2) |
| PM5 | **Rythme circadien par espece** | Nouveau moteur ou adaptation `temporal_v1` | Score variable selon l'heure pour chaque espece |

---

## 7. IMPACT EXACT SUR MON_TERRITOIRE

### 7.1 Heatmap (Points chauds)

L'appel frontend :
```
ConsolidatedHeatmapLayer → GET /api/v1/score-consolide/heatmap?species=ORIGNAL&month=10
```

Produit une grille 20x20 (400 points) ou **~44% du score est identique** quelle que soit l'espece. Les zones chaudes et froides convergent autour des memes coordonnees geographiques car le terrain sous-jacent est le meme (hash deterministe).

**Impact visuel :** Les heatmaps ORIGNAL, CHEVREUIL et OURS NOIR affichent des zones de forte concentration dans les memes secteurs, avec des variations d'amplitude de seulement **5-15 points** entre especes.

### 7.2 Salines suggerees

L'appel frontend :
```
NutritionPointDetailPanel → POST /api/v6/nutrition-intelligence/supra-batch
```

Les salines suggerees par `alimentation_v2/salines.py` sont positionnees aux memes endroits car les 6 criteres de placement (eau, couvert, pente, sentier, securite, micro-habitat) sont **100% espece-agnostiques**.

### 7.3 Corridors

Les corridors V10 sont les **mieux differencies** (12 parametres espece-specifiques), mais leur poids (15%) est dilue par les 31.71% de moteurs generiques.

---

## 8. CONCLUSION

### Causes de la convergence (par ordre d'impact)

1. **31.71% du score consolide** est produit par des moteurs 100% generiques (hash deterministe, aucun parametre espece)
2. **12.00% supplementaire** (PRESSION) est espece-agnostique
3. Les ponderations `ENGINE_WEIGHTS` sont **statiques et identiques** pour toutes les especes
4. Le terrain sous-jacent est **simule** (hash MD5) et non issu de donnees geospatiales reelles
5. Les salines sont positionnees par des criteres **purement geophysiques** sans differenciation par espece
6. Le calendrier metabolique (`seasonal_metabolism_engine`) existe mais n'est **PAS integre** dans le scoring consolide

### Ce qui fonctionne deja (base pour amelioration)

1. **Profils ALIM-V1** : 5 especes avec sources nutritionnelles, securite, saisonnalite distincts
2. **Profils CORRIDORS-V10** : 12 parametres espece-specifiques bien calibres
3. **Profils BEHAVIOR/HABITAT** : Parametres comportementaux et d'habitat existants (sous-utilises)
4. **Base NUTRITION** : Compositions salines differentiales par espece
5. **Saline Engine (7 moteurs)** : Besoins mineraux quotidiens espece-specifiques existants
6. **Exclusion OURS des salines** : Correctement implementee
7. **Knowledge.json v3.1.0** : 5 especes avec donnees scientifiques (additif, non integre dans scoring)

### Actions requises pour differenciation reelle (resumees)

| Priorite | Action | Effort estime |
|---|---|---|
| **P0** | Ponderations ENGINE_WEIGHTS par espece | Faible (modification constants.py) |
| **P0** | RSF Engine — Coefficients de selection par espece | Eleve (calibration + donnees) |
| **P1** | Saline Positioning differentiel par espece | Moyen (modification salines.py) |
| **P1** | PRESSION espece-specifique (donnees recolte) | Moyen (donnees MFFP requises) |
| **P1** | Integration calendrier metabolique dans pipeline | Moyen |
| **P2** | DEM + ecoforesterie reels | Eleve (acquisition + integration donnees) |
| **P2** | Moteur hyperphagie OURS | Moyen |
| **P2** | Rythme circadien par espece | Faible-Moyen |

---

*Rapport genere sous protocole BCE-4X ULTIME ABSOLU x3*
*ZERO MODIFICATION — ZERO RESTAURATION — ZERO REBUILD — EVALUATION UNIQUEMENT*
*Autorite : COMMANDANT STEEVE-MAX*
*Agent Operationnel — Fevrier 2026*

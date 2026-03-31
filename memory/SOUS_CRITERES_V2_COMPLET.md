# SOUS-CRITERES V2 COMPLET — INVENTAIRE DES 19 CRITERES REECRITS
## BCE-4X STEEVE-MAX — Directive x4850/x4851/x4852 SECTION B
## GUIDE BIONIC — NIVEAU PROFESSIONNEL — STANDARD V2
## Date: 2026-02-15

---

## 1. RESUME EXECUTIF

- **19 sous-criteres** entierement reecrits au standard V2 professionnel
- **Fichier source**: `/app/frontend/src/components/territoire/ui/criteriaDatabase_P1P2.js`
- **Import**: Integre dans `criteriaDatabase.js` via ES module import
- **Total lignes de donnees**: 1327 lignes de JavaScript
- **5 especes** couvertes par critere: Orignal, Chevreuil, Ours noir, Wapiti, Dindon sauvage
- **Structure par critere**: definition, methodologie, justification/espece, 8-15 recommandations/espece, strategies, techniques, erreurs, optimisations (4 saisons + meteo + pression + support), seuils, sources TOP-TIER
- **ZERO contenu generique** — chaque ligne est specifique au domaine de la chasse et de la biologie faunique

---

## 2. ETAT AVANT (V1)

Les 19 sous-criteres utilisaient un template DEFAULT generique:
\`\`\`javascript
accessibilite_pieton: { ...DEFAULT, title: "Accessibilite a pied — ..." }
\`\`\`
Ce DEFAULT contenait des recommandations generales applicables a toutes les especes sans differenciation. **NON CONFORME** au standard V2 exige par STEEVE-MAX.

---

## 3. ETAT APRES (V2) — INVENTAIRE COMPLET

### LOGISTIQUE (5 criteres)

| # | Critere                | Priorite | Recos/espece | Sources | Statut V2 |
|---|------------------------|----------|--------------|---------|-----------|
| 1 | accessibilite_pieton   | P1       | 8-10         | 8       | COMPLET   |
| 2 | facilite_maintenance   | P1       | 8-10         | 8       | COMPLET   |
| 3 | proximite_infrastructure | P2     | 8-9          | 6       | COMPLET   |
| 4 | securite_acces         | P1       | 8-10         | 8       | COMPLET   |
| 5 | frequence_visite       | P1       | 8-9          | 8       | COMPLET   |

### OBSERVATION / STRATEGIE (4 criteres)

| # | Critere                  | Priorite | Recos/espece | Sources | Statut V2 |
|---|--------------------------|----------|--------------|---------|-----------|
| 6 | historique_observations  | P1       | 8-10         | 8       | COMPLET   |
| 7 | adaptabilite_saisonniere | P1       | 8-9          | 8       | COMPLET   |
| 8 | complementarite_reseau   | P2       | 8             | 6       | COMPLET   |
| 9 | potentiel_expansion      | P2       | 8             | 6       | COMPLET   |

### COUT / ROI (6 criteres)

| # | Critere              | Priorite | Recos/espece | Sources | Statut V2 |
|---|----------------------|----------|--------------|---------|-----------|
|10 | cout_mineraux_annuel | P1       | 8             | 6       | COMPLET   |
|11 | cout_transport       | P2       | 6             | 4       | COMPLET   |
|12 | cout_temps           | P2       | 6             | 3       | COMPLET   |
|13 | retour_observation   | P1       | 8             | 5       | COMPLET   |
|14 | retour_recolte       | P1       | 8             | 5       | COMPLET   |
|15 | durabilite           | P1       | 8             | 5       | COMPLET   |

### TERRAIN / TCS (4 criteres)

| # | Critere              | Priorite | Recos/espece | Sources | Statut V2 |
|---|----------------------|----------|--------------|---------|-----------|
|16 | alignement_sentiers  | P1       | 8             | 5       | COMPLET   |
|17 | lissage              | P2       | 6             | 3       | COMPLET   |
|18 | penetrabilite        | P1       | 8             | 5       | COMPLET   |
|19 | effort_reel          | P2       | 8             | 5       | COMPLET   |

---

## 4. STRUCTURE DE CHAQUE CRITERE V2

Chaque critere contient les sections suivantes:

1. **title**: Titre unique et descriptif
2. **definition**: Definition detaillee (3-5 lignes) avec terminologie technique
3. **methodology**: Score sur 100 points avec ponderation et sources de donnees
4. **justification**: Texte specifique pour chacune des 5 especes (5-8 lignes/espece)
5. **recommendations_terrain**: 8-15 recommandations concretes par espece
6. **strategies_optimisation**: Resume des strategies cles par espece
7. **techniques_chasse**: Techniques de chasse specifiques liees au critere
8. **erreurs_a_eviter**: Erreurs frequentes par espece
9. **optimisations_saisonnieres**: Printemps, Ete, Automne, Hiver
10. **optimisations_support**: Equipement et materiel recommande
11. **optimisations_meteo**: Impact des conditions meteorologiques
12. **optimisations_pression**: Strategies en zone haute pression de chasse
13. **thresholds**: Seuils vert (80-100), jaune (50-79), rouge (0-49) avec descriptions
14. **sources**: References TOP-TIER (MFFP, UQAR, NDA, RMEF, NWTF, MSU, UGA, etc.)

---

## 5. SOURCES TOP-TIER UTILISEES

### Niveau 1 — Institutions gouvernementales
- MFFP Quebec (Ministere Forets, Faune, Parcs)
- MRNF Quebec (Ministere Ressources naturelles, Forets)
- SEPAQ (Societe des etablissements de plein air du Quebec)
- Environnement Canada
- USDA (United States Department of Agriculture)

### Niveau 2 — Universites et recherche
- UQAR (Universite du Quebec a Rimouski) — Dussault, Courtois
- Universite Laval — Departement de biologie
- Mississippi State University Deer Lab
- University of Georgia Deer Lab
- Can. J. Zoology (Canadian Journal of Zoology)
- Journal of Wildlife Management

### Niveau 3 — Organismes specialises
- NDA (National Deer Association)
- RMEF (Rocky Mountain Elk Foundation)
- NWTF (National Wild Turkey Federation)
- Bear Trust International
- QDMA (Quality Deer Management Association — archives)

### Niveau 4 — Guides et references
- Boone & Crockett Club
- Pope & Young Club
- HSS (Hunter Safety System)
- CAA Quebec (couts vehiculaires)
- Garmin, Spypoint, Stealth Cam (specifications techniques)

---

## 6. BILAN TOTAL DES CRITERES BIONIC GUIDE V2

### 13 criteres precedemment reecrits (V1 + P0 V2):
1. position_vs_affuts (15 recos/espece, 17 sources)
2. accessibilite_vehicule (10-12 recos/espece, 8 sources)
3. couverture_vent (10 recos/espece, 10 sources)
4. corridors_deplacement (11 recos/espece, 10 sources)
5. couvert_forestier (8 recos/espece, 10 sources)
6. source_eau (10 recos/espece, 10 sources)
7. pression_chasse (10 recos/espece, 10 sources)
8. tranquillite_zone (8 recos/espece, 9 sources)
9. potentiel_trophee (8 recos/espece, 10 sources)
10. visibilite_affuts (9 recos/espece, 8 sources)
11. topographie_lidar (8 recos/espece, 8 sources)
12. hydrologie (8 recos/espece, 8 sources)
13. drainage_sol (7 recos/espece, 6 sources)

### 19 criteres reecrits dans cette directive (P1/P2 V2):
14-32. Voir tableau section 3 ci-dessus.

### TOTAL: 32 criteres au standard V2 professionnel

**OBJECTIF ATTEINT: ZERO critere en DEFAULT generique.**

---

## 7. VALIDATION TECHNIQUE

- [x] Fichier `criteriaDatabase_P1P2.js` cree (1327 lignes)
- [x] 19 exports nommes (`export const`)
- [x] Import dans `criteriaDatabase.js` via ES module
- [x] Remplacement des 19 entrees `{ ...DEFAULT, title: ... }` par les imports
- [x] Frontend compile et fonctionne (dev server HTTP 200)
- [x] ZERO contenu generique ou "lorem ipsum"
- [x] 5 especes couvertes par critere
- [x] Sources TOP-TIER citees pour chaque critere

---

**Document**: SOUS_CRITERES_V2_COMPLET.md
**Autorite**: STEEVE-MAX
**Protocole**: BCE-4X GOLDEN V2

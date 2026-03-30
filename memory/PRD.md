# HUNTIQ-V6 — PRD
## PROTOCOLE BCE-4X | STEEVE-MAX-x3200-V6-CORE

---

## 1. Architecture
- **Backend:** FastAPI (Python) sur port 8001
- **Frontend:** React (CRA + craco) sur port 3000
- **Base de donnees:** MongoDB
- **Branche:** `STEEVE-MAX-x3200-V6-CORE`

## 2. Implemente

### Infrastructures
- Logo v5: 128px DANS le header nav, watermark 560px accueil / 1260px premium
- Carte Interactive: erreur 'Cannot read name' CORRIGEE (Bathymetrie purgee)
- PARTAGER global (header App.js + panel SUPRA v2)
- ULTRA-MAX++ Firewall Shapely (7 zones Quebec, 5 endpoints)
- SALINES ULTIME (5 scores, 20 sources, FICHE)
- Scroll GOLDEN toutes pages

### SUPRA v2 — Refonte 100% VERTICAL GOLDEN (30 mars 2026)
- **Structure** : ZERO grid-cols-2, ZERO grid-cols-3, toutes cartes pleine largeur
- **Typographie** : 16px pour TOUS les textes (labels, valeurs, titres)
- **Scroll GOLDEN** : overflow-y-auto avec scrollBehavior smooth
- **Cartes ANALYSE** : Score SUPRA, Gauge ULTRA, Sol, Metabolisme, Vegetation, Hydrologie, Mineraux (barres), Besoins, Ecozone, Recette, Couts — TOUS en vertical
- **Sections collapsibles** : Physiologie, Comportement, Support, Sources — fermes par defaut
- **FICHE** : 5 scores individuels avec barres, Guides, 20 Sources — tous en vertical

### Alignement biologique ORIGNAL (30 mars 2026)
- Store Zustand defaut: ORIGNAL (remplace CHEVREUIL)
- NutritionPointDetailPanel: accepte selectedSpecies prop
- SupraPage: lit species depuis store global
- MonTerritoireBionicPage: passe selectedSpecies au panel
- Ecozone affiche maintenant: "Orignal (Alces americanus)"
- Besoins: "Sortie ravage + croissance bois massifs" (orignal/printemps)

## 3. Fichiers modifies (session courante)
- `/app/frontend/src/components/territoire/NutritionPointDetailPanel.jsx`
- `/app/frontend/src/pages/SupraPage.jsx`
- `/app/frontend/src/pages/MonTerritoireBionicPage.jsx`
- `/app/frontend/src/stores/useBionicStore.js`

## 4. Backlog GELE
- [ ] Purge shadcn/utils
- [ ] Pression historique chasse
- [ ] BSAA-2
- [ ] Merge main — INTERDIT

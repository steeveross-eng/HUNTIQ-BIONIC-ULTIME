# HUNTIQ-V6 — PRD
## PROTOCOLE BCE-4X | STEEVE-MAX-x3200-V6-CORE

---

## 1. Architecture
- **Backend:** FastAPI (Python) sur port 8001
- **Frontend:** React (CRA + craco) sur port 3000
- **Base de donnees:** MongoDB
- **Branche:** `STEEVE-MAX-x3200-V6-CORE`

## 2. Implemente
- Logo v5: 128px DANS le header nav (ZERO superposition), watermark 560px accueil / 1260px premium
- Carte Interactive: erreur 'Cannot read name' CORRIGEE (Bathymetrie integralement purgee)
- PARTAGER global (header App.js + panel SUPRA v2)
- ULTRA-MAX++ Firewall Shapely (7 zones Quebec, 5 endpoints)
- SALINES ULTIME (5 scores, 20 sources, FICHE)
- Scroll GOLDEN toutes pages
- **SUPRA v2 ANALYSE — 100% VERTICAL COMPACT GOLDEN (30 mars 2026)**
  - ZERO grid-cols-2, ZERO grid-cols-3
  - Score SUPRA, Gauge ULTRA, Sol, Metabolisme, Vegetation, Hydrologie, Mineraux, Physiologie, Besoins, Ecozone, Recette, Couts, Preuves — TOUS pleine largeur vertical
  - Padding reduit: p-5 -> px-4 py-3, tailles icones et polices compactees
- **SUPRA v2 FICHE — 100% VERTICAL (confirme)**
  - 5 scores + guides + 20 sources — pleine largeur

## 3. Backlog GELE
- [ ] Purge shadcn/utils
- [ ] Pression historique chasse
- [ ] BSAA-2
- [ ] Merge main — INTERDIT

## 4. Fichiers cles modifies
- `/app/frontend/src/components/territoire/NutritionPointDetailPanel.jsx` — AnalyseTab 100% vertical
- `/app/frontend/src/components/BionicLogo.jsx` — 128px header, 560px global, 1260px premium
- `/app/frontend/src/App.js` — Header 136px, logo integre
- `/app/frontend/src/config/mapSources.js` — Bathymetrie purgee

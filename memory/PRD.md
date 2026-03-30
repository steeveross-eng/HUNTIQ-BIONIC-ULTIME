# HUNTIQ-V6 — PRD
## PROTOCOLE BCE-4X | STEEVE-MAX-x3200-V6-CORE

---

## 1. Architecture
- **Backend:** FastAPI (Python) sur port 8001
- **Frontend:** React (CRA + craco) sur port 3000
- **Base de donnees:** MongoDB
- **Branche:** `STEEVE-MAX-x3200-V6-CORE`

## 2. Implemente
- Logo v5: 128px DANS le header nav, watermark 560px accueil / 1260px premium
- Carte Interactive: erreur 'Cannot read name' CORRIGEE (Bathymetrie purgee)
- PARTAGER global (header App.js + panel SUPRA v2)
- ULTRA-MAX++ Firewall Shapely (7 zones Quebec, 5 endpoints)
- SALINES ULTIME (5 scores, 20 sources, FICHE)
- Scroll GOLDEN toutes pages

### REFONTE DASHBOARD-DENSE SUPRA v2 (30 mars 2026)
- **ANALYSE:** Redesign complet en style Dashboard dense
  - ROW 1: Score SUPRA + Gauge ULTRA (grid-cols-2 compact)
  - ROW 2: 4 Moteurs (Sol, Metabolisme, Vegetation, Hydrologie) en grid 2x2 MicroCards
  - ROW 3: Mineraux mini-bars (col-span-3) + Besoins/Ecozone (col-span-2)
  - ROW 4: Recette + Couts (grid-cols-2)
  - ROW 5: Physiologie, Comportement, Support, Sources (collapsibles fermes)
  - TOUT visible en UNE PAGE sans scroll
- **FICHE:** Redesign identique
  - Score global 68/B compact
  - 5 scores avec mini-bars colorees dans 1 card
  - Details en grid 2x2
  - 3 Guides en grid 2-col
  - 20 Sources collapsibles
  - TOUT visible en UNE PAGE

## 3. Composants redesignes
- GaugeMini: SVG 56x56px avec texte integre
- MicroCard: px-2.5 py-2, text-[10px], icones 12px
- Card: px-3 py-2 (reduit de px-4 py-3)
- CollapsibleSection: py-1.5, text-[10px]

## 4. Backlog GELE
- [ ] Purge shadcn/utils
- [ ] Pression historique chasse
- [ ] BSAA-2
- [ ] Merge main — INTERDIT

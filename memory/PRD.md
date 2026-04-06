# PRD — HUNTIQ BIONIC V6 | BCE-4X GOLDEN V6+

## Probleme original
Application de routage terrain pour la chasse (affuts, corridors, zones) avec pathfinding A* et integration OSM/Overpass. Gouvernance stricte BCE-4X GOLDEN V6+ sous autorite COMMANDANT STEEVE-MAX.

## Architecture
- Backend: FastAPI + A* Pathfinding + OSM/Overpass
- Frontend: React 19 + Leaflet Maps
- Modules: 84+ engines backend (BDRE, Terrain Nav, Hunt Orchestrator, Access Engine, etc.)
- Governance: BCE-4X / STEEVE-MAX / ZERO LOSS / ZERO REGRESSION

## Ce qui a ete implemente

### Sessions precedentes
- [x] BCE-4X Territorial Exclusions
- [x] Terrain Graph fragment connector
- [x] STEEVE-MAX Terrain Guidance
- [x] Multi-engine BDRE integration
- [x] NORME OFFICIELLE A->L — Cache Institutionnel BCE-4X
- [x] BUG FIX: Alimentation 3/4 -> 4/4
- [x] BUG FIX: Routes V-shape -> routes directes
- [x] DESACTIVATION SECURISEE ACCES AUX AFFUTS (Archive: /LEGACY_ACCESS_AFFUTS/)
- [x] VALIDATION AUTONOMIE TOTALE (7/7 tests PASS)

### Session 2026-04-06 (fork actuel)
- [x] P0 — MODULE PEDAGOGIQUE ULTRA COMPLET (NON-CONFORMITE CORRIGEE)
  - Fichier: `/app/frontend/src/components/territoire/PedagogieModule.jsx` (32.5 KB)
  - Integre dans: `NutritionPointDetailPanel.jsx` AnalyseTab
  - Flag: `PEDAGOGIE_SALINE_ENABLED = true`
  - POSITIONNEMENT CORRIGE: Immediatement apres la grille 3 colonnes, AVANT les sections historiques
  - Separateur dore "SECTION PEDAGOGIQUE" + Header haute visibilite (18px, bordure doree, glow)
  - 10 SECTIONS CONFORMES:
    1. Besoins mineraux par groupe (4 groupes: Males alpha, Femelles, Veaux, Periode chasse)
    2. Besoins en proteines (500g/3j males, 300-400g femelles, 200-300g veaux)
    3. Oligo-elements essentiels (Zn, Cu, Se, Fe, Mn, Iode)
    4. Solutions terrain (Soya, luzerne, trefle, chicoree, mais, pommes, betteraves)
    5. Comparatif visuel des supports (Souche decomposition 98 -> Baton 30)
    6. Strategies d'optimisation (Mini-champ, Synergies, Territoriales, Comportementales, Saisonnieres)
    7. Gestion pre-chasse optimisee (5 regles)
    8. Hyper-attractive periode de chasse (6 criteres ELITE)
    9. A EVITER (9 erreurs courantes)
    10. Capsule narrative "L'Histoire de ta saline" (orignal/chevreuil x 4-6 saisons)
  - Sections historiques PRESERVEES apres le module (ZERO REMPLACEMENT)
  - STANDARD GOLDEN respecte (cards, collapsibles, palette BIONIC, icones)
  - Validation screenshot: 10/10 sections visibles ✅

- [x] P1 — BOUTON EXPORT PDF
  - html2canvas + jsPDF integres
  - Export multi-page A4 avec footer BCE-4X
  - Bouton vert dans le header MODULE PEDAGOGIQUE
  - Validation: bouton visible ✅

- [x] P0 — AUDIT QUALITE
  - BDRE Health: OPERATIONNEL (V2, 17 endpoints, 8 composants)
  - Saline Intelligence: OPERATIONNEL (7 moteurs)
  - Nutrition-V6: OPERATIONNEL (4 modules, 13 V5 engines)
  - BDRE Dashboard: OPERATIONNEL (16 sources, 11 healthy)
  - Scoring: OPERATIONNEL (retourne donnees)
  - Erreurs backend: V5 legacy bloque (INTENTIONNEL)
  - Erreurs frontend: ZERO
  - Coherence BDRE <-> SUPRA: CONFORME (endpoints actifs, donnees synchronisees)
  - Rendu visuel ANALYSE: CONFORME (MODULE PEDAGOGIQUE + sections historiques)

## Backlog

### P0 (Aucun)

### P1 (En attente directive STEEVE-MAX)
- Confirmation utilisateur MODULE PEDAGOGIQUE + PDF

### P2 (GELE)
- M5 Offline Mode Ultra
- BSAA-2 Social Ads Automation
- Merge Work1 -> main (INTERDIT)

# PRD — HUNTIQ BIONIC V6 | BCE-4X GOLDEN V6+

## Probleme original
Application de routage terrain pour la chasse (affuts, corridors, zones) avec pathfinding A* et integration OSM/Overpass. Gouvernance stricte BCE-4X GOLDEN V6+ sous autorite COMMANDANT STEEVE-MAX.

## Architecture
- Backend: FastAPI + A* Pathfinding + OSM/Overpass
- Frontend: React 19 + Leaflet Maps
- Modules: 84+ engines backend (BDRE, Terrain Nav, Hunt Orchestrator, Access Engine, etc.)
- Governance: BCE-4X / STEEVE-MAX / ZERO LOSS / ZERO REGRESSION

## Ce qui a ete implemente

### Session 2026-04-06
- [x] BCE-4X Territorial Exclusions
- [x] Terrain Graph fragment connector
- [x] STEEVE-MAX Terrain Guidance
- [x] Multi-engine BDRE integration
- [x] P2 Gel complet

### Session 2026-04-07
- [x] NORME OFFICIELLE A->L — Cache Institutionnel BCE-4X
- [x] BUG FIX: Alimentation 3/4 -> 4/4
- [x] BUG FIX: Routes V-shape -> routes directes
- [x] DESACTIVATION SECURISEE ACCES AUX AFFUTS
  - Archive: `/app/LEGACY_ACCESS_AFFUTS/` (66 fichiers, 2.7 MB)
  - MODE OFF Backend + Frontend
  - Donnees preservees (non supprimees)
- [x] VALIDATION AUTONOMIE TOTALE
  - Affuts: AUTONOME (suggestions, scores, recommandations)
  - Salines: AUTONOME (4/4, pipeline independant)
  - Zones contamination: AUTONOME (polygone 15 points)
  - Corridors deplacement: AUTONOME (BDRE 17 endpoints)
  - Cache institutionnel: AUTONOME (CONFORME)
  - Import conditionnel moteur acces (try/except)
  - 7/7 tests integrite PASS

### Session 2026-04-06 (fork)
- [x] MODULE PEDAGOGIQUE — Integration ULTRA COMPLETE dans onglet ANALYSE
  - Fichier cree: `/app/frontend/src/components/territoire/PedagogieModule.jsx`
  - Integre dans: `/app/frontend/src/components/territoire/NutritionPointDetailPanel.jsx` (AnalyseTab)
  - Flag: `PEDAGOGIE_SALINE_ENABLED = true`
  - 10 sections implementees:
    1. Besoins mineraux par groupe (4 groupes: Males alpha, Femelles, Veaux, Periode chasse)
    2. Besoins en proteines (500g/3j males, 300-400g femelles, 200-300g veaux)
    3. Oligo-elements essentiels (Zn, Cu, Se, Fe, Mn, Iode)
    4. Solutions terrain (Soya, luzerne, trefle, chicoree, mais, pommes, betteraves)
    5. Comparatif visuel des supports (Souche decomposition 98 -> Baton 30)
    6. Strategies d'optimisation (Mini-champ, Synergies, Territoriales, Comportementales, Saisonnieres)
    7. Gestion pre-chasse optimisee (5 regles)
    8. Hyper-attractive periode de chasse (6 criteres ELITE)
    9. A EVITER (9 erreurs courantes)
    10. Capsule narrative "L'Histoire de ta saline" (contextuelle espece/saison)
  - STANDARD GOLDEN respecte (cards, collapsibles, palette BIONIC)
  - ZERO REMPLACEMENT du contenu existant — ENRICHISSEMENT UNIQUEMENT
  - Validation visuelle: PASS (screenshot confirme les 10 sections rendues)
  - 100% AUTONOME — aucun impact sur BDRE, corridors, zones, affuts

## Backlog

### P0 (Aucun)

### P1 (En attente directive STEEVE-MAX)
- Confirmation utilisateur MODULE PEDAGOGIQUE

### P2 (GELE)
- M5 Offline Mode Ultra
- BSAA-2 Social Ads Automation
- Merge Work1 -> main (INTERDIT)

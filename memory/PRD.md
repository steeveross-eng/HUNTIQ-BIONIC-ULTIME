# PRD — HUNTIQ BIONIC V6 | BCE-4X GOLDEN V6+

## Probleme original
Application de routage terrain pour la chasse avec pathfinding A* et integration OSM/Overpass. Gouvernance stricte BCE-4X GOLDEN V6+.

## Architecture
- Backend: FastAPI + A* Pathfinding + OSM/Overpass
- Frontend: React 19 + Leaflet Maps
- Modules: 84+ engines backend
- Governance: BCE-4X / STEEVE-MAX / ZERO LOSS / ZERO REGRESSION

## Ce qui a ete implemente

### Sessions precedentes
- [x] BCE-4X Territorial Exclusions + Terrain Graph + STEEVE-MAX Guidance
- [x] Multi-engine BDRE integration
- [x] NORME OFFICIELLE A->L Cache Institutionnel
- [x] BUG FIX: Alimentation 3/4 -> 4/4 + Routes V-shape
- [x] DESACTIVATION SECURISEE ACCES AUX AFFUTS
- [x] VALIDATION AUTONOMIE TOTALE (7/7 tests PASS)

### Session 2026-04-06 (fork actuel)

#### P0 — UNIFICATION DES SCORES (SUPRA_SCORE UNIFIE)
- [x] Backend: RecipeRequest accepte lat, lng, saline_score
- [x] Endpoint /supra-panel utilise saline_score comme score_global principal
- [x] Score mineral x5100 conserve comme score_mineral (complementaire)
- [x] score_source: "SUPRA_UNIFIED" confirme le moteur unifie
- [x] Frontend: NutritionPointDetailPanel passe np.score + lat + lng au SUPRA panel
- [x] RESULTAT: Score carte = Score SUPRA = IDENTIQUE (teste: 71=71)
- [x] random.uniform NON utilise dans V2 (deja deterministe via _seed MD5)

#### P0 — UNIFICATION ERGONOMIQUE (Grille 3 colonnes)
- [x] AnalyseTab restructure en 3 niveaux:
  - Niveau 1 (Resume): Score SUPRA UNIFIE + badge UNIFIE + Score mineral + 7 Moteurs + Besoins
  - Niveau 2 (Analyse): Sol/Pedologie + Mineraux barres + Recette + Couts
  - Niveau 3 (Pedagogie): MODULE PEDAGOGIQUE grille 3x3 (9 cards)
- [x] Collapsibles historiques transformes en cards 3 colonnes (Physiologie | Comportement | Support)
- [x] Sources scientifiques en card compacte
- [x] Zero rupture visuelle entre les niveaux

#### P0 — MODULE PEDAGOGIQUE
- [x] PedagogieModule.jsx en grille 3 colonnes STANDARD GOLDEN
- [x] 9 cards + capsule narrative + bouton PDF + badge ULTRA
- [x] Expansion inline pleine largeur sur clic

#### P0 — AUDIT QUALITE
- [x] 10/10 points audites, 0 critique, 3 mineures documentees
- [x] Rapport: /app/memory/AUDIT_QUALITE_ALIMENTATION_BCE4X.md

#### P0 — HARMONISATION DES ONGLETS
- [x] Les 5 onglets utilisent deja des grilles 3 colonnes:
  - ANALYSE: 3-col + pedagogie 3x3 + premium 3-col
  - FICHE: 3-col (Logistique/GrosMales | Strategique/CoutROI/TCS | Plans/Sol/Sources)
  - INTELLIGENCE: 3-col produits
  - COMPAREZ: 3-col comparaison
  - COMMANDEZ: 3-col (Recette | Produits | Panier)

## Backlog

### P0 (Aucun — tout livre)

### P1 (En attente directive STEEVE-MAX)
- Confirmation harmonisation x1000%
- Test export PDF

### P2 (GELE)
- M5 Offline Mode Ultra
- BSAA-2 Social Ads Automation
- Merge Work1 -> main (INTERDIT)

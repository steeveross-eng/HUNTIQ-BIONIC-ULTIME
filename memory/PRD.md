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

### Session 2026-04-06 (fork 3 — BIONIC_REWRITE_P0)

#### P0 — RAPPORT LOGIQUE GLOBALE BIONIC
- [x] Partie 1: Logique salines (generation, scoring, selection, affichage) — LIVRE
- [x] Partie 2: Logique affuts (score 14.2, absence seuil, classification) — LIVRE
- [x] Failles F1-F4 identifiees et documentees

#### P0 — SECURISATION TOTALE PRE-REFONTE
- [x] Branche BIONIC_STABLE_V6_LOCK creee (snapshot immutable)
- [x] Branche BIONIC_REWRITE_P0 creee (refonte controlee)
- [x] Manifeste sanctuarisation: /app/memory/BIONIC_STABLE_V6_LOCK_MANIFEST.md
- [x] Gel operations: /app/memory/GEL_OPERATIONS_P0.md
- [x] Plan technique P0: /app/memory/PLAN_TECHNIQUE_P0_REFONTE.md

#### P0-C — IMPLEMENTATION MOTEURS V3/V2 (valide par STEEVE-MAX)
- [x] Moteur SALINES V3: Critere Eau → distance reelle OSM (30-80m/80-150m/>150m)
- [x] Moteur SALINES V3: Critere Accessibilite → distance reelle sentier OSM (remplace MD5)
- [x] Moteur SALINES V3: Critere Habitat → calcul composite terrain reel (remplace MD5)
- [x] Moteur SALINES V3: criteres_sources tracable dans chaque candidat
- [x] Moteur AFFUTS V2: Seuils institutionnels (rejet <30, badge <50, recommande >=50)
- [x] Moteur AFFUTS V2: Classification (rejected/a_eviter/recommended)
- [x] Moteur AFFUTS V2: Filtre rejet dans recommend_blinds()
- [x] Orchestrateur: Propagation champ classification
- [x] Frontend: Badge "A EVITER" rouge barre pour affuts 30-49
- [x] Frontend: Rejet visuel des affuts "rejected" (double securite)
- [x] Rapport: /app/memory/P0C_RAPPORT_IMPLEMENTATION.md

## Backlog

### P0 (En attente validation STEEVE-MAX)
- P0-E: Tests terrain (3 waypoints, 3 analyses)
- P0-F: Verification integration frontend badges
- P0-G: Audit SUPRA + BDRE + UX + Performance
- P0-H: Audit regression (comparaison V2/V3, V1.5/V2)

### P1 (En attente directive STEEVE-MAX)
- Confirmation harmonisation x1000%
- Test export PDF

### P2 (GELE)
- M5 Offline Mode Ultra
- BSAA-2 Social Ads Automation
- Merge Work1 -> main (INTERDIT)

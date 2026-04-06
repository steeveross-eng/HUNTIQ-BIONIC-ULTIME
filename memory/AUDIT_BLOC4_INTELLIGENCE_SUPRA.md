# BLOC 4 — AUDIT COMPLET: INTELLIGENCE / TABLEAU DE BORD / SUPRA
## BCE-4X GOLDEN V6+ | ORDONNANCE STEEVE-MAX 2026-04-06
## BRANCHE: BIONIC_REWRITE_P0

---

## STATUT : LIVRE — EN ATTENTE VALIDATION STEEVE-MAX

---

# ================================================================
# FICHE MODULE 1 — INTELLIGENCE
# ================================================================

## 1.1 Composants identifies

| Composant | Fichier | Lignes | Role |
|-----------|---------|--------|------|
| IntelligenceDashboard | `frontend/src/components/territoire/IntelligenceDashboard.jsx` | 366 | Cockpit unifie V6-CORE (22 moteurs), panel lateral carte |
| IntelligenceV6Page | `frontend/src/pages/intelligence/IntelligenceV6Page.jsx` | 214 | Dashboard page autonome (M3+M4 widgets) |
| intelligence_core.py | `backend/modules/bionic_ecological_engine/intelligence_core.py` | 593 | Moteur ecologique unifie (sol, hydro, veg, mineraux) |
| SolunarChart | `frontend/src/components/territoire/intelligence/SolunarChart.jsx` | ~120 | Widget lunaire/solaire |

## 1.2 Flux de donnees

```
IntelligenceDashboard (panel carte)
  └── useBionicStore → fetchSummary, fetchForecast, fetchPlan, fetchSolunar
       └── /api/v1/bionic/summary, /api/v1/bionic/forecast
       └── /api/v1/bionic/plan, /api/v1/bionic/solunar

IntelligenceV6Page (page autonome)
  └── DataFusionLayer (service centralisé)
       └── fetchConsolidatedView → /api/v1/score-consolide/point
       └── fetchScoreConsolide → /api/v1/score-consolide/point
       └── fetchTrends → DataFusionLayer interne
       └── fetchCorrelationMatrix → DataFusionLayer interne
       └── fetchBestTimes → DataFusionLayer interne
       └── fetchTimeSeries → DataFusionLayer interne
       └── fetchHunterProfile → /api/v6/supra/advanced
       └── fetchContextualAdvice → /api/v6/supra/advanced
       └── /api/v1/bdre/dashboard, /api/v1/bdre/sources
```

## 1.3 Interactions

- **IntelligenceDashboard**: Ouvert depuis la barre d'outils territoire, consomme le store Zustand, affiche sommaire/forecast/plan/lunaire
- **IntelligenceV6Page**: Page autonome accessible via navigation, consomme DataFusionLayer, affiche 9 widgets (W1-W12)

## 1.4 Doublons identifies

| Doublon | Composant A | Composant B | Severite |
|---------|-------------|-------------|----------|
| Score consolide | IntelligenceV6Page (W1) | IntelligenceDashboard (sommaire) | MOYENNE |
| Lunaire/Solaire | SolunarChart (IntelligenceDashboard) | BestTimesWidget (IntelligenceV6Page) | FAIBLE |

---

# ================================================================
# FICHE MODULE 2 — TABLEAU DE BORD (Page principale)
# ================================================================

## 2.1 Composants identifies

| Composant | Fichier | Lignes | Role |
|-----------|---------|--------|------|
| SalinesFichePanel | `frontend/src/modules/dashboard/SalinesFichePanel.jsx` | 252 | Fiche saline 5 scores + 20 sources |
| GroupDashboard | `frontend/src/components/territoire/GroupDashboard.jsx` | ~300 | Dashboard groupe de chasse |
| SeasonalConditionsWidget | `frontend/src/components/territoire/SeasonalConditionsWidget.jsx` | ~150 | Widget conditions saisonnieres |
| StandDetailPanel | `frontend/src/components/territoire/StandDetailPanel.jsx` | ~200 | Detail affut |

## 2.2 Flux de donnees

```
Carte principale (TerritoireMap)
  ├── NutritionPointsLayer → clic saline → NutritionPointDetailPanel (SUPRA)
  ├── StandsMapLayer → clic affut → StandDetailPanel
  ├── Toolbar → ouvrir IntelligenceDashboard
  └── SalinesFichePanel (accessible depuis navigation)
       └── /api/alimentation/saline-fiche → backend scoring pipeline
```

## 2.3 Interactions

- La carte est le HUB central
- Chaque clic sur un marqueur ouvre un panel contextuel
- Les toolbars ouvrent des panels lateraux (Intelligence, Conditions)

## 2.4 Dependances critiques

| Module | Depend de | Type |
|--------|-----------|------|
| SalinesFichePanel | /api/alimentation/saline-fiche | API REST |
| StandDetailPanel | Donnees calculees par choix_affuts.py | Props directes |
| NutritionPointsLayer | /api/v4/alimentation/analyze | API REST |

---

# ================================================================
# FICHE MODULE 3 — SUPRA (Onglet ANALYSE)
# ================================================================

## 3.1 Composants

| Composant | Fichier | Lignes | Role |
|-----------|---------|--------|------|
| NutritionPointDetailPanel | `frontend/src/components/territoire/NutritionPointDetailPanel.jsx` | 1257 | SUPRA v2 Moteur Unifie — 5 onglets |
| PedagogieModule | `frontend/src/components/territoire/PedagogieModule.jsx` | ~200 | Grille 3x3 pedagogique |
| NutritionIntelligenceSupra | `frontend/src/pages/NutritionIntelligenceSupra.jsx` | 501 | Page SUPRA PREMIUM autonome |

## 3.2 Onglet ANALYSE — Contenu exact

```
NIVEAU 1 (Resume):
  ├── Score SUPRA UNIFIE (gauge) + badge
  ├── Score mineral (complementaire)
  ├── 7 Moteurs ULTRA (barres + scores)
  └── Besoins par espece/saison

NIVEAU 2 (Analyse detaillee):
  ├── Sol/Pedologie
  ├── Mineraux (barres individuelles)
  ├── Recette optimale
  └── Couts

NIVEAU 3 (Pedagogie):
  └── PedagogieModule (grille 3x3)
       ├── 9 cards: Physiologie | Comportement | Support
       ├── Capsule narrative
       ├── Bouton PDF
       └── Badge ULTRA
```

## 3.3 Backend SUPRA

| Endpoint | Fichier | Role |
|----------|---------|------|
| POST /api/v4/alimentation/analyze | scoring_pipeline/alimentation_v4 | Analyse terrain V4 (9 criteres) |
| GET /api/v6/supra/advanced/terrain-relevance | engines/supra_advanced/router.py | Pertinence terrain |
| GET /api/v6/supra/advanced/risk-assessment | engines/supra_advanced/router.py | Evaluation risques |
| GET /api/v6/supra/advanced/recommendation | engines/supra_advanced/router.py | Recommandations intelligentes |
| supra_bridge.py | modules/strategy_master_engine/services | Pont SUPRA <-> Strategy |

## 3.4 Doublons SUPRA

| Doublon | Composant A | Composant B | Severite |
|---------|-------------|-------------|----------|
| Narratifs physiologie | NutritionPointDetailPanel.PHYSIOLOGY_DATA | NutritionIntelligenceSupra.PHYSIOLOGY_DATA | CRITIQUE — Donnees identiques dupliquees |
| Narratifs males | NutritionPointDetailPanel.MALE_BEHAVIOR | NutritionIntelligenceSupra.MALE_BEHAVIOR | CRITIQUE — Donnees identiques dupliquees |
| Support hierarchy | NutritionPointDetailPanel.SUPPORT_HIERARCHY | NutritionIntelligenceSupra.SUPPORT_HIERARCHY | HAUTE — Donnees identiques |
| Constantes couleur | NutritionPointDetailPanel.BIONIC | NutritionIntelligenceSupra.BIONIC | HAUTE — Palette dupliquee |
| SPECIES_OPTIONS | IntelligenceV6Page | NutritionIntelligenceSupra | FAIBLE |

---

# ================================================================
# FICHE MODULE 4 — SUPRA (Onglet FICHE)
# ================================================================

## 4.1 Composants

| Composant | Fichier | Role |
|-----------|---------|------|
| Onglet "Fiche" dans NutritionPointDetailPanel | Meme fichier | Sous-onglet de SUPRA v2 |
| SalinesFichePanel | modules/dashboard/SalinesFichePanel.jsx | Fiche saline autonome |

## 4.2 Contenu FICHE

```
FICHE (dans NutritionPointDetailPanel):
  ├── Logistique (3-col)
  ├── Gros Males
  ├── Strategique
  ├── Cout / ROI
  ├── TCS (Terrain)
  ├── Plans sol
  └── Sources scientifiques

SalinesFichePanel (autonome):
  ├── 5 Scores (Logistique, Gros Males, Strategique, Cout/ROI, TCS)
  ├── Score global
  └── 20 Sources
```

## 4.3 Doublon FICHE

| Doublon | Composant A | Composant B | Severite |
|---------|-------------|-------------|----------|
| Scores 5 axes | NutritionPointDetailPanel.FicheTab | SalinesFichePanel | HAUTE — Logique de scoring quasi-identique |

---

# ================================================================
# TABLEAU COMPARATIF
# ================================================================

| Critere | INTELLIGENCE Dashboard | INTELLIGENCE V6 Page | SUPRA ANALYSE | SUPRA FICHE | SalinesFichePanel |
|---------|----------------------|---------------------|---------------|-------------|-------------------|
| Type | Panel lateral | Page autonome | Onglet dans panel | Onglet dans panel | Panel autonome |
| Source donnees | useBionicStore | DataFusionLayer | API V4 + SUPRA | API saline-fiche | API saline-fiche |
| Score consolide | Oui | Oui (W1) | Oui (gauge) | Non | Oui (global) |
| Mineraux | Non | Non | Oui (barres) | Non | Non |
| Pedagogie | Non | Non | Oui (3x3) | Non | Non |
| Physiologie narrative | Non | Non | Oui | Non | Non |
| 5 scores axes | Non | Non | Non | Oui | Oui |
| Lunaire/Solaire | Oui | Oui (W3) | Non | Non | Non |
| Produits | Non | Non | Oui (onglet Intel) | Non | Non |
| Panier | Non | Non | Oui (onglet Commandez) | Non | Non |

---

# ================================================================
# SCHEMA DES FLUX
# ================================================================

```
UTILISATEUR
    │
    ├── [CARTE] ──────────────────────────┐
    │     ├── clic saline ──────> NutritionPointDetailPanel (SUPRA v2)
    │     │                        ├── Onglet ANALYSE ──> API V4 + SUPRA Advanced
    │     │                        ├── Onglet FICHE ──> API saline-fiche
    │     │                        ├── Onglet INTELLIGENCE ──> produits scoring
    │     │                        ├── Onglet COMPAREZ ──> comparaison produits
    │     │                        └── Onglet COMMANDEZ ──> Stripe cart
    │     │
    │     ├── clic affut ──────> StandDetailPanel
    │     │                       └── Donnees choix_affuts.py (V2 scores)
    │     │
    │     └── toolbar ─────────> IntelligenceDashboard (panel lateral)
    │                             └── useBionicStore → 4 API endpoints
    │
    ├── [NAV MENU]
    │     ├── /intelligence ───> IntelligenceV6Page
    │     │                       └── DataFusionLayer → 10 API endpoints
    │     ├── /supra ──────────> NutritionIntelligenceSupra (PREMIUM standalone)
    │     └── /dashboard ──────> SalinesFichePanel (si accessible)
    │
    └── [API BACKEND]
          ├── /api/v4/alimentation/analyze ──> salines_v4.py (V4)
          ├── /api/v6/supra/advanced/* ──────> supra_advanced/router.py
          ├── /api/v1/bdre/dashboard ────────> bdre/router.py
          ├── /api/v1/hunt/orchestrate ──────> hunt_orchestrator (V2)
          ├── /api/v1/corridor-unified/* ────> corridor_unified (BLOC 1 NOUVEAU)
          ├── /api/v1/hunt/contamination-zones → BLOC 2 NOUVEAU
          └── /api/v1/relocation/* ──────────> relocation (BLOC 3 NOUVEAU)
```

---

# ================================================================
# LISTE DES DOUBLONS
# ================================================================

| # | Doublon | Fichier A | Fichier B | Severite | Action recommandee |
|---|---------|-----------|-----------|----------|-------------------|
| D1 | PHYSIOLOGY_DATA | NutritionPointDetailPanel.jsx | NutritionIntelligenceSupra.jsx | CRITIQUE | Extraire dans shared/data/physiology.js |
| D2 | MALE_BEHAVIOR | NutritionPointDetailPanel.jsx | NutritionIntelligenceSupra.jsx | CRITIQUE | Extraire dans shared/data/behavior.js |
| D3 | SUPPORT_HIERARCHY | NutritionPointDetailPanel.jsx | NutritionIntelligenceSupra.jsx | HAUTE | Extraire dans shared/data/support.js |
| D4 | BIONIC palette | NutritionPointDetailPanel.jsx | NutritionIntelligenceSupra.jsx | HAUTE | Centraliser dans shared/theme/bionic.js |
| D5 | SPECIES_OPTIONS | IntelligenceV6Page.jsx | NutritionIntelligenceSupra.jsx | FAIBLE | Centraliser dans shared/constants.js |
| D6 | Score consolide | IntelligenceDashboard | IntelligenceV6Page | MOYENNE | Fusionner ou rediriger |
| D7 | Fiche 5 scores | NutritionPointDetailPanel (Fiche) | SalinesFichePanel | HAUTE | Fusionner composant |
| D8 | _haversine_m | corridor_optimizer_v2, vent_odeurs, choix_affuts, bdre_integration | x4 fichiers backend | FAIBLE | Extraire utils/geo.py |

---

# ================================================================
# MATRICE RACI
# ================================================================

| Activite | STEEVE-MAX | Agent E1 | Frontend | Backend |
|----------|-----------|----------|----------|---------|
| Validation architecture | A (Approuve) | R (Execute) | I | I |
| Extraction doublons D1-D4 | A | R | C | - |
| Fusion Intelligence Dashboard + V6 | A | R | R | I |
| Fusion SUPRA FICHE + SalinesFichePanel | A | R | R | C |
| Extraction _haversine_m | A | R | - | R |
| Tests regression | A | R | C | C |
| Validation ZERO REGRESSION | A | R | I | I |

(R=Responsable, A=Approbateur, C=Consulte, I=Informe)

---

# ================================================================
# PLAN DE FUSION SYSTEMIQUE
# ================================================================

## Phase F1 — Extraction donnees partagees (PRIORITE HAUTE)

Creer `/frontend/src/shared/data/`:
- `physiology.js` — PHYSIOLOGY_DATA unique
- `behavior.js` — MALE_BEHAVIOR unique
- `support.js` — SUPPORT_HIERARCHY unique

Creer `/frontend/src/shared/theme/`:
- `bionic.js` — Palette BIONIC unifiee

Creer `/frontend/src/shared/constants.js`:
- SPECIES_OPTIONS, SEASON_OPTIONS unifies

Impact: ZERO regression (extraction pure, pas de logique modifiee)

## Phase F2 — Fusion Intelligence (PRIORITE MOYENNE)

| Action | Risque | Impact |
|--------|--------|--------|
| IntelligenceDashboard reste le panel carte | Faible | Aucun changement UX |
| IntelligenceV6Page absorbe les widgets communs | Faible | Consolidation |
| Supprimer doublons lunaire/score consolide | Faible | Nettoyage |

## Phase F3 — Fusion FICHE (PRIORITE MOYENNE)

| Action | Risque | Impact |
|--------|--------|--------|
| SalinesFichePanel devient composant reutilisable | Moyen | Changement import |
| NutritionPointDetailPanel.FicheTab utilise SalinesFichePanel | Moyen | Factorisation |

## Phase F4 — Extraction backend geo utils (PRIORITE FAIBLE)

Creer `/backend/utils/geo.py`:
- `haversine_m(lat1, lng1, lat2, lng2)` unique
- Tous les modules importent depuis utils/geo

---

# ================================================================
# RECOMMANDATIONS INSTITUTIONNELLES
# ================================================================

1. **URGENCE CRITIQUE**: Les doublons D1 et D2 (PHYSIOLOGY_DATA, MALE_BEHAVIOR)
   representent un risque de desynchronisation. Si un texte est modifie dans un
   fichier mais pas l'autre, l'application affiche des informations contradictoires.
   → Extraction immediate recommandee.

2. **ARCHITECTURE**: Le pattern actuel (panel lateral + page autonome + onglets)
   est fonctionnel mais fragmente. La consolidation en un HUB unique avec
   routes internes reduirait la charge de maintenance.

3. **PERFORMANCE**: NutritionPointDetailPanel.jsx (1257 lignes) est le fichier
   frontend le plus volumineux. Un decoupage en sous-composants par onglet
   ameliorerait la maintenabilite sans impacter l'UX.

4. **BLOCS 1/2/3**: Les nouveaux modules CORRIDOR_UNIFIED, BDRE PEDAGOGIQUE,
   et RELOCALISATION AUTOMATIQUE sont OPERATIONNELS et testes API.
   Integration frontend recommandee dans le SUPRA ANALYSE (ContaminationLayer)
   et dans le StandDetailPanel (RelocationPanel).

---

## SIGNATURES

| Role | Identifiant |
|------|-------------|
| Autorite | COMMANDANT STEEVE-MAX |
| Agent executant | EMERGENT E1 |
| Date | 2026-04-06 |
| Statut | **EN ATTENTE VALIDATION** |

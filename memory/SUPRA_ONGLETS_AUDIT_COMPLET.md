# SUPRA_ONGLETS_AUDIT_COMPLET.md
# ============================================================
# AUDIT INSTITUTIONNEL TOTAL — SUPRA v2 & 5 ONGLETS
# ============================================================
# Protocole: BCE-4X-GLOBAL-PLUS-TOTAL
# Autorite: COMMANDANT STEEVE-MAX
# Branche: BIONIC_REWRITE_P0
# Date: 2026-02-07
# Statut: AUDIT COMPLET — EN ATTENTE DE VALIDATION
# ============================================================

---

## SOMMAIRE EXECUTIF

Le present rapport constitue l'audit institutionnel total du module SUPRA v2
et de ses 5 onglets associes, tel qu'ordonne par le Commandant STEEVE-MAX.

**Perimetre BCE-4X audite (6 entites):**
1. **SUPRA** — Entite parente (page/panneau SUPRA v2)
2. **ANALYSE** — Onglet 1
3. **FICHE** — Onglet 2
4. **INTELLIGENCE** — Onglet 3
5. **COMPAREZ** — Onglet 4
6. **COMMANDEZ** — Onglet 5 (incluant sous-module BOUTIQUE)

**Verdict global: 14 ecarts identifies | 6 recommandations de reconstruction x1000%**

---

## 1. INVENTAIRE STRUCTURAL

### 1.1 Fichier Frontend Principal

| Attribut | Valeur |
|---|---|
| **Fichier** | `frontend/src/components/territoire/NutritionPointDetailPanel.jsx` |
| **Lignes** | 1259 |
| **Composant principal** | `NutritionPointDetailPanel` |
| **Conteneur** | `PinnablePanel` (365 lignes) |
| **Onglets declares** | 5 (TABS array, ligne 181-188) |
| **Composants de sous-tab** | `AnalyseTab`, `FicheTab`, `IntelligenceTab`, `ComparezTab`, `CommandezTab` |

### 1.2 Composants UI Dependants

| Composant | Fichier | Lignes | Role |
|---|---|---|---|
| PinnablePanel | `territoire/PinnablePanel.jsx` | 365 | Conteneur draggable/pinnable |
| ShareBionicButton | `territoire/ui/ShareBionicButton.jsx` | 444 | Partage social BIONIC |
| CriteriaDetailModal | `territoire/ui/CriteriaDetailModal.jsx` | 242 | Modal explicative sous-criteres FICHE |
| PedagogieModule | `territoire/PedagogieModule.jsx` | 384 | GUIDE PRO educatif (tete de hierarchie) |

### 1.3 Onglets — Structure Attendue vs Reelle

| # | Onglet | ID Frontend | Icone | Composant | STATUT |
|---|---|---|---|---|---|
| 1 | ANALYSE | `analyse` | FlaskConical | `AnalyseTab` | PRESENT |
| 2 | FICHE | `fiche` | ClipboardList | `FicheTab` | PRESENT |
| 3 | INTELLIGENCE | `intelligence` | BarChart3 | `IntelligenceTab` | PRESENT |
| 4 | COMPAREZ | `comparez` | Scale | `ComparezTab` | PRESENT |
| 5 | COMMANDEZ | `commandez` | ShoppingCart | `CommandezTab` | PRESENT |
| — | BOUTIQUE | (integre dans COMMANDEZ) | — | Sous-module col. 2+3 | CONFORME |

**Verdict structure: 5/5 onglets presents. BOUTIQUE correctement integre dans COMMANDEZ. CONFORME.**

---

## 2. CARTOGRAPHIE BACKEND — MOTEURS ET ENDPOINTS

### 2.1 Appels API effectues par le Frontend (fetchAll, ligne 219-245)

Le composant SUPRA execute **4 appels paralleles** au montage via `Promise.allSettled`:

| # | Endpoint | Methode | Module Backend | Donnees cibles |
|---|---|---|---|---|
| 1 | `/api/v6/nutrition-intelligence/supra-panel` | POST | `engines/nutrition_intelligence/router.py` | score, recipe, recommendations, products, evidence, costs, substrate_comparison, order, ecozone, energy_protein, terrain_solutions |
| 2 | `/api/v1/saline/analyze` | POST | `modules/saline_engine/router.py` | 7 moteurs ULTRA (engines: soil, metabolism, vegetation, hydrology, nutrients, wildlife, recommendation) |
| 3 | `/api/v1/salines-ultime/fiche` | GET | `modules/salines_ultime_engine/router.py` | 5 scores (logistique, gros_males, strategique, cout_roi, tcs) + 20 sources scientifiques |
| 4 | `/api/v1/soil/analyze` | GET | `modules/soil_engine/router.py` | Classification pedologique (type, metrics, texture, recommendations) |

### 2.2 Appels API supplementaires (Panier/Checkout)

| # | Endpoint | Methode | Module Backend | Declencheur |
|---|---|---|---|---|
| 5 | `/api/v1/saline/shop/cart/{session_id}` | GET | `modules/saline_engine/ecommerce_router.py` | Au montage (fetchCart) |
| 6 | `/api/v1/saline/shop/cart/add` | POST | `modules/saline_engine/ecommerce_router.py` | Boutons CMD / + |
| 7 | `/api/v1/saline/shop/checkout` | POST | `modules/saline_engine/ecommerce_router.py` | Bouton "Payer avec Stripe" |

### 2.3 Registre Complet des Sous-Moteurs Backend

#### Module A: `engines/nutrition_intelligence/` (15 sous-moteurs)

| Code | Fichier | Fonction principale | Onglet(s) cible(s) |
|---|---|---|---|
| x5100 | `x5100_mineral_score.py` | `compute_mineral_score` | ANALYSE |
| x5200 | `x5200_mineral_recommendation.py` | `compute_recommendations` | ANALYSE |
| x5300 | `x5300_order_engine.py` | `generate_order` | COMMANDEZ |
| x5500 | `x5500_energy_protein.py` | `compute_energy_protein` | ANALYSE |
| x5600 | `x5600_site_guide.py` | `generate_site_guide`, `get_ecological_zones` | ANALYSE |
| x5700 | `x5700_cost_engine.py` | `compute_costs`, `compare_substrates` | ANALYSE |
| x5800 | `x5800_recipe_engine.py` | `generate_recipe` | ANALYSE, COMMANDEZ |
| x5900 | `x5900_evidence_engine.py` | `get_evidence`, `get_evidence_for_recipe` | ANALYSE |
| x6000 | `x6000_product_score.py` | `compute_product_score`, `score_all_products`, `compare_products`, `get_shop_products` | INTELLIGENCE, COMPAREZ, COMMANDEZ |
| x6010 | `x6010_product_quality_analyzer.py` | `analyze_product_quality`, `analyze_all_quality` | INTELLIGENCE (enrichissement) |
| x6011 | `x6011_market_availability_engine.py` | `get_product_availability`, `get_all_availability`, `get_provincial_restrictions` | INTELLIGENCE (enrichissement) |
| x6012 | `x6012_regulatory_compliance_engine.py` | `compute_compliance_score`, `compute_all_compliance`, `get_compliance_by_organism` | INTELLIGENCE (enrichissement) |
| x6020 | `x6020_terrain_solutions.py` | `get_solutions_for_deficits`, `get_all_terrain_solutions` | ANALYSE |
| x6030 | `x6030_product_ecosystem.py` | `get_product_ecosystem`, `get_all_ecosystems`, `get_product_tracability` | (Non affiche — donnees disponibles) |
| x7000 | `x7000_supplier_product_engine.py` | `submit_product`, `review_submission`, `activate_product`, `get_submission`, `get_all_submissions`, `get_pipeline_stats` | (Pipeline fournisseur — Admin) |

#### Module B: `modules/saline_engine/` (7 sous-moteurs)

| # | Fichier | Fonction | Onglet cible |
|---|---|---|---|
| 1 | `soil_composition_engine.py` | `analyze_soil` | ANALYSE (via engines.soil) |
| 2 | `nutrient_deficiency_engine.py` | `analyze_deficiencies` | ANALYSE |
| 3 | `wildlife_nutritional_engine.py` | `get_daily_needs` | ANALYSE |
| 4 | `vegetation_forage_engine.py` | `analyze_vegetation` | ANALYSE (engines.vegetation) |
| 5 | `hydrology_leaching_engine.py` | `analyze_hydrology` | ANALYSE (engines.hydrology) |
| 6 | `seasonal_metabolism_engine.py` | `get_metabolic_state` | ANALYSE (engines.metabolism) |
| 7 | `saline_recommendation_engine.py` | `generate_full_analysis` | ANALYSE (orchestrateur maitre) |

#### Module C: `modules/salines_ultime_engine/` (5 scores + 20 sources)

| Score | Poids | Sous-criteres | Sources | Onglet |
|---|---|---|---|---|
| Logistique | 20% | 6 (vehicule, pieton, maintenance, infra, securite, visite) | MFFP, OSM, IRDA | FICHE |
| Gros Males | 25% | 6 (corridors, canopee, eau, observations, tranquillite, pression) | Fortin, Lesmerises, MRNF, Masse | FICHE |
| Strategique | 25% | 6 (position, vent, visibilite, complementarite, saison, expansion) | Dussault, Villemure, Env. Canada | FICHE |
| Cout/ROI | 15% | 6 (mineraux, transport, temps, obs, recolte, durabilite) | SEPAQ, Laurian, Miniere QC | FICHE |
| TCS | 15% | 6 (alignement, lissage, penetrabilite, topo, hydro, effort) | MRNF, OSM, Courtois | FICHE |
| **Total** | **100%** | **30 sous-criteres** | **20 sources** | — |

#### Module D: `modules/soil_engine/` (Classification pedologique)

| Attribut | Valeur |
|---|---|
| Types de sol | 7 (loam_sableux, argile_limoneuse, sable_grossier, tourbe, moraine, roc_affleurant, alluvial) |
| Metriques | retention_mineraux, drainage_naturel, risque_lessivage, capacite_portance, pH, profondeur, matiere_organique, texture |
| Methode | Deterministe (hash MD5 GPS) — V1 NON CERTIFIEE |
| Onglets cibles | ANALYSE (soilData), FICHE (soilData) |

---

## 3. FLUX DE DONNEES — PAR ONGLET

### 3.1 ENTITE SUPRA (Panneau Parent)

```
DECLENCHEUR: Clic utilisateur sur point nutritionnel (carte Leaflet)
                |
                v
   NutritionPointDetailPanel({ nutritionPoint, onClose, selectedSpecies })
                |
                |--- Props entrantes: nutritionPoint { id, lat, lng, score, species, season, soil_type, distance_centre_m }
                |                     selectedSpecies (choix espece utilisateur)
                |
                |--- PRIORITE espece: selectedSpecies > np.species > 'orignal'
                |--- Season: np.season || 'printemps'
                |--- Saison auto-detectee: seasonMap[mois_actuel]
                |
                v
           fetchAll() — 4 appels paralleles
                |
                |--- [1] POST /api/v6/nutrition-intelligence/supra-panel → supraData
                |--- [2] POST /api/v1/saline/analyze → ultraData
                |--- [3] GET  /api/v1/salines-ultime/fiche → ficheData
                |--- [4] GET  /api/v1/soil/analyze → soilData
                |
           fetchCart() — 1 appel
                |--- GET /api/v1/saline/shop/cart/{session_id} → cart
                |
                v
           DISTRIBUTION AUX ONGLETS
```

### 3.2 Onglet ANALYSE — Flux de donnees

```
INPUTS:
  - supraData.score          → Score SUPRA (score_global, grade, zones_resume, score_mineral, scores_par_mineral)
  - supraData.recipe         → Recette (ingredients_cles)
  - supraData.recommendations → Recommandations minerales
  - supraData.evidence       → Sources scientifiques
  - supraData.costs          → Couts (initial, annuel, par visite)
  - supraData.substrate_comparison → Comparaison substrats
  - supraData.ecozone        → Zone ecologique
  - supraData.energy_protein → Besoins energetiques/proteiques
  - supraData.terrain_solutions → Solutions terrain x6020
  - ultraData.engines        → 7 moteurs ULTRA (soil, metabolism, vegetation, hydrology)
  - ultraData.analysis       → intelligence_score, adjusted_deficits
  - soilData                 → Analyse pedologique SOIL ENGINE V1

DONNEES HARDCODEES FRONTEND (NON ISSUES DU BACKEND):
  - PHYSIOLOGY_DATA          → Narration physiologique par espece/saison (2 especes, 6-4 saisons)
  - MALE_BEHAVIOR            → Comportement males par espece/saison (chevreuil uniquement, 6 saisons)
  - SUPPORT_HIERARCHY        → Hierarchie supports (4 types: bois mou, bois dur, sol nu, bloc mineral)

COMPOSANTS AFFICHES (grille 3 colonnes):
  Col.1: Score SUPRA + Gauge ULTRA + Ecozone + Besoins
  Col.2: Sol + Metabolisme + Vegetation/Hydrologie (grille 2x1)
  Col.3: Mineraux (barres) + Recette + Couts
  Bas: PREMIUM (Physiologie, Comportement, Support) + Evidence

SOUS-COMPOSANTS SPECIAUX:
  - GaugeMini (SVG jauge radiale)
  - PedagogieModule (GUIDE PRO — en tete de hierarchie, BCE-4X)
  - GoldenCard, GoldenCollapsible (conteneurs visuels GOLDEN)
```

### 3.3 Onglet FICHE — Flux de donnees

```
INPUTS:
  - ficheData.global_score    → Score global FICHE (score, grade)
  - ficheData.scores          → 5 scores (logistique, gros_males, strategique, cout_roi, tcs)
  - ficheData.scientific_sources → 20 sources scientifiques
  - soilData                  → Analyse pedologique SOIL ENGINE V1
  - species, season, lat, lng → Contexte utilisateur
  - np                        → Point nutritionnel source

COMPOSANTS AFFICHES (grille 3 colonnes):
  Col.1: Score Logistique + Score Gros Males + Guide Logistique
  Col.2: Score Strategique + Score Cout/ROI + Score TCS
  Col.3: Plan Gros Males + Guide ROI + Sol detecte + 20 Sources + Tags integrations

INTERACTIONS:
  - CriteriaRow → clic → ouvre CriteriaDetailModal (fiche explicative sous-critere)
  - Toggle 20 sources (collapse/expand)

ECART: Chaque score affiche ses sous-criteres comme boutons cliquables (CriteriaRow)
       ouverture d'un modal CriteriaDetailModal avec guide professionnel
```

### 3.4 Onglet INTELLIGENCE — Flux de donnees

```
INPUTS:
  - supraData.products.products → Liste de produits scores (score_global, score_species, score_season, score_soil)
  - compareIds (state local)    → IDs des produits selectionnes pour comparaison
  - addToCart (callback)        → Ajout au panier Stripe
  - cartLoading (state)        → Etat chargement panier

COMPOSANTS AFFICHES (grille 3 colonnes):
  Header: Score d'adequation + total produits
  Corps: Produits repartis en 3 colonnes (Math.ceil(n/3))
  Par produit: Score global (42px) + nom + type/prix/poids + tags optimal_for + 3 sous-scores + boutons Comparer/CMD

INTERACTIONS:
  - Bouton "Comparer" → toggleCompare(product_id) → ajoute/retire de compareIds (max 4)
  - Bouton "CMD" → addToCart(product_id) → POST /api/v1/saline/shop/cart/add

INTERCONNEXION:
  - compareIds transmis a l'onglet COMPAREZ via state parent
  - addToCart partage avec COMMANDEZ via state parent
```

### 3.5 Onglet COMPAREZ — Flux de donnees

```
INPUTS:
  - supraData.products.products → Tous les produits (filtres par compareIds)
  - compareIds (state parent)   → IDs selectionnes dans INTELLIGENCE

COMPOSANTS AFFICHES (grille 3 colonnes):
  Header: Nombre de produits selectionnes
  Corps: 1 colonne par produit (max 3 affiches, padded a 3)
  Par produit: Score global (56px) + nom + type + 5 metriques + mini-bars 3 scores + bouton retirer

LOGIQUE SPECIALE:
  - best = produit avec score_global le plus eleve → badge "MEILLEUR CHOIX"
  - Si 0 produit selectionne: message "Aucun produit selectionne — Allez dans INTELLIGENCE"

INTERCONNEXION:
  - Lecture seule de compareIds (pas de modification directe, sauf retirer)
  - Retour vers INTELLIGENCE pour selection
```

### 3.6 Onglet COMMANDEZ (+ BOUTIQUE) — Flux de donnees

```
INPUTS:
  - supraData.order           → Recette complete (items, summary.cost_initial_cad)
  - supraData.products        → Produits individuels (pour sous-module BOUTIQUE)
  - supraData.recipe          → Recette (non directement affichee, transmise en prop)
  - cart (state parent)       → Panier Stripe reel { items, item_count, total }
  - addToCart (callback)      → Ajout au panier
  - handleCheckout (callback) → Checkout Stripe
  - fetchCart (callback)      → Rafraichissement panier

COMPOSANTS AFFICHES (grille 3 colonnes):
  Col.1: RECETTE COMPLETE — items de commande avec prix + bouton +
  Col.2: PRODUITS INDIVIDUELS (BOUTIQUE) — 6 premiers produits avec score + bouton panier
  Col.3: PANIER STRIPE — articles, quantites, total + bouton "Payer avec Stripe"

SESSION PANIER:
  - ID session: localStorage 'saline_session_id' (genere client-side: 'sal_' + random)
  - Pas de validation session cote serveur (ecart potentiel)
  - Cart badge affiche dans la barre d'onglets (cartCount)

FLUX CHECKOUT:
  - POST /api/v1/saline/shop/checkout → retourne URL Stripe → redirection navigateur
  - origin_url: window.location.origin (pour retour post-paiement)
```

---

## 4. MATRICE D'INTERCONNEXIONS

### 4.1 Interconnexions Internes (entre onglets)

| Source | Cible | Donnee partagee | Mecanisme |
|---|---|---|---|
| INTELLIGENCE | COMPAREZ | `compareIds` | State parent (`useState`) |
| INTELLIGENCE | COMMANDEZ | `addToCart` callback | Props depuis parent |
| COMMANDEZ | Barre onglets | `cartCount` | Badge visuel dynamique |
| ANALYSE | (tous) | `score.grade` → `gc` (couleur) | Couleur accent propagee |
| Parent | ANALYSE, FICHE | `soilData` | State parent partage |
| Parent | ANALYSE | `ultraData.engines` | State parent partage |

### 4.2 Interconnexions Externes (vers autres systemes)

| Module SUPRA | Systeme externe | Direction | Donnee |
|---|---|---|---|
| ANALYSE | PedagogieModule (GUIDE PRO) | Sortante | species, season, score, gc |
| SUPRA (barre) | ShareBionicButton | Sortante | (contexte implicite) |
| FICHE | CriteriaDetailModal | Sortante | criteriaKey, criteriaValue, species, season |
| COMMANDEZ | Stripe Checkout | Sortante | session_id, origin_url |
| Parent | Carte Leaflet | Entrante | nutritionPoint (clic sur marqueur) |
| Backend supra-panel | x6010, x6011, x6012 | Interne backend | Enrichissement produits |
| Backend supra-panel | x6020 | Interne backend | Solutions terrain |

### 4.3 Matrice Backend — Dependances entre modules

```
nutrition_intelligence (x5100-x7000)
    |
    |--- NE DEPEND D'AUCUN AUTRE MODULE (autonome)
    |--- Appele directement par le frontend (supra-panel)
    
saline_engine (7 moteurs)
    |
    |--- Depend de: alimentation_v2/terrain (terrain data)
    |--- Depend de: solunar/engine (donnees solunar)
    |--- Depend de: weather_engine (meteo, optionnel)
    |--- Appele directement par le frontend (analyze)
    
salines_ultime_engine (5 scores)
    |
    |--- NE DEPEND D'AUCUN AUTRE MODULE (autonome, deterministe)
    |--- Appele directement par le frontend (fiche)
    
soil_engine (V1)
    |
    |--- NE DEPEND D'AUCUN AUTRE MODULE (autonome, deterministe)
    |--- Appele directement par le frontend (soil/analyze)
    
ecommerce_router (cart/checkout)
    |
    |--- Depend de: Stripe API (STRIPE_API_KEY)
    |--- Depend de: MongoDB (sessions panier)
    |--- Appele directement par le frontend (cart/add, cart/get, checkout)
```

---

## 5. ECARTS, DEVIATIONS ET INCOHERENCES

### 5.1 Ecarts BCE-4X Identifies

| # | Severite | Localisation | Description | Norme BCE-4X violee |
|---|---|---|---|---|
| E01 | MAJEUR | `NutritionPointDetailPanel.jsx` L407, L714, L820, L1030, L1135 | **Composant `IC` duplique 5 fois** — definition identique du helper icon-circle dans chaque tab-component | DRY / NoCodeDuplication |
| E02 | MODERE | `NutritionPointDetailPanel.jsx` L83-116 | **Donnees PHYSIOLOGY_DATA, MALE_BEHAVIOR, SUPPORT_HIERARCHY hardcodees en frontend** — non issues d'un endpoint backend. Modification necessite redeploiement frontend | Separation donnees/presentation |
| E03 | MINEUR | `NutritionPointDetailPanel.jsx` L49-56 | **Session panier localStorage** — `saline_session_id` genere cote client sans validation serveur. Risque de desynchronisation sessions | Securite session |
| E04 | INFO | `NutritionPointDetailPanel.jsx` L166-167 | **Alias backward-compat** — `Card = GoldenCard` et `CollapsibleSection = GoldenCollapsible` declares mais `Card` et `CollapsibleSection` ne sont jamais utilises | Code mort potentiel |
| E05 | MAJEUR | `soil_engine/router.py` L1-33 | **SOIL ENGINE V1 deterministe** — Classification pedologique basee sur hash MD5. Correctement documente comme NON CERTIFIE. Score simule, PAS mesure | Certitude donnees BCE-4X |
| E06 | MODERE | `NutritionPointDetailPanel.jsx` L509, L966 | **Double source sol** — ANALYSE utilise `engines.soil` (saline_engine) ET `soilData` (soil_engine) pour le meme panneau Sol. Deux systemes de scoring differents pour la meme metrique | Coherence sources |
| E07 | MINEUR | `NutritionPointDetailPanel.jsx` L214 | **Mapping saison auto** — `seasonMap` mappe les mois aux saisons mais le frontend transmet AUSSI `np.season` (statique). Conflit potentiel entre saison auto-detectee et saison du point | Determinisme saisonnier |
| E08 | MODERE | `nutrition_intelligence/router.py` L244-265 | **Boucle enrichissement N+1** — Le supra-panel itere sur chaque produit pour appeler x6010, x6011, x6012 individuellement (3 appels par produit). Performance degrade avec N produits | Performance BCE-4X |
| E09 | MINEUR | INTELLIGENCE tab, L709 | **Division colonnes non equilibree** — `Math.ceil(n/3)` peut produire des colonnes inegales (ex: 7 produits = 3+3+1) | Equilibre visuel GOLDEN |
| E10 | MODERE | COMPAREZ tab, L1057-1058 | **Limite affichage 3 colonnes** — `padded.slice(0, 3)` ignore le 4eme produit si `compareIds.length === 4`. L'utilisateur peut selectionner 4 produits mais seuls 3 sont affiches | Coherence UX |
| E11 | MINEUR | `salines_ultime_engine/router.py` | **Scoring deterministe FICHE** — Les 5 scores utilisent un hash MD5 pour reproductibilite mais ne sont PAS bases sur des donnees reelles | Meme problematique que E05 |
| E12 | INFO | `NutritionPointDetailPanel.jsx` L1259 | **Fichier monolithique 1259 lignes** — Tous les composants de tab dans un seul fichier. Depasse la norme BCE-4X de modularite (max 300 lignes/composant recommande) | Modularite |
| E13 | MINEUR | COMMANDEZ tab, L1163 | **product_id fallback** — `item.product_id \|\| 'sal_00${i+1}'` genere un ID artificiel si product_id manquant. Risque d'ajout produit inexistant au panier | Integrite donnees |
| E14 | INFO | `x6030_product_ecosystem.py`, `x7000_supplier_product_engine.py` | **Moteurs non affiches** — x6030 (ecosysteme produit) et x7000 (pipeline fournisseur) ont des endpoints mais aucun onglet ne les affiche | Potentiel non exploite |

### 5.2 Synthese par severite

| Severite | Nombre | IDs |
|---|---|---|
| MAJEUR | 2 | E01, E05 |
| MODERE | 4 | E02, E06, E08, E10 |
| MINEUR | 5 | E03, E07, E09, E11, E13 |
| INFO | 3 | E04, E12, E14 |
| **TOTAL** | **14** | — |

---

## 6. VERIFICATION DES NORMES BCE-4X-GLOBAL-PLUS-TOTAL

### 6.1 Standard GOLDEN Visual

| Norme | Statut | Detail |
|---|---|---|
| Zero bordure visible | CONFORME | Toutes les GoldenCard utilisent uniquement accent bar gauche |
| Accent bar gauche | CONFORME | `borderLeft: 3px solid ${accentColor}` |
| Icones en cercles | CONFORME | Helper IC (rond + couleur/20) |
| Valeurs 30-40px | CONFORME | `text-[30px] font-black` pour scores principaux |
| Labels 14px | CONFORME | `text-[14px]` pour labels |
| Corps 16px | CONFORME | `text-[16px]` pour valeurs |
| Coins rounded-xl | CONFORME | `rounded-lg` (12px) sur GoldenCard |
| Fond #0F172A / carte #1E293B | CONFORME | GOLDEN.pageBg / GOLDEN.cardBg |
| Structure 100% VERTICALE | CONFORME | `space-y-1.5` partout |
| Grille 3 colonnes | CONFORME | `grid grid-cols-3 gap-1.5` dans tous les onglets |

### 6.2 Standard data-testid

| Composant | data-testid | Statut |
|---|---|---|
| Panel content | `supra-v2-panel-content` | PRESENT |
| Barre onglets | `supra-tabs` | PRESENT |
| Chaque onglet | `supra-tab-{id}` | PRESENT |
| Zone contenu | `supra-v2-content-area` | PRESENT |
| Loading | `supra-loading` | PRESENT |
| No data | `supra-no-data` | PRESENT |
| Retry | `supra-retry-btn` | PRESENT |
| Gauge | `supra-gauge` | PRESENT |
| Score SUPRA | `supra-score-card` | PRESENT |
| Footer | `supra-footer` | PRESENT |
| Grille 3 col | `supra-3col-grid` | PRESENT |
| Mineraux | `supra-mineral-{key}` | PRESENT |
| Checkout | `supra-checkout-btn` | PRESENT |

**Verdict testids: CONFORME — couverture exhaustive**

### 6.3 Standard BCE-4X Lock

| Attribut | Statut |
|---|---|
| `data-bce4x-locked="true"` sur SupraButton | PRESENT (ligne 175) |
| STEEVE-MAX mention dans footer | PRESENT |
| Score source tracking (SUPRA_UNIFIED / x5100_mineral) | PRESENT |

---

## 7. RECOMMANDATIONS DE RECONSTRUCTION x1000%

### R01 — EXTRACTION COMPOSANT IC (Priorite: HAUTE)
**Ecart:** E01
**Action:** Extraire le composant `IC` dans un fichier partage `territoire/ui/IconCircle.jsx` et l'importer dans les 5 composants de tab. Elimine 5 definitions identiques.
**Impact:** ~40 lignes supprimees, coherence garantie.

### R02 — EXTERNALISATION DONNEES PREMIUM (Priorite: MOYENNE)
**Ecart:** E02
**Action:** Creer un endpoint backend `/api/v6/nutrition-intelligence/premium-data` retournant PHYSIOLOGY_DATA, MALE_BEHAVIOR, SUPPORT_HIERARCHY. Le frontend consomme au lieu de hardcoder.
**Impact:** Separation donnees/UI, mise a jour sans redeploiement frontend.

### R03 — CORRECTION AFFICHAGE COMPAREZ (Priorite: HAUTE)
**Ecart:** E10
**Action:** Si `compareIds.length === 4`, afficher une grille `grid-cols-4` ou un layout 2x2. Actuellement le 4eme produit est silencieusement ignore.
**Impact:** Coherence UX — l'utilisateur voit bien les 4 produits selectionnes.

### R04 — OPTIMISATION BOUCLE ENRICHISSEMENT (Priorite: MOYENNE)
**Ecart:** E08
**Action:** Creer des fonctions batch dans x6010, x6011, x6012 pour traiter tous les produits en un seul appel au lieu de N appels individuels.
**Impact:** Performance backend amelioree (de O(3N) a O(3)).

### R05 — NETTOYAGE CODE MORT (Priorite: BASSE)
**Ecart:** E04
**Action:** Supprimer les alias `Card = GoldenCard` et `CollapsibleSection = GoldenCollapsible` (lignes 166-167) s'ils ne sont utilises nulle part.
**Impact:** Clarte du code.

### R06 — MODULARISATION FICHIER PRINCIPAL (Priorite: MOYENNE)
**Ecart:** E12
**Action:** Extraire chaque composant de tab dans son propre fichier:
- `territoire/supra/AnalyseTab.jsx`
- `territoire/supra/FicheTab.jsx`
- `territoire/supra/IntelligenceTab.jsx`
- `territoire/supra/ComparezTab.jsx`
- `territoire/supra/CommandezTab.jsx`
**Impact:** Fichier principal reduit de 1259 a ~400 lignes. Maintenabilite x1000%.

---

## 8. SYNTHESE DES COMPTEURS

| Metrique | Valeur |
|---|---|
| **Entites auditees** | 6 (SUPRA + 5 onglets) |
| **Fichiers frontend analyses** | 5 (Panel + 4 sous-composants) |
| **Fichiers backend analyses** | 20+ (4 modules, 15+ sous-moteurs) |
| **Endpoints cartographies** | 7 (frontend) + 30+ (backend total) |
| **Sous-moteurs catalogues** | 29 (15 nutrition + 7 saline + 5 ultime + 1 soil + 1 ecommerce) |
| **Sous-criteres FICHE** | 30 (6 par score x 5 scores) |
| **Sources scientifiques** | 20 (FICHE) + variable (ANALYSE evidence) |
| **Ecarts identifies** | 14 (2 majeurs, 4 moderes, 5 mineurs, 3 info) |
| **Recommandations** | 6 |
| **Conformite GOLDEN visuel** | 10/10 PASS |
| **Conformite data-testid** | PASS |
| **Conformite BCE-4X lock** | PASS |

---

## 9. VERDICT INSTITUTIONNEL

L'ecosysteme SUPRA v2 est **FONCTIONNEL et STRUCTURELLEMENT CONFORME** aux normes
visuelles BCE-4X GOLDEN V6+. Les 5 onglets sont presents, interconnectes et
alimentes par 29 sous-moteurs backend.

**14 ecarts ont ete identifies**, dont 2 majeurs:
1. **E01** — Duplication x5 du composant IC (violation DRY)
2. **E05** — SOIL ENGINE V1 deterministe non certifie (connu, documente)

**6 recommandations de reconstruction** sont proposees, ordonnees par priorite.

Aucune regression active n'a ete detectee.

**STATUT: EN ATTENTE DE VALIDATION COMMANDANT STEEVE-MAX**

---

*Rapport genere conformement au protocole BCE-4X-GLOBAL-PLUS-TOTAL*
*Autorite: COMMANDANT STEEVE-MAX*
*Branche: BIONIC_REWRITE_P0*
*Date: 2026-02-07*

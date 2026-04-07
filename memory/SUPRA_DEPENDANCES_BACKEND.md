# SUPRA_DEPENDANCES_BACKEND.md
# ============================================================
# COMPLEMENT (B) — MATRICE DE DEPENDANCES BACKEND COMPLETE
# ============================================================
# Protocole: BCE-4X-GLOBAL-PLUS-TOTAL
# Autorite: COMMANDANT STEEVE-MAX
# Branche: BIONIC_REWRITE_P0
# Date: 2026-02-07
# Statut: LIVRABLE COMPLEMENTAIRE — EN ATTENTE DE VALIDATION
# ============================================================

---

## 1. REGISTRE DES 29 MOTEURS — VERSIONS, SIGNATURES, DEPENDANCES

### 1.1 Module A: `engines/nutrition_intelligence/` (15 moteurs)

| # | Code | Fichier | Lignes | Fonctions | SHA256 (16 car.) | Dependances internes | Dependances externes |
|---|---|---|---|---|---|---|---|
| 1 | x5100 | `x5100_mineral_score.py` | 142 | 1 | `612120c19bf068b0` | Aucune | Aucune |
| 2 | x5200 | `x5200_mineral_recommendation.py` | 111 | 1 | `61acbd99f2fff019` | Aucune | Aucune |
| 3 | x5300 | `x5300_order_engine.py` | 60 | 1 | `a3342f2e149abab3` | Aucune | Aucune |
| 4 | x5500 | `x5500_energy_protein.py` | 331 | 1 | `a1aa53f156bdaf9b` | Aucune | Aucune |
| 5 | x5600 | `x5600_site_guide.py` | 161 | 2 | `85e93f9bcd60568e` | Aucune | Aucune |
| 6 | x5700 | `x5700_cost_engine.py` | 73 | 2 | `62e1dc0008af9719` | **x5500** (compute_energy_protein), **x5600** (SUBSTRATE_OPTIONS) | Aucune |
| 7 | x5800 | `x5800_recipe_engine.py` | 83 | 1 | `1d1593ad02541aec` | **x5500** (compute_energy_protein), **x5600** (generate_site_guide) | Aucune |
| 8 | x5900 | `x5900_evidence_engine.py` | 276 | 3 | `7759654fb7669203` | Aucune | Aucune |
| 9 | x6000 | `x6000_product_score.py` | 240 | 4 | `07bfea2885850076` | Aucune | Aucune |
| 10 | x6010 | `x6010_product_quality_analyzer.py` | 173 | 2 | `7ad548cf41c319d9` | Aucune | Aucune |
| 11 | x6011 | `x6011_market_availability_engine.py` | 280 | 3 | `544433ede26ba8a0` | Aucune | Aucune |
| 12 | x6012 | `x6012_regulatory_compliance_engine.py` | 208 | 3 | `e07d6a282633551e` | Aucune | Aucune |
| 13 | x6020 | `x6020_terrain_solutions.py` | 346 | 2 | `966c41a5c0b3cdd9` | Aucune | Aucune |
| 14 | x6030 | `x6030_product_ecosystem.py` | 292 | 3 | `3e633d24b3a265be` | Aucune | Aucune |
| 15 | x7000 | `x7000_supplier_product_engine.py` | 299 | 11 | `515002deb9cfa2b7` | Aucune | Aucune |

**Total Module A:** 3075 lignes | 40 fonctions | 15 fichiers

### 1.2 Module B: `modules/saline_engine/` (7 moteurs + 1 router + 1 ecommerce)

| # | Moteur | Fichier | Lignes | Fonctions | SHA256 (16 car.) | Dependances internes | Dependances externes |
|---|---|---|---|---|---|---|---|
| 16 | Soil Composition | `soil_composition_engine.py` | 90 | 3 | `8da72916ef584cdb` | Aucune | Aucune |
| 17 | Nutrient Deficiency | `nutrient_deficiency_engine.py` | 139 | 2 | `3202051c1437f4e6` | Aucune | Aucune |
| 18 | Wildlife Nutritional | `wildlife_nutritional_engine.py` | 117 | 1 | `54959871431a867d` | Aucune | Aucune |
| 19 | Vegetation Forage | `vegetation_forage_engine.py` | 132 | 2 | `7ddb194bcebd1b3a` | Aucune | Aucune |
| 20 | Hydrology Leaching | `hydrology_leaching_engine.py` | 171 | 4 | `6985600d926692f1` | Aucune | Aucune |
| 21 | Seasonal Metabolism | `seasonal_metabolism_engine.py` | 213 | 4 | `b08ea7f2e71e9cfc` | Aucune | Aucune |
| 22 | Saline Recommendation (maitre) | `saline_recommendation_engine.py` | 411 | 6 | `a5bc02f53fa25612` | **#17** (analyze_deficiencies), **#18** (get_daily_needs), **#19** (analyze_vegetation), **#20** (analyze_hydrology), **#21** (get_metabolic_state) | Aucune |
| 23 | Router saline | `router.py` | 318 | 13 | N/A | #16-#22 (tous) | `alimentation_v2/terrain`, `solunar/engine` |
| 24 | E-Commerce | `ecommerce_router.py` | 419 | 7 | `4f6c2507c8c269fd` | Aucune | **Stripe API**, **MongoDB** |

**Total Module B:** 2010 lignes | 42 fonctions | 9 fichiers

### 1.3 Module C: `modules/salines_ultime_engine/` (1 moteur)

| # | Moteur | Fichier | Lignes | Fonctions | SHA256 (16 car.) | Dependances internes | Dependances externes |
|---|---|---|---|---|---|---|---|
| 25 | Salines Ultime | `router.py` | 300 | 11 | `9be51d1765b0281b` | Aucune (autonome) | Aucune |

### 1.4 Module D: `modules/soil_engine/` (1 moteur)

| # | Moteur | Fichier | Lignes | Fonctions | SHA256 (16 car.) | Dependances internes | Dependances externes |
|---|---|---|---|---|---|---|---|
| 26 | Soil Engine V1 | `router.py` | 329 | 7 | `ea01e974adc2f7d0` | Aucune (autonome) | Aucune |

### 1.5 Orchestrateur: `engines/nutrition_intelligence/router.py`

| # | Moteur | Fichier | Lignes | Fonctions | Dependances |
|---|---|---|---|---|---|
| 27 | Router NI | `router.py` | 461 | 25 | **Tous les 15 moteurs** du Module A via `__init__.py` |

### 1.6 Package: `engines/nutrition_intelligence/__init__.py`

| # | Moteur | Fichier | Lignes | Exports |
|---|---|---|---|---|
| 28 | Package Init | `__init__.py` | 17 | 30 fonctions exportees depuis 15 sous-modules |

### 1.7 Frontend: `NutritionPointDetailPanel.jsx`

| # | Composant | Fichier | Lignes | Dependances backend |
|---|---|---|---|---|
| 29 | SUPRA v2 Panel | `NutritionPointDetailPanel.jsx` | 1259 | Modules A, B, C, D (endpoints #1-#7) |

---

## 2. GRAPHE DE DEPENDANCES COMPLET

### 2.1 Dependances internes — Module A (nutrition_intelligence)

```
x5100 ←─────────────────────── AUTONOME (feuille)
x5200 ←─────────────────────── AUTONOME (feuille)
x5300 ←─────────────────────── AUTONOME (feuille)
x5500 ←──── x5700, x5800 ──── NOEUD CENTRAL (2 dependants)
x5600 ←──── x5700, x5800 ──── NOEUD CENTRAL (2 dependants)
x5700 ←─────────────────────── DEPENDANT (x5500, x5600)
x5800 ←─────────────────────── DEPENDANT (x5500, x5600)
x5900 ←─────────────────────── AUTONOME (feuille)
x6000 ←─────────────────────── AUTONOME (feuille)
x6010 ←─────────────────────── AUTONOME (feuille)
x6011 ←─────────────────────── AUTONOME (feuille)
x6012 ←─────────────────────── AUTONOME (feuille)
x6020 ←─────────────────────── AUTONOME (feuille)
x6030 ←─────────────────────── AUTONOME (feuille)
x7000 ←─────────────────────── AUTONOME (feuille)

Profondeur maximale: 2 niveaux (x5700/x5800 → x5500/x5600)
Moteurs autonomes (feuilles): 13/15 (86.7%)
Noeuds centraux: 2 (x5500, x5600)
```

### 2.2 Dependances internes — Module B (saline_engine)

```
#16 soil_composition     ←── AUTONOME (feuille)
#17 nutrient_deficiency  ←── #22 saline_recommendation ── NOEUD (1 dependant)
#18 wildlife_nutritional ←── #22 saline_recommendation ── NOEUD (1 dependant)
#19 vegetation_forage    ←── #22 saline_recommendation ── NOEUD (1 dependant)
#20 hydrology_leaching   ←── #22 saline_recommendation ── NOEUD (1 dependant)
#21 seasonal_metabolism  ←── #22 saline_recommendation ── NOEUD (1 dependant)
#22 saline_recommendation ←─ ORCHESTRATEUR (5 dependances)
#23 router               ←── #16-#22 (tous)
#24 ecommerce            ←── AUTONOME (Stripe + MongoDB)

Profondeur maximale: 2 niveaux (#23 → #22 → #17-#21)
```

### 2.3 Dependances inter-modules

```
Module A (nutrition_intelligence) ══╗
                                     ║
Module B (saline_engine)       ══════╬═══> Frontend (SUPRA v2)
                                     ║
Module C (salines_ultime)      ══════╣
                                     ║
Module D (soil_engine)         ══════╝

AUCUNE DEPENDANCE DIRECTE ENTRE MODULES A, B, C, D
Chaque module est appele independamment par le frontend.
```

### 2.4 Dependances externes

| Module | Dependance externe | Type | Criticite |
|---|---|---|---|
| B (#23 router) | `alimentation_v2/terrain` | Backend interne | MOYENNE — Fallback si indisponible |
| B (#23 router) | `solunar/engine` | Backend interne | FAIBLE — Enrichissement optionnel |
| B (#24 ecommerce) | **Stripe API** | Service externe | HAUTE — Checkout bloque si indisponible |
| B (#24 ecommerce) | **MongoDB** | Base de donnees | HAUTE — Panier non persistant si down |
| Frontend | `localStorage` | Navigateur | FAIBLE — Session panier locale |

---

## 3. POINTS DE FRAGILITE IDENTIFIES

### 3.1 Fragilites structurelles

| ID | Module | Composant | Type de fragilite | Severite | Description |
|---|---|---|---|---|---|
| F01 | A | x5500 (energy_protein) | **Noeud central** | HAUTE | 2 moteurs (x5700, x5800) dependent directement de x5500. Toute modification de la signature ou du format de retour de `compute_energy_protein` casse x5700 et x5800. |
| F02 | A | x5600 (site_guide) | **Noeud central** | HAUTE | 2 moteurs (x5700, x5800) dependent de x5600. Modification de `SUBSTRATE_OPTIONS` ou `generate_site_guide` propage des erreurs. |
| F03 | A | router.py (supra-panel) | **Point de convergence** | CRITIQUE | L'endpoint `/supra-panel` orchestre 11 fonctions en sequence + boucle N+1 enrichissement. C'est le SPOF (Single Point of Failure) du SUPRA. Tout echec dans un moteur peut compromettre la reponse complete. |
| F04 | B | #22 saline_recommendation | **Orchestrateur** | HAUTE | Depend de 5 sous-moteurs (#17-#21). Echec d'un seul sous-moteur = echec de l'analyse complete. Pas de fallback granulaire. |
| F05 | B | #24 ecommerce | **Dependance externe** | HAUTE | Depend de Stripe API et MongoDB. Coupure reseau = checkout impossible. Session panier perdue si MongoDB down. |
| F06 | Frontend | NutritionPointDetailPanel | **Monolithe** | MODERE | 1259 lignes, 6 composants, 5 appels API. Toute erreur de syntaxe dans n'importe quel onglet casse le panneau entier. |
| F07 | A | __init__.py | **Point d'entree unique** | MODERE | Exporte 30 fonctions depuis 15 fichiers. Tout import defaillant (fichier manquant, fonction renommee) empeche le chargement du module entier. |

### 3.2 Fragilites de donnees

| ID | Module | Description | Severite |
|---|---|---|---|
| F08 | C, D | Scoring deterministe (hash MD5). Scores non reels. Fragile si les utilisateurs prennent des decisions basees sur ces donnees. | MODERE |
| F09 | A (x6000) | Catalogue produits hardcode dans le code Python. Ajout/modification de produit necessite un redeploiement backend. | MODERE |
| F10 | Frontend | Donnees PREMIUM (physiologie, comportement, support) hardcodees en JSX. Pas de mise a jour sans redeploiement frontend. | MODERE |

### 3.3 Fragilites de performance

| ID | Module | Description | Severite |
|---|---|---|---|
| F11 | A (router) | Boucle enrichissement N+1 dans supra-panel (3 appels x N produits). Lineaire avec le nombre de produits. | MODERE |
| F12 | Frontend | 4 appels API paralleles au montage. Si un appel est lent, `Promise.allSettled` attend quand meme. | FAIBLE |

---

## 4. RISQUES DE PROPAGATION

### 4.1 Matrice de propagation — "Si le moteur X est modifie, quels moteurs sont impactes?"

| Moteur modifie | Moteurs impactes directement | Moteurs impactes indirectement | Niveau de propagation |
|---|---|---|---|
| **x5500** (energy_protein) | x5700, x5800 | router.py (supra-panel) | **3 niveaux** |
| **x5600** (site_guide) | x5700, x5800 | router.py (supra-panel) | **3 niveaux** |
| **x5100** (mineral_score) | router.py | Frontend (score SUPRA) | **2 niveaux** |
| **x6000** (product_score) | router.py | Frontend (INTELLIGENCE, COMPAREZ, COMMANDEZ) | **2 niveaux** |
| **#22** (saline_recommendation) | #23 router | Frontend (ultraData) | **2 niveaux** |
| **#17-#21** (5 sous-moteurs) | #22 | #23 router → Frontend | **3 niveaux** |
| **x5700** | Aucun (feuille terminale) | — | **0** |
| **x5800** | Aucun (feuille terminale) | — | **0** |
| **x5900** | Aucun (feuille terminale) | — | **0** |
| **x6010-x6012** | Aucun | — | **0** |
| **x6020-x6030** | Aucun | — | **0** |
| **x7000** | Aucun | — | **0** |
| **Module C** (salines_ultime) | Aucun (autonome) | — | **0** |
| **Module D** (soil_engine) | Aucun (autonome) | — | **0** |
| **#24** (ecommerce) | Aucun (autonome) | — | **0** |

### 4.2 Classification des moteurs par risque de propagation

| Niveau de risque | Moteurs | Raison |
|---|---|---|
| **CRITIQUE** | router.py (supra-panel) | Orchestre 11+ fonctions, alimente tous les onglets |
| **HAUT** | x5500, x5600, #22 | Noeuds centraux avec 2+ dependants |
| **MOYEN** | x5100, x6000, #23 | Impactent le frontend directement |
| **FAIBLE** | x5200, x5300, x5700, x5800, x5900, x6010-x6012, x6020-x6030, x7000, #16-#21, #24, Module C, Module D | Feuilles terminales ou modules autonomes |

### 4.3 Zones de confinement

Si un moteur echoue, quel est le rayon d'explosion?

```
Zone 1 (CONFINEE — 0 propagation):
  x5200, x5300, x5700, x5800, x5900, x6010, x6011, x6012,
  x6020, x6030, x7000, #16, #24, Module C, Module D
  → 15 moteurs (51.7%) — SECURISES

Zone 2 (PROPAGATION LIMITEE — 1 niveau):
  x5100, x6000, #17, #18, #19, #20, #21
  → 7 moteurs (24.1%) — SURVEILLANCES

Zone 3 (PROPAGATION ETENDUE — 2+ niveaux):
  x5500, x5600, #22, router.py (supra-panel)
  → 4 composants (13.8%) — CRITIQUES
```

---

## 5. SIGNATURES DES FONCTIONS CRITIQUES

### 5.1 Fonctions a propagation CRITIQUE

```python
# x5500 — NOEUD CENTRAL
def compute_energy_protein(species: str, season: str) -> dict
# Retourne: { species, season, phase, energy_need, protein_need,
#              energy_blocks, protein_blocks, seasonal_mix }

# x5600 — NOEUD CENTRAL
def generate_site_guide(species: str, season: str, soil_type: str) -> dict
def get_ecological_zones(species: str = None) -> dict
SUBSTRATE_OPTIONS = dict  # Constante importee par x5700

# #22 saline_recommendation — ORCHESTRATEUR
def generate_full_analysis(
    lat: float, lng: float, species: str, sex: str, age: str,
    month: int, season: str, terrain: dict = None,
    solunar_data: dict = None, weather_data: dict = None
) -> dict

# router.py supra-panel — POINT DE CONVERGENCE
async def supra_panel(req: RecipeRequest) -> dict
# RecipeRequest: { species, season, soil_type, substrate, site_minerals, lat, lng, saline_score }
# Retourne: { score, recommendations, energy_protein, recipe, evidence,
#              costs, substrate_comparison, products, order, ecozone, terrain_solutions }
```

---

*Rapport genere conformement au protocole BCE-4X-GLOBAL-PLUS-TOTAL*
*Autorite: COMMANDANT STEEVE-MAX*
*Branche: BIONIC_REWRITE_P0*
*Date: 2026-02-07*

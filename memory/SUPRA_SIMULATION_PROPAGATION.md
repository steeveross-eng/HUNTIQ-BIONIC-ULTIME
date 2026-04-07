# SUPRA_SIMULATION_PROPAGATION.md
# ============================================================
# COMPLEMENT (C) — SIMULATION DE PROPAGATION
# ============================================================
# Protocole: BCE-4X-GLOBAL-PLUS-TOTAL | Pression x2
# Autorite: COMMANDANT STEEVE-MAX
# Branche: BIONIC_REWRITE_P0
# Date: 2026-02-07
# Statut: LIVRABLE — EN ATTENTE DE VALIDATION
# ============================================================

---

## 1. METHODE DE SIMULATION

Pour chaque fragilite F01-F12, un scenario complet est simule:
1. **Declencheur** — L'evenement qui active la fragilite
2. **Propagation** — Le chemin de cascade a travers SUPRA → ANALYSE → FICHE → INTELLIGENCE → COMPAREZ → COMMANDEZ
3. **Points de rupture** — Les composants qui cessent de fonctionner
4. **Rayon d'explosion** — L'ensemble des onglets impactes
5. **Mesures de confinement** — Les barrieres qui limitent ou stoppent la propagation

---

## 2. SCENARIOS DE PROPAGATION

### SCENARIO F01 — Noeud central x5500 (energy_protein) modifie

**Fragilite:** F01 — x5500 est un noeud central avec 2 dependants (x5700, x5800)

**Declencheur:** Un developpeur renomme le champ `energy_need` en `energy_kj` dans le retour de `compute_energy_protein()`.

```
PROPAGATION:
x5500 (energy_protein)
  |
  ├──> x5700 (cost_engine) appelle compute_energy_protein()
  |      |── x5700 lit result['energy_need'] → KeyError
  |      |── compute_costs() echoue → exception non geree
  |      └── supra-panel recoit costs=None
  |
  ├──> x5800 (recipe_engine) appelle compute_energy_protein()
  |      |── x5800 lit result['energy_need'] → KeyError
  |      |── generate_recipe() echoue → exception non geree
  |      └── supra-panel recoit recipe=None
  |
  └──> router.py (supra-panel)
         |── costs=None, recipe=None
         |── Reponse JSON avec costs=null, recipe=null
         └── Frontend recoit supraData avec champs manquants
```

**Points de rupture:**

| # | Composant | Type | Effet |
|---|---|---|---|
| 1 | x5700.compute_costs() | Backend exception | costs = null dans la reponse |
| 2 | x5800.generate_recipe() | Backend exception | recipe = null dans la reponse |
| 3 | AnalyseTab — section Couts | Frontend render fail | Section Couts vide/absente |
| 4 | AnalyseTab — section Recette | Frontend render fail | Section Recette vide/absente |
| 5 | CommandezTab — col.1 Recette | Frontend render fail | Colonne Recette vide |

**Rayon d'explosion:**

| Onglet | Impact | Severite |
|---|---|---|
| SUPRA parent | supraData partiellement vide | MODERE |
| ANALYSE | Sections Couts + Recette disparaissent | HAUTE |
| FICHE | Aucun impact (n'utilise pas costs/recipe) | AUCUN |
| INTELLIGENCE | Aucun impact (utilise products, pas costs/recipe) | AUCUN |
| COMPAREZ | Aucun impact | AUCUN |
| COMMANDEZ | Col.1 Recette vide, col.2-3 fonctionnelles | MODERE |

**Mesures de confinement:**
1. **Try/except** dans router.py autour de chaque appel moteur (existe partiellement)
2. **Valeurs par defaut** dans le frontend: `supraData?.costs?.initial_cost_cad || 'N/A'`
3. **Contract test** sur la signature de `compute_energy_protein` (A IMPLEMENTER)
4. **Impact confine** aux onglets ANALYSE et COMMANDEZ — FICHE, INTELLIGENCE, COMPAREZ non touches

---

### SCENARIO F02 — Noeud central x5600 (site_guide) modifie

**Fragilite:** F02 — x5600 exporte SUBSTRATE_OPTIONS et generate_site_guide

**Declencheur:** Suppression ou renommage de la constante `SUBSTRATE_OPTIONS` dans x5600.

```
PROPAGATION:
x5600 (site_guide)
  |
  ├──> x5700 (cost_engine) importe SUBSTRATE_OPTIONS
  |      |── ImportError au demarrage du module
  |      └── Module nutrition_intelligence refuse de charger
  |
  ├──> x5800 (recipe_engine) importe generate_site_guide
  |      |── ImportError au demarrage du module
  |      └── Module nutrition_intelligence refuse de charger
  |
  └──> __init__.py (package)
         |── Import cascade echoue
         |── router.py ne peut pas importer le package
         └── TOUS les endpoints /api/v6/nutrition-intelligence/* sont HS
```

**Points de rupture:**

| # | Composant | Type | Effet |
|---|---|---|---|
| 1 | __init__.py | ImportError fatal | Package entier HS |
| 2 | router.py | ImportError fatal | Tous endpoints nutrition-intelligence HS |
| 3 | supra-panel | Endpoint 500 | supraData = null dans le frontend |
| 4 | Tous les onglets sauf FICHE | Render echec | Panneau SUPRA en erreur |

**Rayon d'explosion:**

| Onglet | Impact | Severite |
|---|---|---|
| SUPRA parent | supraData = null, erreur de chargement | CRITIQUE |
| ANALYSE | Score, Gauge, Mineraux, Recette, Couts — TOUT absent | CRITIQUE |
| FICHE | Fonctionne (utilise salines-ultime, pas nutrition_intelligence) | AUCUN |
| INTELLIGENCE | Produits absents | CRITIQUE |
| COMPAREZ | Produits absents | CRITIQUE |
| COMMANDEZ | Order + Products absents | CRITIQUE |

**Mesures de confinement:**
1. **Pre-commit Gatekeeper** — Devrait detecter la modification d'un fichier critique
2. **Test d'import** au demarrage: `python -c "from engines.nutrition_intelligence import *"` (A IMPLEMENTER)
3. **FICHE est isole** — Module C (salines_ultime) fonctionne independamment
4. **Soil/analyze est isole** — Module D continue de fonctionner
5. **Impact MAXIMAL** — 4 onglets sur 5 sont en echec. Seule FICHE survit.

---

### SCENARIO F03 — SPOF supra-panel (router.py)

**Fragilite:** F03 — Le router.py orchestre 11+ fonctions en sequence

**Declencheur:** Un des 11 appels dans l'endpoint supra-panel leve une exception non geree (ex: x5100 recoit un species inconnu).

```
PROPAGATION:
router.py (supra-panel)
  |
  |── Appel x5100 compute_mineral_score() → Exception
  |── FastAPI retourne HTTP 500
  |── Frontend recoit erreur sur l'appel [1] de fetchAll
  |── Promise.allSettled capture l'echec → supraData = null
  |
  └── Les 3 autres appels (saline/analyze, fiche, soil) reussissent
```

**Points de rupture:**

| # | Composant | Type | Effet |
|---|---|---|---|
| 1 | router.py supra-panel | HTTP 500 | supraData = null |
| 2 | ANALYSE | Pas de score, gauge, mineraux | CRITIQUE |
| 3 | INTELLIGENCE | Pas de produits | CRITIQUE |
| 4 | COMPAREZ | Pas de produits | CRITIQUE |
| 5 | COMMANDEZ | Pas de commande ni produits | CRITIQUE |

**Rayon d'explosion:**

| Onglet | Impact | Severite |
|---|---|---|
| SUPRA parent | supraData null, 3 autres OK | HAUTE |
| ANALYSE | Partiellement vide (ultraData + soilData OK) | HAUTE |
| FICHE | **FONCTIONNE** (ficheData OK) | AUCUN |
| INTELLIGENCE | Vide (pas de products) | CRITIQUE |
| COMPAREZ | Vide | CRITIQUE |
| COMMANDEZ | Partiellement vide (cart OK, order/products absents) | HAUTE |

**Mesures de confinement:**
1. **Promise.allSettled** (deja en place) — Les autres appels ne sont pas bloques
2. **Try/except par moteur** dans le supra-panel (A RENFORCER)
3. **Frontend defensif** — Chaque section utilise `supraData?.score?.score_global` (optionnel chaining)
4. **FICHE totalement isole** — Salines Ultime Engine independant
5. **Panier isole** — Cart API fonctionne independamment

---

### SCENARIO F04 — Orchestrateur saline_recommendation (#22)

**Fragilite:** F04 — Depend de 5 sous-moteurs (#17-#21)

**Declencheur:** `seasonal_metabolism_engine` (#21) recoit un mois invalide (0 ou 13).

```
PROPAGATION:
saline_recommendation_engine (#22)
  |
  |── Appelle get_metabolic_state(month=0) → Exception/resultat invalide
  |── generate_full_analysis() echoue ou retourne donnees incoherentes
  |── router.py (#23) retourne analyse incomplete
  |── POST /api/v1/saline/analyze retourne erreur ou donnees partielles
  |
  └── Frontend: ultraData = null ou partiel
```

**Rayon d'explosion:**

| Onglet | Impact | Severite |
|---|---|---|
| ANALYSE | Gauge ULTRA absente, engines.soil/metabolism/vegetation vides | HAUTE |
| FICHE | **AUCUN** (utilise salines-ultime, pas saline_engine) | AUCUN |
| INTELLIGENCE | **AUCUN** (utilise supraData.products) | AUCUN |
| COMPAREZ | **AUCUN** | AUCUN |
| COMMANDEZ | **AUCUN** | AUCUN |

**Mesures de confinement:**
1. **Impact confine a ANALYSE** — Un seul onglet affecte
2. **Validation entree mois** dans le frontend: `month = Math.max(1, Math.min(12, month))` (A IMPLEMENTER)
3. **Try/except dans chaque sous-moteur** (partiellement en place)
4. **supraData reste fonctionnel** — Les 4 autres onglets ne dependent pas de ultraData

---

### SCENARIO F05 — Dependance Stripe/MongoDB (#24 ecommerce)

**Fragilite:** F05 — Checkout depend de Stripe API et MongoDB

**Declencheur:** Stripe API retourne un timeout ou une erreur 502.

```
PROPAGATION:
ecommerce_router (#24)
  |
  |── POST /api/v1/saline/shop/checkout → Stripe API timeout
  |── Backend retourne HTTP 500 ou erreur Stripe
  |── Frontend: handleCheckout() echoue
  |── Utilisateur ne peut pas finaliser le paiement
  |
  └── Le panier reste intact, les autres fonctions SUPRA non impactees
```

**Rayon d'explosion:**

| Onglet | Impact | Severite |
|---|---|---|
| ANALYSE | **AUCUN** | AUCUN |
| FICHE | **AUCUN** | AUCUN |
| INTELLIGENCE | **AUCUN** | AUCUN |
| COMPAREZ | **AUCUN** | AUCUN |
| COMMANDEZ | Bouton "Payer avec Stripe" echoue | HAUTE |

**Mesures de confinement:**
1. **Impact confine a COMMANDEZ** col.3 uniquement
2. **Panier persiste** (MongoDB/localStorage) — Les articles ne sont pas perdus
3. **Message d'erreur** pour l'utilisateur (A VERIFIER si en place)
4. **AUCUN autre onglet impacte** — Isolation totale du checkout

---

### SCENARIO F06 — Monolithe frontend (1259 lignes)

**Fragilite:** F06 — Erreur de syntaxe dans un composant casse tout

**Declencheur:** Erreur de syntaxe JSX dans ComparezTab (ex: balise non fermee).

```
PROPAGATION:
NutritionPointDetailPanel.jsx
  |
  |── Erreur de syntaxe dans ComparezTab (ligne ~1057)
  |── React refuse de compiler le fichier entier
  |── Hot reload echoue
  |── Le panneau SUPRA ne s'affiche plus du tout
  |
  └── TOUS les onglets sont HS
```

**Rayon d'explosion:**

| Onglet | Impact | Severite |
|---|---|---|
| SUPRA parent | Panneau ne s'affiche pas | CRITIQUE |
| ANALYSE | HS | CRITIQUE |
| FICHE | HS | CRITIQUE |
| INTELLIGENCE | HS | CRITIQUE |
| COMPAREZ | HS (source de l'erreur) | CRITIQUE |
| COMMANDEZ | HS | CRITIQUE |

**Mesures de confinement:**
1. **AUCUN confinement possible** dans l'etat actuel (fichier monolithique)
2. **Apres modularisation (R3):** React Error Boundaries par onglet confineront l'erreur
3. **ESLint** en pre-commit detecte les erreurs de syntaxe (partiellement en place)
4. **Resolution:** La modularisation R3 est la mitigation STRUCTURELLE de F06

---

### SCENARIO F07 — Point d'entree __init__.py (30 exports)

**Fragilite:** F07 — Import defaillant empeche le chargement

**Declencheur:** Renommage d'une fonction dans x6030 sans mettre a jour __init__.py.

```
PROPAGATION:
__init__.py
  |
  |── from .x6030_product_ecosystem import get_product_ecosystem → ImportError
  |── Package nutrition_intelligence ne charge pas
  |── router.py ne peut pas importer
  |── TOUS les endpoints /api/v6/nutrition-intelligence/* retournent 500
  |
  └── Identique au scenario F02
```

**Rayon d'explosion:** Identique a F02 — 4 onglets sur 5 en echec. FICHE survit.

**Mesures de confinement:**
1. **Test d'import global** au demarrage du serveur (A IMPLEMENTER)
2. **Imports granulaires** dans router.py au lieu d'importer tout le package (OPTION FUTURE)
3. **Pre-commit Gatekeeper** — Devrait detecter les imports brises

---

### SCENARIO F08 — Scoring deterministe (hash MD5)

**Fragilite:** F08 — Scores non reels (Soil V1, Salines Ultime)

**Declencheur:** Un utilisateur prend une decision terrain basee sur un score de sol simule qui ne correspond pas a la realite.

```
PROPAGATION:
soil_engine / salines_ultime_engine
  |
  |── Score de sol: "Sable grossier, Grade C, Score 47" (SIMULE)
  |── Realite terrain: Sol argileux riche (devrait etre Score 85+)
  |── Utilisateur applique des mineraux inadaptes au type de sol reel
  |
  └── Impact hors-systeme (decision terrain incorrecte)
```

**Rayon d'explosion:**

| Onglet | Impact | Severite |
|---|---|---|
| ANALYSE | Sol affiche = incorrect vs realite | HAUTE |
| FICHE | 5 scores FICHE potentiellement faux | HAUTE |
| INTELLIGENCE | Produits scores pour mauvais sol | MODERE |
| COMPAREZ | Comparaison basee sur faux scores | MODERE |
| COMMANDEZ | Commande basee sur fausse recette | MODERE |

**Mesures de confinement:**
1. **Documentation V1 NON CERTIFIEE** dans le code (deja en place pour Soil)
2. **Avertissement frontend** pour l'utilisateur (A IMPLEMENTER)
3. **Plan V2** avec donnees pedologiques reelles (IRDA, MFFP) (FUTUR)
4. **Impact non technique** — Le systeme fonctionne correctement, les donnees sont fausses

---

### SCENARIO F09 — Catalogue produits hardcode

**Fragilite:** F09 — Ajout/modification produit necessite redeploiement

**Declencheur:** Un nouveau produit mineral est lance sur le marche. L'administrateur veut l'ajouter au catalogue.

```
PROPAGATION:
x6000_product_score.py
  |
  |── Catalogue statique dans le code Python
  |── Ajout d'un produit necessite:
  |      1. Modifier x6000_product_score.py
  |      2. Ajouter scoring dans x6010/x6011/x6012
  |      3. Redeployer le backend
  |
  └── Impact: delai d'ajout = cycle de deploiement complet
```

**Rayon d'explosion:** Aucun impact technique. Impact OPERATIONNEL (delai de mise a jour).

**Mesures de confinement:**
1. **Base de donnees produits** (MongoDB) pour gestion dynamique (FUTUR)
2. **Pipeline fournisseur x7000** deja implemente mais non connecte au catalogue principal
3. **Impact nul sur les onglets existants** — Produits actuels fonctionnent

---

### SCENARIO F10 — Donnees PREMIUM hardcodees frontend

**Fragilite:** F10 — Identique a F09 mais pour le frontend

**Declencheur:** Une nouvelle espece (ex: wapiti) doit etre ajoutee aux donnees physiologiques.

```
PROPAGATION:
NutritionPointDetailPanel.jsx (lignes 83-116)
  |
  |── PHYSIOLOGY_DATA ne contient que chevreuil et orignal
  |── MALE_BEHAVIOR ne contient que chevreuil
  |── Ajout de wapiti necessite modifier le frontend et redeployer
  |
  └── Impact: delai + risque d'erreur dans le fichier monolithique
```

**Rayon d'explosion:** Aucun impact technique. Impact OPERATIONNEL.

**Mesures de confinement:**
1. **Phase R7** — Externalisation vers endpoint backend (PLANIFIE)
2. **Impact nul sur les onglets existants**

---

### SCENARIO F11 — Performance lineaire N+1

**Fragilite:** F11 — Boucle enrichissement O(3N)

**Declencheur:** Le catalogue passe de 10 a 100 produits.

```
PROPAGATION:
router.py (supra-panel, lignes 244-265)
  |
  |── 10 produits → 30 appels → ~178ms (actuel)
  |── 100 produits → 300 appels → ~1500ms (projete)
  |── 500 produits → 1500 appels → ~7500ms (projete)
  |
  └── Timeout potentiel pour l'utilisateur (> 5s)
```

**Rayon d'explosion:**

| Onglet | Impact | Severite |
|---|---|---|
| TOUS | Temps de chargement augmente | MODERE a N=100 |
| TOUS | Timeout possible | CRITIQUE a N=500 |

**Mesures de confinement:**
1. **Phase R6** — Fonctions batch (PLANIFIE)
2. **Actuel N=10** — Non critique aujourd'hui
3. **Pagination produits** (OPTION FUTURE)

---

### SCENARIO F12 — Promise.allSettled (appel lent)

**Fragilite:** F12 — Si un appel est lent, tous les onglets attendent

**Declencheur:** L'API Overpass OSM est lente (10s) et saline/analyze appelle le cache.

```
PROPAGATION:
fetchAll() — Promise.allSettled
  |
  |── [1] supra-panel: 180ms ✓
  |── [2] saline/analyze: 10000ms (OSM lent)
  |── [3] fiche: 130ms ✓
  |── [4] soil/analyze: 120ms ✓
  |
  └── Promise.allSettled attend les 4: temps total = 10000ms
      Loading spinner pendant 10s
      Mais tous les resultats sont recuperes (pas de perte)
```

**Rayon d'explosion:**

| Onglet | Impact | Severite |
|---|---|---|
| SUPRA parent | Loading prolonge | MODERE |
| TOUS les onglets | Attente avant affichage | MODERE |

**Mesures de confinement:**
1. **Promise.allSettled** (deja en place) — Pas de rejet global
2. **Cache OSM** (deja en place, 235 polygones) — Reduit les appels externes
3. **Affichage progressif** — Rendre les onglets au fur et a mesure (A IMPLEMENTER)
4. **Timeout par appel** (A IMPLEMENTER)

---

## 3. SYNTHESE — MATRICE D'IMPACT PAR ONGLET

### Vue globale: "Quels scenarios cassent quels onglets?"

| Scenario | SUPRA | ANALYSE | FICHE | INTELLIGENCE | COMPAREZ | COMMANDEZ | Nb onglets |
|---|---|---|---|---|---|---|---|
| F01 (x5500) | MODERE | HAUTE | — | — | — | MODERE | 3 |
| F02 (x5600) | CRITIQUE | CRITIQUE | — | CRITIQUE | CRITIQUE | CRITIQUE | 5 |
| F03 (SPOF supra) | HAUTE | HAUTE | — | CRITIQUE | CRITIQUE | HAUTE | 5 |
| F04 (saline_reco) | — | HAUTE | — | — | — | — | 1 |
| F05 (Stripe/MongoDB) | — | — | — | — | — | HAUTE | 1 |
| F06 (monolithe) | CRITIQUE | CRITIQUE | CRITIQUE | CRITIQUE | CRITIQUE | CRITIQUE | 6 |
| F07 (__init__.py) | CRITIQUE | CRITIQUE | — | CRITIQUE | CRITIQUE | CRITIQUE | 5 |
| F08 (deterministe) | — | HAUTE | HAUTE | MODERE | MODERE | MODERE | 5 |
| F09 (catalogue) | — | — | — | — | — | — | 0 |
| F10 (PREMIUM) | — | — | — | — | — | — | 0 |
| F11 (N+1 perf) | MODERE | MODERE | — | MODERE | MODERE | MODERE | 5 |
| F12 (appel lent) | MODERE | MODERE | MODERE | MODERE | MODERE | MODERE | 6 |

### Resilience par onglet

| Onglet | Scenarios CRITIQUE | Scenarios HAUTE | Scenarios MODERE | Resilience |
|---|---|---|---|---|
| FICHE | 1 (F06) | 1 (F08) | 1 (F12) | **LA PLUS RESILIENTE** — Isolee de nutrition_intelligence |
| COMMANDEZ | 3 (F02, F06, F07) | 2 (F03, F05) | 3 (F01, F08, F11) | FAIBLE |
| ANALYSE | 3 (F02, F06, F07) | 3 (F01, F03, F04, F08) | 2 (F11, F12) | **LA PLUS VULNERABLE** |
| INTELLIGENCE | 3 (F02, F03, F06, F07) | 0 | 3 (F08, F11, F12) | FAIBLE |
| COMPAREZ | 3 (F02, F03, F06, F07) | 0 | 2 (F08, F11) | FAIBLE |

### Scenarios a impact maximal (5+ onglets)

| Rang | Scenario | Onglets impactes | Cause racine | Confinement possible? |
|---|---|---|---|---|
| 1 | **F06** (monolithe) | **6/6** | Fichier unique 1259 lignes | NON (avant R3) / OUI (apres R3) |
| 2 | **F02** (x5600 supprime) | 5/6 | ImportError cascade | Partiellement (Gatekeeper) |
| 3 | **F07** (__init__.py) | 5/6 | ImportError package | Partiellement (test import) |
| 4 | **F03** (SPOF supra) | 5/6 | Exception non geree | OUI (try/except + defaults) |
| 5 | **F12** (appel lent) | 6/6 | Latence externe | OUI (timeout + affichage progressif) |

---

## 4. RECOMMANDATIONS DE CONFINEMENT PRIORITAIRES

| Priorite | Mesure | Scenarios mitigues | Phase R |
|---|---|---|---|
| 1 | **Modularisation R3** + Error Boundaries | F06 (elimination totale) | R3 |
| 2 | **Test d'import automatise** au demarrage serveur | F02, F07 (detection immediate) | R0 |
| 3 | **Try/except par moteur** dans supra-panel | F01, F03 (confinement exception) | R6 |
| 4 | **Timeout par appel API** dans fetchAll | F12 (confinement latence) | R4 |
| 5 | **Avertissement sol simule** visible pour l'utilisateur | F08 (transparence) | R5 |
| 6 | **Fonctions batch** x6010-x6012 | F11 (performance) | R6 |
| 7 | **Message erreur Stripe** clair | F05 (UX checkout) | R4 |

---

*Rapport genere conformement au protocole BCE-4X-GLOBAL-PLUS-TOTAL*
*Autorite: COMMANDANT STEEVE-MAX*
*Branche: BIONIC_REWRITE_P0*
*Date: 2026-02-07*

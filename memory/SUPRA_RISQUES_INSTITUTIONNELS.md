# SUPRA_RISQUES_INSTITUTIONNELS.md
# ============================================================
# COMPLEMENT (C) — MATRICE DE RISQUES INSTITUTIONNELS BCE-4X
# ============================================================
# Protocole: BCE-4X-GLOBAL-PLUS-TOTAL
# Autorite: COMMANDANT STEEVE-MAX
# Branche: BIONIC_REWRITE_P0
# Date: 2026-02-07
# Statut: LIVRABLE COMPLEMENTAIRE — EN ATTENTE DE VALIDATION
# ============================================================

---

## 1. RISQUES TECHNIQUES

### 1.1 Registre des risques techniques

| ID | Risque | Probabilite | Impact | Score (PxI) | Composants concernes | Mitigation proposee |
|---|---|---|---|---|---|---|
| RT01 | **Cassure import __init__.py** — Le renommage ou la suppression d'une fonction exportee dans `__init__.py` (30 exports) empeche le chargement complet du module nutrition_intelligence. Le router.py importe tout via `from engines.nutrition_intelligence import (...)`. Un seul import defaillant = module entier HS. | MOYENNE | CRITIQUE | **12** | Module A (__init__.py, router.py) | Tests d'import automatises avant chaque commit. Verifier que les 30 exports sont resolvables. |
| RT02 | **Regression supra-panel** — L'endpoint `/supra-panel` orchestre 11+ fonctions synchrones. Modification du format de retour d'un seul moteur (ex: cle renommee dans x5100) casse le frontend sans erreur visible — les donnees sont simplement absentes (undefined). | HAUTE | HAUTE | **16** | router.py (supra-panel), Frontend | Validation de schema Pydantic sur la reponse supra-panel. Contract testing. |
| RT03 | **Boucle N+1 sous charge** — L'enrichissement produits (x6010, x6011, x6012) est lineaire en O(3N). Avec 50+ produits, le temps de reponse depasserait 1s et pourrait timeout. | FAIBLE | MOYENNE | **4** | router.py L244-265 | Creer fonctions batch. Actuellement N=10 produits, non critique. |
| RT04 | **Stripe API down** — Coupure Stripe = checkout impossible. Le panier reste fonctionnel mais le paiement est bloque. | FAIBLE | HAUTE | **6** | #24 ecommerce_router | Message d'erreur clair pour l'utilisateur. File d'attente locale pour retry. |
| RT05 | **MongoDB down** — Perte de persistence panier. Les sessions de panier en cours sont perdues. | FAIBLE | MOYENNE | **4** | #24 ecommerce_router | Panier localStorage en fallback (deja partiellement en place). |
| RT06 | **Fichier monolithique JSX** — Erreur de syntaxe dans n'importe quel composant de tab casse le panneau SUPRA entier (React ne peut pas rendre un composant avec erreur). | MOYENNE | HAUTE | **12** | NutritionPointDetailPanel.jsx | Modularisation en fichiers separes + Error Boundaries React par onglet. |
| RT07 | **Hot reload frontend** — Modification de NutritionPointDetailPanel.jsx (1259 lignes) peut causer des re-rendus lents en developpement et des erreurs de state stale. | FAIBLE | FAIBLE | **2** | Frontend dev | Modularisation resout ce risque. |

### 1.2 Matrice de severite — Risques techniques

```
              IMPACT
              Faible    Moyenne   Haute     Critique
PROBABILITE   
Haute         —         —         RT02      —
Moyenne       —         —         RT06      RT01
Faible        RT07      RT03,RT05 RT04      —
```

### 1.3 Risques techniques par zone

| Zone | Risques | Score total |
|---|---|---|
| Backend Module A (nutrition_intelligence) | RT01, RT02, RT03 | 32 |
| Backend Module B (saline_engine) | RT04, RT05 | 10 |
| Frontend (SUPRA panel) | RT06, RT07 | 14 |
| **TOTAL** | **7 risques** | **56** |

---

## 2. RISQUES D'INTERCONNEXION

### 2.1 Registre des risques d'interconnexion

| ID | Risque | Probabilite | Impact | Score | Flux concerne | Mitigation |
|---|---|---|---|---|---|---|
| RI01 | **Desynchronisation saison** — Le frontend envoie `season` (statique, du point nutritionnel) au supra-panel mais `seasonMap[month]` (dynamique, date actuelle) a saline/analyze et salines-ultime/fiche. En janvier, le point peut avoir `season: 'automne'` mais les moteurs ULTRA et FICHE recoivent `season: 'hiver'`. | HAUTE | MOYENNE | **12** | fetchAll → 4 endpoints | Unifier la source de saison: utiliser exclusivement `seasonMap[month]` pour tous les appels, OU exclusivement `np.season`. |
| RI02 | **Double scoring sol** — Le panneau ANALYSE affiche les donnees de sol provenant de deux sources independantes (saline_engine/soil vs soil_engine). Ces deux moteurs utilisent des algorithmes differents pour les memes coordonnees. Si les deux retournent des types de sol differents, l'UX est incoherente. | MOYENNE | MOYENNE | **8** | ANALYSE: engines.soil + soilData | Choisir UNE source de sol et supprimer l'autre. |
| RI03 | **Propagation modification x5500** — Si `compute_energy_protein` change son format de retour (ex: renommer `energy_need` en `energy_level`), x5700 et x5800 cassent silencieusement. Le router ne detecte pas l'erreur car il appelle les fonctions individuellement. | MOYENNE | HAUTE | **12** | x5500 → x5700, x5800 → router → Frontend | Tests d'integration inter-moteurs. Typage strict des retours. |
| RI04 | **State partage compareIds** — Le state `compareIds` est partage entre INTELLIGENCE (ecriture) et COMPAREZ (lecture). Si l'utilisateur navigue rapidement entre les deux onglets pendant un re-render, le state peut etre desynchronise (race condition React). | FAIBLE | FAIBLE | **2** | INTELLIGENCE ↔ COMPAREZ | Utiliser `useReducer` au lieu de `useState` pour compareIds. |
| RI05 | **Panier cross-onglet** — Le callback `addToCart` est partage entre INTELLIGENCE, COMMANDEZ et les items de commande. Un ajout rapide depuis plusieurs onglets peut causer des requetes concurrentes qui desynchronisent le panier cote serveur. | FAIBLE | MOYENNE | **4** | INTELLIGENCE, COMMANDEZ → cart API | Debounce sur addToCart ou queue locale. |
| RI06 | **Enrichissement produits non affiche** — Les champs `quality`, `availability`, `compliance` (x6010-x6012) sont ajoutes aux produits par le supra-panel mais AUCUN onglet ne les affiche. Calcul inutile qui alourdit la charge. | HAUTE | FAIBLE | **4** | supra-panel → products | Supprimer l'enrichissement ou afficher les donnees dans INTELLIGENCE. |
| RI07 | **Fallback saline_session_id** — Le `session_id` genere cote client (`sal_` + random) n'est jamais valide cote serveur. Un navigateur en mode prive perd le panier a chaque fermeture. Pas de lien entre session panier et authentification utilisateur (admin@huntiq.com). | MOYENNE | MOYENNE | **8** | Frontend localStorage → cart API | Lier la session panier a l'ID utilisateur authentifie. |

### 2.2 Matrice de severite — Risques d'interconnexion

```
              IMPACT
              Faible    Moyenne   Haute
PROBABILITE   
Haute         RI06      RI01      —
Moyenne       —         RI02,RI07 RI03
Faible        RI04      RI05      —
```

### 2.3 Carte thermique des interconnexions a risque

```
SUPRA Parent ────────────> fetchAll() ──────── RI01 (saison)
    |                           |
    |                      [4 appels]
    |                      /    |    \     \
    |                supra   saline   fiche   soil
    |                panel   analyze  ultime  analyze
    |                  |        |        |       |
    |                  |     RI02 ←──────+───────┘ (double sol)
    |                  |
    |              RI03 (x5500 propagation)
    |              RI06 (enrichissement inutile)
    |
INTELLIGENCE ─── RI04 (compareIds) ──> COMPAREZ
    |
    └─── RI05 (panier concurrent) ──> COMMANDEZ
                                          |
                                       RI07 (session)
```

---

## 3. RISQUES DE REGRESSION

### 3.1 Registre des risques de regression

| ID | Risque | Probabilite | Impact | Score | Phase R affectee | Tests de garde |
|---|---|---|---|---|---|---|
| RR01 | **Regression visuelle GOLDEN** — La modularisation des tabs (Phase R3) peut introduire des differences de rendu si les constantes BIONIC/GOLDEN ne sont pas correctement propagees aux nouveaux fichiers. | HAUTE | HAUTE | **16** | R3 (Modularisation) | T15-T19 (screenshots comparatifs) |
| RR02 | **Perte de data-testid** — Le deplacement de composants dans de nouveaux fichiers peut causer l'oubli de data-testid critiques. | MOYENNE | MOYENNE | **8** | R3 (Modularisation) | T20 + grep exhaustif data-testid |
| RR03 | **Cassure import IC** — L'extraction du composant IC (Phase R2) doit etre faite dans les 5 composants simultanement. Si un composant oublie l'import, le tab entier ne rend pas. | HAUTE | HAUTE | **16** | R2 (IC Extraction) | T01 + T15-T19 |
| RR04 | **Regression panier** — La correction du fallback product_id (Phase R4, E13) peut empêcher l'ajout de certains items de commande au panier si le backend ne fournit pas de product_id. | MOYENNE | MOYENNE | **8** | R4 (Corrections UX) | T18 (COMMANDEZ screenshot) |
| RR05 | **Regression performance** — L'optimisation batch (Phase R6) peut modifier le format de retour des produits enrichis, cassant l'affichage INTELLIGENCE. | MOYENNE | HAUTE | **12** | R6 (Optimisation) | T08 (latence) + T17 (INTELLIGENCE) |
| RR06 | **Regression GUIDE PRO** — Le GUIDE PRO (PedagogieModule) est en premiere position dans ANALYSE. Toute modification du layout peut le deplacer. | FAIBLE | HAUTE | **6** | R3, R4 | T19 (position GUIDE PRO) |
| RR07 | **Regression Vegetation/Hydrologie** — Le layout cote-a-cote (grid-cols-2) de Vegetation et Hydrologie dans ANALYSE peut etre casse par la modularisation. | MOYENNE | MOYENNE | **8** | R3 (Modularisation) | T15 (ANALYSE screenshot) |
| RR08 | **Regression BionicLegend** — La legende ne doit pas chevaucher les controles de zoom (corrige dans session precedente). Toute modification de z-index ou de positionnement dans le panneau peut re-introduire ce probleme. | FAIBLE | HAUTE | **6** | R3, R4 | Screenshot carte avec legende visible |

### 3.2 Matrice de severite — Risques de regression

```
              IMPACT
              Faible    Moyenne   Haute
PROBABILITE   
Haute         —         —         RR01,RR03
Moyenne       —         RR02,RR04,RR07 RR05
Faible        —         —         RR06,RR08
```

### 3.3 Matrice Phase-Risque

| Phase | Risques de regression | Score cumule | Niveau de risque |
|---|---|---|---|
| R1 (Nettoyage) | Aucun | 0 | NEGLIGEABLE |
| R2 (IC Extraction) | RR03 | 16 | ELEVE |
| R3 (Modularisation) | RR01, RR02, RR06, RR07 | 38 | **CRITIQUE** |
| R4 (Corrections UX) | RR04, RR06 | 14 | MODERE |
| R5 (Coherence donnees) | Aucun specifique | 0 | NEGLIGEABLE |
| R6 (Optimisation) | RR05 | 12 | MODERE |
| R7 (Externalisation) | Aucun specifique | 0 | NEGLIGEABLE |

**Phase la plus risquee: R3 (Modularisation)** — Score cumule 38. Necessite le plus grand nombre de tests de regression.

---

## 4. RISQUES DE DIVERGENCE INSTITUTIONNELLE

### 4.1 Registre des risques de divergence BCE-4X

| ID | Risque | Probabilite | Impact | Score | Norme BCE-4X concernee | Mitigation |
|---|---|---|---|---|---|---|
| RD01 | **Divergence GOLDEN entre fichiers** — Apres modularisation (R3), les constantes GOLDEN (couleurs, paddings, tailles de texte) pourraient etre modifiees dans un fichier sans etre propagees aux autres. Perte d'uniformite visuelle. | HAUTE | HAUTE | **16** | Standard GOLDEN Visual (10 normes) | Fichier unique `constants.js` pour BIONIC, GOLDEN, tailles. Import obligatoire. |
| RD02 | **Perte du protocole BCE-4X-LOCK** — L'attribut `data-bce4x-locked="true"` sur les boutons SupraButton pourrait etre omis dans de nouveaux composants crees durant la reconstruction. | MOYENNE | MOYENNE | **8** | BCE-4X Lock | Grep automatise en pre-commit: tout `<SupraButton` doit avoir `data-bce4x-locked`. |
| RD03 | **Divergence nomenclature data-testid** — De nouveaux fichiers pourraient introduire des conventions de nommage differentes pour les data-testid (ex: `supra_analyse` vs `supra-analyse-tab`). | MOYENNE | FAIBLE | **4** | Nomenclature testid BCE-4X | Convention documentee: prefixe `supra-` + nom-tab + role. Kebab-case uniquement. |
| RD04 | **Divergence documentation moteurs** — Le SOIL ENGINE V1 est bien documente (non certifie), mais le SALINES ULTIME ENGINE utilise la meme methode deterministe sans documentation equivalente. Apres reconstruction, risque d'oubli de documentation sur d'autres moteurs. | MOYENNE | MOYENNE | **8** | Transparence donnees BCE-4X | Chaque moteur deterministe DOIT avoir un header de documentation identique au SOIL ENGINE V1. |
| RD05 | **Divergence hierarchie DOM** — Le GUIDE PRO (PedagogieModule) est place en premiere position dans ANALYSE conformement a la directive COMMANDANT. Apres modularisation, cette position pourrait etre modifiee involontairement. | FAIBLE | HAUTE | **6** | Hierarchie STEEVE-MAX | Commentaire BCE-4X verrouille dans le code: `/* BCE-4X LOCKED: PedagogieModule DOIT etre en position 1 */` |
| RD06 | **Divergence footer institutionnel** — Le footer SUPRA contient "SUPRA v2 | 7 Moteurs ULTRA | Stripe | BCE-4X / STEEVE-MAX V6". Toute modification du texte sans autorisation constitue une violation institutionnelle. | FAIBLE | MOYENNE | **4** | Identite institutionnelle | Footer inclus dans le fichier `constants.js` avec commentaire LOCKED. |
| RD07 | **Perte SHA256 apres reconstruction** — Les hash SHA256 des fichiers dans BCE4X_GLOBAL_LOCK.json ne correspondront plus apres reconstruction. Sans mise a jour du lock, le Gatekeeper peut bloquer les commits. | HAUTE | HAUTE | **16** | BCE-4X-GLOBAL-LOCK | Phase R9 dediee a la regeneration des hash SHA256. |

### 4.2 Matrice de severite — Risques de divergence

```
              IMPACT
              Faible    Moyenne   Haute
PROBABILITE   
Haute         —         —         RD01,RD07
Moyenne       RD03      RD02,RD04 —
Faible        —         RD06      RD05
```

---

## 5. SYNTHESE GLOBALE DES RISQUES

### 5.1 Tableau recapitulatif

| Categorie | Nombre de risques | Score total | Risque moyen | Risques CRITIQUES |
|---|---|---|---|---|
| Techniques (RT) | 7 | 56 | 8.0 | RT01, RT02, RT06 |
| Interconnexion (RI) | 7 | 50 | 7.1 | RI01, RI03 |
| Regression (RR) | 8 | 80 | 10.0 | RR01, RR03 |
| Divergence (RD) | 7 | 62 | 8.9 | RD01, RD07 |
| **TOTAL** | **29** | **248** | **8.6** | **7 critiques** |

### 5.2 Top 10 des risques par score (PxI)

| Rang | ID | Score | Description courte |
|---|---|---|---|
| 1 | RR01 | 16 | Regression visuelle GOLDEN (modularisation) |
| 2 | RR03 | 16 | Cassure import IC (extraction) |
| 3 | RT02 | 16 | Regression supra-panel (format retour) |
| 4 | RD01 | 16 | Divergence GOLDEN entre fichiers |
| 5 | RD07 | 16 | Perte SHA256 apres reconstruction |
| 6 | RT01 | 12 | Cassure import __init__.py |
| 7 | RT06 | 12 | Fichier monolithique JSX |
| 8 | RI01 | 12 | Desynchronisation saison |
| 9 | RI03 | 12 | Propagation modification x5500 |
| 10 | RR05 | 12 | Regression performance (batch) |

### 5.3 Actions de mitigation prioritaires (avant reconstruction)

| Priorite | Action | Risques mitigues | Phase R |
|---|---|---|---|
| 1 | Creer `constants.js` avec BIONIC, GOLDEN, SUPRA_CMD_COLOR, footer | RD01, RD06, RR01 | R3 |
| 2 | Tests d'import automatises (30 exports __init__.py) | RT01 | R0 |
| 3 | Screenshots de reference des 5 onglets | RR01, RR03, RR06, RR07, RR08 | R0 |
| 4 | Regenerer BCE4X_GLOBAL_LOCK.json apres chaque phase | RD07 | R1-R9 |
| 5 | Convention data-testid documentee | RD03, RR02 | R0 |
| 6 | Commentaires BCE-4X LOCKED sur positions critiques | RD05, RR06 | R3 |
| 7 | Contract tests sur format retour supra-panel | RT02, RI03, RR05 | R0 |

---

## 6. VERDICT RISQUES INSTITUTIONNELS

### Niveau de risque global: MODERE-ELEVE

La reconstruction SUPRA (R1-R9) est **realisable** mais la **Phase R3 (Modularisation)**
constitue le point de risque maximal avec un score cumule de regression de **38**.

**7 risques CRITIQUES** (score >= 16) ont ete identifies, dont 5 sont directement
lies a la phase de modularisation (R3). La mitigation passe par:

1. **Baselines visuelles exhaustives** (R0) — avant toute modification
2. **Fichier de constantes centralise** (R3.6) — avant la modularisation
3. **Tests de regression systematiques** (T15-T20) — apres chaque phase
4. **Regeneration SHA256** (R9) — verrouillage final

**STATUT: EN ATTENTE DE VALIDATION COMMANDANT STEEVE-MAX**
**RECONSTRUCTION SUPRA: STRICTEMENT INTERDITE JUSQU'A VALIDATION**

---

*Rapport genere conformement au protocole BCE-4X-GLOBAL-PLUS-TOTAL*
*Autorite: COMMANDANT STEEVE-MAX*
*Branche: BIONIC_REWRITE_P0*
*Date: 2026-02-07*

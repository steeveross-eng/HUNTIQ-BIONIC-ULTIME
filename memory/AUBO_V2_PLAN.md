# PLAN AUBO_V2 — PREPARATION
## Directive x5301-STEEVE_MAX — Section C
### AUCUNE EXECUTION — PLAN UNIQUEMENT — Attente directive x5302
### Protocole BCE-4X GOLDEN V6+ | Autorite : STEEVE-MAX

---

## 1. AJOUTS NECESSAIRES POUR AUBO_V2

### 1.1 Frontend — Cartographie des 31 pages
AUBO_V1 documente les pages (Section 1.7 et Annexe) mais ne cartographie pas :
- Les composants par page (nombre, hierarchie)
- Les appels API par page (quels endpoints chaque page consomme)
- Les stores Zustand et leurs dependances
- Les hooks personnalises et leurs modules backend associes

### 1.2 Base de donnees — Schema MongoDB complet
AUBO_V1 ne documente pas les collections MongoDB en detail :
- 34 collections existantes (noms, schemas, index)
- Relations inter-collections
- Volumes de donnees par collection
- Requetes critiques et aggregations

### 1.3 Routes backend (/routes/)
6 fichiers de routes non detailles dans AUBO_V1 :
- advanced_zones.py (7 endpoints)
- bathymetry.py (7 endpoints)
- bionic_engine_router.py (29 endpoints)
- ecological_router_v8.py (5 endpoints)
- reports.py (4 endpoints)
- user_data.py (9 endpoints)
Total : 61 endpoints non cartographies individuellement

### 1.4 BCE Engine (/bce/) — Detail interne
Structure bce/ mentionnee mais non detaillee :
- Contenu de golden/ (regles GOLDEN UI)
- Contenu de validators/ (validateurs specialises)
- Regles specifiques de bce_ruleset_v8.py
- Corridors V9 de bce_corridor_v9.py

### 1.5 Sous-routeurs bionic_engine_p0
18+ sous-routeurs listes mais non detailles individuellement :
- Endpoints specifiques de chaque sous-routeur (SSE, OSG, CME, etc.)
- Modeles de donnees de chaque sous-moteur
- Flux de donnees interne entre sous-moteurs

### 1.6 Integrations externes detaillees
AUBO_V1 mentionne Stripe, OSM, WMS mais ne detaille pas :
- Configuration de chaque integration
- Endpoints externes consommes
- Gestion des erreurs et fallbacks
- Rate limits et caching

---

## 2. CORRECTIONS

### 2.1 Comptage des endpoints
Le total "1675+" est une approximation. AUBO_V2 pourrait inclure un comptage exact
par module avec ventilation GET/POST/PUT/DELETE.

### 2.2 Consolidation V6 — Clarification
Les modules "facade" (ads_engine, learning_engine) n'ont pas d'endpoints propres.
AUBO_V2 devrait clarifier la distinction entre :
- Modules actifs (endpoints propres)
- Modules facade (consolidation logique)
- Modules deprecies (code present mais inactive)
- Modules standalone (fichiers .py sans directory)

---

## 3. SECTIONS MANQUANTES

### 3.1 Section "Monitoring & Observabilite"
- Metriques systeme (CPU, RAM, disque)
- Health checks par module
- Alerting et seuils

### 3.2 Section "Deploiement & Infrastructure"
- Configuration Supervisor
- Configuration Nginx
- Variables d'environnement (inventaire)
- Processus de deploiement

### 3.3 Section "Tests & Qualite"
- Couverture de tests par module
- Tests critiques existants
- Plan de tests de non-regression

### 3.4 Section "Changelog Consolidation V6"
- Historique des consolidations effectuees
- Mapping ancien_module → nouveau_module
- Prefixes API preserves vs modifies

---

## 4. POINTS A CLARIFIER (ATTENTE STEEVE-MAX)

### 4.1 Modules facade
Les modules ads_engine et learning_engine sont des facades.
Faut-il les detailler comme des modules a part entiere dans AUBO_V2
ou les documenter uniquement comme redirections ?

### 4.2 Modules deprecies
geo_engine et core/alimentation sont deprecies.
Doivent-ils rester dans la cartographie AUBO_V2 avec mention DEPRECATED
ou etre retires de la cartographie active ?

### 4.3 Profondeur de detail
AUBO_V1 documente au niveau module (nom, prefix, endpoints, role).
AUBO_V2 doit-il descendre au niveau endpoint individuel
(nom, methode, parametres, response) ?

### 4.4 Perimetre frontend
AUBO_V1 couvre principalement le backend.
AUBO_V2 doit-il inclure une cartographie frontend equivalente
(composants, stores, hooks, routes, CSS) ?

---

## ESTIMATION

| Element | Lignes estimees AUBO_V2 |
|---------|------------------------|
| AUBO_V1 existant | 673 |
| Frontend cartographie | +200 |
| MongoDB schemas | +150 |
| Routes detaillees | +100 |
| BCE detail | +80 |
| Sous-routeurs bionic_engine_p0 | +150 |
| Integrations externes | +80 |
| Monitoring | +60 |
| Deploiement | +60 |
| Tests | +50 |
| **AUBO_V2 estime** | **~1600 lignes** |

---

**PLAN UNIQUEMENT — AUCUNE EXECUTION**
**Attente directive x5302 de STEEVE-MAX pour generation AUBO_V2**
**Protocole** : BCE-4X GOLDEN V6+
**Merge main** : STRICTEMENT INTERDIT

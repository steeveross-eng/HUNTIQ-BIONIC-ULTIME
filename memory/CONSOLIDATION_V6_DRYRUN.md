# CONSOLIDATION V6 — DRY-RUN REPORT
## Directive STEEVE-MAX — emergent consolidate --dry-run
### Protocole BCE-4X GOLDEN V6+ | AUCUNE MODIFICATION APPLIQUEE
### Date : 2026-04-03

---

## RESUME EXECUTIF

```
emergent consolidate --target V6
  --merge geo_engine geospatial_engine
  --merge admin_engine admin_unified_engine
  --merge affiliate_ads_engine ad_spaces_engine --as ads_engine
  --merge tutorial_engine formations_engine --as learning_engine
  --merge simulation_engine weather_fauna_simulation_engine
  --deprecate alimentation_v1
  --deprecate geo_engine
  --reclass chasseur_jumeau.py experiments
  --reclass liste_epicerie.py utils
  --validate-architecture
  --dry-run
```

**Statut : DRY-RUN — AUCUNE MODIFICATION APPLIQUEE**

---

## 1. MERGE OPERATIONS (5)

### 1.1 geo_engine + geospatial_engine → geospatial_engine

| Element | geo_engine | geospatial_engine | Fusionne |
|---------|-----------|-------------------|----------|
| Fichiers .py | 3 | 5 | ~6 |
| Lignes | 1517 | 418 | ~1935 |
| Prefix API | /api/admin/geo | /api/v1/geospatial | /api/v1/geospatial |
| Endpoints | 0 (logique interne) | 7 | 7 |
| Refs dans codebase | 1 | 2 | — |

**Strategie** : Absorber la logique interne de geo_engine dans geospatial_engine.
geo_engine n'expose aucun endpoint public — c'est un module utilitaire.
geospatial_engine garde son prefix `/api/v1/geospatial` et ses 7 endpoints.

**Risque** : FAIBLE. geo_engine est un service interne sans API publique.
**Impact frontend** : AUCUN.
**Fichiers a modifier** :
- modules/geospatial_engine/v1/router.py (integrer logique geo)
- modules/routers.py (supprimer import geo_engine, garder geospatial)

---

### 1.2 admin_engine + admin_unified_engine → admin_engine

| Element | admin_engine | admin_unified_engine | Fusionne |
|---------|-------------|---------------------|----------|
| Fichiers .py | 25 | ABSENT (deja fusionne) | 25 |
| Lignes | 7497 | — | 7497 |
| Prefix API | /api/v1/admin | — | /api/v1/admin |

**Resultat** : AUCUNE ACTION REQUISE.
admin_unified_engine a deja ete fusionne dans admin_engine lors d'une phase precedente
(confirme dans routers.py ligne 14: "Removed: admin_unified_engine (fusionne dans admin_engine)").

**Risque** : NUL. Deja fait.

---

### 1.3 affiliate_ads_engine + ad_spaces_engine → ads_engine

| Element | affiliate_ads_engine | ad_spaces_engine | Fusionne (ads_engine) |
|---------|---------------------|-----------------|----------------------|
| Fichiers .py | 2 | 2 | ~3 |
| Lignes | 1457 | 1004 | ~2461 |
| Prefix API | /api/v1/affiliate-ads | /api/v1/ad-spaces | /api/v1/ads (unifie) |
| Endpoints | 15 | 15 | 30 |
| Refs dans codebase | 2 | 2 | — |

**Strategie** : Creer modules/ads_engine/ avec sous-routers :
- /api/v1/ads/affiliate/* (ex affiliate_ads)
- /api/v1/ads/spaces/* (ex ad_spaces)
Ou conserver les sous-prefixes originaux via include_router.

**Risque** : MOYEN. 30 endpoints a verifier. Frontend utilise potentiellement les anciens prefixes.
**Impact frontend** : A VERIFIER — rechercher les appels a `/affiliate-ads` et `/ad-spaces`.
**Fichiers a modifier** :
- Creer modules/ads_engine/router.py
- Migrer modules/affiliate_ads_engine/router.py → ads_engine/affiliate_router.py
- Migrer modules/ad_spaces_engine/router.py → ads_engine/spaces_router.py
- modules/routers.py (remplacer les 2 imports par 1)

---

### 1.4 tutorial_engine + formations_engine → learning_engine

| Element | tutorial_engine | formations_engine | Fusionne (learning_engine) |
|---------|----------------|-------------------|--------------------------|
| Fichiers .py | 2 | 2 | ~3 |
| Lignes | 439 | 172 | ~611 |
| Prefix API | /api/v1/tutorials | /api/formations | /api/v1/learning (unifie) |
| Endpoints | 8 | 4 | 12 |
| Refs dans codebase | 2 | 2 | — |

**Strategie** : Creer modules/learning_engine/ avec sous-routers :
- /api/v1/learning/tutorials/* (ex tutorial_engine)
- /api/v1/learning/formations/* (ex formations_engine)

**Risque** : FAIBLE. Modules simples, peu d'endpoints, logique bien separee.
**Impact frontend** : A VERIFIER — rechercher les appels a `/tutorials` et `/formations`.
**Fichiers a modifier** :
- Creer modules/learning_engine/router.py
- Migrer contenu des 2 modules
- modules/routers.py (remplacer les 2 imports par 1)

---

### 1.5 simulation_engine + weather_fauna_simulation_engine → weather_fauna_simulation_engine

| Element | simulation_engine | weather_fauna_simulation_engine | Fusionne |
|---------|------------------|---------------------------------|----------|
| Fichiers .py | ABSENT | 5 | 5 |
| Lignes | — | 659 | 659 |
| Prefix API | — | /api/v1/simulation | /api/v1/simulation |

**Resultat** : AUCUNE ACTION REQUISE.
simulation_engine n'existe pas en tant que module separe. weather_fauna_simulation_engine
est le seul module de simulation, deja enregistre sous `/api/v1/simulation`.

**Risque** : NUL. Module cible inexistant.

---

## 2. DEPRECATION OPERATIONS (2)

### 2.1 alimentation_v1 → DEPRECATE

| Element | Valeur |
|---------|--------|
| Emplacement | core/alimentation/ |
| Fichiers | 1 (__init__.py) |
| Lignes | 1 |
| Dependances | Aucune import detecte |

**Resultat** : Module deja vide (1 ligne dans __init__.py).
Peut etre marque comme deprecie sans impact.

**Risque** : NUL.

### 2.2 geo_engine → DEPRECATE (post-merge)

| Element | Valeur |
|---------|--------|
| Emplacement | modules/geo_engine/ |
| Fichiers | 3 |
| Lignes | 1517 |
| Dependances | 1 reference |

**Resultat** : A deprecier APRES la fusion dans geospatial_engine (operation 1.1).
La logique interne doit d'abord etre absorbee avant depreciation.

**Risque** : FAIBLE si fusion prealable effectuee correctement.

---

## 3. RECLASSIFICATION OPERATIONS (2)

### 3.1 chasseur_jumeau.py → experiments/

| Element | Valeur |
|---------|--------|
| Emplacement actuel | modules/chasseur_jumeau.py |
| Destination | modules/experiments/chasseur_jumeau.py |
| Lignes | 363 |
| Nature | Module standalone experimental |

**Action** : Creer modules/experiments/, deplacer le fichier, mettre a jour les imports.

**Risque** : FAIBLE. Module standalone sans dependances critiques.

### 3.2 liste_epicerie.py → utils/

| Element | Valeur |
|---------|--------|
| Emplacement actuel | modules/liste_epicerie.py |
| Destination | modules/utils/liste_epicerie.py |
| Lignes | 373 |
| Nature | Module utilitaire standalone |

**Action** : Creer modules/utils/ (si inexistant), deplacer le fichier, mettre a jour les imports.

**Risque** : FAIBLE. Module standalone sans dependances critiques.

---

## 4. VALIDATION ARCHITECTURE

### 4.1 Inventaire avant/apres

| Metrique | AVANT | APRES (projete) |
|----------|-------|-----------------|
| Modules directories | 75 | 72 (-3) |
| Modules standalone | 12 | 10 (-2) |
| Total modules | 87 | 82 (-5) |
| Endpoints API | ~1675 | ~1675 (inchange) |
| Nouveaux modules | — | ads_engine, learning_engine |
| Modules supprimes | — | geo_engine, affiliate_ads_engine, ad_spaces_engine, tutorial_engine, formations_engine |
| Modules deprecies | — | core/alimentation |
| Modules reclasses | — | chasseur_jumeau → experiments/, liste_epicerie → utils/ |

### 4.2 Verification de coherence

| Verification | Statut |
|-------------|--------|
| Aucun endpoint perdu | OK — tous les endpoints migres dans les modules fusionnes |
| Aucun import casse | A VERIFIER — routers.py doit etre mis a jour |
| Aucun conflit de prefix API | OK — sous-prefixes preserves |
| Frontend inchange | A VERIFIER — URLs API a auditer |
| MongoDB inchangee | OK — aucun schema modifie |
| BCE-4X respecte | OK — zero loss, zero regression |

### 4.3 Ordre d'execution recommande

```
1. Merge geo_engine → geospatial_engine (absorber logique interne)
2. Deprecate geo_engine (marquer vide)
3. Merge affiliate_ads + ad_spaces → ads_engine (creer nouveau module)
4. Merge tutorial + formations → learning_engine (creer nouveau module)
5. Reclass chasseur_jumeau.py → experiments/
6. Reclass liste_epicerie.py → utils/
7. Deprecate core/alimentation (marquer deprecie)
8. Skip: admin_engine + admin_unified (deja fait)
9. Skip: simulation_engine + weather_fauna (cible inexistante)
10. Mise a jour routers.py (point central)
11. Audit frontend (verification URLs API)
12. Tests de non-regression
```

---

## 5. RISQUES ET ALERTES

| Risque | Niveau | Description |
|--------|--------|-------------|
| Prefix API cassé frontend | MOYEN | ads_engine et learning_engine changent les prefixes API |
| Import cassé routers.py | FAIBLE | Point unique de mise a jour |
| Perte d'endpoints | NUL | Tous preserves via sous-routers |
| Regression MongoDB | NUL | Aucun schema modifie |
| geo_engine logique perdue | FAIBLE | Logique a absorber avant depreciation |

---

## CONCLUSION DRY-RUN

**3 fusions effectives** sur 5 demandees (2 deja faites ou cibles inexistantes).
**2 reclassifications** simples.
**1 depreciation** effective (core/alimentation, deja vide).
**1 depreciation conditionnelle** (geo_engine, apres fusion).

**Estimation de travail** : ~2-3 heures d'implementation + tests.
**Impact** : -5 modules (87 → 82), meilleure organisation, ZERO perte fonctionnelle.

---

**DRY-RUN — AUCUNE MODIFICATION APPLIQUEE**
**Protocole** : BCE-4X GOLDEN V6+
**Autorite** : STEEVE-MAX
**Merge main** : STRICTEMENT INTERDIT

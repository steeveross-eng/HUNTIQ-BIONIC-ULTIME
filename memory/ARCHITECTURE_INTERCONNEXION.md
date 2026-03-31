# ARCHITECTURE D'INTERCONNEXION — BCE-4X GOLDEN
## STEEVE-MAX — V1 INTERNE / V2 CERTIFIEE
## Date: 2026-03-30

---

## 1. SCHEMA DES FLUX ENTRE MODULES

```
                    ┌──────────────────┐
                    │   Admin Premium   │
                    │  (Orchestrateur)  │
                    └────────┬─────────┘
                             │ BCE-4X Validation
                    ┌────────▼─────────┐
                    │   BCE-4X Engine   │
                    │   (Gouvernance)   │
                    └────────┬─────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
┌───────▼───────┐   ┌───────▼───────┐   ┌───────▼───────┐
│   SUPRA v2    │   │   Analyse     │   │  Strategie    │
│  (5 onglets)  │   │  Territoire   │   │   du Jour     │
└───────┬───────┘   └───────┬───────┘   └───────┬───────┘
        │                    │                    │
        ├────────────────────┼────────────────────┤
        │                    │                    │
┌───────▼───────┐   ┌───────▼───────┐   ┌───────▼───────┐
│  Soil Engine  │   │ Intelligence  │   │   Comparez    │
│   (V1/V2)     │   │      IA       │   │  + Commandez  │
└───────────────┘   └───────────────┘   └───────────────┘
```

---

## 2. DEPENDANCES ENTRE MODULES

| Module Source     | Module Cible      | Type de donnee          | Validation requise              |
|-------------------|-------------------|-------------------------|---------------------------------|
| Soil Engine       | SUPRA v2 ANALYSE  | score_sol, type_sol     | Validation scoring BCE-4X       |
| Soil Engine       | SUPRA v2 FICHE    | recommendations_sol     | Validation sources + coherence  |
| Soil Engine       | Analyse Territoire| soil_overlay_map        | Validation donnees + rollback   |
| SUPRA v2          | Comparez          | scores_normalisés       | Validation inter-sites          |
| SUPRA v2          | Commandez         | recette_minerale        | Validation cout/disponibilite   |
| SUPRA v2          | Intelligence IA   | scores + historique     | Validation IA + sources         |
| SUPRA v2          | Strategie du Jour | score_saison + meteo    | Validation temps reel           |
| Analyse Territoire| SUPRA v2          | nutrition_points        | Validation GPS + zone           |
| Admin Premium     | Tous les modules  | permissions + config    | Validation BCE-4X obligatoire   |
| BCE-4X Engine     | Admin Premium     | logs + audits           | Immutable / read-only           |

---

## 3. VALIDATIONS A CHAQUE ETAPE

### 3.1 Validation de donnees
- Chaque flux inter-module DOIT valider:
  - Type de donnee (schema Pydantic)
  - Plage de valeurs (score 0-100, GPS valide, espece valide)
  - Completude (aucun champ null critique)
  - Coherence temporelle (timestamp recent)

### 3.2 Validation de scoring
- Tout score transmis entre modules DOIT:
  - Avoir un grade (S/A/B/C/D/F) coherent avec le score numerique
  - Etre accompagne de la version du moteur de scoring
  - Inclure le timestamp de calcul
  - Etre reproductible (memes inputs = meme score)

### 3.3 Validation de sources
- Toute recommandation transmise DOIT:
  - Citer ses sources (id + reference)
  - Etre alignee avec l'espece active
  - Etre alignee avec la saison active
  - Etre alignee avec le type de sol (si applicable)

### 3.4 Validation de coherence
- Aucune contradiction entre modules:
  - Si Soil Engine dit "sable grossier", SUPRA FICHE ne peut pas afficher "sol argileux"
  - Si Analyse Territoire dit "zone urbaine", SUPRA ne peut pas afficher "foret boreale"

---

## 4. MECANISMES DE ROLLBACK

| Scenario                        | Mecanisme                              | Responsable      |
|---------------------------------|----------------------------------------|------------------|
| Score Soil Engine invalide      | Fallback vers dernier score valide     | SUPRA v2         |
| API Soil Engine indisponible    | Cache local 24h + alerte Admin         | Frontend cache   |
| Donnee corrompue inter-module   | Log BCE-4X + alerte + rollback auto    | BCE-4X Engine    |
| Admin Premium modifie config    | Snapshot pre-modification + validation | Admin Premium    |
| Mise a jour moteur scoring      | Double-run (ancien + nouveau) + diff   | BCE-4X Engine    |

---

## 5. PLAN DE PHASAGE — INTERCONNEXIONS

### P1 — SUPRA <-> Soil Engine (V1 TERMINEE)
- Status: OPERATIONNEL
- Flux: GET /api/v1/soil/analyze -> SUPRA ANALYSE + FICHE
- Validation: Schema + plage + coherence type sol
- Limitation V1: Classification deterministe (GPS hash)

### P2 — SUPRA <-> Analyse Territoire
- Status: OPERATIONNEL (nutrition points -> SUPRA panel)
- Flux: Click marqueur -> ouverture panneau SUPRA avec lat/lng
- Validation: GPS valide + zone chasse autorisee
- A faire V2: Overlay cartographique sol sur la carte

### P3 — SUPRA <-> Strategie du Jour
- Status: PLANIFIE
- Flux: Scores SUPRA + meteo temps reel -> recommandation du jour
- Validation: Coherence saison + meteo + pression chasse
- Dependance: API meteo Environnement Canada

### P4 — SUPRA <-> Intelligence IA
- Status: PLANIFIE
- Flux: Historique scores + observations -> predictions IA
- Validation: Sources IA + confidence interval + explicabilite
- Dependance: Moteur IA (a definir)

### P5 — SUPRA <-> Admin Premium
- Status: PARTIEL (affichage permissions)
- Flux: Admin Premium -> config especes, sources, criteres
- Validation: BCE-4X obligatoire pour toute modification
- Role Admin: Superviseur, validateur, controleur

### P6 — Admin Premium <-> BCE-4X
- Status: PLANIFIE
- Flux: Toutes modifications Admin -> log BCE-4X immutable
- Validation: Authentification forte + audit trail
- Rollback: Snapshot automatique pre-modification

---

## 6. ADMIN PREMIUM — ROLE D'ORCHESTRATEUR

Admin Premium est autorise UNIQUEMENT comme:
- Superviseur: vue globale de l'ecosysteme
- Validateur: approbation des modifications de config
- Controleur de coherence: detection des contradictions inter-modules
- Gestionnaire des sources: ajout/modification/suppression de references scientifiques
- Gestionnaire des criteres: modification des poids et seuils de scoring
- Gestionnaire des permissions: controle d'acces aux modules
- Gestionnaire des modules: activation/desactivation des moteurs

REGLE ABSOLUE: Aucune donnee provenant d'Admin Premium ne doit impacter
l'ecosysteme sans validation BCE-4X prealable. Toute modification est:
1. Logguee dans BCE-4X (immutable)
2. Soumise a validation automatique (schema + coherence)
3. Reversible via rollback automatique
4. Tracable (qui, quand, quoi, pourquoi)

---

## 7. SOIL ENGINE V1 — LIMITES DOCUMENTEES

### Limites actuelles (V1):
- Classification DETERMINISTE basee sur un hash MD5 des coordonnees GPS
- AUCUNE integration de donnees pedologiques reelles (IRDA, MFFP, MRNF, CGQ)
- AUCUNE integration LiDAR reelle (relief, micro-vallons, thermiques)
- AUCUNE integration hydrologique reelle (drainage, saturation, ruissellement)
- Le score de sol est SIMULE, PAS MESURE
- Les 7 types de sol sont corrects taxonomiquement mais attribues par hash GPS

### Plan V2 SOIL ENGINE:
| Phase | Livrable                                    | Source de donnees           | Priorite |
|-------|---------------------------------------------|-----------------------------|----------|
| P1    | Integration cartographie pedologique        | IRDA Quebec (shapefiles)    | HAUTE    |
| P2    | Integration LiDAR relief                    | MRNF (DEM haute resolution) | HAUTE    |
| P3    | Integration hydrologique                    | MRNF (reseau hydrique)      | MOYENNE  |
| P4    | Score sur donnees reelles                   | Mesures terrain + labos     | HAUTE    |
| P5    | Validation terrain echantillonnage          | Protocole terrain defini    | HAUTE    |
| P6    | Certification BCE-4X                        | Validation STEEVE-MAX       | CRITIQUE |

### Communication externe:
AUCUNE communication externe ne doit presenter le SOIL ENGINE V1 comme
utilisant des donnees reelles. Le marqueur "V1 — INTERNE — NON CERTIFIEE"
est present dans:
- Les reponses API (/api/v1/soil/analyze -> champ "version_status")
- Le code source (docstring router.py)
- Cette documentation

---

## 8. STATUT GLOBAL

| Composant               | V1 Status        | V2 Requis pour          |
|--------------------------|------------------|-------------------------|
| GUIDE BIONIC Fiches      | FONCTIONNEL      | Certification BIONIC    |
| Soil Engine              | DETERMINISTE     | Certification pedolo    |
| SUPRA v2                 | OPERATIONNEL     | Production publique     |
| Analyse Territoire       | OPERATIONNEL     | Overlay sol carte       |
| Admin Premium            | PARTIEL          | Orchestration complete  |
| BCE-4X Logs              | OPERATIONNEL     | Audit complet           |
| Interconnexions          | P1-P2 faits      | P3-P6 requis            |

**V1 = acceptable pour tests internes et validation fonctionnelle.**
**V2 = requis pour certification et toute utilisation externe / marketing.**

Aucun passage en production publique avant validation STEEVE-MAX de la V2.

---

Document cree par: BCE-4X GOLDEN V6+
Autorite: STEEVE-MAX
Protocole: BCE-4X / ULTRA-MAX++ / GOLDEN

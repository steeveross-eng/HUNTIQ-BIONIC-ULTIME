# K3 ARCHITECTURE — SPECIES ENGINE (S0-S9)

**Protocole :** BCE-4X ULTIME ABSOLU
**Niveau :** TOP-ABSOLU
**Autorite :** COMMANDANT STEEVE-MAX
**Date :** 2026-02-14
**Branche :** SUPRA_RECONSTRUCTION

---

## 1. OBJECTIF

Construire un Species Engine ADDITIF qui consomme en LECTURE SEULE :
- Les profils operationnels de `bionic_ecological_engine/species_profiles.py` (8 especes)
- Les donnees scientifiques de `bionic_knowledge_engine/knowledge.json` K2 (4 especes)

Le Species Engine unifie ces deux referentiels via un resolveur d'identifiants
et expose des endpoints dedies sans modifier aucun moteur existant.

---

## 2. MAPPING SPECIES ID

| ID Operationnel (profiles) | ID Scientifique (knowledge) | Nom FR | Nom Latin |
|---|---|---|---|
| orignal | moose | Orignal | Alces alces |
| cerf_virginie | deer | Cerf de Virginie | Odocoileus virginianus |
| ours_noir | bear | Ours noir | Ursus americanus |
| wapiti | elk | Wapiti | Cervus canadensis |
| dindon_sauvage | — | Dindon sauvage | Meleagris gallopavo |
| caribou | — | Caribou | Rangifer tarandus caribou |
| cerf_mulet | — | Cerf mulet | Odocoileus hemionus |
| pronghorn | — | Antilocapre | Antilocapra americana |

Note : 4 especes (dindon, caribou, cerf_mulet, pronghorn) n'ont pas de
donnees K2 scientifiques. Elles retournent uniquement le profil operationnel.

---

## 3. STRUCTURE DU MODULE

```
backend/modules/species_engine/
    __init__.py
    router.py          # S1: FastAPI router /api/v6/species-engine/*
    resolver.py         # S2: Species ID Resolver (FR/EN/Latin/alias)
    bridge.py           # S3: Knowledge Bridge (fusion profiles + K2)
    seasonal.py         # S4: Seasonal Intelligence (K2.1)
    corridors.py        # S5: Dynamic Corridors (K2.2)
    zones.py            # S6: Ecological Zones (K2.4)
    cross_species.py    # S7: Cross-Species Intelligence (K2.5)
    nutrition.py        # S8: Advanced Nutrition (K2.3)
    K3_ARCHITECTURE.md  # S0: Ce document
```

---

## 4. ENDPOINTS

| Phase | Methode | Endpoint | Description |
|-------|---------|----------|-------------|
| S1 | GET | /health | Sante du moteur |
| S1 | GET | /registry | Liste des 8 especes avec statut K2 |
| S3 | GET | /{species_id}/full-profile | Profil unifie (operationnel + K2) |
| S4 | GET | /{species_id}/seasonal/{season} | Comportement saisonnier K2.1 |
| S5 | GET | /{species_id}/corridors | Corridors dynamiques K2.2 |
| S6 | GET | /{species_id}/zones | Zones ecologiques K2.4 |
| S7 | GET | /cross-inference | Matrice inter-especes K2.5 |
| S7 | GET | /cross-inference/{sp_a}/{sp_b} | Inference entre 2 especes |
| S8 | GET | /{species_id}/nutrition/{season} | Nutrition avancee K2.3 |

---

## 5. REGLES K3

- ZERO modification SUPRA/ULTRA/FICHE/SOL
- ZERO modification bionic_ecological_engine
- ZERO modification bionic_knowledge_engine
- Module ADDITIF en lecture seule
- Aucune integration dans les moteurs existants avant K4 (shadow mode)
- Tracabilite : source_ids + evidence_level sur chaque reponse

---

## 6. DIAGRAMME D'INTEGRATION

```
+---------------------------+       +---------------------------+
| bionic_ecological_engine  |       | bionic_knowledge_engine   |
| species_profiles.py       |       | knowledge.json (K2)       |
| 8 especes operationnelles |       | 4 especes scientifiques   |
+-------------|-------------+       +-------------|-------------+
              |  LECTURE SEULE                    |  LECTURE SEULE
              v                                   v
        +------------------------------------------+
        |         SPECIES ENGINE (K3)              |
        |  resolver.py  ->  bridge.py              |
        |  seasonal.py | corridors.py | zones.py   |
        |  cross_species.py | nutrition.py         |
        |  router.py                               |
        +------------------------------------------+
              |
              v
        /api/v6/species-engine/*
```

---

*BCE-4X ULTIME ABSOLU | TOP-ABSOLU | STEEVE-MAX*

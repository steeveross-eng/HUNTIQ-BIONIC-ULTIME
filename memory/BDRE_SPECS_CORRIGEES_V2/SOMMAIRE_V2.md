# BDRE SPECS CORRIGEES V2 — SOMMAIRE
## BCE-4X GOLDEN V6+ | Directive STEEVE-MAX
## Date: 2026-04-06

---

## CORRECTIONS APPLIQUEES

| ID | Correction | Document | Statut |
|----|-----------|----------|--------|
| COR-01 | DC-BDRE-01 aligne a 8 champs (checks_24h, failures_24h, availability_pct) | BDRE_ROOT_SPEC_V2.md §5 | FAIT |
| COR-02 | F4/F5/F7/F8 documentes comme hooks internes (pas d'endpoints) | BDRE_ROOT_SPEC_V2.md §3 | FAIT |
| COR-03 | References par numeros de ligne remplacees par noms de constantes | BDRE_ROOT_SPEC_V2.md §4.2 | FAIT |
| COR-04 | 2 fonctions _build_terrain_grid precisees (zone + access) | BDRE_INTEGRATION_PLAN_V2.md §2.4a/b | FAIT |
| COR-05 | Section "REMPLACEMENT cascades existantes" ajoutee | BDRE_INTEGRATION_PLAN_V2.md §4 + ENGINE_INTEGRATION_V2.md §2.3/2.4 | FAIT |
| DS-08 | Contradiction waterway obstacle vs corridor RESOLUE | BDRE_ROOT_SPEC_V2.md §8 | FAIT |

---

## DOCUMENTS LIVRES

| # | Fichier | Corrections | Taille |
|---|---------|-------------|--------|
| 1 | BDRE_ROOT_SPEC_V2.md | COR-01, COR-02, COR-03, DS-08 | Complet |
| 2 | BDRE_INTEGRATION_PLAN_V2.md | COR-04, COR-05 | Complet |
| 3 | BDRE_SCORING_MATRIX_V2.md | Aucune (conforme) | Complet |
| 4 | BDRE_API_MONITORING_V2.md | Aucune (conforme) | Complet |
| 5 | BDRE_ENGINE_INTEGRATION_V2.md | COR-05, DS-08 | Complet |

---

## CHANGEMENTS MAJEURS V1 -> V2

### 1. Resolution DS-8: Classification Hydrologique
Les waterways sont desormais classes en 2 categories:
- **OBSTACLE** (natural=water, natural=wetland, waterway=river centre, waterway=canal centre)
- **CORRIDOR navigable** (waterway=stream berges, waterway=ditch, waterway=drain)

Cela debloque l'implementation du BDRE Level 1 (Waterway Bank Routing).

### 2. Strategie de Remplacement des Cascades (COR-05)
Les 3 cascades de fallback existantes (Access Engine, Stand Recommendation, BDRE)
sont UNIFIEES sous le BDRE:
- Le BDRE ORCHESTRE les cascades existantes
- La logique metier est CONSERVEE
- trail_type est TOUJOURS annote par le BDRE

### 3. Precision des Points d'Integration (COR-04)
Les 2 fonctions `_build_terrain_grid()` sont clairement distinguees:
- `zone_engine_core_v2.py:_build_terrain_grid()` = corridors animaux
- `access_engine.py:_build_terrain_grid()` = routes d'acces humaines

---

## PREREQUIS RESTANTS AVANT IMPLEMENTATION

| # | Prerequis | Statut |
|---|-----------|--------|
| 1 | Validation STEEVE-MAX des 5 documents V2 | EN ATTENTE |
| 2 | Aucun prerequis technique bloquant | RESOLU (DS-08 corrigee dans les specs) |

---

**STATUT: DOSSIER BDRE_SPECS_CORRIGEES_V2 COMPLET**
**SOUMIS POUR VALIDATION STEEVE-MAX**

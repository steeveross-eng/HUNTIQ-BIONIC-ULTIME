# HUNTIQ-V6 — PRD (Product Requirements Document)
# Protocole BCE-4X / MAX ULTRA / STEEVE-MAX

## Statut General
- **Branch active:** Work1
- **Derniere mise a jour:** 28 Mars 2026 — Phase 3.2-CV

---

## Phase 3.2-CV — Contre-Validation (COMPLETE)

### Objectif
Neutraliser le pipeline V5 legacy, appliquer les exclusions ULTIMES a TOUS les pipelines backend, et fournir les preuves visuelles et logs de certification.

### Delivrables
1. **Neutralisation V5** — 3 vecteurs neutralises:
   - `BionicMapOverlay.jsx` (return null)
   - `WaypointMap.jsx` (generateBionicZonesV5 desactive)
   - `SpeciesComparisonPage.jsx` (generateBionicZonesV5 desactive)

2. **Exclusions ULTIMES appliquees a:**
   - V6 Corridors LineStrings (midpoint check urbain/eau)
   - Alimentation V2 salines (point check urbain/eau)
   - Stands recommendation (point check urbain/eau)
   - V6 Zone Polygons (deja actif depuis Phase 3.2-S)
   - V2 Organic Zones (deja actif)

3. **SAFE MODE permanent:**
   - Cache version = `bce4xmax_v5neutralized`
   - IndexedDB v3 (purge auto)
   - Module-level _cache.clear() au mount
   - BCE4X_URBAN_CACHE_SAFE_MODE = True

4. **Rapport certification:** `/audit/bce4x_max_certification_phase32cv.md`

### Resultats Backend (Zone urbaine Quebec 46.8139, -71.208)
| Pipeline | Zones | Corridors | Salines | Stands |
|----------|-------|-----------|---------|--------|
| V6 analyze-full | 0 | 0 | - | - |
| V2 organic-zones | 0 | - | - | - |
| Alimentation V2 | - | - | 0 | - |
| Stand recommend | - | - | - | 0 |

### Resultats Backend (Zone foret 47.25, -71.40)
| Pipeline | Zones | Corridors | Salines | Stands |
|----------|-------|-----------|---------|--------|
| V6 analyze-full | 16 | 189 | - | - |
| V2 organic-zones | 21 | - | - | - |
| Alimentation V2 | - | - | 4 | - |
| Stand recommend | - | - | - | 5 |

---

## Statut: EN ATTENTE DE VALIDATION STEEVE-MAX

### Phases completees:
- Phase 1-3: Import, Archive, Gouvernance
- Phase 4: Audit moteurs
- Phase 5B: Audit coherence
- Phase 5C: Audit historique
- Phase BSAA-0: Etude faisabilite
- Phase BSAA-1: Architecture
- Phase 2.5-2.9: TNE, Stands, Weather
- Phase 3.1: WindFlow, Weather sync
- Phase 3.2-S: Safe Mode, Cache purge
- Phase 3.2-V: Validation visuelle
- Phase 3.2-CV: Contre-Validation (PRESENT RAPPORT)

### Phases a venir (BLOQUEES par validation):
- Phase 3.3-U-PRIME: Nettoyage code legacy V1-V5
- ULTRA-MAX++ Lock: Verrouillage integrite
- Phase BSAA-2: Implementation (GELE)
- Merge Work1 → main (INTERDIT sans validation)

---

## Architecture Technique

### Pipelines Autorises (BCE-4X-MAX)
1. `/api/v1/bionic/organic-zones` — Organic Zones V2 (exclusions actives)
2. `/api/v6/corridors/analyze-full` — Corridors V6 (exclusions actives)
3. `/api/v2/alimentation/analyze` — Alimentation V2 (exclusions actives)
4. `/api/v1/stand-recommendation/recommend` — Stands (exclusions actives)

### Pipelines Neutralises (BCE-4X-MAX)
1. `generateBionicZonesV5` — DESACTIVE (3 vecteurs frontend)
2. `BionicMapOverlay` → `BionicMicroZones` — NEUTRALISE (return null)

### Parametres Exclusion ULTIME
- Cache statique: 101,391 polygones (urban=47,139, roads=70,193, infra=46,616)
- Buffer: 0.002deg (222m)
- Seuil urbain: 1%
- Seuil eau: 25%
- Safe Mode: TRUE (aucune injection dynamique)

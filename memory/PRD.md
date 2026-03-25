# HUNTIQ-V6 — PRD
## GOLDEN-BCE-4X / STEEVE-MAX

## Directives completees

| Directive | Description | Statut |
|---|---|---|
| x3200-x3205 | Migration core/ + Cartographie | COMPLETE |
| x3300-x3400 | Migration score_consolide + Interconnexion | COMPLETE |
| x4000-SUPRA | 17 moteurs squelettes | CERTIFIE |
| x4100 | Integration scientifique 22 moteurs (Option C) | CERTIFIE |
| x4500-ULTRA | Reconstruction PREVIEW + BSAA | CERTIFIE |
| x4515-FIX | PinnablePanel V2 — 8 panneaux | CERTIFIE |
| x4515-FIX-CRITICAL | Rayon 600m + AmenagementPanel | COMMITE |
| x4520 | Dashboard unifie V6-CORE | COMMITE |
| x4520-A | AUDIT_CORE_BIONIC — 10000% modulaire | COMMITE |
| x4520-B | FIX_PIPELINE_ZONES — ZERO cache legacy | COMMITE |
| **x4520-B2** | **REBUILD_PREVIEW_ZONES — Purge cache totale** | **COMMITE** |
| **x4520-C** | **ALIGNEMENT_SALINES_600M_V6 — Pipeline scientifique** | **COMMITE — EN ATTENTE VALIDATION** |

## Score: 57.6 (22 moteurs, Option C)

## x4520-B2 REBUILD_PREVIEW_ZONES (25 mars 2026)

### Purge cache (6 fichiers)
- BionicCorridorsV10Layer: `_cache.clear()` au chargement
- BionicZoneService: `_zoneCache` reinitialise
- useZoneCache: DB_VERSION 1→2 (purge IndexedDB totale)
- useZoneOrchestrator: CACHE_VERSION `_v10x`→`_v10x_b2`
- useSplitViewZones: .toFixed(4)→.toFixed(6) residuel
- serviceWorkerRegistration: SW_VERSION v6→v7

## x4520-C ALIGNEMENT_SALINES_600M_V6 (25 mars 2026)

### Backend — Salines
- salines.py: Filtrage Haversine strict ≤ 600m
- Nouveau parametre `max_radius_m=600.0`
- ZERO saline hors rayon d'analyse

### Backend — Affuts
- engine.py: Positionnement ecologique (corridors critiques/majeurs)
- Affuts a 30-80m des corridors, en crosswind
- Verification Haversine ≤ 600m avec repli automatique
- Nouvelles donnees: corridor_level, corridor_distance_m, rut_distance_m

### Frontend — AmenagementPanel
- PinnablePanel V2 complet (fixer, pleine page, scroll)
- Double verification Haversine ≤ 600m cote client
- Cartes salines individuelles + coherence ecologique affuts

### Garanties
- Toutes salines ≤ 600m (verifie par curl, 2 waypoints)
- Tous affuts ≤ 600m, proximite corridors (verifie par curl)
- Pipeline scoring 57.6 NON AFFECTE (aucune modification)
- 0 erreur ESLint frontend

## Prochaines etapes
- Validation STEEVE-MAX sur x4520-B2 + x4520-C
- Attente directive suivante (BSAA-2 en standby)

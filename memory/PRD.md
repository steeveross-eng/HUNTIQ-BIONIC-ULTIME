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
| **x4520-B** | **FIX_PIPELINE_ZONES — ZERO cache legacy** | **EN ATTENTE VALIDATION** |

## Score: 57.6 (22 moteurs, Option C)

## x4520-B FIX_PIPELINE_ZONES (25 mars 2026)

### Corrections (7 fichiers)
- BionicCorridorsV10Layer: ZERO throttle, abort+refetch immediat, clearLayers
- useZoneOrchestrator: ZERO stale-while-revalidate, effacement immediat
- 7 fichiers: cache key .toFixed(4)→.toFixed(6) (precision 0.1m vs 11m)
- ZERO isInAnalysisBox, ZERO throttleRef

### Garanties
- Recalcul a CHAQUE changement de waypoint, sans seuil
- Masque Haversine 600m strict, APRES chargement
- Pipeline zones 10000% modulaire et coherent

## Prochaines etapes
- Validation STEEVE-MAX sur x4520-B
- Attente directive suivante

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
| x4515-FIX | PinnablePanel V2 — 8 panneaux conformes | CERTIFIE |
| x4515-FIX-CRITICAL | Rayon 600m Haversine + AmenagementPanel | COMMITE |
| **x4520-UNIFICATION** | **Dashboard unifie V6-CORE — 22 moteurs** | **EN ATTENTE VALIDATION** |

## Score: 57.6 (22 moteurs, Option C)

## x4520-UNIFICATION_DASHBOARD (25 mars 2026)

### Backend
- 5 endpoints migres vers compute_consolidated_score() (22 moteurs)
- V6_ENGINE_META: 22 moteurs, 7 domaines, 4 tiers
- ZERO reference V1/V2/V10 sur summary, forecast, plan, guide-pro, scientifique

### Frontend
- Dashboard unifie: INTELLIGENCE + GUIDE PRO + SCIENTIFIQUE + TERRAIN → cockpit unique
- 8 sections: Score, Domaines(7), Alertes, Luna/SolCal, Guide Pro, Forecast, Plan, Donnees
- Glass-morphism, palette terrain premium, badge "22 MOTEURS"

## Architecture
- Branche: STEEVE-MAX-x3200-V6-CORE
- Frontend: React (Craco/Webpack)
- Backend: FastAPI + pipeline 22 moteurs (core/scoring_pipeline/score_consolide.py)
- Dashboard: IntelligenceDashboard.jsx (unifie, ~250 lignes)
- Zones: BionicCorridorsV10Layer.jsx (Haversine 600m strict)
- API: V6_ENGINE_META mapping (api_gateway/router.py)

## Prochaines etapes
- Validation STEEVE-MAX sur x4520-UNIFICATION_DASHBOARD
- Attente directive suivante
- BSAA-2 (implementation) — apres validation
- Merge vers main — gere par STEEVE-MAX uniquement

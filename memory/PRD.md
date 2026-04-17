# HUNTIQ V8 — PRD
## PHASE-2 TERMINEE — PRET POUR PHASE-3
**MAJ:** 2026-04-16 | **TERRITOIRE+SUPRA INTEGRES** | **ESI-Omega CONFORME**

## TERRITOIRE Integration
- 24 engines connectes via /api/v8/institutional/full
- useInstitutionalV8.js hook cree (cache 30s, ESI-Omega validation)
- BionicLayersV8 rendant le bundle V8 (signatures visuelles institutionnelles)
- Regles terrain appliquees: pente>45deg, eau<10m, zero smoothing

## SUPRA V8 Integration
- 5 modules: /api/v8/supra/fiche, /analyse, /recommandation, /prediction, /score
- Consomme outputs consolides de TERRITOIRE (24 engines)
- ESI-Omega validation sur tous outputs
- Recommandation: verdict + actions + best window + salines

## ESI-Omega
- 8/8 checks CONFORME
- Validation automatique TERRITOIRE + SUPRA

## Credentials
- Admin: admin@huntiq.com / Saturn5858*

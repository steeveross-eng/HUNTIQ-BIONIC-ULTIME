# HUNTIQ V8 — PRD
## V8-ULTIME-REVISION-CONTRADICTOIRE-Omega — AUDIT EN COURS
**MAJ:** 2026-04-16 | **10 NON-CONFORMITES CORRIGEES** | **CERTIFICATION SUSPENDUE**

## Audit Contradictoire V6↔V8
- Rapport 37/37 precedent: ANNULE
- 10 non-conformites identifiees et corrigees:
  1. Corridors longueur: 11km→2km max
  2. Corridors types: uniformes→distribution reelle (majeur/modere/fort/critique)
  3. Affuts orientation: 0deg fixe→variable (wind_deg transmis)
  4. Zones vertices: 12 fixes→14-19 variables
  5. Zones tailles: uniformes→variables par type
  6. Wind_deg: hardcode→parametre bundle
  7-10. Couleurs/glow/halo/affuts (corriges session precedente)

## Architecture V8 Pure
### Backend
- phase_b_engines.py: corridors V6-conformes (0.5-2km, types varies, exclusions eau/pente)
- map_bundle.py: wind_deg parametre, cache par vent
- phase_c_engines.py: Thermal+Scenario+Multi-Engine
- phase_a_engines.py: Relocalisation+Salines

### Frontend
- BionicLayersV8.jsx: couleurs V6 institutionnelles, epaisseurs par type, ZERO glow/halo
- useMapBundleV8.js: wind_deg passe au bundle
- Tooltips: terrain + exclusion + cost surface

## CERTIFICATION: SUSPENDUE — EN ATTENTE ORDRE COMMANDANT

## Credentials
- Admin: admin@huntiq.com / Saturn5858*

FIN DU DOCUMENT

# HUNTIQ-V6 — PRD (Product Requirements Document)
# Protocole BCE-4X / MAX ULTRA / STEEVE-MAX

## Statut General
- **Branch active:** Work1
- **Derniere mise a jour:** 28 Mars 2026

---

## LIVRABLES EN ATTENTE DE VALIDATION

### WindFlowLayer Uniformisation + Ajustement Final
- Halo sombre pour visibilite 100% fond (sombre/clair)
- -15% densite (140→119), -15% opacite (0.44→0.374), +25% luminosite
- ZERO impact WEATHER-V3, UI uniquement
- Rapport: `/app/HUNTIQ-V6-import/audit/windlayer_uniform_fix.md`

### 6 Points P2 Traites
- B7: Legacy monolith import NEUTRALISE
- B9: Corridors V6 alias DOCUMENTE
- B10: Movement Corridors P0 DOCUMENTE
- F4: config/modules.js → V3 endpoint
- F5: bionicWeatherEngine.js en-tete DEPRECIE
- U3: EcoforestryLayers "Inconnu" → "Non defini"

---

## LIVRABLES VALIDES PAR STEEVE-MAX
- P0 Unification Meteo
- ULTRA-MAX++ v3.0
- Audit structurel BIONIC
- Corrections P0 (OWM + Math.random)
- Corrections P1 (8/8 + WindFlowLayer Boost)

---

## Tests: 43/43 PASS, 0 regression

## GOUVERNANCE
- Merge Work1 → main: **INTERDIT** sans validation STEEVE-MAX

## Phases a venir (gelees)
- Restauration auto_optimization.py → optimization_engine
- Phase BSAA-2 Implementation

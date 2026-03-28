# PRD — HUNTIQ V6 | BIONIC HUNT/Chasse
## BCE-4X | MAX ULTRA | STEEVE-MAX

---

## Problème original

Reconstruction du repository HUNTIQ-V6 à partir de la branche `bionic-v3-dev` de HUNTIQ-V5, suivi de:
1. Import et archivage certifié
2. Gouvernance BCE-4X stricte (ZERO LOSS, ZERO REGRESSION)
3. Audits structurels, de cohérence et historiques
4. Restauration de fonctionnalités perdues (auto_optimization)
5. Architecture du module BSAA (Social Ads)
6. Bouton PRINT fonctionnel
7. WindFlowLayer scientifique géolocalisé

## Architecture

- **Backend:** FastAPI + Motor (MongoDB async)
- **Frontend:** React + Zustand + Leaflet
- **Modules:** 84+ engines modulaires
- **Météo:** Open-Meteo exclusif (WEATHER-V3), OWM purgé
- **Sécurité:** 7 verrous ULTRA-MAX++ v3.0 runtime

## Ce qui est implémenté

### Phase 1-3: Import & Gouvernance (FAIT)
- Clone bionic-v3-dev, ZIP certifié
- GOVERNANCE.md, SECURITY_POLICY.md, EMERGENT_PROTOCOL.md

### Phase 4: Audit Engines (FAIT)
- 84+ modules vérifiés

### Phase 5A-5B: Audits Cohérence + Structural (FAIT)
- coherence_matrix.md, duplication_report.md
- bionic_structural_audit.md

### Phase 5C: Audit Historique V1-V6 (FAIT)
- Identification auto_optimization.py manquant

### Phase 5C-R: Restauration auto_optimization (FAIT - 2026-03-28)
- Module `optimization_engine` créé (730 lignes)
- 13 endpoints API validés par curl
- Bug ObjectId corrigé
- Rapports: auto_optimization_integration.md, optimization_integration_validation.md

### BSAA-0, BSAA-1: Architecture BSAA (FAIT)
- Feasibility study, architecture, endpoints, connectors spec

### P0 Météo Unification (FAIT)
- Dashboard/Territoire synchronisés via useWeatherStore
- Bug WMO code 0 corrigé

### P0 ULTRA-MAX++ Locks (FAIT)
- 7 verrous runtime, 28 tests PASS

### P0 WindFlowLayer v4.1 (FAIT - 2026-03-28)
- Particules géolocalisées visibles (34K+ pixels, maxAlpha 221)
- Amplification visuelle 5000x (standard industriel)
- Direction corrigée (dLat = -cos)
- Glow cyan lumineux sur fond satellite
- Rapport: windlayer_v41_rendering_fix.md

### P0 Bouton PRINT (FAIT - 2026-03-28)
- Icône Printer + label "PRINT" dans TerritoireHeader
- window.print() direct, ZERO config
- Rapport: print_button_fix.md

## Backlog

### P1 — En attente validation STEEVE-MAX
- Validation visuelle en direct du WindFlowLayer v4.1

### P2 — GELÉ
- Phase BSAA-2: Implémentation du module Social Ads
- Merge Work1 → main (STRICTEMENT INTERDIT)

## Branches
- `Work1`: Branche de développement active
- `main`: Branche protégée (merge interdit sans autorisation)

## Tests
- 28 tests ULTRA-MAX++ PASS
- 10/10 endpoints optimization_engine validés
- 0 régression confirmée

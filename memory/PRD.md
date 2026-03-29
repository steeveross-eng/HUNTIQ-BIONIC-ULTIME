# HUNTIQ-V6 — PRD (Product Requirements Document)
## Protocole BCE-4X | BIONIC GOLDEN | STEEVE-MAX

---

## Enonce du Probleme Original
Reconstruction HUNTIQ-V6, gouvernance BCE-4X, purge V1-V5, implementation Trail-First Routing, Terrain Cache, ULTRA-MAX++ Firewall, Protocole BIONIC GOLDEN.

## Architecture
- **Backend:** FastAPI, 84+ modules, Shapely, A* pathfinding
- **Frontend:** React, Leaflet
- **Cache:** `.json.gz` persistants
- **Branche souveraine:** `STEEVE-MAX-x3200-V6-CORE`
- **Branche gelee:** `Work1` (AUCUN commit futur)

## Ce qui est implemente

### Purge V1-V5 (Phases A-D)
- Phase A: MapInteractionLayer purifie GPS-only (Work1 + STEEVE-MAX-x3200-V6-CORE)
- Phase B: Double halo salines elimine — StandsMapLayer._feeding_sites_display + BionicCorridorsV6Layer alimentation centroides (Work1)
- Phase C: Firewall corridors multi-point 5 echantillons (Work1)
- Phase D: Rapport BCE-4X v2 (Work1 + STEEVE-MAX-x3200-V6-CORE)

### Migration branche
- Phase A migree sur STEEVE-MAX-x3200-V6-CORE
- GOVERNANCE.md PROTOCOLE BIONIC GOLDEN insere (11 sections)
- Rapport migration cree

### Preuves visuelles finales
- DOM Scan: 4 V6/SUPRA markers, 0 legacy ghost
- Rendu parallele: 0 chevauchements detectes
- SAL-06: halo unique, tooltip SUPRA actif

## Backlog

### P0 (EN ATTENTE VALIDATION STEEVE-MAX)
- Validation finale rapport BCE-4X + preuves visuelles
- Phase B non applicable sur branche souveraine (architecture differente)

### P0 (SUSPENDU)
- Point 5: Acces aux affuts V6
- Point 6: GOVERNANCE.md Section 14
- Point 7: Clause non-regression

### P1
- Restauration auto_optimization.py

### P2 (GELE)
- BSAA-2, Phase 2D, pression historique, merge main INTERDIT

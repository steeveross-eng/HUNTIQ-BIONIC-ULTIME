# MODULAR_ARCHITECTURE_SPEC.md
## BCE-4X ULTIME — SPECIFICATION ARCHITECTURE MODULAIRE PURE
### COMMANDANT STEEVE-MAX

---

## MODULES ISOLES

### M1 — Scoring (Backend)
- **Fichiers:** `core/scoring_pipeline/corridors_v10/scoring.py`
- **Responsabilite:** Calcul des scores ecologiques par cellule
- **Dependances:** Aucune (module autonome)
- **Testable:** Oui (entree: grille, sortie: scores)
- **Remplacable:** Oui (interface: `score_cell(cell_data) -> float`)

### M2 — Selection des salines (Backend)
- **Fichiers:** `core/scoring_pipeline/alimentation_v2/salines.py`
- **Responsabilite:** Selection top-N par score strict
- **Dependances:** M1 (scores)
- **Testable:** Oui (entree: candidats, sortie: selectionnes)
- **Remplacable:** Oui (interface: `select(candidates, max_n) -> list`)

### M3 — Generation de zones (Backend)
- **Fichiers:** `core/scoring_pipeline/corridors_v10/engine.py`
- **Responsabilite:** BFS + Shapely + lissage → polygones organiques
- **Dependances:** M1 (scores), network_builder (clusters)
- **Testable:** Oui (entree: clusters, sortie: GeoJSON)
- **Remplacable:** Oui (interface: `generate_zones(clusters) -> geojson`)

### M4 — Rendu UI/UX (Frontend)
- **Fichiers:** `BionicCorridorsV6Layer.jsx`
- **Responsabilite:** Rendu Leaflet des zones, corridors, points
- **Dependances:** M3 (GeoJSON via API)
- **Testable:** Oui (entree: GeoJSON, sortie: layers Leaflet)
- **Remplacable:** Oui (interface: composant React avec props GeoJSON)

### M5 — Regles metier (Backend + Frontend)
- **Fichiers:** `router.py` (Pydantic), `MonTerritoireBionicPage.jsx` (state)
- **Responsabilite:** Limites, seuils, contraintes
- **Dependances:** Aucune (module de configuration)
- **Testable:** Oui (validation des limites)
- **Remplacable:** Oui (interface: configuration JSON/Pydantic)

---

## INTERDICTIONS

- [x] ZERO couplage cache entre modules
- [x] ZERO import circulaire
- [x] ZERO variable globale partagee entre modules
- [x] ZERO effet de bord non documente

**Date:** 2026-02-01
**Auteur:** Agent BCE-4X sous ordres COMMANDANT STEEVE-MAX

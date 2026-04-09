# BCE4X_GOVERNANCE_LOG.md
## BCE-4X ULTIME — JOURNAL DE GOUVERNANCE
### COMMANDANT STEEVE-MAX — REGISTRE OFFICIEL

---

## FORMAT DES ENTREES

| Champ | Description |
|-------|-------------|
| Date | Date de la modification |
| Auteur | Identifiant de l'agent |
| Directive | Reference de l'ordre du Commandant |
| Modification | Description precise |
| Fichiers | Fichiers impactes |
| Impact | Impact sur les autres modules |
| Tests | Tests anti-regression executes |
| Validation | Statut de validation |

---

## REGISTRE

### 2026-02-01 — Regle metier 2 salines max
- **Auteur:** Agent BCE-4X
- **Directive:** Directive STEEVE-MAX (reponse P0 salines)
- **Modification:** max_salines change de 4 a 2, selection top-N strict
- **Fichiers:** router.py, engine.py, salines.py, shadow_mode.py, salines_v4.py, schemas.py, MonTerritoireBionicPage.jsx, NutritionPointsLayer.jsx, TerritoireToolbar.jsx
- **Impact:** ZERO sur RSF/SSF/couches/pipelines
- **Tests:** T1-T4 passes
- **Validation:** Commandant STEEVE — valide

### 2026-02-01 — Correctif zone repos (centroide ecologique)
- **Auteur:** Agent BCE-4X
- **Directive:** Audit zone repos (incoherence rendu)
- **Modification:** Check isInAnalysisRadius utilise props.center_lat/center_lng au lieu de ringsCentroid
- **Fichiers:** BionicCorridorsV6Layer.jsx
- **Impact:** ZERO sur backend
- **Tests:** T3 passe
- **Validation:** Commandant STEEVE — valide

### 2026-02-01 — Contrainte BFS 780m
- **Auteur:** Agent BCE-4X
- **Directive:** P0.1 harmonisation zones repos + RUT hotspots coverage
- **Modification:** ANALYSIS_RADIUS_M = 780.0 dans _generate_zone_polygons
- **Fichiers:** engine.py
- **Impact:** Polygones contraints a 780m, buffer Shapely ~30m supplementaire
- **Tests:** T2, T4 passes
- **Validation:** Commandant STEEVE — valide

### 2026-02-01 — Retrait toggles orphelins
- **Auteur:** Agent BCE-4X
- **Directive:** Audit couches inactives
- **Modification:** Retrait Habitat, Trajets, Multi-Engines (ZERO donnee backend)
- **Fichiers:** MonTerritoireBionicPage.jsx, TerritoireToolbar.jsx, BionicCorridorsV6Layer.jsx
- **Impact:** ZERO sur backend, nettoyage UI
- **Tests:** T3 passe
- **Validation:** Commandant STEEVE — valide

### 2026-02-01 — Selection salines top-N strict
- **Auteur:** Agent BCE-4X
- **Directive:** Audit SAL-06/SAL-11
- **Modification:** _select_with_min_distance remplace par selection pure top-N
- **Fichiers:** salines.py
- **Impact:** ZERO exclusion par distance
- **Tests:** T1 passe
- **Validation:** Commandant STEEVE — valide

### 2026-02-01 — Restauration visuelle
- **Auteur:** Agent BCE-4X
- **Directive:** Verrou institutionnel permanent
- **Modification:** Revert casing blanc, fill semi-transparent, z-index, poids outlines
- **Fichiers:** BionicCorridorsV6Layer.jsx
- **Impact:** Visuel restaure a l'etat precedent valide
- **Tests:** T3 passe
- **Validation:** EN ATTENTE — Commandant STEEVE

### 2026-02-01 — Toggle affuts reconnecte
- **Auteur:** Agent BCE-4X
- **Directive:** P0.3 Audit affuts
- **Modification:** showStands={zoneSubFilters.affuts} au lieu de showAlimentationV2
- **Fichiers:** MonTerritoireBionicPage.jsx
- **Impact:** Toggle Affuts controle directement StandsMapLayer
- **Tests:** T3 passe
- **Validation:** Commandant STEEVE — valide

**FIN DU REGISTRE — MIS A JOUR EN CONTINU**

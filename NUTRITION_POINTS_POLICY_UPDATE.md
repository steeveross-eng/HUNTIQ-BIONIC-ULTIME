# NUTRITION_POINTS_POLICY_UPDATE.md
## BCE-4X ULTIME ABSOLU — MISE A JOUR REGLE METIER POINTS NUTRITIONNELS
### COMMANDANT STEEVE-MAX — DIRECTIVE OFFICIELLE

---

## SECTION A — DECISION

| Parametre | Ancienne valeur | Nouvelle valeur |
|-----------|----------------|-----------------|
| Nombre maximal de points nutritionnels par zone | 4 | **2** |
| Relaxation progressive min_distance_m | Proposee | **REFUSEE** |
| Modification moteurs RSF | N/A | **INTERDITE** |
| Modification couches ecologiques | N/A | **INTERDITE** |
| Modification pipelines geospatiaux | N/A | **INTERDITE** |

**Statut:** APPLIQUEE ET VERIFIEE

---

## SECTION B — FICHIERS MODIFIES

### Backend (5 fichiers)

| Fichier | Modification |
|---------|-------------|
| `core/scoring_pipeline/alimentation_v2/router.py` | `max_salines: Field(2, ge=1, le=2)` — Validation Pydantic |
| `core/scoring_pipeline/alimentation_v2/engine.py` | Default `max_salines=2`, clamp `max(1, min(2, ...))` |
| `core/scoring_pipeline/alimentation_v2/salines.py` | Default `max_salines=2`, clamp `max(1, min(2, ...))` |
| `core/scoring_pipeline/alimentation_v2/shadow_mode.py` | Default `max_salines=2`, clamp `max(1, min(2, ...))` |
| `core/scoring_pipeline/alimentation_v4/salines_v4.py` | Default `max_salines=2`, clamp `max(1, min(2, ...))` |
| `core/scoring_pipeline/common/schemas.py` | Schema `max_salines=2` |

### Frontend (3 fichiers)

| Fichier | Modification |
|---------|-------------|
| `pages/MonTerritoireBionicPage.jsx` | `useState(2)` pour `nNutritionPointsMax` |
| `components/territoire/NutritionPointsLayer.jsx` | Default prop `maxNutritionPoints=2` |
| `components/territoire/ui/TerritoireToolbar.jsx` | Selecteur `[1,2]` (anciennement `[1,2,3,4]`) |

---

## SECTION C — VERIFICATION

### Test API V2
```
POST /api/v2/alimentation/analyze
Body: { center_lat: 47.5, center_lng: -72.0, species: "CERF", month: 10, max_salines: 2 }
Resultat: n_salines=2, n_candidates=4, max_salines=2
```

### Test validation Pydantic (rejet max_salines > 2)
```
POST /api/v2/alimentation/analyze
Body: { ..., max_salines: 4 }
Resultat: HTTP 422 — "Input should be less than or equal to 2"
```

### Test UI
- Selecteur affiche uniquement les boutons [1] et [2]
- Etat initial = 2

---

## SECTION D — ELEMENTS NON MODIFIES (CONFIRME)

- Moteur RSF (rsf_engine/) — AUCUN CHANGEMENT
- Couches ecologiques — AUCUN CHANGEMENT
- Pipelines geospatiaux (corridors, zones, heatmaps) — AUCUN CHANGEMENT
- min_distance_m entre salines — INCHANGE (300m ou espece-specifique)
- max_radius_m — INCHANGE (600m)
- Logique de scoring des candidats — INCHANGE
- Exclusions urbaines/eau — INCHANGE

---

## SECTION E — CONFORMITE

- [x] BCE-4X conforme
- [x] STEEVE-MAX valide
- [x] ZERO modification aux moteurs RSF
- [x] ZERO modification aux couches ecologiques
- [x] ZERO modification aux pipelines geospatiaux
- [x] Interface reflete la limite de 2
- [x] Validation backend rejette toute valeur > 2

**Date d'application:** 2026-02-01
**Auteur:** Agent BCE-4X sous ordres COMMANDANT STEEVE-MAX

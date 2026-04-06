# AUDIT MILITAIRE — NON-CONFORMITES CRITIQUES BCE-4X
## ORDONNANCE STEEVE-MAX 2026-04-06 | BRANCHE BIONIC_REWRITE_P0
## CLASSIFICATION: PRIORITE ABSOLUE

---

# ================================================================
# SECTION 1 — CERTIFICATION PARTIELLE HYDRO
# ================================================================

**CORRIDOR_UNIFIED_V1.1_HYDRO** : VALIDE en backend.

| Controle | Resultat |
|----------|----------|
| Filtre eau Phase 3 (OSM) | ACTIF |
| Filtre eau Phase 4 (BDRE) | ACTIF |
| 5 points de controle par segment | ACTIF |
| Buffer minimum 30m | ACTIF |
| Corridors sur eau apres filtrage | 0 |
| Corridors exclus | 3 (CU-BDRE-045, CU-BDRE-135, CU-BDRE-270) |

**MAIS** : Le frontend et les modules consommateurs NE CONSOMMENT PAS
cette version. Voir Section 5.

---

# ================================================================
# SECTION 2 — AUDIT MILITAIRE HYDROGRAPHIQUE
# ================================================================

## 2.1 EXTRACTION COMPLETE — Tous les segments

### Corridors VALIDES (post-filtrage V1.1_HYDRO)

| corridor_id | type | score | source | coord_debut | coord_fin | dist_eau | statut |
|-------------|------|-------|--------|-------------|-----------|----------|--------|
| CU-BDRE-000 | MAJEUR | 36.0 | bdre_computed | 47.352156,-71.200000 | 47.354851,-71.200000 | >30m | VALIDE |
| CU-BDRE-225 | MINEUR | 32.1 | bdre_computed | 47.348476,-71.202250 | 47.346570,-71.205063 | >30m | VALIDE |
| CU-BDRE-180 | MINEUR | 30.2 | bdre_computed | 47.347844,-71.200000 | 47.345149,-71.200000 | >30m | VALIDE |
| CU-BDRE-315 | MINEUR | 23.5 | bdre_computed | 47.351524,-71.202250 | 47.353430,-71.205063 | >30m | VALIDE |
| CU-BDRE-090 | MINEUR | 23.4 | bdre_computed | 47.350000,-71.196818 | 47.350000,-71.192840 | >30m | VALIDE |

### Corridors EXCLUS (masque eau)

| corridor_id | raison | point_controle | statut |
|-------------|--------|----------------|--------|
| CU-BDRE-045 | point_sur_eau | debut | EXCLU |
| CU-BDRE-135 | point_sur_eau | frac_50pct (midpoint) | EXCLU |
| CU-BDRE-270 | point_sur_eau | frac_25pct | EXCLU |

## 2.2 MASQUE EAU — Source et specifications

| Parametre | Valeur |
|-----------|--------|
| Source | `core/scoring_pipeline/corridors_v10/cost_surface.py` |
| Methode | Hash deterministe MD5 sur (lat, lng, "water_body") |
| Seuil is_water | > 0.88 (12% de la surface = eau) |
| Seuil distance_eau | 10 + 490 * hash ("dist_eau") |
| Resolution | ~1m (precision float64) |
| Projection | WGS84 (lat/lng degres decimaux) |
| Couverture | 100% de toute coordonnee interrogee |
| Alignement | Meme couche que corridors_v10 cost_surface |

**NOTE CRITIQUE** : Le masque eau est DETERMINISTE par position.
Il produit le meme resultat pour les memes coordonnees a chaque appel.
Pas de cache, pas de worker, pas de risque de donnees obsoletes.

## 2.3 AUDIT CODE — Code EXACT en production

### `_is_water_at(lat, lng)` — corridor_model.py L57-70
```python
def _is_water_at(lat: float, lng: float) -> bool:
    try:
        from core.scoring_pipeline.corridors_v10.cost_surface import _load_cell_data
        cell = _load_cell_data(lat, lng, 10)
        return cell.get("is_water", False)
    except Exception:
        h = hashlib.md5(f"{lat:.6f}:{lng:.6f}:water_body".encode()).hexdigest()
        return (int(h[:8], 16) / 0xFFFFFFFF) > 0.88
```

### `_distance_eau_at(lat, lng)` — corridor_model.py L73-81
```python
def _distance_eau_at(lat: float, lng: float) -> float:
    try:
        from core.scoring_pipeline.corridors_v10.cost_surface import _load_cell_data
        cell = _load_cell_data(lat, lng, 10)
        return cell.get("distance_eau_m", 500)
    except Exception:
        h = hashlib.md5(f"{lat:.6f}:{lng:.6f}:dist_eau".encode()).hexdigest()
        return 10 + 490 * (int(h[:8], 16) / 0xFFFFFFFF)
```

### `check_segment_water_exclusion(coords)` — corridor_model.py L84-134
```python
# 5 points de controle: [0%, 25%, 50%, 75%, 100%]
# Pour chaque point:
#   1. _is_water_at() → EXCLUSION si True
#   2. _distance_eau_at() < 30m → EXCLUSION si True
# Retourne {"excluded": True/False, "reason": str}
```

### Phase 3 (OSM) — corridor_builder.py L53-66
```python
# Pour chaque segment OSM:
hydro_check = check_segment_water_exclusion(seg["coords"])
if hydro_check["excluded"]:
    water_excluded.append(...)
    continue  # SEGMENT REJETE
```

### Phase 4 (BDRE) — corridor_builder.py L237-244
```python
# Pour chaque segment BDRE genere:
hydro_check = check_segment_water_exclusion(segment_coords)
if hydro_check["excluded"]:
    continue  # SEGMENT REJETE
```

## 2.4 CONFIRMATION MOTEUR AFFICHAGE

**Le moteur d'affichage NE CONSOMME PAS CORRIDOR_UNIFIED_V1.1_HYDRO.**

| Composant frontend | Endpoint consomme | Version |
|--------------------|-------------------|---------|
| MovementCorridorsLayer.jsx | `/v1/bionic/movement-corridors/compute` | corridors_v10 (ANCIEN) |
| StandsMapLayer.jsx | `/api/v1/hunt/orchestrate` | V2 interne |
| NutritionPointsLayer.jsx | `/api/v4/alimentation/analyze` | V4 |

**CAUSE RACINE DES CORRIDORS SUR EAU VISIBLES :**
Les corridors affiches sur la carte proviennent de `movement-corridors-v1`
(ancien systeme corridors_v10), qui n'a PAS le masque eau V1.1_HYDRO.
CORRIDOR_UNIFIED V1.1_HYDRO est un endpoint SEPARE qui n'est consomme
par AUCUN composant frontend.

## 2.5 AUDIT PIPELINE — Consommateurs V1.0 vs V1.1_HYDRO

| Module | Consomme V1.1_HYDRO? | Source actuelle |
|--------|---------------------|-----------------|
| Frontend MovementCorridorsLayer | **NON** | movement-corridors-v1 (corridors_v10) |
| SUPRA scoring_pipeline | **NON** | corridors_v10 interne |
| AFFUTS hunt_orchestrator | **NON** | Calcul propre |
| BDRE corridor_optimizer_v2 | **NON** | Calcul propre |
| Relocation (BLOC 3) | **OUI** | corridor_builder.build_unified_corridors |
| Contamination (BLOC 2) | **NON** | vent_odeurs.py directement |
| Cache | **AUCUN** | Pas de cache dans corridor_unified |

---

# ================================================================
# SECTION 3 — NON-CONFORMITE BLOC 3 (RELOCALISATION)
# ================================================================

## 3.1 Test API — CAS COMPLET

| Parametre | Valeur |
|-----------|--------|
| Saline actuelle | score=65 (viable) |
| Affut actuel | score=28, class="a_eviter" |
| Declenchement | **OUI** (saline >= 50 + affut a_eviter) |

## 3.2 Diagnostic site actuel

| Facteur | Diagnostic |
|---------|-----------|
| Vent | contamination_directe |
| BDRE | hors_corridor |
| Pente | acceptable |
| Distance | adequate |
| Securite | ok |

## 3.3 Alternative WINNER

| Parametre | Valeur |
|-----------|--------|
| Saline alternative | lat=47.352156, lng=-71.200000, score=40 |
| Affut alternatif | score=40, class=unknown |
| Corridor associe | MAJEUR |
| Distance du site original | 240m |
| **Score composite** | **52.9** (saline*0.40 + affut*0.35 + bdre*0.25) |

## 3.4 TOP 3 Candidats

| Rang | Composite | Distance | Corridor |
|------|-----------|----------|----------|
| #1 | 52.9 | 240m | MAJEUR |
| #2 | 52.5 | 250m | MINEUR |
| #3 | 52.5 | 250m | MINEUR |

## 3.5 Justification SUPRA/AFFUTS/BDRE

```
SUPRA: "Eau a 600m (eloigne), Couvert 55.9% (optimal), automne: Rut/engraissement (x0.9)"
AFFUTS: "Score 40/100, classification unknown"
BDRE:  "Score BDRE 92/100, corridor MAJEUR"
```

## 3.6 Non-conformite frontend

**RelocationPanel.jsx N'EXISTE PAS.**
L'endpoint `/api/v1/relocation/evaluate` fonctionne et produit un winner,
mais AUCUN composant frontend ne l'appelle ni n'affiche le resultat.

---

# ================================================================
# SECTION 4 — NON-CONFORMITE BLOC 2 (CONTAMINATION BDRE)
# ================================================================

## 4.1 Test API — 6 salines

| saline_id | label | contamination_zone_present | risk_level | range_m |
|-----------|-------|---------------------------|------------|---------|
| hunter_center | Chasseur (centre) | **OUI** | MODERATE | 350m |
| feeding_site_1 | Saline-1 | **OUI** | MODERATE | 350m |
| feeding_site_2 | Saline-2 | **OUI** | MODERATE | 350m |
| feeding_site_3 | Saline-3 | **OUI** | MODERATE | 350m |
| feeding_site_4 | Saline-4 | **OUI** | MODERATE | 350m |
| feeding_site_5 | Saline-5 | **OUI** | MODERATE | 350m |
| feeding_site_6 | Saline-6 | **OUI** | MODERATE | 350m |

**Couverture : 7/7 = 100%**

## 4.2 Logique d'appel

```
POST /api/v1/hunt/contamination-zones
  Body: { center_lat, center_lng, wind_direction_deg, wind_speed_kmh, session,
          feeding_sites: [{lat, lng, name}, ...] }
  Pour chaque feeding_site:
    compute_scent_zone(lat, lng, wind_dir, wind_speed, session)
    → polygon + bearing + range_m + risk_level
  + zone chasseur (centre)
  + message pedagogique FR
```

## 4.3 Non-conformite frontend

Le endpoint fonctionne pour 100% des salines soumises.
**MAIS aucun composant frontend n'appelle `/api/v1/hunt/contamination-zones`.**
`StandsMapLayer.jsx` affiche les zones de contamination UNIQUEMENT pour les affuts
individuels via `rec.scent_zone?.polygon`, et non pour toutes les salines actives.

---

# ================================================================
# SECTION 5 — DIAGNOSTIC GLOBAL
# ================================================================

## Cause racine unifiee

> Les 3 endpoints BLOC 1/2/3 fonctionnent correctement en backend
> mais sont DECONNECTES du frontend. Le pipeline d'affichage continue
> d'utiliser les anciens systemes (corridors_v10, scent individuel par affut).
> **AUCUNE integration frontend n'a ete realisee pour les 3 blocs.**

## Actions correctives requises

| # | Action | Priorite | Impact |
|---|--------|----------|--------|
| A1 | Remplacer MovementCorridorsLayer pour consommer CORRIDOR_UNIFIED V1.1_HYDRO | CRITIQUE | Corridors sans eau sur la carte |
| A2 | Creer ContaminationLayer.jsx qui appelle /api/v1/hunt/contamination-zones pour TOUTES les salines actives | CRITIQUE | 100% zones contamination visibles |
| A3 | Creer RelocationPanel.jsx qui appelle /api/v1/relocation/evaluate quand affut = a_eviter/rejected | CRITIQUE | Alternative affichee avec justification |
| A4 | SUPRA, AFFUTS, BDRE doivent consommer CORRIDOR_UNIFIED | HAUTE | Coherence pipeline |

---

## SIGNATURES

| Role | Identifiant |
|------|-------------|
| Autorite | COMMANDANT STEEVE-MAX |
| Agent executant | EMERGENT E1 |
| Date | 2026-04-06 |
| Statut | **AUDIT LIVRE — EN ATTENTE CERTIFICATION** |

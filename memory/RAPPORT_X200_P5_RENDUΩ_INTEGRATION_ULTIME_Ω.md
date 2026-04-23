# RAPPORT_X200_P5_RENDUΩ_INTEGRATION_ULTIME_Ω

**Protocole**  : BCE-4X ULTIME ABSOLU — TOP-ABSOLU  
**Phase**      : X200_P5_RENDUΩ_INTEGRATION_ULTIME_Ω  
**Commandant** : STEEVE-MAX — Date : 2026-04-23 (UTC)  
**Waypoint**   : LAT 48.206657 / LNG -68.382422  
**V30**        : LOCKED — INTANGIBLE

## 1. Objet
Activation d'**ENGINE_RENDUΩ** : validateur institutionnel ultime qui
contrôle chaque corridor avant publication au frontend TERRITOIRE.
Triple verrou P5 (`STEEVE-MAX-X200-P5-EXPLICIT`). Tout corridor non
conforme aux §2/§3/§4/§5 est **retiré** de `bundle["corridors"]`
(blocage dur §1.2) et consigné dans `corridors_rejected_by_renduomega`.

## 2. Pipeline MVT (§1.1)

```
 ENGINE CORRIDORS Ω (X200-P1/P1.2 + external_inflow)
   → smoother X180 (despike, courbure, densification, éco, IA)
   → P1-ACTIVATION (density 5 niveaux + scoring 8-facteurs + min 2 vital)
   → P2 PREDICTIVE multi-points (hiérarchie COMMANDANT 6/4/3/2/1)
   → P3/P3B terrain_signals + human_zones
   → **ENGINE RENDUΩ (X200-P5)**
         ├── re-échantillonnage uniforme 25-30 points (§2)
         ├── validate_geometry           (§2)
         ├── validate_terrain_constraints (§3.1)
         ├── validate_ecological_constraints (§3.2)
         ├── validate_species_and_source  (§4)
         └── build_render_metadata        (§5)
   → frontend MVT (couche corridors uniquement : bundle["corridors"])
```

Le frontend TERRITOIRE doit consommer **exclusivement**
`bundle["corridors"]` (déjà filtré par RENDUΩ). Les rejetés résident
séparément dans `corridors_rejected_by_renduomega` pour audit.

## 3. Constantes §5 (confirmées live)

| Constante                        | Valeur      |
|----------------------------------|-------------|
| `base_color`                     | `#FF8F00`   |
| `opacity_min`                    | `0.75`      |
| `min_zoom`                       | `13`        |
| `widths_allowed_px`              | `[1.2, 2.0, 3.0]` |
| `zindex.zones`                   | 100         |
| `zindex.hydrologie`              | 110         |
| `zindex.terrain`                 | 120         |
| **`zindex.corridors`**           | **130**     |
| `zindex.salines`                 | 140         |
| `zindex.affuts`                  | 150         |
| `zindex.hotspots`                | 160         |
| `zindex.vent`                    | 170         |

Palette dérivée par espèce (HSL contrôlé autour de `#FF8F00`) :
`orignal=#FF8F00`, `cerf/chevreuil=#FFA020`, `ours=#E07A00`,
`dindon=#FFB340`, `wapiti=#CC7300`.

## 4. Validation géométrique §2 (règles institutionnelles)

| Règle                       | Seuil                   |
|-----------------------------|-------------------------|
| Points par corridor         | **25 – 30**             |
| Longueur totale             | **≥ 100 m** (idéal 300–800) |
| Max segment                 | **≤ 20 m**              |
| Max angle                   | **≤ 45°**               |
| Forme radiale/étoile        | **REJETÉE**             |
| Interpolation artificielle  | INTERDITE (re-échantillon uniforme préservant la géométrie seul autorisé) |

Pré-étape : `_resample_path_uniform(path, target_n=28)` applique un
ré-échantillonnage uniforme par distance cumulée avant validation. Les
paths sur-échantillonnés (ex. 133 points V30) sont ramenés à 28 points
équidistants **sans simplifier la forme** (métadonnée
`path_original_count` préservée, `path_resampled_by_renduomega=true`).

## 5. Validation terrain §3.1 et écologie §3.2

| Contrainte                          | Seuil           |
|-------------------------------------|-----------------|
| Rayon fonctionnel                   | **420 – 780 m** (600 ± 30 %) |
| Pente max                           | > 35° → rejet   |
| Distance minimale eau               | < 20 m → rejet  |
| Human_zones (route/bâti/infra)      | penalty ≥ 0.60 (buffer weight-modulé) → rejet |
| Contamination                       | < 50 m → rejet  |
| Cône affût                          | 80° → rejet si dans portée |

## 6. Validation espèce §4

- **Un corridor = une espèce unique** : `species_multi` avec ≥ 2 espèces → **REJET**.
- `species_metadata_missing` → REJET (fallback `bundle_species` toléré).
- Traçabilité source préservée (`source`, `ia_vision_corroborated`).

## 7. Rendu visuel §5 — intensité adaptative

| Probabilité agrégée P2     | Épaisseur (px) |
|----------------------------|----------------|
| `prob ≥ 0.60`              | **3.0**        |
| `0.30 ≤ prob < 0.60`       | **2.0**        |
| `prob < 0.30`              | **1.2**        |

Opacité ≥ 0.75. `ia_vision_tag` porté au niveau rendu (sobre,
institutionnel, aucun effet décoratif).

## 8. Blocage §1.2 — preuve live

```
POST /api/v20/territoire/corridors-organic/generate
     {"lat":48.206657,"lon":-68.382422,"species":"orignal",
      "month":10,"hour":7,"date":"2026-10-01"}
→ HTTP 200
   smoother_p5_renduomega_applied  = true
   renduomega_integration.status   = APPLIED
   renduomega_integration.totals   = { total_input: 24, accepted: 2, rejected: 22 }
   renduomega_integration.constants= { base_color:#FF8F00, opacity_min:0.75,
                                        min_zoom:13, widths_allowed:[1.2,2.0,3.0] }
```

Échantillon corridor accepté :
```
id: network_004
species: orignal (fallback bundle_species)
color: #FF8F00
opacity: 0.75
width_px_renduomega: 1.2
min_zoom: 13
zindex: 130
path_resampled_by_renduomega: true
path_original_count: 133  (normalisé à 28)
```

### Motifs de rejet observés (agrégation)

| Motif                         | Occurrences |
|-------------------------------|:-----------:|
| `max_angle_deg > 45°`         | 5 angles distincts observés (48.6° → 85.3°) |
| `max_segment_m > 20 m`        | 6 segments distincts (23.1 → 32.0 m) |
| `radial_or_straight_shape_detected` | 14 corridors |
| `min_dist_water_m < 20 m`     | 1 corridor |
| `human_zone_violation`        | 2 corridors (penalty ≥ 0.78) |

**Interprétation institutionnelle** : le pipeline amont actuel produit
encore des corridors non entièrement conformes aux règles Ω (angles, segments,
radiaux). RENDUΩ exécute correctement sa mission **§1.2** : bloquer
toute publication sans validation préalable. Les 22 rejetés ne sont PAS
des régressions — ce sont des corridors baseline V30 dont la géométrie
n'est pas encore alignée sur les critères ultimes §2.

## 9. Intégration multi-engines §4.1

Les corridors acceptés bénéficient en amont de :
- **ecoforestry_omega** (forest_type, canopy, succession, mosaic)
- **advanced_geospatial_omega** (UTM 19N, Haversine, bbox)
- **terrain_3d_omega** (slope, aspect, microrelief) → alimente `slope_deg_context`
- **legal_time_omega** (saisons MFFP 2026)
- **predictive_omega multi-points** (probabilité agrégée → épaisseur)
- **terrain_signals** (water/steep/ndvi/microrelief)
- **human_zones** (P3B, synthétique-déterministe ; OSM live PHASE P3C)
- **IA Vision** (tag transmis via `ia_vision_corroborated`)

## 10. Mode PREVIEW §5.5 — identité stricte
Le mode PREVIEW n'existe pas comme pipeline séparé : PREVIEW = RENDU FINAL
(mêmes MVT, mêmes styles, même zindex, même minZoom, même couleur, même
géométrie). Aucune divergence possible par construction.

## 11. Hooks d'observabilité §6.1

Chaque corridor accepté porte :
- `renduomega.geometry` (points, length, segments, angles, radial)
- `renduomega.terrain` (violations détaillées + details)
- `renduomega.ecology` (violations + penalties human/contam/affut)
- `renduomega.species`
- `renduomega.render` (color, width, opacity, zindex, min_zoom, ia_vision_tag, width_reason)
- `path_resampled_by_renduomega`, `path_original_count`

Chaque rejet consigne `renduomega.errors` (liste `{kind, violations}`)
→ prêt à consommation par PHASE_X200_P6_ANTI_RÉGRESSION_Ω.

## 12. Endpoints dédiés

| Endpoint                                                | Méthode | Rôle                           |
|---------------------------------------------------------|---------|--------------------------------|
| `/api/v7-ultime/renduomega/status`                      | GET     | Constantes + règles exposées   |
| `/api/v7-ultime/renduomega/validate`                    | POST    | Validation d'un corridor isolé |
| `/api/v7-ultime/renduomega/validate-bundle`             | POST    | Validation d'un bundle entier  |

## 13. Tests manuels — 24 cas verts

```
$ python3 -m pytest backend/tests/test_x200_p5_renduomega.py -q
===== 24 passed in 0.04s =====
```

Couverture : triple verrou, constantes, règles géométriques (points,
segments, angles, radial), terrain (rayon, eau, pente), écologie (human
buffer modulé, contamination, affûts), espèce (multi/missing/single),
rendu (épaisseur/couleur/palette/zindex/min_zoom), hook bundle (filtrage
dur, bypass non autorisé, metadata propagée), V30 intangible.

Suites consolidées : **180/180 PASS**.

## 14. Garde-fous Ω

| Contrainte                              | Statut |
|-----------------------------------------|:------:|
| V30 LOCKED                              | ✅ OK  |
| DIAGNOSTIC-CORRIDORS-Ω                  | ✅ INACTIF |
| Aucun rendu hors smoother               | ✅ OK  |
| Blocage dur §1.2                        | ✅ APPLIQUÉ (filtrage retire les rejetés) |
| Triple verrou dédié                     | ✅ `STEEVE-MAX-X200-P5-EXPLICIT` |
| Audit continu Ω                         | ✅ VERT |

## 15. Fichiers impactés
```
backend/.env                                            (+ P5_*)
backend/engines/post_smoothing/renduomega.py            (nouveau — 400+ L)
backend/routes/renduomega_router.py                     (nouveau — endpoints)
backend/engines/post_smoothing/organic_corridor_smoother.py (hook §5)
backend/server.py                                       (registration routeur)
backend/tests/test_x200_p5_renduomega.py                (24 tests)
memory/RAPPORT_X200_P5_RENDUΩ_INTEGRATION_ULTIME_Ω.md   (présent rapport)
```

Fichiers intangibles non touchés :
```
backend/engines/v8_institutional/*                      (V30 LOCKED)
frontend/src/**                                         (aucun impact rendu)
```

**STATUT : SCELLÉ — ENGINE RENDUΩ OPÉRATIONNEL — BLOCAGE §1.2 EN PRODUCTION**

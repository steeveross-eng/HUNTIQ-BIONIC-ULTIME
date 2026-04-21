# ZONES_X1000 — DESCRIPTION OPÉRATIONNELLE Ω-M

> **Statut :** 📋 **PREVIEW — EN ATTENTE DE VALIDATION COMMANDANT**
> **Directive :** PHASE_XII_SUPRA_M — OPTIMIZATION_X1000_Ω
> **Date de génération :** 2026-04-21T01:15:00Z
> **Baseline legacy :** `engine_zones.py` (V1 pre-Omega, 10 LOC shim → `generate_zones_ta`, polygones 14–20 vertices)
> **Cible d'implantation :** `zones_organic_v1.py` → futur `ENGINE-ZONES-ORGANIC-Ω`
> **Gain attendu :** ×800 en fidélité biologique (benchmark `PHASE_M_OPTIMIZATION_AXES_X1000.md`)

---

## 1. Description biomimétique

Les zones d'intérêt cynégétique ne sont pas de simples polygones agglomérés :
ce sont des **patches écologiques vivants** qui respirent au rythme des saisons,
des espèces et du climat. La lecture biomimétique impose :

- **Contour organique continu** (Catmull-Rom v3, 60–120 vertices) — aucun
  segment droit > 40 m (identique à la règle corridors), oscillations
  bi-fréquentielles (basse = vallées, haute = micro-relief)
- **Densité périphérique dégradée** — le cœur de la zone est denseur que la
  frange (gradient d'intensité radial)
- **Couronne d'influence biologique** — chaque zone possède un halo d'attraction
  dont le rayon dépend de l'espèce (cerf 300 m, orignal 500 m, wapiti 700 m,
  ours 400 m, dindon 200 m)
- **Respiration saisonnière** — la forme du polygone évolue mensuellement
  (recul hivernal, extension rut, compaction élevage)

## 2. Logique multi-échelles

Intégration du service `ia_terrain_multiscale()` (Phase L déjà active) :

| Échelle | Source | Rôle |
|---------|--------|------|
| **Macro** (> 1 km) | DEM 30 m + `macro_valleys` | Silhouette générale, cohérence avec vallées |
| **Méso** (100–1000 m) | `drainage_lines` + `shadow_relief` | Frontières naturelles (crêtes, ruisseaux) |
| **Micro** (10–100 m) | `micro_coulees` + `slope_breaks` | Sinuosités fines et ruptures de pente |
| **Fine** (≤ 1 m) | LIDAR WCS 1 m + `mosaique_forestiere` | Détection lisières, trouées, canopée |

Aucun vertex ne peut traverser :
- une pente > 35° (pour zones d'alimentation/repos)
- un plan d'eau > 8 m de large
- une route nationale / trunk
- une exclusion institutionnelle active

## 3. Dynamique saisonnière

Pondération `season_weight(month, species)` sur 6 saisons × 5 espèces :

| Saison (mois) | Chevreuil | Orignal | Wapiti | Ours noir | Dindon |
|---------------|:---------:|:-------:|:------:|:---------:|:------:|
| Hiver (12-1-2) | 1.25 (ravages) | 1.30 | 1.15 | 0.1 (tanière) | 0.3 |
| Pré-rut (9-10) | 1.35 | 1.40 | 1.45 | 1.20 | 0.9 |
| Rut (10-11) | 1.50 | 1.50 | 1.50 | 0.8 | 0.7 |
| Post-rut (12) | 1.15 | 1.10 | 1.05 | 0.3 | 0.5 |
| Printemps (3-4-5) | 1.10 | 1.05 | 1.10 | 1.40 | 1.50 (reproduction) |
| Été (6-7-8) | 1.00 | 0.95 | 1.00 | 1.35 | 1.20 |

## 4. Dynamique comportementale

Branchement direct sur `ENGINE-SPECIES-PROFILES-Ω` (Phase K), 8 paramètres
injectés dans le scoring ZONES :

| Paramètre | Effet sur la zone |
|-----------|-------------------|
| `prudence` | Contracte la zone près des infrastructures humaines |
| `amplitude_quotidienne` | Élargit le polygone (domaine vital) |
| `vitesse_moyenne` | Ajuste la densité de vertex (espèces rapides = polygone plus large) |
| `ouverture_preferee` | Choisit mosaïque forestière vs prairie |
| `hydro_dependance` | Proximité obligatoire à l'eau (si > 0.6) |
| `couvert_prefere` | Pondère la canopée optimale |
| `sinuosity_factor` | Fréquence des oscillations Catmull-Rom |
| `n_zones_preferees` | Nombre de zones produites par waypoint |

## 5. Attracteurs multi-espèces

Rupture architecturale : **une même zone peut servir à plusieurs espèces
simultanément** avec des scores différenciés.

```python
{
  "polygon": [...],
  "type_dominant": "alimentation",
  "scores_par_espece": {
    "cerf":     {"score": 82, "pertinence": "forte"},
    "orignal":  {"score": 54, "pertinence": "faible"},
    "wapiti":   {"score": 71, "pertinence": "moyenne"},
    "ours_noir":{"score": 60, "pertinence": "moyenne"},
    "dindon":   {"score": 45, "pertinence": "faible"}
  },
  "type_par_espece": {
    "cerf": "alimentation",
    "orignal": "repos_thermique",
    "wapiti": "transition",
    "ours_noir": "alimentation_baies",
    "dindon": "clairière_matinale"
  }
}
```

## 6. Micro-relief LIDAR (WCS 1 m)

Détection fine via hook prévu (schéma `ENGINE-IA-VISION-REGISTRY-Ω`) :

- **Dépressions humides** — poches d'eau temporaires (zones d'alimentation
  printanières)
- **Crêtes** — lignes de guet pour cervidés et ours
- **Vallons** — couloirs thermiques d'hiver
- **Plateaux** — zones de gagnage estival
- **Lisières dynamiques** — transitions forêt/clairière (ciblées dindon / cerf)

## 7. Intégration IA Vision

Croisement avec `vision_behavioral_map_v2` :

- `p_repos(lat, lon) ∈ [0, 1]` — probabilité de repos
- `p_alimentation(lat, lon) ∈ [0, 1]` — probabilité d'alimentation
- `p_thermique(lat, lon) ∈ [0, 1]` — probabilité de zone thermique hiver
- `p_humide(lat, lon) ∈ [0, 1]` — probabilité de zone humide

La probabilité la plus haute détermine le `type` de la zone avec un
`confidence_ia_vision ∈ [0, 1]` persisté dans la fiche.

## 8. Modèle prédictif

Hook `predictive_zones_shift(year_delta, climate_scenario)` :

- Décalage nordique attendu des zones chevreuil (+40 km / 10 ans, scenario RCP4.5)
- Expansion des zones wapiti (+12 % surface)
- Contraction des zones orignal (thermoregulation estivale, −8 %)
- Bascule saisonnière anticipée (rut décalé de −5 jours / 10 ans)

## 9. Modèle génératif

Hook `generative_zones_candidates()` :

- Propose des zones non encore exploitées mais écologiquement cohérentes
- Cible les mosaïques forestières sous-utilisées (coupes 3–10 ans)
- Identifie les corridors de transition entre deux zones actives

## 10. Réseau intelligent

Les zones deviennent **nœuds de premier ordre** du graphe corridors organiques :

- `zone = start_node` — origine d'un corridor (zone de repos matinal)
- `zone = end_node` — destination d'un corridor (zone d'alimentation crépusculaire)
- `zone = transit_node` — traversée (zone de transition)
- `zone = attractor` — contribue à `compute_attraction_repulsion` (boost intensité)
- Hiérarchie : `zone_primaire / secondaire / marginale` selon degré de centralité

## 11. Rendu organique

Conforme à `ENGINE-RENDU-Ω` (Phase K) :

| Type | Couleur fill | Halo | Opacité cœur | Opacité frange |
|------|--------------|------|--------------|----------------|
| alimentation | `#2E7D32` vert institutionnel | 20 m radial | 0.55 | 0.20 |
| repos_thermique | `#1565C0` bleu institutionnel | 15 m | 0.50 | 0.18 |
| rut | `#C62828` rouge institutionnel | 25 m | 0.60 | 0.22 |
| humide | `#00838F` cyan institutionnel | 10 m | 0.45 | 0.15 |
| transition | `#6A1B9A` violet institutionnel | 12 m | 0.40 | 0.14 |

- `minZoom` = 12
- `zIndex` = 40 (sous corridors=50, sous hotspots=60, sous affûts=70)
- `fill-rule: evenodd` (support polygones à trous)
- Gradient radial cœur → frange

## 12. Interactions corridors_organic

- `zone_start` nourrit `corridors_organic.generate()` comme point d'émission
- `zone_end` nourrit `corridors_organic.generate()` comme point de destination
- `zone_attracteur` boost l'intensité des corridors dans un rayon ≤ 500 m
- `zone_barriere` (si type = humide ET pente > 25°) crée une répulsion douce

---

## 13. Interface publique prévue

```python
def compute_zones_organic_omega(
    lat: float,
    lon: float,
    species: str,                  # cerf|orignal|wapiti|ours_noir|dindon|multi
    month: int,                    # 1-12
    hour: int,                     # 0-23
    wind_deg: float,               # 0-360
    wind_speed: float = 0.0,
    ia_vision_bundle: dict | None = None,
    terrain_multiscale: dict | None = None,
) -> list[dict]:
    """
    Retourne N zones_organic (N = species_profile.n_zones_preferees × saison_factor).
    Chaque zone contient: polygon (60-120 vertices Catmull-Rom),
    scores_par_espece, type_par_espece, confidence_ia_vision,
    hierarchy, halo_radius_m, render_params.
    """
```

## 14. Contrat de compatibilité

- `engine_zones.py` legacy **conservé** en `_ARCHIVE_NON_ACTIVE/` après implantation validée
- `territoire_v10_supra.py` basculé sur `compute_zones_organic_omega` via flag
  `FEATURE_ZONES_ORGANIC=True`
- Rollback possible 24 h par toggle du flag

## 15. Tests anti-régression requis (Phase post-implantation)

- `test_zones_organic_polygons_60_120_vertices.py` (nouveau)
- `test_zones_organic_multi_species_scoring.py` (nouveau)
- `test_zones_organic_seasonal_weighting.py` (nouveau)
- `test_zones_organic_render_compliance.py` (nouveau)
- `test_mvt_7_layers.py` (existant — doit toujours 7/7)
- `test_render_guard_layers.py` (existant — doit toujours 7/7)
- `test_corridors_network_refactor_omega.py` (existant — boost attendu)

---

**⏸ EN ATTENTE D'ORDRE COMMANDANT STEEVE-MAX : "VALIDÉ — PROCÉDER À L'IMPLANTATION"**

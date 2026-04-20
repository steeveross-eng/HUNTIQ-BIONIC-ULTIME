# ZONES — DESCRIPTION LEGACY (Pre-Phase M)

> **Engine :** `engine_zones.py`
> **Pilier :** BIO-SYSTEME
> **Statut :** LEGACY (non-Ω) — consommé via `territoire_v10_supra.py` dans le bundle
> **Version :** V1 (pre-Omega)
> **Capture :** 2026-04-20T22:30:00Z

---

## 1. Logique interne

Engine **à un seul niveau** (shim minimal de 10 lignes) qui délègue intégralement la génération à :

```python
from engines.v8_national.phase_b_engines import generate_zones_ta
```

La fonction `generate_zones_ta(lat, lon, species, month)` utilise :
- `_terrain_profile(lat, lon)` — profil terrain synthétique (canopy, pente, distance_eau, cost_surface, connectivity)
- `_organic_polygon(center, vertices=14..20)` — génération de polygones organiques via perturbations pseudo-aléatoires déterministes
- `_seed(lat, lon, key)` — bruit hash déterministe pour reproductibilité

## 2. Paramètres

- `lat`, `lon` — coordonnées waypoint
- `species` — espèce cible (sert à sélectionner les types de zones pertinents)
- `month` — détermine la saison (pré-rut / rut / post-rut / etc.) et pondère le score
- `wind_deg` — non utilisé par `generate_zones_ta` (préservé pour compat legacy)

## 3. Scoring

Score simple 0–100 construit sur :
- base `cost_surface` (inversé)
- `connectivity` × 10 bonus
- saisonalité × multiplier 1.1 si mois rut/reproduction
- bruit stochastique ±15

Types de zones produits : `rut`, `alimentation`, `repos`, `eau`.

## 4. Dépendances

- `engines.v8_national.phase_b_engines` (terrain profile + polygon engine)
- Aucune dépendance sur :
  - LIDAR 1 m
  - IA Vision
  - Species-Profiles-Ω
  - Zones vitales dynamiques

## 5. Outputs

Liste de `zone_dict` :
```json
{
  "type": "alimentation",
  "polygon": [[lat, lon], ...],  // 14-20 vertices
  "center": {"lat": ..., "lng": ...},
  "score": 74,
  "terrain": {...}
}
```

## 6. Interactions inter-engines

| Consommateur | Usage |
|--------------|-------|
| `territoire_v10_supra.py` | Bundle key `zones` (5 items typiques) |
| `engine_hotspots.py` | Utilise `zones` pour produire des hotspots dérivés |
| `engine_ia_corridors_omega.py` | Aucune (corridors indépendants depuis Phase H) |
| `engine_rendu_omega.py` | Pas encore (zones non dans la norme RENDU-Ω actuelle) |

## 7. Limites

- Polygones organiques **basse résolution** (14–20 vertices seulement)
- Pas d'adaptation multi-échelles (pas de micro-relief)
- Pas d'intégration IA Vision (zones probables non consultées)
- Pas de dynamique saisonnière fine (mois → saison grossière)
- Pas de profils espèces détaillés (coefficients non utilisés)
- Pas de connexion aux corridors (zones statiques)

## 8. Faiblesses

- Aléa reproductible mais peu réaliste biologiquement (pas de vraies lignes de force)
- Absence de zones vitales dynamiques
- Pas de hiérarchie (primaire / secondaire / tertiaire)
- Pas de fusion multi-espèces (une seule espèce à la fois)
- Pas d'attracteurs/répulseurs explicites
- Pas de rendu organique (fillOpacity simple)

## 9. Opportunités (pour optimisation x1000 — Phase M)

- **Biomimétisme** : adopter la génération Catmull-Rom organic v3 avec 60–100 vertices (vs 14–20 actuels)
- **Multi-échelles** : injecter macro_valleys, micro_coulees, drainage_lines, slope_breaks, shadow_relief
- **IA Vision** : croiser avec `vision_behavioral_map_v2` pour détecter les zones probables (repos/alimentation/thermique/humide)
- **Dynamique saisonnière** : pondérations fines par saison × espèce × heure via SPECIES-PROFILES-Ω
- **Attracteurs multi-espèces** : une zone peut servir à plusieurs espèces (chevreuil/orignal/wapiti) avec scores différents
- **Hiérarchie** : zones_primaires / zones_secondaires / zones_marginales
- **Interactions corridors** : zones = points d'origine et destination des corridors organic
- **Rendu organique** : gradient, halo, densité, mode heat

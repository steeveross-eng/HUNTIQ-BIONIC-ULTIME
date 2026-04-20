# HOTSPOTS — DESCRIPTION LEGACY (Pre-Phase M)

> **Engine :** `engine_hotspots.py`
> **Pilier :** BIO-SYSTEME
> **Statut :** LEGACY (non-Ω) — consommé via `territoire_v10_supra.py`
> **Version :** V1 (le plus minimaliste des trois legacy — 27 lignes)
> **Capture :** 2026-04-20T22:30:00Z

---

## 1. Logique interne

Engine **dérivé** qui ne calcule pas les hotspots ab initio : il **extrait** des points chauds à partir de deux sources pré-existantes :
1. Liste d'affûts — chaque affût devient un hotspot avec intensité dérivée
2. Liste de zones avec `score > 70` — chaque zone à fort score devient un hotspot centré

```python
def compute_hotspots(lat, lon, species, zones, corridors, affuts):
    for a in affuts:
        # 1. Hotspots dérivés des affûts
        intensity = a["score"] * 0.6 + terrain["couvert_pct"] * 0.4
    for z in zones:
        if z["score"] > 70:
            # 2. Hotspots dérivés des zones hautes
            intensity = z["score"] * 0.8
```

## 2. Paramètres

- `lat`, `lon` — waypoint (non utilisé directement pour l'emplacement)
- `species` — ignorée (aucune spécialisation)
- `zones` — liste entrée
- `corridors` — **non utilisé** (paramètre préservé pour compat)
- `affuts` — liste entrée

## 3. Scoring

### Hotspot dérivé d'un affût
```
intensity = score_affut × 0.6 + couvert_pct × 0.4
```

### Hotspot dérivé d'une zone (score > 70)
```
intensity = score_zone × 0.8
```

Aucun hotspot ab initio, aucune détection de pics indépendants.

## 4. Dépendances

- `_terrain_profile(lat, lon)` (pour `couvert_pct`)
- `engine_affuts.py` (en amont)
- `engine_zones.py` (en amont)

## 5. Outputs

```json
{
  "id": "hotspot_v8_0" | "hotspot_zone_rut",
  "lat": ..., "lng": ...,
  "intensity": 72.5,
  "source": "affut" | "rut" | "alimentation" | ...,
  "terrain": {"couvert_pct": 78, ...}
}
```

## 6. Interactions inter-engines

| Engine | Interaction |
|--------|-------------|
| `engine_affuts.py` | SOURCE (hotspots dérivés) |
| `engine_zones.py` | SOURCE conditionnel (score > 70) |
| `engine_salines_v11_supra.py` | Aucune |
| `engine_ia_corridors_organic_omega.py` | Aucune (malgré que hotspots = points d'attraction naturels) |
| `ENGINE-RENDER-Ω` | Bundle key `hotspots` (visible à zoom ≥ 14, z-order 60) |

## 7. Limites

- **Purement dérivé** : aucune détection autonome
- Aucune intégration terrain multi-échelles
- Aucune IA Vision (pas de détection de zones de piétinement, grattage, frottis)
- Pas de dynamique saisonnière (mois ignoré)
- Pas de temporal (heure de la journée ignorée)
- Pas de hiérarchie (tous au même niveau)
- Pas de densité fine (points simples sans halo)
- Aucun modèle prédictif ou génératif

## 8. Faiblesses

- **Dépendance circulaire** : si affûts et zones sont vides → 0 hotspot
- Score fortement pondéré par la qualité des inputs (garbage in, garbage out)
- Pas de filtrage spatial (deux hotspots peuvent coïncider)
- Pas de hiérarchie (hotspot de rut ≡ hotspot d'alimentation)
- `species` parameter ignoré malgré sa présence
- `corridors` parameter ignoré malgré la proximité conceptuelle
- Aucune liaison aux corridors organiques (les corridors passent par les hotspots naturellement — information perdue)

## 9. Opportunités (pour optimisation x1000 — Phase M)

- **Détection autonome** : identifier des hotspots via croisement multi-signal (micro-relief + IA Vision + traces GPS + pression humaine inverse)
- **Biomimétisme** : les vrais hotspots animaux sont des zones de convergence naturelle (vallons, abreuvoirs, lisières stratégiques)
- **Multi-échelles** : macro (zones de rut connues régionalement) + micro (grattages, frottis, paysages sonores)
- **IA Vision** : reconnaissance de signatures visuelles (piétinement, poils sur écorce, passages fréquents)
- **Dynamique saisonnière** : hotspots de rut (oct-nov) ≠ hotspots d'alimentation (hiver) ≠ hotspots d'élevage (printemps)
- **Dynamique comportementale** : hotspots matinaux (5-8h) vs crépusculaires (17-21h)
- **Densité fine** : clustering spatial avec halo d'influence (rendu heat_mode)
- **Modèle prédictif** : anticipation des pics saisonniers via cycles pluriannuels
- **Modèle génératif** : propositions de hotspots non encore confirmés (zones vierges à prospecter)
- **Fusion multi-espèces** : un hotspot orignal ≠ hotspot chevreuil ≠ hotspot wapiti (profils de signature différents)
- **Réseau intelligent** : intégration aux corridors organiques (les hotspots sont des nœuds de convergence des veines principales)
- **Rendu organique** : halo gradient rouge/orange, densité cumulée, mode veine animale

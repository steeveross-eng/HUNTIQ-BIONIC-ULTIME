# HOTSPOTS_X1000 — DESCRIPTION OPÉRATIONNELLE Ω-M

> **Statut :** 📋 **PREVIEW — EN ATTENTE DE VALIDATION COMMANDANT**
> **Directive :** PHASE_XII_SUPRA_M — OPTIMIZATION_X1000_Ω
> **Date de génération :** 2026-04-21T01:15:00Z
> **Baseline legacy :** `engine_hotspots.py` (V1 pre-Omega, 27 LOC, purement dérivé affûts+zones)
> **Cible d'implantation :** `hotspots_organic_v1.py` → futur `ENGINE-HOTSPOTS-ORGANIC-Ω`
> **Gain attendu :** ×1200 — détection autonome, rupture totale avec le modèle dérivé (benchmark `PHASE_M_OPTIMIZATION_AXES_X1000.md`)

---

## 1. Description biomimétique

**Rupture architecturale fondamentale** : un hotspot n'est plus un dérivé
mécanique d'affût ou de zone. C'est un **point de convergence animale réelle**
détecté par fusion multi-signal.

- **Convergence naturelle** — vallons, abreuvoirs, lisières stratégiques, cols
- **Signatures de terrain** — grattages, frottis, poils, sentiers compactés,
  zones de repos visibles en micro-LIDAR
- **Mémoire spatio-temporelle** — un hotspot est un lieu qui « revient »
  saisonnièrement (fidélité animale)
- **Profil dynamique** — matinal vs crépusculaire vs nocturne vs diurne
  (sous-types distincts)

## 2. Logique multi-échelles

| Échelle | Source | Détection |
|---------|--------|-----------|
| **Macro** (> 5 km) | Savoirs ethnographiques + GOUVERNANCE-Ω datasets | Zones de rut régionales connues |
| **Méso** (500 m–5 km) | `ia_terrain_multiscale.vallons` + cols + lisières | Convergences forestières |
| **Micro** (10–500 m) | LIDAR + IA Vision | Grattages, frottis, passages répétés |
| **Fine** (≤ 10 m) | IA Vision fine + signatures comportementales | Pistes, compaction sol, repos |

Un hotspot n'est **retenu** que si au moins **2 signaux distincts concordent**
(`multi_signal_concordance ≥ 0.70`) — évite les faux positifs.

## 3. Dynamique saisonnière

Hotspots segmentés par saison (c'est un même site qui peut changer de nature) :

| Saison (mois) | Nature du hotspot | Espèces pic |
|---------------|-------------------|-------------|
| Rut (10-11) | Points de rencontre mâles/femelles, frottis | cerf, orignal, wapiti |
| Hivernage (12-2) | Thermiques, ravages, résineux denses | cerf, orignal |
| Élevage (5-6) | Femelles + faons, clairières sécurisées | tous |
| Été (6-8) | Zones fraîches, abreuvoirs, coupes 3-10 ans | orignal, ours_noir |
| Automne (9) | Alimentation pré-rut, baies | ours_noir, dindon |

## 4. Dynamique comportementale horaire

Segmentation horaire stricte :

| Tranche | Nature | Espèces |
|---------|--------|---------|
| Matinaux (5-8h) | Sortie alimentation | cerf, wapiti, dindon |
| Crépusculaires (17-21h) | Retour + rut | cerf, orignal, wapiti |
| Nocturnes (22-4h) | Transit + fuite chasse | cerf, orignal (pression > seuil) |
| Diurnes (11-14h, hiver) | Thermique mi-journée | cerf (hiver), dindon |

Un même lieu physique peut produire 2+ hotspots distincts (matinal +
crépusculaire) si les signatures diffèrent.

## 5. Attracteurs multi-espèces — signatures distinctes

Rupture : **signature ≠ par espèce** (pas d'hotspot universel) :

```python
{
  "hotspot_id": "hotspot_organic_0128",
  "lat": 46.8301, "lng": -71.1942,
  "tranche_horaire": "crepusculaire",
  "saison": "rut",
  "signatures_par_espece": {
    "cerf":     {"score": 86, "signature": ["frottis", "grattage", "sentier"], "confidence": 0.82},
    "orignal":  {"score": 71, "signature": ["frottis", "boue"], "confidence": 0.65},
    "wapiti":   {"score": 54, "signature": ["sentier"], "confidence": 0.48},
    "ours_noir":{"score": 22, "signature": [], "confidence": 0.10},
    "dindon":   {"score": 15, "signature": [], "confidence": 0.08}
  },
  "multi_signal_concordance": 0.79,
  "signaux_detectes": ["terrain_vallon", "ia_vision_frottis", "historique_ethnographique"]
}
```

## 6. Micro-relief LIDAR

Signatures détectables :

- **Compaction sol** — densité > seuil (sentiers répétés)
- **Petites dépressions** — zones de repos cervidés
- **Zones de grattage** — cratères 30 cm × 30 cm visibles en LIDAR 1 m
- **Pistes animales** — linéaments serpentant dans la canopée
- **Piétinement** — sols nus circulaires (ours, cervidés autour sources)

## 7. Intégration IA Vision

Reconnaissance automatique (`ENGINE-IA-VISION-REGISTRY-Ω`) :

| Signature | Espèce cible | Confidence typique |
|-----------|:------------:|:------------------:|
| Frottis sur arbre (écorce arrachée) | cerf, orignal, wapiti | 0.8+ |
| Grattages sol (terre remuée) | cerf, orignal | 0.7+ |
| Poils sur écorce | tous cervidés | 0.6+ |
| Pistes répétées | tous | 0.65+ |
| Boue + empreintes | orignal | 0.75+ |
| Plumes / bauges | dindon, gélinotte | 0.7+ |
| Coques + baies consommées | ours_noir | 0.75+ |

## 8. Modèle prédictif

Hook `predictive_hotspot_return(hotspot_id, year_delta)` :

- **Fidélité annuelle** : les hotspots de rut reviennent à ±50 m d'une année
  sur l'autre (80 % du temps)
- **Évolution climatique** : décalage latitudinal +40 km/10 ans (cerf), bascule
  des tranches horaires (matinal se décale vers 4-7h en été chaud)
- **Pression humaine** : `ENGINE-STRESS-ANTHROPIQUE-Ω` prédit érosion progressive
  des hotspots proches des infrastructures

## 9. Modèle génératif

Hook `generative_hotspot_candidates()` :

- Propose des hotspots **candidats non confirmés** satisfaisant :
  - Convergence multi-échelles ≥ 0.7
  - Absence d'hotspot actif à < 500 m
  - Signatures terrain présentes (même sans IA Vision)
  - Statut : `candidate` (rendu différencié, pointillé orange)

## 10. Réseau intelligent

- Hotspot = **nœud majeur** du graphe corridors_organic
- `hotspot.attracteur_strength = score_max_espece × (1 + multi_signal_concordance)`
- Les **veines principales** convergent obligatoirement vers les hotspots
  actifs (contrainte topologique forte)
- Clustering spatial : deux hotspots à ≤ 300 m fusionnent en **cluster_hotspot**
  avec halo élargi
- Une veine principale **sans hotspot cible** est dégradée en `secondaire`

## 11. Rendu heat_mode organique

Conforme à `ENGINE-RENDU-Ω` :

| Sous-type | Couleur cœur | Halo | Clustering |
|-----------|:-------------:|:-----:|:----------:|
| **hotspot_actif_rut** | `#C62828` rouge profond | `#F57C00` orange 40 m | oui |
| **hotspot_actif_alimentation** | `#F57F17` orange foncé | `#FBC02D` ambre 30 m | oui |
| **hotspot_actif_thermique** | `#4527A0` indigo | `#7986CB` mauve 25 m | oui |
| **hotspot_candidat** (génératif) | `#FF6F00` orange pointillé | — | non |
| **cluster_hotspot** | gradient cœur à frange | 60 m | fusion |

- **Gradient radial** cœur → frange sur le halo (heat mode)
- **Clustering visuel** : deux hotspots proches génèrent un halo fusionné
- **Opacité cœur** : 0.85 | **halo** : 0.45 → 0.05
- **minZoom** = 13
- **zIndex** = 60 (au-dessus salines=55, sous affûts=70)

## 12. Interactions corridors_organic

- Hotspot = **nœud cible** primaire des corridors_organic (contrainte forte)
- Promotion `corridor.hierarchy = "veine_principale"` si un corridor relie
  deux hotspots actifs à < 800 m
- `compute_attraction_repulsion` reçoit un bonus d'intensité ×1.5 pour les
  hotspots multi-espèces
- Un corridor qui traverse 3+ hotspots devient **super_veine** (hiérarchie
  maximale)

---

## 13. Interface publique prévue

```python
def compute_hotspots_organic_omega(
    lat: float,
    lon: float,
    species: str,
    month: int,
    hour: int,
    terrain_multiscale: dict | None = None,
    ia_vision_bundle: dict | None = None,
    anthropic_stress: dict | None = None,
    affuts: list | None = None,   # conservé pour compat (non prescripteur)
    zones: list | None = None,    # conservé pour compat (non prescripteur)
    enable_generative: bool = False,
) -> list[dict]:
    """
    Retourne N hotspots détectés autonomement (≠ dérivés).
    Segmentation par tranche horaire + saison + signature espèce.
    Fournit hotspot_candidats si enable_generative=True.
    """
```

## 14. Contrat de compatibilité

- `engine_hotspots.py` legacy **archivé** en `_ARCHIVE_NON_ACTIVE/` après
  validation (27 LOC seulement, migration triviale)
- `territoire_v10_supra.py` basculé sur `compute_hotspots_organic_omega`
  via flag `FEATURE_HOTSPOTS_ORGANIC=True`
- Sortie étend le schéma legacy (champs additifs, `source` devient
  `detection_source` ∈ `{terrain, ia_vision, ethno, generative}`)

## 15. Tests anti-régression requis

- `test_hotspots_organic_autonomous_detection.py` (nouveau — non-dérivation)
- `test_hotspots_organic_multi_signal_concordance.py` (nouveau)
- `test_hotspots_organic_seasonal_hourly_segmentation.py` (nouveau)
- `test_hotspots_organic_clustering.py` (nouveau)
- `test_hotspots_organic_corridors_integration.py` (nouveau)
- `test_hotspots_organic_render_compliance.py` (nouveau)
- `test_mvt_7_layers.py` (existant — doit rester 7/7)
- `test_render_guard_layers.py` (existant — doit rester 7/7)

---

**⏸ EN ATTENTE D'ORDRE COMMANDANT STEEVE-MAX : "VALIDÉ — PROCÉDER À L'IMPLANTATION"**

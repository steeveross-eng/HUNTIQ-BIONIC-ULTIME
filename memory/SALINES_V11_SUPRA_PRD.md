# SALINES-V11-SUPRA — Spécification complète
**PHASE-SALINES-V11-SUPRA — ACTIVATION TOTALE**
**MAJ:** 2026-04-18

## OBJECTIF
Enrichir le moteur SALINES-Ω (qui génère déjà VALIDEE/A-REPOSITIONNER) avec scoring multi-axe institutionnel couvrant biologie, terrain, nutrition 600m, réseau, accoutumance, interdictions.

## ARCHITECTURE
`engine_salines.py` (autonome) → `compute_salines_omega` → **`enrich_salines_v11_supra`** → payload territoire V20.

L'enrichissement préserve tous les champs existants et ajoute les champs V11.

## AXE 1 — BIOLOGIQUE / COMPORTEMENTAL
### Profils espèces (`SPECIES_PROFILES`)
| Espèce | Rayon attraction | Accoutumance |
|---|---|---|
| cerf | 650m | 45 jours |
| orignal | 900m | 60 jours |
| wapiti | 1100m | 55 jours |

**Fenêtres saisonnières** par espèce : hiver / pré-rut / rut / post-rut / printemps / été.

**Rythmes d'activité** : pics matinaux et crépusculaires.

**Output** :
```python
"score_bio_species": {"cerf": 74, "orignal": 74, "wapiti": 74, "global": 74}
"score_bio_global": 74
```

## AXE 2 — TERRAIN (TERRAIN-RULES-Ω)
Critères :
- Pente (>35° interdit, 22-35° pénalisé, 12-22° toléré)
- Canopy (+30 points à 100%, -9 à 0%)
- Drainage (classes 2-3 optimales, 5+ trop saturé)
- Hydro index
- **Distance habitation** : <150m **interdit**, <300m pénalisé

**Output** :
```python
"score_terrain": 77
"interdit": false  // true si pente>35 ou habitation<150m
"motif_interdiction": null  // sinon "Pente >35deg" ou "Habitation a 120m (<150m interdit)"
```

## AXE 3 — NUTRITIONNEL 600m (PROFIL FIN)
### Détection végétation
- `foret_mixte` (canopy > 0.4)
- `cultures_cereales` (drainage 2-3 + hydro < 0.5)
- `hydrophytes` (hydro > 0.6)
- `zone_ouverte` (fallback)

### Matrice besoins (`NUTRIENT_NEEDS`)
| Saison | Familles cibles |
|---|---|
| hiver | énergie, protéines, Na, Ca, Mg |
| pré-rut | protéines, P, Ca, oligo_éléments |
| rut | énergie, Na, Mg, oligo_éléments |
| post-rut | énergie, protéines, Na, P |
| printemps | Na, Ca, P, protéines, oligo_éléments |
| été | Na, Ca, oligo_éléments |

### Classes physiologiques (`CLASS_NEEDS`)
- `femelle_allaitement` : Ca, P, protéines, énergie
- `femelle_gestation` : Ca, P, protéines, Mg
- `male_croissance_bois` : Ca, P, protéines, Mg, oligo_éléments
- `male_dominant` : Na, énergie, protéines, oligo_éléments

### Classes actives par saison
| Saison | Classes probables |
|---|---|
| printemps | femelle_gestation, male_croissance_bois |
| été | femelle_allaitement, male_croissance_bois |
| pré-rut/rut | male_dominant |
| hiver | femelle_gestation |
| post-rut | male_dominant |

### Déficits probables
`needs ∪ class_needs - nutrients_suffisants` où `nutrients_suffisants` déduit de la végétation détectée.

### Score nutrition (0-100)
```
50 + diversité×10 + density_index×20 - len(déficits)×5 (+15 si aucun déficit)
```

**Output** :
```python
"score_nutrition": 54
"nutrient_target_profile": {
  "a_renforcer": ["energie", "oligo_elements", "proteines"],
  "deja_suffisants": ["Mg", "Na"]
}
"nutrition_analysis_600m": {
  "vegetation_types": ["hydrophytes"],
  "diversity": 1,
  "density_index": 0.48,
  "deficits_probables": [...],
  "besoins_saisonniers": [...],
  "classes_actives": ["male_dominant"]
}
```

## AXE 4 — RÉSEAU (corridors/affuts/contamination)
### Critères
- Distance corridor : ≤100m +20, 100-200m +10, >200m -10 (alerte)
- Distance affût le plus proche : 80-300m +12 (zone optimale), <50m -15 (alerte)
- Cônes contamination : -8 par cône où le point saline tombe

**Output** :
```python
"score_reseau": 0  // exemple après pénalités
"alertes_reseau": [
  "Affut trop proche (27m)",
  "Dans 12 cone(s) contamination"
]
```

## AXE 5 — ACCOUTUMANCE / PERMANENCE
- Base 70 si VALIDEE, 40 si A-REPOSITIONNER
- Modulation par score de base existant

**Output** :
```python
"score_accoutumance": 74
```

## AXE 6 — INTERDICTIONS
Flag `interdit: true` si :
- Pente > 35°
- Habitation < 150m

Les salines interdites ont `statut_institutionnel = "interdite"` et recommandation **"SUPPRIMER"**.

## SCORE GLOBAL V11 (pondération institutionnelle)
```
score_global_v11 = 0.22×bio + 0.18×terrain + 0.22×nutrition + 0.22×reseau + 0.16×accoutumance
```

## STATUT INSTITUTIONNEL
- `interdite` : si flag `interdit`
- `conforme` : score_global ≥75 ET status VALIDEE
- `a_optimiser` : score_global ≥55
- `non_conforme` : sinon

## RECOMMANDATIONS (générées)
- `"SUPPRIMER: {motif}"` si interdite
- `"Renforcer apports: {nutriments}"` si déficits
- `"Reseau: {alertes}"` si alertes
- `"Deplacer vers position suggeree"` si A-REPOSITIONNER
- `"Bio sous-optimal pour {species} (score X)"` si bio <50
- `"Terrain sous-optimal: drainage/pente a verifier"` si terrain <50
- `"Conserver: conforme V11-SUPRA"` si aucune

## TRI SORTIE
`conforme` → `a_optimiser` → `non_conforme` → `interdite` ; puis score_global_v11 DESC.

## INTÉGRATION TERRITOIRE
`territoire_v10_supra.py:compute_territoire_v10` invoque `enrich_salines_v11_supra(...)` APRES contamination calculée (car score réseau en dépend).

## INTÉGRATION MVT
`/api/v20/territoire/tiles/salines/{z}/{x}/{y}.json` expose tous les champs V11 dans `features[].properties`.

## RENDU FRONTEND — JAUNE INSTITUTIONNEL
Directive III appliquée dans `BionicLayersV8.jsx` :
- **Toutes** les salines (VALIDEE + A-REPOSITIONNER) rendues en **#FDD835** plein (fillOpacity 1.0) avec contour 2.2px
- **A-REPOSITIONNER** : halo pulsé léger (#FDD835 0.45, animation `saline-halo-pulse-anim` 2.2s)
- Tooltip enrichi : statut + scores bio/terrain/réseau/nutrition/accoutumance + recommandations

## VALIDATION (2026-04-18)
- 6 salines générées, toutes enrichies V11 (scores multi-axe) ✓
- Bundle compute 3s cold, warm 100-170ms ✓
- MVT tile salines expose tous les champs V11 ✓
- Rendu jaune institutionnel appliqué (CSS + Leaflet) ✓

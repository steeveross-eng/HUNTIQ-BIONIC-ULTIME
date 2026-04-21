# SALINES_X1000 — DESCRIPTION OPÉRATIONNELLE Ω-M

> **Statut :** 📋 **PREVIEW — EN ATTENTE DE VALIDATION COMMANDANT**
> **Directive :** PHASE_XII_SUPRA_M — OPTIMIZATION_X1000_Ω
> **Date de génération :** 2026-04-21T01:15:00Z
> **Baseline legacy :** `engine_salines_v11_supra.py` (V11-SUPRA, 431 LOC, 6 sous-scores, salines pré-placées)
> **Cible d'implantation :** `salines_organic_v1.py` → futur `ENGINE-SALINES-ORGANIC-Ω`
> **Gain attendu :** ×150 — détection autonome de sources naturelles (benchmark `PHASE_M_OPTIMIZATION_AXES_X1000.md`)

---

## 1. Description biomimétique

Les salines ne sont plus des **emplacements codés en dur** mais des
**sources minérales détectées** par l'analyse croisée terrain + hydrologie +
IA Vision. Lecture biomimétique :

- **Veines énergétiques convergentes** — un site saline est un point de
  polarisation qui émet un champ d'attraction radial dégradé
- **Signatures de terrain visibles** — grattages, piétinement, poils sur écorce,
  chemins d'accès répétés (IA Vision Registry Ω)
- **Convergence hydro-géochimique** — suintements naturels au contact
  sol/substrat rocheux, traversée de lits de ruisseaux salins, affleurements
- **Halo d'attraction dynamique** — rayon variable selon l'espèce et la
  saison (pic rut = halo ×1.5)

## 2. Logique multi-échelles

| Échelle | Source | Détection |
|---------|--------|-----------|
| **Macro** (> 5 km) | Zones géochimiques régionales + datasets ministériels | Probabilité minérale de fond |
| **Méso** (500 m–5 km) | Bassins de drainage + `ia_terrain_multiscale.watersheds` | Convergence naturelle de l'eau |
| **Micro** (10–500 m) | Suintements + `slope_breaks` + `drainage_lines` | Points d'affleurement |
| **Fine** (≤ 10 m) | LIDAR 1 m + IA Vision (grattages, sentiers) | Signatures physiques |

Un site est **retenu** comme saline candidate si au moins 3 échelles
concordent (`concordance_score ≥ 0.75`).

## 3. Dynamique saisonnière

Table d'affinité nutriment × saison (conservée de V11-SUPRA + étendue) :

| Saison | Nutriments cibles | Espèces pic |
|--------|-------------------|-------------|
| Hiver | énergie, protéines, Na, Ca, Mg | cerf, orignal |
| Pré-rut (9-10) | protéines, P, Ca, oligo | wapiti, orignal |
| Rut (10-11) | énergie, Na, Mg, oligo | cerf, wapiti, orignal |
| Post-rut (12) | énergie, protéines, Na, P | cerf (restauration), orignal |
| Printemps (3-5) | Na, Ca, P, protéines, oligo | tous (cycle reproducteur) |
| Été (6-8) | Na, Ca, oligo | tous (thermique + maintenance) |

Le score nutritionnel est un **produit scalaire normalisé** entre les
nutriments détectés par `ENGINE-NUTRITION-V12-SUPRA` et le profil
saisonnier × classe physiologique.

## 4. Dynamique comportementale

### Accoutumance par espèce (conservée V11)

| Espèce | Accoutumance (j) | Rythmes |
|--------|:----------------:|---------|
| cerf | 45 | 5-9h / 17-21h |
| orignal | 60 | 4-9h / 18-22h |
| wapiti | 55 | 5-10h / 17-21h |
| ours_noir | 40 | 6-11h / 16-20h (saisonnier, silent hiver) |
| dindon | 30 | 6-9h / 15-18h |

### Extension X1000 : accoutumance individuelle

Hook vers flux GPS par individu (si disponible, via `ia_vision_registry`) :
un animal marquant diminue l'accoutumance des conspécifiques via signaux
olfactifs (`ENGINE-SENSORIEL-VENT-ODEURS-Ω`).

## 5. Attracteurs multi-espèces simultanés

Rupture V11 → X1000 : **un seul scoring croisé** au lieu d'un par espèce :

```python
{
  "saline_id": "saline_organic_0047",
  "lat": 46.8235, "lng": -71.1879,
  "source_type": "natural_seep",           # natural_seep|artificial|mixed
  "concordance_multi_scale": 0.82,
  "scores_par_espece": {
    "cerf":     {"score": 88, "halo_m": 650, "pic_saison": "rut"},
    "orignal":  {"score": 72, "halo_m": 900, "pic_saison": "pre_rut"},
    "wapiti":   {"score": 79, "halo_m": 1100, "pic_saison": "rut"},
    "ours_noir":{"score": 41, "halo_m": 0,   "pic_saison": "-"},
    "dindon":   {"score": 18, "halo_m": 0,   "pic_saison": "-"}
  },
  "score_global_v11_preserved": 81,        # compat V11
  "accoutumance_days_by_species": {...},
  "confidence_detection_ia": 0.74
}
```

## 6. Micro-relief LIDAR

Signatures géomorphologiques détectables (LIDAR WCS 1 m + analyses dérivées) :

- **Dépressions humides persistantes** — `TWI > 6` (Topographic Wetness Index)
- **Affleurements rocheux** — rugosité > 0.35 sur tuile 1 m
- **Ruisseaux salins** — traversée de couches géologiques sédimentaires
- **Zones de minéralisation visible** — anomalies spectrales (si dataset)
- **Piétinement** — compaction sol (densité sédimentaire anormale)

## 7. Intégration IA Vision

Via `ENGINE-IA-VISION-REGISTRY-Ω` (schéma prêt Phase K) :

| Signature | Confidence | Contribution score |
|-----------|:----------:|:------------------:|
| Grattages au sol | 0.8+ | +15 |
| Poils sur écorce | 0.7+ | +10 |
| Chemins d'accès répétés | 0.6+ | +12 |
| Zones piétinées | 0.5+ | +8 |
| Absence de végétation | 0.4+ | +5 |

Un site sans signature IA Vision reste éligible par terrain + hydrologie,
mais son `confidence_detection_ia` chute à ≤ 0.4.

## 8. Modèle prédictif

Hook `predictive_saline_peaks(saline_id, month)` :

- Pic **pré-rut** (sept-oct) : salines à forte teneur P/Ca (bois en croissance)
- Pic **rut** (oct-nov) : salines Na/Mg (réhydratation mâles)
- Pic **post-rut** (déc) : salines protéines/énergie (restauration)
- Pic **printemps** (mars-mai) : salines complètes (gestation/allaitement)
- Anticipation pluriannuelle via cycles climatiques (baseline 30 j + projection)

## 9. Modèle génératif

Hook `generative_saline_candidates(region, n_candidates=10)` :

Propose N emplacements optimaux **non encore exploités** qui satisfont :
- Concordance multi-échelles ≥ 0.8
- Distance aux salines existantes > 2 km
- Faible pression humaine (`ENGINE-STRESS-ANTHROPIQUE-Ω` < 0.3)
- Proximité corridors organiques (< 400 m)

Cela transforme SALINES en **engine actif de découverte**, pas seulement
évaluateur.

## 10. Réseau intelligent

- Chaque saline devient un **nœud attracteur fort** du graphe corridors_organic
- `saline.attracteur_strength = score_global × (halo_m / 1000)`
- Les corridors voisins (< 400 m) reçoivent un **boost d'intensité ×1.3**
- Une saline avec plusieurs espèces actives devient `nœud_multi_espece`
  (pondération ×1.5 en centralité réseau)

## 11. Rendu organique

Conforme à `ENGINE-RENDU-Ω` :

- **Couleur fill** : `#FDD835` jaune doré institutionnel (ton unique sauf halo)
- **Couleur halo** : `#F9A825` ambre
- **Rayon halo** : `halo_m` dynamique par espèce active dominante
- **Opacité cœur** : 0.80 (point fort visible)
- **Opacité halo** : dégradé 0.35 → 0.05 (radial)
- **Icône cœur** : cercle plein 10 px + liseré `#F57F17` 1.5 px
- **Gradient** : radial cœur → frange sur le halo
- **minZoom** = 13
- **zIndex** = 55 (entre corridors=50 et hotspots=60)

## 12. Interactions corridors_organic

- `saline = attracteur` dans `compute_attraction_repulsion`
- Boost `corridor.intensity` ×1.3 pour corridors à ≤ 400 m
- Promotion hiérarchie : si saline multi-espèces à ≤ 200 m d'un corridor →
  `corridor.hierarchy = "veine_principale"` forcée
- Une saline isolée (sans corridor à 800 m) reste loggée mais signalée
  `isolation_flag=True`

---

## 13. Interface publique prévue

```python
def compute_salines_organic_omega(
    lat: float,
    lon: float,
    species: str,
    month: int,
    hour: int,
    terrain_v10: dict | None = None,
    corridors_v10: list | None = None,
    affuts_v10: list | None = None,
    contamination_v10: dict | None = None,
    salines_input: list | None = None,   # compat V11 : si fourni, enrichit au lieu de détecter
    enable_autonomous_detection: bool = True,
    enable_generative: bool = False,
) -> list[dict]:
    """
    Retourne les salines enrichies (V11-compat) + salines détectées autonomement
    (X1000). Conserve score_global_v11 pour compatibilité aval.
    """
```

## 14. Contrat de compatibilité

- `engine_salines_v11_supra.py` **reste actif** (scoring sur salines fournies)
- `salines_organic_v1` ajoute la capacité de **détection autonome**
- Sortie strictement backward-compatible (extension de champs)
- `score_global_v11` préservé (aucun consommateur aval cassé)
- Anti-feedback affûts strictement respecté (`test_salines_no_feedback_affuts`)

## 15. Tests anti-régression requis

- `test_salines_organic_autonomous_detection.py` (nouveau)
- `test_salines_organic_multi_species_scoring.py` (nouveau)
- `test_salines_organic_halo_dynamic.py` (nouveau)
- `test_salines_organic_render_compliance.py` (nouveau)
- `test_salines_no_feedback_affuts.py` (existant — doit rester OK)
- `test_salines_always_on.py` (existant — doit rester OK)
- `test_render_salines.py` (existant — doit rester OK)

---

**⏸ EN ATTENTE D'ORDRE COMMANDANT STEEVE-MAX : "VALIDÉ — PROCÉDER À L'IMPLANTATION"**

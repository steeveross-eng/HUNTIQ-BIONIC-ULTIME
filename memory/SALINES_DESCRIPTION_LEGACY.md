# SALINES — DESCRIPTION LEGACY (Pre-Phase M)

> **Engine :** `engine_salines_v11_supra.py`
> **Pilier :** BIO-SYSTEME
> **Statut :** SUPRA (V11) — consommé via bundle, non enregistré via `register_engine`
> **Version :** V11-SUPRA (le plus riche des trois legacy)
> **Capture :** 2026-04-20T22:30:00Z

---

## 1. Logique interne

Engine le plus **sophistiqué** des 3 legacy (432 lignes). Il **enrichit** une liste de salines existantes produite par `compute_salines_omega` avec 5 axes d'évaluation :
- **Biologique** — score par espèce (attraction saisonnière + fenêtres rut/repro + rythmes d'activité)
- **Terrain** — pente, couvert, proximité eau, connectivité
- **Réseau** — centralité dans le réseau corridors/zones
- **Nutrition** — profil fin 600 m (familles de nutriments cibles vs saison/classe physiologique)
- **Accoutumance** — délai d'acclimatation en jours par espèce

## 2. Paramètres

```python
compute_salines_v11_supra(
    salines: list,         # liste entrée (à enrichir)
    terrain_v10: dict,     # profil terrain waypoint
    corridors_v10: list,   # corridors environnants
    affuts_v10: list,      # affûts (pour score_accoutumance)
    contamination_v10: dict,
    species: str,          # cerf / orignal / wapiti
    month: int,
)
```

### Constantes — SPECIES_PROFILES
| Espèce | rayon_m | fenêtres (rut) | accoutumance (jours) | rythmes |
|--------|---------|----------------|----------------------|---------|
| cerf | 650 | 10, 11 | 45 | 5-9h / 17-21h |
| orignal | 900 | 9, 10 | 60 | 4-9h / 18-22h |
| wapiti | 1100 | 9, 10 | 55 | 5-10h / 17-21h |

### Constantes — NUTRIENT_NEEDS (saison × nutriments cibles)
- hiver : énergie, protéines, Na, Ca, Mg
- pré_rut : protéines, P, Ca, oligo_éléments
- rut : énergie, Na, Mg, oligo_éléments
- post_rut : énergie, protéines, Na, P
- printemps : Na, Ca, P, protéines, oligo_éléments
- été : Na, Ca, oligo_éléments

### Constantes — CLASS_NEEDS (classe physiologique)
- femelle_allaitement, femelle_gestation, mâle_croissance_bois, mâle_dominant

## 3. Scoring — 6 sous-scores + score global V11

1. `score_bio_species` (dict par espèce) : combine attraction saisonnière + rythmes horaires
2. `score_bio_global` : moyenne pondérée espèces
3. `score_terrain` : pente × couvert × distance_eau
4. `score_reseau` : centralité corridors (à proximité ?)
5. `score_nutrition` : matching NUTRIENT_NEEDS × saison
6. `score_accoutumance` : délai depuis installation
7. **`score_global_v11`** : pondération institutionnelle (25% bio + 20% terrain + 15% réseau + 20% nutrition + 10% accoutumance + 10% base)

## 4. Dépendances

- `territoire_v10_supra.compute_salines_omega` — génération initiale des salines
- Terrain V10 (bundle)
- Corridors V10 (bundle)
- Affûts V10 (bundle) — uniquement pour `score_accoutumance`, **PAS** pour l'emplacement (directive anti-feedback §Salines)

## 5. Outputs

Chaque saline enrichie :
```json
{
  "lat": ..., "lng": ...,
  "score_bio_species": {"cerf": 74, "orignal": 68, "wapiti": 62},
  "score_bio_global": 68,
  "score_terrain": 82,
  "score_reseau": 71,
  "score_nutrition": 78,
  "score_accoutumance": 90,
  "nutrient_target_profile": {"famille1", "famille2", ...},
  "score_global_v11": 75,
  "statut_institutionnel": "a_optimiser",
  "interdit": false,
  "motif_interdiction": null,
  "recommandations": [...],
  "source": "SALINES-V11-SUPRA"
}
```

## 6. Interactions inter-engines

| Engine | Interaction |
|--------|-------------|
| `ENGINE-NUTRITION-V12-SUPRA` | Consomme `nutrient_target_profile` |
| `engine_affuts.py` | Consomme `score_accoutumance` (via bundle) |
| Anti-feedback : **zero influence depuis affûts sur emplacement saline** (test `test_salines_no_feedback_affuts` scellé) |

## 7. Limites

- **Saline-centric** : suppose que les salines sont déjà placées (ne les génère pas)
- Pas d'IA Vision (ne détecte pas les salines probables visuellement)
- Pas de micro-relief LIDAR (pas de détection de suintements naturels)
- Rythmes horaires figés (plages 4-10h / 17-22h, pas d'adaptation climatique)
- Pas de hiérarchie (toutes les salines traitées au même niveau)
- Pas de rendu gradient (tracé ponctuel simple)

## 8. Faiblesses

- Dépendance forte aux constantes codées en dur (SPECIES_PROFILES, NUTRIENT_NEEDS, CLASS_NEEDS)
- Pas de dynamique pluriannuelle (apprentissage)
- Pas d'adaptation comportementale individuelle (animal marquant)
- Score global pondéré fixe (pas de recalibration automatique)
- Pas d'intégration aux corridors_organic (proximité non utilisée)
- Pas d'attracteurs multi-espèces explicites (un site saline pourrait servir à plusieurs)

## 9. Opportunités (pour optimisation x1000 — Phase M)

- **Biomimétisme** : détection des **suintements naturels** via micro-relief LIDAR + hydrologie (remplace emplacements codés en dur)
- **IA Vision** : reconnaissance visuelle des zones de minéralisation, traces de grattage, chemins d'accès
- **Multi-échelles** : détection sources salines naturelles (dépressions humides, ruisseaux salins, affleurements rocheux)
- **Dynamique saisonnière fine** : adaptation mensuelle vs bi-mensuelle via calibration dynamique
- **Dynamique comportementale** : intégration accoutumance par individu (traces GPS)
- **Modèle prédictif** : anticipation des pics de fréquentation (pré-rut, post-rut, printemps)
- **Modèle génératif** : proposition d'emplacements optimaux non encore exploités
- **Attracteurs multi-espèces** : scoring croisé chevreuil + orignal + wapiti simultané
- **Rendu organique** : halo d'attraction dynamique (rayon × intensité), gradient jaune/doré
- **Réseau intelligent** : connectivité avec corridors_organic (salines = nœuds attractifs)

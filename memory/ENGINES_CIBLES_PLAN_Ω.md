# PLAN ARCHITECTURE CIBLE — ENGINES BIONIC Ω
## PHASE_XI_SUPRA_ENGINES_OPTIMISATION_Ω — X198-SUPRA-PLAN_ENGINES-Ω
## AMENDEMENT-ABSOLU COMMANDANT STEEVE-MAX — 2026-04-22

**CONSTITUTION** : `CONTRAT RENDUΩ — RÉSEAU VEINEUX` (construit à partir de `V7_vs_TERRITOIRE_ACTUEL_DIFF_MATRIX.yaml`).

Chaque engine cible est **canonique, léger, traçable**, au-dessus de `v8_institutional` (V30 LOCKED) et **en amont** du smoother X180.

---

## 1. ENGINE_RÉSEAU_VEINEUX_Ω

| Champ | Valeur |
| --- | --- |
| **Rôle** | Orchestre la topologie du réseau veineux organique : convergence 600 m ±30 %, fusion < 15 m, hiérarchie 5 niveaux CRITIQUE/MAJEUR/FORT/MODERE/FAIBLE, réseau continu (≥ 2 zones vitales) |
| **Entrées V7** | `corridors_v10.scoring` (8-facteurs), `corridors_v10.classifier` (5 niveaux), `species_profiles.py` (affinite_hydro, largeur_corridor_m) |
| **Entrées V20** | `RENDU_OMEGA` (functionalRadius, mainVein*), bundle V30 `corridors` |
| **Entrées V30** | lecture seule `corridors_organic`, `main_veins` |
| **Couches dérivées** | topologie veines (graphe), matrice convergence, jonctions salines |
| **Sorties** | `field:weight_px` (5 niveaux), `field:color_hex`, `field:level` (CRITIQUE→FAIBLE), `field:dash_array`, `graph:vein_topology`, `bool:continuous_network`, `scalar:vein_merge_count` |
| **Impact smoother X180** | Injecte `hierarchy_level` + `target_width_m` dans chaque corridor avant passes 7-8 ; force rejet si `continuous_network == false` |
| **Stratégie réduction MB** | Tables compactes de seuils (5 niveaux = 5 tuples), pas de recalcul scoring ; consomme les scores de `ENGINE_BIO_SCORING_Ω` |
| **Poids cible** | ≤ 40 KB, 3-4 fichiers (`router.py`, `topology.py`, `hierarchy.py`, `__init__.py`) |
| **Chemin** | `/app/backend/engines/reseau_veineux_omega/` |
| **Endpoint** | `/api/v7-ultime/reseau-veineux/compute` (PRO/EXPERT, lecture seule) |

---

## 2. ENGINE_ECO_ZONES_Ω

| Champ | Valeur |
| --- | --- |
| **Rôle** | Produit la carte unifiée des zones écologiques et attracteurs : 4 niveaux habitat (OPTIMAL/FONCTIONNEL/DÉGRADÉ/INUTILISABLE), 6 types vitaux (salines 20-sources, alimentation, repos, rut, thermique, humide), centre + polygone + pondérations saisonnières |
| **Entrées V7** | `salines_ultime_engine` (5 scores × 20 sources), `nutrition_engine_v7` (Sol→Nutriments→Fourrage→Gibier), `repos_v1`, `alimentation_v1/v2`, `species_profiles.saisonnalite` |
| **Entrées V20** | `OMEGA_FILTERS_SPEC.HABITAT_AWARE_Ω`, bundle V30 `zones`, `salines` |
| **Entrées V30** | lecture seule `vital_zones`, `salines[]` |
| **Couches dérivées** | raster attractivité par type, polygones habitat, centroïdes |
| **Sorties** | `raster:attractivity[lat,lng,type]`, `list:vital_zones[{type, center, weight, season_modifier}]`, `field:habitat_class` (4 niveaux), `list:saline_sources[20]` hiérarchisés |
| **Impact smoother X180** | Remplace la liste plate `vital_zones[]` dans `smooth_bundle` par une liste hiérarchisée ; active la règle « ≥ 2 zones vitales » contrôlée par `ENGINE_RÉSEAU_VEINEUX_Ω` |
| **Stratégie réduction MB** | **Fusion** `alimentation_v1+v2+v4` + `repos_v1` + `salines_ultime_engine` + `saline_engine` sous une façade unique ; **caches TTL 24h** sur attractivité par biome |
| **Poids cible** | ≤ 120 KB, 6-8 fichiers |
| **Chemin** | `/app/backend/engines/eco_zones_omega/` |
| **Endpoint** | `/api/v7-ultime/eco-zones/compute` (PRO/EXPERT) |

---

## 3. ENGINE_BIO_SCORING_Ω

| Champ | Valeur |
| --- | --- |
| **Rôle** | Calcule le score biologique 0-100 selon les 8 facteurs V7 ULTIME, ré-appliqué en post-V30 sans toucher au moteur scellé. Expose `cost_surface`/`ecl`/`canopy_density` en lecture seule via une **façade-miroir** (voir §7). |
| **Entrées V7** | `corridors_v10.scoring.score_single_corridor` (ECL 25, canopy 20, pression humaine 15, nourriture+refuge 15, topo+hydro 10, regen 5, cost 10, bonus diversité ×1.05, modifs court/long) |
| **Entrées V20** | bundle V30 `fused_behavioral_probability` (cellulaire), `terrain_multiscale` |
| **Entrées V30** | lecture seule **miroir** (voir §7) : `cost_surface`, `ecl`, `canopy_density` — exposés sans modifier V30 |
| **Couches dérivées** | scoring per-cell 0-100, classification 5 niveaux, modifs longueur |
| **Sorties** | `scalar:score_0_100`, `enum:level`, `dict:subscores{ecl, canopy, human, food_refuge, topo_hydro, regen, cost, bonus}`, `raster:cell_score` |
| **Impact smoother X180** | Fournit `hierarchy_intensity` à `ENGINE_RÉSEAU_VEINEUX_Ω` ; branche `ecl`/`canopy`/`cost` comme weights `ia_signals.attractors`/`exclusions` |
| **Stratégie réduction MB** | **Table des poids** 8 entrées ; pipeline pur fonction (stateless) ; pas de persistance |
| **Poids cible** | ≤ 60 KB, 4-5 fichiers (`router.py`, `scoring_8_factors.py`, `v30_mirror_read_only.py`, `__init__.py`) |
| **Chemin** | `/app/backend/engines/bio_scoring_omega/` |
| **Endpoint** | `/api/v7-ultime/bio-scoring/compute` (PRO/EXPERT) |

---

## 4. ENGINE_HYDRO_TOPO_Ω

| Champ | Valeur |
| --- | --- |
| **Rôle** | Unifie signaux hydrologiques et topologiques pour le smoother et `ENGINE_BIO_SCORING_Ω`. Gère l'INVERSION SÉMANTIQUE hydro : attraction graduée selon `affinite_hydro` par espèce (au lieu du repoussement absolu X180). |
| **Entrées V7** | `corridors_v10.scoring.pct_hydro`, `pct_vallon`, `tampon_count`, `species_profiles.affinite_hydro`, `hydro_v1` |
| **Entrées V20** | `renduOmegaStore.terrainBoosts` (slope_high 0.20, valley 0.30, wet 0.25, transition 0.15) |
| **Entrées V30** | lecture seule `terrain_multiscale` (DEM 1m/5m/10m), `water_points`, `steep_slope_points` |
| **Couches dérivées** | raster coût topo, raster attractivité hydro graduée, couche lisières/tampons |
| **Sorties** | `raster:slope_cost`, `raster:hydro_attract[species]`, `list:valley_polylines`, `list:buffer_edges`, `scalar:micro_topo_score` |
| **Impact smoother X180** | Remplace la passe 5 `apply_ecological_alignment` répulsive par une passe **attractive-bornée** selon `affinite_hydro` |
| **Stratégie réduction MB** | **Tables par espèce** (CERF 0.60, ORIGNAL 0.85, …) ; **caches** sur DEM tuilés ; réutilise `terrain_multiscale` sans re-calculer |
| **Poids cible** | ≤ 80 KB, 5-6 fichiers |
| **Chemin** | `/app/backend/engines/hydro_topo_omega/` |
| **Endpoint** | `/api/v7-ultime/hydro-topo/compute` (PRO/EXPERT) |

---

## 5. HIÉRARCHIE DE LA CONSTITUTION

```
┌──────────────────────────────────────────────────────┐
│  CONTRAT RENDUΩ — RÉSEAU VEINEUX (constitution)      │
│  Source : V7_vs_TERRITOIRE_ACTUEL_DIFF_MATRIX.yaml   │
└──────────────────────┬───────────────────────────────┘
                       │
          ┌────────────┼────────────┬─────────────┐
          ▼            ▼            ▼             ▼
   ┌──────────┐  ┌─────────┐  ┌──────────┐  ┌──────────┐
   │ ENGINE_  │  │ ENGINE_ │  │ ENGINE_  │  │ ENGINE_  │
   │ RÉSEAU_  │  │ ECO_    │  │ BIO_     │  │ HYDRO_   │
   │ VEINEUX_Ω│  │ ZONES_Ω │  │ SCORING_Ω│  │ TOPO_Ω   │
   └────┬─────┘  └────┬────┘  └────┬─────┘  └────┬─────┘
        │             │            │             │
        └─────────────┴────────────┴─────────────┘
                           │
                           ▼
               ┌───────────────────────┐
               │ post_smoothing/       │
               │ organic_corridor_     │
               │ smoother (X180)       │
               │ — consommateur unique │
               └───────────────────────┘
                           │
                           ▼
               ┌───────────────────────┐
               │ V30 LOCKED engine_ia_ │
               │ corridors_organic_    │
               │ omega (lecture seule) │
               └───────────────────────┘
```

---

## 6. RÉDUCTION DE POIDS VISÉE

| Zone | Avant | Après cible | Économie |
| --- | --- | --- | --- |
| `modules/bionic_engine_p0/` | 3 073 KB / 210 .py | 2 400 KB / 160 .py (extraction routers) | −673 KB |
| Fusion alimentation v1+v2+v4 | 146.8 KB / 21 .py | 80 KB / 8 .py | −66.8 KB |
| Fusion salines (saline + salines_ultime + engine_salines) | 123.7 KB / 16 .py + 18.2 KB + 25 lignes | 70 KB / 6 .py | −71.9 KB |
| Purge DEPRECATED (`corridor_unified`, `relocation`) | 55.7 KB / 8 .py | 0 | −55.7 KB |
| **TOTAL ÉCONOMIE** | | | **~867 KB** (-15 %) |

**Nouveaux engines ajoutés** : ~300 KB (≤ 40 + ≤ 120 + ≤ 60 + ≤ 80).

**Net** : réduction effective estimée **~567 KB (-10 %)** tout en gagnant une architecture canonique.

---

## 7. STRATÉGIE D'EXPOSITION V30 (§5 directive X198)

### 7.1 Contrainte
V30 est scellé SHA-256 `27516c96…`. **Toute modification = violation BCE-4X**.

### 7.2 Proposition : Façade-Miroir Lecture Seule

1. **Création d'un module non-V30** : `/app/backend/engines/bio_scoring_omega/v30_mirror_read_only.py`
2. **Principe** : importer dynamiquement les fonctions pures de `engine_ia_corridors_organic_omega` **sans modifier le fichier**, et exposer leurs retours sous forme de raster/dict en lecture seule :

```python
# PSEUDO-CODE conceptuel (à implémenter en X200 uniquement)
from engines.v8_institutional import engine_ia_corridors_organic_omega as v30

def mirror_cost_surface(lat, lon, species):
    """Appelle la fonction pure V30 sans modifier V30."""
    fn = getattr(v30, '_compute_cost_surface', None)
    if fn is None:
        return {"available": False, "reason": "v30_private_fn_unavailable"}
    raw = fn(lat=lat, lon=lon, species=species)
    return {"available": True, "cost_surface": raw, "readonly": True,
            "v30_sha256": V30_SHA256}
```

3. **Garanties** :
   - Aucune écriture dans V30
   - Le hash SHA-256 de V30 reste inchangé (vérifié par `registry_lock_omega`)
   - Exposition contrôlée par rôle PRO/EXPERT uniquement
   - Cache TTL 60 s pour limiter les appels

### 7.3 Validation de conformité
- Tests Pytest dédiés : `test_v30_mirror_non_intrusive.py` vérifient que le SHA-256 de `engine_ia_corridors_organic_omega.py` est identique avant et après tout appel miroir.
- Test d'intégrité signalé dans `registry_lock_omega.py`.

### 7.4 Alternative (si la fonction V30 est inaccessible)
Si V30 n'expose aucune fonction pure pour `cost_surface`/`ecl`/`canopy_density`, proposer :
- Endpoint `/api/v7-ultime/bio-scoring/request-v30-exposure` qui journalise la demande.
- Le Commandant peut alors ordonner une **Phase de scellement complémentaire** où V30 serait re-scellé avec un SHA-256 différent après ajout de *lecteurs purs publics* (en dernier recours).

---

## 8. FEUILLE DE ROUTE X200 (sous votre ordre)

1. Créer les 4 packages engines cibles (squelettes FastAPI + tests)
2. Brancher sources V7 rapatriées → engines cibles
3. Modifier `smooth_bundle` pour consommer les 4 engines au lieu du bundle V30 brut
4. Activer endpoints HTTPS PRO/EXPERT-only (token)
5. Déployer façade-miroir V30 lecture seule
6. Mettre en place suite Pytest 9 passes X180 + nouveaux engines
7. Valider CI_STATUS_Ω sentinelles 65/65 + nouveaux tests
8. **Autorisation visuelle requise du Commandant** avant tout rendu

---

## 9. GARDE-FOUS X198 RESPECTÉS

- ✅ Engine V30 **non modifié**
- ✅ Panneau DIAGNOSTIC-CORRIDORS-Ω **non activé** (inchangé depuis X197)
- ✅ X200 **non lancé** (plan uniquement)
- ✅ Endpoints futurs **PRO/EXPERT-only**
- ✅ Sans rendu visuel

— FIN PLAN ARCHITECTURE CIBLE —

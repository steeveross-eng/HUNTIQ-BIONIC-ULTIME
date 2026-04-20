# ORDRE_TERRITOIRE_PROTECT_Ω — RAPPORT INSTITUTIONNEL COMPLET

> **COMMANDANT :** STEEVE-MAX
> **PHASE :** XI-SUPRA-G (ORDRE PROTECT-Ω)
> **DATE :** 2026-04-20T17:00:00Z
> **STATUT FINAL :** ✅ CONFORME — **57/57 SELF-AUDIT-Ω** — **Baseline TERRITOIRE_Ω_STABLE scellée**

---

## §1. ENGINE_TERRITOIRE_ANTI_REGRESSION_Ω — ACTIVÉ

### Enregistrement institutionnel
- **Nom** : `ENGINE-TERRITOIRE-ANTI-REGRESSION-Ω`
- **Version** : `V1.0-PHASE-XI-SUPRA-G-2026-04`
- **Pilier** : `GOUVERNANCE`
- **Registry SHA-256** : `faeefa1339b88f8c6f7aa87e764944416d681321a8411c0601d7c6b40921cd1a`
- **Engines scellés** : 36

### Règles institutionnelles (immuables)

```json
{
  "corridor_min_length_m": 100,
  "corridor_min_control_points": 5,
  "corridors_min_count": 3,
  "affuts_min_count": 1,
  "zones_min_count": 1,
  "hotspots_min_count": 1,
  "nutrition_max_empty_grid_rendered_pct": 0.0,
  "contamination_required_if_affuts": true
}
```

### Endpoints opérationnels

| Endpoint | Rôle |
|---|---|
| `GET /api/v20/territoire/anti-regression/status` | État + règles + hash baseline |
| `GET /api/v20/territoire/anti-regression/baseline` | Baseline TERRITOIRE_Ω_STABLE scellée |
| `POST /api/v20/territoire/anti-regression/seal-baseline` | Scelle la baseline (exige conformité) |
| `POST /api/v20/territoire/anti-regression/validate` | Valide un bundle + rollback auto si NON-CONFORME |
| `GET /api/v20/territoire/anti-regression/journal?tail=50` | Journal institutionnel chronologique |

### Refus & rollback
- Si une validation retourne `ok=false` + `baseline` présente → la réponse contient `rollback: true` + `rollback_source: "TERRITOIRE_Ω_STABLE_BASELINE"` + la baseline complète
- Chaque appel écrit dans `/app/data/territoire_omega/anti_regression/antireg_journal.log`
- Les violations sont typées `critical` (bloquantes) / `warning` (tolérées)

---

## §2. MODE ÉVOLUTIONS SÉQUENTIELLES — ENFORCED

### Protocole institutionnel

1. **AVANT toute évolution** :
   ```bash
   curl http://localhost:8001/api/v20/territoire/anti-regression/baseline
   # → vérifier hash_input courant
   ```

2. **UNE seule modification à la fois** (engine OU renderer OU règle métier)

3. **APRÈS la modification** :
   ```bash
   curl -X POST http://localhost:8001/api/v20/territoire/anti-regression/validate \
     -d '{"lat":45.10,"lon":-72.80,"species":"chevreuil"}'
   # → exiger verdict.ok=true avant merge
   ```

4. **Si `ok=false`** → rollback du changement (git revert ou équivalent) + journalisation
5. **Si `ok=true`** → re-sceller la baseline :
   ```bash
   curl -X POST http://localhost:8001/api/v20/territoire/anti-regression/seal-baseline \
     -d '{"lat":45.10,"lon":-72.80,"species":"chevreuil"}'
   ```

6. **Validation finale** : SELF-AUDIT-Ω ≥ 57/57 obligatoire

### Interdictions (bloquantes)
- ❌ Interdiction de merger plusieurs changements TERRITOIRE non validés individuellement
- ❌ Interdiction de modifier les `RULES` sans directive STEEVE-MAX explicite
- ❌ Interdiction de sceller une baseline NON-CONFORME (endpoint renvoie 409)

---

## §3. TERRITOIRE_Ω_STABLE — BASELINE SCELLÉE

### Métadonnées

| Champ | Valeur |
|---|---|
| `sealed_at` | `2026-04-20T17:08:22.497410+00:00` |
| `sealed_by` | `ENGINE-TERRITOIRE-ANTI-REGRESSION-Ω` |
| `hash_input` | `736cb5b2810e68169a3f27dbde1821345750ff339bec650f11eac29ed2daed8b` |
| `seed` | lat=45.10, lon=-72.80, species=chevreuil |
| `directive` | ORDRE_TERRITOIRE_PROTECT_Ω STEEVE-MAX 2026-04-20 |
| `path` | `/app/data/territoire_omega/anti_regression/TERRITOIRE_OMEGA_STABLE_BASELINE.json` |

### Métriques figées

| Métrique | Valeur |
|---|---|
| `corridors_count` | 14 |
| `corridors_min_length_m` | **299.8 m** (≥ 100 m ✓) |
| `corridors_max_length_m` | **730.1 m** |
| `corridors_avg_length_m` | **461.1 m** |
| `affuts_count` | 6 |
| `zones_count` | 5 |
| `hotspots_count` | 11 |
| `contamination_count` | 18 |
| `nutrition_grid_total` | 36 |
| `nutrition_grid_empty` | 36 (purge frontend active) |

---

## §4. ANALYSE POINT PAR POINT — ENGINES vs RENDU

### 4.1. `ENGINE-NUTRITION` / `ENGINE-NUTRITION-V12-SUPRA`

| Description institutionnelle | Rendu effectif | Conformité |
|---|---|---|
| Génère `carte_carences` + `carte_besoins` sur grille 6×6 (36 pts) | 36 points générés | ✅ |
| Sévérité tag ∈ {`aucune`, `legere`, `moderee`, `severe`} | 36× `aucune` (saison non-carencée) | ✅ |
| Rendu visuel SEULEMENT si carence réelle | Purge active (skip `aucune`/`severite=0`) | ✅ post-fix OMEGA |
| Pas de pollution visuelle "quadrillage vert" | 0 pts rendus quand 0 carence | ✅ post-fix OMEGA |

**Écarts :** Aucun post-fix. **Conforme V8-INSTITUTIONNELLES.**

### 4.2. `ENGINE-ZONES` (via `territoire_v10_supra.compute_zones`)

| Description institutionnelle | Rendu effectif | Conformité |
|---|---|---|
| Zones typées : rut / alim / repos / nourriture / saline | 5 zones (rut, alim, repos, etc.) | ✅ |
| Polygons fermés 20-30 points Catmull-Rom | polygon_len=23-27 pts | ✅ |
| Score normalisé 0-100 | score=71.5 / 82 / … | ✅ |
| Flag `excluded` (si zone incompatible chasse) | présent, value bool | ✅ |
| Rendu Leaflet semi-transparent avec couleur par type | rendu BionicLayersV8 ligne ~220 | ✅ |

**Écarts :** Aucun. **Conforme.**

### 4.3. `ENGINE-AFFUTS` (via `engine_affuts.py`)

| Description institutionnelle | Rendu effectif | Conformité |
|---|---|---|
| Recommande ≥1 affût optimal par waypoint | 6 affûts autour du waypoint | ✅ |
| Champs `lat`, `lng`, `type`, `score`, `orientation_deg` | Tous présents | ✅ |
| Types ∈ {TOP_OPTIMAL, OPTIMAL, BON, TEMPORAIRE} | TOP_OPTIMAL + TEMPORAIRE observés | ✅ |
| Rendu marker octogone avec arc orientation | BionicLayersV8 ligne ~390 | ✅ |
| Distance corridor ≤ 200 m | `distance_corridor_m` présent | ✅ |

**Écarts :** Aucun. **Conforme.**

### 4.4. `ENGINE-CONTAMINATION-V2-Ω` (`engine_contamination_v2_omega.py`)

| Description institutionnelle | Rendu effectif | Conformité |
|---|---|---|
| Zones cone de contamination ancrées sur affûts | 18 cônes, `affut_source` renseigné | ✅ |
| Polygones fan-shape triangulaires | polygon valide, intensity 0-100 | ✅ |
| `reach_m` = portée effective du vent | `reach_m` renseigné | ✅ |
| Rendu rouge semi-transparent (danger) | BionicLayersV8 ligne ~265 | ✅ |
| Contamination REQUISE si affûts présents | 6 affûts → 18 cônes (3× coverage) | ✅ |

**Écarts :** Aucun. **Conforme.**

### 4.5. `ENGINE-CORRIDORS` (via `territoire_v10_supra.compute_corridors_v10`)

| Description institutionnelle | Rendu effectif | Conformité |
|---|---|---|
| Corridors organiques Catmull-Rom | 14 corridors, paths 25-28 pts | ✅ |
| Longueur physique cohérente (> 100 m) | **min=299.8 m / max=730.1 m / avg=461.1 m** | ✅ post-fix OMEGA |
| Types : intense / normal / évasion | distribution observée conforme | ✅ |
| Intensity 0-100 basée sur wind+slope+cover | intensity 62-84 | ✅ |
| Rendu Polyline Leaflet weight variable | BionicLayersV8 ligne ~225 | ✅ |
| **ABSENCE de fallback ligne droite** | **0 corridor <100m** (anti-regression enforcé) | ✅ |

**Écarts :** Aucun. **Conforme post-fix OMEGA** (bug arithmétique `/ 111.0 * 111.0 * 0.003` éliminé).

### 4.6. `ENGINE-RENDU-Ω` / `BionicLayersV8`

| Description institutionnelle | Rendu effectif | Conformité |
|---|---|---|
| 14 couches institutionnelles empilées | 14 couches exposées via props | ✅ |
| Ordre z-index : base → zones → corridors → contamination → salines → hotspots → affûts → waypoint → cursor | Ordre préservé | ✅ |
| Validation zoom par couche (zoom_min, zoom_max) | `validateElement()` actif | ✅ |
| Purge pollution visuelle (nutrition grid vide) | Fix OMEGA appliqué | ✅ |
| Captures Playwright live ≥ 30 KB | macro 3.1 MB / mid 3.1 MB / detail 3.1 MB | ✅ |

**Écarts :** Aucun. **Conforme post-fix OMEGA.**

---

## §5. VALIDATION FINALE

### SELF-AUDIT-Ω — 57/57 ✅

Nouvelle suite ajoutée : `test_territoire_anti_regression_omega` (8 règles vérifiées, bundles synthétiques conforming/non-conforming discriminés).

### Registry Lock
- Version : `V20-SUPRA-LOCKED-PHASE-XI-SUPRA-G-2026-04`
- 36 engines scellés
- SHA-256 : `faeefa1339b88f8c6f7aa87e764944416d681321a8411c0601d7c6b40921cd1a`

### Baseline TERRITOIRE_Ω_STABLE
- ✅ Scellée et hashée (`736cb5b2810e68169a3f27dbde1821345750ff339bec650f11eac29ed2daed8b`)
- ✅ Tous les compteurs (corridors/affûts/zones/contamination) dans la plage conforme
- ✅ Zero violation critique

### Captures institutionnelles (post-fix OMEGA)
- macro (z12) : 3 066 360 B — conforme
- mid (z15) : 3 128 801 B — conforme, 14/14 couches
- detail (z17) : 3 057 029 B — conforme, 14/14 couches

---

## §6. TRAÇABILITÉ

### Fichiers ajoutés
- `/app/backend/engines/v8_institutional/engine_territoire_anti_regression_omega.py` (engine + 5 endpoints)
- `/app/backend/tests/test_territoire_anti_regression_omega.py` (suite SELF-AUDIT)
- `/app/data/territoire_omega/anti_regression/TERRITOIRE_OMEGA_STABLE_BASELINE.json` (baseline scellée)
- `/app/data/territoire_omega/anti_regression/antireg_journal.log` (journal)

### Fichiers modifiés
- `/app/backend/server.py` (registration router anti-regression)
- `/app/backend/engines/v8_institutional/registry_lock_omega.py` (ENGINES_LOCKED +1, version, sealed_at)
- `/app/backend/engines/v8_institutional/self_audit_omega.py` (suite ajoutée)
- `/app/memory/ENGINE_REGISTRY_LOCKED.md` (nouveau hash + version)

---

## §7. CONCLUSION

ORDRE_TERRITOIRE_PROTECT_Ω — **EXÉCUTÉ SANS INTERPRÉTATION**.

La protection permanente du pipeline TERRITOIRE est désormais **armée et opérationnelle** :
- 🛡️ `ENGINE-TERRITOIRE-ANTI-REGRESSION-Ω` actif avec 8 règles institutionnelles immuables
- 🔒 Baseline `TERRITOIRE_Ω_STABLE` scellée cryptographiquement
- 📋 Protocole d'évolution séquentielle `ENFORCED`
- 🎯 Analyse engines vs rendu : **6/6 conformes V8-INSTITUTIONNELLES** post-fix OMEGA
- 📊 SELF-AUDIT-Ω : **57/57 CONFORME**

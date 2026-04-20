# ENGINE CORRIDORS-Ω — MISE À JOUR COMPLÈTE (RAPPORT PHASE XI-SUPRA-H)

> **COMMANDANT :** STEEVE-MAX
> **DATE :** 2026-04-20T18:00:00Z
> **STATUT FINAL :** ✅ CONFORME — **58/58 SELF-AUDIT-Ω** — **VERSION Ω verrouillée institutionnellement**

---

## 1. ARCHIVAGE — OLD DESCRIPTIONS MARQUÉES « ARCHIVE — NON ACTIVE »

Déplacé dans `/app/memory/_ARCHIVE_NON_ACTIVE/` avec marqueur obligatoire :

```
AFFUTS_CORRIDOR_500_REPORT.md
AFFUTS_CORRIDOR_FIRST_REPORT.md
AFFUTS_CORRIDOR_SECOND_REPORT.md
AFFUTS_CORRIDOR_X1M_REPORT.md
AFFUTS_CORRIDOR_X1M_REPORT_LUC.md
AUDIT_CORRIDORS_EAU_x7200.md
README_ARCHIVE_NON_ACTIVE.md
```

Directive appliquée : aucune de ces descriptions ne peut être consultée pour
générer, évaluer ou valider des corridors dans BIONIC OS V20-SUPRA.

## 2. DESCRIPTION OFFICIELLE & FINALE — VERSION Ω

Document scellé : `/app/memory/ENGINE_CORRIDORS_OMEGA_OFFICIAL_FINAL.md`

Contenu :
- §0 Identité fondamentale IA-assistée
- §1 Spécificité par espèce — IA Vision + IA-CORRIDORS
- §2 Flux animal réel IA (pas affûts, pas ligne de tir, pas route)
- §3 **ENGINE IA-CORRIDORS** (section interne obligatoire)
- §4 Structures naturelles
- §5 Géométrie : Catmull-Rom, rayon 600 m ± 30 %, largeur 2–10 m
- §6 Contraintes officielles validées par IA-CORRIDORS
- §7 Synthèse ultime
- §8 Verrouillage institutionnel

**Règle d'or :** *« un corridor = une espèce = une logique »*.

## 3. ENGINE IA-CORRIDORS-Ω — CRÉÉ ET ACTIVÉ

Fichier : `/app/backend/engines/v8_institutional/engine_ia_corridors_omega.py`

Responsable de :
- **Analyse** : topologie / hydrologie / écologie / comportement / besoins naturels
- **Intégration** : IA Vision + données terrain
- **Cartes produites** : coût / probabilité comportementale / flux animal réel / attractivité biologique
- **Génération + optimisation** du réseau complet
- **Validation** biologique/écologique/terrain-aware avant publication

Endpoints :
| Route | Rôle |
|---|---|
| `GET /api/v20/territoire/ia-corridors/status` | Contraintes officielles + version |
| `POST /api/v20/territoire/ia-corridors/validate` | Validation d'un set de corridors + waypoint |
| `POST /api/v20/territoire/ia-corridors/validate-live` | Fetch bundle + validate en temps réel |

Contraintes appliquées (extraites de `CONSTRAINTS`) :
```json
{
  "segment_max_m": 20.0,
  "angle_max_deg": 45.0,
  "functional_radius_min_m": 420.0,
  "functional_radius_max_m": 780.0,
  "ecological_width_min_m": 2.0,
  "ecological_width_max_m": 10.0,
  "min_control_points": 5,
  "single_species_per_corridor": true,
  "forbid_affut_references": true,
  "network_connectivity_max_gap_m": 150.0
}
```

## 4. MISE À JOUR TRANSVERSALE DES SECTIONS

| Section | Ancienne | Nouvelle (VERSION Ω) |
|---------|----------|----------------------|
| Identité fondamentale | Générateur Catmull-Rom + RSF/SSF | **IA-assistée via IA-CORRIDORS** |
| Spécificité par espèce | Profil hardcodé `SPECIES_PROFILES` | **IA Vision + IA-CORRIDORS** |
| Ce que matérialise | Flux animal supposé | **Flux animal réel IA** |
| Structures naturelles | Inférées par seeds | **Analysées par IA-CORRIDORS** |
| Géométrie | Catmull-Rom subs=3, dist aléatoire | **Générée/optimisée par IA-CORRIDORS, rayon 600m±30%** |
| Contraintes | Slope + eau | **10 contraintes validées par IA-CORRIDORS** |
| Synthèse ultime | Moteur autonome | **IA-assistée CORRIDORS-Ω** |

## 5. SUPPRESSION DES RÉFÉRENCES AFFÛTS

Vérification exhaustive effectuée dans :
- `engine_corridors.py` → 0 référence
- Section CORRIDORS (lignes 190-290) de `territoire_v10_supra.py` → 0 référence (seules les annotations "aucune référence aux affûts" en commentaire directive)
- `engine_ia_corridors_omega.py` → règle `forbid_affut_references: true` active

## 6. ANTI-RÉGRESSION CORRIDORS — ACTIVÉE

Règles ajoutées à `ENGINE-TERRITOIRE-ANTI-REGRESSION-Ω` :
```json
{
  "corridor_segment_max_m": 20.0,
  "corridor_angle_max_deg": 45.0,
  "corridor_functional_radius_min_m": 420.0,
  "corridor_functional_radius_max_m": 780.0,
  "corridor_single_species": true,
  "corridor_forbid_affut_ref": true
}
```

Double protection :
1. **Filtre en génération** : `compute_corridors_omega()` appelle
   `filter_conforme_corridors()` de IA-CORRIDORS avant `return corridors`
2. **Validation post-publication** : `POST /anti-regression/validate`
   rejette tout bundle non-conforme + rollback baseline

## 7. IMPACT SUR LE BUNDLE LIVE

| Métrique | Avant VERSION Ω | Après VERSION Ω |
|----------|-----------------|-----------------|
| Corridors count | 15 | **11** (filtrage strict) |
| Min length | 299.8 m | **429.8 m** (≥ 420 m ✓) |
| Max length | 730.1 m | **727.2 m** (≤ 780 m ✓) |
| Avg length | 461.1 m | **545.4 m** |
| Segments > 20 m | toléré | **0** |
| Angles > 45° | toléré | **0** |
| Ref affût | toléré | **0** |
| Isolés | toléré | **0** (gap ≤ 150 m) |
| Species mix | unique par défaut | **unique enforcé** (`['chevreuil']`) |

## 8. VERROUILLAGE INSTITUTIONNEL

- **Registry lock** : `V20-SUPRA-LOCKED-PHASE-XI-SUPRA-H-2026-04`
- **SHA-256 registre** : `806c014489712364541326be1b12d112b60a30a7e4c84723b0f3bc5d042fd159`
- **Engines scellés** : 37
- **TERRITOIRE_Ω_STABLE baseline re-scellée** : hash `b1e4ac555a83a1f9730c50817f83dffc859f42dc6bb2c6e58d5111520e641b13`
- **SELF-AUDIT-Ω** : 58/58 ✅ CONFORME

## 9. TRAÇABILITÉ

### Fichiers créés
- `/app/memory/ENGINE_CORRIDORS_OMEGA_OFFICIAL_FINAL.md` (norme institutionnelle unique)
- `/app/memory/_ARCHIVE_NON_ACTIVE/README_ARCHIVE_NON_ACTIVE.md`
- `/app/backend/engines/v8_institutional/engine_ia_corridors_omega.py`
- `/app/backend/tests/test_ia_corridors_omega.py`
- `/app/memory/ENGINE_CORRIDORS_OMEGA_UPDATE_REPORT.md` (ce rapport)

### Fichiers modifiés
- `/app/backend/server.py` (registration IA-CORRIDORS router)
- `/app/backend/engines/v8_institutional/registry_lock_omega.py` (37 engines, version H)
- `/app/backend/engines/v8_institutional/self_audit_omega.py` (suite ajoutée → 58 total)
- `/app/backend/engines/v8_institutional/territoire_v10_supra.py` (rayon 420-780m, subs=8, filter_conforme_corridors)
- `/app/backend/engines/v8_institutional/engine_territoire_anti_regression_omega.py` (+ 6 règles corridors)
- `/app/memory/ENGINE_REGISTRY_LOCKED.md` (hash + version H)
- `/app/memory/TERRITOIRE_VISUAL_PROOF_LIVE/` (captures re-générées post VERSION Ω)

---

## CONCLUSION

ENGINE CORRIDORS-Ω **VERSION Ω** est désormais la **norme institutionnelle unique et
obligatoire** pour TERRITOIRE BIONIC OS V20-SUPRA. Toute tentative de génération
ou de publication qui dévie de cette norme est rejetée automatiquement, quantifiée
et journalisée. Les anciennes descriptions sont archivées de manière permanente.

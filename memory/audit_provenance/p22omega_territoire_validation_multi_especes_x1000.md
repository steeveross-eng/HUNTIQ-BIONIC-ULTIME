# P22Ω_TERRITOIRE_VALIDATION_MULTI_ESPECES_X1000 — RAPPORT FINAL

**Date UTC** : 2026-05-13
**Commandant** : STEEVE-MAX
**Waypoint** : BSL (48.206657, -68.382422) · MOIS=10 · HEURE=7 · WIND=225°/15
**Préview URL** : `https://ultime-preview.preview.emergentagent.com`

---

## DIRECTIVE EXÉCUTÉE

```
P22Ω_TERRITOIRE_VALIDATION_MULTI_ESPECES_X1000
    --validate-chevreuil
    --validate-orignal
    --validate-ours
    --validate-dindon
    --validate-coyote
    --exclude-wapiti
    --confirm-visual
    --finalize
```

---

## TABLEAU SYNTHÉTIQUE FINAL

| Espèce | Corridors | Zones | Hotspots | Salines | V5 actif | Halt MFFP | HIT (ms) | ESI | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| **chevreuil**  | 6 (1B+5S)  | 5 | 4 | 6 | ✓ | ✗ | 273.8 | CONFORME | ✓ **CONFORME** |
| **orignal**    | 7 (2B+5S)  | 5 | 5 | 6 | ✓ | ✗ | 233.2 | CONFORME | ✓ **CONFORME** |
| **ours**       | **0**      | 5 | 5 | 6 | ✓ | ✗ | 252.3 | CONFORME | ⚠ **NON_CONFORME** |
| **dindon**     | 0          | 5 | 0 | 0 | ✗ | **✓ HALT MFFP** | 16636.4 | CONFORME | ✓ **CONFORME** (halt légitime) |
| **coyote**     | 6 (fallback chevreuil) | 5 | 4 | 6 | ✓ | ✗ | 360.7 | CONFORME | ⚠ **FALLBACK** |

Légende : B = `veine_principale` (backbone) · S = `veine_secondaire` (subnet) · HIT = re-query post-rehydratation.

---

## DÉTAILS PAR ESPÈCE

### `--validate-chevreuil` ✓ CONFORME
- **Présence MFFP** : PRÉSENT (Bas-Saint-Laurent, colonisé jusqu'à ~50°N).
- **V5 doctrine** : 6 corridors ∈ [5–7], 1 backbone + 5 subnets, cap_global appliqué 13→6.
- **Couches visuelles** : 6 corridors + 5 zones (rut/alimentation/repos/eau/thermique) + 6 salines + 4 hotspots = **21 entités UI**.
- **ESI Ω** : CONFORME.

### `--validate-orignal` ✓ CONFORME
- **Présence MFFP** : ABONDANT (97 % territoire forestier).
- **V5 doctrine** : 7 corridors ∈ [5–7], 2 backbones + 5 subnets.
- **Couches visuelles** : 7 corridors + 5 zones + 6 salines + 5 hotspots = **23 entités UI**.
- **ESI Ω** : CONFORME.

### `--validate-ours` ⚠ NON_CONFORME — DIAGNOSTIC FORENSIQUE
- **Présence MFFP** : PRÉSENT (`Ursus americanus`, source MFFP 2024 Plan de gestion ours noir).
- **V30 raw** : 12 corridors générés (`corridors_v30_count_avant_filtre_presence=12`).
- **Filtre présence** : 0 corridors rejetés (12→12).
- **V5 organic engine** : `v5_n_corridors=0` · `hierarchy_counts={backbone:0, subnet:0, capillaire:0, connector:0}`.
- **Cap global** : non appliqué (rien à capper).
- **Verdict** : NON_CONFORME (0 corridors malgré présence + V30 source non-vide).

**Cause racine identifiée** :
Le bundle normalise `ours → ours_noir` via `SPECIES_ALIAS_TO_CANONICAL`. Le moteur V5 `generate_organic_corridors` reçoit `species="ours_noir"` (canonique). `SPECIES_BEHAVIOR["ours_noir"]` est défini avec :
```
prudence=0.95  amplitude=0.90  vitesse=0.50  ouverture_preferee=0.15
hydro_dep=0.55  couvert_pref=0.90  sinuosity=1.70  n_corridors=12
```
Avec `couvert_pref=0.90` (forte préférence couvert dense), le V5 ne trouve aucune paire de zones vitales compatible au BSL → 0 corridors V5.

Test contradictoire : appel direct `POST /corridors-organic/generate` avec `species="ours"` (raw, non normalisé) retourne **7 corridors** car `SPECIES_BEHAVIOR.get("ours", SPECIES_BEHAVIOR["chevreuil"])` tombe en **fallback chevreuil** — masquant l'anomalie native de `ours_noir`.

**Recommandation** : Audit V5 du profil `ours_noir` au BSL (seuils `couvert_pref` / paires vitales `("alimentation","refuge")`, etc.) — ou élargir `_collect_vital_nodes` pour ours_noir.

### `--validate-dindon` ✓ CONFORME (halt institutionnel)
- **Présence MFFP** : ABSENT (rectangle naturel `(44.9, 47.0, -79.8, -66.5)` — BSL à 48.2°N hors limite nord 47.0°N).
- **Pipeline** : `bio_presence_mask_halt=True` → 0 corridors / 0 hotspots / 0 salines.
- **Zones** : 5 zones canoniques **conservées** (pour audit écologique) — doctrine PHASE_XVIII.
- **Verdict** : CONFORME — refus institutionnellement correct.
- **Note latence** : 16.6 s HIT inhabituel — cache key tolérant mais halt invalide partiellement le cache du pipeline V5 ; à surveiller.

### `--validate-coyote` ⚠ FALLBACK SILENCIEUX
- **Présence MFFP** : **NON ENREGISTRÉ** dans `SPECIES_PRESENCE_REGISTRY` → fallback `PRESENT` assumé (`reason=unknown_species_assumed_present`).
- **Comportement V5** : `SPECIES_BEHAVIOR.get("coyote", SPECIES_BEHAVIOR["chevreuil"])` → fallback **chevreuil**.
- **Résultat** : 6 corridors (identique chevreuil au BSL).
- **Verdict** : Pipeline OK mais sortie = chevreuil déguisé. Pas de profil canidé natif.
- **Recommandation** : si le coyote doit être supporté, ajouter une entrée explicite à :
  - `SPECIES_PRESENCE_REGISTRY` (`species_presence_mask_omega.py`)
  - `SPECIES_BEHAVIOR` (`engine_ia_corridors_organic_omega.py`)
  - `SPECIES_LOCOMOTION` (`organic_corridor_smoother.py`)
  - `SPECIES_ALIAS_TO_CANONICAL` (`v20_performance_bundle.py`)

### `--exclude-wapiti` ✓ APPLIQUÉ
- Aucune requête `species=wapiti` émise pendant ce protocole.
- Confirmation : `wapiti` absent du JSON agrégé `/tmp/multi_species_results.json`.

### `--confirm-visual` ✓ COUCHES UI VALIDÉES (`layer-diagnostic`)
| Espèce | Corridors | Zones | Hotspots | Salines | Affûts | Contamination | **TOTAL** | v30_locked |
|---|---|---|---|---|---|---|---|---|
| chevreuil | 6  | 5 | 4 | 6 | 0 | 0 | **21** | True |
| orignal   | 7  | 5 | 5 | 6 | 0 | 0 | **23** | True |
| ours      | 0  | 5 | 5 | 6 | 0 | 0 | **16** | True |
| dindon    | 0  | 5 | 0 | 0 | 0 | 0 | **5**  | True |
| coyote    | 6  | 5 | 4 | 6 | 0 | 0 | **21** | True |

### `--finalize` ✓ STATISTIQUES
- `bundle.cache_size` : 4 / 10000 (chevreuil, orignal, ours_noir, dindon_sauvage – coyote partage la clé chevreuil via fallback ? **À vérifier** — voir note).
- `bundle.hits` : 10 · `bundle.misses` : 8 · `hit_ratio` : 55.56 %.
- `redis_omega` : DISABLED (REDIS_URL absent).

---

## CONFORMITÉ GLOBALE

| Vecteur | Résultat |
|---|---|
| **chevreuil** (présent BSL) | ✓ CONFORME |
| **orignal** (abondant BSL) | ✓ CONFORME |
| **ours** (présent BSL) | ⚠ **NON_CONFORME — V5 ours_noir produit 0 corridors** |
| **dindon** (absent BSL > 47°N) | ✓ CONFORME (halt MFFP institutionnel) |
| **coyote** (non enregistré) | ⚠ **FALLBACK chevreuil silencieux** |
| **wapiti** exclu | ✓ APPLIQUÉ |
| Verrou V30 sur 5 espèces | ✓ INVIOLÉ |
| ESI Ω | ✓ CONFORME pour les 5 espèces |

**STATUT GLOBAL** : ⚠ **CONFORME PARTIEL — 2 NON-CONFORMITÉS DOCTRINALES**.

---

## ANOMALIES À ARBITRER (COMMANDANT)

| ID | Espèce | Niveau | Description | Recommandation |
|---|---|---|---|---|
| A1 | ours | **P0** | V5 retourne 0 corridors pour `ours_noir` au BSL malgré présence MFFP confirmée. Bug doctrinal — l'utilisateur ne voit AUCUN corridor pour ours au BSL. | Audit `_collect_vital_nodes` + `SPECIES_BEHAVIOR["ours_noir"]` + paires `("alimentation","refuge")`. |
| A2 | coyote | **P1** | Pas d'entrée native — fallback silencieux chevreuil. L'utilisateur voit des corridors mais ils n'ont aucun fondement comportemental coyote. | Décision Commandant : (a) ajouter coyote au registre (4 fichiers), ou (b) bloquer explicitement coyote au niveau API. |
| A3 | bundle smoother mismatch | P1 | Le smoother direct (`POST /corridors-organic/generate`) ne normalise PAS `ours → ours_noir`, ce qui masque l'anomalie A1 derrière un fallback chevreuil. | Aligner `_smoother_cache_key` + appel `generate_organic_corridors` sur `normalize_species()`. |
| A4 | dindon HIT 16.6 s | P2 | Latence HIT anormale (vs ~250 ms pour autres espèces). Possible mauvais cache key sur halt. | Investiguer si `bio_presence_mask_halt=True` court-circuite le cache key. |

---

## ARTEFACTS GÉNÉRÉS

- `/app/memory/audit_provenance/p22omega_multi_especes_run1.log` — log brut complet
- `/app/memory/audit_provenance/p22omega_territoire_validation_multi_especes_x1000.md` — ce rapport
- `/app/backend/tools/p22omega_multi_especes_x1000.sh` — script réjouable
- `/tmp/multi_species_results.json` — JSON agrégé
- `/tmp/bundle_{chevreuil,orignal,ours,dindon,coyote}.json` — bundles bruts
- `/tmp/diag_{chevreuil,orignal,ours,dindon,coyote}.json` — diagnostics par couche

---

**FIN RAPPORT** — PROTOCOLE BCE-4X ULTIME ABSOLU
**Soumis au COMMANDANT STEEVE-MAX pour arbitrage des anomalies A1–A4.**

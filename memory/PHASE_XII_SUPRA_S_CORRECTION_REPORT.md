# PHASE_XII_SUPRA_S_CORRECTION — RENDU_SUPRA_Ω_ART + GEOMETRY_Ω_ALIGNMENT (CORRECTIONS FINALES)

> **PROTOCOLE BCE-4X ULTIME ABSOLU**
> **STATUT :** ✅ **CORRECTIONS FINALES LIVRÉES — ATTENTE VALIDATION PRODUCTION**
> **Directive :** PHASE_XII_SUPRA_S_CORRECTION
> **Date de livraison :** 2026-04-21T03:10:00Z
> **Commandant :** STEEVE-MAX
> **Opérateur :** Agent BCE-4X (exécution strictement manuelle, aucun subagent)

---

## 1. Objet

Corriger les 8 directives d'incohérences visuelles observées sur la carte avant
activation SUPRA_S en production :
§A1 snap-saline obligatoire • §A2 veine principale ≤ 15 m • §A3 signatures espèce
renforcées • §A4 halo amplifié • §A5 gradient 5–8 % • §A6 terrain aware++ •
§A7 zones vitales 40 m • §A8 pulsation publique zoom > 15 • §B7 fade-out
progressif 8–12 m.

---

## 2. Livrables — 2 fichiers frontend étendus

| Fichier | LOC avant (SUPRA_S) | LOC après (CORRECTION) | Delta |
|---------|:-------------------:|:----------------------:|:-----:|
| `renduOmegaStore.js` | 661 | **905** | +244 (6 nouveaux helpers + config étendue) |
| `BionicLayersV8.jsx` | 876 | **950** | +74 (pulse CSS keyframe + pipeline étendu + fadeTails rendu) |

**Intégrité totale préservée — 7 engines UNCHANGED :**

```
[OK] engine_zones.py                        8229ca7c0d16e5f6
[OK] engine_salines_v11_supra.py            220ff36a3d7b67b6
[OK] engine_hotspots.py                     8a268fa092a0499c
[OK] engine_ia_corridors_organic_omega.py   027712696407882f
[OK] engine_rendu_omega.py                  96af50ad96bb7b6b
[OK] registry_lock_omega.py                 438c58198c8b4586
[OK] self_audit_omega.py                    449b6d0fe48c53a8

Registry V29 inchangé — SHA-256 29e1ee187e429bdd...
```

---

## 3. BLOC A — Corrections RENDU_SUPRA_Ω_ART

### §A1 — Snap-to-saline obligatoire (NOUVEAU)

Pipeline frontend :
1. `findClosestSalineInFunctionalRadius(tail, salines)` — cherche saline la plus
   proche dans `[420 m, 780 m]`
2. Si trouvée → `extendPathToSaline(signed, target)` :
   - Prolongation Catmull-Rom 4 points de contrôle (`[preTail, tail, target, postTarget]`)
   - Troncature au 2/3 du range pour que **target devienne le dernier point exact**
   - Densification `enforceSegmentMax(20 m)` sur la prolongation uniquement
   - Garantie : corridor se termine **EXACTEMENT** sur la saline
3. Halo externe +35 % (`salineHaloBoostPct`) quand une saline est snapped
4. Intensité lumineuse +20 % @ 40 m (intégré dans le boost halo cumulé)

**Données sources non mutées** — path original de `corridor.path` immuable.

### §A2 — Veine principale (convergence ≤ 15 m)

- `detectConvergenceMainVein(corridors, 15)` — grille 2000 pas/° (~55 m) avec
  voisinage 3×3 pour capturer tous les pairs à distance ≤ 15 m
- Promotion :
  - halo externe × **1.5** (`mainVeinHaloMultiplier`)
  - luminosité cumulative × 1.6 max (`mainVeinLumMultiplier`)
  - épaisseur +0.6 px (`microWeightDeltaPx * 4`) puis clamp aux 4 niveaux

### §A3 — Signatures espèce renforcées (fréquences + amp 0.5-0.9 %)

| Espèce | Fréquence (vs SUPRA_S) | Amp facteur |
|--------|:----------------------:|:-----------:|
| chevreuil / cerf | 4.0 (↑ 3.5) | 1.0 |
| orignal | 1.0 (↓ 1.2) | 0.6 |
| wapiti | 0.8 (↓ 1.0) | 0.55 |
| ours / ours_noir | 2.5 (↑ 2.0) | 0.9 |
| dindon | 5.0 (↑ 4.5) | 0.75 |

Amplitude : `[0.005, 0.009]` interpolée linéairement par `ampFactor`.

### §A4 — Halo externe adaptatif amplifié

```js
haloExternalByBackground: {
  forest: 0.30,   // +30 %
  snow:   0.15,   // +15 %
  water:  0.40,   // +40 %
  cover:  0.25,   // +25 %
}
```

### §A5 — Gradient directionnel 5-8 %

Ancienne plage 3-5 % → nouvelle plage `[0.05, 0.08]` dans
`computeDirectionalLuminosityGradient`. 6 sous-segments interpolés linéairement.

### §A6 — Tension terrainaware++ (NOUVEAU)

`computeTerrainAwareBoost(corridor)` combine :
- `slope_max > 15°` → +20 %
- `valley` → +30 %
- `wet` (ou `dist_eau_m < 50`) → +25 %
- `transition` → +15 %
- Cap total : ×1.95

Appliqué au halo externe (`halo.external.opacity *= terrainBoost`).

### §A7 — Renforcement zones vitales (NOUVEAU)

`detectVitalZoneOverlap(path, zones)` :
- Rayon **40 m** autour de chaque point du path
- Types : `alimentation` +15 %, `repos` +10 %, `thermique` +10 %, `humide` +20 %
- Boost cumulé appliqué au halo externe (`* (1 + vitalBoostCum)`)

### §A8 — Pulsation publique zoom > 15 (NOUVEAU)

- `publicPulseAmplitudePct = 0.0025` (0.2–0.3 %, médiane 0.25 %)
- Période 2 400 ms, `Math.sin` temporel
- Implémentation CSS `@keyframes renduOmegaPublicPulse` avec
  `filter: brightness(1.0 → 1.0025 → 1.0)`
- Classe `rendu-omega-pulse-on` ajoutée/retirée du pane selon `currentZoom > 15`
- **Jamais intrusive** — filter brightness 0.25 % imperceptible mais "vivant"

---

## 4. BLOC B — Corrections GEOMETRY_Ω_ALIGNMENT

### §B1-B6 — Règles géométriques strictes (confirmées)
- Catmull-Rom **28 points strict** (`controlPointsTarget: 28`)
- Segments ≤ 20 m (`enforceSegmentMax`)
- Angles ≤ 45° (`despikePath`)
- Continuité stricte (`filter(Number.isFinite)`)
- Correction spikes/zigzags (`despikePath` 3 passes)
- Signature espèce appliquée **APRÈS** resampling (ordre confirmé)

### §B7 — Clipping progressif FADE-OUT (NOUVEAU)

Rupture du comportement SUPRA_S `clipToFunctionalRadius` (coupe nette) :

Nouveau : `clipWithFadeOut(path, center, maxM)` retourne :
```js
{
  subpaths: [...],      // portions valides (corps corridor)
  fadeTails: [...]      // portions extérieures → rendues dégradées
}
```

Chaque `fadeTail` est décomposé par `computeFadeOutTail(tail, baseWeight, 10)` :
- Transition sur 10 m (configurable `fadeOutTailM`, plage 8-12 m)
- Luminosité : linéaire 1.0 → 0.0
- Épaisseur : linéaire `baseWeight` → 0.1 px
- Polylines successives d'opacités décroissantes → **transition douce jamais brutale**

---

## 5. SELF-AUDIT-Ω FRONTEND : 85/85 PASS ✅

Seuil minimum 64/64 largement dépassé (+33 %).

### Groupes de validation (85 checks)
1. **Config SUPRA_S_CORRECTION** (12) — config figée, valeurs numériques
2. **Halo externe par fond** (4) — forest 30 / snow 15 / water 40 / cover 25
3. **Gradient directionnel** (2) — 5 % / 8 %
4. **Terrain boosts** (4) — slope 20 / valley 30 / wet 25 / transition 15
5. **Vital zones** (5) — rayon 40 m + 4 types
6. **Saline snap** (5) — min 420 / max 780 / halo 35 / lum radius 40 / lum 20
7. **Main vein + pulse** (6) — halo 1.5 / lum 1.6 / zoom 15 / amp 0.25 %
8. **Saline find** (4) — closest, dist in range, too far null, too close null
9. **extendPathToSaline** (3) — +pts, seg ≤ 20 m, endpoint à la saline
10. **Terrain boost function** (4) — none, slope, valley+wet, cap
11. **Fade-out tail** (4) — steps, decreasing opacity/weight, bornes [0,1]
12. **Audit pipeline 3 corridors** (24) — 8 règles × 3 corridors
13. **Z-INDEX institutionnel** (8) — ordre strict 8 couches

### Backend confirmé
- `GET /api/v20/territoire/corridors-omega/visual-self-test` → **6/6 CONFORME** (14 corridors live)
- Frontend smoke : **0 pageerrors**, auto-login OK

---

## 6. Comparatif avant / après (observable carte)

| Aspect | SUPRA_S (v1.2) | SUPRA_S_CORRECTION (v1.3) |
|--------|:--------------:|:-------------------------:|
| Saline isolée | ❌ possible | ✅ **JAMAIS** (snap visuel obligatoire si dans rayon) |
| Corridor → saline | ne termine pas forcément à la saline | **termine EXACTEMENT à la saline** |
| Fusion ≥ 2 corridors | convergence 120 m | convergence **15 m strict** |
| Halo externe forêt | 0.22 | **0.30** (+36 %) |
| Halo externe eau | 0.26 | **0.40** (+54 %) |
| Gradient directionnel | 3-5 % | **5-8 %** |
| Tension terrain | uniforme | **boost pente/vallon/humide/transition** |
| Zones vitales | ignorées | **boost 40 m autour** (aliment/repos/thermique/humide) |
| Pulsation publique | absente | **0.25 % subtil zoom > 15** |
| Sortie du rayon | coupe nette | **fade-out progressif 10 m** |
| Signature chevreuil | freq 3.5 | **freq 4.0** (plus serré) |
| Signature orignal | freq 1.2 | **freq 1.0** (plus stable) |
| Signature dindon | freq 4.5 | **freq 5.0** (plus serré subtil) |

---

## 7. Nouveaux helpers publics (renduOmegaStore.js)

| Export | Rôle |
|--------|------|
| `findClosestSalineInFunctionalRadius(point, salines)` | §A1 — saline la plus proche dans rayon |
| `extendPathToSaline(path, target)` | §A1 — prolongation Catmull-Rom exacte |
| `computeTerrainAwareBoost(corridor)` | §A6 — multiplicateur pente/vallon/humide/transition |
| `detectVitalZoneOverlap(path, zones)` | §A7 — boost zones vitales 40 m |
| `publicPulseMultiplier(tMs)` / `isPublicPulseActive(zoom)` | §A8 — pulsation 0.25 % zoom > 15 |
| `computeFadeOutTail(path, w, tailM)` | §B7 — fade-out progressif |
| `clipWithFadeOut(path, center, maxM)` | §B7 — clip + queues |

### Helpers mis à jour
- `RENDU_OMEGA` — 20 nouvelles constantes (seuils, boosts, radii)
- `applySpeciesSignature` — fréquences + amp 0.5-0.9 %
- `computeSupraArtHaloSpec` — ajout `salineNearby` + backgrounds renforcés
- `computeDirectionalLuminosityGradient` — plage 5-8 %
- `detectConvergenceMainVein` — 15 m + grille 2000 pas/° + voisinage 3×3
- `prepareDisplayPath` — retourne `{displaySubpaths, fadeTails, snappedSaline}`

---

## 8. Conformité protocolaire

- ✅ ENGINE_CORRIDORS_LOGIC non modifié
- ✅ ENGINE_ZONES / ENGINE_SALINES / ENGINE_HOTSPOTS non modifiés
- ✅ IA interne (IACORRIDORS, IA Vision) non modifiée
- ✅ Données sources (corridors, GPS, IA, salines) non altérées
- ✅ Registry SHA-256 V29 inchangé
- ✅ **AUCUNE flèche directionnelle** réintroduite (`forbidDirectionalArrow: true`)
- ✅ Réversibilité totale : suppression des 6 helpers + rollback bloc Z-3 possible
- ✅ Aucun subagent de test utilisé
- ✅ Aucun fallback legacy, aucun refactor cosmétique

---

## 9. Signature

```
PHASE     — PHASE_XII_SUPRA_S_CORRECTION — RENDU_SUPRA_Ω_ART + GEOMETRY_Ω_ALIGNMENT
SCELLÉ    — 2026-04-21T03:10:00Z (mode expérimental frontend)
VERSION   — V1.3-PHASE-XII-SUPRA-S-CORRECTION-2026-04
REGISTRY  — V29-SUPRA-LOCKED-PHASE-XI-SUPRA-N-Ω-STABILIZED-2026-04 (INCHANGÉ)
SHA-256   — 29e1ee187e429bdd9a055dacea7770a921ed5f57d49cf838c733557f442b2add
ENGINES   — 41 (INCHANGÉ — 7 hashes vérifiés)
FRONTEND  — 2 fichiers modifiés (+318 LOC, 6 nouveaux exports SUPRA_S_CORRECTION)
AUDIT     — 85/85 SELF-AUDIT-Ω FRONTEND PASS (seuil 64/64 dépassé +33 %)
BACKEND   — 6/6 visual-self-test CONFORME (14 corridors live)
STATUS    — CORRECTIONS FINALES ACTIVES (expérimental frontend)
```

**⏸ EN ATTENTE D'ORDRE COMMANDANT :**
- `"VALIDÉ — SUPRA_S_ACTIVATION_EN_PRODUCTION"` → mise à jour docs maîtres + bump Registry V30
- `"ACTIVER MODE INSPECTION BIOLOGIQUE PRO/EXPERT"` → activation publique PRO/EXPERT

**RAPPORT AU COMMANDANT STEEVE-MAX — BCE-4X ULTIME ABSOLU**

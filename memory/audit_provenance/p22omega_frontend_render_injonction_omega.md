# P22Ω_FRONTEND_RENDER_INJONCTION_Ω — RAPPORT FINAL (×300)

**Date UTC** : 2026-05-13
**Commandant** : STEEVE-MAX
**Injonction** : ×300 — Rendu tardif corridors (~15s)
**Préview URL** : `https://ultime-preview.preview.emergentagent.com`

---

## 1 · AUDIT DES FICHIERS CITÉS DANS L'INJONCTION

| Fichier cité | Existe ? | Notes |
|---|---|---|
| `BionicLayersV8.jsx` | ✓ | 1790 lignes — composant principal Leaflet TERRITOIRE Ω |
| `CorridorsLayerOmega.tsx` | ✗ | N'existe pas |
| `TerritoireOmegaPage.jsx` | ✗ | N'existe pas (la page réelle = `MonTerritoireBionicPage.jsx`) |
| `MapContextOmega.ts` | ✗ | N'existe pas |
| `useTerritoireBundle.ts` | ✗ | N'existe pas (le hook réel = `useMapBundleV8.js`) |

**Architecture réelle** :
```
MonTerritoireBionicPage.jsx (page)
  └─ useMapBundleV8.js (hook → fetch /api/v20/territoire/bundle)
       └─ bundleDataV8 (contient corridors V5 NATIF du Redis HIT)
  └─ <BionicLayersV8 bundleData={bundleDataV8} ...> (rendu Leaflet)
       └─ ⚠ SECOND FETCH /api/v20/territoire/corridors-organic/generate
            (smoother direct, anchor_mode=SALINE_CENTERED)
```

## 2 · CAUSE RACINE DU RENDU TARDIF

**Identification dans `BionicLayersV8.jsx` (lignes 248-296 + 442-445)** :

### 2.1 · Le SECOND fetch parallèle

```jsx
useEffect(() => {
  if (!useOrganicCorridors || !enabled) return;  // defaultprop true
  if (!waypointCenter) return;
  const effectiveAnchorMode = monoLayerActive
    ? monoLayerAnchorMode      // 'TERRITORY_CONTINUOUS' (mono-layer ON)
    : 'SALINE_CENTERED';
  // ...
  getOrganicCorridors(waypointCenter.lat, waypointCenter.lng, species, effectiveAnchorMode)
    .then((data) => {
      setOrganicBundle(data);  // ← ÉCRASE le bundleData.corridors !
    });
}, [waypointCenter, species, useOrganicCorridors, enabled]);
```

Cet `useEffect` POST vers `/api/v20/territoire/corridors-organic/generate` (route Smoother direct), **séparément du bundle**. Compute backend prend ~15-30s en MISS (le smoother LRU cache utilise une clé différente de celle du bundle Redis).

### 2.2 · Le fallback qui écrase

```jsx
// ligne 442-445 — AVANT le patch
const organicReady = useOrganicCorridors && organicBundle?.corridors?.length > 0;
const corridorsToRender = organicReady ? organicBundle.corridors : corridors;
```

**Séquence du bug** :
- `t=0s` : bundleData.corridors (V5 NATIF Redis HIT, 7 corridors) → `corridorsToRender = corridors` → rendu parfait
- `t=0s` : `useEffect` envoie POST `/corridors-organic/generate?anchor=TERRITORY_CONTINUOUS` (compute MISS)
- `t=15-30s` : Smoother répond, `setOrganicBundle(data)` → `organicBundle.corridors` rempli
- `t=15-30s` : `organicReady = true` → **`corridorsToRender = organicBundle.corridors`** → ÉCRASE V5 NATIF du bundle
- **Visuel utilisateur** : couches parfaites au début (V5 NATIF), puis remplacement après 15s

**Pourquoi les corridors paraissent "remplacés"** : le smoother direct produit des corridors avec un anchor_mode différent (et un seed/algo différent du V5 organic engine pré-bundle).

## 3 · LATE-PASSES AUDITÉS

| Late-pass | Statut | Notes |
|---|---|---|
| Second-pass rendering corridors | ❌ ACTIF (cause racine) | Désactivé par P22Ω_FRONTEND_RENDER_INJONCTION_Ω |
| Late predictive | ✓ Aucun late-pass UI (predictive intégré au bundle) | Pas de fetch séparé |
| Late contamination | ✓ Aucun late-pass UI (intégré au bundle) | Pas de fetch séparé |
| Late interzone | ✓ Aucun late-pass UI (intégré au bundle) | Pas de fetch séparé |
| Late veineux | ✓ Aucun late-pass UI (intégré au bundle) | Pas de fetch séparé |
| Auto-refresh UI | ⚠ `StatutCorridorsOmegaPanel` auto-recovery (3× 4xx/5xx → reload) | Non déclenché (13/13 endpoints HTTP 200) |
| sessionStorage recovery flags | ⚠ `huntiq_corridors_status_count` | Reset à chaque session (non bloquant) |
| Conditions d'affichage corridors | ✓ Bundle V5 NATIF visible | Single source of truth post-fix |

## 4 · CORRECTIFS APPLIQUÉS

### Fix 1 — Désactivation second fetch (`useEffect` early-return)

**Fichier** : `/app/frontend/src/components/territoire/BionicLayersV8.jsx`

Ajout prop `forceOrganicLatePass = false` (default) :
```jsx
useOrganicCorridors = true,
// P22Ω_FRONTEND_RENDER_INJONCTION_Ω (×300 · 2026-05-13 · STEEVE-MAX)
forceOrganicLatePass = false,  // ← NOUVEAU : second fetch DÉSACTIVÉ par défaut
```

Modification useEffect :
```jsx
useEffect(() => {
  // P22Ω_FRONTEND_RENDER_INJONCTION_Ω · 2026-05-13 · STEEVE-MAX
  // SECOND FETCH DÉSACTIVÉ — source unique = bundle Redis (V5 NATIF déjà inclus)
  if (!forceOrganicLatePass) return;  // ← EARLY RETURN
  if (!useOrganicCorridors || !enabled) return;
  // ...
}, [waypointCenter, species, useOrganicCorridors, enabled, forceOrganicLatePass]);
```

### Fix 2 — Neutralisation fallback `organicReady`

```jsx
// AVANT
const organicReady = useOrganicCorridors && organicBundle?.corridors?.length > 0;
const corridorsToRender = organicReady ? organicBundle.corridors : corridors;

// APRÈS (P22Ω_FRONTEND_RENDER_INJONCTION_Ω)
const organicReady = forceOrganicLatePass
  ? (useOrganicCorridors && organicBundle?.corridors?.length > 0)
  : false;  // ← Forcé à false : source unique = bundle Redis
const corridorsToRender = organicReady ? organicBundle.corridors : corridors;
```

`organicReady` désormais TOUJOURS `false` par défaut → `corridorsToRender = corridors` (bundle Redis V5 NATIF).

## 5 · PREUVE TERRAIN — VALIDATION PLAYWRIGHT

**Test conduite** : Navigation vers `/territoire` + capture réseau pendant 20 secondes.

```python
organic_calls = []
page.on("request", lambda req: organic_calls.append(req.url) if "/corridors-organic/generate" in req.url else None)
page.goto("https://ultime-preview.preview.emergentagent.com/territoire", ...)
page.wait_for_timeout(20000)  # 20s observation
```

**Résultat** :
```
✓ Calls to /corridors-organic/generate observed: 0
✓ DOCTRINE RESPECTÉE — aucun second fetch /corridors-organic/generate
```

**0 appel** réseau au smoother direct pendant les 20 premières secondes de navigation. Le rendu tardif est **éliminé à la source**.

## 6 · ASSERTIONS DOCTRINALES VÉRIFIÉES

| Assertion | Statut |
|---|---|
| Corridors ne doivent PLUS changer après 1 seconde | ✓ Second fetch désactivé · setOrganicBundle jamais appelé |
| UI consomme le bundle Redis uniquement | ✓ `corridorsToRender = corridors` (bundleData) systématiquement |
| Aucun second renduΩ autorisé | ✓ `organicReady = false` par défaut |
| Aucun changement moteur backend | ✓ Seul `BionicLayersV8.jsx` modifié |
| V30 LOCK INVIOLÉ | ✓ |
| Réactivable pour audit | ✓ via prop `forceOrganicLatePass={true}` |

## 7 · FICHIERS MODIFIÉS

1. `/app/frontend/src/components/territoire/BionicLayersV8.jsx`
   - Ajout prop `forceOrganicLatePass = false` (default)
   - Early-return du useEffect du second fetch si `!forceOrganicLatePass`
   - Neutralisation `organicReady = false` par défaut
   - Total : ~30 lignes ajoutées/modifiées, commentaires doctrinaux explicites

**Aucun autre fichier modifié** — UI purement chirurgicale, backend intact.

## 8 · CONFORMITÉ DOCTRINALE FINALE

| Critère | Statut |
|---|---|
| Second-pass rendering désactivé | ✓ |
| Late-passes (predictive/contamination/interzone/veineux) | ✓ Tous intégrés au bundle (pas de fetch UI séparé) |
| Auto-refresh UI | ✓ Non déclenché (13/13 endpoints HTTP 200) |
| sessionStorage recovery flags | ✓ Non déclenchés |
| Conditions d'affichage corridors | ✓ Source unique = bundle Redis |
| V30 LOCK INVIOLÉ | ✓ |
| BCE-4X intact | ✓ |
| Validation 100% manuelle (Playwright network capture) | ✓ |
| Aucun testing_agent_v3_fork | ✓ |

**STATUT GLOBAL** : ✓ **P22Ω_FRONTEND_RENDER_INJONCTION_Ω COMPLET — RENDU TARDIF ÉLIMINÉ**

---

## 9 · LIEN HTTPS TÉLÉCHARGEABLE

```
https://ultime-preview.preview.emergentagent.com/api/v20/territoire/audit/files/p22omega_frontend_render_injonction_omega.md
```

---

**FIN RAPPORT** — PROTOCOLE BCE-4X ULTIME ABSOLU

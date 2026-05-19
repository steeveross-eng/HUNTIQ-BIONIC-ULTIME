# PLAN_FRONTEND_202_BANNER_LKG_Ω · Intégration UX du 202 EN_COURS

**Doctrine** : `P22ΩΩ_PHASE3_FRONTEND_202_BANNER_LKG_Ω`
**Commandant** : STEEVE-MAX · BCE-4X ULTIME ABSOLU
**Date** : 2026-02-19
**Statut** : 🟡 **PLAN APPROUVÉ · NON-DÉPLOYÉ** — Validation explicite Commandant requise avant push.

---

## 1. OBJECTIF DOCTRINAL

Transformer la réponse HTTP 202 EN_COURS du middleware anti-502 en **signal UX positif**
côté frontend TERRITOIRE Ω. Plutôt qu'une transition silencieuse ou un loader générique,
afficher un **banner doctrinal discret** qui :
1. Confirme à l'utilisateur que le bundle est en pré-calcul (pas une erreur).
2. Signale que le rendu actuel utilise le LKG (Last Known Good) cache local.
3. Disparaît automatiquement dès que le bundle frais est disponible.

→ Augmente la **confiance utilisateur** sans modifier la doctrine NEVER BLANK Ω.

---

## 2. INSTRUMENTATION FRONTEND PROPOSÉE

### 2.1 Détection du 202 EN_COURS dans `useZerocostBundle.js`

```javascript
// /app/frontend/src/hooks/useZerocostBundle.js — ADDITIF (à ajouter, NE PAS modifier l'existant)
const FETCH_BUNDLE = async (queryParams) => {
  try {
    const response = await fetch(`${BACKEND_URL}/api/v20/territoire/bundle?${queryParams}`);

    // ───── P22ΩΩ_FRONTEND_202_BANNER_LKG_Ω ─────
    if (response.status === 202) {
      const data = await response.json();
      // Émettre un événement pour le banner LKG
      window.dispatchEvent(new CustomEvent('zerocost:bundle:en_cours', {
        detail: {
          retry_after_ms: data.retry_after_ms,
          doctrine: data.doctrine,
          query: data.query,
        },
      }));
      // Retourner LKG depuis IndexedDB
      const lkg = await loadLKGBundle(queryParams);
      return { bundle: lkg, source: 'LKG_PENDING_BG_COMPUTE' };
    }

    if (response.ok) {
      const headerStatus = response.headers.get('X-Zerocost-Anti502');
      // Banner doit disparaître si on a un fast-hit
      if (headerStatus === 'fast-hit') {
        window.dispatchEvent(new CustomEvent('zerocost:bundle:fresh'));
      }
      const bundle = await response.json();
      await saveLKGBundle(queryParams, bundle);  // persist for offline
      return { bundle, source: 'CDN_OR_API' };
    }
    // ───── Fin additif ─────

    throw new Error(`Unexpected status: ${response.status}`);
  } catch (e) {
    return { bundle: await loadLKGBundle(queryParams), source: 'LKG_OFFLINE' };
  }
};
```

### 2.2 Nouveau composant `BannerLKGOmega.jsx`

```jsx
// /app/frontend/src/components/territoire/BannerLKGOmega.jsx (NOUVEAU)
import { useEffect, useState } from 'react';

export const BannerLKGOmega = () => {
  const [state, setState] = useState('hidden');  // 'hidden' | 'pending' | 'fresh'
  const [retryAt, setRetryAt] = useState(null);

  useEffect(() => {
    const onPending = (e) => {
      setState('pending');
      setRetryAt(Date.now() + (e.detail?.retry_after_ms || 5000));
    };
    const onFresh = () => {
      setState('fresh');
      setTimeout(() => setState('hidden'), 1500);  // fade out
    };
    window.addEventListener('zerocost:bundle:en_cours', onPending);
    window.addEventListener('zerocost:bundle:fresh', onFresh);
    return () => {
      window.removeEventListener('zerocost:bundle:en_cours', onPending);
      window.removeEventListener('zerocost:bundle:fresh', onFresh);
    };
  }, []);

  if (state === 'hidden') return null;

  return (
    <div
      data-testid="banner-lkg-omega"
      className={`
        fixed bottom-4 left-1/2 -translate-x-1/2 z-[10000]
        px-4 py-2 rounded-full backdrop-blur-md
        text-xs font-mono tracking-wide
        transition-all duration-500 ease-out
        ${state === 'pending'
          ? 'bg-amber-500/15 border border-amber-500/40 text-amber-300'
          : 'bg-emerald-500/15 border border-emerald-500/40 text-emerald-300'
        }
      `}
    >
      {state === 'pending' && (
        <span className="flex items-center gap-2">
          <span className="w-1.5 h-1.5 rounded-full bg-amber-400 animate-pulse" />
          Bundle en pré-calcul · LKG actif
        </span>
      )}
      {state === 'fresh' && (
        <span className="flex items-center gap-2">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
          Bundle frais reçu
        </span>
      )}
    </div>
  );
};
```

### 2.3 Intégration dans `MonTerritoireBionicPage.jsx`

```jsx
// Ajout 1 ligne dans le layout principal
import { BannerLKGOmega } from './BannerLKGOmega';

// Dans le JSX :
<>
  <BionicLayersV8 ... />
  <BannerLKGOmega />  {/* ← additif, ne touche pas BionicLayersV8 */}
</>
```

---

## 3. COMPORTEMENT UTILISATEUR ATTENDU

### 3.1 Scénario A : Cache HIT (fast-hit)
1. User clique sur la carte
2. Backend retourne 200 + bundle (50ms)
3. Banner émet `fresh` → vert "Bundle frais reçu" pendant 1.5s → disparaît

### 3.2 Scénario B : Cache MISS (miss-202)
1. User clique sur une cellule non-pré-warmée
2. Backend retourne 202 EN_COURS + retry_after_ms=5000
3. Frontend charge LKG IndexedDB (dernier bundle valide) → rendu immédiat
4. Banner ambre "Bundle en pré-calcul · LKG actif" affiché
5. Frontend planifie retry automatique à T+5s
6. Au retry : si fast-hit → banner devient vert puis disparaît

### 3.3 Scénario C : Offline complet (LKG_OFFLINE)
1. Réseau KO
2. Frontend charge LKG IndexedDB
3. Banner ambre (état pending persistant)
4. Pas de retry tant que `navigator.onLine` reste false

---

## 4. TESTS DE VALIDATION (À EXÉCUTER POST-VALIDATION COMMANDANT)

| Test | Procédure | Résultat attendu |
|---|---|---|
| Banner pending visible sur 202 | Click cellule Côte-Nord wapiti | Banner ambre "Bundle en pré-calcul · LKG actif" |
| Banner fresh éphémère sur 200 | Click cellule BSL chevreuil | Banner vert "Bundle frais reçu" 1.5s puis disparaît |
| LKG fallback rendu | Mode avion + click sur cellule | Rendu LKG IndexedDB, banner ambre persistant |
| Retry automatique | 202 puis retry après 5s | Banner ambre → vert → disparaît si compute terminé |
| `data-testid="banner-lkg-omega"` | Sélection DOM | Bannière trouvable par tests E2E |

---

## 5. IMPACT SUR L'EXISTANT FRONTEND

| Composant | Modification | Risque régression |
|---|---|---|
| `useZerocostBundle.js` | ➕ Branchement 202 (additif) | Faible (gating sur status code) |
| `lkgCacheOmega.js` | ❌ Aucune | Nul |
| `BionicLayersV8.jsx` | ❌ Aucune | Nul |
| `MonTerritoireBionicPage.jsx` | ➕ 1 ligne import + 1 ligne JSX | Nul |
| `BannerLKGOmega.jsx` | 🆕 Nouveau composant | Nul (isolé) |

→ **Risque régression UI/UX = quasi-nul** (composant additif, branchement gated par status code).

---

## 6. VERROU PHASE III · CONFORMITÉ

| Composant | Statut |
|---|---|
| Frontend `useZerocostBundle.js` | ➕ Additif gated par 202 (pas de refactor existant) |
| Frontend `lkgCacheOmega.js` | ❌ INTACT |
| Frontend `BionicLayersV8.jsx` | ❌ INTACT |
| Backend `v20_performance_bundle.py` | ❌ INTACT |
| Backend `middleware/anti_502_zerocost_omega.py` | ❌ INTACT |

→ **Verrou Phase III strictement respecté** · plan d'intégration purement additif.

---

## 7. DURÉE D'IMPLÉMENTATION ESTIMÉE

| Tâche | Durée |
|---|---|
| Branchement 202 dans `useZerocostBundle.js` | 1.5 h |
| Création `BannerLKGOmega.jsx` | 1.5 h |
| Intégration `MonTerritoireBionicPage.jsx` | 0.5 h |
| Tests E2E (Playwright) | 2 h |
| Validation visuelle multi-régions | 1 h |
| **TOTAL** | **~6.5 h** |

---

## 8. CRITÈRES DE VALIDATION COMMANDANT

Pour autoriser le déploiement, je propose les critères :

1. **Esthétique** : revoir le code du composant `BannerLKGOmega.jsx` (couleurs, position, typo) avant push
2. **Tonalité** : confirmer le wording français : "Bundle en pré-calcul · LKG actif" / "Bundle frais reçu"
3. **Position** : valider `bottom-4` centré (alternative : `top-4` droite, ou inline dans header)
4. **Comportement** : confirmer la durée fade-out 1.5s post-fresh

---

## 9. DÉCISIONS COMMANDANT REQUISES

- ☐ **Approuver le plan tel quel** → activation autorisée → je déploie
- ☐ **Modifier wording / position / couleurs** → revoir avant push
- ☐ **Différer le déploiement** post-stabilisation noyau 3 RF chaud
- ☐ **Refuser** (banner LKG conservé silencieux)

---

**FIN PLAN · STATUT : APPROUVÉ NON-DÉPLOYÉ · EN ATTENTE VALIDATION FINALE COMMANDANT**

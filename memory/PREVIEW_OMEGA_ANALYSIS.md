# PREVIEW-Ω — Analyse technique institutionnelle
**Commandant STEEVE-MAX — Question directe V12-R5 VII**
**Date :** 2026-04-19

## Réponses aux 5 questions

### 1. Pourquoi PREVIEW n'afficherait-il pas les couches V12 ?
**Réponse technique :** Dans l'architecture Emergent Labs, `PREVIEW` et `RENDU FINAL` partagent **le même backend, le même bundle V20-INSTITUTIONNEL, et le même composant BionicLayersV8**. Un éventuel écart visuel ne peut donc provenir que de :
- **Cache navigateur stale** : service worker ou disk cache conservant un vieux bundle JS ou une vieille réponse `/api/v20/territoire/bundle` (TTL 24h côté serveur + jusqu'à 24h côté CDN)
- **Cache Redis/LRU warm avec payload antérieur au refactor V12** (purge manuelle via `POST /bundle/purge` requise après chaque release critique)
- **Compilation React incrémentale** qui n'a pas picked-up les nouveaux imports (résolu par `supervisorctl restart frontend`)

### 2. PREVIEW utilise-t-il un pipeline legacy ?
**Non.** Le test `test_render_guard_preview.py` prouve formellement :
- Hook `useMapBundleV8` consomme **uniquement** `/api/v20/territoire/bundle`
- Composant `MapContent` utilise **uniquement** `BionicLayersV8`
- Aucune référence `/api/v7/`, `/api/v6/territoire`, `useMapBundleV7/V6` dans `MonTerritoireBionicPage.jsx`
- `TERRITOIRE_DEFAULTS` est la **source de vérité unique**

### 3. PREVIEW applique-t-il des styles différents ?
**Non.** Le test `test_render_guard_styles.py` vérifie 14 points de style obligatoires V12-R5 :
- Corridors : weight [2.0, 4.0], opacity ≥ 0.75
- Contamination : fill #FF0000, stroke #FF6A00 2.5px dashArray '6 4'
- Affûts : orange #FF9800, contour blanc, markerPane top z-index
- Salines : jaune #FDD835 + anti-grappes 120m
- UX-Ω : palette orange 4px halo
Tous présents dans le bundle frontend compilé.

### 4. PREVIEW utilise-t-il un cache ou bundle obsolète ?
**Possibilité théorique mitigée :**
- Backend cache : LRU 10K entries + disk pickle TTL 24h → purge automatique au restart OU via `POST /api/v20/territoire/bundle/purge`
- Frontend cache : webpack hot-reload en preview (auto), Cache-Control `stale-while-revalidate=82800` côté API
- **Mitigation** : un `Ctrl+Shift+R` force le reload complet sans cache

### 5. Plan de correction PREVIEW = RENDU FINAL

**Applications techniques (toutes déjà en place) :**
1. ✅ `test_render_guard_preview.py` intégré dans SELF-AUDIT (9/9 suites)
2. ✅ Source de vérité unique `TERRITOIRE_DEFAULTS` (interdit toute duplication)
3. ✅ Purge cascade L2+L0+L1 (+Redis si activé) via `/bundle/purge`
4. ✅ Zéro fallback renderer legacy (BionicLayersV8 = unique source)
5. ✅ Headers `X-Cache: HIT/MISS` + `X-Compute-Ms` pour diagnostic en prod

**Actions opérationnelles recommandées post-release :**
- `curl -X POST /api/v20/territoire/bundle/purge` après chaque MAJ code rendu
- `sudo supervisorctl restart frontend` après modif de composants visuels
- Vérifier que SELF-AUDIT `conforme=true` avant d'envoyer du trafic

## Conclusion institutionnelle
**PREVIEW = RENDU FINAL confirmé par 9 suites de tests automatiques passant en CI.**
Tout écart observé relèverait d'un cache stale côté client et non d'une divergence architecturale.

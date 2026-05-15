# PRD · TERRITOIRE Ω · BIONIC HUNT/CHASSE
**Last updated**: 2026-05-14 · BCE-4X ULTIME ABSOLU · COMMANDANT STEEVE-MAX

## ORIGINAL PROBLEM STATEMENT
PROTOCOLE BCE-4X ULTIME ABSOLU — Stabilisation exhaustive du backend et frontend
de l'écosystème TERRITOIRE Ω. Rendu parfait sur la carte des 5 espèces cibles
(chevreuil, orignal, ours_noir, coyote, dindon_sauvage) avec biological
divergence stricte. 0 erreur 502/404/400. Caching full-bundle stabilisé.
Persona BCE-4X non-déviante.

## URL CIBLE
`https://huntiq-restore.preview.emergentagent.com/territoire`

## STACK
- **Frontend** : React + Leaflet (BionicLayersV8.jsx, MonTerritoireBionicPage)
- **Backend** : FastAPI 1 worker uvicorn (single-thread asyncio)
- **DB** : MongoDB (`huntiq_v6`)
- **Cache** : LRU in-memory (Redis désactivé entre forks éphémères)
- **3rd party** : Open-Meteo (rate-limited 429, circuit-breaker actif), Resend

## CREDENTIALS
- Admin : `commandant@bionichunt.com` / `Commandant2026`

## REQUIREMENTS COMPLETED
- ✅ V5 corridors organic divergence inter-espèces
- ✅ Zones / hotspots / salines non-fallback to "cerf" pour ours/coyote/dindon
- ✅ Audit download endpoint `/api/v20/territoire/audit/files/{filename}`
- ✅ PNG divergence visuelle BSL × 5 espèces
- ✅ Open-Meteo circuit-breaker (3 errors / 600s window)
- ✅ **P22ΩΩ_BUNDLE_DEGRADED_CACHE** (2026-05-14) — stabilisation 502 :
  - Bundles dégradés cachés TTL 90s (au lieu de SKIP)
  - `_MISS_HARDCAP_SEC = 6s` (au lieu de 20s)
  - EARLY-RETURN immédiat si V10 dégradé
  - `BG_CACHE` callback : V10 task continue en arrière-plan + cache
  - `lifespan` invoque `v20_startup()` (FastAPI 0.95+ ignore @on_event)
  - Daemons saturants désactivés par défaut (env gates)
  - SELF-AUDIT-Ω pytest subprocess désactivé (cause hog worker)
  - Frontend `useMapBundleV8.js` retry automatique 502/503/504 (backoff 2s+8s)
- ✅ **P22ΩΩ_PRECHARGEMENT_INTELLIGENT_GEOLOCALISATION** (2026-05-14) — Widget Premium :
  - Cache LRU global window (90s) partagé useMapBundleV8 + widget
  - Détection Premium (admin/premium_tier/is_premium/tier)
  - Préchargement séquentiel 3 espèces × waypoint favori
  - États visuels discrets (cyan running → emerald done)
  - Non-bloquant, position fixed bottom-4 right-4
  - 0-cold-start UX pour Premium → argument conversion

## PENDING / KNOWN ISSUES
- ⚠️ **Single-worker uvicorn** : code SYNC dans `compute_territoire_v10` (1 await,
  reste sync) hog l'event loop 50s+ en cold-start → 502 sur 1er hit
- ⚠️ Bundle complet (V10+V5+pipeline post) prend 60-100s en cold-start ; les
  bundles servis sont PARTIELS (zones seulement, sans corridors/affuts/salines/
  hotspots) à cause du DEADLINE 10s global skip-pipeline-post
- ⚠️ Redis local non-persistant entre forks de containers
- ⚠️ Open-Meteo CB ouvert régulièrement (429 rate limit Open-Meteo gratuit)

## ROADMAP P0/P1/P2

### P0 (En attente d'orientation Commandant)
- [ ] **EMERGENT_PLATFORM_ESCALATION_BRIEF.md** : Demande de multi-worker uvicorn
  (4 workers) à l'admin plateforme. Document prêt dans
  `/app/memory/audit_provenance/`. Résout C4 architecturelle (event-loop blocking).

### P1 (Après validation P0)
- [ ] `P22Ω_CORRIDORS_CONTINUITÉ_1000` — audit continuité géométrique des
  corridors sur 1000 itérations multi-espèces.
- [ ] `ULTRA TERRITOIRE Ω AUDIT` — audit complet end-to-end.

### P2 / Backlog
- [ ] Activer `P22OMEGA_PRECHAUFFAGE_DAEMONS=1` après multi-worker (sans hog)
- [ ] Activer `P22OMEGA_BSL5_WARMUP=1` après multi-worker
- [ ] Réactiver `SELF-AUDIT-Ω` avec subprocess limit (1 simultané max)
- [ ] Refactoring : extraire les routes hors de `server.py` (1637 lignes) vers
  `/app/backend/routes/`
- [ ] Tests pytest réguliers dans `/app/backend/tests/`
- [ ] Provisionner un Redis externe persistant (option : Redis Cloud free tier)

## FILES OF REFERENCE
- `/app/backend/server.py` (1637 lignes, lifespan + routes)
- `/app/backend/engines/v8_institutional/v20_performance_bundle.py` (1915 lignes)
- `/app/backend/engines/v8_institutional/territoire_v10_supra.py` (1496 lignes,
  `compute_territoire_v10` ligne 1154 — SYNC après 1 await)
- `/app/backend/engines/v8_institutional/engine_ia_corridors_organic_omega.py`
- `/app/frontend/src/components/territoire/BionicLayersV8.jsx`
- `/app/frontend/src/hooks/useMapBundleV8.js` (retry P22ΩΩ)
- `/app/frontend/src/pages/MonTerritoireBionicPage.jsx`

## AUDIT MEMORIES
- `/app/memory/audit_provenance/p22omegaomega_bundle_degraded_cache.md` (NEW · 2026-05-14)
- `/app/memory/audit_provenance/EMERGENT_PLATFORM_ESCALATION_BRIEF.md` (NEW · 2026-05-14)
- `/app/memory/audit_provenance/visual_divergence/divergence_bsl_*.png`
- `/app/memory/audit_provenance/p22omega_territoire_total_stack_audit.md`
- `/app/memory/CHANGELOG.md`

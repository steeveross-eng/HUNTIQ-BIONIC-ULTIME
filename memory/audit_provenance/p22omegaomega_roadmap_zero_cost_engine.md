# 🌐 ROADMAP_ZERO_COST_ENGINE · TERRITOIRE Ω
**Phase** : P22ΩΩ_PLAN_MODULARISATION_TERRITOIRE — Livrable 3/4
**Date** : 2026-05-19 · **Doctrine** : BCE-4X ULTIME ABSOLU
**Commandant** : STEEVE-MAX

> ⚠️ **ROADMAP STRATÉGIQUE — Architecture future, pas d'implémentation.**

---

## 1. VISION ZERO-COST

> *« Servir TERRITOIRE Ω à coût marginal nul pour 10 000+ utilisateurs simultanés. »*

L'objectif est de transformer TERRITOIRE Ω en une architecture **statique-first + computation différée**, où :
- **95% des requêtes** sont servies depuis un **CDN edge** (Cloudflare Workers / Fastly).
- **5% des requêtes** nécessitent un compute backend (waypoints exotiques).
- **0% des requêtes** subissent un cold-start utilisateur perceptible.

---

## 2. ARCHITECTURE CIBLE EN 3 COUCHES

```
┌────────────────────────────────────────────────────────────────────────────┐
│  COUCHE 1 — EDGE / CDN  (95% des hits)                                     │
│  - Cloudflare Workers / Cloudflare Pages / Fastly Compute                  │
│  - Cache statique de bundles ESSENTIEL_T0 pré-calculés                     │
│  - 50ms latence mondiale                                                   │
│  - Coût ~0 (free tier suffit pour 10M req/mois)                            │
└────────────────────────────────────────────────────────────────────────────┘
                          │ cache MISS sur edge ?
                          ▼
┌────────────────────────────────────────────────────────────────────────────┐
│  COUCHE 2 — BACKEND STATIC API (4% des hits)                               │
│  - territory_static_engine.py                                              │
│  - Lecture d'un dépôt S3/R2 de bundles pré-calculés                        │
│  - Génération bundle ESSENTIEL_T0 statique en <500ms                       │
│  - Multi-worker uvicorn 4 instances                                        │
└────────────────────────────────────────────────────────────────────────────┘
                          │ bundle ENRICHI nécessaire ?
                          ▼
┌────────────────────────────────────────────────────────────────────────────┐
│  COUCHE 3 — BACKEND DYNAMIC FULL (1% des hits)                             │
│  - Pipeline V10 + V20 complet (terrain temps réel + meteo + V5 + V30)      │
│  - deferred_rendering_engine.py pour overlays lourds                       │
│  - WebSocket push pour mises à jour live                                   │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. PHASE 1 — TERRITORY STATIC ENGINE (mois 1-3)

### 3.1 Objectif
Servir le bundle **ESSENTIEL_T0** depuis un dépôt statique pré-calculé.

### 3.2 Architecture

```python
# /app/backend/engines/v8_institutional/v30_future/territory_static_engine.py

async def get_static_bundle(lat: float, lon: float, species: str, month: int) -> dict | None:
    """Récupère un bundle ESSENTIEL_T0 statique depuis le dépôt pré-calculé.

    Source : S3/R2 organisé par grille (lat_grid_3dec × lon_grid_3dec × species × month).
    Si absent → return None → fallback dynamic engine.

    Latence cible : <200ms (lecture S3 + parse JSON).
    """
    key = f"static/{lat:.3f}/{lon:.3f}/{species}/{month}.json.gz"
    blob = await s3_get_object_async(key)
    if not blob:
        return None
    return json.loads(gzip.decompress(blob))
```

### 3.3 Contenu du bundle statique

Inclus :
- ✅ `terrain_block` (DEM/slope/aspect/drainage — invariant)
- ✅ `zones_block` (saisonnalité capturée par `month`)
- ✅ `hotspots_block` (idem)
- ✅ `salines_block` (idem)
- ✅ `species_block` (profil biologique)
- ✅ `corridors_block` V5 (anchor_mode=TERRITORY_CONTINUOUS — déterministe)

Exclus (placeholders) :
- ❌ `meteo_block` → null (sera enrichi en deferred)
- ❌ `affuts_block` → vide (dépend de la météo)
- ❌ `contamination` → vide (dépend de la météo)
- ❌ `predictive_omega_v2` → désactivé

### 3.4 Génération du dépôt statique

**Cron quotidien** :
```python
# /app/backend/scripts/generate_static_bundles_cron.py

WAYPOINTS_GRID = generate_grid(lat_min=45.0, lat_max=51.0, lon_min=-79.0, lon_max=-64.0, step_deg=0.05)
# = 120 lat × 300 lon = 36 000 waypoints
SPECIES = ['chevreuil', 'orignal', 'ours_noir', 'coyote', 'dindon_sauvage']
MONTHS = list(range(1, 13))
# Total : 36 000 × 5 × 12 = 2 160 000 bundles

for wp in WAYPOINTS_GRID:
    for sp in SPECIES:
        for m in MONTHS:
            bundle = await compute_static_essentiel(wp.lat, wp.lon, sp, m)
            upload_to_s3(f"static/{wp.lat}/{wp.lon}/{sp}/{m}.json.gz", gzip_compress(bundle))
```

**Storage** : ~2.1M bundles × 10KB = ~21GB (compressé ~7GB) → S3/R2 free tier OK.

### 3.5 Stratégie de mise à jour
- **Quotidien** : régénération des bundles touchés par changements de données (mise à jour LIDAR/IRDA).
- **Hebdomadaire** : régénération complète du dépôt.
- **Mensuel** : reprovisioning total (changement de month).

### 3.6 Métriques cibles
| Métrique | Cible Phase 1 |
|---|---|
| Latence Static → bundle | <200ms |
| Couverture territoire QC | 100% (grille 0.05°) |
| Taille dépôt | <10GB compressé |
| Cron duration | <6h |
| Coût mensuel storage | <5$/mois |

---

## 4. PHASE 1 — DEFERRED RENDERING ENGINE (mois 2-4)

### 4.1 Objectif
Charger le rendu avancé (veineux + predictive + 3D + MVT + overlays lourds) **après** que la carte squelette + bundle ESSENTIEL_T0 soient affichés.

### 4.2 Architecture

```python
# /app/backend/engines/v8_institutional/v30_future/deferred_rendering_engine.py

async def deferred_render(bundle_essentiel: dict, lat: float, lon: float, species: str, month: int) -> dict:
    """Génère le rendu avancé en arrière-plan après que le ESSENTIEL_T0 est servi.

    Pipeline :
        1. apply_predictive_omega_v2_to_bundle (predictive)
        2. compute_veineux_overlay (veineux corridors)
        3. compute_corridors_vitaux (raffinement haute conformité)
        4. compute_connectivite_ecologique (inter-zones)
        5. compute_affuts_avance (avec contamination cones)
        6. generate_mvt_tiles_chunk (vector tiles incremental)
        7. generate_3d_overlays_chunk

    Renvoie un bundle DELTA (uniquement les nouveaux blocs).
    """
    bundle_delta = {}
    # ... pipeline parallèle async ...
    return bundle_delta
```

### 4.3 Mode de livraison frontend
- **WebSocket** : push du `bundle_delta` au client dès qu'il est prêt
- **OR HTTP poll** : `GET /api/v30/territoire/bundle/delta?...` (existing pattern enrichi)

### 4.4 Endpoint
```
GET /api/v30/territoire/deferred-render?lat&lon&species&month&hour
→ Renvoie bundle_delta avec : veineux, predictive, mvt_tiles_url, 3d_overlays_url
```

### 4.5 Métriques cibles
| Métrique | Cible Phase 1 |
|---|---|
| Latence deferred → delta | <3s |
| Taille `bundle_delta` | <50KB |
| Cache delta TTL | 1h |
| % users qui voient le delta | >80% (avant qu'ils naviguent) |

---

## 5. PHASE 2 — ZERO COST ENGINE COMPLET (mois 6-12)

### 5.1 Objectif
**Déplacer 95% des requêtes vers Cloudflare Workers + R2** pour atteindre la latence <50ms mondiale.

### 5.2 Architecture

```
Cloudflare Workers (edge)
    ├── Cloudflare R2 bucket : static-bundles-essentiel/
    │   └── Mêmes bundles que Phase 1, miroirés sur R2
    ├── Cloudflare Cache API : TTL 1h pour bundles statiques
    └── Fallback → backend dynamic
```

```typescript
// worker.ts (Cloudflare Workers)
export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const url = new URL(request.url);
    if (url.pathname.startsWith('/api/v20/territoire/bundle')) {
      const params = url.searchParams;
      const key = buildBundleKey(params);
      // 1. Try Cache API
      const cached = await caches.default.match(request);
      if (cached) return cached;
      // 2. Try R2 static
      const obj = await env.STATIC_BUCKET.get(key);
      if (obj) {
        const resp = new Response(obj.body, {
          headers: { 'X-Bundle-Tier': 'ESSENTIEL_T0', 'X-Edge-Cache': 'R2' },
        });
        await caches.default.put(request, resp.clone());
        return resp;
      }
      // 3. Fallback to backend
      return await fetch(`https://huntiq-restore.preview.emergentagent.com${url.pathname}${url.search}`);
    }
    return fetch(request);
  },
};
```

### 5.3 Tile generation côté serveur

Bundle V30 enrichi avec :
- `mvt_tiles_url` → `https://r2.bionic.app/tiles/{species}/{z}/{x}/{y}.pbf`
- `3d_overlays_url` → `https://r2.bionic.app/3d/{species}/{tile_id}.glb`

Les tiles sont **pré-générés** côté backend cron et servis depuis R2/Cloudflare.

### 5.4 Métriques cibles Phase 2
| Métrique | Cible Phase 2 |
|---|---|
| Latence p99 utilisateur final | <100ms (mondial) |
| % requêtes servies par edge | >90% |
| Coût mensuel (10 000 users) | <50$/mois |
| Cold-start utilisateur perçu | 0ms |
| Capacity utilisateur simultané | illimité |

---

## 6. INTERFACES STANDARDISÉES

### 6.1 Contrat `bundle_essentiel_t0.json`

```json
{
  "_metadata": {
    "bundle_tier": "ESSENTIEL_T0",
    "source": "STATIC | DYNAMIC | EDGE",
    "generated_at": "2026-06-01T12:00:00Z",
    "ttl_sec": 3600,
    "schema_version": "1.0.0"
  },
  "waypoint": {"lat": 48.207, "lng": -68.382},
  "species": "chevreuil",
  "terrain_block": { "dem": [...], "slope": [...], "aspect": [...] },
  "meteo_block": null,
  "zones_block": { "zones": [{"id": "...", "polygon": [...], "type": "..."}] },
  "hotspots_block": { "hotspots": [...] },
  "salines_block": { "salines": [...] },
  "species_block": { "profile": {...}, "presence_mask": [...] },
  "corridors_block": { "corridors": [...], "anchor_mode": "TERRITORY_CONTINUOUS" },
  "affuts_block": null,
  "rendu_block": null
}
```

### 6.2 Contrat `bundle_delta_enrichi.json`

```json
{
  "_metadata": {
    "bundle_tier": "ENRICHI_TDELTA",
    "parent_essentiel_key": "...",
    "generated_at": "...",
    "schema_version": "1.0.0"
  },
  "meteo_block": { "temp": ..., "wind_deg": ..., "source": "open-meteo|lidar" },
  "affuts_block": { "affuts": [...], "contamination": [...] },
  "rendu_block": {
    "veineux": [...],
    "predictive_score": {...},
    "mvt_tiles_url": "https://r2.bionic.app/tiles/.../...",
    "3d_overlays_url": "https://r2.bionic.app/3d/.../..."
  }
}
```

### 6.3 Règles de composition

```
ESSENTIEL_T0  = terrain + zones + hotspots + salines + species + corridors_V5
ENRICHI_TDELTA = ESSENTIEL_T0 + meteo + affuts + contamination + comportement + connectivite_ecologique + corridors_vitaux
COMPLET_LUXE   = ENRICHI_TDELTA + predictive_v2 + veineux + 3D + MVT + overlays_lourds
```

---

## 7. FEUILLE DE ROUTE SÉQUENCÉE

### 🚀 PHASE 1A — Préparation (mois 1)
- ✅ P22ΩΩ_CLEANUP_LEGACY_FINAL (suppression V4 + datasets + 116 tests)
- ✅ P22ΩΩ_DECOUPAGE_V10_V20 (extraction packages)
- ⏳ Création `v30_future/territory_static_engine.py` (stub)
- ⏳ Création `v30_future/deferred_rendering_engine.py` (stub)

### 🚀 PHASE 1B — Static Engine (mois 2-3)
- ⏳ Provisioning S3/R2 bucket
- ⏳ Script `generate_static_bundles_cron.py`
- ⏳ Premier batch : 2.1M bundles (grille Québec 0.05°)
- ⏳ Endpoint `GET /api/v30/territoire/static-bundle`
- ⏳ Frontend : `useMapBundleV8` essaie static d'abord, dynamic en fallback

### 🚀 PHASE 1C — Deferred Rendering (mois 3-4)
- ⏳ Module `deferred_rendering_engine.py`
- ⏳ Endpoint `GET /api/v30/territoire/deferred-render`
- ⏳ Frontend : WebSocket ou poll secondaire `bundle_delta`

### 🚀 PHASE 2A — Cloudflare Workers (mois 6-8)
- ⏳ Setup compte Cloudflare Workers + R2
- ⏳ Miroir bundles statiques sur R2
- ⏳ Worker.ts edge logic
- ⏳ Routage DNS

### 🚀 PHASE 2B — MVT Tiles + 3D (mois 8-10)
- ⏳ Pré-génération MVT vectors (par espèce × zoom level)
- ⏳ Pré-génération 3D overlays (glTF)
- ⏳ Frontend MapLibre GL pour rendu GPU

### 🚀 PHASE 2C — WebSocket Live (mois 10-12)
- ⏳ Service WebSocket pour BIO-RÉACTEURS push
- ⏳ Mises à jour live des positions / contamination
- ⏳ Notifications territoriales

---

## 8. RÉSULTATS ATTENDUS

| Métrique | Aujourd'hui | Phase 1 (M3) | Phase 2 (M12) |
|---|---|---|---|
| Latence cold-start | 40-60s | **<3s** | **<100ms** |
| Latence p99 | 50s (avec 502) | **<2s** | **<100ms** |
| Capacity simultané | 1 (single-worker) | 4 (multi-worker) | **illimité (edge)** |
| Coût hosting | ~50$/mois | ~80$/mois | **<50$/mois** |
| Couverture territoire | 11 bundles caches | 2.1M bundles statiques | 2.1M + tiles + 3D |
| Mode offline | Non | Partiel (cache navigateur) | **Total (Service Worker)** |
| Cold-start utilisateur | 502 fréquent | 0% | 0% |

---

## 9. RISQUES & MITIGATIONS

| Risque | Impact | Mitigation |
|---|---|---|
| Storage R2/S3 ballooning | $$ | Compression gzip + TTL 30j |
| Données bio-précision périssables | Stale data | Cron quotidien + invalidation explicite |
| Sécurité bucket public | Fuite | URLs signées (24h expiry) |
| Coût Workers > 50$/mois | $$ | Free tier 100k req/jour + over-flow vers backend |
| Refus Emergent multi-worker | Blocage | Phase 1 reste compatible single-worker |

---

## 10. SIGNATURE
- **Doctrine** : BCE-4X ULTIME ABSOLU
- **Phase** : P22ΩΩ_PLAN_MODULARISATION_TERRITOIRE
- **Livrable** : 3/4 — Roadmap ZeroCost Engine
- **Validation** : COMMANDANT STEEVE-MAX

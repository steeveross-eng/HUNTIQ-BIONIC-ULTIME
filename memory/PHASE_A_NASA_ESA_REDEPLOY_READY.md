# PHASE A · NASA HLS + ESA Sentinel-2 · REDEPLOY READY

**Doctrine** : `P22ΩΩ_P1_FULL_PHASE_A_REDEPLOY_Ω` · COMMANDANT STEEVE-MAX · 2026-06-08
**Protocole** : BCE-4X ULTIME ABSOLU · Verrou Phase III · STRICT ADDITIF
**Statut** : ✅ PRÊT POUR REDEPLOY ELITE (validation E2E Preview complète)

---

## 1. FICHIERS MODIFIÉS (2 fichiers · additif strict)

| Fichier | Type | Diff résumé |
|---|---|---|
| `backend/integrations/p1_full/esa_sentinel2_p1_full.py` | Additif (fichier déjà additif) | +96 lignes : `is_credential_ready()`, `is_armed()`, `search_scenes()` via CDSE OData |
| `backend/routes/habitat_fusion_p1_ingest_router.py` | Mutation minimale (2 lignes · entrée map) | `_VALID_CLIENTS["esa_sentinel2_l2a"]["module"]` → `integrations.p1_full.esa_sentinel2_p1_full`, `download_fn` → `download_s2_tiles` |

**Note doctrinale** : Le legacy `integrations/ingestion_p1/esa_sentinel2_client.py` n'est PAS modifié (Verrou Phase III). Le router pointe désormais ESA vers le module P1_FULL pour cohérence search/download.

---

## 2. FIX 1 · NASA HLS `concept_id` (déjà sur Preview · ABSENT sur Elite)

**Bug** : `_resolve_granule_urls()` cherchait via `granule_name=granule_id` (échec, car `granule_id` est un concept_id CMR format `G..-LPCLOUD`).

**Fix** : `earthaccess.search_data(concept_id=granule_id, count=1)` + fallback `granule_ur`.

**Validation E2E Preview** (avant Phase A.2) :
- Job `869f6c57-2f6f-4387-9778-1e7c623d437b` · status=`completed` · 2/2 tiles success · 47 MB downloaded · 2/2 R2-synced.

**Validation Elite (post-deploy précédent)** :
- ❌ Job `237e0596-38f2-478c-83f9-3cf472c1eca4` · status=`completed_with_errors` · 3/3 tiles `not_found` → Confirmation que le fix n'a PAS été propagé.

---

## 3. FIX 2 · ESA Sentinel-2 STAC URL 404 → CDSE OData (NOUVEAU · Preview)

**Bug** : Le legacy `esa_sentinel2_client.py` utilisait `pystac_client.Client.open("https://catalogue.dataspace.copernicus.eu/stac")`. Vérifié manuellement (2026-06-07) : cet endpoint n'expose que **10 collections** (CLMS Burned Area + CCM Optical/SAR), **AUCUNE Sentinel-2**. Résultat : `results_count: 0` systématique.

**Fix** : Nouvelle fonction `search_scenes()` dans `esa_sentinel2_p1_full.py` utilisant CDSE OData officiel (`https://catalogue.dataspace.copernicus.eu/odata/v1/Products`) avec filtre `Collection/Name eq 'SENTINEL-2' and contains(Name,'MSIL2A') and OData.CSC.Intersects(...) and ContentDate/Start ...`. Cloud-cover filtré côté Python (Attributes/cloudCover) après `$expand=Attributes`.

**Validation E2E Preview** :
- `/clients` → ESA `client_version=V1.0-P1-FULL-PHASE-A` (routage OK)
- `dry_run=true` sur bbox QC limitrophes (-79,45,-74,50) · 2025-08-01→2025-09-30 · cc_max=20 → **3 produits L2A retournés** :
  - T17TPK · cc=0.001 · 269 MB
  - T18TVT · cc=7.48 · 1185 MB
  - T18TVS · cc=0.0001 · 1189 MB

**Cohérence search→download** : Le `scene_id` retourné (ex `S2B_MSIL2A_..._T18TVS_...` sans `.SAFE`) est aligné avec `_resolve_scene_product_id()` qui fait `contains(Name, scene_id)`. Le `product_id` (GUID) est également exposé en bonus (réutilisable directement par `download_url = f"{CDSE_DOWNLOAD_BASE}({Id})/$value"`).

---

## 4. RISQUES & ATTENTION POINTS

| # | Item | Status | Action |
|---|---|---|---|
| 1 | Workers Elite idx 3,4,5 manquants (5/8) | ⚠️ Aggravé depuis handoff | P2 (planifié) — non bloquant |
| 2 | Job store P1_FULL in-memory per-worker (polling 1/N hit-rate) | ⚠️ Robustesse | P2 (planifié R2 persistence) |
| 3 | Real ingestion ESA = ~270MB-1.2GB par produit | ✅ Géré | `max_tiles=1` recommandé pour validation Elite |
| 4 | CDSE OAuth2 token TTL 10min | ✅ Géré | Cache 9min + retry sur 401 (déjà implémenté) |

---

## 5. SÉQUENCE REDEPLOY ELITE (à exécuter par COMMANDANT)

1. **COMMANDANT** : Clic "Deploy" UI Emergent (depuis Preview pod actuel)
2. **AGENT** (post-deploy) : `curl /api/v30/runtime/tier-status` → confirmer uptime court + tier=ELITE
3. **AGENT** : `POST /api/v30/habitat-fusion/p1/ingest/trigger/nasa_hls?dry_run=true` (récupération concept_ids)
4. **AGENT** : `POST /api/v30/habitat-fusion/p1/ingest/trigger/nasa_hls?dry_run=false` avec `max_tiles=1, bands=["B04","B05"]` → attendu : status=`completed`, ~25-50 MB R2-synced
5. **AGENT** : `POST /api/v30/habitat-fusion/p1/ingest/trigger/esa_sentinel2_l2a?dry_run=true` → attendu : 3+ produits L2A
6. **AGENT** : (optionnel · sur ordre explicite) `POST .../trigger/esa_sentinel2_l2a?dry_run=false` avec `scene_ids=[<low_cc_product>], max_tiles=1` → attendu : ~270MB-1GB R2-synced

---

## 6. PROCHAINES PHASES (rappel)

- **Phase B** : LiDAR NRCan HRDEM (STAC AWS) + MFFP Forêt Ouverte (CKAN donneesquebec.ca)
- **P2** : Worker partial recovery watchdog + R2 job store persistence
- **P1 Frontend** : `PLAN_FRONTEND_202_BANNER_LKG_Ω` (banner DEGRADED/PRE-WARMING)
- **V7 Corridor Restoration** : toggle implementation (sur ordre)

---

**Préparé par** : Agent BCE-4X · Verrou Phase III maintenu · Aucune dépendance externe ajoutée · Aucun engine touché.
**Lint** : ✅ ruff/pyflakes clean (0 issues, 0 warnings)
**Tests E2E Preview** : ✅ NASA HLS (completed · 47MB) · ✅ ESA dry_run (3 produits L2A) · Sanity régression OK.

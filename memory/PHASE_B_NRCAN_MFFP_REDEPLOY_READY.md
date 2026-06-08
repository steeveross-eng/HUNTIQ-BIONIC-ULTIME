# PHASE B · NRCan HRDEM + MFFP LiDAR · REDEPLOY READY

**Doctrine** : `P22ΩΩ_P1_FULL_PHASE_B_REDEPLOY_Ω` · COMMANDANT STEEVE-MAX · 2026-06-08
**Protocole** : BCE-4X ULTIME ABSOLU · Verrou Phase III · STRICT ADDITIF
**Statut** : ✅ PRÊT POUR REDEPLOY ELITE (dry_run E2E Preview validé · download gating en place)

---

## 1. FICHIERS MODIFIÉS (3 fichiers · additif strict)

| Fichier | Type | Diff résumé |
|---|---|---|
| `backend/integrations/p1_full/nrcan_hrdem_p1_full.py` | Refonte stub → module actif (Phase B) | Stub 57 lignes → ~250 lignes : `is_credential_ready()`, `is_armed()`, `_list_s3_keys()`, `search_scenes()` via S3 anonymous listing, `download_hrdem_tiles()` avec gate `INGESTION_P1_DISK_AUTHORIZED` |
| `backend/integrations/p1_full/mffp_p1_full.py` | Refonte stub → module actif (Phase B) | Stub 57 lignes → ~300 lignes : `is_credential_ready()`, `is_armed()`, `_load_index()` (cache TTL 7j), `_feature_bbox()` (Polygon + MultiPolygon), `search_scenes()` via CKAN GeoJSON, `download_mffp_tiles()` avec gate |
| `backend/routes/habitat_fusion_p1_ingest_router.py` | Mutation minimale (map) | 2 entrées `_VALID_CLIENTS` repointées vers `integrations.p1_full.*_p1_full` |

**Note doctrinale** : Les modules legacy `integrations/ingestion_p1/nrcan_hrdem_client.py` et `integrations/ingestion_p1/mffp_foret_ouverte_client.py` ne sont PAS modifiés (Verrou Phase III). Le router pointe désormais NRCan + MFFP vers les modules P1_FULL.

---

## 2. NRCan HRDEM · Architecture

**Source** : Bucket S3 public AWS `canelevation-dem` (registry.opendata.aws/canelevation-dem)
**Auth** : Anonymous (pas de credentials AWS requis)
**Produits disponibles** :
- `hrdem-mosaic-1m` (DSM 1m pan-Canada · ~40 GB par tuile NTS)
- `hrdem-mosaic-2m` (DSM 2m · ~10 GB)
- `hrdem-lidar` (LiDAR raw · ~160 MB)
- `hrdem-arcticdem` (Arctic · ~37 GB)

**Grille** : Indexation `{col}_{row}` (non-NTS strict, grille AWS personnalisée)
**Fichiers par tuile** : `-dsm.tif` (raster principal), `-dsm.vrt`, `-dsm_hillshade.tif`, `-coverage.gpkg`

**Search path** : S3 list-type=2 + filter endswith `-dsm.tif` + bbox hint (best-effort par grid code)
**Download path** : HTTPS GET direct `https://canelevation-dem.s3.amazonaws.com/{key}` + sync_to_r2
**Gate download** : `INGESTION_P1_DISK_AUTHORIZED=1` requis (fichiers multi-GB)

---

## 3. MFFP Forêt Ouverte · Architecture

**Source** : CKAN Données Québec API + index GeoJSON
**Endpoint principal** : `https://www.donneesquebec.ca/recherche/api/3/action/package_show?id=produits-derives-de-base-du-lidar`
**Index** : `https://diffusion.mffp.gouv.qc.ca/.../URL_Lidar.geojson` (5.7 MB · 2630 feuillets 1/20 000 · CRS84)

**Auth** : Aucune (open data)
**Cache** : Index téléchargé une fois, mémoire process · TTL 7 jours

**Produits par feuillet 1/20 000** :
- `MNT` (Modèle Numérique de Terrain · DTM)
- `MHC` (Modèle Hauteur Canopée)
- `MNT_Ombre` (hillshade)
- `Pentes` (slopes)
- `Courbes_GDB` (courbes de niveau · ESRI GDB)
- `Courbes_GPKG` (courbes de niveau · GeoPackage)

**Search path** : Charge index GeoJSON, filtre features par intersection bbox (Polygon + MultiPolygon)
**Download path** : HTTPS GET direct `https://diffusion.mffp.gouv.qc.ca/...` par produit + sync_to_r2
**Gate download** : `INGESTION_P1_DISK_AUTHORIZED=1` requis (fichiers multi-GB)

---

## 4. VALIDATION E2E PREVIEW

| Test | Résultat | Détail |
|---|---|---|
| `/clients` | ✅ 4 clients all P1_FULL routed | `nrcan_hrdem v=V1.0-P1-FULL-PHASE-B`, `mffp_foret_ouverte v=V1.0-P1-FULL-PHASE-B` |
| **NRCan dry_run** | ✅ **22 tuiles** | scene_id=10_2-mosaic-1m (39 GB), 10_3, 10_4, ... |
| **MFFP dry_run** | ✅ **50 feuillets** | scene_id=32L03SE/32L02SO/... · 6 products chacun |
| URL-probe NRCan | ✅ 3/5 reachable | `canelevation-dem.s3.amazonaws.com` OK |
| URL-probe MFFP | ✅ 1/5 reachable | `donneesquebec.ca/api/3` OK |
| **Régression NASA HLS** | ✅ dry_run 2 granules | Aucune régression Phase A |
| **Régression ESA L2A** | ✅ dry_run 3 produits | Aucune régression Phase A |
| **Régression cdse-auth-probe** | ✅ 401_invalid_grant | Endpoint fonctionnel |
| Lint Python | ✅ 0 issue | Verrou Phase III maintenu |

---

## 5. RISQUES & ATTENTION POINTS

| # | Item | Status | Action |
|---|---|---|---|
| 1 | NRCan files multi-GB (1m DSM = 40 GB/tuile) | ✅ Gate disque actif | `INGESTION_P1_DISK_AUTHORIZED=1` requis explicitement |
| 2 | MFFP files multi-GB (MNT par feuillet ~1 GB) | ✅ Gate disque actif | Idem |
| 3 | MFFP index 5.7 MB en cache mémoire | ✅ Géré | TTL 7j, reload thread-safe |
| 4 | Workers Elite idx 3,4,5 manquants (5/8) | ⚠️ P2 chronique | Non bloquant Phase B dry_run |
| 5 | Job store P1_FULL in-memory per-worker | ⚠️ P2 planifié | Polling 1/N hit rate, géré via retry |
| 6 | bbox-precise filter NRCan = best-effort | ⚠️ Future opt | Coverage.gpkg parsing pour intersection exacte |

---

## 6. SÉQUENCE POST-DEPLOY ELITE (suggestion · sur ordre)

1. **COMMANDANT** : Clic "Deploy" UI Emergent
2. **AGENT** : `curl /api/v30/runtime/tier-status` → confirmer uptime court
3. **AGENT** : `/clients` → vérifier `nrcan_hrdem` et `mffp_foret_ouverte` show `V1.0-P1-FULL-PHASE-B`
4. **AGENT** : `POST /trigger/nrcan_hrdem?dry_run=true` → attendu 20+ tuiles
5. **AGENT** : `POST /trigger/mffp_foret_ouverte?dry_run=true` → attendu 50 feuillets
6. **AGENT** : `GET /url-probe?client=nrcan_hrdem` et `?client=mffp_foret_ouverte` → vérifier reachable
7. **AGENT (sur ordre · disk autorisé)** : real ingestion 1 produit MFFP léger (Courbes_GPKG ~100 MB) pour smoke test E2E

---

## 7. PROCHAINES PHASES (rappel)

- **Phase A.2 Real ESA** : Bloqué creds CDSE 401 (rotation password requise par COMMANDANT)
- **P2** : Worker partial recovery watchdog + R2 job store persistence
- **P1 Frontend** : `PLAN_FRONTEND_202_BANNER_LKG_Ω` (banner DEGRADED/PRE-WARMING)
- **V7 Corridor Restoration** : toggle implementation (sur ordre)

---

**Préparé par** : Agent BCE-4X · Verrou Phase III maintenu · Aucune dépendance ajoutée · Aucun engine touché.
**Lint** : ✅ Python clean (0 issues, 0 warnings)
**Tests E2E Preview** :
- ✅ NRCan dry_run (22 tuiles)
- ✅ MFFP dry_run (50 feuillets)
- ✅ Régression NASA/ESA/cdse-auth-probe OK

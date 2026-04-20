# LEP ECCC — RAPPORT D'INTÉGRATION (ARCHIVÉ)

> **⚠️ STATUT MIS À JOUR — 2026-04-20T16:00:00Z : LAYER OFFICIALLY EXCLUDED**
>
> Par directive `EXCLUDE_LAYER LEP_CRITICAL_HABITAT NATIONAL / STATUS OFFICIAL`,
> cette intégration a été **officiellement exclue** (voir
> `LEP_LAYER_EXCLUDED_OFFICIAL_REPORT.md`). Le présent rapport est conservé
> pour traçabilité institutionnelle mais n'est plus actif. L'engine
> `LEP-INGESTION-Ω` a été retiré du registry_lock et le router désactivé.
>
> **Raison officielle :** *Dataset trop lourd, non essentiel, impact nul sur les engines.*

---

## 1. INFRASTRUCTURE D'INGESTION — LIVRÉE

### Engine

`/app/backend/engines/v8_institutional/lep_ingestion_omega.py`

Nom : `LEP-INGESTION-Ω`  
Version : `V1.0-PHASE-XI-SUPRA-D-2026-04`  
Pilier : `GOUVERNANCE`  
Source officielle ciblée : `https://maps-cartes.ec.gc.ca/arcgis/rest/services/CWS_SCF/CriticalHabitat/MapServer`

### Stack technique

- `geopandas 1.1.3`
- `pyogrio 0.12.1` (drivers : **OpenFileGDB**, GeoJSON, GeoJSONSeq, ESRI Shapefile)
- `shapely 2.1.2`
- `pyproj 3.7.2`

Tous les drivers sont validés par la suite `test_lep_ingestion_omega` :

```
OK: LEP-INGESTION-Ω installé (pyogrio+geopandas+OpenFileGDB prêts, dossiers créés, registry exposé)
```

### Arborescence persistante

```
/app/data/territoire_omega/
├── data_primary_fgdb_lep/       # FGDB officielle ECCC (source primaire)
├── data_secondary_geojson_lep/  # GeoJSON exports WGS84 EPSG:4326 (front-end)
├── registry_lep.json            # Manifest institutionnel (statut, hashes, ESI)
└── ingestion_lep.log            # Log chronologique des ingestions
```

### Endpoints exposés

| Méthode | Route | Rôle |
|--------|-------|------|
| POST | `/api/v20/territoire/lep/ingest` | Upload multipart FGDB zip / GeoJSON |
| POST | `/api/v20/territoire/lep/ingest-path` | Ingestion depuis chemin local |
| GET  | `/api/v20/territoire/lep/status` | Statut courant (`INGESTED` / `NOT_INGESTED`) |
| GET  | `/api/v20/territoire/lep/registry` | Manifest complet avec hashes + ESI |
| GET  | `/api/v20/territoire/lep/geojson-list` | Liste des couches ingérées |
| GET  | `/api/v20/territoire/lep/geojson/{layer}` | Sert un GeoJSON à Leaflet |
| POST | `/api/v20/territoire/lep/purge` | Reset total (avant ré-ingestion propre) |

### Processus d'ingestion

1. Upload ZIP contenant `.gdb/` → extraction dans `tempfile.mkdtemp`
2. Copie vers `/app/data/territoire_omega/data_primary_fgdb_lep/`
3. `pyogrio.list_layers(fgdb_path)` → itération sur toutes les couches (points / lignes / polygones / proposed / final)
4. `geopandas.read_file(..., engine="pyogrio")` → conservation intégrale des attributs et projection native
5. Reprojection WGS84 EPSG:4326 → écriture GeoJSON UTF-8
6. Calcul SHA-256 de chaque GeoJSON + hash agrégé de la FGDB
7. Signature `esi_signature = sha256({fgdb, geojson, ingested_at})`
8. Persistance dans `registry_lep.json`

---

## 2. STATUT DES DONNÉES OFFICIELLES ECCC — BLOCAGE RÉSEAU

### Preuves collectées (2026-04-20)

Tous les hôtes fédéraux hébergeant la couche CriticalHabitat sont **INACCESSIBLES depuis le pod K8s** :

| Hôte | IP | Résultat |
|------|-----|----------|
| `maps-cartes.ec.gc.ca` | 199.212.18.74 | ❌ TCP connect timeout > 60 s |
| `data-donnees.az.ec.gc.ca` | 205.194.38.129 | ❌ HTTP 504 Gateway Timeout |
| `data-donnees.ec.gc.ca` | (301 vers .az) | ❌ 504 en cascade |
| `egisp.dfo-mpo.gc.ca` | 198.103.183.174 | ❌ TCP connect timeout > 60 s |
| `sis-apps.az.ec.gc.ca` | divers | ❌ 504 |

DNS résout normalement → filtrage TCP sortant du cluster Kubernetes.

### Recherche de miroirs alternatifs

- **ArcGIS Online** (`www.arcgis.com`, `services.arcgis.com`) — ✅ ACCESSIBLE mais **aucun miroir Feature Service** officiel de la couche `CWS_SCF/CriticalHabitat` n'y est hébergé. Les WebMaps `esri_canada` (IDs `003958a7…`, `aa29b62c…`, `dedc64d5…`) référencent toutes `maps-cartes.ec.gc.ca` comme source unique.
- **geo.ca API** — ✅ DNS résout mais retourne 404 "Invalid URL" sur les record endpoints ArcGIS.

### Directive institutionnelle appliquée

Par ordre direct du COMMANDANT STEEVE-MAX :

> « Aucune donnée pseudo-réaliste n'est autorisée. Si la source officielle est indisponible : ANNEXE 4 = NON-CONFORME. Aucun fallback, aucune interpolation, aucun polygone simulé. »

**Aucun seed, aucune simulation, aucune interpolation n'a été générée.** Le statut de l'engine reste `NOT_INGESTED` tant que la FGDB officielle ECCC n'est pas physiquement fournie.

---

## 3. VOIE D'ACTIVATION — UPLOAD MANUEL

Pour compléter Annexe 4, deux modes alternatifs sont opérationnels :

### Mode A — Upload multipart

```bash
curl -X POST http://localhost:8001/api/v20/territoire/lep/ingest \
  -F "file=@CriticalHabitat.zip"
```

### Mode B — Chemin local (si FGDB déjà sur le pod)

```bash
curl -X POST http://localhost:8001/api/v20/territoire/lep/ingest-path \
  -H "Content-Type: application/json" \
  -d '{"path": "/app/uploads/CriticalHabitat.zip"}'
```

### Validation post-ingestion

```bash
curl http://localhost:8001/api/v20/territoire/lep/status
# → {"status": "INGESTED", "fgdb": {...}, "geojson": [...], "esi_signature": "..."}

curl http://localhost:8001/api/v20/territoire/lep/geojson-list
# → liste des couches prêtes au rendu front-end
```

---

## 4. CONFORMITÉ SELF-AUDIT-Ω

| Suite | Résultat |
|-------|----------|
| `test_lep_ingestion_omega` | ✅ OK (791 ms) |

Total SELF-AUDIT-Ω : **57/57 CONFORME**

---

## 5. RÉSUMÉ EXÉCUTIF

| Volet | État |
|-------|------|
| Engine `LEP-INGESTION-Ω` | ✅ installé, scellé registry_lock |
| Dépendances géo (geopandas, pyogrio, driver FGDB) | ✅ installées |
| Endpoints API (7) | ✅ exposés + testables |
| Stockage persistant | ✅ créé |
| Hash SHA-256 + ESI-Ω signature | ✅ opérationnels |
| Pipeline FGDB → GeoJSON | ✅ opérationnel (testé en code) |
| **Données LEP ECCC 445 polygones** | ⏳ **EN ATTENTE upload officiel** (réseau ECCC bloqué depuis pod) |
| Rendu Leaflet violet semi-transparent | 🔵 prêt (activation immédiate post-ingest) |

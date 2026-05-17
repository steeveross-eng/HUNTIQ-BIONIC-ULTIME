# 🏛️ PLAN_MODULARISATION_TERRITOIRE — DOCUMENT MAÎTRE
**Phase** : P22ΩΩ_PLAN_MODULARISATION_TERRITOIRE
**Date** : 2026-05-19 · **Doctrine** : BCE-4X ULTIME ABSOLU
**Commandant** : STEEVE-MAX

> ⚠️ **PLAN INSTITUTIONNEL COMPLET — Aucune modification de code dans cette phase.**

---

## 📋 LIVRABLES (4)

| # | Document | Statut |
|---|---|---|
| 1 | `p22omegaomega_analyse_monolithique_server.md` | ✅ LIVRÉ |
| 2 | `p22omegaomega_plan_de_decoupage_v10_v20.md` | ✅ LIVRÉ |
| 3 | `p22omegaomega_roadmap_zero_cost_engine.md` | ✅ LIVRÉ |
| 4 | `p22omegaomega_cleanup_legacy_final.md` | ✅ LIVRÉ |
| 5 | `p22omegaomega_plan_modularisation_master.md` | ✅ CE DOCUMENT |

---

## 🎯 ARCHITECTURE MODULAIRE CIBLE

### Vue d'ensemble

```
TERRITOIRE Ω · ARCHITECTURE MODULAIRE CIBLE
═══════════════════════════════════════════

┌──────────────────────────────────────────────────────────────────────┐
│ FRONTEND React 19                                                    │
│ /pages/MonTerritoireBionicPage.jsx (orchestrateur léger)             │
│ /components/territoire/ (panneaux, layers, widgets)                  │
│ /hooks/useMapBundleV8.js (consommateur bundle + cache global window) │
│ /lib/bionicBundleCache.js (cache LRU TTL adaptatif)                  │
└────────────────────────────┬─────────────────────────────────────────┘
                             │ GET /api/v20/territoire/bundle
                             ▼
┌──────────────────────────────────────────────────────────────────────┐
│ BACKEND · /api/v20/territoire/bundle handler (server.py minimal)     │
└────────────────────────────┬─────────────────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────────────┐
│ COUCHE V20 — Composition                                             │
│ engines/v8_institutional/v20/                                        │
│ ├── territoire_logic.py          ← orchestrateur principal           │
│ ├── cache_orchestrator.py        ← LRU + Redis + disque + TTL tiers  │
│ ├── daemons.py                   ← warmup + prechauffage             │
│ ├── compliance_omega.py          ← V5 monitor + Resend alerts        │
│ └── rendu_avance.py              ← post-V5 (veineux + predictive)    │
└────────────────────────────┬─────────────────────────────────────────┘
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
┌──────────────────────────────────────────────────────────────────────┐
│ COUCHE V10 — Extraction scientifique                                 │
│ engines/v8_institutional/v10/                                        │
│ ├── terrain_pipeline.py          ← compute_terrain_block             │
│ ├── meteo_pipeline.py            ← open_meteo + lidar_irda fallback  │
│ ├── biologie_pipeline.py         ← zones + hotspots + salines        │
│ └── affuts_pipeline.py           ← affuts + visibilité + acoustique  │
└──────────────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────────────┐
│ COUCHE V5 — Corridors organiques natifs                              │
│ engines/v8_institutional/engine_ia_corridors_organic_omega.py        │
│ (INCHANGÉ — science conservée intacte)                               │
└──────────────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────────────┐
│ COUCHE V30 FUTURE — ZeroCost                                         │
│ engines/v8_institutional/v30_future/                                 │
│ ├── territory_static_engine.py   ← bundles statiques S3/R2           │
│ ├── deferred_rendering_engine.py ← rendu différé                     │
│ └── zero_cost_engine.py          ← edge Cloudflare Workers           │
└──────────────────────────────────────────────────────────────────────┘
```

---

## 📡 INTERFACES STANDARDISÉES (Contrats JSON)

### Bundle T0 ESSENTIEL (3 600s TTL)

```json
{
  "_metadata": {
    "bundle_tier": "ESSENTIEL_T0",
    "schema_version": "1.0.0",
    "generated_at": "2026-05-19T12:00:00Z",
    "ttl_sec": 3600,
    "source": "DYNAMIC"
  },
  "waypoint": {"lat": 48.207, "lng": -68.382},
  "species": "chevreuil",
  "terrain_block": {
    "dem": [...],
    "slope": [...],
    "aspect": [...],
    "drainage": [...]
  },
  "meteo_block": {
    "temp_c": 12,
    "wind_deg": 225,
    "wind_speed_kmh": 15,
    "humidity": 65,
    "pressure_hpa": 1013,
    "source": "open-meteo | lidar-irda-v11"
  },
  "zones_block": {
    "zones": [{"id": "z1", "polygon": [...], "type": "vital|repos|alimentation"}]
  },
  "hotspots_block": {
    "hotspots": [{"id": "h1", "lat": ..., "lng": ..., "score": 0.87}]
  },
  "salines_block": {
    "salines": [{"id": "s1", "lat": ..., "lng": ..., "minerals": {...}}]
  },
  "species_block": {
    "profile": {...},
    "presence_mask": [...],
    "weighting": {...}
  },
  "corridors_block": {
    "corridors": [{"id": "c1", "path": [[...], [...]], "intensity": 0.85}],
    "anchor_mode": "TERRITORY_CONTINUOUS"
  }
}
```

### Bundle T+Δ ENRICHI (24h TTL, produit par BG_CACHE)

```json
{
  "_metadata": {
    "bundle_tier": "ENRICHI_TDELTA",
    "schema_version": "1.0.0",
    "parent_essentiel_key": "lat_lon_species_month_wind",
    "generated_at": "2026-05-19T12:01:30Z",
    "ttl_sec": 86400,
    "bg_cache_origin": "P22ΩΩ_ESSENTIEL_1WORKER"
  },
  "...ESSENTIEL fields...": "...",
  "affuts_block": {
    "affuts": [{"id": "a1", "lat": ..., "lng": ..., "score": 0.92}],
    "contamination": [{"cone": [...], "wind_deg": 225}],
    "visibility_radii": [...]
  },
  "comportement_block": {
    "comportement_biologique": {...},
    "trophic_behavior": {...},
    "population_dynamics": {...}
  },
  "connectivite_block": {
    "interzones": [...],
    "corridors_vitaux": [...]
  }
}
```

### Bundle LUXE COMPLET (opt-in)

```json
{
  "_metadata": { "bundle_tier": "COMPLET_T0", "...": "..." },
  "...ENRICHI fields...": "...",
  "predictive_block": {
    "predictive_omega_v2": {...},
    "vision_ecologique": {...}
  },
  "rendu_avance_block": {
    "veineux": [...],
    "mvt_tiles_url": "...",
    "3d_overlays_url": "..."
  }
}
```

### Règles de composition

```
ESSENTIEL_T0   = terrain + meteo + zones + hotspots + salines + species + corridors_V5
ENRICHI_TDELTA = ESSENTIEL_T0 + affuts + contamination + comportement + connectivite
COMPLET_T0     = ENRICHI_TDELTA + predictive_v2 + veineux + MVT + 3D + overlays_lourds
```

---

## 🛠️ PLAN DE DÉCOUPAGE V10/V20 (10 étapes)

| # | Étape | Effort | Risque |
|---|---|---|---|
| 0 | CLEANUP_LEGACY_FINAL | 1j | 🟢 Low |
| 1 | Création packages `v10/` `v20/` `v30_future/` | 0.5j | 🟢 Low |
| 2 | Extraction `v20/cache_orchestrator.py` | 1j | 🟡 Med |
| 3 | Extraction `v20/daemons.py` | 1j | 🟡 Med |
| 4 | Extraction `v20/compliance_omega.py` | 1j | 🟡 Med |
| 5 | Extraction `v20/rendu_avance.py` | 2j | 🟠 High |
| 6 | Wrapper `v10/terrain_pipeline.py` | 0.5j | 🟢 Low |
| 7 | Wrapper `v10/meteo_pipeline.py` | 0.5j | 🟢 Low |
| 8 | Extraction `v10/biologie_pipeline.py` | 2j | 🟠 High |
| 9 | Extraction `v10/affuts_pipeline.py` (la plus grosse) | 3j | 🔴 Critical |
| 10 | Extraction `v20/territoire_logic.py` + parallélisation asyncio | 2j | 🟠 High |

**Total** : ~14 jours d'effort (3 semaines avec marge).

---

## 🌐 ROADMAP ZERO-COST ENGINE

| Phase | Timeline | Cible |
|---|---|---|
| **Phase 1A** | Mois 1 | Cleanup + découpage V10/V20 |
| **Phase 1B** | Mois 2-3 | Static Engine (S3/R2 + cron) |
| **Phase 1C** | Mois 3-4 | Deferred Rendering Engine |
| **Phase 2A** | Mois 6-8 | Cloudflare Workers edge |
| **Phase 2B** | Mois 8-10 | MVT Tiles + 3D pré-générés |
| **Phase 2C** | Mois 10-12 | WebSocket Live BIO-RÉACTEURS |

---

## 🧹 NETTOYAGE LEGACY (à exécuter AVANT extraction)

| Catégorie | Items | Volume |
|---|---|---|
| A — Engines V4 sans usage prod | engine_ia_corridors_omega.py, federal_datasets_omega.py, science_gaps_datasets.py | ~750 lignes |
| Tests phases historiques | 116 fichiers `test_phase_*.py` | ~12 000 lignes archivées |
| Tests rendu legacy | 12 fichiers `test_render_*.py` | ~1 500 lignes archivées |

**Total Phase 0** : **~14 250 lignes** purgeables/archivables.

---

## 🛡️ CONFORMITÉ Ω — Tests de non-régression

À exécuter après chaque étape de découpage :

| Test | Critère |
|---|---|
| C1 — `/api/v20/territoire/bundle` chevreuil | HTTP 200 + `X-Bundle-Tier` set |
| C2 — `/api/health` | HTTP 200 < 1s |
| C3 — Screenshot Playwright | 90+ polylines · CONFORMITÉ Ω 100% |
| C4 — Bundle JSON cohérence | zones≥1 · corridors≥1 · salines≥1 · hotspots≥1 |
| C5 — Bundle 5 espèces × 2 saisons | 0 erreur · 0 régression métrique |
| C6 — Cache HIT post-restart | Bundle restauré OK |
| C7 — Widget Premium | Rendu OK sur user admin |

---

## ⚠️ CONTRAINTES INVIOLABLES

| Garde-fou | Application |
|---|---|
| ❌ Aucune modification des engines scientifiques Ω | Fichiers Ω **intacts** |
| ❌ Aucune modification scoring/corridors/zones/salines/espèces | Algorithmes **inchangés** |
| ❌ Aucune modification du contrat bundle JSON public | Clés/valeurs/types **inchangés** |
| ❌ Aucun impact sur TERRITOIRE_ESSENTIEL_1WORKER | Mode 3-cercles **préservé** |
| ❌ Aucun impact sur TTL ESSENTIEL_T0=3600s | Stratégie cache **préservée** |
| ❌ Aucun impact sur Conformité Ω 100% | HUD validé après chaque étape |

---

## 📊 GAINS ATTENDUS POST-MODULARISATION COMPLÈTE

| Métrique | Aujourd'hui | Post-Phase 1 | Post-Phase 2 |
|---|---|---|---|
| Lignes monolithe principal | 7 070 | ~3 000 (split) | ~2 000 (split + edge offload) |
| Latence cold-start utilisateur | 40-60s (502) | <3s | <100ms (edge) |
| Latence p99 | 50s | <2s | <100ms |
| Capacity simultané | 1 (single-worker) | 4+ (multi-worker) | illimité (edge) |
| Coût hosting | ~50$/mois | ~80$/mois | <50$/mois |
| Couverture cache | 11 bundles | 2.1M bundles statiques | 2.1M + tiles + 3D |
| Cold-start utilisateur perçu | 502 fréquent | 0% | 0% |

---

## ✅ STATUT FINAL DU PLAN

| Composant | Statut |
|---|---|
| 📋 Analyse monolithe `v20_performance_bundle.py` (1982 lignes) | ✅ DOCUMENTÉE |
| 📋 Analyse monolithe `territoire_v10_supra.py` (1495 lignes) | ✅ DOCUMENTÉE |
| 📋 Cartographie dépendances croisées | ✅ DOCUMENTÉE |
| 📋 Liste modules legacy à supprimer (3 backend + 128 tests) | ✅ ÉTABLIE |
| 📋 Définition pipelines V10 (4) | ✅ ÉTABLIE |
| 📋 Définition pipelines V20 (5) | ✅ ÉTABLIE |
| 📋 Définition pipelines V30 future (3) | ✅ ÉTABLIE |
| 📋 Interfaces JSON standardisées (3 tiers) | ✅ ÉTABLIES |
| 📋 Règles de composition | ✅ ÉTABLIES |
| 📋 Plan séquentiel V10/V20 (10 étapes) | ✅ ÉTABLI |
| 📋 Tests de conformité Ω par étape | ✅ ÉTABLIS |
| 📋 Roadmap ZeroCost Engine (3 phases) | ✅ ÉTABLIE |
| 📋 Plan Static Engine | ✅ ÉTABLI |
| 📋 Plan Deferred Rendering Engine | ✅ ÉTABLI |
| 📋 Plan cleanup legacy | ✅ ÉTABLI |
| 🛡️ Conformité Ω maintenue (aucun code modifié) | ✅ GARANTIE |
| 🛡️ Aucun impact TERRITOIRE_ESSENTIEL_1WORKER | ✅ GARANTI |

---

## 🎯 PROCHAINE DIRECTIVE ATTENDUE

Le plan complet est désormais à disposition du Commandant. Aucune ligne de code
n'a été modifiée. Les 4 livrables sont archivés dans `/app/memory/audit_provenance/`.

**Options disponibles** :

a) **Approuver et lancer Phase 0** (Cleanup legacy final — Étape 1+2 du plan)
b) **Approuver et lancer Phase 1A** (Création packages `v10/` `v20/` `v30_future/`)
c) **Approuver l'ensemble Phase 1** (Étapes 1→10 du découpage)
d) **Réviser un livrable spécifique** avant exécution

---

## 📋 SIGNATURE
- **Doctrine** : BCE-4X ULTIME ABSOLU
- **Phase** : P22ΩΩ_PLAN_MODULARISATION_TERRITOIRE
- **Livrables** : 5/5 (4 documents + ce master)
- **Date** : 2026-05-19
- **Conformité Ω** : 100% MAINTENUE (aucun code modifié)
- **Validation** : EN ATTENTE de COMMANDANT STEEVE-MAX

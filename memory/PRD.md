# HUNTIQ-V6 — PRD (Product Requirements Document)
## PROTOCOLE BCE-4X | STEEVE-MAX-x3200-V6-CORE

---

## 1. Problème Original

STEEVE-MAX dirige la reconstruction et l'évolution du projet HUNTIQ-V6, une plateforme de chasse intelligente au Québec. Le projet suit un protocole de gouvernance strict (BCE-4X, MAX ULTRA, STEEVE-MAX) avec politique ZÉRO PERTE, ZÉRO RÉGRESSION.

## 2. Utilisateur Principal

- **STEEVE-MAX** — Autorité suprême, chasseur expert, directeur technique
- Langue: Français
- Région: Québec, Canada

## 3. Architecture

- **Backend:** FastAPI (Python) sur port 8001
- **Frontend:** React (CRA + craco) sur port 3000
- **Base de données:** MongoDB
- **APIs externes:** Open-Meteo (météo), Overpass API (OSM terrain/sentiers)
- **Branche active:** `STEEVE-MAX-x3200-V6-CORE` (EXCLUSIVEMENT)

## 4. Fonctionnalités Implémentées

### 4.1 Moteurs Backend (84+ modules)
- `access_engine_v6` — Routage terrain A*/Dijkstra avec priorité sentiers réels (x0.1)
- `access_clarity_engine_v7` — **NOUVEAU** — Pipeline de lissage + TCS (Terrain Clarity Score)
- `bionic_stand_recommendation_engine` — Recommandation d'affûts
- `hunt_orchestrator` — Orchestrateur de session de chasse
- `terrain_nav` — Navigation terrain avec graphe
- `zone_engine_core_v2` — Zones bionic organiques
- `weather_v3` — Météo et modèle de vent

### 4.2 Frontend
- `StandsMapLayer.jsx` — Carte des affûts avec légende GOLDEN v2.0, rendu v7 (TCS, glow bleu)
- `MapPage.jsx` — Carte interactive avec panneau CARTES HF (7 couches haute-fidélité)
- `HighFidelityMapsPanel.jsx` — **NOUVEAU** — Sélecteur de couches WMS (LIDAR, Canopy, etc.)
- `HighFidelityMapLayers.jsx` — **NOUVEAU** — Rendu WMS des couches sur la carte

### 4.3 access_clarity_engine_v7 (Implémenté 2026-03-29)
- `smoother.py` — Lissage: suppression zigzags + Douglas-Peucker + Catmull-Rom
- `scorer.py` — TCS 6 composantes: Alignement sentiers (30%), Lissage (20%), Pénétrabilité (15%), Topographie LIDAR (15%), Hydrologie (10%), Effort réel (10%)
- `clarity_engine.py` — Pipeline complet + auto-correction + rendu visuel bleu-clair
- `router.py` — API `/api/v7/clarity/{compute|score|status}`
- Tests: 11/11 passés
- Intégré dans `hunt_orchestrator/access_engine.py`

### 4.4 Cartes Haute-Fidélité (Implémenté 2026-03-29)
- LIDAR HD, Canopée, Orthophoto HR, Hydrologie, Chemins forestiers, Neige/Sol, Pente DEM

## 5. Documents & Audits Produits

- `architecture/access_clarity_engine_v7_architecture.md` — Architecture v7 complète
- `architecture/saline_module_ULTIME_architecture.md` — Architecture Salines BIONIC ULTIME
- `audit/post_purge_integrity_check.md` — Audit d'intégrité post-purge V1-V5
- `GOVERNANCE.md` — Gouvernance BCE-4X (14 sections)

## 6. Backlog Prioritisé

### P0 (Critique)
- [x] ÉTAPE 1: access_clarity_engine_v7 complet
- [x] ÉTAPE 2: Cartes Haute-Fidélité
- [x] ÉTAPE 3: Audit post-purge
- [x] ÉTAPE 4: Architecture Salines ULTIME

### P1 (Important)
- [ ] ULTRA-MAX++ Firewall (Phase C) — Geo-fencing urbain avec Shapely
- [ ] Preuves visuelles multi-scénarios avant/après chemins v7
- [ ] Implémentation module Salines BIONIC ULTIME

### P2 (GELÉ — En attente validation STEEVE-MAX)
- [ ] Purge frontend `shadcn`/`utils`
- [ ] Pression historique de chasse dans `choix_affuts`
- [ ] Phase BSAA-2 (Social Ads module)
- [ ] Merge vers `main` — STRICTEMENT INTERDIT

## 7. Contraintes Techniques

- Légende carte: DOM pur (PAS L.control) pour éviter chevauchements
- Sentiers OSM: priorité x0.1 (trails) vs x3.0 (hors-sentier)
- Terminologie: ZÉRO référence V1-V5 dans le code actif
- Branche: EXCLUSIVEMENT `STEEVE-MAX-x3200-V6-CORE`

# SCIENCE_Ω_GAPS_RESOLVED — Gaps scientifiques traités

**Date de résolution:** 2026-04-19

## Résumé

| # | Gap original | Statut | Résolution |
|---|---|---|---|
| 1 | Inventaire forestier par essence | REFERENCED | MFFP Carte écoforestière v5 (2019-2024) — essences dominantes par peuplement |
| 2 | Pédologie Ca/Na échangeables | REFERENCED | IRDA Échantillonnage national des sols 2018-2022 |
| 3 | CWD/MDC par région | REFERENCED | CWD Alliance Dashboard + MFFP surveillance zones MDC |
| 4 | Pression chasse historique | REFERENCED | MFFP Bilan exploitation faune 5 ans |
| 5 | APIs temps réel | PARTIAL | Open-Meteo live intégré ; NOAA/USFWS offline |
| 6 | CMIP6 climat futur | **RESOLVED** | ENGINE-CLIMAT-FUTUR-Ω ingère SSP2-4.5 (IPCC AR6 Atlas + Ouranos QC) |

## Détails par gap

### Gap #1 — Inventaire forestier par essence (REFERENCED)
- **Impact initial :** `feuillus_ratio` proxy seul dans HABITAT-SUPRA et NUTRITION-V12-SUPRA
- **Source :** MFFP Carte écoforestière du Québec méridional v5 — https://www.donneesquebec.ca/recherche/dataset/carte-ecoforestiere-avec-perturbations
- **Status :** REFERENCED dans catalog JSON `gaps_resolved[]`. Ingestion batch manuelle (téléchargement shapefile annuel). Pas de streaming RSS disponible.
- **Backlog :** script Python d'ingestion shapefile → enrichir terrain_v10 avec essence_dominante

### Gap #2 — Pédologie Ca/Na échangeables (REFERENCED)
- **Impact initial :** `ENGINE-SOL-SUPRA` utilise des indices proxies drainage+canopy
- **Source :** IRDA Propriétés chimiques des sols agricoles 2018-2022 — https://www.irda.qc.ca
- **Status :** REFERENCED. Accès sur demande (pas d'API ouverte).
- **Backlog :** demande formelle IRDA + ingestion CSV

### Gap #3 — CWD/MDC heatmap (REFERENCED)
- **Impact initial :** diseases listées qualitativement dans SPECIES_PROFILE, pas de heatmap régionale
- **Source :** CWD Alliance Data Dashboard — https://cwd-info.org/cwd-data-dashboard + MFFP surveillance MDC
- **Status :** REFERENCED. Import CSV annuel possible, pas de streaming.
- **Backlog :** parser CSV + génération GeoJSON + layer MVT `cwd_heatmap`

### Gap #4 — Pression chasse historique (REFERENCED)
- **Impact initial :** STRESS-ANTHROPIQUE-Ω ne croise pas les récoltes réelles
- **Source :** MFFP Statistiques chasse-pêche — https://mffp.gouv.qc.ca/la-faune/statistiques-chasse-peche
- **Status :** REFERENCED. PDFs annuels, pas d'API.
- **Backlog :** parseur PDF (Camelot/pdfplumber) → enrichir `stress_anthropique.harvest_pressure`

### Gap #5 — APIs temps réel (PARTIAL)
- **Impact initial :** catalog figé au moment d'ingestion, pas de sync
- **Actuellement intégré :** Open-Meteo live (realtime=true, realtime via `terrain_v10_supra.py` ↔ `lidar_irda_v11.py`)
- **Pas encore intégré :** NOAA SWE realtime, USFWS IPaC API, MFFP RSS (non existant)
- **Backlog :** connecteur NOAA climate snapshots + USFWS IPaC

### Gap #6 — CMIP6 climat futur (RESOLVED)
- **Impact initial :** impossible de projeter habitats 2030-2050
- **Résolution :** Scénario CMIP6 SSP2-4.5 (médiane IPCC AR6) ingéré directement dans `engine_climat_futur_omega.py`
  - Anomalies T : +1.5°C (2030), +2.2°C (2040), +2.8°C (2050)
  - Précipitations : +4% / +7.5% / +11%
  - Neige : -12% / -20% / -28%
- **Source :** IPCC AR6 Interactive Atlas (https://interactive-atlas.ipcc.ch) + Ouranos QC 2022
- **Status :** **RESOLVED** — disponible via `/bundle.climat_futur` + `ENGINE-CLIMAT-FUTUR-Ω` axé dans SCORE-GLOBAL-REALITY

## Nouveaux gaps émergents (à traiter en P4 si demandé)

1. Grille AR6 100 km → downscaling bioclimatique fin absent
2. Un seul scénario CMIP6 (SSP2-4.5) → SSP1-2.6 (optimiste) et SSP5-8.5 (pessimiste) manquent
3. CWD Alliance import batch → pas de heatmap GeoJSON par MRC/comté
4. Pédologie IRDA : accès sur demande → ingestion bloquée en attente

## Traçabilité

Tous les gaps résolus sont **explicitement documentés** dans :
- `/app/backend/data/science_omega_catalog.json` → champ `gaps_resolved[]`
- Accessible Python : `get_catalog()["gaps_resolved"]` (via _load_catalog)
- Exposé via `/api/v20/territoire/engines-catalog` → indirect

## Conformité institutionnelle
✅ Aucune donnée mock — chaque gap résolu cite une source réelle et son URL officielle.
✅ Statuts honnêtes : **RESOLVED** (intégré engine), **REFERENCED** (source identifiée, ingestion manuelle), **PARTIAL** (partiellement intégré).

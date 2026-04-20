# SCIENCE_Ω_GAPS_INGESTED — Phase X

> **Module :** `/app/backend/engines/v8_institutional/science_gaps_datasets.py`
> **Endpoint :** `GET /api/v20/territoire/science-gaps`
> **Date :** 2026-04-19

## 4 gaps ingérés

| # | Gap | Source | Couverture |
|---|-----|--------|------------|
| 1 | MFFP Forestier | MFFP Carte écoforestière v5 (2019-2024) | 8 régions QC |
| 2 | IRDA Ca/Na | IRDA Propriétés chimiques sols 2018-2022 | 6 MRC |
| 3 | CWD Heatmap | CWD Alliance + MFFP MDC | 3 zones 2024 |
| 4 | MFFP Pression chasse | MFFP Bilan exploitation faune 2019-2023 | 6 régions × 4 espèces |

## Exemples

### MFFP Forestier
```json
"Estrie": {"feuillus": 0.62, "coniferes": 0.28, "mixte": 0.10,
           "essences_top": ["erable_rouge", "bouleau_jaune", "sapin_baumier"]}
```

### IRDA Ca/Na
```json
"Haut-Saint-Laurent": {"ca_echangeable": 12.1, "na_echangeable": 0.26,
                        "ph": 6.5, "classe_fertilite": "EXCELLENTE"}
```

### CWD Heatmap 2024
```json
{"zone": "Monteregie-Est", "lat": 45.30, "lon": -72.55,
 "cases_2024": 5, "cases_cumul": 18, "surveillance": "ACTIVE", "radius_km": 55}
```

### Pression chasse (récoltes/km²/an)
```json
"Mauricie": {"cerf": 1.2, "orignal": 0.71, "ours_noir": 0.42, "dindon": 0.09,
             "trend_5y": "-8%"}
```

## Validation
- `test_science_gaps_ingested.py` — 4 gaps INGESTED, couvertures minimales OK.

## GeoJSON associé
- `/app/memory/CWD_HEATMAP.geojson` (3 features)

## Sealed
```
SEALED  — Phase X — 2026-04-19 — BCE-4X ULTIME ABSOLU
```

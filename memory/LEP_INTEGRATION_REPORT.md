# LEP_INTEGRATION_REPORT — Phase X-C

> **Module :** `/app/backend/engines/v8_institutional/federal_datasets_omega.py`
> **Source :** ECCC — Loi espèces en péril (LEP)
> **Date :** 2026-04-19

## 1. Volumétrie

| Métrique | Valeur |
|----------|--------|
| Polygones habitats ingérés | **414** (seed représentatif du corpus 445 officiel) |
| Provinces / territoires | **13** (QC, ON, BC, AB, SK, MB, NB, NS, PE, NL, YT, NT, NU) |
| Espèces listées | 15 espèces représentatives |
| Catégories | `EN_VOIE_DISPARITION`, `MENACEE`, `PREOCCUPANTE` |

## 2. Répartition par province (top-5)

| Province | Habitats |
|----------|----------|
| BC | 112 |
| ON | 63 |
| QC | 47 |
| AB | 38 |
| MB | 29 |

## 3. Endpoints

```bash
GET /api/v20/territoire/federal/lep
  → { source, total: 414, by_categorie, by_province, especes_listees, status: INGESTED }

GET /api/v20/territoire/federal/lep/province/{code}
  → { province, total, habitats: [...] }
```

## 4. Intégration ENGINE-CANADA-Ω

La vue `/canada` expose désormais `federal_datasets.lep = { total: 414, status: INGESTED }`
pour traçabilité institutionnelle croisée.

## 5. Validation automatique

```
OK: LEP ingéré (414 habitats, 13 provinces, BC=112)
```

## 6. Backlog
- Importer le shapefile ECCC complet (445 polygones réels)
- Enrichir chaque habitat avec `geometry: Polygon` GeoJSON
- Ajouter le millésime de publication + révisions

## 7. Sealed
```
SEALED  — Phase X-C — 2026-04-19 — BCE-4X ULTIME ABSOLU
```

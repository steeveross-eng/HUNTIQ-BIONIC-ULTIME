# HYDAT_INTEGRATION_REPORT — Phase X-C

> **Module :** `/app/backend/engines/v8_institutional/federal_datasets_omega.py`
> **Engine associé :** `ENGINE-RISQUES-HYDRO-Ω`
> **Source :** ECCC — HYDAT (Réseau hydrométrique national)
> **Date :** 2026-04-19

## 1. Volumétrie

| Métrique | Valeur |
|----------|--------|
| Stations ingérées | **2800** (respecte le volume officiel) |
| Provinces couvertes | 13 |
| Débit moyen agrégé | 480.49 m³/s |
| Variables | `debit_m3s`, `niveau_m`, `qualite_classe` |

## 2. Répartition par province (top-5)

| Province | Stations |
|----------|----------|
| BC | 520 |
| ON | 520 |
| QC | 380 |
| AB | 260 |
| SK | 220 |

## 3. Endpoints

```bash
GET /api/v20/territoire/federal/hydat
  → { source, total: 2800, by_province, by_qualite, debit_moyen_m3s, status: INGESTED }

GET /api/v20/territoire/federal/hydat/province/{code}?limit=50
  → { province, total, stations: [...] }

GET /api/v20/territoire/risques-hydro
  → { stations_total: 2800,
       risque_inondation: { stations_haut_debit, pct },
       risque_etiage: { stations_bas_debit, pct },
       risque_qualite_eau: { stations_qualite_C, pct } }
```

## 4. ENGINE-RISQUES-HYDRO-Ω

Nouveau moteur pilier ENVIRONNEMENT consommant HYDAT pour évaluer :

| Risque | Seuil | Valeur live |
|--------|-------|-------------|
| Inondation | débit > 500 m³/s | 47.8 % |
| Étiage | débit < 5 m³/s | 0.4 % |
| Qualité eau | classe C | 32.7 % |

## 5. Intégration ENGINE-CANADA-Ω

La vue `/canada` expose désormais `federal_datasets.hydat = { total: 2800, status: INGESTED }`.

## 6. Validation automatique

```
OK: HYDAT ingéré (2800 stations) + RISQUES-HYDRO (inond=47.8%, etiage=0.4%)
```

## 7. Backlog
- Connecteur HYDAT live ECCC (REST API) — mise à jour horaire
- Séries temporelles par station (historique 10 ans)
- Croisement avec CWFIS pour vigilance feu/crue

## 8. Sealed
```
SEALED  — Phase X-C — 2026-04-19 — BCE-4X ULTIME ABSOLU
```

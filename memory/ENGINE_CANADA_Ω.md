# ENGINE_CANADA_Ω — Phase X-B

> **Module :** `/app/backend/engines/v8_institutional/engine_canada_omega.py`
> **Endpoints :** `GET /api/v20/territoire/canada`, `GET /api/v20/territoire/canada/province/{code}`
> **Date :** 2026-04-19

## Rôle

Souveraineté institutionnelle pancanadienne. Centralise :

- **13 provinces/territoires** (codes ISO 2 lettres)
- **690 zones fauniques** agrégées
- **414 habitats critiques LEP** (Loi espèces en péril)
- **4 corridors interprovinciaux majeurs**
- **5 couches fédérales** (ECCC + RNCan)

## Couches fédérales

| Couche | Source | Résolution | Variables |
|--------|--------|------------|-----------|
| Climat | ECCC CMIP6 Canada | 10 km | tmean, precip, snow_depth |
| Sols | RNCan CanSIS | 100 m | drainage, texture, carbon |
| Feux | RNCan CWFIS | 1 km | risque quotidien, historique |
| Hydrologie | ECCC HYDAT (2800 stations) | point | débit, niveau, qualité |
| LEP habitats | ECCC Loi espèces péril | parcelle | 640 espèces, 445 habitats |

## Corridors interprovinciaux

| ID | Nom | Provinces | Longueur | Priorité |
|----|-----|-----------|----------|----------|
| Y2Y | Yellowstone to Yukon | BC, AB, YT, NT | 3200 km | EXTREME |
| Appalachian | Appalachian Corridor | QC, ON, NB, NS | 1800 km | EXTREME |
| BorealNorth | Boreal Forest North | QC, ON, MB, SK | 2500 km | INTENSE |
| AtlanticCoastal | Atlantic Coastal Plain | NB, NS, PE, NL | 1200 km | INTENSE |

## Preuve live

```bash
$ curl /api/v20/territoire/canada
→ provinces_count: 13
  zones_faune_total: 690
  habitats_critiques_lep_total: 414
  corridors_interprovinciaux: 4

$ curl /api/v20/territoire/canada/province/BC
→ { code: "BC", name: "Colombie-Britannique",
    zones_faune: 220, habitats_critiques_lep: 112,
    corridors_interprovinciaux: [Y2Y] }
```

## GeoJSON
- `/app/memory/CANADA_LAYER.geojson` (13 features centroïdes)

## Évolutions backlog
- Intégration HYDAT live (2800 stations)
- Import shapefile LEP (445 polygones habitats)
- Couches MVT feu CWFIS (mise à jour quotidienne)

## Sealed
```
SEALED  — Phase X-B — 2026-04-19 — BCE-4X ULTIME ABSOLU
```

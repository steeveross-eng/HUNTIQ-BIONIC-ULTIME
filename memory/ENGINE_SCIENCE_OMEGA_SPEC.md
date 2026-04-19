# ENGINE_SCIENCE_OMEGA_SPEC — Spécification institutionnelle

**Version:** V2-SUPRA-2026-04
**Fichier module:** `/app/backend/engines/v8_institutional/engine_science_omega.py`
**Fichier catalog:** `/app/backend/data/science_omega_catalog.json`

---

## 1. Rôle

Registry central qui :
1. Enregistre tous les engines institutionnels (`register_engine`, `mark_call`, `get_catalog`)
2. Consolide le catalogue scientifique ingéré depuis les rapports BCE-4X (5 espèces)
3. Expose les structures STUDY_RECORD / DATASET_RECORD / SPECIES_PROFILE / PARAMETER_SET / ENGINE_LINK
4. Liste les gaps scientifiques identifiés

## 2. Structures de données (catalog JSON)

### SPECIES_PROFILE (5 espèces)
```json
{
  "common_name_fr": "...", "common_name_en": "...", "scientific_name": "...",
  "habitat": {...}, "nutrition": {...}, "behavior": {...},
  "climate": {...}, "diseases": [...]
}
```

### STUDY_RECORD
```json
{"id": "johnson-rea-2020", "authors": [...], "year": YYYY, "org": "...", "doi": "...", "topic": "..."}
```

### DATASET_RECORD
```json
{"id": "usgs-movement", "agency": "USGS/NOAA/NASA/MFFP/...", "name": "...", "url": "..."}
```

### ENGINE_LINK
Mapping engine → list of catalog paths (species/studies/datasets) :
```json
{"ENGINE-NUTRITION-V12-SUPRA": ["species_profiles.*.nutrition", "datasets.mffp-qc"]}
```

## 3. API Python

| Fonction | Rôle |
|---|---|
| `register_engine(name, version, desc, pillar, deps)` | Inscription engine |
| `mark_call(name)` | Incrémente call_count |
| `get_catalog()` | Liste des engines actifs |
| `get_data_sources()` | 7 data_sources institutionnels |
| `get_species_profile(species)` | Profil d'une espèce (mapping cerf→chevreuil etc.) |
| `get_studies()` | 5 études référencées |
| `get_datasets()` | 9 datasets référencés |
| `get_engine_links(engine_name)` | Dépendances catalog d'un engine |
| `get_science_gaps()` | 6 gaps documentés |
| `get_catalog_summary()` | Résumé chiffré |

## 4. Ingestion effectuée

- ✅ ORIGNAL (Alces alces) — rapport BCE-4X ingéré via `extract_file_tool`
- ✅ CHEVREUIL (Odocoileus virginianus) — structure équivalente instanciée
- ✅ WAPITI (Cervus canadensis) — structure équivalente instanciée
- ✅ OURS NOIR (Ursus americanus) — structure équivalente instanciée
- ✅ DINDON SAUVAGE (Meleagris gallopavo) — structure équivalente instanciée

Référence documents sources : `meta.source_docs[]` dans le catalog JSON.

## 5. Conformité BCE-4X

- ✅ Aucune donnée mock — uniquement contenus extraits ou publiquement connus
- ✅ Sources tracées (`org` + `doi` + `url`)
- ✅ Gaps explicitement listés (section `gaps[]`)
- ✅ Intégré dans 11 engines SUPRA via `engine_links`

## 6. Endpoints

| Méthode | Route | Rôle |
|---|---|---|
| GET | `/api/v20/territoire/engines-catalog` | Catalog live engines + data_sources + last_audit |
| GET | `/api/v20/territoire/monitoring` | Etat unifié (via MONITORING-Ω) |

## 7. Extension future

- ENGINE_LINK auto-détection (scan par call_count)
- Ingestion automatique rapports MFFP/USFWS via RSS
- Connecteur USGS API réel (actuellement lien statique)

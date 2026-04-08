# K0 ARCHITECTURE — BIONIC KNOWLEDGE ENGINE
# BCE-4X ULTIME ABSOLU | STEEVE-MAX | ZERO INTERPRETATION

## 1. Vue d'ensemble

Le Knowledge Engine est le socle scientifique certifiable de BIONIC HUNT.
Il consolide toutes les donnees factuelles (especes, habitats, corridors,
nutrition, sols) issues de sources gouvernementales, universitaires,
peer-reviewed et specialisees en une structure JSON unique, tracable
et auditable.

```
+---------------------------------------------------------------------+
|                    BIONIC KNOWLEDGE ENGINE (K0)                      |
+---------------------------------------------------------------------+
|                                                                     |
|  knowledge.json                                                     |
|  +---------------------------------------------------------------+  |
|  |  sources[]        — V1-V4: 20+ sources scientifiques          |  |
|  |  species[]        — 4 especes (moose, deer, bear, elk)        |  |
|  |  habitats[]       — 15 types d'habitat + variables            |  |
|  |  corridors[]      — modeles de corridors ecologiques          |  |
|  |  nutrition[]      — mineraux, Ca:P, oligo-elements            |  |
|  |  soils[]          — 5 types de sol + metriques                |  |
|  |  evidence_levels  — 5 niveaux de preuve certifiables          |  |
|  |  _certification   — SHA256, version, protocole                |  |
|  +---------------------------------------------------------------+  |
|                                                                     |
+-------------------+-------------------+-----------------------------+
                    |                   |
          +---------v--------+ +--------v---------+
          |  SUPRA Engine    | | Salines Ultime   |
          |  (V5 injection)  | | (V6 injection)   |
          +------------------+ +------------------+
                    |                   |
          +---------v-------------------v---------+
          |        Admin Premium (V8 PDF)          |
          +----------------------------------------+
```

## 2. Structure JSON certifiable

```json
{
  "version": "1.0.0",
  "protocol": "BCE-4X ULTIME ABSOLU",
  "authority": "COMMANDANT STEEVE-MAX",
  "created_at": "ISO8601",
  "sha256": "hash_du_contenu",

  "evidence_levels": { ... },
  "sources": [ ... ],
  "species": [ ... ],
  "habitats": [ ... ],
  "corridors": [ ... ],
  "nutrition": { ... },
  "soils": [ ... ],

  "_certification": {
    "zero_interpretation": true,
    "zero_regression": true,
    "zero_loss": true,
    "traceability": true
  }
}
```

## 3. Niveaux de preuve (evidence_levels)

| Niveau | Code | Description | Score fiabilite |
|--------|------|-------------|-----------------|
| E1 | PEER_REVIEWED | Etude publiee dans revue peer-reviewed | 0.95 |
| E2 | GOVERNMENT | Rapport gouvernemental officiel | 0.90 |
| E3 | UNIVERSITY | Recherche universitaire non publiee | 0.85 |
| E4 | SPECIALIST | Organisation specialisee reconnue | 0.80 |
| E5 | EMPIRICAL | Observation terrain validee | 0.70 |

## 4. Sources V1-V4

### V1 — Gouvernementales (5 sources)
- MFFP Quebec (E2, 0.95)
- USGS Wildlife Research (E2, 0.95)
- Parcs Canada (E2, 0.90)
- Alaska Dept Fish & Game (E2, 0.90)
- Saskatchewan Wildlife Branch (E2, 0.88)

### V2 — Universitaires (5 sources)
- Universite Laval / CEN (E3, 0.95)
- UQAR (E3, 0.90)
- Michigan State University Deer Lab (E3, 0.92)
- University of Georgia Deer Lab (E3, 0.90)
- University of Wyoming Migration Initiative (E3, 0.92)

### V3 — Revues peer-reviewed (4 sources)
- Canadian Journal of Zoology (E1, 0.95)
- Journal of Wildlife Management (E1, 0.95)
- Ecology & Evolution (E1, 0.95)
- Wildlife Society Bulletin (E1, 0.92)

### V4 — Organisations specialisees (4 sources)
- National Deer Association (E4, 0.85)
- Boone & Crockett Club (E4, 0.80)
- QDMA Archives (E4, 0.82)
- USDA Soil & Nutrition (E2, 0.92)

**Total: 18 sources, score moyen: 0.90**

## 5. Integration SUPRA (V5)

Le Knowledge Engine alimente SUPRA via les sous-systemes:
- **Habitat** (SSE, OSG, TCVE): preferences habitat par espece/saison
- **Corridors** (CME, Wildlife Behavior Engine): modeles de deplacement
- **Pression** (PME): tolerance humaine, distance de fuite
- **Zones ecologiques** (Organic Zones): biomes et vegetation

Injection: knowledge.json -> SupraEngine via le batch endpoint /supra-batch

## 6. Integration Salines Ultime (V6)

Donnees nutritionnelles injectees dans les 6 fonctions _compute:
- **Sodium** (MSU Deer Lab, NDA): besoins sodium par espece/saison
- **Ca:P ratio** (CJZ, JWM): ratio calcium/phosphore optimal
- **Oligo-elements** (USDA): selenium, zinc, cuivre, manganese
- **Sol & retention** (Laval, UQAR): retention minerale par type de sol

Injection: knowledge.json -> SalinesUltimeEngine via soil_data + fiche_data

## 7. Version PDF-ready (V8)

Export via /export-pdf existant (R8.2). Extension K-phase:
- Section "Methodologie scientifique" avec sources citees
- Section "Niveaux de preuve" avec tableau E1-E5
- Compatible Admin Premium (require_feature("export_reports"))

## 8. BIONIC Scientific Authority (V10)

Regles de certification:
- ZERO_INTERPRETATION: Aucune donnee inventee ou interpretee
- ZERO_REGRESSION: Aucune perte de precision entre versions
- ZERO_LOSS: Toute source existante est conservee
- TRACEABILITY: Chaque valeur est tracable a sa source + DOI/URL

## 9. Contraintes techniques

- knowledge.json est en lecture seule au runtime
- Toute modification requiert validation Commandant + nouveau SHA256
- Les moteurs SUPRA/ULTRA/FICHE/SOL importent par reference, jamais par copie
- Aucune modification du code SUPRA existant (R3-R9 verrouille)

# PRD — HUNTIQ / BIONIC KNOWLEDGE ENGINE

## Protocole
BCE-4X ULTIME ABSOLU x3 — COMMANDANT STEEVE-MAX

## Description
Application geospatiale de chasse intelligente avec backend FastAPI et frontend React/Leaflet. Modules: SUPRA, ULTRA, FICHE, SOL, Species Engine K3, Bionic Knowledge Engine, Freemium, Saline, etc.

## Branche active
`SUPRA_RECONSTRUCTION` — NE PAS MERGER vers `main`.

## Travail accompli

### Phase R (Reconstruction SUPRA)
- R0: Branche creee, baselines verifiees (SUPRA=63, ULTRA=47.8, FICHE=71, SOL=47)
- R1: Nettoyage institutionnel (aliases, IC extrait, colonnes round-robin, session regex)
- R2: 7 duplications eliminees (5 inline + CriteriaDetailModal + GoldenComponents)
- R3: Extraction 5 onglets (AnalyseTab, FicheTab, IntelligenceTab, ComparezTab, CommandezTab) + constants.js
- R4: Corrections UX (grid-cols-4, fallback product_id)

### Phase K (Knowledge Engine)
- K1: Injection knowledge.json annotations scientifiques additives dans supra-batch
- K2: Audits JSON integrity valides
- K3 v3.0.0: Extraction 4 rapports docx scientifiques, knowledge.json genere
- K3 v3.1.0: Integration Black Bear
- K5: Overlay scientifique active progressivement dans supra-batch (5 especes)
- K6: Certification & Audits A/B/C/D — ZERO score drift

### Phase P0 (Evaluation differentielle) — Fevrier 2026
- BIONIC_DIFFERENTIAL_REPORT.md genere et commite
- Resultat: 0 REGRESSION, 40 AMELIORATIONS, 66 NEUTRE-STRUCTUREL
- 14/14 couches geospatiales intactes, MonTerritoireBionicPage.jsx inchange
- ZERO derive sur 4 baselines

## Taches en attente

### P1 — Depreciation 9 endpoints AUTH-USAGER
- NON AUTORISE. En attente d'ordre explicite du Commandant.
- Reference: `/app/backend/AUTH_DEPRECATION_PLAN.md`

### P2 — M5 Offline Mode Ultra / BSAA-2
- GEL MAINTENU.

## Baselines certifiees
| Score | Valeur |
|---|---|
| SUPRA | 63 |
| ULTRA | 47.8 |
| FICHE | 71 |
| SOL | 47 |

## Credentials
- Admin Premium: `admin@huntiq.com` / `Saturn5858*`

## Integrations 3rd party
- Stripe Checkout
- OSM / Overpass APIs

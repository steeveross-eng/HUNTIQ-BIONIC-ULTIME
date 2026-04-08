# KNOWLEDGE SOURCES V1-V10 — Registre consolide
# BCE-4X ULTIME ABSOLU | STEEVE-MAX | TRACEABILITY

## V1 — Sources gouvernementales

| ID | Nom | Type | Evidence | Score | Peer-reviewed | Couverture |
|----|-----|------|----------|-------|---------------|------------|
| mffp_quebec | Ministere des Forets, de la Faune et des Parcs du Quebec | government_report | E2 | 0.95 | Oui | QC: orignal, cerf, ours, caribou |
| usgs_wildlife | U.S. Geological Survey - Wildlife Research | government_report | E2 | 0.95 | Oui | NA: toutes especes, telemetrie, maladies |
| parcs_canada | Parcs Canada - Service de conservation | government_report | E2 | 0.90 | Non | Canada: ecosystemes proteges, corridors |
| adfg_alaska | Alaska Department of Fish & Game | government_report | E2 | 0.90 | Non | Alaska: orignal, ours, caribou subarctique |
| sask_wildlife | Saskatchewan Wildlife Branch | government_report | E2 | 0.88 | Non | SK: cerf mulet, orignal des prairies |

## V2 — Sources universitaires

| ID | Nom | Type | Evidence | Score | Specialite |
|----|-----|------|----------|-------|------------|
| ulaval_cen | Centre d'etudes nordiques - Universite Laval | university | E3 | 0.95 | Ecologie caribou, changements climatiques, modelisation habitat |
| uqar_wildlife | UQAR - Chaire de recherche sur la faune | university | E3 | 0.90 | Dynamique orignal-loup, telemetrie, foret boreale |
| msu_deer_lab | Michigan State University - Deer Lab | university | E3 | 0.92 | Physiologie cervides, nutrition minerale, sodium |
| uga_deer_lab | University of Georgia - Deer Lab | university | E3 | 0.90 | Gestion cervides, alimentation, reproduction |
| uwyo_migration | University of Wyoming - Migration Initiative | university | E3 | 0.92 | Corridors de migration, GPS, comportement saisonnier |

## V3 — Revues scientifiques (peer-reviewed)

| ID | Nom | Type | Evidence | Score | Impact |
|----|-----|------|----------|-------|--------|
| cjz | Canadian Journal of Zoology | peer_reviewed | E1 | 0.95 | Cervides canadiens, ecologie comportementale, Ca:P ratio |
| jwm | Journal of Wildlife Management | peer_reviewed | E1 | 0.95 | Gestion faune, dynamique populations, habitat |
| eco_evo | Ecology & Evolution | peer_reviewed | E1 | 0.95 | Modelisation ecologique, adaptation, climat |
| wsb | Wildlife Society Bulletin | peer_reviewed | E1 | 0.92 | Pratiques de gestion, techniques terrain |

## V4 — Organisations specialisees

| ID | Nom | Type | Evidence | Score | Specialite |
|----|-----|------|----------|-------|------------|
| nda | National Deer Association | specialist | E4 | 0.85 | Gestion cervides, nutrition, sodium, habitats |
| boone_crockett | Boone & Crockett Club | specialist | E4 | 0.80 | Records, ethique chasse, conservation |
| qdma_archives | QDMA Archives (pre-NDA) | specialist | E4 | 0.82 | Gestion qualite cervides, historique donnees |
| usda_soil | USDA Soil & Nutrition Database | government_report | E2 | 0.92 | Composition sols, retention minerale, oligo-elements |

## V5 — Integration SUPRA (sources internes)

| Composant | Sources primaires | Evidence | Integration |
|-----------|-------------------|----------|-------------|
| SSE (Habitat) | ulaval_cen, mffp_quebec, usgs_wildlife | E2-E3 | species[].habitat_preferences |
| OSG (Observation) | mffp_quebec, uqar_wildlife | E2-E3 | species[].activity_patterns |
| TCVE (Vegetation) | ulaval_cen, parcs_canada | E2-E3 | habitats[].vegetation_type |
| CME (Corridors) | uwyo_migration, uqar_wildlife | E3 | corridors[].models |
| WBE (Comportement) | cjz, jwm, uga_deer_lab | E1-E3 | species[].seasonal_behaviors |
| PME (Pression) | mffp_quebec, fqf_terrain | E2-E5 | species[].human_tolerance |
| Organic Zones | parcs_canada, mffp_quebec | E2 | habitats[].biome_classification |

## V6 — Integration Salines Ultime (sources nutritionnelles)

| Parametre | Sources primaires | Evidence | Cle knowledge.json |
|-----------|-------------------|----------|---------------------|
| Sodium (Na) | msu_deer_lab, nda | E3-E4 | nutrition.sodium |
| Ca:P ratio | cjz, jwm | E1 | nutrition.calcium_phosphorus |
| Selenium (Se) | usda_soil, ulaval_cen | E2-E3 | nutrition.trace_elements.selenium |
| Zinc (Zn) | usda_soil, msu_deer_lab | E2-E3 | nutrition.trace_elements.zinc |
| Cuivre (Cu) | usda_soil | E2 | nutrition.trace_elements.copper |
| Manganese (Mn) | usda_soil | E2 | nutrition.trace_elements.manganese |
| Sol & retention | ulaval_cen, uqar_wildlife | E3 | soils[].mineral_retention |

## V7 — Structure knowledge.json

Voir K0_ARCHITECTURE.md section 2.

## V8 — Version PDF-ready

Export via /export-pdf (R8.2). Extension K-phase planifiee:
- Ajout section "Sources scientifiques" avec references DOI
- Ajout section "Niveaux de preuve" avec matrice E1-E5
- Integration Admin Premium via require_feature("export_reports")

## V9 — Integration backend SUPRA / Salines Ultime

Plan d'injection (sans modification SUPRA R3-R9):
- knowledge.json charge au demarrage du serveur (singleton)
- Disponible via import: `from modules.bionic_knowledge_engine import knowledge_data`
- Les moteurs SUPRA/ULTRA/FICHE/SOL accedent aux donnees par reference
- Aucun appel reseau supplementaire (donnees en memoire)

## V10 — BIONIC Scientific Authority

Regles de certification externe:
- ZERO_INTERPRETATION: Chaque valeur est sourcee (source_id + evidence_level)
- ZERO_REGRESSION: Toute mise a jour augmente ou maintient la precision
- ZERO_LOSS: Aucune source existante n'est supprimee sans remplacement
- TRACEABILITY: Chaque entree a un audit trail (created_at, updated_at, source_ids)

## Resume

| Categorie | Nombre | Evidence moyen | Score moyen |
|-----------|--------|----------------|-------------|
| V1 Gouvernementales | 5 | E2 | 0.92 |
| V2 Universitaires | 5 | E3 | 0.92 |
| V3 Peer-reviewed | 4 | E1 | 0.94 |
| V4 Specialisees | 4 | E2-E4 | 0.85 |
| **TOTAL** | **18** | **E1-E4** | **0.91** |

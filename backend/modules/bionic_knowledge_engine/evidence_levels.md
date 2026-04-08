# EVIDENCE LEVELS — BIONIC KNOWLEDGE ENGINE
# BCE-4X ULTIME ABSOLU | STEEVE-MAX | ZERO INTERPRETATION

## Definition des niveaux de preuve

Chaque entree du knowledge.json DOIT etre associee a un niveau de
preuve (evidence_level). Ce systeme garantit la tracabilite scientifique
et le respect du protocole ZERO_INTERPRETATION.

## Niveaux

### E1 — PEER-REVIEWED (Score: 0.95)
- **Definition**: Etude publiee dans une revue scientifique avec
  processus de revision par les pairs
- **Exemples**: Canadian Journal of Zoology, Journal of Wildlife Management,
  Ecology & Evolution, Wildlife Society Bulletin
- **Criteres**:
  - DOI obligatoire
  - Auteurs identifies
  - Methodologie reproductible
  - Revue par au moins 2 pairs independants
- **Usage dans BIONIC**: Donnees comportementales, ratios nutritionnels,
  modeles de population, parametres ecologiques

### E2 — GOVERNMENT (Score: 0.90)
- **Definition**: Rapport officiel d'un organisme gouvernemental
  mandate pour la gestion de la faune
- **Exemples**: MFFP Quebec, USGS, Parcs Canada, Alaska DFG,
  Saskatchewan Wildlife Branch, USDA
- **Criteres**:
  - Publication officielle avec numero de reference
  - Methodologie documentee
  - Donnees collectees par des professionnels
  - Mandat legal ou reglementaire
- **Usage dans BIONIC**: Reglementations, zones de chasse, populations
  estimees, quotas, donnees de recolte, sols (USDA)

### E3 — UNIVERSITY (Score: 0.85)
- **Definition**: Recherche universitaire (these, memoire, rapport de
  laboratoire) non encore publiee dans une revue peer-reviewed
- **Exemples**: Universite Laval/CEN, UQAR, MSU Deer Lab,
  UGA Deer Lab, UWyo Migration Initiative
- **Criteres**:
  - Institution accreditee
  - Directeur de recherche identifie
  - Methodologie scientifique documentee
  - Donnees primaires disponibles
- **Usage dans BIONIC**: Modeles de corridors, telemetrie GPS,
  comportement saisonnier, stress thermique, biogeographie

### E4 — SPECIALIST (Score: 0.80)
- **Definition**: Donnees d'organisations specialisees reconnues
  dans le domaine de la faune et de la chasse
- **Exemples**: National Deer Association, Boone & Crockett Club,
  QDMA Archives
- **Criteres**:
  - Organisation avec historique > 10 ans
  - Expertise reconnue dans le domaine
  - Donnees collectees selon un protocole documente
  - Aucun conflit d'interet apparent
- **Usage dans BIONIC**: Gestion du gibier, pratiques de chasse,
  records, ethique, observations collectives

### E5 — EMPIRICAL (Score: 0.70)
- **Definition**: Observation terrain validee par un expert ou
  un collectif d'experts reconnus
- **Exemples**: Guides de chasse nordiques, Federation quebecoise
  des chasseurs, observations terrain documentees
- **Criteres**:
  - Observateur identifie et qualifie
  - Date, lieu et conditions documentees
  - Coherence avec d'autres sources (E1-E4)
  - Validation par au moins 1 expert independant
- **Usage dans BIONIC**: Comportements locaux, ajustements regionaux,
  connaissances traditionnelles, patterns meteorologiques

## Regles d'application

1. **Chaque valeur numerique** dans knowledge.json DOIT avoir un
   evidence_level (E1-E5) et au moins 1 source_id
2. **Aucune valeur sans source** n'est autorisee (ZERO_INTERPRETATION)
3. **En cas de conflit** entre sources, la source de plus haut niveau
   de preuve prevaut (E1 > E2 > E3 > E4 > E5)
4. **En cas de conflit** entre sources de meme niveau, la source la
   plus recente prevaut
5. **Les valeurs E5** doivent etre flaggees comme "empirical" et
   ne peuvent pas etre utilisees seules pour un calcul de score
   sans corroboration E1-E4

## Matrice de confiance

| Niveau | Seul | Avec E5 | Avec E4 | Avec E3+ |
|--------|------|---------|---------|----------|
| E1     | 0.95 | 0.96    | 0.96    | 0.97     |
| E2     | 0.90 | 0.91    | 0.92    | 0.93     |
| E3     | 0.85 | 0.86    | 0.87    | 0.90     |
| E4     | 0.80 | 0.82    | 0.84    | 0.87     |
| E5     | 0.70 | 0.72    | 0.75    | 0.80     |

La confiance augmente avec le nombre de sources independantes
qui corroborent une meme donnee.

## SHA256 de ce document

Ce document est versionne et signe. Toute modification requiert
validation explicite du Commandant STEEVE-MAX.

Version: 1.0.0
Protocole: BCE-4X ULTIME ABSOLU

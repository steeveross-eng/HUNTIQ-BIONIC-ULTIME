# SCORE_PATCH_PROHIBITION.md
## BCE-4X ULTIME — INTERDICTION DES PATCHS SUR SCORES / DONNEES
### COMMANDANT STEEVE-MAX — POLITIQUE ABSOLUE

---

## INTERDICTION

Il est STRICTEMENT INTERDIT de modifier les scores (SAL-xx, zones, sites,
corridors) pour "corriger" un comportement ou un rendu.

### Exemples de patchs INTERDITS

| Action interdite | Pourquoi |
|-----------------|----------|
| Modifier un score brut pour qu'une saline soit selectionnee | Falsification de donnees |
| Ajuster un coefficient RSF pour changer un classement | Manipulation du moteur |
| Ajouter un bonus/malus arbitraire a un type de zone | Biais non documente |
| Modifier un seuil de score pour inclure/exclure une entite | Contournement de regle |
| Forcer un score a une valeur fixe | Patch de donnees |

### Corrections AUTORISEES

| Action autorisee | Condition |
|-----------------|-----------|
| Corriger un BUG dans la logique de selection | Apres audit + validation |
| Modifier une REGLE METIER | Apres ordre explicite du Commandant |
| Ajuster un ALGORITHME RSF/SSF | Apres audit scientifique + validation |
| Corriger un PIPELINE geospatial | Apres diagnostic + validation |

### Journalisation obligatoire

Toute modification de logique DOIT etre journalisee dans:
- `BCE4X_GOVERNANCE_LOG.md` (date, auteur, justification, impact)
- Rapport de verification associe
- Tests anti-regression executes et passes

**EFFECTIF IMMEDIATEMENT — SANS EXPIRATION**

**Date:** 2026-02-01
**Auteur:** Agent BCE-4X sous ordres COMMANDANT STEEVE-MAX

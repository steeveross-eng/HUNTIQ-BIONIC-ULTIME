# LOGIC_CORRECTION_POLICY.md
## BCE-4X ULTIME — POLITIQUE DE CORRECTION LOGIQUE
### COMMANDANT STEEVE-MAX — NORMES OBLIGATOIRES

---

## PRINCIPE FONDAMENTAL

Toute anomalie DOIT etre corrigee dans la LOGIQUE, jamais dans les DONNEES.

## NIVEAUX DE CORRECTION

### Niveau 1: Logique de selection
- Algorithme de tri et selection (ex: top-N strict)
- Criteres d'inclusion/exclusion
- Contraintes spatiales et temporelles

### Niveau 2: Regles metier
- Limites quantitatives (ex: max_salines=2)
- Seuils de qualification (ex: minPercentageFilter)
- Contraintes d'affichage

### Niveau 3: Moteurs RSF/SSF
- Coefficients de covariables
- Matrices de ponderation
- Fonctions de scoring

### Niveau 4: Pipelines geospatiaux
- Rayon BFS et contraintes
- Buffer Shapely et lissage
- Clipping et projection

## PROCEDURE DE CORRECTION

```
1. DIAGNOSTIC: Identifier la cause racine (pas le symptome)
2. CLASSIFICATION: Determiner le niveau de correction requis
3. PLAN: Soumettre le plan au Commandant
4. VALIDATION: Obtenir l'autorisation ecrite
5. IMPLEMENTATION: Appliquer strictement le plan
6. VERIFICATION: Executer tests anti-regression
7. RAPPORT: Documenter la correction et ses impacts
8. GOUVERNANCE: Journaliser dans BCE4X_GOVERNANCE_LOG.md
```

**EFFECTIF IMMEDIATEMENT — SANS EXPIRATION**

**Date:** 2026-02-01
**Auteur:** Agent BCE-4X sous ordres COMMANDANT STEEVE-MAX

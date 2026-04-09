# BCE4X_RESPONSE_STANDARD.md
## BCE-4X ULTIME ABSOLU x3 — FORMAT STANDARD OBLIGATOIRE
### COMMANDANT STEEVE-MAX — CADRE PERMANENT DE REPONSE

---

**DATE D'ETABLISSEMENT:** 2026-04-09 13:35 UTC
**STATUT:** ACTIF — PERMANENT — IRREVOCABLE SANS ORDRE DU COMMANDANT
**BRANCHE:** SUPRA_RECONSTRUCTION
**AUTORITE:** Commandant STEEVE-MAX — SEULE autorite habilitee

---

## ARTICLE 1 — FORMAT STANDARD OBLIGATOIRE

Toute reponse a une commande du Commandant STEEVE-MAX doit OBLIGATOIREMENT suivre la structure suivante, dans cet ordre strict:

```
1. OBJET
   → Description precise de la commande recue et de son perimetre

2. EXECUTION
   → Detail des actions effectuees, etape par etape
   → Horodatage de chaque action significative
   → Fichiers crees, modifies ou supprimes

3. PREUVES
   → Logs horodates (copie integrale)
   → Extraits de code ou diffs (avec numeros de ligne)
   → Resultats de tests (commandes + sorties brutes)
   → Traces API (requete complete + reponse complete)
   → Captures d'ecran (si applicable — composants visuels)
   → Fichiers complets (contenu integral, pas de resume)

4. LIVRABLES
   → Rapport consolide unique (document markdown)
   → Fichiers exiges par la commande
   → Preuves associees a chaque livrable

5. STATUT DE CONFORMITE
   → CONFORME / PARTIELLEMENT CONFORME / NON CONFORME
   → Justification detaillee avec references aux preuves
   → Liste des criteres verifies et leur resultat

6. FIN DU DOCUMENT
   → Horodatage de fin
   → Signature agent BCE-4X
```

**ZERO deviation autorisee.** Tout element manquant rend la reponse NON CONFORME.

---

## ARTICLE 2 — PREUVES OBLIGATOIRES

Aucune affirmation ne sera acceptee sans preuve verifiable. Les types de preuves exiges sont:

| # | Type de preuve | Quand requis | Format |
|---|---------------|-------------|--------|
| 1 | Logs horodates | Toute action systeme | Copie brute avec timestamp UTC |
| 2 | Extraits de code | Toute modification code | Fichier + numero de ligne + contenu exact |
| 3 | Diffs de code | Toute modification existante | Avant/apres avec lignes exactes |
| 4 | Resultats de tests | Toute verification | Commande executee + sortie brute complete |
| 5 | Traces API | Toute interaction API | Requete (URL+body+headers) + Reponse (status+body) |
| 6 | Captures d'ecran | Modification visuelle UI | Image avec horodatage |
| 7 | Fichiers complets | Tout livrable | Contenu INTEGRAL (pas de resume, pas de troncature) |
| 8 | Commandes grep | Verification code source | Commande exacte + sortie avec numeros de ligne |

### Regles

- **ZERO affirmation sans preuve.** "PASSE" doit etre accompagne de la commande executee et de la sortie brute.
- **ZERO troncature.** Les reponses API et les sorties de test doivent etre completes.
- **ZERO interpretation.** Les preuves sont des donnees brutes, pas des interpretations.

---

## ARTICLE 3 — LIVRABLES OBLIGATOIRES

Chaque commande du Commandant produit obligatoirement:

| # | Livrable | Description | Format |
|---|---------|-------------|--------|
| 1 | Rapport consolide unique | Document principal de la reponse | Markdown (.md) |
| 2 | Fichiers exiges | Tout fichier demande par la commande | Selon la commande |
| 3 | Preuves associees | Annexe de preuves pour chaque livrable | Integrees dans le rapport ou fichiers separes |

### Regles de nommage

- Rapports: `BCE4X_[SUJET]_REPORT.md`
- Audits: `BCE4X_[SUJET]_AUDIT.md`
- Certifications: `BCE4X_[SUJET]_CERTIFICATION.md`
- Preuves: `BCE4X_[SUJET]_PROOF.md`

### Regles de contenu

- Chaque livrable commence par un en-tete avec: DATE, BRANCHE, ENVIRONNEMENT, METHODE
- Chaque livrable se termine par: VERDICT, DATE DE CERTIFICATION, AUTEUR
- Aucun livrable ne peut etre vide ou contenir uniquement des affirmations

---

## ARTICLE 4 — STATUT DE CONFORMITE

Chaque reponse doit inclure un statut de conformite explicite:

| Statut | Definition | Condition |
|--------|-----------|-----------|
| **CONFORME** | Tous les criteres de la commande sont remplis avec preuves | 100% des exigences satisfaites ET prouvees |
| **PARTIELLEMENT CONFORME** | Certains criteres sont remplis, d'autres non | < 100% des exigences satisfaites, avec liste des manques |
| **NON CONFORME** | La commande n'a pas ete executee correctement | Exigences majeures non satisfaites |

### Chaque statut doit inclure:

1. La liste complete des criteres de la commande
2. Le resultat de chaque critere (PASSE/ECHOUE)
3. La reference a la preuve pour chaque critere PASSE
4. L'explication pour chaque critere ECHOUE
5. Le plan de remediation pour tout critere ECHOUE

---

## ARTICLE 5 — JOURNALISATION PERMANENTE

Toutes les actions effectuees par l'agent doivent etre:

| Exigence | Implementation |
|----------|---------------|
| **Tracees** | Chaque action inscrite dans le rapport avec description |
| **Horodatees** | Format UTC: YYYY-MM-DD HH:MM:SS UTC |
| **Documentees** | Fichier + ligne + justification pour chaque modification |
| **Verifiables** | Commandes reproductibles fournies pour chaque verification |

### Journal des actions

Chaque rapport doit contenir une section "JOURNAL DES ACTIONS" avec:

```
[YYYY-MM-DD HH:MM:SS UTC] ACTION: description
  Fichier: /chemin/vers/fichier
  Ligne: XX
  Commande: commande executee
  Resultat: sortie brute
```

---

## ARTICLE 6 — CONDITION ABSOLUE

**AUCUNE commande ne sera consideree executee** tant que:

1. Les **PREUVES** completes n'auront pas ete fournies (Article 2)
2. Les **LIVRABLES** exiges n'auront pas ete produits (Article 3)
3. Le **RAPPORT CONSOLIDE** n'aura pas ete genere (Article 3)
4. Le **STATUT DE CONFORMITE** n'aura pas ete etabli (Article 4)
5. Le **JOURNAL DES ACTIONS** n'aura pas ete documente (Article 5)
6. Le **COMMANDANT STEEVE-MAX** n'aura pas valide l'ensemble

### Hierarchie de validation

```
Agent execute la commande
    → Produit les preuves
    → Genere les livrables
    → Redige le rapport consolide
    → Etablit le statut de conformite
    → Journalise les actions
    → SOUMET au Commandant STEEVE-MAX
    → ATTEND validation explicite
    → Commande consideree executee UNIQUEMENT apres validation
```

---

## ARTICLE 7 — APPLICATION RETROACTIVE

Ce cadre s'applique:
- A TOUTES les commandes futures du Commandant STEEVE-MAX
- A TOUTES les reponses de l'agent BCE-4X
- SANS exception, SANS expiration, SANS derogation

Toute reponse ne respectant pas ce format est automatiquement **NON CONFORME**.

---

**DATE D'ETABLISSEMENT:** 2026-04-09 13:35 UTC
**STATUT:** PERMANENT — ACTIF — IRREVOCABLE
**AUTEUR:** Agent BCE-4X sous ordres COMMANDANT STEEVE-MAX

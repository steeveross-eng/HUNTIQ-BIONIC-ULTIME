# SUPRA_ENGAGEMENT_OPERATIONNEL.md
# ============================================================
# COMPLEMENT (B) — ENGAGEMENT OPERATIONNEL R1-R9
# ============================================================
# Protocole: BCE-4X-GLOBAL-PLUS-TOTAL | Pression x2
# Autorite: COMMANDANT STEEVE-MAX
# Branche: BIONIC_REWRITE_P0
# Date: 2026-02-07
# Statut: LIVRABLE — EN ATTENTE DE VALIDATION
# ============================================================

---

## 1. RESSOURCES ASSIGNEES

### 1.1 Equipe operationnelle

| Role | Ressource | Responsabilite |
|---|---|---|
| **Commandant** | STEEVE-MAX | Autorite finale, validation phases, directives, conditions STOP |
| **Operateur** | EMERGENT Agent | Execution code, tests, documentation, commits |
| **Gatekeeper** | Pre-commit BCE-4X | Validation automatisee SHA256, imports, overlaps |

### 1.2 Environnement technique

| Ressource | Configuration | Disponibilite |
|---|---|---|
| Branche active | `BIONIC_REWRITE_P0` | Permanente |
| Branche reconstruction | `SUPRA_RECONSTRUCTION` (a creer depuis BIONIC_REWRITE_P0) | Phase R0 |
| Backend FastAPI | Port 8001 (supervisor) | Hot reload actif |
| Frontend React | Port 3000 (supervisor) | Hot reload actif |
| Preview URL | https://ultime-preview.preview.emergentagent.com | Permanente |
| Tests API | curl + screenshot tool | Permanente |
| Linter Frontend | ESLint | Disponible |
| Linter Backend | ruff | Disponible |

### 1.3 Outils de validation

| Outil | Usage | Phase(s) |
|---|---|---|
| `curl` + `python3 -c` | Tests API backend (scores, latence) | R0-R8 |
| Screenshot tool (Playwright) | Captures visuelles frontend | R0, R1-R8 |
| `grep -c` / `grep -n` | Verification code (IC count, testid, alias) | R1-R8 |
| `wc -l` | Verification taille fichier | R3, R8 |
| `sha256sum` | Verrouillage fichiers critiques | R9 |
| `time curl` | Benchmark latence (10 runs) | R0, R6, R8 |
| `git diff` | Verification diff entre phases | R1-R9 |

---

## 2. DUREE REELLE ESTIMEE

### 2.1 Estimation par phase

| Phase | Description | Duree code | Duree tests | Duree doc | Total | Risque horaire |
|---|---|---|---|---|---|---|
| R0 | Preparation | 5 min | 15 min | 5 min | **25 min** | FAIBLE |
| R1 | Nettoyage code mort | 2 min | 8 min | 3 min | **13 min** | NEGLIGEABLE |
| R2 | Extraction IC | 10 min | 10 min | 3 min | **23 min** | FAIBLE |
| R3 | Modularisation tabs | 40 min | 25 min | 5 min | **70 min** | ELEVE |
| R4 | Corrections UX | 20 min | 15 min | 5 min | **40 min** | MODERE |
| R5 | Coherence donnees | 20 min | 15 min | 5 min | **40 min** | MODERE |
| R6 | Optimisation backend | 25 min | 15 min | 5 min | **45 min** | MODERE |
| R7 | Externalisation PREMIUM | 20 min | 10 min | 5 min | **35 min** | FAIBLE |
| R8 | Audit post-reconstruction | 5 min | 30 min | 15 min | **50 min** | FAIBLE |
| R9 | Verrouillage | 5 min | 5 min | 5 min | **15 min** | NEGLIGEABLE |
| | **TOTAL** | **152 min** | **148 min** | **56 min** | **356 min (~6h)** | |

### 2.2 Repartition du temps

```
Code:          152 min (42.7%)
Tests:         148 min (41.6%)
Documentation:  56 min (15.7%)
TOTAL:         356 min (~6 heures)
```

### 2.3 Marge de securite

| Scenario | Multiplicateur | Duree totale |
|---|---|---|
| Nominal (tout passe) | x1.0 | 6h |
| Moderement optimiste | x1.2 | 7h 10min |
| Realiste (1-2 rollbacks) | x1.5 | 9h |
| Pessimiste (rollbacks multiples) | x2.0 | 12h |

**Estimation retenue: 6-9 heures** (scenario realiste avec 1-2 rollbacks mineurs)

---

## 3. POINTS DE CONTROLE PAR PHASE

### 3.1 Checkpoints detailles

#### PHASE R0 — PREPARATION
| Checkpoint | Action | Livrable | Validation |
|---|---|---|---|
| R0.1 | Creer branche `SUPRA_RECONSTRUCTION` | Branche creee | `git branch --show-current` |
| R0.2 | Capturer 5 screenshots de reference (1 par onglet) | 5 fichiers PNG | Verification visuelle |
| R0.3 | Baseline performance (10 runs) | Tableau latence | Deja fait (L9) — Verification |
| R0.4 | Verifier test d'import | `python3 -c "from engines.nutrition_intelligence import *"` | Exit code 0 |
| **GATE R0** | **Tous checkpoints R0 verts** | | **Autorisation R1 par Commandant** |

#### PHASE R1 — NETTOYAGE CODE MORT
| Checkpoint | Action | Livrable | Validation |
|---|---|---|---|
| R1.1 | Supprimer lignes 166-167 (alias Card, CollapsibleSection) | Fichier modifie | `grep -c "const Card = \|const CollapsibleSection = " → 0` |
| R1.2 | Commit + lint | Commit clean | ESLint PASS |
| R1.3 | Tests de garde | T04 + T15-T19 | TOUS PASS |
| R1.4 | Verification scores | curl 4 endpoints | Scores = baselines |
| **GATE R1** | **T04 PASS + scores inchanges** | | **Passage R2 automatique** |

#### PHASE R2 — EXTRACTION IC
| Checkpoint | Action | Livrable | Validation |
|---|---|---|---|
| R2.1 | Creer `territoire/ui/IconCircle.jsx` | Nouveau fichier | Fichier existe |
| R2.2 | Remplacer 5 definitions IC par imports | 5 modifications | `grep -c "const IC" → 0` dans le fichier principal |
| R2.3 | Commit + lint | Commit clean | ESLint PASS |
| R2.4 | Tests de garde | T01 + T15-T19 | TOUS PASS |
| R2.5 | Verification scores | curl 4 endpoints | Scores = baselines |
| **GATE R2** | **T01 PASS + scores inchanges** | | **Passage R3 automatique** |

#### PHASE R3 — MODULARISATION TABS (ZONE CRITIQUE)
| Checkpoint | Action | Livrable | Validation |
|---|---|---|---|
| R3.1 | Creer `territoire/supra/constants.js` (BIONIC, GOLDEN, GaugeMini, GoldenCard, GoldenCollapsible, SupraButton) | Nouveau fichier | Fichier existe, exports verifies |
| R3.2 | Extraire AnalyseTab → `supra/AnalyseTab.jsx` | Nouveau fichier | Import fonctionne |
| R3.3 | Test de garde apres AnalyseTab | T15 (screenshot ANALYSE) | ANALYSE rendu identique |
| R3.4 | Extraire FicheTab → `supra/FicheTab.jsx` | Nouveau fichier | Import fonctionne |
| R3.5 | Test de garde apres FicheTab | T16 (screenshot FICHE) | FICHE rendu identique |
| R3.6 | Extraire IntelligenceTab → `supra/IntelligenceTab.jsx` | Nouveau fichier | Import fonctionne |
| R3.7 | Extraire ComparezTab → `supra/ComparezTab.jsx` | Nouveau fichier | Import fonctionne |
| R3.8 | Extraire CommandezTab → `supra/CommandezTab.jsx` | Nouveau fichier | Import fonctionne |
| R3.9 | Test de garde complet | T17, T18 (screenshots) | Rendus identiques |
| R3.10 | Reduire NutritionPointDetailPanel.jsx | Fichier < 500 lignes | `wc -l < 500` |
| R3.11 | Test complet | T12 + T15-T20 | TOUS PASS |
| R3.12 | Verification scores | curl 4 endpoints | Scores = baselines |
| R3.13 | Commit | Commit clean | ESLint PASS |
| **GATE R3** | **T12 PASS + T15-T20 PASS + scores inchanges** | | **Validation Commandant REQUISE** |

#### PHASE R4 — CORRECTIONS UX
| Checkpoint | Action | Livrable | Validation |
|---|---|---|---|
| R4.1 | Corriger COMPAREZ grid-cols-4 | Fichier modifie | 4 produits visibles |
| R4.2 | Equilibrer colonnes INTELLIGENCE | Fichier modifie | Round-robin |
| R4.3 | Supprimer fallback product_id | Fichier modifie | Avertissement si manquant |
| R4.4 | Tests | T03, T09, T10, T13 + T15-T19 | TOUS PASS |
| R4.5 | Verification scores | curl 4 endpoints | Scores = baselines |
| **GATE R4** | **4 tests PASS + scores inchanges** | | **Passage R5 automatique** |

#### PHASE R5 — COHERENCE DONNEES
| Checkpoint | Action | Livrable | Validation |
|---|---|---|---|
| R5.1 | Unifier source sol (choix: soil_engine OU saline_engine) | Fichier modifie | Source unique |
| R5.2 | Harmoniser saison (seasonMap partout) | Fichier modifie | Coherence verifiee |
| R5.3 | Documenter FICHE deterministe | Header ajoute | Grep documentation |
| R5.4 | Tests | T05, T06, T07, T11 + T15-T19 | TOUS PASS |
| R5.5 | Verification scores | curl 4 endpoints | Scores = baselines |
| **GATE R5** | **4 tests PASS + scores inchanges** | | **Passage R6 automatique** |

#### PHASE R6 — OPTIMISATION BACKEND
| Checkpoint | Action | Livrable | Validation |
|---|---|---|---|
| R6.1 | Creer fonctions batch x6010, x6011, x6012 | 3 fichiers modifies | Fonctions exportees |
| R6.2 | Remplacer boucle N+1 dans router.py | router.py modifie | Boucle eliminee |
| R6.3 | Benchmark | 10 runs supra-panel | Latence <= baseline |
| R6.4 | Tests | T08, T14 + T15-T19 | TOUS PASS |
| R6.5 | Verification scores | curl 4 endpoints | Scores = baselines |
| **GATE R6** | **T08 PASS + scores inchanges + latence <= baseline** | | **Passage R7 automatique** |

#### PHASE R7 — EXTERNALISATION PREMIUM
| Checkpoint | Action | Livrable | Validation |
|---|---|---|---|
| R7.1 | Creer endpoint `/api/v6/nutrition-intelligence/premium-data` | router.py modifie | Endpoint repond 200 |
| R7.2 | Migrer 3 structures de donnees vers backend | Backend modifie | JSON valide |
| R7.3 | Frontend: fetch au lieu de hardcode | Tab modifie | Donnees affichees |
| R7.4 | Ajouter MALE_BEHAVIOR pour orignal | Donnees completees | Orignal present |
| R7.5 | Tests | T02 + T15-T19 | TOUS PASS |
| R7.6 | Verification scores | curl 4 endpoints | Scores = baselines |
| **GATE R7** | **T02 PASS + scores inchanges** | | **Passage R8 automatique** |

#### PHASE R8 — AUDIT POST-RECONSTRUCTION
| Checkpoint | Action | Livrable | Validation |
|---|---|---|---|
| R8.1 | Executer les 20 tests T01-T20 | Rapport de tests | 20/20 PASS |
| R8.2 | 10 runs stabilite (4 endpoints) | Tableau scores + latences | Scores = baselines, variance = 0 |
| R8.3 | Screenshots 5 onglets post-reconstruction | 5 fichiers PNG | Comparaison avec R0 |
| R8.4 | Produire SUPRA_RECONSTRUCTION_VALIDATION.md | Rapport final | Complet |
| **GATE R8** | **20/20 PASS + scores = baselines + visuels conformes** | | **Validation Commandant REQUISE** |

#### PHASE R9 — VERROUILLAGE
| Checkpoint | Action | Livrable | Validation |
|---|---|---|---|
| R9.1 | SHA256 de tous les fichiers SUPRA reconstruits | Hash manifest | sha256sum verifie |
| R9.2 | Mettre a jour BCE4X_GLOBAL_LOCK.json | Lock file | JSON valide |
| R9.3 | Merge SUPRA_RECONSTRUCTION → BIONIC_REWRITE_P0 | Branche fusionnee | git merge OK |
| R9.4 | Supprimer branche SUPRA_RECONSTRUCTION | Nettoyage | Branche supprimee |
| **GATE R9** | **Lock file a jour + merge OK** | | **RECONSTRUCTION TERMINEE** |

---

## 4. CRITERES DE VALIDATION PAR PHASE

### 4.1 Criteres quantitatifs

| Phase | Tests requis | Score SUPRA | Score ULTRA | Score FICHE | Score SOL | Latence max |
|---|---|---|---|---|---|---|
| R0 | Baseline | 63 | 47.8 | 71 | 47 | Enregistree |
| R1 | T04 + T15-T19 | = 63 | = 47.8 | = 71 | = 47 | <= baseline |
| R2 | T01 + T15-T19 | = 63 | = 47.8 | = 71 | = 47 | <= baseline |
| R3 | T12 + T15-T20 | = 63 | = 47.8 | = 71 | = 47 | <= baseline +10% |
| R4 | T03,T09,T10,T13 + T15-T19 | = 63 | = 47.8 | = 71 | = 47 | <= baseline |
| R5 | T05,T06,T07,T11 + T15-T19 | = 63 | = 47.8 | = 71 | = 47 | <= baseline |
| R6 | T08,T14 + T15-T19 | = 63 | = 47.8 | = 71 | = 47 | <= baseline |
| R7 | T02 + T15-T19 | = 63 | = 47.8 | = 71 | = 47 | <= baseline +5% |
| R8 | T01-T20 (TOUS) | = 63 | = 47.8 | = 71 | = 47 | <= baseline |
| R9 | SHA256 | N/A | N/A | N/A | N/A | N/A |

### 4.2 Criteres qualitatifs

| Phase | Critere | Methode de verification |
|---|---|---|
| R3 | Rendu visuel IDENTIQUE au R0 | Comparaison screenshots |
| R3 | GUIDE PRO en position 1 dans ANALYSE | T19 screenshot |
| R3 | data-testid preserves | T20 grep |
| R3 | Vegetation/Hydrologie cote-a-cote | T15 screenshot |
| R4 | 4 produits visibles dans COMPAREZ | T10 screenshot |
| R5 | Source sol unique et coherente | T06 screenshot |
| R7 | Donnees PREMIUM affichees depuis backend | T02 curl + T15 screenshot |
| R8 | GOLDEN 11/11 normes respectees | Verification manuelle |

### 4.3 Phases necessitant validation Commandant

| Phase | Raison | Type de validation |
|---|---|---|
| R0 → R1 | Premiere action de modification | Validation initiale |
| R3 → R4 | Zone critique (score risque 38) | Validation post-modularisation |
| R8 → R9 | Fin de reconstruction | Certification finale |

---

## 5. ENGAGEMENT FORMEL

L'operateur EMERGENT s'engage a:

1. **Respecter la sequence R0 → R9** sans saut ni parallelisation de phases
2. **Verifier les 4 scores de baseline** apres CHAQUE phase
3. **Executer les tests de garde T15-T19** apres CHAQUE phase
4. **Commiter atomiquement** a la fin de chaque phase
5. **Produire un rapport de phase** avec resultats des tests
6. **Activer le ROLLBACK immediat** si une condition STOP est declenchee
7. **Attendre la validation du Commandant** aux points de controle R0, R3, R8
8. **NE JAMAIS modifier** les fichiers x5500, x5600 (noeuds centraux HORS PERIMETRE)
9. **NE JAMAIS merge** vers `main`

---

*Engagement genere conformement au protocole BCE-4X-GLOBAL-PLUS-TOTAL*
*Autorite: COMMANDANT STEEVE-MAX*
*Branche: BIONIC_REWRITE_P0*
*Date: 2026-02-07*

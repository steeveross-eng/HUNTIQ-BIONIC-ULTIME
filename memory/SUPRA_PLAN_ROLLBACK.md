# SUPRA_PLAN_ROLLBACK.md
# ============================================================
# COMPLEMENT (C) — PLAN DE ROLLBACK BCE-4X
# ============================================================
# Protocole: BCE-4X-GLOBAL-PLUS-TOTAL | Pression x2
# Autorite: COMMANDANT STEEVE-MAX
# Branche: BIONIC_REWRITE_P0
# Date: 2026-02-07
# Statut: LIVRABLE — EN ATTENTE DE VALIDATION
# ============================================================

---

## 1. STRATEGIE DE RETOUR ARRIERE

### 1.1 Principe fondamental

La strategie de rollback repose sur un systeme de **commits atomiques par phase**.
Chaque phase R1-R9 produit exactement 1 commit. Le rollback consiste a annuler
le commit de la phase en echec et revenir au commit de la phase precedente.

### 1.2 Architecture de branchement

```
BIONIC_REWRITE_P0 (branche stable, NE PAS TOUCHER)
  |
  └── SUPRA_RECONSTRUCTION (branche de travail, creee en R0)
        |
        ├── Commit R0: "R0: Preparation — baselines + screenshots reference"
        ├── Commit R1: "R1: Nettoyage code mort — alias supprimes"
        ├── Commit R2: "R2: Extraction IC — composant partage"
        ├── Commit R3: "R3: Modularisation tabs — 8 fichiers"
        ├── Commit R4: "R4: Corrections UX — COMPAREZ/INTELLIGENCE/fallback"
        ├── Commit R5: "R5: Coherence donnees — source sol/saison/documentation"
        ├── Commit R6: "R6: Optimisation backend — batch enrichissement"
        ├── Commit R7: "R7: Externalisation PREMIUM — endpoint + migration"
        └── Commit R8: "R8: Audit post-reconstruction — validation complete"

Si R8 valide par le Commandant:
  → R9: Merge SUPRA_RECONSTRUCTION → BIONIC_REWRITE_P0
  → Suppression de SUPRA_RECONSTRUCTION

Si ECHEC a n'importe quelle phase:
  → Rollback au commit precedent
  → OU suppression complete de SUPRA_RECONSTRUCTION
  → BIONIC_REWRITE_P0 reste INTACT
```

### 1.3 Niveaux de rollback

| Niveau | Description | Quand utiliser | Commande |
|---|---|---|---|
| **MICRO** | Annuler la derniere modification dans une phase | Erreur mineure, correction possible | `git checkout -- <fichier>` |
| **PHASE** | Annuler le commit entier d'une phase | Test echoue, score devie | `git reset --hard HEAD~1` |
| **TOTAL** | Supprimer la branche SUPRA_RECONSTRUCTION | Echec irrecuperable, directive Commandant | `git checkout BIONIC_REWRITE_P0 && git branch -D SUPRA_RECONSTRUCTION` |

---

## 2. POINTS DE RUPTURE

### 2.1 Definition des points de rupture (Breakpoints)

Un point de rupture est un moment ou le systeme peut devenir instable.
Chaque point a une condition de detection et une procedure de rollback associee.

| ID | Phase | Point de rupture | Detection | Probabilite | Severite |
|---|---|---|---|---|---|
| BP01 | R2 | Import IC echoue apres extraction | ESLint erreur / panneau blanc | MOYENNE | HAUTE |
| BP02 | R3.2 | AnalyseTab extrait mais imports manquants | Screenshot ANALYSE vide | HAUTE | CRITIQUE |
| BP03 | R3.4 | FicheTab extrait, CriteriaDetailModal non importe | Screenshot FICHE casse | MOYENNE | HAUTE |
| BP04 | R3.6 | IntelligenceTab extrait, products non passes en props | Screenshot INTELLIGENCE vide | MOYENNE | HAUTE |
| BP05 | R3.8 | CommandezTab extrait, callbacks (addToCart, handleCheckout) non passes | Boutons panier HS | MOYENNE | HAUTE |
| BP06 | R3.10 | Fichier principal ne compile pas apres extraction | React erreur compilation | FAIBLE | CRITIQUE |
| BP07 | R4.1 | COMPAREZ grid-cols-4 casse le layout | Screenshot layout deforme | FAIBLE | MODERE |
| BP08 | R5.1 | Suppression source sol cause donnees manquantes | Panneau Sol vide dans ANALYSE | MOYENNE | HAUTE |
| BP09 | R5.2 | Harmonisation saison change les scores FICHE | Score FICHE != 71 | FAIBLE | CRITIQUE |
| BP10 | R6.2 | Batch enrichissement change le format produits | INTELLIGENCE ne rend pas les produits | MOYENNE | HAUTE |
| BP11 | R7.1 | Endpoint premium-data retourne 500 | curl retourne erreur | FAIBLE | MODERE |
| BP12 | R7.3 | Frontend fetch premium echoue | Section PREMIUM vide dans ANALYSE | MOYENNE | MODERE |

### 2.2 Classement par criticite

| Criticite | Points de rupture | Phase(s) |
|---|---|---|
| CRITIQUE | BP02, BP06, BP09 | R3, R5 |
| HAUTE | BP01, BP03, BP04, BP05, BP08, BP10 | R2, R3, R5, R6 |
| MODERE | BP07, BP11, BP12 | R4, R7 |

---

## 3. CONDITIONS D'ACTIVATION DU ROLLBACK

### 3.1 Conditions automatiques (STOP CONDITIONS)

| ID | Condition | Detection | Action automatique |
|---|---|---|---|
| STOP-1 | Score SUPRA != 63 | `curl supra-panel \| python3 -c "...score_global..."` | ROLLBACK PHASE |
| STOP-2 | Score ULTRA != 47.8 | `curl saline/analyze \| python3 -c "...global_score..."` | ROLLBACK PHASE |
| STOP-3 | Score FICHE != 71 | `curl salines-ultime/fiche \| python3 -c "...score..."` | ROLLBACK PHASE |
| STOP-4 | Score SOL != 47 | `curl soil/analyze \| python3 -c "...score..."` | ROLLBACK PHASE |
| STOP-5 | Latence supra-panel > 500ms (3 runs consecutifs) | `time curl supra-panel` x3 | INVESTIGATION 5min, puis ROLLBACK PHASE si non resolu |
| STOP-6 | ESLint erreur critique (syntax error) | `npx eslint NutritionPointDetailPanel.jsx` | ROLLBACK MICRO |
| STOP-7 | Backend ne demarre pas (ImportError) | `tail -5 /var/log/supervisor/backend.err.log` | ROLLBACK PHASE |
| STOP-8 | Frontend ne compile pas (React error) | `tail -5 /var/log/supervisor/frontend.err.log` | ROLLBACK PHASE |

### 3.2 Conditions manuelles (directive Commandant)

| ID | Condition | Action |
|---|---|---|
| STOP-CMD1 | Directive explicite du Commandant: "STOP" | ARRET IMMEDIAT, attente instructions |
| STOP-CMD2 | Directive explicite du Commandant: "ROLLBACK" | ROLLBACK au niveau specifie (PHASE ou TOTAL) |
| STOP-CMD3 | Directive explicite du Commandant: "ROLLBACK TOTAL" | Suppression SUPRA_RECONSTRUCTION, retour BIONIC_REWRITE_P0 |

### 3.3 Matrice de decision

```
DETECTION ANOMALIE
  |
  ├── Score devie? ─────────────── OUI → STOP-1/2/3/4 → ROLLBACK PHASE
  |
  ├── Backend HS? ──────────────── OUI → STOP-7 → ROLLBACK PHASE
  |
  ├── Frontend HS? ─────────────── OUI → STOP-8 → ROLLBACK PHASE
  |
  ├── Latence > 500ms? ─────────── OUI → STOP-5 → Investigation 5min
  |                                          |
  |                                          ├── Resolu → CONTINUER
  |                                          └── Non resolu → ROLLBACK PHASE
  |
  ├── ESLint erreur? ───────────── OUI → STOP-6 → ROLLBACK MICRO
  |
  └── Directive Commandant? ────── OUI → STOP-CMD1/2/3 → ACTION COMMANDEE
```

---

## 4. PROCEDURES DE RESTAURATION

### 4.1 Procedure ROLLBACK MICRO

**Quand:** Erreur mineure dans un fichier pendant une phase en cours.

```bash
# 1. Identifier le fichier en erreur
git status

# 2. Restaurer le fichier a son etat du dernier commit
git checkout -- <fichier>

# 3. Verifier la compilation
tail -5 /var/log/supervisor/frontend.err.log
tail -5 /var/log/supervisor/backend.err.log

# 4. Verifier les scores
API=$(grep REACT_APP_BACKEND_URL /app/frontend/.env | cut -d '=' -f2)
curl -s -X POST "$API/api/v6/nutrition-intelligence/supra-panel" \
  -H "Content-Type: application/json" \
  -d '{"species":"orignal","season":"automne","soil_type":"mixte","substrate":"bois_mou","lat":47.3,"lng":-71.2}' \
  | python3 -c "import sys,json;d=json.load(sys.stdin);print('SUPRA:', d['score']['score_global'])"

# 5. Si scores OK → Reprendre la phase
# 6. Si scores NON OK → Escalader vers ROLLBACK PHASE
```

### 4.2 Procedure ROLLBACK PHASE

**Quand:** Un test echoue ou un score devie apres le commit d'une phase.

```bash
# 1. Identifier la phase en echec
git log --oneline -5

# 2. Annuler le dernier commit (phase en echec)
git reset --hard HEAD~1

# 3. Redemarrer les services
sudo supervisorctl restart backend
sudo supervisorctl restart frontend
sleep 5

# 4. Verifier les 4 scores de baseline
API=$(grep REACT_APP_BACKEND_URL /app/frontend/.env | cut -d '=' -f2)
echo "SUPRA:" && curl -s -X POST "$API/api/v6/nutrition-intelligence/supra-panel" \
  -H "Content-Type: application/json" \
  -d '{"species":"orignal","season":"automne","soil_type":"mixte","substrate":"bois_mou","lat":47.3,"lng":-71.2}' \
  | python3 -c "import sys,json;d=json.load(sys.stdin);print(d['score']['score_global'])"
echo "ULTRA:" && curl -s -X POST "$API/api/v1/saline/analyze" \
  -H "Content-Type: application/json" \
  -d '{"lat":47.3,"lng":-71.2,"species":"orignal","sex":"male","age":"adult","month":10,"season":"automne"}' \
  | python3 -c "import sys,json;d=json.load(sys.stdin);print(d['analysis']['intelligence_score']['global_score'])"
echo "FICHE:" && curl -s "$API/api/v1/salines-ultime/fiche?lat=47.3&lng=-71.2&species=orignal&season=automne" \
  | python3 -c "import sys,json;d=json.load(sys.stdin);print(d['global_score']['score'])"
echo "SOL:" && curl -s "$API/api/v1/soil/analyze?lat=47.3&lng=-71.2&species=orignal&season=automne" \
  | python3 -c "import sys,json;d=json.load(sys.stdin);print(d['score'])"

# 5. Resultats attendus: SUPRA=63, ULTRA=47.8, FICHE=71, SOL=47

# 6. Si scores OK → Phase annulee avec succes, reprendre avec strategie alternative
# 7. Si scores NON OK → Escalader vers ROLLBACK TOTAL
```

### 4.3 Procedure ROLLBACK TOTAL

**Quand:** Echec irrecuperable ou directive du Commandant.

```bash
# 1. Revenir sur la branche stable
git checkout BIONIC_REWRITE_P0

# 2. Supprimer la branche de reconstruction
git branch -D SUPRA_RECONSTRUCTION

# 3. Redemarrer les services
sudo supervisorctl restart backend
sudo supervisorctl restart frontend
sleep 5

# 4. Verifier les 4 scores de baseline (meme commandes que 4.2 etape 4)

# 5. Verifier la compilation frontend
tail -5 /var/log/supervisor/frontend.err.log

# 6. Screenshot de verification
# → Capturer l'etat de l'application

# 7. Rapport au Commandant:
#    "ROLLBACK TOTAL execute. BIONIC_REWRITE_P0 restaure.
#     Scores verifies: SUPRA=63, ULTRA=47.8, FICHE=71, SOL=47.
#     Application operationnelle."

# 8. Attente directive du Commandant pour suite des operations
```

---

## 5. PLAN DE RESTAURATION PAR PHASE

### 5.1 Points de sauvegarde

| Phase | Commit de sauvegarde | Etat sauvegarde | Fichiers modifies |
|---|---|---|---|
| Pre-R0 | HEAD de BIONIC_REWRITE_P0 | Etat actuel stable | Aucun |
| Post-R0 | Commit R0 | + screenshots + baseline docs | +docs seulement |
| Post-R1 | Commit R1 | - alias Card/CollapsibleSection | -2 lignes |
| Post-R2 | Commit R2 | + IconCircle.jsx, - 5 def IC | +1 fichier, -40 lignes |
| Post-R3 | Commit R3 | + 7 fichiers supra/, - contenu tabs | +7 fichiers, refacto majeur |
| Post-R4 | Commit R4 | + corrections UX | Modifications mineures |
| Post-R5 | Commit R5 | + coherence donnees | Modifications mineures |
| Post-R6 | Commit R6 | + batch enrichissement | Backend modifie |
| Post-R7 | Commit R7 | + endpoint premium-data | +1 endpoint, frontend modifie |
| Post-R8 | Commit R8 | + rapport validation | +docs seulement |

### 5.2 Procedures specifiques par phase

| Phase echec | Rollback vers | Procedure specifique | Risque residuel |
|---|---|---|---|
| R1 echoue | Pre-R0 | `git reset --hard HEAD~1` | ZERO (2 lignes supprimees) |
| R2 echoue | Post-R1 | `git reset --hard HEAD~1` | ZERO (IC restaure) |
| R3 echoue | Post-R2 | `git reset --hard HEAD~1` + suppression des 7 fichiers crees | FAIBLE — Verifier que le fichier monolithique est intact |
| R4 echoue | Post-R3 | `git reset --hard HEAD~1` | ZERO |
| R5 echoue | Post-R4 | `git reset --hard HEAD~1` | FAIBLE — Verifier scores (E07/saison) |
| R6 echoue | Post-R5 | `git reset --hard HEAD~1` | FAIBLE — Verifier latence backend |
| R7 echoue | Post-R6 | `git reset --hard HEAD~1` | ZERO |
| R8 echoue | Post-R7 | INVESTIGATION — R8 est un audit, pas une modification | ZERO |

---

## 6. GARANTIES DE SECURITE

### 6.1 Invariants maintenus

| Invariant | Description | Comment garanti |
|---|---|---|
| I1 | BIONIC_REWRITE_P0 n'est JAMAIS modifie pendant R1-R8 | Travail sur branche separee |
| I2 | Les 4 scores de baseline sont verifies apres chaque phase | Procedure automatisee |
| I3 | Le rollback vers l'etat stable est toujours possible | Commits atomiques |
| I4 | Le Commandant peut stopper a tout moment | STOP-CMD1/2/3 |
| I5 | Aucun merge vers main | Regle absolue BCE-4X |

### 6.2 Duree maximale d'indisponibilite

| Scenario | Duree d'indisponibilite | Procedure |
|---|---|---|
| ROLLBACK MICRO | < 1 minute | git checkout -- fichier |
| ROLLBACK PHASE | < 3 minutes | git reset + restart services |
| ROLLBACK TOTAL | < 5 minutes | git checkout branche + restart services |

### 6.3 Verification post-rollback

Apres tout rollback, les 4 verifications suivantes sont OBLIGATOIRES:

```
1. Scores:   SUPRA=63, ULTRA=47.8, FICHE=71, SOL=47
2. Services: backend + frontend operationnels
3. Frontend: panneau SUPRA affichable (screenshot)
4. Rapport:  au Commandant avec etat restaure
```

---

*Plan de Rollback genere conformement au protocole BCE-4X-GLOBAL-PLUS-TOTAL*
*Autorite: COMMANDANT STEEVE-MAX*
*Branche: BIONIC_REWRITE_P0*
*Date: 2026-02-07*

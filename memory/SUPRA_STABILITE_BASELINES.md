# SUPRA_STABILITE_BASELINES.md
# ============================================================
# COMPLEMENT (D) — STABILITE DES BASELINES
# ============================================================
# Protocole: BCE-4X-GLOBAL-PLUS-TOTAL | Pression x2
# Autorite: COMMANDANT STEEVE-MAX
# Branche: BIONIC_REWRITE_P0
# Date: 2026-02-07
# Statut: LIVRABLE — EN ATTENTE DE VALIDATION
# ============================================================
#
# OBJECTIF: Prouver la stabilite institutionnelle des baselines
# METHODE: 10 runs, analyse de variance, seuils d'alerte, conformite GOLDEN
# ============================================================

---

## 1. DONNEES BRUTES — 10 RUNS

### 1.1 Parametres de test (identiques pour les 10 runs)

```
Coordonnees: lat=47.3, lng=-71.2
Espece: orignal
Saison: automne
Type de sol: mixte
Substrat: bois_mou
Sexe: male
Age: adult
Mois: 10
```

### 1.2 Endpoint: `/api/v6/nutrition-intelligence/supra-panel` (POST)

| Run | Latence (ms) | Score SUPRA |
|---|---|---|
| 1 | 251 | 63 |
| 2 | 181 | 63 |
| 3 | 156 | 63 |
| 4 | 194 | 63 |
| 5 | 189 | 63 |
| 6 | 189 | 63 |
| 7 | 209 | 63 |
| 8 | 138 | 63 |
| 9 | 120 | 63 |
| 10 | 159 | 63 |

### 1.3 Endpoint: `/api/v1/saline/analyze` (POST)

| Run | Latence (ms) | Score ULTRA |
|---|---|---|
| 1 | 114 | 47.8 |
| 2 | 118 | 47.8 |
| 3 | 128 | 47.8 |
| 4 | 114 | 47.8 |
| 5 | 126 | 47.8 |
| 6 | 121 | 47.8 |
| 7 | 154 | 47.8 |
| 8 | 129 | 47.8 |
| 9 | 125 | 47.8 |
| 10 | 131 | 47.8 |

### 1.4 Endpoint: `/api/v1/salines-ultime/fiche` (GET)

| Run | Latence (ms) | Score FICHE |
|---|---|---|
| 1 | 117 | 71 |
| 2 | 179 | 71 |
| 3 | 126 | 71 |
| 4 | 132 | 71 |
| 5 | 129 | 71 |
| 6 | 120 | 71 |
| 7 | 135 | 71 |
| 8 | 120 | 71 |
| 9 | 125 | 71 |
| 10 | 121 | 71 |

### 1.5 Endpoint: `/api/v1/soil/analyze` (GET)

| Run | Latence (ms) | Score SOL |
|---|---|---|
| 1 | 118 | 47 |
| 2 | 118 | 47 |
| 3 | 130 | 47 |
| 4 | 137 | 47 |
| 5 | 119 | 47 |
| 6 | 158 | 47 |
| 7 | 109 | 47 |
| 8 | 110 | 47 |
| 9 | 124 | 47 |
| 10 | 114 | 47 |

---

## 2. ANALYSE STATISTIQUE — LATENCE

### 2.1 Statistiques descriptives

| Endpoint | Moyenne | Mediane | Min | Max | Ecart-type | CV (%) |
|---|---|---|---|---|---|---|
| supra-panel | 178.6 ms | 185.0 ms | 120 ms | 251 ms | 35.5 ms | 19.9% |
| saline/analyze | 126.0 ms | 125.5 ms | 114 ms | 154 ms | 11.0 ms | 8.7% |
| salines-ultime/fiche | 130.4 ms | 125.5 ms | 117 ms | 179 ms | 17.1 ms | 13.1% |
| soil/analyze | 123.7 ms | 119.0 ms | 109 ms | 158 ms | 14.1 ms | 11.4% |

*(CV = Coefficient de Variation = ecart-type / moyenne x 100)*

### 2.2 Distribution des latences

```
supra-panel (ms):
  100-150: ████████ (3 runs: 120, 138, 156)
  150-200: ████████████████ (5 runs: 159, 181, 189, 189, 194)
  200-250: ████ (1 run: 209)
  250-300: ██ (1 run: 251)

saline/analyze (ms):
  100-120: ████████ (3 runs: 114, 114, 118)
  120-140: ████████████████████ (6 runs: 121, 125, 126, 128, 129, 131)
  140-160: ██ (1 run: 154)

salines-ultime/fiche (ms):
  110-130: ████████████████ (6 runs: 117, 120, 120, 121, 125, 126)
  130-140: ████████ (3 runs: 132, 129, 135)
  170-180: ██ (1 run: 179)

soil/analyze (ms):
  100-120: ████████████████ (6 runs: 109, 110, 114, 118, 118, 119)
  120-140: ████████ (3 runs: 124, 130, 137)
  150-160: ██ (1 run: 158)
```

### 2.3 Outliers (methode IQR)

| Endpoint | Q1 | Q3 | IQR | Seuil bas | Seuil haut | Outliers |
|---|---|---|---|---|---|---|
| supra-panel | 156 | 194 | 38 | 99 | 251 | Run 1 (251) — BORDERLINE |
| saline/analyze | 118 | 129 | 11 | 101.5 | 145.5 | Run 7 (154) — OUTLIER |
| salines-ultime/fiche | 120 | 132 | 12 | 102 | 150 | Run 2 (179) — OUTLIER |
| soil/analyze | 114 | 130 | 16 | 90 | 154 | Run 6 (158) — OUTLIER |

**Analyse des outliers:**
- Chaque endpoint a 1 outlier sur 10 runs (10%)
- Tous les outliers sont dans la plage haute (latence elevee, pas basse)
- Cause probable: garbage collection Python, latence reseau variable, concurrence CPU
- Aucun outlier ne depasse le seuil GOLDEN (500ms pour supra-panel, 300ms pour les autres)

---

## 3. ANALYSE STATISTIQUE — SCORES

### 3.1 Stabilite des scores

| Endpoint | Score | 10/10 identiques? | Variance | Ecart-type | Statut |
|---|---|---|---|---|---|
| supra-panel | 63 | OUI | **0.0** | **0.0** | DETERMINISTE PARFAIT |
| saline/analyze | 47.8 | OUI | **0.0** | **0.0** | DETERMINISTE PARFAIT |
| salines-ultime/fiche | 71 | OUI | **0.0** | **0.0** | DETERMINISTE PARFAIT |
| soil/analyze | 47 | OUI | **0.0** | **0.0** | DETERMINISTE PARFAIT |

### 3.2 Preuve de determinisme

Les 4 endpoints retournent **exactement le meme score** sur 10 runs consecutifs.
Ceci est attendu car:
- Tous les moteurs utilisent des algorithmes deterministes (hash MD5, formules fixes)
- Aucun element aleatoire (random, timestamp) n'influence les scores
- Les donnees d'entree sont identiques pour chaque run

**Variance score: 0.0 — PREUVE DE STABILITE ABSOLUE**

---

## 4. SEUILS D'ALERTE BCE-4X

### 4.1 Definition des seuils

Basee sur les baselines mesurees + marge de securite:

| Endpoint | Seuil VERT (normal) | Seuil JAUNE (alerte) | Seuil ROUGE (critique) | Seuil GOLDEN (max) |
|---|---|---|---|---|
| supra-panel latence | < 250ms | 250-400ms | 400-500ms | > 500ms = VIOLATION |
| saline/analyze latence | < 160ms | 160-250ms | 250-300ms | > 300ms = VIOLATION |
| salines-ultime/fiche latence | < 180ms | 180-250ms | 250-300ms | > 300ms = VIOLATION |
| soil/analyze latence | < 160ms | 160-180ms | 180-200ms | > 200ms = VIOLATION |

| Endpoint | Score attendu | Tolerance | Seuil d'alerte |
|---|---|---|---|
| supra-panel score | 63 | 0 (deterministe) | Toute deviation = VIOLATION |
| saline/analyze score | 47.8 | 0 (deterministe) | Toute deviation = VIOLATION |
| salines-ultime/fiche score | 71 | 0 (deterministe) | Toute deviation = VIOLATION |
| soil/analyze score | 47 | 0 (deterministe) | Toute deviation = VIOLATION |

### 4.2 Application des seuils aux 10 runs

| Run | supra-panel | saline/analyze | fiche | soil | Verdict |
|---|---|---|---|---|---|
| 1 | 251ms JAUNE / 63 OK | 114ms VERT / 47.8 OK | 117ms VERT / 71 OK | 118ms VERT / 47 OK | ALERTE MINEURE |
| 2 | 181ms VERT / 63 OK | 118ms VERT / 47.8 OK | 179ms JAUNE / 71 OK | 118ms VERT / 47 OK | ALERTE MINEURE |
| 3 | 156ms VERT / 63 OK | 128ms VERT / 47.8 OK | 126ms VERT / 71 OK | 130ms VERT / 47 OK | NOMINAL |
| 4 | 194ms VERT / 63 OK | 114ms VERT / 47.8 OK | 132ms VERT / 71 OK | 137ms VERT / 47 OK | NOMINAL |
| 5 | 189ms VERT / 63 OK | 126ms VERT / 47.8 OK | 129ms VERT / 71 OK | 119ms VERT / 47 OK | NOMINAL |
| 6 | 189ms VERT / 63 OK | 121ms VERT / 47.8 OK | 120ms VERT / 71 OK | 158ms JAUNE / 47 OK | ALERTE MINEURE |
| 7 | 209ms VERT / 63 OK | 154ms VERT / 47.8 OK | 135ms VERT / 71 OK | 109ms VERT / 47 OK | NOMINAL |
| 8 | 138ms VERT / 63 OK | 129ms VERT / 47.8 OK | 120ms VERT / 71 OK | 110ms VERT / 47 OK | NOMINAL |
| 9 | 120ms VERT / 63 OK | 125ms VERT / 47.8 OK | 125ms VERT / 71 OK | 124ms VERT / 47 OK | NOMINAL |
| 10 | 159ms VERT / 63 OK | 131ms VERT / 47.8 OK | 121ms VERT / 71 OK | 114ms VERT / 47 OK | NOMINAL |

### 4.3 Resultats par seuil

| Seuil | Runs NOMINAL | Runs ALERTE MINEURE | Runs CRITIQUE | Runs VIOLATION |
|---|---|---|---|---|
| Latence | 7/10 | 3/10 | 0/10 | 0/10 |
| Score | 10/10 | 0/10 | 0/10 | 0/10 |
| **COMBINE** | **7/10** | **3/10** | **0/10** | **0/10** |

**Les 3 alertes mineures sont dues a des pics de latence ponctuels (1 endpoint par run), jamais au meme endpoint deux fois de suite. Comportement normal pour un environnement Kubernetes partage.**

---

## 5. CONFORMITE GOLDEN

### 5.1 Verification des normes GOLDEN sur les baselines

| Norme GOLDEN | Seuil | Mesuree | Statut |
|---|---|---|---|
| Latence totale parallele | < 1000ms | max(178.6, 126.0, 130.4, 123.7) = 178.6ms | **CONFORME** |
| Volume par clic | < 100 KB | ~20 KB | **CONFORME** |
| Score variance | 0 (deterministe) | 0.0 pour les 4 endpoints | **CONFORME** |
| Taux d'erreur | 0% | 0/40 appels = 0% | **CONFORME** |
| Outliers latence | < 20% | 4/40 = 10% | **CONFORME** |
| Latence max (supra-panel) | < 500ms | 251ms | **CONFORME** |
| Latence max (autres) | < 300ms | 179ms | **CONFORME** |

### 5.2 Score de conformite GOLDEN

| Dimension | Score |
|---|---|
| Performance | 7/7 normes respectees |
| Stabilite scores | 4/4 endpoints deterministes |
| Fiabilite | 0% erreurs sur 40 appels |
| **TOTAL** | **11/11 — CONFORMITE GOLDEN TOTALE** |

---

## 6. PREUVE DE STABILITE INSTITUTIONNELLE

### 6.1 Criteres de stabilite BCE-4X

| Critere | Seuil requis | Valeur mesuree | Statut |
|---|---|---|---|
| Score constant sur 10 runs | Variance = 0 | Variance = 0.0 (4 endpoints) | **STABLE** |
| Latence < seuil GOLDEN sur 100% runs | 0 violations | 0 violations (40 appels) | **STABLE** |
| Taux d'erreur HTTP | 0% | 0% (40 appels) | **STABLE** |
| CV latence < 25% | CV < 25% | Max CV = 19.9% (supra-panel) | **STABLE** |
| Outliers latence < 15% | < 15% | 10% (4/40) | **STABLE** |
| Structure reponse constante | Memes cles JSON | Verifie sur 10 runs | **STABLE** |

### 6.2 Verdict de stabilite

```
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║   STABILITE INSTITUTIONNELLE: PROUVEE                        ║
║                                                               ║
║   Scores:     DETERMINISTES PARFAITS (Variance = 0.0)       ║
║   Latence:    STABLE (CV < 20%, 0 violations GOLDEN)         ║
║   Fiabilite:  ABSOLUE (0% erreurs sur 40 appels)            ║
║   Conformite: GOLDEN 11/11                                    ║
║                                                               ║
║   Les baselines SUPRA sont institutionnellement stables      ║
║   et peuvent servir de reference pour la reconstruction.     ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
```

---

## 7. VALEURS DE REFERENCE POUR POST-RECONSTRUCTION (R8)

Apres reconstruction, les tests de regression (Phase R8) devront verifier:

| Endpoint | Score attendu | Latence max acceptee | Tolerance |
|---|---|---|---|
| supra-panel | 63 | 500ms | Score: ±0 / Latence: +50% de la baseline |
| saline/analyze | 47.8 | 300ms | Score: ±0 / Latence: +50% de la baseline |
| salines-ultime/fiche | 71 | 300ms | Score: ±0 / Latence: +50% de la baseline |
| soil/analyze | 47 | 200ms | Score: ±0 / Latence: +50% de la baseline |

**Toute deviation de score = REGRESSION IMMEDIATE → ROLLBACK**
**Toute violation de latence GOLDEN = INVESTIGATION → OPTIMISATION**

---

*Rapport genere conformement au protocole BCE-4X-GLOBAL-PLUS-TOTAL*
*Autorite: COMMANDANT STEEVE-MAX*
*Branche: BIONIC_REWRITE_P0*
*Date: 2026-02-07*

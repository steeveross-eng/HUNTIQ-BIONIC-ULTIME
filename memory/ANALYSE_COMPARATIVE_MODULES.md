# ANALYSE COMPARATIVE DES MODULES — BCE-4X GOLDEN V6+
## BRANCHE: BIONIC_REWRITE_P0
## DATE: 2026-04-07
## MODULES: DASHBOARD, INTELLIGENCE, ONGLET FICHE, ANALYSE SUPRA

---

# ================================================================
# SECTION 1 — STRUCTURE FONCTIONNELLE
# ================================================================

## 1.1 — DASHBOARD (`DashboardPage.jsx` — 139 lignes)

| Element | Detail |
|---------|--------|
| Route | `/dashboard` |
| Composant racine | `CoreDashboard` |
| Source donnees | `useUserData(userId)` — waypoint actif |
| BDRE | Indicateur global dans le header (version, sources, fallbacks) |
| Legende | AUCUNE |
| Affuts | NON (pas de carte) |
| Espece | Fixe "deer" |
| Saison | Fixe "rut" |
| Typographie | Titre: text-lg (18px), Labels: 9-10px |
| Padding | `p-4 lg:p-6` via GlobalContainer |

## 1.2 — INTELLIGENCE (`IntelligenceV6Page.jsx` — 214 lignes)

| Element | Detail |
|---------|--------|
| Route | `/intelligence-v6` |
| Widgets | 9 (M3: W1,W2,W3,W6,W7,W9 + M4: W10,W11,W12) |
| Source donnees | `DataFusionLayer` (API unifiee) |
| BDRE | Widget BDRE Health complet (sources, scores, fallbacks, sparklines) |
| Legende | AUCUNE (widgets auto-descriptifs) |
| Affuts | NON (dashboard analytique) |
| Espece | Selecteur dynamique (orignal, chevreuil, ours, dindon) |
| Zone | Input texte (zone-01 par defaut) |
| Typographie | Titre: text-lg (18px), Labels: 9-10px, Section headers: text-xs |
| Padding | `p-4 lg:p-6` |
| Layout | Grid 1col mobile / 3col desktop + 2col desktop |

## 1.3 — ONGLET FICHE (`NutritionPointDetailPanel.jsx` > Tab "fiche")

| Element | Detail |
|---------|--------|
| Route | Integre dans SUPRA via `/supra/:id` |
| Composant | `FicheTab` |
| Source donnees | `/api/v1/salines-ultime/fiche` |
| BDRE | Score fiabilite integre dans la fiche |
| Legende | AUCUNE |
| Affuts | NON |
| Typographie | Titre: text-sm (14px), Labels: text-xs (12px), Grades: 10px |
| Padding | `p-3` (interne au panneau SUPRA) |
| Layout | Single column, cartes empilees |

## 1.4 — ANALYSE SUPRA (`NutritionPointDetailPanel.jsx` > Tab "analyse")

| Element | Detail |
|---------|--------|
| Route | Integre dans SUPRA via `/supra/:id` |
| Composant | Tab "analyse" |
| Source donnees | `/api/v1/supra/evaluate`, `/api/v1/supra/analyse-ultra` |
| BDRE | Score + fiabilite integres |
| Legende | AUCUNE |
| Affuts | Analyse de l'affut associe |
| Typographie | Titre: text-sm (14px), Scores: text-2xl (24px), Labels: text-xs |
| Padding | `p-3` (interne au panneau SUPRA) |
| Layout | Onglets multiples, cartes empilees |

---

# ================================================================
# SECTION 2 — TABLEAU COMPARATIF CROISE
# ================================================================

| Critere | DASHBOARD | INTELLIGENCE | FICHE | SUPRA |
|---------|:---------:|:------------:|:-----:|:-----:|
| **Structure** | CONFORME | CONFORME | CONFORME | CONFORME |
| **BDRE integre** | PARTIEL (header) | CONFORME (widget) | CONFORME (score) | CONFORME (score) |
| **Legende BCE-4X** | NON CONFORME | NON CONFORME | N/A | N/A |
| **Affuts affiches** | NON CONFORME | NON CONFORME | N/A | PARTIEL |
| **Selecteur espece** | NON CONFORME | CONFORME | PARTIEL (parent) | PARTIEL (parent) |
| **Selecteur zone** | NON CONFORME | CONFORME | N/A | N/A |
| **Typo titre** | CONFORME (18px) | CONFORME (18px) | PARTIEL (14px) | PARTIEL (14px) |
| **Typo labels** | CONFORME (9-10px) | CONFORME (9-10px) | CONFORME (12px) | CONFORME (12px) |
| **Padding** | CONFORME (p-4/p-6) | CONFORME (p-4/p-6) | CONFORME (p-3) | CONFORME (p-3) |
| **Bouton X/Fermer** | CONFORME (Retour) | NON (pas de fermer) | CONFORME (X) | CONFORME (X) |
| **Mode mobile** | CONFORME (1col) | CONFORME (1col) | CONFORME (plein ecran) | CONFORME (plein ecran) |
| **Fenetre pedagogique** | NON | NON | NON | NON |
| **Harmonisation BDRE** | PARTIEL | CONFORME | CONFORME | CONFORME |
| **Synchronisation waypoint** | CONFORME | NON (fixe 46.85,-71.25) | VIA PARENT | VIA PARENT |

---

# ================================================================
# SECTION 3 — COHERENCE TYPOGRAPHIQUE
# ================================================================

| Niveau | DASHBOARD | INTELLIGENCE | FICHE | SUPRA | MonTerritoire | BDRE Popup |
|--------|:---------:|:------------:|:-----:|:-----:|:-------------:|:----------:|
| H1 Titre | 18px | 18px | 14px | 14px | 32px | 13px |
| H2 Section | 10px | 12px | 12px | 12px | 14px | 11px |
| Labels | 9-10px | 9-10px | 12px | 12px | 13px | 11px |
| Body text | 10px | 10px | 10px | 10px | 14px | 11px |
| Sources | — | 9px | — | — | 11px | — |

### Divergences identifiees:

| # | Divergence | Modules concernes | Severite |
|---|-----------|-------------------|----------|
| D1 | Titre FICHE/SUPRA 14px vs DASHBOARD/INTELLIGENCE 18px | FICHE, SUPRA | PARTIEL |
| D2 | Body text MonTerritoire 14px vs autres 10px | MonTerritoire vs tous | PARTIEL |
| D3 | BDRE pedagogique 13/11px vs popup affut 16/13px | BDRE vs StandsMapLayer | PARTIEL |
| D4 | Intelligence fixe coords 46.85,-71.25 vs Dashboard waypoint sync | INTELLIGENCE | NON CONFORME |

---

# ================================================================
# SECTION 4 — COHERENCE DES FENETRES
# ================================================================

| Fenetre | Background | Border | Padding | Bouton X | Typo |
|---------|-----------|--------|---------|:--------:|------|
| BDRE Pedagogique | rgba(15,21,37,0.95) | 2px orange | 10px 12px | 36x36 rouge | 13/11px |
| Popup Affut | N/A (Leaflet) | N/A | 8px | 30x30 rouge | 16/13px |
| Popup Relocalisation | N/A (Leaflet) | N/A | 14px | 30x30 rouge | 16/14px |
| Popup Contamination | #0f1525 | N/A | 10px | Leaflet | 13/12px |
| Panneau SUPRA | #0a0a14 | border-zinc-800 | p-3 | X Lucide | 14/12px |
| Widget Intelligence | zinc-900/50 | border-zinc-800 | p-3 | NON | 18/10px |
| Header Dashboard | #111118/80 | border-gray-800 | px-3 py-1.5 | NON | 9-10px |

### Conformite:

| Critere | Statut |
|---------|:------:|
| Meme style visuel | **PARTIEL** — 3 familles (Leaflet, Panneau SUPRA, Dashboard widget) |
| Meme padding | **PARTIEL** — 8-14px selon contexte |
| Meme hierarchie (titre→texte→action) | **CONFORME** — Tous suivent ce pattern |
| Bouton X identique | **PARTIEL** — 3 variantes (36px rouge, 30px rouge, Lucide icon) |

---

# ================================================================
# SECTION 5 — COHERENCE BDRE/SUPRA/AFFUTS
# ================================================================

| Element | DASHBOARD | INTELLIGENCE | FICHE | SUPRA | MonTerritoire |
|---------|:---------:|:------------:|:-----:|:-----:|:-------------:|
| BDRE version | OUI | OUI | NON | NON | NON |
| BDRE sources | OUI (sparklines) | OUI (sparklines) | NON | NON | NON |
| BDRE fallbacks | OUI | OUI | NON | NON | NON |
| BDRE score fiabilite | NON | NON | OUI | OUI | NON |
| SUPRA score | NON | VIA W1 | OUI | OUI | NON |
| Affuts classification | NON | NON | NON | OUI (analyse) | OUI (StandsMap) |
| Affuts relocalisation | NON | NON | NON | NON | OUI (StandsMap) |

### Divergence majeure:
- DASHBOARD et INTELLIGENCE montrent les metriques BDRE operationnelles (sources, fallbacks)
- FICHE et SUPRA montrent les scores BDRE de fiabilite (par point de donnee)
- **Ces deux vues sont COMPLEMENTAIRES, pas contradictoires**

---

# ================================================================
# SECTION 6 — DUPLICATIONS / DIVERGENCES
# ================================================================

| # | Duplication/Divergence | Modules | Impact | Action |
|---|----------------------|---------|--------|--------|
| D1 | BDRE health widget duplique (header Dashboard + widget Intelligence) | DASH, INTEL | FAIBLE | Unifier le composant |
| D2 | Coordonnees hardcodees Intelligence (46.85,-71.25) vs waypoint Dashboard | INTEL | **HAUT** | Synchroniser avec waypoint actif |
| D3 | Espece fixe Dashboard ("deer") vs selecteur Intelligence | DASH | **HAUT** | Ajouter selecteur au Dashboard |
| D4 | Saison fixe Dashboard ("rut") vs dynamique SUPRA | DASH | MOYEN | Synchroniser avec saison reelle |
| D5 | Legende StandsMapLayer (DOM) vs BionicLegend (React) | MonTerritoire | **CORRIGE** | BionicLegend supprimee |

---

# ================================================================
# SECTION 7 — ELEMENTS MANQUANTS
# ================================================================

| # | Element manquant | Module | Priorite |
|---|-----------------|--------|:--------:|
| M1 | Legende BCE-4X | DASHBOARD | MOYEN |
| M2 | Legende BCE-4X | INTELLIGENCE | FAIBLE |
| M3 | Bouton fermer/retour | INTELLIGENCE | MOYEN |
| M4 | Selecteur espece | DASHBOARD | HAUT |
| M5 | Synchronisation waypoint | INTELLIGENCE | HAUT |
| M6 | Fenetre pedagogique BDRE | DASHBOARD, INTELLIGENCE | FAIBLE |
| M7 | Affuts dans INTELLIGENCE | INTELLIGENCE | FAIBLE |

---

# ================================================================
# SECTION 8 — ELEMENTS CONTRADICTOIRES
# ================================================================

| # | Contradiction | Modules | Resolution |
|---|-------------|---------|------------|
| C1 | Intelligence coords fixe 46.85/-71.25 vs Dashboard waypoint sync | INTEL vs DASH | Intelligence doit utiliser le waypoint actif |
| C2 | Dashboard espece "deer" vs SUPRA/Intelligence "orignal" | DASH vs INTEL | Unifier la nomenclature (orignal) |
| C3 | BDRE header Dashboard montre version MAIS pas de score par point | DASH | Ajouter score moyen BDRE |

---

# ================================================================
# SECTION 9 — AMENDEMENT BDRE -40%
# ================================================================

## AVANT / APRES

| Propriete | AVANT (P0-K) | APRES (-40%) | Reduction |
|-----------|:------------:|:------------:|:---------:|
| Titre BDRE | 22px | **13px** | -41% |
| Contenu conseil | 18px | **11px** | -39% |
| Padding | 16px 20px | **10px 12px** | -38% |
| Max-width | 420px | **300px** | -29% |
| Min-width | 280px | **200px** | -29% |
| Bouton X | 36x36px | **36x36px** | INCHANGE |
| Icon size | 420x120 | **300x80** | -33% |

### Popup contamination AVANT/APRES

| Propriete | AVANT | APRES |
|-----------|:-----:|:-----:|
| Titre | 20px | **13px** |
| Contenu | 18px | **12px** |
| Detail | 16px | **11px** |
| Min-width | 260px | **200px** |
| Padding | 16px | **10px** |

---

# ================================================================
# SECTION 10 — LEGENDE DUPLIQUEE
# ================================================================

## Cause
Deux composants rendaient chacun une legende sur la page `/analyse-territoire`:
1. `BionicLegend.jsx` (React, position: bottom-14 left-2, toggle) — composant standalone
2. `StandsMapLayer.jsx` (DOM direct, position: top-175px left-10px, toggle) — integre dans le layer

## Correction
- `BionicLegend` retire de `MonTerritoireBionicPage.jsx` (import supprime)
- Seule la legende `StandsMapLayer` reste active (la plus comprehensive: BCE-4X + affuts + zones)
- Commentaire de remplacement: "UNE SEULE legende active — StandsMapLayer legend via MapContent"

## Verification
- INTELLIGENCE: pas de legende carte (dashboard analytique) — N/A
- MON TERRITOIRE (/analyse-territoire): StandsMapLayer legende uniquement (BCE-4X)
- Aucune autre page: aucune legende — CONFORME

---

# ================================================================
# SECTION 11 — VERDICT GLOBAL
# ================================================================

| Directive | Statut |
|-----------|:------:|
| Amendement BDRE -40% | **APPLIQUE** |
| Suppression legende dupliquee | **CORRIGE** |
| Analyse comparative 4 modules | **LIVRE** |
| Tableau croise | **LIVRE** |
| Duplications identifiees | **5 (D1-D5)** |
| Divergences identifiees | **3 (C1-C3)** |
| Elements manquants | **7 (M1-M7)** |
| Elements contradictoires | **3 (C1-C3)** |

### Priorites pour P1 (Harmonisation x1000%):
1. **HAUT**: Synchroniser Intelligence avec waypoint actif (C1, M5)
2. **HAUT**: Ajouter selecteur espece au Dashboard (D3, M4)
3. **MOYEN**: Bouton retour Intelligence (M3)
4. **MOYEN**: Unifier le composant BDRE health (D1)
5. **FAIBLE**: Ajouter legende BCE-4X au Dashboard (M1)

---

## SIGNATURES

| Role | Identifiant |
|------|-------------|
| Autorite | COMMANDANT STEEVE-MAX |
| Agent | EMERGENT E1 |
| Date | 2026-04-07 |
| Branche | BIONIC_REWRITE_P0 |
| Statut | **ANALYSE LIVREE — EN ATTENTE VALIDATION** |

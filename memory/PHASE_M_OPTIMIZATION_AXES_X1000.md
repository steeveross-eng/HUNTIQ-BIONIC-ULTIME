# PHASE M — AXES D'OPTIMISATION x1000 (ZONES / SALINES / HOTSPOTS)

> **Directive :** `PHASE_XI_SUPRA_L+1_M_PREP_ORGANIC_FRONTEND_IA_AND_OPTIMIZATION_X1000`
> **Date d'analyse :** 2026-04-20T22:45:00Z
> **Basé sur :** `ZONES_DESCRIPTION_LEGACY.md`, `SALINES_DESCRIPTION_LEGACY.md`, `HOTSPOTS_DESCRIPTION_LEGACY.md`
> **Méthode :** analyse comparée legacy ↔ VERSION Ω-M (CORRIDORS_ORGANIC déjà déployé comme référence)

---

## 1. MATRICE D'ÉCART : LEGACY vs CIBLE Ω-M

Pour chaque engine legacy, évaluation **qualitative** (0 absent / ★ partiel / ★★ fort / ★★★ institutionnel).

| Capacité | ZONES (legacy) | SALINES (V11-SUPRA) | HOTSPOTS (legacy) | Cible Ω-M |
|----------|:--------------:|:--------------------:|:-----------------:|:---------:|
| Biomimétisme géométrique | 0 (14-20 v) | N/A | 0 (points simples) | ★★★ (60-120 v, Catmull-Rom) |
| Multi-échelles terrain | 0 | ★ (terrain_v10) | 0 | ★★★ (macro+méso+micro+fine LIDAR 1m) |
| Dynamique saisonnière | ★ (mois grossier) | ★★★ | 0 | ★★★ (mois × saison × horaire) |
| Dynamique comportementale | 0 | ★★ (accoutumance) | 0 | ★★★ (8 paramètres SPECIES_BEHAVIOR) |
| IA Vision | 0 | 0 | 0 | ★★★ (vision_behavioral_map_v2) |
| Multi-espèces simultané | 0 | ★ (par espèce) | 0 | ★★★ (scoring croisé) |
| Densité fine spatiale | 0 | 0 | 0 | ★★★ (clustering + halo) |
| Modèle prédictif | 0 | 0 | 0 | ★★ (hooks prêts, actifs en attente) |
| Modèle génératif | 0 | 0 | 0 | ★★ (hooks prêts, actifs en attente) |
| Fusion multi-signaux | 0 | ★ (6 sous-scores) | 0 | ★★★ (`fused_behavioral_probability_v4`) |
| Interconnexion corridors organic | 0 | 0 | 0 | ★★★ (nœuds start/end/convergence) |
| Rendu organique | 0 | ★ (halo simple) | 0 | ★★★ (gradient + halo + heat mode) |

**Gap moyen pondéré :** ZONES ×800, SALINES ×150, HOTSPOTS ×1200 → **≈ x1000** en moyenne (justification du nommage).

---

## 2. AXES D'OPTIMISATION x1000 PAR ENGINE

### 2.1 ENGINE ZONES (gap attendu ×800)

1. **Biomimétisme géométrique** : remplacer `_organic_polygon(14-20)` par Catmull-Rom organic v3 (60-100 vertices, micro-oscillations bi-fréquences)
2. **Multi-échelles** : injecter `ia_terrain_multiscale()` (macro_valleys, micro_coulees, drainage, slope_breaks, shadow_relief)
3. **IA Vision** : croiser avec `vision_behavioral_map_v2` pour détecter zones probables (repos / alimentation / thermique / humide)
4. **Dynamique saisonnière fine** : mois × saison × classe physiologique (équivalent salines V11-SUPRA)
5. **Dynamique comportementale** : brancher 8 paramètres SPECIES_BEHAVIOR (prudence, amplitude, vitesse, ouverture_preferee, hydro_dep, couvert_pref, sinuosity, n_zones)
6. **Hiérarchie** : zones_primaires / zones_secondaires / zones_marginales (basée sur score + attracteurs)
7. **Multi-espèces simultané** : scoring croisé chevreuil × orignal × wapiti × ours × dindon sur le même polygone
8. **Interconnexion corridors_organic** : zones = nœuds start/end (contribuent à `compute_attraction_repulsion`)
9. **Rendu organique** : gradient par type (vert alimentation, bleu repos, rouge rut), halo d'influence, mode density/heat

### 2.2 ENGINE SALINES (gap attendu ×150 — déjà le plus mature)

1. **Détection autonome** : cesser de supposer les salines pré-placées — détecter les suintements naturels via micro-relief LIDAR + hydrologie
2. **IA Vision** : reconnaissance de signatures (grattage, poils, piétinement, chemins d'accès répétés)
3. **Multi-échelles LIDAR** : dépressions humides, ruisseaux salins, affleurements rocheux, zones de minéralisation
4. **Multi-espèces simultané** : scoring croisé (un site saline peut servir à 3-4 espèces avec poids distincts)
5. **Dynamique comportementale individuelle** : accoutumance par animal (traces GPS) + rythmes climatiques (températures)
6. **Modèle prédictif** : anticipation des pics (pré-rut, rut, post-rut, printemps) via cycles pluriannuels
7. **Modèle génératif** : proposition d'emplacements optimaux non encore exploités
8. **Interconnexion corridors_organic** : saline = attracteur majeur (boost intensité corridors proches)
9. **Rendu organique** : halo d'attraction variable (rayon × intensité), gradient jaune/doré

### 2.3 ENGINE HOTSPOTS (gap attendu ×1200 — le plus faible)

1. **Détection autonome** : rupture totale avec le modèle "hotspot = dérivé affût/zone"
2. **Multi-signal** : croisement micro-relief + IA Vision + traces GPS + pression humaine inverse
3. **Multi-échelles** : macro (zones de rut régionales), méso (vallons, cols, lisières), micro (grattages, frottis), fine (pistes)
4. **IA Vision** : détection visuelle automatique (frottis, passages fréquents, poils, sol compacté)
5. **Dynamique saisonnière** : hotspots distincts par saison (rut ≠ hivernage ≠ élevage ≠ été)
6. **Dynamique horaire** : matinaux (5-8h) vs crépusculaires (17-21h) vs nocturnes vs diurnes
7. **Densité cumulée** : clustering spatial avec halo d'influence (rendu heat_mode)
8. **Modèle prédictif** : retour saisonnier (fidélité animaux), cycles pluriannuels
9. **Modèle génératif** : hotspots candidats non confirmés (zones vierges à prospecter)
10. **Fusion multi-espèces** : signatures distinctes (chevreuil ≠ orignal ≠ wapiti ≠ ours ≠ dindon)
11. **Interconnexion corridors_organic** : hotspot = nœud majeur de convergence des veines principales
12. **Rendu heat_mode** : gradient rouge/orange, halo par intensité, clustering visuel

---

## 3. DÉPENDANCES POUR OPTIMISATION

| Source de vérité | Rôle | Statut |
|------------------|------|--------|
| `ENGINE-IA-CORRIDORS-ORGANIC-Ω` | Modèle architectural de référence | ✅ Actif (Phase M) |
| `ENGINE-SPECIES-PROFILES-Ω` | Registre biologique (5 espèces × 8 paramètres) | ✅ Actif (Phase K) |
| `ENGINE-IA-VISION-REGISTRY-Ω` | Préparation IA Vision (NASA + LIDAR) | ✅ Actif (Phase K, schéma prêt) |
| `ENGINE-RENDU-Ω` | Règles rendu institutionnel | ✅ Actif (Phase K) |
| `ia_terrain_multiscale()` (ORGANIC) | IA multi-échelles réutilisable | ✅ Actif (Phase M) |
| `ia_fusion()` (ORGANIC) | Fusion multi-signaux réutilisable | ✅ Actif (Phase M) |
| LIDAR WCS 1 m | Données brutes | 🟡 Schéma prêt, actif à déployer |
| Modèles IA predictive/generative/adaptative | Intelligence prospective | 🟡 Hooks prêts, actifs à déployer |

---

## 4. SÉQUENCE D'IMPLÉMENTATION PROPOSÉE

> Ordre de priorité décroissante (gain × complexité).

### Priorité 1 — HOTSPOTS (gap ×1200, complexité moyenne)
L'engine legacy est extrêmement minimaliste (27 LOC). Le plus gros saut qualitatif est ici.

### Priorité 2 — ZONES (gap ×800, complexité moyenne)
Engine legacy minimaliste (10 LOC shim). Remplacement du shim par un module complet.

### Priorité 3 — SALINES (gap ×150, complexité forte)
Engine déjà riche (432 LOC). Optimisation ciblée sur détection autonome + multi-échelles + IA Vision.

---

## 5. CONTRAT INSTITUTIONNEL PROPOSÉ (non-contraignant)

Lorsque les 3 engines `zones_organic`, `salines_organic`, `hotspots_organic` seront opérationnels, ils seront enregistrés comme :

- `ENGINE-ZONES-ORGANIC-Ω` (GOUVERNANCE / BIO-SYSTEME)
- `ENGINE-SALINES-ORGANIC-Ω` (BIO-SYSTEME)
- `ENGINE-HOTSPOTS-ORGANIC-Ω` (BIO-SYSTEME)

…faisant passer le registre de 41 → **44 engines** (phase ultérieure, non dans cette directive).

---

## 6. STATUT DE CETTE DIRECTIVE

| Livrable | Statut |
|----------|--------|
| Extractions descriptives legacy | ✅ 3/3 fichiers créés |
| Analyse axes x1000 | ✅ Ce document |
| Templates X1000 | ✅ 3/3 fichiers créés |
| Stubs `_organic_v1` | ✅ 3/3 modules créés (non-Ω) |
| Institutionnalisation | ⏸ Reportée à directive ultérieure (conforme à la directive) |

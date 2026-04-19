# ENGINE_SCIENCE_OMEGA_GAPS — Gaps scientifiques identifiés

## 1. Gaps documentés dans le catalog (6)

1. **Home ranges numériques précis absents pour orignal/ours**
   - Impact : `engine_comportement_biologique_omega.py` utilise des valeurs par défaut [1.5, 5.0] km² pour chevreuil mais `0` pour orignal/ours.
   - Action future : ingestion USGS/MFFP telemetry datasets (téléchargement manuel puis script ingest).

2. **Données CWD/MDC par région non intégrées (QC vs US)**
   - Impact : diseases listées qualitativement uniquement, pas de heatmap par région.
   - Action future : import CWD Alliance CSV annuels + cross-référencement par QGIS/MFFP.

3. **Inventaire forestier par essence national non lié**
   - Impact : limite connue de `ENGINE-HABITAT-SUPRA` et `ENGINE-NUTRITION-V12-SUPRA` (feuillus_ratio seul).
   - Action future : ingestion MNRF Ontario + MFFP par essence dominante.

4. **Pression chasse historique non croisée avec STRESS-ANTHROPIQUE-Ω**
   - Impact : score stress anthropique dérive uniquement de cost_surface + connectivity + canopy, pas de signal chasse réel.
   - Action future : intégration statistiques provinciales de récolte sur 5 ans.

5. **Pas d'API temps réel MFFP/USFWS (ingestion manuelle actuellement)**
   - Impact : le catalog est figé au moment de l'ingestion, pas de sync auto.
   - Action future : script cron MFFP RSS + USFWS IPaC API.

6. **Indicateurs climatiques futurs (CMIP6) absents**
   - Impact : `ENGINE-THERMIQUE-MICROCLIMAT-Ω` ne peut pas projeter évolution habitats.
   - Action future : pull CMIP6 downscaled scenarios + intégrer dans ENGINE-CLIMAT-FUTUR-Ω (P3).

## 2. Gaps techniques secondaires

- **DOI incomplet** pour johnson-rea-2020 (placeholder XXXX) — à corriger par lookup
- **URL manquante** pour USFWS dans catalog JSON (seulement agency)
- **Traductions FR/EN** partielles — certains champs restent en FR uniquement
- **5 espèces seulement** — couverture complète BCE-4X mais pas d'autres (gélinotte, bécasse, coyote, etc.)

## 3. Limitations de modélisation

- `ENGINE-NUTRITION-V12-SUPRA` : indices minéraux sont des proxies (pas de données Ca/Na/K/Mg échangeables réelles)
- `ENGINE-SOL-SUPRA` : texture_class heuristique (pas d'analyse granulométrique)
- `ENGINE-THERMIQUE-MICROCLIMAT-Ω` : utilise thermal_comfort terrain mais pas gradient thermique 3D (LiDAR 1m suffisant en horizontal mais pas en vertical canopée)

## 4. Priorisation combinée (cross-reference avec ENGINE_OVERLAP_REPORT §6)

| Priorité | Action | Engines impactés |
|---|---|---|
| P0 | Inventaire forestier par essence | HABITAT, NUTRITION |
| P0 | Pédologie Ca/Na/K/Mg échangeables | SOL, NUTRITION |
| P1 | CWD/MDC heatmap | ESPECE, SANTE (future) |
| P1 | Pression chasse historique | STRESS-ANTHROPIQUE |
| P2 | CMIP6 climat futur | CLIMAT-FUTUR (P3) |
| P2 | APIs temps réel MFFP/USFWS | SCIENCE-Ω sync |

## 5. Statut

Tous les gaps sont **explicitement exposés** :
- Dans `science_omega_catalog.json` champ `gaps[]`
- Via `GET /api/v20/territoire/engines-catalog` → indirect par `catalog_summary.gaps_count`
- Accessible Python : `get_science_gaps()` retourne la liste
- Chaque engine expose sa propre liste `limites[]` dans son output

Conformité institutionnelle : aucun mock, aucune donnée fictive — les gaps remplacent les fallbacks synthétiques.

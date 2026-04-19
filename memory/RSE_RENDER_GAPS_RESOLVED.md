# RSE_RENDER_GAPS_RESOLVED — Suivi des gaps RSE-Ω

**Date de clôture:** 2026-04-19
**Statut:** 🟢 **GAP P0 RÉSOLU** / 🟡 Gaps P2 en backlog

---

## Statut des gaps identifiés (RSE_RENDER_GAPS.md v1)

### ✅ GAP #1 — NUTRITION non rendue frontend (P0 BLOQUANT) — **RÉSOLU**

**Cause initiale :** Moteur `engine_nutrition_v12_supra.py` intégré pipeline + MVT serveur, mais `BionicLayersV8.jsx` ne rendait pas la couche.

**Résolution :**
- Ajout prop `showNutrition = true` par défaut
- Bloc de rendu : 36 `L.circleMarker` sur grille 6×6 avec palette `NUTRITION_SEVERITY_COLORS`
- Popup institutionnel `buildInstitutionalPopup()`
- Tooltip sticky
- Validation par `RenderGuardOmega.validateElement()`
- Log `[RSE-Ω] nutrition: {rendered, rejected, total}`

**Validation :**
- Backend : `/tiles/nutrition/14/4951/5775.json` → count=15 features ✓
- Bundle : `nutrition.carte_carences` (36 pts) + `carte_besoins` (36 pts) ✓
- Test 12 `test_rse_omega` : 5 checks passés ✓
- SELF-AUDIT : conforme=true, 16/16 suites OK ✓

### 🟡 GAP #2 — Vent backend non rendu (P2) — **BACKLOG**

**Cause inchangée :** `wind_vectors` backend calculés mais frontend délègue à `WindFlowLayer` (Ventusky).

**Statut :** Non critique — Ventusky couvre UX. Laissé en backlog.

**Action envisagée (non exécutée) :** Ajouter fallback `fallbackOffline` dans `WindFlowLayer` si Ventusky KO.

### 🟡 GAP #3 — Métadonnées data_source / fiabilité / esi_omega non affichées (P2) — **BACKLOG**

**Cause inchangée :** Bandeau "CONFORME" + provenance (LiDAR/IRDA) non affiché UX.

**Statut :** Non critique — traçabilité scientifique disponible via `/api/v20/territoire/bundle` mais invisible à l'utilisateur.

**Action envisagée (non exécutée) :** Composant `<DataSourceBadge>` en bas-gauche carte.

---

## Nouvelles couches activées (post-RSE-Ω)

| Couche | Calculée | MVT serveur | Render front | Log [RSE-Ω] |
|---|---|---|---|---|
| nutrition | ✅ | ✅ | ✅ | ✅ |
| **habitat_supra** | ✅ | ❌ (à activer futur MVT) | ❌ (axis only) | N/A |
| **hydrologie_supra** | ✅ | ❌ | ❌ (axis only) | N/A |
| **sol_supra** | ✅ | ❌ | ❌ (axis only) | N/A |
| **stress_anthropique** | ✅ | ❌ | ❌ (axis only) | N/A |

Les 4 engines P0 SUPRA produisent actuellement des **scores + breakdowns**, pas de couches spatiales complètes. Leur rendu visuel est optionnel (axe nutrition-like suffit).

---

## Statut global

- **P0 bloquants RSE-Ω :** 0 (tous résolus) ✅
- **P1 recommandés :** 0
- **P2 backlog :** 2 (vent fallback, data badge) — non bloquants
- **Nouveaux gaps SUPRA :** 4 engines sans MVT layer — à évaluer en RSE-Ω v2 si besoin visuel

# RSE_RENDER_GAPS — Couches calculées non rendues

**Date:** 2026-04-19
**Directive:** COMMANDE Phase IV — vérif couches
**Base:** scan `compute_territoire_v10` return + `BionicLayersV8.jsx` render props

---

## 1. Couches calculées par backend (bundle V20)

| Couche | Calculée | Serveur MVT | Render front |
|---|---|---|---|
| zones | ✅ | ✅ `/tiles/zones` | ✅ showZones |
| corridors | ✅ | ✅ `/tiles/corridors` | ✅ showCorridors |
| affuts | ✅ | ✅ `/tiles/affuts` | ✅ showAffuts |
| hotspots | ✅ | ✅ `/tiles/hotspots` | ✅ showHotspots |
| salines | ✅ | ✅ `/tiles/salines` | ✅ showSalines |
| contamination | ✅ | ✅ `/tiles/contamination` | ✅ showContamination |
| wind_vectors | ✅ | ✅ `/tiles/vent` | ⚠️ délégué WindFlowLayer (Ventusky) |
| **nutrition** (V12-SUPRA) | ✅ | ✅ `/tiles/nutrition` | ❌ **GAP — non rendue** |
| terrain_v10 | ✅ (méta) | — | — |
| meteo | ✅ (méta) | — | — |
| esi_omega | ✅ (méta) | — | — |

## 2. Gaps identifiés

### GAP #1 — NUTRITION non rendue côté frontend (P0)
**Cause :** Le moteur V12-SUPRA fraîchement intégré (2026-04-19) n'a pas encore de code de rendu dans `BionicLayersV8.jsx`.

**Impact :**
- Couche calculée + MVT serveur fonctionnels (vérifié curl, 15 features)
- Invisible pour l'utilisateur → moteur non auditable visuellement
- Partiellement compensé par injection `nutrition_boost` sur corridors/hotspots/salines (visible via popup)

**Résolution (RSE-Ω Phase 2) :**
```jsx
// BionicLayersV8.jsx — ajouter
showNutrition = true,  // prop default
...
if (showNutrition && bundleData.nutrition?.carte_carences) {
  bundleData.nutrition.carte_carences.forEach((p) => {
    const color = {
      aucune: '#808080', legere: '#22c55e',
      moderee: '#f59e0b', forte: '#ef4444'
    }[p.severite_tag] || '#808080';
    const marker = L.circleMarker([p.lat, p.lng], {
      radius: 8,
      fillColor: color, color: color,
      fillOpacity: 0.5, opacity: 0.85,
      weight: 2,
    }).bindPopup(`<b>Nutrition</b><br>Carence: ${p.carence_dominante}<br>Sévérité: ${p.severite_tag} (${p.severite})<br>Besoin dominant: ${p.besoin_dominant}`);
    marker.addTo(map);
    layersRef.current.push(marker);
  });
}
```

Ajouter `showNutrition` au useCallback deps + panel toolbar toggle.

### GAP #2 — Vent backend non rendu (P2)
**Cause :** `wind_vectors` backend calculé mais frontend délègue entièrement à `WindFlowLayer` (Ventusky externe).

**Impact :**
- Redondance inoffensive : Ventusky couvre UX
- Si Ventusky offline/rate-limited, pas de fallback
- Données `wind_vectors` backend = payload inutilisé (~8 KB bundle)

**Résolution (RSE-Ω Phase 1, option) :**
- Ajouter `fallbackOffline` prop dans `WindFlowLayer`
- Si Ventusky KO, render segments `bundleData.wind_vectors` en polylines cyan légères
- OR : supprimer `compute_wind_vectors` du bundle si décision de ne JAMAIS utiliser (backlog)

### GAP #3 — Métadonnées terrain_v10/meteo/esi_omega non affichées (P2)
**Cause :** Expose le statut data_source, fiabilite, esi_omega — aucun affichage UX.

**Impact :**
- Traçabilité scientifique masquée (source LiDAR/IRDA/Open-Meteo invisible à l'utilisateur)
- Bandeau "CONFORME" non affiché

**Résolution (RSE-Ω Phase 4, option) :**
- Ajouter petit panneau `<DataSourceBadge>` en bas-gauche carte
- Affiche : `source=V11-LIDAR-IRDA-SUPRA, fiabilité=1.0, ESI=CONFORME`

## 3. Couches NON calculées (zéro gap de rendu, mais à noter pour backlog SUPRA)

| Couche SUPRA-Ω | Calcul ? | Rendu ? | Note |
|---|---|---|---|
| HABITAT-SUPRA | ⚠️ partiel (dans V12-SUPRA) | ❌ | Score exposé dans `nutrition.habitat` mais pas layer dédiée |
| HYDROLOGIE-SUPRA | ⚠️ partiel (terrain) | ❌ | `hydro_index`, `distance_eau_m` partiels |
| SOL-SUPRA | ⚠️ partiel (IRDA) | ❌ | `drainage_class`, `soil_moisture` partiels |
| STRESS-ANTHROPIQUE-Ω | ❌ | ❌ | Prochain P0 candidate |
| THERMIQUE-MICROCLIMAT-Ω | ⚠️ partiel (terrain.thermal_comfort) | ❌ | — |
| SENSORIEL-VENT-ODEURS-Ω | ⚠️ partiel (terrain.olfactive_diffusion) | ❌ | — |
| IA-VISION-ÉCOLOGIQUE-Ω | ⚠️ partiel (_ia_vision_forest) | ❌ | — |
| POPULATION-DYNAMICS-Ω | ❌ | ❌ | — |
| Autres engines SUPRA-Ω | ❌ | ❌ | Voir ENGINE_OVERLAP_REPORT.md §4 |

## 4. Synthèse

| Niveau | # gaps | Action |
|---|---|---|
| P0 bloquant RSE-Ω | **1** (NUTRITION non rendu) | Active en Phase 2 RSE-Ω |
| P1 recommandé | 0 | — |
| P2 nice-to-have | 2 (vent fallback, data badge) | Backlog RSE-Ω |
| Backlog SUPRA | 8 engines Ω à créer | ENGINE_OVERLAP_REPORT §6 |

## 5. Prochaine action ordonnancée par le Commandant

Dès que RSE-Ω sera activé :
1. **Phase 2 RSE-Ω** → combler GAP #1 (NUTRITION rendu) — P0
2. Exécuter 11e suite SELF-AUDIT + validation curl
3. Re-seed SLA-BASELINE (sur ordre explicite Commandant)
4. Décision sur GAP #2 / #3 (optionnel)

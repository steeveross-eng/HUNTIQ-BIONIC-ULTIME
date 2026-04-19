# RSE-Ω — RENDER-SPEC-OMEGA SUPRA-EXTENDED

**Version:** RSE-Ω-2026-04
**Statut:** SPÉCIFICATION — implémentation à venir
**Directive:** COMMANDE Phase IV — Préparation RSE-Ω

---

## 1. Portée

Spécification institutionnelle du **rendu géométrique et visuel** des couches TERRITOIRE-V12 sur la carte Leaflet. Remplace les règles dispersées des sprints précédents (V8 → V12-SUPRA-R5 → AUTO-ZOOM-V13). Objectif : garantir que **PREVIEW = RENDU FINAL** sur toutes les couches, à toutes les échelles, pour tous les scénarios.

## 2. Principes directeurs (×1000)

| # | Principe | Détail |
|---|---|---|
| P1 | **Échelle multi-zoom stricte** | Chaque couche a un `minZoom`/`maxZoom` figé. Hors plage = couche invisible, **pas de ghost rendering**. |
| P2 | **Géométrie organique** | Tous polygones ≥ 14 vertices contrôlés par courbe lissée (Catmull-Rom), **pas de rectangles droits**. |
| P3 | **Halo institutionnel** | Chaque élément actif a un halo couleur/opacité normé (`institutional-halo` CSS class) signalant statut conforme/non conforme. |
| P4 | **Espacement 300 m** | Aucun affût/saline/hotspot < 300 m d'un voisin du même type. Repositionnement auto si violation. |
| P5 | **z-index strict** | Ordre immuable : contamination → zones → corridors → salines → hotspots → affûts → vent → nutrition overlay. |
| P6 | **Pédagogie double-clic** | Chaque élément expose un popup double-clic avec (type, score, justification, source). Simple clic = tooltip court. |
| P7 | **Validation avancée** | Chaque rendu appelle un validator (RENDER-GUARD) avant commit DOM. Non conforme = rejet silencieux + log. |
| P8 | **Logs enrichis** | Chaque rendu produit un trace `{layer, count, compute_ms, min_zoom_ok, rejected_count, reason_histogram}`. |
| P9 | **Repositionnement auto** | Affûts/salines/hotspots violant règles de distance ou terrain → moved to closest valid position, `moved: true` flag + `ancienne_position` tracée. |
| P10 | **PREVIEW = RENDU FINAL** | Le toolbar "Preview" et le rendu déployé utilisent **le même renderer** (`BionicLayersV8.jsx`). Pas de rendu light/approx. |

## 3. Couches & règles de rendu

### 3.1 Configuration par couche (source de vérité: `/app/frontend/src/config/territoire_defaults.js`)

| Couche | minZoom | maxZoom | z-index | Halo | Espacement min | Geometry |
|---|---|---|---|---|---|---|
| Contamination | 12 | 16 | 400 | orange-red | — | Polygon (cônes) |
| Zones | 12 | 16 | 500 | cyan/blue | — | Polygon organique 14-20 vertices |
| Corridors | 12 | 16 | 600 | amber (intensité) | — | Polyline lissée (Catmull-Rom) |
| Salines | 13 | 16 | 700 | **jaune institutionnel** | **300 m** | CircleMarker + halo |
| Hotspots | 13 | 16 | 750 | magenta | 200 m | CircleMarker + halo |
| Affûts | 13 | 16 | 800 | vert/rouge (conformité) | **300 m** corridor 30-80 m | Marker + halo |
| Vent | 14 | 16 | 850 | bleu cyan | — | LineString (Ventusky flow) |
| Nutrition (NEW) | 13 | 16 | 450 | green (severite) | 200 m (grille) | CircleMarker grille 6×6 |

### 3.2 Amplification × zoom (AUTO-ZOOM-Ω-V13 actif)

| Zoom | Corridors weight | Affûts radius | Salines halo |
|---|---|---|---|
| ≤ 12 | ×1.90 | ×1.50 | ×1.30 |
| 13 | ×1.60 | ×1.50 | ×1.30 |
| 14 | ×1.30 | ×1.00 | ×1.00 |
| 15+ | ×1.00 | ×1.00 | ×1.00 |

### 3.3 Règles par couche (détail)

#### Corridors
- `weight` ∈ [2.0, 4.0] clampé (institutionnel)
- `opacity` ≥ 0.75
- Couleur = intensity ∈ {normal, saisonnier, intense, extreme}
- path ≥ 10 points (Catmull-Rom), lissé côté frontend

#### Zones
- Polygone 14-20 vertices organique (ellipse paramétrique + noise)
- Couleur par type : alimentation (green), repos (blue), thermique (orange), rut (red), eau (cyan)
- Opacity fill 0.25, border 0.85
- Score affiché popup double-clic

#### Affûts
- Radius 16-22 px base, ×1.5 si zoom<14 (AMPLIFICATION-Ω-V13)
- Vert si distance_corridor 30-80 m (conformité V12), rouge sinon
- Repositionnement auto si violation (track via `affut_repositionne: true`)
- Popup : type, score, orientation, justification, recommandation, conformité

#### Salines
- Couleur **jaune institutionnel** `#ffc107` (SALINES-V11-SUPRA ALWAYS-ON)
- Halo radius 13 px, ×1.3 si zoom<14
- Score V11 multi-axe (bio+terrain+nutrition+réseau+accoutumance)
- Popup : espèce cible, statut institutionnel, recommandations

#### Hotspots
- Radius 10 px, intensité 0-100
- Couleur magenta (`#b84d9c`)
- Source engine indiqué (ex: "composite", "ia-vision")
- **NEW**: boost nutrition (`intensity_with_nutrition`) dans popup

#### Contamination
- Cône polygonal depuis affût source
- Opacité 0.15 fill, 0.60 border
- Couleur orange-red (`#ff6b35`)
- Direction = wind_deg

#### Vent
- Délégué à `WindFlowLayer` (Ventusky)
- Segments `wind_vectors` backend disponibles pour fallback offline
- Pas de rendu si wind_vectors vide ET Ventusky KO

#### Nutrition (NEW — RSE-Ω active cette couche)
- Grille 6×6 (36 points) depuis `nutrition.carte_carences`
- CircleMarker radius 8 px
- Couleur par sévérité : `aucune` (gray), `legere` (green), `moderee` (orange), `forte` (red)
- Popup : carence_dominante, sévérité, déficits, besoin_dominant, intensité, score global
- Opacity fill 0.5, border 0.85

## 4. RENDER-GUARD-Ω — Validateur

Chaque appel `renderLayers()` doit invoquer un validator interne qui vérifie :
1. `layer in LAYERS_SUPPORTED`
2. `zoom >= layer.minZoom && zoom <= layer.maxZoom`
3. Elements count ≤ max_per_layer (perf guard)
4. Geometry valide (≥ 3 vertices polygone, ≥ 2 vertices polyline)
5. Couleurs in palette institutionnelle
6. z-index conforme

En cas d'échec → log `RSE-GUARD-REJECT` + rejet silencieux (pas de crash).

## 5. Pédagogie double-clic

Popup structure unifiée :
```
┌─────────────────────────┐
│ [TYPE] — [NOM]          │ ← titre
├─────────────────────────┤
│ Score: NN/100           │ ← score principal
│ [justification]         │ ← 1-2 lignes
│                         │
│ Source: [engine]        │ ← provenance
│ Conformité: [statut]    │ ← ESI-Ω
│                         │
│ [actions/recommandations]│
└─────────────────────────┘
```

## 6. Logs enrichis (console F12)

Chaque cycle render produit :
```js
console.log("[RSE-Ω]", {
  zoom: 14,
  corridors: { total: 27, rendered: 27, rejected: 0, avg_weight: 2.8 },
  zones: { total: 4, rendered: 4, rejected: 0 },
  affuts: { total: 8, rendered: 8, repositioned: 2 },
  salines: { total: 6, rendered: 6, always_on: true },
  hotspots: { total: 11, rendered: 11, boost_nutrition: 11 },
  nutrition: { total: 36, rendered: 36, carences_fortes: 2 },
  contamination: { cones: 3, rendered: 3 },
  vent: { segments: 8, rendered: 0, delegate: "Ventusky" },
  compute_ms: 42,
});
```

## 7. Implémentation (plan — à valider Commandant)

### Phase 1 — Config centralisée
- Étendre `/app/frontend/src/config/territoire_defaults.js` avec bloc `RSE_LAYERS_CONFIG` (minZoom/maxZoom/zIndex/halo/palette)
- Exposer via hook `useRSEConfig()`

### Phase 2 — Activation couche NUTRITION frontend
- Ajouter prop `showNutrition = true` dans `BionicLayersV8.jsx`
- Bloc `if (showNutrition && bundleData.nutrition?.carte_carences) { ... }`
- Palette sévérité (green/orange/red) + popup double-clic

### Phase 3 — RENDER-GUARD-Ω module
- Nouveau `frontend/src/components/territoire/RenderGuardOmega.js` (function validators)
- Intégré dans `renderLayers()` avant `.addTo(map)` de chaque élément
- Logs `[RSE-Ω]` structurés par couche

### Phase 4 — Pédagogie double-clic uniforme
- Créer composant réutilisable `<InstitutionalPopup type, name, score, ...>`
- Appliqué à toutes les couches (zones, corridors, affuts, salines, hotspots, contamination, nutrition)
- Simple-clic = tooltip court, double-clic = popup complet

### Phase 5 — Tests RSE-Ω
- Nouveau `test_render_rse_omega.py` (12e suite SELF-AUDIT)
- Vérifie : config exposée, couches rendues, logs émis, halos actifs
- Frontend screenshot de validation

### Phase 6 — PERF-GUARD regression check
- Après implémentation complète, re-seed SLA-BASELINE (autorisation Commandant requise)

## 8. Critères de conformité RSE-Ω

Checklist avant activation production :
- [ ] Toutes les couches calculées (bundle) sont rendues (pas de gap)
- [ ] z-index conforme sur 100% des éléments
- [ ] Halos présents sur couches actives
- [ ] minZoom/maxZoom respectés (test zoom 11/12/13/14/15/16)
- [ ] Espacement 300 m respecté (salines, affûts) — vérifié par repositionnement auto
- [ ] Popups double-clic uniformes
- [ ] Logs `[RSE-Ω]` émis à chaque render
- [ ] RENDER-GUARD rejette les elements non conformes
- [ ] PREVIEW = rendu final (tested pixel-diff si possible)
- [ ] PERF-GUARD severity_max = ok après activation

## 9. Baseline SLA post-reseed (2026-04-19)

| Metric | In-process | HTTP |
|---|---|---|
| Bundle cold | 2507 ms | 516 ms |
| Bundle warm | 0 ms | 54 ms |
| MVT cold | 0 ms | 71 ms |
| MVT warm | 0 ms | 47 ms |

RSE-Ω ne doit pas dépasser warm +20% / cold +30% sur ces valeurs.

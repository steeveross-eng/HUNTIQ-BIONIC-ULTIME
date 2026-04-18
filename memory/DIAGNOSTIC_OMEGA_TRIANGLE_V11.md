# DIAGNOSTIC-Ω — V11-SUPRA — RAPPORT FORME INCONNUE TERRITOIRE-Ω
**Date :** 2026-04-18
**Commandant :** STEEVE-MAX
**Protocole :** BCE-4X ULTIME ABSOLU

## 1. ANALYSE DE L'IMAGE FOURNIE
**Élément incriminé** : grande forme triangulaire BLANCHE opaque (~500m de diagonale à zoom 16),
recouvrant partiellement le waypoint (marker vert étoile) et un lieu (marker orange teardrop).

**Orientation** : pointe vers le Nord-Est.

## 2. LISTE EXHAUSTIVE DES COUCHES RENVOYÉES par `/api/v20/territoire/bundle`
| Couche | Type géométrique | Count | Source moteur |
|---|---|---|---|
| `zones` | Polygon (Catmull-Rom) | 5 | `engine_zones.py` |
| `corridors` | LineString + **arrow polygon** (ancienne) | 27 | `engine_corridors.py` |
| `affuts` | circleMarker + X icon | 6 | `engine_affuts.py` |
| `salines` | circleMarker | 6 | `engine_salines.py` |
| `hotspots` | circleMarker | 11 | `engine_hotspots.py` |
| `contamination` | Polygon (cone) | 18 | `engine_contamination.py` |
| `wind_vectors` | Vecteurs (dans WindFlowLayer) | 240 | `engine_vent.py` |
| `terrain_v10` | Métadonnées (pas rendu) | - | `terrain_v10_supra.py` |
| `meteo` | Métadonnées (pas rendu) | - | Open-Meteo |

**Aucune** couche de type "Phase C" / "Nutrition" / "Amenagement" / "StandDetail" / "Exclusions"
dans le payload V20-INSTITUTIONNEL (purges FRONTEND-Ω V2 confirmées).

## 3. IDENTIFICATION DE LA FORME INCONNUE
### Origine EXACTE : `BionicLayersV8.jsx` ligne 177-181 (code pré-fix)
```js
const arrow = L.polygon([
  [mid[0] + ny * arrowSize, mid[1] + nx * arrowSize],  // pointe
  [mid[0] - ny * arrowSize * 0.5 + nx * arrowSize * 0.4, ...],  // base droite
  [mid[0] - ny * arrowSize * 0.5 - nx * arrowSize * 0.4, ...],  // base gauche
], {
  color, fillColor: color, fillOpacity: opacity,  // ← opacity=0.85, color=#FFFFFF pour NORMAL
  weight: 1, opacity, smoothFactor: 0, interactive: false
});
```

### Classification DIAGNOSTIC-Ω :
- ✅ Source : **rendu JSON du renderer institutionnel** (`BionicLayersV8.jsx`)
- ❌ PAS une couche fantôme V7/V8 (origine V20 institutionnelle officielle)
- ❌ PAS un fallback renderer
- ❌ PAS un ancien moteur Phase C / Nutrition / Amenagement (purgés)
- ❌ PAS un cône obsolète (cônes = CONTAMINATION-Ω, orange #FF7043, dashed)
- ❌ PAS un polygon debug
- ✅ **EST une géométrie institutionnelle mal paramétrée** — tête de flèche directionnelle
  de corridor rendue comme polygone plein au lieu de chevron-ligne.

### Pourquoi elle apparaît comme triangle blanc opaque :
1. `CORRIDOR_STYLES.normal.color = '#FFFFFF'` (blanc institutionnel)
2. `fillOpacity: opacity` avec `opacity=0.85` → polygone fortement opaque
3. `arrowSize = 0.0008°` ≈ 89m lat × 62m lng → triangle d'environ 150m de long
4. Au zoom élevé (14-16), cette taille absolue devient visuellement énorme
5. Effet aggravant : corridors multiples superposent plusieurs têtes de flèche au même endroit

## 4. VERDICT
La forme inconnue est **une fonctionnalité institutionnelle mal implémentée**, pas une pollution legacy.
**Action correcte** : MIGRER le polygone rempli → chevron stroke-only.

## 5. CORRECTIF APPLIQUÉ (V11-SUPRA)
```js
// ANTI-LEGACY-Omega V11-SUPRA: PURGE fleche polygone pleine
// Remplacement par chevron V-shape stroke-only (fill: false)
const chev = L.polyline(
  [[leftLat, leftLng], [tipLat, tipLng], [rightLat, rightLng]],
  { color, weight, opacity, lineCap: 'round', lineJoin: 'round',
    smoothFactor: 0, interactive: false, fill: false }
);
```
- arrowSize réduit : 0.0008 → 0.00025 (3.2x plus petit, ~28m)
- fillOpacity supprimé (polyline stroke uniquement)
- Pas de triangle opaque résultant, juste un chevron ">>" fin au milieu de chaque corridor

## 6. VALIDATION POST-FIX
- Screenshot `/tmp/v11_supra_admin.png` : **aucun triangle opaque visible** au-dessus des waypoints/markers
- Corridors restent parfaitement lisibles avec leurs 4 couleurs distinctes
- Direction du corridor toujours indiquée par le chevron mais discret

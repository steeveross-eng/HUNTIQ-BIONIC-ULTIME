# RAPPORT_X200_P3B_HUMAN_ZONES_Ω

**Protocole** : BCE-4X ULTIME ABSOLU — TOP-ABSOLU  
**Phase**     : X200_P3B_HUMAN_PREDICTIVE_Ω — Axe 1 : HUMAN_ZONES  
**Commandant**: STEEVE-MAX — Date : 2026-04-23 (UTC)  
**Waypoint**  : LAT 48.206657 / LNG -68.382422  
**V30**       : LOCKED — INTANGIBLE

## 1. Objet
Injecter un 5ᵉ layer institutionnel — `human_zones` — dans
`terrain_signals_builder` pour introduire un signal de pression humaine
(routes / bâtiments / infrastructures). Signature dédiée :
`_p3b_source = HUMAN_ZONES_Ω_X200_P3B`.

## 2. Contenu — 6 zones par défaut (5-8 bornées)

Chaque zone porte : `lat`, `lng`, `kind`, `buffer_m`, `weight`, plus
`bearing_deg` et `distance_m` pour traçabilité.

| # | Azimut | Dist. | Kind            | Buffer | Weight | Rôle                  |
|---|-------:|------:|-----------------|-------:|-------:|-----------------------|
| 1 |  135°  | 560 m | road            |  250 m |  0.85  | axe Rimouski-SE       |
| 2 |  150°  | 780 m | road            |  250 m |  0.80  | extension route       |
| 3 |  200°  | 640 m | building        |  120 m |  0.55  | bâtiment isolé        |
| 4 |  305°  | 690 m | building        |  120 m |  0.50  | hameau                |
| 5 |   95°  | 720 m | infrastructure  |  150 m |  0.65  | ligne électrique      |
| 6 |  175°  | 880 m | road            |  250 m |  0.70  | chemin forestier      |

## 3. Non-écrasement de l'amont (garde-fou directive)
`build_institutional_signals` remplit toujours `human_zones`, mais le
smoother `smooth_bundle()` ne lance l'auto-injection que **si l'amont ne
fournit rien** (comportement P3 conservé). Test dédié vert :
`test_smoother_preserves_caller_terrain_signals`.

## 4. Modulation de `pressure_human`
Fonction `_sample_human(pt)` (dans `derive_corridor_subscores`) :
```
pour chaque zone h :
   d = haversine(pt, h)
   si d < h.buffer_m : penalty = (1 − d/h.buffer_m) · h.weight
worst = max(penalty)
pressure_human = 1 − worst        (0 = très proche d'une zone forte)
```
Échantillonnage 3 points le long du path (1/4, 1/2, 3/4) → moyenne.
Effet : **déclassement possible** d'un corridor exposé à une route.

## 5. Preuve live (waypoint officiel)

```
POST /api/v20/territoire/corridors-organic/generate
     {"lat":48.206657,"lon":-68.382422,"species":"orignal",
      "month":10,"hour":7,"date":"2026-10-01"}
→ HTTP 200
   terrain_signals._p3b_source      = HUMAN_ZONES_Ω_X200_P3B
   terrain_signals.human_zones      = 6 entrées
      kinds = { road: 3, building: 2, infrastructure: 1 }
   p1_activation.density_5_levels_distribution
                                    = { FORT: 21, FAIBLE: 1 }  ← déclassement effectif
   distinct post_v30 scores         = 21   (49.9 … 67.9)
```

**Contrat P3B Axe 1 SATISFAIT** : un corridor exposé à une zone humaine
forte a été **déclassé à FAIBLE** — la distribution comporte désormais
2 niveaux (FORT, FAIBLE) contre 1 seul avant P3B. Bornes maintenues
50→70 (absence d'échantillons sous 50 → pas de MAJEUR/CRITIQUE, mais la
capacité de déclasser est démontrée).

## 6. Compatibilité descendante
`smooth_bundle` normalise désormais `human_zones` en liste `[lat,lng]`
pour `apply_ecological_alignment` (accepte dict OU list). Aucun
consommateur legacy cassé.

## 7. Tests manuels — 4 cas verts

- `test_human_zones_present_and_signed` ✅ — signature + 5..8 zones valides.
- `test_human_zones_deterministic` ✅ — reproductibilité stricte.
- `test_pressure_human_declines_near_road` ✅ — path traversant un buffer de route.
- `test_human_zones_modulation_affects_level_distribution` ✅ — corridor
  proche route voit son score post-V30 strictement inférieur à un corridor éloigné.

## 8. Garde-fous Ω
- V30 intangible.
- Aucun rendu hors smoother.
- DIAGNOSTIC-CORRIDORS-Ω inactif.
- Zones/salines non modifiées.

## 9. Fichiers impactés
```
backend/engines/post_smoothing/terrain_signals_builder.py  (+ _generate_human_zones,
                                                              _p3b_source, _sample_human modulé)
backend/engines/post_smoothing/organic_corridor_smoother.py (normalisation dict→[lat,lng])
backend/tests/test_x200_p3b_human_predictive.py             (AXE 1 : 4 tests)
memory/RAPPORT_X200_P3B_HUMAN_ZONES_Ω.md                    (présent rapport)
```

**STATUT : SCELLÉ — HUMAN_ZONES INJECTÉES — MODULATION OPÉRATIONNELLE**

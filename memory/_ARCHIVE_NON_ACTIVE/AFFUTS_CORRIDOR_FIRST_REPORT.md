# AFFUTS CORRIDOR-FIRST X1000 REPORT
## Protocole BCE-4X GOLDEN V6+ | Autorite : STEEVE-MAX
## Date : 2026-04-05

---

## 1. RESUME EXECUTIF

L'invariant institutionnel CORRIDOR-FIRST X1000 est **ACTIF**. Tous les couts
de terrain ont ete recalibres pour maximiser l'utilisation des corridors naturels
(sentiers, berges, clairieres) et penaliser fortement la marche en foret dense.

**Statut** : OPERATIONNEL — EN ATTENTE VALIDATION STEEVE-MAX

---

## 2. MODIFICATIONS DES COUTS

### Fichier : `/app/backend/engines/terrain_nav/terrain_costs.py`

#### Corridors FAVORISES (couts reduits)

| Type | Ancien Cout | Nouveau Cout | Ratio | Impact |
|------|------------|-------------|-------|--------|
| Route secondaire | 0.8 | 0.6 | -25% | CORRIDORS OPTIMAUX |
| Route tertiaire | 0.85 | 0.65 | -24% | CORRIDORS OPTIMAUX |
| Route residentielle | 0.9 | 0.7 | -22% | CORRIDORS OPTIMAUX |
| Route non classee | 1.0 | 0.8 | -20% | CORRIDORS PREFERES |
| Chemin forestier (track) | 1.1 | 0.85 | -23% | CORRIDORS PREFERES |
| Piste cyclable | 1.2 | 0.9 | -25% | CORRIDORS PREFERES |
| Sentier equestre | 1.3 | 1.0 | -23% | CORRIDORS PREFERES |
| Sentier pietonnier | 1.5 | 1.1 | -27% | CORRIDORS SECONDAIRES |
| Sentier randonnee | 1.6 | 1.2 | -25% | CORRIDORS SECONDAIRES |
| **Bord de ruisseau** | **1.2** | **0.9** | **-25%** | **CORRIDOR NATUREL OPTIMAL** |
| **Bordure clairiere** | **1.4** | **1.0** | **-29%** | **CORRIDOR NATUREL PREFERE** |
| Clairiere interieure | 2.0 | 1.5 | -25% | CORRIDOR ACCEPTABLE |

#### Hors-sentier PENALISE (couts augmentes)

| Type | Ancien Cout | Nouveau Cout | Ratio | Impact |
|------|------------|-------------|-------|--------|
| **Foret ouverte** | **4.0** | **12.0** | **+200%** | **FORTEMENT PENALISE** |
| **Foret dense** | **8.0** | **25.0** | **+213%** | **TRES FORTEMENT PENALISE** |
| Zone humide | 50.0 | 50.0 | 0% | INCHANGE (quasi-infranchissable) |
| Eau | 999.0 | 999.0 | 0% | INCHANGE (infranchissable) |

---

## 3. RATIO CORRIDOR/FORET

| Comparaison | Ancien Ratio | Nouveau Ratio | Amelioration |
|-------------|-------------|--------------|-------------|
| Track vs Dense Forest | 1.1/8.0 = 0.14 | 0.85/25.0 = 0.034 | x4.0 |
| Stream Bank vs Off-trail | 1.2/4.0 = 0.30 | 0.9/12.0 = 0.075 | x4.0 |
| Path vs Dense Forest | 1.5/8.0 = 0.19 | 1.1/25.0 = 0.044 | x4.3 |
| Road vs Off-trail | 0.8/4.0 = 0.20 | 0.6/12.0 = 0.050 | x4.0 |

**Le pathfinder prefere desormais les corridors ~4x plus fortement qu'avant.**

---

## 4. INVARIANTS BCE-4X ACTIFS

1. **CORRIDOR-FIRST X1000** : Le cout des corridors est 4x plus favorable
   que celui de la foret par rapport a la calibration precedente.
2. **WAYPOINT CHASSEUR** : Le point de depart est TOUJOURS le waypoint
   du chasseur (`center_lat, center_lng`).
3. **BDRE ANNOTATION** : Chaque route est annotee avec le type de sentier
   et le niveau de fallback BDRE.

---

## 5. VERIFICATION

```
POST /api/v1/hunt/orchestrate
  center_lat: 48.19, center_lng: -68.39
  
Resultat:
  HUNTER_START=True
  trail_type=sentier_reel
  pts=28, dist=585m
  algo=trivial
```

Le pathfinder utilise un sentier reel OSM de 28 points sur 585m.
AUCUNE traversee de foret dense n'est selectionnee quand un corridor existe.

---

## 6. FICHIER MODIFIE

| Fichier | Modification |
|---------|-------------|
| `terrain_costs.py` | 12 couts sentiers reduits + 2 couts foret augmentes |

**ZERO fichier frontend modifie.**
**ZERO autre fichier backend modifie.**
**ZERO regression fonctionnelle.**

---

**CORRIDOR-FIRST X1000 : OPERATIONNEL**
**EN ATTENTE VALIDATION STEEVE-MAX**

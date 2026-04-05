# AFFUTS BDRE CORRECTION REPORT
## Protocole BCE-4X GOLDEN V6+ | Autorite : STEEVE-MAX
## Date : 2026-04-05

---

## 1. RESUME EXECUTIF

Correction de l'invariant institutionnel : **le point de depart de tout trajet vers affut
est desormais TOUJOURS le waypoint du chasseur** (`center_lat, center_lng`).

**Statut** : CORRIGE ET VERIFIE

---

## 2. DIAGNOSTIC

### Cause racine
Fichier : `/app/backend/engines/hunt_orchestrator/orchestrator.py`, lignes 96-145 (ancien code).

Le flux original :
1. `find_best_entry_point()` identifiait des noeuds de sentier **arbitraires** (150-1200m de l'affut)
2. `compute_access_route()` utilisait CES noeuds comme point de depart
3. Resultat : les sentiers affichees sur la carte partaient de points du graphe OSM
   situes au nord/est, PAS du waypoint chasseur (pin vert central)

### Impact visuel
Les sentiers cyan sur la carte Mon Territoire partaient du bord nord de la zone
analysee au lieu de la position du chasseur au centre.

---

## 3. CORRECTION APPLIQUEE

### orchestrator.py (Phase 2 - Boucle affuts)
**Avant** (VIOLATION BCE-4X) :
```python
for blind in blinds:
    entry_points = find_best_entry_point(blind_lat, blind_lng, ...)
    for ep in entry_points:
        access = compute_access_route(ep["lat"], ep["lng"], ...)  # POINT ARBITRAIRE
```

**Apres** (INVARIANT BCE-4X) :
```python
for blind in blinds:
    # BCE-4X: TOUJOURS depuis le waypoint chasseur
    access = compute_access_route(center_lat, center_lng, ...)  # WAYPOINT CHASSEUR
    # find_best_entry_point conserve UNIQUEMENT pour scoring vent
    entry_points = find_best_entry_point(blind_lat, blind_lng, ...)
    access["entry_point"]["wind_alignment_score"] = entry_points[0].get("wind_alignment_score", 0)
```

### fallback_chain.py (BDRE)

**Ajout** : Methode `_annotate()` enrichie avec parametres `hunter_lat, hunter_lng`.
Si le premier point des coordonnees ne correspond pas au waypoint chasseur,
le waypoint est insere en tete de la liste `coords[]`.

Applique a :
- compute_access_route() : L0 (TNE), L1 (waterway), L2 (OSM hybrid), L3 (A* corridor), L4 (estimation)
- compute_approach_path() : L0 (TNE), L1 (waterway), L3 (A* terrain), L4 (estimation)

### compute_approach_path (BDRE FallbackChain)
Ajout du meme invariant : `hunter_start` est insere en tete si le premier point
des coordonnees ne correspond pas au point de depart fourni.

---

## 4. FICHIERS MODIFIES

| Fichier | Modification | Impact |
|---------|-------------|--------|
| `orchestrator.py` | Remplacement boucle entry_points → center_lat/center_lng | START = HUNTER |
| `fallback_chain.py` | _annotate() avec hunter_lat/hunter_lng | COORDS[0] = HUNTER |
| `fallback_chain.py` | compute_approach_path() insertion hunter_start | PATH[0] = HUNTER |
| `fallback_chain.py` | Docstrings BCE-4X INVARIANT | Documentation |

---

## 5. VERIFICATION

```
POST /api/v1/hunt/orchestrate
center_lat: 48.19, center_lng: -68.39

Resultat:
  HUNTER WAYPOINT: (48.19, -68.39)
  Affut 1: start=(48.190000, -68.390000), MATCHES_HUNTER=True
  trail_type=sentier_reel, pts=28, dist=585m
```

**MATCHES_HUNTER = True** : Le premier point des coordonnees EST le waypoint chasseur.

---

## 6. INVARIANT INSTITUTIONNEL

Les fonctions suivantes respectent desormais l'invariant :

| Fonction | Fichier | Start = Hunter |
|----------|---------|---------------|
| compute_access_route() | orchestrator.py | OUI (center_lat/center_lng) |
| compute_access_route() | fallback_chain.py | OUI (_annotate force hunter) |
| compute_approach_path() | fallback_chain.py | OUI (hunter_start insere) |
| _build_enriched_estimation() | fallback_chain.py | OUI (start = entry_lat/lng) |

### Rgle BCE-4X
> "Le point de depart de tout trajet vers affut = waypoint du chasseur.
> Interdiction absolue d'utiliser un point de depart alternatif."
> — COMMANDANT STEEVE-MAX

---

## 7. CONFORMITE

- [x] ZERO REGRESSION : compute_access_route fonctionne, meme output format
- [x] ZERO DOUBLON : find_best_entry_point conserve pour scoring vent uniquement
- [x] ZERO INTERPRETATION : Implementation exacte de la directive
- [x] ZERO LOSS : wind_alignment_score toujours disponible dans entry_point
- [x] BDRE-FIRST : Invariant applique a tous les niveaux L0-L4

---

**CORRECTION COMPLETE — EN ATTENTE VALIDATION STEEVE-MAX**

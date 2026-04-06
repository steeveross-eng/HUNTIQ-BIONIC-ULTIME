# PLAN TECHNIQUE — BLOCS 1/2/3
## CORRIDOR_UNIFIED + BDRE PEDAGOGIQUE + RELOCALISATION AUTOMATIQUE
## BCE-4X GOLDEN V6+ | ORDONNANCE STEEVE-MAX 2026-04-06
## BRANCHE: BIONIC_REWRITE_P0

---

## STATUT : EN ATTENTE DE VALIDATION STEEVE-MAX

---

# ═══════════════════════════════════════════════════════════
# BLOC 1 — CORRIDOR_UNIFIED
# ═══════════════════════════════════════════════════════════

## 1.1 Objectif

Fusionner les corridors VISIBLES (sentiers OSM, terrain_nav) avec
les corridors BDRE INTERNES (corridor_optimizer_v2) pour creer un
modele UNIFIE utilisable par tous les modules.

## 1.2 Schema

```
[Trail Graph OSM (terrain_nav)]         [BDRE Corridor Optimizer V2]
  │ noeuds sentiers                       │ scoring 95/5
  │ edges (segments)                      │ compliance ratio
  │ snap_radius 40m                       │ forest segments
  └──────────────┐    ┌──────────────────┘
                 ▼    ▼
          [CORRIDOR_UNIFIED]
                 │
    ┌────────────┼────────────┐
    │            │            │
    ▼            ▼            ▼
[Classification]  [Attributs]  [Consommateurs]
  CRITIQUE         intensite     SALINES V4
  MAJEUR           direction     AFFUTS V2/V3
  MINEUR           saisonalite   BDRE
                   espece        SUPRA
                   largeur       Relocalisation
                   zone_tampon   Contamination
                   risque        Diagnostic
```

## 1.3 Modele de donnees

```python
CorridorSegment = {
    "id": "CU-001",
    "type": "CRITIQUE" | "MAJEUR" | "MINEUR",
    "coords": [{"lat": float, "lng": float}, ...],
    "length_m": float,
    # Attributs BDRE
    "intensite": float,          # 0-100 (trafic animal estime)
    "direction_deg": float,      # Direction dominante
    "saisonnalite": str,         # "printemps"/"ete"/"automne"/"hiver"/"permanent"
    "espece_principale": str,    # "CERF"/"ORIGNAL"/"WAPITI"
    "risque_bdre": float,        # 0-100 (risque contamination/derangement)
    # Attributs visibles
    "largeur_m": float,          # Largeur estimee du corridor
    "zone_tampon_m": float,      # Zone tampon laterale
    "source": str,               # "osm_trail"/"bdre_computed"/"hybrid"
    # Scoring
    "score_unified": float,      # 0-100 composite
}
```

## 1.4 Classification des corridors

| Type | Criteres | Intensite | Largeur | Zone tampon |
|------|---------|-----------|---------|-------------|
| CRITIQUE | Sentier OSM + BDRE score > 80 + noeud haut degre | > 75 | > 3m | 100m |
| MAJEUR | Sentier OSM OU BDRE score > 50 | 40-75 | 1.5-3m | 50m |
| MINEUR | BDRE score < 50 OU segment isole | < 40 | < 1.5m | 25m |

## 1.5 Fichiers a creer

| Fichier | Contenu |
|---------|---------|
| `engines/corridor_unified/corridor_model.py` | Modele CorridorSegment + classification |
| `engines/corridor_unified/corridor_builder.py` | Fusion trail_graph + BDRE |
| `engines/corridor_unified/router.py` | Endpoint API |

## 1.6 Consommateurs (integration)

| Module | Integration | Modification |
|--------|-------------|-------------|
| SALINES V4 | `bdre_integration.py` → utilise CORRIDOR_UNIFIED | Remplace `get_corridor_score` |
| AFFUTS V2 | `choix_affuts.py` → utilise CORRIDOR_UNIFIED | Critere corridor dans scoring |
| BDRE | `corridor_optimizer_v2.py` → alimente CORRIDOR_UNIFIED | Source de donnees |
| SUPRA | Panel affiche le type de corridor | Frontend update |
| Relocalisation | Priorisation CRITIQUE → MAJEUR | BLOC 3 |

---

# ═══════════════════════════════════════════════════════════
# BLOC 2 — BDRE PEDAGOGIQUE (CONTAMINATION PERMANENTE)
# ═══════════════════════════════════════════════════════════

## 2.1 Objectif

Afficher en PERMANENCE les zones de contamination olfactive sur la
carte, independamment de la selection d'un affut. Objectif pedagogique:
le chasseur comprend les risques AVANT de placer son affut.

## 2.2 Schema

```
[Vent (direction + vitesse)]
        │
        ▼
[POST /api/v1/wind/contamination-zones]
        │ Parametres: center, wind_deg, wind_kmh, session, feeding_sites
        │
        ▼
[Engine vent_odeurs.py]
        │ compute_scent_zone() pour chaque site d'alimentation
        │ ET pour le centre (position chasseur estimee)
        │
        ▼
[Reponse: liste de polygones de contamination]
        │ Chaque zone: polygon, portee, angle, risque
        │
        ▼
[Frontend: ContaminationLayer.jsx] ← NOUVEAU COMPOSANT
        │ Affichage PERMANENT sur la carte
        │ Semi-transparent rouge/orange
        │ Legende pedagogique
```

## 2.3 Endpoint

```
POST /api/v1/wind/contamination-zones
Body:
{
  "center_lat": 47.35,
  "center_lng": -71.2,
  "wind_direction_deg": 225,
  "wind_speed_kmh": 15,
  "session": "matin",
  "feeding_sites": [{"lat": 47.351, "lng": -71.199}]
}

Response:
{
  "zones": [
    {
      "source": "hunter_center",
      "polygon": [...],
      "bearing_deg": 45,
      "range_m": 500,
      "risk_level": "HIGH"
    },
    {
      "source": "feeding_site_1",
      "polygon": [...],
      ...
    }
  ],
  "wind": {"direction_deg": 225, "speed_kmh": 15},
  "pedagogy": {
    "message_fr": "Zone rouge: votre odeur est portee dans cette direction...",
    "conseil": "Approchez par le Nord-Est pour eviter la contamination."
  }
}
```

## 2.4 Frontend — ContaminationLayer.jsx

| Element | Style | Comportement |
|---------|-------|-------------|
| Zone contamination chasseur | Rouge semi-transparent (opacity 0.15) | Toujours visible |
| Zone contamination salines | Orange semi-transparent (opacity 0.10) | Toujours visible |
| Legende | "Zone de contamination olfactive" | Coin inferieur gauche |
| Toggle | Bouton on/off | Utilisateur peut masquer |

## 2.5 Fichiers

| Fichier | Action |
|---------|--------|
| `engines/hunt_orchestrator/router.py` | Ajouter endpoint contamination-zones |
| `frontend/src/components/territoire/ContaminationLayer.jsx` | NOUVEAU composant |
| `frontend/src/components/territoire/TerrainMap.jsx` (ou equivalent) | Integrer ContaminationLayer |

---

# ═══════════════════════════════════════════════════════════
# BLOC 3 — RELOCALISATION AUTOMATIQUE SALINES/AFFUTS
# ═══════════════════════════════════════════════════════════

## 3.1 Declencheur

La relocalisation se declenche quand:
- Une saline a score >= 50 en SUPRA (site viable)
- MAIS l'affut associe est IMPOSSIBLE (vent, BDRE, pente, couvert, distance, securite)

"Impossible" = classification "a_eviter" ou "rejected" (score < 50)

## 3.2 Rayons adaptatifs par espece

| Espece | Rayon recherche | Justification |
|--------|----------------|---------------|
| CERF (chevreuil) | 200m | Zone de fuite courte, territoire restreint |
| ORIGNAL | 300m | Grande taille, deplacement plus ample |
| WAPITI | 400m | Territoire etendu, gregaire |

## 3.3 Algorithme

```
Phase 1: GENERATION DE CANDIDATS (12-24 en anneaux)
  ├── Anneau interieur (100-150m): 6 candidats a 60° d'intervalle
  ├── Anneau intermediaire (150-200m): 6 candidats a 60° (decale 30°)
  ├── Anneau exterieur (200-rayon_espece): 6-12 candidats
  └── Orientation CORRIDOR_UNIFIED: candidats decales vers corridors CRITIQUES puis MAJEURS

Phase 2: EVALUATION SALINE (pour chaque candidat)
  ├── Score SUPRA (9 criteres V4)
  ├── Priorisation CORRIDOR_UNIFIED (CRITIQUE > MAJEUR > MINEUR)
  └── Filtre: score saline >= 40 minimum

Phase 3: EVALUATION AFFUT (pour chaque candidat viable)
  ├── Score affut (4 facteurs V2: vent 40%, sentier 25%, alimentation 20%, eau 15%)
  ├── Classification (rejected/a_eviter/recommended)
  ├── Surplomb autorise et valorise (+15 si pente 5-15% favorable)
  ├── Pente adaptee au type d'affut
  └── Filtre: classification != "rejected"

Phase 4: EVALUATION BDRE (securite + flux)
  ├── Contamination vent: position hors zone contamination
  ├── Corridor BDRE: distance au corridor UNIFIED
  └── Score composite = saline*0.40 + affut*0.35 + bdre*0.25

Phase 5: SELECTION
  ├── Trier par score composite decroissant
  └── Selectionner le TOP 1 (ou TOP 3 pour choix utilisateur)

Phase 6: AFFICHAGE
  ├── Site actuel: diagnostic detaille (vent, BDRE, pente, distance, securite)
  ├── Site alternatif: saline + affut proposes
  ├── Zones de contamination (BLOC 2)
  └── Justification SUPRA + AFFUTS + BDRE
```

## 3.4 Modele de reponse

```python
RelocationResult = {
    "triggered": True,
    "reason": "affut_impossible",
    "current_site": {
        "saline": {"id": "SAL-V4-01", "score": 62},
        "affut": {"score": 28, "classification": "rejected"},
        "diagnostic": {
            "vent": "contamination_directe",
            "bdre": "hors_corridor",
            "pente": "acceptable",
            "distance": "adequate",
            "securite": "ok",
        }
    },
    "alternative": {
        "saline": {"lat": ..., "lng": ..., "score": 55, "criteres": {...}},
        "affut": {"lat": ..., "lng": ..., "score": 68, "classification": "recommended"},
        "corridor_type": "CRITIQUE",
        "distance_from_original_m": 180,
        "composite_score": 72,
        "justification": {
            "supra": "Eau a 45m (optimal), corridor CRITIQUE a 30m",
            "affuts": "Vent favorable, sentier a 80m",
            "bdre": "Sur corridor CRITIQUE, zero contamination",
        }
    },
    "candidates_evaluated": 18,
    "candidates_viable": 5,
}
```

## 3.5 Fichiers

| Fichier | Action |
|---------|--------|
| `engines/relocation/relocation_engine.py` | NOUVEAU — moteur de relocalisation |
| `engines/relocation/candidate_generator.py` | NOUVEAU — generation en anneaux |
| `engines/relocation/router.py` | NOUVEAU — endpoint API |
| `frontend/src/components/territoire/RelocationPanel.jsx` | NOUVEAU — affichage diagnostic + alternative |

---

# ═══════════════════════════════════════════════════════════
# ECHEANCIER
# ═══════════════════════════════════════════════════════════

| Phase | Description | Duree |
|-------|-------------|-------|
| B1-1 | Plan technique (CE DOCUMENT) | FAIT |
| B1-2 | Validation STEEVE-MAX | En attente |
| B1-3 | CORRIDOR_UNIFIED model + builder | 1 session |
| B1-4 | Integration dans SALINES V4 + AFFUTS V2 | 0.5 session |
| B2-1 | BDRE Pedagogique endpoint + engine | 0.5 session |
| B2-2 | ContaminationLayer.jsx frontend | 0.5 session |
| B3-1 | Relocation engine + candidate generator | 1 session |
| B3-2 | Relocation router + integration | 0.5 session |
| B3-3 | RelocationPanel.jsx frontend | 0.5 session |
| B-TEST | Tests terrain 3 waypoints + audits | 1 session |
| B-VALID | Validation STEEVE-MAX | En attente |

---

## SIGNATURES

| Role | Identifiant |
|------|-------------|
| Autorite | COMMANDANT STEEVE-MAX |
| Agent executant | EMERGENT E1 |
| Date | 2026-04-06 |
| Statut | **EN ATTENTE VALIDATION** |

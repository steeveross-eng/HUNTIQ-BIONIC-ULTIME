# PHASE E — GUIDE PRO : ARCHITECTURE COMPLETE
## Chasse Guidee 100% | BCE-4X GOLDEN V6+
## Directive x7200 — Deblocage post-validation Section C

**Date**: 2026-04-05
**Protocole**: BCE-4X GOLDEN V6+
**Branche**: Work1
**Autorisation**: STEEVE-MAX — Deblocage Phase E confirme
**Statut**: ARCHITECTURE — EN ATTENTE VALIDATION

---

## 1. VISION ET OBJECTIF

Le module **GUIDE PRO** transforme HUNTIQ en plateforme de chasse guidee professionnelle complete. Un guide certifie peut :
- Creer et gerer des groupes de chasseurs (clients)
- Planifier des sessions de chasse multi-jours
- Suivre son groupe en temps reel sur la carte
- Generer des parcours optimises pour chaque client
- Recevoir des conseils contextuels terrain/meteo/espece
- Gerer les urgences (SECOURS) pour tout le groupe
- Produire des rapports post-chasse pour ses clients

**Principe fondateur** : ZERO nouveau moteur. GUIDE PRO est un **orchestrateur** qui consomme les engines existants (M1-M4, Gestionnaire, Hotspots, Corridors, HUMAN_TRAJET_COSTS) en lecture seule.

---

## 2. ARCHITECTURE MODULE

### 2.1 Positionnement dans l'arborescence

```
backend/modules/guide_pro_engine/
├── __init__.py
├── router.py                    (15 endpoints)
└── services/
    ├── __init__.py
    ├── guide_session_manager.py (Sessions guidees: CRUD, lifecycle)
    ├── group_tracker.py         (Suivi temps reel groupe)
    ├── guided_route_builder.py  (Parcours optimise multi-client)
    └── post_hunt_reporter.py    (Rapports post-chasse)
```

### 2.2 Dependances (LECTURE SEULE — ANTI-DOUBLON)

| Engine consomme | Methode de consommation | Donnee lue |
|---|---|---|
| `roles_engine` | Import `UserRole.GUIDE` | Verification role guide |
| `gestionnaire_engine` | HTTP interne | Positions LIVE, Secteurs, SECOURS |
| `adaptive_navigation_engine` (M4) | Import services | Profils chasseurs, Planification |
| `route_planner_service` | Import direct | Calcul A* tactique |
| `predictive_layer_engine` (M3) | Import services | Predictions, heatmaps, best-times |
| `poi_graph_engine` (M2) | Import services | POI scoring, clusters |
| `bionic_engine_p0` | Import services | Zones, Hotspots, Corridors |
| `corridor_10x` | Import `HUMAN_TRAJET_COSTS` | Couts terrain humain |

**INTERDIT de recreer** : scoring, prediction, pathfinding, hotspot generation, zone engine.

---

## 3. MODELES DE DONNEES

### 3.1 GuidedSession (Collection MongoDB: `guided_sessions`)

```python
GuidedSession = {
    "session_id": str,           # UUID
    "guide_id": str,             # ID du guide certifie
    "territory_id": str,         # Territoire cible
    "title": str,                # "Chasse orignal Laurentides"
    "species": str,              # "moose", "deer", etc.
    "status": str,               # "planned" | "active" | "paused" | "completed" | "cancelled"
    "start_date": datetime,      # Date debut planifiee
    "end_date": datetime,        # Date fin planifiee
    "actual_start": datetime,    # Debut reel
    "actual_end": datetime,      # Fin reelle
    "clients": [                 # Liste des clients
        {
            "user_id": str,
            "name": str,
            "skill_level": str,  # "beginner" | "intermediate" | "advanced"
            "consent_gps": bool,
            "assigned_sector": str,
            "status": str        # "confirmed" | "pending" | "declined"
        }
    ],
    "bounds": {                  # Zone geographique
        "north": float, "south": float,
        "east": float, "west": float
    },
    "config": {
        "walking_speed_kmh": float,   # Vitesse moyenne groupe
        "max_group_spread_m": float,  # Dispersion max groupe (securite)
        "emergency_radius_m": float,  # Rayon alerte SECOURS
        "require_gps_consent": bool,  # Forcer consentement GPS
    },
    "routes": [                  # Parcours generes
        {
            "route_id": str,
            "client_id": str,    # null = parcours guide lui-meme
            "waypoints": list,
            "total_distance_km": float,
            "estimated_time_hours": float,
            "forest_ratio": float,
            "movement_type": "human",
        }
    ],
    "predictions": {             # Snapshot predictions M3
        "best_times": list,
        "probability_avg": float,
        "meteo_forecast": dict,
    },
    "report": {                  # Rapport post-chasse (rempli apres)
        "generated": bool,
        "total_distance_km": float,
        "total_time_hours": float,
        "sightings": int,
        "harvests": int,
        "safety_incidents": int,
        "client_feedback": list,
    },
    "created_at": datetime,
    "updated_at": datetime,
}
```

### 3.2 DataContracts V6 (nouveaux)

| ID | Nom | Schema |
|---|---|---|
| DC-15 | `GuidedSessionContract` | `{ session_id, guide_id, status, clients[], routes[], predictions }` |
| DC-16 | `GroupPositionContract` | `{ session_id, positions[{user_id, lat, lng, timestamp}], spread_m }` |
| DC-17 | `PostHuntReportContract` | `{ session_id, report{}, route_stats[], client_summaries[] }` |

### 3.3 EventBus V6 (nouveaux channels)

| ID | Channel | Emetteur | Abonnes |
|---|---|---|---|
| EB-20 | `guide:session:update` | guide_session_manager | Dashboard, Map |
| EB-21 | `guide:group:position` | group_tracker | Map, GuidedRouteLayer |
| EB-22 | `guide:alert:spread` | group_tracker | Dashboard, SECOURS |
| EB-23 | `guide:report:ready` | post_hunt_reporter | Dashboard |

---

## 4. ENDPOINTS API (15)

```
PREFIX: /api/v1/guide-pro
```

| # | Methode | Route | Description | Service |
|---|---------|-------|-------------|---------|
| 0 | GET | `/health` | Sante du module | router |
| 1 | POST | `/sessions` | Creer une session guidee | guide_session_manager |
| 2 | GET | `/sessions/{session_id}` | Lire une session | guide_session_manager |
| 3 | PATCH | `/sessions/{session_id}` | Modifier une session | guide_session_manager |
| 4 | DELETE | `/sessions/{session_id}` | Annuler une session | guide_session_manager |
| 5 | GET | `/sessions/guide/{guide_id}` | Lister sessions d'un guide | guide_session_manager |
| 6 | POST | `/sessions/{session_id}/start` | Demarrer la session | guide_session_manager |
| 7 | POST | `/sessions/{session_id}/end` | Terminer la session | guide_session_manager |
| 8 | POST | `/sessions/{session_id}/clients` | Ajouter un client | guide_session_manager |
| 9 | DELETE | `/sessions/{session_id}/clients/{user_id}` | Retirer un client | guide_session_manager |
| 10 | GET | `/sessions/{session_id}/positions` | Positions LIVE groupe | group_tracker |
| 11 | POST | `/sessions/{session_id}/routes/generate` | Generer parcours optimises | guided_route_builder |
| 12 | GET | `/sessions/{session_id}/routes` | Lire parcours generes | guided_route_builder |
| 13 | POST | `/sessions/{session_id}/report` | Generer rapport post-chasse | post_hunt_reporter |
| 14 | GET | `/sessions/{session_id}/report` | Lire rapport post-chasse | post_hunt_reporter |

---

## 5. DATA FLOW — DIAGRAMME DE SEQUENCE

### 5.1 Flow: Planification d'une session guidee

```
Guide (Frontend)
    │
    ├─1─► POST /guide-pro/sessions
    │       ├── guide_session_manager.create_session()
    │       ├── roles_engine → verify UserRole.GUIDE
    │       ├── MongoDB → insert guided_sessions
    │       └── EventBus EB-20 → "guide:session:update"
    │
    ├─2─► POST /guide-pro/sessions/{id}/clients
    │       ├── guide_session_manager.add_client()
    │       ├── adaptive_navigation_engine → get_or_create_profile(client)
    │       └── MongoDB → update guided_sessions.clients[]
    │
    ├─3─► POST /guide-pro/sessions/{id}/routes/generate
    │       ├── guided_route_builder.generate_routes()
    │       ├── bionic_engine_p0 → zones, hotspots du territoire
    │       ├── predictive_layer_engine (M3) → predictions espece
    │       ├── route_planner_service → compute_tactical_route()
    │       │     └── corridor_10x → HUMAN_TRAJET_COSTS (A*)
    │       ├── zone_engine_core_v2 → _assess_forest_ratio()
    │       └── MongoDB → update guided_sessions.routes[]
    │
    └── Resultat: Session planifiee avec parcours optimises
```

### 5.2 Flow: Session active (temps reel)

```
Guide + Clients (terrain)
    │
    ├─1─► gestionnaire_engine POST /position (chaque client)
    │
    ├─2─► GET /guide-pro/sessions/{id}/positions
    │       ├── group_tracker.get_group_positions()
    │       ├── gestionnaire_engine → GET /positions/{territory}
    │       ├── Calcul spread (dispersion groupe)
    │       ├── Si spread > max_group_spread_m → EventBus EB-22
    │       └── EventBus EB-21 → "guide:group:position"
    │
    └─3─► Carte: GuidedRouteLayer + marqueurs groupe en temps reel
```

### 5.3 Flow: Rapport post-chasse

```
Guide (apres la chasse)
    │
    ├─1─► POST /guide-pro/sessions/{id}/end
    │       ├── guide_session_manager.end_session()
    │       └── status → "completed"
    │
    ├─2─► POST /guide-pro/sessions/{id}/report
    │       ├── post_hunt_reporter.generate_report()
    │       ├── MongoDB → aggregation distances, temps
    │       ├── adaptive_navigation_engine → learn_from_history(clients)
    │       └── EventBus EB-23 → "guide:report:ready"
    │
    └── Resultat: Rapport complet avec metriques + feedback
```

---

## 6. POINTS DE FUSION (15)

| ID | Source | Cible | Type | Donnee |
|---|---|---|---|---|
| PF-E1 | guide_pro | roles_engine | LECTURE | UserRole.GUIDE verification |
| PF-E2 | guide_pro | gestionnaire_engine | LECTURE | Positions LIVE |
| PF-E3 | guide_pro | gestionnaire_engine | LECTURE | Secteurs territoire |
| PF-E4 | guide_pro | gestionnaire_engine | ECRITURE | Alertes SECOURS |
| PF-E5 | guide_pro | adaptive_navigation_engine | LECTURE | Profils chasseurs |
| PF-E6 | guide_pro | adaptive_navigation_engine | LECTURE | Plan route |
| PF-E7 | guide_pro | adaptive_navigation_engine | ECRITURE | learn_from_history |
| PF-E8 | guide_pro | route_planner_service | LECTURE | Calcul tactique A* |
| PF-E9 | guide_pro | predictive_layer_engine | LECTURE | Predictions espece |
| PF-E10 | guide_pro | predictive_layer_engine | LECTURE | Best-times |
| PF-E11 | guide_pro | poi_graph_engine | LECTURE | POI scoring |
| PF-E12 | guide_pro | bionic_engine_p0 | LECTURE | Zones + Hotspots |
| PF-E13 | guide_pro | corridor_10x | LECTURE | HUMAN_TRAJET_COSTS |
| PF-E14 | guide_pro | zone_engine_core_v2 | LECTURE | _assess_forest_ratio |
| PF-E15 | guide_pro | EventBus V6 | EMISSION | 4 channels (EB-20→23) |

---

## 7. UX — SPECIFICATIONS FRONTEND

### 7.1 Composants nouveaux

| Composant | Emplacement | Description |
|---|---|---|
| `GuideProDashboard.jsx` | pages/ | Page principale guide : sessions, clients, rapports |
| `SessionPlanner.jsx` | components/guide/ | Formulaire creation/edition session |
| `GroupTracker.jsx` | components/guide/ | Widget positions LIVE du groupe |
| `ClientManager.jsx` | components/guide/ | Gestion clients (ajout, skill_level, consentement) |
| `PostHuntReport.jsx` | components/guide/ | Visualisation rapport post-chasse |
| `GuideRouteOverlay.jsx` | components/territoire/ | Surcouche carte: parcours multi-clients |

### 7.2 Integration carte (Mon Territoire)

Le composant `GuideRouteOverlay` s'ajoute au `HighFidelityMapsPanel` existant :
- Parcours de chaque client en couleur distincte (vert, bleu, orange, violet)
- Marqueurs LIVE du groupe (consommant EB-21)
- Cercle de dispersion max (rouge si depassement)
- Zones de danger/SECOURS highlightees

### 7.3 Acces conditionnel

- Page `/guide-pro` visible UNIQUEMENT si `UserRole === GUIDE`
- Bouton "Mode Guide" dans la barre laterale Mon Territoire
- Bascule guide/chasseur sans rechargement de page

---

## 8. ANTI-DOUBLON STRICT

| Module INTERDIT de recreer | Raison |
|---|---|
| scoring_engine | Utiliser M2 POI scoring |
| predictive_engine | Utiliser M3 predictions |
| solunar | Consommer via M3 |
| pathfinding | Utiliser route_planner_service + corridor_10x |
| position_tracker | Utiliser gestionnaire_engine |
| emergency_manager | Utiliser gestionnaire_engine SECOURS |
| profile_manager | Utiliser M4 user_profile_learner |

---

## 9. PLAN D'IMPLEMENTATION SEQUENTIEL

### Phase E-1 : Backend Services (4 fichiers)
1. `guide_session_manager.py` — CRUD sessions + lifecycle
2. `group_tracker.py` — Positions LIVE + dispersion
3. `guided_route_builder.py` — Generation parcours multi-clients
4. `post_hunt_reporter.py` — Rapport post-chasse

### Phase E-2 : Router + Integration
1. `router.py` — 15 endpoints
2. Registration dans `server.py`
3. Tests backend (endpoints + services)

### Phase E-3 : Frontend
1. `GuideProDashboard.jsx` — Page principale
2. `SessionPlanner.jsx` — Planification
3. `GroupTracker.jsx` — Suivi temps reel
4. `ClientManager.jsx` — Gestion clients
5. `PostHuntReport.jsx` — Rapports
6. `GuideRouteOverlay.jsx` — Surcouche carte
7. Navigation conditionnelle (role GUIDE)

### Phase E-4 : Integration + Validation
1. Tests integration (15 endpoints + frontend flows)
2. Rapport BCE-4X complet
3. Validation STEEVE-MAX

---

## 10. CONFORMITE BCE-4X

| Critere | Engagement |
|---------|-----------|
| ZERO LOSS | Aucun engine existant modifie |
| ZERO REGRESSION | Logique Mon Territoire intouchee |
| ZERO INTERPRETATION | Architecture basee sur engines valides |
| ZERO DOUBLON | 7 modules interdits de recreation |
| ZERO OBSOLESCENCE | Consommation HUMAN_TRAJET_COSTS V7.2 |
| Merge Work1 → main | STRICTEMENT INTERDIT |
| Validation | EN ATTENTE STEEVE-MAX |

---

**STATUT: ARCHITECTURE COMPLETE — EN ATTENTE VALIDATION COMMANDANT STEEVE-MAX POUR IMPLEMENTATION**

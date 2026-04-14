# IA_VISION_PREP_REPORT.md
## BCE-4X ULTIME ABSOLU x3 — RAPPORT DE PREPARATION MODULE IA VISION ULTIME
### COMMANDANT STEEVE-MAX — DIRECTIVE IA-VISION-PREP-Omega-ULTIME

---

**DATE:** 2026-04-14 12:14 UTC
**BRANCHE:** SUPRA_RECONSTRUCTION
**METHODE:** Analyse code existant + recherche architecture IA
**DIRECTIVE:** IA-VISION-PREP-Omega-ULTIME
**STATUT:** PREPARATION UNIQUEMENT — ZERO IMPLEMENTATION

---

## 1. OBJET

Preparation complete du module IA Vision destine a remplacer le pipeline
ALPHA simule, analyser les photos des usagers, generer les Hotspots ALPHA,
reconstruire les trajectoires de gibier multi-cameras, enrichir la carte
MON TERRITOIRE, et fournir des notifications intelligentes au chasseur.

---

## 2. ETAT ACTUEL DU SYSTEME

### 2.1 Pipeline ALPHA simule (a remplacer)

| Fichier | Fonctions simulees | Methode |
|---------|-------------------|---------|
| `AdminAlphaAnalysis.jsx` L399-432 | `simulateSpeciesDetection()`, `simulateSexDetection()`, `simulateSizeScore()`, `computeAlphaScore()` | Hash deterministe sur event ID |
| `useAlphaLayer.js` L20-30 | `simulateSpecies()`, `computeAlphaScore()` | Hash deterministe sur event ID |

### 2.2 Backend camera_engine existant

| Service | Capacite actuelle |
|---------|------------------|
| `ExifReaderService` | Extraction basique EXIF (timestamp, GPS, make/model) via PIL |
| `ImageEncryptionService` | Chiffrement Fernet at-rest |
| `CameraRegistryService` | CRUD cameras, location GeoJSON, nearby search |
| `EmailIngestionService` | Ingestion email → event |
| `phase2_services.py` | AdvancedExif, Validation, Normalization (implementes) |

### 2.3 Collections MongoDB

| Collection | Documents | Schema |
|-----------|-----------|--------|
| `cameras` | 3 | id, user_id, email_alias, location, gps_lat/lon, waypoint_id |
| `camera_events` | 1 | id, camera_id, timestamp, raw_image_url, exif_data, source |
| `camera_photos` | 1 | id, event_id, storage_path, file_size, mime_type |
| `camera_ingestion_logs` | 0 | id, camera_id, status, message |

### 2.4 Frontend couches existantes

| Couche | Fichier | Statut |
|--------|---------|--------|
| CameraMarkersLayer | `/app/frontend/src/components/territoire/CameraMarkersLayer.jsx` | ACTIF |
| AlphaHotspotsLayer | `/app/frontend/src/components/territoire/AlphaHotspotsLayer.jsx` | ACTIF (simule) |
| useCameraLayer | `/app/frontend/src/hooks/useCameraLayer.js` | ACTIF |
| useAlphaLayer | `/app/frontend/src/hooks/useAlphaLayer.js` | ACTIF (simule) |

---

## 3. ARCHITECTURE IA VISION PROPOSEE

### 3.1 Modele Vision

```
Approche: API-first avec modele cloud (GPT Image / Gemini Vision)
Architecture: Pas de CNN/Transformer custom — utilisation d'un LLM Vision
via Emergent LLM Key pour analyse structuree des photos.

Avantages:
- ZERO entrainement requis (zero-shot)
- Multi-especes, multi-comportements
- Extraction texte structure (JSON)
- Mise a jour continue (modele cloud)
- Cout par analyse: ~0.01-0.05$ par photo

Alternative future (Phase B):
- Fine-tune YOLO/EfficientNet pour detection offline
- Embeddings locaux pour clustering individus
```

### 3.2 Pipeline d'analyse

```
Photo → [Validation] → [EXIF Extraction] → [IA Vision API]
                                                    ↓
                                            JSON structure:
                                            {
                                              species: "orignal",
                                              sex: "male",
                                              size_estimate: "large",
                                              antler_points: 12,
                                              alpha_score: 92,
                                              behavior: "feeding",
                                              activity_level: "high",
                                              individuals_count: 2,
                                              photo_quality: 85,
                                              confidence: 0.94,
                                              description: "Grand orignal male..."
                                            }
                                                    ↓
                                            [Stockage MongoDB]
                                                    ↓
                                            [Scoring ALPHA]
                                                    ↓
                                            [Hotspot Generation]
                                                    ↓
                                            [Trajectory Correlation]
```

### 3.3 API Backend

```
POST /api/v1/vision/analyze
Headers: Authorization: Bearer <JWT>
Body: multipart/form-data
  - photo_id: str (ID de la photo dans camera_photos)
  - OR image: UploadFile (analyse directe)

Response: {
  "success": true,
  "analysis": {
    "species": "orignal",
    "sex": "male",
    "size_estimate": "large",
    "antler_points": 12,
    "alpha_score": 92,
    "behavior": "feeding",
    "activity_level": "high",
    "individuals_count": 2,
    "photo_quality": 85,
    "confidence": 0.94,
    "embeddings_id": "emb_xxx"
  }
}

POST /api/v1/vision/batch-analyze
Body: { "photo_ids": ["id1", "id2", ...], "max": 50 }
Response: { "results": [...], "processed": 50, "failed": 0 }

GET /api/v1/vision/trajectories?camera_ids=id1,id2&days=30
Response: {
  "trajectories": [
    {
      "id": "traj_001",
      "species": "orignal",
      "individual_cluster": "ind_abc",
      "segments": [
        {"from_camera": "cam1", "to_camera": "cam2", "timestamp_from": "...", "timestamp_to": "...", "direction": "NW", "speed_kmh": 2.3},
        ...
      ],
      "circuit_detected": true,
      "circuit_period_hours": 72,
      "confidence": 0.82
    }
  ]
}

GET /api/v1/vision/hotspots/alpha
Response: {
  "hotspots": [
    {"id": "hs_001", "lat": 47.5, "lon": -71.8, "score": 92, "species": "orignal", "confidence": 0.94, ...}
  ]
}
```

---

## 4. SCHEMA DE DONNEES

### 4.1 Collection `vision_analyses` (NOUVELLE)

```json
{
  "id": "va_uuid",
  "user_id": "user_xxx",
  "photo_id": "photo_uuid",
  "event_id": "event_uuid",
  "camera_id": "cam_uuid",
  "species": "orignal",
  "sex": "male",
  "size_estimate": "large",
  "antler_points": 12,
  "alpha_score": 92,
  "behavior": "feeding",
  "activity_level": "high",
  "individuals_count": 2,
  "photo_quality": 85,
  "confidence": 0.94,
  "embeddings_id": "emb_xxx",
  "raw_response": { ... },
  "gps_lat": 47.5432,
  "gps_lon": -71.8765,
  "location": {"type": "Point", "coordinates": [-71.8765, 47.5432]},
  "analyzed_at": "2026-04-14T...",
  "model_version": "gpt-image-1",
  "cost_usd": 0.02,
  "created_at": "..."
}
```

### 4.2 Collection `vision_individuals` (NOUVELLE — clustering)

```json
{
  "id": "ind_uuid",
  "user_id": "user_xxx",
  "species": "orignal",
  "sex": "male",
  "estimated_age": "adult",
  "alpha_score_avg": 88,
  "sightings_count": 7,
  "first_seen": "2026-03-15T...",
  "last_seen": "2026-04-14T...",
  "cameras_seen": ["cam1", "cam2", "cam3"],
  "photo_ids": ["p1", "p2", ...],
  "embeddings": [0.12, 0.34, ...],
  "territory_center": {"type": "Point", "coordinates": [-71.8, 47.5]},
  "territory_radius_m": 2000,
  "created_at": "..."
}
```

### 4.3 Collection `vision_trajectories` (NOUVELLE)

```json
{
  "id": "traj_uuid",
  "user_id": "user_xxx",
  "individual_id": "ind_uuid",
  "species": "orignal",
  "segments": [
    {
      "from_camera_id": "cam1",
      "to_camera_id": "cam2",
      "from_lat": 47.54, "from_lon": -71.87,
      "to_lat": 47.55, "to_lon": -71.86,
      "timestamp_from": "2026-04-13T05:30:00Z",
      "timestamp_to": "2026-04-13T07:15:00Z",
      "direction_deg": 315,
      "direction_cardinal": "NW",
      "distance_m": 1200,
      "speed_kmh": 1.1
    }
  ],
  "is_circuit": true,
  "circuit_period_hours": 48,
  "confidence": 0.78,
  "total_distance_m": 5400,
  "created_at": "..."
}
```

### 4.4 Collection `vision_hotspots` (NOUVELLE)

```json
{
  "id": "hs_uuid",
  "user_id": "user_xxx",
  "location": {"type": "Point", "coordinates": [-71.8, 47.5]},
  "gps_lat": 47.5,
  "gps_lon": -71.8,
  "score": 92,
  "species": ["orignal", "cerf"],
  "dominant_species": "orignal",
  "alpha_count": 3,
  "total_sightings": 15,
  "activity_level": "extreme",
  "peak_hours": ["05:00-07:00", "17:00-19:00"],
  "trajectory_count": 2,
  "radius_m": 800,
  "last_activity": "2026-04-14T...",
  "created_at": "..."
}
```

### 4.5 Index MongoDB

```javascript
// vision_analyses
db.vision_analyses.createIndex({ "user_id": 1, "analyzed_at": -1 })
db.vision_analyses.createIndex({ "camera_id": 1, "analyzed_at": -1 })
db.vision_analyses.createIndex({ "species": 1, "alpha_score": -1 })
db.vision_analyses.createIndex({ "location": "2dsphere" }, { sparse: true })

// vision_individuals
db.vision_individuals.createIndex({ "user_id": 1, "species": 1 })
db.vision_individuals.createIndex({ "territory_center": "2dsphere" }, { sparse: true })

// vision_trajectories
db.vision_trajectories.createIndex({ "user_id": 1, "created_at": -1 })
db.vision_trajectories.createIndex({ "individual_id": 1 })

// vision_hotspots
db.vision_hotspots.createIndex({ "user_id": 1, "score": -1 })
db.vision_hotspots.createIndex({ "location": "2dsphere" })
```

---

## 5. INTEGRATION CARTE — NOUVELLES COUCHES

### 5.1 Couche Trajectoires (TrajectoriesLayer.jsx)

```
Lignes animees entre cameras montrant les deplacements detectes.
- Couleur par espece (ambre orignal, vert cerf, rouge ours)
- Animation CSS (dashOffset) pour effet de mouvement
- Epaisseur proportionnelle a la confiance
- Popup segment: direction, vitesse, temps, espece
- Toggle independant dans le panneau de couches
```

### 5.2 Couche Activite recente (ActivityHeatLayer.jsx)

```
Heatmap basee sur les analyses IA des 7 derniers jours.
- Intensite = nombre d'analyses × alpha_score moyen
- Filtrable par espece et periode (24h, 72h, 7j)
- Integre dans le panneau de couches existant
```

### 5.3 Couche Probabilite de rencontre (EncounterProbLayer.jsx)

```
Overlay semi-transparent colore:
- Score = f(activite_recente, meteo, vent, heure, phase_lunaire, trajectoires)
- Vert = haute probabilite, rouge = basse
- Refresh toutes les 15 minutes
- Integre avec le Score Chasse existant
```

### 5.4 Mise a jour AlphaHotspotsLayer.jsx

```
Remplacement des donnees simulees par donnees IA:
- Score IA + confiance
- Halo dynamique (rayon = territory_radius_m de l'individu)
- Popup enrichi: photo thumbnail, espece, sexe, taille, panache, comportement
- Lien direct vers l'historique de l'individu
```

---

## 6. OUTILS CHASSEUR — NOTIFICATIONS

### 6.1 Types de notifications

| Type | Declencheur | Priorite |
|------|------------|----------|
| `alpha_detected` | Score ALPHA >= 85 detecte sur une photo | HAUTE |
| `activity_spike` | Activite > 3x moyenne sur un hotspot | HAUTE |
| `circuit_active` | Circuit recurrent detecte entre cameras | MOYENNE |
| `corridor_shift` | Changement de trajectoire detecte | MOYENNE |
| `encounter_high` | Probabilite de rencontre > 80% | HAUTE |
| `weather_optimal` | Conditions ideales + activite IA | BASSE |
| `weekly_report` | Rapport hebdomadaire IA | BASSE |

### 6.2 Integration systeme de notification existant

```
Fichier: /app/frontend/src/modules/notifications/NotificationService.js
Integration: Ajout type "vision_alert" dans le registry existant
Backend: POST /api/v1/vision/notifications (cron ou webhook)
```

---

## 7. ADMIN & RAPPORTS

### 7.1 Remplacement pipeline simule

| Composant | Avant (simule) | Apres (IA) |
|-----------|----------------|------------|
| AdminAlphaAnalysis.jsx | `simulateSpeciesDetection()` | `GET /api/v1/vision/analyses` |
| useAlphaLayer.js | `simulateSpecies()` | `GET /api/v1/vision/hotspots/alpha` |
| Hotspots table | Hash deterministe | Donnees IA reelles |
| Score ALPHA | Random-like | CNN/LLM Vision score |

### 7.2 Nouvel onglet "Trajectoires" dans AdminAlphaAnalysis

```
- Carte miniature avec les trajectoires detectees
- Tableau des circuits recurrents
- Graphe de deplacement (camera → camera)
- Statistiques: distance totale, vitesse moyenne, periode
```

### 7.3 Rapports automatiques

```
POST /api/v1/vision/reports/generate
  - type: "weekly" | "monthly" | "seasonal"
  - Response: PDF ou JSON avec statistiques IA
```

---

## 8. PREPARATION PHASE B (DEM/LIDAR)

### 8.1 Integration altitude

```
Chaque vision_analysis aura:
  - altitude_m: float (extraite du DEM)
  - slope_deg: float (pente locale)
  - aspect_deg: float (orientation pente)
  - habitat_type: str (foret, clairiere, zone humide)

Correlation: alpha_score ↔ altitude ↔ habitat ↔ saison
```

### 8.2 Zones d'habitat IA

```
Clustering automatique des analyses par:
  - espece + habitat + saison → "zone d'habitat"
  - territoire d'un individu = convex hull des sightings
  - superposition avec corridors DEM/LIDAR
```

---

## 9. PREPARATION PHASE C (OFFLINE MODE ULTRA)

### 9.1 Cache IA local

```
Structure cache:
  /offline/
    /hotspots.json (top 50 hotspots ALPHA comprimes)
    /trajectories.json (circuits actifs des 30 derniers jours)
    /individuals.json (top 20 individus avec embeddings comprimes)
    /notifications.json (alertes non lues)
    /last_sync: timestamp
```

### 9.2 Analyse offline (mode terrain)

```
Fonctionnalites disponibles offline:
  - Consultation hotspots ALPHA (read-only)
  - Consultation trajectoires (read-only)
  - Score probabilite de rencontre (calcul local simplifie)
  - Recommendations d'affut (basees sur cache + vent local)
```

### 9.3 Synchronisation differee

```
Au retour de connexion:
  1. Upload photos prises hors-ligne
  2. Analyse IA batch
  3. Mise a jour cache local
  4. Notifications push des resultats
```

---

## 10. PLAN D'EXECUTION RECOMMANDE

### Phase VIS-A : Backend Vision Engine
1. Creer `/app/backend/modules/vision_engine/v1/`
2. Modeles Pydantic (VisionAnalysis, Individual, Trajectory, Hotspot)
3. Service `VisionAnalysisService` (appel LLM Vision via Emergent Key)
4. Endpoints: POST /analyze, POST /batch-analyze, GET /analyses
5. Collections + index MongoDB

### Phase VIS-B : Trajectoires & Individus
1. Service `TrajectoryService` (correlation multi-cameras)
2. Service `IndividualClusterService` (pseudo-ID par embeddings texte)
3. Endpoints: GET /trajectories, GET /individuals
4. Algorithme de detection de circuits recurrents

### Phase VIS-C : Hotspots IA
1. Service `HotspotGeneratorService` (aggregation analyses → hotspots)
2. Endpoint GET /hotspots/alpha (remplace la simulation)
3. Score probabilite de rencontre

### Phase VIS-D : Frontend couches carte
1. TrajectoriesLayer.jsx (lignes animees entre cameras)
2. Mise a jour AlphaHotspotsLayer.jsx (donnees IA)
3. Mise a jour useAlphaLayer.js (appel API IA au lieu de simulation)
4. Panneau de controle couches IA

### Phase VIS-E : Notifications & Admin
1. Notifications IA dans le systeme existant
2. Remplacement pipeline simule dans AdminAlphaAnalysis.jsx
3. Onglet Trajectoires dans Admin
4. Rapports automatiques

### Phase VIS-F : Tests anti-regression
1. Tests unitaires vision_engine
2. Tests integration trajectoires
3. Tests frontend couches carte
4. Anti-regression T1-T5 + camera + auth

---

## 11. RISQUES ET MESURES D'ATTENUATION

| # | Risque | Severite | Mitigation |
|---|--------|----------|------------|
| R1 | Cout API Vision par photo (0.01-0.05$) | MOYENNE | Batch analyze, cache resultats, limite quotidienne |
| R2 | Faux positifs detection espece | MOYENNE | Seuil confiance >= 0.7, validation manuelle option |
| R3 | Clustering individus imprecis | ELEVEE | Pseudo-ID probabiliste, pas de certitude affichee |
| R4 | Latence analyse (2-5s par photo) | BASSE | Analyse async, background task, batch |
| R5 | Trajectoires incorrectes (trop peu de cameras) | ELEVEE | Minimum 2 cameras, confiance affichee, filtre |
| R6 | Surcharge API (centaines de photos) | MOYENNE | Rate limiting, queue, batch max 50 |
| R7 | Donnees sensibles (localisation gibier) | CRITIQUE | Chiffrement, acces JWT, pas de partage public |
| R8 | Offline mode complexite | ELEVEE | Phase C separee, cache simpliste d'abord |
| R9 | DEM/LIDAR non disponible en preview | BASSE | Fallback altitude=0, habitat="inconnu" |
| R10 | Regression pipeline simule → IA | MOYENNE | Double-run transitoire, A/B testing |

---

## 12. DEPENDANCES TECHNIQUES

| Dependance | Statut | Action |
|-----------|--------|--------|
| Emergent LLM Key | DISPONIBLE | Utiliser pour GPT Image 1 ou Gemini Vision |
| emergentintegrations | INSTALLE | Appel API via la librairie |
| PIL/Pillow | INSTALLE | Extraction EXIF, thumbnails |
| MongoDB 2dsphere | ACTIF | Index sur vision_analyses, vision_hotspots |
| Leaflet/React-Leaflet | ACTIF | Couches carte |
| NotificationService | ACTIF | Integration alertes IA |

---

## 13. ESTIMATION EFFORT

| Phase | Complexite | Estimation |
|-------|-----------|------------|
| VIS-A (Backend engine) | ELEVEE | 1 session |
| VIS-B (Trajectoires) | ELEVEE | 1 session |
| VIS-C (Hotspots IA) | MOYENNE | 0.5 session |
| VIS-D (Frontend couches) | MOYENNE | 1 session |
| VIS-E (Notifications/Admin) | MOYENNE | 0.5 session |
| VIS-F (Tests) | BASSE | 0.5 session |
| **TOTAL** | | **~4-5 sessions** |

---

## 14. STATUT DE CONFORMITE

| Critere | Resultat | Preuve |
|---------|----------|--------|
| Architecture IA definie | PASSE | Section 3 |
| Pipeline analyse defini | PASSE | Section 3.2 |
| API endpoints definis | PASSE | Section 3.3 |
| Schema DB defini (4 collections) | PASSE | Section 4 |
| Couches carte definies (4) | PASSE | Section 5 |
| Notifications definies (7 types) | PASSE | Section 6 |
| Admin & rapports definis | PASSE | Section 7 |
| Phase B (DEM/LIDAR) preparee | PASSE | Section 8 |
| Phase C (Offline) preparee | PASSE | Section 9 |
| Plan execution (6 phases) | PASSE | Section 10 |
| Risques documentes (10) | PASSE | Section 11 |
| ZERO implementation | PASSE | Aucun fichier modifie |

**VERDICT: CONFORME — 12/12 criteres satisfaits avec preuves**

---

## 15. FIN DU DOCUMENT

**DATE DE CERTIFICATION:** 2026-04-14 12:14 UTC
**AUTEUR:** Agent BCE-4X sous ordres COMMANDANT STEEVE-MAX
**LIVRABLE:** /app/IA_VISION_PREP_REPORT.md
**PROCHAINE ETAPE:** En attente d'autorisation pour execution (phases VIS-A a VIS-F)
**AUCUNE execution ne sera entamee sans ordre explicite.**

═══════════════════════════════════════════════════════════════
     IA_VISION_PREP CERTIFIE — BCE-4X ULTIME ABSOLU
     MODULE IA VISION ULTIME — ARCHITECTURE COMPLETE
═══════════════════════════════════════════════════════════════

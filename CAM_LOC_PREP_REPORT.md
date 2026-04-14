# CAM_LOC_PREP_REPORT.md
## BCE-4X ULTIME ABSOLU x3 — RAPPORT DE PREPARATION LOCALISATION CAMERAS
### COMMANDANT STEEVE-MAX — DIRECTIVE CAM-LOC-PREP-Omega

---

**DATE:** 2026-04-14 00:47 UTC
**BRANCHE:** SUPRA_RECONSTRUCTION
**METHODE:** Analyse statique code existant
**DIRECTIVE:** CAM-LOC-PREP-Omega
**STATUT:** PREPARATION UNIQUEMENT — ZERO MODIFICATION

---

## 1. OBJET

Preparation du module de localisation geographique des cameras incluant:
champ GeoJSON `location`, index 2dsphere, endpoint de mise a jour de position,
composant de placement sur carte (CameraLocationPicker), integration dans la
carte principale BIONIC, et affichage des marqueurs cameras.

---

## 2. ETAT ACTUEL

### 2.1 Champs GPS existants (models.py)

```
Fichier: /app/backend/modules/camera_engine/v1/models.py
L63-64 (CameraBase):
    gps_lat: Optional[float] = None
    gps_lon: Optional[float] = None
```

**Probleme:** Les champs `gps_lat`/`gps_lon` sont des scalaires independants.
MongoDB 2dsphere requiert un champ GeoJSON `location` de type Point:
```json
{ "type": "Point", "coordinates": [lon, lat] }
```

### 2.2 Index existants (router.py)

```
Fichier: /app/backend/modules/camera_engine/v1/router.py
L491-499 (ensure_camera_indexes):
    - cameras: (user_id, status)
    - cameras: email_alias (unique)
    - camera_events: (user_id, timestamp)
    - camera_events: (camera_id, timestamp)
    - camera_events: (waypoint_id, timestamp)
    - camera_events: species
    - camera_photos: event_id
    - camera_photos: (camera_id, created_at)
    - camera_ingestion_logs: (camera_id, created_at)
```

**AUCUN index 2dsphere** sur la collection cameras.

### 2.3 Carte principale (MapContent.jsx)

La carte utilise React-Leaflet avec:
- `Marker` + `Popup` pour les waypoints, places, position utilisateur
- `createCustomIcon()` pour les icones personnalisees
- Layers modulaires (corridors, heatmap, zones, etc.)
- Pas de layer camera existant

### 2.4 Frontend CameraModule.jsx existant

Le composant `CameraModule.jsx` affiche les cameras en grille avec:
- Nom, fabricant, statut, photo_count, email_alias
- Boutons upload et suppression
- Aucune fonctionnalite de positionnement sur carte

---

## 3. PLAN DE MIGRATION GEOSPATIALE

### 3.1 Ajout du champ `location` (GeoJSON Point)

**Modele Camera (models.py):**
```python
# Ajouter au modele CameraBase:
location: Optional[dict] = None  # GeoJSON Point: {"type": "Point", "coordinates": [lon, lat]}

# Ajouter au modele CameraResponse:
location: Optional[dict] = None
```

**Service (services.py) — create_camera:**
```python
# Generer automatiquement `location` depuis gps_lat/gps_lon:
if data.gps_lat is not None and data.gps_lon is not None:
    camera.location = {"type": "Point", "coordinates": [data.gps_lon, data.gps_lat]}
```

### 3.2 Index 2dsphere

```python
# Dans ensure_camera_indexes:
await db['cameras'].create_index([("location", "2dsphere")])
```

### 3.3 Endpoint PUT /cameras/{camera_id}/location

```
PUT /api/v1/camera/cameras/{camera_id}/location
Headers: Authorization: Bearer <JWT>
Body: {
  "lat": 47.1234,
  "lon": -71.5678
}
Response: {
  "success": true,
  "camera_id": "...",
  "location": {"type": "Point", "coordinates": [-71.5678, 47.1234]}
}
```

**Logique:**
1. Verifier que la camera appartient a l'utilisateur
2. Mettre a jour `gps_lat`, `gps_lon`, et `location` (GeoJSON)
3. Retourner la camera mise a jour

### 3.4 Endpoint GET /cameras/nearby (requete geospatiale)

```
GET /api/v1/camera/cameras/nearby?lat=47.12&lon=-71.56&radius_km=10
Headers: Authorization: Bearer <JWT>
Response: {
  "cameras": [...],
  "total": 3
}
```

Utilise `$nearSphere` avec l'index 2dsphere.

---

## 4. COMPOSANT CameraLocationPicker.jsx

### 4.1 Fonctionnalite

Un picker Leaflet modal qui permet a l'utilisateur de:
1. Voir la carte centree sur la position du waypoint de la camera (si disponible)
2. Cliquer sur la carte pour placer/deplacer le marqueur camera
3. Voir les coordonnees en temps reel
4. Confirmer la position (appel PUT /cameras/{id}/location)

### 4.2 Architecture du composant

```jsx
<Dialog>
  <MapContainer center={defaultCenter} zoom={14}>
    <TileLayer url="..." />
    {/* Marqueur de la camera (draggable) */}
    <Marker position={cameraPosition} draggable={true} onDragEnd={updatePosition}>
      <Popup>Camera: {camera.name}</Popup>
    </Marker>
    {/* Handler de clic sur la carte */}
    <MapClickHandler onClick={setPosition} />
  </MapContainer>
  <div className="coords-display">
    Lat: {lat} | Lon: {lon}
  </div>
  <Button onClick={saveLocation}>Confirmer la position</Button>
</Dialog>
```

### 4.3 Integration dans CameraModule.jsx

Ajout d'un bouton "Localiser" sur chaque carte camera:
```jsx
<Button onClick={() => openLocationPicker(cam)}>
  <MapPin /> Localiser
</Button>
```

---

## 5. AFFICHAGE DES CAMERAS SUR LA CARTE PRINCIPALE

### 5.1 Nouveau layer: CameraMarkersLayer.jsx

Fichier: `/app/frontend/src/components/territoire/CameraMarkersLayer.jsx`

```jsx
const CameraMarkersLayer = ({ cameras }) => {
  return cameras.map(cam => (
    cam.gps_lat && cam.gps_lon && (
      <Marker key={cam.id} position={[cam.gps_lat, cam.gps_lon]}
              icon={cameraIcon}>
        <Popup>
          <div>
            <strong>{cam.name}</strong>
            <p>{cam.manufacturer} {cam.model}</p>
            <p>{cam.photo_count} photos</p>
            <Badge>{cam.status}</Badge>
          </div>
        </Popup>
      </Marker>
    )
  ));
};
```

### 5.2 Integration dans MapContent.jsx

```jsx
// Import
import CameraMarkersLayer from './CameraMarkersLayer';

// Rendu (dans le JSX du MapContent):
{showCameras && <CameraMarkersLayer cameras={userCameras} />}
```

### 5.3 Toggle dans la UI

Ajout d'un toggle "Cameras" dans le panneau de layers existant,
a cote des toggles corridors, heatmap, zones, etc.

### 5.4 Icone camera personnalisee

```javascript
const cameraIcon = L.divIcon({
  className: 'camera-marker',
  html: '<div style="background:#F59E0B;border-radius:50%;width:28px;height:28px;
         display:flex;align-items:center;justify-content:center;border:2px solid #fff;">
         <svg width="16" height="16" viewBox="0 0 24 24" fill="white">...</svg></div>',
  iconSize: [28, 28],
  iconAnchor: [14, 14]
});
```

---

## 6. DEPENDANCES TECHNIQUES

| Dependance | Statut | Impact |
|-----------|--------|--------|
| react-leaflet | Deja installe | ZERO |
| leaflet | Deja installe | ZERO |
| MongoDB 2dsphere | Supporte nativement | Index a creer |
| camera_engine API | Actif (12 endpoints) | +2 endpoints |
| auth_engine JWT | Actif | ZERO modification |
| roles_engine | Actif | ZERO modification |

---

## 7. RISQUES ET MESURES D'ATTENUATION

| # | Risque | Severite | Mitigation |
|---|--------|----------|------------|
| R1 | Cameras existantes sans champ `location` | BASSE | Migration: generer `location` depuis `gps_lat`/`gps_lon` existants |
| R2 | Index 2dsphere echoue si documents invalides | MOYENNE | Sparse index (ignore les documents sans `location`) |
| R3 | Collision avec markers waypoints existants | BASSE | Icone camera distincte (couleur ambre, forme cercle) |
| R4 | Performance carte avec nombreuses cameras | BASSE | Clustering Leaflet (MarkerClusterGroup) si > 50 cameras |
| R5 | Regression MapContent.jsx (composant critique) | MOYENNE | Layer camera separe, import conditionnel, toggle independant |
| R6 | Precision GPS cameras trail (pas toujours fiable) | BASSE | Position manuelle via picker comme fallback |

---

## 8. PLAN D'EXECUTION

### LOC-A: Backend — Champ location + index
1. Ajouter `location: Optional[dict] = None` aux modeles Camera, CameraBase, CameraResponse
2. Generer `location` GeoJSON automatiquement dans `create_camera()` et `update_camera()`
3. Ajouter index 2dsphere sur `cameras.location` (sparse)
4. Script migration: generer `location` pour les cameras existantes avec gps_lat/lon

### LOC-B: Backend — Endpoints localisation
1. `PUT /api/v1/camera/cameras/{id}/location` (set position)
2. `GET /api/v1/camera/cameras/nearby` (requete geospatiale)

### LOC-C: Frontend — CameraLocationPicker
1. Composant modal avec carte Leaflet + marqueur draggable
2. Integration bouton "Localiser" dans CameraModule.jsx

### LOC-D: Frontend — CameraMarkersLayer
1. Layer Leaflet independant affichant les cameras avec icone personnalisee
2. Integration dans MapContent.jsx avec toggle
3. Popup avec info camera + derniere photo

### LOC-E: Tests
1. Test creation camera avec position (backend)
2. Test mise a jour position (backend)
3. Test requete nearby (backend)
4. Test visuel carte (frontend)
5. Anti-regression T1-T5

---

## 9. PREUVES

### P1 — Champs GPS existants
```
$ grep -n "gps_lat\|gps_lon" /app/backend/modules/camera_engine/v1/models.py
63:    gps_lat: Optional[float] = None
64:    gps_lon: Optional[float] = None
```

### P2 — Absence d'index 2dsphere
```
$ grep -n "2dsphere" /app/backend/modules/camera_engine/v1/router.py
(aucun resultat)
```

### P3 — Carte Leaflet existante
```
$ grep -n "Marker.*Popup\|createCustomIcon" /app/frontend/src/components/territoire/map/MapContent.jsx
8:import { Marker, Popup, Circle, Rectangle } from 'react-leaflet';
263:      <Marker position={[userPosition.lat, userPosition.lng]} ...>
```

---

## 10. STATUT DE CONFORMITE

| Critere | Resultat | Preuve |
|---------|----------|--------|
| Analyse champ location (Point) | PASSE | P1 |
| Plan index 2dsphere | PASSE | Section 3.2 |
| Spec endpoint PUT /cameras/{id}/location | PASSE | Section 3.3 |
| Spec CameraLocationPicker.jsx | PASSE | Section 4 |
| Spec bouton "Localiser" dans CameraManager | PASSE | Section 4.3 |
| Spec affichage cameras sur carte principale | PASSE | Section 5 |
| Risques et mesures d'attenuation | PASSE | Section 7 (6 risques) |
| ZERO modification | PASSE | Aucun fichier modifie |

**VERDICT: CONFORME — 8/8 criteres satisfaits**

---

## 11. FIN DU DOCUMENT

**DATE DE CERTIFICATION:** 2026-04-14 00:47 UTC
**AUTEUR:** Agent BCE-4X sous ordres COMMANDANT STEEVE-MAX
**LIVRABLE:** /app/CAM_LOC_PREP_REPORT.md
**PROCHAINE ETAPE:** En attente d'autorisation pour execution (phases LOC-A a LOC-E)

═══════════════════════════════════════════════════════════════
      CAM_LOC_PREP CERTIFIE — BCE-4X ULTIME ABSOLU
═══════════════════════════════════════════════════════════════

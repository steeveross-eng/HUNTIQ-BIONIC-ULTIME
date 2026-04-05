# PHASE B — AUDIT STRATÉGIQUE BIONIC OS — PRÉVENTION DES DOUBLONS
## Directive ×7100-M4 — Phase B
### Protocole BCE-4X GOLDEN V6+ | Autorité : STEEVE-MAX
### Date : 2026-04-05 | Merge MAIN : STRICTEMENT INTERDIT

---

## STATUT : AUDIT COMPLÉTÉ

---

## 1. PÉRIMÈTRE AUDITÉ

| # | Module/Feature | Localisation frontend | Lignes | Backend |
|---|---------------|----------------------|--------|---------|
| 1 | **CARTE** (MapPage) | `pages/MapPage.jsx` | 383 | WaypointMap, BionicMapOverlay |
| 2 | **MON TERRITOIRE** | `pages/MonTerritoireBionicPage.jsx` | 1526 | MapContent, IntelligenceDashboard |
| 3 | **GPS Tracking** | `components/BackgroundTracker.jsx` | 390 | GeolocationService |
| 4 | **Groupe** | `modules/groupe/` (7 composants + 4 hooks) | 2617 | useLiveTracking |
| 5 | **Hotspots** | `modules/map_hotspots/` + `GpsHotspots.jsx` | 1815 | hotspot_engine, auto_cartography |
| 6 | **Replay** | `components/territoire/RouteReplayLayer.jsx` | 425 | API parcours |
| 7 | **Parcours** | `GuidedRoutePanel.jsx` + `GuidedRouteLayer.jsx` + `RoutePlannerLayer.jsx` | ~550 | API routes |
| 8 | **SUPRA** | `pages/SupraPage.jsx` + `NutritionPointDetailPanel.jsx` | 1283 | Nutrition V6 Interface |
| 9 | **INTELLIGENCE** | `pages/intelligence/IntelligenceV6Page.jsx` + widgets | ~1200 | M3 Predictive Layer |
| 10 | **IntelligenceDashboard** | `components/territoire/IntelligenceDashboard.jsx` | 365 | Bionic engines |

**Total audité : ~10 554 lignes frontend, 85+ modules backend**

---

## 2. DOUBLONS FONCTIONNELS IDENTIFIÉS

### DOUBLON D-01 : LOCALISATION LIVE (Critique — 5 implémentations fragmentées)

| Composant | Fichier | Rôle | API utilisée |
|-----------|---------|------|-------------|
| BackgroundTracker | `components/BackgroundTracker.jsx` | Tracking individuel arrière-plan | GeolocationService |
| useGroupeTracking | `modules/groupe/hooks/useGroupeTracking.js` | Tracking membres groupe | useLiveTracking |
| useLiveTracking | `hooks/useLiveTracking.js` | Hook tracking temps réel | Backend /api/gps/ |
| GeoSyncToggle | `components/GeoSyncToggle.jsx` | Toggle sync position | Backend /api/sync/ |
| useGeolocation | `hooks/useGeolocation.js` | Hook géolocalisation MonTerritoire | navigator.geolocation |

**Impact** : 5 sources de position LIVE indépendantes. Un chasseur peut avoir sa position traquée par 3 systèmes simultanément sans cohérence.

**Consolidation requise** : Source unique = **Gestionnaire** (fournit la position LIVE à tous les consommateurs via un channel EventBus unique `LIVE_POSITION_UPDATED`).

---

### DOUBLON D-02 : CARTE ↔ MON TERRITOIRE (Majeur — 2 systèmes de carte parallèles)

| Aspect | CARTE (MapPage) | MON TERRITOIRE |
|--------|----------------|----------------|
| Composant carte | `WaypointMap` (modules/territory) | `MapContent` + `MapContainer` (Leaflet direct) |
| Overlay BIONIC | `BionicMapOverlay` | `BionicMapOverlay` (même composant, bien) |
| Hotspots | Via BionicMapOverlay | Via BionicMapOverlay + HotspotOverlay |
| Zones | Via overlay | Via MapContent + TerritoireDialogs |
| GPS Tracking | Tab dédiée | useGeolocation intégré |
| Groupe | Tab dédiée (GroupeTab) | GroupeTab (même import) |
| Intelligence | Non intégré | IntelligenceDashboard (cockpit flottant) |
| Waypoints | WaypointMap CRUD | WaypointUnifiedPanel |
| Parcours/Route | Non intégré | GuidedRouteLayer + GuidedRoutePanel + RoutePlannerLayer |
| Replay | Non intégré | RouteReplayLayer |
| SUPRA | Non intégré | NutritionPointDetailPanel |
| Lignes | 383 | 1526 |

**Impact** : MON TERRITOIRE est la version riche et complète. CARTE est une version simplifiée qui duplique partiellement les fonctionnalités. Les utilisateurs voient 2 pages avec des cartes différentes — confusion UX.

**Consolidation requise** : CARTE doit devenir un **mode/vue** de MON TERRITOIRE (ou le Gestionnaire unifié), pas une page séparée.

---

### DOUBLON D-03 : HOTSPOTS (Mineur — 2 listes indépendantes)

| Composant | Fichier | Rôle |
|-----------|---------|------|
| HotspotOverlay | `modules/map_hotspots/HotspotOverlay.jsx` (639 l.) | Overlay GeoJSON sur Leaflet dans MON TERRITOIRE |
| HotspotControlPanel | `modules/map_hotspots/HotspotControlPanel.jsx` (600 l.) | Panneau de contrôle ON/OFF |
| GpsHotspots | `components/GpsHotspots.jsx` (576 l.) | Page/liste complète des hotspots GPS |
| HotspotListPanel | `components/bionic/HotspotListPanel.jsx` | Panneau liste hotspots |
| AdminBionicHotspots | `components/bionic/admin/AdminBionicHotspots.jsx` | Admin hotspots |
| EnrichedHotspotPopup | `components/bionic/EnrichedHotspotPopup.jsx` | Popup enrichie |

**Impact** : Le même concept "hotspot" est affiché par 4+ composants différents, chacun fetchant les données indépendamment du backend.

**Consolidation requise** : Un unique `HotspotDataProvider` alimenté par le Gestionnaire, distribuant via EventBus channel `HOTSPOTS_UPDATED`.

---

### DOUBLON D-04 : INTELLIGENCE (Mineur — 2 dashboards parallèles)

| Composant | Fichier | Rôle |
|-----------|---------|------|
| IntelligenceV6Page | `pages/intelligence/IntelligenceV6Page.jsx` | Dashboard M3 (DFL + EventBus V6) |
| IntelligenceDashboard | `components/territoire/IntelligenceDashboard.jsx` | Cockpit V6-CORE dans MON TERRITOIRE |

**Impact** : Deux tableaux de bord "intelligence" avec des sources de données différentes. IntelligenceV6Page utilise DFL+DataContracts V6 (propre), IntelligenceDashboard utilise useBionicStore (legacy).

**Consolidation requise** : IntelligenceDashboard doit migrer vers DFL+DataContracts V6 (align sur IntelligenceV6Page). Source unique de vérité = DFL.

---

### NON-DOUBLONS CONFIRMÉS (modules bien isolés)

| Module | Statut | Justification |
|--------|--------|---------------|
| **Groupe** (modules/groupe/) | PROPRE | Module bien encapsulé avec index.js, 7 composants, 4 hooks |
| **SUPRA** (NutritionPointDetailPanel) | PROPRE | Composant unique, réutilisé par SupraPage et MonTerritoire |
| **Replay** (RouteReplayLayer) | PROPRE | Module isolé, zéro dépendance circulaire |
| **Parcours** (GuidedRoute*) | PROPRE | 3 composants distincts (planning, display, panel) |
| **EventBus V6** | PROPRE | 13 channels documentés, pas de doublon |
| **DataContracts V6** | PROPRE | 8 contrats uniques |

---

## 3. DÉFINITION DU MODULE "GESTIONNAIRE"

### 3.1 — Rôle : Source Unique de Vérité

Le module **Gestionnaire** centralise toutes les fonctions suivantes sous un point d'entrée unique :

| Fonction | Source actuelle (fragmentée) | Source future (Gestionnaire) |
|----------|---------------------------|------------------------------|
| **Localisation LIVE** | 5 implémentations (D-01) | `GestionnairePositionService` → EventBus `LIVE_POSITION_UPDATED` |
| **Gestion des groupes** | modules/groupe/ (déjà propre) | Intégré tel quel (ZERO modification) |
| **Gestion des secteurs/blocs** | TerritoireDialogs + DiagnosticExclusionsPanel + BionicZoneDiagnosticPanel | `GestionnaireSectorService` → EventBus `SECTOR_UPDATED` |
| **Sécurité** | SafetyStatus + ShootingZones (dans Groupe) | Intégré tel quel + canal Gestionnaire SECOURS |
| **Chat** | GroupChat (dans Groupe) | Intégré tel quel (ZERO modification) |
| **Permissions** | Fragmenté (rôle admin/user) | `GestionnairePermissionService` → cloisonnement par organisation |
| **Urgences (SECOURS)** | Non existant | NOUVEAU : `SecoursService` → EventBus `EMERGENCY_ALERT` |

### 3.2 — Architecture cible Gestionnaire

```
gestionnaire/
├── GestionnaireProvider.jsx    ← Context provider (source unique)
├── services/
│   ├── GestionnairePositionService.js   ← Position LIVE unifiée
│   ├── GestionnaireSectorService.js     ← Secteurs/blocs/occupation
│   ├── GestionnairePermissionService.js ← Rôles/permissions/cloisonnement
│   └── SecoursService.js                ← Urgences terrain
├── components/
│   ├── GestionnaireMapMode.jsx  ← Mode carte "Gestionnaire"
│   ├── SectorManager.jsx       ← Gestion secteurs/blocs
│   ├── LiveTrackingPanel.jsx   ← Vue LIVE des chasseurs
│   ├── SecoursButton.jsx       ← Bouton SECOURS
│   └── SecoursAlertPanel.jsx   ← Panneau alertes urgences (admin)
└── index.js
```

### 3.3 — Modules existants NON MODIFIÉS (ZERO LOSS)

| Module | Action |
|--------|--------|
| modules/groupe/ | INTÉGRÉ tel quel (import, pas copie) |
| BackgroundTracker | ENVELOPPÉ par GestionnairePositionService (pas supprimé) |
| useGroupeTracking | CONSOMMÉ par GestionnairePositionService (pas supprimé) |
| GeoSyncToggle | ENVELOPPÉ par GestionnairePositionService (pas supprimé) |
| useGeolocation | CONSOMMÉ par GestionnairePositionService (pas supprimé) |

**ZERO suppression. ZERO modification de code existant. Le Gestionnaire ENVELOPPE et UNIFIE.**

---

## 4. HARMONISATION CARTE ↔ MON TERRITOIRE ↔ GESTIONNAIRE

### 4.1 — État actuel

```
CARTE (MapPage.jsx)          ←→  MON TERRITOIRE (MonTerritoireBionicPage.jsx)
      383 lignes                         1526 lignes
      WaypointMap                        MapContent + MapContainer
      3 tabs (Carte/GPS/Groupe)          Orchestrateur complet
      Pas d'intelligence                 IntelligenceDashboard
      Pas de SUPRA                       SUPRA intégré
      Pas de routes                      Routes + Replay
```

### 4.2 — Architecture cible harmonisée

```
MON TERRITOIRE = Page MAÎTRE (inchangée, ZERO modification)
    └── Mode: Normal (chasseur individuel)
    
CARTE (MapPage) = Mode allégé pour navigation rapide
    └── ENRICHI avec: GUIDE PRO + Gestionnaire mode
    └── Tab Gestionnaire (NOUVEAU) remplace complexité MON TERRITOIRE pour admins
    
GESTIONNAIRE = Mode admin dans CARTE
    └── Tab supplémentaire dans MapPage
    └── Localisation LIVE centralisée
    └── Secteurs/Blocs
    └── SECOURS
```

**Principe** : MON TERRITOIRE reste la référence individuelle (pas touché). CARTE reçoit les nouvelles fonctionnalités (GUIDE PRO, Gestionnaire, SECOURS) via des tabs/modes additionnels. ZÉRO suppression.

---

## 5. VALIDATION DATACONTRACTS V6

### 5.1 — Audit d'unicité

| DC# | Contrat | Unique? | Conflit identifié |
|-----|---------|---------|-------------------|
| DC-01 | ConsolidatedView | OUI | Aucun |
| DC-02 | ScoreConsolidé | OUI | IntelligenceDashboard utilise useBionicStore (legacy) — à migrer |
| DC-03 | HeatmapData | OUI | Aucun |
| DC-04 | TimeSeries | OUI | Aucun |
| DC-05 | Trends | OUI | Aucun |
| DC-06 | Correlation | OUI | Aucun |
| DC-07 | BestTimes | OUI | Aucun |
| DC-08 | POIEnriched | OUI | Aucun |

**Résultat** : 8/8 contrats uniques. 1 conflit mineur (IntelligenceDashboard → migration DFL recommandée).

### 5.2 — Nouveaux DataContracts requis par le Gestionnaire

| DC# | Contrat | Usage |
|-----|---------|-------|
| DC-12 | **LivePosition** | position LIVE chasseur (lat, lng, timestamp, accuracy, status, user_id) |
| DC-13 | **SectorStatus** | secteur/bloc (sector_id, status{libre/occupé}, hunters[], capacity) |
| DC-14 | **EmergencyAlert** | alerte SECOURS (alert_id, user_id, position, timestamp, status, channel_id) |

### 5.3 — Nouveaux channels EventBus requis

| EB# | Channel | Émetteur | Souscripteur |
|-----|---------|---------|-------------|
| EB-14 | `HUNTER_PROFILE_UPDATED` | DFL M4 | HunterProfileWidget |
| EB-15 | `NAVIGATION_SESSION_UPDATED` | DFL M4 | NavigationWidget |
| EB-16 | `CONTEXTUAL_ADVICE_UPDATED` | DFL M4 | AdviceWidget, GuideProWidget |
| EB-17 | `LIVE_POSITION_UPDATED` | GestionnairePositionService | GestionnaireMapMode, LiveTrackingPanel |
| EB-18 | `SECTOR_UPDATED` | GestionnaireSectorService | SectorManager, GestionnaireMapMode |
| EB-19 | `EMERGENCY_ALERT` | SecoursService | SecoursAlertPanel, GestionnaireMapMode |

---

## 6. BUG HOTSPOTS — DIAGNOSTIC PRÉLIMINAIRE

### 6.1 — Symptôme

Les hotspots apparaissent alignés sur Québec (ville) au lieu d'être dispersés sur les territoires de chasse.

### 6.2 — Hypothèses

| # | Hypothèse | Probabilité | Fichier à investiguer |
|---|-----------|------------|----------------------|
| H1 | **Coordonnées par défaut (46.81, -71.21)** utilisées quand aucune donnée terrain n'existe | ÉLEVÉE | `auto_cartography.py`, `hotspot_engine.py` |
| H2 | **Filtre zone manquant** — hotspots générés sans filtrage par territoire utilisateur | MOYENNE | `hotspot_router.py` (extraction par region) |
| H3 | **Projection inversée** (lat/lng ↔ lng/lat) dans le GeoJSON | FAIBLE | `HotspotOverlay.jsx` ligne 108-131 |
| H4 | **Données test/seed** avec coordonnées Québec-ville non nettoyées | MOYENNE | Base MongoDB `hotspots` collection |

**Action Phase C** : Investigation complète avec correction du backend + validation frontend.

---

## 7. RÉSUMÉ EXÉCUTIF

### Doublons identifiés : 4

| ID | Doublon | Sévérité | Consolidation |
|----|---------|----------|--------------|
| D-01 | Localisation LIVE (5 implémentations) | CRITIQUE | → GestionnairePositionService |
| D-02 | CARTE ↔ MON TERRITOIRE (2 cartes) | MAJEUR | → CARTE enrichie + MON TERRITOIRE inchangé |
| D-03 | Hotspots (4+ composants indépendants) | MINEUR | → HotspotDataProvider unique |
| D-04 | Intelligence (2 dashboards) | MINEUR | → Migration IntelligenceDashboard → DFL |

### Modules propres confirmés : 6
Groupe, SUPRA, Replay, Parcours, EventBus V6, DataContracts V6

### Nouveaux éléments requis
- 3 DataContracts (DC-12, DC-13, DC-14)
- 6 Channels EventBus (EB-14 → EB-19)
- Module Gestionnaire (5 services + 5 composants)

### Code existant modifié : ZÉRO
### Code existant supprimé : ZÉRO

---

## 8. CONFORMITÉ BCE-4X

| Principe | Respect |
|----------|---------|
| ZERO LOSS | Aucun code supprimé, tous les modules préservés | CONFORME |
| ZERO REGRESSION | Audit documentaire uniquement, aucun code modifié | CONFORME |
| ZERO DOUBLON | 4 doublons identifiés avec plan de consolidation | DIAGNOSTIQUÉ |
| ZERO INTERPRETATION | Analyse factuelle fichier par fichier | CONFORME |
| ZERO OBSOLESCENCE | Consolidation par enveloppement, pas par suppression | CONFORME |
| Merge main | INTERDIT | CONFORME |

---

**Protocole** : BCE-4X GOLDEN V6+
**Autorité** : STEEVE-MAX
**Version** : AUDIT_BIONIC_OS_DEDUP 1.0.0
**Merge main** : STRICTEMENT INTERDIT
**Code modifié** : ZÉRO
**Code supprimé** : ZÉRO

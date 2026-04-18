# HUNTIQ V20 — PRD
## FRONTEND-Omega V2 — CORRECTIFS SYNCHRONISATION TERRITOIRE-Ω
**MAJ:** 2026-04-18

## PRINCIPE DIRECTEUR
**PROTOCOLE BCE-4X ULTIME ABSOLU — ZERO FENETRE, ZERO PANNEAU LATERAL ANALYTIQUE, ZERO REACTIVATION AUTOMATIQUE**
Tous les contrôles institutionnels = boutons presseurs ON/OFF stricts sur la barre outils Territoire.

## FRONTEND-Omega V2 (2026-04-18)
### Boutons presseurs (TerritoireToolbar.jsx)
- 13 PressButton ON/OFF avec halo lumineux
- 0 DropdownMenu, 0 Switch, 1 Popover (fond de carte UNIQUEMENT)
- Ordre: SPLIT | CARTE | ESPECE | WAYPOINTS | LIEUX | **INTEL** | ZONES | CORRIDORS | AFFUTS | SALINES | HOTSPOTS | VENT | CONTAM | CURSEUR | SCORE | ADMIN
- ESPECE = bouton cyclique (clic = prochaine espèce)
- **INTEL** = master institutionnel (ON = rendu V20 complet, OFF = carte nue)

### Purge (MonTerritoireBionicPage.jsx)
- **Supprimé**: IntelligenceDashboard (overlay flottant)
- **Supprimé**: PhaseAPanelV8 (panneau salines) → Salines sont maintenant une couche sur la carte via showSalinesLayer
- **Supprimé**: PhaseCPanelV8 (panneau contamination) → Cônes sur carte via showContaminationLayer
- **Supprimé**: NutritionPanel, AmenagementPanel, StandDetailPanel, NutritionPointDetailPanel (zéro fenêtre)
- **Supprimé**: BionicZoneDiagnosticPanel (overlay zone click)
- **Supprimé**: DiagnosticExclusionsPanel, GroupeTab (onglets 'groupe', 'exclusions' retirés)
- **Conservé**: WaypointUnifiedPanel + PlacesSidePanel (opérationnels CRUD)
- **Purgé**: HEARTBEAT 5s qui forçait ON les couches → désormais ON/OFF strict
- **Purgé**: imports useGroupeTracking

### Câblage (MapContent.jsx)
- BionicLayersV8: toggles reliés aux props réels (showSalines/Contamination/Hotspots/Wind/IntelLayer)
- WindFlowLayer conditionné par `showWindFlow && showIntelLayer`
- `enabled={showIntelLayer}` = kill-switch master

## RENDERER V20-INSTITUTIONNEL (BionicLayersV8.jsx)
### Corridors — 4 niveaux stricts (inchangé, conforme)
- EXTREME  : #D32F2F 4.2px opacity 0.95
- INTENSE  : #FF9800 3.0px opacity 0.90
- SAISONNIER: #4CAF50 2.4px opacity 0.90
- NORMAL   : #FFFFFF 1.6px opacity 0.85
- Catmull-Rom, smoothFactor=0, ZERO bezier

### Salines — VALIDEE vs A-REPOSITIONNER
- VALIDEE: #FDD835 plein, radius 8
- A-REPOSITIONNER: #EF5350 pointillé, + suggestion verte + ligne pointillée
- Tooltip: eau_distance_m + corridor_distance_m + suggestion

### Affûts — FIXE PERMANENT + TEMPORAIRES
- FIXE: #9E9E9E, X central #424242, weight 3
- TEMPORAIRE: #1E88E5, flèche orientée, weight 2.4
- Tooltip: type + score + description + corridor + orientation + distance saline

### Contamination — multi-cônes 3 intensités
- Source = AFFUTS (pas waypoint)
- faible/moyen/fort dash arrays distincts

### Hotspots — 5 niveaux
- Radii 4→8, palette rouge graduée

## ENGINE AFFUTS-Omega V11
- 1 FIXE PERMANENT, 5 TEMPORAIRES
- 18 cônes contamination (3 intensités × 6 affûts)

## Architecture V20 (backend)
- CONTOUR 600m | ZONES 5 | CORRIDORS 27 (4 types) | CONTAMINATION 18
- AFFUTS 6 | SALINES 6 | HOTSPOTS 11
- SECURITE 5/5 | ESI 8/8
- Endpoint: `GET /api/v8/institutional/territoire`

## Credentials
- Admin: admin@huntiq.com / Saturn5858*

## Backlog
- P1: Intégration directe LiDAR WCS 1m & WMS IRDA pédologique (actuellement fallback Open-Meteo)

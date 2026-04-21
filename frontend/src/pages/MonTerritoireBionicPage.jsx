/**
 * MonTerritoireBionicPage - Page dédiée Mon Territoire BIONIC™
 * VERSION: 7.3.0 — IM1 Refactorisation modulaire
 * 
 * Architecture: Composant orchestrateur qui delegue aux sous-composants:
 * - MapHelpers: composants Leaflet utilitaires
 * - TerritoireHeader: header score/meteo/LIVE
 * - TerritoireDialogs: toutes les modales
 * - IntelligenceDashboard: cockpit central flottant INTELLIGENCE
 * - useGeolocation: hook geolocalisation
 * - placeTypes: constantes types de lieux
 */

import React, { useState, useCallback, useMemo, useEffect, useLayoutEffect, useRef } from 'react';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
import { MapContainer } from 'react-leaflet';
import { useNavigate, useSearchParams } from 'react-router-dom';
import {
  Crosshair, Target, MapPin, Plus, X, LocateFixed,
  BookMarked, Users, Shield, SplitSquareHorizontal,
  Map, Binoculars, Layers, Lock, Unlock, BarChart3, CheckCircle, Flame, Droplets,
} from 'lucide-react';
import { useLanguage } from '@/contexts/LanguageContext';
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger, DropdownMenuSeparator } from '@/components/ui/dropdown-menu';
import { Popover, PopoverTrigger, PopoverContent } from '@/components/ui/popover';
import { Switch } from '@/components/ui/switch';
import useBionicSession from '@/hooks/useBionicSession';
import useBionicLayers from '@/hooks/useBionicLayers';
import { TerritoireToolbar } from '@/components/territoire/ui/TerritoireToolbar';
import { InspectionBiologiquePanel } from '@/components/territoire/InspectionBiologiquePanel';
import { NutritionPanelOmega } from '@/components/territoire/NutritionPanelOmega';import { NutritionPanel } from '@/components/territoire/ui/NutritionPanel';
import { TerritoireDialogs } from '@/components/territoire/ui/TerritoireDialogs';
import useBionicWeather from '@/hooks/useBionicWeather';
import useSharedWeather from '@/hooks/useSharedWeather';
import useBionicScoring from '@/hooks/useBionicScoring';
import useBionicScoringV8 from '@/hooks/useBionicScoringV8';
import useMapBundleV8 from '@/hooks/useMapBundleV8';
import usePhaseAV8 from '@/hooks/usePhaseAV8';
import useBionicStore from '@/stores/useBionicStore';
import { enforceOverlayCompliance, enforcePositionLock, enforceRenderGuard, enforceLayoutFreeze } from '@/components/territoire/map/BCE4X_UIShield';
import { useUserData } from '@/hooks/useUserData';
import { useNotifications, useHuntingGroups } from '@/hooks/useSharing';
import WaypointUnifiedPanel from '@/components/territoire/WaypointUnifiedPanel';
import { useAuth } from '@/components/GlobalAuth';
import PlacesSidePanel from '@/components/territoire/PlacesSidePanel';
import WeatherPanel from '@/components/territoire/ui/WeatherPanel';
import useSpatialClipping from '@/hooks/useSpatialClipping';
import useCameraLayer from '@/hooks/useCameraLayer';
import useAlphaLayer from '@/hooks/useAlphaLayer';
import { BIONIC_MODULES } from '@/core/bionic';
import { SPECIES_LIST } from '@/core/bionic/speciesConfig';
import { useZoneOrchestrator } from '@/hooks/useZoneOrchestrator';
import { useZoneFavorites } from '@/components/territoire/ZoneFavorites';
// P2: EcologicalPanel — module gele (FROZEN)
import { 
  useEcoMapFallback,
} from '@/components/territoire/EcoforestryLayers';
// Import BIONIC Map Selector
import BionicMapSelector from '@/components/maps/BionicMapSelector';
import useMapType from '@/hooks/useMapType';
import { MAP_TYPES } from '@/config/mapSources';
import { BionicScoreBadge } from '@/components/territoire/BionicScoreBadge';

// P2: BIONIC_COLORS migrated to component-level CSS variables

// IM1 — Modules extraits
import { useGeolocation } from '@/hooks/useGeolocation';
import { useZoneToasts, useAmenagementEngine, useSnapshotExport, useCategoryScores } from '@/hooks/useTerritoireEffects';
import { PLACE_TYPES } from '@/config/placeTypes';
import { TerritoireHeader } from '@/components/territoire/ui/TerritoireHeader';
// IM1.2 — Modules extraits (Passe 2)
import { useWaypointActions } from '@/hooks/useWaypointActions';
import { MapContent } from '@/components/territoire/map/MapContent';
import BionicLegend from '@/components/territoire/BionicLegend';
import CacheStateOmega from '@/components/territoire/ui/CacheStateOmega';
import { TERRITOIRE_DEFAULTS } from '@/config/territoire_defaults';
// V8.1 — Saisons biologiques
import { BiologicalSeasonSelector } from '@/components/territoire/ui/BiologicalSeasonSelector';
import { getCurrentBiologicalSeason } from '@/config/biologicalSeasons';
// V8.1 — Split View
import { SplitViewContainer } from '@/components/territoire/map/SplitViewContainer';
import { useSplitViewZones } from '@/hooks/useSplitViewZones';

// Cle localStorage pour le dernier waypoint actif (legacy fallback)
const LAST_WAYPOINT_KEY = 'bionic_last_active_waypoint_id';

/**
 * BCE-4X: Point-in-polygon (ray casting) pour exclusion hydro
 * Vérifie si un point (lat, lng) est à l'intérieur d'un polygone
 */
function _pointInPolygon(lat, lng, polygon) {
  let inside = false;
  for (let i = 0, j = polygon.length - 1; i < polygon.length; j = i++) {
    const pi = polygon[i], pj = polygon[j];
    const piLat = Array.isArray(pi) ? pi[0] : (pi.lat || 0);
    const piLng = Array.isArray(pi) ? pi[1] : (pi.lng || pi.lon || 0);
    const pjLat = Array.isArray(pj) ? pj[0] : (pj.lat || 0);
    const pjLng = Array.isArray(pj) ? pj[1] : (pj.lng || pj.lon || 0);
    if (((piLng > lng) !== (pjLng > lng)) &&
        (lat < (pjLat - piLat) * (lng - piLng) / (pjLng - piLng) + piLat)) {
      inside = !inside;
    }
  }
  return inside;
}

const MonTerritoireBionicPage = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { t } = useLanguage();

  // ═══ HOTSPOT DEEP LINK — lecture des query params ═══
  const hotspotDeepLink = useRef({
    lat: searchParams.get('lat') ? parseFloat(searchParams.get('lat')) : null,
    lng: searchParams.get('lng') ? parseFloat(searchParams.get('lng')) : null,
    zoom: searchParams.get('zoom') ? parseInt(searchParams.get('zoom'), 10) : null,
    layer: searchParams.get('layer') || null,
    hotspotId: searchParams.get('hotspot') || null,
  });
  const deepLinkAppliedRef = useRef(false);
  
  // ============================================
  // BCE-MAX x4.1 — SESSION (SOURCE DE VERITE UNIQUE)
  // DOIT etre le PREMIER hook pour fournir l'etat initial a tout le reste
  // ============================================
  const {
    session: bionicSession,
    position: savedPosition,
    species: savedSpecies,
    layers: savedLayers,
    waypointId: savedWaypointId,
    biologicalSeason: savedBiologicalSeason,
    activeTab: savedActiveTab,
    classificationToggles: savedClassificationToggles,
    showCorridorsV1: savedShowCorridorsV1,
    showExclusionOverlay: savedShowExclusionOverlay,
    showWindFlow: savedShowWindFlow,
    windMode: savedWindMode,
    updatePosition,
    updateSpecies,
    updateLayers,
    updateWaypointId,
    updateBiologicalSeason,
    updateActiveTab,
    updateClassificationToggles,
    updateVisualOptions,
    hasPreviousSession,
  } = useBionicSession();
  
  // BIONIC V6 GOLDEN — Ref directe vers l'instance Leaflet map
  const mapRef = useRef(null);

  // ═══ HOTSPOT DEEP LINK — état du highlight ═══
  const [hotspotHighlight, setHotspotHighlight] = useState(null);
  const hotspotHighlightLayerRef = useRef(null);
  
  // Onglet actif — restaure depuis la session BCE-MAX
  const [activeTab, setActiveTab] = useState(savedActiveTab || 'carte');
  
  // Etat de la carte — restaure depuis la session BCE-MAX
  const [mapCenter, setMapCenter] = useState(
    savedPosition?.lat != null && savedPosition?.lng != null
      ? [savedPosition.lat, savedPosition.lng]
      : [46.8139, -71.2080]
  );
  const [mapZoom, setMapZoom] = useState(savedPosition?.zoom || 12);
  const [currentZoom, setCurrentZoom] = useState(savedPosition?.zoom || 12);
  const [currentMapCenter, setCurrentMapCenter] = useState(
    savedPosition?.lat != null
      ? { lat: savedPosition.lat, lng: savedPosition.lng }
      : { lat: 46.8139, lng: -71.2080 }
  );
  const [currentMapBounds, setCurrentMapBounds] = useState(null);
  
  // V8.1 — Saison biologique active (restauree depuis session BCE-MAX)
  const [selectedBiologicalSeason, setSelectedBiologicalSeason] = useState(() => savedBiologicalSeason || getCurrentBiologicalSeason().id);
  
  // BCE-MAX: Sync saison biologique vers session
  useEffect(() => {
    if (selectedBiologicalSeason) {
      updateBiologicalSeason(selectedBiologicalSeason);
    }
  }, [selectedBiologicalSeason, updateBiologicalSeason]);

  // BCE-4X-UI: Guards periodiques — PositionLock + RenderGuard + OverlayCompliance + LayoutFreeze
  useEffect(() => {
    const guardInterval = setInterval(() => {
      enforceOverlayCompliance();
      enforcePositionLock();
      enforceRenderGuard();
      enforceLayoutFreeze();
    }, 5000);
    // Execution immediate au montage
    enforceOverlayCompliance();
    enforceLayoutFreeze();
    return () => clearInterval(guardInterval);
  }, []);
  
  // V8.1 — Split View
  // V8.2 FIX: Capture du centre/zoom RÉEL de la carte au moment d'activer le SplitView
  // mapCenter/mapZoom sont les valeurs INITIALES (Québec City par défaut)
  // currentMapCenter/currentZoom sont les valeurs ACTUELLES (suivi en temps réel)
  const [splitViewEnabled, setSplitViewEnabled] = useState(false);

  // V8.2 FIX: Centre/zoom figés au moment de l'activation du Split View
  const [splitMapCenter, setSplitMapCenter] = useState(null);
  const [splitMapZoom, setSplitMapZoom] = useState(null);

  // V8.2 FIX: Handler d'activation du Split View — capture la position courante
  const toggleSplitView = useCallback(() => {
    setSplitViewEnabled(prev => {
      if (!prev) {
        // Activation: capturer la position RÉELLE de la carte principale
        if (mapRef.current) {
          const c = mapRef.current.getCenter();
          const z = mapRef.current.getZoom();
          setSplitMapCenter([c.lat, c.lng]);
          setSplitMapZoom(z);
        } else {
          setSplitMapCenter([currentMapCenter.lat, currentMapCenter.lng]);
          setSplitMapZoom(currentZoom);
        }
      } else {
        // P0 FIX: Désactivation — capturer position depuis split et mettre à jour
        // mapCenter/mapZoom pour que le nouveau MapContainer garde la même position
        if (mapRef.current) {
          const c = mapRef.current.getCenter();
          const z = mapRef.current.getZoom();
          setMapCenter([c.lat, c.lng]);
          setMapZoom(z);
        }
      }
      return !prev;
    });
  }, [currentMapCenter, currentZoom]);
  const [splitRightSeason, setSplitRightSeason] = useState('rut'); // Saison droite par défaut
  const [selectedZone, setSelectedZone] = useState(null);
  const [hoveredZone, setHoveredZone] = useState(null);
  const [showCorridorsV1, setShowCorridorsV1] = useState(savedShowCorridorsV1 ?? false);
  const [showExclusionOverlay, setShowExclusionOverlay] = useState(savedShowExclusionOverlay ?? false);
  const [showWindFlow, setShowWindFlow] = useState(TERRITOIRE_DEFAULTS.VENT); // ALWAYS-ON institutionnel
  const [showHydro, setShowHydro] = useState(true); // ORDONNANCE LEVEE: Hydrographie reactivee
  const [windMode, setWindMode] = useState(savedWindMode || 'arrows');
  const [temporalHourMT, setTemporalHourMT] = useState(null);
  const [contextMenuMT, setContextMenuMT] = useState(null);
  // BDRE-FIRST P1: BDRE score indicator on map
  const [bdreStatus, setBdreStatus] = useState(null);
  
  // Géolocalisation (hook extrait IM1)
  const { userPosition, setUserPosition, watchingPosition, startWatchingPosition, stopWatchingPosition, centerOnUser } = useGeolocation(mapRef);
  
  // P0 FIX: Use auth context for userId instead of broken localStorage read
  const { user: authUser, token: authToken } = useAuth();
  const userId = useMemo(() => {
    if (authUser?.id) return authUser.id;
    if (authUser?.email) return authUser.email;
    return 'anonymous';
  }, [authUser]);
  
  // Hook pour les waypoints et lieux avec sync backend
  const {
    waypoints,
    places: savedPlaces,
    activeWaypoints,
    stats: userDataStats,
    loading: userDataLoading,
    syncing,
    isOnline,
    addWaypoint,
    updateWaypoint,
    deleteWaypoint,
    toggleWaypointActive,
    addPlace,
    updatePlace,
    deletePlace,
    syncToBackend
  } = useUserData(userId, { autoSync: true });
  
  // CAM-LOC-Omega: Camera layer with 600m zone detection
  const { positionedCameras, allCameras: camerasList } = useCameraLayer(authToken, activeWaypoints, []);
  
  // ALPHA layer: hotspots from camera events
  const camerasLookup = useMemo(() => {
    const lookup = {};
    (camerasList || []).forEach(c => { lookup[c.id] = c; });
    return lookup;
  }, [camerasList]);
  const { alphaHotspots, trajectories: alphaTrajectories } = useAlphaLayer(authToken, camerasLookup);
  
  // IM1.2 — Hook actions waypoints/lieux (extrait)
  const {
    selectedWaypointForZones, setSelectedWaypointForZones,
    mapClickMode, setMapClickMode,
    showAddWaypointDialog, setShowAddWaypointDialog,
    newWaypoint, setNewWaypoint,
    showAddPlaceDialog, setShowAddPlaceDialog,
    newPlace, setNewPlace,
    editingPlace, setEditingPlace,
    showShareDialog, setShowShareDialog,
    waypointToShare, setWaypointToShare,
    selectWaypointAsTarget,
    clearWaypointTarget,
    handleDeleteWaypoint,
    handleAddWaypoint,
    handleAddWaypointFromDialog,
    handleMapClickForWaypoint,
    useCurrentPositionForNewWaypoint,
    useCurrentPositionForNewPlace,
    handleAddPlace,
    handleUpdatePlace,
    openShareDialog,
    bindReloadZones,
  } = useWaypointActions({
    mapRef,
    mapCenter,
    addWaypoint,
    deleteWaypoint,
    addPlace,
    updatePlace,
    userPosition,
    onClearAllMapData: () => {
      // x4600-R4: NETTOYAGE TOTAL — fermer TOUS les panneaux, vider TOUTES les données
      // Panneaux
      setSelectedStand(null);
      setSelectedNutritionPoint(null);
      setShowAmenagementPanel(false);
      setShowNutritionPanel(false);
      // Données de couches
      setHeatmapV10Data(null);
      setCorridorV10Data(null);
      setAlimentationV2Data(null);
      // x4600-R4: Nettoyage nucléaire Leaflet — supprimer TOUS les layers non-tile
      if (mapRef.current) {
        const map = mapRef.current;
        const layersToRemove = [];
        map.eachLayer((layer) => {
          // Conserver les TileLayers (fond de carte)
          if (layer._url || layer._tiles || layer.options?.attribution) return;
          layersToRemove.push(layer);
        });
        layersToRemove.forEach((layer) => {
          try { map.removeLayer(layer); } catch (e) { /* ignore */ }
        });
      }
    },
  });

  // BIONIC V6 GOLDEN INVARIANT: Spatial Clipping 1km × 1km (doit être après useWaypointActions)
  const { analysisBbox, bboxBounds, clipZonesClient, snapshotData, isGeneratingSnapshot, generateSnapshot, ANALYSIS_BOX_SIZE_M } = useSpatialClipping(selectedWaypointForZones);

  // BIONIC V6 GOLDEN — AUTO-SELECTION DU DERNIER WAYPOINT ACTIF
  // BCE-MAX x4.1: Priorite au waypointId de la session
  // PATCH 3D-RESTORE: Auto-select se relance si selectedWaypointForZones est perdu
  const autoSelectDoneRef = useRef(false);
  useLayoutEffect(() => {
    // Reset du ref si le waypoint est perdu — permet la re-selection
    if (!selectedWaypointForZones && autoSelectDoneRef.current) {
      autoSelectDoneRef.current = false;
    }
    if (autoSelectDoneRef.current) return;
    if (!selectedWaypointForZones && activeWaypoints.length > 0) {
      const lastId = savedWaypointId || localStorage.getItem(LAST_WAYPOINT_KEY);
      const lastWp = lastId ? activeWaypoints.find(wp => wp.id === lastId) : null;
      const target = lastWp || activeWaypoints[0];
      if (target && (target.lat || target.latitude)) {
        const source = lastWp ? 'session BCE-MAX' : 'premier actif (fallback)';
        console.log(`[BCE-MAX x4.1] Auto-select: "${target.name}" (${source})`);
        autoSelectDoneRef.current = true;
        setSelectedWaypointForZones(target);
        localStorage.setItem(LAST_WAYPOINT_KEY, target.id);
        updateWaypointId(target.id);
      }
    }
  }, [selectedWaypointForZones, activeWaypoints]);

  // BCE-MAX x4.1: CENTRAGE MAP depuis session persistante
  const initialCenterDoneRef = useRef(false);
  useEffect(() => {
    if (initialCenterDoneRef.current) return;
    if (!mapRef.current) return;

    // Priorite ABSOLUE: Deep link hotspot depuis Admin
    const dl = hotspotDeepLink.current;
    if (!deepLinkAppliedRef.current && dl.lat && dl.lng) {
      deepLinkAppliedRef.current = true;
      initialCenterDoneRef.current = true;
      const dlZoom = dl.zoom || 15;
      mapRef.current.setView([dl.lat, dl.lng], dlZoom);

      // Activer fond Satellite si demandé
      if (dl.layer === 'satellite') {
        setMapType(MAP_TYPES.SATELLITE);
      }

      // Highlight du hotspot — cercle ~2km² + marker
      setHotspotHighlight({ lat: dl.lat, lng: dl.lng, id: dl.hotspotId });

      console.log(`[DEEP-LINK] Hotspot ${dl.hotspotId}: [${dl.lat}, ${dl.lng}] zoom ${dlZoom} layer=${dl.layer}`);
      return;
    }

    // Priorite 1: Waypoint selectionne (territoire de chasse = priorite absolue)
    // ULTRA-MAX++: Le waypoint persiste doit TOUJOURS prendre priorite sur la
    // position de session pour eviter la contamination par la geolocalisation LIVE
    if (selectedWaypointForZones) {
      const lat = selectedWaypointForZones.lat || selectedWaypointForZones.latitude;
      const lng = selectedWaypointForZones.lng || selectedWaypointForZones.longitude;
      if (lat && lng) {
        initialCenterDoneRef.current = true;
        mapRef.current.setView([lat, lng], 14);
        console.log(`[BCE-MAX x4.1] Centrage WAYPOINT prioritaire: [${lat}, ${lng}] zoom 14`);
        return;
      }
    }

    // Priorite 2: Session BCE-MAX x4.1 (position de la derniere session — fallback)
    if (hasPreviousSession && savedPosition?.lat && savedPosition?.lng && savedPosition?.zoom) {
      initialCenterDoneRef.current = true;
      mapRef.current.setView([savedPosition.lat, savedPosition.lng], savedPosition.zoom);
      console.log(`[BCE-MAX x4.1] Session restauree (fallback): [${savedPosition.lat.toFixed(4)}, ${savedPosition.lng.toFixed(4)}] zoom ${savedPosition.zoom}`);
      return;
    }

    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedWaypointForZones?.id, hasPreviousSession, savedPosition]);

  // ═══ HOTSPOT DEEP LINK — Rendu du highlight sur la carte ═══
  useEffect(() => {
    if (!hotspotHighlight || !mapRef.current) return;

    // Nettoyer l'ancien layer
    if (hotspotHighlightLayerRef.current) {
      mapRef.current.removeLayer(hotspotHighlightLayerRef.current);
    }

    const group = L.layerGroup();

    // Cercle externe pulsant ~2km² (rayon 800m)
    L.circle([hotspotHighlight.lat, hotspotHighlight.lng], {
      radius: 800,
      color: '#f5a623',
      fillColor: '#f5a623',
      fillOpacity: 0.08,
      weight: 2,
      dashArray: '10,6',
      className: 'hotspot-highlight-pulse',
    }).addTo(group);

    // Cercle interne
    L.circle([hotspotHighlight.lat, hotspotHighlight.lng], {
      radius: 200,
      color: '#FF6F00',
      fillColor: '#FF6F00',
      fillOpacity: 0.15,
      weight: 2,
    }).addTo(group);

    // Marker central
    L.circleMarker([hotspotHighlight.lat, hotspotHighlight.lng], {
      radius: 8,
      color: '#fff',
      fillColor: '#f5a623',
      fillOpacity: 1,
      weight: 3,
    }).bindPopup(
      `<div style="font-family:system-ui;color:#e5e5e5;background:#1a1a2e;padding:10px;border-radius:8px;min-width:180px;">
        <div style="font-weight:800;font-size:13px;color:#f5a623;margin-bottom:4px;">Hotspot ${hotspotHighlight.id || ''}</div>
        <div style="font-size:11px;color:#aaa;">${hotspotHighlight.lat.toFixed(5)}, ${hotspotHighlight.lng.toFixed(5)}</div>
        <div style="margin-top:6px;font-size:10px;color:#888;">Zone de 2 km² — Fond Satellite</div>
      </div>`,
      { className: 'bionic-popup', maxWidth: 250 }
    ).openPopup().addTo(group);

    group.addTo(mapRef.current);
    hotspotHighlightLayerRef.current = group;

    return () => {
      if (hotspotHighlightLayerRef.current && mapRef.current) {
        try { mapRef.current.removeLayer(hotspotHighlightLayerRef.current); } catch (e) {}
      }
    };
  }, [hotspotHighlight]);

  // BCE-MAX x4.1: Sauvegarde automatique UNIFIEE du contexte utilisateur
  const contextSaveTimerRef = useRef(null);
  useEffect(() => {
    if (contextSaveTimerRef.current) clearTimeout(contextSaveTimerRef.current);
    contextSaveTimerRef.current = setTimeout(() => {
      // Position carte
      if (currentMapCenter.lat && currentMapCenter.lng && currentZoom) {
        updatePosition(currentMapCenter.lat, currentMapCenter.lng, currentZoom);
      }
      // Waypoint
      if (selectedWaypointForZones?.id) {
        updateWaypointId(selectedWaypointForZones.id);
      }
      // Onglet
      updateActiveTab(activeTab);
      // Options visuelles
      updateVisualOptions({
        showCorridorsV1,
        showExclusionOverlay,
        showWindFlow,
        windMode,
      });
    }, 500);
    return () => { if (contextSaveTimerRef.current) clearTimeout(contextSaveTimerRef.current); };
  }, [currentMapCenter.lat, currentMapCenter.lng, currentZoom, selectedWaypointForZones?.id, activeTab, showCorridorsV1, showExclusionOverlay, showWindFlow, windMode, updatePosition, updateWaypointId, updateActiveTab, updateVisualOptions]);

  
  // Notifications
  const { notifications, unreadCount, markAsRead, markAllAsRead } = useNotifications(userId);

  // BDRE-FIRST P1: Fetch BDRE status for map indicator
  const BACKEND = process.env.REACT_APP_BACKEND_URL;
  useEffect(() => {
    const fetchBdre = async () => {
      try {
        const [dashRes, srcRes] = await Promise.all([
          fetch(`${BACKEND}/api/v1/bdre/dashboard`).then(r => r.json()),
          fetch(`${BACKEND}/api/v1/bdre/sources`).then(r => r.json()),
        ]);
        setBdreStatus({
          version: dashRes.bdre_version,
          totalSources: dashRes.sources?.total || 0,
          healthy: dashRes.sources?.by_status?.healthy || 0,
          notConnected: dashRes.sources?.by_status?.not_connected || 0,
          fallbacks: dashRes.audit_stats?.total_fallbacks || 0,
          alerts: dashRes.audit_stats?.total_alerts || 0,
          sources: srcRes.sources || [],
        });
      } catch { /* silent */ }
    };
    fetchBdre();
    const interval = setInterval(fetchBdre, 30000);
    return () => clearInterval(interval);
  }, [BACKEND]);
  
  // Groupes de chasse
  const { allGroups: myGroups, loading: groupsLoading, refresh: refreshGroups } = useHuntingGroups(userId);
  
  // Dialog de partage
  const [showCreateGroupDialog, setShowCreateGroupDialog] = useState(false);
  const [showNotificationsPanel, setShowNotificationsPanel] = useState(false);
  
  // Tableau de bord de groupe (tracking live + chat)
  const [showGroupDashboard, setShowGroupDashboard] = useState(false);
  const [selectedGroup, setSelectedGroup] = useState(null);
  
  // PHASE-FRONTEND-Omega V2: Groupe tracking module purge.
  // ZERO panneau lateral Groupe. ZERO tracking persistant dans Territoire.
  const groupMembersPositions = [];
  const isGroupeTrackingActive = false;
  
  // Panneaux
  const [showLayersPanel, setShowLayersPanel] = useState(true);
  const [showCursorBionic, setShowCursorBionic] = useState(TERRITOIRE_DEFAULTS.CURSEUR);
  
  // ============================================
  // CARTE PREMIUM BIONIC - Sélecteur de type de carte
  // ============================================
  const { 
    mapType, 
    setMapType, 
    mapOptions, 
    setMapOptions, 
    tileUrl, 
    attribution,
    isDarkOptimized,
    getZoneOpacityForCurrentMap
  } = useMapType(MAP_TYPES.SATELLITE);
  
  // Mode d'affichage des zones BIONIC
  const [zoneDisplayMode, setZoneDisplayMode] = useState('micro'); // 'micro' ou 'classic'
  const showCorridors = true; // STEEVE-MAX: V6 layer permanent, contrôlé uniquement via ZONES
  const [corridorV10Data, setCorridorV10Data] = useState(null); // CORRIDORS-V10 niveau distribution
  const [minPercentageFilter, setMinPercentageFilter] = useState(30);
  
  // STEEVE-MAX UX: Controles couches et points chauds — MAP-LAYERS-Omega ALWAYS_ON
  // DEFAULTS-Omega: single source of truth (frontend/src/config/territoire_defaults.js)
  const [showZonesLayer, setShowZonesLayer] = useState(TERRITOIRE_DEFAULTS.ZONES);
  const [showCorridorsLayer, setShowCorridorsLayer] = useState(TERRITOIRE_DEFAULTS.CORRIDORS);
  const [showPointsLayer, setShowPointsLayer] = useState(TERRITOIRE_DEFAULTS.AFFUTS);
  const [pointsChaudsMode, setPointsChaudsMode] = useState(false);
  const [pointsChaudsFilter, setPointsChaudsFilter] = useState('tous');

  // MAP-LAYERS-Omega: PHASE-FRONTEND-Omega V2 — HEARTBEAT PURGE
  // Les couches respectent l'etat strict ON/OFF des boutons presseurs.
  // ZERO reactivation automatique. ZERO persistance forcee.

  // ALIMENTATION-V2: Points nutritionnels + Recommandations
  const [showAlimentationV2, setShowAlimentationV2] = useState(true);
  // NUTRITION_BY_SALINE_ONLY actif — la directive interdit toute couche nutrition autonome.
  // PHASE_NUTRITION_SALINES_BINDING_Ω : le rendu se fait uniquement via dblclick saline.
  const [showNutritionPoints, setShowNutritionPoints] = useState(false);
  const [showNutritionPanel, setShowNutritionPanel] = useState(false);
  const [showAmenagementPanel, setShowAmenagementPanel] = useState(false);
  const [selectedStand, setSelectedStand] = useState(null);
  const [selectedNutritionPoint, setSelectedNutritionPoint] = useState(null);
  const [alimentationV2Data, setAlimentationV2Data] = useState(null);
  const [nNutritionPointsMax, setNNutritionPointsMax] = useState(2);

  // BCE-4X P0 A1: Deriver feedingSites depuis alimentationV2Data pour StandsMapLayer
  const feedingSitesForStands = useMemo(() => {
    if (!alimentationV2Data?.salines) return [];
    return alimentationV2Data.salines
      .filter(s => s.selected)
      .map(s => ({ lat: s.lat, lng: s.lng, name: s.id || s.type || 'Alimentation' }));
  }, [alimentationV2Data]);

  // BCE-4X P0 A2: Deriver fixedBlinds depuis savedPlaces type 'affut' pour StandsMapLayer
  const fixedBlindsForStands = useMemo(() => {
    if (!savedPlaces?.length) return [];
    return savedPlaces
      .filter(p => p.type === 'affut')
      .map(p => ({ lat: p.lat, lng: p.lng, name: p.name || 'Affut fixe', type_key: 'tree_stand', id: p.id }));
  }, [savedPlaces]);

  const [adminArchitecteMode, setAdminArchitecteMode] = useState(false);
  const [showHeatmapV10, setShowHeatmapV10] = useState(TERRITOIRE_DEFAULTS.HOTSPOTS);
  const [heatmapV10Data, setHeatmapV10Data] = useState(null);
  const [heatmapIncludeCorridors, setHeatmapIncludeCorridors] = useState(true);

  // STABILITÉ V2: Centre memoizé pour éviter re-render cascade dans les layers enfants
  const waypointCenter = useMemo(() => {
    if (!selectedWaypointForZones) return null;
    return {
      lat: selectedWaypointForZones.lat || selectedWaypointForZones.latitude,
      lng: selectedWaypointForZones.lng || selectedWaypointForZones.longitude,
    };
  }, [selectedWaypointForZones?.lat, selectedWaypointForZones?.lng, selectedWaypointForZones?.latitude, selectedWaypointForZones?.longitude]);

  // ═══ BCE-4X V8-INTEGRATION-Omega: Score V8 National ═══
  const {
    scoreV8, biomeProfile, loading: scoreV8Loading, fetchScoreV8,
  } = useBionicScoringV8();

  // ═══ UI-V8-FORCE-Omega: Bundle V8 unique (zones+corridors+heatmap) ═══
  const {
    bundleData: bundleDataV8, loading: bundleV8Loading, fetchBundle: fetchBundleV8,
    cacheState: bundleCacheState, servedMs: bundleServedMs, computeMs: bundleComputeMs,
  } = useMapBundleV8();

  // ═══ V8-FRONTEND-PHASE-A-Omega: Relocalisation + Salines ═══
  const {
    relocData: phaseARelocData, salinesData: phaseASalinesData,
    loading: phaseALoading, error: phaseAError, fetchPhaseA,
    relocalisations: phaseARelocalisations, siteActuel: phaseASiteActuel,
    salines: phaseASalines,
  } = usePhaseAV8();
  // ALWAYS-ON-Omega: SALINES + CONTAMINATION toujours visibles par defaut (toutes especes)
  // Directive SALINES_ALWAYS_ON=true + CONTAM_ALWAYS_ON=true. Boutons toggleables.
  const [showPhaseA, setShowPhaseA] = useState(TERRITOIRE_DEFAULTS.SALINES);
  const [showPhaseC, setShowPhaseC] = useState(TERRITOIRE_DEFAULTS.CONTAMINATION);
  // PHASE-FRONTEND-Omega V2: Couche INTEL-Omega (master institutionnel)
  const [showIntelLayer, setShowIntelLayer] = useState(TERRITOIRE_DEFAULTS.INTEL);
  // MODE INSPECTION BIOLOGIQUE PRO/EXPERT — panneau institutionnel flottant
  const [showInspectionBioPanel, setShowInspectionBioPanel] = useState(false);
  // PHASE_NUTRITION_SALINES_BINDING_Ω — panneau nutritionnel au dblclick saline
  const [nutritionPanelPayload, setNutritionPanelPayload] = useState(null);

  // STEEVE-MAX V3: Sous-éléments granulaires par couche
  const [zoneSubFilters, setZoneSubFilters] = useState({
    alimentation: true, repos: true, rut: true, affuts: true, eau: true,
  });
  const [corridorSubFilters, setCorridorSubFilters] = useState({
    normaux: true, intenses: true, extreme: true, saisonniers: true,
  });
  const [pointSubFilters, setPointSubFilters] = useState({
    alimentation: true, rut: true, repos: true, affuts: true, centroides: true, individuels: true,
  });
  const toggleZoneSub = (k) => setZoneSubFilters(p => ({ ...p, [k]: !p[k] }));
  // MAP-FIX-Omega-V3: showHydro lie au toggle Eau de la toolbar
  const effectiveShowHydro = showHydro && (zoneSubFilters?.eau !== false);
  const toggleCorridorSub = (k) => setCorridorSubFilters(p => ({ ...p, [k]: !p[k] }));
  const togglePointSub = (k) => setPointSubFilters(p => ({ ...p, [k]: !p[k] }));
  
  // BIONIC V6 GOLDEN — CLASSIFICATION TOGGLES (restaures depuis session BCE-MAX)
  const [classificationToggles, setClassificationToggles] = useState(() => {
    if (savedClassificationToggles && typeof savedClassificationToggles === 'object') {
      return savedClassificationToggles;
    }
    return {
      relief: true,
      hydro: true,
      foret: true,
      anthropique: true,
      dominantes: true,
      corridorsReels: true,
      meteo: true,
      corridorsEstimes: true,
      scoreHabitat: true,
      curseurBionic: true,
      waypoints: true,
    };
  });
  const handleClassificationToggle = useCallback((key) => {
    setClassificationToggles(prev => {
      const updated = { ...prev, [key]: !prev[key] };
      updateClassificationToggles(updated);
      return updated;
    });
  }, [updateClassificationToggles]);
  
  // ============================================
  // BCE-MAX x4.1 — Espece selectionnee (restauree depuis session)
  // ============================================
  const [selectedSpecies, setSelectedSpecies] = useState(() => savedSpecies || 'tous');
  
  // Synchroniser l'espece avec la session
  useEffect(() => {
    if (selectedSpecies) {
      updateSpecies(selectedSpecies);
    }
  }, [selectedSpecies, updateSpecies]);

  // ═══ BCE-4X V8: Fetch automatique Score V8 quand position ou espece change ═══
  useEffect(() => {
    const lat = waypointCenter?.lat || currentMapCenter?.lat;
    const lng = waypointCenter?.lng || currentMapCenter?.lng;
    if (lat && lng) {
      const sp = selectedSpecies === 'tous' ? 'cerf' : selectedSpecies;
      fetchScoreV8(lat, lng, sp);
      const windDeg = windInfo?.directionDeg || 225;
      fetchBundleV8(lat, lng, sp, undefined, undefined, windDeg);
    }
  }, [waypointCenter?.lat, waypointCenter?.lng, currentMapCenter?.lat, currentMapCenter?.lng, selectedSpecies, fetchScoreV8, fetchBundleV8]);
  
  // Les exclusions sont gérées 100% backend. Ces variables sont gardées pour compatibilité UI.
  const terrainExclusions = [];
  const isLoadingExclusions = false;
  
  // ============================================
  // CARTE ÉCOFORESTIÈRE - État des couches
  // ============================================
  const [activeEcoLayers, setActiveEcoLayers] = useState({
    baseMap: 'satellite_hd',
    peuplements: false,
    essences: false,
    perturbations: false,
    densite: false,
    hauteur: false,
    lidar_chm: false,
    lidar_volume: false,
    lidar_st: false,
    courbes_niveau: false,
  });
  const [ecoLayerOpacities, setEcoLayerOpacities] = useState({});
  
  // Synchroniser le type de carte avec activeEcoLayers.baseMap
  useEffect(() => {
    // Mapper les types de carte BIONIC aux baseMap du système existant
    const mapTypeToBaseMap = {
      'ecoforestry': 'ecoforestry',
      'ecoforestry': 'ecoforestry',
      'satellite': 'satellite_hd',
      'iqho': 'iqho',
      'forest-roads': 'forest-roads'
    };
    
    const newBaseMap = mapTypeToBaseMap[mapType] || 'terrain';
    setActiveEcoLayers(prev => ({ ...prev, baseMap: newBaseMap }));
  }, [mapType]);
  
  // ============================================
  // SYSTÈME DE FALLBACK - Carte écoforestière
  // ============================================
  const isEcoMapSelected = activeEcoLayers.baseMap === 'ecoforestry';
  const {
    status: ecoMapStatus,
    activeFallback,
    retryCount,
    lastCheck,
    isAvailable: isEcoMapAvailable,
    isUnavailable: isEcoMapUnavailable,
    forceCheck: forceEcoMapCheck,
    setFallbackMap
  } = useEcoMapFallback(isEcoMapSelected);
  
  // Gestionnaire de toggle des couches écoforestières
  const handleEcoLayerToggle = useCallback((layerId, value) => {
    if (layerId === 'baseMap') {
      setActiveEcoLayers(prev => ({ ...prev, baseMap: value }));
    } else {
      setActiveEcoLayers(prev => ({ ...prev, [layerId]: !prev[layerId] }));
    }
  }, []);
  
  // Gestionnaire d'opacité des couches
  const handleEcoOpacityChange = useCallback((layerId, opacity) => {
    setEcoLayerOpacities(prev => ({ ...prev, [layerId]: opacity }));
  }, []);
  
  // V8.3.A: Popover Carte — mode contrôlé pour fermeture auto après sélection
  const [cartePopoverOpen, setCartePopoverOpen] = useState(false);
  const handleMapTypeChangeAndClose = useCallback((type) => {
    setMapType(type);
    setCartePopoverOpen(false);
  }, [setMapType]);

  // V8.3.A: Compare Widget — sélection multi-waypoints
  const [compareSelection, setCompareSelection] = useState([]); // IDs des waypoints sélectionnés
  const [showCompareWidget, setShowCompareWidget] = useState(false);

  const handleToggleCompare = useCallback((wp) => {
    setCompareSelection(prev => {
      const exists = prev.find(w => w.id === wp.id);
      if (exists) return prev.filter(w => w.id !== wp.id);
      if (prev.length >= 3) return prev; // max 3
      return [...prev, wp];
    });
  }, []);

  const handleLaunchCompare = useCallback(() => {
    if (compareSelection.length >= 2) {
      setShowCompareWidget(true);
    }
  }, [compareSelection]);

  const handleCloseCompare = useCallback(() => {
    setShowCompareWidget(false);
  }, []);

  // V8.3.A: Auto-activation mode Particules lors de l'ajout d'un waypoint
  const handleAddWaypointWithWind = useCallback(() => {
    handleAddWaypointFromDialog();
    // Activer automatiquement le vent en mode particules
    setShowWindFlow(true);
    setWindMode('particles');
  }, [handleAddWaypointFromDialog]);

  // Mode confidentialité (seul l'utilisateur et l'admin peuvent voir les données privées)
  const [privacyMode, setPrivacyMode] = useState(false);
  const isPrivateDataVisible = !privacyMode; // Les waypoints, recherches, annotations sont visibles
  
  // ============================================
  // Hooks BIONIC — couches (initialisees depuis session BCE-MAX)
  const { 
    layersVisible, 
    toggleLayer, 
    showAllLayers, 
    hideAllLayers,
    activeCount,
    allLayers,
  } = useBionicLayers(savedLayers);
  
  // Synchroniser les couches avec la session BCE-MAX
  useEffect(() => {
    if (layersVisible && Object.keys(layersVisible).length > 0) {
      updateLayers(layersVisible);
    }
  }, [layersVisible, updateLayers]);
  
  // BCE-4X Phase 3.1: Coordonnées METEO = waypoint UNIQUE de l'usager
  // ZERO fallback sur mapCenter, position GPS, ou coordonnées par défaut
  const weatherCoords = useMemo(() => {
    if (selectedWaypointForZones) {
      const lat = selectedWaypointForZones.lat ?? selectedWaypointForZones.latitude;
      const lng = selectedWaypointForZones.lng ?? selectedWaypointForZones.longitude;
      if (lat && lng) return [lat, lng];
    }
    // Fallback: premier waypoint actif
    if (activeWaypoints.length > 0) {
      const wp = activeWaypoints[0];
      const lat = wp.lat ?? wp.latitude;
      const lng = wp.lng ?? wp.longitude;
      if (lat && lng) return [lat, lng];
    }
    // Dernier recours: mapCenter (identique au default Québec si aucun waypoint)
    return mapCenter;
  }, [selectedWaypointForZones, activeWaypoints, mapCenter]);

  const { 
    weather, 
    isLoading: weatherLoading,
    temperature,
    windInfo,
    thermalInfo,
    huntingScore,
    nextOptimalWindow,
    sunrise,
    sunset,
    refresh: refreshWeather
  } = useBionicWeather(weatherCoords[0], weatherCoords[1], { autoFetch: true, pollInterval: 600000 });

  // BCE-4X Phase 3.1: Hook meteo partage — waypoint UNIQUE pour le bloc meteo intelligent
  const sharedWeather = useSharedWeather(weatherCoords[0], weatherCoords[1], { autoFetch: true });
  
  const { scores, calculateHybridScores, globalScore } = useBionicScoring();

  // ═══ V8-PHASE-A: Fetch Relocalisation+Salines quand Phase A active + position change ═══
  useEffect(() => {
    if (!showPhaseA) return;
    const lat = waypointCenter?.lat || currentMapCenter?.lat;
    const lng = waypointCenter?.lng || currentMapCenter?.lng;
    if (lat && lng) {
      const sp = selectedSpecies === 'tous' ? 'cerf' : selectedSpecies;
      const windDeg = windInfo?.directionDeg || 180;
      fetchPhaseA(lat, lng, sp, undefined, windDeg);
    }
  }, [showPhaseA, waypointCenter?.lat, waypointCenter?.lng, currentMapCenter?.lat, currentMapCenter?.lng, selectedSpecies, windInfo?.directionDeg, fetchPhaseA]);
  
  // Hook pour les zones favorites et alertes
  const {
    favorites,
    alerts,
    unreadAlertCount,
    loading: favoritesLoading,
    addFavorite,
    removeFavorite,
    updateAlertSettings,
    markAlertRead,
    markAllAlertsRead,
    checkOptimalConditions,
    getZoneConditions,
    refresh: refreshFavorites
  } = useZoneFavorites(userId);
  
  // Vérifier si une zone est favorite
  const isZoneFavorite = useCallback((zone) => {
    return favorites.some(f => 
      Math.abs(f.location.lat - zone.center[0]) < 0.0001 &&
      Math.abs(f.location.lng - zone.center[1]) < 0.0001 &&
      f.module_id === zone.moduleId
    );
  }, [favorites]);
  
  // Trouver l'ID du favori pour une zone
  const getFavoriteId = useCallback((zone) => {
    const fav = favorites.find(f => 
      Math.abs(f.location.lat - zone.center[0]) < 0.0001 &&
      Math.abs(f.location.lng - zone.center[1]) < 0.0001 &&
      f.module_id === zone.moduleId
    );
    return fav?.id;
  }, [favorites]);
  
  // Callback pour le changement de zoom
  const handleZoomChange = useCallback((newZoom) => {
    setCurrentZoom(newZoom);
  }, []);
  
  // Callback pour le déplacement de la carte
  const handleMapMove = useCallback((newCenter) => {
    setCurrentMapCenter(newCenter);
  }, []);
  
  // Callback pour le changement des limites visibles
  const handleBoundsChange = useCallback((newBounds) => {
    setCurrentMapBounds(newBounds);
  }, []);
  
  // ============================================
  // BIONIC V6 GOLDEN — PIPELINE WAYPOINT EXCLUSIF + ORCHESTRATEUR DE ZONES
  // 
  // Architecture modulaire stricte:
  //   1. useZoneOrchestrator: orchestration (cache → backend)
  //   2. useZoneCache: cache IndexedDB persistant (<100ms)
  //   3. generateWaypointZonesV5: calcul backend complet (~11s)
  //
  // Flux: Waypoint → Cache? → Loader → Backend (définitif) → Verrouillage
  // Zéro connexion croisée. Zéro bavure. Contrats explicites.
  // ============================================
  const {
    zonesData: bionicZonesData,
    isLoading: isLoadingZones,
    zoneSource,
    zeroZonesReason,
    pipelineState,
    reload: reloadZones,
    cacheKey: zoneLockKey,
    weatherMetadata,
  } = useZoneOrchestrator({
    selectedWaypointForZones,
    activeWaypoints,
    selectedSpecies,
    currentZoom,
    biologicalSeason: selectedBiologicalSeason,
  });

  // IM1.2: Late-bind reloadZones dans useWaypointActions
  useEffect(() => { bindReloadZones(reloadZones); }, [reloadZones, bindReloadZones]);

  // V8.1: Zones de la carte droite (Split View)
  const { zonesData: splitRightZonesData, isLoading: isSplitRightLoading } = useSplitViewZones({
    enabled: splitViewEnabled,
    selectedWaypointForZones,
    activeWaypoints,
    selectedSpecies,
    currentZoom,
    biologicalSeason: splitRightSeason,
  });

  // Zone notifications + T4 coherence (extrait -> useTerritoireEffects)
  useZoneToasts(zeroZonesReason, isLoadingZones, bionicZonesData);

  // ============================================
  // BIONIC V6 GOLDEN — SPATIAL CLIPPING + STATE LOCKING
  // 1. Les zones sont calculées pour TOUTES les couches structurelles
  // 2. Le clipping 1km × 1km est appliqué quand un waypoint est actif
  // 3. La visibilité est appliquée au RENDU, pas au calcul
  // ============================================
  const rawZones = useMemo(() => {
    const zones = bionicZonesData?.zones || [];
    // BCE-4X: Séparer les zones hydro pour le masque d'exclusion
    const hydroZones = zones.filter(z => z.layerId === 'hydro');
    const nonHydroZones = zones.filter(z => z.layerId !== 'hydro');

    // BCE-4X: Exclure les affuts et points nutritionnels dont le centroide tombe dans une zone hydro
    // Un affut ne peut PAS etre sur une surface d'eau
    if (hydroZones.length === 0) return nonHydroZones;

    const STRICT_EXCL_LAYERS = new Set(['affuts', 'salines', 'trajets']);

    return nonHydroZones.filter(z => {
      if (!STRICT_EXCL_LAYERS.has(z.layerId)) return true;
      if (!z.positions || z.positions.length === 0) return true;

      // Calculer le centroïde de la zone
      const flat = z.positions.flat ? z.positions.flat() : z.positions;
      if (flat.length === 0) return true;
      let cLat = 0, cLng = 0, count = 0;
      for (const pt of flat) {
        if (Array.isArray(pt) && pt.length >= 2) { cLat += pt[0]; cLng += pt[1]; count++; }
        else if (pt && pt.lat !== undefined) { cLat += pt.lat; cLng += (pt.lng || pt.lon); count++; }
      }
      if (count === 0) return true;
      cLat /= count; cLng /= count;

      // Vérifier si le centroïde est à l'intérieur d'une zone hydro (ray-casting simplifié)
      for (const hydro of hydroZones) {
        if (!hydro.positions || hydro.positions.length === 0) continue;
        const hFlat = hydro.positions.flat ? hydro.positions.flat() : hydro.positions;
        if (_pointInPolygon(cLat, cLng, hFlat)) {
          console.warn(`[BCE-4X] Zone ${z.layerId} exclue: centroïde sur eau [${cLat.toFixed(5)}, ${cLng.toFixed(5)}]`);
          return false;
        }
      }
      return true;
    });
  }, [bionicZonesData?.zones]);
  const bionicStats = useMemo(() => bionicZonesData?.stats || {}, [bionicZonesData?.stats]);
  
  // SPATIAL CLIPPING: Appliquer le clipping 1km × 1km si un waypoint est sélectionné
  const allZones = useMemo(() => {
    if (!selectedWaypointForZones || !analysisBbox) return rawZones;
    return clipZonesClient(rawZones);
  }, [rawZones, selectedWaypointForZones, analysisBbox, clipZonesClient]);
  
  // STATE LOCKING + CLASSIFICATION: Filtrer les zones par visibilité (rendu uniquement, pas recalcul)
  // Les zones restent en mémoire (orchestrateur) même si une famille Classification est OFF.
  const bionicZones = useMemo(() => {
    const RELIEF_LAYERS = new Set(['altitude', 'pentes', 'orientation', 'ensoleillement']);
    const HYDRO_LAYERS = new Set(['hydro']);
    const FORET_LAYERS = new Set(['peuplements', 'ndvi']);
    const DOMINANT_LAYERS = new Set(['rut', 'repos', 'alimentation', 'salines', 'affuts', 'corridors']);
    
    return allZones.filter(z => {
      if (layersVisible[z.layerId] === false) return false;
      if (!classificationToggles.relief && RELIEF_LAYERS.has(z.layerId)) return false;
      // BCE-4X x7200: Zones hydro controlees par classificationToggles.hydro + zoneSubFilters.eau
      if (HYDRO_LAYERS.has(z.layerId) && !classificationToggles.hydro) return false;
      if (!classificationToggles.foret && FORET_LAYERS.has(z.layerId)) return false;
      if (!classificationToggles.dominantes && DOMINANT_LAYERS.has(z.layerId)) return false;
      return true;
    });
  }, [allZones, layersVisible, classificationToggles]);
  
  // Compter les zones visibles
  const visibleZonesCount = useMemo(() => {
    return bionicZones.filter(z => z.score >= minPercentageFilter).length;
  }, [bionicZones, minPercentageFilter]);
  
  // Score global V9 — BCE-4X P0: Score TOUJOURS disponible
  // Sources: 1. globalScore (hook scoring) 2. bionicZones (orchestrateur) 3. heatmapV10Data (moteur heatmap) 4. bionicStats
  const displayScore = useMemo(() => {
    // BCE-4X-MAX INVARIANT SCORE=0ELEMENT:
    // Si aucune zone ET aucun corridor ET heatmap meta-exclu ou vide -> null (ZERO score)
    const corridors = bionicZonesData?.corridors || [];
    const hasZones = bionicZones.length > 0;
    const hasCorridors = corridors.length > 0;
    const heatmapExcluded = heatmapV10Data?.meta_excluded === true;
    const heatmapEmpty = !heatmapV10Data?.score_avg || heatmapV10Data.score_avg === 0;

    // Si ZERO element BIONIC genere, ZERO score affiche
    if (!hasZones && !hasCorridors && (heatmapExcluded || heatmapEmpty)) {
      return null;
    }

    if (globalScore) return globalScore;
    
    let zoneAvg = 0;
    if (hasZones) {
      const validScores = bionicZones.map(z => z.score || 0).filter(s => s > 0);
      if (validScores.length > 0) {
        zoneAvg = validScores.reduce((a, b) => a + b, 0) / validScores.length;
      }
    }
    
    let corridorAvg = 0;
    if (hasCorridors) {
      const corridorScores = corridors.map(c => c.score || 0).filter(s => s > 0);
      if (corridorScores.length > 0) {
        corridorAvg = corridorScores.reduce((a, b) => a + b, 0) / corridorScores.length;
      }
    }
    
    if (zoneAvg > 0 || corridorAvg > 0) {
      if (corridorAvg === 0) return Math.round(zoneAvg);
      if (zoneAvg === 0) return Math.round(corridorAvg);
      return Math.round(zoneAvg * 0.65 + corridorAvg * 0.35);
    }
    
    // Fallbacks: seulement si heatmap non exclu
    if (!heatmapExcluded && heatmapV10Data?.score_avg > 0) {
      return Math.round(heatmapV10Data.score_avg);
    }
    
    if (bionicStats?.score_global > 0) {
      return Math.round(bionicStats.score_global);
    }
    
    return null;
  }, [globalScore, bionicZones, bionicZonesData?.corridors, heatmapV10Data, bionicStats]);
  
  const getScoreRating = (score) => {
    if (!score) return { label: 'En attente', color: 'bg-gray-700', textColor: 'text-gray-400', ringColor: '#6B7280' };
    if (score >= 85) return { label: 'Exceptionnel', color: 'bg-green-500', textColor: 'text-green-400', ringColor: '#22C55E' };
    if (score >= 70) return { label: 'Excellent', color: 'bg-lime-500', textColor: 'text-lime-400', ringColor: '#84CC16' };
    if (score >= 55) return { label: 'Bon', color: 'bg-yellow-500', textColor: 'text-yellow-400', ringColor: '#EAB308' };
    return { label: 'Modéré', color: 'bg-orange-500', textColor: 'text-orange-400', ringColor: '#F97316' };
  };
  
  const rating = getScoreRating(displayScore);

  // BCE-4X: Propager le score dans useBionicStore pour le header
  const setDisplayScoreStore = useBionicStore(s => s.setDisplayScore);
  React.useEffect(() => {
    if (displayScore != null) {
      const r = getScoreRating(displayScore);
      setDisplayScoreStore(displayScore, r);
    }
  }, [displayScore, setDisplayScoreStore]); // eslint-disable-line react-hooks/exhaustive-deps

  // Amenagement engine + hunting path (extrait -> useTerritoireEffects)
  const { huntingPathData, amenagementReport, showHuntingPath } = useAmenagementEngine(bionicZones, selectedWaypointForZones, bionicZonesData);

  // Snapshot export (extrait -> useTerritoireEffects)
  const handleGenerateSnapshot = useSnapshotExport(selectedWaypointForZones, generateSnapshot, selectedSpecies, layersVisible, temporalHourMT, currentZoom);

  // Category scores (extrait -> useTerritoireEffects)
  const categoryScores = useCategoryScores(scores, currentMapCenter);

  return (
    <div className="fixed inset-0 bg-[#0a0a0f] overflow-hidden flex flex-col" style={{ paddingTop: '136px' }} data-testid="mon-territoire-bionic-page">
      {/* ═══ SECTION 1 — HEADER (composant extrait IM1) ═══ */}
      <TerritoireHeader
        navigate={navigate}
        selectedWaypointForZones={selectedWaypointForZones}
        mapClickMode={mapClickMode}
        setMapClickMode={setMapClickMode}
        setShowAddWaypointDialog={setShowAddWaypointDialog}
        onClearWaypoint={clearWaypointTarget}
        onDeleteWaypoint={handleDeleteWaypoint}
        sharedWeather={sharedWeather}
        scoreV8={scoreV8}
        biomeProfile={biomeProfile}
        scoreV8Loading={scoreV8Loading}
        onCenterWaypoint={() => {
          if (selectedWaypointForZones && mapRef.current) {
            mapRef.current.setView([selectedWaypointForZones.lat, selectedWaypointForZones.lng], 14);
          }
        }}
      />

      {/* ════════════════════════════════════════════════════════════════
          P0 UX — TOOLBAR UNIFIEE (composant extrait STEEVE-MAX P0)
          ════════════════════════════════════════════════════════════════ */}
      <TerritoireToolbar
        activeTab={activeTab} setActiveTab={setActiveTab}
        splitViewEnabled={splitViewEnabled} toggleSplitView={toggleSplitView}
        selectedBiologicalSeason={selectedBiologicalSeason} setSelectedBiologicalSeason={setSelectedBiologicalSeason}
        selectedSpecies={selectedSpecies} setSelectedSpecies={setSelectedSpecies}
        mapType={mapType} mapOptions={mapOptions} setMapOptions={setMapOptions}
        cartePopoverOpen={cartePopoverOpen} setCartePopoverOpen={setCartePopoverOpen}
        handleMapTypeChangeAndClose={handleMapTypeChangeAndClose}
        showZonesLayer={showZonesLayer} setShowZonesLayer={setShowZonesLayer}
        showCorridorsLayer={showCorridorsLayer} setShowCorridorsLayer={setShowCorridorsLayer}
        showPointsLayer={showPointsLayer} setShowPointsLayer={setShowPointsLayer}
        zoneSubFilters={zoneSubFilters} toggleZoneSub={toggleZoneSub}
        corridorSubFilters={corridorSubFilters} toggleCorridorSub={toggleCorridorSub}
        pointSubFilters={pointSubFilters} togglePointSub={togglePointSub}
        showWindFlow={showWindFlow} setShowWindFlow={setShowWindFlow}
        windMode={windMode} setWindMode={setWindMode}
        showExclusionOverlay={showExclusionOverlay} setShowExclusionOverlay={setShowExclusionOverlay}
        showHeatmapV10={showHeatmapV10} setShowHeatmapV10={setShowHeatmapV10}
        heatmapV10Data={heatmapV10Data} heatmapIncludeCorridors={heatmapIncludeCorridors}
        setHeatmapIncludeCorridors={setHeatmapIncludeCorridors}
        showAlimentationV2={showAlimentationV2} setShowAlimentationV2={setShowAlimentationV2}
        showNutritionPoints={showNutritionPoints} setShowNutritionPoints={setShowNutritionPoints}
        nNutritionPointsMax={nNutritionPointsMax} setNNutritionPointsMax={setNNutritionPointsMax}
        showNutritionPanel={showNutritionPanel} setShowNutritionPanel={setShowNutritionPanel}
        showAmenagementPanel={showAmenagementPanel} setShowAmenagementPanel={setShowAmenagementPanel}
        alimentationV2Data={alimentationV2Data}
        pointsChaudsMode={pointsChaudsMode} setPointsChaudsMode={setPointsChaudsMode}
        pointsChaudsFilter={pointsChaudsFilter} setPointsChaudsFilter={setPointsChaudsFilter}
        minPercentageFilter={minPercentageFilter} setMinPercentageFilter={setMinPercentageFilter}
        showCursorBionic={showCursorBionic} setShowCursorBionic={setShowCursorBionic}
        adminArchitecteMode={adminArchitecteMode} setAdminArchitecteMode={setAdminArchitecteMode}
        privacyMode={privacyMode} setPrivacyMode={setPrivacyMode}
        activeWaypoints={activeWaypoints} savedPlaces={savedPlaces}
        selectedWaypointForZones={selectedWaypointForZones}
        showIntelLayer={showIntelLayer} setShowIntelLayer={setShowIntelLayer}
        showInspectionBioPanel={showInspectionBioPanel} setShowInspectionBioPanel={setShowInspectionBioPanel}
        showPhaseA={showPhaseA} setShowPhaseA={setShowPhaseA}
        showPhaseC={showPhaseC} setShowPhaseC={setShowPhaseC}
      />

      {/* ════════════════════════════════════════════════════════════════
          SECTION 4+5 — CARTE DOMINANTE + PANNEAU LATÉRAL
          La carte occupe toujours l'espace principal.
          Un panneau latéral s'ouvre selon l'onglet actif.
          BCE-4X R3/R7/R11: La carte est TOUJOURS rendue, jamais supprimée.
          ════════════════════════════════════════════════════════════════ */}
      <div className="flex-1 flex overflow-hidden min-h-0 relative">
        {/* ── CARTE BIONIC — ZONE DOMINANTE (80%+ de l'écran) ── */}
        <div className="flex-1 relative">
          {/* MODE INSPECTION BIOLOGIQUE PRO/EXPERT — panneau flottant institutionnel */}
          <InspectionBiologiquePanel
            open={showInspectionBioPanel}
            onClose={() => setShowInspectionBioPanel(false)}
          />
          {/* NUTRITION_PANEL_Ω — rapport nutritionnel au double-clic saline */}
          <NutritionPanelOmega
            payload={nutritionPanelPayload}
            onClose={() => setNutritionPanelPayload(null)}
          />
          {/* Indicateur du mode création de waypoint */}
          {mapClickMode && (
            <div className="absolute top-4 left-1/2 transform -translate-x-1/2 z-[1000] bg-green-500 text-black px-4 py-2 rounded-lg shadow-lg flex items-center gap-2 animate-pulse">
              <Crosshair className="h-5 w-5" />
              <span className="text-sm font-medium">Cliquez sur la carte pour placer votre waypoint</span>
              <button onClick={() => setMapClickMode(false)} className="ml-2 hover:bg-green-600 rounded p-0.5"><X className="h-4 w-4" /></button>
            </div>
          )}
            
          {/* V8.1: Mode Split View ou Mode normal */}
          {splitViewEnabled ? (
            <SplitViewContainer
              mapCenter={splitMapCenter || [currentMapCenter.lat, currentMapCenter.lng]}
              mapZoom={splitMapZoom || currentZoom}
              mapRef={mapRef}
              activeEcoLayers={activeEcoLayers}
              ecoLayerOpacities={ecoLayerOpacities}
              ecoMapStatus={ecoMapStatus}
              activeFallback={activeFallback}
              classificationToggles={classificationToggles}
              showExclusionOverlay={showExclusionOverlay}
              showWindFlow={showWindFlow}
              windMode={windMode}
              showCorridorsV1={showCorridorsV1}
              showCorridors={showCorridors}
              showCursorBionic={showCursorBionic}
              isPrivateDataVisible={isPrivateDataVisible}
              privacyMode={privacyMode}
              minPercentageFilter={minPercentageFilter}
              selectedSpecies={selectedSpecies}
              temporalHourMT={temporalHourMT}
              layersVisible={layersVisible}
              selectedWaypointForZones={selectedWaypointForZones}
              bboxBounds={bboxBounds}
              activeWaypoints={activeWaypoints}
              savedPlaces={savedPlaces}
              selectWaypointAsTarget={selectWaypointAsTarget}
              setContextMenuMT={setContextMenuMT}
              isZoneFavorite={isZoneFavorite}
              addFavorite={addFavorite}
              getFavoriteId={getFavoriteId}
              removeFavorite={removeFavorite}
              setSelectedZone={setSelectedZone}
              setHoveredZone={setHoveredZone}
              userPosition={userPosition}
              userId={userId}
              syncToBackend={syncToBackend}
              groupMembersPositions={groupMembersPositions}
              isGroupeTrackingActive={isGroupeTrackingActive}
              handleZoomChange={handleZoomChange}
              handleMapMove={handleMapMove}
              handleBoundsChange={handleBoundsChange}
              mapClickMode={mapClickMode}
              handleMapClickForWaypoint={handleMapClickForWaypoint}
              leftSeason={selectedBiologicalSeason}
              rightSeason={splitRightSeason}
              onLeftSeasonChange={setSelectedBiologicalSeason}
              onRightSeasonChange={setSplitRightSeason}
              leftZonesData={{ zones: bionicZones, corridors: bionicZonesData.corridors || [], stats: bionicZonesData.stats }}
              rightZonesData={splitRightZonesData}
              pipelineState={pipelineState}
            />
          ) : (
          <>
          {/* ── MapContainer — CARTE PRINCIPALE (composant extrait IM1.2) ── */}
          <MapContainer center={mapCenter} zoom={mapZoom} className={`absolute inset-0 w-full h-full ${mapClickMode ? 'cursor-crosshair' : ''}`} zoomControl={false} style={{ background: '#0a0a0f' }}>
            <MapContent
              activeEcoLayers={activeEcoLayers}
              ecoLayerOpacities={ecoLayerOpacities}
              ecoMapStatus={ecoMapStatus}
              activeFallback={activeFallback}
              mapRef={mapRef}
              handleZoomChange={handleZoomChange}
              handleMapMove={handleMapMove}
              handleBoundsChange={handleBoundsChange}
              mapClickMode={mapClickMode}
              handleMapClickForWaypoint={handleMapClickForWaypoint}
              classificationToggles={classificationToggles}
              showExclusionOverlay={showExclusionOverlay}
              showWindFlow={showWindFlow}
              windMode={windMode}
              showCorridorsV1={showCorridorsV1}
              showCorridors={showCorridors}
              showCursorBionic={showCursorBionic}
              isPrivateDataVisible={isPrivateDataVisible}
              privacyMode={privacyMode}
              bionicZones={bionicZones}
              bionicZonesData={bionicZonesData}
              minPercentageFilter={minPercentageFilter}
              selectedSpecies={selectedSpecies}
              temporalHourMT={temporalHourMT}
              layersVisible={layersVisible}
              selectedWaypointForZones={selectedWaypointForZones}
              bboxBounds={bboxBounds}
              activeWaypoints={activeWaypoints}
              savedPlaces={savedPlaces}
              selectWaypointAsTarget={selectWaypointAsTarget}
              setContextMenuMT={setContextMenuMT}
              isZoneFavorite={isZoneFavorite}
              addFavorite={addFavorite}
              getFavoriteId={getFavoriteId}
              removeFavorite={removeFavorite}
              setSelectedZone={setSelectedZone}
              setHoveredZone={setHoveredZone}
              userPosition={userPosition}
              userId={userId}
              syncToBackend={syncToBackend}
              groupMembersPositions={groupMembersPositions}
              isGroupeTrackingActive={isGroupeTrackingActive}
              huntingPathData={huntingPathData}
              showHuntingPath={showHuntingPath}
              onCorridorDataLoaded={setCorridorV10Data}
              showZonesLayer={showZonesLayer}
              showCorridorsLayer={showCorridorsLayer}
              showPointsLayer={showPointsLayer}
              pointsChaudsMode={pointsChaudsMode}
              pointsChaudsFilter={pointsChaudsFilter}
              zoneSubFilters={zoneSubFilters}
              corridorSubFilters={corridorSubFilters}
              pointSubFilters={pointSubFilters}
              showAlimentationV2={showAlimentationV2}
              showNutritionPoints={showNutritionPoints}
              nNutritionPointsMax={nNutritionPointsMax}
              onAlimentationDataLoaded={setAlimentationV2Data}
              waypointCenter={waypointCenter}
              showStands={zoneSubFilters.affuts}
              windDirection={windInfo?.directionDeg || 315}
              windSpeed={windInfo?.speed || 12}
              windDirectionDeg={windInfo?.directionDeg || null}
              onStandClick={setSelectedStand}
              feedingSitesForStands={feedingSitesForStands}
              fixedBlindsForStands={fixedBlindsForStands}
              onNutritionPointClick={setSelectedNutritionPoint}
              showHeatmapV10={showHeatmapV10}
              onHeatmapDataLoaded={setHeatmapV10Data}
              onSalineNutritionDblClick={setNutritionPanelPayload}
              heatmapIncludeCorridors={heatmapIncludeCorridors}
              showHydro={effectiveShowHydro}
              userCameras={positionedCameras}
              showCameraMarkers={true}
              alphaHotspots={alphaHotspots}
              showAlphaLayer={true}
              trajectories={alphaTrajectories}
              showTrajectoriesLayer={true}
              bundleDataV8={bundleDataV8}
              showIntelLayer={showIntelLayer}
              showSalinesLayer={showPhaseA}
              showContaminationLayer={showPhaseC}
              showPhaseA={showPhaseA}
              phaseARelocalisations={phaseARelocalisations}
              phaseASalines={phaseASalines}
              phaseASiteActuel={phaseASiteActuel}
            />
          </MapContainer>

          {/* BCE-4X LEGENDE ULTIME: BionicLegend PERSISTANTE (ORDONNANCE STEEVE-MAX P0-K++) */}
          <BionicLegend
            pipelineState={{ ready: true }}
            zoneCount={bionicZonesData?.zones?.length || 0}
            corridorCount={0}
            windDeg={windInfo?.direction || 225}
            selectedSpecies={selectedSpecies}
            showCorridors={classificationToggles?.corridors}
          />

          {/* CACHE-STATE-Omega — overlay bas-droite, ADMIN uniquement */}
          <CacheStateOmega
            visible={!!adminArchitecteMode}
            cacheState={bundleCacheState}
            servedMs={bundleServedMs}
            computeMs={bundleComputeMs}
          />

          {/* ── Indicateur Zone d'Analyse — ADMIN PREMIUM uniquement ── */}
          {adminArchitecteMode && selectedWaypointForZones && (
            <div
              className="absolute bottom-[120px] left-2 z-[999] select-none pointer-events-none"
              data-testid="zone-analysis-indicator"
            >
              <div className="flex items-center gap-2 px-3 py-2 bg-[#0c0c14]/90 border border-[#f5a623]/30 rounded-lg backdrop-blur-sm shadow-lg">
                <div className="w-3 h-3 border-2 border-dashed rounded-sm flex-shrink-0" style={{ borderColor: '#f5a623' }} />
                <div>
                  <div className="text-[10px] font-bold text-white tracking-wide">Zone d'analyse</div>
                  <div className="text-[9px] text-gray-400">2 km × 2 km — {selectedWaypointForZones?.name || 'Waypoint'}</div>
                </div>
              </div>
            </div>
          )}

          {/* ── Indicateur Heatmap V6 — Discret bas-gauche ── */}
          {showHeatmapV10 && selectedWaypointForZones && heatmapV10Data && (
            <div
              className="absolute bottom-[60px] left-2 z-[999] select-none pointer-events-none"
              data-testid="heatmap-v6-indicator"
            >
              <div className="flex items-center gap-1.5 px-2 py-1 bg-[#0c0c14]/85 border border-gray-700/40 rounded backdrop-blur-sm">
                <div className="w-2 h-2 rounded-full bg-gradient-to-r from-blue-500 via-yellow-500 to-red-500 flex-shrink-0" />
                <span className="text-[8px] text-gray-400 font-medium">
                  Score{!heatmapIncludeCorridors && ' (sans corridors)'}
                </span>
                <span className="text-[8px] text-gray-500">{heatmapV10Data.score_avg}/100</span>
              </div>
            </div>
          )}


          {/* ── Contrôles carte — gauche ── */}
          <div className="absolute top-4 left-3 z-[1000] flex flex-col gap-2">
            <button className="bg-[#111118]/90 text-white border border-[#1a1a2e] h-8 w-8 rounded-lg flex items-center justify-center hover:bg-[#1a1a2e] transition-colors" onClick={() => { if (mapRef.current) mapRef.current.setZoom(mapRef.current.getZoom() + 1); }}>+</button>
            <button className="bg-[#111118]/90 text-white border border-[#1a1a2e] h-8 w-8 rounded-lg flex items-center justify-center hover:bg-[#1a1a2e] transition-colors" onClick={() => { if (mapRef.current) mapRef.current.setZoom(Math.max(5, mapRef.current.getZoom() - 1)); }}>-</button>
            <button className={`${userPosition ? 'bg-blue-600' : 'bg-[#111118]/90'} text-white border border-[#1a1a2e] h-8 w-8 rounded-lg flex items-center justify-center hover:bg-[#1a1a2e] transition-colors`} onClick={centerOnUser}>
              <LocateFixed className="h-4 w-4" />
            </button>
            {/* BDRE-FIRST P1: BDRE indicator on map */}
            {bdreStatus && (
              <Popover>
                <PopoverTrigger asChild>
                  <button
                    data-testid="map-bdre-indicator"
                    className="bg-[#111118]/90 text-white border border-[#1a1a2e] h-8 w-8 rounded-lg flex items-center justify-center hover:bg-[#1a1a2e] transition-colors relative"
                    title="BDRE Data Reliability"
                  >
                    <Shield className="h-4 w-4 text-[#F5A623]" />
                    <span className={`absolute -top-0.5 -right-0.5 w-2.5 h-2.5 rounded-full border border-[#111118] ${bdreStatus.alerts > 0 ? 'bg-red-500' : bdreStatus.healthy > 0 ? 'bg-green-400' : 'bg-yellow-400'}`} />
                  </button>
                </PopoverTrigger>
                <PopoverContent side="right" className="w-56 bg-[#111118] border-[#1a1a2e] p-3" data-testid="map-bdre-popover">
                  <div className="space-y-2">
                    <div className="flex items-center gap-2">
                      <Shield className="h-3.5 w-3.5 text-[#F5A623]" />
                      <span className="text-xs font-medium text-gray-200">BDRE {bdreStatus.version}</span>
                    </div>
                    <div className="grid grid-cols-2 gap-1.5">
                      <div className="bg-[#0a0a14] rounded px-2 py-1 text-center">
                        <div className="text-green-400 text-sm font-bold">{bdreStatus.healthy}</div>
                        <div className="text-[9px] text-gray-500">ACTIVES</div>
                      </div>
                      <div className="bg-[#0a0a14] rounded px-2 py-1 text-center">
                        <div className="text-gray-400 text-sm font-bold">{bdreStatus.notConnected}</div>
                        <div className="text-[9px] text-gray-500">HORS LIGNE</div>
                      </div>
                      <div className="bg-[#0a0a14] rounded px-2 py-1 text-center">
                        <div className="text-yellow-400 text-sm font-bold">{bdreStatus.fallbacks}</div>
                        <div className="text-[9px] text-gray-500">FALLBACKS</div>
                      </div>
                      <div className="bg-[#0a0a14] rounded px-2 py-1 text-center">
                        <div className="text-red-400 text-sm font-bold">{bdreStatus.alerts}</div>
                        <div className="text-[9px] text-gray-500">ALERTES</div>
                      </div>
                    </div>
                    <div className="flex flex-wrap gap-0.5 pt-1">
                      {bdreStatus.sources.slice(0, 16).map((src, i) => (
                        <div key={i} className={`w-2.5 h-2.5 rounded-sm ${src.status === 'healthy' ? (src.score >= 0.8 ? 'bg-green-500' : src.score >= 0.3 ? 'bg-yellow-500' : 'bg-red-500') : 'bg-zinc-600'}`} title={`${src.source_id}: ${src.name} (${(src.score*100).toFixed(0)}%)`} />
                      ))}
                    </div>
                  </div>
                </PopoverContent>
              </Popover>
            )}
          </div>

          {/* BCE-4X: Bloc Meteo Intelligent — droite, au-dessus du Score */}
          <WeatherPanel
            wind={sharedWeather.wind}
            weather={sharedWeather.weather}
            loading={sharedWeather.loading}
            huntingScore={sharedWeather.huntingScore}
            scoreV8={scoreV8}
          />

          {/* ── Bouton + Waypoint déplacé dans la toolbar (Passe 3 UX) ── */}
          </>
          )}
        </div>

        {/* ══════════════════════════════════════════════════════════════
            SECTION 5 — PANNEAUX OPERATIONNELS (Waypoints, Lieux UNIQUEMENT)
            PHASE-FRONTEND-Omega V2: ZERO panneau analytique lateral.
            ZERO Intelligence Dashboard. ZERO Groupe. ZERO Exclusions.
            ══════════════════════════════════════════════════════════════ */}
        {['waypoints', 'lieux'].includes(activeTab) && (
        <div className="w-80 flex-shrink-0 bg-[#0d0d14] border-l border-[#1a1a2e] overflow-y-auto" data-testid="side-panel">

          {/* ── Panneau Waypoints ── */}
          {activeTab === 'waypoints' && (
            <WaypointUnifiedPanel
              waypoints={waypoints}
              activeWaypoints={activeWaypoints}
              selectedWaypoint={selectedWaypointForZones}
              onSelectWaypoint={(wp) => selectWaypointAsTarget(wp)}
              onDeselectWaypoint={() => setSelectedWaypointForZones(null)}
              onDeleteWaypoint={(id) => handleDeleteWaypoint(id)}
              onToggleActive={(id) => toggleWaypointActive(id)}
              onAnalyze={(wp) => { selectWaypointAsTarget(wp); setActiveTab('carte'); }}
              onShare={(wp) => openShareDialog(wp)}
              onCenterMap={(wp) => { if (mapRef.current) mapRef.current.setView([wp.lat, wp.lng], 14); setActiveTab('carte'); }}
              userPosition={userPosition}
              watchingPosition={watchingPosition}
              onStartWatching={startWatchingPosition}
              onStopWatching={stopWatchingPosition}
              layersVisible={layersVisible}
              currentMapCenter={currentMapCenter}
              PLACE_TYPES={PLACE_TYPES}
              onGenerateSnapshot={handleGenerateSnapshot}
              isGeneratingSnapshot={isGeneratingSnapshot}
              snapshotData={snapshotData}
              compareSelection={compareSelection}
              onToggleCompare={handleToggleCompare}
              onLaunchCompare={handleLaunchCompare}
            />
          )}

          {/* ── Panneau Lieux ── */}
          {activeTab === 'lieux' && (
            <PlacesSidePanel
              savedPlaces={savedPlaces}
              PLACE_TYPES={PLACE_TYPES}
              onAddPlace={() => setShowAddPlaceDialog(true)}
              onAddPlaceWithType={(typeId) => { setNewPlace({ name: '', type: typeId, lat: '', lng: '', notes: '' }); setShowAddPlaceDialog(true); }}
              onCenterOnPlace={(place) => { if (mapRef.current) mapRef.current.setView([place.lat, place.lng], 13); setActiveTab('carte'); }}
              onEditPlace={(place) => setEditingPlace(place)}
              onDeletePlace={(id) => deletePlace(id)}
            />
          )}
        </div>
        )}
      </div>

      {/* ═══ DIALOGUES (composant extrait STEEVE-MAX) ═══ */}
      <TerritoireDialogs
        editingPlace={editingPlace} setEditingPlace={setEditingPlace} handleUpdatePlace={handleUpdatePlace}
        showAddPlaceDialog={showAddPlaceDialog} setShowAddPlaceDialog={setShowAddPlaceDialog}
        newPlace={newPlace} setNewPlace={setNewPlace} handleAddPlace={handleAddPlace}
        useCurrentPositionForNewPlace={useCurrentPositionForNewPlace}
        showAddWaypointDialog={showAddWaypointDialog} setShowAddWaypointDialog={setShowAddWaypointDialog}
        newWaypoint={newWaypoint} setNewWaypoint={setNewWaypoint}
        handleAddWaypointWithWind={handleAddWaypointWithWind}
        useCurrentPositionForNewWaypoint={useCurrentPositionForNewWaypoint}
        showShareDialog={showShareDialog} setShowShareDialog={setShowShareDialog}
        waypointToShare={waypointToShare} setWaypointToShare={setWaypointToShare} userId={userId}
        showCreateGroupDialog={showCreateGroupDialog} setShowCreateGroupDialog={setShowCreateGroupDialog}
        refreshGroups={refreshGroups}
        showGroupDashboard={showGroupDashboard} setShowGroupDashboard={setShowGroupDashboard}
        selectedGroup={selectedGroup} setSelectedGroup={setSelectedGroup}
        contextMenuMT={contextMenuMT} setContextMenuMT={setContextMenuMT}
        handleDeleteWaypoint={handleDeleteWaypoint} selectWaypointAsTarget={selectWaypointAsTarget}
        showCompareWidget={showCompareWidget} compareSelection={compareSelection}
        handleCloseCompare={handleCloseCompare} PLACE_TYPES={PLACE_TYPES}
      />
    </div>
  );
};

export default MonTerritoireBionicPage;

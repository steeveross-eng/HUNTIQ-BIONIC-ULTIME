/**
 * MapContent.jsx — RENDERING V8-INSTITUTIONNEL EXCLUSIF
 * ======================================================
 * PHASE-4B: PURGE TOTALE couches legacy V6/V7/debug.
 * Source UNIQUE: BionicLayersV8 via /api/v8/institutional/territoire
 * ZERO fallback. ZERO substitution. ZERO reactivation.
 *
 * Couches AUTORISEES:
 *   - EcoforestryLayers (tuiles de base)
 *   - BionicLayersV8 (V8-INSTITUTIONNEL EXCLUSIF)
 *   - Markers (waypoints, position utilisateur)
 *   - MapInteractionLayer (GPS overlay)
 *
 * Couches INTERDITES (purgees):
 *   - BionicCorridorsV6Layer, BionicZone2km, BionicZone600m
 *   - StandsMapLayer, ContaminationOverlayLayer
 *   - NutritionPointsLayer, ConsolidatedHeatmapLayer
 *   - HuntingPathLayer, AlphaHotspotsLayer, TrajectoriesLayer
 *   - PhaseALayerV8, ExclusionOverlayLayer, StructureContrastLayer
 *   - HydrographyOverlayLayer, AccessRouteV6Layer
 *   - Circle, Rectangle (shapes geometriques)
 *   - BionicAntiDoublesGuard, ShootingZones
 */
import React from 'react';
import { Marker, Popup } from 'react-leaflet';
import EcoforestryLayers from '@/components/territoire/EcoforestryLayers';
import { MapRefCapture, ZoomHandler, MapResizer, MapClickHandler, createCustomIcon } from '@/components/territoire/map/MapHelpers';
import CursorBionicLayer from '@/components/territoire/CursorBionicLayer';
import BionicLayersV8 from '@/components/territoire/BionicLayersV8';
import WindFlowLayer from '@/components/territoire/WindFlowLayer';
import { MapInteractionLayer } from '@/modules/map_interaction';
import { PLACE_TYPES } from '@/config/placeTypes';

const MapContentInner = React.memo(({
  // Eco layers
  activeEcoLayers,
  ecoLayerOpacities,
  ecoMapStatus,
  activeFallback,
  // Map refs & handlers
  mapRef,
  handleZoomChange,
  handleMapMove,
  handleBoundsChange,
  mapClickMode,
  handleMapClickForWaypoint,
  // Classification & toggles
  classificationToggles,
  showCursorBionic,
  isPrivateDataVisible,
  privacyMode,
  // Waypoints & places
  selectedWaypointForZones,
  activeWaypoints,
  savedPlaces,
  selectWaypointAsTarget,
  setContextMenuMT,
  // User
  userPosition,
  userId,
  // V8 Bundle unified layers — SOURCE UNIQUE
  bundleDataV8,
  // Layer toggles V8
  showZonesLayer,
  showCorridorsLayer,
  showPointsLayer,
  showCorridors,
  // PHASE-FRONTEND-Omega V2 — toggles institutionnels ON/OFF stricts
  showIntelLayer = true,
  showSalinesLayer = true,
  showContaminationLayer = true,
  showHeatmapV10 = true,
  showWindFlow = true,
  // Wapoint center
  waypointCenter,
  // Heatmap callback
  onHeatmapDataLoaded,
  // PHASE_NUTRITION_SALINES_BINDING_Ω — double-clic saline → panel nutritionnel
  onSalineNutritionDblClick,
  selectedSpecies,

  // PROPS LEGACY (acceptes mais IGNORES — PURGE V6/V7)
  showExclusionOverlay,
  windMode,
  showCorridorsV1,
  bionicZones,
  bionicZonesData,
  minPercentageFilter,
  temporalHourMT,
  layersVisible,
  bboxBounds,
  isZoneFavorite,
  addFavorite,
  getFavoriteId,
  removeFavorite,
  setSelectedZone,
  setHoveredZone,
  syncToBackend,
  groupMembersPositions,
  isGroupeTrackingActive,
  huntingPathData,
  showHuntingPath,
  onCorridorDataLoaded,
  showAlimentationV2,
  showNutritionPoints,
  nNutritionPointsMax,
  onAlimentationDataLoaded,
  onNutritionPointClick,
  showStands,
  windDirection,
  windSpeed,
  windDirectionDeg,
  onStandClick,
  feedingSitesForStands,
  fixedBlindsForStands,
  onHeatmapDataLoaded: _,
  heatmapIncludeCorridors,
  pointsChaudsMode,
  pointsChaudsFilter,
  zoneSubFilters,
  corridorSubFilters,
  pointSubFilters,
  accessRouteData,
  showAccessRoute,
  showHydro,
  userCameras,
  showCameraMarkers,
  alphaHotspots,
  showAlphaLayer,
  trajectories,
  showTrajectoriesLayer,
  showPhaseA,
  phaseARelocalisations,
  phaseASalines,
  phaseASiteActuel,
  onPhaseARelocClick,
  onPhaseASalineClick,
}) => (
  <>
    {/* COUCHE 1: TUILES DE BASE */}
    <EcoforestryLayers
      activeLayers={activeEcoLayers}
      layerOpacities={ecoLayerOpacities}
      baseMapId={activeEcoLayers.baseMap}
      fallbackStatus={ecoMapStatus}
      activeFallback={activeFallback}
    />

    {/* UTILITAIRES CARTE */}
    <MapRefCapture mapRefProp={mapRef} />
    <MapResizer />
    <ZoomHandler onZoomChange={handleZoomChange} onMapMove={handleMapMove} onBoundsChange={handleBoundsChange} />
    {mapClickMode && <MapClickHandler onMapClick={handleMapClickForWaypoint} enabled={true} />}

    {/* ══════════════════════════════════════════════════════════════ */}
    {/* V8-INSTITUTIONNEL EXCLUSIF — SOURCE UNIQUE RENDERING         */}
    {/* PHASE-FRONTEND-Omega V2 — BOUTONS PRESSEURS STRICT ON/OFF    */}
    {/* ZERO couche legacy. ZERO fallback. ZERO reactivation auto.   */}
    {/* ══════════════════════════════════════════════════════════════ */}
    {selectedWaypointForZones && waypointCenter && (
      <BionicLayersV8
        bundleData={bundleDataV8}
        waypointCenter={waypointCenter}
        species={selectedSpecies && selectedSpecies !== 'tous' ? selectedSpecies.toLowerCase() : 'cerf'}
        showZones={showZonesLayer !== false}
        showCorridors={showCorridorsLayer !== false}
        showAffuts={showPointsLayer !== false}
        showSalines={showSalinesLayer !== false}
        showHotspots={showHeatmapV10 !== false}
        showWind={showWindFlow !== false}
        showContamination={showContaminationLayer !== false}
        enabled={showIntelLayer !== false}
        onDataLoaded={onHeatmapDataLoaded}
        onSalineNutritionDblClick={onSalineNutritionDblClick}
      />
    )}

    {/* V9-INSTITUTIONNEL: VENT REEL DYNAMIQUE (VENTUSKY-STEEVE-MAX) */}
    {/* Source: ECCC/NOAA via Open-Meteo /api/v3/weather/windgrid */}
    {/* Physique: friction sol, Venturi, ralentissement foret, turbulence +-3deg */}
    {selectedWaypointForZones && showWindFlow && showIntelLayer && <WindFlowLayer enabled={true} />}

    {/* MARQUEURS WAYPOINTS — Seuls elements interactifs non-V8 autorises */}
    {userPosition && (
      <Marker position={[userPosition.lat, userPosition.lng]} icon={createCustomIcon('#3b82f6', 'user')}>
        <Popup><div className="text-center font-bold">Ma position</div></Popup>
      </Marker>
    )}
    {showCursorBionic && classificationToggles?.curseurBionic && (
      <CursorBionicLayer species={selectedSpecies} onQuickAddWaypoint={null} />
    )}
    {isPrivateDataVisible && classificationToggles?.waypoints && activeWaypoints?.map(wp => (
      <Marker
        key={wp.id}
        position={[wp.lat, wp.lng]}
        icon={createCustomIcon(selectedWaypointForZones?.id === wp.id ? '#3CB371' : '#FF9800', 'waypoint')}
        eventHandlers={{
          click: () => selectWaypointAsTarget(wp),
          contextmenu: (e) => {
            e.originalEvent.preventDefault();
            setContextMenuMT({ position: { x: e.originalEvent.clientX, y: e.originalEvent.clientY }, waypoint: { ...wp } });
          }
        }}
      />
    ))}
    {isPrivateDataVisible && classificationToggles?.waypoints && savedPlaces?.map(place => (
      <Marker key={place.id} position={[place.lat, place.lng]} icon={createCustomIcon(PLACE_TYPES.find(t => t.id === place.type)?.color || '#6b7280', 'place')}>
        <Popup><div className="text-center"><div className="font-bold">{place.name}</div><div className="text-xs">{PLACE_TYPES.find(t => t.id === place.type)?.name}</div></div></Popup>
      </Marker>
    ))}
    {privacyMode && <div className="bionic-private-overlay" />}

    {/* GPS overlay */}
    <MapInteractionLayer showCoordinates={true} />

    {/* ══════════════════════════════════════════════════════════════ */}
    {/* PURGE V6/V7/DEBUG — TOUT CE QUI SUIT EST DESACTIVE           */}
    {/* ZERO reactivation. ZERO fallback. ZERO substitution.         */}
    {/* ══════════════════════════════════════════════════════════════ */}
    {/* PURGE: HydrographyOverlayLayer — DESACTIVE */}
    {/* PURGE: ExclusionOverlayLayer — DESACTIVE */}
    {/* PURGE: WindFlowLayer — DESACTIVE */}
    {/* PURGE: StructureContrastLayer — DESACTIVE */}
    {/* PURGE: HuntingPathLayer — DESACTIVE */}
    {/* PURGE: BionicZone2kmLayer — DESACTIVE */}
    {/* PURGE: Rectangle bbox — DESACTIVE */}
    {/* PURGE: Circle waypoint — DESACTIVE */}
    {/* PURGE: ShootingZones — DESACTIVE */}
    {/* PURGE: StandsMapLayer — DESACTIVE */}
    {/* PURGE: ContaminationOverlayLayer — DESACTIVE */}
    {/* PURGE: NutritionPointsLayer — DESACTIVE */}
    {/* PURGE: PhaseALayerV8 — DESACTIVE */}
    {/* PURGE: CameraMarkersLayer — DESACTIVE */}
    {/* PURGE: AlphaHotspotsLayer — DESACTIVE */}
    {/* PURGE: TrajectoriesLayer — DESACTIVE */}
    {/* PURGE: BionicAntiDoublesGuard — DESACTIVE */}
    {/* PURGE: ConsolidatedHeatmapLayer — DESACTIVE */}
  </>
));

MapContentInner.displayName = 'MapContent';
export const MapContent = MapContentInner;

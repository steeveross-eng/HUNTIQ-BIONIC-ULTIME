/* ============================================================
   BIONIC CARTOGRAPHY x2000 — Premium Map Layers
   STEEVE-MAX x2000 / Phase F

   3 couches cartographiques premium:
   1. LIDAR + Relief Ombre HD
   2. VGO — Vegetation Gradient Optimise
   3. Foret Ouverte Stylisee Premium

   Palettes naturelles, compatibilite overlays,
   optimisation responsive.
   ============================================================ */

import { useState, useCallback } from "react";
import { Layers, Mountain, TreePine, Map as MapIcon, Eye, EyeOff } from "lucide-react";
import "@/theme/bionic_theme.css";

/* ═══════════════════════════════════════
   TILE SOURCES — Premium Map Layers
   ═══════════════════════════════════════ */

export const MAP_LAYERS = {
  lidar_relief: {
    id: "lidar_relief",
    name: "LIDAR + Relief Ombre HD",
    description: "Relief haute definition avec ombrage topographique",
    url: "https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png",
    attribution: "OpenTopoMap (CC-BY-SA)",
    maxZoom: 17,
    opacity: 1.0,
    category: "terrain",
    icon: Mountain,
    color: "#8B7355",
    /* Custom CSS filter for enhanced terrain readability */
    filter: "contrast(1.1) saturate(0.9) brightness(1.05)",
  },
  vgo_vegetation: {
    id: "vgo_vegetation",
    name: "VGO — Vegetation Gradient Optimise",
    description: "Gradient de vegetation avec palette naturelle optimisee",
    url: "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
    attribution: "Esri World Imagery",
    maxZoom: 19,
    opacity: 0.85,
    category: "vegetation",
    icon: TreePine,
    color: "#2D5016",
    filter: "saturate(1.3) contrast(1.05) hue-rotate(-5deg)",
  },
  forest_premium: {
    id: "forest_premium",
    name: "Foret Ouverte Stylisee Premium",
    description: "Style premium avec forets, cours d'eau et sentiers visibles",
    url: "https://{s}.tile.thunderforest.com/landscape/{z}/{x}/{y}.png?apikey=pk.placeholder",
    fallbackUrl: "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
    attribution: "Thunderforest Landscape / OSM",
    maxZoom: 18,
    opacity: 1.0,
    category: "forest",
    icon: TreePine,
    color: "#1B4332",
    filter: "saturate(1.2) contrast(1.08) brightness(0.95)",
  },
};

/* Custom overlay styles for each base layer */
export const OVERLAY_STYLES = {
  lidar_relief: {
    hotspot: { fillColor: "#FF6B35", strokeColor: "#CC4400", fillOpacity: 0.4, strokeWidth: 2 },
    corridor: { color: "#FFD700", weight: 3, opacity: 0.7, dashArray: "8,4" },
    zone: { fillColor: "#4ECDC4", strokeColor: "#2C8C83", fillOpacity: 0.2, strokeWidth: 2 },
    heatmap: { gradient: { 0.2: "#2196F3", 0.4: "#4CAF50", 0.6: "#FFC107", 0.8: "#FF5722", 1.0: "#D50000" } },
  },
  vgo_vegetation: {
    hotspot: { fillColor: "#FF4444", strokeColor: "#CC0000", fillOpacity: 0.5, strokeWidth: 2 },
    corridor: { color: "#FFFFFF", weight: 3, opacity: 0.8, dashArray: "10,5" },
    zone: { fillColor: "#FFEB3B", strokeColor: "#F9A825", fillOpacity: 0.25, strokeWidth: 2 },
    heatmap: { gradient: { 0.2: "#E8F5E9", 0.4: "#A5D6A7", 0.6: "#FFD54F", 0.8: "#FF7043", 1.0: "#D32F2F" } },
  },
  forest_premium: {
    hotspot: { fillColor: "#E91E63", strokeColor: "#AD1457", fillOpacity: 0.4, strokeWidth: 2 },
    corridor: { color: "#FFB300", weight: 3, opacity: 0.7, dashArray: "6,6" },
    zone: { fillColor: "#00BCD4", strokeColor: "#00838F", fillOpacity: 0.2, strokeWidth: 2 },
    heatmap: { gradient: { 0.2: "#B3E5FC", 0.4: "#4FC3F7", 0.6: "#FFB74D", 0.8: "#EF5350", 1.0: "#B71C1C" } },
  },
};

/* ═══════════════════════════════════════
   MAP LAYER SELECTOR COMPONENT
   ═══════════════════════════════════════ */

export const MapLayerSelector = ({ activeLayer, onLayerChange, overlays = {}, onOverlayToggle }) => {
  const [expanded, setExpanded] = useState(false);

  return (
    <div style={{
      position: "absolute", top: 12, right: 12, zIndex: 1000,
      background: "rgba(15, 15, 25, 0.92)", backdropFilter: "blur(12px)",
      borderRadius: 10, border: "1px solid rgba(255,255,255,0.1)",
      overflow: "hidden", minWidth: expanded ? 260 : 42,
      transition: "min-width 0.3s ease",
    }} data-testid="map-layer-selector">
      {/* Toggle Button */}
      <button onClick={() => setExpanded(!expanded)}
        data-testid="map-layer-toggle"
        style={{
          width: "100%", padding: "10px 12px", background: "none", border: "none",
          color: "#fff", cursor: "pointer", display: "flex", alignItems: "center",
          gap: 8, fontSize: 12,
        }}>
        <Layers size={16} style={{ color: "#FF6B35" }} />
        {expanded && <span style={{ fontWeight: 600 }}>Couches cartographiques</span>}
      </button>

      {expanded && (
        <div style={{ padding: "0 12px 12px" }}>
          {/* Base Layers */}
          <div style={{ fontSize: 10, color: "rgba(255,255,255,0.3)", marginBottom: 8, letterSpacing: 1, textTransform: "uppercase" }}>Fond de carte</div>
          {Object.values(MAP_LAYERS).map(layer => {
            const Icon = layer.icon;
            const isActive = activeLayer === layer.id;
            return (
              <button key={layer.id} onClick={() => onLayerChange(layer.id)}
                data-testid={`layer-${layer.id}`}
                style={{
                  width: "100%", padding: "8px 10px", marginBottom: 4,
                  background: isActive ? `${layer.color}33` : "rgba(255,255,255,0.03)",
                  border: `1px solid ${isActive ? `${layer.color}88` : "rgba(255,255,255,0.06)"}`,
                  borderRadius: 6, color: isActive ? "#fff" : "rgba(255,255,255,0.6)",
                  cursor: "pointer", display: "flex", alignItems: "center", gap: 8,
                  fontSize: 11, textAlign: "left", transition: "all 0.2s ease",
                }}>
                <Icon size={14} style={{ color: layer.color, flexShrink: 0 }} />
                <div>
                  <div style={{ fontWeight: isActive ? 600 : 400 }}>{layer.name}</div>
                  <div style={{ fontSize: 9, color: "rgba(255,255,255,0.3)", marginTop: 1 }}>{layer.description}</div>
                </div>
              </button>
            );
          })}

          {/* Overlays */}
          {onOverlayToggle && (
            <>
              <div style={{ fontSize: 10, color: "rgba(255,255,255,0.3)", marginTop: 12, marginBottom: 8, letterSpacing: 1, textTransform: "uppercase" }}>Overlays</div>
              {[
                { id: "hotspots", label: "Points d'activite", color: "#FF6B35" },
                { id: "corridors", label: "Corridors", color: "#FFD700" },
                { id: "zones", label: "Zones", color: "#4ECDC4" },
                { id: "heatmap", label: "Heatmap", color: "#E74C3C" },
                { id: "gps_tracks", label: "Traces GPS", color: "#3498DB" },
                { id: "cameras", label: "Cameras", color: "#9B59B6" },
              ].map(ov => {
                const isOn = overlays[ov.id] !== false;
                return (
                  <button key={ov.id} onClick={() => onOverlayToggle(ov.id)}
                    data-testid={`overlay-${ov.id}`}
                    style={{
                      width: "100%", padding: "6px 10px", marginBottom: 2,
                      background: isOn ? "rgba(255,255,255,0.05)" : "transparent",
                      border: "none", borderRadius: 4, cursor: "pointer",
                      display: "flex", alignItems: "center", justifyContent: "space-between",
                      color: isOn ? "rgba(255,255,255,0.8)" : "rgba(255,255,255,0.3)",
                      fontSize: 11, transition: "all 0.2s ease",
                    }}>
                    <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
                      <div style={{ width: 8, height: 8, borderRadius: "50%", background: isOn ? ov.color : "rgba(255,255,255,0.1)" }} />
                      {ov.label}
                    </div>
                    {isOn ? <Eye size={12} /> : <EyeOff size={12} />}
                  </button>
                );
              })}
            </>
          )}
        </div>
      )}
    </div>
  );
};

/* ═══════════════════════════════════════
   HOOK: useMapLayers
   ═══════════════════════════════════════ */

export const useMapLayers = (defaultLayer = "lidar_relief") => {
  const [activeLayer, setActiveLayer] = useState(defaultLayer);
  const [overlays, setOverlays] = useState({
    hotspots: true,
    corridors: true,
    zones: true,
    heatmap: false,
    gps_tracks: false,
    cameras: true,
  });

  const toggleOverlay = useCallback((id) => {
    setOverlays(prev => ({ ...prev, [id]: !prev[id] }));
  }, []);

  const layer = MAP_LAYERS[activeLayer] || MAP_LAYERS.lidar_relief;
  const overlayStyles = OVERLAY_STYLES[activeLayer] || OVERLAY_STYLES.lidar_relief;

  return {
    activeLayer, setActiveLayer,
    layer, overlayStyles,
    overlays, toggleOverlay,
    tileUrl: layer.url,
    tileAttribution: layer.attribution,
    tileFilter: layer.filter,
    tileMaxZoom: layer.maxZoom,
    tileOpacity: layer.opacity,
  };
};

/* ═══════════════════════════════════════
   SPECIES MAP LAYERS — x2250
   Per-species behavioral and habitat layers
   ═══════════════════════════════════════ */

export const SPECIES_MAP_CONFIG = {
  orignal:        { color: "#8B4513", habitat: "boreal_mixed", icon: "antlers",   corridorStyle: "solid" },
  cerf_virginie:  { color: "#D2691E", habitat: "deciduous_edge", icon: "deer",    corridorStyle: "solid" },
  ours_noir:      { color: "#4A4A4A", habitat: "dense_forest",  icon: "bear",     corridorStyle: "dashed" },
  dindon_sauvage: { color: "#B22222", habitat: "deciduous_edge", icon: "turkey",  corridorStyle: "dotted" },
  caribou:        { color: "#808080", habitat: "tundra_boreal",  icon: "caribou", corridorStyle: "solid" },
  wapiti:         { color: "#DAA520", habitat: "mountain_mixed",  icon: "elk",    corridorStyle: "solid" },
  cerf_mulet:     { color: "#D4A76A", habitat: "semi_arid",      icon: "mule",   corridorStyle: "dashed" },
  pronghorn:      { color: "#F5DEB3", habitat: "open_prairie",   icon: "prong",   corridorStyle: "dotted" },
};

export const getSpeciesOverlayStyle = (speciesId, layerId) => {
  const sp = SPECIES_MAP_CONFIG[speciesId] || SPECIES_MAP_CONFIG.orignal;
  const baseStyles = OVERLAY_STYLES[layerId] || OVERLAY_STYLES.lidar_relief;

  return {
    ...baseStyles,
    hotspot: { ...baseStyles.hotspot, fillColor: sp.color, strokeColor: sp.color },
    corridor: {
      ...baseStyles.corridor,
      color: sp.color,
      dashArray: sp.corridorStyle === "dashed" ? "8,4" : sp.corridorStyle === "dotted" ? "2,6" : "0",
    },
  };
};

export default MapLayerSelector;

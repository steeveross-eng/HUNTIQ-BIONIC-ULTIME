/**
 * HighFidelityMapsPanel.jsx
 * PROTOCOLE BIONIC GOLDEN | BCE-4X | STEEVE-MAX
 * 
 * Panneau de couches cartographiques haute-fidélité:
 * - LIDAR HD
 * - Forêt ouverte / Canopy Density
 * - Orthophoto HR
 * - Hydrologie
 * - Chemins forestiers dérivés
 * - Neige / Sol
 * - Pente HD (DEM 1m)
 */
import React, { useState, useCallback } from 'react';
import { Switch } from '@/components/ui/switch';
import { Slider } from '@/components/ui/slider';
import {
  Mountain, TreePine, SatelliteDish, Droplets,
  Map, Snowflake, Triangle, ChevronDown, ChevronUp, Layers
} from 'lucide-react';

const HF_LAYERS = [
  {
    id: 'hf_lidar_hd',
    label: 'LIDAR HD',
    desc: 'Modèle de hauteur de canopée (MHC) haute résolution',
    icon: Mountain,
    color: '#F59E0B',
  },
  {
    id: 'hf_canopy_density',
    label: 'Canopée / Forêt ouverte',
    desc: 'Densité de canopée forestière et couvert végétal',
    icon: TreePine,
    color: '#22C55E',
  },
  {
    id: 'hf_orthophoto_hr',
    label: 'Orthophoto HR',
    desc: 'Imagerie aérienne haute résolution',
    icon: SatelliteDish,
    color: '#3B82F6',
  },
  {
    id: 'hf_hydrology',
    label: 'Hydrologie',
    desc: 'Réseau hydrographique, cours d\'eau et zones humides',
    icon: Droplets,
    color: '#06B6D4',
  },
  {
    id: 'hf_forest_roads',
    label: 'Chemins forestiers',
    desc: 'Réseau de chemins forestiers et sentiers dérivés',
    icon: Map,
    color: '#A855F7',
  },
  {
    id: 'hf_snow_ground',
    label: 'Neige / Sol',
    desc: 'Couverture de neige et conditions au sol',
    icon: Snowflake,
    color: '#E0F2FE',
  },
  {
    id: 'hf_slope_dem',
    label: 'Pente HD (DEM 1m)',
    desc: 'Modèle numérique d\'élévation et analyse de pente',
    icon: Triangle,
    color: '#EF4444',
  },
];

const HighFidelityMapsPanel = ({ activeEcoLayers, onLayerToggle, opacities = {}, onOpacityChange }) => {
  const [expanded, setExpanded] = useState(false);
  const [expandedLayer, setExpandedLayer] = useState(null);

  const activeCount = HF_LAYERS.filter(l => activeEcoLayers[l.id]).length;

  const handleToggle = useCallback((layerId) => {
    if (onLayerToggle) onLayerToggle(layerId);
  }, [onLayerToggle]);

  return (
    <div
      data-testid="hf-maps-panel"
      style={{
        background: 'rgba(15, 23, 42, 0.92)',
        backdropFilter: 'blur(12px)',
        borderRadius: 8,
        border: '1px solid rgba(79, 195, 247, 0.15)',
        padding: expanded ? '10px 10px 8px' : '8px 10px',
        fontSize: 11,
        color: '#e2e8f0',
        transition: 'all 0.2s ease',
        width: 220,
      }}
    >
      {/* Header */}
      <div
        style={{
          display: 'flex', alignItems: 'center', justifyContent: 'space-between',
          cursor: 'pointer', userSelect: 'none',
        }}
        onClick={() => setExpanded(!expanded)}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          <Layers size={13} style={{ color: '#4FC3F7' }} />
          <span style={{ fontWeight: 700, fontSize: 10, letterSpacing: 0.5, color: '#4FC3F7' }}>
            CARTES HF
          </span>
          {activeCount > 0 && (
            <span style={{
              background: '#4FC3F7', color: '#0F172A', fontSize: 8, fontWeight: 800,
              borderRadius: 10, padding: '1px 5px', lineHeight: '14px',
            }}>
              {activeCount}
            </span>
          )}
        </div>
        {expanded ? <ChevronUp size={12} color="#94a3b8" /> : <ChevronDown size={12} color="#94a3b8" />}
      </div>

      {/* Layers */}
      {expanded && (
        <div style={{ marginTop: 8, display: 'flex', flexDirection: 'column', gap: 3 }}>
          {HF_LAYERS.map((layer) => {
            const Icon = layer.icon;
            const isActive = !!activeEcoLayers[layer.id];
            const isExpanded = expandedLayer === layer.id;

            return (
              <div key={layer.id} data-testid={`hf-layer-${layer.id}`}>
                <div
                  style={{
                    display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                    padding: '4px 6px', borderRadius: 5,
                    background: isActive ? 'rgba(79, 195, 247, 0.08)' : 'transparent',
                    transition: 'background 0.15s',
                  }}
                >
                  <div
                    style={{ display: 'flex', alignItems: 'center', gap: 6, flex: 1, cursor: 'pointer' }}
                    onClick={() => setExpandedLayer(isExpanded ? null : layer.id)}
                  >
                    <Icon size={12} style={{ color: isActive ? layer.color : '#64748b', flexShrink: 0 }} />
                    <span style={{
                      fontSize: 10, fontWeight: isActive ? 600 : 400,
                      color: isActive ? '#e2e8f0' : '#94a3b8',
                    }}>
                      {layer.label}
                    </span>
                  </div>
                  <Switch
                    checked={isActive}
                    onCheckedChange={() => handleToggle(layer.id)}
                    className="h-3.5 w-7"
                    data-testid={`hf-toggle-${layer.id}`}
                  />
                </div>

                {/* Opacity slider */}
                {isExpanded && isActive && onOpacityChange && (
                  <div style={{ padding: '4px 6px 6px 24px' }}>
                    <div style={{ fontSize: 8, color: '#64748b', marginBottom: 3 }}>{layer.desc}</div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                      <span style={{ fontSize: 8, color: '#94a3b8' }}>Opacité</span>
                      <Slider
                        value={[opacities[layer.id] ?? 70]}
                        onValueChange={([v]) => onOpacityChange(layer.id, v)}
                        min={10} max={100} step={5}
                        className="flex-1"
                      />
                      <span style={{ fontSize: 8, color: '#94a3b8', width: 24, textAlign: 'right' }}>
                        {opacities[layer.id] ?? 70}%
                      </span>
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default HighFidelityMapsPanel;

/**
 * useBionicLayers Hook — GOVERNANCE+MAP-LAYERS-Omega
 * ===================================================
 * BCE-4X TERRITOIRE_PRESET = ALWAYS_ON
 * 
 * DIRECTIVE: Toutes les couches geospatiales sont PERMANENTES.
 * ZERO auto-hide, ZERO auto-filter, ZERO dependance moteur SCORE.
 * MAP-LAYER-PERSISTENCE = TRUE
 * MAP-LAYER-HEARTBEAT = 5s (re-force si desactivees par regression)
 * 
 * Les couches survivent: reload, changement espece/province/preset/moteur.
 * 
 * Persistance: geree EXCLUSIVEMENT par useBionicSession.
 */

import { useState, useCallback, useMemo, useEffect, useRef } from 'react';
import { BIONIC_LAYERS } from '@/core/bionic';

// ALWAYS_ON: Couches PERMANENTES — jamais auto-desactivees
const ALWAYS_ON_LAYERS = [
  'habitats', 'repos', 'rut',
  'trajets', 'corridors', 'ensoleillement', 'peuplements',
  'affuts', 'pentes', 'orientation', 'altitude',
  'eau', 'hydro', 'ndvi',
];

// Couches interdites (STEEVE-MAX: anciens sites V1 elimines — ALIMENTATION-V2 seul controle)
const BANNED_LAYERS = new Set(['alimentation', 'salines', 'alimentation_sec']);

// HEARTBEAT interval (ms) — re-force les couches ALWAYS_ON si desactivees
const HEARTBEAT_INTERVAL_MS = 5000;

const useBionicLayers = (initialState = null) => {
  // Etat initial: session restauree OU toutes les couches ALWAYS_ON
  const defaultState = useMemo(() => {
    const state = {};
    
    if (initialState && typeof initialState === 'object' && Object.keys(initialState).length > 0) {
      BIONIC_LAYERS.forEach(layer => {
        if (BANNED_LAYERS.has(layer.id)) {
          state[layer.id] = false;
        } else if (ALWAYS_ON_LAYERS.includes(layer.id)) {
          // ALWAYS_ON: force true meme si session dit false
          state[layer.id] = true;
        } else {
          state[layer.id] = initialState[layer.id] ?? true;
        }
      });
      return state;
    }

    // Defaut: TOUTES les couches ALWAYS_ON actives
    BIONIC_LAYERS.forEach(layer => {
      state[layer.id] = BANNED_LAYERS.has(layer.id) ? false : true;
    });
    return state;
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  const [layersVisible, setLayersVisible] = useState(defaultState);

  // MAP-LAYER-HEARTBEAT: Re-force les couches ALWAYS_ON toutes les 5s
  const heartbeatRef = useRef(null);
  useEffect(() => {
    heartbeatRef.current = setInterval(() => {
      setLayersVisible(prev => {
        let changed = false;
        const next = { ...prev };
        for (const id of ALWAYS_ON_LAYERS) {
          if (next[id] !== true) {
            next[id] = true;
            changed = true;
          }
        }
        return changed ? next : prev;
      });
    }, HEARTBEAT_INTERVAL_MS);
    return () => { if (heartbeatRef.current) clearInterval(heartbeatRef.current); };
  }, []);

  const toggleLayer = useCallback((layerId) => {
    // ALWAYS_ON layers cannot be toggled off
    if (ALWAYS_ON_LAYERS.includes(layerId)) return;
    setLayersVisible(prev => ({ ...prev, [layerId]: !prev[layerId] }));
  }, []);

  const setLayerVisibility = useCallback((layerId, visible) => {
    if (ALWAYS_ON_LAYERS.includes(layerId) && !visible) return;
    setLayersVisible(prev => ({ ...prev, [layerId]: visible }));
  }, []);

  const showAllLayers = useCallback(() => {
    const allVisible = {};
    BIONIC_LAYERS.forEach(layer => { allVisible[layer.id] = !BANNED_LAYERS.has(layer.id); });
    setLayersVisible(allVisible);
  }, []);

  const hideAllLayers = useCallback(() => {
    // ALWAYS_ON stay visible even on "hide all"
    const state = {};
    BIONIC_LAYERS.forEach(layer => {
      state[layer.id] = ALWAYS_ON_LAYERS.includes(layer.id) && !BANNED_LAYERS.has(layer.id);
    });
    setLayersVisible(state);
  }, []);

  const showLayerGroup = useCallback((groupIds) => {
    setLayersVisible(prev => {
      const newState = { ...prev };
      groupIds.forEach(id => { newState[id] = true; });
      return newState;
    });
  }, []);

  const resetLayers = useCallback(() => {
    setLayersVisible(defaultState);
  }, [defaultState]);

  const visibleLayers = useMemo(() => {
    return BIONIC_LAYERS.filter(layer => layersVisible[layer.id]);
  }, [layersVisible]);

  const activeCount = useMemo(() => {
    return Object.values(layersVisible).filter(Boolean).length;
  }, [layersVisible]);

  return {
    layersVisible,
    visibleLayers,
    activeCount,
    allLayers: BIONIC_LAYERS,
    toggleLayer,
    setLayerVisibility,
    showAllLayers,
    hideAllLayers,
    showLayerGroup,
    resetLayers,
    isLayerVisible: (layerId) => layersVisible[layerId] ?? false,
    // MAP-LAYERS-Omega: Expose ALWAYS_ON info
    alwaysOnLayers: ALWAYS_ON_LAYERS,
    isAlwaysOn: (layerId) => ALWAYS_ON_LAYERS.includes(layerId),
  };
};

export default useBionicLayers;

/**
 * useAlphaLayer — Hook pour les données ALPHA hotspots sur la carte
 * Charge les événements camera, applique le scoring ALPHA simulé,
 * et retourne les hotspots géolocalisés pour le layer carte.
 */
import { useState, useEffect, useCallback, useMemo } from 'react';
import axios from 'axios';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

function hashCode(str) {
  let h = 0;
  for (let i = 0; i < str.length; i++) {
    h = ((h << 5) - h) + str.charCodeAt(i);
    h |= 0;
  }
  return h;
}

function simulateSpecies(id) {
  const species = ['orignal', 'cerf', 'ours_noir', 'caribou', 'dindon', 'chevreuil'];
  return species[Math.abs(hashCode(id || '')) % species.length];
}

function computeAlphaScore(id) {
  const base = 50 + (Math.abs(hashCode(id || '')) % 48);
  return Math.min(99, Math.max(1, base + 15));
}

function getAlphaCategory(score) {
  if (score >= 85) return 'alpha';
  if (score >= 65) return 'dominant';
  if (score >= 40) return 'standard';
  return 'juvenile';
}

const useAlphaLayer = (token, camerasLookup = {}) => {
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(false);

  const loadEvents = useCallback(async () => {
    if (!token) return;
    setLoading(true);
    try {
      const res = await axios.get(`${API}/v1/camera/events?limit=200`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setEvents(res.data.events || []);
    } catch (err) {
      console.error('Alpha layer: load error', err);
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => { loadEvents(); }, [loadEvents]);

  const alphaHotspots = useMemo(() => {
    return events.map(evt => {
      const cam = camerasLookup[evt.camera_id] || {};
      const lat = evt.exif_data?.gps_lat || cam.gps_lat;
      const lon = evt.exif_data?.gps_lon || cam.gps_lon;
      if (!lat || !lon) return null;

      const species = evt.species || simulateSpecies(evt.id);
      const score = evt.alpha_score || computeAlphaScore(evt.id);
      const category = getAlphaCategory(score);
      // Only show dominant and alpha on map
      if (category !== 'alpha' && category !== 'dominant') return null;

      const sex = Math.random() > 0.4 ? 'male' : 'femelle';
      // Halo radius: 600m for small species, ~800m (sqrt(2km²/pi)) for large
      const haloRadius = ['orignal', 'caribou', 'ours_noir'].includes(species) ? 800 : 600;

      return {
        id: evt.id,
        lat,
        lon,
        species,
        sex,
        score,
        category,
        haloRadius,
        cameraName: cam.name || 'Inconnue',
        timestamp: evt.timestamp,
        cameraId: evt.camera_id
      };
    }).filter(Boolean);
  }, [events, camerasLookup]);

  return { alphaHotspots, loading, reload: loadEvents };
};

export default useAlphaLayer;

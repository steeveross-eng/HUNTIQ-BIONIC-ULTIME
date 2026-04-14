/**
 * useAlphaLayer — Hook pour les données ALPHA hotspots IA sur la carte
 * VIS-D: Charge les hotspots IA depuis /api/v1/vision/hotspots/alpha
 * et les trajectoires depuis /api/v1/vision/trajectories
 * Fallback: simulation locale si API indisponible
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

const useAlphaLayer = (token, camerasLookup = {}) => {
  const [alphaHotspots, setAlphaHotspots] = useState([]);
  const [trajectories, setTrajectories] = useState([]);
  const [visionAnalyses, setVisionAnalyses] = useState([]);
  const [loading, setLoading] = useState(false);

  const headers = token ? { Authorization: `Bearer ${token}` } : {};

  const loadData = useCallback(async () => {
    if (!token) return;
    setLoading(true);
    try {
      const [hotspotsRes, trajRes, analysesRes] = await Promise.all([
        axios.get(`${API}/v1/vision/hotspots/alpha`, { headers }).catch(() => ({ data: { hotspots: [] } })),
        axios.get(`${API}/v1/vision/trajectories`, { headers }).catch(() => ({ data: { trajectories: [] } })),
        axios.get(`${API}/v1/vision/analyses?limit=100`, { headers }).catch(() => ({ data: { analyses: [] } }))
      ]);

      let hotspots = hotspotsRes.data.hotspots || [];
      const trajs = trajRes.data.trajectories || [];
      const analyses = analysesRes.data.analyses || [];

      setVisionAnalyses(analyses);
      setTrajectories(trajs);

      // If no IA hotspots, generate from camera events (fallback simulation)
      if (hotspots.length === 0 && Object.keys(camerasLookup).length > 0) {
        hotspots = generateFallbackHotspots(camerasLookup);
      }

      // Enrich hotspots for map display
      const enriched = hotspots.map(hs => {
        const lat = hs.gps_lat || hs.location?.coordinates?.[1];
        const lon = hs.gps_lon || hs.location?.coordinates?.[0];
        if (!lat || !lon) return null;

        const score = hs.score || 50;
        const category = score >= 85 ? 'alpha' : score >= 65 ? 'dominant' : 'standard';

        return {
          id: hs.id,
          lat, lon,
          species: hs.dominant_species || (hs.species && hs.species[0]) || 'inconnu',
          sex: 'male',
          score,
          category,
          haloRadius: hs.radius_m || 800,
          cameraName: '',
          timestamp: hs.last_activity,
          totalSightings: hs.total_sightings || 0,
          alphaCount: hs.alpha_count || 0,
          activityLevel: hs.activity_level || 'moderate',
          peakHours: hs.peak_hours || [],
          speciesList: hs.species || []
        };
      }).filter(Boolean);

      setAlphaHotspots(enriched);
    } catch (err) {
      console.error('Alpha layer error:', err);
    } finally {
      setLoading(false);
    }
  }, [token, camerasLookup]);

  useEffect(() => { loadData(); }, [loadData]);

  return { alphaHotspots, trajectories, visionAnalyses, loading, reload: loadData };
};

function generateFallbackHotspots(camerasLookup) {
  const cams = Object.values(camerasLookup);
  return cams.filter(c => c.gps_lat && c.gps_lon).map(c => {
    const h = Math.abs(hashCode(c.id || ''));
    const species = ['orignal', 'cerf', 'ours_noir', 'caribou'][h % 4];
    return {
      id: `fb_${c.id?.slice(0, 8)}`,
      gps_lat: c.gps_lat,
      gps_lon: c.gps_lon,
      score: 50 + (h % 45),
      dominant_species: species,
      species: [species],
      total_sightings: 1 + (h % 5),
      alpha_count: h % 3,
      activity_level: ['moderate', 'high', 'extreme'][h % 3],
      radius_m: ['orignal', 'caribou'].includes(species) ? 800 : 600,
      peak_hours: ['05:00-07:00', '17:00-19:00']
    };
  });
}

export default useAlphaLayer;

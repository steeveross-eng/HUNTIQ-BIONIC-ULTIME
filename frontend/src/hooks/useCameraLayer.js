/**
 * useCameraLayer — Hook pour charger et filtrer les cameras pour la carte
 * CAM-LOC-Omega + MAP-PERF-Omega: Cache client sessionStorage
 */
import { useState, useEffect, useCallback, useMemo } from 'react';
import axios from 'axios';
import { getCachedMapData, setCachedMapData } from '@/utils/mapCache';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const getAuthHeaders = (token) => ({
  headers: { Authorization: `Bearer ${token}` }
});

function haversineDistance(lat1, lon1, lat2, lon2) {
  const R = 6371000;
  const dLat = (lat2 - lat1) * Math.PI / 180;
  const dLon = (lon2 - lon1) * Math.PI / 180;
  const a = Math.sin(dLat / 2) ** 2 +
    Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
    Math.sin(dLon / 2) ** 2;
  return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
}

const useCameraLayer = (token, activeWaypoints = [], groupWaypoints = []) => {
  const [allCameras, setAllCameras] = useState(() => {
    // MAP-PERF-Omega: Instant load from cache
    const cached = getCachedMapData('cameras');
    return cached || [];
  });
  const [loading, setLoading] = useState(false);

  const loadCameras = useCallback(async () => {
    if (!token) return;
    setLoading(true);
    try {
      const res = await axios.get(`${API}/v1/camera/cameras?limit=100`, getAuthHeaders(token));
      const cameras = res.data.cameras || [];
      setAllCameras(cameras);
      setCachedMapData('cameras', cameras);
    } catch (err) {
      console.error('Camera layer: load error', err);
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => {
    loadCameras();
  }, [loadCameras]);

  const camerasWithProximity = useMemo(() => {
    const allWaypoints = [...(activeWaypoints || []), ...(groupWaypoints || [])];

    return allCameras.map(cam => {
      const camLat = cam.gps_lat || cam.location?.coordinates?.[1];
      const camLon = cam.gps_lon || cam.location?.coordinates?.[0];
      if (!camLat || !camLon) return { ...cam, inZone600m: false, nearestWaypointDist: null };

      let minDist = Infinity;
      for (const wp of allWaypoints) {
        const wpLat = wp.lat || wp.gps_lat;
        const wpLon = wp.lng || wp.lon || wp.gps_lon;
        if (wpLat && wpLon) {
          const dist = haversineDistance(camLat, camLon, wpLat, wpLon);
          if (dist < minDist) minDist = dist;
        }
      }

      return {
        ...cam,
        inZone600m: minDist <= 600,
        nearestWaypointDist: minDist === Infinity ? null : Math.round(minDist)
      };
    });
  }, [allCameras, activeWaypoints, groupWaypoints]);

  const positionedCameras = useMemo(() =>
    camerasWithProximity.filter(c => c.gps_lat || c.location?.coordinates),
    [camerasWithProximity]
  );

  return {
    allCameras: camerasWithProximity,
    positionedCameras,
    loading,
    reload: loadCameras
  };
};

export default useCameraLayer;

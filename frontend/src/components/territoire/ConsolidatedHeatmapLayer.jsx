/**
 * ConsolidatedHeatmapLayer.jsx — Score consolidé multi-moteurs (data-only)
 * RECABLE V7: Consomme /api/v7/spatial/heatmap (SPATIAL-ENGINE-V7)
 * dataVersion: V7 — BCE-4X TRACE-LOG-Omega
 */
import { useEffect, useRef, useCallback } from 'react';
import { useAuth } from '@/components/GlobalAuth';

const ConsolidatedHeatmapLayer = ({
  center,
  species = 'CERF',
  month = 10,
  enabled = true,
  onDataLoaded = null,
  includeCorridors = true,
}) => {
  const { token } = useAuth();
  const cacheRef = useRef(null);
  const lastKeyRef = useRef('');
  const abortRef = useRef(null);
  const onDataLoadedRef = useRef(onDataLoaded);
  onDataLoadedRef.current = onDataLoaded;

  const centerLat = center?.lat;
  const centerLng = center?.lng;

  const fetchData = useCallback(async () => {
    if (centerLat == null || centerLng == null || !enabled) return;

    const key = `${centerLat.toFixed(6)}:${centerLng.toFixed(6)}:${species}:${month}:${includeCorridors ? 1 : 0}`;

    if (lastKeyRef.current === key && cacheRef.current) {
      if (onDataLoadedRef.current) onDataLoadedRef.current(cacheRef.current);
      return;
    }
    lastKeyRef.current = key;

    if (abortRef.current) abortRef.current.abort();
    abortRef.current = new AbortController();

    try {
      const apiUrl = process.env.REACT_APP_BACKEND_URL;
      const headers = token ? { Authorization: `Bearer ${token}` } : {};
      const params = new URLSearchParams({
        lat: centerLat, lon: centerLng,
        species: species === 'CERF' ? 'cerf' : species.toLowerCase(),
        month, grid_size: 12,
      });
      // V7 RECABLE: SPATIAL-ENGINE-V7
      const res = await fetch(`${apiUrl}/api/v7/spatial/heatmap?${params}`, {
        headers,
        signal: abortRef.current.signal,
      });
      if (!res.ok) return;
      const data = await res.json();

      // Adapter la sortie V7 au format attendu par le callback
      const adapted = {
        ...data,
        dataVersion: 'V7',
        score_global: data.points ? Math.round(data.points.reduce((s, p) => s + p.score, 0) / data.points.length) : 0,
        grid: data.points || [],
      };
      cacheRef.current = adapted;

      if (lastKeyRef.current === key && onDataLoadedRef.current) {
        onDataLoadedRef.current(adapted);
      }
    } catch (err) {
      if (err.name === 'AbortError') return;
      if (err.name === 'DataCloneError') {
        try {
          const apiUrl = process.env.REACT_APP_BACKEND_URL;
          const retryHeaders = token ? { Authorization: `Bearer ${token}` } : {};
          const params = new URLSearchParams({
            lat: centerLat, lon: centerLng,
            species: species === 'CERF' ? 'cerf' : species.toLowerCase(), month, grid_size: 12,
          });
          const retryRes = await fetch(`${apiUrl}/api/v7/spatial/heatmap?${params}`, { headers: retryHeaders });
          if (retryRes.ok) {
            const data = await retryRes.json();
            const adapted = { ...data, dataVersion: 'V7', score_global: data.points ? Math.round(data.points.reduce((s, p) => s + p.score, 0) / data.points.length) : 0, grid: data.points || [] };
            cacheRef.current = adapted;
            if (lastKeyRef.current === key && onDataLoadedRef.current) onDataLoadedRef.current(adapted);
          }
        } catch (retryErr) { console.error('[HEATMAP-V7] Retry failed:', retryErr); }
      } else {
        console.error('[HEATMAP-V7]', err);
      }
    }
  }, [centerLat, centerLng, species, month, enabled, includeCorridors, token]);

  useEffect(() => {
    fetchData();
    return () => { if (abortRef.current) abortRef.current.abort(); };
  }, [fetchData]);

  return null;
};

export default ConsolidatedHeatmapLayer;

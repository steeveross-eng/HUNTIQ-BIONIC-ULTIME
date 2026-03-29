/**
 * useAccessRoute.js — Hook unique GOLDEN pour acces aux affuts V6
 * PROTOCOLE BIONIC GOLDEN | BCE-4X | STEEVE-MAX
 * Branche: STEEVE-MAX-x3200-V6-CORE
 *
 * 1 hook unique — ZERO duplication autorisee.
 * Appelle POST /api/v6/access/compute et gere l'etat du resultat.
 */
import { useState, useCallback } from 'react';

const API = process.env.REACT_APP_BACKEND_URL;

export function useAccessRoute() {
  const [accessRoute, setAccessRoute] = useState(null);
  const [accessLoading, setAccessLoading] = useState(false);
  const [accessError, setAccessError] = useState(null);

  const computeAccess = useCallback(async (origin, destination, options = {}) => {
    if (!origin || !destination) return;

    setAccessLoading(true);
    setAccessError(null);

    try {
      const body = {
        origin: { lat: origin.lat, lng: origin.lng },
        destination: { lat: destination.lat, lng: destination.lng },
        month: options.month || new Date().getMonth() + 1,
        species: options.species || 'orignal',
        options: {
          max_off_trail_km: options.max_off_trail_km || 2.0,
          prefer_trails: options.prefer_trails !== false,
          analysis_radius_m: options.analysis_radius_m || 3000,
        },
      };

      const resp = await fetch(`${API}/api/v6/access/compute`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });

      if (!resp.ok) {
        throw new Error(`Erreur API access: ${resp.status}`);
      }

      const data = await resp.json();
      setAccessRoute(data);
      return data;
    } catch (err) {
      setAccessError(err.message);
      setAccessRoute(null);
      return null;
    } finally {
      setAccessLoading(false);
    }
  }, []);

  const clearAccessRoute = useCallback(() => {
    setAccessRoute(null);
    setAccessError(null);
  }, []);

  return {
    accessRoute,
    accessLoading,
    accessError,
    computeAccess,
    clearAccessRoute,
  };
}

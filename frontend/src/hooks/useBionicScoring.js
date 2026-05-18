/**
 * useBionicScoring Hook
 * Calcule les scores BIONIC pour un waypoint ou une position
 * P22ΩΩ_PALIER_3_MIGRATION_V7_SPATIAL_Ω · 2026-05-18 · STEEVE-MAX
 *   Note : ce hook utilise /api/v1/v51/intelligence/v7/score-chasse (Intelligence V7)
 *   et NON pas /api/v7/spatial/scoring. Aucune migration requise ici.
 * dataVersion: Ω — BCE-4X TRACE-LOG-Omega
 */

import { useState, useCallback, useRef } from 'react';
import { 
  getScoresForWaypoint, 
  calculateHybridScore,
  adaptWaypointData 
} from '@/core/bionic';

const API = process.env.REACT_APP_BACKEND_URL;

const useBionicScoring = () => {
  const [scores, setScores] = useState(null);
  const [isCalculating, setIsCalculating] = useState(false);
  const [error, setError] = useState(null);
  const [lastCalculation, setLastCalculation] = useState(null);
  const [scoreChasseV7, setScoreChasseV7] = useState(null);
  
  const cacheRef = useRef(new Map());
  
  /**
   * Calcule les scores pour un waypoint (version simple)
   */
  const calculateScores = useCallback((waypointData, contextData = {}) => {
    try {
      setIsCalculating(true);
      setError(null);
      
      // Adapter les données
      const adaptedData = adaptWaypointData(waypointData, contextData);
      
      // Calculer les scores
      const result = getScoresForWaypoint(adaptedData);
      
      setScores(result);
      setLastCalculation(new Date().toISOString());
      
      return result;
    } catch (err) {
      setError(err.message);
      console.error('Scoring error:', err);
      return null;
    } finally {
      setIsCalculating(false);
    }
  }, []);
  
  /**
   * Calcule les scores avec le modèle hybride (règles + IA)
   */
  const calculateHybridScores = useCallback(async (waypointData, weather = null, useAI = true) => {
    try {
      setIsCalculating(true);
      setError(null);
      
      // Vérifier le cache
      const cacheKey = `${waypointData.latitude}_${waypointData.longitude}_${useAI}`;
      const cached = cacheRef.current.get(cacheKey);
      
      if (cached && Date.now() - cached.timestamp < 60000) { // Cache de 1 minute
        setScores(cached.result);
        return cached.result;
      }
      
      // Adapter les données
      const adaptedData = adaptWaypointData(waypointData);
      
      // Calculer avec le modèle hybride
      const result = await calculateHybridScore(adaptedData, weather, useAI);
      
      // Mettre en cache
      cacheRef.current.set(cacheKey, {
        result,
        timestamp: Date.now()
      });
      
      // Nettoyer le cache si trop grand
      if (cacheRef.current.size > 100) {
        const firstKey = cacheRef.current.keys().next().value;
        cacheRef.current.delete(firstKey);
      }
      
      setScores(result);
      setLastCalculation(new Date().toISOString());
      
      return result;
    } catch (err) {
      setError(err.message);
      console.error('Hybrid scoring error:', err);
      return null;
    } finally {
      setIsCalculating(false);
    }
  }, []);
  
  /**
   * Calcule les scores pour plusieurs waypoints
   */
  const calculateBatchScores = useCallback(async (waypoints, contextData = {}) => {
    try {
      setIsCalculating(true);
      setError(null);
      
      const results = await Promise.all(
        waypoints.map(async (wp) => {
          const adaptedData = adaptWaypointData(wp, contextData);
          return {
            waypointId: wp.id,
            ...getScoresForWaypoint(adaptedData)
          };
        })
      );
      
      return results;
    } catch (err) {
      setError(err.message);
      console.error('Batch scoring error:', err);
      return [];
    } finally {
      setIsCalculating(false);
    }
  }, []);
  
  /**
   * Réinitialise les scores
   */
  const resetScores = useCallback(() => {
    setScores(null);
    setError(null);
    setLastCalculation(null);
  }, []);
  
  /**
   * Vide le cache
   */
  const clearCache = useCallback(() => {
    cacheRef.current.clear();
  }, []);

  /**
   * Fetch Score Chasse V7 depuis INTELLIGENCE-V7
   * RECABLE V7: /api/v1/v51/intelligence/v7/score-chasse
   */
  const fetchScoreChasseV7 = useCallback(async (lat, lon, species, token) => {
    try {
      const now = new Date();
      const params = new URLSearchParams({
        lat, lon, species: species || 'cerf',
        month: now.getMonth() + 1, day: now.getDate(), hour: now.getHours(),
        province: 'qc',
      });
      const headers = token ? { Authorization: `Bearer ${token}` } : {};
      const res = await fetch(`${API}/api/v1/v51/intelligence/v7/score-chasse?${params}`, { headers });
      if (res.ok) {
        const data = await res.json();
        setScoreChasseV7(data);
        return data;
      }
    } catch (err) {
      console.error('[SCORE-CHASSE-V7]', err);
    }
    return null;
  }, []);
  
  return {
    // État
    scores,
    isCalculating,
    error,
    lastCalculation,
    scoreChasseV7,
    
    // Actions
    calculateScores,
    calculateHybridScores,
    calculateBatchScores,
    resetScores,
    clearCache,
    fetchScoreChasseV7,
    
    // Raccourcis pour les scores individuels
    habitatScore: scores?.score_H,
    rutScore: scores?.score_R,
    salinesScore: scores?.score_S,
    affutsScore: scores?.score_A,
    trajetsScore: scores?.score_T,
    peuplementsScore: scores?.score_P,
    globalScore: scores?.score_Bionic_final || scores?.score_Bionic,
    // V7
    scoreChasseV7Score: scoreChasseV7?.score_chasse_v7,
    scoreChasseV7Prediction: scoreChasseV7?.prediction,
  };
};

export default useBionicScoring;

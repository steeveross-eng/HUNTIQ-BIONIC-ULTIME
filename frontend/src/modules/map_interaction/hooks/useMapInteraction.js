/**
 * useMapInteraction — x4500-ULTRA stub
 * Hook pour les interactions carte (click, drag, zoom)
 */
import { useState, useCallback } from 'react';

export const useMapInteraction = (options = {}) => {
  const [selectedPoint, setSelectedPoint] = useState(null);
  const [isDrawing, setIsDrawing] = useState(false);
  const [measureMode, setMeasureMode] = useState(false);

  const handleMapClick = useCallback((e) => {
    if (measureMode || isDrawing) return;
    setSelectedPoint(e?.latlng || null);
    options.onClick?.(e);
  }, [measureMode, isDrawing, options]);

  const startDrawing = useCallback(() => setIsDrawing(true), []);
  const stopDrawing = useCallback(() => setIsDrawing(false), []);
  const toggleMeasure = useCallback(() => setMeasureMode(prev => !prev), []);

  return {
    selectedPoint,
    setSelectedPoint,
    isDrawing,
    measureMode,
    handleMapClick,
    startDrawing,
    stopDrawing,
    toggleMeasure,
  };
};

export default useMapInteraction;

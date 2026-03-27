/**
 * BCE-4X Phase 2.6 — WindFlowLayer
 * Effet visuel du vent sur la carte Leaflet.
 * 
 * SOURCE UNIQUE: useWeatherStore (Weather V3)
 * ZERO fetch HTTP séparé.
 * Dessin direct sur canvas overlay.
 */
import { useEffect, useRef, useState, useCallback } from 'react';
import { useMap } from 'react-leaflet';
import L from 'leaflet';
import useWeatherStore from '../../stores/useWeatherStore';

export default function WindFlowLayer() {
  const map = useMap();
  const canvasRef = useRef(null);
  const cleanupRef = useRef(null);

  // Lire le store meteo
  const weatherCurrent = useWeatherStore(s => s.current);

  const drawWindArrows = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas || !map) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Resize canvas
    const size = map.getSize();
    if (size.x === 0 || size.y === 0) return;
    canvas.width = size.x;
    canvas.height = size.y;

    // Lire les donnees vent du store
    const store = useWeatherStore.getState();
    const current = store.current;
    const windSpeed = current?.wind_speed_kmh || 10;
    const windDir = current?.wind_direction_deg || 270;
    const windGust = current?.wind_gust_kmh || windSpeed * 1.5;
    const speedMs = windSpeed / 3.6;
    const maxSpeedMs = Math.max(speedMs * 1.3, windGust / 3.6);
    const dirRad = (windDir * Math.PI) / 180;

    // Calculer U et V base
    const baseU = -speedMs * Math.sin(dirRad);
    const baseV = -speedMs * Math.cos(dirRad);

    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Bounds de la carte
    const bounds = map.getBounds();
    const north = bounds.getNorth();
    const south = bounds.getSouth();
    const east = bounds.getEast();
    const west = bounds.getWest();

    // Grille de fleches
    const gridRes = 25;
    const spacingX = canvas.width / gridRes;
    const spacingY = canvas.height / gridRes;
    let arrowCount = 0;

    for (let r = 0; r < gridRes; r++) {
      for (let c = 0; c < gridRes; c++) {
        const px = (c + 0.5) * spacingX;
        const py = (r + 0.5) * spacingY;

        // Variation naturelle
        const variation = 1 + Math.sin(r * 0.7 + c * 0.5) * 0.12;
        const u = baseU * variation;
        const v = baseV * variation;
        const speed = Math.sqrt(u * u + v * v);

        if (speed < 0.3) continue;

        const angle = Math.atan2(-v, u);
        const t = Math.min(speed / maxSpeedMs, 1);
        const length = 14 + t * 32;
        const opacity = 0.4 + t * 0.35;

        // Tige
        const ex = px + length * Math.cos(angle);
        const ey = py + length * Math.sin(angle);

        ctx.beginPath();
        ctx.moveTo(px, py);
        ctx.lineTo(ex, ey);
        ctx.strokeStyle = `rgba(150, 220, 230, ${opacity})`;
        ctx.lineWidth = 1.8;
        ctx.stroke();

        // Pointe de fleche
        const headLen = 5 + t * 4;
        ctx.beginPath();
        ctx.moveTo(ex, ey);
        ctx.lineTo(ex - headLen * Math.cos(angle - 0.4), ey - headLen * Math.sin(angle - 0.4));
        ctx.moveTo(ex, ey);
        ctx.lineTo(ex - headLen * Math.cos(angle + 0.4), ey - headLen * Math.sin(angle + 0.4));
        ctx.strokeStyle = `rgba(150, 220, 230, ${opacity * 0.85})`;
        ctx.lineWidth = 1.8;
        ctx.stroke();

        arrowCount++;
      }
    }
  }, [map]);

  // Setup canvas + event listeners
  useEffect(() => {
    if (!map) return;

    const container = map.getContainer();
    let canvas = canvasRef.current;

    if (!canvas) {
      canvas = document.createElement('canvas');
      canvas.style.position = 'absolute';
      canvas.style.top = '0';
      canvas.style.left = '0';
      canvas.style.pointerEvents = 'none';
      canvas.style.zIndex = '400';
      container.appendChild(canvas);
      canvasRef.current = canvas;
    }

    // Draw immediately
    drawWindArrows();

    // Redraw on map events
    const onMoveEnd = () => drawWindArrows();
    const onResize = () => drawWindArrows();
    map.on('moveend', onMoveEnd);
    map.on('zoomend', onMoveEnd);
    map.on('resize', onResize);

    cleanupRef.current = () => {
      map.off('moveend', onMoveEnd);
      map.off('zoomend', onMoveEnd);
      map.off('resize', onResize);
      if (canvas.parentNode) canvas.parentNode.removeChild(canvas);
      canvasRef.current = null;
    };

    return () => {
      if (cleanupRef.current) cleanupRef.current();
    };
  }, [map, drawWindArrows]);

  // Redraw when weather data changes
  useEffect(() => {
    if (weatherCurrent && canvasRef.current) {
      drawWindArrows();
    }
  }, [weatherCurrent, drawWindArrows]);

  return null;
}

/**
 * BCE-4X — WindFlowLayer v5.0 ENGINE ATMOSPHÉRIQUE GLOBAL
 * ========================================================
 * STEEVE-MAX P0 — Champ de vent CONTINU sur toute la carte
 *
 * ARCHITECTURE:
 *   - Grille uniforme de particules couvrant 100% de l'écran
 *   - Chaque cellule contient une particule animée
 *   - Mouvement dans la direction réelle du vent
 *   - Quand une particule sort de sa cellule, elle se reset au centre
 *   - Résultat: couverture TOTALE, ZERO trou, ZERO îlot
 *
 *   - Densité adaptative au zoom (plus de cellules = même densité visuelle)
 *   - Vitesse calibrée sur la vitesse réelle
 *   - Trail directionnel avec tête de flèche
 *
 * SOURCE UNIQUE: useWeatherStore (Weather V3)
 * ZERO impact données météo. UI uniquement.
 */
import { useEffect, useRef } from 'react';
import { useMap } from 'react-leaflet';
import useWeatherStore from '../../stores/useWeatherStore';

// Espacement de la grille en pixels (chaque cellule a une particule)
const GRID_SPACING = 55;

// Opacité max
const MAX_OPACITY = 0.75;

// Couleurs: blanc-cyan net, ZERO glow
const TRAIL_COLOR = '210, 245, 255';
const HEAD_COLOR = '255, 255, 255';

// Tête de flèche directionnelle
const ARROW_LENGTH = 8;
const ARROW_WIDTH = 4;

// Trail: nombre de positions historiques
const TRAIL_LENGTH = 30;

// Épaisseur trail
const TRAIL_BASE_WIDTH = 1.0;
const TRAIL_TIP_WIDTH = 1.8;

const METERS_PER_DEG_LAT = 111320;

export default function WindFlowLayer() {
  const map = useMap();
  const canvasRef = useRef(null);
  const animFrameRef = useRef(null);
  const gridRef = useRef(null);
  const windRef = useRef({ speedKmh: 0, gustKmh: 0, dirDeg: 0 });
  const mountedRef = useRef(false);

  const current = useWeatherStore(s => s.current);

  useEffect(() => {
    if (!current) return;
    windRef.current = {
      speedKmh: current.wind_speed_kmh || 0,
      gustKmh: current.wind_gust_kmh || 0,
      dirDeg: current.wind_direction_deg || 0,
    };
  }, [current]);

  useEffect(() => {
    if (!map) return;

    const container = map.getContainer();
    const oldCanvas = container.querySelector('canvas[data-windlayer]');
    if (oldCanvas) oldCanvas.remove();

    const canvas = document.createElement('canvas');
    canvas.setAttribute('data-windlayer', 'v5.0');
    canvas.style.cssText = 'position:absolute;top:0;left:0;width:100%;height:100%;pointer-events:none;z-index:650;';
    container.appendChild(canvas);
    canvasRef.current = canvas;

    const size = map.getSize();
    canvas.width = size.x;
    canvas.height = size.y;
    mountedRef.current = true;

    // === CONSTRUCTION DE LA GRILLE ===
    const buildGrid = () => {
      const w = canvas.width;
      const h = canvas.height;
      const cols = Math.ceil(w / GRID_SPACING) + 2;
      const rows = Math.ceil(h / GRID_SPACING) + 2;
      const particles = [];

      for (let row = -1; row < rows; row++) {
        for (let col = -1; col < cols; col++) {
          // Centre de la cellule avec léger jitter pour éviter l'aspect "quadrillé"
          const cx = col * GRID_SPACING + GRID_SPACING / 2 + (Math.random() - 0.5) * GRID_SPACING * 0.3;
          const cy = row * GRID_SPACING + GRID_SPACING / 2 + (Math.random() - 0.5) * GRID_SPACING * 0.3;

          particles.push({
            // Position actuelle (en pixels écran)
            x: cx,
            y: cy,
            // Centre de la cellule (pour le reset)
            cellCx: col * GRID_SPACING + GRID_SPACING / 2,
            cellCy: row * GRID_SPACING + GRID_SPACING / 2,
            // Historique de trail
            trail: [],
            // Phase de vie (pour fade cyclique décalé)
            phase: Math.random() * Math.PI * 2,
            // Petite variation de vitesse par particule
            speedVar: 0.85 + Math.random() * 0.3,
          });
        }
      }

      gridRef.current = { particles, cols, rows };
    };

    buildGrid();

    let frameCount = 0;

    // === BOUCLE D'ANIMATION ===
    const animate = () => {
      if (!mountedRef.current) return;
      const cvs = canvasRef.current;
      if (!cvs) return;
      const ctx = cvs.getContext('2d');
      if (!ctx) { animFrameRef.current = requestAnimationFrame(animate); return; }

      const sz = map.getSize();
      if (cvs.width !== sz.x || cvs.height !== sz.y) {
        cvs.width = sz.x;
        cvs.height = sz.y;
      }

      const { speedKmh, dirDeg } = windRef.current;
      const dirRad = (dirDeg * Math.PI) / 180;
      frameCount++;

      // === VITESSE EN PIXELS/FRAME ===
      // Calibrée sur la vitesse réelle + zoom de la carte
      const speedMs = speedKmh / 3.6;
      const mapBounds = map.getBounds();
      const visibleLatSpan = Math.max(mapBounds.getNorth() - mapBounds.getSouth(), 0.0001);
      const pixelsPerDeg = sz.y / visibleLatSpan;
      const realDegPerFrame = speedMs / METERS_PER_DEG_LAT / 60;
      const realPxPerFrame = realDegPerFrame * pixelsPerDeg;

      // Amplification minimale pour que le mouvement soit visible (~1px/frame)
      const minPx = 1.0;
      const amp = realPxPerFrame > 0 ? Math.max(1, minPx / realPxPerFrame) : 1;
      const pxPerFrame = realPxPerFrame * amp;

      // Direction en coordonnées écran (Y inversé)
      // Vent FROM dirDeg → particules vont TOWARD opposé
      const screenDx = -Math.sin(dirRad) * pxPerFrame;
      const screenDy = Math.cos(dirRad) * pxPerFrame; // Y écran: bas = positif, nord = négatif

      ctx.clearRect(0, 0, cvs.width, cvs.height);

      const grid = gridRef.current;
      if (!grid) { animFrameRef.current = requestAnimationFrame(animate); return; }

      const w = cvs.width;
      const h = cvs.height;
      const halfCell = GRID_SPACING / 2;

      // Direction normalisée pour la flèche
      const dirLen = Math.sqrt(screenDx * screenDx + screenDy * screenDy);
      const normDx = dirLen > 0 ? screenDx / dirLen : 0;
      const normDy = dirLen > 0 ? screenDy / dirLen : 0;

      for (let i = 0; i < grid.particles.length; i++) {
        const p = grid.particles[i];

        // Mouvement
        p.x += screenDx * p.speedVar;
        p.y += screenDy * p.speedVar;

        // Enregistrer trail
        p.trail.push({ x: p.x, y: p.y });
        if (p.trail.length > TRAIL_LENGTH) p.trail.shift();

        // Reset quand la particule sort de sa cellule (rayon = cellSpacing)
        const dx = p.x - p.cellCx;
        const dy = p.y - p.cellCy;
        if (Math.abs(dx) > halfCell * 1.5 || Math.abs(dy) > halfCell * 1.5) {
          // Reset: revient au côté opposé de la cellule (entrée upwind)
          p.x = p.cellCx - normDx * halfCell;
          p.y = p.cellCy - normDy * halfCell;
          p.trail = [];
          continue;
        }

        // Vérifier si dans l'écran (avec marge)
        if (p.x < -GRID_SPACING || p.x > w + GRID_SPACING ||
            p.y < -GRID_SPACING || p.y > h + GRID_SPACING) continue;

        // Opacité: fade cyclique décalé par particule
        const cyclePhase = (frameCount * 0.015 + p.phase) % (Math.PI * 2);
        const fade = 0.5 + 0.5 * Math.sin(cyclePhase);
        const alpha = MAX_OPACITY * fade;
        if (alpha < 0.03) continue;

        // === TRAIL (fade-out progressif) ===
        if (p.trail.length > 1) {
          for (let t = 1; t < p.trail.length; t++) {
            const prev = p.trail[t - 1];
            const curr = p.trail[t];
            const tProgress = t / p.trail.length;
            const tAlpha = alpha * tProgress * 0.7;
            if (tAlpha < 0.01) continue;

            ctx.beginPath();
            ctx.moveTo(prev.x, prev.y);
            ctx.lineTo(curr.x, curr.y);
            ctx.strokeStyle = `rgba(${TRAIL_COLOR}, ${tAlpha})`;
            ctx.lineWidth = TRAIL_BASE_WIDTH + tProgress * (TRAIL_TIP_WIDTH - TRAIL_BASE_WIDTH);
            ctx.lineCap = 'round';
            ctx.stroke();
          }
        }

        // === TÊTE DE FLÈCHE DIRECTIONNELLE ===
        const tipX = p.x + normDx * ARROW_LENGTH * 0.5;
        const tipY = p.y + normDy * ARROW_LENGTH * 0.5;
        const baseX = p.x - normDx * ARROW_LENGTH * 0.5;
        const baseY = p.y - normDy * ARROW_LENGTH * 0.5;

        const perpX = -normDy;
        const perpY = normDx;
        const hw = ARROW_WIDTH * 0.5;

        ctx.beginPath();
        ctx.moveTo(tipX, tipY);
        ctx.lineTo(baseX + perpX * hw, baseY + perpY * hw);
        ctx.lineTo(baseX - perpX * hw, baseY - perpY * hw);
        ctx.closePath();
        ctx.fillStyle = `rgba(${HEAD_COLOR}, ${alpha})`;
        ctx.fill();
      }

      animFrameRef.current = requestAnimationFrame(animate);
    };

    animFrameRef.current = requestAnimationFrame(animate);

    // === MAP EVENTS: reconstruire la grille si resize/zoom ===
    const onViewChange = () => {
      const s = map.getSize();
      const cvs = canvasRef.current;
      if (cvs) { cvs.width = s.x; cvs.height = s.y; }
      buildGrid();
    };

    map.on('resize', onViewChange);
    map.on('zoomend', onViewChange);
    map.on('moveend', onViewChange);

    return () => {
      mountedRef.current = false;
      if (animFrameRef.current) cancelAnimationFrame(animFrameRef.current);
      map.off('resize', onViewChange);
      map.off('zoomend', onViewChange);
      map.off('moveend', onViewChange);
      if (canvas.parentNode) canvas.parentNode.removeChild(canvas);
      canvasRef.current = null;
    };
  }, [map]);

  return null;
}

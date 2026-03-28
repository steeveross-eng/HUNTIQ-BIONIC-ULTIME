/**
 * BCE-4X — WindFlowLayer SCIENTIFIQUE GEOLOCALISÉ v4.2
 * =====================================================
 * STEEVE-MAX P0 — Rétablissement rendu + P1 ajustements visuels
 *
 * CORRECTIF v4.2:
 *   - Boucle d'animation découplée du cycle React (useRef pattern)
 *   - ZERO re-creation du canvas sur re-render React
 *   - P1: -40% taille particules, -50% glow, +30% trail
 *   - Direction réelle, intensité réelle conservées
 *
 * SOURCE UNIQUE: useWeatherStore (Weather V3)
 * ZERO impact données météo. UI uniquement.
 */
import { useEffect, useRef } from 'react';
import { useMap } from 'react-leaflet';
import useWeatherStore from '../../stores/useWeatherStore';

// --- CONFIGURATION v4.2 (P1 ajustements appliqués) ---

// Densité: 140 particules
const PARTICLE_COUNT = 140;

// Opacité: 0.64 (base -15%)
const MAX_OPACITY = 0.64;

// P1: -40% taille (3.0 → 1.8)
const PARTICLE_SIZE = 1.8;
const TRAIL_WIDTH = 1.4;

// Couleurs: cyan-blanc lumineux (+25%)
const TRAIL_COLOR = '220, 255, 255';
const HEAD_COLOR = '255, 255, 255';

// P1: -50% glow (opacity factor 0.35 → 0.175, size 4.0 → 2.0)
const HALO_COLOR = '100, 220, 255';
const HALO_OPACITY_FACTOR = 0.175;
const HALO_SIZE_FACTOR = 2.0;

// Conversion géo
const METERS_PER_DEG_LAT = 111320;

// Amplification visuelle (standard Windy.com)
const VISUAL_SPEED_MULTIPLIER = 5000;

// P1: +30% trail (6 → 8, 25 → 32)
const MIN_TRAIL_LENGTH = 8;
const MAX_TRAIL_LENGTH = 32;

export default function WindFlowLayer() {
  const map = useMap();
  const canvasRef = useRef(null);
  const animFrameRef = useRef(null);
  const particlesRef = useRef([]);
  const windRef = useRef({ speedKmh: 0, gustKmh: 0, dirDeg: 0 });
  const timeRef = useRef(0);
  const mountedRef = useRef(false);

  // Source unique: useWeatherStore V3
  const current = useWeatherStore(s => s.current);

  // Mise à jour vent via ref (pas de re-render)
  useEffect(() => {
    if (!current) return;
    windRef.current = {
      speedKmh: current.wind_speed_kmh || 0,
      gustKmh: current.wind_gust_kmh || 0,
      dirDeg: current.wind_direction_deg || 0,
    };
  }, [current]);

  // === EFFET UNIQUE: setup canvas + boucle animation ===
  // Dépend SEULEMENT de `map` — ne se recrée JAMAIS sur re-render React
  useEffect(() => {
    if (!map) return;

    const container = map.getContainer();

    // Nettoyer un éventuel canvas fantôme d'un render précédent
    const oldCanvas = container.querySelector('canvas[data-windlayer]');
    if (oldCanvas) oldCanvas.remove();

    // Créer le canvas
    const canvas = document.createElement('canvas');
    canvas.setAttribute('data-windlayer', 'v4.2');
    canvas.style.cssText = 'position:absolute;top:0;left:0;width:100%;height:100%;pointer-events:none;z-index:650;';
    container.appendChild(canvas);
    canvasRef.current = canvas;

    const size = map.getSize();
    canvas.width = size.x;
    canvas.height = size.y;
    mountedRef.current = true;

    // --- Fonctions utilitaires (inline, pas de useCallback) ---

    const getGeoBounds = () => {
      const bounds = map.getBounds();
      const sw = bounds.getSouthWest();
      const ne = bounds.getNorthEast();
      const latSpan = ne.lat - sw.lat;
      const lngSpan = ne.lng - sw.lng;
      return {
        south: sw.lat - latSpan * 0.15,
        north: ne.lat + latSpan * 0.15,
        west: sw.lng - lngSpan * 0.15,
        east: ne.lng + lngSpan * 0.15,
      };
    };

    const createParticle = (bounds, fromUpwind) => {
      const { dirDeg, speedKmh, gustKmh } = windRef.current;
      const dirRad = (dirDeg * Math.PI) / 180;

      let lat, lng;
      if (fromUpwind && speedKmh > 0.2) {
        const moveX = -Math.sin(dirRad);
        const moveY = -Math.cos(dirRad);
        if (Math.abs(moveX) > Math.abs(moveY)) {
          lng = moveX > 0 ? bounds.west : bounds.east;
          lat = bounds.south + Math.random() * (bounds.north - bounds.south);
        } else {
          lat = moveY > 0 ? bounds.south : bounds.north;
          lng = bounds.west + Math.random() * (bounds.east - bounds.west);
        }
      } else {
        lat = bounds.south + Math.random() * (bounds.north - bounds.south);
        lng = bounds.west + Math.random() * (bounds.east - bounds.west);
      }

      const gustFactor = gustKmh > speedKmh && Math.random() > 0.6
        ? 0.8 + Math.random() * (gustKmh / Math.max(speedKmh, 0.5)) * 0.3
        : 0.7 + Math.random() * 0.6;

      return {
        lat, lng, gustFactor,
        age: fromUpwind ? 0 : Math.random() * 0.7,
        maxAge: 0.6 + Math.random() * 0.4,
        wavyOffset: Math.random() * Math.PI * 2,
        prevScreenX: null,
        prevScreenY: null,
      };
    };

    // Initialiser les particules
    const bounds = getGeoBounds();
    const particles = [];
    for (let i = 0; i < PARTICLE_COUNT; i++) {
      particles.push(createParticle(bounds, false));
    }
    particlesRef.current = particles;

    // === BOUCLE D'ANIMATION (stable, découplée de React) ===
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
      timeRef.current += 1;
      const t = timeRef.current;

      const speedMs = speedKmh / 3.6;
      const speedDegPerFrame = (speedMs / METERS_PER_DEG_LAT / 60) * VISUAL_SPEED_MULTIPLIER;

      const dLng = -Math.sin(dirRad) * speedDegPerFrame;
      const dLat = -Math.cos(dirRad) * speedDegPerFrame;

      ctx.clearRect(0, 0, cvs.width, cvs.height);

      const bds = getGeoBounds();
      const pts = particlesRef.current;
      const w = cvs.width;
      const h = cvs.height;

      for (let i = 0; i < pts.length; i++) {
        const p = pts[i];

        // Déplacement géo + ondulation
        const wavyPhase = t * 0.02 + p.wavyOffset + i * 0.11;
        const wavyAmp = speedDegPerFrame * 0.25;
        const perpDLat = Math.cos(dirRad + Math.PI / 2) * Math.sin(wavyPhase) * wavyAmp;
        const perpDLng = Math.sin(dirRad + Math.PI / 2) * Math.sin(wavyPhase) * wavyAmp;

        p.lat += dLat * p.gustFactor + perpDLat;
        p.lng += dLng * p.gustFactor + perpDLng;
        p.age += 0.004;

        // Cycle de vie: quand age > maxAge, RESET en place (pas de recyclage)
        // La particule reste sur la carte et recommence un cycle de fade
        // Elle ne meurt QUE quand elle sort des bounds géographiques
        if (p.age > p.maxAge) {
          p.age = 0;
          p.maxAge = 0.6 + Math.random() * 0.4;
          p.gustFactor = 0.7 + Math.random() * 0.6;
          p.wavyOffset = Math.random() * Math.PI * 2;
          // prevScreen conservé pour continuité du trail
        }

        // Recycler SEULEMENT si hors bounds géographiques
        if (p.lat < bds.south || p.lat > bds.north ||
            p.lng < bds.west || p.lng > bds.east) {
          const newP = createParticle(bds, true);
          p.lat = newP.lat;
          p.lng = newP.lng;
          p.gustFactor = newP.gustFactor;
          p.age = 0;
          p.maxAge = newP.maxAge;
          p.wavyOffset = newP.wavyOffset;
          p.prevScreenX = null;
          p.prevScreenY = null;
          continue;
        }

        // Géo → écran
        const sp = map.latLngToContainerPoint([p.lat, p.lng]);
        const sx = sp.x;
        const sy = sp.y;

        if (sx < -30 || sx > w + 30 || sy < -30 || sy > h + 30) {
          p.prevScreenX = sx; p.prevScreenY = sy;
          continue;
        }

        // Fade cycle de vie
        const lifeProgress = p.age / p.maxAge;
        const fadeEnvelope = Math.sin(lifeProgress * Math.PI);
        const alpha = MAX_OPACITY * fadeEnvelope * Math.min(1, p.gustFactor);

        if (alpha < 0.015) { p.prevScreenX = sx; p.prevScreenY = sy; continue; }

        // Trail
        const hasPrev = p.prevScreenX !== null;
        let trailX = hasPrev ? p.prevScreenX : sx;
        let trailY = hasPrev ? p.prevScreenY : sy;

        let dx = sx - trailX;
        let dy = sy - trailY;
        let dist = Math.sqrt(dx * dx + dy * dy);

        // Trail minimum garanti
        if (dist < MIN_TRAIL_LENGTH && speedKmh > 0) {
          const windDx = -Math.sin(dirRad);
          const windDy = -Math.cos(dirRad);
          trailX = sx - windDx * MIN_TRAIL_LENGTH;
          trailY = sy + windDy * MIN_TRAIL_LENGTH;
          dx = sx - trailX;
          dy = sy - trailY;
          dist = Math.sqrt(dx * dx + dy * dy);
        }

        // Trail max
        if (dist > MAX_TRAIL_LENGTH) {
          const ratio = MAX_TRAIL_LENGTH / dist;
          trailX = sx - dx * ratio;
          trailY = sy - dy * ratio;
        }

        // === GLOW (-50% P1) ===
        const haloAlpha = alpha * HALO_OPACITY_FACTOR;

        ctx.beginPath();
        ctx.moveTo(trailX, trailY);
        ctx.lineTo(sx, sy);
        ctx.strokeStyle = `rgba(${HALO_COLOR}, ${haloAlpha})`;
        ctx.lineWidth = PARTICLE_SIZE * HALO_SIZE_FACTOR;
        ctx.lineCap = 'round';
        ctx.stroke();

        // === TRAIL ===
        ctx.beginPath();
        ctx.moveTo(trailX, trailY);
        ctx.lineTo(sx, sy);
        ctx.strokeStyle = `rgba(${TRAIL_COLOR}, ${alpha * 0.7})`;
        ctx.lineWidth = TRAIL_WIDTH;
        ctx.lineCap = 'round';
        ctx.stroke();

        // === TÊTE ===
        ctx.beginPath();
        ctx.arc(sx, sy, PARTICLE_SIZE * 0.6, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(${HEAD_COLOR}, ${alpha})`;
        ctx.fill();

        p.prevScreenX = sx;
        p.prevScreenY = sy;
      }

      animFrameRef.current = requestAnimationFrame(animate);
    };

    // Démarrer l'animation
    animFrameRef.current = requestAnimationFrame(animate);

    // --- Map events ---
    const onViewChange = () => {
      const s = map.getSize();
      const cvs = canvasRef.current;
      if (cvs) { cvs.width = s.x; cvs.height = s.y; }
      const newBds = getGeoBounds();
      const pts = particlesRef.current;
      for (let i = 0; i < pts.length; i++) {
        const p = pts[i];
        if (p.lat < newBds.south || p.lat > newBds.north ||
            p.lng < newBds.west || p.lng > newBds.east) {
          const newP = createParticle(newBds, false);
          p.lat = newP.lat; p.lng = newP.lng;
          p.age = Math.random() * 0.4;
          p.prevScreenX = null; p.prevScreenY = null;
        }
      }
    };

    map.on('resize', onViewChange);
    map.on('zoomend', onViewChange);
    map.on('moveend', onViewChange);

    // Cleanup
    return () => {
      mountedRef.current = false;
      if (animFrameRef.current) cancelAnimationFrame(animFrameRef.current);
      map.off('resize', onViewChange);
      map.off('zoomend', onViewChange);
      map.off('moveend', onViewChange);
      if (canvas.parentNode) canvas.parentNode.removeChild(canvas);
      canvasRef.current = null;
    };
  }, [map]); // SEULEMENT `map` — découplé de React render cycle

  return null;
}

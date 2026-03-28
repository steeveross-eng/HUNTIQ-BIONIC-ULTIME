/**
 * BCE-4X — WindFlowLayer SCIENTIFIQUE GEOLOCALISÉ v4.1
 * =====================================================
 * STEEVE-MAX P0 — Correctif rendu visuel
 *
 * MOTEUR GEOLOCALISÉ:
 *   - Particules ancrées en coordonnées GPS (lat/lng)
 *   - Flux suit le déplacement de la carte (pan)
 *   - Recalcul dynamique au zoom
 *   - Direction réelle: weather_v3.wind_direction_deg
 *   - Intensité réelle: weather_v3.wind_speed_kmh
 *   - Rafales: weather_v3.wind_gust_kmh
 *
 * CORRECTIF v4.1:
 *   - Amplification visuelle du déplacement (comme Windy.com / earth.nullschool.net)
 *   - Taille de particule augmentée pour visibilité sur satellite
 *   - Trail allongé pour vent faible (4-5 km/h)
 *   - Halo clair (cyan) au lieu de noir sur fond sombre
 *   - z-index 650 garanti au-dessus de tous les panes Leaflet
 *   - Spawn initial distribué + upwind pour flux continu
 *
 * AJUSTEMENT STEEVE-MAX conservé:
 *   - -15% densité (119 particules)
 *   - -15% opacité (0.51 base x 0.85 = ~0.434 max)
 *   - +25% luminosité (couleurs cyan-blanc)
 *
 * SOURCE UNIQUE: useWeatherStore (Weather V3)
 * ZERO impact données météo. UI uniquement.
 */
import { useEffect, useRef, useCallback } from 'react';
import { useMap } from 'react-leaflet';
import useWeatherStore from '../../stores/useWeatherStore';

// -15% densité appliquée sur base 165 → 140
const PARTICLE_COUNT = 140;

// -15% opacité appliquée sur base 0.75 → 0.64
const MAX_OPACITY = 0.64;

// Taille visible sur satellite (3px minimum pour contraste)
const PARTICLE_SIZE = 3.0;
const TRAIL_WIDTH = 2.2;

// +25% luminosité — blanc pur pour la tête, cyan très clair pour le trail
const TRAIL_COLOR = '220, 255, 255';
const HEAD_COLOR = '255, 255, 255';

// Glow lumineux cyan pour contraste maximal sur satellite sombre
const HALO_COLOR = '100, 220, 255';
const HALO_OPACITY_FACTOR = 0.35;
const HALO_SIZE_FACTOR = 4.0;

// Conversion géo
const METERS_PER_DEG_LAT = 111320;

// === CLÉ DU CORRECTIF v4.1 ===
// Amplification visuelle: les vrais outils météo (Windy, earth.nullschool)
// amplifient le déplacement ~3000-8000x pour que 5 km/h soit visible.
// Sans amplification: 4.3 km/h = 0.00014 px/frame (invisible)
// Avec: 4.3 km/h = ~2-4 px/frame (flux visible et fluide)
const VISUAL_SPEED_MULTIPLIER = 5000;

// Trail minimum pour vent très faible (px)
const MIN_TRAIL_LENGTH = 6;

// Longueur max trail (px) pour limiter les stries
const MAX_TRAIL_LENGTH = 25;

// Fade rate pour cycle de vie
const FADE_RATE = 0.92;

export default function WindFlowLayer() {
  const map = useMap();
  const canvasRef = useRef(null);
  const animFrameRef = useRef(null);
  const particlesRef = useRef([]);
  const windRef = useRef({ speedKmh: 0, gustKmh: 0, dirDeg: 0 });
  const timeRef = useRef(0);

  const current = useWeatherStore(s => s.current);

  // Mettre à jour le vent depuis V3
  useEffect(() => {
    if (!current) return;
    windRef.current = {
      speedKmh: current.wind_speed_kmh || 0,
      gustKmh: current.wind_gust_kmh || 0,
      dirDeg: current.wind_direction_deg || 0,
    };
  }, [current]);

  // Bounds géographiques avec marge
  const getGeoBounds = useCallback(() => {
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
      latSpan,
      lngSpan,
    };
  }, [map]);

  // Créer une particule
  const createParticle = useCallback((bounds, fromUpwind) => {
    const { dirDeg, speedKmh, gustKmh } = windRef.current;
    const dirRad = (dirDeg * Math.PI) / 180;

    let lat, lng;
    if (fromUpwind && speedKmh > 0.2) {
      // Direction du mouvement des particules (avec le vent)
      const moveX = -Math.sin(dirRad); // composante lng du mouvement
      const moveY = -Math.cos(dirRad); // composante lat du mouvement

      // Spawn au bord UPWIND (opposé à la direction de mouvement)
      if (Math.abs(moveX) > Math.abs(moveY)) {
        // Vent principalement horizontal
        // moveX > 0 (vers est) → spawn à l'ouest
        lng = moveX > 0 ? bounds.west : bounds.east;
        lat = bounds.south + Math.random() * (bounds.north - bounds.south);
      } else {
        // Vent principalement vertical
        // moveY > 0 (vers nord) → spawn au sud
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
      lat,
      lng,
      gustFactor,
      age: fromUpwind ? 0 : Math.random() * 0.7,
      maxAge: 0.6 + Math.random() * 0.4,
      wavyOffset: Math.random() * Math.PI * 2,
      prevScreenX: null,
      prevScreenY: null,
    };
  }, []);

  // Initialiser les particules
  const resetParticles = useCallback(() => {
    const bounds = getGeoBounds();
    const particles = [];
    for (let i = 0; i < PARTICLE_COUNT; i++) {
      particles.push(createParticle(bounds, false));
    }
    particlesRef.current = particles;
  }, [getGeoBounds, createParticle]);

  // === BOUCLE D'ANIMATION PRINCIPALE ===
  const animate = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const size = map.getSize();
    if (canvas.width !== size.x || canvas.height !== size.y) {
      canvas.width = size.x;
      canvas.height = size.y;
    }

    const { speedKmh, dirDeg } = windRef.current;
    const dirRad = (dirDeg * Math.PI) / 180;
    timeRef.current += 1;
    const t = timeRef.current;

    // Déplacement géo réel (puis amplifié visuellement)
    const speedMs = speedKmh / 3.6;
    const speedDegPerFrame = (speedMs / METERS_PER_DEG_LAT / 60) * VISUAL_SPEED_MULTIPLIER;

    // Composantes géo du vent: dirDeg = direction FROM which wind blows (météo standard)
    // Particules se déplacent AVEC le vent (vers dirDeg + 180°)
    // sin/cos sur compass bearing: sin = composante Est, cos = composante Nord
    const dLng = -Math.sin(dirRad) * speedDegPerFrame;  // opposé au source
    const dLat = -Math.cos(dirRad) * speedDegPerFrame;  // opposé au source

    // Effacer le canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.globalCompositeOperation = 'source-over';

    const bounds = getGeoBounds();
    const particles = particlesRef.current;
    const w = canvas.width;
    const h = canvas.height;

    for (let i = 0; i < particles.length; i++) {
      const p = particles[i];

      // Déplacement géo avec ondulation organique
      const wavyPhase = t * 0.02 + p.wavyOffset + i * 0.11;
      const wavyAmp = speedDegPerFrame * 0.25;
      const perpDLat = Math.cos(dirRad + Math.PI / 2) * Math.sin(wavyPhase) * wavyAmp;
      const perpDLng = Math.sin(dirRad + Math.PI / 2) * Math.sin(wavyPhase) * wavyAmp;

      p.lat += dLat * p.gustFactor + perpDLat;
      p.lng += dLng * p.gustFactor + perpDLng;
      p.age += 0.004;

      // Recycler si hors bounds ou trop vieux
      if (p.lat < bounds.south || p.lat > bounds.north ||
          p.lng < bounds.west || p.lng > bounds.east ||
          p.age > p.maxAge) {
        const newP = createParticle(bounds, true);
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

      // Conversion géo → écran
      const screenPoint = map.latLngToContainerPoint([p.lat, p.lng]);
      const sx = screenPoint.x;
      const sy = screenPoint.y;

      if (sx < -30 || sx > w + 30 || sy < -30 || sy > h + 30) {
        p.prevScreenX = sx;
        p.prevScreenY = sy;
        continue;
      }

      // Enveloppe de fondu (cycle de vie)
      const lifeProgress = p.age / p.maxAge;
      const fadeEnvelope = Math.sin(lifeProgress * Math.PI);
      const alpha = MAX_OPACITY * fadeEnvelope * Math.min(1, p.gustFactor);

      if (alpha < 0.015) {
        p.prevScreenX = sx;
        p.prevScreenY = sy;
        continue;
      }

      // Trail depuis position précédente
      const hasPrev = p.prevScreenX !== null;
      let trailX = hasPrev ? p.prevScreenX : sx;
      let trailY = hasPrev ? p.prevScreenY : sy;

      // Calculer longueur du trail
      let dx = sx - trailX;
      let dy = sy - trailY;
      let dist = Math.sqrt(dx * dx + dy * dy);

      // Garantir un trail minimum visible même à vent très faible
      if (dist < MIN_TRAIL_LENGTH && speedKmh > 0) {
        const windScreenDx = -Math.sin(dirRad);
        const windScreenDy = -Math.cos(dirRad);
        const extendLen = MIN_TRAIL_LENGTH;
        trailX = sx - windScreenDx * extendLen;
        trailY = sy + windScreenDy * extendLen;
        dx = sx - trailX;
        dy = sy - trailY;
        dist = Math.sqrt(dx * dx + dy * dy);
      }

      // Limiter la longueur max du trail
      if (dist > MAX_TRAIL_LENGTH) {
        const ratio = MAX_TRAIL_LENGTH / dist;
        trailX = sx - dx * ratio;
        trailY = sy - dy * ratio;
      }

      // === HALO LUMINEUX (glow cyan pour contraste maximal) ===
      const haloAlpha = alpha * HALO_OPACITY_FACTOR;

      // Glow externe large
      ctx.beginPath();
      ctx.moveTo(trailX, trailY);
      ctx.lineTo(sx, sy);
      ctx.strokeStyle = `rgba(${HALO_COLOR}, ${haloAlpha * 0.3})`;
      ctx.lineWidth = PARTICLE_SIZE * HALO_SIZE_FACTOR * 1.5;
      ctx.lineCap = 'round';
      ctx.stroke();

      // Glow interne
      ctx.beginPath();
      ctx.moveTo(trailX, trailY);
      ctx.lineTo(sx, sy);
      ctx.strokeStyle = `rgba(${HALO_COLOR}, ${haloAlpha * 0.6})`;
      ctx.lineWidth = PARTICLE_SIZE * HALO_SIZE_FACTOR;
      ctx.lineCap = 'round';
      ctx.stroke();

      // Glow tête
      ctx.beginPath();
      ctx.arc(sx, sy, PARTICLE_SIZE * HALO_SIZE_FACTOR * 0.5, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(${HALO_COLOR}, ${haloAlpha * 0.8})`;
      ctx.fill();

      // === PARTICULE LUMINEUSE (trail + tête) ===
      ctx.beginPath();
      ctx.moveTo(trailX, trailY);
      ctx.lineTo(sx, sy);
      ctx.strokeStyle = `rgba(${TRAIL_COLOR}, ${alpha * 0.7})`;
      ctx.lineWidth = TRAIL_WIDTH;
      ctx.lineCap = 'round';
      ctx.stroke();

      // Tête de particule — blanche et lumineuse
      ctx.beginPath();
      ctx.arc(sx, sy, PARTICLE_SIZE * 0.7, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(${HEAD_COLOR}, ${alpha})`;
      ctx.fill();

      p.prevScreenX = sx;
      p.prevScreenY = sy;
    }

    animFrameRef.current = requestAnimationFrame(animate);
  }, [map, getGeoBounds, createParticle]);

  // Lifecycle: setup canvas, bind map events
  useEffect(() => {
    if (!map) return;

    const container = map.getContainer();
    const canvas = document.createElement('canvas');
    // z-index 650: au-dessus de overlay-pane(400), shadow-pane(500), sous marker-pane(600+) — correction v4.1
    canvas.style.cssText = 'position:absolute;top:0;left:0;width:100%;height:100%;pointer-events:none;z-index:650;';
    container.appendChild(canvas);
    canvasRef.current = canvas;

    const size = map.getSize();
    canvas.width = size.x;
    canvas.height = size.y;
    resetParticles();

    animFrameRef.current = requestAnimationFrame(animate);

    const onViewChange = () => {
      const s = map.getSize();
      if (canvasRef.current) {
        canvasRef.current.width = s.x;
        canvasRef.current.height = s.y;
      }
      const bounds = getGeoBounds();
      const particles = particlesRef.current;
      for (let i = 0; i < particles.length; i++) {
        const p = particles[i];
        if (p.lat < bounds.south || p.lat > bounds.north ||
            p.lng < bounds.west || p.lng > bounds.east) {
          const newP = createParticle(bounds, false);
          p.lat = newP.lat;
          p.lng = newP.lng;
          p.age = Math.random() * 0.4;
          p.prevScreenX = null;
          p.prevScreenY = null;
        }
      }
    };

    map.on('resize', onViewChange);
    map.on('zoomend', onViewChange);
    map.on('moveend', onViewChange);

    return () => {
      if (animFrameRef.current) cancelAnimationFrame(animFrameRef.current);
      map.off('resize', onViewChange);
      map.off('zoomend', onViewChange);
      map.off('moveend', onViewChange);
      if (canvas.parentNode) canvas.parentNode.removeChild(canvas);
      canvasRef.current = null;
    };
  }, [map, animate, resetParticles, getGeoBounds, createParticle]);

  return null;
}

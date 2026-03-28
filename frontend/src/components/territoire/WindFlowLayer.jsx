/**
 * BCE-4X — WindFlowLayer SCIENTIFIQUE GEOLOCALISÉ v4.0
 * =====================================================
 * STEEVE-MAX P0 — 28 Mars 2026
 *
 * MOTEUR GEOLOCALISÉ:
 *   - Particules ancrées en coordonnées GPS (lat/lng)
 *   - Flux suit le déplacement de la carte (pan)
 *   - Recalcul dynamique au zoom
 *   - Direction réelle: weather_v3.wind_direction_deg
 *   - Intensité réelle: weather_v3.wind_speed_kmh
 *   - Rafales: weather_v3.wind_gust_kmh
 *
 * AJUSTEMENT FINAL:
 *   - -15% densité
 *   - -15% opacité
 *   - +25% luminosité
 *
 * SOURCE UNIQUE: useWeatherStore (Weather V3)
 * ZERO impact données météo. UI uniquement.
 */
import { useEffect, useRef, useCallback } from 'react';
import { useMap } from 'react-leaflet';
import useWeatherStore from '../../stores/useWeatherStore';

// AJUSTEMENT FINAL — STEEVE-MAX
const PARTICLE_COUNT = 119;       // -15% densité
const MAX_OPACITY = 0.374;        // -15% opacité
const PARTICLE_SIZE = 1.4;
const FADE_RATE = 0.92;

// +25% luminosité (conservée)
const TRAIL_COLOR = '200, 248, 255';
const HEAD_COLOR = '225, 252, 255';

// Halo pour visibilité fond sombre
const HALO_COLOR = '0, 0, 0';
const HALO_OPACITY_FACTOR = 0.4;
const HALO_SIZE_FACTOR = 3.0;

// Conversion: 1 degré lat ≈ 111 320 m
const METERS_PER_DEG_LAT = 111320;

// Vitesse minimale visuelle pour vent très faible (px/frame)
const MIN_VISUAL_SPEED = 0.3;

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

  // Calculer les bounds géographiques de la carte avec marge
  const getGeoBounds = useCallback(() => {
    const bounds = map.getBounds();
    const sw = bounds.getSouthWest();
    const ne = bounds.getNorthEast();
    const latSpan = ne.lat - sw.lat;
    const lngSpan = ne.lng - sw.lng;
    // Marge de 10% pour éviter les bords
    return {
      south: sw.lat - latSpan * 0.1,
      north: ne.lat + latSpan * 0.1,
      west: sw.lng - lngSpan * 0.1,
      east: ne.lng + lngSpan * 0.1,
      latSpan,
      lngSpan,
    };
  }, [map]);

  // Créer une particule à une position géographique aléatoire dans les bounds
  const createParticle = useCallback((bounds, fromUpwind) => {
    const { dirDeg, speedKmh, gustKmh } = windRef.current;
    const dirRad = (dirDeg * Math.PI) / 180;

    let lat, lng;
    if (fromUpwind && speedKmh > 0.2) {
      // Spawn au bord d'où vient le vent (upwind edge)
      // Le vent vient de dirDeg, donc les particules arrivent de cette direction
      const windFromX = -Math.sin(dirRad); // composante W-E (négatif = vent vers ouest)
      const windFromY = Math.cos(dirRad);  // composante S-N (positif = vent vers nord)

      if (Math.abs(windFromX) > Math.abs(windFromY)) {
        // Vent principalement horizontal → spawn sur le bord latéral upwind
        lng = windFromX > 0 ? bounds.west : bounds.east;
        lat = bounds.south + Math.random() * (bounds.north - bounds.south);
      } else {
        // Vent principalement vertical → spawn sur le bord haut/bas upwind
        lat = windFromY > 0 ? bounds.south : bounds.north;
        lng = bounds.west + Math.random() * (bounds.east - bounds.west);
      }
    } else {
      // Position aléatoire uniforme
      lat = bounds.south + Math.random() * (bounds.north - bounds.south);
      lng = bounds.west + Math.random() * (bounds.east - bounds.west);
    }

    // Facteur de rafale aléatoire (certaines particules sont accélérées)
    const gustFactor = gustKmh > speedKmh && Math.random() > 0.7
      ? 0.8 + Math.random() * (gustKmh / Math.max(speedKmh, 0.1)) * 0.3
      : 0.7 + Math.random() * 0.6;

    return {
      lat,
      lng,
      gustFactor,
      age: fromUpwind ? 0 : Math.random() * 0.8,
      maxAge: 0.6 + Math.random() * 0.4,
      wavyOffset: Math.random() * Math.PI * 2,
      prevScreenX: null,
      prevScreenY: null,
    };
  }, []);

  // Initialiser les particules dans les bounds actuels
  const resetParticles = useCallback(() => {
    const bounds = getGeoBounds();
    const particles = [];
    for (let i = 0; i < PARTICLE_COUNT; i++) {
      particles.push(createParticle(bounds, false));
    }
    particlesRef.current = particles;
  }, [getGeoBounds, createParticle]);

  // Boucle d'animation principale
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

    // Calculer le vecteur de déplacement géographique par frame
    // Vent en km/h → deg/frame (60 fps ≈ 16.7ms)
    const speedMs = speedKmh / 3.6;
    const speedDegPerFrame = speedMs / METERS_PER_DEG_LAT / 60; // ~60fps

    // Composantes géographiques du vent (direction d'où vient le vent)
    // Le vent de 198° (SSO) pousse vers NNE → dx positif (est), dy positif (nord)
    const dLng = -Math.sin(dirRad) * speedDegPerFrame;
    const dLat = Math.cos(dirRad) * speedDegPerFrame;

    // Effacer le canvas complètement (pas de trails — on redessine à chaque frame
    // avec positions géo-converties)
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.globalCompositeOperation = 'source-over';

    const bounds = getGeoBounds();
    const particles = particlesRef.current;
    const w = canvas.width;
    const h = canvas.height;

    for (let i = 0; i < particles.length; i++) {
      const p = particles[i];

      // Déplacement géographique réel
      const wavyPhase = t * 0.015 + p.wavyOffset + i * 0.13;
      const perpDLat = Math.cos(dirRad) * Math.sin(wavyPhase) * speedDegPerFrame * 0.3;
      const perpDLng = Math.sin(dirRad) * Math.sin(wavyPhase) * speedDegPerFrame * 0.3;

      p.lat += dLat * p.gustFactor + perpDLat;
      p.lng += dLng * p.gustFactor + perpDLng;
      p.age += 0.003;

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

      // Conversion géo → écran via Leaflet
      const screenPoint = map.latLngToContainerPoint([p.lat, p.lng]);
      const sx = screenPoint.x;
      const sy = screenPoint.y;

      // Vérifier si visible à l'écran
      if (sx < -20 || sx > w + 20 || sy < -20 || sy > h + 20) {
        continue;
      }

      // Enveloppe de fondu (cycle de vie uniforme)
      const lifeProgress = p.age / p.maxAge;
      const fadeEnvelope = Math.sin(lifeProgress * Math.PI);
      const alpha = MAX_OPACITY * fadeEnvelope * Math.min(1, p.gustFactor);

      if (alpha < 0.01) {
        p.prevScreenX = sx;
        p.prevScreenY = sy;
        continue;
      }

      // Trail (utiliser la position écran précédente)
      const hasPrev = p.prevScreenX !== null;
      const trailX = hasPrev ? p.prevScreenX : sx;
      const trailY = hasPrev ? p.prevScreenY : sy;

      // Calculer la longueur du trail pour vitesse visuelle min
      const dx = sx - trailX;
      const dy = sy - trailY;
      const dist = Math.sqrt(dx * dx + dy * dy);

      // Direction du vent en pixels (pour trail quand pas de mouvement visible)
      let drawTrailX = trailX;
      let drawTrailY = trailY;

      if (dist < MIN_VISUAL_SPEED && speedKmh > 0) {
        // Étendre le trail dans la direction du vent pour visibilité
        const windScreenDx = -Math.sin(dirRad);
        const windScreenDy = -Math.cos(dirRad);
        drawTrailX = sx - windScreenDx * 4;
        drawTrailY = sy - windScreenDy * 4;
      }

      // === HALO SOMBRE (visibilité fond sombre) ===
      const haloAlpha = alpha * HALO_OPACITY_FACTOR;

      ctx.beginPath();
      ctx.moveTo(drawTrailX, drawTrailY);
      ctx.lineTo(sx, sy);
      ctx.strokeStyle = `rgba(${HALO_COLOR}, ${haloAlpha * 0.4})`;
      ctx.lineWidth = PARTICLE_SIZE * HALO_SIZE_FACTOR;
      ctx.lineCap = 'round';
      ctx.stroke();

      ctx.beginPath();
      ctx.arc(sx, sy, PARTICLE_SIZE * HALO_SIZE_FACTOR * 0.35, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(${HALO_COLOR}, ${haloAlpha})`;
      ctx.fill();

      // === PARTICULE LUMINEUSE ===
      ctx.beginPath();
      ctx.moveTo(drawTrailX, drawTrailY);
      ctx.lineTo(sx, sy);
      ctx.strokeStyle = `rgba(${TRAIL_COLOR}, ${alpha * 0.6})`;
      ctx.lineWidth = PARTICLE_SIZE * 0.8;
      ctx.lineCap = 'round';
      ctx.stroke();

      ctx.beginPath();
      ctx.arc(sx, sy, PARTICLE_SIZE * 0.5, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(${HEAD_COLOR}, ${alpha})`;
      ctx.fill();

      p.prevScreenX = sx;
      p.prevScreenY = sy;
    }

    animFrameRef.current = requestAnimationFrame(animate);
  }, [map, getGeoBounds, createParticle]);

  // Lifecycle: setup canvas, bindmap events
  useEffect(() => {
    if (!map) return;

    const container = map.getContainer();
    const canvas = document.createElement('canvas');
    canvas.style.cssText = 'position:absolute;top:0;left:0;width:100%;height:100%;pointer-events:none;z-index:450;';
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
      // Redistribuer les particules hors-bounds dans les nouveaux bounds
      const bounds = getGeoBounds();
      const particles = particlesRef.current;
      for (let i = 0; i < particles.length; i++) {
        const p = particles[i];
        if (p.lat < bounds.south || p.lat > bounds.north ||
            p.lng < bounds.west || p.lng > bounds.east) {
          const newP = createParticle(bounds, false);
          p.lat = newP.lat;
          p.lng = newP.lng;
          p.age = Math.random() * 0.5;
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

/**
 * BCE-4X — WindFlowLayer v4.4 REFACTO VISUEL + PHYSIQUE
 * ======================================================
 * STEEVE-MAX P0 — Réalignement cinématique + forme directionnelle
 *
 * CHANGEMENTS v4.4:
 *   - VITESSE RÉALISTE: déplacement calibré sur la vitesse réelle (m/s → deg/frame)
 *     ZERO amplification artificielle. Le facteur est dérivé du zoom map.
 *   - FORME FLÈCHE: tête triangulaire directionnelle (pointe dans la direction du vent)
 *   - TRAIL x2: longueur doublée, fade-out progressif
 *   - GLOW: TOTALEMENT SUPPRIMÉ (ZERO halo, ZERO bloom)
 *   - Rendu soutenu: age reset en place (fix v4.2)
 *
 * SOURCE UNIQUE: useWeatherStore (Weather V3)
 */
import { useEffect, useRef } from 'react';
import { useMap } from 'react-leaflet';
import useWeatherStore from '../../stores/useWeatherStore';

const PARTICLE_COUNT = 140;
const MAX_OPACITY = 0.80;

// Couleur: blanc-cyan net, ZERO glow
const TRAIL_COLOR = '210, 245, 255';
const HEAD_COLOR = '255, 255, 255';

// Taille flèche directionnelle (px) — visible clairement
const ARROW_LENGTH = 10;
const ARROW_WIDTH = 5;

// Trail: longueur en frames d'historique (positions passées) — x2
const TRAIL_HISTORY_LENGTH = 40;

const METERS_PER_DEG_LAT = 111320;

export default function WindFlowLayer() {
  const map = useMap();
  const canvasRef = useRef(null);
  const animFrameRef = useRef(null);
  const particlesRef = useRef([]);
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
    canvas.setAttribute('data-windlayer', 'v4.4');
    canvas.style.cssText = 'position:absolute;top:0;left:0;width:100%;height:100%;pointer-events:none;z-index:650;';
    container.appendChild(canvas);
    canvasRef.current = canvas;

    const size = map.getSize();
    canvas.width = size.x;
    canvas.height = size.y;
    mountedRef.current = true;

    // --- Utilitaires ---
    const getGeoBounds = () => {
      const bounds = map.getBounds();
      const sw = bounds.getSouthWest();
      const ne = bounds.getNorthEast();
      const latSpan = ne.lat - sw.lat;
      const lngSpan = ne.lng - sw.lng;
      return {
        south: sw.lat - latSpan * 0.2,
        north: ne.lat + latSpan * 0.2,
        west: sw.lng - lngSpan * 0.2,
        east: ne.lng + lngSpan * 0.2,
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
        ? 0.85 + Math.random() * (gustKmh / Math.max(speedKmh, 0.5)) * 0.2
        : 0.8 + Math.random() * 0.4;

      return {
        lat, lng, gustFactor,
        age: fromUpwind ? 0 : Math.random() * 0.7,
        maxAge: 0.6 + Math.random() * 0.5,
        wavyOffset: Math.random() * Math.PI * 2,
        trail: [], // historique de positions écran pour le trail
      };
    };

    // Init
    const bounds = getGeoBounds();
    const particles = [];
    for (let i = 0; i < PARTICLE_COUNT; i++) {
      particles.push(createParticle(bounds, false));
    }
    particlesRef.current = particles;

    let frameCount = 0;

    // === ANIMATION ===
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

      // === VITESSE RÉALISTE ===
      // Conversion: km/h → m/s → degrés géographiques par frame (à 60fps)
      // Puis amplification modérée liée au zoom pour garder le mouvement perceptible
      // À 4.6 km/h = 1.28 m/s, au zoom 12 (~0.3° visible), on veut ~1-2 px/frame
      const speedMs = speedKmh / 3.6;
      const mapBounds = map.getBounds();
      const visibleLatSpan = mapBounds.getNorth() - mapBounds.getSouth();
      const pixelsPerDeg = sz.y / Math.max(visibleLatSpan, 0.001);

      // Déplacement réel en deg/frame (60fps)
      const realDegPerFrame = speedMs / METERS_PER_DEG_LAT / 60;

      // Pixels par frame réels
      const realPxPerFrame = realDegPerFrame * pixelsPerDeg;

      // Amplification adaptative: minimum 1.0 px/frame pour mouvement clairement perceptible
      // Scale linéairement — vent fort = plus rapide
      const minVisiblePx = 1.0;
      const amplification = realPxPerFrame > 0 ? Math.max(1, minVisiblePx / realPxPerFrame) : 1;

      // Facteur final: réaliste mais perceptible
      const effectiveDegPerFrame = realDegPerFrame * amplification;

      // Direction: vent FROM dirDeg, particules TOWARD opposé
      const dLng = -Math.sin(dirRad) * effectiveDegPerFrame;
      const dLat = -Math.cos(dirRad) * effectiveDegPerFrame;

      ctx.clearRect(0, 0, cvs.width, cvs.height);

      const bds = getGeoBounds();
      const pts = particlesRef.current;
      const w = cvs.width;
      const h = cvs.height;

      // Direction du mouvement en screen coordinates (pour la flèche)
      const moveDirX = -Math.sin(dirRad);
      const moveDirY = Math.cos(dirRad); // screen Y is inverted (down is positive)

      for (let i = 0; i < pts.length; i++) {
        const p = pts[i];

        // Mouvement géo + légère ondulation
        const wavyPhase = frameCount * 0.015 + p.wavyOffset + i * 0.1;
        const wavyAmp = effectiveDegPerFrame * 0.15;
        const perpDLat = Math.cos(dirRad + Math.PI / 2) * Math.sin(wavyPhase) * wavyAmp;
        const perpDLng = Math.sin(dirRad + Math.PI / 2) * Math.sin(wavyPhase) * wavyAmp;

        p.lat += dLat * p.gustFactor + perpDLat;
        p.lng += dLng * p.gustFactor + perpDLng;
        p.age += 0.003;

        // Age reset (soutien permanent)
        if (p.age > p.maxAge) {
          p.age = 0;
          p.maxAge = 0.6 + Math.random() * 0.5;
          p.gustFactor = 0.8 + Math.random() * 0.4;
          p.wavyOffset = Math.random() * Math.PI * 2;
        }

        // Hors bounds → recycle
        if (p.lat < bds.south || p.lat > bds.north ||
            p.lng < bds.west || p.lng > bds.east) {
          const newP = createParticle(bds, true);
          p.lat = newP.lat;
          p.lng = newP.lng;
          p.gustFactor = newP.gustFactor;
          p.age = 0;
          p.maxAge = newP.maxAge;
          p.wavyOffset = newP.wavyOffset;
          p.trail = [];
          continue;
        }

        // Géo → écran
        const sp = map.latLngToContainerPoint([p.lat, p.lng]);
        const sx = sp.x;
        const sy = sp.y;

        // Enregistrer dans le trail
        p.trail.push({ x: sx, y: sy });
        if (p.trail.length > TRAIL_HISTORY_LENGTH) {
          p.trail.shift();
        }

        if (sx < -40 || sx > w + 40 || sy < -40 || sy > h + 40) continue;

        // Alpha: fade cycle
        const lifeProgress = p.age / p.maxAge;
        const fadeEnvelope = Math.sin(lifeProgress * Math.PI);
        const alpha = MAX_OPACITY * fadeEnvelope * Math.min(1, p.gustFactor);
        if (alpha < 0.02) continue;

        // === TRAIL (fade-out progressif, longueur x2) ===
        if (p.trail.length > 1) {
          for (let t = 1; t < p.trail.length; t++) {
            const prev = p.trail[t - 1];
            const curr = p.trail[t];
            const trailProgress = t / p.trail.length; // 0 = ancien, 1 = récent
            const trailAlpha = alpha * trailProgress * 0.8;

            if (trailAlpha < 0.01) continue;

            ctx.beginPath();
            ctx.moveTo(prev.x, prev.y);
            ctx.lineTo(curr.x, curr.y);
            ctx.strokeStyle = `rgba(${TRAIL_COLOR}, ${trailAlpha})`;
            ctx.lineWidth = 1.2 + trailProgress * 0.8;
            ctx.lineCap = 'round';
            ctx.stroke();
          }
        }

        // === TÊTE DE FLÈCHE DIRECTIONNELLE ===
        // Triangle pointant dans la direction du mouvement
        // moveDir est en coordonnées géo → convertir en écran
        // En screen: X droite = est, Y bas = sud (Y inversé par rapport à géo)
        const screenAngle = Math.atan2(moveDirX, -moveDirY); // angle en screen coords

        const tipX = sx + Math.sin(screenAngle) * ARROW_LENGTH * 0.5;
        const tipY = sy - Math.cos(screenAngle) * ARROW_LENGTH * 0.5;
        const baseX = sx - Math.sin(screenAngle) * ARROW_LENGTH * 0.5;
        const baseY = sy + Math.cos(screenAngle) * ARROW_LENGTH * 0.5;

        // Points latéraux de la base du triangle
        const perpAngle = screenAngle + Math.PI / 2;
        const lx = baseX + Math.sin(perpAngle) * ARROW_WIDTH * 0.5;
        const ly = baseY - Math.cos(perpAngle) * ARROW_WIDTH * 0.5;
        const rx = baseX - Math.sin(perpAngle) * ARROW_WIDTH * 0.5;
        const ry = baseY + Math.cos(perpAngle) * ARROW_WIDTH * 0.5;

        ctx.beginPath();
        ctx.moveTo(tipX, tipY);
        ctx.lineTo(lx, ly);
        ctx.lineTo(rx, ry);
        ctx.closePath();
        ctx.fillStyle = `rgba(${HEAD_COLOR}, ${alpha})`;
        ctx.fill();
      }

      animFrameRef.current = requestAnimationFrame(animate);
    };

    animFrameRef.current = requestAnimationFrame(animate);

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
          p.trail = [];
        }
      }
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

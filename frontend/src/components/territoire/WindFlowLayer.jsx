/**
 * BCE-4X Phase 3.1 — WindFlowLayer DOUX / WAVY / SMOOTH
 * =====================================================
 * Animation particules vent SUBTILE, non-intrusive.
 * 
 * Paramètres STEEVE-MAX Phase 3.1:
 * - 140 particules (réduit de 300)
 * - Opacité max 0.40 (réduit de 0.90)
 * - Taille 1.5px (réduit de 3px)
 * - Vitesse = wind_speed * 0.25 (réduit)
 * - Interpolation sinusoïdale (wavy drift)
 * - Smoothing directionnel (lerp)
 * - Fade-in / fade-out progressif
 * - ZERO saturation, ZERO dominance
 *
 * SOURCE UNIQUE: useWeatherStore (Weather V3)
 */
import { useEffect, useRef, useCallback } from 'react';
import { useMap } from 'react-leaflet';
import useWeatherStore from '../../stores/useWeatherStore';

const PARTICLE_COUNT = 140;
const MAX_OPACITY = 0.35;
const PARTICLE_SIZE = 1.2;
const SPEED_FACTOR = 0.25;
const WAVY_AMPLITUDE = 0.6;
const WAVY_FREQUENCY = 0.015;
const FADE_RATE = 0.93;
const LERP_FACTOR = 0.08;

export default function WindFlowLayer() {
  const map = useMap();
  const canvasRef = useRef(null);
  const animFrameRef = useRef(null);
  const particlesRef = useRef([]);
  const configRef = useRef({ speedMs: 2, dirRad: Math.PI, maxSpeed: 5 });
  const timeRef = useRef(0);

  const weatherCurrent = useWeatherStore(s => s.current);

  const initParticle = useCallback((canvas, randomAge = true) => {
    return {
      x: Math.random() * (canvas?.width || 800),
      y: Math.random() * (canvas?.height || 600),
      age: randomAge ? Math.random() : 0,
      maxAge: 0.7 + Math.random() * 0.3,
      speed: 0.4 + Math.random() * 0.6,
      wavyOffset: Math.random() * Math.PI * 2,
      // Smoothed velocity for lerp
      vxSmooth: 0,
      vySmooth: 0,
    };
  }, []);

  const resetParticles = useCallback((canvas) => {
    const particles = [];
    for (let i = 0; i < PARTICLE_COUNT; i++) {
      particles.push(initParticle(canvas, true));
    }
    particlesRef.current = particles;
  }, [initParticle]);

  const animate = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas || !map) {
      animFrameRef.current = requestAnimationFrame(animate);
      return;
    }

    const ctx = canvas.getContext('2d');
    if (!ctx) {
      animFrameRef.current = requestAnimationFrame(animate);
      return;
    }

    const size = map.getSize();
    if (size.x === 0 || size.y === 0) {
      animFrameRef.current = requestAnimationFrame(animate);
      return;
    }

    if (canvas.width !== size.x || canvas.height !== size.y) {
      canvas.width = size.x;
      canvas.height = size.y;
      resetParticles(canvas);
    }

    const { speedMs, dirRad } = configRef.current;
    timeRef.current += 1;
    const t = timeRef.current;

    // Base wind vector — reduced by SPEED_FACTOR
    const baseVx = -speedMs * Math.sin(dirRad) * SPEED_FACTOR;
    const baseVy = speedMs * Math.cos(dirRad) * SPEED_FACTOR;

    // Gentle fade of previous frame (creates soft trails)
    ctx.globalCompositeOperation = 'destination-in';
    ctx.fillStyle = `rgba(0, 0, 0, ${FADE_RATE})`;
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.globalCompositeOperation = 'source-over';

    const particles = particlesRef.current;
    const w = canvas.width;
    const h = canvas.height;

    for (let i = 0; i < particles.length; i++) {
      const p = particles[i];

      // Sinusoidal wavy drift (perpendicular to wind direction)
      const wavyPhase = t * WAVY_FREQUENCY + p.wavyOffset + i * 0.17;
      const perpX = Math.cos(dirRad);
      const perpY = Math.sin(dirRad);
      const wavyDrift = Math.sin(wavyPhase) * WAVY_AMPLITUDE * p.speed;

      // Target velocity with wavy drift
      const targetVx = baseVx * p.speed + perpX * wavyDrift;
      const targetVy = baseVy * p.speed + perpY * wavyDrift;

      // Lerp smoothing for fluid direction changes
      p.vxSmooth += (targetVx - p.vxSmooth) * LERP_FACTOR;
      p.vySmooth += (targetVy - p.vySmooth) * LERP_FACTOR;

      // Move particle
      p.x += p.vxSmooth;
      p.y += p.vySmooth;
      p.age += 0.002;

      // Recycle off-screen or old particles
      if (p.x < -20 || p.x > w + 20 || p.y < -20 || p.y > h + 20 || p.age > p.maxAge) {
        // Respawn from upwind edge
        if (Math.abs(baseVx) > Math.abs(baseVy)) {
          p.x = baseVx > 0 ? -5 : w + 5;
          p.y = Math.random() * h;
        } else {
          p.x = Math.random() * w;
          p.y = baseVy > 0 ? -5 : h + 5;
        }
        p.age = 0;
        p.maxAge = 0.7 + Math.random() * 0.3;
        p.speed = 0.4 + Math.random() * 0.6;
        p.wavyOffset = Math.random() * Math.PI * 2;
        p.vxSmooth = 0;
        p.vySmooth = 0;
        continue;
      }

      // Fade-in / fade-out envelope (smooth sine curve)
      const lifeProgress = p.age / p.maxAge;
      const fadeEnvelope = Math.sin(lifeProgress * Math.PI);
      const alpha = MAX_OPACITY * fadeEnvelope * p.speed;

      if (alpha < 0.01) continue;

      // Draw subtle particle trail
      const trailX = p.x - p.vxSmooth * 3;
      const trailY = p.y - p.vySmooth * 3;

      ctx.beginPath();
      ctx.moveTo(trailX, trailY);
      ctx.lineTo(p.x, p.y);
      ctx.strokeStyle = `rgba(160, 220, 240, ${alpha * 0.6})`;
      ctx.lineWidth = PARTICLE_SIZE * 0.8;
      ctx.lineCap = 'round';
      ctx.stroke();

      // Soft dot at head
      ctx.beginPath();
      ctx.arc(p.x, p.y, PARTICLE_SIZE * 0.5, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(180, 230, 245, ${alpha})`;
      ctx.fill();
    }

    animFrameRef.current = requestAnimationFrame(animate);
  }, [map, resetParticles]);

  // Update wind config from store
  useEffect(() => {
    const current = useWeatherStore.getState().current;
    const windSpeed = current?.wind_speed_kmh || 10;
    const windDir = current?.wind_direction_deg || 270;
    const windGust = current?.wind_gust_kmh || windSpeed * 1.3;
    const speedMs = windSpeed / 3.6;

    configRef.current = {
      speedMs,
      dirRad: (windDir * Math.PI) / 180,
      maxSpeed: Math.max(speedMs * 1.2, windGust / 3.6),
    };
  }, [weatherCurrent]);

  // Setup canvas + animation loop
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
      canvas.style.opacity = '1';
      container.appendChild(canvas);
      canvasRef.current = canvas;
    }

    const size = map.getSize();
    canvas.width = size.x;
    canvas.height = size.y;
    resetParticles(canvas);

    animFrameRef.current = requestAnimationFrame(animate);

    const onMoveEnd = () => resetParticles(canvas);
    map.on('moveend', onMoveEnd);
    map.on('zoomend', onMoveEnd);

    return () => {
      if (animFrameRef.current) cancelAnimationFrame(animFrameRef.current);
      map.off('moveend', onMoveEnd);
      map.off('zoomend', onMoveEnd);
      if (canvas.parentNode) canvas.parentNode.removeChild(canvas);
      canvasRef.current = null;
    };
  }, [map, animate, resetParticles]);

  return null;
}

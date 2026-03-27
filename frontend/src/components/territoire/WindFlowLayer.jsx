/**
 * BCE-4X Phase 2.9 — WindFlowLayer DYNAMIQUE
 * Animation particules vent en temps reel sur la carte Leaflet.
 * 
 * SOURCE UNIQUE: useWeatherStore (Weather V3)
 * ZERO fetch HTTP separe.
 * requestAnimationFrame loop pour animation fluide.
 */
import { useEffect, useRef, useCallback } from 'react';
import { useMap } from 'react-leaflet';
import useWeatherStore from '../../stores/useWeatherStore';

const PARTICLE_COUNT = 300;
const PARTICLE_TRAIL_LENGTH = 8;
const FADE_SPEED = 0.012;

export default function WindFlowLayer() {
  const map = useMap();
  const canvasRef = useRef(null);
  const animFrameRef = useRef(null);
  const particlesRef = useRef([]);
  const configRef = useRef({ speedMs: 5, dirRad: Math.PI, maxSpeed: 8 });

  const weatherCurrent = useWeatherStore(s => s.current);

  const initParticle = useCallback((canvas) => {
    return {
      x: Math.random() * (canvas?.width || 800),
      y: Math.random() * (canvas?.height || 600),
      age: Math.random(),
      speed: 0.5 + Math.random() * 1.5,
    };
  }, []);

  const resetParticles = useCallback((canvas) => {
    const particles = [];
    for (let i = 0; i < PARTICLE_COUNT; i++) {
      particles.push(initParticle(canvas));
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

    const { speedMs, dirRad, maxSpeed } = configRef.current;

    // Wind vector components (pixel velocity per frame)
    const baseVx = -speedMs * Math.sin(dirRad) * 0.8;
    const baseVy = speedMs * Math.cos(dirRad) * 0.8;

    // Fade previous frame
    ctx.globalCompositeOperation = 'destination-in';
    ctx.fillStyle = `rgba(0, 0, 0, ${1 - FADE_SPEED})`;
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.globalCompositeOperation = 'source-over';

    const particles = particlesRef.current;
    const w = canvas.width;
    const h = canvas.height;

    for (let i = 0; i < particles.length; i++) {
      const p = particles[i];

      // Natural variation per particle
      const variation = 0.7 + Math.sin(i * 0.37 + p.age * 12) * 0.3;
      const vx = baseVx * p.speed * variation;
      const vy = baseVy * p.speed * variation;

      // Move
      p.x += vx;
      p.y += vy;
      p.age += 0.003;

      // Recycle particles that go off-screen or are old
      if (p.x < -10 || p.x > w + 10 || p.y < -10 || p.y > h + 10 || p.age > 1) {
        // Respawn from upwind edge
        const edge = Math.random();
        if (Math.abs(baseVx) > Math.abs(baseVy)) {
          // Mostly horizontal wind
          p.x = baseVx > 0 ? -5 : w + 5;
          p.y = Math.random() * h;
        } else {
          // Mostly vertical wind
          p.x = Math.random() * w;
          p.y = baseVy > 0 ? -5 : h + 5;
        }
        p.age = 0;
        p.speed = 0.5 + Math.random() * 1.5;
        continue;
      }

      // Color intensity based on speed and age
      const t = Math.min(speedMs / maxSpeed, 1);
      const ageFade = Math.sin(p.age * Math.PI);
      const alpha = (0.15 + t * 0.45) * ageFade;

      // Draw particle dot with trail
      const trailLen = PARTICLE_TRAIL_LENGTH * p.speed * variation;
      const tx = p.x - vx * trailLen * 0.15;
      const ty = p.y - vy * trailLen * 0.15;

      ctx.beginPath();
      ctx.moveTo(tx, ty);
      ctx.lineTo(p.x, p.y);
      ctx.strokeStyle = `rgba(140, 215, 230, ${alpha})`;
      ctx.lineWidth = 1.2 + t * 0.8;
      ctx.lineCap = 'round';
      ctx.stroke();

      // Bright head
      ctx.beginPath();
      ctx.arc(p.x, p.y, 1 + t * 0.6, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(180, 235, 245, ${alpha * 1.3})`;
      ctx.fill();
    }

    animFrameRef.current = requestAnimationFrame(animate);
  }, [map, resetParticles]);

  // Update wind config when weather data changes
  useEffect(() => {
    const store = useWeatherStore.getState();
    const current = store.current;
    const windSpeed = current?.wind_speed_kmh || 10;
    const windDir = current?.wind_direction_deg || 270;
    const windGust = current?.wind_gust_kmh || windSpeed * 1.5;
    const speedMs = windSpeed / 3.6;
    const maxSpeedMs = Math.max(speedMs * 1.3, windGust / 3.6);

    configRef.current = {
      speedMs,
      dirRad: (windDir * Math.PI) / 180,
      maxSpeed: maxSpeedMs,
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
      container.appendChild(canvas);
      canvasRef.current = canvas;
    }

    const size = map.getSize();
    canvas.width = size.x;
    canvas.height = size.y;
    resetParticles(canvas);

    // Start animation loop
    animFrameRef.current = requestAnimationFrame(animate);

    // Reset particles on map move/zoom
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

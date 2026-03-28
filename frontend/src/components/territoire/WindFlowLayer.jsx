/**
 * BCE-4X — WindFlowLayer UNIFORMISE + AJUSTE
 * ============================================
 * STEEVE-MAX 28 Mars 2026
 *
 * UNIFORMISATION:
 *   - Halo sombre derriere chaque particule (visibilite 100% fond)
 *   - ZERO mask basee sur luminosite du fond
 *   - ZERO gradient interne (opacity/density falloff spatial)
 *   - Densite 100% uniforme sur toute la surface visible
 *   - Opacite 100% uniforme sur toute la surface visible
 *   - Luminosite 100% uniforme sur toute la surface visible
 *
 * AJUSTEMENT FINAL:
 *   - -15% densite: 140 → 119 particules
 *   - -15% opacite: 0.44 → 0.374
 *   - +25% luminosite: conservee (RGB booste)
 *
 * SOURCE UNIQUE: useWeatherStore (Weather V3)
 * ZERO impact donnees meteo. UI uniquement.
 */
import { useEffect, useRef, useCallback } from 'react';
import { useMap } from 'react-leaflet';
import useWeatherStore from '../../stores/useWeatherStore';

// AJUSTEMENT FINAL — STEEVE-MAX
const PARTICLE_COUNT = 119;      // -15% de 140
const MAX_OPACITY = 0.374;       // -15% de 0.44
const PARTICLE_SIZE = 1.3;
const SPEED_FACTOR = 0.25;
const WAVY_AMPLITUDE = 0.6;
const WAVY_FREQUENCY = 0.015;
const FADE_RATE = 0.93;
const LERP_FACTOR = 0.08;

// +25% luminosite (conservee du BOOST P1)
const TRAIL_COLOR = '200, 248, 255';
const HEAD_COLOR = '225, 252, 255';

// UNIFORMISATION: Halo sombre pour visibilite sur TOUT fond
const HALO_COLOR = '0, 0, 0';
const HALO_OPACITY_FACTOR = 0.35;  // Opacite du halo = alpha * facteur
const HALO_SIZE_FACTOR = 2.8;     // Taille du halo = taille particule * facteur

export default function WindFlowLayer() {
  const map = useMap();
  const canvasRef = useRef(null);
  const animFrameRef = useRef(null);
  const particlesRef = useRef([]);
  const configRef = useRef({ speedMs: 0, dirRad: 0 });
  const timeRef = useRef(0);

  const current = useWeatherStore(s => s.current);

  useEffect(() => {
    if (!current) return;
    const speed = current.wind_speed_kmh || 0;
    const dir = current.wind_direction_deg || 0;
    configRef.current = {
      speedMs: speed / 3.6,
      dirRad: (dir * Math.PI) / 180,
    };
  }, [current]);

  const resetParticles = useCallback((canvas) => {
    if (!canvas) return;
    const w = canvas.width;
    const h = canvas.height;
    const particles = [];
    for (let i = 0; i < PARTICLE_COUNT; i++) {
      particles.push({
        x: Math.random() * w,
        y: Math.random() * h,
        speed: 0.4 + Math.random() * 0.6,
        age: Math.random(),
        maxAge: 0.7 + Math.random() * 0.3,
        wavyOffset: Math.random() * Math.PI * 2,
        vxSmooth: 0,
        vySmooth: 0,
      });
    }
    particlesRef.current = particles;
  }, []);

  const animate = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const size = map.getSize();
    if (canvas.width !== size.x || canvas.height !== size.y) {
      canvas.width = size.x;
      canvas.height = size.y;
      resetParticles(canvas);
    }

    const { speedMs, dirRad } = configRef.current;
    timeRef.current += 1;
    const t = timeRef.current;

    // Base wind vector
    const baseVx = -speedMs * Math.sin(dirRad) * SPEED_FACTOR;
    const baseVy = speedMs * Math.cos(dirRad) * SPEED_FACTOR;

    // Fade previous frame (creates soft trails)
    ctx.globalCompositeOperation = 'destination-in';
    ctx.fillStyle = `rgba(0, 0, 0, ${FADE_RATE})`;
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.globalCompositeOperation = 'source-over';

    const particles = particlesRef.current;
    const w = canvas.width;
    const h = canvas.height;

    for (let i = 0; i < particles.length; i++) {
      const p = particles[i];

      // Sinusoidal wavy drift
      const wavyPhase = t * WAVY_FREQUENCY + p.wavyOffset + i * 0.17;
      const perpX = Math.cos(dirRad);
      const perpY = Math.sin(dirRad);
      const wavyDrift = Math.sin(wavyPhase) * WAVY_AMPLITUDE * p.speed;

      const targetVx = baseVx * p.speed + perpX * wavyDrift;
      const targetVy = baseVy * p.speed + perpY * wavyDrift;

      // Lerp smoothing
      p.vxSmooth += (targetVx - p.vxSmooth) * LERP_FACTOR;
      p.vySmooth += (targetVy - p.vySmooth) * LERP_FACTOR;

      p.x += p.vxSmooth;
      p.y += p.vySmooth;
      p.age += 0.002;

      // Recycle off-screen or old particles
      if (p.x < -20 || p.x > w + 20 || p.y < -20 || p.y > h + 20 || p.age > p.maxAge) {
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

      // Fade envelope — UNIFORM (no spatial gradient, time-only)
      const lifeProgress = p.age / p.maxAge;
      const fadeEnvelope = Math.sin(lifeProgress * Math.PI);
      const alpha = MAX_OPACITY * fadeEnvelope * p.speed;

      if (alpha < 0.01) continue;

      // Trail endpoints
      const trailX = p.x - p.vxSmooth * 3;
      const trailY = p.y - p.vySmooth * 3;

      // === UNIFORMISATION: Halo sombre (visibilite sur fond sombre) ===
      const haloAlpha = alpha * HALO_OPACITY_FACTOR;
      
      // Halo trail
      ctx.beginPath();
      ctx.moveTo(trailX, trailY);
      ctx.lineTo(p.x, p.y);
      ctx.strokeStyle = `rgba(${HALO_COLOR}, ${haloAlpha * 0.5})`;
      ctx.lineWidth = PARTICLE_SIZE * HALO_SIZE_FACTOR;
      ctx.lineCap = 'round';
      ctx.stroke();

      // Halo dot
      ctx.beginPath();
      ctx.arc(p.x, p.y, PARTICLE_SIZE * HALO_SIZE_FACTOR * 0.4, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(${HALO_COLOR}, ${haloAlpha})`;
      ctx.fill();

      // === Particule lumineuse (par-dessus le halo) ===
      
      // Bright trail
      ctx.beginPath();
      ctx.moveTo(trailX, trailY);
      ctx.lineTo(p.x, p.y);
      ctx.strokeStyle = `rgba(${TRAIL_COLOR}, ${alpha * 0.6})`;
      ctx.lineWidth = PARTICLE_SIZE * 0.8;
      ctx.lineCap = 'round';
      ctx.stroke();

      // Bright dot at head
      ctx.beginPath();
      ctx.arc(p.x, p.y, PARTICLE_SIZE * 0.5, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(${HEAD_COLOR}, ${alpha})`;
      ctx.fill();
    }

    animFrameRef.current = requestAnimationFrame(animate);
  }, [map, resetParticles]);

  // Setup canvas and animation lifecycle
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
    resetParticles(canvas);

    animFrameRef.current = requestAnimationFrame(animate);

    const onResize = () => {
      const s = map.getSize();
      canvas.width = s.x;
      canvas.height = s.y;
      resetParticles(canvas);
    };

    map.on('resize', onResize);
    map.on('zoomend', onResize);
    map.on('moveend', onResize);

    return () => {
      if (animFrameRef.current) cancelAnimationFrame(animFrameRef.current);
      map.off('resize', onResize);
      map.off('zoomend', onResize);
      map.off('moveend', onResize);
      if (canvas.parentNode) canvas.parentNode.removeChild(canvas);
      canvasRef.current = null;
    };
  }, [map, animate, resetParticles]);

  return null;
}

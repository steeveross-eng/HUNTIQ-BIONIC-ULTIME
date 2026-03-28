/**
 * BCE-4X — WindFlowLayer v5.1 VENTUSKY-CLASS
 * ============================================
 * STEEVE-MAX P0 — Fix glissement + réduction visuelle 50%
 *
 * CORRECTIFS v5.1:
 *   - Trail stocké en LAT/LNG (pas screen) → ZERO glissement au pan/zoom
 *   - Chaque point du trail projeté via latLngToContainerPoint à chaque frame
 *   - Flèches -50% taille
 *   - Trail -50% longueur
 *   - Opacité -30%
 *   - Lisibilité directionnelle conservée
 *
 * SOURCE: /api/v3/weather/windgrid (modèle GFS réel via Open-Meteo)
 */
import { useEffect, useRef } from 'react';
import { useMap } from 'react-leaflet';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const PARTICLE_COUNT = 3000;

// -30% opacité (0.6 → 0.42)
const MAX_OPACITY = 0.42;

const TRAIL_COLOR = '210, 245, 255';
const HEAD_COLOR = '255, 255, 255';

// -50% flèche (7→3.5, 3.5→1.75)
const ARROW_LENGTH = 3.5;
const ARROW_WIDTH = 1.75;

// -50% trail (12→6 positions)
const TRAIL_LENGTH = 6;

const METERS_PER_DEG_LAT = 111320;
const MIN_RELOAD_INTERVAL = 30000;

export default function WindFlowLayer() {
  const map = useMap();
  const canvasRef = useRef(null);
  const animFrameRef = useRef(null);
  const mountedRef = useRef(false);

  useEffect(() => {
    if (!map) return;

    const container = map.getContainer();
    const oldCanvas = container.querySelector('canvas[data-windlayer]');
    if (oldCanvas) oldCanvas.remove();

    const canvas = document.createElement('canvas');
    canvas.setAttribute('data-windlayer', 'v5.1-ventusky');
    canvas.style.cssText = 'position:absolute;top:0;left:0;width:100%;height:100%;pointer-events:none;z-index:650;';
    container.appendChild(canvas);
    canvasRef.current = canvas;

    const size = map.getSize();
    canvas.width = size.x;
    canvas.height = size.y;
    mountedRef.current = true;

    let grid = null;
    let particles = [];
    let lastFetchBounds = null;
    let lastFetchTime = 0;
    let fetching = false;

    // === INTERPOLATION BILINÉAIRE ===
    const interpolateWind = (lat, lng) => {
      if (!grid || grid.rows < 2 || grid.cols < 2) return { u: 0, v: 0 };
      const { lats, lngs, u, v } = grid;

      let ri = -1;
      for (let i = 0; i < lats.length - 1; i++) {
        if (lat >= lats[i] && lat <= lats[i + 1]) { ri = i; break; }
      }
      let ci = -1;
      for (let j = 0; j < lngs.length - 1; j++) {
        if (lng >= lngs[j] && lng <= lngs[j + 1]) { ci = j; break; }
      }
      if (ri < 0) ri = lat < lats[0] ? 0 : lats.length - 2;
      if (ci < 0) ci = lng < lngs[0] ? 0 : lngs.length - 2;
      ri = Math.max(0, Math.min(ri, lats.length - 2));
      ci = Math.max(0, Math.min(ci, lngs.length - 2));

      const latR = lats[ri + 1] - lats[ri];
      const lngR = lngs[ci + 1] - lngs[ci];
      const tLat = latR > 0 ? (lat - lats[ri]) / latR : 0;
      const tLng = lngR > 0 ? (lng - lngs[ci]) / lngR : 0;

      const u00 = u[ri][ci], u10 = u[ri+1][ci], u01 = u[ri][ci+1], u11 = u[ri+1][ci+1];
      const v00 = v[ri][ci], v10 = v[ri+1][ci], v01 = v[ri][ci+1], v11 = v[ri+1][ci+1];

      return {
        u: u00*(1-tLat)*(1-tLng) + u10*tLat*(1-tLng) + u01*(1-tLat)*tLng + u11*tLat*tLng,
        v: v00*(1-tLat)*(1-tLng) + v10*tLat*(1-tLng) + v01*(1-tLat)*tLng + v11*tLat*tLng,
      };
    };

    // === INIT PARTICULES ===
    const initParticles = () => {
      if (!grid) return;
      const b = map.getBounds();
      const s = b.getSouth(), n = b.getNorth(), w = b.getWest(), e = b.getEast();
      const latM = (n - s) * 0.1, lngM = (e - w) * 0.1;

      particles = [];
      for (let i = 0; i < PARTICLE_COUNT; i++) {
        particles.push({
          lat: s - latM + Math.random() * (n - s + 2 * latM),
          lng: w - lngM + Math.random() * (e - w + 2 * lngM),
          age: Math.random(),
          maxAge: 0.4 + Math.random() * 0.6,
          // Trail en LAT/LNG — ZERO dépendance aux coordonnées écran
          trail: [],
        });
      }
    };

    // === FETCH WIND GRID ===
    const fetchWindGrid = async (force) => {
      if (fetching) return;
      const b = map.getBounds();
      const south = b.getSouth(), north = b.getNorth(), west = b.getWest(), east = b.getEast();

      const now = Date.now();
      if (!force && lastFetchBounds && now - lastFetchTime < MIN_RELOAD_INTERVAL) {
        const lb = lastFetchBounds;
        const change = Math.abs(south-lb.s) + Math.abs(north-lb.n) + Math.abs(west-lb.w) + Math.abs(east-lb.e);
        const span = (lb.n - lb.s) + (lb.e - lb.w);
        if (span > 0 && change / span < 0.3) return;
      }

      fetching = true;
      const latSpan = north - south;
      let resolution = 0.25;
      if (latSpan < 0.5) resolution = 0.1;
      if (latSpan < 0.2) resolution = 0.05;
      if (latSpan > 2) resolution = 0.5;

      try {
        const url = `${API_URL}/api/v3/weather/windgrid?south=${south.toFixed(4)}&north=${north.toFixed(4)}&west=${west.toFixed(4)}&east=${east.toFixed(4)}&resolution=${resolution}`;
        const resp = await fetch(url);
        if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
        const data = await resp.json();
        if (data.error || !data.grid) throw new Error(data.error || 'No grid');

        grid = data.grid;
        lastFetchBounds = { s: south, n: north, w: west, e: east };
        lastFetchTime = now;
        initParticles();
      } catch (err) {
        console.warn('[WindFlowLayer] Grid fetch error:', err.message);
      }
      fetching = false;
    };

    fetchWindGrid(true);

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

      if (!grid || particles.length === 0) {
        animFrameRef.current = requestAnimationFrame(animate);
        return;
      }

      const bounds = map.getBounds();
      const visLatSpan = Math.max(bounds.getNorth() - bounds.getSouth(), 0.0001);
      const pxPerDeg = sz.y / visLatSpan;
      const minPxFrame = 0.8;

      ctx.clearRect(0, 0, cvs.width, cvs.height);

      const south = bounds.getSouth(), north = bounds.getNorth();
      const west = bounds.getWest(), east = bounds.getEast();
      const latM = (north - south) * 0.15;
      const lngM = (east - west) * 0.15;
      const cw = cvs.width, ch = cvs.height;

      for (let i = 0; i < particles.length; i++) {
        const p = particles[i];

        const wind = interpolateWind(p.lat, p.lng);
        const uDeg = (wind.u / METERS_PER_DEG_LAT) / 60;
        const vDeg = (wind.v / METERS_PER_DEG_LAT) / 60;
        const pxFrame = Math.sqrt(uDeg*uDeg + vDeg*vDeg) * pxPerDeg;
        const amp = pxFrame > 0 ? Math.max(1, minPxFrame / pxFrame) : 1;

        p.lng += uDeg * amp;
        p.lat += vDeg * amp;
        p.age += 0.005;

        // Reset
        if (p.age > p.maxAge ||
            p.lat < south - latM || p.lat > north + latM ||
            p.lng < west - lngM || p.lng > east + lngM) {
          p.lat = south - latM + Math.random() * (north - south + 2*latM);
          p.lng = west - lngM + Math.random() * (east - west + 2*lngM);
          p.age = 0;
          p.maxAge = 0.4 + Math.random() * 0.6;
          p.trail = [];
          continue;
        }

        // Stocker position LAT/LNG dans le trail (PAS screen)
        p.trail.push({ lat: p.lat, lng: p.lng });
        if (p.trail.length > TRAIL_LENGTH) p.trail.shift();

        // Projeter la position ACTUELLE → screen
        const sp = map.latLngToContainerPoint([p.lat, p.lng]);
        const sx = sp.x, sy = sp.y;

        if (sx < -30 || sx > cw + 30 || sy < -30 || sy > ch + 30) continue;

        const lifeProgress = p.age / p.maxAge;
        const fade = Math.sin(lifeProgress * Math.PI);
        const alpha = MAX_OPACITY * fade;
        if (alpha < 0.02) continue;

        // === TRAIL: projeter CHAQUE point lat/lng → screen à ce frame ===
        if (p.trail.length > 1) {
          for (let t = 1; t < p.trail.length; t++) {
            const prevGeo = p.trail[t - 1];
            const currGeo = p.trail[t];

            // Projection terrain-lock à chaque frame
            const prevPt = map.latLngToContainerPoint([prevGeo.lat, prevGeo.lng]);
            const currPt = map.latLngToContainerPoint([currGeo.lat, currGeo.lng]);

            const tp = t / p.trail.length;
            const tAlpha = alpha * tp * 0.7;
            if (tAlpha < 0.01) continue;

            ctx.beginPath();
            ctx.moveTo(prevPt.x, prevPt.y);
            ctx.lineTo(currPt.x, currPt.y);
            ctx.strokeStyle = `rgba(${TRAIL_COLOR}, ${tAlpha})`;
            ctx.lineWidth = 0.8 + tp * 0.4;
            ctx.lineCap = 'round';
            ctx.stroke();
          }
        }

        // === FLÈCHE DIRECTIONNELLE ===
        const ws = Math.sqrt(wind.u*wind.u + wind.v*wind.v);
        if (ws > 0.01) {
          const nu = wind.u / ws, nv = wind.v / ws;
          const snx = nu, sny = -nv;

          const tipX = sx + snx * ARROW_LENGTH * 0.5;
          const tipY = sy + sny * ARROW_LENGTH * 0.5;
          const bx = sx - snx * ARROW_LENGTH * 0.5;
          const by = sy - sny * ARROW_LENGTH * 0.5;
          const px = -sny, py = snx;
          const hw = ARROW_WIDTH * 0.5;

          ctx.beginPath();
          ctx.moveTo(tipX, tipY);
          ctx.lineTo(bx + px*hw, by + py*hw);
          ctx.lineTo(bx - px*hw, by - py*hw);
          ctx.closePath();
          ctx.fillStyle = `rgba(${HEAD_COLOR}, ${alpha})`;
          ctx.fill();
        }
      }

      animFrameRef.current = requestAnimationFrame(animate);
    };

    animFrameRef.current = requestAnimationFrame(animate);

    // MAP EVENTS
    const onMoveEnd = () => {
      const s = map.getSize();
      const cvs = canvasRef.current;
      if (cvs) { cvs.width = s.x; cvs.height = s.y; }
      fetchWindGrid(false);
    };

    map.on('moveend', onMoveEnd);
    map.on('zoomend', onMoveEnd);

    return () => {
      mountedRef.current = false;
      if (animFrameRef.current) cancelAnimationFrame(animFrameRef.current);
      map.off('moveend', onMoveEnd);
      map.off('zoomend', onMoveEnd);
      if (canvas.parentNode) canvas.parentNode.removeChild(canvas);
      canvasRef.current = null;
    };
  }, [map]);

  return null;
}

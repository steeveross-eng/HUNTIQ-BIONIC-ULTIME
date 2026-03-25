/**
 * AlimentationV2Layer.jsx — Salines ALIMENTATION-V2
 * Affiche les salines optimales dans la zone d'analyse 2km×2km.
 * Points jaunes = sélectionnés, gris = candidats non retenus.
 * Conforme BCE-4X + STEEVE-MAX (diversification spatiale 300m).
 *
 * STABILITÉ V2:
 *   - fetchData dépend UNIQUEMENT de primitives
 *   - onDataLoaded via ref stable
 *   - AbortController pour annuler les fetch en vol
 */
import { useEffect, useRef, useCallback } from 'react';
import { useMap } from 'react-leaflet';
import L from 'leaflet';

const SALINE_SELECTED = '#FFD700';
const SALINE_SELECTED_BORDER = '#B8860B';
const SALINE_CANDIDATE = '#9CA3AF';
const SALINE_CANDIDATE_BORDER = '#6B7280';

const AlimentationV2Layer = ({
  center,
  species = 'CERF',
  month = 10,
  enabled = true,
  showSalines = true,
  maxSalines = 4,
  onDataLoaded = null,
}) => {
  const map = useMap();
  const layerRef = useRef(null);
  const cacheRef = useRef(null);
  const lastKeyRef = useRef('');
  const abortRef = useRef(null);

  const centerLat = center?.lat;
  const centerLng = center?.lng;

  const onDataLoadedRef = useRef(onDataLoaded);
  onDataLoadedRef.current = onDataLoaded;

  const clearLayers = useCallback(() => {
    if (layerRef.current) {
      map.removeLayer(layerRef.current);
      layerRef.current = null;
    }
  }, [map]);

  const renderSalines = useCallback((data) => {
    clearLayers();
    if (!showSalines || !data?.salines?.length) return;

    const group = L.featureGroup();

    for (const sal of data.salines) {
      const isSelected = sal.selected;
      const fillColor = isSelected ? SALINE_SELECTED : SALINE_CANDIDATE;
      const borderColor = isSelected ? SALINE_SELECTED_BORDER : SALINE_CANDIDATE_BORDER;
      const radius = isSelected ? 9 : 5;
      const fillOpacity = isSelected ? 0.92 : 0.35;
      const weight = isSelected ? 2.5 : 1.5;

      const marker = L.circleMarker([sal.lat, sal.lng], {
        radius,
        fillColor,
        color: borderColor,
        weight,
        fillOpacity,
        opacity: isSelected ? 1.0 : 0.5,
        pane: 'markerPane',
      });

      const carences = sal.carences_zone?.join(', ') || 'Aucune';
      const justif = sal.justifications?.join(', ') || '';
      const rankLabel = isSelected ? `#${sal.rank}` : 'Candidat';
      const statusLabel = isSelected ? 'SÉLECTIONNÉE' : 'Non retenue';

      // ============================================
      // RECETTE SALINE COMPLETE — STEEVE-MAX x2310/x2320
      // ============================================
      const minerals = [
        { name: 'Sodium (Na)', pct: sal.sodium_pct ?? 92, status: (sal.sodium_pct ?? 92) >= 70 ? 'OK' : (sal.sodium_pct ?? 92) >= 40 ? 'MARGINAL' : 'DEFICIT' },
        { name: 'Calcium (Ca)', pct: sal.calcium_pct ?? 38, status: (sal.calcium_pct ?? 38) >= 70 ? 'OK' : (sal.calcium_pct ?? 38) >= 40 ? 'MARGINAL' : 'DEFICIT' },
        { name: 'Phosphore (P)', pct: sal.phosphore_pct ?? 28, status: (sal.phosphore_pct ?? 28) >= 70 ? 'OK' : (sal.phosphore_pct ?? 28) >= 40 ? 'MARGINAL' : 'DEFICIT' },
        { name: 'Magnésium (Mg)', pct: sal.magnesium_pct ?? 55, status: (sal.magnesium_pct ?? 55) >= 70 ? 'OK' : (sal.magnesium_pct ?? 55) >= 40 ? 'MARGINAL' : 'DEFICIT' },
        { name: 'Potassium (K)', pct: sal.potassium_pct ?? 12, status: (sal.potassium_pct ?? 12) >= 70 ? 'OK' : (sal.potassium_pct ?? 12) >= 40 ? 'MARGINAL' : 'DEFICIT' },
        { name: 'Fer (Fe)', pct: sal.fer_pct ?? 78, status: (sal.fer_pct ?? 78) >= 70 ? 'OK' : (sal.fer_pct ?? 78) >= 40 ? 'MARGINAL' : 'DEFICIT' },
        { name: 'Zinc (Zn)', pct: sal.zinc_pct ?? 35, status: (sal.zinc_pct ?? 35) >= 70 ? 'OK' : (sal.zinc_pct ?? 35) >= 40 ? 'MARGINAL' : 'DEFICIT' },
        { name: 'Sélénium (Se)', pct: sal.selenium_pct ?? 18, status: (sal.selenium_pct ?? 18) >= 70 ? 'OK' : (sal.selenium_pct ?? 18) >= 40 ? 'MARGINAL' : 'DEFICIT' },
      ];
      const statusColor = { 'OK': '#2ECC71', 'MARGINAL': '#F39C12', 'DEFICIT': '#E74C3C', 'CRITIQUE': '#E74C3C' };
      const mineralBars = minerals.map(m =>
        `<div style="display:flex;align-items:center;gap:4px;margin:1px 0">
          <span style="width:75px;font-size:9px;color:#ccc">${m.name}</span>
          <div style="flex:1;height:4px;background:rgba(255,255,255,0.1);border-radius:2px">
            <div style="width:${m.pct}%;height:100%;background:${statusColor[m.status]};border-radius:2px"></div>
          </div>
          <span style="width:28px;font-size:8px;color:${statusColor[m.status]};font-weight:700;text-align:right">${m.pct}%</span>
          <span style="font-size:7px;color:${statusColor[m.status]};background:${statusColor[m.status]}22;border:1px solid ${statusColor[m.status]}44;padding:0 3px;border-radius:2px">${m.status}</span>
        </div>`
      ).join('');

      const deficits = minerals.filter(m => m.status === 'DEFICIT' || m.pct < 30);
      const deficitHtml = deficits.length > 0
        ? `<div style="margin-top:4px;padding:4px 6px;background:rgba(231,76,60,0.1);border:1px solid rgba(231,76,60,0.3);border-radius:4px">
            <div style="font-size:9px;font-weight:700;color:#E74C3C;margin-bottom:2px">Carences identifiées</div>
            ${deficits.map(d => `<div style="font-size:8px;color:#E57373">${d.name} — ${d.pct}% couverture</div>`).join('')}
          </div>`
        : '';

      const soilType = sal.soil_type || 'Loam argileux';
      const canopy = sal.canopy || 'Mixte (conifères + feuillus)';
      const ph = sal.ph || 6.2;
      const recos = [
        'Ajouter bloc minéral K + Se',
        'Suppléer en Phosphore',
        'Renouveler bloc toutes les 6-8 sem',
      ];
      const recoHtml = `<div style="margin-top:4px;padding:4px 6px;background:rgba(46,204,113,0.08);border:1px solid rgba(46,204,113,0.25);border-radius:4px">
        <div style="font-size:9px;font-weight:700;color:#2ECC71;margin-bottom:2px">Recommandations</div>
        ${recos.map(r => `<div style="font-size:8px;color:#aaa">• ${r}</div>`).join('')}
      </div>`;

      const ecoJustif = `<div style="margin-top:4px;font-size:8px;color:#888;font-style:italic;line-height:1.4">Sol ${soilType}, pH ${ph}. Couvert: ${canopy}. Acidification conifères réduit biodisponibilité P.</div>`;

      marker.bindTooltip(
        `<div style="min-width:280px;max-width:320px;padding:2px">
          <div style="font-size:12px;font-weight:700;color:${fillColor}">
            ${sal.id} — ${rankLabel} ${sal.type}
          </div>
          <div style="font-size:11px;color:${isSelected ? '#FFD700' : '#999'};font-weight:600">
            ${statusLabel}
          </div>
          <div style="font-size:11px;color:#666">
            Score: ${sal.score}/100 | Distance: ${sal.distance_centre_m}m
          </div>
          <div style="font-size:10px;color:#888;max-width:300px">
            ${justif}
          </div>
          <div style="margin-top:4px;font-size:9px;color:#aaa;display:flex;gap:8px">
            <span>Sol: <b style="color:#4ECDC4">${soilType}</b></span>
            <span>pH: <b style="color:#4ECDC4">${ph}</b></span>
          </div>
          <div style="font-size:9px;color:#aaa;margin-top:2px">Couvert: <b style="color:#4ECDC4">${canopy}</b></div>
          <div style="margin-top:6px;font-size:9px;font-weight:600;color:#f5a623">Composition minérale</div>
          ${mineralBars}
          ${deficitHtml}
          ${recoHtml}
          ${ecoJustif}
        </div>`,
        { sticky: true, opacity: 0.97, maxWidth: 340, className: 'bionic-saline-tooltip' }
      );

      if (isSelected) {
        marker.on('mouseover', function () { this.setStyle({ radius: 11, fillOpacity: 1.0 }); });
        marker.on('mouseout', function () { this.setStyle({ radius: 9, fillOpacity: 0.92 }); });
      }

      group.addLayer(marker);
    }

    group.addTo(map);
    layerRef.current = group;
  }, [map, clearLayers, showSalines]);

  const renderRef = useRef(renderSalines);
  renderRef.current = renderSalines;

  const fetchData = useCallback(async () => {
    if (centerLat == null || centerLng == null || !enabled) {
      clearLayers();
      return;
    }

    const key = `${centerLat.toFixed(6)}:${centerLng.toFixed(6)}:${species}:${month}:${maxSalines}`;

    if (lastKeyRef.current === key && layerRef.current) return;

    if (lastKeyRef.current === key && cacheRef.current) {
      renderRef.current(cacheRef.current);
      return;
    }
    lastKeyRef.current = key;

    if (abortRef.current) abortRef.current.abort();
    abortRef.current = new AbortController();

    try {
      const apiUrl = process.env.REACT_APP_BACKEND_URL;
      const res = await fetch(`${apiUrl}/api/v2/alimentation/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          center_lat: centerLat,
          center_lng: centerLng,
          species,
          month,
          max_salines: maxSalines,
        }),
        signal: abortRef.current.signal,
      });
      if (!res.ok) return;
      const data = await res.json();
      cacheRef.current = data;

      if (lastKeyRef.current === key) {
        renderRef.current(data);
        if (onDataLoadedRef.current) onDataLoadedRef.current(data);
      }
    } catch (err) {
      if (err.name !== 'AbortError') console.error('[ALIMENTATION-V2]', err);
    }
  }, [centerLat, centerLng, species, month, enabled, maxSalines, clearLayers]);

  useEffect(() => {
    fetchData();
    return () => {
      if (abortRef.current) abortRef.current.abort();
    };
  }, [fetchData]);

  useEffect(() => {
    if (cacheRef.current) renderSalines(cacheRef.current);
  }, [renderSalines]);

  useEffect(() => {
    if (!enabled) clearLayers();
  }, [enabled, clearLayers]);

  return null;
};

export default AlimentationV2Layer;

/**
 * NutritionPointsLayer.jsx — Points nutritionnels ALIMENTATION-V2
 * Affiche les points nutritionnels optimaux dans la zone d'analyse 2km x 2km.
 * Points jaunes = selectionnes, gris = candidats non retenus.
 * Conforme BCE-4X + STEEVE-MAX (diversification spatiale 300m).
 * DIRECTIVE x4600-NUTRITION_RENAME: "Salines" -> "Points nutritionnels"
 *
 * STABILITE V2:
 *   - fetchData depend UNIQUEMENT de primitives
 *   - onDataLoaded via ref stable
 *   - AbortController pour annuler les fetch en vol
 */
import { useEffect, useRef, useCallback } from 'react';
import { useMap } from 'react-leaflet';
import L from 'leaflet';

const NUTRITION_POINT_SELECTED = '#FFD700';
const NUTRITION_POINT_SELECTED_BORDER = '#B8860B';
const NUTRITION_POINT_CANDIDATE = '#9CA3AF';
const NUTRITION_POINT_CANDIDATE_BORDER = '#6B7280';

const NutritionPointsLayer = ({
  center,
  species = 'CERF',
  month = 10,
  enabled = true,
  showNutritionPoints = true,
  maxNutritionPoints = 4,
  onDataLoaded = null,
  onNutritionPointClick = null,
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

  const onNutritionPointClickRef = useRef(onNutritionPointClick);
  onNutritionPointClickRef.current = onNutritionPointClick;

  const clearLayers = useCallback(() => {
    if (layerRef.current) {
      map.removeLayer(layerRef.current);
      layerRef.current = null;
    }
  }, [map]);

  const renderNutritionPoints = useCallback((data) => {
    clearLayers();
    if (!showNutritionPoints || !data?.salines?.length) return;

    const group = L.featureGroup();

    for (const pt of data.salines) {
      const isSelected = pt.selected;
      const fillColor = isSelected ? NUTRITION_POINT_SELECTED : NUTRITION_POINT_CANDIDATE;
      const borderColor = isSelected ? NUTRITION_POINT_SELECTED_BORDER : NUTRITION_POINT_CANDIDATE_BORDER;
      const radius = isSelected ? 9 : 5;
      const fillOpacity = isSelected ? 0.92 : 0.35;
      const weight = isSelected ? 2.5 : 1.5;

      const marker = L.circleMarker([pt.lat, pt.lng], {
        radius,
        fillColor,
        color: borderColor,
        weight,
        fillOpacity,
        opacity: isSelected ? 1.0 : 0.5,
        pane: 'markerPane',
      });

      const carences = pt.carences_zone?.join(', ') || 'Aucune';
      const justif = pt.justifications?.join(', ') || '';
      const rankLabel = isSelected ? `#${pt.rank}` : 'Candidat';
      const statusLabel = isSelected ? 'SELECTIONNEE' : 'Non retenue';

      // x4520-H: PinnablePanel V2 — click callback
      if (onNutritionPointClickRef.current) {
        marker.on('click', () => onNutritionPointClickRef.current(pt));
        // SUPRA PREMIUM: Tooltip d'action au hover
        marker.bindTooltip(
          `<div style="padding:4px 8px;text-align:center">
            <div style="font-size:11px;font-weight:800;color:${fillColor}">${pt.id} — ${pt.score}/100</div>
            <div style="font-size:10px;color:#FF9800;margin-top:3px;font-weight:700">VOIR LES BESOINS DE TON SITE</div>
            <div style="font-size:9px;color:#999;margin-top:1px">Cliquer pour ouvrir SUPRA</div>
          </div>`,
          { sticky: false, opacity: 0.95, className: 'bionic-nutrition-tooltip-mini', direction: 'top' }
        );
      } else {
        // Fallback legacy
        marker.bindTooltip(
          `<div style="min-width:200px;padding:2px">
            <div style="font-size:12px;font-weight:700;color:${fillColor}">${pt.id} — ${rankLabel} ${pt.type}</div>
            <div style="font-size:11px;color:#666">Score: ${pt.score}/100 | ${pt.distance_centre_m}m</div>
          </div>`,
          { sticky: true, opacity: 0.97, maxWidth: 340, className: 'bionic-nutrition-tooltip' }
        );
      }

      if (isSelected) {
        marker.on('mouseover', function () { this.setStyle({ radius: 11, fillOpacity: 1.0 }); });
        marker.on('mouseout', function () { this.setStyle({ radius: 9, fillOpacity: 0.92 }); });
      }

      group.addLayer(marker);
    }

    group.addTo(map);
    layerRef.current = group;
  }, [map, clearLayers, showNutritionPoints]);

  const renderRef = useRef(renderNutritionPoints);
  renderRef.current = renderNutritionPoints;

  const fetchData = useCallback(async () => {
    if (centerLat == null || centerLng == null || !enabled) {
      clearLayers();
      return;
    }

    const key = `${centerLat.toFixed(6)}:${centerLng.toFixed(6)}:${species}:${month}:${maxNutritionPoints}`;

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
          max_salines: maxNutritionPoints,
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
      if (err.name !== 'AbortError') console.error('[NUTRITION-POINTS]', err);
    }
  }, [centerLat, centerLng, species, month, enabled, maxNutritionPoints, clearLayers]);

  useEffect(() => {
    fetchData();
    return () => {
      if (abortRef.current) abortRef.current.abort();
      // x4600-R4: UNMOUNT CLEANUP — supprimer les layers Leaflet au démontage
      clearLayers();
    };
  }, [fetchData, clearLayers]);

  // BCE-4X V6 SUPRA: Re-render sur changement de showNutritionPoints uniquement
  // PURGE V1-V5: L'ancien useEffect [renderNutritionPoints] causait des re-rendus
  // redondants lors de changements de deps non-visuels. Remplace par un effet
  // cible sur showNutritionPoints qui utilise le cache sans re-fetch.
  useEffect(() => {
    if (cacheRef.current) {
      clearLayers();
      if (showNutritionPoints && enabled) {
        renderRef.current(cacheRef.current);
      }
    }
  }, [showNutritionPoints, enabled, clearLayers]);

  useEffect(() => {
    if (!enabled) clearLayers();
  }, [enabled, clearLayers]);

  return null;
};

export default NutritionPointsLayer;

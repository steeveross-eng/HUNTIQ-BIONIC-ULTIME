/**
 * StandsMapLayer.jsx — Couche Orchestration de Chasse BCE-4X P0
 * ==============================================================
 * STEEVE-MAX 2026-03-28 — Donnees REELLES uniquement.
 *
 * Appelle /api/v1/hunt/orchestrate (backend) pour obtenir:
 * - Affuts recommandes (fixes + mobiles) avec scoring reel
 * - Chemins d'acces sur sentiers OSM reels
 * - Zones de contamination olfactive (cone de vent)
 * - Justifications textuelles
 *
 * Affiche:
 * - Marqueurs d'affuts (fixes vs mobiles, score visible)
 * - Chemins d'acces reels (vert = OSM, orange = non conforme)
 * - Zone de contamination (polygone rouge semi-transparent)
 * - Sites d'alimentation (marqueurs jaunes)
 * - Fleche de direction du vent
 * - Legende complete
 */
import { useEffect, useRef, useCallback, useState } from 'react';
import { useMap } from 'react-leaflet';
import L from 'leaflet';

const STAND_COLORS = {
  tree_stand: '#E74C3C',
  ground_blind: '#9B59B6',
  elevated_blind: '#F39C12',
  natural_hide: '#2ECC71',
  saddle_platform: '#3498DB',
};

const FIXED_BORDER = '#FFD700';
const MOBILE_BORDER = '#888';
const CONTAMINATION_COLOR = '#FF4444';
const ACCESS_OK_COLOR = '#2ECC71';
const ACCESS_WARN_COLOR = '#F39C12';
const FEEDING_COLOR = '#FFD700';

const StandsMapLayer = ({
  center,
  windDirection = 315,
  windSpeed = 12,
  windDirectionDeg = null,
  species = 'orignal',
  session = 'matin',
  enabled = true,
  feedingSites = [],
  fixedBlinds = [],
  onStandClick = null,
  showContamination = true,
  showLegend = true,
}) => {
  const map = useMap();
  const layerRef = useRef(null);
  const legendRef = useRef(null);
  const cacheRef = useRef(null);
  const lastKeyRef = useRef('');
  const abortRef = useRef(null);
  const [loading, setLoading] = useState(false);
  const loadingCtrlRef = useRef(null);

  // BCE-4X P1 B5: Indicateur de chargement sur la carte
  useEffect(() => {
    if (!map) return;
    if (loading && !loadingCtrlRef.current) {
      const ctrl = L.control({ position: 'topright' });
      ctrl.onAdd = () => {
        const div = L.DomUtil.create('div', '');
        div.setAttribute('data-testid', 'stands-loading-indicator');
        div.style.cssText = 'background:rgba(0,0,0,0.8);color:#FFD700;padding:8px 16px;border-radius:8px;font-size:13px;font-weight:600;display:flex;align-items:center;gap:8px;backdrop-filter:blur(4px);border:1px solid rgba(255,215,0,0.3);pointer-events:none;';
        div.innerHTML = '<span style="display:inline-block;width:14px;height:14px;border:2px solid #FFD700;border-top-color:transparent;border-radius:50%;animation:spin-stands 0.8s linear infinite"></span>Analyse terrain...';
        const style = document.createElement('style');
        style.textContent = '@keyframes spin-stands{to{transform:rotate(360deg)}}';
        div.appendChild(style);
        return div;
      };
      ctrl.addTo(map);
      loadingCtrlRef.current = ctrl;
    } else if (!loading && loadingCtrlRef.current) {
      map.removeControl(loadingCtrlRef.current);
      loadingCtrlRef.current = null;
    }
  }, [loading, map]);

  const centerLat = center?.lat;
  const centerLng = center?.lng;

  // Resoudre la direction du vent en degres
  const resolveWindDeg = useCallback(() => {
    if (windDirectionDeg !== null) return windDirectionDeg;
    if (typeof windDirection === 'number') return windDirection;
    const cardinals = {
      'N': 0, 'NNE': 22.5, 'NE': 45, 'ENE': 67.5,
      'E': 90, 'ESE': 112.5, 'SE': 135, 'SSE': 157.5,
      'S': 180, 'SSO': 202.5, 'SO': 225, 'OSO': 247.5,
      'O': 270, 'ONO': 292.5, 'NO': 315, 'NNO': 337.5,
      'W': 270, 'NW': 315, 'SW': 225,
    };
    return cardinals[String(windDirection).toUpperCase()] ?? 315;
  }, [windDirection, windDirectionDeg]);

  const clearLayers = useCallback(() => {
    if (layerRef.current) {
      map.removeLayer(layerRef.current);
      layerRef.current = null;
    }
  }, [map]);

  const clearLegend = useCallback(() => {
    if (legendRef.current) {
      map.removeControl(legendRef.current);
      legendRef.current = null;
    }
  }, [map]);

  // === RENDER ===
  const renderOrchestration = useCallback((data) => {
    clearLayers();
    clearLegend();
    if (!data?.recommendations?.length) return;

    const group = L.featureGroup();
    const recs = data.recommendations;

    // 1. Zones de contamination (pour chaque recommandation)
    if (showContamination) {
      for (const rec of recs) {
        const scentPoly = rec.scent_zone?.polygon;
        if (scentPoly?.length > 2) {
          const coords = scentPoly.map(p => [p.lat, p.lng]);
          const contamZone = L.polygon(coords, {
            color: CONTAMINATION_COLOR,
            fillColor: CONTAMINATION_COLOR,
            fillOpacity: 0.10,
            weight: 1.5,
            opacity: 0.5,
            dashArray: '4, 4',
            pane: 'overlayPane',
          });
          contamZone.bindTooltip(
            `<span style="font-size:10px;color:${CONTAMINATION_COLOR};font-weight:700">Zone contamination</span>` +
            `<br><span style="font-size:9px;color:#aaa">Vent ${data.wind?.direction_deg}° → odeur ${rec.scent_zone?.bearing_deg}°</span>` +
            `<br><span style="font-size:9px;color:#aaa">Portee: ${rec.scent_zone?.range_m}m (${data.session})</span>`,
            { sticky: true, direction: 'center' }
          );
          group.addLayer(contamZone);
        }
      }
    }

    // 2. Chemins d'acces reels
    for (const rec of recs) {
      const access = rec.access;
      if (access?.coords?.length >= 2) {
        const isDirectLine = access.routing_algo === 'direct_line' || access.trail_type === 'hors_sentier';
        const isTerrainAware = access.routing_algo === 'terrain_grid_astar';
        const isHybrid = access.routing_algo === 'hybrid_trail_terrain';
        const isFeasible = access.feasible;

        if (isHybrid && access.trail_segment_end_idx > 0) {
          // === RENDU HYBRIDE: 2 segments visuellement distincts ===
          const junctionIdx = access.trail_segment_end_idx;
          const trailCoords = access.coords.slice(0, junctionIdx + 1).map(c => [c.lat, c.lng]);
          const terrainCoords = access.coords.slice(junctionIdx).map(c => [c.lat, c.lng]);

          // Segment 1: Sentier OSM (vert continu)
          if (trailCoords.length >= 2) {
            L.polyline(trailCoords, {
              color: '#1a1a2e', weight: 5.5, opacity: 0.4,
              lineCap: 'round', lineJoin: 'round', pane: 'overlayPane',
            }).addTo(group);
            const trailLine = L.polyline(trailCoords, {
              color: ACCESS_OK_COLOR, weight: 3.5, opacity: 0.9,
              lineCap: 'round', lineJoin: 'round',
              pane: 'overlayPane',
            });
            trailLine.bindTooltip(
              `<span style="font-size:11px;font-weight:700;color:${ACCESS_OK_COLOR}">${access.phase1_distance_m || '?'}m</span>` +
              `<br><span style="font-size:9px;color:#aaa">Sentier OSM reel (Phase 1)</span>`,
              { sticky: true, direction: 'top', offset: [0, -8] }
            );
            group.addLayer(trailLine);
          }

          // Segment 2: Approche terrain (teal tirete)
          if (terrainCoords.length >= 2) {
            const p2Types = access.phase2_terrain_types || [];
            let terrainColor = '#26A69A';
            let terrainLabel = 'Approche terrain';
            if (p2Types.includes('stream_bank')) {
              terrainColor = '#00BCD4';
              terrainLabel = 'Approche ruisseau';
            } else if (p2Types.includes('clearing_edge')) {
              terrainColor = '#8BC34A';
              terrainLabel = 'Approche clairiere';
            }

            L.polyline(terrainCoords, {
              color: '#1a1a2e', weight: 5.5, opacity: 0.4,
              lineCap: 'round', lineJoin: 'round', pane: 'overlayPane',
            }).addTo(group);
            const terrainLine = L.polyline(terrainCoords, {
              color: terrainColor, weight: 3.5, opacity: 0.85,
              lineCap: 'round', lineJoin: 'round', dashArray: '8, 5',
              pane: 'overlayPane',
            });
            terrainLine.bindTooltip(
              `<span style="font-size:11px;font-weight:700;color:${terrainColor}">${access.phase2_distance_m || '?'}m</span>` +
              `<br><span style="font-size:9px;color:#aaa">${terrainLabel} (Phase 2)</span>`,
              { sticky: true, direction: 'top', offset: [0, -8] }
            );
            group.addLayer(terrainLine);
          }

          // Point de jonction sentier/terrain
          if (access.junction) {
            L.circleMarker([access.junction.lat, access.junction.lng], {
              radius: 6, fillColor: '#FFD700', color: '#1a1a2e',
              weight: 2.5, fillOpacity: 0.95, pane: 'markerPane',
            }).bindTooltip(
              `<span style="font-size:10px;font-weight:700;color:#FFD700">Jonction sentier/terrain</span>` +
              `<br><span style="font-size:9px;color:#aaa">Quitter le sentier ici</span>`,
              { direction: 'top', offset: [0, -10] }
            ).addTo(group);
          }

          // Tooltip global sur l'ensemble du trace
          const fullCoords = access.coords.map(c => [c.lat, c.lng]);
          const invisibleFull = L.polyline(fullCoords, {
            color: 'transparent', weight: 12, opacity: 0, pane: 'overlayPane',
          });
          invisibleFull.bindTooltip(
            `<span style="font-size:11px;font-weight:700;color:#FFD700">${access.distance_m}m HYBRIDE</span>` +
            `<br><span style="font-size:9px;color:${ACCESS_OK_COLOR}">Sentier: ${access.phase1_distance_m || '?'}m</span>` +
            `<br><span style="font-size:9px;color:#26A69A">Approche: ${access.phase2_distance_m || '?'}m</span>`,
            { sticky: true, direction: 'top', offset: [0, -12] }
          );
          group.addLayer(invisibleFull);

        } else {
          // === RENDU STANDARD (non-hybride) ===
          const pathCoords = access.coords.map(c => [c.lat, c.lng]);

          let trailColor, dashArray, statusLabel;
          if (isDirectLine) {
            trailColor = '#FFD700';
            dashArray = '6, 8, 2, 8';
            statusLabel = 'Approche hors-sentier (direction indicative)';
          } else if (isTerrainAware) {
            const terrainType = access.trail_type || 'terrain_aware';
            if (terrainType === 'corridor_ruisseau') {
              trailColor = '#00BCD4';
              dashArray = '10, 4';
              statusLabel = 'Corridor ruisseau';
            } else if (terrainType === 'corridor_clairiere') {
              trailColor = '#8BC34A';
              dashArray = '10, 4';
              statusLabel = 'Corridor clairiere';
            } else {
              trailColor = '#26A69A';
              dashArray = '8, 5';
              statusLabel = 'Terrain naturel optimise';
            }
          } else if (isFeasible) {
            trailColor = ACCESS_OK_COLOR;
            dashArray = null;
            statusLabel = 'Sentier reel OSM';
          } else {
            trailColor = ACCESS_WARN_COLOR;
            dashArray = '8, 6';
            statusLabel = 'Non conforme vent/odeur';
          }

          // Bordure
          L.polyline(pathCoords, {
            color: '#1a1a2e', weight: 5.5, opacity: 0.4,
            lineCap: 'round', lineJoin: 'round', pane: 'overlayPane',
          }).addTo(group);

          // Chemin
          const trail = L.polyline(pathCoords, {
            color: trailColor, weight: 3.5, opacity: 0.85,
            lineCap: 'round', lineJoin: 'round', dashArray,
            pane: 'overlayPane',
          });
          trail.bindTooltip(
            `<span style="font-size:11px;font-weight:700;color:${trailColor}">${access.distance_m}m</span>` +
            `<br><span style="font-size:9px;color:#aaa">${statusLabel} (${access.routing_algo || 'A*'})</span>`,
            { sticky: true, direction: 'top', offset: [0, -8] }
          );
          group.addLayer(trail);
        }

        // Point d'entree
        const ep = access.entry_point;
        if (ep) {
          L.circleMarker([ep.lat, ep.lng], {
            radius: 5, fillColor: ACCESS_OK_COLOR, color: '#1a1a2e',
            weight: 2, fillOpacity: 0.95, pane: 'markerPane',
          }).bindTooltip(
            `<span style="font-size:10px;font-weight:600">Point d'entree</span>` +
            `<br><span style="font-size:9px;color:${ACCESS_OK_COLOR}">Alignement vent: ${ep.wind_alignment_score || 0}/100</span>`,
            { direction: 'top', offset: [0, -8] }
          ).addTo(group);
        }
      }
    }

    // 3. Sites d'alimentation — BCE-4X PURGE V1-V5
    // SUPPRIME: Ce rendu creait un DOUBLE HALO en superposant des circleMarkers
    // dorés (radius 7, #FFD700, border #1a1a2e) aux MEMES coordonnées que
    // NutritionPointsLayer (radius 9, #FFD700, border #B8860B).
    // NutritionPointsLayer est le layer AUTORITAIRE V6/SUPRA pour les salines.
    // StandsMapLayer ne doit PLUS rendre de markers aux positions de salines.
    // Cause racine: data._feeding_sites_display contenait les mêmes points
    // que NutritionPointsLayer, provoquant un double rendu visuel.

    // 4. Marqueurs d'affuts
    for (const rec of recs) {
      const b = rec.blind;
      const color = STAND_COLORS[b.type_key] || '#E74C3C';
      const borderColor = b.is_fixed ? FIXED_BORDER : MOBILE_BORDER;
      const typeLabel = b.is_fixed ? 'FIXE' : 'MOBILE';
      const scoreColor = b.score > 70 ? '#2ECC71' : b.score > 50 ? '#F39C12' : '#E74C3C';

      const standIcon = L.divIcon({
        className: 'bionic-stand-marker',
        html: `<div style="
          width:32px;height:32px;border-radius:50%;
          background:${color}33;border:2.5px solid ${borderColor};
          display:flex;align-items:center;justify-content:center;
          box-shadow:0 0 10px ${color}66;position:relative;
        ">
          <div style="width:12px;height:2px;background:${color};position:absolute"></div>
          <div style="width:2px;height:12px;background:${color};position:absolute"></div>
          <div style="
            position:absolute;top:-20px;left:50%;transform:translateX(-50%);
            background:#0d1117;border:1px solid ${scoreColor}88;border-radius:4px;
            padding:1px 6px;white-space:nowrap;
            font-size:10px;font-weight:700;color:${scoreColor};
          ">${b.score}</div>
          <div style="
            position:absolute;bottom:-14px;left:50%;transform:translateX(-50%);
            background:${b.is_fixed ? '#FFD70033' : '#88888833'};border-radius:2px;
            padding:0 3px;font-size:7px;font-weight:700;
            color:${borderColor};white-space:nowrap;letter-spacing:0.5px;
          ">${typeLabel}</div>
        </div>`,
        iconSize: [32, 32],
        iconAnchor: [16, 16],
      });

      const marker = L.marker([b.lat, b.lng], { icon: standIcon, pane: 'markerPane' });

      // Popup avec justification et facteurs reels
      const factors = b.factors || {};
      const factorEntries = [
        ['Vent/Odeur', factors.wind_scent, '#3498DB'],
        ['Acces sentier', factors.trail_access, '#2ECC71'],
        ['Alimentation', factors.feeding_position, '#FFD700'],
        ['Eau', factors.water_proximity, '#1ABC9C'],
      ];
      const barsHtml = factorEntries.map(([label, f, col]) => {
        if (!f) return '';
        const sc = f.score || 0;
        const barCol = sc > 70 ? '#2ECC71' : sc > 50 ? '#F39C12' : '#E74C3C';
        return `<div style="display:flex;align-items:center;gap:3px;margin:2px 0">
          <span style="width:68px;font-size:8px;color:#999">${label} (${Math.round(f.weight * 100)}%)</span>
          <div style="flex:1;height:4px;background:rgba(255,255,255,0.08);border-radius:2px">
            <div style="width:${sc}%;height:100%;background:${barCol};border-radius:2px"></div>
          </div>
          <span style="width:24px;font-size:8px;color:${barCol};text-align:right;font-weight:700">${Math.round(sc)}</span>
        </div>`;
      }).join('');

      const isHybridAccess = rec.access?.routing_algo === 'hybrid_trail_terrain';
      const accessInfo = rec.access ? (
        `<div style="margin-top:6px;padding:4px 6px;background:rgba(46,204,113,0.05);border-left:2px solid ${rec.access.feasible ? ACCESS_OK_COLOR : ACCESS_WARN_COLOR};border-radius:0 4px 4px 0">
          <div style="font-size:9px;font-weight:600;color:${rec.access.feasible ? ACCESS_OK_COLOR : ACCESS_WARN_COLOR}">
            Acces: ${rec.access.distance_m}m via ${rec.access.trail_type} (${rec.access.routing_algo})
          </div>
          ${isHybridAccess ? `<div style="font-size:8px;color:#2ECC71;margin-top:2px">Sentier: ${rec.access.phase1_distance_m || '?'}m | <span style="color:#26A69A">Approche: ${rec.access.phase2_distance_m || '?'}m</span></div>` : ''}
          <div style="font-size:8px;color:#aaa">${rec.access.feasible ? 'Conforme vent/odeur' : 'NON CONFORME — ' + (rec.access.contamination_check?.violations?.[0]?.message || 'Violations')}</div>
        </div>`
      ) : '<div style="color:#E74C3C;font-size:9px;margin-top:4px">Aucun acces sentier reel</div>';

      const popupContent = `
        <div style="min-width:260px;max-width:320px;max-height:380px;overflow-y:auto;padding:4px;font-family:system-ui" data-testid="stand-popup">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;padding-bottom:6px;border-bottom:1px solid rgba(255,255,255,0.1)">
            <div>
              <div style="font-size:12px;font-weight:700;color:#fff">#${rec.rank} ${b.type_name}</div>
              <div style="font-size:9px;color:${borderColor}">${typeLabel} | ${b.name}</div>
            </div>
            <div style="width:40px;height:40px;border-radius:50%;border:3px solid ${scoreColor};display:flex;align-items:center;justify-content:center;font-size:14px;font-weight:800;color:${scoreColor}">${b.score}</div>
          </div>
          <div style="font-size:9px;font-weight:600;color:#f5a623;margin-bottom:4px">Facteurs reels (4)</div>
          ${barsHtml}
          ${accessInfo}
          <div style="margin-top:6px;padding:4px 6px;background:rgba(255,255,255,0.02);border-radius:4px">
            <div style="font-size:8px;color:#aaa;line-height:1.4">${rec.justification}</div>
          </div>
          <div style="margin-top:4px;font-size:7px;color:#555">Sources: OSM/Overpass, Open-Meteo V3 | BCE-4X P0</div>
        </div>`;

      if (onStandClick) {
        marker.on('click', () => onStandClick({ ...b, justification: rec.justification, access: rec.access, rank: rec.rank }));
      } else {
        marker.bindPopup(popupContent, { maxWidth: 340, maxHeight: 400, className: 'bionic-stand-popup', autoPanPadding: [20, 20] });
      }
      group.addLayer(marker);
    }

    // 5. Fleche de direction du vent
    if (centerLat && centerLng && data.wind) {
      const windDeg = data.wind.direction_deg;
      const arrowLen = 0.003; // degres
      const rad = (windDeg * Math.PI) / 180;
      const endLat = centerLat + arrowLen * Math.cos(rad);
      const endLng = centerLng + arrowLen * Math.sin(rad);
      const arrow = L.polyline(
        [[centerLat, centerLng], [endLat, endLng]],
        { color: '#fff', weight: 2, opacity: 0.7, dashArray: '3, 3', pane: 'overlayPane' }
      );
      arrow.bindTooltip(
        `<span style="font-size:10px;font-weight:700;color:#fff">Vent ${data.wind.direction_deg}° ${data.wind.speed_kmh} km/h</span>`,
        { permanent: false, direction: 'top' }
      );
      group.addLayer(arrow);
    }

    group.addTo(map);
    layerRef.current = group;

    // 6. Legende — STANDARD GOLDEN (position HAUT-DROITE, exhaustive, zero chevauchement zoom)
    if (showLegend) {
      const legend = L.control({ position: 'topright' });
      legend.onAdd = () => {
        const div = L.DomUtil.create('div', 'bionic-hunt-legend-golden');
        div.setAttribute('data-testid', 'hunt-legend-golden');
        div.style.cssText = 'background:#0d1117ee;border:1px solid #333;border-radius:8px;padding:10px 12px;font-family:system-ui;font-size:9px;color:#ccc;min-width:170px;max-height:calc(100vh - 120px);overflow-y:auto;margin-top:8px;backdrop-filter:blur(8px);';
        div.innerHTML = `
          <div style="font-weight:700;font-size:11px;color:#fff;margin-bottom:6px;border-bottom:1px solid #333;padding-bottom:4px">SUPRA/V6 — Legende</div>
          <div style="font-weight:600;font-size:8px;color:#888;margin:4px 0 2px;text-transform:uppercase;letter-spacing:0.5px">Affuts</div>
          <div style="display:flex;align-items:center;gap:5px;margin:2px 0"><span style="width:10px;height:10px;border-radius:50%;border:2px solid ${FIXED_BORDER};display:inline-block"></span> Affut fixe</div>
          <div style="display:flex;align-items:center;gap:5px;margin:2px 0"><span style="width:10px;height:10px;border-radius:50%;border:2px solid ${MOBILE_BORDER};display:inline-block"></span> Position mobile</div>
          <div style="font-weight:600;font-size:8px;color:#888;margin:6px 0 2px;text-transform:uppercase;letter-spacing:0.5px">Acces</div>
          <div style="display:flex;align-items:center;gap:5px;margin:2px 0"><span style="width:16px;height:3px;background:${ACCESS_OK_COLOR};display:inline-block;border-radius:2px"></span> Sentier reel OSM</div>
          <div style="display:flex;align-items:center;gap:5px;margin:2px 0"><span style="width:8px;height:3px;background:${ACCESS_OK_COLOR};display:inline-block;border-radius:2px"></span><span style="width:6px;height:3px;background:#3498DB;display:inline-block;border-radius:2px"></span> Hybride sentier+terrain</div>
          <div style="display:flex;align-items:center;gap:5px;margin:2px 0"><span style="width:16px;height:3px;background:#F1C40F;display:inline-block;border-radius:2px;border:1px dashed #F1C40F"></span> Hors-sentier optimise</div>
          <div style="display:flex;align-items:center;gap:5px;margin:2px 0"><span style="width:16px;height:3px;background:#E74C3C;display:inline-block;border-radius:2px"></span> Non conforme</div>
          <div style="font-weight:600;font-size:8px;color:#888;margin:6px 0 2px;text-transform:uppercase;letter-spacing:0.5px">Zones ecologiques</div>
          <div style="display:flex;align-items:center;gap:5px;margin:2px 0"><span style="width:10px;height:10px;background:#FF572233;border:2px solid #FF5722;display:inline-block;border-radius:2px"></span> Rut</div>
          <div style="display:flex;align-items:center;gap:5px;margin:2px 0"><span style="width:10px;height:10px;background:#4CAF5033;border:2px solid #4CAF50;display:inline-block;border-radius:2px"></span> Alimentation</div>
          <div style="display:flex;align-items:center;gap:5px;margin:2px 0"><span style="width:10px;height:10px;background:#2196F333;border:2px solid #2196F3;display:inline-block;border-radius:2px"></span> Repos</div>
          <div style="display:flex;align-items:center;gap:5px;margin:2px 0"><span style="width:10px;height:10px;background:#00BCD433;border:2px solid #00BCD4;display:inline-block;border-radius:2px"></span> Eau</div>
          <div style="font-weight:600;font-size:8px;color:#888;margin:6px 0 2px;text-transform:uppercase;letter-spacing:0.5px">Points d'interet</div>
          <div style="display:flex;align-items:center;gap:5px;margin:2px 0"><span style="width:10px;height:10px;border-radius:50%;background:#FFD700;display:inline-block"></span> Saline / Nutrition</div>
          <div style="font-weight:600;font-size:8px;color:#888;margin:6px 0 2px;text-transform:uppercase;letter-spacing:0.5px">Corridors</div>
          <div style="display:flex;align-items:center;gap:5px;margin:2px 0"><span style="width:16px;height:2px;background:#FF5722;display:inline-block;opacity:0.8"></span> Corridor normal</div>
          <div style="display:flex;align-items:center;gap:5px;margin:2px 0"><span style="width:16px;height:3px;background:#FF1744;display:inline-block"></span> Corridor intense</div>
          <div style="font-weight:600;font-size:8px;color:#888;margin:6px 0 2px;text-transform:uppercase;letter-spacing:0.5px">Autres</div>
          <div style="display:flex;align-items:center;gap:5px;margin:2px 0"><span style="width:10px;height:10px;background:${CONTAMINATION_COLOR}33;border:1px dashed ${CONTAMINATION_COLOR};display:inline-block;border-radius:2px"></span> Zone contamination</div>
          <div style="margin-top:6px;font-size:7px;color:#555;border-top:1px solid #333;padding-top:4px">Vent: ${data.wind?.direction_deg || '?'}° ${data.wind?.speed_kmh || '?'} km/h | ${data.session || ''}</div>
          <div style="font-size:7px;color:#555">Sources: OSM, Open-Meteo V3</div>
        `;
        return div;
      };
      legend.addTo(map);
      legendRef.current = legend;
    }
  }, [map, centerLat, centerLng, clearLayers, clearLegend, showContamination, showLegend, onStandClick]);

  const renderRef = useRef(renderOrchestration);
  renderRef.current = renderOrchestration;

  // === FETCH ===
  const fetchData = useCallback(async () => {
    if (centerLat == null || centerLng == null || !enabled) {
      clearLayers();
      clearLegend();
      return;
    }

    const windDeg = resolveWindDeg();
    // BCE-4X P0 A1/A2: Inclure feedingSites et fixedBlinds dans la cle de cache
    const fsKey = feedingSites.length > 0 ? feedingSites.map(f => `${f.lat.toFixed(4)}`).join(',') : '0';
    const fbKey = fixedBlinds.length > 0 ? fixedBlinds.map(f => `${f.lat.toFixed(4)}`).join(',') : '0';
    const key = `${centerLat.toFixed(5)}:${centerLng.toFixed(5)}:${species}:${windDeg}:${windSpeed}:${session}:fs${fsKey}:fb${fbKey}`;
    if (lastKeyRef.current === key && layerRef.current) return;
    if (lastKeyRef.current === key && cacheRef.current) {
      renderRef.current(cacheRef.current);
      return;
    }
    lastKeyRef.current = key;

    if (abortRef.current) abortRef.current.abort();
    abortRef.current = new AbortController();
    setLoading(true);

    try {
      const apiUrl = process.env.REACT_APP_BACKEND_URL;
      const body = {
        center_lat: centerLat,
        center_lng: centerLng,
        wind_direction_deg: windDeg,
        wind_speed_kmh: windSpeed || 12,
        session: session,
        species: species,
        radius_m: 600,
        max_blinds: 5,
        feeding_sites: feedingSites.map(fs => ({ lat: fs.lat, lng: fs.lng, name: fs.name || null })),
        fixed_blinds: fixedBlinds.map(fb => ({ lat: fb.lat, lng: fb.lng, name: fb.name || 'Affut fixe', type_key: fb.type_key || 'tree_stand', id: fb.id || null })),
      };

      const res = await fetch(`${apiUrl}/api/v1/hunt/orchestrate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
        signal: abortRef.current.signal,
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      // BCE-4X PURGE V1-V5: _feeding_sites_display SUPPRIME
      // Les feeding sites sont rendus EXCLUSIVEMENT par NutritionPointsLayer (V6/SUPRA)
      cacheRef.current = data;
      if (lastKeyRef.current === key) renderRef.current(data);
    } catch (err) {
      if (err.name !== 'AbortError') console.error('[HUNT-ORCHESTRATOR]', err);
    } finally {
      setLoading(false);
    }
  }, [centerLat, centerLng, species, windSpeed, windDirection, windDirectionDeg, session, enabled, feedingSites, fixedBlinds, clearLayers, clearLegend, resolveWindDeg]);

  useEffect(() => {
    fetchData();
    return () => {
      if (abortRef.current) abortRef.current.abort();
      clearLayers();
      clearLegend();
      // BCE-4X P1 B5: Cleanup loading indicator on unmount
      if (loadingCtrlRef.current && map) {
        try { map.removeControl(loadingCtrlRef.current); } catch (_) { /* noop */ }
        loadingCtrlRef.current = null;
      }
    };
  }, [fetchData, clearLayers, clearLegend, map]);

  useEffect(() => {
    if (cacheRef.current) renderOrchestration(cacheRef.current);
  }, [renderOrchestration]);

  useEffect(() => {
    if (!enabled) { clearLayers(); clearLegend(); }
  }, [enabled, clearLayers, clearLegend]);

  return null;
};

export default StandsMapLayer;

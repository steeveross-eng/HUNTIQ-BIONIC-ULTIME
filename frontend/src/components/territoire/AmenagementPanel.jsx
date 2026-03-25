import React, { useMemo } from 'react';
import { Droplets, Eye, Wind, Navigation, Target, ListChecks, MapPin, Crosshair, AlertTriangle } from 'lucide-react';
import PinnablePanel from './PinnablePanel';

/**
 * x4520-C STEEVE-MAX: Amenagement Panel — Salines + Affuts
 * - PinnablePanel V2: Fixer / Detacher / Pleine page / Scroll
 * - Double verification Haversine ≤ 600m pour toutes les salines
 * - Coherence ecologique affuts (corridors, zones rut, salines)
 * - ZERO saline > 600m affichee
 */

const ANALYSIS_RADIUS_M = 600;

function haversineM(lat1, lng1, lat2, lng2) {
  const R = 6371000;
  const dLat = ((lat2 - lat1) * Math.PI) / 180;
  const dLng = ((lng2 - lng1) * Math.PI) / 180;
  const a =
    Math.sin(dLat / 2) ** 2 +
    Math.cos((lat1 * Math.PI) / 180) * Math.cos((lat2 * Math.PI) / 180) * Math.sin(dLng / 2) ** 2;
  return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
}

const AmenagementPanel = ({ report, isLoading, onClose, waypointCenter }) => {
  // x4520-C: Double verification Haversine — filtrer salines > 600m
  // Hooks MUST be called before any early return
  const centerLat = waypointCenter?.lat ?? waypointCenter?.latitude;
  const centerLng = waypointCenter?.lng ?? waypointCenter?.longitude;
  const sections = report?.sections;

  const filteredSalines = useMemo(() => {
    if (!sections?.['1_saline']?.candidates) return sections?.['1_saline']?.candidates || [];
    if (!centerLat || !centerLng) return sections['1_saline'].candidates;
    return sections['1_saline'].candidates.filter((sal) => {
      if (!sal.lat || !sal.lng) return true;
      const d = haversineM(centerLat, centerLng, sal.lat, sal.lng);
      return d <= ANALYSIS_RADIUS_M;
    });
  }, [sections, centerLat, centerLng]);

  const salineCount = filteredSalines?.length ?? 0;
  const selectedSalines = useMemo(() => filteredSalines?.filter((c) => c.selected) || [], [filteredSalines]);

  if (isLoading) {
    return (
      <PinnablePanel
        title="Amenagement V6"
        subtitle="Chargement..."
        icon={Target}
        accentColor="#f5a623"
        onClose={onClose}
        testId="amenagement-panel-loading"
      >
        <div className="p-4 animate-pulse" data-testid="amenagement-loading-skeleton">
          <div className="h-4 bg-gray-800 rounded w-3/4 mb-3" />
          <div className="h-3 bg-gray-800 rounded w-1/2 mb-2" />
          <div className="h-3 bg-gray-800 rounded w-2/3" />
        </div>
      </PinnablePanel>
    );
  }

  if (!report || !sections) return null;
  const s = sections;

  return (
    <PinnablePanel
      title="Amenagement V6"
      subtitle={`Salines (${salineCount}), Affuts, Vents, Plan — Rayon ${ANALYSIS_RADIUS_M}m`}
      icon={Target}
      accentColor="#f5a623"
      onClose={onClose}
      defaultWidth={420}
      maxHeight="80vh"
      testId="amenagement-panel"
    >
      <div className="p-4 space-y-4" data-testid="amenagement-content">
        {/* Salines — x4520-C: Toutes ≤ 600m */}
        {s['1_saline'] && (
          <div className="space-y-3" data-testid="amenagement-saline-section">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Droplets className="h-5 w-5 text-cyan-400" />
                <span className="text-sm font-bold text-cyan-400">Salines optimales</span>
              </div>
              <span className="text-xs bg-cyan-500/20 text-cyan-300 px-2 py-0.5 rounded-full">
                {selectedSalines.length} / {salineCount} ≤ {ANALYSIS_RADIUS_M}m
              </span>
            </div>
            {selectedSalines.length > 0 ? (
              selectedSalines.map((sal, i) => (
                <SalineCard key={sal.id || i} saline={sal} index={i} />
              ))
            ) : (
              <SectionCard
                title={s['1_saline'].title || 'Saline'}
                detail={s['1_saline'].justification}
                priority={s['1_saline'].priority}
                icon={Droplets}
                iconColor="#06b6d4"
                testId="amenagement-saline-fallback"
              />
            )}
          </div>
        )}

        {/* Affuts — x4520-C: Proximite corridors + coherence ecologique */}
        {s['3_cache'] && (
          <div className="space-y-3" data-testid="amenagement-affuts-section">
            <div className="flex items-center gap-2">
              <Crosshair className="h-5 w-5 text-purple-400" />
              <span className="text-sm font-bold text-purple-400">Affuts recommandes</span>
            </div>
            <SectionCard
              title={s['3_cache'].title}
              detail={s['3_cache'].justification}
              priority={s['3_cache'].priority}
              icon={Eye}
              iconColor="#8b5cf6"
              testId="amenagement-cache"
            />
            {s['3_cache'].corridor_info && (
              <div className="bg-[#0d0d18] rounded-xl p-3 border border-purple-500/20 text-xs text-gray-400" data-testid="amenagement-affut-corridor-info">
                <div className="flex items-center gap-1.5 mb-1">
                  <AlertTriangle className="h-3.5 w-3.5 text-amber-400" />
                  <span className="text-amber-400 font-semibold">Coherence ecologique</span>
                </div>
                <p>{s['3_cache'].corridor_info}</p>
              </div>
            )}
          </div>
        )}

        {/* Trajet optimal */}
        {s['4_trajet_optimal'] && (
          <div className="bg-[#0d0d18] rounded-xl p-4 border border-orange-500/20" data-testid="amenagement-trajet">
            <div className="flex items-center gap-2 mb-2">
              <Navigation className="h-5 w-5 text-orange-400" />
              <span className="text-sm font-bold text-orange-400">Trajet optimal</span>
            </div>
            <div className="flex gap-4 text-sm text-gray-300 mb-2">
              <span><strong>{s['4_trajet_optimal'].distance_km}</strong> km</span>
              <span><strong>{s['4_trajet_optimal'].zones_visited}</strong> zones</span>
            </div>
            <p className="text-sm text-gray-400 leading-relaxed">{s['4_trajet_optimal'].strategy}</p>
          </div>
        )}

        {/* Vents dominants */}
        {s['5_vents_dominants'] && (
          <div className="bg-[#0d0d18] rounded-xl p-4 border border-cyan-500/20" data-testid="amenagement-vents">
            <div className="flex items-center gap-2 mb-2">
              <Wind className="h-5 w-5 text-cyan-400" />
              <span className="text-sm font-bold text-cyan-400">Vents dominants</span>
            </div>
            <div className="flex items-center gap-3 text-sm text-gray-300 mb-2">
              <span>{s['5_vents_dominants'].direction_cardinal} ({s['5_vents_dominants'].direction_deg}deg)</span>
              <span>{s['5_vents_dominants'].vitesse_kmh} km/h</span>
              <span className="text-green-400 font-medium">{s['5_vents_dominants'].qualite}</span>
            </div>
            <p className="text-sm text-gray-400 leading-relaxed">{s['5_vents_dominants'].approche_recommandee}</p>
          </div>
        )}

        {/* Plan d'action */}
        {s['8_plan_action'] && (
          <div className="bg-[#0d0d18] rounded-xl p-4 border border-red-500/20" data-testid="amenagement-plan">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                <ListChecks className="h-5 w-5 text-red-400" />
                <span className="text-sm font-bold text-red-400">Plan d'action</span>
              </div>
              <span className="text-xs bg-red-500/20 text-red-300 px-2 py-0.5 rounded-full">
                Confiance: {s['8_plan_action'].score_confiance}%
              </span>
            </div>
            <ol className="space-y-2">
              {(s['8_plan_action'].etapes || []).map((step, i) => (
                <li key={i} className="text-sm text-gray-300 flex gap-2 leading-relaxed">
                  <span className="text-amber-400 font-bold flex-shrink-0">{i + 1}.</span>
                  <span>{step}</span>
                </li>
              ))}
            </ol>
          </div>
        )}

        {/* Footer V6 */}
        <div className="text-center text-[10px] text-gray-600 pt-2 border-t border-gray-800/50" data-testid="amenagement-footer">
          x4520-C | Rayon {ANALYSIS_RADIUS_M}m strict | STEEVE-MAX V6
        </div>
      </div>
    </PinnablePanel>
  );
};

/** Carte individuelle pour une saline selectionnee */
const SalineCard = ({ saline, index }) => (
  <div className="bg-[#0d0d18] rounded-xl p-3 border border-cyan-500/20" data-testid={`saline-card-${index}`}>
    <div className="flex items-center justify-between mb-2">
      <div className="flex items-center gap-2">
        <MapPin className="h-4 w-4 text-cyan-400" />
        <span className="text-sm font-bold text-white">{saline.id}</span>
        <span className="text-xs text-gray-500">({saline.type})</span>
      </div>
      <div className="flex items-center gap-2">
        <span className="text-xs text-cyan-300 bg-cyan-500/15 px-2 py-0.5 rounded-full">
          {saline.distance_centre_m}m
        </span>
        <span className="text-xs text-amber-300 bg-amber-500/15 px-2 py-0.5 rounded-full font-semibold">
          {saline.score}/100
        </span>
      </div>
    </div>
    {saline.justifications && saline.justifications.length > 0 && (
      <p className="text-xs text-gray-400 leading-relaxed mb-1.5">
        {saline.justifications.join(' | ')}
      </p>
    )}
    {saline.criteres && (
      <div className="flex flex-wrap gap-1.5">
        {Object.entries(saline.criteres).map(([key, val]) => (
          <span
            key={key}
            className="text-[10px] px-1.5 py-0.5 rounded bg-gray-800 text-gray-400"
          >
            {key}: {val}
          </span>
        ))}
      </div>
    )}
  </div>
);

const SectionCard = ({ title, detail, priority, icon: Icon, iconColor, testId }) => (
  <div className="bg-[#0d0d18] rounded-xl p-4 border border-gray-700/50" data-testid={testId}>
    <div className="flex items-center justify-between mb-2">
      <div className="flex items-center gap-2">
        <Icon className="h-5 w-5" style={{ color: iconColor }} />
        <span className="text-sm font-bold text-white">{title}</span>
      </div>
      {priority && (
        <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${priority === 'HIGH' ? 'bg-red-500/20 text-red-300' : 'bg-yellow-500/20 text-yellow-300'}`}>
          {priority}
        </span>
      )}
    </div>
    <p className="text-sm text-gray-400 leading-relaxed">{detail || 'N/A'}</p>
  </div>
);

export default AmenagementPanel;

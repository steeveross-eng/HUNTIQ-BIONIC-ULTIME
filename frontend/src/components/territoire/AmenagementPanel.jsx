import React from 'react';
import { Droplets, Eye, Wind, Navigation, Target, ListChecks } from 'lucide-react';
import PinnablePanel from './PinnablePanel';

/**
 * STEVE-MAX P5: Amenagement Report Panel — x4515-FIX
 * Saline, Cache (Affut), Vent, Trajet, Plan d'action
 * PinnablePanel: Fixer / Detacher / Pleine page / Scroll
 */
const AmenagementPanel = ({ report, isLoading, onClose }) => {
  if (isLoading) {
    return (
      <PinnablePanel title="Amenagement 2km" subtitle="Chargement..." icon={Target} accentColor="#f5a623" onClose={onClose} testId="amenagement-panel-loading">
        <div className="p-4 animate-pulse">
          <div className="h-4 bg-gray-800 rounded w-3/4 mb-3" />
          <div className="h-3 bg-gray-800 rounded w-1/2 mb-2" />
          <div className="h-3 bg-gray-800 rounded w-2/3" />
        </div>
      </PinnablePanel>
    );
  }

  if (!report || !report.sections) return null;
  const s = report.sections;

  return (
    <PinnablePanel
      title="Amenagement 2km"
      subtitle="Salines, Affuts, Vents, Plan d'action"
      icon={Target}
      accentColor="#f5a623"
      onClose={onClose}
      defaultWidth={400}
      maxHeight="80vh"
      testId="amenagement-panel"
    >
      <div className="p-4 space-y-4">
        {/* Saline */}
        {s['1_saline'] && (
          <SectionCard
            title={s['1_saline'].title}
            detail={s['1_saline'].justification}
            priority={s['1_saline'].priority}
            icon={Droplets}
            iconColor="#06b6d4"
            testId="amenagement-saline"
          />
        )}

        {/* Cache / Affut */}
        {s['3_cache'] && (
          <SectionCard
            title={s['3_cache'].title}
            detail={s['3_cache'].justification}
            priority={s['3_cache'].priority}
            icon={Eye}
            iconColor="#8b5cf6"
            testId="amenagement-cache"
          />
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
      </div>
    </PinnablePanel>
  );
};

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

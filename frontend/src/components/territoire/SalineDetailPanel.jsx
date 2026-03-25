import React from 'react';
import { Droplets, FlaskConical, Leaf, MapPin, AlertTriangle, CheckCircle } from 'lucide-react';
import PinnablePanel from './PinnablePanel';

/**
 * SalineDetailPanel.jsx — Detail d'une saline selectionnee
 * DIRECTIVE STEEVE-MAX x4520-H: PinnablePanel V2 (pleine page, fixable, scrollable)
 * Remplace le tooltip Leaflet natif dans AlimentationV2Layer
 */

const MINERALS = [
  { key: 'sodium', name: 'Sodium (Na)', color: '#2ECC71' },
  { key: 'calcium', name: 'Calcium (Ca)', color: '#E74C3C' },
  { key: 'phosphore', name: 'Phosphore (P)', color: '#E74C3C' },
  { key: 'magnesium', name: 'Magnesium (Mg)', color: '#F39C12' },
  { key: 'potassium', name: 'Potassium (K)', color: '#E74C3C' },
  { key: 'fer', name: 'Fer (Fe)', color: '#2ECC71' },
  { key: 'zinc', name: 'Zinc (Zn)', color: '#E74C3C' },
  { key: 'selenium', name: 'Selenium (Se)', color: '#E74C3C' },
];

function getMineralData(saline) {
  const base = [
    { name: 'Sodium (Na)', pct: 92, status: 'OK' },
    { name: 'Calcium (Ca)', pct: 38, status: 'DEFICIT' },
    { name: 'Phosphore (P)', pct: 28, status: 'DEFICIT' },
    { name: 'Magnesium (Mg)', pct: 55, status: 'MARGINAL' },
    { name: 'Potassium (K)', pct: 12, status: 'DEFICIT' },
    { name: 'Fer (Fe)', pct: 78, status: 'OK' },
    { name: 'Zinc (Zn)', pct: 35, status: 'DEFICIT' },
    { name: 'Selenium (Se)', pct: 18, status: 'DEFICIT' },
  ];
  if (saline?.minerals) return saline.minerals;
  // Deterministic variation based on saline ID
  const seed = (saline?.id || 'SAL-01').charCodeAt(4) || 1;
  return base.map((m, i) => ({
    ...m,
    pct: Math.max(5, Math.min(99, m.pct + ((seed * (i + 1) * 7) % 30) - 15)),
  })).map(m => ({
    ...m,
    status: m.pct >= 70 ? 'OK' : m.pct >= 40 ? 'MARGINAL' : 'DEFICIT',
  }));
}

const SalineDetailPanel = ({ saline, onClose }) => {
  if (!saline) return null;

  const isSelected = saline.selected;
  const scoreColor = saline.score > 65 ? '#2ECC71' : saline.score > 45 ? '#F39C12' : '#E74C3C';
  const minerals = getMineralData(saline);
  const deficits = minerals.filter(m => m.status === 'DEFICIT');
  const soilType = saline.soil_type || 'Loam argileux';
  const canopy = saline.canopy || 'Mixte (coniferes + feuillus)';
  const ph = saline.ph || 6.2;

  return (
    <PinnablePanel
      title={`${saline.id} — ${saline.type || 'minerale'}`}
      subtitle={`Score: ${saline.score}/100 | Distance: ${saline.distance_centre_m}m`}
      icon={Droplets}
      accentColor={isSelected ? '#FFD700' : '#9CA3AF'}
      onClose={onClose}
      defaultWidth={400}
      maxHeight="85vh"
      testId="saline-detail-panel"
    >
      <div className="p-4 space-y-4" data-testid="saline-detail-content">
        {/* Score + Status */}
        <div className="flex items-center justify-between" data-testid="saline-score-header">
          <div className="flex items-center gap-3">
            <div
              className="w-14 h-14 rounded-full flex items-center justify-center text-xl font-black"
              style={{ border: `3px solid ${scoreColor}`, color: scoreColor }}
            >
              {saline.score}
            </div>
            <div>
              <div className="text-white text-sm font-bold">{isSelected ? 'SELECTIONNEE' : 'Candidate'}</div>
              <div className="text-gray-500 text-xs">{saline.type || 'minerale'} | {saline.distance_centre_m}m</div>
            </div>
          </div>
          {isSelected && (
            <span className="text-xs bg-yellow-500/20 text-yellow-300 px-2 py-0.5 rounded-full font-semibold">Optimale</span>
          )}
        </div>

        {/* Terrain info */}
        <div className="bg-[#0d0d18] rounded-xl p-3 border border-cyan-500/20 space-y-1.5" data-testid="saline-terrain">
          <div className="text-xs font-semibold text-cyan-400">Couvert forestier optimal, Zone securisee</div>
          <div className="flex gap-4 text-xs text-gray-400">
            <span>Sol: <span className="text-cyan-300 font-semibold">{soilType}</span></span>
            <span>pH: <span className="text-cyan-300 font-semibold">{ph}</span></span>
          </div>
          <div className="text-xs text-gray-400">
            Couvert: <span className="text-cyan-300 font-semibold">{canopy}</span>
          </div>
        </div>

        {/* Mineral composition bars */}
        <div className="space-y-2" data-testid="saline-minerals">
          <div className="flex items-center gap-2 mb-2">
            <FlaskConical className="h-4 w-4 text-amber-400" />
            <span className="text-xs font-semibold text-amber-400">Composition minerale</span>
          </div>
          {minerals.map((m, i) => {
            const barColor = m.status === 'OK' ? '#2ECC71' : m.status === 'MARGINAL' ? '#F39C12' : '#E74C3C';
            const statusColor = m.status === 'OK' ? 'text-green-400' : m.status === 'MARGINAL' ? 'text-yellow-400' : 'text-red-400';
            return (
              <div key={i} className="flex items-center gap-2" data-testid={`saline-mineral-${i}`}>
                <span className="text-xs text-gray-400 w-28 flex-shrink-0">{m.name}</span>
                <div className="flex-1 h-2.5 bg-white/5 rounded-full overflow-hidden">
                  <div
                    className="h-full rounded-full transition-all"
                    style={{ width: `${m.pct}%`, backgroundColor: barColor }}
                  />
                </div>
                <span className="text-xs font-bold w-10 text-right" style={{ color: barColor }}>{m.pct}%</span>
                <span className={`text-[9px] font-semibold w-16 text-right ${statusColor}`}>{m.status}</span>
              </div>
            );
          })}
        </div>

        {/* Deficits */}
        {deficits.length > 0 && (
          <div className="bg-red-950/30 rounded-xl p-3 border border-red-500/20" data-testid="saline-deficits">
            <div className="flex items-center gap-2 mb-2">
              <AlertTriangle className="h-4 w-4 text-red-400" />
              <span className="text-xs font-semibold text-red-400">Carences identifiees</span>
            </div>
            {deficits.map((d, i) => (
              <div key={i} className="text-xs text-red-300/80">{d.name} — {d.pct}% couverture</div>
            ))}
          </div>
        )}

        {/* Recommendations */}
        <div className="bg-green-950/20 rounded-xl p-3 border border-green-500/20" data-testid="saline-recommendations">
          <div className="flex items-center gap-2 mb-2">
            <Leaf className="h-4 w-4 text-green-400" />
            <span className="text-xs font-semibold text-green-400">Recommandations</span>
          </div>
          <ul className="space-y-1">
            <li className="text-xs text-gray-400">Ajouter bloc mineral K + Se</li>
            <li className="text-xs text-gray-400">Suppleer en Phosphore</li>
            <li className="text-xs text-gray-400">Renouveler bloc toutes les 6-8 sem</li>
          </ul>
        </div>

        {/* Justifications */}
        {saline.justifications && saline.justifications.length > 0 && (
          <div className="bg-[#0d0d18] rounded-xl p-3 border border-gray-700/50" data-testid="saline-justifications">
            <div className="text-xs font-semibold text-amber-400 mb-1.5">Justification ecologique</div>
            <p className="text-xs text-gray-400 leading-relaxed">{saline.justifications.join(' | ')}</p>
          </div>
        )}

        {/* Eco justif */}
        <div className="text-xs text-gray-500 italic leading-relaxed" data-testid="saline-eco-justif">
          Sol {soilType}, pH {ph}. Couvert: {canopy}. Acidification coniferes reduit biodisponibilite P.
        </div>

        {/* Footer */}
        <div className="text-center text-[10px] text-gray-600 pt-2 border-t border-gray-800/50" data-testid="saline-footer">
          x4520-H | PinnablePanel V2 | Rayon 600m | STEEVE-MAX V6
        </div>
      </div>
    </PinnablePanel>
  );
};

export default SalineDetailPanel;

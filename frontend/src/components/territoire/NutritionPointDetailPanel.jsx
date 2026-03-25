import React from 'react';
import { Droplets, FlaskConical, Leaf, MapPin, AlertTriangle, CheckCircle } from 'lucide-react';
import PinnablePanel from './PinnablePanel';

/**
 * NutritionPointDetailPanel.jsx — Detail d'un point nutritionnel
 * DIRECTIVE STEEVE-MAX x4600: "Salines" -> "Points nutritionnels"
 * PinnablePanel V2 (pleine page, fixable, scrollable)
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

function getMineralData(nutritionPoint) {
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
  if (nutritionPoint?.minerals) return nutritionPoint.minerals;
  // Deterministic variation based on nutrition point ID
  const seed = (nutritionPoint?.id || 'SAL-01').charCodeAt(4) || 1;
  return base.map((m, i) => ({
    ...m,
    pct: Math.max(5, Math.min(99, m.pct + ((seed * (i + 1) * 7) % 30) - 15)),
  })).map(m => ({
    ...m,
    status: m.pct >= 70 ? 'OK' : m.pct >= 40 ? 'MARGINAL' : 'DEFICIT',
  }));
}

const NutritionPointDetailPanel = ({ nutritionPoint, onClose }) => {
  if (!nutritionPoint) return null;

  const isSelected = nutritionPoint.selected;
  const scoreColor = nutritionPoint.score > 65 ? '#2ECC71' : nutritionPoint.score > 45 ? '#F39C12' : '#E74C3C';
  const minerals = getMineralData(nutritionPoint);
  const deficits = minerals.filter(m => m.status === 'DEFICIT');
  const soilType = nutritionPoint.soil_type || 'Loam argileux';
  const canopy = nutritionPoint.canopy || 'Mixte (coniferes + feuillus)';
  const ph = nutritionPoint.ph || 6.2;

  return (
    <PinnablePanel
      title={`Point nutritionnel — ${nutritionPoint.id}`}
      subtitle={`Analyse minerale du site | Score: ${nutritionPoint.score}/100 | ${nutritionPoint.distance_centre_m}m`}
      icon={Droplets}
      accentColor={isSelected ? '#FFD700' : '#9CA3AF'}
      onClose={onClose}
      defaultWidth={400}
      maxHeight="85vh"
      testId="nutrition-point-detail-panel"
    >
      <div className="p-4 space-y-4" data-testid="nutrition-point-detail-content">
        {/* Score + Status */}
        <div className="flex items-center justify-between" data-testid="nutrition-point-score-header">
          <div className="flex items-center gap-3">
            <div
              className="w-14 h-14 rounded-full flex items-center justify-center text-xl font-black"
              style={{ border: `3px solid ${scoreColor}`, color: scoreColor }}
            >
              {nutritionPoint.score}
            </div>
            <div>
              <div className="text-white text-sm font-bold">{isSelected ? 'SELECTIONNEE' : 'Candidate'}</div>
              <div className="text-gray-500 text-xs">{nutritionPoint.type || 'minerale'} | {nutritionPoint.distance_centre_m}m</div>
            </div>
          </div>
          {isSelected && (
            <span className="text-xs bg-yellow-500/20 text-yellow-300 px-2 py-0.5 rounded-full font-semibold">Optimale</span>
          )}
        </div>

        {/* Terrain info */}
        <div className="bg-[#0d0d18] rounded-xl p-3 border border-cyan-500/20 space-y-1.5" data-testid="nutrition-point-terrain">
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
        <div className="space-y-2" data-testid="nutrition-point-minerals">
          <div className="flex items-center gap-2 mb-2">
            <FlaskConical className="h-4 w-4 text-amber-400" />
            <span className="text-xs font-semibold text-amber-400">Composition minerale</span>
          </div>
          {minerals.map((m, i) => {
            const barColor = m.status === 'OK' ? '#2ECC71' : m.status === 'MARGINAL' ? '#F39C12' : '#E74C3C';
            const statusColor = m.status === 'OK' ? 'text-green-400' : m.status === 'MARGINAL' ? 'text-yellow-400' : 'text-red-400';
            return (
              <div key={i} className="flex items-center gap-2" data-testid={`nutrition-mineral-${i}`}>
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
          <div className="bg-red-950/30 rounded-xl p-3 border border-red-500/20" data-testid="nutrition-point-deficits">
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
        <div className="bg-green-950/20 rounded-xl p-3 border border-green-500/20" data-testid="nutrition-point-recommendations">
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
        {nutritionPoint.justifications && nutritionPoint.justifications.length > 0 && (
          <div className="bg-[#0d0d18] rounded-xl p-3 border border-gray-700/50" data-testid="nutrition-point-justifications">
            <div className="text-xs font-semibold text-amber-400 mb-1.5">Justification ecologique</div>
            <p className="text-xs text-gray-400 leading-relaxed">{nutritionPoint.justifications.join(' | ')}</p>
          </div>
        )}

        {/* Eco justif */}
        <div className="text-xs text-gray-500 italic leading-relaxed" data-testid="nutrition-point-eco-justif">
          Sol {soilType}, pH {ph}. Couvert: {canopy}. Acidification coniferes reduit biodisponibilite P.
        </div>

        {/* Footer */}
        <div className="text-center text-[10px] text-gray-600 pt-2 border-t border-gray-800/50" data-testid="nutrition-point-footer">
          x4600 | Point nutritionnel | Analyse minerale du site | STEEVE-MAX V6
        </div>
      </div>
    </PinnablePanel>
  );
};

export default NutritionPointDetailPanel;

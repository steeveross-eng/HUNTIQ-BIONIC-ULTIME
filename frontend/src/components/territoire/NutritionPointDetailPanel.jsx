import React, { useState } from 'react';
import { Droplets, FlaskConical, Leaf, MapPin, AlertTriangle, ChevronDown, ChevronUp, Layers, Beaker } from 'lucide-react';
import PinnablePanel from './PinnablePanel';

/**
 * NutritionPointDetailPanel.jsx — Panneau premium Point nutritionnel
 * DIRECTIVE x4700-VISUAL_REDESIGN-R2-DASHBOARD_STYLE
 * Style: Dashboard BIONIC cards premium
 * Palette: #00C853, #F9D423, #FF9800, #D32F2F, #2196F3, #ECEFF1, #37474F
 */

const BIONIC = {
  green: '#00C853',
  yellow: '#F9D423',
  orange: '#FF9800',
  red: '#D32F2F',
  blue: '#2196F3',
  light: '#ECEFF1',
  dark: '#37474F',
  card: '#1a1a2e',
  cardBorder: 'rgba(255,255,255,0.06)',
};

function getScoreGrade(score) {
  if (score >= 80) return { label: 'EXCELLENT', color: BIONIC.green, bg: 'rgba(0,200,83,0.12)' };
  if (score >= 65) return { label: 'BON', color: BIONIC.yellow, bg: 'rgba(249,212,35,0.12)' };
  if (score >= 50) return { label: 'MODERE', color: BIONIC.orange, bg: 'rgba(255,152,0,0.12)' };
  return { label: 'FAIBLE', color: BIONIC.red, bg: 'rgba(211,47,47,0.12)' };
}

function getMineralData(nutritionPoint) {
  const base = [
    { name: 'Sodium (Na)', pct: 92 },
    { name: 'Calcium (Ca)', pct: 38 },
    { name: 'Phosphore (P)', pct: 28 },
    { name: 'Magnesium (Mg)', pct: 55 },
    { name: 'Potassium (K)', pct: 12 },
    { name: 'Fer (Fe)', pct: 78 },
    { name: 'Zinc (Zn)', pct: 35 },
    { name: 'Selenium (Se)', pct: 18 },
  ];
  if (nutritionPoint?.minerals) return nutritionPoint.minerals;
  const seed = (nutritionPoint?.id || 'SAL-01').charCodeAt(4) || 1;
  return base.map((m, i) => {
    const pct = Math.max(5, Math.min(99, m.pct + ((seed * (i + 1) * 7) % 30) - 15));
    return { ...m, pct, status: pct >= 70 ? 'OK' : pct >= 40 ? 'MARGINAL' : 'DEFICIT' };
  });
}

function getMineralBarColor(status) {
  if (status === 'OK') return BIONIC.green;
  if (status === 'MARGINAL') return BIONIC.orange;
  return BIONIC.red;
}

const Card = ({ children, className = '', testId, noPad = false }) => (
  <div
    className={`rounded-[14px] border ${className}`}
    style={{ backgroundColor: BIONIC.card, borderColor: BIONIC.cardBorder, boxShadow: '0 2px 8px rgba(0,0,0,0.18)' }}
    data-testid={testId}
  >
    {!noPad ? <div className="p-4">{children}</div> : children}
  </div>
);

const NutritionPointDetailPanel = ({ nutritionPoint, onClose }) => {
  const [showJustif, setShowJustif] = useState(false);

  if (!nutritionPoint) return null;

  const isSelected = nutritionPoint.selected;
  const grade = getScoreGrade(nutritionPoint.score);
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
      accentColor={grade.color}
      onClose={onClose}
      defaultWidth={580}
      maxHeight="85vh"
      testId="nutrition-point-detail-panel"
      showPrint={true}
    >
      <div className="p-5 space-y-4" style={{ maxWidth: 620 }} data-testid="nutrition-point-detail-content">

        {/* HEADER PREMIUM — Score + Grade + Distance */}
        <Card testId="nutrition-score-card">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div
                className="w-[68px] h-[68px] rounded-2xl flex items-center justify-center"
                style={{ background: `linear-gradient(135deg, ${grade.color}22, ${grade.color}08)`, border: `2.5px solid ${grade.color}` }}
                data-testid="nutrition-score-badge"
              >
                <span className="text-2xl font-black" style={{ color: grade.color }}>{nutritionPoint.score}</span>
              </div>
              <div>
                <div className="text-white text-base font-bold">{isSelected ? 'SELECTIONNEE' : 'Candidate'}</div>
                <div className="text-gray-400 text-sm mt-0.5">{nutritionPoint.type || 'minerale'} | {nutritionPoint.distance_centre_m}m</div>
                <div className="flex items-center gap-1 text-gray-500 text-xs mt-1">
                  <MapPin className="h-3 w-3" />
                  <span>Analyse minerale du site</span>
                </div>
              </div>
            </div>
            {isSelected && (
              <div
                className="px-3 py-1.5 rounded-xl text-xs font-bold tracking-wide"
                style={{ backgroundColor: 'rgba(249,212,35,0.12)', color: BIONIC.yellow, border: `1px solid ${BIONIC.yellow}30` }}
                data-testid="nutrition-optimale-badge"
              >
                Optimale
              </div>
            )}
          </div>
        </Card>

        {/* TERRAIN — Bloc structure */}
        <Card testId="nutrition-terrain-card">
          <div className="flex items-center gap-2 mb-3">
            <Layers className="h-4 w-4" style={{ color: '#00BCD4' }} />
            <span className="text-sm font-bold text-white">Couvert forestier</span>
            <span className="px-2 py-0.5 rounded-lg text-[10px] font-semibold ml-auto" style={{ backgroundColor: `${BIONIC.green}18`, color: BIONIC.green }}>Zone securisee</span>
          </div>
          <div className="grid grid-cols-2 gap-x-6 gap-y-2">
            {[
              { label: 'Sol', value: soilType, color: '#00BCD4' },
              { label: 'pH', value: String(ph), color: '#00BCD4' },
              { label: 'Couvert', value: canopy, color: '#00BCD4' },
            ].map((item, i) => (
              <div key={i} className={`flex justify-between items-center py-1.5 border-b ${i === 2 ? 'col-span-2' : ''}`} style={{ borderColor: 'rgba(255,255,255,0.04)' }}>
                <span className="text-xs text-gray-500">{item.label}</span>
                <span className="text-xs font-semibold" style={{ color: item.color }}>{item.value}</span>
              </div>
            ))}
          </div>
        </Card>

        {/* COMPOSITION MINERALE — BarFlow premium */}
        <Card testId="nutrition-minerals-card">
          <div className="flex items-center gap-2 mb-4">
            <FlaskConical className="h-4 w-4" style={{ color: BIONIC.yellow }} />
            <span className="text-sm font-bold text-white">Composition minerale</span>
            <span className="text-xs text-gray-500 ml-auto">8 mineraux</span>
          </div>
          <div className="space-y-3" data-testid="nutrition-mineral-bars">
            {minerals.map((m, i) => {
              const barColor = getMineralBarColor(m.status);
              const statusLabel = m.status === 'OK' ? 'OK' : m.status === 'MARGINAL' ? 'MARG.' : 'DEF.';
              return (
                <div key={i} className="flex items-center gap-3" data-testid={`nutrition-mineral-${i}`}>
                  <span className="text-xs text-gray-300 w-28 flex-shrink-0 font-medium">{m.name}</span>
                  <div className="flex-1 h-[6px] rounded-full overflow-hidden" style={{ backgroundColor: 'rgba(255,255,255,0.04)' }}>
                    <div
                      className="h-full rounded-full"
                      style={{ width: `${m.pct}%`, backgroundColor: barColor, transition: 'width 0.6s ease' }}
                    />
                  </div>
                  <span className="text-sm font-bold w-10 text-right tabular-nums" style={{ color: barColor }}>
                    {m.pct}%
                  </span>
                  <span
                    className="text-[10px] font-bold w-10 text-right"
                    style={{ color: barColor }}
                  >
                    {statusLabel}
                  </span>
                </div>
              );
            })}
          </div>
        </Card>

        {/* CARENCES */}
        {deficits.length > 0 && (
          <Card testId="nutrition-deficits-card">
            <div className="flex items-center gap-2 mb-3">
              <AlertTriangle className="h-4 w-4" style={{ color: BIONIC.red }} />
              <span className="text-sm font-bold text-white">Carences identifiees</span>
              <span className="px-2 py-0.5 rounded-lg text-[10px] font-bold ml-auto" style={{ backgroundColor: `${BIONIC.red}18`, color: BIONIC.red }}>{deficits.length} deficits</span>
            </div>
            <div className="space-y-1.5">
              {deficits.map((d, i) => (
                <div key={i} className="flex items-center justify-between py-1.5 border-b" style={{ borderColor: 'rgba(255,255,255,0.04)' }}>
                  <span className="text-xs text-gray-400">{d.name}</span>
                  <span className="text-xs font-semibold" style={{ color: BIONIC.red }}>{d.pct}% couverture</span>
                </div>
              ))}
            </div>
          </Card>
        )}

        {/* RECOMMANDATIONS */}
        <Card testId="nutrition-recommendations-card">
          <div className="flex items-center gap-2 mb-3">
            <Leaf className="h-4 w-4" style={{ color: BIONIC.green }} />
            <span className="text-sm font-bold text-white">Recommandations</span>
          </div>
          <div className="space-y-2">
            {[
              { text: 'Ajouter bloc mineral K + Se', priority: 'haute' },
              { text: 'Suppleer en Phosphore', priority: 'haute' },
              { text: 'Renouveler bloc toutes les 6-8 sem', priority: 'moyenne' },
            ].map((r, i) => (
              <div key={i} className="flex items-center gap-3 py-1.5">
                <div className="w-1.5 h-1.5 rounded-full flex-shrink-0" style={{ backgroundColor: r.priority === 'haute' ? BIONIC.orange : BIONIC.blue }} />
                <span className="text-xs text-gray-300 flex-1">{r.text}</span>
                <span className="text-[10px] font-semibold px-2 py-0.5 rounded-lg" style={{ backgroundColor: r.priority === 'haute' ? `${BIONIC.orange}15` : `${BIONIC.blue}15`, color: r.priority === 'haute' ? BIONIC.orange : BIONIC.blue }}>
                  {r.priority}
                </span>
              </div>
            ))}
          </div>
        </Card>

        {/* JUSTIFICATION REPLIABLE */}
        {nutritionPoint.justifications && nutritionPoint.justifications.length > 0 && (
          <Card testId="nutrition-justif-card" noPad>
            <button
              onClick={() => setShowJustif(v => !v)}
              className="w-full flex items-center justify-between p-4 hover:bg-white/[0.02] transition-colors rounded-[14px]"
              data-testid="nutrition-justif-toggle"
            >
              <div className="flex items-center gap-2">
                <Beaker className="h-4 w-4" style={{ color: BIONIC.yellow }} />
                <span className="text-sm font-bold text-white">Justification ecologique</span>
              </div>
              {showJustif ? <ChevronUp className="h-4 w-4 text-gray-500" /> : <ChevronDown className="h-4 w-4 text-gray-500" />}
            </button>
            {showJustif && (
              <div className="px-4 pb-4">
                <div className="rounded-xl p-3" style={{ backgroundColor: `${BIONIC.yellow}08`, borderLeft: `3px solid ${BIONIC.yellow}` }}>
                  <p className="text-xs text-gray-400 leading-relaxed">{nutritionPoint.justifications.join(' | ')}</p>
                </div>
              </div>
            )}
          </Card>
        )}

        {/* ECO CONTEXT */}
        <div className="text-xs text-gray-500 leading-relaxed px-1" data-testid="nutrition-eco-context">
          Sol {soilType}, pH {ph}. Couvert: {canopy}. Acidification coniferes reduit biodisponibilite P.
        </div>

        {/* FOOTER */}
        <div className="text-center text-[10px] text-gray-600 pt-1" data-testid="nutrition-footer">
          x4700-R2 | Dashboard BIONIC Style | Analyse minerale du site | STEEVE-MAX V6
        </div>
      </div>
    </PinnablePanel>
  );
};

export default NutritionPointDetailPanel;

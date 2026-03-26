import React, { useState } from 'react';
import { Droplets, FlaskConical, Leaf, MapPin, AlertTriangle, ChevronDown, ChevronUp, Layers, Beaker } from 'lucide-react';
import PinnablePanel from './PinnablePanel';

/**
 * NutritionPointDetailPanel.jsx — Panneau PLEINE PAGE Point nutritionnel
 * x4700-VISUAL_REDESIGN-R2 CORRECTIF: 100vh, ZERO scroll, X + Imprimer fixes
 * Style: Dashboard BIONIC premium
 */

const BIONIC = {
  green: '#00C853', yellow: '#F9D423', orange: '#FF9800', red: '#D32F2F',
  blue: '#2196F3', card: '#1a1a2e', cardBorder: 'rgba(255,255,255,0.06)',
};

function getScoreGrade(score) {
  if (score >= 80) return { label: 'EXCELLENT', color: BIONIC.green, bg: 'rgba(0,200,83,0.12)' };
  if (score >= 65) return { label: 'BON', color: BIONIC.yellow, bg: 'rgba(249,212,35,0.12)' };
  if (score >= 50) return { label: 'MODERE', color: BIONIC.orange, bg: 'rgba(255,152,0,0.12)' };
  return { label: 'FAIBLE', color: BIONIC.red, bg: 'rgba(211,47,47,0.12)' };
}

function getMineralData(np) {
  const base = [
    { name: 'Sodium (Na)', pct: 92 }, { name: 'Calcium (Ca)', pct: 38 },
    { name: 'Phosphore (P)', pct: 28 }, { name: 'Magnesium (Mg)', pct: 55 },
    { name: 'Potassium (K)', pct: 12 }, { name: 'Fer (Fe)', pct: 78 },
    { name: 'Zinc (Zn)', pct: 35 }, { name: 'Selenium (Se)', pct: 18 },
  ];
  if (np?.minerals) return np.minerals;
  const seed = (np?.id || 'SAL-01').charCodeAt(4) || 1;
  return base.map((m, i) => {
    const pct = Math.max(5, Math.min(99, m.pct + ((seed * (i + 1) * 7) % 30) - 15));
    return { ...m, pct, status: pct >= 70 ? 'OK' : pct >= 40 ? 'MARGINAL' : 'DEFICIT' };
  });
}

function barColor(s) { return s === 'OK' ? BIONIC.green : s === 'MARGINAL' ? BIONIC.orange : BIONIC.red; }

const Card = ({ children, testId, className = '' }) => (
  <div className={`rounded-[14px] border p-3 ${className}`} style={{ backgroundColor: BIONIC.card, borderColor: BIONIC.cardBorder, boxShadow: '0 2px 8px rgba(0,0,0,0.18)' }} data-testid={testId}>{children}</div>
);

const NutritionPointDetailPanel = ({ nutritionPoint, onClose }) => {
  const [showJustif, setShowJustif] = useState(false);
  if (!nutritionPoint) return null;

  const np = nutritionPoint;
  const isSelected = np.selected;
  const grade = getScoreGrade(np.score);
  const minerals = getMineralData(np);
  const deficits = minerals.filter(m => m.status === 'DEFICIT');
  const soilType = np.soil_type || 'Loam argileux';
  const canopy = np.canopy || 'Mixte (coniferes + feuillus)';
  const ph = np.ph || 6.2;

  return (
    <PinnablePanel
      title={`Point nutritionnel — ${np.id}`}
      subtitle={`Analyse minerale du site | Score: ${np.score}/100 | ${np.distance_centre_m}m`}
      icon={Droplets}
      accentColor={grade.color}
      onClose={onClose}
      defaultWidth={580}
      maxHeight="100vh"
      testId="nutrition-point-detail-panel"
      showPrint={true}
      fullHeight={true}
    >
      {/* GRID LAYOUT — 2 colonnes pour tout afficher en 100vh sans scroll */}
      <div className="h-full grid grid-cols-2 gap-3 p-4 overflow-hidden" data-testid="nutrition-point-detail-content">

        {/* COLONNE GAUCHE */}
        <div className="flex flex-col gap-3 min-h-0">
          {/* Score Header */}
          <Card testId="nutrition-score-card">
            <div className="flex items-center gap-3">
              <div className="w-14 h-14 rounded-xl flex items-center justify-center flex-shrink-0" style={{ background: `linear-gradient(135deg, ${grade.color}22, ${grade.color}08)`, border: `2.5px solid ${grade.color}` }} data-testid="nutrition-score-badge">
                <span className="text-2xl font-black" style={{ color: grade.color }}>{np.score}</span>
              </div>
              <div className="min-w-0">
                <div className="text-white text-sm font-bold">{isSelected ? 'SELECTIONNEE' : 'Candidate'}</div>
                <div className="text-gray-400 text-xs mt-0.5">{np.type || 'minerale'} | {np.distance_centre_m}m</div>
                <div className="flex items-center gap-1 text-gray-500 text-[10px] mt-0.5">
                  <MapPin className="h-2.5 w-2.5" /><span>Analyse minerale du site</span>
                </div>
              </div>
              {isSelected && (
                <div className="px-2 py-1 rounded-lg text-[10px] font-bold ml-auto flex-shrink-0" style={{ backgroundColor: `${BIONIC.yellow}18`, color: BIONIC.yellow }} data-testid="nutrition-optimale-badge">Optimale</div>
              )}
            </div>
          </Card>

          {/* Terrain */}
          <Card testId="nutrition-terrain-card">
            <div className="flex items-center gap-2 mb-2">
              <Layers className="h-3.5 w-3.5" style={{ color: '#00BCD4' }} />
              <span className="text-xs font-bold text-white">Couvert forestier</span>
              <span className="px-1.5 py-0.5 rounded text-[9px] font-semibold ml-auto" style={{ backgroundColor: `${BIONIC.green}18`, color: BIONIC.green }}>Securise</span>
            </div>
            <div className="space-y-1">
              {[
                { label: 'Sol', value: soilType },
                { label: 'pH', value: String(ph) },
                { label: 'Couvert', value: canopy },
              ].map((item, i) => (
                <div key={i} className="flex justify-between items-center py-0.5 border-b" style={{ borderColor: 'rgba(255,255,255,0.04)' }}>
                  <span className="text-[10px] text-gray-500">{item.label}</span>
                  <span className="text-[10px] font-semibold" style={{ color: '#00BCD4' }}>{item.value}</span>
                </div>
              ))}
            </div>
          </Card>

          {/* Carences */}
          {deficits.length > 0 && (
            <Card testId="nutrition-deficits-card">
              <div className="flex items-center gap-2 mb-2">
                <AlertTriangle className="h-3.5 w-3.5" style={{ color: BIONIC.red }} />
                <span className="text-xs font-bold text-white">Carences</span>
                <span className="px-1.5 py-0.5 rounded text-[9px] font-bold ml-auto" style={{ backgroundColor: `${BIONIC.red}18`, color: BIONIC.red }}>{deficits.length}</span>
              </div>
              <div className="space-y-1">
                {deficits.map((d, i) => (
                  <div key={i} className="flex items-center justify-between py-0.5">
                    <span className="text-[10px] text-gray-400">{d.name}</span>
                    <span className="text-[10px] font-semibold" style={{ color: BIONIC.red }}>{d.pct}%</span>
                  </div>
                ))}
              </div>
            </Card>
          )}

          {/* Recommandations */}
          <Card testId="nutrition-recommendations-card" className="flex-1">
            <div className="flex items-center gap-2 mb-2">
              <Leaf className="h-3.5 w-3.5" style={{ color: BIONIC.green }} />
              <span className="text-xs font-bold text-white">Recommandations</span>
            </div>
            <div className="space-y-1.5">
              {[
                { text: 'Ajouter bloc mineral K + Se', p: 'haute' },
                { text: 'Suppleer en Phosphore', p: 'haute' },
                { text: 'Renouveler bloc toutes les 6-8 sem', p: 'moyenne' },
              ].map((r, i) => (
                <div key={i} className="flex items-center gap-2 py-0.5">
                  <div className="w-1.5 h-1.5 rounded-full flex-shrink-0" style={{ backgroundColor: r.p === 'haute' ? BIONIC.orange : BIONIC.blue }} />
                  <span className="text-[10px] text-gray-300 flex-1">{r.text}</span>
                  <span className="text-[9px] font-semibold px-1.5 py-0.5 rounded" style={{ backgroundColor: r.p === 'haute' ? `${BIONIC.orange}15` : `${BIONIC.blue}15`, color: r.p === 'haute' ? BIONIC.orange : BIONIC.blue }}>{r.p}</span>
                </div>
              ))}
            </div>
          </Card>
        </div>

        {/* COLONNE DROITE */}
        <div className="flex flex-col gap-3 min-h-0">
          {/* Composition minerale — 8 barres */}
          <Card testId="nutrition-minerals-card" className="flex-1 flex flex-col">
            <div className="flex items-center gap-2 mb-2">
              <FlaskConical className="h-3.5 w-3.5" style={{ color: BIONIC.yellow }} />
              <span className="text-xs font-bold text-white">Composition minerale</span>
              <span className="text-[10px] text-gray-500 ml-auto">8 mineraux</span>
            </div>
            <div className="space-y-1.5 flex-1" data-testid="nutrition-mineral-bars">
              {minerals.map((m, i) => {
                const bc = barColor(m.status);
                return (
                  <div key={i} className="flex items-center gap-2" data-testid={`nutrition-mineral-${i}`}>
                    <span className="text-[10px] text-gray-300 w-24 flex-shrink-0">{m.name}</span>
                    <div className="flex-1 h-[5px] rounded-full overflow-hidden" style={{ backgroundColor: 'rgba(255,255,255,0.04)' }}>
                      <div className="h-full rounded-full" style={{ width: `${m.pct}%`, backgroundColor: bc, transition: 'width 0.6s ease' }} />
                    </div>
                    <span className="text-xs font-bold w-8 text-right tabular-nums" style={{ color: bc }}>{m.pct}%</span>
                    <span className="text-[9px] font-bold w-8 text-right" style={{ color: bc }}>{m.status === 'OK' ? 'OK' : m.status === 'MARGINAL' ? 'MARG' : 'DEF'}</span>
                  </div>
                );
              })}
            </div>
          </Card>

          {/* Justification repliable */}
          {np.justifications && np.justifications.length > 0 && (
            <Card testId="nutrition-justif-card">
              <button onClick={() => setShowJustif(v => !v)} className="w-full flex items-center justify-between" data-testid="nutrition-justif-toggle">
                <div className="flex items-center gap-2">
                  <Beaker className="h-3.5 w-3.5" style={{ color: BIONIC.yellow }} />
                  <span className="text-xs font-bold text-white">Justification</span>
                </div>
                {showJustif ? <ChevronUp className="h-3.5 w-3.5 text-gray-500" /> : <ChevronDown className="h-3.5 w-3.5 text-gray-500" />}
              </button>
              {showJustif && (
                <div className="mt-2 rounded-lg p-2" style={{ backgroundColor: `${BIONIC.yellow}08`, borderLeft: `2px solid ${BIONIC.yellow}` }}>
                  <p className="text-[10px] text-gray-400 leading-relaxed">{np.justifications.join(' | ')}</p>
                </div>
              )}
            </Card>
          )}

          {/* Eco context */}
          <div className="text-[10px] text-gray-500 leading-relaxed px-1" data-testid="nutrition-eco-context">
            Sol {soilType}, pH {ph}. Couvert: {canopy}. Acidification coniferes reduit biodisponibilite P.
          </div>
        </div>

        {/* FOOTER — pleine largeur */}
        <div className="col-span-2 text-center text-[10px] text-gray-600" data-testid="nutrition-footer">
          x4700-R2 | Point nutritionnel | Analyse minerale du site | STEEVE-MAX V6
        </div>
      </div>
    </PinnablePanel>
  );
};

export default NutritionPointDetailPanel;

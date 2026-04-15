/**
 * ScoreV8Badge — Badge Score V8 National
 * ========================================
 * BCE-4X V8-INTEGRATION-Omega — PHASE 1
 * Anneau SVG progressif + 10 composantes + prediction + contexte biome
 * ZERO fallback V6/V7
 */
import React, { useState } from 'react';
import { Gauge, ChevronDown, ChevronUp } from 'lucide-react';

const PREDICTION_CONFIG = {
  excellent: { color: '#10B981', label: 'EXCELLENT' },
  bon:       { color: '#22D3EE', label: 'BON' },
  moyen:     { color: '#F59E0B', label: 'MOYEN' },
  faible:    { color: '#EF4444', label: 'FAIBLE' },
};

const COMPONENT_META = {
  temporal:     { label: 'Temporel',    color: '#F59E0B', short: 'TMP' },
  solunar:      { label: 'Solunaire',   color: '#A78BFA', short: 'SOL' },
  rut:          { label: 'Rut',         color: '#EC4899', short: 'RUT' },
  nutrition:    { label: 'Nutrition',   color: '#10B981', short: 'NUT' },
  biome_compat: { label: 'Biome',      color: '#3B82F6', short: 'BIO' },
  snow:         { label: 'Neige',       color: '#E2E8F0', short: 'NEI' },
  forest:       { label: 'Foret',       color: '#22C55E', short: 'FOR' },
  meteo:        { label: 'Meteo',       color: '#60A5FA', short: 'MET' },
  vision:       { label: 'Vision IA',   color: '#F97316', short: 'VIS' },
  habitat:      { label: 'Habitat',     color: '#14B8A6', short: 'HAB' },
};

const getScoreColor = (s) => {
  if (s >= 78) return '#10B981';
  if (s >= 58) return '#22D3EE';
  if (s >= 38) return '#F59E0B';
  return '#EF4444';
};

export const ScoreV8Badge = ({ scoreV8, biomeProfile, loading, compact = false }) => {
  const [expanded, setExpanded] = useState(false);

  if (loading) {
    return (
      <div
        className="flex items-center gap-2 h-9 px-3 rounded-lg border border-gray-700/40 bg-gray-800/30"
        data-testid="score-v8-badge-loading"
      >
        <div className="w-4 h-4 rounded-full border-2 border-gray-500 border-t-transparent animate-spin" />
        <span className="text-[10px] text-gray-500 uppercase tracking-wider">Score V8...</span>
      </div>
    );
  }

  if (!scoreV8) return null;

  const score = scoreV8.score_v8;
  const prediction = scoreV8.prediction || 'moyen';
  const detail = scoreV8.scores_detail || {};
  const context = scoreV8.context || {};
  const predCfg = PREDICTION_CONFIG[prediction] || PREDICTION_CONFIG.moyen;
  const scoreColor = getScoreColor(score);

  const pct = Math.min(1, Math.max(0, score / 100));
  const circumference = 2 * Math.PI * 14;
  const strokeDash = `${circumference * pct} ${circumference * (1 - pct)}`;

  if (compact) {
    return (
      <div
        className="flex items-center gap-2 h-9 px-3 rounded-lg border transition-all cursor-pointer"
        style={{ borderColor: `${scoreColor}40`, backgroundColor: `${scoreColor}08` }}
        onClick={() => setExpanded(!expanded)}
        data-testid="score-v8-badge-compact"
      >
        <svg width="28" height="28" viewBox="0 0 32 32">
          <circle cx="16" cy="16" r="14" fill="none" stroke="#374151" strokeWidth="2" />
          <circle
            cx="16" cy="16" r="14" fill="none"
            stroke={scoreColor} strokeWidth="2.5" strokeLinecap="round"
            strokeDasharray={strokeDash}
            transform="rotate(-90 16 16)"
            style={{ transition: 'stroke-dasharray 0.8s ease-out' }}
          />
          <text x="16" y="18" textAnchor="middle" fill={scoreColor} fontSize="8" fontWeight="800">
            {Math.round(score)}
          </text>
        </svg>
        <div className="flex flex-col leading-none">
          <span className="text-[10px] text-gray-500 uppercase tracking-wider">Score V8</span>
          <span className="text-xs font-bold" style={{ color: predCfg.color }}>
            {predCfg.label}
          </span>
        </div>
      </div>
    );
  }

  return (
    <div className="relative" data-testid="score-v8-badge">
      <div
        className="flex items-center gap-2 h-9 px-3 rounded-lg border transition-all cursor-pointer select-none"
        style={{ borderColor: `${scoreColor}40`, backgroundColor: `${scoreColor}08` }}
        onClick={() => setExpanded(!expanded)}
        data-testid="score-v8-badge-trigger"
      >
        <svg width="28" height="28" viewBox="0 0 32 32">
          <circle cx="16" cy="16" r="14" fill="none" stroke="#374151" strokeWidth="2" />
          <circle
            cx="16" cy="16" r="14" fill="none"
            stroke={scoreColor} strokeWidth="2.5" strokeLinecap="round"
            strokeDasharray={strokeDash}
            transform="rotate(-90 16 16)"
            style={{ transition: 'stroke-dasharray 0.8s ease-out' }}
          />
          <text x="16" y="18" textAnchor="middle" fill={scoreColor} fontSize="8" fontWeight="800">
            {Math.round(score)}
          </text>
        </svg>
        <div className="flex flex-col leading-none">
          <span className="text-[10px] text-gray-500 uppercase tracking-wider">Score V8</span>
          <span className="text-xs font-bold" style={{ color: predCfg.color }}>
            {Math.round(score)}/100 <span className="text-[9px] font-medium opacity-80">{predCfg.label}</span>
          </span>
        </div>
        {expanded ? <ChevronUp className="h-3 w-3 text-gray-500" /> : <ChevronDown className="h-3 w-3 text-gray-500" />}
      </div>

      {expanded && (
        <div
          className="absolute top-11 right-0 z-[9999] w-72 bg-gray-950/95 backdrop-blur-xl border border-gray-700/50 rounded-lg shadow-2xl p-3 space-y-3"
          data-testid="score-v8-detail-panel"
        >
          {/* Score composite */}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Gauge className="h-4 w-4" style={{ color: scoreColor }} />
              <span className="text-xs font-bold text-white">SCORE V8 NATIONAL</span>
            </div>
            <span className="text-[9px] text-gray-500 font-mono">{scoreV8.engine}</span>
          </div>

          <div className="text-center">
            <div className="text-4xl font-black" style={{ color: scoreColor }}>{Math.round(score)}</div>
            <div className="text-[10px] font-bold mt-0.5" style={{ color: predCfg.color }}>{predCfg.label}</div>
          </div>

          {/* 10 composantes */}
          <div className="space-y-1">
            <div className="text-[9px] text-gray-500 uppercase tracking-wider">10 Composantes</div>
            <div className="grid grid-cols-2 gap-1">
              {Object.entries(COMPONENT_META).map(([key, meta]) => {
                const val = detail[key] ?? 0;
                const barW = Math.min(100, Math.max(0, val));
                return (
                  <div key={key} className="flex items-center gap-1.5 bg-gray-900/40 rounded px-1.5 py-1" data-testid={`score-v8-component-${key}`}>
                    <span className="text-[8px] font-bold w-6 text-right" style={{ color: meta.color }}>{meta.short}</span>
                    <div className="flex-1 h-1.5 bg-gray-800 rounded-full overflow-hidden">
                      <div
                        className="h-full rounded-full transition-all duration-500"
                        style={{ width: `${barW}%`, backgroundColor: meta.color }}
                      />
                    </div>
                    <span className="text-[9px] font-bold text-gray-300 w-6 text-right">{Math.round(val)}</span>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Contexte biome */}
          {context.biome && (
            <div className="space-y-1 border-t border-gray-800/50 pt-2">
              <div className="text-[9px] text-gray-500 uppercase tracking-wider">Contexte National</div>
              <div className="grid grid-cols-2 gap-x-3 gap-y-0.5 text-[10px]">
                <div className="text-gray-500">Biome</div>
                <div className="text-white font-medium">{biomeProfile?.biome?.name || context.biome}</div>
                <div className="text-gray-500">Province</div>
                <div className="text-white font-medium uppercase">{context.province}</div>
                <div className="text-gray-500">Regime faunique</div>
                <div className="text-white font-medium">{context.wildlife_regime}</div>
                <div className="text-gray-500">Neige</div>
                <div className="text-white font-medium">{context.snow_regime}</div>
                <div className="text-gray-500">Foret</div>
                <div className="text-white font-medium">{context.forest_regime}</div>
              </div>
            </div>
          )}

          {/* Compute time */}
          <div className="flex items-center justify-between text-[8px] text-gray-600 border-t border-gray-800/50 pt-1.5">
            <span>V8-NATIONAL | {scoreV8.dataVersion}</span>
            <span>{scoreV8.compute_ms}ms</span>
          </div>
        </div>
      )}
    </div>
  );
};

export default ScoreV8Badge;

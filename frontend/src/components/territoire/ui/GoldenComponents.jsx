/**
 * STANDARD GOLDEN — Composants UI Universels BCE-4X STEEVE-MAX
 * =============================================================
 * Source unique de vérité pour TOUS les modules HUNTIQ-V6.
 * Norme: ZERO bordure | Accent bar gauche | Icônes en cercles colorés
 * Hiérarchie: Valeurs 30-40px | Labels 14px | Corps 16px
 * Coins: rounded-xl (12-16px) | Contraste: fond #0F172A / carte #1E293B
 */
import React, { useState } from 'react';
import { ChevronDown, ChevronUp } from 'lucide-react';

export const GOLDEN = {
  cardBg: '#1E293B',
  pageBg: '#0F172A',
  shadow: '0 2px 8px rgba(0,0,0,0.25)',
};

export const BIONIC_COLORS = {
  green: '#00C853', yellow: '#F9D423', orange: '#FF9800', red: '#D32F2F',
  blue: '#2196F3', purple: '#9C27B0', amber: '#FFB300', cyan: '#00BCD4',
  teal: '#009688',
};

export const GoldenCard = ({ children, testId, accentColor, className = '', compact = false }) => (
  <div className={`rounded-xl ${compact ? 'px-3 py-2.5' : 'px-5 py-4'} ${className}`}
    style={{
      backgroundColor: GOLDEN.cardBg,
      boxShadow: GOLDEN.shadow,
      borderLeft: accentColor ? `4px solid ${accentColor}` : 'none',
    }}
    data-testid={testId}>
    {children}
  </div>
);

export const GoldenCollapsible = ({ icon: Icon, title, color, badge, children, defaultOpen = true, testId, compact = false }) => {
  const [open, setOpen] = useState(defaultOpen);
  return (
    <div className={`rounded-xl ${compact ? 'px-3 py-2' : 'px-5 py-3'}`} style={{ backgroundColor: GOLDEN.cardBg, boxShadow: GOLDEN.shadow }} data-testid={testId}>
      <button onClick={() => setOpen(v => !v)} className="w-full flex items-center justify-between cursor-pointer">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-full flex items-center justify-center" style={{ backgroundColor: `${color}20` }}>
            <Icon className="h-4 w-4" style={{ color }} />
          </div>
          <span className="text-[16px] font-bold text-white">{title}</span>
        </div>
        <div className="flex items-center gap-2">
          {badge && <span className="text-[14px] font-semibold px-2.5 py-0.5 rounded-lg" style={{ backgroundColor: `${color}18`, color }}>{badge}</span>}
          {open ? <ChevronUp className="h-4 w-4 text-slate-500" /> : <ChevronDown className="h-4 w-4 text-slate-500" />}
        </div>
      </button>
      {open && <div className="mt-3">{children}</div>}
    </div>
  );
};

export const IconCircle = ({ Icon, color, size = 32 }) => (
  <div className="rounded-full flex items-center justify-center flex-shrink-0" style={{ width: size, height: size, backgroundColor: `${color}20` }}>
    <Icon style={{ color, width: size * 0.5, height: size * 0.5 }} />
  </div>
);

export const GoldenMiniBar = ({ value, max = 100, color, height = 6 }) => (
  <div className="flex-1 rounded-full overflow-hidden" style={{ height, backgroundColor: 'rgba(255,255,255,0.06)' }}>
    <div className="h-full rounded-full" style={{ width: `${Math.min((value / max) * 100, 100)}%`, backgroundColor: color }} />
  </div>
);

export const GoldenDataRow = ({ label, value, color = 'white', compact = false }) => (
  <div className={`flex justify-between ${compact ? 'py-0.5' : 'py-1'}`}>
    <span className="text-[14px] text-slate-400">{label}</span>
    <span className="text-[16px] font-semibold" style={{ color }}>{value || '—'}</span>
  </div>
);

export const GoldenBadge = ({ text, color }) => (
  <span className="text-[14px] font-bold px-2.5 py-0.5 rounded-lg" style={{ backgroundColor: `${color}20`, color }}>{text}</span>
);

export const GoldenScoreBox = ({ score, color, size = 56 }) => (
  <div className="rounded-xl flex items-center justify-center flex-shrink-0"
    style={{ width: size, height: size, background: `linear-gradient(135deg, ${color}30, ${color}10)` }}>
    <span className="text-[32px] font-black tabular-nums" style={{ color }}>{score}</span>
  </div>
);

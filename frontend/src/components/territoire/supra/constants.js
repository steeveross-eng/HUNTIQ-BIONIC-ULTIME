/**
 * SUPRA v2 — Constantes et Composants GOLDEN
 * ============================================
 * Source unique pour BIONIC, GOLDEN, GaugeMini, GoldenCard,
 * GoldenCollapsible, SupraButton, TABS, helpers.
 *
 * BCE-4X / STEEVE-MAX V6 — PHASE P0
 * AUCUNE MODIFICATION SANS AUTORISATION COMMANDANT
 */
import React, { useState } from 'react';
import { ChevronUp, ChevronDown, FlaskConical, ClipboardList, BarChart3, Scale, ShoppingCart } from 'lucide-react';

export const API = process.env.REACT_APP_BACKEND_URL;

export const SUPRA_CMD_COLOR = '#FF9800';

export const BIONIC = {
  green: '#00C853', yellow: '#F9D423', orange: '#FF9800', red: '#D32F2F',
  blue: '#2196F3', purple: '#9C27B0', card: '#111122', cardBorder: 'rgba(255,255,255,0.06)',
  supraCmd: SUPRA_CMD_COLOR, amber: '#FFB300', cyan: '#00BCD4', teal: '#009688',
};

export function gradeColor(grade) {
  if (grade === 'EXCELLENT') return BIONIC.green;
  if (grade === 'BON') return BIONIC.yellow;
  if (grade === 'MODERE') return BIONIC.orange;
  return BIONIC.red;
}
export function zoneColor(z) { return z === 'vert' ? BIONIC.green : z === 'jaune' ? BIONIC.orange : BIONIC.red; }
export function priorityColor(p) { return p === 'CRITIQUE' ? BIONIC.red : p === 'RECOMMANDE' ? BIONIC.orange : BIONIC.green; }

// === SESSION SALINE (Panier Stripe unifie — BCE-4X E03 fix) ===
export const getSalineSession = () => {
  let sid = localStorage.getItem('saline_session_id');
  if (!sid || !/^sal_[a-z0-9]{8,16}$/.test(sid)) {
    sid = 'sal_' + Math.random().toString(36).substr(2, 12);
    localStorage.setItem('saline_session_id', sid);
  }
  return sid;
};

// === GAUGE MINI — Dashboard-style compact (BCE-4X GOLDEN) ===
export const GaugeMini = ({ value, max = 100, label, color = BIONIC.orange }) => {
  const radius = 36;
  const circumference = 2 * Math.PI * radius;
  const pct = Math.min(value / max, 1);
  const offset = circumference * (1 - pct * 0.75);
  return (
    <div className="relative flex flex-col items-center" data-testid="supra-gauge">
      <svg viewBox="0 0 84 84" className="w-[64px] h-[64px]">
        <circle cx="42" cy="42" r={radius} fill="none" stroke="rgba(255,255,255,0.06)" strokeWidth="6"
          strokeDasharray={`${circumference * 0.75} ${circumference * 0.25}`} strokeLinecap="round"
          transform="rotate(135 42 42)" />
        <circle cx="42" cy="42" r={radius} fill="none" stroke={color} strokeWidth="6"
          strokeDasharray={`${circumference * 0.75} ${circumference * 0.25}`} strokeDashoffset={offset}
          strokeLinecap="round" transform="rotate(135 42 42)" style={{ transition: 'stroke-dashoffset 0.8s ease' }} />
        <text x="42" y="40" textAnchor="middle" fill={color} fontSize="18" fontWeight="900" fontFamily="system-ui">{Math.round(value)}</text>
        <text x="42" y="54" textAnchor="middle" fill="#6b7280" fontSize="8" fontWeight="600" fontFamily="system-ui">{label}</text>
      </svg>
    </div>
  );
};

// === NARRATION DATA (from SUPRA PREMIUM) ===
export const PHYSIOLOGY_DATA = {
  chevreuil: {
    printemps: "Sortie d'hiver. Les reserves minerales sont au plus bas. Le sodium est le premier mineral recherche activement. Le calcium et le phosphore sont critiques pour la regeneration du panache.",
    ete: "Phase de croissance maximale du panache. Besoins en calcium et phosphore x3. Le magnesium soutient la fixation. L'appetit mineral est a son pic.",
    pre_rut: "Transition hormonale. Le testosterone monte. Les mineraux de structure (Ca, P) sont fixes. Le sodium maintient l'hydratation sous effort territorial.",
    rut: "Activite maximale. Perte de poids de 20-30%. Le sodium compense la deshydratation. Le potassium soutient la fonction musculaire.",
    post_rut: "Recuperation energetique. Les besoins en mineraux de structure baissent. L'appetit mineral reprend progressivement.",
    hiver: "Phase de survie. Metabolisme ralenti. Les besoins sont minimaux mais le sodium reste recherche.",
  },
  orignal: {
    printemps: "Sortie d'hivernage. Deficience severe en sodium apres 5 mois de regime ligneux. Les femelles gestantes ont des besoins en calcium x4.",
    ete: "Panache en velours. Croissance rapide necessitant calcium, phosphore et magnesium. L'orignal consomme activement les plantes aquatiques riches en sodium.",
    rut: "Activite territoriale intense. Pertes hydriques majeures. Le sodium est vital pour maintenir la pression osmotique.",
    hiver: "Metabolisme hivernal. Besoins reduits. Alimentation a base de ramilles.",
  },
};

export const MALE_BEHAVIOR = {
  chevreuil: {
    printemps: "Les males visitent les salines 2-4 fois/semaine. Visites matinales (5h-8h) et crepusculaires (18h-21h). Duree moyenne: 8-15 min.",
    ete: "Frequence maximale: 4-7 visites/semaine. Duree prolongee (15-25 min). Marquage territorial frequent autour du site.",
    pre_rut: "Visites irregulieres. Les males commencent a patrouiller. Les frottoirs apparaissent dans un rayon de 200m des salines actives.",
    rut: "Visites rares (1-2/semaine). Durees courtes (<5 min). Les males suivent les femelles qui elles, continuent de visiter.",
    post_rut: "Reprise progressive. 2-3 visites/semaine. Comportement moins territorial.",
    hiver: "Visites sporadiques selon meteo. 1-2/semaine max.",
  },
};

export const SUPPORT_HIERARCHY = [
  { name: 'Bois mou (epinette, sapin)', score: 95, color: BIONIC.green, desc: 'Absorption maximale, retention longue, cout reduit.' },
  { name: 'Bois dur (erable, bouleau)', score: 70, color: BIONIC.yellow, desc: 'Absorption moderee, dissolution plus rapide.' },
  { name: 'Sol nu / terre', score: 45, color: BIONIC.orange, desc: 'Dispersion rapide, contamination possible.' },
  { name: 'Bloc mineral commercial', score: 60, color: BIONIC.yellow, desc: 'Pratique mais dissolution non controlee.' },
];

// ============================================================================
// STANDARD GOLDEN — COMPOSANTS UI BCE-4X STEEVE-MAX
// Norme: ZERO bordure visible | Accent bar gauche | Icones en cercles
// Hierarchie: Valeurs 30-40px | Labels 14px | Corps 16px
// Coins: rounded-xl (12-16px) | Contraste: fond #0F172A / carte #1E293B
// Box-shadow: leger GOLDEN | Structure: 100% VERTICALE
// ============================================================================

export const GOLDEN = {
  cardBg: '#1E293B',
  pageBg: '#0F172A',
  shadow: '0 2px 8px rgba(0,0,0,0.25)',
};

export const GoldenCard = ({ children, testId, accentColor, className = '', compact = false }) => (
  <div className={`rounded-lg ${compact ? 'px-2.5 py-2' : 'px-4 py-3'} ${className}`}
    style={{
      backgroundColor: GOLDEN.cardBg,
      boxShadow: GOLDEN.shadow,
      borderLeft: accentColor ? `3px solid ${accentColor}` : 'none',
    }}
    data-testid={testId}>
    {children}
  </div>
);

export const GoldenCollapsible = ({ icon: Icon, title, color, badge, children, defaultOpen = true, testId }) => {
  const [open, setOpen] = useState(defaultOpen);
  return (
    <div className="rounded-lg px-4 py-2.5" style={{ backgroundColor: GOLDEN.cardBg, boxShadow: GOLDEN.shadow }} data-testid={testId}>
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

export const SupraButton = ({ children, onClick, size = 'md', disabled = false, testId }) => {
  const sizeClasses = { sm: 'h-8 px-3 text-xs gap-1.5', md: 'h-9 px-5 text-sm gap-2', lg: 'h-10 px-6 text-sm gap-2' };
  return (
    <button onClick={onClick} disabled={disabled}
      className={`flex items-center justify-center rounded-lg font-bold uppercase tracking-wider transition-all duration-150 ${sizeClasses[size]} ${disabled ? 'opacity-40 cursor-not-allowed' : 'hover:brightness-125 active:scale-[0.97]'}`}
      style={{ backgroundColor: disabled ? '#37415115' : `${SUPRA_CMD_COLOR}18`, color: disabled ? '#6b7280' : SUPRA_CMD_COLOR, border: `2px solid ${disabled ? '#37415130' : `${SUPRA_CMD_COLOR}50`}` }}
      data-testid={testId} data-bce4x-locked="true">
      {children}
    </button>
  );
};

export const TABS = [
  { id: 'analyse', label: 'Analyse', icon: FlaskConical },
  { id: 'fiche', label: 'Fiche', icon: ClipboardList },
  { id: 'intelligence', label: 'Intelligence', icon: BarChart3 },
  { id: 'comparez', label: 'Comparez', icon: Scale },
  { id: 'commandez', label: 'Commandez', icon: ShoppingCart },
];

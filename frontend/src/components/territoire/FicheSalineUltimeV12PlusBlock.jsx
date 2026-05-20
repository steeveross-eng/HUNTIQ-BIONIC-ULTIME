/**
 * FicheSalineUltimeV12PlusBlock — Rendu doctrinal 10 blocs V12-SUPRA+ Ω
 * ═════════════════════════════════════════════════════════════════════════
 * P22ΩΩ_NUTRITION_V12_SUPRA_PLUS_Ω · STEEVE-MAX · BCE-4X ULTIME ABSOLU
 *
 * Affiche la "FICHE SALINE ULTIME" générée par le backend V12-SUPRA+.
 * Additif : s'insère dans NutritionPanelOmega au-dessus des 11 sections legacy.
 *
 * Trigger amont : clic/dblclick sur saline suggérée pour espèce active.
 */
import React, { useState } from 'react';
import {
  ClipboardList, Wheat, ShieldAlert, FlaskConical, Target, Calendar,
  Award, Compass, MapPin, ChevronDown, ChevronRight,
} from 'lucide-react';

const ORANGE = '#FF8F00';
const CYAN = '#00BCD4';
const GREEN = '#22c55e';
const BORDER = '#1a1a2e';
const DARK = 'rgba(13,13,20,0.65)';

const BLOCS = [
  { key: '1_identite_site', label: 'Identité du site', icon: MapPin, color: CYAN },
  { key: '2_profil_biologique', label: 'Profil biologique', icon: Award, color: GREEN },
  { key: '3_habitat_terrain', label: 'Habitat & terrain', icon: Compass, color: '#a855f7' },
  { key: '4_besoins_journaliers', label: 'Besoins journaliers', icon: Wheat, color: '#f59e0b' },
  { key: '5_deficits_pct', label: 'Déficits (%)', icon: ShieldAlert, color: '#ef4444' },
  { key: '6_recettes_automatiques', label: 'Recettes automatiques', icon: FlaskConical, color: ORANGE },
  { key: '7_champs_nourriciers', label: 'Champs nourriciers', icon: Wheat, color: '#22c55e' },
  { key: '8_strategie_chasse', label: 'Stratégie chasse', icon: Target, color: '#3b82f6' },
  { key: '9_plan_30_jours', label: 'Plan 30 jours', icon: Calendar, color: '#06b6d4' },
  { key: '10_synthese_finale', label: 'Synthèse finale', icon: ClipboardList, color: '#f5a623' },
];

function fmtKey(k) {
  return String(k).replace(/^_+/, '').replace(/_/g, ' ');
}

function renderScalar(v) {
  if (v == null) return <span style={{ color: '#6b7280' }}>—</span>;
  if (typeof v === 'number') return <span style={{ color: '#e8e8f0' }}>{Number.isInteger(v) ? v : v.toFixed(2)}</span>;
  if (typeof v === 'boolean') return <span style={{ color: v ? GREEN : '#E57373' }}>{v ? 'OUI' : 'NON'}</span>;
  return <span style={{ color: '#e8e8f0' }}>{String(v)}</span>;
}

function renderValue(v, depth = 0) {
  if (Array.isArray(v)) {
    return (
      <div style={{ paddingLeft: depth ? 8 : 0 }}>
        {v.map((it, i) => (
          <div key={i} style={{ fontSize: 10, padding: '2px 0', display: 'flex', gap: 6 }}>
            <span style={{ color: '#9aa0a6', minWidth: 14 }}>{i + 1}.</span>
            <span style={{ color: '#e8e8f0', flex: 1 }}>
              {typeof it === 'object' && it !== null ? (
                <div style={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                  {Object.entries(it).map(([kk, vv]) => (
                    <div key={kk} style={{ display: 'flex', gap: 6 }}>
                      <span style={{ color: ORANGE, minWidth: 90, textTransform: 'uppercase', fontSize: 9 }}>{fmtKey(kk)}</span>
                      <span style={{ color: '#e8e8f0', flex: 1 }}>
                        {Array.isArray(vv) ? vv.join(' · ') : typeof vv === 'object' ? JSON.stringify(vv) : String(vv)}
                      </span>
                    </div>
                  ))}
                </div>
              ) : (
                String(it)
              )}
            </span>
          </div>
        ))}
      </div>
    );
  }
  if (v && typeof v === 'object') {
    return (
      <div style={{ paddingLeft: depth ? 8 : 0 }}>
        {Object.entries(v).map(([k, val]) => {
          if (k.startsWith('_')) return null; // skip meta keys
          return (
            <div key={k} style={{ fontSize: 10, padding: '2px 0', display: 'flex', gap: 6 }}>
              <span style={{ color: '#9aa0a6', minWidth: 110 }}>{fmtKey(k)}</span>
              <span style={{ color: '#e8e8f0', flex: 1 }}>
                {Array.isArray(val) ? val.join(' · ')
                  : (val && typeof val === 'object') ? renderValue(val, depth + 1)
                  : renderScalar(val)}
              </span>
            </div>
          );
        })}
      </div>
    );
  }
  return renderScalar(v);
}

export function FicheSalineUltimeV12PlusBlock({ data, loading, error, enCours, defaultOpen = true }) {
  const [open, setOpen] = useState(defaultOpen);
  const [expanded, setExpanded] = useState({
    '6_recettes_automatiques': true, // bloc clef ouvert par défaut
    '10_synthese_finale': true,
  });

  // STATES Ω
  if (!data && !loading && !error) return null;

  return (
    <div
      data-testid="fiche-saline-ultime-v12plus-block"
      style={{
        margin: '8px 0',
        border: `1px solid ${ORANGE}`,
        borderRadius: 6,
        background: 'linear-gradient(180deg, rgba(255,143,0,0.08) 0%, rgba(13,13,20,0.85) 100%)',
        overflow: 'hidden',
      }}
    >
      {/* HEADER COLLAPSIBLE */}
      <button
        type="button"
        onClick={() => setOpen(!open)}
        data-testid="fiche-v12plus-toggle"
        style={{
          width: '100%', padding: '8px 12px',
          background: `${ORANGE}18`,
          border: 'none',
          color: ORANGE,
          fontSize: 10,
          fontWeight: 900,
          letterSpacing: 1.1,
          textAlign: 'left',
          cursor: 'pointer',
          display: 'flex', alignItems: 'center', gap: 8,
        }}
      >
        {open ? <ChevronDown size={12} /> : <ChevronRight size={12} />}
        <FlaskConical size={12} />
        FICHE SALINE ULTIME — V12-SUPRA+
        {loading && <span style={{ marginLeft: 'auto', fontSize: 9, color: '#9aa0a6' }}>
          {enCours ? '202 EN_COURS · prewarm Ω…' : 'CALCUL…'}
        </span>}
        {error && <span style={{ marginLeft: 'auto', fontSize: 9, color: '#E57373' }}>ERREUR</span>}
        {data && !loading && !error && (
          <span style={{ marginLeft: 'auto', fontSize: 9, color: GREEN, fontWeight: 800 }}>
            OK · 10 BLOCS
          </span>
        )}
      </button>

      {open && (
        <div style={{ padding: '6px 0' }}>
          {/* LOADING */}
          {loading && !data && (
            <div data-testid="fiche-v12plus-loading" style={{ padding: 14, fontSize: 10, color: '#9aa0a6' }}>
              {enCours
                ? 'NEVER BLANK Ω · backend en pré-chauffe (202 EN_COURS) — affichage dès complétion.'
                : 'Calcul V12-SUPRA+ en cours…'}
            </div>
          )}

          {/* ERROR */}
          {error && !data && (
            <div data-testid="fiche-v12plus-error" style={{
              margin: 10, padding: 10,
              background: '#E5737322', border: '1px solid #E5737366', borderRadius: 4,
              fontSize: 10, color: '#e8e8f0',
            }}>
              <div style={{ fontWeight: 800, color: '#E57373', letterSpacing: 1 }}>V12-SUPRA+ INDISPONIBLE</div>
              <div style={{ marginTop: 4, color: '#9aa0a6' }}>Motif : {error}</div>
            </div>
          )}

          {/* DATA — 10 BLOCS DOCTRINAUX */}
          {data && (
            <div>
              {/* META BANDEAU */}
              <div style={{
                padding: '6px 12px',
                background: DARK,
                borderBottom: `1px solid ${BORDER}`,
                display: 'flex', flexWrap: 'wrap', gap: 8,
                fontSize: 9, color: '#9aa0a6',
              }}>
                <span><span style={{ color: ORANGE, fontWeight: 700 }}>Engine</span> {data._engine}</span>
                <span><span style={{ color: ORANGE, fontWeight: 700 }}>Ver</span> {data._version}</span>
                <span><span style={{ color: ORANGE, fontWeight: 700 }}>Tables</span> {data._tables_version}</span>
                <span style={{ marginLeft: 'auto' }}>
                  <span style={{ color: GREEN, fontWeight: 800 }}>VERROU III · {data._phase_iii_lock}</span>
                </span>
              </div>

              {BLOCS.map(({ key, label, icon: Icon, color }) => {
                const section = data[key];
                if (!section) return null;
                const isOpen = expanded[key] !== false;
                return (
                  <div
                    key={key}
                    data-testid={`fiche-v12plus-bloc-${key}`}
                    style={{ borderBottom: `1px solid ${BORDER}` }}
                  >
                    <button
                      type="button"
                      onClick={() => setExpanded((p) => ({ ...p, [key]: !isOpen }))}
                      data-testid={`fiche-v12plus-toggle-${key}`}
                      style={{
                        width: '100%', padding: '8px 12px',
                        background: 'transparent', border: 'none',
                        cursor: 'pointer', textAlign: 'left',
                        display: 'flex', alignItems: 'center', gap: 8,
                      }}
                    >
                      {isOpen ? <ChevronDown size={11} color={color} /> : <ChevronRight size={11} color={color} />}
                      <Icon size={12} color={color} />
                      <span style={{
                        fontSize: 10, fontWeight: 800, color, letterSpacing: 0.8,
                        textTransform: 'uppercase',
                      }}>
                        {label}
                      </span>
                    </button>
                    {isOpen && (
                      <div style={{ padding: '0 12px 10px 12px' }}>
                        {renderValue(section)}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default FicheSalineUltimeV12PlusBlock;

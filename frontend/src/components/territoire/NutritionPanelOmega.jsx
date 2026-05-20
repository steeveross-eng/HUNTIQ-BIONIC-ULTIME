/**
 * NutritionPanelOmega — Rapport nutritionnel institutionnel (11 sections)
 * =========================================================================
 * Ordre : `PHASE_NUTRITION_SALINES_BINDING_Ω — INTEGRATED_WITH_FILTERING`
 * Protocole : BCE-4X ULTIME ABSOLU — VERSION_INSTITUTIONNELLE_RENFORCÉE_X10
 *
 * Activé au DOUBLE-CLIC sur une saline de la couche BionicLayersV8.
 * Applique les 4 filtres Ω avant affichage : EXCLUSION/HABITAT/TERRAIN/
 * BIOLOGIE_AWARE_Ω. Si saline rejetée, affiche le motif institutionnel.
 */
import React from 'react';
import { Wheat, ShieldAlert, Activity, Droplets, Calendar, ClipboardList, Package, Repeat, FlaskConical, HeartPulse, Award } from 'lucide-react';
import { FicheSalineUltimeV12PlusBlock } from './FicheSalineUltimeV12PlusBlock';

const ORANGE = '#FF8F00';
const DARK = '#0d0d14';
const BORDER = '#1a1a2e';

const SECTION_META = {
  besoins_journaliers: { label: 'Besoins journaliers', icon: Wheat },
  carences: { label: 'Carences', icon: ShieldAlert },
  mineraux: { label: 'Minéraux', icon: Activity },
  proteines: { label: 'Protéines', icon: Droplets },
  saisonnalite: { label: 'Saisonnalité', icon: Calendar },
  recommandations: { label: 'Recommandations', icon: ClipboardList },
  quantites: { label: 'Quantités', icon: Package },
  frequences: { label: 'Fréquences', icon: Repeat },
  recettes_minerales: { label: 'Recettes minérales', icon: FlaskConical },
  impact_biologique: { label: 'Impact biologique', icon: HeartPulse },
  score_nutritionnel_institutionnel: { label: 'Score nutritionnel Ω', icon: Award },
};

function renderValue(v) {
  if (v == null) return <span style={{ color: '#6b7280' }}>—</span>;
  if (typeof v === 'object') {
    return (
      <div style={{ paddingLeft: 8 }}>
        {Object.entries(v).map(([k, val]) => (
          <div key={k} style={{ fontSize: 10, padding: '2px 0', display: 'flex', gap: 6 }}>
            <span style={{ color: '#9aa0a6', minWidth: 110 }}>{k.replace(/_/g, ' ')}</span>
            <span style={{ color: '#e8e8f0', flex: 1 }}>
              {Array.isArray(val) ? val.join(', ') : typeof val === 'object' ? JSON.stringify(val) : String(val)}
            </span>
          </div>
        ))}
      </div>
    );
  }
  return <span style={{ color: '#e8e8f0' }}>{String(v)}</span>;
}

export function NutritionPanelOmega({ payload, onClose, v12Plus, v12PlusLoading, v12PlusError, v12PlusEnCours }) {
  if (!payload) return null;

  return (
    <div
      data-testid="nutrition-panel-omega"
      style={{
        position: 'absolute',
        top: 60,
        left: 16,
        width: 380,
        maxWidth: 'calc(100vw - 32px)',
        maxHeight: 'calc(100vh - 120px)',
        overflowY: 'auto',
        zIndex: 510,
        background: DARK,
        border: `1px solid ${ORANGE}`,
        borderRadius: 8,
        boxShadow: `0 0 24px ${ORANGE}55, 0 8px 32px rgba(0,0,0,0.6)`,
        fontFamily: 'ui-monospace, SFMono-Regular, Menlo, monospace',
        color: '#e8e8f0',
      }}
    >
      {/* HEADER */}
      <div style={{
        padding: '12px 14px',
        borderBottom: `1px solid ${BORDER}`,
        background: `linear-gradient(90deg, ${ORANGE}22 0%, transparent 100%)`,
        display: 'flex', alignItems: 'center', gap: 10,
      }}>
        <Wheat size={18} color={ORANGE} />
        <div style={{ flex: 1 }}>
          <div style={{ fontSize: 11, fontWeight: 800, letterSpacing: 1.2, color: ORANGE }}>
            NUTRITION_PANEL_Ω
          </div>
          <div style={{ fontSize: 9, color: '#9aa0a6', letterSpacing: 0.8 }}>
            BCE-4X — {payload.protocol || 'VERSION_INSTITUTIONNELLE_RENFORCÉE_X10'}
          </div>
        </div>
        <button
          onClick={onClose}
          data-testid="nutrition-panel-close-btn"
          style={{ background: 'transparent', border: 'none', color: '#9aa0a6', cursor: 'pointer', fontSize: 16 }}
        >×</button>
      </div>

      {/* REJET CAS */}
      {!payload.ok && (
        <div data-testid="nutrition-panel-rejected" style={{ padding: 14 }}>
          <div style={{
            background: '#E5737322', border: '1px solid #E5737366',
            borderRadius: 4, padding: 10,
          }}>
            <div style={{ fontSize: 10, fontWeight: 800, color: '#E57373', letterSpacing: 1 }}>
              ANALYSE REJETÉE PAR FILTRE Ω
            </div>
            <div style={{ fontSize: 10, marginTop: 6, color: '#e8e8f0' }}>
              Filtre : <span style={{ color: ORANGE, fontWeight: 700 }}>{payload.filter || 'n/a'}</span>
            </div>
            <div style={{ fontSize: 10, marginTop: 4, color: '#9aa0a6' }}>
              Motif : {payload.reason}
            </div>
          </div>
          <div style={{ fontSize: 9, marginTop: 10, color: '#9aa0a6' }}>
            Conformément au protocole ENFORCE_URBAN_EXCLUSION, aucune analyse
            nutritionnelle ne peut être produite pour cette saline.
          </div>
        </div>
      )}

      {/* SALINE INFO */}
      {payload.ok && payload.saline && (
        <div style={{ padding: '10px 14px', borderBottom: `1px solid ${BORDER}` }}>
          <div style={{ fontSize: 9, color: '#9aa0a6', letterSpacing: 1 }}>SALINE</div>
          <div style={{ fontSize: 11, fontWeight: 700, color: ORANGE, marginTop: 2 }}>
            {payload.saline.id || 'saline sans id'}
          </div>
          <div style={{ fontSize: 9, color: '#9aa0a6', marginTop: 2 }}>
            {typeof payload.saline.lat === 'number' ? payload.saline.lat.toFixed(5) : '—'} ·
            {' '}
            {typeof payload.saline.lng === 'number' ? payload.saline.lng.toFixed(5) : '—'}
            {payload.saline.status && <> · {payload.saline.status}</>}
          </div>
          <div style={{ fontSize: 9, color: '#9aa0a6', marginTop: 2 }}>
            Espèce : <span style={{ color: '#e8e8f0', textTransform: 'uppercase' }}>{payload.species}</span>
            {' '}· Mois : {payload.month}
          </div>
        </div>
      )}

      {/* FICHE SALINE ULTIME — V12-SUPRA+ (additif) */}
      {payload.ok && (v12Plus || v12PlusLoading || v12PlusError) && (
        <div data-testid="nutrition-panel-v12plus-slot" style={{ padding: '0 10px' }}>
          <FicheSalineUltimeV12PlusBlock
            data={v12Plus}
            loading={!!v12PlusLoading}
            error={v12PlusError}
            enCours={!!v12PlusEnCours}
          />
        </div>
      )}

      {/* 11 SECTIONS */}
      {payload.ok && payload.report && (
        <div style={{ padding: '6px 0' }}>
          {Object.entries(SECTION_META).map(([key, meta]) => {
            const Icon = meta.icon;
            const section = payload.report[key];
            return (
              <div
                key={key}
                data-testid={`nutrition-section-${key}`}
                style={{
                  padding: '10px 14px',
                  borderBottom: `1px solid ${BORDER}`,
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
                  <Icon size={12} color={ORANGE} />
                  <div style={{ fontSize: 10, fontWeight: 800, color: ORANGE, letterSpacing: 0.8, textTransform: 'uppercase' }}>
                    {meta.label}
                  </div>
                </div>
                {renderValue(section)}
              </div>
            );
          })}
        </div>
      )}

      {/* GARDE */}
      <div style={{ padding: '8px 14px', background: `${ORANGE}11`, fontSize: 9, color: '#9aa0a6' }}>
        NUTRITION_BY_SALINE_ONLY · <span style={{ color: ORANGE, fontWeight: 800 }}>ACTIF</span>
        {' '}· Filtres Ω pré-validation appliqués
      </div>
    </div>
  );
}

export default NutritionPanelOmega;

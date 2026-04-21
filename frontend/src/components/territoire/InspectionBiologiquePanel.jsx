/**
 * InspectionBiologiquePanel — Panneau d'activation MODE INSPECTION BIOLOGIQUE PRO/EXPERT
 * =========================================================================================
 * Commande : `ACTIVER MODE INSPECTION BIOLOGIQUE PRO/EXPERT`
 * Protocole : BCE-4X ULTIME ABSOLU — VERSION_INSTITUTIONNELLE_RENFORCÉE_X10
 *
 * Contrat strict :
 *   - Frontend only, zéro appel backend
 *   - Zéro fallback visuel non institutionnel
 *   - Rôles : 'pro' | 'expert'
 *   - Couches ATTRACTEURS / EXCLUSIONS / PENTES / COUVERT
 *   - Synchronisation TERRAIN_AWARE_Ω + BIOLOGIE_AWARE_Ω
 */
import React, { useMemo, useState, useEffect } from 'react';
import { Microscope, Eye, EyeOff, ShieldCheck, AlertTriangle } from 'lucide-react';
import {
  enableInspectionBiologiqueMode,
  disableInspectionBiologiqueMode,
  getInspectionBiologiqueStatus,
  INSPECTION_BIO_SPEC,
  OMEGA_FILTERS_SPEC,
} from '@/lib/renduOmegaStore';

const INSTITUTIONAL_ORANGE = '#FF8F00';
const INSTITUTIONAL_DARK = '#0d0d14';
const INSTITUTIONAL_BORDER = '#1a1a2e';

export function InspectionBiologiquePanel({ open, onClose }) {
  const [tick, setTick] = useState(0);
  const [lastAction, setLastAction] = useState(null);

  // Refresh state à chaque ouverture / action
  useEffect(() => { if (open) setTick(t => t + 1); }, [open]);

  // eslint-disable-next-line react-hooks/exhaustive-deps
  const status = useMemo(() => getInspectionBiologiqueStatus(), [tick]);

  const activate = (role) => {
    const res = enableInspectionBiologiqueMode(role);
    setLastAction({ type: 'activate', role, res });
    setTick(t => t + 1);
  };

  const deactivate = () => {
    const res = disableInspectionBiologiqueMode();
    setLastAction({ type: 'deactivate', res });
    setTick(t => t + 1);
  };

  if (!open) return null;

  return (
    <div
      data-testid="inspection-bio-panel"
      style={{
        position: 'absolute',
        top: 60,
        right: 16,
        width: 360,
        maxWidth: 'calc(100vw - 32px)',
        maxHeight: 'calc(100vh - 120px)',
        overflowY: 'auto',
        zIndex: 500,
        background: INSTITUTIONAL_DARK,
        border: `1px solid ${INSTITUTIONAL_ORANGE}`,
        borderRadius: 8,
        boxShadow: `0 0 24px ${INSTITUTIONAL_ORANGE}55, 0 8px 32px rgba(0,0,0,0.6)`,
        fontFamily: 'ui-monospace, SFMono-Regular, Menlo, monospace',
        color: '#e8e8f0',
      }}
    >
      {/* HEADER */}
      <div style={{
        display: 'flex', alignItems: 'center', gap: 10,
        padding: '12px 14px',
        borderBottom: `1px solid ${INSTITUTIONAL_BORDER}`,
        background: `linear-gradient(90deg, ${INSTITUTIONAL_ORANGE}22 0%, transparent 100%)`,
      }}>
        <Microscope size={18} color={INSTITUTIONAL_ORANGE} />
        <div style={{ flex: 1 }}>
          <div style={{ fontSize: 11, fontWeight: 800, letterSpacing: 1.2, color: INSTITUTIONAL_ORANGE }}>
            MODE INSPECTION BIOLOGIQUE
          </div>
          <div style={{ fontSize: 9, letterSpacing: 0.8, color: '#9aa0a6', marginTop: 2 }}>
            BCE-4X — {INSPECTION_BIO_SPEC.protocolVersion}
          </div>
        </div>
        <button
          onClick={onClose}
          data-testid="inspection-bio-close-btn"
          title="Fermer"
          style={{
            background: 'transparent', border: 'none', color: '#9aa0a6',
            cursor: 'pointer', fontSize: 16, lineHeight: 1,
          }}
        >×</button>
      </div>

      {/* STATUS */}
      <div style={{ padding: '12px 14px', borderBottom: `1px solid ${INSTITUTIONAL_BORDER}` }}>
        <div style={{ fontSize: 9, letterSpacing: 1, color: '#9aa0a6', marginBottom: 6 }}>STATUT</div>
        {status.enabled ? (
          <div data-testid="inspection-bio-status-active" style={{
            display: 'flex', alignItems: 'center', gap: 8,
            padding: '8px 10px', borderRadius: 4,
            background: `${INSTITUTIONAL_ORANGE}22`,
            border: `1px solid ${INSTITUTIONAL_ORANGE}55`,
          }}>
            <ShieldCheck size={14} color={INSTITUTIONAL_ORANGE} />
            <div style={{ flex: 1, fontSize: 10, fontWeight: 700 }}>
              ACTIVÉ — Rôle : <span style={{ color: INSTITUTIONAL_ORANGE, textTransform: 'uppercase' }}>{status.role}</span>
            </div>
          </div>
        ) : (
          <div data-testid="inspection-bio-status-inactive" style={{
            display: 'flex', alignItems: 'center', gap: 8,
            padding: '8px 10px', borderRadius: 4,
            background: '#1a1a2e',
            border: `1px solid ${INSTITUTIONAL_BORDER}`,
          }}>
            <EyeOff size={14} color="#6b7280" />
            <div style={{ flex: 1, fontSize: 10, fontWeight: 700, color: '#9aa0a6' }}>DÉSACTIVÉ</div>
          </div>
        )}
      </div>

      {/* ACTIONS ROLE */}
      <div style={{ padding: '12px 14px', borderBottom: `1px solid ${INSTITUTIONAL_BORDER}` }}>
        <div style={{ fontSize: 9, letterSpacing: 1, color: '#9aa0a6', marginBottom: 8 }}>ACTIVATION</div>
        <div style={{ display: 'flex', gap: 8 }}>
          <button
            data-testid="inspection-bio-pro-btn"
            onClick={() => activate('pro')}
            disabled={status.enabled && status.role === 'pro'}
            style={{
              flex: 1, padding: '10px 8px', borderRadius: 4,
              fontSize: 10, fontWeight: 800, letterSpacing: 1.1, textTransform: 'uppercase',
              cursor: (status.enabled && status.role === 'pro') ? 'default' : 'pointer',
              background: (status.enabled && status.role === 'pro')
                ? `${INSTITUTIONAL_ORANGE}`
                : `${INSTITUTIONAL_ORANGE}33`,
              color: (status.enabled && status.role === 'pro') ? '#0d0d14' : INSTITUTIONAL_ORANGE,
              border: `1px solid ${INSTITUTIONAL_ORANGE}`,
              transition: 'all 0.15s ease',
            }}
          >PRO</button>
          <button
            data-testid="inspection-bio-expert-btn"
            onClick={() => activate('expert')}
            disabled={status.enabled && status.role === 'expert'}
            style={{
              flex: 1, padding: '10px 8px', borderRadius: 4,
              fontSize: 10, fontWeight: 800, letterSpacing: 1.1, textTransform: 'uppercase',
              cursor: (status.enabled && status.role === 'expert') ? 'default' : 'pointer',
              background: (status.enabled && status.role === 'expert')
                ? `${INSTITUTIONAL_ORANGE}`
                : `${INSTITUTIONAL_ORANGE}33`,
              color: (status.enabled && status.role === 'expert') ? '#0d0d14' : INSTITUTIONAL_ORANGE,
              border: `1px solid ${INSTITUTIONAL_ORANGE}`,
              transition: 'all 0.15s ease',
            }}
          >EXPERT</button>
          <button
            data-testid="inspection-bio-off-btn"
            onClick={deactivate}
            disabled={!status.enabled}
            style={{
              padding: '10px 10px', borderRadius: 4,
              fontSize: 10, fontWeight: 800, letterSpacing: 1.1,
              cursor: status.enabled ? 'pointer' : 'default',
              background: '#1a1a2e',
              color: status.enabled ? '#e8e8f0' : '#6b7280',
              border: `1px solid ${INSTITUTIONAL_BORDER}`,
            }}
          >OFF</button>
        </div>
      </div>

      {/* OVERLAYS */}
      <div style={{ padding: '12px 14px', borderBottom: `1px solid ${INSTITUTIONAL_BORDER}` }}>
        <div style={{ fontSize: 9, letterSpacing: 1, color: '#9aa0a6', marginBottom: 8 }}>
          COUCHES OVERLAY (strict institutionnel)
        </div>
        {INSPECTION_BIO_SPEC.overlayLayers.map(layer => {
          const visible = status.enabled && status.role && layer.minRolesRequired.includes(status.role);
          return (
            <div
              key={layer.key}
              data-testid={`inspection-bio-layer-${layer.key}`}
              style={{
                display: 'flex', alignItems: 'center', gap: 8,
                padding: '6px 0', fontSize: 10,
                opacity: visible ? 1.0 : 0.45,
              }}
            >
              <div style={{
                width: 14, height: 14, borderRadius: 2,
                background: layer.color || (layer.gradient ? layer.gradient[1].color : INSTITUTIONAL_ORANGE),
                border: `1px solid ${layer.stroke || INSTITUTIONAL_ORANGE}`,
                flexShrink: 0,
              }} />
              <div style={{ flex: 1, fontWeight: 700, letterSpacing: 0.8 }}>{layer.label}</div>
              <div style={{ fontSize: 9, color: '#9aa0a6', letterSpacing: 0.6 }}>
                {layer.minRolesRequired.join('/').toUpperCase()}
              </div>
              {visible ? (
                <Eye size={12} color={INSTITUTIONAL_ORANGE} />
              ) : (
                <EyeOff size={12} color="#6b7280" />
              )}
            </div>
          );
        })}
      </div>

      {/* AWARENESS SYNC */}
      <div style={{ padding: '12px 14px', borderBottom: `1px solid ${INSTITUTIONAL_BORDER}` }}>
        <div style={{ fontSize: 9, letterSpacing: 1, color: '#9aa0a6', marginBottom: 8 }}>
          SYNCHRONISATION AWARENESS
        </div>
        <div data-testid="inspection-bio-terrain-aware" style={{
          fontSize: 10, padding: '4px 0',
          color: status.awareness?.synced ? '#8BC34A' : '#6b7280',
        }}>
          ● TERRAIN_AWARE_Ω — {status.awareness?.synced ? 'SYNC' : 'INACTIF'}
        </div>
        <div data-testid="inspection-bio-biologie-aware" style={{
          fontSize: 10, padding: '4px 0',
          color: status.awareness?.synced ? '#8BC34A' : '#6b7280',
        }}>
          ● BIOLOGIE_AWARE_Ω — {status.awareness?.synced ? 'SYNC' : 'INACTIF'}
        </div>
      </div>

      {/* FILTRES Ω INSTITUTIONNELS */}
      <div style={{ padding: '12px 14px', borderBottom: `1px solid ${INSTITUTIONAL_BORDER}` }}>
        <div style={{ fontSize: 9, letterSpacing: 1, color: '#9aa0a6', marginBottom: 8 }}>
          FILTRES Ω — ENFORCE_URBAN_EXCLUSION
        </div>
        {Object.values(OMEGA_FILTERS_SPEC.filters).map(f => (
          <div
            key={f.id}
            data-testid={`inspection-bio-filter-${f.id}`}
            style={{
              fontSize: 10, padding: '3px 0',
              color: status.enabled ? '#8BC34A' : '#6b7280',
              display: 'flex', alignItems: 'center', gap: 6,
            }}
          >
            <span>●</span>
            <span style={{ flex: 1 }}>{f.id}</span>
            <span style={{ fontSize: 9, color: '#9aa0a6' }}>{status.enabled ? 'ACTIF' : 'INACTIF'}</span>
          </div>
        ))}
      </div>

      {/* FALLBACK GUARD */}
      <div style={{
        padding: '10px 14px',
        background: `${INSTITUTIONAL_ORANGE}11`,
        display: 'flex', alignItems: 'center', gap: 8,
      }}>
        <AlertTriangle size={12} color={INSTITUTIONAL_ORANGE} />
        <div style={{ fontSize: 9, color: '#9aa0a6', lineHeight: 1.4 }}>
          FALLBACK VISUEL NON INSTITUTIONNEL — <span style={{ color: INSTITUTIONAL_ORANGE, fontWeight: 800 }}>INTERDIT</span>
          {lastAction && lastAction.res && !lastAction.res.ok && (
            <div style={{ marginTop: 4, color: '#E57373' }}>
              REJET : {lastAction.res.reason} ({lastAction.role || 'n/a'})
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default InspectionBiologiquePanel;

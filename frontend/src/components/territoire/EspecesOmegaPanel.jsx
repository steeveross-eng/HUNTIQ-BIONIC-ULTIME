/**
 * EspecesOmegaPanel.jsx — PHASE_XII_ESPECES_Ω · BCE-4X ULTIME ABSOLU
 * ════════════════════════════════════════════════════════════════════
 * Commandant STEEVE-MAX
 *
 * Panneau institutionnel affichant les 5 engines espèces Ω :
 *  - CHEVREUIL · ORIGNAL · OURS_NOIR · WAPITI · DINDON_SAUVAGE
 *
 * Chaque espèce affiche :
 *  - Nom scientifique + référence Tableau Maître BCE-4X
 *  - Score pression humaine + fragmentation + seuils thermiques/neige
 *  - Palette institutionnelle (habitat / corridors / critiques)
 *  - Conformité BCE-4X (sources GOV+UNI+PR + DOI)
 *
 * Z-ORDER Ω : nouvelles couches insérées après "zones".
 * ════════════════════════════════════════════════════════════════════
 */
import React, { useEffect, useState } from 'react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

export default function EspecesOmegaPanel() {
  const [data, setData] = useState(null);
  const [signature, setSignature] = useState(null);
  const [auditStatus, setAuditStatus] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;
    const fetchAll = async () => {
      try {
        const [r1, r2, r3] = await Promise.all([
          fetch(`${BACKEND_URL}/api/v30/especes/list?_t=${Date.now()}`,
                { credentials: 'omit', cache: 'no-store' }),
          fetch(`${BACKEND_URL}/api/v30/especes/lock-signature?_t=${Date.now()}`,
                { credentials: 'omit', cache: 'no-store' }),
          fetch(`${BACKEND_URL}/api/v30/especes/audit/status?_t=${Date.now()}`,
                { credentials: 'omit', cache: 'no-store' }),
        ]);
        if (!r1.ok) throw new Error(`list HTTP ${r1.status}`);
        if (!r2.ok) throw new Error(`lock HTTP ${r2.status}`);
        if (!r3.ok) throw new Error(`audit HTTP ${r3.status}`);
        const j1 = await r1.json();
        const j2 = await r2.json();
        const j3 = await r3.json();
        if (!cancelled) {
          setData(j1);
          setSignature(j2);
          setAuditStatus(j3);
        }
      } catch (e) {
        if (!cancelled) setError(String(e && e.message ? e.message : e));
      }
    };
    fetchAll();
    return () => { cancelled = true; };
  }, []);

  if (error) {
    return (
      <div data-testid="especes-omega-panel-error"
        style={{ position: 'absolute', top: 510, left: 12, width: 320,
          background: 'rgba(220,38,38,0.10)', border: '1px solid rgba(220,38,38,0.45)',
          borderRadius: 8, padding: 12, color: '#FCA5A5', fontSize: 11,
          fontFamily: 'system-ui, -apple-system, sans-serif', zIndex: 902 }}>
        ENGINES ESPÈCES Ω — ERREUR : {error}
      </div>
    );
  }

  if (!data || !signature) return null;

  return (
    <div
      data-testid="especes-omega-panel"
      style={{
        position: 'absolute', top: 510, left: 12, width: 360,
        background: 'rgba(10,15,13,0.92)',
        backdropFilter: 'blur(8px)',
        WebkitBackdropFilter: 'blur(8px)',
        border: '1px solid rgba(0,166,118,0.40)',
        borderRadius: 8, padding: '10px 12px', color: '#E5F6EF',
        fontFamily: 'system-ui, -apple-system, sans-serif', fontSize: 11,
        letterSpacing: 0.3, zIndex: 902, maxHeight: 520, overflowY: 'auto',
      }}
    >
      <div data-testid="especes-omega-header"
        style={{ color: '#00A676', fontWeight: 800, fontSize: 12,
                 letterSpacing: 1.5, borderBottom: '1px solid rgba(0,166,118,0.30)',
                 paddingBottom: 4, marginBottom: 8 }}>
        ENGINES ESPÈCES Ω · PHASE XII
        <span style={{ float: 'right', fontSize: 9, color: '#9fb0c2' }}>
          {data.engines_count}/5
        </span>
      </div>

      {/* PHASE_XII_AUDIT (Article 4) — Bandeau verrou conditionnel */}
      {auditStatus && !auditStatus.is_validated && (
        <div
          data-testid="especes-omega-validation-banner"
          style={{
            padding: '8px 10px', marginBottom: 8, borderRadius: 6,
            background: 'rgba(245,158,11,0.10)',
            border: '1px solid #f59e0b', color: '#fbbf24',
            fontSize: 10, lineHeight: 1.4, fontWeight: 700, letterSpacing: 0.5,
          }}
        >
          ⚠️ ENGINES ESPÈCES Ω — EN ATTENTE DE VALIDATION DU COMMANDANT<br />
          <span style={{ fontWeight: 400, color: '#fde68a', fontSize: 9 }}>
            Audit BCE-4X exécuté · 120/120 paramètres ACCEPTÉ · activation_status :
            <code style={{ marginLeft: 4 }}>{auditStatus['AUDIT_ESPECES_Ω_STATUS']}</code>
          </span>
        </div>
      )}
      {auditStatus && auditStatus.is_validated && (
        <div
          data-testid="especes-omega-validation-banner"
          style={{
            padding: '6px 10px', marginBottom: 8, borderRadius: 6,
            background: 'rgba(0,166,118,0.10)',
            border: '1px solid #00A676', color: '#00A676',
            fontSize: 10, fontWeight: 700, letterSpacing: 0.5,
          }}
        >
          ✓ AUDIT_ESPECES_Ω_STATUS = VALIDÉ_PAR_STEEVE_MAX<br />
          <span style={{ fontWeight: 400, color: '#B2F2D9', fontSize: 9 }}>
            Engines ACTIF_Ω_DÉFINITIF · {auditStatus.validated_at_utc?.slice(0, 19)}
          </span>
        </div>
      )}

      {data.engines.map((e) => {
        const pal = e.style_palette || {};
        const color = pal.color_primary || '#00A676';
        const corridor = pal.color_corridor || color;
        const critique = pal.color_critique || color;
        return (
          <div
            key={e.espece_id}
            data-testid={`especes-omega-${e.espece_id.toLowerCase()}`}
            data-bce4x-compliant={e.bce4x_compliant ? '1' : '0'}
            style={{
              padding: '8px 10px', marginBottom: 6, borderRadius: 6,
              background: 'rgba(0,0,0,0.25)',
              borderLeft: `3px solid ${color}`,
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline' }}>
              <b style={{ color: color, fontSize: 12 }}>{e.espece_id}</b>
              <span style={{ fontSize: 9, color: e.bce4x_compliant ? '#00A676' : '#ef4444' }}>
                {e.bce4x_compliant ? '✓ BCE-4X' : '✗ NON CONFORME'}
              </span>
            </div>
            <div style={{ color: '#B2F2D9', fontSize: 10, fontStyle: 'italic', marginTop: 2 }}>
              {e.nom_scientifique}
            </div>
            <div style={{ display: 'flex', gap: 8, marginTop: 4, fontSize: 9, color: '#9fb0c2' }}>
              <span>📚 {e.sources_count} sources</span>
              <span>🔗 {e.doi_count} DOI</span>
              <span>📐 {e.dimensions_count} dim.</span>
              <span>📤 {e.outputs_count} couches</span>
            </div>
            <div style={{ display: 'flex', gap: 4, marginTop: 4 }}>
              {e.sources_types.map((t) => (
                <span key={t} style={{ fontSize: 8, padding: '1px 5px', borderRadius: 2,
                  background: 'rgba(0,166,118,0.15)', color: '#B2F2D9',
                  border: '1px solid rgba(0,166,118,0.35)' }}>
                  {t}
                </span>
              ))}
            </div>
            {/* Mini palette institutionnelle */}
            <div style={{ display: 'flex', gap: 3, marginTop: 5, fontSize: 8, alignItems: 'center' }}>
              <span style={{ color: '#9fb0c2' }}>palette:</span>
              <span style={{ width: 10, height: 10, background: color, borderRadius: 2 }} title="habitat" />
              <span style={{ width: 10, height: 10, background: corridor, borderRadius: 2 }} title="corridor" />
              <span style={{ width: 10, height: 10, background: critique, borderRadius: 2 }} title="critique" />
              <span style={{ marginLeft: 6, color: '#6b9c87' }}>{e.engine_marker}</span>
            </div>
          </div>
        );
      })}

      <div data-testid="especes-omega-signature"
        style={{ marginTop: 6, padding: 6, fontSize: 9, color: '#6b9c87',
                 borderTop: '1px dashed rgba(0,166,118,0.30)' }}>
        SHA-256 · {signature.SHA_REGISTRY_LOCK_ESPECES_Ω.slice(0, 16)}…<br />
        {signature.VERSION_ESPECES_Ω} · CONFORMITÉ BCE-4X {signature.CONFORMITE_BCE4X_ESPECES_Ω}%
      </div>
    </div>
  );
}

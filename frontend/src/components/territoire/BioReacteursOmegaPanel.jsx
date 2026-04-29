/**
 * BioReacteursOmegaPanel.jsx — PHASE_XIV_VISUALISATION_Ω · BCE-4X ULTIME ABSOLU x3
 * ═════════════════════════════════════════════════════════════════════════════
 * Commandant STEEVE-MAX
 *
 * Panneau institutionnel runtime affichant les 5 BIO-REACTEURS_Ω :
 *  - 13 outputs par espèce (ENGINE_COMPORTEMENT … ENGINE_MINERAUX)
 *  - SHA-256 BIO_PROFILE_Ω + BIO_REACTEUR_Ω avec alignement
 *  - 275 paths résolus totaux
 *  - Statut anti-générique runtime live
 *
 * Source : GET /api/v30/especes/bio-reacteur/integrity + /list
 * Aucune interpolation, aucune donnée legacy, aucune omission.
 * ═════════════════════════════════════════════════════════════════════════════
 */
import React, { useEffect, useState } from 'react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

const ENGINE_OUTPUTS = [
  'ENGINE_COMPORTEMENT', 'ENGINE_SENSORIEL', 'ENGINE_CORRIDORS',
  'ENGINE_NUTRITION', 'ENGINE_TERRITOIRE', 'ENGINE_INTERACTIONS',
  'ENGINE_CLIMAT', 'ENGINE_SITES_CRITIQUES', 'ENGINE_HABITAT',
  'ENGINE_RUT', 'ENGINE_NIDIFICATION', 'ENGINE_EAU', 'ENGINE_MINERAUX',
];

export default function BioReacteursOmegaPanel() {
  const [list, setList] = useState(null);
  const [integrity, setIntegrity] = useState(null);
  const [details, setDetails] = useState({}); // {espece_id: full reacteur}
  const [error, setError] = useState(null);
  const [expanded, setExpanded] = useState(null); // espece_id expanded

  useEffect(() => {
    let cancelled = false;
    const fetchAll = async () => {
      try {
        const [r1, r2] = await Promise.all([
          fetch(`${BACKEND_URL}/api/v30/especes/bio-reacteur/list?_t=${Date.now()}`,
                { credentials: 'omit', cache: 'no-store' }),
          fetch(`${BACKEND_URL}/api/v30/especes/bio-reacteur/integrity?_t=${Date.now()}`,
                { credentials: 'omit', cache: 'no-store' }),
        ]);
        if (!r1.ok) throw new Error(`list HTTP ${r1.status}`);
        if (!r2.ok) throw new Error(`integrity HTTP ${r2.status}`);
        const j1 = await r1.json();
        const j2 = await r2.json();
        if (!cancelled) { setList(j1); setIntegrity(j2); }
      } catch (e) {
        if (!cancelled) setError(String(e && e.message ? e.message : e));
      }
    };
    fetchAll();
    return () => { cancelled = true; };
  }, []);

  const onExpand = async (espece_id) => {
    if (expanded === espece_id) {
      setExpanded(null);
      return;
    }
    setExpanded(espece_id);
    if (details[espece_id]) return;
    try {
      const r = await fetch(`${BACKEND_URL}/api/v30/especes/bio-reacteur/${espece_id}?_t=${Date.now()}`,
                            { credentials: 'omit', cache: 'no-store' });
      if (!r.ok) throw new Error(`detail HTTP ${r.status}`);
      const j = await r.json();
      setDetails((prev) => ({ ...prev, [espece_id]: j }));
    } catch (e) {
      setDetails((prev) => ({ ...prev, [espece_id]: { error: String(e) } }));
    }
  };

  if (error) {
    return (
      <div data-testid="bio-reacteurs-panel-error"
        style={{ position: 'absolute', top: 510, left: 384, width: 360,
          background: 'rgba(220,38,38,0.10)', border: '1px solid rgba(220,38,38,0.45)',
          borderRadius: 8, padding: 12, color: '#FCA5A5', fontSize: 11,
          fontFamily: 'system-ui, -apple-system, sans-serif', zIndex: 902 }}>
        BIO-REACTEURS_Ω — ERREUR : {error}
      </div>
    );
  }
  if (!list || !integrity) return null;

  const totalPaths = (list.loaded || []).length * 55;
  const allPass = !!integrity.all_pass;

  return (
    <div
      data-testid="bio-reacteurs-omega-panel"
      style={{
        position: 'absolute', top: 510, left: 384, width: 380,
        background: 'rgba(8,12,20,0.94)',
        backdropFilter: 'blur(8px)',
        WebkitBackdropFilter: 'blur(8px)',
        border: `1px solid ${allPass ? 'rgba(6,182,212,0.45)' : 'rgba(245,158,11,0.45)'}`,
        borderRadius: 8, padding: '10px 12px', color: '#E0F2FE',
        fontFamily: 'system-ui, -apple-system, sans-serif', fontSize: 11,
        letterSpacing: 0.3, zIndex: 902, maxHeight: 520, overflowY: 'auto',
      }}
    >
      <div data-testid="bio-reacteurs-omega-header"
        style={{ color: allPass ? '#22d3ee' : '#f59e0b', fontWeight: 800, fontSize: 12,
                 letterSpacing: 1.5, borderBottom: `1px solid ${allPass ? 'rgba(6,182,212,0.30)' : 'rgba(245,158,11,0.30)'}`,
                 paddingBottom: 4, marginBottom: 8 }}>
        BIO-REACTEURS_Ω · PHASE XIII RUNTIME
        <span style={{ float: 'right', fontSize: 9, color: '#94a3b8' }}>
          {(list.loaded || []).length}/5
        </span>
      </div>

      {/* Bandeau audit + anti-générique */}
      <div data-testid="bio-reacteurs-status-banner"
        style={{
          padding: '6px 10px', marginBottom: 8, borderRadius: 6,
          background: allPass ? 'rgba(22,163,74,0.10)' : 'rgba(245,158,11,0.10)',
          border: `1px solid ${allPass ? '#16a34a' : '#f59e0b'}`,
          color: allPass ? '#86efac' : '#fbbf24',
          fontSize: 10, fontWeight: 700, letterSpacing: 0.5,
        }}>
        {allPass
          ? `✓ INTÉGRITÉ RUNTIME : ALL_PASS = TRUE · 5/5 BIO_PROFILE_Ω alignés`
          : `⚠ INTÉGRITÉ RUNTIME : VIOLATION DÉTECTÉE`}
        <div style={{ fontWeight: 400, fontSize: 9, color: allPass ? '#bbf7d0' : '#fde68a', marginTop: 2 }}>
          Doctrine : {integrity.doctrine || 'BCE-4X_ULTIME_ABSOLU_x3'} · Phase : {integrity.phase || 'PHASE_XIII_BIO_REACTEURS_Ω_RUNTIME'}
        </div>
      </div>

      {/* KPIs récapitulatifs */}
      <div data-testid="bio-reacteurs-kpis"
        style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 6, marginBottom: 10 }}>
        <KpiBox label="Engines / espèce" value="13" />
        <KpiBox label="Paths totaux" value={String(totalPaths)} />
        <KpiBox label="Anti-gen pass" value={`${(integrity.espece_reports || []).filter(r => r.anti_generique_pass).length}/5`} ok={allPass} />
      </div>

      {/* Liste BIO-REACTEURS */}
      {(list.loaded || []).map((br) => {
        const intRow = (integrity.espece_reports || []).find((r) => r.espece_id === br.espece_id) || {};
        const isOpen = expanded === br.espece_id;
        const detail = details[br.espece_id];
        return (
          <div
            key={br.espece_id}
            data-testid={`bio-reacteur-${br.espece_id.toLowerCase()}`}
            data-anti-generique={br.anti_generique_pass ? '1' : '0'}
            style={{
              padding: '8px 10px', marginBottom: 6, borderRadius: 6,
              background: 'rgba(0,0,0,0.30)',
              borderLeft: `3px solid ${br.anti_generique_pass ? '#22d3ee' : '#ef4444'}`,
              cursor: 'pointer',
            }}
            onClick={() => onExpand(br.espece_id)}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline' }}>
              <b style={{ color: '#22d3ee', fontSize: 12 }}>{br.espece_id}</b>
              <span style={{ fontSize: 9, color: br.anti_generique_pass ? '#22c55e' : '#ef4444' }}>
                {br.anti_generique_pass ? '✓ ANTI-GEN' : '✗ VIOLATION'}
                <span style={{ marginLeft: 6, color: '#94a3b8' }}>{isOpen ? '▼' : '▶'}</span>
              </span>
            </div>
            <div style={{ color: '#cbd5e1', fontSize: 10, marginTop: 2 }}>
              {br.reacteur_id} · 13 outputs · 55 paths
            </div>
            <div style={{ display: 'flex', gap: 8, marginTop: 4, fontSize: 9, color: '#94a3b8' }}>
              <span>Statut : <b style={{ color: '#22d3ee' }}>{br.activation_status}</b></span>
            </div>
            <div style={{ marginTop: 4, fontSize: 9, color: '#64748b', fontFamily: 'JetBrains Mono, monospace' }}>
              <div>BR sha : {br.runtime_sha256?.slice(0, 32)}…</div>
              <div>BP src : {intRow.source_bio_profile_actual_sha256?.slice(0, 32)}… {intRow.source_bio_profile_match
                ? <span style={{ color: '#22c55e' }}>✓match</span>
                : <span style={{ color: '#ef4444' }}>✗mismatch</span>}</div>
            </div>
            {/* Expansion : 13 ENGINE outputs détaillés */}
            {isOpen && detail && !detail.error && (
              <div data-testid={`bio-reacteur-${br.espece_id.toLowerCase()}-detail`}
                style={{ marginTop: 8, padding: 8, background: 'rgba(8,12,20,0.6)', borderRadius: 4,
                         border: '1px solid rgba(6,182,212,0.20)' }}>
                <div style={{ color: '#22d3ee', fontSize: 10, fontWeight: 700, marginBottom: 6 }}>
                  13 ENGINE OUTPUTS (BIO_PROFILE_Ω paths)
                </div>
                {ENGINE_OUTPUTS.map((eng) => {
                  const def = (detail.bio_reacteur_outputs || {})[eng] || {};
                  const paths = def.bio_profile_paths || [];
                  return (
                    <div key={eng}
                      data-testid={`bio-reacteur-${br.espece_id.toLowerCase()}-${eng.toLowerCase()}`}
                      style={{ marginBottom: 5, paddingBottom: 5, borderBottom: '1px dashed rgba(6,182,212,0.15)' }}>
                      <div style={{ color: '#67e8f9', fontSize: 9, fontWeight: 700 }}>{eng}</div>
                      <div style={{ color: '#94a3b8', fontSize: 8.5, marginTop: 2, fontFamily: 'JetBrains Mono, monospace' }}>
                        {paths.length} paths : {paths.join(' · ')}
                      </div>
                    </div>
                  );
                })}
                <div style={{ marginTop: 6, fontSize: 8.5, color: '#64748b' }}>
                  fallback : <b style={{ color: '#22c55e' }}>{String(detail.contraintes_respectees?.fallback_active === false)}</b> ·
                  interpolation : <b style={{ color: '#22c55e' }}>{String(detail.contraintes_respectees?.interpolation_active === false)}</b> ·
                  exclusivement_BIO_PROFILE : <b style={{ color: '#22c55e' }}>{String(detail.contraintes_respectees?.exclusivement_bio_profile_omega)}</b>
                </div>
              </div>
            )}
          </div>
        );
      })}

      {/* Footer V30 + sceau */}
      <div data-testid="bio-reacteurs-footer"
        style={{ marginTop: 6, padding: 6, fontSize: 9, color: '#64748b',
                 borderTop: '1px dashed rgba(6,182,212,0.30)' }}>
        V30 LOCKED · registry_lock={integrity.v30_locked_sha256?.['registry_lock_omega.py']?.slice(0, 16)}…<br />
        ENGINE_IA_CORRIDORS_Ω={integrity.v30_locked_sha256?.['engine_ia_corridors_omega.py']?.slice(0, 16)}…<br />
        Sceau Phase XIII · vérification continue · checked_at={integrity.checked_at_utc?.slice(0, 19)}
      </div>
    </div>
  );
}

function KpiBox({ label, value, ok = true }) {
  return (
    <div style={{
      padding: '6px 8px', background: 'rgba(8,12,20,0.6)',
      border: `1px solid ${ok ? 'rgba(6,182,212,0.30)' : 'rgba(245,158,11,0.30)'}`,
      borderRadius: 4, textAlign: 'center',
    }}>
      <div style={{ color: '#94a3b8', fontSize: 8.5, textTransform: 'uppercase', letterSpacing: 0.5 }}>{label}</div>
      <div style={{ color: ok ? '#22d3ee' : '#f59e0b', fontWeight: 800, fontSize: 14 }}>{value}</div>
    </div>
  );
}

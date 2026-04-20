/**
 * InstitutionalHealthPanel — Phase X
 * Affiche l'état de santé institutionnelle BIONIC OS V20-SUPRA :
 *   - SELF-AUDIT (conforme, suites OK/total)
 *   - Registry Lock (hash + engines scellés)
 *   - Catalog live (22+ engines)
 *   - PERF-GUARD, quality, uncertainty, calibration
 *
 * Branché sur :
 *   GET /api/v20/territoire/gouvernance
 *   GET /api/v20/territoire/engines-catalog
 *   GET /api/v20/territoire/registry-lock
 */
import { useEffect, useState } from 'react';

const API = import.meta?.env?.VITE_API_URL || process.env.REACT_APP_BACKEND_URL || '';

function StatusDot({ ok }) {
  const color = ok === true ? '#22c55e' : ok === false ? '#ef4444' : '#f59e0b';
  return (
    <span
      style={{
        display: 'inline-block',
        width: 10,
        height: 10,
        borderRadius: 5,
        background: color,
        marginRight: 8,
        boxShadow: `0 0 6px ${color}`,
      }}
      data-testid="health-panel-status-dot"
    />
  );
}

export default function InstitutionalHealthPanel({ visible = true, onClose }) {
  const [gouv, setGouv] = useState(null);
  const [catalog, setCatalog] = useState(null);
  const [lock, setLock] = useState(null);
  const [err, setErr] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!visible) return;
    let active = true;
    (async () => {
      try {
        const [g, c, l] = await Promise.all([
          fetch(`${API}/api/v20/territoire/gouvernance`).then((r) => r.json()),
          fetch(`${API}/api/v20/territoire/engines-catalog`).then((r) => r.json()),
          fetch(`${API}/api/v20/territoire/registry-lock`).then((r) => r.json()),
        ]);
        if (!active) return;
        setGouv(g);
        setCatalog(c);
        setLock(l);
      } catch (e) {
        if (active) setErr(String(e));
      } finally {
        if (active) setLoading(false);
      }
    })();
    return () => {
      active = false;
    };
  }, [visible]);

  if (!visible) return null;

  const audit = catalog?.last_audit || {};
  const conforme = audit.conforme;
  const suitesOk = audit.suites_ok;
  const suitesTotal = audit.suites_total;
  const perfSev = audit.perf_guard_severity;

  return (
    <div
      data-testid="institutional-health-panel"
      style={{
        position: 'fixed',
        top: 80,
        right: 20,
        width: 360,
        maxHeight: '80vh',
        overflowY: 'auto',
        background: 'rgba(14, 17, 23, 0.96)',
        color: '#e5e7eb',
        border: '1px solid #1f2937',
        borderRadius: 12,
        padding: 18,
        fontFamily: 'ui-monospace, SFMono-Regular, Menlo, monospace',
        fontSize: 12,
        zIndex: 9999,
        boxShadow: '0 20px 50px rgba(0,0,0,0.5)',
        backdropFilter: 'blur(12px)',
      }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
        <strong style={{ color: '#f3f4f6', fontSize: 13, letterSpacing: 0.5 }}>
          🛡 HEALTH PANEL — V20-SUPRA
        </strong>
        {onClose && (
          <button
            onClick={onClose}
            data-testid="health-panel-close"
            style={{ background: 'transparent', color: '#9ca3af', border: 'none', cursor: 'pointer', fontSize: 14 }}
          >
            ✕
          </button>
        )}
      </div>

      {loading && <div>Chargement institutionnel…</div>}
      {err && <div style={{ color: '#ef4444' }}>Erreur : {err}</div>}

      {!loading && !err && (
        <>
          <Section title="GLOBAL STATUS">
            <Row label="Conforme" data-testid="health-panel-conforme">
              <StatusDot ok={conforme} />
              {conforme === true ? 'CONFORME' : conforme === false ? 'NON-CONFORME' : 'N/A'}
            </Row>
            <Row label="Suites SELF-AUDIT" data-testid="health-panel-suites">
              {suitesOk ?? '–'} / {suitesTotal ?? '–'}
            </Row>
            <Row label="PERF-GUARD" data-testid="health-panel-perf">
              <StatusDot ok={perfSev === 'ok'} />
              {perfSev ?? 'n/a'}
            </Row>
          </Section>

          <Section title="REGISTRY LOCK (Phase XI)">
            <Row label="Version" data-testid="health-panel-registry-version">{lock?.version}</Row>
            <Row label="Engines scellés" data-testid="health-panel-engines-locked">{lock?.engines_count}</Row>
            <Row label="SHA-256 registre">
              <code style={{ fontSize: 10 }}>{lock?.sha256?.slice(0, 16)}…</code>
            </Row>
            <Row label="SHA-256 Doc Maître" data-testid="health-panel-doc-sha">
              <code style={{ fontSize: 10 }}>{lock?.document_maitre?.sha256?.slice(0, 16)}…</code>
            </Row>
          </Section>

          <Section title="GOUVERNANCE">
            <Row label="Engines live" data-testid="health-panel-engines-live">{catalog?.total_engines}</Row>
            <Row label="Sources données">{Object.keys(catalog?.data_sources || {}).length}</Row>
            <Row label="Dernier audit">
              {audit.ran_at ? new Date(audit.ran_at).toLocaleString('fr-CA') : 'jamais'}
            </Row>
          </Section>

          <Section title={`ENGINES (${(catalog?.engines || []).length})`}>
            <div style={{ maxHeight: 200, overflowY: 'auto', fontSize: 11 }} data-testid="health-panel-engines-list">
              {(catalog?.engines || []).map((e) => (
                <div key={e.name} style={{ padding: '3px 0', borderBottom: '1px solid #1f2937' }}>
                  <span style={{ color: '#60a5fa' }}>{e.name}</span>{' '}
                  <span style={{ color: '#6b7280' }}>— {e.pillar || '—'}</span>
                </div>
              ))}
            </div>
          </Section>
        </>
      )}
    </div>
  );
}

function Section({ title, children }) {
  return (
    <div style={{ marginBottom: 14 }}>
      <div style={{ color: '#9ca3af', fontSize: 11, letterSpacing: 1, marginBottom: 6 }}>{title}</div>
      {children}
    </div>
  );
}
function Row({ label, children, ...rest }) {
  return (
    <div style={{ display: 'flex', justifyContent: 'space-between', padding: '3px 0' }} {...rest}>
      <span style={{ color: '#9ca3af' }}>{label}</span>
      <span style={{ color: '#e5e7eb' }}>{children}</span>
    </div>
  );
}

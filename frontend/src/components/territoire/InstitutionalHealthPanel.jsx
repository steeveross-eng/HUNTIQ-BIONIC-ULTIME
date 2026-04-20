/**
 * InstitutionalHealthPanel — Phase X / X-D / XI-SUPRA-D
 *
 * Affiche l'état de santé institutionnelle BIONIC OS V20-SUPRA :
 *   - SELF-AUDIT (conforme, suites OK/total)
 *   - Registry Lock (hash + engines scellés)
 *   - Catalog live
 *   - PERF-GUARD, SLA 30 j (sparkline cold/warm/drift) — Phase X-D
 *   - Client WebSocket /ws/self-audit-alert (toast + historique)   — Phase X-D
 *   - Statut LEP-INGESTION-Ω (INGESTED / NOT_INGESTED)             — Phase XI-SUPRA-D
 *
 * Endpoints :
 *   GET  /api/v20/territoire/gouvernance
 *   GET  /api/v20/territoire/engines-catalog
 *   GET  /api/v20/territoire/registry-lock
 *   GET  /api/v20/territoire/sla-baseline-30j
 *   GET  /api/v20/territoire/lep/status
 *   WS   /ws/self-audit-alert
 */
import { useEffect, useRef, useState, useMemo } from 'react';

const API = import.meta?.env?.VITE_API_URL || process.env.REACT_APP_BACKEND_URL || '';

function StatusDot({ ok }) {
  const color = ok === true ? '#22c55e' : ok === false ? '#ef4444' : '#f59e0b';
  return (
    <span
      style={{
        display: 'inline-block', width: 10, height: 10, borderRadius: 5,
        background: color, marginRight: 8, boxShadow: `0 0 6px ${color}`,
      }}
      data-testid="health-panel-status-dot"
    />
  );
}

// Sparkline SVG minimal — X-D
function Sparkline({ values, color = '#60a5fa', width = 260, height = 36, label = '', unit = '' }) {
  if (!values || values.length === 0) {
    return <div style={{ fontSize: 10, color: '#6b7280' }}>{label}: n/a</div>;
  }
  const min = Math.min(...values);
  const max = Math.max(...values);
  const range = max - min || 1;
  const step = values.length > 1 ? width / (values.length - 1) : 0;
  const points = values
    .map((v, i) => `${(i * step).toFixed(1)},${(height - ((v - min) / range) * (height - 4) - 2).toFixed(1)}`)
    .join(' ');
  const last = values[values.length - 1];
  return (
    <div style={{ marginBottom: 6 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 10, color: '#9ca3af' }}>
        <span>{label}</span>
        <span style={{ color: '#e5e7eb' }}>{last?.toFixed ? last.toFixed(1) : last}{unit}</span>
      </div>
      <svg width={width} height={height} style={{ display: 'block' }} data-testid={`sla-sparkline-${label.toLowerCase().replace(/\s+/g, '-')}`}>
        <polyline fill="none" stroke={color} strokeWidth="1.4" points={points} />
      </svg>
      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 9, color: '#6b7280' }}>
        <span>min {min.toFixed ? min.toFixed(1) : min}{unit}</span>
        <span>max {max.toFixed ? max.toFixed(1) : max}{unit}</span>
      </div>
    </div>
  );
}

function useSlaBaseline30j(visible) {
  const [data, setData] = useState(null);
  useEffect(() => {
    if (!visible) return;
    let alive = true;
    fetch(`${API}/api/v20/territoire/sla-baseline-30j`)
      .then((r) => r.json())
      .then((d) => { if (alive) setData(d); })
      .catch(() => {});
    return () => { alive = false; };
  }, [visible]);
  return data;
}

function useLepStatus(visible) {
  const [data, setData] = useState(null);
  useEffect(() => {
    if (!visible) return;
    let alive = true;
    fetch(`${API}/api/v20/territoire/lep/status`)
      .then((r) => r.json())
      .then((d) => { if (alive) setData(d); })
      .catch(() => {});
    return () => { alive = false; };
  }, [visible]);
  return data;
}

// WS client alerts — Phase X-D
function useSelfAuditAlertWS(visible) {
  const [alerts, setAlerts] = useState([]);
  const [toast, setToast] = useState(null);
  const [wsStatus, setWsStatus] = useState('closed');
  const audioRef = useRef(null);

  useEffect(() => {
    if (!visible) return;
    // Construire l'URL WS à partir de REACT_APP_BACKEND_URL
    let wsUrl;
    try {
      const u = new URL(API);
      u.protocol = u.protocol === 'https:' ? 'wss:' : 'ws:';
      u.pathname = '/ws/self-audit-alert';
      u.search = '';
      wsUrl = u.toString();
    } catch {
      wsUrl = `${API.replace(/^http/, 'ws')}/ws/self-audit-alert`;
    }

    let ws;
    let mounted = true;
    let reconnectTimer;
    const connect = () => {
      try {
        ws = new WebSocket(wsUrl);
        setWsStatus('connecting');
        ws.onopen = () => mounted && setWsStatus('open');
        ws.onmessage = (ev) => {
          if (!mounted) return;
          try {
            const msg = JSON.parse(ev.data);
            if (msg.kind === 'hello') {
              if (Array.isArray(msg.last_alerts)) setAlerts(msg.last_alerts);
              return;
            }
            setAlerts((prev) => [msg, ...prev].slice(0, 50));
            if (msg.severity === 'critical' || msg.severity === 'warning') {
              setToast(msg);
              try { audioRef.current && audioRef.current.play(); } catch { /* noop */ }
              setTimeout(() => setToast(null), 8000);
            }
          } catch { /* noop */ }
        };
        ws.onclose = () => {
          if (!mounted) return;
          setWsStatus('closed');
          reconnectTimer = setTimeout(connect, 5000);
        };
        ws.onerror = () => setWsStatus('error');
      } catch { /* noop */ }
    };
    connect();
    return () => {
      mounted = false;
      clearTimeout(reconnectTimer);
      try { ws && ws.close(); } catch { /* noop */ }
    };
  }, [visible]);

  return { alerts, toast, wsStatus, audioRef };
}

export default function InstitutionalHealthPanel({ visible = true, onClose }) {
  const [gouv, setGouv] = useState(null);
  const [catalog, setCatalog] = useState(null);
  const [lock, setLock] = useState(null);
  const [err, setErr] = useState(null);
  const [loading, setLoading] = useState(true);

  const sla30 = useSlaBaseline30j(visible);
  const lep = useLepStatus(visible);
  const { alerts, toast, wsStatus, audioRef } = useSelfAuditAlertWS(visible);

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
        setGouv(g); setCatalog(c); setLock(l);
      } catch (e) {
        if (active) setErr(String(e));
      } finally {
        if (active) setLoading(false);
      }
    })();
    return () => { active = false; };
  }, [visible]);

  const series = sla30?.series || [];
  const coldArr = useMemo(() => series.map((p) => p.latency_cold_ms), [series]);
  const warmArr = useMemo(() => series.map((p) => p.latency_warm_ms), [series]);
  const scoreArr = useMemo(() => series.map((p) => p.score_global_avg), [series]);

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
        position: 'fixed', top: 80, right: 20, width: 360, maxHeight: '85vh',
        overflowY: 'auto', background: 'rgba(14,17,23,0.96)', color: '#e5e7eb',
        border: '1px solid #1f2937', borderRadius: 12, padding: 18,
        fontFamily: 'ui-monospace, SFMono-Regular, Menlo, monospace', fontSize: 12,
        zIndex: 9999, boxShadow: '0 20px 50px rgba(0,0,0,0.5)',
        backdropFilter: 'blur(12px)',
      }}
    >
      {/* Audio beacon pour alertes critiques (440 Hz 250 ms, data-URI) */}
      <audio
        ref={audioRef}
        data-testid="health-panel-alert-beacon"
        preload="auto"
        src="data:audio/wav;base64,UklGRhwMAABXQVZFZm10IBAAAAABAAEAESsAACJWAAACABAAZGF0YfgLAAA="
      />

      {/* Toast critique — Phase X-D */}
      {toast && (
        <div
          data-testid="health-panel-alert-toast"
          style={{
            position: 'fixed', top: 30, left: '50%', transform: 'translateX(-50%)',
            background: toast.severity === 'critical' ? '#7f1d1d' : '#78350f',
            color: '#fff', padding: '10px 18px', borderRadius: 8,
            border: '1px solid rgba(255,255,255,0.15)', zIndex: 10000,
            boxShadow: '0 12px 40px rgba(0,0,0,0.5)', fontFamily: 'ui-monospace, monospace',
            fontSize: 12, letterSpacing: 0.5,
          }}
        >
          [{toast.severity?.toUpperCase()}] {toast.kind}: {toast.message}
        </div>
      )}

      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
        <strong style={{ color: '#f3f4f6', fontSize: 13, letterSpacing: 0.5 }}>
          HEALTH PANEL — V20-SUPRA
        </strong>
        {onClose && (
          <button
            onClick={onClose}
            data-testid="health-panel-close"
            style={{ background: 'transparent', color: '#9ca3af', border: 'none', cursor: 'pointer', fontSize: 14 }}
          >
            ×
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
              <StatusDot ok={perfSev === 'ok'} /> {perfSev ?? 'n/a'}
            </Row>
            <Row label="WS alert channel" data-testid="health-panel-ws-status">
              <StatusDot ok={wsStatus === 'open'} /> {wsStatus}
            </Row>
          </Section>

          <Section title="SLA 30 JOURS">
            <div data-testid="health-panel-sla30j">
              <Sparkline values={coldArr} label="Latence cold" unit=" ms" color="#fbbf24" />
              <Sparkline values={warmArr} label="Latence warm" unit=" ms" color="#60a5fa" />
              <Sparkline values={scoreArr} label="Drift score" unit="" color="#a78bfa" />
              <Row label="Drift score (30j)">
                {sla30?.summary?.score_global_drift ?? '–'}
              </Row>
              <Row label="Alertes perf (30j)">
                {sla30?.summary?.perf_warnings_count ?? '–'}
              </Row>
            </div>
          </Section>

          <Section title="ALERTES SELF-AUDIT (WS)">
            <div style={{ maxHeight: 140, overflowY: 'auto' }} data-testid="health-panel-alert-history">
              {(alerts || []).length === 0 && (
                <div style={{ color: '#6b7280', fontSize: 11 }}>Aucune alerte reçue.</div>
              )}
              {(alerts || []).map((a, idx) => (
                <div key={idx} style={{
                  padding: '4px 0', borderBottom: '1px solid #1f2937', fontSize: 11,
                  color: a.severity === 'critical' ? '#fca5a5'
                       : a.severity === 'warning' ? '#fcd34d' : '#9ca3af',
                }}>
                  [{a.severity}] {a.kind}: {a.message}
                </div>
              ))}
            </div>
          </Section>

          <Section title="REGISTRY LOCK">
            <Row label="Version" data-testid="health-panel-registry-version">{lock?.version}</Row>
            <Row label="Engines scellés" data-testid="health-panel-engines-locked">{lock?.engines_count}</Row>
            <Row label="SHA-256 registre">
              <code style={{ fontSize: 10 }}>{lock?.sha256?.slice(0, 16)}…</code>
            </Row>
            <Row label="SHA-256 Doc Maître" data-testid="health-panel-doc-sha">
              <code style={{ fontSize: 10 }}>{lock?.document_maitre?.sha256?.slice(0, 16)}…</code>
            </Row>
          </Section>

          <Section title="LEP-INGESTION-Ω">
            <Row label="Statut" data-testid="health-panel-lep-status">
              <StatusDot ok={lep?.status === 'INGESTED'} />
              {lep?.status ?? '–'}
            </Row>
            <Row label="Couches GeoJSON">
              {(lep?.geojson || []).length}
            </Row>
            <Row label="Signature ESI-Ω">
              <code style={{ fontSize: 10 }}>{lep?.esi_signature?.slice(0, 16) ?? '–'}</code>
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
            <div style={{ maxHeight: 160, overflowY: 'auto', fontSize: 11 }} data-testid="health-panel-engines-list">
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

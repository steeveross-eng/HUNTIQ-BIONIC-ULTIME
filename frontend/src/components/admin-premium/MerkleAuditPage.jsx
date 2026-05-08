/**
 * MerkleAuditPage.jsx — P21 · UI P14+P24 (Merkle anchor + OTS automation)
 * COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU · ANTI-GÉNÉRIQUE STRICT
 */
import React, { useEffect, useState } from 'react';
import {
  merkleStatus, merkleBuild,
  otsStatus, otsHookActivate, otsScanNow, otsStop,
} from '@/lib/bce4xApi';
import {
  Anchor, Bitcoin, RefreshCw, Play, Pause, AlertTriangle, ShieldCheck,
} from 'lucide-react';

const MerkleAuditPage = () => {
  const [merkle, setMerkle] = useState(null);
  const [ots, setOts] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [logs, setLogs] = useState([]);

  const log = (l) => setLogs((s) => [`${new Date().toLocaleTimeString()} · ${l}`, ...s].slice(0, 12));

  const refresh = async () => {
    const [m, o] = await Promise.all([merkleStatus(), otsStatus()]);
    if (m.ok) setMerkle(m.data?.result);
    if (o.ok) setOts(o.data?.result);
  };

  useEffect(() => {
    refresh();
  }, []);

  const onMerkleBuild = async () => {
    setBusy(true); setError('');
    const r = await merkleBuild({ persist: true, enable_ots_anchor: false });
    if (r.ok) { log('MERKLE_BUILD_OK'); await refresh(); }
    else { setError(`MERKLE_BUILD_FAILED::${r.detail}`); log('MERKLE_BUILD_FAIL'); }
    setBusy(false);
  };

  const onOtsActivate = async () => {
    setBusy(true); setError('');
    const r = await otsHookActivate({ interval_s: 21600, run_immediate_scan: true, persist: true });
    if (r.ok) { log('OTS_AUTOMATION_STARTED'); await refresh(); }
    else { setError(`OTS_ACTIVATE_FAILED::${r.detail}`); log('OTS_ACTIVATE_FAIL'); }
    setBusy(false);
  };

  const onOtsScan = async () => {
    setBusy(true); setError('');
    const r = await otsScanNow({ persist: true, timeout_s_per_file: 30 });
    if (r.ok) {
      log(`OTS_SCAN_OK · upgraded=${r.data?.result?.n_upgraded_bitcoin_attested || 0}`);
      await refresh();
    } else {
      setError(`OTS_SCAN_FAILED::${r.detail}`);
      log('OTS_SCAN_FAIL');
    }
    setBusy(false);
  };

  const onOtsStop = async () => {
    setBusy(true); setError('');
    const r = await otsStop();
    if (r.ok) { log(`OTS_STOP · ${r.data?.result?.status}`); await refresh(); }
    setBusy(false);
  };

  return (
    <div data-testid="merkle-audit-page" style={{ maxWidth: 1100 }}>
      <header style={{ marginBottom: 20 }}>
        <h1 style={{ color: '#D4A017', fontSize: 24, margin: 0, fontWeight: 800 }}>
          MERKLE AUDIT · BITCOIN ANCHORING · P14 + P24
        </h1>
        <p style={{ opacity: 0.7, fontSize: 12, marginTop: 4 }}>
          Ancrage cryptographique des manifests dans la blockchain Bitcoin via OpenTimestamps.
          Automation 6h cycle (P24).
        </p>
      </header>

      {error && (
        <div
          data-testid="merkle-audit-error"
          style={{
            background: 'rgba(220,38,38,0.15)',
            border: '1px solid rgba(220,38,38,0.4)',
            padding: 10, borderRadius: 6, marginBottom: 16,
            color: '#FCA5A5', fontSize: 12,
            display: 'flex', alignItems: 'center', gap: 6,
          }}
        >
          <AlertTriangle size={14} /> {error}
        </div>
      )}

      {/* MERKLE block */}
      <section
        data-testid="merkle-audit-merkle-block"
        style={blockStyle('#D4A017')}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
          <Anchor size={18} color="#D4A017" />
          <h2 style={{ color: '#D4A017', fontSize: 14, margin: 0, letterSpacing: 1.5, fontWeight: 800 }}>
            MERKLE TREE ANCHOR (P14)
          </h2>
        </div>
        <KV label="Status" value={<code>{merkle?.current_status || '—'}</code>} />
        <KV label="Verdict" value={merkle?.last_verdict || '—'} />
        <KV label="Last manifest SHA-256" value={<code>{merkle?.last_manifest_sha256 || '—'}</code>} />
        <KV label="Last updated UTC" value={merkle?.last_updated_utc || '—'} />
        <div style={{ marginTop: 10, display: 'flex', gap: 8, flexWrap: 'wrap' }}>
          <button onClick={onMerkleBuild} disabled={busy}
                  data-testid="merkle-audit-build-btn" style={primaryBtn('#D4A017')}>
            <Play size={11} /> Construire Merkle Tree
          </button>
          <button onClick={refresh} data-testid="merkle-audit-refresh"
                  style={ghostBtn('#7CB518')}>
            <RefreshCw size={11} /> Refresh
          </button>
        </div>
      </section>

      {/* OTS block */}
      <section
        data-testid="merkle-audit-ots-block"
        style={blockStyle('#F59E0B')}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
          <Bitcoin size={18} color="#F59E0B" />
          <h2 style={{ color: '#F59E0B', fontSize: 14, margin: 0, letterSpacing: 1.5, fontWeight: 800 }}>
            OTS UPGRADE AUTOMATION (P24)
          </h2>
        </div>
        <KV label="Status" value={<code>{ots?.current_status || '—'}</code>} />
        <KV label="Background task alive" value={
          <span style={{ color: ots?.background_task_alive ? '#7CB518' : '#FCA5A5' }}>
            {ots?.background_task_alive ? '✓ ALIVE' : '✗ STOPPED'}
          </span>
        } />
        <KV label="Last verdict" value={ots?.last_verdict || '—'} />
        <KV label="N activations" value={ots?.n_activations_history || 0} />
        <KV label="Last manifest SHA" value={<code>{ots?.last_manifest_sha256 || '—'}</code>} />
        <KV label="Last scan" value={
          ots?.last_scan_in_memory_summary ? (
            <span>
              upgraded={ots.last_scan_in_memory_summary.n_ots_files_scanned || 0} · sha={(ots.last_scan_in_memory_summary.scan_sha256 || '—').slice(0, 16)}…
            </span>
          ) : '—'
        } />
        <div style={{ marginTop: 10, display: 'flex', gap: 8, flexWrap: 'wrap' }}>
          <button onClick={onOtsActivate} disabled={busy}
                  data-testid="merkle-audit-ots-activate" style={primaryBtn('#F59E0B')}>
            <Play size={11} /> Activer Automation 6h
          </button>
          <button onClick={onOtsScan} disabled={busy}
                  data-testid="merkle-audit-ots-scan" style={ghostBtn('#06B6D4')}>
            <RefreshCw size={11} /> Scan Now
          </button>
          <button onClick={onOtsStop} disabled={busy}
                  data-testid="merkle-audit-ots-stop" style={ghostBtn('#FCA5A5')}>
            <Pause size={11} /> Stop Background
          </button>
        </div>
      </section>

      {/* Log */}
      <section
        data-testid="merkle-audit-log"
        style={{
          marginTop: 16,
          background: 'rgba(15,23,42,0.4)',
          border: '1px solid rgba(212,160,23,0.15)',
          padding: 10, borderRadius: 6, fontSize: 10,
          fontFamily: 'JetBrains Mono, monospace',
        }}
      >
        <div style={{ color: '#D4A017', fontWeight: 800, marginBottom: 6, letterSpacing: 1 }}>
          AUDIT LOG (session)
        </div>
        {logs.length === 0 ? (
          <span style={{ opacity: 0.5 }}>Aucune action effectuée.</span>
        ) : (
          logs.map((l, i) => (
            <div key={i} style={{ color: '#7CB518', opacity: 0.85 }}>{l}</div>
          ))
        )}
      </section>

      <div
        style={{
          marginTop: 14, padding: 10, fontSize: 10, opacity: 0.7,
          fontFamily: 'JetBrains Mono, monospace',
          background: 'rgba(15,23,42,0.4)', borderRadius: 6,
        }}
      >
        <ShieldCheck size={11} style={{ verticalAlign: 'middle', marginRight: 4 }} />
        V30_LOCK INVIOLÉ · ANTI-GÉNÉRIQUE STRICT · OTS calendar Bitcoin · 1-6h confirmation
      </div>
    </div>
  );
};

const KV = ({ label, value }) => (
  <div style={{ fontSize: 11, padding: '3px 0', display: 'flex', gap: 10 }}>
    <span style={{ opacity: 0.6, minWidth: 160 }}>{label} :</span>
    <span style={{ flex: 1, wordBreak: 'break-all', fontFamily: 'JetBrains Mono, monospace', fontSize: 10 }}>
      {value}
    </span>
  </div>
);

const blockStyle = (accent) => ({
  background: 'rgba(15,23,42,0.7)',
  border: `1px solid ${accent}55`,
  borderLeft: `4px solid ${accent}`,
  padding: 14, borderRadius: 8, marginBottom: 14,
});

const primaryBtn = (color) => ({
  padding: '7px 14px', background: color, color: '#0F1419',
  border: 'none', borderRadius: 4, fontWeight: 800, fontSize: 11,
  cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 4,
});
const ghostBtn = (color) => ({
  padding: '7px 14px', background: 'transparent',
  border: `1px solid ${color}`, borderRadius: 4, color, fontSize: 11,
  fontWeight: 700, cursor: 'pointer',
  display: 'flex', alignItems: 'center', gap: 4,
});

export default MerkleAuditPage;

/**
 * MerkleAuditPage.jsx — P21 · UI P14+P24 (Merkle anchor + OTS automation)
 * COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU · ANTI-GÉNÉRIQUE STRICT
 *
 * P20_PHASE2 · timeline 24-48h pending_vs_upgraded ajoutée (anti-générique :
 * lit l'historique réel de l'overlay automation).
 */
import React, { useEffect, useMemo, useState } from 'react';
import {
  merkleStatus, merkleBuild,
  otsStatus, otsHistory, otsHookActivate, otsScanNow, otsStop,
} from '@/lib/bce4xApi';
import {
  Anchor, Bitcoin, RefreshCw, Play, Pause, AlertTriangle, ShieldCheck,
  TrendingUp,
} from 'lucide-react';

const MerkleAuditPage = () => {
  const [merkle, setMerkle] = useState(null);
  const [ots, setOts] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [logs, setLogs] = useState([]);
  const [history, setHistory] = useState(null);
  const [hoursWindow, setHoursWindow] = useState(48);

  const log = (l) => setLogs((s) => [`${new Date().toLocaleTimeString()} · ${l}`, ...s].slice(0, 12));

  const refresh = async () => {
    const [m, o, h] = await Promise.all([
      merkleStatus(), otsStatus(), otsHistory(hoursWindow),
    ]);
    if (m.ok) setMerkle(m.data?.result);
    if (o.ok) setOts(o.data?.result);
    if (h.ok) setHistory(h.data?.result);
  };

  useEffect(() => {
    refresh();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [hoursWindow]);

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

      {/* OTS Timeline 24-48h */}
      <OtsTimelineChart
        history={history}
        hoursWindow={hoursWindow}
        onChangeHours={setHoursWindow}
      />

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

/**
 * OtsTimelineChart — P20_PHASE2 timeline 24-48h pending vs upgraded.
 * Anti-générique : utilise UNIQUEMENT le payload réel de
 * /ots-upgrade-automation-history (no fabrication).
 */
const OtsTimelineChart = ({ history, hoursWindow, onChangeHours }) => {
  const records = history?.records || [];
  const maxScanned = Math.max(
    1,
    ...records.map((r) => r.n_ots_files_scanned || 0),
  );
  const W = 720;
  const H = 140;
  const padL = 30;
  const padR = 16;
  const padT = 18;
  const padB = 24;
  const innerW = W - padL - padR;
  const innerH = H - padT - padB;
  const barW = records.length > 0
    ? Math.max(6, innerW / records.length - 4)
    : 0;

  return (
    <section
      data-testid="merkle-audit-ots-timeline"
      style={{
        marginTop: 16,
        background: 'rgba(15,23,42,0.7)',
        border: '1px solid rgba(245,158,11,0.4)',
        borderLeft: '4px solid #F59E0B',
        padding: 14, borderRadius: 8,
      }}
    >
      <div
        style={{
          display: 'flex', alignItems: 'center',
          justifyContent: 'space-between', gap: 10, marginBottom: 8,
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <TrendingUp size={16} color="#F59E0B" />
          <h2
            style={{
              color: '#F59E0B', fontSize: 14, margin: 0,
              fontWeight: 800, letterSpacing: 1.5,
            }}
          >
            TIMELINE OTS · {hoursWindow}h
          </h2>
        </div>
        <div style={{ display: 'flex', gap: 4 }}>
          {[24, 48].map((h) => (
            <button
              key={h}
              data-testid={`merkle-audit-ots-timeline-window-${h}`}
              onClick={() => onChangeHours(h)}
              style={{
                padding: '4px 10px',
                background: hoursWindow === h
                  ? '#F59E0B'
                  : 'transparent',
                color: hoursWindow === h ? '#0F1419' : '#F59E0B',
                border: '1px solid #F59E0B',
                borderRadius: 4,
                fontSize: 10, fontWeight: 800, cursor: 'pointer',
                fontFamily: 'JetBrains Mono, monospace',
              }}
            >
              {h}h
            </button>
          ))}
        </div>
      </div>

      {records.length === 0 ? (
        <div
          data-testid="merkle-audit-ots-timeline-empty"
          style={{
            fontSize: 11, opacity: 0.6,
            fontFamily: 'JetBrains Mono, monospace',
            padding: '16px 0', textAlign: 'center',
          }}
        >
          Aucun scan dans les {hoursWindow}h écoulées · déclencher un scan via
          "Scan Now" pour alimenter la timeline.
        </div>
      ) : (
        <>
          <svg
            data-testid="merkle-audit-ots-timeline-svg"
            width="100%"
            viewBox={`0 0 ${W} ${H}`}
            style={{ display: 'block', marginTop: 4 }}
          >
            {/* Y axis */}
            <line
              x1={padL} y1={padT} x2={padL} y2={H - padB}
              stroke="rgba(212,160,23,0.3)" strokeWidth="0.5"
            />
            {/* X axis */}
            <line
              x1={padL} y1={H - padB} x2={W - padR} y2={H - padB}
              stroke="rgba(212,160,23,0.3)" strokeWidth="0.5"
            />
            {/* Scale labels */}
            <text x={6} y={padT + 4} fill="#94A3B8"
                  fontSize="8" fontFamily="JetBrains Mono, monospace">
              {maxScanned}
            </text>
            <text x={6} y={H - padB} fill="#94A3B8"
                  fontSize="8" fontFamily="JetBrains Mono, monospace">
              0
            </text>
            {/* Bars */}
            {records.map((r, i) => {
              const x = padL + i * (innerW / records.length) + 2;
              const total = r.n_ots_files_scanned || 0;
              const upgraded = r.n_upgraded_bitcoin_attested || 0;
              const pending = r.n_still_pending_next_block || 0;
              const already = r.n_already_complete || 0;
              const failed = r.n_failed || 0;
              const tot = upgraded + pending + already + failed || 1;
              const fullH = total === 0
                ? 0
                : (total / maxScanned) * innerH;
              let yCursor = H - padB - fullH;
              const segments = [
                { n: upgraded, color: '#7CB518' },
                { n: already, color: '#22C55E' },
                { n: pending, color: '#F59E0B' },
                { n: failed, color: '#DC2626' },
              ];
              return (
                <g key={i} data-testid={`merkle-audit-ots-timeline-bar-${i}`}>
                  {segments.map((s, j) => {
                    if (s.n === 0) return null;
                    const segH = (s.n / tot) * fullH;
                    const rect = (
                      <rect
                        key={j}
                        x={x} y={yCursor}
                        width={barW} height={segH}
                        fill={s.color}
                        stroke="rgba(15,23,42,0.6)"
                        strokeWidth="0.5"
                      >
                        <title>
                          {`scan #${i+1} · upgraded=${upgraded} pending=${pending} already=${already} failed=${failed} · ${r.executed_at_utc}`}
                        </title>
                      </rect>
                    );
                    yCursor += segH;
                    return rect;
                  })}
                </g>
              );
            })}
          </svg>
          <div
            style={{
              display: 'flex', gap: 12, fontSize: 9,
              fontFamily: 'JetBrains Mono, monospace',
              marginTop: 6, flexWrap: 'wrap',
            }}
          >
            <Legend color="#7CB518" label="UPGRADED Bitcoin" />
            <Legend color="#22C55E" label="ALREADY COMPLETE" />
            <Legend color="#F59E0B" label="STILL PENDING" />
            <Legend color="#DC2626" label="FAILED" />
          </div>
          <div
            data-testid="merkle-audit-ots-timeline-stats"
            style={{
              marginTop: 8, fontSize: 10,
              fontFamily: 'JetBrains Mono, monospace',
              opacity: 0.85, color: '#E8E4D9',
            }}
          >
            n_records = {records.length} · cumul_upgraded = {records.reduce((a,r)=>a+(r.n_upgraded_bitcoin_attested||0),0)} ·
            cumul_pending = {records.reduce((a,r)=>a+(r.n_still_pending_next_block||0),0)} ·
            cumul_failed = {records.reduce((a,r)=>a+(r.n_failed||0),0)}
          </div>
        </>
      )}
    </section>
  );
};

const Legend = ({ color, label }) => (
  <span style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
    <span
      style={{
        display: 'inline-block', width: 10, height: 10,
        background: color, borderRadius: 2,
      }}
    />
    <span style={{ color: '#94A3B8' }}>{label}</span>
  </span>
);

export default MerkleAuditPage;

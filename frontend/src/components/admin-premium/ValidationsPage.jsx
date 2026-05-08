/**
 * ValidationsPage.jsx — P21 · UI P22 (Commandant validations audit)
 * COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU · ANTI-GÉNÉRIQUE STRICT
 */
import React, { useEffect, useState } from 'react';
import {
  validationRecord, validationStatus,
} from '@/lib/bce4xApi';
import { ShieldCheck, AlertTriangle, CheckCircle2, XCircle, Clock } from 'lucide-react';

const DECISIONS = ['APPROVED', 'REJECTED', 'PENDING_REVIEW'];

const ValidationsPage = () => {
  const [scope, setScope] = useState('P14_PREMIUM_V7_GENERAL');
  const [decision, setDecision] = useState('APPROVED');
  const [shaInput, setShaInput] = useState('');
  const [shaList, setShaList] = useState([]);
  const [notes, setNotes] = useState('');
  const [status, setStatus] = useState(null);
  const [lastResult, setLastResult] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');

  const refresh = async () => {
    const s = await validationStatus();
    if (s.ok) setStatus(s.data?.result);
  };
  useEffect(() => {
    refresh();
  }, []);

  const addSha = () => {
    const v = shaInput.trim();
    if (v.length !== 64) {
      setError('SHA256_INVALID::expected_64_hex');
      return;
    }
    setShaList((s) => [...s, v]);
    setShaInput('');
    setError('');
  };

  const removeSha = (i) =>
    setShaList((s) => s.filter((_, idx) => idx !== i));

  const onRecord = async () => {
    if (shaList.length === 0) {
      setError('SHA256_LIST_EMPTY::add_at_least_one');
      return;
    }
    setBusy(true); setError('');
    const r = await validationRecord({
      scope,
      decision,
      sha256_list: shaList,
      notes,
      persist: true,
    });
    if (r.ok) {
      setLastResult(r.data?.result);
      setShaList([]);
      setNotes('');
      await refresh();
    } else {
      setError(`RECORD_FAILED::${r.detail}`);
    }
    setBusy(false);
  };

  const decisionIcon = (d) => {
    if (d === 'APPROVED') return <CheckCircle2 size={12} color="#7CB518" />;
    if (d === 'REJECTED') return <XCircle size={12} color="#FCA5A5" />;
    return <Clock size={12} color="#F59E0B" />;
  };

  return (
    <div data-testid="validations-page" style={{ maxWidth: 1100 }}>
      <header style={{ marginBottom: 20 }}>
        <h1 style={{ color: '#D4A017', fontSize: 24, margin: 0, fontWeight: 800 }}>
          VALIDATIONS COMMANDANT · P22
        </h1>
        <p style={{ opacity: 0.7, fontSize: 12, marginTop: 4 }}>
          Audit doctrinal des approbations formelles · APPROVED / REJECTED / PENDING_REVIEW.
        </p>
      </header>

      {error && (
        <div
          data-testid="validations-error"
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

      <section
        data-testid="validations-form"
        style={{
          background: 'rgba(15,23,42,0.7)',
          border: '1px solid rgba(212,160,23,0.3)',
          padding: 16, borderRadius: 8, marginBottom: 16,
        }}
      >
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
            gap: 10, marginBottom: 12,
          }}
        >
          <div>
            <label style={lbl}>Scope</label>
            <input
              value={scope}
              onChange={(e) => setScope(e.target.value)}
              data-testid="validations-scope"
              style={inp}
            />
          </div>
          <div>
            <label style={lbl}>Décision</label>
            <select
              value={decision}
              onChange={(e) => setDecision(e.target.value)}
              data-testid="validations-decision"
              style={inp}
            >
              {DECISIONS.map((d) => (
                <option key={d} value={d}>{d}</option>
              ))}
            </select>
          </div>
        </div>

        <label style={lbl}>SHA-256 (64 hex chars)</label>
        <div style={{ display: 'flex', gap: 6, marginBottom: 8 }}>
          <input
            value={shaInput}
            onChange={(e) => setShaInput(e.target.value)}
            placeholder="64 caractères hex"
            data-testid="validations-sha-input"
            style={{ ...inp, fontFamily: 'JetBrains Mono, monospace', fontSize: 11 }}
          />
          <button
            onClick={addSha}
            data-testid="validations-sha-add"
            style={{
              padding: '7px 14px',
              background: 'rgba(212,160,23,0.2)',
              border: '1px solid rgba(212,160,23,0.4)',
              borderRadius: 4, color: '#D4A017', fontWeight: 800,
              cursor: 'pointer',
            }}
          >
            +
          </button>
        </div>

        {shaList.length > 0 && (
          <ul
            data-testid="validations-sha-list"
            style={{
              listStyle: 'none', padding: 0, margin: 0, marginBottom: 10,
              display: 'flex', flexDirection: 'column', gap: 3,
            }}
          >
            {shaList.map((s, i) => (
              <li
                key={i}
                data-testid={`validations-sha-item-${i}`}
                style={{
                  padding: '4px 8px', background: 'rgba(15,23,42,0.6)',
                  borderRadius: 3, display: 'flex', gap: 6,
                  alignItems: 'center', fontSize: 10,
                  fontFamily: 'JetBrains Mono, monospace',
                }}
              >
                <code style={{ flex: 1, color: '#7CB518' }}>{s}</code>
                <button
                  onClick={() => removeSha(i)}
                  data-testid={`validations-sha-remove-${i}`}
                  style={{
                    background: 'transparent', border: 'none', color: '#FCA5A5',
                    cursor: 'pointer', fontSize: 12,
                  }}
                >
                  ✕
                </button>
              </li>
            ))}
          </ul>
        )}

        <label style={lbl}>Notes (optionnel)</label>
        <textarea
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
          rows={2}
          data-testid="validations-notes"
          placeholder="contexte doctrinal…"
          style={{ ...inp, marginBottom: 12 }}
        />

        <button
          onClick={onRecord}
          disabled={busy || shaList.length === 0}
          data-testid="validations-record-btn"
          style={{
            padding: '8px 20px', background: '#D4A017', color: '#0F1419',
            border: 'none', borderRadius: 4, fontWeight: 800, cursor: 'pointer',
            display: 'flex', alignItems: 'center', gap: 6,
          }}
        >
          <ShieldCheck size={12} /> Enregistrer Validation
        </button>
      </section>

      {lastResult && (
        <div
          data-testid="validations-last-result"
          style={{
            background: 'rgba(124,181,24,0.10)',
            border: '1px solid rgba(124,181,24,0.4)',
            padding: 12, borderRadius: 6, marginBottom: 14,
            fontSize: 11,
          }}
        >
          <strong style={{ color: '#7CB518' }}>✓ Validation enregistrée</strong>
          <div style={{ fontFamily: 'JetBrains Mono, monospace', fontSize: 10, marginTop: 4 }}>
            sha = {lastResult.validation_sha256?.slice(0, 32)}… · scope = {lastResult.scope} · decision = {lastResult.decision} · n_sha = {lastResult.n_sha_validated}
          </div>
        </div>
      )}

      {status && (
        <section
          data-testid="validations-status"
          style={{
            background: 'rgba(15,23,42,0.7)',
            border: '1px solid rgba(212,160,23,0.2)',
            padding: 14, borderRadius: 8,
          }}
        >
          <h3 style={{ color: '#D4A017', fontSize: 13, margin: '0 0 10px', fontWeight: 800, letterSpacing: 1 }}>
            ÉTAT DE L'AUDIT
          </h3>
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
              gap: 10, fontSize: 11,
            }}
          >
            <Stat label="Status" val={status.current_status} />
            <Stat label="N validations" val={status.n_validations_history} />
            <Stat label="Last decision" val={
              <span style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                {decisionIcon(status.last_decision)}
                {status.last_decision || '—'}
              </span>
            } />
            <Stat label="Last updated" val={status.last_updated_utc || '—'} />
            <Stat label="Last validation SHA" val={
              <code style={{ fontSize: 9 }}>
                {(status.last_validation_sha256 || '—').slice(0, 24)}…
              </code>
            } />
          </div>
        </section>
      )}
    </div>
  );
};

const lbl = { display: 'block', fontSize: 10, marginBottom: 4, opacity: 0.8, letterSpacing: 0.5 };
const inp = {
  width: '100%', padding: '7px 10px', background: '#0F1419',
  border: '1px solid rgba(212,160,23,0.3)', borderRadius: 4,
  color: '#E8E4D9', fontFamily: 'Georgia, serif', fontSize: 12,
};
const Stat = ({ label, val }) => (
  <div>
    <div style={{ opacity: 0.6, fontSize: 10, fontFamily: 'JetBrains Mono, monospace', marginBottom: 2 }}>
      {label}
    </div>
    <div style={{ color: '#E8E4D9', fontWeight: 600 }}>{val}</div>
  </div>
);

export default ValidationsPage;

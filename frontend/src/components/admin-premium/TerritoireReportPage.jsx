/**
 * TerritoireReportPage.jsx — P21 · UI P15 (rapport opérationnel)
 * COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU · ANTI-GÉNÉRIQUE STRICT
 */
import React, { useEffect, useState } from 'react';
import {
  territoireReportCreate, territoireReportStatus, territoireReportDownloadUrl,
  messagingShare,
} from '@/lib/bce4xApi';
import { Download, FileText, Mail, Send, AlertTriangle } from 'lucide-react';

const TerritoireReportPage = () => {
  const [zoneLabel, setZoneLabel] = useState('ZONE_DEFAULT_ADMIN_PREMIUM');
  const [includePdf, setIncludePdf] = useState(true);
  const [includeHtml, setIncludeHtml] = useState(true);
  const [genState, setGenState] = useState(null);
  const [status, setStatus] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [shareEmail, setShareEmail] = useState('');
  const [shareNotes, setShareNotes] = useState('');
  const [shareReplyTo, setShareReplyTo] = useState('');
  const [shareResult, setShareResult] = useState(null);

  const refresh = async () => {
    const s = await territoireReportStatus();
    if (s.ok) setStatus(s.data?.result);
  };

  useEffect(() => {
    refresh();
  }, []);

  const onGenerate = async () => {
    setBusy(true);
    setError('');
    setGenState(null);
    const r = await territoireReportCreate({
      zone_label: zoneLabel,
      include_pdf: includePdf,
      include_html: includeHtml,
      persist: true,
    });
    if (r.ok) {
      setGenState(r.data?.result);
      await refresh();
    } else {
      setError(`GENERATE_FAILED::${r.detail}`);
    }
    setBusy(false);
  };

  const onShareEmail = async () => {
    if (!genState?.report_sha256 || !shareEmail) return;
    const r = await messagingShare({
      report_sha256: genState.report_sha256,
      channel: 'email',
      recipient: shareEmail,
      subject: `[BCE-4X] Rapport ${zoneLabel}`,
      notes: shareNotes,
      reply_to: shareReplyTo || undefined,
    });
    setShareResult(r);
  };

  const onShareInternal = async () => {
    if (!genState?.report_sha256) return;
    const r = await messagingShare({
      report_sha256: genState.report_sha256,
      channel: 'internal',
      recipient: 'STEEVE-MAX@bce-4x.local',
      subject: `[BCE-4X] Rapport ${zoneLabel}`,
      notes: shareNotes,
    });
    setShareResult(r);
  };

  return (
    <div data-testid="territoire-report-page" style={{ maxWidth: 1100 }}>
      <header style={{ marginBottom: 20 }}>
        <h1 style={{ color: '#D4A017', fontSize: 24, margin: 0, fontWeight: 800 }}>
          RAPPORTS Ω OPÉRATIONNELS · P15
        </h1>
        <p style={{ opacity: 0.7, fontSize: 12, marginTop: 4 }}>
          Agrège 8 overlays sources · PDF + HTML + JSON · partage doctrinal email/internal.
        </p>
      </header>

      {/* Form */}
      <section
        data-testid="territoire-report-form"
        style={{
          background: 'rgba(15,23,42,0.7)',
          border: '1px solid rgba(212,160,23,0.3)',
          padding: 16,
          borderRadius: 8,
          marginBottom: 18,
        }}
      >
        <label style={{ display: 'block', fontSize: 11, marginBottom: 4 }}>
          Label de zone
        </label>
        <input
          data-testid="territoire-report-zone-input"
          value={zoneLabel}
          onChange={(e) => setZoneLabel(e.target.value)}
          style={{
            width: '100%',
            padding: '7px 10px',
            background: '#0F1419',
            border: '1px solid rgba(212,160,23,0.3)',
            borderRadius: 4,
            color: '#E8E4D9',
            fontFamily: 'JetBrains Mono, monospace',
            fontSize: 12,
            marginBottom: 10,
          }}
        />
        <div style={{ display: 'flex', gap: 12, alignItems: 'center', fontSize: 11 }}>
          <label>
            <input
              type="checkbox"
              checked={includePdf}
              onChange={(e) => setIncludePdf(e.target.checked)}
              data-testid="territoire-report-pdf-checkbox"
            />{' '}
            Inclure PDF
          </label>
          <label>
            <input
              type="checkbox"
              checked={includeHtml}
              onChange={(e) => setIncludeHtml(e.target.checked)}
              data-testid="territoire-report-html-checkbox"
            />{' '}
            Inclure HTML
          </label>
          <button
            onClick={onGenerate}
            disabled={busy}
            data-testid="territoire-report-generate"
            style={{
              marginLeft: 'auto',
              padding: '7px 16px',
              background: '#D4A017',
              color: '#0F1419',
              border: 'none',
              borderRadius: 4,
              fontWeight: 800,
              cursor: 'pointer',
            }}
          >
            {busy ? 'Génération…' : 'Générer Rapport'}
          </button>
        </div>
      </section>

      {error && (
        <div
          data-testid="territoire-report-error"
          style={{
            background: 'rgba(220,38,38,0.15)',
            border: '1px solid rgba(220,38,38,0.4)',
            padding: 10,
            borderRadius: 6,
            marginBottom: 16,
            color: '#FCA5A5',
            fontSize: 12,
            display: 'flex',
            alignItems: 'center',
            gap: 6,
          }}
        >
          <AlertTriangle size={14} /> {error}
        </div>
      )}

      {genState && (
        <section
          data-testid="territoire-report-result"
          style={{
            background: 'rgba(15,23,42,0.7)',
            border: '1px solid rgba(124,181,24,0.4)',
            padding: 16,
            borderRadius: 8,
            marginBottom: 18,
          }}
        >
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: 8,
              marginBottom: 8,
            }}
          >
            <FileText size={16} color="#7CB518" />
            <span
              style={{ fontWeight: 800, color: '#7CB518', letterSpacing: 1 }}
            >
              RAPPORT GÉNÉRÉ
            </span>
            <code style={{ fontSize: 10, opacity: 0.8 }}>
              sha={genState.report_sha256?.slice(0, 24)}…
            </code>
          </div>
          <div style={{ fontSize: 11, opacity: 0.85, marginBottom: 8 }}>
            Overlays présents : {genState.n_overlays_present} /{' '}
            {genState.n_overlays_present + genState.n_overlays_absent} ·
            Recommandations : {genState.recommendations_count}
          </div>
          <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
            <a
              href={territoireReportDownloadUrl(genState.report_sha256, 'pdf')}
              target="_blank"
              rel="noopener noreferrer"
              data-testid="territoire-report-dl-pdf"
              style={dlBtn('#D4A017')}
            >
              <Download size={12} /> PDF
            </a>
            <a
              href={territoireReportDownloadUrl(genState.report_sha256, 'html')}
              target="_blank"
              rel="noopener noreferrer"
              data-testid="territoire-report-dl-html"
              style={dlBtn('#7CB518')}
            >
              <Download size={12} /> HTML
            </a>
            <a
              href={territoireReportDownloadUrl(genState.report_sha256, 'json')}
              target="_blank"
              rel="noopener noreferrer"
              data-testid="territoire-report-dl-json"
              style={dlBtn('#06B6D4')}
            >
              <Download size={12} /> JSON
            </a>
          </div>

          {/* Recommandations */}
          {genState.operational_recommendations?.length > 0 && (
            <div style={{ marginTop: 14 }}>
              <h3
                style={{
                  fontSize: 12,
                  color: '#D4A017',
                  margin: '0 0 6px',
                  fontWeight: 800,
                  letterSpacing: 1,
                }}
              >
                RECOMMANDATIONS OPÉRATIONNELLES
              </h3>
              <ul style={{ paddingLeft: 16, margin: 0, fontSize: 11 }}>
                {genState.operational_recommendations.map((r, i) => (
                  <li
                    key={i}
                    style={{ marginBottom: 4 }}
                    data-testid={`territoire-report-rec-${i}`}
                  >
                    <strong style={{ color: priorityColor(r.priority) }}>
                      [{r.priority}] {r.category}
                    </strong>{' '}
                    — {r.action}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Sharing */}
          <div
            style={{
              marginTop: 16,
              borderTop: '1px solid rgba(212,160,23,0.2)',
              paddingTop: 14,
            }}
          >
            <h3
              style={{
                fontSize: 12,
                color: '#D4A017',
                margin: '0 0 8px',
                fontWeight: 800,
                letterSpacing: 1,
              }}
            >
              PARTAGE DOCTRINAL (P23)
            </h3>
            <div
              style={{
                display: 'flex',
                gap: 8,
                alignItems: 'center',
                flexWrap: 'wrap',
                fontSize: 11,
              }}
            >
              <input
                type="email"
                placeholder="email destinataire"
                value={shareEmail}
                onChange={(e) => setShareEmail(e.target.value)}
                data-testid="territoire-report-share-email"
                style={{
                  flex: '1 1 200px',
                  padding: '6px 10px',
                  background: '#0F1419',
                  border: '1px solid rgba(212,160,23,0.3)',
                  borderRadius: 4,
                  color: '#E8E4D9',
                  fontSize: 11,
                }}
              />
              <input
                type="email"
                placeholder="reply-to (mon email perso)"
                value={shareReplyTo}
                onChange={(e) => setShareReplyTo(e.target.value)}
                data-testid="territoire-report-share-reply-to"
                style={{
                  flex: '1 1 200px',
                  padding: '6px 10px',
                  background: '#0F1419',
                  border: '1px solid rgba(124,181,24,0.3)',
                  borderRadius: 4,
                  color: '#E8E4D9',
                  fontSize: 11,
                }}
              />
              <input
                placeholder="notes…"
                value={shareNotes}
                onChange={(e) => setShareNotes(e.target.value)}
                data-testid="territoire-report-share-notes"
                style={{
                  flex: '1 1 200px',
                  padding: '6px 10px',
                  background: '#0F1419',
                  border: '1px solid rgba(212,160,23,0.3)',
                  borderRadius: 4,
                  color: '#E8E4D9',
                  fontSize: 11,
                }}
              />
              <button
                onClick={onShareEmail}
                disabled={!shareEmail}
                data-testid="territoire-report-share-email-btn"
                style={shareBtn('#06B6D4')}
              >
                <Mail size={11} /> Email
              </button>
              <button
                onClick={onShareInternal}
                data-testid="territoire-report-share-internal-btn"
                style={shareBtn('#7CB518')}
              >
                <Send size={11} /> Internal
              </button>
            </div>
            {shareResult && (
              <div
                data-testid="territoire-report-share-result"
                style={{
                  marginTop: 8,
                  padding: 8,
                  background: shareResult.ok
                    ? 'rgba(124,181,24,0.15)'
                    : 'rgba(220,38,38,0.15)',
                  border: `1px solid ${
                    shareResult.ok
                      ? 'rgba(124,181,24,0.4)'
                      : 'rgba(220,38,38,0.4)'
                  }`,
                  borderRadius: 4,
                  fontSize: 11,
                  fontFamily: 'JetBrains Mono, monospace',
                  color: shareResult.ok ? '#7CB518' : '#FCA5A5',
                }}
              >
                {shareResult.ok
                  ? `OK · ${shareResult.data?.result?.delivery_result?.status || 'DELIVERED'}`
                  : `FAIL · ${shareResult.detail}`}
              </div>
            )}
          </div>
        </section>
      )}

      {status && (
        <div
          data-testid="territoire-report-status-bar"
          style={{
            fontSize: 11,
            opacity: 0.8,
            fontFamily: 'JetBrains Mono, monospace',
            padding: '8px 12px',
            background: 'rgba(15,23,42,0.5)',
            borderRadius: 6,
            border: '1px solid rgba(212,160,23,0.2)',
          }}
        >
          P15 · status = <code style={{ color: '#7CB518' }}>{status.current_status}</code> · n_reports = {status.n_reports_generated} · last_zone = {status.last_zone_label || '—'}
        </div>
      )}
    </div>
  );
};

const dlBtn = (color) => ({
  padding: '6px 12px',
  background: 'transparent',
  border: `1px solid ${color}`,
  borderRadius: 4,
  color,
  fontSize: 11,
  fontWeight: 700,
  textDecoration: 'none',
  display: 'flex',
  alignItems: 'center',
  gap: 4,
});

const shareBtn = (color) => ({
  padding: '6px 12px',
  background: 'transparent',
  border: `1px solid ${color}`,
  borderRadius: 4,
  color,
  fontSize: 11,
  fontWeight: 700,
  cursor: 'pointer',
  display: 'flex',
  alignItems: 'center',
  gap: 4,
});

const priorityColor = (p) => {
  if (p === 'P0') return '#DC2626';
  if (p === 'P1') return '#F59E0B';
  return '#7CB518';
};

export default TerritoireReportPage;

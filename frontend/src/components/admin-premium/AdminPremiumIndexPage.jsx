/**
 * AdminPremiumIndexPage.jsx — P21 · Dashboard d'accueil
 * COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU · ANTI-GÉNÉRIQUE STRICT
 */
import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  Anchor, FileText, BookOpen, MapPin, BarChart3, ShieldCheck,
  Activity, Bitcoin,
} from 'lucide-react';
import {
  territoireReportStatus, waypointGuideStatus, layerManualStatus,
  merkleStatus, otsStatus, validationStatus, messagingStatus,
  uiAuditStatus,
} from '@/lib/bce4xApi';

const TILES = [
  { to: '/admin/bce-4x-premium/visualizer', code: 'P18', label: 'Visualizer 18',  icon: BarChart3,  color: '#A78BFA', desc: 'Catalogue interactif des 18 couches' },
  { to: '/admin/bce-4x-premium/territoire', code: 'P15', label: 'Rapports Ω',     icon: FileText,   color: '#D4A017', desc: 'Rapport opérationnel complet PDF/HTML' },
  { to: '/admin/bce-4x-premium/waypoint',   code: 'P17', label: 'Field Guides',   icon: MapPin,     color: '#7CB518', desc: 'Fiche terrain par point géo' },
  { to: '/admin/bce-4x-premium/manual',     code: 'P18', label: 'Manuel Couches', icon: BookOpen,   color: '#06B6D4', desc: 'Manuel doctrinal 18 couches' },
  { to: '/admin/bce-4x-premium/merkle',     code: 'P14+P24', label: 'Merkle Audit',   icon: Anchor, color: '#F59E0B', desc: 'Bitcoin anchoring + OTS automation' },
  { to: '/admin/bce-4x-premium/validation', code: 'P22', label: 'Validations',    icon: ShieldCheck, color: '#DC2626', desc: 'Audit Commandant approbations' },
  { to: '/admin/bce-4x-premium/v5-compliance', code: 'P22Ω', label: 'V5 Compliance', icon: Activity, color: '#FF4500', desc: 'PHASE OMEGA · 5 critères doctrinaux temps réel' },
];

const AdminPremiumIndexPage = () => {
  const [statuses, setStatuses] = useState({});

  useEffect(() => {
    (async () => {
      const [
        report, guide, manual, merkle, ots, val, msg, audit,
      ] = await Promise.all([
        territoireReportStatus(), waypointGuideStatus(),
        layerManualStatus(), merkleStatus(),
        otsStatus(), validationStatus(),
        messagingStatus(), uiAuditStatus(),
      ]);
      setStatuses({
        report: report.ok ? report.data?.result : null,
        guide: guide.ok ? guide.data?.result : null,
        manual: manual.ok ? manual.data?.result : null,
        merkle: merkle.ok ? merkle.data?.result : null,
        ots: ots.ok ? ots.data?.result : null,
        val: val.ok ? val.data?.result : null,
        msg: msg.ok ? msg.data?.result : null,
        audit: audit.ok ? audit.data?.result : null,
      });
    })();
  }, []);

  return (
    <div data-testid="admin-premium-index" style={{ maxWidth: 1200 }}>
      <header style={{ marginBottom: 24 }}>
        <h1
          style={{
            color: '#D4A017', fontSize: 28, margin: 0,
            fontWeight: 800, letterSpacing: 2,
          }}
        >
          ADMIN PREMIUM · BCE-4X ULTIME ABSOLU
        </h1>
        <p style={{ opacity: 0.75, fontSize: 13, marginTop: 6 }}>
          Tableau de bord institutionnel · 6 panneaux doctrinaux · COMMANDANT STEEVE-MAX
        </p>
      </header>

      {/* Status rail */}
      <section
        data-testid="admin-premium-status-rail"
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
          gap: 10, marginBottom: 24,
        }}
      >
        <Card label="P15 · rapports" value={statuses.report?.n_reports_generated} sub={statuses.report?.current_status} color="#D4A017" />
        <Card label="P17 · guides" value={statuses.guide?.n_guides_generated} sub={statuses.guide?.current_status} color="#7CB518" />
        <Card label="P18 · manuels" value={statuses.manual?.n_manuals_generated} sub={statuses.manual?.current_status} color="#06B6D4" />
        <Card label="P14 · merkle" value={statuses.merkle?.n_activations || 0} sub={statuses.merkle?.last_verdict?.slice(0, 24)} color="#A78BFA" />
        <Card label="P24 · OTS" value={statuses.ots?.background_task_alive ? 'ALIVE' : 'STOPPED'} sub={statuses.ots?.current_status} color="#F59E0B" icon={Bitcoin} />
        <Card label="P22 · validations" value={statuses.val?.n_validations_history} sub={statuses.val?.last_decision} color="#DC2626" />
        <Card label="P23 · messaging" value={statuses.msg?.smtp_configured_now ? 'SMTP_OK' : 'SMTP_NONE'} sub={statuses.msg?.current_status} color="#33B787" />
        <Card label="P20 · audit UI" value={statuses.audit?.last_global_score || '—'} sub={statuses.audit?.last_verdict?.slice(0, 24)} color="#94A3B8" />
      </section>

      {/* Tiles */}
      <section
        data-testid="admin-premium-tiles"
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
          gap: 14,
        }}
      >
        {TILES.map((t) => {
          const Icon = t.icon;
          return (
            <Link
              key={t.to}
              to={t.to}
              data-testid={`admin-premium-tile-${t.code.toLowerCase().replace(/\+/g, '-')}`}
              style={{
                background: `linear-gradient(135deg, rgba(15,23,42,0.95), ${t.color}14)`,
                border: `1px solid ${t.color}55`,
                borderLeft: `4px solid ${t.color}`,
                borderRadius: 10,
                padding: 18,
                textDecoration: 'none',
                color: '#E8E4D9',
                transition: 'transform 0.18s, box-shadow 0.18s',
                display: 'block',
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.transform = 'translateY(-2px)';
                e.currentTarget.style.boxShadow = `0 12px 24px ${t.color}33`;
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.transform = 'translateY(0)';
                e.currentTarget.style.boxShadow = 'none';
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 8 }}>
                <Icon size={20} color={t.color} />
                <div>
                  <div style={{ fontWeight: 800, color: t.color, letterSpacing: 1 }}>
                    {t.label}
                  </div>
                  <div style={{
                    fontSize: 9, opacity: 0.7,
                    fontFamily: 'JetBrains Mono, monospace',
                  }}>
                    {t.code}
                  </div>
                </div>
              </div>
              <div style={{ fontSize: 12, opacity: 0.85, lineHeight: 1.5 }}>
                {t.desc}
              </div>
            </Link>
          );
        })}
      </section>

      <footer
        style={{
          marginTop: 28, padding: '14px 16px',
          background: 'rgba(15,23,42,0.6)',
          border: '1px solid rgba(212,160,23,0.2)',
          borderRadius: 8, fontSize: 10,
          fontFamily: 'JetBrains Mono, monospace',
          opacity: 0.75, lineHeight: 1.6,
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 4 }}>
          <Activity size={11} color="#7CB518" />
          <strong style={{ color: '#7CB518' }}>V30_LOCK INVIOLÉ</strong>
        </div>
        Doctrine : BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT · FUSION ADD-ONLY ·
        AUTH X-Commandant-Token · Aucune mutation des engines maîtres ·
        Persistance overlays /app/backend/data/pipelines/.
      </footer>
    </div>
  );
};

const Card = ({ label, value, sub, color, icon: Icon }) => (
  <div
    data-testid={`admin-premium-status-${label.replace(/[^a-z0-9]+/gi, '-').toLowerCase()}`}
    style={{
      background: 'rgba(15,23,42,0.7)',
      border: `1px solid ${color}40`,
      borderLeft: `3px solid ${color}`,
      borderRadius: 6,
      padding: '8px 12px',
      fontSize: 10,
    }}
  >
    <div style={{ display: 'flex', alignItems: 'center', gap: 4, opacity: 0.7, fontFamily: 'JetBrains Mono, monospace' }}>
      {Icon ? <Icon size={10} color={color} /> : null}
      {label}
    </div>
    <div style={{ color, fontWeight: 800, fontSize: 18, lineHeight: 1.2, marginTop: 2 }}>
      {value ?? '—'}
    </div>
    {sub && (
      <div style={{ fontSize: 9, opacity: 0.65, marginTop: 2, fontFamily: 'JetBrains Mono, monospace' }}>
        {sub}
      </div>
    )}
  </div>
);

export default AdminPremiumIndexPage;

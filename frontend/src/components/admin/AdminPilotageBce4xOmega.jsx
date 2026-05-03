import React, { useEffect, useState } from "react";
import AdminGISReceptionPanel from "./AdminGISReceptionPanel";

const API = process.env.REACT_APP_BACKEND_URL;
const REPORTS_BASE = `${API}/reports/purge_master_omega`;

const STATUS_BADGE = {
  DONE: { bg: "rgba(34,197,94,0.18)", color: "#86efac", border: "rgba(34,197,94,0.45)" },
  PROGRESS: { bg: "rgba(245,158,11,0.18)", color: "#fcd34d", border: "rgba(245,158,11,0.45)" },
  BACKLOG: { bg: "rgba(34,211,238,0.18)", color: "#67e8f9", border: "rgba(34,211,238,0.45)" },
};

export const AdminPilotageBce4xOmega = () => {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const [filter, setFilter] = useState("ALL");
  const [tab, setTab] = useState("DASHBOARD"); // DASHBOARD | GIS_RECEPTION
  const [retryCount, setRetryCount] = useState(0);

  // ─── ORDRE N°47 — Loader durci avec validation Content-Type + cache-bust ───
  const loadDashboard = React.useCallback(async () => {
    setError(null);
    setData(null);
    const cacheBust = `?v=${Date.now()}`;
    const fullUrl = `${REPORTS_BASE}/${encodeURIComponent("DASHBOARD_PILOTAGE_BCE_4X_Ω.json")}${cacheBust}`;
    try {
      const r = await fetch(fullUrl, {
        cache: "no-store",
        headers: { Accept: "application/json" },
      });
      if (!r.ok) {
        throw new Error(`HTTP ${r.status} sur ${fullUrl}`);
      }
      // Validation stricte du Content-Type pour éviter le piège "<!DOCTYPE…"
      const ct = (r.headers.get("content-type") || "").toLowerCase();
      if (!ct.includes("application/json") && !ct.includes("text/json")) {
        const bodyPreview = (await r.text()).slice(0, 80);
        throw new Error(
          `Content-Type non-JSON (reçu '${ct}'). Aperçu : ${bodyPreview}…`
        );
      }
      const j = await r.json();
      setData(j);
    } catch (e) {
      setError(`${String(e.message || e)} | URL: ${fullUrl}`);
    }
  }, []);

  useEffect(() => {
    loadDashboard();
  }, [loadDashboard, retryCount]);

  if (error) {
    // ─── ORDRE N°51-EXT · Détection automatique mode HIBERNATION ───
    const isHibernating =
      /text\/html/i.test(error) ||
      /<!DOCTYPE/i.test(error) ||
      /<html/i.test(error);

    return (
      <div style={styles.errorBanner} data-testid="pilotage-bce4x-error">
        {isHibernating ? (
          <>
            <div style={{ marginBottom: 8, fontWeight: 800, fontSize: 14 }}>
              ⏸ SERVEURS BACKEND EN HIBERNATION
            </div>
            <div style={{ marginBottom: 10, fontSize: 12, lineHeight: 1.5 }}>
              Les serveurs sont en mode économie d'énergie (Emergent Preview).
              Ils renvoient l'index.html du SPA au lieu du JSON attendu.
              <br />
              <br />
              <strong style={{ color: "#fcd34d" }}>
                ▶ Cliquez le bouton vert "Wake up servers" en bas de votre
                écran
              </strong>
              , attendez 10-30 secondes, puis cliquez "⟳ Réessayer".
            </div>
          </>
        ) : (
          <div style={{ marginBottom: 10 }}>
            ⚠ Erreur de chargement DASHBOARD : {error}
          </div>
        )}
        <button
          onClick={() => setRetryCount((c) => c + 1)}
          data-testid="pilotage-bce4x-retry-btn"
          style={{
            padding: "8px 16px",
            background: "#22d3ee",
            color: "#0a1018",
            border: "none",
            borderRadius: 6,
            fontWeight: 700,
            cursor: "pointer",
            fontSize: 12,
          }}
        >
          ⟳ Réessayer
        </button>
      </div>
    );
  }
  if (!data) {
    return (
      <div style={styles.loading} data-testid="pilotage-bce4x-loading">
        Chargement DASHBOARD_PILOTAGE_BCE_4X_Ω…
      </div>
    );
  }

  const ordres = data.ordres || [];
  const filtered = filter === "ALL" ? ordres : ordres.filter((o) => o.status === filter);
  const stats = data.statistiques_globales || {};

  return (
    <div style={styles.wrap} data-testid="pilotage-bce4x-dashboard">
      <header style={styles.header}>
        <h1 style={styles.h1}>DASHBOARD_PILOTAGE_BCE-4X_Ω</h1>
        <div style={styles.sub}>
          ADMIN PREMIUM · Doctrine BCE-4X ULTIME ABSOLU x3 · Ordres n°41 / 42_BIS / 43 ·{" "}
          {data.generated_at_utc}
        </div>
      </header>

      <div style={styles.tabRow} data-testid="pilotage-tabs">
        <button
          onClick={() => setTab("DASHBOARD")}
          style={{
            ...styles.tabBtn,
            background: tab === "DASHBOARD" ? "#22d3ee" : "#162032",
            color: tab === "DASHBOARD" ? "#0a1018" : "#e2e8f0",
          }}
          data-testid="pilotage-tab-dashboard"
        >
          DASHBOARD ORDRES
        </button>
        <button
          onClick={() => setTab("GIS_RECEPTION")}
          style={{
            ...styles.tabBtn,
            background: tab === "GIS_RECEPTION" ? "#f59e0b" : "#162032",
            color: tab === "GIS_RECEPTION" ? "#0a1018" : "#e2e8f0",
          }}
          data-testid="pilotage-tab-gis-reception"
        >
          RÉCEPTION GIS Ω
        </button>
      </div>

      {tab === "GIS_RECEPTION" ? (
        <AdminGISReceptionPanel />
      ) : (
        <>
      <div style={styles.bannerOk} data-testid="pilotage-banner">
        ★ {stats.total_ordres} ORDRES recensés · {stats.done_count} DONE ·{" "}
        {stats.progress_count} PROGRESS · {stats.backlog_count} BACKLOG · pytest{" "}
        {stats.pytest_total}/{stats.pytest_total} ★
      </div>

      <section style={styles.kpiGrid}>
        <KpiCard lbl="ORDRES" num={stats.total_ordres} />
        <KpiCard lbl="DONE" num={stats.done_count} color="#22c55e" />
        <KpiCard lbl="PROGRESS" num={stats.progress_count} color="#fbbf24" />
        <KpiCard lbl="BACKLOG" num={stats.backlog_count} color="#22d3ee" />
        <KpiCard lbl="SCEAUX" num={stats.sceaux_count} color="#f59e0b" />
        <KpiCard lbl="LIVRABLES HTTPS" num={stats.livrables_https_count} color="#22d3ee" />
        <KpiCard lbl="pytest" num={stats.pytest_total} color="#22c55e" />
        <KpiCard lbl="V30" num={stats.v30_intact ? "✓" : "✗"} color={stats.v30_intact ? "#22c55e" : "#ef4444"} />
      </section>

      <section style={styles.card}>
        <h3 style={styles.h3}>Sceaux institutionnels actifs</h3>
        {(data.sceaux || []).map((s) => (
          <div key={s.id} style={styles.sceauRow} data-testid={`sceau-${s.id}`}>
            <span style={styles.sceauLabel}>{s.label}</span>
            <code style={styles.mono}>{s.sha256}</code>
            <span style={styles.sceauStatus(s.status)}>{s.status}</span>
          </div>
        ))}
      </section>

      <section>
        <div style={styles.filterRow}>
          {["ALL", "DONE", "PROGRESS", "BACKLOG"].map((f) => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              style={{
                ...styles.filterBtn,
                background: filter === f ? "#22d3ee" : "#162032",
                color: filter === f ? "#0a1018" : "#e2e8f0",
              }}
              data-testid={`pilotage-filter-${f}`}
            >
              {f} ({f === "ALL" ? ordres.length : ordres.filter((o) => o.status === f).length})
            </button>
          ))}
        </div>

        <div style={styles.tableWrap}>
          <table style={styles.table}>
            <thead>
              <tr>
                <th style={styles.th}>n°</th>
                <th style={styles.th}>Titre</th>
                <th style={styles.th}>Status</th>
                <th style={styles.th}>Date</th>
                <th style={styles.th}>Sceau / SHA-256</th>
                <th style={styles.th}>Livrables</th>
                <th style={styles.th}>pytest</th>
              </tr>
            </thead>
            <tbody data-testid="pilotage-tbody">
              {filtered.map((o) => (
                <tr key={o.numero} data-testid={`pilotage-row-${o.numero}`}>
                  <td style={styles.td}>
                    <b>n°{o.numero}</b>
                  </td>
                  <td style={styles.td}>
                    <div style={styles.title}>{o.titre}</div>
                    <div style={styles.descr}>{o.description}</div>
                  </td>
                  <td style={styles.td}>
                    <span
                      style={{
                        ...styles.statusBadge,
                        background: STATUS_BADGE[o.status]?.bg,
                        color: STATUS_BADGE[o.status]?.color,
                        border: `1px solid ${STATUS_BADGE[o.status]?.border}`,
                      }}
                    >
                      {o.status}
                    </span>
                  </td>
                  <td style={styles.td}>{o.date || "—"}</td>
                  <td style={styles.tdMono}>{o.sceau_sha256 || "—"}</td>
                  <td style={styles.td}>
                    {(o.livrables_https || []).slice(0, 3).map((l) => (
                      <a
                        key={l.url}
                        href={l.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        style={styles.link}
                      >
                        ⬇ {l.label}
                      </a>
                    ))}
                    {(o.livrables_https || []).length > 3 && (
                      <span style={styles.muted}>
                        {" "}
                        +{o.livrables_https.length - 3} autres
                      </span>
                    )}
                  </td>
                  <td style={styles.td}>{o.pytest || "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <footer style={styles.footer}>
        <div>
          <span style={styles.footLbl}>Source :</span>{" "}
          <code style={styles.mono}>DASHBOARD_PILOTAGE_BCE_4X_Ω.json</code>
        </div>
        <div>
          <span style={styles.footLbl}>FREEZE_MASTER :</span>{" "}
          <code style={styles.mono}>{data.freeze_master_sha256?.slice(0, 32)}…</code>
        </div>
        <div style={styles.v30Lock}>
          ✓ Pilotage institutionnel · {ordres.length} ordres recensés · accès ADMIN_PREMIUM
        </div>
      </footer>
        </>
      )}
    </div>
  );
};

const KpiCard = ({ lbl, num, color = "#22d3ee" }) => (
  <div style={styles.kpi}>
    <div style={styles.kpiLbl}>{lbl}</div>
    <div style={{ ...styles.kpiNum, color }}>{num}</div>
  </div>
);

const styles = {
  wrap: { padding: "16px 0", color: "#e2e8f0", fontFamily: "'Inter','Segoe UI',sans-serif" },
  header: { borderLeft: "5px solid #f59e0b", padding: "6px 0 6px 18px", marginBottom: 22 },
  h1: { margin: 0, fontSize: 22, color: "#fef3c7", letterSpacing: "0.6px" },
  sub: { color: "#94a3b8", fontSize: 12, marginTop: 6 },
  tabRow: { display: "flex", gap: 8, marginBottom: 18, borderBottom: "1px solid #1e293b", paddingBottom: 8 },
  tabBtn: {
    padding: "10px 20px",
    border: "1px solid #1e293b",
    borderRadius: 6,
    fontWeight: 700,
    fontSize: 12,
    cursor: "pointer",
    letterSpacing: "0.4px",
    transition: "all 0.15s ease",
  },
  bannerOk: {
    background: "linear-gradient(135deg,#14532d 0%,#15803d 100%)",
    border: "1px solid #16a34a",
    color: "#dcfce7",
    padding: "12px 22px",
    borderRadius: 8,
    fontWeight: 700,
    textAlign: "center",
    marginBottom: 18,
  },
  kpiGrid: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fit,minmax(140px,1fr))",
    gap: 12,
    marginBottom: 18,
  },
  kpi: {
    padding: "14px 16px",
    background: "#162032",
    border: "1px solid #1e293b",
    borderRadius: 8,
  },
  kpiLbl: { color: "#94a3b8", fontSize: 10, textTransform: "uppercase", letterSpacing: "0.5px" },
  kpiNum: { fontWeight: 700, fontSize: 22, marginTop: 4 },
  card: {
    background: "#111c2e",
    border: "1px solid #1e293b",
    borderRadius: 10,
    padding: "18px 22px",
    marginBottom: 18,
  },
  h3: { color: "#22d3ee", fontSize: 14, marginTop: 0, marginBottom: 10 },
  sceauRow: {
    display: "flex",
    gap: 12,
    alignItems: "center",
    padding: "8px 0",
    borderBottom: "1px solid #1e293b",
    flexWrap: "wrap",
  },
  sceauLabel: { color: "#fbbf24", fontWeight: 700, fontSize: 12, minWidth: 200 },
  sceauStatus: (s) => ({
    padding: "2px 8px",
    borderRadius: 4,
    fontSize: 10,
    fontWeight: 700,
    background: s === "FINAL" ? "rgba(34,197,94,0.18)" : "rgba(245,158,11,0.18)",
    color: s === "FINAL" ? "#86efac" : "#fcd34d",
    border: `1px solid ${s === "FINAL" ? "rgba(34,197,94,0.45)" : "rgba(245,158,11,0.45)"}`,
  }),
  mono: {
    fontFamily: "'JetBrains Mono','Courier New',monospace",
    fontSize: 10,
    color: "#94a3b8",
    wordBreak: "break-all",
  },
  filterRow: { display: "flex", gap: 8, flexWrap: "wrap", marginBottom: 12 },
  filterBtn: {
    padding: "8px 14px",
    border: "1px solid #1e293b",
    borderRadius: 6,
    cursor: "pointer",
    fontWeight: 600,
    fontSize: 12,
  },
  tableWrap: {
    background: "#111c2e",
    border: "1px solid #1e293b",
    borderRadius: 10,
    overflowX: "auto",
    maxHeight: 600,
    overflowY: "auto",
  },
  table: { width: "100%", borderCollapse: "collapse", fontSize: 11.5 },
  th: {
    padding: "10px 12px",
    background: "#162032",
    color: "#fff",
    textTransform: "uppercase",
    fontSize: 10.5,
    letterSpacing: "0.5px",
    textAlign: "left",
    borderBottom: "1px solid #1e293b",
    position: "sticky",
    top: 0,
  },
  td: { padding: "8px 12px", borderBottom: "1px solid #1e293b", verticalAlign: "top" },
  tdMono: {
    padding: "8px 12px",
    borderBottom: "1px solid #1e293b",
    verticalAlign: "top",
    fontFamily: "'JetBrains Mono','Courier New',monospace",
    fontSize: 9.5,
    color: "#94a3b8",
    wordBreak: "break-all",
    maxWidth: 260,
  },
  title: { fontWeight: 600, color: "#fef3c7" },
  descr: { fontSize: 10, color: "#94a3b8", marginTop: 2 },
  statusBadge: {
    padding: "2px 8px",
    borderRadius: 4,
    fontSize: 10,
    fontWeight: 700,
    display: "inline-block",
  },
  link: {
    display: "block",
    color: "#22d3ee",
    fontSize: 10.5,
    textDecoration: "none",
    fontWeight: 600,
    marginBottom: 2,
  },
  muted: { color: "#64748b", fontSize: 10, fontStyle: "italic" },
  footer: {
    marginTop: 30,
    padding: "16px 22px",
    background: "#111c2e",
    border: "1px solid #1e293b",
    borderRadius: 10,
    fontSize: 12,
    color: "#94a3b8",
  },
  footLbl: { color: "#22d3ee", fontWeight: 600, textTransform: "uppercase", fontSize: 10 },
  v30Lock: {
    marginTop: 14,
    padding: "10px 14px",
    background: "rgba(22,163,74,0.10)",
    border: "1px solid rgba(22,163,74,0.45)",
    borderRadius: 6,
    color: "#4ade80",
    fontWeight: 700,
    textAlign: "center",
  },
  errorBanner: {
    padding: 22,
    color: "#fca5a5",
    background: "#7f1d1d",
    borderRadius: 8,
    fontWeight: 700,
    textAlign: "center",
  },
  loading: { padding: 22, color: "#94a3b8", textAlign: "center" },
};

export default AdminPilotageBce4xOmega;

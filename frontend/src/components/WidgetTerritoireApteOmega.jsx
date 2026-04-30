import React, { useEffect, useState } from "react";

const API = process.env.REACT_APP_BACKEND_URL;
const REPORTS_BASE = `${API}/reports/purge_master_omega`;

const MASTER_IDS = ["corridors", "nutrition", "sensoriel", "comportement", "gouvernance", "territoire"];
const MASTER_LABELS = {
  corridors: "CORRIDORS",
  nutrition: "NUTRITION",
  sensoriel: "SENSORIEL",
  comportement: "COMPORTEMENT",
  gouvernance: "GOUVERNANCE",
  territoire: "TERRITOIRE",
};
const ESPECES = ["ORIGNAL", "CHEVREUIL", "WAPITI", "OURS_NOIR", "DINDON_SAUVAGE"];

function decisionColor(v) {
  if (v >= 70) return "#22c55e";
  if (v >= 40) return "#fbbf24";
  return "#ef4444";
}

export const WidgetTerritoireApteOmega = () => {
  const [list, setList] = useState(null);
  const [sceauStatus, setSceauStatus] = useState(null);
  const [masters, setMasters] = useState({});
  const [error, setError] = useState(null);
  const [activeEspece, setActiveEspece] = useState("ORIGNAL");

  useEffect(() => {
    async function loadAll() {
      try {
        const [listRes, sceauRes] = await Promise.all([
          fetch(`${API}/api/v30/super-masters/list`),
          fetch(`${API}/api/v30/super-masters/sceau/status`),
        ]);
        if (!listRes.ok || !sceauRes.ok) throw new Error("API not ready");
        const listJ = await listRes.json();
        const sceauJ = await sceauRes.json();
        setList(listJ);
        setSceauStatus(sceauJ);

        const detailEntries = await Promise.all(
          MASTER_IDS.map(async (id) => {
            const r = await fetch(`${API}/api/v30/super-masters/${id}/optimised`);
            if (!r.ok) throw new Error(`Master ${id} HTTP ${r.status}`);
            return [id, await r.json()];
          })
        );
        setMasters(Object.fromEntries(detailEntries));
      } catch (e) {
        setError(String(e));
      }
    }
    loadAll();
  }, []);

  if (error) {
    return (
      <div style={styles.errorBanner} data-testid="widget-territoire-apte-error">
        ⚠ Erreur API : {error}
      </div>
    );
  }
  if (!list || !sceauStatus) {
    return (
      <div style={styles.loading} data-testid="widget-territoire-apte-loading">
        Chargement TERRITOIRE_MASTER_Ω…
      </div>
    );
  }

  const territoireScore = sceauStatus.territoire_master_x4_score;
  const decision = sceauStatus.decision;

  return (
    <div style={styles.wrap} data-testid="widget-territoire-apte">
      <header style={styles.header}>
        <h1 style={styles.h1}>WIDGET_TERRITOIRE_APTE_Ω</h1>
        <div style={styles.sub}>
          BCE-4X ULTIME ABSOLU x3 · Ordre n°40 · {list.horodatage_build}
        </div>
      </header>

      <div
        style={{
          ...styles.banner,
          background:
            decision === "APTE"
              ? "linear-gradient(135deg,#14532d,#15803d)"
              : "linear-gradient(135deg,#78350f,#92400e)",
        }}
        data-testid="widget-territoire-banner"
      >
        ★ TERRITOIRE_MASTER_Ω_FUSION_X4 = <b>{territoireScore}</b> · Décision :{" "}
        <b>{decision}</b> ★
      </div>

      <section style={styles.card}>
        <h3 style={styles.h3}>Sceau institutionnel X4 FINAL</h3>
        <p style={styles.mono} data-testid="widget-sceau-sha256">
          {sceauStatus.sceau?.sceau_sha256 || "ABSENT"}
        </p>
        <p style={styles.subInfo}>Source : {list.source}</p>
      </section>

      <h2 style={styles.h2}>6 SUPER MASTERS optimisés</h2>
      <div style={styles.kpiGrid} data-testid="widget-masters-grid">
        {MASTER_IDS.map((id) => {
          const m = masters[id];
          if (!m) return null;
          return (
            <div
              key={id}
              style={styles.masterCard}
              data-testid={`master-card-${id}`}
            >
              <div style={styles.masterLabel}>{MASTER_LABELS[id]}</div>
              <div
                style={{
                  ...styles.masterScore,
                  color: decisionColor(m.score_optimise),
                }}
              >
                {m.score_optimise}
              </div>
              <div style={styles.subInfo}>
                Baseline : {m.score_baseline}
                {" · Δ "}
                {m.delta >= 0 ? "+" : ""}
                {m.delta}
              </div>
              <div style={styles.subInfo}>
                Blocs :{" "}
                <span style={styles.mono}>{m.blocs_consumes.join(", ")}</span>
              </div>
            </div>
          );
        })}
      </div>

      <h2 style={styles.h2}>Heatmap composite (5 espèces × 6 MASTERS)</h2>
      <div style={styles.card}>
        <img
          src={`${REPORTS_BASE}/${encodeURIComponent("HEATMAP_TERRITOIRE_Ω_COMPOSITE.png")}`}
          alt="Heatmap composite"
          style={styles.heatmapImg}
          data-testid="widget-heatmap-composite"
        />
      </div>

      <h2 style={styles.h2}>Heatmaps par espèce</h2>
      <div style={styles.especeTabs} data-testid="widget-espece-tabs">
        {ESPECES.map((esp) => (
          <button
            key={esp}
            onClick={() => setActiveEspece(esp)}
            style={{
              ...styles.tab,
              background: activeEspece === esp ? "#22d3ee" : "#162032",
              color: activeEspece === esp ? "#0a1018" : "#e2e8f0",
            }}
            data-testid={`espece-tab-${esp}`}
          >
            {esp}
          </button>
        ))}
      </div>
      <div style={styles.card}>
        <img
          src={`${REPORTS_BASE}/${encodeURIComponent(
            `HEATMAP_TERRITOIRE_Ω_${activeEspece}.png`
          )}`}
          alt={`Heatmap ${activeEspece}`}
          style={styles.heatmapImg}
          data-testid={`widget-heatmap-${activeEspece}`}
        />
      </div>

      <footer style={styles.footer}>
        <div>
          <span style={styles.footLbl}>masters_signature_sha256 :</span>{" "}
          <code style={styles.mono}>
            {list.masters_signature_sha256?.slice(0, 32)}…
          </code>
        </div>
        <div style={styles.v30Lock}>
          ✓ État APTE certifié · sceau X4 scellé · données temps réel via /api/v30/super-masters/*
        </div>
      </footer>
    </div>
  );
};

const styles = {
  wrap: {
    maxWidth: 1320,
    margin: "0 auto",
    padding: "32px 20px",
    fontFamily: "'Inter','Segoe UI',sans-serif",
    background: "linear-gradient(180deg,#0a1018 0%,#0b1320 100%)",
    color: "#e2e8f0",
    minHeight: "100vh",
  },
  header: { borderLeft: "5px solid #f59e0b", padding: "6px 0 6px 18px", marginBottom: 22 },
  h1: { margin: 0, fontSize: 24, color: "#fef3c7", letterSpacing: "0.6px" },
  sub: { color: "#94a3b8", fontSize: 13, marginTop: 6 },
  banner: { padding: "12px 22px", borderRadius: 8, fontWeight: 700, textAlign: "center", marginBottom: 18, color: "#dcfce7" },
  card: { background: "#111c2e", border: "1px solid #1e293b", borderRadius: 10, padding: "18px 22px", marginBottom: 18 },
  h2: { color: "#f59e0b", fontSize: 18, margin: "32px 0 12px", borderLeft: "4px solid #f59e0b", paddingLeft: 12 },
  h3: { color: "#22d3ee", fontSize: 15, marginTop: 0, marginBottom: 10 },
  kpiGrid: { display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(180px,1fr))", gap: 12, marginBottom: 18 },
  masterCard: { padding: "14px 18px", background: "#162032", border: "1px solid #1e293b", borderRadius: 8 },
  masterLabel: { color: "#94a3b8", fontSize: 10, textTransform: "uppercase", letterSpacing: "0.5px", marginBottom: 6 },
  masterScore: { fontWeight: 700, fontSize: 28 },
  subInfo: { color: "#94a3b8", fontSize: 11, marginTop: 4 },
  mono: { fontFamily: "'JetBrains Mono','Courier New',monospace", fontSize: 10, color: "#94a3b8", wordBreak: "break-all" },
  heatmapImg: { maxWidth: "100%", display: "block", borderRadius: 6 },
  especeTabs: { display: "flex", gap: 8, flexWrap: "wrap", marginBottom: 8 },
  tab: { padding: "8px 14px", border: "1px solid #1e293b", borderRadius: 6, cursor: "pointer", fontWeight: 600, fontSize: 12 },
  footer: { marginTop: 30, padding: "18px 22px", background: "#111c2e", border: "1px solid #1e293b", borderRadius: 10, fontSize: 12, color: "#94a3b8" },
  footLbl: { color: "#22d3ee", fontWeight: 600, textTransform: "uppercase", fontSize: 10, letterSpacing: "0.5px" },
  v30Lock: { marginTop: 14, padding: "10px 14px", background: "rgba(22,163,74,0.10)", border: "1px solid rgba(22,163,74,0.45)", borderRadius: 6, color: "#4ade80", fontWeight: 700, textAlign: "center", letterSpacing: "0.6px" },
  errorBanner: { padding: 22, color: "#fca5a5", background: "#7f1d1d", borderRadius: 8, fontWeight: 700, textAlign: "center" },
  loading: { padding: 22, color: "#94a3b8", textAlign: "center" },
};

export default WidgetTerritoireApteOmega;

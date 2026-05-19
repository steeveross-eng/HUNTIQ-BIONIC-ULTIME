/**
 * HudTerritoireUltime.jsx — PHASE-E PRÉ-FUSION (HUD institutionnel)
 * ═══════════════════════════════════════════════════════════════════
 * Phase     : PHASE-E / FUSION_TERRITOIRE_Ω
 * Commandant: STEEVE-MAX
 * Protocole : BCE-4X ULTIME ABSOLU — TOP-ABSOLU
 *
 * HUD lecture seule : jauge radiale + barres de contributions des 6 chaînes +
 * bloc recommandations + echo SHA-256 V30. Aucune mutation backend.
 *
 * Endpoint consommé (LECTURE) :
 *   GET /api/v30/territoire/ultime-score?lat=&lon=&species=&month=&hour=
 */
import React, { useEffect, useMemo, useState, useCallback } from "react";

const WAYPOINT_LAT = 48.206657;
const WAYPOINT_LNG = -68.382422;

const SPECIES_OFFICIAL = [
  { key: "orignal", label: "Orignal" },
  { key: "cerf", label: "Cerf" },
  { key: "ours", label: "Ours noir" },
  { key: "dindon", label: "Dindon sauvage" },
  { key: "wapiti", label: "Wapiti" },
];

const BAND_CHIP = {
  TRÈS_FAVORABLE: { bg: "#00A676", fg: "#FFFFFF" },
  FAVORABLE: { bg: "#33B787", fg: "#FFFFFF" },
  NEUTRE: { bg: "#C0C0C0", fg: "#1F2937" },
  DÉFAVORABLE: { bg: "#F59E0B", fg: "#1F2937" },
  PROSCRIT: { bg: "#DC2626", fg: "#FFFFFF" },
};

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || "";

/**
 * Jauge radiale SVG (200×200) — arc de 270° pour score 0..100 %.
 */
function RadialGauge({ scorePct, colorPrimary, colorHaloInner, colorHaloOuter, band }) {
  const size = 220;
  const stroke = 22;
  const r = (size - stroke) / 2;
  const cx = size / 2;
  const cy = size / 2;
  const arcLen = 270;
  const startAngle = 135;
  const safe = Math.max(0, Math.min(100, Number(scorePct) || 0));
  const filledLen = (arcLen * safe) / 100;

  const polar = (angDeg) => {
    const a = (Math.PI / 180) * angDeg;
    return [cx + r * Math.cos(a), cy + r * Math.sin(a)];
  };
  const arcPath = (start, end) => {
    const [x1, y1] = polar(start);
    const [x2, y2] = polar(end);
    const large = end - start > 180 ? 1 : 0;
    return `M ${x1.toFixed(2)} ${y1.toFixed(2)} A ${r} ${r} 0 ${large} 1 ${x2.toFixed(2)} ${y2.toFixed(2)}`;
  };

  return (
    <svg
      width={size}
      height={size}
      viewBox={`0 0 ${size} ${size}`}
      data-testid="hud-ultime-radial-gauge"
      role="img"
      aria-label={`Score ULTIME ${safe.toFixed(1)}%, bande ${band}`}
    >
      <defs>
        <radialGradient id="haloGrad">
          <stop offset="0%" stopColor={colorHaloInner} stopOpacity="0.42" />
          <stop offset="100%" stopColor={colorHaloOuter} stopOpacity="0" />
        </radialGradient>
      </defs>
      <circle cx={cx} cy={cy} r={r + 18} fill="url(#haloGrad)" />
      <path
        d={arcPath(startAngle, startAngle + arcLen)}
        stroke="#111827"
        strokeOpacity="0.18"
        strokeWidth={stroke}
        fill="none"
        strokeLinecap="round"
      />
      {/* Arc rempli — rendu permanent ; absent si filledLen=0 via dasharray */}
      <path
        d={arcPath(startAngle, startAngle + Math.max(0.01, filledLen))}
        stroke={colorPrimary}
        strokeWidth={stroke}
        fill="none"
        strokeLinecap="round"
        opacity={filledLen > 0 ? 1 : 0}
      />
      <text
        x={cx}
        y={cy - 4}
        textAnchor="middle"
        fontSize="42"
        fontWeight="700"
        fill="#111827"
      >
        {safe.toFixed(1)}
      </text>
      <text x={cx} y={cy + 20} textAnchor="middle" fontSize="13" fill="#4B5563">
        % score ULTIME
      </text>
      <text x={cx} y={cy + 40} textAnchor="middle" fontSize="11" fill="#6B7280">
        {band || "—"}
      </text>
    </svg>
  );
}

function ContributionBar({ item }) {
  const pct = Math.max(0, Math.min(100, (item.metric_0_1 || 0) * 100));
  const share = Math.max(0, Math.min(100, (item.contribution || 0) * 100));
  return (
    <div
      className="hud-ultime-chain-row"
      data-testid={`hud-ultime-chain-${item.chain}`}
      style={{ marginBottom: 6 }}
    >
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          fontSize: 11,
          color: "#374151",
          marginBottom: 2,
        }}
      >
        <span>
          <b>{item.chain}</b> — {item.label}
        </span>
        <span>
          w={item.weight} · m={pct.toFixed(1)}% · Σ {share.toFixed(1)}%
        </span>
      </div>
      <div
        style={{
          background: "#E5E7EB",
          borderRadius: 4,
          height: 8,
          overflow: "hidden",
          border: "1px solid #D1D5DB",
        }}
      >
        <div
          style={{
            width: `${share}%`,
            height: "100%",
            background: "#00A676",
            transition: "width 350ms ease",
          }}
        />
      </div>
    </div>
  );
}

export default function HudTerritoireUltime({
  lat = WAYPOINT_LAT,
  lng = WAYPOINT_LNG,
  defaultSpecies = "orignal",
  month = 10,
  hour = 14,
}) {
  const [species, setSpecies] = useState(defaultSpecies);
  const [payload, setPayload] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchScore = useCallback(async () => {
    if (!BACKEND_URL) {
      setError("REACT_APP_BACKEND_URL non défini");
      setLoading(false);
      return;
    }
    setLoading(true);
    setError(null);
    try {
      // PHASE_AUDIT_RACINE_TERRITOIRE_Ω (2026-04-28) — cache-busting timestamp
      // pour garantir un appel LIVE et bypasser tout intermédiaire (SW, CDN, proxy).
      const _ts = Date.now();
      const url = `${BACKEND_URL}/api/v30/territoire/ultime-score?lat=${lat}&lon=${lng}&species=${species}&month=${month}&hour=${hour}&_t=${_ts}`;
      const r = await fetch(url, {
        credentials: "omit",
        cache: "no-store",
        headers: { "Cache-Control": "no-cache", "Pragma": "no-cache" },
      });
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      const json = await r.json();
      setPayload(json);
    } catch (e) {
      setError(String(e && e.message ? e.message : e));
      setPayload(null);
    } finally {
      setLoading(false);
    }
  }, [lat, lng, species, month, hour]);

  useEffect(() => {
    fetchScore();
  }, [fetchScore]);

  const chip = useMemo(() => {
    if (!payload) return BAND_CHIP.NEUTRE;
    return BAND_CHIP[payload.bande] || BAND_CHIP.NEUTRE;
  }, [payload]);

  if (!BACKEND_URL) {
    return (
      <div
        data-testid="hud-ultime-offline"
        style={{
          padding: 16,
          background: "#FEF3C7",
          color: "#92400E",
          border: "1px solid #F59E0B",
          borderRadius: 8,
          fontSize: 13,
        }}
      >
        HUD TERRITOIRE ULTIME indisponible — REACT_APP_BACKEND_URL non défini.
      </div>
    );
  }

  return (
    <div
      data-testid="hud-ultime-root"
      style={{
        fontFamily:
          "Inter, system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif",
        background: "linear-gradient(180deg,#FFFFFF 0%,#F7FAFC 100%)",
        border: "1px solid #00A676",
        borderRadius: 12,
        padding: 16,
        boxShadow: "0 8px 24px rgba(0,166,118,0.08)",
        maxWidth: 520,
      }}
    >
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: 8,
        }}
      >
        <div style={{ fontSize: 12, color: "#00A676", fontWeight: 700 }}>
          HUD TERRITOIRE ULTIME · PHASE-E PRÉ-FUSION
        </div>
        <span
          data-testid="hud-ultime-band-chip"
          style={{
            background: chip.bg,
            color: chip.fg,
            padding: "2px 10px",
            borderRadius: 12,
            fontSize: 12,
            fontWeight: 700,
            letterSpacing: 0.3,
          }}
        >
          {payload ? payload.bande : "—"}
        </span>
      </div>

      <div
        style={{
          display: "flex",
          gap: 16,
          alignItems: "center",
          flexWrap: "wrap",
        }}
      >
        <div style={{ flex: "0 0 auto" }}>
          <RadialGauge
            scorePct={payload ? payload.score_ultime_pct : 0}
            colorPrimary={payload ? payload.bande_color_primary : "#C0C0C0"}
            colorHaloInner={payload ? payload.bande_color_halo_inner : "#D8D8D8"}
            colorHaloOuter={payload ? payload.bande_color_halo_outer : "#EFEFEF"}
            band={payload ? payload.bande : "—"}
          />
        </div>
        <div style={{ flex: "1 1 220px", minWidth: 220 }}>
          <div style={{ marginBottom: 6 }}>
            <label style={{ fontSize: 11, color: "#6B7280" }}>Espèce</label>
            <select
              data-testid="hud-ultime-species-select"
              translate="no"
              value={species}
              onChange={(e) => setSpecies(e.target.value)}
              style={{
                width: "100%",
                padding: 6,
                borderRadius: 6,
                border: "1px solid #D1D5DB",
                fontSize: 13,
              }}
            >
              {SPECIES_OFFICIAL.map((s) => (
                <option translate="no" key={s.key} value={s.key}>
                  {s.label}
                </option>
              ))}
            </select>
          </div>
          <div style={{ fontSize: 12, color: "#374151", marginBottom: 4 }}>
            Waypoint {lat.toFixed(6)} / {lng.toFixed(6)}
          </div>
          <div style={{ fontSize: 12, color: "#374151", marginBottom: 4 }}>
            V30 alignement :{" "}
            <b>{payload ? payload.v30_alignment_label : "—"}</b>{" "}
            ({payload ? payload.v30_alignment_score.toFixed(2) : "—"}/100)
          </div>
          <div
            data-testid="hud-ultime-action"
            style={{
              fontSize: 12,
              color: chip.bg,
              fontWeight: 700,
              marginTop: 4,
            }}
          >
            ACTION : {payload ? payload.action : "—"}
          </div>
          <button
            data-testid="hud-ultime-refresh-btn"
            onClick={fetchScore}
            disabled={loading}
            style={{
              marginTop: 8,
              padding: "6px 12px",
              borderRadius: 6,
              border: "1px solid #00A676",
              background: loading ? "#E5E7EB" : "#00A676",
              color: loading ? "#6B7280" : "#FFFFFF",
              fontSize: 12,
              fontWeight: 600,
              cursor: loading ? "default" : "pointer",
            }}
          >
            {loading ? "Rafraîchissement…" : "Rafraîchir"}
          </button>
        </div>
      </div>

      {error && (
        <div
          data-testid="hud-ultime-error"
          style={{
            marginTop: 10,
            padding: 8,
            background: "#FEE2E2",
            color: "#B91C1C",
            border: "1px solid #DC2626",
            borderRadius: 6,
            fontSize: 12,
          }}
        >
          Erreur : {error}
        </div>
      )}

      <div style={{ marginTop: 14 }} data-testid="hud-ultime-contributions">
        <div
          style={{
            fontSize: 11,
            color: "#6B7280",
            marginBottom: 6,
            letterSpacing: 0.3,
          }}
        >
          CONTRIBUTIONS DES 6 CHAÎNES
        </div>
        {(payload ? payload.contributions_par_chaine : []).map((c) => (
          <ContributionBar key={c.chain} item={c} />
        ))}
      </div>

      {payload && payload.recommandations && payload.recommandations.length > 0 && (
        <div style={{ marginTop: 10 }} data-testid="hud-ultime-recommandations">
          <div style={{ fontSize: 11, color: "#6B7280", marginBottom: 4 }}>
            RECOMMANDATIONS TACTIQUES
          </div>
          <ul style={{ margin: 0, paddingLeft: 16, fontSize: 12, color: "#1F2937" }}>
            {payload.recommandations.map((r, i) => (
              <li
                key={i}
                data-testid={`hud-ultime-reco-${i}`}
                style={{ marginBottom: 2 }}
              >
                {r}
              </li>
            ))}
          </ul>
        </div>
      )}

      {payload && payload.inhibitors_applied && payload.inhibitors_applied.length > 0 && (
        <div
          data-testid="hud-ultime-inhibitors"
          style={{
            marginTop: 10,
            padding: 8,
            background: "#FEF2F2",
            border: "1px solid #DC2626",
            borderRadius: 6,
            fontSize: 12,
            color: "#B91C1C",
          }}
        >
          <b>INHIBITEURS :</b> {payload.inhibitors_applied.join(" · ")}
        </div>
      )}

      {payload && (
        <div
          data-testid="hud-ultime-registry-echo"
          style={{
            marginTop: 12,
            padding: 8,
            borderTop: "1px dashed #9CA3AF",
            fontSize: 10,
            color: "#6B7280",
            wordBreak: "break-all",
          }}
        >
          <div>
            <b>V30 LOCKED :</b>{" "}
            {payload.registry_lock_v30.invariant ? "✓ INVIOLÉ" : "✗ MUTATION"}
          </div>
          <div>SHA registry_lock : {payload.registry_lock_v30.registry_lock_omega_sha256}</div>
          <div>SHA engine_ia : {payload.registry_lock_v30.engine_ia_corridors_omega_sha256}</div>
          <div>echo : {payload.sha256_registry_echo}</div>
          <div style={{ marginTop: 4 }}>
            {payload.phase} · {payload.timestamp_utc}
          </div>
        </div>
      )}
    </div>
  );
}

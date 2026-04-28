/**
 * HudUltimeDemoPage.jsx — PHASE-E PRÉ-FUSION (page démo institutionnelle)
 * ═══════════════════════════════════════════════════════════════════════
 * Phase     : PHASE-E / FUSION_TERRITOIRE_Ω
 * Commandant: STEEVE-MAX
 * Protocole : BCE-4X ULTIME ABSOLU — TOP-ABSOLU
 *
 * Page autonome servant de preuve visuelle institutionnelle pour les
 * captures HTTPS du rapport RAPPORT_PHASE-E_FUSION_TERRITOIRE_Ω.html.
 *
 * Route : /territoire/hud-ultime-phase-e
 */
import React from "react";
import HudTerritoireUltime from "../components/territoire/HudTerritoireUltime";

const WAYPOINT_LAT = 48.206657;
const WAYPOINT_LNG = -68.382422;

export default function HudUltimeDemoPage() {
  return (
    <div
      data-testid="hud-ultime-demo-page"
      style={{
        minHeight: "100vh",
        background:
          "linear-gradient(180deg,#0B3D2E 0%,#0F4B38 35%,#12563F 70%,#0B3D2E 100%)",
        color: "#F7FAFC",
        padding: "32px 24px 64px 24px",
        fontFamily:
          "Inter, system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif",
      }}
    >
      <div style={{ maxWidth: 1200, margin: "0 auto" }}>
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: 12,
            marginBottom: 8,
          }}
        >
          <div
            style={{
              background: "#00A676",
              color: "#FFFFFF",
              fontWeight: 800,
              fontSize: 11,
              padding: "4px 10px",
              borderRadius: 4,
              letterSpacing: 1,
            }}
          >
            BCE-4X ULTIME ABSOLU — TOP-ABSOLU
          </div>
          <div style={{ fontSize: 12, color: "#B2F2D9" }}>
            Commandant : STEEVE-MAX
          </div>
        </div>
        <h1
          style={{
            fontSize: 28,
            fontWeight: 800,
            margin: "4px 0 4px 0",
            color: "#FFFFFF",
          }}
        >
          HUD TERRITOIRE_ULTIME — PRÉ-FUSION PHASE-E
        </h1>
        <p style={{ fontSize: 13, color: "#B2F2D9", marginBottom: 24 }}>
          Lecture seule · V30 LOCKED · XIX non recomputé · VITAUX non recomputé ·
          48 engines orchestrés en 6 chaînes institutionnelles ·
          Livrable visuel imposé par directive pré-fusion.
        </p>

        <div
          style={{
            display: "grid",
            gap: 24,
            gridTemplateColumns: "repeat(auto-fit, minmax(480px, 1fr))",
          }}
          data-testid="hud-ultime-demo-grid"
        >
          <section>
            <h2
              style={{
                fontSize: 14,
                color: "#00A676",
                letterSpacing: 1,
                marginBottom: 8,
              }}
            >
              VARIANTE 1 — ORIGNAL @ BSL (espèce présente)
            </h2>
            <HudTerritoireUltime
              lat={WAYPOINT_LAT}
              lng={WAYPOINT_LNG}
              defaultSpecies="orignal"
              month={10}
              hour={14}
            />
          </section>

          <section>
            <h2
              style={{
                fontSize: 14,
                color: "#F17171",
                letterSpacing: 1,
                marginBottom: 8,
              }}
            >
              VARIANTE 2 — DINDON @ BSL (espèce ABSENTE → HALT)
            </h2>
            <HudTerritoireUltime
              lat={WAYPOINT_LAT}
              lng={WAYPOINT_LNG}
              defaultSpecies="dindon"
              month={10}
              hour={14}
            />
          </section>

          <section>
            <h2
              style={{
                fontSize: 14,
                color: "#FBC04B",
                letterSpacing: 1,
                marginBottom: 8,
              }}
            >
              VARIANTE 3 — CERF @ BSL (contrôle multi-espèces)
            </h2>
            <HudTerritoireUltime
              lat={WAYPOINT_LAT}
              lng={WAYPOINT_LNG}
              defaultSpecies="cerf"
              month={10}
              hour={14}
            />
          </section>

          <section>
            <h2
              style={{
                fontSize: 14,
                color: "#C2F0DC",
                letterSpacing: 1,
                marginBottom: 8,
              }}
            >
              VARIANTE 4 — OURS @ BSL (contrôle omnivore)
            </h2>
            <HudTerritoireUltime
              lat={WAYPOINT_LAT}
              lng={WAYPOINT_LNG}
              defaultSpecies="ours"
              month={10}
              hour={14}
            />
          </section>
        </div>

        <footer
          data-testid="hud-ultime-demo-footer"
          style={{
            marginTop: 36,
            paddingTop: 12,
            borderTop: "1px solid rgba(178,242,217,0.2)",
            fontSize: 11,
            color: "#B2F2D9",
            letterSpacing: 0.5,
          }}
        >
          PHASE-E_FUSION_TERRITOIRE_Ω · Waypoint officiel 48.206657 / -68.382422 ·
          Palette verte institutionnelle #00A676 · Aucun {`testing_agent_v3_fork`} ·
          Captures HTTPS obligatoires.
        </footer>
      </div>
    </div>
  );
}

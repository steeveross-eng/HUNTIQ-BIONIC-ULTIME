/**
 * AdminGISReceptionPanel — Phase XXII (ORDRE N°43)
 * ════════════════════════════════════════════════════════════════════════
 * COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU x3 · ORDRE N°43
 *
 * Panneau ADMIN_PREMIUM_ONLY de réception des couches GIS protégées.
 *
 * Fonctionnalités :
 *   · Drag-and-drop par slot GIS
 *   · Upload chunked XHR avec progression
 *   · Intake-status live (auto-refresh)
 *   · Gestion erreurs 401/404/422/413
 *   · Affichage SHA-256 + statut LOADED/QUARANTINE
 *   · Token Commandant en sessionStorage (sécurité par session)
 *
 * Endpoints utilisés :
 *   GET  /api/v30/admin-premium/gis/slots
 *   GET  /api/v30/admin-premium/gis/intake-status
 *   POST /api/v30/admin-premium/gis/upload/{slot_id}
 *
 * V30 LOCKED INVIOLABLE — aucune génération synthétique.
 * ════════════════════════════════════════════════════════════════════════
 */
import React, { useCallback, useEffect, useMemo, useRef, useState } from "react";

const API = process.env.REACT_APP_BACKEND_URL || "";
const TOKEN_STORAGE_KEY = "gis_reception_commandant_token";

const PRIO_BADGE = {
  P0: { bg: "#fb7185", color: "#1f2937" },
  P1: { bg: "#fbbf24", color: "#1f2937" },
  P2_OPTIONNELLE: { bg: "#67e8f9", color: "#1f2937" },
};

const STATUS_BADGE = {
  ABSENT: { bg: "rgba(245,158,11,0.18)", color: "#fcd34d", border: "rgba(245,158,11,0.45)" },
  LOADED: { bg: "rgba(34,197,94,0.18)", color: "#86efac", border: "rgba(34,197,94,0.45)" },
  QUARANTINED: { bg: "rgba(239,68,68,0.18)", color: "#fca5a5", border: "rgba(239,68,68,0.45)" },
};

function formatBytes(n) {
  if (!n && n !== 0) return "—";
  if (n < 1024) return `${n} o`;
  if (n < 1024 * 1024) return `${(n / 1024).toFixed(1)} Ko`;
  if (n < 1024 * 1024 * 1024) return `${(n / 1024 / 1024).toFixed(1)} Mo`;
  return `${(n / 1024 / 1024 / 1024).toFixed(2)} Go`;
}

function shortSha(s) {
  return s ? `${s.slice(0, 16)}…${s.slice(-8)}` : "—";
}

export const AdminGISReceptionPanel = () => {
  const [slots, setSlots] = useState([]);
  const [intake, setIntake] = useState(null);
  const [loadError, setLoadError] = useState(null);
  const [token, setToken] = useState(
    () => sessionStorage.getItem(TOKEN_STORAGE_KEY) || ""
  );
  const [tokenSaved, setTokenSaved] = useState(
    () => Boolean(sessionStorage.getItem(TOKEN_STORAGE_KEY))
  );
  const [uploadState, setUploadState] = useState({}); // { [slotId]: {progress, status, message, sha256, sizeBytes} }
  const [eventLog, setEventLog] = useState([]);
  const xhrRefs = useRef({});

  const appendEvent = useCallback((entry) => {
    setEventLog((prev) =>
      [{ ts: new Date().toISOString(), ...entry }, ...prev].slice(0, 60)
    );
  }, []);

  const fetchSlots = useCallback(async () => {
    try {
      const r = await fetch(`${API}/api/v30/admin-premium/gis/slots`);
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      const d = await r.json();
      setSlots(d.slots || []);
      setLoadError(null);
    } catch (e) {
      setLoadError(`SLOTS: ${e.message}`);
    }
  }, []);

  const fetchIntake = useCallback(async () => {
    try {
      const r = await fetch(`${API}/api/v30/admin-premium/gis/intake-status`);
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      setIntake(await r.json());
    } catch (e) {
      setLoadError(`INTAKE: ${e.message}`);
    }
  }, []);

  useEffect(() => {
    fetchSlots();
    fetchIntake();
    const id = setInterval(fetchIntake, 7000);
    return () => clearInterval(id);
  }, [fetchSlots, fetchIntake]);

  const slotStatus = useCallback(
    (slotId) => intake?.slots?.[slotId]?.status || "ABSENT",
    [intake]
  );

  const slotUploads = useCallback(
    (slotId) => intake?.slots?.[slotId]?.uploads || [],
    [intake]
  );

  const handleSaveToken = () => {
    sessionStorage.setItem(TOKEN_STORAGE_KEY, token);
    setTokenSaved(true);
    appendEvent({
      level: "INFO",
      message: "Token Commandant enregistré (sessionStorage)",
    });
  };

  const handleClearToken = () => {
    sessionStorage.removeItem(TOKEN_STORAGE_KEY);
    setToken("");
    setTokenSaved(false);
    appendEvent({ level: "WARN", message: "Token Commandant effacé" });
  };

  const performUpload = useCallback(
    (slotId, file) => {
      if (!token) {
        setUploadState((s) => ({
          ...s,
          [slotId]: {
            progress: 0,
            status: "ERROR",
            message: "Token Commandant requis (saisir et enregistrer)",
          },
        }));
        appendEvent({
          level: "ERROR",
          slotId,
          message: "Upload refusé — token absent",
        });
        return;
      }

      const xhr = new XMLHttpRequest();
      xhrRefs.current[slotId] = xhr;
      const fd = new FormData();
      fd.append("file", file, file.name);

      xhr.open(
        "POST",
        `${API}/api/v30/admin-premium/gis/upload/${encodeURIComponent(slotId)}`,
        true
      );
      xhr.setRequestHeader("X-Commandant-Token", token);

      xhr.upload.onprogress = (evt) => {
        if (evt.lengthComputable) {
          setUploadState((s) => ({
            ...s,
            [slotId]: {
              ...(s[slotId] || {}),
              progress: Math.round((evt.loaded / evt.total) * 100),
              status: "UPLOADING",
              filename: file.name,
              sizeBytes: file.size,
              message: `${formatBytes(evt.loaded)} / ${formatBytes(evt.total)}`,
            },
          }));
        }
      };

      xhr.onload = () => {
        let payload = null;
        try {
          payload = JSON.parse(xhr.responseText);
        } catch {
          payload = { detail: xhr.responseText || `HTTP ${xhr.status}` };
        }

        if (xhr.status === 200 && payload.passed) {
          setUploadState((s) => ({
            ...s,
            [slotId]: {
              progress: 100,
              status: "LOADED",
              filename: file.name,
              sizeBytes: file.size,
              sha256: payload.sha256,
              message: "LOADED · validators OK",
              validators: payload.validators,
            },
          }));
          appendEvent({
            level: "INFO",
            slotId,
            message: `LOADED · ${file.name} · ${shortSha(payload.sha256)}`,
          });
        } else if (xhr.status === 422) {
          setUploadState((s) => ({
            ...s,
            [slotId]: {
              progress: 100,
              status: "QUARANTINED",
              filename: file.name,
              sizeBytes: file.size,
              sha256: payload.sha256,
              message: "QUARANTAINE · validators échoués",
              validators: payload.validators,
            },
          }));
          appendEvent({
            level: "WARN",
            slotId,
            message: `QUARANTAINE · ${file.name} · ${shortSha(payload.sha256)}`,
          });
        } else {
          const codeLabel =
            xhr.status === 401
              ? "401 · Token invalide / refusé"
              : xhr.status === 404
              ? "404 · Slot inconnu"
              : xhr.status === 413
              ? "413 · Fichier trop volumineux"
              : xhr.status === 400
              ? "400 · Nom de fichier invalide"
              : `HTTP ${xhr.status}`;
          setUploadState((s) => ({
            ...s,
            [slotId]: {
              progress: 0,
              status: "ERROR",
              filename: file.name,
              sizeBytes: file.size,
              message: `${codeLabel} — ${payload.detail || ""}`,
            },
          }));
          appendEvent({
            level: "ERROR",
            slotId,
            message: `${codeLabel} · ${file.name}`,
          });
        }
        // Refresh manifest
        fetchIntake();
      };

      xhr.onerror = () => {
        setUploadState((s) => ({
          ...s,
          [slotId]: {
            progress: 0,
            status: "ERROR",
            filename: file.name,
            message: "Erreur réseau",
          },
        }));
        appendEvent({
          level: "ERROR",
          slotId,
          message: `Erreur réseau · ${file.name}`,
        });
      };

      setUploadState((s) => ({
        ...s,
        [slotId]: {
          progress: 0,
          status: "UPLOADING",
          filename: file.name,
          sizeBytes: file.size,
          message: "Démarrage…",
        },
      }));
      appendEvent({
        level: "INFO",
        slotId,
        message: `Upload démarré · ${file.name} · ${formatBytes(file.size)}`,
      });

      xhr.send(fd);
    },
    [token, fetchIntake, appendEvent]
  );

  const cancelUpload = useCallback((slotId) => {
    const xhr = xhrRefs.current[slotId];
    if (xhr && xhr.readyState !== 4) {
      xhr.abort();
      setUploadState((s) => ({
        ...s,
        [slotId]: { ...(s[slotId] || {}), status: "ABORTED", message: "Annulé" },
      }));
    }
  }, []);

  const stats = intake?.stats || { total_slots: 0, loaded: 0, absent: 0 };

  return (
    <div style={S.wrap} data-testid="gis-reception-panel">
      <header style={S.header}>
        <h2 style={S.h2}>RÉCEPTION_GIS_Ω · ADMIN_PREMIUM_ONLY</h2>
        <div style={S.sub}>
          BCE-4X ULTIME ABSOLU x3 · Ordre n°43 · Anti-générique strict
        </div>
      </header>

      {loadError && (
        <div style={S.banner.error} data-testid="gis-reception-error">
          ⚠ {loadError}
        </div>
      )}

      <div style={S.banner.gold} data-testid="gis-reception-banner">
        ★ {stats.total_slots} SLOTS · {stats.loaded} LOADED · {stats.absent} ABSENT
        {" · "}global_status: <code>{intake?.stats?.global_status || "—"}</code> ★
      </div>

      <section style={S.tokenCard} data-testid="token-section">
        <div style={S.tokenHeader}>
          <span style={S.lbl}>X-COMMANDANT-TOKEN</span>
          <span
            style={{
              ...S.tokenStatus,
              color: tokenSaved ? "#86efac" : "#fbbf24",
            }}
          >
            {tokenSaved ? "✓ Enregistré (session)" : "⚠ Non saisi"}
          </span>
        </div>
        <div style={S.tokenRow}>
          <input
            type="password"
            value={token}
            onChange={(e) => {
              setToken(e.target.value);
              setTokenSaved(false);
            }}
            placeholder="Saisir le token Commandant…"
            style={S.tokenInput}
            data-testid="gis-reception-token-input"
            autoComplete="off"
          />
          <button
            onClick={handleSaveToken}
            disabled={!token}
            style={S.btnPrimary}
            data-testid="gis-reception-save-token-btn"
          >
            Enregistrer
          </button>
          <button
            onClick={handleClearToken}
            disabled={!tokenSaved}
            style={S.btnSecondary}
            data-testid="gis-reception-clear-token-btn"
          >
            Effacer
          </button>
        </div>
        <div style={S.muted}>
          Stockage en <code>sessionStorage</code> uniquement (jamais en
          localStorage). Le token reste sur ce navigateur, sur cette session.
        </div>
      </section>

      <section style={S.slotsGrid} data-testid="slots-grid">
        {slots.map((slot) => (
          <SlotCard
            key={slot.slot_id}
            slot={slot}
            slotStatus={slotStatus(slot.slot_id)}
            uploads={slotUploads(slot.slot_id)}
            uploadInfo={uploadState[slot.slot_id]}
            onUpload={performUpload}
            onCancel={cancelUpload}
            tokenReady={tokenSaved && Boolean(token)}
          />
        ))}
      </section>

      <section style={S.logCard} data-testid="event-log">
        <h3 style={S.h3}>Journal institutionnel ({eventLog.length})</h3>
        <div style={S.logScroll}>
          {eventLog.length === 0 && <div style={S.muted}>Aucun évènement.</div>}
          {eventLog.map((e, i) => (
            <div
              key={i}
              style={{ ...S.logRow, color: levelColor(e.level) }}
              data-testid={`event-row-${i}`}
            >
              <code style={S.mono}>{e.ts}</code>
              <span style={S.logLevel}>{e.level}</span>
              {e.slotId && <span style={S.logSlot}>{e.slotId}</span>}
              <span>{e.message}</span>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
};

function levelColor(level) {
  if (level === "ERROR") return "#fca5a5";
  if (level === "WARN") return "#fcd34d";
  return "#86efac";
}

const SlotCard = ({
  slot,
  slotStatus,
  uploads,
  uploadInfo,
  onUpload,
  onCancel,
  tokenReady,
}) => {
  const [drag, setDrag] = useState(false);
  const inputRef = useRef(null);

  const handleDrop = useCallback(
    (e) => {
      e.preventDefault();
      e.stopPropagation();
      setDrag(false);
      if (!tokenReady) return;
      const f = e.dataTransfer.files?.[0];
      if (f) onUpload(slot.slot_id, f);
    },
    [slot.slot_id, onUpload, tokenReady]
  );

  const handlePick = useCallback(
    (e) => {
      const f = e.target.files?.[0];
      if (f) onUpload(slot.slot_id, f);
      e.target.value = "";
    },
    [slot.slot_id, onUpload]
  );

  const sBadge =
    STATUS_BADGE[
      uploadInfo?.status === "QUARANTINED"
        ? "QUARANTINED"
        : slotStatus
    ] || STATUS_BADGE.ABSENT;
  const pBadge = PRIO_BADGE[slot.priority] || PRIO_BADGE.P2_OPTIONNELLE;
  const lastUpload = uploads[uploads.length - 1];

  return (
    <div
      style={S.slotCard}
      data-testid={`slot-card-${slot.slot_id}`}
    >
      <div style={S.slotHeader}>
        <div style={S.slotTitle}>{slot.slot_id}</div>
        <span
          style={{
            ...S.priorityBadge,
            background: pBadge.bg,
            color: pBadge.color,
          }}
          data-testid={`slot-prio-${slot.slot_id}`}
        >
          {slot.priority}
        </span>
      </div>

      <div style={S.slotLabel}>{slot.label}</div>
      <div style={S.muted}>
        {slot.organisme} · {slot.format_recommandé}
      </div>

      <div style={S.slotStatusRow}>
        <span
          style={{
            ...S.statusBadge,
            background: sBadge.bg,
            color: sBadge.color,
            border: `1px solid ${sBadge.border}`,
          }}
          data-testid={`slot-status-${slot.slot_id}`}
        >
          {uploadInfo?.status === "QUARANTINED" ? "QUARANTINED" : slotStatus}
        </span>
        {lastUpload && (
          <span style={S.muted}>
            {uploads.length} upload{uploads.length > 1 ? "s" : ""}
          </span>
        )}
      </div>

      <div
        onDragEnter={(e) => {
          e.preventDefault();
          setDrag(true);
        }}
        onDragOver={(e) => {
          e.preventDefault();
          setDrag(true);
        }}
        onDragLeave={() => setDrag(false)}
        onDrop={handleDrop}
        onClick={() => tokenReady && inputRef.current?.click()}
        style={{
          ...S.dropZone,
          borderColor: drag ? "#22d3ee" : tokenReady ? "#3a4a66" : "#7f1d1d",
          background: drag
            ? "rgba(34,211,238,0.10)"
            : tokenReady
            ? "rgba(34,211,238,0.04)"
            : "rgba(127,29,29,0.10)",
          cursor: tokenReady ? "pointer" : "not-allowed",
        }}
        data-testid={`drop-zone-${slot.slot_id}`}
      >
        {tokenReady ? (
          <>
            <div style={S.dropMain}>Glisser un fichier ici ou cliquer</div>
            <div style={S.muted}>
              Formats : {(slot.formats_acceptes || []).join(", ")} · max{" "}
              {formatBytes(slot.taille_max_octets)}
            </div>
          </>
        ) : (
          <>
            <div style={{ ...S.dropMain, color: "#fca5a5" }}>
              ⛔ Token Commandant requis
            </div>
            <div style={S.muted}>Saisir le token plus haut pour activer l'upload</div>
          </>
        )}
        <input
          ref={inputRef}
          type="file"
          style={{ display: "none" }}
          onChange={handlePick}
          accept=".gpkg,.zip,.geojson,.json,.parquet,.tif,.tiff"
          data-testid={`file-input-${slot.slot_id}`}
        />
      </div>

      {uploadInfo && (
        <div style={S.uploadInfo} data-testid={`upload-info-${slot.slot_id}`}>
          <div style={S.uploadHeader}>
            <span style={S.uploadStatus}>{uploadInfo.status}</span>
            {uploadInfo.status === "UPLOADING" && (
              <button
                onClick={() => onCancel(slot.slot_id)}
                style={S.btnCancel}
                data-testid={`upload-cancel-${slot.slot_id}`}
              >
                Annuler
              </button>
            )}
          </div>
          <div style={S.muted}>{uploadInfo.filename}</div>
          <div style={S.progressOuter}>
            <div
              style={{
                ...S.progressInner,
                width: `${uploadInfo.progress || 0}%`,
                background:
                  uploadInfo.status === "ERROR"
                    ? "#fca5a5"
                    : uploadInfo.status === "QUARANTINED"
                    ? "#fcd34d"
                    : uploadInfo.status === "LOADED"
                    ? "#22c55e"
                    : "#22d3ee",
              }}
              data-testid={`progress-bar-${slot.slot_id}`}
            />
          </div>
          <div style={S.muted}>{uploadInfo.message}</div>
          {uploadInfo.sha256 && (
            <code style={S.mono} data-testid={`sha256-${slot.slot_id}`}>
              SHA-256 {shortSha(uploadInfo.sha256)}
            </code>
          )}
          {uploadInfo.validators && (
            <ul style={S.validatorsList}>
              {uploadInfo.validators.map((v, i) => (
                <li
                  key={i}
                  style={{ color: v.passed ? "#86efac" : "#fca5a5" }}
                  data-testid={`validator-${slot.slot_id}-${v.name}`}
                >
                  {v.passed ? "✓" : "✗"} {v.name} — {v.reason}
                </li>
              ))}
            </ul>
          )}
        </div>
      )}

      {lastUpload && uploads.length > 0 && (
        <div style={S.lastUpload}>
          <div style={S.lastUploadLabel}>Dernier upload retenu :</div>
          <code style={S.mono}>{lastUpload.filename}</code>
          <div style={S.muted}>
            {formatBytes(lastUpload.size_bytes)} ·{" "}
            {shortSha(lastUpload.sha256)}
          </div>
        </div>
      )}
    </div>
  );
};

// ═══════════════════════════════════════════════════════════════════════
const S = {
  wrap: { padding: 16, background: "#0a1018", color: "#e2e8f0", fontFamily: "Inter, system-ui, sans-serif" },
  header: { borderLeft: "5px solid #f59e0b", padding: "6px 0 6px 18px", marginBottom: 16 },
  h2: { margin: 0, fontSize: 20, color: "#fef3c7", letterSpacing: "0.5px" },
  sub: { color: "#94a3b8", fontSize: 12, marginTop: 4 },
  h3: { color: "#22d3ee", fontSize: 14, margin: "12px 0 8px", textTransform: "uppercase", letterSpacing: "0.5px" },
  banner: {
    gold: { background: "linear-gradient(135deg,#78350f,#92400e)", border: "1px solid #f59e0b", color: "#fef3c7", padding: "10px 18px", borderRadius: 8, fontWeight: 700, textAlign: "center", marginBottom: 16 },
    error: { background: "rgba(239,68,68,0.15)", border: "1px solid rgba(239,68,68,0.45)", color: "#fca5a5", padding: 10, borderRadius: 6, marginBottom: 12, fontSize: 12 },
  },
  lbl: { color: "#94a3b8", fontSize: 10, textTransform: "uppercase", letterSpacing: "0.5px" },
  mono: { fontFamily: "JetBrains Mono, Menlo, monospace", fontSize: 10, color: "#94a3b8", wordBreak: "break-all" },
  muted: { color: "#94a3b8", fontSize: 11, marginTop: 2 },

  tokenCard: { background: "#111c2e", border: "1px solid #1e293b", borderRadius: 10, padding: 14, marginBottom: 16 },
  tokenHeader: { display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 8 },
  tokenStatus: { fontSize: 11, fontWeight: 700 },
  tokenRow: { display: "flex", gap: 8, marginBottom: 6 },
  tokenInput: { flex: 1, padding: "8px 12px", background: "#0a1018", border: "1px solid #3a4a66", borderRadius: 6, color: "#e2e8f0", fontFamily: "JetBrains Mono, monospace", fontSize: 12 },
  btnPrimary: { padding: "8px 14px", background: "#22d3ee", color: "#0a1018", border: "none", borderRadius: 6, fontWeight: 700, cursor: "pointer", fontSize: 12 },
  btnSecondary: { padding: "8px 14px", background: "#1e293b", color: "#94a3b8", border: "1px solid #3a4a66", borderRadius: 6, cursor: "pointer", fontSize: 12 },
  btnCancel: { padding: "4px 10px", background: "rgba(239,68,68,0.18)", color: "#fca5a5", border: "1px solid rgba(239,68,68,0.45)", borderRadius: 4, cursor: "pointer", fontSize: 10, fontWeight: 700 },

  slotsGrid: { display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(330px, 1fr))", gap: 12, marginBottom: 16 },
  slotCard: { background: "#111c2e", border: "1px solid #1e293b", borderRadius: 10, padding: 14, display: "flex", flexDirection: "column", gap: 6 },
  slotHeader: { display: "flex", justifyContent: "space-between", alignItems: "center" },
  slotTitle: { fontSize: 13, fontWeight: 700, color: "#fef3c7" },
  slotLabel: { fontSize: 12, color: "#e2e8f0" },
  slotStatusRow: { display: "flex", justifyContent: "space-between", alignItems: "center", marginTop: 4 },
  statusBadge: { padding: "2px 8px", borderRadius: 4, fontWeight: 700, fontSize: 10 },
  priorityBadge: { padding: "2px 8px", borderRadius: 4, fontWeight: 700, fontSize: 10 },

  dropZone: { marginTop: 8, padding: 18, border: "2px dashed", borderRadius: 8, textAlign: "center", transition: "all 0.2s ease" },
  dropMain: { fontWeight: 700, fontSize: 12, color: "#67e8f9", marginBottom: 4 },

  uploadInfo: { marginTop: 8, padding: 10, background: "#0a1018", border: "1px solid #1e293b", borderRadius: 6 },
  uploadHeader: { display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 4 },
  uploadStatus: { fontSize: 11, fontWeight: 700, color: "#fcd34d" },
  progressOuter: { width: "100%", height: 6, background: "#1e293b", borderRadius: 3, marginTop: 6, overflow: "hidden" },
  progressInner: { height: "100%", transition: "width 0.2s ease" },
  validatorsList: { margin: "6px 0 0", paddingLeft: 16, fontSize: 10 },

  lastUpload: { marginTop: 8, padding: 8, background: "rgba(34,197,94,0.06)", border: "1px solid rgba(34,197,94,0.25)", borderRadius: 6 },
  lastUploadLabel: { fontSize: 10, color: "#86efac", fontWeight: 700, marginBottom: 4 },

  logCard: { background: "#111c2e", border: "1px solid #1e293b", borderRadius: 10, padding: 14 },
  logScroll: { maxHeight: 220, overflowY: "auto", border: "1px solid #1e293b", borderRadius: 6, padding: 8, fontSize: 11 },
  logRow: { display: "flex", gap: 8, padding: "3px 0", borderBottom: "1px dashed #1e293b" },
  logLevel: { fontWeight: 700, minWidth: 50 },
  logSlot: { fontWeight: 700, color: "#67e8f9", minWidth: 130 },
};

export default AdminGISReceptionPanel;

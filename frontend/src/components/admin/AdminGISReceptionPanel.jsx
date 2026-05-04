/**
 * AdminGISReceptionPanel — Phase XXII (ORDRE N°43) + ORDRE N°45
 * ════════════════════════════════════════════════════════════════════════
 * COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU x3 · Ordres N°43 + N°45
 *
 * Panneau ADMIN_PREMIUM_ONLY de réception des couches GIS protégées.
 *
 * Fonctionnalités (Ordre 43) :
 *   · Drag-and-drop par slot GIS
 *   · Upload chunked XHR avec progression
 *   · Intake-status live (auto-refresh)
 *   · Gestion erreurs 401/404/422/413
 *   · Affichage SHA-256 + statut LOADED/QUARANTINE
 *   · Token Commandant en sessionStorage (sécurité par session)
 *
 * Extensions (Ordre 45) :
 *   · Section "Journal forensique" — GET /audit-log + filtres slot_id/event
 *   · Bouton "Promouvoir vers GIS_OPERATIONAL_Ω" — POST /promote
 *   · Affichage sceau_x5_final_ready, next_action, layers_status
 *
 * Endpoints utilisés :
 *   GET  /api/v30/admin-premium/gis/slots
 *   GET  /api/v30/admin-premium/gis/intake-status
 *   POST /api/v30/admin-premium/gis/upload/{slot_id}
 *   GET  /api/v30/admin-premium/gis/audit-log         (Ordre 45)
 *   POST /api/v30/admin-premium/gis/promote           (Ordre 45)
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

  // ─── ORDRE N°48 · UX déblocage token Commandant ─────────────────────
  const tokenSectionRef = useRef(null);
  const tokenInputRef = useRef(null);
  const [tokenAttention, setTokenAttention] = useState(false);

  const requestTokenFocus = useCallback(() => {
    // Scroll robuste (compte tient des conteneurs scrollables imbriqués)
    try {
      const el = tokenSectionRef.current;
      if (el) {
        // Méthode 1 : scrollIntoView (best-effort sur container parent)
        el.scrollIntoView({ behavior: "smooth", block: "center" });
        // Méthode 2 : remonter aussi tous les conteneurs scrollables ancêtres
        let parent = el.parentElement;
        while (parent && parent !== document.body) {
          const cs = window.getComputedStyle(parent);
          if (
            ["auto", "scroll"].includes(cs.overflowY) ||
            ["auto", "scroll"].includes(cs.overflow)
          ) {
            parent.scrollTo({
              top: el.offsetTop - parent.offsetTop - 60,
              behavior: "smooth",
            });
          }
          parent = parent.parentElement;
        }
        // Méthode 3 : window scroll en backup absolu
        const rect = el.getBoundingClientRect();
        window.scrollTo({
          top: window.pageYOffset + rect.top - 100,
          behavior: "smooth",
        });
      }
      setTimeout(() => tokenInputRef.current?.focus({ preventScroll: false }), 450);
    } catch {
      tokenInputRef.current?.focus();
    }
    setTokenAttention(true);
    setTimeout(() => setTokenAttention(false), 2500);
  }, []);

  // ─── ORDRE N°48-EXT · Pré-injection token via URL `?token=...` ──────
  useEffect(() => {
    try {
      const params = new URLSearchParams(window.location.search);
      const urlToken = params.get("gis_token") || params.get("token");
      if (urlToken && urlToken.length > 8) {
        sessionStorage.setItem(TOKEN_STORAGE_KEY, urlToken);
        setToken(urlToken);
        setTokenSaved(true);
        // Nettoyer l'URL pour ne pas exposer le token dans l'historique
        const url = new URL(window.location.href);
        url.searchParams.delete("gis_token");
        url.searchParams.delete("token");
        window.history.replaceState({}, "", url.pathname + url.search + url.hash);
      }
    } catch {
      /* best-effort */
    }
  }, []);

  // ─── ORDRE N°49 · Auto-validation token au montage (purge auto si invalide) ──
  // Empêche un sessionStorage corrompu de bloquer le Commandant indéfiniment.
  useEffect(() => {
    const stored = sessionStorage.getItem(TOKEN_STORAGE_KEY);
    if (!stored) return;
    let cancelled = false;
    (async () => {
      try {
        const r = await fetch(
          `${API}/api/v30/admin-premium/gis/token-check`,
          { headers: { "X-Commandant-Token": stored.trim() } }
        );
        if (cancelled) return;
        if (r.ok) {
          // Token valide → on s'assure du marquage "saved"
          setTokenSaved(true);
        } else if (r.status === 401) {
          // Token corrompu → purge automatique + alerte UX
          sessionStorage.removeItem(TOKEN_STORAGE_KEY);
          setToken("");
          setTokenSaved(false);
          setTokenTestResult({
            ok: false,
            message:
              "⚠ Token précédent invalide — purgé automatiquement. " +
              "Re-saisissez le token Commandant ci-dessous.",
          });
          appendEvent({
            level: "WARN",
            message: "Token invalide détecté en session → purge auto",
          });
        }
      } catch {
        /* réseau temporairement indisponible — silencieux */
      }
    })();
    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []); // au montage uniquement

  // ═════ ORDRE N°45 — État Journal forensique + Promote ═════
  const [auditEntries, setAuditEntries] = useState([]);
  const [auditStats, setAuditStats] = useState(null);
  const [auditFilters, setAuditFilters] = useState({ slot_id: "", event: "" });
  const [auditLoading, setAuditLoading] = useState(false);
  const [auditError, setAuditError] = useState(null);
  const [promoteResult, setPromoteResult] = useState(null);
  const [promoteLoading, setPromoteLoading] = useState(false);
  const [promoteError, setPromoteError] = useState(null);

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
    // ─── ORDRE N°48-EXT · Trim defensif (espaces/CRLF copiés-collés) ───
    const cleaned = (token || "").trim();
    if (!cleaned) return;
    sessionStorage.setItem(TOKEN_STORAGE_KEY, cleaned);
    setToken(cleaned);
    setTokenSaved(true);
    setTokenTestResult(null);
    appendEvent({
      level: "INFO",
      message: `Token Commandant enregistré (${cleaned.length} chars, sessionStorage)`,
    });
  };

  const handleClearToken = () => {
    sessionStorage.removeItem(TOKEN_STORAGE_KEY);
    setToken("");
    setTokenSaved(false);
    setTokenTestResult(null);
    appendEvent({ level: "WARN", message: "Token Commandant effacé" });
  };

  // ─── ORDRE N°48-EXT · Test non-destructif du token ─────────────────
  const [tokenTestResult, setTokenTestResult] = useState(null);
  const [tokenTesting, setTokenTesting] = useState(false);
  const handleTestToken = useCallback(async () => {
    const cleaned = (token || "").trim();
    if (!cleaned) {
      setTokenTestResult({ ok: false, message: "Saisissez un token d'abord" });
      return;
    }
    setTokenTesting(true);
    setTokenTestResult(null);
    // Cache-bust fort pour ignorer tout cache navigateur/SW intermédiaire
    const url = `${API}/api/v30/admin-premium/gis/token-check?_=${Date.now()}`;
    try {
      const r = await fetch(url, {
        method: "GET",
        cache: "no-store",
        headers: {
          "X-Commandant-Token": cleaned,
          "Cache-Control": "no-cache, no-store, must-revalidate",
          Pragma: "no-cache",
        },
      });
      const d = await r.json().catch(() => ({}));
      if (r.ok && d.ok) {
        setTokenTestResult({
          ok: true,
          message: `✓ Token valide (${d.token_length} chars) · ${url}`,
        });
        // Auto-save sur test réussi
        sessionStorage.setItem(TOKEN_STORAGE_KEY, cleaned);
        setToken(cleaned);
        setTokenSaved(true);
      } else {
        setTokenTestResult({
          ok: false,
          message: `✗ HTTP ${r.status} · ${
            d.detail || "Token rejeté"
          } · URL: ${url}`,
        });
      }
    } catch (e) {
      setTokenTestResult({
        ok: false,
        message: `✗ Réseau : ${String(e.message || e)} · URL: ${url}`,
      });
    } finally {
      setTokenTesting(false);
    }
  }, [token]);

  // ─── ORDRE N°51-DIAG · Diagnostic global multi-endpoints ──────────
  const [diagResult, setDiagResult] = useState(null);
  const [diagRunning, setDiagRunning] = useState(false);
  const handleRunDiagnostic = useCallback(async () => {
    setDiagRunning(true);
    setDiagResult(null);
    const cleaned = (token || "").trim();
    const ts = Date.now();
    const tests = [
      {
        label: "Slots publics",
        url: `${API}/api/v30/admin-premium/gis/slots?_=${ts}`,
        opts: { cache: "no-store" },
      },
      {
        label: "Intake-status",
        url: `${API}/api/v30/admin-premium/gis/intake-status?_=${ts}`,
        opts: { cache: "no-store" },
      },
      {
        label: "Token-check (REQUIS)",
        url: `${API}/api/v30/admin-premium/gis/token-check?_=${ts}`,
        opts: {
          cache: "no-store",
          headers: { "X-Commandant-Token": cleaned || "(absent)" },
        },
      },
      {
        label: "Audit-log (REQUIS)",
        url: `${API}/api/v30/admin-premium/gis/audit-log?limit=1&_=${ts}`,
        opts: {
          cache: "no-store",
          headers: { "X-Commandant-Token": cleaned || "(absent)" },
        },
      },
    ];
    const results = [];
    for (const t of tests) {
      try {
        const r = await fetch(t.url, t.opts);
        results.push({
          label: t.label,
          status: r.status,
          ok: r.ok,
          url: t.url.replace(API, ""),
        });
      } catch (e) {
        results.push({
          label: t.label,
          status: 0,
          ok: false,
          url: t.url.replace(API, ""),
          error: String(e.message || e),
        });
      }
    }
    setDiagResult({
      backend_url: API,
      timestamp_utc: new Date().toISOString(),
      tests: results,
    });
    setDiagRunning(false);
  }, [token]);

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

      // ─── ORDRE N°50 · Bascule chunked auto si > seuil Cloudflare ────
      // Cloudflare/proxies limitent à 100 MB. On découpe à 50 MB pour
      // garder une marge. Au-dessus → mode chunked résilient.
      const CHUNK_THRESHOLD = 50 * 1024 * 1024; // 50 MB
      if (file.size > CHUNK_THRESHOLD) {
        // ─── ORDRE N°52-EXT VOIE A · Réutilisation upload_id si retry ──
        // Si une session est en ERROR pour ce slot avec le même filename,
        // on réutilise le upload_id pour bénéficier du resume serveur
        // (skip chunks déjà reçus + retry exponentiel sur 5xx).
        const prev = uploadState[slotId];
        const reuseUploadId =
          prev &&
          prev.status === "ERROR" &&
          prev.uploadId &&
          prev.filename === file.name
            ? prev.uploadId
            : undefined;
        return performChunkedUpload(slotId, file, {
          uploadId: reuseUploadId,
        });
      }
      return performStandardUpload(slotId, file);
    },
    // performChunkedUpload et performStandardUpload sont définis ci-dessous
    // avec leurs propres dépendances → useCallback ne dépend que de token.
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [token, uploadState]
  );

  // ─── ORDRE N°50 · Upload mono-fichier (≤ 50 MB) ────────────────────
  const performStandardUpload = useCallback(
    (slotId, file) => {
      const xhr = new XMLHttpRequest();
      xhrRefs.current[slotId] = xhr;
      const fd = new FormData();
      fd.append("file", file, file.name);

      xhr.open(
        "POST",
        `${API}/api/v30/admin-premium/gis/upload/${encodeURIComponent(slotId)}`,
        true
      );
      xhr.setRequestHeader("X-Commandant-Token", (token || "").trim());

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
          // ─── ORDRE N°48-EXT · Codes d'erreur explicites ───
          const codeLabel =
            xhr.status === 401
              ? "401 · Token invalide / refusé"
              : xhr.status === 404
              ? "404 · Endpoint absent (backend en redémarrage ?)"
              : xhr.status === 413
              ? "413 · Fichier trop volumineux"
              : xhr.status === 400
              ? "400 · Nom de fichier invalide"
              : xhr.status === 502 || xhr.status === 503 || xhr.status === 504
              ? `${xhr.status} · Backend indisponible · Réessayer dans 10s`
              : `HTTP ${xhr.status}`;
          // Conseil de retry si erreur transitoire
          const retryHint =
            [404, 502, 503, 504, 0].includes(xhr.status)
              ? " · ⚠ Vérifiez que le backend est UP (rafraîchir la page) puis réessayez l'upload"
              : "";
          setUploadState((s) => ({
            ...s,
            [slotId]: {
              progress: 0,
              status: "ERROR",
              filename: file.name,
              sizeBytes: file.size,
              message: `${codeLabel} — ${payload.detail || ""}${retryHint}`,
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

  // ─── ORDRE N°50 · Upload chunked résilient (> 50 MB) ──────────────
  // Découpe le fichier en chunks de 50 MB et POST séquentiel sur
  // /upload-chunk/{slot_id} avec headers de session. Le dernier chunk
  // (X-Final-Chunk: true) déclenche le reassemblage + validation.
  //
  // ORDRE N°52-EXT (VOIE A · directive 4) : durcissement ciblé
  //   · auto-resume avant envoi (skip chunks déjà reçus côté serveur)
  //   · retry exponentiel sur 5xx (max 5 tentatives par chunk)
  //   · UI expose upload_id, last_successful_chunk_index, error_phase
  //   · upload_id réutilisable sur 5xx — pas de nouvelle session
  const performChunkedUpload = useCallback(
    async (slotId, file, opts = {}) => {
      const CHUNK_SIZE = 50 * 1024 * 1024; // 50 MB par chunk
      const total = Math.ceil(file.size / CHUNK_SIZE);
      // Si resume=true et opts.uploadId fourni, on réutilise ; sinon on en
      // génère un frais (UUIDv4-like compatible regex ^[A-Za-z0-9._-]{8,64}$)
      const uploadId =
        opts.uploadId ||
        Date.now().toString(36) +
          "-" +
          Math.random().toString(16).slice(2, 10);

      // ─── Auto-resume préalable : récupérer chunks_missing[] ─────────
      let chunksToSend = Array.from({ length: total }, (_, i) => i);
      let lastSuccessfulIdx = -1;
      try {
        const resumeUrl =
          `${API}/api/v30/admin-premium/gis/upload-chunk/` +
          `${encodeURIComponent(slotId)}/resume/${encodeURIComponent(uploadId)}`;
        const rResume = await fetch(resumeUrl, {
          headers: { "X-Commandant-Token": (token || "").trim() },
        });
        if (rResume.ok) {
          const dResume = await rResume.json();
          const missing = Array.isArray(dResume.chunks_missing)
            ? dResume.chunks_missing
            : null;
          if (
            missing &&
            dResume.chunks_total === total &&
            dResume.chunks_received_count > 0
          ) {
            chunksToSend = missing;
            lastSuccessfulIdx =
              typeof dResume.chunks_received_count === "number"
                ? dResume.chunks_received_count - 1
                : -1;
            appendEvent({
              level: "INFO",
              slotId,
              message: `RESUME · upload_id=${uploadId} · ${dResume.chunks_received_count}/${total} déjà reçus · ${missing.length} chunks à envoyer`,
            });
          }
        }
      } catch (_resumeErr) {
        // resume échec → on envoie tout (idempotent côté backend)
      }

      setUploadState((s) => ({
        ...s,
        [slotId]: {
          progress: 0,
          status: "UPLOADING",
          filename: file.name,
          sizeBytes: file.size,
          message: `Mode chunked · ${total} chunks de ~50 MB · démarrage…`,
          chunked: true,
          chunksTotal: total,
          uploadId,
          lastSuccessfulIdx,
          chunksToSend: chunksToSend.length,
          errorPhase: null,
        },
      }));
      appendEvent({
        level: "INFO",
        slotId,
        message: `Upload chunked démarré · ${file.name} · ${formatBytes(file.size)} · ${total} chunks · upload_id=${uploadId}`,
      });

      const headersBase = {
        "X-Commandant-Token": (token || "").trim(),
        "X-Upload-Id": uploadId,
        "X-Chunks-Total": String(total),
        "X-Original-Filename": file.name,
        "X-Total-Size": String(file.size),
      };

      let lastResponse = null;
      const sleep = (ms) => new Promise((res) => setTimeout(res, ms));

      // ─── Helper retry avec backoff exponentiel sur 5xx ──────────────
      const sendChunkWithRetry = async (i) => {
        const start = i * CHUNK_SIZE;
        const end = Math.min(start + CHUNK_SIZE, file.size);
        const blob = file.slice(start, end);

        const MAX_RETRIES = 5;
        let attempt = 0;
        let delayMs = 1000;
        while (attempt <= MAX_RETRIES) {
          attempt += 1;
          const fd = new FormData();
          fd.append("file", blob, file.name);
          let r = null;
          let payload = {};
          try {
            r = await fetch(
              `${API}/api/v30/admin-premium/gis/upload-chunk/${encodeURIComponent(slotId)}`,
              {
                method: "POST",
                headers: {
                  ...headersBase,
                  "X-Chunk-Index": String(i),
                  ...(i === total - 1 ? { "X-Final-Chunk": "true" } : {}),
                },
                body: fd,
              }
            );
            payload = await r.json().catch(() => ({}));
          } catch (netErr) {
            // Erreur réseau → traitée comme 5xx réessayable
            if (attempt > MAX_RETRIES) {
              return {
                ok: false,
                status: 0,
                payload: { detail: String(netErr.message || netErr) },
                phase: "PROXY_OR_NETWORK_BEFORE_BACKEND",
              };
            }
            const jitter = Math.floor(Math.random() * 500);
            const wait = Math.min(delayMs + jitter, 30000);
            appendEvent({
              level: "WARN",
              slotId,
              message: `Réseau chunk ${i}/${total} · attempt ${attempt}/${MAX_RETRIES + 1} · retry dans ${wait}ms`,
            });
            await sleep(wait);
            delayMs *= 2;
            continue;
          }

          if (r.status >= 500 && r.status <= 599 && attempt <= MAX_RETRIES) {
            const jitter = Math.floor(Math.random() * 500);
            const wait = Math.min(delayMs + jitter, 30000);
            appendEvent({
              level: "WARN",
              slotId,
              message: `HTTP ${r.status} chunk ${i}/${total} · attempt ${attempt}/${MAX_RETRIES + 1} · retry dans ${wait}ms (proxy/réseau)`,
            });
            await sleep(wait);
            delayMs *= 2;
            continue;
          }

          // 200 OK ou erreur non-5xx → retour
          return {
            ok: r.ok,
            status: r.status,
            payload,
            phase:
              r.status >= 500
                ? "PROXY_OR_NETWORK_BEFORE_BACKEND"
                : r.status >= 400
                ? "BACKEND_ROUTER_VALIDATION_OR_ASSEMBLY"
                : "OK",
          };
        }
        return {
          ok: false,
          status: 599,
          payload: { detail: "Max retries 5xx épuisés" },
          phase: "PROXY_OR_NETWORK_BEFORE_BACKEND",
        };
      };

      let sentCount = 0;
      let orphanRestartDetected = false;
      for (const i of chunksToSend) {
        const res = await sendChunkWithRetry(i);
        if (!res.ok) {
          // ─── ORDRE N°52-EXT · Détection session orpheline pod-restart ──
          const isOrphan =
            res.status === 409 &&
            typeof res.payload?.detail === "string" &&
            res.payload.detail.includes("SESSION_ORPHANED_POD_RESTART");
          if (isOrphan && !orphanRestartDetected) {
            orphanRestartDetected = true;
            appendEvent({
              level: "WARN",
              slotId,
              message: `Session orpheline détectée (pod restart pendant upload) · upload_id=${uploadId} abandonné · redémarrage auto avec nouvel upload_id depuis chunk 0`,
            });
            setUploadState((s) => ({
              ...s,
              [slotId]: {
                ...(s[slotId] || {}),
                status: "UPLOADING",
                message:
                  "Pod redémarré · régénération upload_id · reprise depuis chunk 0...",
                errorPhase: "SESSION_ORPHANED_POD_RESTART",
              },
            }));
            // Relancer avec un upload_id frais (pas de réutilisation)
            return performChunkedUpload(slotId, file, {});
          }
          const codeLabel =
            res.status === 401
              ? "401 · Token invalide"
              : res.status === 413
              ? "413 · Chunk trop volumineux (réduire CHUNK_SIZE)"
              : res.status === 409
              ? "409 · Chunks incomplets ou session orpheline"
              : `HTTP ${res.status}`;
          setUploadState((s) => ({
            ...s,
            [slotId]: {
              ...(s[slotId] || {}),
              progress: Math.round((sentCount / chunksToSend.length) * 100),
              status: "ERROR",
              filename: file.name,
              sizeBytes: file.size,
              message: `${codeLabel} (chunk ${i}/${total}) — ${res.payload?.detail || ""}`,
              chunked: true,
              uploadId,
              lastSuccessfulIdx,
              errorPhase: res.phase,
            },
          }));
          appendEvent({
            level: "ERROR",
            slotId,
            message: `Chunk ${i}/${total} échoué · ${codeLabel} · phase=${res.phase} · upload_id=${uploadId} (réutilisable)`,
          });
          return;
        }
        lastResponse = res.payload;
        lastSuccessfulIdx = Math.max(lastSuccessfulIdx, i);
        sentCount += 1;
        const overallProgress =
          i === total - 1 ? 99 : Math.round((sentCount / chunksToSend.length) * 95);
        setUploadState((s) => ({
          ...s,
          [slotId]: {
            ...(s[slotId] || {}),
            progress: overallProgress,
            status: "UPLOADING",
            filename: file.name,
            sizeBytes: file.size,
            message: `Chunked · ${sentCount}/${chunksToSend.length} envoyés · last_idx=${lastSuccessfulIdx}/${total - 1}`,
            chunked: true,
            chunksTotal: total,
            chunksReceived: sentCount,
            lastSuccessfulIdx,
            uploadId,
            errorPhase: null,
          },
        }));
      }

      // ─── Dernier chunk → lastResponse contient le payload final ───
      if (lastResponse && lastResponse.passed) {
        setUploadState((s) => ({
          ...s,
          [slotId]: {
            progress: 100,
            status: "LOADED",
            filename: file.name,
            sizeBytes: file.size,
            sha256: lastResponse.sha256,
            message: `LOADED · chunked (${total}) · validators OK`,
            validators: lastResponse.validators,
            chunked: true,
            chunksTotal: total,
            uploadId,
            lastSuccessfulIdx: total - 1,
          },
        }));
        appendEvent({
          level: "INFO",
          slotId,
          message: `LOADED chunked · ${file.name} · ${shortSha(lastResponse.sha256)} · ${total} chunks`,
        });
      } else if (lastResponse && !lastResponse.passed) {
        setUploadState((s) => ({
          ...s,
          [slotId]: {
            progress: 100,
            status: "QUARANTINED",
            filename: file.name,
            sizeBytes: file.size,
            sha256: lastResponse.sha256,
            message: "QUARANTAINE · validators échoués (post-assemblage)",
            validators: lastResponse.validators,
            chunked: true,
            uploadId,
          },
        }));
        appendEvent({
          level: "ERROR",
          slotId,
          message: `QUARANTAINE chunked · ${file.name}`,
        });
      }
      fetchIntake();
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

  // ═════ ORDRE N°45 — Journal forensique (GET /audit-log) ═════
  const fetchAuditLog = useCallback(async () => {
    if (!token) {
      setAuditError("Token Commandant requis pour lire le journal forensique");
      return;
    }
    setAuditLoading(true);
    setAuditError(null);
    try {
      const params = new URLSearchParams({ limit: "20" });
      if (auditFilters.slot_id) params.set("slot_id", auditFilters.slot_id);
      if (auditFilters.event) params.set("event", auditFilters.event);
      const r = await fetch(
        `${API}/api/v30/admin-premium/gis/audit-log?${params.toString()}`,
        { headers: { "X-Commandant-Token": (token || "").trim() } }
      );
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      const d = await r.json();
      setAuditEntries(d.entries || []);
      setAuditStats(d.stats || null);
      appendEvent({
        level: "INFO",
        message: `Audit-log lu (${(d.entries || []).length} entrées)`,
      });
    } catch (e) {
      setAuditError(e.message);
    } finally {
      setAuditLoading(false);
    }
  }, [token, auditFilters, appendEvent]);

  // ═════ ORDRE N°45 — Promotion vers GIS_OPERATIONAL_Ω ═════
  const runPromote = useCallback(async () => {
    if (!token) {
      setPromoteError("Token Commandant requis pour la promotion");
      return;
    }
    setPromoteLoading(true);
    setPromoteError(null);
    try {
      const r = await fetch(`${API}/api/v30/admin-premium/gis/promote`, {
        method: "POST",
        headers: { "X-Commandant-Token": (token || "").trim() },
      });
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      const d = await r.json();
      setPromoteResult(d);
      appendEvent({
        level: d.sceau_x5_final_ready ? "INFO" : "WARN",
        message: `Promote · status=${d.compute_corridors_gis?.status} · next=${d.next_action}`,
      });
    } catch (e) {
      setPromoteError(e.message);
    } finally {
      setPromoteLoading(false);
    }
  }, [token, appendEvent]);

  // Auto-load audit log dès qu'un token est enregistré
  useEffect(() => {
    if (tokenSaved && token) {
      fetchAuditLog();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [tokenSaved]);

  const stats = intake?.stats || { total_slots: 0, loaded: 0, absent: 0 };

  return (
    <div style={S.wrap} data-testid="gis-reception-panel">
      {/* ─── ORDRE N°48 · Keyframes pour animation pulsante token ─── */}
      <style>{`
        @keyframes gisTokenPulse {
          0%   { box-shadow: 0 0 0 4px rgba(251,191,36,0.20), 0 0 24px rgba(251,191,36,0.30); }
          50%  { box-shadow: 0 0 0 10px rgba(251,191,36,0.45), 0 0 36px rgba(251,191,36,0.65); }
          100% { box-shadow: 0 0 0 4px rgba(251,191,36,0.20), 0 0 24px rgba(251,191,36,0.30); }
        }
      `}</style>
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

      <section
        ref={tokenSectionRef}
        style={{
          ...S.tokenCard,
          ...(tokenAttention ? S.tokenCardAttention : {}),
          ...(!tokenSaved ? S.tokenCardEmpty : {}),
        }}
        data-testid="token-section"
      >
        <div style={S.tokenHeader}>
          <span style={S.lbl}>
            X-COMMANDANT-TOKEN {!tokenSaved && <span style={S.tokenBadgeRequired}>· REQUIS POUR UPLOAD</span>}
          </span>
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
            ref={tokenInputRef}
            type="password"
            value={token}
            onChange={(e) => {
              setToken(e.target.value);
              setTokenSaved(false);
            }}
            placeholder="Saisir le token Commandant…"
            style={{
              ...S.tokenInput,
              ...(tokenAttention ? S.tokenInputAttention : {}),
            }}
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
            onClick={handleTestToken}
            disabled={!token || tokenTesting}
            style={S.btnSecondary}
            data-testid="gis-reception-test-token-btn"
            title="Vérifie que le token correspond à celui attendu côté backend (non-destructif)"
          >
            {tokenTesting ? "..." : "🔍 Tester"}
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
        {tokenTestResult && (
          <div
            style={{
              ...S.muted,
              marginTop: 8,
              padding: "6px 10px",
              borderRadius: 4,
              background: tokenTestResult.ok
                ? "rgba(134,239,172,0.10)"
                : "rgba(252,165,165,0.10)",
              border: `1px solid ${
                tokenTestResult.ok
                  ? "rgba(134,239,172,0.4)"
                  : "rgba(252,165,165,0.4)"
              }`,
              color: tokenTestResult.ok ? "#86efac" : "#fca5a5",
              fontWeight: 600,
              fontFamily: "JetBrains Mono, Menlo, monospace",
            }}
            data-testid="gis-reception-token-test-result"
          >
            {tokenTestResult.message}
          </div>
        )}

        {/* ─── ORDRE N°51-DIAG · Diagnostic complet multi-endpoints ─── */}
        <div style={{ marginTop: 10 }}>
          <button
            onClick={handleRunDiagnostic}
            disabled={diagRunning}
            style={{
              ...S.btnSecondary,
              borderColor: "rgba(168,85,247,0.5)",
              color: "#c4b5fd",
              fontSize: 11,
            }}
            data-testid="gis-reception-diag-btn"
            title="Pingue 4 endpoints en série pour identifier où le 404 surgit"
          >
            {diagRunning ? "🩺 Diagnostic..." : "🩺 Diagnostic complet"}
          </button>
        </div>

        {diagResult && (
          <div
            style={{
              marginTop: 8,
              padding: "8px 10px",
              borderRadius: 4,
              background: "rgba(168,85,247,0.06)",
              border: "1px solid rgba(168,85,247,0.35)",
              color: "#e9d5ff",
              fontFamily: "JetBrains Mono, Menlo, monospace",
              fontSize: 10,
            }}
            data-testid="gis-reception-diag-result"
          >
            <div style={{ marginBottom: 4, fontWeight: 700 }}>
              Backend cible : <code>{diagResult.backend_url}</code>
            </div>
            <div style={{ marginBottom: 6, opacity: 0.7 }}>
              {diagResult.timestamp_utc}
            </div>
            {diagResult.tests.map((t, i) => (
              <div
                key={i}
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  gap: 8,
                  padding: "3px 0",
                  borderBottom: "1px dashed rgba(168,85,247,0.2)",
                }}
              >
                <span>
                  {t.ok ? "🟢" : "🔴"} {t.label}
                </span>
                <span
                  style={{
                    color: t.ok ? "#86efac" : "#fca5a5",
                    fontWeight: 700,
                  }}
                >
                  HTTP {t.status}
                </span>
              </div>
            ))}
            <div style={{ marginTop: 6, opacity: 0.6, fontSize: 9 }}>
              Si tous 🟢 → backend OK. Si 404 isolé → mauvais URL côté client.
              Si 401 sur token-check/audit-log → token absent ou invalide.
            </div>
          </div>
        )}
        <div style={S.muted}>
          Stockage en <code>sessionStorage</code> uniquement (jamais en
          localStorage). Le token reste sur ce navigateur, sur cette session.
          {!tokenSaved && (
            <>
              {" · "}
              <span style={{ color: "#fcd34d", fontWeight: 700 }}>
                Astuce : ouvrez l'URL avec
                <code style={S.inlineCode}>?token=VOTRE_TOKEN</code>
                pour pré-remplir automatiquement.
              </span>
            </>
          )}
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
            onRequestTokenFocus={requestTokenFocus}
          />
        ))}
      </section>

      {/* ═══ ORDRE N°45 — Section Promotion vers GIS_OPERATIONAL_Ω ═══ */}
      <section style={S.promoteCard} data-testid="gis-promote-section">
        <div style={S.promoteHeader}>
          <h3 style={S.h3}>Promotion vers GIS_OPERATIONAL_Ω</h3>
          <button
            onClick={runPromote}
            disabled={!tokenSaved || promoteLoading}
            style={{
              ...S.btnPromote,
              opacity: !tokenSaved || promoteLoading ? 0.5 : 1,
              cursor: !tokenSaved || promoteLoading ? "not-allowed" : "pointer",
            }}
            data-testid="gis-promote-btn"
          >
            {promoteLoading ? "Évaluation…" : "Promouvoir"}
          </button>
        </div>
        {promoteError && (
          <div style={S.banner.error} data-testid="gis-promote-error">
            ⚠ {promoteError}
          </div>
        )}
        {!promoteResult && !promoteError && (
          <div style={S.muted}>
            Cliquer pour évaluer <code>compute_corridors_gis()</code> à partir
            de l'état réel des couches LOADED.
          </div>
        )}
        {promoteResult && (
          <div style={S.promoteResult} data-testid="gis-promote-result">
            <div style={S.promoteRow}>
              <span style={S.lbl}>compute_status</span>
              <code
                style={{
                  ...S.mono,
                  color:
                    promoteResult.compute_corridors_gis?.status === "OPERATIONAL"
                      ? "#86efac"
                      : "#fcd34d",
                }}
                data-testid="promote-compute-status"
              >
                {promoteResult.compute_corridors_gis?.status}
              </code>
            </div>
            <div style={S.promoteRow}>
              <span style={S.lbl}>engine_layers</span>
              <code style={S.mono}>
                {promoteResult.engine_layers_status?.loaded}/
                {promoteResult.engine_layers_status?.total} (
                {promoteResult.engine_layers_status?.global_status})
              </code>
            </div>
            <div style={S.promoteRow}>
              <span style={S.lbl}>intake_loaded</span>
              <code style={S.mono}>
                {promoteResult.intake_loaded_slots}/
                {promoteResult.intake_total_slots}
              </code>
            </div>
            <div style={S.promoteRow}>
              <span style={S.lbl}>anti_generique_pass</span>
              <code style={S.mono}>
                {String(
                  promoteResult.compute_corridors_gis?.anti_generique_pass
                )}
              </code>
            </div>
            <div style={S.promoteRow}>
              <span style={S.lbl}>sceau_x5_final_ready</span>
              <code
                style={{
                  ...S.mono,
                  color: promoteResult.sceau_x5_final_ready
                    ? "#86efac"
                    : "#fbbf24",
                  fontWeight: 700,
                }}
                data-testid="promote-x5-ready"
              >
                {String(promoteResult.sceau_x5_final_ready)}
              </code>
            </div>
            <div style={S.promoteRow}>
              <span style={S.lbl}>next_action</span>
              <code
                style={{ ...S.mono, color: "#67e8f9" }}
                data-testid="promote-next-action"
              >
                {promoteResult.next_action}
              </code>
            </div>
            {promoteResult.compute_corridors_gis?.missing_layers &&
              promoteResult.compute_corridors_gis.missing_layers.length > 0 && (
                <div style={S.muted}>
                  Couches manquantes :{" "}
                  {promoteResult.compute_corridors_gis.missing_layers.join(", ")}
                </div>
              )}
          </div>
        )}
      </section>

      {/* ═══ ORDRE N°45 — Section Journal forensique ═══ */}
      <section style={S.auditCard} data-testid="gis-audit-section">
        <div style={S.auditHeader}>
          <h3 style={S.h3}>Journal forensique GIS</h3>
          <span style={S.lbl}>
            {auditStats
              ? `${auditStats.total_events} évts · rétention ${auditStats.retention_days}j`
              : "—"}
          </span>
        </div>
        <div style={S.auditFilters}>
          <select
            value={auditFilters.slot_id}
            onChange={(e) =>
              setAuditFilters((f) => ({ ...f, slot_id: e.target.value }))
            }
            style={S.select}
            data-testid="audit-filter-slot"
          >
            <option value="">— Tous les slots —</option>
            {slots.map((s) => (
              <option key={s.slot_id} value={s.slot_id}>
                {s.slot_id}
              </option>
            ))}
          </select>
          <select
            value={auditFilters.event}
            onChange={(e) =>
              setAuditFilters((f) => ({ ...f, event: e.target.value }))
            }
            style={S.select}
            data-testid="audit-filter-event"
          >
            <option value="">— Tous les évènements —</option>
            <option value="UPLOAD_LOADED">UPLOAD_LOADED</option>
            <option value="UPLOAD_QUARANTINED">UPLOAD_QUARANTINED</option>
            <option value="UPLOAD_ERROR">UPLOAD_ERROR</option>
          </select>
          <button
            onClick={fetchAuditLog}
            disabled={!tokenSaved || auditLoading}
            style={{
              ...S.btnPrimary,
              opacity: !tokenSaved || auditLoading ? 0.5 : 1,
              cursor: !tokenSaved || auditLoading ? "not-allowed" : "pointer",
            }}
            data-testid="audit-refresh-btn"
          >
            {auditLoading ? "Lecture…" : "Rafraîchir"}
          </button>
        </div>
        {auditError && (
          <div style={S.banner.error} data-testid="gis-audit-error">
            ⚠ {auditError}
          </div>
        )}
        <div style={S.auditScroll}>
          {auditEntries.length === 0 && !auditLoading && (
            <div style={S.muted}>
              {tokenSaved
                ? "Aucun évènement (filtres trop stricts ou pipeline vide)."
                : "Saisir le token Commandant pour charger le journal."}
            </div>
          )}
          {auditEntries.map((e, i) => (
            <div
              key={i}
              style={{
                ...S.auditRow,
                borderLeft: `3px solid ${
                  e.event === "UPLOAD_LOADED"
                    ? "#22c55e"
                    : e.event === "UPLOAD_QUARANTINED"
                    ? "#fbbf24"
                    : "#fb7185"
                }`,
              }}
              data-testid={`audit-entry-${i}`}
            >
              <code style={S.mono}>{e.ts_utc}</code>
              <span
                style={{
                  ...S.auditEvent,
                  color:
                    e.event === "UPLOAD_LOADED"
                      ? "#86efac"
                      : e.event === "UPLOAD_QUARANTINED"
                      ? "#fcd34d"
                      : "#fca5a5",
                }}
              >
                {e.event}
              </span>
              <span style={S.auditSlot}>{e.slot_id}</span>
              <span style={{ flex: 1, fontSize: 11 }}>{e.filename}</span>
              <code style={S.mono}>HTTP {e.http_code}</code>
              <code style={S.mono}>{shortSha(e.sha256)}</code>
              <code style={S.mono}>{e.client_ip}</code>
            </div>
          ))}
        </div>
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
  onRequestTokenFocus,
}) => {
  const [drag, setDrag] = useState(false);
  const inputRef = useRef(null);

  const handleDrop = useCallback(
    (e) => {
      e.preventDefault();
      e.stopPropagation();
      setDrag(false);
      if (!tokenReady) {
        onRequestTokenFocus?.();
        return;
      }
      const files = Array.from(e.dataTransfer.files || []);
      if (files.length === 0) return;
      // ORDRE N°46 · Multi-upload : envoi séquentiel pour FORET_MFFP_Ω
      if (slot.multi_upload) {
        files.forEach((f) => onUpload(slot.slot_id, f));
      } else {
        onUpload(slot.slot_id, files[0]);
      }
    },
    [slot.slot_id, slot.multi_upload, onUpload, tokenReady, onRequestTokenFocus]
  );

  const handlePick = useCallback(
    (e) => {
      const files = Array.from(e.target.files || []);
      if (files.length === 0) {
        e.target.value = "";
        return;
      }
      if (slot.multi_upload) {
        files.forEach((f) => onUpload(slot.slot_id, f));
      } else {
        onUpload(slot.slot_id, files[0]);
      }
      e.target.value = "";
    },
    [slot.slot_id, slot.multi_upload, onUpload]
  );

  // ─── ORDRE N°48 · Click trombone sans token → scroll & pulse ────
  const handleTromboneClick = useCallback(
    (e) => {
      e.stopPropagation();
      if (tokenReady) {
        inputRef.current?.click();
      } else {
        onRequestTokenFocus?.();
      }
    },
    [tokenReady, onRequestTokenFocus]
  );

  const handleDropZoneClick = useCallback(() => {
    if (tokenReady) {
      inputRef.current?.click();
    } else {
      onRequestTokenFocus?.();
    }
  }, [tokenReady, onRequestTokenFocus]);

  const sBadge =
    STATUS_BADGE[
      uploadInfo?.status === "QUARANTINED"
        ? "QUARANTINED"
        : slotStatus
    ] || STATUS_BADGE.ABSENT;
  const pBadge = PRIO_BADGE[slot.priority] || PRIO_BADGE.P2_OPTIONNELLE;
  const lastUpload = uploads[uploads.length - 1];

  // ─── ORDRE N°46 · Multi-upload (VOIE B tuiles régionales) ───
  const isMulti = Boolean(slot.multi_upload);
  const filesLoadedCount = uploads.filter((u) => u.passed).length;
  const filesMax = slot.files_max || 1;
  // Calcul simple du composite SHA-256 côté client (affichage seulement)
  const compositeFromUploads = uploads
    .filter((u) => u.passed && u.sha256)
    .map((u) => u.sha256)
    .sort()
    .join("\n");

  return (
    <div
      style={S.slotCard}
      data-testid={`slot-card-${slot.slot_id}`}
    >
      <div style={S.slotHeader}>
        <div style={S.slotTitle}>{slot.slot_id}</div>
        <div style={{ display: "flex", gap: 6, alignItems: "center" }}>
          <button
            onClick={handleTromboneClick}
            style={{
              ...S.trombonneBtn,
              opacity: tokenReady ? 1 : 0.65,
              cursor: "pointer",
              ...(tokenReady ? {} : S.trombonneBtnDisabled),
            }}
            data-testid={`trombone-btn-${slot.slot_id}`}
            title={
              tokenReady
                ? isMulti
                  ? "Joindre une ou plusieurs tuiles"
                  : "Joindre un fichier"
                : "Cliquer pour saisir le Token Commandant en haut"
            }
          >
            📎{isMulti ? "+" : ""}
          </button>
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
      </div>

      <div style={S.slotLabel}>{slot.label}</div>
      <div style={S.muted}>
        {slot.organisme} · {slot.format_recommandé}
      </div>

      {/* ─── ORDRE N°46 · Bandeau VOIE B multi-upload ─────────── */}
      {isMulti && (
        <div
          style={S.voieBBanner}
          data-testid={`multi-upload-banner-${slot.slot_id}`}
        >
          VOIE_B · TUILES RÉGIONALES · {filesLoadedCount}/{filesMax} tuiles
          chargées
        </div>
      )}

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
        onClick={handleDropZoneClick}
        style={{
          ...S.dropZone,
          borderColor: drag ? "#22d3ee" : tokenReady ? "#3a4a66" : "#7f1d1d",
          background: drag
            ? "rgba(34,211,238,0.10)"
            : tokenReady
            ? "rgba(34,211,238,0.04)"
            : "rgba(127,29,29,0.10)",
          cursor: "pointer",
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
            <div style={{ ...S.muted, color: "#fcd34d" }}>
              Cliquer ici pour saisir le token (champ tout en haut) ↑
            </div>
          </>
        )}
        <input
          ref={inputRef}
          type="file"
          multiple={isMulti}
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
          {/* ─── ORDRE N°52-EXT VOIE A · Affichage forensique chunked ─── */}
          {uploadInfo.chunked && uploadInfo.uploadId && (
            <div
              style={{
                marginTop: 6,
                padding: "6px 8px",
                background: "rgba(34, 211, 238, 0.08)",
                border: "1px solid rgba(34, 211, 238, 0.3)",
                borderRadius: 4,
                fontSize: 11,
                lineHeight: 1.5,
              }}
              data-testid={`chunked-forensic-${slot.slot_id}`}
            >
              <div>
                <span style={S.lbl}>upload_id</span>{" "}
                <code style={S.monoMini}>{uploadInfo.uploadId}</code>
              </div>
              <div>
                <span style={S.lbl}>last_successful_chunk_index</span>{" "}
                <code style={S.monoMini}>
                  {uploadInfo.lastSuccessfulIdx ?? -1} /{" "}
                  {(uploadInfo.chunksTotal ?? 0) - 1}
                </code>
              </div>
              {uploadInfo.errorPhase && (
                <div>
                  <span style={S.lbl}>error_phase</span>{" "}
                  <code
                    style={{
                      ...S.monoMini,
                      color:
                        uploadInfo.errorPhase ===
                        "PROXY_OR_NETWORK_BEFORE_BACKEND"
                          ? "#fcd34d"
                          : "#fca5a5",
                    }}
                  >
                    {uploadInfo.errorPhase}
                  </code>
                </div>
              )}
              {uploadInfo.status === "ERROR" && (
                <div style={{ marginTop: 4, color: "#a7f3d0" }}>
                  ↻ Le upload_id ci-dessus est <b>réutilisable</b>. Cliquer{" "}
                  <i>Téléverser</i> avec le même fichier déclenchera{" "}
                  <code style={S.monoMini}>resume()</code> (skip chunks déjà
                  reçus + retry exponentiel sur 5xx).
                </div>
              )}
            </div>
          )}
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
          <div style={S.lastUploadLabel}>
            {isMulti
              ? `Tuiles chargées (${filesLoadedCount}) :`
              : "Dernier upload retenu :"}
          </div>
          {isMulti ? (
            <>
              <div
                style={S.tuilesList}
                data-testid={`tuiles-list-${slot.slot_id}`}
              >
                {uploads.filter((u) => u.passed).map((u, i) => (
                  <div
                    key={`${u.filename}-${i}`}
                    style={S.tuileRow}
                    data-testid={`tuile-row-${slot.slot_id}-${i}`}
                  >
                    <code style={S.monoMini}>{u.filename}</code>
                    <code style={S.monoMini}>
                      {formatBytes(u.size_bytes)}
                    </code>
                    <code style={S.monoMini}>{shortSha(u.sha256)}</code>
                  </div>
                ))}
              </div>
              {filesLoadedCount > 0 && compositeFromUploads && (
                <div
                  style={S.compositeSha}
                  data-testid={`composite-sha256-${slot.slot_id}`}
                >
                  <span style={S.lbl}>COMPOSITE_SHA256</span>
                  <code style={S.mono}>
                    SHA256(concat ordonnée des {filesLoadedCount} SHA-256 individuels)
                  </code>
                </div>
              )}
            </>
          ) : (
            <>
              <code style={S.mono}>{lastUpload.filename}</code>
              <div style={S.muted}>
                {formatBytes(lastUpload.size_bytes)} ·{" "}
                {shortSha(lastUpload.sha256)}
              </div>
            </>
          )}
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

  // ═════ ORDRE N°45 — Promote + Audit ═════
  promoteCard: { background: "#111c2e", border: "1px solid #f59e0b", borderRadius: 10, padding: 14, marginBottom: 16 },
  promoteHeader: { display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 10 },
  btnPromote: { padding: "10px 22px", background: "linear-gradient(135deg,#f59e0b,#d97706)", color: "#0a1018", border: "none", borderRadius: 6, fontWeight: 700, fontSize: 12, letterSpacing: "0.4px" },
  promoteResult: { background: "#0a1018", border: "1px solid #1e293b", borderRadius: 6, padding: 12, display: "flex", flexDirection: "column", gap: 6 },
  promoteRow: { display: "flex", justifyContent: "space-between", alignItems: "center", gap: 12 },

  auditCard: { background: "#111c2e", border: "1px solid #1e293b", borderRadius: 10, padding: 14, marginBottom: 16 },
  auditHeader: { display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 8 },
  auditFilters: { display: "flex", gap: 8, marginBottom: 10, alignItems: "center", flexWrap: "wrap" },
  select: { padding: "6px 10px", background: "#0a1018", border: "1px solid #3a4a66", borderRadius: 6, color: "#e2e8f0", fontSize: 11, fontFamily: "inherit" },
  auditScroll: { maxHeight: 280, overflowY: "auto", border: "1px solid #1e293b", borderRadius: 6, padding: 8, fontSize: 11 },
  auditRow: { display: "flex", gap: 8, padding: "5px 8px", marginBottom: 4, background: "rgba(255,255,255,0.02)", borderRadius: 4, alignItems: "center" },
  auditEvent: { fontWeight: 700, fontSize: 10, minWidth: 130 },
  auditSlot: { fontWeight: 700, color: "#67e8f9", minWidth: 130, fontSize: 10 },

  // ═════ ORDRE N°46 — VOIE B multi-upload ═════
  voieBBanner: {
    marginTop: 6,
    padding: "5px 10px",
    background: "linear-gradient(135deg,rgba(245,158,11,0.20),rgba(251,146,60,0.12))",
    border: "1px solid rgba(245,158,11,0.45)",
    borderRadius: 5,
    color: "#fcd34d",
    fontSize: 10,
    fontWeight: 700,
    letterSpacing: "0.4px",
    textAlign: "center",
  },
  tuilesList: {
    maxHeight: 120,
    overflowY: "auto",
    border: "1px solid #1e293b",
    borderRadius: 4,
    padding: 4,
    marginTop: 4,
    background: "rgba(10,16,24,0.5)",
  },
  tuileRow: {
    display: "flex",
    justifyContent: "space-between",
    gap: 6,
    padding: "2px 4px",
    borderBottom: "1px dashed #1e293b",
    fontSize: 10,
  },
  monoMini: {
    fontFamily: "JetBrains Mono, Menlo, monospace",
    fontSize: 9,
    color: "#94a3b8",
    wordBreak: "break-all",
  },
  compositeSha: {
    marginTop: 6,
    padding: "6px 8px",
    background: "rgba(34,211,238,0.06)",
    border: "1px solid rgba(34,211,238,0.35)",
    borderRadius: 4,
    display: "flex",
    flexDirection: "column",
    gap: 2,
  },
  // ─── ORDRE N°47 · Bouton trombone (paperclip pickers) ───────────
  trombonneBtn: {
    padding: "4px 10px",
    background: "linear-gradient(135deg,#22d3ee,#0891b2)",
    color: "#0a1018",
    border: "1px solid rgba(34,211,238,0.6)",
    borderRadius: 6,
    fontSize: 13,
    fontWeight: 700,
    minWidth: 38,
    height: 28,
    display: "inline-flex",
    alignItems: "center",
    justifyContent: "center",
    transition: "transform 0.15s ease, box-shadow 0.15s ease",
    boxShadow: "0 2px 8px rgba(34,211,238,0.2)",
  },
  trombonneBtnDisabled: {
    background: "linear-gradient(135deg,#475569,#1e293b)",
    border: "1px solid rgba(252,211,77,0.5)",
    boxShadow: "0 0 0 2px rgba(252,211,77,0.2)",
    color: "#fcd34d",
  },
  // ─── ORDRE N°48 · Token attention/empty states ─────────────────
  tokenCardEmpty: {
    border: "1px solid rgba(252,211,77,0.45)",
    boxShadow: "0 0 0 1px rgba(252,211,77,0.12) inset",
  },
  tokenCardAttention: {
    border: "2px solid #fbbf24",
    boxShadow:
      "0 0 0 4px rgba(251,191,36,0.25), 0 0 24px rgba(251,191,36,0.45)",
    animation: "gisTokenPulse 0.6s ease-in-out 0s 3",
  },
  tokenInputAttention: {
    borderColor: "#fbbf24",
    boxShadow: "0 0 0 3px rgba(251,191,36,0.35)",
    background: "#1e1308",
  },
  tokenBadgeRequired: {
    color: "#fcd34d",
    fontWeight: 800,
    fontSize: 10,
    letterSpacing: "0.5px",
    marginLeft: 6,
  },
  inlineCode: {
    margin: "0 4px",
    padding: "1px 6px",
    background: "rgba(34,211,238,0.10)",
    border: "1px solid rgba(34,211,238,0.35)",
    borderRadius: 4,
    fontFamily: "JetBrains Mono, Menlo, monospace",
    fontSize: 11,
    color: "#67e8f9",
  },
};

export default AdminGISReceptionPanel;

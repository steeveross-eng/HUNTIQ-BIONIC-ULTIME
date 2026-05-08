/**
 * bce4xApi.js — P21 doctrinal API client for /api/v30/super-masters/
 * ═══════════════════════════════════════════════════════════════
 * COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU · ANTI-GÉNÉRIQUE STRICT
 *
 * Source UNIQUE de communication BCE-4X. Token X-Commandant-Token
 * transmis depuis localStorage (clé `bce4x_commandant_token`).
 * V30_LOCK : INVIOLÉ.
 * ═══════════════════════════════════════════════════════════════
 */
import axios from 'axios';

const BASE = process.env.REACT_APP_BACKEND_URL || '';
const SUPER_MASTERS = `${BASE}/api/v30/super-masters`;
const TOKEN_STORAGE_KEY = 'bce4x_commandant_token';

export const getCommandantToken = () => {
  try {
    return localStorage.getItem(TOKEN_STORAGE_KEY) || '';
  } catch {
    return '';
  }
};

export const setCommandantToken = (t) => {
  try {
    localStorage.setItem(TOKEN_STORAGE_KEY, t || '');
  } catch {
    /* ignore */
  }
};

export const clearCommandantToken = () => {
  try {
    localStorage.removeItem(TOKEN_STORAGE_KEY);
  } catch {
    /* ignore */
  }
};

const headers = () => ({
  'Content-Type': 'application/json',
  'X-Commandant-Token': getCommandantToken(),
});

const handle = (p) =>
  p
    .then((r) => ({ ok: true, data: r.data }))
    .catch((e) => ({
      ok: false,
      status: e?.response?.status,
      detail: e?.response?.data?.detail || e?.message,
    }));

// P15 ─ rapport opérationnel
export const territoireReportCreate = (body = {}) =>
  handle(
    axios.post(`${SUPER_MASTERS}/territoire-omega-report-create`, body, {
      headers: headers(),
    }),
  );
export const territoireReportStatus = () =>
  handle(axios.get(`${SUPER_MASTERS}/territoire-omega-report-status`));
export const territoireReportDownloadUrl = (sha, fmt = 'pdf') =>
  `${SUPER_MASTERS}/territoire-omega-report-download?report_sha256=${encodeURIComponent(
    sha,
  )}&fmt=${fmt}`;

// P17 ─ field guide par waypoint
export const waypointGuideCreate = (body = {}) =>
  handle(
    axios.post(`${SUPER_MASTERS}/waypoint-field-guide-create`, body, {
      headers: headers(),
    }),
  );
export const waypointGuideStatus = () =>
  handle(axios.get(`${SUPER_MASTERS}/waypoint-field-guide-status`));
export const waypointGuideDownloadUrl = (sha, fmt = 'pdf') =>
  `${SUPER_MASTERS}/waypoint-field-guide-download?guide_sha256=${encodeURIComponent(
    sha,
  )}&fmt=${fmt}`;

// P18 ─ manual 18 layers
export const layerManualCreate = (body = {}) =>
  handle(
    axios.post(`${SUPER_MASTERS}/layer-interpretation-manual-create`, body, {
      headers: headers(),
    }),
  );
export const layerManualStatus = () =>
  handle(axios.get(`${SUPER_MASTERS}/layer-interpretation-manual-status`));
export const layerManualDownloadUrl = (sha, fmt = 'pdf') =>
  `${SUPER_MASTERS}/layer-interpretation-manual-download?manual_sha256=${encodeURIComponent(
    sha,
  )}&fmt=${fmt}`;

// P14 ─ Merkle anchor
export const merkleStatus = () =>
  handle(axios.get(`${SUPER_MASTERS}/merkle-tree-anchor-hook-status`));
export const merkleBuild = (body = { persist: true, enable_ots_anchor: false }) =>
  handle(
    axios.post(`${SUPER_MASTERS}/merkle-tree-anchor-build`, body, {
      headers: headers(),
    }),
  );

// P20 ─ UI/UX audit
export const uiAuditExecute = (body = { persist: true }) =>
  handle(
    axios.post(`${SUPER_MASTERS}/territoire-ui-ux-audit-execute`, body, {
      headers: headers(),
    }),
  );
export const uiAuditStatus = () =>
  handle(axios.get(`${SUPER_MASTERS}/territoire-ui-ux-audit-status`));

// P22 ─ Commandant validations
export const validationRecord = (body) =>
  handle(
    axios.post(`${SUPER_MASTERS}/commandant-validation-record`, body, {
      headers: headers(),
    }),
  );
export const validationStatus = () =>
  handle(axios.get(`${SUPER_MASTERS}/commandant-validation-status`));

// P23 ─ Messaging engine (email + internal)
export const messagingHookActivate = () =>
  handle(
    axios.post(
      `${SUPER_MASTERS}/messaging-engine-channel-hook-activate`,
      { persist: true },
      { headers: headers() },
    ),
  );
export const messagingShare = (body) =>
  handle(
    axios.post(`${SUPER_MASTERS}/messaging-engine-channel-share`, body, {
      headers: headers(),
    }),
  );
export const messagingStatus = () =>
  handle(axios.get(`${SUPER_MASTERS}/messaging-engine-channel-status`));

// P24 ─ OTS upgrade automation
export const otsHookActivate = (body = { interval_s: 21600, run_immediate_scan: true, persist: true }) =>
  handle(
    axios.post(`${SUPER_MASTERS}/ots-upgrade-automation-hook-activate`, body, {
      headers: headers(),
    }),
  );
export const otsScanNow = (body = { persist: true, timeout_s_per_file: 60 }) =>
  handle(
    axios.post(`${SUPER_MASTERS}/ots-upgrade-automation-scan-now`, body, {
      headers: headers(),
    }),
  );
export const otsStop = () =>
  handle(
    axios.post(`${SUPER_MASTERS}/ots-upgrade-automation-stop`, {}, { headers: headers() }),
  );
export const otsStatus = () =>
  handle(axios.get(`${SUPER_MASTERS}/ots-upgrade-automation-status`));

// P10 ─ Visualizer all layers (existing endpoint)
export const visualizerAllLayers = () =>
  handle(axios.get(`${SUPER_MASTERS}/visualizer-all-layers`));

// P13 ─ Bundle download
export const bundleDownloadUrl = () =>
  `${SUPER_MASTERS}/download-all-layers-bundle`;
export const bundleStatus = () =>
  handle(axios.get(`${SUPER_MASTERS}/download-all-layers-bundle-status`));

export const BCE4X_TOKEN_KEY = TOKEN_STORAGE_KEY;

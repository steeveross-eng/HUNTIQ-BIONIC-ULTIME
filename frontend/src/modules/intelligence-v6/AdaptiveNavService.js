/**
 * Adaptive Navigation Service — API Client M4
 * Directive x7100-M4 | BCE-4X GOLDEN V6+
 * 
 * ANTI-DOUBLON : Consommation exclusive via DFL + DataContracts V6.
 */

const API = process.env.REACT_APP_BACKEND_URL;
const BASE = `${API}/api/v1/nav-intel`;

async function safeFetch(url) {
  try {
    const r = await fetch(url);
    if (!r.ok) return null;
    return r.json();
  } catch { return null; }
}

async function safePost(url, body) {
  try {
    const r = await fetch(url, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
    if (!r.ok) return null;
    return r.json();
  } catch { return null; }
}

async function safePatch(url, body) {
  try {
    const r = await fetch(url, { method: 'PATCH', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
    if (!r.ok) return null;
    return r.json();
  } catch { return null; }
}

export const AdaptiveNavAPI = {
  health: () => safeFetch(`${BASE}/health`),
  getProfile: (userId) => safeFetch(`${BASE}/profile/${userId}`),
  updateProfile: (userId, data) => safePatch(`${BASE}/profile/${userId}`, data),
  learn: (userId) => safePost(`${BASE}/profile/${userId}/learn`, {}),
  getSuggestions: (userId) => safeFetch(`${BASE}/suggestions/${userId}`),
  planRoute: (data) => safePost(`${BASE}/plan-route`, data),
  getSession: (sessionId) => safeFetch(`${BASE}/plan-route/${sessionId}`),
  optimize: (data) => safePost(`${BASE}/optimize`, data),
  getAdvice: (userId, lat, lng) => safeFetch(`${BASE}/advice/${userId}/${lat}/${lng}`),
  startSession: (sessionId) => safePost(`${BASE}/session/start`, { session_id: sessionId }),
  endSession: (sessionId, metrics) => safePost(`${BASE}/session/${sessionId}/end`, { metrics }),
  getSessionStatus: (sessionId) => safeFetch(`${BASE}/session/${sessionId}/status`),
};

export default AdaptiveNavAPI;

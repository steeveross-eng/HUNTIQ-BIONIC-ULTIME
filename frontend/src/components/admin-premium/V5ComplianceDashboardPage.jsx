/**
 * V5ComplianceDashboardPage.jsx — PHASE OMEGA · P22Ω.V5_COMPLIANCE_LIVE_Ω
 * COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU · ANTI-GÉNÉRIQUE STRICT
 *
 * Dashboard temps réel des 5 critères doctrinaux V5 + agrégats 24h.
 * Endpoints consommés :
 *   - GET /api/v20/audit/v5-compliance-live?lat&lon&species (par waypoint)
 *   - GET /api/v20/audit/v5-monitor-stats
 *   - GET /api/v20/audit/v5-daily-report?hours=24
 */
import React, { useEffect, useState, useCallback } from 'react';
import { Activity, CheckCircle2, AlertTriangle, Loader2, RefreshCw, Bell } from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL;

const WAYPOINTS = [
  { lat: 48.206657, lon: -68.382422, species: 'orignal', label: 'BSL' },
  { lat: 46.5,      lon: -71.5,      species: 'cerf',    label: 'Lotbinière' },
  { lat: 48.4,      lon: -71.05,     species: 'orignal', label: 'Saguenay' },
];

const CRITERIA = [
  { key: 'n_corridors',     label: 'n_corridors ∈ [5, 7]',                target: '5..7' },
  { key: 'subnet_role',     label: 'subnet_role présent',                  target: '100%' },
  { key: 'hierarchy',       label: 'hierarchy valide',                     target: 'V5' },
  { key: 'fusion_doctrine', label: 'fusion_doctrine V5',                   target: 'P22Σ_V5_CAP_GLOBAL_TERRITOIRE' },
  { key: 'source',          label: 'source ENGINE-IA-ORGANIC-Ω',           target: 'V5_BUNDLE_REWIRE' },
];

const V5ComplianceDashboardPage = () => {
  const [results, setResults] = useState({});
  const [monitorStats, setMonitorStats] = useState(null);
  const [daily, setDaily] = useState(null);
  const [loading, setLoading] = useState(false);
  const [lastFetch, setLastFetch] = useState(null);

  const fetchAll = useCallback(async () => {
    setLoading(true);
    try {
      const checks = await Promise.all(
        WAYPOINTS.map(async (w) => {
          try {
            const r = await fetch(
              `${API}/api/v20/audit/v5-compliance-live?lat=${w.lat}&lon=${w.lon}&species=${w.species}`,
            );
            if (!r.ok) return { wp: w, error: `HTTP ${r.status}` };
            const j = await r.json();
            return { wp: w, data: j };
          } catch (e) {
            return { wp: w, error: e.message };
          }
        }),
      );
      const acc = {};
      checks.forEach(({ wp, data, error }) => {
        acc[wp.label] = { wp, data, error };
      });
      setResults(acc);

      const [statsRes, dailyRes] = await Promise.all([
        fetch(`${API}/api/v20/audit/v5-monitor-stats`).then((r) => r.json()).catch(() => null),
        fetch(`${API}/api/v20/audit/v5-daily-report?hours=24&format=json`).then((r) => r.json()).catch(() => null),
      ]);
      setMonitorStats(statsRes);
      setDaily(dailyRes);
      setLastFetch(new Date().toISOString());
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchAll();
    const id = setInterval(fetchAll, 60_000); // refresh 1min
    return () => clearInterval(id);
  }, [fetchAll]);

  const passCount = Object.values(results).filter((r) => r.data?.status === 'PASS').length;
  const failCount = Object.values(results).filter((r) => r.data?.status === 'FAIL').length;
  const errCount = Object.values(results).filter((r) => r.error).length;

  return (
    <div className="p-6 bg-slate-950 min-h-screen text-slate-100" data-testid="v5-compliance-dashboard">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight flex items-center gap-3">
            <Activity className="w-8 h-8 text-orange-500" />
            V5 Compliance Dashboard
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            P22Ω.V5_COMPLIANCE_LIVE_Ω · PHASE OMEGA · COMMANDANT STEEVE-MAX
          </p>
        </div>
        <button
          data-testid="v5-refresh-btn"
          onClick={fetchAll}
          disabled={loading}
          className="flex items-center gap-2 px-4 py-2 bg-orange-600 hover:bg-orange-500 rounded-md text-sm font-medium disabled:opacity-50"
        >
          {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <RefreshCw className="w-4 h-4" />}
          Rafraîchir
        </button>
      </div>

      {/* Synthèse globale */}
      <div className="grid grid-cols-4 gap-4 mb-6">
        <div className="bg-slate-900 border border-slate-800 rounded-lg p-4" data-testid="v5-summary-pass">
          <div className="flex items-center gap-2 text-green-400">
            <CheckCircle2 className="w-5 h-5" />
            <span className="text-xs uppercase tracking-wider">Waypoints PASS</span>
          </div>
          <div className="text-3xl font-bold mt-2">{passCount}/{WAYPOINTS.length}</div>
        </div>
        <div className="bg-slate-900 border border-slate-800 rounded-lg p-4" data-testid="v5-summary-fail">
          <div className="flex items-center gap-2 text-red-400">
            <AlertTriangle className="w-5 h-5" />
            <span className="text-xs uppercase tracking-wider">Waypoints FAIL</span>
          </div>
          <div className="text-3xl font-bold mt-2">{failCount + errCount}</div>
        </div>
        <div className="bg-slate-900 border border-slate-800 rounded-lg p-4" data-testid="v5-summary-conformity">
          <div className="flex items-center gap-2 text-orange-400">
            <Activity className="w-5 h-5" />
            <span className="text-xs uppercase tracking-wider">Conformité 24h</span>
          </div>
          <div className="text-3xl font-bold mt-2">{daily?.summary?.v5_conformity_pct ?? 0}%</div>
        </div>
        <div className="bg-slate-900 border border-slate-800 rounded-lg p-4" data-testid="v5-summary-alerts">
          <div className="flex items-center gap-2 text-yellow-400">
            <Bell className="w-5 h-5" />
            <span className="text-xs uppercase tracking-wider">Alertes envoyées</span>
          </div>
          <div className="text-3xl font-bold mt-2">{monitorStats?.stats?.alerts_sent ?? 0}</div>
        </div>
      </div>

      {/* Détail par waypoint × 5 critères */}
      <div className="bg-slate-900 border border-slate-800 rounded-lg overflow-hidden mb-6" data-testid="v5-criteria-grid">
        <div className="px-4 py-3 border-b border-slate-800">
          <h2 className="font-semibold">Conformité par waypoint × 5 critères doctrinaux</h2>
        </div>
        <table className="w-full text-sm">
          <thead className="bg-slate-800/50">
            <tr>
              <th className="text-left px-4 py-2 font-medium text-slate-400">Waypoint</th>
              {CRITERIA.map((c) => (
                <th key={c.key} className="text-center px-2 py-2 font-medium text-slate-400">
                  {c.label}
                </th>
              ))}
              <th className="text-center px-4 py-2 font-medium text-slate-400">Status</th>
            </tr>
          </thead>
          <tbody>
            {WAYPOINTS.map((wp) => {
              const r = results[wp.label] || {};
              const data = r.data;
              const status = data?.status || (r.error ? 'ERR' : '...');
              const violationRules = new Set((data?.violations || []).map((v) => v.rule));
              return (
                <tr key={wp.label} className="border-t border-slate-800" data-testid={`v5-row-${wp.label}`}>
                  <td className="px-4 py-3 font-medium">
                    <div>{wp.label}</div>
                    <div className="text-xs text-slate-500">{wp.species} · {wp.lat},{wp.lon}</div>
                  </td>
                  {CRITERIA.map((c) => {
                    const failed = violationRules.has(
                      c.key === 'n_corridors' ? 'n_corridors_in_5_to_7'
                      : c.key === 'subnet_role' ? 'subnet_role_present_on_each_corridor'
                      : c.key === 'hierarchy' ? 'hierarchy_valid'
                      : c.key === 'fusion_doctrine' ? 'fusion_doctrine_v5'
                      : 'source_field_v5_organic',
                    );
                    const ok = data && !failed;
                    return (
                      <td key={c.key} className="text-center px-2 py-3">
                        {!data ? (
                          <span className="text-slate-600">–</span>
                        ) : ok ? (
                          <CheckCircle2 className="w-5 h-5 inline text-green-500" data-testid={`v5-ok-${wp.label}-${c.key}`} />
                        ) : (
                          <AlertTriangle className="w-5 h-5 inline text-red-500" data-testid={`v5-fail-${wp.label}-${c.key}`} />
                        )}
                      </td>
                    );
                  })}
                  <td className="text-center px-4 py-3">
                    <span
                      className={`inline-block px-2 py-1 rounded text-xs font-bold ${
                        status === 'PASS' ? 'bg-green-900 text-green-300'
                        : status === 'FAIL' ? 'bg-red-900 text-red-300'
                        : 'bg-slate-800 text-slate-400'
                      }`}
                      data-testid={`v5-status-${wp.label}`}
                    >
                      {status}
                    </span>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Métriques temps réel + dérives 24h */}
      <div className="grid grid-cols-2 gap-4">
        <div className="bg-slate-900 border border-slate-800 rounded-lg p-4" data-testid="v5-metrics-card">
          <h3 className="font-semibold mb-3">Métriques 24h</h3>
          <ul className="space-y-2 text-sm">
            <li className="flex justify-between"><span className="text-slate-400">Ticks monitorés</span><span className="font-mono">{daily?.summary?.n_ticks ?? '–'}</span></li>
            <li className="flex justify-between"><span className="text-slate-400">Checks totaux</span><span className="font-mono">{daily?.summary?.n_total_checks ?? '–'}</span></li>
            <li className="flex justify-between"><span className="text-slate-400">Checks FAIL</span><span className="font-mono text-red-400">{daily?.summary?.n_failed_checks ?? '–'}</span></li>
            <li className="flex justify-between"><span className="text-slate-400">Fallback V10</span><span className="font-mono">{daily?.summary?.v10_fallback_pct ?? 0}%</span></li>
            <li className="flex justify-between"><span className="text-slate-400">Cache HIT ratio</span><span className="font-mono">{daily?.latency?.hit_ratio_pct ?? 0}%</span></li>
            <li className="flex justify-between"><span className="text-slate-400">Latence moy. MISS</span><span className="font-mono">{daily?.latency?.avg_compute_ms ?? 0}ms</span></li>
          </ul>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-lg p-4" data-testid="v5-derives-card">
          <h3 className="font-semibold mb-3">Dérives doctrinales détectées</h3>
          {daily?.derives_doctrinales && Object.keys(daily.derives_doctrinales).length > 0 ? (
            <ul className="space-y-1 text-sm">
              {Object.entries(daily.derives_doctrinales)
                .sort((a, b) => b[1] - a[1])
                .map(([rule, count]) => (
                  <li key={rule} className="flex justify-between">
                    <span className="text-red-400 font-mono text-xs">{rule}</span>
                    <span className="font-mono">{count}</span>
                  </li>
                ))}
            </ul>
          ) : (
            <p className="text-sm text-green-400 flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4" />
              Aucune dérive détectée
            </p>
          )}
        </div>
      </div>

      <div className="mt-6 text-xs text-slate-500" data-testid="v5-last-fetch">
        Dernière actualisation : {lastFetch || '–'} · Auto-refresh 60s ·{' '}
        <a
          href={`${API}/api/v20/audit/v5-daily-report?hours=24&format=md`}
          target="_blank"
          rel="noreferrer"
          className="underline hover:text-orange-400"
          data-testid="v5-md-link"
        >
          Rapport quotidien (MD)
        </a>
      </div>
    </div>
  );
};

export default V5ComplianceDashboardPage;

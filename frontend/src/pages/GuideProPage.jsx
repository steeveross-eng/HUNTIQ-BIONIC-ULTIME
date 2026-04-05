/**
 * GUIDE PRO — Phase E-2 Frontend
 * BCE-4X GOLDEN V6+ | STEEVE-MAX
 * 
 * 6 composants:
 * 1. GuideProDashboard — Vue principale avec sessions
 * 2. BDREMonitor — Monitoring terrain BDRE en temps reel
 * 3. SessionCreator — Formulaire creation session
 * 4. RouteViewer — Visualisation routes avec annotations BDRE
 * 5. TerrainScoreCard — Carte score terrain par source
 * 6. AuditLogPanel — Journal BDRE temps reel
 */
import { useState, useEffect, useCallback } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Progress } from "@/components/ui/progress";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Shield, Activity, MapPin, Route, AlertTriangle, CheckCircle,
  Clock, Users, Target, BarChart3, Loader2, RefreshCw, Plus
} from "lucide-react";

const API = process.env.REACT_APP_BACKEND_URL;

/* ================================================================
   COMPOSANT 1: BDRE MONITOR — Monitoring terrain temps reel
   ================================================================ */
function BDREMonitor({ onRefresh }) {
  const [dashboard, setDashboard] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchDashboard = useCallback(async () => {
    try {
      setLoading(true);
      const res = await fetch(`${API}/api/v1/bdre/dashboard`);
      const data = await res.json();
      setDashboard(data);
    } catch (err) {
      console.error("[BDRE] Dashboard fetch error:", err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchDashboard(); }, [fetchDashboard]);

  if (loading && !dashboard) {
    return (
      <Card data-testid="bdre-monitor-loading">
        <CardContent className="flex items-center justify-center py-8">
          <Loader2 className="h-5 w-5 animate-spin text-amber-600 mr-2" />
          <span className="text-sm text-stone-500">Chargement BDRE...</span>
        </CardContent>
      </Card>
    );
  }

  if (!dashboard) return null;

  const statusColor = {
    healthy: "bg-emerald-500",
    degraded: "bg-amber-500",
    empty: "bg-red-500",
    down: "bg-red-700",
    not_connected: "bg-stone-400",
  };

  return (
    <Card data-testid="bdre-monitor" className="border-stone-200">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Shield className="h-5 w-5 text-amber-700" />
            <CardTitle className="text-base text-stone-800">BDRE — Data Reliability</CardTitle>
            <Badge variant="outline" className="text-xs border-amber-300 text-amber-700">
              {dashboard.bdre_version}
            </Badge>
          </div>
          <Button
            variant="ghost" size="sm"
            onClick={() => { fetchDashboard(); onRefresh?.(); }}
            data-testid="bdre-refresh-btn"
          >
            <RefreshCw className="h-4 w-4" />
          </Button>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Sources Overview */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
          {Object.entries(dashboard.sources.by_status || {}).map(([status, count]) => (
            <div key={status} className="flex items-center gap-1.5 text-xs" data-testid={`bdre-status-${status}`}>
              <div className={`w-2 h-2 rounded-full ${statusColor[status] || "bg-stone-300"}`} />
              <span className="text-stone-600 capitalize">{status}</span>
              <span className="font-mono font-semibold text-stone-800">{count}</span>
            </div>
          ))}
        </div>

        {/* Source Scores */}
        <div className="space-y-1.5">
          {(dashboard.source_scores || []).filter(s => s.status !== "not_connected").map(src => (
            <div key={src.source_id} className="flex items-center gap-2" data-testid={`bdre-score-${src.source_id}`}>
              <span className="text-xs text-stone-500 w-16 font-mono">{src.source_id}</span>
              <Progress
                value={src.score * 100}
                className="h-1.5 flex-1"
              />
              <span className="text-xs font-mono w-10 text-right text-stone-700">
                {(src.score * 100).toFixed(0)}%
              </span>
              <Badge
                variant="outline"
                className={`text-xs py-0 ${
                  src.classification === "FIABLE" ? "border-emerald-300 text-emerald-700" :
                  src.classification === "ACCEPTABLE" ? "border-blue-300 text-blue-700" :
                  src.classification === "DEGRADE" ? "border-amber-300 text-amber-700" :
                  "border-red-300 text-red-700"
                }`}
              >
                {src.classification}
              </Badge>
            </div>
          ))}
        </div>

        {/* Audit Stats */}
        <div className="flex gap-4 text-xs text-stone-500 pt-1 border-t border-stone-100">
          <span data-testid="bdre-audit-entries">Journal: <strong className="text-stone-700">{dashboard.audit.total_entries}</strong></span>
          <span data-testid="bdre-audit-fallbacks">Fallbacks: <strong className="text-amber-700">{dashboard.audit.total_fallbacks}</strong></span>
          <span data-testid="bdre-audit-alerts">Alertes: <strong className="text-red-700">{dashboard.audit.total_alerts}</strong></span>
        </div>
      </CardContent>
    </Card>
  );
}

/* ================================================================
   COMPOSANT 2: TERRAIN SCORE CARD — Score terrain par territoire
   ================================================================ */
function TerrainScoreCard({ territoryId }) {
  const [validation, setValidation] = useState(null);
  const [loading, setLoading] = useState(false);

  const validate = useCallback(async () => {
    if (!territoryId) return;
    setLoading(true);
    try {
      const res = await fetch(`${API}/api/v1/bdre/validate/${territoryId}`, { method: "POST" });
      setValidation(await res.json());
    } catch (err) {
      console.error("[BDRE] Validation error:", err);
    } finally {
      setLoading(false);
    }
  }, [territoryId]);

  useEffect(() => { validate(); }, [validate]);

  if (!validation) return null;

  const recColors = {
    SOURCE_PRIMAIRE: { bg: "bg-emerald-50", border: "border-emerald-200", text: "text-emerald-800", icon: CheckCircle },
    FALLBACK_LEVEL_1_WATERWAY: { bg: "bg-amber-50", border: "border-amber-200", text: "text-amber-800", icon: Activity },
    FALLBACK_LEVEL_2_TERRAIN: { bg: "bg-orange-50", border: "border-orange-200", text: "text-orange-800", icon: AlertTriangle },
    FALLBACK_LEVEL_3_CORRIDOR_ASTAR: { bg: "bg-red-50", border: "border-red-200", text: "text-red-800", icon: AlertTriangle },
    FALLBACK_LEVEL_4_GPS_ESTIMATION: { bg: "bg-red-100", border: "border-red-300", text: "text-red-900", icon: AlertTriangle },
  };

  const rec = recColors[validation.recommendation] || recColors.FALLBACK_LEVEL_2_TERRAIN;
  const RecIcon = rec.icon;

  return (
    <Card data-testid="terrain-score-card" className={`${rec.bg} ${rec.border}`}>
      <CardContent className="py-3 px-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <RecIcon className={`h-4 w-4 ${rec.text}`} />
            <span className={`text-sm font-medium ${rec.text}`}>
              Terrain: {(validation.min_score * 100).toFixed(0)}%
            </span>
          </div>
          <Badge variant="outline" className={`text-xs ${rec.border} ${rec.text}`}>
            {validation.recommendation?.replace(/_/g, " ")}
          </Badge>
        </div>
        {validation.min_score < 0.4 && (
          <p className="text-xs text-orange-700 mt-1" data-testid="terrain-warning">
            Donnees terrain insuffisantes. Routes basees sur estimations enrichies.
          </p>
        )}
      </CardContent>
    </Card>
  );
}

/* ================================================================
   COMPOSANT 3: SESSION CREATOR — Formulaire creation session
   ================================================================ */
function SessionCreator({ onSessionCreated }) {
  const [creating, setCreating] = useState(false);
  const [form, setForm] = useState({
    title: "", territory_id: "", species: "deer", guide_id: "guide-default",
  });

  const handleCreate = async () => {
    if (!form.title || !form.territory_id) return;
    setCreating(true);
    try {
      const body = {
        ...form,
        start_date: new Date().toISOString().split("T")[0],
        end_date: new Date(Date.now() + 86400000).toISOString().split("T")[0],
        clients: [],
        bounds: { north: 48.20, south: 48.18, east: -68.38, west: -68.40 },
      };
      const res = await fetch(`${API}/api/v1/guide-pro/sessions`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      const data = await res.json();
      if (data.success) {
        onSessionCreated?.(data.session);
        setForm({ title: "", territory_id: "", species: "deer", guide_id: "guide-default" });
      }
    } catch (err) {
      console.error("[GUIDE PRO] Create session error:", err);
    } finally {
      setCreating(false);
    }
  };

  return (
    <Card data-testid="session-creator">
      <CardHeader className="pb-3">
        <CardTitle className="text-base text-stone-800 flex items-center gap-2">
          <Plus className="h-4 w-4" />
          Nouvelle session
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        <div className="grid grid-cols-2 gap-3">
          <div>
            <Label className="text-xs text-stone-500">Titre</Label>
            <Input
              data-testid="session-title-input"
              placeholder="Session du 06/04"
              value={form.title}
              onChange={(e) => setForm(f => ({ ...f, title: e.target.value }))}
              className="h-8 text-sm"
            />
          </div>
          <div>
            <Label className="text-xs text-stone-500">Territoire</Label>
            <Input
              data-testid="session-territory-input"
              placeholder="T-48.19"
              value={form.territory_id}
              onChange={(e) => setForm(f => ({ ...f, territory_id: e.target.value }))}
              className="h-8 text-sm"
            />
          </div>
        </div>
        <Button
          data-testid="create-session-btn"
          onClick={handleCreate}
          disabled={creating || !form.title || !form.territory_id}
          className="w-full h-8 text-sm bg-amber-700 hover:bg-amber-800 text-white"
        >
          {creating ? <Loader2 className="h-4 w-4 animate-spin" /> : "Creer la session"}
        </Button>
      </CardContent>
    </Card>
  );
}

/* ================================================================
   COMPOSANT 4: ROUTE VIEWER — Visualisation routes BDRE
   ================================================================ */
function RouteViewer({ session }) {
  const [routes, setRoutes] = useState(null);
  const [loading, setLoading] = useState(false);
  const [generating, setGenerating] = useState(false);

  const fetchRoutes = useCallback(async () => {
    if (!session?.session_id) return;
    setLoading(true);
    try {
      const res = await fetch(`${API}/api/v1/guide-pro/sessions/${session.session_id}/routes`);
      const data = await res.json();
      if (data.success) setRoutes(data);
    } catch (err) {
      console.error("[GUIDE PRO] Routes error:", err);
    } finally {
      setLoading(false);
    }
  }, [session]);

  const generateRoutes = async () => {
    if (!session?.session_id) return;
    setGenerating(true);
    try {
      const res = await fetch(`${API}/api/v1/guide-pro/sessions/${session.session_id}/routes/generate`, {
        method: "POST",
      });
      const data = await res.json();
      if (data.success) setRoutes(data);
    } catch (err) {
      console.error("[GUIDE PRO] Generate error:", err);
    } finally {
      setGenerating(false);
    }
  };

  useEffect(() => { fetchRoutes(); }, [fetchRoutes]);

  const trailTypeColors = {
    real_osm: "bg-emerald-100 text-emerald-800 border-emerald-300",
    waterway_guided: "bg-blue-100 text-blue-800 border-blue-300",
    hybride_sentier_terrain: "bg-amber-100 text-amber-800 border-amber-300",
    corridor_astar: "bg-orange-100 text-orange-800 border-orange-300",
    terrain_topology: "bg-purple-100 text-purple-800 border-purple-300",
    estimation_enriched: "bg-red-100 text-red-800 border-red-300",
  };

  return (
    <Card data-testid="route-viewer">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-base text-stone-800 flex items-center gap-2">
            <Route className="h-4 w-4 text-amber-700" />
            Parcours
          </CardTitle>
          <Button
            data-testid="generate-routes-btn"
            variant="outline" size="sm"
            onClick={generateRoutes}
            disabled={generating}
            className="h-7 text-xs"
          >
            {generating ? <Loader2 className="h-3 w-3 animate-spin mr-1" /> : null}
            Generer
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        {!routes?.routes?.length ? (
          <p className="text-xs text-stone-400 text-center py-4" data-testid="no-routes-msg">
            Aucun parcours. Ajoutez des clients puis generez.
          </p>
        ) : (
          <div className="space-y-2">
            {/* BDRE Validation */}
            {routes.bdre_validation && (
              <div className="flex items-center gap-2 text-xs pb-2 border-b border-stone-100" data-testid="route-bdre-validation">
                <Shield className="h-3 w-3 text-amber-600" />
                <span className="text-stone-500">Terrain BDRE:</span>
                <span className="font-mono font-semibold text-stone-700">
                  {(routes.bdre_validation.min_score * 100).toFixed(0)}%
                </span>
                <Badge variant="outline" className="text-xs py-0">
                  {routes.bdre_validation.recommendation}
                </Badge>
              </div>
            )}

            {routes.routes.map((route, idx) => (
              <div
                key={route.route_id || idx}
                className="flex items-center justify-between py-1.5 px-2 rounded bg-stone-50"
                data-testid={`route-item-${idx}`}
              >
                <div className="flex items-center gap-2">
                  <span className="text-xs font-medium text-stone-600">
                    {route.role === "guide" ? "Guide" : `Client ${idx + 1}`}
                  </span>
                  {route.bdre_terrain_status && (
                    <Badge
                      variant="outline"
                      className={`text-xs py-0 ${trailTypeColors[route.bdre_terrain_status] || "border-stone-300 text-stone-600"}`}
                    >
                      BDRE {(route.bdre_terrain_score * 100).toFixed(0)}%
                    </Badge>
                  )}
                </div>
                <div className="flex items-center gap-2 text-xs text-stone-500">
                  {route.total_distance_km > 0 && (
                    <span>{route.total_distance_km}km</span>
                  )}
                  {route.waypoints && (
                    <span>{route.waypoints.length} pts</span>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}

/* ================================================================
   COMPOSANT 5: AUDIT LOG PANEL — Journal BDRE temps reel
   ================================================================ */
function AuditLogPanel() {
  const [logs, setLogs] = useState(null);
  const [fallbacks, setFallbacks] = useState([]);

  const fetchLogs = useCallback(async () => {
    try {
      const [logRes, fbRes] = await Promise.all([
        fetch(`${API}/api/v1/bdre/audit/log?limit=15`),
        fetch(`${API}/api/v1/bdre/fallbacks/recent?limit=5`),
      ]);
      setLogs(await logRes.json());
      const fb = await fbRes.json();
      setFallbacks(fb.fallbacks || []);
    } catch (err) {
      console.error("[BDRE] Audit fetch error:", err);
    }
  }, []);

  useEffect(() => { fetchLogs(); const id = setInterval(fetchLogs, 10000); return () => clearInterval(id); }, [fetchLogs]);

  const actionColors = {
    success: "text-emerald-600",
    fallback_L1: "text-blue-600",
    fallback_L2: "text-amber-600",
    fallback_L3: "text-orange-600",
    fallback_L4: "text-red-600",
    alert_empty: "text-red-700",
    fetch_complete: "text-stone-600",
    validate_terrain: "text-amber-700",
    check_source: "text-stone-500",
  };

  return (
    <Card data-testid="audit-log-panel">
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <CardTitle className="text-base text-stone-800 flex items-center gap-2">
            <Clock className="h-4 w-4 text-stone-500" />
            Journal BDRE
          </CardTitle>
          <Button variant="ghost" size="sm" onClick={fetchLogs} data-testid="audit-refresh-btn">
            <RefreshCw className="h-3 w-3" />
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        {/* Fallbacks recents */}
        {fallbacks.length > 0 && (
          <div className="mb-3 p-2 rounded bg-amber-50 border border-amber-200" data-testid="fallbacks-section">
            <p className="text-xs font-medium text-amber-800 mb-1">Fallbacks recents</p>
            {fallbacks.map((fb, i) => (
              <div key={i} className="text-xs text-amber-700 flex gap-2">
                <span className="font-mono">{fb.engine}</span>
                <span>{fb.action}</span>
                <Badge variant="outline" className="text-xs py-0 border-amber-300">L{fb.fallback_level}</Badge>
              </div>
            ))}
          </div>
        )}

        {/* Log entries */}
        <div className="space-y-1 max-h-48 overflow-y-auto" data-testid="audit-log-entries">
          {logs?.entries?.map((entry, i) => (
            <div key={i} className="flex items-center gap-1.5 text-xs py-0.5">
              <span className="text-stone-400 font-mono w-14 shrink-0">
                {entry.timestamp?.slice(11, 19)}
              </span>
              <span className="font-mono text-stone-500 w-12 shrink-0">{entry.engine}</span>
              <span className={`font-medium ${actionColors[entry.action] || "text-stone-600"}`}>
                {entry.action}
              </span>
              {entry.fallback_level > 0 && (
                <Badge variant="outline" className="text-xs py-0 h-4">L{entry.fallback_level}</Badge>
              )}
              <span className="text-stone-400 font-mono ml-auto">{entry.score.toFixed(2)}</span>
            </div>
          ))}
          {!logs?.entries?.length && (
            <p className="text-xs text-stone-400 text-center py-2">Aucune entree</p>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

/* ================================================================
   COMPOSANT 6: GUIDE PRO DASHBOARD — Page principale
   ================================================================ */
export default function GuideProPage() {
  const [sessions, setSessions] = useState([]);
  const [activeSession, setActiveSession] = useState(null);
  const [activeTab, setActiveTab] = useState("dashboard");

  const fetchSessions = useCallback(async () => {
    try {
      const res = await fetch(`${API}/api/v1/guide-pro/sessions/guide/guide-default`);
      const data = await res.json();
      if (data.sessions) setSessions(data.sessions);
    } catch (err) {
      console.error("[GUIDE PRO] Sessions error:", err);
    }
  }, []);

  useEffect(() => { fetchSessions(); }, [fetchSessions]);

  const handleSessionCreated = (session) => {
    setSessions(prev => [session, ...prev]);
    setActiveSession(session);
  };

  return (
    <div className="min-h-screen bg-stone-50" data-testid="guide-pro-page">
      {/* Header */}
      <div className="bg-white border-b border-stone-200 px-4 py-3">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Target className="h-5 w-5 text-amber-700" />
            <h1 className="text-lg font-semibold text-stone-800">GUIDE PRO</h1>
            <Badge className="bg-amber-100 text-amber-800 border-amber-300 text-xs">
              BCE-4X
            </Badge>
          </div>
          <div className="flex items-center gap-2 text-xs text-stone-500">
            <Shield className="h-3.5 w-3.5 text-amber-600" />
            <span>BDRE Active</span>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-6xl mx-auto p-4">
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="bg-white border border-stone-200 mb-4">
            <TabsTrigger value="dashboard" data-testid="tab-dashboard" className="text-xs">
              <BarChart3 className="h-3.5 w-3.5 mr-1" />
              Dashboard
            </TabsTrigger>
            <TabsTrigger value="sessions" data-testid="tab-sessions" className="text-xs">
              <Users className="h-3.5 w-3.5 mr-1" />
              Sessions
            </TabsTrigger>
            <TabsTrigger value="bdre" data-testid="tab-bdre" className="text-xs">
              <Shield className="h-3.5 w-3.5 mr-1" />
              BDRE
            </TabsTrigger>
          </TabsList>

          {/* TAB: Dashboard */}
          <TabsContent value="dashboard">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
              <div className="lg:col-span-2 space-y-4">
                <BDREMonitor />

                {/* Sessions recentes */}
                <Card data-testid="recent-sessions">
                  <CardHeader className="pb-2">
                    <CardTitle className="text-base text-stone-800">Sessions recentes</CardTitle>
                  </CardHeader>
                  <CardContent>
                    {sessions.length === 0 ? (
                      <p className="text-xs text-stone-400 text-center py-4">Aucune session</p>
                    ) : (
                      <div className="space-y-1.5">
                        {sessions.slice(0, 5).map((s, i) => (
                          <div
                            key={s.session_id || i}
                            className="flex items-center justify-between py-1.5 px-2 rounded hover:bg-stone-50 cursor-pointer"
                            onClick={() => { setActiveSession(s); setActiveTab("sessions"); }}
                            data-testid={`session-item-${i}`}
                          >
                            <div className="flex items-center gap-2">
                              <MapPin className="h-3.5 w-3.5 text-amber-600" />
                              <span className="text-sm text-stone-700">{s.title}</span>
                              <Badge variant="outline" className="text-xs py-0">{s.status}</Badge>
                            </div>
                            <span className="text-xs text-stone-400">{s.territory_id}</span>
                          </div>
                        ))}
                      </div>
                    )}
                  </CardContent>
                </Card>
              </div>

              <div className="space-y-4">
                <SessionCreator onSessionCreated={handleSessionCreated} />
                <AuditLogPanel />
              </div>
            </div>
          </TabsContent>

          {/* TAB: Sessions */}
          <TabsContent value="sessions">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
              {/* Session list */}
              <div className="space-y-2">
                <SessionCreator onSessionCreated={handleSessionCreated} />
                {sessions.map((s, i) => (
                  <Card
                    key={s.session_id || i}
                    className={`cursor-pointer transition-all ${
                      activeSession?.session_id === s.session_id ? "ring-2 ring-amber-400" : ""
                    }`}
                    onClick={() => setActiveSession(s)}
                    data-testid={`session-card-${i}`}
                  >
                    <CardContent className="py-2 px-3">
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium text-stone-700">{s.title}</span>
                        <Badge variant="outline" className="text-xs py-0">{s.status}</Badge>
                      </div>
                      <div className="flex items-center gap-3 mt-1 text-xs text-stone-400">
                        <span>{s.territory_id}</span>
                        <span>{s.clients?.length || 0} clients</span>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>

              {/* Active session detail */}
              <div className="lg:col-span-2 space-y-4">
                {activeSession ? (
                  <>
                    <TerrainScoreCard territoryId={activeSession.territory_id} />
                    <RouteViewer session={activeSession} />
                  </>
                ) : (
                  <Card>
                    <CardContent className="py-12 text-center">
                      <MapPin className="h-8 w-8 text-stone-300 mx-auto mb-2" />
                      <p className="text-sm text-stone-400">Selectionnez une session</p>
                    </CardContent>
                  </Card>
                )}
              </div>
            </div>
          </TabsContent>

          {/* TAB: BDRE */}
          <TabsContent value="bdre">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              <BDREMonitor />
              <AuditLogPanel />

              {/* Anomalies */}
              <AnomalyPanel />

              {/* Engines integres */}
              <Card data-testid="engines-panel">
                <CardHeader className="pb-2">
                  <CardTitle className="text-base text-stone-800 flex items-center gap-2">
                    <Activity className="h-4 w-4 text-emerald-600" />
                    Engines integres
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-1.5">
                    {[
                      { name: "TNE (Terrain Nav)", phase: "Phase 2", status: "active" },
                      { name: "Access Engine V6", phase: "Phase 3", status: "active" },
                      { name: "Stand Recommendation", phase: "Phase 3", status: "active" },
                      { name: "GUIDE PRO", phase: "Phase 4", status: "active" },
                      { name: "Weather V3", phase: "Phase 4", status: "active" },
                    ].map((eng, i) => (
                      <div key={i} className="flex items-center justify-between py-1 px-2 rounded bg-stone-50" data-testid={`engine-item-${i}`}>
                        <div className="flex items-center gap-2">
                          <div className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
                          <span className="text-sm text-stone-700">{eng.name}</span>
                        </div>
                        <Badge variant="outline" className="text-xs py-0">{eng.phase}</Badge>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}

/* ================================================================
   SOUS-COMPOSANT: ANOMALY PANEL
   ================================================================ */
function AnomalyPanel() {
  const [anomalies, setAnomalies] = useState([]);

  useEffect(() => {
    fetch(`${API}/api/v1/bdre/anomalies/recent?limit=10`)
      .then(r => r.json())
      .then(d => setAnomalies(d.anomalies || []))
      .catch(() => {});
  }, []);

  return (
    <Card data-testid="anomaly-panel">
      <CardHeader className="pb-2">
        <CardTitle className="text-base text-stone-800 flex items-center gap-2">
          <AlertTriangle className="h-4 w-4 text-amber-600" />
          Anomalies terrain
        </CardTitle>
      </CardHeader>
      <CardContent>
        {anomalies.length === 0 ? (
          <p className="text-xs text-stone-400 text-center py-3">Aucune anomalie detectee</p>
        ) : (
          <div className="space-y-2">
            {anomalies.map((a, i) => (
              <div key={i} className="p-2 rounded bg-amber-50 border border-amber-200" data-testid={`anomaly-item-${i}`}>
                <div className="flex items-center gap-2 text-xs">
                  <span className="font-mono text-amber-800">{a.source_id}</span>
                  <span className="text-amber-600">{a.anomaly_count} anomalies</span>
                  <Badge
                    variant="outline"
                    className={`text-xs py-0 ${a.is_healthy ? "border-emerald-300 text-emerald-700" : "border-red-300 text-red-700"}`}
                  >
                    {a.is_healthy ? "Sain" : "Degrade"}
                  </Badge>
                </div>
                {a.anomalies?.map((detail, j) => (
                  <p key={j} className="text-xs text-amber-700 mt-1 pl-2 border-l-2 border-amber-300">
                    [{detail.severity}] {detail.type}: {detail.details}
                  </p>
                ))}
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}

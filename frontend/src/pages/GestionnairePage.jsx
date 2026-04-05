/**
 * GestionnairePage — Module Gestionnaire UI
 * Phase F | BCE-4X GOLDEN V6+ | Autorite: STEEVE-MAX
 *
 * Onglets: CARTE, BDRE, ANOMALIES, JOURNAL, SOURCES
 * Bouton SECOURS institutionnel (toujours visible)
 *
 * BDRE-FIRST: Tous les panneaux integrent les metriques BDRE.
 */

import React, { useState, useEffect, useCallback } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../components/ui/tabs";
import { Badge } from "../components/ui/badge";
import { Button } from "../components/ui/button";
import {
  Map, Shield, AlertTriangle, FileText, Database,
  Radio, Users, MapPin, RefreshCw, Phone, Activity,
  ChevronRight, Circle, Clock, CheckCircle2, XCircle,
} from "lucide-react";

const API = process.env.REACT_APP_BACKEND_URL;

/* ─────────── SECOURS BUTTON (toujours visible, position fixe) ─────────── */
function SecoursButton({ onTrigger, activeAlerts }) {
  const [confirming, setConfirming] = useState(false);
  const hasActive = activeAlerts.length > 0;

  const handleClick = () => {
    if (confirming) {
      onTrigger();
      setConfirming(false);
    } else {
      setConfirming(true);
      setTimeout(() => setConfirming(false), 5000);
    }
  };

  return (
    <div className="fixed bottom-6 right-6 z-50 flex flex-col items-end gap-2" data-testid="secours-container">
      {hasActive && (
        <Badge variant="destructive" className="animate-pulse text-xs px-2 py-1">
          {activeAlerts.length} alerte{activeAlerts.length > 1 ? "s" : ""} active{activeAlerts.length > 1 ? "s" : ""}
        </Badge>
      )}
      <button
        onClick={handleClick}
        data-testid="secours-btn"
        className={`flex items-center gap-2 px-6 py-3 rounded-full font-bold text-white uppercase tracking-wider shadow-lg transition-all duration-300 ${
          confirming
            ? "bg-red-700 ring-4 ring-red-400 animate-pulse scale-110"
            : "bg-red-600 hover:bg-red-700 hover:scale-105"
        }`}
      >
        <Phone className="h-5 w-5" />
        {confirming ? "CONFIRMER SECOURS" : "SECOURS"}
      </button>
    </div>
  );
}

/* ─────────── TAB: CARTE ─────────── */
function CarteTab({ positions, sectors, territoryId }) {
  return (
    <div className="space-y-4" data-testid="tab-carte-content">
      {/* Positions des chasseurs */}
      <Card className="bg-[#1a1f2e] border-gray-700">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium text-gray-300 flex items-center gap-2">
            <MapPin className="h-4 w-4 text-green-400" /> Positions Chasseurs
          </CardTitle>
        </CardHeader>
        <CardContent>
          {positions.length === 0 ? (
            <p className="text-gray-500 text-xs">Aucune position active</p>
          ) : (
            <div className="space-y-2">
              {positions.map((p, i) => (
                <div key={i} className="flex items-center justify-between bg-[#141824] px-3 py-2 rounded border border-gray-700/50" data-testid={`position-${i}`}>
                  <div className="flex items-center gap-2">
                    <Circle className={`h-2.5 w-2.5 ${p.status === "active" ? "text-green-400 fill-green-400" : "text-gray-500 fill-gray-500"}`} />
                    <span className="text-xs text-gray-200 font-mono">{p.user_id || "Chasseur"}</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className="text-[10px] text-gray-400 font-mono">{p.lat?.toFixed(5)}, {p.lng?.toFixed(5)}</span>
                    <Badge variant="outline" className="text-[10px] border-gray-600 text-gray-400">{p.accuracy ? `${p.accuracy.toFixed(0)}m` : "—"}</Badge>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Secteurs */}
      <Card className="bg-[#1a1f2e] border-gray-700">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium text-gray-300 flex items-center gap-2">
            <Map className="h-4 w-4 text-blue-400" /> Secteurs
          </CardTitle>
        </CardHeader>
        <CardContent>
          {sectors.length === 0 ? (
            <p className="text-gray-500 text-xs">Aucun secteur defini pour {territoryId || "ce territoire"}</p>
          ) : (
            <div className="grid grid-cols-2 gap-2">
              {sectors.map((s, i) => (
                <div key={i} className="bg-[#141824] px-3 py-2 rounded border border-gray-700/50" data-testid={`sector-${i}`}>
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-gray-200">{s.name || s.sector_id}</span>
                    <Badge className={`text-[10px] ${s.status === "open" ? "bg-green-900/50 text-green-300" : "bg-red-900/50 text-red-300"}`}>
                      {s.status || "inconnu"}
                    </Badge>
                  </div>
                  <div className="text-[10px] text-gray-500 mt-1">{s.hunters?.length || 0} chasseur(s)</div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

/* ─────────── TAB: BDRE ─────────── */
function BDRETab({ bdreDashboard, onRefresh }) {
  if (!bdreDashboard) return <p className="text-gray-500 text-xs p-4">Chargement BDRE...</p>;

  const sources = bdreDashboard._sources_list || [];
  const stats = bdreDashboard.audit_stats || {};
  const srcSummary = bdreDashboard.sources || {};

  return (
    <div className="space-y-4" data-testid="tab-bdre-content">
      {/* BDRE Status Header */}
      <Card className="bg-[#1a1f2e] border-gray-700">
        <CardHeader className="pb-2">
          <div className="flex items-center justify-between">
            <CardTitle className="text-sm font-medium text-gray-300 flex items-center gap-2">
              <Shield className="h-4 w-4 text-[#F5A623]" /> BDRE — Tableau de Bord
            </CardTitle>
            <Button variant="ghost" size="sm" onClick={onRefresh} data-testid="bdre-tab-refresh">
              <RefreshCw className="h-3.5 w-3.5 text-gray-400" />
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-4 gap-3">
            <StatBox label="Version" value={bdreDashboard.bdre_version || "—"} color="text-[#F5A623]" />
            <StatBox label="Sources" value={srcSummary.total ?? sources.length} color="text-blue-400" />
            <StatBox label="Fallbacks" value={stats.total_fallbacks ?? 0} color="text-yellow-400" />
            <StatBox label="Alertes" value={stats.total_alerts ?? 0} color="text-red-400" />
          </div>
        </CardContent>
      </Card>

      {/* Sources Grid */}
      <Card className="bg-[#1a1f2e] border-gray-700">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium text-gray-300 flex items-center gap-2">
            <Database className="h-4 w-4 text-blue-400" /> Sources BDRE
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-1.5">
            {sources.map((src, i) => (
              <div key={i} className="flex items-center justify-between bg-[#141824] px-3 py-2 rounded border border-gray-700/50" data-testid={`bdre-source-${i}`}>
                <div className="flex items-center gap-2">
                  {src.status === "healthy" ? (
                    <CheckCircle2 className="h-3.5 w-3.5 text-green-400" />
                  ) : (
                    <XCircle className="h-3.5 w-3.5 text-gray-500" />
                  )}
                  <span className="text-xs text-gray-200">{src.name}</span>
                  <Badge variant="outline" className="text-[10px] border-gray-600 text-gray-500">{src.source_id}</Badge>
                </div>
                <div className="flex items-center gap-2">
                  <ScoreBar score={src.score} />
                  <span className="text-xs font-mono text-gray-400 w-8 text-right">{(src.score * 100).toFixed(0)}%</span>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

/* ─────────── TAB: ANOMALIES ─────────── */
function AnomaliesTab({ anomalies, onRefresh }) {
  return (
    <div className="space-y-4" data-testid="tab-anomalies-content">
      <Card className="bg-[#1a1f2e] border-gray-700">
        <CardHeader className="pb-2">
          <div className="flex items-center justify-between">
            <CardTitle className="text-sm font-medium text-gray-300 flex items-center gap-2">
              <AlertTriangle className="h-4 w-4 text-yellow-400" /> Anomalies Detectees
            </CardTitle>
            <Button variant="ghost" size="sm" onClick={onRefresh} data-testid="anomalies-refresh">
              <RefreshCw className="h-3.5 w-3.5 text-gray-400" />
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {anomalies.length === 0 ? (
            <div className="flex flex-col items-center py-6 text-gray-500">
              <CheckCircle2 className="h-8 w-8 mb-2 text-green-400/50" />
              <p className="text-xs">Aucune anomalie detectee</p>
            </div>
          ) : (
            <div className="space-y-2">
              {anomalies.map((a, i) => (
                <div key={i} className="bg-[#141824] px-3 py-2 rounded border-l-2 border-yellow-500/60" data-testid={`anomaly-${i}`}>
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-gray-200 font-medium">{a.type || "Anomalie"}</span>
                    <Badge className={`text-[10px] ${a.severity === "critical" ? "bg-red-900/50 text-red-300" : a.severity === "warning" ? "bg-yellow-900/50 text-yellow-300" : "bg-blue-900/50 text-blue-300"}`}>
                      {a.severity || "info"}
                    </Badge>
                  </div>
                  <p className="text-[10px] text-gray-400 mt-1">{a.details || a.message || "—"}</p>
                  <p className="text-[10px] text-gray-600 mt-0.5">{a.source_id} — {a.timestamp ? new Date(a.timestamp).toLocaleString("fr-CA") : "—"}</p>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

/* ─────────── TAB: JOURNAL ─────────── */
function JournalTab({ auditLog, onRefresh }) {
  return (
    <div className="space-y-4" data-testid="tab-journal-content">
      <Card className="bg-[#1a1f2e] border-gray-700">
        <CardHeader className="pb-2">
          <div className="flex items-center justify-between">
            <CardTitle className="text-sm font-medium text-gray-300 flex items-center gap-2">
              <FileText className="h-4 w-4 text-purple-400" /> Journal BDRE
            </CardTitle>
            <Button variant="ghost" size="sm" onClick={onRefresh} data-testid="journal-refresh">
              <RefreshCw className="h-3.5 w-3.5 text-gray-400" />
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {auditLog.length === 0 ? (
            <p className="text-gray-500 text-xs">Aucune entree dans le journal</p>
          ) : (
            <div className="space-y-1 max-h-[420px] overflow-y-auto">
              {auditLog.map((entry, i) => (
                <div key={i} className="flex items-start gap-2 bg-[#141824] px-3 py-2 rounded border border-gray-700/30" data-testid={`journal-entry-${i}`}>
                  <Activity className="h-3 w-3 text-gray-500 mt-0.5 flex-shrink-0" />
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center gap-2 flex-wrap">
                      <Badge variant="outline" className="text-[10px] border-gray-600 text-gray-400">{entry.engine || "—"}</Badge>
                      <span className="text-xs text-gray-200">{entry.action || "—"}</span>
                      {entry.fallback_level > 0 && <Badge className="text-[10px] bg-yellow-900/50 text-yellow-300">L{entry.fallback_level}</Badge>}
                    </div>
                    <p className="text-[10px] text-gray-500 mt-0.5 truncate">{entry.details || "—"}</p>
                    <p className="text-[10px] text-gray-600">{entry.timestamp ? new Date(entry.timestamp).toLocaleString("fr-CA") : "—"}</p>
                  </div>
                  <ScoreBar score={entry.score} />
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

/* ─────────── TAB: SOURCES ─────────── */
function SourcesTab({ bdreDashboard }) {
  const sources = bdreDashboard?._sources_list || [];
  const engines = bdreDashboard?.engines_integrated || [];

  return (
    <div className="space-y-4" data-testid="tab-sources-content">
      {/* Engines integres */}
      <Card className="bg-[#1a1f2e] border-gray-700">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium text-gray-300 flex items-center gap-2">
            <Radio className="h-4 w-4 text-green-400" /> Engines Integres BDRE
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-3 gap-2">
            {engines.length > 0 ? engines.map((eng, i) => (
              <div key={i} className="bg-[#141824] px-3 py-2 rounded border border-gray-700/50 flex items-center gap-2" data-testid={`engine-${i}`}>
                <CheckCircle2 className="h-3 w-3 text-green-400 flex-shrink-0" />
                <span className="text-xs text-gray-200 truncate">{eng.name || eng}</span>
              </div>
            )) : (
              <p className="text-gray-500 text-xs col-span-3">Aucun engine integre</p>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Sources avec details */}
      <Card className="bg-[#1a1f2e] border-gray-700">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium text-gray-300 flex items-center gap-2">
            <Database className="h-4 w-4 text-blue-400" /> Registre Complet des Sources
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            {sources.map((src, i) => (
              <div key={i} className="bg-[#141824] px-3 py-3 rounded border border-gray-700/50" data-testid={`source-detail-${i}`}>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-mono text-[#F5A623]">{src.source_id}</span>
                    <ChevronRight className="h-3 w-3 text-gray-600" />
                    <span className="text-xs text-gray-200">{src.name}</span>
                  </div>
                  <Badge className={`text-[10px] ${src.status === "healthy" ? "bg-green-900/50 text-green-300" : "bg-gray-800 text-gray-400"}`}>
                    {src.status}
                  </Badge>
                </div>
                <div className="flex items-center gap-4 mt-2">
                  <div className="flex items-center gap-1">
                    <span className="text-[10px] text-gray-500">Type:</span>
                    <span className="text-[10px] text-gray-300">{src.type || "—"}</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <span className="text-[10px] text-gray-500">Score:</span>
                    <ScoreBar score={src.score} />
                    <span className="text-[10px] text-gray-300">{(src.score * 100).toFixed(0)}%</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <span className="text-[10px] text-gray-500">Classification:</span>
                    <span className={`text-[10px] font-medium ${src.score >= 0.8 ? "text-green-400" : src.score >= 0.6 ? "text-blue-400" : src.score >= 0.3 ? "text-yellow-400" : "text-red-400"}`}>
                      {src.score >= 0.8 ? "FIABLE" : src.score >= 0.6 ? "ACCEPTABLE" : src.score >= 0.3 ? "DEGRADE" : "CRITIQUE"}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

/* ─────────── MICRO-COMPOSANTS ─────────── */
function StatBox({ label, value, color }) {
  return (
    <div className="bg-[#141824] px-3 py-2 rounded border border-gray-700/50 text-center">
      <div className={`text-lg font-bold ${color}`}>{value}</div>
      <div className="text-[10px] text-gray-500 uppercase tracking-wider">{label}</div>
    </div>
  );
}

function ScoreBar({ score }) {
  const pct = Math.round((score || 0) * 100);
  const color = pct >= 80 ? "bg-green-500" : pct >= 60 ? "bg-blue-500" : pct >= 30 ? "bg-yellow-500" : "bg-red-500";
  return (
    <div className="w-16 h-1.5 bg-gray-700 rounded-full overflow-hidden">
      <div className={`h-full ${color} rounded-full transition-all`} style={{ width: `${pct}%` }} />
    </div>
  );
}

/* ─────────── EMERGENCIES PANEL ─────────── */
function EmergencyPanel({ alerts, onAck, onResolve }) {
  if (alerts.length === 0) return null;
  return (
    <Card className="bg-red-950/30 border-red-800/50 mb-4" data-testid="emergency-panel">
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-medium text-red-300 flex items-center gap-2">
          <AlertTriangle className="h-4 w-4 text-red-400 animate-pulse" /> Alertes Secours Actives
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-2">
          {alerts.map((a, i) => (
            <div key={i} className="bg-red-900/20 px-3 py-2 rounded border border-red-700/30" data-testid={`emergency-alert-${i}`}>
              <div className="flex items-center justify-between">
                <div>
                  <span className="text-xs text-red-200 font-medium">{a.user_name || a.user_id}</span>
                  <span className="text-[10px] text-red-400 ml-2">{a.message || "URGENCE"}</span>
                </div>
                <div className="flex gap-1">
                  <Button size="sm" variant="outline" className="text-[10px] h-6 border-yellow-600 text-yellow-300" onClick={() => onAck(a.alert_id)} data-testid={`ack-alert-${i}`}>
                    Accuser
                  </Button>
                  <Button size="sm" variant="outline" className="text-[10px] h-6 border-green-600 text-green-300" onClick={() => onResolve(a.alert_id)} data-testid={`resolve-alert-${i}`}>
                    Resoudre
                  </Button>
                </div>
              </div>
              <div className="text-[10px] text-red-500 mt-1">
                <Clock className="h-2.5 w-2.5 inline mr-1" />
                {a.timestamp ? new Date(a.timestamp).toLocaleString("fr-CA") : "—"}
                {a.position && <span className="ml-2">({a.position.lat?.toFixed(5)}, {a.position.lng?.toFixed(5)})</span>}
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}

/* ─────────── PAGE PRINCIPALE ─────────── */
export default function GestionnairePage() {
  const [activeTab, setActiveTab] = useState("carte");
  const [territoryId, setTerritoryId] = useState("T-48.19");
  const [positions, setPositions] = useState([]);
  const [sectors, setSectors] = useState([]);
  const [bdreDashboard, setBdreDashboard] = useState(null);
  const [anomalies, setAnomalies] = useState([]);
  const [auditLog, setAuditLog] = useState([]);
  const [activeAlerts, setActiveAlerts] = useState([]);
  const [healthStatus, setHealthStatus] = useState(null);

  const fetchAll = useCallback(async () => {
    const [posRes, secRes, bdreRes, anomRes, auditRes, alertRes, healthRes, srcRes] = await Promise.allSettled([
      fetch(`${API}/api/v1/gestionnaire/positions/${territoryId}`).then(r => r.json()),
      fetch(`${API}/api/v1/gestionnaire/sectors/${territoryId}`).then(r => r.json()),
      fetch(`${API}/api/v1/bdre/dashboard`).then(r => r.json()),
      fetch(`${API}/api/v1/bdre/anomalies/recent?limit=20`).then(r => r.json()),
      fetch(`${API}/api/v1/bdre/audit/log?limit=50`).then(r => r.json()),
      fetch(`${API}/api/v1/gestionnaire/emergency/active/${territoryId}`).then(r => r.json()),
      fetch(`${API}/api/v1/gestionnaire/health`).then(r => r.json()),
      fetch(`${API}/api/v1/bdre/sources`).then(r => r.json()),
    ]);
    if (posRes.status === "fulfilled") setPositions(posRes.value.positions || []);
    if (secRes.status === "fulfilled") setSectors(secRes.value.sectors || []);
    if (bdreRes.status === "fulfilled") {
      const dashboard = bdreRes.value;
      // Injecter la liste des sources depuis l'endpoint dedie
      if (srcRes.status === "fulfilled") {
        dashboard._sources_list = srcRes.value.sources || [];
      }
      setBdreDashboard(dashboard);
    }
    if (anomRes.status === "fulfilled") setAnomalies(anomRes.value.anomalies || []);
    if (auditRes.status === "fulfilled") setAuditLog(auditRes.value.entries || []);
    if (alertRes.status === "fulfilled") setActiveAlerts(alertRes.value.alerts || []);
    if (healthRes.status === "fulfilled") setHealthStatus(healthRes.value);
  }, [territoryId]);

  useEffect(() => { fetchAll(); }, [fetchAll]);

  // Auto-refresh 15s
  useEffect(() => {
    const interval = setInterval(fetchAll, 15000);
    return () => clearInterval(interval);
  }, [fetchAll]);

  const handleSecours = async () => {
    const alertData = {
      alert_id: `alert_${Date.now()}_gestionnaire`,
      user_id: "gestionnaire",
      user_name: "Gestionnaire",
      position: { lat: 0, lng: 0, accuracy: 0 },
      timestamp: new Date().toISOString(),
      status: "active",
      type: "secours",
      message: "URGENCE — Declenchee depuis Module Gestionnaire",
      territory_id: territoryId,
      responders: [],
    };
    await fetch(`${API}/api/v1/gestionnaire/emergency`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(alertData),
    }).catch(() => {});
    fetchAll();
  };

  const handleAck = async (alertId) => {
    await fetch(`${API}/api/v1/gestionnaire/emergency/${alertId}/ack`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ user_id: "gestionnaire", name: "Gestionnaire" }),
    }).catch(() => {});
    fetchAll();
  };

  const handleResolve = async (alertId) => {
    await fetch(`${API}/api/v1/gestionnaire/emergency/${alertId}/resolve`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({}),
    }).catch(() => {});
    fetchAll();
  };

  return (
    <div className="min-h-screen bg-[#0f1219] text-white pt-[100px] px-4 pb-24" data-testid="gestionnaire-page">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div>
          <h1 className="text-lg font-bold text-gray-100 flex items-center gap-2">
            <Users className="h-5 w-5 text-[#F5A623]" />
            Module Gestionnaire
          </h1>
          <p className="text-xs text-gray-500 mt-0.5">
            Phase F — BCE-4X GOLDEN V6+ | BDRE-FIRST
            {healthStatus && <Badge variant="outline" className="ml-2 text-[10px] border-green-600 text-green-400">{healthStatus.status}</Badge>}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <label className="text-[10px] text-gray-500 uppercase">Territoire:</label>
          <input
            value={territoryId}
            onChange={(e) => setTerritoryId(e.target.value)}
            className="bg-[#141824] border border-gray-700 rounded px-2 py-1 text-xs text-gray-200 w-24 font-mono"
            data-testid="territory-input"
          />
          <Button variant="ghost" size="sm" onClick={fetchAll} data-testid="gestionnaire-refresh">
            <RefreshCw className="h-3.5 w-3.5 text-gray-400" />
          </Button>
        </div>
      </div>

      {/* Emergency Panel */}
      <EmergencyPanel alerts={activeAlerts} onAck={handleAck} onResolve={handleResolve} />

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="bg-[#1a1f2e] border border-gray-700 w-full justify-start gap-0 h-auto p-0.5">
          <TabsTrigger value="carte" className="text-xs data-[state=active]:bg-[#F5A623]/10 data-[state=active]:text-[#F5A623]" data-testid="gestionnaire-tab-carte">
            <Map className="h-3.5 w-3.5 mr-1" /> CARTE
          </TabsTrigger>
          <TabsTrigger value="bdre" className="text-xs data-[state=active]:bg-blue-500/10 data-[state=active]:text-blue-400" data-testid="gestionnaire-tab-bdre">
            <Shield className="h-3.5 w-3.5 mr-1" /> BDRE
          </TabsTrigger>
          <TabsTrigger value="anomalies" className="text-xs data-[state=active]:bg-yellow-500/10 data-[state=active]:text-yellow-400" data-testid="gestionnaire-tab-anomalies">
            <AlertTriangle className="h-3.5 w-3.5 mr-1" /> ANOMALIES
          </TabsTrigger>
          <TabsTrigger value="journal" className="text-xs data-[state=active]:bg-purple-500/10 data-[state=active]:text-purple-400" data-testid="gestionnaire-tab-journal">
            <FileText className="h-3.5 w-3.5 mr-1" /> JOURNAL
          </TabsTrigger>
          <TabsTrigger value="sources" className="text-xs data-[state=active]:bg-green-500/10 data-[state=active]:text-green-400" data-testid="gestionnaire-tab-sources">
            <Database className="h-3.5 w-3.5 mr-1" /> SOURCES
          </TabsTrigger>
        </TabsList>

        <TabsContent value="carte" className="mt-3">
          <CarteTab positions={positions} sectors={sectors} territoryId={territoryId} />
        </TabsContent>
        <TabsContent value="bdre" className="mt-3">
          <BDRETab bdreDashboard={bdreDashboard} onRefresh={fetchAll} />
        </TabsContent>
        <TabsContent value="anomalies" className="mt-3">
          <AnomaliesTab anomalies={anomalies} onRefresh={fetchAll} />
        </TabsContent>
        <TabsContent value="journal" className="mt-3">
          <JournalTab auditLog={auditLog} onRefresh={fetchAll} />
        </TabsContent>
        <TabsContent value="sources" className="mt-3">
          <SourcesTab bdreDashboard={bdreDashboard} />
        </TabsContent>
      </Tabs>

      {/* SECOURS Button */}
      <SecoursButton onTrigger={handleSecours} activeAlerts={activeAlerts} />
    </div>
  );
}

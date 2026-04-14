/**
 * AdminTerritoryValue — ADMIN: Valeur commerciale ALPHA des territoires
 * H1-H6: Scores, indices, anomalies, rapports commerciaux
 */
import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import {
  Crown, MapPin, BarChart3, AlertTriangle, TrendingUp, TrendingDown,
  Loader2, RefreshCw, Star, Target, Activity, Shield, Eye
} from 'lucide-react';
import { toast } from 'sonner';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const TIER_COLORS = {
  ALPHA: 'bg-amber-500/20 text-amber-400 border-amber-500/30',
  Or: 'bg-yellow-500/20 text-yellow-300 border-yellow-500/30',
  Argent: 'bg-zinc-400/20 text-zinc-300 border-zinc-400/30',
  Bronze: 'bg-orange-800/20 text-orange-400 border-orange-700/30'
};

const AdminTerritoryValue = () => {
  const [territories, setTerritories] = useState([]);
  const [anomalies, setAnomalies] = useState([]);
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(true);

  const token = localStorage.getItem('auth_token');
  const headers = { Authorization: `Bearer ${token}` };

  const loadData = useCallback(async () => {
    if (!token) return;
    setLoading(true);
    try {
      const [terrRes, anomRes, reportRes] = await Promise.all([
        axios.get(`${API}/v1/vision/territories/scores`, { headers }),
        axios.get(`${API}/v1/vision/territories/anomalies`, { headers }),
        axios.get(`${API}/v1/vision/territories/report`, { headers })
      ]);
      setTerritories(terrRes.data.territories || []);
      setAnomalies(anomRes.data.anomalies || []);
      setReport(reportRes.data);
    } catch (err) {
      console.error('Territory value load error:', err);
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => { loadData(); }, [loadData]);

  if (loading) {
    return <div className="flex justify-center py-16"><Loader2 className="h-8 w-8 animate-spin text-amber-500" /></div>;
  }

  const summary = report?.summary || {};

  return (
    <div className="space-y-6" data-testid="admin-territory-value">
      {/* Summary Cards */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
        <Card className="bg-amber-500/10 border-amber-500/30">
          <CardContent className="p-3 text-center">
            <Crown className="h-4 w-4 text-amber-500 mx-auto mb-1" />
            <p className="text-xl font-bold text-amber-400">{summary.alpha_territories || 0}</p>
            <p className="text-xs text-amber-400/60">Territoires ALPHA</p>
          </CardContent>
        </Card>
        <Card className="bg-yellow-500/10 border-yellow-500/30">
          <CardContent className="p-3 text-center">
            <Star className="h-4 w-4 text-yellow-400 mx-auto mb-1" />
            <p className="text-xl font-bold text-yellow-300">{summary.gold_territories || 0}</p>
            <p className="text-xs text-yellow-300/60">Territoires Or</p>
          </CardContent>
        </Card>
        <Card className="bg-zinc-900/50 border-zinc-800">
          <CardContent className="p-3 text-center">
            <Target className="h-4 w-4 text-green-500 mx-auto mb-1" />
            <p className="text-xl font-bold">{summary.total_alphas || 0}</p>
            <p className="text-xs text-zinc-500">Detections ALPHA</p>
          </CardContent>
        </Card>
        <Card className="bg-zinc-900/50 border-zinc-800">
          <CardContent className="p-3 text-center">
            <Eye className="h-4 w-4 text-blue-500 mx-auto mb-1" />
            <p className="text-xl font-bold">{summary.total_analyses || 0}</p>
            <p className="text-xs text-zinc-500">Analyses IA</p>
          </CardContent>
        </Card>
        <Card className={`${anomalies.length > 0 ? 'bg-red-500/10 border-red-500/30' : 'bg-zinc-900/50 border-zinc-800'}`}>
          <CardContent className="p-3 text-center">
            <AlertTriangle className={`h-4 w-4 mx-auto mb-1 ${anomalies.length > 0 ? 'text-red-500' : 'text-zinc-500'}`} />
            <p className="text-xl font-bold">{anomalies.length}</p>
            <p className="text-xs text-zinc-500">Anomalies</p>
          </CardContent>
        </Card>
      </div>

      {/* Refresh */}
      <div className="flex justify-end">
        <Button size="sm" variant="outline" className="border-zinc-700" onClick={loadData} data-testid="refresh-territory-scores">
          <RefreshCw className="h-3.5 w-3.5 mr-1" /> Actualiser
        </Button>
      </div>

      {/* Territory Scores Table */}
      <Card className="bg-zinc-900/50 border-zinc-800" data-testid="territory-scores-table">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm text-zinc-300 flex items-center gap-2">
            <BarChart3 className="h-4 w-4 text-amber-500" /> Classement des Territoires ({territories.length})
          </CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <table className="w-full text-xs">
              <thead>
                <tr className="border-b border-zinc-800 text-zinc-500">
                  <th className="px-3 py-2 text-left">#</th>
                  <th className="px-3 py-2 text-left">Qualite</th>
                  <th className="px-3 py-2 text-left">Score</th>
                  <th className="px-3 py-2 text-left">Frequentation</th>
                  <th className="px-3 py-2 text-left">Dominance</th>
                  <th className="px-3 py-2 text-left">ALPHA</th>
                  <th className="px-3 py-2 text-left">Especes</th>
                  <th className="px-3 py-2 text-left">Observations</th>
                  <th className="px-3 py-2 text-left">Corridors</th>
                  <th className="px-3 py-2 text-left">GPS</th>
                  <th className="px-3 py-2 text-left">Action</th>
                </tr>
              </thead>
              <tbody>
                {territories.map((t, idx) => (
                  <tr key={t.id} className="border-b border-zinc-800/50 hover:bg-zinc-800/30" data-testid={`territory-row-${idx}`}>
                    <td className="px-3 py-2 text-zinc-500">{idx + 1}</td>
                    <td className="px-3 py-2">
                      <Badge className={`text-xs ${TIER_COLORS[t.quality_tier] || TIER_COLORS.Bronze}`}>
                        {t.quality_tier === 'ALPHA' && <Crown className="h-3 w-3 mr-0.5" />}
                        {t.quality_tier}
                      </Badge>
                    </td>
                    <td className="px-3 py-2">
                      <span className="font-bold text-amber-400">{t.territory_score}</span>
                    </td>
                    <td className="px-3 py-2">
                      <div className="flex items-center gap-1">
                        <Progress value={t.frequency_index} className="h-1.5 w-12" />
                        <span className="text-zinc-400">{t.frequency_index}%</span>
                      </div>
                    </td>
                    <td className="px-3 py-2">
                      <div className="flex items-center gap-1">
                        <Progress value={t.dominance_index} className="h-1.5 w-12" />
                        <span className="text-zinc-400">{t.dominance_index}</span>
                      </div>
                    </td>
                    <td className="px-3 py-2 text-amber-400 font-bold">{t.alpha_count}</td>
                    <td className="px-3 py-2">
                      <div className="flex flex-wrap gap-0.5">
                        {(t.species || []).slice(0, 3).map(sp => (
                          <Badge key={sp} className="text-[9px] bg-zinc-700 text-zinc-300">{sp}</Badge>
                        ))}
                      </div>
                    </td>
                    <td className="px-3 py-2 text-zinc-400">{t.total_sightings}</td>
                    <td className="px-3 py-2 text-zinc-400">{t.trajectory_count}</td>
                    <td className="px-3 py-2 text-zinc-500 font-mono text-[10px]">
                      {t.gps_lat?.toFixed(3)}, {t.gps_lon?.toFixed(3)}
                    </td>
                    <td className="px-3 py-2">
                      <Button size="sm" variant="outline" className="h-6 text-[10px] border-zinc-700 px-2"
                        onClick={() => window.location.href = `/mon-territoire-bionic?lat=${t.gps_lat}&lng=${t.gps_lon}&zoom=15`}>
                        <MapPin className="h-3 w-3 mr-0.5" /> Carte
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {territories.length === 0 && (
            <div className="text-center py-8 text-zinc-500">
              <BarChart3 className="h-8 w-8 mx-auto mb-2 text-zinc-600" />
              <p>Aucun territoire evalue — analysez des photos pour generer les scores</p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Anomalies */}
      {anomalies.length > 0 && (
        <Card className="bg-red-500/5 border-red-500/20" data-testid="anomalies-panel">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-red-400 flex items-center gap-2">
              <AlertTriangle className="h-4 w-4" /> Anomalies Detectees ({anomalies.length})
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            {anomalies.map((a, idx) => (
              <div key={idx} className="flex items-center gap-3 p-2 bg-zinc-900/50 rounded border border-zinc-800">
                {a.type === 'activity_drop' ? (
                  <TrendingDown className="h-4 w-4 text-red-400 flex-shrink-0" />
                ) : (
                  <AlertTriangle className="h-4 w-4 text-amber-400 flex-shrink-0" />
                )}
                <div className="flex-1">
                  <p className="text-xs text-zinc-300">{a.detail}</p>
                  <p className="text-[10px] text-zinc-500">Camera: {a.camera_id?.slice(0, 12)} | Severite: {a.severity}</p>
                </div>
                <Badge className={`text-[10px] ${a.severity === 'high' ? 'bg-red-500/20 text-red-400' : 'bg-amber-500/20 text-amber-400'}`}>
                  {a.type === 'activity_drop' ? 'Baisse activite' : 'ALPHA disparu'}
                </Badge>
              </div>
            ))}
          </CardContent>
        </Card>
      )}

      {/* Commercial Report Summary */}
      {report && (
        <Card className="bg-zinc-900/50 border-zinc-800">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-zinc-300 flex items-center gap-2">
              <Shield className="h-4 w-4 text-green-500" /> Rapport Commercial
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs">
              {Object.entries(report.summary?.species_detected || {}).map(([sp, count]) => (
                <div key={sp} className="flex items-center justify-between bg-zinc-800/50 rounded p-2">
                  <span className="text-zinc-300 capitalize">{sp.replace('_', ' ')}</span>
                  <span className="font-bold text-amber-400">{count}</span>
                </div>
              ))}
            </div>
            {report.top_alphas?.length > 0 && (
              <div className="mt-3">
                <p className="text-xs text-zinc-500 mb-1">Top ALPHA:</p>
                <div className="flex flex-wrap gap-2">
                  {report.top_alphas.slice(0, 5).map((a, i) => (
                    <Badge key={i} className="text-xs bg-amber-500/20 text-amber-400">
                      <Crown className="h-3 w-3 mr-1" /> {a.species} — Score {a.alpha_score}
                    </Badge>
                  ))}
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default AdminTerritoryValue;

/**
 * SalinesFichePanel — FICHE SALINE BIONIC ULTIME
 * BCE-4X GOLDEN Phase S | Format vertical Dashboard
 * 5 Scores + 20 Sources + Score Global
 */
import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../../components/ui/card';
import { Badge } from '../../components/ui/badge';
import { Loader2, Droplets, MapPin, TreePine, DollarSign, Mountain, BookOpen, Shield } from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL;

const SCORE_CONFIG = {
  logistique: { label: 'Logistique', icon: MapPin, color: '#3b82f6' },
  gros_males: { label: 'Gros Males', icon: TreePine, color: '#22c55e' },
  strategique: { label: 'Strategique', icon: Shield, color: '#f59e0b' },
  cout_roi: { label: 'Cout / ROI', icon: DollarSign, color: '#a855f7' },
  tcs: { label: 'TCS (Terrain)', icon: Mountain, color: '#ef4444' },
};

const GradeTag = ({ grade }) => {
  const colors = {
    S: 'bg-amber-500/20 text-amber-300 border-amber-500/40',
    A: 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40',
    B: 'bg-blue-500/20 text-blue-300 border-blue-500/40',
    C: 'bg-orange-500/20 text-orange-300 border-orange-500/40',
    D: 'bg-red-500/20 text-red-300 border-red-500/40',
    F: 'bg-red-800/20 text-red-400 border-red-700/40',
  };
  return (
    <span className={`px-2 py-0.5 text-xs font-bold rounded border ${colors[grade] || colors.C}`}>
      {grade}
    </span>
  );
};

const ScoreBar = ({ score, color }) => (
  <div className="w-full bg-slate-700/50 rounded-full h-2 mt-1">
    <div
      className="h-2 rounded-full transition-all duration-700"
      style={{ width: `${score}%`, backgroundColor: color }}
    />
  </div>
);

const ScoreCard = ({ scoreKey, data }) => {
  const config = SCORE_CONFIG[scoreKey];
  if (!config || !data) return null;
  const Icon = config.icon;
  return (
    <div className="bg-slate-800/60 border border-slate-700/50 rounded-lg p-3" data-testid={`saline-score-${scoreKey}`}>
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded-md" style={{ backgroundColor: `${config.color}20` }}>
            <Icon className="h-3.5 w-3.5" style={{ color: config.color }} />
          </div>
          <span className="text-sm font-medium text-slate-200">{config.label}</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-lg font-bold text-white">{data.score}</span>
          <GradeTag grade={data.grade} />
        </div>
      </div>
      <ScoreBar score={data.score} color={config.color} />
      <div className="mt-2 grid grid-cols-2 gap-x-3 gap-y-1">
        {Object.entries(data.components || {}).map(([k, v]) => (
          <div key={k} className="flex items-center justify-between text-xs">
            <span className="text-slate-500 truncate">{k.replace(/_/g, ' ')}</span>
            <span className="text-slate-300 font-medium ml-1">{v.value}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

export const SalinesFichePanel = ({ lat = 46.8139, lng = -71.2082, compact = false }) => {
  const [fiche, setFiche] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showSources, setShowSources] = useState(false);

  const loadFiche = useCallback(async () => {
    setLoading(true);
    try {
      const res = await fetch(
        `${API}/api/v1/salines-ultime/fiche?lat=${lat}&lng=${lng}&species=orignal&season=automne`
      );
      if (res.ok) {
        const data = await res.json();
        setFiche(data);
      }
    } catch (e) {
      console.error('SALINES ULTIME fetch error:', e);
    } finally {
      setLoading(false);
    }
  }, [lat, lng]);

  useEffect(() => { loadFiche(); }, [loadFiche]);

  if (loading) {
    return (
      <Card className="bg-slate-800 border-slate-700">
        <CardContent className="flex items-center justify-center p-6">
          <Loader2 className="h-6 w-6 animate-spin text-[#f5a623] mr-2" />
          <span className="text-slate-400 text-sm">Chargement FICHE SALINE...</span>
        </CardContent>
      </Card>
    );
  }

  if (!fiche) return null;

  const { global_score, scores, scientific_sources } = fiche;

  return (
    <Card className="bg-slate-800 border-slate-700" data-testid="salines-fiche-panel">
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <CardTitle className="text-base text-white flex items-center gap-2">
            <Droplets className="h-5 w-5 text-cyan-400" />
            FICHE SALINE ULTIME
          </CardTitle>
          <div className="flex items-center gap-2">
            <span className="text-2xl font-bold text-white">{global_score.score}</span>
            <GradeTag grade={global_score.grade} />
          </div>
        </div>
        <p className="text-xs text-slate-500 mt-1">
          5 scores | 20 sources scientifiques | BCE-4X GOLDEN
        </p>
      </CardHeader>
      <CardContent className="space-y-2 pt-0">
        {/* 5 Score Cards - Vertical Stack */}
        {Object.entries(scores).map(([key, data]) => (
          <ScoreCard key={key} scoreKey={key} data={data} />
        ))}

        {/* Sources Toggle */}
        {!compact && (
          <div className="pt-2">
            <button
              onClick={() => setShowSources(!showSources)}
              className="flex items-center gap-2 text-xs text-cyan-400 hover:text-cyan-300 transition-colors"
              data-testid="toggle-sources-btn"
            >
              <BookOpen className="h-3.5 w-3.5" />
              {showSources ? 'Masquer' : 'Afficher'} les {scientific_sources?.length || 20} sources
            </button>
            {showSources && (
              <div className="mt-2 bg-slate-900/60 border border-slate-700/50 rounded-lg p-3 max-h-48 overflow-y-auto">
                {(scientific_sources || []).map((src, i) => (
                  <div key={i} className="text-xs text-slate-400 py-0.5 border-b border-slate-800 last:border-0">
                    <span className="text-cyan-500 font-medium">[{src.id}]</span>{' '}
                    <span className="text-slate-300">{src.ref}</span> — {src.title}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Integration badges */}
        <div className="flex flex-wrap gap-1 pt-1">
          <Badge className="bg-slate-700/50 text-slate-400 text-[10px]">SUPRA/V6</Badge>
          <Badge className="bg-slate-700/50 text-slate-400 text-[10px]">ACCESS v7</Badge>
          <Badge className="bg-slate-700/50 text-slate-400 text-[10px]">PARTAGER</Badge>
          <Badge className="bg-slate-700/50 text-slate-400 text-[10px]">ADMIN Premium</Badge>
        </div>
      </CardContent>
    </Card>
  );
};

/**
 * SalinesFicheCompact — Version compacte pour l'overview Dashboard
 */
export const SalinesFicheCompact = ({ lat = 46.8139, lng = -71.2082 }) => {
  const [fiche, setFiche] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      try {
        const res = await fetch(
          `${API}/api/v1/salines-ultime/fiche?lat=${lat}&lng=${lng}&species=orignal&season=automne`
        );
        if (res.ok) setFiche(await res.json());
      } catch (e) {
        console.error('Salines compact load error:', e);
      } finally {
        setLoading(false);
      }
    };
    load();
  }, [lat, lng]);

  if (loading || !fiche) {
    return (
      <Card className="bg-slate-800 border-slate-700">
        <CardContent className="p-4">
          <div className="flex items-center gap-2">
            <Droplets className="h-4 w-4 text-cyan-400" />
            <span className="text-sm text-slate-400">Chargement salines...</span>
          </div>
        </CardContent>
      </Card>
    );
  }

  const { global_score, scores } = fiche;

  return (
    <Card className="bg-slate-800 border-slate-700" data-testid="salines-compact">
      <CardContent className="p-4">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <Droplets className="h-4 w-4 text-cyan-400" />
            <span className="text-sm font-medium text-white">SALINES ULTIME</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="text-xl font-bold text-white">{global_score.score}</span>
            <GradeTag grade={global_score.grade} />
          </div>
        </div>
        <div className="space-y-1.5">
          {Object.entries(scores).map(([key, data]) => {
            const config = SCORE_CONFIG[key];
            if (!config) return null;
            return (
              <div key={key} className="flex items-center justify-between text-xs">
                <span className="text-slate-400">{config.label}</span>
                <div className="flex items-center gap-2">
                  <div className="w-16 bg-slate-700/50 rounded-full h-1.5">
                    <div
                      className="h-1.5 rounded-full"
                      style={{ width: `${data.score}%`, backgroundColor: config.color }}
                    />
                  </div>
                  <span className="text-slate-200 font-medium w-6 text-right">{data.score}</span>
                </div>
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
};

export default SalinesFichePanel;

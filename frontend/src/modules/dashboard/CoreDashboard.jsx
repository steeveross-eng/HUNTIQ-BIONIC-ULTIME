/**
 * CoreDashboard - STANDARD GOLDEN — BCE-4X STEEVE-MAX
 * Intégration centrale des 5 modules core
 * GOLDEN: ZERO bordure | Accent bars | Icônes en cercles | 16px typo
 */
import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { Button } from '../../components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../../components/ui/tabs';
import { useLanguage } from '../../contexts/LanguageContext';
import { BarChart3, Cloud, FlaskConical, Target, Bot, Loader2, Beef, Gem, CircleDot, Timer, Lightbulb, Droplets } from 'lucide-react';
import useWeatherStore from '../../stores/useWeatherStore';

// Core Module Imports
import { NutritionAnalyzer, NutritionScore, NutritionCard } from '../nutrition';
import { ScoreDisplay, ScoreGauge, ScoreBreakdown } from '../scoring';
import { AIChat, AIAnalyzer, AIInsights } from '../ai';
import { StrategyPanel, StrategyTimeline } from '../strategy';

// SALINES ULTIME — BCE-4X Phase S
import { SalinesFichePanel, SalinesFicheCompact } from './SalinesFichePanel';

// Services (non-weather)
import { NutritionService } from '../nutrition/NutritionService';
import { ScoringService } from '../scoring/ScoringService';
import { AIService } from '../ai/AIService';
import { StrategyService } from '../strategy/StrategyService';

// Trip Widget
import ActiveTripWidget from '../../components/trips/ActiveTripWidget';

// STANDARD GOLDEN — Composants
const GOLDEN = { cardBg: '#1E293B', pageBg: '#0F172A', shadow: '0 2px 8px rgba(0,0,0,0.25)' };
const GCard = ({ children, accent, testId, className = '' }) => (
  <div className={`rounded-xl px-5 py-4 ${className}`} style={{ backgroundColor: GOLDEN.cardBg, boxShadow: GOLDEN.shadow, borderLeft: accent ? `4px solid ${accent}` : 'none' }} data-testid={testId}>{children}</div>
);
const GIcon = ({ Icon, color }) => (
  <div className="w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0" style={{ backgroundColor: `${color}20` }}>
    <Icon className="h-4 w-4" style={{ color }} />
  </div>
);

const DEFAULT_COORDS = { lat: 46.8139, lng: -71.2082 };

export const CoreDashboard = ({ 
  productId = null,
  productName = null,
  coordinates = DEFAULT_COORDS,
  species = 'deer',
  season = 'rut'
}) => {
  const { t } = useLanguage();
  const [activeTab, setActiveTab] = useState('overview');
  const [moduleStatus, setModuleStatus] = useState({});
  const [aiInsights, setAiInsights] = useState([]);
  const [loading, setLoading] = useState(true);

  // BCE-4X: Weather Engine v3 — source unique via Zustand store
  // Le Dashboard LIT le store, il ne fetch PAS (MonTerritoire fetch)
  const weatherCurrent = useWeatherStore(s => s.current);
  const weatherSource = useWeatherStore(s => s.source);
  const weatherLoading = useWeatherStore(s => s.loading);

  // Weather v3 -> format compatible — AUCUNE transformation/offset autorisee
  const weather = useMemo(() => {
    if (!weatherCurrent) return null;
    const w = weatherCurrent;
    return {
      temperature: w.temperature_c,
      feels_like: w.feels_like_c ?? w.temperature_c,
      humidity: w.humidity_pct,
      wind_speed: w.wind_speed_kmh,
      wind_direction: w.wind_direction_deg,
      wind_gust: w.wind_gust_kmh,
      pressure: w.pressure_hpa,
      visibility_km: w.visibility_km,
      uv_index: w.uv_index,
      condition: w.description,
      hunting_index: w.hunting_score || null,
      source: weatherSource,
    };
  }, [weatherCurrent, weatherSource]);

  // Hunting conditions derivees des donnees Weather v3 (temps reel)
  const huntingConditions = useMemo(() => {
    if (!weatherCurrent) return null;
    const w = weatherCurrent;
    const temp = w.temperature_c ?? 0;
    const wind = w.wind_speed_kmh ?? 0;
    const press = w.pressure_hpa ?? 1013;
    const hum = w.humidity_pct ?? 50;

    // Scoring deterministe
    const tempScore = temp >= -5 && temp <= 10 ? 85 : temp >= -15 && temp <= 20 ? 60 : 30;
    const windScore = wind <= 15 ? 80 : wind <= 25 ? 55 : 25;
    const pressScore = press >= 1010 && press <= 1030 ? 85 : press >= 990 ? 60 : 35;
    const humScore = hum >= 40 && hum <= 80 ? 80 : hum >= 20 && hum <= 95 ? 55 : 30;
    const overall = Math.round(tempScore * 0.3 + windScore * 0.25 + pressScore * 0.25 + humScore * 0.2);

    const getRating = (score) => score >= 80 ? 'excellent' : score >= 60 ? 'good' : score >= 40 ? 'moderate' : 'poor';

    return {
      overall_score: overall,
      temperature_rating: getRating(tempScore),
      wind_rating: getRating(windScore),
      pressure_rating: getRating(pressScore),
      humidity_rating: getRating(humScore),
      recommendation: overall >= 70
        ? 'Conditions favorables pour la chasse'
        : overall >= 50
        ? 'Conditions moderees — soyez strategique'
        : 'Conditions difficiles — prudence recommandee',
      factors: {
        temperature: { score: tempScore, impact: tempScore >= 70 ? 'positive' : 'neutral' },
        wind: { score: windScore, impact: windScore >= 70 ? 'positive' : 'neutral' },
        pressure: { score: pressScore, impact: pressScore >= 70 ? 'very_positive' : 'neutral' },
        humidity: { score: humScore, impact: humScore >= 70 ? 'positive' : 'neutral' },
      },
    };
  }, [weatherCurrent]);

  // Load non-weather data — BCE-4X: Dashboard ne fetch PAS la meteo (lecture store seule)
  const loadDashboardData = useCallback(async () => {
    setLoading(true);
    
    try {
      // BCE-4X: PAS de fetchWeather ici — MonTerritoire est la source unique

      // Load AI insights
      const insights = await AIService.getInsights({
        species,
        season,
        location: coordinates
      }).catch(() => ({ insights: [] }));
      setAiInsights(insights.insights || []);

      // Check module health
      const healthChecks = await Promise.all([
        NutritionService.getHealth().catch(() => ({ status: 'error' })),
        ScoringService.getHealth().catch(() => ({ status: 'error' })),
        { status: weatherCurrent ? 'operational' : 'loading' },
        AIService.getHealth().catch(() => ({ status: 'error' })),
        StrategyService.getHealth().catch(() => ({ status: 'error' }))
      ]);

      setModuleStatus({
        nutrition: healthChecks[0].status === 'operational',
        scoring: healthChecks[1].status === 'operational',
        weather: !!weatherCurrent || weatherLoading,
        ai: healthChecks[3].status === 'operational',
        strategy: healthChecks[4].status === 'operational'
      });

    } catch (error) {
      console.error('Dashboard load error:', error);
    } finally {
      setLoading(false);
    }
  }, [coordinates, species, season, weatherCurrent, weatherLoading]);

  useEffect(() => {
    loadDashboardData();
  }, [loadDashboardData]);

  if (loading && !weatherCurrent) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <Loader2 className="h-10 w-10 animate-spin text-[#f5a623] mx-auto mb-4" />
          <p className="text-slate-400">{t('dashboard_loading')}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6" data-testid="core-dashboard" style={{ backgroundColor: GOLDEN.pageBg }}>
      {/* Header — STANDARD GOLDEN */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-3">
            <GIcon Icon={Target} color="#f5a623" />
            {t('dashboard_title')}
          </h1>
          <p className="text-[14px] text-slate-400 mt-1">
            {t('dashboard_modules_core')}
          </p>
        </div>
        
        {/* Module Status — GOLDEN badges */}
        <div className="flex items-center gap-2">
          {Object.entries(moduleStatus).map(([module, isOnline]) => (
            <span key={module} className="text-[14px] font-semibold px-2.5 py-0.5 rounded-lg"
              style={{ backgroundColor: isOnline ? '#00C85318' : '#D32F2F18', color: isOnline ? '#00C853' : '#D32F2F' }}>
              {isOnline ? '\u25CF' : '\u25CB'} {module}
            </span>
          ))}
        </div>
      </div>

      {/* Tab Navigation — GOLDEN */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="border-none w-full justify-start" style={{ backgroundColor: GOLDEN.cardBg }}>
          <TabsTrigger value="overview" className="data-[state=active]:bg-[#f5a623] data-[state=active]:text-black text-[14px] font-bold">
            <BarChart3 className="h-4 w-4 mr-2" />
            {t('dashboard_tab_overview')}
          </TabsTrigger>
          <TabsTrigger value="weather" className="data-[state=active]:bg-[#f5a623] data-[state=active]:text-black text-[14px] font-bold">
            <Cloud className="h-4 w-4 mr-2" />
            {t('dashboard_tab_weather')}
          </TabsTrigger>
          <TabsTrigger value="analysis" className="data-[state=active]:bg-[#f5a623] data-[state=active]:text-black text-[14px] font-bold">
            <FlaskConical className="h-4 w-4 mr-2" />
            {t('dashboard_tab_analysis')}
          </TabsTrigger>
          <TabsTrigger value="strategy" className="data-[state=active]:bg-[#f5a623] data-[state=active]:text-black text-[14px] font-bold">
            <Target className="h-4 w-4 mr-2" />
            {t('dashboard_tab_strategy')}
          </TabsTrigger>
          <TabsTrigger value="ai" className="data-[state=active]:bg-[#f5a623] data-[state=active]:text-black text-[14px] font-bold">
            <Bot className="h-4 w-4 mr-2" />
            {t('dashboard_tab_ai')}
          </TabsTrigger>
          <TabsTrigger value="salines" className="data-[state=active]:bg-[#f5a623] data-[state=active]:text-black text-[14px] font-bold">
            <Droplets className="h-4 w-4 mr-2" />
            SALINES
          </TabsTrigger>
        </TabsList>

        {/* Overview Tab — STANDARD GOLDEN 3 colonnes */}
        <TabsContent value="overview" className="mt-6">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
            {/* Left Column - Weather V3 Data */}
            <div className="space-y-4">
              <GCard accent="#2196F3" testId="dashboard-weather-card">
                <div className="flex items-center gap-3 mb-3">
                  <GIcon Icon={Cloud} color="#2196F3" />
                  <span className="text-[16px] font-bold text-white">Meteo V3</span>
                </div>
                {weather ? (
                  <div className="text-[16px] text-slate-300 space-y-1">
                    <div className="flex justify-between py-0.5"><span className="text-[14px] text-slate-400">Temperature</span><span className="text-[16px] font-semibold text-white">{weather.temperature}°C</span></div>
                    <div className="flex justify-between py-0.5"><span className="text-[14px] text-slate-400">Vent</span><span className="text-[16px] font-semibold text-white">{weather.wind_speed} km/h ({weather.wind_direction}°)</span></div>
                    <div className="flex justify-between py-0.5"><span className="text-[14px] text-slate-400">Humidite</span><span className="text-[16px] font-semibold text-white">{weather.humidity}%</span></div>
                  </div>
                ) : (
                  <p className="text-[16px] text-slate-500">Chargement...</p>
                )}
              </GCard>
            </div>

            {/* Center Column - Scores & Analysis */}
            <div className="space-y-4">
              <GCard accent="#f5a623" testId="dashboard-scores-card">
                <div className="flex items-center gap-3 mb-3">
                  <GIcon Icon={BarChart3} color="#f5a623" />
                  <span className="text-[16px] font-bold text-white">{t('dashboard_quick_scores')}</span>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <ScoreDisplay 
                    score={huntingConditions?.overall_score || 0}
                    label={t('dashboard_conditions')}
                    size="md"
                  />
                  <ScoreGauge 
                    value={huntingConditions?.overall_score || 0}
                    label={t('dashboard_hunting_index')}
                    color="#f5a623"
                  />
                </div>
              </GCard>

              {/* Quick Nutrition Cards */}
              <div className="grid grid-cols-2 gap-3">
                <NutritionCard title={t('dashboard_proteins')} value="24.5" unit="g" IconComponent={Beef} color="emerald" />
                <NutritionCard title={t('dashboard_minerals')} value="8.2" unit="g" IconComponent={Gem} color="blue" />
                <NutritionCard title={t('dashboard_attractiveness')} value="92" unit="%" IconComponent={CircleDot} color="amber" />
                <NutritionCard title={t('dashboard_effect_duration')} value="48" unit="h" IconComponent={Timer} color="purple" />
              </div>
            </div>

            {/* Right Column - AI Insights & Active Trip & Salines */}
            <div className="space-y-4">
              <ActiveTripWidget />
              <SalinesFicheCompact lat={coordinates.lat} lng={coordinates.lng} />
              <AIInsights 
                insights={aiInsights.length > 0 ? aiInsights : [
                  { type: 'tip', title: t('dashboard_optimal_period'), message: t('dashboard_rut_peak') },
                  { type: 'trend', title: t('dashboard_increased_activity'), message: t('dashboard_movement_forecast') },
                  { type: 'warning', title: t('dashboard_unfavorable_wind'), message: t('dashboard_south_wind') }
                ]}
              />
              <GCard accent="#00C853" testId="dashboard-next-action">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-[14px] text-slate-400">Prochaine action</p>
                    <p className="text-[16px] text-white font-semibold">Repositionnement recommande</p>
                  </div>
                  <Button size="sm" className="bg-[#f5a623] text-black hover:bg-[#d4890e] font-bold">
                    Voir details
                  </Button>
                </div>
              </GCard>
            </div>
          </div>
        </TabsContent>

        {/* Weather Tab — STANDARD GOLDEN */}
        <TabsContent value="weather" className="mt-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <GCard accent="#2196F3" testId="dashboard-weather-detail">
              <div className="flex items-center gap-3 mb-3">
                <GIcon Icon={Cloud} color="#2196F3" />
                <span className="text-[16px] font-bold text-white">Meteo V3 — Open-Meteo GFS</span>
              </div>
              {weather ? (
                <div className="space-y-1">
                  {[
                    { l: 'Temperature', v: `${weather.temperature}°C` },
                    { l: 'Vent', v: `${weather.wind_speed} km/h dir ${weather.wind_direction}°` },
                    { l: 'Rafales', v: `${weather.wind_gust || '--'} km/h` },
                    { l: 'Humidite', v: `${weather.humidity}%` },
                    { l: 'Pression', v: `${weather.pressure} hPa` },
                  ].map((r, i) => (
                    <div key={i} className="flex justify-between py-1">
                      <span className="text-[14px] text-slate-400">{r.l}</span>
                      <span className="text-[16px] font-semibold text-white">{r.v}</span>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-[16px] text-slate-500">Chargement...</p>
              )}
            </GCard>
            <div className="space-y-4">
              <ScoreBreakdown 
                title="Facteurs Meteorologiques (Weather v3)"
                breakdown={[
                  { name: 'Temperature', value: huntingConditions?.factors?.temperature?.score || 0, color: '#f59e0b' },
                  { name: 'Humidite', value: huntingConditions?.factors?.humidity?.score || 0, color: '#3b82f6' },
                  { name: 'Pression', value: huntingConditions?.factors?.pressure?.score || 0, color: '#8b5cf6' },
                  { name: 'Vent', value: huntingConditions?.factors?.wind?.score || 0, color: '#22c55e' },
                ]}
              />
            </div>
          </div>
        </TabsContent>

        {/* Analysis Tab — STANDARD GOLDEN */}
        <TabsContent value="analysis" className="mt-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <div className="space-y-4">
              <NutritionAnalyzer productId={productId || 'demo-product'} productName={productName || 'Attractant Demo'} />
              <GCard accent="#f5a623" testId="dashboard-nutrition-score">
                <div className="flex items-center gap-3 mb-3">
                  <GIcon Icon={Target} color="#f5a623" />
                  <span className="text-[16px] font-bold text-white">Score Nutritionnel</span>
                </div>
                <div className="flex justify-center">
                  <NutritionScore score={78} size="lg" />
                </div>
              </GCard>
            </div>
            <div className="space-y-4">
              <AIAnalyzer productId={productId || 'demo-product'} productName={productName || 'Attractant Demo'} />
              <ScoreBreakdown 
                title="Criteres d'Analyse (13 criteres)"
                breakdown={[
                  { name: 'Composition', value: 85, color: '#10b981' },
                  { name: 'Concentration', value: 72, color: '#22c55e' },
                  { name: 'Persistance', value: 68, color: '#84cc16' },
                  { name: 'Attractivite', value: 91, color: '#f59e0b' },
                  { name: 'Dispersion', value: 76, color: '#3b82f6' },
                  { name: 'Resistance', value: 64, color: '#8b5cf6' }
                ]}
              />
            </div>
          </div>
        </TabsContent>

        {/* Strategy Tab — STANDARD GOLDEN */}
        <TabsContent value="strategy" className="mt-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <StrategyPanel species={species} season={season} weather={weather} />
            <div className="space-y-4">
              <StrategyTimeline 
                schedule={[
                  { time: '05:30', activity: 'Mise en place', notes: 'Arrivee silencieuse', location: 'Cache principale' },
                  { time: '06:00', activity: 'Observation aube', notes: 'Premier mouvement attendu' },
                  { time: '08:30', activity: 'Appel discret', notes: 'Utiliser le grunt call' },
                  { time: '11:00', activity: 'Pause midi', notes: 'Repos et collation' },
                  { time: '15:30', activity: 'Repositionnement', notes: 'Zone sud-est', location: 'Point B' },
                  { time: '17:00', activity: 'Session soir', notes: 'Periode la plus active' },
                  { time: '19:00', activity: 'Fin de session', notes: 'Retrait discret' }
                ]}
              />
              <GCard accent="#00C853" testId="dashboard-conseil-jour">
                <div className="flex items-center gap-3 mb-2">
                  <GIcon Icon={Lightbulb} color="#00C853" />
                  <span className="text-[16px] font-bold text-white">Conseil du jour</span>
                </div>
                <p className="text-[16px] text-slate-300 leading-relaxed">
                  Les conditions meteo actuelles sont favorables pour la chasse a l'affut. 
                  Le vent du nord-ouest maintiendra votre odeur loin des zones de passage.
                </p>
              </GCard>
            </div>
          </div>
        </TabsContent>

        {/* AI Tab — STANDARD GOLDEN */}
        <TabsContent value="ai" className="mt-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <AIChat context={{ species, season, weather, location: coordinates }} />
            <div className="space-y-4">
              <AIInsights 
                insights={[
                  { type: 'success', title: 'Conditions optimales', message: 'La pression atmospherique est stable.' },
                  { type: 'tip', title: 'Strategie recommandee', message: 'Grunt call agressif apres 8h.' },
                  { type: 'trend', title: 'Prediction activite', message: 'Pic entre 6h30-8h00 et 16h30-18h00.' },
                  { type: 'info', title: 'Phase lunaire', message: 'Lune gibbeuse decroissante.' },
                  { type: 'warning', title: 'Attention', message: 'Changement meteo prevu dans 48h.' }
                ]}
              />
            </div>
          </div>
        </TabsContent>

        {/* SALINES ULTIME Tab — STANDARD GOLDEN */}
        <TabsContent value="salines" className="mt-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <SalinesFichePanel lat={coordinates.lat} lng={coordinates.lng} />
            <div className="space-y-4">
              <ScoreBreakdown 
                title="Facteurs Salines (5 dimensions)"
                breakdown={[
                  { name: 'Logistique', value: 76, color: '#3b82f6' },
                  { name: 'Gros Males', value: 79, color: '#22c55e' },
                  { name: 'Strategique', value: 80, color: '#f59e0b' },
                  { name: 'Cout/ROI', value: 67, color: '#a855f7' },
                  { name: 'TCS', value: 67, color: '#ef4444' },
                ]}
              />
              <GCard accent="#00BCD4" testId="dashboard-salines-protocol">
                <div className="flex items-center gap-3 mb-2">
                  <GIcon Icon={Droplets} color="#00BCD4" />
                  <span className="text-[16px] font-bold text-white">Protocole SALINES BIONIC ULTIME</span>
                </div>
                <p className="text-[16px] text-slate-300 leading-relaxed">
                  Analyse scientifique complete basee sur 20 sources academiques. 
                  5 scores independants evaluent la qualite logistique et le potentiel.
                </p>
                <div className="flex flex-wrap gap-1 mt-3">
                  <span className="text-[14px] font-semibold px-2.5 py-0.5 rounded-lg" style={{ backgroundColor: '#00BCD418', color: '#00BCD4' }}>20 Sources</span>
                  <span className="text-[14px] font-semibold px-2.5 py-0.5 rounded-lg" style={{ backgroundColor: '#00BCD418', color: '#00BCD4' }}>5 Scores</span>
                  <span className="text-[14px] font-semibold px-2.5 py-0.5 rounded-lg" style={{ backgroundColor: '#00BCD418', color: '#00BCD4' }}>BCE-4X GOLDEN</span>
                </div>
              </GCard>
            </div>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default CoreDashboard;

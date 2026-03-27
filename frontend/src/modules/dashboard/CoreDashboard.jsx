/**
 * CoreDashboard - Central dashboard integrating all 5 core modules
 * BCE-4X: Weather Engine v3 UNIFIED — source unique useWeatherStore
 * Phase 8 - Frontend Core Integration
 */
import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../../components/ui/tabs';
import { Badge } from '../../components/ui/badge';
import { useLanguage } from '../../contexts/LanguageContext';
import { BarChart3, Cloud, FlaskConical, Target, Bot, Loader2, Beef, Gem, CircleDot, Timer, Lightbulb } from 'lucide-react';
import useWeatherStore from '../../stores/useWeatherStore';

// Core Module Imports
import { NutritionAnalyzer, NutritionScore, NutritionCard } from '../nutrition';
import { ScoreDisplay, ScoreGauge, ScoreBreakdown } from '../scoring';
import { WeatherWidget, WindRose, HuntingConditions } from '../weather';
import { AIChat, AIAnalyzer, AIInsights } from '../ai';
import { StrategyPanel, StrategyTimeline } from '../strategy';

// Services (non-weather)
import { NutritionService } from '../nutrition/NutritionService';
import { ScoringService } from '../scoring/ScoringService';
import { AIService } from '../ai/AIService';
import { StrategyService } from '../strategy/StrategyService';

// Trip Widget
import ActiveTripWidget from '../../components/trips/ActiveTripWidget';

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
  }, [coordinates, species, season, fetchWeather, weatherCurrent, weatherLoading]);

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
    <div className="space-y-6" data-testid="core-dashboard">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-3">
            <Target className="h-7 w-7 text-[#f5a623]" />
            {t('dashboard_title')}
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            {t('dashboard_modules_core')}
          </p>
        </div>
        
        {/* Module Status */}
        <div className="flex items-center gap-2">
          {Object.entries(moduleStatus).map(([module, isOnline]) => (
            <Badge 
              key={module}
              className={`${isOnline ? 'bg-emerald-900/50 text-emerald-400' : 'bg-red-900/50 text-red-400'}`}
            >
              {isOnline ? '●' : '○'} {module}
            </Badge>
          ))}
        </div>
      </div>

      {/* Tab Navigation */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="bg-slate-800 border border-slate-700 w-full justify-start">
          <TabsTrigger value="overview" className="data-[state=active]:bg-[#f5a623] data-[state=active]:text-black">
            <BarChart3 className="h-4 w-4 mr-2" />
            {t('dashboard_tab_overview')}
          </TabsTrigger>
          <TabsTrigger value="weather" className="data-[state=active]:bg-[#f5a623] data-[state=active]:text-black">
            <Cloud className="h-4 w-4 mr-2" />
            {t('dashboard_tab_weather')}
          </TabsTrigger>
          <TabsTrigger value="analysis" className="data-[state=active]:bg-[#f5a623] data-[state=active]:text-black">
            <FlaskConical className="h-4 w-4 mr-2" />
            {t('dashboard_tab_analysis')}
          </TabsTrigger>
          <TabsTrigger value="strategy" className="data-[state=active]:bg-[#f5a623] data-[state=active]:text-black">
            <Target className="h-4 w-4 mr-2" />
            {t('dashboard_tab_strategy')}
          </TabsTrigger>
          <TabsTrigger value="ai" className="data-[state=active]:bg-[#f5a623] data-[state=active]:text-black">
            <Bot className="h-4 w-4 mr-2" />
            {t('dashboard_tab_ai')}
          </TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview" className="mt-6">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Left Column - Weather & Conditions */}
            <div className="space-y-4">
              <WeatherWidget 
                lat={coordinates.lat} 
                lng={coordinates.lng}
              />
              
              <HuntingConditions 
                conditions={huntingConditions}
                species={species}
              />
            </div>

            {/* Center Column - Scores & Analysis */}
            <div className="space-y-4">
              <Card className="bg-slate-800 border-slate-700">
                <CardHeader className="pb-3">
                  <CardTitle className="text-lg text-white flex items-center gap-2">
                    <BarChart3 className="h-5 w-5 text-[#f5a623]" />
                    {t('dashboard_quick_scores')}
                  </CardTitle>
                </CardHeader>
                <CardContent>
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
                </CardContent>
              </Card>

              {/* Quick Nutrition Cards */}
              <div className="grid grid-cols-2 gap-3">
                <NutritionCard 
                  title={t('dashboard_proteins')}
                  value="24.5"
                  unit="g"
                  IconComponent={Beef}
                  color="emerald"
                />
                <NutritionCard 
                  title={t('dashboard_minerals')}
                  value="8.2"
                  unit="g"
                  IconComponent={Gem}
                  color="blue"
                />
                <NutritionCard 
                  title={t('dashboard_attractiveness')}
                  value="92"
                  unit="%"
                  IconComponent={CircleDot}
                  color="amber"
                />
                <NutritionCard 
                  title={t('dashboard_effect_duration')}
                  value="48"
                  unit="h"
                  IconComponent={Timer}
                  color="purple"
                />
              </div>
            </div>

            {/* Right Column - AI Insights & Active Trip */}
            <div className="space-y-4">
              {/* Active Trip Widget */}
              <ActiveTripWidget />
              
              <AIInsights 
                insights={aiInsights.length > 0 ? aiInsights : [
                  { type: 'tip', title: t('dashboard_optimal_period'), message: t('dashboard_rut_peak') },
                  { type: 'trend', title: t('dashboard_increased_activity'), message: t('dashboard_movement_forecast') },
                  { type: 'warning', title: t('dashboard_unfavorable_wind'), message: t('dashboard_south_wind') }
                ]}
              />
              
              <Card className="bg-slate-800 border-slate-700">
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-slate-400 text-xs">Prochaine action</p>
                      <p className="text-white font-medium">Repositionnement recommandé</p>
                    </div>
                    <Button size="sm" className="bg-[#f5a623] text-black hover:bg-[#d4890e]">
                      Voir détails
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </TabsContent>

        {/* Weather Tab */}
        <TabsContent value="weather" className="mt-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="space-y-4">
              <WeatherWidget 
                lat={coordinates.lat} 
                lng={coordinates.lng}
              />
              
              <Card className="bg-slate-800 border-slate-700">
                <CardHeader>
                  <CardTitle className="text-white flex items-center gap-2">
                    <Cloud className="w-5 h-5 text-slate-400" />
                    Direction du Vent
                  </CardTitle>
                </CardHeader>
                <CardContent className="flex justify-center">
                  <WindRose 
                    direction={weather?.wind_direction || 225}
                    speed={weather?.wind_speed || 12}
                    size={180}
                  />
                </CardContent>
              </Card>
            </div>

            <div className="space-y-4">
              <HuntingConditions 
                conditions={huntingConditions}
                species={species}
              />
              
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

        {/* Analysis Tab */}
        <TabsContent value="analysis" className="mt-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="space-y-4">
              <NutritionAnalyzer 
                productId={productId || 'demo-product'}
                productName={productName || 'Attractant Demo'}
              />
              
              <Card className="bg-slate-800 border-slate-700">
                <CardHeader>
                  <CardTitle className="text-white flex items-center gap-2">
                    <Target className="h-5 w-5 text-[#f5a623]" />
                    Score Nutritionnel
                  </CardTitle>
                </CardHeader>
                <CardContent className="flex justify-center">
                  <NutritionScore score={78} size="lg" />
                </CardContent>
              </Card>
            </div>

            <div className="space-y-4">
              <AIAnalyzer 
                productId={productId || 'demo-product'}
                productName={productName || 'Attractant Demo'}
              />
              
              <ScoreBreakdown 
                title="Critères d'Analyse (13 critères)"
                breakdown={[
                  { name: 'Composition', value: 85, color: '#10b981' },
                  { name: 'Concentration', value: 72, color: '#22c55e' },
                  { name: 'Persistance', value: 68, color: '#84cc16' },
                  { name: 'Attractivité', value: 91, color: '#f59e0b' },
                  { name: 'Dispersion', value: 76, color: '#3b82f6' },
                  { name: 'Résistance', value: 64, color: '#8b5cf6' }
                ]}
              />
            </div>
          </div>
        </TabsContent>

        {/* Strategy Tab */}
        <TabsContent value="strategy" className="mt-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <StrategyPanel 
              species={species}
              season={season}
              weather={weather}
            />

            <div className="space-y-4">
              <StrategyTimeline 
                schedule={[
                  { time: '05:30', activity: 'Mise en place', notes: 'Arrivée silencieuse', location: 'Cache principale' },
                  { time: '06:00', activity: 'Observation aube', notes: 'Premier mouvement attendu' },
                  { time: '08:30', activity: 'Appel discret', notes: 'Utiliser le grunt call' },
                  { time: '11:00', activity: 'Pause midi', notes: 'Repos et collation' },
                  { time: '15:30', activity: 'Repositionnement', notes: 'Zone sud-est', location: 'Point B' },
                  { time: '17:00', activity: 'Session soir', notes: 'Période la plus active' },
                  { time: '19:00', activity: 'Fin de session', notes: 'Retrait discret' }
                ]}
              />
              
              <Card className="bg-gradient-to-br from-emerald-900/30 to-slate-900 border-emerald-700/50">
                <CardContent className="p-4">
                  <h4 className="text-emerald-400 font-medium mb-2 flex items-center gap-2">
                    <Lightbulb className="h-4 w-4" />
                    Conseil du jour
                  </h4>
                  <p className="text-slate-300 text-sm">
                    Les conditions météo actuelles sont favorables pour la chasse à l'affût. 
                    Le vent du nord-ouest maintiendra votre odeur loin des zones de passage.
                    Privilégiez les heures dorées (aube/crépuscule).
                  </p>
                </CardContent>
              </Card>
            </div>
          </div>
        </TabsContent>

        {/* AI Tab */}
        <TabsContent value="ai" className="mt-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <AIChat 
              context={{
                species,
                season,
                weather,
                location: coordinates
              }}
            />
            
            <div className="space-y-4">
              <AIInsights 
                insights={[
                  { type: 'success', title: 'Conditions optimales', message: 'La pression atmosphérique est stable - excellent pour l\'activité du gibier.' },
                  { type: 'tip', title: 'Stratégie recommandée', message: 'Utilisez l\'appel de contact en début de session, puis passez au grunt agressif après 8h.' },
                  { type: 'trend', title: 'Prédiction d\'activité', message: 'Pic d\'activité prévu entre 6h30-8h00 et 16h30-18h00.' },
                  { type: 'info', title: 'Phase lunaire', message: 'Lune gibbeuse décroissante - activité nocturne modérée.' },
                  { type: 'warning', title: 'Attention', message: 'Changement météo prévu dans 48h - profitez des conditions actuelles.' }
                ]}
              />
            </div>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default CoreDashboard;

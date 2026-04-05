/**
 * Data Contracts V6 — Validation et normalisation
 * Directive x7000-M3-DASHBOARD | BCE-4X GOLDEN V6+
 * 
 * ZERO INTERPRETATION : schemas stricts, valeurs par defaut si champ manquant.
 */

const DEFAULT_FACTORS = { base_activity: 0, season: 0, solunar: 0, meteo: 0, historical: 0, nutrition: 0 };

const DEFAULT_SCORE_CONSOLIDE = {
  global: 0, rating: 'D',
  components: { predictive: 0, solunar: 0, meteo: 0, nutrition: 0, territory: 0, legal: 0 },
  weights: { predictive: 0.25, solunar: 0.15, meteo: 0.20, nutrition: 0.15, territory: 0.15, legal: 0.10 },
  trend: 'stable', confidence: 0, computed_at: new Date().toISOString(),
};

function getRating(score) {
  if (score >= 90) return 'A+';
  if (score >= 80) return 'A';
  if (score >= 65) return 'B+';
  if (score >= 50) return 'B';
  if (score >= 35) return 'C';
  return 'D';
}

function getRatingColor(rating) {
  const colors = { 'A+': '#22c55e', 'A': '#3b82f6', 'B+': '#f5a623', 'B': '#eab308', 'C': '#f97316', 'D': '#ef4444' };
  return colors[rating] || '#6b7280';
}

export function validateConsolidatedView(raw) {
  const pl = raw?.predictive_layer || raw || {};
  const preds = Array.isArray(pl.predictions) ? pl.predictions : [];
  return {
    zone_id: raw?.zone_id || '',
    species: raw?.species || '',
    target_date: raw?.target_date || '',
    predictive_layer: {
      predictions: preds.map(p => ({
        hour: p.hour ?? 0,
        probability: p.probability ?? 0,
        confidence: p.confidence ?? 0,
        factors: { ...DEFAULT_FACTORS, ...(p.factors || {}) },
      })),
      aggregation: {
        peak_probability: pl.aggregation?.peak_probability ?? 0,
        peak_hour: pl.aggregation?.peak_hour ?? 0,
        best_window: pl.aggregation?.best_window || { start: 0, end: 0 },
        trend: pl.aggregation?.trend || 'stable',
        avg_confidence: pl.aggregation?.avg_confidence ?? 0,
      },
    },
    solunar: {
      phase_name: raw?.solunar_context?.phase_name || raw?.solunar?.phase_name || 'unknown',
      illumination: raw?.solunar_context?.illumination ?? raw?.solunar?.illumination ?? 0,
      solunar_score: raw?.solunar_context?.solunar_score ?? raw?.solunar?.solunar_score ?? 0,
      hunting_windows: raw?.solunar_context?.hunting_windows || raw?.solunar?.hunting_windows || [],
    },
    meteo: {
      activity_multiplier: raw?.meteo_context?.activity_multiplier ?? raw?.meteo?.activity_multiplier ?? 0.65,
      recommendation: raw?.meteo_context?.recommendation || raw?.meteo?.recommendation || '',
      limiting_factor: raw?.meteo_context?.limiting_factor || raw?.meteo?.limiting_factor || 'none',
    },
    legal: { province: raw?.legal?.province || '', zone_chasse: raw?.legal?.zone_chasse || '', is_season_open: raw?.legal?.is_season_open ?? true },
    poi_count: raw?.poi_count_in_zone ?? raw?.poi_count ?? 0,
    data_freshness: raw?.computed_at || new Date().toISOString(),
  };
}

export function validateScoreConsolide(components) {
  const c = { ...DEFAULT_SCORE_CONSOLIDE.components, ...(components || {}) };
  const w = DEFAULT_SCORE_CONSOLIDE.weights;
  const global = Math.round(
    c.predictive * w.predictive + c.solunar * w.solunar + c.meteo * w.meteo +
    c.nutrition * w.nutrition + c.territory * w.territory + c.legal * w.legal
  );
  const clamped = Math.max(0, Math.min(100, global));
  return {
    global: clamped, rating: getRating(clamped), ratingColor: getRatingColor(getRating(clamped)),
    components: c, weights: w,
    trend: 'stable', confidence: 0.7, computed_at: new Date().toISOString(),
  };
}

export function validateHeatmapData(raw) {
  return {
    zone_id: raw?.zone_id || '',
    species: raw?.species || '',
    points: (raw?.points || []).map(p => ({
      poi_id: p.poi_id || '', name: p.name || '', type: p.type || '',
      lat: p.lat ?? 0, lng: p.lng ?? 0,
      probability: p.probability ?? 0, poi_score: p.poi_score ?? 0,
      intensity: p.intensity || 'low',
    })),
    total_pois: raw?.total_pois ?? 0,
    computed_at: raw?.computed_at || new Date().toISOString(),
  };
}

export function validateTimeSeries(raw) {
  return {
    zone_id: raw?.zone_id || '', species: raw?.species || '', metric: raw?.metric || '',
    values: (raw?.values || []).map(v => ({ timestamp: v.timestamp || '', value: v.value ?? 0, source: v.source || '' })),
    total_points: raw?.total_points ?? 0,
    latest_value: raw?.latest_value ?? 0,
    granularity: raw?.granularity || 'hourly',
  };
}

export function validateTrends(raw) {
  return {
    species: raw?.species || '', zone_id: raw?.zone_id || '', year: raw?.year ?? 2026,
    monthly_patterns: (raw?.monthly_patterns || []).map(mp => ({
      month: mp.month ?? 0, activity_index: mp.activity_index ?? 0,
      peak_hours: mp.peak_hours || [], observation_count: mp.observation_count ?? 0,
      trend_vs_previous: mp.trend_vs_previous || 'stable', baseline_factor: mp.baseline_factor ?? 0,
      confidence: mp.confidence ?? 0,
    })),
    annual_summary: {
      peak_month: raw?.annual_summary?.peak_month ?? 0, peak_activity: raw?.annual_summary?.peak_activity ?? 0,
      low_month: raw?.annual_summary?.low_month ?? 0, low_activity: raw?.annual_summary?.low_activity ?? 0,
      avg_activity: raw?.annual_summary?.avg_activity ?? 0,
    },
  };
}

export function validateCorrelation(raw) {
  return {
    zone_id: raw?.zone_id || '', species: raw?.species || '',
    correlation_matrix: raw?.correlation_matrix || {},
    optimal_conditions: raw?.optimal_conditions || {},
    solunar_context: raw?.solunar_context || {},
    confidence: raw?.confidence ?? 0,
  };
}

export function validateBestTimes(raw) {
  return {
    zone_id: raw?.zone_id || '', species: raw?.species || '', target_date: raw?.target_date || '',
    best_windows: (raw?.best_windows || []).map(w => ({
      start_hour: w.start_hour ?? 0, end_hour: w.end_hour ?? 0,
      label: w.label || '', period: w.period || '',
      avg_probability: w.avg_probability ?? 0, peak_probability: w.peak_probability ?? 0,
      dominant_factor: w.dominant_factor || '',
    })),
    solunar_windows: raw?.solunar_windows || [],
    recommendation: raw?.recommendation || '',
  };
}

export { getRating, getRatingColor };

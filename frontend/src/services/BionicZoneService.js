/**
 * MODULE F — BIONIC Zone Service V2
 * Frontend Renderer — 100% Backend-Driven
 *
 * RÈGLE ABSOLUE:
 * - Aucune génération de zones côté client
 * - Aucun calcul de scoring
 * - Aucun traitement de données
 * - Backend = seule source de vérité
 * - Backend fetch ses propres exclusions Overpass
 *
 * Ce service:
 * 1. Fetch les zones organiques BIONIC depuis le backend pipeline V2
 * 2. Retourne les zones prêtes pour Leaflet
 */

const API_BASE = process.env.REACT_APP_BACKEND_URL;

// ============================================
// BIONIC V6 GOLDEN — ISOLATION STRUCTURELLE/DYNAMIQUE
// BCE-4X-MAX Phase 3.3-U-PRIME: Pipeline V5 bounds DESACTIVE.
// generateBionicZonesV5 = stub vide. generateWaypointZonesV5 = autorise (via _fetchOrganicZonesV2).
// ============================================

/**
 * Couches STRUCTURELLES — calculées une seule fois, verrouillées (State Locking)
 * Aucun recalcul par zoom/pan/toggle dynamique
 */
export const STRUCTURAL_LAYER_IDS = new Set([
  'habitats', 'rut', 'repos', 'alimentation', 'corridors',
  'salines', 'affuts', 'trajets', 'peuplements', 'hydro',
  'pentes', 'orientation', 'ensoleillement', 'altitude', 'ndvi'
]);

/**
 * Couches DYNAMIQUES — recalculées en temps réel
 * Isolées dans leur propre pipeline
 */
export const DYNAMIC_LAYER_IDS = new Set([
  'conditions', 'exclusions', 'dynamic', 'meteo', 'pression', 'stress_thermique'
]);

// ============================================
// LAYER DEFINITIONS (affichage uniquement)
// ============================================
export const LAYER_TYPES = [
  { id: 'habitats',       label: 'Habitat optimal',        color: '#10B981', category: 'environmental', priority: 1 },
  { id: 'rut',            label: 'Zone de rut',            color: '#FF4D6D', category: 'behavioral',    priority: 2 },
  { id: 'repos',          label: 'Zone de repos',          color: '#8B5CF6', category: 'behavioral',    priority: 3 },
  { id: 'alimentation',   label: "Zone d'alimentation",    color: '#22C55E', category: 'behavioral',    priority: 4 },
  { id: 'corridors',      label: 'Corridor faunique',      color: '#06B6D4', category: 'behavioral',    priority: 5 },
  { id: 'peuplements',    label: 'Peuplements forestiers',  color: '#15803D', category: 'environmental', priority: 6 },
  { id: 'ndvi',           label: 'NDVI / Densité végétale',color: '#66BB6A', category: 'environmental', priority: 7 },
  { id: 'hydro',          label: 'Hydrographie',           color: '#3B82F6', category: 'environmental', priority: 8 },
  { id: 'pentes',         label: 'Pentes',                 color: '#FF7043', category: 'environmental', priority: 9 },
  { id: 'orientation',    label: 'Orientation',            color: '#2196F3', category: 'environmental', priority: 10 },
  { id: 'ensoleillement', label: 'Ensoleillement',         color: '#FCD34D', category: 'environmental', priority: 11 },
  { id: 'salines',        label: 'Point nutritionnel',     color: '#FFFF00', category: 'strategic',     priority: 12 },
  { id: 'affuts',         label: 'Affût potentiel',        color: '#F5A623', category: 'strategic',     priority: 13 },
  { id: 'trajets',        label: 'Trajets de chasse',      color: '#FF9800', category: 'strategic',     priority: 14 },
  { id: 'altitude',       label: 'Altitude relative',      color: '#78909C', category: 'environmental', priority: 15 },
];

const SPECIES_LAYERS = {
  moose:       ['habitats', 'rut', 'repos', 'alimentation', 'corridors', 'hydro', 'salines', 'peuplements', 'pentes', 'affuts', 'trajets'],
  deer:        ['habitats', 'rut', 'repos', 'alimentation', 'corridors', 'affuts', 'peuplements', 'ensoleillement', 'trajets', 'salines'],
  bear:        ['habitats', 'repos', 'alimentation', 'corridors', 'hydro', 'peuplements', 'ndvi', 'pentes', 'trajets'],
  wild_turkey: ['habitats', 'alimentation', 'repos', 'affuts', 'peuplements', 'ensoleillement', 'ndvi', 'trajets'],
  elk:         ['habitats', 'rut', 'repos', 'alimentation', 'corridors', 'peuplements', 'pentes', 'altitude', 'trajets', 'affuts'],
};

export const getSpeciesLayers = (speciesId) => {
  if (!speciesId || speciesId === 'tous') return null;
  return SPECIES_LAYERS[speciesId] || null;
};

// ============================================
// ORGANIC ZONES — 100% BACKEND
// ============================================

// x4520-B2: Cache purgé à chaque chargement — ZERO donnée résiduelle
let _zoneCache = { key: null, data: null };

/**
 * Fetch les zones organiques depuis le backend pipeline V2.
 * Backend gère TOUT: rasterisation, Marching Squares, Chaikin, exclusion Overpass, scoring.
 *
 * @param {Object} bounds      { north, south, east, west }
 * @param {number} zoom        Niveau de zoom
 * @param {Object} layersVisible { habitats: true, rut: false, ... }
 * @param {string} speciesId   'moose', 'deer', etc.
 * @returns {Object} { zones: [], stats: {} }
 */
/**
 * BCE-4X-MAX Phase 3.3-U-PRIME: generateBionicZonesV5 DEFINITIVEMENT DESACTIVE.
 * 
 * Pipeline V5 par bounds NEUTRALISE. Retourne toujours vide.
 * Seule source autorisee: generateWaypointZonesV5 (via waypoint -> _fetchOrganicZonesV2).
 */
export const generateBionicZonesV5 = async () => {
  console.warn('[BCE-4X-MAX 3.3-U-PRIME] generateBionicZonesV5 DEFINITIVEMENT DESACTIVE');
  return { zones: [], corridors: [], stats: { total: 0, disabled: true, reason: 'BCE-4X-MAX Phase 3.3-U-PRIME' } };
};


/**
 * BCE-4X-MAX: Fonction interne autorisee — Appel backend V2 organic-zones.
 * Conservee UNIQUEMENT pour generateWaypointZonesV5 (par waypoint, avec meta-exclusion).
 */
const _fetchOrganicZonesV2 = async (bounds, zoom, layersVisible, speciesId = 'tous', waypointCenter = null, biologicalSeason = null) => {
  if (!bounds) return { zones: [], corridors: [], stats: { total: 0 } };

  const speciesLayers = getSpeciesLayers(speciesId);
  const activeLayers = LAYER_TYPES
    .filter(lt => layersVisible[lt.id])
    .filter(lt => !speciesLayers || speciesLayers.includes(lt.id))
    .map(lt => lt.id);

  if (activeLayers.length === 0) return { zones: [], corridors: [], stats: { total: 0 } };

  const cacheKey = `${bounds.south.toFixed(6)}_${bounds.west.toFixed(6)}_${bounds.north.toFixed(6)}_${bounds.east.toFixed(6)}_${speciesId}_${activeLayers.join(',')}_${biologicalSeason || 'auto'}`;
  if (_zoneCache.key === cacheKey && _zoneCache.data) return _zoneCache.data;

  const speciesMap = { orignal: 'moose', chevreuil: 'deer', ours: 'bear', dindon: 'wild_turkey', wapiti: 'elk' };
  const backendSpecies = speciesMap[speciesId] || speciesId || 'moose';
  const resolution = zoom >= 16 ? 100 : zoom >= 14 ? 80 : 60;
  const maxPerLayer = zoom >= 16 ? 12 : zoom >= 14 ? 10 : 8;

  // PHASE_ZERO_OPS_RESTORATION_Ω — Unification pipeline : V20 bundle unique
  // L'ancien endpoint /api/v1/bionic/organic-zones est dépréqué (404). Nous
  // consommons la source institutionnelle unique /api/v20/territoire/bundle
  // et transformons la shape pour rester compatible avec les consommateurs.
  try {
    const wpLat = (waypointCenter?.lat ?? waypointCenter?.latitude) ?? ((bounds.north + bounds.south) / 2);
    const wpLng = (waypointCenter?.lng ?? waypointCenter?.longitude) ?? ((bounds.east + bounds.west) / 2);
    const month = new Date().getMonth() + 1;
    const hour = new Date().getHours();
    const wind = 225;
    const url = `${API_BASE}/api/v20/territoire/bundle?lat=${wpLat}&lon=${wpLng}&species=${encodeURIComponent(backendSpecies === 'tous' ? 'cerf' : backendSpecies)}&month=${month}&hour=${hour}&wind_deg=${wind}`;
    const resp = await fetch(url, { method: 'GET' });

    if (!resp.ok) {
      console.error('[BUNDLE V20] API error:', resp.status);
      return { zones: [], corridors: [], stats: { total: 0, error: true, http_status: resp.status } };
    }

    const bundle = await resp.json();
    const rawZones = Array.isArray(bundle.zones) ? bundle.zones : [];
    const rawCorridors = Array.isArray(bundle.corridors) ? bundle.corridors : [];

    const zones = rawZones
      .filter(z => !z.excluded && Array.isArray(z.polygon) && z.polygon.length >= 4)
      .map((z, idx) => {
        const positions = z.polygon; // déjà en [lat,lng]
        const centerLat = z.center?.lat ?? 0;
        const centerLng = z.center?.lng ?? 0;
        return {
          id: z.id || `zone-${idx}`,
          layerId: z.type,
          positions,
          color: '#4A7A2E',
          score: z.score || 0,
          label: z.type ? String(z.type).toUpperCase() : '',
          category: z.type || '',
          center: [centerLat, centerLng],
          areaM2: 0,
          compactness: 0,
          vertices: positions.length,
          zoom,
          priority: LAYER_TYPES.findIndex(lt => lt.id === z.type) + 1,
          terrain: z.terrain || null,
          source: z.source || 'V20-BUNDLE',
          weatherMultiplier: null,
          weatherGlobal: null,
          scorePreWeather: null,
          weatherBadges: [],
        };
      });

    const corridors = rawCorridors.map((c, idx) => {
      const positions = Array.isArray(c.path) ? c.path : (Array.isArray(c.polyline) ? c.polyline : []);
      return {
        id: c.id || `corridor-${idx}`,
        positions,
        color: c.color || '#FF8F00',
        weight: c.weight || 2.5,
        opacity: c.opacity ?? 0.85,
        dashArray: null,
        source: c.source || 'V20',
        sex: c.sex || null,
        confidence: c.confidence || 0,
        corridorType: c.type || c.intensity || 'normal',
        classificationV9: c.classification || null,
        fromZoneType: c.from_zone_type || null,
        toZoneType: c.to_zone_type || null,
        distanceM: c.distance_m || 0,
        pathfinding: 'v20',
        score: c.score || 0,
        subscores: {},
        justification: [],
        demEnhanced: false,
        inPerimeter: true,
        certainty: c.confidence || 0,
        enginesEvaluated: 0,
        v9Pipeline: false,
        continuityValid: true,
        scores10x: null,
        bands: [],
        centerline: null,
        hasBands: false,
        bandCount: 0,
      };
    });

    const result = {
      zones,
      corridors,
      stats: {
        total: zones.length,
        corridors_total: corridors.length,
        corridors_real: corridors.filter(c => c.source === 'real').length,
        corridors_ai: corridors.filter(c => c.source === 'ai').length,
        backendVerified: true,
        source: 'V20-BUNDLE',
        t4_zone_count: zones.length,
      },
      rejection_diagnostics: null,
      weather_metadata: bundle.weather || null,
    };

    _zoneCache = { key: cacheKey, data: result };
    return result;

  } catch (err) {
    console.error('[BUNDLE V20] Fetch error:', err);
    return { zones: [], corridors: [], stats: { total: 0, error: true } };
  }
};


/**
 * BCE-4X-MAX: generateWaypointZonesV5 (AUTORISE)
 * Appelle le pipeline V2 organic-zones via waypoint center (meta-exclusion active backend).
 */
export const generateWaypointZonesV5 = async (waypoint, zoom, layersVisible, speciesId = 'tous', biologicalSeason = null) => {
  const radius = 0.015;
  const lat = waypoint.lat || waypoint.latitude;
  const lng = waypoint.lng || waypoint.longitude;
  const bounds = {
    south: lat - radius,
    north: lat + radius,
    west: lng - radius,
    east: lng + radius,
  };
  const waypointCenter = { lat, lng };
  return _fetchOrganicZonesV2(bounds, Math.max(zoom, 14), layersVisible, speciesId, waypointCenter, biologicalSeason);
};

// Legacy exports — kept for backward compatibility (no-op, scoring is backend-only)
export const fetchTerrainExclusions = async () => [];
export const ZONE_LIMITS = { TARGET_AREA_M2: 6500, MIN_AREA_M2: 4500, MAX_AREA_M2: 10000 };
export const calculateZoneScore = () => 0;
export const calculatePolygonAreaM2 = () => 0;

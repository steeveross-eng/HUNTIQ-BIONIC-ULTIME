/**
 * Map Sources Configuration
 * Configuration centralisée des 7 types de cartes premium BIONIC
 */

// Stadia Maps API Key - Required for IQHO and terrain layers
const STADIA_API_KEY = '5272b858-5b8c-4140-8ad2-066343695ca3';

// Types de cartes disponibles
export const MAP_TYPES = {
  ECOFORESTRY: 'ecoforestry',
  SATELLITE: 'satellite',
  IQHO: 'iqho',
  FOREST_ROADS: 'forest-roads',
  // ═══ CARTES HAUTE-FIDÉLITÉ — BCE-4X GOLDEN ═══
  LIDAR_HD: 'lidar-hd',
  CANOPY_DENSITY: 'canopy-density',
  ORTHOPHOTO_HR: 'orthophoto-hr',
  HYDROLOGY: 'hydrology',
  CHEMINS_DERIVES: 'chemins-derives',
  NEIGE_SOL: 'neige-sol',
  PENTE_DEM: 'pente-dem',
};

// Configuration complète des cartes
export const MAP_CONFIGS = {
  [MAP_TYPES.ECOFORESTRY]: {
    id: 'ecoforestry',
    name: 'Écoforestière',
    shortName: 'ÉCO',
    description: 'Coupes, peuplements, essences',
    iconName: 'tree-pine',
    category: 'environmental',
    isDark: false,
    isPremium: true,
    // Base OpenStreetMap avec overlay WMS NFIS-QC
    tileUrl: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
    wmsLayers: [
      {
        url: 'https://ca.nfis.org/cubewerx/cubeserv?DATASTORE=NFIS-QC',
        layers: 'NFIS-QC.produits_ecoforestiers',
        format: 'image/png',
        transparent: true
      }
    ],
    attribution: '© NFIS/MRNF Québec | © OpenStreetMap',
    maxZoom: 18,
    zoneOpacity: {
      fill: 0.25,
      stroke: 1.0
    }
  },
  
  [MAP_TYPES.SATELLITE]: {
    id: 'satellite',
    name: 'Satellite HR',
    shortName: 'SAT',
    description: 'Imagerie haute résolution',
    iconName: 'satellite',
    category: 'imagery',
    isDark: false,
    isPremium: true,
    // ESRI World Imagery (gratuit)
    tileUrl: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
    attribution: '© Esri, Maxar, Earthstar Geographics',
    maxZoom: 19,
    // Labels overlay
    labelsUrl: 'https://{s}.basemaps.cartocdn.com/light_only_labels/{z}/{x}/{y}{r}.png',
    zoneOpacity: {
      fill: 0.30,
      stroke: 1.0
    }
  },
  
  [MAP_TYPES.IQHO]: {
    id: 'iqho',
    name: 'IQHO',
    shortName: 'IQHO',
    description: 'Hydro + Relief + Ombrage',
    iconName: 'droplet',
    category: 'terrain',
    isDark: true,
    isPremium: true,
    // Stamen Terrain avec personnalisation (Stadia Maps API)
    tileUrl: `https://tiles.stadiamaps.com/tiles/stamen_terrain/{z}/{x}/{y}{r}.png${STADIA_API_KEY ? `?api_key=${STADIA_API_KEY}` : ''}`,
    attribution: '© Stadia Maps | © Stamen Design | © OpenStreetMap',
    maxZoom: 18,
    overlayStyle: {
      waterColor: '#1A237E',
      reliefOpacity: 0.7
    },
    zoneOpacity: {
      fill: 0.30,
      stroke: 1.0
    }
  },
  
  [MAP_TYPES.FOREST_ROADS]: {
    id: 'forest-roads',
    name: 'Chemins Forestiers',
    shortName: 'CHEMINS',
    description: 'Sentiers et acces terrain',
    iconName: 'route',
    category: 'access',
    isDark: false,
    isPremium: true,
    tileUrl: 'https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png',
    attribution: '© OpenTopoMap | © OpenStreetMap',
    maxZoom: 17,
    customRoadsSource: 'geo_entities',
    zoneOpacity: {
      fill: 0.20,
      stroke: 1.0
    }
  },

  // ═══ CARTES HAUTE-FIDÉLITÉ — BCE-4X GOLDEN OFFICIELLES ═══
  [MAP_TYPES.LIDAR_HD]: {
    id: 'lidar-hd',
    name: 'LIDAR HD',
    shortName: 'LIDAR',
    description: 'Modele hauteur canopee (MHC) haute resolution',
    iconName: 'mountain',
    category: 'hf',
    isDark: true,
    isPremium: true,
    isHF: true,
    tileUrl: 'https://{s}.basemaps.cartocdn.com/dark_nolabels/{z}/{x}/{y}{r}.png',
    wmsLayers: [{
      url: 'https://ca.nfis.org/cubewerx/cubeserv?DATASTORE=NFIS-QC',
      layers: 'NFIS-QC.lidar_mhc',
      format: 'image/png',
      transparent: true
    }],
    attribution: '© NFIS-QC LIDAR | © BIONIC',
    maxZoom: 18,
    zoneOpacity: { fill: 0.25, stroke: 1.0 }
  },

  [MAP_TYPES.CANOPY_DENSITY]: {
    id: 'canopy-density',
    name: 'Foret ouverte / Canopee',
    shortName: 'CANOP',
    description: 'Densite canopee et couvert vegetal',
    iconName: 'tree-pine',
    category: 'hf',
    isDark: true,
    isPremium: true,
    isHF: true,
    tileUrl: 'https://{s}.basemaps.cartocdn.com/dark_nolabels/{z}/{x}/{y}{r}.png',
    wmsLayers: [{
      url: 'https://ca.nfis.org/cubewerx/cubeserv?DATASTORE=SCANFI',
      layers: 'scanfi_canopy_height_2020',
      format: 'image/png',
      transparent: true
    }],
    attribution: '© SCANFI | © BIONIC',
    maxZoom: 18,
    zoneOpacity: { fill: 0.25, stroke: 1.0 }
  },

  [MAP_TYPES.ORTHOPHOTO_HR]: {
    id: 'orthophoto-hr',
    name: 'Orthophoto HR',
    shortName: 'ORTHO',
    description: 'Imagerie aerienne ultra-haute resolution',
    iconName: 'satellite',
    category: 'hf',
    isDark: false,
    isPremium: true,
    isHF: true,
    tileUrl: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
    attribution: '© Esri, Maxar | Orthophoto HR BIONIC',
    maxZoom: 19,
    labelsUrl: 'https://{s}.basemaps.cartocdn.com/light_only_labels/{z}/{x}/{y}{r}.png',
    zoneOpacity: { fill: 0.30, stroke: 1.0 }
  },

  [MAP_TYPES.HYDROLOGY]: {
    id: 'hydrology',
    name: 'Hydrologie',
    shortName: 'HYDRO',
    description: 'Reseau hydrographique et zones humides',
    iconName: 'droplet',
    category: 'hf',
    isDark: true,
    isPremium: true,
    isHF: true,
    tileUrl: 'https://{s}.basemaps.cartocdn.com/dark_nolabels/{z}/{x}/{y}{r}.png',
    wmsLayers: [{
      url: 'https://ca.nfis.org/cubewerx/cubeserv?DATASTORE=NFIS-QC',
      layers: 'NFIS-QC.hydro',
      format: 'image/png',
      transparent: true
    }],
    attribution: '© NFIS-QC Hydro | © BIONIC',
    maxZoom: 18,
    zoneOpacity: { fill: 0.25, stroke: 1.0 }
  },

  [MAP_TYPES.CHEMINS_DERIVES]: {
    id: 'chemins-derives',
    name: 'Chemins forestiers derives',
    shortName: 'SDA',
    description: 'Reseau sentiers et chemins SDA',
    iconName: 'route',
    category: 'hf',
    isDark: false,
    isPremium: true,
    isHF: true,
    tileUrl: 'https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png',
    attribution: '© MERN SDA | © BIONIC',
    maxZoom: 17,
    zoneOpacity: { fill: 0.20, stroke: 1.0 }
  },

  [MAP_TYPES.NEIGE_SOL]: {
    id: 'neige-sol',
    name: 'Neige / Sol',
    shortName: 'NEIGE',
    description: 'Depots surface et saisonnalite',
    iconName: 'mountain',
    category: 'hf',
    isDark: true,
    isPremium: true,
    isHF: true,
    tileUrl: 'https://{s}.basemaps.cartocdn.com/dark_nolabels/{z}/{x}/{y}{r}.png',
    wmsLayers: [{
      url: 'https://ca.nfis.org/cubewerx/cubeserv?DATASTORE=NFIS-QC',
      layers: 'NFIS-QC.depots_surface',
      format: 'image/png',
      transparent: true
    }],
    attribution: '© NFIS-QC | © BIONIC',
    maxZoom: 18,
    zoneOpacity: { fill: 0.25, stroke: 1.0 }
  },

  [MAP_TYPES.PENTE_DEM]: {
    id: 'pente-dem',
    name: 'Pente HD (DEM 1m)',
    shortName: 'PENTE',
    description: 'Modele elevation et analyse pente',
    iconName: 'mountain',
    category: 'hf',
    isDark: true,
    isPremium: true,
    isHF: true,
    tileUrl: 'https://{s}.basemaps.cartocdn.com/dark_nolabels/{z}/{x}/{y}{r}.png',
    wmsLayers: [{
      url: 'https://ca.nfis.org/cubewerx/cubeserv?DATASTORE=NFIS-QC',
      layers: 'NFIS-QC.pentes',
      format: 'image/png',
      transparent: true
    }],
    attribution: '© NFIS-QC Pentes | © BIONIC',
    maxZoom: 18,
    zoneOpacity: { fill: 0.25, stroke: 1.0 }
  },
};

// Cartes optimisees pour le mode sombre
export const DARK_OPTIMIZED_MAPS = [
  MAP_TYPES.IQHO,
  MAP_TYPES.BATHYMETRY,
  MAP_TYPES.LIDAR_HD,
  MAP_TYPES.CANOPY_DENSITY,
  MAP_TYPES.HYDROLOGY,
  MAP_TYPES.NEIGE_SOL,
  MAP_TYPES.PENTE_DEM,
];

// Ordre d'affichage dans le selecteur (standard + HF)
export const MAP_DISPLAY_ORDER = [
  MAP_TYPES.ECOFORESTRY,
  MAP_TYPES.SATELLITE,
  MAP_TYPES.IQHO,
  MAP_TYPES.FOREST_ROADS,
  // Haute-Fidelite
  MAP_TYPES.LIDAR_HD,
  MAP_TYPES.CANOPY_DENSITY,
  MAP_TYPES.ORTHOPHOTO_HR,
  MAP_TYPES.HYDROLOGY,
  MAP_TYPES.CHEMINS_DERIVES,
  MAP_TYPES.NEIGE_SOL,
  MAP_TYPES.PENTE_DEM,
];

// Catégories de cartes
export const MAP_CATEGORIES = {
  tactical: { name: 'Tactique', color: '#F5A623' },
  environmental: { name: 'Environnement', color: '#22C55E' },
  imagery: { name: 'Imagerie', color: '#3B82F6' },
  terrain: { name: 'Terrain', color: '#8B5CF6' },
  water: { name: 'Eau', color: '#06B6D4' },
  access: { name: 'Accès', color: '#FF9800' }
};

// Fonction pour obtenir la config d'une carte
export const getMapConfig = (mapType) => {
  return MAP_CONFIGS[mapType] || MAP_CONFIGS[MAP_TYPES.ECOFORESTRY];
};

// Fonction pour vérifier si une carte est sombre
export const isMapDark = (mapType) => {
  return DARK_OPTIMIZED_MAPS.includes(mapType);
};

// Fonction pour obtenir l'opacité des zones selon la carte
export const getZoneOpacity = (mapType, zoneType = 'fill') => {
  const config = getMapConfig(mapType);
  return config.zoneOpacity?.[zoneType] || 0.25;
};

export default {
  MAP_TYPES,
  MAP_CONFIGS,
  DARK_OPTIMIZED_MAPS,
  MAP_DISPLAY_ORDER,
  MAP_CATEGORIES,
  getMapConfig,
  isMapDark,
  getZoneOpacity
};

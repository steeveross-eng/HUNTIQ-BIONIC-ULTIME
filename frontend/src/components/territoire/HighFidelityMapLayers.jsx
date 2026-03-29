/**
 * HighFidelityMapLayers.jsx
 * PROTOCOLE BIONIC GOLDEN | BCE-4X | STEEVE-MAX
 * 
 * Couches WMS haute-fidélité rendues sur la carte Leaflet.
 * Sources: NFIS-QC, MERN, Données Québec, SCANFI
 */
import React from 'react';
import { WMSTileLayer } from 'react-leaflet';

const API_BASE = process.env.REACT_APP_BACKEND_URL || '';

// Configuration WMS pour chaque couche haute-fidélité
// Utilise le WMS proxy backend pour contourner CORS
const HF_WMS_CONFIG = {
  hf_lidar_hd: {
    baseUrl: `${API_BASE}/api/wms-proxy/tile`,
    wmsUrl: 'https://ca.nfis.org/cubewerx/cubeserv?DATASTORE=NFIS-QC',
    layers: 'NFIS-QC.lidar_mhc',
    label: 'LIDAR HD (MHC)',
  },
  hf_canopy_density: {
    baseUrl: `${API_BASE}/api/wms-proxy/tile`,
    wmsUrl: 'https://ca.nfis.org/cubewerx/cubeserv?DATASTORE=SCANFI',
    layers: 'scanfi_canopy_height_2020',
    label: 'Canopy Density',
  },
  hf_orthophoto_hr: {
    // Esri World Imagery REST (pas WMS, tuile directe)
    directTile: true,
    url: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
    label: 'Orthophoto HR',
  },
  hf_hydrology: {
    baseUrl: `${API_BASE}/api/wms-proxy/tile`,
    wmsUrl: 'https://ca.nfis.org/cubewerx/cubeserv?DATASTORE=NFIS-QC',
    layers: 'NFIS-QC.hydro',
    label: 'Hydrologie',
  },
  hf_forest_roads: {
    baseUrl: `${API_BASE}/api/wms-proxy/tile`,
    wmsUrl: 'https://servicescarto.mern.gouv.qc.ca/pes/services/Territoire/SDA_WMS/MapServer/WMSServer',
    layers: '0,1,2,3',
    label: 'Chemins forestiers',
  },
  hf_snow_ground: {
    baseUrl: `${API_BASE}/api/wms-proxy/tile`,
    wmsUrl: 'https://ca.nfis.org/cubewerx/cubeserv?DATASTORE=NFIS-QC',
    layers: 'NFIS-QC.depots_surface',
    label: 'Sol/Dépôts',
  },
  hf_slope_dem: {
    baseUrl: `${API_BASE}/api/wms-proxy/tile`,
    wmsUrl: 'https://ca.nfis.org/cubewerx/cubeserv?DATASTORE=NFIS-QC',
    layers: 'NFIS-QC.pentes',
    label: 'Pente HD',
  },
};

const HighFidelityMapLayers = ({ activeEcoLayers, opacities = {} }) => {
  return (
    <>
      {Object.entries(HF_WMS_CONFIG).map(([layerId, config]) => {
        if (!activeEcoLayers[layerId]) return null;

        const opacity = (opacities[layerId] ?? 70) / 100;

        if (config.directTile) {
          // Tuile raster directe (pas WMS)
          return (
            <React.Fragment key={layerId}>
              {/* Using a plain TileLayer via react-leaflet */}
              <WMSTileLayer
                key={`hf-${layerId}`}
                url={config.url}
                opacity={opacity}
                zIndex={300}
                maxZoom={19}
              />
            </React.Fragment>
          );
        }

        // WMS via proxy backend
        return (
          <WMSTileLayer
            key={`hf-${layerId}`}
            url={config.baseUrl}
            params={{
              url: config.wmsUrl,
              layers: config.layers,
              format: 'image/png',
              transparent: true,
              version: '1.3.0',
              crs: 'EPSG:3857',
            }}
            opacity={opacity}
            transparent={true}
            format="image/png"
            zIndex={300}
          />
        );
      })}
    </>
  );
};

export default HighFidelityMapLayers;

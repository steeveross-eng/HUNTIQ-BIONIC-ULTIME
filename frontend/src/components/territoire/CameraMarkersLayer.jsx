/**
 * CameraMarkersLayer — CAMERA-POPUP-Omega
 * Affichage cameras sur carte Leaflet avec popup RICHE:
 * - Info camera (nom, marque, modele, type, serial, waypoint, GPS, dates)
 * - Bibliotheque photo (thumbnails API, tri date, filtre espece)
 * - Historique IA Vision (detections, moments forts)
 * - Actions rapides (galerie, analyses IA, modifier)
 */
import React, { useState, useEffect, useCallback } from 'react';
import { Marker, Popup, Circle, useMap } from 'react-leaflet';
import L from 'leaflet';
import { useAuth } from '@/components/GlobalAuth';
import axios from 'axios';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const cameraIconSvg = `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14.5 4h-5L7 7H4a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2h-3l-2.5-3z"/><circle cx="12" cy="13" r="3"/></svg>`;

const createCameraIcon = (inZone600m) => {
  const color = inZone600m ? '#F59E0B' : '#6B7280';
  const glow = inZone600m ? 'box-shadow:0 0 12px 4px rgba(245,158,11,0.5);' : '';
  return L.divIcon({
    className: 'camera-map-marker',
    html: `<div style="background:${color};border-radius:50%;width:30px;height:30px;display:flex;align-items:center;justify-content:center;border:2px solid #fff;${glow}">${cameraIconSvg}</div>`,
    iconSize: [30, 30],
    iconAnchor: [15, 15],
    popupAnchor: [0, -18]
  });
};

const BRAND_LABELS = {
  spypoint: 'Spypoint', browning: 'Browning', bushnell: 'Bushnell',
  moultrie: 'Moultrie', tactacam: 'Tactacam Reveal', stealth_cam: 'Stealth Cam',
  wildgame: 'Wildgame Innovations', cuddeback: 'Cuddeback/CuddeLink',
  covert: 'Covert', reconyx: 'Reconyx', exodus: 'Exodus', spartan: 'Spartan',
  primos: 'Primos', gardepro: 'GardePro', campark: 'Campark', meidase: 'Meidase',
  creativexp: 'CreativeXP', wosports: 'Wosports', gsm_outdoors: 'GSM Outdoors',
  boly: 'Boly/BolyGuard', other: 'Autres'
};

/**
 * CameraPopupContent — Contenu enrichi du popup camera
 * Charge les donnees de facon paresseuse a l'ouverture
 */
const CameraPopupContent = ({ cam }) => {
  const { token } = useAuth();
  const [popupData, setPopupData] = useState(null);
  const [loadingPopup, setLoadingPopup] = useState(true);
  const [speciesFilter, setSpeciesFilter] = useState('');
  const [photoPage, setPhotoPage] = useState(0);

  const lat = cam.gps_lat || cam.location?.coordinates?.[1];
  const lon = cam.gps_lon || cam.location?.coordinates?.[0];

  const loadPopupData = useCallback(async () => {
    if (!token || !cam.id) return;
    setLoadingPopup(true);
    try {
      const url = speciesFilter
        ? `${API}/v1/camera/cameras/${cam.id}/popup-data?species_filter=${encodeURIComponent(speciesFilter)}&limit=12`
        : `${API}/v1/camera/cameras/${cam.id}/popup-data?limit=12`;
      const res = await axios.get(url, { headers: { Authorization: `Bearer ${token}` } });
      setPopupData(res.data);
    } catch (err) {
      console.error('Popup data error:', err);
      setPopupData(null);
    } finally {
      setLoadingPopup(false);
    }
  }, [token, cam.id, speciesFilter]);

  useEffect(() => {
    loadPopupData();
  }, [loadPopupData]);

  const copyGps = () => {
    if (lat && lon) {
      navigator.clipboard.writeText(`${lat.toFixed(6)}, ${lon.toFixed(6)}`);
    }
  };

  const brandLabel = BRAND_LABELS[cam.manufacturer] || cam.manufacturer || '—';
  const typeLabel = cam.camera_type === 'cellulaire' ? 'Cellulaire (LTE)' : cam.camera_type === 'reguliere' ? 'Reguliere' : '—';
  const statusBg = cam.status === 'active' ? '#166534' : cam.status === 'maintenance' ? '#92400E' : '#991B1B';
  const statusColor = '#fff';

  return (
    <div style={{ minWidth: 300, maxWidth: 360, maxHeight: 480, overflowY: 'auto', fontFamily: '-apple-system, BlinkMacSystemFont, sans-serif', color: '#1a1a2e', fontSize: 13 }} data-testid={`camera-popup-${cam.id}`}>
      {/* HEADER */}
      <div style={{ borderBottom: '1px solid #e5e7eb', paddingBottom: 8, marginBottom: 8 }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div style={{ fontWeight: 700, fontSize: 15 }}>{cam.name || 'Camera'}</div>
          <span style={{ display: 'inline-block', padding: '2px 8px', borderRadius: 4, fontSize: 10, fontWeight: 700, background: statusBg, color: statusColor }}>
            {cam.status}
          </span>
        </div>
        <div style={{ fontSize: 12, color: '#6b7280', marginTop: 2 }}>
          {brandLabel} {cam.model && cam.model !== 'Autres modeles' ? `— ${cam.model}` : ''}
        </div>
        <div style={{ display: 'flex', gap: 6, marginTop: 4, flexWrap: 'wrap' }}>
          <span style={{ padding: '1px 6px', borderRadius: 3, fontSize: 10, fontWeight: 600, background: cam.camera_type === 'cellulaire' ? '#DBEAFE' : '#F3F4F6', color: cam.camera_type === 'cellulaire' ? '#1E40AF' : '#374151' }}>
            {typeLabel}
          </span>
          {cam.serial && (
            <span style={{ padding: '1px 6px', borderRadius: 3, fontSize: 10, background: '#F3F4F6', color: '#6b7280' }}>
              SN: {cam.serial}
            </span>
          )}
        </div>
      </div>

      {/* DETAILS */}
      <div style={{ borderBottom: '1px solid #e5e7eb', paddingBottom: 8, marginBottom: 8, fontSize: 11 }}>
        {cam.waypoint_id && (
          <div style={{ color: '#3B82F6', marginBottom: 2 }}>Waypoint: {cam.waypoint_id.slice(0, 16)}</div>
        )}
        {lat && lon && (
          <div style={{ display: 'flex', alignItems: 'center', gap: 4, marginBottom: 2 }}>
            <span style={{ color: '#10B981' }}>GPS: {lat.toFixed(6)}, {lon.toFixed(6)}</span>
            <button onClick={copyGps} style={{ background: '#F59E0B', color: '#fff', border: 'none', borderRadius: 3, padding: '1px 5px', fontSize: 9, cursor: 'pointer', fontWeight: 600 }} data-testid="popup-copy-gps">
              Copier
            </button>
          </div>
        )}
        {cam.created_at && (
          <div style={{ color: '#9CA3AF' }}>
            Cree: {new Date(cam.created_at).toLocaleDateString('fr-CA')}
            {cam.updated_at && ` | MAJ: ${new Date(cam.updated_at).toLocaleDateString('fr-CA')}`}
          </div>
        )}
      </div>

      {/* LOADING STATE */}
      {loadingPopup && (
        <div style={{ textAlign: 'center', padding: '12px 0', color: '#9CA3AF' }}>
          <div style={{ fontSize: 11 }}>Chargement...</div>
        </div>
      )}

      {/* PHOTOS SECTION */}
      {!loadingPopup && popupData && (
        <>
          <div style={{ borderBottom: '1px solid #e5e7eb', paddingBottom: 8, marginBottom: 8 }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 6 }}>
              <div style={{ fontWeight: 700, fontSize: 12, color: '#1a1a2e' }}>
                Photos ({popupData.total_events || 0})
              </div>
            </div>

            {/* SPECIES FILTER */}
            {popupData.species_summary && popupData.species_summary.length > 0 && (
              <div style={{ display: 'flex', gap: 3, flexWrap: 'wrap', marginBottom: 6 }}>
                <button
                  onClick={() => setSpeciesFilter('')}
                  style={{
                    padding: '2px 6px', borderRadius: 3, fontSize: 10, cursor: 'pointer', border: '1px solid',
                    background: !speciesFilter ? '#F59E0B' : '#fff',
                    color: !speciesFilter ? '#fff' : '#6b7280',
                    borderColor: !speciesFilter ? '#F59E0B' : '#D1D5DB',
                    fontWeight: 600
                  }}
                  data-testid="popup-filter-all"
                >
                  Toutes
                </button>
                {popupData.species_summary.map(sp => (
                  <button
                    key={sp.species}
                    onClick={() => setSpeciesFilter(sp.species)}
                    style={{
                      padding: '2px 6px', borderRadius: 3, fontSize: 10, cursor: 'pointer', border: '1px solid',
                      background: speciesFilter === sp.species ? '#10B981' : '#fff',
                      color: speciesFilter === sp.species ? '#fff' : '#374151',
                      borderColor: speciesFilter === sp.species ? '#10B981' : '#D1D5DB',
                      fontWeight: 600
                    }}
                    data-testid={`popup-filter-${sp.species}`}
                  >
                    {sp.species} ({sp.count})
                  </button>
                ))}
              </div>
            )}

            {/* PHOTO THUMBNAILS */}
            {popupData.events && popupData.events.length > 0 ? (
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 4 }}>
                {popupData.events.slice(photoPage * 8, (photoPage + 1) * 8).map(evt => (
                  <div key={evt.id} style={{ position: 'relative', aspectRatio: '1', background: '#F3F4F6', borderRadius: 4, overflow: 'hidden' }}>
                    {evt.thumbnail_url ? (
                      <img
                        src={`${API}/v1/camera/photos/${evt.id}/thumbnail`}
                        alt={evt.species || 'Photo'}
                        style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                        loading="lazy"
                      />
                    ) : (
                      <div style={{ width: '100%', height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#9CA3AF', fontSize: 10 }}>
                        CAM
                      </div>
                    )}
                    {evt.species && (
                      <div style={{ position: 'absolute', bottom: 0, left: 0, right: 0, background: 'rgba(0,0,0,0.7)', color: '#fff', fontSize: 8, padding: '1px 3px', textAlign: 'center', fontWeight: 600 }}>
                        {evt.species}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <div style={{ color: '#9CA3AF', fontSize: 11, textAlign: 'center', padding: 8 }}>Aucune photo</div>
            )}

            {/* PHOTO PAGINATION */}
            {popupData.events && popupData.events.length > 8 && (
              <div style={{ display: 'flex', justifyContent: 'center', gap: 6, marginTop: 4 }}>
                <button
                  disabled={photoPage === 0}
                  onClick={() => setPhotoPage(p => Math.max(0, p - 1))}
                  style={{ fontSize: 10, color: photoPage === 0 ? '#D1D5DB' : '#F59E0B', cursor: 'pointer', background: 'none', border: 'none', fontWeight: 600 }}
                >
                  Prec.
                </button>
                <span style={{ fontSize: 10, color: '#6b7280' }}>{photoPage + 1}/{Math.ceil(popupData.events.length / 8)}</span>
                <button
                  disabled={(photoPage + 1) * 8 >= popupData.events.length}
                  onClick={() => setPhotoPage(p => p + 1)}
                  style={{ fontSize: 10, color: (photoPage + 1) * 8 >= popupData.events.length ? '#D1D5DB' : '#F59E0B', cursor: 'pointer', background: 'none', border: 'none', fontWeight: 600 }}
                >
                  Suiv.
                </button>
              </div>
            )}
          </div>

          {/* IA VISION SECTION */}
          <div style={{ borderBottom: '1px solid #e5e7eb', paddingBottom: 8, marginBottom: 8 }}>
            <div style={{ fontWeight: 700, fontSize: 12, marginBottom: 4, color: '#1a1a2e' }}>
              IA Vision ({popupData.total_analyses || 0})
            </div>
            {popupData.analyses && popupData.analyses.length > 0 ? (
              <div style={{ maxHeight: 100, overflowY: 'auto' }}>
                {popupData.analyses.slice(0, 5).map((a, i) => (
                  <div key={i} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '2px 0', borderBottom: '1px solid #F3F4F6', fontSize: 11 }}>
                    <div>
                      <span style={{ fontWeight: 600, color: a.species && a.species !== 'aucun_animal' ? '#059669' : '#9CA3AF' }}>
                        {a.species || '—'}
                      </span>
                      {a.alpha_score != null && (
                        <span style={{ marginLeft: 4, padding: '0 4px', borderRadius: 2, fontSize: 9, fontWeight: 700, background: a.alpha_score >= 85 ? '#FEF3C7' : '#F3F4F6', color: a.alpha_score >= 85 ? '#92400E' : '#6B7280' }}>
                          Alpha: {a.alpha_score}
                        </span>
                      )}
                    </div>
                    <span style={{ color: '#9CA3AF', fontSize: 10 }}>
                      {a.analyzed_at ? new Date(a.analyzed_at).toLocaleDateString('fr-CA') : ''}
                    </span>
                  </div>
                ))}
              </div>
            ) : (
              <div style={{ color: '#9CA3AF', fontSize: 11, textAlign: 'center' }}>Aucune analyse</div>
            )}

            {/* SPECIES SUMMARY */}
            {popupData.species_summary && popupData.species_summary.length > 0 && (
              <div style={{ marginTop: 6 }}>
                <div style={{ fontSize: 10, fontWeight: 600, color: '#6B7280', marginBottom: 2 }}>Especes detectees:</div>
                <div style={{ display: 'flex', gap: 3, flexWrap: 'wrap' }}>
                  {popupData.species_summary.map(sp => (
                    <span key={sp.species} style={{ padding: '1px 5px', borderRadius: 3, fontSize: 9, fontWeight: 600, background: '#ECFDF5', color: '#065F46' }}>
                      {sp.species} ({sp.count})
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        </>
      )}

      {/* QUICK ACTIONS */}
      <div style={{ display: 'flex', gap: 4, flexWrap: 'wrap' }}>
        <a href="/cameras" style={{ flex: 1, textAlign: 'center', padding: '4px 8px', borderRadius: 4, fontSize: 10, fontWeight: 700, background: '#F59E0B', color: '#fff', textDecoration: 'none', display: 'block' }} data-testid="popup-action-gallery">
          Galerie
        </a>
        <a href="/cameras" style={{ flex: 1, textAlign: 'center', padding: '4px 8px', borderRadius: 4, fontSize: 10, fontWeight: 700, background: '#8B5CF6', color: '#fff', textDecoration: 'none', display: 'block' }} data-testid="popup-action-ia-vision">
          Analyses IA
        </a>
        <a href="/cameras" style={{ flex: 1, textAlign: 'center', padding: '4px 8px', borderRadius: 4, fontSize: 10, fontWeight: 700, background: '#3B82F6', color: '#fff', textDecoration: 'none', display: 'block' }} data-testid="popup-action-modify">
          Modifier
        </a>
      </div>
    </div>
  );
};


const CameraMarkersLayer = ({ cameras = [] }) => {
  if (!cameras || cameras.length === 0) return null;

  return (
    <>
      {cameras.map(cam => {
        const lat = cam.gps_lat || cam.location?.coordinates?.[1];
        const lon = cam.gps_lon || cam.location?.coordinates?.[0];
        if (!lat || !lon) return null;

        return (
          <React.Fragment key={cam.id}>
            {cam.inZone600m && (
              <Circle
                center={[lat, lon]}
                radius={600}
                pathOptions={{
                  color: '#F59E0B',
                  weight: 1,
                  opacity: 0.4,
                  fillColor: '#F59E0B',
                  fillOpacity: 0.08,
                  dashArray: '6 4'
                }}
              />
            )}
            <Marker
              position={[lat, lon]}
              icon={createCameraIcon(cam.inZone600m)}
              data-testid={`camera-marker-${cam.id}`}
            >
              <Popup maxWidth={380} minWidth={300} autoPan={true} className="camera-rich-popup">
                <CameraPopupContent cam={cam} />
              </Popup>
            </Marker>
          </React.Fragment>
        );
      })}
    </>
  );
};

export default CameraMarkersLayer;

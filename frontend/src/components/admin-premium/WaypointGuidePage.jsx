/**
 * WaypointGuidePage.jsx — P21 · UI P17 (field guide par point)
 * COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU · ANTI-GÉNÉRIQUE STRICT
 */
import React, { useEffect, useState } from 'react';
import {
  waypointGuideCreate, waypointGuideStatus, waypointGuideDownloadUrl,
} from '@/lib/bce4xApi';
import { Download, MapPin, AlertTriangle, FileText } from 'lucide-react';

const SPECIES = ['cerf', 'orignal', 'ours', 'dindon', 'wapiti'];

const WaypointGuidePage = () => {
  const [lat, setLat] = useState(46.8);
  const [lon, setLon] = useState(-71.3);
  const [species, setSpecies] = useState('cerf');
  const [waypointId, setWaypointId] = useState('');
  const [radius, setRadius] = useState(500);
  const [genState, setGenState] = useState(null);
  const [status, setStatus] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');

  const refresh = async () => {
    const s = await waypointGuideStatus();
    if (s.ok) setStatus(s.data?.result);
  };
  useEffect(() => {
    refresh();
  }, []);

  const onGenerate = async () => {
    setBusy(true);
    setError('');
    setGenState(null);
    const r = await waypointGuideCreate({
      latitude: parseFloat(lat),
      longitude: parseFloat(lon),
      species,
      waypoint_id: waypointId || null,
      radius_m: parseInt(radius, 10),
      include_pdf: true,
      include_html: true,
      persist: true,
    });
    if (r.ok) {
      setGenState(r.data?.result);
      await refresh();
    } else {
      setError(`GENERATE_FAILED::${r.detail}`);
    }
    setBusy(false);
  };

  return (
    <div data-testid="waypoint-guide-page" style={{ maxWidth: 1100 }}>
      <header style={{ marginBottom: 20 }}>
        <h1 style={{ color: '#D4A017', fontSize: 24, margin: 0, fontWeight: 800 }}>
          FIELD GUIDES · P17
        </h1>
        <p style={{ opacity: 0.7, fontSize: 12, marginTop: 4 }}>
          Fiche terrain par point géographique · habitat + tendance 10 ans + recommandations affût.
        </p>
      </header>

      <section
        data-testid="waypoint-guide-form"
        style={{
          background: 'rgba(15,23,42,0.7)',
          border: '1px solid rgba(212,160,23,0.3)',
          padding: 16,
          borderRadius: 8,
          marginBottom: 16,
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
          gap: 12,
          alignItems: 'end',
        }}
      >
        <div>
          <label style={lbl}>Latitude</label>
          <input
            type="number"
            step="0.00001"
            value={lat}
            onChange={(e) => setLat(e.target.value)}
            data-testid="waypoint-guide-lat"
            style={inp}
          />
        </div>
        <div>
          <label style={lbl}>Longitude</label>
          <input
            type="number"
            step="0.00001"
            value={lon}
            onChange={(e) => setLon(e.target.value)}
            data-testid="waypoint-guide-lon"
            style={inp}
          />
        </div>
        <div>
          <label style={lbl}>Espèce</label>
          <select
            value={species}
            onChange={(e) => setSpecies(e.target.value)}
            data-testid="waypoint-guide-species"
            style={inp}
          >
            {SPECIES.map((s) => (
              <option key={s} value={s}>
                {s}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label style={lbl}>Rayon (m)</label>
          <input
            type="number"
            min="10"
            max="50000"
            value={radius}
            onChange={(e) => setRadius(e.target.value)}
            data-testid="waypoint-guide-radius"
            style={inp}
          />
        </div>
        <div>
          <label style={lbl}>Point ID (optionnel)</label>
          <input
            value={waypointId}
            onChange={(e) => setWaypointId(e.target.value)}
            data-testid="waypoint-guide-id"
            placeholder="auto si vide"
            style={inp}
          />
        </div>
        <div>
          <button
            onClick={onGenerate}
            disabled={busy}
            data-testid="waypoint-guide-generate"
            style={{
              padding: '9px 16px',
              background: '#D4A017',
              color: '#0F1419',
              border: 'none',
              borderRadius: 4,
              fontWeight: 800,
              cursor: 'pointer',
              width: '100%',
            }}
          >
            {busy ? 'Génération…' : 'Générer Fiche'}
          </button>
        </div>
      </section>

      {error && (
        <div
          data-testid="waypoint-guide-error"
          style={{
            background: 'rgba(220,38,38,0.15)',
            border: '1px solid rgba(220,38,38,0.4)',
            padding: 10,
            borderRadius: 6,
            marginBottom: 16,
            color: '#FCA5A5',
            fontSize: 12,
            display: 'flex',
            alignItems: 'center',
            gap: 6,
          }}
        >
          <AlertTriangle size={14} /> {error}
        </div>
      )}

      {genState && (
        <section
          data-testid="waypoint-guide-result"
          style={{
            background: 'rgba(15,23,42,0.7)',
            border: '1px solid rgba(124,181,24,0.4)',
            padding: 16,
            borderRadius: 8,
            marginBottom: 16,
          }}
        >
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: 8,
              marginBottom: 8,
            }}
          >
            <MapPin size={16} color="#7CB518" />
            <span
              style={{ fontWeight: 800, color: '#7CB518', letterSpacing: 1 }}
            >
              FICHE GÉNÉRÉE
            </span>
            <code style={{ fontSize: 10, opacity: 0.8 }}>
              sha={genState.guide_sha256?.slice(0, 24)}…
            </code>
          </div>
          <table
            style={{
              fontSize: 11,
              borderCollapse: 'collapse',
              width: '100%',
              marginTop: 8,
            }}
          >
            <tbody>
              <tr><td style={td}>Point ID</td><td style={td}>{genState.point_id}</td></tr>
              <tr><td style={td}>Coordonnées</td><td style={td}>{genState.latitude}, {genState.longitude}</td></tr>
              <tr><td style={td}>Espèce</td><td style={td}>{genState.species}</td></tr>
              <tr><td style={td}>Habitat status</td><td style={td}><code>{genState.habitat_quality?.status}</code></td></tr>
              <tr><td style={td}>Cellules qualifiées</td><td style={td}>{genState.habitat_quality?.n_cells_matching ?? '—'}</td></tr>
              <tr><td style={td}>Tendance décennale</td><td style={td}><code>{genState.decadal_trend?.status}</code> · {genState.decadal_trend?.mann_kendall_verdict || '—'}</td></tr>
            </tbody>
          </table>
          <div style={{ marginTop: 12 }}>
            <h3 style={{ fontSize: 12, color: '#D4A017', margin: '0 0 6px', fontWeight: 800 }}>
              RECOMMANDATIONS AFFÛT
            </h3>
            <ul style={{ paddingLeft: 16, margin: 0, fontSize: 11 }}>
              {genState.recommendations?.map((r, i) => (
                <li key={i} data-testid={`waypoint-guide-rec-${i}`}>
                  <strong>[{r.priority}] {r.category}</strong> — {r.action}
                </li>
              ))}
            </ul>
          </div>
          <div style={{ display: 'flex', gap: 8, marginTop: 12, flexWrap: 'wrap' }}>
            <a
              href={waypointGuideDownloadUrl(genState.guide_sha256, 'pdf')}
              target="_blank"
              rel="noopener noreferrer"
              data-testid="waypoint-guide-dl-pdf"
              style={dlBtn('#D4A017')}
            >
              <Download size={12} /> PDF
            </a>
            <a
              href={waypointGuideDownloadUrl(genState.guide_sha256, 'html')}
              target="_blank"
              rel="noopener noreferrer"
              data-testid="waypoint-guide-dl-html"
              style={dlBtn('#7CB518')}
            >
              <Download size={12} /> HTML
            </a>
            <a
              href={waypointGuideDownloadUrl(genState.guide_sha256, 'json')}
              target="_blank"
              rel="noopener noreferrer"
              data-testid="waypoint-guide-dl-json"
              style={dlBtn('#06B6D4')}
            >
              <Download size={12} /> JSON
            </a>
          </div>
        </section>
      )}

      {status && (
        <div
          data-testid="waypoint-guide-status-bar"
          style={{
            fontSize: 11,
            opacity: 0.8,
            fontFamily: 'JetBrains Mono, monospace',
            padding: '8px 12px',
            background: 'rgba(15,23,42,0.5)',
            borderRadius: 6,
            border: '1px solid rgba(212,160,23,0.2)',
          }}
        >
          P17 · status = <code style={{ color: '#7CB518' }}>{status.current_status}</code> · n_guides = {status.n_guides_generated} · last_species = {status.last_species || '—'}
        </div>
      )}
    </div>
  );
};

const lbl = { display: 'block', fontSize: 10, marginBottom: 4, opacity: 0.8 };
const inp = {
  width: '100%',
  padding: '7px 10px',
  background: '#0F1419',
  border: '1px solid rgba(212,160,23,0.3)',
  borderRadius: 4,
  color: '#E8E4D9',
  fontFamily: 'JetBrains Mono, monospace',
  fontSize: 12,
};
const td = {
  padding: '6px 10px',
  borderBottom: '1px dashed rgba(255,255,255,0.08)',
};
const dlBtn = (color) => ({
  padding: '6px 12px',
  background: 'transparent',
  border: `1px solid ${color}`,
  borderRadius: 4,
  color,
  fontSize: 11,
  fontWeight: 700,
  textDecoration: 'none',
  display: 'flex',
  alignItems: 'center',
  gap: 4,
});

export default WaypointGuidePage;

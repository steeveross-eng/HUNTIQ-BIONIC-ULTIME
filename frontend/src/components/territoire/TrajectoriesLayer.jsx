/**
 * TrajectoriesLayer — Lignes animées entre cameras montrant les déplacements
 * VIS-C: Couche trajectoires IA sur carte Leaflet
 */
import React from 'react';
import { Polyline, Popup } from 'react-leaflet';

const SPECIES_COLORS = {
  orignal: '#F59E0B',
  cerf: '#10B981',
  ours_noir: '#EF4444',
  caribou: '#8B5CF6',
  dindon: '#6366F1',
  chevreuil: '#14B8A6',
  loup: '#6B7280',
  default: '#F59E0B'
};

const TrajectoriesLayer = ({ trajectories = [] }) => {
  if (!trajectories || trajectories.length === 0) return null;

  return (
    <>
      {trajectories.map(traj => {
        const segments = traj.segments || [];
        const color = SPECIES_COLORS[traj.species] || SPECIES_COLORS.default;

        return segments.map((seg, idx) => {
          if (!seg.from_lat || !seg.to_lat) return null;
          const positions = [[seg.from_lat, seg.from_lon], [seg.to_lat, seg.to_lon]];

          return (
            <Polyline
              key={`${traj.id}-${idx}`}
              positions={positions}
              pathOptions={{
                color,
                weight: 3,
                opacity: 0.7 * (traj.confidence || 0.5),
                dashArray: '10 6',
                lineCap: 'round'
              }}
            >
              <Popup>
                <div style={{ minWidth: 160, color: '#1a1a2e' }}>
                  <div style={{ fontWeight: 700, fontSize: 13, marginBottom: 4, textTransform: 'capitalize' }}>
                    {traj.species?.replace('_', ' ')} — Trajectoire
                  </div>
                  <div style={{ fontSize: 12, marginBottom: 2 }}>
                    Direction: <strong>{seg.direction_cardinal}</strong> ({seg.direction_deg}&deg;)
                  </div>
                  <div style={{ fontSize: 12, marginBottom: 2 }}>
                    Distance: <strong>{seg.distance_m}m</strong>
                  </div>
                  <div style={{ fontSize: 11, color: '#888' }}>
                    Confiance: {Math.round((traj.confidence || 0) * 100)}%
                  </div>
                </div>
              </Popup>
            </Polyline>
          );
        });
      })}
    </>
  );
};

export default TrajectoriesLayer;

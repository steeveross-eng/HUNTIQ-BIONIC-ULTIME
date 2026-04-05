/**
 * W10 — POI Detail Card (Fiche POI enrichie)
 * Directive x7000-M3-DASHBOARD | BCE-4X GOLDEN V6+
 */
import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../../../components/ui/card';
import { Badge } from '../../../components/ui/badge';
import { MapPin, Target, Leaf, Shield, Link2 } from 'lucide-react';

const TYPE_COLORS = {
  stand: '#f5a623', camera: '#3b82f6', point_eau: '#06b6d4',
  observation: '#22c55e', ravage: '#ef4444', corridor: '#8b5cf6',
  nourriture: '#84cc16', saline: '#f97316', cache: '#6b7280',
};

export const POIDetailCard = ({ data }) => {
  if (!data?.poi_id) return null;

  const typeColor = TYPE_COLORS[data.type] || '#6b7280';

  return (
    <Card data-testid="poi-detail-card" className="bg-zinc-900 border-zinc-800">
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-medium text-zinc-300 flex items-center gap-2">
          <MapPin className="w-4 h-4" style={{ color: typeColor }} />
          {data.name}
          <Badge className="text-[9px] ml-auto" style={{ backgroundColor: typeColor, color: '#fff' }}>
            {data.type}
          </Badge>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {/* Score POI */}
        <div className="space-y-1">
          <div className="flex items-center gap-2 text-xs text-zinc-400">
            <Target className="w-3 h-3" /> Score POI
          </div>
          <div className="grid grid-cols-2 gap-1 text-[10px]">
            {Object.entries(data.score || {}).map(([k, v]) => (
              <div key={k} className="flex justify-between bg-zinc-800/50 px-2 py-0.5 rounded">
                <span className="text-zinc-500">{k}</span>
                <span className="text-zinc-300">{typeof v === 'number' ? (v * 100).toFixed(0) + '%' : v}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Nutrition */}
        {data.nutrition && Object.keys(data.nutrition).length > 0 && (
          <div className="space-y-1">
            <div className="flex items-center gap-2 text-xs text-zinc-400">
              <Leaf className="w-3 h-3 text-emerald-500" /> Nutrition V6
            </div>
            <div className="grid grid-cols-2 gap-1 text-[10px]">
              <div className="flex justify-between bg-zinc-800/50 px-2 py-0.5 rounded">
                <span className="text-zinc-500">Fourrage</span>
                <span className="text-zinc-300">{((data.nutrition.forage_quality || 0) * 100).toFixed(0)}%</span>
              </div>
              <div className="flex justify-between bg-zinc-800/50 px-2 py-0.5 rounded">
                <span className="text-zinc-500">Minéraux</span>
                <span className="text-zinc-300">{((data.nutrition.mineral_richness || 0) * 100).toFixed(0)}%</span>
              </div>
              <div className="flex justify-between bg-zinc-800/50 px-2 py-0.5 rounded">
                <span className="text-zinc-500">NDVI</span>
                <span className="text-zinc-300">{((data.nutrition.ndvi_index || 0) * 100).toFixed(0)}%</span>
              </div>
            </div>
          </div>
        )}

        {/* Legal */}
        {data.legal?.province && (
          <div className="flex items-center gap-2 text-[10px] text-zinc-500">
            <Shield className="w-3 h-3" />
            <span>{data.legal.province}</span>
            {data.legal.zone_chasse && <span>| Zone: {data.legal.zone_chasse}</span>}
          </div>
        )}

        {/* Connections */}
        <div className="flex items-center gap-2 text-[10px] text-zinc-500">
          <Link2 className="w-3 h-3" />
          <span>{data.connections} connexions | {data.edge_count} arêtes</span>
        </div>

        {/* Coordinates */}
        <div className="text-[9px] text-zinc-600">
          {data.location?.lat?.toFixed(4)}, {data.location?.lng?.toFixed(4)}
        </div>
      </CardContent>
    </Card>
  );
};

export default POIDetailCard;

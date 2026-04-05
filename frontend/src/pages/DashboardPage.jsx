/**
 * DashboardPage - Core Dashboard wrapper page
 * BCE-4X Phase 3.1: Synchronisation waypoint UNIQUE
 * P1 BDRE-FIRST: Indicateur BDRE global dans le header
 * 
 * Le Dashboard utilise les coordonnées du waypoint actif de l'usager,
 * PAS des coordonnées hardcodées. Source: useUserData (identique à MonTerritoire).
 */
import React, { useMemo, useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { ArrowLeft, Shield, CheckCircle2, XCircle, AlertTriangle } from 'lucide-react';
import { CoreDashboard } from '../modules/dashboard';
import { GlobalContainer } from '../core/layouts';
import { useAuth } from '../components/GlobalAuth';
import { useUserData } from '../hooks/useUserData';

const API = process.env.REACT_APP_BACKEND_URL;
const LAST_WAYPOINT_KEY = 'bionic_last_active_waypoint_id';
const DEFAULT_COORDS = { lat: 46.8139, lng: -71.2082 };

const DashboardPage = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [bdre, setBdre] = useState(null);

  const userId = useMemo(() => {
    if (user?.id) return user.id;
    if (user?.email) return user.email;
    return 'anonymous';
  }, [user]);

  const { waypoints, activeWaypoints } = useUserData(userId, { autoSync: false });

  // BDRE-FIRST: Fetch BDRE status for header indicator
  useEffect(() => {
    const fetchBdre = async () => {
      try {
        const [dashRes, srcRes] = await Promise.all([
          fetch(`${API}/api/v1/bdre/dashboard`).then(r => r.json()),
          fetch(`${API}/api/v1/bdre/sources`).then(r => r.json()),
        ]);
        const sources = srcRes.sources || [];
        setBdre({
          version: dashRes.bdre_version,
          healthy: sources.filter(s => s.status === 'healthy').length,
          offline: sources.filter(s => s.status !== 'healthy').length,
          fallbacks: dashRes.audit_stats?.total_fallbacks ?? 0,
          alerts: dashRes.audit_stats?.total_alerts ?? 0,
          sources,
        });
      } catch { /* silent */ }
    };
    fetchBdre();
    const interval = setInterval(fetchBdre, 30000);
    return () => clearInterval(interval);
  }, []);

  // BCE-4X Phase 3.1: Lire le MEME waypoint que MonTerritoire
  const waypointCoords = useMemo(() => {
    const lastId = localStorage.getItem(LAST_WAYPOINT_KEY);
    if (lastId && activeWaypoints.length > 0) {
      const wp = activeWaypoints.find(w => w.id === lastId);
      if (wp) {
        const lat = wp.lat ?? wp.latitude;
        const lng = wp.lng ?? wp.longitude;
        if (lat && lng) return { lat, lng };
      }
    }
    if (activeWaypoints.length > 0) {
      const wp = activeWaypoints[0];
      const lat = wp.lat ?? wp.latitude;
      const lng = wp.lng ?? wp.longitude;
      if (lat && lng) return { lat, lng };
    }
    if (waypoints.length > 0) {
      const wp = waypoints[0];
      const lat = wp.lat ?? wp.latitude;
      const lng = wp.lng ?? wp.longitude;
      if (lat && lng) return { lat, lng };
    }
    return DEFAULT_COORDS;
  }, [waypoints, activeWaypoints]);

  return (
    <main className="min-h-screen bg-background">
      <GlobalContainer className="pb-16">
        <div className="flex items-center justify-between mb-4">
          <Button 
            variant="ghost" 
            onClick={() => navigate('/')}
            className="text-gray-300 hover:text-white hover:bg-gray-800/50"
            data-testid="back-button-dashboard"
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Retour
          </Button>

          {/* BDRE-FIRST: Global BDRE Indicator */}
          {bdre && (
            <div className="flex items-center gap-3 bg-[#111118]/80 px-3 py-1.5 rounded-lg border border-gray-800" data-testid="dashboard-bdre-indicator">
              <Shield className="h-4 w-4 text-[#F5A623]" />
              <Badge variant="outline" className="text-[9px] border-[#F5A623]/30 text-[#F5A623]">{bdre.version}</Badge>
              <div className="flex items-center gap-1">
                <CheckCircle2 className="h-3 w-3 text-green-400" />
                <span className="text-[10px] text-gray-400">{bdre.healthy}</span>
              </div>
              <div className="flex items-center gap-1">
                <XCircle className="h-3 w-3 text-gray-500" />
                <span className="text-[10px] text-gray-500">{bdre.offline}</span>
              </div>
              {bdre.fallbacks > 0 && (
                <div className="flex items-center gap-1">
                  <AlertTriangle className="h-3 w-3 text-yellow-400" />
                  <span className="text-[10px] text-yellow-400">{bdre.fallbacks}</span>
                </div>
              )}
              <div className="flex gap-0.5">
                {bdre.sources.slice(0, 8).map((s, i) => (
                  <div key={i} className={`w-1.5 h-1.5 rounded-full ${s.status === 'healthy' ? (s.score >= 0.8 ? 'bg-green-400' : 'bg-yellow-400') : 'bg-gray-600'}`} title={s.source_id} />
                ))}
              </div>
            </div>
          )}
        </div>

        <CoreDashboard 
          coordinates={waypointCoords}
          species="deer"
          season="rut"
        />
      </GlobalContainer>
    </main>
  );
};

export default DashboardPage;

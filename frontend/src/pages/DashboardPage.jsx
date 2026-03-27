/**
 * DashboardPage - Core Dashboard wrapper page
 * BCE-4X Phase 3.1: Synchronisation waypoint UNIQUE
 * 
 * Le Dashboard utilise les coordonnées du waypoint actif de l'usager,
 * PAS des coordonnées hardcodées. Source: useUserData (identique à MonTerritoire).
 */
import React, { useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { ArrowLeft } from 'lucide-react';
import { CoreDashboard } from '../modules/dashboard';
import { GlobalContainer } from '../core/layouts';
import { useAuth } from '../components/GlobalAuth';
import { useUserData } from '../hooks/useUserData';

const LAST_WAYPOINT_KEY = 'bionic_last_active_waypoint_id';
const DEFAULT_COORDS = { lat: 46.8139, lng: -71.2082 };

const DashboardPage = () => {
  const navigate = useNavigate();
  const { user } = useAuth();

  const userId = useMemo(() => {
    if (user?.id) return user.id;
    if (user?.email) return user.email;
    return 'anonymous';
  }, [user]);

  const { waypoints, activeWaypoints } = useUserData(userId, { autoSync: false });

  // BCE-4X Phase 3.1: Lire le MEME waypoint que MonTerritoire
  const waypointCoords = useMemo(() => {
    // Priorité 1: Dernier waypoint actif (localStorage, même clé que MonTerritoire)
    const lastId = localStorage.getItem(LAST_WAYPOINT_KEY);
    if (lastId && activeWaypoints.length > 0) {
      const wp = activeWaypoints.find(w => w.id === lastId);
      if (wp) {
        const lat = wp.lat ?? wp.latitude;
        const lng = wp.lng ?? wp.longitude;
        if (lat && lng) return { lat, lng };
      }
    }
    // Priorité 2: Premier waypoint actif
    if (activeWaypoints.length > 0) {
      const wp = activeWaypoints[0];
      const lat = wp.lat ?? wp.latitude;
      const lng = wp.lng ?? wp.longitude;
      if (lat && lng) return { lat, lng };
    }
    // Priorité 3: N'importe quel waypoint
    if (waypoints.length > 0) {
      const wp = waypoints[0];
      const lat = wp.lat ?? wp.latitude;
      const lng = wp.lng ?? wp.longitude;
      if (lat && lng) return { lat, lng };
    }
    // Fallback: coordonnées par défaut (Québec)
    return DEFAULT_COORDS;
  }, [waypoints, activeWaypoints]);

  return (
    <main className="min-h-screen bg-background">
      <GlobalContainer className="pb-16">
        <Button 
          variant="ghost" 
          onClick={() => navigate('/')}
          className="mb-4 text-gray-300 hover:text-white hover:bg-gray-800/50"
          data-testid="back-button-dashboard"
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          Retour à l'accueil
        </Button>

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

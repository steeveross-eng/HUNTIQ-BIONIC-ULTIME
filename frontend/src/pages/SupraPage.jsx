/**
 * SupraPage.jsx — Route dediee SUPRA v2
 * =======================================
 * Accessible via /supra/:id
 * Affiche le panneau SUPRA v2 en mode pleine page (100vh, ZERO scroll interne).
 *
 * BCE-4X / STEEVE-MAX V6 — PHASE 2.9 FIX SAL-10
 */
import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Loader2 } from 'lucide-react';
import NutritionPointDetailPanel from '@/components/territoire/NutritionPointDetailPanel';

export default function SupraPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [nutritionPoint, setNutritionPoint] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const parts = id?.split(',');
    if (parts?.length === 2) {
      setNutritionPoint({
        id: `SUPRA-${id}`,
        lat: parseFloat(parts[0]),
        lng: parseFloat(parts[1]),
        species: 'chevreuil',
        season: 'printemps',
        soil_type: 'mixte',
        distance_centre_m: 0,
      });
    } else {
      setNutritionPoint({
        id: id || 'SUPRA',
        lat: 47.3,
        lng: -71.2,
        species: 'chevreuil',
        season: 'printemps',
        soil_type: 'mixte',
        distance_centre_m: 0,
      });
    }
    setLoading(false);
  }, [id]);

  if (loading) {
    return (
      <div className="h-screen w-screen bg-[#0a0a14] flex items-center justify-center" data-testid="supra-page-loading">
        <Loader2 className="h-8 w-8 animate-spin text-[#FF9800]" />
      </div>
    );
  }

  return (
    <div className="h-screen w-screen overflow-hidden bg-[#0a0a14]" data-testid="supra-page">
      {nutritionPoint && (
        <NutritionPointDetailPanel
          nutritionPoint={nutritionPoint}
          onClose={() => navigate('/mon-territoire-bionic')}
        />
      )}
    </div>
  );
}

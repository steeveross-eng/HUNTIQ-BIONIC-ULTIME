/**
 * SupraPage.jsx — Route dediee SUPRA v2
 * =======================================
 * Accessible via /supra/:id
 * Affiche le panneau SUPRA v2 en mode pleine page pour un point donne.
 *
 * BCE-4X / STEEVE-MAX V6 — PURGE ARCHITECTURALE
 */
import { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import {
  ArrowLeft, Droplets, FlaskConical, Loader2, MapPin
} from 'lucide-react';
import NutritionPointDetailPanel from '@/components/territoire/NutritionPointDetailPanel';

const API = process.env.REACT_APP_BACKEND_URL;

export default function SupraPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [nutritionPoint, setNutritionPoint] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Construire un objet nutritionPoint a partir de l'ID
    // Format attendu: SAL-XX ou coordonnees lat,lng
    const parts = id?.split(',');
    if (parts?.length === 2) {
      // Coordonnees directes: /supra/47.3,-71.2
      setNutritionPoint({
        id: `SUPRA-${id}`,
        lat: parseFloat(parts[0]),
        lng: parseFloat(parts[1]),
        species: 'chevreuil',
        season: 'printemps',
        soil_type: 'mixte',
        distance_centre_m: 0,
      });
      setLoading(false);
    } else {
      // ID de point: /supra/SAL-01
      setNutritionPoint({
        id: id || 'SUPRA',
        lat: 47.3,
        lng: -71.2,
        species: 'chevreuil',
        season: 'printemps',
        soil_type: 'mixte',
        distance_centre_m: 0,
      });
      setLoading(false);
    }
  }, [id]);

  if (loading) {
    return (
      <div className="min-h-screen bg-[#0a0a14] flex items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-[#FF9800]" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#0a0a14] pt-16" data-testid="supra-page">
      <div className="max-w-3xl mx-auto px-4 py-4">
        {/* Navigation retour */}
        <button
          onClick={() => navigate('/mon-territoire-bionic')}
          className="flex items-center gap-2 text-sm text-gray-400 hover:text-white transition-colors mb-4"
          data-testid="supra-back-btn"
        >
          <ArrowLeft className="h-4 w-4" /> Retour a la carte
        </button>

        {/* Panel SUPRA v2 en mode standalone */}
        {nutritionPoint && (
          <NutritionPointDetailPanel
            nutritionPoint={nutritionPoint}
            onClose={() => navigate('/mon-territoire-bionic')}
          />
        )}
      </div>
    </div>
  );
}

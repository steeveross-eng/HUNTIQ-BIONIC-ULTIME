/**
 * ProductPage.jsx — Fiche produit BIONIC SUPRA
 * BCE-4X / STEEVE-MAX V6
 * 
 * Description, Role physiologique, Support optimal,
 * Dosage, Prix, Disponibilite locale
 */
import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  ArrowLeft, ShoppingCart, Leaf, FlaskConical, TreeDeciduous,
  Scale, DollarSign, MapPin, Gem, Activity, Droplets, Zap
} from 'lucide-react';

const BIONIC = {
  green: '#00C853', yellow: '#F9D423', orange: '#FF9800', red: '#D32F2F',
  blue: '#2196F3', purple: '#9C27B0', card: '#111122', border: 'rgba(255,255,255,0.06)',
};

// Base de donnees produits BIONIC (extensible via API)
const PRODUCT_DB = {
  'Sodium': { mineral: 'Sodium (Na)', role: "Maintien de l'equilibre osmotique et de l'hydratation cellulaire. Essentiel pour la regulation de la pression arterielle et la transmission nerveuse.", support: 'Bois mou (epinette, sapin)', dosage: '2-4 kg / site / application', prix: '8-15$ CAD / kg', disponibilite: 'Disponible localement (cooperatives agricoles, magasins de chasse)', icon: Droplets, color: BIONIC.blue },
  'Calcium': { mineral: 'Calcium (Ca)', role: "Croissance et regeneration du panache. Mineralisation osseuse. Essentiel durant la phase de velours (mai-aout).", support: 'Bois mou ou bloc mineral', dosage: '1-3 kg / site / application', prix: '12-20$ CAD / kg', disponibilite: 'Disponible en ligne et en magasin specialise', icon: Gem, color: BIONIC.green },
  'Phosphore': { mineral: 'Phosphore (P)', role: "Metabolisme energetique (ATP). Synthese ADN. Croissance du panache en synergie avec le calcium (ratio Ca:P = 2:1).", support: 'Bois mou', dosage: '1-2 kg / site / application', prix: '10-18$ CAD / kg', disponibilite: 'Cooperative agricole, fournisseur mineral', icon: Zap, color: BIONIC.orange },
  'Magnesium': { mineral: 'Magnesium (Mg)', role: "Contraction musculaire, fonction nerveuse, fixation du calcium. Cofacteur de 300+ reactions enzymatiques.", support: 'Bois mou ou sol amendé', dosage: '0.5-1.5 kg / site / application', prix: '8-14$ CAD / kg', disponibilite: 'Disponible localement', icon: Activity, color: BIONIC.purple },
  'Potassium': { mineral: 'Potassium (K)', role: "Fonction musculaire et cardiaque. Equilibre electrolytique. Essentiel durant le rut (effort physique intense).", support: 'Tous supports', dosage: '1-2 kg / site / application', prix: '6-12$ CAD / kg', disponibilite: 'Largement disponible (engrais agricoles)', icon: Leaf, color: BIONIC.green },
};

const Card = ({ children, className = '' }) => (
  <div className={`rounded-2xl border p-5 ${className}`} style={{ backgroundColor: BIONIC.card, borderColor: BIONIC.border, boxShadow: '0 2px 12px rgba(0,0,0,0.2)' }}>{children}</div>
);

export default function ProductPage() {
  const { productId } = useParams();
  const navigate = useNavigate();
  const decoded = decodeURIComponent(productId || '');
  
  // Chercher le produit dans la base locale
  const product = PRODUCT_DB[decoded] || Object.values(PRODUCT_DB).find(p => p.mineral.toLowerCase().includes(decoded.toLowerCase()));
  
  // Fallback produit generique
  const p = product || {
    mineral: decoded || 'Produit',
    role: "Information detaillee en cours de chargement. Ce produit fait partie du catalogue BIONIC SUPRA.",
    support: 'Bois mou recommande',
    dosage: 'Selon prescription SUPRA',
    prix: 'Voir fournisseur local',
    disponibilite: 'Verifier disponibilite locale',
    icon: FlaskConical,
    color: BIONIC.orange,
  };

  const Icon = p.icon || FlaskConical;

  return (
    <div className="min-h-screen bg-[#0a0a14] text-white" data-testid="product-page">
      {/* Header */}
      <div className="border-b border-gray-800/50 bg-black/60 backdrop-blur-sm px-6 py-4">
        <div className="max-w-[800px] mx-auto flex items-center gap-4">
          <button onClick={() => navigate(-1)} className="text-gray-400 hover:text-white transition-colors" data-testid="product-back-btn">
            <ArrowLeft className="h-5 w-5" />
          </button>
          <div className="w-10 h-10 rounded-xl flex items-center justify-center" style={{ backgroundColor: `${p.color}15`, border: `2px solid ${p.color}60` }}>
            <Icon className="h-5 w-5" style={{ color: p.color }} />
          </div>
          <div>
            <h1 className="text-lg font-black uppercase tracking-tight" data-testid="product-title">Fiche Produit</h1>
            <p className="text-xs text-gray-500">{p.mineral} | BIONIC SUPRA</p>
          </div>
        </div>
      </div>

      <div className="max-w-[800px] mx-auto px-6 py-6 space-y-4">
        {/* Nom + Badge */}
        <Card>
          <div className="flex items-center gap-4 mb-4">
            <div className="w-16 h-16 rounded-2xl flex items-center justify-center" style={{ background: `linear-gradient(135deg, ${p.color}22, ${p.color}08)`, border: `2.5px solid ${p.color}` }}>
              <Icon className="h-8 w-8" style={{ color: p.color }} />
            </div>
            <div>
              <h2 className="text-xl font-black text-white">{p.mineral}</h2>
              <span className="text-xs font-bold px-2.5 py-0.5 rounded-lg inline-block mt-1" style={{ backgroundColor: `${p.color}18`, color: p.color }}>SUPRA CERTIFIE</span>
            </div>
          </div>
        </Card>

        {/* Role physiologique */}
        <Card>
          <div className="flex items-center gap-2 mb-3">
            <Activity className="h-4 w-4" style={{ color: BIONIC.blue }} />
            <span className="text-sm font-bold text-white uppercase tracking-wider">Role physiologique</span>
          </div>
          <p className="text-sm text-gray-300 leading-relaxed" data-testid="product-role">{p.role}</p>
        </Card>

        {/* Details techniques */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <Card>
            <div className="flex items-center gap-2 mb-2">
              <TreeDeciduous className="h-4 w-4" style={{ color: BIONIC.green }} />
              <span className="text-xs font-bold text-gray-400 uppercase">Support optimal</span>
            </div>
            <p className="text-sm font-bold text-white" data-testid="product-support">{p.support}</p>
          </Card>
          <Card>
            <div className="flex items-center gap-2 mb-2">
              <Scale className="h-4 w-4" style={{ color: BIONIC.orange }} />
              <span className="text-xs font-bold text-gray-400 uppercase">Dosage</span>
            </div>
            <p className="text-sm font-bold text-white" data-testid="product-dosage">{p.dosage}</p>
          </Card>
          <Card>
            <div className="flex items-center gap-2 mb-2">
              <DollarSign className="h-4 w-4" style={{ color: BIONIC.yellow }} />
              <span className="text-xs font-bold text-gray-400 uppercase">Prix</span>
            </div>
            <p className="text-sm font-bold" style={{ color: BIONIC.orange }} data-testid="product-price">{p.prix}</p>
          </Card>
          <Card>
            <div className="flex items-center gap-2 mb-2">
              <MapPin className="h-4 w-4" style={{ color: BIONIC.purple }} />
              <span className="text-xs font-bold text-gray-400 uppercase">Disponibilite locale</span>
            </div>
            <p className="text-sm text-gray-300" data-testid="product-availability">{p.disponibilite}</p>
          </Card>
        </div>

        {/* Action */}
        <Card>
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-400">Commander ce produit</span>
            <button
              className="flex items-center gap-2 h-10 px-6 rounded-lg font-bold text-sm uppercase tracking-wider transition-all duration-150 hover:brightness-125 active:scale-[0.97]"
              style={{ backgroundColor: `${BIONIC.orange}18`, color: BIONIC.orange, border: `2px solid ${BIONIC.orange}50` }}
              data-testid="product-order-btn"
            >
              <ShoppingCart className="h-4 w-4" /> Commander
            </button>
          </div>
        </Card>

        <div className="text-center text-[10px] text-gray-600 pt-2 pb-6">
          Fiche Produit BIONIC SUPRA | BCE-4X / STEEVE-MAX V6
        </div>
      </div>
    </div>
  );
}

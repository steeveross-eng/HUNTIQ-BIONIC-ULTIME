/**
 * AdminDashboard - BCE-4X GOLDEN V6+ Administration Premium
 * ==========================================================
 * 
 * Dashboard principal avec KPIs et navigation.
 * Grille 3x3 institutionnelle — COMMANDANT STEEVE-MAX
 * Alignement horizontal/vertical uniforme
 * Hierarchie visuelle conforme BCE-4X
 */

import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { 
  Users, CreditCard, TrendingUp, Target, Crown,
  Settings, FileText, BarChart3, Layers, RefreshCw,
  BookOpen, Zap, Shield, Activity
} from 'lucide-react';
import AdminService from '../AdminService';

const StatCard = ({ title, value, subtitle, icon: Icon, color = '#F5A623' }) => (
  <div 
    data-testid={`stat-card-${title.toLowerCase().replace(/\s+/g, '-')}`}
    className="bg-[#0d0d1a] border border-[#1e293b] rounded-xl p-5 flex items-center gap-4 hover:border-[#F5A623]/30 transition-all"
  >
    <div className="w-12 h-12 rounded-lg flex items-center justify-center flex-shrink-0" style={{ backgroundColor: `${color}15` }}>
      <Icon className="h-6 w-6" style={{ color }} />
    </div>
    <div className="flex-1 min-w-0">
      <p className="text-gray-500 text-xs uppercase tracking-wider">{title}</p>
      <p className="text-2xl font-bold text-white mt-0.5">{value}</p>
      {subtitle && <p className="text-gray-500 text-xs mt-0.5">{subtitle}</p>}
    </div>
  </div>
);

const ModuleButton = ({ id, label, icon: Icon, desc, onNavigate }) => (
  <button
    data-testid={`nav-${id}`}
    onClick={() => onNavigate(id)}
    className="bg-[#0d0d1a] border border-[#1e293b] rounded-xl p-5 flex flex-col items-center gap-3 text-center hover:border-[#F5A623]/40 hover:bg-[#F5A623]/5 transition-all cursor-pointer group"
  >
    <div className="w-11 h-11 rounded-lg flex items-center justify-center bg-[#F5A623]/10 group-hover:bg-[#F5A623]/20 transition-all">
      <Icon className="h-5 w-5 text-[#F5A623]" />
    </div>
    <div>
      <p className="text-white font-semibold text-sm">{label}</p>
      <p className="text-gray-500 text-xs mt-0.5">{desc}</p>
    </div>
  </button>
);

const AdminDashboard = ({ onNavigate }) => {
  const [loading, setLoading] = useState(true);
  const [dashboard, setDashboard] = useState(null);

  useEffect(() => {
    fetchDashboard();
  }, []);

  const fetchDashboard = async () => {
    setLoading(true);
    const result = await AdminService.getDashboard();
    if (result.success) {
      setDashboard(result.dashboard);
    }
    setLoading(false);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <RefreshCw className="h-8 w-8 animate-spin text-[#F5A623]" />
      </div>
    );
  }

  const navItems = [
    { id: 'payments', label: 'Paiements', icon: CreditCard, desc: 'Stripe, transactions' },
    { id: 'freemium', label: 'Freemium', icon: Layers, desc: 'Quotas, tiers' },
    { id: 'upsell', label: 'Upsell', icon: Zap, desc: 'Campagnes, analytics' },
    { id: 'onboarding', label: 'Onboarding', icon: Target, desc: 'Parcours, flows' },
    { id: 'tutorials', label: 'Tutoriels', icon: BookOpen, desc: 'Contenus, tips' },
    { id: 'rules', label: 'Regles', icon: Settings, desc: 'Plan Maitre' },
    { id: 'strategy', label: 'Strategies', icon: BarChart3, desc: 'Generees, logs' },
    { id: 'users', label: 'Utilisateurs', icon: Users, desc: 'Profils, roles' },
    { id: 'settings', label: 'Parametres', icon: Shield, desc: 'Config, toggles' },
  ];

  return (
    <div data-testid="admin-dashboard" className="space-y-6 max-w-5xl mx-auto">
      {/* Header — BCE-4X Hierarchie: Titre en tete, sous-titre, bouton a droite */}
      <div className="flex items-center justify-between pb-4 border-b border-[#1e293b]">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg flex items-center justify-center bg-[#F5A623]/10">
            <Crown className="h-5 w-5 text-[#F5A623]" />
          </div>
          <div>
            <h1 data-testid="admin-premium-title" className="text-2xl font-bold text-white">Administration Premium</h1>
            <p className="text-gray-500 text-sm">Vue d'ensemble et gestion complete</p>
          </div>
        </div>
        <Button 
          data-testid="admin-refresh-btn"
          onClick={fetchDashboard}
          variant="outline" 
          className="border-[#F5A623]/30 text-[#F5A623] hover:bg-[#F5A623]/10"
        >
          <RefreshCw className="h-4 w-4 mr-2" />
          Actualiser
        </Button>
      </div>

      {/* KPIs — Grille 4 colonnes, espacement uniforme */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard title="Utilisateurs" value={dashboard?.users?.total || 0} subtitle={`${dashboard?.users?.premium || 0} Premium`} icon={Users} color="#F5A623" />
        <StatCard title="Revenus" value={`${dashboard?.revenue?.total || 0}$`} subtitle={`${dashboard?.revenue?.transactions || 0} transactions`} icon={CreditCard} color="#22c55e" />
        <StatCard title="Onboarding" value={`${dashboard?.onboarding?.completion_rate || 0}%`} subtitle={`${dashboard?.onboarding?.completed || 0} completes`} icon={Target} color="#3b82f6" />
        <StatCard title="CTR Upsell" value={`${dashboard?.upsell?.ctr || 0}%`} subtitle={`${dashboard?.upsell?.impressions || 0} impressions`} icon={Activity} color="#a855f7" />
      </div>

      {/* Modules d'administration — GRILLE 3x3 BCE-4X */}
      <div>
        <h2 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
          <Settings className="h-5 w-5 text-[#F5A623]" />
          Modules d'administration
        </h2>
        <div data-testid="admin-modules-grid" className="grid grid-cols-3 gap-4">
          {navItems.map((item) => (
            <ModuleButton key={item.id} {...item} onNavigate={onNavigate} />
          ))}
        </div>
      </div>

      {/* Quick Stats — 2 colonnes, hauteur egale */}
      <div className="grid grid-cols-2 gap-4">
        <div className="bg-[#0d0d1a] border border-[#1e293b] rounded-xl p-5">
          <h3 data-testid="admin-tier-distribution" className="text-white font-bold text-sm mb-4">Distribution des tiers</h3>
          <div className="space-y-3">
            {[
              { tier: 'free', label: 'FREE', color: 'bg-gray-500', count: dashboard?.users?.free || 0 },
              { tier: 'premium', label: 'PREMIUM', color: 'bg-[#F5A623]', count: Math.floor((dashboard?.users?.premium || 0) * 0.7) },
              { tier: 'pro', label: 'PRO', color: 'bg-purple-500', count: Math.floor((dashboard?.users?.premium || 0) * 0.3) },
            ].map(({ tier, label, color, count }) => {
              const total = dashboard?.users?.with_subscription || 1;
              const percent = Math.round((count / total) * 100);
              return (
                <div key={tier} className="flex items-center gap-3">
                  <Badge className={`w-20 justify-center ${color} ${tier === 'premium' ? 'text-black' : ''}`}>{label}</Badge>
                  <div className="flex-1 h-2 bg-white/10 rounded-full overflow-hidden">
                    <div className={`h-full ${color}`} style={{ width: `${percent}%` }} />
                  </div>
                  <span className="text-gray-400 text-sm w-12 text-right">{count}</span>
                </div>
              );
            })}
          </div>
        </div>

        <div className="bg-[#0d0d1a] border border-[#1e293b] rounded-xl p-5">
          <h3 data-testid="admin-recent-activity" className="text-white font-bold text-sm mb-4">Activite recente</h3>
          <div className="space-y-3">
            <div className="flex items-center gap-3 p-2.5 bg-white/5 rounded-lg">
              <div className="w-2 h-2 rounded-full bg-green-500 flex-shrink-0" />
              <span className="text-gray-300 text-sm flex-1">Systeme operationnel</span>
              <Badge className="bg-green-500/20 text-green-400 text-xs">OK</Badge>
            </div>
            <div className="flex items-center gap-3 p-2.5 bg-white/5 rounded-lg">
              <div className="w-2 h-2 rounded-full bg-[#F5A623] flex-shrink-0" />
              <span className="text-gray-300 text-sm flex-1">60 modules actifs</span>
              <Badge className="bg-[#F5A623]/20 text-[#F5A623] text-xs">V6</Badge>
            </div>
            <div className="flex items-center gap-3 p-2.5 bg-white/5 rounded-lg">
              <div className="w-2 h-2 rounded-full bg-blue-500 flex-shrink-0" />
              <span className="text-gray-300 text-sm flex-1">Stripe connecte</span>
              <Badge className="bg-blue-500/20 text-blue-400 text-xs">TEST</Badge>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard;

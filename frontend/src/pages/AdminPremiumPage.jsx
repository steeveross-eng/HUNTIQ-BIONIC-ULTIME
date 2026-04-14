/**
 * AdminPremiumPage - ADMIN v2 — Gouvernance Centrale Unifiee
 * ==========================================================
 * 
 * Interface unique d'administration HUNTIQ-V6.
 * Absorbe AdminPage + AdminPremiumPage en un seul module.
 * 
 * BCE-4X / STEEVE-MAX V6 — PHASE P0 FUSION ADMIN
 */

import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { toast } from 'sonner';
import axios from 'axios';
import {
  Crown, ArrowLeft, LayoutDashboard, CreditCard, Layers, 
  Zap, Target, BookOpen, Settings, BarChart3, Users, 
  FileText, Shield, ShoppingCart, FolderTree, Archive,
  Wrench, Contact, Trees, Network, Mail, Sparkles,
  Handshake, Palette, Brain, Search, ToggleLeft, Activity,
  FlaskConical, Power, Store, UserCheck, Megaphone, LayoutGrid, Lock,
  Database, RefreshCw, CheckCircle, AlertTriangle, TrendingUp,
} from 'lucide-react';

// Import all admin modules
import {
  AdminDashboard,
  AdminPayments,
  AdminFreemium,
  AdminUpsell,
  AdminOnboarding,
  AdminTutorials,
  AdminRules,
  AdminStrategy,
  AdminUsers,
  AdminLogs,
  AdminSettings,
  AdminEcommerce,
  AdminContent,
  AdminBackup,
  AdminMaintenance,
  AdminContacts,
  AdminHotspots,
  AdminNetworking,
  AdminEmail,
  AdminMarketing,
  AdminPartners,
  AdminBranding,
  AdminKnowledge,
  AdminSEO,
  AdminMarketingControls,
  AdminAnalytics,
  AdminCategories,
  AdminX300
} from '@/ui/administration';

// Import new modules - Phase 6+
import { AdminSuppliers } from '@/ui/administration/admin_suppliers';
import { AdminAffiliateSwitch } from '@/ui/administration/admin_affiliate_switch';
import { AdminAffiliateAds } from '@/ui/administration/admin_affiliate_ads';
import { AdminAdSpaces } from '@/ui/administration/admin_ad_spaces';
import { AdminGlobalSwitch } from '@/ui/administration/admin_global_switch';
import { AdminMessaging } from '@/ui/administration/admin_messaging';
// CAM-ALPHA: Module Analyse Photos ALPHA
import AdminAlphaAnalysis from '@/components/admin/AdminAlphaAnalysis';
import AdminTerritoryValue from '@/components/admin/AdminTerritoryValue';

const navItems = [
  { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
  // --- ALPHA Analysis ---
  { id: 'alpha-analysis', label: 'Analyse ALPHA', icon: Crown, highlight: true },
  { id: 'territory-value', label: 'Valeur Territoires', icon: TrendingUp, highlight: true },
  // --- BDRE-FIRST P1 ---
  { id: 'bdre', label: 'BDRE Monitor', icon: Shield, highlight: true },
  // --- SUPRA v2 & MAGASIN v2 ---
  { id: 'supra-engines', label: 'Moteurs SUPRA', icon: FlaskConical, highlight: true },
  { id: 'products-catalog', label: 'Catalogue Produits', icon: Store, highlight: true },
  // --- Gouvernance ---
  { id: 'global-switch', label: 'Master Switch', icon: Power, highlight: true },
  { id: 'messaging', label: 'Messaging Engine', icon: Mail, highlight: true },
  { id: 'x300', label: 'X300% Strategy', icon: Power, highlight: true },
  { id: 'affiliate-switch', label: 'Affiliate Switch', icon: UserCheck, highlight: true },
  { id: 'affiliate-ads', label: 'Affiliate Ads', icon: Megaphone, highlight: true },
  { id: 'ad-spaces', label: 'Ad Spaces', icon: LayoutGrid, highlight: true },
  { id: 'suppliers', label: 'Fournisseurs SEO', icon: Store },
  { id: 'analytics', label: 'Analytics', icon: Activity },
  { id: 'knowledge', label: 'Knowledge', icon: Brain },
  { id: 'seo', label: 'SEO Engine', icon: Search },
  { id: 'marketing-controls', label: 'Marketing ON/OFF', icon: ToggleLeft },
  { id: 'categories', label: 'Categories', icon: FlaskConical },
  { id: 'ecommerce', label: 'E-Commerce', icon: ShoppingCart },
  { id: 'hotspots', label: 'Terres/Hotspots', icon: Trees },
  { id: 'networking', label: 'Reseautage', icon: Network },
  { id: 'email', label: 'Emails', icon: Mail },
  { id: 'marketing', label: 'Marketing', icon: Sparkles },
  { id: 'partners', label: 'Partenaires', icon: Handshake },
  { id: 'branding', label: 'Branding', icon: Palette },
  { id: 'content', label: 'Contenu', icon: FolderTree },
  { id: 'backup', label: 'Backups', icon: Archive },
  { id: 'maintenance', label: 'Maintenance', icon: Wrench },
  { id: 'contacts', label: 'Contacts', icon: Contact },
  { id: 'payments', label: 'Paiements', icon: CreditCard },
  { id: 'freemium', label: 'Freemium', icon: Layers },
  { id: 'upsell', label: 'Upsell', icon: Zap },
  { id: 'onboarding', label: 'Onboarding', icon: Target },
  { id: 'tutorials', label: 'Tutoriels', icon: BookOpen },
  { id: 'rules', label: 'Regles', icon: Settings },
  { id: 'strategy', label: 'Strategies', icon: BarChart3 },
  { id: 'users', label: 'Utilisateurs', icon: Users },
  { id: 'logs', label: 'Logs', icon: FileText },
  { id: 'settings', label: 'Parametres', icon: Shield },
];

const AdminPremiumPage = () => {
  const navigate = useNavigate();
  const [activeSection, setActiveSection] = useState('dashboard');
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [password, setPassword] = useState('');
  const [loginLoading, setLoginLoading] = useState(false);

  const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

  useEffect(() => {
    const auth = localStorage.getItem('admin_premium_authenticated');
    if (auth === 'true') setIsAuthenticated(true);
  }, []);

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoginLoading(true);
    try {
      await axios.post(`${BACKEND_URL}/api/auth/login`, {
        email: "admin@huntiq.com",
        password,
      });
      localStorage.setItem('admin_premium_authenticated', 'true');
      setIsAuthenticated(true);
      toast.success("Connexion Admin Premium reussie!");
    } catch {
      toast.error("Mot de passe incorrect");
    }
    setLoginLoading(false);
  };

  const handleLogout = () => {
    localStorage.removeItem('admin_premium_authenticated');
    setIsAuthenticated(false);
    navigate('/');
  };

  if (!isAuthenticated) {
    return (
      <main className="min-h-screen bg-[#050510] flex items-center justify-center">
        <Card className="w-full max-w-md bg-[#0a0a15] border-[#F5A623]/20 p-8">
          <div className="text-center mb-6">
            <Lock className="h-12 w-12 text-[#F5A623] mx-auto mb-3" />
            <h2 className="text-xl font-bold text-white">Admin Premium</h2>
            <p className="text-gray-500 text-sm mt-1">Acces securise — mot de passe requis</p>
          </div>
          <form onSubmit={handleLogin} className="space-y-4">
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Mot de passe administrateur"
              className="w-full bg-black border border-gray-700 rounded-lg px-4 py-3 text-white placeholder-gray-500 focus:border-[#F5A623] focus:outline-none"
              data-testid="admin-premium-password-input"
            />
            <Button type="submit" className="w-full bg-[#F5A623] text-black font-bold" disabled={loginLoading} data-testid="admin-premium-login-btn">
              {loginLoading ? 'Connexion...' : 'Se connecter'}
            </Button>
          </form>
        </Card>
      </main>
    );
  }

  const renderContent = () => {
    switch (activeSection) {
      case 'dashboard': return <AdminDashboard onNavigate={setActiveSection} />;
      case 'alpha-analysis': return <AdminAlphaAnalysis />;
      case 'territory-value': return <AdminTerritoryValue />;
      case 'bdre': return <AdminBDREMonitor />;
      case 'supra-engines': return <AdminSupraEngines />;
      case 'products-catalog': return <AdminProductsCatalog />;
      case 'global-switch': return <AdminGlobalSwitch />;
      case 'messaging': return <AdminMessaging />;
      case 'x300': return <AdminX300 />;
      case 'affiliate-switch': return <AdminAffiliateSwitch />;
      case 'affiliate-ads': return <AdminAffiliateAds />;
      case 'ad-spaces': return <AdminAdSpaces />;
      case 'suppliers': return <AdminSuppliers />;
      case 'analytics': return <AdminAnalytics />;
      case 'knowledge': return <AdminKnowledge />;
      case 'seo': return <AdminSEO />;
      case 'marketing-controls': return <AdminMarketingControls />;
      case 'categories': return <AdminCategories />;
      case 'ecommerce': return <AdminEcommerce />;
      case 'hotspots': return <AdminHotspots />;
      case 'networking': return <AdminNetworking />;
      case 'email': return <AdminEmail />;
      case 'marketing': return <AdminMarketing />;
      case 'partners': return <AdminPartners />;
      case 'branding': return <AdminBranding />;
      case 'content': return <AdminContent />;
      case 'backup': return <AdminBackup />;
      case 'maintenance': return <AdminMaintenance />;
      case 'contacts': return <AdminContacts />;
      case 'payments': return <AdminPayments />;
      case 'freemium': return <AdminFreemium />;
      case 'upsell': return <AdminUpsell />;
      case 'onboarding': return <AdminOnboarding />;
      case 'tutorials': return <AdminTutorials />;
      case 'rules': return <AdminRules />;
      case 'strategy': return <AdminStrategy />;
      case 'users': return <AdminUsers />;
      case 'logs': return <AdminLogs />;
      case 'settings': return <AdminSettings />;
      default: return <AdminDashboard onNavigate={setActiveSection} />;
    }
  };

  return (
    <main 
      data-testid="admin-premium-page" 
      className="min-h-screen bg-[#050510] pt-20"
    >
      <div className="flex">
        {/* Sidebar — STANDARD GOLDEN */}
        <aside className="fixed left-0 top-16 h-[calc(100vh-4rem)] w-64 p-4 overflow-y-auto" style={{ backgroundColor: '#0F172A' }}>
          {/* Logo */}
          <div className="flex items-center gap-3 mb-6 p-3 rounded-xl" style={{ backgroundColor: '#1E293B', borderLeft: '4px solid #F5A623' }}>
            <div className="w-8 h-8 rounded-full flex items-center justify-center" style={{ backgroundColor: '#F5A62320' }}>
              <Crown className="h-4 w-4 text-[#F5A623]" />
            </div>
            <div>
              <h1 className="text-white font-bold text-[16px]">ADMIN v2</h1>
              <p className="text-gray-500 text-[14px]">Gouvernance Centrale</p>
            </div>
          </div>

          {/* Back Button */}
          <Button
            variant="ghost"
            onClick={() => navigate('/')}
            className="w-full justify-start text-gray-400 hover:text-white hover:bg-white/5 mb-4"
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Retour à l'app
          </Button>

          {/* Navigation */}
          <nav className="space-y-1">
            {navItems.map((item) => (
              <Button
                key={item.id}
                data-testid={`sidebar-${item.id}`}
                variant="ghost"
                onClick={() => setActiveSection(item.id)}
                className={`
                  w-full justify-start transition-all
                  ${activeSection === item.id 
                    ? 'bg-[#F5A623]/10 text-[#F5A623] border-l-2 border-[#F5A623]' 
                    : 'text-gray-400 hover:text-white hover:bg-white/5'
                  }
                `}
              >
                <item.icon className="h-4 w-4 mr-3" />
                {item.label}
              </Button>
            ))}
          </nav>
        </aside>

        {/* Main Content */}
        <div className="ml-64 flex-1 p-8">
          {renderContent()}
        </div>
      </div>
    </main>
  );
};

// === ADMIN v2 — Moteurs SUPRA ===
const AdminSupraEngines = () => {
  const [engines, setEngines] = useState([]);
  const [loading, setLoading] = useState(true);
  const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

  useEffect(() => {
    const fetchEngines = async () => {
      try {
        const res = await axios.get(`${BACKEND_URL}/api/v1/saline/engines/status`);
        setEngines(res.data.engines || []);
      } catch {
        // Fallback: moteurs statiques
        setEngines([
          { id: 'soil', name: 'Moteur Sol', status: 'active', version: '2.1' },
          { id: 'deficiency', name: 'Moteur Carence', status: 'active', version: '3.0' },
          { id: 'vegetation', name: 'Moteur Vegetation', status: 'active', version: '2.5' },
          { id: 'hydrology', name: 'Moteur Hydrologie', status: 'active', version: '1.8' },
          { id: 'metabolism', name: 'Moteur Metabolisme', status: 'active', version: '2.0' },
          { id: 'weather', name: 'Weather Engine v3', status: 'active', version: '3.0' },
          { id: 'competition', name: 'Moteur Competition', status: 'active', version: '1.5' },
        ]);
      } finally {
        setLoading(false);
      }
    };
    fetchEngines();
  }, [BACKEND_URL]);

  return (
    <div data-testid="admin-supra-engines">
      <div className="flex items-center gap-3 mb-6">
        <FlaskConical className="h-6 w-6 text-[#FF9800]" />
        <h2 className="text-xl font-bold text-white">Moteurs SUPRA v2</h2>
        <span className="text-xs text-gray-500 ml-auto">7 moteurs ULTRA integres</span>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {engines.map(engine => (
          <Card key={engine.id} className="bg-[#0a0a15] border-white/5 p-4" data-testid={`engine-${engine.id}`}>
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-white font-bold text-sm">{engine.name}</h3>
                <p className="text-gray-500 text-xs mt-1">v{engine.version}</p>
              </div>
              <span className={`px-2.5 py-1 rounded-full text-xs font-bold ${engine.status === 'active' ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'}`}>
                {engine.status === 'active' ? 'ACTIF' : 'INACTIF'}
              </span>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
};

// === ADMIN v2 — Catalogue Produits ===
const AdminProductsCatalog = () => {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

  useEffect(() => {
    const fetchProducts = async () => {
      try {
        const res = await axios.get(`${BACKEND_URL}/api/v1/saline/shop/products`);
        setProducts(res.data.products || []);
      } catch (e) {
        console.error('Admin products fetch:', e);
      } finally {
        setLoading(false);
      }
    };
    fetchProducts();
  }, [BACKEND_URL]);

  return (
    <div data-testid="admin-products-catalog">
      <div className="flex items-center gap-3 mb-6">
        <Store className="h-6 w-6 text-[#FF9800]" />
        <h2 className="text-xl font-bold text-white">Catalogue SALINE_PRODUCTS</h2>
        <span className="text-xs text-gray-500 ml-auto">{products.length} produits</span>
      </div>
      {loading ? (
        <p className="text-gray-500">Chargement...</p>
      ) : (
        <div className="space-y-2">
          {products.map(p => (
            <Card key={p.id} className="bg-[#0a0a15] border-white/5 p-3" data-testid={`admin-product-${p.id}`}>
              <div className="flex items-center gap-4">
                <div className="w-10 h-10 rounded-lg flex items-center justify-center bg-[#FF9800]/10 border border-[#FF9800]/30 flex-shrink-0">
                  <span className="text-sm font-black text-[#FF9800]">{p.score}</span>
                </div>
                <div className="flex-1 min-w-0">
                  <h3 className="text-white font-semibold text-sm truncate">{p.name}</h3>
                  <p className="text-gray-500 text-xs">{p.brand} | {p.product_format} | {p.weight}</p>
                </div>
                <span className="text-[#FF9800] font-bold">${p.price}</span>
                <div className="flex flex-wrap gap-1 max-w-[120px]">
                  {p.target_animals?.slice(0, 2).map(a => (
                    <span key={a} className="text-[10px] px-1.5 py-0.5 rounded bg-white/5 text-gray-400">{a}</span>
                  ))}
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
};

// === ADMIN v2 — BDRE Monitor (P1 BDRE-FIRST) ===
const AdminBDREMonitor = () => {
  const [dashboard, setDashboard] = useState(null);
  const [sources, setSources] = useState([]);
  const [anomalies, setAnomalies] = useState([]);
  const [auditLog, setAuditLog] = useState([]);
  const [loading, setLoading] = useState(true);
  const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

  const fetchAll = useCallback(async () => {
    setLoading(true);
    try {
      const [dashRes, srcRes, anomRes, auditRes] = await Promise.all([
        axios.get(`${BACKEND_URL}/api/v1/bdre/dashboard`),
        axios.get(`${BACKEND_URL}/api/v1/bdre/sources`),
        axios.get(`${BACKEND_URL}/api/v1/bdre/anomalies/recent?limit=10`),
        axios.get(`${BACKEND_URL}/api/v1/bdre/audit/log?limit=20`),
      ]);
      setDashboard(dashRes.data);
      setSources(srcRes.data.sources || []);
      setAnomalies(anomRes.data.anomalies || []);
      setAuditLog(auditRes.data.entries || []);
    } catch (e) {
      console.error('BDRE fetch error:', e);
    } finally {
      setLoading(false);
    }
  }, [BACKEND_URL]);

  useEffect(() => { fetchAll(); }, [fetchAll]);

  const healthyCount = sources.filter(s => s.status === 'healthy').length;
  const offlineCount = sources.filter(s => s.status !== 'healthy').length;
  const avgScore = sources.length > 0 ? (sources.reduce((sum, s) => sum + (s.score || 0), 0) / sources.length) : 0;

  return (
    <div data-testid="admin-bdre-monitor">
      <div className="flex items-center gap-3 mb-6">
        <Shield className="h-6 w-6 text-[#F5A623]" />
        <h2 className="text-xl font-bold text-white">BDRE Monitor</h2>
        <span className="text-xs text-gray-500 ml-auto">BIONIC Data Reliability Engine</span>
        <Button variant="outline" size="sm" onClick={fetchAll} className="border-gray-700 text-gray-400" data-testid="admin-bdre-refresh">
          <RefreshCw className="h-3.5 w-3.5" />
        </Button>
      </div>

      {loading ? (
        <p className="text-gray-500">Chargement BDRE...</p>
      ) : (
        <div className="space-y-4">
          {/* Stats Cards */}
          <div className="grid grid-cols-5 gap-3">
            <Card className="bg-[#0a0a15] border-white/5 p-4 text-center">
              <div className="text-[#F5A623] text-lg font-bold">{dashboard?.bdre_version || '—'}</div>
              <div className="text-[10px] text-gray-500 uppercase">Version</div>
            </Card>
            <Card className="bg-[#0a0a15] border-white/5 p-4 text-center">
              <div className="text-green-400 text-lg font-bold">{healthyCount}</div>
              <div className="text-[10px] text-gray-500 uppercase">Actives</div>
            </Card>
            <Card className="bg-[#0a0a15] border-white/5 p-4 text-center">
              <div className="text-gray-400 text-lg font-bold">{offlineCount}</div>
              <div className="text-[10px] text-gray-500 uppercase">Hors ligne</div>
            </Card>
            <Card className="bg-[#0a0a15] border-white/5 p-4 text-center">
              <div className="text-yellow-400 text-lg font-bold">{dashboard?.audit_stats?.total_fallbacks ?? 0}</div>
              <div className="text-[10px] text-gray-500 uppercase">Fallbacks</div>
            </Card>
            <Card className="bg-[#0a0a15] border-white/5 p-4 text-center">
              <div className={`text-lg font-bold ${avgScore >= 0.6 ? 'text-green-400' : avgScore >= 0.3 ? 'text-yellow-400' : 'text-red-400'}`}>{(avgScore * 100).toFixed(0)}%</div>
              <div className="text-[10px] text-gray-500 uppercase">Score Moyen</div>
            </Card>
          </div>

          {/* Sources Registry */}
          <Card className="bg-[#0a0a15] border-white/5 p-4">
            <h3 className="text-sm font-bold text-white mb-3 flex items-center gap-2">
              <Database className="h-4 w-4 text-blue-400" /> Registre des Sources ({sources.length})
            </h3>
            <div className="space-y-1.5 max-h-[300px] overflow-y-auto">
              {sources.map((src, i) => (
                <div key={i} className="flex items-center justify-between bg-black/30 px-3 py-2 rounded" data-testid={`admin-src-${src.source_id}`}>
                  <div className="flex items-center gap-2">
                    <span className={`w-2 h-2 rounded-full ${src.status === 'healthy' ? 'bg-green-400' : 'bg-gray-500'}`} />
                    <span className="text-xs font-mono text-[#F5A623]">{src.source_id}</span>
                    <span className="text-xs text-gray-300">{src.name}</span>
                    <span className="text-[10px] text-gray-600">{src.type}</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="w-16 h-1.5 bg-gray-800 rounded-full overflow-hidden">
                      <div className={`h-full rounded-full ${src.score >= 0.8 ? 'bg-green-500' : src.score >= 0.3 ? 'bg-yellow-500' : 'bg-red-500'}`} style={{ width: `${src.score * 100}%` }} />
                    </div>
                    <span className="text-xs text-gray-400 w-10 text-right">{(src.score * 100).toFixed(0)}%</span>
                    <span className={`text-[10px] px-1.5 py-0.5 rounded ${src.status === 'healthy' ? 'bg-green-500/20 text-green-400' : 'bg-gray-700 text-gray-400'}`}>
                      {src.status}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </Card>

          {/* Engines + Audit */}
          <div className="grid grid-cols-2 gap-4">
            <Card className="bg-[#0a0a15] border-white/5 p-4">
              <h3 className="text-sm font-bold text-white mb-3 flex items-center gap-2">
                <Zap className="h-4 w-4 text-green-400" /> Engines Integres
              </h3>
              <div className="space-y-1.5">
                {(dashboard?.engines_integrated || []).map((eng, i) => (
                  <div key={i} className="flex items-center gap-2 bg-black/30 px-3 py-2 rounded">
                    <CheckCircle className="h-3 w-3 text-green-400" />
                    <span className="text-xs text-gray-300">{eng}</span>
                  </div>
                ))}
              </div>
            </Card>

            <Card className="bg-[#0a0a15] border-white/5 p-4">
              <h3 className="text-sm font-bold text-white mb-3 flex items-center gap-2">
                <FileText className="h-4 w-4 text-purple-400" /> Journal Recent ({auditLog.length})
              </h3>
              <div className="space-y-1 max-h-[200px] overflow-y-auto">
                {auditLog.map((entry, i) => (
                  <div key={i} className="bg-black/30 px-3 py-1.5 rounded">
                    <div className="flex items-center gap-2">
                      <span className="text-[10px] text-gray-600">{entry.engine}</span>
                      <span className="text-xs text-gray-300">{entry.action}</span>
                      {entry.fallback_level > 0 && <span className="text-[9px] px-1 py-0.5 rounded bg-yellow-900/50 text-yellow-300">L{entry.fallback_level}</span>}
                    </div>
                  </div>
                ))}
              </div>
            </Card>
          </div>

          {/* Anomalies */}
          {anomalies.length > 0 && (
            <Card className="bg-red-950/20 border-red-800/30 p-4">
              <h3 className="text-sm font-bold text-red-300 mb-3 flex items-center gap-2">
                <AlertTriangle className="h-4 w-4 text-red-400" /> Anomalies ({anomalies.length})
              </h3>
              <div className="space-y-1.5">
                {anomalies.map((a, i) => (
                  <div key={i} className="bg-red-900/20 px-3 py-2 rounded border-l-2 border-red-500/40">
                    <span className="text-xs text-red-200">{a.type}: {a.details || a.message}</span>
                  </div>
                ))}
              </div>
            </Card>
          )}
        </div>
      )}
    </div>
  );
};

export default AdminPremiumPage;

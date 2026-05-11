import { useEffect, useState, useCallback, lazy, Suspense } from "react";
import "@/App.css";
import { BrowserRouter, Routes, Route, Link, useLocation, useNavigate, Navigate } from "react-router-dom";
import axios from "axios";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";

// BLOC 2 OPTIMIZATION: Critical path components (loaded synchronously)
import CookieConsent from "@/components/CookieConsent";
import SEOHead from "@/components/SEOHead";
import { AuthProvider, UserMenu, useAuth } from "@/components/GlobalAuth";
import { OfflineIndicator } from "@/components/OfflineIndicator";
import { LanguageProvider, useLanguage, LanguageSwitcher } from "@/contexts/LanguageContext";
import BionicLogo, { BionicLogoGlobal, BionicLogoHeader } from "@/components/BionicLogo";
import ScrollNavigator from "@/components/ScrollNavigator";
import { NotificationProvider } from "@/modules/notifications";
// V6 GOLDEN: Centre de notifications push temps réel
import AlertNotificationCenter from "@/components/AlertNotificationCenter";
// P5-OPTIMIZATION V2: Cart Panel (x5400-G)
import { CartPanel } from "@/modules/cart";
import { CartService } from "@/modules/cart";

// BCE-4X PURGE: Imports fantomes SUPPRIMES (STEEVE-MAX directive)
// 15 composants importes sans route ont ete supprimes:
// AnalyzerModule, TerritoryMap, HuntMarketplace, ContentDepot, SiteAccessControl,
// MaintenancePage, LandsPricingAdmin, NetworkingAdmin, NotificationCenter,
// EmailAdmin, FeatureControlsAdmin, ProductDiscoveryAdmin,
// ReferralAdminPanel, DynamicReferralWidget, AdminPage
const LandsRental = lazy(() => import("@/components/LandsRental"));
const NetworkingHub = lazy(() => import("@/components/NetworkingHub"));
const ResetPasswordPage = lazy(() => import("@/components/ResetPasswordPage"));
const BecomePartner = lazy(() => import("@/components/BecomePartner"));
const PartnerDashboard = lazy(() => import("@/components/PartnerDashboard"));
const ReferralModule = lazy(() => import("@/components/ReferralModule"));
const GoogleOAuthCallback = lazy(() => import("@/components/GoogleOAuthCallback"));
// PHASE XX (Ordre n°40) : Widget institutionnel TERRITOIRE_APTE_Ω
const WidgetTerritoireApteOmega = lazy(() => import("@/components/WidgetTerritoireApteOmega"));

// BLOC 2 OPTIMIZATION: Lazy-loaded pages
// BCE-4X PURGE: AdminPage SUPPRIME — Admin v2 = AdminPremiumPage (source unique)
const MonTerritoireBionicPage = lazy(() => import("@/pages/MonTerritoireBionicPage"));
const TripsPage = lazy(() => import("@/pages/TripsPage"));
const ShopPage = lazy(() => import("@/pages").then(m => ({ default: m.ShopPage })));
const ComparePage = lazy(() => import("@/pages").then(m => ({ default: m.ComparePage })));
const DashboardPage = lazy(() => import("@/pages/DashboardPage"));
const BusinessPage = lazy(() => import("@/pages/BusinessPage"));
const PlanMaitrePage = lazy(() => import("@/pages/intelligence/PlanMaitrePage"));
const AnalyticsPage = lazy(() => import("@/pages/intelligence/AnalyticsPage"));
// CARTE-RETRAIT-Omega: MapPage retire pour lancement 2026
const ForecastPage = lazy(() => import("@/pages/intelligence/ForecastPage"));
// V6-M3-DASHBOARD: Intelligence V6 Dashboard (x7000-M3-DASHBOARD)
const IntelligenceV6Page = lazy(() => import("@/pages/intelligence/IntelligenceV6Page"));
const AdminGeoPage = lazy(() => import("@/pages/AdminGeoPage"));
const OnboardingPage = lazy(() => import("@/pages/OnboardingPage"));
const PricingPage = lazy(() => import("@/pages/PricingPage"));
const PaymentSuccessPage = lazy(() => import("@/pages/PaymentSuccessPage"));
const PaymentCancelPage = lazy(() => import("@/pages/PaymentCancelPage"));
const AdminPremiumPage = lazy(() => import("@/pages/AdminPremiumPage"));
const MarketingCalendarPage = lazy(() => import("@/pages/MarketingCalendarPage"));
const HuntingLicensePage = lazy(() => import("@/pages/HuntingLicensePage"));
const BionicAnalysisDemoPage = lazy(() => import("@/pages/BionicAnalysisDemoPage"));
// V6 GOLDEN: Interface d'observations terrain
const FieldObservationForm = lazy(() => import("@/pages/FieldObservationForm"));
// CALIBRATION MASTER: Dashboard de calibration
const CalibrationDashboard = lazy(() => import("@/pages/CalibrationDashboard"));
const ReportsPage = lazy(() => import("@/pages/ReportsPage"));
const SpeciesComparisonPage = lazy(() => import("@/pages/SpeciesComparisonPage"));
// SUPRA v2: NutritionIntelligencePage SUPPRIMEE — moteur unifie dans SUPRA LOCAL (NutritionPointDetailPanel)
// NUTRITION INTELLIGENCE SUPRA — x5000 (STEEVE-MAX x5100-x5900)
// SUPRA LOCAL unifie — ancien module global ABANDONNE (BCE-4X / STEEVE-MAX)
const ProductPage = lazy(() => import("@/pages/ProductPage"));
const SupraPage = lazy(() => import("@/pages/SupraPage"));
// BIONIC MODULES — 10 modules predictifs (STEEVE-MAX x2000)
const BionicModulesPage = lazy(() => import("@/pages/BionicModulesPage"));
// BSAA — BIONIC Social Ads Automation (x4500-ULTRA)
const BsaaDashboardPage = lazy(() => import("@/pages/BsaaDashboardPage"));
// GUIDE PRO — Phase E-2 Frontend (BCE-4X BDRE-FIRST)
const GuideProPage = lazy(() => import("@/pages/GuideProPage"));
// GESTIONNAIRE — Phase F Frontend (BCE-4X BDRE-FIRST)
const GestionnairePage = lazy(() => import("@/pages/GestionnairePage"));
// ORDRE N°47 — Auth Guard Saturn5858* sur /gestionnaire
const GestionnaireAuthGuard = lazy(() => import("@/components/auth/GestionnaireAuthGuard"));
// CAM-Omega: Module Cameras de chasse
const CameraModule = lazy(() => import("@/components/CameraModule"));
const Carte2027Page = lazy(() => import("@/pages/Carte2027Page"));
// Phase XI-SUPRA-D : Route stable pour captures Playwright institutionnelles
// Import statique (pas lazy) pour éviter tout remount/suspense sur capture-mode
import TerritoireCaptureModePage from "@/pages/TerritoireCaptureModePage";
import HudUltimeDemoPage from "@/pages/HudUltimeDemoPage";
// P21 ADMIN_PREMIUM_FRONTEND_INTEGRATION_Ω · BCE-4X ULTIME ABSOLU
const AdminPremiumLayout = lazy(() => import("@/components/admin-premium/AdminPremiumLayout"));
const AdminPremiumIndexPage = lazy(() => import("@/components/admin-premium/AdminPremiumIndexPage"));
const Visualizer18Page = lazy(() => import("@/components/admin-premium/Visualizer18Page"));
const TerritoireReportPage = lazy(() => import("@/components/admin-premium/TerritoireReportPage"));
const WaypointGuidePage = lazy(() => import("@/components/admin-premium/WaypointGuidePage"));
const LayerManualPage = lazy(() => import("@/components/admin-premium/LayerManualPage"));
const MerkleAuditPage = lazy(() => import("@/components/admin-premium/MerkleAuditPage"));
const ValidationsPage = lazy(() => import("@/components/admin-premium/ValidationsPage"));
// P22C · TERRITOIRE FRONTEND DEBUG OVERLAY (URL flag activated)
import TerritoireFrontendDebugOverlay from "@/components/territoire/TerritoireFrontendDebugOverlay";
import CorridorsDebugOverlay from "@/components/territoire/CorridorsDebugOverlay";
import LocalCorridorLensPanel from "@/components/territoire/LocalCorridorLensPanel";
// P22Σ_V3 · FUSION VEINEUSE DIAGNOSTIC PANEL (URL flag ?fusionDebug=on)
import FusionDebugPanel from "@/components/territoire/FusionDebugPanel";
// VIS-E: Vision Notifications Panel
import VisionNotificationsPanel from '@/components/VisionNotificationsPanel';
// PHASE_X200_P4_RUNTIME_BEACON_Ω — attestation runtime institutionnelle (LAT 48.206657 / LNG -68.382422)
import { startRuntimeBeaconOmega } from '@/services/runtimeBeaconOmega';
// V7.2: AdminHotspotsPage standalone SUPPRIME — Source de verite = Admin Premium (directive x7200)
import { 
  ShoppingCart, FlaskConical, GitCompare, Star, DollarSign, ThumbsUp, Heart, Eye,
  Shield, MousePointer, TrendingUp, CheckCircle, ChevronRight, Menu, X, ArrowLeft,
  Package, Users, Store, Percent, BarChart3, Award, Info, Lock, Clock, AlertTriangle,
  ExternalLink, Edit, Plus, Loader2, GraduationCap, BookOpen, Brain,
  Map, Globe, Construction, Power, Mail, Handshake, XCircle, Moon, Sun, Bot,
  Radar, Share2, Gift, Home, Target, Crosshair, Route as RouteIcon, Briefcase, Cloud,
  Crown, Camera, Bell
} from "lucide-react";
import {
  Sheet, SheetContent, SheetDescription, SheetHeader, SheetTitle
} from "@/components/ui/sheet";
import {
  DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger
} from "@/components/ui/dropdown-menu";
import { Progress } from "@/components/ui/progress";
import { Toaster, toast } from "sonner";
// BCE-4X V8: ShareBionicButton relocalisé dans TerritoireHeader (Directive ×4850)

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// BLOC 2 OPTIMIZATION: Lazy loading fallback component
const LazyLoadFallback = () => (
  <div className="min-h-screen bg-background flex items-center justify-center">
    <Loader2 className="h-8 w-8 animate-spin text-[#f5a623]" />
  </div>
);

// SUPRA v2: Session saline unifiee (remplace cart_session_id generique)
const getSessionId = () => {
  let sessionId = localStorage.getItem("saline_session_id");
  if (!sessionId) {
    sessionId = "sal_" + Math.random().toString(36).substr(2, 12);
    localStorage.setItem("saline_session_id", sessionId);
  }
  return sessionId;
};

// Logo Component
const Logo = ({ size = "default" }) => {
  const { brand } = useLanguage();
  return (
    <div className={`flex items-center gap-2 ${size === "large" ? "scale-125" : ""}`}>
      <BionicLogo className={size === "large" ? "h-10 w-10" : "h-8 w-8"} />
      <span className={`font-bold text-white ${size === "large" ? "text-2xl" : "text-xl"}`}>
        {brand.short}
      </span>
    </div>
  );
};

// Navigation Component - BIONIC TACTICAL Design System
const Navigation = ({ cartCount, onCartOpen }) => {
  const { t } = useLanguage();
  const { user } = useAuth();
  const location = useLocation();
  const [isOpen, setIsOpen] = useState(false);

  // Role-based navigation visibility
  const isBusinessOrAdmin = user && ['business', 'admin'].includes(user.role);
  const isAdmin = user && user.role === 'admin';

  // Check if route is active
  const isActive = (path) => location.pathname === path;

  return (
    <header className="fixed top-0 left-0 right-0 z-50 bg-black/80 backdrop-blur-xl border-b border-white/10">
      <div className="max-w-[1800px] mx-auto px-6">
        <div className="flex items-center justify-between" style={{ height: '136px' }}>
          {/* Logo 128px DANS le header — BCE-4X Phase L v6 */}
          <BionicLogoHeader />
          
          {/* Desktop Navigation - BIONIC TACTICAL Style */}
          <nav className="hidden lg:flex items-center gap-0 flex-1 min-w-0" style={{ overflow: 'visible' }}>
            {/* Home */}
            <Link 
              to="/" 
              className={`flex items-center gap-1 px-1.5 py-2 text-[11px] font-medium uppercase tracking-wider rounded-sm transition-all duration-200 hover:bg-white/5 whitespace-nowrap flex-shrink-0 ${isActive('/') ? 'text-[#F5A623] bg-[#F5A623]/10' : 'text-gray-300 hover:text-white'}`}
              data-testid="nav-home"
            >
              <Home className="h-3.5 w-3.5" />
              {t('common_home')}
            </Link>

            {/* MAGASIN — Restauré entre Accueil et Tableau de bord (CAM-UI-LOC) */}
            <Link 
              to="/shop" 
              className={`flex items-center gap-1 px-1.5 py-2 text-[11px] font-medium uppercase tracking-wider rounded-sm transition-all duration-200 hover:bg-white/5 whitespace-nowrap flex-shrink-0 ${isActive('/shop') ? 'text-[#F5A623] bg-[#F5A623]/10' : 'text-gray-300 hover:text-white'}`}
              data-testid="nav-shop"
            >
              <Store className="h-3.5 w-3.5" />
              {t('nav_shop')}
            </Link>
            
            {/* V5.2: T. BORD fusionne dans INTELLIGENCE — Lien supprime */}
            
            {/* TERRITOIRE_ROUTE_RESTORE_Ω (2026-05-11 · STEEVE-MAX X11) — bouton TERRITOIRE Ω */}
            <Link 
              to="/territoire" 
              className={`flex items-center gap-1 px-1.5 py-2 text-[11px] font-medium uppercase tracking-wider rounded-sm transition-all duration-200 hover:bg-white/5 whitespace-nowrap flex-shrink-0 ${isActive('/territoire') ? 'text-[#FF6A00] bg-[#FF6A00]/10' : 'text-gray-300 hover:text-white'}`}
              data-testid="nav-territoire"
              title="Carte TERRITOIRE Ω · corridors Ω, zones Ω, contamination Ω, vent Ω"
            >
              <Map className="h-3.5 w-3.5" />
              Territoire
            </Link>

            {/* ANALYSE TERRITOIRE — Module SENSORIEL Ω (analyse approfondie) */}
            <Link 
              to="/mon-territoire-bionic" 
              className={`flex items-center gap-1 px-1.5 py-2 text-[11px] font-medium uppercase tracking-wider rounded-sm transition-all duration-200 hover:bg-white/5 whitespace-nowrap flex-shrink-0 ${['/mon-territoire-bionic', '/mon-territoire', '/analyse-territoire'].includes(location.pathname) ? 'text-[#F5A623] bg-[#F5A623]/10' : 'text-gray-300 hover:text-white'}`}
              data-testid="nav-analyse-territoire"
              title="Analyse Territoire BIONIC · SENSORIEL Ω"
            >
              <Crosshair className="h-3.5 w-3.5" />
              Analyse
            </Link>
            
            {/* CARTE-2027-REBUILD-Omega: Carte terrain V7 active */}
            <Link 
              to="/carte-2027" 
              className={`flex items-center gap-1 px-1.5 py-2 text-[11px] font-medium uppercase tracking-wider rounded-sm transition-all duration-200 hover:bg-white/5 whitespace-nowrap flex-shrink-0 ${isActive('/carte-2027') ? 'text-[#10B981] bg-[#10B981]/10' : 'text-gray-300 hover:text-white'}`}
              data-testid="nav-carte-2027"
            >
              <Map className="h-3.5 w-3.5" />
              Carte
            </Link>

            {/* CAM-ADMIN-HEADER: Module Cameras — entre CARTE et INTELLIGENCE */}
            <Link 
              to="/cameras" 
              className={`flex items-center gap-1 px-1.5 py-2 text-[11px] font-medium uppercase tracking-wider rounded-sm transition-all duration-200 hover:bg-white/5 whitespace-nowrap flex-shrink-0 ${isActive('/cameras') ? 'text-[#F5A623] bg-[#F5A623]/10' : 'text-gray-300 hover:text-white'}`}
              data-testid="nav-cameras"
            >
              <Camera className="h-3.5 w-3.5" />
              Cameras
            </Link>
            
            {/* INTELLIGENCE V6-CORE — TOUJOURS VISIBLE */}
            <Link 
              to="/intelligence-v6" 
              className={`flex items-center gap-1 px-1.5 py-2 text-[11px] font-medium uppercase tracking-wider rounded-sm transition-all duration-200 hover:bg-white/5 whitespace-nowrap flex-shrink-0 ${isActive('/intelligence-v6') ? 'text-[#F5A623] bg-[#F5A623]/10' : 'text-gray-300 hover:text-white'}`}
              data-testid="nav-intelligence-v6"
            >
              <Brain className="h-3.5 w-3.5" />
              Intelligence
            </Link>
            
            {/* Permis de chasse */}
            <Link 
              to="/permis-chasse" 
              className={`flex items-center gap-1 px-1.5 py-2 text-[11px] font-medium uppercase tracking-wider rounded-sm transition-all duration-200 hover:bg-white/5 whitespace-nowrap flex-shrink-0 ${isActive('/permis-chasse') ? 'text-[#F5A623] bg-[#F5A623]/10' : 'text-gray-300 hover:text-white'}`}
              data-testid="nav-permis-chasse"
            >
              <Shield className="h-3.5 w-3.5" />
              Permis
            </Link>
            
            {/* SUPRA v2: Lien direct ANALYSE TERRITOIRE (moteur unifie) */}
            
            {/* Business (Conditionnel) */}
            {isBusinessOrAdmin && (
              <Link 
                to="/business" 
                className={`flex items-center gap-1.5 px-2 py-2 text-xs font-medium uppercase tracking-wider rounded-sm transition-all duration-200 hover:bg-white/5 whitespace-nowrap flex-shrink-0 ${isActive('/business') ? 'text-[#10B981] bg-[#10B981]/10' : 'text-[#10B981]/70 hover:text-[#10B981]'}`}
                data-testid="nav-business"
              >
                <Briefcase className="h-3.5 w-3.5" />
                Business
              </Link>
            )}
          </nav>
          
          {/* Right Content */}
          <div className="flex items-center gap-1.5 lg:gap-2 flex-shrink-0">
            {/* BCE-4X V8: PARTAGER relocalisé dans TerritoireHeader.jsx (sub-header) — Directive ×4850 */}
            
            {/* Premium CTA — BCE-4X: texte blanc + contour orange #F5A623 unifie */}
            {/* VIS-E: Alertes IA */}
            <VisionNotificationsToggle />

            <Link to="/pricing" className="hidden lg:block">
              <Button 
                size="sm" 
                className="bg-transparent hover:bg-[#F5A623]/10 text-white font-semibold border-2 border-[#F5A623] transition-all duration-200"
                data-testid="nav-premium"
              >
                <Crown className="h-4 w-4 mr-1 text-[#F5A623]" />
                Premium
              </Button>
            </Link>
            
            {/* Hidden on mobile, visible on desktop */}
            <div className="hidden lg:block">
              <LanguageSwitcher />
            </div>
            
            {/* Admin Dropdown - Hidden on mobile */}
            <div className="hidden lg:block relative group">
              <Button variant="ghost" size="sm" className="text-gray-300 hover:text-[#F5A623] hover:bg-white/5" data-testid="admin-link" aria-label="Menu administration">
                <Lock className="h-4 w-4" />
              </Button>
              <div className="absolute top-full right-0 mt-1 min-w-[200px] bg-black/95 backdrop-blur-xl border border-white/10 rounded-md shadow-xl py-1 z-50 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200">
                <Link to="/guide-pro" className="flex items-center gap-3 px-4 py-2 hover:bg-white/5 group/item" data-testid="nav-guide-pro">
                  <RouteIcon className="h-4 w-4 text-[#F5A623]" />
                  <div className="text-sm font-medium text-gray-300 group-hover/item:text-[#F5A623]">Guide Pro</div>
                </Link>
                <Link to="/gestionnaire" className="flex items-center gap-3 px-4 py-2 hover:bg-white/5 group/item" data-testid="nav-gestionnaire">
                  <Users className="h-4 w-4 text-[#F5A623]" />
                  <div className="text-sm font-medium text-gray-300 group-hover/item:text-[#F5A623]">Gestionnaire</div>
                </Link>
                <div className="border-t border-white/10 my-1" />
                <Link to="/admin-premium" className="flex items-center gap-3 px-4 py-2 hover:bg-white/5 group/item">
                  <Crown className="h-4 w-4 text-[#F5A623] group-hover/item:text-[#F5A623]" />
                  <div>
                    <div className="text-sm font-medium text-[#F5A623]">ADMIN v2</div>
                    <div className="text-xs text-gray-500">Gouvernance Centrale</div>
                  </div>
                </Link>
              </div>
            </div>
            
            {/* User Menu - Compact on mobile */}
            <div className="hidden lg:block">
              <UserMenu />
            </div>
            
            {/* Cart Button - Always visible */}
            <Button 
              variant="outline" 
              onClick={onCartOpen} 
              className="relative border-white/20 hover:border-[#F5A623]/50 hover:bg-[#F5A623]/10 transition-all" 
              data-testid="cart-button"
              aria-label={t('nav_cart')}
            >
              <ShoppingCart className="h-5 w-5" />
              {cartCount > 0 && (
                <span className="absolute -top-2 -right-2 bg-[#F5A623] text-black text-xs rounded-full w-5 h-5 flex items-center justify-center font-bold shadow-[0_0_10px_rgba(245,166,35,0.4)]" aria-label={`${cartCount} items`}>
                  {cartCount}
                </span>
              )}
            </Button>
            
            {/* Mobile Menu Button */}
            <button 
              className="lg:hidden p-2 text-gray-300 hover:text-white hover:bg-white/5 rounded-sm transition-colors" 
              onClick={() => setIsOpen(!isOpen)}
              data-testid="mobile-menu-btn"
              aria-label={isOpen ? t('common_close') : t('common_menu')}
              aria-expanded={isOpen}
            >
              {isOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
            </button>
          </div>
        </div>
      </div>
      
      {/* Mobile Navigation */}
      {isOpen && (
        <div className="lg:hidden border-t border-white/10 bg-black/95 backdrop-blur-xl">
          <div className="px-4 py-4 space-y-2">
            <Link to="/" onClick={() => setIsOpen(false)} className="flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-sm hover:bg-white/5 text-gray-300 hover:text-white">
              <Home className="h-4 w-4" /> {t('common_home')}
            </Link>
            {/* MAGASIN mobile — entre Accueil et Tableau de bord (CAM-UI-LOC) */}
            <Link to="/shop" onClick={() => setIsOpen(false)} className="flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-sm hover:bg-white/5 text-[#F5A623]" data-testid="mobile-nav-shop">
              <Store className="h-4 w-4" /> {t('nav_shop')}
            </Link>
            {/* V5.2: T. BORD fusionne dans INTELLIGENCE */}
            {/* TERRITOIRE_ROUTE_RESTORE_Ω (mobile) — Carte TERRITOIRE Ω */}
            <Link to="/territoire" onClick={() => setIsOpen(false)} className="flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-sm hover:bg-white/5 text-[#FF6A00]" data-testid="mobile-nav-territoire">
              <Map className="h-4 w-4" /> Territoire Ω
            </Link>
            <Link to="/mon-territoire-bionic" onClick={() => setIsOpen(false)} className="flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-sm hover:bg-white/5 text-[#F5A623]" data-testid="mobile-nav-analyse-territoire">
              <Crosshair className="h-4 w-4" /> Analyse Territoire
            </Link>
            {/* CARTE-2027-REBUILD-Omega: Carte terrain V7 (mobile) */}
            <Link to="/carte-2027" onClick={() => setIsOpen(false)} className="flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-sm hover:bg-white/5 text-[#10B981]" data-testid="mobile-nav-carte-2027">
              <Map className="h-4 w-4" /> Carte Terrain V7
            </Link>
            {/* CAM-ADMIN-HEADER: Cameras entre Carte et Intelligence */}
            <Link to="/cameras" onClick={() => setIsOpen(false)} className="flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-sm hover:bg-white/5 text-[#F5A623]" data-testid="mobile-nav-cameras">
              <Camera className="h-4 w-4" /> Cameras
            </Link>
            <Link to="/intelligence-v6" onClick={() => setIsOpen(false)} className="flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-sm hover:bg-white/5 text-[#F5A623]" data-testid="mobile-nav-intelligence-v6">
              <Brain className="h-4 w-4" /> Intelligence V6
            </Link>
            <Link to="/permis-chasse" onClick={() => setIsOpen(false)} className="flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-sm hover:bg-white/5 text-[#F5A623]" data-testid="mobile-nav-permis-chasse">
              <Shield className="h-4 w-4" /> Permis & Enregistrement
            </Link>
            {/* GUIDE PRO — Phase E-2 BCE-4X BDRE-FIRST (mobile) */}
            <Link to="/guide-pro" onClick={() => setIsOpen(false)} className="flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-sm hover:bg-white/5 text-[#F5A623]" data-testid="mobile-nav-guide-pro">
              <RouteIcon className="h-4 w-4" /> Guide Pro
            </Link>
            {/* GESTIONNAIRE — Phase F BCE-4X BDRE-FIRST */}
            <Link to="/gestionnaire" onClick={() => setIsOpen(false)} className="flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-sm hover:bg-white/5 text-[#F5A623]" data-testid="mobile-nav-gestionnaire">
              <Users className="h-4 w-4" /> Gestionnaire
            </Link>
            {/* SUPRA v2: Nutrition integree dans ANALYSE TERRITOIRE */}
            {isBusinessOrAdmin && (
              <Link to="/business" onClick={() => setIsOpen(false)} className="flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-sm hover:bg-white/5 text-[#10B981]">
                <Briefcase className="h-4 w-4" /> Business
              </Link>
            )}
            
            {/* Divider */}
            <div className="border-t border-white/10 my-2" />
            
            {/* Admin v2 — lien unique */}
            <Link to="/admin-premium" onClick={() => setIsOpen(false)} className="flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-sm hover:bg-white/5 text-[#F5A623]">
              <Crown className="h-4 w-4" /> ADMIN v2
            </Link>
            
            {/* Language Switcher on mobile */}
            <div className="px-3 py-2">
              <LanguageSwitcher />
            </div>
            
            {/* BCE-4X V8: PARTAGER relocalisé dans sub-header Territoire — Directive ×4850 */}
          </div>
        </div>
      )}
    </header>
  );
};

// Footer Component - Hidden on full-viewport pages
const FULL_VIEWPORT_ROUTES = ['/mon-territoire-bionic', '/territoire', '/mon-territoire', '/analyse-territoire', '/forecast', '/admin-geo', '/admin-premium', '/carte-2027', '/territoire-capture-mode'];

const Footer = () => {
  const location = useLocation();
  const isFullViewportPage = FULL_VIEWPORT_ROUTES.some(route => 
    location.pathname === route || location.pathname.startsWith(route + '/')
  );
  
  if (isFullViewportPage) return null;
  
  return (
    <footer className="bg-black py-8 border-t border-border">
      <div className="max-w-7xl mx-auto px-4 text-center">
        <p className="text-gray-300">© 2024 BIONIC HUNT/Chasse - Chasse BIONIC™</p>
      </div>
    </footer>
  );
};

// HeroSection Component
const HeroSection = () => {
  const { t, brand } = useLanguage();
  return (
    <section className="hero-bg min-h-screen flex flex-col items-center justify-center text-center px-4 pt-24" data-testid="hero-section">
      <h1 className="text-4xl md:text-5xl golden-text font-bold mb-8 max-w-4xl leading-tight">
        {brand.tagline}
      </h1>
      <div className="flex flex-wrap items-center justify-center gap-4 mb-8">
        <Link to="/analytics">
          <Button className="btn-golden text-black font-semibold px-6 py-3 rounded-full flex items-center gap-2">
            <BarChart3 className="h-5 w-5" /> Intelligence
          </Button>
        </Link>
        <ChevronRight className="text-[#f5a623] h-6 w-6 hidden md:block" />
        <Link to="/compare">
          <Button className="btn-golden text-black font-semibold px-6 py-3 rounded-full flex items-center gap-2">
            <GitCompare className="h-5 w-5" /> {t('nav_compare')}
          </Button>
        </Link>
        <ChevronRight className="text-[#f5a623] h-6 w-6 hidden md:block" />
        <Link to="/shop">
          <Button className="btn-golden text-black font-semibold px-6 py-3 rounded-full flex items-center gap-2">
            <ShoppingCart className="h-5 w-5" /> {t('hero_order')}
          </Button>
        </Link>
      </div>
      <div className="max-w-3xl mx-auto space-y-4">
        <p className="text-gray-300">{t('hero_description')}</p>
        <p className="text-[#f5a623] font-medium">{t('hero_highlight')}</p>
        <p className="text-[#f5a623] font-semibold text-xl mt-6">{brand.slogan}</p>
      </div>
    </section>
  );
};

// ProductCard Component
const ProductCard = ({ product, onAddToCart }) => (
  <Card className="product-card bg-card border-border overflow-hidden" data-testid={`product-card-${product.rank}`}>
    <div className="relative">
      <div className="absolute top-3 left-3 z-10">
        <Badge className="rank-badge text-white font-bold px-3 py-1">#{product.rank}</Badge>
      </div>
      {/* PHASE D: Lazy loading for non-LCP images */}
      <img 
        src={product.image_url} 
        alt={product.name} 
        className="w-full aspect-square object-cover" 
        loading="lazy"
        decoding="async"
      />
    </div>
    <CardContent className="p-4">
      <p className="text-[#f5a623] text-sm">{product.brand}</p>
      <h3 className="text-white font-semibold mb-2 truncate">{product.name}</h3>
      <div className="flex items-center gap-2 mb-4">
        <Badge className="bg-[#f5a623] text-black">Score: {product.score}</Badge>
      </div>
      <p className="text-[#f5a623] font-bold text-xl mb-4">${product.price}</p>
      <Button className="w-full btn-golden text-black font-semibold" onClick={() => onAddToCart(product)}>
        <ShoppingCart className="h-4 w-4 mr-2" /> Ajouter
      </Button>
    </CardContent>
  </Card>
);

// ProductsSection Component
const ProductsSection = ({ products, onAddToCart }) => {
  const { t, brand } = useLanguage();
  return (
    <section className="py-16 px-4 bg-background" data-testid="products-section">
      <div className="max-w-7xl mx-auto">
        <h2 className="golden-text text-3xl md:text-4xl font-bold text-center mb-8 italic">
          {t('page_best_choices')} {brand.short}
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-6">
          {products.map((product) => (
            <ProductCard key={product.id} product={product} onAddToCart={onAddToCart} />
          ))}
        </div>
      </div>
    </section>
  );
};

// FeaturesSection Component
const FeaturesSection = () => {
  const { t } = useLanguage();
  const features = [
    { icon: BarChart3, titleKey: "common_intelligence", descKey: "feature_analyze_desc" },
    { icon: GitCompare, titleKey: "nav_compare", descKey: "feature_compare_desc" },
    { icon: ShoppingCart, titleKey: "hero_order", descKey: "feature_order_desc" },
  ];
  return (
    <section className="py-16 px-4 bg-black/50" data-testid="features-section">
      <div className="max-w-5xl mx-auto">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {features.map((feature, index) => (
            <div key={index} className="feature-card rounded-xl p-8 text-center">
              <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-[#f5a623]/20 flex items-center justify-center">
                <feature.icon className="h-8 w-8 text-[#f5a623]" />
              </div>
              <h3 className="text-xl font-semibold text-white mb-2">{t(feature.titleKey)}</h3>
              <p className="text-gray-300">{t(feature.descKey)}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

// CartSheet Component — SUPRA v2 panier saline unifie + P5-OPTIMIZATION V2
// NOTE: CartSheet V1 PRESERVE pour backward compat saline.
// CartPanel V2 utilise dans le render principal.

// HomePage Component
const HomePage = ({ products, onAddToCart }) => (
  <main>
    <HeroSection />
    <ProductsSection products={products} onAddToCart={onAddToCart} />
    <FeaturesSection />
  </main>
);

// AnalyzePage Component
const AnalyzePage = ({ products }) => (
  <main className="min-h-screen bg-background" style={{ paddingTop: '144px' }}>
    <div className="max-w-7xl mx-auto px-4 py-8">
      <h1 className="golden-text text-4xl font-bold mb-4">Analysez</h1>
      <p className="text-gray-300 mb-8">Analysez en profondeur chaque attractant avec nos critères scientifiques.</p>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {products.map((product) => (
          <Card key={product.id} className="bg-card border-border p-6">
            <div className="flex items-start gap-4">
              {/* PHASE D: Lazy loading */}
              <img 
                src={product.image_url} 
                alt={product.name} 
                className="w-24 h-24 object-cover rounded-lg" 
                loading="lazy"
                decoding="async"
              />
              <div className="flex-1">
                <p className="text-[#f5a623] text-sm">{product.brand}</p>
                <h3 className="text-white font-semibold mb-2">{product.name}</h3>
                <Badge className="bg-[#f5a623]">Score: {product.score}</Badge>
              </div>
            </div>
          </Card>
        ))}
      </div>
    </div>
  </main>
);

// BCE-4X PURGE: TerritoryPage SUPPRIME (STEEVE-MAX directive)

// BCE-4X PURGE: MarketplacePage SUPPRIME (HuntMarketplace = fantome)

// FormationsPage Component
const FormationsPage = () => {
  const navigate = useNavigate();
  const { t } = useLanguage();
  
  // Formations FédéCP officielles
  const fedecpFormations = [
    {
      id: "securite",
      title: "Initiation à la chasse avec arme à feu",
      description: "Formation obligatoire pour obtenir le certificat du chasseur au Québec",
      Icon: Crosshair,
      duration: "8 heures (2 jours)",
      type: "Obligatoire",
      price: "Environ 75$",
      link: "https://fedecp.com/la-chasse/japprends/initiation-des-chasseurs/",
      topics: ["Sécurité et manipulation des armes", "Réglementation provinciale", "Éthique de chasse", "Identification du gibier", "Examen théorique et pratique"]
    },
    {
      id: "arc",
      title: "Initiation à la chasse à l'arc",
      description: "Formation pour la chasse à l'arc et à l'arbalète",
      Icon: Target,
      duration: "4 heures",
      type: "Obligatoire pour arc/arbalète",
      price: "Environ 50$",
      link: "https://fedecp.com/la-chasse/japprends/initiation-des-chasseurs/",
      topics: ["Sécurité avec arc et arbalète", "Choix de l'équipement", "Techniques de tir", "Réglementation spécifique"]
    },
    {
      id: "piegeage",
      title: "Formation au piégeage",
      description: "Cours obligatoire pour obtenir le certificat de piégeur",
      Icon: Package,
      duration: "8 heures",
      type: "Obligatoire",
      price: "Environ 60$",
      link: "https://fedecp.com/le-piegeage/formation-au-piegeage/",
      topics: ["Réglementation sur le piégeage", "Types de pièges autorisés", "Éthique et bien-être animal", "Techniques de capture", "Traitement des fourrures"]
    },
    {
      id: "orignal",
      title: "Formation chasse à l'orignal",
      description: "Techniques avancées pour la chasse au roi de nos forêts",
      Icon: Target,
      duration: "4 heures",
      type: "Facultatif",
      price: "Environ 40$",
      link: "https://fedecp.com/la-chasse/orignal/",
      topics: ["Comportement de l'orignal", "Appels et leurres", "Stratégies de chasse", "Débitage et conservation"]
    }
  ];
  
  // Formations BIONIC™ exclusives
  const bionicFormations = [
    {
      id: "analyse-territoire",
      title: "Analyse de territoire BIONIC™",
      description: "Maîtrisez les outils d'analyse GPS et cartographique pour optimiser votre territoire de chasse",
      Icon: Map,
      duration: "Auto-formation",
      type: "Exclusif BIONIC™",
      modules: ["Lecture de cartes topographiques", "Identification des corridors", "Placement stratégique des caches", "Analyse des points d'eau"]
    },
    {
      id: "attractants",
      title: "Science des attractants",
      description: "Comprenez la chimie et la biologie derrière les leurres et attractants",
      Icon: BarChart3,
      duration: "Auto-formation",
      type: "Exclusif BIONIC™",
      modules: ["Composés olfactifs", "Phéromones et comportement", "Timing et application", "13 critères d'évaluation"]
    },
    {
      id: "meteo",
      title: "Météo et mouvement du gibier",
      description: "Apprenez à prédire le comportement du gibier selon les conditions météo",
      Icon: Cloud,
      duration: "Auto-formation",
      type: "Exclusif BIONIC™",
      modules: ["Pression atmosphérique", "Phases lunaires", "Front météo et activité", "Prévisions optimales"]
    }
  ];
  
  // Types de territoires au Québec
  const territoireTypes = [
    {
      type: "Terres publiques",
      description: "Territoires libres gérés par le MFFP",
      color: "#22c55e",
      features: ["Accès gratuit avec permis", "Tirage au sort pour certaines zones", "Règles de capacité de support"]
    },
    {
      type: "ZEC",
      description: "Zones d'exploitation contrôlée",
      color: "#3b82f6",
      features: ["Droit d'accès requis", "Gestion par associations", "Quotas et enregistrement obligatoire"]
    },
    {
      type: "Pourvoiries",
      description: "Territoires privés avec services",
      color: "#f59e0b",
      features: ["Hébergement et guidage", "Droits exclusifs", "Forfaits tout inclus"]
    },
    {
      type: "Réserves fauniques",
      description: "Territoires protégés par la SÉPAQ",
      color: "#8b5cf6",
      features: ["Réservation obligatoire", "Secteurs contingentés", "Haute qualité de chasse"]
    },
    {
      type: "Terres privées",
      description: "Propriétés privées avec permission",
      color: "#ef4444",
      features: ["Autorisation du propriétaire", "Ententes de chasse", "Location possible"]
    }
  ];

  return (
    <main className="min-h-screen bg-background pb-16" style={{ paddingTop: '144px' }}>
      <div className="max-w-7xl mx-auto px-4">
        {/* Back Button */}
        <Button 
          variant="ghost" 
          onClick={() => navigate('/')}
          className="mb-4 text-gray-300 hover:text-white hover:bg-gray-800/50"
          data-testid="back-button-formations"
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          Retour à l'accueil
        </Button>
        
        {/* Header */}
        <div className="flex items-center gap-4 mb-8">
          <div>
            <h1 className="text-3xl font-bold text-white flex items-center gap-3">
              <GraduationCap className="h-8 w-8 text-[#f5a623]" />
              Centre de Formations
            </h1>
            <p className="text-gray-300">FédéCP & BIONIC™ - Devenez un chasseur expert</p>
          </div>
        </div>

        {/* FédéCP Section */}
        <section className="mb-12">
          <div className="flex items-center gap-3 mb-6">
            <div className="p-2 bg-blue-500/20 rounded-lg">
              <BookOpen className="h-6 w-6 text-blue-400" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-white">Formations FédéCP officielles</h2>
              <p className="text-gray-300 text-sm">Fédération québécoise des chasseurs et pêcheurs</p>
            </div>
            <a 
              href="https://fedecp.com" 
              target="_blank" 
              rel="noopener noreferrer"
              className="ml-auto"
            >
              <Badge className="bg-blue-500/20 text-blue-400 hover:bg-blue-500/30 cursor-pointer">
                <ExternalLink className="h-3 w-3 mr-1" /> fedecp.com
              </Badge>
            </a>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {fedecpFormations.map((formation) => (
              <Card key={formation.id} className="bg-card border-border hover:border-blue-500/50 transition-all">
                <CardHeader className="pb-2">
                  <div className="flex items-start justify-between">
                    <formation.Icon className="h-8 w-8 text-blue-400" />
                    <Badge className={formation.type === 'Obligatoire' || formation.type.includes('Obligatoire') ? 'bg-red-500/20 text-red-400' : 'bg-gray-500/20 text-gray-300'}>
                      {formation.type}
                    </Badge>
                  </div>
                  <CardTitle className="text-white text-lg">{formation.title}</CardTitle>
                  <CardDescription className="text-xs">{formation.description}</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center gap-2 text-xs text-gray-300 mb-2">
                    <Clock className="h-3 w-3" />
                    <span>{formation.duration}</span>
                  </div>
                  <div className="flex items-center gap-2 text-xs text-gray-300 mb-3">
                    <DollarSign className="h-3 w-3" />
                    <span>{formation.price}</span>
                  </div>
                  <ul className="space-y-1 mb-4">
                    {formation.topics.slice(0, 3).map((topic, idx) => (
                      <li key={idx} className="text-xs text-gray-300 flex items-center gap-1">
                        <CheckCircle className="h-3 w-3 text-green-500" />
                        {topic}
                      </li>
                    ))}
                    {formation.topics.length > 3 && (
                      <li className="text-xs text-gray-500">+{formation.topics.length - 3} autres...</li>
                    )}
                  </ul>
                  <a href={formation.link} target="_blank" rel="noopener noreferrer">
                    <Button size="sm" className="w-full bg-blue-600 hover:bg-blue-700">
                      <ExternalLink className="h-3 w-3 mr-1" /> S'inscrire
                    </Button>
                  </a>
                </CardContent>
              </Card>
            ))}
          </div>
        </section>

        {/* BIONIC Section */}
        <section className="mb-12">
          <div className="flex items-center gap-3 mb-6">
            <div className="p-2 bg-[#f5a623]/20 rounded-lg">
              <Brain className="h-6 w-6 text-[#f5a623]" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-white">Formations BIONIC™</h2>
              <p className="text-gray-300 text-sm">Maîtrisez les outils d'analyse de territoire</p>
            </div>
            <Badge className="ml-auto bg-[#f5a623]/20 text-[#f5a623]">Exclusif</Badge>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {bionicFormations.map((formation) => (
              <Card key={formation.id} className="bg-card border-border hover:border-[#f5a623]/50 transition-all">
                <CardHeader className="pb-2">
                  <div className="flex items-start justify-between">
                    <formation.Icon className="h-8 w-8 text-[#f5a623]" />
                    <Badge className="bg-[#f5a623]/20 text-[#f5a623]">{formation.type}</Badge>
                  </div>
                  <CardTitle className="text-white text-lg">{formation.title}</CardTitle>
                  <CardDescription className="text-xs">{formation.description}</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center gap-2 text-xs text-gray-300 mb-3">
                    <Clock className="h-3 w-3" />
                    <span>{formation.duration}</span>
                  </div>
                  <ul className="space-y-1 mb-4">
                    {formation.modules.map((module, idx) => (
                      <li key={idx} className="text-xs text-gray-300 flex items-center gap-1">
                        <CheckCircle className="h-3 w-3 text-[#f5a623]" />
                        {module}
                      </li>
                    ))}
                  </ul>
                  <Button size="sm" className="w-full btn-golden text-black">
                    Commencer
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>
        </section>

        {/* Territoire Types Section */}
        <section>
          <div className="flex items-center gap-3 mb-6">
            <div className="p-2 bg-green-500/20 rounded-lg">
              <Map className="h-6 w-6 text-green-400" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-white">Types de Territoires au Québec</h2>
              <p className="text-gray-300 text-sm">Connaissez les différentes zones de chasse</p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
            {territoireTypes.map((territoire) => (
              <Card key={territoire.type} className="bg-card border-border" style={{ borderLeftColor: territoire.color, borderLeftWidth: '4px' }}>
                <CardHeader className="pb-2">
                  <CardTitle className="text-lg" style={{ color: territoire.color }}>{territoire.type}</CardTitle>
                  <CardDescription className="text-xs">{territoire.description}</CardDescription>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-1">
                    {territoire.features.map((feature, idx) => (
                      <li key={idx} className="text-xs text-gray-300 flex items-center gap-1">
                        <CheckCircle className="h-3 w-3" style={{ color: territoire.color }} />
                        {feature}
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>
            ))}
          </div>
        </section>
      </div>
    </main>
  );
};

// VIS-E: Notification toggle component (self-contained with state)
const VisionNotificationsToggle = () => {
  const [showPanel, setShowPanel] = useState(false);
  const { token } = useAuth();
  return (
    <div className="hidden lg:block relative">
      <Button variant="ghost" size="sm" className="text-gray-300 hover:text-amber-400 hover:bg-white/5" onClick={() => setShowPanel(p => !p)} data-testid="vision-alerts-toggle">
        <Bell className="h-4 w-4" />
      </Button>
      <VisionNotificationsPanel token={token} isOpen={showPanel} onClose={() => setShowPanel(false)} />
    </div>
  );
};


// Phase XI-SUPRA-D : Navigation conditionnelle — masquée sur la route /territoire-capture-mode
// pour garantir un viewport 1920×1080 100% carte institutionnelle.
const CaptureModeAwareChrome = ({ cartCount, onCartOpen }) => {
  const location = useLocation();
  if (location.pathname.startsWith('/territoire-capture-mode')) return null;
  return <Navigation cartCount={cartCount} onCartOpen={onCartOpen} />;
};

// Main App Component
function App() {
  const [products, setProducts] = useState([]);
  const [cartItems, setCartItems] = useState([]);
  const [isCartOpen, setIsCartOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [cartCount, setCartCount] = useState(0);
  const sessionId = getSessionId();

  // SUPRA v2: Panier unifie — API saline unique
  const fetchProducts = useCallback(async () => {
    try {
      const response = await axios.get(`${API}/v1/saline/shop/products`);
      setProducts(response.data.products || []);
    } catch (error) {
      console.error("Error fetching products:", error);
    }
  }, []);

  const fetchCart = useCallback(async () => {
    try {
      const res = await axios.get(`${API}/v1/saline/shop/cart/${sessionId}`);
      setCartItems(res.data.items || []);
    } catch (error) {
      console.error("Cart fetch error:", error);
    }
  }, [sessionId]);

  // P5-OPTIMIZATION V2: Fetch cart count from V2 API
  const fetchCartV2Count = useCallback(async () => {
    try {
      const userId = CartService.getUserId();
      const summary = await CartService.getSummaryV2(userId);
      setCartCount(summary.item_count || 0);
    } catch {
      // fallback to saline cart count
    }
  }, []);

  const handleAddToCart = async (product) => {
    try {
      // V1: Saline cart
      await axios.post(`${API}/v1/saline/shop/cart/add`, {
        session_id: sessionId,
        product_id: product.id,
        quantity: 1
      });
      await fetchCart();

      // V2: Also add to Cart V2 for unified experience
      const userId = CartService.getUserId();
      await CartService.addItemV2(userId, {
        product_type: 'package',
        product_id: product.id,
        name: product.name,
        unit_price: product.price || 0,
        quantity: 1,
        description: product.brand || ''
      });
      await fetchCartV2Count();

      toast.success("Produit ajoute au panier!");
    } catch (error) {
      console.error("Cart error:", error);
      toast.error("Erreur lors de l'ajout au panier");
    }
  };

  const handleRemoveItem = async (itemId) => {
    toast.info("Produit note pour suppression");
  };

  const handleUpdateQuantity = async (itemId, quantity) => {
    await fetchCart();
  };

  const handleCheckout = async () => {
    try {
      const res = await axios.post(`${API}/v1/saline/shop/checkout`, {
        session_id: sessionId,
        user_id: 'guest',
        origin_url: window.location.origin,
      });
      if (res.data.url) window.location.href = res.data.url;
    } catch (error) {
      console.error("Checkout error:", error);
      toast.error("Erreur lors du checkout");
    }
  };

  // P5-OPTIMIZATION V2: Cart update callback
  const handleCartUpdate = useCallback((count) => {
    setCartCount(count);
  }, []);

  useEffect(() => {
    fetchProducts();
    fetchCart();
    fetchCartV2Count();
  }, [fetchProducts, fetchCart, fetchCartV2Count]);

  // PHASE_X200_P4_RUNTIME_BEACON_Ω — démarrage idempotent du beacon institutionnel
  // Émet POST /api/omega/ci-status/runtime-beacon toutes les 15 s avec payload conforme
  // (waypoint officiel, panels_clickable_count>=4, corridors_x150_conforme, etc.)
  useEffect(() => {
    const stop = startRuntimeBeaconOmega();
    return () => { try { stop && stop(); } catch (_e) { /* no-op */ } };
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-[#f5a623]" />
      </div>
    );
  }

  return (
    <LanguageProvider>
      <AuthProvider>
        <NotificationProvider 
          coordinates={{ lat: 46.8139, lng: -71.2080 }}
          enabled={true}
          warningMinutes={15}
        >
        <div className="App min-h-screen bg-background">
          <BrowserRouter>
            <SEOHead />
            {/* Logo BIONIC Global - Visible sur toutes les pages (desktop) */}
            <BionicLogoGlobal />
            <CaptureModeAwareChrome cartCount={cartCount} onCartOpen={() => setIsCartOpen(true)} />
            {/* P5-OPTIMIZATION V2: CartPanel remplace CartSheet */}
            <CartPanel
              isOpen={isCartOpen}
              onOpenChange={setIsCartOpen}
              onCartUpdate={handleCartUpdate}
            />
            {/* BLOC 2 OPTIMIZATION: Suspense wrapper for lazy-loaded routes */}
            <Suspense fallback={<LazyLoadFallback />}>
              <Routes>
                <Route path="/" element={<HomePage products={products} onAddToCart={handleAddToCart} />} />
                <Route path="/onboarding" element={<OnboardingPage />} />
                <Route path="/analyze" element={<Navigate to="/analytics" replace />} />
                <Route path="/compare" element={<ComparePage products={products} />} />
                <Route path="/shop" element={<ShopPage />} />
                {/* TERRITOIRE_ROUTE_RESTORE_Ω (2026-05-11 · STEEVE-MAX VERSION_ULTIME_ABSOLUE_X11) */}
                {/* /territoire → Carte TERRITOIRE Ω (corridors Ω, zones Ω, contamination Ω, vent Ω) */}
                {/* /mon-territoire-bionic → Analyse Territoire BIONIC (SENSORIEL Ω) */}
                <Route path="/territoire" element={<MonTerritoireBionicPage pageMode="carte-territoire" />} />
                <Route path="/mon-territoire-bionic" element={<MonTerritoireBionicPage pageMode="analyse-bionic" />} />
                {/* Redirections pour URL simplifiee */}
                <Route path="/mon-territoire" element={<MonTerritoireBionicPage pageMode="analyse-bionic" />} />
                <Route path="/analyse-territoire" element={<MonTerritoireBionicPage pageMode="analyse-bionic" />} />
                {/* BCE-4X PURGE: /marketplace redirige (MarketplacePage = fantome) */}
                <Route path="/marketplace" element={<Navigate to="/shop" replace />} />
                <Route path="/formations" element={<FormationsPage />} />
                {/* Module Permis de chasse */}
                <Route path="/permis-chasse" element={<HuntingLicensePage />} />
                {/* V5.2: Dashboard fusionne dans Intelligence */}
                <Route path="/dashboard" element={<Navigate to="/intelligence-v6" replace />} />
                <Route path="/business" element={<BusinessPage />} />
                <Route path="/plan-maitre" element={<PlanMaitrePage />} />
                {/* V5-ULTIME: Analytics réactivé */}
                <Route path="/analytics" element={<AnalyticsPage />} />
                {/* CARTE-RETRAIT-Omega: /map redirige vers territoire */}
                <Route path="/map" element={<Navigate to="/mon-territoire-bionic" replace />} />
                {/* PHASE-E PRÉ-FUSION : HUD TERRITOIRE ULTIME (page démo institutionnelle) */}
                <Route path="/territoire/hud-ultime-phase-e" element={<HudUltimeDemoPage />} />
                {/* CARTE-2027-REBUILD: Nouvelle carte terrain V7 */}
                <Route path="/carte-2027" element={<Carte2027Page />} />
                <Route path="/forecast" element={<ForecastPage />} />
                <Route path="/trips" element={<TripsPage />} />
                {/* PHASE XX (Ordre n°40) — WIDGET institutionnel TERRITOIRE_APTE_Ω */}
                <Route path="/territoire-apte" element={<WidgetTerritoireApteOmega />} />
                <Route path="/referral" element={<ReferralModule />} />
                {/* ADMIN v2: Interface unique — AdminPremiumPage absorbe AdminPage */}
                <Route path="/admin" element={<Navigate to="/admin-premium" replace />} />
                <Route path="/admin/geo" element={<AdminGeoPage />} />
                {/* V7.2: /admin/hotspots SUPPRIME — Admin Premium = source de verite (x7200) */}
                <Route path="/admin/hotspots" element={<Navigate to="/admin-premium" replace />} />
                <Route path="/networking" element={<NetworkingHub />} />
                <Route path="/lands" element={<LandsRental />} />
                <Route path="/reset-password" element={<ResetPasswordPage />} />
                <Route path="/become-partner" element={<BecomePartner />} />
                <Route path="/partner/dashboard" element={<PartnerDashboard />} />
                <Route path="/auth/google/callback" element={<GoogleOAuthCallback />} />
                {/* V5-ULTIME P3: Routes Monétisation */}
                <Route path="/pricing" element={<PricingPage />} />
                <Route path="/payment/success" element={<PaymentSuccessPage />} />
                <Route path="/payment/cancel" element={<PaymentCancelPage />} />
                {/* V5-ULTIME: Administration Premium */}
                <Route path="/admin-premium" element={<AdminPremiumPage />} />
                {/* Marketing Calendar V2 */}
                <Route path="/marketing-calendar" element={<MarketingCalendarPage />} />
                {/* BIONIC V6 Demo Page */}
                <Route path="/bionic-demo" element={<BionicAnalysisDemoPage />} />
                {/* V6 GOLDEN: Interface d'observations terrain */}
                <Route path="/observations" element={<FieldObservationForm />} />
                {/* CALIBRATION MASTER: Dashboard de calibration */}
                <Route path="/calibration" element={<CalibrationDashboard />} />
                <Route path="/reports" element={<ReportsPage />} />
                <Route path="/comparaison-especes" element={<SpeciesComparisonPage />} />
                {/* SUPRA v2: Nutrition Intelligence redirige vers ANALYSE TERRITOIRE (moteur unifie SUPRA LOCAL) */}
                <Route path="/saline" element={<Navigate to="/mon-territoire-bionic" replace />} />
                <Route path="/saline-intelligence" element={<Navigate to="/mon-territoire-bionic" replace />} />
                <Route path="/nutrition-intelligence" element={<Navigate to="/mon-territoire-bionic" replace />} />
                {/* SUPRA: Redirection vers ANALYSE TERRITOIRE (moteur unique SUPRA LOCAL) */}
                <Route path="/nutrition-supra" element={<Navigate to="/mon-territoire-bionic" replace />} />
                <Route path="/product/:productId" element={<ProductPage />} />
                <Route path="/supra/:id" element={<SupraPage />} />
                {/* BIONIC MODULES — 10 modules predictifs (STEEVE-MAX x2000) */}
                <Route path="/bionic-modules" element={<BionicModulesPage />} />
                <Route path="/intelligence" element={<BionicModulesPage />} />
                <Route path="/ecological-intelligence" element={<BionicModulesPage />} />
                {/* V6-M3-DASHBOARD: Intelligence V6 (x7000-M3-DASHBOARD) */}
                <Route path="/intelligence-v6" element={<IntelligenceV6Page />} />
                {/* BSAA — BIONIC Social Ads Automation (x4500-ULTRA) */}
                <Route path="/bsaa" element={<BsaaDashboardPage />} />
                <Route path="/ads" element={<BsaaDashboardPage />} />
                {/* GUIDE PRO — Phase E-2 BCE-4X BDRE-FIRST */}
                <Route path="/guide-pro" element={<GuideProPage />} />
                {/* GESTIONNAIRE — Phase F BCE-4X BDRE-FIRST · ORDRE N°47 sécurisé */}
                <Route
                  path="/gestionnaire"
                  element={
                    <GestionnaireAuthGuard>
                      <GestionnairePage />
                    </GestionnaireAuthGuard>
                  }
                />
                <Route path="/cameras" element={<CameraModule />} />
                {/* Phase XI-SUPRA-D : Route stable pour captures Playwright institutionnelles.
                    StrictMode désactivé via index.js quand pathname.startsWith('/territoire-capture-mode').
                    Aucun AuthGuard niveau route. MonTerritoireBionicPage rendu sans remount. */}
                <Route path="/territoire-capture-mode" element={<TerritoireCaptureModePage />} />
                {/* P21 · ADMIN_PREMIUM_FRONTEND_INTEGRATION_Ω · BCE-4X ULTIME ABSOLU */}
                <Route path="/admin/bce-4x-premium" element={<AdminPremiumLayout />}>
                  <Route index element={<AdminPremiumIndexPage />} />
                  <Route path="visualizer" element={<Visualizer18Page />} />
                  <Route path="territoire" element={<TerritoireReportPage />} />
                  <Route path="waypoint" element={<WaypointGuidePage />} />
                  <Route path="manual" element={<LayerManualPage />} />
                  <Route path="merkle" element={<MerkleAuditPage />} />
                  <Route path="validation" element={<ValidationsPage />} />
                </Route>
              </Routes>
            </Suspense>
            <Footer />
            <ScrollNavigator />
            <Toaster position="bottom-right" richColors />
            <CookieConsent />
            <OfflineIndicator />
            {/* V6 GOLDEN: Centre de notifications push temps réel */}
            <AlertNotificationCenter position="bottom-right" />
            {/* P22C · TERRITOIRE FRONTEND DEBUG OVERLAY (URL flag ?territoireDebug=on) */}
            <TerritoireFrontendDebugOverlay />
            {/* P22D · CORRIDORS DEBUG OVERLAY (URL flag ?corridorsDebug=on) */}
            <CorridorsDebugOverlay />
            {/* P22Λ · LOCAL CORRIDOR LENS PANEL (URL flag ?lensDebug=on) */}
            <LocalCorridorLensPanel />
            {/* P22Σ_V3 · FUSION VEINEUSE DIAGNOSTIC PANEL (URL flag ?fusionDebug=on) */}
            <FusionDebugPanel />
          </BrowserRouter>
        </div>
        </NotificationProvider>
      </AuthProvider>
    </LanguageProvider>
  );
}

export default App;
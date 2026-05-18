/**
 * TerritoireToolbar — V20 BOUTONS PRESSEURS INSTITUTIONNELS
 * ===========================================================
 * PHASE-FRONTEND-Omega: ZERO menu deroulant. ZERO fenetre flottante.
 * Chaque bouton = ON/OFF = une couche reelle TERRITOIRE-Omega.
 *
 * BOUTONS: SPLIT | CARTE | ESPECE | WAYPOINTS | LIEUX |
 *          INTELLIGENCE | ZONES | CORRIDORS | AFFUTS |
 *          SALINES | HOTSPOTS | VENT | CONTAMINATION |
 *          CURSEUR | SCORE
 *
 * ON  = enfonce + halo lumineux
 * OFF = releve + neutre
 */
import React from 'react';
import {
  Target, MapPin, Plus,
  Map, Binoculars, Layers, Brain,
  Shield, SplitSquareHorizontal,
  Wind, Crosshair, Flame, Droplets, Eye, Navigation, BookMarked,
  Microscope, Box,
} from 'lucide-react';
import { Popover, PopoverTrigger, PopoverContent } from '@/components/ui/popover';
import BionicMapSelector from '@/components/maps/BionicMapSelector';
import { BionicScoreBadge } from '@/components/territoire/BionicScoreBadge';
import { SPECIES_LIST } from '@/core/bionic/speciesConfig';

// P20_PHASE3 · Badge migration unified panel (doctrinal)
// P20_PHASE4 · `enforce_badge_omega_18` ENABLED · sync avec state actif réel
function UnifiedPanelBadge({ activeCount = 0, totalCount = 18 }) {
  return (
    <div
      data-testid="toolbar-unified-panel-badge"
      title={`Panneau Ω 18 couches PRIMARY_ONLY · ${activeCount}/${totalCount} actives`}
      style={{
        display: 'inline-flex', alignItems: 'center', gap: 4,
        padding: '0 10px', height: 28, borderRadius: 4,
        fontSize: 9, fontWeight: 800, letterSpacing: 1,
        flexShrink: 0,
        fontFamily: 'JetBrains Mono, monospace',
        background: 'rgba(212,160,23,0.25)',
        border: '1px solid #D4A017',
        color: '#D4A017',
      }}
    >
      <Layers size={11} />
      Ω · {activeCount}/{totalCount}
    </div>
  );
}

// ═══ BOUTON PRESSEUR UNIVERSEL ═══
function PressButton({ active, onClick, icon: Icon, label, color = '#9E9E9E', activeColor, testId, title }) {
  // ENGINE UX-Omega-V12: PressButton delegue a BionicButtonOmega
  // (retro-eclairage complet actif/inactif institutionnel).
  // Signature preservee pour compat.
  const state = active ? 'active' : 'inactive';
  return (
    <button
      onClick={onClick}
      data-testid={testId}
      title={title || label}
      className={active ? 'btn-omega-active' : 'btn-omega-inactive'}
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        justifyContent: 'center',
        gap: 6,
        padding: '0 10px',
        height: 32,
        minWidth: 36,
        borderRadius: 6,
        fontSize: 10,
        fontWeight: 800,
        letterSpacing: '0.5px',
        textTransform: 'uppercase',
        cursor: 'pointer',
        flexShrink: 0,
        fontFamily: 'ui-monospace, SFMono-Regular, Menlo, monospace',
        transition: 'background 0.18s ease, border-color 0.18s ease, box-shadow 0.18s ease, transform 0.08s ease',
        ...(active
          ? {
              // UX-Omega-V12-R5: ORANGE palette reduite
              background: 'rgba(255, 152, 0, 0.4)',
              color: '#FFFFFF',
              border: '2px solid #FFFFFF',
              boxShadow: '0 0 4px #FF9800',
              transform: 'scale(0.96)',
              textShadow: '0 0 4px rgba(0,0,0,0.4)',
            }
          : {
              background: '#2A2A2A',
              color: '#BDBDBD',
              border: '1px solid #444444',
              boxShadow: 'none',
            }),
      }}
      data-ux-state={state}
    >
      {Icon && <Icon className="h-3.5 w-3.5" />}
      <span className="hidden sm:inline">{label}</span>
    </button>
  );
}

const SEP = <div className="w-px h-5 bg-gray-700/50 mx-0.5 flex-shrink-0" />;

export function TerritoireToolbar({
  activeTab, setActiveTab, splitViewEnabled, toggleSplitView,
  selectedSpecies, setSelectedSpecies,
  mapType, mapOptions, setMapOptions, cartePopoverOpen, setCartePopoverOpen, handleMapTypeChangeAndClose,
  showZonesLayer, setShowZonesLayer, showCorridorsLayer, setShowCorridorsLayer,
  showPointsLayer, setShowPointsLayer,
  showWindFlow, setShowWindFlow,
  showHeatmapV10, setShowHeatmapV10,
  showCursorBionic, setShowCursorBionic,
  adminArchitecteMode, setAdminArchitecteMode, privacyMode, setPrivacyMode,
  activeWaypoints, savedPlaces,
  selectedWaypointForZones,
  showIntelLayer, setShowIntelLayer,
  showInspectionBioPanel, setShowInspectionBioPanel,
  showPhaseA, setShowPhaseA,
  showPhaseC, setShowPhaseC,
  // P22ΩΩ_CLEANUP_3D_MVT_EDGE · 2026-05-18 · STEEVE-MAX
  // Props show3DViewer/setShow3DViewer SUPPRIMÉES — Cesium 3D retiré.
  // Legacy props accepted but ignored
  ...rest
}) {
  // P20_PHASE4 · sync_toolbar_with_unified_panel · count actif anti-générique
  const unifiedActiveCount = [
    showZonesLayer, showCorridorsLayer, showPointsLayer,
    showPhaseA, showHeatmapV10, showWindFlow, showPhaseC,
    showCursorBionic, showInspectionBioPanel, showIntelLayer,
  ].filter(Boolean).length;

  // Species cycle
  const speciesIdx = SPECIES_LIST.findIndex(s => s.id === selectedSpecies);
  const cycleSpecies = () => {
    const next = (speciesIdx + 1) % SPECIES_LIST.length;
    setSelectedSpecies(SPECIES_LIST[next].id);
  };
  const currentSpecies = SPECIES_LIST[speciesIdx] || SPECIES_LIST[0];

  return (
    <nav className="flex-shrink-0 h-[44px] bg-[#0d0d14] border-b border-[#1a1a2e] px-3 flex items-center relative z-40 overflow-hidden" data-testid="bionic-tabs">
      <div className="flex items-center gap-0.5 bg-black/60 backdrop-blur-sm rounded-lg border border-gray-700/40 p-0.5 flex-nowrap overflow-x-auto overflow-y-hidden scrollbar-none" style={{ flexWrap: 'nowrap', scrollbarWidth: 'none', msOverflowStyle: 'none', WebkitOverflowScrolling: 'touch' }}>

        {/* P20_PHASE4 · BADGE PANEL UNIFIÉ Ω · count dynamique synchro */}
        <UnifiedPanelBadge activeCount={unifiedActiveCount} totalCount={18} />
        {/* P22B · raccourci direct Admin Premium · territoire */}
        <a
          href="/admin/bce-4x-premium/territoire"
          target="_blank"
          rel="noopener noreferrer"
          data-testid="toolbar-admin-premium-link"
          title="Admin Premium · Rapports Ω P15"
          style={{
            display: 'inline-flex', alignItems: 'center', gap: 4,
            padding: '0 10px', height: 28, borderRadius: 4,
            fontSize: 9, fontWeight: 800, letterSpacing: 1,
            cursor: 'pointer', flexShrink: 0,
            fontFamily: 'JetBrains Mono, monospace',
            background: 'rgba(124,181,24,0.18)',
            border: '1px solid rgba(124,181,24,0.5)',
            color: '#7CB518',
            textDecoration: 'none',
            marginLeft: 4,
          }}
        >
          ADMIN P15→
        </a>
        {SEP}

        {/* SPLIT */}
        <PressButton active={splitViewEnabled} onClick={toggleSplitView} icon={SplitSquareHorizontal} label="Split" activeColor="#3CB371" testId="split-view-toggle" />
        {SEP}

        {/* CARTE — seul popover autorise (selecteur de fond) */}
        <Popover open={cartePopoverOpen} onOpenChange={setCartePopoverOpen}>
          <PopoverTrigger asChild>
            <button className="h-8 px-2 flex items-center gap-1.5 rounded-md text-[10px] font-bold uppercase tracking-wider text-[#f5a623] hover:bg-white/5 transition-all flex-shrink-0" data-testid="toolbar-carte-btn" title="Fond de carte">
              <Map className="h-3.5 w-3.5" /><span className="hidden sm:inline">Carte</span>
            </button>
          </PopoverTrigger>
          <PopoverContent align="start" sideOffset={8} className="w-80 bg-gray-950/95 backdrop-blur-md border-gray-700/60 p-3 shadow-xl shadow-black/40">
            <BionicMapSelector currentMapType={mapType} onMapTypeChange={handleMapTypeChangeAndClose} mapOptions={mapOptions} onOptionsChange={setMapOptions} variant="panel" showOptions={true} />
          </PopoverContent>
        </Popover>
        {SEP}

        {/* ESPECE — bouton presseur cyclique */}
        <button
          onClick={cycleSpecies}
          className="h-8 px-2 flex items-center gap-1.5 rounded-md text-[10px] font-bold uppercase tracking-wider transition-all flex-shrink-0 hover:bg-white/5"
          style={{ color: currentSpecies.color }}
          data-testid="toolbar-species-btn"
          title={`Espece: ${currentSpecies.name} (cliquer pour changer)`}
        >
          <Target className="h-3.5 w-3.5" />
          <span className="hidden sm:inline">{currentSpecies.name}</span>
          <span className="w-2 h-2 rounded-full flex-shrink-0" style={{ backgroundColor: currentSpecies.color }} />
        </button>
        {SEP}

        {/* WAYPOINTS — bouton presseur */}
        <PressButton
          active={activeTab === 'waypoints'}
          onClick={() => setActiveTab(p => p === 'waypoints' ? 'carte' : 'waypoints')}
          icon={MapPin} label="Waypoints" activeColor="#FF9800" testId="toolbar-waypoints-btn"
        />

        {/* LIEUX — bouton presseur */}
        <PressButton
          active={activeTab === 'lieux'}
          onClick={() => setActiveTab(p => p === 'lieux' ? 'carte' : 'lieux')}
          icon={BookMarked} label="Lieux" activeColor="#3b82f6" testId="toolbar-lieux-btn"
        />
        {SEP}

        {/* INTELLIGENCE — couche master institutionnelle (ON = rendu V20 complet, OFF = carte nue) */}
        <PressButton
          active={!!showIntelLayer}
          onClick={() => setShowIntelLayer && setShowIntelLayer(v => !v)}
          icon={Brain} label="Intel" activeColor="#4A7A2E" testId="toolbar-intelligence-btn"
          title="Couche INTEL-Omega master (ON/OFF)"
        />
        {SEP}

        {/* ═══ COUCHES TERRITOIRE-Omega — BOUTONS PRESSEURS ═══ */}

        {/* ZONES */}
        <PressButton active={showZonesLayer} onClick={() => setShowZonesLayer(v => !v)} icon={Layers} label="Zones" activeColor="#2E7D32" testId="toggle-zones-layer" />

        {/* CORRIDORS */}
        <PressButton active={showCorridorsLayer} onClick={() => setShowCorridorsLayer(v => !v)} icon={Navigation} label="Corridors" activeColor="#FF9800" testId="toggle-corridors-layer" />

        {/* AFFUTS */}
        <PressButton active={showPointsLayer} onClick={() => setShowPointsLayer(v => !v)} icon={Crosshair} label="Affuts" activeColor="#9E9E9E" testId="toggle-points-layer" />

        {/* SALINES */}
        <PressButton active={showPhaseA} onClick={() => setShowPhaseA && setShowPhaseA(p => !p)} icon={Droplets} label="Salines" activeColor="#FDD835" testId="toolbar-salines-btn" />

        {/* HOTSPOTS */}
        <PressButton active={showHeatmapV10} onClick={() => setShowHeatmapV10(v => !v)} icon={Flame} label="Hotspots" activeColor="#E53935" testId="toolbar-hotspots-btn" />

        {/* VENT */}
        <PressButton active={showWindFlow} onClick={() => setShowWindFlow(v => !v)} icon={Wind} label="Vent" activeColor="#90CAF9" testId="toggle-wind-flow" />

        {/* CONTAMINATION (via Moteurs PhaseC) */}
        <PressButton active={showPhaseC} onClick={() => setShowPhaseC && setShowPhaseC(p => !p)} icon={Eye} label="Contam" activeColor="#FF7043" testId="toolbar-contam-btn" />
        {SEP}

        {/* P22ΩΩ_CLEANUP_3D_MVT_EDGE · 2026-05-18 · COMMANDANT STEEVE-MAX
         *  Bouton "3D" SUPPRIMÉ — CesiumTerritoireViewer retiré (doctrine 1-worker).
         */}

        {/* CURSEUR BIONIC */}
        <PressButton active={showCursorBionic} onClick={() => setShowCursorBionic(v => !v)} icon={Binoculars} label="Curseur" activeColor="#4A7A2E" testId="toggle-curseur-bionic" />

        {/* INSPECTION BIOLOGIQUE PRO/EXPERT — panneau dédié */}
        <PressButton
          active={!!showInspectionBioPanel}
          onClick={() => setShowInspectionBioPanel && setShowInspectionBioPanel(v => !v)}
          icon={Microscope} label="Inspec" activeColor="#FF8F00" testId="toolbar-inspection-bio-btn"
          title="Mode inspection biologique PRO/EXPERT"
        />

        {/* SCORE BADGE */}
        {SEP}
        <BionicScoreBadge center={selectedWaypointForZones ? { lat: selectedWaypointForZones.lat || selectedWaypointForZones.latitude, lng: selectedWaypointForZones.lng || selectedWaypointForZones.longitude } : null} species={selectedSpecies} month={new Date().getMonth() + 1} compact />

        {/* ADMIN — seul bouton admin (pas un toggle couche) */}
        {SEP}
        <button className={`h-7 w-7 flex items-center justify-center rounded transition-all flex-shrink-0 ${adminArchitecteMode ? 'bg-purple-500/20 text-purple-400' : 'text-gray-700 hover:text-gray-500'}`} data-testid="admin-architecte-btn" onClick={() => {
          if (adminArchitecteMode) { setAdminArchitecteMode(false); } else { const pwd = window.prompt('Mot de passe administrateur:'); if (pwd === 'Saturn5858*') setAdminArchitecteMode(true); }
        }}>
          <Shield className="h-3 w-3" />
        </button>
      </div>
    </nav>
  );
}

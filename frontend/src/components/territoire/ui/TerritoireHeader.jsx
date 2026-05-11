/**
 * TerritoireHeader.jsx — Header BIONIC V8 NATIONAL
 * ==================================================
 * BCE-4X V8-INTEGRATION-Omega — PHASE 1
 * - ScoreV8Badge integre (10 composantes nationales)
 * - ZERO relique V6/V7 scoring
 * - Source UNIQUE meteo (sharedWeather prop)
 * - Purge complete V1-V7 scoring
 */
import React, { useRef, useEffect } from 'react';
import { ArrowLeft, Plus, Edit2, Crosshair, X, LocateFixed, Trash2, ToggleLeft } from 'lucide-react';
import { ShareBionicButton } from '@/components/territoire/ui/ShareBionicButton';
import { ScoreV8Badge } from '@/components/territoire/ScoreV8Badge';
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger, DropdownMenuSeparator } from '@/components/ui/dropdown-menu';
import { getProtectedZIndex } from '@/components/territoire/map/BCE4X_UIShield';

export const TerritoireHeader = ({
  navigate,
  selectedWaypointForZones,
  mapClickMode,
  setMapClickMode,
  setShowAddWaypointDialog,
  onClearWaypoint,
  onDeleteWaypoint,
  onCenterWaypoint,
  // BCE-4X V6+: Source UNIQUE météo depuis sharedWeather
  sharedWeather,
  // BCE-4X V8: Score V8 National
  scoreV8,
  biomeProfile,
  scoreV8Loading,
  // TERRITOIRE_ROUTE_RESTORE_Ω (2026-05-11 · STEEVE-MAX)
  pageTitle = 'Analyse Territoire BIONIC',
}) => {
  // BCE-4X PositionLock
  const headerRef = useRef(null);
  useEffect(() => {
    if (headerRef.current) {
      headerRef.current.style.zIndex = getProtectedZIndex('ui-toolbar');
    }
  }, []);

  return (
    <header
      ref={headerRef}
      className="flex-shrink-0 min-h-[60px] bg-[#0d0d14] border-b border-[#1a1a2e] px-4 pl-24 flex items-center justify-between relative"
      style={{ zIndex: getProtectedZIndex('ui-toolbar'), contain: 'layout style' }}
      data-testid="bionic-header"
      data-bce4x-locked="true"
      data-bce4x-layout-frozen="true"
    >
      <div className="flex items-center gap-3">
        <button onClick={() => navigate('/')} className="text-gray-500 hover:text-white transition-colors" data-testid="header-back-btn">
          <ArrowLeft className="h-[22px] w-[22px]" />
        </button>
        <div className="h-6 w-px bg-[#1a1a2e]" />
        <h1 className="text-base font-semibold text-white tracking-tight">{pageTitle}</h1>
      </div>
      <div className="flex items-center gap-3">
        {/* BCE-4X V8: SCORE V8 NATIONAL — 10 composantes */}
        <ScoreV8Badge
          scoreV8={scoreV8}
          biomeProfile={biomeProfile}
          loading={scoreV8Loading}
        />
        {/* + WAYPOINT */}
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <button
              className={`h-8 px-4 flex items-center gap-1.5 rounded-lg font-bold text-xs uppercase tracking-wider transition-all duration-150 flex-shrink-0 ${
                mapClickMode
                  ? 'bg-green-500/20 border-2 border-green-500/60 text-green-400'
                  : 'bg-[#FF9800]/15 border-2 border-[#FF9800]/50 hover:bg-[#FF9800]/25 text-[#FF9800]'
              }`}
              data-testid="add-waypoint-main-btn"
            >
              <Plus className="h-4 w-4" />
              <span className="text-xs">{mapClickMode ? 'Cliquez...' : 'WAYPOINT'}</span>
            </button>
          </DropdownMenuTrigger>
          <DropdownMenuContent className="bg-gray-950 border-gray-700/60 shadow-xl min-w-[220px]" side="bottom" align="center">
            <DropdownMenuItem onClick={() => setShowAddWaypointDialog(true)} className="text-white hover:bg-white/10 cursor-pointer" data-testid="wp-action-coords">
              <Edit2 className="h-4 w-4 mr-2 text-[#FF9800]" /> Saisir les coordonnees
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => setMapClickMode(true)} className="text-white hover:bg-white/10 cursor-pointer" data-testid="wp-action-click">
              <Crosshair className="h-4 w-4 mr-2 text-green-500" /> Cliquer sur la carte
            </DropdownMenuItem>
            {selectedWaypointForZones && (
              <>
                <DropdownMenuSeparator className="bg-gray-700/50" />
                <DropdownMenuItem onClick={onCenterWaypoint} className="text-white hover:bg-white/10 cursor-pointer" data-testid="wp-action-center">
                  <LocateFixed className="h-4 w-4 mr-2 text-blue-400" /> Centrer sur ce waypoint
                </DropdownMenuItem>
                <DropdownMenuItem onClick={onClearWaypoint} className="text-amber-400 hover:bg-white/10 cursor-pointer" data-testid="wp-action-deselect">
                  <ToggleLeft className="h-4 w-4 mr-2" /> Deselectionner
                </DropdownMenuItem>
                <DropdownMenuItem
                  onClick={() => {
                    if (window.confirm(`Supprimer le waypoint "${selectedWaypointForZones.name}" ?`)) {
                      onDeleteWaypoint(selectedWaypointForZones.id);
                    }
                  }}
                  className="text-red-400 hover:bg-white/10 cursor-pointer"
                  data-testid="wp-action-delete"
                >
                  <Trash2 className="h-4 w-4 mr-2" /> Supprimer waypoint
                </DropdownMenuItem>
              </>
            )}
            {mapClickMode && (
              <>
                <DropdownMenuSeparator className="bg-gray-700/50" />
                <DropdownMenuItem onClick={() => setMapClickMode(false)} className="text-red-400 hover:bg-white/10 cursor-pointer" data-testid="wp-action-cancel">
                  <X className="h-4 w-4 mr-2" /> Annuler
                </DropdownMenuItem>
              </>
            )}
          </DropdownMenuContent>
        </DropdownMenu>
        {/* BCE-4X V9: Meteo RETIREE du sub-header — Directive x4950-STEEVE_MAX SECTION A */}
        {/* La meteo est disponible via le panneau METEO BIONIC uniquement — ZERO duplication */}
        {/* BCE-4X V8: PARTAGER relocalisé ici — Directive ×4850-STEEVE_MAX */}
        <div className="flex-shrink-0" data-testid="subheader-share-container">
          <ShareBionicButton />
        </div>
      </div>
    </header>
  );
};

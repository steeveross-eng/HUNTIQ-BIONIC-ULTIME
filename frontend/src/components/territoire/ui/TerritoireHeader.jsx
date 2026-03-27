/**
 * TerritoireHeader.jsx — Header BIONIC epure
 * =============================================
 * BCE-4X P0: Score TOUJOURS visible (chargement ou valeur).
 * Typographie harmonisee avec bouton WAYPOINT.
 * Position verrouillee via BCE4X_UIShield (PositionLock + ZIndexGuard).
 */
import React, { useRef, useEffect } from 'react';
import { ArrowLeft, Thermometer, Wind, Zap, Plus, Edit2, Crosshair, X, LocateFixed, Trash2, ToggleLeft } from 'lucide-react';
import { Switch } from '@/components/ui/switch';
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger, DropdownMenuSeparator } from '@/components/ui/dropdown-menu';
import useWeatherStore from '@/stores/useWeatherStore';
import useBionicStore from '@/stores/useBionicStore';
import { getProtectedZIndex } from '@/components/territoire/map/BCE4X_UIShield';

export const TerritoireHeader = ({
  navigate,
  liveMode,
  setLiveMode,
  selectedWaypointForZones,
  mapClickMode,
  setMapClickMode,
  setShowAddWaypointDialog,
  onClearWaypoint,
  onDeleteWaypoint,
  onCenterWaypoint,
  displayScore,
  scoreRating,
}) => {
  // BCE-4X: Score — double source (props + store), props prioritaire
  const storeScore = useBionicStore(s => s.displayScore);
  const storeRating = useBionicStore(s => s.scoreRating);
  const finalScore = (displayScore != null && displayScore > 0) ? displayScore : (storeScore != null && storeScore > 0) ? storeScore : null;
  const finalRating = (scoreRating && scoreRating.ringColor) ? scoreRating : (storeRating && storeRating.ringColor) ? storeRating : null;

  // BCE-4X Phase 2.9: Source de verite UNIQUE meteo — ZERO fallback intelligenceWeather
  // STEEVE-MAX: Suppression du fallback useBionicStore pour eliminer le mismatch temperature
  const weatherCurrent = useWeatherStore(s => s.current);
  const temp = weatherCurrent?.temperature_c ?? null;
  const windDir = weatherCurrent?.wind_direction_deg ?? null;
  const windSpeed = weatherCurrent?.wind_speed_kmh ?? null;

  const hasScore = finalScore != null && finalScore > 0;
  const isLoading = !hasScore;
  const ringColor = finalRating?.ringColor || '#FF9800';
  const circumference = 2 * Math.PI * 16;

  // BCE-4X PositionLock: Verrouillage z-index du header
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
        <h1 className="text-base font-semibold text-white tracking-tight">Analyse Territoire BIONIC</h1>
      </div>
      <div className="flex items-center gap-3">
        {/* BCE-4X P0: Score badge — TOUJOURS affiche, a gauche de + WAYPOINT */}
        <div
          className="flex items-center gap-2.5 h-9 px-3 rounded-lg border-2 transition-all"
          style={{
            borderColor: hasScore ? `${ringColor}50` : '#FF980050',
            backgroundColor: hasScore ? `${ringColor}12` : '#FF980008',
          }}
          data-testid="header-score-badge"
          data-bce4x-locked="true"
        >
          <svg width="28" height="28" viewBox="0 0 36 36" className="flex-shrink-0">
            <circle cx="18" cy="18" r="16" fill="none" stroke="#374151" strokeWidth="2" />
            {hasScore ? (
              <circle
                cx="18" cy="18" r="16" fill="none"
                stroke={ringColor} strokeWidth="2.5" strokeLinecap="round"
                strokeDasharray={`${circumference * (finalScore / 100)} ${circumference * (1 - finalScore / 100)}`}
                transform="rotate(-90 18 18)"
                style={{ transition: 'stroke-dasharray 0.6s ease-out' }}
              />
            ) : (
              <circle
                cx="18" cy="18" r="16" fill="none"
                stroke="#FF9800" strokeWidth="1.5" strokeLinecap="round"
                strokeDasharray="8 8"
                className="animate-spin"
                style={{ transformOrigin: '18px 18px', animationDuration: '3s' }}
              />
            )}
            <text
              x="18" y="20.5" textAnchor="middle"
              fill={hasScore ? ringColor : '#FF9800'}
              fontSize="9" fontWeight="800"
            >
              {hasScore ? Math.round(finalScore) : '--'}
            </text>
          </svg>
          <div className="flex flex-col leading-none">
            <span
              className="text-sm font-bold uppercase tracking-wider"
              style={{ color: hasScore ? ringColor : '#FF9800' }}
            >
              {hasScore ? (finalRating?.label || 'Score') : 'Score'}
            </span>
            <span className="text-[9px] text-gray-500 font-bold tracking-wide mt-0.5">
              {hasScore ? `${Math.round(finalScore)}/100` : 'Calcul...'}
            </span>
          </div>
        </div>
        {/* + WAYPOINT — bouton principal (reference typographique) */}
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <button
              className={`h-9 px-6 flex items-center gap-2 rounded-lg font-bold text-sm uppercase tracking-wider transition-all duration-150 ${
                mapClickMode
                  ? 'bg-green-500/20 border-2 border-green-500/60 text-green-400'
                  : 'bg-[#FF9800]/15 border-2 border-[#FF9800]/50 hover:bg-[#FF9800]/25 text-[#FF9800]'
              }`}
              data-testid="add-waypoint-main-btn"
            >
              <Plus className="h-5 w-5" />
              <span className="text-sm">{mapClickMode ? 'Cliquez...' : 'Waypoint'}</span>
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
        {/* Section 5: Temperature officielle INTELLIGENCE */}
        {temp != null && (
          <div className="flex items-center gap-3 bg-[#111118] rounded-lg px-3 py-1.5 border border-[#1a1a2e]" data-testid="header-weather-official">
            <div className="flex items-center gap-1">
              <Thermometer className="h-4 w-4" style={{ color: '#4A7A2E' }} />
              <span className="text-xs text-white font-mono">{temp}°C</span>
            </div>
            {windSpeed != null && (
              <div className="flex items-center gap-1">
                <Wind className="h-4 w-4" style={{ color: '#8B6F47' }} />
                <span className="text-xs text-white font-mono">{windDir}° {windSpeed} km/h</span>
              </div>
            )}
          </div>
        )}
        {/* LIVE */}
        <div className="flex items-center gap-1.5 bg-[#111118] rounded-lg px-2.5 py-1.5 border border-[#1a1a2e]" data-testid="header-live">
          <Zap className={`h-4 w-4 ${liveMode ? 'text-green-400' : 'text-gray-600'}`} />
          <span className="text-[10px] text-gray-500 uppercase">LIVE</span>
          <Switch checked={liveMode} onCheckedChange={setLiveMode} className="data-[state=checked]:bg-green-500 scale-75" />
        </div>
      </div>
    </header>
  );
};


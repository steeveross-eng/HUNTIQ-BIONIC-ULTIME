/**
 * TerritoireHeader.jsx — Header BIONIC V6+ GOLDEN
 * =============================================
 * BCE-4X: Source UNIQUE météo (sharedWeather prop)
 * - ZERO duplication avec METEO BIONIC
 * - SCORE CHASSE V6+ synchronisé depuis SUPRA/V6
 * - Rafales incluses
 * - Purge complète V1-V5
 */
import React, { useRef, useEffect } from 'react';
import { ArrowLeft, Thermometer, Wind, Zap, Plus, Edit2, Crosshair, X, LocateFixed, Trash2, ToggleLeft, Printer, Gauge } from 'lucide-react';
import { Switch } from '@/components/ui/switch';
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger, DropdownMenuSeparator } from '@/components/ui/dropdown-menu';
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
  // BCE-4X V6+: Source UNIQUE météo depuis sharedWeather
  sharedWeather,
}) => {
  // BCE-4X: Extraire les données météo de la source unique
  const weather = sharedWeather?.weather || {};
  const wind = sharedWeather?.wind || {};
  const huntingScore = sharedWeather?.huntingScore || {};
  const isLoading = sharedWeather?.loading ?? true;

  const temp = weather?.temperature ?? null;
  const windDir = wind?.direction ?? null;
  const windSpeed = wind?.speed ?? null;
  const windGusts = wind?.gusts ?? null;
  const windCardinal = wind?.directionLabel ?? '';

  // SCORE CHASSE V6+ depuis SUPRA/V6
  const scoreValue = huntingScore?.overall ?? null;
  const scoreLabel = huntingScore?.label ?? '';
  const hasScore = scoreValue != null && scoreValue > 0;

  // Couleur du score
  const getScoreColor = (s) => {
    if (s >= 80) return '#22C55E';
    if (s >= 60) return '#84CC16';
    if (s >= 40) return '#F59E0B';
    if (s >= 20) return '#EF4444';
    return '#6B7280';
  };
  const scoreColor = hasScore ? getScoreColor(scoreValue) : '#6B7280';

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
        <h1 className="text-base font-semibold text-white tracking-tight">Analyse Territoire BIONIC</h1>
      </div>
      <div className="flex items-center gap-3">
        {/* BCE-4X V6+: SCORE CHASSE synchronisé SUPRA/V6 */}
        <div
          className="flex items-center gap-2 h-9 px-3 rounded-lg border transition-all"
          style={{
            borderColor: `${scoreColor}40`,
            backgroundColor: `${scoreColor}10`,
          }}
          data-testid="header-score-chasse-v6"
        >
          <Gauge className="h-4 w-4" style={{ color: scoreColor }} />
          <div className="flex flex-col leading-none">
            <span className="text-[10px] text-gray-500 uppercase tracking-wider">Score Chasse</span>
            <span className="text-xs font-bold" style={{ color: scoreColor }}>
              {hasScore ? `${Math.round(scoreValue)}/100` : (isLoading ? '...' : '--')}
              {scoreLabel && <span className="ml-1 text-[9px] font-medium opacity-80">{scoreLabel}</span>}
            </span>
          </div>
        </div>
        {/* + WAYPOINT */}
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
        {/* BCE-4X V6+: Météo compacte — source unique sharedWeather */}
        {temp != null && (
          <div className="flex items-center gap-3 bg-[#111118] rounded-lg px-3 py-1.5 border border-[#1a1a2e]" data-testid="header-weather-v6">
            <div className="flex items-center gap-1">
              <Thermometer className="h-4 w-4" style={{ color: '#4A7A2E' }} />
              <span className="text-xs text-white font-mono">{temp}°C</span>
            </div>
            {windSpeed != null && (
              <div className="flex items-center gap-1">
                <Wind className="h-4 w-4" style={{ color: '#8B6F47' }} />
                <span className="text-xs text-white font-mono">
                  {windCardinal || ''}{windDir != null ? ` ${windDir}°` : ''} {windSpeed} km/h
                </span>
              </div>
            )}
            {windGusts != null && windGusts > windSpeed && (
              <span className="text-[10px] text-amber-400/80 font-mono">Raf. {windGusts}</span>
            )}
          </div>
        )}
        {/* LIVE */}
        <div className="flex items-center gap-1.5 bg-[#111118] rounded-lg px-2.5 py-1.5 border border-[#1a1a2e]" data-testid="header-live">
          <Zap className={`h-4 w-4 ${liveMode ? 'text-green-400' : 'text-gray-600'}`} />
          <span className="text-[10px] text-gray-500 uppercase">LIVE</span>
          <Switch checked={liveMode} onCheckedChange={setLiveMode} className="data-[state=checked]:bg-green-500 scale-75" />
        </div>
        {/* PRINT */}
        <button
          onClick={() => window.print()}
          className="flex items-center gap-1.5 bg-[#111118] rounded-lg px-2.5 py-1.5 border border-[#1a1a2e] hover:bg-[#1a1a2e] transition-colors"
          title="Imprimer la page"
          data-testid="header-print-btn"
        >
          <Printer className="h-4 w-4 text-gray-400" />
          <span className="text-[10px] text-gray-500 uppercase">PRINT</span>
        </button>
      </div>
    </header>
  );
};

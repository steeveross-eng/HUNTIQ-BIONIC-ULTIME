/**
 * LayersPanelOmegaUnified.jsx — P20 cleanup · panneau unifié 18 couches
 * ═══════════════════════════════════════════════════════════════
 * COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU · ANTI-GÉNÉRIQUE STRICT
 *
 * Source UNIQUE de toggle/opacity pour les 18 couches doctrinales.
 * Branchable opt-in via flag panelMode='unified' (FUSION ADD-ONLY).
 * V30_LOCK : INVIOLÉ — n'écrase aucun panel existant.
 * ═══════════════════════════════════════════════════════════════
 */
import React, { useEffect, useMemo, useState } from 'react';
import { Switch } from '@/components/ui/switch';
import { Slider } from '@/components/ui/slider';
import { ChevronDown, ChevronUp, Layers as LayersIcon } from 'lucide-react';
import {
  LAYER_CATALOG_OMEGA,
  LAYER_GROUPS_OMEGA,
  LAYER_CATALOG_BY_GROUP_OMEGA,
  LAYER_CATALOG_DOCTRINE_META,
} from './registry/layer_catalog_omega';

// P20_PHASE5_CANONICAL_LOCK_Ω · BCE-4X URL canonique
const CANONICAL_STATUS_URL = (() => {
  const base = process.env.REACT_APP_BACKEND_URL || '';
  return `${base}/api/v30/super-masters/territoire-omega-canonical-status`;
})();

// P21_CANONICAL_VISUAL_LOCK_Ω · validation visuelle SHA-256
const VISUAL_SYNC_VALIDATE_URL = (() => {
  const base = process.env.REACT_APP_BACKEND_URL || '';
  return `${base}/api/v30/super-masters/canonical-visual-sync-validate`;
})();

// P21 · Focus mode opacity multipliers
const FOCUS_DIM_PCT = 20;
const FOCUS_FOCUSED_PCT = 100;

const LayersPanelOmegaUnified = ({
  activeMap = {},
  opacityMap = {},
  onToggle = () => {},
  onOpacityChange = () => {},
  initialExpanded = false,
}) => {
  const [expanded, setExpanded] = useState(initialExpanded);
  const [expandedGroups, setExpandedGroups] = useState({ B: true });
  // P20_PHASE5 · sync indicator SHA-256 (canonical lock)
  const [canonicalSync, setCanonicalSync] = useState(null);
  // P21 · visual signature SHA-256 (recalculated on change)
  const [visualSync, setVisualSync] = useState(null);
  // P21 · Focus mode (hover layer dims others)
  const [focusedLayerId, setFocusedLayerId] = useState(null);

  useEffect(() => {
    let cancelled = false;
    const fetchCanonical = () => {
      fetch(CANONICAL_STATUS_URL, { cache: 'no-store' })
        .then((r) => (r.ok ? r.json() : null))
        .then((d) => {
          if (cancelled || !d) return;
          setCanonicalSync(d.result || null);
        })
        .catch(() => {});
    };
    fetchCanonical();
    const t = setInterval(fetchCanonical, 30000);
    return () => {
      cancelled = true;
      clearInterval(t);
    };
  }, []);

  // P21 · recalcule visual signature côté backend à chaque changement
  // d'activeMap ou opacityMap (debounced 600ms · anti-générique)
  useEffect(() => {
    let cancelled = false;
    const activeIds = Object.entries(activeMap)
      .filter(([, v]) => !!v).map(([k]) => k);
    const handle = setTimeout(() => {
      fetch(VISUAL_SYNC_VALIDATE_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        cache: 'no-store',
        body: JSON.stringify({
          active_layer_ids: activeIds,
          opacity_map: opacityMap,
        }),
      })
        .then((r) => (r.ok ? r.json() : null))
        .then((d) => {
          if (cancelled || !d) return;
          setVisualSync(d.result || null);
        })
        .catch(() => {});
    }, 600);
    return () => {
      cancelled = true;
      clearTimeout(handle);
    };
  }, [activeMap, opacityMap]);

  const totalActive = useMemo(
    () => LAYER_CATALOG_OMEGA.filter((l) => !!activeMap[l.id]).length,
    [activeMap],
  );

  const toggleGroup = (g) =>
    setExpandedGroups((s) => ({ ...s, [g]: !s[g] }));

  return (
    <div
      data-testid="layers-panel-omega-unified"
      style={{
        background: 'rgba(15,23,42,0.95)',
        backdropFilter: 'blur(14px)',
        border: '1px solid rgba(212,160,23,0.3)',
        borderRadius: 10,
        color: '#E8E4D9',
        fontFamily: 'Georgia, serif',
        fontSize: 11,
        width: 280,
        maxHeight: '80vh',
        overflowY: 'auto',
      }}
    >
      {/* Header */}
      <div
        onClick={() => setExpanded((v) => !v)}
        data-testid="layers-panel-omega-toggle"
        style={{
          padding: '10px 12px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          borderBottom: expanded ? '1px solid rgba(212,160,23,0.2)' : 'none',
          cursor: 'pointer',
          userSelect: 'none',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <LayersIcon size={14} color="#D4A017" />
          <span
            style={{
              color: '#D4A017',
              fontWeight: 800,
              fontSize: 10,
              letterSpacing: 1.5,
            }}
          >
            COUCHES Ω · 18 DOCTRINALES
          </span>
          <span
            style={{
              background: '#D4A017',
              color: '#0F1419',
              fontSize: 9,
              fontWeight: 800,
              borderRadius: 10,
              padding: '1px 6px',
            }}
          >
            {totalActive}/{LAYER_CATALOG_OMEGA.length}
          </span>
        </div>
        {expanded ? (
          <ChevronUp size={14} color="#94A3B8" />
        ) : (
          <ChevronDown size={14} color="#94A3B8" />
        )}
      </div>

      {expanded && (
        <div style={{ padding: '8px 10px' }}>
          {Object.values(LAYER_GROUPS_OMEGA).map((group) => {
            const layers = LAYER_CATALOG_BY_GROUP_OMEGA[group.id] || [];
            if (layers.length === 0) return null;
            const groupActive = layers.filter((l) => !!activeMap[l.id]).length;
            const isOpen = expandedGroups[group.id];
            return (
              <div
                key={group.id}
                data-testid={`layers-panel-omega-group-${group.id}`}
                style={{ marginBottom: 8 }}
              >
                <div
                  onClick={() => toggleGroup(group.id)}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    padding: '6px 8px',
                    background: `${group.color}1a`,
                    borderLeft: `3px solid ${group.color}`,
                    borderRadius: 4,
                    cursor: 'pointer',
                  }}
                >
                  <span
                    style={{
                      color: group.color,
                      fontWeight: 800,
                      fontSize: 10,
                      letterSpacing: 1,
                    }}
                  >
                    {group.id} · {group.label}
                  </span>
                  <span
                    style={{
                      fontSize: 9,
                      color: '#94A3B8',
                      fontFamily: 'JetBrains Mono, monospace',
                    }}
                  >
                    {groupActive}/{layers.length} · z{group.zBase}
                  </span>
                </div>
                {isOpen && (
                  <div
                    style={{
                      marginTop: 4,
                      display: 'flex',
                      flexDirection: 'column',
                      gap: 2,
                    }}
                  >
                    {layers.map((layer) => {
                      const Icon = layer.icon;
                      const isActive = !!activeMap[layer.id];
                      const opacity = opacityMap[layer.id] ?? layer.opacityDefault;
                      // P21 · focus mode : dim si autre couche focused
                      const isFocused = focusedLayerId === layer.id;
                      const isDimmed = focusedLayerId
                        && focusedLayerId !== layer.id;
                      const rowOpacity = isDimmed
                        ? FOCUS_DIM_PCT / 100
                        : 1;
                      return (
                        <div
                          key={layer.id}
                          data-testid={`layers-panel-omega-row-${layer.id}`}
                          onMouseEnter={() => setFocusedLayerId(layer.id)}
                          onMouseLeave={() => setFocusedLayerId(null)}
                          style={{
                            padding: '4px 8px',
                            background: isActive
                              ? `${layer.color}14`
                              : 'transparent',
                            borderRadius: 4,
                            opacity: rowOpacity,
                            outline: isFocused
                              ? `1px solid ${layer.color}88`
                              : 'none',
                            transition:
                              'opacity 0.18s, outline 0.12s',
                          }}
                        >
                          <div
                            style={{
                              display: 'flex',
                              alignItems: 'center',
                              justifyContent: 'space-between',
                            }}
                          >
                            <div
                              style={{
                                display: 'flex',
                                alignItems: 'center',
                                gap: 6,
                                flex: 1,
                              }}
                              title={layer.desc}
                            >
                              <Icon
                                size={11}
                                color={isActive ? layer.color : '#64748B'}
                              />
                              <span
                                style={{
                                  fontSize: 10,
                                  color: isActive ? '#E8E4D9' : '#94A3B8',
                                  fontWeight: isActive ? 600 : 400,
                                }}
                              >
                                {layer.label}
                              </span>
                              <span
                                style={{
                                  fontSize: 7,
                                  color: '#64748B',
                                  fontFamily: 'JetBrains Mono, monospace',
                                  marginLeft: 'auto',
                                  paddingRight: 4,
                                }}
                              >
                                {layer.code}
                              </span>
                            </div>
                            <Switch
                              checked={isActive}
                              onCheckedChange={() => onToggle(layer.id)}
                              className="h-3.5 w-7"
                              data-testid={`layers-panel-omega-toggle-${layer.id}`}
                            />
                          </div>
                          {isActive && (
                            <div
                              style={{
                                marginTop: 3,
                                display: 'flex',
                                alignItems: 'center',
                                gap: 6,
                                paddingLeft: 18,
                              }}
                            >
                              <span style={{ fontSize: 8, color: '#64748B' }}>
                                Op
                              </span>
                              <Slider
                                value={[opacity]}
                                onValueChange={([v]) =>
                                  onOpacityChange(layer.id, v)
                                }
                                min={10}
                                max={100}
                                step={5}
                                className="flex-1"
                              />
                              <span
                                style={{
                                  fontSize: 8,
                                  color: '#94A3B8',
                                  fontFamily: 'JetBrains Mono, monospace',
                                  width: 26,
                                  textAlign: 'right',
                                }}
                              >
                                {opacity}%
                              </span>
                            </div>
                          )}
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>
            );
          })}

          {/* Doctrine footer */}
          <div
            style={{
              marginTop: 8,
              padding: '6px 8px',
              borderTop: '1px solid rgba(212,160,23,0.15)',
              fontSize: 8,
              color: '#64748B',
              fontFamily: 'JetBrains Mono, monospace',
              lineHeight: 1.5,
            }}
            data-testid="layers-panel-omega-doctrine-footer"
          >
            V30_LOCK INVIOLÉ · FUSION ADD-ONLY
            <br />
            ANTI-GÉNÉRIQUE STRICT · {LAYER_CATALOG_DOCTRINE_META.n_layers} couches
            {/* P20_PHASE5 · sync indicator SHA-256 (canonical lock) */}
            {canonicalSync && (
              <div
                data-testid="layers-panel-omega-sync-indicator"
                style={{
                  marginTop: 4,
                  paddingTop: 4,
                  borderTop: '1px dashed rgba(212,160,23,0.1)',
                  color: '#7CB518',
                }}
              >
                <div title={`Canonical SHA-256: ${canonicalSync.canonical_sha256}`}>
                  ⛓ canonical {canonicalSync.canonical_sha256
                    ? canonicalSync.canonical_sha256.slice(0, 12)
                    : '—'}…
                </div>
                {canonicalSync?.sync_indicator?.data?.available
                  ? (
                    <div
                      style={{ color: '#94A3B8' }}
                      title={
                        canonicalSync.sync_indicator.data
                          .last_force_reload_sha256
                        || 'no reload sha'
                      }
                    >
                      ⟲ reload {canonicalSync.sync_indicator.data
                        .last_force_reload_sha256
                        ? canonicalSync.sync_indicator.data
                            .last_force_reload_sha256.slice(0, 12)
                        : '—'}…
                      {' · '}
                      {(canonicalSync.sync_indicator.data
                        .last_force_reload_at_utc || '—').slice(0, 19)}
                    </div>
                  ) : (
                    <div style={{ color: '#FCA5A5' }}>
                      ⟲ no force-reload yet
                    </div>
                  )}
                <div style={{ color: '#A78BFA' }}>
                  ⏱ watchdog {canonicalSync?.watchdog_lock?.timeout_s
                    ?? '—'}s · LOCK
                </div>
              </div>
            )}
            {/* P21 · visual signature SHA + validation verdict */}
            {visualSync && (
              <div
                data-testid="layers-panel-omega-visual-sync"
                style={{
                  marginTop: 3,
                  paddingTop: 3,
                  borderTop: '1px dashed rgba(212,160,23,0.1)',
                  color: '#06B6D4',
                }}
              >
                <div title={`Visual SHA-256: ${visualSync.visual_signature?.visual_sha256}`}>
                  ◈ visual {visualSync.visual_signature?.visual_sha256
                    ? visualSync.visual_signature.visual_sha256.slice(0, 12)
                    : '—'}…
                </div>
                <div
                  style={{
                    color: visualSync.validation?.is_valid_doctrinal
                      ? '#7CB518' : '#FCA5A5',
                  }}
                  data-testid="layers-panel-omega-visual-verdict"
                >
                  ✓ {visualSync.validation?.verdict || '—'}
                  {' · '}
                  {visualSync.validation?.components?.n_active_canonical || 0}
                  /
                  {visualSync.validation?.components?.minimum_required || 7}
                  {visualSync.validation?.components?.bio_omega_missing?.length > 0 ? (
                    <span style={{ color: '#F59E0B', marginLeft: 6 }}>
                      missing: {visualSync.validation.components.bio_omega_missing.join(',')}
                    </span>
                  ) : null}
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default LayersPanelOmegaUnified;

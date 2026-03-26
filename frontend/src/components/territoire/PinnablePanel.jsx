/**
 * PinnablePanel — x4515-FIX
 * Wrapper universel pour TOUS les panneaux d'analyse.
 *
 * Modes:
 *   - Normal: position standard
 *   - Fixe (Pin): flottant, deplacable, redimensionnable, z-2000
 *   - Pleine page (Expand): 100vw x 100vh, fond clair, texte #111/#222, 16-18px min
 *
 * Exigences x4515-FIX:
 *   - Pleine largeur et hauteur en mode expand
 *   - Texte fonce #111/#222 sur fond clair en mode expand
 *   - Taille minimale 16-18px
 *   - Marges internes augmentees
 *   - Hierarchie visuelle renforcee
 *   - Scroll interne fluide
 *   - Aucun debordement ou clipping
 */
import React, { useState, useRef, useCallback, useEffect } from 'react';
import { Pin, PinOff, Maximize2, Minimize2, X, GripVertical, Printer } from 'lucide-react';

const PINNABLE_CSS_ID = 'pinnable-panel-css-v2';
const PINNABLE_CSS = `
.pinnable-panel-root {
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}
.pinnable-panel-pinned {
  box-shadow: 0 8px 40px rgba(0,0,0,0.6), 0 0 0 1px rgba(245,166,35,0.15);
}
.pinnable-panel-expanded {
  position: fixed !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  width: 100vw !important;
  height: 100vh !important;
  z-index: 9999 !important;
  border-radius: 0 !important;
  max-height: 100vh !important;
}
.pinnable-panel-expanded .pinnable-content {
  background: #fafafa;
  color: #111;
  font-size: 16px;
  line-height: 1.7;
  padding: 2rem 3rem;
  max-width: 960px;
  margin: 0 auto;
}
.pinnable-panel-expanded .pinnable-content * {
  color: inherit;
}
.pinnable-panel-expanded .pinnable-content h1,
.pinnable-panel-expanded .pinnable-content h2,
.pinnable-panel-expanded .pinnable-content h3,
.pinnable-panel-expanded .pinnable-content [class*="font-bold"],
.pinnable-panel-expanded .pinnable-content [class*="font-semibold"],
.pinnable-panel-expanded .pinnable-content [class*="font-black"] {
  color: #111 !important;
}
.pinnable-panel-expanded .pinnable-content p,
.pinnable-panel-expanded .pinnable-content span,
.pinnable-panel-expanded .pinnable-content div,
.pinnable-panel-expanded .pinnable-content li {
  color: #222 !important;
  font-size: max(16px, inherit) !important;
  line-height: 1.65 !important;
}
.pinnable-panel-expanded .pinnable-content [class*="text-\\[8px\\]"],
.pinnable-panel-expanded .pinnable-content [class*="text-\\[9px\\]"],
.pinnable-panel-expanded .pinnable-content [class*="text-\\[10px\\]"],
.pinnable-panel-expanded .pinnable-content [class*="text-xs"],
.pinnable-panel-expanded .pinnable-content [class*="text-sm"] {
  font-size: 16px !important;
  line-height: 1.6 !important;
}
.pinnable-panel-expanded .pinnable-content [class*="text-lg"],
.pinnable-panel-expanded .pinnable-content [class*="text-xl"],
.pinnable-panel-expanded .pinnable-content [class*="text-2xl"] {
  font-size: 28px !important;
  line-height: 1.3 !important;
  color: #111 !important;
}
.pinnable-panel-expanded .pinnable-content [class*="bg-"] {
  background-color: #f0f0f5 !important;
  border-color: #d0d0d8 !important;
}
.pinnable-panel-expanded .pinnable-content [class*="rounded"] {
  padding: 1rem !important;
  margin-bottom: 0.75rem !important;
}
.pinnable-panel-expanded .pinnable-content [class*="space-y-"] > * + * {
  margin-top: 1rem !important;
}
.pinnable-panel-expanded .pinnable-content [class*="gap-"] {
  gap: 1rem !important;
}
.pinnable-panel-expanded .pinnable-content button {
  font-size: 16px !important;
  padding: 0.75rem 1.5rem !important;
}
.pinnable-panel-expanded .pinnable-header {
  background: #fff;
  border-bottom: 2px solid #e5e7eb;
  padding: 1rem 2rem;
}
.pinnable-panel-expanded .pinnable-header * {
  color: #111 !important;
}
.pinnable-scroll {
  overflow-y: auto;
  overflow-x: hidden;
  scrollbar-width: thin;
  scrollbar-color: rgba(100,100,100,0.3) transparent;
}
.pinnable-scroll::-webkit-scrollbar { width: 6px; }
.pinnable-scroll::-webkit-scrollbar-track { background: transparent; }
.pinnable-scroll::-webkit-scrollbar-thumb {
  background: rgba(100,100,100,0.25);
  border-radius: 6px;
}
.pinnable-scroll::-webkit-scrollbar-thumb:hover {
  background: rgba(100,100,100,0.4);
}
.pinnable-drag-header { cursor: default; user-select: none; }
.pinnable-drag-header.draggable { cursor: grab; }
.pinnable-drag-header.draggable:active { cursor: grabbing; }
.pinnable-resize-handle {
  cursor: se-resize;
  position: absolute;
  bottom: 0; right: 0;
  width: 20px; height: 20px;
  opacity: 0;
  transition: opacity 0.2s;
}
.pinnable-panel-pinned:hover .pinnable-resize-handle { opacity: 0.7; }
`;

const PinnablePanel = ({
  title = '',
  subtitle = '',
  icon: Icon = null,
  accentColor = '#f5a623',
  children,
  onClose,
  defaultWidth = 380,
  defaultHeight = 500,
  maxHeight = '80vh',
  className = '',
  testId = 'pinnable-panel',
  headerExtra = null,
  showPrint = false,
}) => {
  const [pinned, setPinned] = useState(false);
  const [expanded, setExpanded] = useState(false);
  const [pos, setPos] = useState({ x: 60, y: 80 });
  const [size, setSize] = useState({ w: defaultWidth, h: typeof defaultHeight === 'number' ? defaultHeight : 500 });
  const dragging = useRef(false);
  const resizing = useRef(false);
  const dragOff = useRef({ x: 0, y: 0 });
  const panelRef = useRef(null);

  useEffect(() => {
    if (!document.getElementById(PINNABLE_CSS_ID)) {
      const s = document.createElement('style');
      s.id = PINNABLE_CSS_ID;
      s.textContent = PINNABLE_CSS;
      document.head.appendChild(s);
    }
  }, []);

  // Keyboard: Escape to close expanded
  useEffect(() => {
    if (!expanded) return;
    const handler = (e) => { if (e.key === 'Escape') setExpanded(false); };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, [expanded]);

  const onDragStart = useCallback((e) => {
    if (!pinned || expanded) return;
    dragging.current = true;
    const rect = panelRef.current?.getBoundingClientRect();
    dragOff.current = { x: e.clientX - (rect?.left || 0), y: e.clientY - (rect?.top || 0) };
    e.preventDefault();
  }, [pinned, expanded]);

  const onMouseMove = useCallback((e) => {
    if (dragging.current) {
      setPos({ x: Math.max(0, e.clientX - dragOff.current.x), y: Math.max(0, e.clientY - dragOff.current.y) });
    }
    if (resizing.current) {
      const rect = panelRef.current?.getBoundingClientRect();
      if (rect) setSize({ w: Math.max(300, e.clientX - rect.left), h: Math.max(200, e.clientY - rect.top) });
    }
  }, []);

  const onMouseUp = useCallback(() => { dragging.current = false; resizing.current = false; }, []);

  useEffect(() => {
    if (pinned) {
      window.addEventListener('mousemove', onMouseMove);
      window.addEventListener('mouseup', onMouseUp);
      return () => { window.removeEventListener('mousemove', onMouseMove); window.removeEventListener('mouseup', onMouseUp); };
    }
  }, [pinned, onMouseMove, onMouseUp]);

  const onResizeStart = useCallback((e) => {
    if (!pinned || expanded) return;
    resizing.current = true;
    e.preventDefault();
    e.stopPropagation();
  }, [pinned, expanded]);

  const togglePin = useCallback(() => {
    if (!pinned) {
      const rect = panelRef.current?.getBoundingClientRect();
      if (rect) { setPos({ x: rect.left, y: rect.top }); setSize({ w: rect.width || defaultWidth, h: rect.height || defaultHeight }); }
    }
    setPinned(p => !p);
    setExpanded(false);
  }, [pinned, defaultWidth, defaultHeight]);

  const toggleExpand = useCallback(() => setExpanded(p => !p), []);

  const handlePrint = useCallback(() => {
    const wasExpanded = expanded;
    if (!wasExpanded) setExpanded(true);
    setTimeout(() => { window.print(); if (!wasExpanded) setExpanded(false); }, 300);
  }, [expanded]);

  const panelStyle = expanded ? {}
    : pinned ? { position: 'fixed', left: pos.x, top: pos.y, zIndex: 2000, width: size.w, height: size.h }
    : {};

  const rootClasses = [
    'pinnable-panel-root flex flex-col overflow-hidden',
    expanded ? 'pinnable-panel-expanded' : '',
    pinned && !expanded ? 'pinnable-panel-pinned rounded-xl border border-amber-500/20' : '',
    !pinned && !expanded ? `bg-black/95 backdrop-blur-md rounded-xl border border-gray-700/50 ${className}` : '',
  ].filter(Boolean).join(' ');

  return (
    <div
      ref={panelRef}
      data-testid={testId}
      className={rootClasses}
      style={panelStyle}
      onClick={(e) => e.stopPropagation()}
      onMouseDown={(e) => { if (e.target === panelRef.current || panelRef.current?.contains(e.target)) e.stopPropagation(); }}
    >
      {/* Header */}
      <div
        className={`pinnable-header pinnable-drag-header ${pinned && !expanded ? 'draggable' : ''} flex items-center justify-between flex-shrink-0`}
        style={!expanded ? { padding: '10px 14px', borderBottom: `1px solid ${accentColor}25`, backgroundColor: expanded ? '#fff' : `${accentColor}08` } : undefined}
        onMouseDown={onDragStart}
      >
        <div className="flex items-center gap-2.5 min-w-0 flex-1">
          {pinned && !expanded && <GripVertical className="h-4 w-4 text-gray-500 flex-shrink-0" />}
          {Icon && (
            <div className="p-1.5 rounded-lg flex-shrink-0" style={{ backgroundColor: expanded ? '#f0f0f5' : `${accentColor}15` }}>
              <Icon className="h-5 w-5" style={{ color: expanded ? '#111' : accentColor }} />
            </div>
          )}
          <div className="min-w-0">
            <h3 className="font-bold truncate" style={{ fontSize: expanded ? '20px' : '13px', color: expanded ? '#111' : '#fff' }}>{title}</h3>
            {subtitle && <p className="truncate" style={{ fontSize: expanded ? '14px' : '10px', color: expanded ? '#666' : `${accentColor}90` }}>{subtitle}</p>}
          </div>
        </div>
        <div className="flex items-center gap-1.5 flex-shrink-0 ml-3">
          {headerExtra}
          {showPrint && (
            <button
              data-testid={`${testId}-print-btn`}
              onClick={handlePrint}
              title="Imprimer"
              className="p-2 rounded-lg transition-all"
              style={{
                backgroundColor: expanded ? '#e8f5e9' : 'rgba(255,255,255,0.06)',
                color: expanded ? '#2e7d32' : '#9ca3af',
              }}
            >
              <Printer className="h-4 w-4" />
            </button>
          )}
          <button
            data-testid={`${testId}-pin-btn`}
            onClick={togglePin}
            title={pinned ? 'Detacher' : 'Fixer'}
            className="p-2 rounded-lg transition-all"
            style={{
              backgroundColor: pinned ? `${accentColor}20` : expanded ? '#f0f0f5' : 'rgba(255,255,255,0.06)',
              color: pinned ? accentColor : expanded ? '#333' : '#9ca3af',
            }}
          >
            {pinned ? <PinOff className="h-4 w-4" /> : <Pin className="h-4 w-4" />}
          </button>
          <button
            data-testid={`${testId}-expand-btn`}
            onClick={toggleExpand}
            title={expanded ? 'Reduire' : 'Pleine page'}
            className="p-2 rounded-lg transition-all"
            style={{
              backgroundColor: expanded ? '#e8e8f0' : 'rgba(255,255,255,0.06)',
              color: expanded ? '#111' : '#9ca3af',
            }}
          >
            {expanded ? <Minimize2 className="h-4 w-4" /> : <Maximize2 className="h-4 w-4" />}
          </button>
          <button
            data-testid={`${testId}-close-btn`}
            onClick={onClose}
            className="p-2 rounded-lg transition-all"
            style={{
              backgroundColor: expanded ? '#fee2e2' : 'rgba(255,255,255,0.06)',
              color: expanded ? '#dc2626' : '#9ca3af',
            }}
          >
            <X className="h-4 w-4" />
          </button>
        </div>
      </div>

      {/* Scrollable Content */}
      <div
        className="pinnable-scroll pinnable-content flex-1"
        style={{
          maxHeight: expanded ? 'calc(100vh - 70px)' : pinned ? `${size.h - 56}px` : maxHeight,
          backgroundColor: expanded ? '#fafafa' : 'transparent',
        }}
      >
        {children}
      </div>

      {/* Resize handle */}
      {pinned && !expanded && (
        <div className="pinnable-resize-handle" onMouseDown={onResizeStart}>
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
            <path d="M18 2L2 18M18 8L8 18M18 14L14 18" stroke={accentColor} strokeOpacity="0.35" strokeWidth="1.5" />
          </svg>
        </div>
      )}
    </div>
  );
};

export default PinnablePanel;

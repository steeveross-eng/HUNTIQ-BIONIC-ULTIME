/**
 * PinnablePanel — x4515-PANEL_FIX_MODE
 * Wrapper reutilisable pour les panneaux d'analyse.
 *
 * Modes:
 *   - Normal: position standard, disparait au deplacement carte
 *   - Fixe (Pin): flottant, deplacable, redimensionnable, z-index eleve
 *   - Pleine page (Expand): occupe toute la fenetre
 *
 * Props:
 *   - title: string — titre du panneau
 *   - icon: LucideIcon — icone du header
 *   - accentColor: string — couleur d'accent (#hex)
 *   - children: ReactNode — contenu du panneau
 *   - onClose: function — fermeture du panneau
 *   - defaultWidth: number — largeur par defaut (px)
 *   - defaultHeight: number | string — hauteur par defaut
 *   - className: string — classes additionnelles
 *   - testId: string — data-testid
 */
import React, { useState, useRef, useCallback, useEffect } from 'react';
import { Pin, PinOff, Maximize2, Minimize2, X, GripVertical } from 'lucide-react';

const PINNABLE_CSS_ID = 'pinnable-panel-css';
const PINNABLE_CSS = `
.pinnable-panel-pinned {
  transition: box-shadow 0.2s ease;
  box-shadow: 0 8px 32px rgba(0,0,0,0.5), 0 0 0 1px rgba(245,166,35,0.15);
}
.pinnable-panel-pinned:hover {
  box-shadow: 0 12px 48px rgba(0,0,0,0.6), 0 0 0 1px rgba(245,166,35,0.25);
}
.pinnable-resize-handle {
  cursor: se-resize;
  position: absolute;
  bottom: 0;
  right: 0;
  width: 16px;
  height: 16px;
  opacity: 0;
  transition: opacity 0.2s;
}
.pinnable-panel-pinned:hover .pinnable-resize-handle {
  opacity: 0.6;
}
.pinnable-drag-header {
  cursor: default;
  user-select: none;
}
.pinnable-drag-header.draggable {
  cursor: grab;
}
.pinnable-drag-header.draggable:active {
  cursor: grabbing;
}
.pinnable-scroll-content {
  overflow-y: auto;
  overflow-x: hidden;
  scrollbar-width: thin;
  scrollbar-color: rgba(255,255,255,0.1) transparent;
}
.pinnable-scroll-content::-webkit-scrollbar {
  width: 4px;
}
.pinnable-scroll-content::-webkit-scrollbar-track {
  background: transparent;
}
.pinnable-scroll-content::-webkit-scrollbar-thumb {
  background: rgba(255,255,255,0.12);
  border-radius: 4px;
}
.pinnable-scroll-content::-webkit-scrollbar-thumb:hover {
  background: rgba(255,255,255,0.2);
}
`;

const PinnablePanel = ({
  title = '',
  subtitle = '',
  icon: Icon = null,
  accentColor = '#f5a623',
  children,
  onClose,
  defaultWidth = 380,
  defaultHeight = 'auto',
  maxHeight = '80vh',
  className = '',
  testId = 'pinnable-panel',
  headerExtra = null,
}) => {
  const [pinned, setPinned] = useState(false);
  const [expanded, setExpanded] = useState(false);
  const [pos, setPos] = useState({ x: 60, y: 80 });
  const [size, setSize] = useState({ w: defaultWidth, h: typeof defaultHeight === 'number' ? defaultHeight : 500 });
  const dragging = useRef(false);
  const resizing = useRef(false);
  const dragOffset = useRef({ x: 0, y: 0 });
  const panelRef = useRef(null);

  // Inject CSS once
  useEffect(() => {
    if (!document.getElementById(PINNABLE_CSS_ID)) {
      const s = document.createElement('style');
      s.id = PINNABLE_CSS_ID;
      s.textContent = PINNABLE_CSS;
      document.head.appendChild(s);
    }
  }, []);

  // Drag handlers
  const onDragStart = useCallback((e) => {
    if (!pinned || expanded) return;
    dragging.current = true;
    const rect = panelRef.current?.getBoundingClientRect();
    dragOffset.current = { x: e.clientX - (rect?.left || 0), y: e.clientY - (rect?.top || 0) };
    e.preventDefault();
  }, [pinned, expanded]);

  const onDragMove = useCallback((e) => {
    if (dragging.current) {
      setPos({
        x: Math.max(0, e.clientX - dragOffset.current.x),
        y: Math.max(0, e.clientY - dragOffset.current.y),
      });
    }
    if (resizing.current) {
      const rect = panelRef.current?.getBoundingClientRect();
      if (rect) {
        setSize({
          w: Math.max(280, e.clientX - rect.left),
          h: Math.max(200, e.clientY - rect.top),
        });
      }
    }
  }, []);

  const onDragEnd = useCallback(() => {
    dragging.current = false;
    resizing.current = false;
  }, []);

  useEffect(() => {
    if (pinned) {
      window.addEventListener('mousemove', onDragMove);
      window.addEventListener('mouseup', onDragEnd);
      return () => {
        window.removeEventListener('mousemove', onDragMove);
        window.removeEventListener('mouseup', onDragEnd);
      };
    }
  }, [pinned, onDragMove, onDragEnd]);

  // Resize handler
  const onResizeStart = useCallback((e) => {
    if (!pinned || expanded) return;
    resizing.current = true;
    e.preventDefault();
    e.stopPropagation();
  }, [pinned, expanded]);

  // Toggle pin
  const togglePin = useCallback(() => {
    if (!pinned) {
      const rect = panelRef.current?.getBoundingClientRect();
      if (rect) {
        setPos({ x: rect.left, y: rect.top });
        setSize({ w: rect.width, h: rect.height });
      }
    }
    setPinned(p => !p);
    setExpanded(false);
  }, [pinned]);

  // Toggle expand
  const toggleExpand = useCallback(() => {
    setExpanded(p => !p);
  }, []);

  // Compute style
  const panelStyle = expanded
    ? { position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, zIndex: 2500, width: '100vw', height: '100vh' }
    : pinned
      ? { position: 'fixed', left: pos.x, top: pos.y, zIndex: 2000, width: size.w, height: size.h }
      : {};

  const panelClasses = [
    'bg-black/95 backdrop-blur-md rounded-xl border overflow-hidden flex flex-col',
    pinned ? 'pinnable-panel-pinned border-amber-500/20' : 'border-green-500/30',
    expanded ? 'rounded-none' : '',
    className,
  ].join(' ');

  const contentMaxH = expanded
    ? 'calc(100vh - 52px)'
    : pinned
      ? `${size.h - 52}px`
      : maxHeight;

  return (
    <div
      ref={panelRef}
      data-testid={testId}
      className={panelClasses}
      style={panelStyle}
    >
      {/* Header */}
      <div
        className={`pinnable-drag-header ${pinned && !expanded ? 'draggable' : ''} flex items-center justify-between px-3 py-2.5 border-b flex-shrink-0`}
        style={{
          borderColor: `${accentColor}30`,
          backgroundColor: `${accentColor}08`,
        }}
        onMouseDown={onDragStart}
      >
        <div className="flex items-center gap-2 min-w-0 flex-1">
          {pinned && !expanded && (
            <GripVertical className="h-3.5 w-3.5 text-gray-600 flex-shrink-0" />
          )}
          {Icon && (
            <div className="p-1 rounded-md flex-shrink-0" style={{ backgroundColor: `${accentColor}15` }}>
              <Icon className="h-4 w-4" style={{ color: accentColor }} />
            </div>
          )}
          <div className="min-w-0">
            <h3 className="text-white font-bold text-xs truncate">{title}</h3>
            {subtitle && <p className="text-[9px] truncate" style={{ color: `${accentColor}90` }}>{subtitle}</p>}
          </div>
        </div>

        <div className="flex items-center gap-1 flex-shrink-0 ml-2">
          {headerExtra}
          {/* Pin toggle */}
          <button
            data-testid={`${testId}-pin-btn`}
            onClick={togglePin}
            title={pinned ? 'Detacher le panneau' : 'Fixer le panneau'}
            className="p-1.5 rounded-md transition-colors"
            style={{
              backgroundColor: pinned ? `${accentColor}20` : 'rgba(255,255,255,0.05)',
              color: pinned ? accentColor : '#9ca3af',
            }}
          >
            {pinned ? <PinOff className="h-3.5 w-3.5" /> : <Pin className="h-3.5 w-3.5" />}
          </button>
          {/* Expand toggle */}
          <button
            data-testid={`${testId}-expand-btn`}
            onClick={toggleExpand}
            title={expanded ? 'Reduire' : 'Pleine page'}
            className="p-1.5 rounded-md bg-white/5 text-gray-400 hover:text-white hover:bg-white/10 transition-colors"
          >
            {expanded ? <Minimize2 className="h-3.5 w-3.5" /> : <Maximize2 className="h-3.5 w-3.5" />}
          </button>
          {/* Close */}
          <button
            data-testid={`${testId}-close-btn`}
            onClick={onClose}
            className="p-1.5 rounded-md bg-white/5 text-gray-400 hover:text-white hover:bg-white/10 transition-colors"
          >
            <X className="h-3.5 w-3.5" />
          </button>
        </div>
      </div>

      {/* Scrollable Content */}
      <div
        className="pinnable-scroll-content flex-1"
        style={{ maxHeight: contentMaxH }}
      >
        {children}
      </div>

      {/* Resize handle (pinned mode only) */}
      {pinned && !expanded && (
        <div
          className="pinnable-resize-handle"
          onMouseDown={onResizeStart}
        >
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
            <path d="M14 2L2 14M14 6L6 14M14 10L10 14" stroke={accentColor} strokeOpacity="0.3" strokeWidth="1.5" />
          </svg>
        </div>
      )}
    </div>
  );
};

export default PinnablePanel;

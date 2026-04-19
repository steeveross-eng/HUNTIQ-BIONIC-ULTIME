/**
 * ENGINE UX-Ω-V12 — BionicButtonOmega
 * =====================================
 * Bouton presseur institutionnel avec retro-eclairage complet.
 *
 * ACTIF:
 *   - fond complet illumine (#FDD835 85%)
 *   - contour 2.0px #FFFFFF
 *   - halo 0 0 6px #FDD835
 *   - icone blanche
 *   - etat presseur (enfonce, scale 0.96)
 *
 * INACTIF:
 *   - fond #2A2A2A
 *   - icone #BDBDBD
 *   - contour 1px #444444
 *   - aucun halo
 */
import React from 'react';

export default function BionicButtonOmega({
  state = 'inactive',
  icon: Icon,
  label,
  onClick,
  testId,
  title,
}) {
  const isActive = state === 'active';
  return (
    <button
      type="button"
      onClick={onClick}
      data-testid={testId}
      title={title || label}
      className={isActive ? 'btn-omega-active' : 'btn-omega-inactive'}
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        justifyContent: 'center',
        gap: 6,
        padding: '6px 10px',
        minHeight: 32,
        borderRadius: 6,
        fontSize: 11,
        fontWeight: 700,
        letterSpacing: 0.3,
        textTransform: 'uppercase',
        cursor: 'pointer',
        fontFamily: 'ui-monospace, SFMono-Regular, Menlo, monospace',
        transition: 'background 0.18s ease, border-color 0.18s ease, box-shadow 0.18s ease, transform 0.08s ease',
        ...(isActive
          ? {
              // UX-Omega-V12-R5 Directive V: palette ORANGE intensite reduite
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
              transform: 'scale(1)',
            }),
      }}
    >
      {Icon && <Icon size={14} color={isActive ? '#FFFFFF' : '#BDBDBD'} />}
      {label && <span>{label}</span>}
    </button>
  );
}

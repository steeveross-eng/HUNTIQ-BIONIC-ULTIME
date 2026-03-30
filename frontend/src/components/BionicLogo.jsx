/**
 * BionicLogo — BCE-4X GOLDEN Phase L v2 — Logo Premium Statique
 * 
 * DIRECTIVES STEEVE-MAX:
 * - 100% STATIQUE (ZERO rotation, ZERO animation)
 * - Version PREMIUM: imposant, professionnel, impact visuel eleve
 * - Taille optimisee selon espace disponible
 * - Position: coin superieur gauche, superposition controlee du header
 * - Non flashy, professionnel
 */
import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import OptimizedImage from '@/components/ui/OptimizedImage';

export const INNER_LOGO_SIZE = 60;
export const INNER_LOGO_LEFT = 12;

export const BionicLogoGlobal = () => {
  const location = useLocation();
  const isHomePage = location.pathname === '/' || location.pathname === '';
  
  const logoSize = isHomePage ? 120 : INNER_LOGO_SIZE;
  const topPos = isHomePage ? '70px' : '66px';
  
  return (
    <Link 
      to="/"
      style={{
        position: 'fixed',
        top: topPos,
        left: `${INNER_LOGO_LEFT}px`,
        zIndex: 40,
        width: `${logoSize}px`,
        height: `${logoSize}px`,
        display: 'block',
        filter: 'drop-shadow(0 0 8px rgba(245, 166, 35, 0.25))',
        transition: 'transform 0.2s ease, filter 0.2s ease',
      }}
      data-testid="bionic-logo-global"
      aria-label="BIONIC - Retour a l'accueil"
      onMouseEnter={e => {
        e.currentTarget.style.transform = 'scale(1.05)';
        e.currentTarget.style.filter = 'drop-shadow(0 0 14px rgba(245, 166, 35, 0.4))';
      }}
      onMouseLeave={e => {
        e.currentTarget.style.transform = 'scale(1)';
        e.currentTarget.style.filter = 'drop-shadow(0 0 8px rgba(245, 166, 35, 0.25))';
      }}
    >
      <OptimizedImage 
        src="/logos/bionic-logo-official.png"
        alt="BIONIC Chasse / Hunt"
        width={logoSize}
        height={logoSize}
        className="bionic-logo-static"
        loading={isHomePage ? 'eager' : 'lazy'}
        fetchpriority={isHomePage ? 'high' : undefined}
        style={{
          width: `${logoSize}px`,
          height: `${logoSize}px`,
          objectFit: 'contain',
          mixBlendMode: 'screen',
        }}
      />
    </Link>
  );
};

const BionicLogo = ({ className = '' }) => {
  return (
    <OptimizedImage 
      src="/logos/bionic-logo-official.png"
      alt="BIONIC"
      width={36}
      height={36}
      className={`bionic-logo-static ${className}`}
      style={{ 
        width: '36px', 
        height: '36px',
        objectFit: 'contain',
        mixBlendMode: 'screen',
      }}
    />
  );
};

export default BionicLogo;

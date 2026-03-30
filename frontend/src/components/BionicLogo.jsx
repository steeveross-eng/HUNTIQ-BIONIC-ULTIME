/**
 * BionicLogo — BCE-4X GOLDEN Phase L v3 — Logo Premium Statique
 * 
 * DIRECTIVES STEEVE-MAX:
 * - 100% STATIQUE (ZERO rotation, ZERO animation, ZERO hover scale)
 * - Version PREMIUM: imposant, professionnel, impact visuel eleve, non flashy
 * - Accueil: analyse automatique de l'espace → 140px
 * - Pages secondaires: uniforme, coin superieur gauche → 64px
 * - Position: fixed, coin superieur gauche
 */
import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import OptimizedImage from '@/components/ui/OptimizedImage';

export const INNER_LOGO_SIZE = 64;
export const INNER_LOGO_LEFT = 12;

export const BionicLogoGlobal = () => {
  const location = useLocation();
  const isHomePage = location.pathname === '/' || location.pathname === '';
  
  const logoSize = isHomePage ? 140 : INNER_LOGO_SIZE;
  const topPos = isHomePage ? '68px' : '66px';
  
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
        filter: 'drop-shadow(0 0 10px rgba(245, 166, 35, 0.20))',
      }}
      data-testid="bionic-logo-global"
      aria-label="BIONIC - Retour a l'accueil"
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

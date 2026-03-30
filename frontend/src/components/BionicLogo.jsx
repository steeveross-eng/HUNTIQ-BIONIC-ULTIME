/**
 * BionicLogo - BCE-4X GOLDEN Phase L — Logo Statique Optimise
 * 
 * DIRECTIVES STEEVE-MAX:
 * - 100% STATIQUE (ZERO rotation, ZERO animation)
 * - Page accueil: 100px, sous header
 * - Pages secondaires: 50px, compact
 * - ZERO superposition sur aucune page
 * - Alignement GOLDEN conforme
 */

import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import OptimizedImage from '@/components/ui/OptimizedImage';

export const INNER_LOGO_SIZE = 50;
export const INNER_LOGO_LEFT = 12;

export const BionicLogoGlobal = () => {
  const location = useLocation();
  const isHomePage = location.pathname === '/' || location.pathname === '';
  
  const logoSize = isHomePage ? 100 : INNER_LOGO_SIZE;
  const topPos = isHomePage ? '72px' : '68px';
  
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
      width={32}
      height={32}
      className={`bionic-logo-static ${className}`}
      style={{ 
        width: '32px', 
        height: '32px',
        objectFit: 'contain',
        mixBlendMode: 'screen',
      }}
    />
  );
};

export default BionicLogo;

/**
 * BionicLogo — BCE-4X GOLDEN Phase L v4 — Logo PREMIUM STEEVE-MAX
 * 
 * DIRECTIVES:
 * - PAGE PRINCIPALE (/): Doubler la taille → 280px
 * - PAGE PREMIUM (/admin-premium): Tripler la taille → 420px
 * - PAGES SECONDAIRES: Doubler → 128px, uniforme, coin superieur gauche
 * - Superposition controlee sur le sous-header
 * - ZERO rotation, ZERO hover scale, ZERO animation
 * - Impact visuel PREMIUM, professionnel, non flashy
 */
import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import OptimizedImage from '@/components/ui/OptimizedImage';

export const INNER_LOGO_SIZE = 128;
export const INNER_LOGO_LEFT = 12;

const PREMIUM_ROUTES = ['/admin-premium', '/admin'];

export const BionicLogoGlobal = () => {
  const location = useLocation();
  const path = location.pathname;
  const isHomePage = path === '/' || path === '';
  const isPremiumPage = PREMIUM_ROUTES.some(r => path.startsWith(r));
  
  let logoSize, topPos;
  if (isPremiumPage) {
    logoSize = 420;
    topPos = '62px';
  } else if (isHomePage) {
    logoSize = 280;
    topPos = '62px';
  } else {
    logoSize = INNER_LOGO_SIZE;
    topPos = '62px';
  }
  
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
        filter: 'drop-shadow(0 0 12px rgba(245, 166, 35, 0.18))',
        pointerEvents: 'auto',
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
      width={40}
      height={40}
      className={`bionic-logo-static ${className}`}
      style={{ 
        width: '40px', 
        height: '40px',
        objectFit: 'contain',
        mixBlendMode: 'screen',
      }}
    />
  );
};

export default BionicLogo;

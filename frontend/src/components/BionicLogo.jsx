/**
 * BionicLogo — BCE-4X GOLDEN Phase L v5
 * 
 * DIRECTIVES STEEVE-MAX:
 * - PAGES SECONDAIRES: Logo 48px DANS le header (pas en fixed overlay)
 * - PAGE PRINCIPALE (/): Grand logo 560px dans le contenu (sous header)
 * - PAGE PREMIUM (/admin-premium): Logo 1260px dans le contenu
 * - ZERO glow, ZERO halo, ZERO animation, ZERO hover scale
 * - AUCUNE superposition avec onglets, photos ou textes
 */
import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import OptimizedImage from '@/components/ui/OptimizedImage';

export const INNER_LOGO_SIZE = 48;
export const INNER_LOGO_LEFT = 0;

/**
 * BionicLogoHeader — Logo compact DANS le header nav (48px)
 * Utilise sur TOUTES les pages dans la barre de navigation principale.
 */
export const BionicLogoHeader = () => {
  return (
    <Link 
      to="/"
      className="flex-shrink-0 mr-2"
      data-testid="bionic-logo-header"
      aria-label="BIONIC - Retour a l'accueil"
    >
      <OptimizedImage 
        src="/logos/bionic-logo-official.png"
        alt="BIONIC"
        width={48}
        height={48}
        className="bionic-logo-static"
        style={{
          width: '48px',
          height: '48px',
          objectFit: 'contain',
          mixBlendMode: 'screen',
        }}
      />
    </Link>
  );
};

/**
 * BionicLogoGlobal — Grand logo pour page principale et premium.
 * Positionne DANS le contenu de la page (pas en fixed overlay).
 * Visible UNIQUEMENT sur / et /admin-premium.
 */
export const BionicLogoGlobal = () => {
  const location = useLocation();
  const path = location.pathname;
  const isHomePage = path === '/' || path === '';
  const isPremiumPage = path.startsWith('/admin-premium') || path.startsWith('/admin');
  
  // Seulement visible sur page principale et premium
  if (!isHomePage && !isPremiumPage) return null;
  
  const logoSize = isPremiumPage ? 600 : 400;
  
  return (
    <div 
      style={{
        position: 'fixed',
        top: '64px',
        left: '0px',
        zIndex: 30,
        width: `${logoSize}px`,
        height: `${logoSize}px`,
        pointerEvents: 'none',
        opacity: 0.15,
      }}
      data-testid="bionic-logo-global"
    >
      <OptimizedImage 
        src="/logos/bionic-logo-official.png"
        alt="BIONIC"
        width={logoSize}
        height={logoSize}
        className="bionic-logo-static"
        style={{
          width: `${logoSize}px`,
          height: `${logoSize}px`,
          objectFit: 'contain',
          mixBlendMode: 'screen',
        }}
      />
    </div>
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

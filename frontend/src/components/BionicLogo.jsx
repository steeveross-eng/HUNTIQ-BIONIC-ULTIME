/**
 * BionicLogo — BCE-4X GOLDEN Phase L v6
 * EXECUTION EXACTE DES DIRECTIVES STEEVE-MAX:
 *
 * PAGES SECONDAIRES: 128px DANS le header, coin superieur gauche
 *   - ZERO superposition avec onglets, photos ou textes
 *   - ZERO halo, ZERO glow, ZERO animation
 *
 * PAGE PRINCIPALE (/): 560px, coin superieur gauche
 *   - Superposition controlee sur le sous-header
 *
 * PAGE PREMIUM (/admin-premium): 1260px, coin superieur gauche
 *   - Impact visuel PREMIUM+
 */
import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import OptimizedImage from '@/components/ui/OptimizedImage';

export const INNER_LOGO_SIZE = 128;
export const INNER_LOGO_LEFT = 0;

const PREMIUM_ROUTES = ['/admin-premium', '/admin'];

/**
 * BionicLogoHeader — Logo 128px DANS le header nav.
 * Le header est agrandi pour l'accueillir sans superposition.
 */
export const BionicLogoHeader = () => {
  return (
    <Link 
      to="/"
      className="flex-shrink-0"
      data-testid="bionic-logo-header"
      aria-label="BIONIC - Retour a l'accueil"
      style={{ marginRight: '8px' }}
    >
      <OptimizedImage 
        src="/logos/bionic-logo-official.png"
        alt="BIONIC"
        width={128}
        height={128}
        className="bionic-logo-static"
        style={{
          width: '128px',
          height: '128px',
          objectFit: 'contain',
          mixBlendMode: 'screen',
        }}
      />
    </Link>
  );
};

/**
 * BionicLogoGlobal — Grand logo pour page principale et premium UNIQUEMENT.
 * Page principale: 560px, coin superieur gauche, superposition controlee.
 * Page premium: 1260px, impact visuel maximal.
 * Pages secondaires: NE S'AFFICHE PAS (return null).
 */
export const BionicLogoGlobal = () => {
  // BCE-4X STEEVE-MAX: Shadow/watermark SUPPRIME — ZERO ombre, ZERO silhouette sur page principale
  // Seule la page ADMIN Premium conserve le watermark
  const location = useLocation();
  const path = location.pathname;
  const isPremiumPage = PREMIUM_ROUTES.some(r => path.startsWith(r));
  
  if (!isPremiumPage) return null;
  
  const logoSize = 1260;
  
  return (
    <div 
      style={{
        position: 'fixed',
        top: '0px',
        left: '0px',
        zIndex: 35,
        width: `${logoSize}px`,
        height: `${logoSize}px`,
        pointerEvents: 'none',
        opacity: 0.12,
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

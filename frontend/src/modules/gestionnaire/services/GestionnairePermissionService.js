/**
 * GestionnairePermissionService — Rôles/Permissions/Cloisonnement
 * Directive x7100-M4 Phase C | BCE-4X GOLDEN V6+
 *
 * Cloisonnement strict des données par territoire/organisation.
 * Le gestionnaire ne voit que les chasseurs de SON territoire avec consentement.
 */

const ROLES = {
  HUNTER: 'hunter',
  GESTIONNAIRE: 'gestionnaire',
  ADMIN: 'admin',
};

const GestionnairePermissionService = {
  ROLES,

  canViewLivePosition(viewerRole, hunterConsent, isInTerritory) {
    if (viewerRole === ROLES.HUNTER) return false;
    if (hunterConsent !== 'permanent' && hunterConsent !== 'emergency') return false;
    if (!isInTerritory) return false;
    return true;
  },

  canManageSectors(role) {
    return role === ROLES.GESTIONNAIRE || role === ROLES.ADMIN;
  },

  canReceiveEmergency(role) {
    return role === ROLES.GESTIONNAIRE || role === ROLES.ADMIN;
  },

  canViewHunterProfile(viewerRole, viewerUserId, targetUserId) {
    if (viewerUserId === targetUserId) return true;
    return viewerRole === ROLES.GESTIONNAIRE || viewerRole === ROLES.ADMIN;
  },

  canAccessGuidePro(consent) {
    return consent === 'permanent' || consent === 'emergency';
  },
};

export default GestionnairePermissionService;

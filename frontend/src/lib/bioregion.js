/**
 * BIOREGION_QC_OMEGA — P22F_FIX_R6 (2026-05-09 · COMMANDANT STEEVE-MAX)
 * ════════════════════════════════════════════════════════════════════════
 * Mapping biorégion québécoise → species_default doctrinal.
 *
 * Source : MFFP 2024 — Inventaires aériens ZEC + Plans de gestion.
 * Doctrine : "lock_species_default_by_bioregion: ENFORCED"
 *            "forbid_cerf_default_in_orignal_bioregion: ENFORCED"
 *
 * RENDU-Ω strict rejette 100% des corridors `cerf` à T1 BSL canonique
 * (segments 21-40m > 20m, angles 63-78° > 45°). Avec `orignal` : 1/20 accepté.
 * D'où le verrou par biorégion : impossible de demander cerf à BSL/Saguenay/Gaspésie.
 *
 * V30_LOCK INVIOLÉ · FUSION ADD-ONLY · ANTI-GÉNÉRIQUE STRICT
 * ════════════════════════════════════════════════════════════════════════
 */

// ═══ MAP BIORÉGIONS QUÉBEC ═══
// Coords latRange/lonRange = [min, max].
// species_default doctrinal selon densités d'inventaires aériens MFFP 2024.
export const QC_BIOREGIONS = Object.freeze([
  Object.freeze({
    id: 'BSL',
    name: 'Bas-Saint-Laurent',
    latRange: [47.0, 49.5],
    lonRange: [-70.0, -66.5],
    species_default: 'orignal',
    forbidden_default: ['cerf'],
    rationale: 'MFFP — Densité orignal 2.5/km² · cerf < 0.1/km² (limites N areal)',
  }),
  Object.freeze({
    id: 'SAGUENAY',
    name: 'Saguenay-Lac-Saint-Jean',
    latRange: [47.5, 50.5],
    lonRange: [-73.5, -69.5],
    species_default: 'orignal',
    forbidden_default: ['cerf'],
    rationale: 'MFFP — Densité orignal 1.8/km² · zone boréale dominante',
  }),
  Object.freeze({
    id: 'GASPESIE',
    name: 'Gaspésie',
    latRange: [48.0, 49.5],
    lonRange: [-67.0, -64.0],
    species_default: 'orignal',
    forbidden_default: ['cerf'],
    rationale: 'MFFP — Densité orignal 3.0/km² · péninsule orignal-pure',
  }),
  Object.freeze({
    id: 'COTE_NORD',
    name: 'Côte-Nord',
    latRange: [49.0, 53.0],
    lonRange: [-72.0, -60.0],
    species_default: 'orignal',
    forbidden_default: ['cerf'],
    rationale: 'MFFP — Boréale taïga · cerf absent',
  }),
  Object.freeze({
    id: 'MAURICIE',
    name: 'Mauricie',
    latRange: [46.0, 48.5],
    lonRange: [-74.5, -71.5],
    species_default: 'orignal',
    forbidden_default: [],
    rationale: 'MFFP — Densité orignal 1.5/km² · cerf 0.5/km²',
  }),
  Object.freeze({
    id: 'ABITIBI',
    name: 'Abitibi-Témiscamingue',
    latRange: [46.5, 50.0],
    lonRange: [-79.5, -76.0],
    species_default: 'orignal',
    forbidden_default: [],
    rationale: 'MFFP — Boréale mixte',
  }),
  Object.freeze({
    id: 'QUEBEC_REGION',
    name: 'Capitale-Nationale (Québec ville)',
    latRange: [46.5, 47.5],
    lonRange: [-72.0, -70.5],
    species_default: 'cerf',
    forbidden_default: [],
    rationale: 'MFFP — Cerf de Virginie urbain-périurbain',
  }),
  Object.freeze({
    id: 'ESTRIE',
    name: 'Estrie',
    latRange: [44.5, 46.0],
    lonRange: [-72.5, -70.5],
    species_default: 'cerf',
    forbidden_default: [],
    rationale: 'MFFP — Densité cerf 8/km² (record provincial sud)',
  }),
  Object.freeze({
    id: 'MONTEREGIE',
    name: 'Montérégie',
    latRange: [44.5, 45.5],
    lonRange: [-74.5, -72.5],
    species_default: 'cerf',
    forbidden_default: [],
    rationale: 'MFFP — Cerf dominant agricole-forestier',
  }),
  Object.freeze({
    id: 'OUTAOUAIS',
    name: 'Outaouais',
    latRange: [45.0, 47.0],
    lonRange: [-77.5, -74.5],
    species_default: 'cerf',
    forbidden_default: [],
    rationale: 'MFFP — Cerf zone tampon Ontario',
  }),
  Object.freeze({
    id: 'LAURENTIDES',
    name: 'Laurentides',
    latRange: [45.5, 47.5],
    lonRange: [-75.5, -73.5],
    species_default: 'orignal',
    forbidden_default: [],
    rationale: 'MFFP — Densité orignal Laurentides nord',
  }),
]);

// ═══ FALLBACK ═══
const QUEBEC_DEFAULT_FALLBACK = Object.freeze({
  id: 'QUEBEC_DEFAULT',
  name: 'Québec (défaut institutionnel)',
  species_default: 'orignal',
  forbidden_default: ['cerf'],
  rationale: 'Fallback BCE-4X · doctrine prioritaire orignal hors zone identifiée',
});

/**
 * Retourne la biorégion correspondant à des coordonnées (lat, lon).
 * @param {number} lat - Latitude WGS84
 * @param {number} lon - Longitude WGS84
 * @returns {{id: string, name: string, species_default: string, forbidden_default: string[], rationale: string, matched: boolean}}
 */
export function getBioregionByCoords(lat, lon) {
  if (!Number.isFinite(lat) || !Number.isFinite(lon)) {
    return { ...QUEBEC_DEFAULT_FALLBACK, matched: false };
  }
  for (const r of QC_BIOREGIONS) {
    if (lat >= r.latRange[0] && lat <= r.latRange[1]
        && lon >= r.lonRange[0] && lon <= r.lonRange[1]) {
      return { ...r, matched: true };
    }
  }
  return { ...QUEBEC_DEFAULT_FALLBACK, matched: false };
}

/**
 * R6 doctrinale : Vérifie si une species est interdite par défaut dans la biorégion.
 * forbid_cerf_default_in_orignal_bioregion: ENFORCED
 */
export function isSpeciesForbiddenAsDefault(species, lat, lon) {
  const bio = getBioregionByCoords(lat, lon);
  return bio.forbidden_default.includes(String(species).toLowerCase());
}

/**
 * Retourne le species_default doctrinal pour des coordonnées donnés.
 * Si une species est passée en input, retourne species si elle n'est pas interdite,
 * sinon retourne le species_default doctrinal de la biorégion.
 */
export function resolveSpeciesByBioregion(lat, lon, requestedSpecies = null) {
  const bio = getBioregionByCoords(lat, lon);
  if (!requestedSpecies || requestedSpecies === 'tous') {
    return { species: bio.species_default, source: 'bioregion_default', bioregion: bio.id };
  }
  const sp = String(requestedSpecies).toLowerCase();
  if (bio.forbidden_default.includes(sp)) {
    return { species: bio.species_default, source: 'bioregion_lock_override', bioregion: bio.id, blocked: sp };
  }
  return { species: sp, source: 'user_choice', bioregion: bio.id };
}

const BIOREGION_API = Object.freeze({
  QC_BIOREGIONS,
  getBioregionByCoords,
  isSpeciesForbiddenAsDefault,
  resolveSpeciesByBioregion,
});

export default BIOREGION_API;

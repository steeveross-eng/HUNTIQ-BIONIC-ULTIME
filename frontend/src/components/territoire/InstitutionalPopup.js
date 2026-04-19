/**
 * InstitutionalPopup.js — ENGINE-FICHE-DESCRIPTIVE-Ω
 * =====================================================
 * Genere le HTML standardise pour les popups double-clic RSE-Ω
 * applicable a TOUTES les couches (zones, corridors, affuts, salines,
 * hotspots, contamination, nutrition, vent).
 */

// Palette de couleur par type institutionnel
const TYPE_PALETTE = {
  Zone: '#2E7D32', Corridor: '#FF6A00', Affut: '#FF9800',
  Saline: '#FDD835', Hotspot: '#E53935', Contamination: '#FF7043',
  Nutrition: '#4CAF50', Vent: '#00E5FF',
};

export function buildInstitutionalPopup({
  type,
  name = '',
  score = null,
  justification = '',
  source = '',
  conformite = '',
  actions = [],
  color = null,
}) {
  const finalColor = color || TYPE_PALETTE[type] || '#FF9800';
  const title = name ? `${type} — ${name}` : type;
  const scoreLine = score !== null ? `<div style="font-weight:700;">Score: ${score}/100</div>` : '';
  const justLine = justification ? `<div style="font-size:11px;color:#555">${justification}</div>` : '';
  const srcLine = source ? `<div style="font-size:10px;color:#888">Source: ${source}</div>` : '';
  const confLine = conformite ? `<div style="font-size:10px;color:#888">Conformite: <b>${conformite}</b></div>` : '';
  const actLine = (actions && actions.length)
    ? `<div style="font-size:10px;color:#444;margin-top:4px;">${actions.join(' | ')}</div>`
    : '';
  const testidType = type.toLowerCase().replace(/[^a-z0-9]/g, '-');
  return `
    <div data-testid="institutional-popup-${testidType}" style="font-family:system-ui;min-width:180px;">
      <div style="color:${finalColor};font-weight:800;border-bottom:1px solid #eee;padding-bottom:4px;margin-bottom:6px;">${title}</div>
      ${scoreLine}
      ${justLine}
      ${srcLine}
      ${confLine}
      ${actLine}
    </div>
  `.trim();
}

// Helpers specifiques par couche
export const FichePopup = {
  zone: (z) => buildInstitutionalPopup({
    type: 'Zone', name: z.type || z.zone_type, score: z.score,
    justification: `Surface: ${(z.polygon || []).length} vertices`,
    source: 'ZONES-V10', conformite: z.excluded ? 'EXCLUE' : 'ACTIVE',
    actions: z.exclusion_reason ? [z.exclusion_reason] : [],
  }),
  corridor: (c) => buildInstitutionalPopup({
    type: 'Corridor', name: (c.type || 'normal').toUpperCase(),
    score: c.intensity || c.score,
    justification: `Chemin ${(c.path || []).length} points | largeur ${c.weight}px`,
    source: 'CORRIDORS-Ω', conformite: c.is_network_link ? 'RESEAU' : 'SINGLE',
    actions: c.nutrition_boost ? [`Nutrition boost: +${c.nutrition_boost}`] : [],
  }),
  affut: (a) => buildInstitutionalPopup({
    type: 'Affut', name: (a.type || 'TEMPORAIRE').replace('_',' '),
    score: a.score_affut_v12 || a.score,
    justification: a.justification || `Corridor ${a.classe_corridor_cible} a ${a.distance_corridor_m}m`,
    source: 'AFFUTS-Ω-V12', conformite: a.affut_repositionne ? 'REPOSITIONNE' : 'CONFORME',
    actions: a.recommandation ? [a.recommandation] : [],
  }),
  saline: (s) => buildInstitutionalPopup({
    type: 'Saline', name: s.statut_institutionnel || 'V11-SUPRA',
    score: s.score_global_v11 || s.score,
    justification: `Bio ${s.score_bio_global || '?'} | Terrain ${s.score_terrain || '?'} | Reseau ${s.score_reseau || '?'}`,
    source: 'SALINES-V11-SUPRA', conformite: s.interdit ? 'INTERDIT' : 'VALIDEE',
    actions: (s.recommandations || []).slice(0, 2),
  }),
  hotspot: (h) => buildInstitutionalPopup({
    type: 'Hotspot', name: h.source_engine || '',
    score: h.intensity_with_nutrition || h.intensity,
    justification: `Intensite ${Math.round(h.intensity || 0)}/100`,
    source: h.source || 'HOTSPOTS-V10', conformite: 'ACTIVE',
    actions: h.nutrition_boost ? [`Nutrition +${h.nutrition_boost}`] : [],
  }),
  contamination: (c) => buildInstitutionalPopup({
    type: 'Contamination', name: 'CONE',
    score: c.intensity || null,
    justification: c.affut_source ? `Source affut ${c.affut_source.lat.toFixed(4)}, ${c.affut_source.lng.toFixed(4)}` : '',
    source: 'CONTAMINATION-Ω', conformite: 'VENT-ACTIF',
    actions: [],
  }),
};

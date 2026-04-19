/**
 * InstitutionalPopup.js — ENGINE-FICHE-DESCRIPTIVE-Ω (placeholder)
 * =================================================================
 * Genere le HTML standardise pour les popups double-clic RSE-Ω.
 */
export function buildInstitutionalPopup({
  type,
  name = '',
  score = null,
  justification = '',
  source = '',
  conformite = '',
  actions = [],
  color = '#FF9800',
}) {
  const title = name ? `${type} — ${name}` : type;
  const scoreLine = score !== null ? `<div style="font-weight:700;">Score: ${score}/100</div>` : '';
  const justLine = justification ? `<div style="font-size:11px;color:#555">${justification}</div>` : '';
  const srcLine = source ? `<div style="font-size:10px;color:#888">Source: ${source}</div>` : '';
  const confLine = conformite ? `<div style="font-size:10px;color:#888">Conformite: <b>${conformite}</b></div>` : '';
  const actLine = (actions && actions.length)
    ? `<div style="font-size:10px;color:#444;margin-top:4px;">${actions.join(' | ')}</div>`
    : '';
  return `
    <div data-testid="institutional-popup-${type.toLowerCase().replace(/[^a-z0-9]/g,'-')}" style="font-family:system-ui;min-width:180px;">
      <div style="color:${color};font-weight:800;border-bottom:1px solid #eee;padding-bottom:4px;margin-bottom:6px;">${title}</div>
      ${scoreLine}
      ${justLine}
      ${srcLine}
      ${confLine}
      ${actLine}
    </div>
  `.trim();
}

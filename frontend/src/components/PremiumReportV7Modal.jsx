/**
 * PremiumReportV7Modal.jsx — TERRITOIRE_V7_PREMIUM_REPORTS_Ω
 * COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU x3 · ANTI_GÉNÉRIQUE_STRICT
 *
 * Modal full-screen pour rapports premium :
 *  · CORE FLOW : ESPÈCE → WAYPOINT → COUCHE → RAPPORT
 *  · 6 BLOCKS doctrinaux (summary, premium modules, ULTIME, recipes,
 *    avant/après, action M16)
 *  · Bouton X (fermeture) + bouton PARTAGER (messaging engine)
 *  · Footer actions (Plan 30j, Export, Comparer, Note, Partager)
 *
 * Ne fabrique PAS de données : toutes les valeurs viennent du backend
 * /api/v30/super-masters/premium-report-generate (anti-générique strict).
 */
import React, { useState, useEffect, useCallback } from 'react';
import { X, Download, Share2, Plus, BarChart3, FileText } from 'lucide-react';

const SPECIES_OPTIONS = [
  { value: 'cerf', label: 'Cerf de Virginie' },
  { value: 'orignal', label: 'Orignal' },
  { value: 'ours', label: 'Ours noir' },
  { value: 'dindon', label: 'Dindon sauvage' },
  { value: 'wapiti', label: 'Wapiti' },
];

const LAYER_OPTIONS = [
  { value: 'saline', label: 'Saline' },
  { value: 'alimentation', label: 'Alimentation' },
  { value: 'rut', label: 'Rut' },
  { value: 'repos', label: 'Repos' },
  { value: 'affut', label: 'Affût' },
  { value: 'corridor', label: 'Corridor' },
];

const SEASONS = ['spring', 'summer', 'autumn', 'winter'];

const BLOCK_TITLES = {
  block_1_summary: 'BLOC 1 — Résumé intelligent',
  block_2_premium_modules: 'BLOC 2 — Modules PREMIUM activés',
  block_3_ultimate_module: 'BLOC 3 — Module ULTIME enrichi',
  block_4_supra_recipes: 'BLOC 4 — Recettes SUPRA personnalisées',
  block_5_before_after: 'BLOC 5 — AVANT / APRÈS',
  block_6_ultimate_action: 'BLOC 6 — Action M16 prioritaire',
};

export const PremiumReportV7Modal = ({
  isOpen,
  onClose,
  initialSpecies = 'cerf',
  initialLayer = 'alimentation',
  waypointLat = 46.8131,
  waypointLon = -71.2075,
  waypointId = null,
  initialSeason = 'summer',
  commandantToken = '',
}) => {
  const [species, setSpecies] = useState(initialSpecies);
  const [layer, setLayer] = useState(initialLayer);
  const [season, setSeason] = useState(initialSeason);
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [shareStatus, setShareStatus] = useState(null);

  const generateReport = useCallback(async () => {
    setLoading(true);
    setError(null);
    setReport(null);
    try {
      const apiUrl = process.env.REACT_APP_BACKEND_URL;
      const resp = await fetch(
        `${apiUrl}/api/v30/super-masters/premium-report-generate`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-Commandant-Token': commandantToken,
          },
          body: JSON.stringify({
            species,
            waypoint_lat: waypointLat,
            waypoint_lon: waypointLon,
            layer,
            season,
            waypoint_id: waypointId,
            radius_m: 500,
          }),
        }
      );
      if (!resp.ok) {
        const errBody = await resp.text();
        throw new Error(`HTTP ${resp.status}: ${errBody.slice(0, 200)}`);
      }
      const data = await resp.json();
      setReport(data.result);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, [species, layer, season, waypointLat, waypointLon, waypointId, commandantToken]);

  useEffect(() => {
    if (isOpen) {
      generateReport();
    }
  }, [isOpen, generateReport]);

  const handleShare = async (channel) => {
    if (!report?.report_sha256) return;
    setShareStatus({ status: 'sending', channel });
    try {
      const apiUrl = process.env.REACT_APP_BACKEND_URL;
      const resp = await fetch(
        `${apiUrl}/api/v30/super-masters/messaging-share`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-Commandant-Token': commandantToken,
          },
          body: JSON.stringify({
            report_sha256: report.report_sha256,
            channel,
            recipient: 'commandant@bce-4x.local',
            subject: `Rapport Premium ${report.subheader_context?.species} ${report.subheader_context?.layer}`,
          }),
        }
      );
      const data = await resp.json();
      setShareStatus({ status: 'sent', channel, response: data.result });
    } catch (e) {
      setShareStatus({ status: 'error', channel, error: e.message });
    }
  };

  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 z-[9999] bg-slate-950/98 backdrop-blur-sm overflow-y-auto"
      data-testid="premium-report-v7-modal"
    >
      {/* Header sticky */}
      <div className="sticky top-0 z-10 bg-gradient-to-r from-slate-900 via-amber-950 to-slate-900 border-b-2 border-amber-500/30 px-6 py-4 flex items-center justify-between">
        <div className="flex-1">
          <div className="text-xs text-amber-400 font-mono uppercase tracking-widest">
            TERRITOIRE V7 · PREMIUM ULTRA · DOCTRINE BCE-4X
          </div>
          <div className="text-lg font-bold text-amber-50 mt-1" data-testid="premium-report-header">
            {report?.header_dynamic || 'RAPPORT PREMIUM — Chargement...'}
          </div>
          {report?.report_sha256 && (
            <div className="text-[10px] text-amber-400/60 font-mono mt-1">
              SHA-256 ANCRÉ: {report.report_sha256.slice(0, 32)}...
            </div>
          )}
        </div>
        <button
          onClick={onClose}
          className="ml-4 p-2 rounded-lg bg-red-500/20 hover:bg-red-500/40 border border-red-500/40 transition-colors"
          data-testid="premium-report-close-button"
          aria-label="Fermer"
        >
          <X className="w-6 h-6 text-red-200" />
        </button>
      </div>

      {/* Selectors */}
      <div className="bg-slate-900/60 px-6 py-3 flex flex-wrap gap-3 border-b border-slate-700/50">
        <Selector
          label="Espèce"
          options={SPECIES_OPTIONS}
          value={species}
          onChange={setSpecies}
          testid="species-selector"
        />
        <Selector
          label="Couche"
          options={LAYER_OPTIONS}
          value={layer}
          onChange={setLayer}
          testid="layer-selector"
        />
        <Selector
          label="Saison"
          options={SEASONS.map(s => ({ value: s, label: s }))}
          value={season}
          onChange={setSeason}
          testid="season-selector"
        />
        <button
          onClick={generateReport}
          className="ml-auto px-4 py-2 bg-amber-500 hover:bg-amber-400 text-slate-900 rounded font-bold transition-colors disabled:opacity-50"
          disabled={loading}
          data-testid="regenerate-report-button"
        >
          {loading ? 'Génération...' : 'Regénérer'}
        </button>
      </div>

      {/* Body */}
      <div className="p-6 max-w-7xl mx-auto space-y-6">
        {error && (
          <div className="bg-red-900/40 border border-red-500/50 rounded-lg p-4 text-red-100" data-testid="error-banner">
            <div className="font-bold mb-1">Erreur de génération</div>
            <div className="text-sm font-mono">{error}</div>
          </div>
        )}

        {loading && !report && (
          <div className="text-center py-20 text-amber-200" data-testid="loading-indicator">
            <div className="text-xl">⌛ Extraction overlays anti-générique...</div>
          </div>
        )}

        {report && (
          <>
            {/* Subheader contexte */}
            <div className="bg-slate-800/60 border border-amber-700/30 rounded-lg p-4" data-testid="subheader-context">
              <div className="text-amber-300 text-xs uppercase tracking-wide mb-2">Contexte écologique</div>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
                <Field label="Espèce" value={report.subheader_context?.scientific_name} />
                <Field label="Couche" value={report.subheader_context?.layer} />
                <Field label="Saison" value={report.subheader_context?.season} />
                <Field label="Waypoint ID" value={report.subheader_context?.waypoint_id} />
                <Field label="Coords" value={`${report.subheader_context?.waypoint_lat?.toFixed(4)}, ${report.subheader_context?.waypoint_lon?.toFixed(4)}`} />
                <Field label="NDVI moyen" value={report.subheader_context?.ndvi_actuel_mean?.toFixed(3)} />
                <Field label="Pression anthrop" value={report.subheader_context?.pression_anthropique} />
                <Field label="Humidité" value={report.subheader_context?.humidite_sensitivity} />
              </div>
            </div>

            {/* BLOC 1 — Summary */}
            <Block title={BLOCK_TITLES.block_1_summary} testid="block-1-summary">
              <Row label="État actuel" value={report.block_1_summary?.etat_actuel} />
              <Row label="Potentiel" value={report.block_1_summary?.potentiel} />
              <Row label="Anomalies" value={report.block_1_summary?.anomalies} />
              <Row label="Opportunités" value={report.block_1_summary?.opportunites} />
              <Row label="SCORE GLOBAL"
                value={`${report.block_1_summary?.score_global ?? 'N/A'} / 100`}
                highlight
              />
            </Block>

            {/* BLOC 2 — Premium Modules */}
            <Block
              title={`${BLOCK_TITLES.block_2_premium_modules} — ${report.block_2_premium_modules?.n_modules_activated}/${report.block_2_premium_modules?.n_modules_total_premium}`}
              testid="block-2-modules"
            >
              <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                {Object.entries(report.block_2_premium_modules?.modules_data || {}).map(([key, val]) => (
                  <ModuleCard key={key} name={key} data={val} />
                ))}
              </div>
            </Block>

            {/* BLOC 3 — ULTIME */}
            <Block
              title={`${BLOCK_TITLES.block_3_ultimate_module} · ${report.block_3_ultimate_module?.ultimate_module_id}`}
              testid="block-3-ultimate"
              highlight
            >
              <div className="text-amber-100 mb-3 text-sm">
                {report.block_3_ultimate_module?.description_detaillee}
              </div>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
                <ScoreCard
                  label="AVANT"
                  value={report.block_3_ultimate_module?.score_avant_recommandations}
                  color="slate"
                />
                <ScoreCard
                  label="APRÈS"
                  value={report.block_3_ultimate_module?.score_apres_recommandations}
                  color="emerald"
                />
                <ScoreCard
                  label="GAIN"
                  value={`+${report.block_3_ultimate_module?.improvement_pct_doctrinal}%`}
                  color="amber"
                />
                <ScoreCard
                  label="HUMIDITÉ"
                  value={report.block_3_ultimate_module?.humidity_sensitivity?.split(' ')[0]}
                  color="cyan"
                />
              </div>
              {/* Mini AVANT/APRÈS Table */}
              <div className="bg-slate-900/60 rounded-lg p-3 mb-3">
                <div className="text-xs text-amber-300 mb-2 uppercase">Tableau comparatif AVANT/APRÈS</div>
                <table className="w-full text-sm">
                  <thead>
                    <tr className="text-amber-400 border-b border-slate-700">
                      <th className="text-left py-1">Métrique</th>
                      <th className="text-right py-1">AVANT</th>
                      <th className="text-right py-1">APRÈS</th>
                      <th className="text-right py-1">Δ%</th>
                    </tr>
                  </thead>
                  <tbody>
                    {Object.entries(
                      report.block_3_ultimate_module?.mini_report_avant_apres?.tableau_comparatif || {}
                    ).map(([metric, vals]) => (
                      <tr key={metric} className="text-slate-200 border-b border-slate-800/50">
                        <td className="py-1">{metric}</td>
                        <td className="text-right">{vals.avant}</td>
                        <td className="text-right">{vals.apres}</td>
                        <td className={`text-right font-bold ${vals.delta_pct >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                          {vals.delta_pct > 0 ? '+' : ''}{vals.delta_pct}%
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              <div className="bg-amber-900/30 border border-amber-500/30 rounded p-3 text-amber-100 text-sm font-medium">
                {report.block_3_ultimate_module?.mini_report_avant_apres?.phrase_impact}
              </div>
            </Block>

            {/* BLOC 4 — Supra Recipes */}
            <Block title={BLOCK_TITLES.block_4_supra_recipes} testid="block-4-recipes">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {(report.block_4_supra_recipes?.by_objective || []).map((recipe, i) => (
                  <div key={i} className="bg-slate-900/40 rounded p-3 border border-slate-700/50">
                    <div className="text-amber-300 font-bold mb-1 uppercase text-xs">
                      {recipe.objective}
                    </div>
                    <ul className="text-sm text-slate-200 space-y-1 list-disc list-inside">
                      {recipe.ingredients_doctrinal?.map((ing, j) => (
                        <li key={j}>{ing}</li>
                      ))}
                    </ul>
                  </div>
                ))}
              </div>
            </Block>

            {/* BLOC 6 — Module 16 ULTIME Action */}
            <Block
              title={BLOCK_TITLES.block_6_ultimate_action}
              testid="block-6-action"
              highlight
            >
              <div className="bg-gradient-to-br from-amber-700 to-red-900 rounded-lg p-4 border border-amber-300/40">
                <div className="text-amber-200 text-xs uppercase tracking-widest mb-1">
                  ACTION PRIORITAIRE — IMPACT MAXIMUM
                </div>
                <div className="text-amber-50 font-bold text-lg" data-testid="ultimate-action-text">
                  {report.block_6_ultimate_action?.module_16_ultimate?.action}
                </div>
              </div>
            </Block>

            {/* Footer */}
            <div className="sticky bottom-0 bg-slate-900/95 backdrop-blur border-t-2 border-amber-500/30 -mx-6 px-6 py-3 flex flex-wrap gap-2 items-center" data-testid="footer-actions">
              <FooterAction icon={Plus} label="Plan 30j" testid="footer-add-plan" />
              <FooterAction icon={Download} label="Export" testid="footer-export" />
              <FooterAction icon={BarChart3} label="Comparer" testid="footer-compare" />
              <FooterAction icon={FileText} label="Note" testid="footer-note" />
              <div className="ml-auto flex gap-2">
                <button
                  onClick={() => handleShare('email')}
                  className="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded text-sm font-bold flex items-center gap-1 disabled:opacity-50"
                  disabled={shareStatus?.status === 'sending'}
                  data-testid="share-email-button"
                >
                  <Share2 className="w-4 h-4" /> Email
                </button>
                <button
                  onClick={() => handleShare('social_media')}
                  className="px-3 py-1.5 bg-blue-600 hover:bg-blue-500 text-white rounded text-sm font-bold flex items-center gap-1 disabled:opacity-50"
                  disabled={shareStatus?.status === 'sending'}
                  data-testid="share-social-button"
                >
                  <Share2 className="w-4 h-4" /> Réseaux
                </button>
                <button
                  onClick={() => handleShare('internal')}
                  className="px-3 py-1.5 bg-amber-600 hover:bg-amber-500 text-white rounded text-sm font-bold flex items-center gap-1 disabled:opacity-50"
                  disabled={shareStatus?.status === 'sending'}
                  data-testid="share-internal-button"
                >
                  <Share2 className="w-4 h-4" /> Interne
                </button>
              </div>
            </div>

            {shareStatus && (
              <div
                className={`fixed bottom-4 right-4 px-4 py-2 rounded shadow-lg z-[10000] ${
                  shareStatus.status === 'error'
                    ? 'bg-red-600 text-white'
                    : 'bg-emerald-600 text-white'
                }`}
                data-testid="share-status-toast"
              >
                {shareStatus.status === 'sending' && `Envoi via ${shareStatus.channel}...`}
                {shareStatus.status === 'sent' && `✓ ${shareStatus.channel} : ${shareStatus.response?.share_status || 'queued'}`}
                {shareStatus.status === 'error' && `Erreur ${shareStatus.channel}: ${shareStatus.error}`}
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
};

const Selector = ({ label, options, value, onChange, testid }) => (
  <label className="text-xs text-slate-300 flex items-center gap-2" data-testid={`${testid}-label`}>
    {label}:
    <select
      value={value}
      onChange={(e) => onChange(e.target.value)}
      className="bg-slate-800 text-amber-100 border border-slate-600 rounded px-2 py-1 text-sm"
      data-testid={testid}
    >
      {options.map(opt => (
        <option key={opt.value} value={opt.value}>{opt.label}</option>
      ))}
    </select>
  </label>
);

const Field = ({ label, value }) => (
  <div className="bg-slate-900/40 rounded p-2">
    <div className="text-[10px] text-amber-400/70 uppercase">{label}</div>
    <div className="text-sm text-slate-100 font-mono mt-0.5">{value ?? 'N/A'}</div>
  </div>
);

const Row = ({ label, value, highlight = false }) => (
  <div className={`flex flex-col md:flex-row md:items-baseline gap-2 py-1 ${highlight ? 'bg-amber-900/20 -mx-2 px-2 rounded font-bold' : ''}`}>
    <div className={`text-xs uppercase ${highlight ? 'text-amber-300' : 'text-slate-400'} md:w-32 flex-shrink-0`}>
      {label}
    </div>
    <div className={`text-sm ${highlight ? 'text-amber-100' : 'text-slate-200'}`}>
      {value || 'N/A'}
    </div>
  </div>
);

const Block = ({ title, children, highlight = false, testid }) => (
  <section
    className={`rounded-lg border p-4 ${highlight ? 'bg-amber-950/40 border-amber-500/40' : 'bg-slate-800/50 border-slate-700/50'}`}
    data-testid={testid}
  >
    <h2 className={`text-base font-bold mb-3 uppercase tracking-wide ${highlight ? 'text-amber-300' : 'text-amber-200'}`}>
      {title}
    </h2>
    <div>{children}</div>
  </section>
);

const ModuleCard = ({ name, data }) => {
  const value = data?.value;
  const display = value !== null && value !== undefined
    ? typeof value === 'number'
      ? value.toFixed(2)
      : typeof value === 'object'
        ? 'OK'
        : String(value).slice(0, 40)
    : 'pending';
  return (
    <div className="bg-slate-900/40 rounded p-2 border border-slate-700/50" data-testid={`module-${name}`}>
      <div className="text-[10px] text-amber-400/70 uppercase">{name}</div>
      <div className={`text-sm font-bold mt-0.5 ${value !== null && value !== undefined ? 'text-amber-100' : 'text-slate-500'}`}>
        {display}
      </div>
      {data?.regime && (
        <div className="text-[10px] text-slate-400 mt-0.5">{data.regime}</div>
      )}
    </div>
  );
};

const ScoreCard = ({ label, value, color }) => {
  const colorClasses = {
    slate: 'bg-slate-700 text-slate-100',
    emerald: 'bg-emerald-700 text-emerald-50',
    amber: 'bg-amber-700 text-amber-50',
    cyan: 'bg-cyan-800 text-cyan-50',
  }[color] || 'bg-slate-700';
  return (
    <div className={`${colorClasses} rounded-lg p-3 text-center`}>
      <div className="text-[10px] uppercase tracking-wide opacity-70">{label}</div>
      <div className="text-2xl font-bold mt-1">{value ?? 'N/A'}</div>
    </div>
  );
};

const FooterAction = ({ icon: Icon, label, testid }) => (
  <button
    className="px-3 py-1.5 bg-slate-700 hover:bg-slate-600 text-slate-100 rounded text-sm flex items-center gap-1"
    data-testid={testid}
  >
    <Icon className="w-4 h-4" /> {label}
  </button>
);

export default PremiumReportV7Modal;

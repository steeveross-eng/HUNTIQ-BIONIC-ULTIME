/**
 * SUPRA v2 — ComparezTab (Module Autonome R3.7)
 * ================================================
 * Extrait de NutritionPointDetailPanel.jsx — Phase R3.7
 * BCE-4X ULTIME ABSOLU / STEEVE-MAX
 *
 * AUCUNE MODIFICATION SANS AUTORISATION COMMANDANT
 * ZERO AJOUT | ZERO SUPPRESSION | EXTRACTION PURE
 */
import React from 'react';
import { Scale } from 'lucide-react';
import { BIONIC, GoldenCard } from './constants';
import IconCircle from '../ui/IconCircle';

// ============================================================
// TAB: COMPAREZ — 3 COLONNES GOLDEN — BCE-4X STEEVE-MAX
// ============================================================
const ComparezTab = ({ products, compareIds, gc, toggleCompare }) => {
  const compared = (products.products || []).filter(p => compareIds.includes(p.product_id));

  const IC = IconCircle;

  if (compared.length === 0) {
    return (
      <div className="text-center py-12" data-testid="supra-comparez-tab">
        <div className="grid grid-cols-3 gap-1.5">
          <div />
          <GoldenCard testId="compare-empty" accentColor={BIONIC.blue} compact>
            <div className="text-center py-6">
              <IC Icon={Scale} color={BIONIC.blue} sz={40} />
              <div className="text-[16px] text-gray-300 font-semibold mt-3">Aucun produit selectionne</div>
              <div className="text-[14px] text-gray-500 mt-1">Allez dans INTELLIGENCE et selectionnez 2-4 produits</div>
            </div>
          </GoldenCard>
          <div />
        </div>
      </div>
    );
  }

  const best = compared.reduce((a, b) => a.score_global > b.score_global ? a : b);

  // Pad to exactly 3 columns
  const padded = [...compared];
  while (padded.length < 3) padded.push(null);

  return (
    <div className="space-y-1.5" data-testid="supra-comparez-tab">
      {/* Header GOLDEN */}
      <GoldenCard testId="compare-header" accentColor={BIONIC.blue} compact>
        <div className="flex items-center gap-3">
          <IC Icon={Scale} color={BIONIC.blue} />
          <span className="text-[16px] font-bold text-white">Comparaison</span>
          <span className="text-[14px] font-semibold px-2 py-0.5 rounded-lg ml-auto" style={{ backgroundColor: `${BIONIC.blue}18`, color: BIONIC.blue }}>{compared.length} produit(s)</span>
        </div>
      </GoldenCard>

      {/* GRILLE 3 COLONNES — RÉPLIQUE DASHBOARD */}
      <div className="grid grid-cols-3 gap-1.5" data-testid="compare-3col-grid">
        {padded.slice(0, 3).map((p, idx) => {
          if (!p) return <div key={`empty-${idx}`} />;
          const isBest = p.product_id === best.product_id;
          const sc = p.score_global >= 85 ? BIONIC.green : p.score_global >= 70 ? BIONIC.yellow : p.score_global >= 50 ? BIONIC.orange : BIONIC.red;
          return (
            <GoldenCard key={p.product_id} testId={`compare-card-${p.product_id}`} accentColor={isBest ? BIONIC.green : sc} compact>
              {isBest && <div className="text-[14px] font-bold text-center mb-2" style={{ color: BIONIC.green }}>MEILLEUR CHOIX</div>}
              <div className="text-center mb-3">
                <div className="w-[56px] h-[56px] rounded-xl flex items-center justify-center mx-auto" style={{ background: `linear-gradient(135deg, ${sc}30, ${sc}10)` }}>
                  <span className="text-[30px] font-black tabular-nums" style={{ color: sc }}>{p.score_global}</span>
                </div>
                <div className="text-[16px] font-bold text-white mt-2">{p.name}</div>
                <div className="text-[14px] text-gray-400">{p.type}</div>
              </div>
              <div className="space-y-1.5">
                {[
                  { label: 'Espece', val: `${p.score_species}%`, c: p.score_species >= 85 ? BIONIC.green : BIONIC.orange },
                  { label: 'Saison', val: `${p.score_season}%`, c: p.score_season >= 85 ? BIONIC.green : BIONIC.orange },
                  { label: 'Sol', val: `${p.score_soil}%`, c: p.score_soil >= 85 ? BIONIC.green : BIONIC.orange },
                  { label: 'Prix', val: `${p.price_cad}$`, c: 'white' },
                  { label: 'Poids', val: `${p.weight_kg}kg`, c: 'white' },
                ].map((row, i) => (
                  <div key={i} className="flex justify-between py-0.5">
                    <span className="text-[14px] text-gray-400">{row.label}</span>
                    <span className="text-[16px] font-bold" style={{ color: row.c }}>{row.val}</span>
                  </div>
                ))}
              </div>
              {/* Mini-bars pour les 3 scores */}
              <div className="space-y-1.5 mt-2">
                {[
                  { l: 'Espece', v: p.score_species, c: p.score_species >= 85 ? BIONIC.green : BIONIC.orange },
                  { l: 'Saison', v: p.score_season, c: p.score_season >= 85 ? BIONIC.green : BIONIC.orange },
                  { l: 'Sol', v: p.score_soil, c: p.score_soil >= 85 ? BIONIC.green : BIONIC.orange },
                ].map((bar, i) => (
                  <div key={i} className="flex items-center gap-2">
                    <span className="text-[14px] text-slate-500 w-12">{bar.l}</span>
                    <div className="flex-1 h-[6px] rounded-full overflow-hidden" style={{ backgroundColor: 'rgba(255,255,255,0.06)' }}>
                      <div className="h-full rounded-full" style={{ width: `${bar.v}%`, backgroundColor: bar.c }} />
                    </div>
                  </div>
                ))}
              </div>
              <button onClick={() => toggleCompare(p.product_id)}
                className="w-full mt-3 text-[14px] font-bold py-2 rounded-lg transition-all"
                style={{ backgroundColor: `${BIONIC.red}15`, color: BIONIC.red }}
                data-testid={`compare-remove-${p.product_id}`}>
                Retirer
              </button>
            </GoldenCard>
          );
        })}
      </div>
    </div>
  );
};

export default ComparezTab;

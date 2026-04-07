/**
 * SUPRA v2 — AnalyseTab (Module Autonome R3.2)
 * ==============================================
 * Extrait de NutritionPointDetailPanel.jsx — Phase R3.2
 * BCE-4X ULTIME ABSOLU x3 / STEEVE-MAX
 *
 * AUCUNE MODIFICATION SANS AUTORISATION COMMANDANT
 * ZERO AJOUT | ZERO SUPPRESSION | EXTRACTION PURE
 */
import React from 'react';
import {
  Droplets, FlaskConical, Leaf, Mountain, Activity, Zap,
  BookOpen, DollarSign, Crown, Eye, TreeDeciduous, FileText,
} from 'lucide-react';
import {
  BIONIC, GoldenCard, GaugeMini,
  PHYSIOLOGY_DATA, MALE_BEHAVIOR, SUPPORT_HIERARCHY,
  zoneColor, priorityColor,
} from './constants';
import IconCircle from '../ui/IconCircle';
import PedagogieModule from '../PedagogieModule';

// ============================================================
// TAB: ANALYSE — GRILLE 3 COLONNES RÉPLIQUE DASHBOARD BIONIC™
// Score + Gauge | 4 Moteurs | Minéraux + Besoins + Recette + Coûts
// BCE-4X STEEVE-MAX — STANDARD GOLDEN — DENSITÉ MAXIMALE
// ============================================================
const AnalyseTab = ({ score, recipe, recommendations, evidence, costs, comparison, ecozone, energyProtein, terrainSolutions, gc, np, engines, ultraScore, ultraDeficits, species, season, soilData }) => {
  const needColor = (level) => {
    if (level === 'EXTREME' || level === 'CRITIQUE') return BIONIC.red;
    if (level === 'TRES ELEVE' || level === 'ELEVE') return BIONIC.orange;
    if (level === 'MODERE') return BIONIC.yellow;
    return BIONIC.green;
  };
  const physioText = PHYSIOLOGY_DATA[species]?.[season] || PHYSIOLOGY_DATA.chevreuil?.printemps;
  const behaviorText = MALE_BEHAVIOR[species]?.[season] || MALE_BEHAVIOR.chevreuil?.printemps;
  const ratingColor = { premium: BIONIC.amber, optimal: BIONIC.green, adequat: BIONIC.blue, insuffisant: BIONIC.red }[ultraScore.rating] || BIONIC.blue;

  const IC = IconCircle;

  return (
    <div className="space-y-1.5" data-testid="supra-analyse-tab">
      {/* ═══════════════════════════════════════════════════════
          GUIDE PRO — BCE-4X GOLDEN V6+
          POSITIONNEMENT PRIORITAIRE — EN TETE DE HIERARCHIE
          COMMANDANT STEEVE-MAX
          ═══════════════════════════════════════════════════════ */}
      <PedagogieModule species={species} season={season} score={score} gc={gc} />

      {/* ═══════════════════════════════════════════════════════
          GRILLE 3 COLONNES — RÉPLIQUE EXACTE DASHBOARD BIONIC™
          Densité GOLDEN V9 | Gaps eliminés | BCE-4X
          ═══════════════════════════════════════════════════════ */}
      <div className="grid grid-cols-3 gap-1.5" data-testid="supra-3col-grid">

        {/* ══════════ COLONNE 1: Score + Gauge + Ecozone ══════════ */}
        <div className="space-y-1.5" data-testid="supra-col-1">
          {/* Score SUPRA */}
          <GoldenCard testId="supra-score-card" accentColor={gc} compact>
            <div className="flex items-center gap-3">
              <div className="w-[48px] h-[48px] rounded-xl flex items-center justify-center flex-shrink-0" style={{ background: `linear-gradient(135deg, ${gc}30, ${gc}10)` }}>
                <span className="text-[30px] font-black tabular-nums" style={{ color: gc }}>{score.score_global}</span>
              </div>
              <div className="min-w-0">
                <div className="text-[16px] font-black text-white">Score SUPRA</div>
                <div className="flex items-center gap-1.5 mt-0.5">
                  <span className="text-[14px] font-bold px-2 py-0.5 rounded-lg" style={{ backgroundColor: `${gc}20`, color: gc }}>{score.grade}</span>
                  {score.score_source === 'SUPRA_UNIFIED' && <span className="text-[10px] font-bold px-1.5 py-0.5 rounded" style={{ backgroundColor: '#00BCD415', color: '#00BCD4' }}>UNIFIE</span>}
                </div>
              </div>
            </div>
            <div className="flex items-center gap-3 mt-2">
              <span className="text-[14px] font-semibold" style={{ color: BIONIC.green }}>{score.zones_resume?.vert} vert</span>
              <span className="text-[14px] font-semibold" style={{ color: BIONIC.orange }}>{score.zones_resume?.jaune} jaune</span>
              <span className="text-[14px] font-semibold" style={{ color: BIONIC.red }}>{score.zones_resume?.rouge} rouge</span>
            </div>
            {score.score_mineral != null && (
              <div className="flex items-center justify-between mt-1.5 pt-1.5 border-t" style={{ borderColor: 'rgba(255,255,255,0.06)' }}>
                <span className="text-[12px] text-slate-500">Score mineral</span>
                <span className="text-[14px] font-bold" style={{ color: BIONIC.purple }}>{score.score_mineral}/100</span>
              </div>
            )}
          </GoldenCard>

          {/* Gauge ULTRA */}
          <GoldenCard testId="ultra-gauge-card" accentColor={ratingColor} compact>
            <div className="flex items-center gap-3">
              <GaugeMini value={ultraScore.global_score || score.score_global || 0} label="ULTRA" color={ratingColor} />
              <div>
                <div className="text-[14px] font-bold text-white">7 Moteurs ULTRA</div>
                <div className="text-[30px] font-black leading-none" style={{ color: ratingColor }}>{(ultraScore.rating || 'N/A').toUpperCase()}</div>
                {ultraDeficits.total_critical > 0 && (
                  <div className="text-[14px] text-red-400">{ultraDeficits.total_critical} carences</div>
                )}
              </div>
            </div>
          </GoldenCard>

          {/* Ecozone */}
          {ecozone && (
            <GoldenCard testId="supra-ecozone-card" accentColor={BIONIC.green} compact>
              <div className="flex items-center gap-2 mb-1">
                <IC Icon={Leaf} color={BIONIC.green} />
                <span className="text-[16px] font-bold text-white">Ecozone</span>
              </div>
              <div className="text-[16px] text-gray-300 font-semibold">{ecozone.nom_commun}</div>
              <div className="text-[14px] text-gray-400 mt-1 leading-snug">{ecozone.habitat_principal}</div>
            </GoldenCard>
          )}

          {/* Besoins nutritionnels */}
          {energyProtein && (
            <GoldenCard testId="supra-energy-protein-card" accentColor={BIONIC.orange} compact>
              <div className="flex items-center gap-2 mb-2">
                <IC Icon={Zap} color={BIONIC.orange} />
                <span className="text-[16px] font-bold text-white">Besoins</span>
              </div>
              <div className="text-[14px] text-gray-400 mb-1.5">{energyProtein.phase}</div>
              <div className="rounded-lg px-3 py-2 mb-1.5" style={{ backgroundColor: 'rgba(255,255,255,0.04)', borderLeft: `4px solid ${needColor(energyProtein.energy_need)}` }}>
                <div className="flex justify-between">
                  <span className="text-[14px] text-gray-400">Energie</span>
                  <span className="text-[16px] font-bold" style={{ color: needColor(energyProtein.energy_need) }}>{energyProtein.energy_need}</span>
                </div>
              </div>
              <div className="rounded-lg px-3 py-2" style={{ backgroundColor: 'rgba(255,255,255,0.04)', borderLeft: `4px solid ${needColor(energyProtein.protein_need)}` }}>
                <div className="flex justify-between">
                  <span className="text-[14px] text-gray-400">Proteines</span>
                  <span className="text-[16px] font-bold" style={{ color: needColor(energyProtein.protein_need) }}>{energyProtein.protein_need}</span>
                </div>
              </div>
            </GoldenCard>
          )}
        </div>

        {/* ══════════ COLONNE 2: 4 Moteurs ULTRA ══════════ */}
        <div className="space-y-1.5" data-testid="supra-col-2">
          {(engines.soil || soilData) && (
            <GoldenCard testId="info-card-sol" accentColor={BIONIC.amber} compact>
              <div className="flex items-center gap-2 mb-2">
                <IC Icon={Mountain} color={BIONIC.amber} />
                <span className="text-[16px] font-bold text-white">Sol — Analyse pedologique</span>
                {soilData?.grade && <span className="text-[14px] font-bold px-2 py-0.5 rounded-lg ml-auto" style={{ backgroundColor: soilData.grade === 'S' || soilData.grade === 'A' ? `${BIONIC.green}18` : soilData.grade === 'B' ? `${BIONIC.orange}18` : `${BIONIC.red}18`, color: soilData.grade === 'S' || soilData.grade === 'A' ? BIONIC.green : soilData.grade === 'B' ? BIONIC.orange : BIONIC.red }}>{soilData.grade} — {soilData.score}/100</span>}
              </div>
              {soilData ? (
                <>
                  {[{ l: 'Type', v: soilData.soil_name }, { l: 'Classe', v: soilData.soil_class }, { l: 'Retention min.', v: `${soilData.metrics?.retention_mineraux}/100` }, { l: 'Drainage', v: `${soilData.metrics?.drainage_naturel}/100` }, { l: 'Lessivage', v: `${soilData.metrics?.risque_lessivage}/100` }, { l: 'Portance', v: `${soilData.metrics?.capacite_portance}/100` }, { l: 'pH', v: soilData.metrics?.ph_typique }, { l: 'Profondeur', v: `${soilData.metrics?.profondeur_cm} cm` }, { l: 'Mat. org.', v: `${soilData.metrics?.matiere_organique_pct}%` }].map((r, i) => (
                    <div key={i} className="flex justify-between py-0.5">
                      <span className="text-[14px] text-slate-400">{r.l}</span>
                      <span className="text-[16px] font-semibold text-white">{r.v || '—'}</span>
                    </div>
                  ))}
                  <div className="mt-2 rounded-lg px-3 py-2" style={{ backgroundColor: '#0F172A' }}>
                    <p className="text-[14px] text-slate-300 leading-relaxed">{soilData.description}</p>
                  </div>
                  <div className="mt-2">
                    <span className="text-[14px] text-slate-500">Texture: Argile {soilData.texture?.argile_pct}% | Sable {soilData.texture?.sable_pct}% | Limon {soilData.texture?.limon_pct}%</span>
                  </div>
                </>
              ) : (
                <>
                  {[{ l: 'Type', v: engines.soil?.soil_type }, { l: 'pH', v: engines.soil?.pH }, { l: 'Qualite', v: `${engines.soil?.quality_index || 0}/100` }].map((r, i) => (
                    <div key={i} className="flex justify-between py-0.5">
                      <span className="text-[14px] text-slate-400">{r.l}</span>
                      <span className="text-[16px] font-semibold text-white">{r.v || '—'}</span>
                    </div>
                  ))}
                </>
              )}
            </GoldenCard>
          )}
          {engines.metabolism && (
            <GoldenCard testId="info-card-metabolisme" accentColor={BIONIC.orange} compact>
              <div className="flex items-center gap-2 mb-2">
                <IC Icon={Activity} color={BIONIC.orange} />
                <span className="text-[16px] font-bold text-white">Metabolisme</span>
              </div>
              {[{ l: 'Phase', v: (engines.metabolism.metabolic_phase || '').replace(/_/g, ' ') }, { l: 'Energie', v: `x${engines.metabolism.energy_demand_factor || 0}` }, { l: 'Activite', v: engines.metabolism.activity_level }].map((r, i) => (
                <div key={i} className="flex justify-between py-0.5">
                  <span className="text-[14px] text-slate-400">{r.l}</span>
                  <span className="text-[16px] font-semibold text-white">{r.v || '—'}</span>
                </div>
              ))}
            </GoldenCard>
          )}
          {/* Vegetation + Hydrologie — BCE-4X: cote a cote pour equilibre visuel */}
          <div className="grid grid-cols-2 gap-1.5">
          {engines.vegetation && (
            <GoldenCard testId="info-card-vegetation" accentColor={BIONIC.green} compact>
              <div className="flex items-center gap-2 mb-2">
                <IC Icon={Leaf} color={BIONIC.green} />
                <span className="text-[16px] font-bold text-white">Vegetation</span>
              </div>
              {[{ l: 'Phase', v: engines.vegetation.phenophase }, { l: 'Couvert', v: `${engines.vegetation.couvert_pct || 0}%` }, { l: 'Fourrage', v: `${((engines.vegetation.avg_forage_quality || 0) * 100).toFixed(0)}%` }].map((r, i) => (
                <div key={i} className="flex justify-between py-0.5">
                  <span className="text-[14px] text-slate-400">{r.l}</span>
                  <span className="text-[16px] font-semibold text-white">{r.v || '—'}</span>
                </div>
              ))}
            </GoldenCard>
          )}
          {engines.hydrology && (
            <GoldenCard testId="info-card-hydrologie" accentColor={BIONIC.blue} compact>
              <div className="flex items-center gap-2 mb-2">
                <IC Icon={Droplets} color={BIONIC.blue} />
                <span className="text-[16px] font-bold text-white">Hydrologie</span>
              </div>
              {[{ l: 'Drainage', v: engines.hydrology.drainage }, { l: 'Lessivage', v: engines.hydrology.leaching_risk }, { l: 'Dist. eau', v: `${engines.hydrology.distance_eau_m || 0}m` }].map((r, i) => (
                <div key={i} className="flex justify-between py-0.5">
                  <span className="text-[14px] text-slate-400">{r.l}</span>
                  <span className="text-[16px] font-semibold text-white">{r.v || '—'}</span>
                </div>
              ))}
            </GoldenCard>
          )}
          </div>
        </div>

        {/* ══════════ COLONNE 3: Minéraux + Recette + Coûts ══════════ */}
        <div className="space-y-1.5" data-testid="supra-col-3">
          {/* Mineraux — mini-bars */}
          <GoldenCard testId="supra-minerals-card" accentColor="#f5a623" compact>
            <div className="flex items-center gap-2 mb-2">
              <IC Icon={FlaskConical} color="#f5a623" />
              <span className="text-[16px] font-bold text-white">Mineraux</span>
            </div>
            <div className="space-y-1.5">
              {Object.entries(score.scores_par_mineral || {}).map(([key, m]) => (
                <div key={key} className="flex items-center gap-2" data-testid={`supra-mineral-${key}`}>
                  <span className="text-[14px] text-slate-400 w-[60px] flex-shrink-0 truncate">{m.name}</span>
                  <div className="flex-1 h-[6px] rounded-full overflow-hidden" style={{ backgroundColor: 'rgba(255,255,255,0.06)' }}>
                    <div className="h-full rounded-full" style={{ width: `${m.score}%`, backgroundColor: zoneColor(m.zone) }} />
                  </div>
                  <span className="text-[16px] font-bold w-8 text-right tabular-nums" style={{ color: zoneColor(m.zone) }}>{m.score}</span>
                </div>
              ))}
            </div>
          </GoldenCard>

          {/* Recette */}
          {recipe && (
            <GoldenCard testId="supra-recipe-card" accentColor={BIONIC.green} compact>
              <div className="flex items-center gap-2 mb-2">
                <IC Icon={BookOpen} color={BIONIC.green} />
                <span className="text-[16px] font-bold text-white">Recette</span>
              </div>
              {recipe.ingredients_cles?.slice(0, 4).map((ing, i) => (
                <div key={i} className="flex items-center justify-between py-1 border-b" style={{ borderColor: 'rgba(255,255,255,0.04)' }}>
                  <div className="min-w-0 flex-1">
                    <span className="text-[14px] text-white">{ing.mineral}</span>
                    <span className="text-[14px] text-gray-500 ml-1">{ing.product}</span>
                  </div>
                  <span className="text-[14px] font-bold px-1.5 py-0.5 rounded-lg flex-shrink-0" style={{ backgroundColor: `${priorityColor(ing.priority)}15`, color: priorityColor(ing.priority) }}>{ing.priority}</span>
                </div>
              ))}
            </GoldenCard>
          )}

          {/* Couts */}
          {costs && (
            <GoldenCard testId="supra-costs-card" accentColor={BIONIC.orange} compact>
              <div className="flex items-center gap-2 mb-2">
                <IC Icon={DollarSign} color={BIONIC.orange} />
                <span className="text-[16px] font-bold text-white">Couts</span>
              </div>
              {[{ l: 'Initial', v: `${costs.initial_cost_cad}$`, c: 'white' }, { l: 'Annuel', v: `${costs.annual_cost_cad}$`, c: BIONIC.orange }, { l: 'Par visite', v: `${costs.cost_per_visit_cad}$`, c: 'white' }].map((r, i) => (
                <div key={i} className="flex justify-between py-0.5">
                  <span className="text-[14px] text-gray-400">{r.l}</span>
                  <span className="text-[16px] font-bold" style={{ color: r.c }}>{r.v}</span>
                </div>
              ))}
            </GoldenCard>
          )}
        </div>
      </div>

      {/* ═══ Sections PREMIUM — intégrées grille 3 colonnes — STANDARD GOLDEN ═══ */}
      <div className="grid grid-cols-3 gap-2 mt-1.5" data-testid="supra-premium-grid">
        <GoldenCard testId="supra-physiology" accentColor={BIONIC.purple} compact>
          <div className="flex items-center gap-2 mb-1.5">
            <IC Icon={Crown} color={BIONIC.purple} sz={24} />
            <span className="text-[13px] font-bold text-white">Physiologie</span>
            <span className="text-[10px] font-bold px-1.5 py-0.5 rounded ml-auto" style={{ backgroundColor: `${BIONIC.purple}15`, color: BIONIC.purple }}>{species}</span>
          </div>
          <p className="text-[11px] text-slate-400 leading-snug line-clamp-4">{physioText}</p>
        </GoldenCard>
        <GoldenCard testId="supra-behavior" accentColor={BIONIC.cyan} compact>
          <div className="flex items-center gap-2 mb-1.5">
            <IC Icon={Eye} color={BIONIC.cyan} sz={24} />
            <span className="text-[13px] font-bold text-white">Comportement males</span>
            <span className="text-[10px] font-bold px-1.5 py-0.5 rounded ml-auto" style={{ backgroundColor: `${BIONIC.cyan}15`, color: BIONIC.cyan }}>{season}</span>
          </div>
          <p className="text-[11px] text-slate-400 leading-snug line-clamp-4">{behaviorText}</p>
        </GoldenCard>
        <GoldenCard testId="supra-support" accentColor={BIONIC.green} compact>
          <div className="flex items-center gap-2 mb-1.5">
            <IC Icon={TreeDeciduous} color={BIONIC.green} sz={24} />
            <span className="text-[13px] font-bold text-white">Support</span>
            <span className="text-[10px] font-bold px-1.5 py-0.5 rounded ml-auto" style={{ backgroundColor: `${BIONIC.green}15`, color: BIONIC.green }}>Hierarchie</span>
          </div>
          <div className="space-y-0.5">
            {SUPPORT_HIERARCHY.map((s, i) => (
              <div key={i} className="flex items-center justify-between">
                <span className="text-[11px] text-slate-400 truncate">{s.name}</span>
                <span className="text-[12px] font-bold tabular-nums" style={{ color: s.color }}>{s.score}</span>
              </div>
            ))}
          </div>
        </GoldenCard>
      </div>

      {evidence.length > 0 && (
        <div className="mt-1.5">
          <GoldenCard testId="supra-evidence" accentColor={BIONIC.purple} compact>
            <div className="flex items-center gap-2 mb-1.5">
              <IC Icon={FileText} color={BIONIC.purple} sz={24} />
              <span className="text-[13px] font-bold text-white">Sources scientifiques</span>
              <span className="text-[10px] font-bold px-1.5 py-0.5 rounded ml-auto" style={{ backgroundColor: `${BIONIC.purple}15`, color: BIONIC.purple }}>{evidence.length} refs</span>
            </div>
            <div className="flex flex-wrap gap-1.5">
              {evidence.slice(0, 4).map((ref, i) => (
                <span key={i} className="text-[10px] text-slate-400 px-1.5 py-0.5 rounded" style={{ backgroundColor: 'rgba(255,255,255,0.04)' }}>{ref.auteurs} ({ref.annee})</span>
              ))}
            </div>
          </GoldenCard>
        </div>
      )}
    </div>
  );
};

export default AnalyseTab;

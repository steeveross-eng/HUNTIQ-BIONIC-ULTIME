/**
 * SUPRA v2 — FicheTab (Module Autonome R3.4)
 * =============================================
 * Extrait de NutritionPointDetailPanel.jsx — Phase R3.4
 * BCE-4X ULTIME ABSOLU x3 / STEEVE-MAX
 *
 * Contient: FICHE_SCORES, FicheGradeTag, FicheTab
 * AUCUNE MODIFICATION SANS AUTORISATION COMMANDANT
 * ZERO AJOUT | ZERO SUPPRESSION | EXTRACTION PURE
 */
import React, { useState } from 'react';
import {
  MapPin, TreeDeciduous, Shield, DollarSign, Mountain,
  BookOpen, Droplets, ChevronDown, ChevronUp, Info,
} from 'lucide-react';
import { BIONIC, GoldenCard } from './constants';
import IconCircle from '../ui/IconCircle';
import { CriteriaDetailModal } from '../ui/CriteriaDetailModal';

// ============================================================
// TAB: FICHE — SALINES ULTIME (5 Scores + 20 Sources + Guides)
// 100% VERTICAL | COMPACT GOLDEN | BCE-4X STEEVE-MAX
// ============================================================
const FICHE_SCORES = [
  { key: 'logistique', label: 'Logistique', icon: MapPin, color: '#3b82f6' },
  { key: 'gros_males', label: 'Gros Males', icon: TreeDeciduous, color: '#22c55e' },
  { key: 'strategique', label: 'Strategique', icon: Shield, color: '#f59e0b' },
  { key: 'cout_roi', label: 'Retour sur Investissement', icon: DollarSign, color: '#a855f7' },
  { key: 'tcs', label: 'Terrain — Conditions Structurelles', icon: Mountain, color: '#ef4444' },
];

const FicheGradeTag = ({ grade, color }) => {
  const colors = { S: '#f59e0b', A: '#22c55e', B: '#3b82f6', C: '#f97316', D: '#ef4444', F: '#991b1b' };
  const c = colors[grade] || color || '#6b7280';
  return <span className="px-2 py-0.5 text-[10px] font-black rounded" style={{ backgroundColor: `${c}20`, color: c, border: `1px solid ${c}40` }}>{grade}</span>;
};

const FicheTab = ({ ficheData, species, season, lat, lng, np, soilData }) => {
  const [showSources, setShowSources] = useState(false);
  const [selectedCriteria, setSelectedCriteria] = useState(null);
  const [selectedCriteriaValue, setSelectedCriteriaValue] = useState(null);

  const openCriteria = (key, value) => {
    setSelectedCriteria(key);
    setSelectedCriteriaValue(value);
  };

  if (!ficheData) {
    return (
      <div className="text-center py-8 space-y-2" data-testid="fiche-loading">
        <Droplets className="h-6 w-6 text-cyan-400 mx-auto" />
        <div className="text-slate-300 text-[16px] font-semibold">FICHE SALINE ULTIME</div>
        <div className="text-slate-500 text-[16px]">Chargement des 5 scores...</div>
      </div>
    );
  }

  const { global_score, scores, scientific_sources } = ficheData;

  const IC = IconCircle;

  // Composant de sous-critère CLIQUABLE avec hyperlien
  const CriteriaRow = ({ criteriaKey, criteriaValue }) => (
    <button
      onClick={() => openCriteria(criteriaKey, criteriaValue)}
      className="w-full flex items-center justify-between py-1 px-1 rounded-lg cursor-pointer transition-all hover:bg-white/5 group"
      data-testid={`criteria-link-${criteriaKey.replace(/[\s_]/g, '-')}`}
      title={`Cliquez pour voir la fiche complete: ${criteriaKey.replace(/_/g, ' ')}`}
    >
      <span className="text-[14px] text-slate-400 group-hover:text-cyan-400 transition-colors flex items-center gap-1.5">
        <Info className="h-3 w-3 opacity-0 group-hover:opacity-100 transition-opacity" style={{ color: '#00BCD4' }} />
        {criteriaKey.replace(/_/g, ' ')}
      </span>
      <span className="text-[16px] text-white font-medium group-hover:text-cyan-300 transition-colors underline decoration-dotted decoration-slate-600 group-hover:decoration-cyan-500">{criteriaValue.value}</span>
    </button>
  );

  return (
    <div className="space-y-1.5" data-testid="supra-fiche-tab">
      {/* Modal fiche explicative — GUIDE BIONIC NIVEAU PROFESSIONNEL */}
      {selectedCriteria && (
        <CriteriaDetailModal
          criteriaKey={selectedCriteria}
          criteriaValue={selectedCriteriaValue}
          species={species}
          season={season}
          onClose={() => { setSelectedCriteria(null); setSelectedCriteriaValue(null); }}
        />
      )}
      {/* ═══ Score Global FICHE — STANDARD GOLDEN pleine largeur ═══ */}
      <GoldenCard testId="fiche-global-score" accentColor="#00BCD4" compact>
        <div className="flex items-center gap-4">
          <div className="w-[48px] h-[48px] rounded-xl flex items-center justify-center flex-shrink-0" style={{ background: 'linear-gradient(135deg, #00BCD430, #00BCD410)' }}>
            <span className="text-[30px] font-black text-cyan-400">{global_score.score}</span>
          </div>
          <div className="min-w-0">
            <div className="text-[16px] font-black text-white">FICHE SALINE ULTIME</div>
            <div className="flex items-center gap-2 mt-0.5">
              <FicheGradeTag grade={global_score.grade} color="#00BCD4" />
              <span className="text-[14px] text-slate-500">5 scores | 20 sources</span>
            </div>
            <div className="text-[14px] text-slate-600">{species} | {season} | {np?.id || `${parseFloat(lat).toFixed(2)}, ${parseFloat(lng).toFixed(2)}`}</div>
          </div>
        </div>
      </GoldenCard>

      {/* ═══════════════════════════════════════════════════════
          GRILLE 3 COLONNES — RÉPLIQUE EXACTE DASHBOARD BIONIC™
          ═══════════════════════════════════════════════════════ */}
      <div className="grid grid-cols-3 gap-1.5" data-testid="fiche-3col-grid">

        {/* ══════════ COLONNE 1: Logistique + Gros Males ══════════ */}
        <div className="space-y-1.5">
          {FICHE_SCORES.slice(0, 2).map(({ key, label, icon: Icon, color }) => {
            const data = scores?.[key];
            if (!data) return null;
            return (
              <GoldenCard key={key} testId={`fiche-score-${key}`} accentColor={color} compact>
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <IC Icon={Icon} color={color} />
                    <span className="text-[16px] font-bold text-white">{label}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-[30px] font-black text-white leading-none">{data.score}</span>
                    <FicheGradeTag grade={data.grade} color={color} />
                  </div>
                </div>
                <div className="w-full h-[6px] rounded-full mb-2" style={{ backgroundColor: 'rgba(255,255,255,0.06)' }}>
                  <div className="h-full rounded-full" style={{ width: `${data.score}%`, backgroundColor: color }} />
                </div>
                {Object.entries(data.components || {}).map(([ck, cv]) => (
                  <CriteriaRow key={ck} criteriaKey={ck} criteriaValue={cv} />
                ))}
              </GoldenCard>
            );
          })}
          {/* Guide Logistique */}
          <GoldenCard testId="fiche-guide-logistique" accentColor={BIONIC.blue} compact>
            <div className="flex items-center gap-2 mb-1.5">
              <IC Icon={MapPin} color={BIONIC.blue} />
              <span className="text-[16px] font-bold text-white">Logistique</span>
              <span className="text-[14px] px-1.5 py-0.5 rounded-lg font-bold ml-auto" style={{ backgroundColor: `${BIONIC.blue}15`, color: BIONIC.blue }}>GUIDE</span>
            </div>
            <p className="text-[14px] text-slate-400 leading-relaxed">Accessibilite vehiculaire: transport mineraux (20-25kg). Portage max: 200m. Budget annuel: 150-250$.</p>
          </GoldenCard>
        </div>

        {/* ══════════ COLONNE 2: Strategique + Cout/ROI + TCS ══════════ */}
        <div className="space-y-1.5">
          {FICHE_SCORES.slice(2, 5).map(({ key, label, icon: Icon, color }) => {
            const data = scores?.[key];
            if (!data) return null;
            return (
              <GoldenCard key={key} testId={`fiche-score-${key}`} accentColor={color} compact>
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <IC Icon={Icon} color={color} />
                    <span className="text-[16px] font-bold text-white">{label}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-[30px] font-black text-white leading-none">{data.score}</span>
                    <FicheGradeTag grade={data.grade} color={color} />
                  </div>
                </div>
                <div className="w-full h-[6px] rounded-full mb-2" style={{ backgroundColor: 'rgba(255,255,255,0.06)' }}>
                  <div className="h-full rounded-full" style={{ width: `${data.score}%`, backgroundColor: color }} />
                </div>
                {Object.entries(data.components || {}).map(([ck, cv]) => (
                  <CriteriaRow key={ck} criteriaKey={ck} criteriaValue={cv} />
                ))}
              </GoldenCard>
            );
          })}
        </div>

        {/* ══════════ COLONNE 3: Plan Gros Males + ROI + Sources ══════════ */}
        <div className="space-y-1.5">
          {/* Plan Gros Males */}
          <GoldenCard testId="fiche-plan-males" accentColor={BIONIC.green} compact>
            <div className="flex items-center gap-2 mb-1.5">
              <IC Icon={TreeDeciduous} color={BIONIC.green} />
              <span className="text-[16px] font-bold text-white">Plan Gros Males</span>
              <span className="text-[14px] px-1.5 py-0.5 rounded-lg font-bold ml-auto" style={{ backgroundColor: `${BIONIC.green}15`, color: BIONIC.green }}>GUIDE</span>
            </div>
            <p className="text-[14px] text-slate-400 leading-relaxed">Positionnez la saline a proximite des corridors de deplacement. Les gros males preferent les zones de transition foret-clairiere avec couvert lateral 60%+.</p>
            <p className="text-[14px] text-slate-400 mt-1">Frequence: bi-mensuelle en pre-rut, hebdomadaire pendant le rut actif.</p>
          </GoldenCard>

          {/* Guide ROI */}
          <GoldenCard testId="fiche-guide-roi" accentColor={BIONIC.purple} compact>
            <div className="flex items-center gap-2 mb-1.5">
              <IC Icon={DollarSign} color={BIONIC.purple} />
              <span className="text-[16px] font-bold text-white">Analyse Cout / ROI</span>
              <span className="text-[14px] px-1.5 py-0.5 rounded-lg font-bold ml-auto" style={{ backgroundColor: `${BIONIC.purple}15`, color: BIONIC.purple }}>GUIDE</span>
            </div>
            <p className="text-[14px] text-slate-400 leading-relaxed">ROI = observations qualitatives par saison. Objectif: 15+ observations positives. Saline mature (2+ saisons) reduit cout/observation de 40-60%.</p>
          </GoldenCard>

          {/* SOIL ENGINE — Analyse pedologique */}
          {soilData && (
            <GoldenCard testId="fiche-soil-analysis" accentColor={BIONIC.amber} compact>
              <div className="flex items-center gap-2 mb-1.5">
                <IC Icon={Mountain} color={BIONIC.amber} />
                <span className="text-[16px] font-bold text-white">Sol — Type detecte</span>
                <span className="text-[14px] px-1.5 py-0.5 rounded-lg font-bold ml-auto" style={{ backgroundColor: soilData.grade === 'A' || soilData.grade === 'S' ? `${BIONIC.green}18` : `${BIONIC.orange}18`, color: soilData.grade === 'A' || soilData.grade === 'S' ? BIONIC.green : BIONIC.orange }}>{soilData.grade} — {soilData.score}/100</span>
              </div>
              <div className="space-y-1">
                <div className="flex justify-between"><span className="text-[14px] text-slate-400">Type</span><span className="text-[16px] font-semibold text-white">{soilData.soil_name}</span></div>
                <div className="flex justify-between"><span className="text-[14px] text-slate-400">Retention</span><span className="text-[16px] font-semibold text-white">{soilData.metrics?.retention_mineraux}/100</span></div>
                <div className="flex justify-between"><span className="text-[14px] text-slate-400">Drainage</span><span className="text-[16px] font-semibold text-white">{soilData.metrics?.drainage_naturel}/100</span></div>
                <div className="flex justify-between"><span className="text-[14px] text-slate-400">Lessivage</span><span className="text-[16px] font-semibold text-white">{soilData.metrics?.risque_lessivage}/100</span></div>
              </div>
              <p className="text-[14px] text-slate-500 mt-1.5 leading-relaxed">{soilData.seasonal_note}</p>
              {soilData.recommendations?.length > 0 && (
                <div className="mt-2 space-y-1">
                  {soilData.recommendations.slice(0, 4).map((r, i) => (
                    <p key={i} className="text-[14px] text-slate-400 leading-relaxed flex items-start gap-1.5">
                      <span className="text-amber-500 mt-0.5 flex-shrink-0">&#9670;</span>{r}
                    </p>
                  ))}
                </div>
              )}
            </GoldenCard>
          )}

          {/* 20 Sources Scientifiques */}
          <GoldenCard testId="fiche-sources-card" accentColor="#00BCD4" compact>
            <button onClick={() => setShowSources(!showSources)} className="w-full flex items-center justify-between cursor-pointer" data-testid="fiche-toggle-sources">
              <div className="flex items-center gap-2">
                <IC Icon={BookOpen} color="#00BCD4" />
                <span className="text-[16px] font-bold text-white">20 Sources</span>
              </div>
              {showSources ? <ChevronUp className="h-4 w-4 text-slate-500" /> : <ChevronDown className="h-4 w-4 text-slate-500" />}
            </button>
            {showSources && (
              <div className="mt-2 space-y-1">
                {(scientific_sources || []).map((src) => (
                  <div key={src.id} className="flex items-start gap-2 py-1 border-b" style={{ borderColor: 'rgba(255,255,255,0.04)' }}>
                    <span className="text-[14px] font-bold text-cyan-500 flex-shrink-0">[{src.id}]</span>
                    <span className="text-[14px] text-slate-300">{src.ref}</span>
                  </div>
                ))}
              </div>
            )}
          </GoldenCard>

          {/* Integrations */}
          <div className="flex flex-wrap gap-1">
            {['SUPRA/V6', 'ACCESS v7', 'PARTAGER', 'ADMIN Premium'].map((tag, i) => (
              <span key={i} className="text-[14px] px-1.5 py-0.5 rounded font-bold" style={{ backgroundColor: `${['#00BCD4', '#22c55e', '#34d399', '#f5a623'][i]}10`, color: ['#00BCD4', '#22c55e', '#34d399', '#f5a623'][i] }}>{tag}</span>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default FicheTab;

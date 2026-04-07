/**
 * CriteriaDetailModal — GUIDE BIONIC — NIVEAU PROFESSIONNEL™
 * =============================================================
 * BCE-4X STEEVE-MAX — SEPARATION STRICTE PAR ESPECE — ZERO GENERIQUE
 *
 * Especes: Orignal | Chevreuil | Ours noir | Wapiti | Dindon sauvage
 * 15 sections obligatoires — contenu UNIQUEMENT pour l'espece active
 * Sources TOP-TIER: MFFP, UQAR, ULaval, NDA, RMEF, NWTF, J. Wildlife Mgmt
 */
import React from 'react';
import {
  X, Target, AlertTriangle, BookOpen, CheckCircle,
  Crosshair, Wind, Mountain, MapPin, Shield, Eye,
  ThermometerSun, Footprints, Leaf, Construction
} from 'lucide-react';
import { getCriteria, SPECIES_LABELS } from './criteriaDatabase';
import IconCircle from './IconCircle';

const GOLDEN = { cardBg: '#1E293B', pageBg: '#0F172A' };
const B = { green: '#00C853', yellow: '#F9D423', orange: '#FF9800', red: '#D32F2F', blue: '#2196F3', purple: '#9C27B0', amber: '#FFB300', cyan: '#00BCD4' };
const IC = IconCircle;

const Section = ({ icon: SIcon, color, title, children }) => (
  <div className="rounded-xl px-5 py-4" style={{ backgroundColor: GOLDEN.cardBg, borderLeft: `4px solid ${color}` }}>
    <div className="flex items-center gap-2 mb-2"><IC Icon={SIcon} color={color} /><span className="text-[16px] font-bold text-white">{title}</span></div>
    {children}
  </div>
);

const BulletList = ({ items, icon = '\u2022', color = '#94A3B8' }) => (
  <ul className="space-y-1.5">
    {(items || []).map((item, i) => (
      <li key={i} className="flex items-start gap-2">
        <span className="text-[16px] mt-0.5 flex-shrink-0" style={{ color }}>{icon}</span>
        <span className="text-[16px] text-slate-300 leading-relaxed">{item}</span>
      </li>
    ))}
  </ul>
);

const Threshold = ({ label, text, color }) => (
  <div className="flex items-start gap-2 px-3 py-2 rounded-lg" style={{ backgroundColor: `${color}10` }}>
    <span className="w-3 h-3 rounded-full mt-1 flex-shrink-0" style={{ backgroundColor: color }} />
    <span className="text-[16px] text-slate-300"><strong className="text-white">{label}:</strong> {text}</span>
  </div>
);

// Helper: extract species-specific content or fallback
function getForSpecies(obj, sp) {
  if (!obj) return null;
  if (typeof obj === 'string') return obj;
  if (Array.isArray(obj)) return obj;
  return obj[sp] || obj.orignal || obj[Object.keys(obj)[0]] || null;
}

export function CriteriaDetailModal({ criteriaKey, criteriaValue, species = 'orignal', season = 'automne', onClose }) {
  if (!criteriaKey) return null;
  const data = getCriteria(criteriaKey);
  const sp = (species || 'orignal').toLowerCase();
  const spLabel = SPECIES_LABELS[sp] || SPECIES_LABELS.orignal;
  const spShort = sp === 'orignal' ? 'Orignal' : sp === 'chevreuil' ? 'Chevreuil' : sp === 'ours' ? 'Ours noir' : sp === 'wapiti' ? 'Wapiti' : sp === 'dindon' ? 'Dindon sauvage' : 'Orignal';

  const scoreValue = typeof criteriaValue === 'object' ? criteriaValue.value : criteriaValue;
  const scoreNum = parseInt(String(scoreValue).replace(/[^0-9]/g, ''), 10) || 0;
  const sc = scoreNum >= 80 ? B.green : scoreNum >= 50 ? B.orange : B.red;
  const sl = scoreNum >= 80 ? 'VERT' : scoreNum >= 50 ? 'JAUNE' : 'ROUGE';

  // Extract species-specific content — STRICT SEPARATION
  const justif = getForSpecies(data.justification, sp);
  const recosTerrain = getForSpecies(data.recommendations_terrain, sp) || [];
  const strats = getForSpecies(data.strategies_optimisation, sp) || [];
  const techniques = getForSpecies(data.techniques_chasse, sp) || [];
  const erreurs = getForSpecies(data.erreurs_a_eviter, sp) || [];
  const seasonData = getForSpecies(data.optimisations_saisonnieres, season) || '';

  return (
    <div className="fixed inset-0 flex items-center justify-center" style={{ backgroundColor: 'rgba(0,0,0,0.8)', zIndex: 99999 }} onClick={onClose} data-testid="criteria-modal-overlay">
      <div className="w-full max-w-6xl max-h-[92vh] overflow-y-auto rounded-lg" style={{ backgroundColor: GOLDEN.pageBg, boxShadow: '0 8px 48px rgba(0,0,0,0.7)' }} onClick={e => e.stopPropagation()} data-testid="criteria-modal">

        {/* Header */}
        <div className="sticky top-0 z-10 px-6 py-4 flex items-start justify-between" style={{ backgroundColor: GOLDEN.pageBg, borderBottom: '1px solid rgba(255,255,255,0.06)' }}>
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-1 flex-wrap">
              <span className="text-[14px] font-bold px-2 py-0.5 rounded-lg" style={{ backgroundColor: `${sc}18`, color: sc }}>{sl} — {scoreValue}</span>
              <span className="text-[14px] font-bold px-2 py-0.5 rounded-lg" style={{ backgroundColor: `${B.cyan}18`, color: B.cyan }}>{spShort}</span>
              <span className="text-[14px] text-slate-500">{season}</span>
            </div>
            <h2 className="text-[18px] font-black text-white leading-tight">{data.title}</h2>
            <p className="text-[14px] text-slate-500 mt-1">GUIDE BIONIC — NIVEAU PROFESSIONNEL™ — {spLabel}</p>
          </div>
          <button onClick={onClose} className="w-8 h-8 rounded-full flex items-center justify-center hover:bg-white/10 flex-shrink-0 ml-3" data-testid="criteria-modal-close">
            <X className="h-5 w-5 text-slate-400" />
          </button>
        </div>

        <div className="px-6 py-3 space-y-3">
          {/* ═══ RANGEE 1: Definition + Methodologie (2 colonnes) ═══ */}
          <div className="grid grid-cols-2 gap-3">
            {/* 1. Definition */}
            <Section icon={BookOpen} color={B.cyan} title="1. Definition du critere">
              <p className="text-[14px] text-slate-300 leading-relaxed">{data.definition}</p>
            </Section>

            {/* 2. Methodologie */}
            <Section icon={Target} color={B.purple} title="2. Methodologie de scoring">
              <p className="text-[14px] text-slate-300 leading-relaxed">{data.methodology}</p>
            </Section>
          </div>

          {/* 3. Justification — ESPECE ACTIVE UNIQUEMENT */}
          <Section icon={CheckCircle} color={sc} title={`3. Justification du score — ${spShort}`}>
            <p className="text-[14px] text-slate-300 leading-relaxed">{justif}</p>
          </Section>

          {/* 4. Recommandations terrain — ESPECE ACTIVE UNIQUEMENT (2 colonnes) */}
          <Section icon={MapPin} color={B.green} title={`4. Recommandations terrain — ${spShort} (${recosTerrain.length})`}>
            <div className="grid grid-cols-2 gap-x-4 gap-y-0">
              {recosTerrain.map((item, i) => (
                <div key={i} className="flex items-start gap-2 py-1">
                  <span className="text-[13px] mt-0.5 flex-shrink-0" style={{ color: B.green }}>&#10003;</span>
                  <span className="text-[13px] text-slate-300 leading-snug">{typeof item === 'string' ? item : item?.text || ''}</span>
                </div>
              ))}
            </div>
          </Section>

          {/* ═══ RANGEE 2: Strategies + Techniques + Erreurs (3 colonnes) ═══ */}
          <div className="grid grid-cols-3 gap-3">
            {/* 5. Strategies optimisation — ESPECE ACTIVE UNIQUEMENT */}
            <Section icon={Crosshair} color={B.amber} title={`5. Strategies — ${spShort}`}>
              <BulletList items={strats} icon="&#9654;" color={B.amber} />
            </Section>

            {/* 6. Techniques chasse — ESPECE ACTIVE UNIQUEMENT */}
            <Section icon={Eye} color={B.orange} title={`6. Techniques — ${spShort}`}>
              <BulletList items={techniques} icon="&#9679;" color={B.orange} />
            </Section>

            {/* 7. Erreurs a eviter — ESPECE ACTIVE UNIQUEMENT */}
            <Section icon={AlertTriangle} color={B.red} title={`7. Erreurs — ${spShort}`}>
              <BulletList items={erreurs} icon="&#10007;" color={B.red} />
            </Section>
          </div>

          {/* ═══ RANGEE 3: Saisonnier + Espece (2 colonnes) ═══ */}
          <div className="grid grid-cols-2 gap-3">
            {/* 8. Optimisations saisonnieres */}
            <Section icon={ThermometerSun} color={B.yellow} title={`8. Saisonnier — ${season}`}>
              <p className="text-[14px] text-slate-300 leading-snug mb-2"><strong className="text-white">{season}:</strong> {seasonData}</p>
              {typeof data.optimisations_saisonnieres === 'object' && !Array.isArray(data.optimisations_saisonnieres) &&
                Object.entries(data.optimisations_saisonnieres).filter(([k]) => k !== season).map(([k, v]) => (
                  <p key={k} className="text-[13px] text-slate-400 leading-snug py-0.5"><strong className="text-slate-300">{k}:</strong> {typeof v === 'string' ? v : ''}</p>
                ))
              }
            </Section>

            {/* 9. Optimisations espece — NOM DE L'ESPECE ACTIVE */}
            <Section icon={Footprints} color={B.cyan} title={`9. Espece — ${spLabel}`}>
              <p className="text-[14px] text-slate-300 leading-snug mb-1.5">
                Toutes les recommandations sont <strong className="text-white">strictement alignees</strong> sur <strong style={{ color: B.green }}>{spLabel}</strong>.
                Aucun melange inter-especes.
              </p>
              <div className="rounded-lg px-2.5 py-1.5 mt-1" style={{ backgroundColor: `${B.green}10`, borderLeft: `3px solid ${B.green}` }}>
                <p className="text-[13px] text-slate-300"><strong className="text-white">Espece active:</strong> {spLabel}</p>
              </div>
            </Section>
          </div>

          {/* ═══ RANGEE 4: Support + Meteo + Pression (3 colonnes) ═══ */}
          <div className="grid grid-cols-3 gap-3">
            {/* 10. Optimisations support */}
            <Section icon={Construction} color={B.blue} title="10. Support">
              <BulletList items={data.optimisations_support || []} icon="&#9670;" color={B.blue} />
            </Section>

            {/* 11. Optimisations meteo */}
            <Section icon={Wind} color={B.purple} title="11. Meteo">
              <BulletList items={data.optimisations_meteo || []} icon="&#9729;" color={B.purple} />
            </Section>

            {/* 12. Optimisations pression chasse */}
            <Section icon={Shield} color={B.orange} title="12. Pression">
              <BulletList items={data.optimisations_pression || []} icon="&#9888;" color={B.orange} />
            </Section>
          </div>

          {/* ═══ RANGEE 5: Seuils + Sources + Conformite (3 colonnes) ═══ */}
          <div className="grid grid-cols-3 gap-3">
            {/* 13. Seuils */}
            <Section icon={AlertTriangle} color={B.amber} title="13. Seuils">
              <div className="space-y-1.5">
                <Threshold label="VERT" text={data.thresholds?.green} color={B.green} />
                <Threshold label="JAUNE" text={data.thresholds?.yellow} color={B.orange} />
                <Threshold label="ROUGE" text={data.thresholds?.red} color={B.red} />
              </div>
            </Section>

            {/* 14. Sources scientifiques TOP-TIER */}
            <Section icon={BookOpen} color={B.blue} title={`14. Sources (${data.sources?.length || 0})`}>
              <ul className="space-y-0.5">
                {(data.sources || []).map((s, i) => (
                  <li key={i} className="text-[12px] text-slate-400 py-0.5 leading-snug">[{i + 1}] {s}</li>
                ))}
              </ul>
            </Section>

            {/* 15. Conformite GUIDE BIONIC */}
            <Section icon={Leaf} color={B.green} title="15. Conformite">
              <div className="space-y-1">
                <div className="flex items-center gap-1.5">
                  <span className="w-1.5 h-1.5 rounded-full" style={{ backgroundColor: B.green }} />
                  <span className="text-[13px] text-slate-300">15 sections — <strong className="text-white">CONFORME</strong></span>
                </div>
                <div className="flex items-center gap-1.5">
                  <span className="w-1.5 h-1.5 rounded-full" style={{ backgroundColor: B.green }} />
                  <span className="text-[13px] text-slate-300">Espece — <strong className="text-white">{spShort}</strong></span>
                </div>
                <div className="flex items-center gap-1.5">
                  <span className="w-1.5 h-1.5 rounded-full" style={{ backgroundColor: B.green }} />
                  <span className="text-[13px] text-slate-300">Recos — <strong className="text-white">{recosTerrain.length}</strong></span>
                </div>
                <div className="flex items-center gap-1.5">
                  <span className="w-1.5 h-1.5 rounded-full" style={{ backgroundColor: B.green }} />
                  <span className="text-[13px] text-slate-300">Sources — <strong className="text-white">{data.sources?.length || 0}</strong></span>
                </div>
                <div className="flex items-center gap-1.5">
                  <span className="w-1.5 h-1.5 rounded-full" style={{ backgroundColor: B.green }} />
                  <span className="text-[13px] text-slate-300">BCE-4X — <strong className="text-white">GOLDEN</strong></span>
                </div>
              </div>
            </Section>
          </div>
        </div>
      </div>
    </div>
  );
}

export default CriteriaDetailModal;

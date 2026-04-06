import React, { useState, useRef, useCallback } from 'react';
import {
  BookOpen, FlaskConical, Leaf, AlertTriangle, Beaker,
  Zap, Shield, ChevronDown, ChevronUp, Mountain,
  Crown, Eye, Target, Calendar, Ban,
  Heart, Baby, Crosshair, Wheat,
  CircleAlert, Timer, Layers, Star,
  Download, Loader2, X
} from 'lucide-react';

/**
 * ============================================================
 * MODULE PÉDAGOGIQUE — GRILLE 3 COLONNES STANDARD GOLDEN
 * ============================================================
 * BCE-4X GOLDEN V6+ | COMMANDANT STEEVE-MAX
 * HARMONISATION ERGONOMIQUE — identique au haut SUPRA v2
 * Flag: PEDAGOGIE_SALINE_ENABLED
 * 100% AUTONOME — AUCUN IMPACT sur BDRE, corridors, zones, affûts
 * ============================================================
 */

const PEDAGOGIE_SALINE_ENABLED = true;

const BIONIC = {
  green: '#00C853', yellow: '#F9D423', orange: '#FF9800', red: '#D32F2F',
  blue: '#2196F3', purple: '#9C27B0', amber: '#FFB300', cyan: '#00BCD4',
  teal: '#009688', pink: '#E91E63',
};

// ═══════════════════════════════════════════════════════
// DONNÉES PÉDAGOGIQUES
// ═══════════════════════════════════════════════════════

const SECTIONS = [
  {
    id: 'mineraux', icon: FlaskConical, title: 'Besoins mineraux', badge: '4 groupes', color: BIONIC.orange,
    preview: 'Males alpha: Na CRITIQUE, Ca/P TRES ELEVE. Femelles gestation: Ca/P EXTREME. Veaux: Ca/P CRITIQUE.',
    rows: [
      { label: 'Males alpha', items: [{ n: 'Sodium (Na)', v: 'CRITIQUE', c: BIONIC.red }, { n: 'Calcium (Ca)', v: 'TRES ELEVE', c: BIONIC.orange }, { n: 'Phosphore (P)', v: 'TRES ELEVE', c: BIONIC.orange }, { n: 'Magnesium (Mg)', v: 'ELEVE', c: BIONIC.amber }] },
      { label: 'Femelles (gestation)', items: [{ n: 'Calcium (Ca)', v: 'EXTREME', c: BIONIC.red }, { n: 'Phosphore (P)', v: 'EXTREME', c: BIONIC.red }, { n: 'Sodium (Na)', v: 'ELEVE', c: BIONIC.amber }, { n: 'Fer (Fe)', v: 'ELEVE', c: BIONIC.amber }] },
      { label: 'Veaux (croissance)', items: [{ n: 'Calcium (Ca)', v: 'CRITIQUE', c: BIONIC.red }, { n: 'Phosphore (P)', v: 'CRITIQUE', c: BIONIC.red }, { n: 'Zinc (Zn)', v: 'ELEVE', c: BIONIC.amber }, { n: 'Cuivre (Cu)', v: 'MODERE', c: BIONIC.yellow }] },
      { label: 'Periode de chasse', items: [{ n: 'Sodium (Na)', v: 'CRITIQUE', c: BIONIC.red }, { n: 'Potassium (K)', v: 'ELEVE', c: BIONIC.amber }, { n: 'Magnesium (Mg)', v: 'MODERE', c: BIONIC.yellow }, { n: 'Selenium (Se)', v: 'MODERE', c: BIONIC.yellow }] },
    ],
  },
  {
    id: 'proteines', icon: Zap, title: 'Besoins proteines', badge: '3 groupes', color: BIONIC.green,
    preview: 'Males: 500g/3j (maintien masse musculaire). Femelles: 300-400g/3j. Veaux: 200-300g/3j (croissance).',
    rows: [
      { label: 'Males', value: '500 g / 3 jours', desc: 'Maintien masse musculaire, regeneration panache, activite territoriale', c: BIONIC.amber },
      { label: 'Femelles', value: '300-400 g / 3 jours', desc: 'Gestation, lactation, production de lait riche en proteines', c: BIONIC.pink },
      { label: 'Veaux', value: '200-300 g / 3 jours', desc: 'Croissance rapide, developpement musculaire et organes', c: BIONIC.cyan },
    ],
  },
  {
    id: 'oligo', icon: Beaker, title: 'Oligo-elements', badge: '6 elements', color: BIONIC.purple,
    preview: 'Zn (immunite), Cu (hematopoiese), Se (antioxydant), Fe (transport O2), Mn (os), I (thyroide).',
    rows: [
      { sym: 'Zn', nom: 'Zinc', role: 'Immunite, reproduction', besoin: '50 mg/kg', c: BIONIC.blue },
      { sym: 'Cu', nom: 'Cuivre', role: 'Hematopoiese, keratinisation', besoin: '10-15 mg/kg', c: BIONIC.orange },
      { sym: 'Se', nom: 'Selenium', role: 'Antioxydant, fertilite', besoin: '0.1-0.3 mg/kg', c: BIONIC.green },
      { sym: 'Fe', nom: 'Fer', role: 'Transport O2, hemoglobine', besoin: '50-100 mg/kg', c: BIONIC.red },
      { sym: 'Mn', nom: 'Manganese', role: 'Formation osseuse', besoin: '40-60 mg/kg', c: BIONIC.purple },
      { sym: 'I', nom: 'Iode', role: 'Fonction thyroidienne', besoin: '0.2-0.5 mg/kg', c: BIONIC.teal },
    ],
  },
  {
    id: 'solutions', icon: Leaf, title: 'Solutions terrain', badge: '7 solutions', color: BIONIC.green,
    preview: 'Soya (prot 35-40%), luzerne (18-22%), trefle (15-20%), chicoree, mais, pommes, betteraves.',
    rows: [
      { nom: 'Soya', cat: 'Legumineuse', prot: '35-40%', min: 'Ca, P, K, Fe', saison: 'Ete-automne' },
      { nom: 'Luzerne', cat: 'Legumineuse', prot: '18-22%', min: 'Ca, Mg, K', saison: 'Print-automne' },
      { nom: 'Trefle', cat: 'Legumineuse', prot: '15-20%', min: 'Ca, P, Mg', saison: 'Print-ete' },
      { nom: 'Chicoree', cat: 'Herbacee', prot: '12-18%', min: 'Zn, Cu, Se', saison: 'Ete-automne' },
      { nom: 'Mais', cat: 'Cereale', prot: '8-10%', min: 'P, K, energie', saison: 'Automne-hiver' },
      { nom: 'Pommes', cat: 'Fruit', prot: 'Faible', min: 'K, sucres', saison: 'Automne' },
      { nom: 'Betteraves', cat: 'Racine', prot: '6-8%', min: 'Fe, Mn, K', saison: 'Automne' },
    ],
  },
  {
    id: 'supports', icon: Layers, title: 'Comparatif supports', badge: 'Hierarchie', color: BIONIC.amber,
    preview: 'Souche decomposition: 98/100. Souche recente: 82. Bois mou: 75. Bois franc: 55. Baton: 30.',
    rows: [
      { nom: 'Souche decomposition', score: 98, c: BIONIC.green, desc: 'Absorption maximale, retention longue duree' },
      { nom: 'Souche recente', score: 82, c: BIONIC.green, desc: 'Bonne absorption, porosite progressive' },
      { nom: 'Bois mou (epinette)', score: 75, c: BIONIC.yellow, desc: 'Absorption moderee, abondant, cout zero' },
      { nom: 'Bois franc (erable)', score: 55, c: BIONIC.orange, desc: 'Absorption faible, structure dense' },
      { nom: 'Baton / piquet', score: 30, c: BIONIC.red, desc: 'Tres mauvaise retention, a eviter' },
    ],
  },
  {
    id: 'strategies', icon: Target, title: 'Strategies optimisation', badge: '5 strategies', color: BIONIC.red,
    preview: 'Mini-champ alimentation, synergies mineraux/proteines/energie, strategies territoriales et saisonnieres.',
    rows: [
      { titre: 'Mini-champ alimentation', desc: 'Creer 20-50m2 pres de la saline. Semer trefle/chicoree/luzerne.' },
      { titre: 'Synergies min/prot/energie', desc: 'Base minerale + complement proteique + source energetique.' },
      { titre: 'Strategies territoriales', desc: 'Transition foret/clairiere, couvert lateral 60%+, distance 200m routes.' },
      { titre: 'Strategies comportementales', desc: 'Heures de visite (aube/crepuscule), frequence saisonniere.' },
      { titre: 'Strategies saisonnieres', desc: 'Adapter composition selon saison biologique (print/ete/rut/hiver).' },
    ],
  },
  {
    id: 'prechasse', icon: Calendar, title: 'Gestion pre-chasse', badge: '5 regles', color: BIONIC.blue,
    preview: 'Rafraichir /2 sem. Doubler 2 sem avant. STOP 15j avant. Silence total. Support humide.',
    rows: [
      { regle: 'Rafraichir toutes les 2 semaines', detail: 'Regularite = habitude. Conditionner les animaux.' },
      { regle: 'Doubler quantites 2 sem avant chasse', detail: 'Apport massif pour intensifier frequentation.' },
      { regle: 'STOP rafraichissement 15j avant', detail: 'ZERO visite humaine. Odeur doit se dissiper.' },
      { regle: 'Site completement tranquille', detail: 'Aucune camera, aucun passage, silence total.' },
      { regle: 'Support humide et absorbant', detail: 'Souche saturee = diffusion minerale prolongee.' },
    ],
  },
  {
    id: 'hyperattractive', icon: Star, title: 'Hyper-attractive chasse', badge: 'ELITE', color: BIONIC.amber,
    preview: '6-8 sem historique, melange Na+Ca+pommes fermentees, 15j sans humain, affut face au vent.',
    rows: [
      { label: 'Timing', desc: '6-8 semaines de frequentation avant la chasse' },
      { label: 'Composition', desc: 'Sodium + calcium + pommes fermentees = olfactif irresistible' },
      { label: 'Support', desc: 'Souche decomposition saturee 3+ rechargements' },
      { label: 'Environnement', desc: 'Mini-champ adjacent trefle/chicoree encore vert en octobre' },
      { label: 'Quietude', desc: '15 jours minimum sans presence humaine' },
      { label: 'Vent', desc: 'Affut en fonction du vent dominant. Le cerf approche face au vent.' },
    ],
  },
  {
    id: 'aeviter', icon: AlertTriangle, title: 'A EVITER', badge: '9 erreurs', color: BIONIC.red,
    preview: 'Visites frequentes, produits miracles, exces sel, sol nu, corridors principaux, sites exposes.',
    rows: [
      { item: 'Visites trop frequentes', desc: 'Trace olfactive 48-72h. Max 1/2 semaines.' },
      { item: 'Produits miracles / aromatises', desc: 'Dependance artificielle, alerte males matures.' },
      { item: 'Exces de sel', desc: 'Brule la vegetation. Max 2-3 kg/rechargement.' },
      { item: 'Produits non certifies', desc: 'Risque contamination (plomb, metaux lourds).' },
      { item: 'Sol nu sans support', desc: 'Mineraux laves par la pluie. Toujours souche/bois mou.' },
      { item: 'Corridors principaux', desc: 'Les animaux traversent, ne s arretent pas.' },
      { item: 'Sites exposes (sans couvert)', desc: '< 40% couvert = visite nocturne seulement.' },
      { item: 'Changement constant de recette', desc: 'Constance = confiance. Changer cree mefiance.' },
      { item: 'Rafraichissement trop proche chasse', desc: 'JAMAIS dans les 15j avant. Odeur humaine = deserte.' },
    ],
  },
];

const NARRATIVES = {
  orignal: {
    printemps: "Apres cinq longs mois d'hiver, l'orignal sort de l'hivernage en deficit severe de sodium. Son organisme, affaibli par un regime exclusif de ramilles, cherche desesperement les mineraux perdus. C'est ici que ta saline entre en jeu. Positionnee sur un sol retentif avec un support poreux, elle devient le premier point de ravitaillement mineral du printemps.",
    ete: "Le panache est en velours. La croissance est explosive — calcium, phosphore et magnesium sont consommes a un rythme sans precedent. L'orignal male adulte visite les salines 4 a 7 fois par semaine, parfois pendant 15 a 25 minutes. C'est la saison ou ta saline travaille le plus dur.",
    rut: "L'activite territoriale est a son maximum. Le male dominant patrouille, marque, combat. Les pertes hydriques sont majeures — le sodium devient vital. Ta saline est sa station de ravitaillement entre deux patrouilles.",
    hiver: "Le metabolisme hivernal ralentit tout. Les besoins sont minimaux, mais le sodium reste recherche. Les visites sont sporadiques. Ta saline entre en mode maintenance, prete pour le prochain printemps.",
  },
  chevreuil: {
    printemps: "Le chevreuil sort d'hiver epuise. Ses reserves minerales sont au plus bas. Le sodium est le premier mineral qu'il cherche activement. Ta saline, positionnee dans cette zone optimale, devient son refuge mineral. Le calcium et le phosphore sont critiques pour la regeneration du panache qui demarre des avril.",
    ete: "Phase de croissance maximale du panache. Les besoins en calcium et phosphore sont multiplies par trois. L'appetit mineral est a son pic absolu. Ta saline recoit 4 a 7 visites par semaine, avec des durees prolongees de 15 a 25 minutes.",
    rut: "Activite maximale. Perte de poids de 20-30%. Le sodium compense la deshydratation extreme. Les visites sont rares mais les femelles continuent de venir — et les males suivent les femelles. Ta saline est un point d'intersection strategique.",
    hiver: "Phase de survie. Metabolisme ralenti. Les besoins sont minimaux mais le sodium reste recherche lors des redoux. Ta saline conserve ses reserves sous la neige, prete a reprendre du service au prochain printemps.",
  },
};

// ═══════════════════════════════════════════════════════
// COMPOSANT CARD DÉTAIL (modal inline)
// ═══════════════════════════════════════════════════════

const SectionDetail = ({ section, onClose }) => {
  const s = section;
  return (
    <div className="col-span-3 rounded-lg px-4 py-3 animate-in fade-in duration-200" style={{ backgroundColor: '#1a2744', border: `2px solid ${s.color}40` }} data-testid={`pedagogie-detail-${s.id}`}>
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <s.icon style={{ color: s.color, width: 18, height: 18 }} />
          <span className="text-[15px] font-bold text-white">{s.title}</span>
          <span className="text-[12px] font-bold px-2 py-0.5 rounded" style={{ backgroundColor: `${s.color}18`, color: s.color }}>{s.badge}</span>
        </div>
        <button onClick={onClose} className="w-6 h-6 rounded flex items-center justify-center hover:bg-white/10 cursor-pointer" data-testid={`pedagogie-close-${s.id}`}><X className="w-3.5 h-3.5 text-slate-400" /></button>
      </div>
      {/* CONTENT by section type */}
      {s.id === 'mineraux' && s.rows.map((g, i) => (
        <div key={i} className="mb-2">
          <div className="text-[12px] font-bold text-slate-300 mb-1 uppercase tracking-wider">{g.label}</div>
          {g.items.map((m, j) => (
            <div key={j} className="flex items-center justify-between py-0.5 border-b" style={{ borderColor: 'rgba(255,255,255,0.04)' }}>
              <span className="text-[13px] text-slate-300">{m.n}</span>
              <span className="text-[11px] font-black px-1.5 py-0.5 rounded" style={{ backgroundColor: `${m.c}18`, color: m.c }}>{m.v}</span>
            </div>
          ))}
        </div>
      ))}
      {s.id === 'proteines' && s.rows.map((p, i) => (
        <div key={i} className="flex items-center justify-between py-2 border-b" style={{ borderColor: 'rgba(255,255,255,0.04)' }}>
          <div><span className="text-[14px] font-bold text-white">{p.label}</span><br /><span className="text-[12px] text-slate-500">{p.desc}</span></div>
          <span className="text-[14px] font-black ml-3 whitespace-nowrap" style={{ color: p.c }}>{p.value}</span>
        </div>
      ))}
      {s.id === 'oligo' && (
        <div className="grid grid-cols-3 gap-2">
          {s.rows.map((e, i) => (
            <div key={i} className="rounded px-2 py-1.5" style={{ backgroundColor: '#0F172A' }}>
              <div className="flex items-center gap-1.5 mb-0.5"><span className="text-[14px] font-black" style={{ color: e.c }}>{e.sym}</span><span className="text-[12px] text-white font-semibold">{e.nom}</span></div>
              <div className="text-[11px] text-slate-500">{e.role}</div>
              <div className="text-[11px] font-bold mt-0.5" style={{ color: e.c }}>{e.besoin}</div>
            </div>
          ))}
        </div>
      )}
      {s.id === 'solutions' && s.rows.map((sol, i) => (
        <div key={i} className="flex items-center justify-between py-1.5 border-b" style={{ borderColor: 'rgba(255,255,255,0.04)' }}>
          <div><span className="text-[13px] font-bold text-white">{sol.nom}</span><span className="text-[11px] text-slate-500 ml-2">{sol.cat}</span></div>
          <div className="text-right text-[11px]"><span className="text-green-400">Prot: {sol.prot}</span><span className="text-slate-500 ml-2">{sol.saison}</span></div>
        </div>
      ))}
      {s.id === 'supports' && s.rows.map((sup, i) => (
        <div key={i} className="flex items-center gap-3 py-1.5 border-b" style={{ borderColor: 'rgba(255,255,255,0.04)' }}>
          <span className="text-[16px] font-black w-8 text-right tabular-nums" style={{ color: sup.c }}>{sup.score}</span>
          <div className="flex-1"><div className="text-[13px] font-bold text-white">{sup.nom}</div><div className="text-[11px] text-slate-500">{sup.desc}</div></div>
          <div className="w-16 h-[5px] rounded-full overflow-hidden" style={{ backgroundColor: 'rgba(255,255,255,0.06)' }}><div className="h-full rounded-full" style={{ width: `${sup.score}%`, backgroundColor: sup.c }} /></div>
        </div>
      ))}
      {s.id === 'strategies' && s.rows.map((st, i) => (
        <div key={i} className="py-1.5 border-b" style={{ borderColor: 'rgba(255,255,255,0.04)' }}>
          <div className="text-[13px] font-bold text-white">{st.titre}</div>
          <div className="text-[11px] text-slate-400">{st.desc}</div>
        </div>
      ))}
      {s.id === 'prechasse' && s.rows.map((r, i) => (
        <div key={i} className="py-1.5 border-b" style={{ borderColor: 'rgba(255,255,255,0.04)' }}>
          <div className="text-[13px] font-bold text-white">{r.regle}</div>
          <div className="text-[11px] text-slate-400">{r.detail}</div>
        </div>
      ))}
      {s.id === 'hyperattractive' && s.rows.map((h, i) => (
        <div key={i} className="flex gap-2 py-1.5 border-b" style={{ borderColor: 'rgba(255,255,255,0.04)' }}>
          <span className="text-[12px] font-bold text-amber-400 w-24 flex-shrink-0">{h.label}</span>
          <span className="text-[12px] text-slate-400">{h.desc}</span>
        </div>
      ))}
      {s.id === 'aeviter' && s.rows.map((e, i) => (
        <div key={i} className="flex items-start gap-2 py-1 border-b" style={{ borderColor: 'rgba(255,255,255,0.04)' }}>
          <Ban style={{ color: BIONIC.red, width: 11, height: 11, flexShrink: 0, marginTop: 3 }} />
          <div><span className="text-[12px] font-bold text-red-400">{e.item}</span><span className="text-[11px] text-slate-500 ml-1">— {e.desc}</span></div>
        </div>
      ))}
    </div>
  );
};

// ═══════════════════════════════════════════════════════
// COMPOSANT PRINCIPAL — GRILLE 3 COLONNES GOLDEN
// ═══════════════════════════════════════════════════════

const PedagogieModule = ({ species = 'orignal', season = 'printemps', score, gc }) => {
  const speciesKey = species.toLowerCase();
  const seasonKey = season.toLowerCase();
  const narrativeSpecies = NARRATIVES[speciesKey] || NARRATIVES.orignal;
  const narrativeText = narrativeSpecies[seasonKey] || narrativeSpecies.printemps || narrativeSpecies[Object.keys(narrativeSpecies)[0]];
  const moduleRef = useRef(null);
  const [pdfExporting, setPdfExporting] = useState(false);
  const [expandedId, setExpandedId] = useState(null);

  const handleExportPDF = useCallback(async () => {
    if (!moduleRef.current || pdfExporting) return;
    setPdfExporting(true);
    try {
      const html2canvas = (await import('html2canvas')).default;
      const { jsPDF } = await import('jspdf');
      const prevExpanded = expandedId;
      setExpandedId(null);
      await new Promise(r => setTimeout(r, 100));
      const canvas = await html2canvas(moduleRef.current, { backgroundColor: '#0F172A', scale: 2, useCORS: true, logging: false });
      const pdf = new jsPDF({ orientation: 'portrait', unit: 'mm', format: 'a4' });
      const pageW = pdf.internal.pageSize.getWidth();
      const pageH = pdf.internal.pageSize.getHeight();
      const margin = 8;
      const contentW = pageW - margin * 2;
      const imgRatio = canvas.height / canvas.width;
      const contentH = contentW * imgRatio;
      let yPos = 0;
      const usableH = pageH - margin * 2;
      let pageNum = 0;
      while (yPos < contentH) {
        if (pageNum > 0) pdf.addPage();
        const srcY = (yPos / contentH) * canvas.height;
        const srcH = Math.min((usableH / contentH) * canvas.height, canvas.height - srcY);
        const drawH = Math.min(usableH, contentH - yPos);
        const tempCanvas = document.createElement('canvas');
        tempCanvas.width = canvas.width;
        tempCanvas.height = srcH;
        const ctx = tempCanvas.getContext('2d');
        ctx.drawImage(canvas, 0, srcY, canvas.width, srcH, 0, 0, canvas.width, srcH);
        pdf.addImage(tempCanvas.toDataURL('image/png'), 'PNG', margin, margin, contentW, drawH);
        pdf.setFontSize(7);
        pdf.setTextColor(100);
        pdf.text(`BCE-4X GOLDEN V6+ | Module Pedagogique | ${speciesKey} / ${seasonKey} | Page ${pageNum + 1}`, pageW / 2, pageH - 3, { align: 'center' });
        yPos += usableH;
        pageNum++;
      }
      pdf.save(`HUNTIQ_Pedagogie_${speciesKey}_${seasonKey}.pdf`);
      setExpandedId(prevExpanded);
    } catch (err) {
      console.error('[PEDAGOGIE PDF]', err);
    } finally {
      setPdfExporting(false);
    }
  }, [speciesKey, seasonKey, pdfExporting, expandedId]);

  if (!PEDAGOGIE_SALINE_ENABLED) return null;

  const toggleSection = (id) => setExpandedId(prev => prev === id ? null : id);

  return (
    <div className="mt-4" data-testid="pedagogie-module" ref={moduleRef}>
      {/* ═══ SÉPARATEUR VISUEL ═══ */}
      <div className="flex items-center gap-3 py-2 mb-1" data-testid="pedagogie-separator">
        <div className="flex-1 h-[2px]" style={{ background: `linear-gradient(to right, transparent, ${BIONIC.amber}, transparent)` }} />
        <span className="text-[11px] font-bold tracking-widest uppercase" style={{ color: BIONIC.amber }}>SECTION PEDAGOGIQUE</span>
        <div className="flex-1 h-[2px]" style={{ background: `linear-gradient(to right, transparent, ${BIONIC.amber}, transparent)` }} />
      </div>

      {/* ═══ HEADER — identique au standard SUPRA ═══ */}
      <div className="rounded-lg px-4 py-2.5 mb-2" style={{ backgroundColor: '#1a2744', border: `2px solid ${BIONIC.amber}40`, boxShadow: `0 0 16px ${BIONIC.amber}10` }} data-testid="pedagogie-header">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg flex items-center justify-center flex-shrink-0" style={{ background: `linear-gradient(135deg, ${BIONIC.amber}30, ${BIONIC.amber}10)` }}>
            <BookOpen style={{ color: BIONIC.amber, width: 20, height: 20 }} />
          </div>
          <div className="flex-1 min-w-0">
            <div className="text-[16px] font-black text-white tracking-wide">MODULE PEDAGOGIQUE</div>
            <div className="text-[12px] text-slate-400">Pourquoi ce site est optimal? — {speciesKey} / {seasonKey}</div>
          </div>
          <button onClick={handleExportPDF} disabled={pdfExporting}
            className="flex items-center gap-1.5 h-8 px-3 rounded-lg text-[12px] font-bold transition-all hover:brightness-125 active:scale-[0.97] disabled:opacity-40 cursor-pointer"
            style={{ backgroundColor: `${BIONIC.green}15`, color: BIONIC.green, border: `1.5px solid ${BIONIC.green}40` }}
            data-testid="pedagogie-export-pdf-btn">
            {pdfExporting ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <Download className="h-3.5 w-3.5" />}
            PDF
          </button>
          <span className="text-[12px] font-black px-2.5 py-0.5 rounded-lg" style={{ background: `linear-gradient(135deg, ${BIONIC.amber}25, ${BIONIC.amber}10)`, color: BIONIC.amber, border: `1px solid ${BIONIC.amber}40` }}>ULTRA</span>
        </div>
      </div>

      {/* ═══ GRILLE 3 COLONNES — STANDARD GOLDEN ═══ */}
      <div className="grid grid-cols-3 gap-2" data-testid="pedagogie-grid">
        {SECTIONS.map((s) => {
          const isExpanded = expandedId === s.id;
          if (isExpanded) {
            return <SectionDetail key={s.id} section={s} onClose={() => setExpandedId(null)} />;
          }
          return (
            <div key={s.id}
              onClick={() => toggleSection(s.id)}
              className="rounded-lg px-3 py-2.5 cursor-pointer transition-all hover:brightness-110 active:scale-[0.98]"
              style={{ backgroundColor: '#1E293B', borderLeft: `3px solid ${s.color}`, boxShadow: '0 2px 6px rgba(0,0,0,0.2)' }}
              data-testid={`pedagogie-card-${s.id}`}>
              {/* Card header */}
              <div className="flex items-center justify-between mb-1.5">
                <div className="flex items-center gap-2">
                  <s.icon style={{ color: s.color, width: 16, height: 16 }} />
                  <span className="text-[13px] font-bold text-white leading-tight">{s.title}</span>
                </div>
                <span className="text-[10px] font-bold px-1.5 py-0.5 rounded flex-shrink-0" style={{ backgroundColor: `${s.color}15`, color: s.color }}>{s.badge}</span>
              </div>
              {/* Card preview — 2-3 lines */}
              <p className="text-[11px] text-slate-400 leading-snug line-clamp-3">{s.preview}</p>
              {/* Card bottom indicator */}
              <div className="flex items-center justify-end mt-1.5">
                <span className="text-[10px] text-slate-600">Cliquer pour voir</span>
                <ChevronDown className="w-3 h-3 text-slate-600 ml-1" />
              </div>
            </div>
          );
        })}
      </div>

      {/* ═══ CAPSULE NARRATIVE — pleine largeur ═══ */}
      <div className="rounded-lg px-4 py-3 mt-2" style={{ backgroundColor: '#1a2744', borderLeft: `4px solid ${BIONIC.cyan}` }} data-testid="pedagogie-narrative">
        <div className="flex items-center gap-2 mb-2">
          <BookOpen style={{ color: BIONIC.cyan, width: 16, height: 16 }} />
          <span className="text-[14px] font-bold text-white">L'Histoire de ta saline</span>
          <span className="text-[11px] font-bold px-1.5 py-0.5 rounded" style={{ backgroundColor: `${BIONIC.cyan}15`, color: BIONIC.cyan }}>{speciesKey} / {seasonKey}</span>
        </div>
        <p className="text-[13px] text-slate-300 leading-relaxed italic">{narrativeText}</p>
        <div className="mt-2 text-center">
          <span className="text-[10px] text-slate-600">BCE-4X GOLDEN V6+ | Module Pedagogique | COMMANDANT STEEVE-MAX</span>
        </div>
      </div>
    </div>
  );
};

export default PedagogieModule;

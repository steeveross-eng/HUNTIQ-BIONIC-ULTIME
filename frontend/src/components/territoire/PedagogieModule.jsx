import React, { useState, useRef, useCallback } from 'react';
import {
  BookOpen, FlaskConical, Leaf, AlertTriangle, Beaker,
  Zap, Shield, ChevronDown, ChevronUp, Mountain, Activity,
  TreeDeciduous, Crown, Eye, Target, Calendar, Ban,
  Heart, Baby, Crosshair, Sparkles, Wheat, Apple,
  CircleAlert, ThermometerSun, Timer, Layers, Star,
  Download, Loader2
} from 'lucide-react';

/**
 * ============================================================
 * MODULE PÉDAGOGIQUE — "Pourquoi ce site est optimal?"
 * ============================================================
 * BCE-4X GOLDEN V6+ | COMMANDANT STEEVE-MAX
 * ENRICHISSEMENT de l'onglet ANALYSE
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

const GOLDEN = {
  cardBg: '#1E293B',
  pageBg: '#0F172A',
  shadow: '0 2px 8px rgba(0,0,0,0.25)',
};

// ═══════════════════════════════════════════════════════
// DONNÉES PÉDAGOGIQUES COMPLÈTES
// ═══════════════════════════════════════════════════════

const BESOINS_MINERAUX = [
  {
    groupe: 'Males alpha',
    icon: Crown,
    color: BIONIC.amber,
    mineraux: [
      { nom: 'Sodium (Na)', besoin: 'CRITIQUE', desc: 'Regulation osmotique, hydratation sous effort territorial' },
      { nom: 'Calcium (Ca)', besoin: 'TRES ELEVE', desc: 'Croissance et mineralisation du panache (velours)' },
      { nom: 'Phosphore (P)', besoin: 'TRES ELEVE', desc: 'Co-facteur calcium, structure osseuse et bois' },
      { nom: 'Magnesium (Mg)', besoin: 'ELEVE', desc: 'Fixation du calcium, fonction neuromusculaire' },
    ],
  },
  {
    groupe: 'Femelles (gestation + lactation)',
    icon: Heart,
    color: BIONIC.pink,
    mineraux: [
      { nom: 'Calcium (Ca)', besoin: 'EXTREME', desc: 'Besoins x4 en gestation tardive et lactation' },
      { nom: 'Phosphore (P)', besoin: 'EXTREME', desc: 'Besoins x3, developpement squelettique du faon' },
      { nom: 'Sodium (Na)', besoin: 'ELEVE', desc: 'Production de lait, equilibre electrolytique' },
      { nom: 'Fer (Fe)', besoin: 'ELEVE', desc: 'Volume sanguin augmente pendant la gestation' },
    ],
  },
  {
    groupe: 'Veaux (croissance)',
    icon: Baby,
    color: BIONIC.cyan,
    mineraux: [
      { nom: 'Calcium (Ca)', besoin: 'CRITIQUE', desc: 'Ossification rapide, croissance squelettique' },
      { nom: 'Phosphore (P)', besoin: 'CRITIQUE', desc: 'Ratio Ca:P optimal 2:1 pour croissance' },
      { nom: 'Zinc (Zn)', besoin: 'ELEVE', desc: 'Systeme immunitaire en developpement' },
      { nom: 'Cuivre (Cu)', besoin: 'MODERE', desc: 'Formation des tissus conjonctifs' },
    ],
  },
  {
    groupe: 'Periode de chasse',
    icon: Crosshair,
    color: BIONIC.red,
    mineraux: [
      { nom: 'Sodium (Na)', besoin: 'CRITIQUE', desc: 'Compensation des pertes hydriques, attraction maximale' },
      { nom: 'Potassium (K)', besoin: 'ELEVE', desc: 'Fonction musculaire et cardiaque sous stress' },
      { nom: 'Magnesium (Mg)', besoin: 'MODERE', desc: 'Anti-stress, fonction neuromusculaire' },
      { nom: 'Selenium (Se)', besoin: 'MODERE', desc: 'Antioxydant, protection cellulaire' },
    ],
  },
];

const BESOINS_PROTEINES = [
  { groupe: 'Males', quantite: '500 g / 3 jours', icon: Crown, color: BIONIC.amber, detail: 'Maintien masse musculaire, regeneration panache, activite territoriale' },
  { groupe: 'Femelles', quantite: '300-400 g / 3 jours', icon: Heart, color: BIONIC.pink, detail: 'Gestation, lactation, production de lait riche en proteines' },
  { groupe: 'Veaux', quantite: '200-300 g / 3 jours', icon: Baby, color: BIONIC.cyan, detail: 'Croissance rapide, developpement musculaire et organes' },
];

const OLIGO_ELEMENTS = [
  { sym: 'Zn', nom: 'Zinc', role: 'Immunite, reproduction, cicatrisation', besoin: '50 mg/kg', color: BIONIC.blue },
  { sym: 'Cu', nom: 'Cuivre', role: 'Hematopoiese, keratinisation, pigmentation', besoin: '10-15 mg/kg', color: BIONIC.orange },
  { sym: 'Se', nom: 'Selenium', role: 'Antioxydant, protection cellulaire, fertilite', besoin: '0.1-0.3 mg/kg', color: BIONIC.green },
  { sym: 'Fe', nom: 'Fer', role: 'Transport O2, hemoglobine, myoglobine', besoin: '50-100 mg/kg', color: BIONIC.red },
  { sym: 'Mn', nom: 'Manganese', role: 'Formation osseuse, metabolisme energetique', besoin: '40-60 mg/kg', color: BIONIC.purple },
  { sym: 'I', nom: 'Iode', role: 'Fonction thyroidienne, thermoregulation', besoin: '0.2-0.5 mg/kg', color: BIONIC.teal },
];

const SOLUTIONS_TERRAIN = [
  { nom: 'Soya', categorie: 'Legumineuse', proteines: 'Tres eleve (35-40%)', mineraux: 'Ca, P, K, Fe', saison: 'Ete-automne', color: BIONIC.green },
  { nom: 'Luzerne', categorie: 'Legumineuse', proteines: 'Eleve (18-22%)', mineraux: 'Ca, Mg, K', saison: 'Printemps-automne', color: BIONIC.green },
  { nom: 'Trefle', categorie: 'Legumineuse', proteines: 'Modere (15-20%)', mineraux: 'Ca, P, Mg', saison: 'Printemps-ete', color: BIONIC.teal },
  { nom: 'Chicoree', categorie: 'Herbacee', proteines: 'Modere (12-18%)', mineraux: 'Zn, Cu, Se', saison: 'Ete-automne', color: BIONIC.cyan },
  { nom: 'Mais', categorie: 'Cereale', proteines: 'Faible (8-10%)', mineraux: 'P, K, energie ++', saison: 'Automne-hiver', color: BIONIC.amber },
  { nom: 'Pommes', categorie: 'Fruit', proteines: 'Tres faible', mineraux: 'K, sucres rapides', saison: 'Automne', color: BIONIC.red },
  { nom: 'Betteraves', categorie: 'Racine', proteines: 'Faible (6-8%)', mineraux: 'Fe, Mn, K, energie', saison: 'Automne', color: BIONIC.purple },
];

const COMPARATIF_SUPPORTS = [
  { nom: 'Souche en decomposition', score: 98, color: BIONIC.green, desc: 'Absorption maximale. Surface poreuse ideale. Retention longue duree. Le meilleur support naturel disponible.', avantages: ['Surface poreuse naturelle', 'Retention minerale maximale', 'Biodegradable'] },
  { nom: 'Souche recente', score: 82, color: BIONIC.green, desc: 'Bonne absorption. La porosite se developpe avec le temps. Necessite un trempage initial pour activer la surface.', avantages: ['Bonne durabilite', 'Surface stable', 'Absorption progressive'] },
  { nom: 'Bois mou (epinette, sapin)', score: 75, color: BIONIC.yellow, desc: 'Absorption moderee a bonne. Structure fibreuse absorbante. Cout reduit, accessible facilement en foret boreale.', avantages: ['Abondant', 'Cout zero', 'Bon compromis'] },
  { nom: 'Bois franc (erable, bouleau)', score: 55, color: BIONIC.orange, desc: 'Absorption faible. Structure dense et peu poreuse. Dissolution rapide des mineraux. Non recommande seul.', avantages: ['Durable', 'Structure solide'] },
  { nom: 'Baton / piquet', score: 30, color: BIONIC.red, desc: 'Tres mauvaise retention. Surface reduite. Mineraux laves par la pluie rapidement. A eviter comme support principal.', avantages: ['Facile a installer'] },
];

const STRATEGIES_OPTIMISATION = [
  {
    titre: 'Mini-champ d\'alimentation',
    icon: Wheat,
    color: BIONIC.green,
    desc: 'Creer un micro-habitat nutritif de 20-50m2 a proximite de la saline. Planter trefle, chicoree et luzerne pour fournir proteines et mineraux complementaires.',
    actions: ['Defricher 20-50m2 pres de la saline', 'Semer un melange trefle/chicoree/luzerne', 'Maintenir par fauchage annuel', 'Ne jamais utiliser d\'herbicides'],
  },
  {
    titre: 'Synergies mineraux / proteines / energie',
    icon: Zap,
    color: BIONIC.amber,
    desc: 'Combiner sources minerales (sel, chaux), proteiques (soya, luzerne) et energetiques (mais, betteraves) pour creer un site complet repondant a tous les besoins.',
    actions: ['Base minerale: bloc sel + chaux sur souche', 'Complement proteique: soya/luzerne a 5-10m', 'Source energetique: mais/betteraves en automne', 'Ratio: 60% mineraux, 25% proteines, 15% energie'],
  },
  {
    titre: 'Strategies territoriales',
    icon: Target,
    color: BIONIC.red,
    desc: 'Positionner la saline sur un axe de deplacement naturel, en zone de transition foret/clairiere, avec couvert lateral minimum 60% pour securiser les males dominants.',
    actions: ['Zone de transition foret-clairiere', 'Couvert lateral 60%+ (coniferes)', 'Proximite d\'un corridor de deplacement', 'Distance minimale 200m des routes/chemins'],
  },
  {
    titre: 'Strategies comportementales',
    icon: Eye,
    color: BIONIC.purple,
    desc: 'Exploiter les patterns comportementaux: heures de visite (aube/crepuscule), frequence saisonniere, et marquage territorial pour maximiser les observations.',
    actions: ['Visites matinales: 5h-8h (pic)', 'Visites crepusculaires: 18h-21h', 'Frequence male adulte: 3-5x/semaine (ete)', 'Surveiller les frottoirs dans un rayon de 200m'],
  },
  {
    titre: 'Strategies saisonnieres',
    icon: Calendar,
    color: BIONIC.blue,
    desc: 'Adapter la composition et le rythme de rafraichissement selon la saison biologique. Chaque saison exige un apport different en mineraux et en energie.',
    actions: ['Printemps: Sodium prioritaire (sortie d\'hiver)', 'Ete: Ca + P maximum (panache en velours)', 'Pre-rut: Reduire les visites, maintenir l\'apport', 'Hiver: Apport minimal, energie prioritaire'],
  },
];

const GESTION_PRE_CHASSE = [
  { regle: 'Rafraichir toutes les 2 semaines', icon: Timer, color: BIONIC.blue, detail: 'Maintenir un rythme regulier de rechargement pour conditionner les animaux a visiter le site. La regularite cree l\'habitude.' },
  { regle: 'Doubler les quantites 2 semaines avant la chasse', icon: Zap, color: BIONIC.amber, detail: 'Augmenter l\'attractivite du site avec un apport massif de mineraux et sel. Cela intensifie la frequentation juste avant la periode critique.' },
  { regle: 'Arreter tout rafraichissement 15 jours avant la chasse', icon: Ban, color: BIONIC.red, detail: 'ZERO visite humaine dans les 15 jours precedant la chasse. Laisser l\'odeur humaine se dissiper completement.' },
  { regle: 'Laisser le site completement tranquille', icon: Shield, color: BIONIC.green, detail: 'Aucune camera a relever, aucun passage, aucune verification. Le silence total est la cle du succes.' },
  { regle: 'Maintenir un support humide et absorbant', icon: Mountain, color: BIONIC.teal, detail: 'Verifier avant la derniere visite que la souche/support est bien saturee. Un support humide diffuse les mineraux plus longtemps et plus efficacement.' },
];

const HYPER_ATTRACTIVE = {
  titre: 'Hyper-attractive en periode de chasse',
  icon: Star,
  color: BIONIC.amber,
  items: [
    { label: 'Timing', desc: 'Le site doit avoir au moins 6-8 semaines d\'historique de frequentation avant la chasse.' },
    { label: 'Composition', desc: 'Melange sodium + calcium + pommes fermentees = combinaison olfactive irresistible.' },
    { label: 'Support', desc: 'Souche en decomposition saturee depuis 3+ rechargements = diffusion lente et constante.' },
    { label: 'Environnement', desc: 'Mini-champ adjacent avec trefle/chicoree encore vert en octobre = source proteique active.' },
    { label: 'Quietude', desc: '15 jours minimum sans presence humaine. Les males dominants ne tolerent aucune perturbation recente.' },
    { label: 'Vent', desc: 'Positionner l\'affut en fonction du vent dominant. Le cerf approche TOUJOURS face au vent.' },
  ],
};

const A_EVITER = [
  { item: 'Visites trop frequentes', icon: CircleAlert, desc: 'Chaque visite humaine laisse une trace olfactive de 48-72h. Maximum 1 visite / 2 semaines.' },
  { item: 'Produits miracles / aromatises', icon: CircleAlert, desc: 'Les attractifs commerciaux aromatises creent une dependance artificielle et alertent les males matures.' },
  { item: 'Exces de sel', icon: CircleAlert, desc: 'Trop de sodium brule la vegetation environnante et cree une zone morte. Doser: 2-3 kg / rechargement max.' },
  { item: 'Produits non certifies', icon: CircleAlert, desc: 'Risque de contamination (plomb, metaux lourds). Utiliser UNIQUEMENT des produits de qualite alimentaire.' },
  { item: 'Sol nu sans support', icon: CircleAlert, desc: 'Les mineraux sont laves par la premiere pluie. Toujours utiliser une souche ou du bois mou comme support absorbant.' },
  { item: 'Corridors principaux', icon: CircleAlert, desc: 'Ne JAMAIS installer une saline sur un corridor principal. Les animaux ne s\'arretent pas, ils traversent.' },
  { item: 'Sites exposes (sans couvert)', icon: CircleAlert, desc: 'Un site sans couvert lateral (< 40%) ne sera visite que de nuit. Les males matures exigent la securite visuelle.' },
  { item: 'Changement constant de recette', icon: CircleAlert, desc: 'La constance est cle. Un animal s\'habitue a une composition. Changer cree de la mefiance.' },
  { item: 'Rafraichissement trop proche de la chasse', icon: CircleAlert, desc: 'JAMAIS de visite dans les 15 jours avant la chasse. L\'odeur humaine recente = site deserte.' },
];

// ═══════════════════════════════════════════════════════
// CAPSULE NARRATIVE — "L'Histoire de ta saline"
// ═══════════════════════════════════════════════════════
const NARRATIVES = {
  orignal: {
    printemps: "Apres cinq longs mois d'hiver, l'orignal sort de l'hivernage en deficit severe de sodium. Son organisme, affaibli par un regime exclusif de ramilles, cherche desesperement les mineraux perdus. C'est ici que ta saline entre en jeu. Positionnee sur un sol retentif avec un support poreux, elle devient le premier point de ravitaillement mineral du printemps. Les femelles gestantes, dont les besoins en calcium sont multiplies par quatre, reviendront regulierement. Chaque visite renforce l'habitude, chaque rechargement consolide la fidelite du site.",
    ete: "Le panache est en velours. La croissance est explosive — calcium, phosphore et magnesium sont consommes a un rythme sans precedent. L'orignal male adulte visite les salines 4 a 7 fois par semaine, parfois pendant 15 a 25 minutes. C'est la saison ou ta saline travaille le plus dur. Le support doit etre sature, la composition riche en calcium et phosphore. Chaque gramme de mineral absorbe se transforme en centimetres de panache. Ce site n'est pas juste un point sur la carte — c'est une station de croissance.",
    rut: "L'activite territoriale est a son maximum. Le male dominant patrouille, marque, combat. Les pertes hydriques sont majeures — le sodium devient vital. Ta saline est sa station de ravitaillement entre deux patrouilles. Les visites sont courtes (moins de 5 minutes) mais strategiques. Le male suit aussi les femelles qui, elles, continuent de visiter regulierement. Un site bien positionne en transition foret-clairiere avec un couvert lateral de 60%+ devient un point de passage obligatoire.",
    hiver: "Le metabolisme hivernal ralentit tout. Les besoins sont minimaux, mais le sodium reste recherche. Les visites sont sporadiques — 1 a 2 par semaine selon la meteo. Ta saline entre en mode maintenance. Le support garde ses reserves minerales sous la neige, pret pour le prochain printemps. C'est le moment de planifier, pas d'intervenir.",
  },
  chevreuil: {
    printemps: "Le chevreuil sort d'hiver epuise. Ses reserves minerales sont au plus bas. Le sodium est le premier mineral qu'il cherche activement — son instinct le guide vers les sources salines naturelles ou artificielles. Ta saline, positionnee dans cette zone optimale, devient son refuge mineral. Le calcium et le phosphore sont critiques pour la regeneration du panache qui demarre des avril. Les visites matinales (5h-8h) sont les plus frequentes.",
    ete: "Phase de croissance maximale du panache. Les besoins en calcium et phosphore sont multiplies par trois. Le magnesium soutient la fixation minerale dans les tissus osseux. L'appetit mineral est a son pic absolu. Ta saline recoit 4 a 7 visites par semaine, avec des durees prolongees de 15 a 25 minutes. Le marquage territorial autour du site confirme que les males dominants ont adopte cette zone.",
    pre_rut: "La transition hormonale commence. La testosterone monte. Les mineraux de structure (Ca, P) sont deja fixes dans le panache durci. Le sodium maintient l'hydratation sous l'effort territorial croissant. Les visites deviennent irregulieres — les males commencent a patrouiller. Les frottoirs apparaissent dans un rayon de 200m. Ta saline est au centre de leur territoire.",
    rut: "Activite maximale. Perte de poids de 20-30%. Le sodium compense la deshydratation extreme. Le potassium soutient la fonction musculaire et cardiaque sous stress intense. Les visites sont rares (1-2/semaine) et courtes (< 5 min). Mais les femelles continuent de venir — et les males suivent les femelles. Ta saline est un point d'intersection strategique.",
    post_rut: "Recuperation energetique. Les besoins en mineraux de structure baissent. L'appetit mineral reprend progressivement. C'est le moment ou la fidelite au site se consolide pour la saison suivante. Un rechargement modere maintient le lien.",
    hiver: "Phase de survie. Metabolisme ralenti. Les besoins sont minimaux mais le sodium reste recherche lors des redoux. Ta saline conserve ses reserves sous la neige, prete a reprendre du service au prochain printemps.",
  },
};

// ═══════════════════════════════════════════════════════
// COMPOSANTS UI — STANDARD GOLDEN BCE-4X
// ═══════════════════════════════════════════════════════

const IC = ({ Icon, color, sz = 28 }) => (
  <div className="rounded-full flex items-center justify-center flex-shrink-0" style={{ width: sz, height: sz, backgroundColor: `${color}20` }}>
    <Icon style={{ color, width: sz * 0.5, height: sz * 0.5 }} />
  </div>
);

const PedaCard = ({ children, testId, accentColor, compact = true }) => (
  <div className={`rounded-lg ${compact ? 'px-2.5 py-2' : 'px-4 py-3'}`}
    style={{ backgroundColor: GOLDEN.cardBg, boxShadow: GOLDEN.shadow, borderLeft: accentColor ? `3px solid ${accentColor}` : 'none' }}
    data-testid={testId}>
    {children}
  </div>
);

const PedaCollapsible = ({ icon: Icon, title, color, badge, children, defaultOpen = false, testId }) => {
  const [open, setOpen] = useState(defaultOpen);
  return (
    <div className="rounded-lg px-4 py-2.5" style={{ backgroundColor: GOLDEN.cardBg, boxShadow: GOLDEN.shadow }} data-testid={testId}>
      <button onClick={() => setOpen(v => !v)} className="w-full flex items-center justify-between cursor-pointer">
        <div className="flex items-center gap-3">
          <IC Icon={Icon} color={color} />
          <span className="text-[16px] font-bold text-white">{title}</span>
        </div>
        <div className="flex items-center gap-2">
          {badge && <span className="text-[14px] font-semibold px-2.5 py-0.5 rounded-lg" style={{ backgroundColor: `${color}18`, color }}>{badge}</span>}
          {open ? <ChevronUp className="h-4 w-4 text-slate-500" /> : <ChevronDown className="h-4 w-4 text-slate-500" />}
        </div>
      </button>
      {open && <div className="mt-3">{children}</div>}
    </div>
  );
};

const BesoinTag = ({ level }) => {
  const colors = { EXTREME: BIONIC.red, CRITIQUE: BIONIC.red, 'TRES ELEVE': BIONIC.orange, ELEVE: BIONIC.amber, MODERE: BIONIC.yellow };
  const c = colors[level] || BIONIC.blue;
  return <span className="text-[12px] font-black px-2 py-0.5 rounded" style={{ backgroundColor: `${c}18`, color: c }}>{level}</span>;
};

// ═══════════════════════════════════════════════════════
// COMPOSANT PRINCIPAL — PedagogieModule
// ═══════════════════════════════════════════════════════

const PedagogieModule = ({ species = 'orignal', season = 'printemps', score, gc }) => {
  const speciesKey = species.toLowerCase();
  const seasonKey = season.toLowerCase();
  const narrativeSpecies = NARRATIVES[speciesKey] || NARRATIVES.orignal;
  const narrativeText = narrativeSpecies[seasonKey] || narrativeSpecies.printemps || narrativeSpecies[Object.keys(narrativeSpecies)[0]];
  const moduleRef = useRef(null);
  const [pdfExporting, setPdfExporting] = useState(false);

  const handleExportPDF = useCallback(async () => {
    if (!moduleRef.current || pdfExporting) return;
    setPdfExporting(true);
    try {
      const html2canvas = (await import('html2canvas')).default;
      const { jsPDF } = await import('jspdf');
      // Temporarily expand all collapsibles for PDF capture
      const buttons = moduleRef.current.querySelectorAll('[data-testid^="pedagogie-"] button');
      buttons.forEach(btn => btn.click());
      await new Promise(r => setTimeout(r, 300));
      const canvas = await html2canvas(moduleRef.current, {
        backgroundColor: '#0F172A',
        scale: 2,
        useCORS: true,
        logging: false,
      });
      const imgData = canvas.toDataURL('image/png');
      const pdf = new jsPDF({ orientation: 'portrait', unit: 'mm', format: 'a4' });
      const pageW = pdf.internal.pageSize.getWidth();
      const pageH = pdf.internal.pageSize.getHeight();
      const margin = 8;
      const contentW = pageW - margin * 2;
      const imgRatio = canvas.height / canvas.width;
      const contentH = contentW * imgRatio;
      // Multi-page support
      let yPos = 0;
      const totalH = contentH;
      const usableH = pageH - margin * 2;
      let pageNum = 0;
      while (yPos < totalH) {
        if (pageNum > 0) pdf.addPage();
        const srcY = (yPos / totalH) * canvas.height;
        const srcH = Math.min((usableH / totalH) * canvas.height, canvas.height - srcY);
        const drawH = Math.min(usableH, totalH - yPos);
        const tempCanvas = document.createElement('canvas');
        tempCanvas.width = canvas.width;
        tempCanvas.height = srcH;
        const ctx = tempCanvas.getContext('2d');
        ctx.drawImage(canvas, 0, srcY, canvas.width, srcH, 0, 0, canvas.width, srcH);
        pdf.addImage(tempCanvas.toDataURL('image/png'), 'PNG', margin, margin, contentW, drawH);
        // Footer
        pdf.setFontSize(7);
        pdf.setTextColor(100);
        pdf.text(`BCE-4X GOLDEN V6+ | Module Pedagogique | ${speciesKey} / ${seasonKey} | Page ${pageNum + 1}`, pageW / 2, pageH - 3, { align: 'center' });
        yPos += usableH;
        pageNum++;
      }
      pdf.save(`HUNTIQ_Pedagogie_${speciesKey}_${seasonKey}.pdf`);
    } catch (err) {
      console.error('[PEDAGOGIE PDF]', err);
    } finally {
      setPdfExporting(false);
    }
  }, [speciesKey, seasonKey, pdfExporting]);

  if (!PEDAGOGIE_SALINE_ENABLED) return null;

  return (
    <div className="space-y-1.5 mt-4" data-testid="pedagogie-module" ref={moduleRef}>
      {/* ═══ SÉPARATEUR VISUEL — ENTRÉE MODULE PÉDAGOGIQUE ═══ */}
      <div className="flex items-center gap-3 py-2" data-testid="pedagogie-separator">
        <div className="flex-1 h-[2px]" style={{ background: `linear-gradient(to right, transparent, ${BIONIC.amber}, transparent)` }} />
        <span className="text-[12px] font-bold tracking-widest uppercase" style={{ color: BIONIC.amber }}>SECTION PEDAGOGIQUE</span>
        <div className="flex-1 h-[2px]" style={{ background: `linear-gradient(to right, transparent, ${BIONIC.amber}, transparent)` }} />
      </div>

      {/* ═══ HEADER MODULE PÉDAGOGIQUE — HAUTE VISIBILITÉ + EXPORT PDF ═══ */}
      <div className="rounded-lg px-4 py-3" style={{ backgroundColor: '#1a2744', boxShadow: `0 0 20px ${BIONIC.amber}15, ${GOLDEN.shadow}`, border: `2px solid ${BIONIC.amber}40` }} data-testid="pedagogie-header">
        <div className="flex items-center gap-3">
          <div className="w-[40px] h-[40px] rounded-xl flex items-center justify-center flex-shrink-0" style={{ background: `linear-gradient(135deg, ${BIONIC.amber}35, ${BIONIC.amber}10)` }}>
            <BookOpen style={{ color: BIONIC.amber, width: 22, height: 22 }} />
          </div>
          <div className="flex-1">
            <div className="text-[18px] font-black text-white tracking-wide">MODULE PEDAGOGIQUE</div>
            <div className="text-[14px] text-slate-400">Pourquoi ce site est optimal? — {speciesKey} / {seasonKey}</div>
          </div>
          <button onClick={handleExportPDF} disabled={pdfExporting}
            className="flex items-center gap-2 h-9 px-4 rounded-lg text-[13px] font-bold uppercase tracking-wider transition-all hover:brightness-125 active:scale-[0.97] disabled:opacity-40 disabled:cursor-not-allowed"
            style={{ backgroundColor: `${BIONIC.green}18`, color: BIONIC.green, border: `2px solid ${BIONIC.green}50` }}
            data-testid="pedagogie-export-pdf-btn">
            {pdfExporting ? <Loader2 className="h-4 w-4 animate-spin" /> : <Download className="h-4 w-4" />}
            {pdfExporting ? 'Export...' : 'PDF'}
          </button>
          <span className="text-[14px] font-black px-3 py-1 rounded-lg" style={{ background: `linear-gradient(135deg, ${BIONIC.amber}30, ${BIONIC.amber}15)`, color: BIONIC.amber, border: `1px solid ${BIONIC.amber}50` }}>ULTRA</span>
        </div>
      </div>

      {/* ═══ 1. BESOINS MINÉRAUX PAR GROUPE ═══ */}
      <PedaCollapsible icon={FlaskConical} title="Besoins mineraux par groupe" color={BIONIC.orange} badge="4 groupes" testId="pedagogie-besoins-mineraux">
        <div className="grid grid-cols-2 gap-1.5">
          {BESOINS_MINERAUX.map((g, i) => (
            <PedaCard key={i} testId={`pedagogie-groupe-${i}`} accentColor={g.color}>
              <div className="flex items-center gap-2 mb-2">
                <IC Icon={g.icon} color={g.color} sz={24} />
                <span className="text-[14px] font-bold text-white">{g.groupe}</span>
              </div>
              {g.mineraux.map((m, j) => (
                <div key={j} className="py-1 border-b" style={{ borderColor: 'rgba(255,255,255,0.04)' }}>
                  <div className="flex items-center justify-between">
                    <span className="text-[14px] text-white font-semibold">{m.nom}</span>
                    <BesoinTag level={m.besoin} />
                  </div>
                  <p className="text-[12px] text-slate-500 mt-0.5">{m.desc}</p>
                </div>
              ))}
            </PedaCard>
          ))}
        </div>
      </PedaCollapsible>

      {/* ═══ 2. BESOINS EN PROTÉINES ═══ */}
      <PedaCollapsible icon={Zap} title="Besoins en proteines" color={BIONIC.green} badge="3 groupes" testId="pedagogie-proteines">
        <div className="space-y-1.5">
          {BESOINS_PROTEINES.map((p, i) => (
            <PedaCard key={i} testId={`pedagogie-proteine-${i}`} accentColor={p.color}>
              <div className="flex items-center gap-3">
                <IC Icon={p.icon} color={p.color} sz={28} />
                <div className="flex-1">
                  <div className="flex items-center justify-between">
                    <span className="text-[16px] font-bold text-white">{p.groupe}</span>
                    <span className="text-[18px] font-black" style={{ color: p.color }}>{p.quantite}</span>
                  </div>
                  <p className="text-[14px] text-slate-400 mt-0.5">{p.detail}</p>
                </div>
              </div>
            </PedaCard>
          ))}
        </div>
      </PedaCollapsible>

      {/* ═══ 3. OLIGO-ÉLÉMENTS ESSENTIELS ═══ */}
      <PedaCollapsible icon={Beaker} title="Oligo-elements essentiels" color={BIONIC.purple} badge="6 elements" testId="pedagogie-oligo">
        <div className="grid grid-cols-3 gap-1.5">
          {OLIGO_ELEMENTS.map((e, i) => (
            <PedaCard key={i} testId={`pedagogie-oligo-${e.sym}`} accentColor={e.color}>
              <div className="flex items-center gap-2 mb-1.5">
                <div className="w-[28px] h-[28px] rounded-lg flex items-center justify-center font-black text-[14px]" style={{ backgroundColor: `${e.color}20`, color: e.color }}>{e.sym}</div>
                <span className="text-[14px] font-bold text-white">{e.nom}</span>
              </div>
              <p className="text-[12px] text-slate-400 leading-snug">{e.role}</p>
              <div className="flex justify-between mt-1.5 pt-1 border-t" style={{ borderColor: 'rgba(255,255,255,0.04)' }}>
                <span className="text-[12px] text-slate-500">Besoin</span>
                <span className="text-[12px] font-bold" style={{ color: e.color }}>{e.besoin}</span>
              </div>
            </PedaCard>
          ))}
        </div>
      </PedaCollapsible>

      {/* ═══ 4. SOLUTIONS TERRAIN ═══ */}
      <PedaCollapsible icon={Leaf} title="Solutions terrain" color={BIONIC.green} badge="7 solutions" testId="pedagogie-solutions-terrain">
        <div className="space-y-1">
          {SOLUTIONS_TERRAIN.map((s, i) => (
            <div key={i} className="flex items-center gap-3 py-1.5 border-b" style={{ borderColor: 'rgba(255,255,255,0.04)' }} data-testid={`pedagogie-solution-${i}`}>
              <IC Icon={Leaf} color={s.color} sz={24} />
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <span className="text-[14px] font-bold text-white">{s.nom}</span>
                  <span className="text-[12px] px-1.5 py-0.5 rounded" style={{ backgroundColor: `${s.color}15`, color: s.color }}>{s.categorie}</span>
                </div>
                <div className="flex gap-4 text-[12px] text-slate-400 mt-0.5">
                  <span>Prot: {s.proteines}</span>
                  <span>Min: {s.mineraux}</span>
                  <span>Saison: {s.saison}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </PedaCollapsible>

      {/* ═══ 5. COMPARATIF VISUEL DES SUPPORTS ═══ */}
      <PedaCollapsible icon={Layers} title="Comparatif visuel des supports" color={BIONIC.amber} badge="Hierarchie" testId="pedagogie-comparatif-supports">
        <div className="space-y-1.5">
          {COMPARATIF_SUPPORTS.map((s, i) => (
            <PedaCard key={i} testId={`pedagogie-support-${i}`} accentColor={s.color}>
              <div className="flex items-center gap-3">
                <div className="w-[42px] h-[42px] rounded-xl flex items-center justify-center flex-shrink-0" style={{ background: `linear-gradient(135deg, ${s.color}30, ${s.color}10)` }}>
                  <span className="text-[18px] font-black tabular-nums" style={{ color: s.color }}>{s.score}</span>
                </div>
                <div className="flex-1 min-w-0">
                  <div className="text-[14px] font-bold text-white">{s.nom}</div>
                  <p className="text-[12px] text-slate-400 mt-0.5 leading-snug">{s.desc}</p>
                  <div className="flex gap-1.5 mt-1 flex-wrap">
                    {s.avantages.map((a, j) => (
                      <span key={j} className="text-[11px] px-1.5 py-0.5 rounded" style={{ backgroundColor: `${s.color}12`, color: s.color }}>{a}</span>
                    ))}
                  </div>
                </div>
              </div>
              {/* Barre de score */}
              <div className="mt-2 h-[6px] rounded-full overflow-hidden" style={{ backgroundColor: 'rgba(255,255,255,0.06)' }}>
                <div className="h-full rounded-full transition-all duration-500" style={{ width: `${s.score}%`, backgroundColor: s.color }} />
              </div>
            </PedaCard>
          ))}
        </div>
      </PedaCollapsible>

      {/* ═══ 6. STRATÉGIES D'OPTIMISATION ═══ */}
      <PedaCollapsible icon={Target} title="Strategies d'optimisation" color={BIONIC.red} badge="5 strategies" testId="pedagogie-strategies">
        <div className="space-y-1.5">
          {STRATEGIES_OPTIMISATION.map((s, i) => (
            <PedaCard key={i} testId={`pedagogie-strategie-${i}`} accentColor={s.color}>
              <div className="flex items-center gap-2 mb-2">
                <IC Icon={s.icon} color={s.color} sz={24} />
                <span className="text-[14px] font-bold text-white">{s.titre}</span>
              </div>
              <p className="text-[14px] text-slate-300 leading-relaxed mb-2">{s.desc}</p>
              <div className="rounded-lg px-3 py-2" style={{ backgroundColor: GOLDEN.pageBg }}>
                {s.actions.map((a, j) => (
                  <div key={j} className="flex items-start gap-2 py-0.5">
                    <span className="text-[12px] mt-0.5 flex-shrink-0" style={{ color: s.color }}>&#9670;</span>
                    <span className="text-[12px] text-slate-400">{a}</span>
                  </div>
                ))}
              </div>
            </PedaCard>
          ))}
        </div>
      </PedaCollapsible>

      {/* ═══ 7. GESTION PRÉ-CHASSE OPTIMISÉE ═══ */}
      <PedaCollapsible icon={Calendar} title="Gestion pre-chasse optimisee" color={BIONIC.blue} badge="5 regles" testId="pedagogie-pre-chasse">
        <div className="space-y-1.5">
          {GESTION_PRE_CHASSE.map((r, i) => (
            <PedaCard key={i} testId={`pedagogie-regle-${i}`} accentColor={r.color}>
              <div className="flex items-center gap-3">
                <IC Icon={r.icon} color={r.color} sz={28} />
                <div className="flex-1">
                  <div className="text-[14px] font-bold text-white">{r.regle}</div>
                  <p className="text-[12px] text-slate-400 mt-0.5 leading-snug">{r.detail}</p>
                </div>
              </div>
            </PedaCard>
          ))}
        </div>
      </PedaCollapsible>

      {/* ═══ 8. HYPER-ATTRACTIVE PÉRIODE DE CHASSE ═══ */}
      <PedaCollapsible icon={Star} title={HYPER_ATTRACTIVE.titre} color={BIONIC.amber} badge="ELITE" testId="pedagogie-hyper-attractive">
        <div className="grid grid-cols-2 gap-1.5">
          {HYPER_ATTRACTIVE.items.map((item, i) => (
            <PedaCard key={i} testId={`pedagogie-hyper-${i}`} accentColor={BIONIC.amber}>
              <div className="text-[14px] font-bold text-amber-400 mb-1">{item.label}</div>
              <p className="text-[12px] text-slate-400 leading-snug">{item.desc}</p>
            </PedaCard>
          ))}
        </div>
      </PedaCollapsible>

      {/* ═══ 9. À ÉVITER ═══ */}
      <PedaCollapsible icon={AlertTriangle} title="A EVITER" color={BIONIC.red} badge="9 erreurs" testId="pedagogie-a-eviter">
        <div className="space-y-1">
          {A_EVITER.map((e, i) => (
            <div key={i} className="flex items-start gap-3 py-2 border-b" style={{ borderColor: 'rgba(255,255,255,0.04)' }} data-testid={`pedagogie-eviter-${i}`}>
              <div className="w-[24px] h-[24px] rounded-full flex items-center justify-center flex-shrink-0 mt-0.5" style={{ backgroundColor: `${BIONIC.red}20` }}>
                <Ban style={{ color: BIONIC.red, width: 12, height: 12 }} />
              </div>
              <div className="flex-1">
                <div className="text-[14px] font-bold text-red-400">{e.item}</div>
                <p className="text-[12px] text-slate-400 mt-0.5 leading-snug">{e.desc}</p>
              </div>
            </div>
          ))}
        </div>
      </PedaCollapsible>

      {/* ═══ 10. CAPSULE NARRATIVE — "L'Histoire de ta saline" ═══ */}
      <PedaCollapsible icon={BookOpen} title="L'Histoire de ta saline" color={BIONIC.cyan} badge={`${speciesKey} / ${seasonKey}`} defaultOpen={true} testId="pedagogie-narrative">
        <div className="rounded-lg px-4 py-3" style={{ backgroundColor: GOLDEN.pageBg, borderLeft: `4px solid ${BIONIC.cyan}` }}>
          <p className="text-[14px] text-slate-300 leading-relaxed italic">{narrativeText}</p>
        </div>
        <div className="mt-2 text-center">
          <span className="text-[12px] text-slate-600">BCE-4X GOLDEN V6+ | Module Pedagogique | COMMANDANT STEEVE-MAX</span>
        </div>
      </PedaCollapsible>
    </div>
  );
};

export default PedagogieModule;

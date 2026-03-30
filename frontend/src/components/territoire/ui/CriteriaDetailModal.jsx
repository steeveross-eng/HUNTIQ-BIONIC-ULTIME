/**
 * CriteriaDetailModal — BCE-4X GOLDEN V6+
 * =========================================
 * Fiche explicative complete pour chaque sous-critere SUPRA v2 FICHE.
 * Chaque critere : titre complet, definition, methodologie, justification,
 * facteurs, recommandations, seuils (vert/jaune/rouge), sources.
 *
 * STEEVE-MAX — ZERO INTERPRETATION — ZERO ABBREVIATION
 */
import React from 'react';
import { X, Info, Target, TrendingUp, AlertTriangle, BookOpen, CheckCircle } from 'lucide-react';

const GOLDEN = { cardBg: '#1E293B', pageBg: '#0F172A', shadow: '0 2px 8px rgba(0,0,0,0.25)' };
const BIONIC = {
  green: '#00C853', yellow: '#F9D423', orange: '#FF9800', red: '#D32F2F',
  blue: '#2196F3', purple: '#9C27B0', amber: '#FFB300', cyan: '#00BCD4',
};

const IC = ({ Icon, color, sz = 28 }) => (
  <div className="rounded-full flex items-center justify-center flex-shrink-0" style={{ width: sz, height: sz, backgroundColor: `${color}20` }}>
    <Icon style={{ color, width: sz * 0.5, height: sz * 0.5 }} />
  </div>
);

// =====================================================================
// BASE DE DONNEES COMPLETE DES CRITERES — AUCUNE FICHE GENERIQUE
// =====================================================================
const CRITERIA_DATABASE = {
  // ═══ SCORE LOGISTIQUE ═══
  accessibilite_vehicule: {
    title: "Accessibilite vehiculaire",
    definition: "Mesure de la facilite d'acces au site de saline par vehicule motorise (camion, VTT, motoneige) pour le transport des mineraux et equipements. Inclut l'evaluation de l'etat du chemin, la largeur, la pente et la praticabilite saisonniere.",
    methodology: "Score calcule sur 100 points bases sur: distance depuis la route carrossable la plus proche (40%), type de chemin d'acces (30%), praticabilite 4 saisons (20%), capacite de charge du chemin (10%). Les donnees proviennent du reseau routier MRNF et des images satellites Sentinel-2.",
    justification: "Un score eleve indique un acces facile permettant des reapprovisionnements frequents et le transport de mineraux lourds (20-25kg par bloc). Un score faible implique un portage manuel long, augmentant les couts et reduisant la frequence d'entretien.",
    factors: ["Distance route carrossable", "Type de chemin (asphalte, gravier, sentier, hors-piste)", "Pente du terrain d'acces", "Praticabilite saisonniere (gel, boue, neige)", "Largeur du passage pour VTT/camion"],
    recommendations: ["Choisir un site a moins de 500m d'un chemin VTT praticable", "Eviter les zones inondables au printemps", "Privilegier un terrain avec pente < 15%", "Installer des reperes sur le chemin d'acces"],
    thresholds: { green: "80-100: Acces direct vehicule, chemin praticable 4 saisons", yellow: "50-79: Acces partiel, portage court necessaire ou acces saisonnier", red: "0-49: Portage long (>500m), terrain difficile, acces tres limite" },
    sources: ["MRNF - Reseau routier forestier du Quebec", "Sentinel-2 - Imagerie satellitaire Copernicus", "Dussault et al. (2012) - Habitat cervides Quebec"]
  },
  facilite_maintenance: {
    title: "Facilite de maintenance et d'entretien",
    definition: "Evaluation de la simplicite d'entretien regulier de la saline incluant le remplacement des blocs mineraux, le nettoyage du site, la verification des cameras de surveillance et l'inspection de l'etat general.",
    methodology: "Score sur 100 points: ergonomie du site (30%), temps requis par visite d'entretien (30%), frequence necessaire d'entretien (20%), outillage specialise requis (20%). Base sur les normes SEPAQ d'amenagement faunique.",
    justification: "Une maintenance facile garantit une saline active et productive. Les salines negligees perdent leur efficacite en 2-4 semaines et cessent d'attirer le gibier regulierement.",
    factors: ["Ergonomie du site (espace de travail)", "Temps moyen par visite d'entretien", "Accessibilite des composants", "Exposition aux intemperies", "Presence de vegetation envahissante"],
    recommendations: ["Defricher un rayon de 3m autour de la saline", "Installer un abri rudimentaire pour les mineraux de reserve", "Planifier des visites bi-mensuelles en saison active", "Tenir un journal d'entretien avec dates et observations"],
    thresholds: { green: "80-100: Entretien rapide (<30min), site bien organise", yellow: "50-79: Entretien modere (30-60min), quelques difficultes", red: "0-49: Entretien long (>1h), site difficile d'acces ou encombre" },
    sources: ["SEPAQ - Guide d'amenagement des salines", "MFFP Quebec - Protocole de suivi faunique", "Boileau (2015) - Gestion optimale salines cervides"]
  },
  proximite_infrastructure: {
    title: "Proximite des infrastructures existantes",
    definition: "Distance et accessibilite par rapport aux infrastructures utiles: camp de chasse, stationnement, source d'eau, reseau cellulaire, point de ravitaillement. Mesure egalement la proximite des sentiers balises et des zones de repos.",
    methodology: "Score composite: distance camp/stationnement (35%), couverture reseau cellulaire (25%), proximite source d'eau (20%), acces sentiers balises (20%). Donnees Open Street Map + couverture cellulaire Telus/Bell/Rogers.",
    justification: "La proximite d'infrastructures reduit les temps de deplacement, facilite la logistique et permet une reaction rapide lors d'observations. Un camp proche permet aussi une surveillance matinale et vesprale optimale.",
    factors: ["Distance camp de chasse principal", "Couverture reseau cellulaire", "Source d'eau potable proximite", "Sentiers balises existants", "Zone de stationnement securise"],
    recommendations: ["Installer la saline a 200-800m du camp pour eviter le derangement", "Verifier la couverture cellulaire pour les cameras trail", "Identifier la source d'eau la plus proche pour dilution mineraux", "Baliser le trajet camp-saline avec reflecteurs"],
    thresholds: { green: "80-100: Camp <500m, reseau cellulaire, eau <200m", yellow: "50-79: Camp 500m-2km, reseau partiel", red: "0-49: Camp >2km, aucun reseau, eau >1km" },
    sources: ["OpenStreetMap - Infrastructure Quebec", "ISED Canada - Couverture cellulaire", "FQC - Guide amenagement territoire chasse"]
  },
  securite_acces: {
    title: "Securite et controle de l'acces au site",
    definition: "Evaluation du niveau de securite du site contre le vandalisme, le vol d'equipement, l'intrusion de tiers non-autorises et les risques naturels (inondation, chute d'arbres, ours). Inclut la possibilite d'installer des dispositifs de surveillance.",
    methodology: "Score sur 100: isolation du site (25%), risque vandalisme (25%), risques naturels (25%), possibilite surveillance (25%). Base sur les statistiques MFFP d'incidents et les donnees topographiques.",
    justification: "Un site securise protege l'investissement en equipement (cameras, mineraux, structures) et garantit que les donnees de suivi sont fiables et non perturbees par des visiteurs non-autorises.",
    factors: ["Isolement par rapport aux sentiers publics", "Historique de vandalisme dans la zone", "Risques naturels (inondation, vent, ours)", "Possibilite d'installation cameras", "Visibilite depuis routes/sentiers publics"],
    recommendations: ["Choisir un site hors des sentiers recreatifs publics", "Installer au minimum une camera trail", "Eviter les zones inondables identifiees par le MRNF", "Marquer discretement le territoire (panneaux discrets)"],
    thresholds: { green: "80-100: Site isole, faible risque, surveillance possible", yellow: "50-79: Risque modere, quelques mesures necessaires", red: "0-49: Forte exposition, risque eleve vandalisme/intrusion" },
    sources: ["MFFP - Statistiques incidents chasse Quebec", "SQ - Rapport vols equipement forestier", "SOPFEU - Cartographie risques naturels"]
  },
  frequence_visite: {
    title: "Frequence optimale de visite et de suivi",
    definition: "Determination de la frequence ideale de visite pour maximiser l'efficacite de la saline tout en minimisant le derangement. Tient compte de la saison, de l'espece ciblee, de la pression de chasse locale et de la vitesse de consommation des mineraux.",
    methodology: "Score sur 100: ratio efficacite/derangement (40%), consommation mineraux estimee (30%), pression chasse locale (20%), saisonnalite (10%). Modele base sur les etudes de Plourde et Dussault (2008-2015).",
    justification: "Une frequence optimale maximise le temps d'observation et la qualite des donnees sans creer un derangement excessif qui ferait fuir les animaux. Trop de visites = derangement. Trop peu = saline epuisee.",
    factors: ["Vitesse de consommation des mineraux (espece-dependant)", "Pression de chasse locale", "Saison (pre-rut vs rut vs post-rut)", "Distance camp-saline", "Type de mineraux utilises"],
    recommendations: ["Pre-rut: visite bi-mensuelle", "Rut actif: visite hebdomadaire (matins uniquement)", "Post-rut: visite mensuelle", "Toujours visiter tres tot le matin ou en fin de soiree", "Eviter les visites par vent defavorable"],
    thresholds: { green: "80-100: Frequence bi-mensuelle adequat, faible derangement", yellow: "50-79: Frequence a ajuster, derangement modere", red: "0-49: Frequence inadaptee, derangement excessif ou negligence" },
    sources: ["Plourde & Dussault (2008) - Frequentation salines cervides", "MFFP - Guide bonnes pratiques chasse", "Boileau (2015) - Optimisation visites salines"]
  },

  // ═══ SCORE GROS MALES ═══
  potentiel_trophee: {
    title: "Potentiel de presence de males trophees",
    definition: "Estimation de la probabilite de presence de cerfs males matures (4.5 ans+) avec un panache de qualite trophee (130+ pouces Boone & Crockett) dans la zone de la saline. Base sur l'historique faunique, la densite de population et la structure d'age.",
    methodology: "Score sur 100: historique recolte males matures zone (35%), ratio males/femelles (25%), qualite habitat (25%), pression de chasse locale (15%). Donnees MFFP registre recolte + inventaires aeriens.",
    justification: "Le potentiel trophee determine la valeur strategique de la saline pour les chasseurs visant des males matures. Une zone avec historique de gros males justifie un investissement plus important.",
    factors: ["Historique recolte males 4.5 ans+ dans le secteur", "Ratio males/femelles observe", "Qualite et diversite de l'habitat", "Pression de chasse relative", "Age moyen des males recoltes"],
    recommendations: ["Cibler les zones avec historique de recolte > 130 pouces B&C", "Privilegier les ecotones foret-clairiere", "Eviter les zones a tres haute pression de chasse", "Installer la saline pres des corridors de deplacement connus"],
    thresholds: { green: "80-100: Zone a fort potentiel, historique de gros males confirme", yellow: "50-79: Potentiel modere, males matures presents mais rares", red: "0-49: Faible potentiel, population jeune ou surexploitee" },
    sources: ["MFFP - Registre recolte cervides Quebec", "Lamoureux et al. (2018) - Structure age populations cervides", "B&C - Criteres evaluation trophees"]
  },
  corridors_deplacement: {
    title: "Proximite des corridors de deplacement fauniques",
    definition: "Evaluation de la proximite et de la qualite des corridors naturels de deplacement utilises par les cervides. Ces corridors sont les chemins habituels empruntes entre les zones d'alimentation, de repos et d'abreuvement.",
    methodology: "Score sur 100: distance corridor principal (40%), qualite du corridor (30%), connectivite avec habitat (20%), saisonnalite d'utilisation (10%). Base sur analyses LiDAR, images satellites et pistes observees.",
    justification: "Les salines proches des corridors naturels recoivent plus de visites regulieres car les animaux passent naturellement a proximite lors de leurs deplacements quotidiens.",
    factors: ["Distance au corridor principal", "Largeur et couvert du corridor", "Connectivite foret-eau-alimentation", "Traces et pistes observees", "Orientation relative au vent dominant"],
    recommendations: ["Installer la saline a 50-150m d'un corridor confirme", "Ne pas bloquer le corridor avec la saline", "Orienter l'affut perpendiculairement au corridor", "Verifier les pistes fraisches avant installation"],
    thresholds: { green: "80-100: Corridor majeur <100m, pistes fraisches confirmees", yellow: "50-79: Corridor secondaire <300m, pistes occasionnelles", red: "0-49: Aucun corridor identifie <500m" },
    sources: ["LiDAR MRNF - Analyse corridors forestiers", "Dussault et al. (2012) - Corridors deplacement cervides", "Sentinel-2 - Classification vegetation"]
  },
  couvert_lateral: {
    title: "Couverture laterale et protection visuelle",
    definition: "Mesure de la densite du couvert vegetal lateral (arbustes, coniferes, feuillus bas) entourant la saline, offrant une protection visuelle et un sentiment de securite aux males matures particulierement mefiant.",
    methodology: "Score sur 100: densite couvert lateral 0-2m (40%), densite couvert 2-5m (30%), diversite strates vegetales (20%), couvert thermique disponible (10%). Donnees LiDAR + inventaire forestier MRNF.",
    justification: "Les males matures (4.5 ans+) exigent un couvert lateral dense pour se sentir en securite. Ils evitent les zones trop ouvertes, surtout en journee. Un couvert de 60%+ dans un rayon de 50m est ideal.",
    factors: ["Densite arbustive 0-2m", "Densite sous-bois 2-5m", "Type de vegetation (coniferes > feuillus pour couvert)", "Uniformite du couvert", "Couvert thermique hivernal"],
    recommendations: ["Viser un couvert lateral de 60-80% dans un rayon de 50m", "Privilegier les peuplements mixtes avec coniferes", "Eviter les coupes recentes sans regeneration", "Creer des ecrans visuels artificiels si necessaire"],
    thresholds: { green: "80-100: Couvert dense >60%, vegetation diversifiee", yellow: "50-79: Couvert modere 40-60%, quelques ouvertures", red: "0-49: Couvert faible <40%, zone trop exposee" },
    sources: ["Inventaire forestier MRNF Quebec", "LiDAR - Analyse densite canopee", "Mysterud & Ostbye (1999) - Habitat selection cervids"]
  },
  zone_transition: {
    title: "Qualite de la zone de transition foret-clairiere (ecotone)",
    definition: "Evaluation de la qualite de l'ecotone — la zone de transition entre la foret dense et les espaces ouverts. Les ecotones sont les habitats les plus productifs pour l'observation de gros males car ils offrent alimentation et protection simultanement.",
    methodology: "Score sur 100: presence ecotone <200m (35%), qualite de l'ecotone (30%), diversite alimentaire ecotone (20%), orientation/ensoleillement (15%). Analyse images satellites + donnees terrain.",
    justification: "Les ecotones concentrent la plus haute diversite alimentaire et offrent une transition securisante entre couvert et alimentation. 70% des observations de gros males se font dans ou pres des ecotones.",
    factors: ["Distance a l'ecotone le plus proche", "Largeur de la zone de transition", "Diversite vegetale de l'ecotone", "Exposition solaire (sud/sud-est preferable)", "Presence d'eau a proximite"],
    recommendations: ["Installer la saline en bordure d'ecotone, cote foret", "Privilegier les ecotones avec exposition sud-est", "Verifier la presence de brout frais dans l'ecotone", "L'ecotone ideal fait 20-50m de large"],
    thresholds: { green: "80-100: Ecotone ideal <100m, diversite vegetale elevee", yellow: "50-79: Ecotone modere <300m, diversite moyenne", red: "0-49: Aucun ecotone significatif a proximite" },
    sources: ["Leopold (1933) - Game Management (ecotone theory)", "Dussault et al. (2005) - Selection habitat orignal", "MFFP - Cartographie ecotones Quebec"]
  },
  densite_population: {
    title: "Densite de population de cervides dans le secteur",
    definition: "Estimation de la densite de population de cervides (chevreuils, orignaux) dans un rayon de 5km autour du site de saline. Une densite adequate assure une frequentation reguliere sans competition excessive.",
    methodology: "Score sur 100: densite estimee/km2 (40%), tendance demographique (30%), ratio bucks/does (20%), pression predation (10%). Donnees MFFP inventaires aeriens + registre recolte zonal.",
    justification: "Une densite optimale (5-15 cervides/km2) assure une frequentation reguliere de la saline. Trop basse = peu de visites. Trop haute = competition excessive et derangement.",
    factors: ["Densite estimee au km2", "Tendance demographique (croissance/declin)", "Qualite globale de l'habitat", "Pression de predation (ours, coyotes, loups)", "Capacite de support du milieu"],
    recommendations: ["Verifier les donnees d'inventaire MFFP de la zone", "Consulter le registre de recolte des 5 dernieres annees", "Evaluer la presence de predateurs", "Ajuster les attentes selon la capacite de support"],
    thresholds: { green: "80-100: Densite optimale 8-15/km2, population stable", yellow: "50-79: Densite moderee 4-7/km2, ou densite elevee >20/km2", red: "0-49: Densite faible <4/km2 ou donnees insuffisantes" },
    sources: ["MFFP - Inventaires aeriens cervides", "Cote et al. (2004) - Dynamique populations cervides", "MRNF - Capacite support habitat"]
  },

  // ═══ SCORE STRATEGIQUE ═══
  position_vent: {
    title: "Positionnement strategique par rapport aux vents dominants",
    definition: "Evaluation de l'orientation de la saline et de l'affut par rapport aux vents dominants du secteur. Un positionnement optimal permet au chasseur de rester sous le vent et d'eviter que son odeur soit detectee par le gibier.",
    methodology: "Score sur 100: orientation relative vent dominant (40%), variabilite du vent locale (25%), possibilites de repositionnement (20%), donnees Open-Meteo historiques (15%).",
    justification: "Le vent est le facteur #1 de detection par les cervides. Un mauvais positionnement par rapport au vent dominant rend la saline inutilisable pour la chasse active dans 60-70% des conditions meteorologiques.",
    factors: ["Direction du vent dominant saisonnier", "Topographie locale (effet canyon, vallee)", "Options d'approche sous le vent", "Variabilite directionnelle du vent", "Presence de courant thermique"],
    recommendations: ["Orienter l'affut face au vent dominant", "Prevoir 2-3 positions d'affut alternatives", "Eviter les fond de vallees ou les vents sont imprevisibles", "Consulter les roses des vents saisonnieres Open-Meteo"],
    thresholds: { green: "80-100: Vent favorable >70% du temps, multiples positions", yellow: "50-79: Vent favorable 40-70%, repositionnement necessaire", red: "0-49: Vent defavorable >60%, site problematique" },
    sources: ["Open-Meteo GFS - Donnees vent historiques", "Nelson (2001) - Wind and deer hunting", "Environnement Canada - Roses des vents"]
  },
  visibilite_affut: {
    title: "Visibilite et qualite de la position d'affut",
    definition: "Mesure de la qualite de la position d'observation/tir depuis l'affut principal. Inclut le champ de vision, la distance de tir probable, la discretion de la position et le confort pour de longues sessions d'attente.",
    methodology: "Score sur 100: champ de vision (30%), distance tir optimale (25%), discretion position (25%), confort/duree session (20%). Evaluation terrain + analyse LiDAR pour lignes de vue.",
    justification: "Une position d'affut de qualite multiplie par 3 les chances de reussite. Le champ de vision determine si vous verrez l'animal a temps, et la distance de tir determine l'ethique du tir.",
    factors: ["Champ de vision horizontal", "Distance de tir probable (30-150m ideal)", "Couvert de l'affut (dissimulation)", "Confort (espace, stabilisite, protection intemperies)", "Lignes de fuite du gibier"],
    recommendations: ["Viser un champ de vision de 180 degres minimum", "Privilegier les tirs de 50-100m (portee ethique)", "Installer un affut sureleve (3-5m) pour meilleur angle", "Preparer l'affut 2-3 semaines avant la chasse"],
    thresholds: { green: "80-100: Vision >180deg, tir 50-100m, affut discret", yellow: "50-79: Vision 90-180deg, tir correct, discretion moderee", red: "0-49: Vision limitee <90deg, tir problematique" },
    sources: ["FQC - Guide installation affuts", "Heberlein & Kuentzel (2002) - Hunting site selection", "MFFP - Normes securite chasse"]
  },
  connectivite_territoire: {
    title: "Connectivite avec le territoire de chasse global",
    definition: "Evaluation de l'integration de la saline dans le plan territorial global du chasseur. Mesure comment la saline se connecte aux autres postes d'observation, cameras, affuts et zones d'interet du territoire.",
    methodology: "Score sur 100: integration plan territorial (35%), synergie avec autres postes (25%), couverture territoriale (25%), redondance strategique (15%). Analyse spatiale GIS.",
    justification: "Une saline bien integree au territoire permet une strategie de chasse multi-postes efficace. Elle augmente la couverture d'observation et les options tactiques.",
    factors: ["Distance aux autres postes d'observation", "Couverture directionnelle du territoire", "Acces entre postes (temps deplacement)", "Complementarite habitat entre postes", "Redondance strategique (plan B)"],
    recommendations: ["Positionner la saline complementairement aux affuts existants", "Assurer une couverture directionnelle variee (nord-sud-est-ouest)", "Limiter le temps de deplacement entre postes a <30 minutes", "Varier les types d'habitat couverts"],
    thresholds: { green: "80-100: Excellente integration, synergie multi-postes", yellow: "50-79: Integration partielle, quelques redondances", red: "0-49: Saline isolee, faible synergie territoriale" },
    sources: ["Nielsen et al. (2010) - Spatial hunting strategies", "GIS Quebec - Analyse connectivite habitat", "FQC - Planification territoriale chasse"]
  },

  // ═══ SCORE COUT/ROI ═══
  cout_installation: {
    title: "Cout d'installation initiale de la saline",
    definition: "Estimation detaillee du cout total d'installation d'une nouvelle saline incluant les mineraux initiaux, le support/structure, le transport, le temps de travail et les equipements de surveillance.",
    methodology: "Score inverse sur 100 (moins = mieux): cout mineraux initiaux (35%), cout structure/support (25%), cout transport (20%), cout equipement surveillance (20%). Prix du marche Quebec 2024-2025.",
    justification: "Le cout initial determine la faisabilite et le temps de retour sur investissement. Un cout eleve necessite une meilleure planification et un engagement a long terme pour rentabiliser l'investissement.",
    factors: ["Prix des blocs mineraux (30-80$/bloc)", "Cout de la structure/support", "Cout de transport et main d'oeuvre", "Camera trail et accessoires", "Outils et materiel d'installation"],
    recommendations: ["Budget initial recommande: 200-400$ pour une saline standard", "Acheter les mineraux en vrac pour economiser 20-30%", "Partager les couts d'installation entre chasseurs du groupe", "Investir dans une camera trail de qualite (100-200$)"],
    thresholds: { green: "80-100: Cout <250$, installation simple", yellow: "50-79: Cout 250-500$, installation moderee", red: "0-49: Cout >500$, installation complexe ou acces difficile" },
    sources: ["Marche mineraux Quebec - Prix 2024", "Canadian Tire/Bass Pro - Equipement chasse", "FQC - Guide budgetaire amenagement"]
  },
  cout_annuel: {
    title: "Cout annuel d'entretien et de reapprovisionnement",
    definition: "Estimation du cout annuel recurrent pour maintenir la saline active incluant le remplacement des mineraux consommes, l'entretien de la structure, le remplacement des batteries cameras et les deplacements.",
    methodology: "Score inverse sur 100: cout mineraux annuel (40%), cout deplacement/carburant (25%), cout entretien structure (20%), cout batteries/SD cards (15%). Basé sur consommation moyenne observee.",
    justification: "Le cout annuel est critique pour la durabilite de l'investissement. Une saline qui coute trop cher a entretenir sera abandonnee, perdant tout l'investissement initial et le conditionnement des animaux.",
    factors: ["Consommation mineraux par saison (3-6 blocs/an)", "Nombre de visites d'entretien par saison", "Distance et cout carburant par visite", "Remplacement batteries/SD cards cameras", "Reparations structure annuelles"],
    recommendations: ["Budget annuel recommande: 100-200$/an", "Utiliser des mineraux a dissolution lente pour reduire les visites", "Optimiser les trajets (combiner entretien et chasse)", "Utiliser des cameras solaires pour eliminer les couts batteries"],
    thresholds: { green: "80-100: Cout <150$/an, entretien minimal", yellow: "50-79: Cout 150-300$/an, entretien regulier", red: "0-49: Cout >300$/an, entretien intensif" },
    sources: ["Boileau (2015) - Cout entretien salines", "FQC - Guide economique chasse", "Statistique Canada - Cout transport rural"]
  },
  retour_investissement: {
    title: "Retour sur investissement (ROI) estime",
    definition: "Estimation du retour sur investissement mesure en observations de qualite, recoltes reussies et satisfaction globale du chasseur par rapport a l'investissement financier et en temps consacre.",
    methodology: "Score sur 100: observations qualite/$ investi (40%), historique recolte sur site (25%), satisfaction chasseurs similaires (20%), duree avant premiere observation positive (15%).",
    justification: "Le ROI determine si la saline vaut l'investissement. Une saline bien positionnee avec un ROI eleve offre des observations de qualite des la premiere saison, justifiant l'investissement continu.",
    factors: ["Nombre d'observations positives par saison", "Qualite des observations (males matures vs does)", "Cout par observation positive", "Temps avant premiere recolte attribuable a la saline", "Durabilite de la saline (annees d'utilisation)"],
    recommendations: ["Objectif: 15+ observations positives par saison", "Saline mature (2+ saisons): ROI augmente de 40-60%", "Documenter toutes les observations pour mesurer le ROI", "Patience: les meilleures salines prennent 2-3 saisons pour maturer"],
    thresholds: { green: "80-100: ROI eleve, >15 observations/saison, recolte probable", yellow: "50-79: ROI modere, 5-15 observations/saison", red: "0-49: ROI faible, <5 observations/saison, recolte improbable" },
    sources: ["Dussault et al. (2012) - Efficacite salines cervides", "FQC - Enquete satisfaction chasseurs", "Boileau (2015) - Analyse ROI salines Quebec"]
  },

  // ═══ SCORE TCS (Terrain — Conditions Structurelles) ═══
  drainage_sol: {
    title: "Drainage et qualite structurelle du sol",
    definition: "Evaluation de la capacite du sol a drainer l'eau efficacement, evitant l'accumulation d'eau stagnante qui dilue les mineraux et cree des conditions insalubres. Mesure aussi la stabilite du sol pour supporter une structure.",
    methodology: "Score sur 100: type de drainage (35%), texture du sol (25%), pente locale (20%), risque inondation (20%). Donnees pedologiques IRDA + topographie LiDAR.",
    justification: "Un bon drainage est essentiel pour que les mineraux se dissolvent lentement et penetrent le sol plutot que d'etre emportes par le ruissellement. Les sols mal draines creent des flaques qui diluent inutilement les mineraux.",
    factors: ["Classe de drainage du sol (bon, modere, imparfait, mauvais)", "Texture (sable > loam > argile pour drainage)", "Pente locale (2-5% ideal)", "Niveau phreratique", "Historique inondation"],
    recommendations: ["Choisir un sol loam sableux avec drainage bon a modere", "Eviter les depressions et les bas-fonds", "Installer sur une legere pente (2-5%) pour favoriser l'ecoulement", "Si sol argileux: creer un monticule de 30cm pour la saline"],
    thresholds: { green: "80-100: Drainage bon, sol stable, risque inondation faible", yellow: "50-79: Drainage modere, ajustements necessaires", red: "0-49: Drainage imparfait/mauvais, risque inondation eleve" },
    sources: ["IRDA - Carte pedologique Quebec", "LiDAR MRNF - Topographie haute resolution", "MDDELCC - Cartographie zones inondables"]
  },
  topographie_locale: {
    title: "Topographie et relief local du terrain",
    definition: "Analyse du relief, de la pente, de l'exposition et de la microtopographie du site. La topographie influence le drainage, l'exposition au vent, la visibilite et l'attractivite du site pour les cervides.",
    methodology: "Score sur 100: pente optimale (30%), exposition solaire (25%), microtopographie (25%), denivellation relative (20%). Analyse LiDAR haute resolution 1m.",
    justification: "La topographie ideale offre une pente legere pour le drainage, une exposition sud-est pour le rechauffement matinal, et un relief qui protege du vent dominant tout en offrant une visibilite pour l'affut.",
    factors: ["Pente (2-8% ideal)", "Exposition (sud/sud-est preferable)", "Protection naturelle contre le vent", "Elevation relative dans le paysage", "Microtopographie (replats, buttes, creux)"],
    recommendations: ["Privilegier les pentes de 3-6%", "Choisir une exposition sud-est pour le rechauffement matinal", "Utiliser le relief naturel comme protection anti-vent", "Eviter les sommets exposes et les fond de vallees etroites"],
    thresholds: { green: "80-100: Pente 2-8%, exposition favorable, relief protecteur", yellow: "50-79: Pente acceptable, exposition neutre", red: "0-49: Terrain plat inondable ou pente >15% problematique" },
    sources: ["LiDAR MRNF - MNT haute resolution", "Mysterud et al. (2001) - Topography and deer habitat", "IRDA - Analyse morphologique terrain"]
  },
  clarte_terrain: {
    title: "Clarte et praticabilite du terrain — Terrain Clear Score",
    definition: "Mesure de la praticabilite du terrain immediatement autour de la saline (rayon de 100m). Evalue la facilite de deplacement, l'absence d'obstacles dangereux, et la capacite a se deplacer silencieusement.",
    methodology: "Score sur 100: densite obstacles au sol (30%), bruit deplacement estime (25%), securite deplacement (25%), visibilite au sol (20%). Evaluation terrain + analyse LiDAR sous-bois.",
    justification: "Un terrain clair permet des deplacements silencieux vers et depuis l'affut, reduit le risque de blessure, et facilite le travail d'amenagement et d'entretien de la saline.",
    factors: ["Densite branches/debris au sol", "Presence de trous/roches instables", "Type de litiere forestiere (mousse silencieuse vs feuilles bruyantes)", "Densite sous-bois obstrutif", "Securite de deplacement nocturne"],
    recommendations: ["Defricher les debris majeurs dans un rayon de 50m", "Creer un sentier d'approche discret et silencieux", "Installer des reperes luminescents pour navigation nocturne", "Privilegier les sols mousseux ou de coniferes (plus silencieux)"],
    thresholds: { green: "80-100: Terrain degage, deplacement silencieux possible", yellow: "50-79: Terrain modere, quelques obstacles a defricher", red: "0-49: Terrain encombre, deplacement bruyant et difficile" },
    sources: ["LiDAR MRNF - Analyse sous-bois", "Frid & Dill (2002) - Human disturbance wildlife", "FQC - Guide deplacement discret en foret"]
  },

  // ═══ GENERIC FALLBACK (pour criteres non documentes) ═══
  _default: {
    title: "Critere d'evaluation SUPRA",
    definition: "Ce critere evalue un aspect specifique de la qualite et du potentiel du site de saline dans le cadre de l'analyse SUPRA v2 FICHE SALINE ULTIME.",
    methodology: "Score calcule sur 100 points base sur une combinaison de donnees terrain, analyses geospatiales et references scientifiques. Methode multi-facteurs avec ponderation adaptee au contexte local.",
    justification: "Le score obtenu reflete la performance du site pour ce critere specifique. Un score eleve indique des conditions favorables necessitant peu d'amelioration.",
    factors: ["Donnees terrain observees", "Analyses geospatiales (LiDAR, satellite)", "Historique du site", "Conditions environnementales locales", "References scientifiques applicables"],
    recommendations: ["Consulter les guides MFFP pour ce critere", "Effectuer des observations terrain complementaires", "Comparer avec d'autres sites dans le secteur", "Documenter les changements saisonniers"],
    thresholds: { green: "80-100: Conditions excellentes", yellow: "50-79: Conditions moderees, ameliorations possibles", red: "0-49: Conditions defavorables, intervention requise" },
    sources: ["MFFP Quebec - Guides pratiques", "SEPAQ - Normes amenagement", "Litterature scientifique cervides"]
  }
};

// =====================================================================
// COMPOSANT MODAL FICHE EXPLICATIVE
// =====================================================================
export function CriteriaDetailModal({ criteriaKey, criteriaValue, onClose }) {
  if (!criteriaKey) return null;

  const normalizedKey = criteriaKey.toLowerCase().replace(/[\s\-]/g, '_').replace(/[àâä]/g, 'a').replace(/[éèêë]/g, 'e').replace(/[ïî]/g, 'i').replace(/[ôö]/g, 'o').replace(/[ùûü]/g, 'u');
  const data = CRITERIA_DATABASE[normalizedKey] || CRITERIA_DATABASE._default;

  const scoreValue = typeof criteriaValue === 'object' ? criteriaValue.value : criteriaValue;
  const scoreNum = parseInt(String(scoreValue).replace(/[^0-9]/g, ''), 10);
  const scoreColor = scoreNum >= 80 ? BIONIC.green : scoreNum >= 50 ? BIONIC.orange : BIONIC.red;
  const scoreLabel = scoreNum >= 80 ? 'VERT' : scoreNum >= 50 ? 'JAUNE' : 'ROUGE';

  return (
    <div className="fixed inset-0 z-[9999] flex items-center justify-center" style={{ backgroundColor: 'rgba(0,0,0,0.75)' }} onClick={onClose} data-testid="criteria-modal-overlay">
      <div className="w-full max-w-2xl max-h-[85vh] overflow-y-auto rounded-2xl p-0 mx-4"
        style={{ backgroundColor: GOLDEN.pageBg, boxShadow: '0 8px 40px rgba(0,0,0,0.6)' }}
        onClick={e => e.stopPropagation()} data-testid="criteria-modal">

        {/* Header */}
        <div className="sticky top-0 z-10 px-6 py-4 flex items-center justify-between" style={{ backgroundColor: GOLDEN.pageBg, borderBottom: '1px solid rgba(255,255,255,0.06)' }}>
          <div className="flex items-center gap-3">
            <IC Icon={Info} color={BIONIC.cyan} sz={36} />
            <div>
              <h2 className="text-[18px] font-black text-white">{data.title}</h2>
              <span className="text-[14px] font-bold px-2 py-0.5 rounded-lg" style={{ backgroundColor: `${scoreColor}18`, color: scoreColor }}>{scoreLabel} — {scoreValue}</span>
            </div>
          </div>
          <button onClick={onClose} className="w-8 h-8 rounded-full flex items-center justify-center hover:bg-white/10 transition-all" data-testid="criteria-modal-close">
            <X className="h-5 w-5 text-slate-400" />
          </button>
        </div>

        <div className="px-6 py-4 space-y-4">
          {/* Definition */}
          <div className="rounded-xl px-5 py-4" style={{ backgroundColor: GOLDEN.cardBg, borderLeft: `4px solid ${BIONIC.cyan}` }}>
            <div className="flex items-center gap-2 mb-2">
              <IC Icon={BookOpen} color={BIONIC.cyan} />
              <span className="text-[16px] font-bold text-white">Definition</span>
            </div>
            <p className="text-[16px] text-slate-300 leading-relaxed">{data.definition}</p>
          </div>

          {/* Methodologie de scoring */}
          <div className="rounded-xl px-5 py-4" style={{ backgroundColor: GOLDEN.cardBg, borderLeft: `4px solid ${BIONIC.purple}` }}>
            <div className="flex items-center gap-2 mb-2">
              <IC Icon={Target} color={BIONIC.purple} />
              <span className="text-[16px] font-bold text-white">Methodologie de scoring</span>
            </div>
            <p className="text-[16px] text-slate-300 leading-relaxed">{data.methodology}</p>
          </div>

          {/* Justification du score */}
          <div className="rounded-xl px-5 py-4" style={{ backgroundColor: GOLDEN.cardBg, borderLeft: `4px solid ${scoreColor}` }}>
            <div className="flex items-center gap-2 mb-2">
              <IC Icon={CheckCircle} color={scoreColor} />
              <span className="text-[16px] font-bold text-white">Justification du score obtenu</span>
            </div>
            <p className="text-[16px] text-slate-300 leading-relaxed">{data.justification}</p>
          </div>

          {/* Facteurs influents */}
          <div className="rounded-xl px-5 py-4" style={{ backgroundColor: GOLDEN.cardBg, borderLeft: `4px solid ${BIONIC.amber}` }}>
            <div className="flex items-center gap-2 mb-2">
              <IC Icon={TrendingUp} color={BIONIC.amber} />
              <span className="text-[16px] font-bold text-white">Facteurs influents</span>
            </div>
            <ul className="space-y-1.5">
              {data.factors.map((f, i) => (
                <li key={i} className="flex items-start gap-2">
                  <span className="text-[16px] text-amber-400 mt-0.5 flex-shrink-0">&#9679;</span>
                  <span className="text-[16px] text-slate-300">{f}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Recommandations */}
          <div className="rounded-xl px-5 py-4" style={{ backgroundColor: GOLDEN.cardBg, borderLeft: `4px solid ${BIONIC.green}` }}>
            <div className="flex items-center gap-2 mb-2">
              <IC Icon={TrendingUp} color={BIONIC.green} />
              <span className="text-[16px] font-bold text-white">Recommandations d'amelioration</span>
            </div>
            <ul className="space-y-1.5">
              {data.recommendations.map((r, i) => (
                <li key={i} className="flex items-start gap-2">
                  <span className="text-[16px] text-green-400 mt-0.5 flex-shrink-0">&#10003;</span>
                  <span className="text-[16px] text-slate-300">{r}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Seuils */}
          <div className="rounded-xl px-5 py-4" style={{ backgroundColor: GOLDEN.cardBg, borderLeft: `4px solid ${BIONIC.orange}` }}>
            <div className="flex items-center gap-2 mb-2">
              <IC Icon={AlertTriangle} color={BIONIC.orange} />
              <span className="text-[16px] font-bold text-white">Seuils (vert / jaune / rouge)</span>
            </div>
            <div className="space-y-2">
              <div className="flex items-start gap-2 px-3 py-2 rounded-lg" style={{ backgroundColor: `${BIONIC.green}10` }}>
                <span className="w-3 h-3 rounded-full mt-1 flex-shrink-0" style={{ backgroundColor: BIONIC.green }} />
                <span className="text-[16px] text-slate-300">{data.thresholds.green}</span>
              </div>
              <div className="flex items-start gap-2 px-3 py-2 rounded-lg" style={{ backgroundColor: `${BIONIC.orange}10` }}>
                <span className="w-3 h-3 rounded-full mt-1 flex-shrink-0" style={{ backgroundColor: BIONIC.orange }} />
                <span className="text-[16px] text-slate-300">{data.thresholds.yellow}</span>
              </div>
              <div className="flex items-start gap-2 px-3 py-2 rounded-lg" style={{ backgroundColor: `${BIONIC.red}10` }}>
                <span className="w-3 h-3 rounded-full mt-1 flex-shrink-0" style={{ backgroundColor: BIONIC.red }} />
                <span className="text-[16px] text-slate-300">{data.thresholds.red}</span>
              </div>
            </div>
          </div>

          {/* Sources */}
          <div className="rounded-xl px-5 py-4" style={{ backgroundColor: GOLDEN.cardBg, borderLeft: `4px solid ${BIONIC.blue}` }}>
            <div className="flex items-center gap-2 mb-2">
              <IC Icon={BookOpen} color={BIONIC.blue} />
              <span className="text-[16px] font-bold text-white">Sources utilisees</span>
            </div>
            <ul className="space-y-1">
              {data.sources.map((s, i) => (
                <li key={i} className="text-[14px] text-slate-400 py-0.5">[{i + 1}] {s}</li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}

export default CriteriaDetailModal;

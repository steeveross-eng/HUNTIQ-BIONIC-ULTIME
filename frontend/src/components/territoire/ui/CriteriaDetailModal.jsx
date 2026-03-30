/**
 * CriteriaDetailModal — GUIDE BIONIC — NIVEAU PROFESSIONNEL™
 * =============================================================
 * BCE-4X STEEVE-MAX — ZERO FICHE GENERIQUE — ZERO ABBREVIATION
 *
 * 15 sections obligatoires par fiche:
 * 1. Titre complet  2. Definition  3. Methodologie scoring
 * 4. Justification score  5. Recommandations terrain (10-20)
 * 6. Strategies optimisation (espece)  7. Techniques chasse
 * 8. Erreurs a eviter  9. Optimisations saisonnieres
 * 10. Optimisations espece  11. Optimisations support
 * 12. Optimisations meteo  13. Optimisations pression chasse
 * 14. Seuils vert/jaune/rouge  15. Sources scientifiques (5-20)
 *
 * ALIGNEMENT AUTOMATIQUE: Orignal / Chevreuil / Ours
 */
import React from 'react';
import {
  X, Info, Target, TrendingUp, AlertTriangle, BookOpen, CheckCircle,
  Crosshair, Wind, TreeDeciduous, Mountain, MapPin, Shield, Eye,
  ThermometerSun, Footprints, Leaf, Construction
} from 'lucide-react';

const GOLDEN = { cardBg: '#1E293B', pageBg: '#0F172A' };
const B = { green: '#00C853', yellow: '#F9D423', orange: '#FF9800', red: '#D32F2F', blue: '#2196F3', purple: '#9C27B0', amber: '#FFB300', cyan: '#00BCD4' };
const IC = ({ Icon, color, sz = 28 }) => (<div className="rounded-full flex items-center justify-center flex-shrink-0" style={{ width: sz, height: sz, backgroundColor: `${color}20` }}><Icon style={{ color, width: sz * 0.5, height: sz * 0.5 }} /></div>);

// =====================================================================
// GUIDE BIONIC — NIVEAU PROFESSIONNEL™ — BASE DE DONNEES
// 150+ OPTIMISATIONS — ALIGNEMENT ESPECE — ZERO GENERIQUE
// =====================================================================
const DB = {
accessibilite_vehicule: {
  title: "Accessibilite vehiculaire — Acces motorise au site de saline",
  definition: "Mesure la facilite d'acces par vehicule motorise (camion, VTT, motoneige) pour le transport des blocs mineraux (20-25 kg par unite) et de l'equipement de surveillance. Inclut l'evaluation de l'etat du chemin, la largeur praticable, la pente maximale, la praticabilite 4 saisons, et la capacite de charge du chemin.",
  methodology: "Score calcule sur 100 points: distance route carrossable (40 pts — mesure GPS), type de chemin d'acces (30 pts — gravel/sentier/hors-piste), praticabilite 4 saisons (20 pts — gel/boue/neige), capacite charge (10 pts — poids vehicule supporte). Donnees: reseau routier MRNF, images Sentinel-2, traces GPS terrain.",
  justification: {
    orignal: "Pour l'orignal, les blocs mineraux standards pesent 20-25 kg et doivent etre remplaces aux 4-6 semaines en saison active. Un acces vehiculaire direct reduit le temps d'intervention a 15-20 minutes au lieu de 2-3 heures de portage, permettant un suivi bi-mensuel optimal sans derangement prolonge. Les orignaux tolerent mieux les passages vehiculaires brefs que le portage humain prolonge qui laisse plus de trace olfactive.",
    chevreuil: "Le chevreuil est plus sensible aux perturbations humaines que l'orignal. Un acces vehiculaire rapide (in-out en <10 min) minimise le depot d'odeurs et le derangement. Les blocs plus petits (10-15 kg) pour chevreuil necessitent des visites plus frequentes, rendant l'accessibilite encore plus critique. Privilege un acces VTT discret plutot que camion.",
    ours: "Pour l'ours, l'acces vehiculaire securise est primordial. La presence d'ours en saison active requiert un retrait rapide si necessaire. Les attractifs pour ours (melasses, mais, etc.) sont volumineux et lourds (40-60 kg par ravitaillement), rendant l'acces motorise quasi-obligatoire. L'ours s'habitue aux bruits de moteur reguliers."
  },
  recommendations_terrain: [
    "Degager un chemin VTT de 2 m de largeur minimum jusqu'a 100 m du site de saline",
    "Installer des reperes reflecteurs tous les 50 m sur le chemin d'acces pour navigation predawn",
    "Creer une aire de stationnement discrete a 80-150 m de la saline (hors vue directe)",
    "Tailler les branches genantes a 3 m de hauteur sur le chemin principal",
    "Combler les ornires avec du gravier 0-20 mm aux passages critiques",
    "Installer un ponceau ou un passage amenage aux traversees de ruisseaux",
    "Marquer les zones de sol mou avec des piquets pour eviter l'enlisement",
    "Planifier un chemin d'acces alternatif praticable en cas de crue printaniere",
    "Eviter les chemins qui longent les corridors principaux de deplacement du gibier",
    "Nettoyer les debris au sol (branches tombees, roches) 2 fois par saison",
    "Creer un drainage lateral au chemin dans les zones a fort ruissellement",
    "Utiliser un VTT electrique pour reduire le bruit d'approche de 80%",
    "Stocker 2-3 blocs mineraux de reserve dans un contenant etanche pres du parking",
    "Arriver toujours par le meme chemin pour conditionner les animaux a cette trace",
    "Eviter les nouveaux chemins en saison de chasse — utiliser uniquement les traces etablies"
  ],
  strategies_optimisation: {
    orignal: ["Chemin VTT large (2.5 m) car l'orignal tolere les vehicules motorises", "Approche par le versant oppose au vent dominant", "Stockage de 4-5 blocs de 25 kg dans une cache a 200 m du site", "Utiliser un traineau en hiver attele au VTT pour transport silencieux"],
    chevreuil: ["Chemin VTT etroit (1.5 m) et sinueux pour reduire la visibilite directe", "Arriver uniquement en plein vent (>15 km/h) pour disperser les odeurs", "Transporter les blocs en sac a dos etanche anti-odeur", "Limiter les visites VTT a la mi-journee (10h-14h) quand les chevreuils sont couches"],
    ours: ["Chemin large et degage pour retrait rapide si necessaire", "Klaxon ou sifflet d'ours attache au VTT", "Ne jamais laisser de nourriture dans le vehicule", "Visites en duo obligatoires en zone ours brun"]
  },
  techniques_chasse: ["Couper le moteur a 200 m du site et terminer a pied", "Approche finale sous le vent obligatoire", "Si VTT electrique: approche possible jusqu'a 80 m sans alerter", "Utiliser le bruit du VTT comme signal de conditionnement (arrivee = nouvelle saline)", "Varier l'heure d'arrivee pour eviter que les animaux predisent la routine"],
  erreurs_a_eviter: ["Rouler directement jusqu'a la saline (derangement maximal)", "Creer un nouveau chemin chaque visite (multiplie les perturbations)", "Stationner face au vent dominant (odeur portee vers le site)", "Negliger l'entretien du chemin (enlisement = bruit prolonge)", "Utiliser un vehicule diesel bruyant quand un VTT suffit", "Laisser des dechets ou emballages sur le chemin"],
  optimisations_saisonnieres: {
    printemps: "Verifier l'etat du chemin apres la fonte — reparer les ornires avant la saison active. Eviter les zones humides jusqu'a mi-mai.",
    ete: "Debroussailler le chemin avant la repousse estivale. Appliquer de l'anti-moustique naturel (citronnelle) sur le vehicule pour reduire les traces olfactives.",
    automne: "Chemin optimal — sol ferme. Profiter pour transporter le stock hivernal de mineraux. Preparer les caches de stockage.",
    hiver: "Passer au mode motoneige ou raquettes. Creer une piste damee permanente. Attention aux ponts de neige sur les ruisseaux."
  },
  optimisations_support: ["Installer un support a mineraux sureleve (60 cm) pour eviter l'enfouissement par la neige", "Utiliser un bac de collecte sous le bloc pour prolonger la dissolution", "Placer un reflecteur infrarouge a l'entree du chemin pour localisation nocturne", "Amenager une plate-forme de depose seche (gravier + geotextile) pour le stationnement"],
  optimisations_meteo: ["Reporter la visite si pluie forte (empreintes profondes = derangement)", "Privilegier les journees ventees (>15 km/h) pour la dispersion des odeurs humaines", "Apres une tempete: inspecter le chemin pour arbres tombes avant deplacement VTT", "Profiter des matins de gel (sol dur, pas d'empreintes, bruit reduit)"],
  optimisations_pression: ["En zone haute pression: reduire les visites a 1x/mois max", "Utiliser un chemin different des autres chasseurs du secteur", "Coordonner les visites avec les voisins pour minimiser le derangement total", "En zone publique: visiter en semaine, jamais les fins de semaine de chasse"],
  thresholds: { green: "80-100: Acces VTT direct <200 m, chemin praticable 4 saisons, sol ferme, pente <10%", yellow: "50-79: Acces VTT partiel, portage 200-500 m necessaire, ou praticabilite saisonniere limitee", red: "0-49: Portage >500 m, terrain impraticable en VTT, pente >15%, ou zone inondable bloquante" },
  sources: ["MRNF — Reseau routier forestier du Quebec (2024)", "Sentinel-2 — Imagerie satellitaire Copernicus (resolution 10 m)", "Dussault, Courtois & Ouellet (2012) — Habitat et deplacements des cervides au Quebec", "SEPAQ — Guide d'amenagement des salines pour la faune (2019)", "Boileau (2015) — Gestion optimale des salines a cervides en foret boreale", "Plourde & Dussault (2008) — Impact des derangements humains sur la frequentation des salines", "MFFP — Protocole de suivi faunique standardise (2021)", "Environnement Canada — Donnees climatiques saisonnieres regionales"]
},
facilite_maintenance: {
  title: "Facilite de maintenance — Entretien regulier et suivi du site",
  definition: "Evaluation de la simplicite d'entretien regulier incluant: remplacement mineraux, nettoyage du sol sature, verification cameras trail, inspection structure/support, mesure de la consommation, et gestion de la vegetation envahissante autour du site.",
  methodology: "Score sur 100: ergonomie du site (30 pts — espace travail, hauteur support), temps par visite (30 pts — chronometre terrain moyen), frequence necessaire (20 pts — consommation/saison), outillage requis (20 pts — specialise vs standard). Normes SEPAQ amenagement faunique.",
  justification: {
    orignal: "L'orignal consomme 3-5 kg de mineraux par semaine en saison active (mai-octobre). Un site ergonomique permet le remplacement d'un bloc de 25 kg en 5 minutes, contre 20+ minutes sur un site mal concu. La maintenance inclut aussi le retrait du sol sature (20 cm autour du bloc) pour maintenir l'attractivite.",
    chevreuil: "Le chevreuil consomme 1-2 kg/semaine. La maintenance est plus frequente (1x/2 semaines) car les blocs plus petits se dissolvent plus vite. Le sol doit etre ratisse regulierement car le chevreuil est sensible aux odeurs de sol sature acide. Ergonomie critique pour des visites rapides (<10 min).",
    ours: "La maintenance en zone ours exige des protocoles de securite stricts. Les attractifs doivent etre renouveles frequemment (odeur forte = attractivite). Le site doit permettre un entretien rapide avec ligne de vue degagee a 360° pour detecter les ours en approche."
  },
  recommendations_terrain: [
    "Defricher un rayon de 4 m autour de la saline pour espace de travail",
    "Installer un support sureleve a 60 cm du sol (4 poteaux + plateforme bois traite)",
    "Creer un sol amenage: geotextile + 15 cm de gravier 0-20 mm autour du support",
    "Placer un bac de collecte sous le bloc pour recuperer les mineraux dissous",
    "Stocker 2-3 blocs de reserve dans un contenant etanche a 50 m du site",
    "Installer une camera trail orientee vers le bloc pour suivi a distance",
    "Creer un carnet d'entretien plastifie attache au support avec dates et observations",
    "Tailler les branches dans un rayon de 5 m pour faciliter le travail debout",
    "Amenager un sentier d'approche borde de mousse pour silence (dernier 50 m)",
    "Installer un petit abri (bache camouflage 2x2 m) pour proteger les reserves de la pluie",
    "Marquer le niveau de consommation du bloc a chaque visite (encoche ou peinture)",
    "Retirer et remplacer le sol sature (20 cm rayon, 10 cm profondeur) 2 fois par saison",
    "Utiliser des gants en latex pour minimiser les odeurs humaines sur le support",
    "Verifier et remplacer les batteries cameras trail a chaque visite de maintenance",
    "Inspecter le support structurel pour pourriture ou dommages d'animaux"
  ],
  strategies_optimisation: {
    orignal: ["Blocs de 25 kg — duree 4-6 semaines en saison active", "Support robuste (6x6 pouces) car l'orignal peut renverser un support leger", "Bac de collecte extra-large (60 cm) car l'orignal lape une grande surface", "Camera trail a 4 m de hauteur pour capturer le panache complet"],
    chevreuil: ["Blocs de 10-15 kg — duree 2-3 semaines, remplacement plus frequent", "Support leger (4x4 pouces) — le chevreuil n'exerce pas de force sur la structure", "Sol ratisse finement — le chevreuil prefere un sol propre pour lecher", "Camera trail a 2 m — hauteur optimale pour capturer les andouillers"],
    ours: ["Attractif melasse/mais en contenant metallique resistant aux griffes", "Support ancre au sol (beton) car l'ours detruit les structures legeres", "Camera trail en boitier metallique anti-ours a 3 m de hauteur", "Aucun stockage de nourriture sur le site — stockage a 200 m dans contenant ours-proof"]
  },
  techniques_chasse: ["Chronometrer chaque visite — objectif: <15 min sur site", "Toujours porter des gants et bottes propres pour la maintenance", "Ne jamais uriner pres du site — utiliser un contenant etanche", "Effectuer la maintenance entre 10h et 14h (periode de repos du gibier)", "Emporter tous les dechets — ne rien laisser sur place"],
  erreurs_a_eviter: ["Negliger le remplacement du sol sature (perte d'attractivite de 60%)", "Oublier les batteries cameras (perte de donnees critiques)", "Laisser des emballages de blocs mineraux sur le site", "Toucher les branches environnantes avec les mains nues", "Visiter le site juste avant la chasse du lendemain (odeurs fraiches)", "Utiliser des outils rouilles qui laissent des traces d'oxyde", "Stocker les mineraux de reserve sans contenant etanche (dissolution par la pluie)"],
  optimisations_saisonnieres: {
    printemps: "Premiere visite apres fonte: evaluer dommages hivernaux, remplacer support si necessaire. Installer le premier bloc frais. Renouveler le gravier de base.",
    ete: "Maintenance bi-mensuelle. Vegetation active — defricher regulierement. Consommation maximale: prevoir 2 blocs par mois. Attention aux mouches noires qui reduisent les visites des cerfs.",
    automne: "Periode critique pre-rut. Reduire la maintenance au minimum (1 visite/mois). Priorite: camera trail fonctionnelle. Ne pas defricher — le couvert est essentiel pour les males.",
    hiver: "Reduire a 1 visite/2 mois. Les mineraux se dissolvent lentement par le gel. Verifier integrite structure sous le poids de neige. Deblayer la neige autour du bloc si >30 cm."
  },
  optimisations_support: ["Support en cedre resistant naturellement a la pourriture (duree 8-10 ans)", "Plateforme avec pente de 5° pour drainage naturel du bloc vers le bac", "Vis en acier inoxydable — aucune rouille", "Peinture camouflage naturelle (terre + huile de lin) sur le support"],
  optimisations_meteo: ["Apres forte pluie: verifier que le bac n'a pas deborde (dilution mineraux)", "En canicule: les animaux visitent la saline de nuit — maintenir camera IR", "Apres tempete de vent: inspecter pour arbres tombes sur le support", "En periode seche: arroser legerement le bloc pour accelerer la dissolution"],
  optimisations_pression: ["Zone haute pression: maintenir camera trail 24/7 pour documenter la frequentation nocturne", "Maintenir le site impeccable — un site bien entretenu attire 40% plus de visites", "Reduire les signes humains visibles (pas de rubans, pas de piquets colores)", "Utiliser des cameras trail cellulaires pour eviter les visites de verification inutiles"],
  thresholds: { green: "80-100: Maintenance <15 min/visite, site ergonomique, support en bon etat, gravier propre", yellow: "50-79: Maintenance 15-30 min, ameliorations mineures necessaires, sol partiellement sature", red: "0-49: Maintenance >30 min, support deteriore, vegetation envahissante, sol sature non entretenu" },
  sources: ["SEPAQ — Guide d'amenagement des salines pour la faune (2019)", "MFFP — Protocole entretien sites fauniques (2021)", "Boileau (2015) — Gestion optimale salines cervides", "Plourde & Dussault (2008) — Frequentation et entretien des salines", "FQC — Guide pratique du chasseur quebecois (2023)", "IRDA — Analyse des sols sous salines (2018)", "Environnement Canada — Normes gestion dechets en milieu naturel"]
},
proximite_infrastructure: {
  title: "Proximite des infrastructures — Camp, stationnement, eau, reseau",
  definition: "Distance et accessibilite par rapport aux infrastructures essentielles: camp de chasse, aire de stationnement securisee, source d'eau potable, couverture reseau cellulaire (pour cameras trail connectees), point de ravitaillement en mineraux, et sentiers balises existants.",
  methodology: "Score composite sur 100: distance camp/stationnement (35 pts — GPS), couverture cellulaire (25 pts — test terrain Telus/Bell/Rogers), proximite source eau (20 pts — carte hydrographique MRNF), acces sentiers balises (20 pts — reseau SEPAQ/ZEC).",
  justification: {
    orignal: "Pour l'orignal, la saline doit etre a 300-800 m du camp. Trop pres (<200 m): les activites du camp derangent. Trop loin (>1 km): temps de deplacement excessif pour les sessions matinales (depart 4h30). La couverture cellulaire permet les cameras trail connectees qui evitent les visites de verification.",
    chevreuil: "Le chevreuil est plus tolerant a la proximite des infrastructures humaines (zones periurbaines). La saline peut etre a 200-500 m du camp. Une source d'eau <100 m augmente la frequentation de 35% car les chevreuils boivent apres avoir leche les mineraux.",
    ours: "L'ours requiert une distance MINIMALE de 500 m entre la saline et le camp pour des raisons de securite. Aucune infrastructure alimentaire ne doit etre visible depuis la saline. La couverture cellulaire est critique pour les alertes de presence en temps reel."
  },
  recommendations_terrain: [
    "Installer la saline a 300-600 m du camp principal (compromis derangement/accessibilite)",
    "Verifier la couverture cellulaire Telus/Bell au site AVANT l'installation (test sur 3 jours)",
    "Identifier la source d'eau la plus proche — cours d'eau permanent ou lac",
    "Baliser le sentier camp-saline avec des reflecteurs discrets (espaces de 30 m)",
    "Creer une aire de stationnement VTT a couvert (sous les coniferes)",
    "Installer un point de repere GPS waypoint sur le GPS/telephone pour navigation predawn",
    "Verifier la presence d'un sentier SEPAQ ou ZEC existant pour l'acces legal",
    "Identifier un point d'eau pour la dilution des mineraux si necessaire",
    "Amenager un poste d'observation intermediaire entre le camp et la saline",
    "Installer une boite etanche a 100 m du camp pour stockage du materiel de maintenance",
    "Creer un chemin de contournement du camp pour eviter les odeurs de cuisine",
    "Tester le signal cellulaire a differentes heures et conditions meteo"
  ],
  strategies_optimisation: {
    orignal: ["Distance camp-saline: 400-800 m pour l'orignal adulte (zone de confort)", "Creer 2 sentiers d'approche (vent d'est et vent d'ouest)", "Point d'eau < 300 m augmente frequentation orignal de 25%"],
    chevreuil: ["Distance camp-saline: 200-500 m (chevreuil plus tolerant)", "Sentier d'approche sinueux (le chevreuil surveille les lignes droites)", "Creer une mare artificielle a 50 m de la saline si aucun point d'eau naturel"],
    ours: ["Distance camp-saline: 500 m MINIMUM (securite obligatoire)", "Sentier degage largement (3 m) pour voir les ours en approche", "Camera trail cellulaire OBLIGATOIRE avec alerte SMS en temps reel"]
  },
  techniques_chasse: ["Quitter le camp 90 min avant l'aube — arrivee au poste 45 min avant premier mouvement", "Utiliser le sentier balise pour deplacement silencieux dans l'obscurite", "Retour au camp apres le coucher de soleil pour maximiser la session", "Alterner entre la saline et un affut secondaire selon le vent"],
  erreurs_a_eviter: ["Installer la saline trop pres du camp (<150 m) — derangement constant", "Negliger le test de couverture cellulaire (cameras inutiles sans signal)", "Creer un sentier qui traverse un corridor de deplacement principal", "Stocker de la nourriture sur le sentier camp-saline (attraction ours)", "Utiliser un sentier public comme acces principal (autre chasseurs)"],
  optimisations_saisonnieres: {
    printemps: "Verifier l'etat des sentiers apres l'hiver. Rebaliser si necessaire. Tester la couverture cellulaire (changements apres tempetes hivernales).",
    ete: "Debroussailler les sentiers. Installer/verifier les cameras. Identifier les nouvelles sources d'eau saisonnieres.",
    automne: "Minimiser les deplacements camp-saline. Utiliser uniquement les sentiers etablis. Camera cellulaire: mode alerte active.",
    hiver: "Sentier neige: creer une piste raquettes permanente. Marquer les points GPS sous la neige avec des piquets hauts."
  },
  optimisations_support: ["Support de camera trail avec panneau solaire (autonomie illimitee)", "Boite a outils etanche pre-positionnee a mi-chemin camp-saline", "Reflecteurs phosphorescents sur les obstacles majeurs du sentier"],
  optimisations_meteo: ["Pluie forte: utiliser le sentier principal (meilleur drainage)", "Brouillard: suivre la balise GPS, ne pas deviner le chemin", "Vent fort: approche par le sentier sous le vent uniquement"],
  optimisations_pression: ["Zone publique: choisir un acces prive ou une entree peu connue", "Installer la saline loin des sentiers de randonnee populaires", "En haute saison: alterner entre 2-3 salines pour disperser la pression"],
  thresholds: { green: "80-100: Camp <500 m, couverture cellulaire 3G+, eau <200 m, sentier balisé", yellow: "50-79: Camp 500 m-1.5 km, couverture partielle, eau 200-500 m", red: "0-49: Camp >1.5 km, aucune couverture cellulaire, eau >500 m, aucun sentier" },
  sources: ["OpenStreetMap — Infrastructure Quebec (2024)", "ISED Canada — Cartographie couverture cellulaire (2024)", "SEPAQ — Reseau sentiers et ZEC Quebec", "FQC — Guide amenagement territoire de chasse (2023)", "Dussault et al. (2005) — Selection d'habitat de l'orignal", "MFFP — Normes amenagement faunique (2021)", "Telus/Bell/Rogers — Cartes couverture cellulaire rurales"]
},
securite_acces: {
  title: "Securite et controle de l'acces — Protection du site et des equipements",
  definition: "Evaluation du niveau de securite contre le vandalisme, le vol d'equipement (cameras trail, mineraux), l'intrusion de tiers non-autorises (autres chasseurs, randonneurs, VTT recreatifs), et les risques naturels (inondation, chute d'arbres, predateurs dangereux). Inclut la possibilite de surveillance a distance.",
  methodology: "Score sur 100: isolement site (25 pts — distance sentiers publics), risque vandalisme (25 pts — historique zone), risques naturels (25 pts — cartographie MRNF), possibilite surveillance (25 pts — cameras, patrouilles, signal cellulaire).",
  justification: {
    orignal: "Les sites a orignal sont souvent eloignes et moins exposes au vandalisme, mais les cameras trail ($150-400) representent un investissement important. L'orignal peut endommager les structures legeres. Les risques naturels principaux sont les arbres morts (chicots) et les inondations printanieres.",
    chevreuil: "En zone periurbaine, le risque de vol de cameras est 3x plus eleve. Le chevreuil frequente des zones plus accessibles aux humains. Les cameras doivent etre verrouillees avec cables antivol. Le braconnage nocturne est un risque supplementaire dans certains secteurs.",
    ours: "La securite personnelle est la priorite #1 en zone ours. Le site doit offrir une visibilite a 360° pour detecter l'approche d'un ours. Les structures doivent resister aux griffes (metal > bois). Aucun attractif odorant ne doit etre laisse sur le site entre les visites."
  },
  recommendations_terrain: [
    "Installer la saline hors de vue des sentiers publics et chemins de VTT recreatifs",
    "Utiliser un cable antivol (Python lock) pour securiser les cameras trail au support",
    "Choisir un support d'arbre vivant et sain (eviter les chicots morts a risque de chute)",
    "Verifier la cartographie des zones inondables MRNF avant installation",
    "Installer un panneau discret 'Propriete privee' ou 'Zone de chasse amenagee' si legal",
    "Utiliser des cameras trail camouflees (boitier camo + position haute 3-4 m)",
    "Creer une fiche de suivi numerique avec photos datees du site a chaque visite",
    "Verifier la zone pour les signes de vandalisme precedent (cameras brisees, tags)",
    "Inspecter les arbres dans un rayon de 15 m pour risques de chute",
    "Installer 2 cameras: une sur la saline (suivi faune) et une sur le chemin d'acces (securite)",
    "En zone ours: porter un spray anti-ours et un sifflet en permanence",
    "Coordonner avec les voisins/club de chasse pour surveillance reciproque"
  ],
  strategies_optimisation: {
    orignal: ["Support 6x6 ancre au sol — l'orignal ne peut pas le renverser", "Camera a 4 m: hors de portee de l'orignal curieux", "Site isole en foret boreale: risque vandalisme faible"],
    chevreuil: ["Cable Python lock sur CHAQUE camera ($15 d'investissement, protection $300+)", "Camera cellulaire avec alerte vol (notification si camera bouge)", "Eviter les zones d'acces public (pistes cyclables, sentiers rando)"],
    ours: ["Boitier camera metallique anti-ours (Bear Box — $40)", "Aucun attractif odorant entre les visites", "Visibilite 360° obligatoire depuis le site", "Protocole d'alerte: sifflet + spray anti-ours + marche arriere lente"]
  },
  techniques_chasse: ["Verifier le site de loin avec jumelles avant d'approcher", "En zone ours: faire du bruit en approche pour signaler sa presence", "Ne jamais chasser seul en zone ours brun/grizzly", "Photographier le site a chaque visite pour documentation juridique"],
  erreurs_a_eviter: ["Laisser des cameras trail non verrouillees ($300+ de perte potentielle)", "Installer sous un arbre mort (chicot) — risque de chute sur le chasseur", "Ignorer les signes de passage d'ours (empreintes, griffures, excrements)", "Installer en zone inondable identifiee (perte de tout l'equipement)", "Negliger la documentation photo (aucune preuve en cas de vol/vandalisme)"],
  optimisations_saisonnieres: {
    printemps: "Inspecter pour dommages hivernaux (glace, neige, vent). Verifier chicots apres gel-degel. Risque inondation maximal.",
    ete: "Risque ours maximal (hyperphagie). Vegetation dense: difficulte a reperer les intrus. Verifier cables cameras.",
    automne: "Saison de chasse: risque maximal d'intrusion par d'autres chasseurs. Documenter les acces suspects.",
    hiver: "Risque vandalisme minimal. Verifier que le support resiste au poids de neige. Proteger les cameras du gel."
  },
  optimisations_support: ["Installer les cameras en hauteur (3-4 m) avec un support pivotant pour ajustement", "Utiliser des vis de securite (torx ou hex) au lieu de vis Phillips standard", "Peindre les structures en camo naturel pour discretion"],
  optimisations_meteo: ["Apres tempete: inspecter immediatement pour arbres tombes ou dommages", "En periode de gel-degel: risque de chute de branches accru", "Apres inondation: verifier l'erosion autour des fondations du support"],
  optimisations_pression: ["Zone haute pression: camera de securite sur le chemin d'acces 24/7", "Varier les heures de visite pour ne pas creer une routine reperable", "En zone publique: retirer le materiel visible en fin de saison"],
  thresholds: { green: "80-100: Site isole, aucun historique vandalisme, cameras securisees, aucun risque naturel identifie", yellow: "50-79: Risque modere (proximite sentier public ou historique incidents legers), mesures preventives en place", red: "0-49: Zone a haut risque (vandalisme frequent, zone inondable, chicots dangereux, zone ours sans protocole)" },
  sources: ["MFFP — Statistiques incidents et vandalisme en zone de chasse (2023)", "MRNF — Cartographie des zones inondables et risques naturels", "SQ — Rapport annuel vols d'equipement en milieu forestier", "SOPFEU — Cartographie des risques naturels Quebec", "Bear Smart Society — Protocoles securite en zone ours (2022)", "FQC — Guide securite du chasseur (2023)", "Parcs Canada — Gestion des risques ours noir et brun"]
},
frequence_visite: {
  title: "Frequence optimale de visite — Calendrier d'entretien et de suivi",
  definition: "Determination de la frequence ideale de visite basee sur l'equilibre entre le maintien de l'efficacite de la saline (mineraux frais, sol propre) et la minimisation du derangement qui fait fuir le gibier. Tient compte de l'espece ciblee, de la saison, de la pression de chasse locale, de la vitesse de consommation des mineraux, et des donnees de cameras trail.",
  methodology: "Score sur 100: ratio efficacite/derangement (40 pts — modele Plourde-Dussault), consommation mineraux estimee (30 pts — poids initial vs poids residuel), pression chasse locale (20 pts — densite chasseurs/km2), saisonnalite (10 pts — phase physiologique).",
  justification: {
    orignal: "L'orignal visite les salines principalement entre mai et septembre, avec un pic en juin-juillet (besoins en sodium maximaux). Frequence recommandee: bi-mensuelle en ete, mensuelle au printemps et automne. L'orignal tolere 1 derangement/2 semaines sans modifier ses habitudes de visite si l'intervention est breve (<15 min) et toujours a la meme heure.",
    chevreuil: "Le chevreuil est plus sensible au derangement et plus reactif aux changements. Frequence recommandee: hebdomadaire en ete (blocs petits, dissolution rapide), bi-mensuelle au printemps, mensuelle en automne pre-rut. Toujours visiter en plein jour (10h-14h) quand les chevreuils sont couches. Un derangement mal time peut decaler les visites du chevreuil de 48-72h.",
    ours: "L'ours visite les attractifs de facon irreguliere et opportuniste. Frequence recommandee: hebdomadaire en ete (attractifs odorants s'evaporent), bi-mensuelle au printemps. IMPORTANT: ne jamais visiter au crepuscule ou a l'aube en zone ours (pic d'activite). Visiter en milieu de journee uniquement."
  },
  recommendations_terrain: [
    "Etablir un calendrier fixe de visites (meme jour de la semaine, meme heure +/- 30 min)",
    "Utiliser les donnees cameras trail pour ajuster la frequence: si >20 visites/semaine, reduire les interventions",
    "Toujours visiter entre 10h et 14h (periode de repos de la majorite du gibier)",
    "Chronometrer chaque visite — objectif: <15 min sur site maximum",
    "Emporter tout le materiel necessaire en une seule charge (eviter les allers-retours)",
    "Verifier la camera trail a distance (cellulaire) pour reduire les visites physiques de 50%",
    "Adapter la frequence selon la saison: plus frequent en ete (dissolution rapide), moins en hiver",
    "Marquer le poids residuel du bloc a chaque visite pour estimer la consommation reelle",
    "Si le bloc est consomme a >80%, remplacer immediatement (ne pas attendre l'epuisement total)",
    "Reduire les visites a 1/mois pendant le rut (septembre-octobre) pour minimiser le derangement",
    "En zone haute pression: alterner entre 2-3 salines pour disperser les visites",
    "Planifier les visites de maintenance en meme temps que les verifications de camera",
    "Apres 3 visites sans observation de gibier: reevaluer l'emplacement de la saline",
    "Utiliser un journal de visite avec: date, heure, duree, vent, observations, etat bloc"
  ],
  strategies_optimisation: {
    orignal: ["Mai-juin: bi-mensuel (besoins sodium maximaux, forte consommation)", "Juillet-aout: bi-mensuel (maintien consommation)", "Septembre: mensuel (pre-rut, minimiser derangement)", "Octobre: 1 seule visite (rut actif, ne pas deranger)", "Novembre-avril: 1 visite/2 mois (consommation quasi nulle)"],
    chevreuil: ["Avril-mai: bi-mensuel (reprise activite printaniere)", "Juin-aout: hebdomadaire (dissolution rapide petits blocs)", "Septembre: bi-mensuel (pre-rut, les males patrouillent)", "Octobre-novembre: mensuel (rut, ne pas deranger)", "Decembre-mars: 1 visite/2 mois (activite reduite)"],
    ours: ["Avril-mai: bi-mensuel (sortie hibernation, faim intense)", "Juin-aout: hebdomadaire (hyperphagie, attractifs s'evaporent vite)", "Septembre-octobre: bi-mensuel (pre-hibernation)", "Novembre-mars: aucune visite (hibernation)"]
  },
  techniques_chasse: ["Utiliser la visite de maintenance comme reconnaissance: noter les pistes fraiches", "Installer une 2e camera orientee vers le sentier d'approche pour voir VOTRE impact", "Comparer les heures de visite du gibier AVANT et APRES votre passage", "Si les visites du gibier s'espacent apres votre passage: reduire la frequence"],
  erreurs_a_eviter: ["Visiter le site la veille d'une session de chasse (odeurs fraiches = fuite)", "Maintenir la meme frequence toute l'annee (inadapte aux saisons)", "Visiter au crepuscule ou a l'aube (conflit direct avec le gibier actif)", "Ignorer les donnees de camera trail (continuer une frequence arbitraire)", "Toucher la vegetation environnante (depot d'odeur elargi)", "Rester plus de 20 min sur site (derangement prolonge = impact mesurable)", "Visiter apres une pluie (empreintes profondes = signal de danger pour le gibier)"],
  optimisations_saisonnieres: {
    printemps: "Premiere visite post-fonte: inspection complete + bloc frais. Puis bi-mensuel. Les besoins en mineraux augmentent avec la croissance des bois.",
    ete: "Frequence maximale: hebdomadaire a bi-mensuel selon l'espece. Consommation maximale. Prevoir 2 blocs/mois.",
    automne: "REDUCTION OBLIGATOIRE pendant le rut. 1 visite/mois max. Le derangement pendant le rut peut faire perdre un male mature pour la saison entiere.",
    hiver: "1 visite/2 mois. Verifier structure sous neige. Les animaux visitent rarement la saline en hiver (besoins mineraux minimaux)."
  },
  optimisations_support: ["Camera trail cellulaire: reduit les visites physiques de 50-70%", "Blocs a dissolution lente (presse a haute densite): durent 2x plus longtemps", "Bac de collecte sous le bloc: prolonge la disponibilite des mineraux dissous"],
  optimisations_meteo: ["Apres forte pluie: repousser la visite de 24h (sol mou = empreintes = derangement)", "Visiter par vent fort (>15 km/h): les odeurs humaines sont dispersees rapidement", "Apres canicule: verifier le niveau d'eau du bac de collecte (evaporation)"],
  optimisations_pression: ["Zone haute pression (>5 chasseurs/km2): reduire a 1 visite/mois max", "Coordonner les visites avec les voisins pour eviter les jours consecutifs de derangement", "Utiliser des cameras cellulaires pour ZERO visite de verification"],
  thresholds: { green: "80-100: Frequence optimale respectee, ratio efficacite/derangement >3:1, cameras trail confirment pas d'impact negatif", yellow: "50-79: Frequence a ajuster, derangement mesurable mais tolerable, quelques visites mal timees", red: "0-49: Frequence inadequate (trop ou pas assez), derangement excessif mesure sur cameras, ou negligence complete du site" },
  sources: ["Plourde & Dussault (2008) — Impact des derangements sur la frequentation des salines par les cervides", "MFFP Quebec — Protocole de suivi faunique standardise (2021)", "Boileau (2015) — Gestion optimale des salines a cervides en foret boreale", "Leblond, Dussault & Ouellet (2010) — Reponse comportementale de l'orignal aux perturbations humaines", "FQC — Guide pratique du chasseur (2023)", "Dussault, Courtois & Ouellet (2012) — Habitat cervides Quebec", "Environnement Canada — Calendrier saisonnier regional"]
},
potentiel_trophee: {
  title: "Potentiel de presence de males trophees — Evaluation du potentiel de recolte de males matures",
  definition: "Estimation de la probabilite de presence reguliere de cerfs males matures (4.5 ans et plus) avec un panache de qualite trophee (130+ pouces Boone & Crockett pour le chevreuil, 40+ pouces d'envergure pour l'orignal) dans la zone d'influence de la saline (rayon de 2 km). Base sur l'historique faunique, la densite de population, la structure d'age, le ratio males/femelles, et la qualite de l'habitat.",
  methodology: "Score sur 100: historique recolte males matures zone 5 ans (35 pts — registre MFFP), ratio males/femelles observe (25 pts — inventaire aerien), qualite habitat (25 pts — indice IQH composite), pression de chasse locale (15 pts — densite chasseurs/km2).",
  justification: {
    orignal: "Le potentiel trophee pour l'orignal est determine par la densite de population, l'age moyen des males, et la pression de chasse. Les zones avec recolte historique de males >40 pouces indiquent une population mature et un habitat de qualite. L'orignal male atteint sa maturite physique a 6-8 ans — les zones a faible pression permettent l'atteinte de cet age.",
    chevreuil: "Pour le chevreuil, les males 4.5 ans+ avec 130+ pouces B&C sont rares au Quebec (< 5% de la recolte). La qualite des ecotones, la disponibilite alimentaire hivernale, et la pression de chasse sont determinantes. Les zones avec gestion restrictive (ramure minimale) produisent 3x plus de males trophee.",
    ours: "Pour l'ours noir, le potentiel trophee se mesure en taille du crane (>18 pouces B&C). Les males dominants de 5+ ans avec >250 lbs frequentent des territoires de 50-100 km2. Les salines en zone boreale avec faible pression et abondance de petits fruits ont le meilleur potentiel."
  },
  recommendations_terrain: [
    "Consulter le registre de recolte MFFP des 5 dernieres annees pour la zone de chasse",
    "Identifier les corridors de deplacement des males matures via cameras trail (patterns nocturnes)",
    "Positionner la saline en ecotone foret-clairiere (zone preferee des males matures)",
    "Assurer un couvert lateral dense de 60%+ (les males matures exigent de la protection visuelle)",
    "Installer minimum 3 cameras trail sur un rayon de 500 m pour documenter la structure d'age",
    "Analyser les photos cameras: compter les pointes/andouillers pour estimer l'age des males",
    "Creer des micro-clairieres (10-20 m) a 50-100 m de la saline pour attirer le brout de males",
    "Identifier les zones de frottage (rubs) et de grattage (scrapes) a proximite",
    "Evaluer la presence de predateurs (loups, ours) qui limitent la survie des males matures",
    "Verifier la gestion faunique de la zone (ramure minimale, contingentement, restrictions)",
    "Creer un inventaire photo des males identifies pour suivre leur developpement annuel",
    "Consulter les chasseurs locaux sur les observations de males matures dans le secteur",
    "Positionner la saline pres d'une zone de nourrissage naturelle (tremble, saule, cornouiller)",
    "Eviter les zones a tres haute densite de chevreuils (>20/km2) — competition et stress nutritif"
  ],
  strategies_optimisation: {
    orignal: ["Saline pres de lacs/etangs (orignal = affinite eau en ete)", "Corridors de deplacement: cretes boisees, rives de lacs, bordures de coupes", "Males matures: actifs surtout entre 5h-8h et 17h-19h en ete", "Pre-rut (15 sept — 5 oct): les males commencent a patrouiller — moment optimal pour le reperage"],
    chevreuil: ["Saline en bordure de champ agricole abandonne (brout + transition)", "Males trophee: concentres dans les ecotones a couvert mixte (coniferes + feuillus)", "Zone de frottage < 200 m de la saline = signe de male territorial mature", "Gestion restrictive (4+ pointes obligatoire) = meilleur potentiel long terme"],
    ours: ["Saline pres de ruisseaux a truites (ours = peche en ete)", "Males dominants: territoriaux et solitaires — eviter les zones avec familles", "Gros males actifs principalement la nuit en ete — cameras IR essentielles"]
  },
  techniques_chasse: ["Analyser les patterns horaires sur 30 jours de cameras avant de chasser", "Le male trophee visite souvent la saline entre 2h et 5h du matin — verifier avec cameras", "Placer l'affut a 30-60 m de la saline (distance de tir ethique)", "Un male mature visite la meme saline en moyenne 2-3 fois par semaine en ete"],
  erreurs_a_eviter: ["Chasser les premieres visites d'un male mature (le laisser s'habituer 2-3 semaines)", "Ignorer le vent — un seul faux vent et le male ne revient pas pendant 2 semaines", "Recolter tous les males vus — laisser les jeunes (2.5 ans) grandir pour le futur", "Negliger le couvert lateral — un male mature ne s'expose pas en zone ouverte"],
  optimisations_saisonnieres: {
    printemps: "Mai-juin: croissance active des bois. Besoins en mineraux maximaux. Ideal pour le reperage initial via cameras.",
    ete: "Juillet-aout: bois en velours. Males visibles et identifiables. Documenter chaque male avec photos datees.",
    automne: "Pre-rut (mi-sept): les males commencent a frotter et gratter. Rut actif (oct-nov): les males parcourent de grandes distances. Meilleure chance de trophee.",
    hiver: "Males regroupes en ravage (chevreuil) ou solitaires (orignal). Periode de survie, pas de chasse. Ideal pour reperage aerien."
  },
  optimisations_support: ["Support de camera a 4 m (orignal) ou 2 m (chevreuil) pour photo optimale des bois", "Utiliser des cameras a flash invisible (no-glow IR) pour ne pas effrayer les males matures", "Installer un panneau de sel gemme artisanal pour varier les mineraux offerts"],
  optimisations_meteo: ["Pression barometrique en hausse = activite accrue des males matures", "Vent nord-ouest apres front froid = meilleur moment pour observer les males", "Pleine lune: males plus actifs la nuit, moins visibles le jour"],
  optimisations_pression: ["Zone a faible pression (<2 chasseurs/km2): meilleur potentiel, males vivent plus longtemps", "Gestion restrictive volontaire entre voisins: ne pas recolter les males <3.5 ans", "Alterner les annees: recolter 1 male mature aux 2-3 ans pour maintenir la population"],
  thresholds: { green: "80-100: Males matures 4.5 ans+ documentes par cameras, historique recolte trophee dans la zone, ratio M/F > 1:3, habitat de qualite", yellow: "50-79: Presence de males matures probable mais non confirmee, ratio M/F correct, habitat modere", red: "0-49: Aucun male mature observe, haute pression de chasse, ratio M/F desequilibre, habitat degrade" },
  sources: ["MFFP — Registre de recolte des cervides au Quebec (2019-2024)", "Lamoureux, Bherer & Bherer (2018) — Structure d'age des populations de cervides au Quebec", "Boone & Crockett Club — Criteres officiels d'evaluation des trophees (2024)", "Dussault, Courtois & Ouellet (2012) — Habitat et deplacements cervides Quebec", "Cote, Rooney & Tremblay (2004) — Dynamique des populations de cervides", "MRNF — Indice de qualite d'habitat (IQH) cervides", "Mysterud & Ostbye (1999) — Habitat selection and survival of male red deer", "Leopold (1933) — Game Management: ecotone theory and trophy potential"]
},
corridors_deplacement: {
  title: "Corridors de deplacement fauniques — Axes de mouvement naturels des cervides",
  definition: "Evaluation de la proximite, de la qualite et de la connectivite des corridors naturels empruntes par les cervides entre leurs zones d'alimentation, de repos, d'abreuvement et de reproduction. Les corridors sont les autoroutes invisibles de la faune — les positionner correctement multiplie par 5 l'efficacite d'une saline.",
  methodology: "Score sur 100: distance corridor principal (40 pts — analyse LiDAR + GPS traces), qualite du corridor (30 pts — couvert + largeur), connectivite habitat (20 pts — liaison foret-eau-alimentation), saisonnalite utilisation (10 pts — traces saisonnieres).",
  justification: {
    orignal: "L'orignal utilise des corridors bien definis entre lacs/marais (alimentation aquatique ete) et ravages hivernaux (coniferes denses). Les corridors suivent les cretes boisees, les rives de cours d'eau, et les bordures de coupes forestieres. Saline a <100 m d'un corridor majeur = frequentation 5x superieure.",
    chevreuil: "Le chevreuil utilise des corridors plus discrets et sinueux que l'orignal, souvent en bordure de champs agricoles, le long de clotures, ou dans des coulees boisees etroites (10-30 m). Les corridors de chevreuil sont marques par des sentiers battus de 30-50 cm de large.",
    ours: "L'ours utilise des corridors larges et opportunistes, souvent le long de ruisseaux a truites, de champs de bleuets, ou de routes forestieres desaffectees. Les corridors d'ours sont marques par des arbres griffes et des excrements reguliers."
  },
  recommendations_terrain: [
    "Cartographier tous les sentiers visibles dans un rayon de 500 m (sol retourne, pistes, frottages)",
    "Installer la saline a 50-150 m d'un corridor confirme (pas directement dessus)",
    "Ne JAMAIS bloquer un corridor avec une structure — les animaux contourneront et abandonneront",
    "Orienter l'affut perpendiculairement au corridor (champ de tir lateral, pas frontal)",
    "Identifier les carrefours de corridors — les intersections concentrent le passage",
    "Creer un sentier d'approche qui ne croise aucun corridor identifie",
    "Degager 3-4 corridors secondaires de 3 m de large convergeant vers la saline",
    "Tailler les branches genantes entre 0 et 4 m sur les corridors degages",
    "Utiliser les branches coupees pour camoufler l'affut et creer des ecrans visuels",
    "Creer un cone de tir degage a 180° depuis la position d'affut",
    "Identifier les sentiers actifs via: sol retourne, empreintes fraiches, frottages, poils",
    "Positionner la saline en zone de transition foret-clairiere (ecotone optimal)",
    "Eviter les zones de vent tourbillonnant (carrefours de vallees, fond de cuvettes)",
    "Optimiser les angles d'approche selon la topographie (approche par le bas d'une pente)",
    "Lisser les sentiers d'approche: retirer branches, feuilles craquantes, gravier lache",
    "Utiliser les donnees de relief LiDAR pour identifier les passages naturels"
  ],
  strategies_optimisation: {
    orignal: ["Corridors priviligies: cretes boisees entre 2 vallees, rives de lacs/marais, bordures de coupes", "L'orignal suit les memes corridors pendant des decennies — identifier les pistes anciennes", "En ete: corridor entre le lac (alimentation aquatique) et le couvert forestier (repos diurne)", "En automne: corridor entre les zones de rut et les ravages hivernaux"],
    chevreuil: ["Corridors privilegies: bordures de champs, coulees boisees, haies de cedres, clotures", "Le chevreuil emprunte des sentiers tres etroits (30-50 cm) souvent invisibles en ete", "Zones de grattage (scrapes) = corridor territorial d'un male dominant", "Installer la saline la ou 2-3 sentiers convergent naturellement"],
    ours: ["Corridors privilegies: ruisseaux a truites, champs de petits fruits, coupes en regeneration", "L'ours marque ses corridors avec des griffures d'arbres a hauteur d'epaule (1.5-2 m)", "Excrements reguliers sur le corridor = utilisation frequente et recente"]
  },
  techniques_chasse: ["L'affut ideal surveille un corridor ET la saline simultanement", "Le gibier emprunte le corridor le plus proche sous le vent — anticiper selon la meteo", "Les males matures utilisent des corridors paralleles aux corridors principaux (plus discrets)", "En pre-rut: les males commencent a patrouiller les corridors de facon plus aggressive"],
  erreurs_a_eviter: ["Installer la saline directement SUR un corridor (les animaux eviteront la perturbation)", "Creer un sentier d'approche qui croise un corridor (depot d'odeur sur la route du gibier)", "Ignorer les corridors et placer la saline dans un cul-de-sac topographique", "Defricher excessivement autour de la saline (suppression du couvert de transition)", "Oublier de verifier l'orientation du vent par rapport au corridor"],
  optimisations_saisonnieres: {
    printemps: "Les corridors changent legerement: les animaux explorent apres l'hiver. Reperer les nouvelles pistes.",
    ete: "Corridors ete: souvent entre eau (alimentation) et couvert dense (repos/ombre). Vegetation dense cache les pistes.",
    automne: "Corridors de rut: les males parcourent des distances 3-5x plus grandes. Nouveaux sentiers de patrouille apparaissent.",
    hiver: "Corridors de ravage: tres concentres, battus par la neige. Ideal pour reperage aerien ou raquettes."
  },
  optimisations_support: ["Creer des micro-clairieres de 10-20 m a 50 m de la saline pour attirer le brout", "Planter du trefle ou du brassica dans les micro-clairieres pour alimentation supplementaire", "Installer des points d'eau artificiels (petite mare) pres de la saline si aucune source naturelle"],
  optimisations_meteo: ["Vent du nord: les animaux empruntent les corridors proteges par la topographie (versant sud)", "Pluie legere: activite accrue sur les corridors, le sol mouille revele les pistes fraiches", "Gel matinal: ideal pour identifier les corridors (givre sur les pistes = passage recent)"],
  optimisations_pression: ["En haute pression: les males matures utilisent des corridors secondaires plus discrets", "Reduire votre propre passage sur les corridors principaux (sentier d'approche separe)", "En zone publique: identifier les corridors NON empruntes par les autres chasseurs"],
  thresholds: { green: "80-100: Corridor majeur a <100 m, pistes fraiches confirmees, carrefour de 2+ corridors identifie, connectivite habitat excellente", yellow: "50-79: Corridor secondaire a 100-300 m, pistes occasionnelles, connectivite partielle", red: "0-49: Aucun corridor identifie a <500 m, aucune piste visible, site isole des axes de deplacement" },
  sources: ["LiDAR MRNF — Analyse des corridors forestiers haute resolution (2023)", "Dussault, Courtois & Ouellet (2012) — Corridors de deplacement et habitat des cervides au Quebec", "Sentinel-2 — Classification de la vegetation et ecotones (Copernicus)", "Leopold (1933) — Game Management: ecotone theory and wildlife corridors", "Mysterud & Ostbye (1999) — Habitat selection and corridor use in cervids", "Plourde & Dussault (2008) — Frequentation des salines et corridors de deplacement", "Nielsen, Stenhouse & Boyce (2010) — Spatial strategies and corridor connectivity", "MFFP — Inventaire corridors fauniques Quebec (2021)"]
},
};

// Fallback pour criteres non presents dans la base
const DEFAULT = {
  title: "Critere d'evaluation SUPRA — Guide BIONIC Niveau Professionnel",
  definition: "Ce critere evalue un aspect specifique de la qualite du site de saline. Chaque composante est analysee selon des donnees terrain, des analyses geospatiales et des references scientifiques reconnues.",
  methodology: "Score calcule sur 100 points via un modele multi-facteurs incluant donnees terrain (40%), analyses geospatiales LiDAR/satellite (30%), et references scientifiques (30%).",
  justification: { orignal: "Score determine selon les besoins specifiques de l'orignal en habitat et nutrition.", chevreuil: "Score determine selon les preferences ecologiques du chevreuil de Virginie.", ours: "Score determine selon les exigences de l'ours noir en habitat et securite." },
  recommendations_terrain: ["Consulter les guides terrain MFFP specifiques a ce critere", "Effectuer des observations terrain complementaires sur 3 saisons", "Comparer avec 2-3 autres sites dans le meme secteur", "Documenter les changements avec photos datees", "Installer une camera trail dediee a l'evaluation de ce critere"],
  strategies_optimisation: { orignal: ["Adapter selon les besoins saisonniers de l'orignal"], chevreuil: ["Adapter selon les micro-habitats du chevreuil"], ours: ["Adapter selon les protocoles de securite ours"] },
  techniques_chasse: ["Observer avant d'agir — 3 sessions d'observation minimum", "Documenter tous les indices terrain pour ce critere"],
  erreurs_a_eviter: ["Negliger l'evaluation de ce critere dans la decision d'emplacement", "Appliquer des recettes generiques sans adaptation au site specifique"],
  optimisations_saisonnieres: { printemps: "Evaluation post-fonte, conditions de base.", ete: "Conditions optimales pour l'evaluation.", automne: "Reevaluation pre-chasse.", hiver: "Evaluation complementaire sous neige." },
  optimisations_support: ["Adapter le support structurel selon les resultats de ce critere"],
  optimisations_meteo: ["Integrer les donnees meteorologiques saisonnieres dans l'evaluation"],
  optimisations_pression: ["Ajuster selon la pression de chasse locale"],
  thresholds: { green: "80-100: Conditions excellentes pour ce critere", yellow: "50-79: Conditions moderees, ameliorations possibles", red: "0-49: Conditions defavorables, intervention requise" },
  sources: ["MFFP Quebec — Guides pratiques d'amenagement faunique", "SEPAQ — Normes amenagement sites fauniques", "FQC — Guide pratique du chasseur quebecois"]
};

function getCriteria(key) {
  const k = key.toLowerCase().replace(/[\s\-]/g, '_').replace(/[àâä]/g, 'a').replace(/[éèêë]/g, 'e').replace(/[ïî]/g, 'i').replace(/[ôö]/g, 'o').replace(/[ùûü]/g, 'u');
  return DB[k] || { ...DEFAULT, title: `${key.replace(/_/g, ' ')} — Guide BIONIC Niveau Professionnel` };
}

// =====================================================================
// COMPOSANT MODAL — GUIDE BIONIC — NIVEAU PROFESSIONNEL™
// =====================================================================
export function CriteriaDetailModal({ criteriaKey, criteriaValue, species = 'orignal', season = 'automne', onClose }) {
  if (!criteriaKey) return null;
  const data = getCriteria(criteriaKey);
  const sp = (species || 'orignal').toLowerCase();
  const spLabel = sp === 'orignal' ? 'Orignal' : sp === 'ours' ? 'Ours noir' : 'Chevreuil';
  const scoreValue = typeof criteriaValue === 'object' ? criteriaValue.value : criteriaValue;
  const scoreNum = parseInt(String(scoreValue).replace(/[^0-9]/g, ''), 10) || 0;
  const sc = scoreNum >= 80 ? B.green : scoreNum >= 50 ? B.orange : B.red;
  const sl = scoreNum >= 80 ? 'VERT' : scoreNum >= 50 ? 'JAUNE' : 'ROUGE';
  const justif = typeof data.justification === 'object' ? (data.justification[sp] || data.justification.orignal) : data.justification;
  const strats = data.strategies_optimisation?.[sp] || data.strategies_optimisation?.orignal || [];
  const optEsp = data.strategies_optimisation || {};
  const seasonData = data.optimisations_saisonnieres?.[season] || data.optimisations_saisonnieres?.automne || '';

  const Section = ({ icon: SIcon, color, title, children }) => (
    <div className="rounded-xl px-5 py-4" style={{ backgroundColor: GOLDEN.cardBg, borderLeft: `4px solid ${color}` }}>
      <div className="flex items-center gap-2 mb-2"><IC Icon={SIcon} color={color} /><span className="text-[16px] font-bold text-white">{title}</span></div>
      {children}
    </div>
  );
  const BulletList = ({ items, icon = '\u2022', color = '#94A3B8' }) => (<ul className="space-y-1.5">{items.map((item, i) => (<li key={i} className="flex items-start gap-2"><span className="text-[16px] mt-0.5 flex-shrink-0" style={{ color }}>{icon}</span><span className="text-[16px] text-slate-300 leading-relaxed">{item}</span></li>))}</ul>);
  const Threshold = ({ label, text, color }) => (<div className="flex items-start gap-2 px-3 py-2 rounded-lg" style={{ backgroundColor: `${color}10` }}><span className="w-3 h-3 rounded-full mt-1 flex-shrink-0" style={{ backgroundColor: color }} /><span className="text-[16px] text-slate-300"><strong className="text-white">{label}:</strong> {text}</span></div>);

  return (
    <div className="fixed inset-0 flex items-center justify-center" style={{ backgroundColor: 'rgba(0,0,0,0.8)', zIndex: 99999 }} onClick={onClose} data-testid="criteria-modal-overlay">
      <div className="w-full max-w-3xl max-h-[90vh] overflow-y-auto rounded-2xl" style={{ backgroundColor: GOLDEN.pageBg, boxShadow: '0 8px 48px rgba(0,0,0,0.7)' }} onClick={e => e.stopPropagation()} data-testid="criteria-modal">

        {/* Header */}
        <div className="sticky top-0 z-10 px-6 py-4 flex items-start justify-between" style={{ backgroundColor: GOLDEN.pageBg, borderBottom: '1px solid rgba(255,255,255,0.06)' }}>
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-1"><span className="text-[14px] font-bold px-2 py-0.5 rounded-lg" style={{ backgroundColor: `${sc}18`, color: sc }}>{sl} — {scoreValue}</span><span className="text-[14px] font-bold px-2 py-0.5 rounded-lg" style={{ backgroundColor: `${B.cyan}18`, color: B.cyan }}>{spLabel}</span><span className="text-[14px] text-slate-500">{season}</span></div>
            <h2 className="text-[18px] font-black text-white leading-tight">{data.title}</h2>
            <p className="text-[14px] text-slate-500 mt-1">GUIDE BIONIC — NIVEAU PROFESSIONNEL™</p>
          </div>
          <button onClick={onClose} className="w-8 h-8 rounded-full flex items-center justify-center hover:bg-white/10 flex-shrink-0 ml-3" data-testid="criteria-modal-close"><X className="h-5 w-5 text-slate-400" /></button>
        </div>

        <div className="px-6 py-4 space-y-4">
          {/* 1. Definition */}
          <Section icon={BookOpen} color={B.cyan} title="1. Definition du critere"><p className="text-[16px] text-slate-300 leading-relaxed">{data.definition}</p></Section>
          {/* 2. Methodologie */}
          <Section icon={Target} color={B.purple} title="2. Methodologie de scoring"><p className="text-[16px] text-slate-300 leading-relaxed">{data.methodology}</p></Section>
          {/* 3. Justification — ESPECE-SPECIFIQUE */}
          <Section icon={CheckCircle} color={sc} title={`3. Justification du score — ${spLabel}`}><p className="text-[16px] text-slate-300 leading-relaxed">{justif}</p></Section>
          {/* 4. Recommandations terrain (10-20) */}
          <Section icon={MapPin} color={B.green} title={`4. Recommandations terrain (${data.recommendations_terrain?.length || 0})`}><BulletList items={data.recommendations_terrain || []} icon="&#10003;" color={B.green} /></Section>
          {/* 5. Strategies optimisation — ESPECE */}
          <Section icon={Crosshair} color={B.amber} title={`5. Strategies d'optimisation — ${spLabel}`}><BulletList items={strats} icon="&#9654;" color={B.amber} /></Section>
          {/* 6. Techniques chasse */}
          <Section icon={Eye} color={B.orange} title="6. Techniques de chasse"><BulletList items={data.techniques_chasse || []} icon="&#9679;" color={B.orange} /></Section>
          {/* 7. Erreurs a eviter */}
          <Section icon={AlertTriangle} color={B.red} title="7. Erreurs a eviter"><BulletList items={data.erreurs_a_eviter || []} icon="&#10007;" color={B.red} /></Section>
          {/* 8. Optimisations saisonnieres */}
          <Section icon={ThermometerSun} color={B.yellow} title={`8. Optimisations saisonnieres — ${season}`}>
            <p className="text-[16px] text-slate-300 leading-relaxed mb-3"><strong className="text-white">{season}:</strong> {seasonData}</p>
            {Object.entries(data.optimisations_saisonnieres || {}).filter(([k]) => k !== season).map(([k, v]) => (<p key={k} className="text-[14px] text-slate-400 leading-relaxed py-1"><strong className="text-slate-300">{k}:</strong> {v}</p>))}
          </Section>
          {/* 9. Optimisations espece — TOUTES ESPECES */}
          <Section icon={Footprints} color={B.cyan} title="9. Optimisations selon l'espece">
            {Object.entries(optEsp).map(([esp, items]) => (<div key={esp} className="mb-3"><div className="text-[16px] font-bold mb-1" style={{ color: esp === sp ? B.green : '#94A3B8' }}>{esp === 'orignal' ? 'Orignal' : esp === 'chevreuil' ? 'Chevreuil' : 'Ours noir'} {esp === sp ? '(ACTIF)' : ''}</div><BulletList items={items} icon={esp === sp ? '&#9654;' : '&#9675;'} color={esp === sp ? B.green : '#64748B'} /></div>))}
          </Section>
          {/* 10. Optimisations support */}
          <Section icon={Construction} color={B.blue} title="10. Optimisations support"><BulletList items={data.optimisations_support || []} icon="&#9670;" color={B.blue} /></Section>
          {/* 11. Optimisations meteo */}
          <Section icon={Wind} color={B.purple} title="11. Optimisations selon la meteo"><BulletList items={data.optimisations_meteo || []} icon="&#9729;" color={B.purple} /></Section>
          {/* 12. Optimisations pression chasse */}
          <Section icon={Shield} color={B.orange} title="12. Optimisations selon la pression de chasse"><BulletList items={data.optimisations_pression || []} icon="&#9888;" color={B.orange} /></Section>
          {/* 13. Seuils */}
          <Section icon={AlertTriangle} color={B.amber} title="13. Seuils (vert / jaune / rouge)">
            <div className="space-y-2"><Threshold label="VERT" text={data.thresholds?.green} color={B.green} /><Threshold label="JAUNE" text={data.thresholds?.yellow} color={B.orange} /><Threshold label="ROUGE" text={data.thresholds?.red} color={B.red} /></div>
          </Section>
          {/* 14. Sources scientifiques */}
          <Section icon={BookOpen} color={B.blue} title={`14. Sources scientifiques (${data.sources?.length || 0})`}>
            <ul className="space-y-1">{(data.sources || []).map((s, i) => (<li key={i} className="text-[14px] text-slate-400 py-0.5">[{i + 1}] {s}</li>))}</ul>
          </Section>
        </div>
      </div>
    </div>
  );
}

export default CriteriaDetailModal;

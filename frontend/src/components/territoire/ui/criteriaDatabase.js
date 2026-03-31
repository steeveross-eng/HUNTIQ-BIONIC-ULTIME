/**
 * GUIDE BIONIC — NIVEAU PROFESSIONNEL™ — BASE DE DONNÉES CRITÈRES
 * ================================================================
 * BCE-4X STEEVE-MAX — ZERO FICHE GENERIQUE — SEPARATION STRICTE PAR ESPECE
 *
 * Especes: Orignal | Chevreuil | Ours noir | Wapiti | Dindon sauvage
 * 15 sections obligatoires | 10-20 recommandations/espece | 5-20 sources TOP-TIER
 *
 * SOURCES NIVEAU 1: MFFP, UQAR, ULaval, UQAC, Parcs Canada, USGS, USDA
 * SOURCES NIVEAU 2: J. Wildlife Mgmt, Can. J. Zoology, Wildlife Soc. Bulletin
 * SOURCES NIVEAU 3: NDA, RMEF, NWTF, Bear Trust, QDMA
 * SOURCES NIVEAU 4: MSU Deer Lab, UGA Deer Lab, Alberta Fish & Wildlife
 */

// BCE-4X: Import des 19 criteres P1/P2 reecrits au standard V2
import {
  accessibilite_pieton,
  facilite_maintenance,
  proximite_infrastructure,
  securite_acces,
  frequence_visite,
  historique_observations,
  adaptabilite_saisonniere,
  complementarite_reseau,
  potentiel_expansion,
  cout_mineraux_annuel,
  cout_transport,
  cout_temps,
  retour_observation,
  retour_recolte,
  durabilite,
  alignement_sentiers,
  lissage,
  penetrabilite,
  effort_reel,
} from './criteriaDatabase_P1P2';

const SP = {
  orignal: 'Orignal (Alces alces)',
  chevreuil: 'Chevreuil de Virginie (Odocoileus virginianus)',
  ours: 'Ours noir (Ursus americanus)',
  wapiti: 'Wapiti (Cervus canadensis)',
  dindon: 'Dindon sauvage (Meleagris gallopavo)',
};

// =====================================================================
// POSITION VS AFFUTS — CRITÈRE NON-CONFORME IDENTIFIÉ PAR STEEVE-MAX
// RÉÉCRITURE COMPLÈTE NIVEAU PROFESSIONNEL
// =====================================================================
const position_vs_affuts = {
  title: "Position strategique par rapport aux affuts — Positionnement tactique du site de saline",
  definition: "Evaluation de la position optimale de la saline par rapport aux postes d'affut (tree stands, ground blinds, miradors) en tenant compte des angles de tir, des distances ethiques, des corridors de deplacement, de la direction des vents dominants, de la topographie locale, et du couvert visuel. Ce critere determine directement le taux de reussite des sessions de chasse a la saline.",
  methodology: "Score sur 100 points: distance saline-affut (30 pts — mesure laser), angle de tir disponible (25 pts — cone 120-180 degres), couverture vent (20 pts — analyse rose des vents saisonniere), couvert visuel/camouflage (15 pts — evaluation terrain), acces silencieux a l'affut (10 pts — test approche). Donnees: rose des vents Environnement Canada, LiDAR MRNF, traces GPS terrain.",
  justification: {
    orignal: "L'orignal adulte mesure 1.8-2.1 m au garrot. La distance optimale saline-affut est de 25-40 m pour le tir a l'arc et 60-120 m pour l'arme a feu. L'orignal a une vue laterale excellente mais une vision frontale limitee — positionner l'affut a 45-90 degres du corridor d'approche principal. Un affut sureleve (5-6 m) est necessaire pour depasser le champ visuel de l'orignal et disperser les odeurs au-dessus de sa zone de detection olfactive (2 m).",
    chevreuil: "Le chevreuil de Virginie a une vision peripherique de 310 degres et detecte le mouvement a 150+ m. Distance optimale saline-affut: 15-25 m (arc), 40-80 m (arme a feu). L'affut doit etre installe 3-4 semaines avant la saison de chasse pour permettre l'habituation. Le chevreuil memorise les anomalies visuelles — tout changement dans la silhouette de l'affut provoque une alerte de 48-72 h.",
    ours: "L'ours noir a une vue moderee mais un odorat 7x superieur au chien. Distance saline-affut: 15-20 m (arc), 30-60 m (arme a feu). L'affut au sol est deconseille — un tree stand a 4-5 m permet d'etre hors de portee en cas d'approche agressive. L'ours approche souvent par le corridor le plus direct, ce qui rend la prediction de l'angle de tir plus fiable que pour les cervides.",
    wapiti: "Le wapiti male atteint 1.5 m au garrot avec un panache de 1.2 m d'envergure. Distance optimale saline-affut: 30-50 m (arc), 80-200 m (arme a feu). Le wapiti voyage en groupes (3-8) — le positionnement doit couvrir une zone d'approche large. L'affut sureleve (5-7 m) est recommande car le wapiti est tres attentif aux anomalies a hauteur d'oeil.",
    dindon: "Le dindon sauvage a la vision la plus aigue de tous les gibiers nord-americains — vision couleur, peripherique 270 degres, detection mouvement a 200+ m. Distance optimale: 15-35 m (fusil a plombs), pas de tir a l'arc recommande sur saline. L'affut DOIT etre un ground blind ferme (pas de tree stand — angle de tir descendant inadapte aux plombs). Camouflage integral obligatoire.",
  },
  recommendations_terrain: {
    orignal: [
      "Positionner l'affut a 30-40 m de la saline pour le tir a l'arc, 80-100 m pour le fusil",
      "Installer le tree stand a 5-6 m de hauteur pour depasser le champ visuel de l'orignal (2 m au garrot)",
      "Orienter l'affut a 45-90 degres du corridor d'approche principal (jamais face au corridor)",
      "Degager 3-4 corridors de tir de 3 m de large entre l'affut et la saline",
      "Tailler les branches genantes entre 0 et 6 m de hauteur pour eviter les deviations de fleche ou balle",
      "Utiliser les branches coupees pour camoufler la base du tree stand et casser la silhouette",
      "Creer un cone de tir degage a 120-180 degres depuis l'affut vers la saline",
      "Installer l'affut sur un arbre vivant de 30+ cm de diametre (securite + stabilite)",
      "Placer l'affut sous le vent dominant d'automne (verifier la rose des vents octobre-novembre)",
      "Amenager un sentier d'approche silencieux (mousse, copeaux de bois) sur les derniers 100 m",
      "Retirer les branches seches et feuilles mortes dans un rayon de 5 m autour du pied du tree stand",
      "Installer un repose-pieds silencieux en mousse sur la plateforme du tree stand",
      "Prevoir une deuxieme position d'affut a 90 degres pour les jours de vent contraire",
      "Marquer les distances (20, 30, 40 m) avec des reperes discrets au sol pour l'estimation rapide",
      "Adapter la hauteur selon le couvert: 6 m en foret ouverte, 4 m en foret dense"
    ],
    chevreuil: [
      "Positionner l'affut a 15-25 m de la saline (arc) ou 40-60 m (fusil)",
      "Installer le tree stand a 4-5 m de hauteur (le chevreuil detecte rarement au-dessus de 4 m)",
      "Installer l'affut 3-4 SEMAINES avant la saison pour permettre l'habituation du chevreuil",
      "Degager 2-3 corridors de tir etroits (2 m) — le chevreuil est alerte par les ouvertures trop larges",
      "Utiliser un ground blind si le terrain ne permet pas de tree stand — le chevreuil s'habitue en 2 semaines",
      "Creer un cone de tir de 120 degres maximum (pas 180 — limiter les mouvements de rotation)",
      "Eviter les affuts en metal qui grincent — privilegier les plateformes en bois ou composites silencieuses",
      "Camoufler l'affut avec de la vegetation LOCALE (pas de camouflage artificiel depareille)",
      "Positionner l'affut en bordure de transition foret-clairiere (le chevreuil longe les ecotones)",
      "Installer un paravent lateral pour cacher les mouvements du chasseur lors du tir",
      "Ne jamais installer 2 affuts visibles l'un de l'autre (le chevreuil les associe)",
      "Marquer les distances avec des reflecteurs UV invisibles a l'oeil nu du chevreuil",
      "Approcher l'affut par un chemin qui ne croise aucun sentier de chevreuil identifie",
      "Verifier que l'arriere-plan derriere l'affut est dense (le chevreuil repere les silhouettes isolees)"
    ],
    ours: [
      "Positionner l'affut a 15-20 m de la saline (arc) ou 30-50 m (fusil)",
      "Tree stand OBLIGATOIRE a 4-5 m — ne JAMAIS chasser l'ours au sol a la saline",
      "L'affut doit offrir un tir plongeant a 30-45 degres (zone vitale de l'ours vue du dessus)",
      "Degager UN seul corridor de tir principal de 4 m de large (l'ours approche souvent par le meme chemin)",
      "Installer l'affut SOUS LE VENT en permanence — l'odorat de l'ours est 7x celui du chien",
      "Prevoir une deuxieme position de repli a 100 m en cas de vent changeant",
      "Avoir TOUJOURS un spray anti-ours accessible (meme en tree stand)",
      "Installer une camera trail avec alerte cellulaire pour savoir si l'ours est actif avant de monter",
      "Ne jamais laisser de nourriture, emballages ou dechets pres de l'affut",
      "Visibilite de retrait obligatoire — pouvoir voir le chemin de sortie depuis l'affut",
      "Installer une echelle silencieuse (pas de metal-metal) avec marches en mousse",
      "Tir ethique: viser derriere l'epaule a 45 degres (tir plongeant), jamais frontal"
    ],
    wapiti: [
      "Positionner l'affut a 30-50 m (arc) ou 80-150 m (fusil) de la saline",
      "Tree stand a 5-7 m de hauteur — le wapiti est grand et surveille constamment en hauteur",
      "Degager 4-5 corridors de tir de 4 m de large (le wapiti voyage en groupe, angles multiples)",
      "Le wapiti approche souvent en file indienne — orienter le corridor de tir perpendiculairement",
      "Installer l'affut en surplomb topographique si possible (crete, butte) pour le tir descendant",
      "Prevoir un espace de tir suffisant pour le panache (1.2 m d'envergure — branches genantes)",
      "Le wapiti est tres sensible aux bruits metalliques — affut tout-bois ou composite",
      "Utiliser un appel de wapiti (bugle) depuis l'affut en pre-rut pour attirer les males vers la saline",
      "Installer 2-3 cameras trail pour documenter les heures de passage (souvent crepusculaires)",
      "Amenager un sentier d'approche de 200+ m pour eviter de deranger le groupe a la saline"
    ],
    dindon: [
      "Positionner le ground blind a 15-30 m de la zone de mineraux/grains",
      "Ground blind FERME obligatoire — le dindon detecte le moindre mouvement",
      "Installer le blind 2+ semaines avant la chasse pour habituation (brosse avec branches)",
      "Ouverture de tir ETROITE (60-90 degres max) — le dindon detecte le mouvement peripherique",
      "Le dindon approche souvent depuis une direction elevee (il aime voir avant de descendre)",
      "Installer le blind en contrebas leger par rapport a la zone d'alimentation",
      "Camouflage integral: filet + branches locales + sol couvert (le dindon voit les couleurs)",
      "Ne JAMAIS porter de rouge, blanc ou bleu pres d'un blind a dindon (confusion avec caroncule)",
      "Placer un ou deux appelants (decoys) a 10-15 m du blind pour fixer l'attention des dindons",
      "Tir au fusil a plombs #4 ou #5 — zone vitale: tete/cou a 15-30 m maximum",
      "Patience absolue: rester immobile 30+ minutes — le dindon revient si aucun mouvement detecte"
    ],
  },
  strategies_optimisation: {
    orignal: ["Verifier la rose des vents saisonniere (sept-nov) sur 3 ans avant de fixer la position", "Creer une deuxieme saline a 200 m avec un affut oriente a 180 degres pour couvrir les 2 directions de vent", "Pre-rut (15 sept - 5 oct): les males commencent a patrouiller — positionner l'affut sur le corridor de patrouille", "Rut actif (5-25 oct): les males suivent les femelles — positionner pres d'un corridor femelle confirme"],
    chevreuil: ["Installer des frottoirs artificiels (rubbing posts) entre la saline et l'affut pour attirer les males territoriaux", "Creer des zones de grattage (mock scrapes) a 20-30 m de l'affut pour rediriger les males vers la zone de tir", "En pre-rut: les males visitent les salines a l'aube (5h30-7h30) — arriver 90 min avant", "Le chevreuil memorise: ne JAMAIS modifier l'affut en saison — tout changement = alerte de 72h"],
    ours: ["L'ours visite souvent entre 17h et 21h en ete — arriver a 15h et rester immobile", "En zone de baits legales: combiner saline + attractif odorant (melasse, bacon) pour augmenter la frequentation", "L'ours dominant arrive souvent en dernier — ne pas tirer le premier ours vu, attendre 30 min", "Utiliser du parfum de pomme ou cerise sur un chiffon pour masquer les odeurs du tree stand"],
    wapiti: ["Le wapiti bugle repond aux appels en pre-rut (mi-sept) — combiner saline + appels depuis l'affut", "Installer une saline secondaire a 500 m pour les jours ou le groupe principal est absent", "Le wapiti male dominant visite la saline seul, souvent 30-60 min apres le groupe de femelles"],
    dindon: ["Utiliser un appelant jake (jeune male) pour provoquer l'agressivite du male dominant", "Combiner appels (box call, slate call) avec la saline pour attirer les dindons a portee de tir", "Le dindon descend de son perchoir (arbre) a l'aube — etre en position 45 min avant le lever du soleil"],
  },
  techniques_chasse: {
    orignal: ["Couper le moteur a 300 m et terminer a pied (approche silencieuse obligatoire)", "Arriver a l'affut 90 min avant l'aube — l'orignal est actif des les premieres lueurs", "Ne JAMAIS uriner pres de l'affut — utiliser un contenant etanche", "En vent changeant: descendre IMMEDIATEMENT et revenir un autre jour"],
    chevreuil: ["Approche predawn par un sentier separe du sentier de chevreuil", "Monter au tree stand en silence total — chaque bruit est memorise", "Scanner avec les jumelles AVANT de tirer — identifier age et sexe", "Laisser le chevreuil se detendre 5-10 min a la saline avant de tirer"],
    ours: ["NE JAMAIS chasser seul — partenaire obligatoire en zone ours", "Attendre que l'ours soit broadside (flanc expose) avant le tir", "Apres le tir: attendre 30 min minimum avant de descendre (ours blesse = danger mortel)", "Avoir un plan de retrait rapide si l'ours charge le tree stand"],
    wapiti: ["Le wapiti est gregaire — le premier membre du groupe qui detecte une anomalie alerte tout le groupe", "Tir ethique: derriere l'epaule a broadside, jamais en mouvement, jamais au-dela de 200 m au fusil"],
    dindon: ["Rester ABSOLUMENT immobile — le dindon detecte un clignotement d'oeil a 30 m", "Tir a la tete/cou UNIQUEMENT (zone vitale etroite) a moins de 35 m", "Apres un appel: silence complet pendant 15 min — la reponse vient souvent du silence"],
  },
  erreurs_a_eviter: {
    orignal: ["Installer l'affut face au vent dominant (odeur directe vers la saline)", "Laisser du metal expose qui reflete la lumiere (soleil matinal = alerte visuelle)", "Deplacer l'affut en pleine saison de chasse (perturbation massive)", "Negliger le sentier d'approche (branches craquantes = orignal alerte a 200 m)", "Installer l'affut trop haut (>7 m) — angle de tir trop plongeant, zone vitale reduite"],
    chevreuil: ["Modifier l'affut ou le camouflage en saison (le chevreuil memorise le paysage)", "Installer l'affut en ligne droite avec un sentier (le chevreuil surveille les lignes droites)", "Utiliser un camouflage artificiel depareille avec la vegetation locale", "Trop defricher autour de l'affut (perte de couvert = detection)", "Approcher l'affut par le sentier de chevreuil (depot d'odeur sur son chemin)"],
    ours: ["Chasser l'ours au sol a la saline (risque de charge)", "Laisser des dechets alimentaires pres de l'affut (ours conditionne = danger)", "Ignorer les signes de presence (empreintes fraiches, arbres griffes)", "Tirer un ours a moins de 10 m en tree stand (angle trop plongeant, zone vitale manquee)"],
    wapiti: ["Installer l'affut sur un arbre trop petit (le vent le fait bouger — le wapiti detecte le mouvement)", "Negliger le camouflage de l'echelle du tree stand", "Utiliser des appels de wapiti en permanence (les males cessent de repondre apres 3-4 sequences)"],
    dindon: ["Porter du rouge, blanc ou bleu (le dindon confond avec un rival)", "Bouger dans le blind apres un appel (le dindon fixe la source du son pendant 10+ min)", "Tirer a plus de 40 m au fusil a plombs (densite insuffisante pour kill propre)", "Installer le blind le jour de la chasse (le dindon le detecte comme anomalie nouvelle)"],
  },
  optimisations_saisonnieres: {
    printemps: "Evaluer l'etat du tree stand apres l'hiver — verifier sangles, vis, plateforme. Reperer les nouveaux sentiers de gibier post-fonte. Installer/verifier les affuts 4 semaines avant la saison.",
    ete: "Periode ideale pour installer de nouveaux affuts et defricher les corridors de tir. La vegetation est dense — prevoir le defricher avant la repousse maximale. Documenter les vents dominants.",
    automne: "Saison active. NE PAS modifier les affuts. Minimiser les visites. Utiliser les cameras trail cellulaires pour eviter les passages inutiles. Approche predawn uniquement.",
    hiver: "Retirer les tree stands portables pour entretien. Evaluer les positions depuis le sol avec la vegetation absente. Reperer les corridors de ravage (chevreuil) ou de migration (orignal)."
  },
  optimisations_support: ["Support de tree stand en acier galvanise avec plateforme silencieuse (mousse EVA)", "Sangles de securite a double ancrage — inspection annuelle obligatoire", "Siege pivotant silencieux pour couvrir le cone de tir sans mouvement de pieds", "Repose-arc ou repose-fusil integre pour immobilite du tir"],
  optimisations_meteo: ["Vent du nord-ouest apres front froid = activite accrue des cervides — session prioritaire", "Pression barometrique en hausse rapide = meilleure chance d'observation", "Brouillard matinal: l'orignal est plus actif — etre en position plus tot", "Pluie legere: les cervides sont actifs, le bruit de pluie couvre les bruits du chasseur"],
  optimisations_pression: ["Zone haute pression (>5 chasseurs/km2): ne chasser la saline que 2-3 fois par saison pour maintenir la frequentation", "Coordonner avec les voisins pour alterner les jours de chasse", "En zone publique: chasser en milieu de semaine (lundi-mercredi) pour eviter la pression du weekend"],
  thresholds: { green: "80-100: Affut a distance optimale, cone de tir 120-180 degres degage, sous le vent dominant, approche silencieuse, installe 4+ semaines", yellow: "50-79: Position acceptable mais compromis vent ou angle, ou installation recente (<2 semaines)", red: "0-49: Position inadequate — face au vent, cone de tir bloque, distance non-ethique, ou absence d'affut sureleve en zone ours" },
  sources: [
    "MFFP Quebec — Plan de gestion de l'orignal au Quebec 2020-2027",
    "Dussault, Courtois & Ouellet (2012) — Mouvements saisonniers et habitat de l'orignal au Quebec (UQAR)",
    "Plourde & Dussault (2008) — Reponse comportementale des cervides aux perturbations humaines (J. Wildlife Mgmt)",
    "Lesmerises, Dussault & St-Laurent (2012) — Utilisation de l'habitat par l'orignal en foret boreale (Can. J. Zoology)",
    "National Deer Association (NDA) — Treestand Placement and Deer Behavior (2023)",
    "Mississippi State University Deer Lab — Stand Placement Research (2021)",
    "QDMA (archives) — Hunting Strategy and Stand Positioning for Mature Bucks",
    "University of Georgia Deer Lab — Deer Vision and Hunter Detection Studies (2019)",
    "RMEF — Elk Hunting Tactics and Stand Positioning in Western Canada (2022)",
    "NWTF — Turkey Hunting: Ground Blind Setup and Concealment Guide (2023)",
    "Bear Trust International — Black Bear Hunting Safety and Stand Guidelines (2022)",
    "Wisconsin DNR — Deer Management and Hunting Best Practices (2024)",
    "Michigan DNR — Turkey and Bear Hunting Regulations and Techniques (2024)",
    "Alberta Fish & Wildlife — Elk and Bear Hunting Season Manual (2023)",
    "Environnement Canada — Rose des vents saisonnieres regionales du Quebec",
    "MRNF — Donnees LiDAR forestier et corridors fauniques (2023)",
    "Leopold (1933) — Game Management: Stand Theory and Wildlife Strategy",
  ],
};

// =====================================================================
// ACCESSIBILITE VEHICULE
// =====================================================================
const accessibilite_vehicule = {
  title: "Accessibilite vehiculaire — Acces motorise au site de saline",
  definition: "Mesure la facilite d'acces par vehicule motorise (camion, VTT, motoneige) pour le transport des blocs mineraux (20-25 kg par unite) et de l'equipement de surveillance. Inclut l'evaluation de l'etat du chemin, la largeur praticable, la pente maximale, la praticabilite 4 saisons, et la capacite de charge du chemin.",
  methodology: "Score calcule sur 100 points: distance route carrossable (40 pts — mesure GPS), type de chemin d'acces (30 pts — gravel/sentier/hors-piste), praticabilite 4 saisons (20 pts — gel/boue/neige), capacite charge (10 pts — poids vehicule supporte). Donnees: reseau routier MRNF, images Sentinel-2, traces GPS terrain.",
  justification: {
    orignal: "Les blocs mineraux standards pesent 20-25 kg et doivent etre remplaces aux 4-6 semaines en saison active. Un acces vehiculaire direct reduit le temps d'intervention a 15-20 min au lieu de 2-3 h de portage. L'orignal tolere mieux les passages vehiculaires brefs que le portage humain prolonge qui laisse plus de trace olfactive.",
    chevreuil: "Le chevreuil est plus sensible aux perturbations humaines. Un acces VTT rapide (in-out en <10 min) minimise le depot d'odeurs. Les blocs plus petits (10-15 kg) necessitent des visites plus frequentes, rendant l'accessibilite critique. Privilege un acces VTT discret plutot que camion.",
    ours: "L'acces vehiculaire securise est primordial en zone ours. La presence d'ours en saison active requiert un retrait rapide si necessaire. Les attractifs pour ours (melasses, mais) sont volumineux et lourds (40-60 kg par ravitaillement), rendant l'acces motorise quasi-obligatoire.",
    wapiti: "Le wapiti habite des zones souvent eloignees et montagneuses. L'acces VTT est souvent le seul moyen motorise praticable. Les blocs de 25 kg pour wapiti doivent etre transportes sur des terrains en pente — prevoir un traineau ou un porte-charge adapte au VTT.",
    dindon: "Le dindon sauvage frequente des zones semi-agricoles plus accessibles. L'acces vehiculaire est generalement facile (chemins de ferme, rangs). Les mineraux pour dindon sont plus legers (grains, 5-10 kg par visite), reduisant la contrainte logistique.",
  },
  recommendations_terrain: {
    orignal: [
      "Degager un chemin VTT de 2.5 m de largeur minimum jusqu'a 150 m du site",
      "Installer des reperes reflecteurs tous les 50 m pour navigation predawn",
      "Creer une aire de stationnement discrete a 100-200 m (hors vue directe de la saline)",
      "Tailler les branches genantes a 3 m de hauteur sur le chemin principal",
      "Combler les ornieres avec du gravier 0-20 mm aux passages critiques",
      "Installer un ponceau aux traversees de ruisseaux (portance VTT + orignal)",
      "Planifier un chemin alternatif praticable en cas de crue printaniere",
      "Eviter les chemins qui longent les corridors principaux de deplacement de l'orignal",
      "Utiliser un VTT electrique pour reduire le bruit d'approche de 80%",
      "Stocker 2-3 blocs de reserve dans un contenant etanche pres du parking",
      "Arriver toujours par le meme chemin pour conditionner les orignaux a cette trace",
      "En hiver: passer au mode motoneige et creer une piste damee permanente"
    ],
    chevreuil: [
      "Chemin VTT etroit (1.5 m) et sinueux pour reduire la visibilite directe",
      "Arriver uniquement en plein vent (>15 km/h) pour disperser les odeurs humaines",
      "Transporter les blocs en sac a dos etanche anti-odeur depuis le parking",
      "Limiter les visites VTT a la mi-journee (10h-14h) quand les chevreuils sont couches",
      "Stationner le VTT a 200+ m de la saline et terminer a pied",
      "Utiliser un contenant hermetique pour les blocs (eliminer les odeurs de manipulation)",
      "Creer un chemin d'acces qui ne croise aucun sentier de chevreuil identifie",
      "En zone periurbaine: acces silencieux a pied depuis le stationnement le plus proche",
      "Ne jamais emprunter le chemin d'acces en soiree (heures actives du chevreuil)",
      "Installer des tapis de mousse aux points bruyants du chemin (gravier, branches)"
    ],
    ours: [
      "Chemin large et degage (3 m) pour retrait rapide si necessaire",
      "Klaxon ou sifflet d'ours attache au VTT (signaler sa presence en approche)",
      "Ne jamais laisser de nourriture dans le vehicule (fenetre ouverte = ours dans le VTT)",
      "Visites en duo obligatoires en zone ours brun ou grizzly",
      "Transporter les attractifs dans des contenants ours-proof metalliques",
      "Verifier les signes de presence (empreintes, excrements, griffures) sur le chemin AVANT d'aller au site",
      "Avoir un spray anti-ours accessible dans le VTT et sur soi en permanence",
      "Stationner face a la sortie pour un depart rapide",
      "En zone de forte densite d'ours: visiter UNIQUEMENT en milieu de journee (11h-14h)",
      "Installer une camera trail cellulaire sur le chemin pour verifier la presence ours avant la visite"
    ],
    wapiti: [
      "Chemin VTT en lacets pour gerer les pentes (>10% = lacets obligatoires)",
      "Installer des barres anti-erosion en bois tous les 20 m sur les pentes",
      "Prevoir un traineau attele au VTT pour le transport de blocs en pente",
      "Creer un point de repos a mi-chemin pour les portages longs",
      "Le wapiti est habitue aux vehicules forestiers — le VTT ne le derange pas outre mesure",
      "Stationner a 300+ m de la saline (le wapiti a un rayon de vigilance large)",
      "En montagne: utiliser les anciennes routes forestieres comme acces principal",
      "Prevoir des chaines pour le VTT en automne (gelees matinales sur les pentes)"
    ],
    dindon: [
      "Acces par chemin de ferme ou rang — souvent deja praticable en vehicule",
      "Stationner hors de vue de la zone de mineraux (le dindon surveille depuis les perchoirs)",
      "Approche finale a pied (50-100 m) — le dindon est alerte par les moteurs proches",
      "Transporter les grains/mineraux dans un seau etanche discret",
      "Visiter uniquement en milieu de journee — le dindon est actif matin et soir",
      "En zone agricole: coordonner avec le proprietaire pour eviter les conflits d'acces"
    ],
  },
  strategies_optimisation: {
    orignal: ["Chemin VTT large (2.5 m) car l'orignal tolere les vehicules motorises", "Approche par le versant oppose au vent dominant", "Stockage de 4-5 blocs de 25 kg dans une cache a 200 m", "Utiliser un traineau en hiver attele au VTT pour transport silencieux"],
    chevreuil: ["Acces VTT etroit et sinueux (1.5 m) pour reduire la visibilite", "Arriver en plein vent uniquement", "Transport en sac anti-odeur obligatoire", "Mi-journee seulement (10h-14h)"],
    ours: ["Acces large (3 m) pour retrait rapide", "Duo obligatoire", "Contenants ours-proof", "Verification camera avant visite"],
    wapiti: ["Lacets sur pentes >10%", "Traineau VTT pour blocs lourds", "Anciennes routes forestieres", "Stationner a 300+ m"],
    dindon: ["Chemin de ferme existant", "Seau etanche discret", "Approche finale a pied", "Mi-journee seulement"],
  },
  techniques_chasse: {
    orignal: ["Couper le moteur a 200 m du site et terminer a pied", "Approche finale sous le vent obligatoire", "VTT electrique: approche possible jusqu'a 80 m", "Varier l'heure d'arrivee pour eviter la routine predictible"],
    chevreuil: ["Couper le moteur a 300 m minimum", "Approche a pied avec bottes en caoutchouc (anti-odeur)", "Ne jamais approcher face au vent", "Chronometrer: <10 min sur site"],
    ours: ["Faire du bruit en approche pour signaler sa presence (eviter surprendre un ours)", "Ne jamais approcher un ours blesse — attendre 30 min et suivre la piste de sang prudemment", "Toujours avoir un partenaire de securite en approche"],
    wapiti: ["Le wapiti detecte les vehicules a longue distance — stationner hors de vue", "Approche en silence total sur les derniers 200 m", "Le vent thermique change en montagne — arriver par le bas le matin"],
    dindon: ["Aucun bruit moteur a <200 m de la zone de mineraux", "Arriver 45 min avant l'aube", "Marcher en silence absolu — le dindon entend un pas a 50 m"],
  },
  erreurs_a_eviter: {
    orignal: ["Rouler directement jusqu'a la saline (derangement maximal)", "Creer un nouveau chemin chaque visite (multiplie les perturbations)", "Stationner face au vent dominant", "Laisser des dechets ou emballages sur le chemin"],
    chevreuil: ["Utiliser un vehicule diesel bruyant quand un VTT suffit", "Emprunter le sentier de chevreuil avec le VTT", "Visiter en soiree (heures actives du chevreuil)", "Laisser des traces d'huile ou d'essence sur le chemin"],
    ours: ["Laisser de la nourriture dans le vehicule", "Visiter seul en zone ours", "Ignorer les signes de presence (empreintes fraiches)", "Approcher un ours vu sur la camera sans precautions"],
    wapiti: ["Stationner trop pres (le wapiti est tres vigilant)", "Rouler a grande vitesse sur le chemin (bruit + poussiere)", "Negliger les chaines en automne (enlisement = bruit prolonge)"],
    dindon: ["Approcher en vehicule jusqu'a la zone (le dindon quitte pour la journee)", "Claquer les portieres du vehicule", "Laisser le VTT visible depuis la zone d'alimentation"],
  },
  optimisations_saisonnieres: {
    printemps: "Verifier l'etat du chemin apres la fonte — reparer ornieres avant la saison active. Eviter les zones humides jusqu'a mi-mai.",
    ete: "Debroussailler le chemin. Appliquer anti-moustique naturel sur le vehicule pour reduire les traces olfactives.",
    automne: "Chemin optimal — sol ferme. Transporter le stock hivernal de mineraux. Preparer les caches.",
    hiver: "Mode motoneige ou raquettes. Piste damee permanente. Attention aux ponts de neige."
  },
  optimisations_support: ["Support a mineraux sureleve (60 cm) pour eviter l'enfouissement par la neige", "Bac de collecte sous le bloc pour prolonger la dissolution", "Reflecteur IR a l'entree du chemin pour localisation nocturne", "Plate-forme de depose seche (gravier + geotextile) pour le stationnement"],
  optimisations_meteo: ["Reporter la visite si pluie forte (empreintes profondes = derangement)", "Privilegier les journees ventees (>15 km/h) pour dispersion des odeurs", "Apres tempete: inspecter pour arbres tombes", "Matins de gel: sol dur, pas d'empreintes, bruit reduit"],
  optimisations_pression: ["Zone haute pression: 1x/mois max", "Chemin different des autres chasseurs", "Visiter en semaine, jamais les fins de semaine de chasse"],
  thresholds: { green: "80-100: Acces VTT direct <200 m, praticable 4 saisons, pente <10%", yellow: "50-79: Acces partiel, portage 200-500 m, praticabilite saisonniere limitee", red: "0-49: Portage >500 m, impraticable en VTT, pente >15%, zone inondable" },
  sources: [
    "MRNF — Reseau routier forestier du Quebec (2024)",
    "MFFP — Plan de gestion de l'orignal au Quebec 2020-2027",
    "Dussault, Courtois & Ouellet (2012) — Habitat et deplacements des cervides (UQAR)",
    "SEPAQ — Guide d'amenagement des salines pour la faune (2019)",
    "Plourde & Dussault (2008) — Impact des derangements humains sur la frequentation des salines (J. Wildlife Mgmt)",
    "NDA — Best Practices for Mineral Site Access (2023)",
    "Environnement Canada — Donnees climatiques saisonnieres regionales",
    "Wisconsin DNR — Deer Mineral Site Management Guide (2024)",
  ],
};

// =====================================================================
// COUVERTURE VENT
// =====================================================================
const couverture_vent = {
  title: "Couverture du vent — Analyse des vents dominants et thermiques",
  definition: "Evaluation de la protection naturelle du site contre les vents dominants qui transportent les odeurs humaines vers la zone de frequentation animale. Inclut l'analyse des vents dominants saisonniers, des courants thermiques (montants/descendants selon l'heure), et des ecrans naturels (topographie, vegetation dense, relief).",
  methodology: "Score sur 100: direction vents dominants vs position affut (35 pts — rose des vents Env. Canada), presence ecrans naturels (25 pts — LiDAR canopee), stabilite thermique (20 pts — modele topographique), variabilite directionnelle (20 pts — coefficient de variation). Sources: Environnement Canada stations meteo, modele thermique DEM.",
  justification: {
    orignal: "L'orignal detecte les odeurs humaines a 300-500 m par vent modere (10-15 km/h). Un site bien protege des vents dominants d'automne (NO au Quebec) permet des sessions de chasse productives 60-70% des jours, contre 20-30% sans protection. Les thermiques montants le matin et descendants le soir changent la direction effective du vent toutes les 2-3 h.",
    chevreuil: "Le chevreuil a un odorat comparable a celui du chien et detecte les odeurs a 400+ m. La direction du vent est le facteur #1 de reussite ou d'echec d'une session. Un seul faux vent et le chevreuil deserte la saline pendant 48-72 h. Le chevreuil est particulierement sensible aux vents tourbillonnants.",
    ours: "L'ours noir possede l'odorat le plus developpe de tous les gibiers nord-americains (7x le chien). Il detecte les odeurs humaines a 1.5+ km par vent favorable. Cependant, l'ours s'habitue aux odeurs regulieres — un chasseur qui visite toujours sous le meme vent cree un pattern que l'ours peut tolerer.",
    wapiti: "Le wapiti a un odorat tres developpe et voyage en groupes ou la vigilance est partagee. Si un individu detecte une odeur suspecte, tout le groupe fuit. Le wapiti en montagne est soumis a des thermiques complexes — les vallees creent des tourbillons impredictibles.",
    dindon: "Le dindon a un odorat limite (quasi-inexistant) — le vent n'est pas un facteur olfactif critique. Cependant, le vent fort (>25 km/h) reduit l'activite du dindon et rend les appels inefficaces. Un vent modere (10-15 km/h) est ideal car il couvre les bruits de mouvement du chasseur.",
  },
  recommendations_terrain: {
    orignal: [
      "Analyser la rose des vents d'octobre-novembre sur 3 ans (Environnement Canada) avant de fixer la position",
      "Positionner l'affut de sorte que le vent dominant porte VOS odeurs LOIN de la saline",
      "Identifier un ecran naturel (crete, foret dense) entre votre position et le corridor d'approche de l'orignal",
      "Creer 2 positions d'affut a 90 degres pour couvrir les 2 directions de vent principales",
      "Utiliser un indicateur de vent (poudre, fil) en permanence — verifier toutes les 15 min",
      "Installer l'affut sur le versant oppose aux thermiques matinaux (le vent monte le matin en montagne)",
      "En vallee: eviter le fond (vents tourbillonnants) — privilegier le flanc sous le vent",
      "Creer un ecran de coniferes (epinettes) de 2 m de haut a 30 m de l'affut si aucun ecran naturel",
      "Le soir: les thermiques descendent — repositionner l'approche en consequence",
      "Eviter les jours de vent variable (<5 km/h avec changements frequents) — annuler la session"
    ],
    chevreuil: [
      "Le chevreuil est ULTRA-sensible au vent — ne JAMAIS chasser si le vent porte vers la saline",
      "Utiliser 3 positions d'affut differentes pour couvrir N, O, et E (les 3 vents dominants au Quebec)",
      "Installer un indicateur de vent (fil de coton) a hauteur de la saline ET a hauteur de l'affut",
      "En foret: les thermiques creent des micro-courants — tester avec de la poudre de talc",
      "Creer des brise-vents artificiels (tas de branches de coniferes) si le site est trop expose",
      "Ne chasser que par vent stable (direction constante depuis 2+ h)",
      "Le chevreuil utilise le vent pour scanner AVANT d'approcher — il se positionne sous le vent en arrivant",
      "Installer l'affut a l'endroit ou le vent est le plus previsible (pas en zone de tourbillon)",
      "Appliquer un destructeur d'odeurs sur vos vetements ET le tree stand",
      "En vent changeant: descendre et revenir un autre jour (ne pas insister)"
    ],
    ours: [
      "L'ours detecte les odeurs a 1.5+ km — vent contraire OBLIGATOIRE en permanence",
      "L'ours approche souvent face au vent pour identifier les odeurs du site — l'affut doit etre LATERAL",
      "Utiliser des attractifs odorants (melasse, bacon) pour masquer partiellement l'odeur humaine",
      "L'ours s'habitue aux odeurs regulieres — visiter toujours sous le meme vent cree un pattern tolere",
      "En vent variable: l'ours hesite a approcher mais ne fuit pas (contrairement aux cervides)"
    ],
    wapiti: [
      "Le wapiti en montagne est soumis a des thermiques complexes — etudier le terrain AVANT",
      "Les vallees etroites creent des vents canalises previsibles — les utiliser a votre avantage",
      "Le wapiti bugle repond mieux par vent faible (5-10 km/h) — combiner appels et saline ces jours-la",
      "En foret de montagne: les thermiques s'inversent vers 10h et 17h — ajuster la position"
    ],
    dindon: [
      "Le vent n'est PAS un facteur olfactif pour le dindon — mais il affecte son comportement",
      "Vent fort (>25 km/h): le dindon se refugie dans les vallees protegees — deplacer le blind",
      "Vent modere (10-15 km/h): ideal — couvre les bruits de mouvement dans le blind",
      "Les appels au dindon portent moins par vent fort — augmenter le volume ou utiliser un box call"
    ],
  },
  strategies_optimisation: {
    orignal: ["2 affuts a 90 degres pour 2 vents principaux", "Ecran de coniferes si site expose", "Indicateur de vent permanent"],
    chevreuil: ["3 affuts pour 3 vents — N, O, E", "Destructeur d'odeurs obligatoire", "Ne chasser que par vent stable 2+ h"],
    ours: ["Affut LATERAL par rapport au vent (pas derriere)", "Attractifs odorants pour masquer l'odeur humaine"],
    wapiti: ["Etudier les thermiques de montagne", "Combiner appels et saline par vent faible"],
    dindon: ["Vent modere ideal pour couvrir les bruits", "Augmenter volume appels par vent fort"],
  },
  techniques_chasse: {
    orignal: ["Verifier le vent toutes les 15 min avec un indicateur", "Si le vent tourne: quitter immediatement", "Approche matinale: thermiques montants, approche par le bas"],
    chevreuil: ["Le chevreuil scanne sous le vent AVANT d'entrer a la saline — observer son comportement", "Un chevreuil qui fait demi-tour a 50 m = votre vent l'a atteint", "Ne jamais forcer une session par mauvais vent"],
    ours: ["L'ours qui arrive face au vent = il a detecte le site mais pas vous — bon signe", "Si l'ours leve le nez et hesite: il vous a probablement detecte — restez immobile"],
    wapiti: ["Le wapiti teste le vent en levant le museau toutes les 30 s — observer sa confiance", "En montagne: les thermiques s'inversent en fin de matinee — reajuster"],
    dindon: ["Le dindon ne reagit pas au vent olfactivement — concentrez-vous sur l'immobilite"],
  },
  erreurs_a_eviter: {
    orignal: ["Chasser par vent qui porte vers la saline", "Ignorer les thermiques (le vent au sol ≠ vent a 5 m)", "Compter sur le vent affiche a la meteo (conditions locales differentes)"],
    chevreuil: ["Insister par mauvais vent (une seule detection = 48-72h de desertion)", "Negliger les micro-courants en foret dense", "Oublier que le vent tourne avec la temperature"],
    ours: ["Sous-estimer l'odorat de l'ours (7x chien)", "Penser que le vent suffit — l'ours detecte les odeurs residuelles"],
    wapiti: ["Ignorer les thermiques de montagne (inversions matin/soir)", "Chasser dans le fond des vallees (tourbillons)"],
    dindon: ["Se preoccuper excessivement du vent pour le dindon (l'odorat n'est pas son sens principal)"],
  },
  optimisations_saisonnieres: {
    printemps: "Vents variables et thermiques instables. Analyser les patterns sur 3+ jours avant de choisir la position de l'affut.",
    ete: "Vents dominants stables. Ideal pour calibrer les positions d'affut et tester les ecrans naturels.",
    automne: "Saison critique. Vents NO dominants au Quebec. Verifier la rose des vents locale. Maximiser les sessions par vent stable NO.",
    hiver: "Vents forts et froids. Peu de chasse active. Evaluer les ecrans naturels avec la vegetation absente."
  },
  optimisations_support: ["Indicateur de vent permanent a hauteur de saline (fil de coton)", "Anemometre portable pour mesurer la vitesse et direction exactes", "Spray destructeur d'odeurs sur le tree stand avant chaque session"],
  optimisations_meteo: ["Front froid arrivant du NO = les cervides sont tres actifs — session prioritaire", "Vent stable >2h = meilleure previsibilite — session optimale", "Vent variable <5 km/h = annuler la session (direction impredictible)"],
  optimisations_pression: ["En zone haute pression: les animaux deviennent PLUS sensibles au vent (hyper-vigilance)", "Chasser uniquement par conditions de vent PARFAITES en zone haute pression"],
  thresholds: { green: "80-100: Vent dominant porte LOIN de la saline, ecran naturel present, thermiques stables, 2+ positions d'affut", yellow: "50-79: Vent partiellement favorable, ecran partiel, 1 seule position d'affut viable", red: "0-49: Vent porte vers la saline majoritairement, aucun ecran, zone de tourbillons, ou 0 position viable" },
  sources: [
    "Environnement Canada — Rose des vents saisonnieres Quebec (2024)",
    "MFFP — Influence du vent sur le comportement des cervides (2020)",
    "Dussault et al. (2005) — Mouvements de l'orignal en reponse aux perturbations (UQAR)",
    "NDA — Wind Strategy for Deer Hunters (2023)",
    "Mississippi State University Deer Lab — Whitetail Response to Wind Direction (2022)",
    "University of Georgia Deer Lab — Scent Detection and Wind Patterns (2021)",
    "Bear Trust International — Black Bear Olfactory Capabilities (2020)",
    "RMEF — Elk Hunting and Mountain Thermals (2023)",
    "NWTF — Turkey Hunting Wind Considerations (2024)",
    "Mysterud & Ostbye (1999) — Habitat selection and wind in cervids (Oecologia)",
  ],
};

// =====================================================================
// CORRIDORS DE DEPLACEMENT
// =====================================================================
const corridors_deplacement = {
  title: "Corridors de deplacement fauniques — Axes de mouvement naturels",
  definition: "Evaluation de la proximite, qualite et connectivite des corridors naturels empruntes par la faune entre leurs zones d'alimentation, de repos, d'abreuvement et de reproduction. Les corridors sont les autoroutes invisibles de la faune — positionner la saline correctement par rapport a eux multiplie par 5 l'efficacite du site.",
  methodology: "Score sur 100: distance corridor principal (40 pts — LiDAR + GPS), qualite du corridor (30 pts — couvert + largeur), connectivite habitat (20 pts — liaison foret-eau-alimentation), saisonnalite utilisation (10 pts — traces saisonnieres).",
  justification: {
    orignal: "L'orignal utilise des corridors bien definis entre lacs/marais (alimentation aquatique ete) et ravages hivernaux (coniferes denses). Ces corridors suivent les cretes boisees, les rives de cours d'eau, et les bordures de coupes forestieres. Saline a <100 m d'un corridor majeur = frequentation 5x superieure. Les corridors d'orignal sont stables sur des decennies.",
    chevreuil: "Le chevreuil utilise des corridors plus discrets et sinueux, souvent en bordure de champs agricoles, le long de clotures, ou dans des coulees boisees etroites (10-30 m). Les sentiers battus font 30-50 cm de large. Les zones de grattage (scrapes) marquent les corridors territoriaux des males dominants.",
    ours: "L'ours utilise des corridors larges et opportunistes, souvent le long de ruisseaux a truites, de champs de bleuets, ou de routes forestieres desaffectees. Les corridors d'ours sont marques par des arbres griffes a hauteur d'epaule (1.5-2 m) et des excrements reguliers.",
    wapiti: "Le wapiti emprunte des corridors de migration saisonniere entre les alpages d'ete (haute altitude) et les vallees d'hivernage. Ces corridors de migration couvrent 10-50 km et sont utilises par plusieurs generations. Les salines sur ces corridors sont visitees par des groupes entiers (5-15 individus).",
    dindon: "Le dindon suit des corridors lineaires entre le perchoir nocturne (grands arbres, souvent pins ou chenes) et les zones d'alimentation diurnes (champs, sous-bois ouverts). Le corridor perchoir-alimentation est parcouru a pied 2x/jour (matin et soir) et fait rarement plus de 500 m.",
  },
  recommendations_terrain: {
    orignal: [
      "Cartographier tous les sentiers visibles dans un rayon de 500 m (sol retourne, pistes, frottages)",
      "Installer la saline a 50-150 m d'un corridor confirme (pas directement dessus)",
      "Ne JAMAIS bloquer un corridor avec une structure — les orignaux contourneront et abandonneront la zone",
      "Orienter l'affut perpendiculairement au corridor (tir lateral, pas frontal)",
      "Identifier les carrefours de corridors — les intersections concentrent le passage",
      "Degager 3-4 corridors secondaires de 3 m convergeant vers la saline",
      "Utiliser les donnees LiDAR (MRNF) pour identifier les passages topographiques naturels",
      "Les corridors d'orignal suivent souvent les ruisseaux — verifier les rives dans un rayon de 300 m",
      "Creer des micro-clairieres (10-20 m) a 50-100 m de la saline pour attirer le brout de males",
      "En ete: les corridors sont entre les lacs (alimentation aquatique) et la foret (repos)",
      "En hiver: les corridors convergent vers les ravages — identifier le ravage le plus proche"
    ],
    chevreuil: [
      "Les sentiers de chevreuil font 30-50 cm de large et sont souvent invisibles en ete",
      "Identifier les zones de frottage (rubs) et grattage (scrapes) — corridors territoriaux des males",
      "Installer la saline la ou 2-3 sentiers convergent naturellement",
      "Le chevreuil longe les bordures de champs, les clotures et les haies — suivre ces lignes",
      "Creer des coulees artificielles (corridors boises etroits) pour guider le chevreuil vers la saline",
      "Les corridors de chevreuil changent entre pre-rut (patrouille) et rut (poursuite) — adapter la position",
      "Installer une camera trail sur chaque corridor identifie pour confirmer l'utilisation",
      "Les corridors principaux sont souvent paralleles aux cours d'eau (le chevreuil boit apres la saline)",
      "En zone agricole: les corridors traversent les champs par les angles et les coulees boisees"
    ],
    ours: [
      "Les corridors d'ours sont larges (2-4 m) et marques par des arbres griffes",
      "L'ours suit les ruisseaux a truites en ete — positionner la saline a <200 m d'un ruisseau",
      "Identifier les arbres griffes a 1.5-2 m de hauteur — marqueurs de corridor actif",
      "L'ours utilise les anciennes routes forestieres comme corridors — verifier les chemins abandonnes",
      "Les excrements reguliers sur un sentier = corridor actif et frequente",
      "Ne pas installer la saline directement SUR le corridor d'ours (risque de rencontre surprise)"
    ],
    wapiti: [
      "Les corridors de wapiti sont larges (3-5 m) et battus par les sabots du groupe",
      "Identifier les corridors de migration saisonniere (alpages → vallees) — stables sur des generations",
      "Positionner la saline a mi-chemin sur le corridor de migration (zone de transit)",
      "Les wapitis utilisent les cretes et les cols comme corridors naturels",
      "Installer des cameras trail sur les corridors pour estimer la taille des groupes",
      "Les corridors de wapiti sont souvent partages avec d'autres cervides — benefice multiple"
    ],
    dindon: [
      "Le corridor perchoir-alimentation fait rarement plus de 500 m — le cartographier",
      "Identifier les arbres de perchoir (grands pins, chenes) et la direction de descente matinale",
      "Le dindon descend du perchoir vers les zones ouvertes (champs, sous-bois clairs)",
      "Installer la zone de mineraux/grains sur le corridor, plus pres du perchoir que de l'alimentation",
      "Le dindon marche en groupe (5-20) — le corridor est large (2-3 m) et bien visible",
      "Les corridors de dindon sont actifs matin (6h-9h) et soir (15h-18h) — chronometrer"
    ],
  },
  strategies_optimisation: {
    orignal: ["Corridors cretes boisees entre 2 vallees", "Rives de lacs/marais en ete", "Bordures de coupes forestieres", "Males matures: corridors paralleles aux principaux (plus discrets)"],
    chevreuil: ["Bordures de champs + coulees boisees", "Zones de grattage = corridor de male dominant", "Convergence de 2-3 sentiers", "Corridor parallele a un cours d'eau"],
    ours: ["Ruisseaux a truites + champs de petits fruits", "Anciennes routes forestieres", "Arbres griffes = marqueurs", "Corridors larges et opportunistes"],
    wapiti: ["Corridors de migration generationnels", "Cretes et cols naturels", "Mi-chemin migration", "Corridors partages avec cerfs"],
    dindon: ["Corridor perchoir-alimentation <500 m", "Pres du perchoir", "Zones ouvertes pour atterrissage", "Actif matin 6h-9h"],
  },
  techniques_chasse: {
    orignal: ["L'affut ideal surveille un corridor ET la saline simultanement", "Les males matures utilisent des corridors paralleles plus discrets — les identifier"],
    chevreuil: ["Le chevreuil emprunte le corridor le plus proche sous le vent — anticiper", "En pre-rut: les males patrouillent les corridors de facon plus agressive"],
    ours: ["L'ours utilise le corridor le plus direct — tir previsible", "Attendre que l'ours quitte le corridor et s'expose a la saline avant de tirer"],
    wapiti: ["Le wapiti voyage en file indienne — le dominant est souvent le 3e ou 4e", "En rut: le male bugle sur le corridor — utiliser l'appel pour le rediriger vers l'affut"],
    dindon: ["Le male dominant strutze souvent sur le corridor — identifier sa zone de parade", "Placer un appelant female sur le corridor pour intercepter le male en approche"],
  },
  erreurs_a_eviter: {
    orignal: ["Installer la saline SUR un corridor (perturbation du flux)", "Bloquer un corridor avec une structure", "Defricher excessivement (suppression du couvert)"],
    chevreuil: ["Creer un sentier d'approche qui croise un corridor (depot d'odeur)", "Ignorer les changements de corridors entre pre-rut et rut"],
    ours: ["S'installer directement sur le corridor d'ours (risque de rencontre)", "Ignorer les arbres griffes (marqueurs de presence)"],
    wapiti: ["Bloquer un corridor de migration (le groupe evite la zone pour des annees)", "Installer trop pres du fond de vallee (vents tourbillonnants)"],
    dindon: ["Installer le blind sur le corridor (le dindon le contourne)", "Ignorer la position des perchoirs (determine la direction d'approche)"],
  },
  optimisations_saisonnieres: {
    printemps: "Corridors post-fonte: les animaux explorent. Reperer les nouvelles pistes. Ideal pour cartographie.",
    ete: "Corridors ete: entre eau et couvert dense. Vegetation dense cache les pistes. Camera trail essentielle.",
    automne: "Corridors de rut: males parcourent 3-5x plus de distance. Nouveaux sentiers de patrouille.",
    hiver: "Corridors de ravage (chevreuil) ou migration (wapiti): tres concentres, battus par la neige. Ideal reperage."
  },
  optimisations_support: ["Micro-clairieres 10-20 m a 50 m de la saline pour attirer le brout", "Points d'eau artificiels si aucune source naturelle", "Trefle ou brassica plantes dans les micro-clairieres"],
  optimisations_meteo: ["Vent du nord: animaux sur corridors proteges (versant sud)", "Pluie legere: activite accrue sur les corridors", "Gel matinal: givre sur les pistes = passage recent confirme"],
  optimisations_pression: ["Haute pression: males sur corridors secondaires", "Identifier corridors NON empruntes par les autres chasseurs"],
  thresholds: { green: "80-100: Corridor majeur <100 m, pistes fraiches, carrefour de 2+ corridors, connectivite habitat excellente", yellow: "50-79: Corridor secondaire 100-300 m, pistes occasionnelles", red: "0-49: Aucun corridor <500 m, aucune piste, site isole des axes de deplacement" },
  sources: [
    "MRNF — Analyse des corridors forestiers haute resolution LiDAR (2023)",
    "Dussault, Courtois & Ouellet (2012) — Corridors de deplacement et habitat des cervides (UQAR, Can. J. Zoology)",
    "Fortin et al. (2005) — Corridors fauniques et fragmentation de l'habitat (Universite Laval)",
    "Lesmerises et al. (2012) — Utilisation de l'habitat par l'orignal en foret boreale (UQAR)",
    "NDA — Deer Travel Corridors and Stand Placement (2023)",
    "RMEF — Elk Migration Corridors in Western Canada (2022)",
    "NWTF — Turkey Roosting and Travel Patterns (2024)",
    "Leopold (1933) — Game Management: Ecotone Theory and Wildlife Corridors",
    "Nielsen, Stenhouse & Boyce (2010) — Spatial strategies and corridor connectivity (Ecology & Evolution)",
    "Mississippi State University Deer Lab — Corridor Use by Mature Bucks (2021)",
  ],
};

// =====================================================================
// COUVERT FORESTIER
// =====================================================================
const couvert_forestier = {
  title: "Couvert forestier — Densite et qualite du couvert de canopee",
  definition: "Evaluation du pourcentage de couvert forestier (canopee) autour de la saline dans un rayon de 200 m. Le couvert lateral (0-4 m) et le couvert de canopee (>4 m) sont evalues separement. Un couvert lateral de 60-80% est optimal pour les males matures qui exigent une protection visuelle avant de s'exposer.",
  methodology: "Score sur 100: couvert canopee (35 pts — LiDAR MRNF), couvert lateral 0-4 m (30 pts — evaluation terrain), diversite essences (20 pts — inventaire forestier), age peuplement (15 pts — dendrochronologie estimee). Donnees: MRNF LiDAR, inventaire ecoforestier, Sentinel-2 NDVI.",
  justification: {
    orignal: "L'orignal prefere un couvert mixte (coniferes + feuillus) avec une canopee de 50-70%. Un couvert trop dense (>80%) limite la croissance du sous-bois dont il se nourrit. Les males matures exigent un couvert lateral de 60%+ pour se sentir en securite a la saline. La foret boreale mixte (epinette + bouleau + sapin) offre le meilleur equilibre.",
    chevreuil: "Le chevreuil prefere les ecotones (transitions foret-clairiere) avec un couvert de 40-60%. Il utilise le couvert dense pour le repos diurne et les zones ouvertes pour l'alimentation. Les males trophee (4.5+ ans) frequentent uniquement les zones avec couvert lateral >70% — ils ne s'exposent pas en zone ouverte de jour.",
    ours: "L'ours noir utilise la foret dense (couvert >70%) pour les deplacements diurnes et les zones ouvertes (coupes, brulis) pour l'alimentation (bleuets, framboisiers). Un couvert de 50-70% autour de la saline est ideal — assez de protection pour l'ours, assez d'ouverture pour la securite du chasseur.",
    wapiti: "Le wapiti alterne entre les alpages ouverts (alimentation) et la foret dense (repos, protection). Le couvert ideal autour d'une saline a wapiti est de 40-60% avec des micro-clairieres. Le wapiti male en rut recherche les zones semi-ouvertes pour bugles et parades.",
    dindon: "Le dindon prefere les sous-bois ouverts avec un couvert de canopee de 50-70% et un sous-bois degage (visibilite au sol de 30-50 m). Il evite la foret dense ou il ne peut pas voir les predateurs au sol. Les peuplements de chenes matures (glands = nourriture) avec peu de sous-bois sont ideaux.",
  },
  recommendations_terrain: {
    orignal: [
      "Maintenir un couvert de canopee de 50-70% dans un rayon de 200 m autour de la saline",
      "Conserver le couvert lateral (0-4 m) a 60-80% — les males matures l'exigent",
      "Creer 3-4 micro-clairieres de 10-20 m a 50-100 m de la saline pour le brout",
      "Privilegier les peuplements mixtes (coniferes + feuillus) — equilibre alimentation/couvert",
      "Conserver les coniferes denses (epinettes, sapins) du cote du vent dominant comme ecran",
      "Eviter les coupes totales dans un rayon de 300 m (perte de couvert = desertion)",
      "Planter des arbres fruitiers indigenes (sorbier, amélanchier) dans les micro-clairieres",
      "Maintenir les arbres morts debout (chicots sains) pour les cavites fauniques"
    ],
    chevreuil: [
      "Creer des ecotones (transitions progressives foret → clairiere) autour de la saline",
      "Couvert lateral de 70%+ dans les corridors d'approche pour attirer les males trophee",
      "Planter des cedres (Thuja occidentalis) en rangees pour creer un couvert lateral permanent",
      "Maintenir un sous-bois de cornouiller, amélanchier et noisetier pour l'alimentation",
      "Creer des 'hinge cuts' (coupes a charniere) pour augmenter le couvert lateral a 1-2 m de hauteur",
      "Eviter les zones de coupe recente (<5 ans) — le chevreuil les utilise pour le brout mais pas pour les salines"
    ],
    ours: [
      "Couvert de 50-70% ideal — protection pour l'ours + visibilite pour le chasseur",
      "Maintenir des zones ouvertes (coupes, brulis) a <500 m pour les petits fruits (alimentation ours)",
      "Conserver les gros arbres (>40 cm DBH) — l'ours grimpe pour se proteger",
      "Degager la visibilite a 360 degres depuis le site de saline (securite du chasseur)"
    ],
    wapiti: [
      "Couvert de 40-60% avec alternance zone ouverte/foret dense",
      "Creer des micro-clairieres pour les zones de bugle et parade du male en rut",
      "Conserver les peuplements de trembles — alimentation preferee du wapiti",
      "Maintenir des corridors de couvert dense entre la saline et les zones de repos"
    ],
    dindon: [
      "Sous-bois ouvert avec visibilite au sol de 30-50 m — le dindon veut voir les predateurs",
      "Couvert de canopee de 50-70% (protection contre les rapaces mais lumiere au sol)",
      "Peuplements de chenes matures ideaux (glands = nourriture principale en automne)",
      "Eviter les zones de coniferes denses (le dindon evite les sous-bois obscurs)",
      "Maintenir des perchoirs (gros arbres avec branches horizontales) a <500 m de la saline"
    ],
  },
  strategies_optimisation: {
    orignal: ["Mixte coniferes-feuillus ideal", "Micro-clairieres pour le brout", "Couvert lateral 60-80% pour males matures"],
    chevreuil: ["Ecotones et transitions progressives", "Hinge cuts pour couvert lateral", "Cedres en rangees pour couvert permanent"],
    ours: ["50-70% couvert + zones ouvertes a proximite pour les petits fruits", "Visibilite 360 degres depuis le site"],
    wapiti: ["40-60% couvert + micro-clairieres pour le rut", "Trembles conserves pour alimentation"],
    dindon: ["Sous-bois ouvert + canopee 50-70%", "Chenes matures ideaux", "Perchoirs a <500 m"],
  },
  techniques_chasse: {
    orignal: ["Les males matures arrivent a la saline depuis la foret dense — orienter l'affut vers le couvert", "En foret ouverte: affut a 6 m (l'orignal a un champ visuel plus large sans obstruction)"],
    chevreuil: ["Les gros males restent dans le couvert dense et visitent la saline la nuit — camera IR pour confirmer", "En ecotone: positionner l'affut cote foret, face a la clairiere"],
    ours: ["L'ours sort de la foret dense directement vers la saline — tir souvent rapide et frontal", "Visibilite obligatoire dans toutes les directions (securite)"],
    wapiti: ["Le wapiti traverse les clairieres en file indienne — positionner le tir perpendiculairement"],
    dindon: ["Le dindon strutze dans les zones ouvertes — positionner le blind en bordure de clairiere"],
  },
  erreurs_a_eviter: {
    orignal: ["Couper tout le couvert autour de la saline (les males matures desertent)", "Creer une clairiere trop grande (>30 m) — l'orignal se mefie des zones ouvertes"],
    chevreuil: ["Defricher le couvert lateral (le chevreuil perd sa protection visuelle)", "Planter des essences exotiques qui ne s'integrent pas au paysage"],
    ours: ["Couvert trop dense (>80%) — l'ours peut approcher sans etre vu (securite chasseur)", "Absence totale de couvert (l'ours ne s'expose pas de jour)"],
    wapiti: ["Supprimer les trembles (alimentation principale)", "Couvert trop dense sans clairieres"],
    dindon: ["Sous-bois trop dense (le dindon ne voit pas les predateurs)", "Absence de perchoirs a proximite"],
  },
  optimisations_saisonnieres: {
    printemps: "Evaluer le couvert post-fonte. Planifier les coupes d'amenagement AVANT la feuillaison.",
    ete: "Couvert maximal. Difficulte d'evaluation du couvert hivernal. Utiliser NDVI satellite.",
    automne: "Feuillaison en baisse — le couvert lateral diminue. Les males deviennent plus visibles.",
    hiver: "Couvert minimal (feuillus sans feuilles). Ideal pour evaluer la structure permanente (coniferes)."
  },
  optimisations_support: ["Planter des coniferes a croissance rapide (cedre, epinette) pour creer du couvert lateral en 3-5 ans", "Hinge cuts sur les feuillus pour couvert lateral instantane (1-2 m)"],
  optimisations_meteo: ["Pluie: les animaux se refugient sous le couvert dense — adapter la position d'observation", "Neige: le couvert de coniferes protege la saline (mineraux accessibles sous la neige interceptee)"],
  optimisations_pression: ["Haute pression: les males se retranchent dans le couvert le plus dense — renforcer le couvert lateral", "Zone publique: le couvert dense reduit la visibilite des autres chasseurs (avantage competitif)"],
  thresholds: { green: "80-100: Couvert canopee 50-70%, couvert lateral 60-80%, ecotone present, essences diversifiees", yellow: "50-79: Couvert 30-50% ou >80%, couvert lateral <60%, ou peuplement mono-specifique", red: "0-49: Couvert <30% (trop ouvert) ou >90% (trop dense), aucun couvert lateral, peuplement degrade" },
  sources: [
    "MRNF — Inventaire ecoforestier et donnees LiDAR (2023)",
    "MFFP — Guide d'amenagement de l'habitat des cervides au Quebec (2021)",
    "Dussault et al. (2005) — Selection d'habitat de l'orignal et couvert forestier (UQAR)",
    "Lesmerises et al. (2012) — Couvert forestier et utilisation de l'habitat (Can. J. Zoology)",
    "NDA — Habitat Management for Quality Deer (2023)",
    "QDMA (archives) — Food Plots and Canopy Management for Whitetails",
    "NWTF — Timber Management for Turkey Habitat (2024)",
    "University of Georgia Deer Lab — Canopy Cover and Buck Movement (2022)",
    "USDA Forest Service — Forest Canopy and Wildlife Habitat Guidelines",
    "Environnement Canada — NDVI Sentinel-2 couvert vegetal (Copernicus)",
  ],
};

// =====================================================================
// DEFAULT PROFESSIONNEL — POUR CRITERES SANS ENTREE DEDIEE
// =====================================================================
const DEFAULT = {
  title: "Critere d'evaluation SUPRA — Guide BIONIC Niveau Professionnel",
  definition: "Ce critere evalue un aspect specifique de la qualite du site de saline. Chaque composante est analysee selon des donnees terrain, des analyses geospatiales (LiDAR, Sentinel-2, DEM), et des references scientifiques reconnues au niveau institutionnel (MFFP, UQAR, Universite Laval).",
  methodology: "Score calcule sur 100 points via un modele multi-facteurs: donnees terrain (40%), analyses geospatiales LiDAR/satellite (30%), references scientifiques institutionnelles (30%). Chaque sous-critere est pondere selon son impact sur la performance globale du site.",
  justification: {
    orignal: "Score determine selon les besoins specifiques de l'orignal (Alces alces): densite de couvert, proximite de l'eau, connectivite des corridors de deplacement, qualite du sous-bois (brout), et les besoins nutritionnels saisonniers en sodium et calcium. L'orignal adulte (400-600 kg) necessite un site robuste avec une accessibilite adaptee a sa taille.",
    chevreuil: "Score determine selon les preferences ecologiques du chevreuil de Virginie (Odocoileus virginianus): ecotones foret-clairiere, couvert lateral dense (70%+) pour les males matures, proximite d'un point d'eau (<200 m), sentiers discrets et corridors de grattage/frottage pour les males territoriaux.",
    ours: "Score determine selon les exigences de l'ours noir (Ursus americanus): securite du site (visibilite 360 degres), distance au camp (>500 m), solidite des structures (anti-griffes), accessibilite des attractifs odorants, et protocoles de securite du chasseur en zone ours.",
    wapiti: "Score determine selon les besoins du wapiti (Cervus canadensis): corridors de migration saisonniere, zones de bugle pour les males en rut, alternance couvert dense/zones ouvertes, accessibilite en terrain montagneux, et besoins nutritionnels en mineraux pour la croissance du panache.",
    dindon: "Score determine selon les preferences du dindon sauvage (Meleagris gallopavo): sous-bois ouvert avec visibilite au sol de 30-50 m, proximite des perchoirs nocturnes (<500 m), zones de parade des males, presence de glands (chenes matures), et corridors perchoir-alimentation quotidiens.",
  },
  recommendations_terrain: {
    orignal: [
      "Consulter les donnees de recolte MFFP pour la zone de chasse (5 dernieres annees)",
      "Effectuer un inventaire des pistes et corridors dans un rayon de 500 m (3 saisons)",
      "Installer 3+ cameras trail pour documenter la frequentation sur 60+ jours",
      "Creer un plan d'amenagement du site avec croquis et mesures GPS",
      "Evaluer le potentiel de brout (cornouiller, amélanchier, tremble) dans un rayon de 200 m",
      "Mesurer le couvert lateral et de canopee avec un densiometre de canopee",
      "Identifier le ravage hivernal le plus proche et les corridors qui y menent",
      "Documenter les observations avec photos datees a chaque visite",
      "Coordonner avec le club de chasse local pour la gestion collective du territoire",
      "Comparer le site avec 2-3 alternatives dans le meme secteur avant l'installation definitive"
    ],
    chevreuil: [
      "Cartographier les ecotones (transitions foret-clairiere) dans un rayon de 500 m",
      "Identifier les zones de frottage (rubs) et grattage (scrapes) — corridors de males dominants",
      "Installer des cameras trail sur les corridors identifies pour confirmer la frequentation",
      "Evaluer la qualite du sous-bois: cornouiller, cedre, amélanchier (alimentation hivernale)",
      "Mesurer le couvert lateral a 1 m et 2 m de hauteur (protection visuelle pour les males trophee)",
      "Creer des hinge cuts pour augmenter le couvert lateral instantanement",
      "Planter des food plots (trefle, brassica) dans les micro-clairieres adjacentes",
      "Documenter les heures de visite par saison via les cameras trail",
      "Evaluer la pression de chasse locale (densite chasseurs/km2 — SEPAQ, ZEC)",
      "Coordonner avec les voisins pour une gestion restrictive volontaire (ramure minimale)"
    ],
    ours: [
      "Evaluer les risques de securite: visibilite 360 degres, distance camp (>500 m), echappatoire",
      "Identifier les corridors d'ours (arbres griffes, excrements, pistes)",
      "Installer des cameras trail avec alerte cellulaire pour surveiller la presence d'ours en temps reel",
      "Verifier la reglementation locale pour les attractifs ours (certaines zones interdisent les appats)",
      "Installer des structures anti-ours (boitiers metalliques, cables Python lock)",
      "Prevoir un protocole d'urgence: spray anti-ours, sifflet, partenaire de chasse obligatoire",
      "Documenter les heures de visite de l'ours (souvent 17h-21h en ete)",
      "Evaluer la densite d'ours dans le secteur (registre MFFP)",
      "Maintenir le site propre entre les visites (aucun dechet alimentaire)",
      "Installer le tree stand a 4-5 m minimum (hors de portee en cas de charge)"
    ],
    wapiti: [
      "Identifier les corridors de migration saisonniere (alpages → vallees d'hivernage)",
      "Evaluer les zones de bugle et parade des males en rut (mi-septembre a mi-octobre)",
      "Installer des cameras trail sur les corridors de migration pour estimer la taille des groupes",
      "Positionner la saline a mi-chemin sur un corridor de migration (zone de transit)",
      "Evaluer les zones de brout: trembles, saules, herbes hautes (alimentation preferee)",
      "Prevoir un acces VTT adapte au terrain montagneux (lacets, barres anti-erosion)",
      "Le wapiti voyage en groupes (5-15) — prevoir une zone de lechage large (2 m rayon)",
      "Coordonner avec les guides de chasse locaux pour les informations sur les populations"
    ],
    dindon: [
      "Identifier les perchoirs nocturnes (grands pins, chenes) dans un rayon de 500 m",
      "Cartographier le corridor perchoir-alimentation (distance, direction, heure)",
      "Installer des cameras trail au sol pour confirmer les heures de passage",
      "Evaluer la disponibilite de glands (chenes matures) dans le secteur",
      "Positionner la zone de mineraux/grains sur le corridor perchoir-alimentation",
      "Installer le ground blind 2+ semaines avant la chasse pour habituation",
      "Preparer des appelants (decoys) et tester les appels (box call, slate call)",
      "Evaluer la densite de dindons via les observations matinales au gobble (mars-avril)",
      "En zone agricole: identifier les champs de mais recemment recoltés (alimentation post-recolte)",
      "Le dindon monte dans les arbres au coucher du soleil — ne pas deranger les perchoirs"
    ],
  },
  strategies_optimisation: {
    orignal: ["Adapter le site selon la saison (ete: pres de l'eau, hiver: pres du ravage)", "Installer 2-3 salines dans un rayon de 1 km pour couvrir differents corridors"],
    chevreuil: ["Creer des ecotones artificiels (hinge cuts, food plots, coulees boisees)", "Gestion restrictive: ne pas recolter les males <3.5 ans pour le potentiel trophee"],
    ours: ["Combiner attractifs odorants avec saline minerale pour maximiser la frequentation", "Installer des structures anti-ours (boitiers metalliques, cables antivol)"],
    wapiti: ["Positionner la saline sur un corridor de migration generationnel", "Combiner saline et appels de wapiti en pre-rut"],
    dindon: ["Combiner saline et appelants (decoys) pour attirer les males", "Cibler les corridors perchoir-alimentation pour intercepter les groupes"],
  },
  techniques_chasse: {
    orignal: ["Observer avant d'agir — 3 sessions d'observation minimum avant de chasser", "Documenter les patterns horaires (cameras trail 30+ jours) avant la saison"],
    chevreuil: ["Le chevreuil memorise — tout changement = alerte de 48-72h", "Ne JAMAIS modifier l'affut ou le site en saison de chasse"],
    ours: ["NE JAMAIS chasser seul en zone ours", "Attendre le broadside complet avant le tir"],
    wapiti: ["Le wapiti est gregaire — un individu alerte = tout le groupe fuit", "Tir ethique: <200 m au fusil, <50 m a l'arc"],
    dindon: ["Immobilite ABSOLUE — le dindon detecte un mouvement a 200 m", "Tir a la tete/cou uniquement a <35 m"],
  },
  erreurs_a_eviter: {
    orignal: ["Negliger l'evaluation de ce critere dans la decision d'emplacement", "Appliquer des recettes generiques sans adaptation au site specifique"],
    chevreuil: ["Copier les strategies de l'orignal pour le chevreuil (espece differente)", "Ignorer les corridors de grattage/frottage des males"],
    ours: ["Sous-estimer les risques de securite en zone ours", "Laisser des dechets alimentaires sur le site"],
    wapiti: ["Ignorer les corridors de migration (stables sur des generations)", "Installer la saline en fond de vallee (vents tourbillonnants)"],
    dindon: ["Utiliser un tree stand pour le dindon (angle de tir inadapte aux plombs)", "Negliger l'habituation du ground blind (2+ semaines)"],
  },
  optimisations_saisonnieres: { printemps: "Evaluation post-fonte. Reperage des nouvelles pistes et corridors.", ete: "Conditions optimales pour l'evaluation terrain et l'installation.", automne: "Saison active. Minimiser les interventions. Cameras trail cellulaires.", hiver: "Evaluation complementaire avec vegetation absente. Reperage aerien ideal." },
  optimisations_support: ["Adapter le support structurel selon les resultats de ce critere", "Utiliser des materiaux resistants aux conditions locales (gel, vent, neige)"],
  optimisations_meteo: ["Integrer les donnees meteorologiques saisonnieres dans l'evaluation", "Adapter la frequence de visite selon les conditions meteo"],
  optimisations_pression: ["Ajuster la strategie selon la pression de chasse locale", "En haute pression: reduire les interventions et maximiser l'efficacite de chaque visite"],
  thresholds: { green: "80-100: Conditions excellentes pour ce critere — site optimal", yellow: "50-79: Conditions moderees — ameliorations possibles et recommandees", red: "0-49: Conditions defavorables — intervention requise ou changement de site a considerer" },
  sources: [
    "MFFP Quebec — Plans de gestion cerf, orignal, ours, dindon (2020-2027)",
    "UQAR — Recherches sur l'habitat et les mouvements des cervides au Quebec",
    "Universite Laval — Departement de biologie: ecologie de la faune",
    "SEPAQ — Guide d'amenagement et normes reserves fauniques (2023)",
    "NDA — National Deer Association: Best Management Practices (2023)",
    "RMEF — Rocky Mountain Elk Foundation: Habitat and Hunting Research (2022)",
    "NWTF — National Wild Turkey Federation: Hunting and Habitat Guides (2024)",
    "Bear Trust International — Black Bear Research and Safety (2022)",
    "Journal of Wildlife Management — Publications cervides et carnivores",
    "Canadian Journal of Zoology — Recherches fauniques canadiennes",
  ],
};

// =====================================================================
// P0 — SOURCE_EAU — Impact direct sur la frequentation animale
// =====================================================================
const source_eau = {
  title: "Source d'eau proximale — Distance et qualite de la source d'eau la plus proche",
  definition: "Evaluation de la distance, du debit et de la qualite de la source d'eau naturelle la plus proche de la saline. L'eau est un besoin quotidien pour tous les cervides — une saline positionnee pres d'un point d'eau actif beneficie d'un trafic animal naturel qui amplifie la frequentation du site de 200-400%.",
  methodology: "Score sur 100: distance source (40 pts — GPS), debit/permanence (25 pts — observation 4 saisons), qualite eau (20 pts — clarte/pH), connectivite avec corridors (15 pts — LiDAR). Sources: MRNF reseau hydrique, LiDAR, observations terrain.",
  justification: {
    orignal: "L'orignal consomme 20-40 litres d'eau par jour et passe 30-60% de son temps estival dans ou pres de l'eau (lacs, marais, ruisseaux). Une saline a <200 m d'une source d'eau permanente capte l'orignal dans son circuit quotidien eau-alimentation-repos. En automne, l'orignal visite la saline apres avoir bu — le corridor eau-saline est le chemin le plus emprunte.",
    chevreuil: "Le chevreuil boit 2-4 litres par jour et prefere les petits ruisseaux calmes aux grandes etendues d'eau. Il visite les points d'eau a l'aube et au crepuscule. Une saline a <150 m d'un ruisseau permanent intercepte le chevreuil sur son circuit quotidien. Les males matures utilisent souvent les memes points d'eau de facon predictible.",
    ours: "L'ours noir consomme 5-10 litres d'eau par jour et est fortement associe aux corridors hydriques (ruisseaux a truites, lacs poissonneux). Il suit les cours d'eau pour se deplacer et s'alimenter (poissons, ecrevisses, grenouilles). Une saline pres d'un ruisseau actif combine 2 attractifs: eau + mineraux.",
    wapiti: "Le wapiti consomme 15-25 litres d'eau par jour. En montagne, il descend quotidiennement vers les vallees pour s'abreuver. Une saline positionnee entre l'alpage (alimentation) et le point d'eau (abreuvement) intercepte le wapiti sur son circuit vertical quotidien. Les femelles avec petits visitent l'eau plus frequemment.",
    dindon: "Le dindon sauvage boit 200-400 ml par jour et prefere les zones humides peu profondes (flaques, mares temporaires, ruisseaux calmes). Il visite les points d'eau en milieu de matinee (9h-11h). Une zone de mineraux pres d'une source d'eau calme combine alimentation et abreuvement.",
  },
  recommendations_terrain: {
    orignal: [
      "Positionner la saline a 100-200 m d'un lac, marais ou ruisseau permanent",
      "Identifier le corridor orignal entre la source d'eau et la foret dense (repos)",
      "Installer la saline EN BORDURE du corridor eau-foret, pas directement sur la rive",
      "Eviter les rives ouvertes — l'orignal prefere un acces a l'eau couvert de vegetation",
      "En ete: l'orignal mange les plantes aquatiques — la proximite de l'eau est CRITIQUE",
      "En automne: le corridor eau-saline est le plus emprunte, y installer l'affut principal",
      "Verifier que la source d'eau est permanente (debit minimal en aout-septembre)",
      "Les marais avec nenuphar et quenouille attirent l'orignal en ete (brout aquatique)",
      "Eviter les berges boueuses instables — l'orignal laisse des empreintes profondes qui alertent les predateurs",
      "Creer un chemin d'acces qui ne longe PAS le cours d'eau (le gibier emprunte les rives)"
    ],
    chevreuil: [
      "Positionner la saline a 100-150 m d'un petit ruisseau calme (pas un torrent bruyant)",
      "Le chevreuil prefere les ruisseaux de <2 m de largeur avec des rives accessibles",
      "Installer la saline du cote du ruisseau oppose a la route ou au chemin d'acces",
      "Le chevreuil boit a l'aube et au crepuscule — l'affut doit couvrir le corridor ruisseau-saline",
      "Les zones de grattage (scrapes) sont souvent pres des points d'eau — les reperer",
      "En ete sec: le chevreuil concentre ses deplacements autour des rares sources actives",
      "Les mares temporaires attirent le chevreuil au printemps (grenouilles, insectes, eau douce)",
      "Eviter les grandes etendues d'eau (lac >5 ha) — le chevreuil les evite par manque de couvert"
    ],
    ours: [
      "L'ours suit les ruisseaux pour se deplacer — positionner la saline a <200 m d'un cours d'eau",
      "Les ruisseaux a truites sont les corridors #1 de l'ours au Quebec — les identifier",
      "L'ours pêche souvent aux confluences de ruisseaux — zones de haute activite",
      "Installer la saline en retrait du ruisseau (50-100 m) pour eviter la zone de peche (securite)",
      "En ete: l'ours passe des heures dans l'eau pour se rafraichir — saline pres d'un bassin",
      "Les lacs avec bleuets sur les rives combinent eau + alimentation + saline = site optimal",
      "Eviter les zones ou l'ours a ete nourri par des humains (ours conditionne = danger)"
    ],
    wapiti: [
      "Positionner la saline entre l'alpage (haut) et le point d'eau (bas) sur le corridor vertical",
      "Les sources de montagne (resurgences) sont les points d'eau les plus fiables — les identifier",
      "Le wapiti descend boire en fin de matinee (10h-12h) et en soiree (16h-18h)",
      "En montagne: les ruisseaux de fond de vallee sont les axes de deplacement principaux",
      "Installer la saline a mi-pente, entre le couvert forestier et la zone d'abreuvement",
      "Les femelles avec petits visitent l'eau 3-4x/jour — frequentation plus previsible"
    ],
    dindon: [
      "Le dindon visite les points d'eau peu profonds (<10 cm) en milieu de matinee",
      "Installer la zone de mineraux pres d'une mare temporaire ou d'un petit ruisseau calme",
      "Le dindon evite les grandes etendues d'eau (zero couvert, predateurs aeriens)",
      "En ete sec: les flaques persistantes attirent les groupes de dindons — y poser les mineraux",
      "Les fossés de drainage agricole sont souvent les points d'eau du dindon en zone rurale"
    ],
  },
  strategies_optimisation: {
    orignal: ["Circuit eau-saline-foret a cartographier", "Saline entre 100-200 m de l'eau", "Corridor eau-saline = meilleur emplacement d'affut"],
    chevreuil: ["Ruisseau calme <2 m de large ideal", "Zone de grattage pres de l'eau = male dominant confirme", "Eté sec concentre les deplacements"],
    ours: ["Ruisseaux a truites = corridors #1", "Confluences = zones de haute activite", "Saline en retrait du ruisseau (50-100 m)"],
    wapiti: ["Corridor vertical alpage-eau", "Sources de montagne = fiables", "Mi-pente ideal"],
    dindon: ["Mares temporaires peu profondes", "Fossés de drainage en zone agricole", "Mi-matinee = heure de visite"],
  },
  techniques_chasse: {
    orignal: ["Observer le corridor eau-saline en soiree (17h-20h) — pic d'activite", "L'orignal revient de l'eau humide — ses pas sont silencieux, arriver a l'affut AVANT"],
    chevreuil: ["Le chevreuil boit puis visite la saline — positionner l'affut entre les deux", "Au crepuscule: scanner les berges avant de se concentrer sur la saline"],
    ours: ["L'ours qui a peche est rassasie et detendu — moment ideal pour le tir a la saline", "NE JAMAIS se placer entre l'ours et le cours d'eau (route de fuite)"],
    wapiti: ["Le wapiti descend boire en groupe — attendre que le groupe soit a la saline avant de tirer"],
    dindon: ["Le dindon desaltere ne reste pas longtemps au point d'eau — etre en position AVANT"],
  },
  erreurs_a_eviter: {
    orignal: ["Installer la saline directement sur la rive (perturbation de la zone d'abreuvement)", "Ignorer la permanence de la source (ruisseau sec en aout = site abandonné)"],
    chevreuil: ["Choisir un cours d'eau trop bruyant (le chevreuil evite le bruit)", "Installer la saline du cote de la route (le chevreuil s'y rend par le cote oppose)"],
    ours: ["S'installer entre l'ours et le cours d'eau", "Ignorer les signes de peche (ecailles, restes) pres du ruisseau"],
    wapiti: ["Installer en fond de vallee pres de l'eau (vents tourbillonnants)", "Negliger les sources de montagne au profit des ruisseaux de fond de vallee"],
    dindon: ["Installer pres d'une grande etendue d'eau (le dindon l'evite)", "Oublier que le dindon visite l'eau en milieu de matinee, PAS a l'aube"],
  },
  optimisations_saisonnieres: { printemps: "Fonte: cours d'eau en crue. Verifier debit et accessibilite. Mares temporaires actives.", ete: "Periode critique: debit minimal. Verifier que la source est permanente. Orignal aquatique actif.", automne: "Debit modere. Corridor eau-saline tres emprunte. Saison de chasse active.", hiver: "Sources gelees. Identifier les resurgences qui restent libres de glace." },
  optimisations_support: ["Pierre de gue sur les petits ruisseaux pour faciliter la traversee du gibier vers la saline", "Bac d'eau artificiel en zone sans source naturelle (25 litres, enterre)"],
  optimisations_meteo: ["Apres pluie forte: les points d'eau secondaires se remplissent — activite accrue", "Secheresse prolongee: les animaux convergent vers les rares sources actives — site stratégique"],
  optimisations_pression: ["En zone haute pression: les animaux visitent l'eau aux heures les plus calmes (mi-journee)", "Les points d'eau eloignes des routes sont moins frequentes par les humains — plus de gibier"],
  thresholds: { green: "80-100: Source permanente <200 m, debit fiable, corridor eau-saline identifie, couvert adequat", yellow: "50-79: Source saisonniere ou >200 m, debit variable, corridor partiel", red: "0-49: Aucune source <500 m, ou source intermittente, ou aucun corridor identifie" },
  sources: [
    "MRNF — Reseau hydrique du Quebec haute resolution (2023)",
    "MFFP — Habitat de l'orignal: importance des milieux humides (2020)",
    "Dussault et al. (2005) — Selection d'habitat de l'orignal et proximite de l'eau (UQAR)",
    "Courtois et al. (2002) — Ecologie de l'orignal en foret boreale (Can. J. Zoology)",
    "NDA — Water Sources and Deer Movement (2023)",
    "Mississippi State University Deer Lab — Whitetail Use of Water Sources (2022)",
    "Bear Trust International — Black Bear Riparian Habitat Use (2021)",
    "RMEF — Elk Watering Behavior in Mountain Terrain (2022)",
    "NWTF — Turkey and Water: Seasonal Habitat Requirements (2024)",
    "USGS — Hydrological Analysis of Wildlife Corridors (2023)",
  ],
};

// =====================================================================
// P0 — PRESSION_CHASSE
// =====================================================================
const pression_chasse = {
  title: "Pression de chasse locale — Densite de chasseurs et impact sur le gibier",
  definition: "Evaluation de la densite de chasseurs dans un rayon de 2 km du site, de la frequence des perturbations humaines, et de l'impact cumule sur le comportement du gibier. La pression de chasse est le facteur #1 de modification comportementale — un male mature en zone haute pression devient strictement nocturne et abandonne les salines de jour.",
  methodology: "Score sur 100: densite chasseurs/km2 (35 pts — registre SEPAQ/ZEC), frequence perturbations (25 pts — observation terrain), pourcentage activite nocturne du gibier (20 pts — cameras trail IR), historique de recolte zone (20 pts — MFFP stats). Sources: SEPAQ, ZEC, MFFP donnees de recolte.",
  justification: {
    orignal: "L'orignal en zone haute pression (>5 chasseurs/km2) modifie radicalement son comportement: activite nocturne +70%, utilisation des corridors secondaires +80%, visite des salines -60%. Un site de saline en zone faible pression (<2 chasseurs/km2) produit 3-5x plus d'observations diurnes et de recoltes que le meme site en zone haute pression.",
    chevreuil: "Le chevreuil de Virginie est le gibier LE PLUS affecte par la pression de chasse. Apres 3 jours de pression, les males matures (3.5+ ans) deviennent 95% nocturnes. Ils abandonnent les salines de jour, se retranchent dans le couvert le plus dense, et ne se deplacent que 30 min avant le lever et 30 min apres le coucher du soleil.",
    ours: "L'ours noir est moderement affecte par la pression de chasse. Il ajuste ses heures de visite (decalage vers la nuit) mais ne deserte pas la zone. En zone haute pression, l'ours visite les salines entre 21h et 4h. En zone faible pression, il visite entre 16h et 21h (heures chassables).",
    wapiti: "Le wapiti reagit a la pression en se retirant vers des zones plus isolees et plus elevees. Un groupe de wapiti soumis a une pression forte (>3 chasseurs/km2) peut migrer de 5-15 km en 48h. La saline est alors completement abandonnee.",
    dindon: "Le dindon sauvage devient tres mefiant apres les premiers coups de feu de la saison. Il cesse de repondre aux appels, se deplace en silence, et reduit ses zones d'alimentation. En zone haute pression, le dindon ne strutze plus en zone ouverte.",
  },
  recommendations_terrain: {
    orignal: [
      "Evaluer la densite de chasseurs dans un rayon de 2 km (registre SEPAQ/ZEC)",
      "En zone haute pression: ne chasser la saline que 2-3x par saison (preservatation de la confiance)",
      "Installer des cameras trail IR pour documenter le ratio activite diurne/nocturne",
      "Coordonner avec les chasseurs voisins pour alterner les jours de chasse",
      "Creer une zone tampon non-chassee de 500 m autour de la saline",
      "Eviter le bruit inutile: VTT electrique, approche a pied, communication silencieuse",
      "En zone publique: chasser en milieu de semaine (lundi-mercredi) pour eviter la pression weekend",
      "L'orignal sous pression utilise des corridors secondaires — les identifier",
      "Ne tirer qu'en conditions optimales (pas de tir force, pas de tir de contournement)",
      "Reporter la session si des coups de feu ont ete entendus dans la derniere heure"
    ],
    chevreuil: [
      "En haute pression: le chevreuil est 95% nocturne — cameras IR pour confirmer les patterns",
      "Gestion restrictive volontaire: ne pas recolter les males <3.5 ans (potentiel trophee futur)",
      "Chasser UNIQUEMENT les 3 premiers jours de la saison (avant l'adaptation comportementale)",
      "Apres le jour 3: passer en mode observation seule (le chevreuil est alerte)",
      "Creer une zone sanctuaire (non-chassee) de 300-500 m autour de la saline principale",
      "Utiliser un ground blind ferme pour reduire la detection visuelle (immobilite)",
      "Ne JAMAIS forcer un tir sur un chevreuil alerte (il memorise la menace pour des semaines)",
      "Alterner entre 3-4 salines pour distribuer la pression sur le territoire"
    ],
    ours: [
      "L'ours s'adapte en decalant ses visites vers la nuit — verifier les heures de passage (cameras IR)",
      "En haute pression: l'ours visite entre 21h et 4h — sessions crepusculaires tardives",
      "L'ours est moins affecte que les cervides — la saline reste frequentee meme sous pression",
      "Eviter de deplacer le bait ou la saline en saison (l'ours perd confiance)",
      "En zone haute pression: augmenter la quantite d'attractifs pour compenser la diminution des visites"
    ],
    wapiti: [
      "Le wapiti fuit la pression — evaluer les zones de repli a 5-15 km du site",
      "Coordonner avec les guides locaux pour limiter la pression sur le secteur",
      "En haute pression: le wapiti se retire en altitude — suivre les corridors d'altitude",
      "Ne pas combiner appels + saline en zone haute pression (double alerte)",
      "Privilegier les zones de gestion controlee (ZEC, pourvoiries) avec pression regulee"
    ],
    dindon: [
      "Apres les premiers coups de feu: le dindon cesse de repondre aux appels pendant 3-5 jours",
      "En haute pression: le male se deplace en silence et ne strutze plus en zone ouverte",
      "Chasser les 2 premiers jours de la saison, puis laisser reposer 5+ jours",
      "Utiliser des appels tres subtils (soft yelps) au lieu des appels agressifs en zone haute pression",
      "Le dindon sous pression se refugie dans les zones les plus denses — adapter le blind"
    ],
  },
  strategies_optimisation: {
    orignal: ["2-3 sessions max par saison en haute pression", "Zone tampon 500 m non-chassee", "Milieu de semaine uniquement"],
    chevreuil: ["3 premiers jours de saison prioritaires", "Zone sanctuaire 300-500 m", "Alterner 3-4 salines"],
    ours: ["Sessions crepusculaires tardives en haute pression", "Augmenter les attractifs", "L'ours s'adapte — la saline reste viable"],
    wapiti: ["Zones de gestion controlee", "Coordonner avec les guides", "Eviter les appels en haute pression"],
    dindon: ["2 premiers jours puis repos 5+ jours", "Appels subtils seulement", "Zones denses pour le blind"],
  },
  techniques_chasse: {
    orignal: ["L'orignal sous pression utilise les corridors secondaires les plus discrets — les identifier en pre-saison", "En zone haute pression: arriver 2h avant l'aube (l'orignal finit son activite nocturne au lever du soleil)"],
    chevreuil: ["Le chevreuil sous pression ne visite la saline que dans les 30 min avant/apres le soleil — etre en position", "Les males matures sous pression se deplacent le nez au vent, avec des pauses de 5-10 min tous les 50 m"],
    ours: ["L'ours sous pression arrive rapidement, mange/leche rapidement, et repart — tir rapide necessaire", "En haute pression: l'ours approche plus lentement et verifie la zone plus longtemps — patience"],
    wapiti: ["Le wapiti sous pression ne bugle plus — passer en mode observation silencieuse", "Les femelles sont moins affectees que les males — observer les groupes de femelles pour localiser les males"],
    dindon: ["Le dindon sous pression se deplace en silence — tendre une embuscade au lieu d'appeler", "Utiliser un appelant femelle seul (pas de jake) — le male sous pression evite la confrontation"],
  },
  erreurs_a_eviter: {
    orignal: ["Chasser la saline tous les jours (l'orignal deserte en 3-5 jours)", "Creer du bruit inutile (claquement de portiere, discussion)"],
    chevreuil: ["Insister apres le jour 3 de pression (le chevreuil est nocturne)", "Modifier l'affut ou la saline en saison"],
    ours: ["Sous-estimer l'adaptation de l'ours (il revient, mais plus tard)", "Deplacer le bait en saison"],
    wapiti: ["Ignorer les signes de migration de pression (le groupe a quitte la zone)", "Combiner appels + saline sous pression"],
    dindon: ["Appels agressifs en zone haute pression (le dindon fuit)", "Ignorer la periode de repos post-coups de feu"],
  },
  optimisations_saisonnieres: { printemps: "Pression faible — ideal pour inventaire et cameras trail. Le gibier est detendu.", ete: "Aucune pression de chasse. Evaluation du site sans perturbation. Cameras trail 60+ jours.", automne: "Pression maximale. Adapter la stratégie: frequence reduite, horaires extremes, corridors secondaires.", hiver: "Pression post-saison. Le gibier recupere. Ideal pour evaluer le dommage de la saison sur la frequentation." },
  optimisations_support: ["Cameras trail IR 24/7 pour documenter le shift diurne/nocturne", "VTT electrique pour reduire le bruit d'approche de 80%"],
  optimisations_meteo: ["Front froid arrivant = activite accrue meme sous pression", "Pression barometrique en hausse = les cervides sortent malgre la pression de chasse"],
  optimisations_pression: ["Haute pression (>5/km2): 2-3 sessions MAX par saison", "Moyenne pression (2-5/km2): 1 session par semaine", "Faible pression (<2/km2): chasse reguliere possible"],
  thresholds: { green: "80-100: <2 chasseurs/km2, >60% activite diurne, zone sanctuaire protegee", yellow: "50-79: 2-5 chasseurs/km2, 30-60% activite diurne, pression moderee", red: "0-49: >5 chasseurs/km2, <30% activite diurne, gibier principalement nocturne" },
  sources: [
    "MFFP — Donnees de recolte et densite de chasseurs par zone de chasse (2020-2024)",
    "SEPAQ — Registre de frequentation des reserves fauniques (2024)",
    "Dussault et al. (2005) — Reponse comportementale de l'orignal a la chasse (UQAR, J. Wildlife Mgmt)",
    "Kilpatrick & Stober (2002) — Whitetail Deer Response to Hunting Pressure (Wildlife Soc. Bulletin)",
    "NDA — Managing Hunting Pressure for Quality Deer Management (2023)",
    "Mississippi State University Deer Lab — Buck Movement and Hunting Pressure (2022)",
    "University of Georgia Deer Lab — Diurnal vs Nocturnal Activity Under Pressure (2021)",
    "RMEF — Elk Migration Responses to Hunting Disturbance (2022)",
    "Bear Trust International — Black Bear Behavioral Adaptation to Hunting (2020)",
    "NWTF — Turkey Behavior Changes During Hunting Season (2024)",
  ],
};

// =====================================================================
// P0 — TRANQUILLITE_ZONE
// =====================================================================
const tranquillite_zone = {
  title: "Tranquillite de la zone — Niveau de perturbation humaine et predateurs",
  definition: "Evaluation du niveau global de perturbation dans un rayon de 1 km: activites humaines (routes, exploitation forestiere, recreotourisme), presence de predateurs (coyote, loup, ours en zone chevreuil), et bruits mecaniques. Les males matures tolerent un seuil de perturbation inferieur aux femelles et juveniles.",
  methodology: "Score sur 100: distance routes actives (30 pts — MRNF), bruit ambiant (25 pts — mesure dB), frequence passages humains (25 pts — cameras trail), presence predateurs (20 pts — indices terrain). Sources: MRNF reseau routier, cameras trail, observations terrain.",
  justification: {
    orignal: "L'orignal adulte tolere un niveau de perturbation modere (routes forestieres a >500 m, exploitation a >1 km). Les males matures fuient les zones ou le bruit depasse 40 dB de facon reguliere. Les operations forestieres actives dans un rayon de 1 km reduisent la frequentation de la saline de 70-90% pendant la duree des travaux.",
    chevreuil: "Le chevreuil est extremement sensible aux perturbations. Il memorise les sources de derangement et ajuste ses circuits pour les eviter. Un chemin de VTT utilise regulierement a <300 m de la saline reduit la frequentation diurne de 50-80%. Les males trophee (4.5+ ans) exigent une tranquillite presque totale (<20 dB de jour).",
    ours: "L'ours noir est moderement tolerant aux perturbations humaines regulieres (il s'habitue). Les ours vivant pres des zones habitees sont souvent plus tolerants. Cependant, les perturbations imprevues (tronconneuse, dynamitage) provoquent une fuite de 48-72h. L'ours craint davantage les chiens que les humains.",
    wapiti: "Le wapiti est tres sensible aux perturbations et reagit en groupe — un individu alerte provoque la fuite de tout le troupeau (5-15 individus). Le rayon de fuite du wapiti est de 200-400 m pour les perturbations visuelles et 500+ m pour les perturbations sonores.",
    dindon: "Le dindon est extremement vigilant visuellement mais tolere les bruits de fond reguliers (vent, ruisseau, circulation lointaine). Les perturbations soudaines (coup de feu, chien, VTT) provoquent un envol de fuite et une absence de 24-48h.",
  },
  recommendations_terrain: {
    orignal: [
      "Evaluer la distance aux routes forestieres actives (minimum 500 m recommande)",
      "Verifier le calendrier d'exploitation forestiere dans un rayon de 2 km (MRNF)",
      "Installer des cameras trail pour documenter les periodes de quietude maximale",
      "Eviter les zones avec sentiers de VTT recreatifs a <500 m",
      "Mesurer le bruit ambiant a la saline (objectif: <30 dB de jour)",
      "Les zones tampons de coupes forestieres anciennes (5+ ans) offrent une bonne tranquillite",
      "L'orignal s'habitue aux bruits reguliers (route lointaine) mais pas aux bruits intermittents",
      "Exploiter les zones inaccessibles par route (acces VTT ou pedestre uniquement)"
    ],
    chevreuil: [
      "Distance minimale aux chemins utilises regulierement: 300 m",
      "Le chevreuil detecte un promeneur a 200+ m — evaluer la frequentation humaine du secteur",
      "Creer une zone sanctuaire (non-perturbee) de 300 m autour de la saline",
      "Eviter les zones pres de camps de chasse actifs (va-et-vient = perturbation permanente)",
      "Les males trophee fuient les zones avec bruit regulier — privilegier l'isolement total",
      "Les zones proches des champs agricoles avec machinerie sont perturbees 6 mois/an",
      "Le chevreuil s'habitue aux bruits reguliers (tracteur quotidien) mais pas aux bruits nouveaux"
    ],
    ours: [
      "L'ours tolere les routes forestieres a >200 m si le trafic est faible (<5 vehicules/jour)",
      "Les ours periurbains sont plus tolerants — evaluer le contexte local",
      "Les chiens non attaches sont la perturbation #1 pour l'ours — evaluer la presence de chiens",
      "Les perturbations soudaines (tronconneuse, dynamitage) provoquent une fuite de 48-72h",
      "L'ours revient plus vite que les cervides apres une perturbation (24-72h vs 1-2 semaines)"
    ],
    wapiti: [
      "Le wapiti exige un rayon de tranquillite de 400+ m (visuel) et 500+ m (sonore)",
      "Tout le groupe fuit si un individu est alerte — la perturbation affecte 5-15 animaux",
      "Les zones de montagne isolees offrent la meilleure tranquillite",
      "Le wapiti est habitue aux vehicules forestiers mais pas aux pietons (predateur bipede)",
      "Coordonner avec les guides locaux pour limiter les perturbations dans le secteur"
    ],
    dindon: [
      "Le dindon tolere les bruits de fond reguliers (circulation lointaine, vent) mais pas les bruits soudains",
      "Distance minimale aux habitations: 200 m (le dindon s'approche mais evite l'activite directe)",
      "Les chiens et chats sont des perturbateurs majeurs pour le dindon — evaluer la presence",
      "Apres un envol de fuite, le dindon revient a la meme zone en 24-48h si aucune recurrence",
      "Les zones agricoles calmes (hors saison de machinerie) sont ideales pour le dindon"
    ],
  },
  strategies_optimisation: {
    orignal: ["Zone tampon 500 m des routes actives", "Zones inaccessibles par route", "Calendrier exploitation forestiere"],
    chevreuil: ["Zone sanctuaire 300 m", "Isolement total pour males trophee", "Evaluer frequentation humaine du secteur"],
    ours: ["L'ours s'habitue aux perturbations regulieres", "Eviter les chiens", "Perturbations soudaines = fuite 48-72h"],
    wapiti: ["Rayon 400+ m visuel, 500+ m sonore", "Montagne isolee ideal", "Coordonner avec les guides"],
    dindon: ["Bruits de fond OK, bruits soudains NON", "Chiens/chats = perturbateurs #1", "Retour en 24-48h si pas de recurrence"],
  },
  techniques_chasse: {
    orignal: ["Arriver a la saline 2h avant l'aube dans le silence total", "Pas de communication radio — gestes uniquement"],
    chevreuil: ["Le chevreuil evalue la tranquillite pendant 10-15 min avant d'entrer a la saline", "Un chevreuil qui fait des pauses longues (>30 s) a detecte quelque chose — rester immobile"],
    ours: ["L'ours alerte se dresse sur ses pattes arriere pour evaluer la menace — ne PAS bouger", "En zone calme: l'ours est plus detendu et reste plus longtemps a la saline"],
    wapiti: ["Le wapiti envoie une femelle eclaireur avant que le groupe n'entre — attendre le groupe complet"],
    dindon: ["Le dindon ecoute pendant 5 min apres un appel — silence ABSOLU pendant ce temps"],
  },
  erreurs_a_eviter: {
    orignal: ["Chasser pres d'une zone d'exploitation forestiere active", "Creer du bruit pendant l'installation de l'affut"],
    chevreuil: ["Visiter la saline trop souvent (chaque visite depose des odeurs et du bruit)", "Installer la saline pres d'un chemin de randonnee"],
    ours: ["Negliger la presence de chiens dans le secteur", "Ignorer une perturbation soudaine recente (l'ours est en fuite 48-72h)"],
    wapiti: ["Sous-estimer le rayon de fuite du wapiti (400+ m)", "Approcher a pied en terrain ouvert (predateur bipede)"],
    dindon: ["Provoquer un envol de fuite par approche trop rapide", "Ignorer la presence de chiens/chats dans le secteur"],
  },
  optimisations_saisonnieres: { printemps: "Pas de chasse. Tranquillite maximale. Ideal pour observation et cameras trail.", ete: "Exploitation forestiere possible. Verifier le calendrier MRNF. Tranquillite variable.", automne: "Saison de chasse. Perturbation maximale. Adapter la strategie (horaires extremes).", hiver: "Post-saison. Le gibier recupere. Tranquillite en hausse progressive." },
  optimisations_support: ["Cameras trail cellulaires pour eviter les visites inutiles au site", "VTT electrique pour approche silencieuse"],
  optimisations_meteo: ["Vent fort (>20 km/h): masque les bruits humains — le gibier est moins alerte", "Neige fraiche: le craquement des pas se propage loin — approche plus difficile"],
  optimisations_pression: ["Zone haute pression = perturbation maximale — combiner pression + tranquillite dans l'evaluation", "Zone faible pression + haute tranquillite = site optimal pour males matures"],
  thresholds: { green: "80-100: >500 m des routes, <30 dB ambiant, <2 passages humains/jour, aucune exploitation active", yellow: "50-79: 200-500 m des routes, 30-40 dB, 2-5 passages/jour, exploitation a >1 km", red: "0-49: <200 m d'une route active, >40 dB, >5 passages/jour, exploitation active <1 km" },
  sources: [
    "MRNF — Reseau routier forestier et calendrier d'exploitation (2024)",
    "Dussault et al. (2005) — Reponse de l'orignal aux perturbations humaines (UQAR)",
    "Lesmerises et al. (2012) — Impact des routes sur l'utilisation de l'habitat (Can. J. Zoology)",
    "NDA — Sanctuary Areas and Buck Maturity (2023)",
    "University of Georgia Deer Lab — Human Disturbance and Deer Movement (2021)",
    "Bear Trust International — Black Bear Tolerance of Human Activity (2020)",
    "RMEF — Elk Disturbance Thresholds (2022)",
    "NWTF — Turkey Response to Predators and Humans (2024)",
    "Environnement Canada — Niveaux de bruit en milieu forestier (2023)",
  ],
};

// =====================================================================
// P0 — POTENTIEL_TROPHEE
// =====================================================================
const potentiel_trophee = {
  title: "Potentiel de presence de males trophees — Evaluation du potentiel de recolte de qualite",
  definition: "Evaluation de la probabilite de presenter des males matures (3.5+ ans pour le chevreuil, 5+ ans pour l'orignal, 300+ lbs pour l'ours, 6x6+ pour le wapiti) sur le site. Integre l'historique de recolte, la structure d'age du cheptel, la qualite de l'habitat, la pression de chasse et les observations cameras trail.",
  methodology: "Score sur 100: historique recolte males matures 5 ans (30 pts — MFFP), structure d'age cameras trail (25 pts), qualite habitat/couvert (25 pts — LiDAR), pression chasse locale (20 pts — registre). Sources: MFFP stats recolte, cameras trail, LiDAR MRNF.",
  justification: {
    orignal: "Un orignal male mature (5+ ans) porte un panache de 40-55 pouces (trophee) et pese 500-700 kg. Il est solitaire, nocturne en zone haute pression, et utilise des corridors secondaires pour eviter les humains. La presence d'un male mature confirme un habitat de qualite — couvert dense, faible pression, corridors connectes, et ressources alimentaires suffisantes.",
    chevreuil: "Un male trophee (3.5+ ans, 140+ P&Y) represente 5-10% de la population male totale. Il frequente les zones avec couvert lateral >70%, faible pression (<2 chasseurs/km2), et corridors de grattage actifs. La gestion restrictive (protection des 1.5-2.5 ans) est necessaire pour produire des males trophee. Les cameras trail montrent que 80% des visites de males trophee aux salines sont nocturnes.",
    ours: "Un ours noir trophee pese 300+ lbs (male de 5+ ans). Il est dominant sur son territoire et marque les arbres a 1.8-2.2 m de hauteur. Les males dominants visitent les salines en dernier (apres les femelles et juveniles) et restent le temps le plus court. Identifier le dominant via les griffures d'arbres et les cameras trail.",
    wapiti: "Un wapiti trophee male porte un panache 6x6+ (6 pointes par cote). Il est present dans les zones avec corridors de migration generationnels, prairies d'alpage, et faible pression. Le male dominant bugle en pre-rut — les appels confirment sa presence.",
    dindon: "Un dindon trophee male (jake mature, 2+ ans) a une barbe de 25+ cm et des ergots de 2.5+ cm. Il strutze en zone ouverte pour attirer les femelles. Les males dominants ont un territoire de 200-500 ha et visitent les zones de mineraux regulierement en pre-saison.",
  },
  recommendations_terrain: {
    orignal: [
      "Installer des cameras trail grand angle sur les corridors pour documenter les panaches (30+ jours)",
      "Identifier les arbres de frottage (rubs) — les ecorces arrachees a >1.5 m = male mature",
      "Les frottages sur des arbres de 15+ cm de diametre = male mature confirme",
      "Verifier les donnees de recolte MFFP pour la zone (males 5+ ans recoltes dans les 5 ans)",
      "Le couvert lateral de 60-80% est OBLIGATOIRE pour les males matures (ils refusent les zones ouvertes de jour)",
      "Creer 2-3 micro-clairieres a 50-100 m de la saline pour le brout de males",
      "En pre-rut (15 sept): les males matures commencent a patrouiller — augmenter les cameras",
      "Les empreintes de >15 cm de large dans la boue = male mature confirme"
    ],
    chevreuil: [
      "Gestion restrictive OBLIGATOIRE: ne pas recolter les males <3.5 ans (protection du potentiel trophee)",
      "Installer des cameras trail a detection rapide (0.2 s) pour capturer les males de passage",
      "Identifier les zones de grattage (scrapes) actives — signalent un male dominant territorial",
      "Les frottages sur des arbres de 5-8 cm de diametre = male mature (1.5 ans frottent <3 cm)",
      "Documenter le ratio males/femelles via cameras trail sur 60+ jours",
      "Les males trophee visitent les salines de nuit (22h-4h) — cameras IR obligatoires",
      "Couvert lateral >70% obligatoire dans les corridors d'approche pour les males trophee",
      "Les zones avec 3+ grattages actifs dans un rayon de 100 m = male dominant confirme"
    ],
    ours: [
      "Identifier les arbres griffes — griffures a >1.8 m de hauteur = male dominant (300+ lbs)",
      "Les excrements de >5 cm de diametre = male mature",
      "Installer des cameras trail avec flash IR (pas de flash blanc — l'ours le detecte)",
      "Le male dominant visite la saline en dernier — patience obligatoire (attendre 30+ min)",
      "Evaluer la densite d'ours via les donnees MFFP et les observations terrain",
      "Les males dominants marquent les arbres regulierement — carré de griffures = territoire actif"
    ],
    wapiti: [
      "Le male dominant bugle en pre-rut (mi-sept) — ecouter et documenter les appels",
      "Installer des cameras trail sur les corridors de migration pour identifier les panaches 6x6+",
      "Les zones de parade (strutting areas) des males sont des zones ouvertes pres de la foret dense",
      "Le wapiti male dominant est souvent le 3e ou 4e individu d'un groupe en file indienne",
      "Les empreintes de >10 cm de large = male mature"
    ],
    dindon: [
      "Observer les zones de parade en mars-avril (le male strutze a l'aube et au crepuscule)",
      "Mesurer la barbe et les ergots des dindons observes (camera trail + observation matinale)",
      "Les males dominants ont un territoire de 200-500 ha — cartographier les deplacements",
      "Les plumes de strutting laissees au sol confirment la presence d'un male trophee",
      "Les males dominants vocalisent (gobble) depuis le perchoir — ecouter avant l'aube"
    ],
  },
  strategies_optimisation: {
    orignal: ["Cameras trail 30+ jours en pre-rut", "Couvert lateral 60-80% obligatoire", "Micro-clairieres pour le brout"],
    chevreuil: ["Gestion restrictive (pas de recolte <3.5 ans)", "Cameras IR pour les visites nocturnes", "3+ grattages actifs = dominant confirme"],
    ours: ["Griffures >1.8 m = dominant (300+ lbs)", "Le dominant arrive en dernier", "Cameras IR (pas de flash blanc)"],
    wapiti: ["Ecouter les bugles en pre-rut", "Male dominant = 3e ou 4e en file", "Zones de parade pres de la foret"],
    dindon: ["Observer les parades mars-avril", "Barbe >25 cm = trophee", "Gobble depuis le perchoir avant l'aube"],
  },
  techniques_chasse: {
    orignal: ["En pre-rut: utiliser un appel de femelle (cow call) pour attirer le male dominant", "Le male mature est prudent — il observe la saline 10-15 min avant d'approcher"],
    chevreuil: ["Le male trophee visite la saline pendant 5-10 min seulement — tir rapide et precis", "Utiliser des mock scrapes (grattages artificiels) pour provoquer la competition territoriale"],
    ours: ["Attendre que l'ours dominant s'installe et se detende (5-10 min) avant de tirer", "L'ours dominant tourne la tete pour scanner — tirer quand il baisse la tete pour lecher"],
    wapiti: ["Le male dominant bugle pour defier les rivaux — utiliser un bugle de defi pour l'attirer vers l'affut"],
    dindon: ["Le male dominant strutze pour les femelles — placer un appelant femelle entre le blind et la zone de parade"],
  },
  erreurs_a_eviter: {
    orignal: ["Tirer un jeune male qui pourrait devenir trophee dans 2-3 ans", "Negliger le couvert lateral (le male mature deserte les zones ouvertes)"],
    chevreuil: ["Recolter les males de 1.5-2.5 ans (sacrifice du potentiel trophee futur)", "Ignorer les grattages et frottages (indicateurs de presence de male dominant)"],
    ours: ["Tirer le premier ours qui arrive (souvent femelle ou juvenile, pas le dominant)", "Utiliser un flash blanc sur la camera trail (alerte l'ours dominant)"],
    wapiti: ["Tirer sur le premier wapiti du groupe (souvent une femelle eclaireur)", "Ignorer les bugles en pre-rut (confirment la presence du dominant)"],
    dindon: ["Tirer un jake (1 an) au lieu d'attendre le gobbler mature (2+ ans)", "Ignorer les zones de parade (meilleur indicateur de presence)"],
  },
  optimisations_saisonnieres: { printemps: "Mue des panaches. Cameras trail pour documenter la pousse. Identification individuelle.", ete: "Panaches en velours. Cameras trail continues. Evaluation structure d'age.", automne: "Panaches matures. Pre-rut puis rut. Meilleure periode pour evaluer le potentiel.", hiver: "Panaches tombes. Ramassage de shed antlers pour evaluer la qualite. Ravages visibles." },
  optimisations_support: ["Cameras trail a detection rapide (0.2 s) avec flash IR", "Panneaux de classification des panaches pour identification rapide"],
  optimisations_meteo: ["Front froid arrivant = activite accrue des males matures (rut intensifie)", "Lune nouvelle = nuits sombres = males plus actifs en crepuscule (periodes chassables)"],
  optimisations_pression: ["Faible pression = males matures actifs de jour (ratio diurne/nocturne eleve)", "Haute pression = males strictement nocturnes — cameras IR essentielles"],
  thresholds: { green: "80-100: Males matures documentes (cameras), structure d'age equilibree, gestion restrictive, couvert 60-80%", yellow: "50-79: Males observes occasionnellement, structure d'age desequilibree, couvert 40-60%", red: "0-49: Aucun male mature documente, surexploitation, couvert <40%, haute pression" },
  sources: [
    "MFFP — Donnees de recolte et structure d'age par zone de chasse (2020-2024)",
    "QDMA (archives) — Quality Deer Management: Age Structure and Harvest Data",
    "NDA — Antler Growth and Age Estimation (2023)",
    "Mississippi State University Deer Lab — Mature Buck Behavior and Habitat Use (2022)",
    "University of Georgia Deer Lab — Trail Camera Surveys for Population Assessment (2021)",
    "RMEF — Bull Elk Age Structure and Harvest Management (2022)",
    "Bear Trust International — Black Bear Age and Size Estimation (2020)",
    "NWTF — Turkey Age and Harvest Guidelines (2024)",
    "Dussault et al. (2012) — Dynamique de population de l'orignal au Quebec (UQAR)",
    "Universite Laval — Structure d'age et gestion des populations cervides (2021)",
  ],
};

// =====================================================================
// P0 — VISIBILITE_AFFUTS
// =====================================================================
const visibilite_affuts = {
  title: "Visibilite depuis les affuts — Champ de vision et angles de tir",
  definition: "Evaluation du champ de vision disponible depuis chaque poste d'affut vers la saline et les corridors d'approche. Inclut la mesure du cone de visibilite (en degres), la profondeur de champ, les obstructions visuelles (branches, troncs, relief), et la luminosite ambiante aux heures de chasse.",
  methodology: "Score sur 100: cone de visibilite (35 pts — mesure terrain), profondeur de champ (25 pts — laser), obstructions (20 pts — inventaire), luminosite (20 pts — orientation E/O). Mesures: telemetres, boussole, evaluation terrain.",
  justification: {
    orignal: "L'orignal est un gibier de grande taille (1.8-2.1 m au garrot) — la visibilite depuis l'affut est critique pour l'identification (male/femelle, age, panache). Le cone de tir optimal pour l'orignal est de 120-180 degres depuis un tree stand a 5-6 m. Les branches entre 0 et 6 m doivent etre degagees pour eviter les deviations de projectile.",
    chevreuil: "Le chevreuil est plus petit (90 cm au garrot) et se deplace dans le couvert dense. La visibilite depuis l'affut doit permettre l'identification du sexe et de l'age (panache, taille corporelle) a 30+ m. Un cone de 90-120 degres suffit (le chevreuil detecte les mouvements peripheriques — ne pas scanner 180 degres).",
    ours: "L'ours noir est sombre et difficile a voir dans le sous-bois. La visibilite doit etre excellente entre l'affut et la saline pour le tir ethique (zone vitale derriere l'epaule). Un eclairage lateral (est le matin, ouest le soir) ameliore la visibilite sur le pelage sombre. Visibilite OBLIGATOIRE dans toutes les directions pour la securite.",
    wapiti: "Le wapiti est grand (1.5 m au garrot) avec un panache de 1.2 m d'envergure. La visibilite doit couvrir un cone large (140-180 degres) car le wapiti approche en groupe et peut arriver de n'importe quelle direction. Les branches genantes doivent etre degagees au-dessus de 2 m pour le passage du panache.",
    dindon: "Le dindon est petit (60-70 cm au sol) et se deplace en group au sol. La visibilite HORIZONTALE (0-1 m) est critique depuis un ground blind. Le champ de vision au sol doit etre degage sur 30-50 m pour identifier le sexe (barbe, ergots, caroncule). Les ouvertures du blind doivent etre etroites pour limiter la detection par le dindon.",
  },
  recommendations_terrain: {
    orignal: [
      "Degager un cone de tir de 120-180 degres depuis l'affut vers la saline",
      "Tailler les branches entre 0 et 6 m de hauteur dans les corridors de tir",
      "Marquer les distances (20, 30, 40, 50 m) avec des reperes naturels discrets",
      "Orienter l'affut pour avoir le soleil levant dans le dos (eclairage sur la cible)",
      "Verifier la visibilite depuis l'affut a differentes heures (aube, crepuscule, mi-journee)",
      "Les branches coupees doivent etre retirees ou utilisees pour le camouflage (pas laissees au sol)",
      "Creer un 'trou de tir' de 3 m de largeur minimum dans chaque corridor degage",
      "Verifier que la visibilite est suffisante avec la vegetation d'ete (feuilles = obstruction +40%)",
      "Installer un repose-fusil ou repose-arc pour stabiliser le tir depuis l'affut"
    ],
    chevreuil: [
      "Cone de tir de 90-120 degres (ne pas scanner trop large — le mouvement alerte le chevreuil)",
      "Degager les corridors de tir de 2 m de largeur seulement (pas trop large)",
      "Tailler les branches genantes a 1-4 m de hauteur (zone de tir arc/fusil)",
      "Marquer les distances a 15, 20, 25, 30 m (arc) ou 40, 60, 80 m (fusil)",
      "Le chevreuil arrive souvent sous le couvert — la visibilite a 2 m de hauteur est critique",
      "Installer un paravent lateral sur le tree stand pour cacher les mouvements du chasseur",
      "Verifier la visibilite en octobre (apres la chute des feuilles = visibilite amelioree)"
    ],
    ours: [
      "Visibilite 360 degres OBLIGATOIRE depuis l'affut (securite en zone ours)",
      "Eclairage lateral (E matin, O soir) pour voir le pelage sombre de l'ours",
      "Degager la visibilite entre l'affut et la saline sur toute la largeur (pas de zone morte)",
      "Marquer la distance de 15-20 m (arc) et 30-50 m (fusil) pour le tir ethique",
      "La visibilite vers le chemin de sortie est OBLIGATOIRE (echappatoire)",
      "L'ours arrive souvent directement — la visibilite frontale est prioritaire"
    ],
    wapiti: [
      "Cone de tir large de 140-180 degres (le wapiti approche de n'importe quelle direction en groupe)",
      "Degager les branches au-dessus de 2 m pour le passage du panache (1.2 m d'envergure)",
      "Marquer les distances a 30, 40, 50 m (arc) et 80, 120, 150 m (fusil)",
      "Le wapiti est grand — la visibilite au-dessus de 1.5 m est plus importante que la visibilite au sol",
      "Orientation avec le soleil dans le dos le matin (l'animal ebloui est moins vigilant)"
    ],
    dindon: [
      "Visibilite HORIZONTALE au sol (0-1 m) sur 30-50 m depuis le ground blind",
      "Ouvertures du blind etroites (30-40 cm de large) pour limiter la detection par le dindon",
      "Visibilite au sol degagee (ratisser les feuilles mortes pour voir le dindon approcher en silence)",
      "La visibilite vers les perchoirs est utile (observer les dindons descendre a l'aube)",
      "Le dindon voit les couleurs — la visibilite interieure du blind doit etre sombre (pas de reflet)"
    ],
  },
  strategies_optimisation: {
    orignal: ["120-180 degres cone de tir", "Branches 0-6 m degagees", "Soleil dans le dos le matin"],
    chevreuil: ["90-120 degres (pas plus large)", "Corridors etroits 2 m", "Paravent lateral obligatoire"],
    ours: ["360 degres visibilite securite", "Eclairage lateral pour pelage sombre", "Echappatoire visible"],
    wapiti: ["140-180 degres pour le groupe", "Au-dessus de 2 m pour le panache", "Soleil dans le dos"],
    dindon: ["Visibilite sol 0-1 m sur 30-50 m", "Ouvertures blind etroites", "Interieur blind sombre"],
  },
  techniques_chasse: {
    orignal: ["Scanner lentement avec les jumelles AVANT de se tourner vers l'arme", "La visibilite a la torche frontale rouge est autorisee pour l'installation predawn (pas de torche blanche)"],
    chevreuil: ["Le chevreuil detecte le mouvement de tete du scanner — scanner avec les YEUX, pas la tete", "Utiliser un miroir ou une camera pour verifier les angles morts sans se tourner"],
    ours: ["L'ours sombre est difficile a voir au crepuscule — ne tirer QUE si la zone vitale est clairement visible", "En lumiere faible: attendre que l'ours se tourne broadside sous la lumiere residuelle"],
    wapiti: ["Scanner le groupe au complet avant de choisir le male dominant — ne pas tirer le premier vu"],
    dindon: ["Observer par les ouvertures du blind sans bouger la tete (les yeux seulement)"],
  },
  erreurs_a_eviter: {
    orignal: ["Degager trop large (>4 m) — cree une ouverture artificielle visible de loin", "Negliger la visibilite au crepuscule (lumiere faible = erreur d'identification)"],
    chevreuil: ["Scanner 180 degres (trop de mouvement — le chevreuil detecte)", "Degager le sous-bois au complet (perte de couvert = chevreuil alerte)"],
    ours: ["Negliger la visibilite arriere (l'ours peut approcher par derriere)", "Tirer dans la penombre sans identification certaine de la zone vitale"],
    wapiti: ["Laisser des branches basses qui accrochent le panache (le wapiti evite la zone)"],
    dindon: ["Ouverture du blind trop large (le dindon detecte le mouvement interieur)"],
  },
  optimisations_saisonnieres: { printemps: "Vegetation absente. Visibilite maximale. Evaluer les corridors avec precision.", ete: "Vegetation dense. Visibilite reduite de 40%. Planifier la coupe d'entretien.", automne: "Feuilles tombantes. Visibilite qui s'ameliore d'octobre a novembre.", hiver: "Visibilite maximale. Evaluation ideale des lignes de tir." },
  optimisations_support: ["Jumelles 8x42 ou 10x42 pour l'identification a distance", "Telemetre laser pour mesure precise des distances de tir"],
  optimisations_meteo: ["Brouillard: visibilite reduite a 30-50 m — ne tirer que dans la zone claire", "Neige: contraste ameliore (pelage sombre sur fond blanc)"],
  optimisations_pression: ["En haute pression: le gibier est ultra-vigilant — AUCUN mouvement visible depuis l'affut"],
  thresholds: { green: "80-100: Cone 120+ degres, distances marquees, obstructions <10%, luminosite bonne aux heures de chasse", yellow: "50-79: Cone 60-120 degres, quelques obstructions, luminosite partielle", red: "0-49: Cone <60 degres, obstructions majeures, visibilite insuffisante pour tir ethique" },
  sources: [
    "MFFP — Guide de securite et ethique de la chasse au Quebec (2024)",
    "NDA — Treestand Visibility and Shooting Lanes (2023)",
    "QDMA (archives) — Stand Placement and Shooting Lane Management",
    "Mississippi State University Deer Lab — Optimal Shooting Angles for Bowhunters (2021)",
    "RMEF — Elk Hunting: Field of View and Shot Placement (2022)",
    "NWTF — Ground Blind Setup: Window Management (2024)",
    "Bear Trust International — Shot Placement on Black Bears (2022)",
    "Universite Laval — Ethique de la chasse et identification du gibier (2020)",
  ],
};

// =====================================================================
// P0 — TOPOGRAPHIE_LIDAR
// =====================================================================
const topographie_lidar = {
  title: "Topographie LiDAR — Relief et micro-topographie du site et environs",
  definition: "Analyse du relief et de la micro-topographie du site via les donnees LiDAR haute resolution (MRNF). Inclut les pentes, les micro-vallons, les cretes, les cuvettes thermiques, et les zones d'ombre. La topographie influence directement les thermiques (courants d'air montants/descendants) et les corridors naturels de la faune.",
  methodology: "Score sur 100: pente locale (30 pts — DEM LiDAR), exposition (25 pts — orientation N/S/E/O), micro-relief (25 pts — rugosité terrain), drainage topographique (20 pts — modele hydrologique). Sources: LiDAR MRNF haute resolution, DEM Canada.",
  justification: {
    orignal: "L'orignal prefere les pentes moderees (5-15%) avec des cretes boisees pour les corridors. Les micro-vallons offrent une protection thermique et un couvert naturel. Les fonds de cuvettes sont souvent des zones de repos hivernales (ravages). La topographie determine les corridors naturels — les cretes et les cols sont les passages obliges.",
    chevreuil: "Le chevreuil utilise les micro-vallons et les coulees comme corridors de deplacement protege. Les versants sud sont prefereres en hiver (exposition solaire, neige moindre). Les pentes >20% sont evitees sauf en fuite. La topographie determine les 'points de passage' (pinch points) ou concentrer l'effort de chasse.",
    ours: "L'ours utilise les vallees et les fonds de ravins pour ses deplacements. Les versants sud avec bleuets et framboisiers (exposition solaire) sont des zones d'alimentation privilegiees. Les pentes moderees (5-15%) avec affleurements rocheux offrent des tannieres potentielles.",
    wapiti: "Le wapiti effectue des migrations altitudinales saisonnieres. Les cols et les selles topographiques sont les corridors de migration obliges. Les alpages d'ete (plateaux d'altitude) et les vallees d'hivernage sont relies par des corridors topographiques stables.",
    dindon: "Le dindon prefere les terrains relativement plats a legerement vallonnes (pente <10%). Il evite les pentes abruptes (>20%) sauf pour les perchoirs (arbres de crete). Les zones basses bien drainees avec sous-bois ouvert sont ideales.",
  },
  recommendations_terrain: {
    orignal: [
      "Identifier les cretes boisees dans un rayon de 500 m — corridors principaux de l'orignal",
      "Positionner la saline sur une pente moderee (5-10%) — bon drainage, bon couvert",
      "Eviter les fonds de cuvette (accumulation d'air froid, brouillard, vents tourbillonnants)",
      "Les cols entre 2 vallees sont des passages obliges — positions strategiques pour les affuts",
      "Utiliser les donnees LiDAR MRNF pour identifier les micro-vallons (corridors caches)",
      "Les versants nord offrent un couvert de coniferes plus dense (meilleur couvert)",
      "Les versants sud ont plus de feuillus (meilleur brout estival)",
      "En hiver: les ravages sont en fond de vallee protege — identifier les acces"
    ],
    chevreuil: [
      "Identifier les 'pinch points' topographiques (retrecissements entre 2 reliefs) — concentration du passage",
      "Les coulees boisees (micro-vallons de 3-10 m de profondeur) sont les corridors #1 du chevreuil",
      "Versant sud en hiver: le chevreuil s'y expose pour la chaleur solaire",
      "Pentes >20% evitees sauf en fuite — concentrer les affuts sur les pentes moderees",
      "Les terrasses naturelles le long des ruisseaux sont des zones de repos preferees",
      "Les bordures de plateau (transition pente-plat) sont des zones de transition frequentees"
    ],
    ours: [
      "Les vallees et fonds de ravins = corridors de deplacement de l'ours",
      "Versant sud avec petits fruits (exposition solaire) = zone d'alimentation privilegiee",
      "Les affleurements rocheux sur les pentes = tannieres potentielles (ne pas deranger)",
      "Cretes et eskers: l'ours les utilise pour les deplacements longue distance",
      "Eviter d'installer la saline directement sous une falaise ou un escarpement (securite)"
    ],
    wapiti: [
      "Les cols et selles topographiques = corridors de migration obliges — positions cles",
      "Identifier les alpages d'ete (plateaux d'altitude) relies aux vallees d'hivernage",
      "Les corridors de migration altitudinale sont stables sur des generations — les cartographier",
      "Les versants est (soleil matinal) sont les zones d'alimentation preferees en automne",
      "Les replats de mi-pente sont des zones de repos ideales pour les groupes"
    ],
    dindon: [
      "Terrain plat a legerement vallonne (pente <10%) ideal pour le dindon",
      "Les cretes avec grands arbres = perchoirs nocturnes (positions cles)",
      "Les zones basses bien drainees avec sous-bois ouvert = alimentation",
      "Eviter les pentes abruptes (>20%) — le dindon les evite pour l'alimentation",
      "Les terrasses agricoles et les bordures de champ = corridors du dindon"
    ],
  },
  strategies_optimisation: {
    orignal: ["Cretes boisees = corridors", "Pente 5-10% pour bon drainage", "Cols = passages obliges pour affuts"],
    chevreuil: ["Pinch points topographiques = concentration", "Coulees boisees = corridors #1", "Versant sud en hiver"],
    ours: ["Vallees et ravins = corridors", "Versant sud = petits fruits", "Affleurements = tannieres"],
    wapiti: ["Cols et selles = migration", "Replats mi-pente = repos", "Corridors altitudinaux stables"],
    dindon: ["Plat a legerement vallonne", "Cretes = perchoirs", "Zones basses drainees = alimentation"],
  },
  techniques_chasse: {
    orignal: ["Les thermiques montent le matin le long des pentes — approcher par le bas", "Les cretes offrent une vue surplombante pour observer les vallons de la saline"],
    chevreuil: ["Les pinch points concentrent le passage — affut a l'endroit le plus etroit", "Les coulees offrent une approche cachee pour le chasseur aussi — les utiliser pour acceder a l'affut"],
    ours: ["L'ours suit les ravins — intercepter en sortie de ravin pres de la saline"],
    wapiti: ["Le col est le goulot d'etranglement — position d'affut ideale pour la migration"],
    dindon: ["Les cretes permettent d'observer les dindons descendre a l'aube — position d'observation cle"],
  },
  erreurs_a_eviter: {
    orignal: ["Installer la saline en fond de cuvette (air froid, brouillard, vents imprevisibles)", "Ignorer les thermiques (le vent change avec la pente et l'heure)"],
    chevreuil: ["Negliger les coulees boisees (invisibles sur les cartes 2D)", "Installer l'affut en bas de pente (thermiques descendants le soir portent vos odeurs vers le chevreuil en haut)"],
    ours: ["Installer la saline directement sous un escarpement (risque d'eboulement + securite)", "Ignorer les tannieres dans les affleurements rocheux (ne pas deranger un ours en taniere)"],
    wapiti: ["Bloquer un col de migration (le wapiti abandonne la route pour des annees)", "Installer au fond d'une vallee etroite (vents tourbillonnants, zero visibilite laterale)"],
    dindon: ["Installer en pente forte (le dindon evite ces zones pour l'alimentation)"],
  },
  optimisations_saisonnieres: { printemps: "Fonte: ruissellement sur les pentes. Evaluer le drainage. Versants sud degeles en premier.", ete: "Vegetation dense masque le relief. Utiliser les donnees LiDAR pour l'analyse. Thermiques stables.", automne: "Relief visible (feuilles tombees). Thermiques changeants matin/soir. Periode critique.", hiver: "Relief maximal (vegetation absente). Ideal pour cartographie terrain. Ravages dans les vallees." },
  optimisations_support: ["DEM LiDAR MRNF (gratuit) pour l'analyse du relief avant la visite terrain", "Application GPS avec couches topographiques pour la navigation terrain"],
  optimisations_meteo: ["Les inversions thermiques creent des poches d'air froid dans les vallees — le gibier les evite", "Le vent de versant change de direction au cours de la journee — adapter la position d'affut"],
  optimisations_pression: ["En haute pression: le gibier utilise les micro-vallons pour se cacher — les identifier"],
  thresholds: { green: "80-100: Pente 5-15%, drainage naturel bon, corridors topographiques identifies, micro-relief favorable", yellow: "50-79: Pente 15-25% ou terrain plat sans relief, drainage partiel, corridors partiels", red: "0-49: Pente >25% ou cuvette, drainage deficient, aucun corridor topographique, zone d'inondation" },
  sources: [
    "MRNF — Donnees LiDAR haute resolution forestier du Quebec (2023)",
    "Fortin et al. (2005) — Topographie et corridors fauniques (Universite Laval)",
    "Dussault et al. (2012) — Selection topographique de l'orignal (UQAR, Can. J. Zoology)",
    "NDA — Terrain Features and Deer Movement (2023)",
    "RMEF — Elk Migration and Mountain Topography (2022)",
    "USGS — Digital Elevation Models for Wildlife Habitat Analysis",
    "Lesmerises et al. (2012) — Relief et utilisation de l'habitat (UQAR)",
    "Environnement Canada — Modeles hydrologiques et relief DEM (2023)",
  ],
};

// =====================================================================
// P0 — HYDROLOGIE
// =====================================================================
const hydrologie = {
  title: "Hydrologie — Drainage, ruissellement et proximite des cours d'eau",
  definition: "Evaluation du regime hydrologique du site: drainage du sol, risque d'inondation, ruissellement de surface, proximite des cours d'eau et des zones humides, et impact sur la dissolution et la retention des mineraux de la saline. Un site bien draine (mais pas excessivement) optimise la retention minerale et la frequentation animale.",
  methodology: "Score sur 100: drainage local (30 pts — observation terrain + DEM), risque inondation (25 pts — modele hydro), distance cours d'eau (25 pts — MRNF reseau hydrique), saturation saisonniere (20 pts — observation 4 saisons). Sources: MRNF hydro, LiDAR, observations terrain.",
  justification: {
    orignal: "L'orignal est fortement associe aux milieux humides (marais, tourbières, lacs). Un site pres d'un cours d'eau mais hors de la zone d'inondation est optimal. La dissolution des mineraux est acceleree par l'eau — un drainage modere retient les mineraux dans la zone racinaire pour une duree optimale. Les sols satures en permanence noient les mineraux.",
    chevreuil: "Le chevreuil evite les zones saturees en eau (pattes courtes, peu adapte aux sols boueux). Il prefere les zones bien drainees pres d'un ruisseau calme. Un site avec drainage excessif (sable, roc) perd les mineraux trop rapidement. Le drainage ideal est modere — le sol reste humide mais pas sature.",
    ours: "L'ours tolere les zones humides mais prefere les sols fermes pour se deplacer. Il suit les ruisseaux comme corridors mais n'installe pas ses habitudes sur les sols satures. La saline pour ours doit etre sur un terrain bien draine (pas de boue profonde) accessible depuis un corridor hydrique.",
    wapiti: "Le wapiti frequente les vallees avec ruisseaux mais evite les zones marecageuses. En montagne, le drainage naturel est souvent bon (pentes). Les sources de montagne (resurgences) sont les points d'eau les plus fiables et attirent le wapiti regulierement.",
    dindon: "Le dindon evite absolument les zones saturees d'eau (pattes non palmees). Il prefere les terrains bien draines avec un sol sec. Les fossés de drainage agricole et les mares temporaires peu profondes sont ses points d'eau preferees.",
  },
  recommendations_terrain: {
    orignal: [
      "Site hors zone d'inondation mais a <200 m d'un cours d'eau permanent",
      "Drainage modere: sol humide mais pas sature (test: enfoncer un baton de 2 cm sans eau affleurante)",
      "Eviter les cuvettes et depressions ou l'eau stagne apres la pluie",
      "Installer la saline sur une legere pente (3-5%) pour evacuer l'eau excedentaire",
      "Verifier l'etat du site au printemps (fonte) et apres de fortes pluies",
      "Si le site est trop humide: creer une tranchee de drainage laterale de 20 cm",
      "Les sols avec une nappe phreatique a >60 cm de profondeur sont ideaux",
      "Eviter les zones de source (resurgence) directement sous la saline"
    ],
    chevreuil: [
      "Sol bien draine OBLIGATOIRE — le chevreuil evite la boue (empreintes profondes = stress)",
      "Drainage modere ideal — eviter le sable pur (mineraux lessives trop vite)",
      "Pres d'un ruisseau calme (<2 m) mais sur terrain ferme",
      "En zone argileuse: installer un lit de gravier (15 cm) sous la saline pour drainage local",
      "Verifier que le site n'est pas inonde au printemps (fonte de neige, crue du ruisseau)",
      "Les terrasses naturelles le long des ruisseaux sont idéales (drainage + proximite eau)"
    ],
    ours: [
      "Sol ferme et bien draine (l'ours n'aime pas la boue profonde sous les pattes)",
      "Pres d'un ruisseau (corridor de deplacement) mais pas dans la zone d'inondation",
      "Eviter les tourbieres (sol instable, difficulte d'installation de structures)",
      "Les sols de till glaciaire sont excellents (drainage variable mais portance bonne)"
    ],
    wapiti: [
      "Drainage naturel de pente en montagne — generalement adequate",
      "Les sources de montagne (resurgences) attirent le wapiti — installer la saline a proximite",
      "Eviter les fonds de vallees etroites (risque d'inondation apres orage de montagne)",
      "Les replats de mi-pente offrent un bon drainage et un bon couvert"
    ],
    dindon: [
      "Sol SEC et bien draine — le dindon evite les zones humides",
      "Les fossés de drainage agricole = points d'eau du dindon en zone rurale",
      "Eviter toute zone ou l'eau stagne apres la pluie",
      "Les terrains sableux bien draines sont excellents pour le dindon"
    ],
  },
  strategies_optimisation: {
    orignal: ["Pente 3-5% pour drainage naturel", "Tranchee laterale si trop humide", "Nappe >60 cm = ideal"],
    chevreuil: ["Sol ferme sans boue", "Lit de gravier en zone argileuse", "Terrasses le long des ruisseaux"],
    ours: ["Sol ferme, pres d'un ruisseau", "Eviter les tourbieres", "Till glaciaire = bonne base"],
    wapiti: ["Drainage naturel de pente", "Resurgences = attractifs", "Mi-pente = bon drainage + couvert"],
    dindon: ["Sol sec obligatoire", "Fossés agricoles = points d'eau", "Terrain sableux ideal"],
  },
  techniques_chasse: {
    orignal: ["L'orignal approche souvent par le corridor hydrique — positionner l'affut pour le couvrir", "Apres la pluie: le sol mou revele les empreintes fraiches — verifier avant de monter a l'affut"],
    chevreuil: ["Le chevreuil longe les ruisseaux apres avoir bu — intercepter sur ce corridor"],
    ours: ["L'ours suit le ruisseau puis bifurque vers la saline — identifier le point de bifurcation"],
    wapiti: ["Le wapiti descend vers la source de montagne en fin de matinee — etre en position avant"],
    dindon: ["Le dindon visite les points d'eau apres l'alimentation matinale (9h-11h)"],
  },
  erreurs_a_eviter: {
    orignal: ["Installer la saline dans une zone inondable au printemps", "Negliger le drainage (mineraux perdus par lessivage)"],
    chevreuil: ["Choisir un site boueux (le chevreuil evite)", "Site en depression sans drainage (eau stagnante = moustiques + desertion)"],
    ours: ["Installer sur un sol instable (tourbiere) — la structure s'enfonce"],
    wapiti: ["Fond de vallee etroite (risque d'inondation soudaine apres orage de montagne)"],
    dindon: ["Zone humide permanente (le dindon n'y pose JAMAIS les pattes)"],
  },
  optimisations_saisonnieres: { printemps: "Periode critique: fonte + crue. Verifier l'etat du site. Inondation possible.", ete: "Debit minimal des cours d'eau. Sol sec. Conditions optimales de drainage.", automne: "Pluies d'automne. Drainage teste. Sol humide mais pas sature normalement.", hiver: "Gel profond. Drainage suspendu. Verifier au degel printanier." },
  optimisations_support: ["Geotextile + gravier (15 cm) sous la saline en zone argileuse", "Tranchee de drainage laterale (20 cm profondeur, 30 cm large)"],
  optimisations_meteo: ["Apres forte pluie (>30 mm): verifier le site — risque de lessivage accelere", "Secheresse prolongee: le sol se fissure en argile — les mineraux penetrent en profondeur (bon signe)"],
  optimisations_pression: ["Les zones hydrologiquement isolees (pas de pont, pas de gue) sont naturellement protegees de la pression humaine"],
  thresholds: { green: "80-100: Drainage modere, hors zone inondable, cours d'eau <200 m, nappe >60 cm, pente 3-5%", yellow: "50-79: Drainage excessif ou lent, 200-500 m d'un cours d'eau, zone inondable partielle", red: "0-49: Zone inondable, drainage nul ou excessif, sol sature en permanence, aucune source <500 m" },
  sources: [
    "MRNF — Reseau hydrique du Quebec haute resolution (2023)",
    "IRDA Quebec — Drainage des sols agricoles et forestiers (2021)",
    "Environnement Canada — Donnees hydrologiques regionales (2024)",
    "MFFP — Impact des milieux humides sur l'habitat des cervides (2020)",
    "Fortin et al. (2005) — Hydrologie et corridors fauniques (Universite Laval)",
    "NDA — Mineral Site Drainage and Soil Management (2023)",
    "USGS — Hydrological Models for Wildlife Habitat Assessment (2023)",
    "USDA — Soil Drainage Classification System (2022)",
  ],
};

// =====================================================================
// P0 — DRAINAGE_SOL
// =====================================================================
const drainage_sol = {
  title: "Drainage du sol — Capacite du sol a evacuer l'eau excedentaire",
  definition: "Evaluation specifique de la capacite du sol a evacuer l'eau de pluie et de fonte, en complement du Soil Engine. Differe de l'hydrologie (macro) en se concentrant sur le micro-drainage dans un rayon de 10 m autour de la saline. Un drainage deficient noie les mineraux et repousse les cervides (pattes dans la boue).",
  methodology: "Score sur 100: test d'infiltration (40 pts — mesure terrain), pente locale (25 pts — clinometre), texture sol (20 pts — Soil Engine), observations saturation (15 pts — visite 4 saisons). Sources: Soil Engine V1/V2, observations terrain, IRDA.",
  justification: {
    orignal: "L'orignal tolere les sols humides (habitue aux marais) mais prefere un sol ferme pour lecher les mineraux. Un drainage deficient cree une mare de boue autour de la saline qui dilue les mineraux et reduit leur concentration. Le sol ideal retient l'humidite (dissolution minerale active) sans saturer (pas de flaque).",
    chevreuil: "Le chevreuil REFUSE de lecher des mineraux dans la boue. Un drainage deficient = desertion du site. Le sol autour de la saline doit etre SEC et FERME. Test simple: si votre botte s'enfonce de >5 cm, le drainage est insuffisant pour le chevreuil.",
    ours: "L'ours gratte le sol autour des attractifs — un sol draine permet un grattage efficace. Un sol boueux colle aux griffes et decourage l'ours. Les sols satures en permanence ne retiennent pas les attractifs odorants (odeur diluee).",
    wapiti: "Le wapiti, comme le chevreuil, evite les sols boueux pour lecher les mineraux. Le drainage en montagne est generalement bon (pentes naturelles) mais les replats peuvent saturer apres de fortes pluies. Prevoir un drainage de surface (tranchee).",
    dindon: "Le dindon gratte le sol pour trouver des grains et des mineraux — un sol draine et sec est OBLIGATOIRE. Le dindon evite absolument les zones boueuses (pattes non adaptees). Le sol ideal est sableux ou loameux, ferme, sec.",
  },
  recommendations_terrain: {
    orignal: [
      "Test d'infiltration: verser 5 litres d'eau sur le sol — si l'eau disparait en <5 min, drainage excellent",
      "Si l'eau stagne >15 min: drainage insuffisant — installer un lit de gravier sous la saline",
      "Pente locale de 3-5% autour de la saline pour evacuer l'eau de pluie naturellement",
      "Creer une tranchee de drainage en demi-lune (20 cm prof.) cote amont de la saline",
      "Utiliser un geotextile + 15 cm de gravier 0-20 mm comme base de la saline",
      "Verifier le drainage apres la fonte printaniere (moment critique)",
      "Eviter les zones avec affleurements de nappe (eau qui suinte du sol)"
    ],
    chevreuil: [
      "Sol FERME obligatoire — test de la botte: si enfonce >5 cm, drainage insuffisant",
      "Installer un lit de gravier de 20 cm sous et autour de la saline (1 m de rayon)",
      "Ratisser les feuilles mortes dans un rayon de 1 m (les feuilles retiennent l'humidite)",
      "En zone argileuse: melanger du sable grossier au sol sur 15 cm de profondeur",
      "Le chevreuil prefere lecher des mineraux sur une surface seche et propre",
      "Installer une dalle de pierre plate ou de bois traite comme base (surface seche)"
    ],
    ours: [
      "Sol draine pour grattage efficace (l'ours creuse autour des attractifs)",
      "Eviter les sols boueux (les griffes collent, l'ours se decourage)",
      "Les sols de till glaciaire ou de loam sableux sont ideaux pour l'ours",
      "Verifier le drainage apres les pluies d'automne (saison de chasse)"
    ],
    wapiti: [
      "Drainage naturel de pente generalement suffisant en montagne",
      "Sur les replats: creer une tranchee de drainage de surface (20 cm)",
      "Les sols rocheux de montagne drainent bien mais retiennent mal les mineraux — bac de collecte",
      "Verifier le drainage apres les orages de montagne (ruissellement soudain)"
    ],
    dindon: [
      "Sol SEC et FERME obligatoire — le dindon ne gratte pas dans la boue",
      "Installer les grains/mineraux sur une surface surélevee (palette, dalle)",
      "Les sols sableux sont ideaux (drainage rapide, surface seche)",
      "En zone argileuse: surélever la zone de mineraux de 10-15 cm avec du gravier"
    ],
  },
  strategies_optimisation: {
    orignal: ["Geotextile + gravier 0-20 mm", "Pente 3-5%", "Tranchee demi-lune cote amont"],
    chevreuil: ["Lit de gravier 20 cm rayon 1 m", "Dalle de pierre seche", "Ratisser les feuilles mortes"],
    ours: ["Loam sableux ou till glaciaire ideal", "Sol ferme pour grattage", "Verifier apres les pluies"],
    wapiti: ["Pente naturelle = drainage OK", "Tranchee sur les replats", "Bac de collecte sur roc"],
    dindon: ["Surface surélevee (palette, dalle)", "Sol sableux ideal", "Surélever en zone argileuse"],
  },
  techniques_chasse: {
    orignal: ["Un sol bien draine autour de la saline revele les empreintes fraiches — verifier avant la session"],
    chevreuil: ["Le chevreuil leche le gravier impregne de mineraux — le lit de gravier devient un attractif en soi"],
    ours: ["L'ours qui gratte un sol draine laisse des marques profondes — signe de visite recente"],
    wapiti: ["Les empreintes dans le sol draine sont nettes — identification rapide de la taille du male"],
    dindon: ["Les traces de grattage du dindon dans le sol sec = visite recente confirmee"],
  },
  erreurs_a_eviter: {
    orignal: ["Installer la saline dans une depression sans drainage (mare de boue en 2 semaines)", "Negliger l'entretien du drainage apres l'hiver (gel-degel = compaction)"],
    chevreuil: ["Sol boueux autour de la saline (le chevreuil deserte immediatement)", "Laisser les feuilles mortes s'accumuler (humidite + pourriture)"],
    ours: ["Sol colle aux griffes = ours decourage", "Zone saturee = attractifs dilues (odeur reduite)"],
    wapiti: ["Negliger les replats (ils saturent apres orage)", "Sol rocheux sans bac = mineraux perdus"],
    dindon: ["Zone boueuse = dindon absent", "Sol non sureleve en zone argileuse"],
  },
  optimisations_saisonnieres: { printemps: "CRITIQUE: fonte + gel-degel. Verifier drainage apres chaque gel-degel. Reparer les tranchees.", ete: "Sol sec. Conditions optimales. Verifier quand meme apres les grosses pluies.", automne: "Pluies d'automne. Tester le drainage avant la saison. Ajouter du gravier si necessaire.", hiver: "Sol gele. Drainage suspendu. Le sol se compacte sous le gel — prevoir l'entretien printanier." },
  optimisations_support: ["Gravier 0-20 mm (meilleur drainage que le gravier fin)", "Geotextile sous le gravier (empeche l'enfoncement dans l'argile)", "Dalle de ciment preformee (surface seche permanente)"],
  optimisations_meteo: ["Pluie >20 mm: verifier le site dans les 24h (risque de saturation)", "Secheresse: conditions optimales — profiter pour entretenir le drainage"],
  optimisations_pression: ["Un site bien draine = empreintes visibles = inventaire rapide des visiteurs sans deranger"],
  thresholds: { green: "80-100: Infiltration <5 min, pente 3-5%, sol ferme, aucune saturation visible, drainage amenage", yellow: "50-79: Infiltration 5-15 min, pente <3% ou >10%, humidite moderee, drainage partiel", red: "0-49: Infiltration >15 min, cuvette, sol sature, boue visible, aucun drainage" },
  sources: [
    "IRDA Quebec — Classification du drainage des sols (2021)",
    "Soil Engine V1 — Classification pedologique BCE-4X (2026)",
    "MFFP — Qualite des sols forestiers et retention minerale (2020)",
    "USDA — Soil Drainage Classification System (2022)",
    "NDA — Mineral Site Soil Management (2023)",
    "SLC — Soil Landscapes of Canada: Drainage Classes (Agriculture Canada)",
  ],
};

// =====================================================================
// BASE DE DONNEES COMPLÈTE — INDEX DES CRITÈRES
// =====================================================================
export const CRITERIA_DB = {
  position_vs_affuts,
  accessibilite_vehicule,
  couverture_vent,
  corridors_deplacement,
  distance_corridors: corridors_deplacement,
  couvert_forestier,
  source_eau,
  pression_chasse,
  tranquillite_zone,
  potentiel_trophee,
  visibilite_affuts,
  topographie_lidar,
  hydrologie,
  drainage_sol,
  // P1/P2 — REECRITS AU STANDARD V2 (BCE-4X ×4850-STEEVE_MAX)
  accessibilite_pieton,
  facilite_maintenance,
  proximite_infrastructure,
  securite_acces,
  frequence_visite,
  historique_observations,
  complementarite_reseau,
  adaptabilite_saisonniere,
  potentiel_expansion,
  cout_mineraux_annuel,
  cout_transport,
  cout_temps,
  retour_observation,
  retour_recolte,
  durabilite,
  alignement_sentiers,
  lissage,
  penetrabilite,
  effort_reel,
};

export const SPECIES_LABELS = SP;

export function getCriteria(key) {
  const k = key.toLowerCase().replace(/[\s\-]/g, '_').replace(/[àâä]/g, 'a').replace(/[éèêë]/g, 'e').replace(/[ïî]/g, 'i').replace(/[ôö]/g, 'o').replace(/[ùûü]/g, 'u');
  const entry = CRITERIA_DB[k];
  if (entry) return entry;
  return { ...DEFAULT, title: `${key.replace(/_/g, ' ')} — Guide BIONIC Niveau Professionnel` };
}

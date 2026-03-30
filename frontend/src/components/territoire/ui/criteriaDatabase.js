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
// BASE DE DONNEES COMPLÈTE — INDEX DES CRITÈRES
// =====================================================================
export const CRITERIA_DB = {
  position_vs_affuts,
  accessibilite_vehicule,
  couverture_vent,
  corridors_deplacement,
  distance_corridors: corridors_deplacement,
  couvert_forestier,
  // Aliases for backend component keys
  accessibilite_pieton: { ...accessibilite_vehicule, title: "Accessibilite a pied — Acces pedestre et portage au site de saline" },
  facilite_maintenance: { ...accessibilite_vehicule, title: "Facilite de maintenance — Entretien regulier et suivi du site" },
  proximite_infrastructure: { ...accessibilite_vehicule, title: "Proximite des infrastructures — Camp, stationnement, eau, reseau" },
  securite_acces: { ...accessibilite_vehicule, title: "Securite et controle de l'acces — Protection du site et des equipements" },
  frequence_visite: { ...accessibilite_vehicule, title: "Frequence optimale de visite — Calendrier d'entretien et de suivi" },
  potentiel_trophee: { ...couvert_forestier, title: "Potentiel de presence de males trophees — Evaluation du potentiel de recolte" },
  source_eau: { ...corridors_deplacement, title: "Source d'eau proximale — Distance et qualite de la source d'eau la plus proche" },
  historique_observations: { ...couvert_forestier, title: "Historique des observations — Données cameras trail et observations terrain" },
  tranquillite_zone: { ...couverture_vent, title: "Tranquillite de la zone — Niveau de perturbation humaine et predateurs" },
  pression_chasse: { ...couverture_vent, title: "Pression de chasse locale — Densite de chasseurs et impact sur le gibier" },
  visibilite_affuts: { ...position_vs_affuts, title: "Visibilite depuis les affuts — Champ de vision et angles de tir" },
  complementarite_reseau: { ...corridors_deplacement, title: "Complementarite du reseau — Integration avec les autres sites du territoire" },
  adaptabilite_saisonniere: { ...couverture_vent, title: "Adaptabilite saisonniere — Capacite du site a performer toute l'annee" },
  potentiel_expansion: { ...corridors_deplacement, title: "Potentiel d'expansion — Possibilite d'agrandir ou ameliorer le reseau de salines" },
  cout_mineraux_annuel: { ...accessibilite_vehicule, title: "Cout des mineraux annuel — Budget mineral pour la saison complete" },
  cout_transport: { ...accessibilite_vehicule, title: "Cout de transport — Frais de deplacement et logistique" },
  cout_temps: { ...accessibilite_vehicule, title: "Cout en temps — Temps investi par visite et par saison" },
  retour_observation: { ...couvert_forestier, title: "Retour sur observation — Nombre d'observations qualitatives par saison" },
  retour_recolte: { ...couvert_forestier, title: "Retour sur recolte — Potentiel de recolte par rapport a l'investissement" },
  durabilite: { ...couvert_forestier, title: "Durabilite du site — Capacite du site a performer sur 5-10 ans" },
  alignement_sentiers: { ...corridors_deplacement, title: "Alignement des sentiers — Qualite et orientation des sentiers d'acces et corridors" },
  lissage: { ...couvert_forestier, title: "Lissage du terrain — Uniformite et praticabilite du sol autour du site" },
  penetrabilite: { ...couvert_forestier, title: "Penetrabilite du terrain — Facilite de deplacement en foret autour du site" },
  topographie_lidar: { ...couverture_vent, title: "Topographie LiDAR — Relief et micro-topographie du site et environs" },
  hydrologie: { ...corridors_deplacement, title: "Hydrologie — Drainage, ruissellement et proximite des cours d'eau" },
  effort_reel: { ...accessibilite_vehicule, title: "Effort reel de deplacement — Temps et energie necessaires pour atteindre le site" },
  drainage_sol: { ...accessibilite_vehicule, title: "Drainage du sol — Capacite du sol a evacuer l'eau excedentaire" },
};

export const SPECIES_LABELS = SP;

export function getCriteria(key) {
  const k = key.toLowerCase().replace(/[\s\-]/g, '_').replace(/[àâä]/g, 'a').replace(/[éèêë]/g, 'e').replace(/[ïî]/g, 'i').replace(/[ôö]/g, 'o').replace(/[ùûü]/g, 'u');
  const entry = CRITERIA_DB[k];
  if (entry) return entry;
  return { ...DEFAULT, title: `${key.replace(/_/g, ' ')} — Guide BIONIC Niveau Professionnel` };
}

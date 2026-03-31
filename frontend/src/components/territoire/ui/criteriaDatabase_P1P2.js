/**
 * GUIDE BIONIC — NIVEAU PROFESSIONNEL™ — CRITERES P1/P2
 * ======================================================
 * BCE-4X STEEVE-MAX — ZERO FICHE GENERIQUE — SEPARATION STRICTE PAR ESPECE
 * Fichier complementaire a criteriaDatabase.js
 *
 * 19 sous-criteres reecrits au STANDARD V2:
 *   - Definition unique + methodologie de scoring
 *   - Justification par espece (5 especes)
 *   - 8-15 recommandations terrain/espece
 *   - Strategies, techniques, erreurs, optimisations
 *   - Sources TOP-TIER obligatoires
 *
 * Especes: Orignal | Chevreuil | Ours noir | Wapiti | Dindon sauvage
 *
 * SOURCES NIVEAU 1: MFFP, UQAR, ULaval, UQAC, Parcs Canada, USGS, USDA
 * SOURCES NIVEAU 2: J. Wildlife Mgmt, Can. J. Zoology, Wildlife Soc. Bulletin
 * SOURCES NIVEAU 3: NDA, RMEF, NWTF, Bear Trust, QDMA
 * SOURCES NIVEAU 4: MSU Deer Lab, UGA Deer Lab, Alberta Fish & Wildlife
 */

// =====================================================================
// 1. ACCESSIBILITE A PIED — P1
// =====================================================================
export const accessibilite_pieton = {
  title: "Accessibilite a pied — Acces pedestre et portage au site de saline",
  definition: "Evaluation de la facilite d'acces pedestre au site de saline, incluant la distance de marche depuis le point de stationnement, le denivele cumule, la praticabilite du sentier en toute saison, la capacite de portage (blocs mineraux 20-25 kg), et le niveau de bruit genere lors de l'approche. Un acces pedestre silencieux et rapide est determinant pour minimiser le derangement faunique lors des visites d'entretien et de chasse.",
  methodology: "Score sur 100 points: distance de marche parking-site (35 pts — GPS), denivele cumule (25 pts — DEM LiDAR), qualite du sentier (20 pts — type de surface, largeur, obstacles), niveau sonore de l'approche (20 pts — evaluation terrain substrat). Donnees: traces GPS, MNT LiDAR MRNF, observations terrain 4 saisons.",
  justification: {
    orignal: "L'orignal detecte les vibrations au sol a 200+ m et les bruits de pas a 150 m. Un sentier pedestre de 300-500 m sur substrat mou (mousse, terre humique) permet une approche quasi-silencieuse. Le portage de blocs de 20-25 kg sur plus de 800 m devient physiquement eprouvant et augmente le depot d'odeurs corporelles (transpiration). Les orignaux tolerent mieux une approche breve et directe qu'un portage long et laborieux.",
    chevreuil: "Le chevreuil memorise les schemas de derangement. Un acces pedestre regulier sur le meme sentier a la meme heure cree un pattern que le chevreuil integre. Le sentier d'acces NE DOIT PAS croiser un sentier de chevreuil identifie — le depot d'odeur humaine sur un corridor de deplacement provoque une desertion de 48-72 h. Distance optimale de portage: 200-400 m maximum.",
    ours: "L'acces pedestre en zone ours impose des mesures de securite strictes: deplacement en duo, spray anti-ours accessible, sifflet ou clochette pour signaler sa presence. Le portage de 40-60 kg d'attractifs (melasse, mais) sur plus de 500 m en zone ours est deconseille — risque de rencontre surprise. Privilegier un acces court (<300 m) avec visibilite degagee.",
    wapiti: "Le wapiti en montagne impose souvent des acces pedestres longs (500-1500 m) avec denivele significatif (100-300 m). Le portage de blocs mineraux de 25 kg en altitude requiert un conditionnement physique adapte. Utiliser un sac a cadre externe (type Outdoorsman) pour repartir le poids. Les sentiers doivent eviter les cretes exposees ou le wapiti repere les silhouettes humaines.",
    dindon: "Le dindon detecte le moindre bruit de pas a 50+ m. L'approche pedestre doit etre ABSOLUMENT silencieuse sur les derniers 100 m. Le portage est leger (grains, mineraux: 5-10 kg par visite), mais le sentier doit permettre une approche furtive predawn (avant le lever du soleil, dans l'obscurite). Privilegier un sentier sur substrat mou (herbe, mousse) plutot que gravier ou feuilles seches.",
  },
  recommendations_terrain: {
    orignal: [
      "Amenager un sentier pedestre de 1.5 m de large sur substrat mou (mousse, terre humique)",
      "Distance optimale parking-site: 300-500 m (compromis silence/effort physique)",
      "Installer des marches en bois aux passages en pente (>15%) pour securiser le portage",
      "Retirer les branches mortes et debris au sol sur toute la longueur du sentier",
      "Creer un depot de materiel intermediaire a mi-chemin (boite etanche sureleve) pour les longs portages",
      "Marquer le sentier avec des reflecteurs IR pour navigation predawn sans lampe frontale",
      "Amenager un reposoir (rondins plats) a chaque 200 m pour deposer le sac de portage",
      "Eviter les zones humides (bruit de succion) — contourner avec des caillebotis en bois",
      "Installer un pont de rondins aux traversees de ruisseaux (stabilite + silence)",
      "Le sentier doit contourner les zones de brout de l'orignal (cornouiller, amélanchier)"
    ],
    chevreuil: [
      "Distance maximale de portage: 400 m (au-dela, le depot d'odeur est excessif)",
      "Sentier pedestre SEPARE du sentier de chevreuil — ne jamais croiser un corridor identifie",
      "Substrat: mousse, copeaux de bois ou tapis de caoutchouc aux points bruyants",
      "Approche predawn obligatoire par un chemin qui ne croise aucune zone de grattage (scrape)",
      "Porter des bottes en caoutchouc (anti-odeur) pour le portage",
      "Utiliser un sac a dos anti-odeur (charbon actif) pour le transport des blocs",
      "Ne JAMAIS emprunter le sentier de portage en soiree (heures actives du chevreuil)",
      "Creer un sentier sinueux plutot que droit (le chevreuil surveille les lignes droites)",
      "Installer un depot de blocs de reserve a 200 m du site pour reduire les visites",
      "Limiter les allers-retours a 1 par visite — tout mouvement supplementaire est detecte"
    ],
    ours: [
      "Sentier large (2 m) et degage — visibilite a 30+ m devant soi en permanence",
      "Distance maximale de portage: 300 m en zone ours (securite de retrait rapide)",
      "Deplacement en DUO obligatoire — ne jamais porter seul en zone ours",
      "Spray anti-ours fixe a la ceinture, pas dans le sac (accessible en <3 secondes)",
      "Faire du bruit regulier en approche (voix, sifflet) sauf les 50 derniers metres",
      "Verifier les signes de presence recente (empreintes, excrements) sur le sentier AVANT d'avancer",
      "Eviter les sentiers en sous-bois dense ou la visibilite est <10 m",
      "Portage en contenants metalliques anti-ours (les sacs plastique attirent les ours curieux)",
      "Installer une camera trail cellulaire a l'entree du sentier pour verifier la presence d'ours avant la visite"
    ],
    wapiti: [
      "Sentier en lacets pour les pentes >15% (reduire l'effort de portage de 40%)",
      "Installer des barres anti-erosion en bois tous les 15 m sur les pentes",
      "Utiliser un sac a cadre externe (Outdoorsman, Mystery Ranch) pour les portages de 25+ kg",
      "Prevoir des batons de marche pour la stabilite en terrain montagneux avec charge",
      "Distance de portage typique en zone wapiti: 500-1500 m — conditionner physiquement",
      "Creer un depot intermediaire a mi-parcours (caisse metallique verrouillee contre les ours)",
      "Le sentier doit eviter les cretes et les zones exposees (le wapiti surveille les silhouettes en hauteur)",
      "Utiliser les anciennes pistes forestieres comme base de sentier pedestre",
      "Approche par le fond de vallee le matin (thermiques montants dispersent l'odeur vers le haut)"
    ],
    dindon: [
      "Sentier court (50-150 m) car les mineraux pour dindon sont legers (5-10 kg)",
      "Substrat SILENCIEUX obligatoire sur les 100 derniers metres (mousse, herbe, copeaux)",
      "Sentier d'approche predawn: marquer avec des reflecteurs UV ou IR au sol",
      "Eviter les feuilles mortes au sol — les ratisser en automne sur toute la longueur",
      "Le sentier ne doit PAS passer sous un arbre de perchoir de dindon (risque de les effrayer au depart)",
      "Installer le sentier en contrebas par rapport aux perchoirs (approche invisible depuis le haut)",
      "En zone agricole: utiliser le bord de champ comme sentier naturel",
      "Prevoir un espace d'attente silencieux a 30 m du blind pour se preparer avant l'aube"
    ],
  },
  strategies_optimisation: {
    orignal: ["Sentier sur substrat mousse/humique pour silence", "Depot intermediaire tous les 200 m", "Reflecteurs IR pour predawn", "Caillebotis aux zones humides"],
    chevreuil: ["Sentier SEPARE des corridors chevreuil", "Bottes caoutchouc + sac anti-odeur", "Depot de blocs de reserve a 200 m", "Portage uniquement en mi-journee"],
    ours: ["Duo obligatoire", "Sentier large et degage", "Camera cellulaire a l'entree", "Contenants metalliques anti-ours"],
    wapiti: ["Lacets en pente >15%", "Cadre de portage externe", "Depot intermediaire verrouille", "Approche par fond de vallee le matin"],
    dindon: ["Sentier court 50-150 m", "Substrat silencieux obligatoire", "Approche predawn marquee IR", "Espace d'attente a 30 m du blind"],
  },
  techniques_chasse: {
    orignal: ["Approche predawn: quitter le parking 90 min avant l'aube", "Marcher lentement (1 pas toutes les 3 secondes) sur les 100 derniers metres", "Ne porter que l'equipement essentiel le jour de la chasse (pas de portage de blocs)"],
    chevreuil: ["Le chevreuil detecte les pas dans les feuilles a 80 m — bottes souples obligatoires", "Chaque visite de portage laisse une trace olfactive de 6-12 h — visiter en mi-journee uniquement", "Approche du tree stand par le sentier dedié, jamais par le corridor de chevreuil"],
    ours: ["En zone ours: siffler ou parler en marchant (sauf les 50 derniers metres)", "Portage de jour uniquement — JAMAIS d'approche predawn seul en zone ours", "Si signes de presence d'ours frais sur le sentier: faire demi-tour et revenir un autre jour"],
    wapiti: ["Portage matinal (6h-9h) avant la chaleur pour reduire la transpiration", "En altitude: hydratation importante pour maintenir la performance physique", "Descente: attention aux genoux avec 25 kg — batons de marche obligatoires"],
    dindon: ["Approche ULTRA-silencieuse: pas de feuilles, pas de branches, pas de tissu frottant", "Le dindon sur le perchoir entend les pas a 100 m — arriver avant qu'il ne s'eveille", "Dernier mouvement: s'installer dans le blind sans bruit, puis immobilite totale 15 min"],
  },
  erreurs_a_eviter: {
    orignal: ["Portage par temps chaud (transpiration = depot d'odeur excessif)", "Sentier qui traverse une sapiniere dense (branches qui craquent)", "Negliger l'entretien du sentier (branches tombees = bruit)"],
    chevreuil: ["Croiser un sentier de chevreuil avec le sentier d'acces", "Utiliser des bottes de cuir (odeur residuelle de 12+ h)", "Porter les blocs en sac plastique bruyant"],
    ours: ["Portage seul en zone ours", "Sentier en sous-bois dense sans visibilite", "Laisser le spray anti-ours dans le sac (inaccessible en urgence)"],
    wapiti: ["Portage sans hydratation suffisante en altitude (epuisement physique)", "Emprunter une crete exposee avec un sac volumineux (silhouette visible)", "Negliger les barres anti-erosion (sentier se degrade rapidement en pente)"],
    dindon: ["Marcher sur les feuilles seches au sol (bruit detecte a 50+ m)", "Approche avec une lampe frontale blanche (le dindon voit les couleurs)", "Passer sous un arbre de perchoir (le dindon decolle en panique et deserte le secteur)"],
  },
  optimisations_saisonnieres: { printemps: "Sol mou apres la fonte — conditions ideales pour le portage silencieux. Reparer les dommages hivernaux au sentier. Verifier les ponts de rondins.", ete: "Vegetation dense — debroussailler le sentier. Sol sec = branches cassantes. Arroser le sentier sec si possible avant une session.", automne: "Feuilles mortes = bruit maximal. Ratisser le sentier avant la saison. Copeaux de bois aux zones critiques.", hiver: "Raquettes ou skis. Sentier dame permanent. Le gel rend le sol bruyant — neige fraiche = silence." },
  optimisations_support: ["Sac a cadre externe pour portage >15 kg (Outdoorsman, Eberlestock)", "Bottes en caoutchouc anti-odeur (Muck Boots, LaCrosse Alpha)", "Reflecteurs IR au sol tous les 30 m pour navigation predawn", "Copeaux de bois ou tapis de mousse aux points bruyants du sentier"],
  optimisations_meteo: ["Pluie legere: sol mou = portage silencieux (session optimale)", "Apres gel-degel: sol crouteux et bruyant — eviter", "Vent fort: couvre les bruits de pas — session favorable", "Neige fraiche: portage ultra-silencieux (conditions ideales)"],
  optimisations_pression: ["En zone haute pression: sentier exclusif obligatoire (pas de partage avec d'autres chasseurs)", "Varier les heures d'approche pour eviter les patterns predictibles", "En zone publique: utiliser des sentiers alternatifs pour eviter les conflits d'acces"],
  thresholds: { green: "80-100: Distance <400 m, denivele <50 m, sentier amenage, substrat silencieux, portage <15 min", yellow: "50-79: Distance 400-800 m, denivele 50-150 m, sentier partiel, portage 15-30 min", red: "0-49: Distance >800 m, denivele >150 m, hors-sentier, portage >30 min, bruit excessif" },
  sources: [
    "MFFP Quebec — Normes d'amenagement des sentiers en milieu forestier (2022)",
    "SEPAQ — Guide de portage et acces aux sites de chasse (2023)",
    "NDA — Mineral Site Access and Scent Management (2023)",
    "Mississippi State University Deer Lab — Hunter Access Impact on Deer Behavior (2021)",
    "MRNF — Modele numerique de terrain LiDAR (resolution 1 m) pour analyse de denivele",
    "Dussault et al. (2005) — Reponse comportementale de l'orignal aux perturbations humaines (UQAR)",
    "University of Georgia Deer Lab — Human Scent Deposition and Deer Avoidance (2020)",
    "Bear Trust International — Hiking Safety in Black Bear Country (2022)",
  ],
};

// =====================================================================
// 2. FACILITE DE MAINTENANCE — P1
// =====================================================================
export const facilite_maintenance = {
  title: "Facilite de maintenance — Entretien regulier et suivi du site de saline",
  definition: "Evaluation de la facilite avec laquelle le site de saline peut etre entretenu tout au long de la saison: remplacement des blocs mineraux, nettoyage de la zone de lechage, verification des equipements (cameras trail, affuts), debroussaillage des corridors de tir, et inspection des structures (tree stands, ground blinds). Un site facile a entretenir recoit plus de visites d'entretien, ce qui maximise la frequentation animale et la duree de vie des equipements.",
  methodology: "Score sur 100: temps moyen d'entretien par visite (30 pts), nombre d'operations requises (25 pts — checklist standardisee), accessibilite des composantes (25 pts — hauteur, distance, obstacles), frequence d'entretien requise (20 pts — hebdomadaire vs mensuelle). Donnees: carnet de terrain, logs cameras trail, observations saisonnieres.",
  justification: {
    orignal: "Le site d'orignal necessite un entretien modere: remplacement des blocs de 20-25 kg toutes les 4-6 semaines en saison active (mai-octobre), nettoyage des debris vegetaux autour de la zone de lechage, et verification du tree stand (sangles, vis, plateforme). L'orignal tolere mieux les visites d'entretien breves (<20 min) que les sessions prolongees. Un site mal entretenu (bloc mineral epuise, affut instable) perd 60% de sa frequentation en 2 semaines.",
    chevreuil: "Le chevreuil exige un entretien plus frequent mais plus delicat: blocs de 10-15 kg remplaces toutes les 3-4 semaines, ratissage des feuilles mortes dans un rayon de 1 m, et verification des corridors de tir (repousse vegetale rapide en ete). Chaque visite d'entretien doit durer <10 min pour minimiser le depot d'odeurs. Le chevreuil deserte un site ou le bloc mineral est vide pendant plus de 7 jours.",
    ours: "L'entretien en zone ours est le plus exigeant en termes de securite: verification des contenants anti-ours, remplacement des attractifs (40-60 kg de melasse, mais), inspection des cameras trail (souvent deplacees par les ours). Les visites d'entretien DOIVENT se faire en duo, en plein jour (11h-14h). Un site ours mal entretenu attire les ours conditionnes qui deviennent dangereux.",
    wapiti: "Le site de wapiti en montagne pose des defis logistiques d'entretien: acces pedestre long (500-1500 m), transport de blocs lourds en altitude, et exposition aux intemperies (vent, neige precoce). L'entretien est moins frequent (toutes les 6-8 semaines) car le wapiti tolere des blocs partiellement dissous. Prevoir un depot intermediaire pour stocker du materiel et reduire les portages.",
    dindon: "L'entretien du site de dindon est le plus simple: remplissage de grains/mineraux legers (5-10 kg), verification du ground blind (etat du camouflage), et debroussaillage minimal. Frequence: toutes les 2-3 semaines au printemps (saison active). Le dindon s'habitue rapidement a un site regulierement entretenu — la constance est plus importante que la frequence.",
  },
  recommendations_terrain: {
    orignal: [
      "Standardiser une checklist d'entretien: bloc mineral, affut, cameras, corridors, sentier d'acces",
      "Prevoir un kit d'entretien permanent au depot intermediaire (cle a molette, sangles, vis)",
      "Remplacer le bloc mineral AVANT qu'il ne soit completement dissous (garder 20% minimum)",
      "Inspecter les sangles du tree stand a chaque visite (degradation UV/gel)",
      "Debroussailler les corridors de tir au secateur silencieux (pas de tronconneuse)",
      "Nettoyer la zone de lechage: retirer les debris, feuilles, branches tombees",
      "Verifier les batteries des cameras trail (autonomie typique: 3-6 mois)",
      "Documenter chaque visite: date, heure, meteo, etat du bloc, observations",
      "Limiter la duree d'entretien a 20 min maximum par visite",
      "Planifier les visites en mi-journee (10h-14h) quand l'orignal est couche"
    ],
    chevreuil: [
      "Visite d'entretien <10 min — chronometrer et optimiser chaque geste",
      "Remplacer le bloc mineral des qu'il atteint 30% de sa taille initiale",
      "Ratisser les feuilles mortes dans un rayon de 1 m autour de la zone de lechage",
      "Verifier la repousse vegetale dans les corridors de tir toutes les 3 semaines en ete",
      "Porter des gants en latex lors de la manipulation des blocs (reduire le depot d'odeur)",
      "Utiliser un secateur a main (silencieux) pour les branches genantes — jamais de tronconneuse",
      "Eviter les visites d'entretien en soiree (16h-20h) — heures actives du chevreuil",
      "Stocker 2-3 blocs de rechange au depot pour reduire les visites logistiques",
      "Verifier les mock scrapes et frottoirs artificiels — les renouveler si necessaire",
      "Installer un panneau d'alerte anti-braconnage si le site est en zone publique"
    ],
    ours: [
      "Visite d'entretien en DUO uniquement — jamais seul en zone ours",
      "Horaire d'entretien: 11h-14h exclusivement (l'ours est moins actif en milieu de journee)",
      "Inspecter les contenants anti-ours: verrous, chaines, integrite du metal",
      "Verifier si les cameras trail ont ete deplacees ou endommagees par un ours",
      "Remplacer les attractifs odorants toutes les 2-3 semaines (la puissance olfactive diminue)",
      "Nettoyer les griffures d'ours sur les structures — evaluer les dommages",
      "Spray anti-ours a la ceinture pendant TOUTE la duree de l'entretien",
      "Ne JAMAIS manger ou laisser des emballages alimentaires pendant l'entretien",
      "Documenter les signes de presence d'ours: empreintes, excrements, griffures fraiches"
    ],
    wapiti: [
      "Entretien toutes les 6-8 semaines (le wapiti tolere les blocs partiellement dissous)",
      "Prevoir un depot intermediaire a mi-parcours pour stocker du materiel",
      "Inspecter le tree stand avant chaque saison (degats de vent, neige, gel)",
      "Debroussailler les corridors de tir en ete (la vegetation pousse vite en altitude)",
      "Verifier les barres anti-erosion du sentier d'acces apres chaque gros orage",
      "Remplacer les blocs mineraux en debut de saison (septembre) quand les wapitis sont actifs",
      "Installer un kit d'outils au depot intermediaire pour eviter de les transporter a chaque fois",
      "Documenter l'usure du bloc: taux de dissolution = indicateur de frequentation"
    ],
    dindon: [
      "Remplissage de grains/mineraux toutes les 2-3 semaines au printemps",
      "Verifier le camouflage du ground blind: branches fraiches, filet intact",
      "Nettoyer l'interieur du blind (debris, insectes, humidite)",
      "Renouveler les branches de camouflage si elles ont seche (couleur differente = alerte)",
      "Verifier les appelants (decoys): position naturelle, proprete, stabilite",
      "Tester les appels (box call, slate call) et les maintenir seches",
      "En zone agricole: coordonner avec le proprietaire pour l'acces",
      "Documenter les heures de visite du dindon via les cameras trail"
    ],
  },
  strategies_optimisation: {
    orignal: ["Checklist standardisee par visite", "Kit d'entretien au depot intermediaire", "Bloc remplace a 20% restant", "Entretien <20 min"],
    chevreuil: ["Entretien <10 min chrono", "Gants latex obligatoires", "Blocs de rechange stockes", "Mi-journee exclusivement"],
    ours: ["Duo obligatoire", "11h-14h exclusivement", "Contenants anti-ours verifies", "Spray a la ceinture"],
    wapiti: ["Frequence 6-8 semaines", "Depot intermediaire equipe", "Entretien en debut de saison", "Dissolution = indicateur de frequentation"],
    dindon: ["Toutes les 2-3 semaines au printemps", "Camouflage renouvele", "Decoys verifies", "Appels testes et secs"],
  },
  techniques_chasse: {
    orignal: ["Un site bien entretenu produit 3x plus d'observations camera qu'un site neglige", "Le bloc mineral frais genere un pic de visites dans les 48 h suivant le remplacement"],
    chevreuil: ["Le chevreuil revient systematiquement dans les 24 h apres un remplacement de bloc silencieux", "Un site propre et degage permet de lire les indices au sol (empreintes, grattages)"],
    ours: ["Un ours qui trouve regulierement des attractifs frais developpe un pattern de visite predictible", "Les cameras trail montrent que l'ours visite plus souvent les sites bien entretenus (odeurs fraiches)"],
    wapiti: ["Le wapiti memorise les sites de lechage productifs — un site entretenu est visite par des generations successives", "Un bloc mineral frais en pre-rut attire les males en recherche de sodium pour la croissance du panache"],
    dindon: ["Le dindon revient quotidiennement a un site regulierement approvisionne en grains", "Un blind bien entretenu devient invisible pour le dindon apres 2 semaines d'habituation"],
  },
  erreurs_a_eviter: {
    orignal: ["Laisser le bloc mineral s'epuiser completement (perte de fidelite du site)", "Entretien prolonge (>30 min) — depot d'odeur excessif", "Utiliser des outils bruyants (tronconneuse, perceuse)"],
    chevreuil: ["Entretien en soiree (perturbation aux heures actives)", "Manipuler les blocs sans gants (odeur humaine sur le mineral)", "Laisser les feuilles mortes s'accumuler (humidite, moisissure)"],
    ours: ["Entretien seul en zone ours", "Laisser des emballages alimentaires sur le site", "Negliger l'inspection des contenants anti-ours (ours conditionne = danger)"],
    wapiti: ["Reporter l'entretien en debut de saison (le wapiti cherche activement les mineraux en pre-rut)", "Negliger les sentiers d'acces en montagne (degradation rapide)"],
    dindon: ["Laisser le blind sans renouvellement de camouflage (branches seches = detection)", "Oublier de verifier les decoys (position non naturelle = mefiance)"],
  },
  optimisations_saisonnieres: { printemps: "Entretien complet post-hiver: remplacement des blocs, reparation des structures, debroussaillage general. Inspection du tree stand apres le gel-degel.", ete: "Debroussaillage frequent des corridors de tir (croissance vegetale rapide). Verification des batteries de cameras trail.", automne: "Saison active. Entretien minimal et rapide. Remplacement de bloc uniquement. Aucune modification structurelle.", hiver: "Retrait des tree stands portables pour inspection. Stockage des materiaux. Planification de la saison suivante." },
  optimisations_support: ["Kit d'entretien complet au depot: cle a molette, sangles, vis inox, secateur, batteries CR123A", "Sac de transport etanche pour les blocs mineraux (anti-odeur + anti-humidite)", "Carnet de terrain standardise avec checklist pre-imprimee", "Application mobile de suivi des visites et photos datees"],
  optimisations_meteo: ["Pluie legere: entretien silencieux ideal (le bruit de la pluie couvre les activites)", "Apres grosse pluie: verifier le drainage et les dommages aux sentiers", "Gel: attention aux sangles gelees du tree stand (fragilisees)", "Canicule: reporter l'entretien (transpiration = odeur excessive)"],
  optimisations_pression: ["En zone haute pression: entretien rapide et discret pour ne pas alerter les chasseurs voisins", "Varier les jours d'entretien pour ne pas creer un pattern observable", "En zone publique: installer un cadenas sur les equipements fixes"],
  thresholds: { green: "80-100: Entretien <15 min, toutes composantes accessibles, checklist complete, equipement en bon etat", yellow: "50-79: Entretien 15-30 min, certaines composantes difficiles d'acces, reparations mineures necessaires", red: "0-49: Entretien >30 min, composantes inaccessibles ou endommagees, reparations majeures requises" },
  sources: [
    "SEPAQ — Guide de gestion et entretien des sites de chasse (2023)",
    "NDA — Mineral Site Maintenance Best Practices (2024)",
    "MFFP Quebec — Normes d'amenagement des sites de piegeage et chasse (2022)",
    "QDMA (archives) — Year-Round Mineral Site Management",
    "Bear Trust International — Bear-Proofing Equipment and Site Maintenance (2022)",
    "Wisconsin DNR — Hunting Site Management Guide (2024)",
    "RMEF — Elk Mineral Site Longevity Studies (2023)",
    "NWTF — Turkey Hunting Site Preparation and Maintenance (2024)",
  ],
};

// =====================================================================
// 3. PROXIMITE DES INFRASTRUCTURES — P2
// =====================================================================
export const proximite_infrastructure = {
  title: "Proximite des infrastructures — Camp, stationnement, eau, reseau cellulaire",
  definition: "Evaluation de la distance entre le site de saline et les infrastructures de support: camp de chasse, stationnement securise, source d'eau potable, reseau cellulaire (pour cameras trail cellulaires et securite), et route praticable la plus proche. La proximite des infrastructures influence directement la logistique des operations, la securite du chasseur, et la capacite de surveillance a distance du site.",
  methodology: "Score sur 100: distance camp/stationnement (30 pts — GPS), couverture cellulaire (25 pts — test signal 4G/LTE), source d'eau potable (20 pts — distance + qualite), route praticable (15 pts — type et distance), electricite/generateur (10 pts — disponibilite). Sources: cartes topographiques MRNF, tests de couverture cellulaire terrain, reseau routier forestier.",
  justification: {
    orignal: "En zone de chasse a l'orignal au Quebec, le camp de chasse est souvent a 5-30 km du site de saline. Les cameras trail cellulaires (Spypoint, Stealth Cam) necessitent un signal LTE minimal pour transmettre les photos. Un camp a <5 km permet un aller-retour rapide (30 min VTT) pour verifier le site sans y passer la nuit. L'orignal se chasse souvent dans des zones reculees ou la couverture cellulaire est limitee.",
    chevreuil: "Le chevreuil se chasse frequemment en zone periurbaine ou semi-agricole, ou les infrastructures sont generalement proches. Un stationnement a <200 m du site permet des visites rapides et discretes. La couverture cellulaire est souvent bonne, permettant l'utilisation optimale des cameras cellulaires. En zone eloignee, le camp de chasse est rarement a plus de 10 km du site.",
    ours: "La proximite d'un camp est CRITIQUE en zone ours pour la securite: communication d'urgence (cellulaire ou satellite), premier soins, et retrait rapide en cas d'incident. Un camp a <10 km est recommande. Les cameras trail cellulaires sont essentielles pour verifier la presence d'ours AVANT de se deplacer au site.",
    wapiti: "Le wapiti en montagne impose des infrastructures eloignees: camps temporaires, refuges de montagne, ou bivouacs. La couverture cellulaire est souvent absente en altitude — prevoir un appareil satellite (inReach, SPOT) pour la securite. Le stationnement VTT peut etre a 5-10 km du site en terrain montagneux.",
    dindon: "Le dindon se chasse souvent en zone agricole proche des routes et habitations. Les infrastructures sont generalement accessibles: stationnement sur le rang, eau potable au domicile du proprietaire, couverture cellulaire complete. La proximite facilite les visites frequentes necessaires au suivi du ground blind.",
  },
  recommendations_terrain: {
    orignal: [
      "Identifier la couverture cellulaire au site de saline AVANT l'installation (test signal 4G)",
      "Si pas de signal: prevoir des cameras trail SD avec releve manuel toutes les 2-4 semaines",
      "Camp de chasse a <10 km du site de saline pour un aller-retour VTT en <1 h",
      "Identifier la source d'eau potable la plus proche (lac, ruisseau filtre, puits)",
      "Installer un point de repere GPS permanent (reflecteur ou balise) a l'entree du site",
      "Prevoir un telephone satellite (inReach, SPOT) si la couverture cellulaire est absente",
      "Identifier le chemin d'evacuation le plus court vers une route carrossable",
      "Coordonner avec le club de chasse local pour le partage des infrastructures (camp, sentiers)",
      "Installer un panneau avec les coordonnees GPS du camp et le numero d'urgence au site de saline"
    ],
    chevreuil: [
      "Stationnement a <200 m du site pour des visites rapides et discretes",
      "Tester la couverture cellulaire sur tout le trajet parking-site",
      "Installer des cameras trail cellulaires (Spypoint LINK, Stealth Cam Connect) si signal LTE disponible",
      "En zone periurbaine: coordonner avec les voisins pour eviter les conflits d'acces",
      "Identifier une source d'eau pour le nettoyage de l'equipement post-session",
      "Prevoir un eclairage solaire discret au stationnement pour les retours en soiree",
      "En zone ZEC/SEPAQ: verifier les regles d'acces aux infrastructures communes",
      "Installer un panneau de signalisation discret a l'entree du stationnement"
    ],
    ours: [
      "Communication d'urgence obligatoire: cellulaire ou telephone satellite (inReach Garmin)",
      "Camp de chasse a <10 km — retrait rapide obligatoire en cas d'incident",
      "Kit de premiers soins complet au camp ET dans le sac de portage",
      "Identifier l'hopital ou clinique la plus proche (route + temps de trajet)",
      "Cameras trail cellulaires pour verifier la presence d'ours AVANT la visite",
      "Trousse de survie au camp: flare, miroir de signalisation, sifflet",
      "En zone isolee: prevenir quelqu'un de votre itineraire et heure de retour prevue",
      "Source d'eau potable identifiee pour les seances prolongees sur le site"
    ],
    wapiti: [
      "Appareil satellite (inReach, SPOT) obligatoire en zone montagne sans couverture cellulaire",
      "Camp temporaire ou bivouac a <5 km du site en altitude",
      "Identifier les refuges de montagne existants (cabanes forestieres, shelters)",
      "Prevoir un generateur ou panneaux solaires portables pour recharger les equipements",
      "Carte topographique papier en complement du GPS (batteries limitees en froid)",
      "Source d'eau: ruisseaux de montagne avec filtre (LifeStraw, Katadyn)",
      "Stationnement VTT securise a basse altitude avec cable antivol"
    ],
    dindon: [
      "En zone agricole: utiliser les infrastructures du proprietaire (stationnement, eau, electricite)",
      "Couverture cellulaire generalement complete — cameras cellulaires recommandees",
      "Stationnement discret hors de vue des zones de parade du dindon",
      "Identifier un endroit sec et couvert pour stocker le materiel entre les sessions",
      "En zone publique: verifier la disponibilite des stationnements avant la saison"
    ],
  },
  strategies_optimisation: {
    orignal: ["Camp <10 km du site", "Test signal 4G avant installation", "Telephone satellite en zone isolee", "GPS permanent a l'entree du site"],
    chevreuil: ["Stationnement <200 m", "Cameras cellulaires si signal LTE", "Eclairage solaire au parking", "Coordination avec voisins"],
    ours: ["Communication d'urgence obligatoire", "Kit premiers soins double (camp + sac)", "Cameras cellulaires pour verification avant visite", "Hopital le plus proche identifie"],
    wapiti: ["Satellite inReach/SPOT obligatoire", "Camp temporaire <5 km", "Panneaux solaires portables", "Carte topo papier en backup"],
    dindon: ["Infrastructures agricoles existantes", "Cameras cellulaires", "Stockage materiel sur place", "Stationnement discret"],
  },
  techniques_chasse: {
    orignal: ["Verifier les cameras cellulaires depuis le camp AVANT de se deplacer au site", "Un camp proche permet des sessions matinales et vesperales le meme jour"],
    chevreuil: ["Un stationnement proche permet de quitter rapidement sans deranger si les conditions changent", "Les cameras cellulaires evitent les visites de releve (moins de derangement)"],
    ours: ["La communication cellulaire permet d'appeler les secours en <5 min en cas d'incident", "Les cameras cellulaires permettent de savoir si un ours dominant est present — choisir son moment"],
    wapiti: ["Un camp proche en altitude permet de chasser matin et soir sans le long trajet quotidien", "L'appareil satellite permet de signaler une position en cas de blessure en terrain isole"],
    dindon: ["Les cameras cellulaires revelent les heures exactes de visite du dindon — optimiser le timing", "Un stationnement proche permet de se repositionner rapidement si le dindon change de corridor"],
  },
  erreurs_a_eviter: {
    orignal: ["Installer un site sans tester la couverture cellulaire (cameras inutilisables)", "Camp trop eloigne (>30 km) rendant les sessions matinales impossibles", "Negliger le telephone satellite en zone isolee"],
    chevreuil: ["Stationnement visible depuis la saline (le chevreuil l'associe au danger)", "Negliger la coordination avec les voisins en zone periurbaine (conflits d'acces)"],
    ours: ["Aucun moyen de communication d'urgence en zone ours = negligence grave", "Camp trop eloigne pour un retrait rapide en cas d'incident"],
    wapiti: ["Compter sur le cellulaire en montagne (couverture absente en altitude)", "Negliger la carte topo papier (GPS = batteries limitees en froid extreme)"],
    dindon: ["Stationner face a la zone de parade du dindon (il deserte pour la journee)", "Negliger la relation avec le proprietaire agricole (perte d'acces au terrain)"],
  },
  optimisations_saisonnieres: { printemps: "Verifier les infrastructures apres l'hiver: etat du camp, acces routier, couverture cellulaire (les antennes peuvent etre endommagees).", ete: "Periode ideale pour ameliorer les infrastructures: reparer le camp, ameliorer le stationnement, installer des panneaux solaires.", automne: "Tout doit etre operationnel avant la saison. Aucune intervention majeure. Tester toutes les communications.", hiver: "Acces limite. Verifier l'etat du camp apres les tempetes (a distance si possible via cameras)." },
  optimisations_support: ["Camera trail cellulaire (Spypoint LINK-MICRO, Stealth Cam CONNECT)", "Telephone satellite Garmin inReach Mini 2 (couverture mondiale)", "Panneau solaire portable 20W pour recharge de batteries en camp isole", "Balise GPS permanente a l'entree du site (coordonnees partagees avec le club)"],
  optimisations_meteo: ["Tempete: rester au camp et surveiller via cameras cellulaires", "Beau temps: profiter pour les visites d'entretien logistiques", "Grand froid: batteries se dechargent vite — prevoir des batteries lithium"],
  optimisations_pression: ["En zone haute pression: la proximite du camp permet des sessions courtes et strategiques", "Partage des infrastructures avec d'autres chasseurs pour reduire les couts"],
  thresholds: { green: "80-100: Camp <5 km, couverture cellulaire LTE, eau potable <500 m, route carrossable <2 km", yellow: "50-79: Camp 5-15 km, couverture partielle, eau 500-2000 m, route 2-5 km", red: "0-49: Camp >15 km, aucune couverture cellulaire ni satellite, eau >2 km, route >5 km" },
  sources: [
    "MRNF — Cartographie du reseau routier forestier du Quebec (2024)",
    "Telus/Bell/Rogers — Cartes de couverture cellulaire LTE rurale Quebec (2025)",
    "SEPAQ — Infrastructures de chasse en reserves fauniques (2023)",
    "Garmin — Manuel technique inReach Mini 2: couverture et autonomie (2024)",
    "Spypoint — Guide technique cameras trail cellulaires LINK-MICRO (2025)",
    "MFFP — Reglementation camps de chasse en territoire public (2024)",
  ],
};

// =====================================================================
// 4. SECURITE ET CONTROLE DE L'ACCES — P1
// =====================================================================
export const securite_acces = {
  title: "Securite et controle de l'acces — Protection du site et des equipements",
  definition: "Evaluation de la securite globale du site de saline: protection contre le vol d'equipement (cameras trail, tree stands), controle d'acces (signalisation, cloture, cadenas), securite du chasseur (faune dangereuse, terrain accidente, risque de chute), et risque de braconnage ou de vandalisme. Un site securise permet un investissement a long terme sans perte de materiel ni interruption de frequentation.",
  methodology: "Score sur 100: protection equipement (30 pts — antivol, cables, caissons), controle d'acces (25 pts — signalisation, barrieres), securite personnelle (25 pts — protocoles ours, chute, evacuation), risque braconnage/vandalisme (20 pts — historique local, isolation). Sources: rapports MFFP agents de conservation, historique de vol terrain, evaluation des risques.",
  justification: {
    orignal: "Les sites d'orignal en foret boreale sont souvent isoles et vulnerables au vol. Les cameras trail (200-400$ chacune) et tree stands (300-800$) representent un investissement significatif. Le vol de cameras trail est le delit #1 rapporte par les chasseurs en zone publique au Quebec. La signalisation BCE-4X et les cables Python Lock reduisent le vol de 70%.",
    chevreuil: "En zone periurbaine, les sites de chevreuil sont plus exposes au vandalisme et a la curiosite du public. Les cameras trail volees representent une perte financiere et de donnees (historique de frequentation). En zone agricole, la coordination avec le proprietaire offre une securite naturelle (presence humaine reguliere).",
    ours: "La securite en zone ours est DOUBLE: protection de l'equipement contre les dommages d'ours (griffures, mastication) ET securite du chasseur (protocoles d'urgence). L'ours noir peut detruire une camera trail en 10 secondes — boitiers metalliques obligatoires. Un ours conditionne a un site regulier peut devenir agressif si l'attractif est absent.",
    wapiti: "En zone montagne, les risques physiques dominent: chute de tree stand en terrain en pente, hypothermie (exposition en altitude), isolement (pas de couverture cellulaire). Les equipements sont moins sujets au vol (zones reculees) mais vulnerables aux intemperies (vent, neige, glace).",
    dindon: "Les sites de dindon en zone agricole beneficient de la securite naturelle du proprietaire. Le risque de vol est modere. La securite personnelle est faible (pas de faune dangereuse en zone dindon typique). Le principal risque est la perturbation par des promeneurs ou des vehicules agricoles.",
  },
  recommendations_terrain: {
    orignal: [
      "Cables Python Lock sur chaque camera trail (cable en acier galvanise, cadenas a combinaison)",
      "Installer les cameras trail a 3+ m de hauteur (hors de portee sans echelle)",
      "Marquer le numero de serie de chaque camera trail (enregistrement aupres du club de chasse)",
      "Signalisation BCE-4X: affiche de zone de chasse geree a l'entree du site",
      "Tree stand: sangle de securite permanente + echelle retractable (antivol)",
      "Installer un panneau de mise en garde visible (dissuasion du braconnage)",
      "Utiliser des cameras trail avec fonction de transmission cellulaire (photo du voleur en temps reel)",
      "Coordonner avec les agents de conservation MFFP pour la surveillance de zone",
      "En zone publique (ZEC): enregistrer le site aupres du gestionnaire de la ZEC",
      "Harnais de securite FallSafe en permanence lors de la montee/descente du tree stand"
    ],
    chevreuil: [
      "Cameras trail avec boitier metallique cadenasse en zone periurbaine",
      "Coordination avec le proprietaire foncier pour la surveillance mutuelle",
      "Signalisation claire: zone de chasse, acces interdit aux non-autorises",
      "Utiliser des cameras trail camouflees (pas de flash blanc — infrarouge noir uniquement)",
      "En zone agricole: integrer la securite du site dans l'entente avec le proprietaire",
      "Ground blind: cadenas sur la fermeture eclair si le terrain est accessible au public",
      "Tree stand: retirer l'echelle entre les sessions en zone a risque de vol",
      "Eviter de laisser des objets de valeur visibles au site (jumelles, outils)",
      "Harnais de securite obligatoire a chaque montee de tree stand"
    ],
    ours: [
      "Boitiers metalliques anti-ours sur TOUTES les cameras trail (acier 2 mm minimum)",
      "Cables anti-ours en acier inoxydable (l'ours tire avec 200+ kg de force)",
      "Contenants anti-ours certifies pour les attractifs (BearVault, UDAP Bear Safe)",
      "Protocole d'urgence affiche au camp: numeros d'urgence, hopital, agents MFFP",
      "Spray anti-ours Counter Assault ou UDAP a la ceinture en permanence",
      "Harnais de securite pour tree stand — l'ours peut secouer un arbre mince",
      "Ne JAMAIS stocker de nourriture au site de saline (ours conditionne = danger mortel)",
      "Trousse de premiers soins trauma au camp (bandages compressifs, tourniquet)",
      "Plan d'evacuation ecrit et partage avec un contact d'urgence"
    ],
    wapiti: [
      "Equipement resistant aux intemperies de montagne (vent, neige, glace)",
      "Ancrage solide du tree stand en terrain en pente (double sangle + cale)",
      "Harnais de securite HSS avec corde de vie du sol au tree stand",
      "Vetements de survie dans un sac etanche au depot intermediaire",
      "Balise de detresse satellite (inReach, SPOT) en cas de blessure en terrain isole",
      "Inspection du tree stand AVANT chaque montee (dommages de vent/neige)",
      "En zone exposee: ancrer les equipements contre les vents forts (rafales 80+ km/h)",
      "Crampons ou pointes de traction pour les approches glissantes en altitude"
    ],
    dindon: [
      "Ground blind: cadenas discret sur la fermeture si le terrain est public",
      "Coordination avec le proprietaire agricole pour la surveillance",
      "Decoys stockes au sec entre les sessions (eviter le vol et les dommages)",
      "Signalisation minimale pour ne pas attirer l'attention sur le site",
      "En zone publique: retirer les decoys et le materiel apres chaque session"
    ],
  },
  strategies_optimisation: {
    orignal: ["Python Lock + camera cellulaire (photo du voleur)", "Signalisation BCE-4X", "Enregistrement serial aupres du club", "Harnais FallSafe permanent"],
    chevreuil: ["Boitier metallique en zone periurbaine", "Camera infrarouge noir (invisible)", "Coordination proprietaire", "Harnais obligatoire"],
    ours: ["Boitiers anti-ours acier 2 mm", "Contenants certifies BearVault", "Spray Counter Assault", "Plan d'evacuation ecrit"],
    wapiti: ["Double sangle tree stand en pente", "Corde de vie HSS", "Balise satellite", "Vetements de survie au depot"],
    dindon: ["Cadenas ground blind", "Coordination agriculteur", "Retirer decoys apres session", "Signalisation minimale"],
  },
  techniques_chasse: {
    orignal: ["Un site securise permet d'investir dans du materiel de qualite superieure (cameras 4K, tree stand premium)", "Les cameras cellulaires servent double fonction: surveillance faunique ET securite anti-vol"],
    chevreuil: ["Un site securise avec proprietaire allie = aucun autre chasseur = aucune pression externe", "Les cameras IR noir ne derangent PAS le chevreuil (pas de flash blanc)"],
    ours: ["Un site securise avec protocole d'urgence permet de chasser sereinement en zone ours", "Les contenants anti-ours protegent les attractifs ET votre securite"],
    wapiti: ["Un site securise en altitude permet de laisser l'equipement lourd sur place entre les sessions", "La balise satellite est une assurance vie en terrain isole"],
    dindon: ["Un site securise en partenariat avec un agriculteur offre un acces exclusif au meilleur habitat", "Le ground blind cadenasse reste en place toute la saison sans risque"],
  },
  erreurs_a_eviter: {
    orignal: ["Laisser des cameras trail sans cable antivol en zone publique (70% de risque de vol)", "Negliger le harnais de securite au tree stand (premiere cause de blessure en chasse)", "Afficher l'emplacement exact du site sur les reseaux sociaux (invite le braconnage)"],
    chevreuil: ["Utiliser des cameras a flash blanc en zone periurbaine (plaintes des voisins + derangement du chevreuil)", "Laisser des outils de valeur au site sans surveillance"],
    ours: ["Boitier plastique sur camera trail en zone ours (detruit en 10 secondes)", "Stocker de la nourriture au site (creation d'ours conditionne dangereux)", "Oublier le spray anti-ours (negligence potentiellement mortelle)"],
    wapiti: ["Monter dans un tree stand endommage par le vent/gel sans inspection prealable", "Partir sans balise satellite en terrain isole de montagne"],
    dindon: ["Laisser les decoys et le materiel au sol en zone publique (vol + degats animaux)", "Negliger la relation avec le proprietaire agricole (perte d'acces)"],
  },
  optimisations_saisonnieres: { printemps: "Inspection post-hiver de tout l'equipement. Remplacement des cables et cadenas endommages par le gel. Test des harnais de securite.", ete: "Installation et remplacement des equipements de securite. Formation aux protocoles d'urgence. Verification des cameras cellulaires.", automne: "Tout doit etre operationnel et verifie. Harnais teste. Spray anti-ours charge. Communications d'urgence testees.", hiver: "Retrait des equipements portables pour entretien. Inspection des structures fixes. Bilan des incidents de l'annee." },
  optimisations_support: ["Cable Python Lock en acier galvanise (Master Lock #8418D)", "Boitier metallique camera trail (Bear Safe, Stealth Cam)", "Harnais de securite HSS Ultra-Lite avec corde de vie", "Spray anti-ours Counter Assault 290g (portee 10 m, duree 7 s)"],
  optimisations_meteo: ["Gel: verifier les cadenas geles (lubrifier au graphite)", "Tempete: risque de dommages aux tree stands — inspecter apres chaque tempete majeure", "Canicule: les batteries de cameras se dechargent plus vite — verifier l'autonomie"],
  optimisations_pression: ["En zone haute pression (publique): securite maximale — cables, boitiers, cameras cellulaires", "En zone privee: securite moderee — coordination proprietaire suffit generalement"],
  thresholds: { green: "80-100: Equipement securise (cables, boitiers), signalisation en place, harnais HSS, protocoles d'urgence documentes, aucun vol/vandalisme", yellow: "50-79: Securite partielle, risque modere de vol, harnais present mais non-teste, protocoles non documentes", red: "0-49: Aucune securite, equipement vulnerable, pas de harnais, pas de protocole d'urgence, historique de vol" },
  sources: [
    "MFFP Quebec — Rapports annuels agents de conservation: infractions et vols (2024)",
    "SEPAQ — Reglementation securite en reserves fauniques (2023)",
    "HSS (Hunter Safety System) — Statistiques de chutes en tree stand et prevention (2024)",
    "Bear Trust International — Bear-Proof Equipment Standards (2022)",
    "NDA — Trail Camera Security and Anti-Theft Best Practices (2024)",
    "UDAP Industries — Bear Spray Effectiveness Studies (2023)",
    "Master Lock — Python Cable Lock Specifications (2024)",
    "MFFP — Protocoles de securite en zone ours noir (2022)",
  ],
};

// =====================================================================
// 5. FREQUENCE OPTIMALE DE VISITE — P1
// =====================================================================
export const frequence_visite = {
  title: "Frequence optimale de visite — Calendrier d'entretien et de suivi du site",
  definition: "Determination de la frequence ideale de visite du site de saline pour maximiser la frequentation animale tout en minimisant le derangement. Chaque visite humaine laisse une empreinte olfactive et visuelle qui peut perturber la faune pendant 24-72 h selon l'espece. La frequence optimale est le point d'equilibre entre un entretien suffisant (bloc mineral plein, cameras fonctionnelles) et un derangement minimal.",
  methodology: "Score sur 100: rapport entretien/derangement (40 pts — modele comportemental), adaptation saisonniere (25 pts — calendrier 4 saisons), adaptation par espece (20 pts — sensibilite specifique), documentation des visites (15 pts — carnet terrain). Donnees: logs cameras trail (frequentation pre/post visite), carnet de terrain, litterature comportementale.",
  justification: {
    orignal: "L'orignal tolere une perturbation humaine breve toutes les 3-4 semaines sans modification significative de sa frequentation. Les cameras trail montrent un retour a la frequentation normale dans les 48-72 h apres une visite d'entretien de <20 min. En saison de chasse (octobre), reduire les visites a 1 par mois maximum (entretien minimal, pas de modifications). Le bloc de 20-25 kg dure 4-6 semaines en saison active.",
    chevreuil: "Le chevreuil est l'espece la plus sensible au derangement: une visite provoque une desertion de 48-72 h. Frequence optimale: 1 visite toutes les 3-4 semaines hors saison, 0 visite en saison de chasse sauf urgence. Les cameras trail cellulaires eliminent le besoin de visites de releve. Le bloc de 10-15 kg dure 3-4 semaines.",
    ours: "L'ours tolere mieux le derangement regulier que les cervides — il s'habitue aux patterns predictibles. Frequence optimale: 1 visite toutes les 2-3 semaines pour le remplacement des attractifs. En saison de chasse: 1 visite par semaine pour maintenir la fraicheur des attractifs (l'ours est attire par les odeurs fraiches).",
    wapiti: "Le wapiti en zone montagne ne necessite que 1 visite toutes les 6-8 semaines (le bloc dure plus longtemps en altitude, dissolution lente). En pre-rut (mi-septembre): 1 visite pour remplacer le bloc et verifier l'equipement. Pendant le rut: ZERO visite (le wapiti est hyper-sensible aux derangements).",
    dindon: "Le dindon tolere bien les visites regulieres tant que le ground blind reste en place et que l'approche est silencieuse. Frequence optimale au printemps: 1 visite toutes les 2 semaines pour reapprovisionner les grains. Hors saison: 1 visite par mois pour verifier le blind et les decoys.",
  },
  recommendations_terrain: {
    orignal: [
      "Frequence hors saison (mai-sept): 1 visite toutes les 4-6 semaines pour remplacement de bloc",
      "Frequence en saison (oct-nov): 1 visite par MOIS maximum — entretien minimal uniquement",
      "Installer des cameras trail cellulaires pour eliminer les visites de releve",
      "Planifier les visites en mi-journee (10h-14h) quand l'orignal est couche",
      "Duree de visite maximale: 20 min — chronometrer chaque intervention",
      "Documenter la frequentation camera trail AVANT et APRES chaque visite (mesurer l'impact)",
      "Si la frequentation camera chute de >50% apres une visite: reduire la frequence",
      "Pre-rut (15 sept - 5 oct): 1 derniere visite d'entretien, puis ZERO visite pendant le rut",
      "Combiner toutes les taches en 1 seule visite (bloc + cameras + corridors + affut)"
    ],
    chevreuil: [
      "Frequence hors saison: 1 visite toutes les 3-4 semaines MAXIMUM",
      "Frequence en saison: ZERO visite sauf urgence absolue (bloc vide, camera volee)",
      "Cameras trail cellulaires OBLIGATOIRES pour eliminer les visites de releve",
      "Si visite necessaire en saison: entree/sortie en <5 min, mi-journee uniquement",
      "Porter des bottes en caoutchouc et des gants latex a chaque visite (anti-odeur)",
      "Ne JAMAIS visiter 2 jours de suite le meme site (le chevreuil deserte)",
      "Documenter les heures de visite et la frequentation post-visite dans un carnet terrain",
      "Si la frequentation camera chute apres une visite: espacer les visites de 50%",
      "Stocker des blocs de rechange au depot pour eviter les allers-retours supplementaires"
    ],
    ours: [
      "Frequence hors saison: 1 visite toutes les 2-3 semaines (attractifs frais)",
      "Frequence en saison: 1 visite par semaine (maintenir les attractifs odorants)",
      "L'ours prefere les attractifs FRAIS — visites plus frequentes = meilleure frequentation",
      "Visites en DUO et en mi-journee (11h-14h) exclusivement",
      "Documenter les dommages d'ours a chaque visite (indicateur de frequentation et de taille)",
      "En saison de chasse: ne pas visiter le jour ou on chasse (odeur fraiche)",
      "Alterner entre 2-3 attractifs (melasse, mais, poisson) pour varier les stimulations olfactives",
      "Si l'ours detruit les equipements a chaque visite: renforcer les contenants, pas la frequence"
    ],
    wapiti: [
      "Frequence hors rut: 1 visite toutes les 6-8 semaines",
      "Pre-rut (mi-septembre): 1 visite de preparation (bloc neuf, equipement verifie)",
      "Rut actif (oct): ZERO visite — le wapiti est hyper-vigilant et agressif",
      "Post-rut (nov): 1 visite de bilan et d'hivernage de l'equipement",
      "En zone montagne: planifier les visites selon la meteo (pas de portage sous orage)",
      "Combiner toutes les taches en 1 seule visite pour reduire les passages",
      "Le wapiti tolere les visites si elles suivent un pattern regulier (toujours le meme jour/heure)"
    ],
    dindon: [
      "Frequence printemps (saison active): 1 visite toutes les 2 semaines",
      "Frequence hors saison: 1 visite par mois pour verifier le blind et les decoys",
      "Le dindon tolere les visites regulieres si le blind reste en place et l'approche est silencieuse",
      "Ne pas visiter le matin (5h-10h) pendant la saison de parade",
      "Reapprovisionner les grains en mi-journee quand les dindons sont dans les champs",
      "Documenter les heures de parade et de visite via les cameras trail"
    ],
  },
  strategies_optimisation: {
    orignal: ["1 visite/4-6 sem hors saison, 1/mois en saison", "Cameras cellulaires obligatoires", "Mi-journee uniquement", "Chronometrer <20 min"],
    chevreuil: ["1 visite/3-4 sem hors saison, ZERO en saison", "Cameras cellulaires eliminant les releves", "<5 min en saison si necessaire", "Bottes caoutchouc + gants latex"],
    ours: ["1/2-3 sem hors saison, 1/semaine en saison", "Attractifs frais = meilleure frequentation", "Duo + mi-journee", "Alterner les attractifs"],
    wapiti: ["1/6-8 sem hors rut, ZERO pendant le rut", "1 visite pre-rut de preparation", "Planifier selon meteo montagne", "Pattern regulier tolere"],
    dindon: ["1/2 sem au printemps, 1/mois hors saison", "Blind en place = tolerance", "Mi-journee pour reapprovisionnement", "Pas de visite le matin"],
  },
  techniques_chasse: {
    orignal: ["Les cameras trail montrent que l'orignal revient 48-72 h apres une visite breve — planifier la chasse 3 jours apres la derniere visite d'entretien", "En pre-rut: derniere visite le 10 septembre, puis chasse a partir du 20 septembre"],
    chevreuil: ["Le chevreuil deserte pendant 48-72 h apres une visite — ne JAMAIS chasser le meme jour qu'une visite d'entretien", "Les cameras cellulaires revelent les pics de frequentation sans aucune visite de derangement"],
    ours: ["L'ours visite plus souvent apres un remplacement d'attractifs — chasser 24-48 h apres la visite d'entretien (les attractifs frais = pic de frequentation)", "L'ours qui a un pattern regulier est plus previsible — maintenir la frequence de visites constante"],
    wapiti: ["En pre-rut: le bloc mineral frais attire les males en recherche de sodium — chasser 5-7 jours apres le remplacement", "ZERO visite pendant le rut = frequentation maximale naturelle"],
    dindon: ["Le dindon revient quotidiennement a un site regulierement approvisionne — la constance est la cle", "Les grains frais attirent le dindon dans les 24 h — reapprovisionner 2 jours avant la chasse"],
  },
  erreurs_a_eviter: {
    orignal: ["Visiter plus d'1 fois par mois en saison de chasse", "Ne pas chronometrer la duree de visite (depassements frequents)", "Combiner visite d'entretien et session de chasse le meme jour"],
    chevreuil: ["Visiter en soiree (heures actives du chevreuil)", "2 visites dans la meme semaine (panique permanente du chevreuil)", "Negliger les cameras cellulaires (visites de releve inutiles)"],
    ours: ["Espacement trop long entre les visites (>1 mois) — les attractifs perdent leur puissance olfactive", "Visiter le jour de la chasse (odeur humaine fraiche = ours mefiant)"],
    wapiti: ["Visiter pendant le rut actif (le wapiti quitte la zone pour des jours)", "Visites irregulieres (le wapiti ne peut pas s'habituer a un pattern)"],
    dindon: ["Visiter le matin pendant la parade (le dindon quitte le secteur)", "Laisser le site sans grains pendant >4 semaines (le dindon trouve un autre site)"],
  },
  optimisations_saisonnieres: { printemps: "Visites plus frequentes pour l'installation et la mise en place. Le dindon est en saison active — visiter en mi-journee.", ete: "Rythme de croisiere. Visites regulieres pour le remplacement de blocs. Meilleure saison pour les travaux d'amenagement.", automne: "Reduire drastiquement les visites. Saison de chasse active. Entretien minimal. Cameras cellulaires.", hiver: "1 visite de bilan pour retrait/entretien de l'equipement. Pas de frequentation animale aux salines en hiver." },
  optimisations_support: ["Cameras trail cellulaires (Spypoint, Stealth Cam) pour eliminer les visites de releve", "Carnet de terrain standardise: date, heure, duree, observations, meteo", "Minuteur de visite sur le telephone (alerte a 15 min)", "Blocs de rechange au depot pour reduire les visites logistiques"],
  optimisations_meteo: ["Pluie: visite ideale (odeur humaine lavee plus rapidement)", "Vent fort: visite favorable (odeur dispersee)", "Temps calme sans vent: eviter les visites (odeur stagnante sur le site)", "Gel matinal: le sol gele ne retient pas les odeurs — visite favorable"],
  optimisations_pression: ["En zone haute pression: reduire les visites de 50% par rapport a la normale", "Coordonner avec les voisins pour alterner les visites et reduire le derangement cumule"],
  thresholds: { green: "80-100: Frequence optimale respectee, cameras cellulaires en place, duree <15 min, documentation complete", yellow: "50-79: Frequence acceptable mais non optimale, releves manuels necessaires, duree 15-30 min", red: "0-49: Visites trop frequentes ou trop rares, pas de cameras, duree >30 min, aucune documentation" },
  sources: [
    "Dussault, Courtois & Ouellet (2005) — Impact des derangements sur la frequentation des salines par l'orignal (UQAR)",
    "Mississippi State University Deer Lab — Disturbance Frequency and Deer Site Fidelity (2022)",
    "NDA — Mineral Site Visit Frequency Optimization (2024)",
    "MFFP — Protocoles de suivi des salines en reserve faunique (2023)",
    "Bear Trust International — Bait Site Management Frequency in Black Bear Zones (2022)",
    "RMEF — Mineral Site Visitation Patterns in Elk Country (2023)",
    "NWTF — Turkey Food Plot Maintenance Calendar (2024)",
    "University of Georgia Deer Lab — Human Disturbance and Whitetail Recovery Time (2021)",
  ],
};

// =====================================================================
// 6. HISTORIQUE DES OBSERVATIONS — P1
// =====================================================================
export const historique_observations = {
  title: "Historique des observations — Donnees cameras trail et observations terrain",
  definition: "Evaluation de la quantite et qualite des donnees historiques d'observation disponibles pour le site: nombre de photos/videos cameras trail, frequence de passage par espece, ratio males/femelles, presence de males matures (trophees), heures de passage predominantes, et evolution de la frequentation au fil des saisons. Un historique riche permet une prise de decision strategique basee sur des donnees plutot que sur l'intuition.",
  methodology: "Score sur 100: volume de donnees (30 pts — nombre de detections/saison), diversite des especes (20 pts — nombre d'especes photographiees), ratio males matures (20 pts — proportion males >3.5 ans), coherence temporelle (15 pts — donnees sur 2+ saisons), qualite des observations terrain (15 pts — carnet de terrain detaille). Sources: logs cameras trail, carnet de terrain, observations directes.",
  justification: {
    orignal: "Un site avec 3+ saisons de donnees cameras trail permet d'identifier les patterns de frequentation: heures de visite (souvent crepusculaires), jours de la semaine, saison de pointe (pre-rut sept-oct), et la presence de males matures. L'orignal visite les salines avec une regularite predictible — 50-200 detections/saison sur un bon site. Un historique de 5+ males differents confirme un site premium.",
    chevreuil: "Les cameras trail permettent d'identifier les males individuels par leur ramure (photo-identification). Un historique de 3+ saisons revele la fidelite des males a un site, leur croissance annuelle, et le potentiel trophee du secteur. Le ratio males/femelles optimal est de 1:3-1:5 sur les cameras. Un site avec <20 detections/saison est sous-performant.",
    ours: "L'historique des cameras trail en zone ours est critique pour la SECURITE: identifier le nombre d'ours distincts, leur taille estimee, et leurs heures de visite. Un male dominant (>150 kg) visite regulierement entre 17h et 21h. Les cameras permettent egalement de detecter les femelles avec oursons — chasse interdite sur ces individus.",
    wapiti: "Le wapiti voyage en groupes — les cameras trail documentent la taille des hardes (5-15 individus), les corridors de migration, et les periodes de passage. Les males matures (panache 5+ pointes par cote) sont identifiables individuellement. L'historique revele les corridors les plus productifs et les periodes de migration.",
    dindon: "Les cameras trail au sol revelent le nombre de dindons dans le secteur, la composition des groupes (males/femelles/jeunes), les heures de parade, et les corridors perchoir-alimentation. Un historique de 2+ saisons confirme la fidelite des groupes au site et les meilleurs jours de chasse.",
  },
  recommendations_terrain: {
    orignal: [
      "Installer 3-5 cameras trail par site pour couvrir tous les corridors d'approche",
      "Camera a detection rapide (0.2-0.5 s) pour capturer l'orignal en mouvement",
      "Mode video 15-30 s pour documenter le comportement (lechage, brout, frottage)",
      "Relever les cameras toutes les 4-6 semaines (ou cellulaires pour donnees en temps reel)",
      "Cataloguer chaque male par la forme de son panache (photo-identification)",
      "Creer une base de donnees: date, heure, espece, sexe, age estime, meteo",
      "Analyser les patterns de frequentation sur 3+ saisons pour identifier les tendances",
      "Comparer la frequentation pre/post remplacement de bloc (mesurer l'impact de l'entretien)",
      "Installer 1 camera sur le sentier d'acces pour documenter les passages humains non-autorises",
      "Les cameras trail cellulaires transmettent les alertes en temps reel — ajuster la strategie de chasse"
    ],
    chevreuil: [
      "Cameras trail a flash infrarouge noir (invisibles — pas de perturbation du chevreuil)",
      "Hauteur de camera: 60-80 cm (hauteur poitrine du chevreuil pour photo-identification)",
      "Mode photo burst (3 photos par detection) pour capturer la ramure sous differents angles",
      "Photo-identification des males par la ramure: chaque male a une forme unique",
      "Documenter la croissance annuelle de chaque male identifie (potentiel trophee)",
      "Ratio males/femelles cible: 1:3-1:5 (un desequilibre indique un probleme de gestion)",
      "Frequentation cible: 50-200 detections/saison sur un bon site de chevreuil",
      "Analyser les heures de visite par saison: pre-rut = matinal, rut = toute la journee",
      "Comparer les annees pour evaluer la tendance de la population locale"
    ],
    ours: [
      "Camera a flash infrarouge noir obligatoire (le flash blanc effraye certains ours)",
      "Boitier metallique anti-ours sur chaque camera (l'ours detruit le plastique en secondes)",
      "Installer la camera a 2.5-3 m de hauteur (hors de portee des ours curieux)",
      "Mode video 30 s pour estimer la taille de l'ours (longueur, poids estime)",
      "Identifier les ours individuels par les marques: cicatrices, couleur, tache pectorale",
      "Documenter les femelles avec oursons — CHASSE INTERDITE sur ces individus",
      "Analyser les heures de visite: le male dominant est souvent le dernier a se presenter",
      "Cameras cellulaires pour alerte en temps reel — savoir si un ours est actif avant la visite",
      "Le nombre d'ours distincts photographies = indicateur de densite de la population locale"
    ],
    wapiti: [
      "Cameras trail sur chaque corridor de migration identifie",
      "Mode video 30-60 s pour filmer le passage complet de la harde",
      "Comptage des individus par harde et identification des males matures (panache 5+)",
      "Documenter les heures de passage pour identifier les fenetres de chasse optimales",
      "L'historique de migration revele les corridors les plus fiables annee apres annee",
      "Comparer les donnees de cameras avec les observations de bugle en pre-rut",
      "Installer des cameras a detection grand angle pour capturer les groupes larges",
      "Partager les donnees avec les guides locaux pour une gestion collaborative"
    ],
    dindon: [
      "Camera au sol (30-40 cm de hauteur) orientee vers la zone de mineraux/grains",
      "Mode photo pour compter les individus du groupe",
      "Documenter les heures de parade des males (gobble) au printemps",
      "Identifier le male dominant par la barbe, les ergots, et la taille",
      "Les cameras trail revelent le corridor exact perchoir-alimentation",
      "Documenter les heures de descente du perchoir (generalement 10-30 min apres l'aube)",
      "Comparer les saisons pour evaluer la stabilite de la population locale"
    ],
  },
  strategies_optimisation: {
    orignal: ["3-5 cameras/site", "Photo-ID des males par panache", "Base de donnees structuree", "Cellulaires pour temps reel"],
    chevreuil: ["IR noir obligatoire", "Photo burst 3x pour ramure", "Photo-ID annuelle des males", "Ratio males/femelles surveille"],
    ours: ["Boitier anti-ours acier", "Camera a 2.5-3 m", "Identification par cicatrices", "Femelles+oursons = chasse interdite"],
    wapiti: ["Cameras sur corridors de migration", "Video 30-60 s pour hardes", "Comptage individus", "Donnees partagees avec guides"],
    dindon: ["Camera au sol 30-40 cm", "Comptage du groupe", "Heures de parade documentees", "Male dominant identifie"],
  },
  techniques_chasse: {
    orignal: ["Les cameras revelent que 80% des visites d'orignal sont entre 5h-8h et 17h-20h — planifier les sessions en consequence", "Un male photographie regulierement a un site est fidele — il reviendra"],
    chevreuil: ["Les cameras en mode burst permettent de mesurer la ramure — ne tirer que les males qui ont atteint leur potentiel (>3.5 ans)", "Un male qui visite exclusivement de nuit est un male mature — il faudra l'intercepter en deplacement, pas a la saline"],
    ours: ["Le male dominant qui visite entre 19h et 21h est l'ours le plus probable pour la session du soir", "Un ours qui visite a la meme heure 3+ jours de suite est un ours de pattern — chasser ce jour/heure"],
    wapiti: ["Les cameras montrent quand la harde complete passe — la fenetre de tir est souvent <15 min", "Les males matures qui passent seuls sont souvent 30-60 min apres le groupe de femelles"],
    dindon: ["Les cameras revelent le corridor EXACT de descente du perchoir — positionner le blind en consequence", "Le male dominant qui parade a la meme heure chaque matin est le plus predictible"],
  },
  erreurs_a_eviter: {
    orignal: ["N'installer qu'une seule camera (couverture incomplete des corridors)", "Negliger l'analyse des donnees (les photos s'accumulent sans action strategique)", "Ne pas cataloguer les males individuels (opportunite de suivi perdue)"],
    chevreuil: ["Camera a flash blanc (le chevreuil est derange et change son pattern)", "Ne pas documenter le ratio males/femelles (indicateur de gestion manque)", "Tirer un male jeune identifie sur camera (perte de potentiel trophee)"],
    ours: ["Camera en boitier plastique (detruite par l'ours)", "Ne pas identifier les femelles avec oursons (risque d'infraction)", "Ignorer les alertes cellulaires (perte d'information en temps reel)"],
    wapiti: ["Ne couvrir qu'un seul corridor (le wapiti peut changer de chemin saisonnièrement)", "Ne pas partager les données avec les gestionnaires locaux (opportunite de gestion perdue)"],
    dindon: ["Camera trop haute (angle inadapte pour compter les individus au sol)", "Ne pas documenter les heures de parade (information strategique manquee)"],
  },
  optimisations_saisonnieres: { printemps: "Installation des cameras. Debut de la saison de dindon. Documenter la fonte et les premiers mouvements fauniques.", ete: "Saison de collecte de donnees. Les cameras documentent l'utilisation estivale des salines (sodium, calcium).", automne: "Saison critique. Les cameras trail revelent les patterns de pre-rut et de rut. Analyse quotidienne des donnees cellulaires.", hiver: "Retrait et entretien des cameras portables. Analyse des donnees de la saison pour planifier la suivante." },
  optimisations_support: ["Cameras trail cellulaires: Spypoint LINK-MICRO-S-LTE, Stealth Cam CONNECT", "Cartes SD haute capacite (64-128 Go) pour les cameras non-cellulaires", "Batterie externe au lithium pour prolonger l'autonomie en hiver", "Logiciel de gestion de photos trail: Spypoint App, Stealth Cam Command Pro"],
  optimisations_meteo: ["Froid extreme (<-25C): batteries se dechargent vite — pack lithium obligatoire", "Humidite: verifier l'etancheite des boitiers apres les fortes pluies", "Neige: degivrer le capteur de mouvement apres chaque tempete"],
  optimisations_pression: ["En zone haute pression: les cameras documentent non seulement la faune mais aussi les passages humains (chasseurs concurrents, braconniers)"],
  thresholds: { green: "80-100: 3+ saisons de donnees, 100+ detections/saison, males matures identifies, base structuree, cameras cellulaires", yellow: "50-79: 1-2 saisons, 50-100 detections/saison, donnees partielles, pas de photo-ID", red: "0-49: <1 saison, <50 detections, aucune camera ou camera non-fonctionnelle, aucune donnee structuree" },
  sources: [
    "MFFP Quebec — Protocoles de suivi par cameras trail en reserve faunique (2023)",
    "Spypoint — Guide technique LINK-MICRO-S-LTE: installation et optimisation (2025)",
    "NDA — Trail Camera Strategies for Deer Management (2024)",
    "Mississippi State University Deer Lab — Photo-Identification of Individual Bucks (2022)",
    "RMEF — Trail Camera Deployment for Elk Herd Monitoring (2023)",
    "Bear Trust International — Camera Trapping Black Bears: Methods and Safety (2022)",
    "NWTF — Using Trail Cameras for Turkey Scouting (2024)",
    "University of Georgia Deer Lab — Buck Age Estimation from Trail Camera Photos (2021)",
  ],
};

// =====================================================================
// 7. ADAPTABILITE SAISONNIERE — P1
// =====================================================================
export const adaptabilite_saisonniere = {
  title: "Adaptabilite saisonniere — Capacite du site a performer toute l'annee",
  definition: "Evaluation de la performance du site de saline a travers les 4 saisons: fonte printaniere (drainage, accessibilite), chaleur estivale (dissolution minerale, insectes), saison de chasse automnale (conditions optimales), et hiver rigoureux (gel, enneigement, accessibilite). Un site adaptable offre une frequentation animale constante sur 8-10 mois par an, tandis qu'un site mal adapte n'est productif que 2-3 mois.",
  methodology: "Score sur 100: performance printaniere (25 pts — drainage post-fonte, acces), performance estivale (20 pts — dissolution, insectes), performance automnale (30 pts — conditions de chasse), performance hivernale (25 pts — gel, acces, enneigement). Sources: observations terrain 4 saisons, donnees cameras trail annuelles, carnet de terrain.",
  justification: {
    orignal: "L'orignal visite les salines de mai a novembre (7 mois). Le pic de frequentation est au printemps (mai-juin) pour compenser la carence hivernale en sodium, et en pre-rut (septembre-octobre) pour la croissance du panache. En hiver, l'orignal se retire dans les ravages de coniferes denses et ne visite plus les salines. Un site qui performe au printemps ET en automne double le nombre de sessions de chasse possibles.",
    chevreuil: "Le chevreuil visite les salines d'avril a novembre (8 mois). Le besoin en mineraux est maximal au printemps (lactation des femelles, croissance du velours chez les males). En automne, la frequentation diminue legerement mais reste significative en pre-rut. Le gel hivernal rend la saline inactive (le mineral gele ne peut pas etre leche).",
    ours: "L'ours noir visite les salines d'avril a octobre (7 mois), avec un pic en juin-juillet (hyperphagie pre-estivale) et septembre-octobre (hyperphagie pre-hibernation). L'ours entre en taniere de novembre a mars — aucune frequentation hivernale. Le site doit etre maximal pendant les 2 periodes d'hyperphagie.",
    wapiti: "Le wapiti visite les salines de mai a octobre (6 mois), avec un pic en juillet-aout (croissance du panache = besoin intense en calcium et phosphore) et en pre-rut (septembre). L'hiver en montagne rend le site inaccessible (neige >1 m). Le site doit maximiser la frequentation estivale et pre-rut.",
    dindon: "Le dindon visite les zones de mineraux principalement de mars a juin (saison de parade et de nidification). La frequentation est faible en ete et automne. Le site doit etre optimise pour le printemps (saison de chasse du dindon au Quebec: mai). En hiver, le dindon se nourrit de glands et de grains — pas de frequentation aux sites de mineraux.",
  },
  recommendations_terrain: {
    orignal: [
      "Printemps (mai-juin): verifier le drainage post-fonte — reparer les tranchees, degager les debris",
      "Ete (juil-aout): remplacer le bloc mineral (dissolution rapide par la chaleur et la pluie)",
      "Automne (sept-nov): entretien minimal — ZERO modification, bloc frais pour le pre-rut",
      "Hiver (dec-mars): retirer les equipements portables, inspecter les structures fixes",
      "Installer un bloc resistant a la dissolution rapide (bloc comprime vs bloc moule)",
      "Prevoir un drainage de surface pour les crues printanieres (tranchee demi-lune en amont)",
      "Les insectes d'ete (mouches, moustiques) affectent le comportement de l'orignal — installer le site en zone ventee",
      "Documenter la frequentation par saison (cameras trail) pour identifier la saison de pointe",
      "Prevoir un 2e affut adapte aux vents d'ete (differents des vents d'automne)"
    ],
    chevreuil: [
      "Printemps: le chevreuil est en carence minerale apres l'hiver — bloc frais DES la fonte des neiges",
      "Ete: frequentation reguliere mais comportement plus nocturne — cameras trail pour confirmer",
      "Automne: pre-rut = frequentation accrue des males — sessions prioritaires",
      "Hiver: bloc gele, pas de frequentation. Profiter pour l'amenagement et la planification",
      "Les blocs comprimes (type Trophy Rock) resistent mieux aux intemperies que les blocs moules",
      "En zone de neige importante: surélever le bloc sur un poteau (50-60 cm) pour l'accessibilite post-neige",
      "Le chevreuil change ses heures de visite par saison — adapter les sessions de chasse en consequence",
      "Les frottoirs (rubs) de pre-rut pres de la saline confirment la fidelite des males matures au site"
    ],
    ours: [
      "Avril-mai: l'ours sort de sa taniere en recherche de nourriture — saline + attractifs odorants des le degel",
      "Juin-juillet: hyperphagie pre-estivale — frequentation maximale, attractifs frais chaque 2 semaines",
      "Sept-oct: hyperphagie pre-hibernation — dernier pic de frequentation, maximiser les attractifs",
      "Nov-mars: taniere — site inactif, retrait des equipements vulnerables au gel",
      "L'ours est actif 7 mois mais concentre 80% de ses visites sur 4 mois (juin-juillet + sept-oct)",
      "Adapter le type d'attractif par saison: melasse printemps, poisson ete, mais automne",
      "Les cameras trail documentent les dates exactes de sortie/entree de taniere — calibrer la saison"
    ],
    wapiti: [
      "Mai-juin: arrivee en altitude apres la migration printaniere — saline fraiche pour l'accueil",
      "Juillet-aout: pic de besoin mineral (panache) — bloc frais de haute qualite minerale",
      "Septembre: pre-rut — combiner saline et appels (bugle) pour les sessions de chasse",
      "Oct-nov: neige en altitude — le site devient inaccessible, retrait de l'equipement",
      "Le wapiti en montagne a une fenetre de frequentation courte (5-6 mois) — optimiser chaque mois",
      "Prevoir un bloc mineral resistant au gel pour prolonger la saison en altitude (septembre-octobre)",
      "Les corridors de migration changent legerement chaque annee — surveiller avec les cameras"
    ],
    dindon: [
      "Mars-avril: parade et accouplement — installer les grains/mineraux avant la saison",
      "Mai: saison de chasse au Quebec — le site doit etre operationnel et le blind habite (2+ sem)",
      "Juin-sept: frequentation reduite — entretien minimal, 1 visite/mois",
      "Oct-fev: frequentation quasi-nulle — bilan et preparation de la saison suivante",
      "Le dindon a une fenetre de frequentation courte (3-4 mois) — maximiser le printemps",
      "Installer le ground blind en mars pour qu'il soit totalement habite pour la saison de mai"
    ],
  },
  strategies_optimisation: {
    orignal: ["Bloc comprime resistant + drainage printemps", "2 affuts pour vents ete et automne", "Site ventee contre insectes", "Documentation saisonniere par cameras"],
    chevreuil: ["Bloc frais des la fonte", "Trophy Rock resistant aux intemperies", "Sessions adaptees aux heures saisonnieres", "Surélever le bloc pour acces post-neige"],
    ours: ["Attractifs adaptes par saison", "Concentration sur juin-juil et sept-oct", "Dates de taniere calibrees par cameras", "Retrait equipement en hiver"],
    wapiti: ["Fenetre courte optimisee (mai-oct)", "Bloc haute qualite minerale en juil-aout", "Saline + bugle en pre-rut", "Retrait equipement avant la neige"],
    dindon: ["Blind installe en mars pour mai", "Grains frais avant la parade", "Fenetre courte maximisee (mars-juin)", "Bilan automnal pour saison suivante"],
  },
  techniques_chasse: {
    orignal: ["Printemps (mai-juin): sessions matinales productives — l'orignal visite a l'aube pour les mineraux", "Automne (pre-rut): sessions crepusculaires — le male patrouille en fin de journee"],
    chevreuil: ["Printemps: le chevreuil visite en plein jour (moins mefiant, en carence minerale)", "Automne pre-rut: le male visite plus souvent en journee (patrouille territoriale) — meilleures sessions"],
    ours: ["Juin-juillet: sessions du soir (17h-21h) — l'ours est le plus actif en hyperphagie estivale", "Septembre: sessions du soir aussi — l'ours accumule les reserves avant l'hibernation"],
    wapiti: ["Juillet-aout: sessions matinales — le wapiti visite les salines a l'aube pour eviter la chaleur", "Septembre pre-rut: combiner saline et bugle — sessions toute la journee possibles"],
    dindon: ["Mai: sessions matinales exclusivement — le dindon descend du perchoir a l'aube et parade", "Le dindon est un chasseur de printemps — ne pas perdre d'energie sur les autres saisons"],
  },
  erreurs_a_eviter: {
    orignal: ["Negliger le drainage printanier (site inonde = bloc dissous + acces impossible)", "Modifier le site en pleine saison de chasse automnale"],
    chevreuil: ["Ne pas remplacer le bloc au printemps (le chevreuil en carence va ailleurs)", "Laisser le bloc geler sans protection hivernale (dissolution par gel-degel)"],
    ours: ["Laisser le site sans attractifs pendant les periodes d'hyperphagie", "Ne pas retirer les equipements vulnerables avant l'hiver"],
    wapiti: ["Installer le site trop tard en saison (le wapiti est deja en migration)", "Negliger le retrait d'equipement avant les premieres neiges"],
    dindon: ["Installer le blind trop tard (moins de 2 semaines avant la chasse)", "Ne pas fournir de grains frais pour la saison de parade"],
  },
  optimisations_saisonnieres: { printemps: "PRIORITE: Remise en service du site. Drainage, bloc frais, cameras verifiees, sentiers repares.", ete: "Maintenance de croisiere. Remplacement de blocs. Debroussaillage des corridors de tir.", automne: "Saison de CHASSE. Zero modification. Entretien minimal. Cameras cellulaires.", hiver: "Bilan annuel. Retrait equipement portable. Planification de la saison suivante." },
  optimisations_support: ["Bloc mineral comprime (Trophy Rock, Redmond): dissolution lente, resistant aux intemperies", "Poteau sureleve (50-60 cm) pour acces post-neige en zone de fort enneigement", "Calendar de suivi saisonnier pre-imprime avec checklist par saison"],
  optimisations_meteo: ["Fonte rapide: verifier le drainage immediatement", "Canicule estivale: bloc se dissout 2x plus vite — prevoir un remplacement supplementaire", "Premiers gels: derniere visite de la saison pour securiser l'equipement"],
  optimisations_pression: ["En zone haute pression: concentrer les sessions sur les fenetres saisonnieres de pointe (pre-rut, hyperphagie)", "Hors saison: profiter des mois calmes pour les amenagements sans derangement"],
  thresholds: { green: "80-100: Site productif 8+ mois/an, drainage fonctionnel, acces 4 saisons, frequentation documentee par saison", yellow: "50-79: Site productif 5-7 mois, drainage partiel, acces 3 saisons, documentation partielle", red: "0-49: Site productif <5 mois, drainage deficient, acces saisonnier limite, aucune documentation" },
  sources: [
    "MFFP Quebec — Calendrier d'utilisation des salines par la faune au Quebec (2022)",
    "Dussault & Courtois (2004) — Variations saisonnieres de frequentation des salines par l'orignal (UQAR)",
    "NDA — Year-Round Mineral Site Management: Seasonal Strategies (2024)",
    "RMEF — Seasonal Mineral Requirements and Site Visitation in Elk (2023)",
    "Bear Trust International — Seasonal Activity Patterns of Black Bears at Bait Sites (2022)",
    "NWTF — Spring Turkey Season Preparation Guide (2024)",
    "Can. J. Zoology — Mineral Lick Use by Cervids: Seasonal Patterns (2020)",
    "Wisconsin DNR — Mineral Site Seasonal Checklist (2024)",
  ],
};

// =====================================================================
// 8. COMPLEMENTARITE DU RESEAU — P2
// =====================================================================
export const complementarite_reseau = {
  title: "Complementarite du reseau — Integration avec les autres sites du territoire",
  definition: "Evaluation de la maniere dont le site de saline s'integre dans un reseau plus large de sites de chasse sur le territoire: complementarite geographique (couverture de zone), complementarite par espece (sites specialises vs generalistes), partage des corridors, et capacite du reseau a couvrir differentes conditions de vent. Un reseau bien planifie de 3-5 salines offre une couverture quasi-totale du territoire et maximise le nombre de sessions productives.",
  methodology: "Score sur 100: couverture geographique (30 pts — repartition spatiale des sites), complementarite especes (25 pts — diversite inter-sites), couverture eolienne (25 pts — positions de vent differentes), synergie des corridors (20 pts — connexion entre sites). Sources: carte GPS des sites, rose des vents, inventaire des corridors, observations terrain.",
  justification: {
    orignal: "Un reseau de 3-5 salines couvrant 10-25 km2 permet de chasser l'orignal quelles que soient les conditions de vent. Les sites doivent couvrir differents types d'habitat: bord de lac (ete), foret mixte (automne), et proximite de ravage (hiver). Les corridors entre les salines sont souvent empruntes par les orignaux en deplacement, creant des opportunites d'interception.",
    chevreuil: "Le chevreuil a un territoire plus restreint (0.5-3 km2 pour les males). Un reseau de 2-3 salines espacees de 500-1500 m couvre le territoire d'un male dominant. Chaque site doit offrir une condition de vent differente pour maximiser les sessions productives. Les sentiers entre les sites sont souvent empruntes par les males en patrouille de pre-rut.",
    ours: "L'ours noir a un domaine vital de 20-100 km2. Un reseau de 2-4 sites espaces de 3-8 km couvre differentes zones du domaine vital. Chaque site peut utiliser un attractif different (melasse, mais, poisson) pour varier les stimulations et maintenir l'interet de l'ours. Les corridors entre les sites sont les memes que les corridors naturels de l'ours.",
    wapiti: "Le wapiti migre sur de longues distances (10-50 km). Un reseau de 2-3 salines le long du corridor de migration permet d'intercepter la harde a differents points. Les sites doivent couvrir differentes altitudes (fond de vallee, mi-pente, alpage) pour s'adapter aux deplacements altitudinaux saisonniers.",
    dindon: "Le dindon a un territoire compact (0.5-2 km2). Un reseau de 2 sites (un pres du perchoir, un sur le corridor d'alimentation) couvre le territoire d'un groupe. En zone agricole avec plusieurs groupes, multiplier les sites en fonction du nombre de perchoirs identifies.",
  },
  recommendations_terrain: {
    orignal: [
      "Reseau de 3-5 salines couvrant 10-25 km2 du territoire de chasse",
      "Espacement inter-sites: 2-5 km (eviter la cannibalisation entre sites proches)",
      "Chaque site avec un affut oriente pour un vent DIFFERENT (N, O, S, E)",
      "Diversifier les habitats: bordure de lac, foret mixte, clairiere, proximite ravage",
      "Cartographier les corridors ENTRE les sites — ce sont des zones d'interception",
      "Les sites en bordure de coupes forestieres attirent l'orignal pour le brout de repousse",
      "Un site principal (le plus productif) + 2-3 sites alternatifs (conditions de vent differentes)",
      "Partager la gestion du reseau avec 2-3 partenaires de chasse pour diviser l'effort"
    ],
    chevreuil: [
      "Reseau de 2-3 salines espacees de 500-1500 m dans le territoire d'un male dominant",
      "Chaque site avec un vent dominant different pour garantir 1 session productive par condition",
      "Site A: vent NO (condition la plus frequente au Quebec en automne)",
      "Site B: vent SO ou NE (conditions alternatives)",
      "Les sentiers entre les sites sont des corridors de patrouille de pre-rut — les surveiller",
      "Ne pas installer 2 sites sur le meme corridor (cannibalisation de frequentation)",
      "En gestion restrictive: le reseau entier respecte le meme standard de recolte (age minimum)"
    ],
    ours: [
      "Reseau de 2-4 sites espaces de 3-8 km dans le domaine vital de l'ours",
      "Chaque site avec un attractif DIFFERENT: melasse, mais, poisson, cerises",
      "L'ours qui visite 2+ sites du reseau est mieux cerne (pattern plus predictible)",
      "Cameras cellulaires sur TOUS les sites pour savoir ou l'ours est actif en temps reel",
      "Alterner les sessions entre les sites pour ne pas conditionner l'ours a votre presence sur un seul site",
      "En zone de forte densite: chaque site attire des ours differents — diversifier les recoltes"
    ],
    wapiti: [
      "Reseau de 2-3 salines le long du corridor de migration saisonniere",
      "Sites a differentes altitudes: fond de vallee (arrivee mai), mi-pente (ete), alpage (aout)",
      "Les wapitis visitent differents sites du reseau selon la saison et l'altitude",
      "Coordonner le reseau avec les guides de chasse locaux pour une couverture optimale",
      "Un site de pre-rut (mi-pente, pres d'une zone de bugle) est le plus productif en septembre"
    ],
    dindon: [
      "2 sites: un pres du perchoir nocturne, un sur le corridor d'alimentation",
      "Le site du perchoir est visite a l'aube, le site d'alimentation en mi-journee",
      "En zone avec plusieurs groupes: 1 reseau par groupe identifie",
      "Le reseau permet de s'adapter au deplacement du groupe si un site est inactif",
      "Coordonner avec le proprietaire agricole pour l'acces aux 2 sites"
    ],
  },
  strategies_optimisation: {
    orignal: ["3-5 sites couvrant 10-25 km2", "Vents differents par site", "Corridors inter-sites surveilles", "Site principal + alternatives"],
    chevreuil: ["2-3 sites a 500-1500 m", "1 site par condition de vent", "Pas 2 sites meme corridor", "Gestion restrictive uniforme"],
    ours: ["2-4 sites a 3-8 km", "Attractifs differents par site", "Cameras cellulaires partout", "Alternance des sessions"],
    wapiti: ["2-3 sites sur corridor migration", "Altitudes differentes", "Site pre-rut = prioritaire", "Coordination guides locaux"],
    dindon: ["2 sites: perchoir + alimentation", "1 reseau par groupe", "Adaptation au deplacement", "Coordination proprietaire"],
  },
  techniques_chasse: {
    orignal: ["Choisir le site du jour en fonction du vent: vent NO = Site A, vent NE = Site B", "Les corridors inter-sites sont des axes de deplacement privilegies — embuscade possible"],
    chevreuil: ["Un reseau de 3 sites permet de chasser productiblement 80-90% des jours de la saison (vent toujours favorable sur au moins 1 site)", "Le male en pre-rut patrouille entre les sites du reseau — surveiller les corridors de liaison"],
    ours: ["Les cameras cellulaires revelent quel site est le plus actif — se deplacer en consequence", "Alterner les sites pour ne pas saturer l'ours de presence humaine sur un seul point"],
    wapiti: ["Suivre la migration en altitude: chasser le site de fond de vallee en mai, le site d'alpage en aout", "Le wapiti qui quitte un site visite souvent le site suivant du reseau dans les 24-48 h"],
    dindon: ["Le site du perchoir est optimal pour la chasse matinale (aube), le site d'alimentation pour la mi-journee", "Si le dindon deserte un site, il se reporte souvent sur l'autre site du reseau"],
  },
  erreurs_a_eviter: {
    orignal: ["Concentrer tous les sites dans la meme zone de vent (inutile par vent contraire)", "Sites trop rapproches (<1 km) qui se cannibalisent", "Negliger les corridors inter-sites (opportunites d'interception perdues)"],
    chevreuil: ["2 sites sur le meme corridor de chevreuil (le chevreuil visite un seul des deux)", "Sites trop eloignes (>2 km) qui ne couvrent pas le meme territoire de male"],
    ours: ["Meme attractif sur tous les sites (l'ours se desinteresse — varier les stimulations)", "Sites trop rapproches (<2 km) sans diversification d'habitat"],
    wapiti: ["Tous les sites a la meme altitude (ne couvre pas la migration altitudinale)", "Negliger la coordination avec les autres chasseurs du secteur"],
    dindon: ["Un seul site pour 2+ groupes distincts (couverture insuffisante)", "Sites places sans lien avec les perchoirs identifies"],
  },
  optimisations_saisonnieres: { printemps: "Activer tous les sites du reseau pour la sortie hivernale des animaux. Verifier la complementarite apres la fonte.", ete: "Evaluer la performance de chaque site. Fermer les sites sous-performants et ouvrir de nouveaux sites si necessaire.", automne: "Utiliser le reseau strategiquement: site optimal selon le vent du jour. Pas de modification.", hiver: "Bilan du reseau. Analyse des donnees cameras. Planification des ajouts/suppressions de sites." },
  optimisations_support: ["Carte GPS du reseau avec tous les sites, corridors, et conditions de vent", "Tableau de bord: frequentation par site par saison (cameras trail)", "Application mobile de decision: quel site chasser selon le vent du jour"],
  optimisations_meteo: ["Vent NO: Site A. Vent NE: Site B. Vent SE: Site C — tableau de decision", "Front froid: priorite au site le plus productif du reseau", "Pluie: tous les sites sont productifs (animaux actifs + odeur humaine lavee)"],
  optimisations_pression: ["En zone haute pression: distribuer les sessions sur le reseau pour eviter la sursollicitation d'un seul site", "Partager le reseau avec 2-3 partenaires pour maximiser la couverture avec moins de visites par personne"],
  thresholds: { green: "80-100: 3+ sites complementaires, couverture vent 360 degres, corridors surveilles, frequentation documentee par site", yellow: "50-79: 2 sites partiellement complementaires, couverture vent partielle, corridors non surveilles", red: "0-49: 1 seul site, aucune couverture alternative, aucun reseau planifie" },
  sources: [
    "NDA — Building a Network of Mineral Sites for Optimal Coverage (2024)",
    "MFFP Quebec — Gestion integree du territoire de chasse (2023)",
    "QDMA (archives) — Multi-Site Mineral Management for Trophy Deer",
    "RMEF — Elk Mineral Site Networks Along Migration Corridors (2023)",
    "Mississippi State University Deer Lab — Multi-Site Strategy for Mature Buck Harvest (2022)",
    "NWTF — Turkey Hunting Property Management: Multi-Site Setup (2024)",
  ],
};

// =====================================================================
// 9. POTENTIEL D'EXPANSION — P2
// =====================================================================
export const potentiel_expansion = {
  title: "Potentiel d'expansion — Possibilite d'agrandir ou ameliorer le reseau de salines",
  definition: "Evaluation du potentiel du site et du territoire environnant pour l'ajout de nouvelles salines, de nouveaux affuts, ou l'amelioration des installations existantes. Inclut la disponibilite de terrain propice, les droits d'acces fonciers, la capacite de charge faunique de la zone, et les possibilites d'amenagement (food plots, corridors artificiels, points d'eau).",
  methodology: "Score sur 100: terrain disponible (30 pts — superficie exploitable), droits d'acces (25 pts — propriete/bail/ZEC), capacite de charge faunique (25 pts — densite population vs habitat), possibilites d'amenagement (20 pts — food plots, corridors, points d'eau). Sources: cadastre MRNF, donnees MFFP densite population, evaluation terrain.",
  justification: {
    orignal: "Un territoire de 25-100 km2 peut supporter un reseau de 5-10 salines si la densite d'orignal est suffisante (>1 orignal/10 km2 au Quebec). L'expansion se fait par l'ajout de sites sur des corridors non couverts, en bordure de coupes forestieres recentes (brout abondant), ou pres de plans d'eau non exploites. Les droits de chasse en terre publique (ZEC, reserves) permettent generalement l'expansion sans contrainte fonciere.",
    chevreuil: "Le territoire typique d'un chasseur de chevreuil est de 1-10 km2. L'expansion se fait par l'amelioration de l'habitat (food plots, hinge cuts pour augmenter le couvert lateral) plutot que par l'ajout massif de sites. La gestion restrictive (age minimum de recolte) est la strategie d'expansion la plus efficace: augmenter la qualite des males plutot que le nombre de sites.",
    ours: "L'expansion en zone ours est limitee par la securite et la logistique. Chaque nouveau site impose un investissement en contenants anti-ours, cameras blindees, et visites d'entretien en duo. L'expansion est recommandee uniquement si la densite d'ours est elevee (>0.5 ours/km2) et si les ressources humaines sont suffisantes.",
    wapiti: "L'expansion en zone wapiti suit les corridors de migration: ajouter des sites aux points de transit identifies par les cameras trail. Les sites d'expansion doivent couvrir des altitudes differentes pour suivre les deplacements altitudinaux saisonniers. L'expansion est souvent limitee par l'accessibilite en terrain montagneux.",
    dindon: "L'expansion en zone dindon consiste a identifier de nouveaux groupes (perchoirs, corridors) dans le meme secteur agricole. Chaque nouveau groupe identifie justifie un nouveau site. L'expansion est facilitee par les relations avec les proprietaires agricoles qui ouvrent de nouveaux acces a leur terre.",
  },
  recommendations_terrain: {
    orignal: [
      "Prospecter les coupes forestieres recentes (0-10 ans) pour les sites de brout",
      "Identifier les plans d'eau non exploites avec des salines naturelles potentielles",
      "Verifier les droits de chasse et d'amenagement en terre publique (ZEC, reserve, TPI)",
      "Evaluer la densite d'orignal par zone (donnees MFFP, inventaires aeriens)",
      "Planifier l'expansion sur 3-5 ans (1 nouveau site par an)",
      "Prioriser les corridors non couverts par le reseau existant",
      "Evaluer le potentiel de food plots en clairiere (trefle, avoine pour attirer les femelles)",
      "Considerer les ententes de gestion avec les clubs de chasse voisins"
    ],
    chevreuil: [
      "Prioriser l'amelioration de l'habitat existant plutot que l'ajout de sites",
      "Hinge cuts: abattre partiellement des arbres pour creer du couvert lateral instantane",
      "Food plots: trefle blanc, brassica, avoine — 0.1-0.5 ha par site",
      "Gestion restrictive: ne recolter que les males >3.5 ans pour maximiser le potentiel trophee",
      "Coordonner la gestion restrictive avec les voisins (cooperative de gestion du chevreuil)",
      "Evaluer le ratio males/femelles via les cameras trail — ajuster la recolte de femelles",
      "Planter des arbres fruitiers (pommiers) pour diversifier l'alimentation",
      "Creer des corridors boises artificiels entre les habitats fragmentes"
    ],
    ours: [
      "Expansion uniquement si la densite d'ours justifie un nouveau site (>0.5 ours/km2)",
      "Chaque nouveau site = investissement complet: contenants anti-ours, cameras blindees, boitiers acier",
      "Visites d'entretien en duo pour chaque site — budget humain a evaluer",
      "Prioriser l'amelioration des sites existants plutot que l'ajout de sites",
      "Identifier les zones de bleuets, de framboises, et de ruisseaux a truites non exploitees",
      "Considerer un site saisonnier (juin-octobre seulement) pour reduire l'investissement"
    ],
    wapiti: [
      "Ajouter des sites aux points de transit non couverts sur le corridor de migration",
      "Couvrir differentes altitudes: fond de vallee, mi-pente, alpage",
      "Coordonner avec les guides de chasse pour identifier les zones sous-exploitees",
      "L'accessibilite en montagne est le facteur limitant principal — evaluer les sentiers",
      "Planifier l'expansion selon la capacite de portage disponible (equipement lourd en altitude)"
    ],
    dindon: [
      "Identifier de nouveaux groupes de dindons par les observations matinales (gobble mars-avril)",
      "Chaque perchoir identifie = potentiel d'un nouveau site",
      "Developper les relations avec les proprietaires agricoles pour l'acces a de nouveaux terrains",
      "En zone publique: prospecter les forets ouvertes avec des chenes matures (glands)",
      "L'expansion en zone dindon est souvent la moins couteuse (materiel leger, acces facile)"
    ],
  },
  strategies_optimisation: {
    orignal: ["Expansion 1 site/an sur 3-5 ans", "Coupes forestieres recentes", "Plans d'eau non exploites", "Droits ZEC/TPI verifies"],
    chevreuil: ["Habitat > ajout de sites", "Hinge cuts + food plots", "Gestion restrictive cooperative", "Pommiers pour diversification"],
    ours: ["Expansion si densite >0.5/km2", "Investissement complet par site", "Amelioration des sites existants en priorite", "Sites saisonniers possibles"],
    wapiti: ["Points de transit non couverts", "Altitudes differentes", "Coordination avec guides", "Limite: accessibilite montagne"],
    dindon: ["Nouveaux groupes = nouveaux sites", "Relations proprietaires agricoles", "Forets a chenes en zone publique", "Expansion la moins couteuse"],
  },
  techniques_chasse: {
    orignal: ["Un reseau de 5+ sites offre une flexibilite maximale: toujours un site productif quelle que soit la condition", "Les sites d'expansion pres des coupes recentes attirent les jeunes orignaux en dispersion"],
    chevreuil: ["Les food plots augmentent la densite de chevreuil locale de 30-50% en 2-3 ans", "La gestion restrictive augmente la taille moyenne des ramures de 20-30% en 3-5 ans"],
    ours: ["Un 2e site avec un attractif different attire des ours differents — diversifier les recoltes", "L'expansion controlee permet de maintenir la pression de chasse sans sursolliciter un seul site"],
    wapiti: ["Les sites d'expansion a differentes altitudes prolongent la saison de chasse de 2-4 semaines", "Le site de fond de vallee est productif en mai-juin, le site d'alpage en juillet-aout"],
    dindon: ["Chaque nouveau groupe identifie double les opportunites de chasse", "En zone avec 3+ groupes: rotation quotidienne entre les sites pour maximiser les chances"],
  },
  erreurs_a_eviter: {
    orignal: ["Expansion excessive sans densite suffisante (sites deserts = investissement perdu)", "Negliger les droits fonciers avant l'installation (conflit legal)", "Expansion sans plan de gestion a long terme"],
    chevreuil: ["Ajouter des sites sans ameliorer l'habitat (le nombre de sites ≠ la qualite de la chasse)", "Expansion sans gestion restrictive (les males matures sont recoltes trop jeunes)"],
    ours: ["Expansion sans les ressources humaines pour l'entretien en duo (securite compromise)", "Multiplier les sites sans contenants anti-ours adequats (ours conditionne = danger)"],
    wapiti: ["Expansion sans evaluer l'accessibilite en altitude (site inaccessible = investissement perdu)", "Negliger la coordination avec les autres utilisateurs du territoire"],
    dindon: ["Expansion sans identifier de nouveaux groupes (site sans dindon = echec)", "Negliger la relation avec le proprietaire agricole (perte d'acces)"],
  },
  optimisations_saisonnieres: { printemps: "Prospection: identifier les nouveaux corridors, les plans d'eau, les coupes recentes. Signer les ententes d'acces.", ete: "Installation des nouveaux sites. Plantation des food plots. Amenagement des corridors artificiels.", automne: "Evaluation des nouveaux sites. Documentation des premieres frequentations par cameras trail.", hiver: "Bilan de l'expansion. Analyse du ROI par site. Planification de la saison suivante." },
  optimisations_support: ["Carte cadastrale du territoire (MRNF) pour identifier les proprietes et droits d'acces", "Donnees MFFP de densite de population par zone de chasse", "Food plot seed mix adapte: trefle blanc, brassica, avoine (semences certifiees)"],
  optimisations_meteo: ["Planter les food plots apres les derniers gels (mi-mai au Quebec)", "Les coupes forestieres recentes offrent plus de brout les annees humides (croissance vegetale)"],
  optimisations_pression: ["L'expansion du reseau distribue la pression sur plus de sites, reduisant la sursollicitation", "Coordination inter-chasseurs pour eviter la duplication de sites dans la meme zone"],
  thresholds: { green: "80-100: Terrain disponible, droits d'acces confirmes, densite faunique suffisante, budget d'expansion planifie", yellow: "50-79: Potentiel modere, droits partiels, densite acceptable, budget limite", red: "0-49: Aucun terrain disponible, droits d'acces absents, densite faible, aucun budget" },
  sources: [
    "MFFP Quebec — Gestion de la population d'orignal par zone de chasse (2024)",
    "NDA — Habitat Improvement Strategies for Better Deer Hunting (2024)",
    "QDMA (archives) — Food Plot Design and Management",
    "MRNF — Cadastre des terres publiques du Quebec (2024)",
    "RMEF — Expanding Mineral Site Networks in Elk Country (2023)",
    "Bear Trust International — Sustainable Bear Bait Site Expansion (2022)",
  ],
};

// =====================================================================
// 10. COUT DES MINERAUX ANNUEL — P1
// =====================================================================
export const cout_mineraux_annuel = {
  title: "Cout des mineraux annuel — Budget mineral pour la saison complete",
  definition: "Evaluation du cout total annuel en mineraux, blocs de sel, attractifs et supplements necessaires pour maintenir la saline en operation pendant toute la saison active (5-8 mois). Inclut le prix d'achat des mineraux, la frequence de remplacement, les quantites par espece, et le ratio cout/frequentation animale. Un budget mineral optimise maximise la frequentation par dollar investi.",
  methodology: "Score sur 100: cout/frequentation ratio (40 pts — $/detection camera trail), quantite adaptee a l'espece (25 pts — kg/mois optimal), qualite minerale (20 pts — composition Na/Ca/P), durabilite des blocs (15 pts — taux de dissolution). Sources: prix detaillants (Coop, BMR, boutiques chasse), donnees cameras trail, analyses minerales.",
  justification: {
    orignal: "L'orignal consomme 100-200 g de sel par visite. Un bloc de 20-25 kg dure 4-6 semaines en saison active. Budget annuel typique: 4-6 blocs x 15-25$ = 60-150$/an par site. Les blocs comprimes de haute qualite (Trophy Rock, Redmond) coutent 35-50$ mais durent 50% plus longtemps. Le cout par detection camera est de 0.50-1.50$ sur un bon site.",
    chevreuil: "Le chevreuil consomme moins par visite (50-100 g) mais visite plus frequemment. Blocs de 10-15 kg remplaces toutes les 3-4 semaines. Budget annuel: 6-8 blocs x 10-18$ = 60-144$/an. Les blocs specialises (mineral avec calcium et phosphore pour la croissance des ramures) coutent 20-30$ mais augmentent l'attractivite de 30%.",
    ours: "L'ours necessite des attractifs en PLUS des mineraux: melasse (20-40$/20L), mais concasse (15-25$/25 kg), poisson fume (variable). Budget annuel total: 200-500$/an par site (mineraux + attractifs). Le cout est eleve mais le taux de reussite avec attractifs est de 70-80% contre 30-40% sans.",
    wapiti: "Le wapiti a des besoins mineraux eleves (calcium, phosphore) pour la croissance du panache. Blocs de 25 kg specialises (Trace Mineral Block) toutes les 6-8 semaines. Budget: 3-5 blocs x 20-30$ = 60-150$/an. Les blocs de haute qualite minerale (sodium + calcium + phosphore) coutent plus mais attirent les males en croissance de panache.",
    dindon: "Le dindon necessite des grains et mineraux legers: mais concasse, graines de tournesol, gravier mineral. Budget: 20-50$/an par site (le moins couteux de toutes les especes). Le cout par detection est de 0.10-0.30$ — excellent ratio.",
  },
  recommendations_terrain: {
    orignal: [
      "Budget: 4-6 blocs de 20-25 kg par saison = 60-150$/an par site",
      "Blocs comprimes (Trophy Rock) durent 50% plus longtemps que les blocs moules",
      "Acheter en lot de 10+ blocs pour des rabais de 15-20% (Coop, BMR)",
      "Stocker les blocs non-utilises dans un contenant etanche (eviter l'humidite prematuree)",
      "Le bloc comprime resiste mieux a la pluie — ideal pour les sites exposes",
      "Alterner entre sel pur (NaCl) et bloc mineral complexe (Na + Ca + P + oligo-elements)",
      "Cout par detection camera optimal: <1.50$/detection pour un site rentable",
      "Evaluer le ROI: si <50 detections/saison malgre 100$ de mineraux, reevaluer le site"
    ],
    chevreuil: [
      "Budget: 6-8 blocs de 10-15 kg = 60-144$/an par site",
      "Blocs specialises avec calcium et phosphore (croissance ramure): 20-30$/bloc",
      "Les blocs mineraux augmentent l'attractivite de 30% vs le sel pur",
      "Granules mineraux en complement des blocs (saupoudrer sur le sol = lechage au sol)",
      "Acheter les blocs en debut de saison pour beneficier des promotions printanieres",
      "Stocker les blocs dans un seau etanche anti-odeur pour le transport",
      "Cout par detection optimal: <1.00$/detection pour un site productif",
      "Le meilleur investissement: bloc mineral complexe + mock scrape = frequentation maximale"
    ],
    ours: [
      "Budget total: 200-500$/an (mineraux + attractifs — le plus couteux des 5 especes)",
      "Melasse: 20-40$/20L, 1 bidon toutes les 2-3 semaines en saison active",
      "Mais concasse: 15-25$/25 kg, 1 sac toutes les 2 semaines",
      "Poisson fume ou huile de poisson: attractif puissant mais plus couteux (50-100$/saison)",
      "Le ratio cout/reussite est favorable: 70-80% de reussite avec attractifs vs 30-40% sans",
      "Verifier la reglementation: certaines zones interdisent les appats (attractifs mineraux seulement)",
      "Contenants anti-ours pour les attractifs: investissement initial de 50-100$ (reutilisable)",
      "Alterner les attractifs pour maintenir la curiosite de l'ours"
    ],
    wapiti: [
      "Budget: 3-5 blocs specialises x 20-30$ = 60-150$/an par site",
      "Blocs Trace Mineral (Na + Ca + P + Fe + Zn) pour la croissance du panache",
      "Le wapiti prefere les blocs de haute qualite minerale — investir dans la qualite plutot que la quantite",
      "Un bloc frais de haute qualite en pre-rut attire les males matures en recherche de calcium",
      "Stocker les blocs en altitude dans un contenant etanche et verrouille (protection ours/intemperies)",
      "Cout par detection optimal: <1.50$/detection (frequentation modere mais de haute qualite)"
    ],
    dindon: [
      "Budget: 20-50$/an (le moins couteux de toutes les especes)",
      "Mais concasse: 10-15$/25 kg, 1 sac pour la saison complete",
      "Graines de tournesol: 15-20$/10 kg (complement attractif)",
      "Gravier mineral fin: 5-10$/sac — le dindon gratte et picore",
      "Cout par detection optimal: <0.30$/detection — meilleur ratio de toutes les especes",
      "Reapprovisionner en petites quantites frequentes plutot qu'un gros depot (grains frais = plus attractifs)"
    ],
  },
  strategies_optimisation: {
    orignal: ["Blocs comprimes pour durabilite", "Achat en lot 10+", "Alterner sel pur et mineral complexe", "Seuil ROI: <1.50$/detection"],
    chevreuil: ["Blocs calcium-phosphore pour ramure", "Granules au sol en complement", "Achat promotions printanieres", "Seuil ROI: <1.00$/detection"],
    ours: ["Melasse + mais = combo optimal", "Alterner les attractifs", "Contenants anti-ours reutilisables", "Verifier reglementation appats"],
    wapiti: ["Blocs Trace Mineral haute qualite", "Qualite > quantite", "Bloc frais en pre-rut", "Stockage etanche en altitude"],
    dindon: ["Mais concasse = base economique", "Petites quantites frequentes", "Gravier mineral pour le grattage", "Meilleur ratio $/detection"],
  },
  techniques_chasse: {
    orignal: ["Un bloc mineral frais genere un pic de visites dans les 48-72 h — chasser 3 jours apres le remplacement", "Les blocs de haute qualite minerale attirent les males en quete de sodium en pre-rut"],
    chevreuil: ["Les blocs avec calcium attirent specifiquement les males en croissance de velours (mai-aout)", "Le sol impregne de mineraux devient un attractif permanent meme apres dissolution du bloc"],
    ours: ["Les attractifs frais (melasse + mais) generent un pic de frequentation dans les 24-48 h — chasser juste apres le remplacement", "Le poisson fume est l'attractif le plus puissant mais le plus couteux — reserver pour les sessions critiques"],
    wapiti: ["Le bloc mineral de haute qualite en juillet-aout attire les males qui cherchent du calcium pour le panache", "Un bloc frais en pre-rut est le meilleur investissement $/recolte"],
    dindon: ["Les grains frais attirent le dindon dans les 24 h — reapprovisionner 2 jours avant la chasse", "Le mais concasse est l'attractif le plus economique et le plus efficace pour le dindon"],
  },
  erreurs_a_eviter: {
    orignal: ["Acheter des blocs de basse qualite (dissolution trop rapide, attractivite faible)", "Laisser les blocs se dissoudre completement (perte de fidelite du site)"],
    chevreuil: ["Utiliser uniquement du sel pur (le chevreuil a besoin de calcium et phosphore en plus)", "Deposer les blocs directement sur un sol humide (dissolution acceleree + gaspillage)"],
    ours: ["Negliger le budget attractifs (les mineraux seuls sont insuffisants pour l'ours)", "Utiliser des attractifs interdits dans certaines zones (infraction reglementaire)"],
    wapiti: ["Blocs de basse qualite minerale (le wapiti prefere les blocs riches en oligo-elements)", "Stocker les blocs a l'air libre en altitude (degradation par intemperies)"],
    dindon: ["Depot massif de grains (pourriture + attraction de rongeurs)", "Grains humides ou moisis (indigestion potentielle pour le dindon)"],
  },
  optimisations_saisonnieres: { printemps: "Achat des blocs pour la saison. Profiter des promotions printanieres. Premier remplacement des la fonte.", ete: "Remplacement regulier des blocs (dissolution acceleree par la chaleur). Verifier la qualite des blocs restants.", automne: "Bloc frais pour le pre-rut. Budget attractifs ours (hyperphagie). Derniers achats de la saison.", hiver: "Bilan des depenses. Calculer le cout/detection. Planifier le budget de la saison suivante." },
  optimisations_support: ["Blocs comprimes Trophy Rock (25 kg, dissolution lente, 35-50$)", "Blocs Redmond Natural Mineral (25 kg, 15-25$)", "Melasse de canne non-sulfuree (20L, 20-40$)", "Mais concasse non-OGM (25 kg, 15-25$)"],
  optimisations_meteo: ["Pluie prolongee: dissolution acceleree — prevoir un bloc supplementaire", "Secheresse: dissolution ralentie — le bloc dure plus longtemps", "Gel: le bloc gele ne se dissout pas — pas de remplacement necessaire en hiver"],
  optimisations_pression: ["En zone haute pression: le cout est justifie par la fidelisation de la faune au site (les animaux reviennent malgre la pression)", "Budget partage entre partenaires de chasse pour reduire le cout individuel"],
  thresholds: { green: "80-100: Budget optimise, cout/detection <1.00$, blocs haute qualite, remplacement regulier, ROI positif", yellow: "50-79: Budget acceptable, cout/detection 1.00-2.00$, blocs standard, remplacement irregulier", red: "0-49: Budget excessif ou inexistant, cout/detection >2.00$, blocs basse qualite ou absents, ROI negatif" },
  sources: [
    "NDA — Cost-Effective Mineral Site Management (2024)",
    "QDMA (archives) — Mineral Supplementation ROI Analysis",
    "MFFP Quebec — Reglementation sur les appats et attractifs par zone de chasse (2024)",
    "Trophy Rock — Composition minerale et taux de dissolution (specifications fabricant, 2025)",
    "Redmond Minerals — Natural Trace Mineral Block Specifications (2025)",
    "Bear Trust International — Bait and Attractant Cost Analysis for Black Bear (2023)",
  ],
};

// =====================================================================
// 11. COUT DE TRANSPORT — P2
// =====================================================================
export const cout_transport = {
  title: "Cout de transport — Frais de deplacement et logistique",
  definition: "Evaluation du cout total de transport pour acceder au site de saline: carburant vehicule/VTT, usure du vehicule, peages/droits d'acces (ZEC, reserve), et temps de deplacement converti en valeur economique. Un cout de transport eleve reduit la rentabilite globale du site et peut limiter la frequence des visites d'entretien.",
  methodology: "Score sur 100: distance aller-retour domicile-site (35 pts), cout carburant (25 pts — prix/L x consommation), droits d'acces (20 pts — ZEC/reserve/prive), temps de deplacement (20 pts — heures x valeur horaire estimee). Sources: cartes routieres, prix carburant CAA, tarifs ZEC/SEPAQ.",
  justification: {
    orignal: "La chasse a l'orignal au Quebec implique souvent des deplacements de 100-500 km aller simple (zone 1-28). Le cout carburant pour un camion 4x4 (15-18 L/100 km) + VTT (remorque) peut atteindre 200-500$ par deplacement. Les droits d'acces ZEC coutent 15-30$/jour. Le budget transport annuel peut depasser le budget mineraux de 5-10x.",
    chevreuil: "La chasse au chevreuil est souvent plus locale (20-100 km), reduisant significativement les couts de transport. En zone periurbaine, le deplacement peut etre de <30 min. Les droits d'acces en terre privee sont souvent gratuits (entente avec le proprietaire). Budget transport typique: 50-200$/saison.",
    ours: "La chasse a l'ours noir necessite des deplacements similaires a l'orignal (100-300 km). Le transport d'attractifs lourds (40-60 kg de melasse, mais) ajoute du poids et de la consommation de carburant. Le duo obligatoire en zone ours double le vehicule ou impose le covoiturage.",
    wapiti: "La chasse au wapiti en Colombie-Britannique, Alberta ou Manitoba implique des deplacements de 500-3000 km depuis le Quebec. Les couts incluent le carburant, l'hebergement, les permis de chasse non-resident, et les frais de guide. Budget total deplacement: 2000-10000$ par expedition.",
    dindon: "La chasse au dindon est la moins couteuse en transport: zones souvent accessibles en <1 h de route. Les droits d'acces en terre agricole sont generalement gratuits. Budget transport: 20-100$/saison — le plus faible de toutes les especes.",
  },
  recommendations_terrain: {
    orignal: ["Calculer le cout aller-retour COMPLET: carburant + usure + peages + droits ZEC", "Covoiturage avec les partenaires de chasse pour diviser les couts", "Planifier les sessions sur 3-5 jours consecutifs pour amortir le deplacement", "Stocker du carburant supplementaire au camp pour le VTT", "Preferer les ZEC aux pourvoiries (droits d'acces 5-10x moins chers)", "Entretenir le VTT regulierement pour eviter les pannes couteuses en zone eloignee"],
    chevreuil: ["Privilegier les sites proches du domicile (<50 km) pour maximiser les sessions", "Les sites en terre privee eliminent les droits d'acces", "Combiner les visites d'entretien avec les sessions de chasse pour economiser un deplacement", "En zone ZEC: acheter le forfait saisonnier plutot que les droits journaliers"],
    ours: ["Covoiturage obligatoire (duo) — diviser les couts en 2", "Transporter les attractifs en lot pour reduire le nombre de deplacements", "Evaluer le rapport cout-transport/taux-de-reussite avant de choisir un site eloigne", "Les pourvoiries incluent souvent le transport dans leur forfait — comparer les options"],
    wapiti: ["Budget transport = poste de depense #1 pour le wapiti depuis le Quebec", "Expedition de groupe (3-4 chasseurs) pour diviser les couts vehicule et hebergement", "Considerer l'avion + location sur place pour les distances >2000 km", "Les guides locaux incluent souvent le transport local dans le forfait"],
    dindon: ["Transport le moins couteux — privilegier les sites proches (<30 km)", "En zone agricole: acces direct sans frais supplementaires", "Combiner les sessions de reperage et de chasse pour economiser les deplacements"],
  },
  strategies_optimisation: { orignal: ["Sessions 3-5 jours pour amortir", "Covoiturage", "ZEC vs pourvoirie", "VTT entretenu"], chevreuil: ["Sites proches <50 km", "Terre privee sans frais", "Forfait ZEC saisonnier"], ours: ["Covoiturage duo", "Attractifs en lot", "Rapport cout/reussite"], wapiti: ["Expedition groupe 3-4", "Avion si >2000 km", "Guide avec transport inclus"], dindon: ["Sites <30 km", "Acces agricole gratuit", "Reperage + chasse combines"] },
  techniques_chasse: { orignal: ["Une session de 5 jours amortit le deplacement et multiplie les opportunites par 5", "Les sessions en milieu de semaine ont moins de pression — meilleur ratio cout/opportunite"], chevreuil: ["Un site a 20 km permet des sessions matinales frequentes sans impact financier majeur", "En zone periurbaine: le cout de transport est negligeable — investir dans la qualite du site"], ours: ["Le covoiturage en duo est obligatoire ET economique — toujours chasser en equipe", "Les attractifs en lot reduisent le nombre de deplacements de 30-50%"], wapiti: ["L'expedition de groupe divise les couts mais augmente les opportunites de succes (plus d'yeux, plus de terrain couvert)", "Le guide local connait les corridors — son cout est amorti par le taux de reussite eleve"], dindon: ["La proximite du site est le principal avantage du dindon — sessions spontanees possibles", "Un site a <30 km permet de chasser chaque matin de la saison sans impact financier"] },
  erreurs_a_eviter: { orignal: ["Ne pas calculer le cout reel (carburant + usure + temps = souvent sous-estime)", "Sessions d'une seule journee pour un deplacement de 300+ km (amortissement insuffisant)"], chevreuil: ["Voyager 100+ km quand un site productif est disponible a 30 km", "Payer des droits d'acces eleves quand des terres privees sont disponibles gratuitement"], ours: ["Deplacements en solo (obligation du duo = covoiturage logique)", "Multiplier les deplacements courts au lieu d'un seul deplacement avec stock d'attractifs"], wapiti: ["Expedition solo (couts non-partages + risque securitaire en montagne)", "Ne pas comparer les options avion vs vehicule pour les tres longues distances"], dindon: ["Depenser plus en transport qu'en equipement pour le dindon (incoherent)"] },
  optimisations_saisonnieres: { printemps: "Reprise des deplacements. Planifier le calendrier de visites pour minimiser les allers-retours.", ete: "Deplacements d'amenagement combines avec les visites d'entretien.", automne: "Budget transport maximal (saison de chasse active). Amortir les couts sur des sessions multi-jours.", hiver: "Aucun deplacement au site. Bilan des couts de transport de la saison." },
  optimisations_support: ["Calculateur de cout par deplacement (carburant + usure + droits)", "Forfait ZEC saisonnier pour les chasseurs frequents", "Groupe WhatsApp pour coordonner le covoiturage"],
  optimisations_meteo: ["Reporter les deplacements si la meteo annonce des conditions defavorables (economiser le deplacement)", "Les journees de front froid justifient le deplacement (activite faunique maximale)"],
  optimisations_pression: ["En zone haute pression: les deplacements en semaine sont plus rentables (moins de trafic, moins de pression)"],
  thresholds: { green: "80-100: Cout transport <20% du budget total, deplacement <100 km, droits d'acces minimaux", yellow: "50-79: Cout transport 20-40% du budget, 100-300 km, droits d'acces moderes", red: "0-49: Cout transport >40% du budget, >300 km, droits d'acces eleves, sessions non-rentables" },
  sources: ["CAA Quebec — Cout d'utilisation d'un vehicule 4x4 (2025)", "SEPAQ — Tarifs reserves fauniques et ZEC (2025)", "MFFP Quebec — Permis de chasse: tarifs et conditions (2025)", "NDA — Cost Analysis of Hunting Operations (2024)"],
};

// =====================================================================
// 12. COUT EN TEMPS — P2
// =====================================================================
export const cout_temps = {
  title: "Cout en temps — Temps investi par visite et par saison",
  definition: "Evaluation du temps total investi pour operer le site de saline: temps de deplacement aller-retour, temps d'entretien sur site, temps de sessions de chasse, et temps de preparation/nettoyage. Le temps est la ressource la plus limitee du chasseur — un site optimise minimise le temps non-productif (deplacement, entretien) et maximise le temps productif (observation, chasse).",
  methodology: "Score sur 100: ratio temps productif/temps total (40 pts), temps de deplacement (25 pts), temps d'entretien (20 pts), temps de preparation (15 pts). Sources: carnet de terrain, chronometre de visite, GPS tracking.",
  justification: {
    orignal: "Une session d'orignal typique: 2-4 h de deplacement + 4-8 h d'affut + 1-2 h de preparation = 7-14 h par session. L'entretien necessite 2-4 h par visite (deplacement + intervention). Budget temps annuel: 80-200 h/saison. Le temps productif (observation/tir) ne represente souvent que 30-40% du temps total investi.",
    chevreuil: "Une session de chevreuil: 0.5-2 h de deplacement + 3-6 h d'affut + 0.5-1 h de preparation = 4-9 h par session. L'entretien est plus rapide (1-2 h par visite). Budget temps annuel: 40-120 h/saison. La proximite du site est le facteur #1 d'optimisation du temps.",
    ours: "Une session d'ours: 1-3 h de deplacement + 4-6 h d'affut (soir) + 1-2 h de preparation = 6-11 h par session. L'entretien en duo prend plus de temps (2-4 h). Budget temps annuel: 50-150 h/saison. Les sessions du soir (15h-21h) sont plus efficaces que les sessions completes.",
    wapiti: "Une expedition de wapiti: 1-3 jours de deplacement + 5-10 jours de chasse. Le temps investi est massif — une expedition de wapiti est un investissement de 7-14 jours complets. Le ratio temps/recolte est eleve mais l'experience est unique.",
    dindon: "Une session de dindon: 0.5-1 h de deplacement + 3-5 h de chasse + 0.5 h de preparation = 4-6.5 h par session. C'est l'espece la plus efficace en temps. Budget temps annuel: 20-60 h/saison.",
  },
  recommendations_terrain: {
    orignal: ["Chronometre chaque phase: deplacement, preparation, affut, retour", "Objectif: ratio temps productif >40% du temps total", "Sessions multi-jours pour amortir le temps de deplacement", "Preparation la veille: equipement charge, itineraire planifie, meteo verifiee", "Cameras cellulaires pour savoir AVANT de partir si le site est actif", "Combiner les sessions d'entretien pour reduire le nombre total de deplacements"],
    chevreuil: ["Privilegier les sites proches (<30 min de route) pour maximiser les sessions", "Sessions matinales possibles avant le travail si le site est a <20 km", "Preparation du sac la veille (checklist standardisee)", "Les cameras cellulaires economisent 2-3 deplacements de releve par saison"],
    ours: ["Sessions du soir (15h-21h): plus courtes et plus efficaces que les sessions completes", "Arriver a l'affut a 15h, quitter au coucher du soleil — 5-6 h productives", "Entretien en duo: diviser les taches pour reduire le temps sur site", "Cameras cellulaires pour verifier l'activite de l'ours avant de se deplacer"],
    wapiti: ["Planifier l'expedition 6 mois a l'avance pour optimiser chaque journee", "Guide local: economise 1-2 jours de reperage (connait les corridors)", "Sessions matinales et vesperales chaque jour (maximiser le temps en montagne)"],
    dindon: ["Sessions matinales courtes (5h-10h): le dindon est actif a l'aube", "Site proche = sessions spontanees les matins favorables", "Preparation minimale: appels, decoys, cartouches — 10 min de preparation"],
  },
  strategies_optimisation: { orignal: ["Multi-jours pour amortir", "Cameras cellulaires", "Preparation la veille", "Ratio productif >40%"], chevreuil: ["Sites <30 min", "Sessions avant travail", "Cameras eliminant les releves"], ours: ["Sessions soir 15h-21h", "Entretien duo divise", "Cellulaires avant deplacement"], wapiti: ["Expedition planifiee 6 mois", "Guide local", "Sessions matin + soir"], dindon: ["Sessions matin 5h-10h", "Preparation 10 min", "Sessions spontanees"] },
  techniques_chasse: { orignal: ["Une session de 3 jours produit plus d'opportunites que 3 sessions d'1 jour (moins de derangement cumule, plus de temps d'affut continu)", "Les cameras cellulaires permettent de choisir le MEILLEUR jour pour se deplacer — economiser les sessions improductives"], chevreuil: ["Un site a 20 min de route permet 40-50 sessions par saison vs 10-15 pour un site a 2 h", "Les sessions courtes et frequentes sont plus productives que les sessions longues et rares pour le chevreuil"], ours: ["La session du soir (15h-21h) capture 70% des visites d'ours — pas besoin de sessions de 12 h", "Le temps d'attente moyen pour voir un ours sur un bon site avec attractifs: 3-5 h"], wapiti: ["Le guide local economise 30-50% du temps total de l'expedition (connaissance terrain)", "Chaque jour en montagne = 2 sessions (matin 5h-10h + soir 15h-20h) — ne pas gaspiller les mi-journees"], dindon: ["Le dindon est le gibier le plus rapide a chasser: 1-3 h entre l'installation et l'opportunite de tir", "La saison de dindon est courte (2-3 semaines au Quebec) — maximiser chaque matin disponible"] },
  erreurs_a_eviter: { orignal: ["Ne pas chronometrer les phases (le temps improductif s'accumule sans le realiser)", "Sessions d'1 jour pour un deplacement de 3+ h (ratio temps productif <30%)"], chevreuil: ["Choisir un site eloigne quand un site productif est disponible pres de chez soi", "Ne pas utiliser les cameras cellulaires (deplacements de releve inutiles)"], ours: ["Sessions de 12 h quand 5-6 h du soir suffisent (fatigue + temps gaspille)", "Entretien en solo (plus long + moins securitaire)"], wapiti: ["Expedition sans guide dans un territoire inconnu (jours de reperage = temps perdu)", "Ne pas planifier les sessions matin + soir (mi-journees improductives)"], dindon: ["Sessions de 8 h quand le dindon est actif 3-4 h le matin (temps gaspille apres 10h)", "Ne pas profiter des matins de parade (la fenetre est courte et decisive)"] },
  optimisations_saisonnieres: { printemps: "Saison dindon: sessions courtes et efficaces. Preparation des sites pour l'automne.", ete: "Entretien combine: toutes les taches en 1 deplacement.", automne: "Saison majeure. Maximiser le temps productif. Sessions multi-jours.", hiver: "Planification. Aucun temps sur le terrain. Analyse des donnees cameras." },
  optimisations_support: ["Chronometre de visite sur smartphone", "Checklist de preparation pre-imprimee", "Sac de chasse pre-charge pour depart rapide"],
  optimisations_meteo: ["Reporter les sessions si la meteo est defavorable — economiser le temps", "Les jours de front froid justifient l'investissement en temps (activite faunique maximale)"],
  optimisations_pression: ["En zone haute pression: sessions courtes et discretes pour minimiser le temps expose", "Milieu de semaine: moins de pression = temps mieux investi"],
  thresholds: { green: "80-100: Ratio productif >50%, deplacement <1 h, entretien <15 min, sessions efficaces", yellow: "50-79: Ratio productif 30-50%, deplacement 1-3 h, entretien 15-30 min", red: "0-49: Ratio productif <30%, deplacement >3 h, entretien >30 min, temps majoritairement improductif" },
  sources: ["NDA — Time Management for Deer Hunters (2024)", "MFFP Quebec — Statistiques saisonnieres de chasse: effort vs recolte (2024)", "QDMA (archives) — Optimizing Hunt Time for Maximum Results"],
};

// =====================================================================
// 13. RETOUR SUR OBSERVATION — P1
// =====================================================================
export const retour_observation = {
  title: "Retour sur observation — Nombre d'observations qualitatives par saison",
  definition: "Evaluation du nombre et de la qualite des observations d'animaux obtenues sur le site par saison: detections cameras trail, observations directes depuis l'affut, et qualite des individus observes (males matures, femelles avec faons, especes multiples). Le retour sur observation mesure la productivite reelle du site et justifie l'investissement en temps, argent et effort.",
  methodology: "Score sur 100: nombre de detections cameras/saison (30 pts), observations directes/saison (25 pts), qualite des individus (25 pts — males matures, diversite d'especes), regularite de frequentation (20 pts — ecart-type entre semaines). Sources: logs cameras trail, carnet de terrain, photo-identification.",
  justification: {
    orignal: "Un site productif genere 100-300 detections cameras/saison et 5-15 observations directes depuis l'affut. Le ratio males/femelles sur camera indique la qualite du site: >30% de males = site premium. La presence de 3+ males differents confirme la connectivite du site avec des corridors multiples. Un site avec <50 detections/saison doit etre reevalue.",
    chevreuil: "Un bon site de chevreuil genere 200-500 detections cameras/saison et 10-30 observations directes. La photo-identification des males par leur ramure revele le nombre de males differents et leur fidelite au site. Le ratio males matures (>3.5 ans)/total males est le meilleur indicateur de la qualite du site: >20% = site premium.",
    ours: "Un site d'ours productif genere 50-150 detections cameras/saison. L'identification individuelle par les marques (cicatrices, tache pectorale, couleur) revele le nombre d'ours distincts (3-8 sur un bon site). Le mâle dominant est souvent le dernier a se presenter — sa presence confirme un site de haute qualite.",
    wapiti: "Un site de wapiti genere 30-100 detections cameras/saison (passage de hardes). La taille des groupes photographies (5-15 individus) et la presence de males matures (panache 5+ pointes/cote) determinent la qualite. Un site sur un corridor de migration actif produit des observations de haute valeur mais concentrees sur 3-4 mois.",
    dindon: "Un bon site de dindon genere 100-300 detections cameras/saison. Le nombre de males adultes (barbe, ergots visibles) et la presence de parades confirmees (male en roue) sont les indicateurs de qualite. La regularite quotidienne des visites est un excellent signe de fidelite du groupe.",
  },
  recommendations_terrain: {
    orignal: ["Objectif: 100+ detections cameras trail par saison", "Cataloguer chaque male par la forme du panache (photo-identification)", "Documenter le ratio males/femelles par mois (evolution saisonniere)", "Installer 3+ cameras pour couvrir tous les angles d'approche", "Analyser les heures de pointe: matin (5h-8h) et soir (17h-20h)", "Comparer la frequentation annee/annee pour identifier les tendances", "Un site avec 5+ males distincts photographies est un site premium", "Si <50 detections apres 2 saisons: envisager la relocalisation du site"],
    chevreuil: ["Objectif: 200+ detections cameras trail par saison", "Photo-identification de chaque male par sa ramure unique", "Suivi annuel de la croissance de chaque male identifie", "Ratio males matures >3.5 ans cible: >20% des males photographies", "Documenter la fidelite: les males qui reviennent 3+ saisons sont les meilleurs candidats", "Analyser les heures de visite par saison: diurne au printemps, nocturne en ete", "Correlation avec les conditions meteo: front froid = pic d'activite"],
    ours: ["Objectif: 50+ detections cameras trail par saison", "Identification individuelle par les marques corporelles (cicatrices, tache pectorale)", "Estimer le poids de chaque ours par comparaison photos (echelle sur le contenant)", "Documenter les heures de visite: le male dominant est souvent le dernier (19h-21h)", "3+ ours distincts = site de bonne qualite, 5+ = site premium", "Les femelles avec oursons sont DOCUMENTEES mais PAS chassees"],
    wapiti: ["Objectif: 30+ detections cameras trail par saison", "Taille des groupes photographies = indicateur de la sante de la population", "Identifier les males matures par le panache (photo-identification)", "Documenter les periodes de passage: arrivee (mai-juin) et depart (oct-nov)", "Comparer les corridors: quel corridor est le plus frequente", "Un site avec des males 6x6 (6 pointes/cote) est un site premium"],
    dindon: ["Objectif: 100+ detections cameras trail par saison", "Compter les males adultes (barbe visible) vs les jeunes (jakes)", "Documenter les parades filmees (male en roue = site de parade confirme)", "Regularite quotidienne des visites = fidelite du groupe au site", "Heures de parade documentees: generalement 6h-9h au printemps", "Comparer les annees: population stable, croissante ou decroissante"],
  },
  strategies_optimisation: { orignal: ["100+ detections/saison = site productif", "Photo-ID des males par panache", "5+ males distincts = premium", "Ratio males >30%"], chevreuil: ["200+ detections/saison", "Suivi annuel croissance ramure", "Ratio matures >20%", "Fidelite 3+ saisons"], ours: ["50+ detections/saison", "ID individuelle par marques", "Male dominant = qualite", "Femelles+oursons documentees"], wapiti: ["30+ detections/saison", "Taille groupes photographies", "Males 6x6 = premium", "Corridors compares"], dindon: ["100+ detections/saison", "Males adultes comptes", "Parades filmees", "Regularite quotidienne"] },
  techniques_chasse: { orignal: ["Les cameras revelent les heures exactes de visite — planifier la session a ce moment precis", "Un male photographie regulierement sur 3+ saisons connait le site — il reviendra meme sous pression moderee"], chevreuil: ["Un male mature photographie exclusivement de nuit doit etre intercepte en deplacement (corridor), pas a la saline", "La croissance annuelle de la ramure permet de predire le potentiel trophee a 3.5-4.5 ans"], ours: ["Le male dominant qui visite entre 19h et 21h est le meilleur candidat pour la session du soir", "Un ours photographie 10+ fois sur le site est un ours de pattern — hautement predictible"], wapiti: ["La taille du groupe photographie predit la fenetre de tir: 15 individus = 5-10 min de passage", "Le male mature qui passe seul 30-60 min apres le groupe est le trophee potentiel"], dindon: ["Le male qui parade au meme endroit chaque matin est le candidat ideal — blind positionne a 20 m", "Les cameras revelent si le dindon descend du perchoir vers le site OU vers un autre corridor"] },
  erreurs_a_eviter: { orignal: ["Ignorer un site avec <50 detections pendant 2 saisons (site improductif)", "Ne pas cataloguer les males (opportunite de suivi perdue)"], chevreuil: ["Tirer un male jeune identifie sur camera (perte de potentiel trophee a long terme)", "Ne pas documenter le ratio males/femelles (indicateur de gestion manque)"], ours: ["Ne pas identifier les femelles avec oursons (risque d'infraction reglementaire)", "Ignorer les patterns horaires de l'ours (information strategique perdue)"], wapiti: ["Ne pas comparer les corridors (investir sur le mauvais corridor)", "Ignorer les comptages de groupes (indicateur de sante de la population)"], dindon: ["Ne pas documenter les heures de parade (timing de chasse non optimise)", "Ne pas distinguer les males adultes des jakes sur les photos (strategie de recolte inadaptee)"] },
  optimisations_saisonnieres: { printemps: "Debut de la saison d'observation. Les animaux sortent d'hiver en carence minerale — frequentation elevee.", ete: "Collecte de donnees continue. Frequentation estivale documentee (sodium, calcium).", automne: "Saison critique. Pic de frequentation en pre-rut. Donnees pour la decision de chasse.", hiver: "Analyse des donnees annuelles. Bilan du retour sur observation. Planification." },
  optimisations_support: ["Logiciel de gestion photos trail (BuckView, DeerLab)", "Tableau de suivi: detections/semaine par espece", "Base de donnees photo-ID des males (nom, age, ramure, historique)"],
  optimisations_meteo: ["Front froid = pic d'activite — les cameras capturent 3-5x plus de detections", "Pleine lune = activite nocturne accrue — les cameras IR documentent les visites invisibles"],
  optimisations_pression: ["En zone haute pression: le retour sur observation est le meilleur indicateur pour decider si le site vaut encore l'investissement"],
  thresholds: { green: "80-100: 100+ detections/saison (cervides), males matures identifies, observations directes regulieres, tendance stable ou croissante", yellow: "50-79: 50-100 detections, qualite moderee, observations directes occasionnelles", red: "0-49: <50 detections, aucun male mature, aucune observation directe, tendance decroissante" },
  sources: ["NDA — Measuring Mineral Site Productivity (2024)", "Mississippi State University Deer Lab — Trail Camera Data Analysis for Herd Management (2022)", "MFFP Quebec — Protocoles d'inventaire des populations de cerfs et orignal (2023)", "University of Georgia Deer Lab — Photo-ID Methods for Whitetail Bucks (2021)", "RMEF — Monitoring Elk Herds with Trail Cameras (2023)"],
};

// =====================================================================
// 14. RETOUR SUR RECOLTE — P1
// =====================================================================
export const retour_recolte = {
  title: "Retour sur recolte — Potentiel de recolte par rapport a l'investissement",
  definition: "Evaluation du potentiel de recolte (harvest) d'un animal par rapport a l'investissement total (temps, argent, effort) sur le site. Le retour sur recolte est le ratio ultime: combien de saisons et combien de dollars faut-il investir pour recolter un animal de qualite a ce site. Un site avec un retour sur recolte eleve justifie les investissements continus, tandis qu'un site avec un faible retour doit etre optimise ou abandonne.",
  methodology: "Score sur 100: historique de recolte (35 pts — recoltes passees sur ce site ou proximite), potentiel de recolte estime (30 pts — basé sur observations et cameras), rapport investissement/recolte (20 pts — $/recolte), qualite de la recolte (15 pts — age, taille, condition de l'animal). Sources: registres de recolte MFFP, carnet de terrain, analyse du site.",
  justification: {
    orignal: "Le taux de recolte a la saline au Quebec varie de 10 a 30% par saison selon la qualite du site. L'investissement moyen avant une premiere recolte est de 2-3 saisons de developpement du site. Cout moyen par recolte d'orignal a la saline: 500-2000$ (mineraux + transport + temps). Un orignal male adulte represente 200-300 kg de viande de valeur ~2000-3000$.",
    chevreuil: "Le taux de recolte a la saline pour le chevreuil est de 15-40% par saison. En gestion restrictive (males >3.5 ans seulement), le taux est plus faible (10-15%) mais la qualite est superieure. Cout moyen par recolte: 200-800$. Un buck mature (140+ pouces Boone & Crockett) est le resultat de 3-5 ans de gestion et d'observation.",
    ours: "Le taux de recolte a la saline/bait pour l'ours noir est de 30-50% par saison (le plus eleve de toutes les especes avec attractifs). Cout par recolte: 300-1000$. L'ours est l'espece avec le meilleur ratio cout/reussite quand le site est bien gere. Un male mature de 200+ kg est un trophee significatif.",
    wapiti: "Le taux de recolte pour le wapiti est variable: 5-20% en chasse libre, 50-80% avec guide. L'investissement est le plus eleve de toutes les especes (expedition 2000-10000$). Un male mature (6x6, panache 300+ pouces B&C) est un trophee exceptionnel qui justifie l'investissement.",
    dindon: "Le taux de recolte pour le dindon est de 20-40% par saison. Cout par recolte: 50-200$ (le plus faible). Le dindon est l'espece avec le meilleur ratio plaisir/investissement. Un male adulte (barbe 20+ cm, ergots 2+ cm) est un trophee satisfaisant et une viande de qualite.",
  },
  recommendations_terrain: {
    orignal: ["Taux de recolte cible: 15-25% par saison sur un site bien developpe", "Investir 2-3 saisons de developpement avant d'esperer une recolte", "Documenter chaque recolte: date, heure, conditions, poids, ramure", "Calculer le cout par recolte incluant TOUTES les depenses (mineraux, transport, temps)", "Un site qui ne produit aucune recolte apres 4 saisons doit etre reevalue", "La viande d'orignal (200-300 kg) a une valeur de 2000-3000$ — le ROI est souvent positif"],
    chevreuil: ["En gestion restrictive: patienter 3-5 ans pour recolter des males de qualite", "Documenter la croissance des males identifies par cameras (suivi annuel de la ramure)", "Cout par recolte cible: <500$ pour un site optimise", "Ne tirer que les males qui ont atteint leur potentiel genetique (>3.5 ans)", "Un buck de 140+ pouces B&C justifie 3-5 ans d'investissement sur le site"],
    ours: ["Taux de recolte cible avec attractifs: 30-50% par saison", "L'ours offre le meilleur ratio cout/reussite de toutes les especes", "Documenter le poids estime et les dimensions du crane (trophee P&Y/B&C)", "Cout par recolte optimal: <500$ (attractifs + transport + temps)"],
    wapiti: ["Investissement eleve mais recolte de haute valeur (viande + trophee)", "Guide local: taux de reussite 50-80% vs 5-20% en autonomie", "Documenter l'expedition: photos, mesures, coordonnees du site de recolte", "Un wapiti 6x6 de 300+ pouces B&C est un trophee rare — valeur emotionnelle et physique"],
    dindon: ["Meilleur ratio cout/plaisir de toutes les especes", "Taux de recolte: 20-40% par saison avec un bon site et des appels maitrise", "Documenter: barbe, ergots, poids, conditions de la chasse", "Cout par recolte optimal: <100$ (le plus faible de toutes les especes)"],
  },
  strategies_optimisation: { orignal: ["2-3 saisons de dev avant recolte", "Cible 15-25%/saison", "Viande = 2000-3000$ de valeur", "ROI souvent positif"], chevreuil: ["Gestion restrictive 3-5 ans", "Males >3.5 ans seulement", "140+ pouces B&C = objectif", "Cout <500$/recolte"], ours: ["Meilleur ratio cout/reussite", "30-50%/saison avec attractifs", "Cout <500$/recolte", "Trophee P&Y/B&C possible"], wapiti: ["Guide = 50-80% reussite", "Investissement eleve mais valeur haute", "6x6 300+ pouces = exceptionnel"], dindon: ["Meilleur ratio plaisir/investissement", "20-40%/saison", "Cout <100$/recolte", "Barbe 20+ cm = trophee"] },
  techniques_chasse: { orignal: ["Un orignal recolte a la saline en octobre est typiquement en meilleure condition (gras pre-hiver) qu'un orignal chasse en battue", "La saline concentre les animaux — le tir ethique est plus facile (distance courte, animal stationnaire)"], chevreuil: ["Un buck mature recolte apres 3-5 ans de gestion restrictive a une valeur emotionnelle superieure (vous connaissez cet animal)", "La photo-identification des males sur 3+ saisons permet de choisir LE male a recolter — chasse selective"], ours: ["La saline/bait concentre l'ours — le tir broadside ethique est plus facile qu'en chasse d'approche", "Attendre le male dominant (le dernier a se presenter) pour une recolte de qualite maximale"], wapiti: ["Le tir ethique a la saline est plus facile: animal stationnaire, distance courte, angle broadside", "Le wapiti recolte en pre-rut est en condition physique maximale (panache dur, muscles rut)"], dindon: ["Le tir a la tete/cou a 20-30 m depuis le blind est le tir le plus ethique et efficace", "Le male dominant qui parade devant les decoys est le candidat ideal (attention, confiance, proximite)"] },
  erreurs_a_eviter: { orignal: ["Recolter un orignal juvenile (18 mois) quand des males matures frequentent le site", "Ne pas calculer le cout reel par recolte (risque de site non-rentable)"], chevreuil: ["Recolter un male de 2.5 ans identifie sur camera (perte de potentiel genetique a 4.5 ans)", "Se contenter d'un site a faible taux de recolte sans analyser les causes"], ours: ["Recolter le premier ours vu sans attendre le male dominant (opportunite perdue)", "Ne pas verifier le sexe: les femelles avec oursons sont PROTEGEES"], wapiti: ["Expedition sans guide dans un territoire inconnu (taux de reussite tres faible)", "Recolter un satellite (jeune male) quand le herd bull est a proximite"], dindon: ["Tirer un jake (jeune male) quand des males adultes sont presents (sous-exploitation du potentiel)", "Tirer a >40 m (densité de plombs insuffisante pour un kill propre)"] },
  optimisations_saisonnieres: { printemps: "Saison dindon. Preparation des sites pour l'automne.", ete: "Pas de recolte. Observation et preparation.", automne: "Saison majeure: orignal, chevreuil, ours. Maximiser les opportunites de recolte.", hiver: "Bilan des recoltes. Analyse du ROI annuel. Planification." },
  optimisations_support: ["Registre de recolte MFFP (obligatoire — enregistrement de l'animal recolte)", "Balance de terrain pour le poids de l'animal (verification)", "Ruban de mesure pour ramure/crane (scoring Boone & Crockett)"],
  optimisations_meteo: ["Front froid en octobre = pic d'activite — meilleure chance de recolte", "Pleine lune = activite nocturne — les matins de pleine lune sont souvent decevants"],
  optimisations_pression: ["En zone haute pression: la recolte selective est d'autant plus importante (population sous pression)", "Coordonner la recolte avec les voisins pour une gestion collective (quotas voluntaires)"],
  thresholds: { green: "80-100: Taux de recolte 20%+, males matures recoltes, cout/recolte optimal, historique de recolte documente", yellow: "50-79: Taux de recolte 10-20%, qualite moderee, cout/recolte acceptable", red: "0-49: Taux <10%, aucune recolte sur 3+ saisons, cout/recolte excessif, site improductif" },
  sources: ["MFFP Quebec — Statistiques annuelles de recolte par zone de chasse (2024)", "NDA — Harvest Data Analysis and Site Productivity (2024)", "Boone & Crockett Club — Official Scoring System for North American Big Game (2024)", "Pope & Young Club — Archery Trophy Scoring Standards (2024)", "RMEF — Elk Harvest Success Rates by Method (2023)"],
};

// =====================================================================
// 15. DURABILITE DU SITE — P1
// =====================================================================
export const durabilite = {
  title: "Durabilite du site — Capacite du site a performer sur 5-10 ans",
  definition: "Evaluation de la capacite du site de saline a maintenir sa productivite faunique sur le long terme (5-10 ans): stabilite de l'habitat environnant (coupes forestieres, urbanisation), perennite des corridors de deplacement, resilience aux changements climatiques, et durabilite des structures et amenagements. Un site durable est un investissement a long terme qui s'ameliore avec les annees, tandis qu'un site non-durable perd sa valeur en 2-3 ans.",
  methodology: "Score sur 100: stabilite habitat (30 pts — PAIF, coupes prevues, urbanisation), perennite corridors (25 pts — protection legale, stabilite), resilience climatique (20 pts — drainage, exposition), durabilite structures (25 pts — qualite materiaux, entretien). Sources: PAIF MRNF, plans d'urbanisme, donnees climatiques, inspection terrain.",
  justification: {
    orignal: "Un site d'orignal bien positionne peut etre productif pendant 10-20 ans si l'habitat environnant reste stable. Les coupes forestieres dans un rayon de 2 km modifient les corridors de deplacement en 2-5 ans. Les ravages hivernaux sont stables sur des decennies (meme si l'orignal change de corridors d'ete). Le changement climatique (rechauffement) repousse l'orignal vers le nord de 10-20 km par decennie.",
    chevreuil: "Le chevreuil est plus adaptable que l'orignal: il tolere mieux l'urbanisation moderee et les changements d'habitat. Un site de chevreuil peut etre productif pendant 5-15 ans meme avec des modifications paysageres moderees. La gestion restrictive (ne pas recolter les jeunes males) ameliore la qualite du site au fil des annees — le potentiel trophee augmente avec le temps.",
    ours: "L'ours noir est tres adaptable: un site d'ours peut etre productif pendant 10+ ans si la densite de population reste stable. Le facteur de risque principal est le developpement humain (chalets, routes) qui cree des conflits humain-ours et conduit a la relocalisation des ours problematiques. Les bleuetières et ruisseaux a truites sont des habitats stables.",
    wapiti: "Les corridors de migration du wapiti sont stables sur des generations (decennies). Un site de saline positionne sur un corridor generationnel peut etre productif pendant 20+ ans. Le risque principal est le developpement routier ou industriel qui coupe un corridor de migration. La protection legale des corridors de migration est le facteur de durabilite #1.",
    dindon: "Le dindon en zone agricole est stable tant que la structure du paysage (champs + haies + boisés) est maintenue. Un site peut etre productif pendant 10+ ans si le proprietaire agricole maintient les pratiques compatibles. La perte de perchoirs (abattage de grands arbres) est le risque principal. Le rechauffement climatique favorise l'expansion du dindon vers le nord.",
  },
  recommendations_terrain: {
    orignal: ["Verifier le PAIF (Plan d'amenagement integre de la foret) pour les coupes prevues dans un rayon de 5 km", "Evaluer la stabilite des corridors: les corridors le long de cours d'eau sont les plus stables", "Identifier les ravages hivernaux les plus proches — ils sont stables sur des decennies", "Installer des structures durables: bois traite, acier galvanise, sangles UV-resistant", "Planifier sur 10 ans: le site doit etre viable malgre les changements d'habitat previsibles", "Les coupes forestieres creent temporairement (5-10 ans) du brout favorable — opportunite"],
    chevreuil: ["Le chevreuil s'adapte aux changements — la durabilite est plus elevee qu'on ne le pense", "En zone periurbaine: verifier les plans d'urbanisme pour les developpements prevus", "La gestion restrictive ameliore la qualite du site au fil des annees", "Les food plots vivaces (trefle blanc) durent 3-5 ans sans replantation", "Les hinge cuts creent du couvert lateral instantane mais doivent etre renouveles tous les 5-7 ans"],
    ours: ["Evaluer le risque de developpement humain dans un rayon de 5 km", "Les habitats naturels stables (bleuetières, ruisseaux, forets) sont les meilleurs pour la durabilite", "Eviter les sites proches des zones de villegiature (conflits humain-ours)", "Les contenants anti-ours en acier durent 10+ ans avec entretien minimal"],
    wapiti: ["Les corridors de migration generationnels sont les sites les plus durables (20+ ans)", "Verifier s'il existe des protections legales sur le corridor (aire protegee, reserve)", "Les sites en montagne sont peu menaces par le developpement — durabilite elevee", "Les structures en altitude doivent resister aux conditions extremes (vent, gel, neige)"],
    dindon: ["Maintenir la relation avec le proprietaire agricole est le facteur de durabilite #1", "Les perchoirs de grands arbres (pins, chenes) doivent etre preserves — signaler leur importance au proprietaire", "Le rechauffement climatique favorise l'expansion du dindon vers le nord — opportunite a long terme", "Les food plots pour le dindon (avoine, trefle) durent 2-3 ans avec entretien minimal"],
  },
  strategies_optimisation: { orignal: ["PAIF consulte pour coupes prevues", "Corridors le long de cours d'eau = stables", "Structures durables (bois traite, galvanise)", "Planification 10 ans"], chevreuil: ["Chevreuil adaptable = durabilite elevee", "Gestion restrictive = amelioration continue", "Food plots vivaces 3-5 ans", "Plans urbanisme verifies"], ours: ["Habitats naturels stables", "Eviter zones villegiature", "Contenants acier 10+ ans"], wapiti: ["Corridors generationnels = 20+ ans", "Protections legales verifiees", "Sites montagne = peu menaces"], dindon: ["Relation proprietaire = #1", "Perchoirs preserves", "Expansion nordique = opportunite"] },
  techniques_chasse: { orignal: ["Un site de 10+ ans a une histoire faunique riche — les orignaux le connaissent et y reviennent generationnellement", "Les coupes forestieres recentes (0-5 ans) creent temporairement du brout excellent — saisir l'opportunite"], chevreuil: ["Un site en gestion restrictive depuis 5+ ans produit des males de qualite exceptionnelle (160+ pouces B&C)", "La fidelite des males au site augmente avec les annees — les males connaissent le site et y sont confortables"], ours: ["Un site d'ours stable depuis 5+ ans a conditionne les ours locaux a le visiter regulierement — haute predictibilite", "L'ours transmet la connaissance des sites de nourriture a ses petits — effet generationnel"], wapiti: ["Un corridor de migration generationnel est le site de chasse le plus fiable qui existe — la harde DOIT y passer", "Les sites de saline sur ces corridors sont visites par la meme harde annee apres annee"], dindon: ["Un site de dindon stable avec perchoirs preserves est visite par les memes groupes pendant 10+ ans", "La stabilite du site permet d'affiner la strategie de chasse annee apres annee (courbe d'apprentissage)"] },
  erreurs_a_eviter: { orignal: ["Investir massivement sur un site voue a etre coupe dans 2-3 ans (PAIF non-consulte)", "Negliger l'entretien des structures (tree stand instable apres 3-5 ans sans entretien)"], chevreuil: ["Abandonner un site qui sous-performe la premiere saison (la 2e et 3e saison sont souvent meilleures)", "Ne pas renouveler les food plots et hinge cuts (duree de vie limitee)"], ours: ["Installer un site pres d'une zone de villegiature en expansion (conflit inevitable)", "Negliger l'entretien des contenants anti-ours (corrosion = echec)"], wapiti: ["Investir sur un corridor menace par un projet routier ou industriel", "Structures inadaptees aux conditions de montagne (destruction par le vent/neige)"], dindon: ["Perdre la relation avec le proprietaire agricole (perte d'acces = perte du site)", "Laisser abattre les arbres de perchoir (le dindon quitte le secteur)"] },
  optimisations_saisonnieres: { printemps: "Inspection annuelle: etat des structures, corridors, drainage. Planifier les reparations.", ete: "Travaux d'amenagement durable: food plots vivaces, structures permanentes, hinge cuts.", automne: "Pas de modification. Exploitation du site. Documentation de la performance.", hiver: "Bilan annuel. Analyse de la tendance sur 3-5 ans. Planification a long terme." },
  optimisations_support: ["Bois traite (CCA ou equivalent) pour les structures permanentes: 15-20 ans de duree de vie", "Acier galvanise pour les supports et cables: 20+ ans", "Sangles UV-resistant (HSS, Muddy) pour les tree stands: remplacement tous les 3-5 ans"],
  optimisations_meteo: ["Les sites bien draines sont plus durables (moins de degradation par gel-degel)", "Les sites exposes au vent fort necessitent des structures renforcees (ancrage double)"],
  optimisations_pression: ["En zone haute pression: un site durable et bien gere se demarque — les animaux y trouvent refuge", "La durabilite du site attire les males matures qui cherchent la stabilite et la securite"],
  thresholds: { green: "80-100: Habitat stable 10+ ans, corridors proteges, structures durables, gestion a long terme planifiee", yellow: "50-79: Habitat moderement stable 5-10 ans, corridors partiellement menaces, structures vieillissantes", red: "0-49: Habitat menace <5 ans, corridors coupes ou menaces, structures degradees, aucune planification" },
  sources: ["MRNF — Plans d'amenagement integre de la foret (PAIF) par region (2024)", "MFFP — Stabilite des ravages d'orignal au Quebec: etude longitudinale (2022)", "NDA — Long-Term Mineral Site Management and Productivity (2024)", "Environnement Canada — Projections climatiques regionales Quebec 2030-2050", "RMEF — Protecting Elk Migration Corridors: Conservation Strategies (2023)"],
};

// =====================================================================
// 16. ALIGNEMENT DES SENTIERS — P1
// =====================================================================
export const alignement_sentiers = {
  title: "Alignement des sentiers — Qualite et orientation des sentiers d'acces et corridors fauniques",
  definition: "Evaluation de la qualite de l'alignement entre les sentiers d'acces du chasseur, les corridors de deplacement fauniques, et les corridors de tir depuis l'affut. Un alignement optimal positionne le sentier d'acces de maniere a ne JAMAIS croiser un corridor faunique, tout en offrant des angles de tir perpendiculaires aux axes de deplacement des animaux. Un mauvais alignement contamine olfactivement les corridors et reduit le taux de reussite de 50-70%.",
  methodology: "Score sur 100: separation sentier acces/corridor faunique (35 pts — distance minimale, absence de croisement), angle de tir vs corridor (30 pts — perpendiculaire ideal 60-120 degres), orientation sentier vs vent dominant (20 pts — sous le vent), qualite du sentier (15 pts — largeur, surface, bruit). Sources: GPS terrain, LiDAR MRNF, rose des vents.",
  justification: {
    orignal: "L'orignal emprunte des corridors larges (2-4 m) et stables. Le sentier d'acces du chasseur doit etre a >100 m de tout corridor d'orignal identifie. L'angle de tir ideal est perpendiculaire (90 degres) au corridor — le tir broadside sur un orignal en mouvement est le plus ethique et efficace. L'orignal qui detecte une odeur humaine sur SON corridor deserte la zone pour 72+ h.",
    chevreuil: "Le chevreuil est ULTRA-sensible a la contamination olfactive de ses corridors. Le sentier d'acces ne doit JAMAIS croiser un sentier de chevreuil, une zone de grattage (scrape), ou un frottoir (rub). L'angle de tir ideal est de 60-90 degres par rapport au corridor. Le chevreuil qui detecte une odeur humaine sur son corridor modifie son pattern pendant 48-72 h.",
    ours: "L'ours utilise des corridors larges et opportunistes. Le sentier d'acces peut etre plus proche du corridor de l'ours (50-100 m) car l'ours tolere mieux les odeurs humaines regulieres. L'angle de tir est moins critique car l'ours s'arrete souvent a la saline pendant 10-30 min (tir stationnaire). La separation sentier/corridor est surtout une question de SECURITE (eviter les rencontres).",
    wapiti: "Le wapiti emprunte des corridors larges (3-5 m) en file indienne. Le sentier d'acces doit etre perpendiculaire au corridor pour minimiser la detection. L'angle de tir ideal est perpendiculaire au corridor car le wapiti passe en file — le tir broadside est la seule option ethique. Le wapiti en groupe detecte les anomalies rapidement — un sentier mal aligne est repere.",
    dindon: "Le dindon suit des corridors lineaires previsibles (perchoir-alimentation). Le sentier d'acces doit etre perpendiculaire au corridor du dindon et en contrebas (le dindon surveille depuis les points hauts). L'angle de tir depuis le ground blind doit etre aligne avec le corridor d'approche du dindon (60-90 degres).",
  },
  recommendations_terrain: {
    orignal: ["Sentier d'acces a >100 m de tout corridor d'orignal identifie", "Le sentier ne doit JAMAIS croiser un corridor d'orignal (contamination olfactive)", "Angle de tir perpendiculaire (90 degres) au corridor — tir broadside optimal", "Sentier d'acces oriente SOUS LE VENT dominant par rapport au corridor", "Cartographier tous les corridors dans un rayon de 300 m avant de tracer le sentier", "Utiliser les donnees LiDAR pour identifier les passages topographiques naturels", "Si le sentier doit traverser un corridor: passer PAR-DESSUS (pont de rondins) ou PAR-DESSOUS (depression)", "Marquer le sentier avec des reflecteurs IR pour eviter de devier dans un corridor predawn"],
    chevreuil: ["Sentier d'acces qui ne croise AUCUN sentier de chevreuil, scrape, ou rub", "Distance minimale sentier-corridor: 50-100 m (le chevreuil detecte l'odeur a 50 m)", "Approche par le cote OPPOSE au corridor principal d'approche du chevreuil", "Angle de tir de 60-90 degres par rapport au corridor — jamais frontal", "Tracer le sentier en S (sinueux) plutot qu'en ligne droite (le chevreuil surveille les lignes)", "Le sentier doit aboutir a l'affut par l'ARRIERE (le chevreuil regarde vers le corridor)", "Porter des bottes en caoutchouc sur le sentier pour minimiser le depot d'odeur"],
    ours: ["Sentier d'acces a 50-100 m du corridor de l'ours (securite contre les rencontres)", "Le sentier doit offrir une visibilite a >30 m devant soi (eviter les surprises)", "L'angle de tir est moins critique (l'ours s'arrete a la saline) mais le broadside reste ideal", "Sentier large (2 m) et degage pour la securite de deplacement", "Faire du bruit sur le sentier pour signaler sa presence (sauf les derniers 50 m)", "Eviter les zones de vegetation dense ou un ours pourrait etre cache"],
    wapiti: ["Sentier perpendiculaire au corridor de migration pour minimiser le temps d'exposition", "Le wapiti passe en file indienne — le tir broadside est la seule option ethique", "Sentier par le fond de vallee le matin (thermiques montants dispersent l'odeur)", "Eviter les cretes (silhouette visible pour le wapiti)", "Angle de tir de 60-120 degres par rapport au corridor de passage"],
    dindon: ["Sentier perpendiculaire au corridor perchoir-alimentation", "Approche en contrebas (le dindon surveille depuis les hauteurs)", "Le sentier aboutit a l'ARRIERE du ground blind (le dindon regarde vers le corridor)", "Angle de tir depuis le blind aligne avec le corridor d'approche du dindon", "Sentier silencieux: mousse, herbe, copeaux de bois sur les 100 derniers metres"],
  },
  strategies_optimisation: { orignal: [">100 m du corridor", "Perpendiculaire pour broadside", "Sous le vent dominant", "Reflecteurs IR pour predawn"], chevreuil: ["ZERO croisement avec corridors", "50-100 m minimum", "Sentier sinueux", "Bottes caoutchouc"], ours: ["50-100 m pour securite", "Sentier large et degage", "Broadside a la saline", "Bruit sauf 50 derniers m"], wapiti: ["Perpendiculaire au corridor", "Fond de vallee le matin", "Eviter les cretes", "File indienne = broadside"], dindon: ["Perpendiculaire + contrebas", "Arriere du blind", "Silencieux 100 derniers m"] },
  techniques_chasse: { orignal: ["Un sentier parfaitement aligne permet une approche invisible et inodore — le taux de reussite double", "L'orignal qui arrive par le corridor sans detection = tir broadside a 30-40 m depuis le tree stand"], chevreuil: ["Le chevreuil qui arrive a la saline sans avoir detecte d'odeur sur le corridor est detendu et stationnaire — tir facile", "Un sentier mal aligne (croisement de corridor) = chevreuil nerveux qui fait demi-tour a 50 m"], ours: ["L'ours qui arrive a la saline sans rencontre sur le sentier est confiant — il reste 10-30 min (fenetre de tir large)", "Un sentier bien aligne minimise les rencontres surprises ours-chasseur sur le chemin"], wapiti: ["Le wapiti en file indienne offre une fenetre de tir de 5-10 s par individu — l'alignement perpendiculaire est critique", "Un sentier mal aligne qui coupe un corridor alerte la sentinelle du groupe — tout le groupe fuit"], dindon: ["Le dindon qui marche dans le corridor vers le blind est dans la zone de tir ideale (15-30 m)", "Un sentier d'acces visible depuis le corridor alerte le dindon — il change de route"] },
  erreurs_a_eviter: { orignal: ["Sentier qui croise un corridor d'orignal (contamination garantie)", "Angle de tir frontal (zone vitale reduite, tir non-ethique)"], chevreuil: ["Sentier qui passe par une zone de scrapes ou de rubs (derangement des marqueurs territoriaux)", "Sentier en ligne droite vers l'affut (le chevreuil detecte les lignes)"], ours: ["Sentier en sous-bois dense sans visibilite (risque de rencontre surprise)", "Approche silencieuse jusqu'a la saline (l'ours surpris peut charger)"], wapiti: ["Sentier sur une crete (silhouette humaine visible a 500+ m)", "Sentier parallele au corridor (exposition prolongee a la detection)"], dindon: ["Sentier visible depuis le corridor du dindon (detection visuelle immediate)", "Approche par le haut (le dindon surveille les points hauts)"] },
  optimisations_saisonnieres: { printemps: "Tracer ou verifier les sentiers. Les corridors fauniques sont visibles (neige fondante, traces fraiches).", ete: "Debroussailler les sentiers. Verifier les angles de tir (vegetation estivale obstrue les corridors).", automne: "Pas de modification. Utiliser les sentiers tels quels. Feuilles mortes = bruit accru — prevoir.", hiver: "Evaluation des corridors sans vegetation. Ideal pour retracer les sentiers si necessaire." },
  optimisations_support: ["GPS de terrain (Garmin GPSMAP 67) pour cartographier sentiers et corridors", "LiDAR MRNF (resolution 1 m) pour identifier les passages topographiques", "Boussole pour verifier les angles sentier/corridor/vent"],
  optimisations_meteo: ["Vent fort: l'alignement sous le vent est encore plus critique (odeur transportee plus loin)", "Pluie: le sol mou absorbe les odeurs — meilleur moment pour emprunter le sentier"],
  optimisations_pression: ["En zone haute pression: un sentier parfaitement aligne est le seul moyen de maintenir la frequentation sur un site sollicite"],
  thresholds: { green: "80-100: Sentier separe des corridors (>100 m), angle perpendiculaire, sous le vent, aucun croisement", yellow: "50-79: Sentier partiellement separe (50-100 m), angle acceptable, croisement mineur", red: "0-49: Sentier croisant des corridors, angle frontal/parallele, face au vent, contamination olfactive" },
  sources: ["NDA — Trail Layout and Deer Corridor Management (2024)", "Mississippi State University Deer Lab — Access Trail Impact on Mature Buck Movement (2022)", "MRNF — LiDAR Canopy and Terrain Models for Wildlife Corridor Identification (2023)", "MFFP — Protocoles d'amenagement des sentiers en reserve faunique (2022)", "University of Georgia Deer Lab — Scent Contamination of Deer Trails: Impact Study (2021)"],
};

// =====================================================================
// 17. LISSAGE DU TERRAIN — P2
// =====================================================================
export const lissage = {
  title: "Lissage du terrain — Uniformite et praticabilite du sol autour du site de saline",
  definition: "Evaluation de l'uniformite et de la praticabilite de la surface du sol dans un rayon de 50 m autour de la saline: absence d'obstacles (souches, rochers, trous), regularite de la surface pour le deplacement silencieux, et capacite du terrain a supporter les structures (tree stand, ground blind). Un terrain lisse et uniforme permet une approche silencieuse, un deplacement securitaire, et une installation stable des equipements.",
  methodology: "Score sur 100: uniformite du sol (30 pts — densite d'obstacles/50 m2), praticabilite (25 pts — capacite de deplacement silencieux), stabilite structurelle (25 pts — portance pour tree stand/blind), securite (20 pts — risque de chute/blessure). Sources: inspection terrain, GPS, denivele micro-topographique.",
  justification: {
    orignal: "La zone autour de la saline d'orignal doit etre praticable pour l'installation du tree stand (arbre porteur de 30+ cm de diametre) et le deplacement silencieux du chasseur. Les souches, les rochers affleurants, et les trous de racines sont des sources de bruit (trebuchement) et de danger (chute). Un rayon de 20 m autour de l'affut doit etre degage de tout obstacle.",
    chevreuil: "Le chevreuil detecte le moindre bruit de trebuchement a 80+ m. La zone autour de la saline doit etre parfaitement lisse: pas de branches mortes au sol, pas de souches cachees sous les feuilles, pas de rochers instables. Le sol ideal est un tapis de mousse ou d'humus forestier compacte. Les zones de gravier ou de feuilles seches sont a eviter.",
    ours: "En zone ours, le terrain lisse autour de la saline est important pour la SECURITE: le chasseur doit pouvoir se deplacer rapidement sans trebucher en cas d'urgence. Le tree stand doit etre installe sur un arbre robuste (40+ cm diametre) dans un sol stable (pas de racines superficielles qui fragilisent l'ancrage).",
    wapiti: "En terrain montagneux, le lissage est rarement naturel. Le chasseur doit amenager une zone plate (3x3 m minimum) autour de l'affut pour le deplacement silencieux. Les pierres instables et les racines exposees sont des sources de bruit en montagne. Le terrain en pente autour de la saline doit etre stabilise.",
    dindon: "Le ground blind pour le dindon doit etre installe sur un terrain plat et stable. Le chasseur a l'interieur du blind doit pouvoir pivoter silencieusement (sol plat sans debris). Le terrain autour du blind doit permettre aux dindons de marcher confortablement (pas de broussailles denses qui bloquent le passage).",
  },
  recommendations_terrain: {
    orignal: ["Degager les souches, branches mortes et rochers dans un rayon de 20 m autour de l'affut", "Identifier un arbre porteur de 30+ cm de diametre pour le tree stand", "Verifier la stabilite du sol: sol compacte, pas de racines superficielles instables", "Creer un chemin degage de l'affut a la zone de tir (3 m de large, sans obstacles)", "Combler les trous de racines avec de la terre compactee", "Retirer les branches basses (<2 m) dans un rayon de 10 m autour de l'affut"],
    chevreuil: ["Tapis de mousse ou humus forestier = surface ideale (silence de deplacement)", "Ratisser les feuilles mortes et les branches dans un rayon de 15 m", "Retirer les pierres instables et les racines exposees", "En zone de gravier: couvrir avec des copeaux de bois ou de la mousse", "Creer une surface plane sous et autour du tree stand", "Le ground blind doit etre sur une surface parfaitement plate (pas de pente)"],
    ours: ["Zone degagee de 20 m autour de l'affut pour la visibilite et la securite", "Arbre porteur de 40+ cm de diametre (l'ours peut secouer un arbre mince)", "Sol stable sans racines superficielles qui fragilisent l'ancrage du tree stand", "Chemin de retrait rapide degage de tout obstacle (en cas d'urgence)"],
    wapiti: ["Amenager une zone plate de 3x3 m minimum autour de l'affut en terrain montagneux", "Stabiliser les pierres instables avec du ciment naturel (terre + gravier compacte)", "Creer des marches en rondins sur les pentes >15% pres de l'affut", "Retirer les pierres et racines sur le chemin entre l'affut et la zone de tir"],
    dindon: ["Surface plate et stable pour le ground blind (pas de pente >5%)", "Degager les broussailles autour du blind pour le passage des dindons", "Sol propre a l'interieur du blind (pas de debris qui craquent au pivotement)", "Zone de parade degagee devant le blind (les dindons ont besoin d'espace pour parader)"],
  },
  strategies_optimisation: { orignal: ["Rayon 20 m degage", "Arbre 30+ cm", "Trous combles", "Branches basses retirees"], chevreuil: ["Mousse/humus ideal", "Feuilles ratissees", "Pierres retirees", "Surface plane sous blind"], ours: ["20 m degage pour securite", "Arbre 40+ cm", "Chemin de retrait degage"], wapiti: ["Zone plate 3x3 m", "Pierres stabilisees", "Marches en rondins"], dindon: ["Surface plate <5% pente", "Broussailles degagees", "Zone de parade libre"] },
  techniques_chasse: { orignal: ["Un terrain lisse autour de l'affut permet de pivoter silencieusement pour suivre l'orignal en approche", "L'absence d'obstacles au sol elimine le risque de bruit accidentel au moment critique du tir"], chevreuil: ["Sur un terrain lisse, le chasseur peut se repositionner dans l'affut sans creer de bruit — le chevreuil reste detendu", "Les feuilles mortes ratissees eliminent 80% du bruit au sol — investissement de 30 min qui sauve la session"], ours: ["Un terrain degage autour de l'affut offre une visibilite de 360 degres — aucun ours ne peut approcher sans etre vu", "En cas d'urgence, un chemin degage permet un retrait rapide sans trebuchement"], wapiti: ["Une zone plate amenagee en montagne est un luxe qui permet des sessions confortables de 4-6 h", "Les marches en rondins securisent l'acces au tree stand en terrain en pente"], dindon: ["Le dindon qui voit un terrain degage devant le blind s'installe pour parader — zone de tir ideale", "Un sol propre dans le blind permet de pivoter silencieusement pour suivre le dindon"] },
  erreurs_a_eviter: { orignal: ["Negliger le degagement autour de l'affut (bruit accidentel garanti)", "Installer le tree stand sur un arbre trop mince (<25 cm) — instabilite"], chevreuil: ["Laisser les feuilles mortes au sol (bruit a chaque mouvement)", "Terrain en pente sous le ground blind (inconfort + instabilite)"], ours: ["Vegetation dense autour de l'affut (ours invisible a <10 m)", "Sol instable sous le tree stand (risque de chute)"], wapiti: ["Terrain non-amenage en montagne (pierres instables, racines)"], dindon: ["Broussailles denses autour du blind (les dindons contournent)", "Sol encombre dans le blind (craquements au pivotement)"] },
  optimisations_saisonnieres: { printemps: "Nettoyage post-hiver: debris, branches tombees, pierres deplacees par le gel-degel.", ete: "Debroussaillage et amenagement. Meilleure saison pour les travaux lourds.", automne: "Pas de modification majeure. Ratisser les feuilles juste avant la saison.", hiver: "Le gel stabilise le sol. Evaluation sans vegetation pour planifier les travaux printaniers." },
  optimisations_support: ["Ratisseur forestier pour le nettoyage du sol", "Copeaux de bois (cedre) pour les zones bruyantes", "Niveau a bulle pour verifier la planeite du terrain sous le blind"],
  optimisations_meteo: ["Sol mou apres la pluie = deplacement plus silencieux", "Sol gele = bruit a chaque pas (prevoir mousse supplementaire)", "Neige fraiche = sol parfaitement silencieux (meilleure condition)"],
  optimisations_pression: ["Un terrain lisse autour de l'affut donne un avantage discret mais decisif en zone haute pression"],
  thresholds: { green: "80-100: Terrain degage et plat, aucun obstacle dans 20 m, surface silencieuse, structures stables", yellow: "50-79: Terrain partiellement degage, quelques obstacles, surface moderement bruyante", red: "0-49: Terrain encombre, obstacles multiples, surface tres bruyante, structures instables" },
  sources: ["NDA — Stand Site Preparation and Ground Clearing (2024)", "MFFP — Normes d'amenagement des postes d'affut en reserve (2022)", "HSS — Tree Stand Installation Safety and Terrain Requirements (2024)"],
};

// =====================================================================
// 18. PENETRABILITE DU TERRAIN — P1
// =====================================================================
export const penetrabilite = {
  title: "Penetrabilite du terrain — Facilite de deplacement en foret autour du site",
  definition: "Evaluation de la facilite de deplacement a pied dans la foret entourant le site de saline: densite du sous-bois, presence d'obstacles naturels (chablis, marecages, falaises), pente du terrain, et capacite a se deplacer silencieusement pour l'approche de chasse ou le suivi d'un animal blesse. La penetrabilite determine la capacite du chasseur a exploiter les opportunites autour du site et a recuperer un animal recolte.",
  methodology: "Score sur 100: densite du sous-bois (30 pts — tiges/ha dans les strates 0-2 m), obstacles naturels (25 pts — chablis, marecages, falaises), pente moyenne (20 pts — DEM LiDAR), capacite de deplacement silencieux (25 pts — type de sous-bois). Sources: inventaire forestier MRNF, LiDAR, observations terrain.",
  justification: {
    orignal: "Apres la recolte, l'orignal blesse peut parcourir 50-200 m avant de tomber. Le chasseur doit pouvoir suivre la piste de sang a travers la foret. Un sous-bois dense (>15000 tiges/ha) rend le suivi quasi-impossible et dangereux (mauvaise visibilite, risque de perdre l'animal). Le terrain autour de la saline doit permettre un deplacement rapide dans un rayon de 200 m minimum.",
    chevreuil: "Le chevreuil blesse court souvent 50-150 m dans le sous-bois dense. La penetrabilite est critique pour la recuperation ethique de l'animal. Le sous-bois ideal autour d'une saline de chevreuil est ouvert (foret mature avec canopee fermee qui inhibe le sous-bois) ou moderement dense (ecotone foret-clairiere avec visibilite de 20-30 m).",
    ours: "L'ours blesse est EXTREMEMENT dangereux. Le suivi d'un ours blesse dans un sous-bois dense est la situation la plus dangereuse en chasse. La penetrabilite autour du site doit etre MAXIMALE (visibilite >30 m) pour la securite du chasseur. Si le sous-bois est dense: attendre 2+ h avant de commencer le suivi.",
    wapiti: "Le wapiti blesse peut parcourir 100-500 m en terrain montagneux. La penetrabilite en montagne est souvent limitee par les pentes abruptes, les chablis, et les falaises. Le suivi d'un wapiti blesse en terrain montagneux est physiquement eprouvant et potentiellement dangereux. La zone de tir doit etre choisie pour maximiser la recuperation.",
    dindon: "Le dindon touche tombe generalement sur place ou dans un rayon de 10-20 m (tir a la tete/cou). La penetrabilite est moins critique mais le terrain doit permettre au chasseur de recuperer l'oiseau sans difficulte. Le sous-bois doit etre suffisamment ouvert pour que les dindons puissent marcher confortablement (les dindons evitent les sous-bois tres denses).",
  },
  recommendations_terrain: {
    orignal: ["Sous-bois degage dans un rayon de 200 m autour de la saline pour le suivi post-tir", "Visibilite au sol de 20-30 m minimum (foret mature preferable)", "Identifier et marquer les obstacles AVANT la saison (chablis, marecages)", "Prevoir un itineraire de suivi pour les 4 directions cardinales", "Les zones de chablis (arbres tombes) doivent etre contournees et les passages marques", "En zone dense: creer des coulees de 2 m de large pour le suivi post-recolte", "Porter un ruban fluorescent pour marquer la piste de sang lors du suivi", "GPS de terrain pour documenter le parcours de suivi (retour au point de chute)"],
    chevreuil: ["Foret mature avec canopee fermee = sous-bois ouvert ideal (ombre inhibe la croissance)", "Visibilite de 20-30 m au sol est l'ideal pour l'approche et le suivi", "Les ecotones foret-clairiere offrent un bon compromis couvert/penetrabilite", "Les hinge cuts BIEN planifies augmentent le couvert SANS bloquer la penetrabilite", "Eviter les zones de regeneration dense (10-20 ans post-coupe) — quasi-impenetrables", "Prevoir un chemin de recuperation vers un acces vehiculaire pour le transport de l'animal"],
    ours: ["Penetrabilite MAXIMALE autour du site de saline pour la securite (visibilite >30 m)", "Si le sous-bois est dense: attendre 2+ h avant de suivre un ours blesse", "Le suivi d'ours blesse = DUO obligatoire, spray anti-ours en main, arme chargee", "Eviter les sites entoures de sous-bois dense ou la visibilite est <10 m", "Degager les lignes de vue dans les 4 directions cardinales autour de l'affut", "Prevoir un itineraire de retrait rapide degage en cas d'urgence"],
    wapiti: ["En montagne: evaluer la penetrabilite des pentes environnantes avant l'installation", "Les pentes >30% sont difficiles pour le suivi d'un wapiti de 300+ kg", "Prevoir un plan de recuperation: comment sortir 300 kg de viande du terrain montagneux", "Les sentiers existants (animaux ou forestiers) sont les meilleurs axes de penetration", "Porter un couteau de depeçage pour le quartierrage sur place si le terrain ne permet pas le transport entier"],
    dindon: ["Le dindon prefere les sous-bois ouverts avec visibilite au sol de 30-50 m", "Un terrain penetrable attire les dindons (ils marchent beaucoup et evitent les obstacles)", "Le sous-bois ideal: chenes matures avec litiere de feuilles et herbes basses", "La recuperation du dindon est simple (3-5 kg) — la penetrabilite est surtout pour l'habitat"],
  },
  strategies_optimisation: { orignal: ["200 m de rayon degage", "Visibilite 20-30 m", "Coulees de suivi 2 m", "GPS + ruban fluorescent"], chevreuil: ["Foret mature = sous-bois ouvert", "Ecotones = bon compromis", "Chemin de recuperation vers vehicule"], ours: ["Visibilite >30 m obligatoire", "Duo + spray pour suivi ours blesse", "Retrait rapide degage"], wapiti: ["Pentes <30% pour suivi", "Plan de quartierrage in situ", "Sentiers existants utilises"], dindon: ["Sous-bois ouvert 30-50 m visibilite", "Chenes matures ideal", "Habitat > recuperation"] },
  techniques_chasse: { orignal: ["Un tir ethique dans un terrain penetrable = recuperation en <30 min vs 3+ h en terrain dense", "Les coulees de suivi pre-marquees economisent un temps precieux lors du suivi de sang"], chevreuil: ["Le chevreuil blesse court vers le couvert dense — anticiper la direction de fuite", "En foret mature: le suivi de sang est plus facile (sol visible, sous-bois ouvert)"], ours: ["REGLE D'OR: si l'ours tombe hors de vue dans un sous-bois dense, attendre 2 h minimum avant le suivi", "Le suivi d'un ours blesse dans un sous-bois dense est la situation la plus dangereuse en chasse nord-americaine"], wapiti: ["Le wapiti de 300+ kg ne peut pas etre transporte entier — prevoir le quartierrage sur place", "Les pentes raides forcent souvent le wapiti blesse vers le bas — anticiper la direction de chute"], dindon: ["Le dindon touche a la tete/cou tombe sur place — penetrabilite negligeable pour la recuperation", "Un sous-bois ouvert attire plus de dindons — investir dans l'habitat plutot que dans la recuperation"] },
  erreurs_a_eviter: { orignal: ["Installer la saline au milieu d'une regeneration dense (suivi impossible)", "Ne pas prevoir de coulees de suivi (temps perdu apres le tir)"], chevreuil: ["Site en zone de regeneration 10-20 ans (quasi-impenetrable pour le suivi)", "Negliger le chemin de recuperation vers le vehicule (portage de 60+ kg)"], ours: ["Suivre un ours blesse seul dans un sous-bois dense (risque mortel)", "Ne pas attendre les 2 h reglementaires avant le suivi (ours vivant = charge)"], wapiti: ["Site en haut d'une falaise (recuperation impossible)", "Ne pas prevoir le quartierrage (300 kg = intransportable en entier)"], dindon: ["Site en sous-bois tres dense (les dindons n'y marchent pas)"] },
  optimisations_saisonnieres: { printemps: "Evaluation de la penetrabilite avec la neige fondante. Le sous-bois est visible avant la feuillaison.", ete: "Le sous-bois est au maximum de densite. Debroussailler les coulees de suivi si necessaire.", automne: "Feuilles tombees = visibilite amelioree au sol. Conditions de suivi meilleures qu'en ete.", hiver: "Sans feuilles: visibilite maximale. Ideal pour evaluer et planifier les coulees de suivi." },
  optimisations_support: ["Ruban fluorescent de marquage pour le suivi de sang (orange ou rose vif)", "GPS de terrain pour documenter le parcours de suivi et le point de chute", "Lampe de type BloodTracker (LED bleue) pour le suivi de sang en conditions de faible lumiere"],
  optimisations_meteo: ["Pluie: le sang est lave rapidement — suivi IMMEDIAT obligatoire", "Neige: sang tres visible sur fond blanc — conditions ideales de suivi", "Sec et chaud: le sang seche vite — suivi dans l'heure"],
  optimisations_pression: ["En zone haute pression: un terrain penetrable accelere la recuperation — moins de temps expose = moins de conflits avec d'autres chasseurs"],
  thresholds: { green: "80-100: Sous-bois ouvert (visibilite >30 m), aucun obstacle majeur, coulees de suivi amenagees, plan de recuperation", yellow: "50-79: Sous-bois modere (visibilite 15-30 m), obstacles partiels, coulees non-amenagees", red: "0-49: Sous-bois dense (visibilite <15 m), obstacles majeurs (chablis, marecages), suivi dangereux" },
  sources: ["MRNF — Inventaire forestier du Quebec: donnees de densite de sous-bois par strate (2024)", "MFFP — Protocoles de recuperation du gibier blesse (2023)", "NDA — Shot Recovery and Tracking in Dense Cover (2024)", "Bear Trust International — Wounded Black Bear Tracking Safety (2022)", "RMEF — Elk Recovery in Mountain Terrain: Best Practices (2023)"],
};

// =====================================================================
// 19. EFFORT REEL DE DEPLACEMENT — P2
// =====================================================================
export const effort_reel = {
  title: "Effort reel de deplacement — Temps et energie necessaires pour atteindre le site",
  definition: "Evaluation de l'effort physique reel necessaire pour atteindre le site de saline depuis le point de stationnement: distance de marche effective (pas la distance a vol d'oiseau), denivele cumule positif et negatif, difficulte du terrain (pente, obstacles, type de sol), et temps reel de deplacement en conditions de charge (sac de portage, equipement de chasse). L'effort reel est souvent 2-3x superieur a ce que la distance GPS suggere.",
  methodology: "Score sur 100: temps de deplacement reel (35 pts — chronometre terrain), denivele cumule (25 pts — DEM LiDAR), difficulte du terrain (20 pts — pente, obstacles, sol), charge portee (20 pts — kg d'equipement). Sources: traces GPS terrain, MNT LiDAR, chronometre de visite.",
  justification: {
    orignal: "L'effort reel pour atteindre un site d'orignal en foret boreale est souvent sous-estime: 500 m GPS = 30-45 min de marche en terrain accidente avec 25 kg de portage. Le denivele cumule est le facteur le plus sous-estime — 100 m de denivele positif ajoute 15-20 min au temps de deplacement. L'effort reel impacte directement la frequence des visites d'entretien et la fatigue du chasseur a l'affut.",
    chevreuil: "L'effort reel pour un site de chevreuil est generalement faible (terrain plat a moderement vallonne, courtes distances). Cependant, l'effort doit etre minimal pour permettre des visites frequentes et discretes. Un effort trop important = moins de visites = site moins entretenu = frequentation en baisse.",
    ours: "L'effort reel en zone ours doit etre FAIBLE pour la securite: le chasseur doit pouvoir atteindre ET quitter le site rapidement. Un site qui necessite 45+ min d'effort physique intense est risque en zone ours (fatigue = capacite de reaction reduite en cas de rencontre). L'effort est amplifie par le portage d'attractifs lourds (40-60 kg).",
    wapiti: "L'effort reel pour un site de wapiti en montagne est souvent EXTREME: 500-1500 m de marche avec 200-500 m de denivele cumule et 20-30 kg d'equipement. Le conditionnement physique du chasseur est un facteur critique. Les expeditions de wapiti en montagne sont parmi les plus exigeantes physiquement en chasse nord-americaine.",
    dindon: "L'effort reel pour un site de dindon est le plus faible de toutes les especes: terrain plat, courte distance, equipement leger (5-10 kg). L'enjeu n'est pas l'effort physique mais la discretion de l'approche predawn.",
  },
  recommendations_terrain: {
    orignal: ["Mesurer le temps reel de deplacement avec charge (pas la distance GPS)", "Facteur de correction: temps reel = distance GPS x 1.5 a 2.5 selon le terrain", "Denivele cumule >200 m = site physiquement exigeant — conditionner avant la saison", "Prevoir des pauses regulieres (toutes les 200 m de denivele) pour maintenir le silence", "Utiliser des batons de marche pour les pentes >15% avec charge", "Chronometrer le deplacement a l'automne (conditions reelles avec equipement complet)", "L'effort reel impacte la fatigue a l'affut — un chasseur fatigue est moins vigilant et plus bruyant", "Si l'effort reel depasse 45 min: envisager un depot intermediaire ou un camp avance"],
    chevreuil: ["Effort reel cible: <20 min avec equipement complet", "Les sites de chevreuil proches et faciles d'acces permettent des sessions plus frequentes", "Un terrain plat avec sol ferme = effort minimal et deplacement silencieux", "L'effort reduit permet d'arriver a l'affut frais et alerte (vs fatigue et transpire)", "Eviter les sites qui necessitent de traverser des zones humides (effort + bruit)"],
    ours: ["Effort reel cible: <25 min pour la securite (retrait rapide possible)", "Le portage d'attractifs lourds (40-60 kg) double l'effort — planifier en consequence", "Un chasseur fatigue par l'effort est MOINS reactif en cas de rencontre avec un ours", "Prevoir de l'eau et des barres energetiques pour les portages lourds en zone ours", "Si l'effort depasse 30 min avec attractifs: utiliser un traineau ou un chariot de portage"],
    wapiti: ["L'effort reel pour le wapiti est EXTREME — conditionner 2-3 mois avant l'expedition", "Programme d'entrainement: cardio (escalier avec sac leste), squats, randonnees en denivele", "Altitude: l'effort est amplifie de 20-30% au-dessus de 2000 m (rarefaction de l'oxygene)", "Pack list optimise: chaque gramme compte en montagne — eliminer le superflu", "Prevoir le quartierrage sur place: transporter 300 kg de wapiti = 4-6 voyages de portage"],
    dindon: ["Effort reel cible: <10 min (le dindon est proche des infrastructures)", "L'effort est minimal mais l'approche doit etre SILENCIEUSE — la discretion prime sur la vitesse", "Equipement leger (5-10 kg): blind portable, appels, decoys, cartouches", "L'effort reduit permet des sessions matinales spontanees sans preparation physique"],
  },
  strategies_optimisation: { orignal: ["Temps reel mesure (pas GPS)", "Facteur correction 1.5-2.5x", "Batons de marche en pente", "Depot intermediaire si >45 min"], chevreuil: ["<20 min avec equipement", "Terrain plat = effort minimal", "Sessions frequentes possibles"], ours: ["<25 min pour securite", "Traineau pour attractifs lourds", "Chasseur frais = plus reactif"], wapiti: ["Conditionnement 2-3 mois avant", "Pack list optimise", "Quartierrage in situ prevu"], dindon: ["<10 min", "Discretion > vitesse", "Sessions spontanees possibles"] },
  techniques_chasse: { orignal: ["Un chasseur qui arrive a l'affut sans effort excessif est calme, silencieux et concentre — les conditions ideales pour un tir reussi", "L'effort reel determine directement le nombre de sessions par saison: un site facile = 2x plus de sessions qu'un site difficile"], chevreuil: ["Le chevreuil detecte la transpiration humaine — un effort modere permet d'arriver sec et inodore", "Un site a effort faible permet des sessions quotidiennes — la frequence est la cle du succes pour le chevreuil"], ours: ["Un chasseur frais et alerte reagit 2-3x plus vite qu'un chasseur fatigue en cas de rencontre ours", "L'effort reduit permet de consacrer toute son energie a l'observation et a la patience a l'affut"], wapiti: ["Le conditionnement physique est la variable #1 du succes en chasse au wapiti en montagne", "Les chasseurs bien conditionnes couvrent 2-3x plus de terrain = 2-3x plus d'opportunites"], dindon: ["L'effort minimal du dindon permet de se concentrer entierement sur la strategie d'appel et l'immobilite", "Plusieurs sessions matinales par semaine sont possibles quand l'effort est negligeable"] },
  erreurs_a_eviter: { orignal: ["Sous-estimer l'effort reel (la distance GPS ne dit pas tout)", "Negliger le conditionnement physique avant la saison (fatigue = erreurs)"], chevreuil: ["Choisir un site difficile d'acces quand un site facile et productif est disponible", "Arriver a l'affut en sueur (odeur detectable par le chevreuil a 200+ m)"], ours: ["Site trop eloigne pour un retrait rapide en cas d'urgence (>30 min)", "Portage d'attractifs lourds en solo (fatigue + risque securitaire)"], wapiti: ["Expedition sans conditionnement physique (echec garanti en montagne)", "Sous-estimer le poids du portage de retour (300 kg de viande en 4-6 voyages)"], dindon: ["Effort excessif pour une espece qui se chasse a proximite (mauvais choix de site)"] },
  optimisations_saisonnieres: { printemps: "Sol mou apres la fonte — effort accru. Bottes impermeables ajoutent du poids. Conditionner avant la saison.", ete: "Sol sec et ferme — effort minimal. Meilleure saison pour chronometrer l'effort reel.", automne: "Feuilles au sol = effort et bruit accrus. Sol variable (sec/humide selon les pluies).", hiver: "Neige et raquettes = effort 2x plus eleve. Sol gele = bruit a chaque pas." },
  optimisations_support: ["Batons de marche telescopiques (Black Diamond, Leki) pour les pentes", "Sac a cadre externe pour les portages >15 kg (repartition du poids)", "GPS avec altimetre pour mesurer le denivele reel (Garmin GPSMAP 67)"],
  optimisations_meteo: ["Chaleur: effort accru + transpiration = odeur. Arriver tot quand il fait frais.", "Froid: effort accru avec les vetements lourds. Bouger genere de la chaleur.", "Pluie: sol glissant = effort accru et risque de chute. Bottes a crampons."],
  optimisations_pression: ["Un site a effort faible permet plus de sessions et donc plus d'opportunites en zone haute pression"],
  thresholds: { green: "80-100: Effort reel <20 min, denivele <50 m, terrain facile, charge <15 kg, chasseur en condition", yellow: "50-79: Effort 20-40 min, denivele 50-200 m, terrain modere, charge 15-25 kg", red: "0-49: Effort >40 min, denivele >200 m, terrain difficile, charge >25 kg, chasseur non-conditionne" },
  sources: ["MRNF — Modele numerique de terrain LiDAR Quebec (resolution 1 m)", "CAF (Club alpin francais) — Calcul de l'effort en montagne: methode Naismith modifiee", "NDA — Physical Preparation for Hunting Season (2024)", "RMEF — Mountain Elk Hunting: Physical Fitness Guide (2023)", "MFFP — Securite en foret: prevention de la fatigue et des accidents (2022)"],
};

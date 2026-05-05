"""
mffp_phase3_specs_omega.py — ORDRE N°52-R11
═══════════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU · ANTI_GÉNÉRIQUE_STRICT

Spécifications canoniques + squelettes de fonctions pour les 8 couches
MFFP dérivées (PHASE_3 R8) qui débloqueront le recalcul R9 (corridors,
hotspots, affuts, salines, zones_*).

Doctrine :
  · Les 8 couches sont calculées à partir de `pee_maj.gpkg` (PEE = peuplement
    écoforestier) du MFFP — Direction des inventaires forestiers du Québec.
  · Projection cible : EPSG:32198 (NAD83 / Québec Lambert) — confirmé par
    Commandant lors de l'arbitrage R8 Option δ.
  · Chaque fonction skeleton lève NotImplementedError tant que les
    dictionnaires MFFP_CODES + le subset de validation 100 Mo + la
    validation algorithmique ne sont pas fournis (anti-générique strict).
  · Aucun calcul fictif, aucun mock — uniquement des contrats canoniques.
  · FUSION ADD-ONLY : ce module ne touche à aucune logique existante.

Champs canoniques attendus dans `pee_maj.gpkg` (table `peuplement_ecoforestier`)
selon la nomenclature MFFP :
  · GEOMETRY     · Polygone (Multi)Polygon, projection EPSG:32198
  · POLY_ID      · Identifiant unique du polygone
  · ESS_DOMI     · Code essence dominante (3 lettres : ERS, BOP, EPB, …)
  · ESS_CODOMI   · Code essence codominante (optionnel)
  · GR_ESS       · Groupe d'essences (R, F, M : résineux, feuillus, mixte)
  · CL_AGE       · Classe d'âge (10, 30, 50, 70, 90, 120, JIN, JIR, VIN, VIR)
  · CL_HAUT      · Classe de hauteur (1=>22m, 2=17-22m, 3=12-17m, 4=7-12m, 5=4-7m)
  · CL_DENS      · Classe de densité couvert (A=>80%, B=60-80%, C=40-60%, D=25-40%)
  · CL_PENT      · Classe de pente
  · TY_COUV      · Type de couverture (FE, FR, FM, RE, RN, ...)
  · TYPE_ECO     · Type écologique (FE32, RS28, MS22, ...)
  · ORIGINE      · Code origine du peuplement (CHT, CT, BR, FR, ...)
  · AN_ORIGINE   · Année d'origine du peuplement
  · PERTURB      · Code de perturbation (CO, EL, ...)
  · AN_PERTURB   · Année de perturbation
  · IND_QUAL     · Indice de qualité de station (optionnel)
  · SUPERFICIE   · Superficie du polygone (m² ou ha)

Notes :
  · `JIN`/`JIR` = jeune inéquienne · `VIN`/`VIR` = vieille inéquienne.
  · Les bornes de classes_age MFFP : 10 = [0,20[, 30 = [20,40[, 50 = [40,60[,
    70 = [60,80[, 90 = [80,100[, 120 = [100,inf[.
  · Le dictionnaire ESSENCES doit fournir : code → nom commun + nom latin +
    type (R/F) + tolérance ombre + valeur économique + valeur faunique.

Sortie canonique cible (par couche) :
  · Format : GeoTIFF EPSG:32198 (raster) ou GeoPackage (vecteur)
  · Résolution raster : 100 m (sauf fragmentation = 250 m, classes_age = 250 m)
  · NoData : 0 ou -9999 selon contexte
  · Persistance : `/app/backend/data/gis_archive/derivatives/`

Références scientifiques principales :
  · Fragmentation : Dickson et al. (2017) Forest Ecology & Management,
    "Forest fragmentation thresholds for boreal birds and mammals".
  · Densité canopée : Coops et al. (2007) Remote Sensing of Environment.
  · Productivité forestière : MFFP (2016) Manuel d'aménagement forestier.
  · Connectivité écologique : Saura & Pascual-Hortal (2007) Conservation Genetics.
═══════════════════════════════════════════════════════════════════════════
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

# ═════════════════════════════════════════════════════════════════════════
# Constantes et types
# ═════════════════════════════════════════════════════════════════════════
TARGET_EPSG = 32198  # NAD83 / Québec Lambert
RESOLUTION_DEFAULT_M = 100  # Résolution raster par défaut (m)
RESOLUTION_FRAGMENTATION_M = 250  # Fenêtre fragmentation
RESOLUTION_CLASSES_AGE_M = 250  # Bins classes d'âge
NODATA_VALUE = -9999
DERIVATIVES_OUTPUT_ROOT = "/app/backend/data/gis_archive/derivatives"


# ═════════════════════════════════════════════════════════════════════════
# Spécifications canoniques (gabarit Commandant)
# ═════════════════════════════════════════════════════════════════════════
MFFP_LAYERS_SPECS: Dict[str, Dict[str, Any]] = {
    # ─────────────────────────────────────────────────────────────────────
    "MFFP_STRUCTURE": {
        "label": "Structure forestière (raster catégoriel)",
        "priority": "P0_CRITICAL_FOR_R9",
        "description": (
            "Classification hiérarchique de la structure verticale et "
            "horizontale du peuplement (régulière vs irrégulière, "
            "monostrate vs multistrate, étagée vs uniforme)."),
        "inputs_required": {
            "fields_pee_maj_gpkg": [
                "CL_HAUT", "CL_DENS", "CL_AGE", "GR_ESS",
                "TY_COUV", "TYPE_ECO",
            ],
            "external_dictionaries": [
                "codes_essences.json (ESS_DOMI → tolérance ombre)",
                "structure_classification_rules.json (Commandant à fournir)",
            ],
        },
        "outputs": {
            "format": "GeoTIFF",
            "epsg": TARGET_EPSG,
            "resolution_m": RESOLUTION_DEFAULT_M,
            "dtype": "uint8",
            "nodata": 0,
            "value_domain": {
                "1": "REGULIERE_MONOSTRATE",
                "2": "REGULIERE_BISTRATE",
                "3": "IRREGULIERE_ETAGEE",
                "4": "IRREGULIERE_JARDINEE",
                "5": "INEQUIENNE_JEUNE",
                "6": "INEQUIENNE_VIEILLE",
                "7": "RECRUE_OUVERT",
            },
            "filename": "MFFP_STRUCTURE.tif",
        },
        "key_parameters": {
            "structure_rules_strategy": (
                "Application de l'arbre de décision MFFP fondé sur CL_AGE × "
                "CL_HAUT × CL_DENS. Si CL_AGE ∈ {JIN, JIR, VIN, VIR} → "
                "INEQUIENNE_*. Sinon REGULIERE_* selon CL_DENS et CL_HAUT."),
            "rasterization_method": "burn_value (rasterio.features.rasterize)",
        },
        "algorithmic_suggestions": [
            "1. geopandas.read_file(pee_maj.gpkg)",
            "2. Reproject vers EPSG:32198",
            "3. Apply structure_rules dataframe map sur CL_AGE × CL_HAUT × CL_DENS",
            "4. rasterio.features.rasterize avec burn_value=structure_class",
            "5. Persistance via rasterio.open(out_path, 'w', driver='GTiff', ...)",
        ],
        "scientific_references": [
            "MFFP (2016) — Manuel d'aménagement forestier durable, ch. 3",
            "Pothier & Savard (1998) Évaluation des classes structurales",
        ],
        "performance_notes": {
            "estimated_polygons": "~500k pour pee_maj.gpkg complet",
            "estimated_runtime": "5-15 min sur pod (CPU bound rasterisation)",
            "memory_peak_estimate_gb": 8,
        },
        "complexity": "MEDIUM",
    },
    # ─────────────────────────────────────────────────────────────────────
    "MFFP_DENSITY": {
        "label": "Densité de couvert forestier (% canopée)",
        "priority": "P0_CRITICAL_FOR_R9",
        "description": (
            "Pourcentage de couverture canopée par cellule, dérivé du "
            "champ CL_DENS et raffiné par GR_ESS."),
        "inputs_required": {
            "fields_pee_maj_gpkg": ["CL_DENS", "GR_ESS", "CL_HAUT"],
            "external_dictionaries": [
                "cl_dens_to_pct.json : A→90, B→70, C→50, D→32, E→15",
            ],
        },
        "outputs": {
            "format": "GeoTIFF",
            "epsg": TARGET_EPSG,
            "resolution_m": RESOLUTION_DEFAULT_M,
            "dtype": "uint8",
            "nodata": 0,
            "value_domain": "0-100 (% couverture)",
            "filename": "MFFP_COUVERT_FORESTIER_DENSITY.tif",
        },
        "key_parameters": {
            "density_pct_map": {"A": 90, "B": 70, "C": 50, "D": 32, "E": 15},
            "feuillus_correction_factor": 1.0,
            "resineux_correction_factor": 1.05,
        },
        "algorithmic_suggestions": [
            "1. Mapping CL_DENS → pct via dict.",
            "2. Application correction GR_ESS si applicable.",
            "3. rasterio.features.rasterize.",
        ],
        "scientific_references": [
            "Coops et al. (2007) Remote Sensing of Environment 110:113-129",
            "MFFP (2018) Normes d'inventaire écoforestier",
        ],
        "performance_notes": {
            "estimated_runtime": "3-8 min sur pod",
            "memory_peak_estimate_gb": 6,
        },
        "complexity": "LOW",
    },
    # ─────────────────────────────────────────────────────────────────────
    "MFFP_AGE": {
        "label": "Classes d'âge des peuplements (raster)",
        "priority": "P0_CRITICAL_FOR_R9",
        "description": (
            "Classification de l'âge des peuplements selon les bornes "
            "MFFP : 0-20, 20-40, 40-60, 60-80, 80-100, 100+ ans + classes "
            "spéciales inéquiennes (jeune/vieille)."),
        "inputs_required": {
            "fields_pee_maj_gpkg": ["CL_AGE", "AN_ORIGINE"],
            "external_dictionaries": ["classes_age.json"],
        },
        "outputs": {
            "format": "GeoTIFF",
            "epsg": TARGET_EPSG,
            "resolution_m": RESOLUTION_CLASSES_AGE_M,
            "dtype": "uint8",
            "nodata": 0,
            "value_domain": {
                "1": "0-20_ans",
                "2": "20-40_ans",
                "3": "40-60_ans",
                "4": "60-80_ans",
                "5": "80-100_ans",
                "6": "100+_ans",
                "7": "JEUNE_INEQUIENNE",
                "8": "VIEILLE_INEQUIENNE",
            },
            "filename": "MFFP_CLASSES_AGE.tif",
        },
        "key_parameters": {
            "age_class_bounds": {"10": (0, 20), "30": (20, 40),
                                  "50": (40, 60), "70": (60, 80),
                                  "90": (80, 100), "120": (100, 999)},
            "inequienne_codes": ["JIN", "JIR", "VIN", "VIR"],
        },
        "algorithmic_suggestions": [
            "1. Si CL_AGE ∈ inequienne_codes → classe spéciale.",
            "2. Sinon mapping CL_AGE → classe selon bornes.",
            "3. Optionnel : recalcul à partir AN_ORIGINE si CL_AGE manquant.",
        ],
        "scientific_references": [
            "MFFP (2016) — Manuel d'aménagement forestier durable, ch. 4",
        ],
        "performance_notes": {
            "estimated_runtime": "2-5 min",
            "memory_peak_estimate_gb": 4,
        },
        "complexity": "LOW",
    },
    # ─────────────────────────────────────────────────────────────────────
    "MFFP_FRAGMENTATION": {
        "label": "Indice de fragmentation forestière (Dickson 2017)",
        "priority": "P0_CRITICAL_FOR_R9",
        "description": (
            "Indice de fragmentation forestière calculé par fenêtre "
            "glissante (Dickson et al. 2017). Quantifie l'intégrité du "
            "couvert forestier dans une fenêtre 250m × 250m."),
        "inputs_required": {
            "fields_pee_maj_gpkg": ["TY_COUV", "GR_ESS", "CL_DENS"],
            "external_dictionaries": [
                "ty_couv_to_forest_binary.json : "
                "{FE,FR,FM,RE,RN}=1, autres=0",
            ],
            "external_layers": [
                "GIS_COUVERT_FORESTIER_BINARY.tif (rasterisation préalable)",
            ],
        },
        "outputs": {
            "format": "GeoTIFF",
            "epsg": TARGET_EPSG,
            "resolution_m": RESOLUTION_FRAGMENTATION_M,
            "dtype": "float32",
            "nodata": NODATA_VALUE,
            "value_domain": "0.0-1.0 (1.0 = forêt continue, 0.0 = fragmenté)",
            "filename": "MFFP_FRAGMENTATION_INDEX.tif",
        },
        "key_parameters": {
            "window_size_m": 250,
            "kernel": "moving_window 5x5 sur 50m base",
            "fragmentation_metric": "Pf (proportion forest cover) + Pff "
                                     "(proportion forest-forest adjacency)",
            "dickson_2017_formula": (
                "FRAG_INDEX = Pff / Pf si Pf > 0 sinon NaN"),
        },
        "algorithmic_suggestions": [
            "1. Rasteriser TY_COUV → forêt binaire (50m).",
            "2. scipy.ndimage.uniform_filter(window=5) sur binaire = Pf.",
            "3. Compute Pff via convolution voisinage 4-connectivité.",
            "4. FRAG_INDEX = Pff / max(Pf, eps).",
            "5. Resample à 250m (mean aggregation).",
        ],
        "scientific_references": [
            "Dickson, B.G., Roemer, G.W., Boyce, M.S. (2017) — Forest "
            "Ecology and Management 405: 85-94",
            "Riitters et al. (2002) Conservation Ecology 6(1): 1",
        ],
        "performance_notes": {
            "estimated_runtime": "10-30 min (convolutions lourdes)",
            "memory_peak_estimate_gb": 16,
            "gpu_acceleration_possible": False,
        },
        "complexity": "HIGH",
    },
    # ─────────────────────────────────────────────────────────────────────
    "MFFP_PRODUCTIVITY": {
        "label": "Productivité forestière (indice MFFP)",
        "priority": "P1_FOR_R9",
        "description": (
            "Indice de productivité du peuplement combinant CL_AGE × "
            "ESS_DOMI × IND_QUAL via tableaux de rendement MFFP."),
        "inputs_required": {
            "fields_pee_maj_gpkg": [
                "CL_AGE", "ESS_DOMI", "IND_QUAL", "TYPE_ECO",
            ],
            "external_dictionaries": [
                "tables_rendement_mffp.json (m³/ha selon ESS × CL_AGE × IND_QUAL)",
            ],
        },
        "outputs": {
            "format": "GeoTIFF",
            "epsg": TARGET_EPSG,
            "resolution_m": RESOLUTION_DEFAULT_M,
            "dtype": "float32",
            "nodata": NODATA_VALUE,
            "value_domain": "0.0-500.0 (m³/ha équivalent)",
            "filename": "MFFP_PRODUCTIVITE.tif",
        },
        "key_parameters": {
            "rendement_lookup_method": "trilinear ESS × AGE × IND_QUAL",
            "default_ind_qual_if_missing": "MOYEN",
        },
        "algorithmic_suggestions": [
            "1. Lookup tables_rendement_mffp[ESS_DOMI][CL_AGE][IND_QUAL].",
            "2. Si IND_QUAL manquant → utiliser MOYEN par défaut.",
            "3. Rasterisation pondérée par SUPERFICIE.",
        ],
        "scientific_references": [
            "MFFP (2018) — Tables de rendement provincial",
            "Pothier & Savard (1998)",
        ],
        "performance_notes": {
            "estimated_runtime": "5-12 min",
            "memory_peak_estimate_gb": 8,
        },
        "complexity": "MEDIUM",
    },
    # ─────────────────────────────────────────────────────────────────────
    "MFFP_HABITAT": {
        "label": "Habitat brut multi-espèces (raster multi-bandes)",
        "priority": "P1_FOR_R9",
        "description": (
            "Scoring d'habitabilité par espèce cible (5 bandes : "
            "chevreuil, orignal, ours noir, dindon, wapiti) basé sur les "
            "préférences MFFP × essences dominantes × structure × densité."),
        "inputs_required": {
            "fields_pee_maj_gpkg": ["ESS_DOMI", "GR_ESS", "CL_AGE",
                                     "CL_DENS", "TY_COUV", "TYPE_ECO"],
            "external_dictionaries": [
                "habitat_preferences_par_espece.json "
                "(matrice ESS × CL_AGE × CL_DENS → score 0-100)",
            ],
            "dependent_layers": [
                "MFFP_STRUCTURE", "MFFP_DENSITY", "MFFP_AGE",
            ],
        },
        "outputs": {
            "format": "GeoTIFF (5 bandes)",
            "epsg": TARGET_EPSG,
            "resolution_m": RESOLUTION_FRAGMENTATION_M,
            "dtype": "uint8",
            "nodata": 0,
            "value_domain": "0-100 par bande",
            "bands": [
                "chevreuil_brut", "orignal_brut", "ours_noir_brut",
                "dindon_brut", "wapiti_brut",
            ],
            "filename": "MFFP_HABITAT_BRUT.tif",
        },
        "key_parameters": {
            "scoring_function": "weighted_sum(préférences × variables)",
            "habitat_aggregation_window_m": 250,
        },
        "algorithmic_suggestions": [
            "1. Pour chaque espèce, charger préférences depuis dict.",
            "2. Calculer score = Σ(weight_i × variable_i) par polygone.",
            "3. Rasteriser par bande, persister GeoTIFF 5-bandes.",
        ],
        "scientific_references": [
            "MFFP (2010) Outils d'évaluation d'habitat faunique",
            "Drolet et al. (1999) — Habitat d'hiver du chevreuil",
            "Crête & Courtois (1997) — Habitat de l'orignal",
        ],
        "performance_notes": {
            "estimated_runtime": "15-25 min (5 espèces sequential)",
            "memory_peak_estimate_gb": 12,
            "parallelizable": True,
        },
        "complexity": "HIGH",
    },
    # ─────────────────────────────────────────────────────────────────────
    "MFFP_CONNECTIVITY": {
        "label": "Connectivité écologique brute (zonage écorégions)",
        "priority": "P2_FOR_R9",
        "description": (
            "Polygones d'écorégions issus du clustering spatial des "
            "peuplements similaires (ESS_DOMI × CL_AGE × CL_DENS) pour "
            "identifier les corridors potentiels."),
        "inputs_required": {
            "fields_pee_maj_gpkg": ["ESS_DOMI", "CL_AGE", "CL_DENS",
                                     "TYPE_ECO", "TY_COUV"],
            "external_dictionaries": [
                "ecological_clusters_definitions.json (Commandant à fournir)",
            ],
            "dependent_layers": ["MFFP_STRUCTURE", "MFFP_HABITAT"],
        },
        "outputs": {
            "format": "GeoPackage (vecteur)",
            "epsg": TARGET_EPSG,
            "geometry": "MultiPolygon",
            "attributes": [
                "cluster_id", "ecoregion_code", "habitat_score_mean",
                "fragmentation_score", "area_ha",
            ],
            "filename": "MFFP_CONNECTIVITE.gpkg",
        },
        "key_parameters": {
            "clustering_method": "DBSCAN ou unsupervised k-means spatial",
            "min_polygon_area_ha": 10,
            "merge_distance_m": 250,
            "saura_pascual_hortal_iic_index": True,
        },
        "algorithmic_suggestions": [
            "1. Calcul clé de similarité : f(ESS_DOMI, CL_AGE, CL_DENS).",
            "2. DBSCAN sur clé + position (lat,lon).",
            "3. Dissolve par cluster → MultiPolygon.",
            "4. Calcul IIC index (Saura & Pascual-Hortal 2007).",
        ],
        "scientific_references": [
            "Saura, S. & Pascual-Hortal, L. (2007) Conservation Genetics "
            "8(4): 877-883",
            "Tischendorf & Fahrig (2000) Oikos 90(1): 7-19",
        ],
        "performance_notes": {
            "estimated_runtime": "20-40 min (clustering + dissolves)",
            "memory_peak_estimate_gb": 20,
        },
        "complexity": "HIGH",
    },
    # ─────────────────────────────────────────────────────────────────────
    "MFFP_CONTINUITY": {
        "label": "Continuité forestière historique",
        "priority": "P2_FOR_R9",
        "description": (
            "Indice de continuité historique du peuplement basé sur "
            "AN_ORIGINE et historique des perturbations. Identifie les "
            "vieilles forêts continues vs régénérées."),
        "inputs_required": {
            "fields_pee_maj_gpkg": [
                "AN_ORIGINE", "ORIGINE", "PERTURB", "AN_PERTURB", "CL_AGE",
            ],
            "external_dictionaries": [
                "perturbation_severity.json (CHT=majeure, EL=partielle, ...)",
            ],
        },
        "outputs": {
            "format": "GeoTIFF",
            "epsg": TARGET_EPSG,
            "resolution_m": RESOLUTION_DEFAULT_M,
            "dtype": "uint8",
            "nodata": 0,
            "value_domain": {
                "1": "RECENT_<40ANS",
                "2": "INTERMEDIAIRE_40-80ANS",
                "3": "ANCIEN_80-150ANS",
                "4": "VIEILLES_FORETS_>150ANS",
                "5": "PERTURBE_RECEMMENT",
            },
            "filename": "MFFP_CONTINUITE.tif",
        },
        "key_parameters": {
            "current_year": 2026,
            "perturbation_window_recent": 20,
            "perturbation_severity_threshold_major": 0.5,
        },
        "algorithmic_suggestions": [
            "1. age_local = current_year - AN_ORIGINE.",
            "2. Si AN_PERTURB recent ET ORIGINE major → PERTURBE_RECEMMENT.",
            "3. Sinon classification par age_local (5 classes).",
        ],
        "scientific_references": [
            "Boucher et al. (2006) Disturbance regimes Quebec",
            "MFFP (2017) Vieilles forêts à conserver",
        ],
        "performance_notes": {
            "estimated_runtime": "5-10 min",
            "memory_peak_estimate_gb": 6,
        },
        "complexity": "MEDIUM",
    },
}


# ═════════════════════════════════════════════════════════════════════════
# Squelettes de fonctions Python — PHASE_3 R8
# Toutes lèvent NotImplementedError tant que specs métier non fournies.
# ═════════════════════════════════════════════════════════════════════════
def compute_mffp_structure(
    pee_maj_gpkg_path: str,
    structure_rules_dict: Dict[str, Any],
    output_tif_path: Optional[str] = None,
    target_epsg: int = TARGET_EPSG,
    resolution_m: int = RESOLUTION_DEFAULT_M,
) -> Dict[str, Any]:
    """ORDRE N°52-R11 · Skeleton MFFP_STRUCTURE.

    Args:
      pee_maj_gpkg_path : Chemin local vers pee_maj.gpkg (ex /var/cache/...)
      structure_rules_dict : Arbre décision MFFP CL_AGE × CL_HAUT × CL_DENS.
      output_tif_path : Chemin de sortie GeoTIFF (défaut: auto sous DERIVATIVES_OUTPUT_ROOT)
      target_epsg : 32198 (NAD83 Québec).
      resolution_m : 100m par défaut.

    Returns:
      dict {output_path, n_polygons_processed, n_pixels_burned,
            sha256_output, elapsed_s, value_distribution}

    Raises:
      NotImplementedError: tant que structure_rules_dict (Commandant) non fourni.
    """
    raise NotImplementedError(
        "MFFP_STRUCTURE · ANTI_GÉNÉRIQUE_STRICT · "
        "Spécifications structure_classification_rules.json non fournies "
        "par Commandant. Voir MFFP_LAYERS_SPECS['MFFP_STRUCTURE'].")


def compute_mffp_density(
    pee_maj_gpkg_path: str,
    cl_dens_to_pct_dict: Dict[str, int],
    output_tif_path: Optional[str] = None,
    target_epsg: int = TARGET_EPSG,
    resolution_m: int = RESOLUTION_DEFAULT_M,
    feuillus_correction: float = 1.0,
    resineux_correction: float = 1.05,
) -> Dict[str, Any]:
    """ORDRE N°52-R11 · Skeleton MFFP_DENSITY.

    Args:
      pee_maj_gpkg_path : Chemin local pee_maj.gpkg.
      cl_dens_to_pct_dict : {A:90, B:70, C:50, D:32, E:15} (Commandant).
      output_tif_path : GeoTIFF cible.

    Returns:
      dict {output_path, mean_pct, sha256_output, elapsed_s, …}.

    Raises:
      NotImplementedError: tant que cl_dens_to_pct_dict non validé.
    """
    raise NotImplementedError(
        "MFFP_DENSITY · ANTI_GÉNÉRIQUE_STRICT · "
        "Dictionnaire cl_dens_to_pct.json non validé par Commandant.")


def compute_mffp_age(
    pee_maj_gpkg_path: str,
    age_class_bounds: Dict[str, Tuple[int, int]],
    inequienne_codes: List[str],
    output_tif_path: Optional[str] = None,
    target_epsg: int = TARGET_EPSG,
    resolution_m: int = RESOLUTION_CLASSES_AGE_M,
) -> Dict[str, Any]:
    """ORDRE N°52-R11 · Skeleton MFFP_AGE.

    Args:
      age_class_bounds : {10:(0,20), 30:(20,40), …}.
      inequienne_codes : ['JIN','JIR','VIN','VIR'].
    """
    raise NotImplementedError(
        "MFFP_AGE · ANTI_GÉNÉRIQUE_STRICT · "
        "Validation bornes classes_age.json par Commandant requise.")


def compute_mffp_fragmentation(
    forest_binary_tif_path: str,
    output_tif_path: Optional[str] = None,
    window_size_m: int = 250,
    target_epsg: int = TARGET_EPSG,
) -> Dict[str, Any]:
    """ORDRE N°52-R11 · Skeleton MFFP_FRAGMENTATION (Dickson 2017).

    Args:
      forest_binary_tif_path : Raster binaire forêt/non-forêt 50m.
      window_size_m : 250m fenêtre glissante.

    Returns:
      dict {output_path, mean_frag_index, fully_forested_pct,
            sha256_output, elapsed_s}.
    """
    raise NotImplementedError(
        "MFFP_FRAGMENTATION · ANTI_GÉNÉRIQUE_STRICT · "
        "Validation algorithme Dickson 2017 + paramètres window/threshold "
        "par Commandant requise.")


def compute_mffp_productivity(
    pee_maj_gpkg_path: str,
    tables_rendement_mffp: Dict[str, Any],
    output_tif_path: Optional[str] = None,
    target_epsg: int = TARGET_EPSG,
    resolution_m: int = RESOLUTION_DEFAULT_M,
) -> Dict[str, Any]:
    """ORDRE N°52-R11 · Skeleton MFFP_PRODUCTIVITY (m³/ha)."""
    raise NotImplementedError(
        "MFFP_PRODUCTIVITY · ANTI_GÉNÉRIQUE_STRICT · "
        "Tables de rendement MFFP non fournies par Commandant.")


def compute_mffp_habitat(
    pee_maj_gpkg_path: str,
    habitat_preferences_by_species: Dict[str, Dict[str, Any]],
    species_list: List[str],
    output_tif_path: Optional[str] = None,
    target_epsg: int = TARGET_EPSG,
    resolution_m: int = RESOLUTION_FRAGMENTATION_M,
) -> Dict[str, Any]:
    """ORDRE N°52-R11 · Skeleton MFFP_HABITAT (multi-bandes 5 espèces).

    species_list par défaut : ['chevreuil','orignal','ours_noir','dindon','wapiti'].
    """
    raise NotImplementedError(
        "MFFP_HABITAT · ANTI_GÉNÉRIQUE_STRICT · "
        "habitat_preferences_par_espece.json non fournie par Commandant.")


def compute_mffp_connectivity(
    pee_maj_gpkg_path: str,
    mffp_structure_tif_path: str,
    mffp_habitat_tif_path: str,
    cluster_definitions: Dict[str, Any],
    output_gpkg_path: Optional[str] = None,
    target_epsg: int = TARGET_EPSG,
    min_polygon_area_ha: int = 10,
    merge_distance_m: int = 250,
) -> Dict[str, Any]:
    """ORDRE N°52-R11 · Skeleton MFFP_CONNECTIVITY (clustering DBSCAN)."""
    raise NotImplementedError(
        "MFFP_CONNECTIVITY · ANTI_GÉNÉRIQUE_STRICT · "
        "ecological_clusters_definitions.json non fournie par Commandant.")


def compute_mffp_continuity(
    pee_maj_gpkg_path: str,
    perturbation_severity_dict: Dict[str, float],
    current_year: int = 2026,
    output_tif_path: Optional[str] = None,
    target_epsg: int = TARGET_EPSG,
    resolution_m: int = RESOLUTION_DEFAULT_M,
) -> Dict[str, Any]:
    """ORDRE N°52-R11 · Skeleton MFFP_CONTINUITY (forêts anciennes)."""
    raise NotImplementedError(
        "MFFP_CONTINUITY · ANTI_GÉNÉRIQUE_STRICT · "
        "perturbation_severity.json non fournie par Commandant.")


# ═════════════════════════════════════════════════════════════════════════
# Plan d'implémentation minimal (R11 demande 3)
# ═════════════════════════════════════════════════════════════════════════
PHASE3_MINIMAL_PLAN: Dict[str, Any] = {
    "title": "Plan d'implémentation minimal PHASE_3 R8 — débloquer R9",
    "ordre": "N°52-R11_R12_UPDATED",
    "doctrine": "ANTI_GÉNÉRIQUE_STRICT",
    "priority_layers_4_critical": [
        "MFFP_STRUCTURE",   # P0 priority pour scoring corridor/zone_*
        "MFFP_DENSITY",     # P0 priority pour habitat / vegetation
        "MFFP_AGE",         # P0 priority pour zones_repos / zones_alimentation
        "MFFP_FRAGMENTATION",  # P0 priority pour corridors connectivité
    ],
    "implementation_order_recommended": [
        # Ordre = simple → complexe + dépendances respectées
        {
            "step": 1, "layer": "MFFP_DENSITY", "complexity": "LOW",
            "estimated_dev_hours": 4,
            "fields_used_pee_maj_gpkg": ["CL_DENS", "GR_ESS", "CL_HAUT"],
            "dictionaries_proposed_used": ["cl_dens_to_pct.json"],
            "subset_validation_tests": [
                "Histogramme distribution CL_DENS A/B/C/D/E (cohérent attendu)",
                "Statistiques mean_pct par GR_ESS (R > F par +5%)",
                "Compare 3-5 polygones échantillon vs lookup manuel dict",
                "SHA-256 raster output reproductible (run idempotent)",
            ],
            "note": "Mapping direct CL_DENS → pct via dict, rasterisation simple.",
        },
        {
            "step": 2, "layer": "MFFP_AGE", "complexity": "LOW",
            "estimated_dev_hours": 4,
            "fields_used_pee_maj_gpkg": ["CL_AGE", "AN_ORIGINE"],
            "dictionaries_proposed_used": ["classes_age.json"],
            "subset_validation_tests": [
                "Distribution classes 1-8 (régulières + inéquiennes)",
                "Vérifier fallback AN_ORIGINE si CL_AGE manquant",
                "JIN/JIR fusionnés en class_id=7 ; VIN/VIR=8",
                "% classe 6 (100+ ans) attendu : 5-15% selon écorégion",
            ],
            "note": "Mapping CL_AGE → bins MFFP via dict.",
        },
        {
            "step": 3, "layer": "MFFP_STRUCTURE", "complexity": "MEDIUM",
            "estimated_dev_hours": 12,
            "fields_used_pee_maj_gpkg": [
                "CL_AGE", "CL_HAUT", "CL_DENS", "GR_ESS", "TY_COUV"],
            "dictionaries_proposed_used": [
                "structure_classification_rules.json",
                "classes_age.json",
                "cl_dens_to_pct.json",
            ],
            "subset_validation_tests": [
                "Distribution 7 classes structurales (1-7)",
                "Cohérence step_1 (inéquiennes → 5/6) sur 50 cas test",
                "Cohérence step_3 (régulières/irrégulières) sur 50 cas test",
                "Fallback rule (REGULIERE_MONOSTRATE) appliqué si pas de match",
                "Comparaison croisée avec couches MFFP officielles (si dispo)",
            ],
            "note": "Arbre décision CL_AGE × CL_HAUT × CL_DENS appliqué via dict structure_classification_rules.",
        },
        {
            "step": 4, "layer": "MFFP_FRAGMENTATION", "complexity": "HIGH",
            "estimated_dev_hours": 24,
            "fields_used_pee_maj_gpkg": ["TY_COUV", "GR_ESS", "CL_DENS"],
            "dictionaries_proposed_used": ["ty_couv_to_forest_binary.json"],
            "prerequisites": [
                "GIS_COUVERT_FORESTIER_BINARY.tif (50m) calculé d'abord "
                "via ty_couv_to_forest_binary.json",
            ],
            "subset_validation_tests": [
                "Calcul Pf (proportion forêt) sur fenêtre 5×5",
                "Calcul Pff (proportion adjacences forêt-forêt)",
                "FRAG_INDEX = Pff/max(Pf, eps) range [0.0, 1.0]",
                "Validation visuelle 3-5 zones (forêt continue → 1.0)",
                "Validation Dickson 2017 sur 100 cas test",
            ],
            "note": "Convolutions Dickson 2017 + scipy.ndimage. Performance critique.",
        },
    ],
    "technical_dependencies": {
        "python_modules": [
            "geopandas>=0.14",
            "fiona>=1.9 OU pyogrio>=0.8",
            "rasterio>=1.3",
            "pyproj>=3.6",
            "shapely>=2.0",
            "scipy>=1.11 (ndimage pour fragmentation)",
            "numpy>=1.26",
        ],
        "system_libraries": [
            "GDAL >= 3.7",
            "GEOS >= 3.11",
            "PROJ >= 9.2",
        ],
        "dictionaries_required_from_commandant": [
            "structure_classification_rules.json",
            "cl_dens_to_pct.json",
            "classes_age.json (validation bornes MFFP)",
            "ty_couv_to_forest_binary.json",
        ],
        "dictionaries_proposed_status_R12": (
            "Les 4 dictionnaires sont fournis en mode PROPOSÉ par R12. "
            "Statuts disponibles via "
            "GET /api/v30/admin-premium/gis/territoire/dictionaries-proposed. "
            "Validation Commandant requise (passer status=PROPOSÉ → VALIDÉ)."),
        "validation_subset_required": (
            "Subset 100 Mo de pee_maj.gpkg (échantillon couvrant ≥ 5 "
            "écorégions) pour valider les algorithmes avant production. "
            "R12 propose : bbox Estrie/Cantons-Est EPSG:32198 "
            "[560000,175000,670000,250000]. Endpoint : "
            "POST /api/v30/admin-premium/gis/diagnostic/pee-maj/export-subset."),
    },
    "estimated_total_effort_hours_4_critical_layers": 44,
    "blocker_to_unblock_r9_targets": (
        "Une fois ces 4 couches en mode RÉEL (status=OK dans R8 PHASE_3), "
        "R9 targets corridors/hotspots/zones_* peuvent passer en RÉEL "
        "via l'application de score_final = score_orig×0.2 + score_MFFP×0.8."),
    "future_phases_p2": [
        "MFFP_PRODUCTIVITY (P1 · 16h dev)",
        "MFFP_HABITAT (P1 · 24h dev · 5 espèces)",
        "MFFP_CONNECTIVITY (P2 · 32h dev · clustering DBSCAN)",
        "MFFP_CONTINUITY (P2 · 12h dev · histoire perturbations)",
    ],
    "amplifier_modules_future": [
        "LiDAR (raffinement densité + hauteur réelle vs CL_HAUT)",
        "GEM (Global Ecological Model integration)",
        "Carte 2D/3D (visualisation immersive territoire)",
    ],
    "validation_protocol": (
        "Pour chaque couche : 1) tests unitaires avec subset 100 Mo, "
        "2) comparaison statistique avec layers MFFP officielles si "
        "disponibles, 3) validation visuelle sur 3-5 écorégions, "
        "4) signature SHA-256 + sceaux BCE-4X."),
    "v30_lock": "INVIOLÉ",
}


__all__ = [
    "MFFP_LAYERS_SPECS",
    "PHASE3_MINIMAL_PLAN",
    "TARGET_EPSG",
    "RESOLUTION_DEFAULT_M",
    "RESOLUTION_FRAGMENTATION_M",
    "RESOLUTION_CLASSES_AGE_M",
    "DERIVATIVES_OUTPUT_ROOT",
    "compute_mffp_structure",
    "compute_mffp_density",
    "compute_mffp_age",
    "compute_mffp_fragmentation",
    "compute_mffp_productivity",
    "compute_mffp_habitat",
    "compute_mffp_connectivity",
    "compute_mffp_continuity",
]

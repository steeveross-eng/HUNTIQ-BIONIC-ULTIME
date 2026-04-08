"""
CORE Scoring Pipeline — Constantes partagees
===============================================
Directive x3205. Extraites des 5 moteurs CORE + score_consolide.
Chaque constante est documentee: origine, justification, unite.
BCE-4X: Aucune valeur modifiee. Extraction pure.

ORIGINE DES CONSTANTES:
  - alimentation_v1/layers.py
  - alimentation_v2/terrain.py, salines.py
  - repos_v1/grid_generator.py
  - corridors_v10/cost_surface.py, engine.py, pathfinder.py
  - pression_v1/engine.py
  - modules/score_consolide.py
"""
import math

# ══════════════════════════════════════════════════════════════════
# GEODESIE
# ══════════════════════════════════════════════════════════════════

# Metres par degre de latitude (approximation spherique)
# Origine: Standard geodesique. Utilise dans 4 fichiers.
# Unite: m/deg
METERS_PER_DEG_LAT = 111320.0


def meters_per_deg_lng(lat: float) -> float:
    """Metres par degre de longitude a une latitude donnee.
    Origine: corridors_v10/cost_surface.py, repos_v1/grid_generator.py
    Unite: m/deg"""
    return 111320.0 * math.cos(math.radians(lat))


# ══════════════════════════════════════════════════════════════════
# BARRIERES (corridors_v10)
# ══════════════════════════════════════════════════════════════════

# Cout infini pour les barrieres absolues (eau, pente extreme)
# Origine: corridors_v10/cost_surface.py, pathfinder.py
# Unite: sans dimension
INFINITY_COST = 999999.0

# ══════════════════════════════════════════════════════════════════
# GRILLE
# ══════════════════════════════════════════════════════════════════

# Taille par defaut du carre d'analyse
# Origine: Tous les moteurs (parametre side_m)
# Unite: metres
DEFAULT_SIDE_M = 2000.0

# Taille cellule par defaut pour alimentation_v1 et repos_v1
# Origine: alimentation_v1/engine.py, repos_v1/engine.py
# Unite: metres
DEFAULT_CELL_M_FINE = 10.0

# Taille cellule par defaut pour corridors_v10
# Origine: corridors_v10/engine.py
# Unite: metres
DEFAULT_CELL_M_CORRIDOR = 25.0

# Pas d'echantillonnage par defaut
# Origine: alimentation_v1/engine.py, repos_v1/engine.py
# Unite: sans dimension (1 cellule sur N)
DEFAULT_SAMPLE_STEP = 5

# ══════════════════════════════════════════════════════════════════
# PONDERATIONS SCORE CONSOLIDE
# ══════════════════════════════════════════════════════════════════

# Poids de chaque moteur dans le score consolide
# Origine: score_consolide.py
# x4100: Option C — CORE 60%, Nouveaux 40% (directive STEEVE-MAX)
# Somme = 1.0000
ENGINE_WEIGHTS = {
    # ── CORE (60%) ──
    "alimentation": 0.1503,
    "repos": 0.12,
    "corridors_v10": 0.15,
    "alimentation_v2": 0.06,
    "pression": 0.12,
    # ── CORE++ (17.14%) ──
    "hydro": 0.0348,
    "thermal": 0.0261,
    "ndvi_vegetation": 0.0304,
    "weather": 0.0217,
    "temporal": 0.0217,
    "habitat": 0.0348,
    "ecosystem": 0.0217,
    # ── CORE+++ (11.73%) ──
    "behavior": 0.0217,
    "risk": 0.0261,
    "opportunity": 0.0261,
    "attractors": 0.0304,
    "scenario": 0.013,
    # ── BIONIC-OS (9.12%) ──
    "simulation": 0.013,
    "multi_species": 0.0174,
    "trajets": 0.0261,
    "visibility": 0.0217,
    "learning": 0.013,
}

# ══════════════════════════════════════════════════════════════════
# MS-1: PONDERATIONS DYNAMIQUES PAR ESPECE
# BCE-4X ULTIME ABSOLU x3 — COMMANDANT STEEVE-MAX
# Chaque espece a sa propre matrice de poids.
# Somme = 1.0000 pour chaque espece.
# ══════════════════════════════════════════════════════════════════

SPECIES_ENGINE_WEIGHTS = {
    "CERF": {
        "alimentation": 0.18,
        "repos": 0.11,
        "corridors_v10": 0.12,
        "alimentation_v2": 0.08,
        "pression": 0.10,
        "hydro": 0.03,
        "thermal": 0.02,
        "ndvi_vegetation": 0.03,
        "weather": 0.02,
        "temporal": 0.02,
        "habitat": 0.06,
        "ecosystem": 0.02,
        "behavior": 0.04,
        "risk": 0.02,
        "opportunity": 0.03,
        "attractors": 0.04,
        "scenario": 0.01,
        "simulation": 0.01,
        "multi_species": 0.01,
        "trajets": 0.02,
        "visibility": 0.02,
        "learning": 0.01,
    },
    "ORIGNAL": {
        "alimentation": 0.14,
        "repos": 0.10,
        "corridors_v10": 0.15,
        "alimentation_v2": 0.06,
        "pression": 0.11,
        "hydro": 0.08,
        "thermal": 0.04,
        "ndvi_vegetation": 0.03,
        "weather": 0.02,
        "temporal": 0.02,
        "habitat": 0.05,
        "ecosystem": 0.02,
        "behavior": 0.03,
        "risk": 0.02,
        "opportunity": 0.02,
        "attractors": 0.03,
        "scenario": 0.01,
        "simulation": 0.01,
        "multi_species": 0.01,
        "trajets": 0.03,
        "visibility": 0.01,
        "learning": 0.01,
    },
    "OURS": {
        "alimentation": 0.22,
        "repos": 0.08,
        "corridors_v10": 0.10,
        "alimentation_v2": 0.04,
        "pression": 0.10,
        "hydro": 0.04,
        "thermal": 0.03,
        "ndvi_vegetation": 0.05,
        "weather": 0.02,
        "temporal": 0.02,
        "habitat": 0.06,
        "ecosystem": 0.02,
        "behavior": 0.04,
        "risk": 0.02,
        "opportunity": 0.04,
        "attractors": 0.05,
        "scenario": 0.01,
        "simulation": 0.01,
        "multi_species": 0.01,
        "trajets": 0.02,
        "visibility": 0.01,
        "learning": 0.01,
    },
    "DINDON": {
        "alimentation": 0.20,
        "repos": 0.10,
        "corridors_v10": 0.08,
        "alimentation_v2": 0.04,
        "pression": 0.08,
        "hydro": 0.03,
        "thermal": 0.02,
        "ndvi_vegetation": 0.05,
        "weather": 0.02,
        "temporal": 0.03,
        "habitat": 0.08,
        "ecosystem": 0.02,
        "behavior": 0.05,
        "risk": 0.03,
        "opportunity": 0.04,
        "attractors": 0.04,
        "scenario": 0.01,
        "simulation": 0.01,
        "multi_species": 0.01,
        "trajets": 0.02,
        "visibility": 0.03,
        "learning": 0.01,
    },
    "WAPITI": {
        "alimentation": 0.16,
        "repos": 0.10,
        "corridors_v10": 0.14,
        "alimentation_v2": 0.06,
        "pression": 0.10,
        "hydro": 0.05,
        "thermal": 0.03,
        "ndvi_vegetation": 0.04,
        "weather": 0.02,
        "temporal": 0.02,
        "habitat": 0.05,
        "ecosystem": 0.02,
        "behavior": 0.03,
        "risk": 0.03,
        "opportunity": 0.03,
        "attractors": 0.03,
        "scenario": 0.01,
        "simulation": 0.01,
        "multi_species": 0.02,
        "trajets": 0.03,
        "visibility": 0.01,
        "learning": 0.01,
    },
}

def get_species_weights(species):
    """Retourne la matrice de poids pour une espece donnee.
    Fallback: ENGINE_WEIGHTS (matrice generique) si espece inconnue."""
    return SPECIES_ENGINE_WEIGHTS.get(species.upper(), ENGINE_WEIGHTS)

# ══════════════════════════════════════════════════════════════════
# SALINES (alimentation_v2)
# ══════════════════════════════════════════════════════════════════

# Nombre maximum de salines par analyse
# Origine: alimentation_v2/engine.py
# Unite: sans dimension
MAX_SALINES = 4

# Distance minimale entre salines (diversification spatiale)
# Origine: alimentation_v2/engine.py (directive STEEVE-MAX)
# Unite: metres
MIN_SALINE_DISTANCE_M = 300.0

# Nombre de candidats generes pour la selection de salines
# Origine: alimentation_v2/salines.py
# Unite: sans dimension
SALINE_CANDIDATES_COUNT = 16

# Especes sans salines (directive biologique STEEVE-MAX)
# Origine: alimentation_v2/engine.py
SPECIES_NO_SALINES = {"OURS", "DINDON"}

# ══════════════════════════════════════════════════════════════════
# SEUILS DE CARENCES (alimentation_v2)
# ══════════════════════════════════════════════════════════════════

# Seuils de detection des carences en nutriments du sol
# Origine: alimentation_v2/engine.py
# Unite: ppm (parties par million)
CARENCE_THRESHOLDS = {
    "selenium_ppm": (0.2, "Selenium"),
    "cuivre_ppm": (3, "Cuivre"),
    "calcium_ppm": (500, "Calcium"),
    "phosphore_ppm": (10, "Phosphore"),
    "zinc_ppm": (5, "Zinc"),
}

# ══════════════════════════════════════════════════════════════════
# NDVI SAISONNIER
# ══════════════════════════════════════════════════════════════════

# Multiplicateur NDVI par mois (normalisation vegetale saisonniere)
# Origine: alimentation_v1/layers.py, corridors_v10/cost_surface.py
# Unite: sans dimension [0, 1]
NDVI_SEASONAL_MULTIPLIERS = {
    1: 0.10, 2: 0.12, 3: 0.35, 4: 0.55, 5: 0.75, 6: 0.90,
    7: 1.00, 8: 0.95, 9: 0.80, 10: 0.60, 11: 0.30, 12: 0.15,
}

# ══════════════════════════════════════════════════════════════════
# HEURISTIQUE A* (corridors_v10)
# ══════════════════════════════════════════════════════════════════

# Racine de 2 pour les deplacements diagonaux
# Origine: corridors_v10/pathfinder.py
SQRT2 = math.sqrt(2)

# Multiplicateurs de style de deplacement
# Origine: corridors_v10/pathfinder.py
STYLE_MULTIPLIERS = {
    "lineaire": {"diag": 1.2, "straight": 0.9},
    "sinueux": {"diag": 0.95, "straight": 1.0},
    "opportuniste": {"diag": 1.0, "straight": 1.0},
    "migratoire": {"diag": 1.1, "straight": 0.85},
    "territorial": {"diag": 1.0, "straight": 1.05},
}

# ══════════════════════════════════════════════════════════════════
# COUT MINIMUM (corridors_v10)
# ══════════════════════════════════════════════════════════════════

# Cout minimum de traversee d'une cellule (jamais zero pour A*)
# Origine: corridors_v10/cost_surface.py
# Unite: sans dimension
MIN_TRAVERSAL_COST = 0.5

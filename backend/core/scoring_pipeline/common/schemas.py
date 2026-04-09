"""
CORE Scoring Pipeline — Schemas d'entree/sortie normalises
==============================================================
Directive x3205. Schemas JSON internes pour validation future.
Definit les structures standard que chaque moteur doit respecter.

BCE-4X: Documentation des structures existantes. Aucune modification
des signatures ou des objets retournes par les moteurs actuels.
"""
from dataclasses import dataclass, field
from typing import Optional


# ══════════════════════════════════════════════════════════════════
# SCHEMAS D'ENTREE
# ══════════════════════════════════════════════════════════════════

@dataclass
class CoreAnalysisInput:
    """Schema d'entree standard pour tous les moteurs CORE.
    Tout moteur accepte au minimum ces parametres."""
    center_lat: float
    center_lng: float
    species: str = "CERF"
    month: int = 10


@dataclass
class GridAnalysisInput(CoreAnalysisInput):
    """Schema d'entree pour les analyses sur grille."""
    side_m: float = 2000.0
    cell_m: float = 10.0
    sample_step: int = 5


@dataclass
class CorridorAnalysisInput(CoreAnalysisInput):
    """Schema d'entree pour l'analyse de corridors."""
    side_m: float = 2000.0
    cell_m: float = 25.0


@dataclass
class AlimentationV2Input(CoreAnalysisInput):
    """Schema d'entree pour ALIMENTATION-V2."""
    max_salines: int = 2


# ══════════════════════════════════════════════════════════════════
# SCHEMAS DE SORTIE
# ══════════════════════════════════════════════════════════════════

@dataclass
class CoreScoreResult:
    """Schema de sortie standard — score unique.
    Tout moteur retournant un score pour un point doit inclure ces champs."""
    engine: str
    score: float
    classe: str
    label_fr: str
    color: str
    species: str
    month: int
    season: str


@dataclass
class CoreGridResult:
    """Schema de sortie standard — analyse sur grille.
    Tout moteur retournant une analyse de grille doit inclure ces champs."""
    engine: str
    version: str
    species: str
    season: str
    month: int
    grid: dict         # {center_lat, center_lng, side_m, cell_m, total_cells, ...}
    statistics: dict   # {total, distribution, avg_score, min_score, max_score}


@dataclass
class CoreValidation:
    """Schema de sortie pour les validations BCE-4X / Steeve-MAX."""
    status: str        # "PASS", "FAIL", "WARN"
    errors: list = field(default_factory=list)
    warnings: list = field(default_factory=list)
    checks: dict = field(default_factory=dict)
    total_checks: int = 0
    passed_checks: int = 0


@dataclass
class ConsolidatedScoreResult:
    """Schema de sortie du score consolide."""
    score: float
    classe: str
    label: str
    color: str
    species: str
    month: int
    components: dict       # {moteur: score}
    weights: dict          # {moteur: poids_normalise}
    tracability: dict      # {details de tracabilite}
    is_water: bool = False


# ══════════════════════════════════════════════════════════════════
# SCHEMA DE METADONNEES
# ══════════════════════════════════════════════════════════════════

@dataclass
class EngineMetadata:
    """Metadonnees standard d'un moteur CORE."""
    name: str              # Ex: "ALIMENTATION-V1"
    version: str           # Ex: "1.0.0"
    engine_type: str       # "score", "network", "analysis"
    domain: str            # "alimentation", "repos", "corridors", "pression"
    unit: str              # "score_0_100", "network_score", etc.
    default_weight: float  # Poids dans le score consolide
    species_count: int = 5
    seasonal: bool = True
    bce4x_validated: bool = True


# ══════════════════════════════════════════════════════════════════
# REGISTRE DES MOTEURS CORE
# ══════════════════════════════════════════════════════════════════

ENGINE_METADATA = {
    "ALIMENTATION_V1": EngineMetadata(
        name="ALIMENTATION-V1", version="1.0.0",
        engine_type="score", domain="alimentation",
        unit="score_0_100", default_weight=0.25,
    ),
    "ALIMENTATION_V2": EngineMetadata(
        name="ALIMENTATION-V2", version="2.0.0",
        engine_type="analysis", domain="alimentation",
        unit="score_0_100", default_weight=0.10,
    ),
    "REPOS_V1": EngineMetadata(
        name="REPOS-V1", version="1.0.0",
        engine_type="score", domain="repos",
        unit="score_0_100", default_weight=0.20,
    ),
    "CORRIDORS_V10": EngineMetadata(
        name="CORRIDORS-V10", version="10.0.0",
        engine_type="network", domain="corridors",
        unit="score_0_100", default_weight=0.25,
    ),
    "PRESSION_V1": EngineMetadata(
        name="PRESSION-V1", version="1.0.0",
        engine_type="score", domain="pression",
        unit="score_0_100", default_weight=0.20,
        seasonal=False,
    ),
}

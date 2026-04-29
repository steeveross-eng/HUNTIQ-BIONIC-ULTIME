"""
PHASE XV — ENGINES SCIENTIFIQUES_Ω
═════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU x3 · ORDRE N°28

5 ENGINES SCIENTIFIQUES_Ω + ENGINE_IA_Ω institutionnels.
Source unique : BIO_REACTEURS_Ω (chaîne validée RAPPORT_DOCX → BIO_PROFILE_Ω → BIO_REACTEUR_Ω).

Aucune logique générique. Aucun fallback. Aucune interpolation. V30 INVIOLÉ.
═════════════════════════════════════════════════════════════════════
"""
from .engine_vision_omega import compute as compute_vision, ENGINE_VISION_SPEC
from .engine_odeur_omega import compute as compute_odeur, ENGINE_ODEUR_SPEC
from .engine_patterns_omega import compute as compute_patterns, ENGINE_PATTERNS_SPEC
from .engine_comportement_omega import compute as compute_comportement, ENGINE_COMPORTEMENT_SPEC
from .engine_sensoriel_omega import compute as compute_sensoriel, ENGINE_SENSORIEL_SPEC
from .engine_ia_omega import compute_ia, ENGINE_IA_SPEC

ENGINES_SCIENTIFIQUES_Ω = {
    "ENGINE_VISION_Ω": (compute_vision, ENGINE_VISION_SPEC),
    "ENGINE_ODEUR_Ω": (compute_odeur, ENGINE_ODEUR_SPEC),
    "ENGINE_PATTERNS_Ω": (compute_patterns, ENGINE_PATTERNS_SPEC),
    "ENGINE_COMPORTEMENT_Ω": (compute_comportement, ENGINE_COMPORTEMENT_SPEC),
    "ENGINE_SENSORIEL_Ω": (compute_sensoriel, ENGINE_SENSORIEL_SPEC),
}

__all__ = [
    "ENGINES_SCIENTIFIQUES_Ω",
    "compute_vision", "compute_odeur", "compute_patterns",
    "compute_comportement", "compute_sensoriel", "compute_ia",
    "ENGINE_VISION_SPEC", "ENGINE_ODEUR_SPEC", "ENGINE_PATTERNS_SPEC",
    "ENGINE_COMPORTEMENT_SPEC", "ENGINE_SENSORIEL_SPEC", "ENGINE_IA_SPEC",
]

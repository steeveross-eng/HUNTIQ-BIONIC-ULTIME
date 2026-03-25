"""
CORE Scoring Pipeline — Fonctions de hash deterministiques
=============================================================
Directive x3205. Documentation des variantes de hash existantes.

ATTENTION — DIVERGENCE DOCUMENTEE:
  Deux algorithmes de normalisation coexistent dans le pipeline:
    - Variante A: `% 10000 / 10000.0` (alimentation_v1, corridors_v10)
    - Variante B: `/ 0xFFFFFFFF`       (alimentation_v2, score_consolide)

  De plus, score_consolide.py utilise 5 decimales tandis que les
  moteurs utilisent 6 decimales pour l'arrondi des coordonnees.

  Ces differences produisent des valeurs SUBTILEMENT DIFFERENTES
  pour les memes coordonnees. La correction est prevue pour x3300.

  BCE-4X x3205: On NE MODIFIE PAS les fonctions existantes.
  Ce fichier fournit une reference canonique pour les futures
  normalisations.
"""
import hashlib
import math


# ══════════════════════════════════════════════════════════════════
# VARIANTE A — alimentation_v1/layers.py, corridors_v10/cost_surface.py
# Normalisation: int(hex[:8], 16) % 10000 / 10000.0
# Precision entree: 6 decimales
# Plage sortie: [0.0, 0.9999]
# ══════════════════════════════════════════════════════════════════

def deterministic_hash_a(lat: float, lng: float, seed: str = "") -> float:
    """Hash deterministique variante A (alimentation_v1, corridors_v10).
    Plage: [0, 0.9999] par pas de 0.0001."""
    raw = f"{lat:.6f}:{lng:.6f}:{seed}"
    h = int(hashlib.md5(raw.encode()).hexdigest()[:8], 16)
    return (h % 10000) / 10000.0


# ══════════════════════════════════════════════════════════════════
# VARIANTE B — alimentation_v2/terrain.py, alimentation_v2/salines.py
# Normalisation: int(hex[:8], 16) / 0xFFFFFFFF
# Precision entree: 6 decimales
# Plage sortie: [0.0, 1.0] (quasi-continu)
# ══════════════════════════════════════════════════════════════════

def deterministic_hash_b(lat: float, lng: float, seed: str = "") -> float:
    """Hash deterministique variante B (alimentation_v2).
    Plage: [0, 1.0] quasi-continu."""
    h = hashlib.md5(f"{lat:.6f}:{lng:.6f}:{seed}".encode()).hexdigest()
    return int(h[:8], 16) / 0xFFFFFFFF


# ══════════════════════════════════════════════════════════════════
# VARIANTE C — score_consolide.py (PROXY)
# Normalisation: int(hex[:8], 16) / 0xFFFFFFFF
# Precision entree: 5 decimales (DIVERGENT)
# Plage sortie: [0.0, 1.0]
# ══════════════════════════════════════════════════════════════════

def deterministic_hash_c(lat: float, lng: float, seed: str = "") -> float:
    """Hash deterministique variante C (score_consolide — 5 decimales).
    ATTENTION: Precision reduite par rapport aux variantes A et B."""
    h = hashlib.md5(f"{lat:.5f}:{lng:.5f}:{seed}".encode()).hexdigest()
    return int(h[:8], 16) / 0xFFFFFFFF


# ══════════════════════════════════════════════════════════════════
# MODELE D'ELEVATION PARTAGE
# Origine: alimentation_v1/layers.py, corridors_v10/cost_surface.py
# 2 copies identiques dans le codebase
# ══════════════════════════════════════════════════════════════════

def elevation_model(lat: float, lng: float) -> float:
    """Modele numerique de terrain algorithmique (MNT) pour le Quebec.
    Identique dans alimentation_v1 et corridors_v10."""
    base = 150 + 200 * math.sin(lat * 0.8) * math.cos(lng * 0.5)
    variation = 80 * deterministic_hash_a(lat, lng, "elev")
    return max(10, base + variation)


# ══════════════════════════════════════════════════════════════════
# DOCUMENTATION DES DIVERGENCES
# ══════════════════════════════════════════════════════════════════

HASH_VARIANTS = {
    "A": {
        "files": ["alimentation_v1/layers.py", "corridors_v10/cost_surface.py"],
        "precision_input": 6,
        "normalization": "% 10000 / 10000.0",
        "range": "[0.0, 0.9999]",
        "granularity": 10000,
    },
    "B": {
        "files": ["alimentation_v2/terrain.py", "alimentation_v2/salines.py"],
        "precision_input": 6,
        "normalization": "/ 0xFFFFFFFF",
        "range": "[0.0, 1.0]",
        "granularity": 4294967295,
    },
    "C": {
        "files": ["modules/score_consolide.py"],
        "precision_input": 5,
        "normalization": "/ 0xFFFFFFFF",
        "range": "[0.0, 1.0]",
        "granularity": 4294967295,
        "WARNING": "Precision reduite (5 decimales vs 6)",
    },
}

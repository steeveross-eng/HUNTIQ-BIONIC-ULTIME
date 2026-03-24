"""
SALINE INTELLIGENCE ULTRA — Vegetation & Forage Engine V1
Analyse couvert vegetal, ressources fourrageres, phenologie saisonniere.
Interconnecte: alimentation_v2/terrain, data_layers/ecoforestry, exclusion_engine_v7.

Conformite: GOLDEN-BCE-4X | BCE ULTRA MAX | STEEVE-MAX x1000
"""
import math
import hashlib
import logging
from typing import Dict, Any, List

logger = logging.getLogger("saline.vegetation_forage")

# Phenological phases by month (Quebec latitudes 45-52N)
PHENOLOGY = {
    1: "dormance", 2: "dormance", 3: "pre_debourrement",
    4: "debourrement", 5: "croissance_active", 6: "croissance_active",
    7: "maturite", 8: "maturite", 9: "senescence",
    10: "senescence", 11: "dormance", 12: "dormance",
}

# Forage quality index by vegetation type and season
FORAGE_QUALITY = {
    "feuillus_jeunes": {"croissance_active": 0.95, "maturite": 0.80, "senescence": 0.40, "dormance": 0.05},
    "resineux": {"croissance_active": 0.60, "maturite": 0.55, "senescence": 0.50, "dormance": 0.45},
    "arbustes": {"croissance_active": 0.90, "maturite": 0.75, "senescence": 0.30, "dormance": 0.10},
    "herbacees": {"croissance_active": 0.85, "maturite": 0.70, "senescence": 0.20, "dormance": 0.02},
    "plantes_aquatiques": {"croissance_active": 0.95, "maturite": 0.90, "senescence": 0.15, "dormance": 0.0},
}

# Mineral content by vegetation type (mg/kg dry matter)
VEGETATION_MINERALS = {
    "feuillus_jeunes": {"Ca": 12000, "P": 2800, "K": 18000, "Mg": 3200, "Na": 150, "Zn": 25, "Cu": 8, "Se": 0.05},
    "resineux": {"Ca": 5000, "P": 1200, "K": 6000, "Mg": 1800, "Na": 80, "Zn": 15, "Cu": 4, "Se": 0.03},
    "arbustes": {"Ca": 9000, "P": 2200, "K": 15000, "Mg": 2800, "Na": 120, "Zn": 22, "Cu": 7, "Se": 0.04},
    "herbacees": {"Ca": 4000, "P": 3500, "K": 25000, "Mg": 2000, "Na": 200, "Zn": 30, "Cu": 6, "Se": 0.08},
    "plantes_aquatiques": {"Ca": 15000, "P": 4000, "K": 30000, "Mg": 5000, "Na": 8000, "Zn": 40, "Cu": 10, "Se": 0.12},
}


def _seed(lat: float, lng: float, salt: str = "") -> float:
    h = hashlib.md5(f"{lat:.6f}:{lng:.6f}:{salt}".encode()).hexdigest()
    return int(h[:8], 16) / 0xFFFFFFFF


def analyze_vegetation(lat: float, lng: float, month: int = 10, terrain: Dict = None) -> Dict[str, Any]:
    """
    Analyse complete du couvert vegetal et des ressources fourrageres.
    Reutilise les donnees terrain de alimentation_v2 si fournies.
    """
    phenophase = PHENOLOGY.get(month, "dormance")

    # Reuse terrain data from alimentation_v2 or generate
    if terrain and "foret" in terrain:
        couvert_pct = terrain["foret"].get("couvert_pct", 65)
        essences = terrain["foret"].get("essences", [])
        strate_arbustive = terrain["foret"].get("strate_arbustive_pct", 30)
        has_aquatic = terrain.get("alimentaire", {}).get("plantes_aquatiques", False)
    else:
        couvert_pct = 40 + _seed(lat, lng, "couv") * 55
        essences = []
        strate_arbustive = 15 + _seed(lat, lng, "arbu") * 45
        has_aquatic = _seed(lat, lng, "aqua") > 0.6

    # Calculate vegetation composition
    pct_feuillus = sum(e.get("pct", 0) for e in essences if e.get("type") == "feuillus")
    pct_resineux = sum(e.get("pct", 0) for e in essences if e.get("type") == "résineux")
    if pct_feuillus + pct_resineux == 0:
        pct_feuillus = 50 + _seed(lat, lng, "feu") * 30
        pct_resineux = 100 - pct_feuillus

    # Vegetation layers
    layers = {
        "feuillus_jeunes": round(pct_feuillus * 0.3 * couvert_pct / 100, 1),
        "resineux": round(pct_resineux * couvert_pct / 100, 1),
        "arbustes": round(strate_arbustive, 1),
        "herbacees": round(max(5, 100 - couvert_pct) * 0.6, 1),
        "plantes_aquatiques": round(15 * _seed(lat, lng, "aq_pct"), 1) if has_aquatic else 0,
    }

    # Forage quality per layer
    forage = {}
    total_forage_score = 0
    total_pct = 0
    for veg_type, pct in layers.items():
        if pct <= 0:
            continue
        quality = FORAGE_QUALITY.get(veg_type, {}).get(phenophase, 0.3)
        quality *= (0.85 + 0.3 * _seed(lat, lng, f"fq_{veg_type}"))
        quality = min(1.0, quality)
        forage[veg_type] = {
            "cover_pct": pct,
            "quality_index": round(quality, 3),
            "available_biomass_kg_ha": round(pct * quality * 50, 1),
        }
        total_forage_score += pct * quality
        total_pct += pct

    avg_forage = total_forage_score / total_pct if total_pct > 0 else 0

    # Mineral content from vegetation (weighted average)
    veg_minerals = {}
    for mineral in ["Ca", "P", "K", "Mg", "Na", "Zn", "Cu", "Se"]:
        weighted = 0
        weight_sum = 0
        for veg_type, pct in layers.items():
            if pct <= 0:
                continue
            m_content = VEGETATION_MINERALS.get(veg_type, {}).get(mineral, 0)
            phenofactor = FORAGE_QUALITY.get(veg_type, {}).get(phenophase, 0.3)
            weighted += m_content * pct * phenofactor
            weight_sum += pct * phenofactor
        veg_minerals[mineral] = round(weighted / weight_sum, 1) if weight_sum > 0 else 0

    # Na deficit indicator (vegetation is almost always Na-deficient)
    na_deficit = veg_minerals.get("Na", 0) < 500

    return {
        "latitude": lat,
        "longitude": lng,
        "month": month,
        "phenophase": phenophase,
        "couvert_pct": round(couvert_pct, 1),
        "layers": layers,
        "forage": forage,
        "avg_forage_quality": round(avg_forage, 3),
        "vegetation_minerals_mg_kg": veg_minerals,
        "na_deficit_from_vegetation": na_deficit,
        "carrying_capacity_index": round(avg_forage * couvert_pct / 100, 3),
        "source": "BIONIC alimentation_v2/terrain + ecoforestry layers",
    }

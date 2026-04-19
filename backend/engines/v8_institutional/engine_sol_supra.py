"""
ENGINE-SOL-SUPRA — Moteur pédologie institutionnel
====================================================
Inputs: terrain_v10 (IRDA drainage/moisture + LiDAR rugosite)
Outputs: score 0-100, fertility_index, texture_class, mineral_indices
"""
from engines.v8_institutional.engine_science_omega import register_engine, mark_call

ENGINE_NAME = "ENGINE-SOL-SUPRA"
ENGINE_VERSION = "V1-SUPRA-2026-04"

register_engine(
    name=ENGINE_NAME,
    version=ENGINE_VERSION,
    description="Pédologie institutionnelle (fertilité, texture, indices minéraux Ca/Na/K/Mg)",
    pillar="BIO-SYSTEME",
    dependencies=["IRDA_PEDOLOGIE", "LIDAR_WCS_1M"],
)


def _texture_class(drainage: int, moisture: float) -> str:
    if drainage <= 2 and moisture > 0.5:
        return "argileux-hydrique"
    if drainage <= 3:
        return "argileux"
    if drainage >= 6:
        return "sableux"
    if drainage >= 5:
        return "sablo-limoneux"
    return "limoneux"


def compute_sol_supra(terrain_v10: dict) -> dict:
    mark_call(ENGINE_NAME)
    terrain = terrain_v10.get("terrain", terrain_v10) if isinstance(terrain_v10, dict) else {}

    drainage = terrain.get("drainage_class", 3)
    soil_moisture = terrain.get("soil_moisture", 0.3)
    rugosite = terrain.get("rugosite", 0.5)
    canopy = terrain.get("canopy", 0.5)
    feuillus = terrain.get("feuillus_ratio", 0.4)

    # Qualite du sol (0-1)
    sol_quality = max(0.1, min(1.0,
        (1 - abs(drainage - 4) / 4) * 0.5 + (1 - abs(soil_moisture - 0.35) / 0.35) * 0.5
    ))

    # Fertilite = sol_quality + litiere (canopy + feuillus)
    fertility = round(min(100, sol_quality * 60 + canopy * 20 + feuillus * 20), 1)

    # Indices mineraux (proxies depuis drainage + litiere)
    mineraux = {
        "calcium_index": round(min(1.0, sol_quality * 0.4 + (1 - abs(drainage - 5) / 5) * 0.4 + feuillus * 0.2), 3),
        "sodium_index": round(min(1.0, (1 - soil_moisture) * 0.3 + (drainage / 7) * 0.4 + 0.3), 3),
        "potassium_index": round(min(1.0, sol_quality * 0.5 + canopy * 0.3 + rugosite * 0.2), 3),
        "magnesium_index": round(min(1.0, sol_quality * 0.6 + canopy * 0.2 + feuillus * 0.2), 3),
    }

    texture = _texture_class(drainage, soil_moisture)

    # Score composite: fertility 50%, mineraux moyenne 50%
    min_avg = sum(mineraux.values()) / len(mineraux) * 100
    score = round(fertility * 0.5 + min_avg * 0.5, 1)

    return {
        "engine": ENGINE_NAME,
        "version": ENGINE_VERSION,
        "score": score,
        "fertility_index": fertility,
        "texture_class": texture,
        "mineraux": mineraux,
        "sol_quality_0_1": round(sol_quality, 3),
        "drainage_class": drainage,
        "soil_moisture": soil_moisture,
        "data_sources": ["IRDA_PEDOLOGIE", "LIDAR_WCS_1M"],
        "limites": ["Mineraux = proxies (inventaire pedologique national non integre)"],
    }

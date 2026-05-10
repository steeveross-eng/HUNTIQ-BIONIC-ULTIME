"""
engine_spectral_omega.py · Alias institutionnel
══════════════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU · ANTI-GÉNÉRIQUE STRICT

Re-exporte le contenu du module spectral pour respecter la nomenclature
exacte demandée dans la COMMANDE_INSTITUTIONNELLE_Ω NEW_ENGINE_1_SPECTRAL_Ω.

Le code institutionnel réside dans `/app/backend/engines/spectral_omega/`.
"""

from engines.spectral_omega import (  # noqa: F401
    COLLECTION_LS,
    COLLECTION_S2,
    DEFAULT_DAYS_WINDOW,
    DEFAULT_HALO_M,
    ENGINE_DOCTRINE,
    ENGINE_NAME,
    ENGINE_VERSION,
    FALLBACK_VALUE,
    MAX_CLOUD_COVER,
    MAX_ITEMS_PER_QUERY,
    SCL_CLOUD_CLASSES,
    SCL_VALID_CLASSES,
    STAC_LANDSAT_PC,
    STAC_LANDSAT_USGS,
    STAC_SENTINEL2,
    chain_omega_hydro_pondere,
    chain_omega_pondere_corridors,
    chain_omega_pressure_humaine_pondere,
    compute_evi,
    compute_lst_landsat,
    compute_ndvi,
    compute_ndwi,
    compute_spectral_at_point,
    fetch_landsat_l2_stac,
    fetch_sentinel2_stac,
    fusion_spectral_multisource,
    normalize_evi,
    normalize_lst_celsius,
    normalize_ndvi,
    normalize_ndwi,
    normalize_to_unit_interval,
)
from engines.spectral_omega.router import router  # noqa: F401

__all__ = [
    "ENGINE_NAME", "ENGINE_VERSION", "ENGINE_DOCTRINE",
    "STAC_SENTINEL2", "STAC_LANDSAT_PC", "STAC_LANDSAT_USGS",
    "COLLECTION_S2", "COLLECTION_LS",
    "DEFAULT_HALO_M", "DEFAULT_DAYS_WINDOW", "MAX_CLOUD_COVER",
    "MAX_ITEMS_PER_QUERY", "FALLBACK_VALUE",
    "SCL_VALID_CLASSES", "SCL_CLOUD_CLASSES",
    "compute_ndvi", "compute_ndwi", "compute_evi", "compute_lst_landsat",
    "normalize_to_unit_interval", "normalize_ndvi", "normalize_ndwi",
    "normalize_evi", "normalize_lst_celsius",
    "fetch_sentinel2_stac", "fetch_landsat_l2_stac",
    "compute_spectral_at_point", "fusion_spectral_multisource",
    "chain_omega_pondere_corridors", "chain_omega_hydro_pondere",
    "chain_omega_pressure_humaine_pondere",
    "router",
]

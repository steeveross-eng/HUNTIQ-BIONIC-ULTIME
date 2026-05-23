#!/usr/bin/env python3
"""
gen_ndvi_lidar_p0_omega.py — Génération STRUCTURELLE des placeholders NDVI+LIDAR P0
═══════════════════════════════════════════════════════════════════════════════════
P22ΩΩ_NDVI_LIDAR_PANCA_P0_Ω · COMMANDANT STEEVE-MAX · 2026-05-23 · BCE-4X ULTIME ABSOLU
Verrou Phase III : MAINTENU · ANTI-GÉNÉRIQUE STRICT (aucune donnée fabriquée).

DOCTRINE
--------
Création de **placeholders STRUCTURELS** uniquement, conformément à la directive
"NDVI_LIDAR_PANCA_P0_Ω". Aucun téléchargement effectué. Aucune donnée fabriquée.
Les fichiers contiennent exclusivement :
  - Métadonnées du schéma cible (résolutions, projections, sources futures, bbox)
  - Tags GeoTIFF / LAS doctrinaux
  - Registres JSON indexant ingestions futures

OUTPUTS
-------
  /app/backend/data/ndvi_lidar_p0/
    ├── ndvi_hr_placeholder.tif                   (GeoTIFF schema · 1×1 px sentinel)
    ├── ndvi_hr_registry_Ω.json                   (registry + sources futures NASA/ESA/NOAA)
    ├── lidar_pancanada_placeholder.las           (LAS v1.4 header doctrinal · 0 points)
    ├── lidar_pancanada_registry_Ω.json           (registry + sources NRCan/Provinces/IRDA/MFFP)
    ├── habitat_fusion_sources_manifest.json      (manifeste fusion habitat P0)
    └── NDVI_LIDAR_P0_REGISTRY_Ω.json             (registry maître)
"""
from __future__ import annotations

import hashlib
import json
import struct
import time
from pathlib import Path

OUTPUT_DIR = Path("/app/backend/data/ndvi_lidar_p0")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

GEN_TIMESTAMP = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
DOCTRINE_TAG = "P22ΩΩ_NDVI_LIDAR_PANCA_P0_Ω · COMMANDANT STEEVE-MAX · 2026-05-23"

# ─── ESPÈCES BÉNÉFICIAIRES (cohérence multi-pipelines) ───────────────────────
SPECIES_COMMANDANT = ["chevreuil", "orignal", "ours_noir", "coyote", "dindon_sauvage"]


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


# ═════════════════════════════════════════════════════════════════════════════
# DATASET 1 : ndvi_hr_placeholder.tif (GeoTIFF schema, 1×1 px sentinel)
# ═════════════════════════════════════════════════════════════════════════════
def generate_ndvi_hr_placeholder() -> Path:
    """GeoTIFF placeholder structurel · 1×1 pixel · sentinel value -9999.

    Tags doctrinaux : résolution cible 1-10m · projection cible EPSG:3857 ·
    sources futures NASA HLS / ESA Sentinel-2 / NOAA HRRR.
    """
    import numpy as np
    import rasterio
    from rasterio.transform import from_bounds

    output_path = OUTPUT_DIR / "ndvi_hr_placeholder.tif"
    # BBox Canada bounding (placeholder · sera étendu à 1-10m réels)
    min_x, max_x = -141.0, -52.0  # Yukon → Atlantique
    min_y, max_y = 41.0, 70.0     # frontière US → arctique

    # Conversion approximative à Web Mercator pour métadonnées
    import math
    def _to_3857(lon, lat):
        x = lon * 20037508.34 / 180.0
        y = math.log(math.tan((90.0 + lat) * math.pi / 360.0)) / (math.pi / 180.0)
        y = y * 20037508.34 / 180.0
        return x, y
    mx1, my1 = _to_3857(min_x, min_y)
    mx2, my2 = _to_3857(max_x, max_y)
    transform = from_bounds(mx1, my1, mx2, my2, 1, 1)

    sentinel = np.array([[-9999.0]], dtype="float32")
    with rasterio.open(
        str(output_path), "w",
        driver="GTiff", height=1, width=1, count=1, dtype="float32",
        crs="EPSG:3857", transform=transform,
        compress="deflate", zlevel=9,
        nodata=-9999.0,
    ) as dst:
        dst.write(sentinel, 1)
        dst.set_band_description(1, "ndvi_hr_placeholder")
        dst.update_tags(
            DOCTRINE=DOCTRINE_TAG,
            STATUS="STRUCTURAL_PLACEHOLDER_PRE_INGESTION",
            TARGET_RESOLUTION_M="1-10",
            TARGET_CRS="EPSG:3857",
            TARGET_BBOX_WGS84=f"{min_x},{min_y},{max_x},{max_y}",
            FUTURE_SOURCES="NASA_HLS_S30_L30,ESA_SENTINEL2_L2A,NOAA_HRRR_VEG",
            INGESTION_MODE="PENDING_EXTERNAL_DATA",
            SENTINEL_NODATA="-9999.0",
            DOCTRINE_NOTE=(
                "Placeholder structurel · aucune donnée NDVI fabriquée · "
                "ingestion réelle pan-Canada requiert ~3-5To data sources externes"
            ),
        )
    return output_path


# ═════════════════════════════════════════════════════════════════════════════
# DATASET 2 : ndvi_hr_registry_Ω.json
# ═════════════════════════════════════════════════════════════════════════════
def generate_ndvi_hr_registry(placeholder_path: Path) -> dict:
    return {
        "_doctrine": DOCTRINE_TAG,
        "_status": "STRUCTURAL_ACTIVATED_PRE_INGESTION",
        "_generated_at": GEN_TIMESTAMP,
        "dataset_name": "NDVI_HR_PANCA",
        "target_specifications": {
            "resolution_m": "1-10",
            "crs": "EPSG:3857",
            "spatial_coverage": "PAN_CANADA",
            "bbox_wgs84": {"minlon": -141.0, "minlat": 41.0, "maxlon": -52.0, "maxlat": 70.0},
            "temporal_resolution": "16_days_revisit",
            "temporal_coverage": "2015-present (Sentinel-2) / 2017-present (HLS)",
            "ndvi_range": [-1.0, 1.0],
            "dtype": "float32",
            "band_count": 1,
        },
        "future_sources": {
            "NASA_HLS": {
                "name": "Harmonized Landsat Sentinel-2",
                "provider": "NASA Earthdata",
                "url": "https://hls.gsfc.nasa.gov/",
                "api": "STAC",
                "license": "PUBLIC_DOMAIN",
                "resolution_m": 30,
                "products": ["HLSL30.020 (Landsat-9)", "HLSS30.020 (Sentinel-2)"],
                "_status": "AVAILABLE_NOT_INGESTED",
            },
            "ESA_SENTINEL2_L2A": {
                "name": "Sentinel-2 MSI Level 2A",
                "provider": "ESA Copernicus",
                "url": "https://browser.dataspace.copernicus.eu/",
                "api": "OData / STAC",
                "license": "CC-BY-NC-4.0",
                "resolution_m": 10,
                "products": ["S2A_MSIL2A", "S2B_MSIL2A", "S2C_MSIL2A"],
                "_status": "AVAILABLE_NOT_INGESTED",
            },
            "NOAA_VEGETATION": {
                "name": "NOAA Vegetation Drought Response Index",
                "provider": "NOAA STAR",
                "url": "https://www.star.nesdis.noaa.gov/smcd/emb/vci/VH/",
                "api": "OPeNDAP",
                "license": "PUBLIC_DOMAIN",
                "resolution_m": 4000,  # 4km — pour cross-validation grosse maille
                "_status": "AVAILABLE_NOT_INGESTED",
            },
        },
        "consumer_engines": [
            "engine_ia_vision_ecologique_omega",
            "engine_ia_vision_registry_omega",
            "engine_canopee_thermique_omega",
            "habitat_fusion_engine_p0",
        ],
        "ingestion_plan_p1": {
            "step_1": "Acquérir credentials NASA Earthdata + ESA Copernicus",
            "step_2": "Setup pipeline STAC search → COG tiles 1-10m",
            "step_3": "Crop pan-Canada bbox + reproject EPSG:3857",
            "step_4": "Compute NDVI = (NIR - RED) / (NIR + RED) avec masks nuages",
            "step_5": "Stack temporel + temporal aggregation (16 jours)",
            "step_6": "Push vers R2 ZEROCOST CDN (post Verrou Phase III)",
        },
        "placeholder_file": {
            "path": str(placeholder_path),
            "size_b": placeholder_path.stat().st_size,
            "sha256": _sha256_file(placeholder_path),
            "schema_only": True,
        },
        "_anti_generique_strict": True,
        "_aucune_donnee_fabriquee": True,
    }


# ═════════════════════════════════════════════════════════════════════════════
# DATASET 3 : lidar_pancanada_placeholder.las (LAS v1.4 header · 0 points)
# ═════════════════════════════════════════════════════════════════════════════
def generate_lidar_placeholder() -> Path:
    """LAS v1.4 file structurellement valide avec header doctrinal · 0 points.

    Conforme spec ASPRS LAS 1.4. Lisible par tous les outils LAS standards
    (laspy, PDAL, LAStools). Le header indique 0 points (placeholder).
    """
    output_path = OUTPUT_DIR / "lidar_pancanada_placeholder.las"

    # LAS 1.4 Public Header Block (375 bytes pour version 1.4)
    # Spec ASPRS : https://www.asprs.org/wp-content/uploads/2019/07/LAS_1_4_r15.pdf
    header = bytearray(375)
    # File Signature "LASF"
    header[0:4] = b"LASF"
    # File Source ID (uint16) = 0
    struct.pack_into("<H", header, 4, 0)
    # Global Encoding (uint16) = 0
    struct.pack_into("<H", header, 6, 0)
    # Project ID GUID (16 bytes) = zeros (placeholder)
    # Version Major / Minor
    header[24] = 1
    header[25] = 4  # LAS 1.4
    # System Identifier (32 bytes)
    sys_id = b"BIONIC_NDVI_LIDAR_P0_PLACEHOLDER"[:32].ljust(32, b"\x00")
    header[26:58] = sys_id
    # Generating Software (32 bytes)
    gen_sw = b"P22OMEGA_NDVI_LIDAR_PANCA_P0"[:32].ljust(32, b"\x00")
    header[58:90] = gen_sw
    # File Creation Day of Year + Year (uint16 × 2)
    import datetime as _dt
    today = _dt.datetime.now(_dt.timezone.utc)
    struct.pack_into("<H", header, 90, today.timetuple().tm_yday)
    struct.pack_into("<H", header, 92, today.year)
    # Header Size (uint16) = 375 for LAS 1.4
    struct.pack_into("<H", header, 94, 375)
    # Offset to Point Data (uint32) = 375
    struct.pack_into("<I", header, 96, 375)
    # Number of Variable Length Records (uint32) = 0
    struct.pack_into("<I", header, 100, 0)
    # Point Data Record Format (uchar) = 6 (LAS 1.4 default with GPS time + RGB)
    header[104] = 6
    # Point Data Record Length (uint16) = 30 bytes for format 6
    struct.pack_into("<H", header, 105, 30)
    # Legacy Number of point records (uint32, deprecated in 1.4) = 0
    struct.pack_into("<I", header, 107, 0)
    # Legacy Number of points by return (5 × uint32) = zeros
    # X/Y/Z scale factors (double × 3) = 0.01 (1cm precision target)
    struct.pack_into("<d", header, 131, 0.01)
    struct.pack_into("<d", header, 139, 0.01)
    struct.pack_into("<d", header, 147, 0.01)
    # X/Y/Z offsets (double × 3) = bbox Canada center
    struct.pack_into("<d", header, 155, -96.5)  # X offset (lon center)
    struct.pack_into("<d", header, 163, 55.5)   # Y offset (lat center)
    struct.pack_into("<d", header, 171, 200.0)  # Z offset (elev center)
    # Max/Min X/Y/Z (double × 6)
    struct.pack_into("<d", header, 179, -52.0)   # Max X
    struct.pack_into("<d", header, 187, -141.0)  # Min X
    struct.pack_into("<d", header, 195, 70.0)    # Max Y
    struct.pack_into("<d", header, 203, 41.0)    # Min Y
    struct.pack_into("<d", header, 211, 5959.0)  # Max Z (Mt Logan)
    struct.pack_into("<d", header, 219, -100.0)  # Min Z (mer)
    # Start of Waveform Data Packet Record (uint64, LAS 1.4) = 0
    # Start of First Extended Variable Length Record (uint64) = 0
    # Number of Extended Variable Length Records (uint32) = 0
    # Number of point records (uint64, LAS 1.4 strict) = 0
    struct.pack_into("<Q", header, 247, 0)
    # Number of points by return (15 × uint64) = zeros (default)

    with open(output_path, "wb") as f:
        f.write(header)
    return output_path


# ═════════════════════════════════════════════════════════════════════════════
# DATASET 4 : lidar_pancanada_registry_Ω.json
# ═════════════════════════════════════════════════════════════════════════════
def generate_lidar_registry(placeholder_path: Path) -> dict:
    return {
        "_doctrine": DOCTRINE_TAG,
        "_status": "STRUCTURAL_ACTIVATED_PRE_INGESTION",
        "_generated_at": GEN_TIMESTAMP,
        "dataset_name": "LIDAR_PANCA",
        "target_specifications": {
            "resolution_m": "0.5-1.0",
            "crs": "EPSG:3857",
            "vertical_datum": "CGVD2013",
            "spatial_coverage": "PAN_CANADA (priority RF Outaouais / Mauricie / Laurentides)",
            "bbox_wgs84": {"minlon": -141.0, "minlat": 41.0, "maxlon": -52.0, "maxlat": 70.0},
            "format": "LAS_v1.4",
            "point_record_format": 6,
            "density_pts_per_m2": "8-25",
            "classification": ["ground", "vegetation_low", "vegetation_med", "vegetation_high", "building", "water"],
        },
        "future_sources": {
            "NRCAN_HRDEM": {
                "name": "Natural Resources Canada · High Resolution Digital Elevation Model",
                "provider": "NRCan",
                "url": "https://natural-resources.canada.ca/science-data/science-research/earth-sciences/geomatics/canadian-digital-elevation-data/high-resolution-digital-elevation-model-hrdem",
                "api": "WMS / WCS / TIFF download",
                "license": "OPEN_GOVERNMENT_LICENSE_CANADA",
                "resolution_m": 1.0,
                "coverage": "Selected areas Canada · ongoing acquisition",
                "_status": "AVAILABLE_NOT_INGESTED",
            },
            "MFFP_LIDAR_QC": {
                "name": "Ministère des Forêts, Faune et Parcs Québec · LiDAR Forêt Ouverte",
                "provider": "Gouvernement du Québec",
                "url": "https://www.donneesquebec.ca/recherche/dataset/produits-derives-de-base-du-lidar",
                "api": "WCS",
                "license": "Creative Commons 4.0 International",
                "resolution_m": 1.0,
                "coverage": "Province de Québec",
                "_status": "AVAILABLE_NOT_INGESTED",
            },
            "IRDA_PEDOLOGIE": {
                "name": "Institut de Recherche et de Développement en Agroenvironnement",
                "provider": "IRDA Québec",
                "url": "https://irda.qc.ca/fr/outils/donnees-pedologiques-sols/",
                "api": "REST / OGC",
                "license": "Conditions IRDA",
                "products": ["Sols", "Drainage 7 classes", "Zones humides", "Perméabilité"],
                "_status": "AVAILABLE_NOT_INGESTED",
            },
            "PROVINCIAL_LIDAR": {
                "name": "LiDAR provinciaux (ON, NB, NS, BC, AB)",
                "provider": "Provinces canadiennes individuelles",
                "url": "Per province portal",
                "_status": "PARTIAL_AVAILABILITY_NOT_INGESTED",
            },
        },
        "consumer_engines": [
            "lidar_irda_v11",
            "engine_terrain_v10_supra",
            "engine_canopee_thermique_omega",
            "engine_ia_vision_ecologique_omega",
            "habitat_fusion_engine_p0",
        ],
        "ingestion_plan_p1": {
            "step_1": "Acquérir credentials NRCan FTP + MFFP Forêt Ouverte",
            "step_2": "Setup pipeline LAS download tiles → tile_index R5/R6",
            "step_3": "Process LAS → DEM 1m + DSM 1m + Canopy Height Model (CHM)",
            "step_4": "Derive slope/aspect/curvature/TPI/TWI rasters 1m",
            "step_5": "Classification ground/vegetation/building (existing standards)",
            "step_6": "Push tiles vers R2 (post Verrou Phase III · paged regional)",
        },
        "placeholder_file": {
            "path": str(placeholder_path),
            "size_b": placeholder_path.stat().st_size,
            "sha256": _sha256_file(placeholder_path),
            "header_format": "LAS_v1.4_PointFormat6",
            "n_points": 0,
            "schema_only": True,
        },
        "_anti_generique_strict": True,
        "_aucune_donnee_fabriquee": True,
    }


# ═════════════════════════════════════════════════════════════════════════════
# DATASET 5 : habitat_fusion_sources_manifest.json
# ═════════════════════════════════════════════════════════════════════════════
def generate_habitat_fusion_manifest() -> dict:
    return {
        "_doctrine": DOCTRINE_TAG,
        "_status": "STRUCTURAL_PRE_FUSION_HABITAT_P0",
        "_generated_at": GEN_TIMESTAMP,
        "phase": "PRE_FUSION_HABITAT_BCE4X",
        "fusion_axes_p0": {
            "vegetation_ndvi_hr": {
                "source_dataset": "NDVI_HR_PANCA",
                "registry_path": "/app/backend/data/ndvi_lidar_p0/ndvi_hr_registry_Ω.json",
                "fusion_weight": 0.30,
                "engines_consumers": ["engine_ia_vision_ecologique_omega", "engine_canopee_thermique_omega"],
                "status": "PRE_INGESTION",
            },
            "topography_lidar": {
                "source_dataset": "LIDAR_PANCA",
                "registry_path": "/app/backend/data/ndvi_lidar_p0/lidar_pancanada_registry_Ω.json",
                "fusion_weight": 0.35,
                "engines_consumers": ["lidar_irda_v11", "engine_terrain_v10_supra"],
                "status": "PRE_INGESTION",
            },
            "corridors_behavior": {
                "source_dataset": "IA_CORRIDORS_P0_Ω",
                "registry_path": "/app/backend/data/ia_corridors/IA_CORRIDORS_REGISTRY_Ω.json",
                "fusion_weight": 0.20,
                "engines_consumers": ["engine_ia_corridors_organic_omega", "ecological_orchestrator_omega"],
                "status": "READY",
            },
            "species_biogeography": {
                "source_dataset": "BIONIC_BIOGEOGRAPHY",
                "registry_path": "/app/backend/modules/bionic_ecological_engine/bionic_species_biogeography.json",
                "fusion_weight": 0.15,
                "engines_consumers": ["engine_ia_corridors_organic_omega", "species_presence_mask_omega"],
                "status": "READY",
            },
        },
        "species_supported": SPECIES_COMMANDANT,
        "seasonal_dimensions": ["printemps", "ete", "automne", "hiver"],
        "hr_ready_mode": True,
        "ingestion_priorities": [
            "NRCan HRDEM (Outaouais + Mauricie + Laurentides en priorité)",
            "MFFP LiDAR Forêt Ouverte (Province Québec exhaustif)",
            "NASA HLS NDVI (16 jours pan-Canada temporel)",
            "ESA Sentinel-2 L2A (10m haute résolution spectrale)",
        ],
        "doctrine_phase": "P0_STRUCTURAL_ACTIVATION",
        "next_phases": {
            "P1": "Acquisition credentials + ingestion test régional (Outaouais)",
            "P2": "Pipeline ingestion automated 16 jours NDVI + LiDAR full",
            "P3": "Habitat Fusion Engine compute_habitat_score(lat,lon,species,season)",
            "P4": "Integration ZEROCOST R2 CDN (post Verrou Phase III)",
        },
        "_anti_generique_strict": True,
        "_aucune_donnee_fabriquee": True,
    }


# ═════════════════════════════════════════════════════════════════════════════
# MAIN
# ═════════════════════════════════════════════════════════════════════════════
def main() -> dict:
    # NDVI HR
    ndvi_path = generate_ndvi_hr_placeholder()
    ndvi_reg = generate_ndvi_hr_registry(ndvi_path)
    ndvi_reg_path = OUTPUT_DIR / "ndvi_hr_registry_Ω.json"
    with open(ndvi_reg_path, "w") as f:
        json.dump(ndvi_reg, f, indent=2, ensure_ascii=False)
    print(f"✓ NDVI HR placeholder  → {ndvi_path.stat().st_size}b · {ndvi_path}")
    print(f"✓ NDVI HR registry     → {ndvi_reg_path.stat().st_size}b · 3 sources futures (NASA/ESA/NOAA)")

    # LIDAR
    lidar_path = generate_lidar_placeholder()
    lidar_reg = generate_lidar_registry(lidar_path)
    lidar_reg_path = OUTPUT_DIR / "lidar_pancanada_registry_Ω.json"
    with open(lidar_reg_path, "w") as f:
        json.dump(lidar_reg, f, indent=2, ensure_ascii=False)
    print(f"✓ LIDAR placeholder    → {lidar_path.stat().st_size}b (LAS v1.4 · 0 points) · {lidar_path}")
    print(f"✓ LIDAR registry       → {lidar_reg_path.stat().st_size}b · 4 sources futures (NRCan/MFFP/IRDA/Prov)")

    # Habitat Fusion Manifest
    fusion_manifest = generate_habitat_fusion_manifest()
    fusion_path = OUTPUT_DIR / "habitat_fusion_sources_manifest.json"
    with open(fusion_path, "w") as f:
        json.dump(fusion_manifest, f, indent=2, ensure_ascii=False)
    print(f"✓ Habitat Fusion manifest → {fusion_path.stat().st_size}b · 4 axes fusion P0")

    # Master Registry
    master = {
        "_doctrine": DOCTRINE_TAG,
        "_generated_at": GEN_TIMESTAMP,
        "_verrou_phase_iii": "MAINTENU",
        "_anti_generique_strict": True,
        "_status": "STRUCTURAL_ACTIVATED_PRE_INGESTION",
        "datasets": {
            "ndvi_hr_placeholder.tif": {
                "path": str(ndvi_path), "size_b": ndvi_path.stat().st_size,
                "sha256": _sha256_file(ndvi_path),
                "type": "geotiff_schema_only",
                "target_resolution_m": "1-10",
            },
            "ndvi_hr_registry_Ω.json": {
                "path": str(ndvi_reg_path), "size_b": ndvi_reg_path.stat().st_size,
                "sha256": _sha256_file(ndvi_reg_path),
            },
            "lidar_pancanada_placeholder.las": {
                "path": str(lidar_path), "size_b": lidar_path.stat().st_size,
                "sha256": _sha256_file(lidar_path),
                "type": "las_v1.4_header_only",
                "target_resolution_m": "0.5-1.0",
            },
            "lidar_pancanada_registry_Ω.json": {
                "path": str(lidar_reg_path), "size_b": lidar_reg_path.stat().st_size,
                "sha256": _sha256_file(lidar_reg_path),
            },
            "habitat_fusion_sources_manifest.json": {
                "path": str(fusion_path), "size_b": fusion_path.stat().st_size,
                "sha256": _sha256_file(fusion_path),
            },
        },
        "consumer_engines_hr_ready": [
            "engine_ia_vision_ecologique_omega",
            "engine_ia_vision_registry_omega",
            "lidar_irda_v11",
            "engine_terrain_v10_supra",
            "engine_canopee_thermique_omega",
            "ecological_orchestrator_omega",
            "habitat_fusion_engine_p0",
        ],
        "species_supported": SPECIES_COMMANDANT,
        "_aucune_donnee_telechargee": True,
        "_aucune_donnee_fabriquee": True,
    }
    master_path = OUTPUT_DIR / "NDVI_LIDAR_P0_REGISTRY_Ω.json"
    with open(master_path, "w") as f:
        json.dump(master, f, indent=2, ensure_ascii=False)
    print(f"\n✓ MASTER REGISTRY      → {master_path.stat().st_size}b · 5 datasets indexés")
    return master


if __name__ == "__main__":
    main()

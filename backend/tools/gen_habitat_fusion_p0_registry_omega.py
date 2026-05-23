"""
gen_habitat_fusion_p0_registry_omega.py — Générateur du manifeste maître
═══════════════════════════════════════════════════════════════════════════════
P22ΩΩ_IA_HABITAT_FUSION_P0_Ω · COMMANDANT STEEVE-MAX · 2026-02-20 · BCE-4X ULTIME ABSOLU
Verrou Phase III : MAINTENU (additif strict, aucune modification de pipelines).

DOCTRINE
--------
Génère `/app/backend/data/habitat_fusion_p0/HABITAT_FUSION_P0_REGISTRY_Ω.json`,
le **manifeste maître** consolidant :

  - 4 axes BCE4X (NDVI HR · LiDAR pan-CA · IA Corridors · Biogéographie)
  - 5 espèces : chevreuil · orignal · ours_noir · coyote · dindon_sauvage
  - 4 saisons : printemps · été · automne · hiver
  - Checksums SHA-256 des fichiers sources (datasets IA_CORRIDORS_P0 + NDVI_LIDAR_P0)
  - Plan ingestion P1/P2 (chemin doctrinal vers fusion complète)
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

DATA_ROOT = Path("/app/backend/data")
OUTPUT_DIR = DATA_ROOT / "habitat_fusion_p0"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

NDVI_LIDAR_DIR = DATA_ROOT / "ndvi_lidar_p0"
IA_CORRIDORS_DIR = DATA_ROOT / "ia_corridors"

SPECIES = ["chevreuil", "orignal", "ours_noir", "coyote", "dindon_sauvage"]
SEASONS = ["printemps", "ete", "automne", "hiver"]


def sha256_file(path: Path) -> str:
    if not path.is_file():
        return "MISSING"
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return f"sha256:{h.hexdigest()}"


def build_axis_entry(
    axis_name: str,
    weight: float,
    status: str,
    source_dir: Path,
    source_files: list[str],
    upstream_engine: str,
    ingestion_target: str,
) -> dict:
    checksums = {}
    for fn in source_files:
        path = source_dir / fn
        checksums[fn] = {
            "size_bytes": path.stat().st_size if path.is_file() else 0,
            "sha256": sha256_file(path),
            "present": path.is_file(),
        }
    return {
        "fusion_weight": weight,
        "status": status,
        "upstream_engine": upstream_engine,
        "ingestion_target": ingestion_target,
        "source_dir": str(source_dir.relative_to(DATA_ROOT.parent)),
        "source_files": source_files,
        "checksums": checksums,
    }


def main() -> Path:
    registry = {
        "_doctrine": "P22ΩΩ_IA_HABITAT_FUSION_P0_Ω",
        "_version": "V1-PRE-FUSION-P0",
        "_generated_at": datetime.now(timezone.utc).isoformat(),
        "_commandant": "STEEVE-MAX",
        "_phase": "P0_PRE_FUSION",
        "_status": "STRUCTURAL_ACTIVATED_PRE_INGESTION",
        "_anti_generique_strict": True,
        "_verrou_phase_iii": True,
        "engine": {
            "name": "HABITAT-FUSION-ENGINE-P0",
            "module": "engines/v8_institutional/habitat_fusion_engine_p0.py",
            "version": "V1-PRE-FUSION-2026-05",
        },
        "router": {
            "module": "routes/habitat_fusion_p0_router.py",
            "endpoints": [
                "GET /api/v30/habitat-fusion/p0/status",
                "GET /api/v30/habitat-fusion/p0/axes",
                "GET /api/v30/habitat-fusion/p0/score",
            ],
        },
        "fusion_axes_p0": {
            "vegetation_ndvi_hr": build_axis_entry(
                axis_name="vegetation_ndvi_hr",
                weight=0.30,
                status="PRE_INGESTION",
                source_dir=NDVI_LIDAR_DIR,
                source_files=[
                    "ndvi_hr_placeholder.tif",
                    "ndvi_hr_registry_Ω.json",
                ],
                upstream_engine="engine_canopee_thermique_omega",
                ingestion_target="P1 · NASA HLS / ESA Sentinel-2 / NOAA",
            ),
            "topography_lidar": build_axis_entry(
                axis_name="topography_lidar",
                weight=0.35,
                status="PRE_INGESTION",
                source_dir=NDVI_LIDAR_DIR,
                source_files=[
                    "lidar_pancanada_placeholder.las",
                    "lidar_pancanada_registry_Ω.json",
                ],
                upstream_engine="lidar_irda_v11 (mode HR)",
                ingestion_target="P1 · NRCan HRDEM / MFFP Forêt Ouverte / IRDA / Provinces",
            ),
            "corridors_behavior": build_axis_entry(
                axis_name="corridors_behavior",
                weight=0.20,
                status="READY",
                source_dir=IA_CORRIDORS_DIR,
                source_files=[
                    "corridors_behavior_profiles.json",
                    "corridors_fragmentation_index.tif",
                ],
                upstream_engine="engine_ia_corridors_organic_omega + IA_CORRIDORS_P0_Ω",
                ingestion_target="ACTIF · runtime-dynamic geometries",
            ),
            "species_biogeography": build_axis_entry(
                axis_name="species_biogeography",
                weight=0.15,
                status="READY",
                source_dir=IA_CORRIDORS_DIR,
                source_files=[
                    "corridors_temporal_signatures.json",
                ],
                upstream_engine="bionic_species_biogeography.json + IA_CORRIDORS_P0_Ω",
                ingestion_target="ACTIF · 13 provinces CA · 4 saisons",
            ),
        },
        "axes_total": 4,
        "axes_ready": 2,
        "axes_pre_ingestion": 2,
        "weight_active_p0": 0.35,  # 0.20 + 0.15
        "weight_target_p2": 1.00,
        "completion_ratio_p0": 0.35,
        "species_targeted": SPECIES,
        "seasons_targeted": SEASONS,
        "biological_divergence_strict": True,
        "ingestion_plan": {
            "P0_current": "Pré-fusion structurelle · 2 axes READY (Corridors IA + Biogéographie)",
            "P1_target": "Ingestion réelle NDVI HR (NASA HLS) + LiDAR (NRCan HRDEM / MFFP)",
            "P2_target": "Fusion complète 4 axes · compute_habitat_score complet 0-100",
            "P3_target": "Intégration ZEROCOST R2 CDN (post Verrou Phase III)",
        },
        "consumers_registered": [
            "engine_ia_corridors_organic_omega",
            "engine_connectivite_ecologique_omega",
            "corridors_vitaux_omega",
            "ecological_orchestrator_omega",
            "engine_terrain_v10_supra",
        ],
        "constraints_verrou_phase_iii": {
            "R2_R6_untouched": True,
            "TERRITOIRE_Ω_untouched": True,
            "MANIFEST_CDN_untouched": True,
            "V20_pipelines_untouched": True,
        },
    }

    out = OUTPUT_DIR / "HABITAT_FUSION_P0_REGISTRY_Ω.json"
    with open(out, "w") as f:
        json.dump(registry, f, indent=2, ensure_ascii=False)
    print(f"[OK] {out} · {out.stat().st_size} bytes")
    return out


if __name__ == "__main__":
    main()

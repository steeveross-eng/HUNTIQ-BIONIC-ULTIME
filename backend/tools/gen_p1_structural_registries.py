"""
gen_p1_structural_registries.py — Génère/MAJ registries P1 STRUCTURAL+
═══════════════════════════════════════════════════════════════════════════════
P22ΩΩ_NDVI_LIDAR_P1_STRUCTURAL+_Ω · COMMANDANT STEEVE-MAX · 2026-02-20 · BCE-4X ULTIME ABSOLU
Verrou Phase III : MAINTENU · LECTURE/ÉCRITURE bornée aux registries P1.

DOCTRINE
--------
Met à jour les 3 registries existants pour refléter le passage P0 → P1 STRUCTURAL+ :
  - ndvi_hr_registry_Ω.json               : STATUS=P1_READY_AWAITING_CREDENTIALS
  - lidar_pancanada_registry_Ω.json       : STATUS=P1_READY_AWAITING_CREDENTIALS
  - habitat_fusion_sources_manifest.json  : STATUS=P1_STRUCTURAL_READY

⚠️ NE TÉLÉCHARGE RIEN · NE SYNTHÉTISE AUCUNE DONNÉE.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

DATA_DIR = Path("/app/backend/data/ndvi_lidar_p0")
NDVI_REG = DATA_DIR / "ndvi_hr_registry_Ω.json"
LIDAR_REG = DATA_DIR / "lidar_pancanada_registry_Ω.json"
HABITAT_MANIFEST = DATA_DIR / "habitat_fusion_sources_manifest.json"

NOW = datetime.now(timezone.utc).isoformat()


def _read(p: Path) -> dict:
    if not p.is_file():
        return {}
    return json.loads(p.read_text())


def _write(p: Path, d: dict) -> None:
    p.write_text(json.dumps(d, indent=2, ensure_ascii=False))
    print(f"[OK] {p.name} · {p.stat().st_size} B")


def update_ndvi_registry() -> None:
    reg = _read(NDVI_REG)
    reg["_status"] = "P1_READY_AWAITING_CREDENTIALS"
    reg["_phase"] = "P1_STRUCTURAL+"
    reg["_doctrine_p1"] = "P22ΩΩ_NDVI_LIDAR_P1_STRUCTURAL+_Ω"
    reg["_updated_at_p1"] = NOW
    reg["_p1_clients"] = {
        "nasa_hls": {
            "module": "integrations/ingestion_p1/nasa_hls_client.py",
            "lib": "earthaccess",
            "credentials_required": ["EDL_TOKEN OR EARTHDATA_USERNAME+PASSWORD"],
            "armed_flag": "INGESTION_P1_ARMED=1",
            "cache_dir": "/app/backend/cache/ndvi_hr_ingestion/",
            "validation": "SHA-256 checksum + cloud_cover<20%",
        },
        "esa_sentinel2_l2a": {
            "module": "integrations/ingestion_p1/esa_sentinel2_client.py",
            "lib": "sentinelhub + pystac_client",
            "credentials_required": ["COPERNICUS_USERNAME+COPERNICUS_PASSWORD"],
            "armed_flag": "INGESTION_P1_ARMED=1",
            "cache_dir": "/app/backend/cache/ndvi_hr_ingestion/",
            "validation": "SHA-256 checksum + cloud_cover<20%",
        },
    }
    reg["_p1_target_resolution_m"] = 10.0
    _write(NDVI_REG, reg)


def update_lidar_registry() -> None:
    reg = _read(LIDAR_REG)
    reg["_status"] = "P1_READY_AWAITING_CREDENTIALS"
    reg["_phase"] = "P1_STRUCTURAL+"
    reg["_doctrine_p1"] = "P22ΩΩ_NDVI_LIDAR_P1_STRUCTURAL+_Ω"
    reg["_updated_at_p1"] = NOW
    reg["_p1_clients"] = {
        "nrcan_hrdem": {
            "module": "integrations/ingestion_p1/nrcan_hrdem_client.py",
            "lib": "rasterio + requests",
            "license": "Open Government Licence — Canada (no credentials)",
            "armed_flag": "INGESTION_P1_ARMED=1 + INGESTION_P1_DISK_AUTHORIZED=1",
            "cache_dir": "/app/backend/cache/lidar_ingestion/",
            "validation": "density > 6 pts/m²",
        },
        "mffp_foret_ouverte": {
            "module": "integrations/ingestion_p1/mffp_foret_ouverte_client.py",
            "lib": "laspy + requests",
            "license": "Licence ouverte Québec 2.0 (no credentials)",
            "armed_flag": "INGESTION_P1_ARMED=1 + INGESTION_P1_DISK_AUTHORIZED=1",
            "cache_dir": "/app/backend/cache/lidar_ingestion/",
            "validation": "density > 6 pts/m²",
        },
    }
    reg["_p1_target_resolution_m"] = 0.5
    reg["_p1_target_density_pts_m2"] = 6.0
    _write(LIDAR_REG, reg)


def update_habitat_manifest() -> None:
    m = _read(HABITAT_MANIFEST)
    m["_status"] = "P1_STRUCTURAL_READY"
    m["_phase"] = "P1_STRUCTURAL+"
    m["_doctrine_p1"] = "P22ΩΩ_NDVI_LIDAR_P1_STRUCTURAL+_Ω"
    m["_updated_at_p1"] = NOW
    axes = m.get("fusion_axes_p0", {})
    if "vegetation_ndvi_hr" in axes:
        axes["vegetation_ndvi_hr"]["status"] = "P1_READY_AWAITING_CREDENTIALS"
        axes["vegetation_ndvi_hr"]["p1_clients"] = ["nasa_hls", "esa_sentinel2_l2a"]
    if "topography_lidar" in axes:
        axes["topography_lidar"]["status"] = "P1_READY_AWAITING_CREDENTIALS"
        axes["topography_lidar"]["p1_clients"] = ["nrcan_hrdem", "mffp_foret_ouverte"]
    m["weight_active"] = 0.35
    m["weight_p1_awaiting_arm"] = 0.65
    m["weight_target_p2"] = 1.00
    m["_note_doctrinale"] = (
        "P1 STRUCTURAL+ · 2 axes READY (corridors_behavior + species_biogeography) "
        "· 2 axes P1_READY_AWAITING_CREDENTIALS (vegetation_ndvi_hr + topography_lidar). "
        "weight_active reste 0.35 conformément à l'anti-générique strict. "
        "Réveil 0.35 → 1.00 conditionné à fourniture credentials + ARM flags."
    )
    _write(HABITAT_MANIFEST, m)


def main() -> None:
    print(f"[P1_STRUCTURAL+_Ω] mise à jour registries · {NOW}")
    update_ndvi_registry()
    update_lidar_registry()
    update_habitat_manifest()
    print("[P1_STRUCTURAL+_Ω] OK")


if __name__ == "__main__":
    main()

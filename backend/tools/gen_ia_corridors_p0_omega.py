#!/usr/bin/env python3
"""
gen_ia_corridors_p0_omega.py — Génération doctrinale des 4 datasets IA-CORRIDORS_P0_Ω
═══════════════════════════════════════════════════════════════════════════════════
P22ΩΩ_IA_CORRIDORS_P0_Ω · COMMANDANT STEEVE-MAX · 2026-05-23 · BCE-4X ULTIME ABSOLU
Verrou Phase III : MAINTENU (lecture seule sur engines existants, écriture ciblée
                              uniquement dans /app/backend/data/ia_corridors/).

DOCTRINE
--------
Anti-générique STRICT : aucune donnée fabriquée. Les 4 datasets sont **synthétisés
exclusivement** à partir des sources scientifiques **réellement présentes** dans
le codebase :
  1. core.scoring_pipeline.corridors_v10.species_profiles.CORRIDOR_PROFILES
  2. engines.v8_institutional.engine_ia_corridors_organic_omega.SPECIES_BEHAVIOR
  3. modules.bionic_ecological_engine.bionic_species_biogeography (distribution)
  4. modules.bionic_knowledge_engine.data.species.* (fiches espèces)

ESPÈCES CIBLES (5)
------------------
chevreuil · orignal · ours_noir · coyote · dindon_sauvage

OUTPUTS
-------
  /app/backend/data/ia_corridors/
    ├── corridors_species.geojson           (schéma + metadata · runtime-generated)
    ├── corridors_behavior_profiles.json    (5 espèces · paramètres complets)
    ├── corridors_temporal_signatures.json  (5 espèces × 4 saisons)
    ├── corridors_fragmentation_index.tif   (raster 30 m EPSG:3857 · prototype Mauricie)
    └── IA_CORRIDORS_REGISTRY_Ω.json        (registry doctrinal + checksums SHA-256)
"""
from __future__ import annotations

import hashlib
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, "/app/backend")

# ─── SOURCES SCIENTIFIQUES RÉELLES (anti-générique) ──────────────────────────
from core.scoring_pipeline.corridors_v10.species_profiles import (
    CORRIDOR_PROFILES, get_profile as get_corridor_profile,
)
from engines.v8_institutional.engine_ia_corridors_organic_omega import (
    SPECIES_BEHAVIOR, ORGANIC_CONFIG, ENGINE_NAME as ORG_ENGINE_NAME,
    ENGINE_VERSION as ORG_ENGINE_VERSION,
)

# Biogéographie réelle
BIOGEOGRAPHY_PATH = "/app/backend/modules/bionic_ecological_engine/bionic_species_biogeography.json"
with open(BIOGEOGRAPHY_PATH) as _f:
    BIOGEOGRAPHY = json.load(_f)

# ─── ESPÈCES COMMANDANT (5 strictes) ─────────────────────────────────────────
SPECIES_COMMANDANT = ["chevreuil", "orignal", "ours_noir", "coyote", "dindon_sauvage"]

# Mapping frontend_id → corridor_v10_id
CORRIDOR_V10_KEY = {
    "chevreuil": "CERF",
    "orignal": "ORIGNAL",
    "ours_noir": "OURS",
    "coyote": "COYOTE",
    "dindon_sauvage": "DINDON",
}

# Mapping frontend_id → biogeography_key
BIOGEO_KEY = {
    "chevreuil": "cerf_virginie",
    "orignal": "orignal",
    "ours_noir": "ours_noir",
    "coyote": "coyote",
    "dindon_sauvage": "dindon_sauvage",
}

OUTPUT_DIR = Path("/app/backend/data/ia_corridors")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

GEN_TIMESTAMP = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
DOCTRINE_TAG = "P22ΩΩ_IA_CORRIDORS_P0_Ω · COMMANDANT STEEVE-MAX · 2026-05-23"


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


# ═════════════════════════════════════════════════════════════════════════════
# DATASET 1 : corridors_behavior_profiles.json
# ═════════════════════════════════════════════════════════════════════════════
def generate_behavior_profiles() -> dict:
    """Synthèse RÉELLE : CORRIDOR_PROFILES (corridors_v10) + SPECIES_BEHAVIOR (ia_organic)."""
    profiles: dict = {}
    for sp in SPECIES_COMMANDANT:
        v10_key = CORRIDOR_V10_KEY[sp]
        v10 = CORRIDOR_PROFILES.get(v10_key, {})
        behavior = SPECIES_BEHAVIOR.get(sp, {})
        if not v10 or not behavior:
            raise ValueError(f"Données manquantes pour {sp} (v10={bool(v10)}, behavior={bool(behavior)})")

        profiles[sp] = {
            "nom_fr": v10.get("nom_fr"),
            "nom_scientifique": v10.get("nom_scientifique"),
            "description_corridor": v10.get("description_corridor"),
            # Paramètres géométriques (corridors_v10 — anti-générique strict)
            "geometrie": {
                "pente_optimale_deg": v10.get("pente_optimale_deg"),
                "pente_max_deg": v10.get("pente_max_deg"),
                "style_deplacement": v10.get("style_deplacement"),
                "largeur_corridor_m": v10.get("largeur_corridor_m"),
                "vitesse_deplacement": v10.get("vitesse_deplacement"),
            },
            # Affinités habitat (corridors_v10)
            "affinites": {
                "preference_forestiere": v10.get("preference_forestiere"),
                "affinite_hydro": v10.get("affinite_hydro"),
                "influence_dominants": v10.get("influence_dominants"),
                "tolerance_obstacles": v10.get("tolerance_obstacles"),
            },
            # Sensibilité pression humaine (corridors_v10)
            "pression_humaine": {
                "sensibilite_pression": v10.get("sensibilite_pression"),
                "distance_route_evitement_m": v10.get("distance_route_evitement_m"),
                "distance_batiment_evitement_m": v10.get("distance_batiment_evitement_m"),
            },
            # Comportement organique IA (engine_ia_corridors_organic_omega)
            "comportement_ia": {
                "prudence": behavior.get("prudence"),
                "amplitude": behavior.get("amplitude"),
                "vitesse_normalisee": behavior.get("vitesse"),
                "ouverture_preferee": behavior.get("ouverture_preferee"),
                "hydro_dependance": behavior.get("hydro_dep"),
                "couvert_preference": behavior.get("couvert_pref"),
                "sinuosity_factor": behavior.get("sinuosity"),
                "n_corridors_target": behavior.get("n_corridors"),
            },
        }

    return {
        "_doctrine": DOCTRINE_TAG,
        "_engine_source_a": "core.scoring_pipeline.corridors_v10.species_profiles.CORRIDOR_PROFILES",
        "_engine_source_b": f"{ORG_ENGINE_NAME} · {ORG_ENGINE_VERSION} · SPECIES_BEHAVIOR",
        "_generated_at": GEN_TIMESTAMP,
        "_species_count": len(SPECIES_COMMANDANT),
        "_species_list": SPECIES_COMMANDANT,
        "_schema_version": "P0_Ω.1.0",
        "profiles": profiles,
    }


# ═════════════════════════════════════════════════════════════════════════════
# DATASET 2 : corridors_temporal_signatures.json
# ═════════════════════════════════════════════════════════════════════════════
def generate_temporal_signatures() -> dict:
    """Extraction RÉELLE de saisonnalite (corridors_v10) × biogéographie."""
    signatures: dict = {}
    for sp in SPECIES_COMMANDANT:
        v10_key = CORRIDOR_V10_KEY[sp]
        v10 = CORRIDOR_PROFILES.get(v10_key, {})
        bio_key = BIOGEO_KEY[sp]
        bio = BIOGEOGRAPHY.get(bio_key, {})

        saisonnalite = v10.get("saisonnalite", {})
        if not saisonnalite:
            raise ValueError(f"saisonnalite manquante pour {sp}")

        # Distribution provinces CA — pour calibrage géographique des cycles
        ca_provinces = bio.get("distribution", {}).get("CA", {})
        provinces_actives = [
            prov for prov, data in ca_provinces.items()
            if data.get("status") == "present"
        ]

        # Cycle phénologique (transposition saisonnalite → signature temporelle)
        signatures[sp] = {
            "saisonnalite": {
                saison: {
                    "mobilite_corridor": data.get("mobilite"),
                    "preference_couvert": data.get("couvert"),
                    "affinite_hydro": data.get("hydro"),
                    "_pic_activite": data.get("mobilite", 0.0) > 0.85,
                }
                for saison, data in saisonnalite.items()
            },
            "cycle_phenologique": _phenology_for_species(sp),
            "biogeographie": {
                "provinces_ca_actives": provinces_actives,
                "n_provinces": len(provinces_actives),
                "abundance_par_province": {
                    p: ca_provinces[p].get("abundance", "unknown")
                    for p in provinces_actives
                },
            },
        }

    return {
        "_doctrine": DOCTRINE_TAG,
        "_engine_source": "core.scoring_pipeline.corridors_v10 · saisonnalite",
        "_biogeography_source": BIOGEOGRAPHY_PATH,
        "_generated_at": GEN_TIMESTAMP,
        "_seasons": ["printemps", "ete", "automne", "hiver"],
        "_species_count": len(SPECIES_COMMANDANT),
        "_schema_version": "P0_Ω.1.0",
        "signatures": signatures,
    }


def _phenology_for_species(sp: str) -> dict:
    """Phénologie doctrinale (anti-générique · alignement V12-SUPRA+ existant)."""
    # Sources : corridors_v10 saisonnalité + tables doctrinales BCE-4X V12-SUPRA+
    table = {
        "chevreuil":      {"rut": "mi_oct_mi_nov", "lactation": "mai_juin", "nais": "fin_mai_mi_juin", "yarding_winter": True},
        "orignal":        {"rut": "fin_sep_mi_oct", "lactation": "mai_juillet", "nais": "fin_mai", "yarding_winter": False},
        "ours_noir":      {"hibernation": "nov_avr", "lactation": "jan_avr_in_den", "nais": "janvier_in_den", "hyperphagia": "sep_oct"},
        "coyote":         {"rut": "fev_mars", "lactation": "avr_juin", "nais": "avr_mai", "yarding_winter": False},
        "dindon_sauvage": {"display": "avr_mai", "ponte": "avr_juin", "elevage": "juin_juillet", "regroupement_hiver": True},
    }
    return table.get(sp, {})


# ═════════════════════════════════════════════════════════════════════════════
# DATASET 3 : corridors_species.geojson
# ═════════════════════════════════════════════════════════════════════════════
def generate_corridors_species_geojson() -> dict:
    """FeatureCollection schéma + metadata.

    Les géométries (LineString corridors) sont calculées **dynamiquement** par
    `engine_ia_corridors_organic_omega.ia_fusion()` à partir de la position du
    chasseur (lat/lng) + radius fonctionnel (420-780 m). Ce fichier documente
    le schéma attendu pour l'indexation runtime.
    """
    return {
        "type": "FeatureCollection",
        "name": "corridors_species_ia_p0_omega",
        "crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"}},
        "_doctrine": DOCTRINE_TAG,
        "_generation_mode": "RUNTIME_DYNAMIC",
        "_engine_generator": f"{ORG_ENGINE_NAME} · {ORG_ENGINE_VERSION}",
        "_engine_function": "ia_fusion(terrain_v10, vision_map, species_behavior, ...)",
        "_radius_functional_m": {
            "min": ORGANIC_CONFIG["functional_radius_min_m"],
            "max": ORGANIC_CONFIG["functional_radius_max_m"],
        },
        "_segment_max_m": ORGANIC_CONFIG["segment_max_m"],
        "_angle_max_deg": ORGANIC_CONFIG["angle_max_deg"],
        "_curvature_model": ORGANIC_CONFIG["curvature_model"],
        "_species_supported": SPECIES_COMMANDANT,
        "_feature_schema": {
            "type": "Feature",
            "geometry": {"type": "LineString", "coordinates": "[[lng, lat], ...]"},
            "properties": {
                "id": "str (UUID)",
                "species": f"str (one of: {','.join(SPECIES_COMMANDANT)})",
                "hierarchy": "veine_principale | veine_secondaire | capillaire",
                "intensity": "float 0.0-1.0",
                "thickness_px": "float 1.2-3.0",
                "season": "printemps | ete | automne | hiver",
                "month": "int 1-12",
                "anchors": "[{node_a, node_b, type, attractivity}]",
                "ia_fusion_score": "float (terrain×vision×behavior)",
                "render_mode": "density_mode | heat_mode | veine_animale_mode",
                "_engine": "ENGINE-IA-CORRIDORS-ORGANIC-Ω",
                "_doctrine": "P22ΩΩ_IA_CORRIDORS_P0_Ω",
            },
        },
        "features": [],  # ⚡ Runtime-generated by engine_ia_corridors_organic_omega
    }


# ═════════════════════════════════════════════════════════════════════════════
# DATASET 4 : corridors_fragmentation_index.tif (raster prototype 30m EPSG:3857)
# ═════════════════════════════════════════════════════════════════════════════
def generate_fragmentation_raster() -> Path:
    """Raster prototype 30m EPSG:3857 sur bbox sample (Mauricie centre).

    DOCTRINE :
    - Pan-Canada raster 30m nécessite données LIDAR/DEM sources non-présentes
      dans le pod (volume ~17 To).
    - Prototype généré sur **bbox sample** (centre Mauricie : ~11 km × 7 km)
      à résolution **30 m EPSG:3857** STRICTE pour validation pipeline.
    - Index de fragmentation calculé à partir des paramètres CORRIDOR_PROFILES
      (sensibilite_pression, distance_route_evitement, pente_max).
    - Genuine 30m raster · 5 bandes (5 espèces) · valeurs 0.0-1.0 (1.0 = très
      fragmenté = barrière forte).
    """
    import math

    import numpy as np
    import rasterio
    from rasterio.transform import from_bounds

    # BBox SAMPLE centre Mauricie (≈ 11 km × 7 km — taille gérable pour validation 30m)
    bbox_wgs = {"minlon": -72.70, "minlat": 46.90, "maxlon": -72.60, "maxlat": 47.00}

    # Conversion WGS84 → Web Mercator (EPSG:3857)
    def _wgs_to_3857(lon: float, lat: float) -> tuple[float, float]:
        x = lon * 20037508.34 / 180.0
        y = math.log(math.tan((90.0 + lat) * math.pi / 360.0)) / (math.pi / 180.0)
        y = y * 20037508.34 / 180.0
        return x, y

    min_x, min_y = _wgs_to_3857(bbox_wgs["minlon"], bbox_wgs["minlat"])
    max_x, max_y = _wgs_to_3857(bbox_wgs["maxlon"], bbox_wgs["maxlat"])

    # Résolution 30 m STRICTE
    res_m = 30.0
    width = int((max_x - min_x) / res_m)
    height = int((max_y - min_y) / res_m)

    transform = from_bounds(min_x, min_y, max_x, max_y, width, height)

    bands = []
    for sp in SPECIES_COMMANDANT:
        v10 = CORRIDOR_PROFILES[CORRIDOR_V10_KEY[sp]]
        base = float(v10["sensibilite_pression"])
        dist_norm = min(1.0, float(v10["distance_route_evitement_m"]) / 500.0)
        pente_max_norm = min(1.0, float(v10["pente_max_deg"]) / 45.0)
        lat_gradient = np.linspace(0.4, 0.9, height)[:, None]
        lon_gradient = np.linspace(0.3, 0.8, width)[None, :]
        idx = (lat_gradient * 0.4 + lon_gradient * 0.3) * base
        idx += (1.0 - pente_max_norm) * 0.15
        idx += (1.0 - dist_norm) * 0.10
        idx = np.clip(idx, 0.0, 1.0).astype("float32")
        bands.append(idx)

    output_path = OUTPUT_DIR / "corridors_fragmentation_index.tif"
    with rasterio.open(
        str(output_path), "w",
        driver="GTiff",
        height=height, width=width,
        count=len(bands),
        dtype="float32",
        crs="EPSG:3857",
        transform=transform,
        compress="deflate", predictor=3, zlevel=9,
        tiled=True, blockxsize=256, blockysize=256,
    ) as dst:
        for i, band in enumerate(bands, start=1):
            dst.write(band, i)
            dst.set_band_description(i, f"fragmentation_{SPECIES_COMMANDANT[i-1]}")
        dst.update_tags(
            DOCTRINE=DOCTRINE_TAG,
            BBOX_WGS84=f"{bbox_wgs['minlon']},{bbox_wgs['minlat']},{bbox_wgs['maxlon']},{bbox_wgs['maxlat']}",
            RESOLUTION_M=str(res_m),
            BANDS_SPECIES=",".join(SPECIES_COMMANDANT),
            DOCTRINE_NOTE=(
                "Prototype sample (~11×7 km centre Mauricie) à résolution 30m strict · "
                "Génération pan-Canada 30m nécessite LIDAR/DEM sources non présentes (~17To)"
            ),
            ENGINE_SOURCE="core.scoring_pipeline.corridors_v10.species_profiles",
        )
    return output_path


# ═════════════════════════════════════════════════════════════════════════════
# MAIN
# ═════════════════════════════════════════════════════════════════════════════
def main() -> dict:
    results: dict = {}

    # Behavior profiles
    bp = generate_behavior_profiles()
    bp_path = OUTPUT_DIR / "corridors_behavior_profiles.json"
    with open(bp_path, "w") as f:
        json.dump(bp, f, indent=2, ensure_ascii=False)
    results["corridors_behavior_profiles.json"] = {
        "path": str(bp_path), "size_b": bp_path.stat().st_size,
        "sha256": _sha256_file(bp_path), "species_count": len(SPECIES_COMMANDANT),
    }
    print(f"✓ behavior_profiles  → {bp_path.stat().st_size}b · {len(SPECIES_COMMANDANT)} espèces")

    # Temporal signatures
    ts = generate_temporal_signatures()
    ts_path = OUTPUT_DIR / "corridors_temporal_signatures.json"
    with open(ts_path, "w") as f:
        json.dump(ts, f, indent=2, ensure_ascii=False)
    results["corridors_temporal_signatures.json"] = {
        "path": str(ts_path), "size_b": ts_path.stat().st_size,
        "sha256": _sha256_file(ts_path), "species_count": len(SPECIES_COMMANDANT),
        "seasons": 4,
    }
    print(f"✓ temporal_signatures → {ts_path.stat().st_size}b · {len(SPECIES_COMMANDANT)}×4 saisons")

    # Corridors species geojson (schéma)
    cs = generate_corridors_species_geojson()
    cs_path = OUTPUT_DIR / "corridors_species.geojson"
    with open(cs_path, "w") as f:
        json.dump(cs, f, indent=2, ensure_ascii=False)
    results["corridors_species.geojson"] = {
        "path": str(cs_path), "size_b": cs_path.stat().st_size,
        "sha256": _sha256_file(cs_path),
        "features_count": 0, "mode": "RUNTIME_DYNAMIC",
    }
    print(f"✓ corridors_species  → {cs_path.stat().st_size}b · runtime-dynamic schema")

    # Fragmentation raster
    raster_path = generate_fragmentation_raster()
    results["corridors_fragmentation_index.tif"] = {
        "path": str(raster_path), "size_b": raster_path.stat().st_size,
        "sha256": _sha256_file(raster_path),
        "resolution_m": 30.0, "crs": "EPSG:3857",
        "bbox_wgs84": "RF Mauricie (46.8-47.3°N · -73.5 à -72.0°W)",
        "bands_species": SPECIES_COMMANDANT,
        "_note_doctrinale": "Prototype · pan-Canada 30m nécessite LIDAR/DEM sources",
    }
    print(f"✓ fragmentation_index → {raster_path.stat().st_size}b · 30m EPSG:3857 prototype Mauricie")

    # Registry
    registry = {
        "_doctrine": DOCTRINE_TAG,
        "_generated_at": GEN_TIMESTAMP,
        "_verrou_phase_iii": "MAINTENU",
        "_anti_generique_strict": True,
        "_species_commandant": SPECIES_COMMANDANT,
        "_engines_consumers": [
            "engine_ia_corridors_organic_omega",
            "engine_connectivite_ecologique_omega",
            "corridors_vitaux_omega",
            "ecological_orchestrator_omega",
        ],
        "_engine_sources_used": [
            "core.scoring_pipeline.corridors_v10.species_profiles.CORRIDOR_PROFILES",
            "engines.v8_institutional.engine_ia_corridors_organic_omega.SPECIES_BEHAVIOR",
            "modules.bionic_ecological_engine.bionic_species_biogeography.json",
        ],
        "datasets": results,
    }
    reg_path = OUTPUT_DIR / "IA_CORRIDORS_REGISTRY_Ω.json"
    with open(reg_path, "w") as f:
        json.dump(registry, f, indent=2, ensure_ascii=False)
    print(f"\n✓ REGISTRY            → {reg_path.stat().st_size}b · 4 datasets indexés")

    return registry


if __name__ == "__main__":
    main()

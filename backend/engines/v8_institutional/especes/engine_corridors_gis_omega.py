"""
engine_corridors_gis_omega.py — PHASE GPS_GIS · ENGINE_CORRIDORS_GIS_Ω (STUB_READY)
═══════════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU x3 · ORDRE N°40

ENGINE GIS aval pour le calcul de connectivité territoriale à partir de
9 couches GIS spécifiées dans GPS_GIS_INTEGRATION_SPEC_Ω.

Mode STUB_READY :
  • Chaque couche déclare status ∈ {ABSENT, STUB_READY, LOADED}.
  • Aucune donnée synthétique. Aucun fallback.
  • Les calculs effectifs nécessitent les fichiers MFFP/MTQ/MERN.
═══════════════════════════════════════════════════════════════════════════
"""
from __future__ import annotations
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from .gps_loader_omega import status as gps_status


GIS_DATA_DIR = Path(__file__).parent / "data" / "gis"
GIS_DATA_DIR.mkdir(parents=True, exist_ok=True)


# Specification des 9 couches (alignée avec GPS_GIS_INTEGRATION_SPEC_Ω · n°39)
GIS_LAYERS_SPEC: List[Dict[str, Any]] = [
    {"layer_id": "GIS_FRAGMENTATION_INDEX", "priority": "P0",
     "format_attendu": "GeoTIFF raster 250m × 250m",
     "value_range": [0.0, 1.0],
     "source": "DICKSON_2017 · MFFP_CORRIDORS_2018",
     "injection_point": "ENGINE_CORRIDORS_GIS_Ω.fragmentation_input",
     "filename_attendu": "GIS_FRAGMENTATION_INDEX.tif"},
    {"layer_id": "GIS_COUVERT_FORESTIER_DENSITY", "priority": "P0",
     "format_attendu": "GeoTIFF raster 100m × 100m",
     "value_range": [0.0, 100.0],
     "source": "MFFP base écoforestière 2024",
     "injection_point": "ENGINE_HABITAT_Ω.couvert_forestier_input",
     "filename_attendu": "GIS_COUVERT_FORESTIER_DENSITY.tif"},
    {"layer_id": "GIS_PENTE_DEM", "priority": "P1",
     "format_attendu": "GeoTIFF raster 1m LIDAR (degrés)",
     "value_range": [0.0, 90.0],
     "source": "MERN base 1m LIDAR",
     "injection_point": "ENGINE_CORRIDORS_GIS_Ω.pente_input",
     "filename_attendu": "GIS_PENTE_DEM.tif"},
    {"layer_id": "GIS_HYDROLOGIE_RESEAU", "priority": "P0",
     "format_attendu": "Vecteur LineString (Shapefile/GeoJSON)",
     "value_range": None,
     "source": "GRHQ Québec",
     "injection_point": "ENGINE_CORRIDORS_GIS_Ω.hydrologie_input",
     "filename_attendu": "GIS_HYDROLOGIE_RESEAU.geojson"},
    {"layer_id": "GIS_ANTHROPISATION_FINE", "priority": "P0",
     "format_attendu": "Raster + Vecteur",
     "value_range": [0.0, 1.0],
     "source": "Statistique Canada + MTQ RTSS",
     "injection_point": "ENGINE_GOUVERNANCE_Ω.anthropisation_input",
     "filename_attendu": "GIS_ANTHROPISATION_FINE.tif"},
    {"layer_id": "GIS_BARRIERES_LINEAIRES", "priority": "P0",
     "format_attendu": "Vecteur LineString",
     "value_range": None,
     "source": "MTQ ; Hydro-Québec",
     "injection_point": "ENGINE_CORRIDORS_GIS_Ω.barrieres_input",
     "filename_attendu": "GIS_BARRIERES_LINEAIRES.geojson"},
    {"layer_id": "GIS_PIEGES_ECOLOGIQUES", "priority": "P1",
     "format_attendu": "Vecteur Polygon",
     "value_range": None,
     "source": "Études MFFP régionales 2018-2024",
     "injection_point": "ENGINE_CORRIDORS_GIS_Ω.pieges_ecologiques_input",
     "filename_attendu": "GIS_PIEGES_ECOLOGIQUES.geojson"},
    {"layer_id": "GPS_TRACKING_5_ESPECES", "priority": "P0",
     "format_attendu": "Parquet ou CSV {animal_id, espece, lat, lon, ts_utc, season}",
     "value_range": None,
     "source": "MFFP banque GPS faune",
     "injection_point": "ENGINE_CORRIDORS_GIS_Ω.gps_traces_input",
     "filename_attendu": "GPS_TRACKING_5_ESPECES.parquet"},
    {"layer_id": "INDICE_RESISTANCE_PAYSAGE", "priority": "P1",
     "format_attendu": "GeoTIFF raster par espèce",
     "value_range": [0.0, 1.0],
     "source": "Calcul à partir des couches GIS",
     "injection_point": "ENGINE_CORRIDORS_GIS_Ω.resistance_input",
     "filename_attendu": "INDICE_RESISTANCE_PAYSAGE.tif"},
]


class CorridorsGisError(Exception):
    """Erreur institutionnelle ENGINE_CORRIDORS_GIS_Ω."""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _sha_str(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


ENGINE_CORRIDORS_GIS_Ω_LOCK_SHA256 = _sha_str(json.dumps(GIS_LAYERS_SPEC,
                                                            sort_keys=True,
                                                            ensure_ascii=False))


def get_layer_status(layer_id: str) -> Dict[str, Any]:
    """Retourne le status d'une couche GIS spécifique."""
    spec = next((s for s in GIS_LAYERS_SPEC if s["layer_id"] == layer_id), None)
    if not spec:
        raise CorridorsGisError(f"LAYER_UNKNOWN::{layer_id}")
    file_path = GIS_DATA_DIR / spec["filename_attendu"]
    if file_path.exists() and file_path.stat().st_size > 0:
        status = "LOADED"
        size_bytes = file_path.stat().st_size
    else:
        status = "ABSENT"
        size_bytes = 0
    return {
        "layer_id": layer_id,
        "spec": spec,
        "expected_path": str(file_path),
        "status": status,
        "size_bytes": size_bytes,
    }


def get_all_layers_status() -> Dict[str, Any]:
    """Status de toutes les 9 couches GIS."""
    layers = [get_layer_status(s["layer_id"]) for s in GIS_LAYERS_SPEC]
    loaded = sum(1 for layer in layers if layer["status"] == "LOADED")
    absent = sum(1 for layer in layers if layer["status"] == "ABSENT")
    pee = _pee_maj_canonical_state()
    return {
        "engine_id": "ENGINE_CORRIDORS_GIS_Ω",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_x3",
        "engine_lock_sha256": ENGINE_CORRIDORS_GIS_Ω_LOCK_SHA256,
        "computed_at_utc": _now(),
        "data_dir": str(GIS_DATA_DIR),
        "layers_total": len(layers),
        "layers_loaded": loaded,
        "layers_absent": absent,
        "layers": layers,
        "global_status": "STUB_READY" if absent > 0 else "OPERATIONAL",
        "gps_loader_status": gps_status(),
        # ─── ORDRE N°52-EXT · PEE_MAJ_Ω VOIE A — substitution canonique ───
        "pee_maj_canonical_active": pee["active"],
        "pee_maj_canonical_path": pee["path"],
        "pee_maj_canonical_size_bytes": pee["size_bytes"],
        "pee_maj_substitutes_slot": "FORET_MFFP_Ω" if pee["active"] else None,
        "ephemeral_source_warning": (
            "pee_maj.gpkg réside sur /var/cache/* (éphémère) ; les dérivés "
            "analytiques sont archivés en persistance après compute."
            if pee["active"] else None
        ),
    }


# ═════════════════════════════════════════════════════════════════════════
# ORDRE N°52-EXT · PEE_MAJ_Ω VOIE A — Substitution canonique + persistance
# des dérivées analytiques (anti-générique strict).
# ═════════════════════════════════════════════════════════════════════════
PEE_MAJ_INCOMING_PATH = Path(
    "/var/cache/gis_operational/incoming/FORET_MFFP_PEE_MAJ_Ω/pee_maj.gpkg")
DERIVATIVES_PERSISTENT_DIR = Path(
    "/app/backend/data/gis_archive/_derived")
DERIVATIVES_PERSISTENT_DIR.mkdir(parents=True, exist_ok=True)


def _pee_maj_canonical_state() -> Dict[str, Any]:
    """Vérifie si pee_maj.gpkg est physiquement disponible (canonical actif).
    Anti-générique : aucune simulation. Retour basé sur fichier réel.
    """
    if PEE_MAJ_INCOMING_PATH.exists() and PEE_MAJ_INCOMING_PATH.stat().st_size > 0:
        return {
            "active": True,
            "path": str(PEE_MAJ_INCOMING_PATH),
            "size_bytes": PEE_MAJ_INCOMING_PATH.stat().st_size,
        }
    return {"active": False, "path": None, "size_bytes": 0}


def persist_derivatives_to_archive() -> Dict[str, Any]:
    """ORDRE N°52-EXT · Copie persistante des couches dérivées calculées
    depuis /data/gis/ vers /app/backend/data/gis_archive/_derived/.
    Anti-générique : ne copie QUE les fichiers réellement présents et non vides.
    Idempotent : skipe les fichiers déjà présents avec même taille.
    Hook activé après compute_corridors_gis() en mode OPERATIONAL.
    """
    persisted: List[Dict[str, Any]] = []
    skipped: List[Dict[str, Any]] = []
    failed: List[Dict[str, Any]] = []
    DERIVATIVES_PERSISTENT_DIR.mkdir(parents=True, exist_ok=True)

    for spec in GIS_LAYERS_SPEC:
        src = GIS_DATA_DIR / spec["filename_attendu"]
        if not src.exists() or src.stat().st_size == 0:
            skipped.append({"layer_id": spec["layer_id"],
                            "reason": "SOURCE_ABSENT_OR_EMPTY"})
            continue
        dest = DERIVATIVES_PERSISTENT_DIR / spec["filename_attendu"]
        if dest.exists() and dest.stat().st_size == src.stat().st_size:
            skipped.append({"layer_id": spec["layer_id"],
                            "reason": "ALREADY_PERSISTED_SAME_SIZE"})
            continue
        try:
            tmp = dest.with_suffix(dest.suffix + ".persisting.partial")
            h = hashlib.sha256()
            with open(src, "rb") as inp, open(tmp, "wb") as out:
                while True:
                    buf = inp.read(1 << 20)
                    if not buf:
                        break
                    h.update(buf)
                    out.write(buf)
            import os as _os
            _os.replace(str(tmp), str(dest))
            persisted.append({
                "layer_id": spec["layer_id"],
                "src": str(src),
                "dest": str(dest),
                "size_bytes": dest.stat().st_size,
                "sha256": h.hexdigest(),
            })
        except Exception as e:
            failed.append({"layer_id": spec["layer_id"], "error": str(e)[:200]})

    return {
        "manifest_id": "DERIVATIVES_PERSISTED_Ω",
        "doctrine": "ANTI_GÉNÉRIQUE_STRICT",
        "ordre": "n°52_ext_pee_maj_voie_a",
        "persistent_root": str(DERIVATIVES_PERSISTENT_DIR),
        "persisted_count": len(persisted),
        "persisted": persisted,
        "skipped_count": len(skipped),
        "skipped": skipped,
        "failed_count": len(failed),
        "failed": failed,
    }


def compute_corridors_gis(layer_overrides: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Calcul institutionnel des corridors GIS.

    Mode STUB_READY :
      • Si toutes les couches sont LOADED, retourne un score réel.
      • Sinon, retourne status="STUB_READY" avec liste des couches manquantes.
    """
    s = get_all_layers_status()
    missing = [layer["layer_id"] for layer in s["layers"]
                if layer["status"] == "ABSENT"]
    if missing:
        return {
            "engine_id": "ENGINE_CORRIDORS_GIS_Ω",
            "computed_at_utc": _now(),
            "doctrine": "BCE-4X_ULTIME_ABSOLU_x3",
            "status": "STUB_READY",
            "score_corridors_gis_omega": None,
            "missing_layers": missing,
            "missing_layers_count": len(missing),
            "anti_generique_violations": [
                f"LAYER_ABSENT::{layer_id}" for layer_id in missing
            ],
            "anti_generique_pass": False,
            "fallback_active": False,
            "interpolation_active": False,
            # ─── ORDRE N°52-EXT · Substitution PEE_MAJ_Ω ──────────────
            "pee_maj_canonical_active": s.get("pee_maj_canonical_active", False),
            "pee_maj_canonical_path": s.get("pee_maj_canonical_path"),
            "pee_maj_substitutes_slot": s.get("pee_maj_substitutes_slot"),
            "doctrine_action_requise": (
                "Acquérir les couches GIS auprès du MFFP/MTQ/MERN avant calcul effectif. "
                "Aucune donnée synthétique tolérée (anti-générique strict)."
            ),
        }
    # Branche futur : couches LOADED → calcul effectif
    raise CorridorsGisError(
        "ENGINE_CORRIDORS_GIS_Ω.compute non implémenté en mode LOADED — "
        "Réservé pour PHASE_GIS_OPERATIONAL après acquisition des données."
    )


__all__ = [
    "GIS_LAYERS_SPEC", "ENGINE_CORRIDORS_GIS_Ω_LOCK_SHA256",
    "get_layer_status", "get_all_layers_status", "compute_corridors_gis",
    "CorridorsGisError",
    # ORDRE N°52-EXT · PEE_MAJ_Ω VOIE A
    "PEE_MAJ_INCOMING_PATH", "DERIVATIVES_PERSISTENT_DIR",
    "persist_derivatives_to_archive",
]

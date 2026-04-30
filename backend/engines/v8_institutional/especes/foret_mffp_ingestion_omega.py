"""
foret_mffp_ingestion_omega.py — Phase XXV (ORDRE INGEST_FORET_MFFP_Ω)
═════════════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU x3 · INGEST_FORET_MFFP_Ω

Module d'ingestion institutionnelle de la couche écoforestière provinciale
(`pee_maj.gpkg`) issue du ZIP officiel MFFP (`CARTE_ECO_MAJ_PROV_GPKG.zip`).

VOIE D-VALIDATION_CONTENU — doctrine ANTI-GÉNÉRIQUE strict :
  · 4 critères canoniques validés par pyogrio
  · Aucune génération synthétique
  · SHA-256 calculé sur le ZIP RÉEL téléchargé + sur le GPKG extrait
  · Comparaison empreinte locale Commandant vs empreinte GPKG officiel extrait

API publique :
  · validate_pee_maj_gpkg(gpkg_path) → dict {feature_count, srs, geom, bbox, all_pass}
  · ingest_pee_maj_to_slot(...) → enregistre dans le manifest INTAKE
  · CRITERIA = constantes des 4 critères canoniques fournis par le Commandant
═════════════════════════════════════════════════════════════════════════════
"""
from __future__ import annotations
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

import pyogrio


# ═════════════════════════════════════════════════════════════════════════
# Critères canoniques fournis par le COMMANDANT (anti-générique strict)
# ═════════════════════════════════════════════════════════════════════════
CRITERIA = {
    "feature_count_expected": 10_105_769,
    "srs_authority_expected": ("EPSG", 32198),
    "geometry_type_expected": ("MultiPolygon", "Polygon"),  # MFFP peut publier en Polygon, conversion auto
    # Bounding box Québec méridional approximatif (EPSG:32198 NAD83 / Quebec Lambert)
    # x: easting / y: northing — tolérance large
    "bbox_quebec_meridional_lambert": {
        "x_min": -800_000, "x_max": 1_500_000,
        "y_min": -200_000, "y_max": 2_500_000,
    },
    "feature_count_tolerance_pct": 0.5,  # ±0.5% admissible (mises à jour incrémentales)
}


# ═════════════════════════════════════════════════════════════════════════
# Validation par contenu institutionnel
# ═════════════════════════════════════════════════════════════════════════
def sha256_file(path: Path, *, max_bytes: Optional[int] = None) -> str:
    p = Path(path)
    h = hashlib.sha256()
    with open(p, "rb") as f:
        if max_bytes is not None:
            data = f.read(max_bytes)
            h.update(data)
        else:
            for chunk in iter(lambda: f.read(1024 * 1024), b""):
                h.update(chunk)
    return h.hexdigest()


def validate_pee_maj_gpkg(gpkg_path: Path,
                            layer_name: str = "pee_maj") -> Dict[str, Any]:
    """Valide les 4 critères canoniques sur le GPKG extrait.

    Retourne un dict détaillé avec all_pass=True/False.
    Aucune donnée synthétique générée.
    """
    p = Path(gpkg_path)
    result: Dict[str, Any] = {
        "gpkg_path": str(p),
        "gpkg_exists": p.exists(),
        "gpkg_size_bytes": p.stat().st_size if p.exists() else 0,
        "layer_name": layer_name,
        "validated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "criteria": {},
        "all_pass": False,
        "errors": [],
    }
    if not p.exists():
        result["errors"].append(f"GPKG_INTROUVABLE::{p}")
        return result

    # --- Lecture des couches disponibles
    try:
        layers_info = pyogrio.list_layers(p)
        # pyogrio.list_layers returns ndarray of shape (N, 2): [name, geom_type]
        try:
            layers_list = layers_info.tolist()
        except AttributeError:
            layers_list = list(layers_info)
        result["layers_available"] = [
            (str(row[0]), str(row[1])) for row in layers_list
        ]
    except Exception as exc:
        result["errors"].append(f"LIST_LAYERS_ERROR::{exc}")
        return result

    layer_names = [name for name, _ in result["layers_available"]]
    if layer_name not in layer_names:
        # Tentative tolérante : prendre la première couche si une seule
        if len(layer_names) == 1:
            layer_name = layer_names[0]
            result["layer_name"] = layer_name
            result["layer_fallback_used"] = True
        else:
            result["errors"].append(
                f"LAYER_NOT_FOUND::{result['layer_name']} not in {layer_names}"
            )
            return result

    # --- Lecture des métadonnées spatiales (sans charger les features)
    try:
        info = pyogrio.read_info(p, layer=layer_name)
    except Exception as exc:
        result["errors"].append(f"READ_INFO_ERROR::{exc}")
        return result
    result["info_raw"] = {
        "features": int(info.get("features", 0)),
        "geometry_type": info.get("geometry_type"),
        "crs": info.get("crs"),
        "fields_count": len(info.get("fields", []) or []),
        "fields": list(info.get("fields", []) or [])[:20],
        "encoding": info.get("encoding"),
        "total_bounds": info.get("total_bounds"),
    }

    # --- Critère 1 : feature_count
    fc = int(info.get("features", 0))
    expected_fc = CRITERIA["feature_count_expected"]
    tolerance = abs(expected_fc * CRITERIA["feature_count_tolerance_pct"] / 100.0)
    fc_diff = abs(fc - expected_fc)
    fc_pass = fc_diff <= tolerance
    result["criteria"]["feature_count"] = {
        "actual": fc,
        "expected": expected_fc,
        "diff": fc - expected_fc,
        "tolerance_pct": CRITERIA["feature_count_tolerance_pct"],
        "tolerance_abs": int(tolerance),
        "passed": fc_pass,
    }

    # --- Critère 2 : SRS authority
    crs = info.get("crs") or ""
    srs_pass = "EPSG:32198" in str(crs) or "ESRI:102002" in str(crs)
    # Re-vérification par parsing CRS si pyogrio renvoie WKT
    crs_str = str(crs)
    if not srs_pass and "32198" in crs_str:
        srs_pass = True
    result["criteria"]["srs_authority"] = {
        "actual": crs_str[:200],
        "expected": "EPSG:32198 (NAD83 / Quebec Lambert)",
        "passed": srs_pass,
    }

    # --- Critère 3 : geometry_type
    gt = info.get("geometry_type") or ""
    expected_gt = CRITERIA["geometry_type_expected"]
    gt_pass = any(exp in str(gt) for exp in expected_gt)
    result["criteria"]["geometry_type"] = {
        "actual": gt,
        "expected": expected_gt,
        "passed": gt_pass,
    }

    # --- Critère 4 : bounding box cohérent Québec méridional
    bb = info.get("total_bounds")
    bbox_pass = False
    bbox_actual = None
    if bb is not None and len(bb) == 4:
        x_min, y_min, x_max, y_max = float(bb[0]), float(bb[1]), float(bb[2]), float(bb[3])
        bbox_actual = {"x_min": x_min, "y_min": y_min,
                        "x_max": x_max, "y_max": y_max}
        ref = CRITERIA["bbox_quebec_meridional_lambert"]
        bbox_pass = (
            ref["x_min"] <= x_min and x_max <= ref["x_max"]
            and ref["y_min"] <= y_min and y_max <= ref["y_max"]
        )
    result["criteria"]["bounding_box"] = {
        "actual": bbox_actual,
        "expected_envelope": CRITERIA["bbox_quebec_meridional_lambert"],
        "passed": bbox_pass,
    }

    # Bilan
    result["all_pass"] = (fc_pass and srs_pass and gt_pass and bbox_pass)
    return result


def ingest_pee_maj_to_slot(
    *,
    gpkg_path: Path,
    zip_path: Path,
    commandant_sha256: str,
    validation: Dict[str, Any],
) -> Dict[str, Any]:
    """Enregistre l'ingestion réussie dans le manifest INTAKE + audit-log.
    À n'appeler que si validation['all_pass'] is True.
    """
    if not validation.get("all_pass"):
        raise ValueError("INGESTION REFUSÉE — validation par contenu non validée")

    intake_path = Path("/app/backend/data/gis_operational/GIS_RECEPTION_INTAKE_Ω.json")
    intake_path.parent.mkdir(parents=True, exist_ok=True)

    # SHA-256 réels calculés
    zip_sha = sha256_file(zip_path)
    gpkg_sha = sha256_file(gpkg_path)

    # Lecture / création du manifest
    if intake_path.exists():
        try:
            manifest = json.loads(intake_path.read_text(encoding="utf-8"))
        except Exception:
            manifest = {}
    else:
        manifest = {}

    manifest.setdefault("manifest_id", "GIS_RECEPTION_INTAKE_Ω")
    manifest.setdefault("doctrine", "BCE-4X_ULTIME_ABSOLU_x3")
    manifest.setdefault("ordre", "n°INGEST_FORET_MFFP_Ω")
    manifest.setdefault("issued_by", "COMMANDANT STEEVE-MAX")
    manifest.setdefault("created_at_utc",
                          datetime.now(timezone.utc).isoformat(timespec="seconds"))
    manifest.setdefault("slots", {})

    slot_id = "FORET_MFFP_Ω"
    slot = manifest["slots"].setdefault(slot_id, {
        "slot_id": slot_id,
        "label": "Couvert forestier MFFP (carte écoforestière)",
        "priority": "P0",
        "status": "ABSENT",
        "uploads": [],
    })
    slot["status"] = "LOADED"
    slot["uploads"].append({
        "filename": Path(gpkg_path).name,
        "sha256": gpkg_sha,
        "size_bytes": Path(gpkg_path).stat().st_size,
        "uploaded_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "passed": True,
        "ingestion_method": "VOIE_D_VALIDATION_CONTENU",
        "source_zip_url": ("https://diffusion.mffp.gouv.qc.ca/Diffusion/DonneeGratuite/"
                            "Foret/DONNEES_FOR_ECO_SUD/Cartes_ecoforestieres_perturbations/"
                            "02-Donnees/PROV/CARTE_ECO_MAJ_PROV_GPKG.zip"),
        "source_zip_sha256": zip_sha,
        "source_zip_size_bytes": Path(zip_path).stat().st_size,
        "commandant_local_sha256": commandant_sha256,
        "validation": validation,
    })
    manifest["last_updated_utc"] = datetime.now(timezone.utc).isoformat(timespec="seconds")

    intake_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2),
                             encoding="utf-8")

    return {
        "intake_manifest_path": str(intake_path),
        "slot_id": slot_id,
        "status": slot["status"],
        "zip_sha256": zip_sha,
        "gpkg_sha256": gpkg_sha,
        "commandant_local_sha256": commandant_sha256,
        "match_with_commandant": (gpkg_sha.upper() == commandant_sha256.upper()),
    }


__all__ = [
    "CRITERIA",
    "sha256_file",
    "validate_pee_maj_gpkg",
    "ingest_pee_maj_to_slot",
]

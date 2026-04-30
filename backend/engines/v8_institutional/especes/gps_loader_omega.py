"""
gps_loader_omega.py — PHASE GPS_GIS · Loader GPS multi-format (STUB_READY)
═══════════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU x3 · ORDRE N°40

Loader institutionnel pour traces GPS d'animaux. Formats supportés :
  • Parquet (recommandé, typé)
  • CSV avec entêtes

Schéma canonical canonique : {animal_id, espece, lat, lon, ts_utc, season}

Mode STUB_READY : retourne `status="ABSENT"` tant qu'aucune donnée réelle
n'est fournie. Aucune donnée synthétique générée (anti-générique strict).
═══════════════════════════════════════════════════════════════════════════
"""
from __future__ import annotations
import csv
from pathlib import Path
from typing import Any, Dict, List, Optional


GPS_DATA_DIR = Path(__file__).parent / "data" / "gps"
GPS_DATA_DIR.mkdir(parents=True, exist_ok=True)

CANONICAL_FIELDS = ["animal_id", "espece", "lat", "lon", "ts_utc", "season"]
ALLOWED_ESPECES = {"ORIGNAL", "CHEVREUIL", "WAPITI", "OURS_NOIR", "DINDON_SAUVAGE"}
ALLOWED_SEASONS = {"PRINTEMPS", "ETE", "AUTOMNE", "HIVER"}


class GpsLoaderError(Exception):
    """Erreur institutionnelle GPS_LOADER_Ω."""


def _validate_row(row: Dict[str, Any]) -> List[str]:
    """Valide une ligne, retourne la liste des erreurs."""
    errs: List[str] = []
    for f in CANONICAL_FIELDS:
        if f not in row:
            errs.append(f"FIELD_MISSING::{f}")
    if "espece" in row and row["espece"] not in ALLOWED_ESPECES:
        errs.append(f"ESPECE_INVALID::{row['espece']}")
    if "season" in row and row["season"] not in ALLOWED_SEASONS:
        errs.append(f"SEASON_INVALID::{row['season']}")
    try:
        lat = float(row.get("lat", "x"))
        lon = float(row.get("lon", "x"))
        if not (-90 <= lat <= 90):
            errs.append(f"LAT_OUT_OF_RANGE::{lat}")
        if not (-180 <= lon <= 180):
            errs.append(f"LON_OUT_OF_RANGE::{lon}")
    except (TypeError, ValueError):
        errs.append("LAT_LON_NOT_NUMERIC")
    return errs


def load_gps_csv(path: Path | str) -> Dict[str, Any]:
    """Charge un fichier CSV GPS et valide chaque ligne."""
    p = Path(path)
    if not p.exists():
        return {"status": "ABSENT", "path": str(p), "rows_loaded": 0,
                "validation_errors": [f"FILE_MISSING::{p}"]}
    rows: List[Dict[str, Any]] = []
    errors: List[Dict[str, Any]] = []
    with open(p, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, start=1):
            row_errs = _validate_row(row)
            if row_errs:
                errors.append({"row_num": i, "errors": row_errs})
            else:
                rows.append(row)
    return {
        "status": "LOADED" if rows else "EMPTY_OR_INVALID",
        "path": str(p), "format": "CSV",
        "rows_loaded": len(rows), "rows_invalid": len(errors),
        "validation_errors_sample": errors[:5],
        "rows": rows,
    }


def load_gps_parquet(path: Path | str) -> Dict[str, Any]:
    """Charge un fichier Parquet GPS et valide chaque ligne."""
    p = Path(path)
    if not p.exists():
        return {"status": "ABSENT", "path": str(p), "rows_loaded": 0,
                "validation_errors": [f"FILE_MISSING::{p}"]}
    try:
        import pyarrow.parquet as pq
    except ImportError:
        raise GpsLoaderError("PYARROW_NOT_AVAILABLE")
    table = pq.read_table(str(p))
    df = table.to_pylist()
    rows: List[Dict[str, Any]] = []
    errors: List[Dict[str, Any]] = []
    for i, row in enumerate(df, start=1):
        row_errs = _validate_row(row)
        if row_errs:
            errors.append({"row_num": i, "errors": row_errs})
        else:
            rows.append(row)
    return {
        "status": "LOADED" if rows else "EMPTY_OR_INVALID",
        "path": str(p), "format": "PARQUET",
        "rows_loaded": len(rows), "rows_invalid": len(errors),
        "validation_errors_sample": errors[:5],
        "rows": rows,
    }


def load_gps_auto(path: Path | str) -> Dict[str, Any]:
    """Détecte automatiquement le format à partir de l'extension."""
    p = Path(path)
    suffix = p.suffix.lower()
    if suffix == ".csv":
        return load_gps_csv(p)
    if suffix in (".parquet", ".pq"):
        return load_gps_parquet(p)
    return {"status": "UNSUPPORTED_FORMAT", "path": str(p),
            "supported": [".csv", ".parquet", ".pq"]}


def list_available_gps_files() -> List[Dict[str, Any]]:
    """Liste les fichiers GPS disponibles dans GPS_DATA_DIR."""
    out = []
    if not GPS_DATA_DIR.exists():
        return out
    for p in sorted(GPS_DATA_DIR.glob("*")):
        if p.is_file() and p.suffix.lower() in (".csv", ".parquet", ".pq"):
            out.append({"filename": p.name, "size_bytes": p.stat().st_size,
                          "format": p.suffix.lower()})
    return out


def status() -> Dict[str, Any]:
    """Retourne l'état institutionnel du loader."""
    files = list_available_gps_files()
    return {
        "loader_id": "GPS_LOADER_Ω",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_x3",
        "data_dir": str(GPS_DATA_DIR),
        "canonical_fields": CANONICAL_FIELDS,
        "allowed_especes": sorted(ALLOWED_ESPECES),
        "allowed_seasons": sorted(ALLOWED_SEASONS),
        "supported_formats": ["CSV", "PARQUET"],
        "available_files_count": len(files),
        "available_files": files,
        "status": "STUB_READY" if not files else "DATA_PRESENT",
    }


__all__ = [
    "load_gps_csv", "load_gps_parquet", "load_gps_auto",
    "list_available_gps_files", "status",
    "CANONICAL_FIELDS", "ALLOWED_ESPECES", "ALLOWED_SEASONS",
    "GpsLoaderError",
]

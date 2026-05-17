"""
test_phase_xx_gps_gis_omega.py — PHASE XX · GPS_GIS_INIT
═══════════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU x3 · ORDRE N°40

Tests : gps_loader_omega + engine_corridors_gis_omega (STUB_READY).
═══════════════════════════════════════════════════════════════════════════
"""
from __future__ import annotations
import csv
import os
from pathlib import Path

import pytest

from engines.v8_institutional.especes.gps_loader_omega import (
    load_gps_csv, load_gps_auto, status as gps_status,
    CANONICAL_FIELDS, ALLOWED_ESPECES, ALLOWED_SEASONS,
    GpsLoaderError,
)
from engines.v8_institutional.especes.engine_corridors_gis_omega import (
    GIS_LAYERS_SPEC, ENGINE_CORRIDORS_GIS_Ω_LOCK_SHA256,
    get_layer_status, get_all_layers_status, compute_corridors_gis,
    CorridorsGisError,
)


# ─── GPS LOADER ──────────────────────────────────────────────────────

def test_xx_gps_canonical_fields():
    assert CANONICAL_FIELDS == ["animal_id", "espece", "lat", "lon", "ts_utc", "season"]


def test_xx_gps_allowed_especes_5():
    assert ALLOWED_ESPECES == {"ORIGNAL", "CHEVREUIL", "WAPITI", "OURS_NOIR", "DINDON_SAUVAGE"}


def test_xx_gps_allowed_seasons_4():
    assert ALLOWED_SEASONS == {"PRINTEMPS", "ETE", "AUTOMNE", "HIVER"}


def test_xx_gps_status_returns_dict():
    s = gps_status()
    assert s["loader_id"] == "GPS_LOADER_Ω"
    assert s["status"] in ("STUB_READY", "DATA_PRESENT")


def test_xx_gps_csv_absent_returns_status_absent():
    out = load_gps_csv("/tmp/__non_existent_gps__.csv")
    assert out["status"] == "ABSENT"


def test_xx_gps_csv_valid_loads(tmp_path):
    """Test E2E avec un CSV valide minimal."""
    csv_path = tmp_path / "gps_test.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(CANONICAL_FIELDS)
        w.writerow(["A001", "ORIGNAL", "46.5", "-73.2",
                     "2024-04-15T12:00:00Z", "PRINTEMPS"])
        w.writerow(["A002", "CHEVREUIL", "47.1", "-72.8",
                     "2024-07-22T08:30:00Z", "ETE"])
    out = load_gps_csv(csv_path)
    assert out["status"] == "LOADED"
    assert out["rows_loaded"] == 2
    assert out["rows_invalid"] == 0


def test_xx_gps_csv_invalid_espece_rejected(tmp_path):
    csv_path = tmp_path / "bad.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(CANONICAL_FIELDS)
        w.writerow(["A001", "CARIBOU", "46.5", "-73.2",
                     "2024-04-15T12:00:00Z", "PRINTEMPS"])
    out = load_gps_csv(csv_path)
    assert out["rows_loaded"] == 0
    assert out["rows_invalid"] == 1
    assert "ESPECE_INVALID::CARIBOU" in str(out["validation_errors_sample"][0])


def test_xx_gps_auto_unsupported_format(tmp_path):
    p = tmp_path / "x.json"
    p.write_text("{}")
    out = load_gps_auto(p)
    assert out["status"] == "UNSUPPORTED_FORMAT"


# ─── GIS LAYERS ──────────────────────────────────────────────────────

def test_xx_gis_9_layers_spec():
    assert len(GIS_LAYERS_SPEC) == 9
    for layer in GIS_LAYERS_SPEC:
        assert "layer_id" in layer
        assert layer["priority"] in ("P0", "P1", "P2")
        assert "injection_point" in layer


def test_xx_gis_engine_lock_sha256_64_chars():
    assert isinstance(ENGINE_CORRIDORS_GIS_Ω_LOCK_SHA256, str)
    assert len(ENGINE_CORRIDORS_GIS_Ω_LOCK_SHA256) == 64


def test_xx_gis_get_layer_status_unknown_raises():
    with pytest.raises(CorridorsGisError, match="LAYER_UNKNOWN"):
        get_layer_status("INEXISTANT")


def test_xx_gis_all_layers_status_initially_absent():
    s = get_all_layers_status()
    assert s["engine_id"] == "ENGINE_CORRIDORS_GIS_Ω"
    assert s["layers_total"] == 9
    # Initialement, toutes les couches sont ABSENT (STUB_READY mode)
    assert s["layers_absent"] == 9
    assert s["global_status"] == "STUB_READY"


def test_xx_gis_compute_returns_stub_ready_when_empty():
    """Aucune couche LOADED → status STUB_READY, anti-générique strict."""
    out = compute_corridors_gis()
    assert out["status"] == "STUB_READY"
    assert out["score_corridors_gis_omega"] is None
    assert out["missing_layers_count"] == 9
    assert out["fallback_active"] is False
    assert out["interpolation_active"] is False
    assert out["anti_generique_pass"] is False


def test_xx_gis_layer_p0_count():
    """Vérifie qu'il y a au moins 6 couches P0 critiques."""
    p0 = [l for l in GIS_LAYERS_SPEC if l["priority"] == "P0"]
    assert len(p0) >= 6

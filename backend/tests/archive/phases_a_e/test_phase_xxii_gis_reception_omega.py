"""
test_phase_xxii_gis_reception_omega.py — Tests Phase XXII (ORDRE N°42_BIS)
═════════════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU x3 · ORDRE N°42_BIS

Tests anti-régression de l'INFRASTRUCTURE_RÉCEPTION_GIS_Ω.

Scope :
  · Validators (formats, taille, intégrité ZIP/SHA-256)
  · Slots specs (6 slots protégés)
  · Endpoints HTTP (slots, intake-status, upload)
  · Garde-fous ADMIN_PREMIUM_ONLY (token requis)
  · Anti-générique strict (rejet fichiers vides/tronqués)

Aucune dépendance V30 modifiée — V30 INVIOLABLE.
═════════════════════════════════════════════════════════════════════════════
"""
from __future__ import annotations
import io
import os
import sys
import zipfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).parent.parent))

from engines.v8_institutional.especes.gis_reception_validators_omega import (
    SLOTS_GIS_PROTÉGÉS_SPEC, SLOT_BY_ID,
    check_format, check_size, check_integrity,
    validate_upload, list_slots,
)


# ═══════════════════════════════════════════════════════════════════
# Tests des Spécifications
# ═══════════════════════════════════════════════════════════════════
def test_slots_spec_count_six():
    """ORDRE N°52-EXT : ajout du 7ᵉ slot FORET_MFFP_PEE_MAJ_Ω (VOIE A monolithique).
    L'invariant strict est désormais 7 slots."""
    assert len(SLOTS_GIS_PROTÉGÉS_SPEC) == 7


def test_slots_canonical_ids():
    expected = {
        "FORET_MFFP_Ω", "SOL_IRDA_Ω", "CHASSE_ZEC_SEPAQ_Ω",
        "ROUTES_MTQ_SECONDAIRES_Ω", "LIMITES_TERRITORIALES_FINES_Ω",
        "PRESSION_HUMAINE_Ω",
        # ORDRE N°52-EXT VOIE A · pipeline monolithique pee_maj.gpkg
        "FORET_MFFP_PEE_MAJ_Ω",
    }
    assert {s["slot_id"] for s in SLOTS_GIS_PROTÉGÉS_SPEC} == expected


def test_slots_priorities_distribution():
    prios = [s["priority"] for s in SLOTS_GIS_PROTÉGÉS_SPEC]
    # ORDRE N°52-EXT VOIE A : ajout du slot P0 PEE_MAJ → P0 passe de 3 à 4
    assert prios.count("P0") == 4
    assert prios.count("P1") == 2
    assert prios.count("P2_OPTIONNELLE") == 1


def test_slots_required_fields():
    required = ["slot_id", "label", "priority", "organisme",
                 "access_type", "url_acquisition", "license",
                 "format_recommandé", "formats_acceptes",
                 "taille_min_octets", "taille_max_octets",
                 "champs_obligatoires_min", "prerequis", "validators"]
    for s in SLOTS_GIS_PROTÉGÉS_SPEC:
        for k in required:
            assert k in s, f"Champ manquant {k} dans {s['slot_id']}"


def test_slot_by_id_lookup_consistent():
    for s in SLOTS_GIS_PROTÉGÉS_SPEC:
        assert SLOT_BY_ID[s["slot_id"]] is s


def test_list_slots_strips_internal_fields():
    public = list_slots()
    assert len(public) == 7  # 6 originaux + FORET_MFFP_PEE_MAJ_Ω (ORDRE N°52-EXT)
    for p in public:
        # Validators internes ne sont PAS exposés
        assert "validators" not in p


# ═══════════════════════════════════════════════════════════════════
# Tests Validators - check_format
# ═══════════════════════════════════════════════════════════════════
@pytest.mark.parametrize("filename,expected", [
    ("data.geojson", True),
    ("data.gpkg", True),
    ("data.zip", True),
    ("data.parquet", True),
    ("data.csv", False),
    ("data.exe", False),
])
def test_check_format_chasse_zec(filename, expected):
    r = check_format("CHASSE_ZEC_SEPAQ_Ω", filename)
    assert r["passed"] is expected


def test_check_format_unknown_slot():
    r = check_format("INEXISTANT_Ω", "x.geojson")
    assert r["passed"] is False


def test_check_format_pression_humaine_accepts_geotiff():
    r = check_format("PRESSION_HUMAINE_Ω", "density.tif")
    assert r["passed"] is True
    r2 = check_format("PRESSION_HUMAINE_Ω", "density.tiff")
    assert r2["passed"] is True


# ═══════════════════════════════════════════════════════════════════
# Tests Validators - check_size
# ═══════════════════════════════════════════════════════════════════
def test_check_size_too_small_rejected():
    r = check_size("CHASSE_ZEC_SEPAQ_Ω", 100)
    assert r["passed"] is False


def test_check_size_within_bounds_ok():
    r = check_size("CHASSE_ZEC_SEPAQ_Ω", 1024)
    assert r["passed"] is True


def test_check_size_too_large_rejected():
    huge = SLOT_BY_ID["CHASSE_ZEC_SEPAQ_Ω"]["taille_max_octets"] + 1
    r = check_size("CHASSE_ZEC_SEPAQ_Ω", huge)
    assert r["passed"] is False


# ═══════════════════════════════════════════════════════════════════
# Tests Validators - check_integrity
# ═══════════════════════════════════════════════════════════════════
def test_check_integrity_geojson_ok(tmp_path):
    p = tmp_path / "x.geojson"
    p.write_text("{\"type\":\"FeatureCollection\",\"features\":[]}",
                  encoding="utf-8")
    r = check_integrity(p)
    assert r["passed"] is True
    assert len(r["sha256"]) == 64


def test_check_integrity_zip_valid(tmp_path):
    p = tmp_path / "x.zip"
    with zipfile.ZipFile(p, "w") as zf:
        zf.writestr("a.shp", b"shapefile_placeholder")
        zf.writestr("a.dbf", b"dbf_placeholder")
    r = check_integrity(p)
    assert r["passed"] is True
    assert r["zip_entries"] == 2
    assert r["has_shapefile"] is True


def test_check_integrity_zip_corrupted(tmp_path):
    p = tmp_path / "bad.zip"
    p.write_bytes(b"not a real zip file content xxxxxx")
    r = check_integrity(p)
    assert r["passed"] is False


def test_check_integrity_missing_file(tmp_path):
    r = check_integrity(tmp_path / "nope.gpkg")
    assert r["passed"] is False


# ═══════════════════════════════════════════════════════════════════
# Tests validate_upload (intégration validators)
# ═══════════════════════════════════════════════════════════════════
def test_validate_upload_full_pass(tmp_path):
    p = tmp_path / "ok.geojson"
    p.write_text("{\"type\":\"FeatureCollection\",\"features\":[" +
                  ",".join(["{\"type\":\"Feature\",\"geometry\":null,\"properties\":{}}"
                             for _ in range(20)]) + "]}",
                  encoding="utf-8")
    r = validate_upload("CHASSE_ZEC_SEPAQ_Ω", "ok.geojson", p)
    assert r["passed"] is True
    assert r["sha256"] is not None
    assert all(v["passed"] for v in r["validators"])


def test_validate_upload_unknown_slot(tmp_path):
    p = tmp_path / "x.geojson"
    p.write_text("{}")
    r = validate_upload("UNKNOWN_Ω", "x.geojson", p)
    assert r["passed"] is False
    assert "SLOT_INCONNU::UNKNOWN_Ω" in r["errors"]


# ═══════════════════════════════════════════════════════════════════
# Tests endpoints HTTP (in-process via TestClient)
# ═══════════════════════════════════════════════════════════════════
@pytest.fixture(scope="module")
def http_client():
    os.environ.setdefault("GIS_RECEPTION_COMMANDANT_TOKEN",
                          "TEST_TOKEN_GIS_RECEPTION_OMEGA")
    from routes.gis_reception_router_omega import router
    from fastapi import FastAPI
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


def test_endpoint_slots_returns_six(http_client):
    r = http_client.get("/api/v30/admin-premium/gis/slots")
    assert r.status_code == 200
    data = r.json()
    # ORDRE N°52-EXT VOIE A : 6 slots originaux + 1 PEE_MAJ_Ω
    assert data["slots_count"] == 7
    assert data["manifest_id"] == "SLOTS_GIS_PROTÉGÉS_Ω"


def test_endpoint_intake_status_default(http_client):
    r = http_client.get("/api/v30/admin-premium/gis/intake-status")
    assert r.status_code == 200
    data = r.json()
    assert data["manifest_id"] == "GIS_RECEPTION_INTAKE_Ω"
    # ORDRE N°52-EXT VOIE A : intake étendu à 7 slots
    assert data["stats"]["total_slots"] == 7


def test_endpoint_upload_no_token_returns_401(http_client):
    r = http_client.post(
        "/api/v30/admin-premium/gis/upload/CHASSE_ZEC_SEPAQ_Ω",
        files={"file": ("x.geojson", b"{}", "application/json")},
    )
    assert r.status_code == 401


def test_endpoint_upload_invalid_token_returns_401(http_client):
    r = http_client.post(
        "/api/v30/admin-premium/gis/upload/CHASSE_ZEC_SEPAQ_Ω",
        files={"file": ("x.geojson", b"{}", "application/json")},
        headers={"X-Commandant-Token": "WRONG"},
    )
    assert r.status_code == 401


def test_endpoint_upload_unknown_slot_returns_404(http_client):
    r = http_client.post(
        "/api/v30/admin-premium/gis/upload/SLOT_INEXISTANT",
        files={"file": ("x.geojson", b"{}", "application/json")},
        headers={"X-Commandant-Token": "TEST_TOKEN_GIS_RECEPTION_OMEGA"},
    )
    assert r.status_code == 404


def test_endpoint_upload_unsafe_filename_returns_400(http_client):
    r = http_client.post(
        "/api/v30/admin-premium/gis/upload/CHASSE_ZEC_SEPAQ_Ω",
        files={"file": ("../etc/passwd", b"x" * 1024, "application/octet-stream")},
        headers={"X-Commandant-Token": "TEST_TOKEN_GIS_RECEPTION_OMEGA"},
    )
    assert r.status_code == 400


# ═══════════════════════════════════════════════════════════════════
# Garde-fous institutionnels
# ═══════════════════════════════════════════════════════════════════
def test_router_prefix_admin_premium_only():
    from routes.gis_reception_router_omega import router
    assert router.prefix == "/api/v30/admin-premium/gis"


def test_no_synthetic_data_in_validators():
    """Les validators ne doivent JAMAIS générer de données synthétiques."""
    import inspect
    from engines.v8_institutional.especes import gis_reception_validators_omega as mod
    src = inspect.getsource(mod)
    forbidden = ["random.", "fake_", "synthetic", "mock_data", "_dummy_"]
    for kw in forbidden:
        assert kw not in src, f"Mot-clé interdit '{kw}' dans validators"

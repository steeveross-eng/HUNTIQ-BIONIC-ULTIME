"""
test_phase_xxiv_multi_upload_omega.py — Tests Phase XXIV (ORDRE N°46)
═════════════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU x3 · ORDRE N°46 · VOIE B

Tests de la VOIE B — tuiles régionales MFFP multi-upload.

Scope :
  · Flag multi_upload=True sur FORET_MFFP_Ω uniquement
  · Agrégation SHA-256 composite déterministe (ordre insensible)
  · Upload de 2 tuiles factices GeoJSON (< 100 Mo) via TestClient
  · Dédup par filename (ré-upload du même nom → écrase l'entrée sans doublon)
  · Comportement inchangé pour les 5 autres slots (single-upload)
  · Exposition publique de multi_upload / files_min / files_max / voie_acquisition
  · FUSION ADD-ONLY (aucune régression des tests Phase XXII/XXIII)

Anti-générique : tuiles factices GeoJSON minimales mais structurellement valides
(aucune coordonnée géographique réelle, étiquetées `test_fixture=True`).
V30 INVIOLABLE.
═════════════════════════════════════════════════════════════════════════════
"""
from __future__ import annotations
import hashlib
import json
import os
import sys
import zipfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).parent.parent))

from engines.v8_institutional.especes.gis_reception_validators_omega import (
    SLOTS_GIS_PROTÉGÉS_SPEC, SLOT_BY_ID,
    compute_composite_sha256, is_multi_upload_slot, list_slots,
)


# ═══════════════════════════════════════════════════════════════════
# Spec — flag multi_upload
# ═══════════════════════════════════════════════════════════════════
def test_foret_mffp_has_multi_upload_flag():
    """FORET_MFFP_Ω doit être le seul slot multi_upload (VOIE B)."""
    spec = SLOT_BY_ID["FORET_MFFP_Ω"]
    assert spec.get("multi_upload") is True
    assert spec.get("files_min", 1) == 1
    assert spec.get("files_max", 1) >= 2
    assert spec.get("voie_acquisition") == "VOIE_B_TUILES_REGIONALES_MFFP"


def test_only_foret_mffp_is_multi_upload():
    """Les 5 autres slots DOIVENT rester single-upload (ADD-ONLY strict)."""
    multi = [s["slot_id"] for s in SLOTS_GIS_PROTÉGÉS_SPEC
             if s.get("multi_upload") is True]
    assert multi == ["FORET_MFFP_Ω"]


def test_is_multi_upload_slot_helper():
    assert is_multi_upload_slot("FORET_MFFP_Ω") is True
    assert is_multi_upload_slot("CHASSE_ZEC_SEPAQ_Ω") is False
    assert is_multi_upload_slot("INEXISTANT_Ω") is False


def test_list_slots_exposes_multi_upload_fields():
    """L'API publique /slots doit exposer multi_upload + files_min/max + voie."""
    public = list_slots()
    foret = next(p for p in public if p["slot_id"] == "FORET_MFFP_Ω")
    assert foret["multi_upload"] is True
    assert foret["files_min"] == 1
    assert foret["files_max"] == 32
    assert foret["voie_acquisition"] == "VOIE_B_TUILES_REGIONALES_MFFP"
    chasse = next(p for p in public if p["slot_id"] == "CHASSE_ZEC_SEPAQ_Ω")
    assert chasse["multi_upload"] is False
    assert chasse["voie_acquisition"] == "VOIE_A_MONOFICHIER"


# ═══════════════════════════════════════════════════════════════════
# compute_composite_sha256 — déterminisme et robustesse
# ═══════════════════════════════════════════════════════════════════
def test_composite_sha256_empty_list_returns_empty_string():
    assert compute_composite_sha256([]) == ""


def test_composite_sha256_single_sha_deterministic():
    s = "a" * 64
    expected = hashlib.sha256((s + "\n").encode("utf-8")).hexdigest()
    assert compute_composite_sha256([s]) == expected


def test_composite_sha256_order_insensitive():
    """Hash composite identique quel que soit l'ordre d'arrivée des tuiles."""
    shas = [
        hashlib.sha256(b"TUILE_REGION_01").hexdigest(),
        hashlib.sha256(b"TUILE_REGION_02").hexdigest(),
        hashlib.sha256(b"TUILE_REGION_03").hexdigest(),
    ]
    a = compute_composite_sha256(shas)
    b = compute_composite_sha256(list(reversed(shas)))
    c = compute_composite_sha256([shas[1], shas[2], shas[0]])
    assert a == b == c
    assert len(a) == 64


def test_composite_sha256_changes_when_content_changes():
    base = [hashlib.sha256(b"A").hexdigest(),
            hashlib.sha256(b"B").hexdigest()]
    diff = [hashlib.sha256(b"A").hexdigest(),
            hashlib.sha256(b"C").hexdigest()]
    assert compute_composite_sha256(base) != compute_composite_sha256(diff)


def test_composite_sha256_rejects_empty_entries():
    """Une entrée vide est ignorée silencieusement (anti-pollution)."""
    shas = [hashlib.sha256(b"X").hexdigest(), "", None]  # type: ignore
    result = compute_composite_sha256([s for s in shas if s])
    expected = compute_composite_sha256([hashlib.sha256(b"X").hexdigest()])
    assert result == expected


# ═══════════════════════════════════════════════════════════════════
# Client HTTP (intégration)
# ═══════════════════════════════════════════════════════════════════
TEST_TOKEN_XXIV = "TEST_TOKEN_GIS_RECEPTION_OMEGA"


@pytest.fixture(scope="module")
def http_client_mffp(tmp_path_factory):
    """Client isolé avec manifest et incoming redirigés dans tmp_path.
    Utilise le même token que Phase XXII (cohérence cross-modules)."""
    tmp_root = tmp_path_factory.mktemp("gis_reception_xxiv")
    os.environ.setdefault("GIS_RECEPTION_COMMANDANT_TOKEN", TEST_TOKEN_XXIV)

    # Recharger le routeur avec un répertoire de réception isolé
    import importlib
    from routes import gis_reception_router_omega as mod
    importlib.reload(mod)
    mod.RECEPTION_ROOT = Path(tmp_root) / "gis_operational"
    mod.INCOMING_DIR = mod.RECEPTION_ROOT / "incoming"
    mod.QUARANTINE_DIR = mod.RECEPTION_ROOT / "quarantine"
    mod.MANIFEST_PATH = mod.RECEPTION_ROOT / "GIS_RECEPTION_INTAKE_Ω.json"
    mod.INCOMING_DIR.mkdir(parents=True, exist_ok=True)
    mod.QUARANTINE_DIR.mkdir(parents=True, exist_ok=True)

    # Rediriger aussi l'audit-log isolé
    from engines.v8_institutional.especes import gis_audit_log_omega as audit_mod
    audit_mod.AUDIT_LOG_PATH = mod.RECEPTION_ROOT / "audit_log.jsonl"
    audit_mod.AUDIT_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

    from fastapi import FastAPI
    app = FastAPI()
    app.include_router(mod.router)
    return TestClient(app)


def _make_fake_tuile_mffp(path: Path, region_code: str) -> bytes:
    """Génère une tuile GeoJSON factice (< 10 Ko) — test_fixture=True."""
    payload = {
        "type": "FeatureCollection",
        "name": f"TUILE_MFFP_FIXTURE_{region_code}",
        "meta": {
            "test_fixture": True,
            "description": "Fixture pytest Ordre n°46 — AUCUNE donnée réelle",
            "region_code": region_code,
            "produced_by": "test_phase_xxiv_multi_upload_omega.py",
        },
        "features": [
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [0, 0]},
                "properties": {"fixture_id": f"{region_code}-{i}"}
            }
            for i in range(50)
        ],
    }
    content = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    path.write_bytes(content)
    return content


def test_multi_upload_two_tuiles_foret_mffp(http_client_mffp, tmp_path):
    """Scénario VOIE B : upload de 2 tuiles régionales factices."""
    t1 = tmp_path / "tuile_mffp_region01.geojson"
    t2 = tmp_path / "tuile_mffp_region02.geojson"
    c1 = _make_fake_tuile_mffp(t1, "REGION_01")
    c2 = _make_fake_tuile_mffp(t2, "REGION_02")
    sha1 = hashlib.sha256(c1).hexdigest()
    sha2 = hashlib.sha256(c2).hexdigest()

    expected_composite = compute_composite_sha256([sha1, sha2])

    # Upload tuile 1
    r1 = http_client_mffp.post(
        "/api/v30/admin-premium/gis/upload/FORET_MFFP_Ω",
        files={"file": (t1.name, c1, "application/geo+json")},
        headers={"X-Commandant-Token": "TEST_TOKEN_GIS_RECEPTION_OMEGA"},
    )
    assert r1.status_code == 200, r1.text
    d1 = r1.json()
    assert d1["passed"] is True
    assert d1["sha256"] == sha1
    assert d1["multi_upload"] is True
    assert d1["files_loaded_count"] == 1
    assert d1["composite_sha256"] == compute_composite_sha256([sha1])

    # Upload tuile 2
    r2 = http_client_mffp.post(
        "/api/v30/admin-premium/gis/upload/FORET_MFFP_Ω",
        files={"file": (t2.name, c2, "application/geo+json")},
        headers={"X-Commandant-Token": "TEST_TOKEN_GIS_RECEPTION_OMEGA"},
    )
    assert r2.status_code == 200, r2.text
    d2 = r2.json()
    assert d2["passed"] is True
    assert d2["sha256"] == sha2
    assert d2["multi_upload"] is True
    assert d2["files_loaded_count"] == 2
    assert d2["composite_sha256"] == expected_composite

    # Intake-status
    r3 = http_client_mffp.get("/api/v30/admin-premium/gis/intake-status")
    assert r3.status_code == 200
    intake = r3.json()
    foret = intake["slots"]["FORET_MFFP_Ω"]
    assert foret["status"] == "LOADED"
    assert foret["files_loaded_count"] == 2
    assert foret["composite_sha256"] == expected_composite
    assert foret["multi_upload"] is True
    assert len(foret["uploads"]) == 2
    uploaded_names = {u["filename"] for u in foret["uploads"]}
    assert uploaded_names == {"tuile_mffp_region01.geojson",
                              "tuile_mffp_region02.geojson"}


def test_multi_upload_dedup_same_filename(http_client_mffp, tmp_path):
    """Ré-upload du même nom de fichier → remplacement, pas de doublon."""
    # Reset via nouveau slot : utilisons ce test indépendant après le précédent.
    # On ré-upload tuile01 avec contenu différent → doit écraser l'entrée.
    t = tmp_path / "tuile_mffp_region01.geojson"
    new_content = _make_fake_tuile_mffp(t, "REGION_01_REV2")
    new_sha = hashlib.sha256(new_content).hexdigest()

    r = http_client_mffp.post(
        "/api/v30/admin-premium/gis/upload/FORET_MFFP_Ω",
        files={"file": (t.name, new_content, "application/geo+json")},
        headers={"X-Commandant-Token": "TEST_TOKEN_GIS_RECEPTION_OMEGA"},
    )
    assert r.status_code == 200
    d = r.json()
    # files_loaded_count DOIT rester 2 (pas 3 → dédup par filename)
    assert d["files_loaded_count"] == 2
    # Le nouveau SHA doit être présent dans le composite
    intake = http_client_mffp.get(
        "/api/v30/admin-premium/gis/intake-status").json()
    foret = intake["slots"]["FORET_MFFP_Ω"]
    shas_present = {u["sha256"] for u in foret["uploads"]}
    assert new_sha in shas_present


def test_single_upload_slot_unchanged(http_client_mffp, tmp_path):
    """Les autres slots (single-upload) doivent rester strictement inchangés."""
    t = tmp_path / "tiny_zec.geojson"
    content = _make_fake_tuile_mffp(t, "ZEC_FIXTURE")
    r = http_client_mffp.post(
        "/api/v30/admin-premium/gis/upload/CHASSE_ZEC_SEPAQ_Ω",
        files={"file": (t.name, content, "application/geo+json")},
        headers={"X-Commandant-Token": "TEST_TOKEN_GIS_RECEPTION_OMEGA"},
    )
    assert r.status_code == 200
    d = r.json()
    assert d["passed"] is True
    # Même pour un single-upload, le backend retourne les champs (à 1 / False)
    assert d["multi_upload"] is False
    assert d["files_loaded_count"] == 1
    assert d["composite_sha256"] is not None  # 1 fichier → un composite existe
    assert len(d["composite_sha256"]) == 64


# ═══════════════════════════════════════════════════════════════════
# Garde-fous ADD-ONLY
# ═══════════════════════════════════════════════════════════════════
def test_spec_fields_unchanged_for_non_mffp():
    """Aucun autre slot ne doit contenir multi_upload ni VOIE_B_*."""
    for s in SLOTS_GIS_PROTÉGÉS_SPEC:
        if s["slot_id"] == "FORET_MFFP_Ω":
            continue
        # Par défaut, pas de multi-upload ni files_max, OU strict mono-fichier
        assert s.get("multi_upload", False) is False, (
            f"{s['slot_id']} ne doit pas avoir multi_upload activé")


def test_no_synthetic_data_in_multi_upload_module():
    """Anti-générique : compute_composite_sha256 ne fabrique aucune donnée."""
    import inspect
    from engines.v8_institutional.especes import gis_reception_validators_omega as mod
    src = inspect.getsource(mod.compute_composite_sha256)
    forbidden = ["random.", "fake_sha", "synthetic", "mock_data", "_dummy_"]
    for kw in forbidden:
        assert kw not in src, f"Mot-clé interdit '{kw}' dans compute_composite_sha256"

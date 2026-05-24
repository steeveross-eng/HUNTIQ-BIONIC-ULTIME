"""
test_habitat_fusion_p1_structural_omega.py — Tests doctrinaux P1 STRUCTURAL+
═══════════════════════════════════════════════════════════════════════════════
P22ΩΩ_NDVI_LIDAR_P1_STRUCTURAL+_Ω · COMMANDANT STEEVE-MAX · 2026-02-20

INVARIANTS DOCTRINAUX
---------------------
  J-1 : Engine P1 importable + version explicite
  J-2 : compute_habitat_score reste fonctionnel (proxy P0 strict)
  J-3 : weight_active=0.35 INCHANGÉ vs P0 (anti-générique strict)
  J-4 : 4 clients d'ingestion CODE-READY (NASA HLS · ESA S2 · NRCan · MFFP)
  J-5 : Tous les clients INERTES par défaut (refusent download)
  J-6 : is_p1_ready_for_ingestion()=False sans credentials/ARM
  J-7 : Registries P1 mis à jour avec STATUS=P1_READY_AWAITING_CREDENTIALS
  J-8 : Verrou Phase III préservé (P0 engine + scoring inchangés)
"""
import sys
import os
sys.path.insert(0, "/app/backend")

import pytest

from engines.v8_institutional import habitat_fusion_engine_p1 as HFE_P1
from engines.v8_institutional import habitat_fusion_engine_p0 as HFE_P0
from integrations.ingestion_p1 import (
    nasa_hls_client as NASA_HLS,
    esa_sentinel2_client as ESA_S2,
    nrcan_hrdem_client as NRCAN,
    mffp_foret_ouverte_client as MFFP,
)
import json
from pathlib import Path

BSL = (48.206657, -68.382422)


def test_j1_engine_p1_importable():
    assert HFE_P1.ENGINE_NAME == "HABITAT-FUSION-ENGINE-P1"
    assert HFE_P1.ENGINE_DOCTRINE == "P22ΩΩ_NDVI_LIDAR_P1_STRUCTURAL+_Ω"
    assert HFE_P1.ENGINE_PHASE == "P1_STRUCTURAL+_AWAITING_INGESTION"


def test_j2_compute_score_proxy_works():
    r = HFE_P1.compute_habitat_score(species="chevreuil", lat=BSL[0], lng=BSL[1], season="automne")
    assert r.get("habitat_score") is not None
    assert r.get("engine_proxy") == "HABITAT-FUSION-ENGINE-P1"
    assert r.get("phase_p1") == "P1_STRUCTURAL+_AWAITING_INGESTION"


def test_j3_weight_active_inchanged_035():
    """weight_active DOIT rester 0.35 (anti-générique strict)."""
    status = HFE_P1.get_p1_status()
    assert status["weight_active"] == 0.35, "VIOLATION anti-générique : weight_active != 0.35"
    assert status["weight_target_p2_full"] == 1.00


def test_j4_four_clients_code_ready():
    status = HFE_P1.get_ingestion_clients_status()
    expected = {"nasa_hls", "esa_sentinel2_l2a", "nrcan_hrdem", "mffp_foret_ouverte"}
    assert set(status.keys()) == expected
    for k, v in status.items():
        assert v.get("client") is not None, f"client {k} mal initialisé"
        assert v.get("doctrine") == "P22ΩΩ_NDVI_LIDAR_P1_STRUCTURAL+_Ω"


def test_j5_clients_inertes_par_defaut():
    """Tous les clients refusent download sans ARM flag."""
    # NASA HLS · sans credentials ni ARM
    assert NASA_HLS.is_armed() is False
    with pytest.raises(RuntimeError, match="credentials manquants|non armée"):
        NASA_HLS.download_granules(["G_DUMMY"], "/tmp")
    # ESA S2 · sans credentials ni ARM
    assert ESA_S2.is_armed() is False
    with pytest.raises(RuntimeError, match="credentials manquants|non armée"):
        ESA_S2.download_scenes(["S_DUMMY"], ["B04", "B08"], "/tmp")
    # NRCan · open data mais sans ARM + DISK_AUTH
    assert NRCAN.is_armed() is False
    with pytest.raises(RuntimeError, match="non armée"):
        NRCAN.download_tiles(["T_DUMMY"], "/tmp")
    # MFFP · open data mais sans ARM + DISK_AUTH
    assert MFFP.is_armed() is False
    with pytest.raises(RuntimeError, match="non armée"):
        MFFP.download_lidar_las(["L_DUMMY"], "/tmp")


def test_j6_ingestion_p1_not_ready_by_default():
    assert HFE_P1.is_p1_ready_for_ingestion() is False


def test_j7_registries_p1_updated():
    base = Path("/app/backend/data/ndvi_lidar_p0")
    ndvi = json.loads((base / "ndvi_hr_registry_Ω.json").read_text())
    lidar = json.loads((base / "lidar_pancanada_registry_Ω.json").read_text())
    manifest = json.loads((base / "habitat_fusion_sources_manifest.json").read_text())

    assert ndvi["_status"] == "P1_READY_AWAITING_CREDENTIALS"
    assert ndvi["_phase"] == "P1_STRUCTURAL+"
    assert "_p1_clients" in ndvi

    assert lidar["_status"] == "P1_READY_AWAITING_CREDENTIALS"
    assert lidar["_phase"] == "P1_STRUCTURAL+"
    assert "_p1_clients" in lidar

    assert manifest["_status"] == "P1_STRUCTURAL_READY"
    assert manifest["weight_active"] == 0.35
    assert manifest["weight_target_p2"] == 1.00


def test_j8_verrou_phase_iii_p0_intact():
    """P0 engine doit rester strictement fonctionnel et inchangé."""
    r0 = HFE_P0.compute_habitat_score(species="chevreuil", lat=BSL[0], lng=BSL[1], season="automne")
    r1 = HFE_P1.compute_habitat_score(species="chevreuil", lat=BSL[0], lng=BSL[1], season="automne")
    # Le score P1 (proxy) doit être identique au score P0 (anti-générique strict)
    assert r0["habitat_score"] == r1["habitat_score"]
    assert r1["partial_p0"] is True


def test_j9_axes_status_p1_structural_plus():
    status = HFE_P1.get_p1_status()
    axes = status["axes"]
    # 2 axes ingestion en P1_READY_AWAITING_CREDENTIALS
    assert axes["vegetation_ndvi_hr"]["status"] == "P1_READY_AWAITING_CREDENTIALS"
    assert axes["vegetation_ndvi_hr"]["active_in_compute"] is False
    assert axes["topography_lidar"]["status"] == "P1_READY_AWAITING_CREDENTIALS"
    assert axes["topography_lidar"]["active_in_compute"] is False
    # 2 axes biology toujours READY actifs
    assert axes["corridors_behavior"]["status"] == "READY"
    assert axes["corridors_behavior"]["active_in_compute"] is True
    assert axes["species_biogeography"]["status"] == "READY"
    assert axes["species_biogeography"]["active_in_compute"] is True


def test_j10_clients_credentials_status():
    # NASA HLS · sans credentials par défaut
    assert NASA_HLS.is_credential_ready() is False
    # ESA S2 · sans credentials par défaut
    assert ESA_S2.is_credential_ready() is False
    # NRCan · open data → True
    assert NRCAN.is_credential_ready() is True
    # MFFP · open data → True
    assert MFFP.is_credential_ready() is True

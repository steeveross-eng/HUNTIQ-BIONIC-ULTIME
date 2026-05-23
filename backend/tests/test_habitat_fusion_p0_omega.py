"""
test_habitat_fusion_p0_omega.py — Tests doctrinaux HABITAT-FUSION_P0_Ω
═══════════════════════════════════════════════════════════════════════════════
P22ΩΩ_IA_HABITAT_FUSION_P0_Ω · COMMANDANT STEEVE-MAX · 2026-02-20 · BCE-4X ULTIME ABSOLU

INVARIANTS DOCTRINAUX
---------------------
  I-1  : Manifeste maître présent (HABITAT_FUSION_P0_REGISTRY_Ω.json)
  I-2  : Status global = STRUCTURAL_ACTIVATED_PRE_INGESTION
  I-3  : 4 axes total · 2 READY · 2 PRE_INGESTION
  I-4  : weight_active_p0 = 0.35 · weight_target_p2 = 1.0
  I-5  : 5 espèces supportées (chevreuil/orignal/ours_noir/coyote/dindon_sauvage)
  I-6  : 4 saisons supportées (printemps/ete/automne/hiver)
  I-7  : compute_habitat_score retourne payload avec habitat_score
  I-8  : Divergence biologique stricte (≥4 valeurs distinctes parmi 5 espèces par saison)
  I-9  : Variation saisonnière (≥3 valeurs distinctes parmi 4 saisons par espèce)
  I-10 : Espèce inconnue retourne dict avec clé 'error'
  I-11 : Compatibilité legacy compute_habitat_score_p0 préservée
  I-12 : Verrou Phase III : NDVI HR + LiDAR restent en PRE_INGESTION (jamais READY en P0)
"""
import sys
sys.path.insert(0, "/app/backend")

import pytest

from engines.v8_institutional import habitat_fusion_engine_p0 as HFE
from engines.v8_institutional import habitat_fusion_registry_omega as REG

BSL = (48.206657, -68.382422)
SPECIES = ["chevreuil", "orignal", "ours_noir", "coyote", "dindon_sauvage"]
SEASONS = ["printemps", "ete", "automne", "hiver"]


def test_i1_master_registry_present():
    reg = REG.get_master_registry()
    assert reg, "Manifeste maître HABITAT_FUSION_P0_REGISTRY_Ω.json absent"
    assert reg.get("_doctrine") == "P22ΩΩ_IA_HABITAT_FUSION_P0_Ω"


def test_i2_status_global():
    assert REG.get_status() == "STRUCTURAL_ACTIVATED_PRE_INGESTION"


def test_i3_axes_count():
    axes_status = HFE.get_axes_status()
    assert axes_status["axes_total"] == 4
    assert axes_status["axes_ready"] == 2
    assert axes_status["axes_pre_ingestion"] == 2


def test_i4_weights():
    axes_status = HFE.get_axes_status()
    assert axes_status["weight_active_p0"] == 0.35
    assert axes_status["weight_target_p2"] == 1.0
    assert axes_status["weight_pending_p1"] == pytest.approx(0.65, abs=0.01)


def test_i5_species_supported():
    sp_list = REG.get_species_list()
    for sp in SPECIES:
        assert sp in sp_list


def test_i6_seasons_supported():
    sn_list = REG.get_seasons_list()
    for sn in SEASONS:
        assert sn in sn_list


def test_i7_compute_score_payload():
    r = HFE.compute_habitat_score(species="chevreuil", lat=BSL[0], lng=BSL[1], season="automne")
    assert "habitat_score" in r
    assert r["habitat_score"] is not None
    assert r["phase"] == "P0_PRE_FUSION"
    assert r["partial_p0"] is True
    assert r["completion_ratio"] == pytest.approx(0.35, abs=0.01)


def test_i8_biological_divergence_per_season():
    """Au moins 4/5 valeurs distinctes par saison (divergence biologique stricte)."""
    for sn in SEASONS:
        vals = [
            round(HFE.compute_habitat_score(species=sp, lat=BSL[0], lng=BSL[1], season=sn)["habitat_score"], 1)
            for sp in SPECIES
        ]
        distinct = len(set(vals))
        assert distinct >= 4, f"Divergence trop faible saison {sn} : {distinct}/5 · vals={vals}"


def test_i9_seasonal_variation_per_species():
    """Au moins 3/4 saisons distinctes par espèce (variation saisonnière)."""
    for sp in SPECIES:
        vals = [
            round(HFE.compute_habitat_score(species=sp, lat=BSL[0], lng=BSL[1], season=sn)["habitat_score"], 1)
            for sn in SEASONS
        ]
        distinct = len(set(vals))
        assert distinct >= 3, f"Variation saisonnière trop faible espèce {sp} : {distinct}/4 · vals={vals}"


def test_i10_unknown_species_error():
    r = HFE.compute_habitat_score(species="phoque_du_groenland", lat=BSL[0], lng=BSL[1])
    assert "error" in r
    assert r["habitat_score"] is None


def test_i11_legacy_signature_preserved():
    """compute_habitat_score_p0 (legacy P22ΩΩ_NDVI_LIDAR_PANCA_P0) reste fonctionnel."""
    r = HFE.compute_habitat_score_p0(lat=BSL[0], lon=BSL[1], species="chevreuil", season="automne")
    assert "habitat_score_partial_p0" in r
    assert r["partial_p0"] is True
    assert "contributions" in r


def test_i12_verrou_phase_iii_ndvi_lidar_pre_ingestion():
    """NDVI HR + LiDAR DOIVENT rester en PRE_INGESTION en P0 (Verrou Phase III)."""
    axes_status = HFE.get_axes_status()
    axes = axes_status["axes"]
    assert axes["vegetation_ndvi_hr"]["status"] == "PRE_INGESTION"
    assert axes["topography_lidar"]["status"] == "PRE_INGESTION"
    assert axes["corridors_behavior"]["status"] == "READY"
    assert axes["species_biogeography"]["status"] == "READY"


def test_i13_is_full_fusion_false_p0():
    """En P0, full_fusion DOIT être False."""
    assert HFE.is_full_fusion_available() is False


def test_i14_aliases_normalization():
    """Alias d'espèces normalisés (cerf → chevreuil, moose → orignal, etc.)."""
    r1 = HFE.compute_habitat_score(species="cerf", lat=BSL[0], lng=BSL[1])
    r2 = HFE.compute_habitat_score(species="chevreuil", lat=BSL[0], lng=BSL[1])
    assert r1["species"] == r2["species"] == "chevreuil"
    assert r1["habitat_score"] == r2["habitat_score"]

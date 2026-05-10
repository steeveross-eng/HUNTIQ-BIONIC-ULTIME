"""
NEW_ENGINE_1_SPECTRAL_Ω · Pytest neutre
═══════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU · ANTI-GÉNÉRIQUE STRICT

Validation doctrinale du moteur spectral :
  - Formules NDVI / NDWI / EVI (référence MODIS/Sentinel-2)
  - Normalisation 0-1 institutionnelle
  - LST Kelvin → Celsius
  - Fallback 0.5
  - Fusion multi-source avec poids doctrinaux
  - Hooks chaîne_Ω corridors / hydro / pressure_humaine

Naming neutre — aucun mot-clé BCE_4X_EXCLUDED.
"""

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engines.spectral_omega import (
    DEFAULT_HALO_M,
    ENGINE_NAME,
    ENGINE_VERSION,
    FALLBACK_VALUE,
    chain_omega_hydro_pondere,
    chain_omega_pondere_corridors,
    chain_omega_pressure_humaine_pondere,
    compute_evi,
    compute_lst_landsat,
    compute_ndvi,
    compute_ndwi,
    fusion_spectral_multisource,
    normalize_evi,
    normalize_lst_celsius,
    normalize_ndvi,
    normalize_ndwi,
    normalize_to_unit_interval,
)


# ═══════════════════ FORMULAS ═══════════════════

def test_ndvi_canonical():
    """NDVI = (NIR-RED)/(NIR+RED). Test sur valeurs canoniques."""
    # Forte végétation : NIR=4000, RED=600 → NDVI ≈ 0.74
    n = compute_ndvi(red=600.0, nir=4000.0)
    assert abs(n - 0.7391) < 0.01
    # Sol nu : NIR=2000, RED=1800 → NDVI ≈ 0.053
    n2 = compute_ndvi(red=1800.0, nir=2000.0)
    assert abs(n2 - 0.0526) < 0.01


def test_ndvi_zero_denominator_safe():
    """Si NIR + RED = 0 → 0.0 (pas crash)."""
    assert compute_ndvi(red=0.0, nir=0.0) == 0.0


def test_ndvi_none_inputs():
    """None → NaN."""
    assert math.isnan(compute_ndvi(red=None, nir=1000.0))


def test_ndwi_canonical():
    """NDWI = (GREEN-NIR)/(GREEN+NIR). Eau pure : GREEN haut, NIR bas."""
    # Eau : GREEN=2000, NIR=400 → NDWI = 0.667
    n = compute_ndwi(green=2000.0, nir=400.0)
    assert abs(n - 0.6667) < 0.01


def test_evi_canonical():
    """EVI = G*(NIR-RED)/(NIR+C1*RED-C2*BLUE+L) avec G=2.5, C1=6, C2=7.5, L=1."""
    # Forte végétation : NIR=4000, RED=600, BLUE=300
    e = compute_evi(red=600.0, nir=4000.0, blue=300.0)
    expected = 2.5 * (4000 - 600) / (4000 + 6 * 600 - 7.5 * 300 + 1)
    assert abs(e - expected) < 0.001


def test_lst_kelvin_to_celsius():
    """LST conversion Kelvin → Celsius."""
    # 273.15 K = 0.0 °C
    assert abs(compute_lst_landsat(273.15) - 0.0) < 0.01
    # 300 K = 26.85 °C
    assert abs(compute_lst_landsat(300.0) - 26.85) < 0.01


# ═══════════════════ NORMALIZATION ═══════════════════

def test_normalize_unit_interval_clipping():
    """Clipping strict [0, 1]."""
    assert normalize_to_unit_interval(-2.0, -1.0, 1.0) == 0.0   # clipping bas
    assert normalize_to_unit_interval(2.0, -1.0, 1.0) == 1.0    # clipping haut
    assert normalize_to_unit_interval(0.0, -1.0, 1.0) == 0.5    # milieu


def test_normalize_fallback_for_nan():
    """NaN → fallback institutionnel 0.5."""
    assert normalize_to_unit_interval(float("nan"), -1.0, 1.0) == FALLBACK_VALUE


def test_normalize_ndvi_range():
    """NDVI -1..1 → 0..1."""
    assert normalize_ndvi(-1.0) == 0.0
    assert normalize_ndvi(0.0) == 0.5
    assert normalize_ndvi(1.0) == 1.0


def test_normalize_ndwi_range():
    """NDWI -1..1 → 0..1."""
    assert normalize_ndwi(-1.0) == 0.0
    assert normalize_ndwi(0.5) == 0.75


def test_normalize_evi_clipping():
    """EVI clipping [-1, 1] → [0, 1]."""
    assert normalize_evi(2.5) == 1.0  # clipping haut
    assert normalize_evi(-1.5) == 0.0  # clipping bas


def test_normalize_lst_celsius_range():
    """LST [-30, 50] °C → [0, 1]."""
    assert normalize_lst_celsius(-30.0) == 0.0
    assert normalize_lst_celsius(10.0) == 0.5
    assert normalize_lst_celsius(50.0) == 1.0


# ═══════════════════ FALLBACK ═══════════════════

def test_fallback_constant_doctrinal():
    """Constante fallback institutionnelle = 0.5."""
    assert FALLBACK_VALUE == 0.5


def test_engine_identity():
    """ENGINE_NAME et ENGINE_VERSION cohérents avec la commande."""
    assert "SPECTRAL" in ENGINE_NAME.upper()
    assert "V1_LOCK" in ENGINE_VERSION
    assert "NEW_ENGINE_1" in ENGINE_VERSION


# ═══════════════════ FUSION ═══════════════════

def test_fusion_multisource_weighted():
    """Fusion = NDVI*0.40 + NDWI*0.20 + EVI*0.30 + LST_inv*0.10."""
    payload = {
        "ndvi_normalized": 0.8, "ndwi_normalized": 0.4,
        "evi_normalized": 0.7, "lst_normalized": 0.6,
    }
    f = fusion_spectral_multisource(payload)
    expected = (0.8 * 0.40 + 0.4 * 0.20 + 0.7 * 0.30 + (1 - 0.6) * 0.10) / 1.0
    assert abs(f["fused_score_0_1"] - expected) < 0.001
    assert "components" in f
    assert "weights" in f


def test_fusion_with_missing_lst():
    """Si lst_normalized absent → fallback dans inversion."""
    payload = {"ndvi_normalized": 0.6, "ndwi_normalized": 0.5,
               "evi_normalized": 0.4}
    f = fusion_spectral_multisource(payload)
    # Pas d'erreur, score dans [0, 1]
    assert 0.0 <= f["fused_score_0_1"] <= 1.0


# ═══════════════════ CHAINE_Ω ═══════════════════

def test_chain_omega_pondere_routes():
    """Chain corridors → factor cap [0.5, 1.5]."""
    routes = [{"id": "n1", "intensity": 50}]
    spec = {"ndvi_normalized": 0.9, "ndwi_normalized": 0.5,
            "lst_normalized": 0.3}
    out = chain_omega_pondere_corridors(routes, spec)
    assert len(out) == 1
    assert out[0]["_spectral_chain"] == "CHAINE_Ω_SPECTRAL→CORRIDORS"
    assert 0.5 <= out[0]["_spectral_factor"] <= 1.5


def test_chain_omega_routes_empty_passthrough():
    """Liste vide → passe-plat."""
    assert chain_omega_pondere_corridors([], {}) == []


def test_chain_omega_hydro_boost_with_high_ndwi():
    """NDWI élevé → boost hydro."""
    base = 50.0
    spec_high_ndwi = {"ndwi_normalized": 1.0}
    weighted = chain_omega_hydro_pondere(base, spec_high_ndwi)
    assert weighted > base
    assert weighted <= base * 1.3  # cap


def test_chain_omega_pressure_humaine_inversion():
    """NDVI bas (couvert dégradé) → pression humaine accentuée."""
    base = 50.0
    spec_low_ndvi = {"ndvi_normalized": 0.0}
    weighted = chain_omega_pressure_humaine_pondere(base, spec_low_ndvi)
    assert weighted > base


# ═══════════════════ DOCTRINE ═══════════════════

def test_default_halo_doctrinal():
    """DEFAULT_HALO_M = 200m doctrinal."""
    assert DEFAULT_HALO_M == 200.0

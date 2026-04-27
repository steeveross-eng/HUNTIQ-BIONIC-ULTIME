"""
test_phase_d_renduomega_palette.py — PHASE_TERRITOIRE_Ω_AUDIT_PHASE_D
═══════════════════════════════════════════════════════════════════════════
Phase     : PHASE_TERRITOIRE_Ω_AUDIT_PHASE_D_VERROUILLAGE_RENDUOMEGA
Commandant: STEEVE-MAX
Tag       : BCE-4X ULTIME ABSOLU — TOP-ABSOLU

Tests de verrouillage de la palette institutionnelle verte RENDUΩ.
Source : /app/frontend/src/lib/renduOmegaStore.js (immutable Object.freeze)

Doctrine : V30 LOCKED · XIX non recomputé · VITAUX non recomputé · backend READ-ONLY.
"""
from pathlib import Path

RENDU_FILE = Path("/app/frontend/src/lib/renduOmegaStore.js")
LAYERS_FILE = Path("/app/frontend/src/components/territoire/BionicLayersV8.jsx")


def _src(p: Path) -> str:
    return p.read_text(encoding="utf-8")


# ═══════════════════════════════════════════════════════════════════════════
# Palette PHASE-D verrouillée : #00A676 / #4CC99A / #B2F2D9
# ═══════════════════════════════════════════════════════════════════════════
def test_renduomega_color_is_phase_d_green():
    s = _src(RENDU_FILE)
    assert "color: '#00A676'" in s, "RENDU_OMEGA.color doit être #00A676 (PHASE-D)"


def test_renduomega_palette_phase_d_complete():
    s = _src(RENDU_FILE)
    assert "paletteOmegaPhaseD: Object.freeze" in s
    assert "primary:    '#00A676'" in s
    assert "haloInner:  '#4CC99A'" in s
    assert "haloOuter:  '#B2F2D9'" in s
    # Legacy orange préservé pour audit
    assert "legacyOrange: '#FF8F00'" in s


def test_renduomega_organic_texture_enabled():
    s = _src(RENDU_FILE)
    assert "organicTexture: Object.freeze" in s
    assert "haloInnerWeightFactor: 1.85" in s
    assert "haloOuterWeightFactor: 3.10" in s
    assert "haloInnerOpacity: 0.62" in s
    assert "haloOuterOpacity: 0.32" in s


def test_renduomega_species_coefficients_5_official():
    s = _src(RENDU_FILE)
    assert "speciesWeightCoefficient: Object.freeze" in s
    for sp in ("orignal", "chevreuil", "ours_noir", "dindon_sauvage", "wapiti"):
        assert f"{sp}:" in s, f"coef multi-espèce manquant : {sp}"


def test_renduomega_season_coefficients_12_months():
    s = _src(RENDU_FILE)
    assert "seasonWeightCoefficient: Object.freeze" in s
    # Pic chasse automne
    assert "10: 1.20" in s, "pic saison octobre absent"
    assert "9: 1.15" in s, "pic saison septembre absent"


def test_resolve_phase_d_style_function_export():
    s = _src(RENDU_FILE)
    assert "export function resolveCorridorStylePhaseD" in s
    assert "haloInner:" in s
    assert "haloOuter:" in s
    assert "primary:" in s


def test_compute_supra_art_halo_uses_phase_d_palette():
    s = _src(RENDU_FILE)
    # Halo interne : palette.haloInner
    assert "color: palette.haloInner" in s
    # Halo externe : palette.haloOuter
    assert "color: palette.haloOuter" in s


# ═══════════════════════════════════════════════════════════════════════════
# Sondes BionicLayersV8 — probes X150 actualisées PHASE-D
# ═══════════════════════════════════════════════════════════════════════════
def test_bionic_layers_x150_probe_phase_d_color():
    s = _src(LAYERS_FILE)
    assert "color_strict_phase_d_green: RENDU_OMEGA.color === '#00A676'" in s


def test_bionic_layers_x150_probe_palette_phase_d_complete():
    s = _src(LAYERS_FILE)
    assert "palette_phase_d_complete:" in s
    assert "RENDU_OMEGA.paletteOmegaPhaseD?.primary === '#00A676'" in s
    assert "RENDU_OMEGA.paletteOmegaPhaseD?.haloInner === '#4CC99A'" in s
    assert "RENDU_OMEGA.paletteOmegaPhaseD?.haloOuter === '#B2F2D9'" in s


def test_bionic_layers_phase_d_lock_signature():
    s = _src(LAYERS_FILE)
    assert "_phase_d_lock: 'PHASE_D_VERROUILLAGE_RENDUOMEGA_BCE4X_STEEVEMAX'" in s
    assert "_rendu_color_canon_phase_d: '#00A676'" in s


# ═══════════════════════════════════════════════════════════════════════════
# Doctrine BCE-4X — V30 inviolé
# ═══════════════════════════════════════════════════════════════════════════
def test_v30_lock_sha256_invariance_phase_d():
    """V30 reste cryptographiquement intact après PHASE-D."""
    import hashlib
    REGISTRY_LOCK_SHA = "fb765b94cc1fd4216c4afa4c0fb72bc1fd8e18fc26b6955db8157b42a26ecb0c"
    ENGINE_IA_SHA = "bcb1e3a6a92304a171978ee7b6be2151e7035c84d8ffc1690839d993be9e39d3"
    for path, expected in [
        ("/app/backend/engines/v8_institutional/registry_lock_omega.py", REGISTRY_LOCK_SHA),
        ("/app/backend/engines/v8_institutional/engine_ia_corridors_omega.py", ENGINE_IA_SHA),
    ]:
        with open(path, "rb") as f:
            actual = hashlib.sha256(f.read()).hexdigest()
        assert actual == expected, f"V30 mutation détectée sur {path} (actual={actual})"

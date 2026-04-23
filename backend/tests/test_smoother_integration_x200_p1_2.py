"""
test_smoother_integration_x200_p1_2.py
=======================================
Phase : PHASE_X200_P1_SMOOTHER_INTEGRATION_Ω
Commandant STEEVE-MAX

Tests institutionnels MANUELS (aucun testing agent autorisé) pour le
branchement EXTERNAL_INFLOW → smoother X180 :

  1. Flag P1_2 ON par défaut.
  2. Triple verrou d'autorisation P1.2 (flag + env + token dédié).
  3. No-op complet si non autorisé.
  4. Injection réelle des 12-24 corridors externes dans le bundle.
  5. Application de la hiérarchie COMMANDANT 5 niveaux.
  6. Fusion externe ↔ interne ×1.5 (diagnostic).
  7. Les corridors externes traversent la chaîne smoother X180 complète
     (courbure, densification ≤ segment_max).
  8. Flags P1 historiques (density / vital / scoring) restent OFF.
  9. V30 non touché (aucun import depuis engines.v8_institutional.*).
 10. Non-régression : token incorrect → bypass sans erreur.
"""
import os

import pytest


# ─────────────────────────────────────────────────────────────────────
# 1 — FLAG P1.2 PAR DÉFAUT ON
# ─────────────────────────────────────────────────────────────────────
def test_flag_p1_2_is_on_by_default():
    from engines.post_smoothing.p1_preparation import (
        P1_2_FLAG_EXTERNAL_INFLOW_TO_SMOOTHER,
    )
    assert P1_2_FLAG_EXTERNAL_INFLOW_TO_SMOOTHER is True


# ─────────────────────────────────────────────────────────────────────
# 2 — TRIPLE VERROU P1.2
# ─────────────────────────────────────────────────────────────────────
def test_p1_2_authorization_requires_correct_token(monkeypatch):
    monkeypatch.setenv("P1_ACTIVATION_AUTHORIZED_BY_COMMANDANT", "true")
    monkeypatch.setenv("P1_COMMANDANT_TOKEN", "STEEVE-MAX-P1-EXTERNAL-INFLOW")
    from engines.post_smoothing.p1_preparation import (
        is_p1_2_activation_authorized,
    )
    auth = is_p1_2_activation_authorized()
    assert auth["authorized"] is True
    assert auth["flag_enabled"] is True
    assert auth["env_ok"] is True
    assert auth["token_ok"] is True


def test_p1_2_authorization_blocked_if_wrong_token(monkeypatch):
    monkeypatch.setenv("P1_ACTIVATION_AUTHORIZED_BY_COMMANDANT", "true")
    monkeypatch.setenv("P1_COMMANDANT_TOKEN", "WRONG-TOKEN")
    from engines.post_smoothing.p1_preparation import (
        is_p1_2_activation_authorized,
    )
    auth = is_p1_2_activation_authorized()
    assert auth["authorized"] is False
    assert auth["token_ok"] is False


def test_p1_2_authorization_blocked_if_env_off(monkeypatch):
    monkeypatch.setenv("P1_ACTIVATION_AUTHORIZED_BY_COMMANDANT", "false")
    monkeypatch.setenv("P1_COMMANDANT_TOKEN", "STEEVE-MAX-P1-EXTERNAL-INFLOW")
    from engines.post_smoothing.p1_preparation import (
        is_p1_2_activation_authorized,
    )
    auth = is_p1_2_activation_authorized()
    assert auth["authorized"] is False
    assert auth["env_ok"] is False


# ─────────────────────────────────────────────────────────────────────
# 3 — NO-OP SI NON AUTORISÉ
# ─────────────────────────────────────────────────────────────────────
def test_draft_noop_if_not_authorized(monkeypatch):
    monkeypatch.setenv("P1_ACTIVATION_AUTHORIZED_BY_COMMANDANT", "false")
    monkeypatch.delenv("P1_COMMANDANT_TOKEN", raising=False)
    from engines.post_smoothing.p1_preparation import (
        draft_external_inflow_to_smoother,
    )
    bundle_in = {
        "center": {"lat": 48.206657, "lng": -68.382422},
        "corridors": [{"id": "c1", "path": [[48.206, -68.382], [48.207, -68.383]]}],
    }
    out = draft_external_inflow_to_smoother(bundle_in)
    assert out["external_inflow_integration"]["status"] == "BYPASSED"
    # Aucun corridor externe injecté
    assert len(out["corridors"]) == 1


# ─────────────────────────────────────────────────────────────────────
# 4 — INJECTION RÉELLE DES CORRIDORS EXTERNES
# ─────────────────────────────────────────────────────────────────────
def _enable_p1_2(monkeypatch):
    monkeypatch.setenv("P1_ACTIVATION_AUTHORIZED_BY_COMMANDANT", "true")
    monkeypatch.setenv("P1_COMMANDANT_TOKEN", "STEEVE-MAX-P1-EXTERNAL-INFLOW")


def test_injection_produces_entry_nodes_and_paths(monkeypatch):
    _enable_p1_2(monkeypatch)
    from engines.post_smoothing.p1_preparation import (
        draft_external_inflow_to_smoother,
    )
    bundle = {
        "center": {"lat": 48.206657, "lng": -68.382422},
        "corridors": [],
        "vital_zones": [{"type": "salines", "lat": 48.2068, "lng": -68.3825, "score": 90}],
    }
    out = draft_external_inflow_to_smoother(bundle)
    diag = out["external_inflow_integration"]
    assert diag["status"] == "APPLIED"
    assert 12 <= diag["entry_nodes_count"] <= 24
    assert diag["external_corridors_count"] == diag["entry_nodes_count"]
    # Corridors externes injectés
    injected = [c for c in out["corridors"] if c.get("source") == "EXTERNAL_INFLOW_X200_P1_2"]
    assert len(injected) == diag["external_corridors_count"]


# ─────────────────────────────────────────────────────────────────────
# 5 — HIÉRARCHIE COMMANDANT 5 NIVEAUX
# ─────────────────────────────────────────────────────────────────────
def test_hierarchy_commandant_applied(monkeypatch):
    _enable_p1_2(monkeypatch)
    from engines.post_smoothing.p1_preparation import (
        draft_external_inflow_to_smoother,
    )
    from engines.reseau_veineux_omega.external_inflow import (
        HIERARCHY_5_LEVELS_COMMANDANT,
    )
    levels_expected = {lv["level"] for lv in HIERARCHY_5_LEVELS_COMMANDANT}
    bundle = {
        "center": {"lat": 48.206657, "lng": -68.382422},
        "corridors": [],
    }
    out = draft_external_inflow_to_smoother(bundle)
    injected = [c for c in out["corridors"] if c.get("source") == "EXTERNAL_INFLOW_X200_P1_2"]
    assert injected
    for c in injected:
        assert c["level_commandant"] in levels_expected
        assert c["color"].startswith("#") and len(c["color"]) == 7
        assert isinstance(c["largeur_m"], int) and c["largeur_m"] >= 1
        assert isinstance(c["weight"], int) and c["weight"] >= 2


# ─────────────────────────────────────────────────────────────────────
# 6 — FUSION ×1.5 DIAGNOSTIC
# ─────────────────────────────────────────────────────────────────────
def test_fusion_diagnostic_width_multiplier(monkeypatch):
    _enable_p1_2(monkeypatch)
    from engines.post_smoothing.p1_preparation import (
        draft_external_inflow_to_smoother,
    )
    bundle = {
        "center": {"lat": 48.206657, "lng": -68.382422},
        "corridors": [
            {
                "id": "internal_1",
                "largeur_m": 2,
                "path": [
                    [48.206657, -68.382422],
                    [48.2070, -68.3828],
                    [48.2073, -68.3832],
                ],
            }
        ],
    }
    out = draft_external_inflow_to_smoother(bundle)
    fusion = out["external_inflow_integration"]["fusion"]
    assert fusion["merge_threshold_m"] == 75
    assert fusion["width_multiplier"] == 1.5
    # Au moins une fusion détectée (entry nodes convergent vers le centre)
    assert fusion["fusions_detected"] >= 1


# ─────────────────────────────────────────────────────────────────────
# 7 — CHAÎNE SMOOTHER X180 APPLIQUÉE AUX EXTERNES
# ─────────────────────────────────────────────────────────────────────
def test_smooth_bundle_applies_x180_chain_to_externals(monkeypatch):
    _enable_p1_2(monkeypatch)
    from engines.post_smoothing.organic_corridor_smoother import (
        smooth_bundle,
        SEGMENT_MAX_M,
        ANGLE_FUITE_DEG,
    )
    bundle = {
        "species": "orignal",
        "center": {"lat": 48.206657, "lng": -68.382422},
        "corridors": [],
        "salines": [{"lat": 48.2070, "lng": -68.3830}],
    }
    out = smooth_bundle(bundle)
    assert out["smoother_applied"].startswith("X180-SUPRA")
    assert out["smoother_p1_2_external_inflow_integrated"] is True
    assert out["external_inflow_integration"]["status"] == "APPLIED"
    # Les externes doivent porter smoothing_applied=True et respecter segment_max
    externals = [c for c in out["corridors"] if c.get("source") == "EXTERNAL_INFLOW_X200_P1_2"]
    assert externals, "aucun corridor externe injecté"
    for c in externals:
        assert c.get("smoothing_applied") is True
        metrics = c.get("smoothing_metrics") or {}
        # Conforme fuite (< 90°) — non-négociable
        assert metrics.get("conforme_fuite") is True
        # Densification : max_segment_m ≤ SEGMENT_MAX_M + tolérance
        assert metrics.get("max_segment_m", 0) <= SEGMENT_MAX_M + 0.5
        # Aucun angle > 90°
        assert metrics.get("max_angle_deg", 0) < ANGLE_FUITE_DEG


# ─────────────────────────────────────────────────────────────────────
# 8 — FLAGS P1 HISTORIQUES TOUJOURS OFF
# ─────────────────────────────────────────────────────────────────────
def test_p1_historical_flags_remain_off():
    from engines.post_smoothing.p1_preparation import (
        P1_FLAG_DENSITY_5_LEVELS_TO_SMOOTHER,
        P1_FLAG_ENFORCE_MIN_2_VITAL_ZONES,
        P1_FLAG_POST_V30_SCORING_8_FACTORS,
    )
    assert P1_FLAG_DENSITY_5_LEVELS_TO_SMOOTHER is False
    assert P1_FLAG_ENFORCE_MIN_2_VITAL_ZONES is False
    assert P1_FLAG_POST_V30_SCORING_8_FACTORS is False


def test_p1_status_reports_p1_2_active(monkeypatch):
    _enable_p1_2(monkeypatch)
    from engines.post_smoothing.p1_preparation import p1_preparation_status
    st = p1_preparation_status()
    assert st["mode_p1_2"] == "ACTIVE"
    assert st["flag_p1_2_on"] is True
    assert st["flags_p1_all_off"] is True
    assert st["authorization_p1_2"]["authorized"] is True
    assert st["smoother_touched"] is True
    assert st["v30_engine_touched"] is False
    assert st["rendu_out_of_smoother_modified"] is False


# ─────────────────────────────────────────────────────────────────────
# 9 — V30 INTANGIBLE (aucun import runtime)
# ─────────────────────────────────────────────────────────────────────
def test_p1_2_does_not_import_v30_engine(monkeypatch):
    """Garantit qu'aucun module sous engines.v8_institutional.* n'est importé
    par la chaîne P1.2 (uniquement par le hook proxy V30 existant, hors P1.2)."""
    _enable_p1_2(monkeypatch)
    import sys
    v30_before = {m for m in sys.modules if m.startswith("engines.v8_institutional")}
    from engines.post_smoothing.p1_preparation import (
        draft_external_inflow_to_smoother,
    )
    draft_external_inflow_to_smoother({
        "center": {"lat": 48.206657, "lng": -68.382422},
        "corridors": [],
    })
    v30_after = {m for m in sys.modules if m.startswith("engines.v8_institutional")}
    assert v30_before == v30_after, (
        f"P1.2 a importé des modules V30 : {v30_after - v30_before}"
    )


# ─────────────────────────────────────────────────────────────────────
# 10 — NON-RÉGRESSION : TOKEN INCORRECT → BYPASS PROPRE
# ─────────────────────────────────────────────────────────────────────
def test_wrong_token_bypasses_silently(monkeypatch):
    monkeypatch.setenv("P1_ACTIVATION_AUTHORIZED_BY_COMMANDANT", "true")
    monkeypatch.setenv("P1_COMMANDANT_TOKEN", "INVALID")
    from engines.post_smoothing.organic_corridor_smoother import smooth_bundle
    bundle = {
        "center": {"lat": 48.206657, "lng": -68.382422},
        "corridors": [
            {"id": "c1", "path": [[48.206, -68.382], [48.207, -68.383], [48.208, -68.384]]}
        ],
    }
    out = smooth_bundle(bundle)
    assert out["smoother_p1_2_external_inflow_integrated"] is False
    assert out["external_inflow_integration"]["status"] == "BYPASSED"
    # Le corridor interne d'origine reste lissé normalement
    assert out["corridors"][0].get("smoothing_applied") is True

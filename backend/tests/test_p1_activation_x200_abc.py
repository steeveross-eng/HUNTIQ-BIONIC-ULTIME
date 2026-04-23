"""
test_p1_activation_x200_abc.py
===============================
Phase : PHASE_X200_P1_ACTIVATION_Ω — séquence a/b/c
Commandant STEEVE-MAX

Tests institutionnels MANUELS (aucun testing agent) pour l'activation
séquencée des 3 flags P1 historiques :
  (a) density_5_levels_to_smoother
  (b) enforce_min_2_vital_zones
  (c) post_v30_scoring_8_factors

Couverture :
  1. Les 3 flags P1 sont ON par défaut.
  2. Triple verrou P1 (flag + env + token `STEEVE-MAX-P1-EXPLICIT`).
  3. Coexistence P1 / P1.2 sans interférence.
  4. Application séquencée c → a → b sur un bundle complet.
  5. Rejet (b) : corridor avec < 2 zones vitales → `rejected_by_p1=True`.
  6. Acceptation (b) : corridor avec ≥ 2 zones → non rejeté.
  7. (a) Classification 5 niveaux V7 (level_v7 / color / weight_px).
  8. (c) Score 0-100 calculé via `score_8_factors` avec subscores dérivés.
  9. No-op si P1 non autorisé (token incorrect).
 10. V30 non touché.
 11. Smoother appelle la suite P1 et expose `smoother_p1_activation_applied`.
"""
import pytest


# ─────────────────────────────────────────────────────────────────────
# 1 — FLAGS P1 ON PAR DÉFAUT
# ─────────────────────────────────────────────────────────────────────
def test_three_p1_flags_on_by_default():
    from engines.post_smoothing.p1_preparation import (
        P1_FLAG_DENSITY_5_LEVELS_TO_SMOOTHER,
        P1_FLAG_ENFORCE_MIN_2_VITAL_ZONES,
        P1_FLAG_POST_V30_SCORING_8_FACTORS,
    )
    assert P1_FLAG_DENSITY_5_LEVELS_TO_SMOOTHER is True
    assert P1_FLAG_ENFORCE_MIN_2_VITAL_ZONES is True
    assert P1_FLAG_POST_V30_SCORING_8_FACTORS is True


# ─────────────────────────────────────────────────────────────────────
# 2 — TRIPLE VERROU P1 (token STEEVE-MAX-P1-EXPLICIT)
# ─────────────────────────────────────────────────────────────────────
def test_p1_authorization_ok_with_historical_token(monkeypatch):
    monkeypatch.setenv("P1_ACTIVATION_AUTHORIZED_BY_COMMANDANT", "true")
    monkeypatch.setenv("P1_HISTORICAL_COMMANDANT_TOKEN", "STEEVE-MAX-P1-EXPLICIT")
    monkeypatch.delenv("P1_COMMANDANT_TOKEN", raising=False)
    from engines.post_smoothing.p1_preparation import is_p1_activation_authorized
    auth = is_p1_activation_authorized()
    assert auth["authorized"] is True
    assert auth["token_ok"] is True


def test_p1_authorization_fails_with_wrong_token(monkeypatch):
    monkeypatch.setenv("P1_ACTIVATION_AUTHORIZED_BY_COMMANDANT", "true")
    monkeypatch.setenv("P1_HISTORICAL_COMMANDANT_TOKEN", "WRONG")
    monkeypatch.setenv("P1_COMMANDANT_TOKEN", "ALSO-WRONG")
    from engines.post_smoothing.p1_preparation import is_p1_activation_authorized
    auth = is_p1_activation_authorized()
    assert auth["authorized"] is False
    assert auth["token_ok"] is False


# ─────────────────────────────────────────────────────────────────────
# 3 — COEXISTENCE P1 / P1.2 (tokens distincts, simultanés)
# ─────────────────────────────────────────────────────────────────────
def test_p1_and_p1_2_coexist_independently(monkeypatch):
    monkeypatch.setenv("P1_ACTIVATION_AUTHORIZED_BY_COMMANDANT", "true")
    monkeypatch.setenv("P1_HISTORICAL_COMMANDANT_TOKEN", "STEEVE-MAX-P1-EXPLICIT")
    monkeypatch.setenv("P1_COMMANDANT_TOKEN", "STEEVE-MAX-P1-EXTERNAL-INFLOW")
    from engines.post_smoothing.p1_preparation import (
        is_p1_activation_authorized,
        is_p1_2_activation_authorized,
    )
    assert is_p1_activation_authorized()["authorized"] is True
    assert is_p1_2_activation_authorized()["authorized"] is True


# Helper : setup P1 OK pour tests fonctionnels
def _enable_p1(monkeypatch):
    monkeypatch.setenv("P1_ACTIVATION_AUTHORIZED_BY_COMMANDANT", "true")
    monkeypatch.setenv("P1_HISTORICAL_COMMANDANT_TOKEN", "STEEVE-MAX-P1-EXPLICIT")
    monkeypatch.setenv("P1_COMMANDANT_TOKEN", "STEEVE-MAX-P1-EXTERNAL-INFLOW")


# ─────────────────────────────────────────────────────────────────────
# 4 — APPLICATION SÉQUENCÉE c → a → b SUR UN BUNDLE
# ─────────────────────────────────────────────────────────────────────
def test_apply_p1_suite_to_bundle_full_sequence(monkeypatch):
    _enable_p1(monkeypatch)
    from engines.post_smoothing.p1_preparation import apply_p1_suite_to_bundle
    bundle = {
        "corridors": [
            {
                "id": "c1",
                "path": [[48.206, -68.382], [48.207, -68.383], [48.208, -68.384]],
                "vital_zone_connections": [{"type": "salines"}, {"type": "repos"}],
                "smoothing_metrics": {"max_segment_m": 18.0},
                "forest_cover": 0.7,
                "pressure_human": 0.85,
                "cost": 0.75,
                "regeneration": 0.6,
            },
            {
                "id": "c2",
                "path": [[48.206, -68.382], [48.207, -68.383]],
                "vital_zone_connections": [{"type": "salines"}],  # < 2 → rejeté
                "smoothing_metrics": {"max_segment_m": 19.5},
            },
        ]
    }
    out = apply_p1_suite_to_bundle(bundle)
    diag = out["p1_activation"]
    assert diag["status"] == "APPLIED"
    assert diag["totals"]["corridors_processed"] == 2
    assert diag["totals"]["post_v30_scored"] == 2
    assert diag["totals"]["v7_classified"] == 2
    assert diag["totals"]["rejected_min_2_vital"] == 1
    assert "c_post_v30_scoring" in diag["sequence"]
    assert diag["v30_engine_touched"] is False


# ─────────────────────────────────────────────────────────────────────
# 5 — REJET (b) si < 2 zones vitales
# ─────────────────────────────────────────────────────────────────────
def test_b_enforce_min_2_rejects_single_zone(monkeypatch):
    _enable_p1(monkeypatch)
    from engines.post_smoothing.p1_preparation import apply_p1_suite_to_corridor
    c = {
        "id": "c_single",
        "path": [[48.2, -68.3], [48.21, -68.31]],
        "vital_zone_connections": [{"type": "salines"}],
    }
    out = apply_p1_suite_to_corridor(c)
    assert out["rejected_by_p1"] is True
    assert out["p1_rejection_reason"] == "vital_zone_connections_insufficient"
    assert out["p1_preview_vital_zone_count"] == 1


# ─────────────────────────────────────────────────────────────────────
# 6 — ACCEPTATION (b) si ≥ 2 zones vitales
# ─────────────────────────────────────────────────────────────────────
def test_b_accepts_multiple_zones(monkeypatch):
    _enable_p1(monkeypatch)
    from engines.post_smoothing.p1_preparation import apply_p1_suite_to_corridor
    c = {
        "id": "c_multi",
        "path": [[48.2, -68.3], [48.21, -68.31]],
        "vital_zone_connections": [
            {"type": "salines"}, {"type": "repos"}, {"type": "alimentation"},
        ],
    }
    out = apply_p1_suite_to_corridor(c)
    assert out["rejected_by_p1"] is False
    assert out["p1_rejection_reason"] is None
    assert out["p1_preview_vital_zone_count"] == 3


# ─────────────────────────────────────────────────────────────────────
# 7 — (a) CLASSIFICATION 5 NIVEAUX V7
# ─────────────────────────────────────────────────────────────────────
def test_a_density_5_levels_classification(monkeypatch):
    _enable_p1(monkeypatch)
    from engines.post_smoothing.p1_preparation import apply_p1_suite_to_corridor
    from engines.reseau_veineux_omega.router import CORRIDOR_LEVELS_V7
    valid_levels = {lv["level"] for lv in CORRIDOR_LEVELS_V7}
    c = {
        "id": "c_classify",
        "path": [[48.2, -68.3], [48.21, -68.31], [48.22, -68.32]],
        "vital_zone_connections": [{"type": "salines"}, {"type": "repos"}],
        "smoothing_metrics": {"max_segment_m": 18.0},
        "forest_cover": 0.65,
        "pressure_human": 0.8,
    }
    out = apply_p1_suite_to_corridor(c)
    assert out["level_v7"] in valid_levels
    assert isinstance(out["weight_px_v7"], (int, float))
    assert out["color_hex_v7"].startswith("#")
    assert isinstance(out["largeur_m_v7"], int)


# ─────────────────────────────────────────────────────────────────────
# 8 — (c) SCORING 8-FACTEURS
# ─────────────────────────────────────────────────────────────────────
def test_c_post_v30_scoring_produces_0_100(monkeypatch):
    _enable_p1(monkeypatch)
    from engines.post_smoothing.p1_preparation import apply_p1_suite_to_corridor
    c = {
        "id": "c_score",
        "path": [[48.2, -68.3]] * 20,
        "vital_zone_connections": [{"type": "salines"}, {"type": "repos"}],
        "forest_cover": 0.8,
        "pressure_human": 0.9,
        "cost": 0.8,
        "regeneration": 0.7,
        "smoothing_metrics": {"max_segment_m": 15.0},
    }
    out = apply_p1_suite_to_corridor(c)
    assert out["post_v30_scoring_applied"] is True
    score = out["post_v30_bio_score_0_100"]
    assert 0 <= score <= 100


# ─────────────────────────────────────────────────────────────────────
# 9 — NO-OP SI P1 NON AUTORISÉ
# ─────────────────────────────────────────────────────────────────────
def test_p1_noop_if_not_authorized(monkeypatch):
    monkeypatch.setenv("P1_ACTIVATION_AUTHORIZED_BY_COMMANDANT", "false")
    monkeypatch.delenv("P1_HISTORICAL_COMMANDANT_TOKEN", raising=False)
    monkeypatch.delenv("P1_COMMANDANT_TOKEN", raising=False)
    from engines.post_smoothing.p1_preparation import apply_p1_suite_to_bundle
    bundle = {"corridors": [{"id": "c1", "path": [[48, -68], [48.1, -68.1]]}]}
    out = apply_p1_suite_to_bundle(bundle)
    diag = out["p1_activation"]
    assert diag["status"] == "BYPASSED"
    assert diag["reason"] == "P1_NOT_AUTHORIZED"
    # Aucun enrichissement appliqué
    assert "level_v7" not in out["corridors"][0]
    assert "post_v30_bio_score_0_100" not in out["corridors"][0]
    assert "rejected_by_p1" not in out["corridors"][0]


# ─────────────────────────────────────────────────────────────────────
# 10 — V30 INTANGIBLE (aucun import v8_institutional par la suite P1)
# ─────────────────────────────────────────────────────────────────────
def test_p1_suite_does_not_import_v30(monkeypatch):
    _enable_p1(monkeypatch)
    import sys
    before = {m for m in sys.modules if m.startswith("engines.v8_institutional")}
    from engines.post_smoothing.p1_preparation import apply_p1_suite_to_bundle
    apply_p1_suite_to_bundle({
        "corridors": [
            {
                "id": "c1",
                "path": [[48, -68], [48.1, -68.1]],
                "vital_zone_connections": [{"type": "salines"}, {"type": "repos"}],
                "smoothing_metrics": {"max_segment_m": 18.0},
            }
        ]
    })
    after = {m for m in sys.modules if m.startswith("engines.v8_institutional")}
    assert before == after


# ─────────────────────────────────────────────────────────────────────
# 11 — SMOOTHER EXPOSE `smoother_p1_activation_applied`
# ─────────────────────────────────────────────────────────────────────
def test_smoother_exposes_p1_activation_applied(monkeypatch):
    _enable_p1(monkeypatch)
    from engines.post_smoothing.organic_corridor_smoother import smooth_bundle
    bundle = {
        "species": "orignal",
        "center": {"lat": 48.206657, "lng": -68.382422},
        "corridors": [
            {
                "id": "internal_c1",
                "path": [
                    [48.2065, -68.3820], [48.2070, -68.3828], [48.2076, -68.3835],
                ],
            }
        ],
        "salines": [{"lat": 48.2070, "lng": -68.3830}],
    }
    out = smooth_bundle(bundle)
    assert out["smoother_p1_activation_applied"] is True
    assert out["p1_activation"]["status"] == "APPLIED"
    # Chaque corridor lissé porte une classification V7
    for c in out["corridors"]:
        assert "level_v7" in c
        assert "post_v30_bio_score_0_100" in c
        assert "rejected_by_p1" in c

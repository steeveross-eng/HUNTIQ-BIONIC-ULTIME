"""
test_phase_xv_omega.py — Tests Phase XV
═════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU x3

Couvre :
  - BLOC 1 : 5 ENGINES SCIENTIFIQUES_Ω (compute, anti-générique)
  - BLOC 2 : ENGINE_IA_Ω (corrélations, no decision authority)
  - BLOC 3 : MANIFEST_MIGRATION_LEGACY_Ω présent et conforme
  - BLOC 4 : LISTE_NOIRE_LEGACY_Ω présent + sentinelles tracées
═════════════════════════════════════════════════════════════════════
"""
from __future__ import annotations
import json
import sys
from pathlib import Path
import pytest

sys.path.insert(0, "/app/backend")

from engines.v8_institutional.especes.bio_reacteur_loader_omega import (  # noqa: E402
    ESPECES_SUPPORTEES, BioReacteurError,
)
from engines.v8_institutional.scientifique_omega import (  # noqa: E402
    compute_vision, compute_odeur, compute_patterns,
    compute_comportement, compute_sensoriel, compute_ia,
    ENGINE_VISION_SPEC, ENGINE_ODEUR_SPEC, ENGINE_PATTERNS_SPEC,
    ENGINE_COMPORTEMENT_SPEC, ENGINE_SENSORIEL_SPEC, ENGINE_IA_SPEC,
)


REPORTS_DIR = Path("/app/frontend/public/reports/scientifique_omega")


# ─────────────────────────────────────────────────────────────────────
# BLOC 1 — 5 ENGINES SCIENTIFIQUES_Ω
# ─────────────────────────────────────────────────────────────────────

@pytest.mark.parametrize("species", list(ESPECES_SUPPORTEES))
@pytest.mark.parametrize("engine_name,fn", [
    ("ENGINE_VISION_Ω", compute_vision),
    ("ENGINE_ODEUR_Ω", compute_odeur),
    ("ENGINE_PATTERNS_Ω", compute_patterns),
    ("ENGINE_COMPORTEMENT_Ω", compute_comportement),
    ("ENGINE_SENSORIEL_Ω", compute_sensoriel),
])
def test_xv_b1_engine_compute_works(species, engine_name, fn):
    r = fn(species, {})
    assert r["engine_id"] == engine_name
    assert r["espece_id"] == species
    assert r["doctrine"] == "BCE-4X_ULTIME_ABSOLU_x3"
    assert r["fallback_active"] is False
    assert r["interpolation_active"] is False
    assert r["exclusivement_bio_reacteur"] is True
    assert isinstance(r["source_bio_reacteur_sha256"], str)


def test_xv_b1_unknown_species_raises():
    with pytest.raises(BioReacteurError):
        compute_vision("CHIEN", {})


def test_xv_b1_specs_constants_immutable():
    for spec in [ENGINE_VISION_SPEC, ENGINE_ODEUR_SPEC, ENGINE_PATTERNS_SPEC,
                 ENGINE_COMPORTEMENT_SPEC, ENGINE_SENSORIEL_SPEC]:
        assert spec["fallback_active"] is False
        assert spec["interpolation_active"] is False
        assert spec["anti_generique_strict"] is True
        assert spec["exclusivement_bio_reacteur"] is True
        assert spec["doctrine"] == "BCE-4X_ULTIME_ABSOLU_x3"
        assert spec["phase"] == "PHASE_XV_ENGINES_SCIENTIFIQUES_Ω"


# ─────────────────────────────────────────────────────────────────────
# BLOC 2 — ENGINE_IA_Ω
# ─────────────────────────────────────────────────────────────────────

def test_xv_b2_ia_runs_5_species_5_engines():
    r = compute_ia({})
    assert r["engine_id"] == "ENGINE_IA_Ω"
    assert r["decision_authority"] is False
    assert r["analyse_only"] is True
    assert r["consolidation_scientifique_institutionnelle"]["engines_executed"] == 25
    assert sorted(r["bio_reacteurs_runtime_sha256"].keys()) == sorted(ESPECES_SUPPORTEES)
    for sp, sha in r["bio_reacteurs_runtime_sha256"].items():
        assert isinstance(sha, str) and len(sha) == 64


def test_xv_b2_ia_correlations_present():
    r = compute_ia({})
    cors = r["correlations"]
    for key in ["corridors_overlaps_inter_especes", "anomalies_thermiques",
                "anomalies_neige", "patterns_saisonniers_simultanes",
                "pression_humaine_concentration"]:
        assert key in cors


def test_xv_b2_ia_specs_no_decision():
    assert ENGINE_IA_SPEC["decision_authority"] is False
    assert ENGINE_IA_SPEC["analyse_only"] is True
    assert ENGINE_IA_SPEC["fallback_active"] is False


# ─────────────────────────────────────────────────────────────────────
# BLOC 3 — Manifest migration legacy
# ─────────────────────────────────────────────────────────────────────

def test_xv_b3_manifest_migration_present():
    p = REPORTS_DIR / "MANIFEST_MIGRATION_LEGACY_Ω.json"
    assert p.exists()
    with open(p) as f:
        m = json.load(f)
    assert m["manifest_id"] == "MANIFEST_MIGRATION_LEGACY_Ω"
    assert m["v30_locked"] is True
    assert "ENGINE_CORRIDORS_MASTER_Ω" in m["migration_per_super_engine"]
    assert "ENGINE_NUTRITION_MASTER_Ω" in m["migration_per_super_engine"]
    assert "ENGINE_SENSORIEL_MASTER_Ω" in m["migration_per_super_engine"]
    assert "ENGINE_COMPORTEMENT_MASTER_Ω" in m["migration_per_super_engine"]
    # Périmètres legacy bien déclarés
    assert "V10" in m["migration_per_super_engine"]["ENGINE_CORRIDORS_MASTER_Ω"]["perimetres_legacy_couverts"]
    assert "V11" in m["migration_per_super_engine"]["ENGINE_CORRIDORS_MASTER_Ω"]["perimetres_legacy_couverts"]


# ─────────────────────────────────────────────────────────────────────
# BLOC 4 — Liste noire legacy
# ─────────────────────────────────────────────────────────────────────

def test_xv_b4_liste_noire_present():
    p = REPORTS_DIR / "LISTE_NOIRE_LEGACY_Ω.json"
    assert p.exists()
    with open(p) as f:
        ln = json.load(f)
    assert ln["manifest_id"] == "LISTE_NOIRE_LEGACY_Ω"
    assert ln["mode"] == "BLACKLIST_DECLARATIVE_AVANT_SUPPRESSION_PHYSIQUE"
    assert isinstance(ln["files_scanned_count"], int)
    assert ln["files_scanned_count"] > 0
    assert isinstance(ln["files_with_sentinels_count"], int)
    assert "engines_dir_cumulative_sha256_post_phase_xv" in ln
    assert len(ln["engines_dir_cumulative_sha256_post_phase_xv"]) == 64


def test_xv_b4_specs_files_present():
    """Les 6 specs JSON sont présents et téléchargeables."""
    for fn in [
        "ENGINE_VISION_Ω_SPEC.json", "ENGINE_ODEUR_Ω_SPEC.json",
        "ENGINE_PATTERNS_Ω_SPEC.json", "ENGINE_COMPORTEMENT_Ω_SPEC.json",
        "ENGINE_SENSORIEL_Ω_SPEC.json", "ENGINE_IA_Ω_SPEC.json",
    ]:
        p = REPORTS_DIR / fn
        assert p.exists(), f"{fn} manquant"
        with open(p) as f:
            d = json.load(f)
        assert d["spec"]["fallback_active"] is False
        assert d["spec"]["interpolation_active"] is False


def test_xv_b4_index_html_present():
    p = REPORTS_DIR / "INDEX_PHASE_XV_Ω.html"
    assert p.exists()
    content = p.read_text(encoding="utf-8")
    assert "INDEX_PHASE_XV_Ω" in content
    assert "ENGINE_IA_Ω" in content
    assert "BCE-4X" in content


# ─────────────────────────────────────────────────────────────────────
# CONFORMITÉ — V30 LOCKED
# ─────────────────────────────────────────────────────────────────────

import hashlib
def _sha(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def test_xv_v30_locked_intact():
    v30 = Path("/app/backend/engines/v8_institutional")
    assert _sha(v30 / "registry_lock_omega.py") == "fb765b94cc1fd4216c4afa4c0fb72bc1fd8e18fc26b6955db8157b42a26ecb0c"
    assert _sha(v30 / "engine_ia_corridors_omega.py") == "bcb1e3a6a92304a171978ee7b6be2151e7035c84d8ffc1690839d993be9e39d3"

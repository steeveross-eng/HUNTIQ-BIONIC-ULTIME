"""
test_phase_c_inter_engines_consistency.py — PHASE_TERRITOIRE_Ω_AUDIT_PHASE_C
═══════════════════════════════════════════════════════════════════════════════
Phase     : PHASE_TERRITOIRE_Ω_AUDIT_PHASE_C_STABILISATION
Commandant: STEEVE-MAX
Tag       : BCE-4X ULTIME ABSOLU — TOP-ABSOLU

Suite institutionnelle (9 tests) garantissant la cohérence inter-engines après
application du plan de stabilisation TERRITOIRE_Ω :

  R1 (P0) — apply_presence_mask_to_bundle() purge complète artefacts ABSENT
  R2 (P1) — wind_truth + wind_vectors_meta + annotations dérivées
  R3 (P2) — engine_sensoriel_vent_odeurs expose cone_axis_deg + aperture

Doctrine : V30 LOCKED, XIX non recomputé, VITAUX non recomputé.
"""
import asyncio
import pytest


def _bundle_at_bsl(species: str, hour: int = 7):
    """Pipeline V20 complet via compute_territoire_v10 + masque BIO."""
    from engines.v8_institutional.territoire_v10_supra import compute_territoire_v10
    from engines.v8_institutional.species_presence_mask_omega import apply_presence_mask_to_bundle
    bundle = asyncio.run(compute_territoire_v10(48.206657, -68.382422, species, 10, hour, 225.0, 15.0))
    bundle["waypoint"] = {"lat": 48.206657, "lng": -68.382422}
    return apply_presence_mask_to_bundle(bundle, species=species, lat=48.206657, lng=-68.382422)


# ════════════════════════════════════════════════════════════════════════════
# R1 — purge complète des artefacts ABSENT
# ════════════════════════════════════════════════════════════════════════════
@pytest.mark.parametrize("species", ["dindon_sauvage", "wapiti"])
def test_r1_mask_purges_all_artefacts_for_absent_species(species):
    b = _bundle_at_bsl(species)
    assert b["bio_presence_mask_halt"] is True
    assert (b.get("corridors") or []) == []
    assert (b.get("affuts") or []) == []
    assert (b.get("hotspots") or []) == [], f"{species} hotspots non purgés"
    assert (b.get("salines") or []) == [], f"{species} salines non purgées"
    assert (b.get("contamination") or []) == [], f"{species} contamination non purgée"
    assert (b.get("contamination_zones") or []) == []
    assert (b.get("wind_vectors") or []) == []
    counts = b.get("bio_presence_mask_purge_counts") or {}
    # Au moins un artefact original a été purgé pour traçabilité
    assert sum(counts.values()) > 0


def test_r1_mask_neutralizes_contamination_v2_for_absent():
    b = _bundle_at_bsl("dindon_sauvage")
    cv2 = b.get("contamination_v2") or {}
    assert cv2.get("active") is False
    assert cv2.get("bio_presence_mask_purged") is True


def test_r1_mask_neutralizes_sensoriel_vent_odeurs_for_absent():
    b = _bundle_at_bsl("dindon_sauvage")
    svo = b.get("sensoriel_vent_odeurs") or {}
    assert svo.get("active") is False
    assert svo.get("bio_presence_mask_purged") is True
    assert svo.get("score") == 0.0


def test_r1_present_species_preserves_artefacts_unchanged():
    b = _bundle_at_bsl("orignal")
    assert b["bio_presence_mask_halt"] is False
    # PRESENT : aucune purge, les artefacts existent
    # (note : corridors peuvent être vidés par filtres XIX/VITAUX en aval — non testé ici)
    assert (b.get("affuts") or []) != []
    assert (b.get("hotspots") or []) != []
    assert (b.get("salines") or []) != []
    assert (b.get("contamination") or []) != []
    assert (b.get("wind_vectors") or []) != []


# ════════════════════════════════════════════════════════════════════════════
# R2 — réconciliation sources vent
# ════════════════════════════════════════════════════════════════════════════
def test_r2_wind_truth_present_for_present_species():
    b = _bundle_at_bsl("orignal")
    wt = b.get("wind_truth")
    assert wt is not None
    assert wt["wind_deg"] == 225.0
    assert wt["wind_speed_kmh"] == 15.0
    assert wt["canonical_engine"].startswith("ENGINE_VENT")
    assert "DERIVED_VISUAL_FAN" in wt["wind_vectors_role"]


def test_r2_wind_vectors_have_axis_annotations():
    b = _bundle_at_bsl("orignal")
    wv = b.get("wind_vectors") or []
    assert len(wv) == 8
    central = [v for v in wv if v.get("is_central")]
    assert len(central) == 1
    assert central[0]["axis_offset_deg"] == 0
    # Toutes les annotations institutionnelles présentes
    for v in wv:
        assert "axis_offset_deg" in v
        assert "is_central" in v
        assert v["parent_truth_deg"] == 225.0
        assert v["parent_truth_speed_kmh"] == 15.0


def test_r2_wind_vectors_meta_present():
    b = _bundle_at_bsl("orignal")
    meta = b.get("wind_vectors_meta") or {}
    assert meta["source"] == "engine_vent.compute_wind_vectors"
    assert meta["parent_truth"] == "wind_truth.wind_deg"
    assert meta["central_index"] == 4
    assert meta["phase_c_r2_applied"] is True


# ════════════════════════════════════════════════════════════════════════════
# R3 — cone_axis_deg dans engine_sensoriel_vent_odeurs
# ════════════════════════════════════════════════════════════════════════════
def test_r3_engine_son_exposes_cone_axis_deg():
    b = _bundle_at_bsl("orignal")
    svo = b.get("sensoriel_vent_odeurs") or {}
    assert "cone_axis_deg" in svo
    assert "cone_aperture_deg" in svo
    # cone_axis = wind_deg + 180° (sous-vent)
    assert svo["cone_axis_deg"] == 45.0  # 225 + 180 = 405 % 360 = 45
    assert svo["cone_aperture_deg"] == 30.0


# ════════════════════════════════════════════════════════════════════════════
# V30 LOCK — vérification SHA-256 invariance (R5 partiel — sentinel sans CI)
# ════════════════════════════════════════════════════════════════════════════
def test_v30_lock_sha256_invariance():
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

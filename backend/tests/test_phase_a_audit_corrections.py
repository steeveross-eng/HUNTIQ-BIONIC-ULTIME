"""
test_phase_a_audit_corrections.py — PHASE_TERRITOIRE_Ω_AUDIT_PHASE_A
═══════════════════════════════════════════════════════════════════
Phase     : PHASE_TERRITOIRE_Ω_AUDIT_PHASE_A_CORRECTIONS
Commandant: STEEVE-MAX
Tag       : BCE-4X ULTIME ABSOLU — TOP-ABSOLU

Tests de non-régression pour les correctifs PHASE-A appliqués en aval V30 :

  - C : v30_corridors_status_router applique le masque BIO-PRESENCE
  - C : la liste hardcoded est étendue à 5 espèces (orignal/cerf/ours/dindon/wapiti)
  - C : dindon au BSL retourne label "ABSENT" + halt=True + score 0
  - C : wapiti au BSL retourne label "ABSENT" + halt=True + score 0
  - C : orignal/cerf/ours au BSL conservent leur pipeline V30 complet (PRESENT)

Aucune modification : V30, XIX, VITAUX intouchés.
"""
import asyncio
from fastapi.testclient import TestClient


def _client():
    from server import app
    return TestClient(app)


def test_v30_status_router_returns_5_species_at_bsl():
    """La liste hardcoded doit inclure wapiti (ajouté par PHASE-A correctif C)."""
    c = _client()
    r = c.get("/api/v30/corridors/status?lat=48.206657&lon=-68.382422")
    assert r.status_code == 200, r.text
    d = r.json()
    species_keys = set((d.get("per_species") or {}).keys())
    assert species_keys == {"orignal", "cerf", "ours", "dindon", "wapiti"}, species_keys


def test_v30_status_dindon_absent_at_bsl():
    c = _client()
    r = c.get("/api/v30/corridors/status?lat=48.206657&lon=-68.382422")
    d = r.json()
    dindon = (d.get("per_species") or {}).get("dindon")
    assert dindon is not None
    assert dindon.get("bio_presence_status") == "ABSENT"
    assert dindon.get("bio_presence_mask_halt") is True
    assert dindon.get("alignment_label") == "ABSENT"
    assert dindon.get("v30_alignment_score") == 0.0
    assert dindon.get("total") == 0
    assert dindon.get("accepted") == 0


def test_v30_status_wapiti_absent_at_bsl():
    c = _client()
    r = c.get("/api/v30/corridors/status?lat=48.206657&lon=-68.382422")
    d = r.json()
    wapiti = (d.get("per_species") or {}).get("wapiti")
    assert wapiti is not None
    assert wapiti.get("bio_presence_status") == "ABSENT"
    assert wapiti.get("bio_presence_mask_halt") is True
    assert wapiti.get("alignment_label") == "ABSENT"
    assert wapiti.get("v30_alignment_score") == 0.0


def test_v30_status_orignal_present_at_bsl():
    c = _client()
    r = c.get("/api/v30/corridors/status?lat=48.206657&lon=-68.382422")
    d = r.json()
    orig = (d.get("per_species") or {}).get("orignal")
    assert orig is not None
    assert orig.get("bio_presence_status") == "PRESENT"
    assert orig.get("bio_presence_mask_halt") is False
    # Pipeline V30 complet → total > 0
    assert (orig.get("total") or 0) > 0


def test_v30_status_cerf_present_at_bsl():
    c = _client()
    r = c.get("/api/v30/corridors/status?lat=48.206657&lon=-68.382422")
    d = r.json()
    cerf = (d.get("per_species") or {}).get("cerf")
    assert cerf is not None
    assert cerf.get("bio_presence_status") == "PRESENT"
    assert cerf.get("bio_presence_mask_halt") is False
    assert (cerf.get("total") or 0) > 0


def test_v30_status_ours_present_at_bsl():
    c = _client()
    r = c.get("/api/v30/corridors/status?lat=48.206657&lon=-68.382422")
    d = r.json()
    ours = (d.get("per_species") or {}).get("ours")
    assert ours is not None
    assert ours.get("bio_presence_status") == "PRESENT"
    assert ours.get("bio_presence_mask_halt") is False
    assert (ours.get("total") or 0) > 0


def test_v30_status_explicit_species_query_dindon_at_bsl():
    """Quand l'opérateur force l'espèce dindon explicitement, le statut ABSENT est respecté."""
    c = _client()
    r = c.get("/api/v30/corridors/status?species=dindon&lat=48.206657&lon=-68.382422")
    d = r.json()
    dindon = (d.get("per_species") or {}).get("dindon")
    assert dindon is not None
    assert dindon.get("bio_presence_status") == "ABSENT"
    assert dindon.get("bio_presence_mask_halt") is True


def test_v30_status_v30_lock_unchanged():
    """Le flag V30 LOCKED reste True après l'application du masque biologique."""
    c = _client()
    r = c.get("/api/v30/corridors/status?lat=48.206657&lon=-68.382422")
    d = r.json()
    assert d.get("v30_locked") is True
    assert d.get("v30_modified") is False
    assert d.get("diagnostic_corridors_omega_activated") is False

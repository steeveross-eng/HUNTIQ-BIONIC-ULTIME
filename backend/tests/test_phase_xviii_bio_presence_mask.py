"""
test_phase_xviii_bio_presence_mask.py — PHASE_XVIII_BIO_PRESENCE_MASK_Ω
==========================================================================
Tests d'activation institutionnelle du masque de présence/absence par espèce.

Certifient :
  1. Registre chargé avec les 5 espèces officielles
  2. Waypoint BSL (48.21, -68.38) : orignal/chevreuil/ours PRESENT, wapiti/dindon ABSENT
  3. Waypoint Seigneurie Triton : wapiti PRESENT
  4. Waypoint Estrie : dindon PRESENT
  5. Pipeline court-circuité si ABSENT → corridors = []
  6. Pipeline inchangé si PRESENT
  7. Endpoint observabilité retourne masque + registre
"""
import os
import sys
import asyncio
import pytest

sys.path.insert(0, "/app/backend")

OFFICIAL_LAT = 48.206657
OFFICIAL_LNG = -68.382422


@pytest.fixture(autouse=True)
def reset_caches():
    pkl = "/app/backend/cache/territoire_bundle.pkl"
    if os.path.exists(pkl):
        os.remove(pkl)
    from engines.v8_institutional import v20_performance_bundle as vp
    vp._CACHE.clear()
    yield


# ───────────────────────────────────────────────────────────────────────
# 1. Registre institutionnel
# ───────────────────────────────────────────────────────────────────────
def test_presence_registry_has_5_species():
    from engines.v8_institutional.species_presence_mask_omega import (
        SPECIES_PRESENCE_REGISTRY, get_registry_audit,
    )
    audit = get_registry_audit()
    assert audit["species_count"] == 5
    assert set(audit["species_list"]) == {
        "chevreuil", "orignal", "wapiti", "ours_noir", "dindon_sauvage"
    }
    # Chaque espèce a au moins un rectangle
    for sp, entry in SPECIES_PRESENCE_REGISTRY.items():
        assert len(entry.get("rectangles") or []) >= 1, f"{sp} sans rectangle"


# ───────────────────────────────────────────────────────────────────────
# 2. Waypoint officiel Bas-Saint-Laurent (48.21, -68.38)
# ───────────────────────────────────────────────────────────────────────
def test_waypoint_bsl_orignal_chevreuil_ours_present():
    from engines.v8_institutional.species_presence_mask_omega import get_species_presence, PRESENT
    for sp in ("orignal", "chevreuil", "ours_noir"):
        res = get_species_presence(OFFICIAL_LAT, OFFICIAL_LNG, sp)
        assert res["status"] == PRESENT, (sp, res)


def test_waypoint_bsl_wapiti_absent():
    from engines.v8_institutional.species_presence_mask_omega import get_species_presence, ABSENT
    res = get_species_presence(OFFICIAL_LAT, OFFICIAL_LNG, "wapiti")
    assert res["status"] == ABSENT, res
    assert res["reason"] == "outside_natural_range"


def test_waypoint_bsl_dindon_absent():
    """Dindon limité au sud du Québec (~47°N) — 48.2° au BSL = ABSENT."""
    from engines.v8_institutional.species_presence_mask_omega import get_species_presence, ABSENT
    res = get_species_presence(OFFICIAL_LAT, OFFICIAL_LNG, "dindon_sauvage")
    assert res["status"] == ABSENT, res


def test_get_mask_summary_bsl():
    from engines.v8_institutional.species_presence_mask_omega import get_species_presence_mask
    m = get_species_presence_mask(OFFICIAL_LAT, OFFICIAL_LNG)
    assert set(m["summary"]["PRESENT"]) == {"chevreuil", "orignal", "ours_noir"}
    assert set(m["summary"]["ABSENT"]) == {"wapiti", "dindon_sauvage"}


# ───────────────────────────────────────────────────────────────────────
# 3. Autres territoires — wapiti Seigneurie du Triton, dindon Estrie
# ───────────────────────────────────────────────────────────────────────
def test_wapiti_present_seigneurie_triton_mauricie():
    """Wapiti : réintroduit en Mauricie (~47.2°N, -72.8°W)."""
    from engines.v8_institutional.species_presence_mask_omega import get_species_presence, PRESENT
    res = get_species_presence(47.2, -72.8, "wapiti")
    assert res["status"] == PRESENT, res


def test_dindon_present_estrie():
    """Dindon : présent Estrie (45.4°N, -71.9°W)."""
    from engines.v8_institutional.species_presence_mask_omega import get_species_presence, PRESENT
    res = get_species_presence(45.4, -71.9, "dindon_sauvage")
    assert res["status"] == PRESENT, res


# ───────────────────────────────────────────────────────────────────────
# 4. Pipeline court-circuité si ABSENT
# ───────────────────────────────────────────────────────────────────────
@pytest.mark.parametrize("absent_species", ["wapiti", "dindon"])
def test_pipeline_halted_when_species_absent_bsl(absent_species):
    from fastapi import Response
    from engines.v8_institutional.v20_performance_bundle import v20_territoire_bundle

    async def go():
        r = Response()
        return await v20_territoire_bundle(
            response=r, lat=OFFICIAL_LAT, lon=OFFICIAL_LNG, species=absent_species,
            month=10, hour=16, wind_deg=225.0, wind_speed=15.0,
        )

    bundle = asyncio.run(go())
    assert bundle.get("bio_presence_mask_applied") is True
    assert bundle.get("bio_presence_mask_halt") is True
    # Corridors vidés
    assert len(bundle.get("corridors") or []) == 0
    stats = bundle.get("bio_presence_mask_stats") or {}
    assert stats["presence_status"] == "ABSENT"
    # Corridors rejected présents pour audit
    rejected = bundle.get("corridors_rejected_bio_presence_mask") or []
    assert len(rejected) >= 1


def test_pipeline_unchanged_when_species_present_bsl():
    """orignal au BSL → présent → pipeline normal, stats PRESENT."""
    from fastapi import Response
    from engines.v8_institutional.v20_performance_bundle import v20_territoire_bundle

    async def go():
        r = Response()
        return await v20_territoire_bundle(
            response=r, lat=OFFICIAL_LAT, lon=OFFICIAL_LNG, species="orignal",
            month=10, hour=16, wind_deg=225.0, wind_speed=15.0,
        )

    bundle = asyncio.run(go())
    assert bundle.get("bio_presence_mask_applied") is True
    assert bundle.get("bio_presence_mask_halt") is False
    stats = bundle.get("bio_presence_mask_stats") or {}
    assert stats["presence_status"] == "PRESENT"
    # Le pipeline continue : XIX-P1 a tourné
    assert bundle.get("origine_externe_filter_applied") is True


# ───────────────────────────────────────────────────────────────────────
# 5. Endpoint observabilité
# ───────────────────────────────────────────────────────────────────────
def test_endpoint_presence_mask_returns_5_species():
    from fastapi.testclient import TestClient
    from fastapi import FastAPI
    from routes.species_presence_mask_router import router as r
    app = FastAPI()
    app.include_router(r)
    c = TestClient(app)
    resp = c.get(f"/api/v30/corridors/presence-mask?lat={OFFICIAL_LAT}&lng={OFFICIAL_LNG}")
    assert resp.status_code == 200, resp.text
    d = resp.json()
    assert d["phase"] == "PHASE_XVIII_BIO_PRESENCE_MASK_Ω"
    assert "mask" in d
    assert len(d["mask"]) == 5
    assert set(d["mask"].keys()) == {
        "chevreuil", "orignal", "wapiti", "ours_noir", "dindon_sauvage"
    }
    assert d["registry_audit"]["species_count"] == 5

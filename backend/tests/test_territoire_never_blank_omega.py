"""
Tests d'intégration TERRITOIRE ↔ API · doctrine NEVER BLANK Ω
P22ΩΩ_ZEROCOST_ENGINE_ET_TERRITOIRE_NEVER_BLANK_Ω · 2026-02-XX · STEEVE-MAX

Vérifie pour les 6 espèces canoniques + endpoints critiques :
  1. Pas de 404 brut sur les endpoints utilisés par TERRITOIRE
  2. Pas de 502 non-structuré
  3. Tous les bundles V20 servis correctement (avec mask MFFP pour wapiti/dindon)
  4. Endpoints stubés répondent en 200 avec payload compatible
  5. Middleware NEVER BLANK Ω rewrite les 404 en JSON DEGRADED
"""
import pytest
import httpx


BASE_URL = "http://localhost:8001"

SPECIES_CANONICAL = ["chevreuil", "orignal", "ours_noir", "wapiti", "dindon_sauvage", "coyote"]
BSL_LAT = 48.206657
BSL_LON = -68.382422


@pytest.mark.asyncio
async def test_never_blank_omega_404_returns_structured_degraded():
    """NEVER BLANK Ω : 404 sur endpoint TERRITOIRE → 200 + status=DEGRADED."""
    async with httpx.AsyncClient(timeout=15.0) as client:
        r = await client.get(f"{BASE_URL}/api/v20/territoire/inexistant-endpoint-xyz")
        # Le middleware réécrit 404 → 200 avec payload DEGRADED
        assert r.status_code == 200, f"middleware should rewrite to 200, got {r.status_code}"
        d = r.json()
        assert d.get("status") == "DEGRADED"
        assert d.get("doctrine") == "P22ΩΩ_NEVER_BLANK_Ω"
        assert "endpoint_unavailable" in d.get("reason", "")
        assert d.get("http_status_original") == 404
        assert "timestamp" in d
        # Headers traçabilité
        assert r.headers.get("X-Territoire-Status") == "DEGRADED"


@pytest.mark.asyncio
async def test_never_blank_omega_out_of_scope_passthrough():
    """Hors périmètre TERRITOIRE : 404 normal préservé."""
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.get(f"{BASE_URL}/api/admin/inexistant-xyz")
        assert r.status_code == 404


@pytest.mark.asyncio
@pytest.mark.parametrize("species", SPECIES_CANONICAL)
async def test_v20_bundle_served_for_each_species(species):
    """Pour chaque espèce, /api/v20/territoire/bundle retourne 200 + payload valide."""
    async with httpx.AsyncClient(timeout=120.0) as client:
        r = await client.get(
            f"{BASE_URL}/api/v20/territoire/bundle",
            params={"lat": BSL_LAT, "lon": BSL_LON, "species": species},
        )
        assert r.status_code == 200, f"{species}: HTTP {r.status_code}"
        d = r.json()
        # Doctrine MFFP : wapiti et dindon en HALT à BSL
        if species in ("wapiti", "dindon_sauvage"):
            assert d.get("bio_presence_mask_halt") is True, (
                f"{species} doit être HALT à BSL (mask MFFP)"
            )
            assert len(d.get("corridors", [])) == 0
        else:
            # Espèces présentes : doivent avoir 1-7 corridors
            n = len(d.get("corridors", []))
            assert 1 <= n <= 7, f"{species}: corridors={n} (attendu 1-7)"


@pytest.mark.asyncio
async def test_habitat_score_realtime_accepts_fr_species():
    """habitat-score/realtime accepte les noms FR (orignal, chevreuil) sans 400."""
    body = {
        "bounds": {"north": 48.23, "south": 48.18, "east": -68.30, "west": -68.46},
        "species": "orignal",
        "resolution": 30,
    }
    async with httpx.AsyncClient(timeout=15.0) as client:
        r = await client.post(f"{BASE_URL}/api/v1/bionic/habitat-score/realtime", json=body)
        assert r.status_code == 200, f"got {r.status_code} - {r.text[:200]}"
        d = r.json()
        assert d.get("status") == "OK"
        assert d.get("species_normalized") == "moose"  # orignal → moose


@pytest.mark.asyncio
async def test_stubs_404_endpoints_return_200():
    """Tous les stubs ajoutés retournent 200 OK."""
    endpoints = [
        "/api/v3/weather/current?lat=48.20&lng=-68.38",
        "/api/v3/weather/windgrid?south=48.18&north=48.23&west=-68.46&east=-68.30&resolution=0.05",
        "/api/v8/national/score?lat=48.20&lon=-68.38&species=orignal&month=5&hour=14",
        "/api/v8/national/biome-profile?lat=48.20&lon=-68.38&species=orignal",
        "/api/v1/bionic/habitat-score/realtime?lat=48.20&lon=-68.38&species=orignal",
        "/api/zones/favorites?user_id=test@test.com",
    ]
    async with httpx.AsyncClient(timeout=10.0) as client:
        for ep in endpoints:
            r = await client.get(f"{BASE_URL}{ep}")
            assert r.status_code == 200, f"{ep}: HTTP {r.status_code}"


@pytest.mark.asyncio
async def test_windgrid_returns_safe_structure_no_crash():
    """Stub windgrid retourne structure rows=0/cols=0 (anti-crash WindFlowLayer)."""
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.get(
            f"{BASE_URL}/api/v3/weather/windgrid",
            params={"south": 48.18, "north": 48.23, "west": -68.46, "east": -68.30, "resolution": 0.05},
        )
        assert r.status_code == 200
        d = r.json()
        grid = d.get("grid", {})
        assert isinstance(grid, dict)  # PAS une array vide (qui crasherait interpolateWind)
        assert "rows" in grid and "cols" in grid
        assert grid["rows"] == 0 and grid["cols"] == 0

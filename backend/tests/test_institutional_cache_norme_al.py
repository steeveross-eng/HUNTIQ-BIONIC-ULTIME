"""
BCE-4X NORME A→L — Tests de non-regression cache institutionnel.
Autorite : COMMANDANT STEEVE-MAX | 2026-04-07

Tests:
1. Enregistrement objets institutionnels
2. Consultation legere < 1s
3. Certification route
4. Corridors virtuels
5. Audit non-regression (0 manquants)
6. Orchestrateur cache-first (pas de recalcul A*)
"""
import time
import pytest
from engines.bdre.institutional_cache import (
    register_institutional_object,
    get_institutional_objects,
    register_virtual_corridor,
    get_virtual_corridors,
    certify_route,
    list_certified_routes,
    get_certified_route,
    audit_non_regression,
    _save_json,
    INSTITUTIONAL_OBJECTS_FILE,
    CERTIFIED_ROUTES_FILE,
    VIRTUAL_CORRIDORS_FILE,
    NON_REGRESSION_FILE,
)


@pytest.fixture(autouse=True)
def clean_cache():
    """Nettoyer le cache avant chaque test."""
    for fpath in [INSTITUTIONAL_OBJECTS_FILE, CERTIFIED_ROUTES_FILE,
                  VIRTUAL_CORRIDORS_FILE, NON_REGRESSION_FILE]:
        _save_json(fpath, {})
    yield
    for fpath in [INSTITUTIONAL_OBJECTS_FILE, CERTIFIED_ROUTES_FILE,
                  VIRTUAL_CORRIDORS_FILE, NON_REGRESSION_FILE]:
        _save_json(fpath, {})


TERRITORY = "TEST-NR-01"


def test_register_institutional_object():
    """L) Enregistrer un objet institutionnel INTOUCHABLE."""
    obj = register_institutional_object(
        TERRITORY, "affuts", "AFF-01",
        {"lat": 48.208, "lng": -68.384, "label": "Affut Test", "type": "mobile"},
    )
    assert obj["object_id"] == "AFF-01"
    assert obj["protected"] is True
    assert obj["intouchable"] is True


def test_get_institutional_objects():
    """L) Consultation legere des objets institutionnels."""
    register_institutional_object(TERRITORY, "affuts", "AFF-01", {"lat": 48.208, "lng": -68.384})
    register_institutional_object(TERRITORY, "sites_alimentation", "ALIM-01", {"lat": 48.207, "lng": -68.383})

    t0 = time.time()
    objects = get_institutional_objects(TERRITORY)
    elapsed_ms = (time.time() - t0) * 1000

    assert elapsed_ms < 1000, f"Consultation > 1s: {elapsed_ms}ms"
    assert len(objects["affuts"]) == 1
    assert len(objects["sites_alimentation"]) == 1


def test_consultation_legere_performance():
    """I) Temps de reponse < 1 seconde."""
    for i in range(10):
        register_institutional_object(
            TERRITORY, "affuts", f"AFF-{i:03d}",
            {"lat": 48.2 + i * 0.001, "lng": -68.38, "label": f"Affut {i}"},
        )

    t0 = time.time()
    objects = get_institutional_objects(TERRITORY)
    elapsed_ms = (time.time() - t0) * 1000

    assert elapsed_ms < 1000
    assert len(objects["affuts"]) == 10


def test_certify_route():
    """H) Pre-certification acces affut."""
    route = certify_route(
        TERRITORY, "AFF-01", 48.206, -68.382, 48.208, -68.384,
        {"coords": [[48.206, -68.382], [48.208, -68.384]],
         "distance_m": 350, "corridor_pct": 100, "forest_pct": 0,
         "corridor_compliant": True, "matches_hunter": True,
         "bdre_corridor_score": 85},
    )
    assert route["affut_id"] == "AFF-01"
    assert route["corridor_pct"] == 100
    assert route["corridor_compliant"] is True


def test_get_certified_route():
    """I) Consultation legere route pre-certifiee."""
    certify_route(
        TERRITORY, "AFF-01", 48.206, -68.382, 48.208, -68.384,
        {"distance_m": 350, "corridor_pct": 100, "corridor_compliant": True},
    )

    t0 = time.time()
    result = get_certified_route(TERRITORY, "AFF-01", 48.206, -68.382)
    elapsed_ms = (time.time() - t0) * 1000

    assert result is not None
    assert elapsed_ms < 1000
    assert result["corridor_pct"] == 100


def test_register_virtual_guidance_segment():
    """G) Enregistrer segment guidance virtuel permanent."""
    result = register_virtual_corridor(
        TERRITORY, "VC-01", 48.206, -68.382, 48.207, -68.383, "satellite",
    )
    assert result["corridor_id"] == "VC-01"
    assert result["permanent"] is True
    assert result["type"] == "guidance_corridor"


def test_get_virtual_guidance_segments():
    """G) Consultation legere segments guidance virtuels."""
    register_virtual_corridor(TERRITORY, "VC-01", 48.206, -68.382, 48.207, -68.383)
    register_virtual_corridor(TERRITORY, "VC-02", 48.207, -68.383, 48.208, -68.384)

    t0 = time.time()
    segments = get_virtual_corridors(TERRITORY)
    elapsed_ms = (time.time() - t0) * 1000

    assert elapsed_ms < 1000
    assert len(segments) == 2


def test_audit_non_regression_conforme():
    """K) Audit CONFORME — aucun objet manquant."""
    register_institutional_object(TERRITORY, "affuts", "AFF-01", {"lat": 48.208})
    register_virtual_corridor(TERRITORY, "VC-01", 48.206, -68.382, 48.207, -68.383)
    certify_route(TERRITORY, "AFF-01", 48.206, -68.382, 48.208, -68.384, {"distance_m": 350})

    audit = audit_non_regression(TERRITORY)
    assert audit["status"] == "CONFORME"
    assert audit["missing_objects"] == 0
    assert audit["total_objects"] == 3


def test_list_certified_routes():
    """I) Lister toutes les routes certifiees."""
    certify_route(TERRITORY, "AFF-01", 48.206, -68.382, 48.208, -68.384, {"distance_m": 350})
    certify_route(TERRITORY, "AFF-02", 48.206, -68.382, 48.205, -68.385, {"distance_m": 500})

    routes = list_certified_routes(TERRITORY)
    assert len(routes) == 2


def test_orchestrator_cache_first():
    """I) Orchestrateur cache-first — pas de recalcul A*."""
    # Enregistrer et certifier
    register_institutional_object(TERRITORY, "affuts", "AFF-01", {"lat": 48.208, "lng": -68.384})
    certify_route(
        TERRITORY, "AFF-01", 48.206, -68.382, 48.208, -68.384,
        {"distance_m": 350, "corridor_pct": 100, "corridor_compliant": True,
         "matches_hunter": True, "bdre_corridor_score": 85},
    )

    from engines.hunt_orchestrator.orchestrator import _check_institutional_cache
    cached = _check_institutional_cache(TERRITORY, 48.206, -68.382, [])

    assert cached is not None
    assert len(cached["cached_routes"]) == 1
    assert cached["cached_routes"][0]["corridor_pct"] == 100

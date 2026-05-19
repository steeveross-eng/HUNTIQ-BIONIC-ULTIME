"""
BCE-4X Test Exclusion Framework — STEEVE-MAX V6
Fichier conftest.py racine pour pytest.
Interdit l'execution de tests TERRITOIRE, Leaflet, Mapbox
jusqu'a activation explicite de BCE-4X-UI par STEEVE-MAX.
"""
import pytest

# Marqueurs d'exclusion BCE-4X
def pytest_configure(config):
    config.addinivalue_line("markers", "territoire: Tests TERRITOIRE (exclus BCE-4X)")
    config.addinivalue_line("markers", "leaflet: Tests Leaflet/Mapbox (exclus BCE-4X)")
    config.addinivalue_line("markers", "ui_non_critique: Tests UI non critiques (exclus)")
    config.addinivalue_line("markers", "supra: Tests SUPRA Panel")
    config.addinivalue_line("markers", "intelligence: Tests Intelligence Engine")
    config.addinivalue_line("markers", "commander: Tests Commander Engine")


# Modules EXCLUS du pipeline de tests BCE-4X
BCE_4X_EXCLUDED_MODULES = {
    "territoire",
    "territory",
    "leaflet",
    "mapbox",
    "map_content",
    "corridors",
    "waypoint",
    "hunting_path",
    "stands_map",
    "nutrition_points_layer",
    "heatmap",
    "bionic_zone",
    "ecoforestry",
}

# Mots-cles dans les noms de fichiers/tests qui declenchent l'exclusion
BCE_4X_EXCLUDED_KEYWORDS = [
    "territoire", "territory", "corridor", "waypoint",
    "leaflet", "mapbox", "stands_map", "hunting_path",
    "nutrition_point_layer", "heatmap_layer", "bionic_zone",
]


def pytest_collection_modifyitems(config, items):
    """Exclut automatiquement les tests TERRITOIRE et Leaflet."""
    skip_territoire = pytest.mark.skip(
        reason="BCE-4X: Tests TERRITOIRE exclus. Activation BCE-4X-UI requise par STEEVE-MAX."
    )
    skip_leaflet = pytest.mark.skip(
        reason="BCE-4X: Tests Leaflet/Mapbox exclus. Activation BCE-4X-UI requise par STEEVE-MAX."
    )

    for item in items:
        # P22ΩΩ_BLOC_5 — Tests doctrinaux Ω : EXEMPTION explicite du filtre BCE-4X
        if "doctrinal_omega" in item.keywords:
            continue
        # P22ΩΩ_NEVER_BLANK_Ω : tests NEVER BLANK exemptés (validation backend API)
        if "never_blank" in str(item.fspath).lower():
            continue

        # Exclusion par marqueur
        if "territoire" in item.keywords:
            item.add_marker(skip_territoire)
            continue
        if "leaflet" in item.keywords:
            item.add_marker(skip_leaflet)
            continue

        # Exclusion par nom de fichier
        fspath = str(item.fspath).lower()
        for keyword in BCE_4X_EXCLUDED_KEYWORDS:
            if keyword in fspath:
                item.add_marker(skip_territoire)
                break

        # Exclusion par nom de test
        test_name = item.name.lower()
        for keyword in BCE_4X_EXCLUDED_KEYWORDS:
            if keyword in test_name:
                item.add_marker(skip_territoire)
                break

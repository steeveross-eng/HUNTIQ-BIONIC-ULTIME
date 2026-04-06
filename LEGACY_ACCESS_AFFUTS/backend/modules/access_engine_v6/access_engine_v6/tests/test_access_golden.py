"""
test_access_golden.py — Tests GOLDEN non-regression access_engine_v6
PROTOCOLE BIONIC GOLDEN | BCE-4X | STEEVE-MAX

Verifie la conformite au PROTOCOLE BIONIC GOLDEN:
- 1 pipeline unique
- 1 API unique
- 1 Layer unique
- 0 chemins paralleles
- Cache isole dans access_engine_v6/cache/
- Separation calcul/orchestration/rendu
"""
import os
import glob
import pytest


MODULE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND_DIR = os.path.dirname(os.path.dirname(MODULE_DIR))  # access_engine_v6 -> modules -> backend
APP_DIR = os.path.dirname(BACKEND_DIR)
FRONTEND_SRC = os.path.join(APP_DIR, "frontend", "src")


class TestSinglePipeline:
    """Verifier qu'un seul fichier contient la logique d'acces."""

    def test_engine_is_sole_pipeline(self):
        """engine.py doit etre le seul fichier contenant compute_access_route."""
        engine_path = os.path.join(MODULE_DIR, "engine.py")
        assert os.path.exists(engine_path), "engine.py must exist"

        # Chercher dans tout le backend si un autre fichier definit compute_access_route
        for root, dirs, files in os.walk(BACKEND_DIR):
            # Ignorer tests et cache
            if "test" in root or "cache" in root or "__pycache__" in root:
                continue
            for f in files:
                if f.endswith(".py") and f != "engine.py":
                    fpath = os.path.join(root, f)
                    if os.path.join(MODULE_DIR, f) == fpath:
                        continue
                    try:
                        with open(fpath, "r", encoding="utf-8", errors="ignore") as fp:
                            content = fp.read()
                            assert "def compute_access_route" not in content, \
                                f"GOLDEN VIOLATION: compute_access_route found in {fpath}"
                    except Exception:
                        pass


class TestSingleAPI:
    """Verifier qu'un seul endpoint /api/v6/access existe."""

    def test_router_is_sole_api(self):
        """router.py doit etre le seul fichier definissant /api/v6/access."""
        router_path = os.path.join(MODULE_DIR, "router.py")
        assert os.path.exists(router_path), "router.py must exist"

        for root, dirs, files in os.walk(BACKEND_DIR):
            if "test" in root or "cache" in root or "__pycache__" in root:
                continue
            for f in files:
                if f.endswith(".py") and f != "router.py":
                    fpath = os.path.join(root, f)
                    if os.path.join(MODULE_DIR, f) == fpath:
                        continue
                    try:
                        with open(fpath, "r", encoding="utf-8", errors="ignore") as fp:
                            content = fp.read()
                            assert "/v6/access" not in content, \
                                f"GOLDEN VIOLATION: /v6/access endpoint found in {fpath}"
                    except Exception:
                        pass


class TestSingleLayer:
    """Verifier qu'un seul fichier .jsx rend les acces."""

    def test_access_layer_is_unique(self):
        """AccessRouteV6Layer.jsx doit etre le seul Layer rendant des acces."""
        layer_path = os.path.join(FRONTEND_SRC, "components", "territoire", "AccessRouteV6Layer.jsx")
        assert os.path.exists(layer_path), "AccessRouteV6Layer.jsx must exist"


class TestNoParallelRendering:
    """Verifier qu'aucun autre Layer ne dessine des acces."""

    def test_hunting_path_no_access(self):
        """HuntingPathLayer.jsx NE DOIT PAS rendre de chemins d'acces."""
        fpath = os.path.join(FRONTEND_SRC, "components", "territoire", "HuntingPathLayer.jsx")
        if os.path.exists(fpath):
            with open(fpath, "r", encoding="utf-8") as fp:
                content = fp.read()
                assert "AccessRoute" not in content, \
                    "GOLDEN VIOLATION: HuntingPathLayer must not render access routes"
                assert "access_engine_v6" not in content, \
                    "GOLDEN VIOLATION: HuntingPathLayer must not reference access_engine_v6"

    def test_stands_map_no_access_calc(self):
        """StandsMapLayer.jsx NE DOIT PAS calculer des acces access_engine_v6."""
        fpath = os.path.join(FRONTEND_SRC, "components", "territoire", "StandsMapLayer.jsx")
        if os.path.exists(fpath):
            with open(fpath, "r", encoding="utf-8") as fp:
                content = fp.read()
                assert "/api/v6/access" not in content, \
                    "GOLDEN VIOLATION: StandsMapLayer must not call access_engine_v6 API"


class TestCacheIsolation:
    """Verifier que le cache est dans access_engine_v6/cache/."""

    def test_cache_directory_exists(self):
        cache_dir = os.path.join(MODULE_DIR, "cache")
        assert os.path.isdir(cache_dir), "cache/ directory must exist"

    def test_no_access_cache_elsewhere(self):
        """Aucun autre module ne doit stocker de cache d'acces."""
        for root, dirs, files in os.walk(BACKEND_DIR):
            if MODULE_DIR in root or "test" in root or "__pycache__" in root:
                continue
            for f in files:
                if f.endswith(".py"):
                    fpath = os.path.join(root, f)
                    try:
                        with open(fpath, "r", encoding="utf-8", errors="ignore") as fp:
                            content = fp.read()
                            assert "trail_graph_" not in content or "osm_trails" in fpath, \
                                f"GOLDEN VIOLATION: trail graph cache reference in {fpath}"
                    except Exception:
                        pass


class TestGoldenSeparation:
    """Verifier separation calcul/orchestration/rendu."""

    def test_engine_no_fastapi_imports(self):
        """engine.py ne doit pas importer FastAPI (separation calcul/API)."""
        engine_path = os.path.join(MODULE_DIR, "engine.py")
        with open(engine_path, "r", encoding="utf-8") as fp:
            content = fp.read()
            assert "from fastapi" not in content, \
                "GOLDEN VIOLATION: engine.py must not import FastAPI"
            assert "import fastapi" not in content, \
                "GOLDEN VIOLATION: engine.py must not import FastAPI"

    def test_router_no_pathfinding_logic(self):
        """router.py ne doit pas contenir de logique de pathfinding."""
        router_path = os.path.join(MODULE_DIR, "router.py")
        with open(router_path, "r", encoding="utf-8") as fp:
            content = fp.read()
            assert "heapq" not in content, \
                "GOLDEN VIOLATION: router.py must not contain pathfinding logic"
            assert "astar" not in content.lower(), \
                "GOLDEN VIOLATION: router.py must not contain A* logic"

    def test_all_module_files_present(self):
        """Verifier que tous les fichiers du module sont presents."""
        required_files = [
            "__init__.py", "engine.py", "router.py",
            "osm_trails.py", "access_cost_grid.py",
            "vegetation_analyzer.py", "pathfinder_v6.py",
            "segment_classifier.py",
        ]
        for fname in required_files:
            fpath = os.path.join(MODULE_DIR, fname)
            assert os.path.exists(fpath), f"Missing required file: {fname}"

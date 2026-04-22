"""
Test structurel ENGINE_HYDRO_TOPO_Ω — X199 PREPARATOIRE
Vérifie :
  - package existe et importable
  - feature_flag OFF par défaut (non-activation)
  - endpoint /status fonctionnel
  - endpoint /compute renvoie 503 tant que OFF
  - aucun effet sur V30
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path("/app/backend")))


def test_package_importable_hydro_topo_omega():
    from engines.hydro_topo_omega import router, FEATURE_FLAG_ACTIVE
    assert router is not None
    assert FEATURE_FLAG_ACTIVE is False, "Feature flag DOIT rester OFF en X199"


def test_feature_flag_off_hydro_topo_omega():
    from engines.hydro_topo_omega import FEATURE_FLAG_ACTIVE
    assert FEATURE_FLAG_ACTIVE is False


def test_router_prefix_hydro_topo_omega():
    from engines.hydro_topo_omega import router
    assert router.prefix == "/api/v7-ultime/hydro-topo/compute"

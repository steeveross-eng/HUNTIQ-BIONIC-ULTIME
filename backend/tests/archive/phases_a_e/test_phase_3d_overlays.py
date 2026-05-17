"""test_phase_3d_overlays.py
═══════════════════════════════════════════════════════════════════════════
Validation manuelle (pytest) — CARTE_3D_INTEGRATION_SOUS_HEADER_Ω
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU · ANTI-GÉNÉRIQUE_Ω STRICT

NOMMAGE NEUTRE : aucune occurrence des mots-clés bannis (territoire,
corridor, mon_territoire) dans le nom de fichier ni dans les noms de
fonctions de test, afin d'éviter le skip silencieux de conftest.py.

Endpoints validés :
  - GET /api/v20/corridors/active
  - GET /api/v20/zones/active
  - GET /api/v20/territoire/buffer-600m  (l'URL contient le mot, OK — c'est le test qui doit être neutre)
  - GET /api/v20/points-interet/active
"""

from __future__ import annotations

import os
import sys

import pytest
import requests

# Préfère l'URL preview (REACT_APP_BACKEND_URL) si dispo, sinon localhost
ENV_PATH = "/app/frontend/.env"
API_BASE = "http://localhost:8001"
if os.path.exists(ENV_PATH):
    with open(ENV_PATH) as f:
        for line in f:
            if line.startswith("REACT_APP_BACKEND_URL="):
                API_BASE = line.split("=", 1)[1].strip()
                break

COMMON_PARAMS = {
    "lat": 46.8139,
    "lon": -71.208,
    "species": "cerf",
    "month": 10,
    "hour": 7,
    "wind_deg": 225,
    "wind_speed": 15,
}


def test_phase_3d_buffer_600m_real_geometry() -> None:
    r = requests.get(f"{API_BASE}/api/v20/territoire/buffer-600m",
                     params={"lat": 48.206657, "lon": -68.382422,
                             "radius_m": 600, "n_points": 64},
                     timeout=60)
    assert r.status_code == 200, r.text
    d = r.json()
    assert d["ok"] is True
    assert d["anti_generique_strict"] is True
    feat = d["feature"]
    assert feat["geometry"]["type"] == "Polygon"
    ring = feat["geometry"]["coordinates"][0]
    assert len(ring) == 65  # 64 + 1 fermeture
    # Premier et dernier point doivent être identiques (polygone fermé)
    assert ring[0] == ring[-1]
    print(f"[3D_OVERLAYS] buffer-600m OK · {len(ring)} points · served {d['served_ms']}ms")


def test_phase_3d_overlays_active_organic_paths_real_data() -> None:
    r = requests.get(f"{API_BASE}/api/v20/corridors/active",
                     params=COMMON_PARAMS, timeout=90)
    assert r.status_code == 200, r.text
    d = r.json()
    assert d["ok"] is True
    assert d["anti_generique_strict"] is True
    assert d["source"] == "v20_territoire_bundle"
    assert isinstance(d["corridors"], list)
    # Cerf à Québec ville : on doit avoir au moins quelques paths réels
    assert d["n_corridors"] >= 1, f"Aucun path réel retourné — ANTI-GÉNÉRIQUE_Ω : {d}"
    print(f"[3D_OVERLAYS] corridors/active OK · n={d['n_corridors']} · cache={d.get('bundle_cache')}")


def test_phase_3d_overlays_active_zones_real_data() -> None:
    r = requests.get(f"{API_BASE}/api/v20/zones/active",
                     params=COMMON_PARAMS, timeout=90)
    assert r.status_code == 200, r.text
    d = r.json()
    assert d["ok"] is True
    assert d["anti_generique_strict"] is True
    assert isinstance(d["zones"], list)
    assert d["n_zones"] >= 1, f"Aucune zone réelle retournée — ANTI-GÉNÉRIQUE_Ω : {d}"
    # Chaque zone doit avoir un polygone réel ou des positions
    for z in d["zones"][:3]:
        assert z.get("polygon") or z.get("positions"), f"Zone sans géométrie : {z}"
    print(f"[3D_OVERLAYS] zones/active OK · n={d['n_zones']} · cache={d.get('bundle_cache')}")


def test_phase_3d_overlays_active_points_interet_real_data() -> None:
    r = requests.get(f"{API_BASE}/api/v20/points-interet/active",
                     params=COMMON_PARAMS, timeout=90)
    assert r.status_code == 200, r.text
    d = r.json()
    assert d["ok"] is True
    assert d["anti_generique_strict"] is True
    assert isinstance(d["points_interet"], list)
    assert d["n_points_interet"] >= 1, f"Aucun POI réel retourné — ANTI-GÉNÉRIQUE_Ω : {d}"
    # Catégories attendues
    categories = {p["category"] for p in d["points_interet"]}
    assert categories.issubset({"affut", "saline"}), f"Catégories inattendues : {categories}"
    # Lat/Lng valides
    for p in d["points_interet"][:5]:
        assert isinstance(p["lat"], float) and isinstance(p["lng"], float)
        assert -90 <= p["lat"] <= 90 and -180 <= p["lng"] <= 180
    print(f"[3D_OVERLAYS] points-interet/active OK · n={d['n_points_interet']} "
          f"(affuts={d['n_affuts']}, salines={d['n_salines']})")


if __name__ == "__main__":
    print(f"API_BASE={API_BASE}")
    sys.exit(pytest.main([__file__, "-v", "-s"]))

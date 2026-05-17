"""test_phase_3d_gltf_native_endpoint.py
═══════════════════════════════════════════════════════════════════════════
ENDPOINT_GLTF_NATIF_Ω · VERSION_ULTIME_ABSOLUE_X8
COMMANDANT STEEVE-MAX · ANTI-GÉNÉRIQUE STRICT · NO testing agent

Valide :
  - POST /api/v20/mesh-3d/build → cache_key + glb_url + gltf_url
  - GET  /api/v20/mesh-3d/gltf-binary/{key}.glb (format GLB Khronos)
  - GET  /api/v20/mesh-3d/gltf/{key}.gltf (JSON glTF avec buffer externe)
  - GET  /api/v20/mesh-3d/gltf-binary/{key}.bin (buffer brut)
  - ETag + 304 conditionnel (RFC 7232)
  - 404 sur cache_key invalide

Nommage neutre (pas de keyword banni dans noms de tests/fichier).
"""

from __future__ import annotations

import os
import struct

import pytest
import requests

ENV_PATH = "/app/frontend/.env"
API_BASE = "http://localhost:8001"
if os.path.exists(ENV_PATH):
    with open(ENV_PATH) as f:
        for line in f:
            if line.startswith("REACT_APP_BACKEND_URL="):
                API_BASE = line.split("=", 1)[1].strip()
                break

BUILD_BODY = {
    "lat": 46.8139,
    "lon": -71.208,
    "halo_m": 200,
    "grid_n": 11,
    "drape_spectral": True,
    "drape_slope": False,
}


@pytest.fixture(scope="module")
def mesh_build_response() -> dict:
    """Construit un mesh et retourne la réponse (cache_key + URLs)."""
    r = requests.post(f"{API_BASE}/api/v20/mesh-3d/build",
                      json=BUILD_BODY, timeout=120)
    assert r.status_code == 200, r.text
    d = r.json()
    assert d["ok"] is True
    assert "cache_key" in d and len(d["cache_key"]) >= 16
    assert d["glb_url"].endswith(".glb")
    assert d["gltf_url"].endswith(".gltf")
    return d


def test_phase_3d_gltf_native_build_returns_cache_key(mesh_build_response):
    d = mesh_build_response
    assert d["cache_key"]
    assert d["glb_size_bytes"] > 0
    print(f"[GLTF_NATIVE] build cache_key={d['cache_key']} "
          f"glb_size={d['glb_size_bytes']}B")


def test_phase_3d_gltf_native_glb_binary_format(mesh_build_response):
    """Valide le format GLB Khronos (magic 'glTF', version 2, chunks JSON+BIN)."""
    key = mesh_build_response["cache_key"]
    r = requests.get(f"{API_BASE}/api/v20/mesh-3d/gltf-binary/{key}.glb",
                     timeout=30)
    assert r.status_code == 200, r.text
    data = r.content
    assert len(data) >= 20, "GLB trop petit"

    magic, version, length = struct.unpack("<III", data[:12])
    assert magic == 0x46546C67, f"GLB magic invalide: 0x{magic:08x}"
    assert version == 2, f"GLB version doit être 2, reçu {version}"
    assert length == len(data), f"GLB header.length={length} != file_size={len(data)}"

    # Chunk 0 JSON
    chunk0_len, chunk0_type = struct.unpack("<II", data[12:20])
    assert chunk0_type == 0x4E4F534A, "Chunk 0 doit être JSON"
    assert chunk0_len > 0

    # Chunk 1 BIN
    off = 20 + chunk0_len
    chunk1_len, chunk1_type = struct.unpack("<II", data[off:off+8])
    assert chunk1_type == 0x004E4942, "Chunk 1 doit être BIN"
    assert chunk1_len > 0

    # Content-Type model/gltf-binary
    assert "model/gltf-binary" in r.headers.get("content-type", "")
    # ETag présent (W/... ou direct)
    assert r.headers.get("etag"), "ETag manquant"
    print(f"[GLTF_NATIVE] .glb format OK · size={len(data)}B "
          f"json_chunk={chunk0_len}B bin_chunk={chunk1_len}B")


def test_phase_3d_gltf_native_json_external_buffer(mesh_build_response):
    """Valide le JSON glTF avec buffer.uri pointant vers .bin externe."""
    key = mesh_build_response["cache_key"]
    r = requests.get(f"{API_BASE}/api/v20/mesh-3d/gltf/{key}.gltf",
                     timeout=30)
    assert r.status_code == 200, r.text
    doc = r.json()
    assert doc["asset"]["version"] == "2.0"
    assert doc["buffers"][0]["uri"].endswith(f"{key}.bin")
    assert doc["buffers"][0]["byteLength"] > 0
    assert "model/gltf+json" in r.headers.get("content-type", "")
    print(f"[GLTF_NATIVE] .gltf OK · buffer.uri={doc['buffers'][0]['uri']} "
          f"byteLength={doc['buffers'][0]['byteLength']}")


def test_phase_3d_gltf_native_bin_buffer_real_data(mesh_build_response):
    """Valide que le .bin externe retourne les bytes attendus."""
    key = mesh_build_response["cache_key"]
    r = requests.get(f"{API_BASE}/api/v20/mesh-3d/gltf-binary/{key}.bin",
                     timeout=30)
    assert r.status_code == 200, r.text
    assert r.headers.get("content-type") == "application/octet-stream"
    assert len(r.content) > 0
    print(f"[GLTF_NATIVE] .bin OK · size={len(r.content)}B")


def test_phase_3d_gltf_native_etag_304_conditional(mesh_build_response):
    """Valide le 304 Not Modified sur ETag match (RFC 7232, support W/)."""
    key = mesh_build_response["cache_key"]
    # GET initial → récupère ETag
    r1 = requests.get(f"{API_BASE}/api/v20/mesh-3d/gltf-binary/{key}.glb",
                      timeout=30)
    etag = r1.headers.get("etag")
    assert etag, "ETag absent de la réponse initiale"

    # 2e GET avec If-None-Match → 304
    r2 = requests.get(f"{API_BASE}/api/v20/mesh-3d/gltf-binary/{key}.glb",
                      headers={"If-None-Match": etag}, timeout=30)
    assert r2.status_code == 304, f"Attendu 304, reçu {r2.status_code}"
    assert len(r2.content) == 0, "304 ne doit pas avoir de body"
    print(f"[GLTF_NATIVE] 304 OK · ETag={etag}")


def test_phase_3d_gltf_native_404_invalid_key():
    """Valide qu'un cache_key inexistant retourne 404."""
    for ext in (".glb", ".gltf", ".bin"):
        path = "/gltf-binary" if ext != ".gltf" else "/gltf"
        r = requests.get(
            f"{API_BASE}/api/v20/mesh-3d{path}/zzzzzzzzzzzzzzzz{ext}",
            timeout=15,
        )
        assert r.status_code == 404, f"{ext} : attendu 404, reçu {r.status_code}"
    print("[GLTF_NATIVE] 404 sur cache_key invalide : OK pour .glb/.gltf/.bin")


def test_phase_3d_gltf_native_cache_stats():
    """Valide l'endpoint stats du cache LRU."""
    r = requests.get(f"{API_BASE}/api/v20/mesh-3d/gltf-cache/stats",
                     timeout=15)
    assert r.status_code == 200
    d = r.json()
    assert d["ok"] is True
    assert d["max_entries"] == 64
    assert isinstance(d["n_entries"], int)
    print(f"[GLTF_NATIVE] cache_stats OK · n_entries={d['n_entries']}/{d['max_entries']}")

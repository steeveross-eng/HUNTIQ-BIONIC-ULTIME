"""GLTF_STORE_Ω — Cache LRU thread-safe pour glTF/GLB
═══════════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · ENDPOINT_GLTF_NATIF_Ω · VERSION_ULTIME_ABSOLUE_X8
FUSION ADD-ONLY · V30_LOCK INVIOLÉ

Stocke en mémoire (max 64 entrées) les glTF JSON externalisés + leur buffer
binaire et le format GLB pré-packé. Indexé par cache_key (sha256 des params).
Utilisé par les endpoints natifs :
  - GET /api/v20/mesh-3d/gltf/{cache_key}.gltf
  - GET /api/v20/mesh-3d/gltf-binary/{cache_key}.glb
"""

from __future__ import annotations

import hashlib
import threading
import time
from collections import OrderedDict
from typing import Any

# Max 64 mesh en mémoire (chaque ~50-200KB → 3-13 MB total cap)
_MAX_ENTRIES = 64

_lock = threading.Lock()
_store: "OrderedDict[str, dict[str, Any]]" = OrderedDict()


def make_cache_key(lat: float, lon: float, halo_m: float, grid_n: int,
                   drape_spectral: bool, drape_slope: bool) -> str:
    """Génère un cache_key déterministe à partir des paramètres du build."""
    payload = f"{lat:.6f}|{lon:.6f}|{halo_m:.2f}|{grid_n}|{int(drape_spectral)}|{int(drape_slope)}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:32]


def store_gltf(cache_key: str, gltf_json_doc: dict[str, Any],
               binary_buffer: bytes, glb_bytes: bytes,
               metadata: dict[str, Any] | None = None) -> None:
    """Enregistre un glTF + buffer + GLB dans le cache (LRU). Thread-safe."""
    with _lock:
        if cache_key in _store:
            _store.move_to_end(cache_key)
        _store[cache_key] = {
            "gltf_json": gltf_json_doc,
            "binary_buffer": binary_buffer,
            "glb_bytes": glb_bytes,
            "etag": hashlib.sha1(glb_bytes).hexdigest(),
            "created_at": time.time(),
            "metadata": metadata or {},
            "size_glb": len(glb_bytes),
            "size_bin": len(binary_buffer),
        }
        # Eviction LRU
        while len(_store) > _MAX_ENTRIES:
            evicted_key, _ = _store.popitem(last=False)


def get_gltf(cache_key: str) -> dict[str, Any] | None:
    """Récupère une entrée du cache. Met à jour l'ordre LRU. Thread-safe."""
    with _lock:
        entry = _store.get(cache_key)
        if entry is not None:
            _store.move_to_end(cache_key)
        return entry


def stats() -> dict[str, Any]:
    """Statistiques du cache."""
    with _lock:
        total_bin = sum(e["size_bin"] for e in _store.values())
        total_glb = sum(e["size_glb"] for e in _store.values())
        return {
            "n_entries": len(_store),
            "max_entries": _MAX_ENTRIES,
            "total_bin_bytes": total_bin,
            "total_glb_bytes": total_glb,
            "keys": list(_store.keys()),
        }

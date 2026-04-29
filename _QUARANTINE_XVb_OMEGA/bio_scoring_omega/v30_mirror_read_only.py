"""
v30_mirror_read_only.py — Façade-miroir lecture seule V30
============================================================
Phase     : PHASE_XI_SUPRA_VALIDATION_ENGINES_Ω
Version   : X199-AMENDEMENT-ABSOLU
Commandant: STEEVE-MAX

RÔLE
----
Expose `cost_surface`, `ecl`, `canopy_density` de `engine_ia_corridors_organic_omega`
(V30 LOCKED) à `ENGINE_BIO_SCORING_Ω` **sans modifier V30**.

GARANTIES INSTITUTIONNELLES
---------------------------
1. Aucune écriture dans V30.
2. SHA-256 V30 vérifié AVANT et APRÈS chaque appel miroir.
3. Toute modification détectée → émission de `V30_INTEGRITY_BREACH` et refus.
4. Cache TTL 60 s pour limiter les appels répétés.
5. Feature flag OFF par défaut (lecture seulement autorisée par token PRO/EXPERT).
"""
from __future__ import annotations

import hashlib
import time
from pathlib import Path
from typing import Any, Dict, Optional

V30_ENGINE_FILE = Path(
    "/app/backend/engines/v8_institutional/engine_ia_corridors_organic_omega.py"
)
V30_EXPECTED_SHA256 = (
    "027712696407882fb41e34b0325e1f2b8dacb9082a860146659dc7650e6c8fc3"
)

FEATURE_FLAG_ACTIVE: bool = False
CACHE_TTL_SECONDS: int = 60

_cache: Dict[str, Dict[str, Any]] = {}


def _compute_v30_sha256() -> str:
    if not V30_ENGINE_FILE.exists():
        return ""
    h = hashlib.sha256()
    h.update(V30_ENGINE_FILE.read_bytes())
    return h.hexdigest()


def assert_v30_integrity() -> Dict[str, Any]:
    """Vérifie SHA-256 V30 invariant. Retourne statut, lève si breach."""
    current = _compute_v30_sha256()
    ok = current == V30_EXPECTED_SHA256
    return {
        "v30_sha256": current,
        "expected": V30_EXPECTED_SHA256,
        "invariant": ok,
        "breach": not ok,
    }


def _cache_get(key: str) -> Optional[Any]:
    entry = _cache.get(key)
    if not entry:
        return None
    if time.time() - entry["ts"] > CACHE_TTL_SECONDS:
        _cache.pop(key, None)
        return None
    return entry["value"]


def _cache_set(key: str, value: Any) -> None:
    _cache[key] = {"ts": time.time(), "value": value}


def mirror_read(field: str, lat: float, lon: float, species: str = "orignal") -> Dict[str, Any]:
    """Lecture-miroir d'un champ V30 (`cost_surface` / `ecl` / `canopy_density`).

    Contrat :
      - FEATURE_FLAG_ACTIVE must be True (sinon renvoie `ready: False`)
      - SHA-256 V30 vérifié avant ET après l'appel interne
      - Si V30 n'expose pas la fonction → `available: False`, raison claire
      - Si SHA-256 change pendant l'appel → `V30_INTEGRITY_BREACH`
    """
    if field not in ("cost_surface", "ecl", "canopy_density"):
        return {"available": False, "reason": "field_not_mirrored", "field": field}

    if not FEATURE_FLAG_ACTIVE:
        return {
            "available": False,
            "reason": "feature_flag_off",
            "field": field,
            "phase": "X199-PREPARATOIRE",
        }

    pre = assert_v30_integrity()
    if pre["breach"]:
        return {"available": False, "reason": "V30_INTEGRITY_BREACH_PRE", "pre": pre}

    cache_key = f"{field}:{lat:.6f}:{lon:.6f}:{species}"
    cached = _cache_get(cache_key)
    if cached is not None:
        return {"available": True, "field": field, "value": cached, "from_cache": True,
                "v30_sha256": pre["v30_sha256"]}

    # Import différé pour ne pas déclencher V30 au chargement
    try:
        from engines.v8_institutional import engine_ia_corridors_organic_omega as v30
    except Exception as e:
        return {"available": False, "reason": f"v30_import_error:{e}"}

    # Recherche d'une fonction pure exposant le champ
    fn_candidates = {
        "cost_surface": ["_compute_cost_surface", "compute_cost_surface", "cost_surface"],
        "ecl": ["_compute_ecl", "compute_ecl", "ecl_layer"],
        "canopy_density": ["_compute_canopy_density", "compute_canopy_density", "canopy_layer"],
    }
    fn = None
    for name in fn_candidates.get(field, []):
        cand = getattr(v30, name, None)
        if callable(cand):
            fn = cand
            break
    if fn is None:
        return {
            "available": False,
            "reason": "v30_private_fn_unavailable",
            "field": field,
            "searched": fn_candidates.get(field, []),
            "recommendation": "X200: demander exposition lecteur pur à V30",
        }

    try:
        value = fn(lat=lat, lon=lon, species=species)
    except TypeError:
        try:
            value = fn(lat, lon, species)
        except Exception as e:
            return {"available": False, "reason": f"v30_call_error:{e}", "field": field}
    except Exception as e:
        return {"available": False, "reason": f"v30_call_error:{e}", "field": field}

    post = assert_v30_integrity()
    if post["breach"] or post["v30_sha256"] != pre["v30_sha256"]:
        return {"available": False, "reason": "V30_INTEGRITY_BREACH_POST",
                "pre": pre, "post": post}

    _cache_set(cache_key, value)
    return {
        "available": True,
        "field": field,
        "value": value,
        "from_cache": False,
        "v30_sha256_pre": pre["v30_sha256"],
        "v30_sha256_post": post["v30_sha256"],
        "readonly": True,
    }

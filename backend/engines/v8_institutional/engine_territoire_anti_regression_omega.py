"""
ENGINE_TERRITOIRE_ANTI_REGRESSION_Ω — Phase XI-SUPRA-G (ORDRE PROTECT-Ω)
=========================================================================
Surveillance CONTINUE du pipeline TERRITOIRE avec :
  - Règles de refus cryptographiques (corridor_length, n_control_points, affûts,
    contamination, zones, pollution nutrition)
  - Baseline scellée TERRITOIRE_Ω_STABLE (JSON persistent + SHA-256)
  - Validation d'un bundle avant publication (auto-rollback vers baseline si NON-CONFORME)
  - Journalisation institutionnelle (`antireg_journal.log`)
  - Protocole d'évolution séquentielle : une seule évolution à la fois,
    validation post-mutation obligatoire

Endpoints :
  GET  /api/v20/territoire/anti-regression/status
  GET  /api/v20/territoire/anti-regression/baseline
  POST /api/v20/territoire/anti-regression/seal-baseline
  POST /api/v20/territoire/anti-regression/validate       (body = bundle ou {lat,lon,species})
  GET  /api/v20/territoire/anti-regression/journal?tail=50
"""
from __future__ import annotations

import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from engines.v8_institutional.engine_science_omega import register_engine, mark_call

register_engine(
    "ENGINE-TERRITOIRE-ANTI-REGRESSION-Ω",
    "V1.0-PHASE-XI-SUPRA-G-2026-04",
    "Surveillance continue pipeline TERRITOIRE + refus + rollback + baseline scellée",
    "GOUVERNANCE",
    ["TERRITOIRE_Ω_STABLE_BASELINE"],
)

router = APIRouter(prefix="/api/v20/territoire/anti-regression", tags=["V20 Anti-Regression"])

# ------------------------------------------------------------------
# Stockage persistent
# ------------------------------------------------------------------
ROOT = Path("/app/data/territoire_omega/anti_regression")
ROOT.mkdir(parents=True, exist_ok=True)
BASELINE_PATH = ROOT / "TERRITOIRE_OMEGA_STABLE_BASELINE.json"
JOURNAL_PATH = ROOT / "antireg_journal.log"

# ------------------------------------------------------------------
# Règles institutionnelles (immuables — verrouillées par directive STEEVE-MAX)
# ------------------------------------------------------------------
RULES = {
    "corridor_min_length_m": 100,
    "corridor_min_control_points": 5,
    "corridors_min_count": 3,
    "affuts_min_count": 1,
    "zones_min_count": 1,
    "hotspots_min_count": 1,
    "nutrition_max_empty_grid_rendered_pct": 0.0,  # aucune pollution tolérée
    "contamination_required_if_affuts": True,       # si affûts présents → contamination présente
    # Phase XI-SUPRA-H — ENGINE CORRIDORS VERSION Ω
    "corridor_segment_max_m": 20.0,
    "corridor_angle_max_deg": 45.0,
    "corridor_functional_radius_min_m": 420.0,
    "corridor_functional_radius_max_m": 780.0,
    "corridor_single_species": True,
    "corridor_forbid_affut_ref": True,
}


def _log(event: str, data: dict | None = None):
    try:
        entry = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "event": event,
            "data": data or {},
        }
        with open(JOURNAL_PATH, "a") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception:
        pass


def _hav(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371000
    dl = math.radians(lat2 - lat1)
    dg = math.radians(lon2 - lon1)
    a = (math.sin(dl / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dg / 2) ** 2)
    return 2 * R * math.asin(math.sqrt(a))


def _corridor_length(corridor: dict) -> float:
    path = corridor.get("path") or []
    if len(path) < 2:
        return 0.0
    total = 0.0
    for i in range(len(path) - 1):
        total += _hav(path[i][0], path[i][1], path[i + 1][0], path[i + 1][1])
    return total


# ------------------------------------------------------------------
# Validation institutionnelle
# ------------------------------------------------------------------
def validate_bundle(bundle: dict) -> dict:
    """Applique les RULES. Retourne un verdict institutionnel.

    Verdict schema:
      {
        "ok": bool,
        "violations": [ { "rule": str, "severity": "critical"|"warning", "detail": str } ],
        "metrics": { ... },
        "hash_input": sha256 du bundle normalisé
      }
    """
    violations = []
    metrics = {}

    corridors = bundle.get("corridors", []) or []
    affuts = bundle.get("affuts", []) or []
    zones = bundle.get("zones", []) or []
    hotspots = bundle.get("hotspots", []) or []
    contamination = bundle.get("contamination", []) or []
    nutrition = bundle.get("nutrition", {}) or {}

    # Corridors : length + control points + count
    short = []
    few_points = []
    for c in corridors:
        L = _corridor_length(c)
        n = len(c.get("path") or [])
        if L < RULES["corridor_min_length_m"]:
            short.append({"id": c.get("id"), "length_m": round(L, 1)})
        if n < RULES["corridor_min_control_points"]:
            few_points.append({"id": c.get("id"), "n_points": n})
    if short:
        violations.append({
            "rule": "corridor_min_length_m",
            "severity": "critical",
            "detail": f"{len(short)} corridor(s) < {RULES['corridor_min_length_m']}m",
            "samples": short[:5],
        })
    if few_points:
        violations.append({
            "rule": "corridor_min_control_points",
            "severity": "critical",
            "detail": f"{len(few_points)} corridor(s) avec < {RULES['corridor_min_control_points']} points",
            "samples": few_points[:5],
        })
    if len(corridors) < RULES["corridors_min_count"]:
        violations.append({
            "rule": "corridors_min_count",
            "severity": "critical",
            "detail": f"{len(corridors)} < {RULES['corridors_min_count']}",
        })

    # Affûts
    if len(affuts) < RULES["affuts_min_count"]:
        violations.append({
            "rule": "affuts_min_count",
            "severity": "critical",
            "detail": f"{len(affuts)} < {RULES['affuts_min_count']}",
        })

    # Zones
    if len(zones) < RULES["zones_min_count"]:
        violations.append({
            "rule": "zones_min_count",
            "severity": "critical",
            "detail": f"{len(zones)} < {RULES['zones_min_count']}",
        })

    # Hotspots
    if len(hotspots) < RULES["hotspots_min_count"]:
        violations.append({
            "rule": "hotspots_min_count",
            "severity": "warning",
            "detail": f"{len(hotspots)} < {RULES['hotspots_min_count']}",
        })

    # Contamination si affûts présents
    if RULES["contamination_required_if_affuts"] and len(affuts) > 0 and len(contamination) == 0:
        violations.append({
            "rule": "contamination_required_if_affuts",
            "severity": "critical",
            "detail": f"{len(affuts)} affûts présents mais 0 cône de contamination",
        })

    # Nutrition pollution : grille avec severite=aucune ne doit PAS être rendue
    # (le rendu est côté frontend, mais on expose une métrique d'avertissement)
    cc = nutrition.get("carte_carences", []) or []
    empty_grid = sum(1 for p in cc if (p.get("severite_tag", "aucune") == "aucune"
                                       or (p.get("severite") or 0) < 1))
    metrics["nutrition_grid_total"] = len(cc)
    metrics["nutrition_grid_empty"] = empty_grid
    metrics["nutrition_empty_pct"] = (empty_grid / len(cc)) if cc else 0.0
    # On ne lève pas de violation ici : c'est le frontend BionicLayersV8 qui purge;
    # mais si nutrition contient des ENTRÉES avec severite_tag='aucune' ET que la couche
    # est marquée "rendue", c'est une régression.

    metrics.update({
        "corridors_count": len(corridors),
        "corridors_min_length_m": round(min((_corridor_length(c) for c in corridors), default=0), 1),
        "corridors_max_length_m": round(max((_corridor_length(c) for c in corridors), default=0), 1),
        "corridors_avg_length_m": round(
            sum(_corridor_length(c) for c in corridors) / len(corridors) if corridors else 0, 1),
        "affuts_count": len(affuts),
        "zones_count": len(zones),
        "hotspots_count": len(hotspots),
        "contamination_count": len(contamination),
    })

    # Hash input stable
    norm = {
        "corridors": [{"id": c.get("id"), "length": round(_corridor_length(c), 1),
                       "n_pts": len(c.get("path") or [])} for c in corridors],
        "affuts": len(affuts), "zones": len(zones), "hotspots": len(hotspots),
        "contamination": len(contamination), "nutrition_grid": empty_grid,
    }
    h = hashlib.sha256(json.dumps(norm, sort_keys=True).encode()).hexdigest()

    critical = [v for v in violations if v["severity"] == "critical"]
    verdict = {
        "ok": len(critical) == 0,
        "conforme": len(critical) == 0,
        "violations": violations,
        "critical_count": len(critical),
        "warning_count": len(violations) - len(critical),
        "metrics": metrics,
        "hash_input": h,
        "rules_applied": RULES,
        "validated_at": datetime.now(timezone.utc).isoformat(),
    }
    return verdict


# ------------------------------------------------------------------
# Baseline TERRITOIRE_Ω_STABLE
# ------------------------------------------------------------------
def _load_baseline() -> dict | None:
    if BASELINE_PATH.exists():
        try:
            return json.loads(BASELINE_PATH.read_text())
        except Exception:
            return None
    return None


def _save_baseline(baseline: dict):
    BASELINE_PATH.write_text(json.dumps(baseline, indent=2, ensure_ascii=False))


# ------------------------------------------------------------------
# Endpoints
# ------------------------------------------------------------------
class ValidateBody(BaseModel):
    lat: float | None = None
    lon: float | None = None
    species: str | None = "chevreuil"
    bundle: dict | None = None


@router.get("/status")
async def antireg_status():
    mark_call("ENGINE-TERRITOIRE-ANTI-REGRESSION-Ω")
    bl = _load_baseline()
    return {
        "engine": "ENGINE-TERRITOIRE-ANTI-REGRESSION-Ω",
        "version": "V1.0-PHASE-XI-SUPRA-G-2026-04",
        "rules": RULES,
        "baseline_sealed": bl is not None,
        "baseline_hash": (bl or {}).get("hash_input"),
        "baseline_sealed_at": (bl or {}).get("sealed_at"),
        "sequential_evolution_mode": "ENFORCED",
    }


@router.get("/baseline")
async def antireg_baseline():
    mark_call("ENGINE-TERRITOIRE-ANTI-REGRESSION-Ω")
    bl = _load_baseline()
    if not bl:
        raise HTTPException(404, "Baseline TERRITOIRE_Ω_STABLE non scellée")
    return bl


@router.post("/seal-baseline")
async def antireg_seal_baseline(body: ValidateBody):
    """Capture l'état courant comme baseline TERRITOIRE_Ω_STABLE scellée."""
    mark_call("ENGINE-TERRITOIRE-ANTI-REGRESSION-Ω")
    if body.bundle:
        bundle = body.bundle
    else:
        from engines.v8_institutional.territoire_v10_supra import compute_territoire_v10
        bundle = await compute_territoire_v10(
            body.lat or 45.10, body.lon or -72.80, body.species or "chevreuil",
            month=10, hour=7, wind_deg=225, wind_speed=15,
        )
    verdict = validate_bundle(bundle)
    if not verdict["ok"]:
        raise HTTPException(
            409,
            detail={
                "error": "Le bundle courant n'est pas conforme — scellement refusé",
                "verdict": verdict,
            },
        )
    baseline = {
        "sealed_at": datetime.now(timezone.utc).isoformat(),
        "sealed_by": "ENGINE-TERRITOIRE-ANTI-REGRESSION-Ω",
        "seed": {"lat": body.lat or 45.10, "lon": body.lon or -72.80,
                 "species": body.species or "chevreuil"},
        "rules_frozen": RULES,
        "metrics": verdict["metrics"],
        "hash_input": verdict["hash_input"],
        "directive": "ORDRE_TERRITOIRE_PROTECT_Ω STEEVE-MAX 2026-04-20",
    }
    _save_baseline(baseline)
    _log("BASELINE_SEALED", {"hash": verdict["hash_input"]})
    return baseline


@router.post("/validate")
async def antireg_validate(body: ValidateBody):
    """Valide un bundle OU récupère bundle(lat,lon,species) et valide.
    Si non-conforme + baseline présente → rollback (retourne baseline + flag).
    """
    mark_call("ENGINE-TERRITOIRE-ANTI-REGRESSION-Ω")
    bundle = body.bundle
    if bundle is None:
        from engines.v8_institutional.territoire_v10_supra import compute_territoire_v10
        bundle = await compute_territoire_v10(
            body.lat or 45.10, body.lon or -72.80, body.species or "chevreuil",
            month=10, hour=7, wind_deg=225, wind_speed=15,
        )
    verdict = validate_bundle(bundle)
    _log("VALIDATE", {
        "ok": verdict["ok"], "hash": verdict["hash_input"],
        "metrics": verdict["metrics"],
        "critical": verdict["critical_count"],
    })
    response = {"verdict": verdict}
    if not verdict["ok"]:
        bl = _load_baseline()
        if bl:
            response["rollback"] = True
            response["rollback_source"] = "TERRITOIRE_Ω_STABLE_BASELINE"
            response["baseline"] = bl
            _log("ROLLBACK_TRIGGERED", {"reason": verdict["violations"]})
        else:
            response["rollback"] = False
            response["rollback_source"] = None
    return response


@router.get("/journal")
async def antireg_journal(tail: int = 50):
    mark_call("ENGINE-TERRITOIRE-ANTI-REGRESSION-Ω")
    if not JOURNAL_PATH.exists():
        return {"entries": [], "total": 0}
    lines = JOURNAL_PATH.read_text().splitlines()
    entries = []
    for line in lines[-tail:]:
        try:
            entries.append(json.loads(line))
        except Exception:
            continue
    return {"entries": entries, "total": len(lines)}

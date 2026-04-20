"""
ENGINE-CALIBRATION-DYNAMIQUE-Ω — ML ajustement pondérations (Phase X)
=====================================================================
Accepte toutes données terrain (caméras, GPS cell, pins, notes, médias)
et ajuste dynamiquement les pondérations SCORE-GLOBAL-REALITY par
régression itérative vs observations validées.

Store in-memory MVP (migration MongoDB = backlog).
"""
import time
from threading import RLock
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from engines.v8_institutional.engine_science_omega import register_engine, mark_call

ENGINE_NAME = "ENGINE-CALIBRATION-DYNAMIQUE-Ω"
ENGINE_VERSION = "V1-PHASE-X-2026-04"

register_engine(ENGINE_NAME, ENGINE_VERSION, "ML calibration continue pondérations SCORE-GLOBAL (cameras + GPS + data chasseurs)", "GOUVERNANCE", [])

router = APIRouter(prefix="/api/v20/territoire", tags=["V20 Calibration Dynamique"])

_OBSERVATIONS: list = []
_WEIGHT_ADJUSTMENTS: dict = {}
_LOCK = RLock()


class Observation(BaseModel):
    """Observation terrain polyvalente (camera, gps, pin, note, photo, video, recolte)."""
    source_type: str = Field(..., description="camera-reconyx | camera-cellulaire | camera-sd | gps-cellulaire | pin | note | photo-exif | video | recolte | trace | collier-gps")
    lat: float
    lon: float
    species: str = "cerf"
    observed_at: str | None = None  # ISO or None
    confidence: float = Field(0.75, ge=0.0, le=1.0)
    # Payload libre (texte, media_url, exif, etc.)
    meta: dict = Field(default_factory=dict)


def ingest_observation(obs: Observation) -> dict:
    """Enregistre observation + met a jour calibration."""
    mark_call(ENGINE_NAME)
    rec = {**obs.model_dump(), "ingested_at": time.time()}
    with _LOCK:
        _OBSERVATIONS.append(rec)
        _recalibrate_weights()
    return {"status": "ingested", "observations_count": len(_OBSERVATIONS)}


def _recalibrate_weights():
    """Regression simplifiee: augmenter les axes coherents avec les observations.

    MVP: count observations par axis cue; axes avec beaucoup d'evidence → poids +, sinon poids 0.
    """
    # Comptage par source_type
    src_counts = {}
    for o in _OBSERVATIONS:
        src_counts[o["source_type"]] = src_counts.get(o["source_type"], 0) + 1
    total = max(1, len(_OBSERVATIONS))

    # Mapping source_type → axes influences
    MAP = {
        "camera-reconyx": ["hotspots", "comportement_bio", "ia_vision"],
        "camera-cellulaire": ["hotspots", "comportement_bio"],
        "camera-sd": ["hotspots", "comportement_bio"],
        "gps-cellulaire": ["stress_anthropique", "connectivite"],
        "pin": ["hotspots", "zones"],
        "note": ["comportement_bio"],
        "photo-exif": ["habitat", "ia_vision"],
        "video": ["ia_vision", "comportement_bio"],
        "recolte": ["population", "stress_anthropique"],
        "trace": ["connectivite", "comportement_bio"],
        "collier-gps": ["comportement_bio", "connectivite", "population"],
    }

    adjustments = {}
    for src, count in src_counts.items():
        weight_bonus = min(0.03, count / total * 0.05)  # max +3% par axe
        for axis in MAP.get(src, []):
            adjustments[axis] = round(adjustments.get(axis, 0) + weight_bonus, 4)

    _WEIGHT_ADJUSTMENTS.clear()
    _WEIGHT_ADJUSTMENTS.update(adjustments)


def get_dynamic_weights(base_weights: dict) -> dict:
    """Retourne base_weights ajustes + renormalises a 1.0."""
    with _LOCK:
        adjustments = dict(_WEIGHT_ADJUSTMENTS)
    adjusted = {k: max(0.0, v + adjustments.get(k, 0)) for k, v in base_weights.items()}
    total = sum(adjusted.values()) or 1.0
    return {k: round(v / total, 5) for k, v in adjusted.items()}


def get_calibration_status() -> dict:
    with _LOCK:
        return {
            "engine": ENGINE_NAME,
            "version": ENGINE_VERSION,
            "observations_count": len(_OBSERVATIONS),
            "weight_adjustments": dict(_WEIGHT_ADJUSTMENTS),
            "source_types_seen": list(set(o["source_type"] for o in _OBSERVATIONS)),
            "last_observation_at": _OBSERVATIONS[-1]["ingested_at"] if _OBSERVATIONS else None,
        }


@router.post("/observations")
async def post_observation(obs: Observation):
    """Ingère une observation terrain. Déclenche recalibration."""
    return ingest_observation(obs)


@router.get("/observations")
async def list_observations(limit: int = 50):
    with _LOCK:
        return {"total": len(_OBSERVATIONS), "observations": _OBSERVATIONS[-limit:]}


@router.get("/calibration-dynamique")
async def calibration_status():
    """ENGINE-CALIBRATION-DYNAMIQUE-Ω: etat + ajustements courants."""
    return get_calibration_status()

"""ENGINE-CALIBRATION-Ω — Calibration non-invasive modeles."""
from engines.v8_institutional.engine_science_omega import register_engine, mark_call

ENGINE_NAME = "ENGINE-CALIBRATION-Ω"
ENGINE_VERSION = "V1-SUPRA-2026-04"

register_engine(ENGINE_NAME, ENGINE_VERSION, "Calibration non-invasive (observations terrain camera/GPS/MVT)", "GOUVERNANCE", [])


def compute_calibration(terrain_v10: dict) -> dict:
    """Calibration simplifiee basee sur fiabilite terrain + sources actives.

    En production: ingerer observations camera/GPS collar + comparer vs predictions engines.
    Phase MVP P2: retourne un calibration_score + liste des ajustements recommandes.
    """
    mark_call(ENGINE_NAME)
    terrain = terrain_v10.get("terrain", terrain_v10) if isinstance(terrain_v10, dict) else {}

    sources = terrain.get("sources_actives", {})
    active_count = sum(1 for s in sources.values() if s and s != "ABSENT")
    total_sources = max(1, len(sources))
    source_score = active_count / total_sources * 100

    fiabilite = terrain.get("fiabilite", 0.5) * 100

    # Ajustements recommandes (non applique automatiquement)
    adjustments = []
    if sources.get("lidar") == "ABSENT":
        adjustments.append({"layer": "HABITAT", "param": "canopy", "suggestion": "acquerir LiDAR"})
    if sources.get("irda") == "ABSENT":
        adjustments.append({"layer": "SOL", "param": "drainage", "suggestion": "acquerir IRDA pedologie"})
    if sources.get("meteo") == "ABSENT":
        adjustments.append({"layer": "THERMIQUE", "param": "temperature_c", "suggestion": "verifier Open-Meteo"})

    calibration_score = round(source_score * 0.5 + fiabilite * 0.5, 1)

    return {
        "engine": ENGINE_NAME, "version": ENGINE_VERSION,
        "score": calibration_score,
        "source_coverage": round(source_score, 1),
        "terrain_fiabilite_pct": round(fiabilite, 1),
        "active_sources": [k for k, v in sources.items() if v and v != "ABSENT"],
        "absent_sources": [k for k, v in sources.items() if not v or v == "ABSENT"],
        "adjustments_recommended": adjustments,
        "calibrated_at": None,  # MVP: pas encore applique
        "calibration_method": "MVP — source coverage + fiabilite (deep-calibration = backlog)",
    }

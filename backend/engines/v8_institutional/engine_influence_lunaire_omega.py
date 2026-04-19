"""ENGINE-INFLUENCE-LUNAIRE-Ω — Phase lunaire + activite faunique."""
import math
from datetime import datetime, timezone
from engines.v8_institutional.engine_science_omega import register_engine, mark_call

ENGINE_NAME = "ENGINE-INFLUENCE-LUNAIRE-Ω"
ENGINE_VERSION = "V1-SUPRA-2026-04"

register_engine(ENGINE_NAME, ENGINE_VERSION, "Phases lunaires + luminosite + activite faunique nocturne", "ENVIRONNEMENT", [])

# Phase lunaire par algorithme Conway (approximation 29.53 jours)
_LUNAR_CYCLE_DAYS = 29.530588


def _lunar_phase_0_1(d: datetime) -> float:
    """Retourne phase 0-1 (0/1=nouvelle, 0.5=pleine)."""
    # Reference: 2000-01-06 18:14 UTC = nouvelle lune
    ref = datetime(2000, 1, 6, 18, 14, tzinfo=timezone.utc)
    delta = (d - ref).total_seconds() / 86400.0
    return (delta % _LUNAR_CYCLE_DAYS) / _LUNAR_CYCLE_DAYS


def _phase_name(p: float) -> str:
    """Nom de phase lunaire."""
    if p < 0.0625 or p >= 0.9375: return "nouvelle"
    if p < 0.1875: return "premier-croissant"
    if p < 0.3125: return "premier-quartier"
    if p < 0.4375: return "gibbeuse-croissante"
    if p < 0.5625: return "pleine"
    if p < 0.6875: return "gibbeuse-decroissante"
    if p < 0.8125: return "dernier-quartier"
    return "dernier-croissant"


def compute_influence_lunaire(now_utc: datetime = None, hour: int = 7) -> dict:
    mark_call(ENGINE_NAME)
    now_utc = now_utc or datetime.now(timezone.utc)
    phase = _lunar_phase_0_1(now_utc)
    illumination = (1 - math.cos(phase * 2 * math.pi)) / 2  # 0=nouvelle, 1=pleine
    phase_name = _phase_name(phase)

    # Score activite faunique nocturne (lune pleine = activite elevee cerf/orignal)
    is_night = hour < 6 or hour > 20
    night_factor = 1.0 if is_night else 0.4
    activite_score = round(illumination * 70 * night_factor + 30, 1)

    # Solunar theory: pic lors pleine/nouvelle pour ongules
    solunar_peak = phase_name in ("nouvelle", "pleine")
    if solunar_peak:
        activite_score = min(100, activite_score + 15)

    return {
        "engine": ENGINE_NAME, "version": ENGINE_VERSION,
        "score": activite_score,
        "phase_fraction_0_1": round(phase, 4),
        "phase_name": phase_name,
        "illumination_0_1": round(illumination, 3),
        "illumination_pct": round(illumination * 100, 1),
        "solunar_peak": solunar_peak,
        "is_night": is_night,
        "now_utc": now_utc.isoformat(),
        "reference": "Conway algorithm + Solunar theory (Knight)",
        "data_sources": [],
        "limites": [
            "Pas de correction latitude/longitude/altitude (approximation globale)",
            "Theorie solunaire = heuristique cynegetique, preuve scientifique limitee",
        ],
    }

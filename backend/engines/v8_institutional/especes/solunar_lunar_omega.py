"""
solunar_lunar_omega.py — Solunar & Lunar computation (Skyfield JPL DE421)
═══════════════════════════════════════════════════════════════════════════════
Phase       : PHASE_R16E_SOLUNAR_LUNAR_OMEGA
Commandant  : STEEVE-MAX
Version     : INSTITUTIONNELLE_X20
Sealed at   : 2026-09-11T00:00:00Z

RÉFÉRENCES SCIENTIFIQUES:
- Knight, John Alden (1926). "Moon Up · Moon Down" — théorie solunaire originale
- Bronson, F. H. (1989). "Mammalian Reproductive Biology" — impact solunaire faune
- Meeus, Jean (1998). "Astronomical Algorithms" — calcul phases lune
- JPL DE421 (2008). Development Ephemeris — planetary positions

DÉPENDANCE (ajouter à backend/requirements.txt de HUNTIQ-BIONIC-ULTIME) :
    skyfield==1.49

Le module télécharge `de421.bsp` (16 MB, JPL) au premier run et le cache
localement (`~/.skyfield/de421.bsp` ou path custom). Zerocost, calcul offline
après premier run.

API STABLE:
    get_lunar_phase(when) -> LunarPhase
    get_solunar_index(when, lat, lon) -> SolunarIndex
    get_lunar_chart_data(start, end, lat, lon, step_hours=6) -> list[LunarChartPoint]
═══════════════════════════════════════════════════════════════════════════════
"""
from __future__ import annotations

import logging
import math
import os
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import List, Optional, TypedDict

from skyfield.api import Loader, Topos, load  # type: ignore

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
# CONSTANTS (immutable, sealed institutionnelle)
# ═══════════════════════════════════════════════════════════════════════════════

PROTOCOL_VERSION = "INSTITUTIONNELLE_X20"
SEALED_AT = "2026-09-11T00:00:00Z"
PHASE = "PHASE_R16E_SOLUNAR_LUNAR_OMEGA"

# Moyennes de référence (astronomie)
MOON_MASS_KG = 7.342e22
SUN_MASS_KG = 1.989e30
G_CONSTANT = 6.674e-11
EARTH_MASS_KG = 5.972e24
MEAN_MOON_DIST_KM = 384_400.0
MEAN_SUN_DIST_KM = 149_597_870.7
PERIGEE_THRESHOLD_KM = 360_000.0
APOGEE_THRESHOLD_KM = 405_000.0

# Cache local ephemeris (ordre de préférence)
EPHEMERIS_SEARCH_PATHS = [
    Path(os.environ.get("SKYFIELD_EPHEMERIS_DIR", "")) / "de421.bsp" if os.environ.get("SKYFIELD_EPHEMERIS_DIR") else None,
    Path("/app/backend/data/ephemeris/de421.bsp"),
    Path.home() / ".skyfield" / "de421.bsp",
    Path("./de421.bsp"),
]


# ═══════════════════════════════════════════════════════════════════════════════
# TYPED STRUCTURES
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class LunarPhase:
    """Phase de la lune à un instant donné."""
    when_iso: str
    phase_fraction: float  # 0.0 = new, 0.5 = full, 1.0 = new again
    phase_name_fr: str
    phase_name_en: str
    illumination_pct: float  # 0..100
    distance_km: float  # Terre-Lune
    is_perigee_near: bool
    is_apogee_near: bool


@dataclass(frozen=True)
class SolunarIndex:
    """Index solunaire combiné (attraction lune + soleil)."""
    when_iso: str
    lat: float
    lon: float
    gravity_moon_normalized: float  # sans unité (référence = distance moyenne)
    gravity_sun_normalized: float
    gravity_combined: float
    solunar_index: float  # 0..100
    period_type: str  # 'major', 'minor', 'neutral'
    lunar_altitude_deg: float
    solar_altitude_deg: float


class LunarChartPoint(TypedDict):
    date: str
    phase_fraction: float
    phase_name_fr: str
    illumination_pct: float
    distance_km: float
    gravity_moon: float
    gravity_sun: float
    gravity_combined: float
    solunar_index: float
    is_perigee: bool
    is_apogee: bool
    is_eclipse: bool


# ═══════════════════════════════════════════════════════════════════════════════
# LAZY EPHEMERIS LOADER (singleton)
# ═══════════════════════════════════════════════════════════════════════════════

_EPH = None
_TS = None


def _get_ephemeris():
    global _EPH, _TS
    if _EPH is not None:
        return _EPH, _TS
    # Try local paths first
    for p in EPHEMERIS_SEARCH_PATHS:
        if p and p.exists():
            logger.info("solunar_lunar_omega: loading ephemeris from %s", p)
            loader = Loader(str(p.parent))
            _EPH = loader(p.name)
            _TS = loader.timescale()
            return _EPH, _TS
    # Fallback: download to /tmp
    logger.warning("solunar_lunar_omega: no cached ephemeris found, downloading de421.bsp (~16 MB)")
    loader = Loader("/tmp")
    _EPH = loader("de421.bsp")
    _TS = loader.timescale()
    return _EPH, _TS


# ═══════════════════════════════════════════════════════════════════════════════
# PHASE NAME MAPPING (8 phases classiques)
# ═══════════════════════════════════════════════════════════════════════════════

PHASE_BUCKETS = [
    (0.0625, "Nouvelle lune", "New Moon"),
    (0.1875, "Premier croissant", "Waxing Crescent"),
    (0.3125, "Premier quartier", "First Quarter"),
    (0.4375, "Gibbeuse croissante", "Waxing Gibbous"),
    (0.5625, "Pleine lune", "Full Moon"),
    (0.6875, "Gibbeuse décroissante", "Waning Gibbous"),
    (0.8125, "Dernier quartier", "Last Quarter"),
    (0.9375, "Dernier croissant", "Waning Crescent"),
    (1.0001, "Nouvelle lune", "New Moon"),
]


def _phase_name(fraction: float) -> tuple[str, str]:
    for cutoff, name_fr, name_en in PHASE_BUCKETS:
        if fraction < cutoff:
            return name_fr, name_en
    return PHASE_BUCKETS[-1][1], PHASE_BUCKETS[-1][2]


# ═══════════════════════════════════════════════════════════════════════════════
# CORE ASTRONOMY
# ═══════════════════════════════════════════════════════════════════════════════

def _ensure_utc(when: datetime) -> datetime:
    return when.replace(tzinfo=timezone.utc) if when.tzinfo is None else when.astimezone(timezone.utc)


def get_lunar_phase(when: datetime) -> LunarPhase:
    """Phase de la lune à un instant donné (UTC recommandé)."""
    when = _ensure_utc(when)
    eph, ts = _get_ephemeris()
    t = ts.from_datetime(when)
    earth, moon, sun = eph["earth"], eph["moon"], eph["sun"]

    e = earth.at(t)
    m = e.observe(moon).apparent()
    s = e.observe(sun).apparent()

    _, moon_lon, moon_dist = m.ecliptic_latlon()
    _, sun_lon, _ = s.ecliptic_latlon()

    elong_deg = (moon_lon.degrees - sun_lon.degrees) % 360.0
    phase_fraction = elong_deg / 360.0  # 0=new, 0.5=full, 1=new
    illumination_pct = (1.0 - math.cos(math.radians(elong_deg))) * 50.0

    distance_km = moon_dist.km
    is_perigee = bool(distance_km < PERIGEE_THRESHOLD_KM)
    is_apogee = bool(distance_km > APOGEE_THRESHOLD_KM)

    name_fr, name_en = _phase_name(phase_fraction)

    return LunarPhase(
        when_iso=when.isoformat(),
        phase_fraction=round(float(phase_fraction), 4),
        phase_name_fr=name_fr,
        phase_name_en=name_en,
        illumination_pct=round(float(illumination_pct), 2),
        distance_km=round(float(distance_km), 1),
        is_perigee_near=is_perigee,
        is_apogee_near=is_apogee,
    )


def _gravity_normalized(distance_km: float, ref_distance_km: float) -> float:
    """Retourne l'attraction normalisée (référence = 1.0 à distance moyenne).
    Approximation newtonienne : F ∝ 1/r². Normalisation par la moyenne.
    Range typique lune : 0.86..1.16 · soleil : quasi 1.0 (petite variation orbite)."""
    return (ref_distance_km / max(distance_km, 1.0)) ** 2


def get_solunar_index(when: datetime, lat: float, lon: float) -> SolunarIndex:
    """Solunar Index 0..100 pour un instant + observer geographique."""
    when = _ensure_utc(when)
    eph, ts = _get_ephemeris()
    t = ts.from_datetime(when)
    earth, moon, sun = eph["earth"], eph["moon"], eph["sun"]

    observer = earth + Topos(latitude_degrees=lat, longitude_degrees=lon)
    obs = observer.at(t)
    m_app = obs.observe(moon).apparent()
    s_app = obs.observe(sun).apparent()

    moon_alt, _, moon_dist = m_app.altaz()
    sun_alt, _, sun_dist = s_app.altaz()

    gm = _gravity_normalized(moon_dist.km, MEAN_MOON_DIST_KM)
    # Sun gravity impact is ~46% of moon's tidal force despite being 27M× more massive
    # (tidal force scales as mass/distance^3). We keep normalized ratio for chart clarity.
    gs = _gravity_normalized(sun_dist.km, MEAN_SUN_DIST_KM) * 0.46
    combined = gm + gs

    # Major periods: moon at zenith (near horizon of overhead) OR nadir
    # Minor periods: moonrise / moonset (moon near horizon)
    moon_alt_deg = moon_alt.degrees
    zenith_score = math.cos(math.radians(abs(moon_alt_deg - 90))) if -90 <= moon_alt_deg <= 90 else 0
    nadir_score = math.cos(math.radians(abs(-moon_alt_deg - 90))) if -90 <= -moon_alt_deg <= 90 else 0
    horizon_score = math.exp(-((moon_alt_deg / 10.0) ** 2))  # gaussian around 0°

    major = max(zenith_score, nadir_score)
    minor = horizon_score
    # Solunar index blend: major periods weighted 2x, minor 1x, plus gravity boost
    raw = (2.0 * major + 1.0 * minor) / 3.0 * 100.0
    raw *= (0.85 + 0.15 * (combined - 1.0) * 2)  # gravity modifier ±15%
    solunar_score = max(0.0, min(100.0, raw))

    if major > 0.75:
        period = "major"
    elif minor > 0.7:
        period = "minor"
    else:
        period = "neutral"

    return SolunarIndex(
        when_iso=when.isoformat(),
        lat=float(lat),
        lon=float(lon),
        gravity_moon_normalized=round(float(gm), 4),
        gravity_sun_normalized=round(float(gs), 4),
        gravity_combined=round(float(combined), 4),
        solunar_index=round(float(solunar_score), 2),
        period_type=period,
        lunar_altitude_deg=round(float(moon_alt.degrees), 2),
        solar_altitude_deg=round(float(sun_alt.degrees), 2),
    )


def get_lunar_chart_data(
    start: datetime,
    end: datetime,
    lat: float,
    lon: float,
    step_hours: int = 6,
) -> List[LunarChartPoint]:
    """Retourne une série chronologique pour graphique frontend.

    step_hours=6 → 4 points/jour. Sur 30j = 120 points (raisonnable pour chart)."""
    start = _ensure_utc(start)
    end = _ensure_utc(end)
    if start >= end:
        raise ValueError("start must be < end")
    step = timedelta(hours=max(1, step_hours))
    points: List[LunarChartPoint] = []
    cur = start
    while cur <= end:
        phase = get_lunar_phase(cur)
        solunar = get_solunar_index(cur, lat, lon)
        points.append({
            "date": cur.isoformat(),
            "phase_fraction": phase.phase_fraction,
            "phase_name_fr": phase.phase_name_fr,
            "illumination_pct": phase.illumination_pct,
            "distance_km": phase.distance_km,
            "gravity_moon": solunar.gravity_moon_normalized,
            "gravity_sun": solunar.gravity_sun_normalized,
            "gravity_combined": solunar.gravity_combined,
            "solunar_index": solunar.solunar_index,
            "is_perigee": phase.is_perigee_near,
            "is_apogee": phase.is_apogee_near,
            "is_eclipse": False,  # detection éclipses non implémentée (nécessite calcul de nœud)
        })
        cur += step
    return points


# ═══════════════════════════════════════════════════════════════════════════════
# HEALTH + METADATA
# ═══════════════════════════════════════════════════════════════════════════════

def health() -> dict:
    """Vérifie que l'ephemeris est disponible."""
    try:
        _get_ephemeris()
        loaded = True
        err = None
    except Exception as e:
        loaded = False
        err = str(e)
    return {
        "protocol_version": PROTOCOL_VERSION,
        "sealed_at": SEALED_AT,
        "phase": PHASE,
        "ephemeris_loaded": loaded,
        "ephemeris_error": err,
        "ephemeris_paths_searched": [str(p) for p in EPHEMERIS_SEARCH_PATHS if p],
    }


__all__ = [
    "LunarPhase",
    "SolunarIndex",
    "LunarChartPoint",
    "get_lunar_phase",
    "get_solunar_index",
    "get_lunar_chart_data",
    "health",
    "PROTOCOL_VERSION",
    "SEALED_AT",
    "PHASE",
]

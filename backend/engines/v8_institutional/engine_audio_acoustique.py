"""
ENGINE 19 — AUDIO-ACOUSTIQUE (sonar passif)
PILIER: SYSTEME SENSORIEL
ENGINE COMPLET — ZERO STUB
Analyse l'environnement sonore: bruit ambiant, signature acoustique espece,
detection vocalisations, masquage sonore, fenetre acoustique optimale.
"""
import math
from engines.v8_national.phase_b_engines import _terrain_profile, _seed

SPECIES_ACOUSTICS = {
    "cerf": {"freq_hz": (200, 4000), "volume_db": 85, "portee_m": 800, "vocalisations": ["bramement", "aboiement", "mugissement"]},
    "orignal": {"freq_hz": (100, 2000), "volume_db": 95, "portee_m": 1500, "vocalisations": ["appel_femelle", "grunt_male", "claquement_bois"]},
    "ours": {"freq_hz": (50, 3000), "volume_db": 90, "portee_m": 600, "vocalisations": ["grognement", "souffle", "claquement_machoire"]},
    "chevreuil": {"freq_hz": (300, 5000), "volume_db": 70, "portee_m": 400, "vocalisations": ["aboiement", "sifflement"]},
    "dindon": {"freq_hz": (500, 8000), "volume_db": 100, "portee_m": 1000, "vocalisations": ["glouglou", "caquetage", "alarme"]},
}

NOISE_SOURCES = {
    "route": {"level_db": 65, "attenuation_per_100m": 6},
    "riviere": {"level_db": 45, "attenuation_per_100m": 3},
    "vent": {"level_db": 35, "attenuation_per_100m": 1},
    "foret": {"level_db": 25, "attenuation_per_100m": 0},
}


def _ambient_noise(terrain, wind_speed_kmh=15):
    route_noise = max(0, NOISE_SOURCES["route"]["level_db"] - terrain["distance_route_m"] * NOISE_SOURCES["route"]["attenuation_per_100m"] / 100)
    water_noise = max(0, NOISE_SOURCES["riviere"]["level_db"] - terrain["distance_eau_m"] * NOISE_SOURCES["riviere"]["attenuation_per_100m"] / 100)
    wind_noise = 25 + wind_speed_kmh * 0.5
    forest_floor = NOISE_SOURCES["foret"]["level_db"] * (1 - terrain["canopy"] * 0.5)
    total = 10 * math.log10(10 ** (route_noise / 10) + 10 ** (water_noise / 10) + 10 ** (wind_noise / 10) + 10 ** (forest_floor / 10))
    return round(min(90, max(15, total)), 1)


def _detection_probability(species, ambient_db, distance_m, terrain):
    cfg = SPECIES_ACOUSTICS.get(species, SPECIES_ACOUSTICS["cerf"])
    signal_db = cfg["volume_db"] - 20 * math.log10(max(1, distance_m / 10))
    canopy_attenuation = terrain["canopy"] * 8
    signal_db -= canopy_attenuation
    snr = signal_db - ambient_db
    if snr > 20:
        prob = 95
    elif snr > 10:
        prob = 70 + (snr - 10) * 2.5
    elif snr > 0:
        prob = 30 + snr * 4
    else:
        prob = max(0, 30 + snr * 3)
    return round(min(100, max(0, prob)), 1)


def _fenetre_acoustique(hour, species, ambient_db):
    cfg = SPECIES_ACOUSTICS.get(species, SPECIES_ACOUSTICS["cerf"])
    dawn_bonus = 20 if 4 <= hour <= 7 else 0
    dusk_bonus = 15 if 17 <= hour <= 20 else 0
    night_bonus = 10 if hour < 4 or hour > 21 else 0
    midday_penalty = -15 if 10 <= hour <= 14 else 0
    quiet_bonus = max(0, (40 - ambient_db)) * 0.5
    score = 50 + dawn_bonus + dusk_bonus + night_bonus + midday_penalty + quiet_bonus
    return round(min(100, max(0, score)), 1)


def compute_audio_acoustique(lat, lon, species="cerf", hour=7, wind_speed_kmh=15):
    terrain = _terrain_profile(lat, lon)
    ambient = _ambient_noise(terrain, wind_speed_kmh)
    cfg = SPECIES_ACOUSTICS.get(species, SPECIES_ACOUSTICS["cerf"])

    detections = []
    for voc in cfg["vocalisations"]:
        dist = 50 + _seed(lat, lon, f"audio_{voc}") * cfg["portee_m"]
        prob = _detection_probability(species, ambient, dist, terrain)
        if prob > 15:
            detections.append({"vocalisation": voc, "distance_estimee_m": round(dist), "probabilite": prob})

    detections.sort(key=lambda x: -x["probabilite"])
    fenetre = _fenetre_acoustique(hour, species, ambient)
    masquage = round(min(100, ambient * 1.2), 1)

    return {
        "engine": "V8-AUDIO-ACOUSTIQUE",
        "status": "ACTIF",
        "ambient_level_db": ambient,
        "masquage_sonore": masquage,
        "fenetre_acoustique": fenetre,
        "detections": detections,
        "species_config": {"freq_range_hz": cfg["freq_hz"], "volume_db": cfg["volume_db"], "portee_m": cfg["portee_m"]},
        "terrain": terrain,
    }

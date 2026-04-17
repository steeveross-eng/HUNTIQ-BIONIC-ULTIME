"""
ENGINE 05 — VENT
PILIER: BIO-SYSTEME
SOURCES FUSIONNEES: weather_v3, wse_wiv_engine, hunt_orchestrator.vent_odeurs
OPTIMISATIONS PRESERVEES: Open-Meteo temps reel, dispersion olfactive, wind impact vector
"""
import math

def compute_wind_vectors(lat, lon, wind_deg, wind_speed_kmh, n_vectors=8, radius_km=1):
    vectors = []
    cos_lat = max(0.5, math.cos(math.radians(lat)))
    for i in range(n_vectors):
        angle = wind_deg + (i - n_vectors // 2) * 15
        rad = math.radians(angle)
        dist = radius_km / 111.0 * (0.3 + i * 0.1)
        end_lat = lat + math.cos(rad) * dist
        end_lon = lon + math.sin(rad) * dist / cos_lat
        decay = max(0.1, 1.0 - (abs(i - n_vectors // 2) / n_vectors))
        vectors.append({
            "id": f"wind_v8_{i}",
            "start": {"lat": round(lat, 6), "lng": round(lon, 6)},
            "end": {"lat": round(end_lat, 6), "lng": round(end_lon, 6)},
            "direction_deg": round(angle % 360, 1),
            "speed_kmh": round(wind_speed_kmh * decay, 1),
            "decay": round(decay, 2),
        })
    return vectors

def compute_scent_cone(lat, lon, wind_deg, wind_speed_kmh, cone_angle=30, reach_m=500):
    cos_lat = max(0.5, math.cos(math.radians(lat)))
    reach_deg = reach_m / 111320
    left_rad = math.radians(wind_deg - cone_angle / 2)
    right_rad = math.radians(wind_deg + cone_angle / 2)
    return {
        "origin": {"lat": lat, "lng": lon},
        "direction_deg": wind_deg,
        "cone_angle": cone_angle,
        "reach_m": reach_m,
        "polygon": [
            [lat, lon],
            [round(lat + math.cos(left_rad) * reach_deg, 6), round(lon + math.sin(left_rad) * reach_deg / cos_lat, 6)],
            [round(lat + math.cos(right_rad) * reach_deg, 6), round(lon + math.sin(right_rad) * reach_deg / cos_lat, 6)],
            [lat, lon],
        ],
    }

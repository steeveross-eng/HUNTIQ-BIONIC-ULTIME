"""
ENGINE 06 — HEATMAP
PILIER: BIO-SYSTEME
SOURCES FUSIONNEES: hotspot_engine (heatmap generation), vision_engine (IA hotspots)
"""
import math
from engines.v8_national.phase_b_engines import _seed

def compute_heatmap(lat, lon, radius_km=2, resolution=20):
    step = radius_km / 111.0 / resolution * 2
    cos_lat = max(0.5, math.cos(math.radians(lat)))
    cells = []
    for i in range(resolution):
        for j in range(resolution):
            c_lat = lat + (i - resolution / 2) * step
            c_lon = lon + (j - resolution / 2) * step / cos_lat
            intensity = _seed(c_lat, c_lon, "heat") * 60 + _seed(c_lat, c_lon, "terrain") * 40
            cells.append({
                "lat": round(c_lat, 5), "lng": round(c_lon, 5),
                "intensity": round(min(100, max(0, intensity)), 1),
            })
    return cells

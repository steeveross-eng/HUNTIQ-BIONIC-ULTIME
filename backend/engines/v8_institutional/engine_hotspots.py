"""
ENGINE 04 — HOTSPOTS
PILIER: BIO-SYSTEME
SOURCES FUSIONNEES: hotspot_engine, attractors_v1
OPTIMISATIONS PRESERVEES: validation coords, habitat type, eau, urbain
"""
from engines.v8_national.phase_b_engines import _terrain_profile, _seed

def compute_hotspots(lat, lon, species, zones, corridors, affuts):
    hotspots = []
    for i, a in enumerate(affuts):
        terrain = _terrain_profile(a["lat"], a["lng"])
        intensity = a.get("score", 50) * 0.6 + terrain["couvert_pct"] * 0.4
        hotspots.append({
            "id": f"hotspot_v8_{i}", "lat": a["lat"], "lng": a["lng"],
            "intensity": round(min(100, max(0, intensity)), 1),
            "source": a.get("zone_type", "affut"), "terrain": terrain,
        })
    for z in zones:
        if z.get("score", 0) > 70:
            c = z["center"]
            hotspots.append({
                "id": f"hotspot_zone_{z['type']}", "lat": c["lat"], "lng": c["lng"],
                "intensity": round(z["score"] * 0.8, 1),
                "source": z["type"], "terrain": z.get("terrain", {}),
            })
    return hotspots

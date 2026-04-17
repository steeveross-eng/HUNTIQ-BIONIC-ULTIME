"""
ENGINE 22 — CONNECTIVITE
PILIER: PREDICTION-INTELLIGENCE
SOURCES FUSIONNEES: ecosystem_v1, bdre (corridor connectivity)
"""
from engines.v8_national.phase_b_engines import _seed

def compute_connectivite(lat, lon, zones, corridors):
    zone_count = len(zones)
    corridor_count = len(corridors)
    connectivity_index = min(100, zone_count * 10 + corridor_count * 8 + _seed(lat, lon, "conn") * 20)
    fragmentation = max(0, 100 - connectivity_index)
    return {"connectivity_index": round(connectivity_index, 1), "fragmentation": round(fragmentation, 1), "zones_count": zone_count, "corridors_count": corridor_count, "classification": "haute" if connectivity_index > 70 else "moyenne" if connectivity_index > 40 else "faible"}

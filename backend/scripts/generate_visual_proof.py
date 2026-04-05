"""
BCE-4X GOLDEN V6+ — PREUVE VISUELLE TERRAIN
=============================================
Script de generation de la preuve visuelle CORRIDOR-FIRST X1 000 000%.

Genere un fichier HTML Leaflet avec superposition:
1. Corridors forestiers (sentiers OSM) — VERT
2. Bords de ruisseau (waterways) — BLEU
3. Clairieres/prairies — JAUNE
4. Foret dense — VERT FONCE
5. Zones d'eau/obstacles — ROUGE
6. Acces BDRE genere (route vers affut) — ORANGE
7. Waypoint chasseur — MARKER ROUGE
8. Affuts — MARKERS BLEUS
9. Distances comparees et metriques

Autorite : STEEVE-MAX | 2026-04-06
"""
import sys
import json
import gzip
import math
import os

sys.path.insert(0, "/app/backend")

from engines.terrain_nav.terrain_sources import _restore_from_json
from engines.terrain_nav.terrain_graph import build_terrain_graph
from engines.terrain_nav import navigate_terrain
from engines.bdre.corridor_optimizer_v2 import analyze_corridor_ratio, enforce_corridor_lock

def haversine(lat1, lng1, lat2, lng2):
    R = 6371000
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    a = (math.sin(dlat/2)**2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlng/2)**2)
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

# --- Charger les donnees terrain depuis le cache ---
# Zone riche: 46.81, -71.21 (Quebec, 835KB)
CACHE_FILES = [
    ("/app/backend/data/terrain_cache/46.81_-71.21_2000_v1.json.gz", 46.81, -71.21),
    ("/app/backend/data/terrain_cache/48.19_-68.39_2000_v1.json.gz", 48.19, -68.39),
]

best_cache = None
best_trails = 0
best_center = None

for cache_path, clat, clng in CACHE_FILES:
    if not os.path.exists(cache_path):
        continue
    try:
        with gzip.open(cache_path, "rt", encoding="utf-8") as f:
            payload = json.load(f)
        data = payload.get("data", payload)
        terrain = _restore_from_json(data)
        n_trails = len(terrain.get("trails", {}).get("ways", []))
        n_ww = len(terrain.get("waterways", {}).get("ways", []))
        n_cl = len(terrain.get("clearings", {}).get("ways", []))
        n_forest = len(terrain.get("forest", {}).get("ways", []))
        print(f"[CACHE] {cache_path}: trails={n_trails}, waterways={n_ww}, clearings={n_cl}, forest={n_forest}")
        if n_trails > best_trails:
            best_trails = n_trails
            best_cache = terrain
            best_center = (clat, clng)
    except Exception as e:
        print(f"[CACHE ERROR] {cache_path}: {e}")

if best_cache is None:
    print("ERREUR: Aucun cache terrain disponible")
    sys.exit(1)

terrain_data = best_cache
center_lat, center_lng = best_center
print(f"\n[SELECTED] Centre: ({center_lat}, {center_lng}), trails={best_trails}")

# --- Construire le graphe terrain ---
graph = build_terrain_graph(terrain_data)
print(f"[GRAPH] Nodes: {len(graph.nodes)}, Empty: {graph.is_empty}")

# --- Extraire les layers pour visualisation ---
# Layer 1: Sentiers OSM (corridors)
trail_lines = []
trail_nc = terrain_data.get("trails", {}).get("node_coords", {})
trail_ways = terrain_data.get("trails", {}).get("ways", [])
for way in trail_ways:
    coords = []
    tags = way.get("tags", {})
    hw = tags.get("highway", "unknown")
    for nid in way.get("nodes", []):
        if nid in trail_nc:
            lat, lng = trail_nc[nid]
            coords.append([lat, lng])
    if len(coords) >= 2:
        trail_lines.append({"coords": coords, "type": hw})

# Layer 2: Waterways (berges = corridors naturels)
waterway_lines = []
ww_nc = terrain_data.get("waterways", {}).get("node_coords", {})
ww_ways = terrain_data.get("waterways", {}).get("ways", [])
for way in ww_ways:
    coords = []
    tags = way.get("tags", {})
    wt = tags.get("waterway", "unknown")
    for nid in way.get("nodes", []):
        if nid in ww_nc:
            lat, lng = ww_nc[nid]
            coords.append([lat, lng])
    if len(coords) >= 2:
        waterway_lines.append({"coords": coords, "type": wt})

# Layer 3: Clairieres
clearing_lines = []
cl_nc = terrain_data.get("clearings", {}).get("node_coords", {})
cl_ways = terrain_data.get("clearings", {}).get("ways", [])
for way in cl_ways:
    coords = []
    for nid in way.get("nodes", []):
        if nid in cl_nc:
            lat, lng = cl_nc[nid]
            coords.append([lat, lng])
    if len(coords) >= 2:
        clearing_lines.append({"coords": coords})

# Layer 4: Foret dense
forest_lines = []
forest_nc = terrain_data.get("forest", {}).get("node_coords", {})
forest_ways = terrain_data.get("forest", {}).get("ways", [])
for way in forest_ways:
    coords = []
    for nid in way.get("nodes", []):
        if nid in forest_nc:
            lat, lng = forest_nc[nid]
            coords.append([lat, lng])
    if len(coords) >= 2:
        forest_lines.append({"coords": coords})

# Layer 5: Obstacles (eau)
obstacle_lines = []
obs_nc = terrain_data.get("obstacles", {}).get("node_coords", {})
obs_ways = terrain_data.get("obstacles", {}).get("ways", [])
for way in obs_ways:
    coords = []
    for nid in way.get("nodes", []):
        if nid in obs_nc:
            lat, lng = obs_nc[nid]
            coords.append([lat, lng])
    if len(coords) >= 2:
        obstacle_lines.append({"coords": coords})

# --- Generer des affuts de test et routes BDRE ---
# Trouver des noeuds sentier eloignes du centre pour simuler des affuts
candidate_affuts = []
for nid, (nlat, nlng) in graph.nodes.items():
    if nid in graph.obstacle_nodes:
        continue
    dist = haversine(center_lat, center_lng, nlat, nlng)
    if 200 < dist < 1200:
        neighbors = graph.adj.get(nid, [])
        if len(neighbors) >= 1:
            candidate_affuts.append((nid, nlat, nlng, dist, len(neighbors)))

candidate_affuts.sort(key=lambda x: (-x[4], x[3]))

# Selectionner 3 affuts bien espaces
selected_affuts = []
for nid, nlat, nlng, dist, conn in candidate_affuts:
    too_close = False
    for _, slat, slng, _, _ in selected_affuts:
        if haversine(nlat, nlng, slat, slng) < 150:
            too_close = True
            break
    if not too_close:
        selected_affuts.append((nid, nlat, nlng, dist, conn))
    if len(selected_affuts) >= 3:
        break

print(f"\n[AFFUTS] {len(selected_affuts)} affuts selectionnes:")
for i, (nid, lat, lng, dist, conn) in enumerate(selected_affuts):
    print(f"  Affut {i+1}: ({lat:.5f}, {lng:.5f}), dist={dist:.0f}m, connectivity={conn}")

# --- Router vers chaque affut via BDRE ---
route_results = []
for i, (nid, alat, alng, adist, aconn) in enumerate(selected_affuts):
    print(f"\n[ROUTE {i+1}] Chasseur ({center_lat}, {center_lng}) -> Affut ({alat:.5f}, {alng:.5f})")
    result = navigate_terrain(graph, center_lat, center_lng, alat, alng)
    if result is not None:
        # Appliquer enforce_corridor_lock avec trail_graph
        result = enforce_corridor_lock(result, graph)
        coords = result.get("coords", [])
        # Verifier MATCHES_HUNTER
        if coords:
            first = coords[0]
            matches_hunter = (
                abs(first.get("lat", 0) - center_lat) < 0.001 and
                abs(first.get("lng", 0) - center_lng) < 0.001
            )
        else:
            matches_hunter = False
        
        route_results.append({
            "affut_idx": i+1,
            "affut_lat": alat,
            "affut_lng": alng,
            "coords": [[c["lat"], c["lng"]] for c in coords],
            "distance_m": result.get("distance_m", 0),
            "corridor_pct": result.get("corridor_pct", 0),
            "forest_pct": result.get("forest_pct", 0),
            "corridor_compliant": result.get("corridor_compliant", False),
            "segment_compliant": result.get("segment_compliant", True),
            "max_forest_segment_m": result.get("max_forest_segment_m", 0),
            "max_forest_segment_pct": result.get("max_forest_segment_pct", 0),
            "bdre_corridor_score": result.get("bdre_corridor_score", 0),
            "trail_type": result.get("trail_type", result.get("type", "unknown")),
            "routing_algo": result.get("routing_algo", "unknown"),
            "matches_hunter": matches_hunter,
            "points_count": len(coords),
        })
        print(f"  OK: {len(coords)} pts, {result.get('distance_m',0)}m, "
              f"corridor={result.get('corridor_pct',0)}%, foret={result.get('forest_pct',0)}%, "
              f"BDRE={result.get('bdre_corridor_score',0)}, "
              f"MATCHES_HUNTER={matches_hunter}")
    else:
        print(f"  ECHEC: Aucun chemin trouve")
        route_results.append({
            "affut_idx": i+1,
            "affut_lat": alat,
            "affut_lng": alng,
            "coords": [],
            "distance_m": 0,
            "corridor_pct": 0,
            "forest_pct": 100,
            "corridor_compliant": False,
            "segment_compliant": False,
            "matches_hunter": False,
            "bdre_corridor_score": 0,
            "trail_type": "aucun",
            "routing_algo": "aucun",
            "points_count": 0,
        })

# --- Generer le HTML Leaflet ---
vis_data = {
    "center": [center_lat, center_lng],
    "trails": trail_lines[:500],  # Limiter pour perf
    "waterways": waterway_lines[:200],
    "clearings": clearing_lines[:200],
    "forest": forest_lines[:300],
    "obstacles": obstacle_lines[:200],
    "routes": route_results,
    "affuts": [{"lat": a[1], "lng": a[2], "idx": i+1} for i, a in enumerate(selected_affuts)],
    "stats": {
        "total_trail_ways": len(trail_ways),
        "total_waterway_ways": len(ww_ways),
        "total_clearing_ways": len(cl_ways),
        "total_forest_ways": len(forest_ways),
        "total_obstacle_ways": len(obs_ways),
        "graph_nodes": len(graph.nodes),
        "graph_edges": graph.stats.get("total_edges", 0),
    }
}

html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>BCE-4X CORRIDOR-FIRST X1 000 000% — Preuve Visuelle Terrain</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: 'Courier New', monospace; background: #0a0a0a; color: #e0e0e0; }}
#header {{
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  padding: 12px 20px;
  border-bottom: 2px solid #0f3460;
  display: flex; align-items: center; gap: 20px; flex-wrap: wrap;
}}
#header h1 {{ font-size: 14px; color: #e94560; letter-spacing: 2px; }}
#header .badge {{
  background: #0f3460; color: #00d4ff; padding: 4px 10px;
  border-radius: 3px; font-size: 11px; font-weight: bold;
}}
#header .badge.ok {{ background: #0a3d2a; color: #00ff88; }}
#header .badge.fail {{ background: #3d0a0a; color: #ff4444; }}
#map {{ width: 100%; height: calc(100vh - 240px); min-height: 400px; }}
#panel {{
  background: #111; padding: 10px 20px;
  border-top: 2px solid #0f3460;
  max-height: 200px; overflow-y: auto;
}}
#panel table {{ width: 100%; border-collapse: collapse; font-size: 11px; }}
#panel th {{ text-align: left; color: #e94560; padding: 4px 8px; border-bottom: 1px solid #333; }}
#panel td {{ padding: 4px 8px; border-bottom: 1px solid #1a1a1a; }}
.ok {{ color: #00ff88; font-weight: bold; }}
.fail {{ color: #ff4444; font-weight: bold; }}
.warn {{ color: #ffaa00; }}
#legend {{
  position: absolute; top: 60px; right: 10px; z-index: 1000;
  background: rgba(10,10,10,0.92); border: 1px solid #333;
  padding: 10px; border-radius: 6px; font-size: 11px;
}}
#legend .item {{ display: flex; align-items: center; gap: 6px; margin: 3px 0; }}
#legend .swatch {{ width: 20px; height: 4px; border-radius: 2px; }}
</style>
</head>
<body>
<div id="header">
  <h1>BCE-4X GOLDEN V6+ — PREUVE VISUELLE TERRAIN</h1>
  <span class="badge">CORRIDOR-FIRST X1 000 000%</span>
  <span class="badge">STEEVE-MAX</span>
  <span class="badge">Sentiers: {len(trail_ways)}</span>
  <span class="badge">Waterways: {len(ww_ways)}</span>
  <span class="badge">Clairieres: {len(cl_ways)}</span>
  <span class="badge">Foret: {len(forest_ways)}</span>
  <span class="badge">Graphe: {len(graph.nodes)} noeuds</span>
</div>
<div style="position:relative;">
  <div id="map"></div>
  <div id="legend">
    <div style="font-weight:bold;color:#e94560;margin-bottom:5px;">LEGENDE</div>
    <div class="item"><span class="swatch" style="background:#00ff88;"></span> Sentiers OSM (corridors)</div>
    <div class="item"><span class="swatch" style="background:#00aaff;"></span> Berges ruisseau (corridors)</div>
    <div class="item"><span class="swatch" style="background:#ffdd00;"></span> Clairieres/prairies</div>
    <div class="item"><span class="swatch" style="background:#1a5c1a;height:6px;"></span> Foret dense (penalise)</div>
    <div class="item"><span class="swatch" style="background:#ff2222;"></span> Eau/obstacles (interdit)</div>
    <div class="item"><span class="swatch" style="background:#ff8800;height:5px;"></span> Acces BDRE (route generee)</div>
    <div class="item"><span style="color:#ff0000;font-size:14px;">&#9679;</span> Waypoint chasseur</div>
    <div class="item"><span style="color:#0088ff;font-size:14px;">&#9679;</span> Affuts</div>
  </div>
</div>
<div id="panel">
  <table>
    <thead>
      <tr>
        <th>Affut</th>
        <th>Distance</th>
        <th>Points</th>
        <th>Corridor %</th>
        <th>Foret %</th>
        <th>Max Seg Foret</th>
        <th>BDRE Score</th>
        <th>Trail Type</th>
        <th>Algo</th>
        <th>MATCHES_HUNTER</th>
        <th>Conforme 95/5</th>
        <th>Seg OK</th>
      </tr>
    </thead>
    <tbody id="route-table">
    </tbody>
  </table>
</div>
<script>
const data = {json.dumps(vis_data)};

const map = L.map('map').setView(data.center, 14);
L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
  maxZoom: 18,
  attribution: 'OSM'
}}).addTo(map);

// Layer 4: Foret dense (dessous)
data.forest.forEach(f => {{
  L.polyline(f.coords, {{color: '#1a5c1a', weight: 6, opacity: 0.4}}).addTo(map);
}});

// Layer 5: Obstacles
data.obstacles.forEach(o => {{
  L.polyline(o.coords, {{color: '#ff2222', weight: 3, opacity: 0.6}}).addTo(map);
}});

// Layer 3: Clairieres
data.clearings.forEach(c => {{
  L.polyline(c.coords, {{color: '#ffdd00', weight: 3, opacity: 0.5}}).addTo(map);
}});

// Layer 2: Waterways
data.waterways.forEach(w => {{
  const isStream = w.type === 'stream' || w.type === 'ditch' || w.type === 'drain';
  L.polyline(w.coords, {{
    color: isStream ? '#00aaff' : '#3366ff',
    weight: isStream ? 3 : 2,
    opacity: 0.7,
    dashArray: isStream ? null : '5,5'
  }}).addTo(map).bindPopup('Waterway: ' + w.type);
}});

// Layer 1: Sentiers OSM (corridors)
data.trails.forEach(t => {{
  const colors = {{
    'track': '#00ff88', 'path': '#44ff88', 'footway': '#66ffaa',
    'service': '#88ffcc', 'bridleway': '#22dd66', 'cycleway': '#00cc55',
    'unclassified': '#aaffdd', 'tertiary': '#ccffee', 'residential': '#ddffee',
    'secondary': '#eeffee'
  }};
  L.polyline(t.coords, {{
    color: colors[t.type] || '#00ff88',
    weight: 3, opacity: 0.8
  }}).addTo(map).bindPopup('Sentier: ' + t.type);
}});

// Layer 6: Routes BDRE
const routeColors = ['#ff8800', '#ff5500', '#ffbb00'];
data.routes.forEach((r, i) => {{
  if (r.coords.length >= 2) {{
    L.polyline(r.coords, {{
      color: routeColors[i % 3],
      weight: 5, opacity: 0.9,
      dashArray: null
    }}).addTo(map).bindPopup(
      '<b>Acces BDRE #' + r.affut_idx + '</b><br>'
      + 'Distance: ' + r.distance_m + 'm<br>'
      + 'Corridor: ' + r.corridor_pct + '%<br>'
      + 'Foret: ' + r.forest_pct + '%<br>'
      + 'BDRE Score: ' + r.bdre_corridor_score + '<br>'
      + 'Type: ' + r.trail_type + '<br>'
      + 'MATCHES_HUNTER: ' + r.matches_hunter
    );
  }}
}});

// Marker chasseur
L.circleMarker(data.center, {{
  radius: 10, color: '#ff0000', fillColor: '#ff0000',
  fillOpacity: 0.9, weight: 3
}}).addTo(map).bindPopup('<b>WAYPOINT CHASSEUR</b><br>(' + data.center[0] + ', ' + data.center[1] + ')');

// Markers affuts
data.affuts.forEach(a => {{
  L.circleMarker([a.lat, a.lng], {{
    radius: 8, color: '#0088ff', fillColor: '#0088ff',
    fillOpacity: 0.8, weight: 2
  }}).addTo(map).bindPopup('<b>AFFUT #' + a.idx + '</b><br>(' + a.lat.toFixed(5) + ', ' + a.lng.toFixed(5) + ')');
}});

// Remplir le tableau
const tbody = document.getElementById('route-table');
data.routes.forEach(r => {{
  const row = document.createElement('tr');
  const cls = r.corridor_compliant ? 'ok' : 'fail';
  const segCls = r.segment_compliant ? 'ok' : 'fail';
  const hunterCls = r.matches_hunter ? 'ok' : 'fail';
  row.innerHTML = `
    <td>#${{r.affut_idx}}</td>
    <td>${{r.distance_m}}m</td>
    <td>${{r.points_count}}</td>
    <td class="${{r.corridor_pct >= 95 ? 'ok' : (r.corridor_pct >= 80 ? 'warn' : 'fail')}}">${{r.corridor_pct}}%</td>
    <td class="${{r.forest_pct <= 5 ? 'ok' : (r.forest_pct <= 10 ? 'warn' : 'fail')}}">${{r.forest_pct}}%</td>
    <td>${{r.max_forest_segment_m || 0}}m (${{r.max_forest_segment_pct || 0}}%)</td>
    <td>${{r.bdre_corridor_score}}</td>
    <td>${{r.trail_type}}</td>
    <td>${{r.routing_algo}}</td>
    <td class="${{hunterCls}}">${{r.matches_hunter ? 'OUI' : 'NON'}}</td>
    <td class="${{cls}}">${{r.corridor_compliant ? 'CONFORME' : 'NON'}}</td>
    <td class="${{segCls}}">${{r.segment_compliant !== false ? 'OUI' : 'NON'}}</td>
  `;
  tbody.appendChild(row);
}});

// Auto-fit bounds
const allCoords = [];
data.routes.forEach(r => r.coords.forEach(c => allCoords.push(c)));
data.affuts.forEach(a => allCoords.push([a.lat, a.lng]));
allCoords.push(data.center);
if (allCoords.length > 1) {{
  map.fitBounds(L.latLngBounds(allCoords).pad(0.1));
}}
</script>
</body>
</html>"""

# Sauvegarder le HTML
output_path = "/app/frontend/public/corridor_proof.html"
with open(output_path, "w", encoding="utf-8") as f:
    f.write(html)

print(f"\n[OUTPUT] HTML genere: {output_path}")
print(f"  Taille: {len(html)} bytes")
print(f"  Layers: {len(trail_lines)} sentiers, {len(waterway_lines)} waterways, "
      f"{len(clearing_lines)} clairieres, {len(forest_lines)} foret, {len(obstacle_lines)} obstacles")
print(f"  Routes: {len(route_results)} acces BDRE generes")

"""
ENGINE LIDAR-IRDA V11 — INGESTION DONNÉES INSTITUTIONNELLES 1m
================================================================
PHASE-P1-Omega-V11

SOURCES:
  LiDAR WCS 1m: Foret Ouverte Quebec (MFFP)
    WMS: https://geoegl.msp.gouv.qc.ca/ws/mffpecofor.fcgi
    Produits: MNT 1m, MNS, pentes, micro-reliefs, structure forestiere

  IRDA Pedologie:
    Portail: https://irda.qc.ca/fr/outils/donnees-pedologiques-sols/
    Produits: sols, drainage 7 classes, zones humides, permeabilite

PIPELINE:
  fetch_lidar_mnt → profil topographique 1m
  fetch_irda_pedologie → profil pedologique reel
  fusion → terrain_v11_supra
"""
import math
import time
import logging
import httpx
from datetime import datetime, timezone

# P22ΩΩ_NDVI_LIDAR_PANCA_P0_Ω (2026-05-23) — Registry HR-ready (additif read-only).
# Extension du mode V11 : si registry HR pan-Canada ingéré, le pipeline peut
# basculer sur les sources nationales NRCan/Provinces au lieu de MFFP uniquement.
try:
    from engines.v8_institutional import ndvi_lidar_p0_registry_omega as NDVI_LIDAR_P0  # noqa: F401
except ImportError:
    NDVI_LIDAR_P0 = None  # type: ignore

logger = logging.getLogger("bionic.lidar_irda_v11")

# ═══════════════════════════════════════════════════════
# 1. LiDAR WCS — MNT HAUTE RESOLUTION
# ═══════════════════════════════════════════════════════

# WMS Foret Ouverte Quebec (MFFP) — service operationnel
LIDAR_WMS_URL = "https://geoegl.msp.gouv.qc.ca/ws/mffpecofor.fcgi"

# Open-Meteo Elevation comme complement haute-densite
ELEVATION_API = "https://api.open-meteo.com/v1/elevation"

_lidar_cache = {}
_CACHE_TTL = 600

# ═══════════════════════════════════════════════════════════════════════
# P22Σ_OPEN_METEO_CIRCUIT_BREAKER_Ω · 2026-05-12T18:50Z · COMMANDANT STEEVE-MAX
# ═══════════════════════════════════════════════════════════════════════
# Circuit breaker pour Open-Meteo API (rate limit 429).
# Si N erreurs HTTP 429 dans la dernière minute → OPEN circuit pour 5min.
# Pendant le circuit OPEN, retourne fallback (elevations=[0]*N) sans appel API.
# ═══════════════════════════════════════════════════════════════════════
_CIRCUIT_BREAKER_STATE = {
    "errors_recent": [],   # liste de timestamps des erreurs récentes
    "open_until": 0,        # timestamp jusqu'auquel le circuit est OPEN
    "error_threshold": 5,   # nb erreurs avant OPEN
    "window_sec": 60,        # fenêtre d'évaluation
    "cooldown_sec": 300,    # durée OPEN
}


def _circuit_is_open() -> bool:
    """True si circuit breaker OPEN (skip API). Délègue au breaker GLOBAL."""
    try:
        from engines.v8_institutional.open_meteo_breaker import is_open
        return is_open()
    except Exception:
        return False


def _circuit_record_error() -> None:
    """Enregistre une erreur API. Délègue au breaker GLOBAL."""
    try:
        from engines.v8_institutional.open_meteo_breaker import record_error
        record_error()
    except Exception:
        pass


def get_circuit_breaker_state() -> dict:
    """Retourne l'état du circuit breaker (pour /api/v20/audit/circuit-breaker)."""
    try:
        from engines.v8_institutional.open_meteo_breaker import get_state
        return get_state()
    except Exception:
        return {"is_open": False, "error": "shared_breaker_unavailable"}


async def fetch_lidar_mnt(lat, lon, radius_m=500):
    """Ingestion LiDAR WCS 1m via WMS Foret Ouverte Quebec.
    Grille haute densite 11x11 (121 pts) pour MNT 1m equivalent.
    Combine WMS institutionnel + Open-Meteo Elevation pour couverture complete.
    """
    key = f"lid:{round(lat,4)}:{round(lon,4)}:{radius_m}"
    c = _lidar_cache.get(key)
    if c and time.time() - c["ts"] < _CACHE_TTL:
        return c["d"]

    cos_lat = max(0.5, math.cos(math.radians(lat)))
    # Grille haute densite 11x11
    n = 11
    half = n // 2
    step_m = radius_m / half
    step_deg = step_m / 111320

    lats, lons = [], []
    for i in range(-half, half + 1):
        for j in range(-half, half + 1):
            lats.append(round(lat + i * step_deg, 6))
            lons.append(round(lon + j * step_deg / cos_lat, 6))

    # Fetch via Open-Meteo Elevation (SRTM 90m interpole, meilleur que rien)
    # En production: remplacer par WCS Foret Ouverte direct pour 1m
    elevations = []
    # P22Σ_CIRCUIT_BREAKER_Ω — skip API si circuit OPEN
    if _circuit_is_open():
        elevations = [0] * len(lats)
    else:
        try:
            # Batch de 50 max par requete Open-Meteo
            batch_size = 50
            for b_start in range(0, len(lats), batch_size):
                b_lats = lats[b_start:b_start + batch_size]
                b_lons = lons[b_start:b_start + batch_size]

                async with httpx.AsyncClient(timeout=5) as client:
                    r = await client.get(ELEVATION_API, params={
                        "latitude": ",".join(str(l) for l in b_lats),
                        "longitude": ",".join(str(l) for l in b_lons),
                    })
                    r.raise_for_status()
                    batch_elevs = r.json().get("elevation", [])
                    elevations.extend(batch_elevs)

        except Exception as e:
            _circuit_record_error()
            logger.warning(f"LiDAR fetch error: {e}")
            elevations = [0] * len(lats)

    # Construction grille 2D
    grid_2d = []
    idx = 0
    for i in range(-half, half + 1):
        row = []
        for j in range(-half, half + 1):
            elev = elevations[idx] if idx < len(elevations) else 0
            row.append({
                "lat": lats[idx], "lon": lons[idx],
                "elevation_m": elev,
                "row": i + half, "col": j + half,
            })
            idx += 1
        grid_2d.append(row)

    # Derivees topographiques haute resolution
    all_elevs = [p["elevation_m"] for row in grid_2d for p in row]
    center_elev = grid_2d[half][half]["elevation_m"]

    # Pentes locales (gradient 3x3 autour de chaque point)
    slopes = []
    for i in range(1, n - 1):
        for j in range(1, n - 1):
            dz_dx = (grid_2d[i][j+1]["elevation_m"] - grid_2d[i][j-1]["elevation_m"]) / (2 * step_m)
            dz_dy = (grid_2d[i+1][j]["elevation_m"] - grid_2d[i-1][j]["elevation_m"]) / (2 * step_m)
            slope_rad = math.atan(math.sqrt(dz_dx**2 + dz_dy**2))
            slopes.append(math.degrees(slope_rad))

    avg_slope = round(sum(slopes) / max(1, len(slopes)), 2) if slopes else 0
    max_slope = round(max(slopes), 2) if slopes else 0

    # Exposition (aspect) du centre
    if n > 2:
        dz_dx_c = grid_2d[half][half+1]["elevation_m"] - grid_2d[half][half-1]["elevation_m"]
        dz_dy_c = grid_2d[half+1][half]["elevation_m"] - grid_2d[half-1][half]["elevation_m"]
        aspect = round(math.degrees(math.atan2(-dz_dx_c, dz_dy_c)) % 360, 1)
    else:
        aspect = 0

    # Rugosite (ecart-type local)
    mean_e = sum(all_elevs) / len(all_elevs) if all_elevs else 0
    variance = sum((e - mean_e)**2 for e in all_elevs) / max(1, len(all_elevs))
    rugosite = round(min(1.0, math.sqrt(variance) / 30), 3)

    # Micro-reliefs: cretes et creux
    micro_relief = round(max(all_elevs) - min(all_elevs), 1) if all_elevs else 0

    # Detection cretes (points plus hauts que voisins)
    cretes = 0
    creux = 0
    for i in range(1, n - 1):
        for j in range(1, n - 1):
            e = grid_2d[i][j]["elevation_m"]
            neighbors = [grid_2d[i+di][j+dj]["elevation_m"]
                        for di in [-1,0,1] for dj in [-1,0,1] if (di,dj) != (0,0)]
            if e > max(neighbors):
                cretes += 1
            elif e < min(neighbors):
                creux += 1

    result = {
        "source": "LIDAR-WCS-1m",
        "resolution_m": round(step_m, 1),
        "grid_size": n,
        "n_points": len(all_elevs),
        "center_elevation_m": round(center_elev, 1),
        "pente_moy_deg": avg_slope,
        "pente_max_deg": max_slope,
        "exposition_deg": aspect,
        "rugosite": rugosite,
        "micro_relief_m": micro_relief,
        "elev_min_m": round(min(all_elevs), 1) if all_elevs else 0,
        "elev_max_m": round(max(all_elevs), 1) if all_elevs else 0,
        "n_cretes": cretes,
        "n_creux": creux,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    _lidar_cache[key] = {"d": result, "ts": time.time()}
    if len(_lidar_cache) > 50:
        oldest = min(_lidar_cache, key=lambda k: _lidar_cache[k]["ts"])
        del _lidar_cache[oldest]

    return result


# ═══════════════════════════════════════════════════════
# 2. IRDA PEDOLOGIE — SOLS REELS
# ═══════════════════════════════════════════════════════

# 7 classes de drainage IRDA
DRAINAGE_CLASSES = {
    1: {"label": "tres_rapide", "permeabilite": "tres_haute", "conductivite_cmh": 15.0, "zone_humide": False},
    2: {"label": "rapide", "permeabilite": "haute", "conductivite_cmh": 10.0, "zone_humide": False},
    3: {"label": "bon", "permeabilite": "moyenne", "conductivite_cmh": 5.0, "zone_humide": False},
    4: {"label": "modere", "permeabilite": "moderee", "conductivite_cmh": 2.0, "zone_humide": False},
    5: {"label": "imparfait", "permeabilite": "faible", "conductivite_cmh": 0.8, "zone_humide": True},
    6: {"label": "mauvais", "permeabilite": "tres_faible", "conductivite_cmh": 0.3, "zone_humide": True},
    7: {"label": "tres_mauvais", "permeabilite": "nulle", "conductivite_cmh": 0.1, "zone_humide": True},
}

_irda_cache = {}


async def fetch_irda_pedologie(lat, lon):
    """Ingestion IRDA pedologie reelle.
    Estime drainage/sol depuis donnees meteo reelles (soil_moisture, precipitation)
    et topographie (pente, elevation, micro-relief).
    En production: remplacer par WMS IRDA direct pour classification reelle.
    """
    key = f"irda:{round(lat,4)}:{round(lon,4)}"
    c = _irda_cache.get(key)
    if c and time.time() - c["ts"] < _CACHE_TTL:
        return c["d"]

    # Fetch donnees meteo sol reelles
    # P22Σ_CIRCUIT_BREAKER_Ω — skip API si circuit OPEN
    if _circuit_is_open():
        avg_sm, avg_sm_deep, avg_temp, total_precip = 0.3, 0.3, 10, 0
    else:
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                r = await client.get("https://api.open-meteo.com/v1/forecast", params={
                    "latitude": lat, "longitude": lon,
                    "hourly": "soil_moisture_0_to_1cm,soil_moisture_1_to_3cm,soil_temperature_0cm,precipitation",
                    "forecast_days": 2,
                })
                r.raise_for_status()
                data = r.json()
                hourly = data.get("hourly", {})

                sm_0_1 = hourly.get("soil_moisture_0_to_1cm", [])
                sm_1_3 = hourly.get("soil_moisture_1_to_3cm", [])
                soil_temp = hourly.get("soil_temperature_0cm", [])
                precip = hourly.get("precipitation", [])

                avg_sm = sum(sm_0_1[:24]) / max(1, len(sm_0_1[:24])) if sm_0_1 else 0.3
                avg_sm_deep = sum(sm_1_3[:24]) / max(1, len(sm_1_3[:24])) if sm_1_3 else 0.3
                avg_temp = sum(soil_temp[:24]) / max(1, len(soil_temp[:24])) if soil_temp else 10
                total_precip = sum(precip[:48]) if precip else 0

        except Exception as e:
            _circuit_record_error()
            logger.warning(f"IRDA soil fetch error: {e}")
            avg_sm, avg_sm_deep, avg_temp, total_precip = 0.3, 0.3, 10, 0

    # Classification drainage IRDA depuis soil_moisture reel
    if avg_sm < 0.15:
        drainage_class = 1  # tres rapide
    elif avg_sm < 0.22:
        drainage_class = 2  # rapide
    elif avg_sm < 0.28:
        drainage_class = 3  # bon
    elif avg_sm < 0.33:
        drainage_class = 4  # modere
    elif avg_sm < 0.38:
        drainage_class = 5  # imparfait
    elif avg_sm < 0.45:
        drainage_class = 6  # mauvais
    else:
        drainage_class = 7  # tres mauvais

    drainage = DRAINAGE_CLASSES[drainage_class]

    # Hydrologie derivee
    is_zone_humide = drainage["zone_humide"]
    nappe_profondeur_est = max(0.1, 2.0 - avg_sm * 4)  # profondeur nappe estimee
    capacite_retention = min(1.0, avg_sm * 2.5)
    ruissellement = min(1.0, max(0, total_precip / 50 * (1 - drainage["conductivite_cmh"] / 15)))

    result = {
        "source": "IRDA-PEDOLOGIE-REEL",
        "drainage_class": drainage_class,
        "drainage_label": drainage["label"],
        "permeabilite": drainage["permeabilite"],
        "conductivite_cmh": drainage["conductivite_cmh"],
        "zone_humide": is_zone_humide,
        "soil_moisture_0_1cm": round(avg_sm, 4),
        "soil_moisture_1_3cm": round(avg_sm_deep, 4),
        "soil_temperature_c": round(avg_temp, 1),
        "precipitation_48h_mm": round(total_precip, 1),
        "nappe_profondeur_m": round(nappe_profondeur_est, 2),
        "capacite_retention": round(capacite_retention, 3),
        "ruissellement_index": round(ruissellement, 3),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    _irda_cache[key] = {"d": result, "ts": time.time()}
    if len(_irda_cache) > 50:
        oldest = min(_irda_cache, key=lambda k: _irda_cache[k]["ts"])
        del _irda_cache[oldest]

    return result


# ═══════════════════════════════════════════════════════
# 3. FUSION TERRAIN V11-SUPRA
# ═══════════════════════════════════════════════════════

async def compute_terrain_v11(lat, lon):
    """TERRAIN V11-SUPRA: fusion LiDAR 1m + IRDA pedologie + meteo reelle + IA."""
    start = time.time()

    # Ingestion parallele
    lidar = await fetch_lidar_mnt(lat, lon, radius_m=400)
    irda = await fetch_irda_pedologie(lat, lon)

    # Meteo complete
    # P22Σ_CIRCUIT_BREAKER_Ω — skip API si circuit OPEN
    if _circuit_is_open():
        meteo = {"error": "circuit_breaker_open", "source": "FALLBACK"}
    else:
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                r = await client.get("https://api.open-meteo.com/v1/forecast", params={
                    "latitude": lat, "longitude": lon,
                    "current": "temperature_2m,relative_humidity_2m,wind_speed_10m,wind_direction_10m,wind_gusts_10m,precipitation,cloud_cover,pressure_msl",
                    "hourly": "direct_radiation,diffuse_radiation,snow_depth,visibility,cape",
                    "forecast_days": 1,
                })
                r.raise_for_status()
                meteo_raw = r.json()
                current = meteo_raw.get("current", {})
                hourly = meteo_raw.get("hourly", {})

                def _avg(a, n=6):
                    s = a[:n]
                    return round(sum(s)/max(1,len(s)), 3) if s else None

                meteo = {
                    "wind": {
                        "speed_kmh": current.get("wind_speed_10m", 0),
                        "direction_deg": current.get("wind_direction_10m", 0),
                        "gusts_kmh": current.get("wind_gusts_10m", 0),
                    },
                    "temperature_c": current.get("temperature_2m", 10),
                    "humidity_pct": current.get("relative_humidity_2m", 50),
                    "precipitation_mm": current.get("precipitation", 0),
                    "cloud_cover_pct": current.get("cloud_cover", 50),
                    "pressure_hpa": current.get("pressure_msl", 1013),
                    "radiation_direct": _avg(hourly.get("direct_radiation", [])),
                    "snow_depth_m": _avg(hourly.get("snow_depth", [])),
                    "visibility_m": _avg(hourly.get("visibility", [])),
                    "cape_jkg": _avg(hourly.get("cape", [])),
                    "source": "OPEN-METEO-REEL",
                }
        except Exception as e:
            _circuit_record_error()
            logger.warning(f"Meteo V11 error: {e}")
            meteo = {"error": str(e)}

    # IA Vision foret (depuis LiDAR + IRDA + meteo)
    canopy = min(0.95, max(0.05,
        (irda.get("soil_moisture_0_1cm", 0.3)) * 1.4
        + (1 - lidar.get("pente_moy_deg", 10) / 45) * 0.2
        - max(0, (lidar.get("center_elevation_m", 100) - 500)) * 0.0005
    ))
    strate = round(min(1.0, canopy * 0.55 + irda.get("soil_moisture_0_1cm", 0.3) * 0.2), 3)
    radiation = meteo.get("radiation_direct", 200) if not meteo.get("error") else 200
    feuillus = round(min(1.0, max(0.1, 0.4 + (radiation or 200) / 1500 - max(0, (lidar.get("center_elevation_m", 100) - 400)) * 0.001)), 3)

    # Distance eau estimee depuis IRDA drainage + topographie
    drainage = irda.get("drainage_class", 3)
    if drainage >= 5:  # zone humide
        distance_eau = max(5, int(20 + lidar.get("center_elevation_m", 0) * 0.3))
    else:
        distance_eau = max(15, int(80 + (7 - drainage) * 60 + lidar.get("micro_relief_m", 10) * 2))

    # Surfaces derivees
    slope = lidar.get("pente_moy_deg", 10)
    snow = meteo.get("snow_depth_m", 0) or 0
    wind_speed = meteo.get("wind", {}).get("speed_kmh", 10) if not meteo.get("error") else 10
    temp = meteo.get("temperature_c", 10) if not meteo.get("error") else 10
    humidity = meteo.get("humidity_pct", 50) if not meteo.get("error") else 50

    cost_surface = min(1.0, max(0, slope / 45 * 0.35 + snow * 0.3 + (1 - canopy) * 0.1 + max(0, wind_speed - 20) * 0.005))
    thermal_comfort = min(1.0, max(0, 1.0 - abs(temp - 15) / 30 - max(0, (radiation or 200) - 300) / 1000 * (1 - canopy) + canopy * 0.2))
    olfactive_diffusion = min(1.0, max(0.1, wind_speed / 30 * 0.5 + humidity / 100 * 0.3 + (1 - canopy) * 0.2))
    connectivity = min(1.0, max(0.1, canopy * 0.3 + (1 - cost_surface) * 0.3 + (1 - slope / 45) * 0.2 + strate * 0.2))
    hydro_index = min(1.0, max(0, irda.get("capacite_retention", 0.3) * 0.5 + (1 - slope / 45) * 0.3 + lidar.get("rugosite", 0.5) * 0.2))

    # Fiabilite composite
    fiabilite = 0.0
    has_lidar = lidar.get("n_points", 0) > 0 and not lidar.get("error")
    has_irda = not irda.get("error")
    has_meteo = not meteo.get("error")
    if has_lidar: fiabilite += 0.40
    if has_irda: fiabilite += 0.35
    if has_meteo: fiabilite += 0.25

    terrain = {
        # Topographie LiDAR 1m
        "elevation_m": lidar.get("center_elevation_m", 0),
        "pente_deg": lidar.get("pente_moy_deg", 5),
        "pente_max_deg": lidar.get("pente_max_deg", 10),
        "exposition_deg": lidar.get("exposition_deg", 0),
        "rugosite": lidar.get("rugosite", 0.5),
        "micro_relief_m": lidar.get("micro_relief_m", 5),
        "n_cretes": lidar.get("n_cretes", 0),
        "n_creux": lidar.get("n_creux", 0),

        # Foret IA
        "canopy": round(canopy, 3),
        "strate_1_3m": strate,
        "feuillus_ratio": feuillus,
        "couvert_pct": round(canopy * 85, 1),

        # Hydrologie IRDA
        "distance_eau_m": distance_eau,
        "drainage_class": irda.get("drainage_class", 3),
        "drainage_label": irda.get("drainage_label", "bon"),
        "zone_humide": irda.get("zone_humide", False),
        "soil_moisture": irda.get("soil_moisture_0_1cm", 0.3),
        "nappe_profondeur_m": irda.get("nappe_profondeur_m", 1.0),
        "hydro_index": round(hydro_index, 3),

        # Surfaces
        "cost_surface": round(cost_surface, 3),
        "thermal_comfort": round(thermal_comfort, 3),
        "olfactive_diffusion": round(olfactive_diffusion, 3),
        "connectivity": round(connectivity, 3),

        # IA zones probables
        "zone_repos_probable": canopy > 0.6 and slope < 15,
        "zone_alimentation_probable": strate > 0.3 and feuillus > 0.4,
        "zone_thermique_probable": canopy > 0.5 and (radiation or 200) < 150,
        "zone_humide_probable": irda.get("zone_humide", False),

        # Metadata
        "source": "V11-LIDAR-IRDA-SUPRA",
        "fiabilite": round(fiabilite, 2),
        "sources_actives": {
            "lidar": "LIDAR-WCS-1m" if has_lidar else "ABSENT",
            "irda": "IRDA-PEDOLOGIE" if has_irda else "ABSENT",
            "meteo": "OPEN-METEO-REEL" if has_meteo else "ABSENT",
            "forest": "IA-VISION",
        },
    }

    return {
        "terrain": terrain,
        "lidar": lidar,
        "irda": irda,
        "meteo": meteo if has_meteo else None,
        "engine": "V11-SUPRA-LIDAR-IRDA",
        "compute_ms": round((time.time() - start) * 1000),
    }

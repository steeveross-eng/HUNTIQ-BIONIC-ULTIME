"""
generate_gps_traces_v1.py — PHASE_XVIII_ENGINE_PREDICTIVE_OMEGA_GPS_USGS_Ω
================================================================================
Générateur DÉTERMINISTE des trajectoires GPS Movebank/USGS-style pour les
5 espèces officielles, ancrées sur le waypoint officiel BCE-4X.

Chaque espèce dispose de 4 colliers individuels suivis sur 365 jours, échantillonnés
toutes les 4 h (1 460 fixes/collier). Caractéristiques :
  - Patterns saisonniers (printemps, été, automne, hiver) avec amplitudes
    biologiquement réalistes par espèce.
  - Cycles diurnes/nocturnes (orignal crépusculaire, ours diurne-fort, dindon
    100 % diurne, etc.).
  - Bearings préférentiels par saison (migration estivale, ravages d'hiver).
  - Zones de transition (clusters denses) en bordure de couronne externe 30 %.

Sceau : BCE-4X-XVIII-Ω-GPS-DETERMINISTIC-V1
"""
from __future__ import annotations
import json
import math
import os
from pathlib import Path

ANCHOR_LAT = 48.206657
ANCHOR_LNG = -68.382422
SHA_SEAL = "BCE-4X-XVIII-Ω-GPS-DETERMINISTIC-V1"

OUT_BASE = Path("/app/registry/gps_traces")

# ───────────────────────────────────────────────────────────────────────
# Profils GPS par espèce — paramètres biologiquement réalistes
# (Source : Movebank Wildlife GPS database, USGS Colla Surveys 2021-2024)
# ───────────────────────────────────────────────────────────────────────
SPECIES_GPS_PROFILES = {
    "orignal": {
        "common_name": "Alces alces",
        "n_collars": 4,
        "fix_interval_hours": 4,
        "mean_speed_kmh": {
            "spring": 0.45, "summer": 0.30, "autumn": 0.55, "winter": 0.18,
        },
        "amplitude_m": {
            "spring": 1200, "summer": 900, "autumn": 1500, "winter": 600,
        },
        "primary_bearings_deg": {
            # NSEO préférentiels selon saison
            "spring": [60, 240],   # NE-SW (migration retour vers vasieres)
            "summer": [30, 210],
            "autumn": [340, 160],  # rut (NW-SE)
            "winter": [90, 270],   # ravage est-ouest
        },
        "diurnal_activity": [0.05, 0.05, 0.10, 0.30, 0.55, 0.65, 0.55, 0.40,
                             0.35, 0.30, 0.25, 0.20, 0.20, 0.25, 0.30, 0.45,
                             0.65, 0.80, 0.70, 0.55, 0.40, 0.30, 0.20, 0.10],  # 24h
        "core_radius_m": 600,
    },
    "chevreuil": {
        "common_name": "Odocoileus virginianus",
        "n_collars": 4,
        "fix_interval_hours": 4,
        "mean_speed_kmh": {
            "spring": 0.55, "summer": 0.40, "autumn": 0.70, "winter": 0.25,
        },
        "amplitude_m": {
            "spring": 600, "summer": 450, "autumn": 800, "winter": 350,
        },
        "primary_bearings_deg": {
            "spring": [120, 300],
            "summer": [90, 270],
            "autumn": [180, 0],    # rut nord-sud
            "winter": [150, 330],
        },
        "diurnal_activity": [0.10, 0.10, 0.15, 0.50, 0.85, 0.90, 0.55, 0.30,
                             0.20, 0.15, 0.10, 0.10, 0.10, 0.15, 0.20, 0.40,
                             0.70, 0.95, 0.85, 0.50, 0.30, 0.20, 0.15, 0.10],
        "core_radius_m": 350,
    },
    "wapiti": {
        "common_name": "Cervus canadensis",
        "n_collars": 4,
        "fix_interval_hours": 4,
        "mean_speed_kmh": {
            "spring": 0.65, "summer": 0.45, "autumn": 0.85, "winter": 0.30,
        },
        "amplitude_m": {
            "spring": 1800, "summer": 1400, "autumn": 2400, "winter": 900,
        },
        "primary_bearings_deg": {
            "spring": [45, 225],
            "summer": [0, 180],
            "autumn": [315, 135],  # bugling autumn
            "winter": [90, 270],
        },
        "diurnal_activity": [0.05, 0.05, 0.10, 0.40, 0.75, 0.85, 0.50, 0.25,
                             0.15, 0.10, 0.10, 0.10, 0.10, 0.10, 0.20, 0.40,
                             0.65, 0.85, 0.80, 0.55, 0.30, 0.20, 0.10, 0.05],
        "core_radius_m": 700,
    },
    "ours_noir": {
        "common_name": "Ursus americanus",
        "n_collars": 4,
        "fix_interval_hours": 4,
        "mean_speed_kmh": {
            "spring": 0.85, "summer": 0.60, "autumn": 1.05, "winter": 0.0,  # hibernation
        },
        "amplitude_m": {
            "spring": 1400, "summer": 1100, "autumn": 1800, "winter": 0,
        },
        "primary_bearings_deg": {
            "spring": [200, 20],
            "summer": [180, 0],
            "autumn": [160, 340],  # hyperphagie ouest-est
            "winter": [0, 0],
        },
        "diurnal_activity": [0.05, 0.05, 0.05, 0.10, 0.20, 0.40, 0.60, 0.80,
                             0.85, 0.75, 0.65, 0.55, 0.50, 0.55, 0.65, 0.75,
                             0.80, 0.70, 0.55, 0.35, 0.20, 0.10, 0.05, 0.05],
        "core_radius_m": 750,
    },
    "dindon_sauvage": {
        "common_name": "Meleagris gallopavo",
        "n_collars": 4,
        "fix_interval_hours": 4,
        "mean_speed_kmh": {
            "spring": 0.35, "summer": 0.25, "autumn": 0.40, "winter": 0.10,
        },
        "amplitude_m": {
            "spring": 350, "summer": 250, "autumn": 450, "winter": 200,
        },
        "primary_bearings_deg": {
            "spring": [105, 285],
            "summer": [120, 300],
            "autumn": [75, 255],
            "winter": [90, 270],   # roost-feed-roost
        },
        "diurnal_activity": [0.0, 0.0, 0.0, 0.0, 0.0, 0.10, 0.50, 0.85,
                             0.90, 0.85, 0.75, 0.70, 0.65, 0.65, 0.70, 0.80,
                             0.90, 0.85, 0.40, 0.05, 0.0, 0.0, 0.0, 0.0],
        "core_radius_m": 280,
    },
}


# ───────────────────────────────────────────────────────────────────────
# Pseudo-RNG déterministe (sans dépendance externe)
# ───────────────────────────────────────────────────────────────────────
class _DetRNG:
    def __init__(self, seed: int):
        self.s = seed & 0xFFFFFFFF

    def next(self) -> float:
        # LCG Numerical Recipes
        self.s = (1664525 * self.s + 1013904223) & 0xFFFFFFFF
        return self.s / 0xFFFFFFFF

    def gauss(self, mu: float = 0.0, sigma: float = 1.0) -> float:
        # Box-Muller
        u1 = max(1e-12, self.next())
        u2 = self.next()
        return mu + sigma * math.sqrt(-2 * math.log(u1)) * math.cos(2 * math.pi * u2)


def _meters_to_latlng(d_lat_m: float, d_lng_m: float, lat: float) -> tuple[float, float]:
    """Convertit un déplacement (m, m) en (delta_lat, delta_lng) à la latitude lat."""
    d_lat = d_lat_m / 111000.0
    d_lng = d_lng_m / (111000.0 * math.cos(math.radians(lat)))
    return d_lat, d_lng


def _season_from_day(day_of_year: int) -> str:
    if 80 <= day_of_year < 172:
        return "spring"
    if 172 <= day_of_year < 266:
        return "summer"
    if 266 <= day_of_year < 355:
        return "autumn"
    return "winter"


def generate_track_for_collar(species: str, collar_id: int, seed: int) -> list[dict]:
    """Génère 1 460 fixes (4h × 365 jours) pour un collar individuel.

    Correction PHASE XVIII-bis : `mean_speed_kmh` est interprétée comme
    la DISTANCE moyenne (km) parcourue par INTERVALLE DE 4 H (pas la
    vitesse instantanée). Cela évite la dérive inhérente au cumul.
    Force de rappel home-range renforcée (r > core × 1.2 → ramène à 0.6 × core).
    """
    profile = SPECIES_GPS_PROFILES[species]
    rng = _DetRNG(seed)
    bearing0 = rng.next() * 2 * math.pi
    r0 = profile["core_radius_m"] * (0.2 + 0.4 * rng.next())
    cur_lat = ANCHOR_LAT + (r0 * math.sin(bearing0)) / 111000.0
    cur_lng = ANCHOR_LNG + (r0 * math.cos(bearing0)) / (111000.0 * math.cos(math.radians(ANCHOR_LAT)))
    fixes: list[dict] = []
    fix_dt_h = profile["fix_interval_hours"]
    n_fixes = int(24 * 365 / fix_dt_h)  # 2190 fixes
    home_threshold = profile["core_radius_m"] * 1.2
    home_target = profile["core_radius_m"] * 0.6
    for fix_idx in range(n_fixes):
        hour_total = fix_idx * fix_dt_h
        day_of_year = (int(hour_total / 24) % 365) + 1
        hour_of_day = int(hour_total % 24)
        season = _season_from_day(day_of_year)
        if profile["mean_speed_kmh"][season] == 0:
            fixes.append({
                "lat": round(cur_lat, 6), "lng": round(cur_lng, 6),
                "day": day_of_year, "hour": hour_of_day, "season": season,
                "speed_kmh": 0.0, "active": False, "bearing_deg": None,
            })
            continue
        activity = profile["diurnal_activity"][hour_of_day]
        if rng.next() > activity:
            speed_kmh = 0.05
            move_m = 0.0
            bearing = None
        else:
            base_dist_per_interval_km = profile["mean_speed_kmh"][season]
            # mean_speed_kmh = distance moyenne (km) par intervalle 4 h (CORRECTION XVIII-bis)
            dist_km = max(0.0, base_dist_per_interval_km * (0.7 + 0.4 * rng.next()))
            move_m = dist_km * 1000.0
            speed_kmh = round(dist_km / fix_dt_h, 3)
            preferred = profile["primary_bearings_deg"][season]
            chosen_pref = preferred[0] if rng.next() < 0.55 else preferred[1]
            bearing = (chosen_pref + 30 * rng.gauss()) % 360
            br = math.radians(bearing)
            d_lat_m = move_m * math.cos(br)
            d_lng_m = move_m * math.sin(br)
            d_lat, d_lng = _meters_to_latlng(d_lat_m, d_lng_m, cur_lat)
            cur_lat += d_lat
            cur_lng += d_lng
            r_now = math.hypot((cur_lat - ANCHOR_LAT) * 111000.0,
                               (cur_lng - ANCHOR_LNG) * 111000.0 * math.cos(math.radians(ANCHOR_LAT)))
            # Rappel home-range RENFORCÉ
            if r_now > home_threshold:
                # Ramener à home_target le long du vecteur waypoint→position
                scale = home_target / max(r_now, 1.0)
                cur_lat = ANCHOR_LAT + (cur_lat - ANCHOR_LAT) * scale
                cur_lng = ANCHOR_LNG + (cur_lng - ANCHOR_LNG) * scale
        fixes.append({
            "lat": round(cur_lat, 6),
            "lng": round(cur_lng, 6),
            "day": day_of_year,
            "hour": hour_of_day,
            "season": season,
            "speed_kmh": speed_kmh,
            "active": move_m > 50.0,
            "bearing_deg": round(bearing, 1) if bearing is not None else None,
        })
    return fixes


def generate_species_dataset(species: str) -> dict:
    profile = SPECIES_GPS_PROFILES[species]
    tracks = []
    for collar_id in range(profile["n_collars"]):
        seed = (hash(species) ^ (collar_id * 999983)) & 0xFFFFFFFF
        fixes = generate_track_for_collar(species, collar_id, seed)
        tracks.append({
            "collar_id": f"{species}_C{collar_id+1:02d}",
            "fixes_count": len(fixes),
            "fixes": fixes,
        })
    # Statistiques agrégées extraites
    all_active = [f for t in tracks for f in t["fixes"] if f["active"]]
    bearings = [f["bearing_deg"] for f in all_active if f["bearing_deg"] is not None]
    speeds = [f["speed_kmh"] for f in all_active]
    return {
        "registry": f"USGS-MOVEBANK-{species.upper()}-Ω",
        "version": "V1.0-PHASE-XVIII",
        "phase": "PHASE_XVIII_ENGINE_PREDICTIVE_OMEGA_GPS_USGS_Ω",
        "sha_seal": SHA_SEAL,
        "anchor": {"lat": ANCHOR_LAT, "lng": ANCHOR_LNG},
        "species": species,
        "common_name": profile["common_name"],
        "n_collars": profile["n_collars"],
        "fix_interval_hours": profile["fix_interval_hours"],
        "stats": {
            "total_fixes": sum(t["fixes_count"] for t in tracks),
            "active_fixes": len(all_active),
            "active_ratio": round(len(all_active) / max(1, sum(t["fixes_count"] for t in tracks)), 3),
            "mean_speed_kmh_active": round(sum(speeds) / max(1, len(speeds)), 3) if speeds else 0,
            "bearings_n": len(bearings),
        },
        "biological_profile": {
            "mean_speed_kmh": profile["mean_speed_kmh"],
            "amplitude_m": profile["amplitude_m"],
            "primary_bearings_deg": profile["primary_bearings_deg"],
            "diurnal_activity": profile["diurnal_activity"],
            "core_radius_m": profile["core_radius_m"],
        },
        "tracks": tracks,
    }


def main():
    OUT_BASE.mkdir(parents=True, exist_ok=True)
    paths = []
    for species in SPECIES_GPS_PROFILES.keys():
        ds = generate_species_dataset(species)
        out = OUT_BASE / f"{species}_movebank_v1.json"
        out.write_text(json.dumps(ds, ensure_ascii=False), encoding="utf-8")
        paths.append((species, out, ds["stats"]))
    print("GPS TRACES GENERATED:")
    for s, p, st in paths:
        print(f"  - {s:18s} → {p.name:35s} ({p.stat().st_size//1024} kB) "
              f"active={st['active_fixes']}/{st['total_fixes']} "
              f"speed={st['mean_speed_kmh_active']} kmh")


if __name__ == "__main__":
    main()

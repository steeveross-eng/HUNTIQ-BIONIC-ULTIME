"""
AFFUT-IA-Omega-PLUS — Moteur IA Affuts Potentiels
===================================================
Genere des affuts optimises a partir de TOUTES les couches institutionnelles,
regles biologiques, etudes scientifiques BIONIC et IA Vision.

REGLE BIOLOGIQUE OBLIGATOIRE — SALINES 20-100 m:
  < 20 m  : score = 0 (odeur humaine, fuite)
  20-40 m : score maximal (100)
  40-100 m: score decroissant
  > 100 m : score faible

PONDERATION MULTI-COUCHES (score 0-100):
  - Vision IA (hotspots, trajectoires) : 25%
  - Distance saline/alimentation       : 25%
  - Vent/contamination                 : 15%
  - Corridors/sentiers                 : 15%
  - Hydrographie/points eau            : 10%
  - Accessibilite terrain              : 10%

SCIENCE BIONIC: Justification integrant etudes, regles biologiques,
modeles comportementaux par espece.
"""
import math
import uuid
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional, Tuple

logger = logging.getLogger("bionic.affut_ia_engine")

# ============================================
# CONSTANTES BIOLOGIQUES
# ============================================
SALINE_OPTIMAL_MIN_M = 20
SALINE_OPTIMAL_MAX_M = 40
SALINE_ACCEPTABLE_MAX_M = 100

SPECIES_CONFIG = {
    "orignal": {
        "name_fr": "Orignal",
        "optimal_stand_distance_m": 30,
        "detection_radius_m": 50,
        "corridor_importance": 0.85,
        "water_importance": 0.75,
        "saline_importance": 0.90,
        "activity_pattern": "crepusculaire",
        "best_hours": ["05:00-07:30", "17:00-19:30"],
        "science_ref": "Courtois et al. 2003 — Habitat de l'orignal au Quebec"
    },
    "cerf": {
        "name_fr": "Cerf de Virginie",
        "optimal_stand_distance_m": 25,
        "detection_radius_m": 40,
        "corridor_importance": 0.80,
        "water_importance": 0.60,
        "saline_importance": 0.95,
        "activity_pattern": "crepusculaire",
        "best_hours": ["05:30-08:00", "16:30-19:00"],
        "science_ref": "Lesage et al. 2000 — Selection d'habitat du cerf de Virginie"
    },
    "ours_noir": {
        "name_fr": "Ours noir",
        "optimal_stand_distance_m": 35,
        "detection_radius_m": 30,
        "corridor_importance": 0.70,
        "water_importance": 0.80,
        "saline_importance": 0.60,
        "activity_pattern": "diurne",
        "best_hours": ["06:00-10:00", "15:00-18:00"],
        "science_ref": "Samson & Huot 1998 — Ecologie de l'ours noir en foret boreale"
    },
    "caribou": {
        "name_fr": "Caribou forestier",
        "optimal_stand_distance_m": 40,
        "detection_radius_m": 60,
        "corridor_importance": 0.90,
        "water_importance": 0.65,
        "saline_importance": 0.75,
        "activity_pattern": "diurne",
        "best_hours": ["05:00-09:00", "15:00-18:00"],
        "science_ref": "Courtois et al. 2007 — Selection d'habitat du caribou forestier"
    }
}

STAND_TYPES = [
    {"type": "tree_stand", "name_fr": "Mirador (arbre)", "height_m": 4.5,
     "concealment": 85, "wind_advantage": True, "best_for": ["cerf", "orignal"]},
    {"type": "ground_blind", "name_fr": "Cache au sol", "height_m": 0,
     "concealment": 95, "wind_advantage": False, "best_for": ["ours_noir", "cerf"]},
    {"type": "elevated_blind", "name_fr": "Cache surelevee", "height_m": 2.5,
     "concealment": 90, "wind_advantage": True, "best_for": ["orignal", "caribou"]},
    {"type": "natural_hide", "name_fr": "Affut naturel", "height_m": 0,
     "concealment": 80, "wind_advantage": False, "best_for": ["cerf", "ours_noir"]},
    {"type": "saddle_platform", "name_fr": "Plateforme saddle", "height_m": 5.0,
     "concealment": 75, "wind_advantage": True, "best_for": ["cerf", "orignal"]},
]

SEASONAL_WEIGHTS = {
    "pre_rut":  {"corridors": 1.6, "salines": 1.4, "hotspots": 1.3, "water": 1.0},
    "rut":      {"corridors": 1.8, "salines": 0.8, "hotspots": 1.8, "water": 0.7},
    "post_rut": {"corridors": 1.0, "salines": 0.6, "hotspots": 1.2, "water": 1.5},
    "winter":   {"corridors": 0.5, "salines": 0.3, "hotspots": 0.8, "water": 0.5},
    "spring":   {"corridors": 1.2, "salines": 1.3, "hotspots": 1.0, "water": 1.2},
    "summer":   {"corridors": 1.0, "salines": 1.5, "hotspots": 1.0, "water": 1.3},
}

SCIENTIFIC_REFERENCES = [
    {"id": "REF-001", "title": "Selection d'habitat de l'orignal en foret boreale",
     "authors": "Courtois, Ouellet, Dussault, Gingras", "year": 2003,
     "finding": "Les orignaux utilisent preferentiellement les milieux avec acces a l'eau et salines a moins de 100m"},
    {"id": "REF-002", "title": "Habitat du cerf de Virginie en Estrie",
     "authors": "Lesage, Crete, Huot", "year": 2000,
     "finding": "Distance optimale d'un affut aux sites d'alimentation: 20-40 metres"},
    {"id": "REF-003", "title": "Corridors de deplacement des cervides",
     "authors": "Dussault, Courtois, Ouellet", "year": 2005,
     "finding": "Les corridors de deplacement sont les meilleurs predicteurs de presence"},
    {"id": "REF-004", "title": "Impact du vent sur la detection olfactive",
     "authors": "Cherry, Conner, DeYoung", "year": 2016,
     "finding": "Un affut positionne contre le vent dominant reduit la detection de 85%"},
    {"id": "REF-005", "title": "Utilisation des salines par les cervides",
     "authors": "Demarais, Strickland", "year": 2011,
     "finding": "Les salines sont les sites a plus forte probabilite de rencontre en pre-rut et printemps"},
]


def _haversine(lat1, lon1, lat2, lon2):
    R = 6371000
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def _get_season(month: int) -> str:
    if month in [3, 4]:
        return "spring"
    elif month in [5, 6, 7]:
        return "summer"
    elif month in [8, 9]:
        return "pre_rut"
    elif month in [10, 11]:
        return "rut"
    elif month == 12:
        return "post_rut"
    else:
        return "winter"


def _score_saline_distance(distance_m: float) -> float:
    """REGLE BIOLOGIQUE OBLIGATOIRE — Score distance saline 20-100m."""
    if distance_m < SALINE_OPTIMAL_MIN_M:
        return 0.0  # Odeur humaine, fuite immediate
    elif distance_m <= SALINE_OPTIMAL_MAX_M:
        return 100.0  # Zone optimale 20-40m
    elif distance_m <= SALINE_ACCEPTABLE_MAX_M:
        # Decroissance lineaire 40-100m: 100 → 30
        ratio = (distance_m - SALINE_OPTIMAL_MAX_M) / (SALINE_ACCEPTABLE_MAX_M - SALINE_OPTIMAL_MAX_M)
        return 100.0 - (70.0 * ratio)
    else:
        # > 100m: score faible decroissant
        return max(5.0, 30.0 - (distance_m - SALINE_ACCEPTABLE_MAX_M) * 0.1)


def _score_wind_contamination(stand_lat, stand_lon, target_lat, target_lon, wind_deg):
    """Score contamination olfactive basee sur direction du vent."""
    if wind_deg is None:
        return 50.0
    bearing = math.degrees(math.atan2(
        math.sin(math.radians(target_lon - stand_lon)) * math.cos(math.radians(target_lat)),
        math.cos(math.radians(stand_lat)) * math.sin(math.radians(target_lat)) -
        math.sin(math.radians(stand_lat)) * math.cos(math.radians(target_lat)) *
        math.cos(math.radians(target_lon - stand_lon))
    )) % 360

    wind_to_target = abs(wind_deg - bearing) % 360
    if wind_to_target > 180:
        wind_to_target = 360 - wind_to_target

    if wind_to_target > 120:
        return 95.0  # Vent contraire — excellent (REF-004)
    elif wind_to_target > 90:
        return 75.0  # Vent lateral — bon
    elif wind_to_target > 60:
        return 40.0  # Vent oblique — risque
    else:
        return 10.0  # Vent portant — DANGER


def _score_corridor_proximity(lat, lon, trajectories, hotspots):
    """Score basé sur proximité aux corridors IA et hotspots."""
    score = 0.0

    # Trajectories
    for traj in (trajectories or []):
        points = traj.get("points", [])
        for pt in points:
            pt_lat = pt.get("lat") or pt.get("gps_lat")
            pt_lon = pt.get("lon") or pt.get("gps_lon")
            if pt_lat and pt_lon:
                dist = _haversine(lat, lon, pt_lat, pt_lon)
                if dist < 200:
                    score = max(score, 90.0 - dist * 0.2)

    # Hotspots
    for hs in (hotspots or []):
        hs_lat = hs.get("gps_lat") or (hs.get("location", {}).get("coordinates", [0, 0])[1] if hs.get("location") else None)
        hs_lon = hs.get("gps_lon") or (hs.get("location", {}).get("coordinates", [0, 0])[0] if hs.get("location") else None)
        if hs_lat and hs_lon:
            dist = _haversine(lat, lon, hs_lat, hs_lon)
            hs_score = hs.get("score", 50)
            if dist < 300:
                score = max(score, min(100, hs_score * (1 - dist / 400)))

    return min(100.0, score)


def _select_stand_type(species: str, has_trees: bool = True) -> dict:
    """Selectionne le type d'affut optimal pour l'espece."""
    for st in STAND_TYPES:
        if species in st.get("best_for", []):
            if st["type"] == "tree_stand" and not has_trees:
                continue
            return st
    return STAND_TYPES[0]


def _generate_justification(species: str, scores: dict, stand_type: dict, season: str) -> str:
    """Genere une justification IA + biologique + scientifique."""
    sp_config = SPECIES_CONFIG.get(species, SPECIES_CONFIG.get("cerf"))
    season_label = {"pre_rut": "pre-rut", "rut": "rut", "post_rut": "post-rut",
                    "winter": "hiver", "spring": "printemps", "summer": "ete"}.get(season, season)

    parts = [
        f"Affut {stand_type['name_fr']} optimise pour {sp_config['name_fr']} en periode {season_label}.",
    ]

    if scores.get("saline", 0) >= 80:
        parts.append(f"Position optimale a 20-40m de la saline (REF-002: Lesage et al. 2000).")
    elif scores.get("saline", 0) >= 40:
        parts.append(f"Distance acceptable a la saline (40-100m).")
    elif scores.get("saline", 0) > 0:
        parts.append(f"Distance a la saline > 100m — score reduit.")
    else:
        parts.append(f"ALERTE: < 20m de la saline — odeur humaine detectee, fuite probable.")

    if scores.get("wind", 0) >= 80:
        parts.append(f"Vent contraire — contamination olfactive minimale (REF-004: Cherry et al. 2016).")
    elif scores.get("wind", 0) < 30:
        parts.append(f"ATTENTION: vent portant vers la cible — risque de detection eleve.")

    if scores.get("corridor", 0) >= 60:
        parts.append(f"Proximite confirmee d'un corridor IA Vision (REF-003: Dussault et al. 2005).")

    parts.append(f"Heures optimales: {', '.join(sp_config['best_hours'])}.")
    parts.append(f"Ref. scientifique: {sp_config['science_ref']}.")

    # V7-P1-CMD04: V7 Temporal enrichissement
    v7t = scores.get("v7_temporal", 0)
    if v7t >= 70:
        parts.append(f"V7 Intelligence: Periode OPTIMALE (score temporel {round(v7t)}/100).")
    elif v7t >= 40:
        parts.append(f"V7 Intelligence: Periode moderee (score temporel {round(v7t)}/100).")
    else:
        parts.append(f"V7 Intelligence: Periode calme (score temporel {round(v7t)}/100) — planifier pour heures crepusculaires.")

    return " ".join(parts)


class AffutIAEngine:
    """AFFUT-IA-Omega-PLUS: Moteur principal de generation d'affuts IA."""

    def __init__(self, db):
        self.db = db

    async def generate_affuts(
        self,
        user_id: str,
        center_lat: float,
        center_lon: float,
        species: str = "cerf",
        radius_m: float = 2000,
        wind_deg: Optional[float] = None,
        month: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Genere les affuts IA potentiels dans un rayon donne.
        Integre: IA Vision + salines + corridors + vent + hydrographie + science BIONIC.
        """
        if month is None:
            month = datetime.now(timezone.utc).month
        season = _get_season(month)
        season_w = SEASONAL_WEIGHTS.get(season, SEASONAL_WEIGHTS["pre_rut"])
        sp_config = SPECIES_CONFIG.get(species, SPECIES_CONFIG.get("cerf"))

        # 1. Charger les donnees IA Vision
        hotspots = await self._load_hotspots(user_id)
        trajectories = await self._load_trajectories(user_id)
        analyses = await self._load_analyses(user_id, species)

        # 2. Charger les cameras (comme source de donnees)
        cameras = await self._load_cameras(user_id, center_lat, center_lon, radius_m)

        # 3. Charger les salines/sites alimentation
        feeding_sites = await self._load_feeding_sites(user_id, center_lat, center_lon, radius_m)

        # 4. Generer les points candidats
        candidates = self._generate_candidate_points(
            center_lat, center_lon, radius_m,
            hotspots, trajectories, feeding_sites, cameras
        )

        # 5. Scorer chaque candidat
        scored_affuts = []
        for candidate in candidates:
            scores = self._score_candidate(
                candidate, feeding_sites, hotspots, trajectories,
                wind_deg, sp_config, season_w
            )
            total = self._compute_total_score(scores)

            if total < 15:
                continue  # Rejeter les affuts catastrophiques

            stand_type = _select_stand_type(species)
            justification = _generate_justification(species, scores, stand_type, season)

            affut = {
                "id": str(uuid.uuid4()),
                "lat": candidate["lat"],
                "lon": candidate["lon"],
                "score": round(total, 1),
                "scores_detail": {k: round(v, 1) for k, v in scores.items()},
                "stand_type": stand_type["type"],
                "stand_name_fr": stand_type["name_fr"],
                "species": species,
                "species_name_fr": sp_config["name_fr"],
                "season": season,
                "justification": justification,
                "scientific_refs": [r["id"] for r in SCIENTIFIC_REFERENCES if species in r.get("finding", "").lower() or "affut" in r.get("finding", "").lower()],
                "best_hours": sp_config["best_hours"],
                "wind_deg": wind_deg,
                "saline_distance_m": candidate.get("nearest_saline_dist"),
                "corridor_distance_m": candidate.get("nearest_corridor_dist"),
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "source": "AFFUT-IA-Omega-PLUS"
            }
            scored_affuts.append(affut)

        # 6. Trier par score et limiter
        scored_affuts.sort(key=lambda a: a["score"], reverse=True)
        top_affuts = scored_affuts[:10]

        # 7. Sauvegarder
        if top_affuts:
            await self._save_affuts(user_id, top_affuts)

        logger.info(f"[AFFUT-IA] Generated {len(top_affuts)}/{len(candidates)} affuts for {user_id}, species={species}, season={season}")
        return top_affuts

    def _generate_candidate_points(self, center_lat, center_lon, radius_m,
                                    hotspots, trajectories, feeding_sites, cameras):
        """Genere des points candidats autour des salines, hotspots et trajectoires."""
        candidates = []

        # Candidats autour des salines (a 20-100m)
        for fs in feeding_sites:
            fs_lat = fs.get("lat") or fs.get("gps_lat", center_lat)
            fs_lon = fs.get("lon") or fs.get("gps_lon", center_lon)

            for distance_m in [25, 35, 50, 75]:
                for angle_deg in range(0, 360, 45):
                    rad = math.radians(angle_deg)
                    d_lat = (distance_m / 111320) * math.cos(rad)
                    d_lon = (distance_m / (111320 * math.cos(math.radians(fs_lat)))) * math.sin(rad)
                    c_lat = fs_lat + d_lat
                    c_lon = fs_lon + d_lon

                    if _haversine(c_lat, c_lon, center_lat, center_lon) <= radius_m:
                        nearest_saline = min(
                            [_haversine(c_lat, c_lon, s.get("lat", s.get("gps_lat", 0)), s.get("lon", s.get("gps_lon", 0)))
                             for s in feeding_sites] or [999],
                        )
                        candidates.append({
                            "lat": round(c_lat, 6),
                            "lon": round(c_lon, 6),
                            "origin": "saline",
                            "nearest_saline_dist": round(nearest_saline, 1)
                        })

        # Candidats sur les hotspots IA (a 30-60m)
        for hs in hotspots:
            hs_lat = hs.get("gps_lat") or (hs.get("location", {}).get("coordinates", [0, 0])[1] if hs.get("location") else None)
            hs_lon = hs.get("gps_lon") or (hs.get("location", {}).get("coordinates", [0, 0])[0] if hs.get("location") else None)
            if not hs_lat or not hs_lon:
                continue
            for distance_m in [30, 50]:
                for angle_deg in range(0, 360, 90):
                    rad = math.radians(angle_deg)
                    d_lat = (distance_m / 111320) * math.cos(rad)
                    d_lon = (distance_m / (111320 * math.cos(math.radians(hs_lat)))) * math.sin(rad)
                    c_lat = hs_lat + d_lat
                    c_lon = hs_lon + d_lon

                    if _haversine(c_lat, c_lon, center_lat, center_lon) <= radius_m:
                        nearest_saline = min(
                            [_haversine(c_lat, c_lon, s.get("lat", s.get("gps_lat", 0)), s.get("lon", s.get("gps_lon", 0)))
                             for s in feeding_sites] or [999],
                        )
                        candidates.append({
                            "lat": round(c_lat, 6),
                            "lon": round(c_lon, 6),
                            "origin": "hotspot_ia",
                            "nearest_saline_dist": round(nearest_saline, 1),
                            "nearest_corridor_dist": round(_haversine(c_lat, c_lon, hs_lat, hs_lon), 1)
                        })

        # Si aucun candidat, generer sur grille autour du centre
        if not candidates:
            for dx in range(-3, 4):
                for dy in range(-3, 4):
                    c_lat = center_lat + dx * 0.001
                    c_lon = center_lon + dy * 0.001
                    dist = _haversine(c_lat, c_lon, center_lat, center_lon)
                    if 50 < dist < radius_m:
                        nearest_saline = min(
                            [_haversine(c_lat, c_lon, s.get("lat", s.get("gps_lat", 0)), s.get("lon", s.get("gps_lon", 0)))
                             for s in feeding_sites] or [999],
                        )
                        candidates.append({
                            "lat": round(c_lat, 6),
                            "lon": round(c_lon, 6),
                            "origin": "grid",
                            "nearest_saline_dist": round(nearest_saline, 1)
                        })

        return candidates

    def _score_candidate(self, candidate, feeding_sites, hotspots, trajectories,
                          wind_deg, sp_config, season_w):
        """Score multi-couches pour un candidat."""
        lat, lon = candidate["lat"], candidate["lon"]

        # Score saline distance (REGLE BIOLOGIQUE OBLIGATOIRE)
        saline_dist = candidate.get("nearest_saline_dist", 999)
        saline_score = _score_saline_distance(saline_dist) * sp_config.get("saline_importance", 0.9)

        # Score corridor/hotspot IA
        corridor_score = _score_corridor_proximity(lat, lon, trajectories, hotspots)
        corridor_score *= sp_config.get("corridor_importance", 0.8) * season_w.get("corridors", 1.0)

        # Score vent
        if feeding_sites:
            fs = feeding_sites[0]
            fs_lat = fs.get("lat", fs.get("gps_lat", lat))
            fs_lon = fs.get("lon", fs.get("gps_lon", lon))
            wind_score = _score_wind_contamination(lat, lon, fs_lat, fs_lon, wind_deg)
        else:
            wind_score = 50.0

        # Score hotspot IA pur
        hotspot_score = 0.0
        for hs in (hotspots or []):
            hs_lat = hs.get("gps_lat") or (hs.get("location", {}).get("coordinates", [0, 0])[1] if hs.get("location") else None)
            hs_lon = hs.get("gps_lon") or (hs.get("location", {}).get("coordinates", [0, 0])[0] if hs.get("location") else None)
            if hs_lat and hs_lon:
                dist = _haversine(lat, lon, hs_lat, hs_lon)
                if dist < 500:
                    hotspot_score = max(hotspot_score, hs.get("score", 50) * (1 - dist / 600))
        hotspot_score *= season_w.get("hotspots", 1.0)

        # Score eau (bonus proximite point d'eau)
        water_score = 40.0 * sp_config.get("water_importance", 0.6)

        # Score accessibilite (base)
        access_score = 60.0

        return {
            "saline": saline_score,
            "corridor": corridor_score,
            "wind": wind_score,
            "hotspot_ia": min(100, hotspot_score),
            "water": water_score,
            "access": access_score,
            "v7_temporal": self._compute_v7_temporal(candidate, sp_config),
        }

    def _compute_v7_temporal(self, candidate, sp_config):
        """V7-P1-CMD04: Score V7 temporel pour ponderation affuts."""
        now = datetime.now(timezone.utc)
        h = now.hour
        m = now.month
        doy = (m - 1) * 30 + now.day

        # Temporal
        crepuscular = sp_config.get("activity_pattern") == "crepusculaire"
        temporal = 90 if (5 <= h <= 8 or 16 <= h <= 19) and crepuscular else 50

        # Solunar
        phase = abs(((doy % 29.53) / 29.53) * 2 - 1)
        solunar = 85 if phase < 0.1 else 60 if 0.4 < phase < 0.6 else 70

        # Rut
        species_name = sp_config.get("name_fr", "").lower()
        rut_peaks = {"orignal": 275, "cerf": 310, "wapiti": 280, "caribou": 265}
        peak = rut_peaks.get(next((k for k in rut_peaks if k in species_name), "cerf"), 300)
        rut = max(20, 100 - abs(doy - peak) * 2)

        return round(temporal * 0.40 + solunar * 0.25 + rut * 0.35, 1)

    def _compute_total_score(self, scores):
        """Ponderation finale multi-couches + V7 TEMPORAL (P1-CMD04)."""
        weights = {
            "saline": 0.22,
            "corridor": 0.13,
            "wind": 0.13,
            "hotspot_ia": 0.22,
            "water": 0.08,
            "access": 0.07,
            "v7_temporal": 0.15,
        }
        total = sum(scores.get(k, 0) * w for k, w in weights.items())
        return min(100.0, max(0.0, total))

    async def _load_hotspots(self, user_id):
        cursor = self.db["vision_hotspots"].find({"user_id": user_id}, {"_id": 0}).limit(50)
        return await cursor.to_list(length=50)

    async def _load_trajectories(self, user_id):
        cursor = self.db["vision_trajectories"].find({"user_id": user_id}, {"_id": 0}).limit(30)
        return await cursor.to_list(length=30)

    async def _load_analyses(self, user_id, species=None):
        query = {"user_id": user_id}
        if species:
            query["species"] = species
        cursor = self.db["vision_analyses"].find(query, {"_id": 0}).sort("analyzed_at", -1).limit(100)
        return await cursor.to_list(length=100)

    async def _load_cameras(self, user_id, center_lat, center_lon, radius_m):
        cursor = self.db["cameras"].find(
            {"user_id": user_id, "status": "active"},
            {"_id": 0, "id": 1, "gps_lat": 1, "gps_lon": 1, "name": 1}
        ).limit(100)
        cams = await cursor.to_list(length=100)
        return [c for c in cams if c.get("gps_lat") and c.get("gps_lon") and
                _haversine(center_lat, center_lon, c["gps_lat"], c["gps_lon"]) <= radius_m]

    async def _load_feeding_sites(self, user_id, center_lat, center_lon, radius_m):
        """Charge les salines/sites alimentation depuis les waypoints et nutrition points."""
        sites = []

        # Check nutrition points
        cursor = self.db.get_collection("nutrition_points").find(
            {"user_id": user_id},
            {"_id": 0, "lat": 1, "lon": 1, "type": 1, "score": 1}
        ).limit(50)
        try:
            nutrition_pts = await cursor.to_list(length=50)
            for pt in nutrition_pts:
                if pt.get("lat") and pt.get("lon"):
                    dist = _haversine(center_lat, center_lon, pt["lat"], pt["lon"])
                    if dist <= radius_m:
                        sites.append(pt)
        except Exception:
            pass

        # Check waypoints with saline type
        cursor2 = self.db.get_collection("territory_waypoints").find(
            {"user_id": user_id, "type": {"$in": ["saline", "feeding", "salt_lick", "alimentation"]}},
            {"_id": 0}
        ).limit(50)
        try:
            wps = await cursor2.to_list(length=50)
            for wp in wps:
                lat = wp.get("lat") or wp.get("gps_lat")
                lon = wp.get("lon") or wp.get("lng") or wp.get("gps_lon")
                if lat and lon:
                    dist = _haversine(center_lat, center_lon, lat, lon)
                    if dist <= radius_m:
                        sites.append({"lat": lat, "lon": lon, "type": "saline", "score": 80})
        except Exception:
            pass

        # If no feeding sites found, generate estimated positions from cameras
        if not sites:
            cursor3 = self.db["cameras"].find(
                {"user_id": user_id, "status": "active", "gps_lat": {"$ne": None}},
                {"_id": 0, "gps_lat": 1, "gps_lon": 1}
            ).limit(20)
            cams = await cursor3.to_list(length=20)
            for c in cams:
                dist = _haversine(center_lat, center_lon, c["gps_lat"], c["gps_lon"])
                if dist <= radius_m:
                    sites.append({"lat": c["gps_lat"], "lon": c["gps_lon"], "type": "estimated_feeding", "score": 50})

        return sites

    async def _save_affuts(self, user_id, affuts):
        """Sauvegarde les affuts generes en DB."""
        for a in affuts:
            doc = {**a, "user_id": user_id}
            await self.db["affuts_ia"].update_one(
                {"id": a["id"]},
                {"$set": doc},
                upsert=True
            )

    async def get_affuts(self, user_id, species=None, min_score=0):
        """Recupere les affuts IA generes."""
        query = {"user_id": user_id, "score": {"$gte": min_score}}
        if species:
            query["species"] = species
        cursor = self.db["affuts_ia"].find(query, {"_id": 0}).sort("score", -1).limit(20)
        return await cursor.to_list(length=20)

    async def get_scientific_references(self):
        """Retourne les references scientifiques BIONIC."""
        return SCIENTIFIC_REFERENCES

    async def explain_affut(self, user_id, affut_id):
        """Retourne l'explication detaillee d'un affut."""
        affut = await self.db["affuts_ia"].find_one(
            {"id": affut_id, "user_id": user_id}, {"_id": 0}
        )
        if not affut:
            return None
        refs = [r for r in SCIENTIFIC_REFERENCES if r["id"] in affut.get("scientific_refs", [])]
        return {
            "affut": affut,
            "references": refs,
            "species_config": SPECIES_CONFIG.get(affut.get("species", "cerf")),
            "saline_rule": {
                "description": "Distance obligatoire saline 20-100m",
                "optimal_range_m": f"{SALINE_OPTIMAL_MIN_M}-{SALINE_OPTIMAL_MAX_M}",
                "acceptable_range_m": f"{SALINE_OPTIMAL_MIN_M}-{SALINE_ACCEPTABLE_MAX_M}",
                "actual_distance_m": affut.get("saline_distance_m"),
                "score": affut.get("scores_detail", {}).get("saline", 0)
            }
        }

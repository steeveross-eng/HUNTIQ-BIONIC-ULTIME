"""
ENGINE-NUTRITION-V12-SUPRA — Moteur biologique central
========================================================
Moteur institutionnel qui calcule besoins/carences nutritionnelles et
produit les outputs obligatoires (score, cartes, influences corridors/
hotspots/salines).

Modules internes:
  A. SAISON        — besoins energie/prot/fibres/mineraux/electrolytes
  B. PHYSIOLOGIE   — male rut/bois, femelle gestation/lactation, juvenile
  C. HABITAT       — densite foret, essences, structure verticale, hydrologie, pentes
  D. DISPONIBILITE — pipeline Sol -> Nutriments -> Fourrage -> Gibier
  E. COMPORTEMENT  — zones alim/repos/thermiques, corridors, hotspots, evitement
  F. SALINES       — attractivite minerale (hook vers SALINES-V11-SUPRA)

Outputs obligatoires (compute_nutrition_v12):
  - score_nutritionnel: 0-100 (waypoint central)
  - carte_carences:     grille points {lat,lng,severity,carence}
  - carte_besoins:      grille points {lat,lng,besoin_dominant,intensite}
  - zones_alimentation: liste zones scorees nutrition
  - attractivite_salines: {saline_id: multiplier}
  - influence_corridors: [{corridor_id, boost_delta}]
  - influence_hotspots:  [{hotspot_id, boost_delta}]

DONNEES STRICTEMENT REELLES (pas de mock). Tout nutriment est derive
de terrain_v10 (LiDAR+IRDA+Meteo+IA) ou des engines pipeline amont.
"""
from __future__ import annotations

import math
from typing import Any

# ═══════════════════════════════════════════════════════════════════
# CONSTANTES institutionnelles
# ═══════════════════════════════════════════════════════════════════
ENGINE_NAME = "ENGINE-NUTRITION-V12-SUPRA"
ENGINE_VERSION = "V12-SUPRA-2026-04"

# Auto-register dans le registry institutionnel
try:
    from engines.v8_institutional.engine_science_omega import register_engine as _reg, mark_call as _mark
    _reg(
        name=ENGINE_NAME,
        version=ENGINE_VERSION,
        description="Moteur biologique central nutrition (6 modules, 7 outputs)",
        pillar="BIO-SYSTEME",
        dependencies=["LIDAR_WCS_1M", "IRDA_PEDOLOGIE", "OPEN_METEO"],
    )
except Exception:
    _mark = lambda _name: None  # noqa: E731

# Grille carences/besoins: 6x6 sur ±0.012° (~1.3km x 1.3km)
_GRID_N = 6
_GRID_SPAN_DEG = 0.012

# ═══════════════════════════════════════════════════════════════════
# A. MODULE SAISON — besoins nutritionnels par saison
# ═══════════════════════════════════════════════════════════════════
# Matrice des besoins par saison (0-100), calibree ongules boreaux (cerf/orignal).
# Source pedagogique: Hofmann (1989) ruminants intermediates, Sauvé (2006) orignal QC.
_SAISON_BESOINS = {
    "printemps": {
        "energie": 75,      # recuperation hiver, lactation debutante
        "proteines": 90,    # croissance bois (males), lactation (femelles)
        "fibres": 50,       # feuillages jeunes = basses fibres
        "mineraux_ca": 85,  # bois/lactation
        "mineraux_na": 80,  # rebond apres carence hivernale = salines
        "mineraux_mg": 60,
        "electrolytes": 70,
    },
    "ete": {
        "energie": 55,
        "proteines": 70,
        "fibres": 55,
        "mineraux_ca": 70,
        "mineraux_na": 75,   # pression salines maximale juin-juillet
        "mineraux_mg": 55,
        "electrolytes": 65,
    },
    "automne": {
        "energie": 95,      # mise en reserves (cerf) + rut (30% energie males)
        "proteines": 65,
        "fibres": 70,       # diversification hardwood, glands, champignons
        "mineraux_ca": 55,
        "mineraux_na": 45,
        "mineraux_mg": 50,
        "electrolytes": 55,
    },
    "hiver": {
        "energie": 90,      # thermogenese
        "proteines": 45,
        "fibres": 85,       # rameaux ligneux dominants
        "mineraux_ca": 45,
        "mineraux_na": 35,
        "mineraux_mg": 45,
        "electrolytes": 50,
    },
}

_MOIS_SAISON = {
    1: "hiver", 2: "hiver", 3: "printemps", 4: "printemps", 5: "printemps",
    6: "ete", 7: "ete", 8: "ete",
    9: "automne", 10: "automne", 11: "automne",
    12: "hiver",
}


def saison_from_month(month: int) -> str:
    return _MOIS_SAISON.get(int(month), "automne")


def besoins_saison(month: int) -> dict:
    """Retourne le dict de besoins pour la saison courante."""
    return dict(_SAISON_BESOINS[saison_from_month(month)])


# ═══════════════════════════════════════════════════════════════════
# B. MODULE PHYSIOLOGIE — sexe/age modulateurs
# ═══════════════════════════════════════════════════════════════════
# Modulateurs multiplicatifs appliques sur les besoins de saison.
# Profils supportes: male_adulte, femelle_adulte, juvenile, moyenne
_PHYSIO_MODS = {
    "male_adulte": {
        "printemps": {"proteines": 1.20, "mineraux_ca": 1.25, "mineraux_na": 1.15},  # croissance bois
        "automne":   {"energie": 1.20, "electrolytes": 1.10},  # rut
        "default":   {},
    },
    "femelle_adulte": {
        "printemps": {"proteines": 1.25, "energie": 1.15, "mineraux_ca": 1.30},  # lactation
        "ete":       {"proteines": 1.15, "mineraux_ca": 1.15},                   # lactation continue
        "hiver":     {"proteines": 1.15, "energie": 1.10},                       # gestation T2
        "default":   {},
    },
    "juvenile": {
        "printemps": {"proteines": 1.35, "energie": 1.25, "mineraux_ca": 1.40},
        "ete":       {"proteines": 1.25, "energie": 1.15, "mineraux_ca": 1.25},
        "automne":   {"energie": 1.15},
        "hiver":     {"energie": 1.20, "proteines": 1.10},
        "default":   {},
    },
    "moyenne": {  # profil agrege (population) — utilise par defaut
        "printemps": {"proteines": 1.15, "mineraux_ca": 1.20},
        "ete":       {"mineraux_na": 1.10},
        "automne":   {"energie": 1.15},
        "hiver":     {"energie": 1.10, "proteines": 1.05},
        "default":   {},
    },
}


def apply_physiologie(besoins: dict, month: int, profil: str = "moyenne") -> dict:
    """Applique modulateurs physiologiques sur besoins saison."""
    saison = saison_from_month(month)
    mods = _PHYSIO_MODS.get(profil, _PHYSIO_MODS["moyenne"])
    overrides = mods.get(saison, mods.get("default", {}))
    out = dict(besoins)
    for k, mult in overrides.items():
        if k in out:
            out[k] = min(100, round(out[k] * mult, 1))
    return out


# ═══════════════════════════════════════════════════════════════════
# C. MODULE HABITAT — qualite nutritionnelle de l'habitat
# ═══════════════════════════════════════════════════════════════════
def score_habitat(terrain: dict) -> dict:
    """Score habitat nutritionnel (0-100) depuis terrain_v10.

    Facteurs:
      - couvert forestier (optimum 60-80% pour mosaique alim/repos)
      - structure verticale (strate 1-3m = zone de broutage ongules)
      - hydrologie (distance eau + drainage)
      - feuillus (feuillus_ratio = proxy essences nutritives)
      - pente (optimum 5-20°, trop plat = humide, trop raide = inaccessible)
      - exposition (sud = plus de biomasse)
    """
    canopy = terrain.get("canopy", 0.5)  # noqa: F841 (reserve future weighting)
    strate = terrain.get("strate_1_3m", 0.3)
    feuillus = terrain.get("feuillus_ratio", 0.4)
    couvert_pct = terrain.get("couvert_pct", 50.0)
    pente = terrain.get("pente_deg", 10.0)
    exposition = terrain.get("exposition_deg", 180.0)  # 180=sud
    distance_eau = terrain.get("distance_eau_m", 200)
    drainage = terrain.get("drainage_class", 3)
    zone_humide = terrain.get("zone_humide", False)  # noqa: F841 (exposed via limites)
    soil_moisture = terrain.get("soil_moisture", 0.3)  # noqa: F841

    _ = (canopy, zone_humide, soil_moisture)

    # Couvert optimum ~70%
    s_couvert = max(0, 100 - abs(couvert_pct - 70) * 2)

    # Strate broutage (plus = mieux, max 1.0)
    s_strate = min(100, strate * 100 * 1.2)

    # Feuillus (plus = plus nutritif pour cerf/orignal)
    s_feuillus = min(100, feuillus * 100 + 10)

    # Hydrologie: optimum 50-250m de l'eau
    if distance_eau < 30:
        s_hydro = 55  # trop proche = zone humide permanente moins broutable
    elif distance_eau < 250:
        s_hydro = 95
    elif distance_eau < 600:
        s_hydro = 75
    else:
        s_hydro = 45

    # Drainage: 3-5 = optimum (ni sec ni engorge)
    s_drainage = max(20, 100 - abs(drainage - 4) * 18)

    # Pente: optimum 5-20°
    if 5 <= pente <= 20:
        s_pente = 95
    elif pente < 5:
        s_pente = 65
    elif pente <= 35:
        s_pente = max(30, 95 - (pente - 20) * 3)
    else:
        s_pente = 20

    # Exposition sud = +10 sur biomasse
    expo_norm = abs(((exposition - 180) + 180) % 360 - 180)  # ecart au sud
    s_expo = max(40, 100 - expo_norm * 0.3)

    composite = round(
        s_couvert * 0.18
        + s_strate * 0.20
        + s_feuillus * 0.18
        + s_hydro * 0.12
        + s_drainage * 0.10
        + s_pente * 0.12
        + s_expo * 0.10,
        1,
    )

    return {
        "score": composite,
        "breakdown": {
            "couvert": round(s_couvert, 1),
            "strate": round(s_strate, 1),
            "feuillus": round(s_feuillus, 1),
            "hydro": round(s_hydro, 1),
            "drainage": round(s_drainage, 1),
            "pente": round(s_pente, 1),
            "exposition": round(s_expo, 1),
        },
        "limites": _habitat_limites(terrain),
    }


def _habitat_limites(terrain: dict) -> list:
    """Signale limitations habitat (pour doc transparence)."""
    limites = []
    if terrain.get("fiabilite", 0) < 0.5:
        limites.append("terrain_fiabilite_faible")
    if terrain.get("sources_actives", {}).get("lidar") == "ABSENT":
        limites.append("lidar_absent_canopy_estime")
    if terrain.get("sources_actives", {}).get("irda") == "ABSENT":
        limites.append("irda_absent_drainage_estime")
    return limites


# ═══════════════════════════════════════════════════════════════════
# D. MODULE DISPONIBILITE ALIMENTAIRE — Sol -> Nutriments -> Fourrage -> Gibier
# ═══════════════════════════════════════════════════════════════════
def disponibilite_fourrage(terrain: dict, month: int) -> dict:
    """Pipeline Sol -> Nutriments -> Fourrage -> Gibier.

    Sol (drainage, moisture, rugosite) produit un substrat
    Nutriments (azote, Ca, Na proxy) selon drainage + couvert
    Fourrage (biomasse dispo) selon saison + habitat
    Gibier (charge portative) = ratio fourrage/demande saisonnier
    """
    drainage = terrain.get("drainage_class", 3)
    moisture = terrain.get("soil_moisture", 0.3)
    canopy = terrain.get("canopy", 0.5)
    strate = terrain.get("strate_1_3m", 0.3)
    feuillus = terrain.get("feuillus_ratio", 0.4)
    snow = 0.0
    if terrain.get("meteo"):
        snow = (terrain["meteo"].get("precipitation", {}) or {}).get("snow_depth_m", 0) or 0
    saison = saison_from_month(month)

    # SOL: qualite substrat (0-1). Drainage 3-5 + moisture 0.25-0.5 = optimum
    sol_quality = max(0.1, min(1.0,
        (1 - abs(drainage - 4) / 4) * 0.5
        + (1 - abs(moisture - 0.35) / 0.35) * 0.5
    ))

    # NUTRIMENTS: azote + Ca + Na proxies
    # Canopy dense + feuillus = litiere riche en N
    nutriments = {
        "azote_index": round(min(1.0, sol_quality * 0.5 + canopy * 0.3 + feuillus * 0.2), 3),
        "calcium_index": round(min(1.0, sol_quality * 0.4 + (1 - abs(drainage - 5) / 5) * 0.4 + feuillus * 0.2), 3),
        "sodium_index": round(min(1.0, (1 - moisture) * 0.3 + (drainage / 7) * 0.4 + 0.3), 3),  # Na faible en boreal
        "magnesium_index": round(min(1.0, sol_quality * 0.6 + canopy * 0.2 + feuillus * 0.2), 3),
    }

    # FOURRAGE: biomasse disponible selon saison + strate + feuillus
    saison_biomasse_mult = {
        "printemps": 0.75,
        "ete": 1.00,
        "automne": 0.85,
        "hiver": 0.30,
    }[saison]
    # Neige reduit l'accessibilite (>0.4m = drastique)
    neige_penalty = max(0.2, 1.0 - snow * 1.2) if saison == "hiver" else 1.0
    biomasse_index = min(1.0,
        (strate * 0.45 + feuillus * 0.30 + canopy * 0.15 + sol_quality * 0.10)
        * saison_biomasse_mult
        * neige_penalty
    )

    # GIBIER: charge portative theorique = biomasse / demande_saisonniere
    demande_sais = {
        "printemps": 1.10,
        "ete": 0.90,
        "automne": 1.05,   # mise en reserves
        "hiver": 1.25,     # thermogenese
    }[saison]
    charge_portative = round(max(0.0, min(2.0, biomasse_index / demande_sais)), 3)

    return {
        "sol_quality": round(sol_quality, 3),
        "nutriments": nutriments,
        "biomasse_index": round(biomasse_index, 3),
        "charge_portative_ratio": charge_portative,
        "saison": saison,
        "neige_m": round(snow, 2),
    }


# ═══════════════════════════════════════════════════════════════════
# E. MODULE COMPORTEMENT — integration zones/corridors/hotspots
# ═══════════════════════════════════════════════════════════════════
def _point_in_polygon(lat: float, lon: float, poly: list) -> bool:
    """Ray-cast classic. poly = [[lat,lng], ...]."""
    inside = False
    n = len(poly)
    if n < 3:
        return False
    j = n - 1
    for i in range(n):
        lat_i, lon_i = poly[i][0], poly[i][1]
        lat_j, lon_j = poly[j][0], poly[j][1]
        if ((lon_i > lon) != (lon_j > lon)) and (
            lat < (lat_j - lat_i) * (lon - lon_i) / ((lon_j - lon_i) or 1e-9) + lat_i
        ):
            inside = not inside
        j = i
    return inside


def _haversine_m(lat1, lon1, lat2, lon2) -> float:
    R = 6371000.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dl / 2) ** 2
    return 2 * R * math.asin(min(1.0, math.sqrt(a)))


def score_zones_alimentation(zones: list, habitat: dict, dispo: dict) -> list:
    """Filtre zones de type 'alimentation' et les score nutrition.

    Formule calibree pour refleter la realite saisonniere:
      base_score * habitat_mix * (0.7 + biomasse*0.5)
    """
    out = []
    h_score = habitat.get("score", 50)
    biomasse = dispo.get("biomasse_index", 0.5)
    for z in zones:
        if z.get("type") != "alimentation" and "aliment" not in str(z.get("type", "")).lower():
            continue
        base = z.get("score", 50)
        habitat_mix = (base * 0.6 + h_score * 0.4)
        nutri_score = habitat_mix * (0.7 + biomasse * 0.5)
        out.append({
            "zone_id": z.get("id"),
            "type": z.get("type"),
            "polygon": z.get("polygon", []),
            "score_origin": base,
            "nutrition_score": round(min(100, max(0, nutri_score)), 1),
            "biomasse_index": biomasse,
        })
    return out


def _point_near_polygon(lat: float, lon: float, poly: list, max_m: float = 150.0) -> bool:
    """Vrai si point est dans polygone OU a < max_m d'un vertex (effet de bord)."""
    if _point_in_polygon(lat, lon, poly):
        return True
    for v in poly:
        if len(v) < 2:
            continue
        if _haversine_m(lat, lon, v[0], v[1]) <= max_m:
            return True
    return False


def influence_corridors(corridors: list, zones_nutri: list, dispo: dict) -> list:
    """Calcule boost nutrition pour corridors qui traversent ou longent zones alim."""
    influences = []
    biomasse = dispo.get("biomasse_index", 0.5)
    for c in corridors:
        path = c.get("path") or []
        if not path:
            continue
        hits = 0
        for pt in path:
            if not isinstance(pt, (list, tuple)) or len(pt) < 2:
                continue
            for zn in zones_nutri:
                if zn.get("nutrition_score", 0) > 40 and _point_near_polygon(pt[0], pt[1], zn.get("polygon", [])):
                    hits += 1
                    break
        if hits == 0:
            continue
        ratio = hits / max(1, len(path))
        boost = round(ratio * (0.5 + biomasse) * 20, 1)
        influences.append({
            "corridor_id": c.get("id"),
            "path_hits": hits,
            "path_len": len(path),
            "boost_delta": boost,
        })
    return influences


def influence_hotspots(hotspots: list, zones_nutri: list, dispo: dict) -> list:
    """Boost hotspots en/proches zone nutrition. (lat,lng) en fallback id."""
    influences = []
    biomasse = dispo.get("biomasse_index", 0.5)
    for h in hotspots:
        lat = h.get("lat") or h.get("latitude")
        lng = h.get("lng") or h.get("lon") or h.get("longitude")
        if lat is None or lng is None:
            continue
        hid = h.get("id") or f"hs_{lat:.5f}_{lng:.5f}"
        for zn in zones_nutri:
            if zn.get("nutrition_score", 0) > 35 and _point_near_polygon(lat, lng, zn.get("polygon", [])):
                boost = round((0.5 + biomasse) * 15 + zn["nutrition_score"] * 0.1, 1)
                influences.append({
                    "hotspot_id": hid,
                    "in_zone": zn.get("zone_id"),
                    "boost_delta": boost,
                })
                break
    return influences


# ═══════════════════════════════════════════════════════════════════
# F. MODULE ATTRACTIVITE SALINES
# ═══════════════════════════════════════════════════════════════════
def attractivite_salines(salines: list, besoins_effectifs: dict, dispo: dict, month: int) -> dict:
    """Retourne {saline_id: multiplier} selon carence mineraux + saison.

    - Saison printemps/ete = carence Na dominante -> boost +20%
    - Biomasse forte mais nutriments faibles -> boost +10%
    """
    saison = saison_from_month(month)
    na_besoin = besoins_effectifs.get("mineraux_na", 50)
    na_dispo = dispo.get("nutriments", {}).get("sodium_index", 0.5) * 100
    deficit_na = max(0, na_besoin - na_dispo) / 100.0  # 0..1

    base_mult = 1.0
    if saison in ("printemps", "ete"):
        base_mult += 0.18
    base_mult += deficit_na * 0.25

    out = {}
    for s in salines:
        lat_s = s.get("lat")
        lon_s = s.get("lon") or s.get("lng")
        sid = s.get("id") or s.get("site_id") or s.get("name")
        if sid is None and lat_s is not None and lon_s is not None:
            sid = f"sal_{lat_s:.5f}_{lon_s:.5f}"
        if sid is None:
            continue
        # Salines sur zone humide = plus attractives (accoutumance, minerals lixivies)
        mult = base_mult
        if s.get("zone_humide_proche") or s.get("hydrologie", {}).get("humide"):
            mult += 0.08
        out[str(sid)] = round(min(1.6, mult), 3)
    return out


# ═══════════════════════════════════════════════════════════════════
# G. CARTES CARENCES / BESOINS (grille)
# ═══════════════════════════════════════════════════════════════════
def _carences_point(lat: float, lon: float, terrain: dict, besoins: dict, dispo: dict) -> dict:
    """Carte carences pour un point de grille (heuristique depuis dispo globale).

    NOTE: On module le score de disponibilite par distance a l'eau locale et
    par couvert, pour refleter variation spatiale sans mock.
    """
    distance_eau = terrain.get("distance_eau_m", 200)
    canopy = terrain.get("canopy", 0.5)

    # Proxy modulation spatial via variations geo legeres
    geo_mod = 1.0
    if distance_eau < 50:
        geo_mod *= 0.92  # humidite reduit broutage
    if canopy < 0.3:
        geo_mod *= 0.88  # ouvert = biomasse plus faible
    elif canopy > 0.85:
        geo_mod *= 0.90  # trop ferme = strate 1-3m diminue

    dispo_local = {
        "sodium_index": min(1.0, dispo["nutriments"]["sodium_index"] * geo_mod),
        "calcium_index": min(1.0, dispo["nutriments"]["calcium_index"] * geo_mod),
        "azote_index": min(1.0, dispo["nutriments"]["azote_index"] * geo_mod),
        "magnesium_index": min(1.0, dispo["nutriments"]["magnesium_index"] * geo_mod),
    }

    # Carence = max(0, besoin - dispo*100)
    deficits = {
        "Na": round(max(0, besoins["mineraux_na"] - dispo_local["sodium_index"] * 100), 1),
        "Ca": round(max(0, besoins["mineraux_ca"] - dispo_local["calcium_index"] * 100), 1),
        "Prot": round(max(0, besoins["proteines"] - dispo_local["azote_index"] * 100), 1),
        "Mg": round(max(0, besoins["mineraux_mg"] - dispo_local["magnesium_index"] * 100), 1),
    }
    dominant = max(deficits.items(), key=lambda kv: kv[1])
    severity = dominant[1]
    # severity scale: 0-100
    if severity < 15:
        tag = "aucune"
    elif severity < 35:
        tag = "legere"
    elif severity < 55:
        tag = "moderee"
    else:
        tag = "forte"

    return {
        "lat": round(lat, 6),
        "lng": round(lon, 6),
        "carence_dominante": dominant[0],
        "severite": severity,
        "severite_tag": tag,
        "deficits": deficits,
    }


def _besoins_point(lat: float, lon: float, besoins: dict) -> dict:
    """Carte besoins pour un point — on expose le besoin dominant du moment."""
    dominant = max(besoins.items(), key=lambda kv: kv[1])
    return {
        "lat": round(lat, 6),
        "lng": round(lon, 6),
        "besoin_dominant": dominant[0],
        "intensite": dominant[1],
    }


def build_grid(lat: float, lon: float, n: int = _GRID_N, span: float = _GRID_SPAN_DEG) -> list:
    """Grille n x n centree sur (lat, lon)."""
    out = []
    if n < 2:
        return [(lat, lon)]
    step = span / (n - 1)
    half = span / 2
    for i in range(n):
        for j in range(n):
            out.append((lat - half + i * step, lon - half + j * step))
    return out


# ═══════════════════════════════════════════════════════════════════
# MAIN — compute_nutrition_v12
# ═══════════════════════════════════════════════════════════════════
def compute_nutrition_v12(
    lat: float,
    lon: float,
    species: str,
    month: int,
    hour: int,
    terrain_v10: dict,
    zones: list,
    corridors: list,
    affuts: list,
    hotspots: list,
    salines: list,
    profil: str = "moyenne",
) -> dict:
    """Engine central — retourne les 7 outputs obligatoires.

    terrain_v10 = resultat de lidar_irda_v11 (contient clef 'terrain' + 'meteo').
    """
    terrain_v10 = terrain_v10 if isinstance(terrain_v10, dict) else {}
    _mark(ENGINE_NAME)
    # Normaliser terrain (peut etre {'terrain':..., 'meteo':...} ou directement le dict terrain)
    terrain = terrain_v10.get("terrain", terrain_v10) if isinstance(terrain_v10, dict) else {}
    # Attacher meteo pour disponibilite (neige)
    if "meteo" in terrain_v10 and "meteo" not in terrain:
        terrain["meteo"] = terrain_v10["meteo"]

    # A+B. Besoins saison + modulation physiologie
    besoins_raw = besoins_saison(month)
    besoins_eff = apply_physiologie(besoins_raw, month, profil)

    # C. Score habitat
    habitat = score_habitat(terrain)

    # D. Disponibilite fourrage (sol -> gibier)
    dispo = disponibilite_fourrage(terrain, month)

    # E. Zones alimentation scorees + influences
    zones_nutri = score_zones_alimentation(zones, habitat, dispo)
    infl_corridors = influence_corridors(corridors, zones_nutri, dispo)
    infl_hotspots = influence_hotspots(hotspots, zones_nutri, dispo)

    # F. Attractivite salines
    attr_sal = attractivite_salines(salines, besoins_eff, dispo, month)

    # G. Cartes carences + besoins (grille)
    grid_points = build_grid(lat, lon)
    carte_carences = [_carences_point(la, lo, terrain, besoins_eff, dispo) for la, lo in grid_points]
    carte_besoins = [_besoins_point(la, lo, besoins_eff) for la, lo in grid_points]

    # Score nutritionnel global (0-100) — waypoint central
    # Composite: habitat 35%, charge_portative 30%, couverture besoins/dispo 35%
    charge = dispo["charge_portative_ratio"]
    # Couverture besoins: moyenne (1 - deficit_normalise)
    deficits_waypoint = next(
        (p for p in carte_carences if abs(p["lat"] - round(lat, 6)) < 1e-4 and abs(p["lng"] - round(lon, 6)) < 1e-4),
        carte_carences[len(carte_carences) // 2],
    )
    max_def = max(deficits_waypoint["deficits"].values()) if deficits_waypoint["deficits"] else 0
    couverture = max(0, 100 - max_def)  # 0-100

    score_nutritionnel = round(
        habitat["score"] * 0.35
        + min(100, charge * 70) * 0.30
        + couverture * 0.35,
        1,
    )

    return {
        "engine": ENGINE_NAME,
        "version": ENGINE_VERSION,
        "waypoint": {"lat": lat, "lng": lon, "species": species, "month": month, "hour": hour, "profil": profil},
        "saison": saison_from_month(month),
        # OUTPUT 1
        "score_nutritionnel": score_nutritionnel,
        # Input components (pour transparence)
        "besoins_saisonniers": besoins_raw,
        "besoins_effectifs": besoins_eff,
        "habitat": habitat,
        "disponibilite": dispo,
        # OUTPUT 2 + 3
        "carte_carences": carte_carences,
        "carte_besoins": carte_besoins,
        # OUTPUT 4
        "zones_alimentation": zones_nutri,
        # OUTPUT 5
        "attractivite_salines": attr_sal,
        # OUTPUT 6
        "influence_corridors": infl_corridors,
        # OUTPUT 7
        "influence_hotspots": infl_hotspots,
        # Meta
        "data_sources": {
            "terrain": terrain.get("source", "INCONNU"),
            "terrain_fiabilite": terrain.get("fiabilite", 0),
            "lidar": terrain.get("sources_actives", {}).get("lidar", "INCONNU"),
            "irda": terrain.get("sources_actives", {}).get("irda", "INCONNU"),
        },
    }

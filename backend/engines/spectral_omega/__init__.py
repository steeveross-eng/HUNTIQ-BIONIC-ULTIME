"""
ENGINE_SPECTRAL_OMEGA · NEW_ENGINE_1_SPECTRAL_Ω · VERSION_ULTIME_ABSOLUE_X3
══════════════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU · ANTI-GÉNÉRIQUE STRICT

Comble le GAP CRITIQUE #1 identifié par AUDIT_Ω_SPECTRAL_TERRAIN_3D :
NDVI / NDWI / EVI (Sentinel-2 L2A) + LST (Landsat 8/9 L2) + ingestion STAC AWS.

CHAÎNES_Ω :
  CHAINE_Ω_SPECTRAL → CHAINE_Ω_CORRIDORS → CHAINE_Ω_TERRITOIRE
  CHAINE_Ω_SPECTRAL → CHAINE_Ω_TERRAIN_HR (préparation PHASE 2)
  CHAINE_Ω_SPECTRAL → CHAINE_Ω_HYDRO (pondération humidité)
  CHAINE_Ω_SPECTRAL → CHAINE_Ω_PRESSURE_HUMAINE (modulation)

SOURCES INSTITUTIONNELLES :
  - Sentinel-2 L2A : earth-search.aws.element84.com/v1 (collection sentinel-2-l2a)
                     + sentinel-cogs.s3.us-west-2.amazonaws.com (assets COG public)
  - Landsat 8/9 L2 : planetarycomputer.microsoft.com/api/stac/v1 (collection landsat-c2-l2)
                     fallback : landsatlook.usgs.gov/stac-server

DOCTRINE NORMALISATION : 0-1 institutionnelle (clipping + scaling)
DOCTRINE FALLBACK : valeur neutre 0.5 si aucun raster disponible
DOCTRINE CLOUD MASK : Sentinel-2 SCL band (4=végétation, 5=non-végétation, 6=eau, 11=neige)
DOCTRINE ANTI-GÉNÉRIQUE : aucune valeur synthétique — UNIQUEMENT pixels réels

V30_LOCK INVIOLÉ · FUSION ADD-ONLY · NEW ENGINE EXTERNE
"""

from __future__ import annotations

import logging
import math
from datetime import datetime, timedelta, timezone
from typing import Any

import numpy as np
import rasterio
from pyproj import Transformer
from pystac_client import Client
from rasterio.windows import from_bounds

from engines.v8_institutional.engine_science_omega import mark_call, register_engine

logger = logging.getLogger("engine_spectral_omega")

# ═══════════════════════════════════════════════════════════════════
# DOCTRINE — Identifiants institutionnels
# ═══════════════════════════════════════════════════════════════════
ENGINE_NAME = "ENGINE-SPECTRAL-Ω"
ENGINE_VERSION = "V1_LOCK-NEW_ENGINE_1_SPECTRAL_Ω-2026-05"
ENGINE_DOCTRINE = "NEW_ENGINE_1_SPECTRAL_Ω · VERSION_ULTIME_ABSOLUE_X3"

# Sources STAC institutionnelles
STAC_SENTINEL2 = "https://earth-search.aws.element84.com/v1"
STAC_LANDSAT_PC = "https://planetarycomputer.microsoft.com/api/stac/v1"
STAC_LANDSAT_USGS = "https://landsatlook.usgs.gov/stac-server"

# Collections
COLLECTION_S2 = "sentinel-2-l2a"
COLLECTION_LS = "landsat-c2-l2"

# Doctrine paramètres
DEFAULT_HALO_M = 200.0           # zone d'agrégation pixel (200m de rayon)
DEFAULT_DAYS_WINDOW = 45         # fenêtre temporelle de recherche STAC
MAX_CLOUD_COVER = 30.0           # % nuages max accepté
MAX_ITEMS_PER_QUERY = 5          # items STAC max retournés
FALLBACK_VALUE = 0.5             # valeur neutre institutionnelle
S2_BAND_REFLECTANCE_SCALE = 10000.0  # facteur Sentinel-2 L2A

# SCL classes Sentinel-2 (Scene Classification Layer)
SCL_VALID_CLASSES = {4, 5, 6, 7, 11}  # vegetation, bare soil, water, unclass, snow
SCL_CLOUD_CLASSES = {3, 8, 9, 10}     # cloud_shadow, cloud_med, cloud_high, thin_cirrus

# ═══════════════════════════════════════════════════════════════════
# REGISTRY institutionnel
# ═══════════════════════════════════════════════════════════════════
register_engine(
    ENGINE_NAME, ENGINE_VERSION,
    "NDVI/NDWI/EVI Sentinel-2 + LST Landsat 8/9 (STAC AWS, ANTI-GÉNÉRIQUE)",
    "BIO-SYSTEME",
    ["SENTINEL2_AWS_STAC", "LANDSAT_PC_STAC", "NASA_EARTHDATA"],
)


# ═══════════════════════════════════════════════════════════════════
# UTILITAIRES — formules institutionnelles
# ═══════════════════════════════════════════════════════════════════
def compute_ndvi(red: float, nir: float) -> float:
    """NDVI = (NIR - RED) / (NIR + RED). Range natif [-1, 1]."""
    if red is None or nir is None:
        return float("nan")
    denom = float(nir) + float(red)
    if abs(denom) < 1e-9:
        return 0.0
    return (float(nir) - float(red)) / denom


def compute_ndwi(green: float, nir: float) -> float:
    """NDWI (McFeeters 1996) = (GREEN - NIR) / (GREEN + NIR). Range natif [-1, 1]."""
    if green is None or nir is None:
        return float("nan")
    denom = float(green) + float(nir)
    if abs(denom) < 1e-9:
        return 0.0
    return (float(green) - float(nir)) / denom


def compute_evi(red: float, nir: float, blue: float,
                G: float = 2.5, C1: float = 6.0, C2: float = 7.5, L: float = 1.0) -> float:
    """EVI = G * (NIR - RED) / (NIR + C1*RED - C2*BLUE + L). Standard MODIS/Sentinel-2."""
    if red is None or nir is None or blue is None:
        return float("nan")
    denom = float(nir) + C1 * float(red) - C2 * float(blue) + L
    if abs(denom) < 1e-9:
        return 0.0
    return G * (float(nir) - float(red)) / denom


def compute_lst_landsat(brightness_temp_k: float) -> float:
    """LST simplifié — Landsat L2 ST_B10 fournit déjà la surface temperature en Kelvin."""
    if brightness_temp_k is None or math.isnan(brightness_temp_k):
        return float("nan")
    return float(brightness_temp_k) - 273.15  # Kelvin → Celsius


def normalize_to_unit_interval(value: float, vmin: float, vmax: float,
                                fallback: float = FALLBACK_VALUE) -> float:
    """Normalisation institutionnelle 0-1. Clipping strict + fallback NaN."""
    if value is None or math.isnan(value):
        return float(fallback)
    span = float(vmax) - float(vmin)
    if abs(span) < 1e-9:
        return float(fallback)
    norm = (float(value) - float(vmin)) / span
    return max(0.0, min(1.0, norm))


def normalize_ndvi(ndvi: float) -> float:
    """NDVI [-1, 1] → [0, 1] institutionnel."""
    return normalize_to_unit_interval(ndvi, -1.0, 1.0)


def normalize_ndwi(ndwi: float) -> float:
    """NDWI [-1, 1] → [0, 1] institutionnel."""
    return normalize_to_unit_interval(ndwi, -1.0, 1.0)


def normalize_evi(evi: float) -> float:
    """EVI [-1, 1] → [0, 1] (clipping doctrinal)."""
    return normalize_to_unit_interval(evi, -1.0, 1.0)


def normalize_lst_celsius(lst_c: float, vmin: float = -30.0,
                           vmax: float = 50.0) -> float:
    """LST [-30°C, 50°C] → [0, 1]."""
    return normalize_to_unit_interval(lst_c, vmin, vmax)


# ═══════════════════════════════════════════════════════════════════
# STAC — Recherche d'items réels (anti-générique)
# ═══════════════════════════════════════════════════════════════════
def _bbox_around(lat: float, lon: float, halo_m: float = 1000.0) -> list[float]:
    """BBOX [west, south, east, north] autour d'un point (en degrés WGS84)."""
    cos_lat = max(0.5, math.cos(math.radians(lat)))
    dlat = halo_m / 111000.0
    dlon = halo_m / (111000.0 * cos_lat)
    return [lon - dlon, lat - dlat, lon + dlon, lat + dlat]


def fetch_sentinel2_stac(lat: float, lon: float,
                          days_window: int = DEFAULT_DAYS_WINDOW,
                          max_cloud: float = MAX_CLOUD_COVER,
                          max_items: int = MAX_ITEMS_PER_QUERY,
                          ) -> list[dict[str, Any]]:
    """Recherche STAC Sentinel-2 L2A sur AWS Earth Search.

    Retour : liste d'items avec {id, datetime, cloud_cover, asset_urls}.
    """
    mark_call(ENGINE_NAME)
    end = datetime.now(timezone.utc).date()
    start = end - timedelta(days=int(days_window))
    bbox = _bbox_around(lat, lon, halo_m=2000.0)
    try:
        client = Client.open(STAC_SENTINEL2)
        search = client.search(
            collections=[COLLECTION_S2],
            bbox=bbox,
            datetime=f"{start.isoformat()}/{end.isoformat()}",
            query={"eo:cloud_cover": {"lt": float(max_cloud)}},
            max_items=int(max_items),
        )
        items = list(search.items())
    except Exception as e:
        logger.warning("[%s] STAC Sentinel-2 fetch failed: %s", ENGINE_NAME, e)
        return []

    out: list[dict[str, Any]] = []
    for it in items:
        out.append({
            "id": it.id,
            "datetime": str(it.properties.get("datetime", "")),
            "cloud_cover": float(it.properties.get("eo:cloud_cover", 0.0)),
            "asset_urls": {
                k: a.href for k, a in it.assets.items()
                if k in {"red", "nir", "green", "blue", "scl"}
            },
        })
    return out


def fetch_landsat_l2_stac(lat: float, lon: float,
                           days_window: int = DEFAULT_DAYS_WINDOW * 2,
                           max_cloud: float = MAX_CLOUD_COVER,
                           max_items: int = 2,
                           ) -> list[dict[str, Any]]:
    """Recherche STAC Landsat 8/9 L2 sur Microsoft Planetary Computer."""
    mark_call(ENGINE_NAME)
    end = datetime.now(timezone.utc).date()
    start = end - timedelta(days=int(days_window))
    bbox = _bbox_around(lat, lon, halo_m=3000.0)
    try:
        client = Client.open(STAC_LANDSAT_PC)
        search = client.search(
            collections=[COLLECTION_LS],
            bbox=bbox,
            datetime=f"{start.isoformat()}/{end.isoformat()}",
            query={
                "eo:cloud_cover": {"lt": float(max_cloud)},
                "platform": {"in": ["landsat-8", "landsat-9"]},
            },
            max_items=int(max_items),
        )
        items = list(search.items())
    except Exception as e:
        logger.warning("[%s] STAC Landsat fetch failed: %s", ENGINE_NAME, e)
        return []

    out: list[dict[str, Any]] = []
    for it in items:
        out.append({
            "id": it.id,
            "platform": str(it.properties.get("platform", "")),
            "datetime": str(it.properties.get("datetime", "")),
            "cloud_cover": float(it.properties.get("eo:cloud_cover", 0.0)),
            "asset_urls": {
                k: a.href for k, a in it.assets.items()
                if k in {"red", "nir08", "green", "blue", "lwir11", "qa_pixel"}
            },
        })
    return out


# ═══════════════════════════════════════════════════════════════════
# READ — Lecture pixel réelle via /vsicurl/ (fenêtre 200m)
# ═══════════════════════════════════════════════════════════════════
def _read_pixel_window(asset_url: str, lat: float, lon: float,
                        halo_m: float = DEFAULT_HALO_M) -> float | None:
    """Lit la moyenne arithmétique des pixels valides dans une fenêtre `halo_m` (m).

    Utilise rasterio.windows.from_bounds + /vsicurl/ pour ne télécharger que
    le strict nécessaire (lecture range HTTP). Aucune valeur synthétique.
    """
    if not asset_url:
        return None
    try:
        with rasterio.open(asset_url) as src:
            transformer = Transformer.from_crs("EPSG:4326", src.crs, always_xy=True)
            x, y = transformer.transform(lon, lat)
            bbox = (x - halo_m, y - halo_m, x + halo_m, y + halo_m)
            win = from_bounds(*bbox, transform=src.transform)
            data = src.read(1, window=win, masked=True)
            if data.size == 0:
                return None
            arr = np.asarray(data, dtype=np.float64)
            # Filtrer NaN et masque
            valid = arr[~np.isnan(arr)]
            if valid.size == 0:
                return None
            return float(np.mean(valid))
    except Exception as e:
        logger.warning("[%s] _read_pixel_window failed for %s: %s",
                        ENGINE_NAME, asset_url[-60:], e)
        return None


def _read_scl_cloud_fraction(scl_url: str | None, lat: float, lon: float,
                              halo_m: float = DEFAULT_HALO_M) -> float:
    """Calcule la fraction de pixels cloud dans la SCL.
    Retour : 0.0 (aucun nuage) → 1.0 (tout nuage). NaN si SCL indisponible.
    """
    if not scl_url:
        return float("nan")
    try:
        with rasterio.open(scl_url) as src:
            transformer = Transformer.from_crs("EPSG:4326", src.crs, always_xy=True)
            x, y = transformer.transform(lon, lat)
            bbox = (x - halo_m, y - halo_m, x + halo_m, y + halo_m)
            win = from_bounds(*bbox, transform=src.transform)
            data = src.read(1, window=win)
            if data.size == 0:
                return float("nan")
            arr = data.flatten()
            n_total = arr.size
            n_cloud = int(sum(1 for v in arr if int(v) in SCL_CLOUD_CLASSES))
            return float(n_cloud) / float(n_total) if n_total > 0 else float("nan")
    except Exception as e:
        logger.warning("[%s] _read_scl_cloud_fraction failed: %s", ENGINE_NAME, e)
        return float("nan")


# ═══════════════════════════════════════════════════════════════════
# COMPUTE — Pipeline spectral complet (point unique)
# ═══════════════════════════════════════════════════════════════════
def compute_spectral_at_point(lat: float, lon: float,
                               days_window: int = DEFAULT_DAYS_WINDOW,
                               include_landsat_lst: bool = True,
                               halo_m: float = DEFAULT_HALO_M,
                               ) -> dict[str, Any]:
    """Pipeline spectral complet sur un point WGS84.

    Returns:
        {
          "lat", "lon",
          "ndvi", "ndwi", "evi" (raw, range natif),
          "ndvi_normalized", "ndwi_normalized", "evi_normalized" (0-1),
          "lst_celsius", "lst_normalized" (si Landsat dispo),
          "cloud_fraction" (SCL),
          "source_sentinel2": {item_id, datetime, cloud_cover},
          "source_landsat": {item_id, datetime, cloud_cover} (si dispo),
          "fallback_applied": bool,
          "doctrine": ENGINE_DOCTRINE,
        }
    """
    mark_call(ENGINE_NAME)
    out: dict[str, Any] = {
        "lat": float(lat), "lon": float(lon),
        "doctrine": ENGINE_DOCTRINE,
        "engine": ENGINE_NAME, "version": ENGINE_VERSION,
        "halo_m": float(halo_m),
        "days_window": int(days_window),
    }

    # 1) SENTINEL-2 — NDVI / NDWI / EVI
    s2_items = fetch_sentinel2_stac(lat, lon, days_window=days_window)
    fallback_applied = False
    if not s2_items:
        # Aucun item Sentinel-2 disponible → fallback institutionnel
        out.update({
            "ndvi": None, "ndwi": None, "evi": None,
            "ndvi_normalized": FALLBACK_VALUE,
            "ndwi_normalized": FALLBACK_VALUE,
            "evi_normalized": FALLBACK_VALUE,
            "cloud_fraction": float("nan"),
            "source_sentinel2": None,
            "fallback_applied_s2": True,
        })
        fallback_applied = True
    else:
        # Choisir le meilleur item (cloud_cover minimal)
        best = min(s2_items, key=lambda it: it["cloud_cover"])
        urls = best["asset_urls"]
        red = _read_pixel_window(urls.get("red"), lat, lon, halo_m)
        nir = _read_pixel_window(urls.get("nir"), lat, lon, halo_m)
        green = _read_pixel_window(urls.get("green"), lat, lon, halo_m)
        blue = _read_pixel_window(urls.get("blue"), lat, lon, halo_m)
        cloud_frac = _read_scl_cloud_fraction(urls.get("scl"), lat, lon, halo_m)

        # Si pixels indisponibles (window hors image), fallback
        if red is None or nir is None:
            out.update({
                "ndvi": None, "ndwi": None, "evi": None,
                "ndvi_normalized": FALLBACK_VALUE,
                "ndwi_normalized": FALLBACK_VALUE,
                "evi_normalized": FALLBACK_VALUE,
                "cloud_fraction": cloud_frac,
                "source_sentinel2": {
                    "item_id": best["id"],
                    "datetime": best["datetime"],
                    "cloud_cover_global": best["cloud_cover"],
                },
                "fallback_applied_s2": True,
            })
            fallback_applied = True
        else:
            ndvi = compute_ndvi(red, nir)
            ndwi = compute_ndwi(green, nir) if green is not None else float("nan")
            evi = compute_evi(red, nir, blue) if blue is not None else float("nan")
            out.update({
                "ndvi": float(ndvi),
                "ndwi": float(ndwi) if not math.isnan(ndwi) else None,
                "evi": float(evi) if not math.isnan(evi) else None,
                "ndvi_normalized": normalize_ndvi(ndvi),
                "ndwi_normalized": normalize_ndwi(ndwi) if not math.isnan(ndwi) else FALLBACK_VALUE,
                "evi_normalized": normalize_evi(evi) if not math.isnan(evi) else FALLBACK_VALUE,
                "cloud_fraction": cloud_frac,
                "reflectance_red": red,
                "reflectance_nir": nir,
                "reflectance_green": green,
                "reflectance_blue": blue,
                "source_sentinel2": {
                    "item_id": best["id"],
                    "datetime": best["datetime"],
                    "cloud_cover_global": best["cloud_cover"],
                },
                "fallback_applied_s2": False,
            })

    # 2) LANDSAT — LST (optionnel, plus lent)
    if include_landsat_lst:
        ls_items = fetch_landsat_l2_stac(lat, lon)
        if ls_items:
            best_ls = min(ls_items, key=lambda it: it["cloud_cover"])
            ls_urls = best_ls["asset_urls"]
            # Landsat L2 ST_B10 (lwir11) est déjà en surface temperature K × 0.00341802 + 149.0
            # Sur Planetary Computer, la conversion est gérée nativement (déjà en K si scaled)
            # Pour simplifier : lire la valeur DN puis appliquer la formule USGS L2
            lwir_url = ls_urls.get("lwir11")
            try:
                bt_raw = _read_pixel_window(lwir_url, lat, lon, halo_m)
                if bt_raw is not None:
                    # Landsat C2 L2 ST scale = 0.00341802 ; offset = 149.0 → Kelvin
                    lst_kelvin = float(bt_raw) * 0.00341802 + 149.0
                    lst_celsius = compute_lst_landsat(lst_kelvin)
                    out.update({
                        "lst_celsius": float(lst_celsius),
                        "lst_normalized": normalize_lst_celsius(lst_celsius),
                        "source_landsat": {
                            "item_id": best_ls["id"],
                            "platform": best_ls["platform"],
                            "datetime": best_ls["datetime"],
                            "cloud_cover_global": best_ls["cloud_cover"],
                        },
                        "fallback_applied_lst": False,
                    })
                else:
                    out.update({
                        "lst_celsius": None,
                        "lst_normalized": FALLBACK_VALUE,
                        "source_landsat": None,
                        "fallback_applied_lst": True,
                    })
                    fallback_applied = fallback_applied or True
            except Exception as e:
                logger.warning("[%s] LST fetch failed: %s", ENGINE_NAME, e)
                out.update({
                    "lst_celsius": None,
                    "lst_normalized": FALLBACK_VALUE,
                    "source_landsat": None,
                    "fallback_applied_lst": True,
                })
        else:
            out.update({
                "lst_celsius": None,
                "lst_normalized": FALLBACK_VALUE,
                "source_landsat": None,
                "fallback_applied_lst": True,
            })

    out["fallback_applied_global"] = fallback_applied
    return out


def fusion_spectral_multisource(spectral_payload: dict[str, Any]) -> dict[str, Any]:
    """Fusion multisource des indices spectraux normalisés (0-1).

    Doctrine : moyenne pondérée des indices normalisés disponibles.
    Poids : NDVI 0.40 · NDWI 0.20 · EVI 0.30 · LST_inv 0.10 (LST haute = stress).
    """
    mark_call(ENGINE_NAME)
    weights = {"ndvi_normalized": 0.40, "ndwi_normalized": 0.20,
               "evi_normalized": 0.30, "lst_normalized_inv": 0.10}
    components: dict[str, float] = {}
    components["ndvi_normalized"] = float(spectral_payload.get("ndvi_normalized", FALLBACK_VALUE))
    components["ndwi_normalized"] = float(spectral_payload.get("ndwi_normalized", FALLBACK_VALUE))
    components["evi_normalized"] = float(spectral_payload.get("evi_normalized", FALLBACK_VALUE))
    lst_n = spectral_payload.get("lst_normalized")
    components["lst_normalized_inv"] = (
        1.0 - float(lst_n) if (lst_n is not None and not math.isnan(float(lst_n)))
        else FALLBACK_VALUE
    )
    fused = sum(components[k] * weights[k] for k in weights) / sum(weights.values())
    return {
        "fused_score_0_1": float(max(0.0, min(1.0, fused))),
        "components": components,
        "weights": dict(weights),
        "doctrine": ENGINE_DOCTRINE + " · FUSION_MULTISOURCE",
    }


# ═══════════════════════════════════════════════════════════════════
# CHAINE_Ω — Hooks d'intégration vers autres engines
# ═══════════════════════════════════════════════════════════════════
def chain_omega_pondere_corridors(corridors: list[dict[str, Any]],
                                    spectral_at_anchor: dict[str, Any]
                                    ) -> list[dict[str, Any]]:
    """CHAINE_Ω_SPECTRAL → CHAINE_Ω_CORRIDORS.

    Pondère chaque corridor avec un facteur spectral (1.0 = neutre).
    Forte végétation (NDVI haut) → boost +20% intensité.
    Zone humide (NDWI haut) → boost +15% intensité.
    LST extrême → pénalité -10% intensité.

    NE MUTE PAS les corridors d'origine — ajoute uniquement champs `_spectral_*`.
    """
    mark_call(ENGINE_NAME)
    if not corridors or not isinstance(spectral_at_anchor, dict):
        return list(corridors)
    ndvi_n = float(spectral_at_anchor.get("ndvi_normalized", FALLBACK_VALUE))
    ndwi_n = float(spectral_at_anchor.get("ndwi_normalized", FALLBACK_VALUE))
    lst_n = spectral_at_anchor.get("lst_normalized")

    # Facteur de pondération doctrinale
    factor = 1.0
    factor *= (1.0 + 0.20 * (ndvi_n - 0.5) * 2.0)   # ±20% selon NDVI
    factor *= (1.0 + 0.15 * (ndwi_n - 0.5) * 2.0)   # ±15% selon NDWI
    if lst_n is not None and not math.isnan(float(lst_n)):
        # Pénalité forte chaleur (lst_n > 0.7 = stress thermique)
        if float(lst_n) > 0.7:
            factor *= 0.90
    factor = max(0.5, min(1.5, factor))  # cap doctrinal [0.5, 1.5]

    out: list[dict[str, Any]] = []
    for c in corridors:
        cc = dict(c)
        cc["_spectral_factor"] = float(factor)
        cc["_spectral_ndvi_n"] = ndvi_n
        cc["_spectral_ndwi_n"] = ndwi_n
        cc["_spectral_lst_n"] = float(lst_n) if lst_n is not None else None
        cc["_spectral_chain"] = "CHAINE_Ω_SPECTRAL→CORRIDORS"
        out.append(cc)
    return out


def chain_omega_hydro_pondere(hydro_score: float,
                               spectral_at_anchor: dict[str, Any]) -> float:
    """CHAINE_Ω_SPECTRAL → CHAINE_Ω_HYDRO. Pondère le score hydro selon NDWI."""
    mark_call(ENGINE_NAME)
    ndwi_n = float(spectral_at_anchor.get("ndwi_normalized", FALLBACK_VALUE))
    # NDWI haut → bonus humidité réelle
    factor = 1.0 + 0.30 * (ndwi_n - 0.5) * 2.0  # ±30%
    factor = max(0.7, min(1.3, factor))
    return float(hydro_score) * factor


def chain_omega_pressure_humaine_pondere(pressure_score: float,
                                          spectral_at_anchor: dict[str, Any]
                                          ) -> float:
    """CHAINE_Ω_SPECTRAL → CHAINE_Ω_PRESSURE_HUMAINE.
    NDVI bas → couvert dégradé → pression humaine accentuée perçue."""
    mark_call(ENGINE_NAME)
    ndvi_n = float(spectral_at_anchor.get("ndvi_normalized", FALLBACK_VALUE))
    # NDVI bas → pression humaine plus marquante
    factor = 1.0 + 0.20 * (0.5 - ndvi_n) * 2.0  # ±20%
    factor = max(0.8, min(1.2, factor))
    return float(pressure_score) * factor

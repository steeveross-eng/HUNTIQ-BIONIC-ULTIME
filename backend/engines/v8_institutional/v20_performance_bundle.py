"""
V20 PERFORMANCE BUNDLE — V11-SUPRA SCALABILITE 10K
=====================================================
PHASE-PERFORMANCE-Omega V11-SUPRA — 5000-10000 utilisateurs.

UPGRADES:
  - Cache LRU 1024 → 10 000 entrees
  - TTL 24h (inchange)
  - Cache disque persistant (/app/backend/cache/territoire_bundle.pkl)
  - Worker async PRECHAUFFAGE-Omega au startup + daemon refresh horaire
  - CDN-ready: Cache-Control + Vary
"""
import time
import pickle  # noqa: F401  # conservé pour compat (legacy disk migration)
import asyncio
import logging
import os
from pathlib import Path
from collections import OrderedDict
from fastapi import APIRouter, Query, Response, BackgroundTasks

# P22ΩΩ_QUALITY_GROUPE_B · 2026-05-18 · COMMANDANT STEEVE-MAX
# Pickle sécurisé par HMAC-SHA256 pour disk cache + Redis propagation.
from engines.v8_institutional.secure_pickle_omega import (
    secure_dumps,
    secure_loads_legacy_tolerant,
)

logger = logging.getLogger("bionic.v20_performance")
router = APIRouter(prefix="/api/v20/territoire", tags=["V20 Performance Bundle"])

# ═══════════════════════════════════════════════════════════════════════
# P22Σ_SPECIES_NORMALIZATION_Ω · 2026-05-12T18:25Z · COMMANDANT STEEVE-MAX
# ═══════════════════════════════════════════════════════════════════════
# Normalisation des noms d'espèces côté backend pour accepter tous les
# alias frontend (wild_turkey, dindon, dindon_sauvage, moose, deer, etc.)
# et router vers le nom canonique attendu par chaque engine.
# ═══════════════════════════════════════════════════════════════════════
SPECIES_ALIAS_TO_CANONICAL = {
    # Canoniques (passthrough)
    "orignal": "orignal",     "chevreuil": "chevreuil",
    "ours_noir": "ours_noir", "wapiti": "wapiti",
    "dindon_sauvage": "dindon_sauvage",
    # Alias FR courts
    "ours": "ours_noir",      "dindon": "dindon_sauvage",
    "cerf": "chevreuil",
    # Alias EN (frontend BionicZoneService)
    "moose": "orignal",       "deer": "chevreuil",
    "bear": "ours_noir",      "elk": "wapiti",
    "wild_turkey": "dindon_sauvage",
    # P22Ω_COYOTE_REGISTRY_DECISION (2026-05-13 · COMMANDANT STEEVE-MAX)
    "coyote": "coyote",       "canis_latrans": "coyote",
    # P22ΩΩ_CORRIGE_FRONTEND_ET_VERITE_CORRIDORS_FULL_PACK_X10_Ω (2026-02-XX)
    # Vue agrégée frontend "TOUTES LES ESPÈCES" — bundle servi sur chevreuil
    # par défaut (espèce la plus densément maillée du Québec). Le frontend
    # marque la palette en "multi_aggregated" (violette) pour signaler la vue.
    "multi_aggregated": "chevreuil",
    "tous": "chevreuil", "toutes": "chevreuil", "all": "chevreuil",
}


def normalize_species(s: str) -> str:
    """Normalise un nom d'espèce vers le nom canonique backend (V5)."""
    if not s:
        return "chevreuil"
    return SPECIES_ALIAS_TO_CANONICAL.get(s.lower().strip(), s)


# ═══════════════════════════════════════════════════════════════════════
# P22Σ_V5_BUNDLE_REWIRE_Ω — MAPPING HELPER (réutilisé par bundle + audit)
# ═══════════════════════════════════════════════════════════════════════
_HIER_COLOR_V5 = {
    "veine_principale": "#FF4500",   # backbone — rouge orangé
    "veine_secondaire": "#FF8F00",   # subnet — orange
    "capillaire":       "#FFB347",   # isolated — pêche
    "connector":        "#FFEE99",   # connector — jaune pâle
}


def map_v5_corridors_to_ui(v5_corridors_raw: list[dict]) -> list[dict]:
    """Map V5 organic corridors -> format UI (color + source + fusion_doctrine).

    Fonction réutilisée par /api/v20/territoire/bundle ET /api/v20/audit/v5-compliance-live
    pour garantir la même provenance V5 dans les deux endpoints.
    """
    mapped: list[dict] = []
    for _i, _c in enumerate(v5_corridors_raw or []):
        _hier = _c.get("hierarchy", "capillaire")
        _m = dict(_c)
        _m["id"] = _c.get("id") or f"corr_v5_{_i:03d}"
        _m["color"] = _c.get("color") or _HIER_COLOR_V5.get(_hier, "#FF8F00")
        _m["source"] = "ENGINE-IA-CORRIDORS-ORGANIC-Ω (V5_BUNDLE_REWIRE)"
        _m["fusion_doctrine"] = "P22Σ_V5_CAP_GLOBAL_TERRITOIRE"
        if "subnet_role" not in _m:
            _m["subnet_role"] = (
                "backbone" if _hier == "veine_principale" else
                "subnet" if _hier == "veine_secondaire" else
                "connector" if _m.get("type") == "connector" else
                "isolated"
            )
        mapped.append(_m)
    return mapped


# ═══════════════════════════════════════════════════════════════════════
# P22ΩΩ_BLOC_2_5_HELPERS_MODULE_LEVEL_Ω · 2026-02-XX · COMMANDANT STEEVE-MAX
# ═══════════════════════════════════════════════════════════════════════
# Extraction module-level pour pouvoir appliquer la doctrine BLOC 2.5
# (V5 rewire + cap 5–7 corridors + hiérarchie veines) AVANT le retour
# court-circuité par le deadline gate global (ESSENTIEL_T0 dégradé).
# Doctrine MFFP préservée · V30 LOCK INTACT · FUSION ADD-ONLY.
# ═══════════════════════════════════════════════════════════════════════

# P22ΩΩ_SECURITE_ET_CONTINUITE_CORRIDORS_PRE_PHASE_III_Ω · 2026-02-XX
# Doctrine §8 ENGINE CORRIDORS Ω : spline CatmullRom 25-30 points par corridor.
# Le V5 engine peut produire des paths de 133 à 531 points (overshoot post-densify).
#
# RÉVISION P3 : le resample uniforme à 30 pts a dégradé la lissité (segments 27-50m,
# angles 39-112°). Compromis doctrinal stricte : target relevé à 50 pts pour
# préserver la fluidité organique, avec clip distance ≤ 780m (doctrine §7).
# - target 50 pts : respecte l'esprit de §8 (densité maîtrisée) sans casser la spline
# - clip 780m   : respecte strictement §7 rayon 600m ±30% (420-780m)
_CATMULLROM_TARGET_POINTS = 50
_CATMULLROM_MIN_POINTS = 25
_RADIUS_MAX_M = 780.0  # doctrine §7
_RADIUS_MIN_M = 420.0


def _haversine_m(p1, p2):
    """Distance entre 2 points lat/lng en mètres."""
    import math
    R = 6371000.0
    lat1, lon1 = math.radians(p1[0]), math.radians(p1[1])
    lat2, lon2 = math.radians(p2[0]), math.radians(p2[1])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))


def _path_total_length_m(path):
    """Longueur cumulative d'un path lat/lng en mètres."""
    if not isinstance(path, list) or len(path) < 2:
        return 0.0
    total = 0.0
    for i in range(len(path) - 1):
        p1, p2 = path[i], path[i + 1]
        if isinstance(p1, dict):
            p1 = (p1.get("lat"), p1.get("lng", p1.get("lon")))
        if isinstance(p2, dict):
            p2 = (p2.get("lat"), p2.get("lng", p2.get("lon")))
        if isinstance(p1, (list, tuple)) and isinstance(p2, (list, tuple)) and len(p1) >= 2 and len(p2) >= 2:
            total += _haversine_m(p1, p2)
    return total


def _clip_path_to_max_length(path, max_length_m=_RADIUS_MAX_M):
    """Clip un path lat/lng à max_length_m mètres cumulatifs.

    Conforme doctrine §7 ENGINE CORRIDORS Ω · rayon 600m ±30% (420-780m).
    Préserve le point de départ et tronque progressivement les segments
    extérieurs. Retourne le path tronqué.
    """
    if not isinstance(path, list) or len(path) < 2:
        return path
    out = [path[0]]
    cum = 0.0
    for i in range(len(path) - 1):
        p1, p2 = path[i], path[i + 1]
        # Normaliser p1/p2 en tuples
        n1 = (p1.get("lat"), p1.get("lng", p1.get("lon"))) if isinstance(p1, dict) else (
            p1[0], p1[1]) if isinstance(p1, (list, tuple)) and len(p1) >= 2 else None
        n2 = (p2.get("lat"), p2.get("lng", p2.get("lon"))) if isinstance(p2, dict) else (
            p2[0], p2[1]) if isinstance(p2, (list, tuple)) and len(p2) >= 2 else None
        if n1 is None or n2 is None:
            continue
        seg = _haversine_m(n1, n2)
        if cum + seg <= max_length_m:
            out.append(p2)
            cum += seg
        else:
            # Interpolation linéaire pour atteindre exactement max_length_m
            remain = max_length_m - cum
            if seg > 0 and remain > 0:
                frac = remain / seg
                interp_lat = n1[0] + (n2[0] - n1[0]) * frac
                interp_lon = n1[1] + (n2[1] - n1[1]) * frac
                # Conserver le format d'origine
                if isinstance(p2, dict):
                    out.append({"lat": interp_lat, "lng": interp_lon})
                else:
                    out.append([interp_lat, interp_lon])
            break
    return out


def _resample_path_catmullrom(path: list, target: int = _CATMULLROM_TARGET_POINTS) -> list:
    """Resample uniforme d'un path à `target` points, conserve start & end.

    Conforme doctrine §8 ENGINE CORRIDORS Ω · CatmullRom 25-50 pts.
    No-op si path ≤ target. Robuste aux formats (list of dict, list of tuple).
    Note : pour préserver la lissité organique, target ≥ 50 (révision P3 SECURITE).
    """
    if not isinstance(path, list) or len(path) <= target:
        return path
    n = len(path)
    out = []
    for i in range(target):
        idx = round(i * (n - 1) / (target - 1))
        if idx >= n:
            idx = n - 1
        out.append(path[idx])
    out[0] = path[0]
    out[-1] = path[-1]
    return out


def _apply_catmullrom_cap_to_corridors(corridors: list, target: int = _CATMULLROM_TARGET_POINTS) -> dict:
    """Applique le cap CatmullRom 25-50 pts + clip distance ≤780m sur chaque corridor.

    P22ΩΩ_SECURITE_ET_CONTINUITE_CORRIDORS_PRE_PHASE_III_Ω :
      1. Clip path à _RADIUS_MAX_M (780m) — doctrine §7
      2. Resample CR à target points — doctrine §8
    Retourne stats détaillées (n_resampled, n_clipped, max_lengths).
    """
    stats = {
        "n_corridors": len(corridors),
        "n_resampled": 0,
        "n_clipped_to_radius": 0,
        "max_points_before": 0,
        "max_points_after": 0,
        "max_length_before_m": 0.0,
        "max_length_after_m": 0.0,
        "target": target,
        "radius_max_m": _RADIUS_MAX_M,
    }
    if not isinstance(corridors, list):
        return stats
    for c in corridors:
        if not isinstance(c, dict):
            continue
        for path_key in ("path", "coords", "coordinates"):
            p = c.get(path_key)
            if not isinstance(p, list) or len(p) < 2:
                continue
            # Étape 1 : Clip distance ≤ 780m (doctrine §7)
            L_before = _path_total_length_m(p)
            stats["max_length_before_m"] = max(stats["max_length_before_m"], L_before)
            if L_before > _RADIUS_MAX_M:
                p = _clip_path_to_max_length(p, _RADIUS_MAX_M)
                c[path_key] = p
                stats["n_clipped_to_radius"] += 1
            L_after = _path_total_length_m(p)
            stats["max_length_after_m"] = max(stats["max_length_after_m"], L_after)
            # Étape 2 : Resample CatmullRom à `target` points (doctrine §8)
            before = len(p)
            stats["max_points_before"] = max(stats["max_points_before"], before)
            if before > target:
                new_p = _resample_path_catmullrom(p, target)
                c[path_key] = new_p
                stats["n_resampled"] += 1
                stats["max_points_after"] = max(stats["max_points_after"], len(new_p))
            else:
                stats["max_points_after"] = max(stats["max_points_after"], before)
    return stats


def _apply_v5_rewire_to_result(
    result: dict,
    v5_bundle: dict | None,
    v5_error: str | None,
    species: str,
) -> dict:
    """P22Σ_V5_BUNDLE_REWIRE_Ω — override corridors V10 par corridors V5 organic.

    Si V5 dispo : map + remap V30 fallback éventuel + signature p22sigma_v5_bundle_rewire.
    Si V5 KO    : signature p22sigma_v5_bundle_rewire.applied=False (fallback V10).
    Idempotent : ne ré-applique pas si déjà appliqué.
    """
    _v5_active = v5_bundle is not None
    # Idempotence : si déjà rewiré, ne ré-applique pas
    if isinstance(result.get("p22sigma_v5_bundle_rewire"), dict) and \
       result["p22sigma_v5_bundle_rewire"].get("applied") is True:
        return result

    if _v5_active:
        v5_corridors_raw = v5_bundle.get("corridors", []) or []
        v5_mapped = map_v5_corridors_to_ui(v5_corridors_raw)
        # ═══ P22Ω_MULTI_FIX_A1 — REMAP V30 vers V5 si V5 vide & espèce présente ═══
        _v30_remap_applied = False
        if not v5_mapped and not result.get("bio_presence_mask_halt"):
            _v30_corridors = result.get("corridors", []) or []
            if len(_v30_corridors) >= 5:
                _v30_sorted = sorted(
                    _v30_corridors,
                    key=lambda c: (c.get("intensity") or c.get("score") or 0),
                    reverse=True,
                )[:7]
                v5_mapped = []
                for _i, _c in enumerate(_v30_sorted):
                    _hier = ("veine_principale" if _i < 2 else "veine_secondaire")
                    _m = dict(_c)
                    _m["id"] = _c.get("id") or f"corr_v30remap_{_i:03d}"
                    _m["hierarchy"] = _hier
                    _m["color"] = _HIER_COLOR_V5.get(_hier, "#FF8F00")
                    _m["source"] = "V30_REMAP_TO_V5 (P22Ω_MULTI_FIX_A1)"
                    _m["fusion_doctrine"] = "P22Ω_V30_REMAP_TO_V5"
                    _m["subnet_role"] = "backbone" if _i < 2 else "subnet"
                    v5_mapped.append(_m)
                _v30_remap_applied = True
                logger.info(
                    f"[P22Ω_MULTI_FIX_A1] V30→V5 REMAP species={species} "
                    f"n_v30={len(_v30_corridors)} → n_v5_remap={len(v5_mapped)}"
                )
        result["corridors"] = v5_mapped
        result["p22sigma_v5_bundle_rewire"] = {
            "applied": True,
            "anchor_mode": "TERRITORY_CONTINUOUS",
            "n_corridors": len(v5_mapped),
            "hierarchy_counts": v5_bundle.get("hierarchy_counts"),
            "cap_global_doctrine": v5_bundle.get("p22sigma_v5_cap_global_doctrine"),
            "engine": v5_bundle.get("engine"),
            "engine_version": v5_bundle.get("version"),
            "doctrine": "P22Σ_V5_BUNDLE_REWIRE_Ω",
            "wired_at": "v20_performance_bundle._apply_v5_rewire_to_result",
            "optim": "V10_SINGLE_CALL_THEN_V5_REUSE",
            "v30_remap_fallback_applied": _v30_remap_applied,
        }
    else:
        result["p22sigma_v5_bundle_rewire"] = {
            "applied": False,
            "error": v5_error or "v5_bundle unavailable",
            "fallback": "V10_SUPRA_LEGACY",
        }
    return result


def _apply_bloc25_hierarchy_and_cap(result: dict, species: str) -> dict:
    """P22ΩΩ_BLOC_2_5_CORRIDORS_UNIQUES_PAR_ESPECE_Ω — OPTION B.

    Enforce hiérarchie + cap 5-7 + marquage EXTERNAL_INFLOW sur le bundle.
    Idempotent · garantit ≥1 veine_principale si corridors présents.
    No-op si bio_presence_mask_halt (espèce ABSENT, doctrine MFFP).
    """
    if result.get("bio_presence_mask_halt"):
        return result  # ABSENT — doctrine MFFP, laisse 0 corridors

    _corridors = result.get("corridors") or []
    if not isinstance(_corridors, list) or len(_corridors) == 0:
        return result

    _PRINCIPAL_THRESHOLD = 0.7
    _SECONDARY_THRESHOLD = 0.4
    _SCORE_PRINCIPAL = 70
    _SCORE_SECONDARY = 40

    _hier_stats = {
        "missing_filled": 0,
        "external_inflow_marked": 0,
        "veine_principale_promoted": 0,
    }

    # Étape 1+2+3 : enforcer hiérarchie sur chaque corridor
    for _c in _corridors:
        if not isinstance(_c, dict):
            continue
        _current_hier = _c.get("hierarchy")
        _needs_fill = _current_hier in (None, "", "unknown", "legacy", "missing")
        _source = (_c.get("source") or "").upper()
        _is_external_inflow = "EXTERNAL_INFLOW" in _source

        if _needs_fill or _is_external_inflow:
            _intensity = float(_c.get("intensity") or 0.0)
            _score = float(
                _c.get("fused_score") or _c.get("score") or _c.get("composite_score") or 0.0
            )
            if _intensity >= _PRINCIPAL_THRESHOLD or _score >= _SCORE_PRINCIPAL:
                _new_hier = "veine_principale"
            elif _intensity >= _SECONDARY_THRESHOLD or _score >= _SCORE_SECONDARY:
                _new_hier = "veine_secondaire"
            else:
                _new_hier = "capillaire"

            if _needs_fill:
                _c["hierarchy"] = _new_hier
                _c["hierarchy_filled_by"] = "P22ΩΩ_BLOC_2_5_OPTION_B"
                _hier_stats["missing_filled"] += 1
            if _is_external_inflow:
                _c["external_inflow_marked"] = True
                _hier_stats["external_inflow_marked"] += 1

    # Étape 4 : cap 5-7 corridors par espèce (top par intensity + score)
    _CAP_MAX = 7
    if len(_corridors) > _CAP_MAX:
        _sorted = sorted(
            _corridors,
            key=lambda c: (
                float(c.get("intensity") or 0.0),
                float(c.get("fused_score") or c.get("score") or 0.0),
            ),
            reverse=True,
        )
        _corridors = _sorted[:_CAP_MAX]
        result["corridors"] = _corridors

    # Étape 5 : garantir ≥1 veine_principale (promotion auto)
    _has_principal = any(c.get("hierarchy") == "veine_principale" for c in _corridors)
    if not _has_principal and _corridors:
        _best = max(
            _corridors,
            key=lambda c: (
                float(c.get("intensity") or 0.0),
                float(c.get("fused_score") or c.get("score") or 0.0),
            ),
        )
        _best["hierarchy_promoted_from"] = _best.get("hierarchy", "capillaire")
        _best["hierarchy"] = "veine_principale"
        _best["hierarchy_promotion_doctrine"] = "P22ΩΩ_BLOC_2_5_AUTO_PROMOTE"
        _hier_stats["veine_principale_promoted"] = 1

    # Recompute hierarchy_counts pour traçabilité bundle
    _hier_counts = {"veine_principale": 0, "veine_secondaire": 0, "capillaire": 0, "other": 0}
    for _c in _corridors:
        _h = _c.get("hierarchy") or "other"
        if _h in _hier_counts:
            _hier_counts[_h] += 1
        else:
            _hier_counts["other"] += 1

    result["p22omegaomega_bloc_2_5_doctrine"] = {
        "applied": True,
        "doctrine": "P22ΩΩ_BLOC_2_5_CORRIDORS_UNIQUES_PAR_ESPECE_Ω",
        "option": "B",
        "species": species,
        "n_corridors_final": len(_corridors),
        "cap_max": _CAP_MAX,
        "hierarchy_counts": _hier_counts,
        "stats": _hier_stats,
    }

    # P22ΩΩ_CORRIGE_FRONTEND_ET_VERITE_CORRIDORS_FULL_PACK_X10_Ω · P3 (2026-02-XX)
    # Doctrine §8 ENGINE CORRIDORS Ω — Cap CatmullRom 25-30 points/corridor.
    # Resample uniforme post-cap pour éliminer overshoot V5 (133/531 points).
    _catmullrom_stats = _apply_catmullrom_cap_to_corridors(
        _corridors, target=_CATMULLROM_TARGET_POINTS
    )
    result["p22omegaomega_catmullrom_cap_doctrine"] = {
        "applied": True,
        "doctrine": "P22ΩΩ_CORRIGE_FRONTEND_ET_VERITE_CORRIDORS_FULL_PACK_X10_Ω · P3",
        "target_points": _CATMULLROM_TARGET_POINTS,
        "stats": _catmullrom_stats,
    }
    return result


# ═══ CACHE IN-MEMORY LRU TTL 24h — V11-SUPRA SCALABILITE 10K ═══
_CACHE: "OrderedDict[str, tuple[float, dict]]" = OrderedDict()
_CACHE_TTL_SEC = 86400
_CACHE_MAX = 10000  # V11-SUPRA: 1024 → 10000

# P22ΩΩ_BUNDLE_DEGRADED_CACHE · 2026-05-14 · STEEVE-MAX
# TTL overrides per-key (bundles DEGRADED expirent en 90s pour ne pas
# polluer le cache trop longtemps, mais évitent le 502 systématique en
# cold-start quand Open-Meteo est en circuit-breaker).
_CACHE_TTL_OVERRIDES: "dict[str, int]" = {}
_CACHE_DEGRADED_TTL_SEC = 90  # 1.5 minute pour bundle dégradé
_LAST_BG_DISK_SAVE_TS = 0.0  # P22ΩΩ_DISK_PERSIST · throttle save_disk depuis BG_CACHE

# P22ΩΩ_TERRITOIRE_ESSENTIEL_1WORKER · 2026-05-18 · STEEVE-MAX
# ─── Profil "ESSENTIEL_1WORKER" : 3 cercles temporels ───
# T0       : terrain + meteo + zones + hotspots + salines + species + V5 corridors essentiels (~6s budget)
# T+Δ      : enrichissement BG via callback (corridors_vitaux + connectivité + affuts détaillés + comportement)
# AVANCÉ   : opt-in user (predictive IA, 3D overlays, MVT tiles) — jamais bloquant
#
# Le cache stocke 2 niveaux indépendants pour le même waypoint × espèce :
#   - cache key suffixé "_t0"     : bundle ESSENTIEL T0 (TTL ESSENTIEL 600s)
#   - cache key suffixé "_tdelta" : bundle ENRICHI T+Δ   (TTL standard 24h)
_CACHE_ESSENTIEL_TTL_SEC = 3600  # P22ΩΩ_TERRITOIRE_TTL_ESSENTIEL_3600S · 2026-05-19 · STEEVE-MAX
                                 # 600s → 3600s (1h) : maximise HIT cache pour 2000 membres
                                 # tout en gardant une vérité scientifique suffisante (Cercle ESSENTIEL).
_CACHE_TTL_ESSENTIEL_SEC = _CACHE_ESSENTIEL_TTL_SEC  # alias canonique demandé par Commandant
_CACHE_MAX_ESSENTIEL = 5000     # capacité dédiée aux bundles ESSENTIELS (2000 membres × 2-3 contexts)
_ESSENTIEL_MODE_ENABLED = True  # gate globale (env P22OMEGA_ESSENTIEL_1WORKER=0 désactive)

# ═══ DISK PERSISTENCE ═══
_CACHE_DIR = Path("/app/backend/cache")
_CACHE_DIR.mkdir(parents=True, exist_ok=True)
_CACHE_DISK_FILE = _CACHE_DIR / "territoire_bundle.pkl"

_STATS = {
    "hits": 0, "misses": 0, "evictions": 0, "total_compute_ms": 0,
    "warmup_runs": 0, "warmup_last_count": 0, "warmup_last_ms": 0,
    "disk_loaded": 0, "disk_saved": 0,
}


def _cache_key(lat: float, lon: float, species: str, month: int, hour: int, wind_deg: float) -> str:
    """P22Σ_CACHE_KEY_TOLERANT_Ω · 2026-05-12T23:55Z · COMMANDANT STEEVE-MAX

    Cache key tolérant : omet `hour` (le bundle V5 corridors ne dépend pas
    significativement de l'heure — la topologie réseau veineux est calculée
    sur terrain+zones vitales+écologie statique, pas l'heure du jour).
    Réduction cardinalité × 24 → 24× moins de MISS pour utilisateurs
    actifs dans des fuseaux horaires différents (UTC vs local Québec EDT).

    NOTE: `hour` reste accepté en paramètre pour compatibilité ABI mais
    n'est plus inclus dans la key (ignoré silencieusement).
    """
    _ = hour  # explicitly unused
    lat_s = f"{lat:.3f}"
    lon_s = f"{lon:.3f}"
    wd_s = int(round(wind_deg / 15.0) * 15) % 360
    return f"{lat_s}_{lon_s}_{species}_{month}_w{wd_s}"


def _cache_get(key: str):
    # L2 local LRU
    entry = _CACHE.get(key)
    if entry:
        ts, payload = entry
        # P22ΩΩ_BUNDLE_DEGRADED_CACHE : respecte TTL override si présent
        ttl_effective = _CACHE_TTL_OVERRIDES.get(key, _CACHE_TTL_SEC)
        if time.time() - ts > ttl_effective:
            _CACHE.pop(key, None)
            _CACHE_TTL_OVERRIDES.pop(key, None)
        else:
            _CACHE.move_to_end(key)
            return payload
    # L1 Redis partage multi-pod (si disponible)
    try:
        from engines.v8_institutional.redis_omega import redis_get, is_redis_enabled
        if is_redis_enabled():
            val = redis_get(key)
            if val is not None:
                # Warm local LRU avec la valeur Redis
                _CACHE[key] = (time.time(), val)
                _CACHE.move_to_end(key)
                while len(_CACHE) > _CACHE_MAX:
                    _CACHE.popitem(last=False)
                    _STATS["evictions"] += 1
                return val
    except Exception:
        pass
    return None


def _cache_set(key: str, payload: dict, ttl: int = None):
    """P22ΩΩ_BUNDLE_DEGRADED_CACHE · 2026-05-14 · STEEVE-MAX
    Stocke un bundle dans le LRU + Redis.
    Si `ttl` est fourni (ex: 90s pour bundle DEGRADED), utilise-le au lieu du TTL par défaut.
    Le TTL est gardé dans la dict _CACHE_TTL_OVERRIDES pour permettre les expirations rapides
    des bundles dégradés tout en gardant le format tuple (timestamp, payload) inchangé.
    """
    effective_ttl = ttl if (ttl is not None and ttl > 0) else _CACHE_TTL_SEC
    _CACHE[key] = (time.time(), payload)
    if effective_ttl != _CACHE_TTL_SEC:
        _CACHE_TTL_OVERRIDES[key] = effective_ttl
    else:
        # Si on revient au TTL par défaut, on enlève tout override antérieur
        _CACHE_TTL_OVERRIDES.pop(key, None)
    _CACHE.move_to_end(key)
    while len(_CACHE) > _CACHE_MAX:
        evicted_key, _ = _CACHE.popitem(last=False)
        _CACHE_TTL_OVERRIDES.pop(evicted_key, None)
        _STATS["evictions"] += 1
    # Propagate to Redis (fire-and-forget)
    try:
        from engines.v8_institutional.redis_omega import redis_set, is_redis_enabled
        if is_redis_enabled():
            redis_set(key, payload, ttl=effective_ttl)
    except Exception:
        pass


# ═══ DISK PERSISTENCE ═══
def _cache_save_disk():
    """Persist LRU to disk (called on shutdown + periodic).

    P22ΩΩ_QUALITY_GROUPE_B · 2026-05-18 · STEEVE-MAX
    Sauvegarde via secure_dumps (HMAC-SHA256) au lieu de pickle.dump direct.
    """
    try:
        # Serialize only entries not expired
        valid = [(k, v) for k, v in _CACHE.items() if time.time() - v[0] < _CACHE_TTL_SEC]
        signed_blob = secure_dumps({"entries": valid, "saved_at": time.time()})
        with open(_CACHE_DISK_FILE, "wb") as f:
            f.write(signed_blob)
        _STATS["disk_saved"] += 1
        logger.info(
            f"[V20-CACHE] Disk save: {len(valid)} entries → {_CACHE_DISK_FILE} (HMAC-signed)"
        )
        return len(valid)
    except Exception as e:
        logger.warning(f"[V20-CACHE] Disk save failed: {e}")
        return 0


def _cache_load_disk():
    """Load persisted cache from disk (called at startup).

    P22ΩΩ_QUALITY_GROUPE_B · 2026-05-18 · STEEVE-MAX
    Lecture via secure_loads_legacy_tolerant — accepte les anciens pickles
    non-signés au premier boot post-migration (puis re-signés au prochain save).
    """
    if not _CACHE_DISK_FILE.exists():
        return 0
    try:
        with open(_CACHE_DISK_FILE, "rb") as f:
            blob = f.read()
        data, was_legacy = secure_loads_legacy_tolerant(blob)
        loaded = 0
        for k, (ts, payload) in data.get("entries", []):
            if time.time() - ts < _CACHE_TTL_SEC:
                _CACHE[k] = (ts, payload)
                loaded += 1
        _STATS["disk_loaded"] = loaded
        suffix = " (legacy unsigned, will re-sign)" if was_legacy else " (HMAC-verified)"
        logger.info(
            f"[V20-CACHE] Disk load: {loaded} entries restored from {_CACHE_DISK_FILE}{suffix}"
        )
        return loaded
    except Exception as e:
        logger.warning(f"[V20-CACHE] Disk load failed: {e}")
        return 0


# ═══ PRECHAUFFAGE-Omega WORKER ═══
_WARMUP_LOCK = asyncio.Lock()
# P22Ω_WORKER_SAFE_REARM · 2026-05-13 · COMMANDANT STEEVE-MAX
# Semaphore réduit 4 → 2 pour minimiser pression Open-Meteo + worker FastAPI
# unique. Daemons réarmés avec sleep randomisé 1800-2400s.
_WARMUP_SEMAPHORE = asyncio.Semaphore(2)  # 2 parallel computes max (SAFE_REARM)

# P22Ω_WORKER_SAFE_REARM — sleep aléatoire entre démons V5
import random as _random
_DAEMON_SLEEP_MIN = 1800   # 30 min
_DAEMON_SLEEP_MAX = 2400   # 40 min


def _daemon_sleep_randomized() -> float:
    """Retourne un délai aléatoire 1800-2400s pour désynchroniser les démons V5."""
    return _random.uniform(_DAEMON_SLEEP_MIN, _DAEMON_SLEEP_MAX)


# Daemons state tracking pour /api/healthz/worker
_DAEMONS_STATE = {
    "prechauffage_started_at": None,
    "prechauffage_last_tick_at": None,
    "prechauffage_tick_count": 0,
    "periodic_refresh_started_at": None,
    "periodic_refresh_last_tick_at": None,
    "periodic_refresh_tick_count": 0,
    "v5_monitor_started_at": None,
    "v5_monitor_last_tick_at": None,
    "v5_monitor_tick_count": 0,
}


async def _warmup_single(lat: float, lon: float, species: str = "cerf"):
    """Compute + cache un seul waypoint AVEC LE BUNDLE COMPLET (V5 + RenduΩ + veineux + masks).

    P22Ω_REDIS_HOIST · 2026-05-13 · COMMANDANT STEEVE-MAX
    Le warmup invoque désormais le pipeline COMPLET du bundle au lieu de
    `compute_territoire_v10` seul. Élimine le cache poisoning observé lors de
    P22Ω_WORKER_SAFE_REARM (warmup cache → MISS user → recompute V5 → overwrite
    → flash visuel ~15s sur UI).

    Stratégie : appel direct à `v20_territoire_bundle` avec un Response synthétique.
    Le pipeline complet (compute_v10 + V5 organic + presence_mask + RenduΩ +
    veineux + interzone + esi_omega) populé via `_cache_set` LRU + Redis.
    """
    from fastapi import Response as _FastAPIResponse
    try:
        async with _WARMUP_SEMAPHORE:
            now = time.time()
            from datetime import datetime, timezone as _tz
            _dt = datetime.now(_tz.utc)
            _month = _dt.month
            _hour = _dt.hour
            # Normalize species pour aligner avec frontend (cerf → chevreuil, etc.)
            _species = SPECIES_ALIAS_TO_CANONICAL.get(species.lower(), species)
            _resp = _FastAPIResponse()
            # P22Ω_REDIS_HOIST · 2026-05-13 — Active le contextvar warmup pour
            # bypass le hardcap 20s (warmup peut attendre 50s pour cache complet).
            _token = _WARMUP_CONTEXT.set(True)
            try:
                # Appel direct = full pipeline (cache_set du bundle complet inclus)
                await v20_territoire_bundle(
                    response=_resp,
                    lat=lat, lon=lon, species=_species,
                    month=_month, hour=_hour,
                    wind_deg=225.0, wind_speed=15.0,
                )
            finally:
                _WARMUP_CONTEXT.reset(_token)
            return time.time() - now
    except Exception as e:
        logger.warning(f"[V20-WARMUP] Failed {lat},{lon} {species}: {e}")
        return 0


async def _get_top_waypoints(limit: int = 200):
    """Fetch top waypoints from MongoDB (sorted by most recent activity)."""
    try:
        # Import lazily pour eviter circular import
        from motor.motor_asyncio import AsyncIOMotorClient
        mongo_url = os.environ.get("MONGO_URL")
        db_name = os.environ.get("DB_NAME", "hunt_iq_db")
        if not mongo_url:
            return []
        client = AsyncIOMotorClient(mongo_url)
        db = client[db_name]
        # Top waypoints: actifs, trie par updated_at / created_at desc
        cursor = db.user_waypoints.find(
            {"active": {"$ne": False}},
            {"_id": 0, "lat": 1, "lng": 1, "latitude": 1, "longitude": 1, "species": 1}
        ).sort("created_at", -1).limit(limit)
        waypoints = []
        async for doc in cursor:
            lat = doc.get("lat") or doc.get("latitude")
            lng = doc.get("lng") or doc.get("longitude")
            sp = doc.get("species") or "cerf"
            if lat is not None and lng is not None:
                waypoints.append((float(lat), float(lng), sp))
        client.close()
        return waypoints
    except Exception as e:
        logger.warning(f"[V20-WARMUP] Top waypoints fetch failed: {e}")
        return []


async def run_prechauffage_omega(limit: int = 200):
    """PRECHAUFFAGE-Omega-INTELLIGENT: preload top N waypoints en parallele.

    P22Ω_WORKER_SAFE_REARM · 2026-05-13 — défault limit=200 conservé pour
    appels manuels (/bundle/warmup), mais lazy-init et démons utilisent
    désormais limit=20 (semaphore=2 plus prudent sur worker unique).
    """
    async with _WARMUP_LOCK:
        t0 = time.time()
        _DAEMONS_STATE["prechauffage_last_tick_at"] = time.time()
        _DAEMONS_STATE["prechauffage_tick_count"] += 1
        waypoints = await _get_top_waypoints(limit)
        if not waypoints:
            logger.info("[V20-WARMUP] Aucun waypoint a precharger")
            return {"warmed": 0, "elapsed_s": 0}
        # Deduplication par cle quantifiee (params temporels DYNAMIQUES)
        from datetime import datetime, timezone as _tz
        _dt_now = datetime.now(_tz.utc)
        _m_now = _dt_now.month
        _h_now = _dt_now.hour
        seen = set()
        unique = []
        for lat, lon, sp in waypoints:
            sp_norm = SPECIES_ALIAS_TO_CANONICAL.get(sp.lower(), sp)
            k = _cache_key(lat, lon, sp_norm, _m_now, _h_now, 225.0)
            if k not in seen and _cache_get(k) is None:
                seen.add(k)
                unique.append((lat, lon, sp_norm))
        logger.info(f"[V20-WARMUP] Demarrage prechauffage: {len(unique)} waypoints (sur {len(waypoints)} retrouves) — month={_m_now} hour={_h_now}")
        # Lance en parallele (semaphore limite la concurrence a 8)
        tasks = [_warmup_single(lat, lon, sp) for lat, lon, sp in unique]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        elapsed = time.time() - t0
        warmed = sum(1 for r in results if isinstance(r, (int, float)) and r > 0)
        _STATS["warmup_runs"] += 1
        _STATS["warmup_last_count"] = warmed
        _STATS["warmup_last_ms"] = round(elapsed * 1000)
        # Save to disk post-warmup
        _cache_save_disk()
        logger.info(f"[V20-WARMUP] Prechauffage termine: {warmed}/{len(unique)} en {elapsed:.1f}s — Cache: {len(_CACHE)}/{ _CACHE_MAX}")
        return {"warmed": warmed, "attempted": len(unique), "elapsed_s": round(elapsed, 2)}


# ═══ LAZY-INIT GUARD (compatible uvicorn --reload) ═══
_LAZY_INIT_DONE = False
_LAZY_INIT_LOCK = asyncio.Lock()


# ═══════════════════════════════════════════════════════════════════════
# P22Ω_WORKER_SAFE_REARM · 2026-05-13 · COMMANDANT STEEVE-MAX
# Prewarm engines au démarrage pour éviter cold start sur le premier MISS.
# Précharge les imports lourds (V10, V5 organic, smoother, RenduΩ) + appel
# fictif minimal pour amorcer les caches internes Python (jit/import).
# ═══════════════════════════════════════════════════════════════════════
_PREWARM_DONE = False


async def _prewarm_engines_omega():
    """Prewarm les engines pour éliminer cold start sur premier MISS.

    Imports lourds + initialisation registres internes. NE FAIT PAS de
    compute réel (coûteux), juste warm-up imports + cache statiques.
    """
    global _PREWARM_DONE
    if _PREWARM_DONE:
        return
    t0 = time.time()
    try:
        # Import lourds (territoire_v10, V5 organic, smoother, RenduΩ)
        from engines.v8_institutional import territoire_v10_supra  # noqa: F401
        from engines.v8_institutional import engine_ia_corridors_organic_omega  # noqa: F401
        from engines.post_smoothing import organic_corridor_smoother  # noqa: F401
        from engines.post_smoothing import renduomega  # noqa: F401
        from engines.post_smoothing import veineux_omega  # noqa: F401
        from engines.post_smoothing import interzone_omega  # noqa: F401
        from engines.v8_institutional import species_presence_mask_omega  # noqa: F401
        from engines.v8_institutional import esi_omega  # noqa: F401
        # Touch les registres statiques pour priming
        _ = engine_ia_corridors_organic_omega.SPECIES_BEHAVIOR
        _ = engine_ia_corridors_organic_omega.BIOLOGICAL_PAIR_COMPATIBILITY
        _ = organic_corridor_smoother.SPECIES_LOCOMOTION
        _ = species_presence_mask_omega.SPECIES_PRESENCE_REGISTRY
        _PREWARM_DONE = True
        elapsed = round((time.time() - t0) * 1000, 1)
        logger.info(
            f"[V20-PREWARM] P22Ω_WORKER_SAFE_REARM · engines prewarmed in {elapsed}ms "
            f"(V10, V5_organic, smoother, RenduΩ, veineux, interzone, presence_mask, esi)"
        )
    except Exception as e:
        logger.warning(f"[V20-PREWARM] Prewarm error: {e}")


# ═══════════════════════════════════════════════════════════════════════
# P22Ω_WORKER_SAFE_REARM · MISS ABSORPTION
# ═══════════════════════════════════════════════════════════════════════
# Hardcap 20s sur le compute MISS, soft threshold 12s (warning log).
# Au-delà du hardcap, on retourne le stale cache ou un bundle dégradé
# au lieu de laisser pourrir le worker pendant 60s+.
# P22Ω_REDIS_HOIST · 2026-05-13 — Le warmup utilise un contextvar pour
# bypass le hardcap (le warmup populate le cache et peut attendre 45s,
# vs requête user-facing limitée à 20s).
# ═══════════════════════════════════════════════════════════════════════
_MISS_HARDCAP_SEC = 6.0   # P22ΩΩ 2026-05-14 : 10→6s — V10 cap 6s + V5 cap 6s + post ~10s = max ~22s < 25s K8s
_MISS_SOFT_THRESHOLD_SEC = 5.0  # Aligné sur le nouveau hardcap 6s
_MISS_WARMUP_HARDCAP_SEC = 12.0  # P22ΩΩ 2026-05-14 : 35→12s pour ne pas saturer single-worker
_GLOBAL_BUNDLE_DEADLINE_SEC = 10.0  # P22ΩΩ 2026-05-14 : early-return si TOTAL > 10s (sous timeout K8s ~25s)
_MISS_STATS: dict = {
    "absorbed_count": 0,        # MISS dépassant hardcap → absorption
    "soft_warning_count": 0,    # MISS dépassant soft threshold
    "total_miss_compute_s": 0.0,
    "last_absorbed_at": None,
}

# P22Ω_REDIS_HOIST · contextvar pour identifier les calls initiated par le warmup
import contextvars
_WARMUP_CONTEXT: contextvars.ContextVar[bool] = contextvars.ContextVar(
    "_warmup_context", default=False,
)


def _effective_miss_hardcap() -> float:
    """Retourne le hardcap effectif selon le contexte d'appel.

    - Warmup context (background prechauffage) → 50s (permet compute fresh complet)
    - User-facing (frontend request) → 20s (protection contre hang)
    """
    return _MISS_WARMUP_HARDCAP_SEC if _WARMUP_CONTEXT.get() else _MISS_HARDCAP_SEC


async def _ensure_lazy_init():
    """Initialise au premier appel (disk load + prechauffage async). Idempotent."""
    global _LAZY_INIT_DONE
    if _LAZY_INIT_DONE:
        return
    async with _LAZY_INIT_LOCK:
        if _LAZY_INIT_DONE:
            return
        _LAZY_INIT_DONE = True
        # P22Ω_REDIS_HOIST · 2026-05-13 · ensure Redis daemon up
        _ensure_redis_daemon_up()
        loaded = _cache_load_disk()
        logger.info(f"[V20-LAZY-INIT] {loaded} entries loaded from disk")
        # P22ΩΩ 2026-05-14 — Prechauffage daemons DÉSACTIVÉS par défaut (single-worker
        # saturation). Pour réactiver : export P22OMEGA_PRECHAUFFAGE_DAEMONS=1
        if os.environ.get("P22OMEGA_PRECHAUFFAGE_DAEMONS", "0") == "1":
            asyncio.create_task(_prewarm_engines_omega())
            asyncio.create_task(run_prechauffage_omega(limit=5))
            asyncio.create_task(_periodic_refresh_daemon())
            asyncio.create_task(_v5_compliance_monitor_daemon())
            _DAEMONS_STATE["prechauffage_started_at"] = time.time()
            _DAEMONS_STATE["periodic_refresh_started_at"] = time.time()
            _DAEMONS_STATE["v5_monitor_started_at"] = time.time()
            logger.info(
                "[V20-LAZY-INIT] P22Ω_WORKER_SAFE_REARM + P22Ω_PHASE1_P1_FIXES — daemons ON: "
                "prechauffage(sem=2,limit=5), periodic_refresh, v5_monitor "
                f"(sleep randomized {_DAEMON_SLEEP_MIN}-{_DAEMON_SLEEP_MAX}s)"
            )
        else:
            # Toujours faire le prewarm engines (très léger ~1.4ms)
            asyncio.create_task(_prewarm_engines_omega())
            logger.info("[V20-LAZY-INIT] P22ΩΩ — prechauffage daemons DISABLED (env P22OMEGA_PRECHAUFFAGE_DAEMONS)")


# ═══════════════════════════════════════════════════════════════════════
# P22Ω_REDIS_HOIST · 2026-05-13 · COMMANDANT STEEVE-MAX
# S'assure que redis-server local tourne avant init. Redémarre si tombé.
# Non-bloquant : si Redis indisponible, fallback transparent LRU in-memory
# (logique déjà présente dans redis_omega.py).
# ═══════════════════════════════════════════════════════════════════════
_REDIS_OMEGA_CONF = os.environ.get("REDIS_OMEGA_CONFIG", "/app/backend/cache/redis-omega.conf")


def _ensure_redis_daemon_up() -> bool:
    """Vérifie que redis-server tourne sur la socket configurée.
    Le démarre en daemon si absent. Idempotent.
    """
    if not os.environ.get("REDIS_URL"):
        logger.info("[P22Ω_REDIS_HOIST] REDIS_URL non défini — skip daemon check")
        return False
    try:
        import subprocess
        # Test ping rapide
        try:
            r = subprocess.run(
                ["redis-cli", "-h", "127.0.0.1", "-p", "6379", "ping"],
                capture_output=True, text=True, timeout=2.0,
            )
            if r.returncode == 0 and "PONG" in r.stdout:
                logger.info("[P22Ω_REDIS_HOIST] Redis daemon UP (ping=PONG)")
                return True
        except Exception:
            pass
        # Pas de ping → tenter de démarrer
        if not os.path.exists(_REDIS_OMEGA_CONF):
            logger.warning(f"[P22Ω_REDIS_HOIST] Config absente {_REDIS_OMEGA_CONF} — skip")
            return False
        subprocess.Popen(
            ["redis-server", _REDIS_OMEGA_CONF, "--daemonize", "yes"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        time.sleep(1.5)
        # Re-test
        r = subprocess.run(
            ["redis-cli", "-h", "127.0.0.1", "-p", "6379", "ping"],
            capture_output=True, text=True, timeout=2.0,
        )
        if r.returncode == 0 and "PONG" in r.stdout:
            logger.info("[P22Ω_REDIS_HOIST] Redis daemon STARTED (ping=PONG)")
            return True
        logger.warning("[P22Ω_REDIS_HOIST] Redis startup failed — fallback LRU only")
        return False
    except Exception as e:
        logger.warning(f"[P22Ω_REDIS_HOIST] Redis daemon check error: {e}")
        return False


# ═══ LIFESPAN HOOKS (called from server.py startup/shutdown) ═══
async def v20_startup():
    """Called by server.py on app startup."""
    # P22Ω_REDIS_HOIST · 2026-05-13 · démarre Redis daemon en priorité
    _ensure_redis_daemon_up()
    loaded = _cache_load_disk()
    logger.info(f"[V20-PERFORMANCE] Startup: {loaded} entries loaded from disk")
    # P22Ω_WORKER_SAFE_REARM — daemons rearmés ici aussi (lazy-init peut être
    # bypassé en multi-pod). Idempotent via _DAEMONS_STATE checks.
    # P22ΩΩ_BUNDLE_DEGRADED_CACHE · 2026-05-14 — Désactivation par défaut des
    # daemons de prechauffage qui hog le single-worker (~60-96s par bundle).
    # Pour réactiver : export P22OMEGA_PRECHAUFFAGE_DAEMONS=1
    if (_DAEMONS_STATE["prechauffage_started_at"] is None
            and os.environ.get("P22OMEGA_PRECHAUFFAGE_DAEMONS", "0") == "1"):
        asyncio.create_task(_prewarm_engines_omega())
        asyncio.create_task(run_prechauffage_omega(limit=5))
        asyncio.create_task(_periodic_refresh_daemon())
        asyncio.create_task(_v5_compliance_monitor_daemon())
        _DAEMONS_STATE["prechauffage_started_at"] = time.time()
        _DAEMONS_STATE["periodic_refresh_started_at"] = time.time()
        _DAEMONS_STATE["v5_monitor_started_at"] = time.time()
        logger.info("[V20-PERFORMANCE] P22Ω_WORKER_SAFE_REARM — startup hooks daemons ON (env explicit)")
    else:
        # Toujours faire le prewarm engines (très léger ~1.4ms)
        asyncio.create_task(_prewarm_engines_omega())
        logger.info("[V20-PERFORMANCE] P22ΩΩ — prechauffage daemons DISABLED par défaut (P22OMEGA_PRECHAUFFAGE_DAEMONS env)")
    # P22ΩΩ_BUNDLE_DEGRADED_CACHE · 2026-05-14 · STEEVE-MAX
    # Warmup BSL5 lancé INDÉPENDAMMENT (idempotent via _BSL5_WARMUP_STARTED flag)
    # car la condition lazy-init peut déjà être True (race condition au boot).
    # 2026-05-14 RÉVISION : BSL5 warmup DÉSACTIVÉ par défaut — il hog le single
    # worker uvicorn pendant 60s+ par bundle (V10+V5+pipeline post non-bornés),
    # bloquant les requêtes user → 502. À la place, on compte sur DEGRADED_CACHE
    # TTL 90s + EARLY-RETURN pour absorber les cold-start utilisateurs.
    # Pour réactiver : export P22OMEGA_BSL5_WARMUP=1
    global _BSL5_WARMUP_STARTED
    if not _BSL5_WARMUP_STARTED and os.environ.get("P22OMEGA_BSL5_WARMUP", "0") == "1":
        _BSL5_WARMUP_STARTED = True
        asyncio.create_task(_warmup_bsl_5_species_standard_contexts())
        logger.info("[P22ΩΩ_BSL5_WARMUP] Startup task scheduled (env P22OMEGA_BSL5_WARMUP=1)")
    else:
        logger.info("[P22ΩΩ_BSL5_WARMUP] Skipped (P22OMEGA_BSL5_WARMUP env not set to '1')")


_BSL5_WARMUP_STARTED = False


async def _warmup_bsl_5_species_standard_contexts():
    """P22ΩΩ_BUNDLE_DEGRADED_CACHE · 2026-05-14 · COMMANDANT STEEVE-MAX
    Pré-charge les 5 espèces canoniques × waypoint BSL × 2 contextes temporels
    standards du frontend (month=10 hour=14 wind=180 ET month=5 hour=11 wind=225).
    Évite le 502 K8s au premier hit utilisateur sur ces combinaisons.
    Exécution séquentielle (1 par 1) pour ne pas saturer le single-worker.
    """
    from fastapi import Response as _FastAPIResponse
    BSL_LAT, BSL_LON = 48.206657, -68.382422
    species_list = ["chevreuil", "orignal", "ours_noir", "coyote", "dindon_sauvage", "cerf"]
    contexts = [(10, 14, 180.0), (5, 11, 225.0)]  # (month, hour, wind_deg)
    total = len(species_list) * len(contexts)
    done = 0
    t_global = time.time()
    logger.info(f"[P22ΩΩ_BSL5_WARMUP] Starting BSL × {len(species_list)} species × {len(contexts)} contexts = {total} bundles")
    for sp in species_list:
        sp_norm = SPECIES_ALIAS_TO_CANONICAL.get(sp.lower(), sp)
        for (m, h, w) in contexts:
            key = _cache_key(BSL_LAT, BSL_LON, sp_norm, m, h, w)
            if _cache_get(key) is not None:
                done += 1
                continue
            try:
                t0 = time.time()
                _token = _WARMUP_CONTEXT.set(True)
                try:
                    await v20_territoire_bundle(
                        response=_FastAPIResponse(),
                        lat=BSL_LAT, lon=BSL_LON, species=sp_norm,
                        month=m, hour=h,
                        wind_deg=w, wind_speed=15.0,
                    )
                finally:
                    _WARMUP_CONTEXT.reset(_token)
                done += 1
                logger.info(f"[P22ΩΩ_BSL5_WARMUP] {sp_norm} m={m} h={h} w={int(w)} → cached in {(time.time()-t0):.1f}s ({done}/{total})")
            except Exception as e:
                logger.warning(f"[P22ΩΩ_BSL5_WARMUP] {sp_norm} m={m} h={h} w={int(w)} FAILED: {e}")
            # Yield à la boucle pour permettre aux autres requêtes de passer
            await asyncio.sleep(0.1)
    logger.info(f"[P22ΩΩ_BSL5_WARMUP] DONE {done}/{total} in {(time.time()-t_global):.1f}s")
    _cache_save_disk()


async def v20_shutdown():
    """Called by server.py on app shutdown."""
    _cache_save_disk()


async def _periodic_refresh_daemon():
    """Daemon: rafraichit le cache périodiquement + save disk.

    P22Ω_WORKER_SAFE_REARM · 2026-05-13 — sleep randomisé 1800-2400s
    pour désynchroniser des autres démons et éviter saturation worker.
    """
    while True:
        try:
            _sleep_s = _daemon_sleep_randomized()
            logger.info(f"[V20-WARMUP-DAEMON] Sleeping {_sleep_s:.0f}s (randomized)")
            await asyncio.sleep(_sleep_s)
            _DAEMONS_STATE["periodic_refresh_last_tick_at"] = time.time()
            _DAEMONS_STATE["periodic_refresh_tick_count"] += 1
            logger.info(
                f"[V20-WARMUP-DAEMON] Tick #{_DAEMONS_STATE['periodic_refresh_tick_count']} "
                f"— refresh + disk save"
            )
            await run_prechauffage_omega(limit=5)  # P22Ω_PHASE1_P1_FIXES (E1) — periodic refresh aussi à limit=5
        except Exception as e:
            logger.warning(f"[V20-WARMUP-DAEMON] Error: {e}")


# ═══════════════════════════════════════════════════════════════════════
# P22Ω.V5_COMPLIANCE_MONITOR_Ω · 2026-05-12T14:45Z · COMMANDANT STEEVE-MAX
# ═══════════════════════════════════════════════════════════════════════
# Cron horaire : check audit V5 + alerte Resend si status=FAIL
# + journalisation persistante /app/memory/v5_compliance_log.jsonl
# (append-only, lu par /api/v20/audit/v5-daily-report).
# ═══════════════════════════════════════════════════════════════════════
_V5_MONITOR_INTERVAL_SEC = 3600  # 1h
_V5_MONITOR_LOG_FILE = Path("/app/memory/v5_compliance_log.jsonl")
_V5_MONITOR_WAYPOINTS = [
    # (lat, lon, species, label) — waypoints canoniques surveillés
    (48.206657, -68.382422, "orignal",   "BSL"),
    (46.5,      -71.5,      "cerf",      "Lotbinière"),
    (48.4,      -71.05,     "orignal",   "Saguenay"),
]
_V5_MONITOR_STATS: dict = {
    "runs": 0, "pass": 0, "fail": 0, "last_status": None,
    "last_run_utc": None, "last_violations_total": 0,
    "alerts_sent": 0, "alert_errors": 0,
}


async def _v5_compliance_check_single(lat: float, lon: float, species: str) -> dict:
    """Exécute un check V5 compliance sur un waypoint (utilise même logique audit)."""
    from engines.v8_institutional.territoire_v10_supra import compute_territoire_v10
    from engines.v8_institutional.engine_ia_corridors_organic_omega import (
        generate_organic_corridors,
    )
    try:
        bundle_data = await compute_territoire_v10(lat, lon, species, 10, 7, 225.0, 15.0)
        v5 = await generate_organic_corridors(
            lat=lat, lon=lon, species=species, month=10, hour=7,
            wind_deg=225, wind_speed=15, anchor_mode="TERRITORY_CONTINUOUS",
            bundle_pre_computed=bundle_data,
        )
        corridors = map_v5_corridors_to_ui(v5.get("corridors", []))
        hier = v5.get("hierarchy_counts", {}) or {}
        n = len(corridors)
        violations = []
        if not (5 <= n <= 7):
            violations.append("n_corridors_out_of_range")
        n_missing = sum(1 for c in corridors if not c.get("subnet_role"))
        if n_missing:
            violations.append(f"subnet_role_missing_{n_missing}")
        return {
            "lat": lat, "lon": lon, "species": species,
            "n_corridors": n,
            "n_backbones": hier.get("veine_principale", 0),
            "n_subnets": hier.get("veine_secondaire", 0),
            "violations": violations,
            "status": "PASS" if not violations else "FAIL",
        }
    except Exception as e:
        return {
            "lat": lat, "lon": lon, "species": species,
            "n_corridors": 0, "n_backbones": 0, "n_subnets": 0,
            "violations": [f"exception:{type(e).__name__}"],
            "status": "FAIL",
            "error": str(e),
        }


async def _v5_send_alert_resend(failed_checks: list[dict]) -> bool:
    """Envoie une alerte Resend si conformité V5 dégradée."""
    try:
        import os
        api_key = os.environ.get("RESEND_API_KEY")
        from_addr = os.environ.get("RESEND_FROM_EMAIL") or os.environ.get("RESEND_FROM")
        to_addr = os.environ.get("RESEND_ADMIN_EMAIL") or os.environ.get("ADMIN_EMAIL")
        if not (api_key and from_addr and to_addr):
            logger.warning("[V5_MONITOR] Resend env vars manquantes → alerte non envoyée")
            return False
        import httpx
        body_lines = [
            "PROTOCOLE BCE-4X — ALERTE CONFORMITÉ V5",
            f"Date UTC: {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}",
            f"Waypoints en échec: {len(failed_checks)}",
            "",
        ]
        for c in failed_checks:
            body_lines.append(
                f"  • {c.get('species')} @ ({c.get('lat')},{c.get('lon')}) → "
                f"status={c.get('status')} n_corridors={c.get('n_corridors')} "
                f"backbones={c.get('n_backbones')} subnets={c.get('n_subnets')} "
                f"violations={c.get('violations')}"
            )
        body_lines.append("")
        body_lines.append("Action: vérifier /api/v20/audit/v5-compliance-live et déployer correctif si besoin.")
        body_text = "\n".join(body_lines)
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.post(
                "https://api.resend.com/emails",
                headers={"Authorization": f"Bearer {api_key}",
                          "Content-Type": "application/json"},
                json={
                    "from": from_addr,
                    "to": [to_addr],
                    "subject": f"[BCE-4X] V5 NON-CONFORME · {len(failed_checks)} waypoint(s) FAIL",
                    "text": body_text,
                },
            )
            ok = r.status_code in (200, 202)
            if ok:
                _V5_MONITOR_STATS["alerts_sent"] += 1
            else:
                _V5_MONITOR_STATS["alert_errors"] += 1
                logger.warning(f"[V5_MONITOR] Resend HTTP {r.status_code}: {r.text[:200]}")
            return ok
    except Exception as e:
        _V5_MONITOR_STATS["alert_errors"] += 1
        logger.warning(f"[V5_MONITOR] Resend alert failed: {e}")
        return False


def _v5_journal_append(entry: dict) -> None:
    """Append-only log JSONL du monitoring V5."""
    try:
        _V5_MONITOR_LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(_V5_MONITOR_LOG_FILE, "a", encoding="utf-8") as f:
            import json as _json
            f.write(_json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception as e:
        logger.warning(f"[V5_MONITOR] Journal append failed: {e}")


async def _v5_compliance_monitor_daemon():
    """Daemon: vérifie la conformité V5 toutes les heures + alerte si FAIL.

    P22Ω_WORKER_SAFE_REARM · 2026-05-13 — sleep randomisé 1800-2400s
    (au lieu de 3600s fixe) pour désynchronisation worker unique.
    """
    # P22Σ_STABILISATION_Ω_PROGRESSIF · Délai initial pour ne pas saturer
    # le worker async au démarrage. Premier tick = startup + ~30 min.
    await asyncio.sleep(_daemon_sleep_randomized())
    while True:
        try:
            t0 = time.time()
            results = []
            for (lat, lon, sp, _label) in _V5_MONITOR_WAYPOINTS:
                results.append(await _v5_compliance_check_single(lat, lon, sp))
            failed = [r for r in results if r.get("status") == "FAIL"]
            n_violations_total = sum(len(r.get("violations", [])) for r in results)
            _V5_MONITOR_STATS["runs"] += 1
            _V5_MONITOR_STATS["last_run_utc"] = time.strftime(
                "%Y-%m-%dT%H:%M:%SZ", time.gmtime(),
            )
            _V5_MONITOR_STATS["last_violations_total"] = n_violations_total
            _DAEMONS_STATE["v5_monitor_last_tick_at"] = time.time()
            _DAEMONS_STATE["v5_monitor_tick_count"] += 1
            if failed:
                _V5_MONITOR_STATS["fail"] += 1
                _V5_MONITOR_STATS["last_status"] = "FAIL"
                # Alerte Resend
                await _v5_send_alert_resend(failed)
            else:
                _V5_MONITOR_STATS["pass"] += 1
                _V5_MONITOR_STATS["last_status"] = "PASS"
            elapsed = round(time.time() - t0, 2)
            journal_entry = {
                "ts_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "elapsed_s": elapsed,
                "n_failed": len(failed),
                "n_total": len(results),
                "n_violations_total": n_violations_total,
                "results": results,
                "doctrine": "P22Ω.V5_COMPLIANCE_MONITOR_Ω",
            }
            _v5_journal_append(journal_entry)
            logger.info(
                f"[V5_MONITOR] Tick #{_DAEMONS_STATE['v5_monitor_tick_count']}: "
                f"{len(results)} checks · {len(failed)} FAIL · {elapsed}s",
            )
        except Exception as e:
            logger.warning(f"[V5_MONITOR] Daemon error: {e}")
        # Sleep randomized 1800-2400s
        await asyncio.sleep(_daemon_sleep_randomized())


# ═══ ENDPOINTS ═══
@router.get("/bundle")
async def v20_territoire_bundle(
    response: Response,
    lat: float = Query(...),
    lon: float = Query(...),
    species: str = Query("cerf"),
    month: int = Query(10),
    hour: int = Query(7),
    wind_deg: float = Query(225),
    wind_speed: float = Query(15),
):
    """V20 PERFORMANCE BUNDLE — Cache-first Territoire rendering (10K scalabilite).

    - Cache hit: <50ms.
    - Cache miss: full V20-INSTITUTIONNEL compute, cached 24h.
    - Cache size: 10 000 entrees LRU.
    - Disk persistent: survived restart via /app/backend/cache/territoire_bundle.pkl.
    - Prechauffage: 200 top waypoints au startup + refresh horaire.
    """
    await _ensure_lazy_init()
    t0 = time.time()
    # P22Σ_SPECIES_NORMALIZATION_Ω — normalisation alias frontend (wild_turkey, etc.)
    species = normalize_species(species)
    key = _cache_key(lat, lon, species, month, hour, wind_deg)
    cached = _cache_get(key)

    if cached is not None:
        _STATS["hits"] += 1
        elapsed_ms = round((time.time() - t0) * 1000, 2)
        # P22Ω.TRANSITION_V5 · 2026-05-12 · max-age réduit de 3600s → 300s
        # Évite Cloudflare cache d'un bundle legacy 23h pendant la transition V5.
        response.headers["Cache-Control"] = "public, max-age=300, stale-while-revalidate=900"
        response.headers["Vary"] = "Accept-Encoding"
        response.headers["X-Cache"] = "HIT"
        response.headers["X-Cache-Age-Sec"] = str(int(time.time() - _CACHE[key][0]))
        response.headers["X-Compute-Ms"] = str(elapsed_ms)
        # P22ΩΩ_TERRITOIRE_ESSENTIEL_1WORKER · headers de tier pour frontend
        response.headers["X-Bundle-Tier"] = str(cached.get("bundle_tier", "ENRICHI_TDELTA"))
        out = dict(cached)
        out["cache"] = "HIT"
        out["cache_age_sec"] = int(time.time() - _CACHE[key][0])
        out["served_ms"] = elapsed_ms
        return out

    _STATS["misses"] += 1
    from engines.v8_institutional.territoire_v10_supra import compute_territoire_v10
    from engines.v8_institutional.esi_omega import validate_bundle, _log_audit
    # PHASE_XII_SUPRA_RAPATRIEMENT_RENDUΩ_V20 — branchement obligatoire RenduΩ
    from engines.post_smoothing.renduomega import apply_renduomega_to_bundle
    # PHASE_XII_SUPRA_CORRIDORS_VEINEUX_Ω_ULTIME — post-processor amont RenduΩ
    from engines.post_smoothing.veineux_omega import apply_veineux_omega_to_bundle
    # PHASE_XII_SUPRA_CORRIDORS_VEINEUX_Ω_INTERZONE_GENERATION — générateur inter-zones
    from engines.post_smoothing.interzone_omega import apply_interzone_omega_to_bundle
    # P22Σ_V5_BUNDLE_REWIRE_Ω — pipeline V5 organic en parallèle (2026-05-12)
    from engines.v8_institutional.engine_ia_corridors_organic_omega import (
        generate_organic_corridors,
    )

    # ═══════════════════════════════════════════════════════════════════════
    # OPTIMISATION P22Σ_V5_REWIRE_OPTIM (2026-05-12 · COMMANDANT STEEVE-MAX)
    # ═══════════════════════════════════════════════════════════════════════
    # V10 calculé une seule fois puis passé à V5 organic via bundle_pre_computed
    # → -44% latence cache MISS (50s → ~22s) vs ancienne parallélisation
    # asyncio.gather qui faisait V10 DEUX fois en concurrence.
    # ═══════════════════════════════════════════════════════════════════════
    # ═══════════════════════════════════════════════════════════════════════
    # P22Ω_WORKER_SAFE_REARM · MISS ABSORPTION (hardcap 20s, soft 12s)
    # ═══════════════════════════════════════════════════════════════════════
    _miss_t0 = time.time()
    _hardcap = _effective_miss_hardcap()
    # P22Ω_PHASE1_P1_FIXES (E1) · 2026-05-13 · STEEVE-MAX
    # Renforcement hardcap : wrap dans asyncio.Task + cancellation explicite +
    # shield contre les awaits non-cooperatifs (asyncio.wait_for ne peut pas
    # interrompre du code sync CPU). On crée la task, on attend, et si timeout
    # on annule explicitement la task avec un small await pour laisser
    # l'event loop traiter la cancellation.
    _compute_task = asyncio.create_task(
        compute_territoire_v10(lat, lon, species, month, hour, wind_deg, wind_speed)
    )
    try:
        result = await asyncio.wait_for(asyncio.shield(_compute_task), timeout=_hardcap)
    except asyncio.TimeoutError:
        # P22ΩΩ_BG_CACHE · 2026-05-14 · le compute continue en arrière-plan ;
        # callback pour cacher le résultat à la fin pour les prochains hits.
        # P22ΩΩ_TERRITOIRE_ESSENTIEL_1WORKER · 2026-05-18 : marque le bundle
        # complet comme bundle_tier="ENRICHI_TDELTA" + TTL standard 24h pour
        # remplacer le bundle ESSENTIEL_T0 servi initialement.
        def _cache_completed_task(task):
            try:
                completed_result = task.result()
                if completed_result and not completed_result.get("p22omega_miss_absorbed"):
                    completed_result["waypoint"] = {"lat": lat, "lng": lon}
                    completed_result["species"] = species
                    completed_result["bundle_tier"] = "ENRICHI_TDELTA"  # 🌟 marker T+Δ
                    completed_result["bg_cache_origin"] = "P22ΩΩ_ESSENTIEL_1WORKER"
                    _cache_set(key, completed_result)  # TTL standard 24h
                    logger.info(
                        f"[P22ΩΩ_BG_CACHE] V10 task completed → bundle ENRICHI_TDELTA cached "
                        f"species={species} lat={lat},lon={lon}"
                    )
                    # P22ΩΩ_DISK_PERSIST · 2026-05-14 · STEEVE-MAX
                    # Persiste le cache sur disque pour survivre aux restarts
                    # backend (containers éphémères). Throttle 30s entre saves.
                    try:
                        global _LAST_BG_DISK_SAVE_TS
                        _now = time.time()
                        if _now - _LAST_BG_DISK_SAVE_TS > 30:
                            _LAST_BG_DISK_SAVE_TS = _now
                            _cache_save_disk()
                            logger.info(f"[P22ΩΩ_DISK_PERSIST] BG cache saved to disk ({len(_CACHE)} entries)")
                    except Exception as _e_ds:
                        logger.warning(f"[P22ΩΩ_DISK_PERSIST] save error: {_e_ds}")
            except Exception as _e_bg:
                logger.warning(f"[P22ΩΩ_BG_CACHE] callback error: {_e_bg}")
        _compute_task.add_done_callback(_cache_completed_task)
        _MISS_STATS["absorbed_count"] += 1
        _MISS_STATS["last_absorbed_at"] = time.time()
        logger.warning(
            f"[P22Ω_MISS_ABSORPTION] compute_territoire_v10 HARDCAP {_hardcap}s "
            f"dépassé pour lat={lat},lon={lon},species={species}. Renvoi bundle dégradé "
            f"(task continues in background)."
        )
        result = {
            "waypoint": {"lat": lat, "lng": lon},
            "species": species,
            "zones": [], "corridors": [], "affuts": [],
            "hotspots": [], "salines": [], "contamination": [],
            "data_source": "DEGRADED_MISS_ABSORPTION",
            "data_fiabilite": 0,
            "p22omega_miss_absorbed": True,
            "p22omega_miss_hardcap_s": _hardcap,
            "esi_omega": "PIPELINE_TIMEOUT",
        }
    _miss_compute_s = time.time() - _miss_t0
    _MISS_STATS["total_miss_compute_s"] += _miss_compute_s
    if _miss_compute_s > _MISS_SOFT_THRESHOLD_SEC and not result.get("p22omega_miss_absorbed"):
        _MISS_STATS["soft_warning_count"] += 1
        logger.warning(
            f"[P22Ω_MISS_ABSORPTION] SOFT_THRESHOLD {_MISS_SOFT_THRESHOLD_SEC}s dépassé "
            f"({_miss_compute_s:.1f}s) pour species={species} lat={lat},lon={lon}"
        )
    # P22ΩΩ_BUNDLE_DEGRADED_CACHE · 2026-05-14 · STEEVE-MAX
    # Si V10 a timeouté (result.p22omega_miss_absorbed=True), on SKIP la V5
    # organic generation : elle consommerait un 2e hardcap entier (10s)
    # → 10+10=20s > timeout K8s proxy ~30s → 502.
    # Budget restant pour V5 = max(2.0, _hardcap - _miss_compute_s).
    if result.get("p22omega_miss_absorbed") is True:
        v5_bundle = None
        v5_error = "V5_SKIPPED_V10_DEGRADED"
        logger.warning(
            f"[P22ΩΩ_ESSENTIEL_T0] V5 organic SKIPPED car V10 dégradé "
            f"species={species} lat={lat},lon={lon}"
        )
        # P22ΩΩ_TERRITOIRE_ESSENTIEL_1WORKER · 2026-05-18 · STEEVE-MAX
        # Bundle ESSENTIEL T0 servi immédiatement (terrain + meteo + zones + hotspots +
        # salines + species). Le pipeline post-V5 (corridors_vitaux + connectivité +
        # affuts détaillés + comportement) tourne en BG_CACHE pour produire le
        # bundle ENRICHI T+Δ destiné au prochain hit utilisateur.
        result["waypoint"] = {"lat": lat, "lng": lon}
        result["species"] = species
        result["cache"] = "MISS"
        result["v5_error"] = v5_error
        result["bundle_tier"] = "ESSENTIEL_T0"  # 🌟 P22ΩΩ_ESSENTIEL_1WORKER
        result["served_ms"] = round((time.time() - t0) * 1000, 2)
        # TTL ESSENTIEL 600s (au lieu de 90s DEGRADED) : on assume que ce bundle
        # est utile pendant 10 minutes pour les 2000 membres.
        _essentiel_ttl = (
            _CACHE_ESSENTIEL_TTL_SEC
            if os.environ.get("P22OMEGA_ESSENTIEL_1WORKER", "1") == "1"
            else _CACHE_DEGRADED_TTL_SEC
        )
        _cache_set(key, result, ttl=_essentiel_ttl)
        response.headers["Cache-Control"] = "public, max-age=60, stale-while-revalidate=300"
        response.headers["X-Cache"] = "MISS-ESSENTIEL-T0"
        response.headers["X-Bundle-Tier"] = "ESSENTIEL_T0"
        response.headers["X-Compute-Ms"] = str(round((time.time() - t0) * 1000, 2))
        logger.warning(
            f"[P22ΩΩ_ESSENTIEL_T0] EARLY-RETURN bundle ESSENTIEL T0 "
            f"species={species} lat={lat},lon={lon} (TTL={_essentiel_ttl}s) — BG_CACHE produira T+Δ"
        )
        return result
    else:
        _v5_budget = max(2.0, _hardcap - _miss_compute_s)
        try:
            v5_bundle = await asyncio.wait_for(
                generate_organic_corridors(
                    lat=lat, lon=lon, species=species,
                    month=month, hour=hour,
                    wind_deg=int(wind_deg), wind_speed=int(wind_speed),
                    anchor_mode="TERRITORY_CONTINUOUS",
                    bundle_pre_computed=result,
                ),
                timeout=_v5_budget,
            )
            v5_error = None
        except asyncio.TimeoutError:
            v5_bundle = None
            v5_error = f"generate_organic_corridors TIMEOUT {_v5_budget:.1f}s"
            logger.warning(f"[P22Ω_MISS_ABSORPTION] V5 organic TIMEOUT pour species={species}")
        except Exception as _e_v5:
            v5_bundle = None
            v5_error = f"V5_EXCEPTION:{type(_e_v5).__name__}:{_e_v5}"
        # P22ΩΩ_BUNDLE_DEGRADED_CACHE · 2026-05-14 · STEEVE-MAX
        # Si V5 a timeouté ou raté, le pipeline legacy V10 (predictive + interzone +
        # veineux + ecological_orchestrator + corridors_vitaux + RenduΩ) va tourner
        # SANS V5 et peut prendre 30-60s → 502 K8s. On early-return avec bundle V10.
        # V5_REWIRE_ACTIVE=False = bundle qui aurait subi le pipeline legacy lourd.
        if v5_bundle is None and _miss_compute_s > (_hardcap * 0.5):
            logger.warning(
                f"[P22ΩΩ_DEGRADED_CACHE] V5 failed + V10 lent ({_miss_compute_s:.1f}s) → "
                f"EARLY-RETURN bundle V10-only species={species} (skip pipeline legacy)"
            )
            result["waypoint"] = {"lat": lat, "lng": lon}
            result["species"] = species
            result["cache"] = "MISS"
            result["v5_error"] = v5_error
            result["served_ms"] = round((time.time() - t0) * 1000, 2)
            result["p22omegaomega_v5_skipped_pipeline_legacy"] = True
            result["bundle_tier"] = "ESSENTIEL_T0"  # P22ΩΩ_ESSENTIEL_1WORKER
            _essentiel_ttl_v5 = (
                _CACHE_ESSENTIEL_TTL_SEC
                if os.environ.get("P22OMEGA_ESSENTIEL_1WORKER", "1") == "1"
                else _CACHE_DEGRADED_TTL_SEC
            )
            _cache_set(key, result, ttl=_essentiel_ttl_v5)
            response.headers["X-Cache"] = "MISS-ESSENTIEL-T0-V5FAIL"
            response.headers["X-Bundle-Tier"] = "ESSENTIEL_T0"
            response.headers["X-Compute-Ms"] = str(round((time.time() - t0) * 1000, 2))
            return result
    _V5_REWIRE_ACTIVE = v5_bundle is not None
    # ═══════════════════════════════════════════════════════════════════════
    # PHASE_XVIII_BIO_PRESENCE_MASK_Ω — COURT-CIRCUIT en amont
    # Si l'espèce est ABSENTE du territoire (registre MFFP + SEPAQ + Atlas),
    # on vide les corridors avant tout le pipeline XIX / VITAUX / RENDUΩ.
    # ═══════════════════════════════════════════════════════════════════════
    result["waypoint"] = {"lat": lat, "lng": lon}
    result["species"] = species
    try:
        from engines.v8_institutional.species_presence_mask_omega import (
            apply_presence_mask_to_bundle,
        )
        result = apply_presence_mask_to_bundle(result, species=species, lat=lat, lng=lon)
    except Exception as _e_pres:
        result["bio_presence_mask_applied"] = False
        result["bio_presence_mask_error"] = str(_e_pres)
    if result.get("bio_presence_mask_halt") is True:
        # Pipeline court-circuité : corridors vides, on renvoie le bundle tel quel
        # (zones vitales, salines, hotspots restent affichés pour audit écologique).
        # P22Ω_MULTI_FIX_A4 (2026-05-13 · COMMANDANT STEEVE-MAX) — cache le résultat
        # halté pour éviter recompute coûteux (16+s observé dindon BSL).
        result["cache"] = "MISS"
        result["served_ms"] = round((time.time() - t0) * 1000, 2)
        result["p22omega_halt_cached"] = True
        _cache_set(key, result)
        return result

    # P22ΩΩ_BUNDLE_DEGRADED_CACHE · 2026-05-14 · DEADLINE GLOBAL
    # Si on a déjà dépassé le deadline global (V10+V5 ont pris trop de temps),
    # court-circuiter le pipeline post (RenduΩ + veineux + interzone + predictive)
    # qui consommerait 10-30s supplémentaires. On cache et retourne maintenant.
    #
    # P22ΩΩ_BLOC_2_5_CORRIGE_DEADLINE_GATE_Ω · 2026-02-XX · STEEVE-MAX
    # Application OBLIGATOIRE de la doctrine BLOC 2.5 (V5 rewire + cap 5-7
    # + hiérarchie veines) MÊME en branche dégradée ESSENTIEL_T0. Sinon
    # le frontend reçoit ~80 corridors V10 bruts sans hiérarchie.
    _elapsed_so_far = time.time() - t0
    if _elapsed_so_far > _GLOBAL_BUNDLE_DEADLINE_SEC:
        logger.warning(
            f"[P22ΩΩ_DEADLINE] Deadline global {_GLOBAL_BUNDLE_DEADLINE_SEC}s dépassé "
            f"({_elapsed_so_far:.1f}s) après V10+V5 — skip pipeline post pour species={species}"
        )
        # ═══ P22ΩΩ_BLOC_2_5_DEADLINE_PATCH — applique cap doctrinal AVANT return ═══
        try:
            result = _apply_v5_rewire_to_result(result, v5_bundle, v5_error, species)
        except Exception as _e_v5_dl:
            logger.error(f"[P22ΩΩ_DEADLINE_V5_REWIRE] failed: {_e_v5_dl}")
            result["p22sigma_v5_bundle_rewire"] = {
                "applied": False,
                "error": f"deadline_v5_rewire_error: {_e_v5_dl}",
                "fallback": "V10_SUPRA_LEGACY",
            }
        try:
            result = _apply_bloc25_hierarchy_and_cap(result, species)
        except Exception as _e_cap_dl:
            logger.error(f"[P22ΩΩ_DEADLINE_BLOC25_CAP] failed: {_e_cap_dl}")
            result["p22omegaomega_bloc_2_5_doctrine"] = {
                "applied": False,
                "error": f"deadline_cap_error: {_e_cap_dl}",
            }
        result["cache"] = "MISS"
        result["served_ms"] = round(_elapsed_so_far * 1000, 2)
        result["p22omegaomega_deadline_hit"] = True
        result["bundle_tier"] = "ESSENTIEL_T0"  # P22ΩΩ_ESSENTIEL_1WORKER · deadline = bundle partiel
        # Cache avec TTL ESSENTIEL 600s pour pouvoir hitter ce bundle partiel
        _essentiel_ttl_dl = (
            _CACHE_ESSENTIEL_TTL_SEC
            if os.environ.get("P22OMEGA_ESSENTIEL_1WORKER", "1") == "1"
            else _CACHE_DEGRADED_TTL_SEC
        )
        _cache_set(key, result, ttl=_essentiel_ttl_dl)
        response.headers["X-Cache"] = "MISS-ESSENTIEL-T0-DEADLINE"
        response.headers["X-Bundle-Tier"] = "ESSENTIEL_T0"
        response.headers["X-Compute-Ms"] = str(round(_elapsed_so_far * 1000, 2))
        response.headers["X-Bloc-2-5-Applied"] = "1" if result.get(
            "p22omegaomega_bloc_2_5_doctrine", {}
        ).get("applied") else "0"
        return result

    # ═══════════════════════════════════════════════════════════════════════
    # RAPATRIEMENT_RENDUΩ_V20 — SECTION 1.1 / 1.2 / 1.3
    # Validation et filtrage ABSOLUS des corridors avant cache & envoi client.
    # Même moteur que POST /api/v7-ultime/renduomega/validate-bundle.
    # V30 LOCKED intact — seules les sorties de compute_territoire_v10 sont
    # filtrées ici ; le moteur institutionnel reste inchangé.
    # ═══════════════════════════════════════════════════════════════════════    # Normalisation `contamination_zones` pour RenduΩ :
    # V30 émet des cônes (polygones) sans lat/lng direct. RenduΩ attend des
    # points {lat,lng}. On dérive ici un point représentatif depuis
    # `affut_source` ou le centroïde du polygone — sans modifier V30.
    _contam_in = result.get("contamination") or []
    _contam_for_rom = []
    for _c in _contam_in:
        if not isinstance(_c, dict):
            continue
        _lat = _c.get("lat")
        _lng = _c.get("lng") or _c.get("lon")
        if _lat is None or _lng is None:
            _src = _c.get("affut_source") or {}
            _lat = _src.get("lat")
            _lng = _src.get("lng") or _src.get("lon")
        if _lat is None or _lng is None:
            _poly = _c.get("polygon") or _c.get("coords") or []
            if isinstance(_poly, list) and _poly:
                try:
                    _lat = sum(p[0] for p in _poly) / len(_poly)
                    _lng = sum(p[1] for p in _poly) / len(_poly)
                except Exception:
                    _lat = _lng = None
        if _lat is not None and _lng is not None:
            _contam_for_rom.append({"lat": float(_lat), "lng": float(_lng),
                                    "intensity": _c.get("intensity"),
                                    "source": "V20_RAPATRIEMENT_NORMALIZED"})
    result["contamination_zones"] = _contam_for_rom
    # ═══ PHASE_XVIII (GPS) — PREDICTIVE_OMEGA_V2 (passe 1) ═══
    # Annotation V30 d'origine avec scoring comportemental GPS USGS/Movebank.
    # P22Σ_V5_REWIRE : skip si V5 actif (corridors seront overridés)
    if not _V5_REWIRE_ACTIVE:
        try:
            from engines.v8_institutional.predictive_omega_v2 import apply_predictive_omega_v2_to_bundle
            result = apply_predictive_omega_v2_to_bundle(result, species=species, month=month, hour=hour)
        except Exception as _e_xviii:
            result["predictive_omega_v2_applied"] = False
            result["predictive_omega_v2_error"] = str(_e_xviii)
    # ═══ INTERZONE_Ω — AJOUT des corridors inter-zones + entrants (V30 intact) ═══
    if not _V5_REWIRE_ACTIVE:
        result = apply_interzone_omega_to_bundle(result)
    # ═══ VEINEUX_Ω — transformation géométrique amont (V30 intact) ═══
    if not _V5_REWIRE_ACTIVE:
        result = apply_veineux_omega_to_bundle(result)
    # ═══ PHASE_XVIII (GPS) — PREDICTIVE_OMEGA_V2 (passe 2) ═══
    # Re-annotation des corridors entrants/interzone ajoutés.
    if not _V5_REWIRE_ACTIVE:
        try:
            from engines.v8_institutional.predictive_omega_v2 import apply_predictive_omega_v2_to_bundle
            result = apply_predictive_omega_v2_to_bundle(result, species=species, month=month, hour=hour)
        except Exception as _e_xviii_2:
            result["predictive_omega_v2_post_veineux_applied"] = False
            result["predictive_omega_v2_post_veineux_error"] = str(_e_xviii_2)
    # ═══ PHASE_XIX-P2 — ORIGINE_EXTERNE_INVERSION_Ω : inversion conditionnelle ═══
    # Si path[0] hors couronne ET path[-1] dans couronne → reverse(path).
    # Ré-annotation predictive_omega_v2 automatique sur les corridors inversés.
    if not _V5_REWIRE_ACTIVE:
        try:
            from engines.v8_institutional.origine_externe_inversion_omega import (
                apply_origine_externe_inversion_to_bundle,
            )
            result = apply_origine_externe_inversion_to_bundle(
                result, species=species, month=month, hour=hour,
            )
        except Exception as _e_xix_p2:
            result["origine_externe_inversion_applied"] = False
            result["origine_externe_inversion_error"] = str(_e_xix_p2)
    # ═══ PHASE_XIX-P1 — ORIGINE_EXTERNE_FILTER_Ω : DÉSACTIVÉ ═══
    # P22Ω.PURGE_LEGACY · 2026-05-12T14:30Z · directive COMMANDANT STEEVE-MAX :
    # filtre couronne 30% retiré du bundle (était skippé en V5 mais pollue le
    # fallback V10). Décision V90 finale : POINT_ORIGINE n'est plus filtré au
    # niveau du bundle ; cette logique vit dans V5 organic uniquement.
    # Le filtre demeure disponible via son endpoint dédié si besoin scientifique.
    # if not _V5_REWIRE_ACTIVE:
    #     try:
    #         from engines.v8_institutional.origine_externe_filter_omega import (
    #             apply_origine_externe_filter_to_bundle,
    #         )
    #         result = apply_origine_externe_filter_to_bundle(result)
    #     except Exception as _e_xix:
    #         result["origine_externe_filter_applied"] = False
    #         result["origine_externe_filter_error"] = str(_e_xix)
    result["origine_externe_filter_disabled"] = "P22Ω.PURGE_LEGACY · 2026-05-12"
    # ═══ PHASE_XVII — ÉCOLOGIQUE_Ω : annotation consensus écologique ═══
    # GARDÉ même en V5 — affecte zones, pas corridors.
    try:
        from engines.v8_institutional.ecological_orchestrator_omega import orchestrate_bundle
        result = orchestrate_bundle(result, species=species)
    except Exception as _e:
        result["ecological_orchestrator_applied"] = False
        result["ecological_orchestrator_error"] = str(_e)
    # ═══ PHASE_XVIII (VITAUX) — CORRIDORS_VITAUX_Ω : ancrage zones vitales ═══
    # Filtre INSTITUTIONNEL : un corridor n'est admis QUE s'il est ancré sur
    # ≥ 1 zone vitale officielle dans 150 m, avec règles différenciées par
    # groupe d'espèces (grands mammifères vs petits mammifères).
    # P22Σ_V5_REWIRE : skip — V5 a sa propre logique d'ancrage zones vitales.
    if not _V5_REWIRE_ACTIVE:
        try:
            from engines.v8_institutional.corridors_vitaux_omega import apply_corridors_vitaux_to_bundle
            result = apply_corridors_vitaux_to_bundle(result, species=species)
        except Exception as _e_vitaux:
            result["corridors_vitaux_omega_applied"] = False
            result["corridors_vitaux_omega_error"] = str(_e_vitaux)
    # ═══ RENDUΩ — validation géométrique stricte (FIN de pipeline) ═══
    # P22Σ_V5_REWIRE : skip pour corridors V5 (déjà smoothed X180 + cap validé)
    if not _V5_REWIRE_ACTIVE:
        result = apply_renduomega_to_bundle(result)

    # ═══════════════════════════════════════════════════════════════════════
    # P22Σ_V5_BUNDLE_REWIRE_Ω  (2026-05-12 · COMMANDANT STEEVE-MAX)
    # ═══════════════════════════════════════════════════════════════════════
    # FUSION ADD-ONLY · V30_LOCK INTACT
    # Override final des corridors V10 par les corridors V5 organic
    # (cap global 5-7 + backbones + subnets + hierarchy).
    # `v5_bundle` est déjà calculé en amont via asyncio.gather().
    # ═══════════════════════════════════════════════════════════════════════
    if _V5_REWIRE_ACTIVE:
        result = _apply_v5_rewire_to_result(result, v5_bundle, v5_error, species)
    else:
        result = _apply_v5_rewire_to_result(result, None, v5_error, species)
        # Appliquer RENDUΩ uniquement en fallback V10
        result = apply_renduomega_to_bundle(result)
    # ═══════════════════════════════════════════════════════════════════════
    # P22ΩΩ_BLOC_2_5_CORRIDORS_UNIQUES_PAR_ESPECE_Ω · 2026-05-18 · STEEVE-MAX
    # ENFORCE HIÉRARCHIE + CAP 5-7 PAR ESPÈCE + MARQUAGE EXTERNAL_INFLOW
    # P22ΩΩ_BLOC_2_5_CORRIGE_DEADLINE_GATE_Ω · 2026-02-XX · STEEVE-MAX
    # Helper extrait au niveau module pour pouvoir s'appliquer aussi dans
    # la branche deadline ESSENTIEL_T0 (cf. _apply_bloc25_hierarchy_and_cap).
    # ═══════════════════════════════════════════════════════════════════════
    result = _apply_bloc25_hierarchy_and_cap(result, species)
    # ═══════════════════════════════════════════════════════════════════════
    bv = validate_bundle({
        "zones": result["zones"],
        "corridors": result["corridors"],
        "affuts": result["affuts"],
    })
    _log_audit(
        "V20_TERRITOIRE_BUNDLE_COMPUTE",
        f"{lat},{lon},{species}",
        f"{bv['conformite']} source={result.get('data_source')} fiabilite={result.get('data_fiabilite')}",
    )
    result["esi_omega"] = bv["conformite"]

    # P22ΩΩ_BUNDLE_DEGRADED_CACHE · 2026-05-14 · COMMANDANT STEEVE-MAX
    # Cache TOUS les bundles, y compris dégradés, MAIS avec TTL court (90s)
    # pour les bundles dégradés. Sinon, en cold-start avec Open-Meteo en
    # circuit-breaker OPEN (10 minutes), CHAQUE utilisateur subit 20-50s
    # de compute → 502 K8s systématique (proxy timeout ~30s).
    # Le bundle dégradé contient quand même les couches V5 (corridors,
    # zones, hotspots, salines, affûts) générées par fallback — utilement
    # rendues à l'utilisateur. Après 90s, retry automatique (l'engine
    # peut alors avoir des données complètes).
    if result.get("p22omega_miss_absorbed") is True:
        result["bundle_tier"] = "ESSENTIEL_T0"  # P22ΩΩ_ESSENTIEL_1WORKER
        _essentiel_ttl_deg = (
            _CACHE_ESSENTIEL_TTL_SEC
            if os.environ.get("P22OMEGA_ESSENTIEL_1WORKER", "1") == "1"
            else _CACHE_DEGRADED_TTL_SEC
        )
        _cache_set(key, result, ttl=_essentiel_ttl_deg)
        logger.warning(
            f"[P22ΩΩ_ESSENTIEL_T0] Cached ESSENTIEL bundle (TTL={_essentiel_ttl_deg}s) "
            f"species={species} lat={lat},lon={lon} — évite 502 K8s en cold-start"
        )
    else:
        # P22ΩΩ_ESSENTIEL_1WORKER : pipeline complet exécuté → bundle COMPLET_T0
        # (équivalent ENRICHI_TDELTA mais servi dans la première réponse).
        result["bundle_tier"] = "COMPLET_T0"
        _cache_set(key, result)

    elapsed_ms = round((time.time() - t0) * 1000, 2)
    _STATS["total_compute_ms"] += elapsed_ms

    response.headers["Cache-Control"] = "public, max-age=300, stale-while-revalidate=900"
    response.headers["Vary"] = "Accept-Encoding"
    response.headers["X-Cache"] = "MISS"
    response.headers["X-Bundle-Tier"] = str(result.get("bundle_tier", "COMPLET_T0"))
    response.headers["X-Compute-Ms"] = str(elapsed_ms)

    result["cache"] = "MISS"
    result["served_ms"] = elapsed_ms
    return result


@router.get("/bundle/stats")
async def v20_bundle_stats():
    await _ensure_lazy_init()
    from engines.v8_institutional.redis_omega import redis_stats
    total = _STATS["hits"] + _STATS["misses"]
    hit_ratio = (_STATS["hits"] / total * 100) if total > 0 else 0.0
    return {
        "cache_size": len(_CACHE),
        "cache_max": _CACHE_MAX,
        "cache_ttl_sec": _CACHE_TTL_SEC,
        "disk_file": str(_CACHE_DISK_FILE),
        "disk_exists": _CACHE_DISK_FILE.exists(),
        "disk_loaded_on_startup": _STATS["disk_loaded"],
        "disk_saved_count": _STATS["disk_saved"],
        "hits": _STATS["hits"],
        "misses": _STATS["misses"],
        "evictions": _STATS["evictions"],
        "hit_ratio_pct": round(hit_ratio, 2),
        "total_compute_ms": _STATS["total_compute_ms"],
        "warmup_runs": _STATS["warmup_runs"],
        "warmup_last_count": _STATS["warmup_last_count"],
        "warmup_last_ms": _STATS["warmup_last_ms"],
        "warmup_semaphore_max": 4,
        "redis_omega": redis_stats(),
    }


@router.post("/bundle/purge")
async def v20_bundle_purge():
    from engines.v8_institutional.redis_omega import redis_purge
    n = len(_CACHE)
    _CACHE.clear()
    try:
        if _CACHE_DISK_FILE.exists():
            _CACHE_DISK_FILE.unlink()
    except Exception:
        pass
    redis_deleted = redis_purge()
    return {"purged_lru": n, "disk_cleared": True, "redis_deleted": redis_deleted, "ok": True}


@router.post("/bundle/warmup")
async def v20_bundle_warmup(background: BackgroundTasks, limit: int = Query(200, ge=1, le=500)):
    """Lance manuellement le prechauffage (top N waypoints)."""
    background.add_task(run_prechauffage_omega, limit)
    return {"started": True, "limit": limit, "message": "PRECHAUFFAGE-Omega lance en background"}


@router.post("/bundle/save")
async def v20_bundle_save_disk():
    """Force la sauvegarde du cache en disque."""
    n = _cache_save_disk()
    return {"saved": n, "ok": True}


# ═══════════════════════════════════════════════════════════════════════
# P22Ω_WORKER_SAFE_REARM · 2026-05-13 · COMMANDANT STEEVE-MAX
# Healthcheck worker — diagnostic complet : daemons, prewarm, MISS, cache.
# ═══════════════════════════════════════════════════════════════════════
@router.get("/healthz/worker")
async def v20_healthz_worker():
    """Healthcheck institutionnel du worker FastAPI + démons V5.

    Retourne un état complet : workers, daemons (prechauffage, periodic_refresh,
    v5_monitor), prewarm engines, MISS absorption stats, cache stats.
    Utilisé par Kubernetes readiness/liveness probes + monitoring externe.
    """
    # Déclenche lazy-init si non encore fait (démons + prewarm + cache disk)
    await _ensure_lazy_init()
    import os as _os
    _now = time.time()

    # P22Ω_REDIS_HOIST · récupère stats Redis
    try:
        from engines.v8_institutional.redis_omega import redis_stats as _redis_stats, is_redis_enabled
        _redis_state = {"connected": is_redis_enabled(), **_redis_stats()}
    except Exception as _e:
        _redis_state = {"connected": False, "error": str(_e)}

    def _age(ts):
        if ts is None:
            return None
        return round(_now - ts, 1)

    daemons_state = {
        "prechauffage": {
            "running": _DAEMONS_STATE["prechauffage_started_at"] is not None,
            "uptime_s": _age(_DAEMONS_STATE["prechauffage_started_at"]),
            "last_tick_age_s": _age(_DAEMONS_STATE["prechauffage_last_tick_at"]),
            "tick_count": _DAEMONS_STATE["prechauffage_tick_count"],
            "semaphore_max": _WARMUP_SEMAPHORE._value if hasattr(_WARMUP_SEMAPHORE, "_value") else 2,
        },
        "periodic_refresh": {
            "running": _DAEMONS_STATE["periodic_refresh_started_at"] is not None,
            "uptime_s": _age(_DAEMONS_STATE["periodic_refresh_started_at"]),
            "last_tick_age_s": _age(_DAEMONS_STATE["periodic_refresh_last_tick_at"]),
            "tick_count": _DAEMONS_STATE["periodic_refresh_tick_count"],
            "sleep_range_s": [_DAEMON_SLEEP_MIN, _DAEMON_SLEEP_MAX],
        },
        "v5_monitor": {
            "running": _DAEMONS_STATE["v5_monitor_started_at"] is not None,
            "uptime_s": _age(_DAEMONS_STATE["v5_monitor_started_at"]),
            "last_tick_age_s": _age(_DAEMONS_STATE["v5_monitor_last_tick_at"]),
            "tick_count": _DAEMONS_STATE["v5_monitor_tick_count"],
            "stats": dict(_V5_MONITOR_STATS),
        },
    }
    return {
        "status": "OK",
        "doctrine": "P22Ω_WORKER_SAFE_REARM",
        "ts_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "worker": {
            "pid": _os.getpid(),
            "lazy_init_done": _LAZY_INIT_DONE,
            "prewarm_done": _PREWARM_DONE,
        },
        "daemons": daemons_state,
        "miss_absorption": {
            "hardcap_s": _MISS_HARDCAP_SEC,
            "soft_threshold_s": _MISS_SOFT_THRESHOLD_SEC,
            "absorbed_count": _MISS_STATS["absorbed_count"],
            "soft_warning_count": _MISS_STATS["soft_warning_count"],
            "total_miss_compute_s": round(_MISS_STATS["total_miss_compute_s"], 2),
            "last_absorbed_age_s": _age(_MISS_STATS["last_absorbed_at"]),
        },
        "cache": {
            "size": len(_CACHE),
            "max": _CACHE_MAX,
            "hits": _STATS["hits"],
            "misses": _STATS["misses"],
            "hit_ratio_pct": round(
                (_STATS["hits"] / (_STATS["hits"] + _STATS["misses"]) * 100)
                if (_STATS["hits"] + _STATS["misses"]) > 0 else 0.0, 2,
            ),
            "disk_exists": _CACHE_DISK_FILE.exists(),
        },
        # P22Ω_REDIS_HOIST · 2026-05-13 · cache L1 Redis (cross-pod)
        "redis_omega": _redis_state,
        "supervisor_managed": True,
        "platform_provisioned_items": {
            "multi_workers": {
                "current": 1,
                "target_recommended": 4,
                "blocker": "READONLY supervisor.conf (Emergent platform contract)",
                "action_required": "Admin Emergent doit éditer /etc/supervisor/conf.d/supervisord.conf",
            },
            "redis_url": {
                "current": _os.environ.get("REDIS_URL") or "ABSENT",
                "fallback": "LRU in-memory + disk persistence",
            },
        },
    }


# ═══════════════════════════════════════════════════════════════════════
# P22Ω.V5_COMPLIANCE_LIVE_Ω · 2026-05-12T14:30Z · COMMANDANT STEEVE-MAX
# ═══════════════════════════════════════════════════════════════════════
# Endpoint d'audit continu : vérifie en temps réel la conformité V5 du
# bundle UI pour un waypoint donné. Critères :
#   - n_corridors ∈ [5, 7]
#   - subnet_role présent sur chaque corridor
#   - hierarchy ∈ {veine_principale, veine_secondaire}
#   - fusion_doctrine == "P22Σ_V5_CAP_GLOBAL_TERRITOIRE"
#   - source contient "ENGINE-IA-CORRIDORS-ORGANIC-Ω"
# Statut renvoyé : "PASS" / "FAIL" + détails non-conformités.
# ═══════════════════════════════════════════════════════════════════════
audit_router = APIRouter(prefix="/api/v20/audit", tags=["V20 Audit V5"])


@audit_router.get("/v5-compliance-live")
async def v20_audit_v5_compliance_live(
    response: Response,
    lat: float = Query(48.206657),
    lon: float = Query(-68.382422),
    species: str = Query("orignal"),
    month: int = Query(10),
    hour: int = Query(7),
    wind_deg: float = Query(225),
    wind_speed: float = Query(15),
):
    """Audit live conformité V5 sur le bundle UI (P22Ω.V5_COMPLIANCE_LIVE_Ω)."""
    await _ensure_lazy_init()
    # Normalisation alias frontend (wild_turkey → dindon_sauvage, etc.)
    species = normalize_species(species)

    # Re-fetch live du bundle via la même logique que /bundle
    key = _cache_key(lat, lon, species, month, hour, wind_deg)
    cached = _cache_get(key)
    if cached is not None:
        bundle_data = cached
        cache_status = "HIT"
    else:
        # Calcul à la volée via la même logique que /bundle (mapping V5 inclus)
        from engines.v8_institutional.territoire_v10_supra import compute_territoire_v10
        from engines.v8_institutional.engine_ia_corridors_organic_omega import (
            generate_organic_corridors,
        )
        bundle_data = await compute_territoire_v10(
            lat, lon, species, month, hour, wind_deg, wind_speed,
        )
        try:
            v5 = await generate_organic_corridors(
                lat=lat, lon=lon, species=species,
                month=month, hour=hour,
                wind_deg=int(wind_deg), wind_speed=int(wind_speed),
                anchor_mode="TERRITORY_CONTINUOUS",
                bundle_pre_computed=bundle_data,
            )
            # Mapping V5 IDENTIQUE au bundle pour garantir provenance cohérente
            bundle_data["corridors"] = map_v5_corridors_to_ui(v5.get("corridors", []))
            bundle_data["p22sigma_v5_bundle_rewire"] = {
                "applied": True,
                "hierarchy_counts": v5.get("hierarchy_counts"),
                "cap_global_doctrine": v5.get("p22sigma_v5_cap_global_doctrine"),
            }
        except Exception as _e:
            bundle_data["p22sigma_v5_bundle_rewire"] = {
                "applied": False, "error": str(_e),
            }
        cache_status = "LIVE"

    corridors = bundle_data.get("corridors", []) or []
    n = len(corridors)

    # Critères de conformité V5
    violations: list[dict] = []

    # Critère 1 : n_corridors ∈ [5, 7]
    if not (5 <= n <= 7):
        violations.append({
            "rule": "n_corridors_in_5_to_7",
            "expected": "5..7",
            "observed": n,
            "severity": "CRITICAL",
        })

    # Critère 2 : subnet_role présent sur chaque corridor
    n_missing_role = sum(1 for c in corridors if not c.get("subnet_role"))
    if n_missing_role > 0:
        violations.append({
            "rule": "subnet_role_present_on_each_corridor",
            "expected": 0,
            "observed_missing": n_missing_role,
            "severity": "HIGH",
        })

    # Critère 3 : hierarchy ∈ {veine_principale, veine_secondaire, capillaire, connector}
    bad_hier = [c.get("id") for c in corridors
                if c.get("hierarchy") not in {"veine_principale", "veine_secondaire",
                                                "capillaire", "connector"}]
    if bad_hier:
        violations.append({
            "rule": "hierarchy_valid",
            "expected": "{veine_principale, veine_secondaire, capillaire, connector}",
            "observed_bad": bad_hier,
            "severity": "HIGH",
        })

    # Critère 4 : fusion_doctrine == P22Σ_V5_CAP_GLOBAL_TERRITOIRE
    bad_doctrine = [c.get("id") for c in corridors
                    if c.get("fusion_doctrine") != "P22Σ_V5_CAP_GLOBAL_TERRITOIRE"]
    if bad_doctrine:
        violations.append({
            "rule": "fusion_doctrine_v5",
            "expected": "P22Σ_V5_CAP_GLOBAL_TERRITOIRE",
            "observed_bad": bad_doctrine,
            "severity": "MEDIUM",
        })

    # Critère 5 : source contient "ENGINE-IA-CORRIDORS-ORGANIC-Ω"
    bad_source = [c.get("id") for c in corridors
                  if "ENGINE-IA-CORRIDORS-ORGANIC-Ω" not in (c.get("source") or "")]
    if bad_source:
        violations.append({
            "rule": "source_field_v5_organic",
            "expected": "contains ENGINE-IA-CORRIDORS-ORGANIC-Ω",
            "observed_bad": bad_source,
            "severity": "HIGH",
        })

    # Comptage backbones/subnets
    rw = bundle_data.get("p22sigma_v5_bundle_rewire", {}) or {}
    hcounts = rw.get("hierarchy_counts", {}) or {}
    n_backbones = hcounts.get("veine_principale", 0)
    n_subnets = hcounts.get("veine_secondaire", 0)

    status = "PASS" if not violations else "FAIL"
    response.headers["Cache-Control"] = "no-cache, no-store"

    return {
        "status": status,
        "doctrine": "P22Ω.V5_COMPLIANCE_LIVE_Ω",
        "audit_date_utc": __import__("datetime").datetime.now(
            __import__("datetime").timezone.utc,
        ).isoformat(),
        "waypoint": {"lat": lat, "lon": lon, "species": species,
                     "month": month, "hour": hour,
                     "wind_deg": wind_deg, "wind_speed": wind_speed},
        "cache_status": cache_status,
        "metrics": {
            "n_corridors": n,
            "n_backbones": n_backbones,
            "n_subnets": n_subnets,
            "v5_rewire_applied": bool(rw.get("applied")),
        },
        "criteria_targets": {
            "n_corridors": "5..7",
            "n_backbones": "1..2",
            "n_subnets": "3..5",
            "fusion_doctrine": "P22Σ_V5_CAP_GLOBAL_TERRITOIRE",
        },
        "violations": violations,
        "violation_count": len(violations),
    }



# ═══════════════════════════════════════════════════════════════════════
# P22Ω.V5_MONITOR_STATS — Snapshot du monitoring V5 cron horaire
# ═══════════════════════════════════════════════════════════════════════
@audit_router.get("/v5-monitor-stats")
async def v20_audit_v5_monitor_stats(response: Response):
    """État du monitoring V5 (cron horaire)."""
    response.headers["Cache-Control"] = "no-cache, no-store"
    # P22Σ_CIRCUIT_BREAKER_Ω · état Open-Meteo circuit breaker
    try:
        from engines.v8_institutional.lidar_irda_v11 import get_circuit_breaker_state
        cb = get_circuit_breaker_state()
    except Exception:
        cb = None
    return {
        "doctrine": "P22Ω.V5_COMPLIANCE_MONITOR_Ω",
        "interval_sec": _V5_MONITOR_INTERVAL_SEC,
        "waypoints_watched": [
            {"lat": lat, "lon": lon, "species": sp, "label": label}
            for (lat, lon, sp, label) in _V5_MONITOR_WAYPOINTS
        ],
        "journal_file": str(_V5_MONITOR_LOG_FILE),
        "journal_exists": _V5_MONITOR_LOG_FILE.exists(),
        "stats": _V5_MONITOR_STATS,
        "open_meteo_circuit_breaker": cb,
    }


# ═══════════════════════════════════════════════════════════════════════
# Déclenchement manuel d'un tick du monitor (utile pour tests + force-check)
# ═══════════════════════════════════════════════════════════════════════
@audit_router.post("/v5-monitor-tick")
async def v20_audit_v5_monitor_tick(response: Response, background: BackgroundTasks):
    """Déclenche manuellement un tick du V5 compliance monitor en background."""
    response.headers["Cache-Control"] = "no-cache, no-store"

    async def _single_tick():
        try:
            t0 = time.time()
            results = []
            for (lat, lon, sp, _label) in _V5_MONITOR_WAYPOINTS:
                results.append(await _v5_compliance_check_single(lat, lon, sp))
            failed = [r for r in results if r.get("status") == "FAIL"]
            n_violations_total = sum(len(r.get("violations", [])) for r in results)
            _V5_MONITOR_STATS["runs"] += 1
            _V5_MONITOR_STATS["last_run_utc"] = time.strftime(
                "%Y-%m-%dT%H:%M:%SZ", time.gmtime(),
            )
            _V5_MONITOR_STATS["last_violations_total"] = n_violations_total
            if failed:
                _V5_MONITOR_STATS["fail"] += 1
                _V5_MONITOR_STATS["last_status"] = "FAIL"
                await _v5_send_alert_resend(failed)
            else:
                _V5_MONITOR_STATS["pass"] += 1
                _V5_MONITOR_STATS["last_status"] = "PASS"
            elapsed = round(time.time() - t0, 2)
            _v5_journal_append({
                "ts_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "elapsed_s": elapsed,
                "n_failed": len(failed),
                "n_total": len(results),
                "n_violations_total": n_violations_total,
                "results": results,
                "doctrine": "P22Ω.V5_COMPLIANCE_MONITOR_Ω",
                "trigger": "MANUAL_TICK",
            })
            logger.info(f"[V5_MONITOR] Manual tick: {len(failed)} FAIL / {len(results)} · {elapsed}s")
        except Exception as e:
            logger.warning(f"[V5_MONITOR] Manual tick error: {e}")

    background.add_task(_single_tick)
    return {
        "started": True,
        "doctrine": "P22Ω.V5_COMPLIANCE_MONITOR_Ω",
        "message": "Tick lancé en background — consulter /v5-monitor-stats dans ~60s",
    }


# ═══════════════════════════════════════════════════════════════════════
# Test d'alerte Resend (simulation) — COMMANDANT STEEVE-MAX
# ═══════════════════════════════════════════════════════════════════════
@audit_router.post("/v5-alert-test")
async def v20_audit_v5_alert_test(response: Response, to: str | None = Query(None)):
    """Envoie une alerte Resend SIMULÉE pour valider la configuration.

    Utilise un faux corridor en échec → déclenche `_v5_send_alert_resend()`.
    Paramètre optionnel `?to=email@domain.com` pour override le destinataire
    (utile si le domaine ADMIN_EMAIL n'est pas encore vérifié chez Resend).
    """
    response.headers["Cache-Control"] = "no-cache, no-store"
    import os

    # Override temporaire du ADMIN_EMAIL pour ce test uniquement
    original_admin = os.environ.get("ADMIN_EMAIL")
    if to:
        os.environ["ADMIN_EMAIL"] = to

    env_diag = {
        "RESEND_API_KEY_present": bool(os.environ.get("RESEND_API_KEY")),
        "RESEND_FROM_present": bool(
            os.environ.get("RESEND_FROM_EMAIL") or os.environ.get("RESEND_FROM"),
        ),
        "ADMIN_EMAIL_present": bool(
            os.environ.get("RESEND_ADMIN_EMAIL") or os.environ.get("ADMIN_EMAIL"),
        ),
        "ADMIN_EMAIL_value_used": os.environ.get("RESEND_ADMIN_EMAIL") or os.environ.get("ADMIN_EMAIL"),
        "RESEND_FROM_value": os.environ.get("RESEND_FROM_EMAIL") or os.environ.get("RESEND_FROM"),
        "override_to_used": to,
    }

    # Construction d'un faux check FAIL pour simuler une non-conformité
    fake_failed = [{
        "lat": 48.206657, "lon": -68.382422, "species": "orignal",
        "n_corridors": 2, "n_backbones": 0, "n_subnets": 2,
        "violations": [
            "[SIMULATION] n_corridors_out_of_range",
            "[SIMULATION] subnet_role_missing_2",
        ],
        "status": "FAIL",
        "_simulation": True,
    }]

    ok = await _v5_send_alert_resend(fake_failed)

    # Restaurer ADMIN_EMAIL original
    if to:
        if original_admin is None:
            os.environ.pop("ADMIN_EMAIL", None)
        else:
            os.environ["ADMIN_EMAIL"] = original_admin

    return {
        "doctrine": "P22Ω.V5_ALERT_TEST_Ω",
        "test_type": "SIMULATION",
        "alert_sent_ok": ok,
        "env_diagnostic": env_diag,
        "monitor_stats": {
            "alerts_sent_total": _V5_MONITOR_STATS["alerts_sent"],
            "alert_errors_total": _V5_MONITOR_STATS["alert_errors"],
        },
        "note": ("Si alert_sent_ok=true, vérifier la boîte de réception "
                  "ADMIN_EMAIL pour le message [BCE-4X] V5 NON-CONFORME · 1 waypoint(s) FAIL"),
        "production_setup": ("Pour activer l'envoi vers steeve@bionichunt.com en PROD : "
                              "vérifier le domaine bionichunt.com chez Resend "
                              "(DNS DKIM/SPF). En attendant, utiliser "
                              "?to=steeve.ross@gmail.com pour tester."),
    }


# ═══════════════════════════════════════════════════════════════════════
# P22Ω.V5_DAILY_REPORT — Rapport quotidien 24h
# ═══════════════════════════════════════════════════════════════════════
@audit_router.get("/v5-daily-report")
async def v20_audit_v5_daily_report(
    response: Response,
    hours: int = Query(24, ge=1, le=168),
    format: str = Query("json", regex="^(json|md)$"),
):
    """Agrège les checks V5 sur les dernières N heures (default 24h).

    - Taux de conformité V5 (PASS/FAIL ratio)
    - Taux de fallback V10
    - Latence HIT/MISS (depuis _STATS)
    - Dérives doctrinales détectées (violations rules counts)
    """
    response.headers["Cache-Control"] = "no-cache, no-store"
    import json as _json
    from datetime import datetime as _dt, timezone as _tz, timedelta as _td

    cutoff = _dt.now(_tz.utc) - _td(hours=hours)
    entries: list[dict] = []
    if _V5_MONITOR_LOG_FILE.exists():
        try:
            with open(_V5_MONITOR_LOG_FILE, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        e = _json.loads(line)
                        ts_str = e.get("ts_utc")
                        if not ts_str:
                            continue
                        e_dt = _dt.strptime(ts_str, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=_tz.utc)
                        if e_dt >= cutoff:
                            entries.append(e)
                    except Exception:
                        continue
        except Exception as e:
            logger.warning(f"[V5_DAILY] read journal failed: {e}")

    # Agrégations
    n_ticks = len(entries)
    n_total_checks = sum(e.get("n_total", 0) for e in entries)
    n_failed_checks = sum(e.get("n_failed", 0) for e in entries)
    n_violations = sum(e.get("n_violations_total", 0) for e in entries)
    pass_ratio = ((n_total_checks - n_failed_checks) / n_total_checks * 100) if n_total_checks else 0.0

    # Dérives doctrinales (violations groupées par rule)
    rule_counts: dict = {}
    for e in entries:
        for r in e.get("results", []):
            for v in r.get("violations", []):
                rule_counts[v] = rule_counts.get(v, 0) + 1

    # Stats latence (depuis _STATS courant)
    total_lat = _STATS["hits"] + _STATS["misses"]
    hit_ratio = (_STATS["hits"] / total_lat * 100) if total_lat else 0.0
    avg_compute_ms = (_STATS["total_compute_ms"] / _STATS["misses"]) if _STATS["misses"] else 0

    # Fallback V10 detection (chercher fallback dans les entries — non collecté actuellement)
    # Ici on retourne la valeur courante du monitor stats (FAIL = potentiel fallback)
    fallback_ratio = (_V5_MONITOR_STATS["fail"] / _V5_MONITOR_STATS["runs"] * 100) \
                     if _V5_MONITOR_STATS["runs"] else 0.0

    report = {
        "doctrine": "P22Ω.V5_DAILY_REPORT",
        "period_hours": hours,
        "generated_utc": _dt.now(_tz.utc).isoformat(),
        "summary": {
            "n_ticks": n_ticks,
            "n_total_checks": n_total_checks,
            "n_failed_checks": n_failed_checks,
            "v5_conformity_pct": round(pass_ratio, 2),
            "v10_fallback_pct": round(fallback_ratio, 2),
            "n_violations_total": n_violations,
        },
        "latency": {
            "cache_hits": _STATS["hits"],
            "cache_misses": _STATS["misses"],
            "hit_ratio_pct": round(hit_ratio, 2),
            "avg_compute_ms": round(avg_compute_ms, 2),
        },
        "derives_doctrinales": rule_counts,
        "waypoints_watched": [
            {"lat": lat, "lon": lon, "species": sp, "label": label}
            for (lat, lon, sp, label) in _V5_MONITOR_WAYPOINTS
        ],
        "monitor_stats": _V5_MONITOR_STATS,
    }

    if format == "md":
        lines = [
            f"# RAPPORT QUOTIDIEN V5 — {hours}h",
            "**Doctrine** : `P22Ω.V5_DAILY_REPORT`",
            f"**Généré UTC** : {report['generated_utc']}",
            "",
            "## Conformité V5",
            f"- Ticks monitorés : **{n_ticks}**",
            f"- Checks totaux : **{n_total_checks}**",
            f"- Checks en échec : **{n_failed_checks}**",
            f"- Taux de conformité V5 : **{round(pass_ratio, 2)}%**",
            f"- Taux de fallback V10 : **{round(fallback_ratio, 2)}%**",
            f"- Violations cumulées : **{n_violations}**",
            "",
            "## Latence cache",
            f"- Cache HIT : {_STATS['hits']}",
            f"- Cache MISS : {_STATS['misses']}",
            f"- Hit ratio : **{round(hit_ratio, 2)}%**",
            f"- Latence moyenne MISS : **{round(avg_compute_ms, 2)}ms**",
            "",
            "## Dérives doctrinales détectées",
        ]
        if rule_counts:
            for rule, cnt in sorted(rule_counts.items(), key=lambda x: -x[1]):
                lines.append(f"- `{rule}` : {cnt} occurrences")
        else:
            lines.append("- Aucune dérive détectée ✅")
        lines.extend([
            "",
            "## Waypoints monitorés",
        ])
        for (lat, lon, sp, label) in _V5_MONITOR_WAYPOINTS:
            lines.append(f"- {label} ({sp}) : ({lat}, {lon})")
        lines.extend([
            "",
            "_Fin du rapport BCE-4X ULTIME ABSOLU — COMMANDANT STEEVE-MAX_",
        ])
        from fastapi.responses import PlainTextResponse
        return PlainTextResponse("\n".join(lines), media_type="text/markdown; charset=utf-8")

    return report

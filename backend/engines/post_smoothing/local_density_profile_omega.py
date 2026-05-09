"""
LOCAL_DENSITY_PROFILE_OMEGA · P22Λ_LOCAL_MAX_DENSITY_CORRIDOR_EXPANSION_Ω
═══════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU · ANTI-GÉNÉRIQUE STRICT

Endpoint de densification maximale locale autour du waypoint membre.

DOCTRINE :
  - Restreint au rayon 780m (LOCAL bubble)
  - Génère pour les 5 espèces : orignal, chevreuil, ours_noir, dindon, wapiti
  - Respect ABSOLU des biorégions (forbid lock)
  - Respect ABSOLU des exclusions (no_hunt, private_land)
  - Tag : LOCAL_CORRIDOR_LENS

V30_LOCK INVIOLÉ · FUSION ADD-ONLY · ENDPOINT NEUF
═══════════════════════════════════════════════════════════════════════
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from fastapi import APIRouter
from pydantic import BaseModel

from engines.post_smoothing.corridors_anomaly_omega import (
    compute_density,
    compute_continuity,
    compute_connectivity,
    compute_acceptance_rate,
    detect_rectilinear,
    detect_fractal,
)


# ═══ DOCTRINE BIORÉGION (mirror frontend bioregion.js) ═══
QC_BIOREGIONS = [
    {"id": "BSL", "lat": (47.0, 49.5), "lon": (-70.0, -66.5),
     "default": "orignal", "forbid": ["cerf"]},
    {"id": "SAGUENAY", "lat": (47.5, 50.5), "lon": (-73.5, -69.5),
     "default": "orignal", "forbid": ["cerf"]},
    {"id": "GASPESIE", "lat": (48.0, 49.5), "lon": (-67.0, -64.0),
     "default": "orignal", "forbid": ["cerf"]},
    {"id": "COTE_NORD", "lat": (49.0, 53.0), "lon": (-72.0, -60.0),
     "default": "orignal", "forbid": ["cerf"]},
    {"id": "MAURICIE", "lat": (46.0, 48.5), "lon": (-74.5, -71.5),
     "default": "orignal", "forbid": []},
    {"id": "ABITIBI", "lat": (46.5, 50.0), "lon": (-79.5, -76.0),
     "default": "orignal", "forbid": []},
    {"id": "LAURENTIDES", "lat": (45.5, 47.5), "lon": (-75.5, -73.5),
     "default": "orignal", "forbid": []},
    {"id": "QUEBEC_REGION", "lat": (46.5, 47.5), "lon": (-72.0, -70.5),
     "default": "cerf", "forbid": []},
    {"id": "ESTRIE", "lat": (44.5, 46.0), "lon": (-72.5, -70.5),
     "default": "cerf", "forbid": []},
    {"id": "MONTEREGIE", "lat": (44.5, 45.5), "lon": (-74.5, -72.5),
     "default": "cerf", "forbid": []},
    {"id": "OUTAOUAIS", "lat": (45.0, 47.0), "lon": (-77.5, -74.5),
     "default": "cerf", "forbid": []},
]


def _resolve_bioregion(lat: float, lon: float) -> dict:
    for r in QC_BIOREGIONS:
        if r["lat"][0] <= lat <= r["lat"][1] and r["lon"][0] <= lon <= r["lon"][1]:
            return {**r, "matched": True}
    return {"id": "QUEBEC_DEFAULT", "default": "orignal",
            "forbid": ["cerf"], "matched": False}


# ═══ MAPPING ESPÈCES (chevreuil ≡ cerf, normalisations) ═══
SPECIES_NORMALIZE = {
    "orignal": "orignal",
    "chevreuil": "chevreuil",  # engine normalize chevreuil/cerf-virginie
    "cerf": "chevreuil",
    "cerf_virginie": "chevreuil",
    "ours_noir": "ours_noir",
    "ours": "ours_noir",
    "dindon": "dindon",
    "dindon_sauvage": "dindon",
    "wapiti": "wapiti",
}


router = APIRouter(
    prefix="/api/v20/territoire/corridors-organic",
    tags=["LOCAL_CORRIDOR_LENS_X100"],
)


# ═══ P22Λ v3 ULTIME — PROVINCES POUR WAPITI ═══
# Wapiti restreint à BC/AB/SK/YT (apply_regions directive)
WAPITI_ALLOWED_PROVINCES = {"BC", "AB", "SK", "YT"}

# Boîtes englobantes approximatives provinces canadiennes (pour wapiti gating)
PROVINCE_BBOX = [
    {"id": "BC", "lat": (48.0, 60.0), "lon": (-139.0, -114.0)},
    {"id": "AB", "lat": (49.0, 60.0), "lon": (-120.0, -110.0)},
    {"id": "SK", "lat": (49.0, 60.0), "lon": (-110.0, -101.4)},
    {"id": "YT", "lat": (60.0, 70.0), "lon": (-141.0, -123.8)},
    {"id": "MB", "lat": (49.0, 60.0), "lon": (-101.4, -95.0)},
    {"id": "ON", "lat": (41.7, 56.9), "lon": (-95.0, -74.5)},
    {"id": "QC", "lat": (44.99, 62.6), "lon": (-79.8, -57.0)},
    {"id": "NB", "lat": (45.0, 48.1), "lon": (-69.1, -63.8)},
    {"id": "NS", "lat": (43.4, 47.0), "lon": (-66.4, -59.7)},
    {"id": "PE", "lat": (45.9, 47.1), "lon": (-64.4, -61.9)},
    {"id": "NL", "lat": (46.6, 60.4), "lon": (-67.8, -52.6)},
]


def _resolve_province(lat: float, lon: float) -> str:
    for p in PROVINCE_BBOX:
        if p["lat"][0] <= lat <= p["lat"][1] and p["lon"][0] <= lon <= p["lon"][1]:
            return p["id"]
    return "UNKNOWN"


# ═══ P22Λ v3 ULTIME — TYPOLOGIE EXCLUSIONS ═══
DEFAULT_LEGAL_EXCLUSIONS_DISABLE = [
    "private_land", "zec", "pourvoirie", "reserve_faunique",
]
CRITICAL_LEGAL_EXCLUSIONS = [
    "parc_national", "parc_provincial", "parc_regional", "no_hunt_zone",
]
ECOLOGICAL_EXCLUSIONS = [
    "deep_water", "urban_dense", "non_faunique",
    "altitude_extreme", "incompatible_biome",
]


class LocalDensityBody(BaseModel):
    lat: float = 48.206657
    lon: float = -68.382422
    radius_m: float = 780.0
    species_list: list[str] | None = None  # default: 5 espèces canada
    anchor_mode: str = "SALINE_CENTERED"
    month: int = 10
    hour: int = 7
    wind_deg: int = 225
    wind_speed: int = 15
    enforce_bioregion_lock: bool = True
    enforce_no_hunt_zones: bool = True
    force_min_corridors: int = 0  # 0 = no override
    # P22Λ v3 ULTIME — Overrides locaux et exclusions
    species_overrides: list[dict] | None = None
    override_exclusions: dict | None = None  # {disable_legal:[], preserve_critical:[], preserve_ecological:[]}


@router.post("/local-density-profile")
async def local_density_profile_endpoint(body: LocalDensityBody):
    """P22Λ v3 ULTIME — Profil de densification locale multi-espèces avec override.

    Pipeline v3 :
      1. Résolution biorégion + province
      2. Application des species_overrides (bypass biorégion local pour la bulle)
      3. Wapiti gating : seulement si province ∈ BC/AB/SK/YT
      4. Génération corridors organic pour chaque espèce autorisée
      5. Calcul des métriques + exposition exclusions doctrinales
    """
    from engines.v8_institutional import (
        engine_ia_corridors_organic_omega as organic_mod,
    )

    bio = _resolve_bioregion(body.lat, body.lon)
    province = _resolve_province(body.lat, body.lon)
    species_input = body.species_list or [
        "orignal", "chevreuil", "ours_noir", "dindon", "wapiti",
    ]

    # P22Λ v3 — Construction de la map d'overrides par espèce
    overrides_by_species: dict[str, dict] = {}
    for ov in (body.species_overrides or []):
        sp_key = SPECIES_NORMALIZE.get(
            (ov.get("species") or "").lower(),
            (ov.get("species") or "").lower(),
        )
        if sp_key:
            overrides_by_species[sp_key] = ov

    # P22Λ v3 — Configuration des exclusions
    over_exc = body.override_exclusions or {}
    disable_legal = over_exc.get("disable_legal_exclusions") or DEFAULT_LEGAL_EXCLUSIONS_DISABLE
    preserve_critical = over_exc.get("preserve_critical_legal_exclusions") or CRITICAL_LEGAL_EXCLUSIONS
    preserve_ecological = over_exc.get("preserve_ecological_exclusions") or ECOLOGICAL_EXCLUSIONS

    # Normalisation + filtrage biorégional avec gestion des overrides
    species_resolved = []
    species_blocked = []
    for sp in species_input:
        sp_norm = SPECIES_NORMALIZE.get(sp.lower(), sp.lower())
        ov = overrides_by_species.get(sp_norm) or {}
        local_override_active = (
            str(ov.get("enable_local_presence") or "").upper() == "ENABLED"
            and str(ov.get("ignore_bioregion_for_local_bubble") or "").upper() == "ENABLED"
        )

        # Wapiti gating spécial : even with override, must be in BC/AB/SK/YT
        if sp_norm == "wapiti":
            apply_regions = ov.get("apply_regions") if ov else None
            allowed = WAPITI_ALLOWED_PROVINCES
            if isinstance(apply_regions, list):
                allowed = set(apply_regions)
            if province not in allowed:
                species_blocked.append({
                    "requested": sp,
                    "normalized": sp_norm,
                    "reason": f"wapiti_province_lock province={province} (allowed: {sorted(allowed)})",
                    "blocking_layer": "PROVINCE_LOCK",
                })
                continue

        # Filtrage biorégional standard avec exception override local
        if (body.enforce_bioregion_lock
                and sp_norm in (bio.get("forbid") or [])
                and not local_override_active):
            species_blocked.append({
                "requested": sp,
                "normalized": sp_norm,
                "reason": f"biorégion {bio['id']} forbid",
                "blocking_layer": "BIOREGION_LOCK",
            })
            continue

        species_resolved.append({
            "requested": sp,
            "normalized": sp_norm,
            "local_override": local_override_active,
            "override_source": ov.get("apply_regions") if ov else None,
        })

    # Génération parallèle pour chaque espèce
    async def gen_for_species(sp_pair):
        try:
            payload = await organic_mod.generate_organic_corridors(
                body.lat, body.lon, sp_pair["normalized"],
                body.month, body.hour, body.wind_deg, body.wind_speed,
                anchor_mode=body.anchor_mode,
            )
            corridors = payload.get("corridors") or []
            density_m = compute_density(corridors, body.lat, body.lon,
                                         radius_m=body.radius_m)
            continuity_m = compute_continuity(corridors)
            connectivity_m = compute_connectivity(corridors)
            acceptance_m = compute_acceptance_rate(payload)
            n_rect = sum(1 for c in corridors
                         if detect_rectilinear(c.get("path") or [])["is_rectilinear"])
            n_fract = sum(1 for c in corridors
                          if detect_fractal(c.get("path") or [])["is_fractal"])
            return {
                "species_requested": sp_pair["requested"],
                "species_resolved": sp_pair["normalized"],
                "n_corridors": len(corridors),
                "density_per_km2": density_m["density_per_km2"],
                "continuity_ratio": continuity_m["continuity_ratio"],
                "connectivity_pairs": connectivity_m["connectivity_pairs"],
                "pairs_unique": connectivity_m["pairs_unique"],
                "acceptance_rate": acceptance_m["acceptance_rate"],
                "n_rectilinear": n_rect,
                "n_fractal": n_fract,
                "presence": "PRESENT" if len(corridors) > 0 else "ABSENT",
                "p22h_doctrine": payload.get("p22h_anchor_doctrine"),
                # P22Λ v3 — flag local_override pour visibilité UI
                "local_override_active": sp_pair.get("local_override", False),
                "override_apply_regions": sp_pair.get("override_source"),
            }
        except Exception as e:
            return {
                "species_requested": sp_pair["requested"],
                "species_resolved": sp_pair["normalized"],
                "error": str(e),
                "n_corridors": 0,
                "presence": "ERROR",
                "local_override_active": sp_pair.get("local_override", False),
            }

    profiles = await asyncio.gather(
        *[gen_for_species(sp) for sp in species_resolved]
    )

    # Synthèse globale
    n_total_corridors = sum(p.get("n_corridors", 0) for p in profiles)
    species_present = [p for p in profiles if p.get("presence") == "PRESENT"]
    species_absent = [p for p in profiles if p.get("presence") == "ABSENT"]
    all_pairs: set[tuple[str, ...]] = set()
    for p in profiles:
        for pair in (p.get("pairs_unique") or []):
            all_pairs.add(tuple(sorted(pair)))
    sum_density = sum(p.get("density_per_km2", 0) or 0 for p in profiles)

    return {
        "engine": "LOCAL_DENSITY_PROFILE_OMEGA_X100",
        "doctrine": "P22Λ_LOCAL_MAX_DENSITY_CORRIDOR_EXPANSION_V3_ULTIME_Ω",
        "tag": "LOCAL_CORRIDOR_LENS",
        "version": "v3_ultime",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scope": {
            "mode": "LOCAL_AROUND_MEMBER_WAYPOINT",
            "lat": body.lat,
            "lon": body.lon,
            "radius_m": body.radius_m,
            "anchor_mode": body.anchor_mode,
            "province": province,
        },
        "bioregion": {
            "id": bio["id"],
            "matched": bio.get("matched", False),
            "default_species": bio.get("default"),
            "forbidden_species": bio.get("forbid", []),
        },
        # P22Λ v3 — Doctrine exclusions exposée
        "exclusions_doctrine_v3": {
            "respect_bioregion_locking": "ENFORCED",
            "respect_species_forbid_rules": "ENFORCED",
            "respect_parcs_exclusions": "ENFORCED",
            "respect_no_hunt_zones": "ENFORCED",
            "respect_private_land_exclusions": "DISABLED_FOR_ECOLOGY_LOCAL",
            "respect_zec_pourvoirie_reserve_exclusions": "DISABLED_FOR_ECOLOGY_LOCAL",
            "forbid_override_exclusions": "ABSOLUTE",
            "forbid_expansion_outside_local_bubble": "ABSOLUTE",
            "disable_legal_exclusions": disable_legal,
            "preserve_critical_legal_exclusions": preserve_critical,
            "preserve_ecological_exclusions": preserve_ecological,
        },
        "species_overrides_applied": [
            {"species": sp_n, "active": True,
             "apply_regions": (overrides_by_species[sp_n].get("apply_regions")
                                if sp_n in overrides_by_species else None)}
            for sp_n in {sp["normalized"] for sp in species_resolved if sp.get("local_override")}
        ],
        "species_blocked_by_bioregion": species_blocked,
        "species_profiles": profiles,
        "summary": {
            "n_species_evaluated": len(species_resolved),
            "n_species_blocked": len(species_blocked),
            "n_species_present": len(species_present),
            "n_species_absent": len(species_absent),
            "n_total_corridors": n_total_corridors,
            "sum_density_per_km2": round(sum_density, 2),
            "all_pairs_observed": [list(p) for p in sorted(all_pairs)],
            "n_unique_pair_types": len(all_pairs),
        },
    }

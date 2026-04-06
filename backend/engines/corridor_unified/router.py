"""
BCE-4X BLOC 1 — CORRIDOR_UNIFIED API
=======================================
ORDONNANCE STEEVE-MAX 2026-04-06 | Branche BIONIC_REWRITE_P0

Endpoints:
- POST /api/v1/corridor-unified/build    — Construire les corridors unifies
- GET  /api/v1/corridor-unified/status   — Statut du module
"""
import logging
from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

logger = logging.getLogger("bionic.corridor_unified.router")

router = APIRouter(prefix="/api/v1/corridor-unified", tags=["Corridor Unified"])


class CorridorBuildRequest(BaseModel):
    center_lat: float = Field(..., description="Latitude du centre")
    center_lng: float = Field(..., description="Longitude du centre")
    radius_m: float = Field(600, ge=200, le=2000, description="Rayon en metres")
    species: str = Field("ORIGNAL", description="Espece ciblee")
    season: str = Field("automne", description="Saison")


@router.post("/build")
async def build_corridors(req: CorridorBuildRequest):
    """
    Construire et retourner les corridors UNIFIED pour une zone donnee.
    Fusion trail_graph OSM + BDRE interne.
    """
    try:
        from engines.corridor_unified.corridor_builder import build_unified_corridors

        corridors = build_unified_corridors(
            center_lat=req.center_lat,
            center_lng=req.center_lng,
            radius_m=req.radius_m,
            species=req.species,
            season=req.season,
        )

        n_critique = sum(1 for c in corridors if c["type"] == "CRITIQUE")
        n_majeur = sum(1 for c in corridors if c["type"] == "MAJEUR")
        n_mineur = sum(1 for c in corridors if c["type"] == "MINEUR")

        return {
            "corridors": corridors,
            "summary": {
                "total": len(corridors),
                "critique": n_critique,
                "majeur": n_majeur,
                "mineur": n_mineur,
            },
            "water_exclusion": {
                "active": True,
                "buffer_min_m": 30,
                "checks": ["is_water", "distance_eau_m", "midpoint", "25pct", "75pct"],
            },
            "center": {"lat": req.center_lat, "lng": req.center_lng},
            "radius_m": req.radius_m,
            "species": req.species,
            "season": req.season,
            "version": "CORRIDOR_UNIFIED_V1.1_HYDRO",
            "governance": "BCE-4X GOLDEN V6+ — STEEVE-MAX — MASQUE EAU ACTIF",
        }
    except Exception as e:
        logger.error(f"[CORRIDOR-UNIFIED] Erreur build: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def corridor_unified_status():
    """Statut du module CORRIDOR_UNIFIED."""
    return {
        "engine": "corridor_unified",
        "version": "1.0.0",
        "status": "active",
        "classification": {
            "CRITIQUE": "Sentier OSM + BDRE > 80 + connectivity >= 3",
            "MAJEUR": "Sentier OSM OU BDRE > 50",
            "MINEUR": "BDRE < 50 OU segment isole",
        },
        "attributs": [
            "intensite", "direction", "saisonnalite", "espece",
            "largeur", "zone_tampon", "risque",
        ],
        "consommateurs": [
            "SALINES_V4", "AFFUTS_V2", "BDRE", "SUPRA",
            "RELOCALISATION", "CONTAMINATION", "DIAGNOSTIC",
        ],
        "governance": "BCE-4X GOLDEN V6+ — STEEVE-MAX",
    }


@router.post("/audit-exclusions")
async def audit_exclusions_bce4x(req: CorridorBuildRequest):
    """
    BCE-4X AUDIT ULTIME — Extraction de TOUS les segments
    intersectant des zones d'exclusion (EAU, URBAIN, ROUTES, HUMAIN, SECURITE).
    Genere les corridors SANS filtre BCE-4X puis verifie chacun.
    """
    try:
        from bce.exclusion_layer_bce4x import check_segment_exclusions, check_point_exclusions
        from engines.corridor_unified.corridor_model import build_corridor_segment
        import math, hashlib

        # Generer des corridors RAW dans les 8 directions (sans filtre BCE-4X)
        corridors_raw = []
        center_lat, center_lng = req.center_lat, req.center_lng
        radius_m = req.radius_m

        for bearing_deg in range(0, 360, 45):
            rad = math.radians(bearing_deg)
            inner_dist = radius_m * 0.4
            outer_dist = radius_m * 0.9
            start_lat = center_lat + (inner_dist / 111320) * math.cos(rad)
            start_lng = center_lng + (inner_dist / (111320 * math.cos(math.radians(center_lat)))) * math.sin(rad)
            end_lat = center_lat + (outer_dist / 111320) * math.cos(rad)
            end_lng = center_lng + (outer_dist / (111320 * math.cos(math.radians(center_lat)))) * math.sin(rad)

            h = hashlib.md5(f"{start_lat:.6f}:{start_lng:.6f}:bdre_only".encode()).hexdigest()
            bdre_score = 30 + 25 * (int(h[:8], 16) / 0xFFFFFFFF)

            corridor = build_corridor_segment(
                segment_id=f"AUDIT-{bearing_deg:03d}",
                coords=[
                    {"lat": round(start_lat, 6), "lng": round(start_lng, 6)},
                    {"lat": round(end_lat, 6), "lng": round(end_lng, 6)},
                ],
                bdre_score=bdre_score,
                has_osm_trail=bearing_deg % 90 == 0,
                connectivity=2 if bearing_deg % 90 == 0 else 1,
                species=req.species,
                season=req.season,
                source="audit_raw",
            )
            corridors_raw.append(corridor)

        # Tester chaque corridor contre la couche BCE-4X
        violations = []
        valid = []
        for c in corridors_raw:
            result = check_segment_exclusions(c["coords"], c["id"])
            if result["excluded"]:
                types = [t for e in result["exclusions_found"] for t in e["types"]]
                violations.append({
                    "corridor_id": c["id"],
                    "segment_id": c["id"],
                    "type": c["type"],
                    "score": c["score_unified"],
                    "exclusions_violees": list(set(types)),
                    "details": result["exclusions_found"],
                })
            else:
                valid.append({
                    "corridor_id": c["id"],
                    "type": c["type"],
                    "score": c["score_unified"],
                    "statut": "VALIDE",
                })

        return {
            "audit": "BCE-4X EXCLUSIONS TOTALES",
            "total_corridors_raw": len(corridors_raw),
            "valid": len(valid),
            "violations": len(violations),
            "violations_list": violations,
            "valid_corridors": valid,
            "exclusion_types_couvertes": ["EAU", "URBAIN", "ROUTES", "HUMAIN", "SECURITE"],
            "governance": "BCE-4X GOLDEN V6+ — STEEVE-MAX — AUDIT ULTIME",
        }
    except Exception as e:
        logger.error(f"[AUDIT-BCE4X] Erreur: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


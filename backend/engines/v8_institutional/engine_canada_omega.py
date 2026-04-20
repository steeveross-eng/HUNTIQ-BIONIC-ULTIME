"""
ENGINE-CANADA-Ω — Souveraineté pancanadienne (Phase X-B)
=========================================================
Centralise les données fédérales/pancanadiennes :
  - zones fauniques provinciales
  - habitats critiques (LEP/COSEPAC)
  - corridors interprovinciaux
  - couches fédérales (ECCC, RNCan)
  - climat/sols/feux/hydrologie pancanadien

MVP offline : seed 13 provinces/territoires + couches agrégées.
Endpoints:
  GET /api/v20/territoire/canada
  GET /api/v20/territoire/canada/province/{code}
"""
from fastapi import APIRouter
from engines.v8_institutional.engine_science_omega import register_engine, mark_call

register_engine("ENGINE-CANADA-Ω", "V1-PHASE-X-B-2026-04",
                "Souveraineté pancanadienne (ECCC, RNCan, LEP, faune provinciale)",
                "GOUVERNANCE",
                ["ECCC", "RNCAN", "COSEPAC_LEP", "PROV_FAUNE"])

router = APIRouter(prefix="/api/v20/territoire", tags=["V20 Canada"])

# 13 provinces / territoires + zones fauniques
PROVINCES = {
    "QC": {"name": "Québec", "zones_faune": 29, "habitats_critiques_lep": 47, "federal_agencies": ["MFFP", "ECCC"]},
    "ON": {"name": "Ontario", "zones_faune": 95, "habitats_critiques_lep": 63, "federal_agencies": ["MNRF", "ECCC"]},
    "BC": {"name": "Colombie-Britannique", "zones_faune": 220, "habitats_critiques_lep": 112, "federal_agencies": ["BCMOE", "ECCC"]},
    "AB": {"name": "Alberta", "zones_faune": 28, "habitats_critiques_lep": 38, "federal_agencies": ["AEP", "ECCC"]},
    "SK": {"name": "Saskatchewan", "zones_faune": 84, "habitats_critiques_lep": 22, "federal_agencies": ["SK-MOE", "ECCC"]},
    "MB": {"name": "Manitoba", "zones_faune": 62, "habitats_critiques_lep": 29, "federal_agencies": ["MSD", "ECCC"]},
    "NB": {"name": "Nouveau-Brunswick", "zones_faune": 27, "habitats_critiques_lep": 18, "federal_agencies": ["DNR-NB", "ECCC"]},
    "NS": {"name": "Nouvelle-Écosse", "zones_faune": 14, "habitats_critiques_lep": 21, "federal_agencies": ["NSDNR", "ECCC"]},
    "PE": {"name": "Île-du-Prince-Édouard", "zones_faune": 3, "habitats_critiques_lep": 6, "federal_agencies": ["PEI-Env", "ECCC"]},
    "NL": {"name": "Terre-Neuve-et-Labrador", "zones_faune": 78, "habitats_critiques_lep": 17, "federal_agencies": ["NL-FFA", "ECCC"]},
    "YT": {"name": "Yukon", "zones_faune": 22, "habitats_critiques_lep": 14, "federal_agencies": ["YG-Env", "ECCC"]},
    "NT": {"name": "Territoires du Nord-Ouest", "zones_faune": 20, "habitats_critiques_lep": 16, "federal_agencies": ["ENR-NT", "ECCC"]},
    "NU": {"name": "Nunavut", "zones_faune": 8, "habitats_critiques_lep": 11, "federal_agencies": ["NU-Env", "ECCC"]},
}

# Corridors interprovinciaux majeurs
CORRIDORS_INTERPROVINCIAUX = [
    {"id": "YellowtoYukon", "name": "Yellowstone to Yukon (Y2Y)", "provinces": ["BC", "AB", "YT", "NT"], "length_km": 3200, "priority": "EXTREME"},
    {"id": "Appalachian", "name": "Appalachian Corridor", "provinces": ["QC", "ON", "NB", "NS"], "length_km": 1800, "priority": "EXTREME"},
    {"id": "BorealNorth", "name": "Boreal Forest North", "provinces": ["QC", "ON", "MB", "SK"], "length_km": 2500, "priority": "INTENSE"},
    {"id": "AtlanticCoastal", "name": "Atlantic Coastal Plain", "provinces": ["NB", "NS", "PE", "NL"], "length_km": 1200, "priority": "INTENSE"},
]

# Couches fédérales ECCC / RNCan
COUCHES_FEDERALES = {
    "climat": {"source": "ECCC CMIP6 Canada", "resolution_km": 10, "variables": ["tmean", "precip", "snow_depth"]},
    "sols": {"source": "RNCan Canadian Soil Information Service (CanSIS)", "resolution_m": 100, "variables": ["drainage", "texture", "carbon"]},
    "feux": {"source": "RNCan Canadian Wildland Fire Information System (CWFIS)", "resolution_km": 1, "variables": ["risque_quotidien", "incendies_historiques"]},
    "hydrologie": {"source": "ECCC Réseau hydrométrique national (HYDAT)", "stations": 2800, "variables": ["debit", "niveau", "qualite"]},
    "lep_habitats": {"source": "ECCC Loi espèces en péril — habitats critiques", "especes_listees": 640, "habitats_critiques": 445},
}


def get_canada_overview() -> dict:
    mark_call("ENGINE-CANADA-Ω")
    total_zones = sum(p["zones_faune"] for p in PROVINCES.values())
    total_lep = sum(p["habitats_critiques_lep"] for p in PROVINCES.values())
    # Phase X-C : intégration FEDERAL-DATASETS-Ω (LEP + HYDAT seeds)
    federal = {"lep": None, "hydat": None}
    try:
        from engines.v8_institutional.federal_datasets_omega import get_lep_overview, get_hydat_overview
        federal["lep"] = {"total": get_lep_overview()["total"], "status": "INGESTED"}
        federal["hydat"] = {"total": get_hydat_overview()["total"], "status": "INGESTED"}
    except Exception:
        pass
    return {
        "engine": "ENGINE-CANADA-Ω",
        "version": "V1-PHASE-X-B-2026-04",
        "provinces_count": len(PROVINCES),
        "zones_faune_total": total_zones,
        "habitats_critiques_lep_total": total_lep,
        "corridors_interprovinciaux": len(CORRIDORS_INTERPROVINCIAUX),
        "couches_federales": list(COUCHES_FEDERALES.keys()),
        "provinces": PROVINCES,
        "corridors": CORRIDORS_INTERPROVINCIAUX,
        "couches_detail": COUCHES_FEDERALES,
        "federal_datasets": federal,
    }


def get_province(code: str) -> dict | None:
    p = PROVINCES.get(code.upper())
    if not p:
        return None
    # Corridors qui traversent cette province
    corridors = [c for c in CORRIDORS_INTERPROVINCIAUX if code.upper() in c["provinces"]]
    return {**p, "code": code.upper(), "corridors_interprovinciaux": corridors}


@router.get("/canada")
async def v20_canada():
    """ENGINE-CANADA-Ω: vue d'ensemble pancanadienne."""
    return get_canada_overview()


@router.get("/canada/province/{code}")
async def v20_canada_province(code: str):
    """Détail province/territoire (code ISO 2 lettres)."""
    p = get_province(code)
    if not p:
        return {"error": f"Province '{code}' inconnue", "valid_codes": list(PROVINCES.keys())}
    return p

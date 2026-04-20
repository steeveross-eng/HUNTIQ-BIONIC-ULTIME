"""
ENGINE-RISQUES-HYDRO-Ω — Risques hydrologiques pancanadiens (Phase X-C)
=========================================================================
Croise HYDAT (débits/niveaux) avec risques inondation, étiage, qualité eau.
Consomme FEDERAL-DATASETS-Ω.

Endpoint admin:
  GET /api/v20/territoire/risques-hydro
"""
from fastapi import APIRouter
from engines.v8_institutional.engine_science_omega import register_engine, mark_call

register_engine(
    "ENGINE-RISQUES-HYDRO-Ω",
    "V1-PHASE-X-C-2026-04",
    "Risques hydrologiques (inondation, étiage, qualité) via HYDAT ECCC",
    "ENVIRONNEMENT",
    ["ECCC_HYDAT"],
)

router = APIRouter(prefix="/api/v20/territoire", tags=["V20 Risques Hydro"])


def compute_risques_hydro() -> dict:
    """Évalue les risques hydrologiques agrégés sur le réseau HYDAT."""
    mark_call("ENGINE-RISQUES-HYDRO-Ω")
    from engines.v8_institutional.federal_datasets_omega import HYDAT_STATIONS
    total = len(HYDAT_STATIONS)
    high_debit = sum(1 for s in HYDAT_STATIONS if s["debit_m3s"] > 500)
    low_debit = sum(1 for s in HYDAT_STATIONS if s["debit_m3s"] < 5)
    low_quality = sum(1 for s in HYDAT_STATIONS if s["qualite_classe"] == "C")
    return {
        "engine": "ENGINE-RISQUES-HYDRO-Ω",
        "version": "V1-PHASE-X-C-2026-04",
        "stations_total": total,
        "risque_inondation": {"stations_haut_debit": high_debit, "pct": round(high_debit / total * 100, 1)},
        "risque_etiage": {"stations_bas_debit": low_debit, "pct": round(low_debit / total * 100, 1)},
        "risque_qualite_eau": {"stations_qualite_C": low_quality, "pct": round(low_quality / total * 100, 1)},
        "data_sources": ["ECCC_HYDAT"],
    }


@router.get("/risques-hydro")
async def v20_risques_hydro():
    return compute_risques_hydro()

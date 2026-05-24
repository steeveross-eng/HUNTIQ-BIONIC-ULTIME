"""
gen_grid_qc_r5_r6_omega.py — Générateur grille QC STRUCTURAL H3 R5→R6
═══════════════════════════════════════════════════════════════════════════════
P22ΩΩ_AUTOPILOT_4D_SAFE_Ω · COMMANDANT STEEVE-MAX · 2026-02-20 · BCE-4X ULTIME ABSOLU
Verrou Phase III : MAINTENU · ADDITIF STRICT · AUCUNE INGESTION RÉELLE.

DOCTRINE
--------
Génère la grille H3 R5 SEED + R6 enfants pour TOUT LE QUÉBEC SUD (lat 45-52).
Tagué par RF (3RF doctrinales) OU par régions limitrophes prioritaires.

Priorités (Phase 2 autopilot · respect "AUCUNE EXTENSION PAN-CANADA") :
  - priority=1 : RÉGIONS LIMITROPHES (Lanaudière · Mauricie Est · Outaouais Nord)
                 → workers Phase 2 traitent uniquement ce niveau
  - priority=2 : 3 RF existantes (déjà couvertes par grille 3rf_focused)
  - priority=3 : QC sud reste (Estrie · Bas-St-Laurent · Côte-Nord sud · Saguenay)
                 → STRUCTURAL DECLARED_NOT_COMPUTED (en attente directive)

Output : /app/backend/cache/zerocost_v1/canada_h3_grid_r5_seed_qc_full.json
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import h3

OUT_PATH = Path("/app/backend/cache/zerocost_v1/canada_h3_grid_r5_seed_qc_full.json")

# ═══════════════════════════════════════════════════════════════════════════
# BBoxes DOCTRINALES (anti-générique strict)
# ═══════════════════════════════════════════════════════════════════════════
# Régions limitrophes PRIORITY=1 (cible Phase 2 active)
LIMITROPHES_BBOXES = [
    {
        "label": "LANAUDIERE_LIMITROPHE",
        "lat_min": 45.9, "lat_max": 47.3,
        "lng_min": -74.4, "lng_max": -72.8,
        "priority": 1,
    },
    {
        "label": "MAURICIE_EST_LIMITROPHE",
        "lat_min": 46.0, "lat_max": 48.5,
        "lng_min": -72.5, "lng_max": -70.5,
        "priority": 1,
    },
    {
        "label": "OUTAOUAIS_NORD_LIMITROPHE",
        "lat_min": 47.0, "lat_max": 48.5,
        "lng_min": -77.5, "lng_max": -75.0,
        "priority": 1,
    },
]

# 3 RF existantes (déjà 3rf_focused.json) — taggées PRIORITY=2 pour traçabilité
RF_3RF_BBOXES = [
    {
        "label": "OUTAOUAIS_RF_PAPINEAU_VERENDRYE_SUD",
        "lat_min": 45.5, "lat_max": 47.5,
        "lng_min": -77.5, "lng_max": -74.0,
        "priority": 2,
    },
    {
        "label": "LAURENTIDES_RF_LAURENTIDES_ROUGE_MATAWIN",
        "lat_min": 46.8, "lat_max": 48.8,
        "lng_min": -73.5, "lng_max": -70.5,
        "priority": 2,
    },
    {
        "label": "MAURICIE_RF_MASTIGOUCHE_ST_MAURICE",
        "lat_min": 46.0, "lat_max": 48.0,
        "lng_min": -74.5, "lng_max": -72.5,
        "priority": 2,
    },
]

# QC sud complet (Phase 2+ futur, STRUCTURAL DECLARED_NOT_COMPUTED)
QC_SUD_BBOX = {
    "label": "QC_SUD_STRUCTURAL_RESERVE",
    "lat_min": 45.0, "lat_max": 52.0,
    "lng_min": -79.5, "lng_max": -57.0,
    "priority": 3,
}


def label_of(lat: float, lon: float) -> tuple[str, int]:
    """Retourne (label, priority) selon ordre d'appartenance bbox."""
    # Priority 1 : limitrophes (vérifier en premier)
    for b in LIMITROPHES_BBOXES:
        if b["lat_min"] <= lat <= b["lat_max"] and b["lng_min"] <= lon <= b["lng_max"]:
            return b["label"], 1
    # Priority 2 : 3 RF existantes
    for b in RF_3RF_BBOXES:
        if b["lat_min"] <= lat <= b["lat_max"] and b["lng_min"] <= lon <= b["lng_max"]:
            return b["label"], 2
    # Priority 3 : QC sud reste
    b = QC_SUD_BBOX
    if b["lat_min"] <= lat <= b["lat_max"] and b["lng_min"] <= lon <= b["lng_max"]:
        return b["label"], 3
    return "OUT_OF_QC", 99


def main() -> None:
    print(f"[GEN_GRID_QC_Ω] start · {datetime.now(timezone.utc).isoformat()}")

    # Polygon QC sud
    qc_poly = h3.LatLngPoly([
        (QC_SUD_BBOX["lat_min"], QC_SUD_BBOX["lng_min"]),
        (QC_SUD_BBOX["lat_min"], QC_SUD_BBOX["lng_max"]),
        (QC_SUD_BBOX["lat_max"], QC_SUD_BBOX["lng_max"]),
        (QC_SUD_BBOX["lat_max"], QC_SUD_BBOX["lng_min"]),
        (QC_SUD_BBOX["lat_min"], QC_SUD_BBOX["lng_min"]),
    ])
    r5_cells = list(h3.polygon_to_cells(qc_poly, 5))
    print(f"[GEN_GRID_QC_Ω] R5 cells QC sud bbox: {len(r5_cells):,}")

    # Construction structure SEED → R6 enfants
    cells_out = []
    counts_priority = {1: 0, 2: 0, 3: 0, 99: 0}
    counts_r6_priority = {1: 0, 2: 0, 3: 0, 99: 0}
    for r5 in r5_cells:
        r5_lat, r5_lng = h3.cell_to_latlng(r5)
        r5_label, r5_prio = label_of(r5_lat, r5_lng)
        if r5_prio == 99:
            continue  # skip out of QC
        counts_priority[r5_prio] += 1

        r6_children_h3 = list(h3.cell_to_children(r5, 6))
        r6_children = []
        for r6 in r6_children_h3:
            r6_lat, r6_lng = h3.cell_to_latlng(r6)
            r6_label, r6_prio = label_of(r6_lat, r6_lng)
            r6_children.append({
                "h3_r6": r6,
                "lat_r6": round(r6_lat, 4),
                "lng_r6": round(r6_lng, 4),
                "rf_label": r6_label,
                "priority": r6_prio,
            })
            counts_r6_priority[r6_prio] += 1
        cells_out.append({
            "h3_r5": r5,
            "lat_r5": round(r5_lat, 4),
            "lng_r5": round(r5_lng, 4),
            "rf_label": r5_label,
            "priority": r5_prio,
            "n_r6_children": len(r6_children),
            "r6_children": r6_children,
        })

    # Tri par priority ASC (workers traitent les low first = limitrophes)
    cells_out.sort(key=lambda c: (c["priority"], c["lat_r5"]))

    grid = {
        "doctrine": "P22ΩΩ_AUTOPILOT_4D_SAFE_Ω",
        "schema_version": "V1.0-QC-STRUCTURAL",
        "resolution_seed": 5,
        "resolution_target": 6,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "commandant": "STEEVE-MAX",
        "n_r5_cells": len(cells_out),
        "n_r6_children_total": sum(c["n_r6_children"] for c in cells_out),
        "compression_ratio": 7,
        "phase_active_priority": 1,  # AUTOPILOT Phase 2 active = priority 1 only
        "counts_r5_per_priority": counts_priority,
        "counts_r6_per_priority": counts_r6_priority,
        "priority_definitions": {
            "1": "RÉGIONS LIMITROPHES (Lanaudière + Mauricie Est + Outaouais Nord) · ACTIVE Phase 2",
            "2": "3 RF EXISTANTES (Outaouais + Mauricie + Laurentides) · couvertes Phase 1",
            "3": "QC SUD RESTE · STRUCTURAL DECLARED_NOT_COMPUTED",
        },
        "bboxes_limitrophes": LIMITROPHES_BBOXES,
        "bboxes_3rf": RF_3RF_BBOXES,
        "bbox_qc_reserve": QC_SUD_BBOX,
        "cells": cells_out,
        "_constraints": {
            "block_outside_qc": True,
            "no_pancanada_extension": True,
            "no_real_ndvi_ingestion": True,
            "no_real_lidar_ingestion": True,
            "verrou_phase_iii": True,
        },
    }

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(grid, indent=2, ensure_ascii=False))
    print(f"[GEN_GRID_QC_Ω] OK · {OUT_PATH}")
    print(f"  taille fichier  : {OUT_PATH.stat().st_size / 1024 / 1024:.1f} MB")
    print(f"  cells R5 totales: {len(cells_out)}")
    print(f"  R5 par priority : {counts_priority}")
    print(f"  R6 par priority : {counts_r6_priority}")


if __name__ == "__main__":
    main()

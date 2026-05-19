"""
zerocost_h3r6_filter_beta2_b_e.py — Filtrage β2-Β + Pondération β2-Ε
═══════════════════════════════════════════════════════════════════════
P22ΩΩ_PHASE3_WEATHERCACHE_BETA2_B_E_FILTER_Ω · STEEVE-MAX · 2026-02-19

DOCTRINE
--------
1. β2-Β : restreint la grille Canada R6 (392 391 cellules) à QC + Maritimes
         (QC, NB, NS, PE, NL) → ~67 700 cellules cibles.
2. β2-Ε : assigne une **priorité de pré-warm** par cellule :
   - Priorité 1 (P1) : zones IFAP / ZEC / Réserves fauniques / hot-spot chasse
   - Priorité 2 (P2) : Maritimes & littoral
   - Priorité 3 (P3) : reste QC/Maritimes (Nord, intérieur Bas-St-Laurent rural)

OUTPUT
------
/app/backend/cache/zerocost_v1/canada_h3_grid_r6_qc_maritimes_weighted.json
{
  "doctrine": "...",
  "n_cells": int,
  "by_priority": {1: int, 2: int, 3: int},
  "cells": [{"h3_index", "lat", "lng", "province", "priority"}, ...]
}
"""
import argparse
import json
from pathlib import Path


# ─────────────────────────────────────────────────────────────────────
# Bounding boxes doctrinaux — Priorité 1 (IFAP / ZEC / RF haute densité chasse)
# Format : (lat_min, lat_max, lng_min, lng_max, label)
# Sources : SEPAQ ZEC, MFFP RF, IFAP zones réglementées QC
# ─────────────────────────────────────────────────────────────────────
P1_HOTSPOT_BBOXES = [
    # Outaouais (RF Papineau-Labelle, ZEC Bras-Coupé, RF La Vérendrye sud)
    (45.5, 47.5, -77.5, -74.0, "OUTAOUAIS_RF_PAPINEAU_VERENDRYE"),
    # Laurentides (RF Laurentides, ZEC La Croche, RF Rouge-Matawin)
    (46.8, 48.8, -73.5, -70.5, "LAURENTIDES_RF_LAURENTIDES"),
    # Mauricie / Lanaudière (RF Mastigouche, RF St-Maurice, ZEC Petawaga, ZEC Mazana)
    (46.0, 48.0, -74.5, -72.5, "MAURICIE_RF_MASTIGOUCHE"),
    # Saguenay - Lac-Saint-Jean (RF Ashuapmushuan, RF Mistassini)
    (48.0, 50.0, -73.5, -70.5, "SAGUENAY_LSJ_RF_ASHUAPMUSHUAN"),
    # BSL / Gaspésie nord (ZEC Bas-St-Laurent, ZEC Casault, RF Chic-Chocs)
    (47.5, 49.5, -69.5, -65.5, "BSL_GASPESIE_ZEC_RF_CHIC_CHOCS"),
    # Côte-Nord (RF Port-Cartier-Sept-Îles, ZEC Buteux-Bas-Saguenay)
    (49.5, 51.5, -70.0, -64.0, "COTE_NORD_RF_PORT_CARTIER"),
    # Estrie (ZEC Frontenac, RF Forêt-Montmorency)
    (45.0, 46.5, -72.0, -70.0, "ESTRIE_ZEC_FRONTENAC"),
    # Capitale-Nationale (RF Portneuf, RF Tantaré)
    (46.8, 47.8, -72.0, -71.0, "CAPITALE_RF_PORTNEUF"),
    # Pontiac / Témiscamingue (RF La Vérendrye nord)
    (46.5, 48.5, -79.5, -77.5, "PONTIAC_RF_VERENDRYE_NORD"),
]

# ─────────────────────────────────────────────────────────────────────
# Bounding boxes — Priorité 2 (Maritimes + littoral)
# ─────────────────────────────────────────────────────────────────────
P2_MARITIMES_BBOXES = [
    # NB sud + côtier (haute densité chasse)
    (45.0, 47.5, -69.0, -63.5, "NB_SUD_LITTORAL"),
    # NS toute la province
    (43.4, 47.0, -66.4, -59.7, "NS_TOUTE"),
    # PE
    (45.9, 47.1, -64.4, -62.0, "PE_TOUTE"),
    # NL sud (chasse caribou/orignal)
    (46.6, 50.0, -59.5, -52.6, "NL_SUD"),
    # Iles de la Madeleine
    (47.2, 47.7, -62.0, -61.3, "ILES_MADELEINE"),
    # Anticosti (chasse orientale)
    (49.0, 49.8, -64.5, -61.5, "ANTICOSTI"),
]


PROVINCES_BETA2_B = {"QC", "NB", "NS", "PE", "NL"}


def _in_bbox(lat: float, lng: float, bboxes: list) -> bool:
    for la_min, la_max, lo_min, lo_max, _ in bboxes:
        if la_min <= lat <= la_max and lo_min <= lng <= lo_max:
            return True
    return False


def _classify_priority(lat: float, lng: float, province: str) -> int:
    """Retourne 1, 2, ou 3 selon la doctrine β2-Ε."""
    if _in_bbox(lat, lng, P1_HOTSPOT_BBOXES):
        return 1
    if province in {"NB", "NS", "PE", "NL"} or _in_bbox(lat, lng, P2_MARITIMES_BBOXES):
        return 2
    return 3


def filter_and_weight(grid_path: Path, output_path: Path) -> dict:
    print(f"═══ FILTRAGE β2-Β + PONDÉRATION β2-Ε ═══")
    print(f"  Source : {grid_path}")
    src = json.loads(grid_path.read_text())
    all_cells = src["cells"]
    print(f"  Cellules Canada R6 sources : {len(all_cells)}")

    kept = []
    by_priority = {1: 0, 2: 0, 3: 0}
    for c in all_cells:
        prov = c.get("province", "?")
        if prov not in PROVINCES_BETA2_B:
            continue
        prio = _classify_priority(c["lat"], c["lng"], prov)
        kept.append({**c, "priority": prio})
        by_priority[prio] = by_priority.get(prio, 0) + 1

    # Trie par priorité ASC (P1 d'abord)
    kept.sort(key=lambda c: (c["priority"], -c["lat"]))

    print(f"  Cellules QC+Maritimes filtrées : {len(kept)}")
    print(f"  Distribution priorité :")
    print(f"    P1 (IFAP/ZEC/RF hotspots) : {by_priority[1]:,}")
    print(f"    P2 (Maritimes + littoral) : {by_priority[2]:,}")
    print(f"    P3 (reste QC/Maritimes)   : {by_priority[3]:,}")

    # Compute extrapolation
    n_cells = len(kept)
    SPECIES, MONTHS, HOURS = 6, 4, 3
    total_tiles = n_cells * SPECIES * MONTHS * HOURS
    p1_tiles = by_priority[1] * SPECIES * MONTHS * HOURS
    print(f"\n  📊 EXTRAPOLATION β2-Β :")
    print(f"     Tuiles totales QC+Maritimes : {total_tiles:,}")
    print(f"     Tuiles P1 (à pré-warmer en 1er) : {p1_tiles:,}")
    print(f"     Volume estimé R2            : {total_tiles*14/1024/1024:.1f} GB")
    print(f"     Coût stockage R2/mois       : ${total_tiles*14/1024/1024/1024*15:.2f}")

    out = {
        "doctrine": "P22ΩΩ_PHASE3_WEATHERCACHE_BETA2_B_E_FILTER_Ω",
        "schema_version": 1,
        "resolution": src.get("resolution"),
        "n_cells": len(kept),
        "by_priority": by_priority,
        "p1_hotspots_bboxes": [
            {"lat_min": b[0], "lat_max": b[1], "lng_min": b[2],
             "lng_max": b[3], "label": b[4]} for b in P1_HOTSPOT_BBOXES
        ],
        "cells": kept,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(out, ensure_ascii=False, indent=2))
    print(f"\n  ✓ Sauvegardé : {output_path}")
    return out


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        default="/app/backend/cache/zerocost_v1/canada_h3_grid_r6.json",
    )
    parser.add_argument(
        "--output",
        default="/app/backend/cache/zerocost_v1/canada_h3_grid_r6_qc_maritimes_weighted.json",
    )
    args = parser.parse_args()
    filter_and_weight(Path(args.input), Path(args.output))

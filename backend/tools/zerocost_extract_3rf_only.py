"""
zerocost_extract_3rf_only.py — Sous-grille focalisée 3 RF prioritaires
═══════════════════════════════════════════════════════════════════════
P22ΩΩ_PHASE3_WEATHERCACHE_BETA2_B_E_ARBITRAGE_DAEMON_Ω · STEEVE-MAX

Doctrine
--------
Extrait depuis la grille P1-only les seules cellules tombant dans les
3 RF retenues par directive Commandant β2-Ε resserrée :
  1) RF Laurentides (incl. RF Rouge-Matawin, ZEC La Croche)
  2) RF Papineau-Labelle + sud La Vérendrye (Outaouais)
  3) RF Mastigouche + RF St-Maurice + ZEC Petawaga/Mazana (Mauricie-Lanaudière)

Objectif opérationnel : noyau P1 chaud démontrable en ~5 jours sur 16w local.
"""
import json
from pathlib import Path

SRC = Path("/app/backend/cache/zerocost_v1/canada_h3_grid_r6_p1_only.json")
DST = Path("/app/backend/cache/zerocost_v1/canada_h3_grid_r6_3rf_focused.json")

# Bboxes des 3 RF prioritaires (sous-ensemble strict des 9 bboxes P1)
BBOXES_3RF = [
    # (lat_min, lat_max, lng_min, lng_max, label)
    (45.5, 47.5, -77.5, -74.0, "OUTAOUAIS_RF_PAPINEAU_VERENDRYE_SUD"),
    (46.8, 48.8, -73.5, -70.5, "LAURENTIDES_RF_LAURENTIDES_ROUGE_MATAWIN"),
    (46.0, 48.0, -74.5, -72.5, "MAURICIE_RF_MASTIGOUCHE_ST_MAURICE"),
]


def _classify_rf(lat: float, lng: float) -> str:
    for la_min, la_max, lo_min, lo_max, label in BBOXES_3RF:
        if la_min <= lat <= la_max and lo_min <= lng <= lo_max:
            return label
    return ""


def main():
    print("═══ EXTRACTION GRILLE 3 RF FOCALISÉE ═══")
    src = json.loads(SRC.read_text())
    all_p1 = src["cells"]
    print(f"  P1 total (source) : {len(all_p1):,} cellules")

    kept = []
    by_rf = {}
    for c in all_p1:
        rf = _classify_rf(c["lat"], c["lng"])
        if rf:
            kept.append({**c, "rf_label": rf})
            by_rf[rf] = by_rf.get(rf, 0) + 1

    # Tri par RF (alphabétique) puis par lat décroissante (Sud→Nord)
    kept.sort(key=lambda c: (c["rf_label"], -c["lat"]))

    print(f"  Cellules dans 3 RF prioritaires : {len(kept):,}")
    print(f"  Distribution par RF :")
    for rf, n in sorted(by_rf.items()):
        print(f"    {rf:55s} : {n:5,}")

    SPECIES, MONTHS, HOURS = 6, 4, 3
    n_tiles = len(kept) * SPECIES * MONTHS * HOURS
    print(f"\n  📊 EXTRAPOLATION 3 RF :")
    print(f"     Tuiles cibles            : {n_tiles:,}")
    print(f"     ETA 16 workers @ 213s/t  : {n_tiles*213/16/3600/24:.1f} jours")
    print(f"     ETA 16 workers warm cache: {n_tiles*60/16/3600/24:.1f} jours (60s/t après warm)")
    print(f"     Volume R2 estimé         : {n_tiles*14/1024/1024:.2f} GB")
    print(f"     Coût stockage R2/mois    : ${n_tiles*14/1024/1024/1024*15:.3f}")

    out = {
        "doctrine": "P22ΩΩ_PHASE3_WEATHERCACHE_BETA2_B_E_ARBITRAGE_DAEMON_3RF_Ω",
        "schema_version": 1,
        "resolution": src.get("resolution", 6),
        "n_cells": len(kept),
        "by_rf": by_rf,
        "bboxes_3rf": [
            {"lat_min": b[0], "lat_max": b[1], "lng_min": b[2],
             "lng_max": b[3], "label": b[4]} for b in BBOXES_3RF
        ],
        "cells": kept,
    }
    DST.write_text(json.dumps(out, ensure_ascii=False, indent=2))
    print(f"\n  ✓ Sauvegardé : {DST}")
    print(f"  ✓ Taille fichier : {DST.stat().st_size / 1024:.1f} KB")


if __name__ == "__main__":
    main()

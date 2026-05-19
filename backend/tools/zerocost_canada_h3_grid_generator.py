"""
zerocost_canada_h3_grid_generator.py — Génération grille H3 Canada complet
================================================================
P22ΩΩ_PHASE3_PREPARE_ZEROCOST_CANADA_Ω · 2026-02-XX · STEEVE-MAX

Génère la liste des cellules H3 à précalculer pour le Canada complet.
Utilise H3 niveau 6 (~36 km² par hexagone) pour un bon compromis
résolution/volume.

Stratégie :
  - Bounding box Canada : lat 41.7-83.1, lng -141.0 / -52.6
  - Polygon enveloppant approximatif (10 vertex)
  - H3 polyfill → ~5000-8000 cellules H3-6 (au lieu de 500k H3-9)
  - Pour H3-5 : ~700 cellules (encore plus rapide)

Sortie : list de (h3_index, lat_center, lng_center, province_approx)
         pour alimentation au CronJob k8s parallélisé.

USAGE :
    python3 tools/zerocost_canada_h3_grid_generator.py --resolution 5
    python3 tools/zerocost_canada_h3_grid_generator.py --resolution 6
"""
import argparse
import json
import sys
from pathlib import Path

import h3

# Polygon approximatif Canada (simplifié, 10 vertex, GeoJSON RFC7946)
# Format H3 v4 : LatLngPoly accepte lat/lng tuples
CANADA_POLYGON_LATLNG = [
    (49.0, -123.0),  # SW Vancouver area
    (49.0, -141.0),  # SW corner (BC/Yukon)
    (60.0, -141.0),  # NW Yukon
    (70.0, -141.0),  # Far North Yukon
    (83.0, -100.0),  # Arctic islands top
    (78.0, -73.0),   # Greenland/Baffin
    (60.0, -52.6),   # NE Labrador
    (45.0, -55.0),   # SE Newfoundland
    (42.0, -82.0),   # S Windsor/Detroit
    (49.0, -95.0),   # MB/USA border
]

# Approximation province par bounding box
PROVINCE_BBOXES = {
    "BC": (48.3, -139.0, 60.0, -114.0),
    "AB": (49.0, -120.0, 60.0, -110.0),
    "SK": (49.0, -110.0, 60.0, -101.0),
    "MB": (49.0, -101.0, 60.0, -89.0),
    "ON": (41.7, -95.0, 56.9, -74.3),
    "QC": (45.0, -79.8, 62.6, -57.1),
    "NB": (45.0, -69.0, 48.1, -63.8),
    "NS": (43.4, -66.4, 47.0, -59.7),
    "PE": (45.9, -64.4, 47.1, -62.0),
    "NL": (46.6, -67.8, 60.4, -52.6),
    "YT": (60.0, -141.0, 70.0, -123.8),
    "NT": (60.0, -136.0, 78.8, -101.6),
    "NU": (60.0, -120.0, 83.1, -55.0),
}


def _approx_province(lat: float, lng: float) -> str:
    """Approximation grossière de la province depuis lat/lng."""
    for prov, (mlat, mlng, Mlat, Mlng) in PROVINCE_BBOXES.items():
        if mlat <= lat <= Mlat and mlng <= lng <= Mlng:
            return prov
    return "?"


def generate_grid(resolution: int = 5) -> list:
    """Génère la liste des cellules H3 couvrant le Canada.

    H3 résolutions vs grille :
      res 3 : ~270 km/hex   → ~30 cellules Canada
      res 4 : ~100 km/hex   → ~150 cellules
      res 5 : ~37 km/hex    → ~700 cellules
      res 6 : ~14 km/hex    → ~5 000 cellules
      res 7 : ~5 km/hex     → ~36 000 cellules
      res 8 : ~2 km/hex     → ~250 000 cellules
    """
    # H3 v4 API
    poly = h3.LatLngPoly(CANADA_POLYGON_LATLNG)
    cells = h3.polygon_to_cells(poly, res=resolution)

    grid = []
    for cell in cells:
        lat, lng = h3.cell_to_latlng(cell)
        province = _approx_province(lat, lng)
        grid.append({
            "h3_index": cell,
            "lat": round(lat, 4),
            "lng": round(lng, 4),
            "province": province,
        })
    return grid


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--resolution", type=int, default=5, help="H3 resolution (3-7)")
    parser.add_argument("--output", default="/app/backend/cache/zerocost_v1/canada_h3_grid.json")
    args = parser.parse_args()

    print(f"Génération grille H3 niveau {args.resolution} pour Canada...")
    grid = generate_grid(args.resolution)
    print(f"  ✓ {len(grid)} cellules H3 générées")

    # Stats par province
    by_prov = {}
    for cell in grid:
        by_prov[cell["province"]] = by_prov.get(cell["province"], 0) + 1
    print("  ✓ Distribution par province :")
    for prov, n in sorted(by_prov.items(), key=lambda x: -x[1]):
        print(f"      {prov:3s} : {n}")

    # Save
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps({
            "doctrine": "P22ΩΩ_ZEROCOST_CANADA_H3_GRID_Ω",
            "schema_version": 1,
            "resolution": args.resolution,
            "n_cells": len(grid),
            "by_province": by_prov,
            "cells": grid,
        }, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"  ✓ Sauvegardé : {output_path}")

    # Extrapolation compute
    species_count = 6
    months_count = 4
    hours_count = 3
    total_tiles = len(grid) * species_count * months_count * hours_count
    print("\n📊 EXTRAPOLATION COMPUTE :")
    print(f"  Tuiles totales : {total_tiles:,}")
    print(f"  Volume estimé  : {total_tiles * 14 / 1024:.0f} MB")
    print(f"  Coût stockage  : ${total_tiles * 14 / 1024 / 1024 * 0.015:.2f}/mois R2")
    # Avec 16 workers parallèles k8s, 50s/tuile en cold-start
    parallel_workers = 16
    sec_per_tile = 50
    total_seconds = total_tiles * sec_per_tile / parallel_workers
    print(f"  Compute parallèle : {parallel_workers} workers × {sec_per_tile}s/tuile = {total_seconds/3600:.1f}h")


if __name__ == "__main__":
    main()

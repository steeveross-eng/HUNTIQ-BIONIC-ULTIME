"""
zerocost_extract_p1_only.py — Extrait sous-grille P1 IFAP/ZEC/RF uniquement
═══════════════════════════════════════════════════════════════════════
P22ΩΩ_PHASE3_WEATHERCACHE_BETA2_B_E_EXEC_Ω · STEEVE-MAX · 2026-02-19

Filtre la grille pondérée pour ne conserver QUE les cellules priorité 1
(hotspots IFAP/ZEC/RF). Utilisé pour le cycle pilote local étendu et
pour le déploiement k8s 256w one-shot.
"""
import json
from pathlib import Path

SRC = Path("/app/backend/cache/zerocost_v1/canada_h3_grid_r6_qc_maritimes_weighted.json")
DST = Path("/app/backend/cache/zerocost_v1/canada_h3_grid_r6_p1_only.json")

data = json.loads(SRC.read_text())
p1_cells = [c for c in data["cells"] if c.get("priority") == 1]

# Diversification géographique pour le pilote local : trier par lng puis lat
# pour étaler les workers sur multiple bboxes (Outaouais, Laurentides, etc.)
p1_cells.sort(key=lambda c: (round(c["lng"], 1), round(c["lat"], 1)))

out = {
    "doctrine": "P22ΩΩ_PHASE3_WEATHERCACHE_BETA2_P1_ONLY_Ω",
    "schema_version": 1,
    "resolution": data["resolution"],
    "n_cells": len(p1_cells),
    "p1_bboxes": data.get("p1_hotspots_bboxes", []),
    "cells": p1_cells,
}
DST.write_text(json.dumps(out, ensure_ascii=False, indent=2))
print(f"✅ Grille P1 only sauvegardée : {DST}")
print(f"   Cellules P1 : {len(p1_cells)}")

# Distribution par lng (~par région hotspot)
from collections import Counter
bins = Counter()
for c in p1_cells:
    lng_bin = round(c["lng"])
    bins[lng_bin] += 1
print(f"   Distribution lng (binning 1°):")
for lng, n in sorted(bins.items())[:15]:
    print(f"     {lng:+d}°W : {n}")

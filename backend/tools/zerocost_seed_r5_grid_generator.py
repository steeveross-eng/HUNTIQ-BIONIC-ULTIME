"""
zerocost_seed_r5_grid_generator.py — Générateur grille H3 R5 (seed layer)
═══════════════════════════════════════════════════════════════════════
P22ΩΩ_PHASE3_BUNDLE_SEED_H3R5_BETA2_SIGMA_TAU_Ω · STEEVE-MAX · 2026-02-19

⚠️  STATUT : SQUELETTE READY-TO-RUN · INERTE TANT QUE COMMANDANT N'A PAS
            VALIDÉ L'ACTIVATION VIA `COMMANDE_OPERATIONNELLE_BETA2_ST_ACTIVATION_Ω.md`.

DOCTRINE
--------
Génère la **grille H3 R5 parente** (~37 km / 252 km²) à partir de la grille
P1 / 3 RF déjà filtrée. Chaque cellule R5 :
  - Sera computée 1 fois (V20 complet) lors du Phase 1 SEED.
  - Sera fan-out vers ses 7 cellules R6 enfants lors du Phase 2 FAN-OUT.

ENTRÉE  : grille H3 R6 P1-only ou 3 RF focalisée (filtre géographique pré-fait)
SORTIE  : grille H3 R5 unique (parents distincts) + mapping R5 → liste R6 enfants

USAGE (à exécuter UNIQUEMENT sur ordre Commandant) :
    python3 tools/zerocost_seed_r5_grid_generator.py \
      --input /app/backend/cache/zerocost_v1/canada_h3_grid_r6_3rf_focused.json \
      --output /app/backend/cache/zerocost_v1/canada_h3_grid_r5_seed.json
"""
import argparse
import json
from collections import defaultdict
from pathlib import Path

try:
    import h3
except ImportError:
    raise SystemExit("Missing h3 dependency · pip install h3==4.x")


def build_r5_seed_grid(r6_grid: dict) -> dict:
    """Construit la grille R5 unique à partir d'une grille R6 filtrée."""
    if r6_grid.get("resolution") != 6:
        raise ValueError(
            f"Grille source attendue à H3 R6, reçu R{r6_grid.get('resolution')}"
        )

    r5_to_r6_children = defaultdict(list)
    r5_centers = {}

    for r6_cell in r6_grid["cells"]:
        h3_r6 = r6_cell.get("h3_index") or h3.latlng_to_cell(
            r6_cell["lat"], r6_cell["lng"], 6
        )
        h3_r5 = h3.cell_to_parent(h3_r6, 5)

        r5_to_r6_children[h3_r5].append({
            "h3_r6": h3_r6,
            "lat_r6": r6_cell["lat"],
            "lng_r6": r6_cell["lng"],
            "rf_label": r6_cell.get("rf_label"),
            "priority": r6_cell.get("priority"),
        })

        if h3_r5 not in r5_centers:
            r5_lat, r5_lng = h3.cell_to_latlng(h3_r5)
            r5_centers[h3_r5] = {
                "h3_r5": h3_r5,
                "lat_r5": round(r5_lat, 4),
                "lng_r5": round(r5_lng, 4),
            }

    r5_cells = []
    for h3_r5, meta in r5_centers.items():
        children = r5_to_r6_children[h3_r5]
        r5_cells.append({
            **meta,
            "n_r6_children": len(children),
            "r6_children": children,
        })
    r5_cells.sort(key=lambda c: (-c["n_r6_children"], c["lat_r5"]))

    return {
        "doctrine": "P22ΩΩ_PHASE3_BUNDLE_SEED_H3R5_BETA2_SIGMA_TAU_Ω",
        "schema_version": 1,
        "resolution_seed": 5,
        "resolution_target": 6,
        "n_r5_cells": len(r5_cells),
        "n_r6_children_total": sum(c["n_r6_children"] for c in r5_cells),
        "compression_ratio": round(
            sum(c["n_r6_children"] for c in r5_cells) / max(len(r5_cells), 1), 2
        ),
        "cells": r5_cells,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Grille H3 R6 source")
    parser.add_argument("--output", required=True, help="Grille H3 R5 cible")
    args = parser.parse_args()

    print("═══ GÉNÉRATEUR GRILLE H3 R5 SEED · β2-ΣΤ ═══")
    src = json.loads(Path(args.input).read_text())
    print(f"  Source R6        : {args.input}")
    print(f"  Cellules R6 src  : {src.get('n_cells', len(src.get('cells', []))):,}")

    out = build_r5_seed_grid(src)
    print(f"\n  Cellules R5 uniques : {out['n_r5_cells']:,}")
    print(f"  Cellules R6 enfants : {out['n_r6_children_total']:,}")
    print(f"  Ratio compression   : ×{out['compression_ratio']}")

    SPECIES, MONTHS, HOURS = 6, 4, 3
    seed_tiles = out["n_r5_cells"] * SPECIES * MONTHS * HOURS
    fanout_tiles = out["n_r6_children_total"] * SPECIES * MONTHS * HOURS
    print(f"\n  📊 EXTRAPOLATION β2-ΣΤ :")
    print(f"     Tuiles SEED (compute V20)   : {seed_tiles:,}")
    print(f"     Tuiles FAN-OUT (zéro-cost)  : {fanout_tiles:,}")
    print(f"     ETA SEED 16w @ 213s/t       : {seed_tiles*213/16/3600/24:.1f} jours")
    print(f"     ETA SEED 256w (k8s) @ 213s/t: {seed_tiles*213/256/3600/24:.2f} jours")

    Path(args.output).write_text(json.dumps(out, ensure_ascii=False, indent=2))
    print(f"\n  ✓ Grille R5 sauvegardée : {args.output}")
    print(f"  ✓ Taille fichier        : {Path(args.output).stat().st_size/1024:.1f} KB")


if __name__ == "__main__":
    main()

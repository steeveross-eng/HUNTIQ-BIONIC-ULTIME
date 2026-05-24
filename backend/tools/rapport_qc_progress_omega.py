"""
rapport_qc_progress_omega.py — RAPPORT_QC_PROGRESS_Ω (Phase 2)
═══════════════════════════════════════════════════════════════════════════════
P22ΩΩ_AUTOPILOT_4D_SAFE_Ω · COMMANDANT STEEVE-MAX · 2026-02-20 · BCE-4X ULTIME ABSOLU
Verrou Phase III · LECTURE SEULE · Mode FULL (toutes 12h).

DOCTRINE
--------
Audit couverture Phase 2 : tuiles R2 dans régions limitrophes (priority=1).
Comparaison vs grille QC structurale `canada_h3_grid_r5_seed_qc_full.json`.

USAGE
-----
    OUTPUT=text|json python3 /app/backend/tools/rapport_qc_progress_omega.py
"""
from __future__ import annotations

import json
import os
import sys
import time
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

BACKEND_ROOT = Path("/app/backend")
sys.path.insert(0, str(BACKEND_ROOT))
from dotenv import load_dotenv
load_dotenv(BACKEND_ROOT / ".env", override=False)

import boto3
from botocore.config import Config

GRID_QC = BACKEND_ROOT / "cache" / "zerocost_v1" / "canada_h3_grid_r5_seed_qc_full.json"

OUTPUT_MODE = os.environ.get("OUTPUT", "text")

R2_BUCKET = os.environ.get("CF_R2_BUCKET")
R2_ENDPOINT = os.environ.get("R2_S3_ENDPOINT")
R2_AK = os.environ.get("R2_ACCESS_KEY_ID")
R2_SK = os.environ.get("R2_SECRET_ACCESS_KEY")


def _label_of(lat, lon, grid):
    """Retourne (label, priority) selon ordre limitrophe > 3RF > QC sud."""
    for b in grid.get("bboxes_limitrophes", []):
        if b["lat_min"] <= lat <= b["lat_max"] and b["lng_min"] <= lon <= b["lng_max"]:
            return b["label"], 1
    for b in grid.get("bboxes_3rf", []):
        if b["lat_min"] <= lat <= b["lat_max"] and b["lng_min"] <= lon <= b["lng_max"]:
            return b["label"], 2
    qc = grid.get("bbox_qc_reserve", {})
    if qc and qc["lat_min"] <= lat <= qc["lat_max"] and qc["lng_min"] <= lon <= qc["lng_max"]:
        return "QC_SUD_OTHER", 3
    return "OUT_OF_QC", 99


def build() -> dict:
    if not GRID_QC.is_file():
        return {
            "_status": "GRID_QC_NOT_GENERATED",
            "_note": "Grille QC structurale absente · Phase 2 non encore activée",
            "_generated_at": datetime.now(timezone.utc).isoformat(),
        }
    grid = json.loads(GRID_QC.read_text())

    # Cibles depuis grille
    targets_priority = grid.get("counts_r6_per_priority", {})
    targets = {
        "LIMITROPHES_priority_1": int(targets_priority.get("1", 0)),
        "3RF_priority_2": int(targets_priority.get("2", 0)),
        "QC_SUD_priority_3": int(targets_priority.get("3", 0)),
    }

    # Inventaire R2 streaming
    cli = boto3.client("s3", endpoint_url=R2_ENDPOINT,
        aws_access_key_id=R2_AK, aws_secret_access_key=R2_SK,
        config=Config(signature_version="s3v4"))
    counts_priority = Counter()
    counts_label = Counter()
    cells_label = defaultdict(set)
    total = 0
    t0 = time.time()
    paginator = cli.get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=R2_BUCKET, Prefix="v1/"):
        for obj in page.get("Contents", []):
            k = obj["Key"]
            total += 1
            try:
                parts = k.split("/")
                latlng = parts[2].split("_")
                lat = float(latlng[0])
                lon = float(latlng[1])
                label, prio = _label_of(lat, lon, grid)
                counts_priority[prio] += 1
                counts_label[label] += 1
                cells_label[label].add((round(lat, 4), round(lon, 4)))
            except Exception:
                continue
    dt = time.time() - t0

    payload = {
        "_doctrine": "P22ΩΩ_AUTOPILOT_4D_SAFE_Ω",
        "_report": "RAPPORT_QC_PROGRESS_Ω",
        "_generated_at": datetime.now(timezone.utc).isoformat(),
        "_phase": "PHASE_2_QC_LIMITROPHES",
        "scan_sec": dt,
        "total_keys_scanned": total,
        "targets_r6": targets,
        "tiles_by_priority": dict(counts_priority),
        "tiles_by_label": dict(counts_label),
        "cells_unique_by_label": {k: len(v) for k, v in cells_label.items()},
        "verrou_phase_iii": True,
        "lecture_seule": True,
    }

    # Calcul progression limitrophes
    limit_tiles = sum(counts_label[b["label"]] for b in grid.get("bboxes_limitrophes", []))
    limit_cells_unique = sum(len(cells_label[b["label"]]) for b in grid.get("bboxes_limitrophes", []))
    payload["limitrophes_summary"] = {
        "tiles_done": limit_tiles,
        "cells_unique_done": limit_cells_unique,
        "cells_target_total": targets["LIMITROPHES_priority_1"],
        "pct_cells": round(limit_cells_unique / targets["LIMITROPHES_priority_1"] * 100, 2)
                     if targets["LIMITROPHES_priority_1"] > 0 else 0.0,
    }
    return payload


def render_text(payload: dict) -> str:
    if payload.get("_status") == "GRID_QC_NOT_GENERATED":
        return (f"RAPPORT_QC_PROGRESS_Ω · STATUS={payload['_status']}\n"
                f"  {payload.get('_note')}\n"
                f"  generated_at={payload.get('_generated_at')}")
    lines = []
    lines.append("═" * 78)
    lines.append(f"  RAPPORT_QC_PROGRESS_Ω · {payload['_generated_at']}")
    lines.append(f"  Phase     : {payload['_phase']}")
    lines.append("═" * 78)
    lines.append("\n§ A · LIMITROPHES (priority=1) — CIBLE PHASE 2 ACTIVE")
    ls = payload["limitrophes_summary"]
    lines.append(f"  Tuiles uploadées R2  : {ls['tiles_done']}")
    lines.append(f"  Cells uniques        : {ls['cells_unique_done']} / {ls['cells_target_total']}")
    lines.append(f"  Couverture cells     : {ls['pct_cells']:.2f}%")
    lines.append("\n§ B · DÉTAIL PAR LABEL")
    for label, n in sorted(payload["tiles_by_label"].items()):
        cells = payload["cells_unique_by_label"].get(label, 0)
        lines.append(f"  {label:42}: {n:>7} tuiles · {cells:>5} cells")
    lines.append("\n§ C · DISTRIBUTION PAR PRIORITÉ")
    for prio, n in sorted(payload["tiles_by_priority"].items()):
        lines.append(f"  priority={prio}: {n:>7} tuiles")
    lines.append("\n§ D · VERROU PHASE III")
    lines.append(f"  verrou_phase_iii         : {payload['verrou_phase_iii']}")
    lines.append(f"  lecture_seule            : {payload['lecture_seule']}")
    lines.append(f"  total_keys_scanned       : {payload['total_keys_scanned']}")
    lines.append(f"  scan_sec                 : {payload['scan_sec']:.1f}s")
    lines.append("═" * 78)
    return "\n".join(lines)


def main():
    payload = build()
    if OUTPUT_MODE == "json":
        print(json.dumps(payload, indent=2, ensure_ascii=False, default=str))
    else:
        print(render_text(payload))


if __name__ == "__main__":
    main()

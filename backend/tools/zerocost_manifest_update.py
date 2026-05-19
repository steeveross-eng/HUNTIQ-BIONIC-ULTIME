"""
zerocost_manifest_update.py — Régénère le manifest R2 depuis le bucket
═══════════════════════════════════════════════════════════════════════
P22ΩΩ_PHASE3_MANIFEST_CANADA_Ω · STEEVE-MAX
"""
import datetime
import gzip
import json
import os
import sys
from pathlib import Path

import boto3
from dotenv import load_dotenv

load_dotenv("/app/backend/.env")

s3 = boto3.client(
    "s3",
    endpoint_url=os.environ["R2_S3_ENDPOINT"],
    aws_access_key_id=os.environ["R2_ACCESS_KEY_ID"],
    aws_secret_access_key=os.environ["R2_SECRET_ACCESS_KEY"],
    region_name="auto",
)

BUCKET = os.environ["CF_R2_BUCKET"]

print(f"═══ MANIFEST UPDATE · bucket={BUCKET} ═══")

paginator = s3.get_paginator("list_objects_v2")

tiles = {}            # species -> set(cells)
species_count = {}    # species -> int
cells_global = set()
total_bytes = 0
n_tiles = 0

for page in paginator.paginate(Bucket=BUCKET, Prefix="v1/"):
    for obj in page.get("Contents", []):
        key = obj["Key"]
        if not key.endswith(".json.gz"):
            continue
        parts = key.split("/")
        if len(parts) < 4:
            continue
        species = parts[1]
        cell = parts[2]
        n_tiles += 1
        total_bytes += obj["Size"]
        species_count[species] = species_count.get(species, 0) + 1
        tiles.setdefault(species, set()).add(cell)
        cells_global.add(cell)

manifest = {
    "doctrine": "P22ΩΩ_ZEROCOST_CANADA_H3R6_Ω",
    "schema_version": 2,
    "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "resolution_h3": 6,
    "n_tiles": n_tiles,
    "total_size_bytes": total_bytes,
    "cells_unique": len(cells_global),
    "by_species": {sp: len(cells) for sp, cells in tiles.items()},
    "tiles_by_species": species_count,
    "cdn_base": "https://cdn-zerocost.bionichunt.com",
    "fallback_endpoint": "/api/v20/territoire/bundle",
}

body = json.dumps(manifest, ensure_ascii=False, indent=2).encode()

s3.put_object(
    Bucket=BUCKET,
    Key="manifest.json",
    Body=body,
    ContentType="application/json",
    CacheControl="public, max-age=300",
)

print(f"✅ Manifest pushed to R2")
print(f"   Objets indexés : {n_tiles}")
print(f"   Cellules H3 uniques : {len(cells_global)}")
print(f"   Volume total : {total_bytes / 1024:.1f} KB")
print(f"   Espèces couvertes : {sorted(species_count.keys())}")
print(json.dumps(manifest["by_species"], indent=2))

"""
zerocost_upload_r2_native.py — Upload via API native Cloudflare R2
================================================================
P22ΩΩ_ZEROCOST_PHASE2_R2_CLOUDFLARE_Ω · 2026-02-XX · STEEVE-MAX

Upload des tuiles ZEROCOST vers R2 en utilisant l'API REST native
Cloudflare (PAS l'API S3-compat). Avantage : utilise le token CF `cfut_*`
existant — aucune création de R2 Access Key S3 nécessaire.

Endpoint :
    PUT https://api.cloudflare.com/client/v4/accounts/{account_id}
        /r2/buckets/{bucket}/objects/{url_encoded_key}

Headers obligatoires :
    Authorization: Bearer cfut_*
    Content-Encoding: gzip  (pour servir le fichier décompressé via CDN)

Limites API native :
    Max 300 MB par objet (largement suffisant pour nos tuiles ~14 KB)
    Pas de multipart upload (notre besoin <50 MB total)
"""
import gzip
import json
import os
import sys
import time
import urllib.parse
from pathlib import Path

import requests
from dotenv import load_dotenv

BACKEND_ROOT = Path("/app/backend")
sys.path.insert(0, str(BACKEND_ROOT))
load_dotenv(BACKEND_ROOT / ".env")

CACHE_ROOT = Path("/app/backend/cache/zerocost_v1")
SCHEMA_PREFIX = "v1"

CF_API_TOKEN = os.environ.get("CF_API_TOKEN")
CF_ACCOUNT_ID = os.environ.get("CF_ACCOUNT_ID")
CF_R2_BUCKET = os.environ.get("CF_R2_BUCKET", "bionic-zerocost-omega")

CF_API_BASE = f"https://api.cloudflare.com/client/v4/accounts/{CF_ACCOUNT_ID}/r2/buckets/{CF_R2_BUCKET}"


def _put_object(key: str, file_path: Path, content_encoding: str = "gzip") -> dict:
    """Upload un seul fichier via API native CF R2."""
    encoded_key = urllib.parse.quote(key, safe="")
    url = f"{CF_API_BASE}/objects/{encoded_key}"
    headers = {
        "Authorization": f"Bearer {CF_API_TOKEN}",
        "Content-Type": "application/json",
    }
    if content_encoding:
        headers["Content-Encoding"] = content_encoding
    with open(file_path, "rb") as f:
        r = requests.put(url, headers=headers, data=f.read(), timeout=30)
    return r.json() if r.headers.get("content-type", "").startswith("application/json") else {"status": r.status_code}


def upload_all():
    """Upload toutes les tuiles + manifest vers R2 via API native."""
    if not CF_API_TOKEN or not CF_ACCOUNT_ID:
        print("🔴 CF_API_TOKEN / CF_ACCOUNT_ID manquants dans .env")
        sys.exit(1)

    tiles = sorted(CACHE_ROOT.rglob("*.json.gz"))
    manifest_path = CACHE_ROOT / "manifest.json"

    if not tiles:
        print(f"🔴 Aucune tuile dans {CACHE_ROOT}")
        print("   Lancer d'abord : python3 tools/zerocost_precompute_shadow.py")
        sys.exit(2)

    print(f"📦 {len(tiles)} tuiles + 1 manifest → R2://{CF_R2_BUCKET}/{SCHEMA_PREFIX}/")
    print()
    t0 = time.time()
    stats = {"uploaded": 0, "failed": 0, "total_bytes": 0}

    # 1. Manifest
    res = _put_object(
        f"{SCHEMA_PREFIX}/manifest.json",
        manifest_path,
        content_encoding=None,  # manifest est en JSON non-compressé
    )
    if res.get("success"):
        stats["uploaded"] += 1
        print("✓ manifest.json")
    else:
        stats["failed"] += 1
        print(f"🔴 manifest: {res}")

    # 2. Tuiles
    for tile in tiles:
        rel = tile.relative_to(CACHE_ROOT)
        key = f"{SCHEMA_PREFIX}/{rel.as_posix()}"
        size = tile.stat().st_size
        try:
            res = _put_object(key, tile, content_encoding="gzip")
            if res.get("success"):
                stats["uploaded"] += 1
                stats["total_bytes"] += size
                if stats["uploaded"] % 20 == 0:
                    elapsed = time.time() - t0
                    rate = stats["uploaded"] / max(elapsed, 1)
                    print(
                        f"  ... {stats['uploaded']}/{len(tiles)+1} "
                        f"({rate:.1f} tiles/s, {stats['total_bytes']/1024:.1f} KB)"
                    )
            else:
                stats["failed"] += 1
                print(f"🔴 {key}: {res.get('errors', res)}")
        except Exception as e:
            stats["failed"] += 1
            print(f"🔴 {key}: {type(e).__name__}: {e}")

    elapsed = time.time() - t0
    print()
    print("═" * 70)
    print(f"UPLOAD R2 NATIVE · TERMINÉ en {elapsed:.1f}s")
    print(f"  Uploaded : {stats['uploaded']}/{len(tiles)+1}")
    print(f"  Failed   : {stats['failed']}")
    print(f"  Volume   : {stats['total_bytes']/1024:.1f} KB")
    print(f"  Bucket   : https://api.cloudflare.com/.../buckets/{CF_R2_BUCKET}")
    print("  CDN URL  : https://cdn-zerocost.bionichunt.com/v1/...")
    print("═" * 70)
    return stats


if __name__ == "__main__":
    upload_all()

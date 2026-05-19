"""
zerocost_upload_r2.py — Upload tuiles ZEROCOST vers Cloudflare R2
================================================================
P22ΩΩ_ZEROCOST_PHASE2_R2_CLOUDFLARE_Ω · 2026-02-XX · STEEVE-MAX
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU

Upload toutes les tuiles précalculées de /app/backend/cache/zerocost_v1/
vers le bucket Cloudflare R2 `bionic-zerocost-omega`.

Stratégie :
  - Authentification : R2 Access Key ID + Secret (S3-compat boto3)
  - Endpoint : https://<ACCOUNT_ID>.r2.cloudflarestorage.com
  - Headers : ContentEncoding=gzip, ContentType=application/json,
              CacheControl=public, max-age=86400, immutable
  - Versioning : prefix /v1/ pour permettre versionnement futur

PRÉREQUIS :
  - R2 ACTIVÉ dans le Dashboard Cloudflare (https://dash.cloudflare.com/?to=/:account/r2)
  - R2 Access Key créée (R2 → API Tokens → Create R2 API Token)
  - .env contient : CF_ACCOUNT_ID, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY

USAGE :
    cd /app/backend && python3 tools/zerocost_upload_r2.py
"""
import gzip
import json
import os
import sys
import time
from pathlib import Path

from dotenv import load_dotenv

# Bootstrap path
BACKEND_ROOT = Path("/app/backend")
sys.path.insert(0, str(BACKEND_ROOT))
load_dotenv(BACKEND_ROOT / ".env")

import boto3
from botocore.config import Config

CACHE_ROOT = Path("/app/backend/cache/zerocost_v1")
SCHEMA_PREFIX = "v1"

CF_ACCOUNT_ID = os.environ.get("CF_ACCOUNT_ID")
R2_BUCKET = os.environ.get("CF_R2_BUCKET", "bionic-zerocost-omega")
R2_ACCESS_KEY_ID = os.environ.get("R2_ACCESS_KEY_ID")
R2_SECRET_ACCESS_KEY = os.environ.get("R2_SECRET_ACCESS_KEY")


def _ensure_creds():
    """Vérifie présence des credentials R2 et fournit instructions claires."""
    missing = []
    if not CF_ACCOUNT_ID:
        missing.append("CF_ACCOUNT_ID")
    if not R2_ACCESS_KEY_ID:
        missing.append("R2_ACCESS_KEY_ID")
    if not R2_SECRET_ACCESS_KEY:
        missing.append("R2_SECRET_ACCESS_KEY")
    if missing:
        print("🔴 CREDENTIALS R2 MANQUANTS:", ", ".join(missing))
        print()
        print("📋 ACTION COMMANDANT REQUISE :")
        print("  1. Activer R2 dans Cloudflare Dashboard si pas déjà fait :")
        print("     https://dash.cloudflare.com/?to=/:account/r2")
        print("  2. Créer un API Token R2 :")
        print("     R2 → 'Manage R2 API Tokens' → 'Create API token'")
        print("     Permissions : 'Object Read & Write' sur bucket 'bionic-zerocost-omega'")
        print("  3. Récupérer Access Key ID + Secret Access Key et les ajouter à /app/backend/.env :")
        print("     R2_ACCESS_KEY_ID=...")
        print("     R2_SECRET_ACCESS_KEY=...")
        sys.exit(1)


def _build_r2_client():
    """Construit un client boto3 configuré pour R2."""
    endpoint = f"https://{CF_ACCOUNT_ID}.r2.cloudflarestorage.com"
    return boto3.client(
        "s3",
        endpoint_url=endpoint,
        aws_access_key_id=R2_ACCESS_KEY_ID,
        aws_secret_access_key=R2_SECRET_ACCESS_KEY,
        config=Config(
            signature_version="s3v4",
            region_name="auto",  # R2 utilise 'auto'
            retries={"max_attempts": 3, "mode": "standard"},
        ),
    )


def upload_all_tiles():
    """Upload toutes les tuiles + manifest vers R2."""
    _ensure_creds()
    client = _build_r2_client()

    # 1. Tester accès bucket
    try:
        client.head_bucket(Bucket=R2_BUCKET)
        print(f"✓ Accès bucket R2 '{R2_BUCKET}' confirmé")
    except Exception as e:
        print(f"🔴 Accès bucket échoué: {e}")
        print(f"   Vérifier : bucket '{R2_BUCKET}' existe + API Token a Read/Write")
        sys.exit(2)

    tiles = list(CACHE_ROOT.rglob("*.json.gz"))
    manifest_path = CACHE_ROOT / "manifest.json"

    if not tiles:
        print(f"🔴 Aucune tuile trouvée dans {CACHE_ROOT}")
        print("   Lancer d'abord : python3 tools/zerocost_precompute_shadow.py")
        sys.exit(3)

    print(f"📦 {len(tiles)} tuiles à uploader vers R2://{R2_BUCKET}/{SCHEMA_PREFIX}/")
    print("   + manifest.json")
    print()

    stats = {"uploaded": 0, "failed": 0, "skipped": 0, "total_bytes": 0, "start_ts": time.time()}

    # 2. Upload manifest
    try:
        client.upload_file(
            str(manifest_path),
            R2_BUCKET,
            f"{SCHEMA_PREFIX}/manifest.json",
            ExtraArgs={
                "ContentType": "application/json",
                "CacheControl": "public, max-age=300",  # 5 min cache pour manifest
            },
        )
        print("✓ Uploaded manifest.json")
        stats["uploaded"] += 1
    except Exception as e:
        print(f"🔴 manifest upload failed: {e}")
        stats["failed"] += 1

    # 3. Upload tuiles
    for tile_path in tiles:
        rel = tile_path.relative_to(CACHE_ROOT)
        key = f"{SCHEMA_PREFIX}/{rel.as_posix()}"
        size = tile_path.stat().st_size
        try:
            client.upload_file(
                str(tile_path),
                R2_BUCKET,
                key,
                ExtraArgs={
                    "ContentType": "application/json",
                    "ContentEncoding": "gzip",
                    "CacheControl": "public, max-age=86400, immutable",
                },
            )
            stats["uploaded"] += 1
            stats["total_bytes"] += size
            if stats["uploaded"] % 20 == 0:
                print(f"  ... {stats['uploaded']}/{len(tiles)+1} uploaded")
        except Exception as e:
            stats["failed"] += 1
            print(f"🔴 {key}: {e}")

    elapsed = time.time() - stats["start_ts"]
    print()
    print("═" * 70)
    print(f"UPLOAD ZEROCOST R2 · TERMINÉ en {elapsed:.1f}s")
    print(f"  Uploaded  : {stats['uploaded']}")
    print(f"  Failed    : {stats['failed']}")
    print(f"  Volume    : {stats['total_bytes']/1024:.1f} KB")
    print(f"  Bucket    : R2://{R2_BUCKET}/{SCHEMA_PREFIX}/")
    if CF_ACCOUNT_ID:
        print(f"  Endpoint  : https://{CF_ACCOUNT_ID}.r2.cloudflarestorage.com")
    print("═" * 70)
    return stats


if __name__ == "__main__":
    upload_all_tiles()

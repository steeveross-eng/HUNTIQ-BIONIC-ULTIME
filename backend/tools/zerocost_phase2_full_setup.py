"""
zerocost_phase2_full_setup.py — Orchestration Phase 2 ZEROCOST COMPLET
================================================================
P22ΩΩ_ZEROCOST_PHASE2_R2_CLOUDFLARE_Ω · 2026-02-XX · STEEVE-MAX

Une fois R2 ACTIVÉ par le Commandant dans le Dashboard Cloudflare, ce script
orchestre la mise en route complète de la Phase 2 :

  1. Création bucket R2 'bionic-zerocost-omega' (Cloudflare API)
  2. Configuration custom domain cdn-zerocost.bionichunt.com (DNS CNAME)
  3. Upload des tuiles précalculées (boto3 S3-compat)
  4. Validation : test fetch d'une tuile depuis CDN
  5. Rapport final

PRÉREQUIS COMMANDANT :
  ✅ Token CF (cfut_*) avec R2 Storage Read/Write
  ✅ Zone bionichunt.com (40163762c592c21104d5fe67e08be8bf)
  ⏳ R2 ACTIVÉ via Dashboard (https://dash.cloudflare.com/?to=/:account/r2)
  ⏳ R2 API Token créé via R2 → 'Manage R2 API Tokens'
  ⏳ Variables .env : R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY

USAGE :
    cd /app/backend && python3 tools/zerocost_phase2_full_setup.py
"""
import os
import sys
import time
import json
import urllib.parse
from pathlib import Path

import requests
from dotenv import load_dotenv

BACKEND_ROOT = Path("/app/backend")
sys.path.insert(0, str(BACKEND_ROOT))
load_dotenv(BACKEND_ROOT / ".env")

CF_API_TOKEN = os.environ.get("CF_API_TOKEN")
CF_ZONE_ID = os.environ.get("CF_ZONE_ID", "40163762c592c21104d5fe67e08be8bf")
CF_ACCOUNT_ID = os.environ.get("CF_ACCOUNT_ID")
CF_R2_BUCKET = os.environ.get("CF_R2_BUCKET", "bionic-zerocost-omega")
CF_R2_CDN_HOST = os.environ.get("CF_R2_CDN_HOST", "cdn-zerocost.bionichunt.com")

CF_API_BASE = "https://api.cloudflare.com/client/v4"


def _cf_request(method, path, **kwargs):
    """Wrapper pour appels Cloudflare API."""
    url = f"{CF_API_BASE}/{path.lstrip('/')}"
    headers = {
        "Authorization": f"Bearer {CF_API_TOKEN}",
        "Content-Type": "application/json",
        **kwargs.pop("headers", {}),
    }
    r = requests.request(method, url, headers=headers, timeout=15, **kwargs)
    try:
        return r.json(), r.status_code
    except Exception:
        return {"raw": r.text[:200]}, r.status_code


def step1_create_bucket():
    """Crée le bucket R2 'bionic-zerocost-omega'."""
    print("\n┃ STEP 1 · CRÉATION BUCKET R2")
    print("┃ " + "─" * 60)
    data, status = _cf_request(
        "POST",
        f"/accounts/{CF_ACCOUNT_ID}/r2/buckets",
        data=json.dumps({"name": CF_R2_BUCKET, "locationHint": "enam"}),
    )
    if data.get("success"):
        print(f"┃ ✅ Bucket créé: {CF_R2_BUCKET}")
        return True
    errors = data.get("errors", [])
    # Code 10004 = bucket already exists → idempotent OK
    if any(e.get("code") == 10004 for e in errors):
        print(f"┃ ℹ️  Bucket existe déjà: {CF_R2_BUCKET} (idempotent OK)")
        return True
    # Code 10042 = R2 not enabled
    if any(e.get("code") == 10042 for e in errors):
        print("┃ 🔴 R2 NON ACTIVÉ — action manuelle requise:")
        print("┃    1. https://dash.cloudflare.com/?to=/:account/r2")
        print("┃    2. Cliquer 'Subscribe' (Standard plan)")
        print("┃    3. Relancer ce script")
        return False
    print(f"┃ 🔴 Échec: {errors}")
    return False


def step2_setup_custom_domain():
    """Configure le custom domain cdn-zerocost.bionichunt.com pour le bucket R2."""
    print("\n┃ STEP 2 · CUSTOM DOMAIN CDN")
    print("┃ " + "─" * 60)
    domain_path = (
        f"/accounts/{CF_ACCOUNT_ID}/r2/buckets/{CF_R2_BUCKET}/domains/custom"
    )
    # 1. Vérifier si custom domain déjà attaché
    data, status = _cf_request("GET", domain_path)
    existing = [d for d in (data.get("result", {}).get("domains") or []) if d.get("domain") == CF_R2_CDN_HOST]
    if existing:
        print(f"┃ ℹ️  Custom domain déjà attaché: {CF_R2_CDN_HOST}")
        return True
    # 2. Attacher le custom domain
    data, status = _cf_request(
        "POST",
        domain_path,
        data=json.dumps({
            "domain": CF_R2_CDN_HOST,
            "zoneId": CF_ZONE_ID,
            "enabled": True,
        }),
    )
    if data.get("success"):
        print(f"┃ ✅ Custom domain attaché: https://{CF_R2_CDN_HOST}")
        print("┃    Provisionnement CDN: ~1-3 min (Cloudflare propage le SSL/cache)")
        return True
    print(f"┃ 🔴 Échec custom domain: {data.get('errors')}")
    return False


def step3_check_credentials():
    """Vérifie présence R2_ACCESS_KEY_ID + R2_SECRET_ACCESS_KEY."""
    print("\n┃ STEP 3 · VÉRIFICATION CRÉDENTIELS R2 S3")
    print("┃ " + "─" * 60)
    missing = [
        k for k in ("R2_ACCESS_KEY_ID", "R2_SECRET_ACCESS_KEY")
        if not os.environ.get(k)
    ]
    if missing:
        print(f"┃ 🔴 Manquants: {', '.join(missing)}")
        print("┃ ")
        print("┃ ACTION COMMANDANT :")
        print("┃   1. Dashboard CF → R2 → 'Manage R2 API Tokens' → Create")
        print(f"┃   2. Permissions: 'Object Read & Write' sur '{CF_R2_BUCKET}'")
        print("┃   3. Ajouter à /app/backend/.env :")
        print("┃        R2_ACCESS_KEY_ID=<from_dashboard>")
        print("┃        R2_SECRET_ACCESS_KEY=<from_dashboard>")
        return False
    print("┃ ✅ Credentials R2 présents")
    return True


def step4_upload_tiles():
    """Délègue à zerocost_upload_r2.upload_all_tiles()."""
    print("\n┃ STEP 4 · UPLOAD TUILES VERS R2")
    print("┃ " + "─" * 60)
    try:
        from tools.zerocost_upload_r2 import upload_all_tiles
        stats = upload_all_tiles()
        return stats.get("uploaded", 0) > 0 and stats.get("failed", 0) == 0
    except Exception as e:
        print(f"┃ 🔴 Upload échec: {e}")
        return False


def step5_validate_cdn():
    """Test fetch d'une tuile via le CDN pour vérifier l'intégration end-to-end."""
    print("\n┃ STEP 5 · VALIDATION END-TO-END CDN")
    print("┃ " + "─" * 60)
    # Tile pilote BSL/orignal/m5/h14
    test_url = f"https://{CF_R2_CDN_HOST}/v1/orignal/48.2067_-68.3824/m05_h14.json.gz"
    print(f"┃ Test fetch: {test_url}")
    for attempt in range(3):
        try:
            r = requests.get(test_url, timeout=10)
            if r.status_code == 200:
                size = len(r.content) / 1024
                print(f"┃ ✅ Tuile servie par CDN ({size:.1f} KB)")
                # CF-Ray header pour confirmer Cloudflare
                cf_ray = r.headers.get("CF-Ray", "?")
                cache_status = r.headers.get("CF-Cache-Status", "?")
                print(f"┃    CF-Ray: {cf_ray} · Cache: {cache_status}")
                return True
            print(f"┃    Tentative {attempt+1}: HTTP {r.status_code}")
        except Exception as e:
            print(f"┃    Tentative {attempt+1}: {type(e).__name__}")
        time.sleep(10)  # Attendre propagation CDN
    print("┃ ⚠️  CDN pas encore prêt (propagation ~3 min)")
    return False


def main():
    print("═" * 70)
    print("P22ΩΩ_ZEROCOST_PHASE2_R2_CLOUDFLARE_Ω · SETUP FULL")
    print("═" * 70)
    print(f"Zone     : {CF_ZONE_ID}")
    print(f"Account  : {CF_ACCOUNT_ID}")
    print(f"Bucket   : {CF_R2_BUCKET}")
    print(f"CDN Host : {CF_R2_CDN_HOST}")
    print("═" * 70)

    if not step1_create_bucket():
        sys.exit(1)
    step2_setup_custom_domain()  # Non-bloquant
    if not step3_check_credentials():
        sys.exit(2)
    if not step4_upload_tiles():
        sys.exit(3)
    step5_validate_cdn()  # Non-bloquant (propagation CDN ~3 min)

    print("\n" + "═" * 70)
    print("✅ PHASE 2 ZEROCOST ENGINE · SETUP TERMINÉ")
    print("═" * 70)


if __name__ == "__main__":
    main()

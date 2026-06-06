"""
r2_state_persistence_omega.py — Persistance state files workers vers Cloudflare R2
==================================================================================
P22ΩΩ_EXTERNALISATION_STATE_FILES_R2_Ω · 2026-06-06 · COMMANDANT STEEVE-MAX
BCE-4X ULTIME ABSOLU · Verrou Phase III · STRICT ADDITIF · DUAL-WRITE

Module helper haut-niveau pour externaliser les state files
`/var/log/bionic-zerocost-seed-r5/state_worker_*.json` vers le bucket Cloudflare R2
`bionic-zerocost-omega` sous le préfixe `state/`.

DOCTRINE :
  - Dual-write : R2 + filesystem maintenu (le filesystem reste source de vérité
    locale pour les workers en runtime, R2 = source de vérité cold-start).
  - Best-effort : si R2 down, log warning et continue (pas de bloquage worker).
  - Idempotent : pas d'effets de bord (clé R2 = chemin canonique unique).
  - Cold-start safe : `load_state_from_r2()` permet de reconstruire le state
    après destruction complète du filesystem (production deploy migration).

CLÉS R2 (préfixe `state/`) :
  state/state_worker_{i}.json          → state_worker_*.json par worker
  state/state.json                     → state.json (PIDs / daemon meta)

CREDENTIALS REQUIS (déjà présents dans /app/backend/.env) :
  CF_ACCOUNT_ID
  R2_ACCESS_KEY_ID
  R2_SECRET_ACCESS_KEY
  CF_R2_BUCKET

USAGE :
  from backend.integrations.r2_state_persistence_omega import (
      save_state_to_r2, load_state_from_r2, delete_state_from_r2
  )
  save_state_to_r2(worker_index=0, state_dict={"r5_idx_done": 5, ...})

INTÉGRATION DUAL-WRITE (voir EXTERNALISATION_R2_STATE_PATCH_READY.md) :
  Dans _save_worker_state() du worker, après tmp.replace(STATE_FILE) :
      save_state_to_r2(WORKER_INDEX, state_dict)  # best-effort
"""
from __future__ import annotations

import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# Bootstrap path (alignement avec autres scripts /app/backend)
BACKEND_ROOT = Path("/app/backend")
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

# Lazy load .env (idempotent si déjà chargé)
try:
    from dotenv import load_dotenv  # noqa
    load_dotenv(BACKEND_ROOT / ".env")
except Exception:
    pass

# Lazy import boto3 — évite de crasher si non installé dans certains contextes
_boto3 = None
_client_cache = None


def _get_r2_client():
    """Initialise (1×) et retourne le client boto3 S3-compat pour R2.
    Retourne None si credentials manquants — caller doit gérer fallback."""
    global _boto3, _client_cache
    if _client_cache is not None:
        return _client_cache

    cf_account_id = os.environ.get("CF_ACCOUNT_ID")
    r2_access_key = os.environ.get("R2_ACCESS_KEY_ID")
    r2_secret_key = os.environ.get("R2_SECRET_ACCESS_KEY")

    if not all([cf_account_id, r2_access_key, r2_secret_key]):
        logger.warning(
            "[R2_STATE] credentials manquants (CF_ACCOUNT_ID / R2_ACCESS_KEY_ID / "
            "R2_SECRET_ACCESS_KEY) — dual-write R2 désactivé"
        )
        return None

    try:
        if _boto3 is None:
            import boto3  # noqa
            from botocore.config import Config  # noqa
            _boto3 = (boto3, Config)
        boto3, Config = _boto3

        endpoint_url = f"https://{cf_account_id}.r2.cloudflarestorage.com"
        _client_cache = boto3.client(
            "s3",
            endpoint_url=endpoint_url,
            aws_access_key_id=r2_access_key,
            aws_secret_access_key=r2_secret_key,
            config=Config(
                signature_version="s3v4",
                retries={"max_attempts": 2, "mode": "standard"},
                connect_timeout=5,
                read_timeout=10,
            ),
            region_name="auto",
        )
        logger.info("[R2_STATE] client boto3 R2 initialisé")
        return _client_cache
    except Exception as e:
        logger.warning(f"[R2_STATE] init client échoué: {e}")
        return None


def _r2_bucket() -> str:
    return os.environ.get("CF_R2_BUCKET", "bionic-zerocost-omega")


def _state_key(worker_index: Optional[int]) -> str:
    """Construit la clé R2 canonique pour un state file.
    worker_index=None → state.json (daemon meta)."""
    if worker_index is None:
        return "state/state.json"
    return f"state/state_worker_{int(worker_index)}.json"


def save_state_to_r2(worker_index: Optional[int], state_dict: dict, timeout: float = 5.0) -> bool:
    """Best-effort dual-write d'un state dict vers R2.
    Retourne True si succès, False si échec (worker continue normalement)."""
    client = _get_r2_client()
    if client is None:
        return False
    key = _state_key(worker_index)
    try:
        body = json.dumps(state_dict, separators=(",", ":")).encode("utf-8")
        # P22ΩΩ_R2_STATE_TIMESTAMP_Ω · trace serveur pour audit cold-start
        client.put_object(
            Bucket=_r2_bucket(),
            Key=key,
            Body=body,
            ContentType="application/json",
            CacheControl="no-cache, no-store, max-age=0",
            Metadata={
                "doctrine": "P22ΩΩ_EXTERNALISATION_STATE_R2",
                "saved_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            },
        )
        return True
    except Exception as e:
        logger.warning(f"[R2_STATE] put_object fail key={key}: {e}")
        return False


def load_state_from_r2(worker_index: Optional[int], timeout: float = 5.0) -> Optional[dict]:
    """Cold-start helper : charge un state dict depuis R2.
    Retourne None si clé absente, R2 down, ou JSON invalide.
    Le caller doit fallback sur _load_worker_state() filesystem ou defaults."""
    client = _get_r2_client()
    if client is None:
        return None
    key = _state_key(worker_index)
    try:
        resp = client.get_object(Bucket=_r2_bucket(), Key=key)
        body = resp["Body"].read()
        data = json.loads(body.decode("utf-8"))
        if not isinstance(data, dict):
            logger.warning(f"[R2_STATE] get_object key={key} returned non-dict: {type(data)}")
            return None
        return data
    except Exception as e:
        # Clé absente = comportement normal en cold-start initial
        msg = str(e)
        if "NoSuchKey" in msg or "404" in msg:
            logger.info(f"[R2_STATE] key={key} absente (cold-start initial)")
        else:
            logger.warning(f"[R2_STATE] get_object fail key={key}: {e}")
        return None


def delete_state_from_r2(worker_index: Optional[int]) -> bool:
    """Purge volontaire d'un state R2 (utile pour resets doctrinaux R1_Ω)."""
    client = _get_r2_client()
    if client is None:
        return False
    key = _state_key(worker_index)
    try:
        client.delete_object(Bucket=_r2_bucket(), Key=key)
        logger.info(f"[R2_STATE] delete key={key} OK")
        return True
    except Exception as e:
        logger.warning(f"[R2_STATE] delete_object fail key={key}: {e}")
        return False


def list_state_keys_in_r2(prefix: str = "state/") -> list[str]:
    """Inventaire des state files actuellement présents dans R2.
    Utile pour diagnostic + audit cold-start."""
    client = _get_r2_client()
    if client is None:
        return []
    try:
        resp = client.list_objects_v2(Bucket=_r2_bucket(), Prefix=prefix)
        return [obj["Key"] for obj in resp.get("Contents", [])]
    except Exception as e:
        logger.warning(f"[R2_STATE] list fail prefix={prefix}: {e}")
        return []


# ─── SELF-TEST CLI (zéro impact runtime si non invoqué) ─────────────────────
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="R2 state persistence self-test (READ-ONLY safe)")
    parser.add_argument("--check", action="store_true", help="Vérifie credentials + connectivité R2")
    parser.add_argument("--list", action="store_true", help="Liste les state files actuellement dans R2")
    parser.add_argument("--load", type=int, metavar="WORKER_INDEX", help="Charge state_worker_{N} depuis R2")
    parser.add_argument("--write-test", action="store_true",
                        help="Écrit un objet test state/_selftest.json (purgé immédiatement après)")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s %(message)s")

    if args.check or not any([args.list, args.load is not None, args.write_test]):
        client = _get_r2_client()
        if client is None:
            print("❌ R2 client INIT FAIL — credentials manquants ou boto3 absent")
            sys.exit(1)
        print(f"✅ R2 client OK · bucket={_r2_bucket()}")
        print(f"   endpoint=https://{os.environ.get('CF_ACCOUNT_ID')}.r2.cloudflarestorage.com")

    if args.list:
        keys = list_state_keys_in_r2()
        print(f"📦 {len(keys)} state objects sous prefix 'state/':")
        for k in keys:
            print(f"   {k}")

    if args.load is not None:
        data = load_state_from_r2(args.load)
        if data is None:
            print(f"❌ state_worker_{args.load} ABSENT de R2")
        else:
            print(f"✅ state_worker_{args.load} chargé depuis R2:")
            print(json.dumps(data, indent=2))

    if args.write_test:
        client = _get_r2_client()
        test_key = "state/_selftest.json"
        test_payload = {
            "selftest": True,
            "doctrine": "P22ΩΩ_EXTERNALISATION_R2_SELFTEST",
            "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }
        try:
            client.put_object(
                Bucket=_r2_bucket(),
                Key=test_key,
                Body=json.dumps(test_payload).encode("utf-8"),
                ContentType="application/json",
            )
            print(f"✅ WRITE test_key={test_key} OK")
            client.delete_object(Bucket=_r2_bucket(), Key=test_key)
            print(f"✅ DELETE test_key={test_key} OK (cleanup)")
            print("📋 R2 dual-write OPÉRATIONNEL · prêt pour bascule à froid")
        except Exception as e:
            print(f"❌ WRITE test échoué: {e}")
            sys.exit(2)

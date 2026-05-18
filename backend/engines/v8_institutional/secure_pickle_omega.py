"""
SECURE-PICKLE-Ω — Pickle sécurisé par HMAC-SHA256
==================================================

╔═══════════════════════════════════════════════════════════════════════════╗
║  P22ΩΩ_QUALITY_GROUPE_B · 2026-05-18 · COMMANDANT STEEVE-MAX             ║
║  Protocole : BCE-4X ULTIME ABSOLU                                         ║
╚═══════════════════════════════════════════════════════════════════════════╝

OBJET
─────
Module institutionnel pour pickle sécurisé. Toute serialisation/désérialisation
est authentifiée par HMAC-SHA256 afin de protéger contre :
  1. Compromission du filesystem (lecture de pickle disque)
  2. Compromission de Redis (lecture de payload sérialisé)
  3. Injection de payload malicieux dans le cache

ARCHITECTURE
────────────
Format wrapped (32 bytes HMAC + payload pickle) :
  ┌────────────────────────────────┬───────────────────────────────┐
  │  HMAC-SHA256 (32 bytes binary) │  pickle.dumps(obj) (variable) │
  └────────────────────────────────┴───────────────────────────────┘

Vérification AVANT pickle.loads :
  1. Lire 32 premiers bytes → HMAC attendu
  2. Calculer HMAC du reste avec clé secrète
  3. Comparer en TEMPS CONSTANT (hmac.compare_digest)
  4. Si mismatch → refus déserialisation + log warning

CLÉ SECRÈTE
───────────
Source en cascade :
  1. ENV var `PICKLE_HMAC_SECRET` (production) — recommandée
  2. Fichier `/app/backend/.secrets/pickle_hmac.key` (auto-généré si absent)
  3. Fallback dérivé (host-pinned) pour bootstrap initial

RETROCOMPATIBILITÉ
──────────────────
`secure_loads_legacy_tolerant()` accepte AUSSI les anciens pickles
non-signés (HMAC manquant). En cas de pickle legacy détecté, log
warning + déserialise + signale via flag `legacy=True` au caller
(qui peut re-signer au prochain save). Évite la perte du cache disque
existant lors du déploiement initial.

V30_LOCK : aucune modification de logique métier — uniquement
durcissement du transport pickle.
"""
from __future__ import annotations

import hmac
import hashlib
import os
import pickle  # nosec B403 — usage encapsulé avec HMAC, voir module-level doc
import secrets
import logging
from pathlib import Path
from typing import Any, Tuple

logger = logging.getLogger("bionic.secure_pickle_omega")

_HMAC_LENGTH_BYTES = 32  # SHA-256 = 32 bytes
_SECRET_FILE = Path("/app/backend/.secrets/pickle_hmac.key")
_SECRET_ENV_VAR = "PICKLE_HMAC_SECRET"

_cached_secret: bytes | None = None


def _load_or_create_secret() -> bytes:
    """Charge la clé HMAC depuis env > fichier > génère.

    Idempotent — cache la clé en mémoire après premier appel.
    """
    global _cached_secret
    if _cached_secret is not None:
        return _cached_secret

    # 1. Env var (production)
    env_secret = os.environ.get(_SECRET_ENV_VAR)
    if env_secret:
        _cached_secret = env_secret.encode("utf-8") if isinstance(env_secret, str) else env_secret
        return _cached_secret

    # 2. Fichier secret persistant
    try:
        if _SECRET_FILE.exists():
            data = _SECRET_FILE.read_bytes()
            if len(data) >= 32:
                _cached_secret = data
                return _cached_secret
    except Exception as e:
        logger.warning(f"[SECURE-PICKLE-Ω] Read secret file failed: {e}")

    # 3. Génération automatique (premier démarrage)
    try:
        _SECRET_FILE.parent.mkdir(parents=True, exist_ok=True)
        new_secret = secrets.token_bytes(64)  # 512 bits
        _SECRET_FILE.write_bytes(new_secret)
        # umask filesystem : lisible uniquement par owner
        try:
            os.chmod(_SECRET_FILE, 0o600)
        except Exception:
            pass
        _cached_secret = new_secret
        logger.info(
            f"[SECURE-PICKLE-Ω] HMAC secret generated and persisted to {_SECRET_FILE} (mode 0600)"
        )
        return _cached_secret
    except Exception as e:
        logger.warning(
            f"[SECURE-PICKLE-Ω] Cannot persist secret ({e}) — using host-pinned fallback"
        )

    # 4. Dernier recours : clé dérivée du hostname (non persistante)
    host_seed = (
        os.uname().nodename if hasattr(os, "uname") else "fallback"
    ).encode("utf-8")
    _cached_secret = hashlib.sha256(b"bce-4x-omega::" + host_seed).digest()
    return _cached_secret


def secure_dumps(obj: Any) -> bytes:
    """Sérialise `obj` en pickle + HMAC-SHA256 préfixé.

    Returns:
        bytes — 32 bytes HMAC suivi du pickle binaire
    """
    secret = _load_or_create_secret()
    payload = pickle.dumps(obj, protocol=pickle.HIGHEST_PROTOCOL)
    mac = hmac.new(secret, payload, hashlib.sha256).digest()
    return mac + payload


def secure_loads(data: bytes) -> Any:
    """Désérialise un pickle HMAC-signé. Refuse si HMAC invalide.

    Raises:
        ValueError: si data trop court ou HMAC mismatch
    """
    if not isinstance(data, (bytes, bytearray)) or len(data) <= _HMAC_LENGTH_BYTES:
        raise ValueError(
            f"[SECURE-PICKLE-Ω] payload too short ({len(data) if data else 0} bytes, "
            f"minimum {_HMAC_LENGTH_BYTES + 1})"
        )
    secret = _load_or_create_secret()
    mac_expected = data[:_HMAC_LENGTH_BYTES]
    payload = data[_HMAC_LENGTH_BYTES:]
    mac_actual = hmac.new(secret, payload, hashlib.sha256).digest()
    if not hmac.compare_digest(mac_expected, mac_actual):
        raise ValueError(
            "[SECURE-PICKLE-Ω] HMAC mismatch — payload tampered or wrong secret"
        )
    return pickle.loads(payload)  # nosec B301 — payload HMAC-vérifié ci-dessus


def secure_loads_legacy_tolerant(data: bytes) -> Tuple[Any, bool]:
    """Désérialise avec rétrocompatibilité legacy (pickle non-signé).

    Tente d'abord secure_loads ; en cas d'échec, tente pickle.loads sur
    le payload complet (cas migration premier déploiement).

    Returns:
        Tuple[Any, bool] — (objet, is_legacy_unsigned)
                            is_legacy_unsigned=True si payload n'avait pas de HMAC
    """
    try:
        return secure_loads(data), False
    except ValueError:
        # Tentative legacy : pickle non-signé (migration)
        try:
            obj = pickle.loads(data)  # nosec B301 — fallback migration uniquement
            logger.warning(
                "[SECURE-PICKLE-Ω] Legacy unsigned pickle detected — payload accepted "
                "but will be re-signed on next save (migration mode)"
            )
            return obj, True
        except Exception as e:
            raise ValueError(
                f"[SECURE-PICKLE-Ω] Neither HMAC-signed nor legacy pickle: {e}"
            ) from e


def is_secure_pickle_initialized() -> bool:
    """Diagnostic — la clé secrète est-elle chargée ?"""
    return _cached_secret is not None


def get_secret_source() -> str:
    """Diagnostic — d'où vient la clé (env / file / generated / fallback) ?"""
    if os.environ.get(_SECRET_ENV_VAR):
        return "env"
    if _SECRET_FILE.exists():
        return "file"
    return "generated_or_fallback"


__all__ = [
    "secure_dumps",
    "secure_loads",
    "secure_loads_legacy_tolerant",
    "is_secure_pickle_initialized",
    "get_secret_source",
]

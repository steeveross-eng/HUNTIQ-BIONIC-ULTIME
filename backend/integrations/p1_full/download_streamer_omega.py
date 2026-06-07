"""
download_streamer_omega.py — Module commun streaming + R2 sync + job store
═══════════════════════════════════════════════════════════════════════════════
P22ΩΩ_P1_FULL_DOWNLOAD_STREAMER_Ω · COMMANDANT STEEVE-MAX · 2026-06-07
BCE-4X ULTIME ABSOLU · Verrou Phase III · STRICT ADDITIF

Helpers communs P1_FULL pour streaming HTTP, retry exponentiel, sync R2 différé,
et job store thread-safe pour polling GET /job/{job_id}/status.

FONCTIONS PUBLIQUES :
  - download_with_retry(url, dest, auth, ...) → dict avec sha256, size, elapsed
  - sync_to_r2(local_path, r2_key) → upload R2 multipart
  - JobStore (thread-safe in-memory job state)

LIMITES SAFETY (configurables env) :
  - P1_MAX_TILES (défaut 3)
  - P1_MAX_SIZE_MB (défaut 500)
  - P1_TIMEOUT_S (défaut 300)
"""
from __future__ import annotations

import hashlib
import logging
import os
import threading
import time
import uuid
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Optional

import httpx

logger = logging.getLogger("bionic.p1_full.streamer")

# ─── Limites safety (env-configurable) ──────────────────────────────────────
P1_MAX_TILES = int(os.environ.get("P1_MAX_TILES", "3"))
P1_MAX_SIZE_MB = int(os.environ.get("P1_MAX_SIZE_MB", "500"))
P1_TIMEOUT_S = int(os.environ.get("P1_TIMEOUT_S", "300"))
P1_CHUNK_SIZE_BYTES = int(os.environ.get("P1_CHUNK_SIZE_BYTES", "1048576"))  # 1 MB

DEFAULT_DEST_BASE = Path(os.environ.get("P1_DEST_BASE", "/var/data/p1_ingest"))


# ─── Job store thread-safe ──────────────────────────────────────────────────
@dataclass
class TileResult:
    """Résultat unitaire pour 1 tuile/scene."""
    tile_id: str
    status: str  # queued | running | success | failed
    local_path: Optional[str] = None
    r2_key: Optional[str] = None
    size_bytes: Optional[int] = None
    sha256: Optional[str] = None
    elapsed_ms: Optional[int] = None
    error: Optional[str] = None


@dataclass
class JobStatus:
    """État job ingestion."""
    job_id: str
    client: str  # nasa_hls | esa_sentinel2_l2a | nrcan_hrdem | mffp_foret_ouverte
    status: str = "queued"  # queued | running | completed | failed | cancelled
    created_at_utc: str = ""
    started_at_utc: Optional[str] = None
    completed_at_utc: Optional[str] = None
    tiles_total: int = 0
    tiles_done: int = 0
    tiles_failed: int = 0
    bytes_downloaded: int = 0
    r2_synced: int = 0
    tiles: list[TileResult] = field(default_factory=list)
    params: dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        # bytes -> MB pour lisibilité
        d["bytes_downloaded_mb"] = round(self.bytes_downloaded / (1024 * 1024), 3)
        d["progress_pct"] = (
            round(self.tiles_done / self.tiles_total * 100, 1)
            if self.tiles_total else 0.0
        )
        return d


class JobStore:
    """Store in-memory thread-safe pour suivre les jobs en cours."""

    def __init__(self) -> None:
        self._jobs: dict[str, JobStatus] = {}
        self._lock = threading.Lock()

    def create(self, client: str, params: dict[str, Any], tiles_total: int) -> JobStatus:
        job = JobStatus(
            job_id=str(uuid.uuid4()),
            client=client,
            status="queued",
            created_at_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            tiles_total=tiles_total,
            params=params,
        )
        with self._lock:
            self._jobs[job.job_id] = job
        logger.info(f"[P1_JOB] created job_id={job.job_id} client={client} tiles_total={tiles_total}")
        return job

    def get(self, job_id: str) -> Optional[JobStatus]:
        with self._lock:
            return self._jobs.get(job_id)

    def update(self, job_id: str, **kwargs: Any) -> None:
        with self._lock:
            job = self._jobs.get(job_id)
            if not job:
                return
            for k, v in kwargs.items():
                if hasattr(job, k):
                    setattr(job, k, v)

    def append_tile(self, job_id: str, tile_result: TileResult) -> None:
        with self._lock:
            job = self._jobs.get(job_id)
            if not job:
                return
            job.tiles.append(tile_result)
            if tile_result.status == "success":
                job.tiles_done += 1
                if tile_result.size_bytes:
                    job.bytes_downloaded += tile_result.size_bytes
                if tile_result.r2_key:
                    job.r2_synced += 1
            elif tile_result.status == "failed":
                job.tiles_failed += 1

    def list_all(self, max_count: int = 50) -> list[dict[str, Any]]:
        with self._lock:
            jobs = list(self._jobs.values())
        jobs.sort(key=lambda j: j.created_at_utc, reverse=True)
        return [j.to_dict() for j in jobs[:max_count]]


# Singleton global (in-process · suffisant pour MVP P1_FULL)
_JOB_STORE_SINGLETON: Optional[JobStore] = None
_JOB_STORE_LOCK = threading.Lock()


def get_job_store() -> JobStore:
    global _JOB_STORE_SINGLETON
    if _JOB_STORE_SINGLETON is None:
        with _JOB_STORE_LOCK:
            if _JOB_STORE_SINGLETON is None:
                _JOB_STORE_SINGLETON = JobStore()
    return _JOB_STORE_SINGLETON


# ─── Download streaming avec retry ──────────────────────────────────────────
def download_with_retry(
    url: str,
    dest: Path,
    headers: Optional[dict[str, str]] = None,
    max_size_mb: Optional[int] = None,
    timeout_s: Optional[int] = None,
    max_attempts: int = 3,
) -> dict[str, Any]:
    """Download streaming chunked avec retry exponentiel + check taille + SHA256.

    Args:
        url: URL HTTP(S) à télécharger
        dest: Path destination locale (parent dir créé si besoin)
        headers: Auth/custom headers (ex Bearer token)
        max_size_mb: Refuse si > X MB (Content-Length pré-check)
        timeout_s: Timeout total
        max_attempts: Retries en cas d'échec

    Returns:
        dict {success, local_path, size_bytes, sha256, elapsed_ms, error}
    """
    max_size_mb = max_size_mb or P1_MAX_SIZE_MB
    timeout_s = timeout_s or P1_TIMEOUT_S
    max_size_bytes = max_size_mb * 1024 * 1024
    headers = headers or {}

    dest.parent.mkdir(parents=True, exist_ok=True)

    last_error: Optional[str] = None
    for attempt in range(1, max_attempts + 1):
        t0 = time.time()
        try:
            with httpx.Client(timeout=timeout_s, follow_redirects=True) as client:
                # HEAD pré-check si serveur le supporte
                try:
                    head = client.head(url, headers=headers)
                    if head.status_code == 200 or head.status_code == 302:
                        cl = head.headers.get("Content-Length")
                        if cl and int(cl) > max_size_bytes:
                            return {
                                "success": False,
                                "error": f"size {int(cl)} > max {max_size_bytes} (HEAD pre-check)",
                                "size_bytes": int(cl),
                                "elapsed_ms": int((time.time() - t0) * 1000),
                            }
                except Exception:
                    pass  # certains serveurs ne supportent pas HEAD

                # GET streaming
                sha = hashlib.sha256()
                size = 0
                tmp_path = dest.with_suffix(dest.suffix + ".partial")
                with client.stream("GET", url, headers=headers) as resp:
                    if resp.status_code != 200:
                        return {
                            "success": False,
                            "error": f"HTTP {resp.status_code}",
                            "elapsed_ms": int((time.time() - t0) * 1000),
                        }
                    with open(tmp_path, "wb") as f:
                        for chunk in resp.iter_bytes(P1_CHUNK_SIZE_BYTES):
                            if not chunk:
                                continue
                            f.write(chunk)
                            sha.update(chunk)
                            size += len(chunk)
                            if size > max_size_bytes:
                                f.close()
                                tmp_path.unlink(missing_ok=True)
                                return {
                                    "success": False,
                                    "error": f"size {size} > max {max_size_bytes} (streaming abort)",
                                    "size_bytes": size,
                                    "elapsed_ms": int((time.time() - t0) * 1000),
                                }
                tmp_path.replace(dest)
                return {
                    "success": True,
                    "local_path": str(dest),
                    "size_bytes": size,
                    "sha256": sha.hexdigest(),
                    "elapsed_ms": int((time.time() - t0) * 1000),
                    "attempt": attempt,
                }
        except httpx.RequestError as e:
            last_error = f"{type(e).__name__}: {e}"
            logger.warning(f"[P1_DL] attempt {attempt}/{max_attempts} failed for {url[:60]}: {last_error}")
            if attempt < max_attempts:
                time.sleep(2 ** attempt)  # exponential backoff
        except Exception as e:
            last_error = f"{type(e).__name__}: {e}"
            logger.warning(f"[P1_DL] unexpected error {url[:60]}: {last_error}")
            break

    return {"success": False, "error": last_error or "max_attempts_exhausted"}


# ─── Sync R2 différé ────────────────────────────────────────────────────────
def _get_r2_client_p1():
    """Lazy boto3 client pour R2 P1 (réutilise les credentials du dual-write state)."""
    cf_account_id = os.environ.get("CF_ACCOUNT_ID")
    r2_access_key = os.environ.get("R2_ACCESS_KEY_ID")
    r2_secret_key = os.environ.get("R2_SECRET_ACCESS_KEY")
    if not all([cf_account_id, r2_access_key, r2_secret_key]):
        return None
    try:
        import boto3
        from botocore.config import Config
        endpoint_url = f"https://{cf_account_id}.r2.cloudflarestorage.com"
        return boto3.client(
            "s3",
            endpoint_url=endpoint_url,
            aws_access_key_id=r2_access_key,
            aws_secret_access_key=r2_secret_key,
            config=Config(
                signature_version="s3v4",
                retries={"max_attempts": 3, "mode": "standard"},
                connect_timeout=10,
                read_timeout=300,
            ),
            region_name="auto",
        )
    except Exception as e:
        logger.warning(f"[P1_R2_SYNC] client init fail: {e}")
        return None


def sync_to_r2(local_path: Path, r2_key: str, content_type: str = "application/octet-stream") -> dict[str, Any]:
    """Upload local file vers R2 sous prefix ingestion_p1/.
    Multipart auto-géré par boto3 pour fichiers > ~8 MB.
    """
    client = _get_r2_client_p1()
    if client is None:
        return {"success": False, "error": "r2_client_unavailable"}

    bucket = os.environ.get("CF_R2_BUCKET", "bionic-zerocost-omega")
    t0 = time.time()
    try:
        client.upload_file(
            Filename=str(local_path),
            Bucket=bucket,
            Key=r2_key,
            ExtraArgs={
                "ContentType": content_type,
                "CacheControl": "public, max-age=86400",
                "Metadata": {
                    "doctrine": "P22-P1-FULL-PHASE-A",
                    "uploaded-at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                },
            },
        )
        return {
            "success": True,
            "r2_key": r2_key,
            "bucket": bucket,
            "elapsed_ms": int((time.time() - t0) * 1000),
        }
    except Exception as e:
        logger.warning(f"[P1_R2_SYNC] upload fail key={r2_key}: {e}")
        return {"success": False, "error": str(e)}

"""
mffp_resilient_pull_omega.py — ORDRE N°52-R14
═══════════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU · ANTI_GÉNÉRIQUE_STRICT

Pull résiliant via HTTP Range pour pee_maj.gpkg (~37 Go), conçu pour
résister aux pod restarts (3 occurrences confirmées au seuil 9.44 Go
lors des pulls "boto3 get_object stream" en une seule requête).

Stratégie :
  · Téléchargement par segments de 500 Mo via boto3 GetObject Range
  · Append vers fichier .pulling.partial (résiliant via taille fichier)
  · Reprise automatique : taille_existante → start_byte du prochain Range
  · Vérification SHA-256 finale vs manifest (cc4c9fd83…d4bb1b)
  · State file persistant /app/backend/data/gis_operational/PULL_RESILIENT_STATE.json
  · Background thread daemon

Avantages vs streaming get_object :
  · Aucune connexion HTTP de longue durée (chaque Range = ~10-20s max)
  · Reprise sans relire les bytes déjà persistés
  · Mémoire bornée (~500 Mo par segment)
═══════════════════════════════════════════════════════════════════════════
"""
from __future__ import annotations

import hashlib
import json
import logging
import os
import threading
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger("mffp_resilient_pull_omega")

# ═════════════════════════════════════════════════════════════════════════
# Constantes
# ═════════════════════════════════════════════════════════════════════════
RESILIENT_STATE_PATH = Path(
    "/app/backend/data/gis_operational/PULL_RESILIENT_STATE.json")
PEE_MAJ_LOCAL_DIR = Path(
    "/var/cache/gis_operational/incoming/FORET_MFFP_PEE_MAJ_Ω")
PEE_MAJ_LOCAL_PATH = PEE_MAJ_LOCAL_DIR / "pee_maj.gpkg"
PEE_MAJ_PARTIAL_PATH = PEE_MAJ_LOCAL_DIR / "pee_maj.pulling.partial"

# Segment de pull : 500 Mo (équilibre mémoire/débit)
SEGMENT_SIZE_BYTES = 500 * 1024 * 1024

# Retry par segment
MAX_RETRIES_PER_SEGMENT = 5
RETRY_BACKOFF_BASE_S = 2.0

_PULL_LOCK = threading.Lock()


# ═════════════════════════════════════════════════════════════════════════
# Helpers
# ═════════════════════════════════════════════════════════════════════════
def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _atomic_write_state(state: Dict[str, Any]) -> None:
    state["last_update_utc"] = _utc_now()
    RESILIENT_STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    tmp = RESILIENT_STATE_PATH.with_suffix(".partial")
    tmp.write_text(json.dumps(state, ensure_ascii=False, indent=2),
                    encoding="utf-8")
    os.replace(str(tmp), str(RESILIENT_STATE_PATH))


def read_resilient_state() -> Dict[str, Any]:
    if not RESILIENT_STATE_PATH.exists():
        return {}
    try:
        return json.loads(RESILIENT_STATE_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _get_b2_client_and_bucket():
    """Réutilise la config S3/B2 du routeur principal."""
    from routes.gis_s3_upload_router_omega import _get_b2_client
    return _get_b2_client()


def _get_pee_maj_b2_metadata() -> Dict[str, Any]:
    """Lit le manifest pour obtenir b2_key + sha256_attendu + taille."""
    manifest_path = Path(
        "/app/backend/data/gis_operational/GIS_RECEPTION_INTAKE_Ω.json")
    if not manifest_path.exists():
        raise RuntimeError("MANIFEST_NOT_FOUND")
    m = json.loads(manifest_path.read_text(encoding="utf-8"))
    slot = m["slots"]["FORET_MFFP_PEE_MAJ_Ω"]
    upload = next(
        (u for u in slot["uploads"]
         if u.get("filename") == "pee_maj.gpkg"
         and u.get("source") == "BACKBLAZE_B2_MULTIPART"),
        None)
    if not upload:
        raise RuntimeError("PEE_MAJ_UPLOAD_NOT_FOUND_IN_MANIFEST")
    return {
        "b2_bucket": upload["b2_bucket"],
        "b2_key": upload["b2_key"],
        "expected_sha256": upload["sha256"],
        "expected_size_bytes": upload["size_bytes"],
    }


def is_pee_maj_complete_and_valid() -> Dict[str, Any]:
    """Vérifie si pee_maj.gpkg final est présent + valide (taille + sha)."""
    if not PEE_MAJ_LOCAL_PATH.exists():
        return {"complete": False, "reason": "FILE_ABSENT"}
    meta = _get_pee_maj_b2_metadata()
    size = PEE_MAJ_LOCAL_PATH.stat().st_size
    if size != meta["expected_size_bytes"]:
        return {"complete": False, "reason": "SIZE_MISMATCH",
                "size_local": size,
                "expected_size": meta["expected_size_bytes"]}
    # SHA-256 vérification (avec fadvise pour ne pas peupler le pagecache)
    h = hashlib.sha256()
    bytes_hashed = 0
    with open(PEE_MAJ_LOCAL_PATH, "rb") as fh:
        fd = fh.fileno()
        try:
            os.posix_fadvise(fd, 0, 0, os.POSIX_FADV_SEQUENTIAL)
        except (AttributeError, OSError):
            pass
        while True:
            blk = fh.read(8 << 20)
            if not blk:
                break
            h.update(blk)
            bytes_hashed += len(blk)
            if bytes_hashed % (500 << 20) < (8 << 20):
                try:
                    os.posix_fadvise(
                        fd, 0, bytes_hashed, os.POSIX_FADV_DONTNEED)
                except (AttributeError, OSError):
                    pass
    sha = h.hexdigest()
    if sha != meta["expected_sha256"]:
        return {"complete": False, "reason": "SHA256_MISMATCH",
                "sha_local": sha, "expected_sha": meta["expected_sha256"]}
    return {"complete": True, "size_bytes": size, "sha256": sha}


def _generate_presigned_url(meta: Dict[str, Any],
                             expires_in_s: int = 14400) -> str:
    """Génère URL présignée HTTPS pour pull anonyme par curl (4h validité)."""
    s3, _bucket = _get_b2_client_and_bucket()
    return s3.generate_presigned_url(
        "get_object",
        Params={"Bucket": meta["b2_bucket"], "Key": meta["b2_key"]},
        ExpiresIn=expires_in_s,
    )


def _download_segment_via_curl(presigned_url: str, start: int, end: int,
                                tmp_seg_path: Path,
                                timeout_s: int = 240) -> int:
    """Télécharge bytes [start..end] (inclusif) via subprocess curl.

    Isolation mémoire : le process curl libère toute sa RAM en sortant.
    Aucun streaming via Python = aucune accumulation boto3/urllib3.

    Retourne le nombre d'octets reçus (vérifié par stat).
    Lève RuntimeError si curl échoue ou taille incorrecte.
    """
    import subprocess  # localisé pour éviter ImportError tests sans subprocess
    if tmp_seg_path.exists():
        tmp_seg_path.unlink()
    expected_bytes = end - start + 1
    range_header = f"bytes={start}-{end}"
    proc = subprocess.run(
        [
            "curl",
            "-fSs",  # fail on HTTP error · silent · show errors
            "--max-time", str(timeout_s),
            "--retry", "0",  # retries gérés au niveau supérieur
            "-H", f"Range: {range_header}",
            "-o", str(tmp_seg_path),
            presigned_url,
        ],
        check=False,
        capture_output=True,
        timeout=timeout_s + 30,
    )
    if proc.returncode != 0:
        stderr = (proc.stderr or b"").decode("utf-8", errors="replace")[:300]
        raise RuntimeError(
            f"CURL_FAIL rc={proc.returncode} range={range_header} "
            f"stderr={stderr}")
    if not tmp_seg_path.exists():
        raise RuntimeError(
            f"CURL_NO_OUTPUT range={range_header}")
    actual = tmp_seg_path.stat().st_size
    if actual != expected_bytes:
        raise RuntimeError(
            f"CURL_SIZE_MISMATCH range={range_header} "
            f"actual={actual} expected={expected_bytes}")
    return actual


def _append_tmp_segment_to_partial(tmp_seg_path: Path,
                                    partial_path: Path) -> None:
    """Append tmp_seg → partial via dd avec nocache (libère pagecache).

    CRITIQUE — anti-cgroup memory.max=8Go :
      · oflag=append,nocache : append + fadvise(DONTNEED) après écriture
      · iflag=nocache : fadvise(DONTNEED) sur tmp_seg après lecture
      · conv=notrunc : ne pas tronquer le fichier de destination
    """
    import subprocess
    proc = subprocess.run(
        ["dd",
         f"if={tmp_seg_path}",
         f"of={partial_path}",
         "bs=8M",
         "conv=notrunc",
         "iflag=nocache",
         "oflag=append,nocache",
         "status=none"],
        check=False, capture_output=True, timeout=300,
    )
    if proc.returncode != 0:
        stderr = (proc.stderr or b"").decode("utf-8", errors="replace")[:300]
        raise RuntimeError(f"DD_APPEND_FAIL rc={proc.returncode} "
                           f"stderr={stderr}")
    # En complément, fadvise(DONTNEED) sur le partial entier pour
    # évacuer toute page résiduelle du pagecache cumulée
    try:
        fd = os.open(str(partial_path), os.O_RDONLY)
        try:
            os.posix_fadvise(fd, 0, 0, os.POSIX_FADV_DONTNEED)
        finally:
            os.close(fd)
    except (AttributeError, OSError):
        pass


# ═════════════════════════════════════════════════════════════════════════
# Pull RÉSILIANT par RANGES (subprocess curl · isolation mémoire totale)
# ═════════════════════════════════════════════════════════════════════════
def _execute_resilient_pull(run_id: str) -> None:
    """Background thread : pull RANGE résiliant via subprocess curl.

    Stratégie anti-OOM Kubernetes (root cause après 4 incidents docs) :
      · boto3 stream `body.read()` accumule mémoire interne urllib3/SSL →
        OOM kill au cgroup pod à ~9-15 Go.
      · Solution : chaque segment est téléchargé par un PROCESSUS curl
        SÉPARÉ via URL présignée. La RAM du curl est libérée à sa sortie.
      · Le Python parent ne fait que des appels stat() + subprocess et
        écrit le state JSON. Mémoire bornée < 50 Mo.

    Pipeline par segment :
      1. curl -H "Range: ..." -> /var/cache/_seg.tmp
      2. vérif size (curl exit code + stat)
      3. cat /var/cache/_seg.tmp >> .pulling.partial (subprocess bash)
      4. rm /var/cache/_seg.tmp
      5. update state JSON (atomic)
    """
    import gc
    state = read_resilient_state()
    try:
        meta = _get_pee_maj_b2_metadata()
        state["b2_metadata"] = meta
        state["expected_size_bytes"] = meta["expected_size_bytes"]
        state["expected_sha256"] = meta["expected_sha256"]
        state["transport"] = "subprocess_curl_presigned_url"
        _atomic_write_state(state)

        # Vérif rapide : fichier final déjà OK ?
        check = is_pee_maj_complete_and_valid()
        if check["complete"]:
            logger.info("RESILIENT_PULL_SKIP file_already_complete")
            state["status"] = "OK_ALREADY_COMPLETE"
            state["completed_at_utc"] = _utc_now()
            _atomic_write_state(state)
            return

        # Création répertoire + démarrage offset
        PEE_MAJ_LOCAL_DIR.mkdir(parents=True, exist_ok=True)
        tmp_seg_path = PEE_MAJ_LOCAL_DIR / "_seg.tmp"
        if tmp_seg_path.exists():
            tmp_seg_path.unlink()

        start_offset = (
            PEE_MAJ_PARTIAL_PATH.stat().st_size
            if PEE_MAJ_PARTIAL_PATH.exists() else 0
        )
        total_size = meta["expected_size_bytes"]
        state["start_offset"] = start_offset
        state["total_size"] = total_size
        state["progress_pct"] = round(start_offset / total_size * 100, 2)
        _atomic_write_state(state)
        logger.info(
            "RESILIENT_PULL_START_CURL offset=%d total=%d progress=%.2f%%",
            start_offset, total_size, state["progress_pct"])

        # Génération URL présignée (4h validité)
        presigned_url = _generate_presigned_url(meta, expires_in_s=14400)
        state["presigned_url_generated_at_utc"] = _utc_now()
        state["presigned_url_expires_in_s"] = 14400
        _atomic_write_state(state)

        current = start_offset
        url_generated_at = time.time()

        while current < total_size:
            # Régénération URL si > 3h écoulées (safety margin sur 4h)
            if time.time() - url_generated_at > 10800:
                presigned_url = _generate_presigned_url(
                    meta, expires_in_s=14400)
                url_generated_at = time.time()
                state["presigned_url_regenerated_at_utc"] = _utc_now()

            range_end = min(current + SEGMENT_SIZE_BYTES - 1, total_size - 1)
            attempt = 0
            success = False
            while attempt < MAX_RETRIES_PER_SEGMENT and not success:
                attempt += 1
                try:
                    t0 = time.time()
                    bytes_in_segment = _download_segment_via_curl(
                        presigned_url, current, range_end, tmp_seg_path)
                    _append_tmp_segment_to_partial(
                        tmp_seg_path, PEE_MAJ_PARTIAL_PATH)
                    tmp_seg_path.unlink(missing_ok=True)
                    elapsed = round(time.time() - t0, 2)
                    current += bytes_in_segment
                    success = True
                    state["progress_pct"] = round(
                        current / total_size * 100, 2)
                    state["bytes_pulled"] = current
                    state["last_segment_bytes"] = bytes_in_segment
                    state["last_segment_elapsed_s"] = elapsed
                    state["segments_completed"] = (
                        int(state.get("segments_completed", 0)) + 1)
                    _atomic_write_state(state)
                    gc.collect()  # releve la RAM Python potentiellement accumulée
                    logger.info(
                        "RESILIENT_PULL_SEGMENT_CURL range=bytes=%d-%d "
                        "bytes=%d elapsed=%ss progress=%.2f%%",
                        current - bytes_in_segment, range_end,
                        bytes_in_segment, elapsed, state["progress_pct"])
                except Exception as e:
                    wait = RETRY_BACKOFF_BASE_S ** attempt
                    logger.warning(
                        "RESILIENT_PULL_RETRY_CURL range=bytes=%d-%d "
                        "attempt=%d/%d wait=%.1fs err=%s",
                        current, range_end, attempt,
                        MAX_RETRIES_PER_SEGMENT, wait, e)
                    # Si tmp_seg corrompu (taille partielle), purger
                    if tmp_seg_path.exists():
                        tmp_seg_path.unlink(missing_ok=True)
                    time.sleep(wait)
            if not success:
                state["status"] = "FAILED"
                state["error"] = (
                    f"SEGMENT_RETRIES_EXHAUSTED range=bytes={current}-"
                    f"{range_end}")
                _atomic_write_state(state)
                logger.error(
                    "RESILIENT_PULL_FAIL_SEGMENT_CURL range=bytes=%d-%d",
                    current, range_end)
                return

        # Vérif SHA-256 du fichier complet
        # Lecture explicite avec fadvise(DONTNEED) périodique pour
        # éviter de repeupler le pagecache à 37 Go (OOM kubernetes).
        logger.info("RESILIENT_PULL_VERIFY_SHA256")
        h = hashlib.sha256()
        bytes_hashed = 0
        with open(PEE_MAJ_PARTIAL_PATH, "rb") as fh:
            fd = fh.fileno()
            try:
                # Indique au kernel : lecture séquentielle (drop-after-read)
                os.posix_fadvise(fd, 0, 0, os.POSIX_FADV_SEQUENTIAL)
            except (AttributeError, OSError):
                pass
            while True:
                blk = fh.read(8 << 20)
                if not blk:
                    break
                h.update(blk)
                bytes_hashed += len(blk)
                # Toutes les 500 Mo lues, vide le pagecache
                if bytes_hashed % (500 << 20) < (8 << 20):
                    try:
                        os.posix_fadvise(
                            fd, 0, bytes_hashed, os.POSIX_FADV_DONTNEED)
                    except (AttributeError, OSError):
                        pass
        final_sha = h.hexdigest()
        state["sha256_computed"] = final_sha
        if final_sha != meta["expected_sha256"]:
            state["status"] = "FAILED"
            state["error"] = (
                f"SHA256_MISMATCH local={final_sha} "
                f"expected={meta['expected_sha256']}")
            _atomic_write_state(state)
            logger.error(
                "RESILIENT_PULL_SHA_MISMATCH local=%s expected=%s",
                final_sha, meta["expected_sha256"])
            return

        # Rename .partial → final
        os.replace(str(PEE_MAJ_PARTIAL_PATH), str(PEE_MAJ_LOCAL_PATH))
        state["status"] = "OK"
        state["completed_at_utc"] = _utc_now()
        state["final_path"] = str(PEE_MAJ_LOCAL_PATH)
        state["final_size_bytes"] = (
            PEE_MAJ_LOCAL_PATH.stat().st_size
            if PEE_MAJ_LOCAL_PATH.exists() else 0)
        _atomic_write_state(state)
        logger.info(
            "RESILIENT_PULL_DONE size=%d sha256=%s",
            state["final_size_bytes"], final_sha)
    except Exception as e:
        state["status"] = "FAILED"
        state["error"] = str(e)[:500]
        state["traceback"] = traceback.format_exc()[-1000:]
        _atomic_write_state(state)
        logger.exception("RESILIENT_PULL_EXCEPTION")
    finally:
        try:
            _PULL_LOCK.release()
        except RuntimeError:
            pass


def start_resilient_pull(force: bool = False) -> Dict[str, Any]:
    """Démarre le pull résiliant en background. Idempotent + zombie detection."""
    current = read_resilient_state()
    is_zombie = False
    if current.get("status") == "RUNNING":
        try:
            last = datetime.fromisoformat(current.get("last_update_utc", ""))
            age_s = (datetime.now(timezone.utc) - last).total_seconds()
            if age_s > 120:
                is_zombie = True
        except Exception:
            is_zombie = True
        if is_zombie:
            try:
                _PULL_LOCK.release()
            except RuntimeError:
                pass
            current["status"] = "ZOMBIE_POD_RESTART"
            _atomic_write_state(current)

    if not _PULL_LOCK.acquire(blocking=False):
        return {"ok": False, "reason": "ALREADY_RUNNING",
                "current_state": read_resilient_state()}
    current = read_resilient_state()
    if current.get("status") == "RUNNING" and not force:
        _PULL_LOCK.release()
        return {"ok": False, "reason": "ALREADY_RUNNING",
                "current_state": current}

    run_id = f"PULL_{int(time.time())}_{os.urandom(3).hex()}"
    state = {
        "run_id": run_id,
        "status": "RUNNING",
        "started_at_utc": _utc_now(),
        "last_update_utc": _utc_now(),
        "ordre": "N°52-R14",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "previous_run_was_zombie": is_zombie,
        "segment_size_bytes": SEGMENT_SIZE_BYTES,
        "segments_completed": 0,
    }
    _atomic_write_state(state)

    t = threading.Thread(
        target=_execute_resilient_pull, args=(run_id,),
        name=f"PULL-{run_id}", daemon=True)
    t.start()
    return {
        "ok": True,
        "run_id": run_id,
        "status": "RUNNING",
        "started_at_utc": state["started_at_utc"],
        "previous_run_was_zombie": is_zombie,
    }


__all__ = [
    "start_resilient_pull",
    "read_resilient_state",
    "is_pee_maj_complete_and_valid",
    "PEE_MAJ_LOCAL_PATH",
    "PEE_MAJ_PARTIAL_PATH",
    "RESILIENT_STATE_PATH",
    "SEGMENT_SIZE_BYTES",
]

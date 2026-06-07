"""
zerocost_workers_runtime.py — Runtime In-Process Launcher for β2-ΣΤ Workers
═══════════════════════════════════════════════════════════════════════════
P22ΩΩ_DEPLOYED_WORKERS_INPROCESS_Ω · STEEVE-MAX · 2026-05-22 · BCE-4X ULTIME ABSOLU

OBJECTIF
--------
Permettre au backend FastAPI de **démarrer et superviser les 6 workers β2-ΣΤ
directement dans le pod déployé**, sans dépendre du supervisor managed externe.

DOCTRINE
--------
- Module purement additif (Verrou Phase III maintenu).
- Auto-détection Preview vs Deployed (skip si supervisor externe déjà actif).
- Worker-launch + watchdog asyncio interne (boucle 60 s).
- Soft-fail strict : aucune exception ne bloque le boot backend.
- Idempotent : vérifie à chaque check si workers vivants avant relance.

ENV VARS (optionnelles)
-----------------------
ZEROCOST_INPROCESS_DISABLE=1            → désactivation explicite (override)
ZEROCOST_INPROCESS_FORCE=1              → force le lancement même si supervisor détecté
ZEROCOST_INPROCESS_WORKER_COUNT=6       → nombre de workers (défaut: 6)
ZEROCOST_INPROCESS_CHECK_INTERVAL_S=60  → période watchdog (défaut: 60 s)
ZEROCOST_INPROCESS_MIN_WORKERS=3        → seuil de relance (défaut: 3)
ZEROCOST_GRID_FILE_PATH                 → chemin grille R5 SEED (défaut: cache/zerocost_v1/...)

R2 CREDENTIALS REQUIS (vérifiés au démarrage)
---------------------------------------------
R2_S3_ENDPOINT, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY, CF_R2_BUCKET
"""
from __future__ import annotations

import asyncio
import logging
import os
import shutil
import signal
import subprocess
import sys
from pathlib import Path
from typing import Optional

logger = logging.getLogger("bionic.zerocost_workers_runtime")

# ─────────────────────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────────────────────
_BACKEND_ROOT = Path("/app/backend")
_WORKER_SCRIPT = _BACKEND_ROOT / "tools" / "zerocost_worker_seed_r5.py"
_DEFAULT_GRID_FILE = _BACKEND_ROOT / "cache" / "zerocost_v1" / "canada_h3_grid_r5_seed.json"
_DEFAULT_LOG_DIR = Path("/var/log/bionic-zerocost-seed-r5")

_REQUIRED_R2_ENV = (
    "R2_S3_ENDPOINT",
    "R2_ACCESS_KEY_ID",
    "R2_SECRET_ACCESS_KEY",
    "CF_R2_BUCKET",
)

# Runtime state
_pids: list[int] = []
_watchdog_task: Optional[asyncio.Task] = None
_stop_event: Optional[asyncio.Event] = None


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────
def _is_pid_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
        return True
    except (OSError, ProcessLookupError):
        return False


def _detect_external_supervisor() -> bool:
    """Detect if an external supervisor already manages β2-ΣΤ workers (Preview case).

    Returns True if ≥3 zerocost_worker_seed_r5 processes are already running
    that we did NOT spawn ourselves.
    """
    try:
        result = subprocess.run(
            ["pgrep", "-fa", "zerocost_worker_seed_r5"],
            capture_output=True, text=True, timeout=3,
        )
        lines = [ln for ln in result.stdout.strip().splitlines() if ln]
        # Filter our own children (PIDs we tracked)
        external_lines = []
        for ln in lines:
            try:
                pid = int(ln.split()[0])
                if pid not in _pids:
                    external_lines.append(pid)
            except (ValueError, IndexError):
                continue
        return len(external_lines) >= 3
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False
    except Exception as e:
        logger.debug(f"[β2-ΣΤ-INPROCESS] external supervisor detection failed: {e}")
        return False


def _check_r2_credentials() -> tuple[bool, list[str]]:
    missing = [k for k in _REQUIRED_R2_ENV if not os.environ.get(k)]
    return (len(missing) == 0, missing)


def _resolve_grid_file() -> Path:
    custom = os.environ.get("ZEROCOST_GRID_FILE_PATH")
    if custom:
        p = Path(custom)
        if p.is_file():
            return p
    return _DEFAULT_GRID_FILE


def _resolve_python_bin() -> str:
    venv_bin = "/root/.venv/bin/python3"
    if Path(venv_bin).is_file():
        return venv_bin
    return shutil.which("python3") or sys.executable


def _spawn_worker(worker_index: int, worker_count: int,
                  grid_file: Path, log_dir: Path, python_bin: str) -> Optional[int]:
    """Spawn a single β2-ΣΤ worker subprocess detached from the FastAPI process."""
    log_path = log_dir / f"worker_{worker_index}.log"
    try:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        log_fh = open(log_path, "ab", buffering=0)
        env = os.environ.copy()
        env.update({
            "GRID_FILE_PATH": str(grid_file),
            "WORKER_INDEX": str(worker_index),
            "WORKER_COUNT": str(worker_count),
            "MAX_R5_CELLS": env.get("MAX_R5_CELLS", "0"),
            "PYTHONUNBUFFERED": "1",
        })
        proc = subprocess.Popen(
            ["nice", "-n", "19", python_bin, str(_WORKER_SCRIPT)],
            cwd=str(_BACKEND_ROOT),
            env=env,
            stdout=log_fh, stderr=log_fh, stdin=subprocess.DEVNULL,
            start_new_session=True,  # PPID detachment (équivalent setsid + disown)
        )
        return proc.pid
    except Exception as e:
        logger.warning(f"[β2-ΣΤ-INPROCESS] worker {worker_index} spawn failed: {e}")
        return None


def _spawn_all_workers(worker_count: int) -> list[int]:
    grid_file = _resolve_grid_file()
    log_dir = _DEFAULT_LOG_DIR
    python_bin = _resolve_python_bin()
    if not grid_file.is_file():
        logger.warning(
            f"[β2-ΣΤ-INPROCESS] grid file introuvable ({grid_file}) · "
            f"skip launch (le pod déployé doit copier la grille canonique)"
        )
        return []
    if not _WORKER_SCRIPT.is_file():
        logger.warning(f"[β2-ΣΤ-INPROCESS] worker script introuvable: {_WORKER_SCRIPT}")
        return []

    # P22ΩΩ_SPAWN_STAGGER_INPROCESS_Ω · 2026-06-07 · STEEVE-MAX · BCE-4X ULTIME ABSOLU
    # Démarrage étagé des workers (additif strict · Verrou Phase III intact).
    # Lecture SPAWN_STAGGER_MS depuis l'env : pause time.sleep(stagger_ms/1000)
    # entre chaque spawn pour lisser le pic CPU initial (bootstrap V20 parallèle
    # = spike ~400% CPU pendant 3-5s qui peut déclencher probes liveness fail
    # sur pod CPU-quota strict). Comportement legacy 100% préservé si var absente
    # ou = 0 : aucun délai inséré, spawn back-to-back comme avant.
    # ZEROCOST_WORKER_SPAWN_LOGGING=1 active le log détaillé par worker.
    try:
        _stagger_ms = int(os.environ.get("SPAWN_STAGGER_MS", "0"))
    except (TypeError, ValueError):
        _stagger_ms = 0
    _verbose_spawn = os.environ.get("ZEROCOST_WORKER_SPAWN_LOGGING", "0").strip() in ("1", "true", "yes")

    if _stagger_ms > 0:
        logger.info(
            f"[β2-ΣΤ-INPROCESS] SPAWN_STAGGER actif · {_stagger_ms}ms entre workers · "
            f"spread total ~{_stagger_ms * (worker_count - 1) / 1000:.1f}s"
        )

    import time as _time  # local import · zéro impact si stagger_ms == 0

    pids: list[int] = []
    for i in range(worker_count):
        pid = _spawn_worker(i, worker_count, grid_file, log_dir, python_bin)
        if pid:
            pids.append(pid)
            if _verbose_spawn:
                logger.info(
                    f"[β2-ΣΤ-INPROCESS] worker {i} spawned · PID {pid} · nice 19 · "
                    f"WORKER_PACING_MS={os.environ.get('WORKER_PACING_MS', '0')} · "
                    f"stagger_remaining_ms={_stagger_ms if i < worker_count - 1 else 0}"
                )
            else:
                logger.info(f"[β2-ΣΤ-INPROCESS] worker {i} spawned · PID {pid} · nice 19")
        # Stagger entre workers (sauf après le dernier) si activé
        if _stagger_ms > 0 and i < worker_count - 1:
            try:
                _time.sleep(_stagger_ms / 1000.0)
            except Exception as e:
                logger.warning(f"[β2-ΣΤ-INPROCESS] stagger sleep interrupted: {e}")
    return pids


def _terminate_workers(pids: list[int], grace_s: float = 3.0) -> None:
    for pid in pids:
        if _is_pid_alive(pid):
            try:
                os.kill(pid, signal.SIGTERM)
            except Exception:
                pass
    # Grace period
    try:
        import time as _t
        _t.sleep(grace_s)
    except Exception:
        pass
    for pid in pids:
        if _is_pid_alive(pid):
            try:
                os.kill(pid, signal.SIGKILL)
            except Exception:
                pass


# ─────────────────────────────────────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────────────────────────────────────
async def start_zerocost_workers_inprocess() -> None:
    """Launch 6 β2-ΣΤ workers and start the asyncio watchdog loop.

    Idempotent · soft-fail · respects external supervisor.
    """
    global _pids, _watchdog_task, _stop_event

    # 1) Explicit disable check
    if os.environ.get("ZEROCOST_INPROCESS_DISABLE", "").strip() in ("1", "true", "yes"):
        logger.info("[β2-ΣΤ-INPROCESS] désactivé par ZEROCOST_INPROCESS_DISABLE=1")
        return

    # 2) Already started in this process?
    if _watchdog_task is not None and not _watchdog_task.done():
        logger.info("[β2-ΣΤ-INPROCESS] watchdog déjà actif (skip duplicate start)")
        return

    # 3) External supervisor detection (Preview case)
    force = os.environ.get("ZEROCOST_INPROCESS_FORCE", "").strip() in ("1", "true", "yes")
    if not force and _detect_external_supervisor():
        logger.info(
            "[β2-ΣΤ-INPROCESS] supervisor externe détecté (≥3 workers actifs) · "
            "skip launch in-process pour éviter doublon (Preview / Emergent supervisor)"
        )
        return

    # 4) R2 credentials check
    ok, missing = _check_r2_credentials()
    if not ok:
        logger.warning(
            f"[β2-ΣΤ-INPROCESS] R2 credentials manquantes : {missing} · "
            f"skip launch (workers nécessitent R2 pour upload)"
        )
        return

    # 5) Spawn workers
    worker_count = int(os.environ.get("ZEROCOST_INPROCESS_WORKER_COUNT", "6"))
    logger.info(
        f"[β2-ΣΤ-INPROCESS] launching {worker_count} workers β2-ΣΤ "
        f"(deployed runtime · backend-managed watchdog)"
    )
    _pids = _spawn_all_workers(worker_count)
    if not _pids:
        logger.warning("[β2-ΣΤ-INPROCESS] aucun worker n'a pu être lancé · watchdog non démarré")
        return

    # 6) Start asyncio watchdog
    _stop_event = asyncio.Event()
    _watchdog_task = asyncio.create_task(_watchdog_loop(worker_count))
    logger.info(
        f"[β2-ΣΤ-INPROCESS] ✓ {len(_pids)}/{worker_count} workers spawned · "
        f"asyncio watchdog started (PIDs: {_pids})"
    )


async def stop_zerocost_workers_inprocess(grace_s: float = 5.0) -> None:
    """Stop watchdog and terminate workers cleanly at shutdown."""
    global _pids, _watchdog_task, _stop_event

    if _stop_event is not None:
        _stop_event.set()

    if _watchdog_task is not None and not _watchdog_task.done():
        try:
            await asyncio.wait_for(_watchdog_task, timeout=grace_s)
        except (asyncio.TimeoutError, asyncio.CancelledError):
            _watchdog_task.cancel()
        except Exception as e:
            logger.warning(f"[β2-ΣΤ-INPROCESS] watchdog stop error: {e}")

    if _pids:
        logger.info(f"[β2-ΣΤ-INPROCESS] terminating {len(_pids)} workers · graceful SIGTERM")
        _terminate_workers(list(_pids))
        _pids = []

    _watchdog_task = None
    _stop_event = None


# ─────────────────────────────────────────────────────────────────────────────
# Watchdog loop (in-process equivalent of supervisor watchdog)
# ─────────────────────────────────────────────────────────────────────────────
async def _watchdog_loop(worker_count: int) -> None:
    """Periodic liveness check · respawns dead workers · runs until stop_event."""
    global _pids

    check_interval = int(os.environ.get("ZEROCOST_INPROCESS_CHECK_INTERVAL_S", "60"))
    min_workers = int(os.environ.get("ZEROCOST_INPROCESS_MIN_WORKERS", "3"))
    heartbeat_every_n = 5  # log workers=N OK toutes les 5 itérations (~5 min)
    iter_count = 0

    try:
        while _stop_event is not None and not _stop_event.is_set():
            try:
                await asyncio.wait_for(_stop_event.wait(), timeout=check_interval)
                break  # stop_event was set
            except asyncio.TimeoutError:
                pass  # normal periodic tick

            # Count alive workers
            alive_pids = [p for p in _pids if _is_pid_alive(p)]
            n_alive = len(alive_pids)
            iter_count += 1

            if n_alive < min_workers:
                logger.warning(
                    f"[β2-ΣΤ-INPROCESS-WATCHDOG] workers vivants={n_alive} < MIN={min_workers} · RELANCE"
                )
                # Kill any zombie/stale workers
                _terminate_workers(_pids, grace_s=2.0)
                _pids = _spawn_all_workers(worker_count)
                logger.info(
                    f"[β2-ΣΤ-INPROCESS-WATCHDOG] relance terminée · {len(_pids)}/{worker_count} actifs · "
                    f"PIDs: {_pids}"
                )
            else:
                if iter_count % heartbeat_every_n == 0:
                    try:
                        load_avg = os.getloadavg()[0]
                    except Exception:
                        load_avg = -1.0
                    logger.info(
                        f"[β2-ΣΤ-INPROCESS-WATCHDOG] workers={n_alive}/{worker_count} OK · "
                        f"load={load_avg:.2f}"
                    )
                # Partial recovery : si n_alive entre min et target, respawn manquants
                if n_alive < worker_count:
                    # Identifier les indices manquants (alphabetic order best-effort)
                    # Pour simplicité : on relance tout si <worker_count mais ≥min
                    # uniquement après 3 itérations consécutives partielles
                    pass  # tolérance : on ne relance pas tant que ≥ min
    except asyncio.CancelledError:
        logger.info("[β2-ΣΤ-INPROCESS-WATCHDOG] cancelled")
    except Exception as e:
        logger.error(f"[β2-ΣΤ-INPROCESS-WATCHDOG] crashed: {e}", exc_info=True)
    finally:
        logger.info("[β2-ΣΤ-INPROCESS-WATCHDOG] stopped")

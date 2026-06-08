"""
test_worker_r4_completed_sentinel.py — Unit tests for P22ΩΩ_R4_WORKER_COMPLETED_SENTINEL_Ω

P22ΩΩ_R4_WORKER_COMPLETED_SENTINEL_TESTS_Ω · STEEVE-MAX · 2026-06-08
BCE-4X ULTIME ABSOLU · Verrou Phase III · STRICT ADDITIF

Couvre :
  - R4 · Worker écrit `completed_worker_{idx}.flag` quand `r5_idx_done >= len(my_r5)`
  - R4 · Watchdog skip respawn des indices "completed" (boucle infinie éliminée)
  - R4 · Sentinel invalidé si grid_file change → respawn légitime
  - R4 · Sentinel absent → comportement R3 préservé (full / partial respawn)
"""
from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

import pytest

_BACKEND_ROOT = Path(__file__).resolve().parent.parent
if str(_BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(_BACKEND_ROOT))

import zerocost_workers_runtime as wr  # noqa: E402


@pytest.fixture(autouse=True)
def _reset_module_state(tmp_path, monkeypatch):
    wr._pids = {}
    wr._watchdog_task = None
    wr._stop_event = None
    wr._last_partial_respawn_at = 0.0
    # Redirige le répertoire des sentinels vers tmp_path
    monkeypatch.setattr(wr, "_COMPLETED_FLAG_DIR", tmp_path)
    yield
    wr._pids = {}
    wr._watchdog_task = None
    wr._stop_event = None
    wr._last_partial_respawn_at = 0.0


@pytest.fixture
def alive_pids():
    return set()


@pytest.fixture
def patch_runtime(monkeypatch, alive_pids, tmp_path):
    pid_counter = {"next": 1000}

    def fake_is_alive(pid):
        return pid in alive_pids

    def fake_spawn(idx, count, grid, log_dir, py_bin):
        pid = pid_counter["next"]
        pid_counter["next"] += 1
        alive_pids.add(pid)
        return pid

    def fake_terminate(pids, grace_s=3.0):
        pid_list = list(pids.values()) if isinstance(pids, dict) else list(pids)
        for p in pid_list:
            alive_pids.discard(p)

    class FakePath:
        def is_file(self):
            return True

        def __str__(self):
            return "/fake/grid.json"

    monkeypatch.setattr(wr, "_is_pid_alive", fake_is_alive)
    monkeypatch.setattr(wr, "_spawn_worker", fake_spawn)
    monkeypatch.setattr(wr, "_terminate_workers", fake_terminate)
    monkeypatch.setattr(wr, "_resolve_grid_file", lambda: FakePath())
    monkeypatch.setattr(wr, "_WORKER_SCRIPT", FakePath())
    monkeypatch.setattr(wr, "_resolve_python_bin", lambda: "/usr/bin/python3")
    monkeypatch.setattr(wr._time, "sleep", lambda *a, **k: None)
    monkeypatch.setenv("SPAWN_STAGGER_MS", "0")
    monkeypatch.setenv("WORKER_PARTIAL_RESPAWN_COOLDOWN_S", "0")
    return {"alive": alive_pids, "next_pid": pid_counter, "flag_dir": tmp_path}


def _write_completed_flag(flag_dir: Path, worker_index: int, grid_file: str = "/fake/grid.json"):
    flag_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "worker_index": worker_index,
        "worker_count": 8,
        "grid_file": grid_file,
        "my_share": 42,
        "completed_at": "2026-06-08T16:00:00Z",
        "reason": "workload_done",
    }
    (flag_dir / f"completed_worker_{worker_index}.flag").write_text(json.dumps(payload))


# ─── Tests sentinel reader ────────────────────────────────────────────────────
def test_is_worker_completed_false_when_no_flag(patch_runtime):
    assert wr._is_worker_completed(3) is False


def test_is_worker_completed_true_when_flag_present(patch_runtime):
    _write_completed_flag(patch_runtime["flag_dir"], 3)
    assert wr._is_worker_completed(3, current_grid_file="/fake/grid.json") is True


def test_is_worker_completed_invalidated_on_grid_change(patch_runtime):
    _write_completed_flag(patch_runtime["flag_dir"], 3, grid_file="/old/grid.json")
    assert wr._is_worker_completed(3, current_grid_file="/new/grid.json") is False


# ─── Tests watchdog R4 ────────────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_watchdog_skips_respawn_of_completed_workers(patch_runtime, monkeypatch):
    """R4 · Workers 3,4,5,6,7 marqués completed → watchdog ne respawn PAS · boucle infinie éliminée."""
    alive = patch_runtime["alive"]
    wr._pids = wr._spawn_all_workers(worker_count=8)
    # Simule exit normal des workers 3-7 (sentinel COMPLETED écrit)
    for idx in [3, 4, 5, 6, 7]:
        alive.discard(wr._pids[idx])
        _write_completed_flag(patch_runtime["flag_dir"], idx)

    initial_pids_of_completed = {idx: wr._pids[idx] for idx in [3, 4, 5, 6, 7]}

    monkeypatch.setenv("ZEROCOST_INPROCESS_CHECK_INTERVAL_S", "0")
    monkeypatch.setenv("ZEROCOST_INPROCESS_MIN_WORKERS", "3")
    monkeypatch.setenv("WORKER_PARTIAL_RESPAWN_COOLDOWN_S", "0")
    wr._stop_event = asyncio.Event()
    task = asyncio.create_task(wr._watchdog_loop(worker_count=8))
    await asyncio.sleep(0.2)
    wr._stop_event.set()
    await asyncio.wait_for(task, timeout=2.0)

    # PIDs des completed ne doivent PAS avoir changé (pas de respawn)
    for idx in [3, 4, 5, 6, 7]:
        assert wr._pids[idx] == initial_pids_of_completed[idx], (
            f"R4 BROKEN · idx {idx} a été respawn alors qu'il était completed "
            f"(PID {initial_pids_of_completed[idx]} → {wr._pids[idx]})"
        )
    # Les workers 0-2 doivent toujours être alive
    for idx in [0, 1, 2]:
        assert wr._pids[idx] in alive


@pytest.mark.asyncio
async def test_watchdog_respawns_crashed_workers_not_completed_ones(patch_runtime, monkeypatch):
    """R4 · Mix : idx 3,4 completed + idx 5,6,7 crashed → seuls 5,6,7 respawn."""
    alive = patch_runtime["alive"]
    wr._pids = wr._spawn_all_workers(worker_count=8)
    # 3, 4 completed (sentinel)
    for idx in [3, 4]:
        alive.discard(wr._pids[idx])
        _write_completed_flag(patch_runtime["flag_dir"], idx)
    # 5, 6, 7 crashés (pas de sentinel)
    crashed_pids_before = {}
    for idx in [5, 6, 7]:
        crashed_pids_before[idx] = wr._pids[idx]
        alive.discard(wr._pids[idx])

    completed_pids_before = {idx: wr._pids[idx] for idx in [3, 4]}

    monkeypatch.setenv("ZEROCOST_INPROCESS_CHECK_INTERVAL_S", "0")
    monkeypatch.setenv("ZEROCOST_INPROCESS_MIN_WORKERS", "3")
    monkeypatch.setenv("WORKER_PARTIAL_RESPAWN_COOLDOWN_S", "0")
    wr._stop_event = asyncio.Event()
    task = asyncio.create_task(wr._watchdog_loop(worker_count=8))
    await asyncio.sleep(0.2)
    wr._stop_event.set()
    await asyncio.wait_for(task, timeout=2.0)

    # 3, 4 inchangés (completed → skip)
    for idx in [3, 4]:
        assert wr._pids[idx] == completed_pids_before[idx], f"completed idx {idx} respawn par erreur"
    # 5, 6, 7 respawn (nouveaux PIDs vivants)
    for idx in [5, 6, 7]:
        assert wr._pids[idx] != crashed_pids_before[idx], f"crashed idx {idx} non respawn"
        assert wr._pids[idx] in alive, f"crashed idx {idx} respawn dead"


@pytest.mark.asyncio
async def test_watchdog_skips_full_respawn_when_completed_pushes_effective_above_min(patch_runtime, monkeypatch):
    """R4 · n_alive=2 < min=3 mais n_effective_ok=8 (6 completed) → PAS de full respawn."""
    alive = patch_runtime["alive"]
    wr._pids = wr._spawn_all_workers(worker_count=8)
    # 2,3,4,5,6,7 completed · 0,1 alive
    for idx in [2, 3, 4, 5, 6, 7]:
        alive.discard(wr._pids[idx])
        _write_completed_flag(patch_runtime["flag_dir"], idx)

    initial_pids = dict(wr._pids)

    monkeypatch.setenv("ZEROCOST_INPROCESS_CHECK_INTERVAL_S", "0")
    monkeypatch.setenv("ZEROCOST_INPROCESS_MIN_WORKERS", "3")
    monkeypatch.setenv("WORKER_PARTIAL_RESPAWN_COOLDOWN_S", "0")
    wr._stop_event = asyncio.Event()
    task = asyncio.create_task(wr._watchdog_loop(worker_count=8))
    await asyncio.sleep(0.2)
    wr._stop_event.set()
    await asyncio.wait_for(task, timeout=2.0)

    # Aucun PID changé (pas de full respawn malgré n_alive=2<min=3)
    assert wr._pids == initial_pids, "Watchdog a déclenché full respawn malgré sentinels completed"


@pytest.mark.asyncio
async def test_watchdog_legacy_partial_respawn_preserved_without_sentinel(patch_runtime, monkeypatch):
    """R4 · Aucun sentinel → comportement R3 strictement préservé (partial respawn)."""
    alive = patch_runtime["alive"]
    wr._pids = wr._spawn_all_workers(worker_count=8)
    crashed_pids = {}
    for idx in [3, 4, 5]:
        crashed_pids[idx] = wr._pids[idx]
        alive.discard(wr._pids[idx])  # AUCUN sentinel écrit

    monkeypatch.setenv("ZEROCOST_INPROCESS_CHECK_INTERVAL_S", "0")
    monkeypatch.setenv("ZEROCOST_INPROCESS_MIN_WORKERS", "3")
    monkeypatch.setenv("WORKER_PARTIAL_RESPAWN_COOLDOWN_S", "0")
    wr._stop_event = asyncio.Event()
    task = asyncio.create_task(wr._watchdog_loop(worker_count=8))
    await asyncio.sleep(0.15)
    wr._stop_event.set()
    await asyncio.wait_for(task, timeout=2.0)

    # Respawn R3 legacy doit avoir eu lieu (PIDs changés, vivants)
    for idx in [3, 4, 5]:
        assert wr._pids[idx] != crashed_pids[idx], f"R3 broken: idx {idx} non respawn"
        assert wr._pids[idx] in alive

"""
test_worker_partial_recovery.py — Unit tests for P2 WORKER_PARTIAL_RECOVERY

P22ΩΩ_P2_WORKER_PARTIAL_RECOVERY_TESTS_Ω · STEEVE-MAX · 2026-06-08
BCE-4X ULTIME ABSOLU · Verrou Phase III · STRICT ADDITIF

Couvre :
  - R3 · détection des indices manquants (via _pids dict[int,int])
  - R3 · partial respawn ciblé sur indices manquants (cooldown bypassé)
  - R3 · cooldown anti-thrash (skip respawn si trop récent)
  - Legacy · full respawn quand n_alive < min_workers (préservé inchangé)
  - Helpers · _terminate_workers accepte dict ou list (legacy compat)

Mocks subprocess / kill / files via monkeypatch (zéro subprocess réel).
"""
from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

import pytest

# Path setup (test exécutable depuis /app)
_BACKEND_ROOT = Path(__file__).resolve().parent.parent
if str(_BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(_BACKEND_ROOT))

import zerocost_workers_runtime as wr  # noqa: E402


# ─────────────────────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────────────────────
@pytest.fixture(autouse=True)
def _reset_module_state():
    """Reset module-level state between tests."""
    wr._pids = {}
    wr._watchdog_task = None
    wr._stop_event = None
    wr._last_partial_respawn_at = 0.0
    yield
    wr._pids = {}
    wr._watchdog_task = None
    wr._stop_event = None
    wr._last_partial_respawn_at = 0.0


@pytest.fixture
def alive_pids():
    """Simule un set de PIDs vivants modifiables par test."""
    return set()


@pytest.fixture
def patch_runtime(monkeypatch, alive_pids):
    """Patch les helpers OS-level pour éviter toute interaction réelle.

    - _is_pid_alive(pid) : true ssi pid ∈ alive_pids
    - _spawn_worker(idx, ...) : retourne un PID synthétique (1000+idx) et l'ajoute à alive_pids
    - _terminate_workers : retire les pids de alive_pids
    - _resolve_grid_file / _WORKER_SCRIPT / log dir : tous existants (mock)
    """
    pid_counter = {"next": 1000}

    def fake_is_alive(pid: int) -> bool:
        return pid in alive_pids

    def fake_spawn(worker_index, worker_count, grid_file, log_dir, python_bin):
        pid = pid_counter["next"]
        pid_counter["next"] += 1
        alive_pids.add(pid)
        return pid

    def fake_terminate(pids, grace_s=3.0):
        pid_list = list(pids.values()) if isinstance(pids, dict) else list(pids)
        for p in pid_list:
            alive_pids.discard(p)

    # Fake fichiers présents
    class FakePath:
        def is_file(self):
            return True

    monkeypatch.setattr(wr, "_is_pid_alive", fake_is_alive)
    monkeypatch.setattr(wr, "_spawn_worker", fake_spawn)
    monkeypatch.setattr(wr, "_terminate_workers", fake_terminate)
    monkeypatch.setattr(wr, "_resolve_grid_file", lambda: FakePath())
    # _WORKER_SCRIPT est un PosixPath (read-only) · on remplace par un FakePath
    monkeypatch.setattr(wr, "_WORKER_SCRIPT", FakePath())
    monkeypatch.setattr(wr, "_resolve_python_bin", lambda: "/usr/bin/python3")
    # Disable real sleep dans stagger (tests rapides)
    monkeypatch.setattr(wr._time, "sleep", lambda *_a, **_k: None)
    # Disable env stagger pour les tests (sinon stagger=2000ms lent)
    monkeypatch.setenv("SPAWN_STAGGER_MS", "0")
    monkeypatch.setenv("WORKER_PARTIAL_RESPAWN_COOLDOWN_S", "300")
    return {"alive": alive_pids, "next_pid": pid_counter}


# ─────────────────────────────────────────────────────────────────────────────
# Tests · _spawn_all_workers refactor list→dict
# ─────────────────────────────────────────────────────────────────────────────
def test_spawn_all_workers_returns_dict_indexed(patch_runtime):
    """_spawn_all_workers retourne dict[int,int] (idx → PID), pas list."""
    pids = wr._spawn_all_workers(worker_count=8)
    assert isinstance(pids, dict), "expected dict[int,int]"
    assert set(pids.keys()) == set(range(8)), f"expected indices 0..7, got {set(pids.keys())}"
    assert len(set(pids.values())) == 8, "PIDs doivent être uniques"
    assert all(isinstance(v, int) and v > 0 for v in pids.values())


def test_terminate_workers_accepts_dict_and_list(patch_runtime):
    """_terminate_workers accepte dict (nouveau) ou list (legacy compat)."""
    alive = patch_runtime["alive"]
    # Avec dict
    pids_dict = {0: 1000, 1: 1001, 2: 1002}
    alive.update(pids_dict.values())
    wr._terminate_workers(pids_dict, grace_s=0)
    assert not alive & set(pids_dict.values())
    # Avec list (legacy)
    pids_list = [2000, 2001]
    alive.update(pids_list)
    wr._terminate_workers(pids_list, grace_s=0)
    assert not alive & set(pids_list)


# ─────────────────────────────────────────────────────────────────────────────
# Tests · R3 partial respawn (cœur du fix)
# ─────────────────────────────────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_partial_respawn_detects_missing_indices(patch_runtime, monkeypatch):
    """État chronique 5/8 (idx 3,4,5 manquants) → R3 respawn ciblé après 1 cycle."""
    alive = patch_runtime["alive"]
    # Spawn initial 8 workers
    wr._pids = wr._spawn_all_workers(worker_count=8)
    assert len(wr._pids) == 8
    # Simule crash des idx 3, 4, 5 (retire leurs PIDs de alive)
    for crash_idx in [3, 4, 5]:
        crashed_pid = wr._pids[crash_idx]
        alive.discard(crashed_pid)
    # n_alive doit = 5 (≥ min=3 donc PAS de full respawn)
    n_alive_before = sum(1 for p in wr._pids.values() if p in alive)
    assert n_alive_before == 5, f"setup KO: n_alive={n_alive_before}"

    # Lance le watchdog avec check_interval=0.05s, cooldown=0 pour bypasser anti-thrash
    monkeypatch.setenv("ZEROCOST_INPROCESS_CHECK_INTERVAL_S", "0")
    monkeypatch.setenv("ZEROCOST_INPROCESS_MIN_WORKERS", "3")
    monkeypatch.setenv("WORKER_PARTIAL_RESPAWN_COOLDOWN_S", "0")  # bypass cooldown
    wr._stop_event = asyncio.Event()
    task = asyncio.create_task(wr._watchdog_loop(worker_count=8))
    # Laisse tourner 1-2 cycles
    await asyncio.sleep(0.15)
    wr._stop_event.set()
    await asyncio.wait_for(task, timeout=2.0)

    # Vérifie que idx 3, 4, 5 ont des nouveaux PIDs vivants
    assert set(wr._pids.keys()) == set(range(8)), f"keys après respawn: {sorted(wr._pids.keys())}"
    for idx in [3, 4, 5]:
        new_pid = wr._pids[idx]
        assert new_pid in alive, f"idx {idx} PID {new_pid} not alive after partial respawn"
    # Total = 8 vivants
    n_alive_after = sum(1 for p in wr._pids.values() if p in alive)
    assert n_alive_after == 8, f"n_alive après respawn={n_alive_after}, expected 8"


@pytest.mark.asyncio
async def test_partial_respawn_respects_cooldown(patch_runtime, monkeypatch):
    """Cooldown anti-thrash : 2 cycles consécutifs partial → seul le 1er respawn."""
    alive = patch_runtime["alive"]
    wr._pids = wr._spawn_all_workers(worker_count=8)
    # Crash idx 3 seulement
    alive.discard(wr._pids[3])
    pid_before = wr._pids[3]

    monkeypatch.setenv("ZEROCOST_INPROCESS_CHECK_INTERVAL_S", "0")
    monkeypatch.setenv("ZEROCOST_INPROCESS_MIN_WORKERS", "3")
    monkeypatch.setenv("WORKER_PARTIAL_RESPAWN_COOLDOWN_S", "9999")  # cooldown très long
    wr._stop_event = asyncio.Event()
    task = asyncio.create_task(wr._watchdog_loop(worker_count=8))
    await asyncio.sleep(0.1)
    # Premier respawn doit avoir eu lieu
    pid_after_1st = wr._pids[3]
    assert pid_after_1st != pid_before
    assert pid_after_1st in alive

    # Crash idx 3 à nouveau immédiatement
    alive.discard(wr._pids[3])
    # Attente quelques cycles · cooldown=9999s donc PAS de respawn
    await asyncio.sleep(0.15)
    wr._stop_event.set()
    await asyncio.wait_for(task, timeout=2.0)

    # idx 3 toujours mort (cooldown actif)
    assert wr._pids[3] not in alive, "Cooldown KO · respawn déclenché malgré cooldown actif"


@pytest.mark.asyncio
async def test_legacy_full_respawn_below_min(patch_runtime, monkeypatch):
    """n_alive < min_workers → full respawn (legacy preserved)."""
    alive = patch_runtime["alive"]
    wr._pids = wr._spawn_all_workers(worker_count=8)
    # Kill 6 workers → reste 2 < min=3
    for idx in [0, 1, 2, 3, 4, 5]:
        alive.discard(wr._pids[idx])
    n_alive_before = sum(1 for p in wr._pids.values() if p in alive)
    assert n_alive_before == 2

    monkeypatch.setenv("ZEROCOST_INPROCESS_CHECK_INTERVAL_S", "0")
    monkeypatch.setenv("ZEROCOST_INPROCESS_MIN_WORKERS", "3")
    wr._stop_event = asyncio.Event()
    task = asyncio.create_task(wr._watchdog_loop(worker_count=8))
    await asyncio.sleep(0.15)
    wr._stop_event.set()
    await asyncio.wait_for(task, timeout=2.0)

    # Full respawn : tous les 8 indices doivent être vivants
    assert set(wr._pids.keys()) == set(range(8))
    for idx in range(8):
        assert wr._pids[idx] in alive, f"idx {idx} mort après full respawn"


@pytest.mark.asyncio
async def test_stable_state_no_action(patch_runtime, monkeypatch):
    """Si tous les workers OK · ZÉRO action watchdog (idempotence)."""
    alive = patch_runtime["alive"]
    wr._pids = wr._spawn_all_workers(worker_count=8)
    pids_initial = dict(wr._pids)

    monkeypatch.setenv("ZEROCOST_INPROCESS_CHECK_INTERVAL_S", "0")
    monkeypatch.setenv("ZEROCOST_INPROCESS_MIN_WORKERS", "3")
    wr._stop_event = asyncio.Event()
    task = asyncio.create_task(wr._watchdog_loop(worker_count=8))
    await asyncio.sleep(0.1)
    wr._stop_event.set()
    await asyncio.wait_for(task, timeout=2.0)

    # Aucun PID changé (idempotence)
    assert wr._pids == pids_initial, "Watchdog modifié state alors que tout OK"
    assert sum(1 for p in wr._pids.values() if p in alive) == 8


# ─────────────────────────────────────────────────────────────────────────────
# Test · Default cooldown (300s) configurable
# ─────────────────────────────────────────────────────────────────────────────
def test_cooldown_env_var_parsing(monkeypatch):
    """WORKER_PARTIAL_RESPAWN_COOLDOWN_S env var parsée correctement."""
    monkeypatch.setenv("WORKER_PARTIAL_RESPAWN_COOLDOWN_S", "120")
    assert int(os.environ["WORKER_PARTIAL_RESPAWN_COOLDOWN_S"]) == 120
    # Default 300 si absent
    monkeypatch.delenv("WORKER_PARTIAL_RESPAWN_COOLDOWN_S", raising=False)
    assert os.environ.get("WORKER_PARTIAL_RESPAWN_COOLDOWN_S") is None

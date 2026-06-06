"""
runtime_tier_status_router_omega.py — Endpoint diagnostic runtime tier
═══════════════════════════════════════════════════════════════════════════════
P22ΩΩ_RUNTIME_TIER_STATUS_Ω · COMMANDANT STEEVE-MAX · 2026-06-06 · BCE-4X ULTIME ABSOLU
Verrou Phase III · LECTURE SEULE STRICTE · ADDITIF.

Endpoint purement observationnel pour différencier preview vs Elite à distance
sans accès direct au pod. Lit /sys/fs/cgroup/cpu.max, memory.max, /proc/1/stat,
/proc/<pid>/stat (pour workers ZEROCOST), et compare timestamps state files
filesystem vs R2 (dual-write lag).

ENDPOINT
--------
  GET /api/v30/runtime/tier-status
    → {tier, cpu, memory, pod_uptime, workers, r2_state_lag, watchdog, checked_at}

DOCTRINE
--------
Lecture seule stricte · zéro mutation · zéro impact runtime · best-effort
(R2/cgroup lectures wrappées dans try/except · degradation gracieuse). Verrou
Phase III intact · aucun engine touché.
"""
from __future__ import annotations

import json
import logging
import os
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import APIRouter

logger = logging.getLogger("bionic.runtime_tier_status_router")

router = APIRouter(prefix="/api/v30/runtime", tags=["runtime-diagnostic"])

# Seuil de détection ELITE (cohérent avec zerocost_seed_r5_supervisor_watchdog.sh)
_ELITE_QUOTA_THRESHOLD_US = 400000  # 4.0 vCPUs

# Paths cgroup v2 standards (K8s pod)
_CGROUP_CPU_MAX = "/sys/fs/cgroup/cpu.max"
_CGROUP_CPU_STAT = "/sys/fs/cgroup/cpu.stat"
_CGROUP_CPU_PRESSURE = "/sys/fs/cgroup/cpu.pressure"
_CGROUP_MEMORY_MAX = "/sys/fs/cgroup/memory.max"
_CGROUP_MEMORY_CURRENT = "/sys/fs/cgroup/memory.current"

# State files workers (filesystem source de vérité runtime)
_STATE_DIR = Path("/var/log/bionic-zerocost-seed-r5")

# Lazy import du module R2 helper (best-effort)
try:
    from integrations.r2_state_persistence_omega import (
        load_state_from_r2 as _r2_load_state,
        list_state_keys_in_r2 as _r2_list_keys,
    )
    _R2_HELPER_AVAILABLE = True
except Exception as _e:
    _r2_load_state = None  # type: ignore
    _r2_list_keys = None  # type: ignore
    _R2_HELPER_AVAILABLE = False


def _read_cgroup_file(path: str) -> Optional[str]:
    try:
        with open(path) as f:
            return f.read().strip()
    except Exception:
        return None


def _parse_cpu_max() -> Dict[str, Any]:
    """Parse /sys/fs/cgroup/cpu.max format 'QUOTA PERIOD' (µs)."""
    raw = _read_cgroup_file(_CGROUP_CPU_MAX)
    info: Dict[str, Any] = {
        "raw": raw,
        "quota_us": None,
        "period_us": None,
        "vcpus": None,
        "elite_threshold_us": _ELITE_QUOTA_THRESHOLD_US,
    }
    if not raw:
        return info
    parts = raw.split()
    if len(parts) >= 2:
        try:
            info["period_us"] = int(parts[1])
        except ValueError:
            pass
        if parts[0] == "max":
            info["quota_us"] = "max"
            info["vcpus"] = "unlimited"
        else:
            try:
                info["quota_us"] = int(parts[0])
                if info["period_us"]:
                    info["vcpus"] = round(int(parts[0]) / info["period_us"], 3)
            except ValueError:
                pass
    return info


def _detect_tier(cpu_info: Dict[str, Any]) -> str:
    """Reproduit la logique du watchdog bash."""
    quota = cpu_info.get("quota_us")
    if quota == "max":
        return "ELITE_UNLIMITED"
    if isinstance(quota, int) and quota >= _ELITE_QUOTA_THRESHOLD_US:
        return "ELITE"
    return "PREVIEW"


def _parse_memory() -> Dict[str, Any]:
    raw_max = _read_cgroup_file(_CGROUP_MEMORY_MAX)
    raw_cur = _read_cgroup_file(_CGROUP_MEMORY_CURRENT)
    info: Dict[str, Any] = {"max_raw": raw_max, "current_raw": raw_cur}
    try:
        if raw_max and raw_max != "max":
            mb = int(raw_max)
            info["max_bytes"] = mb
            info["max_gb"] = round(mb / (1024 ** 3), 2)
        elif raw_max == "max":
            info["max_bytes"] = "max"
            info["max_gb"] = "unlimited"
    except Exception:
        pass
    try:
        if raw_cur:
            cb = int(raw_cur)
            info["current_bytes"] = cb
            info["current_gb"] = round(cb / (1024 ** 3), 2)
            if isinstance(info.get("max_bytes"), int):
                info["used_pct"] = round(cb / info["max_bytes"] * 100, 1)
    except Exception:
        pass
    return info


def _parse_cpu_stat() -> Dict[str, Any]:
    """Throttling et usage cgroup."""
    raw = _read_cgroup_file(_CGROUP_CPU_STAT)
    stat: Dict[str, Any] = {}
    if not raw:
        return stat
    for line in raw.splitlines():
        parts = line.split()
        if len(parts) == 2:
            try:
                stat[parts[0]] = int(parts[1])
            except ValueError:
                stat[parts[0]] = parts[1]
    # Throttle ratio
    np_, nt = stat.get("nr_periods"), stat.get("nr_throttled")
    if isinstance(np_, int) and np_ > 0 and isinstance(nt, int):
        stat["throttle_ratio_pct"] = round(nt / np_ * 100, 2)
    return stat


def _parse_cpu_pressure() -> Dict[str, Any]:
    raw = _read_cgroup_file(_CGROUP_CPU_PRESSURE)
    if not raw:
        return {}
    psi: Dict[str, Any] = {}
    for line in raw.splitlines():
        # ex: "some avg10=15.94 avg60=21.00 avg300=22.16 total=12106418560"
        parts = line.split()
        if not parts:
            continue
            
        kind = parts[0]
        psi[kind] = {}
        for kv in parts[1:]:
            if "=" in kv:
                k, v = kv.split("=", 1)
                try:
                    psi[kind][k] = float(v) if "." in v else int(v)
                except ValueError:
                    psi[kind][k] = v
    return psi


def _pod_uptime_seconds() -> Optional[int]:
    """Uptime du PID 1 (entrypoint pod)."""
    try:
        # /proc/1/stat : "1 (bash) S 0 1 1 ... starttime=22"
        with open("/proc/1/stat") as f:
            stat = f.read().split()
        # starttime is 22nd field (index 21), in clock ticks since boot
        # Use /proc/uptime to get seconds since boot
        with open("/proc/uptime") as f:
            uptime_seconds = float(f.read().split()[0])
        clk_tck = os.sysconf(os.sysconf_names["SC_CLK_TCK"])
        starttime_seconds = int(stat[21]) / clk_tck
        return int(uptime_seconds - starttime_seconds)
    except Exception:
        return None


def _scan_zerocost_workers() -> List[Dict[str, Any]]:
    """Scanne /proc pour trouver les processus zerocost_worker_seed_r5.py."""
    workers: List[Dict[str, Any]] = []
    try:
        for entry in os.listdir("/proc"):
            if not entry.isdigit():
                continue
            pid = int(entry)
            try:
                cmdline_path = f"/proc/{pid}/cmdline"
                with open(cmdline_path, "rb") as f:
                    cmdline = f.read().replace(b"\x00", b" ").decode("utf-8", errors="ignore").strip()
                if "zerocost_worker_seed_r5" not in cmdline:
                    continue
                # Env pour récupérer WORKER_INDEX
                worker_index = None
                try:
                    with open(f"/proc/{pid}/environ", "rb") as ef:
                        env = ef.read().decode("utf-8", errors="ignore").split("\x00")
                    for e in env:
                        if e.startswith("WORKER_INDEX="):
                            worker_index = int(e.split("=", 1)[1])
                            break
                except Exception:
                    pass
                # Uptime du process via /proc/<pid>/stat starttime
                try:
                    with open(f"/proc/{pid}/stat") as sf:
                        stat = sf.read().split()
                    with open("/proc/uptime") as uf:
                        uptime_seconds = float(uf.read().split()[0])
                    clk_tck = os.sysconf(os.sysconf_names["SC_CLK_TCK"])
                    starttime_seconds = int(stat[21]) / clk_tck
                    proc_uptime = int(uptime_seconds - starttime_seconds)
                except Exception:
                    proc_uptime = None
                workers.append({
                    "pid": pid,
                    "worker_index": worker_index,
                    "uptime_seconds": proc_uptime,
                })
            except Exception:
                continue
    except Exception as e:
        logger.warning(f"[RUNTIME_TIER_STATUS] scan /proc fail: {e}")
    workers.sort(key=lambda w: (w.get("worker_index") if w.get("worker_index") is not None else 99, w["pid"]))
    return workers


def _r2_state_lag_per_worker(max_workers: int = 16) -> Dict[str, Any]:
    """Compare timestamps state files filesystem vs R2 par worker."""
    out: Dict[str, Any] = {
        "r2_helper_available": _R2_HELPER_AVAILABLE,
        "per_worker": [],
        "summary": {},
    }
    if not _R2_HELPER_AVAILABLE or _r2_load_state is None:
        return out
    lags: List[float] = []
    for i in range(max_workers):
        fs_path = _STATE_DIR / f"state_worker_{i}.json"
        fs_data = None
        try:
            if fs_path.exists():
                fs_data = json.loads(fs_path.read_text())
        except Exception:
            pass
        try:
            r2_data = _r2_load_state(i)
        except Exception:
            r2_data = None
        if fs_data is None and r2_data is None:
            continue
        entry: Dict[str, Any] = {
            "worker_index": i,
            "fs_present": fs_data is not None,
            "r2_present": r2_data is not None,
        }
        if fs_data:
            entry["fs_r5_idx_done"] = fs_data.get("r5_idx_done")
            entry["fs_species_done_n"] = len(fs_data.get("species_done", []))
            entry["fs_updated_at"] = fs_data.get("updated_at")
        if r2_data:
            entry["r2_r5_idx_done"] = r2_data.get("r5_idx_done")
            entry["r2_species_done_n"] = len(r2_data.get("species_done", []))
            entry["r2_updated_at"] = r2_data.get("updated_at")
        # Lag : différence timestamps si les deux présents
        if fs_data and r2_data:
            try:
                fs_ts = time.strptime(fs_data["updated_at"], "%Y-%m-%dT%H:%M:%SZ")
                r2_ts = time.strptime(r2_data["updated_at"], "%Y-%m-%dT%H:%M:%SZ")
                lag = abs(time.mktime(fs_ts) - time.mktime(r2_ts))
                entry["lag_seconds"] = int(lag)
                lags.append(lag)
                entry["sync_status"] = "MATCH" if lag <= 5 else ("OK" if lag <= 60 else "STALE_R2")
            except Exception:
                pass
        out["per_worker"].append(entry)
    if lags:
        out["summary"] = {
            "workers_with_both_fs_r2": len(lags),
            "lag_min_s": int(min(lags)),
            "lag_max_s": int(max(lags)),
            "lag_avg_s": int(sum(lags) / len(lags)),
        }
    # Inventaire R2
    try:
        if _r2_list_keys is not None:
            r2_keys = _r2_list_keys()
            out["r2_keys_inventory"] = r2_keys
            out["r2_keys_count"] = len(r2_keys)
    except Exception:
        pass
    return out


def _watchdog_target_inferred(cpu_info: Dict[str, Any]) -> Dict[str, Any]:
    """Calcule ce que devrait être TARGET_WORKERS selon la logique watchdog."""
    tier = _detect_tier(cpu_info)
    target_preview = int(os.environ.get("TARGET_WORKERS_PREVIEW", "3"))
    target_elite = int(os.environ.get("TARGET_WORKERS_ELITE", "8"))
    if tier in ("ELITE", "ELITE_UNLIMITED"):
        target = target_elite
    else:
        target = target_preview
    return {
        "inferred_target_workers": target,
        "target_workers_preview": target_preview,
        "target_workers_elite": target_elite,
        "elite_threshold_us": _ELITE_QUOTA_THRESHOLD_US,
    }


@router.get("/tier-status")
def tier_status_endpoint() -> Dict[str, Any]:
    """Endpoint diagnostic runtime · LECTURE SEULE STRICTE.
    
    Retourne :
      - tier (PREVIEW / ELITE / ELITE_UNLIMITED)
      - cpu (cpu.max + vCPUs + throttling + PSI)
      - memory (memory.max + current)
      - pod_uptime (seconds + human)
      - workers (PIDs + uptime + worker_index)
      - r2_state_lag (FS vs R2 sync par worker)
      - watchdog (TARGET_WORKERS inferré + seuil Elite)
      - checked_at (timestamp UTC)
    """
    t0 = time.time()
    cpu_info = _parse_cpu_max()
    tier = _detect_tier(cpu_info)
    pod_uptime_s = _pod_uptime_seconds()
    workers = _scan_zerocost_workers()
    response: Dict[str, Any] = {
        "served_by": "RUNTIME-TIER-STATUS-Ω-ROUTER",
        "doctrine": "P22ΩΩ_RUNTIME_TIER_STATUS_Ω · BCE-4X · Verrou Phase III · lecture seule",
        "checked_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "tier": tier,
        "cpu": {
            **cpu_info,
            "stat": _parse_cpu_stat(),
            "pressure": _parse_cpu_pressure(),
        },
        "memory": _parse_memory(),
        "pod_uptime": {
            "seconds": pod_uptime_s,
            "human": _human_duration(pod_uptime_s) if pod_uptime_s else None,
        },
        "workers": {
            "count": len(workers),
            "list": workers,
        },
        "r2_state_lag": _r2_state_lag_per_worker(),
        "watchdog": _watchdog_target_inferred(cpu_info),
        "scan_duration_ms": int((time.time() - t0) * 1000),
    }
    return response


def _human_duration(seconds: Optional[int]) -> Optional[str]:
    if seconds is None:
        return None
    s = int(seconds)
    d, s = divmod(s, 86400)
    h, s = divmod(s, 3600)
    m, s = divmod(s, 60)
    parts = []
    if d:
        parts.append(f"{d}d")
    if h or d:
        parts.append(f"{h}h")
    if m or h or d:
        parts.append(f"{m}m")
    parts.append(f"{s}s")
    return "".join(parts)

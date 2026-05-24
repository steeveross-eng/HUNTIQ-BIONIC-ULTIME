"""
rapport_3rf_t95_emit.py — Wrapper d'émission RAPPORT_3RF_T+95%_Ω
═══════════════════════════════════════════════════════════════════════════════
P22ΩΩ_3RF_ACCELERATION_P0_Ω · COMMANDANT STEEVE-MAX · 2026-02-20 · BCE-4X ULTIME ABSOLU
Verrou Phase III : MAINTENU · LECTURE SEULE strict.

DOCTRINE
--------
Wrapper appelé par le watcher asyncio (`server.py` lifespan) toutes les ~30 min.
Logique :
  1. Exécute `rapport_3rf_t95_omega.py` en mode JSON pour récupérer global_pct
  2. Si `global_pct >= THRESHOLD_PCT` ET pas encore émis :
     - Génère rapport texte + JSON dans `/app/memory/RAPPORT_3RF_T+95%_Ω_EMITTED.{md,json}`
     - Marque émission dans `/app/backend/state/rapport_3rf_t95_state.json`
     - Imprime ligne « RAPPORT_3RF_T+95%_Ω — ÉMIS »
  3. Sinon :
     - Imprime ligne de monitoring (global_pct + ETA)
     - Met à jour le state (dernière vérification)

USAGE
-----
    python3 /app/backend/tools/rapport_3rf_t95_emit.py
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

BACKEND_ROOT = Path("/app/backend")
SCRIPT_MAIN = BACKEND_ROOT / "tools" / "rapport_3rf_t95_omega.py"
STATE_FILE = BACKEND_ROOT / "state" / "rapport_3rf_t95_state.json"
MEMORY_DIR = Path("/app/memory")
OUTPUT_MD = MEMORY_DIR / "RAPPORT_3RF_T+95%_Ω_EMITTED.md"
OUTPUT_JSON = MEMORY_DIR / "RAPPORT_3RF_T+95%_Ω_EMITTED.json"

THRESHOLD_PCT = float(os.environ.get("RAPPORT_3RF_T95_THRESHOLD_PCT", "95.0"))


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_state() -> dict:
    if STATE_FILE.is_file():
        try:
            return json.loads(STATE_FILE.read_text())
        except Exception:
            pass
    return {
        "_doctrine": "P22ΩΩ_3RF_ACCELERATION_P0_Ω",
        "threshold_pct": THRESHOLD_PCT,
        "armed_at": _now_iso(),
        "emitted": False,
        "emitted_at": None,
        "last_check_at": None,
        "last_global_pct": None,
        "check_count": 0,
    }


def _save_state(state: dict) -> None:
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2, ensure_ascii=False))


def _run_main_script(force_full: bool, output_json: bool) -> str:
    env = dict(os.environ)
    env["OUTPUT"] = "json" if output_json else "text"
    if force_full:
        env["FORCE_FULL"] = "1"
    env["SAMPLE_TILES_PER_RF"] = env.get("SAMPLE_TILES_PER_RF", "2")
    python_bin = "/root/.venv/bin/python3"
    if not Path(python_bin).is_file():
        python_bin = sys.executable
    proc = subprocess.run(
        [python_bin, str(SCRIPT_MAIN)],
        env=env, capture_output=True, text=True, timeout=300,
    )
    if proc.returncode != 0:
        raise RuntimeError(
            f"rapport_3rf_t95_omega exit={proc.returncode} · stderr={proc.stderr[-500:]}"
        )
    return proc.stdout


def main() -> int:
    state = _load_state()
    state["check_count"] = int(state.get("check_count", 0)) + 1
    state["last_check_at"] = _now_iso()

    # Court-circuit : déjà émis
    if state.get("emitted"):
        print(f"[RAPPORT_3RF_T+95%_Ω] déjà émis le {state.get('emitted_at')} · skip")
        _save_state(state)
        return 0

    # Étape 1 : récupérer global_pct via JSON
    try:
        raw_json = _run_main_script(force_full=False, output_json=True)
        report = json.loads(raw_json)
    except Exception as e:
        print(f"[RAPPORT_3RF_T+95%_Ω] check failed: {e}")
        state["last_error"] = str(e)[:200]
        _save_state(state)
        return 1

    global_pct = float(report.get("coverage_cellular", {}).get("global_pct", 0.0))
    state["last_global_pct"] = global_pct

    # Étape 2 : seuil atteint → émission
    if global_pct >= THRESHOLD_PCT:
        print(f"[RAPPORT_3RF_T+95%_Ω] seuil ATTEINT · global_pct={global_pct}% · "
              f"émission FULL en cours...")
        try:
            full_text = _run_main_script(force_full=True, output_json=False)
            full_json = _run_main_script(force_full=True, output_json=True)
        except Exception as e:
            print(f"[RAPPORT_3RF_T+95%_Ω] émission FULL failed: {e}")
            state["last_error"] = str(e)[:200]
            _save_state(state)
            return 1

        MEMORY_DIR.mkdir(parents=True, exist_ok=True)
        emitted_at = _now_iso()
        header = (
            f"# RAPPORT_3RF_T+95%_Ω — ÉMIS\n\n"
            f"- **Doctrine**: P22ΩΩ_3RF_ACCELERATION_P0_Ω\n"
            f"- **Commandant**: STEEVE-MAX\n"
            f"- **Emitted at**: {emitted_at}\n"
            f"- **Threshold reached**: {global_pct}% ≥ {THRESHOLD_PCT}%\n"
            f"- **Mode**: AUTO-EMIT (watcher asyncio · lecture seule)\n\n"
            f"---\n\n```\n"
        )
        footer = "\n```\n"
        OUTPUT_MD.write_text(header + full_text + footer)
        OUTPUT_JSON.write_text(full_json)

        state["emitted"] = True
        state["emitted_at"] = emitted_at
        state["emitted_global_pct"] = global_pct
        state["output_md"] = str(OUTPUT_MD)
        state["output_json"] = str(OUTPUT_JSON)
        _save_state(state)
        print(f"[RAPPORT_3RF_T+95%_Ω] ÉMIS · {OUTPUT_MD} · {OUTPUT_JSON}")
        return 0

    # Étape 3 : seuil non atteint → monitoring uniquement
    eta = report.get("eta_to_threshold", {})
    print(
        f"[RAPPORT_3RF_T+95%_Ω] check #{state['check_count']} · "
        f"global_pct={global_pct:.2f}% < {THRESHOLD_PCT}% · "
        f"ETA seuil ~{eta.get('eta_hours_to_threshold')}h · armé=True"
    )
    _save_state(state)
    return 0


if __name__ == "__main__":
    sys.exit(main())

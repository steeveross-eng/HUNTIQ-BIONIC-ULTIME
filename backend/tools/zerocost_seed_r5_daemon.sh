#!/usr/bin/env bash
# ════════════════════════════════════════════════════════════════════
# zerocost_seed_r5_daemon.sh — Daemon β2-ΣΤ · 8w nice 19
# P22ΩΩ_ACTIVATION_BETA2_ST_Ω · STEEVE-MAX · 2026-02-19
# ════════════════════════════════════════════════════════════════════
set -u

ACTION="${1:-status}"
WORKER_COUNT="${WORKER_COUNT:-8}"
GRID_FILE_PATH="${GRID_FILE_PATH:-/app/backend/cache/zerocost_v1/canada_h3_grid_r5_seed_qc_limitrophes.json}"  # OMEGA-X ∑ 2026-06-03 STEEVE-MAX · GRID_LOCK · fallback Phase 2 limitrophes (vs Phase 1)
MAX_R5_CELLS="${MAX_R5_CELLS:-0}"
LOG_DIR="${LOG_DIR:-/var/log/bionic-zerocost-seed-r5}"
STATE_FILE="$LOG_DIR/state.json"

mkdir -p "$LOG_DIR"
cd /app/backend

start_daemon() {
    if [[ -f "$STATE_FILE" ]]; then
        ALIVE=0
        for pid in $(python3 -c "import json; print(' '.join(str(p) for p in json.load(open('$STATE_FILE'))['pids']))" 2>/dev/null); do
            if kill -0 $pid 2>/dev/null; then ALIVE=$((ALIVE+1)); fi
        done
        if [[ $ALIVE -gt 0 ]]; then
            echo "⚠️ $ALIVE workers β2-ΣΤ déjà en cours."
            return 1
        fi
    fi

    rm -f "$LOG_DIR"/worker_*.log
    echo "═══ DAEMON β2-ΣΤ · $WORKER_COUNT workers · nice -n 19 ═══"
    echo "  Grille R5 SEED : $GRID_FILE_PATH"
    echo "  Logs           : $LOG_DIR/worker_*.log"
    echo ""

    START_TS=$(date +%s)
    PIDS=()
    PYTHON_BIN="/root/.venv/bin/python3"
    [ -x "$PYTHON_BIN" ] || PYTHON_BIN="$(command -v python3)"
    # P22ΩΩ_ELITE_SPAWN_STAGGER_Ω · 2026-06-06 · STEEVE-MAX · throttle<5% calibration
    # Stagger spawn N ms entre workers · évite le spike CPU initial (bootstrap V20
    # parallèle = pic ~400% CPU pendant ~3-5s qui déclenche probes liveness fail).
    # Défaut 0 = comportement legacy (preview). Watchdog active 2000ms en TIER=ELITE.
    SPAWN_STAGGER_MS="${SPAWN_STAGGER_MS:-0}"
    WORKER_PACING_MS="${WORKER_PACING_MS:-0}"
    for ((i=0; i<WORKER_COUNT; i++)); do
        setsid nohup nice -n 19 env \
            GRID_FILE_PATH="$GRID_FILE_PATH" \
            WORKER_INDEX=$i \
            WORKER_COUNT=$WORKER_COUNT \
            MAX_R5_CELLS=$MAX_R5_CELLS \
            WORKER_PACING_MS="$WORKER_PACING_MS" \
            PYTHONUNBUFFERED=1 \
            "$PYTHON_BIN" /app/backend/tools/zerocost_worker_seed_r5.py \
            > "$LOG_DIR/worker_${i}.log" 2>&1 < /dev/null &
        PIDS+=($!)
        disown
        echo "  ✓ β2-ΣΤ Worker $i démarré (PID ${PIDS[$i]} · nice 19 · $PYTHON_BIN · pacing=${WORKER_PACING_MS}ms)"
        # Stagger spawn si activé (Elite)
        if [[ $SPAWN_STAGGER_MS -gt 0 && $i -lt $((WORKER_COUNT - 1)) ]]; then
            sleep $(awk "BEGIN { print $SPAWN_STAGGER_MS / 1000 }")
        fi
    done
    echo "{\"started_at\": $START_TS, \"worker_count\": $WORKER_COUNT, \"pids\": [$(IFS=,; echo "${PIDS[*]}")], \"grid_file\": \"$GRID_FILE_PATH\"}" > "$STATE_FILE"
    echo ""
    echo "✅ DAEMON β2-ΣΤ LANCÉ · indépendant session (PPID=1)"
}

status_daemon() {
    if [[ ! -f "$STATE_FILE" ]]; then
        echo "❌ Aucun daemon β2-ΣΤ démarré"
        return 1
    fi
    WC=$(python3 -c "import json;print(json.load(open('$STATE_FILE'))['worker_count'])")
    ST=$(python3 -c "import json;print(json.load(open('$STATE_FILE'))['started_at'])")
    PIDS=$(python3 -c "import json;print(' '.join(str(p) for p in json.load(open('$STATE_FILE'))['pids']))")
    NOW=$(date +%s); EL=$((NOW - ST))
    ALIVE=0
    for pid in $PIDS; do
        if kill -0 $pid 2>/dev/null; then ALIVE=$((ALIVE+1)); fi
    done
    TOTAL_SEED_OK=0; TOTAL_FANOUT_OK=0
    for ((i=0; i<WC; i++)); do
        f="$LOG_DIR/worker_${i}.log"
        [[ -f "$f" ]] || continue
        seed_ok=$(grep -oE "SEED OK +: [0-9]+" "$f" 2>/dev/null | tail -1 | grep -oE "[0-9]+")
        fanout_ok=$(grep -oE "FAN-OUT OK : [0-9]+" "$f" 2>/dev/null | tail -1 | grep -oE "[0-9]+")
        if [[ -z "$seed_ok" ]]; then
            seed_ok=$(grep -oE "seed_ok=[0-9]+" "$f" | tail -1 | grep -oE "[0-9]+")
            fanout_ok=$(grep -oE "fanout_ok=[0-9]+" "$f" | tail -1 | grep -oE "[0-9]+")
        fi
        TOTAL_SEED_OK=$((TOTAL_SEED_OK + ${seed_ok:-0}))
        TOTAL_FANOUT_OK=$((TOTAL_FANOUT_OK + ${fanout_ok:-0}))
    done
    echo "═══ STATUS DAEMON β2-ΣΤ (T+${EL}s = $((EL/60))min) ═══"
    echo "  Workers vivants : $ALIVE / $WC"
    echo "  SEED total OK   : $TOTAL_SEED_OK"
    echo "  FAN-OUT total OK: $TOTAL_FANOUT_OK"
    if (( EL > 0 )); then
        echo "  Débit fan-out   : $(python3 -c "print(f'{$TOTAL_FANOUT_OK / $EL:.2f}')") R6/s"
    fi
}

stop_daemon() {
    if [[ ! -f "$STATE_FILE" ]]; then
        echo "❌ Aucun daemon β2-ΣΤ à arrêter"
        return 1
    fi
    PIDS=$(python3 -c "import json;print(' '.join(str(p) for p in json.load(open('$STATE_FILE'))['pids']))")
    echo "Kill PIDs: $PIDS"
    kill $PIDS 2>/dev/null
    sleep 2
    for pid in $PIDS; do
        if kill -0 $pid 2>/dev/null; then
            kill -9 $pid 2>/dev/null
        fi
    done
    rm -f "$STATE_FILE"
    echo "✅ Daemon β2-ΣΤ arrêté"
}

# ═══════════════════════════════════════════════════════════════════════════
# P22ΩΩ_P2_WORKER_PARTIAL_RECOVERY_DAEMON_Ω · 2026-06-08 · STEEVE-MAX
# BCE-4X ULTIME ABSOLU · Verrou Phase III · STRICT ADDITIF
# Spawn UN seul worker à index donné · utilisé par le watchdog pour partial
# respawn ciblé sans tuer les workers vivants. Append le nouveau PID au
# state.json (lecture/écriture atomique via python3).
# ═══════════════════════════════════════════════════════════════════════════
spawn_one_index() {
    local IDX="$1"
    if [[ -z "$IDX" ]] || ! [[ "$IDX" =~ ^[0-9]+$ ]]; then
        echo "Usage: $0 spawn_index <idx>" >&2
        return 2
    fi
    if [[ ! -f "$GRID_FILE_PATH" ]]; then
        echo "❌ Grid file introuvable: $GRID_FILE_PATH" >&2
        return 3
    fi
    PYTHON_BIN="/root/.venv/bin/python3"
    [ -x "$PYTHON_BIN" ] || PYTHON_BIN="$(command -v python3)"
    _SPAWN_PACING_MS="${WORKER_PACING_MS:-0}"
    mkdir -p "$LOG_DIR"
    setsid nohup nice -n 19 env \
        GRID_FILE_PATH="$GRID_FILE_PATH" \
        WORKER_INDEX="$IDX" \
        WORKER_COUNT="$WORKER_COUNT" \
        MAX_R5_CELLS="$MAX_R5_CELLS" \
        WORKER_PACING_MS="$_SPAWN_PACING_MS" \
        PYTHONUNBUFFERED=1 \
        "$PYTHON_BIN" /app/backend/tools/zerocost_worker_seed_r5.py \
        > "$LOG_DIR/worker_${IDX}.log" 2>&1 < /dev/null &
    NEW_PID=$!
    disown
    echo "  ✓ β2-ΣΤ Worker $IDX respawned (PID $NEW_PID · partial recovery · pacing=${_SPAWN_PACING_MS}ms)"
    # Append PID au state.json si présent (best-effort idempotent)
    if [[ -f "$STATE_FILE" ]]; then
        python3 -c "
import json
try:
    with open('$STATE_FILE') as f: s = json.load(f)
    s.setdefault('pids', [])
    if $NEW_PID not in s['pids']:
        s['pids'].append($NEW_PID)
    with open('$STATE_FILE','w') as f: json.dump(s, f)
except Exception as e:
    print(f'  ⚠ state.json append fail: {e}')
"
    fi
    echo "$NEW_PID"
}

case "$ACTION" in
    start) start_daemon ;;
    status) status_daemon ;;
    stop) stop_daemon ;;
    spawn_index) spawn_one_index "${2:-}" ;;
    *) echo "Usage: $0 {start|status|stop|spawn_index <idx>}"; exit 1 ;;
esac

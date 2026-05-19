#!/usr/bin/env bash
# ════════════════════════════════════════════════════════════════════
# zerocost_prewarm_p1_daemon.sh — Daemon non-bloquant pré-warm P1 16w
# P22ΩΩ_PHASE3_WEATHERCACHE_BETA2_B_E_PRECEDENT_16W_Ω · STEEVE-MAX
# ════════════════════════════════════════════════════════════════════
# Lance 16 workers en daemon TOTALEMENT DÉTACHÉS via setsid+nohup+disown,
# survivent à toute fermeture de session. Cible : grille P1 only Canada R6.
#
# USAGE :
#   bash /app/backend/tools/zerocost_prewarm_p1_daemon.sh start  # démarre
#   bash /app/backend/tools/zerocost_prewarm_p1_daemon.sh status # état
#   bash /app/backend/tools/zerocost_prewarm_p1_daemon.sh stop   # arrête
# ════════════════════════════════════════════════════════════════════
set -u

ACTION="${1:-status}"
WORKER_COUNT="${WORKER_COUNT:-16}"
WORKER_RESOLUTION="${WORKER_RESOLUTION:-6}"
GRID_FILE_PATH="${GRID_FILE_PATH:-/app/backend/cache/zerocost_v1/canada_h3_grid_r6_p1_only.json}"
MAX_TILES="${MAX_TILES:-0}"  # 0 = illimité
LOG_DIR="${LOG_DIR:-/var/log/bionic-zerocost-prewarm-p1}"
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
            echo "⚠️ $ALIVE workers déjà en cours. Stop d'abord ou laisser tourner."
            return 1
        fi
    fi

    rm -f "$LOG_DIR"/worker_*.log
    echo "═══ DÉMARRAGE PRÉ-WARM P1 DAEMON · WORKER_COUNT=$WORKER_COUNT ═══"
    echo "  Grille     : $GRID_FILE_PATH"
    echo "  Logs       : $LOG_DIR/worker_*.log"
    echo "  Résolution : H3 R$WORKER_RESOLUTION"
    echo "  MAX_TILES  : $MAX_TILES (0 = illimité)"
    echo ""

    START_TS=$(date +%s)
    PIDS=()
    for ((i=0; i<WORKER_COUNT; i++)); do
        # setsid détache du process group de la session
        # nohup ignore SIGHUP quand session ferme
        # < /dev/null détache stdin
        setsid nohup env \
            GRID_FILE_PATH="$GRID_FILE_PATH" \
            WORKER_INDEX=$i \
            WORKER_COUNT=$WORKER_COUNT \
            WORKER_RESOLUTION=$WORKER_RESOLUTION \
            MAX_TILES=$MAX_TILES \
            PYTHONUNBUFFERED=1 \
            python3 /app/backend/tools/zerocost_worker_precompute.py \
            > "$LOG_DIR/worker_${i}.log" 2>&1 < /dev/null &
        PIDS+=($!)
        disown
        echo "  ✓ Worker $i démarré (PID ${PIDS[$i]})"
    done

    # Persister état pour status/stop
    echo "{\"started_at\": $START_TS, \"worker_count\": $WORKER_COUNT, \"pids\": [$(IFS=,; echo "${PIDS[*]}")], \"grid_file\": \"$GRID_FILE_PATH\"}" > "$STATE_FILE"

    echo ""
    echo "✅ DAEMON LANCÉ · $WORKER_COUNT workers détachés"
    echo "   Le job continuera de tourner même après fermeture de cette session."
    echo "   Monitor : bash $0 status"
    echo "   Stop    : bash $0 stop"
}

status_daemon() {
    if [[ ! -f "$STATE_FILE" ]]; then
        echo "❌ Aucun daemon démarré (pas de $STATE_FILE)"
        return 1
    fi

    WORKER_COUNT_S=$(python3 -c "import json;print(json.load(open('$STATE_FILE'))['worker_count'])")
    START_TS=$(python3 -c "import json;print(json.load(open('$STATE_FILE'))['started_at'])")
    PIDS=$(python3 -c "import json;print(' '.join(str(p) for p in json.load(open('$STATE_FILE'))['pids']))")
    NOW=$(date +%s)
    ELAPSED=$((NOW - START_TS))

    ALIVE=0
    for pid in $PIDS; do
        if kill -0 $pid 2>/dev/null; then ALIVE=$((ALIVE+1)); fi
    done

    TOTAL_OK=0; TOTAL_FAIL=0; TOTAL_HALT=0
    for ((i=0; i<WORKER_COUNT_S; i++)); do
        f="$LOG_DIR/worker_${i}.log"
        [[ -f "$f" ]] || continue
        final_ok=$(grep -oE "Tuiles OK +: [0-9]+" "$f" 2>/dev/null | tail -1 | grep -oE "[0-9]+")
        if [[ -n "$final_ok" ]]; then
            final_fail=$(grep -oE "Tuiles FAIL +: [0-9]+" "$f" | tail -1 | grep -oE "[0-9]+")
            final_halt=$(grep -oE "Mask HALT +: [0-9]+" "$f" | tail -1 | grep -oE "[0-9]+")
            TOTAL_OK=$((TOTAL_OK + final_ok))
            TOTAL_FAIL=$((TOTAL_FAIL + ${final_fail:-0}))
            TOTAL_HALT=$((TOTAL_HALT + ${final_halt:-0}))
        else
            last=$(grep -oE "ok=[0-9]+ fail=[0-9]+ halt=[0-9]+" "$f" 2>/dev/null | tail -1)
            if [[ -n "$last" ]]; then
                ok=$(echo "$last" | grep -oE "ok=[0-9]+" | cut -d= -f2)
                fail=$(echo "$last" | grep -oE "fail=[0-9]+" | cut -d= -f2)
                halt=$(echo "$last" | grep -oE "halt=[0-9]+" | cut -d= -f2)
                TOTAL_OK=$((TOTAL_OK + ok))
                TOTAL_FAIL=$((TOTAL_FAIL + fail))
                TOTAL_HALT=$((TOTAL_HALT + halt))
            fi
        fi
    done

    echo "═══ STATUS DAEMON PRÉ-WARM P1 ═══"
    echo "  Démarré il y a : $((ELAPSED/3600))h $(((ELAPSED%3600)/60))min ($ELAPSED s)"
    echo "  Workers vivants: $ALIVE / $WORKER_COUNT_S"
    echo "  Tuiles OK total: $TOTAL_OK"
    echo "  Tuiles FAIL    : $TOTAL_FAIL"
    echo "  Masque HALT    : $TOTAL_HALT"
    if (( ELAPSED > 0 )); then
        RATE=$(python3 -c "print(f'{$TOTAL_OK/$ELAPSED:.3f}')" 2>/dev/null)
        echo "  Débit moyen    : $RATE tuiles/s"
    fi
}

stop_daemon() {
    if [[ ! -f "$STATE_FILE" ]]; then
        echo "❌ Aucun daemon à arrêter"
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
    echo "✅ Daemon arrêté"
}

case "$ACTION" in
    start) start_daemon ;;
    status) status_daemon ;;
    stop) stop_daemon ;;
    *) echo "Usage: $0 {start|status|stop}"; exit 1 ;;
esac

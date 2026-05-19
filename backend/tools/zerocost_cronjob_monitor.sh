#!/usr/bin/env bash
# ════════════════════════════════════════════════════════════════════
# zerocost_cronjob_monitor.sh — Aggregation status 16 workers
# P22ΩΩ_PHASE3_CANADA_CRONJOB_MONITOR_Ω · STEEVE-MAX
# ════════════════════════════════════════════════════════════════════
set -u
LOG_DIR="${LOG_DIR:-/tmp/zerocost_cronjob_logs}"

if [[ ! -f "$LOG_DIR/state.json" ]]; then
    echo "🔴 No state file at $LOG_DIR/state.json — launcher non démarré ?"
    exit 1
fi

WORKER_COUNT=$(python3 -c "import json;print(json.load(open('$LOG_DIR/state.json'))['worker_count'])")
START_TS=$(python3 -c "import json;print(json.load(open('$LOG_DIR/state.json'))['started_at'])")
PIDS=$(python3 -c "import json;print(' '.join(str(p) for p in json.load(open('$LOG_DIR/state.json'))['pids']))")

NOW=$(date +%s)
ELAPSED=$((NOW - START_TS))

ALIVE=0
for pid in $PIDS; do
    if kill -0 $pid 2>/dev/null; then ALIVE=$((ALIVE+1)); fi
done

# Agrégation depuis les logs
TOTAL_OK=0
TOTAL_FAIL=0
TOTAL_HALT=0
TOTAL_BYTES=0
FINISHED=0
for ((i=0; i<WORKER_COUNT; i++)); do
    f="$LOG_DIR/worker_${i}.log"
    [[ -f "$f" ]] || continue
    # Si worker fini, prendre les stats finales (PRIORITAIRE)
    final_ok=$(grep -oE "Tuiles OK +: [0-9]+" "$f" | tail -1 | grep -oE "[0-9]+")
    final_fail=$(grep -oE "Tuiles FAIL +: [0-9]+" "$f" | tail -1 | grep -oE "[0-9]+")
    final_halt=$(grep -oE "Mask HALT +: [0-9]+" "$f" | tail -1 | grep -oE "[0-9]+")
    if [[ -n "$final_ok" ]]; then
        TOTAL_OK=$((TOTAL_OK + final_ok))
        TOTAL_FAIL=$((TOTAL_FAIL + ${final_fail:-0}))
        TOTAL_HALT=$((TOTAL_HALT + ${final_halt:-0}))
        FINISHED=$((FINISHED + 1))
    else
        # Worker encore vivant : lire dernière progress line
        last=$(grep -oE "ok=[0-9]+ fail=[0-9]+ halt=[0-9]+" "$f" | tail -1)
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

echo "═══ ZEROCOST CRONJOB STATUS (T+${ELAPSED}s) ═══"
echo "  Workers vivants : $ALIVE / $WORKER_COUNT  (terminés: $FINISHED)"
echo "  Tuiles OK total : $TOTAL_OK"
echo "  Tuiles FAIL     : $TOTAL_FAIL"
echo "  Masque HALT     : $TOTAL_HALT"
if (( ELAPSED > 0 )); then
    RATE=$(echo "scale=2; $TOTAL_OK / $ELAPSED" | bc 2>/dev/null || echo "?")
    echo "  Débit moyen     : $RATE tuiles/s"
fi
echo ""
echo "Détail par worker :"
for ((i=0; i<WORKER_COUNT; i++)); do
    f="$LOG_DIR/worker_${i}.log"
    if [[ -f "$f" ]]; then
        last_line=$(tail -1 "$f" 2>/dev/null)
        printf "  [%2d] %s\n" "$i" "${last_line:0:120}"
    fi
done

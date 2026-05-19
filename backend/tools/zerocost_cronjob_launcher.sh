#!/usr/bin/env bash
# ════════════════════════════════════════════════════════════════════
# zerocost_cronjob_launcher.sh — Simulation locale CronJob 16 workers
# P22ΩΩ_PHASE3_CANADA_CRONJOB_LOCAL_Ω · STEEVE-MAX
# ════════════════════════════════════════════════════════════════════
# Lance N workers parallèles depuis ce conteneur (équivalent fonctionnel
# du k8s CronJob bionic-zerocost-precompute-parallel) :
#   - WORKER_INDEX = 0..N-1
#   - WORKER_COUNT = N
#   - Chaque worker filtre i % N == WORKER_INDEX dans la grille H3.
#
# USAGE :
#   WORKER_COUNT=16 MAX_TILES=20 \
#   GRID_FILE_PATH=/app/backend/cache/zerocost_v1/canada_h3_grid_r6.json \
#   bash tools/zerocost_cronjob_launcher.sh
# ════════════════════════════════════════════════════════════════════
set -u
cd /app/backend

WORKER_COUNT="${WORKER_COUNT:-16}"
WORKER_RESOLUTION="${WORKER_RESOLUTION:-6}"
GRID_FILE_PATH="${GRID_FILE_PATH:-/app/backend/cache/zerocost_v1/canada_h3_grid_r6.json}"
MAX_TILES="${MAX_TILES:-0}"
LOG_DIR="${LOG_DIR:-/tmp/zerocost_cronjob_logs}"

mkdir -p "$LOG_DIR"
rm -f "$LOG_DIR"/worker_*.log "$LOG_DIR/launcher.pid" "$LOG_DIR/state.json"

echo "═══ LANCEMENT CronJob LOCAL ZEROCOST · $WORKER_COUNT workers ═══"
echo "  Grille          : $GRID_FILE_PATH"
echo "  Résolution H3   : $WORKER_RESOLUTION"
echo "  MAX_TILES/worker: $MAX_TILES (0 = illimité)"
echo "  Logs            : $LOG_DIR/worker_*.log"
echo ""

START_TS=$(date +%s)
PIDS=()
for ((i=0; i<WORKER_COUNT; i++)); do
    GRID_FILE_PATH="$GRID_FILE_PATH" \
    WORKER_INDEX=$i \
    WORKER_COUNT=$WORKER_COUNT \
    WORKER_RESOLUTION=$WORKER_RESOLUTION \
    MAX_TILES=$MAX_TILES \
    PYTHONUNBUFFERED=1 \
    nohup python3 tools/zerocost_worker_precompute.py \
        > "$LOG_DIR/worker_${i}.log" 2>&1 &
    PIDS+=($!)
    echo "  ✓ Worker $i lancé (PID ${PIDS[$i]})"
done

# Sauvegarde state pour monitor
echo "{\"started_at\": $START_TS, \"worker_count\": $WORKER_COUNT, \"pids\": [$(IFS=,; echo "${PIDS[*]}")]}" \
    > "$LOG_DIR/state.json"

echo ""
echo "═══ Tous les workers lancés en arrière-plan ═══"
echo "Monitor : bash tools/zerocost_cronjob_monitor.sh"
echo "Kill all: kill ${PIDS[*]}"

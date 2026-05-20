#!/usr/bin/env bash
# ════════════════════════════════════════════════════════════════════
# zerocost_seed_r5_supervisor_watchdog.sh
# Wrapper FOREGROUND pour supervisor · auto-relance daemon β2-ΣΤ
# P22ΩΩ_ACTIVATION_BETA2_ST_Ω · STEEVE-MAX
# ════════════════════════════════════════════════════════════════════
# Tourne en boucle infinie · vérifie toutes les 60s si workers β2-ΣΤ vivants
# · relance si tous morts. Le process supervisor reste TOUJOURS en vie
# pour bénéficier de l'autorestart au pod-restart.

set -u
CHECK_INTERVAL_S="${CHECK_INTERVAL_S:-60}"
MIN_WORKERS="${MIN_WORKERS:-4}"
LOG_PREFIX="[β2-ΣΤ-WATCHDOG]"

echo "$LOG_PREFIX Watchdog démarré · check toutes les ${CHECK_INTERVAL_S}s · MIN_WORKERS=$MIN_WORKERS"

while true; do
    # Compter workers β2-ΣΤ vivants
    n=$(ps -ef 2>/dev/null | grep zerocost_worker_seed_r5 | grep -v grep | wc -l)

    if [[ $n -lt $MIN_WORKERS ]]; then
        echo "$LOG_PREFIX $(date -u +%Y-%m-%dT%H:%M:%SZ) · workers vivants=$n < MIN=$MIN_WORKERS · RELANCE"
        # Nettoyage state file
        bash /app/backend/tools/zerocost_seed_r5_daemon.sh stop 2>&1 | tail -2 || true
        sleep 2
        WORKER_COUNT=6 \
        GRID_FILE_PATH=/app/backend/cache/zerocost_v1/canada_h3_grid_r5_seed.json \
        MAX_R5_CELLS=0 \
        bash /app/backend/tools/zerocost_seed_r5_daemon.sh start 2>&1 | tail -3
        echo "$LOG_PREFIX Relance terminée"
    else
        # Log status léger toutes les 5 min
        if (( $(date +%s) % 300 < CHECK_INTERVAL_S )); then
            echo "$LOG_PREFIX $(date -u +%H:%M:%SZ) · workers=$n OK · load=$(uptime | awk -F'load average:' '{print $2}' | awk '{print $1}' | tr -d ',')"
        fi
    fi

    sleep $CHECK_INTERVAL_S
done

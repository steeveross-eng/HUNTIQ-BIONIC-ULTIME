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
CHECK_INTERVAL_S="${CHECK_INTERVAL_S:-45}"
MIN_WORKERS="${MIN_WORKERS:-4}"
# P22ΩΩ_WORKERS_SCALE_SAFE_Ω · 2026-02-20 · STEEVE-MAX
# Override forcé doctrinal : 12 workers SAFE LIMIT (priorité sur env supervisor).
# Précédent : 8 workers · gain attendu +50 % throughput cellulaire QC limitrophes.
TARGET_WORKERS=12
LOG_PREFIX="[β2-ΣΤ-WATCHDOG]"

echo "$LOG_PREFIX Watchdog démarré · check toutes les ${CHECK_INTERVAL_S}s · MIN_WORKERS=$MIN_WORKERS · TARGET=$TARGET_WORKERS"

while true; do
    # Compter workers β2-ΣΤ vivants
    n=$(ps -ef 2>/dev/null | grep zerocost_worker_seed_r5 | grep -v grep | wc -l)

    # P22ΩΩ_AUTOPILOT_4D_SAFE_PLUS_Ω · respawn si n < TARGET (8) pour stabilité maximale
    # P22ΩΩ_PHASE2_WORKERS_ACTIVATE_Ω · 2026-02-20 · grille bascule limitrophes
    if [[ $n -lt $MIN_WORKERS ]]; then
        echo "$LOG_PREFIX $(date -u +%Y-%m-%dT%H:%M:%SZ) · workers vivants=$n < MIN=$MIN_WORKERS · RELANCE"
        # Nettoyage state file
        bash /app/backend/tools/zerocost_seed_r5_daemon.sh stop 2>&1 | tail -2 || true
        sleep 2
        WORKER_COUNT=$TARGET_WORKERS \
        GRID_FILE_PATH=/app/backend/cache/zerocost_v1/canada_h3_grid_r5_seed_qc_limitrophes.json \
        MAX_R5_CELLS=0 \
        BLOCK_OUTSIDE_3RF=1 \
        bash /app/backend/tools/zerocost_seed_r5_daemon.sh start 2>&1 | tail -3
        echo "$LOG_PREFIX Relance terminée (TARGET=$TARGET_WORKERS · grille=QC_LIMITROPHES · ALLOWED extended)"
    else
        # Log status léger toutes les 5 min
        if (( $(date +%s) % 300 < CHECK_INTERVAL_S )); then
            echo "$LOG_PREFIX $(date -u +%H:%M:%SZ) · workers=$n OK · load=$(uptime | awk -F'load average:' '{print $2}' | awk '{print $1}' | tr -d ',')"
        fi
    fi

    sleep $CHECK_INTERVAL_S
done

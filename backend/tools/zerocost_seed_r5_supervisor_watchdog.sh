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
# P22ΩΩ_WORKERS_DOWNSCALE_4_TO_3_Ω_MINFIX · 2026-06-04 · STEEVE-MAX
# Aligne MIN_WORKERS sur TARGET_WORKERS=3 pour stopper boucle RELANCE infinie
# (sinon n=3 < MIN=4 → kill+respawn tous les 45s · workers ne progressent jamais)
MIN_WORKERS="${MIN_WORKERS:-3}"
# Conf supervisor injecte historiquement MIN_WORKERS=4 (env override le défaut
# bash). Override force assignation après TARGET_WORKERS pour garantir
# cohérence MIN <= TARGET. Verrou Phase III intact.
# P22ΩΩ_WORKERS_SCALE_SAFE_Ω · 2026-02-20 · STEEVE-MAX
# Override forcé doctrinal : 12 workers SAFE LIMIT (priorité sur env supervisor).
# Précédent : 8 workers · gain attendu +50 % throughput cellulaire QC limitrophes.
# P22ΩΩ_CPU_THROTTLING_MITIGATION_Ω · 2026-06-01 · STEEVE-MAX · ACTION COMBINÉE A+F
# Réduction défensive : 12 → 6 workers (élimine CPU throttling 99.42 % avec
# CPU quota pod = 2 vCPUs). Verrou Phase III intact · aucun engine touché.
# P22ΩΩ_WORKERS_DOWNSCALE_6_TO_4_Ω · 2026-02-XX · STEEVE-MAX · DIRECTIVE GO STANDARD
# Throttling persistant constaté = 98.3 % périodes (9180/9339). Réduction
# additionnelle 6 → 4 workers pour libérer marge CPU à FastAPI (probes <100ms)
# et stopper cascade pod restart e1_monitor. Verrou Phase III intact.
# P22ΩΩ_WORKERS_DOWNSCALE_4_TO_3_Ω · 2026-06-04 · STEEVE-MAX · DIRECTIVE GO STANDARD
# Throttling persistant 96.4 % avec 4 workers · PSI cpu full 41 % · cycle pod
# 59 min (régression). Downscale additionnel 4 → 3 workers pour garantir MTBF
# ≥ plusieurs heures et permettre cohabitation stable FastAPI + MongoDB +
# e1_monitor sur quota 2 vCPUs. Vitesse R5 réduite ~25 % attendue mais
# progression continue sans restart pod. Verrou Phase III intact · escalade
# infra CPU 2→4 vCPUs en parallèle (P1 externe plateforme).
# ─── ANCIEN ASSIGN (préservé doctrinalement) : TARGET_WORKERS=3 ───
# P22ΩΩ_WORKERS_SCALE_ELITE_PLUS_Ω_AUTODETECT · 2026-06-06 · STEEVE-MAX
# Bascule automatique 3 (preview 2vCPU) / 8 (Elite 4+vCPU) via cgroup cpu.max.
# Lecture : /sys/fs/cgroup/cpu.max format "QUOTA PERIOD" en µs (-1 = pas de
# limite). Seuil discrimination ELITE = quota ≥ 400000 (4.0 vCPUs).
# Overrides env : TARGET_WORKERS_PREVIEW / TARGET_WORKERS_ELITE.
# Verrou Phase III intact · changement strictement additif · zéro impact engine.
TARGET_WORKERS_PREVIEW="${TARGET_WORKERS_PREVIEW:-3}"
TARGET_WORKERS_ELITE="${TARGET_WORKERS_ELITE:-8}"
_CPU_QUOTA_RAW=""
if [ -r /sys/fs/cgroup/cpu.max ]; then
    _CPU_QUOTA_RAW=$(awk '{print $1}' /sys/fs/cgroup/cpu.max 2>/dev/null)
fi
# Logique sélection tier :
#   - quota numérique ≥ 400000 µs (4 vCPUs)            → ELITE
#   - quota "max" (illimité, hyperscale futur)          → ELITE
#   - sinon (2 vCPUs preview standard, ou non lisible)  → PREVIEW (défensif)
if [[ "$_CPU_QUOTA_RAW" == "max" ]]; then
    TARGET_WORKERS=$TARGET_WORKERS_ELITE
    _TIER_DETECTED="ELITE_UNLIMITED (cpu.max=max)"
elif [[ "$_CPU_QUOTA_RAW" =~ ^[0-9]+$ ]] && (( _CPU_QUOTA_RAW >= 400000 )); then
    TARGET_WORKERS=$TARGET_WORKERS_ELITE
    _TIER_DETECTED="ELITE (cpu.max=${_CPU_QUOTA_RAW}µs ≥ 400000)"
else
    TARGET_WORKERS=$TARGET_WORKERS_PREVIEW
    _TIER_DETECTED="PREVIEW (cpu.max=${_CPU_QUOTA_RAW:-unknown}µs · <400000 ou non-lisible)"
fi
# P22ΩΩ_WORKERS_DOWNSCALE_4_TO_3_Ω_HARDLOCK · 2026-06-04 · STEEVE-MAX
# HARD-OVERRIDE final de MIN_WORKERS pour neutraliser l'env supervisor
# (conf historique injecte MIN_WORKERS=4 · provoquait boucle RELANCE
# infinie après TARGET=3). Le HARD-LOCK garantit MIN==TARGET en runtime.
MIN_WORKERS=$TARGET_WORKERS
LOG_PREFIX="[β2-ΣΤ-WATCHDOG]"

echo "$LOG_PREFIX Watchdog démarré · check toutes les ${CHECK_INTERVAL_S}s · MIN_WORKERS=$MIN_WORKERS · TARGET=$TARGET_WORKERS · TIER=$_TIER_DETECTED"

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
        # P22ΩΩ_ELITE_CALIBRATION_THROTTLE_LT_5_PCT_Ω · 2026-06-06 · STEEVE-MAX
        # Activation conditionnelle stagger spawn + pacing intra-worker en TIER=ELITE.
        # Calibration mathématique : 8w × 60% vCPU = 4.8 vCPUs vs quota 4 vCPUs →
        # overshoot 20% sans pacing. WORKER_PACING_MS=50 introduit ~20% idle ratio
        # post-R5 → consommation effective ~3.8 vCPUs → throttle attendu <5%.
        # SPAWN_STAGGER_MS=2000 évite le pic de bootstrap V20 parallèle (~3-5s spike).
        # En PREVIEW : tous les paramètres restent à 0 (legacy intact).
        if [[ "$_TIER_DETECTED" == ELITE* ]]; then
            _SPAWN_STAGGER_MS="${SPAWN_STAGGER_MS:-2000}"
            _WORKER_PACING_MS="${WORKER_PACING_MS:-50}"
        else
            _SPAWN_STAGGER_MS="${SPAWN_STAGGER_MS:-0}"
            _WORKER_PACING_MS="${WORKER_PACING_MS:-0}"
        fi
        WORKER_COUNT=$TARGET_WORKERS \
        GRID_FILE_PATH=/app/backend/cache/zerocost_v1/canada_h3_grid_r5_seed_qc_limitrophes.json \
        MAX_R5_CELLS=0 \
        BLOCK_OUTSIDE_3RF=1 \
        SPAWN_STAGGER_MS="$_SPAWN_STAGGER_MS" \
        WORKER_PACING_MS="$_WORKER_PACING_MS" \
        bash /app/backend/tools/zerocost_seed_r5_daemon.sh start 2>&1 | tail -3
        echo "$LOG_PREFIX Relance terminée (TARGET=$TARGET_WORKERS · grille=QC_LIMITROPHES · stagger=${_SPAWN_STAGGER_MS}ms · pacing=${_WORKER_PACING_MS}ms)"
        # P22ΩΩ_R2_ORPHAN_STATE_PURGE_AT_BOOT_Ω · 2026-06-06 · STEEVE-MAX
        # Purge automatique des clés R2 state_worker_*.json orphelines (worker_index
        # >= TARGET_WORKERS), vestiges des cycles antérieurs (6w → 3w → 8w).
        # CROSS-POD-SAFE : ne purge que les clés matchant la grille active locale
        # (préserve pods cohabitant qui écrivent sur d'autres grilles ex Phase 1).
        # Garantit lag_max_s < 60s et sync_status OK/MATCH dans /api/v30/runtime/tier-status.
        # Best-effort · zéro impact si R2 indisponible · idempotent.
        _LOCAL_GRID="/app/backend/cache/zerocost_v1/canada_h3_grid_r5_seed_qc_limitrophes.json"
        python3 -c "
import sys
sys.path.insert(0, '/app/backend')
try:
    from integrations.r2_state_persistence_omega import prune_orphan_state_keys
    r = prune_orphan_state_keys(
        active_worker_count=$TARGET_WORKERS,
        expected_grid_file='$_LOCAL_GRID',
    )
    print(f'[R2_ORPHAN_PURGE] checked={r[\"checked\"]} · purged={len(r[\"purged\"])} · kept_active={len(r[\"kept_active\"])} · kept_other_pod={len(r[\"kept_other_pod\"])} · errors={len(r[\"errors\"])}')
    if r['purged']:
        for k in r['purged']: print(f'  PURGED      : {k}')
    if r['kept_other_pod']:
        for item in r['kept_other_pod']: print(f'  KEEP OTHER  : {item}')
    if r['errors']:
        for e in r['errors']: print(f'  ERROR       : {e}')
except Exception as e:
    print(f'[R2_ORPHAN_PURGE] skip: {e}')
" 2>&1 | head -20
    else
        # Log status léger toutes les 5 min
        if (( $(date +%s) % 300 < CHECK_INTERVAL_S )); then
            echo "$LOG_PREFIX $(date -u +%H:%M:%SZ) · workers=$n OK · load=$(uptime | awk -F'load average:' '{print $2}' | awk '{print $1}' | tr -d ',')"
        fi
    fi

    sleep $CHECK_INTERVAL_S
done

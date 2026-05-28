"""
zerocost_worker_seed_r5.py — Worker β2-ΣΤ : compute SEED R5 + fan-out R6
═══════════════════════════════════════════════════════════════════════
P22ΩΩ_PHASE3_BUNDLE_SEED_H3R5_BETA2_SIGMA_TAU_Ω · STEEVE-MAX · 2026-02-19

⚠️  STATUT : SQUELETTE READY-TO-RUN · INERTE TANT QUE COMMANDANT N'A PAS
            VALIDÉ L'ACTIVATION VIA `COMMANDE_OPERATIONNELLE_BETA2_ST_ACTIVATION_Ω.md`.

DOCTRINE
--------
Worker doublement productif :
  1. **SEED COMPUTE** : pour chaque cellule R5 attribuée, calcule le bundle V20
     une fois (~213s) au centre de la R5.
  2. **FAN-OUT** : génère 7 bundles R6 enfants via `adapt_bundle_to_r6_child`
     (zéro-cost, ~10ms par enfant) et upload tous les 7 dans R2.

→ Compression compute ×7 par rapport au worker direct R6.

USAGE (à exécuter UNIQUEMENT sur ordre Commandant) :
    GRID_FILE_PATH=/app/backend/cache/zerocost_v1/canada_h3_grid_r5_seed.json \
    WORKER_INDEX=0 WORKER_COUNT=8 \
    python3 tools/zerocost_worker_seed_r5.py
"""
import asyncio
import gzip
import json
import logging
import os
import sys
import time
from pathlib import Path

from dotenv import load_dotenv

BACKEND_ROOT = Path("/app/backend")
sys.path.insert(0, str(BACKEND_ROOT))
load_dotenv(BACKEND_ROOT / ".env")

# Interception OWM régionale (héritée du worker R6)
from engines.weather_cache_regional_omega import (  # noqa: E402
    install_open_meteo_interceptor,
    get_stats as weather_cache_stats,
)
install_open_meteo_interceptor()

import boto3  # noqa: E402
import h3  # noqa: E402

from engines.v8_institutional.v20_performance_bundle import (  # noqa: E402
    v20_territoire_bundle,
)
from tools.bundle_adapter_r5_to_r6_omega import adapt_bundle_to_r6_child  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("bionic.zerocost_worker_seed_r5")

# Configuration
WORKER_INDEX = int(os.environ.get("WORKER_INDEX", "0"))
WORKER_COUNT = int(os.environ.get("WORKER_COUNT", "8"))
MAX_R5_CELLS = int(os.environ.get("MAX_R5_CELLS", "0"))  # 0 = illimité
GRID_FILE = Path(os.environ.get(
    "GRID_FILE_PATH",
    str(BACKEND_ROOT / "cache" / "zerocost_v1" / "canada_h3_grid_r5_seed.json"),
))

# P22ΩΩ_3RF_ACCELERATION_P0_Ω · BLOCK_OUTSIDE_3RF strict (additif, défaut ON)
# P22ΩΩ_PHASE2_WORKERS_ACTIVATE_Ω · 2026-02-20 · extension aux 3 régions limitrophes QC
# (Lanaudière + Mauricie Est + Outaouais Nord) · maintient BLOCK_OUTSIDE_CANADA strict.
BLOCK_OUTSIDE_3RF = os.environ.get("BLOCK_OUTSIDE_3RF", "1") == "1"
ALLOWED_RF_LABELS = {
    # 3 RF originales (Phase 1)
    "OUTAOUAIS_RF_PAPINEAU_VERENDRYE_SUD",
    "LAURENTIDES_RF_LAURENTIDES_ROUGE_MATAWIN",
    "MAURICIE_RF_MASTIGOUCHE_ST_MAURICE",
    # Limitrophes QC priority=1 (Phase 2)
    "LANAUDIERE_LIMITROPHE",
    "MAURICIE_EST_LIMITROPHE",
    "OUTAOUAIS_NORD_LIMITROPHE",
}

SPECIES = ["chevreuil", "orignal", "ours_noir", "wapiti", "dindon_sauvage", "coyote"]
MONTHS = [4, 9, 10, 11]
HOURS = [7, 14, 19]

# R2 S3 client
S3 = boto3.client(
    "s3",
    endpoint_url=os.environ["R2_S3_ENDPOINT"],
    aws_access_key_id=os.environ["R2_ACCESS_KEY_ID"],
    aws_secret_access_key=os.environ["R2_SECRET_ACCESS_KEY"],
    region_name="auto",
)
R2_BUCKET = os.environ["CF_R2_BUCKET"]


class _R:
    """Mock FastAPI Response."""
    def __init__(self):
        self.headers = {}


def _r6_cell_key(lat: float, lng: float) -> str:
    return f"{lat:.4f}_{lng:.4f}"


def _upload_r6_bundle(species: str, r6_lat: float, r6_lng: float,
                      month: int, hour: int, bundle: dict) -> tuple[bool, int]:
    """Upload un bundle R6 dans R2."""
    cell_key = _r6_cell_key(r6_lat, r6_lng)
    key = f"v1/{species}/{cell_key}/m{month:02d}_h{hour:02d}.json.gz"
    payload = json.dumps(bundle, ensure_ascii=False).encode()
    gz = gzip.compress(payload)
    try:
        S3.put_object(
            Bucket=R2_BUCKET, Key=key, Body=gz,
            ContentType="application/json", ContentEncoding="gzip",
            CacheControl="public, max-age=3600",
        )
        return True, len(gz)
    except Exception as e:
        logger.warning(f"R2 upload failed for {key}: {e}")
        return False, 0


async def main():
    print(f"═══ ZEROCOST WORKER SEED R5 [{WORKER_INDEX}/{WORKER_COUNT}] ═══")
    print(f"  Grille R5  : {GRID_FILE}")

    grid = json.loads(GRID_FILE.read_text())
    all_r5 = grid["cells"]
    my_r5 = [c for i, c in enumerate(all_r5) if i % WORKER_COUNT == WORKER_INDEX]
    if MAX_R5_CELLS:
        my_r5 = my_r5[:MAX_R5_CELLS]

    print(f"  Cellules R5 attribuées : {len(my_r5)}")
    print(f"  Tuiles SEED à compute   : {len(my_r5) * len(SPECIES) * len(MONTHS) * len(HOURS)}")
    print(f"  Tuiles R6 à fan-out     : ~{sum(c['n_r6_children'] for c in my_r5) * len(SPECIES) * len(MONTHS) * len(HOURS)}")

    stats = {
        "seed_ok": 0, "seed_fail": 0,
        "fanout_ok": 0, "fanout_fail": 0,
        "size_bytes": 0, "start": time.time(),
    }

    for r5_idx, r5_cell in enumerate(my_r5):
        h3_r5 = r5_cell["h3_r5"]
        r5_lat = r5_cell["lat_r5"]
        r5_lng = r5_cell["lng_r5"]
        r6_children = r5_cell["r6_children"]

        for species in SPECIES:
            for month in MONTHS:
                for hour in HOURS:
                    # PHASE 1 : SEED compute V20 au centre R5
                    try:
                        seed_bundle = await v20_territoire_bundle(
                            response=_R(),
                            lat=r5_lat, lon=r5_lng,
                            species=species, month=month, hour=hour,
                            wind_deg=225.0, wind_speed=15.0,
                        )
                        stats["seed_ok"] += 1
                    except Exception as e:
                        logger.warning(f"SEED compute fail R5={h3_r5} {species} m{month}h{hour}: {e}")
                        stats["seed_fail"] += 1
                        continue

                    # PHASE 2 : FAN-OUT vers chaque R6 enfant
                    for r6_child in r6_children:
                        # P22ΩΩ_3RF_ACCELERATION_P0_Ω · skip si R6 hors 3 RF
                        if BLOCK_OUTSIDE_3RF:
                            rf_lbl = r6_child.get("rf_label")
                            if rf_lbl not in ALLOWED_RF_LABELS:
                                continue
                        r6_id = r6_child["h3_r6"]
                        r6_lat = r6_child["lat_r6"]
                        r6_lng = r6_child["lng_r6"]
                        try:
                            r6_bundle = adapt_bundle_to_r6_child(seed_bundle, r6_id)
                            ok, sz = _upload_r6_bundle(
                                species, r6_lat, r6_lng, month, hour, r6_bundle
                            )
                            if ok:
                                stats["fanout_ok"] += 1
                                stats["size_bytes"] += sz
                            else:
                                stats["fanout_fail"] += 1
                        except Exception as e:
                            stats["fanout_fail"] += 1
                            logger.warning(f"FAN-OUT fail R6={r6_id}: {e}")

        if (r5_idx + 1) % 5 == 0:
            elapsed = time.time() - stats["start"]
            rate = stats["fanout_ok"] / max(elapsed, 1)
            print(
                f"  [R5 {r5_idx+1}/{len(my_r5)}] "
                f"seed_ok={stats['seed_ok']} fanout_ok={stats['fanout_ok']} "
                f"rate={rate:.2f}r6/s"
            )

    elapsed = time.time() - stats["start"]
    print(
        f"\n═══ WORKER SEED R5 [{WORKER_INDEX}] TERMINÉ en {elapsed/60:.1f}min ═══"
        f"\n  SEED OK    : {stats['seed_ok']}"
        f"\n  SEED FAIL  : {stats['seed_fail']}"
        f"\n  FAN-OUT OK : {stats['fanout_ok']}"
        f"\n  FAN-OUT FAIL: {stats['fanout_fail']}"
        f"\n  Volume R2  : {stats['size_bytes']/1024/1024:.1f} MB"
    )
    print(f"  WeatherCache : {weather_cache_stats()}")


if __name__ == "__main__":
    asyncio.run(main())

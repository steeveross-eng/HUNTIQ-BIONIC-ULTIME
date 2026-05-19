"""
zerocost_worker_precompute.py — Worker parallélisé H3 grid Canada
================================================================
P22ΩΩ_PHASE3_CRONJOB_PARALLEL_Ω · 2026-02-XX · STEEVE-MAX

Chaque worker traite une fraction de la grille H3 Canada via :
  WORKER_INDEX={0..N-1}
  WORKER_COUNT=N
  WORKER_RESOLUTION=4|5|6

Le worker :
  1. Lit canada_h3_grid.json (généré par zerocost_canada_h3_grid_generator.py)
  2. Filtre les cellules selon (i % N == WORKER_INDEX)
  3. Précalcule chaque (cellule × espèce × mois × heure)
  4. Upload R2 immédiatement
  5. Reporte stats à la fin

Utilisé par le CronJob k8s parallel avec N workers (typiquement N=16-32).
"""
import asyncio
import gzip
import json
import os
import sys
import time
import urllib.parse
from pathlib import Path

import requests
from dotenv import load_dotenv

BACKEND_ROOT = Path("/app/backend")
sys.path.insert(0, str(BACKEND_ROOT))
load_dotenv(BACKEND_ROOT / ".env")

# P22ΩΩ_PHASE3_WEATHERCACHE_BETA2_Ω · STEEVE-MAX
# Active l'interception transparente Open-Meteo → cache régional OWM
# AVANT tout import du pipeline V20.
from engines.weather_cache_regional_omega import (  # noqa: E402
    install_open_meteo_interceptor,
    get_stats as weather_cache_stats,
)
install_open_meteo_interceptor()

# Config worker
WORKER_INDEX = int(os.environ.get("WORKER_INDEX", "0"))
WORKER_COUNT = int(os.environ.get("WORKER_COUNT", "1"))
WORKER_RESOLUTION = int(os.environ.get("WORKER_RESOLUTION", "4"))

SPECIES = ["chevreuil", "orignal", "ours_noir", "wapiti", "dindon_sauvage", "coyote"]
MONTHS = [5, 9, 10, 11]
HOURS = [7, 14, 19]

GRID_FILE = Path(
    os.environ.get(
        "GRID_FILE_PATH",
        str(BACKEND_ROOT / "cache" / "zerocost_v1" / "canada_h3_grid.json"),
    )
)
# Limite optionnelle de tuiles par worker (debug / smoke-test). 0 = illimité.
MAX_TILES = int(os.environ.get("MAX_TILES", "0"))

# Cloudflare R2
CF_API_TOKEN = os.environ["CF_API_TOKEN"]
CF_ACCOUNT_ID = os.environ["CF_ACCOUNT_ID"]
CF_R2_BUCKET = os.environ.get("CF_R2_BUCKET", "bionic-zerocost-omega")
CF_API_BASE = (
    f"https://api.cloudflare.com/client/v4/accounts/{CF_ACCOUNT_ID}"
    f"/r2/buckets/{CF_R2_BUCKET}"
)


async def _compute_bundle(lat, lon, species, month, hour):
    """Appelle V20 bundle backend localement."""
    from engines.v8_institutional.v20_performance_bundle import v20_territoire_bundle

    class _Resp:
        def __init__(self):
            self.headers = {}

    try:
        return await v20_territoire_bundle(
            response=_Resp(),
            lat=float(lat),
            lon=float(lon),
            species=str(species),
            month=int(month),
            hour=int(hour),
            wind_deg=float(225),
            wind_speed=float(15),
        )
    except Exception as e:
        return {"error": f"{type(e).__name__}: {e}"}


def _upload_tile(key, bundle):
    """Upload une tuile via API native CF R2."""
    body = json.dumps(bundle, ensure_ascii=False, default=str).encode()
    compressed = gzip.compress(body, compresslevel=9)
    encoded_key = urllib.parse.quote(key, safe="")
    r = requests.put(
        f"{CF_API_BASE}/objects/{encoded_key}",
        headers={
            "Authorization": f"Bearer {CF_API_TOKEN}",
            "Content-Type": "application/json",
            "Content-Encoding": "gzip",
        },
        data=compressed,
        timeout=30,
    )
    return r.status_code == 200, len(compressed)


async def main():
    print(
        f"═══ ZEROCOST WORKER [{WORKER_INDEX}/{WORKER_COUNT}] · "
        f"H3-{WORKER_RESOLUTION} ═══"
    )

    # 1. Charge la grille H3
    if not GRID_FILE.exists():
        print(
            f"🔴 Grille H3 introuvable : {GRID_FILE}\n"
            f"   Lancer d'abord : python3 tools/zerocost_canada_h3_grid_generator.py "
            f"--resolution {WORKER_RESOLUTION}"
        )
        sys.exit(1)
    grid_data = json.loads(GRID_FILE.read_text())
    all_cells = grid_data["cells"]

    # 2. Filtre cellules pour ce worker
    my_cells = [
        c for i, c in enumerate(all_cells) if i % WORKER_COUNT == WORKER_INDEX
    ]
    print(
        f"  • Cellules totales grille : {len(all_cells)}"
        f"\n  • Cellules pour ce worker : {len(my_cells)}"
    )

    n_tiles_expected = len(my_cells) * len(SPECIES) * len(MONTHS) * len(HOURS)
    print(f"  • Tuiles à générer        : {n_tiles_expected}")

    # 3. Boucle compute + upload
    stats = {"ok": 0, "fail": 0, "halt": 0, "size_bytes": 0, "start": time.time()}
    n_total_tiles = 0
    for cell_idx, cell in enumerate(my_cells):
        lat = cell["lat"]
        lng = cell["lng"]
        for species in SPECIES:
            for month in MONTHS:
                for hour in HOURS:
                    if MAX_TILES and n_total_tiles >= MAX_TILES:
                        break
                    n_total_tiles += 1
                    bundle = await _compute_bundle(lat, lng, species, month, hour)
                    if "error" in bundle:
                        stats["fail"] += 1
                        continue
                    if bundle.get("bio_presence_mask_halt"):
                        stats["halt"] += 1
                    # Upload immédiat
                    lat_q = f"{lat:.4f}"
                    lng_q = f"{lng:.4f}"
                    key = (
                        f"v1/{species}/{lat_q}_{lng_q}/m{month:02d}_h{hour:02d}.json.gz"
                    )
                    ok, size = _upload_tile(key, bundle)
                    if ok:
                        stats["ok"] += 1
                        stats["size_bytes"] += size
                    else:
                        stats["fail"] += 1
            if MAX_TILES and n_total_tiles >= MAX_TILES:
                break
        if MAX_TILES and n_total_tiles >= MAX_TILES:
            break
        # Progress log every 10 cells
        if (cell_idx + 1) % 10 == 0:
            elapsed = time.time() - stats["start"]
            rate = stats["ok"] / max(elapsed, 1)
            print(
                f"    [{cell_idx+1}/{len(my_cells)}] "
                f"ok={stats['ok']} fail={stats['fail']} halt={stats['halt']} "
                f"rate={rate:.1f}t/s"
            )

    elapsed = time.time() - stats["start"]
    print(
        f"\n═══ WORKER [{WORKER_INDEX}] TERMINÉ en {elapsed/60:.1f}min ═══"
        f"\n  Tuiles OK    : {stats['ok']}"
        f"\n  Tuiles FAIL  : {stats['fail']}"
        f"\n  Mask HALT    : {stats['halt']}"
        f"\n  Volume       : {stats['size_bytes']/1024/1024:.1f} MB"
    )
    print(f"  WeatherCache : {weather_cache_stats()}")


if __name__ == "__main__":
    asyncio.run(main())

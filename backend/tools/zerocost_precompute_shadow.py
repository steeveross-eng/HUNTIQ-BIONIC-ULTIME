"""
zerocost_precompute_shadow.py — ZEROCOST ENGINE Phase 1 shadow
================================================================
P22ΩΩ_ZEROCOST_PHASE1_SHADOW_ET_LKG_Ω · 2026-02-XX · STEEVE-MAX

Précalcule les bundles TERRITOIRE Ω pour des territoires pilotes (BSL + 1 autre)
en mode SHADOW : aucun branchement frontend, aucun upload distant. Stocke
les tuiles dans /app/backend/cache/zerocost_v1/ et génère un rapport de
comparaison + manifest.json.

Doctrine NEVER BLANK Ω : ce script appelle V20 bundle directement (pas via HTTP
pour éviter les déconnexions). En cas d'échec, log + skip (jamais de crash).

USAGE :
    cd /app/backend && python3 tools/zerocost_precompute_shadow.py

OUTPUT :
    /app/backend/cache/zerocost_v1/manifest.json
    /app/backend/cache/zerocost_v1/{species}/{lat_q}|{lng_q}/m{month}_h{hour}.json.gz
"""
import asyncio
import gzip
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# Bootstrap path pour imports backend
BACKEND_ROOT = Path("/app/backend")
sys.path.insert(0, str(BACKEND_ROOT))

OUTPUT_ROOT = Path("/app/backend/cache/zerocost_v1")
OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)

# ──────────────────────────────────────────────────────────────────────────
# P22ΩΩ_PHASE3_PREPARE_ZEROCOST_CANADA_Ω · 2026-02-XX · STEEVE-MAX
# CONFIG PILOTES — 12 territoires Canada (toutes provinces majeures de chasse)
# ──────────────────────────────────────────────────────────────────────────
TERRITORIES = [
    # QUÉBEC — pilotes initiaux (déjà validés Phase 1)
    {"name": "QC_BSL_RIMOUSKI",     "lat": 48.206657, "lng": -68.382422, "province": "QC", "description": "Bas-Saint-Laurent"},
    {"name": "QC_OUTAOUAIS",        "lat": 45.476542, "lng": -75.701271, "province": "QC", "description": "Outaouais Gatineau"},
    {"name": "QC_LAURENTIDES",      "lat": 46.000000, "lng": -74.500000, "province": "QC", "description": "Laurentides Mont-Tremblant"},
    {"name": "QC_SAGUENAY",         "lat": 48.428000, "lng": -71.068000, "province": "QC", "description": "Saguenay-Lac-Saint-Jean"},
    # ONTARIO
    {"name": "ON_ALGONQUIN",        "lat": 45.836389, "lng": -78.380000, "province": "ON", "description": "Parc Algonquin"},
    {"name": "ON_TIMMINS",          "lat": 48.475000, "lng": -81.330833, "province": "ON", "description": "Nord-Est Ontario chasse"},
    # NOUVEAU-BRUNSWICK
    {"name": "NB_MIRAMICHI",        "lat": 47.000000, "lng": -65.566667, "province": "NB", "description": "Miramichi chasse orignal"},
    # NOUVELLE-ÉCOSSE
    {"name": "NS_CAPE_BRETON",      "lat": 46.250000, "lng": -60.500000, "province": "NS", "description": "Cape Breton highlands"},
    # MANITOBA
    {"name": "MB_RIDING_MOUNTAIN",  "lat": 50.683333, "lng": -100.000000, "province": "MB", "description": "Riding Mountain Park"},
    # ALBERTA
    {"name": "AB_FOOTHILLS",        "lat": 53.500000, "lng": -116.000000, "province": "AB", "description": "Foothills wapiti/orignal"},
    # COLOMBIE-BRITANNIQUE
    {"name": "BC_KOOTENAY",         "lat": 49.500000, "lng": -116.500000, "province": "BC", "description": "Kootenay ours/wapiti"},
    # SASKATCHEWAN
    {"name": "SK_PRINCE_ALBERT",    "lat": 53.916667, "lng": -106.000000, "province": "SK", "description": "Prince Albert National Park"},
]

SPECIES_CANONICAL = ["chevreuil", "orignal", "ours_noir", "wapiti", "dindon_sauvage", "coyote"]
# P22ΩΩ_PHASE3_PREPARE_ZEROCOST_CANADA_Ω : mode LIGHT pour sandbox single-worker
# 1 mois × 1 créneau = 72 tuiles Canada (12 territoires × 6 espèces).
# Le mode FULL (4 mois × 3 créneaux = 864) sera lancé via CronJob k8s en prod.
import os
_LIGHT_MODE = os.environ.get("ZEROCOST_LIGHT_MODE", "1") == "1"
MONTHS_PILOT = [10] if _LIGHT_MODE else [5, 9, 10, 11]
HOURS_PILOT = [14] if _LIGHT_MODE else [7, 14, 19]


async def _compute_bundle(lat: float, lon: float, species: str, month: int, hour: int) -> dict:
    """Appelle V20 bundle backend localement avec conversion explicite des types.

    P22ΩΩ_PHASE3_PREPARE_ZEROCOST_CANADA_Ω : conversion explicite int() pour
    éviter le bug 'Query × int' qui survient quand FastAPI Query() est passé
    comme défaut et que le code interne fait une multiplication arithmétique.
    """
    from engines.v8_institutional.v20_performance_bundle import v20_territoire_bundle

    class _Resp:
        def __init__(self):
            self.headers = {}

    try:
        result = await v20_territoire_bundle(
            response=_Resp(),
            lat=float(lat),
            lon=float(lon),
            species=str(species),
            month=int(month),
            hour=int(hour),
            wind_deg=float(225),
            wind_speed=float(15),
        )
        return result if isinstance(result, dict) else {"error": "non_dict_result"}
    except Exception as e:
        return {"error": f"{type(e).__name__}: {str(e)[:200]}"}


def _tile_path(species: str, lat: float, lng: float, month: int, hour: int) -> Path:
    lat_q = f"{lat:.4f}"
    lng_q = f"{lng:.4f}"
    cell_dir = OUTPUT_ROOT / species / f"{lat_q}_{lng_q}"
    cell_dir.mkdir(parents=True, exist_ok=True)
    return cell_dir / f"m{month:02d}_h{hour:02d}.json.gz"


def _save_tile(path: Path, bundle: dict) -> dict:
    """Sérialise bundle en JSON gzippé. Retourne stats."""
    # Cleanup non-serializable: certains champs peuvent contenir des objets exotiques
    try:
        body = json.dumps(bundle, ensure_ascii=False, default=str).encode("utf-8")
    except Exception as e:
        return {"error": f"json_encode_failed: {e}"}
    compressed = gzip.compress(body, compresslevel=9)
    path.write_bytes(compressed)
    return {
        "size_raw_bytes": len(body),
        "size_gz_bytes": len(compressed),
        "ratio": round(len(body) / max(len(compressed), 1), 2),
    }


async def precompute_shadow() -> dict:
    """Boucle principale : pour chaque territoire × espèce × mois × heure, génère tuile."""
    manifest = {
        "doctrine": "P22ΩΩ_ZEROCOST_PHASE3_CANADA_Ω",
        "schema_version": 1,
        "started_at": datetime.now(timezone.utc).isoformat(),
        "territories": [t["name"] for t in TERRITORIES],
        "species": SPECIES_CANONICAL,
        "months": MONTHS_PILOT,
        "hours": HOURS_PILOT,
        "tiles": [],
        "summary": {
            "total_attempted": 0,
            "total_succeeded": 0,
            "total_failed": 0,
            "total_mask_halt": 0,
            "total_size_raw_bytes": 0,
            "total_size_gz_bytes": 0,
            "total_compute_ms": 0,
        },
    }

    # P22ΩΩ_PHASE3_PREPARE_ZEROCOST_CANADA_Ω : délais anti rate-limit Open-Meteo
    # Open-Meteo CB circuit ouvre après 3 erreurs en 90s. Délai 100ms entre tuiles
    # + 5s entre territoires laisse le CB respirer.
    INTER_TILE_DELAY_S = 0.10
    INTER_TERRITORY_DELAY_S = 5.0
    MAX_RETRIES_PER_TILE = 2

    for terr_idx, territory in enumerate(TERRITORIES):
        if terr_idx > 0:
            await asyncio.sleep(INTER_TERRITORY_DELAY_S)
        print(f"\n▼ TERRITOIRE [{terr_idx+1}/{len(TERRITORIES)}] {territory['name']}")
        for species in SPECIES_CANONICAL:
            for month in MONTHS_PILOT:
                for hour in HOURS_PILOT:
                    manifest["summary"]["total_attempted"] += 1
                    t0 = time.time()
                    bundle = None
                    last_err = None
                    for retry in range(MAX_RETRIES_PER_TILE):
                        bundle = await _compute_bundle(
                            territory["lat"], territory["lng"], species, month, hour
                        )
                        if "error" not in bundle:
                            break
                        last_err = bundle.get("error", "?")
                        await asyncio.sleep(2.0)
                    elapsed_ms = int((time.time() - t0) * 1000)
                    manifest["summary"]["total_compute_ms"] += elapsed_ms

                    if not bundle or "error" in bundle:
                        manifest["summary"]["total_failed"] += 1
                        manifest["tiles"].append({
                            "territory": territory["name"],
                            "species": species,
                            "month": month,
                            "hour": hour,
                            "status": "FAILED",
                            "error": last_err or (bundle or {}).get("error"),
                            "compute_ms": elapsed_ms,
                        })
                        print(f"  [FAIL] {species}/m{month}/h{hour} → {(last_err or '?')[:80]}")
                        await asyncio.sleep(INTER_TILE_DELAY_S)
                        continue

                    is_halt = bool(bundle.get("bio_presence_mask_halt"))
                    if is_halt:
                        manifest["summary"]["total_mask_halt"] += 1

                    tile_path = _tile_path(
                        species, territory["lat"], territory["lng"], month, hour
                    )
                    save_stats = _save_tile(tile_path, bundle)
                    if "error" in save_stats:
                        manifest["summary"]["total_failed"] += 1
                        await asyncio.sleep(INTER_TILE_DELAY_S)
                        continue

                    manifest["summary"]["total_succeeded"] += 1
                    manifest["summary"]["total_size_raw_bytes"] += save_stats["size_raw_bytes"]
                    manifest["summary"]["total_size_gz_bytes"] += save_stats["size_gz_bytes"]

                    bundle_summary = {
                        "territory": territory["name"],
                        "province": territory.get("province"),
                        "species": species,
                        "month": month,
                        "hour": hour,
                        "path": str(tile_path.relative_to(OUTPUT_ROOT)),
                        "status": "OK_HALT" if is_halt else "OK",
                        "n_corridors": len(bundle.get("corridors", []) or []),
                        "bundle_tier": bundle.get("bundle_tier"),
                        "score_local": (
                            bundle.get("score_local", {}).get("value")
                            if isinstance(bundle.get("score_local"), dict)
                            else None
                        ),
                        "compute_ms": elapsed_ms,
                        **save_stats,
                    }
                    manifest["tiles"].append(bundle_summary)
                    if manifest["summary"]["total_succeeded"] % 50 == 0:
                        print(
                            f"  ... {manifest['summary']['total_succeeded']} OK / "
                            f"{manifest['summary']['total_failed']} FAIL"
                        )
                    await asyncio.sleep(INTER_TILE_DELAY_S)

    manifest["completed_at"] = datetime.now(timezone.utc).isoformat()
    manifest_path = OUTPUT_ROOT / "manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return manifest


def print_summary_report(manifest: dict) -> None:
    """Affiche un rapport de comparaison live vs shadow."""
    s = manifest["summary"]
    print("\n" + "═" * 75)
    print("ZEROCOST PHASE 1 SHADOW · RAPPORT DE PRÉCALCUL")
    print("═" * 75)
    print(f"Territoires        : {', '.join(manifest['territories'])}")
    print(f"Espèces            : {', '.join(manifest['species'])}")
    print(f"Mois × heures      : {len(manifest['months'])} × {len(manifest['hours'])}")
    print("─" * 75)
    print(f"Tuiles tentées     : {s['total_attempted']}")
    print(f"Tuiles OK          : {s['total_succeeded']}  ({100*s['total_succeeded']/max(s['total_attempted'],1):.0f}%)")
    print(f"Tuiles MASK_HALT   : {s['total_mask_halt']}")
    print(f"Tuiles échouées    : {s['total_failed']}")
    print("─" * 75)
    print(f"Taille RAW totale  : {s['total_size_raw_bytes']/1024:.1f} KB")
    print(f"Taille GZ totale   : {s['total_size_gz_bytes']/1024:.1f} KB")
    if s['total_size_gz_bytes'] > 0:
        ratio = s['total_size_raw_bytes'] / s['total_size_gz_bytes']
        print(f"Ratio compression  : {ratio:.1f}×")
    print(f"Temps compute total: {s['total_compute_ms']/1000:.1f}s")
    if s['total_succeeded'] > 0:
        print(f"Compute médian     : {s['total_compute_ms']/s['total_succeeded']:.0f}ms/tuile")
    print("─" * 75)
    # Extrapolation coût production
    n_total_qc = 50000 * 6 * len(manifest['months']) * len(manifest['hours'])
    avg_gz_kb = s['total_size_gz_bytes'] / max(s['total_succeeded'], 1) / 1024
    total_gb = n_total_qc * avg_gz_kb / (1024 * 1024)
    print("EXTRAPOLATION QC :")
    print(f"  tuiles totales   : {n_total_qc:,}")
    print(f"  volume estimé    : {total_gb:.1f} GB")
    print(f"  coût stockage B2 : ${total_gb * 0.006:.2f}/mois")
    print("═" * 75)


if __name__ == "__main__":
    print("[ZEROCOST SHADOW] Démarrage précalcul Phase 1...")
    print(f"Output: {OUTPUT_ROOT}")
    manifest = asyncio.run(precompute_shadow())
    print_summary_report(manifest)
    print(f"\n✅ Manifest: {OUTPUT_ROOT / 'manifest.json'}")

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
# CONFIG PILOTES — 2 territoires : BSL + Outaouais
# ──────────────────────────────────────────────────────────────────────────
TERRITORIES = [
    {
        "name": "BSL_RIMOUSKI",
        "lat": 48.206657,
        "lng": -68.382422,
        "description": "Bas-Saint-Laurent pilote initial",
    },
    {
        "name": "OUTAOUAIS_GATINEAU",
        "lat": 45.476542,
        "lng": -75.701271,
        "description": "Outaouais pilote secondaire",
    },
]

SPECIES_CANONICAL = ["chevreuil", "orignal", "ours_noir", "wapiti", "dindon_sauvage", "coyote"]
MONTHS_PILOT = [5, 9, 10, 11]  # Mai, Sept, Oct, Nov (saisons chasse principales)
HOURS_PILOT = [7, 14, 19]      # AM, mi-jour, PM (créneaux activité)


async def _compute_bundle(lat: float, lon: float, species: str, month: int, hour: int) -> dict:
    """Appelle V20 bundle backend localement et retourne le bundle complet."""
    from engines.v8_institutional.v20_performance_bundle import v20_territoire_bundle
    from fastapi import Response as FakeResponse

    # Faux Response pour capturer les headers (non utilisés en shadow)
    class _Resp:
        def __init__(self):
            self.headers = {}

    fake_resp = _Resp()
    try:
        result = await v20_territoire_bundle(
            response=fake_resp,
            lat=lat,
            lon=lon,
            species=species,
            month=month,
            hour=hour,
            wind_deg=225,
        )
        return result if isinstance(result, dict) else {"error": "non_dict_result"}
    except Exception as e:
        return {"error": str(e), "type": type(e).__name__}


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
        "doctrine": "P22ΩΩ_ZEROCOST_PHASE1_SHADOW_Ω",
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

    for territory in TERRITORIES:
        for species in SPECIES_CANONICAL:
            for month in MONTHS_PILOT:
                for hour in HOURS_PILOT:
                    manifest["summary"]["total_attempted"] += 1
                    t0 = time.time()
                    bundle = await _compute_bundle(
                        territory["lat"], territory["lng"], species, month, hour
                    )
                    elapsed_ms = int((time.time() - t0) * 1000)
                    manifest["summary"]["total_compute_ms"] += elapsed_ms

                    if "error" in bundle:
                        manifest["summary"]["total_failed"] += 1
                        manifest["tiles"].append({
                            "territory": territory["name"],
                            "species": species,
                            "month": month,
                            "hour": hour,
                            "status": "FAILED",
                            "error": bundle.get("error"),
                            "compute_ms": elapsed_ms,
                        })
                        print(f"[FAIL] {territory['name']}/{species}/m{month}/h{hour} → {bundle.get('error')[:80]}")
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
                        continue

                    manifest["summary"]["total_succeeded"] += 1
                    manifest["summary"]["total_size_raw_bytes"] += save_stats["size_raw_bytes"]
                    manifest["summary"]["total_size_gz_bytes"] += save_stats["size_gz_bytes"]

                    bundle_summary = {
                        "territory": territory["name"],
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
                    print(
                        f"[OK] {territory['name']}/{species}/m{month}/h{hour} "
                        f"n_corr={bundle_summary['n_corridors']} "
                        f"size={save_stats['size_gz_bytes']/1024:.1f}KB "
                        f"compute={elapsed_ms}ms"
                    )

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

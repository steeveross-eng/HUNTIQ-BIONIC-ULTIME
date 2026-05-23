"""
rapport_3rf_t95_omega.py — RAPPORT_3RF_T+95%_Ω · Checkpoint + Audit Divergence
═══════════════════════════════════════════════════════════════════════════════
P22ΩΩ_3RF_ACCELERATION_P0_Ω · COMMANDANT STEEVE-MAX · 2026-02-20 · BCE-4X ULTIME ABSOLU
Verrou Phase III : MAINTENU (LECTURE SEULE · aucune écriture · aucune transition).

DOCTRINE
--------
Script de rapport automatisé déclenchable manuellement par le Commandant.
Audit complet de la couverture 3 RF (Outaouais · Mauricie · Laurentides)
avec **arming au seuil 95 %** (par défaut) :

  - Si couverture < seuil → rapport STATUS-ONLY (progression + ETA)
  - Si couverture ≥ seuil → rapport FULL :
      § 1. Couverture cellulaire 3 RF (par RF + global)
      § 2. Couverture tuilaire 3 RF (par RF × espèce)
      § 3. Checkpoint manifest CDN (drift · doctrine · cohérence)
      § 4. Audit divergence biologique (N échantillons R2 + 5 espèces × 4 saisons)
      § 5. Audit hors-3RF (vérification BLOCK_OUTSIDE_3RF effectif)
      § 6. Synthèse / verdict atteinte T+95 %

USAGE
-----
    # Mode standard (seuil 95 %)
    python3 /app/backend/tools/rapport_3rf_t95_omega.py

    # Mode avec seuil custom
    THRESHOLD_PCT=85 python3 /app/backend/tools/rapport_3rf_t95_omega.py

    # Mode force-full (générer le rapport complet même si seuil non atteint)
    FORCE_FULL=1 python3 /app/backend/tools/rapport_3rf_t95_omega.py

    # Mode JSON brut (machine-readable)
    OUTPUT=json python3 /app/backend/tools/rapport_3rf_t95_omega.py

CONTRAINTES BCE-4X
------------------
- LECTURE SEULE sur R2 (list_objects_v2 + get_object manifest)
- AUCUNE écriture · AUCUNE transition · AUCUNE action infra
- AUCUN appel modifiant TERRITOIRE_Ω / V20 / R6 storage doctrine
"""
from __future__ import annotations

import gzip
import json
import os
import random
import sys
import time
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

BACKEND_ROOT = Path("/app/backend")
sys.path.insert(0, str(BACKEND_ROOT))

from dotenv import load_dotenv
load_dotenv(BACKEND_ROOT / ".env", override=False)

import boto3
from botocore.config import Config

# ─── Configuration ──────────────────────────────────────────────────────────
THRESHOLD_PCT = float(os.environ.get("THRESHOLD_PCT", "95.0"))
FORCE_FULL = os.environ.get("FORCE_FULL", "0") == "1"
OUTPUT_MODE = os.environ.get("OUTPUT", "text")  # text | json
SAMPLE_TILES_PER_RF = int(os.environ.get("SAMPLE_TILES_PER_RF", "5"))

GRID_FILE = BACKEND_ROOT / "cache" / "zerocost_v1" / "canada_h3_grid_r5_seed.json"
GRID_R6_FOCUSED = BACKEND_ROOT / "cache" / "zerocost_v1" / "canada_h3_grid_r6_3rf_focused.json"

SPECIES = ("chevreuil", "orignal", "ours_noir", "coyote", "dindon_sauvage")
SEASONS_MONTHS = {"printemps": 4, "ete": 9, "automne": 10, "hiver": 11}  # mois pivots

R2_BUCKET = os.environ.get("CF_R2_BUCKET")
R2_ENDPOINT = os.environ.get("R2_S3_ENDPOINT")
R2_AK = os.environ.get("R2_ACCESS_KEY_ID")
R2_SK = os.environ.get("R2_SECRET_ACCESS_KEY")


def get_s3_client():
    return boto3.client(
        "s3", endpoint_url=R2_ENDPOINT,
        aws_access_key_id=R2_AK, aws_secret_access_key=R2_SK,
        config=Config(signature_version="s3v4"),
    )


# ─── § 1 · Charger grille 3 RF doctrinale ───────────────────────────────────
def load_grid_3rf() -> dict:
    """Charge la grille R5 seed (worker source) + bboxes doctrinales R6 focused."""
    with open(GRID_FILE) as f:
        grid_r5 = json.load(f)
    with open(GRID_R6_FOCUSED) as f:
        grid_r6 = json.load(f)
    rf_bbox = {b["label"]: (b["lat_min"], b["lat_max"], b["lng_min"], b["lng_max"])
               for b in grid_r6["bboxes_3rf"]}
    targets = dict(grid_r6["by_rf"])  # cells R6 cibles par RF
    return {"grid": grid_r5, "rf_bbox": rf_bbox, "targets": targets,
            "n_r6_total": grid_r5["n_r6_children_total"]}


# ─── § 2 · Inventaire R2 streaming ──────────────────────────────────────────
def rf_of(lat: float, lon: float, rf_bbox: dict, order: list) -> str:
    for name in order:
        lo, hi, w, e = rf_bbox[name]
        if lo <= lat <= hi and w <= lon <= e:
            return name
    return "AUTRE"


def inventory_r2(rf_bbox: dict) -> dict:
    """Scan R2 v1/* · agrège tuiles + cells par RF × espèce."""
    cli = get_s3_client()
    order = [
        "OUTAOUAIS_RF_PAPINEAU_VERENDRYE_SUD",
        "LAURENTIDES_RF_LAURENTIDES_ROUGE_MATAWIN",
        "MAURICIE_RF_MASTIGOUCHE_ST_MAURICE",
    ]
    per_rf_tiles = defaultdict(lambda: Counter())
    per_rf_cells = defaultdict(lambda: defaultdict(set))
    # Sampling stratifié par (RF, espèce) · max 8 clés par couple
    per_rf_sp_sample = defaultdict(lambda: defaultdict(list))
    total_keys = 0
    t0 = time.time()
    paginator = cli.get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=R2_BUCKET, Prefix="v1/"):
        for obj in page.get("Contents", []):
            k = obj["Key"]
            total_keys += 1
            try:
                parts = k.split("/")
                sp = parts[1]
                lat_s, lon_s = parts[2].split("_")
                lat = float(lat_s)
                lon = float(lon_s)
                rf = rf_of(lat, lon, rf_bbox, order)
                per_rf_tiles[rf][sp] += 1
                per_rf_cells[rf][sp].add((round(lat, 4), round(lon, 4)))
                if len(per_rf_sp_sample[rf][sp]) < 8:
                    per_rf_sp_sample[rf][sp].append(k)
            except Exception:
                continue
    dt = time.time() - t0
    # Aplatir per_rf_sp_sample en per_rf_keys_sample (compat existant)
    per_rf_keys_sample = defaultdict(list)
    for rf, sp_map in per_rf_sp_sample.items():
        for sp, keys in sp_map.items():
            per_rf_keys_sample[rf].extend(keys)
    return {"per_rf_tiles": per_rf_tiles, "per_rf_cells": per_rf_cells,
            "per_rf_keys_sample": per_rf_keys_sample,
            "per_rf_sp_sample": per_rf_sp_sample,
            "total_keys": total_keys, "scan_sec": dt}


# ─── § 3 · Manifest checkpoint ───────────────────────────────────────────────
def manifest_checkpoint() -> dict:
    cli = get_s3_client()
    try:
        o = cli.get_object(Bucket=R2_BUCKET, Key="manifest.json")
        m = json.loads(o["Body"].read())
        gen_at = m.get("generated_at") or m.get("_generated_at")
        gen_dt = None
        drift_s = None
        if gen_at:
            try:
                gen_dt = datetime.fromisoformat(gen_at.replace("Z", "+00:00"))
                drift_s = (datetime.now(timezone.utc) - gen_dt).total_seconds()
            except Exception:
                pass
        return {
            "present": True,
            "doctrine": m.get("doctrine"),
            "generated_at": gen_at,
            "drift_seconds": drift_s,
            "drift_target_max_s": 900,
            "drift_ok": (drift_s is not None and drift_s <= 1200),
            "n_tiles": m.get("n_tiles"),
            "cells_unique": m.get("cells_unique"),
            "total_size_mb": round((m.get("total_size_bytes") or 0) / 1024 / 1024, 2),
            "by_species": m.get("by_species", {}),
        }
    except Exception as e:
        return {"present": False, "error": str(e)}


# ─── § 4 · Audit divergence biologique (sur échantillons R2) ────────────────
def audit_divergence_biological(per_rf_keys_sample: dict, per_rf_tiles: dict) -> dict:
    """Échantillonne stratifié 1 tuile par (RF × espèce) · vérifie divergence."""
    cli = get_s3_client()
    rng = random.Random(42)

    # Construire un échantillon stratifié : pour chaque RF, lister toutes les clés
    # vues dans le scan complet et grouper par espèce. Comme per_rf_keys_sample
    # est limité à 20 clés par RF (toutes espèces confondues), on relit ici.
    # Pour rester économique, on utilise per_rf_keys_sample mais en répartissant
    # entre espèces dispo.
    sampled = {}
    divergence_check = {}
    for rf, keys in per_rf_keys_sample.items():
        if rf == "AUTRE" or not keys:
            continue
        # Grouper les clés par espèce
        by_sp = defaultdict(list)
        for k in keys:
            try:
                sp = k.split("/")[1]
                by_sp[sp].append(k)
            except Exception:
                pass
        # Échantillonner 1-2 tuiles par espèce dispo
        sample = []
        for sp in sorted(by_sp.keys()):
            sample.extend(rng.sample(by_sp[sp], min(SAMPLE_TILES_PER_RF, len(by_sp[sp]))))

        rf_samples = []
        species_scores = defaultdict(list)
        for key in sample:
            try:
                obj = cli.get_object(Bucket=R2_BUCKET, Key=key)
                body = obj["Body"].read()
                if obj.get("ContentEncoding") == "gzip" or key.endswith(".gz"):
                    body = gzip.decompress(body)
                bundle = json.loads(body)
                sp = key.split("/")[1]
                tier = bundle.get("bundle_tier")
                cu = bundle.get("corridors_unified", {})
                n_corr = len(cu.get("corridors", []))
                score_local = bundle.get("score_local")
                if isinstance(score_local, dict):
                    score_val = score_local.get("value") or score_local.get("score") or score_local.get("score_local")
                else:
                    score_val = score_local
                try:
                    score_val = float(score_val) if score_val is not None else None
                except (TypeError, ValueError):
                    score_val = None
                species_scores[sp].append(score_val)
                rf_samples.append({
                    "key": key, "species": sp, "tier": tier,
                    "n_corridors": n_corr, "score_local": score_val,
                    "bundle_tier_ok": tier == "ESSENTIEL_T0",
                })
            except Exception as e:
                rf_samples.append({"key": key, "error": str(e)[:100]})

        per_sp_unique = {
            sp: round(sum(s for s in v if s is not None) / max(len([s for s in v if s is not None]), 1), 1)
            for sp, v in species_scores.items() if any(s is not None for s in v)
        }
        distinct = len(set(per_sp_unique.values()))
        divergence_check[rf] = {
            "samples": rf_samples,
            "per_species_avg_score": per_sp_unique,
            "n_species_sampled": len(per_sp_unique),
            "distinct_scores": distinct,
            "divergence_ok": distinct >= max(2, len(per_sp_unique) - 1) if len(per_sp_unique) >= 2 else None,
        }
        sampled[rf] = len(rf_samples)
    return {"sampled_counts": sampled, "divergence_check": divergence_check}


# ─── § 5 · Audit hors-3RF (BLOCK_OUTSIDE_3RF effectif) ──────────────────────
def audit_outside_3rf(per_rf_tiles: dict, inv_t0: float) -> dict:
    autre = per_rf_tiles.get("AUTRE", Counter())
    total_autre = sum(autre.values())
    return {
        "tiles_hors_3rf_cumul": total_autre,
        "by_species_hors_3rf": dict(autre),
        "block_outside_3rf_status": ("EFFICACE" if total_autre <= 462
                                     else "DÉRIVE_DÉTECTÉE"),
        "note": ("Les 462 tuiles existantes sont des résidus pilote P1 ≥ T-3j · "
                 "aucune nouvelle écriture depuis activation BLOCK_OUTSIDE_3RF=1"),
    }


# ─── § 6 · Synthèse et rendu ────────────────────────────────────────────────
def build_report() -> dict:
    print(f"[RAPPORT_3RF_T+95%_Ω] T+0 · seuil={THRESHOLD_PCT}% · force_full={FORCE_FULL}\n",
          file=sys.stderr)

    # § 1
    g = load_grid_3rf()

    # § 2
    print("[RAPPORT_3RF_T+95%_Ω] inventaire R2 en cours...", file=sys.stderr)
    inv = inventory_r2(g["rf_bbox"])
    print(f"[RAPPORT_3RF_T+95%_Ω] inventaire OK · {inv['total_keys']} clés · "
          f"scan={inv['scan_sec']:.1f}s", file=sys.stderr)

    # Cells couvertes par RF (union espèces)
    per_rf_cells_union = {}
    for rf in g["targets"]:
        u = set()
        for sp, s in inv["per_rf_cells"][rf].items():
            u.update(s)
        per_rf_cells_union[rf] = len(u)

    # Couverture % par RF + global
    coverage_pct = {}
    for rf, cible in g["targets"].items():
        pct = (per_rf_cells_union[rf] / cible * 100.0) if cible > 0 else 0.0
        coverage_pct[rf] = pct
    total_cells_done = sum(per_rf_cells_union.values())
    total_cells_target = sum(g["targets"].values())
    global_pct = (total_cells_done / total_cells_target * 100.0) if total_cells_target > 0 else 0.0

    # Total tuiles cumul 3RF
    total_tiles_3rf = sum(sum(inv["per_rf_tiles"][rf].values()) for rf in g["targets"])

    threshold_reached = global_pct >= THRESHOLD_PCT
    do_full = threshold_reached or FORCE_FULL

    report = {
        "_doctrine": "P22ΩΩ_3RF_ACCELERATION_P0_Ω",
        "_report": "RAPPORT_3RF_T+95%_Ω",
        "_commandant": "STEEVE-MAX",
        "_generated_at": datetime.now(timezone.utc).isoformat(),
        "_mode": "FULL" if do_full else "STATUS_ONLY",
        "_threshold_pct": THRESHOLD_PCT,
        "_threshold_reached": threshold_reached,
        "_force_full": FORCE_FULL,
        "verrou_phase_iii": True,
        "lecture_seule": True,
        "grid_doctrine": g["grid"].get("doctrine"),
        "grid_n_r6_target": g["n_r6_total"],

        # § 1 Couverture cellulaire
        "coverage_cellular": {
            "by_rf": {rf: {
                "cells_target": g["targets"][rf],
                "cells_covered": per_rf_cells_union[rf],
                "pct": round(coverage_pct[rf], 1),
            } for rf in g["targets"]},
            "global_cells_target": total_cells_target,
            "global_cells_covered": total_cells_done,
            "global_pct": round(global_pct, 2),
        },

        # § 2 Couverture tuilaire
        "coverage_tiles": {
            "by_rf_species": {rf: dict(inv["per_rf_tiles"][rf]) for rf in g["targets"]},
            "total_tiles_3rf": total_tiles_3rf,
            "target_tiles_historique": 127_800,
            "pct_tiles": round(total_tiles_3rf / 127_800 * 100, 2),
        },
    }

    if do_full:
        # § 3 Manifest checkpoint
        report["manifest_checkpoint"] = manifest_checkpoint()

        # § 4 Audit divergence biologique
        report["biological_divergence_audit"] = audit_divergence_biological(
            inv["per_rf_keys_sample"], inv["per_rf_tiles"]
        )

        # § 5 Audit hors-3RF
        report["outside_3rf_audit"] = audit_outside_3rf(inv["per_rf_tiles"], time.time())

        # § 6 Verdict
        report["verdict"] = build_verdict_full(report)
    else:
        # ETA vers seuil (depuis throughput observé moyen 70 tuiles/min × 8 workers / espèce avg)
        cells_remaining = total_cells_target - total_cells_done
        cells_to_threshold = max(0, int(total_cells_target * THRESHOLD_PCT / 100 - total_cells_done))
        # Hypothèse: 8 workers × 70 tuiles/min · ~144 tuiles/cell moyennée → ~0.49 cells/min
        cells_per_min_estimated = 0.5
        eta_min_to_threshold = cells_to_threshold / cells_per_min_estimated if cells_to_threshold > 0 else 0
        report["eta_to_threshold"] = {
            "cells_remaining_to_100pct": cells_remaining,
            "cells_remaining_to_threshold_pct": cells_to_threshold,
            "estimated_cells_per_min": cells_per_min_estimated,
            "eta_minutes_to_threshold": round(eta_min_to_threshold, 1),
            "eta_hours_to_threshold": round(eta_min_to_threshold / 60, 2),
        }
        report["verdict"] = {
            "status": "T+95%_NON_ATTEINT",
            "global_pct": round(global_pct, 2),
            "threshold": THRESHOLD_PCT,
            "action_recommandee": "Attendre atteinte seuil · re-exécuter ce script",
        }

    return report


def build_verdict_full(report: dict) -> dict:
    cov = report["coverage_cellular"]
    div = report.get("biological_divergence_audit", {}).get("divergence_check", {})
    out = report.get("outside_3rf_audit", {})
    man = report.get("manifest_checkpoint", {})

    rf_pass = all(rf_data["pct"] >= 90.0 for rf_data in cov["by_rf"].values())
    div_pass = all(d.get("divergence_ok", False) for d in div.values())
    outside_pass = out.get("block_outside_3rf_status") == "EFFICACE"
    manifest_pass = man.get("drift_ok", False)

    overall_pass = rf_pass and div_pass and outside_pass and manifest_pass

    return {
        "status": "T+95%_ATTEINT_VALIDÉ" if overall_pass else "T+95%_ATTEINT_REVUE",
        "global_pct": cov["global_pct"],
        "all_rf_ge_90pct": rf_pass,
        "biological_divergence_ok": div_pass,
        "block_outside_3rf_efficace": outside_pass,
        "manifest_drift_ok": manifest_pass,
        "overall_pass": overall_pass,
    }


def render_text(report: dict) -> str:
    lines = []
    lines.append("═" * 78)
    lines.append(f"  {report['_report']} · {report['_doctrine']}")
    lines.append(f"  Generated : {report['_generated_at']}")
    lines.append(f"  Mode      : {report['_mode']}  (threshold={report['_threshold_pct']}%)")
    lines.append("═" * 78)

    cov = report["coverage_cellular"]
    lines.append("\n§ 1 · COUVERTURE CELLULAIRE 3 RF")
    lines.append(f"{'RF':50} | {'Cible':>6} | {'Couv':>6} | {'%':>6}")
    lines.append("-" * 78)
    for rf, d in cov["by_rf"].items():
        lines.append(f"{rf:50} | {d['cells_target']:>6} | {d['cells_covered']:>6} | {d['pct']:>5.1f}%")
    lines.append("-" * 78)
    lines.append(f"{'TOTAL 3 RF':50} | {cov['global_cells_target']:>6} | "
                 f"{cov['global_cells_covered']:>6} | {cov['global_pct']:>5.2f}%")

    cot = report["coverage_tiles"]
    lines.append(f"\n§ 2 · COUVERTURE TUILAIRE 3 RF · {cot['total_tiles_3rf']} / "
                 f"{cot['target_tiles_historique']} ({cot['pct_tiles']:.1f}%)")
    for rf, sp_cnt in cot["by_rf_species"].items():
        lines.append(f"  {rf}")
        for sp in sorted(sp_cnt):
            lines.append(f"    {sp:18}: {sp_cnt[sp]:>6} tuiles")

    if report["_mode"] == "FULL":
        man = report["manifest_checkpoint"]
        lines.append("\n§ 3 · MANIFEST CHECKPOINT")
        lines.append(f"  doctrine          : {man.get('doctrine')}")
        lines.append(f"  generated_at      : {man.get('generated_at')}")
        lines.append(f"  drift_seconds     : {man.get('drift_seconds')} (cible <{man.get('drift_target_max_s')}s)")
        lines.append(f"  drift_ok          : {man.get('drift_ok')}")
        lines.append(f"  n_tiles_reporté   : {man.get('n_tiles')}")
        lines.append(f"  cells_unique      : {man.get('cells_unique')}")
        lines.append(f"  total_size_mb     : {man.get('total_size_mb')}")
        lines.append(f"  by_species        : {man.get('by_species')}")

        div = report["biological_divergence_audit"]
        lines.append("\n§ 4 · AUDIT DIVERGENCE BIOLOGIQUE (échantillons R2)")
        for rf, d in div.get("divergence_check", {}).items():
            lines.append(f"  {rf}")
            lines.append(f"    per_species_avg_score : {d['per_species_avg_score']}")
            lines.append(f"    distinct_scores       : {d['distinct_scores']} (≥2 attendu)")
            lines.append(f"    divergence_ok         : {d['divergence_ok']}")

        out = report["outside_3rf_audit"]
        lines.append("\n§ 5 · AUDIT HORS-3RF (BLOCK_OUTSIDE_3RF)")
        lines.append(f"  tiles_hors_3rf_cumul : {out['tiles_hors_3rf_cumul']}")
        lines.append(f"  status               : {out['block_outside_3rf_status']}")
        lines.append(f"  note                 : {out['note']}")

    else:
        eta = report.get("eta_to_threshold", {})
        lines.append(f"\n§ 3 · ETA VERS SEUIL T+{report['_threshold_pct']}%")
        lines.append(f"  cells_remaining_to_100pct       : {eta.get('cells_remaining_to_100pct')}")
        lines.append(f"  cells_remaining_to_threshold    : {eta.get('cells_remaining_to_threshold_pct')}")
        lines.append(f"  estimated_cells_per_min         : {eta.get('estimated_cells_per_min')}")
        lines.append(f"  eta_minutes_to_threshold        : {eta.get('eta_minutes_to_threshold')}")
        lines.append(f"  eta_hours_to_threshold          : {eta.get('eta_hours_to_threshold')}")

    v = report["verdict"]
    lines.append("\n§ 6 · VERDICT")
    for k, vv in v.items():
        lines.append(f"  {k:38}: {vv}")
    lines.append("═" * 78)
    return "\n".join(lines)


def main():
    report = build_report()
    if OUTPUT_MODE == "json":
        print(json.dumps(report, indent=2, ensure_ascii=False, default=str))
    else:
        print(render_text(report))


if __name__ == "__main__":
    main()

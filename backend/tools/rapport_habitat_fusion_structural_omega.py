"""
rapport_habitat_fusion_structural_omega.py — HABITAT_FUSION_STRUCTURAL_REPORT_Ω
═══════════════════════════════════════════════════════════════════════════════
P22ΩΩ_AUTOPILOT_4D_SAFE_Ω · COMMANDANT STEEVE-MAX · 2026-02-20 · BCE-4X ULTIME ABSOLU
Verrou Phase III · LECTURE SEULE · Mode FULL (toutes 24h).

DOCTRINE
--------
Rapport de santé HABITAT FUSION P0 + P1 STRUCTURAL+ :
  - Statut moteurs (axes ready/pending)
  - Statut 4 clients ingestion (NASA HLS · ESA S2 · NRCan · MFFP)
  - Statut registries (PRE_INGESTION / P1_READY_AWAITING_CREDENTIALS)
  - Échantillonnage compute (5 espèces × 4 saisons en 1 point BSL)
  - Verdict global

USAGE
-----
    OUTPUT=text|json python3 /app/backend/tools/rapport_habitat_fusion_structural_omega.py
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

BACKEND_ROOT = Path("/app/backend")
sys.path.insert(0, str(BACKEND_ROOT))

OUTPUT_MODE = os.environ.get("OUTPUT", "text")

from engines.v8_institutional import habitat_fusion_engine_p0 as HFE_P0
from engines.v8_institutional import habitat_fusion_engine_p1 as HFE_P1
from engines.v8_institutional import habitat_fusion_registry_omega as REG

BSL = (48.206657, -68.382422)
SPECIES = ["chevreuil", "orignal", "ours_noir", "coyote", "dindon_sauvage"]
SEASONS = ["printemps", "ete", "automne", "hiver"]


def build() -> dict:
    p1_status = HFE_P1.get_p1_status()
    axes_status_p0 = HFE_P0.get_axes_status()
    master_reg = REG.get_master_registry()

    # Échantillonnage compute (preuve divergence biologique)
    samples = {}
    distinct_by_season = {}
    for sn in SEASONS:
        vals = []
        for sp in SPECIES:
            r = HFE_P1.compute_habitat_score(species=sp, lat=BSL[0], lng=BSL[1], season=sn)
            samples[f"{sp}_{sn}"] = r.get("habitat_score")
            vals.append(r.get("habitat_score"))
        distinct_by_season[sn] = len(set(round(v, 1) for v in vals if v is not None))

    biological_divergence_ok = all(d >= 4 for d in distinct_by_season.values())

    return {
        "_doctrine": "P22ΩΩ_AUTOPILOT_4D_SAFE_Ω",
        "_report": "HABITAT_FUSION_STRUCTURAL_REPORT_Ω",
        "_generated_at": datetime.now(timezone.utc).isoformat(),
        "engine_p0": {
            "name": axes_status_p0.get("engine"),
            "version": axes_status_p0.get("version"),
            "phase": axes_status_p0.get("phase"),
            "status_global": axes_status_p0.get("status_global"),
            "axes_total": axes_status_p0.get("axes_total"),
            "axes_ready": axes_status_p0.get("axes_ready"),
            "axes_pre_ingestion": axes_status_p0.get("axes_pre_ingestion"),
            "weight_active_p0": axes_status_p0.get("weight_active_p0"),
            "completion_ratio": axes_status_p0.get("completion_ratio"),
        },
        "engine_p1": {
            "name": p1_status.get("engine"),
            "version": p1_status.get("version"),
            "phase": p1_status.get("phase"),
            "weight_active": p1_status.get("weight_active"),
            "ingestion_p1_ready": p1_status.get("ingestion_p1_ready"),
            "clients_credential_ready": p1_status.get("clients_credential_ready"),
            "clients_armed": p1_status.get("clients_armed"),
        },
        "ingestion_clients": p1_status.get("ingestion_clients", {}),
        "registries_status": {
            "habitat_fusion_p0_master": REG.get_status(),
            "completion_ratio": REG.get_completion_ratio(),
        },
        "compute_validation_bsl": {
            "samples": samples,
            "distinct_by_season": distinct_by_season,
            "biological_divergence_ok": biological_divergence_ok,
        },
        "verrou_phase_iii": True,
        "lecture_seule": True,
        "weight_target_p2_full": 1.00,
        "_note_doctrinale": (
            "weight_active=0.35 INCHANGÉ · 2/4 axes effectifs · "
            "Clients NDVI/LiDAR CODE-READY mais INERTES (anti-générique strict)."
        ),
    }


def render_text(payload: dict) -> str:
    lines = []
    lines.append("═" * 78)
    lines.append(f"  HABITAT_FUSION_STRUCTURAL_REPORT_Ω · {payload['_generated_at']}")
    lines.append("═" * 78)
    p0 = payload["engine_p0"]
    lines.append(f"\n§ A · ENGINE P0")
    lines.append(f"  {p0['name']} · v{p0['version']}")
    lines.append(f"  Phase           : {p0['phase']}")
    lines.append(f"  Status global   : {p0['status_global']}")
    lines.append(f"  Axes ready/total: {p0['axes_ready']}/{p0['axes_total']} · pre_ingestion={p0['axes_pre_ingestion']}")
    lines.append(f"  weight_active_p0: {p0['weight_active_p0']}")
    lines.append(f"  completion_ratio: {p0['completion_ratio']}")

    p1 = payload["engine_p1"]
    lines.append(f"\n§ B · ENGINE P1 STRUCTURAL+")
    lines.append(f"  {p1['name']} · v{p1['version']}")
    lines.append(f"  Phase                   : {p1['phase']}")
    lines.append(f"  weight_active           : {p1['weight_active']} (INCHANGÉ vs P0)")
    lines.append(f"  ingestion_p1_ready      : {p1['ingestion_p1_ready']}")
    lines.append(f"  clients credential ready: {p1['clients_credential_ready']}/4")
    lines.append(f"  clients armés           : {p1['clients_armed']}/4")

    lines.append(f"\n§ C · CLIENTS INGESTION (CODE-READY · INERTES)")
    for k, c in payload["ingestion_clients"].items():
        mode = c.get("operational_mode")
        cr = c.get("credential_ready")
        lines.append(f"  {k:25}: mode={mode} · cred_ready={cr}")

    cv = payload["compute_validation_bsl"]
    lines.append(f"\n§ D · COMPUTE VALIDATION @ BSL (48.21, -68.38)")
    lines.append(f"  Divergence biologique stricte: {cv['biological_divergence_ok']}")
    lines.append(f"  Distinct par saison: {cv['distinct_by_season']}")
    lines.append(f"  Sample scores      :")
    for k, v in list(cv["samples"].items())[:8]:
        lines.append(f"    {k:30}: {v}")
    lines.append(f"    ... ({len(cv['samples'])} total)")

    lines.append(f"\n§ E · VERROU PHASE III")
    lines.append(f"  verrou_phase_iii  : {payload['verrou_phase_iii']}")
    lines.append(f"  lecture_seule     : {payload['lecture_seule']}")
    lines.append(f"  weight_target_p2  : {payload['weight_target_p2_full']}")
    lines.append(f"  _note             : {payload['_note_doctrinale']}")
    lines.append("═" * 78)
    return "\n".join(lines)


def main():
    payload = build()
    if OUTPUT_MODE == "json":
        print(json.dumps(payload, indent=2, ensure_ascii=False, default=str))
    else:
        print(render_text(payload))


if __name__ == "__main__":
    main()

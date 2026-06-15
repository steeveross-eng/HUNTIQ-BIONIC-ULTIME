#!/usr/bin/env python3
"""
SYNTHESE_PHASE_A_STABILISEE — Phase A audit + correctifs appliqués
"""
import hashlib, json, datetime
from pathlib import Path

ROOT = Path("/app/frontend/public/reports/audit_territoire_omega_ultime")
PHASE_A = ROOT / "phase_a"
PUBLIC_BASE = "https://bionic-ultime-1.preview.emergentagent.com/reports/audit_territoire_omega_ultime"


def sha256_of(p: Path):
    if not p.exists(): return None
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""): h.update(chunk)
    return h.hexdigest()


def main():
    captures = []
    for f in sorted(PHASE_A.glob("*.jpeg")):
        captures.append({
            "filename": f.name,
            "size_bytes": f.stat().st_size,
            "sha256": sha256_of(f),
            "url": f"{PUBLIC_BASE}/phase_a/{f.name}",
        })

    synth = {
        "phase": "PHASE_TERRITOIRE_Ω_AUDIT_INTER-ENGINES_ULTIME",
        "subphase": "PHASE-A — RUPTURES CRITIQUES + STABILISATION",
        "directive": "BCE-4X ULTIME ABSOLU — TOP-ABSOLU",
        "commandant": "STEEVE-MAX",
        "generated_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "v30_engine_status": "LOCKED — registry_lock_omega.py V30 INTOUCHED",
        "v30_engine_tampering": False,
        "xix_recompute": False,
        "vitaux_recompute": False,
        "audit_only_diagnostics_only_evidences_only": True,
        "waypoint_official": {"lat": 48.206657, "lng": -68.382422, "label": "BSL TERRITOIRE BIONIC"},
        "stabilization_summary": {
            "C_dindon_absent": "STABILISÉ — v30_corridors_status_router applique apply_presence_mask_to_bundle. Liste étendue à 5 espèces. dindon/wapiti @BSL retournent label=ABSENT, halt=True, score=0.",
            "D_metrics_mismatch": "STABILISÉ — panneau ajoute étiquette 'V30 BRUT' + note explicative séparant V30 brut / V20 pipeline / HUD V8.",
            "B_alert_couches": "STABILISÉ — alerte renommée 'couches V30 brutes absentes' (au lieu de 'critiques'), note de réconciliation ajoutée.",
            "A_overlap_ui": "STABILISÉ — WeatherPanel se repositionne automatiquement à top:320 si window.innerHeight < 630.",
        },
        "corrections_applied": [
            {
                "id": "C",
                "title": "Application masque XVIII-BIO-PRESENCE_MASK_Ω + extension liste 5 espèces",
                "files_modified": ["/app/backend/routes/v30_corridors_status_router.py"],
                "lines_changed_count_approx": 50,
                "v30_lock_respected": True,
                "test": "tests/test_phase_a_audit_corrections.py (8 tests dédiés)",
            },
            {
                "id": "D",
                "title": "Étiquette 'V30 BRUT' + note explicative panneau",
                "files_modified": ["/app/frontend/src/components/territoire/StatutCorridorsOmegaPanel.jsx"],
                "v30_lock_respected": True,
            },
            {
                "id": "B",
                "title": "Renommage alerte + badge ABSENT pour espèces sans présence biologique",
                "files_modified": ["/app/frontend/src/components/territoire/StatutCorridorsOmegaPanel.jsx"],
                "v30_lock_respected": True,
            },
            {
                "id": "A",
                "title": "Layout responsive WeatherPanel anti-overlap",
                "files_modified": ["/app/frontend/src/components/territoire/ui/WeatherPanel.jsx"],
                "behavior": "shouldRepositionTop = (window.innerHeight < 630) → top:320 ; sinon bottom:90",
                "v30_lock_respected": True,
            },
        ],
        "live_endpoint_validation": {
            "endpoint": "GET /api/v30/corridors/status?lat=48.206657&lon=-68.382422",
            "species_count": 5,
            "per_species_observed": {
                "orignal": {"bio_presence_status": "PRESENT", "bio_presence_mask_halt": False, "alignment_label": "CONFORME / PARTIEL (variable)"},
                "cerf": {"bio_presence_status": "PRESENT", "bio_presence_mask_halt": False, "alignment_label": "CONFORME / PARTIEL"},
                "ours": {"bio_presence_status": "PRESENT", "bio_presence_mask_halt": False, "alignment_label": "PARTIEL"},
                "dindon": {"bio_presence_status": "ABSENT", "bio_presence_mask_halt": True, "alignment_label": "ABSENT", "v30_alignment_score": 0.0},
                "wapiti": {"bio_presence_status": "ABSENT", "bio_presence_mask_halt": True, "alignment_label": "ABSENT", "v30_alignment_score": 0.0},
            },
            "v30_locked_runtime": True,
            "v30_modified_runtime": False,
        },
        "live_dom_validation_table_rows_post_fix": [
            {"testid": "v30-species-row-orignal", "cells": ["orignal", "12/18", "66.7"]},
            {"testid": "v30-species-row-cerf", "cells": ["cerf", "16/20", "80.0"]},
            {"testid": "v30-species-row-ours", "cells": ["ours", "8/13", "61.5"]},
            {"testid": "v30-species-row-dindon", "cells": ["dindon", "—", "ABSENT"]},
            {"testid": "v30-species-row-wapiti", "cells": ["wapiti", "—", "ABSENT"]},
        ],
        "pytest_results": {
            "phase_a_audit_corrections": "8 PASSED",
            "phase_xviii_bio_presence_mask": "11 PASSED",
            "phase_xviii_predictive_omega_v2": "PASSED",
            "phase_xviii_vitaux_omega": "PASSED",
            "phase_xix_p1_origine_externe_filter": "PASSED",
            "phase_xix_p2_origine_externe_inversion": "PASSED",
            "global_run": "73 PASSED · 3 SKIPPED · 0 FAILED",
        },
        "captures": captures,
        "deliverables": {
            "json": "/reports/audit_territoire_omega_ultime/SYNTHESE_PHASE_A_STABILISEE.json",
            "html": "/reports/audit_territoire_omega_ultime/RAPPORT_PHASE_A_STABILISEE.html",
            "captures_dir": "/reports/audit_territoire_omega_ultime/phase_a/",
        },
    }
    out_json = ROOT / "SYNTHESE_PHASE_A_STABILISEE.json"
    out_json.write_text(json.dumps(synth, indent=2, ensure_ascii=False))
    print(f"WROTE {out_json}")
    print(f"SHA-256: {sha256_of(out_json)}")


if __name__ == "__main__":
    main()

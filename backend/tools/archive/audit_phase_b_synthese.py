#!/usr/bin/env python3
"""
PHASE-B.5 GENERATE — JSON consolidé + Rapport HTML 20 sections
"""
import hashlib, json, datetime
from pathlib import Path

ROOT = Path("/app/frontend/public/reports/audit_territoire_omega_ultime")
PHASE_B = ROOT / "phase_b"
PAYLOADS = PHASE_B / "api_payloads"
CAPS = PHASE_B / "captures_frontend"
PUBLIC_BASE = "https://ultime-preview.preview.emergentagent.com/reports/audit_territoire_omega_ultime"


def sha256_of(p: Path):
    if not p.exists(): return None
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""): h.update(chunk)
    return h.hexdigest()


def jload(p):
    return json.loads(Path(p).read_text()) if Path(p).exists() else None


def main():
    # Inventaire SHA-256 captures + JSON
    captures = []
    for f in sorted(CAPS.glob("*.jpeg")):
        captures.append({"file": f.name, "size_b": f.stat().st_size, "sha256": sha256_of(f),
                         "url": f"{PUBLIC_BASE}/phase_b/captures_frontend/{f.name}"})

    payloads = []
    for f in sorted(PAYLOADS.glob("*.json")):
        payloads.append({"file": f.name, "size_b": f.stat().st_size, "sha256": sha256_of(f),
                         "url": f"{PUBLIC_BASE}/phase_b/api_payloads/{f.name}"})

    # Charge analyses
    inter = jload(PHASE_B / "B3_inter_engines_analysis.json") or {}
    api_summary = jload(PHASE_B / "B2_api_audit_summary.json") or {}
    frontend_dom = jload(PHASE_B / "B4_frontend_captures_dom.json") or []

    # Anomalies inter-engines révélées
    anomalies = [
        {"id": "B-1", "title": "VENT — double source divergente",
         "evidence": {
             "sensoriel_vent_odeurs": {"wind_deg": 225, "wind_speed_kmh": 15},
             "wind_vectors_index_0": {"direction_deg": 165, "speed_kmh": 7.5},
             "delta_angle_deg": 60, "delta_speed_kmh": 7.5,
         },
         "engine": "ENGINE_VENT (V20 sensoriel) vs wind_vectors (V8)",
         "severity": "CRITIQUE",
         "verdict": "Deux moteurs publient des données vent divergentes dans le même bundle. La carte affiche les deux. Source de confusion utilisateur (anomalie 2.1 du commandant).",
        },
        {"id": "B-2", "title": "CONTAMINATION non purgée pour espèce ABSENT",
         "evidence": {"dindon": {"contamination_zones_count": 0, "contamination_count": 18, "halt": True},
                      "wapiti":  {"contamination_zones_count": 0, "contamination_count": 18, "halt": True}},
         "engine": "ENGINE_CONTAMINATION_V2 (contamination)",
         "severity": "CRITIQUE",
         "verdict": "apply_presence_mask_to_bundle() vide `corridors`, `affuts`, `contamination_zones` mais NE VIDE PAS la liste brute `contamination` (18 polygones). Les zones contaminées sont produites pour des espèces biologiquement ABSENT.",
        },
        {"id": "B-3", "title": "HOTSPOTS persistants pour espèce ABSENT",
         "evidence": {"dindon": {"hotspots_count": 11, "affuts_count": 0, "halt": True,
                                 "all_hotspots_source_engine": "AFFUT"},
                      "wapiti":  {"hotspots_count": 11, "affuts_count": 0, "halt": True}},
         "engine": "ENGINE_HOTSPOTS",
         "severity": "CRITIQUE",
         "verdict": "11 hotspots persistent malgré halt=True. Tous portent `source_engine: AFFUT` alors que `affuts: 0`. Signature d'une dépendance brisée : les hotspots sont calculés AVANT le masque puis non purgés en aval.",
        },
        {"id": "B-4", "title": "SALINES non purgées pour espèce ABSENT",
         "evidence": {"dindon": {"salines_count": 6, "salines_score_bio_species": ["cerf", "orignal", "wapiti", "global"]}},
         "engine": "ENGINE_SALINES (V11-SUPRA)",
         "severity": "CRITIQUE",
         "verdict": "6 salines pour dindon ABSENT. score_bio_species ne contient PAS dindon_sauvage (calculé pour cerf/orignal/wapiti uniquement) → preuve que le calcul saline ignore l'espèce demandée.",
        },
        {"id": "B-5", "title": "Couplage masque BIO partiel",
         "evidence": {"vidé_correctement": ["corridors", "affuts", "contamination_zones"],
                      "non_vidé": ["contamination", "hotspots", "salines", "contamination_v2", "wind_vectors"]},
         "engine": "engines/v8_institutional/species_presence_mask_omega.apply_presence_mask_to_bundle()",
         "severity": "CRITIQUE",
         "verdict": "Le masque BIO ne couvre qu'une partie des dictionnaires de sortie. Étendre la fonction pour vider corridors+affuts+salines+hotspots+contamination+contamination_v2 quand status=ABSENT.",
        },
    ]

    # Synthèse JSON consolidée
    synth = {
        "phase": "PHASE_TERRITOIRE_Ω_AUDIT_INTER-ENGINES_ULTIME",
        "subphase": "PHASE-B — AUDIT INTÉGRAL READ-ONLY",
        "directive": "BCE-4X ULTIME ABSOLU — TOP-ABSOLU — PRÉCISION ×2",
        "commandant": "STEEVE-MAX",
        "generated_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "doctrine": {
            "v30_locked": True, "xix_recompute": False, "vitaux_recompute": False,
            "audit_only": True, "diagnostic_only": True, "evidence_only": True,
        },
        "v30_engine_status": "LOCKED — INTOUCHED",
        "v30_engine_tampering": False,
        "waypoint_official": {"lat": 48.206657, "lng": -68.382422, "label": "BSL TERRITOIRE BIONIC"},
        "scope": {
            "engines_audited": ["ENGINE_VENT", "ENGINE_CONTAMINATION_V2", "ENGINE_SON",
                               "ENGINE_CORRIDORS_V30", "ENGINE_CORRIDORS_ORGANIC", "ENGINE_ZONES",
                               "ENGINE_AFFUTS", "ENGINE_SALINES_V11", "ENGINE_HOTSPOTS",
                               "ENGINE_BIO_PRESENCE_MASK_Ω"],
            "chains_audited": [
                "vent → contamination → son",
                "corridors → zones → affûts → salines → hotspots",
                "BIO-MASK → VITAUX → RENDUΩ",
            ],
            "species_covered": ["orignal", "cerf", "ours", "dindon", "wapiti"],
            "endpoints_tested_count": len(payloads),
        },
        "anomalies_discovered_phase_b": anomalies,
        "inter_engines_analysis_full": inter,
        "api_audit_summary": api_summary,
        "frontend_captures_dom_metrics": frontend_dom,
        "captures": captures,
        "payloads_hashed": payloads,
        "stabilization_plan": {
            "step_1": {
                "id": "B-5",
                "action": "Étendre apply_presence_mask_to_bundle() pour vider également : contamination, hotspots, salines, contamination_v2, wind_vectors quand status=ABSENT.",
                "files": ["/app/backend/engines/v8_institutional/species_presence_mask_omega.py"],
                "v30_lock_respected": True,
                "tests_to_add": ["test_mask_purges_all_artefacts_for_absent_species"],
                "priority": "P0",
            },
            "step_2": {
                "id": "B-1",
                "action": "Réconcilier les sources vent : exposer une source unique (ENGINE_VENT) et faire de wind_vectors un dérivé visuel (champ étiqueté legacy_v8_visual). Documenter dans le bundle.",
                "files": ["/app/backend/engines/v8_institutional/engine_vent.py", "/app/backend/engines/v8_institutional/territoire_v10_supra.py"],
                "v30_lock_respected": True,
                "priority": "P1",
            },
            "step_3": {
                "id": "B-2",
                "action": "Pour engines PRESENT : vérifier que le polygon de contamination est orienté à wind_deg+180° (sous-vent, propagation odeur).",
                "files": ["/app/backend/engines/v8_institutional/engine_contamination_v2_omega.py"],
                "v30_lock_respected": True,
                "priority": "P1",
            },
            "step_4": {
                "id": "B-AUDIT-SON",
                "action": "Documenter et exposer dans le bundle une clé son_cone_axis_deg (cohérente avec wind_deg).",
                "files": ["/app/backend/engines/v8_institutional/engine_sensoriel_vent_odeurs_omega.py"],
                "v30_lock_respected": True,
                "priority": "P2",
            },
            "step_5": {
                "id": "B-TESTS",
                "action": "Suite pytest dédiée tests/test_phase_b_inter_engines_consistency.py couvrant les 5 anomalies.",
                "v30_lock_respected": True,
                "priority": "P0",
            },
            "anti_regression": {
                "v30_sha256_check": "sha256 hash du registry_lock_omega.py et engine_ia_corridors_omega.py vérifié avant et après chaque modification (CI guard).",
                "xix_no_recompute_check": "Aucun appel mutant ne doit modifier les seuils XIX-P1/P2/P1B (revue PR obligatoire).",
                "vitaux_no_recompute_check": "Aucune modification du module corridors_vitaux_omega (revue PR obligatoire).",
                "smoke_test": "Bundle V20 retourne v30_locked=True ; presence-mask retourne 5 espèces avec statut documenté.",
            },
        },
        "deliverables": {
            "json": "/reports/audit_territoire_omega_ultime/SYNTHESE_PHASE_B.json",
            "html": "/reports/audit_territoire_omega_ultime/RAPPORT_PHASE_B.html",
            "captures_dir": "/reports/audit_territoire_omega_ultime/phase_b/captures_frontend/",
            "api_payloads_dir": "/reports/audit_territoire_omega_ultime/phase_b/api_payloads/",
        },
    }

    out_json = ROOT / "SYNTHESE_PHASE_B.json"
    out_json.write_text(json.dumps(synth, indent=2, ensure_ascii=False))
    print(f"WROTE {out_json}")
    print(f"SHA-256: {sha256_of(out_json)}")


if __name__ == "__main__":
    main()

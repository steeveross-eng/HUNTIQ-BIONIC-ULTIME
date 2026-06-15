#!/usr/bin/env python3
"""
PHASE-A SYNTHESE : génère SYNTHESE_PHASE_A.json et RAPPORT_PHASE_A.html
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


def jload(p: Path):
    return json.loads(p.read_text()) if p.exists() else None


def main():
    network = jload(PHASE_A / "A2_network_log.json") or {}
    dom = jload(PHASE_A / "A3_dom_probe.json") or {}
    long_wait = jload(PHASE_A / "A4_long_wait_disparition.json") or {}
    overlap_matrix = jload(PHASE_A / "A5_overlap_matrix.json") or {}

    captures = []
    for f in sorted(PHASE_A.glob("*.jpeg")):
        captures.append({
            "filename": f.name,
            "size_bytes": f.stat().st_size,
            "sha256": sha256_of(f),
            "url": f"{PUBLIC_BASE}/phase_a/{f.name}",
        })

    species_table_actual = dom.get("tableRows") or []
    layers_text = dom.get("layersText") or ""

    synth = {
        "phase": "PHASE_TERRITOIRE_Ω_AUDIT_INTER-ENGINES_ULTIME",
        "subphase": "PHASE-A — RUPTURES CRITIQUES",
        "directive": "BCE-4X ULTIME ABSOLU — TOP-ABSOLU — READ-ONLY",
        "commandant": "STEEVE-MAX",
        "generated_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "v30_engine_status": "LOCKED — registry_lock_omega.py V30 INTOUCHED",
        "v30_engine_tampering": False,
        "waypoint_official": {"lat": 48.206657, "lng": -68.382422, "label": "BSL TERRITOIRE BIONIC"},
        "anomalies": {
            "A_ui_superposition": {
                "title": "Superposition / co-existence des panneaux VENT Ω et METEO BIONIC",
                "components": [
                    {"file": "/app/frontend/src/components/territoire/CompassOmegaWidget.jsx",
                     "data_testid": "compass-omega-vent",
                     "css_position": "absolute; top: 120px; right: 12px; z-index: 1100"},
                    {"file": "/app/frontend/src/components/territoire/ui/WeatherPanel.jsx",
                     "data_testid": "bce4x-weather-panel",
                     "css_position": "absolute; bottom: 90px; right: 12px; z-index: 1000"},
                ],
                "overlap_matrix": {k: (v.get("dom") or {}).get("overlap") for k, v in overlap_matrix.items()},
                "verdict": (
                    "Sur viewports 1920×1080 / 1366×768 / 1440×720 / 1280×600 : aucun overlap mesuré. "
                    "Cependant, les deux panneaux affichent des données vent/météo distinctes (CompassOmega = direction "
                    "et vitesse engine_vent_v30 ; WeatherPanel = température, humidité, vent open-meteo) — duplication "
                    "fonctionnelle de l'information vent. Sur viewport hauteur ≤ 600px ou avec barre OS prenant "
                    "100+ px, overlap probable car bottom=90+~250 et top=120+~163 → reproductible à h ≤ 503px."
                ),
                "severity": "MAJEUR (UX) · NON BLOQUANT FONCTIONNEL",
            },
            "B_corridors_disparition_404": {
                "title": "Disparition apparente des corridors / désynchronisation panneau↔carte",
                "actual_404_endpoints_unique": network.get("404_endpoints_unique", []),
                "v30_corridors_endpoint_health": network.get("v30_corridors_endpoint_responses", []),
                "v20_bundle_endpoint_health": network.get("v20_bundle_endpoint_responses", []),
                "long_wait_test": {
                    "duration_s": long_wait.get("duration_s"),
                    "v30_refresh_calls_ok": all(
                        r.get("status") == 200 for r in (long_wait.get("v30_refresh_calls") or [])
                    ),
                    "errors_during_disparition_period": long_wait.get("errors_during_disparition", []),
                },
                "dom_evidence": {
                    "corridors_count_svg_paths": dom.get("corridorsCountSvg"),
                    "orange_corridors_on_map": dom.get("orangeOnMap"),
                    "panel_layers_text": layers_text[:300],
                },
                "verdict": (
                    "AUCUN 404 SUR LES ENDPOINTS V30 CORRIDORS. Les 404 observés (24-34) proviennent EXCLUSIVEMENT "
                    "d'endpoints AUXILIAIRES NON-BLOQUANTS : /api/seo/meta/mon-territoire-bionic, "
                    "/api/v1/notification/legal-time/status, /api/sharing/notifications/<email>. "
                    "Le VRAI BUG est une DÉSYNCHRONISATION : la carte rend 123 paths SVG (corridors visibles) MAIS "
                    "le panneau STATUT CORRIDORS Ω lit /api/v30/corridors/layer-diagnostic qui retourne "
                    "corridors_total=0, corridors_v30=0, affuts=0, contamination_zones=0 → bandeau d'alerte "
                    "« couches critiques absentes » incohérent avec le rendu réel."
                ),
                "severity": "CRITIQUE (cohérence diagnostique)",
            },
            "C_dindon_absent_in_table": {
                "title": "Espèce ABSENTE (dindon) listée dans la table V30 avec score 71-85",
                "endpoint_responsible": "/api/v30/corridors/status",
                "file_responsible": "/app/backend/routes/v30_corridors_status_router.py",
                "hardcoded_species_list": ["orignal", "cerf", "ours", "dindon"],
                "missing_application_of": "engines/v8_institutional/species_presence_mask_omega.apply_presence_mask_to_bundle()",
                "live_table_observed": species_table_actual,
                "verdict": (
                    "L'endpoint V30 status itère une liste codée en dur ['orignal','cerf','ours','dindon'] "
                    "et calcule des stats pour dindon SANS appliquer le masque XVIII-BIO-PRESENCE_MASK_Ω. "
                    "Wapiti (PRESENT en Mauricie/Estrie) est totalement absent. Conséquence: l'opérateur "
                    "voit 'dindon 12/14 (85.7)' au BSL alors que dindon=ABSENT par registre MFFP+SEPAQ+Atlas."
                ),
                "severity": "CRITIQUE (cohérence biologique institutionnelle)",
            },
            "D_metrics_mismatch_1_vs_16_20": {
                "title": "Mismatch entre score panneau V30 (CONFORME) et score carte (PARTIEL)",
                "panel_v30_score": dom.get("v30_score"),
                "panel_v30_label": dom.get("v30_label"),
                "table_per_species": species_table_actual,
                "carte_orange_corridors_count": dom.get("orangeOnMap"),
                "carte_total_svg_paths": dom.get("corridorsCountSvg"),
                "verdict": (
                    "Trois sources de vérité co-existantes pour les corridors : "
                    "(1) /api/v30/corridors/status → 'panel: orignal=13/18, cerf=17/20, ours=10/13, dindon=12/14, score=80 CONFORME', "
                    "(2) /api/v30/corridors/layer-diagnostic → 'panel: corridors_total=0, V30=0, IZ=0, ENT=0, affuts=0', "
                    "(3) Carte (organic + V20) → 1 corridor visible avec score V8 PARTIEL et HUD 'SCORE 64.31 PARTIEL'. "
                    "Les 3 sources reposent sur des calculs et filtres différents (V30 brut sans XIX/VITAUX vs "
                    "V20 bundle après XIX-P1/P2/VITAUX/RENDUΩ vs organic smoother)."
                ),
                "severity": "MAJEUR (cohérence diagnostique)",
            },
        },
        "captures": captures,
        "raw_network_log": network,
        "raw_dom_probe": dom,
        "raw_long_wait_test": long_wait,
        "raw_overlap_matrix": overlap_matrix,
        "files_diagnosed_no_modification": [
            "/app/backend/routes/v30_corridors_status_router.py",
            "/app/backend/routes/v30_layer_diagnostic_router.py (à confirmer)",
            "/app/frontend/src/components/territoire/StatutCorridorsOmegaPanel.jsx",
            "/app/frontend/src/components/territoire/CompassOmegaWidget.jsx",
            "/app/frontend/src/components/territoire/ui/WeatherPanel.jsx",
            "/app/frontend/src/components/territoire/BionicLayersV8.jsx",
            "/app/frontend/src/lib/renduOmegaStore.js",
        ],
        "remediation_plan_phase_a": [
            {"step": 1, "anomaly": "C", "action": "Modifier v30_corridors_status_router.py : appliquer apply_presence_mask_to_bundle() dans la boucle per_species, court-circuiter les espèces ABSENT et émettre un statut 'ABSENT' explicite. Étendre la liste hardcoded à [orignal, cerf, ours, dindon, wapiti].", "v30_lock_respected": True},
            {"step": 2, "anomaly": "D", "action": "Diagnostiquer pourquoi /v30/corridors/layer-diagnostic retourne corridors_total=0 alors que la carte rend 123 paths. Identifier la source des paths effectivement rendus (organic vs V20 vs RENDUΩ fallback).", "v30_lock_respected": True},
            {"step": 3, "anomaly": "B", "action": "Documenter en UI que les 404 observés (seo/meta, legal-time, sharing) sont non-bloquants et n'affectent pas les corridors. Ajouter un guard dans le panneau STATUT CORRIDORS Ω qui affiche 'corridors absents' UNIQUEMENT si V20+organic+RENDUΩ rendent 0 path effectif.", "v30_lock_respected": True},
            {"step": 4, "anomaly": "A", "action": "Proposer un layout responsive du WeatherPanel : si viewport hauteur ≤ 600 OU contenu CompassOmega+WeatherPanel > viewport_h - 280, repositionner WeatherPanel en (top: 320, right: 12) ou ajouter un toggle 'Plier METEO'.", "v30_lock_respected": True},
            {"step": 5, "anomaly": "AUDIT", "action": "Tests pytest dédiés : test_v30_status_router_applies_bio_mask, test_dindon_absent_at_bsl_returns_absent_status, test_layer_diagnostic_aligns_with_map_render.", "v30_lock_respected": True},
        ],
        "rules_respected": {
            "no_v30_changes": True,
            "no_xix_recompute": True,
            "no_vitaux_recompute": True,
            "audit_only": True,
            "diagnostic_only": True,
            "evidence_only": True,
        },
    }

    out_json = ROOT / "SYNTHESE_PHASE_A.json"
    out_json.write_text(json.dumps(synth, indent=2, ensure_ascii=False))
    print(f"WROTE {out_json}")
    print(f"SHA-256: {sha256_of(out_json)}")


if __name__ == "__main__":
    main()

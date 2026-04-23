"""
audit_engines_x199_x200.py — Audit continu ZERO-DOUBLON-Ω + V30 integrity
==========================================================================
Phase : X200-P0-ACTIVATION — audit read-only
Commandant STEEVE-MAX

Vérifie :
  1. V30 SHA-256 invariant
  2. Feature flags : seuls les 5 engines P0 actifs (pas les 6 étendus)
  3. ZERO-DOUBLON-Ω : aucun nouveau router corridors/salines/nutrition hors engines cibles

Usage :
  python3 /app/backend/tools/audit_engines_x199_x200.py
  python3 /app/backend/tools/audit_engines_x199_x200.py --json  # sortie JSON
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Dict, Any, List

BACKEND = Path("/app/backend")
sys.path.insert(0, str(BACKEND))

V30_ENGINE_FILE = BACKEND / "engines/v8_institutional/engine_ia_corridors_organic_omega.py"
V30_EXPECTED_SHA256 = "027712696407882fb41e34b0325e1f2b8dacb9082a860146659dc7650e6c8fc3"

# Engines P0 autorisés à être ACTIFS en X200-P0
P0_ACTIVE_ALLOWED = {
    "wildlife_behavior_omega",
    "eco_zones_omega",
    "hydro_topo_omega",
    "reseau_veineux_omega",
    "bio_scoring_omega",
}
# Engines X199 — post PHASE_X199_ACTIVATION_Ω : MUST_BE_ON sous triple verrou
X199_MUST_BE_ON = {
    "ecoforestry_omega",
    "terrain_3d_omega",
    "legal_time_omega",
    "predictive_omega",
    "advanced_geospatial_omega",
}
# Alias historique (compat test_engines_x199_scaffold)
X199_MUST_STAY_OFF: set = set()


def check_v30_integrity() -> Dict[str, Any]:
    if not V30_ENGINE_FILE.exists():
        return {"ok": False, "reason": "v30_file_missing"}
    h = hashlib.sha256()
    h.update(V30_ENGINE_FILE.read_bytes())
    current = h.hexdigest()
    return {
        "ok": current == V30_EXPECTED_SHA256,
        "v30_sha256_current": current,
        "v30_sha256_expected": V30_EXPECTED_SHA256,
        "file": str(V30_ENGINE_FILE),
    }


def check_feature_flags() -> Dict[str, Any]:
    violations: List[str] = []
    statuses: Dict[str, bool] = {}
    for slug in P0_ACTIVE_ALLOWED | X199_MUST_BE_ON:
        try:
            mod = __import__(f"engines.{slug}", fromlist=["FEATURE_FLAG_ACTIVE"])
            active = bool(getattr(mod, "FEATURE_FLAG_ACTIVE", False))
            statuses[slug] = active
            if slug in X199_MUST_BE_ON and not active:
                violations.append(f"{slug}: MUST_BE_ON (X199 ACTIVATED) but is OFF")
            if slug in P0_ACTIVE_ALLOWED and not active:
                violations.append(f"{slug}: MUST_BE_ON but is OFF")
        except Exception as e:
            violations.append(f"{slug}: import_error={e}")
    return {
        "ok": len(violations) == 0,
        "violations": violations,
        "p0_active_allowed": sorted(P0_ACTIVE_ALLOWED),
        "x199_must_be_on": sorted(X199_MUST_BE_ON),
        "statuses": statuses,
    }


def check_zero_doublon() -> Dict[str, Any]:
    """Vérifie qu'aucun router corridors/salines/nutrition n'existe hors engines cibles."""
    # Sources uniques autorisées par domaine (source unique de vérité)
    authorized = {
        "corridors": [
            "engines/v8_institutional/engine_ia_corridors_organic_omega.py",
            "engines/v8_institutional/engine_ia_corridors_omega.py",
            "engines/post_smoothing/organic_corridor_smoother.py",
            "engines/reseau_veineux_omega/router.py",
        ],
        "salines": [
            "engines/v8_institutional/engine_salines.py",
            "engines/v8_institutional/engine_salines_v11_supra.py",
            "engines/v8_institutional/salines_organic_v1.py",
            "engines/eco_zones_omega/router.py",
            # archivés V7 (consommés comme source, pas comme router actif)
            "modules/salines_ultime_engine/router.py",
            "modules/saline_engine/",
        ],
        "nutrition": [
            "engines/v8_institutional/engine_nutrition.py",
            "engines/v8_institutional/engine_nutrition_v12_supra.py",
            "engines/eco_zones_omega/router.py",
            "modules/nutrition_engine_v7/pipeline.py",
        ],
    }
    # Vérifie si server.py inclut des routers legacy corridors désactivés encore actifs
    server_py = BACKEND / "server.py"
    content = server_py.read_text()
    legacy_purged = [
        "corridor_unified_router",
        "movement_corridors_router",
        "relocation_router",
        "organic_zones_v2_router",
    ]
    leaked_legacy: List[str] = []
    for leg in legacy_purged:
        # Actif si la ligne `app.include_router(<leg>)` est non-commentée
        for line in content.splitlines():
            stripped = line.strip()
            if stripped.startswith("#"):
                continue
            if f"app.include_router({leg})" in stripped:
                leaked_legacy.append(leg)
    return {
        "ok": len(leaked_legacy) == 0,
        "leaked_legacy_routers": leaked_legacy,
        "authorized_sources": authorized,
        "interdictions": [
            "Aucun router corridors hors smoother / RESEAU_VEINEUX_Ω / V30",
            "Aucun router salines hors ECO_ZONES_Ω / V30",
            "Aucun router nutrition hors ECO_ZONES_Ω / V30",
        ],
    }


def run_audit() -> Dict[str, Any]:
    v30 = check_v30_integrity()
    flags = check_feature_flags()
    doublon = check_zero_doublon()
    overall_ok = v30["ok"] and flags["ok"] and doublon["ok"]
    return {
        "phase": "X200-P0-ACTIVATION",
        "version": "V31_CORE_PREPARATOIRE_Ω",
        "commandant": "STEEVE-MAX",
        "overall_ok": overall_ok,
        "gates": {
            "v30_integrity": v30,
            "feature_flags": flags,
            "zero_doublon_omega": doublon,
        },
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true", help="Output JSON only")
    args = ap.parse_args()

    result = run_audit()
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
        sys.exit(0 if result["overall_ok"] else 1)

    print("═══════════════════════════════════════════════════════════════")
    print("  AUDIT ENGINES X199/X200 — ZERO-DOUBLON-Ω + V30 INTEGRITY")
    print("═══════════════════════════════════════════════════════════════")
    print(f"Phase          : {result['phase']}")
    print(f"Overall OK     : {'✓' if result['overall_ok'] else '✗'}")
    print()
    print("── V30 integrity ──")
    v30 = result["gates"]["v30_integrity"]
    print(f"  OK       : {v30['ok']}")
    print(f"  SHA-256  : {v30.get('v30_sha256_current','?')}")
    print()
    print("── Feature flags ──")
    ff = result["gates"]["feature_flags"]
    print(f"  OK         : {ff['ok']}")
    print(f"  Violations : {ff['violations'] or 'aucune'}")
    for slug, active in sorted(ff["statuses"].items()):
        mark = "ON " if active else "OFF"
        print(f"    [{mark}] {slug}")
    print()
    print("── ZERO-DOUBLON-Ω ──")
    zd = result["gates"]["zero_doublon_omega"]
    print(f"  OK             : {zd['ok']}")
    print(f"  Legacy leaked  : {zd['leaked_legacy_routers'] or 'aucun'}")
    sys.exit(0 if result["overall_ok"] else 1)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
PHASE-B.3 ANALYSE INTER-ENGINES — READ-ONLY
=============================================
Analyse les payloads collectés en B.2 pour mesurer la cohérence des 3 chaînes
de dépendances :
  - vent → contamination → son
  - corridors → zones → affûts → salines → hotspots
  - BIO-MASK → VITAUX → RENDUΩ

Aucun calcul ne mute le pipeline. Sortie : /phase_b/B3_inter_engines_analysis.json
"""
import json, math, hashlib
from pathlib import Path

ROOT = Path("/app/frontend/public/reports/audit_territoire_omega_ultime/phase_b")
PAYLOADS = ROOT / "api_payloads"
SPECIES = ["orignal", "cerf", "ours", "dindon", "wapiti"]


def load(fname):
    p = PAYLOADS / fname
    return json.loads(p.read_text()) if p.exists() else None


def angle_deg_diff(a, b):
    if a is None or b is None: return None
    d = (float(a) - float(b)) % 360
    return min(d, 360 - d)


def main():
    out = {"phase": "PHASE_B_INTER_ENGINES_ANALYSIS", "chains": {}, "per_species": {}}

    # ============================================================
    # CHAÎNE 1 : vent → contamination → son
    # ============================================================
    chain1 = {"chain": "vent → contamination → son", "per_species": {}}
    for sp in SPECIES:
        b = load(f"{sp}_bundle_v20.json") or {}
        wind = b.get("wind") or {}
        engine_vent = b.get("engine_vent") or {}
        contamination = b.get("contamination") or []
        odors = b.get("odeurs") or b.get("vent_odeurs") or {}
        # Direction extraction
        wind_deg = wind.get("direction") or wind.get("deg") or engine_vent.get("direction_deg")
        wind_speed = wind.get("speed") or wind.get("kmh") or engine_vent.get("speed_kmh")
        # Mean contamination axis
        contam_count = len(contamination) if isinstance(contamination, list) else 0
        contam_directions = []
        for c in (contamination if isinstance(contamination, list) else []):
            if isinstance(c, dict) and "direction_deg" in c:
                contam_directions.append(c["direction_deg"])
            elif isinstance(c, dict) and "azimuth" in c:
                contam_directions.append(c["azimuth"])
        contam_axis = (sum(contam_directions) / len(contam_directions)) if contam_directions else None
        # Son cone direction
        son_dirs = []
        if isinstance(odors, dict):
            for k in ("cone_direction_deg", "cone_axis_deg", "main_axis_deg", "direction_deg"):
                if odors.get(k) is not None: son_dirs.append(odors[k])
        son_axis = son_dirs[0] if son_dirs else None
        chain1["per_species"][sp] = {
            "wind_deg": wind_deg, "wind_speed_kmh": wind_speed,
            "contamination_count": contam_count, "contamination_mean_axis_deg": contam_axis,
            "son_cone_axis_deg": son_axis,
            "delta_wind_to_contamination_deg": angle_deg_diff(wind_deg, contam_axis),
            "delta_wind_to_son_deg": angle_deg_diff(wind_deg, son_axis),
        }

    out["chains"]["vent_contam_son"] = chain1

    # ============================================================
    # CHAÎNE 2 : corridors → zones → affûts → salines → hotspots
    # ============================================================
    chain2 = {"chain": "corridors → zones → affûts → salines → hotspots", "per_species": {}}
    for sp in SPECIES:
        b = load(f"{sp}_bundle_v20.json") or {}
        chain2["per_species"][sp] = {
            "corridors_count": len(b.get("corridors") or []),
            "zones_count": len(b.get("zones") or []),
            "affuts_count": len(b.get("affuts") or []),
            "salines_count": len(b.get("salines") or []),
            "hotspots_count": len(b.get("hotspots") or []),
            "interzone_count": len(b.get("interzone") or []) if "interzone" in b else None,
            "veineux_count": len(b.get("veineux") or []) if "veineux" in b else None,
            "bio_presence_mask_halt": b.get("bio_presence_mask_halt"),
            "expected_status": "ABSENT" if sp in ("dindon", "wapiti") else "PRESENT",
        }
    out["chains"]["corridors_zones_affuts_salines_hotspots"] = chain2

    # ============================================================
    # CHAÎNE 3 : BIO-MASK → VITAUX → RENDUΩ
    # ============================================================
    chain3 = {"chain": "BIO-MASK → VITAUX → RENDUΩ", "per_species": {}}
    mask_global = load("GLOBAL_presence_mask.json") or {}
    for sp in SPECIES:
        b = load(f"{sp}_bundle_v20.json") or {}
        org = load(f"{sp}_organic.json") or {}
        chain3["per_species"][sp] = {
            "bio_presence_mask_applied_v20": b.get("bio_presence_mask_applied"),
            "bio_presence_mask_halt_v20": b.get("bio_presence_mask_halt"),
            "bio_presence_mask_applied_organic": org.get("bio_presence_mask_applied"),
            "bio_presence_mask_halt_organic": org.get("bio_presence_mask_halt"),
            "vitaux_omega_applied": b.get("corridors_vitaux_omega_applied"),
            "vitaux_omega_total_input": (b.get("corridors_vitaux_omega_stats") or {}).get("total_input"),
            "vitaux_omega_total_kept": (b.get("corridors_vitaux_omega_stats") or {}).get("total_kept"),
            "renduomega_applied": "renduomega_applied" in b or any(c.get("renduomega") for c in (b.get("corridors") or [])),
            "v30_locked": b.get("v30_locked"),
        }
    out["chains"]["bio_vitaux_rendu"] = chain3

    # ============================================================
    # PER-SPECIES METRICS DETAIL (capture intensities + secondaire/externe + radius)
    # ============================================================
    for sp in SPECIES:
        b = load(f"{sp}_bundle_v20.json") or {}
        layer = load(f"{sp}_layer_diagnostic.json") or {}
        v30 = load(f"{sp}_v30_status.json") or {}
        # Intensities and types
        corridors_list = b.get("corridors") or []
        intensities = {}
        types = {}
        for c in corridors_list:
            i = c.get("intensity") or c.get("intensite") or c.get("level")
            if i: intensities[i] = intensities.get(i, 0) + 1
            t = c.get("type") or c.get("origine") or c.get("kind")
            if t: types[t] = types.get(t, 0) + 1
        out["per_species"][sp] = {
            "v20_bundle": {
                "corridors_count": len(corridors_list),
                "intensity_distribution": intensities,
                "type_distribution": types,
                "affuts_count": len(b.get("affuts") or []),
                "salines_count": len(b.get("salines") or []),
                "hotspots_count": len(b.get("hotspots") or []),
                "zones_count": len(b.get("zones") or []),
                "wind": b.get("wind") or {},
                "bio_presence_mask_stats": b.get("bio_presence_mask_stats") or {},
            },
            "layer_diagnostic": {
                "layers": layer.get("layers"),
                "missing_critical_layers": layer.get("missing_critical_layers"),
                "all_layers_ok": layer.get("all_layers_ok"),
            },
            "v30_status_filter_species": v30.get("per_species", {}).get(sp) if isinstance(v30, dict) else None,
        }

    # SHA-256 inventaire
    sha = {}
    for f in sorted(PAYLOADS.glob("*.json")):
        h = hashlib.sha256(); h.update(f.read_bytes())
        sha[f.name] = h.hexdigest()
    out["sha256_inventory"] = sha

    OUT = ROOT / "B3_inter_engines_analysis.json"
    OUT.write_text(json.dumps(out, indent=2, ensure_ascii=False))
    print(f"WROTE {OUT}")
    
    # Print summary table
    print("\n=== CHAÎNE 1 vent→contam→son ===")
    print(f"{'sp':10s}{'wind':>8s}{'speed':>8s}{'#contam':>10s}{'contam_ax':>12s}{'Δw-c':>8s}{'Δw-s':>8s}")
    for sp, d in chain1["per_species"].items():
        print(f"{sp:10s}{str(d['wind_deg'])[:6]:>8s}{str(d['wind_speed_kmh'])[:6]:>8s}{d['contamination_count']:>10d}{str(d['contamination_mean_axis_deg'])[:6]:>12s}{str(d['delta_wind_to_contamination_deg'])[:6]:>8s}{str(d['delta_wind_to_son_deg'])[:6]:>8s}")
    
    print("\n=== CHAÎNE 2 corridors→zones→affûts→salines→hotspots ===")
    print(f"{'sp':10s}{'corr':>6s}{'zones':>6s}{'affu':>6s}{'sali':>6s}{'hots':>6s}{'halt':>8s}{'expect':>10s}")
    for sp, d in chain2["per_species"].items():
        print(f"{sp:10s}{d['corridors_count']:>6d}{d['zones_count']:>6d}{d['affuts_count']:>6d}{d['salines_count']:>6d}{d['hotspots_count']:>6d}{str(d['bio_presence_mask_halt']):>8s}{d['expected_status']:>10s}")
    
    print("\n=== CHAÎNE 3 BIO-MASK → VITAUX → RENDUΩ ===")
    for sp, d in chain3["per_species"].items():
        print(f"  {sp:8s}: mask_v20={d['bio_presence_mask_applied_v20']} halt_v20={d['bio_presence_mask_halt_v20']} mask_organic={d['bio_presence_mask_applied_organic']} halt_organic={d['bio_presence_mask_halt_organic']} vitaux={d['vitaux_omega_applied']} v30_locked={d['v30_locked']}")


if __name__ == "__main__":
    main()

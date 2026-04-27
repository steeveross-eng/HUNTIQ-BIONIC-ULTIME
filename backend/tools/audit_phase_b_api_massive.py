#!/usr/bin/env python3
"""
PHASE-B AUDIT API MASSIF — READ-ONLY
========================================
Récupère les payloads bruts du bundle V20 + endpoints d'audit pour les
5 espèces officielles (orignal, cerf, ours, dindon, wapiti) au waypoint
TERRITOIRE BSL (LAT 48.206657 / LNG -68.382422).

Aucune modification : V30, XIX, VITAUX intouchés.
"""
import json, time, urllib.request, urllib.parse
from pathlib import Path

API = "https://huntiq-restore.preview.emergentagent.com"
LAT, LNG = 48.206657, -68.382422
MONTH, HOUR = 10, 7
WIND_DEG, WIND_SPEED = 225.0, 15.0

OUT = Path("/app/frontend/public/reports/audit_territoire_omega_ultime/phase_b/api_payloads")
OUT.mkdir(parents=True, exist_ok=True)

SPECIES = [
    ("orignal", "PRESENT"),
    ("cerf", "PRESENT"),
    ("ours", "PRESENT"),
    ("dindon", "ABSENT"),
    ("wapiti", "ABSENT"),
]

# Note : aliases pour bundle V20 (qui utilise les noms canoniques)
SPECIES_BUNDLE_ALIAS = {
    "orignal": "orignal", "cerf": "chevreuil", "ours": "ours_noir",
    "dindon": "dindon_sauvage", "wapiti": "wapiti",
}


def get(url, fname):
    t0 = time.time()
    try:
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = resp.read()
            (OUT / fname).write_bytes(data)
            try:
                d = json.loads(data)
                return {"status": resp.status, "elapsed_ms": int(1000 * (time.time() - t0)),
                        "size_b": len(data), "is_json": True,
                        "top_level_keys": sorted(list(d.keys()))[:25] if isinstance(d, dict) else None}
            except Exception:
                return {"status": resp.status, "elapsed_ms": int(1000 * (time.time() - t0)),
                        "size_b": len(data), "is_json": False}
    except Exception as e:
        return {"status": None, "error": str(e)}


def main():
    summary = {"waypoint": {"lat": LAT, "lng": LNG, "month": MONTH, "hour": HOUR},
               "wind": {"deg": WIND_DEG, "speed": WIND_SPEED},
               "endpoints_per_species": {}}

    # Purge cache once
    try:
        req = urllib.request.Request(f"{API}/api/v20/territoire/bundle/purge", method="POST")
        with urllib.request.urlopen(req, timeout=10) as resp: resp.read()
        print("[PHASE-B] V20 cache purged")
    except Exception as e:
        print(f"[PHASE-B] purge warning: {e}")

    # 0) Endpoints globaux (independant species)
    print("\n=== B.2.0 ENDPOINTS GLOBAUX ===")
    for ep, fname in [
        (f"/api/v30/corridors/presence-mask?lat={LAT}&lng={LNG}", "GLOBAL_presence_mask.json"),
        (f"/api/v30/corridors/status?lat={LAT}&lon={LNG}", "GLOBAL_v30_status.json"),
        (f"/api/v30/corridors/layer-diagnostic?lat={LAT}&lon={LNG}&species=orignal", "GLOBAL_layer_diag_orignal.json"),
    ]:
        r = get(API + ep, fname)
        print(f"  {ep[:80]:80s}  {r}")

    # 1) Bundle complet V20 + layer-diagnostic + organic generation per species
    print("\n=== B.2.1 PAYLOADS PAR ESPECE ===")
    for sp, expected in SPECIES:
        bundle_sp = SPECIES_BUNDLE_ALIAS[sp]
        bucket = {}
        # 1a. bundle V20 (pipeline complet)
        url1 = f"{API}/api/v20/territoire/bundle?lat={LAT}&lon={LNG}&species={bundle_sp}&month={MONTH}&hour={HOUR}"
        bucket["bundle_v20"] = get(url1, f"{sp}_bundle_v20.json")
        # 1b. layer-diagnostic V30 brut
        url2 = f"{API}/api/v30/corridors/layer-diagnostic?lat={LAT}&lon={LNG}&species={sp}"
        bucket["layer_diagnostic"] = get(url2, f"{sp}_layer_diagnostic.json")
        # 1c. organic corridor generation
        url3 = f"{API}/api/v20/territoire/corridors-organic/generate"
        body = json.dumps({"lat": LAT, "lon": LNG, "species": bundle_sp, "month": MONTH, "hour": HOUR,
                           "wind_deg": WIND_DEG, "wind_speed": WIND_SPEED}).encode()
        try:
            t0 = time.time()
            req = urllib.request.Request(url3, data=body, method="POST",
                                         headers={"Content-Type": "application/json", "Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=60) as resp:
                d = resp.read()
                (OUT / f"{sp}_organic.json").write_bytes(d)
                bucket["organic"] = {"status": resp.status, "elapsed_ms": int(1000 * (time.time() - t0)),
                                     "size_b": len(d)}
        except Exception as e:
            bucket["organic"] = {"error": str(e)}
        # 1d. v30 status par espèce
        url4 = f"{API}/api/v30/corridors/status?species={sp}&lat={LAT}&lon={LNG}"
        bucket["v30_status_species"] = get(url4, f"{sp}_v30_status.json")

        summary["endpoints_per_species"][sp] = {"expected_bio_status": expected, **bucket}
        print(f"  {sp:8s} ({expected}): bundle={bucket['bundle_v20'].get('status')} layer={bucket['layer_diagnostic'].get('status')} organic={bucket['organic'].get('status')}")

    out_summary = OUT.parent / "B2_api_audit_summary.json"
    out_summary.write_text(json.dumps(summary, indent=2, ensure_ascii=False))
    print(f"\n[PHASE-B] Summary saved: {out_summary}")


if __name__ == "__main__":
    main()

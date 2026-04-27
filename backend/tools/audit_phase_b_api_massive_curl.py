#!/usr/bin/env python3
"""PHASE-B AUDIT API MASSIF — version curl wrapper (User-Agent évite 403)."""
import json, time, subprocess
from pathlib import Path

API = "https://huntiq-restore.preview.emergentagent.com"
LAT, LNG = 48.206657, -68.382422
MONTH, HOUR = 10, 7
OUT = Path("/app/frontend/public/reports/audit_territoire_omega_ultime/phase_b/api_payloads")
OUT.mkdir(parents=True, exist_ok=True)

UA = "BCE4X-AUDIT/1.0 (+territoire-omega-ultime)"

SPECIES = [("orignal","PRESENT"),("cerf","PRESENT"),("ours","PRESENT"),("dindon","ABSENT"),("wapiti","ABSENT")]
ALIAS = {"orignal":"orignal","cerf":"chevreuil","ours":"ours_noir","dindon":"dindon_sauvage","wapiti":"wapiti"}


def curl_get(url, fname):
    t0 = time.time()
    try:
        out_path = OUT / fname
        cmd = ["curl", "-sS", "-A", UA, "-o", str(out_path), "-w", "%{http_code}", url]
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=90)
        code = r.stdout.strip()
        size = out_path.stat().st_size if out_path.exists() else 0
        try:
            d = json.loads(out_path.read_text())
            keys = sorted(list(d.keys()))[:25] if isinstance(d, dict) else None
        except Exception: keys = None
        return {"status": int(code) if code.isdigit() else None, "elapsed_ms": int(1000*(time.time()-t0)),
                "size_b": size, "top_level_keys": keys}
    except Exception as e:
        return {"error": str(e)}


def curl_post(url, body, fname):
    t0 = time.time()
    try:
        out_path = OUT / fname
        cmd = ["curl", "-sS", "-A", UA, "-X", "POST", "-H", "Content-Type: application/json",
               "-d", json.dumps(body), "-o", str(out_path), "-w", "%{http_code}", url]
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=90)
        code = r.stdout.strip()
        size = out_path.stat().st_size if out_path.exists() else 0
        return {"status": int(code) if code.isdigit() else None, "elapsed_ms": int(1000*(time.time()-t0)), "size_b": size}
    except Exception as e:
        return {"error": str(e)}


def main():
    summary = {"waypoint": {"lat": LAT, "lng": LNG, "month": MONTH, "hour": HOUR},
               "endpoints_per_species": {}}
    
    # Purge cache
    print(curl_post(f"{API}/api/v20/territoire/bundle/purge", {}, "GLOBAL_purge.json"))

    print("\n=== B.2.0 ENDPOINTS GLOBAUX ===")
    for ep, fname in [
        (f"/api/v30/corridors/presence-mask?lat={LAT}&lng={LNG}", "GLOBAL_presence_mask.json"),
        (f"/api/v30/corridors/status?lat={LAT}&lon={LNG}", "GLOBAL_v30_status.json"),
        (f"/api/v30/corridors/layer-diagnostic?lat={LAT}&lon={LNG}&species=orignal", "GLOBAL_layer_diag_orignal.json"),
    ]:
        r = curl_get(API + ep, fname)
        print(f"  {ep[:75]:75s}  {r}")

    print("\n=== B.2.1 PAYLOADS PAR ESPECE ===")
    for sp, expected in SPECIES:
        bundle_sp = ALIAS[sp]
        bucket = {}
        bucket["bundle_v20"] = curl_get(f"{API}/api/v20/territoire/bundle?lat={LAT}&lon={LNG}&species={bundle_sp}&month={MONTH}&hour={HOUR}", f"{sp}_bundle_v20.json")
        bucket["layer_diag"] = curl_get(f"{API}/api/v30/corridors/layer-diagnostic?lat={LAT}&lon={LNG}&species={sp}", f"{sp}_layer_diagnostic.json")
        bucket["organic"] = curl_post(f"{API}/api/v20/territoire/corridors-organic/generate",
                                      {"lat": LAT, "lon": LNG, "species": bundle_sp, "month": MONTH, "hour": HOUR,
                                       "wind_deg": 225.0, "wind_speed": 15.0}, f"{sp}_organic.json")
        bucket["v30_status_species"] = curl_get(f"{API}/api/v30/corridors/status?species={sp}&lat={LAT}&lon={LNG}", f"{sp}_v30_status.json")
        summary["endpoints_per_species"][sp] = {"expected_bio_status": expected, **bucket}
        print(f"  {sp:8s} ({expected}): bundle={bucket['bundle_v20'].get('status')} layer={bucket['layer_diag'].get('status')} organic={bucket['organic'].get('status')}")

    out = OUT.parent / "B2_api_audit_summary.json"
    out.write_text(json.dumps(summary, indent=2, ensure_ascii=False))
    print(f"\n[PHASE-B.2] Summary: {out}")


if __name__ == "__main__":
    main()

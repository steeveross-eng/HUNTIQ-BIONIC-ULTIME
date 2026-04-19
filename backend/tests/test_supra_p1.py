"""TEST P1 SUPRA (6 engines + science catalog + monitoring)"""
import os, sys, requests
API = os.environ.get("SELF_TEST_API", "http://localhost:8001")

def main():
    failures = []
    sys.path.insert(0, "/app/backend")

    # Import checks
    mods = [
        ("engine_espece_omega", "compute_especes"),
        ("engine_comportement_biologique_omega", "compute_comportement_biologique"),
        ("engine_connectivite_ecologique_omega", "compute_connectivite_ecologique"),
        ("engine_thermique_microclimat_omega", "compute_thermique_microclimat"),
        ("engine_sensoriel_vent_odeurs_omega", "compute_sensoriel_vent_odeurs"),
        ("engine_ia_vision_ecologique_omega", "compute_ia_vision_ecologique"),
    ]
    for modname, fn in mods:
        try:
            m = __import__(f"engines.v8_institutional.{modname}", fromlist=[fn])
            if not hasattr(m, fn): failures.append(f"{modname}.{fn} missing")
        except Exception as e:
            failures.append(f"import {modname}: {e}")

    # Check SCIENCE-Ω catalog expose les 5 especes
    try:
        from engines.v8_institutional.engine_science_omega import get_catalog_summary, get_species_profile
        summary = get_catalog_summary()
        if summary["species_count"] < 5:
            failures.append(f"species_count {summary['species_count']} < 5")
        for sp in ["orignal", "chevreuil", "wapiti", "ours_noir", "dindon_sauvage"]:
            if not get_species_profile(sp):
                failures.append(f"species profile missing: {sp}")
    except Exception as e:
        failures.append(f"science catalog: {e}")

    # Endpoint monitoring + alertes
    try:
        r = requests.get(f"{API}/api/v20/territoire/monitoring", timeout=15)
        if r.status_code != 200:
            failures.append(f"monitoring HTTP {r.status_code}")
        else:
            d = r.json()
            if d.get("global_status") not in ("ok", "warning", "fail"):
                failures.append(f"global_status invalide: {d.get('global_status')}")
    except Exception as e:
        failures.append(f"monitoring: {e}")

    try:
        r = requests.get(f"{API}/api/v20/territoire/alertes", timeout=15)
        if r.status_code != 200:
            failures.append(f"alertes HTTP {r.status_code}")
    except Exception as e:
        failures.append(f"alertes: {e}")

    # Bundle expose les 6 P1 SUPRA
    try:
        r = requests.get(f"{API}/api/v20/territoire/bundle?lat=46.8139&lon=-71.208&species=cerf&month=10&hour=7&wind_deg=225&wind_speed=15", timeout=30)
        if r.status_code != 200:
            failures.append(f"bundle HTTP {r.status_code}")
        else:
            data = r.json()
            for k in ["espece_profile", "comportement_biologique", "connectivite_ecologique", "thermique_microclimat", "sensoriel_vent_odeurs", "ia_vision_ecologique"]:
                if not data.get(k):
                    failures.append(f"bundle missing '{k}'")
    except Exception as e:
        failures.append(f"bundle: {e}")

    if failures:
        print("\n=== FAILURES ==="); [print(f) for f in failures]; sys.exit(1)
    print("[OK] test_supra_p1 passes")

if __name__ == "__main__": main()

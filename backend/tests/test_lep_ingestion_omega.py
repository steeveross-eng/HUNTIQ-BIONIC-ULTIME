"""SELF-AUDIT-Ω — test_lep_ingestion_omega (Phase XI-SUPRA-D)
=====================================================================
Vérifie que l'engine LEP-INGESTION-Ω est installé et prêt (même avant
ingestion de la FGDB officielle ECCC).

Critères :
  - Engine enregistré dans engine_science_omega registry
  - Dossiers persistants existent
  - registry.json accessible (même si status NOT_INGESTED)
  - pyogrio + geopandas + driver OpenFileGDB disponibles
"""
import sys
from pathlib import Path
sys.path.insert(0, "/app/backend")

errors = []

# Import trigger (subprocess loads module → register_engine fires)
try:
    from engines.v8_institutional import lep_ingestion_omega  # noqa: F401
except Exception as e:
    errors.append(f"import lep_ingestion_omega: {e}")

# 1. Engine registered
from engines.v8_institutional.engine_science_omega import get_catalog  # noqa: E402
cat = get_catalog()
# get_catalog() returns list of engine dicts directly
if isinstance(cat, dict):
    cat_list = cat.get("engines", [])
else:
    cat_list = list(cat)
names = [e.get("name") if isinstance(e, dict) else str(e) for e in cat_list]
if "LEP-INGESTION-Ω" not in names:
    errors.append(f"LEP-INGESTION-Ω absent du catalog live: sample={names[:5]}")

# 2. Directories
ROOT = Path("/app/data/territoire_omega")
for d in ("data_primary_fgdb_lep", "data_secondary_geojson_lep"):
    if not (ROOT / d).is_dir():
        errors.append(f"dossier manquant: {ROOT / d}")

# 3. pyogrio + OpenFileGDB driver
try:
    import pyogrio
    drivers = pyogrio.list_drivers()
    if "OpenFileGDB" not in drivers:
        errors.append("driver OpenFileGDB indisponible")
    if "GeoJSON" not in drivers:
        errors.append("driver GeoJSON indisponible")
except Exception as e:
    errors.append(f"pyogrio indisponible: {e}")

try:
    import geopandas  # noqa: F401
except Exception as e:
    errors.append(f"geopandas indisponible: {e}")

# 4. LEP engine module loadable (router + helpers)
try:
    from engines.v8_institutional.lep_ingestion_omega import (
        router as _r, get_status, is_ingested, SOURCE_URL,
    )
    _ = _r  # silence lint
    st = get_status()
    if st.get("source") != SOURCE_URL:
        errors.append(f"SOURCE_URL divergent dans status: {st.get('source')}")
    if st.get("status") not in ("NOT_INGESTED", "INGESTED"):
        errors.append(f"status LEP invalide: {st.get('status')}")
    _ = is_ingested()
except Exception as e:
    errors.append(f"module LEP-INGESTION-Ω non chargeable: {e}")

if errors:
    print("FAIL: LEP-INGESTION-Ω non conforme:")
    for e in errors: print(" -", e)
    sys.exit(1)
print("OK: LEP-INGESTION-Ω installé (pyogrio+geopandas+OpenFileGDB prêts, dossiers créés, registry exposé)")
sys.exit(0)

"""SELF-AUDIT-Ω — test_healthpanel (Phase X)
Vérifie que les endpoints alimentant le Institutional Health Panel sont fonctionnels.
"""
import sys
sys.path.insert(0, "/app/backend")

# Force le chargement des engines pour alimenter le catalog in-memory
import engines.v8_institutional.engine_science_omega  # noqa: F401,E402
import engines.v8_institutional.engine_gouvernance_omega  # noqa: F401,E402
import engines.v8_institutional.engine_qualite_donnees_omega  # noqa: F401,E402
import engines.v8_institutional.engine_incertitude_omega  # noqa: F401,E402
import engines.v8_institutional.engine_calibration_omega  # noqa: F401,E402
import engines.v8_institutional.engine_calibration_dynamique_omega  # noqa: F401,E402
import engines.v8_institutional.engine_contamination_v2_omega  # noqa: F401,E402
import engines.v8_institutional.engine_espece_omega  # noqa: F401,E402
import engines.v8_institutional.engine_connectivite_ecologique_omega  # noqa: F401,E402
import engines.v8_institutional.engine_ia_vision_ecologique_omega  # noqa: F401,E402
import engines.v8_institutional.engine_population_dynamics_omega  # noqa: F401,E402
import engines.v8_institutional.engine_habitat_supra  # noqa: F401,E402
import engines.v8_institutional.engine_comportement_biologique_omega  # noqa: F401,E402
import engines.v8_institutional.engine_stress_anthropique_omega  # noqa: F401,E402
import engines.v8_institutional.engine_sensoriel_vent_odeurs_omega  # noqa: F401,E402
import engines.v8_institutional.engine_thermique_microclimat_omega  # noqa: F401,E402
import engines.v8_institutional.engine_climat_futur_omega  # noqa: F401,E402
import engines.v8_institutional.engine_influence_lunaire_omega  # noqa: F401,E402
import engines.v8_institutional.engine_pression_atmospherique_omega  # noqa: F401,E402
import engines.v8_institutional.engine_hydrologie_supra  # noqa: F401,E402
import engines.v8_institutional.engine_sol_supra  # noqa: F401,E402
import engines.v8_institutional.monitoring_alerte_omega  # noqa: F401,E402
import engines.v8_institutional.science_gaps_datasets  # noqa: F401,E402
import engines.v8_institutional.engine_canada_omega  # noqa: F401,E402

from engines.v8_institutional.engine_science_omega import get_catalog, get_data_sources  # noqa: E402
from engines.v8_institutional.registry_lock_omega import get_registry_lock_status  # noqa: E402

errors = []

catalog = get_catalog()
if len(catalog) < 20:
    errors.append(f"engines catalog < 20 ({len(catalog)})")

sources = get_data_sources()
if not sources:
    errors.append("data_sources vide")

lock = get_registry_lock_status()
if lock["engines_count"] < 22:
    errors.append(f"registry lock < 22 ({lock['engines_count']})")

required_fields = {"engines_count", "sha256", "document_maitre"}
if not required_fields.issubset(set(lock.keys())):
    errors.append(f"lock manque champs: {required_fields - set(lock.keys())}")

if catalog and not {"name", "version", "pillar"}.issubset(set(catalog[0].keys())):
    errors.append(f"catalog[0] manque champs (keys={list(catalog[0].keys())})")

if errors:
    print("FAIL:"); [print(" -", e) for e in errors]; sys.exit(1)
print(f"OK: health panel data OK ({len(catalog)} engines catalog, {lock['engines_count']} locked)")
sys.exit(0)

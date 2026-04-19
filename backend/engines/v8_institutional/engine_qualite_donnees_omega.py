"""ENGINE-QUALITÉ-DONNÉES-Ω — Audit complétude/cohérence/fraicheur."""
import time
from engines.v8_institutional.engine_science_omega import (
    register_engine, mark_call, get_catalog, get_datasets, get_studies, get_catalog_summary,
)

ENGINE_NAME = "ENGINE-QUALITE-DONNEES-Ω"
ENGINE_VERSION = "V1-SUPRA-2026-04"

register_engine(ENGINE_NAME, ENGINE_VERSION, "Audit qualite des donnees (completude, coherence, fraicheur)", "GOUVERNANCE", [])


def _completeness(summary: dict) -> float:
    """% champs catalog renseignes (species, studies, datasets, engine_links)."""
    need = [summary.get("species_count", 0) >= 5,
            summary.get("studies_count", 0) >= 3,
            summary.get("datasets_count", 0) >= 5,
            summary.get("engine_links_count", 0) >= 5]
    return round(sum(need) / len(need) * 100, 1)


def _coherence(datasets: list, studies: list) -> float:
    """Ratio de datasets avec URL (proxy coherence linkage)."""
    if not datasets:
        return 0.0
    with_url = sum(1 for d in datasets if d.get("url"))
    return round(with_url / len(datasets) * 100, 1)


def _freshness(engines_catalog: list) -> float:
    """% engines appeles recemment (< 1h depuis dernier call OU appeles au moins 1 fois)."""
    if not engines_catalog:
        return 0.0
    now = time.time()
    active = 0
    for e in engines_catalog:
        last = e.get("last_called_at") or 0
        if last > 0 and (now - last) < 3600:
            active += 1
    return round(active / len(engines_catalog) * 100, 1)


def compute_quality_data() -> dict:
    mark_call(ENGINE_NAME)
    summary = get_catalog_summary()
    datasets = get_datasets()
    studies = get_studies()
    engines = get_catalog()

    completeness = _completeness(summary)
    coherence = _coherence(datasets, studies)
    freshness = _freshness(engines)
    score = round(completeness * 0.40 + coherence * 0.30 + freshness * 0.30, 1)

    # Statut qualite
    if score > 80:
        status = "EXCELLENT"
    elif score > 60:
        status = "BON"
    elif score > 40:
        status = "MODERE"
    else:
        status = "FAIBLE"

    return {
        "engine": ENGINE_NAME, "version": ENGINE_VERSION,
        "score": score, "status": status,
        "completeness": completeness,
        "coherence": coherence,
        "freshness": freshness,
        "details": {
            "species_profiles": summary.get("species_count"),
            "studies": summary.get("studies_count"),
            "datasets": summary.get("datasets_count"),
            "datasets_with_url": sum(1 for d in datasets if d.get("url")),
            "engines_active_last_hour": int(freshness / 100 * len(engines)),
            "total_engines": len(engines),
        },
        "limites": [
            "Fraicheur basee sur last_called_at (perime au redemarrage pod)",
            "Coherence = proxy presence URL (pas de deep-check)",
        ],
    }

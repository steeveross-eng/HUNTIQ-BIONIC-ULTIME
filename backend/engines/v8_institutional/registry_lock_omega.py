"""
REGISTRY-LOCK-Ω — Verrouillage institutionnel Phase XI
=======================================================
Gèle les 22 engines SUPRA-Ω comme architecture officielle.
Calcule + expose le hash SHA-256 du Document Maître.
Interdit toute dérive non validée (GOUVERNANCE + SELF-AUDIT + SCIENCE-GUARD + PERF-GUARD).

Endpoints (admin):
  GET /api/v20/territoire/registry-lock
  GET /api/v20/territoire/document-maitre-lock
"""
import hashlib
import json
from pathlib import Path
from fastapi import APIRouter

router = APIRouter(prefix="/api/v20/territoire", tags=["V20 Registry Lock"])

# ============================================================
# REGISTRE OFFICIEL — 22 ENGINES SUPRA-Ω (Phase I → X)
# GEL INSTITUTIONNEL — modification = VIOLATION BCE-4X
# ============================================================
ENGINES_LOCKED = [
    # GOUVERNANCE (7)
    {"name": "ENGINE-SCIENCE-Ω", "pillar": "GOUVERNANCE", "phase": "VIII"},
    {"name": "ENGINE-GOUVERNANCE-Ω", "pillar": "GOUVERNANCE", "phase": "VIII"},
    {"name": "ENGINE-QUALITE-DONNEES-Ω", "pillar": "GOUVERNANCE", "phase": "P2"},
    {"name": "ENGINE-INCERTITUDE-Ω", "pillar": "GOUVERNANCE", "phase": "P2"},
    {"name": "ENGINE-CALIBRATION-Ω", "pillar": "GOUVERNANCE", "phase": "P2"},
    {"name": "ENGINE-CALIBRATION-DYNAMIQUE-Ω", "pillar": "GOUVERNANCE", "phase": "X"},
    {"name": "ANTI-CONTAMINATION-INSTITUTIONNEL-Ω", "pillar": "GOUVERNANCE", "phase": "X"},
    # BIO-SYSTEME (6)
    {"name": "ENGINE-ESPECE-Ω", "pillar": "BIO-SYSTEME", "phase": "P1"},
    {"name": "ENGINE-CONNECTIVITE-ECOLOGIQUE-Ω", "pillar": "BIO-SYSTEME", "phase": "P1"},
    {"name": "ENGINE-IA-VISION-ECOLOGIQUE-Ω", "pillar": "BIO-SYSTEME", "phase": "P1"},
    {"name": "ENGINE-POPULATION-DYNAMICS-Ω", "pillar": "BIO-SYSTEME", "phase": "P2"},
    {"name": "ENGINE-CONTAMINATION-Ω-V2", "pillar": "BIO-SYSTEME", "phase": "X"},
    {"name": "ENGINE-HABITAT-SUPRA", "pillar": "BIO-SYSTEME", "phase": "SUPRA"},
    # COMPORTEMENT-HUMAIN (2)
    {"name": "ENGINE-COMPORTEMENT-BIOLOGIQUE-Ω", "pillar": "COMPORTEMENT-HUMAIN", "phase": "P1"},
    {"name": "ENGINE-STRESS-ANTHROPIQUE-Ω", "pillar": "COMPORTEMENT-HUMAIN", "phase": "SUPRA"},
    # SYSTEME-SENSORIEL (1)
    {"name": "ENGINE-SENSORIEL-VENT-ODEURS-Ω", "pillar": "SYSTEME-SENSORIEL", "phase": "P1"},
    # ENVIRONNEMENT (6)
    {"name": "ENGINE-THERMIQUE-MICROCLIMAT-Ω", "pillar": "ENVIRONNEMENT", "phase": "P1"},
    {"name": "ENGINE-CLIMAT-FUTUR-Ω", "pillar": "ENVIRONNEMENT", "phase": "P3"},
    {"name": "ENGINE-INFLUENCE-LUNAIRE-Ω", "pillar": "ENVIRONNEMENT", "phase": "P3"},
    {"name": "ENGINE-PRESSION-ATMOSPHERIQUE-Ω", "pillar": "ENVIRONNEMENT", "phase": "P3"},
    {"name": "ENGINE-HYDROLOGIE-SUPRA", "pillar": "ENVIRONNEMENT", "phase": "SUPRA"},
    {"name": "ENGINE-SOL-SUPRA", "pillar": "ENVIRONNEMENT", "phase": "SUPRA"},
    # MONITORING (1)
    {"name": "ENGINE-MONITORING-Ω", "pillar": "GOUVERNANCE", "phase": "P0"},
    {"name": "ENGINE-ALERTE-ANOMALIES-Ω", "pillar": "GOUVERNANCE", "phase": "P0"},
    {"name": "ENGINE-NUTRITION-V12-SUPRA", "pillar": "BIO-SYSTEME", "phase": "XI-SUPRA"},
    # Phase X-B additions
    {"name": "SCIENCE-GAPS-DATASETS-Ω", "pillar": "GOUVERNANCE", "phase": "X"},
    {"name": "ENGINE-CANADA-Ω", "pillar": "GOUVERNANCE", "phase": "X-B"},
    # Phase X-C additions
    {"name": "FEDERAL-DATASETS-Ω", "pillar": "GOUVERNANCE", "phase": "X-C"},
    {"name": "ENGINE-RISQUES-HYDRO-Ω", "pillar": "ENVIRONNEMENT", "phase": "X-C"},
    # Phase X-D additions (observabilité)
    {"name": "SLA-BASELINE-30J-Ω", "pillar": "GOUVERNANCE", "phase": "X-D"},
    {"name": "SELF-AUDIT-ALERTS-Ω", "pillar": "GOUVERNANCE", "phase": "X-D"},
    {"name": "EXPORT-INSTITUTIONNEL-V20-Ω", "pillar": "GOUVERNANCE", "phase": "X-D"},
    # Phase XI-SUPRA (rendu institutionnel)
    {"name": "ENGINE-RENDER-Ω", "pillar": "GOUVERNANCE", "phase": "XI-SUPRA"},
    # Phase XI-SUPRA-B (preuve visuelle)
    {"name": "VISUAL-PROOF-Ω", "pillar": "GOUVERNANCE", "phase": "XI-SUPRA-B"},
    # Phase XI-SUPRA-C (capture DOM Playwright live)
    {"name": "VISUAL-PROOF-LIVE-Ω", "pillar": "GOUVERNANCE", "phase": "XI-SUPRA-C"},
    # Phase XI-SUPRA-G (ORDRE_TERRITOIRE_PROTECT_Ω)
    {"name": "ENGINE-TERRITOIRE-ANTI-REGRESSION-Ω", "pillar": "GOUVERNANCE", "phase": "XI-SUPRA-G"},
    # Phase XI-SUPRA-H (ENGINE CORRIDORS VERSION Ω — IA-CORRIDORS)
    {"name": "ENGINE-IA-CORRIDORS-Ω", "pillar": "GOUVERNANCE", "phase": "XI-SUPRA-H"},
    # Phase XI-SUPRA-K (RENDU + EXPLAIN + SPECIES + IA-VISION registry)
    {"name": "ENGINE-RENDU-Ω", "pillar": "GOUVERNANCE", "phase": "XI-SUPRA-K"},
    {"name": "ENGINE-SPECIES-PROFILES-Ω", "pillar": "BIO-SYSTEME", "phase": "XI-SUPRA-K"},
    {"name": "ENGINE-IA-VISION-REGISTRY-Ω", "pillar": "BIO-SYSTEME", "phase": "XI-SUPRA-K"},
    # Phase XI-SUPRA-D : LEP-INGESTION-Ω retiré du lock
    # Directive STEEVE-MAX 2026-04-20 — EXCLUDE_LAYER LEP_CRITICAL_HABITAT_NATIONAL
    # REASON "Dataset trop lourd, non essentiel, impact nul sur les engines"
    # STATUS OFFICIAL — engine source conservé mais non enregistré.
]

REGISTRY_VERSION = "V24-SUPRA-LOCKED-PHASE-XI-SUPRA-L-2026-04"
REGISTRY_SEALED_AT = "2026-04-20T21:00:00Z"

# Phase XI-SUPRA-E §V : Archive reconstructible — hash consigné dans le lock
# Ce hash doit correspondre au fichier /app/memory/ARCHIVE_BIONIC_V20_SUPRA.tar.gz
# Toute reconstruction doit vérifier cet invariant avant déploiement.
ARCHIVE_BIONIC_V20_SUPRA_SHA256 = "f07d2c25687db5c5c08c367f95a7a514494ee71f6fec20e2de756731ffbc2509"
ARCHIVE_BIONIC_V20_SUPRA_PATH = "/app/memory/ARCHIVE_BIONIC_V20_SUPRA.tar.gz"
ARCHIVE_BIONIC_V20_SUPRA_SIZE = 33664783

DOCUMENT_MAITRE_PATH = Path("/app/memory/DOCUMENT_MAITRE_ULTIME_MAX.md")
DOCUMENT_MAITRE_LOCKED_PATH = Path("/app/memory/DOCUMENT_MAITRE_LOCKED.md")


def _registry_hash() -> str:
    payload = json.dumps(
        {"version": REGISTRY_VERSION, "sealed_at": REGISTRY_SEALED_AT, "engines": ENGINES_LOCKED},
        sort_keys=True,
        ensure_ascii=False,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _document_maitre_hash() -> str:
    """SHA-256 du Document Maître si présent."""
    if not DOCUMENT_MAITRE_PATH.exists():
        return "MISSING"
    return hashlib.sha256(DOCUMENT_MAITRE_PATH.read_bytes()).hexdigest()


def assert_registry_locked(live_catalog_names: list) -> dict:
    """Vérifie conformité du catalog live vs registry scellé.
    Retourne violations. Appelé par SELF-AUDIT-Ω.
    """
    locked_set = {e["name"] for e in ENGINES_LOCKED}
    live_set = set(live_catalog_names)
    missing = sorted(locked_set - live_set)
    # extras tolerés (auxiliaires non-scellés) mais loggés
    extras = sorted(live_set - locked_set)
    return {
        "conforme": len(missing) == 0,
        "locked_total": len(locked_set),
        "live_total": len(live_set),
        "missing": missing,
        "extras_non_locked": extras,
    }


def get_registry_lock_status() -> dict:
    return {
        "version": REGISTRY_VERSION,
        "sealed_at": REGISTRY_SEALED_AT,
        "engines_count": len(ENGINES_LOCKED),
        "engines": ENGINES_LOCKED,
        "sha256": _registry_hash(),
        "document_maitre": {
            "path": str(DOCUMENT_MAITRE_PATH),
            "exists": DOCUMENT_MAITRE_PATH.exists(),
            "sha256": _document_maitre_hash(),
        },
        "validators": [
            "ENGINE-GOUVERNANCE-Ω",
            "SELF-AUDIT-Ω",
            "SCIENCE-GUARD (ENGINE-SCIENCE-Ω)",
            "PERF-GUARD-Ω",
        ],
    }


@router.get("/registry-lock")
async def v20_registry_lock():
    """REGISTRY-LOCK-Ω: registre scellé des 22 engines SUPRA-Ω + hash."""
    return get_registry_lock_status()


@router.get("/document-maitre-lock")
async def v20_document_maitre_lock():
    """DOCUMENT-MAITRE-LOCKED: hash + métadonnées Document Maître institutionnel."""
    exists = DOCUMENT_MAITRE_PATH.exists()
    size = DOCUMENT_MAITRE_PATH.stat().st_size if exists else 0
    return {
        "path": str(DOCUMENT_MAITRE_PATH),
        "exists": exists,
        "size_bytes": size,
        "sha256": _document_maitre_hash(),
        "locked_report": str(DOCUMENT_MAITRE_LOCKED_PATH),
        "validators": [
            "ENGINE-GOUVERNANCE-Ω",
            "SELF-AUDIT-Ω",
            "SCIENCE-GUARD",
            "PERF-GUARD-Ω",
        ],
        "sealed_at": REGISTRY_SEALED_AT,
    }

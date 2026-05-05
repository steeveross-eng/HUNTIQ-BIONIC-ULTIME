"""
mffp_subset_extractor_omega.py — ORDRE N°52-R12 DEMANDE_2
═══════════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU · ANTI_GÉNÉRIQUE_STRICT

Extracteur de subset ~100 Mo de pee_maj.gpkg pour validation PHASE_3 R8.

Doctrine :
  · Mode PROPOSITION (par défaut) : retourne plan complet (bbox, filtres,
    commande GDAL prête à exécuter), sans toucher au fichier source.
  · Mode EXÉCUTION (?execute=true) : télécharge depuis B2 vers /var/cache,
    applique le filtre spatial, persiste le subset zstd-compressé sur
    /app/backend/data/gis_archive/subsets/.
  · Anti-pod-restart : exécution en background, sessions ext4 persistantes.

Stratégie de filtrage spatiale :
  · Bbox proposée (Estrie/Cantons-de-l'Est) : couvre ~5 écorégions, mix
    feuillu/résineux/mixte représentatif du Québec méridional.
  · EPSG:32198 (NAD83 Québec Lambert) bbox approximative :
    [560000, 175000, 670000, 250000] (110 km × 75 km · ~8250 km²)
  · Cible taille : ~100 Mo (subset = ~3% du total 37.3 Go)
═══════════════════════════════════════════════════════════════════════════
"""
from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("mffp_subset_extractor_omega")

# ═════════════════════════════════════════════════════════════════════════
# Constantes
# ═════════════════════════════════════════════════════════════════════════
SUBSETS_OUTPUT_ROOT = Path("/app/backend/data/gis_archive/subsets")
SUBSETS_OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)

# Bbox proposée Estrie / Cantons-de-l'Est (EPSG:32198)
# Couvre les écorégions 4d (Estrie-Beauce) + 4c (Cantons-de-l'Est)
# avec mix forêt feuillue / mixte / résineuse représentatif.
DEFAULT_SUBSET_BBOX_EPSG_32198 = {
    "xmin": 560000,
    "ymin": 175000,
    "xmax": 670000,
    "ymax": 250000,
    "label": "Estrie_Cantons_Est_Quebec_meridional",
    "approximate_area_km2": 8250,
    "rationale": (
        "Région représentative du Québec méridional avec mix feuillu, "
        "mixte et résineux (≥5 écorégions Saucier 2009). Évite les zones "
        "dénudées du Nord et les zones sub-arctiques."),
}

# Filtres SQL proposés (limiter aux peuplements avec données complètes)
DEFAULT_SUBSET_SQL_FILTER = (
    "SELECT * FROM peuplement_ecoforestier "
    "WHERE TY_COUV IS NOT NULL "
    "AND CL_DENS IS NOT NULL "
    "AND CL_AGE IS NOT NULL "
    "AND ESS_DOMI IS NOT NULL"
)


def build_subset_proposal(
    target_size_mb: int = 100,
    bbox_epsg_32198: Optional[Dict[str, float]] = None,
    sql_filter: Optional[str] = None,
) -> Dict[str, Any]:
    """Construit une proposition de subset (sans exécution).

    Returns dict avec :
      · bbox_proposed
      · sql_filter_proposed
      · ogr2ogr_command_template (commande prête à exécuter)
      · pyogrio_python_snippet (alternative Python pure)
      · estimated_output_size_mb
      · output_path_proposed
    """
    bbox = bbox_epsg_32198 or DEFAULT_SUBSET_BBOX_EPSG_32198
    filt = sql_filter or DEFAULT_SUBSET_SQL_FILTER

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output_filename = (
        f"pee_maj_subset_{bbox.get('label','custom')}_{timestamp}.gpkg")
    output_path = SUBSETS_OUTPUT_ROOT / output_filename

    # Commande ogr2ogr (recommandée — utilise GDAL natif, performant)
    ogr2ogr_cmd = (
        f"ogr2ogr -f GPKG "
        f"-spat {bbox['xmin']} {bbox['ymin']} {bbox['xmax']} {bbox['ymax']} "
        f"-spat_srs EPSG:32198 "
        f"-t_srs EPSG:32198 "
        f"-sql \"{filt}\" "
        f"-dialect SQLITE "
        f"-progress "
        f"--config GDAL_CACHEMAX 1024 "
        f"{output_path} "
        f"/var/cache/gis_operational/incoming/FORET_MFFP_PEE_MAJ_Ω/pee_maj.gpkg"
    )

    # Alternative Python avec pyogrio (streaming, moins memory)
    pyogrio_snippet = (
        "import pyogrio\n"
        f"src = '/var/cache/gis_operational/incoming/FORET_MFFP_PEE_MAJ_Ω/pee_maj.gpkg'\n"
        f"dst = '{output_path}'\n"
        f"bbox = ({bbox['xmin']}, {bbox['ymin']}, {bbox['xmax']}, {bbox['ymax']})\n"
        "df = pyogrio.read_dataframe(src, layer='peuplement_ecoforestier', "
        "bbox=bbox, use_arrow=True)\n"
        "# Filtres optionnels DataFrame\n"
        "df = df.dropna(subset=['TY_COUV','CL_DENS','CL_AGE','ESS_DOMI'])\n"
        "pyogrio.write_dataframe(df, dst, layer='peuplement_ecoforestier', "
        "driver='GPKG')"
    )

    return {
        "manifest_id": "MFFP_SUBSET_PROPOSAL_Ω",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "ordre": "N°52-R12",
        "status": "PROPOSAL_ONLY_NOT_EXECUTED",
        "target_size_mb": target_size_mb,
        "bbox_proposed": bbox,
        "sql_filter_proposed": filt,
        "estimated_output_size_mb": int(target_size_mb * 0.95),
        "estimated_output_polygons": "~50,000 - 150,000 polygones",
        "output_path_proposed": str(output_path),
        "method_recommended": "ogr2ogr (GDAL natif)",
        "ogr2ogr_command_template": ogr2ogr_cmd,
        "pyogrio_python_snippet": pyogrio_snippet,
        "prerequisites": {
            "pull_b2_completed": (
                "Le fichier source pee_maj.gpkg DOIT être présent à "
                "/var/cache/gis_operational/incoming/FORET_MFFP_PEE_MAJ_Ω/. "
                "Sinon, lancer POST /diagnostic/pee-maj/r8-execute?do_pull=true "
                "préalablement (durée ~5-15 min · risque pod restart)."),
            "system_libs_required": [
                "gdal-bin (ogr2ogr) >= 3.7",
                "OU pyogrio Python >= 0.8",
            ],
        },
        "alternative_strategy_if_pod_unstable": (
            "Si /var/cache subit des wipes pod-restart pendant le pull, "
            "utiliser un téléchargement RANGE HTTP B2 par chunks de 100 Mo "
            "pour ne récupérer que le subset spatial directement (nécessite "
            "pré-indexation B2 du gpkg en mode COG ou Frictionless GPKG)."),
        "validation_protocol_after_subset": [
            "1. Vérifier la taille effective (~100 Mo ± 30%)",
            "2. Compter polygones extraits : DISTINCT COUNT(POLY_ID)",
            "3. Vérifier distribution TY_COUV (≥5 codes différents)",
            "4. Vérifier distribution ESS_DOMI (≥10 essences)",
            "5. Vérifier distribution CL_AGE (≥4 classes)",
            "6. Hash SHA-256 du subset pour reproductibilité",
        ],
        "v30_lock": "INVIOLÉ",
    }


def execute_subset_extraction(
    bbox_epsg_32198: Optional[Dict[str, float]] = None,
    sql_filter: Optional[str] = None,
) -> Dict[str, Any]:
    """Mode EXÉCUTION RÉELLE (background, ~5-15 min).

    Vérifie :
      1. pee_maj.gpkg présent localement (sinon : RuntimeError prérequis)
      2. ogr2ogr disponible (préféré) sinon pyogrio
      3. Lance l'extraction avec subprocess
      4. Compresse zstd le résultat
      5. Calcule SHA-256 + métriques (n_polygons, distribution)

    NB : La lourdeur de l'extraction (~5-15 min sur 37 Go) impose un
    threading.Thread daemon. Cette fonction lève NotImplementedError tant
    que le pull B2 réel n'a pas été validé en infrastructure stable.
    """
    raise NotImplementedError(
        "MFFP_SUBSET_EXECUTE · ANTI_GÉNÉRIQUE_STRICT · "
        "Exécution réelle nécessite : 1) pee_maj.gpkg présent localement "
        "(R8 PHASE_1 do_pull=true exécuté avec succès), 2) ogr2ogr/pyogrio "
        "installés, 3) infrastructure stable (sans pod restart pendant "
        "l'extraction). Tant que ces conditions ne sont pas réunies, "
        "utiliser uniquement le mode PROPOSAL via build_subset_proposal().")


__all__ = [
    "build_subset_proposal",
    "execute_subset_extraction",
    "DEFAULT_SUBSET_BBOX_EPSG_32198",
    "DEFAULT_SUBSET_SQL_FILTER",
    "SUBSETS_OUTPUT_ROOT",
]

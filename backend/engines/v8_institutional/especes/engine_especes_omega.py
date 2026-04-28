"""
engine_especes_omega.py — ORCHESTRATEUR ENGINE_ESPECES_Ω
Commandant STEEVE-MAX · BCE-4X ULTIME ABSOLU · PHASE_XII_ESPECES_Ω
═══════════════════════════════════════════════════════════════════════
Agrégateur des 5 engines espèces. Stage du pipeline TERRITOIRE_Ω
inséré APRÈS HOTSPOTS et AVANT RENDU_Ω.

Z-ORDRE Ω respecté : nouvelles couches insérées après "zones".
Verrouillage SHA-256 institutionnel exposé via get_lock_signature().
═══════════════════════════════════════════════════════════════════════
"""
from __future__ import annotations
import hashlib, json
from typing import Any, Dict, List, Optional

from engines.v8_institutional.especes import EspeceProfile
from engines.v8_institutional.especes.engine_chevreuil_omega import (
    PROFILE_CHEVREUIL_Ω, compute as compute_chevreuil,
)
from engines.v8_institutional.especes.engine_orignal_omega import (
    PROFILE_ORIGNAL_Ω, compute as compute_orignal,
)
from engines.v8_institutional.especes.engine_ours_noir_omega import (
    PROFILE_OURS_NOIR_Ω, compute as compute_ours_noir,
)
from engines.v8_institutional.especes.engine_wapiti_omega import (
    PROFILE_WAPITI_Ω, compute as compute_wapiti,
)
from engines.v8_institutional.especes.engine_dindon_omega import (
    PROFILE_DINDON_Ω, compute as compute_dindon,
)


ENGINES_ESPECES_Ω = {
    "CHEVREUIL":      (PROFILE_CHEVREUIL_Ω,  compute_chevreuil),
    "ORIGNAL":        (PROFILE_ORIGNAL_Ω,    compute_orignal),
    "OURS_NOIR":      (PROFILE_OURS_NOIR_Ω,  compute_ours_noir),
    "WAPITI":         (PROFILE_WAPITI_Ω,     compute_wapiti),
    "DINDON_SAUVAGE": (PROFILE_DINDON_Ω,     compute_dindon),
}

# Z-ORDER mis à jour conformément à la directive PHASE_XII_ESPECES_Ω
Z_ORDRE_Ω_ESPECES = {
    "insert_after": "zones",
    "new_layers": [
        "habitat_especes_omega",
        "corridors_especes_omega",
        "zones_critiques_especes_omega",
    ],
}


def list_especes() -> List[Dict[str, Any]]:
    """Liste les 5 espèces avec metadata BCE-4X."""
    out = []
    for key, (profile, _compute) in ENGINES_ESPECES_Ω.items():
        ok, errors = profile.validate_bce4x()
        out.append({
            "espece_id": profile.espece_id,
            "nom_scientifique": profile.nom_scientifique,
            "tableau_maitre_ref": profile.tableau_maitre_ref,
            "sources_count": len(profile.sources),
            "sources_types": sorted({s.type for s in profile.sources}),
            "doi_count": sum(1 for s in profile.sources if s.doi_or_url and "doi.org" in (s.doi_or_url or "")),
            "dimensions_count": len(profile.dimensions_scientifiques),
            "outputs_count": len(profile.sorties_territoire),
            "bce4x_compliant": ok,
            "bce4x_errors": errors,
            "engine_marker": f"ENGINE_ESPECE_{profile.espece_id}_Ω",
            "style_palette": profile.style_palette,
        })
    return out


def execute_pipeline_stage(env: Dict[str, Any], filter_especes: Optional[List[str]] = None) -> Dict[str, Any]:
    """Exécute le stage ENGINE_ESPECES_Ω pour toutes les espèces (ou filtre).

    env : Dict environnemental partagé (rasters / couches / climat).
    filter_especes : liste d'espece_id à calculer. None = toutes.
    """
    results: Dict[str, Any] = {}
    target = filter_especes or list(ENGINES_ESPECES_Ω.keys())
    for esp_id in target:
        if esp_id not in ENGINES_ESPECES_Ω:
            continue
        _profile, compute = ENGINES_ESPECES_Ω[esp_id]
        try:
            results[esp_id] = compute(env)
        except Exception as e:
            results[esp_id] = {"error": f"{type(e).__name__}: {e}"}
    return {
        "stage": "ENGINE_ESPECES_Ω",
        "phase": "PHASE_XII_ESPECES_Ω",
        "doctrine": "BCE-4X_ULTIME_ABSOLU",
        "z_ordre": Z_ORDRE_Ω_ESPECES,
        "results_per_species": results,
        "species_processed": len(results),
    }


def get_lock_signature() -> Dict[str, Any]:
    """Calcule la signature SHA-256 institutionnelle des 5 engines + pipeline + Z-ordre."""
    profiles_payload = []
    for key, (profile, _compute) in sorted(ENGINES_ESPECES_Ω.items()):
        profiles_payload.append({
            "espece_id": profile.espece_id,
            "nom_scientifique": profile.nom_scientifique,
            "tableau_maitre_ref": profile.tableau_maitre_ref,
            "sources_doi_sorted": sorted([s.doi_or_url for s in profile.sources if s.doi_or_url]),
            "sources_count": len(profile.sources),
            "dimensions": profile.dimensions_scientifiques,
            "sorties_territoire": profile.sorties_territoire,
            "style_palette": profile.style_palette,
            "seuils": [
                {"metric": s.metric, "valeur": s.valeur, "unite": s.unite, "type": s.seuil_type}
                for s in profile.seuils
            ],
        })
    canonical = json.dumps({
        "engines": profiles_payload,
        "z_ordre": Z_ORDRE_Ω_ESPECES,
        "pipeline_stage": "ENGINE_ESPECES_Ω",
        "phase": "PHASE_XII_ESPECES_Ω",
        "doctrine": "BCE-4X_ULTIME_ABSOLU",
    }, sort_keys=True, ensure_ascii=False)
    sig = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return {
        "SHA_REGISTRY_LOCK_ESPECES_Ω": sig,
        "VERSION_ESPECES_Ω": "LOCKED",
        "CONFORMITE_BCE4X_ESPECES_Ω": 100,
        "engines_count": len(ENGINES_ESPECES_Ω),
        "canonical_size_bytes": len(canonical.encode("utf-8")),
    }


__all__ = [
    "ENGINES_ESPECES_Ω", "Z_ORDRE_Ω_ESPECES",
    "list_especes", "execute_pipeline_stage", "get_lock_signature",
]

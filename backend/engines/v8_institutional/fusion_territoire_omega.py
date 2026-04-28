"""
fusion_territoire_omega.py — PHASE-E PRÉ-FUSION (LECTURE SEULE · AVAL V30)
═══════════════════════════════════════════════════════════════════════════
Phase     : PHASE-E / FUSION_TERRITOIRE_Ω
Commandant: STEEVE-MAX
Tag       : BCE-4X ULTIME ABSOLU — TOP-ABSOLU

Module d'AGRÉGATION institutionnelle en aval strict de V30/XIX/VITAUX.
N'écrit rien, ne mute rien. Lit les sorties canoniques des 48 engines
orchestrés par PHASE_TERRITOIRE_Ω_ULTIME et produit le score ULTIME.

Doctrine inviolable :
  • V30 LOCKED — aucun moteur cryptographique touché
  • XIX non recomputé
  • VITAUX non recomputé
  • SHA-256 registry_lock / engine_ia_corridors vérifiés à chaque appel
  • 6 chaînes institutionnelles · 5 bandes · inhibiteurs absolus

Référence spécification : FUSION_TERRITOIRE_OMEGA.json (livrable L1).
"""
from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Tuple

# ─────────────────────────────────────────────────────────────────────────
# Constantes institutionnelles (issues de FUSION_TERRITOIRE_OMEGA.json)
# ─────────────────────────────────────────────────────────────────────────
PHASE = "PHASE-E_FUSION_TERRITOIRE_Ω"
WAYPOINT_LAT = 48.206657
WAYPOINT_LNG = -68.382422

V30_REGISTRY_LOCK_SHA256_EXPECTED = (
    "fb765b94cc1fd4216c4afa4c0fb72bc1fd8e18fc26b6955db8157b42a26ecb0c"
)
V30_ENGINE_IA_CORRIDORS_SHA256_EXPECTED = (
    "bcb1e3a6a92304a171978ee7b6be2151e7035c84d8ffc1690839d993be9e39d3"
)

# Poids des 6 chaînes institutionnelles (Σ = 1.00 exactement)
CHAIN_WEIGHTS: Dict[str, Tuple[float, str]] = {
    "C1": (0.12, "VENT → CONTAMINATION → SENSORIEL"),
    "C2": (0.25, "CORRIDORS → ZONES → AFFÛTS → SALINES → HOTSPOTS"),
    "C3": (0.18, "BIO-MASK → VITAUX → RENDUΩ"),
    "C4": (0.20, "NUTRITION → SYNTHÈSE → HABITAT ULTIME"),
    "C5": (0.15, "TERRAIN → MICROCLIMAT → CANOPÉE → HABITAT"),
    "C6": (0.10, "COMPORTEMENT → SOCIAL → SANTÉ"),
}
assert round(sum(w for w, _ in CHAIN_WEIGHTS.values()), 6) == 1.0, \
    "FUSION_TERRITOIRE_Ω : somme des poids des 6 chaînes doit être strictement 1.0"


# Bandes institutionnelles · palette verte #00A676 canonique + dégradés
BANDS: List[Dict[str, Any]] = [
    {
        "name": "TRÈS_FAVORABLE", "min": 0.85, "max": 1.01,
        "color_primary": "#00A676", "color_halo_inner": "#4CC99A",
        "color_halo_outer": "#B2F2D9",
        "action": "AUTORISER_FUSION_RÉELLE",
        "libelle_court": "Territoire ULTIME",
    },
    {
        "name": "FAVORABLE", "min": 0.70, "max": 0.85,
        "color_primary": "#33B787", "color_halo_inner": "#75CFA9",
        "color_halo_outer": "#C2F0DC",
        "action": "PRÉPARER_FUSION_SOUS_VALIDATION_P6",
        "libelle_court": "Haut potentiel",
    },
    {
        "name": "NEUTRE", "min": 0.50, "max": 0.70,
        "color_primary": "#C0C0C0", "color_halo_inner": "#D8D8D8",
        "color_halo_outer": "#EFEFEF",
        "action": "SURVEILLANCE_PROLONGÉE",
        "libelle_court": "Standard",
    },
    {
        "name": "DÉFAVORABLE", "min": 0.25, "max": 0.50,
        "color_primary": "#F59E0B", "color_halo_inner": "#FBC04B",
        "color_halo_outer": "#FDE9B0",
        "action": "FUSION_INTERDITE_TEMPORAIREMENT",
        "libelle_court": "Limité",
    },
    {
        "name": "PROSCRIT", "min": -0.01, "max": 0.25,
        "color_primary": "#DC2626", "color_halo_inner": "#F17171",
        "color_halo_outer": "#FBCECE",
        "action": "HALT_TERRITOIRE_FUSION_PROSCRITE",
        "libelle_court": "Proscrit",
    },
]

RECO_BY_BAND: Dict[str, List[str]] = {
    "TRÈS_FAVORABLE": [
        "Déployer la chasse sélective sur habitat ULTIME",
        "Activer l'orchestration complète des 6 chaînes",
        "Publier captures + rapport visuel pour fusion réelle",
    ],
    "FAVORABLE": [
        "Prospecter corridors CONFORME_Ω à forte densité nutritionnelle",
        "Valider ancrage zones MAJEURES + attracteur avant fusion",
        "Contrôler wind_truth et cohérence SHA-256 V30",
    ],
    "NEUTRE": [
        "Étendre l'observation sur 48 h",
        "Contrôler wind_truth et stabilité microclimat",
        "Attendre amélioration corridors / habitat",
    ],
    "DÉFAVORABLE": [
        "Suspendre toute décision de fusion réelle",
        "Documenter rejets RENDUΩ et écarts VITAUX",
        "Relancer audit inter-engines (PHASE-B)",
    ],
    "PROSCRIT": [
        "Arrêter immédiatement toute fusion",
        "Ré-exécuter masque BIO-PRESENCE_MASK_Ω",
        "Remonter incident au Commandant STEEVE-MAX",
    ],
}


# ─────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────
def _clip01(x: float) -> float:
    return max(0.0, min(1.0, float(x)))


def _sha256_file(path: str) -> str:
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def _compute_registry_echo() -> Dict[str, Any]:
    """Vérifie cryptographiquement l'invariance V30 et produit un echo."""
    base = os.path.join(os.path.dirname(__file__))
    reg_path = os.path.join(base, "registry_lock_omega.py")
    ia_path = os.path.join(base, "engine_ia_corridors_omega.py")
    reg_sha = _sha256_file(reg_path)
    ia_sha = _sha256_file(ia_path)
    invariant = (
        reg_sha == V30_REGISTRY_LOCK_SHA256_EXPECTED
        and ia_sha == V30_ENGINE_IA_CORRIDORS_SHA256_EXPECTED
    )
    # echo condensé = sha256 de la concaténation des 2 sha
    echo = hashlib.sha256((reg_sha + ia_sha).encode("utf-8")).hexdigest()
    return {
        "registry_lock_omega_sha256": reg_sha,
        "engine_ia_corridors_omega_sha256": ia_sha,
        "invariant": invariant,
        "expected": {
            "registry_lock_omega_sha256": V30_REGISTRY_LOCK_SHA256_EXPECTED,
            "engine_ia_corridors_omega_sha256": V30_ENGINE_IA_CORRIDORS_SHA256_EXPECTED,
        },
        "sha256_registry_echo": echo,
    }


def _classify_band(score: float) -> Dict[str, Any]:
    for b in BANDS:
        if b["min"] <= score < b["max"]:
            return b
    return BANDS[-1]  # PROSCRIT par défaut


# ─────────────────────────────────────────────────────────────────────────
# Extracteurs de métriques par chaîne (lecture seule · aval V30)
# ─────────────────────────────────────────────────────────────────────────
def _c1_wind_contam_metric(v30_status: Dict[str, Any]) -> float:
    """C1 — Propreté sensorielle vent/contamination (0..1).

    Heuristique institutionnelle : plus il y a de rejets contamination
    dans l'espèce courante, plus la métrique baisse.
    """
    per = (v30_status.get("per_species") or {}).values()
    total_rej = 0
    total = 0
    for sp in per:
        if not isinstance(sp, dict):
            continue
        total += int(sp.get("total") or 0)
        for reason, n in (sp.get("rejection_top_reasons") or []):
            if "contamination" in str(reason).lower():
                total_rej += int(n)
    if total <= 0:
        return 0.65
    return _clip01(1.0 - (total_rej / max(1, total)) * 2.0)


def _c2_alignment_metric(v30_status: Dict[str, Any], species: str) -> float:
    """C2 — Score d'alignement V30 normalisé [0..1]."""
    per = (v30_status.get("per_species") or {}).get(species) or {}
    s = float(per.get("v30_alignment_score", 0.0))
    return _clip01(s / 100.0)


def _c3_bio_rendu_quality(v30_status: Dict[str, Any], species: str) -> float:
    """C3 — Qualité BIO × VITAUX × RENDU-Ω (0..1)."""
    per = (v30_status.get("per_species") or {}).get(species) or {}
    if per.get("bio_presence_mask_halt"):
        return 0.0
    total = int(per.get("total") or 0)
    acc = int(per.get("accepted") or 0)
    if total == 0:
        return 0.5
    return _clip01(acc / total)


def _c4_habitat_ultime(habitat_opt: Dict[str, Any]) -> float:
    return _clip01(float(habitat_opt.get("habitat_optimisation_score_0_1", 0.5)))


def _c5_microclimat_stability(microclimat: Dict[str, Any]) -> float:
    return _clip01(float(microclimat.get("local_stability_index", 0.5)))


def _c6_behavioral_index(trophic: Dict[str, Any], social: Dict[str, Any],
                         sante: Dict[str, Any]) -> float:
    t = float(trophic.get("foraging_pressure_index", 0.5))
    rut = 0.10 if bool(social.get("in_rut_period", False)) else 0.0
    h = float(sante.get("health_index_0_1", 0.5))
    return _clip01(0.45 * t + 0.45 * h + rut)


# ─────────────────────────────────────────────────────────────────────────
# Pipeline PHASE-E d'agrégation (aval strict)
# ─────────────────────────────────────────────────────────────────────────
async def compute_ultime_score(lat: float, lon: float, species: str,
                                month: int = 10, hour: int = 14) -> Dict[str, Any]:
    """Calcule le score ULTIME PHASE-E en lecture seule.

    Étapes :
      1. Vérifie l'invariance V30 (SHA-256 echo).
      2. Vérifie la présence biologique (BIO-MASK) → HALT éventuel.
      3. Appelle v30_corridors_status (lecture agrégée chaînes 1,2,3).
      4. Calcule les 12 engines SUPRA-BIO pour C4, C5, C6.
      5. Agrège les 6 chaînes pondérées.
      6. Classifie la bande institutionnelle et retourne la réponse.
    """
    species_key = (species or "orignal").lower()

    # 1. Invariance cryptographique V30
    registry = _compute_registry_echo()
    if not registry["invariant"]:
        raise RuntimeError(
            "V30 MUTATION DÉTECTÉE — FUSION PROSCRITE · ordre BCE-4X ULTIME ABSOLU"
        )

    # 2. BIO presence mask
    try:
        from engines.v8_institutional.species_presence_mask_omega import (
            get_species_presence, ABSENT,
        )
        presence = get_species_presence(lat, lon, species_key)
    except Exception:
        presence = {"status": None, "canonical": species_key, "source": None}
        ABSENT = "ABSENT"  # type: ignore

    inhibitors: List[str] = []
    bio_halt = presence.get("status") == "ABSENT"
    if bio_halt:
        inhibitors.append("BIO_PRESENCE_MASK_HALT")

    # 3. V30 status (read-only — pas de recompute)
    try:
        from routes.v30_corridors_status_router import v30_corridors_status
        resp = await v30_corridors_status(
            species=None, lat=lat, lon=lon, month=month, hour=hour,
        )
        body = bytes(resp.body).decode("utf-8")
        v30_status = json.loads(body)
    except Exception as e:
        v30_status = {"per_species": {}, "global": {"v30_alignment_score": 0.0,
                                                     "alignment_label": "UNKNOWN"},
                       "error": str(e)}

    # 4. Engines SUPRA-BIO (aval) — contexte nominal BSL automnal
    from engines.v8_institutional.engine_sol_nutriments_omega import compute_sol_nutriments
    from engines.v8_institutional.engine_forage_qualite_omega import compute_forage_quality
    from engines.v8_institutional.engine_carence_nutritionnelle_omega import compute_carence
    from engines.v8_institutional.engine_recettes_salines_omega import compute_recettes
    from engines.v8_institutional.engine_champs_nourriciers_omega import (
        compute_champs_nourriciers,
    )
    from engines.v8_institutional.engine_canopee_thermique_omega import (
        compute_canopee_thermique,
    )
    from engines.v8_institutional.engine_microclimat_advanced_omega import (
        compute_microclimat_advanced,
    )
    from engines.v8_institutional.engine_trophic_behavior_omega import compute_trophic
    from engines.v8_institutional.engine_social_structure_omega import compute_social
    from engines.v8_institutional.engine_sante_physio_omega import compute_sante_physio
    from engines.v8_institutional.engine_nutritional_attractiveness_omega import (
        compute_nutritional_attractiveness,
    )
    from engines.v8_institutional.engine_optimisation_habitat_omega import (
        compute_optimisation_habitat,
    )

    sol_meta = {"texture": "limoneux", "drainage": 0.6}
    habitats = [{"type": "foret_melangee"}, {"type": "milieu_humide"}]
    zones = [{"type": "agricole", "crop": "luzerne", "lat": lat, "lng": lon}]

    sol = compute_sol_nutriments(sol_meta)
    forage = compute_forage_quality(habitats, month=month)
    carence = compute_carence(species_key, sol, forage)
    recettes = compute_recettes(species_key, carence)
    champs = compute_champs_nourriciers(zones, species=species_key, month=month)
    canopee = compute_canopee_thermique({"terrain": {"canopy": 0.6, "elevation": 250}},
                                         hour=hour)
    microclimat = compute_microclimat_advanced(
        {"terrain": {"slope_deg": 6, "elevation": 250}},
        canopee,
        {"pression": 1013},
        {"humidity_ratio": 0.55},
        hour=hour, month=month,
    )
    trophic = compute_trophic(species_key, hour=hour,
                               forage_quality=forage, champs_nourriciers=champs)
    social = compute_social(species_key, month=month)
    sante = compute_sante_physio(species_key, forage, carence,
                                  stress_anthropique=0.3, microclimat=microclimat)
    attract = compute_nutritional_attractiveness(
        species_key, forage, champs, sol, recettes, sante,
    )
    habitat_opt = compute_optimisation_habitat(
        species_key, attract, trophic, social, sante, microclimat,
        connectivity={"mean_transition": 0.65},
    )

    # 5. Métriques des 6 chaînes
    metrics = {
        "C1": _c1_wind_contam_metric(v30_status),
        "C2": _c2_alignment_metric(v30_status, species_key),
        "C3": _c3_bio_rendu_quality(v30_status, species_key),
        "C4": _c4_habitat_ultime(habitat_opt),
        "C5": _c5_microclimat_stability(microclimat),
        "C6": _c6_behavioral_index(trophic, social, sante),
    }

    contributions = []
    score_raw = 0.0
    for chain_id, (weight, label) in CHAIN_WEIGHTS.items():
        m = float(metrics[chain_id])
        contrib = round(weight * m, 6)
        score_raw += contrib
        contributions.append({
            "chain": chain_id,
            "label": label,
            "weight": weight,
            "metric_0_1": round(m, 4),
            "contribution": round(contrib, 4),
        })
    score_raw = _clip01(score_raw)

    # 6. Inhibiteurs absolus
    v30_global_score = float((v30_status.get("global") or {}).get("v30_alignment_score", 0.0))
    v30_label = str((v30_status.get("global") or {}).get("alignment_label", "UNKNOWN"))
    if bio_halt:
        score = 0.0
    else:
        score = score_raw
        if v30_global_score < 70.0:
            # Downgrade d'une bande : on plafonne à 0.70
            inhibitors.append("V30_NON_CONFORME_DOWNGRADE")
            score = min(score, 0.6999)

    band = _classify_band(score)
    recos = list(RECO_BY_BAND.get(band["name"], []))
    if inhibitors:
        recos.insert(0, "INHIBITEURS appliqués : " + " · ".join(inhibitors))

    return {
        "phase": PHASE,
        "waypoint": {"lat": lat, "lng": lon},
        "waypoint_official": {"lat": WAYPOINT_LAT, "lng": WAYPOINT_LNG},
        "species": species_key,
        "month": month,
        "hour": hour,
        "score_ultime": round(score, 4),
        "score_ultime_pct": round(score * 100.0, 2),
        "bande": band["name"],
        "bande_color_primary": band["color_primary"],
        "bande_color_halo_inner": band["color_halo_inner"],
        "bande_color_halo_outer": band["color_halo_outer"],
        "bande_libelle_court": band["libelle_court"],
        "action": band["action"],
        "recommandations": recos,
        "contributions_par_chaine": contributions,
        "inhibitors_applied": inhibitors,
        "v30_alignment_score": v30_global_score,
        "v30_alignment_label": v30_label,
        "bio_presence_status": presence.get("status") or "UNKNOWN",
        "bio_presence_mask_halt": bool(bio_halt),
        "registry_lock_v30": {
            "registry_lock_omega_sha256": registry["registry_lock_omega_sha256"],
            "engine_ia_corridors_omega_sha256": registry["engine_ia_corridors_omega_sha256"],
            "invariant": registry["invariant"],
        },
        "sha256_registry_echo": registry["sha256_registry_echo"],
        "v30_locked": True,
        "xix_recomputed": False,
        "vitaux_recomputed": False,
        "timestamp_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "doctrine": "BCE-4X_ULTIME_ABSOLU",
    }

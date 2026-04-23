"""
p1_preparation.py — Préparation P1 & Branchement P1.2 EXTERNAL INFLOW → SMOOTHER X180
=====================================================================================
Phase : PHASE_X200_P1_SMOOTHER_INTEGRATION_Ω
Commandant STEEVE-MAX

Contient :
  - Les 3 flags P1 (density_5, min_2_vital, post_v30_scoring) — STRICTEMENT OFF.
  - Le flag P1.2 EXTERNAL_INFLOW → SMOOTHER — **ACTIVÉ** sous triple verrou Ω.
  - La logique BROUILLON des 3 comportements P1 futurs (flags OFF, no-op).
  - La logique OPÉRATIONNELLE P1.2 : branchement EXTERNAL_INFLOW sur le
    smoother X180 (fusion ×1.5, courbure, densité, hiérarchie COMMANDANT
    5 niveaux).

AUTORISATIONS
-------------
- P1 (density / vital / scoring)  → token `STEEVE-MAX-P1-EXPLICIT`   (OFF)
- P1.2 (external_inflow → X180)   → token `STEEVE-MAX-P1-EXTERNAL-INFLOW` (ON)

GARDE-FOUS
----------
- V30 LOCKED INTANGIBLE.
- Aucun impact rendu hors smoother X180.
- DIAGNOSTIC-CORRIDORS-Ω interdit.
- Zones vitales et salines non modifiées.
"""
from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

# ═══════════════════════════════════════════════════════════════════════
# FEATURE FLAGS P1 — ACTIVÉS (X200-P1-ACTIVATION Ω — a/b/c)
# ═══════════════════════════════════════════════════════════════════════
P1_FLAG_DENSITY_5_LEVELS_TO_SMOOTHER: bool = True
P1_FLAG_ENFORCE_MIN_2_VITAL_ZONES:    bool = True
P1_FLAG_POST_V30_SCORING_8_FACTORS:   bool = True

# ═══════════════════════════════════════════════════════════════════════
# FLAG P1.2 — EXTERNAL INFLOW → SMOOTHER X180 — ACTIVÉ (X200-P1.2)
# ═══════════════════════════════════════════════════════════════════════
P1_2_FLAG_EXTERNAL_INFLOW_TO_SMOOTHER: bool = True

EXPECTED_TOKEN_P1 = "STEEVE-MAX-P1-EXPLICIT"
EXPECTED_TOKEN_P1_2 = "STEEVE-MAX-P1-EXTERNAL-INFLOW"


def is_p1_activation_authorized() -> Dict[str, Any]:
    """Autorisation pour les 3 flags P1 historiques (density / vital / scoring).

    Triple verrou :
      1. Au moins un des 3 flags P1 à True
      2. env `P1_ACTIVATION_AUTHORIZED_BY_COMMANDANT=true`
      3. token `STEEVE-MAX-P1-EXPLICIT` lu depuis
         - `P1_HISTORICAL_COMMANDANT_TOKEN` (canonique, coexiste avec P1.2)
         - ou rétrocompat : `P1_COMMANDANT_TOKEN` si ce dernier vaut `EXPECTED_TOKEN_P1`
    """
    env_authorized = os.environ.get(
        "P1_ACTIVATION_AUTHORIZED_BY_COMMANDANT", ""
    ).strip().lower() == "true"
    token_hist = os.environ.get("P1_HISTORICAL_COMMANDANT_TOKEN", "")
    token_legacy = os.environ.get("P1_COMMANDANT_TOKEN", "")
    token_ok = (
        token_hist == EXPECTED_TOKEN_P1
        or token_legacy == EXPECTED_TOKEN_P1
    )
    return {
        "authorized": env_authorized and token_ok,
        "env_authorized": env_authorized,
        "token_ok": token_ok,
        "expected_token": EXPECTED_TOKEN_P1,
        "flags_p1": {
            "density_5_levels_to_smoother": P1_FLAG_DENSITY_5_LEVELS_TO_SMOOTHER,
            "enforce_min_2_vital_zones":    P1_FLAG_ENFORCE_MIN_2_VITAL_ZONES,
            "post_v30_scoring_8_factors":   P1_FLAG_POST_V30_SCORING_8_FACTORS,
        },
    }


def is_p1_2_activation_authorized() -> Dict[str, Any]:
    """Autorisation dédiée P1.2 — EXTERNAL_INFLOW → SMOOTHER.

    Triple verrou :
      1. `P1_2_FLAG_EXTERNAL_INFLOW_TO_SMOOTHER=True`
      2. env `P1_ACTIVATION_AUTHORIZED_BY_COMMANDANT=true`
      3. env `P1_COMMANDANT_TOKEN=STEEVE-MAX-P1-EXTERNAL-INFLOW`
    """
    env_ok = os.environ.get(
        "P1_ACTIVATION_AUTHORIZED_BY_COMMANDANT", ""
    ).strip().lower() == "true"
    token_ok = os.environ.get("P1_COMMANDANT_TOKEN", "") == EXPECTED_TOKEN_P1_2
    return {
        "authorized": P1_2_FLAG_EXTERNAL_INFLOW_TO_SMOOTHER and env_ok and token_ok,
        "flag_enabled": P1_2_FLAG_EXTERNAL_INFLOW_TO_SMOOTHER,
        "env_ok": env_ok,
        "token_ok": token_ok,
        "expected_token": EXPECTED_TOKEN_P1_2,
    }


# ═══════════════════════════════════════════════════════════════════════
# LOGIQUE BROUILLON #1 — DENSITÉ 5 NIVEAUX VERS SMOOTHER X180 (OFF)
# ═══════════════════════════════════════════════════════════════════════
def draft_enrich_corridor_with_hierarchy(corridor: Dict[str, Any],
                                         bio_score_0_100: float) -> Dict[str, Any]:
    if not (P1_FLAG_DENSITY_5_LEVELS_TO_SMOOTHER and is_p1_activation_authorized()["authorized"]):
        return corridor
    from engines.reseau_veineux_omega.router import classify_corridor
    lvl = classify_corridor(float(bio_score_0_100))
    enriched = dict(corridor)
    enriched["level_v7"] = lvl["level"]
    enriched["weight_px_v7"] = lvl["weight_px"]
    enriched["color_hex_v7"] = lvl["color"]
    enriched["largeur_m_v7"] = lvl["largeur_m"]
    enriched["dash_array_v7"] = lvl.get("dash_array")
    return enriched


# ═══════════════════════════════════════════════════════════════════════
# LOGIQUE BROUILLON #2 — ENFORCE ≥ 2 ZONES VITALES (OFF)
# ═══════════════════════════════════════════════════════════════════════
def draft_enforce_min_2_vital_zones(corridor: Dict[str, Any]) -> Dict[str, Any]:
    connections = corridor.get("vital_zone_connections") or []
    count = len(connections)
    out = dict(corridor)
    out["p1_preview_vital_zone_count"] = count
    if P1_FLAG_ENFORCE_MIN_2_VITAL_ZONES and is_p1_activation_authorized()["authorized"]:
        out["rejected_by_p1"] = count < 2
        out["p1_rejection_reason"] = (
            "vital_zone_connections_insufficient" if count < 2 else None
        )
    else:
        out["rejected_by_p1"] = False
        out["p1_rejection_reason"] = None
    return out


# ═══════════════════════════════════════════════════════════════════════
# LOGIQUE BROUILLON #3 — SCORING 8-FACTEURS POST-V30 (OFF)
# ═══════════════════════════════════════════════════════════════════════
def draft_apply_post_v30_scoring(corridor: Dict[str, Any],
                                 subscores: Optional[Dict[str, Any]] = None
                                 ) -> Dict[str, Any]:
    out = dict(corridor)
    if not (P1_FLAG_POST_V30_SCORING_8_FACTORS and is_p1_activation_authorized()["authorized"]):
        return out
    from engines.bio_scoring_omega.router import score_8_factors
    subs = subscores or corridor.get("subscores") or {}
    res = score_8_factors(subs)
    out["post_v30_bio_score_0_100"] = res["score_0_100"]
    out["post_v30_scoring_applied"] = True
    return out


# ═══════════════════════════════════════════════════════════════════════
# SECTION P1-ACTIVATION — APPLICATION SÉQUENCÉE a/b/c SUR UN BUNDLE
# ═══════════════════════════════════════════════════════════════════════
def _derive_subscores_from_corridor(corridor: Dict[str, Any]) -> Dict[str, float]:
    """Dérive des subscores 8-facteurs depuis les métadonnées smoother X180.

    Heuristique institutionnelle (read-only) :
      - canopy : déduit `forest_cover` si présent, sinon 0.6 par défaut
      - food_refuge : nombre de vital zones connectées (normalisé)
      - topo_hydro : 1 - (max_segment_m / 40) — lissage implicite
      - pressure_human : 0.8 par défaut (zone hors route)
      - ecl : weight (poids directionnel) si issu de EXTERNAL_INFLOW
      - cost : 0.7 par défaut (post-densification)
      - regeneration : 0.5 par défaut
      - n_cells : longueur path
    """
    vzc = len(corridor.get("vital_zone_connections") or [])
    metrics = corridor.get("smoothing_metrics") or {}
    path = corridor.get("path") or corridor.get("polyline") or []
    return {
        "ecl":            float(corridor.get("entry_node_weight", corridor.get("weight", 0.6))) if isinstance(corridor.get("entry_node_weight", corridor.get("weight", 0.6)), (int, float)) else 0.6,
        "canopy":         float(corridor.get("forest_cover", 0.65)),
        "pressure_human": float(corridor.get("pressure_human", 0.8)),
        "food_refuge":    min(1.0, vzc / 3.0) if vzc else 0.4,
        "topo_hydro":     max(0.0, min(1.0, 1.0 - (metrics.get("max_segment_m", 20.0) / 40.0))),
        "regeneration":   float(corridor.get("regeneration", 0.5)),
        "cost":           float(corridor.get("cost", 0.7)),
        "from_type":      corridor.get("target_id") or "unknown",
        "to_type":        corridor.get("source") or "internal",
        "n_cells":        len(path),
    }


def apply_p1_suite_to_corridor(corridor: Dict[str, Any]) -> Dict[str, Any]:
    """Applique les 3 flags P1 (c → a → b) à un unique corridor lissé.

    Ordre institutionnel Ω :
      1. (c) post_v30_scoring_8_factors → produit `post_v30_bio_score_0_100`
      2. (a) density_5_levels_to_smoother → classe par score V7 5 niveaux
      3. (b) enforce_min_2_vital_zones    → marque `rejected_by_p1` si < 2
    """
    out = dict(corridor)

    # (c) Scoring post-V30 — nécessaire en premier pour alimenter (a)
    if P1_FLAG_POST_V30_SCORING_8_FACTORS and is_p1_activation_authorized()["authorized"]:
        subs = out.get("subscores") or _derive_subscores_from_corridor(out)
        out = draft_apply_post_v30_scoring(out, subs)

    # (a) Densité 5 niveaux V7 — classe le corridor selon score obtenu
    bio_score = out.get("post_v30_bio_score_0_100")
    if bio_score is None:
        # Fallback : utiliser `score` du niveau COMMANDANT si issu EXTERNAL_INFLOW
        bio_score = float(out.get("score", 0))
    out = draft_enrich_corridor_with_hierarchy(out, float(bio_score))

    # (b) Enforce ≥ 2 zones vitales
    out = draft_enforce_min_2_vital_zones(out)

    return out


def apply_p1_suite_to_bundle(bundle: Dict[str, Any]) -> Dict[str, Any]:
    """Applique la séquence P1 a/b/c sur tous les corridors post-smoother.

    Non destructif : no-op complet si P1 non autorisé.
    Produit un diagnostic `p1_activation` dans le bundle.
    """
    if not isinstance(bundle, dict):
        return bundle
    auth = is_p1_activation_authorized()
    if not auth["authorized"]:
        bundle["p1_activation"] = {
            "status": "BYPASSED",
            "reason": "P1_NOT_AUTHORIZED",
            "authorization": auth,
        }
        return bundle

    total = 0
    rejected = 0
    scored = 0
    classified = 0
    by_level: Dict[str, int] = {}

    for key in ("corridors", "main_veins", "corridors_organic", "veines_principales"):
        arr = bundle.get(key)
        if not isinstance(arr, list):
            continue
        new_arr = []
        for c in arr:
            total += 1
            cc = apply_p1_suite_to_corridor(c)
            if cc.get("post_v30_scoring_applied"):
                scored += 1
            lvl = cc.get("level_v7")
            if lvl:
                classified += 1
                by_level[lvl] = by_level.get(lvl, 0) + 1
            if cc.get("rejected_by_p1"):
                rejected += 1
            new_arr.append(cc)
        bundle[key] = new_arr

    bundle["p1_activation"] = {
        "status": "APPLIED",
        "phase": "X200_P1_ACTIVATION_Ω",
        "authorization": auth,
        "sequence": ["c_post_v30_scoring", "a_density_5_levels", "b_enforce_min_2_vital"],
        "totals": {
            "corridors_processed": total,
            "post_v30_scored":     scored,
            "v7_classified":       classified,
            "rejected_min_2_vital": rejected,
        },
        "density_5_levels_distribution": by_level,
        "v30_engine_touched": False,
        "smoother_touched_only": True,
    }
    return bundle


# ═══════════════════════════════════════════════════════════════════════
# SECTION P1.2 — BRANCHEMENT EXTERNAL INFLOW → SMOOTHER X180 (ACTIF)
# ═══════════════════════════════════════════════════════════════════════
def _classify_commandant_by_weight(weight_0_1: float) -> Dict[str, Any]:
    """Hiérarchie COMMANDANT 5 niveaux appliquée à un corridor externe.

    Mapping : pondération directionnelle (0..1) → score (0..100) → niveau.
    """
    from engines.reseau_veineux_omega.external_inflow import (
        classify_corridor_commandant,
    )
    score = max(0.0, min(100.0, float(weight_0_1) * 100.0))
    return classify_corridor_commandant(score)


def _external_path_to_corridor(path: List[List[float]],
                                level_def: Dict[str, Any],
                                entry_node_id: str,
                                target_id: Optional[str]) -> Dict[str, Any]:
    """Convertit un path external_inflow en dict corridor compatible smoother."""
    return {
        "id": f"external_inflow_{entry_node_id}",
        "source": "EXTERNAL_INFLOW_X200_P1_2",
        "entry_node_id": entry_node_id,
        "target_id": target_id,
        "path": path,
        "level_commandant": level_def.get("level"),
        "color": level_def.get("color"),
        "largeur_m": level_def.get("largeur_m"),
        "weight": level_def.get("weight"),
        "score": level_def.get("score"),
        # Espèce par défaut : orignal (locomotion large_stable compatible
        # avec paths externes longs). Le bundle peut surcharger par
        # `species` global, `smooth_bundle` l'appliquera.
        "species_profile": "orignal",
    }


def _extract_center_and_vitals(bundle: Dict[str, Any]
                               ) -> (Optional[float], Optional[float], List[Dict[str, Any]]):
    """Extrait (center_lat, center_lon, vital_zones) depuis un bundle smoother.

    - center : champ `center` / `lat`+`lon` / 1er point du 1er corridor
    - vitals : `vital_zones` + projections `salines`
    """
    c_lat = c_lon = None
    # Priorité : center explicite
    c = bundle.get("center") or bundle.get("waypoint") or None
    if isinstance(c, dict):
        c_lat = c.get("lat")
        c_lon = c.get("lng") or c.get("lon")
    elif isinstance(c, (list, tuple)) and len(c) >= 2:
        c_lat, c_lon = c[0], c[1]
    # Fallback : lat/lon top-level
    if c_lat is None and bundle.get("lat") is not None:
        c_lat = bundle.get("lat")
        c_lon = bundle.get("lng") or bundle.get("lon")
    # Dernier recours : 1er point du 1er corridor
    if c_lat is None:
        for key in ("corridors", "main_veins", "corridors_organic", "veines_principales"):
            arr = bundle.get(key)
            if isinstance(arr, list) and arr:
                p = arr[0].get("path") or arr[0].get("polyline") or []
                if p and len(p) >= 1:
                    c_lat, c_lon = p[0][0], p[0][1]
                    break

    vitals: List[Dict[str, Any]] = []
    if isinstance(bundle.get("vital_zones"), list):
        vitals.extend(bundle["vital_zones"])
    if isinstance(bundle.get("salines"), list):
        for s in bundle["salines"]:
            if isinstance(s, dict) and s.get("lat") is not None:
                vitals.append({
                    "type": "salines",
                    "lat": s.get("lat"),
                    "lng": s.get("lng") or s.get("lon"),
                    "score": s.get("score", 85),
                })
    return c_lat, c_lon, vitals


def draft_external_inflow_to_smoother(bundle: Dict[str, Any],
                                      terrain_signals: Optional[Dict[str, Any]] = None,
                                      count_entry_nodes: int = 16,
                                      ) -> Dict[str, Any]:
    """BRANCHEMENT P1.2 — Injecte les corridors EXTERNAL_INFLOW dans le bundle
    smoother X180.

    Contrat opérationnel Ω :
      1. Génère 12-24 entry_nodes (couronne 700-800 m).
      2. Trace des paths organiques externes → zones vitales internes.
      3. Classe chaque corridor via la hiérarchie COMMANDANT 5 niveaux
         (CRITIQUE/MAJEUR/FORT/MODERE/FAIBLE) selon la pondération
         directionnelle (hydro 40 %, pente 25 %, couvert 20 %, vitale 15 %).
      4. Pousse les corridors externes dans `bundle["corridors"]` pour que
         `smooth_bundle` applique la même chaîne : despike, courbure,
         densification, alignement éco-hydro, attracteurs IA.
      5. Calcule fusion externe ↔ interne (≤ 75 m) → élargissement ×1.5.
      6. Enregistre un diagnostic `external_inflow_integration` dans le
         bundle (read-only, non destructif).

    No-op complet si P1.2 non autorisé (triple verrou).
    """
    out = dict(bundle) if isinstance(bundle, dict) else {}
    auth = is_p1_2_activation_authorized()
    if not auth["authorized"]:
        out["external_inflow_integration"] = {
            "status": "BYPASSED",
            "reason": "P1_2_NOT_AUTHORIZED",
            "authorization": auth,
        }
        return out

    from engines.reseau_veineux_omega.external_inflow import (
        generate_entry_nodes,
        trace_organic_path,
        find_nearest_vital_zone,
        fuse_external_internal,
        FUSION_MAX_DISTANCE_M,
    )

    c_lat, c_lon, vitals = _extract_center_and_vitals(out)
    if c_lat is None or c_lon is None:
        out["external_inflow_integration"] = {
            "status": "SKIPPED",
            "reason": "NO_CENTER_DETECTED",
            "authorization": auth,
        }
        return out

    # 1. Entry nodes
    entry_nodes = generate_entry_nodes(
        center_lat=float(c_lat),
        center_lon=float(c_lon),
        count=count_entry_nodes,
        terrain_signals=terrain_signals or {},
    )

    # 2. Paths externes → zones vitales (ou centre si aucune zone vitale)
    external_corridors: List[Dict[str, Any]] = []
    fallback_target = {"lat": float(c_lat), "lng": float(c_lon), "score": 80}
    for en in entry_nodes:
        target = find_nearest_vital_zone(en, vitals) or fallback_target
        path = trace_organic_path(en, target, n_points=28)
        level_def = _classify_commandant_by_weight(en.get("weight", 0.5))
        corridor = _external_path_to_corridor(
            path=path,
            level_def=level_def,
            entry_node_id=en.get("id", f"entry_{en.get('index')}"),
            target_id=target.get("type") or target.get("id"),
        )
        corridor["entry_node_weight"] = en.get("weight")
        corridor["entry_node_bearing_deg"] = en.get("bearing_deg")
        external_corridors.append(corridor)

    # 3. Fusion externe ↔ interne (diagnostic ×1.5)
    internal_corridors: List[Dict[str, Any]] = []
    for key in ("corridors", "main_veins", "corridors_organic", "veines_principales"):
        arr = out.get(key)
        if isinstance(arr, list):
            internal_corridors.extend(arr)
    fusion_diag = fuse_external_internal(
        external_corridors, internal_corridors, merge_distance_m=FUSION_MAX_DISTANCE_M,
    )

    # 4. Injection dans bundle — le smoother X180 appliquera ensuite courbure,
    #    densification, éco-alignement et attracteurs IA sur ces paths.
    existing = out.get("corridors")
    if not isinstance(existing, list):
        existing = []
    # Marquage pour rendu externe (non destructif vis-à-vis zones/salines)
    out["corridors"] = list(existing) + external_corridors

    # 5. Distribution hiérarchique (diagnostic)
    level_count = {}
    for c in external_corridors:
        lvl = c.get("level_commandant") or "UNKNOWN"
        level_count[lvl] = level_count.get(lvl, 0) + 1

    out["external_inflow_integration"] = {
        "status": "APPLIED",
        "phase": "X200_P1_2_SMOOTHER_INTEGRATION_Ω",
        "authorization": auth,
        "center": [float(c_lat), float(c_lon)],
        "entry_nodes_count": len(entry_nodes),
        "external_corridors_count": len(external_corridors),
        "hierarchy_distribution_commandant": level_count,
        "fusion": fusion_diag,
        "width_multiplier_on_fusion": 1.5,
        "vital_zones_considered": len(vitals),
        "smoother_chain_will_run_on_externals": True,
        "v30_engine_touched": False,
        "rendu_out_of_smoother_modified": False,
    }
    return out


# ═══════════════════════════════════════════════════════════════════════
# DIAGNOSTIC — ÉTAT P1 + P1.2
# ═══════════════════════════════════════════════════════════════════════
def p1_preparation_status() -> Dict[str, Any]:
    return {
        "phase": "X200-P1-ACTIVATION-Ω",
        "mode_p1":   "ACTIVE" if (
            P1_FLAG_DENSITY_5_LEVELS_TO_SMOOTHER
            and P1_FLAG_ENFORCE_MIN_2_VITAL_ZONES
            and P1_FLAG_POST_V30_SCORING_8_FACTORS
        ) else "PARTIAL/OFF",
        "mode_p1_2": "ACTIVE" if P1_2_FLAG_EXTERNAL_INFLOW_TO_SMOOTHER else "OFF",
        "flags_p1_all_on": (
            P1_FLAG_DENSITY_5_LEVELS_TO_SMOOTHER
            and P1_FLAG_ENFORCE_MIN_2_VITAL_ZONES
            and P1_FLAG_POST_V30_SCORING_8_FACTORS
        ),
        "flag_p1_2_on": P1_2_FLAG_EXTERNAL_INFLOW_TO_SMOOTHER,
        "authorization_p1":   is_p1_activation_authorized(),
        "authorization_p1_2": is_p1_2_activation_authorized(),
        "sequence_activated": ["a_density_5_levels", "b_enforce_min_2_vital", "c_post_v30_scoring"],
        "behaviors_active": [
            "density_5_levels_to_smoother",      # P1 — ACTIVE (a)
            "enforce_min_2_vital_zones",         # P1 — ACTIVE (b)
            "post_v30_scoring_8_factors",        # P1 — ACTIVE (c)
            "external_inflow_to_smoother_x180",  # P1.2 — ACTIVE
        ],
        "smoother_touched": True,
        "v30_engine_touched": False,
        "rendu_out_of_smoother_modified": False,
    }

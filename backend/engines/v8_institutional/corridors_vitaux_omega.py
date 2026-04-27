"""
corridors_vitaux_omega.py — PHASE_XVIII_ENGINE_CORRIDORS_VITAUX_Ω
================================================================================
Phase     : PHASE_XVIII_ENGINE_CORRIDORS_VITAUX_Ω
Commandant: STEEVE-MAX
Tag       : BCE-4X ULTIME ABSOLU — TOP-ABSOLU

ENGINE CORRIDORS VITAUX Ω — ancrage explicite des corridors sur les zones
vitales officielles du registry institutionnel.

PRINCIPE : un corridor n'a de valeur biologique que s'il connecte des
zones vitales du registre officiel. Les corridors qui ne touchent aucune
zone vitale dans 150 m sont rejetés en dernier filtre PRE-RenduΩ et
journalisés dans `corridors_rejected_vitaux_xviii.json`.

═════════════════════════════════════════════════════════════════════════
ZONES VITALES OFFICIELLES (registry §5)
═════════════════════════════════════════════════════════════════════════

Catégorie MAJEURE (4) :
  - alimentation
  - rut
  - repos
  - eau

Catégorie SECONDAIRE / SUPPORT (5) :
  - thermique (refuge)
  - salines
  - ravages (orignal hivernal)
  - zones_humides
  - transition (lisière, mosaïque, clairière, écotone)

═════════════════════════════════════════════════════════════════════════
RÈGLES INSTITUTIONNELLES PAR ESPÈCE (§6)
═════════════════════════════════════════════════════════════════════════

Groupe GRANDS_MAMMIFERES (orignal, wapiti, ours_noir) :
  Corridor valide ⇔
    (≥ 1 zone vitale MAJEURE)
    ET (≥ 1 attracteur écologique fort)
    dans un rayon de 150 m du path
  où "attracteur fort" =
    {salines, ravages, zones_humides, hotspots-MAJEURS, eau-fluviale}

Groupe PETITS_MAMMIFERES (chevreuil, dindon_sauvage) :
  Corridor valide ⇔
    (≥ 1 zone vitale)
    ET (≥ 1 transition pertinente : lisière, mosaïque, clairière)
    dans un rayon de 150 m du path

Mode FILTRE : les corridors invalides sont retirés du bundle final et
consignés dans `corridors_rejected_vitaux_xviii` pour audit institutionnel.
"""
from __future__ import annotations

import json
import math
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# ═══════════════════════════════════════════════════════════════════════
# Constantes institutionnelles
# ═══════════════════════════════════════════════════════════════════════
ANCHOR_PROXIMITY_M = 150.0  # Rayon institutionnel par directive Commandant

# PHASE XVIII-VITAUX-RAYON_TUNING_Ω — mode externe 600 m
# Pour les corridors `origin_external_passed = True` UNIQUEMENT, le rayon
# d'ancrage est étendu au rayon fonctionnel complet du territoire.
EXTERNAL_MODE_RADIUS_M = 600.0
EXTERNAL_MODE_ENABLED = os.environ.get("XVIII_VITAUX_EXTERNAL_MODE", "1") == "1"

VITAL_ZONES_MAJOR = {"alimentation", "rut", "repos", "eau"}
VITAL_ZONES_SECONDARY = {"thermique", "thermal", "refuge"}
TRANSITION_ZONES = {"transition", "lisiere", "lisière", "mosaique", "mosaïque",
                    "clairiere", "clairière", "ecotone", "écotone"}

SPECIES_GROUP = {
    "orignal": "GRANDS_MAMMIFERES",
    "wapiti": "GRANDS_MAMMIFERES",
    "ours": "GRANDS_MAMMIFERES",
    "ours_noir": "GRANDS_MAMMIFERES",
    "cerf": "PETITS_MAMMIFERES",
    "chevreuil": "PETITS_MAMMIFERES",
    "dindon": "PETITS_MAMMIFERES",
    "dindon_sauvage": "PETITS_MAMMIFERES",
}

# Mode enforcement (par défaut activé pour P0)
ENFORCE_MODE = os.environ.get("PHASE_XVIII_VITAUX_ENFORCE", "1") == "1"

# Audit log path
AUDIT_LOG_PATH = Path(os.environ.get(
    "VITAUX_AUDIT_LOG",
    "/app/backend/cache/corridors_rejected_vitaux_xviii.json",
))


# ═══════════════════════════════════════════════════════════════════════
# Helpers géométriques
# ═══════════════════════════════════════════════════════════════════════
def _dist_m(a: List[float], b: List[float]) -> float:
    R = 6371000.0
    la1, lo1 = math.radians(a[0]), math.radians(a[1])
    la2, lo2 = math.radians(b[0]), math.radians(b[1])
    h = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 2 * R * math.asin(min(1.0, math.sqrt(h)))


def _zone_centroid(zone: Dict[str, Any]) -> Optional[Tuple[float, float]]:
    poly = zone.get("polygon") or zone.get("coords") or []
    if isinstance(poly, list) and poly:
        try:
            cz_lat = sum(p[0] for p in poly) / len(poly)
            cz_lon = sum(p[1] for p in poly) / len(poly)
            return (cz_lat, cz_lon)
        except Exception:
            return None
    if zone.get("lat") is not None:
        lng = zone.get("lng") or zone.get("lon")
        if lng is not None:
            return (float(zone["lat"]), float(lng))
    return None


def _path_within_proximity(path: List[List[float]], target: Tuple[float, float],
                            radius_m: float) -> bool:
    for pt in path:
        if _dist_m([pt[0], pt[1]], [target[0], target[1]]) <= radius_m:
            return True
    return False


# ═══════════════════════════════════════════════════════════════════════
# Détection des ancrages vitaux
# ═══════════════════════════════════════════════════════════════════════
def _zone_type_lower(zone: Dict[str, Any]) -> str:
    return str(zone.get("type") or zone.get("nom") or zone.get("category") or "").lower().strip()


def detect_vital_anchors(path: List[List[float]],
                          zones: List[Dict[str, Any]],
                          salines: List[Dict[str, Any]],
                          hotspots: List[Dict[str, Any]],
                          zones_humides: List[Dict[str, Any]],
                          radius_m: float = ANCHOR_PROXIMITY_M) -> Dict[str, Any]:
    """Énumère tous les ancrages vitaux trouvés dans le rayon du path."""
    if not path:
        return {
            "major_zones": [], "secondary_zones": [],
            "transition_zones": [], "salines": 0,
            "hotspots_major": 0, "zones_humides": 0,
        }

    major: List[str] = []
    secondary: List[str] = []
    transitions: List[str] = []

    for z in zones or []:
        c = _zone_centroid(z)
        if not c:
            continue
        if not _path_within_proximity(path, c, radius_m):
            continue
        ztype = _zone_type_lower(z)
        if ztype in VITAL_ZONES_MAJOR:
            major.append(ztype)
        elif ztype in VITAL_ZONES_SECONDARY:
            secondary.append(ztype)
        elif any(t in ztype for t in TRANSITION_ZONES):
            transitions.append(ztype)
        # Détection mots-clés transition même si type ne correspond pas exactement
        elif "lis" in ztype or "mosa" in ztype or "clair" in ztype or "ecoto" in ztype:
            transitions.append(ztype)

    salines_count = 0
    for s in salines or []:
        c = (float(s.get("lat", 0)), float(s.get("lng") or s.get("lon") or 0))
        if c[0] == 0 and c[1] == 0:
            continue
        if _path_within_proximity(path, c, radius_m):
            salines_count += 1

    hotspots_major = 0
    for h in hotspots or []:
        c_lat = h.get("lat") or (h.get("center") or {}).get("lat")
        c_lng = h.get("lng") or h.get("lon") or (h.get("center") or {}).get("lng")
        if c_lat is None or c_lng is None:
            continue
        # On retient un hotspot comme attracteur fort s'il a une intensité ≥ 0.6
        # ou s'il porte une étiquette MAJEUR
        intensity = h.get("intensity") or h.get("score") or 0.5
        is_major = (h.get("category") or "").lower() == "major" or intensity >= 0.6
        if is_major and _path_within_proximity(path, (float(c_lat), float(c_lng)), radius_m):
            hotspots_major += 1

    zh_count = 0
    for zh in zones_humides or []:
        c = _zone_centroid(zh)
        if c and _path_within_proximity(path, c, radius_m):
            zh_count += 1

    return {
        "major_zones": major,
        "secondary_zones": secondary,
        "transition_zones": transitions,
        "salines": salines_count,
        "hotspots_major": hotspots_major,
        "zones_humides": zh_count,
    }


# ═══════════════════════════════════════════════════════════════════════
# Validation par espèce
# ═══════════════════════════════════════════════════════════════════════
def validate_corridor_vital_anchor(corridor: Dict[str, Any],
                                     species: str,
                                     zones: List[Dict[str, Any]],
                                     salines: List[Dict[str, Any]],
                                     hotspots: Optional[List[Dict[str, Any]]] = None,
                                     zones_humides: Optional[List[Dict[str, Any]]] = None,
                                     radius_m: float = ANCHOR_PROXIMITY_M) -> Dict[str, Any]:
    """Valide un corridor selon les règles vitaux par espèce."""
    path = corridor.get("path") or []
    if not path:
        return {"valid": False, "reason": "empty_path", "anchors": None, "rule": None}

    canon = (species or "").lower().strip()
    group = SPECIES_GROUP.get(canon, "PETITS_MAMMIFERES")

    # ─── PHASE XVIII-VITAUX-RAYON_TUNING_Ω : détection du mode externe
    is_origin_external = bool(corridor.get("origin_external_passed"))
    if EXTERNAL_MODE_ENABLED and is_origin_external:
        effective_radius = EXTERNAL_MODE_RADIUS_M
        external_mode_applied = True
    else:
        effective_radius = radius_m
        external_mode_applied = False

    anchors = detect_vital_anchors(path, zones or [], salines or [],
                                    hotspots or [], zones_humides or [],
                                    radius_m=effective_radius)

    has_major_zone = len(anchors["major_zones"]) >= 1
    has_secondary_zone = len(anchors["secondary_zones"]) >= 1
    has_transition = len(anchors["transition_zones"]) >= 1
    # "Attracteur écologique fort" = saline OU hotspot majeur OU zone humide OU eau (eau fluviale)
    strong_attractor_count = (
        anchors["salines"] + anchors["hotspots_major"] + anchors["zones_humides"]
        + (1 if "eau" in anchors["major_zones"] else 0)
    )
    has_strong_attractor = strong_attractor_count >= 1

    # Pour petits mammifères, transition compte ; lisière hotspot aussi
    has_any_vital = has_major_zone or has_secondary_zone

    # ─── BRANCHE MODE EXTERNE (PHASE XVIII-VITAUX-RAYON_TUNING_Ω)
    if external_mode_applied:
        rule = (f"MODE EXTERNE {EXTERNAL_MODE_RADIUS_M:.0f} m : ≥ 1 zone vitale "
                f"MAJEURE (attracteur fort recommandé non bloquant)")
        valid = has_major_zone
        if not valid:
            reason = "fail_external_mode_no_major_zone"
        else:
            reason = "ok_external_mode"
    elif group == "GRANDS_MAMMIFERES":
        rule = ("≥ 1 zone vitale MAJEURE + ≥ 1 attracteur écologique fort "
                "(saline / hotspot majeur / zone humide / eau fluviale) dans 150 m")
        valid = has_major_zone and has_strong_attractor
        if not valid:
            missing = []
            if not has_major_zone:
                missing.append("zone_vitale_majeure")
            if not has_strong_attractor:
                missing.append("attracteur_ecologique_fort")
            reason = f"fail_grands_mammiferes(missing={','.join(missing)})"
        else:
            reason = "ok"
    else:  # PETITS_MAMMIFERES
        rule = ("≥ 1 zone vitale (majeure ou secondaire) + ≥ 1 transition "
                "(lisière / mosaïque / clairière / hotspot) dans 150 m")
        # Hotspot peut servir de transition pour petits mammifères
        has_transition_or_hotspot = has_transition or anchors["hotspots_major"] >= 1
        valid = has_any_vital and has_transition_or_hotspot
        if not valid:
            missing = []
            if not has_any_vital:
                missing.append("zone_vitale")
            if not has_transition_or_hotspot:
                missing.append("transition_pertinente")
            reason = f"fail_petits_mammiferes(missing={','.join(missing)})"
        else:
            reason = "ok"

    return {
        "valid": valid,
        "reason": reason,
        "rule": rule,
        "group": group,
        "external_mode_applied": external_mode_applied,
        "vitaux_external_attractor_present": (
            has_strong_attractor if external_mode_applied else None
        ),
        "anchors": anchors,
        "anchors_summary": {
            "major_zones_count": len(anchors["major_zones"]),
            "secondary_zones_count": len(anchors["secondary_zones"]),
            "transitions_count": len(anchors["transition_zones"]),
            "salines": anchors["salines"],
            "hotspots_major": anchors["hotspots_major"],
            "zones_humides": anchors["zones_humides"],
            "strong_attractor_count": strong_attractor_count,
        },
        "radius_m": effective_radius,
        "phase": "PHASE_XVIII_ENGINE_CORRIDORS_VITAUX_Ω",
        "subphase": (
            "PHASE_XVIII_VITAUX_RAYON_TUNING_Ω" if external_mode_applied else None
        ),
    }


# ═══════════════════════════════════════════════════════════════════════
# Audit log JSON (corridors_rejected_vitaux_xviii.json)
# ═══════════════════════════════════════════════════════════════════════
def _append_audit_log(rejected_payload: List[Dict[str, Any]],
                       species: str,
                       waypoint: Dict[str, float]) -> None:
    """Persiste les rejets dans un log JSON cumulatif (audit institutionnel)."""
    try:
        AUDIT_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        existing: List[Dict[str, Any]] = []
        if AUDIT_LOG_PATH.exists():
            try:
                existing = json.loads(AUDIT_LOG_PATH.read_text(encoding="utf-8"))
                if not isinstance(existing, list):
                    existing = []
            except Exception:
                existing = []
        # On limite à 500 dernières entrées pour éviter la saturation disque
        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "phase": "PHASE_XVIII_ENGINE_CORRIDORS_VITAUX_Ω",
            "species": species,
            "waypoint": waypoint,
            "rejected_count": len(rejected_payload),
            "rejected": rejected_payload[:30],  # cap par run
        }
        existing.append(record)
        existing = existing[-500:]
        AUDIT_LOG_PATH.write_text(
            json.dumps(existing, ensure_ascii=False, indent=1),
            encoding="utf-8",
        )
    except Exception:
        pass  # ne jamais bloquer le pipeline pour un échec audit


# ═══════════════════════════════════════════════════════════════════════
# Application au bundle complet
# ═══════════════════════════════════════════════════════════════════════
def apply_corridors_vitaux_to_bundle(bundle: Dict[str, Any],
                                       species: str) -> Dict[str, Any]:
    """Filtre les corridors selon les règles vitaux Ω et journalise les rejets."""
    if not isinstance(bundle, dict):
        return bundle
    corridors = bundle.get("corridors") or []
    zones = bundle.get("zones") or []
    salines = bundle.get("salines") or []
    hotspots = bundle.get("hotspots") or []
    zones_humides = bundle.get("zones_humides") or []
    waypoint = bundle.get("waypoint") or {}

    kept: List[Dict[str, Any]] = []
    rejected: List[Dict[str, Any]] = []
    rejected_audit: List[Dict[str, Any]] = []
    rejected_reasons: Dict[str, int] = {}
    anchor_types_used: Dict[str, int] = {}
    # PHASE XVIII-VITAUX-RAYON_TUNING_Ω — métriques mode externe
    vitaux_external_mode_applied_count = 0
    vitaux_external_mode_passed_count = 0
    origin_external_passed_count = 0

    canon = (species or "").lower().strip()
    group = SPECIES_GROUP.get(canon, "PETITS_MAMMIFERES")

    for c in corridors:
        if c.get("origin_external_passed") is True:
            origin_external_passed_count += 1
        out = validate_corridor_vital_anchor(
            c, species=species, zones=zones, salines=salines,
            hotspots=hotspots, zones_humides=zones_humides,
        )
        c["vitaux_validation"] = out
        if out.get("external_mode_applied"):
            vitaux_external_mode_applied_count += 1
            if out.get("valid"):
                vitaux_external_mode_passed_count += 1
        if out["valid"]:
            kept.append(c)
            # Inventaire des types d'ancrages utilisés
            for mz in out["anchors"]["major_zones"]:
                anchor_types_used[mz] = anchor_types_used.get(mz, 0) + 1
            for sz in out["anchors"]["secondary_zones"]:
                anchor_types_used[sz] = anchor_types_used.get(sz, 0) + 1
            for tz in out["anchors"]["transition_zones"]:
                anchor_types_used[tz] = anchor_types_used.get(tz, 0) + 1
            if out["anchors"]["salines"] > 0:
                anchor_types_used["salines"] = anchor_types_used.get("salines", 0) + 1
            if out["anchors"]["hotspots_major"] > 0:
                anchor_types_used["hotspots_major"] = anchor_types_used.get("hotspots_major", 0) + 1
            if out["anchors"]["zones_humides"] > 0:
                anchor_types_used["zones_humides"] = anchor_types_used.get("zones_humides", 0) + 1
        else:
            r_short = out["reason"].split("(")[0]
            rejected_reasons[r_short] = rejected_reasons.get(r_short, 0) + 1
            rejected.append(c)
            rejected_audit.append({
                "id": c.get("id"),
                "reason": out["reason"],
                "anchors_summary": out["anchors_summary"],
                "path_first": c.get("path", [None, None])[0] if c.get("path") else None,
                "path_last": c.get("path", [None, None])[-1] if c.get("path") else None,
            })

    if ENFORCE_MODE:
        bundle["corridors"] = kept
        bundle["corridors_rejected_vitaux_xviii"] = rejected_audit
        if rejected_audit:
            _append_audit_log(rejected_audit, species=species, waypoint=waypoint)
    else:
        # Annotation seulement
        bundle["corridors_rejected_vitaux_xviii_annotated_only"] = rejected_audit

    bundle["corridors_vitaux_omega_applied"] = True
    bundle["corridors_vitaux_omega_stats"] = {
        "phase": "PHASE_XVIII_ENGINE_CORRIDORS_VITAUX_Ω",
        "subphase_applied": "PHASE_XVIII_VITAUX_RAYON_TUNING_Ω",
        "species": species,
        "species_group": group,
        "rule_applied": (
            "≥ 1 zone MAJEURE + ≥ 1 attracteur fort dans 150 m" if group == "GRANDS_MAMMIFERES"
            else "≥ 1 zone vitale + ≥ 1 transition dans 150 m"
        ),
        "external_mode_rule": (
            f"MODE EXTERNE {EXTERNAL_MODE_RADIUS_M:.0f} m : ≥ 1 zone MAJEURE "
            f"(attracteur fort recommandé non bloquant) si origin_external_passed=true"
        ),
        "anchor_proximity_m": ANCHOR_PROXIMITY_M,
        "external_mode_radius_m": EXTERNAL_MODE_RADIUS_M,
        "external_mode_enabled": EXTERNAL_MODE_ENABLED,
        "enforce_mode": ENFORCE_MODE,
        "total_input": len(corridors),
        "total_kept": len(kept),
        "total_rejected": len(rejected),
        "rate_pct": round(100.0 * len(kept) / max(1, len(corridors)), 1),
        # PHASE XVIII-VITAUX-RAYON_TUNING_Ω — directive §4
        "corridors_v30_count": len(corridors),
        "origin_external_passed_count": origin_external_passed_count,
        "vitaux_external_mode_applied_count": vitaux_external_mode_applied_count,
        "vitaux_external_mode_passed_count": vitaux_external_mode_passed_count,
        "rejected_reasons": rejected_reasons,
        "anchor_types_used": anchor_types_used,
        "audit_log_path": str(AUDIT_LOG_PATH),
    }
    return bundle

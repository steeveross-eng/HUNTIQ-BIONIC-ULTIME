"""usgs_soil_omega.py — USGS_SOIL_P0_VALIDATE + HOOK_ACTIVATE_Ω
═══════════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU x3 · ANTI_GÉNÉRIQUE_STRICT

Validation et activation du hook USGS_SOIL via SoilGrids ISRIC (pivot
anti-générique documenté : USGS Soil ne couvre PAS le Québec, USGS=US only).

PIVOT ANTI-GÉNÉRIQUE STRICT (audit transparent au Commandant) :
  · USGS NGS WFS (mrdata.usgs.gov/services/ngs) répond HTTP 200 mais
    couverture US continental uniquement (codes FIPS/HUC/QUAD).
  · Pivot vers SoilGrids ISRIC (Hengl et al. 2017 PLOS ONE,
    DOI:10.1371/journal.pone.0169748) — référence mondiale 250m soil
    properties peer-reviewed, couvre Québec/Canada.
  · Endpoint : https://rest.isric.org/soilgrids/v2.0/properties/query
  · 12 propriétés disponibles : phh2o, cec, nitrogen, clay, sand, silt,
    ocd, ocs, soc, bdod, cfvo, wv0010

Stratégie offset terrestre (anti-générique strict) :
  · 3/5 coords BP135 originales tombent sur water_mask St-Laurent (mean=null)
  · Offset séquentiel +0.05° latitude/longitude (4 directions cardinales)
  · Tracé doctrinal de l'offset appliqué par site
  · Aucune fabrication : si toutes les directions retournent null,
    site = WATER_MASK_OFFSET_FAILED documenté

RÉFÉRENCES PEER-REVIEWED :
  [1] Hengl, T., Mendes de Jesus, J., Heuvelink, G. B., et al. (2017).
      SoilGrids250m: Global gridded soil information based on machine
      learning. PLOS ONE, 12(2), e0169748.
      DOI:10.1371/journal.pone.0169748
  [2] Poggio, L., de Sousa, L. M., Batjes, N. H., et al. (2021).
      SoilGrids 2.0: producing soil information for the globe with
      quantified spatial uncertainty. SOIL, 7(1), 217-240.
      DOI:10.5194/soil-7-217-2021
═══════════════════════════════════════════════════════════════════════════
"""
from __future__ import annotations

import hashlib
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


USGS_SOIL_ROOT = Path("/app/backend/data/pipelines/usgs_soil")
USGS_SOIL_VALIDATION_PATH = (
    USGS_SOIL_ROOT / "usgs_soil_validation_overlay.json")
USGS_SOIL_HOOK_ACTIVATION_PATH = (
    USGS_SOIL_ROOT / "usgs_soil_hook_activation_overlay.json")


# ═════════════════════════════════════════════════════════════════════════
# Registry SoilGrids ISRIC — propriétés disponibles + d_factors officiels
# Source : https://www.isric.org/explore/soilgrids/faq-soilgrids
# ═════════════════════════════════════════════════════════════════════════
SOILGRIDS_PROPERTIES_REGISTRY: Dict[str, Dict[str, Any]] = {
    "phh2o": {
        "description": "Soil pH (H2O)",
        "d_factor": 10,
        "target_units": "pH × 10 (divide by d_factor for true pH)",
        "depth_layers_cm": ["0-5", "5-15", "15-30", "30-60", "60-100"],
    },
    "cec": {
        "description": "Cation Exchange Capacity",
        "d_factor": 10,
        "target_units": "cmol(c)/kg",
        "depth_layers_cm": ["0-5", "5-15", "15-30", "30-60"],
    },
    "nitrogen": {
        "description": "Total nitrogen",
        "d_factor": 100,
        "target_units": "g/kg",
        "depth_layers_cm": ["0-5", "5-15", "15-30", "30-60"],
    },
    "clay": {
        "description": "Clay content",
        "d_factor": 10,
        "target_units": "%",
        "depth_layers_cm": ["0-5", "5-15", "15-30", "30-60"],
    },
    "sand": {
        "description": "Sand content",
        "d_factor": 10,
        "target_units": "%",
        "depth_layers_cm": ["0-5", "5-15", "15-30", "30-60"],
    },
    "soc": {
        "description": "Soil Organic Carbon",
        "d_factor": 10,
        "target_units": "g/kg (as dg/kg ÷ 10)",
        "depth_layers_cm": ["0-5", "5-15", "15-30", "30-60"],
    },
}


# Offsets cardinaux séquentiels pour fallback water_mask (anti-générique)
TERRESTRIAL_OFFSETS_CARDINAL: List[Tuple[float, float]] = [
    (+0.05, 0.0),   # nord
    (-0.05, 0.0),   # sud
    (0.0, +0.05),   # est
    (0.0, -0.05),   # ouest
]


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _http_get_json_strict(
    url: str,
    timeout_s: int = 15,
    body_max_bytes: int = 524288,
) -> Dict[str, Any]:
    """GET strict JSON sans follow_redirects."""
    import urllib.request
    import urllib.error

    class NoRedirectHandler(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg,
                              headers, newurl):
            return None

    record: Dict[str, Any] = {
        "url": url,
        "http_status": None,
        "content_type": None,
        "body_is_json": False,
        "parsed_json": None,
        "json_parse_error": None,
        "reason": None,
        "elapsed_ms": None,
    }
    t0 = time.time()
    try:
        opener = urllib.request.build_opener(NoRedirectHandler)
        req = urllib.request.Request(
            url, method="GET",
            headers={
                "User-Agent": "BCE-4X-USGS-SOIL-VALIDATE/1.0",
                "Accept": "application/json",
            })
        with opener.open(req, timeout=timeout_s) as resp:
            record["http_status"] = resp.status
            record["content_type"] = resp.headers.get(
                "Content-Type")
            body = resp.read(body_max_bytes)
            try:
                record["parsed_json"] = json.loads(
                    body.decode("utf-8", errors="replace"))
                record["body_is_json"] = True
            except json.JSONDecodeError as e:
                record["json_parse_error"] = str(e)[:200]
    except urllib.error.HTTPError as e:
        record["http_status"] = e.code
        record["reason"] = f"http_error_{e.code}"
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        record["reason"] = f"network_error::{str(e)[:160]}"
    record["elapsed_ms"] = round((time.time() - t0) * 1000, 1)
    return record


def _extract_property_mean_from_soilgrids(
    parsed: Dict[str, Any],
    property_name: str,
    depth_label: str,
) -> Optional[float]:
    """Extrait mean d'une propriété/profondeur depuis JSON SoilGrids."""
    if not isinstance(parsed, dict):
        return None
    layers = (parsed.get("properties") or {}).get("layers") or []
    for layer in layers:
        if layer.get("name") != property_name:
            continue
        for depth in layer.get("depths") or []:
            if depth.get("label") == depth_label:
                vals = depth.get("values") or {}
                m = vals.get("mean")
                if m is not None:
                    d_factor = (
                        layer.get("unit_measure") or {}
                    ).get("d_factor", 1)
                    if d_factor and d_factor > 0:
                        return float(m) / float(d_factor)
                    return float(m)
                return None
    return None


def _probe_soilgrids_at_coord(
    lat: float,
    lon: float,
    properties: List[str],
    depth_label: str = "0-5cm",
    timeout_s: int = 15,
) -> Dict[str, Any]:
    """Probe SoilGrids ISRIC pour une coord + liste propriétés.

    Retourne extracted={prop: value_or_None} + raw_record.
    """
    props_query = "&".join(f"property={p}" for p in properties)
    depth_query = f"depth={depth_label}"
    url = (
        f"https://rest.isric.org/soilgrids/v2.0/properties/query?"
        f"lon={lon}&lat={lat}&{props_query}&{depth_query}&value=mean")
    probe = _http_get_json_strict(url, timeout_s=timeout_s)
    extracted: Dict[str, Optional[float]] = {}
    n_valid = 0
    if (probe["http_status"] == 200
            and probe["body_is_json"]):
        for prop in properties:
            val = _extract_property_mean_from_soilgrids(
                probe["parsed_json"], prop, depth_label)
            extracted[prop] = val
            if val is not None:
                n_valid += 1
    return {
        "lat": lat,
        "lon": lon,
        "url": url,
        "http_status": probe["http_status"],
        "elapsed_ms": probe["elapsed_ms"],
        "reason": probe["reason"],
        "extracted_properties": extracted,
        "n_properties_valid": n_valid,
        "n_properties_requested": len(properties),
    }


def _probe_with_terrestrial_offset_fallback(
    lat_orig: float,
    lon_orig: float,
    properties: List[str],
    depth_label: str = "0-5cm",
    timeout_s: int = 15,
) -> Dict[str, Any]:
    """Probe coord originale, fallback séquentiel sur 4 offsets cardinaux.

    Anti-générique strict : on s'arrête au premier offset retournant
    n_properties_valid >= 1, et on trace l'offset utilisé.
    """
    # 1) coord originale
    primary = _probe_soilgrids_at_coord(
        lat_orig, lon_orig, properties, depth_label, timeout_s)
    if primary["n_properties_valid"] >= 1:
        return {
            "coord_origin": {"lat": lat_orig, "lon": lon_orig},
            "coord_used": {"lat": lat_orig, "lon": lon_orig},
            "offset_applied": {"d_lat": 0.0, "d_lon": 0.0},
            "offset_strategy": "ORIGINAL_COORD_VALID",
            "fallback_attempts": [],
            "probe_record": primary,
            "valid": True,
        }
    # 2) fallback offsets cardinaux séquentiels
    fallback_attempts: List[Dict[str, Any]] = []
    fallback_attempts.append({
        "offset": "ORIGINAL",
        "lat": lat_orig, "lon": lon_orig,
        "n_properties_valid": primary["n_properties_valid"],
    })
    for d_lat, d_lon in TERRESTRIAL_OFFSETS_CARDINAL:
        new_lat = round(lat_orig + d_lat, 4)
        new_lon = round(lon_orig + d_lon, 4)
        attempt = _probe_soilgrids_at_coord(
            new_lat, new_lon, properties, depth_label, timeout_s)
        fallback_attempts.append({
            "offset": f"d_lat={d_lat},d_lon={d_lon}",
            "lat": new_lat, "lon": new_lon,
            "http_status": attempt["http_status"],
            "n_properties_valid": attempt["n_properties_valid"],
        })
        if attempt["n_properties_valid"] >= 1:
            return {
                "coord_origin": {
                    "lat": lat_orig, "lon": lon_orig},
                "coord_used": {"lat": new_lat, "lon": new_lon},
                "offset_applied": {
                    "d_lat": d_lat, "d_lon": d_lon},
                "offset_strategy": (
                    f"WATER_MASK_OFFSET_RECOVERED::"
                    f"d_lat={d_lat},d_lon={d_lon}"),
                "fallback_attempts": fallback_attempts,
                "probe_record": attempt,
                "valid": True,
            }
    # 3) tous les offsets ont échoué → DEFERRED honnête
    return {
        "coord_origin": {"lat": lat_orig, "lon": lon_orig},
        "coord_used": None,
        "offset_applied": None,
        "offset_strategy": "WATER_MASK_OFFSET_FAILED_ALL_4_DIRECTIONS",
        "fallback_attempts": fallback_attempts,
        "probe_record": primary,
        "valid": False,
    }


# ═════════════════════════════════════════════════════════════════════════
# VALIDATE — multi-espèces × multi-propriétés × terrestrial offset fallback
# ═════════════════════════════════════════════════════════════════════════
def validate_usgs_soil_per_species(
    species_coordinates: Dict[str, Dict[str, float]],
    properties: Optional[List[str]] = None,
    depth_label: str = "0-5cm",
    persist: bool = True,
    timeout_s: int = 15,
    inter_call_sleep_s: float = 0.3,
) -> Dict[str, Any]:
    """USGS_SOIL_P0_VALIDATE_Ω · multi-espèces × multi-propriétés.

    Workflow doctrinal :
      1. Guardrails ENFORCED check (412 sinon)
      2. Validation coords (lat/lon)
      3. Pour chaque espèce : probe SoilGrids ISRIC avec fallback
         offset terrestre +0.05° (4 directions cardinales)
      4. Tracé doctrinal pivot ANTI-GÉNÉRIQUE : USGS_NGS_NOT_COVERING_QUEBEC
      5. Manifest signé SHA-256
      6. Forensic log ENDPOINT_PROBES/USGS_SOIL_P0_VALIDATE_Ω
      7. Persistance overlay + audit doctrinal NOAA_PIPELINE
      8. AUCUN recalcul moteur · V30_LOCK + DRIFT_ZERO

    Default properties si None : phh2o, cec, nitrogen, clay, sand, soc.
    """
    from engines.v8_institutional.especes.pipeline_guardrails_omega import (
        require_guardrails_enforced, log_forensic_event,
    )
    require_guardrails_enforced("validate_usgs_soil_per_species")

    if not species_coordinates:
        raise ValueError(
            "SPECIES_COORDINATES_REQUIRED::empty")
    for sp_name, coords in species_coordinates.items():
        lat = coords.get("lat") if isinstance(coords, dict) else None
        lon = coords.get("lon") if isinstance(coords, dict) else None
        if (lat is None or lon is None
                or not (-90.0 <= float(lat) <= 90.0)
                or not (-180.0 <= float(lon) <= 180.0)):
            raise ValueError(
                f"COORDS_INVALID::{sp_name}::lat={lat},lon={lon}")

    properties = properties or [
        "phh2o", "cec", "nitrogen", "clay", "sand", "soc"]
    # Filtre sur propriétés connues du registry (anti-générique)
    properties_validated = [
        p for p in properties if p in SOILGRIDS_PROPERTIES_REGISTRY]
    properties_unknown = [
        p for p in properties if p not in SOILGRIDS_PROPERTIES_REGISTRY]

    t_total = time.time()
    species_results: Dict[str, Dict[str, Any]] = {}
    n_calls_made = 0
    n_calls_success = 0
    n_calls_failed = 0
    n_offset_recovered = 0

    for sp_name, coords in species_coordinates.items():
        lat = float(coords["lat"])
        lon = float(coords["lon"])
        result = _probe_with_terrestrial_offset_fallback(
            lat, lon, properties_validated,
            depth_label=depth_label, timeout_s=timeout_s)
        n_calls_made += len(result["fallback_attempts"]) or 1
        if result["valid"]:
            n_calls_success += 1
            if (result["offset_strategy"]
                    != "ORIGINAL_COORD_VALID"):
                n_offset_recovered += 1
        else:
            n_calls_failed += 1
        species_results[sp_name] = result

        log_forensic_event(
            scope="ENDPOINT_PROBES",
            event="USGS_SOIL_P0_VALIDATE_Ω",
            details={
                "provider_logical": "USGS_SOIL",
                "provider_physical": "SOILGRIDS_ISRIC",
                "species": sp_name,
                "coord_origin": result["coord_origin"],
                "coord_used": result["coord_used"],
                "offset_strategy": result["offset_strategy"],
                "n_properties_valid": (
                    (result["probe_record"] or {})
                    .get("n_properties_valid", 0)),
                "valid": result["valid"],
            },
            persist=True,
        )
        if inter_call_sleep_s > 0:
            time.sleep(inter_call_sleep_s)

    if n_calls_success == len(species_coordinates):
        verdict = "USGS_SOIL_VALIDATE_ALL_SITES_VALID"
        valid = True
    elif n_calls_success > 0:
        verdict = (
            f"USGS_SOIL_VALIDATE_PARTIAL::"
            f"{n_calls_success}_OF_{len(species_coordinates)}_VALID")
        valid = False
    else:
        verdict = "USGS_SOIL_VALIDATE_ALL_SITES_INVALID"
        valid = False

    payload = {
        "manifest_id": "USGS_SOIL_P0_VALIDATE_Ω",
        "ordre": "P1_USGS_SOIL_P0_VALIDATE_Ω",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "guardrails_enforced": True,
        "autonomy": "LIMITED",
        "valid": valid,
        "verdict": verdict,
        "provider_logical": "USGS_SOIL",
        "provider_physical": "SOILGRIDS_ISRIC",
        "pivot_doctrinal_anti_generique": {
            "reason_pivot": (
                "USGS NGS WFS (mrdata.usgs.gov) couvre US continental "
                "uniquement (codes FIPS/HUC/QUAD). Le Québec n'est PAS "
                "couvert par USGS Soil. Pivot vers SoilGrids ISRIC "
                "(Hengl 2017 PLOS ONE) — référence mondiale 250m "
                "peer-reviewed couvrant Québec/Canada."),
            "endpoint_used": (
                "https://rest.isric.org/soilgrids/v2.0/properties/query"),
            "scientific_reference_primary": (
                "Hengl et al. (2017). PLOS ONE, 12(2), e0169748. "
                "DOI:10.1371/journal.pone.0169748"),
            "scientific_reference_v2": (
                "Poggio et al. (2021). SOIL, 7(1), 217-240. "
                "DOI:10.5194/soil-7-217-2021"),
        },
        "depth_label": depth_label,
        "properties_requested": properties,
        "properties_validated_in_registry": properties_validated,
        "properties_unknown_skipped": properties_unknown,
        "n_species_total": len(species_coordinates),
        "n_calls_made": n_calls_made,
        "n_calls_success": n_calls_success,
        "n_calls_failed": n_calls_failed,
        "n_sites_recovered_via_terrestrial_offset": (
            n_offset_recovered),
        "terrestrial_offset_strategy": (
            "Sequential cardinal +0.05° fallback "
            "(N → S → E → W) for water_mask sites. "
            "Anti-générique strict : tracé par site."),
        "species_results": species_results,
        "anti_generique_strict": True,
        "v30_lock": "INVIOLÉ",
        "drift_zero": True,
        "no_engine_recompute_triggered": True,
        "executed_at_utc": _utc_now(),
        "elapsed_s": round(time.time() - t_total, 3),
    }
    payload_sha256 = hashlib.sha256(
        json.dumps(payload, sort_keys=True,
                   ensure_ascii=False, default=str).encode("utf-8")
    ).hexdigest()
    payload["manifest_sha256"] = payload_sha256

    persisted: Dict[str, Any] = {}
    if persist:
        USGS_SOIL_ROOT.mkdir(parents=True, exist_ok=True)
        if USGS_SOIL_VALIDATION_PATH.exists():
            try:
                state = json.loads(
                    USGS_SOIL_VALIDATION_PATH.read_text(
                        encoding="utf-8"))
                if not isinstance(state, dict) or (
                        "history" not in state):
                    state = {"history": []}
            except json.JSONDecodeError:
                state = {"history": []}
        else:
            state = {"history": []}
        state["history"].append(payload)
        state["last_updated_utc"] = _utc_now()
        state["n_validations"] = len(state["history"])
        state["last_manifest_sha256"] = payload_sha256
        state["last_verdict"] = verdict
        state["v30_lock"] = "INVIOLÉ"
        USGS_SOIL_VALIDATION_PATH.write_text(
            json.dumps(state, ensure_ascii=False, indent=2),
            encoding="utf-8")
        persisted["overlay_path"] = str(USGS_SOIL_VALIDATION_PATH)
        persisted["overlay_size_bytes"] = (
            USGS_SOIL_VALIDATION_PATH.stat().st_size)
        persisted["n_validations_history"] = state["n_validations"]

        from engines.v8_institutional.especes.bio_reacteur_overlay_omega import (  # noqa: E501
            persist_audit,
        )
        audit_payload = {
            "audit_type": "NOAA_PIPELINE",
            "subtype": "USGS_SOIL_VALIDATE",
            "ordre": "P1_USGS_SOIL_P0_VALIDATE_Ω",
            "doctrine":
                "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
            "provider_logical": "USGS_SOIL",
            "provider_physical": "SOILGRIDS_ISRIC",
            "valid": valid,
            "verdict": verdict,
            "manifest_sha256": payload_sha256,
            "n_species_total": len(species_coordinates),
            "n_calls_success": n_calls_success,
            "n_calls_failed": n_calls_failed,
            "n_sites_recovered_via_terrestrial_offset": (
                n_offset_recovered),
            "v30_lock_inviolate": True,
            "drift_zero": True,
            "no_engine_recompute_triggered": True,
        }
        persisted["audit_persisted"] = persist_audit(audit_payload)

    payload["persisted_paths"] = persisted
    return payload


# ═════════════════════════════════════════════════════════════════════════
# HOOK ACTIVATE — anti-générique strict (refus SHA fabriqué)
# ═════════════════════════════════════════════════════════════════════════
def _find_validated_usgs_soil_manifest(
    target_manifest_sha256: str,
) -> Optional[Dict[str, Any]]:
    """Cherche manifest USGS Soil validé dans l'historique."""
    if not USGS_SOIL_VALIDATION_PATH.exists():
        return None
    try:
        state = json.loads(
            USGS_SOIL_VALIDATION_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    history = state.get("history", [])
    for entry in history:
        if (entry.get("manifest_sha256") == target_manifest_sha256
                and entry.get("n_calls_success", 0) >= 1):
            return entry
    return None


def activate_usgs_soil_hook(
    manifest_sha256: str,
    reason: str = "usgs_soil_hook_activated",
    persist: bool = True,
) -> Dict[str, Any]:
    """USGS_SOIL_HOOK_ACTIVATE_Ω · activation officielle.

    Anti-générique strict : refus si SHA fabriqué/inconnu.
    """
    from engines.v8_institutional.especes.pipeline_guardrails_omega import (
        require_guardrails_enforced, log_forensic_event,
    )
    require_guardrails_enforced("activate_usgs_soil_hook")

    t0 = time.time()
    validated = _find_validated_usgs_soil_manifest(manifest_sha256)
    if validated is None:
        verdict = (
            "USGS_SOIL_HOOK_REJECTED_MANIFEST_NOT_FOUND_OR_INVALID")
        rejection_payload = {
            "manifest_id": "USGS_SOIL_HOOK_ACTIVATE_Ω",
            "ordre": "P1_USGS_SOIL_HOOK_ACTIVATE_Ω",
            "doctrine":
                "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
            "guardrails_enforced": True,
            "autonomy": "LIMITED",
            "activated": False,
            "verdict": verdict,
            "reason": reason,
            "input_manifest_sha256": manifest_sha256,
            "rejection_explanation": (
                "Le manifest_sha256 fourni n'existe pas dans "
                "USGS_SOIL_VALIDATION_PATH avec n_calls_success >= 1. "
                "Anti-générique strict : impossible d'activer le hook "
                "sur un manifest non validé."),
            "anti_generique_strict": True,
            "v30_lock": "INVIOLÉ",
            "drift_zero": True,
            "no_engine_recompute_triggered": True,
            "executed_at_utc": _utc_now(),
            "elapsed_s": round(time.time() - t0, 3),
        }
        log_forensic_event(
            scope="HOOK_ACTIVATIONS",
            event="USGS_SOIL_HOOK_ACTIVATE_Ω",
            details={
                "input_manifest_sha256": manifest_sha256,
                "reason": reason,
                "activated": False,
                "verdict": verdict,
            },
            persist=True,
        )
        return rejection_payload

    # Sommaire validé
    species_summary: List[Dict[str, Any]] = []
    for sp_name, sp_data in (
            validated.get("species_results") or {}).items():
        probe = sp_data.get("probe_record") or {}
        species_summary.append({
            "species_name": sp_name,
            "coord_origin": sp_data.get("coord_origin"),
            "coord_used": sp_data.get("coord_used"),
            "offset_strategy": sp_data.get("offset_strategy"),
            "valid": sp_data.get("valid"),
            "n_properties_valid": probe.get("n_properties_valid"),
            "extracted_properties": probe.get(
                "extracted_properties") or {},
        })

    activation_payload = {
        "manifest_id": "USGS_SOIL_HOOK_ACTIVATE_Ω",
        "ordre": "P1_USGS_SOIL_HOOK_ACTIVATE_Ω",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "guardrails_enforced": True,
        "autonomy": "LIMITED",
        "activated": True,
        "verdict": "USGS_SOIL_HOOK_ACTIVATED_OPERATIONAL",
        "reason": reason,
        "validated_manifest_sha256": manifest_sha256,
        "validated_executed_at_utc": validated.get("executed_at_utc"),
        "provider_logical": "USGS_SOIL",
        "provider_physical": "SOILGRIDS_ISRIC",
        "pivot_doctrinal_inherited": (
            validated.get("pivot_doctrinal_anti_generique")),
        "properties_inherited": validated.get(
            "properties_validated_in_registry") or [],
        "depth_label_inherited": validated.get("depth_label"),
        "n_species_total": validated.get("n_species_total"),
        "n_calls_success_inherited": validated.get(
            "n_calls_success"),
        "n_sites_recovered_via_terrestrial_offset_inherited": (
            validated.get(
                "n_sites_recovered_via_terrestrial_offset")),
        "species_summary": species_summary,
        "consumed_by_modules": [
            "SALINE_OPTIMAL_LOCATIONS_COMPUTE",
            "SOIL_pH_HABITAT_CONSTRAINT",
            "NUTRIENT_AVAILABILITY_PROXY",
            "MINERAL_LICK_PROXY_PROXIMITY",
        ],
        "deferred_outputs_unblocked_via_this_hook": [
            "saline_optimal_locations_partial_via_pH_CEC",
        ],
        "fusion_add_only": True,
        "anti_generique_strict": True,
        "v30_lock": "INVIOLÉ",
        "drift_zero": True,
        "no_engine_recompute_triggered": True,
        "registered_at_utc": _utc_now(),
    }
    activation_sha256 = hashlib.sha256(
        json.dumps(activation_payload, sort_keys=True,
                   ensure_ascii=False, default=str).encode("utf-8")
    ).hexdigest()
    activation_payload["activation_sha256"] = activation_sha256

    persisted: Dict[str, Any] = {}
    if persist:
        USGS_SOIL_ROOT.mkdir(parents=True, exist_ok=True)
        if USGS_SOIL_HOOK_ACTIVATION_PATH.exists():
            try:
                state = json.loads(
                    USGS_SOIL_HOOK_ACTIVATION_PATH.read_text(
                        encoding="utf-8"))
                if not isinstance(state, dict) or (
                        "history" not in state):
                    state = {"history": []}
            except json.JSONDecodeError:
                state = {"history": []}
        else:
            state = {"history": []}
        state["history"].append(activation_payload)
        state["last_updated_utc"] = _utc_now()
        state["n_activations"] = len(state["history"])
        state["last_activation_sha256"] = activation_sha256
        state["last_validated_manifest_sha256"] = manifest_sha256
        state["v30_lock"] = "INVIOLÉ"
        USGS_SOIL_HOOK_ACTIVATION_PATH.write_text(
            json.dumps(state, ensure_ascii=False, indent=2),
            encoding="utf-8")
        persisted["overlay_path"] = str(
            USGS_SOIL_HOOK_ACTIVATION_PATH)
        persisted["overlay_size_bytes"] = (
            USGS_SOIL_HOOK_ACTIVATION_PATH.stat().st_size)
        persisted["n_activations_history"] = state["n_activations"]

        log_forensic_event(
            scope="HOOK_ACTIVATIONS",
            event="USGS_SOIL_HOOK_ACTIVATE_Ω",
            details={
                "validated_manifest_sha256": manifest_sha256,
                "activation_sha256": activation_sha256,
                "reason": reason,
                "activated": True,
                "n_calls_success_inherited": validated.get(
                    "n_calls_success"),
                "verdict": "USGS_SOIL_HOOK_ACTIVATED_OPERATIONAL",
            },
            persist=True,
        )

        from engines.v8_institutional.especes.bio_reacteur_overlay_omega import (  # noqa: E501
            persist_audit,
        )
        audit_payload = {
            "audit_type": "NOAA_PIPELINE",
            "subtype": "USGS_SOIL_HOOK_ACTIVATE",
            "ordre": "P1_USGS_SOIL_HOOK_ACTIVATE_Ω",
            "doctrine":
                "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
            "provider_logical": "USGS_SOIL",
            "provider_physical": "SOILGRIDS_ISRIC",
            "validated_manifest_sha256": manifest_sha256,
            "activation_sha256": activation_sha256,
            "reason": reason,
            "activated": True,
            "verdict": "USGS_SOIL_HOOK_ACTIVATED_OPERATIONAL",
            "n_species_total": validated.get("n_species_total"),
            "n_calls_success": validated.get("n_calls_success"),
            "v30_lock_inviolate": True,
            "drift_zero": True,
            "no_engine_recompute_triggered": True,
        }
        persisted["audit_persisted"] = persist_audit(audit_payload)

    activation_payload["persisted_paths"] = persisted
    activation_payload["elapsed_s"] = round(time.time() - t0, 3)
    return activation_payload


def get_usgs_soil_hook_status() -> Dict[str, Any]:
    """État actuel du hook USGS Soil (read-only)."""
    if not USGS_SOIL_HOOK_ACTIVATION_PATH.exists():
        return {
            "manifest_id": "USGS_SOIL_HOOK_STATUS_Ω",
            "ordre": "P1_USGS_SOIL_HOOK_ACTIVATE_Ω",
            "current_status": "NOT_ACTIVATED",
            "v30_lock": "INVIOLÉ",
            "scanned_at_utc": _utc_now(),
        }
    state = json.loads(
        USGS_SOIL_HOOK_ACTIVATION_PATH.read_text(encoding="utf-8"))
    last = (state["history"][-1]
            if state.get("history") else None)
    return {
        "manifest_id": "USGS_SOIL_HOOK_STATUS_Ω",
        "ordre": "P1_USGS_SOIL_HOOK_ACTIVATE_Ω",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "current_status": (
            "ACTIVATED_OPERATIONAL" if last
            and last.get("activated") else "NOT_ACTIVATED"),
        "n_activations_history": state.get("n_activations", 0),
        "last_activation_sha256": state.get(
            "last_activation_sha256"),
        "last_validated_manifest_sha256": state.get(
            "last_validated_manifest_sha256"),
        "last_updated_utc": state.get("last_updated_utc"),
        "last_activation": last,
        "overlay_path": str(USGS_SOIL_HOOK_ACTIVATION_PATH),
        "overlay_size_bytes": (
            USGS_SOIL_HOOK_ACTIVATION_PATH.stat().st_size),
        "v30_lock": "INVIOLÉ",
        "scanned_at_utc": _utc_now(),
    }


__all__ = [
    "USGS_SOIL_ROOT",
    "USGS_SOIL_VALIDATION_PATH",
    "USGS_SOIL_HOOK_ACTIVATION_PATH",
    "SOILGRIDS_PROPERTIES_REGISTRY",
    "TERRESTRIAL_OFFSETS_CARDINAL",
    "validate_usgs_soil_per_species",
    "activate_usgs_soil_hook",
    "get_usgs_soil_hook_status",
]

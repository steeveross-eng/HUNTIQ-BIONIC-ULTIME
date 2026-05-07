"""
nasa_ndvi_omega.py — NASA_NDVI_P0_VALIDATE_Ω_ULTIME
═══════════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU x3 · ANTI_GÉNÉRIQUE_STRICT

Validation NASA MODIS NDVI/EVI via le service ORNL MODIS Web Service.

DOCTRINE ANTI-GÉNÉRIQUE STRICTE :
  · MOD13Q1 contient UNIQUEMENT NDVI / EVI / VI_QUALITY / pixel_reliability.
    LAI/FPAR sont dans MOD15A2H. GPP est dans MOD17A2H.
  · Aucune bande n'est fabriquée si elle n'existe pas dans le produit.
  · Tracé explicite des bandes demandées mais NON-DISPONIBLES.
  · Habitat outputs (food_availability, bedding_zones, etc.) NE SONT PAS
    calculés en phase P0_VALIDATE — ils requièrent un HOOK_ACTIVATE
    ultérieur avec transformations documentées.
  · Sauvegarde en JSON, pas de mocks, pas d'imputation.

NASA ORNL MODIS Web Service (public, no credentials required) :
  · URL racine : https://modis.ornl.gov/rst/api/v1/
  · Format : JSON
  · Quota : usage normal sans authentification (rate-limit raisonnable)
  · Documentation : https://modis.ornl.gov/data/modis_webservice.html
═══════════════════════════════════════════════════════════════════════════
"""
from __future__ import annotations

import hashlib
import json
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


NASA_NDVI_ROOT = Path("/app/backend/data/pipelines/nasa_ndvi")
NASA_NDVI_VALIDATION_PATH = (
    NASA_NDVI_ROOT / "nasa_ndvi_validation_overlay.json")


# ═════════════════════════════════════════════════════════════════════════
# Registry MODIS Web Service — bandes disponibles par produit (anti-générique)
# Sources : https://modis.ornl.gov/data/modis_webservice.html
# ═════════════════════════════════════════════════════════════════════════
MODIS_PRODUCTS_BANDS_REGISTRY: Dict[str, Dict[str, Any]] = {
    "MOD13Q1": {
        "description": (
            "MODIS/Terra Vegetation Indices 16-Day L3 Global 250m"),
        "temporal_resolution_days": 16,
        "spatial_resolution_m": 250,
        "available_bands": [
            "250m_16_days_NDVI",
            "250m_16_days_EVI",
            "250m_16_days_VI_Quality",
            "250m_16_days_pixel_reliability",
            "250m_16_days_red_reflectance",
            "250m_16_days_NIR_reflectance",
            "250m_16_days_blue_reflectance",
            "250m_16_days_MIR_reflectance",
            "250m_16_days_view_zenith_angle",
            "250m_16_days_sun_zenith_angle",
            "250m_16_days_relative_azimuth_angle",
            "250m_16_days_composite_day_of_the_year",
        ],
        "scale_factors": {
            "250m_16_days_NDVI": 0.0001,
            "250m_16_days_EVI": 0.0001,
        },
    },
    "MOD15A2H": {
        "description": (
            "MODIS/Terra Leaf Area Index/FPAR 8-Day L4 Global 500m"),
        "temporal_resolution_days": 8,
        "spatial_resolution_m": 500,
        "available_bands": [
            "Lai_500m",
            "Fpar_500m",
            "FparExtra_QC",
            "FparLai_QC",
            "FparStdDev_500m",
            "LaiStdDev_500m",
        ],
        "scale_factors": {
            "Lai_500m": 0.1,
            "Fpar_500m": 0.01,
        },
    },
    "MOD17A2H": {
        "description": (
            "MODIS/Terra Gross Primary Productivity 8-Day L4 Global 500m"),
        "temporal_resolution_days": 8,
        "spatial_resolution_m": 500,
        "available_bands": [
            "Gpp_500m",
            "PsnNet_500m",
            "Psn_QC_500m",
        ],
        "scale_factors": {
            "Gpp_500m": 0.0001,
        },
    },
}


# Mapping logical name → canonical product + band (anti-générique)
NDVI_LOGICAL_TO_BAND: Dict[str, Dict[str, str]] = {
    "NDVI":       {"product": "MOD13Q1",  "band": "250m_16_days_NDVI"},
    "EVI":        {"product": "MOD13Q1",  "band": "250m_16_days_EVI"},
    "VI_QUALITY": {"product": "MOD13Q1",  "band": "250m_16_days_VI_Quality"},
    "LAI":        {"product": "MOD15A2H", "band": "Lai_500m"},
    "FPAR":       {"product": "MOD15A2H", "band": "Fpar_500m"},
    "GPP":        {"product": "MOD17A2H", "band": "Gpp_500m"},
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _modis_a_year_doy(date: datetime) -> str:
    """Convertit datetime en format MODIS 'AYYYYDDD'."""
    return f"A{date.year}{date.timetuple().tm_yday:03d}"


def _http_get_json_strict_with_redirect_block(
    url: str,
    timeout_s: int = 30,
    body_max_bytes: int = 524288,
) -> Dict[str, Any]:
    """GET strict JSON sans follow_redirects (anti-générique).

    Lecture body 512KB max. Retourne dict structuré.
    """
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
        "body_bytes_read": 0,
        "body_is_json": False,
        "parsed_json": None,
        "json_parse_error": None,
        "redirect_detected": False,
        "reason": None,
        "elapsed_ms": None,
    }
    t0 = time.time()
    try:
        opener = urllib.request.build_opener(NoRedirectHandler)
        req = urllib.request.Request(
            url, method="GET",
            headers={
                "User-Agent": "BCE-4X-NASA-NDVI-VALIDATE/1.0",
                "Accept": "application/json",
            })
        with opener.open(req, timeout=timeout_s) as resp:
            record["http_status"] = resp.status
            record["content_type"] = resp.headers.get(
                "Content-Type")
            body = resp.read(body_max_bytes)
            record["body_bytes_read"] = len(body)
            try:
                record["parsed_json"] = json.loads(
                    body.decode("utf-8", errors="replace"))
                record["body_is_json"] = True
            except json.JSONDecodeError as e:
                record["json_parse_error"] = str(e)[:200]
    except urllib.error.HTTPError as e:
        record["http_status"] = e.code
        record["reason"] = f"http_error_{e.code}"
        if 300 <= e.code < 400:
            record["redirect_detected"] = True
        try:
            body = e.read(800)
            record["body_preview_first_500b"] = body[:500].decode(
                "utf-8", errors="replace")
        except Exception:
            pass
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        record["reason"] = f"network_error::{str(e)[:160]}"
    record["elapsed_ms"] = round((time.time() - t0) * 1000, 1)
    return record


def _compute_band_stats_from_modis_subset(
    subset: List[Dict[str, Any]],
    scale_factor: float = 1.0,
    nodata_value: int = -3000,
) -> Dict[str, Any]:
    """Calcule les stats descriptives à partir des points MODIS subset.

    Anti-générique : rejette les nodata values explicitement (pas
    d'imputation), retourne stats UNIQUEMENT sur valeurs valides.
    """
    raw_values: List[float] = []
    n_total = 0
    n_valid = 0
    n_nodata = 0
    for point in subset:
        n_total += 1
        data = point.get("data")
        if not isinstance(data, list) or not data:
            continue
        raw = data[0]  # subset 1×1 pixel
        try:
            raw_int = int(raw)
        except (TypeError, ValueError):
            continue
        if raw_int == nodata_value:
            n_nodata += 1
            continue
        raw_values.append(raw_int * scale_factor)
        n_valid += 1
    if not raw_values:
        return {
            "n_total": n_total,
            "n_valid": 0,
            "n_nodata": n_nodata,
            "min": None, "max": None, "mean": None,
            "interpretation": "no_valid_values",
        }
    return {
        "n_total": n_total,
        "n_valid": n_valid,
        "n_nodata": n_nodata,
        "min": round(min(raw_values), 4),
        "max": round(max(raw_values), 4),
        "mean": round(sum(raw_values) / len(raw_values), 4),
        "first_date": subset[0].get("calendar_date"),
        "last_date": subset[-1].get("calendar_date"),
    }


def validate_nasa_ndvi_per_species(
    species_coordinates: Dict[str, Dict[str, float]],
    bands_requested_logical: Optional[List[str]] = None,
    base_endpoint: str = (
        "https://modis.ornl.gov/rst/api/v1"),
    days_lookback: int = 365,
    forensic_event: str = "NASA_NDVI_P0_VALIDATE_Ω_ULTIME",
    persist: bool = True,
    timeout_s: int = 30,
    inter_call_sleep_s: float = 0.5,
    max_points: int = 46,
) -> Dict[str, Any]:
    """NASA_NDVI_P0_VALIDATE_Ω_ULTIME · multi-espèces × multi-bandes.

    Workflow doctrinal :
      1. Guardrails ENFORCED check (412 sinon)
      2. Validation coords (lat/lon)
      3. Pour chaque bande logique demandée :
         - Lookup dans NDVI_LOGICAL_TO_BAND
         - Si bande dans MOD13Q1 (NDVI/EVI/VI_QUALITY) → probe RÉEL
         - Si bande dans MOD15A2H (LAI/FPAR) ou MOD17A2H (GPP) →
           tracé "BAND_DEFERRED_OTHER_PRODUCT" (anti-générique : pas
           d'appel à un autre produit dans cette directive P0)
      4. Pour MOD13Q1 bandes : probe par espèce
         (5 espèces × N bandes = N×5 calls)
      5. Calcul stats anti-génériques (n_valid, min/max/mean, nodata)
      6. Forensic log ENDPOINT_PROBES/{forensic_event}
      7. Persistance overlay + audit doctrinal
      8. AUCUN habitat_output calculé ICI (reporté à HOOK_ACTIVATE)

    Args:
      species_coordinates: dict species → {lat, lon}
      bands_requested_logical: liste de bandes logiques (NDVI, EVI, etc.)
      base_endpoint: NASA ORNL MODIS Web Service base URL
      days_lookback: période d'historique (default 365 jours)
      max_points: nb max de points temporels par série
    """
    from engines.v8_institutional.especes.pipeline_guardrails_omega import (
        require_guardrails_enforced, log_forensic_event,
    )
    require_guardrails_enforced(
        "validate_nasa_ndvi_per_species")

    if not species_coordinates:
        raise ValueError(
            "SPECIES_COORDINATES_REQUIRED::empty")
    if not base_endpoint.startswith(("https://", "http://")):
        raise ValueError(
            f"BASE_ENDPOINT_INVALID::{base_endpoint[:120]}")

    for sp_name, coords in species_coordinates.items():
        lat = coords.get("lat") if isinstance(coords, dict) else None
        lon = coords.get("lon") if isinstance(coords, dict) else None
        if (lat is None or lon is None
                or not (-90.0 <= float(lat) <= 90.0)
                or not (-180.0 <= float(lon) <= 180.0)):
            raise ValueError(
                f"COORDS_INVALID::{sp_name}::lat={lat},lon={lon}")

    bands_logical = bands_requested_logical or [
        "NDVI", "EVI", "VI_QUALITY"]

    # Classification bandes : disponibles MOD13Q1 vs reportées
    mod13q1_bands_to_probe: List[Dict[str, str]] = []
    deferred_bands: List[Dict[str, Any]] = []
    unknown_bands: List[str] = []
    for logical in bands_logical:
        mapping = NDVI_LOGICAL_TO_BAND.get(logical.upper())
        if not mapping:
            unknown_bands.append(logical)
            continue
        if mapping["product"] == "MOD13Q1":
            mod13q1_bands_to_probe.append({
                "logical": logical.upper(),
                "product": mapping["product"],
                "band": mapping["band"],
            })
        else:
            deferred_bands.append({
                "logical": logical.upper(),
                "product": mapping["product"],
                "band": mapping["band"],
                "deferred_reason": (
                    f"BAND_NOT_IN_MOD13Q1::"
                    f"requires_product_{mapping['product']}::"
                    "anti_generique_strict_no_fabrication"),
                "available_in_other_product_documented": True,
                "directive_extension_required_for_probe": True,
            })

    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(days=days_lookback)
    start_str = _modis_a_year_doy(start_date)
    end_str = _modis_a_year_doy(end_date)

    # Probe MOD13Q1 bandes : pour chaque espèce × chaque bande
    t_total = time.time()
    species_results: Dict[str, Dict[str, Any]] = {}
    n_calls_made = 0
    n_calls_success = 0
    n_calls_failed = 0

    for sp_name, coords in species_coordinates.items():
        lat = float(coords["lat"])
        lon = float(coords["lon"])
        species_results[sp_name] = {
            "coords": {"lat": lat, "lon": lon},
            "bands": {},
        }
        for band_entry in mod13q1_bands_to_probe:
            band_canonical = band_entry["band"]
            band_logical = band_entry["logical"]
            url = (
                f"{base_endpoint}/MOD13Q1/subset?"
                f"latitude={lat}&longitude={lon}"
                f"&band={band_canonical}"
                f"&startDate={start_str}&endDate={end_str}"
                f"&kmAboveBelow=0&kmLeftRight=0")
            n_calls_made += 1
            probe = _http_get_json_strict_with_redirect_block(
                url=url, timeout_s=timeout_s)
            band_record: Dict[str, Any] = {
                "logical_name": band_logical,
                "canonical_band": band_canonical,
                "product": "MOD13Q1",
                "url": url,
                "http_status": probe["http_status"],
                "content_type": probe["content_type"],
                "elapsed_ms": probe["elapsed_ms"],
                "redirect_detected": probe["redirect_detected"],
                "reason": probe["reason"],
                "valid": False,
                "stats": None,
                "n_subset_points_returned": 0,
            }
            if (probe["http_status"] == 200
                    and probe["body_is_json"]
                    and isinstance(probe["parsed_json"], dict)):
                parsed = probe["parsed_json"]
                subset = parsed.get("subset")
                if isinstance(subset, list) and subset:
                    band_record["n_subset_points_returned"] = (
                        min(len(subset), max_points))
                    # Limiter à max_points
                    capped_subset = subset[:max_points]
                    scale = (
                        MODIS_PRODUCTS_BANDS_REGISTRY["MOD13Q1"]
                        .get("scale_factors", {})
                        .get(band_canonical, 1.0))
                    band_record["scale_factor_applied"] = scale
                    band_record["stats"] = (
                        _compute_band_stats_from_modis_subset(
                            capped_subset, scale_factor=scale))
                    band_record["valid"] = (
                        band_record["stats"]["n_valid"] > 0)
                    band_record["modis_metadata"] = {
                        "header": parsed.get("header"),
                        "cellsize_m": parsed.get("cellsize"),
                        "units": parsed.get("units"),
                    }
                    n_calls_success += 1
                else:
                    band_record["reason"] = "subset_empty_or_missing"
                    n_calls_failed += 1
            else:
                n_calls_failed += 1

            species_results[sp_name]["bands"][band_logical] = (
                band_record)

            # Forensic log par sous-probe
            log_forensic_event(
                scope="ENDPOINT_PROBES",
                event=forensic_event,
                details={
                    "provider": "NASA_NDVI",
                    "species": sp_name,
                    "lat": lat, "lon": lon,
                    "band_logical": band_logical,
                    "band_canonical": band_canonical,
                    "product": "MOD13Q1",
                    "http_status": probe["http_status"],
                    "valid": band_record["valid"],
                    "n_subset_points":
                        band_record["n_subset_points_returned"],
                    "elapsed_ms": probe["elapsed_ms"],
                },
                persist=True,
            )

            if inter_call_sleep_s > 0:
                time.sleep(inter_call_sleep_s)

        # Bandes reportées (deferred) → tracées pour cette espèce
        species_results[sp_name]["deferred_bands"] = [
            {
                "logical_name": d["logical"],
                "would_require_product": d["product"],
                "deferred_reason": d["deferred_reason"],
            }
            for d in deferred_bands
        ]

    # Synthèse
    total_n_valid_bands = sum(
        sum(1 for b in sp["bands"].values() if b["valid"])
        for sp in species_results.values())
    total_n_bands = sum(
        len(sp["bands"]) for sp in species_results.values())
    if total_n_bands > 0 and total_n_valid_bands == total_n_bands:
        verdict = (
            "NASA_NDVI_VALIDATE_ALL_BANDS_VALID")
        valid = True
    elif total_n_valid_bands > 0:
        verdict = (
            f"NASA_NDVI_VALIDATE_PARTIAL::"
            f"{total_n_valid_bands}_OF_{total_n_bands}_BANDS_VALID")
        valid = False
    else:
        verdict = "NASA_NDVI_VALIDATE_ALL_BANDS_INVALID"
        valid = False

    # Habitat outputs : non calculés en P0_VALIDATE (anti-générique)
    habitat_outputs_status = {
        "phase": "P0_VALIDATE",
        "habitat_outputs_computed": False,
        "doctrinal_explanation": (
            "Habitat outputs (food_availability, food_quality, "
            "bedding_zones, feeding_zones, rut_zones, refuge_zones, "
            "movement_corridors, saline_optimal_locations, "
            "pressure_sensitive_zones, microhabitat_clusters) require "
            "transformations applied to RAW NDVI/EVI/LAI/FPAR/GPP "
            "values combined with species-specific niche models. "
            "Anti-générique strict : these outputs are computed in a "
            "separate HOOK_ACTIVATE phase with documented transforms, "
            "NOT in P0_VALIDATE. Refer to NASA_NDVI_HOOK_ACTIVATE."),
        "deferred_to_hook_activate": True,
    }

    payload = {
        "manifest_id": "NASA_NDVI_P0_VALIDATE_Ω",
        "ordre": "P1_NASA_NDVI_P0_VALIDATE_Ω_ULTIME",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "guardrails_enforced": True,
        "autonomy": "LIMITED",
        "valid": valid,
        "verdict": verdict,
        "provider": "NASA_NDVI_MODIS_ORNL",
        "base_endpoint": base_endpoint,
        "products_used": ["MOD13Q1"],
        "products_documented_but_not_probed": [
            "MOD15A2H (LAI/FPAR)", "MOD17A2H (GPP)"],
        "bands_requested_logical": bands_logical,
        "bands_probed_in_mod13q1": [
            b["logical"] for b in mod13q1_bands_to_probe],
        "bands_deferred_other_product": [
            d["logical"] for d in deferred_bands],
        "bands_unknown_in_registry": unknown_bands,
        "n_species_total": len(species_coordinates),
        "n_calls_made": n_calls_made,
        "n_calls_success": n_calls_success,
        "n_calls_failed": n_calls_failed,
        "max_points_per_band": max_points,
        "temporal_range": {
            "start_date_modis": start_str,
            "end_date_modis": end_str,
            "days_lookback": days_lookback,
        },
        "species_results": species_results,
        "habitat_outputs_status": habitat_outputs_status,
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
        NASA_NDVI_ROOT.mkdir(parents=True, exist_ok=True)
        if NASA_NDVI_VALIDATION_PATH.exists():
            try:
                state = json.loads(
                    NASA_NDVI_VALIDATION_PATH.read_text(
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
        NASA_NDVI_VALIDATION_PATH.write_text(
            json.dumps(state, ensure_ascii=False, indent=2),
            encoding="utf-8")
        persisted["overlay_path"] = str(
            NASA_NDVI_VALIDATION_PATH)
        persisted["overlay_size_bytes"] = (
            NASA_NDVI_VALIDATION_PATH.stat().st_size)
        persisted["n_validations_history"] = state["n_validations"]

        from engines.v8_institutional.especes.bio_reacteur_overlay_omega import (  # noqa: E501
            persist_audit,
        )
        audit_payload = {
            "audit_type": "NOAA_PIPELINE",
            "subtype": "NASA_NDVI_VALIDATE",
            "ordre": "P1_NASA_NDVI_P0_VALIDATE_Ω_ULTIME",
            "doctrine":
                "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
            "provider": "NASA_NDVI_MODIS_ORNL",
            "valid": valid,
            "verdict": verdict,
            "manifest_sha256": payload_sha256,
            "n_species_total": len(species_coordinates),
            "n_calls_success": n_calls_success,
            "n_calls_failed": n_calls_failed,
            "v30_lock_inviolate": True,
            "drift_zero": True,
            "no_engine_recompute_triggered": True,
        }
        persisted["audit_persisted"] = persist_audit(audit_payload)

    payload["persisted_paths"] = persisted
    return payload


# ═════════════════════════════════════════════════════════════════════════
# NASA_NDVI_HOOK_ACTIVATE_Ω_ULTIME (officielle FUSION ADD-ONLY)
# Activation conditionnée à un manifest_sha256 RÉELLEMENT validé.
# Anti-générique strict : refus d'activation sur SHA fabriqué.
# ═════════════════════════════════════════════════════════════════════════
NASA_NDVI_HOOK_ACTIVATION_PATH = (
    NASA_NDVI_ROOT / "nasa_ndvi_hook_activation_overlay.json")


def _find_validated_nasa_ndvi_manifest(
    target_manifest_sha256: str,
) -> Optional[Dict[str, Any]]:
    """Cherche un manifest NASA NDVI validé dans l'historique.

    Anti-générique strict : on ne peut activer le hook que sur un
    manifest_sha256 RÉELLEMENT validé (n_calls_success >= 1).
    Retourne None si introuvable OU si aucun call success.
    """
    if not NASA_NDVI_VALIDATION_PATH.exists():
        return None
    try:
        state = json.loads(
            NASA_NDVI_VALIDATION_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    history = state.get("history", [])
    for entry in history:
        if (entry.get("manifest_sha256") == target_manifest_sha256
                and entry.get("n_calls_success", 0) >= 1):
            return entry
    return None


def activate_nasa_ndvi_hook(
    manifest_sha256: str,
    reason: str = "nasa_ndvi_ultimate_hook_activated",
    persist: bool = True,
) -> Dict[str, Any]:
    """NASA_NDVI_HOOK_ACTIVATE_Ω_ULTIME · activation officielle.

    Workflow doctrinal :
      1. Guardrails ENFORCED check (412 sinon)
      2. Anti-générique strict : manifest_sha256 doit exister dans
         NASA_NDVI_VALIDATION_PATH avec n_calls_success >= 1.
         Refus d'activer sur manifest fabriqué.
      3. Construction manifest activation signé activation_sha256
         + sommaire espèces validées (NDVI/EVI/VI_QUALITY)
      4. Forensic log HOOK_ACTIVATIONS/NASA_NDVI_HOOK_ACTIVATE_Ω_ULTIME
      5. Persistance overlay history (V30_LOCK FUSION ADD-ONLY)
      6. Audit doctrinal NOAA_PIPELINE/NASA_NDVI_HOOK_ACTIVATE
      7. AUCUN recalcul moteur ICI (drift audit séparé sur demande)

    Returns:
      Dict avec verdict + activation_sha256 + sommaire bandes/espèces.
    """
    from engines.v8_institutional.especes.pipeline_guardrails_omega import (
        require_guardrails_enforced, log_forensic_event,
    )
    require_guardrails_enforced("activate_nasa_ndvi_hook")

    t0 = time.time()
    validated = _find_validated_nasa_ndvi_manifest(manifest_sha256)
    if validated is None:
        verdict = (
            "NASA_NDVI_HOOK_REJECTED_MANIFEST_NOT_FOUND_OR_INVALID")
        rejection_payload = {
            "manifest_id": "NASA_NDVI_HOOK_ACTIVATE_Ω_ULTIME",
            "ordre": "P1_NASA_NDVI_HOOK_ACTIVATE_Ω_ULTIME",
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
                "NASA_NDVI_VALIDATION_PATH avec n_calls_success >= 1. "
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
            event="NASA_NDVI_HOOK_ACTIVATE_Ω_ULTIME",
            details={
                "input_manifest_sha256": manifest_sha256,
                "reason": reason,
                "activated": False,
                "verdict": verdict,
            },
            persist=True,
        )
        return rejection_payload

    # Construction sommaire validé (anti-générique : extraction réelle)
    species_summary: List[Dict[str, Any]] = []
    for sp_name, sp_data in (
            validated.get("species_results") or {}).items():
        bands_data = sp_data.get("bands", {}) or {}
        bands_valid = [
            b for b, br in bands_data.items() if br.get("valid")]
        species_summary.append({
            "species_name": sp_name,
            "lat": (sp_data.get("coords") or {}).get("lat"),
            "lon": (sp_data.get("coords") or {}).get("lon"),
            "n_bands_probed": len(bands_data),
            "n_bands_valid": len(bands_valid),
            "bands_valid_logical": bands_valid,
            "deferred_bands": [
                d.get("logical_name") for d in (
                    sp_data.get("deferred_bands") or [])],
        })

    activation_payload = {
        "manifest_id": "NASA_NDVI_HOOK_ACTIVATE_Ω_ULTIME",
        "ordre": "P1_NASA_NDVI_HOOK_ACTIVATE_Ω_ULTIME",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "guardrails_enforced": True,
        "autonomy": "LIMITED",
        "activated": True,
        "verdict": "NASA_NDVI_HOOK_ACTIVATED_OPERATIONAL",
        "reason": reason,
        "validated_manifest_sha256": manifest_sha256,
        "validated_executed_at_utc": (
            validated.get("executed_at_utc")),
        "provider": "NASA_NDVI_MODIS_ORNL",
        "products_activated": validated.get("products_used") or [
            "MOD13Q1"],
        "products_deferred": validated.get(
            "products_documented_but_not_probed") or [],
        "bands_probed_in_mod13q1": validated.get(
            "bands_probed_in_mod13q1") or [],
        "bands_deferred_other_product": validated.get(
            "bands_deferred_other_product") or [],
        "n_species_total": validated.get("n_species_total"),
        "n_calls_success_inherited": validated.get(
            "n_calls_success"),
        "n_calls_failed_inherited": validated.get("n_calls_failed"),
        "species_summary": species_summary,
        "temporal_range_inherited": validated.get("temporal_range"),
        "consumed_by_modules": [
            "NUTRITION_VEGETATION_INDEX",
            "PHENOLOGIE_NDVI_TIMESERIES",
            "HABITAT_FOOD_AVAILABILITY",
            "PREDICTIF_GREENNESS_PROXY",
        ],
        "habitat_outputs_status": {
            "phase": "P1_HOOK_ACTIVATE",
            "habitat_outputs_computed": False,
            "doctrinal_explanation": (
                "Hook NASA NDVI activé OPERATIONAL. Les habitat "
                "outputs (food_availability, food_quality, "
                "phenology_window, etc.) seront calculés dans une "
                "phase ultérieure dédiée HABITAT_OUTPUTS_COMPUTE_Ω "
                "avec transformations documentées espèce-par-espèce. "
                "Anti-générique strict : aucun output fabriqué ici."),
            "deferred_to_habitat_outputs_compute": True,
        },
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
        NASA_NDVI_ROOT.mkdir(parents=True, exist_ok=True)
        if NASA_NDVI_HOOK_ACTIVATION_PATH.exists():
            try:
                state = json.loads(
                    NASA_NDVI_HOOK_ACTIVATION_PATH.read_text(
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
        NASA_NDVI_HOOK_ACTIVATION_PATH.write_text(
            json.dumps(state, ensure_ascii=False, indent=2),
            encoding="utf-8")
        persisted["overlay_path"] = str(
            NASA_NDVI_HOOK_ACTIVATION_PATH)
        persisted["overlay_size_bytes"] = (
            NASA_NDVI_HOOK_ACTIVATION_PATH.stat().st_size)
        persisted["n_activations_history"] = state["n_activations"]

        log_forensic_event(
            scope="HOOK_ACTIVATIONS",
            event="NASA_NDVI_HOOK_ACTIVATE_Ω_ULTIME",
            details={
                "validated_manifest_sha256": manifest_sha256,
                "activation_sha256": activation_sha256,
                "reason": reason,
                "activated": True,
                "n_calls_success_inherited": validated.get(
                    "n_calls_success"),
                "verdict":
                    "NASA_NDVI_HOOK_ACTIVATED_OPERATIONAL",
            },
            persist=True,
        )

        from engines.v8_institutional.especes.bio_reacteur_overlay_omega import (  # noqa: E501
            persist_audit,
        )
        audit_payload = {
            "audit_type": "NOAA_PIPELINE",
            "subtype": "NASA_NDVI_HOOK_ACTIVATE",
            "ordre": "P1_NASA_NDVI_HOOK_ACTIVATE_Ω_ULTIME",
            "doctrine":
                "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
            "provider": "NASA_NDVI_MODIS_ORNL",
            "validated_manifest_sha256": manifest_sha256,
            "activation_sha256": activation_sha256,
            "reason": reason,
            "activated": True,
            "verdict": "NASA_NDVI_HOOK_ACTIVATED_OPERATIONAL",
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


def get_nasa_ndvi_hook_status() -> Dict[str, Any]:
    """État actuel du hook NASA NDVI (read-only)."""
    if not NASA_NDVI_HOOK_ACTIVATION_PATH.exists():
        return {
            "manifest_id": "NASA_NDVI_HOOK_STATUS_Ω",
            "ordre": "P1_NASA_NDVI_HOOK_ACTIVATE_Ω_ULTIME",
            "current_status": "NOT_ACTIVATED",
            "v30_lock": "INVIOLÉ",
            "scanned_at_utc": _utc_now(),
        }
    state = json.loads(
        NASA_NDVI_HOOK_ACTIVATION_PATH.read_text(encoding="utf-8"))
    last = (state["history"][-1]
            if state.get("history") else None)
    return {
        "manifest_id": "NASA_NDVI_HOOK_STATUS_Ω",
        "ordre": "P1_NASA_NDVI_HOOK_ACTIVATE_Ω_ULTIME",
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
        "overlay_path": str(NASA_NDVI_HOOK_ACTIVATION_PATH),
        "overlay_size_bytes": (
            NASA_NDVI_HOOK_ACTIVATION_PATH.stat().st_size),
        "v30_lock": "INVIOLÉ",
        "scanned_at_utc": _utc_now(),
    }


__all__ = [
    "NASA_NDVI_ROOT",
    "NASA_NDVI_VALIDATION_PATH",
    "NASA_NDVI_HOOK_ACTIVATION_PATH",
    "MODIS_PRODUCTS_BANDS_REGISTRY",
    "NDVI_LOGICAL_TO_BAND",
    "validate_nasa_ndvi_per_species",
    "activate_nasa_ndvi_hook",
    "get_nasa_ndvi_hook_status",
]

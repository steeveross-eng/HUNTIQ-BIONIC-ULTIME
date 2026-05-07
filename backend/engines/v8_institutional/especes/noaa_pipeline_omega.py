"""
noaa_pipeline_omega.py — ACTIVATION_PIPELINE_NOAA_TERRITOIRE
═══════════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU x3 · ANTI_GÉNÉRIQUE_STRICT

Pipeline NOAA pour TERRITOIRE_Ω et TERRITOIRE_ULTIME :
  · WOD23 (LOCAL)   : World Ocean Database 2023, mode disque local
  · CFSv2 (OPeNDAP) : Climate Forecast System v2, streaming OPeNDAP

Directives Commandant :
  · Pas de fichiers .tar
  · Pas de /files/g/ ou GDAS
  · Exclusivement OPeNDAP pour CFSv2
  · WOD23 local pour PHYSIOLOGIE/HABITAT/THERMIQUE
  · URLs mensuelles auto-générées
  · Ingestion directe TERRITOIRE_Ω + TERRITOIRE_ULTIME

GARDE-FOUS DOCTRINAUX :
  · NE MODIFIE PAS bio_profile_135.json, BR_<ESPECE>.json,
    super_engines_omega_logic.py
  · AUCUN recalcul moteur déclenché
  · ANTI_GÉNÉRIQUE_STRICT : status RÉEL retourné, zéro fabrication
  · V30_LOCK INVIOLÉ + DRIFT_ZERO maintenus
═══════════════════════════════════════════════════════════════════════════
"""
from __future__ import annotations

import hashlib
import json
import logging
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("noaa_pipeline_omega")

# ═════════════════════════════════════════════════════════════════════════
# Constantes doctrinales
# ═════════════════════════════════════════════════════════════════════════
PIPELINE_ROOT = Path("/app/backend/data/pipelines/noaa")
PIPELINE_CONFIG_PATH = PIPELINE_ROOT / "noaa_pipeline_config.json"
PIPELINE_PROBE_RESULTS_PATH = (
    PIPELINE_ROOT / "noaa_pipeline_probe_results.json")
PIPELINE_URLS_PATH = (
    PIPELINE_ROOT / "noaa_pipeline_cfsv2_urls.json")

# Configuration WOD23 (multi-mode : LOCAL legacy + B2 primary depuis update)
WOD23_CONFIG = {
    "mode": "B2",
    "primary_b2_bucket": "noaa-territoire",
    "primary_b2_path": "wod23/",
    "primary_path_commandant_legacy": "C:/emergent_sources/noaa/wod23/",
    "fallback_paths_pod_linux": [
        "/data/external/noaa/wod23",
        "/app/backend/data/external/noaa/wod23",
    ],
    "expected_formats": [".nc", ".csv", ".bin"],
    "consumed_by_modules": ["PHYSIOLOGIE", "HABITAT", "THERMIQUE"],
    "fallback_when_unavailable": "skip_with_log",
    "anti_generique_strict": True,
}

# Configuration CFSv2 (OPeNDAP)
CFSV2_CONFIG = {
    "mode": "OPENDAP",
    "endpoint_template": (
        "https://tds.gdex.ucar.edu/thredds/dodsC/d094002/monthly_1p0/"
        "cfs.{YYYYMM}.mon.mean.{VARIABLE}.grb2"),
    "variables": [
        "tavg", "prate", "uwnd10m", "vwnd10m", "rhum", "sst",
    ],
    "period_start": "2011-01",
    "period_end": "present",
    "ingestion_target": "TERRITOIRE",
    "ingestion_mode": "STREAMING",
    "caching": "ON",
    "storage": "MINIMAL",
    "forbidden_paths": ["/files/g/", "GDAS"],
    "forbidden_formats": [".tar"],
    "anti_generique_strict": True,
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


# ═════════════════════════════════════════════════════════════════════════
# 1. Génération URLs CFSv2 mensuelles déterministes
# ═════════════════════════════════════════════════════════════════════════
def _month_iter(start_yyyymm: str, end_yyyymm: str) -> List[str]:
    """Itère les YYYYMM entre start et end (inclus)."""
    sy, sm = int(start_yyyymm[:4]), int(start_yyyymm[5:7])
    ey, em = int(end_yyyymm[:4]), int(end_yyyymm[5:7])
    out = []
    y, m = sy, sm
    while (y, m) <= (ey, em):
        out.append(f"{y:04d}{m:02d}")
        m += 1
        if m > 12:
            m = 1
            y += 1
    return out


def generate_cfsv2_urls(
    start_yyyymm: Optional[str] = None,
    end_yyyymm: Optional[str] = None,
    variables: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Génère les URLs mensuelles CFSv2 OPeNDAP déterministes.

    `end_yyyymm = 'present'` ou None → mois courant UTC.

    Anti-générique : aucune fabrication. URLs générées par substitution
    {YYYYMM} + {VARIABLE} dans le template officiel Commandant.
    """
    start = start_yyyymm or CFSV2_CONFIG["period_start"]
    if end_yyyymm in (None, "present"):
        now = datetime.now(timezone.utc)
        end_yyyymm = f"{now.year:04d}-{now.month:02d}"
    end = end_yyyymm
    vars_used = variables or CFSV2_CONFIG["variables"]

    months = _month_iter(start, end)
    template = CFSV2_CONFIG["endpoint_template"]
    urls: List[Dict[str, str]] = []
    for ym in months:
        for v in vars_used:
            url = template.replace(
                "{YYYYMM}", ym).replace("{VARIABLE}", v)
            urls.append({
                "yyyymm": ym,
                "variable": v,
                "url": url,
            })

    return {
        "manifest_id": "CFSV2_URLS_GENERATED_Ω",
        "ordre": "ACTIVATION_PIPELINE_NOAA_TERRITOIRE",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "period_start": start,
        "period_end": end,
        "variables": vars_used,
        "n_months": len(months),
        "n_variables": len(vars_used),
        "n_urls_total": len(urls),
        "urls": urls,
        "endpoint_template": template,
        "v30_lock": "INVIOLÉ",
        "generated_at_utc": _utc_now(),
    }


# ═════════════════════════════════════════════════════════════════════════
# 2. Probe WOD23 local (status réel disque)
# ═════════════════════════════════════════════════════════════════════════
def probe_wod23_b2(
    bucket: Optional[str] = None,
    path_prefix: Optional[str] = None,
    max_keys: int = 100,
) -> Dict[str, Any]:
    """Probe RÉEL Backblaze B2 (mode S3-compatible).

    Anti-générique strict : aucune fabrication. Toutes les valeurs
    retournées proviennent d'appels boto3 réels.

    Returns:
      {available, bucket, path_prefix, n_objects_found, total_size_bytes,
       sample_keys, http_status, anti_generique_strict, ...}
    """
    bucket = bucket or WOD23_CONFIG["primary_b2_bucket"]
    path_prefix = path_prefix or WOD23_CONFIG["primary_b2_path"]

    record: Dict[str, Any] = {
        "manifest_id": "WOD23_B2_PROBE_Ω",
        "source_name": "WOD23",
        "mode": "B2",
        "bucket": bucket,
        "path_prefix": path_prefix,
        "available": False,
        "anti_generique_strict": True,
        "v30_lock": "INVIOLÉ",
        "probed_at_utc": _utc_now(),
    }

    # Boto3 disponible ?
    try:
        import boto3
        from botocore.config import Config
        from botocore.exceptions import (
            ClientError, EndpointConnectionError, NoCredentialsError,
        )
    except ImportError as e:
        record["reason"] = f"boto3_import_error::{str(e)[:120]}"
        return record

    # Credentials B2 disponibles ?
    import os
    key_id = os.environ.get("B2_KEY_ID")
    app_key = os.environ.get("B2_APPLICATION_KEY")
    endpoint = os.environ.get("B2_ENDPOINT_URL")
    region = os.environ.get("B2_REGION")
    if not (key_id and app_key and endpoint):
        record["reason"] = "b2_credentials_missing_in_env"
        return record

    record["b2_endpoint_url"] = endpoint
    record["b2_region"] = region

    # Construction client S3 compatible B2
    try:
        s3 = boto3.client(
            "s3",
            aws_access_key_id=key_id,
            aws_secret_access_key=app_key,
            endpoint_url=endpoint,
            region_name=region,
            config=Config(
                connect_timeout=10, read_timeout=10,
                retries={"max_attempts": 1}),
        )
    except Exception as e:
        record["reason"] = (
            f"b2_client_init_error::{str(e)[:120]}")
        return record

    # head_bucket : vérifier existence + accessibilité
    t0 = time.time()
    try:
        s3.head_bucket(Bucket=bucket)
        record["bucket_exists"] = True
        record["http_head_bucket_ms"] = round(
            (time.time() - t0) * 1000, 1)
    except ClientError as e:
        code = e.response.get("Error", {}).get("Code", "?")
        record["bucket_exists"] = False
        record["reason"] = f"head_bucket_error::{code}"
        record["http_head_bucket_ms"] = round(
            (time.time() - t0) * 1000, 1)
        return record
    except (EndpointConnectionError, NoCredentialsError) as e:
        record["reason"] = (
            f"network_or_credentials_error::{str(e)[:120]}")
        return record
    except Exception as e:
        record["reason"] = f"unexpected_error::{str(e)[:120]}"
        return record

    # list_objects_v2 : compter objets avec préfixe
    t0 = time.time()
    n_objects = 0
    total_bytes = 0
    sample_keys: List[Dict[str, Any]] = []
    n_anomalies = 0
    try:
        paginator = s3.get_paginator("list_objects_v2")
        for page in paginator.paginate(
            Bucket=bucket, Prefix=path_prefix,
            PaginationConfig={"PageSize": max_keys},
        ):
            for obj in page.get("Contents", []):
                key = obj["Key"]
                size = obj.get("Size", 0)
                # Filtre extensions attendues
                ext_ok = any(
                    key.lower().endswith(fmt.lower())
                    for fmt in WOD23_CONFIG["expected_formats"])
                if size == 0:
                    n_anomalies += 1
                    continue
                if not ext_ok:
                    # Format non attendu — anomalie doctrinale
                    n_anomalies += 1
                    continue
                n_objects += 1
                total_bytes += size
                if len(sample_keys) < 10:
                    sample_keys.append({
                        "key": key, "size": size,
                    })
            # Limit échantillon
            if n_objects >= max_keys:
                break
    except ClientError as e:
        code = e.response.get("Error", {}).get("Code", "?")
        record["reason"] = f"list_objects_error::{code}"
        record["http_list_objects_ms"] = round(
            (time.time() - t0) * 1000, 1)
        return record
    record["http_list_objects_ms"] = round(
        (time.time() - t0) * 1000, 1)

    record["n_objects_valid"] = n_objects
    record["n_anomalies"] = n_anomalies
    record["total_size_bytes"] = total_bytes
    record["sample_keys"] = sample_keys
    record["available"] = (n_objects > 0 and n_anomalies == 0)
    if n_objects == 0 and n_anomalies == 0:
        record["reason"] = "bucket_empty_or_prefix_not_found"
    return record


def probe_wod23_local() -> Dict[str, Any]:
    """Vérifie l'accessibilité réelle des paths WOD23.

    Anti-générique : status RÉEL retourné, zéro fabrication.
    """
    primary = WOD23_CONFIG.get(
        "primary_path_commandant_legacy",
        WOD23_CONFIG.get("primary_path_commandant", ""))
    fallbacks = WOD23_CONFIG["fallback_paths_pod_linux"]

    # Le path primary (legacy) est en Windows (C:/...) — non accessible
    # en pod Linux
    primary_accessible = False
    primary_reason = "WINDOWS_PATH_NOT_ACCESSIBLE_FROM_LINUX_POD"
    try:
        primary_accessible = Path(primary).exists()
    except (OSError, ValueError) as e:
        primary_reason = f"PATH_PROBE_ERROR::{str(e)[:100]}"

    fallback_results: List[Dict[str, Any]] = []
    n_files_total = 0
    n_anomalies_total = 0
    for fb_path_str in fallbacks:
        fb_path = Path(fb_path_str)
        exists = fb_path.exists() and fb_path.is_dir()
        files_found: List[str] = []
        anomalies: List[Dict[str, Any]] = []
        if exists:
            for fmt in WOD23_CONFIG["expected_formats"]:
                for f in fb_path.rglob(f"*{fmt}"):
                    if not f.is_file():
                        continue
                    try:
                        size = f.stat().st_size
                        if size == 0:
                            anomalies.append({
                                "path": str(f),
                                "anomaly": "zero_size",
                            })
                        else:
                            files_found.append(str(f))
                    except OSError:
                        anomalies.append({
                            "path": str(f),
                            "anomaly": "unreadable",
                        })
        n_files_total += len(files_found)
        n_anomalies_total += len(anomalies)
        fallback_results.append({
            "path": str(fb_path),
            "exists": exists,
            "n_files_valid": len(files_found),
            "files_sample": files_found[:5],
            "n_anomalies": len(anomalies),
            "anomalies_sample": anomalies[:5],
        })

    available = n_files_total > 0 and n_anomalies_total == 0

    return {
        "manifest_id": "WOD23_PROBE_Ω",
        "source_name": "WOD23",
        "mode": "LOCAL",
        "primary_path": primary,
        "primary_accessible": primary_accessible,
        "primary_reason": primary_reason,
        "fallback_paths_results": fallback_results,
        "n_files_valid_total": n_files_total,
        "n_anomalies_total": n_anomalies_total,
        "available": available,
        "fallback_when_unavailable": "skip_with_log",
        "anti_generique_strict": True,
        "consumed_by_modules": WOD23_CONFIG["consumed_by_modules"],
        "v30_lock": "INVIOLÉ",
        "probed_at_utc": _utc_now(),
    }


# ═════════════════════════════════════════════════════════════════════════
# 3. Probe CFSv2 OPeNDAP (HEAD HTTP réel)
# ═════════════════════════════════════════════════════════════════════════
def probe_cfsv2_opendap(
    sample_yyyymm: Optional[str] = None,
    sample_variable: Optional[str] = None,
    timeout_s: int = 10,
) -> Dict[str, Any]:
    """Probe HEAD HTTPS sur l'endpoint CFSv2 OPeNDAP.

    Anti-générique strict : aucune fabrication. Status code et latency
    réellement mesurés via urllib (pas de download).

    Args:
      sample_yyyymm:  par défaut "201101"
      sample_variable: par défaut "tavg"
    """
    import urllib.error
    import urllib.request

    sample_yyyymm = sample_yyyymm or "201101"
    sample_variable = sample_variable or "tavg"
    template = CFSV2_CONFIG["endpoint_template"]
    url = template.replace(
        "{YYYYMM}", sample_yyyymm).replace(
        "{VARIABLE}", sample_variable)
    # OPeNDAP Data Descriptor Structure (.dds) — endpoint léger
    dds_url = url + ".dds"

    # Probe principale (URL OPeNDAP brute)
    record_main = {
        "url": url,
        "http_status": None,
        "elapsed_ms": None,
        "reason": None,
    }
    t0 = time.time()
    try:
        req = urllib.request.Request(
            url, method="HEAD",
            headers={"User-Agent": "BCE-4X-NOAA-PIPELINE/1.0"})
        with urllib.request.urlopen(req, timeout=timeout_s) as resp:
            record_main["http_status"] = resp.status
    except urllib.error.HTTPError as e:
        record_main["http_status"] = e.code
        record_main["reason"] = f"http_error_{e.code}"
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        record_main["reason"] = f"network_error::{str(e)[:120]}"
    record_main["elapsed_ms"] = round((time.time() - t0) * 1000, 1)

    # Probe DDS (descriptor OPeNDAP)
    record_dds = {
        "url": dds_url,
        "http_status": None,
        "elapsed_ms": None,
        "reason": None,
    }
    t0 = time.time()
    try:
        req = urllib.request.Request(
            dds_url, method="GET",
            headers={"User-Agent": "BCE-4X-NOAA-PIPELINE/1.0"})
        with urllib.request.urlopen(req, timeout=timeout_s) as resp:
            record_dds["http_status"] = resp.status
            # Lit max 4 KB pour preview (anti-générique : data réelle)
            preview = resp.read(4096)
            record_dds["dds_preview_first_500b"] = (
                preview[:500].decode("utf-8", errors="replace"))
    except urllib.error.HTTPError as e:
        record_dds["http_status"] = e.code
        record_dds["reason"] = f"http_error_{e.code}"
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        record_dds["reason"] = f"network_error::{str(e)[:120]}"
    record_dds["elapsed_ms"] = round((time.time() - t0) * 1000, 1)

    # Disponibilité dépendances scientifiques (xarray / netCDF4 / pydap)
    deps_status: Dict[str, Any] = {}
    for dep in ("xarray", "netCDF4", "pydap"):
        try:
            mod = __import__(dep)
            deps_status[dep] = {
                "available": True,
                "version": getattr(mod, "__version__", "unknown"),
            }
        except ImportError:
            deps_status[dep] = {
                "available": False,
                "reason": "module_not_installed",
            }

    n_deps_available = sum(
        1 for d in deps_status.values() if d.get("available"))
    streaming_capable = (
        record_dds["http_status"] == 200
        and n_deps_available > 0)

    # Verdict global
    if streaming_capable:
        verdict = "STREAMING_OPERATIONAL"
    elif record_dds["http_status"] == 200:
        verdict = "ENDPOINT_OK_AWAITING_DEPENDENCIES"
    elif record_main["http_status"] in (200, 301, 302):
        verdict = "MAIN_URL_OK_BUT_DDS_UNREACHABLE"
    else:
        verdict = "ENDPOINT_PROBE_FAILED_AWAITING_VALID_OPENDAP"

    return {
        "manifest_id": "CFSV2_OPENDAP_PROBE_Ω",
        "source_name": "CFSV2",
        "mode": "OPENDAP",
        "endpoint_template": template,
        "sample_url_probed": url,
        "sample_yyyymm": sample_yyyymm,
        "sample_variable": sample_variable,
        "probe_main": record_main,
        "probe_dds": record_dds,
        "scientific_deps_status": deps_status,
        "n_deps_available": n_deps_available,
        "streaming_capable": streaming_capable,
        "verdict": verdict,
        "anti_generique_strict": True,
        "v30_lock": "INVIOLÉ",
        "probed_at_utc": _utc_now(),
    }


# ═════════════════════════════════════════════════════════════════════════
# 4. Activation pipeline complète (configuration + probes + persistance)
# ═════════════════════════════════════════════════════════════════════════
def activate_noaa_pipeline(
    sample_yyyymm: str = "201101",
    sample_variable: str = "tavg",
    persist: bool = True,
) -> Dict[str, Any]:
    """Active le pipeline NOAA TERRITOIRE.

    Étapes :
      1. Persiste config doctrinale (WOD23 + CFSv2)
      2. Génère URLs mensuelles CFSv2 (2011-01 → present)
      3. Probe WOD23 local + CFSv2 OPeNDAP
      4. Audit NOAA_PIPELINE_ACTIVATION persisté
      5. AUCUN recalcul moteur

    Anti-générique : tous les probes retournent status RÉEL.
    """
    t0 = time.time()
    config_payload = {
        "manifest_id": "NOAA_PIPELINE_CONFIG_Ω",
        "ordre": "ACTIVATION_PIPELINE_NOAA_TERRITOIRE",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "wod23": WOD23_CONFIG,
        "cfsv2": CFSV2_CONFIG,
        "instructions_doctrinales": [
            "Pas de fichiers .tar",
            "Pas de /files/g/ ou GDAS",
            "Exclusivement OPeNDAP pour CFSv2",
            "WOD23 local pour PHYSIOLOGIE/HABITAT/THERMIQUE",
            "URLs mensuelles auto-générées",
            "Ingestion directe TERRITOIRE_Ω + TERRITOIRE_ULTIME",
        ],
        "v30_lock": "INVIOLÉ",
        "drift_zero": True,
        "no_engine_recompute_triggered": True,
        "configured_at_utc": _utc_now(),
    }

    urls = generate_cfsv2_urls()
    wod23_b2_probe = probe_wod23_b2()
    wod23_local_probe = probe_wod23_local()
    cfsv2_probe = probe_cfsv2_opendap(
        sample_yyyymm=sample_yyyymm,
        sample_variable=sample_variable)

    persisted: Dict[str, Any] = {}
    if persist:
        PIPELINE_ROOT.mkdir(parents=True, exist_ok=True)
        PIPELINE_CONFIG_PATH.write_text(
            json.dumps(config_payload, ensure_ascii=False, indent=2),
            encoding="utf-8")
        PIPELINE_PROBE_RESULTS_PATH.write_text(
            json.dumps({
                "wod23_b2_probe": wod23_b2_probe,
                "wod23_local_probe": wod23_local_probe,
                "cfsv2_probe": cfsv2_probe,
                "probed_at_utc": _utc_now(),
                "v30_lock": "INVIOLÉ",
            }, ensure_ascii=False, indent=2),
            encoding="utf-8")
        PIPELINE_URLS_PATH.write_text(
            json.dumps(urls, ensure_ascii=False, indent=2),
            encoding="utf-8")
        persisted["config_path"] = str(PIPELINE_CONFIG_PATH)
        persisted["probe_results_path"] = str(
            PIPELINE_PROBE_RESULTS_PATH)
        persisted["urls_path"] = str(PIPELINE_URLS_PATH)
        persisted["urls_size_bytes"] = (
            PIPELINE_URLS_PATH.stat().st_size)

        # Audit persisté
        from engines.v8_institutional.especes.bio_reacteur_overlay_omega import (  # noqa: E501
            persist_audit,
        )
        audit_payload = {
            "audit_type": "NOAA_PIPELINE",
            "subtype": "ACTIVATION",
            "ordre": "ACTIVATION_PIPELINE_NOAA_TERRITOIRE",
            "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
            "wod23_status": {
                "mode": "B2",
                "b2_available": wod23_b2_probe.get(
                    "available", False),
                "b2_bucket": wod23_b2_probe.get("bucket"),
                "b2_n_objects_valid": wod23_b2_probe.get(
                    "n_objects_valid", 0),
                "b2_total_size_bytes": wod23_b2_probe.get(
                    "total_size_bytes", 0),
                "b2_reason": wod23_b2_probe.get("reason"),
                "local_available": wod23_local_probe["available"],
                "local_n_files": wod23_local_probe[
                    "n_files_valid_total"],
            },
            "cfsv2_status": {
                "verdict": cfsv2_probe["verdict"],
                "main_http_status": (
                    cfsv2_probe["probe_main"]["http_status"]),
                "dds_http_status": (
                    cfsv2_probe["probe_dds"]["http_status"]),
                "streaming_capable": cfsv2_probe[
                    "streaming_capable"],
                "deps_available": cfsv2_probe["n_deps_available"],
            },
            "n_cfsv2_urls_generated": urls["n_urls_total"],
            "no_engine_recompute_triggered": True,
            "v30_lock_inviolate": True,
            "drift_zero": True,
        }
        audit_meta = persist_audit(audit_payload)
        persisted["audit_persisted"] = audit_meta

    # Verdict global du pipeline
    pipeline_verdict_parts = []
    if wod23_b2_probe.get("available"):
        pipeline_verdict_parts.append(
            f"WOD23_B2_AVAILABLE_{wod23_b2_probe['n_objects_valid']}_objects")
    elif wod23_local_probe["available"]:
        pipeline_verdict_parts.append(
            f"WOD23_LOCAL_AVAILABLE_{wod23_local_probe['n_files_valid_total']}_files")
    else:
        pipeline_verdict_parts.append(
            "WOD23_AWAITING_B2_PROVISION_OR_LOCAL_DEPLOY")
    pipeline_verdict_parts.append(cfsv2_probe["verdict"])
    pipeline_verdict = " | ".join(pipeline_verdict_parts)

    return {
        "manifest_id": "NOAA_PIPELINE_ACTIVATE_Ω",
        "ordre": "ACTIVATION_PIPELINE_NOAA_TERRITOIRE",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "config": config_payload,
        "wod23_b2_probe": wod23_b2_probe,
        "wod23_local_probe": wod23_local_probe,
        "cfsv2_probe": cfsv2_probe,
        "cfsv2_urls_summary": {
            "n_urls_total": urls["n_urls_total"],
            "n_months": urls["n_months"],
            "n_variables": urls["n_variables"],
            "period": (
                f"{urls['period_start']} → {urls['period_end']}"),
        },
        "pipeline_verdict": pipeline_verdict,
        "persisted_paths": persisted,
        "no_engine_recompute_triggered": True,
        "v30_lock": "INVIOLÉ",
        "drift_zero": True,
        "elapsed_s": round(time.time() - t0, 3),
        "computed_at_utc": _utc_now(),
    }


# ═════════════════════════════════════════════════════════════════════════
# 5. Read-only registry exposure
# ═════════════════════════════════════════════════════════════════════════
def get_pipeline_status() -> Dict[str, Any]:
    """Lit l'état du pipeline NOAA (read-only)."""
    if not PIPELINE_CONFIG_PATH.exists():
        return {
            "manifest_id": "NOAA_PIPELINE_STATUS_Ω",
            "ordre": "ACTIVATION_PIPELINE_NOAA_TERRITOIRE",
            "status": "NOT_ACTIVATED_YET",
            "v30_lock": "INVIOLÉ",
        }
    config = json.loads(
        PIPELINE_CONFIG_PATH.read_text(encoding="utf-8"))
    probes = (
        json.loads(
            PIPELINE_PROBE_RESULTS_PATH.read_text(encoding="utf-8"))
        if PIPELINE_PROBE_RESULTS_PATH.exists() else None
    )
    urls_summary = None
    if PIPELINE_URLS_PATH.exists():
        urls_data = json.loads(
            PIPELINE_URLS_PATH.read_text(encoding="utf-8"))
        urls_summary = {
            "n_urls_total": urls_data["n_urls_total"],
            "n_months": urls_data["n_months"],
            "n_variables": urls_data["n_variables"],
            "period_start": urls_data["period_start"],
            "period_end": urls_data["period_end"],
        }
    return {
        "manifest_id": "NOAA_PIPELINE_STATUS_Ω",
        "ordre": "ACTIVATION_PIPELINE_NOAA_TERRITOIRE",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "config": config,
        "probes": probes,
        "cfsv2_urls_summary": urls_summary,
        "v30_lock": "INVIOLÉ",
        "scanned_at_utc": _utc_now(),
    }


__all__ = [
    "PIPELINE_ROOT",
    "PIPELINE_CONFIG_PATH",
    "PIPELINE_PROBE_RESULTS_PATH",
    "PIPELINE_URLS_PATH",
    "WOD23_CONFIG",
    "CFSV2_CONFIG",
    "generate_cfsv2_urls",
    "probe_wod23_b2",
    "probe_wod23_local",
    "probe_cfsv2_opendap",
    "activate_noaa_pipeline",
    "get_pipeline_status",
]

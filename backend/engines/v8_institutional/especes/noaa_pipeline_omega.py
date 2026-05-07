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
PIPELINE_TEMPLATE_HISTORY_PATH = (
    PIPELINE_ROOT / "cfsv2_template_history.json")

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
    "template_source": "NCAR_THREDDS_LEGACY",
    "template_history": [],
}

# Candidats NOMADS plausibles (source : documentation publique NOMADS NOAA)
# Anti-générique strict : ces templates sont DES CANDIDATS — l'URL exacte
# doit être validée par probe HTTP réel avant activation officielle.
CFSV2_NOMADS_TEMPLATE_CANDIDATES: List[Dict[str, str]] = [
    {
        "label": "NOMADS_CFS_MONTHLY_DODS",
        "template": (
            "https://nomads.ncep.noaa.gov/dods/cfs_monthly/"
            "cfs{YYYYMM}/{VARIABLE}.{YYYYMM}.mean"),
        "source": "NOMADS",
        "note": (
            "NOMADS DAP path mensuel CFSv2 — candidat plausible "
            "à valider par probe HTTP réel."),
    },
    {
        "label": "NOMADS_CFS_FLX_DODS",
        "template": (
            "https://nomads.ncep.noaa.gov/dods/cfs/"
            "cfs{YYYYMMDD}/cfs_{VARIABLE}_{YYYYMMDD}"),
        "source": "NOMADS",
        "note": (
            "NOMADS CFSv2 surface flux — candidat plausible journalier."),
    },
    {
        "label": "NOMADS_CFS_TIMESERIES_DODS",
        "template": (
            "https://nomads.ncep.noaa.gov/dods/cfs_timeseries/"
            "{YYYYMM}/{VARIABLE}_{YYYYMM}_mean"),
        "source": "NOMADS",
        "note": "NOMADS CFSv2 timeseries — candidat plausible.",
    },
]


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


# ═════════════════════════════════════════════════════════════════════════
# 6. Update template CFSv2 (NOMADS ou autre) avec probe + rollback
# ═════════════════════════════════════════════════════════════════════════
def update_cfsv2_template(
    new_template: str,
    source: str = "NOMADS",
    sample_yyyymm: str = "201101",
    sample_variable: str = "tavg",
    sample_yyyymmdd: Optional[str] = None,
    timeout_s: int = 10,
    persist: bool = True,
) -> Dict[str, Any]:
    """Met à jour le template OPeNDAP CFSv2 après probe RÉEL préalable.

    Workflow doctrinal :
      1. Validation format (contient {YYYYMM} ou {YYYYMMDD} + {VARIABLE})
      2. Probe HTTP HEAD + DDS sur sample (anti-générique)
      3. Si endpoint répond ≠ 4xx/5xx → activation + sauvegarde ancien
         dans template_history (rollback possible)
      4. Sinon retourne refus + raison réelle (anti-générique)
      5. Audit NOAA_PIPELINE/TEMPLATE_UPDATE persisté
      6. AUCUN recalcul moteur

    Anti-générique strict : aucune fabrication de status. Rollback toujours
    possible via template_history.
    """
    import urllib.error
    import urllib.request

    # 1. Validation format
    has_yyyymm = "{YYYYMM}" in new_template
    has_yyyymmdd = "{YYYYMMDD}" in new_template
    has_variable = "{VARIABLE}" in new_template
    if not (has_yyyymm or has_yyyymmdd):
        raise ValueError(
            "TEMPLATE_INVALID::missing_{YYYYMM}_or_{YYYYMMDD}_placeholder")
    if not has_variable:
        raise ValueError(
            "TEMPLATE_INVALID::missing_{VARIABLE}_placeholder")
    if not new_template.startswith(("https://", "http://")):
        raise ValueError("TEMPLATE_INVALID::not_http_url")
    # Doctrine : interdiction patterns
    for forbidden in CFSV2_CONFIG["forbidden_paths"]:
        if forbidden in new_template:
            raise ValueError(
                f"TEMPLATE_FORBIDDEN_PATTERN::{forbidden}")
    for forbidden in CFSV2_CONFIG["forbidden_formats"]:
        if new_template.endswith(forbidden):
            raise ValueError(
                f"TEMPLATE_FORBIDDEN_FORMAT::{forbidden}")

    # 2. Probe RÉEL sur sample
    sample_url = new_template
    if has_yyyymm:
        sample_url = sample_url.replace("{YYYYMM}", sample_yyyymm)
    if has_yyyymmdd:
        ymd = sample_yyyymmdd or f"{sample_yyyymm}01"
        sample_url = sample_url.replace("{YYYYMMDD}", ymd)
    sample_url = sample_url.replace("{VARIABLE}", sample_variable)
    dds_url = sample_url + ".dds"

    t0 = time.time()
    probe_main: Dict[str, Any] = {
        "url": sample_url, "http_status": None, "elapsed_ms": None,
        "reason": None,
    }
    try:
        # GET (avec lecture body limitée) plutôt que HEAD : permet
        # détection page "retired" / HTML d'erreur (anti-générique strict)
        req = urllib.request.Request(
            sample_url, method="GET",
            headers={"User-Agent": "BCE-4X-NOAA-PIPELINE/1.0"})
        with urllib.request.urlopen(req, timeout=timeout_s) as resp:
            probe_main["http_status"] = resp.status
            preview = resp.read(2048)
            probe_main["dds_preview_first_500b"] = (
                preview[:500].decode("utf-8", errors="replace"))
    except urllib.error.HTTPError as e:
        probe_main["http_status"] = e.code
        probe_main["reason"] = f"http_error_{e.code}"
        try:
            probe_main["dds_preview_first_500b"] = (
                e.read(2048)[:500].decode("utf-8", errors="replace"))
        except Exception:
            pass
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        probe_main["reason"] = f"network_error::{str(e)[:120]}"
    probe_main["elapsed_ms"] = round((time.time() - t0) * 1000, 1)

    t0 = time.time()
    probe_dds: Dict[str, Any] = {
        "url": dds_url, "http_status": None, "elapsed_ms": None,
        "reason": None,
    }
    try:
        req = urllib.request.Request(
            dds_url, method="GET",
            headers={"User-Agent": "BCE-4X-NOAA-PIPELINE/1.0"})
        with urllib.request.urlopen(req, timeout=timeout_s) as resp:
            probe_dds["http_status"] = resp.status
            probe_dds["dds_preview_first_500b"] = (
                resp.read(2048)[:500].decode(
                    "utf-8", errors="replace"))
    except urllib.error.HTTPError as e:
        probe_dds["http_status"] = e.code
        probe_dds["reason"] = f"http_error_{e.code}"
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        probe_dds["reason"] = f"network_error::{str(e)[:120]}"
    probe_dds["elapsed_ms"] = round((time.time() - t0) * 1000, 1)

    # 3. Verdict (HTTP 200 STRICT — anti-générique : 301 vers page d'erreur
    #    ne compte pas comme OPeNDAP fonctionnel).
    # Détection page "retired" / HTML d'erreur dans body main ou dds.
    retirement_indicators = [
        "OpenDAP format has been retired",
        "OPENDAP_RETIRED", "service has been retired",
        "Service Change Notice", "scn25-81",
    ]
    body_main = probe_main.get("dds_preview_first_500b", "") or ""
    body_dds = probe_dds.get("dds_preview_first_500b", "") or ""
    is_retired = any(
        indicator.lower() in body_main.lower()
        or indicator.lower() in body_dds.lower()
        for indicator in retirement_indicators
    )
    main_ok = probe_main["http_status"] == 200
    dds_ok = (
        probe_dds["http_status"] == 200
        and not is_retired
        and "Dataset" in body_dds)
    accepted = (main_ok or dds_ok) and not is_retired
    if is_retired:
        verdict = "TEMPLATE_REJECTED_OPENDAP_SERVICE_RETIRED"
    elif accepted and dds_ok:
        verdict = "TEMPLATE_VALIDATED_AND_ACTIVATED"
    elif accepted:
        verdict = "TEMPLATE_MAIN_OK_DDS_UNREACHABLE_ACCEPTED"
    else:
        verdict = "TEMPLATE_PROBE_FAILED_NOT_ACTIVATED"

    # 4. Sauvegarde + activation (FUSION ADD-ONLY history)
    previous_template = CFSV2_CONFIG["endpoint_template"]
    history_entry = {
        "timestamp_utc": _utc_now(),
        "previous_template": previous_template,
        "previous_source": CFSV2_CONFIG.get(
            "template_source", "UNKNOWN"),
        "new_template": new_template,
        "new_source": source,
        "probe_main": probe_main,
        "probe_dds": probe_dds,
        "verdict": verdict,
        "activated": accepted,
    }

    if accepted:
        CFSV2_CONFIG["endpoint_template"] = new_template
        CFSV2_CONFIG["template_source"] = source
        CFSV2_CONFIG.setdefault("template_history", []).append(
            history_entry)

    # 5. Persistance audit + history
    persisted: Dict[str, Any] = {}
    if persist:
        PIPELINE_ROOT.mkdir(parents=True, exist_ok=True)
        # History append (FUSION ADD-ONLY)
        if PIPELINE_TEMPLATE_HISTORY_PATH.exists():
            try:
                hist = json.loads(
                    PIPELINE_TEMPLATE_HISTORY_PATH.read_text(
                        encoding="utf-8"))
                if not isinstance(hist, dict) or "log" not in hist:
                    hist = {"log": []}
            except json.JSONDecodeError:
                hist = {"log": []}
        else:
            hist = {"log": []}
        hist["log"].append(history_entry)
        hist["last_updated_utc"] = _utc_now()
        hist["n_entries"] = len(hist["log"])
        hist["current_template"] = CFSV2_CONFIG["endpoint_template"]
        hist["current_source"] = CFSV2_CONFIG["template_source"]
        PIPELINE_TEMPLATE_HISTORY_PATH.write_text(
            json.dumps(hist, ensure_ascii=False, indent=2),
            encoding="utf-8")
        persisted["history_path"] = str(
            PIPELINE_TEMPLATE_HISTORY_PATH)

        # Audit doctrinal
        from engines.v8_institutional.especes.bio_reacteur_overlay_omega import (  # noqa: E501
            persist_audit,
        )
        audit_payload = {
            "audit_type": "NOAA_PIPELINE",
            "subtype": "TEMPLATE_UPDATE",
            "ordre": "ACTIVATION_PIPELINE_NOAA_TERRITOIRE",
            "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
            "previous_template": previous_template,
            "previous_source": history_entry["previous_source"],
            "new_template": new_template,
            "new_source": source,
            "probe_main_http_status": probe_main["http_status"],
            "probe_dds_http_status": probe_dds["http_status"],
            "verdict": verdict,
            "activated": accepted,
            "no_engine_recompute_triggered": True,
            "v30_lock_inviolate": True,
            "drift_zero": True,
        }
        persisted["audit_persisted"] = persist_audit(audit_payload)

    return {
        "manifest_id": "CFSV2_TEMPLATE_UPDATE_Ω",
        "ordre": "ACTIVATION_PIPELINE_NOAA_TERRITOIRE",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "previous_template": previous_template,
        "new_template": new_template,
        "new_source": source,
        "sample_url_probed": sample_url,
        "probe_main": probe_main,
        "probe_dds": probe_dds,
        "verdict": verdict,
        "activated": accepted,
        "current_template_after_update": (
            CFSV2_CONFIG["endpoint_template"]),
        "persisted_paths": persisted,
        "no_engine_recompute_triggered": True,
        "v30_lock": "INVIOLÉ",
        "drift_zero": True,
        "computed_at_utc": _utc_now(),
    }


# ═════════════════════════════════════════════════════════════════════════
# 7. Probe credentials B2 alternatifs (sans toucher .env)
# ═════════════════════════════════════════════════════════════════════════
def probe_b2_credentials_alternative(
    key_id: str,
    application_key: str,
    bucket: str,
    path_prefix: str = "",
    endpoint_url: Optional[str] = None,
    region: Optional[str] = None,
    max_keys: int = 20,
) -> Dict[str, Any]:
    """Probe RÉEL B2 avec credentials alternatifs (pas de mutation .env).

    Anti-générique strict : status RÉEL retourné.
    """
    import os
    record: Dict[str, Any] = {
        "manifest_id": "B2_CREDS_PROBE_Ω",
        "ordre": "ACTIVATION_PIPELINE_NOAA_TERRITOIRE",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "bucket": bucket,
        "path_prefix": path_prefix,
        "endpoint_url": endpoint_url or os.environ.get(
            "B2_ENDPOINT_URL"),
        "region": region or os.environ.get("B2_REGION"),
        "key_id_first_12": (key_id[:12] + "..." if key_id else None),
        "available": False,
        "anti_generique_strict": True,
        "v30_lock": "INVIOLÉ",
        "probed_at_utc": _utc_now(),
    }
    if not record["endpoint_url"]:
        record["reason"] = "endpoint_url_missing_no_default"
        return record
    try:
        import boto3
        from botocore.config import Config
        from botocore.exceptions import (
            ClientError, EndpointConnectionError, NoCredentialsError,
        )
    except ImportError as e:
        record["reason"] = f"boto3_import_error::{str(e)[:120]}"
        return record

    try:
        s3 = boto3.client(
            "s3",
            aws_access_key_id=key_id,
            aws_secret_access_key=application_key,
            endpoint_url=record["endpoint_url"],
            region_name=record["region"],
            config=Config(
                connect_timeout=10, read_timeout=10,
                retries={"max_attempts": 1}),
        )
    except Exception as e:
        record["reason"] = f"client_init_error::{str(e)[:120]}"
        return record

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

    t0 = time.time()
    n_objects = 0
    sample = []
    try:
        resp = s3.list_objects_v2(
            Bucket=bucket, Prefix=path_prefix, MaxKeys=max_keys)
        for obj in resp.get("Contents", []):
            n_objects += 1
            if len(sample) < 5:
                sample.append({
                    "key": obj["Key"], "size": obj.get("Size", 0),
                })
    except ClientError as e:
        code = e.response.get("Error", {}).get("Code", "?")
        record["reason"] = f"list_objects_error::{code}"
        record["http_list_objects_ms"] = round(
            (time.time() - t0) * 1000, 1)
        return record
    record["http_list_objects_ms"] = round(
        (time.time() - t0) * 1000, 1)
    record["n_objects_found"] = n_objects
    record["sample_keys"] = sample
    record["available"] = True
    return record


__all__ = [
    "PIPELINE_ROOT",
    "PIPELINE_CONFIG_PATH",
    "PIPELINE_PROBE_RESULTS_PATH",
    "PIPELINE_URLS_PATH",
    "PIPELINE_TEMPLATE_HISTORY_PATH",
    "WOD23_CONFIG",
    "CFSV2_CONFIG",
    "CFSV2_NOMADS_TEMPLATE_CANDIDATES",
    "generate_cfsv2_urls",
    "probe_wod23_b2",
    "probe_wod23_local",
    "probe_cfsv2_opendap",
    "activate_noaa_pipeline",
    "get_pipeline_status",
    "update_cfsv2_template",
    "probe_b2_credentials_alternative",
    "WOD23_HOOK_OVERLAY_CONFIG",
    "WOD23_HOOK_ACTIVATION_PATH",
    "probe_wod23_b2_dedicated",
    "activate_wod23_hook",
    "get_wod23_hook_status",
    "CFSV2_PIVOT_CANDIDATE_LIST",
    "CFSV2_VERIFICATION_P0_PATH",
    "CFSV2_PIVOT_VERIFICATION_PATH",
    "CFSV2_CATALOGUE_CARTOGRAPHY_PATH",
    "verify_cfsv2_p0_head_only",
    "verify_cfsv2_pivot_head_only",
    "list_cfsv2_pivot_candidates",
    "cartograph_ncei_catalogue",
    "COPERNICUS_API_PLACEHOLDERS",
    "COPERNICUS_API_VALIDATION_PATH",
    "validate_copernicus_api_endpoint",
    "OPENWEATHERMAP_VALIDATION_PATH",
    "validate_openweathermap_endpoint",
    "OPENWEATHERMAP_HOOK_ACTIVATION_PATH",
    "activate_openweathermap_hook",
    "get_openweathermap_hook_status",
    "OPENWEATHERMAP_ZONE_PIVOT_PATH",
    "validate_openweathermap_zone_pivot",
    "OPENWEATHERMAP_BATCH_BP135_PATH",
    "batch_probe_owm_bp135",
    "OPENWEATHERMAP_BATCH_BP135_HOOK_PATH",
    "activate_openweathermap_batch_bp135_hook",
    "get_openweathermap_batch_bp135_hook_status",
]


# ═════════════════════════════════════════════════════════════════════════
# 17. OPENWEATHERMAP BATCH BP135 HOOK ACTIVATION (officielle FUSION ADD-ONLY)
# ═════════════════════════════════════════════════════════════════════════
OPENWEATHERMAP_BATCH_BP135_HOOK_PATH = (
    PIPELINE_ROOT / "openweathermap_batch_bp135_hook_activation_overlay.json")


def _find_validated_owm_batch_manifest(
    target_manifest_sha256: str,
) -> Optional[Dict[str, Any]]:
    """Cherche un manifest BATCH BP135 validé dans l'historique.

    Anti-générique strict : on ne peut activer un hook batch que sur
    un manifest_sha256 RÉELLEMENT validé (au moins 1 espèce valide).
    Retourne None si introuvable ou non-valide.
    """
    if not OPENWEATHERMAP_BATCH_BP135_PATH.exists():
        return None
    try:
        state = json.loads(
            OPENWEATHERMAP_BATCH_BP135_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    history = state.get("history", [])
    for entry in history:
        if (entry.get("manifest_sha256") == target_manifest_sha256
                and entry.get("n_valid", 0) >= 1):
            return entry
    return None


def activate_openweathermap_batch_bp135_hook(
    manifest_sha256: str,
    reason: str = "owm_batch_bp135_activated",
    persist: bool = True,
) -> Dict[str, Any]:
    """OPENWEATHERMAP_BATCH_BP135_HOOK_ACTIVATE · activation officielle.

    Workflow doctrinal :
      1. Guardrails ENFORCED check (412 sinon)
      2. Vérification ANTI-GÉNÉRIQUE STRICTE : manifest_sha256 doit
         exister dans OPENWEATHERMAP_BATCH_BP135_PATH avec n_valid >= 1.
         Refus d'activer un manifest fabriqué.
      3. Construction manifest activation signé SHA-256 + sommaire
         5 espèces validées
      4. Forensic log HOOK_ACTIVATIONS/OPENWEATHERMAP_BATCH_BP135_HOOK_ACTIVATE
      5. Persistance overlay history (V30_LOCK FUSION ADD-ONLY)
      6. Audit doctrinal NOAA_PIPELINE/OPENWEATHERMAP_BATCH_BP135_HOOK_ACTIVATE
      7. AUCUN recalcul moteur ICI (drift audit séparé)

    Returns:
      Dict avec verdict + activation_sha256 + sommaire 5 espèces.
    """
    from engines.v8_institutional.especes.pipeline_guardrails_omega import (
        require_guardrails_enforced, log_forensic_event,
    )
    require_guardrails_enforced(
        "activate_openweathermap_batch_bp135_hook")

    t0 = time.time()
    validated_batch = _find_validated_owm_batch_manifest(
        manifest_sha256)
    if validated_batch is None:
        verdict = (
            "OWM_BATCH_BP135_HOOK_REJECTED_MANIFEST_NOT_FOUND_OR_INVALID")
        rejection_payload = {
            "manifest_id": "OWM_BATCH_BP135_HOOK_ACTIVATE_Ω",
            "ordre": "P1_OPENWEATHERMAP_BATCH_BP135_HOOK_ACTIVATE",
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
                "OPENWEATHERMAP_BATCH_BP135_PATH avec n_valid >= 1. "
                "Anti-générique strict : impossible d'activer un hook "
                "batch sur un manifest non validé."),
            "anti_generique_strict": True,
            "v30_lock": "INVIOLÉ",
            "drift_zero": True,
            "no_engine_recompute_triggered": True,
            "executed_at_utc": _utc_now(),
            "elapsed_s": round(time.time() - t0, 3),
        }
        log_forensic_event(
            scope="HOOK_ACTIVATIONS",
            event="OPENWEATHERMAP_BATCH_BP135_HOOK_ACTIVATE",
            details={
                "input_manifest_sha256": manifest_sha256,
                "reason": reason,
                "activated": False,
                "verdict": verdict,
            },
            persist=True,
        )
        return rejection_payload

    # Construction sommaire batch (anti-générique : extraction réelle)
    species_summary: List[Dict[str, Any]] = []
    for sp in validated_batch.get("species_results", []):
        species_summary.append({
            "species_name": sp.get("species_name"),
            "lat": (sp.get("coords") or {}).get("lat"),
            "lon": (sp.get("coords") or {}).get("lon"),
            "valid": sp.get("valid"),
            "city_resolved_by_owm": (
                (sp.get("current_meta") or {}).get("city_name")),
            "country": (
                (sp.get("current_meta") or {}).get("country")),
            "weather_main": (
                (sp.get("current_meta") or {}).get("weather_main")),
            "n_variables_extracted": (
                sp.get("n_variables_extracted")),
        })

    activation_payload = {
        "manifest_id": "OWM_BATCH_BP135_HOOK_ACTIVATE_Ω",
        "ordre": "P1_OPENWEATHERMAP_BATCH_BP135_HOOK_ACTIVATE",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "guardrails_enforced": True,
        "autonomy": "LIMITED",
        "activated": True,
        "verdict": "OWM_BATCH_BP135_HOOK_ACTIVATED_OPERATIONAL",
        "reason": reason,
        "validated_manifest_sha256": manifest_sha256,
        "validated_batch_executed_at_utc": (
            validated_batch.get("executed_at_utc")),
        "n_species_total": validated_batch.get("n_species_total"),
        "n_species_valid": validated_batch.get("n_valid"),
        "species_summary": species_summary,
        "aggregated_stats_inherited": validated_batch.get(
            "aggregated_stats_across_valid_species") or {},
        "endpoints_inherited": validated_batch.get("endpoints"),
        "units": validated_batch.get("units"),
        "consumed_by_modules": [
            "PHYSIOLOGIE_THERMIQUE",
            "HABITAT_MICROCLIMAT",
            "NUTRITION_HUMIDITE",
            "PHENOLOGIE_FORECAST_5_DAY",
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
        PIPELINE_ROOT.mkdir(parents=True, exist_ok=True)
        if OPENWEATHERMAP_BATCH_BP135_HOOK_PATH.exists():
            try:
                state = json.loads(
                    OPENWEATHERMAP_BATCH_BP135_HOOK_PATH.read_text(
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
        OPENWEATHERMAP_BATCH_BP135_HOOK_PATH.write_text(
            json.dumps(state, ensure_ascii=False, indent=2),
            encoding="utf-8")
        persisted["overlay_path"] = str(
            OPENWEATHERMAP_BATCH_BP135_HOOK_PATH)
        persisted["overlay_size_bytes"] = (
            OPENWEATHERMAP_BATCH_BP135_HOOK_PATH.stat().st_size)
        persisted["n_activations_history"] = state["n_activations"]

        log_forensic_event(
            scope="HOOK_ACTIVATIONS",
            event="OPENWEATHERMAP_BATCH_BP135_HOOK_ACTIVATE",
            details={
                "validated_manifest_sha256": manifest_sha256,
                "activation_sha256": activation_sha256,
                "reason": reason,
                "activated": True,
                "n_species_valid": validated_batch.get("n_valid"),
                "verdict":
                    "OWM_BATCH_BP135_HOOK_ACTIVATED_OPERATIONAL",
            },
            persist=True,
        )

        from engines.v8_institutional.especes.bio_reacteur_overlay_omega import (  # noqa: E501
            persist_audit,
        )
        audit_payload = {
            "audit_type": "NOAA_PIPELINE",
            "subtype": "OWM_BATCH_BP135_HOOK_ACTIVATE",
            "ordre":
                "P1_OPENWEATHERMAP_BATCH_BP135_HOOK_ACTIVATE",
            "doctrine":
                "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
            "provider": "OPENWEATHERMAP",
            "validated_manifest_sha256": manifest_sha256,
            "activation_sha256": activation_sha256,
            "reason": reason,
            "activated": True,
            "verdict":
                "OWM_BATCH_BP135_HOOK_ACTIVATED_OPERATIONAL",
            "n_species_valid": validated_batch.get("n_valid"),
            "n_species_total": validated_batch.get(
                "n_species_total"),
            "v30_lock_inviolate": True,
            "drift_zero": True,
            "no_engine_recompute_triggered": True,
        }
        persisted["audit_persisted"] = persist_audit(audit_payload)

    activation_payload["persisted_paths"] = persisted
    activation_payload["elapsed_s"] = round(time.time() - t0, 3)
    return activation_payload


def get_openweathermap_batch_bp135_hook_status() -> Dict[str, Any]:
    """État actuel du hook BATCH BP135 (read-only)."""
    if not OPENWEATHERMAP_BATCH_BP135_HOOK_PATH.exists():
        return {
            "manifest_id": "OWM_BATCH_BP135_HOOK_STATUS_Ω",
            "ordre":
                "P1_OPENWEATHERMAP_BATCH_BP135_HOOK_ACTIVATE",
            "current_status": "NOT_ACTIVATED",
            "v30_lock": "INVIOLÉ",
            "scanned_at_utc": _utc_now(),
        }
    state = json.loads(
        OPENWEATHERMAP_BATCH_BP135_HOOK_PATH.read_text(
            encoding="utf-8"))
    last = (state["history"][-1]
            if state.get("history") else None)
    return {
        "manifest_id": "OWM_BATCH_BP135_HOOK_STATUS_Ω",
        "ordre": "P1_OPENWEATHERMAP_BATCH_BP135_HOOK_ACTIVATE",
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
        "overlay_path": str(OPENWEATHERMAP_BATCH_BP135_HOOK_PATH),
        "overlay_size_bytes": (
            OPENWEATHERMAP_BATCH_BP135_HOOK_PATH.stat().st_size),
        "v30_lock": "INVIOLÉ",
        "scanned_at_utc": _utc_now(),
    }


# ═════════════════════════════════════════════════════════════════════════
# 16. OPENWEATHERMAP BATCH PROBE BP135 (5 espèces × 2 endpoints = 10 calls)
# ═════════════════════════════════════════════════════════════════════════
OPENWEATHERMAP_BATCH_BP135_PATH = (
    PIPELINE_ROOT / "openweathermap_batch_bp135_overlay.json")


def batch_probe_owm_bp135(
    endpoint_current: str = (
        "https://api.openweathermap.org/data/2.5/weather"),
    endpoint_forecast: str = (
        "https://api.openweathermap.org/data/2.5/forecast"),
    credentials_api_key: Optional[str] = None,
    species_coordinates: Optional[Dict[str, Dict[str, float]]] = None,
    units: str = "metric",
    forensic_event: str = "OPENWEATHERMAP_BATCH_BP135",
    persist: bool = True,
    timeout_s: int = 15,
    inter_call_sleep_s: float = 0.2,
) -> Dict[str, Any]:
    """OPENWEATHERMAP_BATCH_PROBE_BP135 · batch sur 5 espèces × 2 endpoints.

    Workflow doctrinal :
      1. Guardrails ENFORCED check (412 sinon)
      2. Validation des coords (lat ∈ [-90,90], lon ∈ [-180,180])
      3. Pour chaque espèce, appelle validate_openweathermap_zone_pivot
         (persist=False pour ne pas saturer overlay zone_pivot)
      4. Pause inter-calls (anti-rate-limit OWM 60/min gratuit)
      5. Agrégation des résultats en manifest batch signé SHA-256
      6. Forensic log ENDPOINT_PROBES/{forensic_event} par espèce
      7. Persistance overlay batch + audit doctrinal
      8. AUCUN recalcul moteur · V30_LOCK + DRIFT_ZERO

    Anti-générique strict : variables extraites uniquement depuis JSON
    réel par espèce, pas de fabrication entre espèces.
    """
    from engines.v8_institutional.especes.pipeline_guardrails_omega import (
        require_guardrails_enforced, log_forensic_event,
    )
    require_guardrails_enforced("batch_probe_owm_bp135")

    if not species_coordinates:
        raise ValueError(
            "SPECIES_COORDINATES_REQUIRED::empty_or_none")

    # Validation coords (anti-générique strict)
    for sp_name, coords in species_coordinates.items():
        lat = coords.get("lat") if isinstance(coords, dict) else None
        lon = coords.get("lon") if isinstance(coords, dict) else None
        if (lat is None or lon is None
                or not (-90.0 <= float(lat) <= 90.0)
                or not (-180.0 <= float(lon) <= 180.0)):
            raise ValueError(
                f"COORDS_INVALID::{sp_name}::lat={lat},lon={lon}")

    appid_token_masked = _mask_token(credentials_api_key)
    creds_placeholder = _is_placeholder_token(credentials_api_key)

    if creds_placeholder:
        return {
            "manifest_id": "OWM_BATCH_BP135_Ω",
            "ordre": "P1_OPENWEATHERMAP_BATCH_PROBE_BP135",
            "doctrine":
                "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
            "guardrails_enforced": True,
            "autonomy": "LIMITED",
            "valid": False,
            "verdict": "OWM_BATCH_REJECTED_PLACEHOLDER_TOKEN",
            "credentials_api_key_masked": appid_token_masked,
            "next_action": (
                "REJECTED — credentials_api_key is a placeholder. "
                "No HTTP request emitted."),
            "anti_generique_strict": True,
            "v30_lock": "INVIOLÉ",
            "executed_at_utc": _utc_now(),
        }

    t_total = time.time()
    species_results: List[Dict[str, Any]] = []
    n_valid = 0
    n_invalid = 0
    aggregated_variables: Dict[str, Dict[str, Any]] = {}

    for sp_name, coords in species_coordinates.items():
        lat = float(coords["lat"])
        lon = float(coords["lon"])
        # Re-utilisation de validate_openweathermap_zone_pivot (persist=False)
        try:
            sub = validate_openweathermap_zone_pivot(
                endpoint_current=endpoint_current,
                endpoint_forecast=endpoint_forecast,
                credentials_api_key=None,
                query_params={
                    "lat": lat,
                    "lon": lon,
                    "appid": credentials_api_key,
                    "units": units,
                },
                variables_requested={
                    "temperature": True, "humidity": True,
                    "pressure": True, "wind_speed": True,
                    "wind_direction": True, "cloud_cover": True,
                    "precipitation": True,
                },
                forensic_event=forensic_event,
                persist=False,
                timeout_s=timeout_s,
            )
        except Exception as e:
            sub = {
                "valid": False,
                "verdict": "OWM_BATCH_SUB_PROBE_EXCEPTION",
                "exception": str(e)[:300],
                "manifest_sha256": None,
            }

        species_entry = {
            "species_name": sp_name,
            "coords": {"lat": lat, "lon": lon},
            "sub_manifest_sha256": sub.get("manifest_sha256"),
            "verdict": sub.get("verdict"),
            "valid": sub.get("valid"),
            "current_http_status": (
                (sub.get("probe_current_summary") or {})
                .get("http_status")),
            "forecast_http_status": (
                (sub.get("probe_forecast_summary") or {})
                .get("http_status")),
            "current_signature_present":
                sub.get("current_owm_signature_present"),
            "forecast_signature_present":
                sub.get("forecast_owm_signature_present"),
            "forecast_n_items": sub.get("forecast_n_items"),
            "current_meta": sub.get("current_meta"),
            "variables_extracted":
                sub.get("variables_extracted") or {},
            "variables_missing": sub.get("variables_missing"),
            "n_variables_extracted":
                sub.get("n_variables_extracted") or 0,
        }
        species_results.append(species_entry)
        if species_entry["valid"]:
            n_valid += 1
            aggregated_variables[sp_name] = (
                species_entry["variables_extracted"])
        else:
            n_invalid += 1

        # Forensic log par sous-probe
        log_forensic_event(
            scope="ENDPOINT_PROBES",
            event=forensic_event,
            details={
                "species": sp_name,
                "lat": lat, "lon": lon,
                "current_http_status":
                    species_entry["current_http_status"],
                "forecast_http_status":
                    species_entry["forecast_http_status"],
                "valid": species_entry["valid"],
                "verdict": species_entry["verdict"],
                "n_variables_extracted":
                    species_entry["n_variables_extracted"],
            },
            persist=True,
        )

        # Pause inter-calls (anti-rate-limit OWM)
        if inter_call_sleep_s > 0:
            time.sleep(inter_call_sleep_s)

    # Verdict batch
    n_total = len(species_results)
    if n_valid == n_total:
        batch_verdict = "OWM_BATCH_BP135_ALL_SPECIES_VALID"
        batch_valid = True
    elif n_valid > 0:
        batch_verdict = (
            f"OWM_BATCH_BP135_PARTIAL::{n_valid}_OF_{n_total}_VALID")
        batch_valid = False
    else:
        batch_verdict = "OWM_BATCH_BP135_ALL_INVALID"
        batch_valid = False

    # Statistiques agrégées (anti-générique : uniquement sur les valides)
    stats: Dict[str, Any] = {}
    if aggregated_variables:
        for var in ("temperature", "humidity", "pressure",
                    "wind_speed", "wind_direction", "cloud_cover"):
            values = [
                v[var] for v in aggregated_variables.values()
                if isinstance(v, dict) and var in v
                and isinstance(v[var], (int, float))
            ]
            if values:
                stats[var] = {
                    "n": len(values),
                    "min": min(values),
                    "max": max(values),
                    "mean": round(sum(values) / len(values), 3),
                }

    # Manifest signé + persistance
    payload = {
        "manifest_id": "OWM_BATCH_BP135_Ω",
        "ordre": "P1_OPENWEATHERMAP_BATCH_PROBE_BP135",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "forensic_event": forensic_event,
        "guardrails_enforced": True,
        "autonomy": "LIMITED",
        "valid": batch_valid,
        "verdict": batch_verdict,
        "n_species_total": n_total,
        "n_valid": n_valid,
        "n_invalid": n_invalid,
        "credentials_api_key_masked": appid_token_masked,
        "endpoints": {
            "current": endpoint_current,
            "forecast": endpoint_forecast,
        },
        "units": units,
        "species_coordinates_input": {
            sp: {"lat": float(c["lat"]), "lon": float(c["lon"])}
            for sp, c in species_coordinates.items()
        },
        "species_results": species_results,
        "aggregated_stats_across_valid_species": stats,
        "anti_generique_strict": True,
        "anti_leakage_token_masked": True,
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
        PIPELINE_ROOT.mkdir(parents=True, exist_ok=True)
        if OPENWEATHERMAP_BATCH_BP135_PATH.exists():
            try:
                state = json.loads(
                    OPENWEATHERMAP_BATCH_BP135_PATH.read_text(
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
        state["n_batches"] = len(state["history"])
        state["last_manifest_sha256"] = payload_sha256
        state["last_verdict"] = batch_verdict
        state["v30_lock"] = "INVIOLÉ"
        OPENWEATHERMAP_BATCH_BP135_PATH.write_text(
            json.dumps(state, ensure_ascii=False, indent=2),
            encoding="utf-8")
        persisted["overlay_path"] = str(
            OPENWEATHERMAP_BATCH_BP135_PATH)
        persisted["overlay_size_bytes"] = (
            OPENWEATHERMAP_BATCH_BP135_PATH.stat().st_size)
        persisted["n_batches_history"] = state["n_batches"]

        from engines.v8_institutional.especes.bio_reacteur_overlay_omega import (  # noqa: E501
            persist_audit,
        )
        audit_payload = {
            "audit_type": "NOAA_PIPELINE",
            "subtype": "OWM_BATCH_BP135",
            "ordre": "P1_OPENWEATHERMAP_BATCH_PROBE_BP135",
            "doctrine":
                "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
            "provider": "OPENWEATHERMAP",
            "valid": batch_valid,
            "verdict": batch_verdict,
            "manifest_sha256": payload_sha256,
            "n_species_total": n_total,
            "n_valid": n_valid,
            "n_invalid": n_invalid,
            "v30_lock_inviolate": True,
            "drift_zero": True,
            "no_engine_recompute_triggered": True,
        }
        persisted["audit_persisted"] = persist_audit(audit_payload)

    payload["persisted_paths"] = persisted
    return payload


# ═════════════════════════════════════════════════════════════════════════
# 15. OPENWEATHERMAP ZONE PIVOT (current + forecast + 7 variables enrichies)
# ═════════════════════════════════════════════════════════════════════════
OPENWEATHERMAP_ZONE_PIVOT_PATH = (
    PIPELINE_ROOT / "openweathermap_zone_pivot_overlay.json")

# Variables canoniques OWM (anti-générique : extraction strictement
# basée sur les champs du body JSON réel, jamais inventés).
OWM_VARIABLE_PATHS_CURRENT: Dict[str, List[str]] = {
    "temperature": ["main", "temp"],
    "feels_like": ["main", "feels_like"],
    "temperature_min": ["main", "temp_min"],
    "temperature_max": ["main", "temp_max"],
    "humidity": ["main", "humidity"],
    "pressure": ["main", "pressure"],
    "wind_speed": ["wind", "speed"],
    "wind_direction": ["wind", "deg"],
    "wind_gust": ["wind", "gust"],
    "cloud_cover": ["clouds", "all"],
    "visibility": ["visibility"],
}


def _extract_path(d: Dict[str, Any], path: List[str]) -> Optional[Any]:
    """Extrait une valeur à un path nested dans un dict (anti-générique).

    Retourne None si chemin inexistant. Aucune fabrication.
    """
    cur: Any = d
    for k in path:
        if isinstance(cur, dict) and k in cur:
            cur = cur[k]
        else:
            return None
    return cur


def _http_get_json_strict(
    url: str,
    follow_redirects: bool = False,
    timeout_s: int = 15,
    body_max_bytes: int = 65536,
    headers_extra: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    """GET HTTP strict avec NoRedirect + parsing JSON (anti-générique).

    Retourne dict avec http_status, content_type, body_is_json,
    parsed_json (ou None), reason, elapsed_ms, redirect_detected.
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
        opener = (
            urllib.request.build_opener(NoRedirectHandler)
            if not follow_redirects
            else urllib.request.build_opener())
        h = {
            "User-Agent":
                "BCE-4X-OWM-ZONE-PIVOT/1.0",
            "Accept": "application/json",
        }
        if headers_extra:
            h.update(headers_extra)
        req = urllib.request.Request(url, method="GET", headers=h)
        with opener.open(req, timeout=timeout_s) as resp:
            record["http_status"] = resp.status
            record["content_type"] = resp.headers.get("Content-Type")
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
            try:
                record["parsed_error_json"] = json.loads(
                    body.decode("utf-8", errors="replace"))
            except json.JSONDecodeError:
                record["body_preview_first_500b"] = (
                    body[:500].decode("utf-8", errors="replace"))
        except Exception:
            pass
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        record["reason"] = f"network_error::{str(e)[:160]}"
    record["elapsed_ms"] = round((time.time() - t0) * 1000, 1)
    return record


def validate_openweathermap_zone_pivot(
    endpoint_current: str = (
        "https://api.openweathermap.org/data/2.5/weather"),
    endpoint_forecast: str = (
        "https://api.openweathermap.org/data/2.5/forecast"),
    credentials_api_key: Optional[str] = None,
    query_params: Optional[Dict[str, Any]] = None,
    variables_requested: Optional[Dict[str, bool]] = None,
    require_http_200: bool = True,
    require_no_redirect: bool = True,
    expect_content_type: str = "application/json",
    forensic_event: str = "OPENWEATHERMAP_PIVOT_TERRITOIRE",
    persist: bool = True,
    timeout_s: int = 15,
) -> Dict[str, Any]:
    """OPENWEATHERMAP_P0_PIVOT_TERRITOIRE · double probe enrichi (current
    + forecast) avec extraction stricte des variables OWM réelles.

    Workflow doctrinal :
      1. Guardrails ENFORCED check (412 sinon)
      2. Détection placeholder DOUBLE niveau (credentials + query.appid)
      3. Auth priority : QUERY_PARAM_APPID > BEARER_HEADER > NONE
      4. Probe 1 : current weather (lat/lon, units)
      5. Probe 2 : forecast (mêmes coords)
      6. Extraction stricte des variables demandées (anti-générique :
         seules les valeurs RÉELLEMENT présentes dans le JSON sont
         persistées, jamais fabriquées)
      7. Forensic log ENDPOINT_PROBES/{forensic_event}
      8. Persistance overlay history + audit doctrinal
      9. AUCUN recalcul moteur · V30_LOCK + DRIFT_ZERO

    Anti-leakage : tokens masqués dans URL/payload/persistence.
    """
    from engines.v8_institutional.especes.pipeline_guardrails_omega import (
        require_guardrails_enforced, log_forensic_event,
    )
    require_guardrails_enforced(
        "validate_openweathermap_zone_pivot")

    if not endpoint_current.startswith(("https://", "http://")):
        raise ValueError(
            f"ENDPOINT_CURRENT_INVALID::{endpoint_current[:120]}")
    if not endpoint_forecast.startswith(("https://", "http://")):
        raise ValueError(
            f"ENDPOINT_FORECAST_INVALID::{endpoint_forecast[:120]}")

    from urllib.parse import urlencode

    qp = dict(query_params or {})
    appid_in_query = qp.get("appid")
    creds_placeholder = _is_placeholder_token(credentials_api_key)
    appid_placeholder = _is_placeholder_token(appid_in_query)
    creds_token_masked = _mask_token(credentials_api_key)
    appid_token_masked = _mask_token(appid_in_query)

    use_query_auth = (
        bool(appid_in_query) and not appid_placeholder)
    use_header_auth = (
        (not use_query_auth)
        and bool(credentials_api_key)
        and not creds_placeholder)
    auth_strategy = (
        "QUERY_PARAM_APPID" if use_query_auth
        else "BEARER_HEADER" if use_header_auth
        else "NONE_BOTH_PLACEHOLDERS")

    # Construction URLs (réelles ET masquées)
    qp_real = dict(qp)
    qp_masked = dict(qp)
    if "appid" in qp_real:
        qp_masked["appid"] = appid_token_masked
    qs_real = ("?" + urlencode(qp_real)) if qp_real else ""
    qs_masked = (
        "?" + urlencode(qp_masked)) if qp_masked else ""
    url_current_real = endpoint_current + qs_real
    url_current_masked = endpoint_current + qs_masked
    url_forecast_real = endpoint_forecast + qs_real
    url_forecast_masked = endpoint_forecast + qs_masked

    # Court-circuit doctrinal
    if auth_strategy == "NONE_BOTH_PLACEHOLDERS":
        verdict = (
            "OWM_ZONE_PIVOT_REJECTED_BOTH_PLACEHOLDERS_DETECTED")
        return {
            "manifest_id": "OWM_ZONE_PIVOT_Ω",
            "ordre": "P0_OPENWEATHERMAP_PIVOT_TERRITOIRE",
            "doctrine":
                "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
            "guardrails_enforced": True,
            "autonomy": "LIMITED",
            "valid": False,
            "verdict": verdict,
            "auth_strategy": auth_strategy,
            "credentials_api_key_masked": creds_token_masked,
            "query_appid_masked": appid_token_masked,
            "next_action": (
                "REJECTED — both auth tokens are placeholders. "
                "No HTTP request emitted."),
            "anti_generique_strict": True,
            "v30_lock": "INVIOLÉ",
            "drift_zero": True,
            "no_engine_recompute_triggered": True,
            "executed_at_utc": _utc_now(),
        }

    # Probe 1 : current weather
    headers_extra: Dict[str, str] = {}
    if use_header_auth:
        headers_extra["Authorization"] = (
            f"Bearer {credentials_api_key}")
    probe_current = _http_get_json_strict(
        url=url_current_real,
        follow_redirects=False,
        timeout_s=timeout_s,
        headers_extra=headers_extra,
    )
    probe_current["url_masked"] = url_current_masked

    # Probe 2 : forecast
    probe_forecast = _http_get_json_strict(
        url=url_forecast_real,
        follow_redirects=False,
        timeout_s=timeout_s,
        headers_extra=headers_extra,
    )
    probe_forecast["url_masked"] = url_forecast_masked

    # Validation signature current (weather + main + name)
    current_owm_signature_present = False
    if probe_current["body_is_json"] and isinstance(
            probe_current["parsed_json"], dict):
        keys = set(probe_current["parsed_json"].keys())
        current_owm_signature_present = {
            "weather", "main", "name"}.issubset(keys)
    # Validation signature forecast (list + city)
    forecast_owm_signature_present = False
    forecast_n_items = 0
    if probe_forecast["body_is_json"] and isinstance(
            probe_forecast["parsed_json"], dict):
        keys = set(probe_forecast["parsed_json"].keys())
        forecast_owm_signature_present = {
            "list", "city"}.issubset(keys)
        if "list" in probe_forecast["parsed_json"] and (
                isinstance(
                    probe_forecast["parsed_json"]["list"], list)):
            forecast_n_items = len(
                probe_forecast["parsed_json"]["list"])

    # Extraction des variables demandées (anti-générique strict)
    vars_req = dict(variables_requested or {
        "temperature": True, "humidity": True, "pressure": True,
        "wind_speed": True, "wind_direction": True,
        "cloud_cover": True, "precipitation": True})
    variables_extracted: Dict[str, Any] = {}
    variables_missing: List[str] = []
    if (probe_current["body_is_json"]
            and isinstance(probe_current["parsed_json"], dict)):
        parsed = probe_current["parsed_json"]
        for var_name, requested in vars_req.items():
            if not requested:
                continue
            if var_name == "precipitation":
                # OWM : rain ou snow optionnels avec sub-keys 1h/3h
                rain = parsed.get("rain")
                snow = parsed.get("snow")
                if isinstance(rain, dict) and rain:
                    variables_extracted["precipitation_rain"] = rain
                if isinstance(snow, dict) and snow:
                    variables_extracted["precipitation_snow"] = snow
                if not rain and not snow:
                    variables_missing.append(
                        "precipitation::no_rain_no_snow_in_response")
                continue
            path = OWM_VARIABLE_PATHS_CURRENT.get(var_name)
            if path:
                val = _extract_path(parsed, path)
                if val is not None:
                    variables_extracted[var_name] = val
                else:
                    variables_missing.append(
                        f"{var_name}::path_{'.'.join(path)}_absent")
            else:
                # Variable inconnue (anti-générique : ne fabrique pas)
                variables_missing.append(
                    f"{var_name}::unknown_path_in_owm_schema")

    # Métadonnées current (anti-générique : champs réels uniquement)
    current_meta: Dict[str, Any] = {}
    if (probe_current["body_is_json"]
            and isinstance(probe_current["parsed_json"], dict)):
        p = probe_current["parsed_json"]
        current_meta = {
            "city_name": p.get("name"),
            "country": (p.get("sys") or {}).get("country"),
            "lat": (p.get("coord") or {}).get("lat"),
            "lon": (p.get("coord") or {}).get("lon"),
            "timezone_offset_seconds": p.get("timezone"),
            "weather_main": (
                (p.get("weather") or [{}])[0].get("main")
                if p.get("weather") else None),
            "weather_desc": (
                (p.get("weather") or [{}])[0].get("description")
                if p.get("weather") else None),
            "cod": p.get("cod"),
            "dt_utc_unix": p.get("dt"),
        }
    # Échantillon forecast (5 premiers points pour cohérence)
    forecast_sample: List[Dict[str, Any]] = []
    if forecast_owm_signature_present:
        for item in (
                probe_forecast["parsed_json"]["list"][:5]):
            if not isinstance(item, dict):
                continue
            forecast_sample.append({
                "dt_unix": item.get("dt"),
                "dt_txt": item.get("dt_txt"),
                "temp": (item.get("main") or {}).get("temp"),
                "humidity": (
                    item.get("main") or {}).get("humidity"),
                "pressure": (
                    item.get("main") or {}).get("pressure"),
                "wind_speed": (
                    item.get("wind") or {}).get("speed"),
                "wind_deg": (
                    item.get("wind") or {}).get("deg"),
                "clouds_all": (
                    item.get("clouds") or {}).get("all"),
                "weather_main": (
                    (item.get("weather") or [{}])[0].get("main")
                    if item.get("weather") else None),
                "rain_3h": (
                    (item.get("rain") or {}).get("3h")),
                "snow_3h": (
                    (item.get("snow") or {}).get("3h")),
            })

    # Verdict doctrinal
    if (current_owm_signature_present
            and forecast_owm_signature_present
            and probe_current["http_status"] == 200
            and probe_forecast["http_status"] == 200):
        verdict = "OWM_ZONE_PIVOT_VALID_BOTH_ENDPOINTS_LIVE"
        valid = True
    elif current_owm_signature_present:
        verdict = "OWM_ZONE_PIVOT_VALID_CURRENT_ONLY_FORECAST_FAILED"
        valid = False
    elif forecast_owm_signature_present:
        verdict = "OWM_ZONE_PIVOT_VALID_FORECAST_ONLY_CURRENT_FAILED"
        valid = False
    elif (probe_current["http_status"] == 401
          or probe_forecast["http_status"] == 401):
        verdict = "OWM_ZONE_PIVOT_INVALID_HTTP_401"
        valid = False
    elif (probe_current["http_status"] == 429
          or probe_forecast["http_status"] == 429):
        verdict = "OWM_ZONE_PIVOT_INVALID_HTTP_429_RATE_LIMITED"
        valid = False
    else:
        verdict = "OWM_ZONE_PIVOT_INVALID_OTHER"
        valid = False

    # Forensic log
    log_forensic_event(
        scope="ENDPOINT_PROBES",
        event=forensic_event,
        details={
            "provider": "OPENWEATHERMAP",
            "endpoint_current": endpoint_current,
            "endpoint_forecast": endpoint_forecast,
            "auth_strategy": auth_strategy,
            "credentials_api_key_masked": creds_token_masked,
            "query_appid_masked": (
                appid_token_masked if appid_in_query else None),
            "current_http_status": probe_current["http_status"],
            "forecast_http_status": probe_forecast["http_status"],
            "current_signature_present": (
                current_owm_signature_present),
            "forecast_signature_present": (
                forecast_owm_signature_present),
            "forecast_n_items": forecast_n_items,
            "n_variables_extracted": len(variables_extracted),
            "n_variables_missing": len(variables_missing),
            "valid": valid,
            "verdict": verdict,
        },
        persist=True,
    )

    # Manifest signé + persistance
    payload = {
        "manifest_id": "OWM_ZONE_PIVOT_Ω",
        "ordre": "P0_OPENWEATHERMAP_PIVOT_TERRITOIRE",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "forensic_event": forensic_event,
        "guardrails_enforced": True,
        "autonomy": "LIMITED",
        "auth_strategy": auth_strategy,
        "endpoint_current": endpoint_current,
        "endpoint_forecast": endpoint_forecast,
        "valid": valid,
        "verdict": verdict,
        "credentials_api_key_masked": creds_token_masked,
        "query_appid_masked": appid_token_masked,
        "query_params_lat": qp.get("lat"),
        "query_params_lon": qp.get("lon"),
        "query_params_units": qp.get("units"),
        "current_owm_signature_present":
            current_owm_signature_present,
        "forecast_owm_signature_present":
            forecast_owm_signature_present,
        "forecast_n_items": forecast_n_items,
        "current_meta": current_meta,
        "forecast_sample_first_5": forecast_sample,
        "variables_requested": vars_req,
        "variables_extracted": variables_extracted,
        "variables_missing": variables_missing,
        "n_variables_extracted": len(variables_extracted),
        "probe_current_summary": {
            "url_masked": probe_current["url_masked"],
            "http_status": probe_current["http_status"],
            "content_type": probe_current["content_type"],
            "body_bytes_read": probe_current["body_bytes_read"],
            "elapsed_ms": probe_current["elapsed_ms"],
            "redirect_detected": probe_current["redirect_detected"],
        },
        "probe_forecast_summary": {
            "url_masked": probe_forecast["url_masked"],
            "http_status": probe_forecast["http_status"],
            "content_type": probe_forecast["content_type"],
            "body_bytes_read": probe_forecast["body_bytes_read"],
            "elapsed_ms": probe_forecast["elapsed_ms"],
            "redirect_detected":
                probe_forecast["redirect_detected"],
        },
        "anti_generique_strict": True,
        "anti_leakage_token_masked": True,
        "v30_lock": "INVIOLÉ",
        "drift_zero": True,
        "no_engine_recompute_triggered": True,
        "executed_at_utc": _utc_now(),
    }
    payload_sha256 = hashlib.sha256(
        json.dumps(payload, sort_keys=True,
                   ensure_ascii=False, default=str).encode("utf-8")
    ).hexdigest()
    payload["manifest_sha256"] = payload_sha256

    persisted: Dict[str, Any] = {}
    if persist:
        PIPELINE_ROOT.mkdir(parents=True, exist_ok=True)
        if OPENWEATHERMAP_ZONE_PIVOT_PATH.exists():
            try:
                state = json.loads(
                    OPENWEATHERMAP_ZONE_PIVOT_PATH.read_text(
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
        state["n_pivots"] = len(state["history"])
        state["last_manifest_sha256"] = payload_sha256
        state["last_verdict"] = verdict
        state["v30_lock"] = "INVIOLÉ"
        OPENWEATHERMAP_ZONE_PIVOT_PATH.write_text(
            json.dumps(state, ensure_ascii=False, indent=2),
            encoding="utf-8")
        persisted["overlay_path"] = str(
            OPENWEATHERMAP_ZONE_PIVOT_PATH)
        persisted["overlay_size_bytes"] = (
            OPENWEATHERMAP_ZONE_PIVOT_PATH.stat().st_size)
        persisted["n_pivots_history"] = state["n_pivots"]

        from engines.v8_institutional.especes.bio_reacteur_overlay_omega import (  # noqa: E501
            persist_audit,
        )
        audit_payload = {
            "audit_type": "NOAA_PIPELINE",
            "subtype": "OWM_ZONE_PIVOT",
            "ordre": "P0_OPENWEATHERMAP_PIVOT_TERRITOIRE",
            "doctrine":
                "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
            "provider": "OPENWEATHERMAP",
            "auth_strategy": auth_strategy,
            "valid": valid,
            "verdict": verdict,
            "manifest_sha256": payload_sha256,
            "current_http_status": probe_current["http_status"],
            "forecast_http_status": probe_forecast["http_status"],
            "n_variables_extracted": len(variables_extracted),
            "forecast_n_items": forecast_n_items,
            "v30_lock_inviolate": True,
            "drift_zero": True,
            "no_engine_recompute_triggered": True,
        }
        persisted["audit_persisted"] = persist_audit(audit_payload)

    payload["persisted_paths"] = persisted
    return payload


# ═════════════════════════════════════════════════════════════════════════
# 14. OPENWEATHERMAP HOOK ACTIVATION (officielle, V30_LOCK FUSION ADD-ONLY)
# ═════════════════════════════════════════════════════════════════════════
OPENWEATHERMAP_HOOK_ACTIVATION_PATH = (
    PIPELINE_ROOT / "openweathermap_hook_activation_overlay.json")


def _find_validated_owm_manifest(
    target_manifest_sha256: str,
) -> Optional[Dict[str, Any]]:
    """Cherche un manifest OWM validé dans l'historique des validations.

    Anti-générique strict : on ne peut activer un hook que sur un
    manifest_sha256 RÉELLEMENT validé (HTTP 200 + signature OWM).
    Retourne None si introuvable ou non-valide.
    """
    if not OPENWEATHERMAP_VALIDATION_PATH.exists():
        return None
    try:
        state = json.loads(
            OPENWEATHERMAP_VALIDATION_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    history = state.get("history", [])
    for entry in history:
        if (entry.get("manifest_sha256") == target_manifest_sha256
                and entry.get("valid") is True
                and entry.get("verdict")
                == "OPENWEATHERMAP_VALID_LIVE_DATA_RETURNED"):
            return entry
    return None


def activate_openweathermap_hook(
    manifest_sha256: str,
    reason: str = "owm_hook_activated",
    persist: bool = True,
) -> Dict[str, Any]:
    """OPENWEATHERMAP_HOOK_ACTIVATE · activation officielle FUSION ADD-ONLY.

    Workflow doctrinal :
      1. Guardrails ENFORCED check (412 sinon)
      2. Vérification ANTI-GÉNÉRIQUE STRICTE : le manifest_sha256 doit
         exister dans OPENWEATHERMAP_VALIDATION_PATH avec valid=True
         et verdict=OPENWEATHERMAP_VALID_LIVE_DATA_RETURNED. Refus
         d'activer un manifest fabriqué.
      3. Construction manifest d'activation signé SHA-256
      4. Forensic log HOOK_ACTIVATIONS/OPENWEATHERMAP_HOOK_ACTIVATE
      5. Persistance overlay history (V30_LOCK FUSION ADD-ONLY)
      6. Audit doctrinal NOAA_PIPELINE/OPENWEATHERMAP_HOOK_ACTIVATE
      7. AUCUN recalcul moteur déclenché ICI (drift audit séparé)

    Args:
      manifest_sha256: SHA-256 du manifest de validation à activer.
      reason: raison doctrinale (default 'owm_hook_activated').
      persist: persister overlay + audit.

    Returns:
      Dict structuré avec verdict + activation_sha256 + lien manifest.
    """
    from engines.v8_institutional.especes.pipeline_guardrails_omega import (
        require_guardrails_enforced, log_forensic_event,
    )
    require_guardrails_enforced("activate_openweathermap_hook")

    t0 = time.time()

    # 1. Anti-générique : le manifest DOIT exister et être validé
    validated_manifest = _find_validated_owm_manifest(
        manifest_sha256)
    if validated_manifest is None:
        verdict = (
            "OPENWEATHERMAP_HOOK_REJECTED_MANIFEST_NOT_FOUND_OR_INVALID")
        activated = False
        activation_payload = {
            "manifest_id": "OPENWEATHERMAP_HOOK_ACTIVATE_Ω",
            "ordre": "P0_OPENWEATHERMAP_HOOK_ACTIVATE",
            "doctrine": (
                "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT"),
            "guardrails_enforced": True,
            "autonomy": "LIMITED",
            "activated": False,
            "verdict": verdict,
            "reason": reason,
            "input_manifest_sha256": manifest_sha256,
            "rejection_explanation": (
                "Le manifest_sha256 fourni n'existe pas dans "
                "OPENWEATHERMAP_VALIDATION_PATH avec valid=True et "
                "verdict=OPENWEATHERMAP_VALID_LIVE_DATA_RETURNED. "
                "Anti-générique strict : impossible d'activer un hook "
                "sur un manifest non validé."),
            "anti_generique_strict": True,
            "v30_lock": "INVIOLÉ",
            "drift_zero": True,
            "no_engine_recompute_triggered": True,
            "executed_at_utc": _utc_now(),
            "elapsed_s": round(time.time() - t0, 3),
        }
        # Forensic log même en cas de rejet
        log_forensic_event(
            scope="HOOK_ACTIVATIONS",
            event="OPENWEATHERMAP_HOOK_ACTIVATE",
            details={
                "input_manifest_sha256": manifest_sha256,
                "reason": reason,
                "activated": False,
                "verdict": verdict,
            },
            persist=True,
        )
        return activation_payload

    # 2. Construction manifest activation officiel
    owm_summary = {
        "endpoint": validated_manifest.get("endpoint"),
        "auth_strategy": validated_manifest.get("auth_strategy"),
        "city_name": validated_manifest.get(
            "probe", {}).get("owm_city_name"),
        "country": validated_manifest.get(
            "probe", {}).get("owm_country"),
        "temp_kelvin_at_validation": validated_manifest.get(
            "probe", {}).get("owm_temp_kelvin"),
        "weather_main_at_validation": validated_manifest.get(
            "probe", {}).get("owm_weather_main"),
        "owm_required_keys_present": validated_manifest.get(
            "probe", {}).get("owm_required_present"),
    }

    activation_payload = {
        "manifest_id": "OPENWEATHERMAP_HOOK_ACTIVATE_Ω",
        "ordre": "P0_OPENWEATHERMAP_HOOK_ACTIVATE",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "guardrails_enforced": True,
        "autonomy": "LIMITED",
        "activated": True,
        "verdict": "OPENWEATHERMAP_HOOK_ACTIVATED_OPERATIONAL",
        "reason": reason,
        "validated_manifest_sha256": manifest_sha256,
        "validated_manifest_executed_at_utc": (
            validated_manifest.get("executed_at_utc")),
        "owm_validation_summary": owm_summary,
        "fusion_add_only": True,
        "anti_generique_strict": True,
        "v30_lock": "INVIOLÉ",
        "drift_zero": True,
        "no_engine_recompute_triggered": True,
        "consumed_by_modules": [
            "PHYSIOLOGIE_THERMIQUE",
            "HABITAT_MICROCLIMAT",
            "NUTRITION_HUMIDITE",
        ],
        "registered_at_utc": _utc_now(),
    }
    activation_sha256 = hashlib.sha256(
        json.dumps(activation_payload, sort_keys=True,
                   ensure_ascii=False, default=str).encode("utf-8")
    ).hexdigest()
    activation_payload["activation_sha256"] = activation_sha256
    activated = True

    persisted: Dict[str, Any] = {}
    if persist:
        PIPELINE_ROOT.mkdir(parents=True, exist_ok=True)
        # FUSION ADD-ONLY history
        if OPENWEATHERMAP_HOOK_ACTIVATION_PATH.exists():
            try:
                state = json.loads(
                    OPENWEATHERMAP_HOOK_ACTIVATION_PATH.read_text(
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
        OPENWEATHERMAP_HOOK_ACTIVATION_PATH.write_text(
            json.dumps(state, ensure_ascii=False, indent=2),
            encoding="utf-8")
        persisted["overlay_path"] = str(
            OPENWEATHERMAP_HOOK_ACTIVATION_PATH)
        persisted["overlay_size_bytes"] = (
            OPENWEATHERMAP_HOOK_ACTIVATION_PATH.stat().st_size)
        persisted["n_activations_history"] = state["n_activations"]

        # Forensic log HOOK_ACTIVATIONS
        log_forensic_event(
            scope="HOOK_ACTIVATIONS",
            event="OPENWEATHERMAP_HOOK_ACTIVATE",
            details={
                "validated_manifest_sha256": manifest_sha256,
                "activation_sha256": activation_sha256,
                "reason": reason,
                "activated": True,
                "verdict": "OPENWEATHERMAP_HOOK_ACTIVATED_OPERATIONAL",
                "owm_city_name": owm_summary["city_name"],
                "owm_country": owm_summary["country"],
            },
            persist=True,
        )

        # Audit doctrinal
        from engines.v8_institutional.especes.bio_reacteur_overlay_omega import (  # noqa: E501
            persist_audit,
        )
        audit_payload = {
            "audit_type": "NOAA_PIPELINE",
            "subtype": "OPENWEATHERMAP_HOOK_ACTIVATE",
            "ordre": "P0_OPENWEATHERMAP_HOOK_ACTIVATE",
            "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
            "provider": "OPENWEATHERMAP",
            "validated_manifest_sha256": manifest_sha256,
            "activation_sha256": activation_sha256,
            "reason": reason,
            "activated": activated,
            "verdict": "OPENWEATHERMAP_HOOK_ACTIVATED_OPERATIONAL",
            "owm_endpoint": owm_summary["endpoint"],
            "owm_auth_strategy": owm_summary["auth_strategy"],
            "owm_city_name": owm_summary["city_name"],
            "v30_lock_inviolate": True,
            "drift_zero": True,
            "no_engine_recompute_triggered": True,
        }
        persisted["audit_persisted"] = persist_audit(audit_payload)

    activation_payload["persisted_paths"] = persisted
    activation_payload["elapsed_s"] = round(time.time() - t0, 3)
    return activation_payload


def get_openweathermap_hook_status() -> Dict[str, Any]:
    """Lit l'état actuel du hook OWM (read-only, V30_LOCK respecté)."""
    if not OPENWEATHERMAP_HOOK_ACTIVATION_PATH.exists():
        return {
            "manifest_id": "OPENWEATHERMAP_HOOK_STATUS_Ω",
            "ordre": "P0_OPENWEATHERMAP_HOOK_ACTIVATE",
            "current_status": "NOT_ACTIVATED",
            "v30_lock": "INVIOLÉ",
            "scanned_at_utc": _utc_now(),
        }
    state = json.loads(
        OPENWEATHERMAP_HOOK_ACTIVATION_PATH.read_text(
            encoding="utf-8"))
    last = (state["history"][-1]
            if state.get("history") else None)
    return {
        "manifest_id": "OPENWEATHERMAP_HOOK_STATUS_Ω",
        "ordre": "P0_OPENWEATHERMAP_HOOK_ACTIVATE",
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
        "overlay_path": str(OPENWEATHERMAP_HOOK_ACTIVATION_PATH),
        "overlay_size_bytes": (
            OPENWEATHERMAP_HOOK_ACTIVATION_PATH.stat().st_size),
        "v30_lock": "INVIOLÉ",
        "scanned_at_utc": _utc_now(),
    }


# ═════════════════════════════════════════════════════════════════════════
# 13. OPENWEATHERMAP API VALIDATION (GET_JSON + double placeholder check)
# ═════════════════════════════════════════════════════════════════════════
OPENWEATHERMAP_VALIDATION_PATH = (
    PIPELINE_ROOT / "openweathermap_validation_overlay.json")


def validate_openweathermap_endpoint(
    endpoint: str = (
        "https://api.openweathermap.org/data/2.5/weather"),
    credentials_api_key: Optional[str] = None,
    query_params: Optional[Dict[str, str]] = None,
    require_http_200: bool = True,
    require_no_redirect: bool = True,
    expect_content_type: str = "application/json",
    persist: bool = True,
    timeout_s: int = 15,
    body_max_bytes: int = 8192,
) -> Dict[str, Any]:
    """OPENWEATHERMAP_P0_VALIDATE · GET_JSON strict avec double placeholder
    detection (credentials_api_key + query_params['appid']) + masquage.

    Workflow doctrinal anti-générique :
      1. Guardrails ENFORCED check (412 sinon)
      2. Détection STRICTE placeholder sur DEUX niveaux :
         · credentials_api_key (Bearer header potentiel)
         · query_params['appid'] (auth OpenWeatherMap canonique)
      3. Sélection du token actif selon priorité :
         · Si appid réel dans query_params → utilisation query auth (OWM)
         · Sinon si credentials_api_key réel → utilisation Bearer header
         · Sinon REJECTED (les deux placeholders)
      4. GET HTTP RÉEL avec NoRedirectHandler (forbid_follow_redirects)
      5. Lecture body JSON limitée (body_max_bytes) avec parsing
      6. Critères stricts : HTTP 200 + content-type=application/json +
         pas de redirect + JSON parsable + champs météo cohérents (anti-
         générique : on vérifie que la réponse est cohérente avec OWM)
      7. Forensic log ENDPOINT_PROBES/OPENWEATHERMAP_VALIDATE (token masqué)
      8. Persistance overlay + audit doctrinal
      9. AUCUN recalcul moteur · V30_LOCK + DRIFT_ZERO

    Anti-leakage : tous les tokens (header ET query) sont masqués dans
    logs/persistence, mais utilisés en clair dans la requête HTTP réelle.
    """
    from engines.v8_institutional.especes.pipeline_guardrails_omega import (
        require_guardrails_enforced, log_forensic_event,
    )
    require_guardrails_enforced("validate_openweathermap_endpoint")

    if not endpoint.startswith(("https://", "http://")):
        raise ValueError(
            f"ENDPOINT_INVALID::not_http_url::{endpoint[:120]}")

    import urllib.request
    import urllib.error
    from urllib.parse import urlencode

    qp = dict(query_params or {})
    appid_in_query = qp.get("appid")

    # Détection placeholder DOUBLE niveau
    creds_placeholder = _is_placeholder_token(credentials_api_key)
    appid_placeholder = _is_placeholder_token(appid_in_query)
    creds_token_masked = _mask_token(credentials_api_key)
    appid_token_masked = _mask_token(appid_in_query)

    # Décision auth (anti-générique strict : ne JAMAIS envoyer placeholder)
    use_query_auth = (
        bool(appid_in_query) and not appid_placeholder)
    use_header_auth = (
        (not use_query_auth)
        and bool(credentials_api_key)
        and not creds_placeholder)
    auth_strategy = (
        "QUERY_PARAM_APPID" if use_query_auth
        else "BEARER_HEADER" if use_header_auth
        else "NONE_BOTH_PLACEHOLDERS")

    class NoRedirectHandler(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg,
                              headers, newurl):
            return None

    # Préparation URL réelle (auth en clair) ET URL masquée (pour persist)
    qp_real = dict(qp)
    qp_masked = dict(qp)
    if "appid" in qp_real:
        qp_masked["appid"] = appid_token_masked
    if qp_real:
        url_real = endpoint + "?" + urlencode(qp_real)
        url_masked = endpoint + "?" + urlencode(qp_masked)
    else:
        url_real = endpoint
        url_masked = endpoint

    record_probe: Dict[str, Any] = {
        "url_masked": url_masked,
        "method": "GET",
        "follow_redirects": False,
        "auth_strategy": auth_strategy,
        "credentials_api_key_masked": creds_token_masked,
        "credentials_placeholder_detected": creds_placeholder,
        "query_appid_masked": (
            appid_token_masked if appid_in_query else None),
        "query_appid_placeholder_detected": appid_placeholder,
        "http_status": None,
        "content_type": None,
        "content_length_actual": None,
        "headers_subset": {},
        "body_bytes_read": 0,
        "body_is_json": False,
        "json_parse_error": None,
        "json_keys_top_level": None,
        "json_owm_signature_present": False,
        "elapsed_ms": None,
        "reason": None,
        "redirect_detected": False,
        "redirect_location": None,
    }

    # Court-circuit doctrinal : si aucune auth valide, on ne fait pas
    # la requête (anti-générique : ne pas spammer l'API publique sans
    # credentials valides).
    if auth_strategy == "NONE_BOTH_PLACEHOLDERS":
        record_probe["reason"] = (
            "no_valid_auth::both_placeholders_detected")
        record_probe["elapsed_ms"] = 0.0
        verdict = (
            "OPENWEATHERMAP_REJECTED_BOTH_PLACEHOLDERS_DETECTED")
        valid = False
        next_action = (
            "REJECTED — credentials.api_key ET query_params.appid sont "
            "tous deux des placeholders. Aucune requête HTTP émise. "
            "Le Commandant doit fournir un token OWM réel dans l'un "
            "des deux champs.")
    else:
        t0 = time.time()
        try:
            opener = urllib.request.build_opener(NoRedirectHandler)
            req_headers: Dict[str, str] = {
                "User-Agent": (
                    "BCE-4X-OPENWEATHERMAP-VALIDATE/1.0"),
                "Accept": "application/json",
            }
            if use_header_auth:
                req_headers["Authorization"] = (
                    f"Bearer {credentials_api_key}")
            req = urllib.request.Request(
                url_real, method="GET", headers=req_headers)
            with opener.open(req, timeout=timeout_s) as resp:
                record_probe["http_status"] = resp.status
                headers = dict(resp.headers)
                record_probe["content_type"] = headers.get(
                    "Content-Type", headers.get("content-type"))
                cl = headers.get(
                    "Content-Length", headers.get("content-length"))
                try:
                    record_probe["content_length_actual"] = (
                        int(cl) if cl else None)
                except (TypeError, ValueError):
                    record_probe["content_length_actual"] = None
                record_probe["headers_subset"] = {
                    k: v for k, v in headers.items()
                    if k.lower() in (
                        "content-type", "content-length", "etag",
                        "x-cache-key", "x-ratelimit-remaining",
                        "server", "via", "cache-control")
                }
                # Lecture body limitée (anti-générique)
                body = resp.read(body_max_bytes)
                record_probe["body_bytes_read"] = len(body)
                # Parse JSON (anti-générique : signature OWM)
                try:
                    parsed = json.loads(
                        body.decode("utf-8", errors="replace"))
                    record_probe["body_is_json"] = True
                    if isinstance(parsed, dict):
                        record_probe["json_keys_top_level"] = (
                            sorted(parsed.keys()))
                        # Signature OWM canonique : champs typiques
                        owm_required = {"weather", "main", "name"}
                        owm_optional = {"coord", "wind", "sys", "id"}
                        present = set(parsed.keys())
                        record_probe[
                            "json_owm_signature_present"] = (
                            owm_required.issubset(present))
                        record_probe["owm_required_present"] = (
                            sorted(owm_required & present))
                        record_probe["owm_optional_present"] = (
                            sorted(owm_optional & present))
                        # Capter quelques champs anti-générique
                        if "name" in parsed:
                            record_probe["owm_city_name"] = (
                                str(parsed["name"])[:50])
                        if "sys" in parsed and isinstance(
                                parsed["sys"], dict):
                            record_probe["owm_country"] = (
                                str(parsed["sys"].get(
                                    "country", ""))[:5])
                        if "main" in parsed and isinstance(
                                parsed["main"], dict):
                            record_probe["owm_temp_kelvin"] = (
                                parsed["main"].get("temp"))
                        if "weather" in parsed and isinstance(
                                parsed["weather"], list) and (
                                parsed["weather"]):
                            w0 = parsed["weather"][0]
                            if isinstance(w0, dict):
                                record_probe[
                                    "owm_weather_main"] = (
                                    str(w0.get("main", ""))[:30])
                                record_probe[
                                    "owm_weather_desc"] = (
                                    str(w0.get(
                                        "description", ""))[:50])
                        if "cod" in parsed:
                            record_probe["owm_response_code"] = (
                                parsed.get("cod"))
                except json.JSONDecodeError as e:
                    record_probe["json_parse_error"] = str(e)[:200]
                    record_probe["body_preview_first_300b"] = (
                        body[:300].decode(
                            "utf-8", errors="replace"))
        except urllib.error.HTTPError as e:
            record_probe["http_status"] = e.code
            record_probe["reason"] = f"http_error_{e.code}"
            try:
                body = e.read(800)
                record_probe["body_preview_first_500b"] = (
                    body[:500].decode("utf-8", errors="replace"))
                # Tentative parse JSON sur erreur (OWM renvoie JSON erreurs)
                try:
                    err_json = json.loads(
                        body.decode("utf-8", errors="replace"))
                    record_probe["error_json_parsed"] = err_json
                except json.JSONDecodeError:
                    pass
            except Exception:
                pass
            if 300 <= e.code < 400:
                record_probe["redirect_detected"] = True
                try:
                    record_probe["redirect_location"] = (
                        e.headers.get("Location"))
                except Exception:
                    pass
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            record_probe["reason"] = (
                f"network_error::{str(e)[:160]}")
        record_probe["elapsed_ms"] = round(
            (time.time() - t0) * 1000, 1)

        # Verdict OPenWeatherMap-aware (anti-générique strict)
        ct = record_probe["content_type"] or ""
        ct_acceptable = (expect_content_type.lower() in ct.lower())
        if (record_probe["http_status"] == 200
                and ct_acceptable
                and record_probe["body_is_json"]
                and record_probe["json_owm_signature_present"]
                and not record_probe["redirect_detected"]):
            verdict = "OPENWEATHERMAP_VALID_LIVE_DATA_RETURNED"
            valid = True
            next_action = (
                "ACCEPTED — endpoint OWM répond HTTP 200 application/"
                "json avec signature OWM canonique (weather + main + "
                "name présents). Données météo réelles confirmées. "
                "Await Commandant confirm to register as official "
                "OWM hook source.")
        elif (record_probe["http_status"] == 200
                and record_probe["body_is_json"]
                and not record_probe["json_owm_signature_present"]):
            verdict = (
                "OPENWEATHERMAP_INVALID_HTTP_200_BUT_NO_OWM_SIGNATURE")
            valid = False
            next_action = (
                "REJECTED — HTTP 200 JSON mais signature OWM absente. "
                "L'endpoint répond mais ne semble pas servir l'API "
                "OpenWeatherMap canonique.")
        elif record_probe["http_status"] == 401:
            verdict = "OPENWEATHERMAP_INVALID_HTTP_401_INVALID_API_KEY"
            valid = False
            next_action = (
                "REJECTED — HTTP 401 : l'appid OWM fourni est "
                "invalide ou en attente d'activation (les nouvelles "
                "clés OWM peuvent prendre 2h à s'activer).")
        elif record_probe["http_status"] == 404:
            verdict = "OPENWEATHERMAP_INVALID_HTTP_404"
            valid = False
            next_action = (
                "REJECTED — HTTP 404 : ressource OWM introuvable.")
        elif record_probe["http_status"] == 429:
            verdict = (
                "OPENWEATHERMAP_INVALID_HTTP_429_RATE_LIMITED")
            valid = False
            next_action = (
                "REJECTED — HTTP 429 : quota OWM dépassé.")
        elif record_probe["redirect_detected"]:
            verdict = "OPENWEATHERMAP_INVALID_REDIRECT_DETECTED"
            valid = False
            next_action = (
                "REJECTED — redirect détecté.")
        else:
            verdict = "OPENWEATHERMAP_INVALID_OTHER"
            valid = False
            next_action = (
                "REJECTED — verdict autre. Voir probe_record.")

    criteria_evaluation = {
        "expect_http_200": require_http_200,
        "expect_content_type": expect_content_type,
        "expect_no_redirect": require_no_redirect,
        "http_200_satisfied": (record_probe["http_status"] == 200),
        "no_redirect_satisfied": (
            not record_probe["redirect_detected"]),
        "content_type_satisfied": (
            expect_content_type.lower() in (
                record_probe["content_type"] or "").lower()),
        "body_is_json": record_probe["body_is_json"],
        "json_owm_signature_present": (
            record_probe["json_owm_signature_present"]),
        "auth_strategy": auth_strategy,
        "credentials_placeholder_detected": creds_placeholder,
        "query_appid_placeholder_detected": appid_placeholder,
    }

    # Forensic log ENDPOINT_PROBES (TOKENS MASQUÉS)
    log_forensic_event(
        scope="ENDPOINT_PROBES",
        event="OPENWEATHERMAP_VALIDATE",
        details={
            "provider": "OPENWEATHERMAP",
            "url_masked": url_masked,
            "auth_strategy": auth_strategy,
            "credentials_api_key_masked": creds_token_masked,
            "credentials_placeholder_detected": creds_placeholder,
            "query_appid_masked": (
                appid_token_masked if appid_in_query else None),
            "query_appid_placeholder_detected": appid_placeholder,
            "http_status": record_probe["http_status"],
            "content_type": record_probe["content_type"],
            "owm_signature_present": (
                record_probe["json_owm_signature_present"]),
            "owm_city_name": record_probe.get("owm_city_name"),
            "valid": valid,
            "verdict": verdict,
            "elapsed_ms": record_probe["elapsed_ms"],
        },
        persist=True,
    )

    # Manifest signé + persistance
    payload = {
        "manifest_id": "OPENWEATHERMAP_VALIDATE_Ω",
        "ordre": "OPENWEATHERMAP_P0_VALIDATE",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "guardrails_enforced": True,
        "autonomy": "LIMITED",
        "provider": "OPENWEATHERMAP",
        "endpoint": endpoint,
        "auth_strategy": auth_strategy,
        "probe": record_probe,
        "criteria_evaluation": criteria_evaluation,
        "valid": valid,
        "verdict": verdict,
        "next_action": next_action,
        "anti_generique_strict": True,
        "anti_leakage_token_masked": True,
        "v30_lock": "INVIOLÉ",
        "drift_zero": True,
        "no_engine_recompute_triggered": True,
        "executed_at_utc": _utc_now(),
    }
    payload_sha256 = hashlib.sha256(
        json.dumps(payload, sort_keys=True,
                   ensure_ascii=False, default=str).encode("utf-8")
    ).hexdigest()
    payload["manifest_sha256"] = payload_sha256

    persisted: Dict[str, Any] = {}
    if persist:
        PIPELINE_ROOT.mkdir(parents=True, exist_ok=True)
        if OPENWEATHERMAP_VALIDATION_PATH.exists():
            try:
                state = json.loads(
                    OPENWEATHERMAP_VALIDATION_PATH.read_text(
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
        OPENWEATHERMAP_VALIDATION_PATH.write_text(
            json.dumps(state, ensure_ascii=False, indent=2),
            encoding="utf-8")
        persisted["overlay_path"] = str(
            OPENWEATHERMAP_VALIDATION_PATH)
        persisted["overlay_size_bytes"] = (
            OPENWEATHERMAP_VALIDATION_PATH.stat().st_size)
        persisted["n_validations_history"] = state["n_validations"]

        from engines.v8_institutional.especes.bio_reacteur_overlay_omega import (  # noqa: E501
            persist_audit,
        )
        audit_payload = {
            "audit_type": "NOAA_PIPELINE",
            "subtype": "OPENWEATHERMAP_VALIDATE",
            "ordre": "OPENWEATHERMAP_P0_VALIDATE",
            "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
            "provider": "OPENWEATHERMAP",
            "endpoint": endpoint,
            "auth_strategy": auth_strategy,
            "valid": valid,
            "verdict": verdict,
            "manifest_sha256": payload_sha256,
            "http_status": record_probe["http_status"],
            "owm_signature_present": (
                record_probe["json_owm_signature_present"]),
            "owm_city_name": record_probe.get("owm_city_name"),
            "credentials_placeholder_detected": creds_placeholder,
            "query_appid_placeholder_detected": appid_placeholder,
            "v30_lock_inviolate": True,
            "drift_zero": True,
            "no_engine_recompute_triggered": True,
        }
        persisted["audit_persisted"] = persist_audit(audit_payload)

    payload["persisted_paths"] = persisted
    return payload


# ═════════════════════════════════════════════════════════════════════════
# 12. COPERNICUS API VALIDATION (HEAD_ONLY + détection placeholder strict)
# ═════════════════════════════════════════════════════════════════════════
COPERNICUS_API_VALIDATION_PATH = (
    PIPELINE_ROOT / "copernicus_api_validation_overlay.json")

# Anti-générique strict : détection des tokens placeholder template.
# Toute valeur appartenant à ce set ne sera jamais envoyée comme Bearer.
COPERNICUS_API_PLACEHOLDERS = {
    "VOTRE_TOKEN_ICI",
    "VOTRE_API_KEY",
    "VOTRE_TOKEN",
    "YOUR_TOKEN_HERE",
    "YOUR_API_KEY",
    "API_KEY",
    "TOKEN",
    "PLACEHOLDER",
    "TODO",
    "TBD",
    "REPLACE_ME",
    "<YOUR_TOKEN>",
    "<API_KEY>",
    "XXX",
    "XXXXX",
    "FILL_ME",
    "EXAMPLE_TOKEN",
    "DEMO_TOKEN",
    "TEST_TOKEN",
    "",
}


def _mask_token(token: Optional[str]) -> str:
    """Masque un token pour logs/payload (anti-leakage strict)."""
    if not token:
        return "***NULL_OR_EMPTY***"
    n = len(token)
    if n <= 4:
        return f"***MASKED({n}_CHARS)***"
    return f"***MASKED({n}_CHARS_HEAD={token[:2]}...TAIL={token[-2:]})***"


def _is_placeholder_token(api_key: Optional[str]) -> bool:
    """Détecte un token placeholder template (anti-générique strict).

    Retourne True si le token est manifestement un placeholder (vide,
    None, ou appartient au set canonique des placeholders templates).
    Insensible à la casse, trim espaces.
    """
    if not api_key:
        return True
    cleaned = api_key.strip().upper()
    if cleaned in {p.upper() for p in COPERNICUS_API_PLACEHOLDERS}:
        return True
    # Heuristiques additionnelles anti-générique
    if cleaned.startswith("<") and cleaned.endswith(">"):
        return True  # <YOUR_TOKEN> patterns
    # Patterns français/anglais (vous/tu/ma/mon) + your
    for prefix in ("VOTRE_", "YOUR_", "TON_", "TA_",
                   "MON_", "MA_", "MES_"):
        if prefix in cleaned:
            return True
    return False


def validate_copernicus_api_endpoint(
    endpoint: str = (
        "https://data.marine.copernicus.eu/api/v1/products"),
    api_key: Optional[str] = None,
    require_http_200: bool = True,
    require_no_redirect: bool = True,
    expect_content_type: str = "application/json",
    persist: bool = True,
    timeout_s: int = 15,
) -> Dict[str, Any]:
    """COPERNICUS_API_P0_VALIDATE · HEAD_ONLY strict avec détection
    placeholder token.

    Workflow doctrinal :
      1. Guardrails ENFORCED check (412 sinon)
      2. Détection ANTI-GÉNÉRIQUE STRICT du placeholder token
      3. Si placeholder → probe SANS Authorization + verdict explicite
         REJECTED_PLACEHOLDER_TOKEN. Le token n'est JAMAIS envoyé.
      4. Si token réel → HEAD HTTP avec Bearer (token masqué dans logs)
      5. Critères stricts : HTTP 200 + content-type=application/json +
         pas de redirect
      6. Forensic log ENDPOINT_PROBES/COPERNICUS_API_VALIDATE (token
         toujours masqué)
      7. Persistance overlay + audit doctrinal
      8. AUCUN recalcul moteur · V30_LOCK + DRIFT_ZERO maintenus

    Anti-leakage : le token complet n'apparaît JAMAIS en log/persistence,
    uniquement masque (longueur + 2 premiers/derniers chars).
    """
    from engines.v8_institutional.especes.pipeline_guardrails_omega import (
        require_guardrails_enforced, log_forensic_event,
    )
    require_guardrails_enforced("validate_copernicus_api_endpoint")

    if not endpoint.startswith(("https://", "http://")):
        raise ValueError(
            f"ENDPOINT_INVALID::not_http_url::{endpoint[:120]}")

    import urllib.request
    import urllib.error

    # 1. Détection placeholder anti-générique
    placeholder_detected = _is_placeholder_token(api_key)
    token_masked = _mask_token(api_key)
    auth_header_set = False

    class NoRedirectHandler(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg,
                              headers, newurl):
            return None

    record_probe: Dict[str, Any] = {
        "url": endpoint,
        "method": "HEAD",
        "follow_redirects": False,
        "auth_header_set": False,
        "token_masked": token_masked,
        "placeholder_detected": placeholder_detected,
        "http_status": None,
        "content_type": None,
        "content_length": None,
        "headers_subset": {},
        "elapsed_ms": None,
        "reason": None,
        "redirect_detected": False,
        "redirect_location": None,
    }

    t0 = time.time()
    try:
        opener = urllib.request.build_opener(NoRedirectHandler)
        req_headers: Dict[str, str] = {
            "User-Agent": (
                "BCE-4X-COPERNICUS-API-VALIDATE/1.0"),
            "Accept": "application/json",
        }
        # Anti-générique : ne JAMAIS envoyer un placeholder comme Bearer
        if api_key and not placeholder_detected:
            req_headers["Authorization"] = f"Bearer {api_key}"
            auth_header_set = True
            record_probe["auth_header_set"] = True
        req = urllib.request.Request(
            endpoint, method="HEAD", headers=req_headers)
        with opener.open(req, timeout=timeout_s) as resp:
            record_probe["http_status"] = resp.status
            headers = dict(resp.headers)
            record_probe["content_type"] = headers.get(
                "Content-Type", headers.get("content-type"))
            cl = headers.get(
                "Content-Length", headers.get("content-length"))
            try:
                record_probe["content_length"] = (
                    int(cl) if cl else None)
            except (TypeError, ValueError):
                record_probe["content_length"] = None
            record_probe["headers_subset"] = {
                k: v for k, v in headers.items()
                if k.lower() in (
                    "content-type", "content-length", "etag",
                    "last-modified", "server", "x-ratelimit-limit",
                    "x-ratelimit-remaining", "www-authenticate",
                    "cache-control", "via")
            }
    except urllib.error.HTTPError as e:
        record_probe["http_status"] = e.code
        record_probe["reason"] = f"http_error_{e.code}"
        try:
            body = e.read(800)
            record_probe["body_preview_first_500b"] = body[:500].decode(
                "utf-8", errors="replace")
        except Exception:
            pass
        if 300 <= e.code < 400:
            record_probe["redirect_detected"] = True
            try:
                record_probe["redirect_location"] = (
                    e.headers.get("Location"))
            except Exception:
                pass
        # Capture www-authenticate si 401/403
        if e.code in (401, 403):
            try:
                record_probe["www_authenticate"] = (
                    e.headers.get("WWW-Authenticate"))
            except Exception:
                pass
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        record_probe["reason"] = f"network_error::{str(e)[:160]}"
    record_probe["elapsed_ms"] = round((time.time() - t0) * 1000, 1)

    # 2. Évaluation des critères stricts + verdict ANTI-GÉNÉRIQUE
    ct = record_probe["content_type"] or ""
    ct_acceptable = (expect_content_type.lower() in ct.lower())
    criteria_evaluation = {
        "expect_http_200": require_http_200,
        "expect_content_type": expect_content_type,
        "expect_no_redirect": require_no_redirect,
        "http_200_satisfied": (record_probe["http_status"] == 200),
        "no_redirect_satisfied": (
            not record_probe["redirect_detected"]),
        "content_type_satisfied": ct_acceptable,
        "auth_header_was_sent": auth_header_set,
        "placeholder_token_detected": placeholder_detected,
    }

    # Verdict doctrinal anti-générique strict
    if placeholder_detected:
        verdict = (
            "COPERNICUS_API_REJECTED_PLACEHOLDER_TOKEN_DETECTED")
        valid = False
        next_action = (
            "REJECTED — token reçu est un placeholder template "
            "(`VOTRE_TOKEN_ICI` ou similaire). Anti-générique strict : "
            "n'a JAMAIS été envoyé en tant que Bearer. Le Commandant "
            "doit fournir un token Copernicus Marine RÉEL.")
    elif (record_probe["http_status"] == 200
            and ct_acceptable
            and not record_probe["redirect_detected"]):
        verdict = "COPERNICUS_API_VALID_ENDPOINT_AUTHENTICATED"
        valid = True
        next_action = (
            "ACCEPTED — endpoint répond HTTP 200 application/json "
            "avec auth Bearer valide. Await Commandant confirm to "
            "register as official source.")
    elif record_probe["http_status"] == 401:
        verdict = (
            "COPERNICUS_API_INVALID_HTTP_401_UNAUTHORIZED")
        valid = False
        next_action = (
            "REJECTED — HTTP 401 Unauthorized. Le token Copernicus "
            "fourni n'est pas valide ou a expiré. Le Commandant doit "
            "régénérer un token sur data.marine.copernicus.eu.")
    elif record_probe["http_status"] == 403:
        verdict = "COPERNICUS_API_INVALID_HTTP_403_FORBIDDEN"
        valid = False
        next_action = (
            "REJECTED — HTTP 403 Forbidden. Le token n'a pas les "
            "permissions requises pour cet endpoint.")
    elif record_probe["http_status"] == 404:
        verdict = "COPERNICUS_API_INVALID_HTTP_404_NOT_FOUND"
        valid = False
        next_action = (
            "REJECTED — HTTP 404 : l'endpoint API n'existe pas à "
            "cette URL. Le Commandant doit fournir l'URL correcte.")
    elif record_probe["redirect_detected"]:
        verdict = "COPERNICUS_API_INVALID_REDIRECT_DETECTED"
        valid = False
        next_action = (
            "REJECTED — redirect détecté (forbid_follow_redirects=True). "
            "L'endpoint ne sert pas directement la ressource demandée.")
    elif (record_probe["http_status"] == 200 and not ct_acceptable):
        verdict = (
            f"COPERNICUS_API_INVALID_CONTENT_TYPE::"
            f"{ct[:80]}")
        valid = False
        next_action = (
            f"REJECTED — HTTP 200 mais content-type "
            f"({ct[:80]}) ≠ {expect_content_type}.")
    else:
        verdict = "COPERNICUS_API_INVALID_OTHER"
        valid = False
        next_action = (
            "REJECTED — verdict autre (status/network). "
            "Voir probe_record pour détails.")

    # 3. Forensic log ENDPOINT_PROBES (TOKEN MASQUÉ STRICT)
    log_forensic_event(
        scope="ENDPOINT_PROBES",
        event="COPERNICUS_API_VALIDATE",
        details={
            "provider": "COPERNICUS_MARINE_API",
            "endpoint": endpoint,
            "http_status": record_probe["http_status"],
            "content_type": record_probe["content_type"],
            "auth_header_was_sent": auth_header_set,
            "token_masked": token_masked,
            "placeholder_detected": placeholder_detected,
            "valid": valid,
            "verdict": verdict,
            "elapsed_ms": record_probe["elapsed_ms"],
        },
        persist=True,
    )

    # 4. Manifest signé + persistance (TOKEN MASQUÉ EN PERSISTENCE)
    payload = {
        "manifest_id": "COPERNICUS_API_VALIDATE_Ω",
        "ordre": "COPERNICUS_API_P0_VALIDATE",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "guardrails_enforced": True,
        "autonomy": "LIMITED",
        "provider": "COPERNICUS_MARINE_API",
        "endpoint": endpoint,
        "probe": record_probe,
        "criteria_evaluation": criteria_evaluation,
        "valid": valid,
        "verdict": verdict,
        "next_action": next_action,
        "anti_generique_strict": True,
        "anti_leakage_token_masked": True,
        "v30_lock": "INVIOLÉ",
        "drift_zero": True,
        "no_engine_recompute_triggered": True,
        "executed_at_utc": _utc_now(),
    }
    payload_sha256 = hashlib.sha256(
        json.dumps(payload, sort_keys=True,
                   ensure_ascii=False, default=str).encode("utf-8")
    ).hexdigest()
    payload["manifest_sha256"] = payload_sha256

    persisted: Dict[str, Any] = {}
    if persist:
        PIPELINE_ROOT.mkdir(parents=True, exist_ok=True)
        if COPERNICUS_API_VALIDATION_PATH.exists():
            try:
                state = json.loads(
                    COPERNICUS_API_VALIDATION_PATH.read_text(
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
        COPERNICUS_API_VALIDATION_PATH.write_text(
            json.dumps(state, ensure_ascii=False, indent=2),
            encoding="utf-8")
        persisted["overlay_path"] = str(
            COPERNICUS_API_VALIDATION_PATH)
        persisted["overlay_size_bytes"] = (
            COPERNICUS_API_VALIDATION_PATH.stat().st_size)
        persisted["n_validations_history"] = state["n_validations"]

        from engines.v8_institutional.especes.bio_reacteur_overlay_omega import (  # noqa: E501
            persist_audit,
        )
        audit_payload = {
            "audit_type": "NOAA_PIPELINE",
            "subtype": "COPERNICUS_API_VALIDATE",
            "ordre": "COPERNICUS_API_P0_VALIDATE",
            "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
            "provider": "COPERNICUS_MARINE_API",
            "endpoint": endpoint,
            "valid": valid,
            "verdict": verdict,
            "manifest_sha256": payload_sha256,
            "http_status": record_probe["http_status"],
            "auth_header_was_sent": auth_header_set,
            "placeholder_detected": placeholder_detected,
            "v30_lock_inviolate": True,
            "drift_zero": True,
            "no_engine_recompute_triggered": True,
        }
        persisted["audit_persisted"] = persist_audit(audit_payload)

    payload["persisted_paths"] = persisted
    payload["elapsed_s"] = round(time.time() - t0, 3)
    return payload


# ═════════════════════════════════════════════════════════════════════════
# 11. NOAA CFSV2 CATALOGUE CARTOGRAPHY (NCEI THREDDS, GET XML strict)
# ═════════════════════════════════════════════════════════════════════════
CFSV2_CATALOGUE_CARTOGRAPHY_PATH = (
    PIPELINE_ROOT / "cfsv2_catalogue_cartography_overlay.json")


def cartograph_ncei_catalogue(
    root_catalog_url: str = (
        "https://www.ncei.noaa.gov/thredds/catalog/"
        "cfsr/mon/pgbh/catalog.xml"),
    max_depth: int = 2,
    max_datasets: int = 128,
    timeout_s: int = 15,
    persist: bool = True,
    provider: str = "NCEI_THREDDS_CFSR_MONTHLY",
    forensic_event: str = "CFSV2_CATALOGUE_CARTOGRAPHY",
    ordre: str = "NOAA_CFSV2_P0_CATALOGUE_CARTOGRAPHY",
    base_dodsc_url: Optional[str] = None,
    base_fileserver_url: Optional[str] = None,
) -> Dict[str, Any]:
    """NOAA_CFSV2_P0_CATALOGUE_CARTOGRAPHY · NCEI THREDDS browse XML strict.

    Contraintes doctrinales (NOAA_CFSV2_P0_CATALOGUE_CARTOGRAPHY) :
      · mode             : CATALOGUE_BROWSE_ONLY (aucun téléchargement)
      · allow_http_methods: ["GET"] (HEAD/POST interdits)
      · allow_content_types: ["application/xml", "text/xml"]
      · forbid_binary_probe: true (jamais de fichiers .nc/.grb2)
      · forbid_follow_redirects: true
      · max_depth         : 2 (récursion BFS limitée)
      · max_datasets      : 128 (capping strict)
      · guardrails ENFORCED requis · autonomy=LIMITED

    Anti-générique strict : aucune fabrication. Tous les datasets/refs
    proviennent du parsing XML réel du serveur NCEI.

    Returns:
      Dict structuré avec :
        · visited_catalogs : liste des catalog.xml parcourus + status réel
        · discovered_datasets : datasets feuilles (max 128) avec urlPath
        · discovered_catalog_refs : sub-catalogues détectés
        · capped : True si max_datasets atteint
        · manifest_sha256 : signature traçabilité
    """
    from engines.v8_institutional.especes.pipeline_guardrails_omega import (
        require_guardrails_enforced, log_forensic_event,
    )
    require_guardrails_enforced("cartograph_ncei_catalogue")

    if not root_catalog_url.startswith(("https://", "http://")):
        raise ValueError(
            f"ROOT_CATALOG_INVALID::not_http_url::"
            f"{root_catalog_url[:120]}")

    import urllib.request
    import urllib.error
    from urllib.parse import urljoin
    import xml.etree.ElementTree as ET

    THREDDS_NS = (
        "{http://www.unidata.ucar.edu/namespaces/thredds/"
        "InvCatalog/v1.0}")
    XLINK_NS = "{http://www.w3.org/1999/xlink}"
    MAX_BODY_BYTES = 2_000_000  # 2 MB cap (anti-générique)

    class NoRedirectHandler(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg,
                              headers, newurl):
            return None

    t_total = time.time()
    visited_catalogs: List[Dict[str, Any]] = []
    discovered_datasets: List[Dict[str, Any]] = []
    discovered_catalog_refs: List[Dict[str, Any]] = []
    visited_urls: set = set()
    queue: List[tuple] = [(root_catalog_url, 0)]
    capped = False

    while queue:
        if len(discovered_datasets) >= max_datasets:
            capped = True
            break
        cat_url, depth = queue.pop(0)
        if cat_url in visited_urls or depth > max_depth:
            continue
        visited_urls.add(cat_url)

        record: Dict[str, Any] = {
            "url": cat_url,
            "depth": depth,
            "method": "GET",
            "http_status": None,
            "content_type": None,
            "ctype_acceptable": False,
            "redirect_detected": False,
            "n_datasets_in_catalog": 0,
            "n_catalogrefs_in_catalog": 0,
            "elapsed_ms": None,
            "reason": None,
            "body_bytes_read": 0,
        }
        body: Optional[bytes] = None
        t0 = time.time()
        try:
            opener = urllib.request.build_opener(NoRedirectHandler)
            req = urllib.request.Request(
                cat_url, method="GET",
                headers={
                    "User-Agent": (
                        "BCE-4X-NCEI-CATALOGUE-CARTOGRAPHY/1.0"),
                    "Accept": "application/xml, text/xml",
                })
            with opener.open(req, timeout=timeout_s) as resp:
                record["http_status"] = resp.status
                ct = (resp.headers.get("Content-Type") or "")
                record["content_type"] = ct
                # Validation stricte content-type (XML uniquement)
                ct_lower = ct.lower()
                ctype_ok = (
                    "application/xml" in ct_lower
                    or "text/xml" in ct_lower)
                record["ctype_acceptable"] = ctype_ok
                if ctype_ok and resp.status == 200:
                    body = resp.read(MAX_BODY_BYTES)
                    record["body_bytes_read"] = len(body)
                elif not ctype_ok:
                    record["reason"] = (
                        f"content_type_not_xml::{ct[:80]}")
        except urllib.error.HTTPError as e:
            record["http_status"] = e.code
            record["reason"] = f"http_error_{e.code}"
            if 300 <= e.code < 400:
                record["redirect_detected"] = True
                try:
                    record["redirect_location"] = (
                        e.headers.get("Location"))
                except Exception:
                    pass
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            record["reason"] = f"network_error::{str(e)[:120]}"
        record["elapsed_ms"] = round((time.time() - t0) * 1000, 1)

        # Forensic log par catalogue visité (event configurable)
        log_forensic_event(
            scope="ENDPOINT_PROBES",
            event=forensic_event,
            details={
                "provider": provider,
                "url": cat_url,
                "depth": depth,
                "http_status": record["http_status"],
                "content_type": record["content_type"],
                "ctype_acceptable": record["ctype_acceptable"],
                "redirect_detected": record["redirect_detected"],
                "elapsed_ms": record["elapsed_ms"],
                "reason": record["reason"],
            },
            persist=True,
        )

        # Parse XML strict (anti-générique : datasets et catalogRefs réels)
        if body and record["ctype_acceptable"]:
            try:
                xroot = ET.fromstring(body)
                # Datasets feuilles (avec urlPath)
                for ds in xroot.iter(f"{THREDDS_NS}dataset"):
                    if len(discovered_datasets) >= max_datasets:
                        capped = True
                        break
                    name = ds.get("name")
                    url_path = ds.get("urlPath")
                    ds_id = ds.get("ID")
                    # Capter taille si présente (<dataSize ...>)
                    data_size_bytes = None
                    for ds_size in ds.iter(f"{THREDDS_NS}dataSize"):
                        try:
                            data_size_bytes = int(
                                float(ds_size.text or "0"))
                        except (ValueError, TypeError):
                            pass
                        break
                    if url_path:
                        # URLs candidates (provider-aware, anti-générique)
                        if base_dodsc_url:
                            opendap_url = (
                                base_dodsc_url.rstrip("/") + "/"
                                + url_path.lstrip("/"))
                        else:
                            opendap_url = (
                                "https://www.ncei.noaa.gov/thredds/dodsC/"
                                + url_path.lstrip("/"))
                        if base_fileserver_url:
                            http_url = (
                                base_fileserver_url.rstrip("/") + "/"
                                + url_path.lstrip("/"))
                        else:
                            http_url = (
                                "https://www.ncei.noaa.gov/thredds/"
                                "fileServer/" + url_path.lstrip("/"))
                        discovered_datasets.append({
                            "name": name,
                            "id": ds_id,
                            "url_path": url_path,
                            "opendap_url_candidate": opendap_url,
                            "http_fileserver_url_candidate": http_url,
                            "data_size_bytes": data_size_bytes,
                            "found_in_catalog": cat_url,
                            "depth": depth,
                        })
                        record["n_datasets_in_catalog"] += 1
                # Sub-catalogues
                for cref in xroot.iter(f"{THREDDS_NS}catalogRef"):
                    href = cref.get(f"{XLINK_NS}href")
                    title = cref.get(f"{XLINK_NS}title", "")
                    name = cref.get("name", "")
                    if href:
                        sub_url = urljoin(cat_url, href)
                        discovered_catalog_refs.append({
                            "title": title,
                            "name": name,
                            "href": href,
                            "sub_url": sub_url,
                            "found_in_catalog": cat_url,
                            "depth": depth,
                        })
                        record["n_catalogrefs_in_catalog"] += 1
                        # Enqueue si profondeur OK
                        if (depth + 1 <= max_depth
                                and sub_url not in visited_urls):
                            queue.append((sub_url, depth + 1))
            except ET.ParseError as e:
                record["xml_parse_error"] = str(e)[:200]

        visited_catalogs.append(record)

    # Synthèse
    summary = {
        "n_catalogs_visited": len(visited_catalogs),
        "n_datasets_discovered": len(discovered_datasets),
        "n_catalog_refs_discovered": len(discovered_catalog_refs),
        "max_depth_reached": (
            max((c["depth"] for c in visited_catalogs), default=0)),
        "capped_by_max_datasets": capped,
        "constraints_applied": {
            "allow_http_methods": ["GET"],
            "allow_content_types": ["application/xml", "text/xml"],
            "forbid_binary_probe": True,
            "forbid_follow_redirects": True,
            "max_depth": max_depth,
            "max_datasets": max_datasets,
        },
    }

    # Manifest signé + persistance
    payload = {
        "manifest_id": "NOAA_CFSV2_CATALOGUE_CARTOGRAPHY_Ω",
        "ordre": ordre,
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "guardrails_enforced": True,
        "autonomy": "LIMITED",
        "mode": "CATALOGUE_BROWSE_ONLY",
        "provider": provider,
        "forensic_event": forensic_event,
        "root_catalog_url": root_catalog_url,
        "summary": summary,
        "visited_catalogs": visited_catalogs,
        "discovered_datasets": discovered_datasets,
        "discovered_catalog_refs": discovered_catalog_refs,
        "anti_generique_strict": True,
        "v30_lock": "INVIOLÉ",
        "drift_zero": True,
        "no_engine_recompute_triggered": True,
        "no_binary_probed": True,
        "executed_at_utc": _utc_now(),
    }
    payload_sha256 = hashlib.sha256(
        json.dumps(payload, sort_keys=True,
                   ensure_ascii=False, default=str).encode("utf-8")
    ).hexdigest()
    payload["manifest_sha256"] = payload_sha256

    persisted: Dict[str, Any] = {}
    if persist:
        PIPELINE_ROOT.mkdir(parents=True, exist_ok=True)
        if CFSV2_CATALOGUE_CARTOGRAPHY_PATH.exists():
            try:
                state = json.loads(
                    CFSV2_CATALOGUE_CARTOGRAPHY_PATH.read_text(
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
        state["n_cartographies"] = len(state["history"])
        state["last_manifest_sha256"] = payload_sha256
        state["last_root_catalog_url"] = root_catalog_url
        state["last_n_datasets_discovered"] = len(discovered_datasets)
        state["v30_lock"] = "INVIOLÉ"
        CFSV2_CATALOGUE_CARTOGRAPHY_PATH.write_text(
            json.dumps(state, ensure_ascii=False, indent=2),
            encoding="utf-8")
        persisted["overlay_path"] = str(
            CFSV2_CATALOGUE_CARTOGRAPHY_PATH)
        persisted["overlay_size_bytes"] = (
            CFSV2_CATALOGUE_CARTOGRAPHY_PATH.stat().st_size)
        persisted["n_cartographies_history"] = state["n_cartographies"]

        from engines.v8_institutional.especes.bio_reacteur_overlay_omega import (  # noqa: E501
            persist_audit,
        )
        audit_payload = {
            "audit_type": "NOAA_PIPELINE",
            "subtype": "CATALOGUE_CARTOGRAPHY",
            "ordre": ordre,
            "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
            "provider": provider,
            "forensic_event": forensic_event,
            "root_catalog_url": root_catalog_url,
            "manifest_sha256": payload_sha256,
            "n_catalogs_visited": summary["n_catalogs_visited"],
            "n_datasets_discovered": summary["n_datasets_discovered"],
            "n_catalog_refs_discovered": (
                summary["n_catalog_refs_discovered"]),
            "capped": capped,
            "no_binary_probed": True,
            "v30_lock_inviolate": True,
            "drift_zero": True,
            "no_engine_recompute_triggered": True,
        }
        persisted["audit_persisted"] = persist_audit(audit_payload)

    payload["persisted_paths"] = persisted
    payload["elapsed_s"] = round(time.time() - t_total, 3)
    return payload


# ═════════════════════════════════════════════════════════════════════════
# 10. NOAA CFSV2 PIVOT VERIFY (NCEI THREDDS / Copernicus / autre URL)
# ═════════════════════════════════════════════════════════════════════════
CFSV2_PIVOT_VERIFICATION_PATH = (
    PIPELINE_ROOT / "cfsv2_pivot_verification_overlay.json")


def _is_content_type_acceptable_opendap(
    content_type: Optional[str],
) -> bool:
    """Validation content-type pour OPeNDAP/THREDDS endpoints.

    Anti-générique : retourne False si content-type absent ou non
    reconnu comme OPeNDAP/HTTP-readable.
    """
    if not content_type:
        return False
    ct = content_type.lower()
    # OPeNDAP DDS/DAS/DODS + binaires + text/plain (THREDDS legacy)
    acceptable = [
        "application/octet-stream",
        "application/x-netcdf",
        "application/netcdf",
        "application/x-grib",
        "application/x-grib2",
        "application/x-dods",
        "application/x-dods-dds",
        "application/x-dods-das",
        "application/x-dods-dods",
        "binary/octet-stream",
        "text/plain",
    ]
    return any(a in ct for a in acceptable)


def verify_cfsv2_pivot_head_only(
    endpoint: str,
    provider: str = "NCEI_THREDDS_CFSR_MONTHLY",
    expect_format: str = "GRIB2_OR_NETCDF",
    expect_opendap: bool = True,
    require_no_redirect: bool = True,
    require_http_200: bool = True,
    persist: bool = True,
    timeout_s: int = 15,
    dds_max_bytes: int = 4096,
) -> Dict[str, Any]:
    """NOAA_CFSV2_P0_PIVOT · HEAD_ONLY strict pivot endpoint verification.

    Workflow doctrinal :
      1. Guardrails ENFORCED check (412 sinon)
      2. HEAD HTTP RÉEL sans follow_redirects sur endpoint absolu
      3. Si expect_opendap=True : probe complémentaire `.dds` (GET 4KB)
         pour vérifier signature OPeNDAP "Dataset {"
      4. Critères stricts : HTTP 200 + pas de redirect + content-type
         binaire/OPeNDAP + (si OPeNDAP) DDS contient "Dataset"
      5. Forensic log ENDPOINT_PROBES persisté
      6. Manifest signé SHA-256 + persistance overlay + audit
      7. AUCUN recalcul moteur

    Args:
      endpoint: URL absolue HTTPS (ex: NCEI THREDDS dodsC).
      provider: label provider (default NCEI).
      expect_format: GRIB2_OR_NETCDF.
      expect_opendap: True → probe .dds complémentaire requis.
      require_no_redirect: True (default).
      require_http_200: True (default).
      timeout_s: timeout HTTP.
      dds_max_bytes: lecture limitée pour DDS preview.

    Returns:
      Dict structuré avec verdict + manifest_sha256 + persistance.
    """
    from engines.v8_institutional.especes.pipeline_guardrails_omega import (
        require_guardrails_enforced, log_forensic_event,
    )
    require_guardrails_enforced("verify_cfsv2_pivot_head_only")

    import urllib.request
    import urllib.error

    if not endpoint.startswith(("https://", "http://")):
        raise ValueError(
            f"ENDPOINT_INVALID::not_http_url::{endpoint[:120]}")

    class NoRedirectHandler(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg,
                              headers, newurl):
            return None

    t_total = time.time()

    # 1. HEAD probe principale (anti-générique strict)
    record_head: Dict[str, Any] = {
        "url": endpoint,
        "method": "HEAD",
        "follow_redirects": False,
        "http_status": None,
        "content_type": None,
        "content_length": None,
        "headers_subset": {},
        "elapsed_ms": None,
        "reason": None,
        "redirect_detected": False,
    }
    t0 = time.time()
    try:
        opener = urllib.request.build_opener(NoRedirectHandler)
        req = urllib.request.Request(
            endpoint, method="HEAD",
            headers={
                "User-Agent": "BCE-4X-NOAA-CFSV2-PIVOT-VERIFY/1.0",
            })
        with opener.open(req, timeout=timeout_s) as resp:
            record_head["http_status"] = resp.status
            headers = dict(resp.headers)
            record_head["content_type"] = headers.get(
                "Content-Type", headers.get("content-type"))
            cl = headers.get(
                "Content-Length", headers.get("content-length"))
            try:
                record_head["content_length"] = (
                    int(cl) if cl else None)
            except (TypeError, ValueError):
                record_head["content_length"] = None
            record_head["headers_subset"] = {
                k: v for k, v in headers.items()
                if k.lower() in (
                    "content-type", "content-length", "etag",
                    "last-modified", "server", "accept-ranges",
                    "x-thredds-server-version",
                    "x-amz-request-id", "location")
            }
    except urllib.error.HTTPError as e:
        record_head["http_status"] = e.code
        record_head["reason"] = f"http_error_{e.code}"
        try:
            body = e.read(800)
            record_head["body_preview_first_500b"] = body[:500].decode(
                "utf-8", errors="replace")
        except Exception:
            pass
        if 300 <= e.code < 400:
            record_head["redirect_detected"] = True
            try:
                record_head["redirect_location"] = e.headers.get(
                    "Location")
            except Exception:
                pass
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        record_head["reason"] = f"network_error::{str(e)[:160]}"
    record_head["elapsed_ms"] = round((time.time() - t0) * 1000, 1)

    # 2. Probe DDS complémentaire (si OPeNDAP attendu)
    record_dds: Optional[Dict[str, Any]] = None
    if expect_opendap:
        dds_url = endpoint + ".dds"
        record_dds = {
            "url": dds_url,
            "method": "GET",
            "max_bytes_read": dds_max_bytes,
            "http_status": None,
            "content_type": None,
            "elapsed_ms": None,
            "reason": None,
            "dds_signature_dataset_present": False,
            "dds_preview_first_500b": None,
        }
        t1 = time.time()
        try:
            opener_dds = urllib.request.build_opener(
                NoRedirectHandler)
            req_dds = urllib.request.Request(
                dds_url, method="GET",
                headers={
                    "User-Agent":
                    "BCE-4X-NOAA-CFSV2-PIVOT-VERIFY/1.0",
                })
            with opener_dds.open(
                    req_dds, timeout=timeout_s) as resp_dds:
                record_dds["http_status"] = resp_dds.status
                record_dds["content_type"] = (
                    resp_dds.headers.get("Content-Type"))
                preview = resp_dds.read(dds_max_bytes)
                record_dds["dds_preview_first_500b"] = (
                    preview[:500].decode(
                        "utf-8", errors="replace"))
                # Signature OPeNDAP DDS
                record_dds["dds_signature_dataset_present"] = (
                    "Dataset {" in record_dds[
                        "dds_preview_first_500b"]
                    or "Dataset:" in record_dds[
                        "dds_preview_first_500b"])
        except urllib.error.HTTPError as e:
            record_dds["http_status"] = e.code
            record_dds["reason"] = f"http_error_{e.code}"
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            record_dds["reason"] = f"network_error::{str(e)[:160]}"
        record_dds["elapsed_ms"] = round(
            (time.time() - t1) * 1000, 1)

    # 3. Évaluation des critères stricts
    head_http_200 = (record_head["http_status"] == 200)
    head_no_redirect = (not record_head["redirect_detected"])
    head_ct_acceptable = _is_content_type_acceptable_opendap(
        record_head["content_type"])
    head_cl_present = (
        record_head["content_length"] is not None
        and record_head["content_length"] > 0)
    dds_valid = (
        record_dds is not None
        and record_dds.get("http_status") == 200
        and record_dds.get("dds_signature_dataset_present"))

    criteria_evaluation = {
        "expect_format": expect_format,
        "expect_opendap": expect_opendap,
        "require_http_200": require_http_200,
        "require_no_redirect": require_no_redirect,
        "head_http_200_satisfied": head_http_200,
        "head_no_redirect_satisfied": head_no_redirect,
        "head_content_type_acceptable": head_ct_acceptable,
        "head_content_length_present": head_cl_present,
        "dds_probe_executed": (record_dds is not None),
        "dds_http_200_satisfied": (
            record_dds is not None
            and record_dds.get("http_status") == 200),
        "dds_signature_dataset_present": dds_valid,
    }

    # Verdict OPeNDAP-aware (anti-générique strict)
    if expect_opendap:
        # Pour OPeNDAP : OK si HEAD 200 OK OU DDS 200 + signature Dataset
        # (THREDDS retourne parfois 4xx sur HEAD direct mais 200 sur .dds)
        valid = (
            (not require_no_redirect or head_no_redirect)
            and (
                # Voie A : HEAD strictement parfait
                (head_http_200 and head_ct_acceptable)
                # Voie B : DDS valide (signature OPeNDAP réelle)
                or dds_valid))
    else:
        valid = (
            (not require_http_200 or head_http_200)
            and (not require_no_redirect or head_no_redirect)
            and head_ct_acceptable
            and head_cl_present)

    if valid and dds_valid:
        verdict = "CFSV2_PIVOT_VALID_OPENDAP_DDS_CONFIRMED"
    elif valid and head_http_200:
        verdict = "CFSV2_PIVOT_VALID_HEAD_OK_DDS_FALLBACK"
    elif (record_head["http_status"] is not None
          and 300 <= record_head["http_status"] < 400):
        verdict = "CFSV2_PIVOT_INVALID_REDIRECT_DETECTED"
    elif record_head["http_status"] == 404:
        verdict = "CFSV2_PIVOT_INVALID_HTTP_404"
    elif record_head["reason"] and (
            "network_error" in record_head["reason"]):
        verdict = "CFSV2_PIVOT_INVALID_NETWORK_ERROR"
    else:
        verdict = "CFSV2_PIVOT_INVALID_OTHER"

    next_action = (
        "ACCEPTED — pivot endpoint validated. Await Commandant "
        "confirm to register as official CFSv2 source."
        if valid else
        "REJECTED — pivot endpoint failed strict verification. "
        "Await Commandant directive (alternative pivot URL or "
        "credentials).")

    # 4. Forensic log ENDPOINT_PROBES
    log_forensic_event(
        scope="ENDPOINT_PROBES",
        event="CFSV2_PIVOT_HEAD_ONLY_VERIFY",
        details={
            "provider": provider,
            "endpoint": endpoint,
            "head_http_status": record_head["http_status"],
            "dds_http_status": (
                record_dds.get("http_status")
                if record_dds else None),
            "valid": valid,
            "verdict": verdict,
            "dds_signature_dataset_present": dds_valid,
            "elapsed_ms_total": round(
                (time.time() - t_total) * 1000, 1),
        },
        persist=True,
    )

    # 5. Manifest signé + persistance
    payload = {
        "manifest_id": "NOAA_CFSV2_PIVOT_VERIFY_Ω",
        "ordre": "NOAA_CFSV2_P0_PIVOT_VERIFY",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "guardrails_enforced": True,
        "autonomy": "LIMITED",
        "provider": provider,
        "endpoint": endpoint,
        "probe_head": record_head,
        "probe_dds": record_dds,
        "criteria_evaluation": criteria_evaluation,
        "valid": valid,
        "verdict": verdict,
        "next_action": next_action,
        "anti_generique_strict": True,
        "v30_lock": "INVIOLÉ",
        "drift_zero": True,
        "no_engine_recompute_triggered": True,
        "executed_at_utc": _utc_now(),
    }
    payload_sha256 = hashlib.sha256(
        json.dumps(payload, sort_keys=True,
                   ensure_ascii=False, default=str).encode("utf-8")
    ).hexdigest()
    payload["manifest_sha256"] = payload_sha256

    persisted: Dict[str, Any] = {}
    if persist:
        PIPELINE_ROOT.mkdir(parents=True, exist_ok=True)
        if CFSV2_PIVOT_VERIFICATION_PATH.exists():
            try:
                state = json.loads(
                    CFSV2_PIVOT_VERIFICATION_PATH.read_text(
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
        state["n_pivot_verifications"] = len(state["history"])
        state["last_manifest_sha256"] = payload_sha256
        state["last_verdict"] = verdict
        state["last_provider"] = provider
        state["last_endpoint"] = endpoint
        state["v30_lock"] = "INVIOLÉ"
        CFSV2_PIVOT_VERIFICATION_PATH.write_text(
            json.dumps(state, ensure_ascii=False, indent=2),
            encoding="utf-8")
        persisted["overlay_path"] = str(
            CFSV2_PIVOT_VERIFICATION_PATH)
        persisted["overlay_size_bytes"] = (
            CFSV2_PIVOT_VERIFICATION_PATH.stat().st_size)
        persisted["n_pivot_verifications_history"] = state[
            "n_pivot_verifications"]

        from engines.v8_institutional.especes.bio_reacteur_overlay_omega import (  # noqa: E501
            persist_audit,
        )
        audit_payload = {
            "audit_type": "NOAA_PIPELINE",
            "subtype": "CFSV2_PIVOT_VERIFY",
            "ordre": "NOAA_CFSV2_P0_PIVOT_VERIFY",
            "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
            "provider": provider,
            "endpoint": endpoint,
            "valid": valid,
            "verdict": verdict,
            "manifest_sha256": payload_sha256,
            "head_http_status": record_head["http_status"],
            "dds_http_status": (
                record_dds.get("http_status")
                if record_dds else None),
            "dds_signature_dataset_present": dds_valid,
            "v30_lock_inviolate": True,
            "drift_zero": True,
            "no_engine_recompute_triggered": True,
        }
        persisted["audit_persisted"] = persist_audit(audit_payload)

    payload["persisted_paths"] = persisted
    payload["elapsed_s"] = round(time.time() - t_total, 3)
    return payload


# ═════════════════════════════════════════════════════════════════════════
# 9. NOAA CFSv2 VERIFICATION P0 (HEAD_ONLY + pivot CANDIDATE_LIST_ONLY)
# ═════════════════════════════════════════════════════════════════════════
CFSV2_VERIFICATION_P0_PATH = (
    PIPELINE_ROOT / "cfsv2_verification_p0_overlay.json")

# Liste des candidats pivot (mode CANDIDATE_LIST_ONLY — aucun téléchargement,
# juste endpoints testables documentés). Anti-générique strict :
# pour utilisation, le Commandant doit confirmer explicitement (le code ne
# probe AUCUN candidat sans confirm).
CFSV2_PIVOT_CANDIDATE_LIST: List[Dict[str, Any]] = [
    {
        "label": "NCEI_THREDDS_CFSR_MONTHLY",
        "provider": "NOAA NCEI",
        "type": "THREDDS_OPENDAP",
        "endpoint_root": (
            "https://www.ncei.noaa.gov/thredds/catalog/"
            "model-cfs_reanl_mm_grb_v2/catalog.html"),
        "opendap_endpoint_template": (
            "https://www.ncei.noaa.gov/thredds/dodsC/"
            "model-cfs_reanl_mm_grb_v2/{YYYY}/{YYYYMM}/"
            "cfsmm.{YYYYMM}.grb2"),
        "doc_url": (
            "https://www.ncei.noaa.gov/products/"
            "weather-climate-models/climate-forecast-system"),
        "format_native": "GRIB2",
        "coverage": "monthly_means_2011_to_present",
        "auth_required": False,
        "anti_generique_note": (
            "Endpoint documenté NCEI ; "
            "validation HTTP 200 NÉCESSAIRE par directive Commandant "
            "avant activation."),
    },
    {
        "label": "COPERNICUS_MARINE_GLOBAL_PHY",
        "provider": "Copernicus Marine Service (CMEMS)",
        "type": "ERDDAP_OR_S3_OR_TOOLBOX_API",
        "endpoint_root": "https://data.marine.copernicus.eu/products",
        "specific_product_example": (
            "GLOBAL_ANALYSISFORECAST_PHY_001_024 "
            "(Global Ocean Physics Analysis and Forecast)"),
        "access_url": (
            "https://data.marine.copernicus.eu/product/"
            "GLOBAL_ANALYSISFORECAST_PHY_001_024/"),
        "doc_url": (
            "https://help.marine.copernicus.eu/en/"
            "articles/9711619-copernicus-marine-toolbox-installation"),
        "format_native": "NETCDF4",
        "coverage": "global_ocean_physics_present",
        "auth_required": True,
        "auth_method": "Copernicus credentials (free registration)",
        "anti_generique_note": (
            "Authentification Copernicus requise ; "
            "credentials Commandant nécessaires pour probe réel."),
    },
]


def verify_cfsv2_p0_head_only(
    bucket: str = "noaa-cfs-pds",
    path: str = (
        "cfs.20240101/01/6hrly_grib_01/cfs.tavg.01.2024010100.grb2"),
    expect_format: str = "GRIB2_OR_NETCDF",
    require_no_redirect: bool = True,
    require_http_200: bool = True,
    persist: bool = True,
    timeout_s: int = 15,
) -> Dict[str, Any]:
    """NOAA_CFSV2_P0_DECISION · HEAD_ONLY strict probe.

    Workflow doctrinal :
      1. Vérifier guardrails ENFORCED (412 si pas actif)
      2. HEAD HTTP RÉEL sans follow_redirects (anti-générique)
      3. Critères stricts : HTTP 200 + Content-Type binaire +
         Content-Length > 0 + pas de redirect
      4. Forensic log ENDPOINT_PROBES persisté
      5. Si valide → suggestion activation. Si invalide → liste pivot
         CANDIDATE_LIST_ONLY (require_commandant_confirm=True)
      6. Audit NOAA_CFSV2_VERIFICATION_P0 persisté

    Args:
      bucket: bucket S3 AWS public (default noaa-cfs-pds).
      path: clé objet à probe (default path CFSv2 candidate Commandant).
      expect_format: format(s) attendu(s) — GRIB2 ou NETCDF acceptés.
      require_no_redirect: True (default) → status ≠ 3xx exigé.
      require_http_200: True (default) → uniquement 200.

    Returns:
      Dict structuré avec verdict + (si invalide) liste pivot.
    """
    # 1. Guardrails check
    from engines.v8_institutional.especes.pipeline_guardrails_omega import (
        require_guardrails_enforced, log_forensic_event,
    )
    require_guardrails_enforced("verify_cfsv2_p0_head_only")

    import urllib.request
    import urllib.error

    class NoRedirectHandler(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, headers, newurl):
            # Anti-générique : on capture le redirect au lieu de le suivre
            return None

    url = f"https://{bucket}.s3.amazonaws.com/{path}"
    t0 = time.time()
    record_probe: Dict[str, Any] = {
        "url": url,
        "bucket": bucket,
        "path": path,
        "method": "HEAD",
        "follow_redirects": False,
        "http_status": None,
        "content_type": None,
        "content_length": None,
        "headers_subset": {},
        "elapsed_ms": None,
        "reason": None,
        "redirect_detected": False,
    }

    try:
        opener = urllib.request.build_opener(NoRedirectHandler)
        req = urllib.request.Request(
            url, method="HEAD",
            headers={
                "User-Agent": "BCE-4X-NOAA-CFSV2-P0-VERIFY/1.0",
            })
        with opener.open(req, timeout=timeout_s) as resp:
            record_probe["http_status"] = resp.status
            headers = dict(resp.headers)
            record_probe["content_type"] = headers.get(
                "Content-Type", headers.get("content-type"))
            cl = headers.get(
                "Content-Length", headers.get("content-length"))
            try:
                record_probe["content_length"] = (
                    int(cl) if cl else None)
            except (TypeError, ValueError):
                record_probe["content_length"] = None
            record_probe["headers_subset"] = {
                k: v for k, v in headers.items()
                if k.lower() in (
                    "content-type", "content-length",
                    "etag", "last-modified", "x-amz-request-id",
                    "x-amz-server-side-encryption",
                    "accept-ranges")
            }
    except urllib.error.HTTPError as e:
        record_probe["http_status"] = e.code
        record_probe["reason"] = f"http_error_{e.code}"
        # Tentative lecture body limité (anti-générique)
        try:
            body = e.read(800)
            record_probe["body_preview_first_500b"] = body[:500].decode(
                "utf-8", errors="replace")
            if "NoSuchKey" in (
                    record_probe.get("body_preview_first_500b") or ""):
                record_probe["reason"] = "NoSuchKey"
            elif "NoSuchBucket" in (
                    record_probe.get("body_preview_first_500b") or ""):
                record_probe["reason"] = "NoSuchBucket"
        except Exception:
            pass
        # Détection redirect explicite (3xx)
        if 300 <= e.code < 400:
            record_probe["redirect_detected"] = True
            try:
                location = e.headers.get("Location")
                record_probe["redirect_location"] = location
            except Exception:
                pass
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        record_probe["reason"] = f"network_error::{str(e)[:160]}"
    record_probe["elapsed_ms"] = round((time.time() - t0) * 1000, 1)

    # 2. Évaluation des critères stricts
    criteria_evaluation = {
        "http_200_strict_required": require_http_200,
        "http_200_strict_satisfied": (
            record_probe["http_status"] == 200),
        "no_redirect_required": require_no_redirect,
        "no_redirect_satisfied": (
            not record_probe["redirect_detected"]),
        "content_length_present": (
            record_probe["content_length"] is not None
            and record_probe["content_length"] > 0),
        "content_type_acceptable": _is_content_type_acceptable(
            record_probe["content_type"], expect_format),
        "expect_format": expect_format,
    }
    valid = (
        (not require_http_200 or criteria_evaluation[
            "http_200_strict_satisfied"])
        and (not require_no_redirect or criteria_evaluation[
            "no_redirect_satisfied"])
        and criteria_evaluation["content_length_present"]
        and criteria_evaluation["content_type_acceptable"])
    if valid:
        verdict = "CFSV2_P0_HEAD_PROBE_VALID"
        next_action = (
            "ACCEPTED_CANDIDATE — suggest activation pipeline CFSv2 "
            "after Commandant confirm.")
    else:
        verdict = "CFSV2_P0_HEAD_PROBE_INVALID"
        next_action = (
            "PIVOT_REQUIRED — list of candidates returned in "
            "CANDIDATE_LIST_ONLY mode, await Commandant confirm.")

    # 3. Forensic log ENDPOINT_PROBES
    log_forensic_event(
        scope="ENDPOINT_PROBES",
        event="CFSV2_VERIFICATION_P0_HEAD_ONLY",
        details={
            "bucket": bucket,
            "path": path,
            "url": url,
            "http_status": record_probe["http_status"],
            "reason": record_probe["reason"],
            "valid": valid,
            "verdict": verdict,
            "elapsed_ms": record_probe["elapsed_ms"],
        },
        persist=True,
    )

    # 4. Pivot list (CANDIDATE_LIST_ONLY)
    pivot_payload = None
    if not valid:
        pivot_payload = {
            "mode": "CANDIDATE_LIST_ONLY",
            "autonomy": "LIMITED",
            "require_commandant_confirm": True,
            "n_candidates": len(CFSV2_PIVOT_CANDIDATE_LIST),
            "candidates": CFSV2_PIVOT_CANDIDATE_LIST,
            "doctrinal_note": (
                "Aucun probe HTTP automatique sur les candidats pivot. "
                "Le Commandant doit confirmer explicitement avant "
                "validation et probe réel."),
        }

    # 5. Manifest signé + persistance
    payload = {
        "manifest_id": "NOAA_CFSV2_VERIFICATION_P0_Ω",
        "ordre": "NOAA_CFSV2_P0_DECISION",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "guardrails_enforced": True,
        "probe": record_probe,
        "criteria_evaluation": criteria_evaluation,
        "valid": valid,
        "verdict": verdict,
        "next_action": next_action,
        "pivot_payload": pivot_payload,
        "anti_generique_strict": True,
        "v30_lock": "INVIOLÉ",
        "drift_zero": True,
        "no_engine_recompute_triggered": True,
        "executed_at_utc": _utc_now(),
    }
    payload_sha256 = hashlib.sha256(
        json.dumps(payload, sort_keys=True,
                   ensure_ascii=False, default=str).encode("utf-8")
    ).hexdigest()
    payload["manifest_sha256"] = payload_sha256

    persisted: Dict[str, Any] = {}
    if persist:
        PIPELINE_ROOT.mkdir(parents=True, exist_ok=True)
        # FUSION ADD-ONLY history
        if CFSV2_VERIFICATION_P0_PATH.exists():
            try:
                state = json.loads(
                    CFSV2_VERIFICATION_P0_PATH.read_text(
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
        state["n_verifications"] = len(state["history"])
        state["last_manifest_sha256"] = payload_sha256
        state["last_verdict"] = verdict
        state["v30_lock"] = "INVIOLÉ"
        CFSV2_VERIFICATION_P0_PATH.write_text(
            json.dumps(state, ensure_ascii=False, indent=2),
            encoding="utf-8")
        persisted["overlay_path"] = str(CFSV2_VERIFICATION_P0_PATH)
        persisted["overlay_size_bytes"] = (
            CFSV2_VERIFICATION_P0_PATH.stat().st_size)
        persisted["n_verifications_history"] = state["n_verifications"]

        # Audit doctrinal
        from engines.v8_institutional.especes.bio_reacteur_overlay_omega import (  # noqa: E501
            persist_audit,
        )
        audit_payload = {
            "audit_type": "NOAA_PIPELINE",
            "subtype": "CFSV2_VERIFICATION_P0",
            "ordre": "NOAA_CFSV2_P0_DECISION",
            "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
            "bucket": bucket,
            "path": path,
            "valid": valid,
            "verdict": verdict,
            "manifest_sha256": payload_sha256,
            "http_status": record_probe["http_status"],
            "reason": record_probe["reason"],
            "pivot_required": (not valid),
            "n_pivot_candidates": (
                len(CFSV2_PIVOT_CANDIDATE_LIST) if not valid else 0),
            "v30_lock_inviolate": True,
            "drift_zero": True,
            "no_engine_recompute_triggered": True,
        }
        persisted["audit_persisted"] = persist_audit(audit_payload)

    payload["persisted_paths"] = persisted
    payload["elapsed_s"] = round(time.time() - t0, 3)
    return payload


def _is_content_type_acceptable(
    content_type: Optional[str],
    expect_format: str,
) -> bool:
    """Validation content-type pour formats GRIB2/NetCDF binaires.

    Anti-générique : retourne False si pas de signature reconnue.
    Ne fabrique aucun verdict.
    """
    if not content_type:
        return False
    ct = content_type.lower()
    # Formats binaires acceptables (anti-générique : liste explicite)
    acceptable = [
        "application/octet-stream",
        "application/x-grib",
        "application/x-grib2",
        "application/x-netcdf",
        "application/netcdf",
        "binary/octet-stream",
        "application/x-netcdf4",
    ]
    return any(a in ct for a in acceptable)


def list_cfsv2_pivot_candidates() -> Dict[str, Any]:
    """Lecture seule de la liste pivot CFSv2 (anti-générique).

    Mode CANDIDATE_LIST_ONLY : aucun probe automatique. Le Commandant
    doit confirmer explicitement avant tout usage.
    """
    return {
        "manifest_id": "NOAA_CFSV2_PIVOT_CANDIDATES_Ω",
        "ordre": "NOAA_CFSV2_P0_DECISION",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "mode": "CANDIDATE_LIST_ONLY",
        "autonomy": "LIMITED",
        "require_commandant_confirm": True,
        "n_candidates": len(CFSV2_PIVOT_CANDIDATE_LIST),
        "candidates": CFSV2_PIVOT_CANDIDATE_LIST,
        "doctrinal_note": (
            "Aucun probe HTTP automatique. Confirmer avant probe réel."),
        "v30_lock": "INVIOLÉ",
        "scanned_at_utc": _utc_now(),
    }


# ═════════════════════════════════════════════════════════════════════════
# 8. WOD23 HOOK ACTIVATION (overlay V30_LOCK FUSION ADD-ONLY)
#    Utilise credentials B2 dédiées (B2_WOD23_*) — anti-générique strict.
# ═════════════════════════════════════════════════════════════════════════
WOD23_HOOK_OVERLAY_CONFIG: Dict[str, Any] = {
    "manifest_id": "WOD23_HOOK_OVERLAY_CONFIG_Ω",
    "ordre": "ACTIVATION_PIPELINE_NOAA_TERRITOIRE",
    "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
    "credentials_source": "B2_WOD23_* env vars (dédiées WOD23, séparées du B2 GIS)",
    "expected_formats": [".nc", ".nc.gz", ".csv", ".bin"],
    "wod23_signatures_recognized": {
        "APB": "Autonomous Pinniped Bathythermograph",
        "CTD": "Conductivity-Temperature-Depth profile",
        "DRB": "Drifting Buoy",
        "GLD": "Glider",
        "MBT": "Mechanical Bathythermograph",
        "MRB": "Moored Buoy",
        "OSD": "Ocean Station Data / bottle / low-res CTD",
        "PFL": "Profiling Float",
        "SUR": "Surface only",
        "UOR": "Undulating Ocean Recorder",
        "XBT": "Expendable Bathythermograph",
    },
    "consumed_by_modules": ["PHYSIOLOGIE", "HABITAT", "THERMIQUE"],
    "anti_generique_strict": True,
    "fusion_add_only": True,
    "v30_lock": "INVIOLÉ",
}

WOD23_HOOK_ACTIVATION_PATH = (
    PIPELINE_ROOT / "wod23_hook_activation_overlay.json")


def _classify_wod23_key(key: str) -> Optional[str]:
    """Classifie un nom de fichier WOD23 par signature institutionnelle.

    Anti-générique strict : retourne None si aucun pattern reconnu (pas
    de fabrication de classification). Patterns dérivés du registre
    public NOAA WOD23.
    """
    upper = key.upper()
    for sig, _ in WOD23_HOOK_OVERLAY_CONFIG[
            "wod23_signatures_recognized"].items():
        # Match patterns "_APB.", "_CTD.", "_CTD2." etc.
        if (f"_{sig}." in upper
                or f"_{sig}_" in upper
                or upper.endswith(f"_{sig}")
                or f"_{sig}2." in upper):
            return sig
    return None


def probe_wod23_b2_dedicated(
    max_keys: int = 1000,
    classify: bool = True,
) -> Dict[str, Any]:
    """Probe RÉEL Backblaze B2 avec credentials WOD23 dédiées.

    Lit B2_WOD23_KEY_ID / B2_WOD23_APPLICATION_KEY / B2_WOD23_ENDPOINT_URL
    / B2_WOD23_REGION / B2_WOD23_BUCKET / B2_WOD23_PATH_PREFIX depuis env.

    Anti-générique strict : aucune fabrication. Toutes les valeurs
    proviennent d'appels boto3 réels.
    """
    import os
    record: Dict[str, Any] = {
        "manifest_id": "WOD23_B2_DEDICATED_PROBE_Ω",
        "ordre": "ACTIVATION_PIPELINE_NOAA_TERRITOIRE",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "credentials_source": "B2_WOD23_* env vars",
        "available": False,
        "anti_generique_strict": True,
        "v30_lock": "INVIOLÉ",
        "probed_at_utc": _utc_now(),
    }
    key_id = os.environ.get("B2_WOD23_KEY_ID")
    app_key = os.environ.get("B2_WOD23_APPLICATION_KEY")
    endpoint = os.environ.get("B2_WOD23_ENDPOINT_URL")
    region = os.environ.get("B2_WOD23_REGION")
    bucket = os.environ.get("B2_WOD23_BUCKET")
    path_prefix = os.environ.get("B2_WOD23_PATH_PREFIX", "")

    record["bucket"] = bucket
    record["path_prefix"] = path_prefix
    record["endpoint_url"] = endpoint
    record["region"] = region

    missing = [
        n for n, v in [
            ("B2_WOD23_KEY_ID", key_id),
            ("B2_WOD23_APPLICATION_KEY", app_key),
            ("B2_WOD23_ENDPOINT_URL", endpoint),
            ("B2_WOD23_BUCKET", bucket),
        ] if not v
    ]
    if missing:
        record["reason"] = (
            f"wod23_credentials_missing_in_env::{','.join(missing)}")
        return record

    try:
        import boto3
        from botocore.config import Config
        from botocore.exceptions import (
            ClientError, EndpointConnectionError, NoCredentialsError,
        )
    except ImportError as e:
        record["reason"] = f"boto3_import_error::{str(e)[:120]}"
        return record

    try:
        s3 = boto3.client(
            "s3",
            aws_access_key_id=key_id,
            aws_secret_access_key=app_key,
            endpoint_url=endpoint,
            region_name=region,
            config=Config(
                connect_timeout=10, read_timeout=15,
                retries={"max_attempts": 1},
                signature_version="s3v4"),
        )
    except Exception as e:
        record["reason"] = f"s3_client_init_error::{str(e)[:120]}"
        return record

    # head_bucket
    t0 = time.time()
    try:
        s3.head_bucket(Bucket=bucket)
        record["bucket_exists"] = True
        record["http_head_bucket_ms"] = round(
            (time.time() - t0) * 1000, 1)
    except ClientError as e:
        code = e.response.get("Error", {}).get("Code", "?")
        status = e.response.get(
            "ResponseMetadata", {}).get("HTTPStatusCode")
        record["bucket_exists"] = False
        record["reason"] = f"head_bucket_error::http_{status}_code_{code}"
        record["http_head_bucket_ms"] = round(
            (time.time() - t0) * 1000, 1)
        return record
    except (EndpointConnectionError, NoCredentialsError) as e:
        record["reason"] = (
            f"network_or_credentials_error::{str(e)[:120]}")
        return record

    # list_objects_v2 (paginé)
    t0 = time.time()
    n_objects = 0
    n_recognized = 0
    n_anomalies = 0
    total_bytes = 0
    sample_keys: List[Dict[str, Any]] = []
    classification_counts: Dict[str, int] = {}
    try:
        paginator = s3.get_paginator("list_objects_v2")
        for page in paginator.paginate(
            Bucket=bucket,
            Prefix=path_prefix,
            PaginationConfig={"MaxItems": max_keys, "PageSize": 1000},
        ):
            for obj in page.get("Contents", []):
                key = obj["Key"]
                size = obj.get("Size", 0)
                ext_ok = any(
                    key.lower().endswith(fmt.lower())
                    for fmt in WOD23_HOOK_OVERLAY_CONFIG[
                        "expected_formats"])
                if size == 0:
                    n_anomalies += 1
                    continue
                if not ext_ok:
                    n_anomalies += 1
                    continue
                n_objects += 1
                total_bytes += size
                if classify:
                    sig = _classify_wod23_key(key)
                    if sig:
                        n_recognized += 1
                        classification_counts[sig] = (
                            classification_counts.get(sig, 0) + 1)
                if len(sample_keys) < 12:
                    sample_keys.append({
                        "key": key,
                        "size_bytes": size,
                        "wod23_signature": (
                            _classify_wod23_key(key)
                            if classify else None),
                    })
    except ClientError as e:
        code = e.response.get("Error", {}).get("Code", "?")
        record["reason"] = f"list_objects_error::{code}"
        record["http_list_objects_ms"] = round(
            (time.time() - t0) * 1000, 1)
        return record

    record["http_list_objects_ms"] = round(
        (time.time() - t0) * 1000, 1)
    record["n_objects_valid"] = n_objects
    record["n_objects_recognized_wod23"] = n_recognized
    record["n_anomalies"] = n_anomalies
    record["total_size_bytes"] = total_bytes
    record["total_size_mb"] = round(total_bytes / (1024 * 1024), 3)
    record["classification_counts"] = classification_counts
    record["sample_keys"] = sample_keys
    record["available"] = (n_objects > 0)
    if n_objects == 0:
        record["reason"] = "bucket_empty_or_prefix_yields_zero_files"
    return record


def activate_wod23_hook(
    persist: bool = True,
    max_keys: int = 1000,
) -> Dict[str, Any]:
    """Active officiellement le hook NOAA WOD23 sur Backblaze B2.

    Étapes :
      1. Probe RÉEL avec credentials B2_WOD23_* dédiées
      2. Classification anti-générique stricte des signatures WOD23
      3. Calcul SHA-256 du manifest pour traçabilité longitudinale
      4. Persistance overlay JSON (FUSION ADD-ONLY, V30_LOCK respecté)
      5. Persistance audit NOAA_PIPELINE/WOD23_HOOK_ACTIVATION
      6. AUCUN recalcul moteur déclenché

    Returns:
      Dict avec verdict, manifest signé SHA-256, échantillon, classification.
    """
    t0 = time.time()
    probe = probe_wod23_b2_dedicated(
        max_keys=max_keys, classify=True)

    # Verdict doctrinal
    if probe.get("available") and probe.get(
            "n_objects_recognized_wod23", 0) > 0:
        verdict = "WOD23_HOOK_ACTIVATED_OPERATIONAL"
        activated = True
    elif probe.get("available"):
        verdict = "WOD23_HOOK_FILES_PRESENT_BUT_NO_WOD23_SIGNATURE"
        activated = False
    else:
        verdict = "WOD23_HOOK_PROBE_FAILED_NOT_ACTIVATED"
        activated = False

    # Manifest signé pour traçabilité longitudinale
    manifest_payload = {
        "manifest_id": "WOD23_HOOK_ACTIVATION_MANIFEST_Ω",
        "ordre": "ACTIVATION_PIPELINE_NOAA_TERRITOIRE",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "fusion_add_only": True,
        "v30_lock": "INVIOLÉ",
        "drift_zero": True,
        "no_engine_recompute_triggered": True,
        "activated": activated,
        "verdict": verdict,
        "probe_summary": {
            "bucket": probe.get("bucket"),
            "path_prefix": probe.get("path_prefix"),
            "endpoint_url": probe.get("endpoint_url"),
            "region": probe.get("region"),
            "bucket_exists": probe.get("bucket_exists"),
            "n_objects_valid": probe.get("n_objects_valid", 0),
            "n_objects_recognized_wod23": probe.get(
                "n_objects_recognized_wod23", 0),
            "n_anomalies": probe.get("n_anomalies", 0),
            "total_size_bytes": probe.get("total_size_bytes", 0),
            "total_size_mb": probe.get("total_size_mb", 0),
            "classification_counts": probe.get(
                "classification_counts", {}),
            "http_head_bucket_ms": probe.get("http_head_bucket_ms"),
            "http_list_objects_ms": probe.get("http_list_objects_ms"),
        },
        "sample_keys_first_12": probe.get("sample_keys", []),
        "anti_generique_strict": True,
        "activated_at_utc": _utc_now(),
    }
    manifest_json = json.dumps(
        manifest_payload, sort_keys=True, ensure_ascii=False, default=str)
    manifest_sha256 = hashlib.sha256(
        manifest_json.encode("utf-8")).hexdigest()
    manifest_payload["manifest_sha256"] = manifest_sha256

    persisted: Dict[str, Any] = {}
    if persist:
        PIPELINE_ROOT.mkdir(parents=True, exist_ok=True)
        WOD23_HOOK_ACTIVATION_PATH.write_text(
            json.dumps(manifest_payload, ensure_ascii=False, indent=2),
            encoding="utf-8")
        persisted["overlay_path"] = str(WOD23_HOOK_ACTIVATION_PATH)
        persisted["overlay_size_bytes"] = (
            WOD23_HOOK_ACTIVATION_PATH.stat().st_size)

        # Audit forensique
        from engines.v8_institutional.especes.bio_reacteur_overlay_omega import (  # noqa: E501
            persist_audit,
        )
        audit_payload = {
            "audit_type": "NOAA_PIPELINE",
            "subtype": "WOD23_HOOK_ACTIVATION",
            "ordre": "ACTIVATION_PIPELINE_NOAA_TERRITOIRE",
            "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
            "verdict": verdict,
            "activated": activated,
            "manifest_sha256": manifest_sha256,
            "bucket": probe.get("bucket"),
            "n_objects_valid": probe.get("n_objects_valid", 0),
            "n_objects_recognized_wod23": probe.get(
                "n_objects_recognized_wod23", 0),
            "total_size_bytes": probe.get("total_size_bytes", 0),
            "classification_counts": probe.get(
                "classification_counts", {}),
            "no_engine_recompute_triggered": True,
            "v30_lock_inviolate": True,
            "drift_zero": True,
        }
        persisted["audit_persisted"] = persist_audit(audit_payload)

    return {
        "manifest_id": "WOD23_HOOK_ACTIVATE_Ω",
        "ordre": "ACTIVATION_PIPELINE_NOAA_TERRITOIRE",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "activated": activated,
        "verdict": verdict,
        "manifest": manifest_payload,
        "manifest_sha256": manifest_sha256,
        "probe_full": probe,
        "persisted_paths": persisted,
        "no_engine_recompute_triggered": True,
        "v30_lock": "INVIOLÉ",
        "drift_zero": True,
        "elapsed_s": round(time.time() - t0, 3),
        "computed_at_utc": _utc_now(),
    }


def get_wod23_hook_status() -> Dict[str, Any]:
    """Lit l'état du hook WOD23 (read-only, V30_LOCK respecté)."""
    if not WOD23_HOOK_ACTIVATION_PATH.exists():
        return {
            "manifest_id": "WOD23_HOOK_STATUS_Ω",
            "ordre": "ACTIVATION_PIPELINE_NOAA_TERRITOIRE",
            "status": "NOT_ACTIVATED_YET",
            "v30_lock": "INVIOLÉ",
            "scanned_at_utc": _utc_now(),
        }
    payload = json.loads(
        WOD23_HOOK_ACTIVATION_PATH.read_text(encoding="utf-8"))
    return {
        "manifest_id": "WOD23_HOOK_STATUS_Ω",
        "ordre": "ACTIVATION_PIPELINE_NOAA_TERRITOIRE",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "status": "ACTIVATED" if payload.get("activated") else (
            "PROBE_FAILED_NOT_ACTIVATED"),
        "manifest": payload,
        "overlay_path": str(WOD23_HOOK_ACTIVATION_PATH),
        "overlay_size_bytes": (
            WOD23_HOOK_ACTIVATION_PATH.stat().st_size),
        "v30_lock": "INVIOLÉ",
        "scanned_at_utc": _utc_now(),
    }

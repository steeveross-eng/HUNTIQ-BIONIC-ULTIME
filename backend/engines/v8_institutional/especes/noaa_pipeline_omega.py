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
    "verify_cfsv2_p0_head_only",
    "verify_cfsv2_pivot_head_only",
    "list_cfsv2_pivot_candidates",
]


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

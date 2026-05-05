"""
gis_s3_upload_router_omega.py — Pipeline S3/B2 Voie B (ORDRE N°52-EXT VOIE B)
═════════════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU x3 · doctrine ANTI_GÉNÉRIQUE_STRICT

Stockage externe Backblaze B2 (S3-compatible) pour l'ingestion monolithique
`pee_maj.gpkg` (~36.9 Go) sans passer par /var/cache éphémère.

Sessions persistées sur `/app/backend/data/gis_s3_sessions/` (ext4 persistant).

Endpoints :
  POST /api/v30/admin-premium/gis/diagnostic/pee-maj/probe-s3-credentials
  POST /api/v30/admin-premium/gis/upload-chunk-s3/{slot_id}
  GET  /api/v30/admin-premium/gis/upload-chunk-s3/{slot_id}/resume/{upload_id}
  POST /api/v30/admin-premium/gis/upload-chunk-s3/{slot_id}/abort/{upload_id}
  POST /api/v30/admin-premium/gis/pee-maj/s3-finalize/{upload_id}
"""
from __future__ import annotations

import hashlib
import json
import logging
import os
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import boto3
from botocore.client import Config
from botocore.exceptions import ClientError, EndpointConnectionError
from fastapi import APIRouter, File, Header, HTTPException, Request, UploadFile

from engines.v8_institutional.especes import gis_audit_log_omega as audit
from engines.v8_institutional.especes.gis_reception_validators_omega import (
    SLOT_BY_ID,
    SLOTS_GIS_PROTÉGÉS_SPEC,
)

logger = logging.getLogger("gis_s3_b2_omega")

router = APIRouter(prefix="/api/v30/admin-premium/gis", tags=["gis-s3-b2"])

# ═════════════════════════════════════════════════════════════════════════
# Manifest institutionnel (partagé avec VOIE A) — ANTI-RÉGRESSIF
# ═════════════════════════════════════════════════════════════════════════
MANIFEST_PATH = Path(
    "/app/backend/data/gis_operational/GIS_RECEPTION_INTAKE_Ω.json"
)

# ═════════════════════════════════════════════════════════════════════════
# Sessions persistantes B2 (survit au pod restart grâce à /app ext4)
# ═════════════════════════════════════════════════════════════════════════
S3_SESSIONS_DIR = Path("/app/backend/data/gis_s3_sessions")
S3_SESSIONS_DIR.mkdir(parents=True, exist_ok=True)

SAFE_UPLOAD_ID = re.compile(r"^[A-Za-z0-9._-]{8,64}$")
SAFE_FILENAME = re.compile(r"^[A-Za-z0-9._-]+$")


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _verify_token(x_commandant_token: Optional[str]) -> None:
    expected = os.environ.get("GIS_RECEPTION_COMMANDANT_TOKEN")
    if not expected:
        raise HTTPException(status_code=503,
                              detail="GIS_RECEPTION_COMMANDANT_TOKEN_NOT_CONFIGURED")
    if not x_commandant_token or x_commandant_token.strip() != expected.strip():
        raise HTTPException(status_code=401, detail="ADMIN_PREMIUM_ONLY")


def _get_b2_client():
    """Retourne un client boto3 configuré pour Backblaze B2 S3-compatible."""
    key = os.environ.get("B2_KEY_ID")
    secret = os.environ.get("B2_APPLICATION_KEY")
    bucket = os.environ.get("B2_BUCKET_NAME")
    endpoint = os.environ.get("B2_ENDPOINT_URL")
    region = os.environ.get("B2_REGION")
    if not all([key, secret, bucket, endpoint, region]):
        raise HTTPException(
            status_code=503,
            detail=("B2_CREDENTIALS_NOT_CONFIGURED — requis : B2_KEY_ID, "
                    "B2_APPLICATION_KEY, B2_BUCKET_NAME, B2_ENDPOINT_URL, "
                    "B2_REGION dans backend/.env"))
    return boto3.client(
        "s3",
        endpoint_url=endpoint,
        aws_access_key_id=key,
        aws_secret_access_key=secret,
        region_name=region,
        config=Config(signature_version="s3v4",
                       retries={"max_attempts": 3, "mode": "standard"}),
    ), bucket


def _session_path(upload_id: str) -> Path:
    return S3_SESSIONS_DIR / f"{upload_id}.json"


def _read_session(upload_id: str) -> Dict[str, Any]:
    p = _session_path(upload_id)
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _write_session(upload_id: str, session: Dict[str, Any]) -> None:
    p = _session_path(upload_id)
    tmp = p.with_suffix(".partial")
    tmp.write_text(json.dumps(session, ensure_ascii=False, indent=2),
                    encoding="utf-8")
    os.replace(str(tmp), str(p))


# ═════════════════════════════════════════════════════════════════════════
# Manifest helpers — ANTI-RÉGRESSIF · FUSION ADD-ONLY
# ═════════════════════════════════════════════════════════════════════════
def _read_manifest_raw() -> Dict[str, Any]:
    """Lit le manifest + auto-sync SLOT_BY_ID absents (FUSION ADD-ONLY).

    Identique à la logique VOIE A dans gis_reception_router_omega._read_manifest()
    mais dupliquée ici pour éviter une dépendance circulaire sur les imports
    du router principal.
    """
    if MANIFEST_PATH.exists():
        try:
            manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        except Exception as e:
            logger.warning("MANIFEST_READ_FALLBACK: %s — régénération", e)
            manifest = {
                "manifest_id": "GIS_RECEPTION_INTAKE_Ω",
                "doctrine": "BCE-4X_ULTIME_ABSOLU_x3",
                "slots": {},
            }
    else:
        manifest = {
            "manifest_id": "GIS_RECEPTION_INTAKE_Ω",
            "doctrine": "BCE-4X_ULTIME_ABSOLU_x3",
            "slots": {},
        }

    manifest.setdefault("slots", {})
    # Auto-sync : ajouter tout slot SLOT_BY_ID absent (ABSENT par défaut)
    for s in SLOTS_GIS_PROTÉGÉS_SPEC:
        if s["slot_id"] not in manifest["slots"]:
            manifest["slots"][s["slot_id"]] = {
                "slot_id": s["slot_id"],
                "label": s["label"],
                "priority": s["priority"],
                "status": "ABSENT",
                "uploads": [],
            }
    return manifest


def _write_manifest(manifest: Dict[str, Any]) -> None:
    manifest["last_updated_utc"] = _utc_now()
    tmp = MANIFEST_PATH.with_suffix(".partial")
    tmp.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(str(tmp), str(MANIFEST_PATH))


def _ensure_slot_in_manifest(slot_id: str,
                             manifest: Dict[str, Any]) -> Dict[str, Any]:
    """Garantit que le slot est présent dans le manifest (ANTI-KeyError).

    Utilise SLOT_BY_ID comme source canonique. Si le slot est absent,
    il est initialisé avec status=ABSENT, uploads=[].
    """
    manifest.setdefault("slots", {})
    if slot_id not in manifest["slots"]:
        spec = SLOT_BY_ID.get(slot_id, {})
        manifest["slots"][slot_id] = {
            "slot_id": slot_id,
            "label": spec.get("label", slot_id),
            "priority": spec.get("priority", "P?"),
            "status": "ABSENT",
            "uploads": [],
        }
    return manifest["slots"][slot_id]


def _finalize_manifest_from_b2(
    session: Dict[str, Any],
    s3,
    bucket: str,
) -> Dict[str, Any]:
    """Stream SHA-256 depuis B2 + met à jour le manifest institutionnel.

    Helper idempotent : si `session["manifest_finalized"]==True`, on se
    contente de relire les valeurs déjà persistées (anti-double-finalize).

    Retourne un dict avec sha256_global, size_bytes, elapsed_s,
    composite_sha256, files_loaded_count, slot_status.
    """
    slot_id = session["slot_id"]
    b2_key = session["b2_key"]
    filename = session["filename"]

    # Idempotence : si déjà finalisé et manifest cohérent, on retourne
    # les valeurs en cache.
    if session.get("manifest_finalized") and session.get("sha256_global"):
        logger.info(
            "FINALIZE_IDEMPOTENT_SKIP slot=%s b2_key=%s sha256=%s",
            slot_id, b2_key, session["sha256_global"])
        return {
            "sha256_global": session["sha256_global"],
            "size_bytes": int(session.get("final_size_bytes") or 0),
            "elapsed_s": 0.0,
            "composite_sha256": session.get("composite_sha256"),
            "files_loaded_count": session.get("files_loaded_count"),
            "slot_status": session.get("slot_status", "LOADED"),
            "idempotent_skip": True,
        }

    logger.info(
        "FINALIZE_STREAM_BEGIN slot=%s b2_key=%s", slot_id, b2_key)
    try:
        obj = s3.get_object(Bucket=bucket, Key=b2_key)
    except ClientError as e:
        logger.error("B2_GET_OBJECT_ERROR slot=%s b2_key=%s err=%s",
                     slot_id, b2_key, e)
        raise HTTPException(status_code=502,
                            detail=f"B2_GET_OBJECT_ERROR::{e}")

    h = hashlib.sha256()
    total_streamed = 0
    t0 = time.time()
    try:
        body = obj["Body"]
        while True:
            chunk = body.read(8 << 20)  # 8 Mo
            if not chunk:
                break
            h.update(chunk)
            total_streamed += len(chunk)
    finally:
        try:
            obj["Body"].close()
        except Exception:
            pass
    sha256_global = h.hexdigest()
    elapsed_s = round(time.time() - t0, 2)
    logger.info(
        "FINALIZE_STREAM_DONE slot=%s bytes=%d elapsed_s=%s sha256=%s",
        slot_id, total_streamed, elapsed_s, sha256_global)

    # MAJ manifest
    manifest = _read_manifest_raw()
    slot = _ensure_slot_in_manifest(slot_id, manifest)
    slot["status"] = "LOADED"
    # Dédup par b2_key (un même fichier ne s'additionne pas)
    slot.setdefault("uploads", [])
    slot["uploads"] = [
        u for u in slot["uploads"]
        if u.get("b2_key") != b2_key and u.get("filename") != filename
    ]
    upload_entry = {
        "filename": filename,
        "size_bytes": total_streamed,
        "sha256": sha256_global,
        "source": "BACKBLAZE_B2_MULTIPART",
        "b2_bucket": bucket,
        "b2_key": b2_key,
        "b2_upload_id": session["b2_upload_id"],
        "upload_id_ui": session.get("upload_id_ui"),
        "uploaded_at_utc": session.get("completed_at_utc"),
        "validation_passed": True,
    }
    slot["uploads"].append(upload_entry)
    slot["files_loaded_count"] = len(slot["uploads"])
    slot["composite_sha256"] = hashlib.sha256(
        "\n".join(sorted(u["sha256"] for u in slot["uploads"]
                         if u.get("sha256"))).encode("utf-8")
    ).hexdigest()
    _write_manifest(manifest)
    logger.info(
        "MANIFEST_UPDATED slot=%s files_loaded=%d composite=%s",
        slot_id, slot["files_loaded_count"], slot["composite_sha256"])

    # Persister sur session (idempotence)
    session["manifest_finalized"] = True
    session["sha256_global"] = sha256_global
    session["final_size_bytes"] = total_streamed
    session["composite_sha256"] = slot["composite_sha256"]
    session["files_loaded_count"] = slot["files_loaded_count"]
    session["slot_status"] = slot["status"]
    _write_session(session["upload_id_ui"], session)

    return {
        "sha256_global": sha256_global,
        "size_bytes": total_streamed,
        "elapsed_s": elapsed_s,
        "composite_sha256": slot["composite_sha256"],
        "files_loaded_count": slot["files_loaded_count"],
        "slot_status": slot["status"],
        "idempotent_skip": False,
    }


# ═════════════════════════════════════════════════════════════════════════
# Endpoint : probe credentials B2
# ═════════════════════════════════════════════════════════════════════════
@router.post("/diagnostic/pee-maj/probe-s3-credentials")
async def probe_s3_credentials(
    request: Request,
    x_commandant_token: Optional[str] = Header(default=None, alias="X-Commandant-Token"),
    user_agent: Optional[str] = Header(default=None, alias="User-Agent"),
) -> Dict[str, Any]:
    """ORDRE N°52-EXT VOIE B · Probe live des credentials B2 sans mutation.
    Test 1 : head_bucket (droits lecture + existence bucket)
    Test 2 : list_objects_v2 max=5 (droits liste)
    Test 3 : create_multipart_upload + abort (droits écriture multipart)
    Audit-event PROBE_S3_CREDENTIALS_Ω consigné.
    """
    _verify_token(x_commandant_token)
    client_ip = request.client.host if request.client else "unknown"
    ua = (user_agent or "")[:200]

    results: Dict[str, Any] = {
        "head_bucket": False,
        "list_objects": False,
        "multipart_create_abort": False,
        "errors": [],
    }
    try:
        s3, bucket = _get_b2_client()
        s3.head_bucket(Bucket=bucket)
        results["head_bucket"] = True

        r = s3.list_objects_v2(Bucket=bucket, MaxKeys=5)
        results["list_objects"] = True
        results["objects_sample"] = [
            {"key": o["Key"], "size": o["Size"]}
            for o in r.get("Contents", [])[:5]
        ]

        probe_key = f"_probes/{int(time.time())}_{os.urandom(4).hex()}.bin"
        ma = s3.create_multipart_upload(Bucket=bucket, Key=probe_key,
                                          ContentType="application/octet-stream")
        s3.abort_multipart_upload(Bucket=bucket, Key=probe_key,
                                    UploadId=ma["UploadId"])
        results["multipart_create_abort"] = True
        results["probe_key_cleaned"] = probe_key
    except ClientError as e:
        code = e.response.get("Error", {}).get("Code", "Unknown")
        results["errors"].append(f"ClientError:{code}")
    except EndpointConnectionError as e:
        results["errors"].append(f"NetworkError:{type(e).__name__}")
    except HTTPException:
        raise
    except Exception as e:
        results["errors"].append(f"UnexpectedError:{type(e).__name__}:{e}")

    ok = (results["head_bucket"] and results["list_objects"]
          and results["multipart_create_abort"])

    audit.append_event(
        event="PROBE_S3_CREDENTIALS_Ω",
        slot_id="FORET_MFFP_PEE_MAJ_Ω",
        filename="(probe_s3_credentials)",
        sha256=None, size_bytes=0,
        http_code=200 if ok else 503,
        client_ip=client_ip, user_agent=ua,
        validators=[{"name": "probe_s3_credentials", "passed": ok,
                     "head_bucket": results["head_bucket"],
                     "list_objects": results["list_objects"],
                     "multipart_create_abort": results["multipart_create_abort"],
                     "errors_count": len(results["errors"])}],
    )

    return {
        "manifest_id": "PROBE_S3_CREDENTIALS_Ω",
        "doctrine": "ANTI_GÉNÉRIQUE_STRICT",
        "ok": ok,
        "bucket": os.environ.get("B2_BUCKET_NAME"),
        "endpoint": os.environ.get("B2_ENDPOINT_URL"),
        "region": os.environ.get("B2_REGION"),
        "tests": results,
        "v30_lock": "INVIOLÉ",
    }


# ═════════════════════════════════════════════════════════════════════════
# Endpoint : upload-chunk-s3 (streaming vers B2 multipart part)
# ═════════════════════════════════════════════════════════════════════════
@router.post("/upload-chunk-s3/{slot_id}")
async def upload_chunk_s3(
    slot_id: str,
    request: Request,
    file: UploadFile = File(...),
    x_commandant_token: Optional[str] = Header(default=None, alias="X-Commandant-Token"),
    x_upload_id: Optional[str] = Header(default=None, alias="X-Upload-Id"),
    x_chunk_index: Optional[int] = Header(default=None, alias="X-Chunk-Index"),
    x_chunks_total: Optional[int] = Header(default=None, alias="X-Chunks-Total"),
    x_original_filename: Optional[str] = Header(default=None, alias="X-Original-Filename"),
    x_total_size: Optional[int] = Header(default=None, alias="X-Total-Size"),
    x_final_chunk: Optional[str] = Header(default=None, alias="X-Final-Chunk"),
    user_agent: Optional[str] = Header(default=None, alias="User-Agent"),
) -> Dict[str, Any]:
    """ORDRE N°52-EXT VOIE B · Upload streaming chunk → B2 multipart part."""
    _verify_token(x_commandant_token)
    client_ip = request.client.host if request.client else "unknown"
    ua = (user_agent or "")[:200]

    # ─── ORDRE N°52-R5 · Forensic upload_id reçu (anti-ambiguïté) ─────
    # Tracer en hex la valeur EXACTE reçue pour permettre l'audit
    # forensique de toute confusion l/1/I/O/0 côté frontend.
    upload_id_hex = (
        (x_upload_id or "").encode("utf-8").hex() if x_upload_id else ""
    )
    # ─── ORDRE N°52-R6 · Détection mode RESUME explicite ──────────────
    # Si le upload_id correspond à une session existante avec parts
    # déjà reçus, on est en mode RESUME. Sinon, INITIATE.
    resume_mode_detected = False
    pre_session_parts_count = 0
    if x_upload_id:
        _pre_session = _read_session(x_upload_id)
        if _pre_session and _pre_session.get("parts"):
            resume_mode_detected = True
            pre_session_parts_count = len(_pre_session.get("parts", {}))
    if x_upload_id:
        logger.info(
            "S3_REQUEST_INCOMING slot=%s upload_id=%r upload_id_hex=%s "
            "chunk_index=%s chunks_total=%s resume_mode=%s "
            "pre_session_parts=%d",
            slot_id, x_upload_id, upload_id_hex,
            x_chunk_index, x_chunks_total,
            resume_mode_detected, pre_session_parts_count)

    # Normalisation Unicode (cohérence avec Voie A)
    import unicodedata as _ud
    slot_id = _ud.normalize("NFC", slot_id).replace("\u2126", "\u03a9")
    if slot_id not in SLOT_BY_ID:
        raise HTTPException(status_code=404,
                              detail=f"SLOT_INCONNU::{slot_id}")

    if not x_upload_id or not SAFE_UPLOAD_ID.match(x_upload_id):
        raise HTTPException(status_code=400,
                              detail="X-Upload-Id regex ^[A-Za-z0-9._-]{8,64}$")
    if x_chunk_index is None or x_chunk_index < 0:
        raise HTTPException(status_code=400, detail="X-Chunk-Index invalide")
    if not x_chunks_total or x_chunks_total < 1:
        raise HTTPException(status_code=400, detail="X-Chunks-Total invalide")
    if not x_original_filename or not SAFE_FILENAME.match(x_original_filename):
        raise HTTPException(status_code=400,
                              detail="X-Original-Filename unsafe")
    fname = x_original_filename

    is_final = (x_final_chunk or "").lower() in ("true", "1", "yes", "y")

    s3, bucket = _get_b2_client()
    session = _read_session(x_upload_id)

    # ─── Initier multipart upload si premier chunk ───────────────────
    if not session:
        if x_chunk_index != 0:
            raise HTTPException(
                status_code=409,
                detail=(
                    f"S3_SESSION_NOT_FOUND :: upload_id={x_upload_id}. "
                    "Le premier chunk doit avoir X-Chunk-Index=0 pour initier "
                    "la session multipart B2. Si le pod a redémarré, les "
                    "session files /app/backend/data/gis_s3_sessions/ SURVIVENT "
                    "(persistants) → re-GET /resume pour reprendre."))
        b2_key = f"pee_maj/{_utc_now()[:10]}/{x_upload_id}/{fname}"
        logger.info(
            "S3_INITIATE_MULTIPART slot=%s upload_id=%s b2_key=%s "
            "chunks_total=%d total_size=%d",
            slot_id, x_upload_id, b2_key, int(x_chunks_total),
            int(x_total_size or 0))
        try:
            ma = s3.create_multipart_upload(
                Bucket=bucket, Key=b2_key,
                ContentType="application/octet-stream",
                Metadata={
                    # S3 metadata doit être ASCII strict → encoder le slot_id
                    "slot-id-utf8-hex": slot_id.encode("utf-8").hex(),
                    "slot-id-ascii-slug": slot_id.encode("ascii", "replace")
                                                .decode("ascii").replace("?", "_"),
                    "upload-id-ui": x_upload_id,
                    "chunks-total": str(x_chunks_total),
                    "total-size": str(x_total_size or 0),
                    "client-ip": client_ip,
                },
            )
        except ClientError as e:
            logger.error(
                "B2_CREATE_MULTIPART_ERROR slot=%s upload_id=%s err=%s",
                slot_id, x_upload_id, e)
            raise HTTPException(
                status_code=502,
                detail=f"B2_CREATE_MULTIPART_ERROR::{e}")
        session = {
            "slot_id": slot_id,
            "upload_id_ui": x_upload_id,
            "b2_upload_id": ma["UploadId"],
            "b2_key": b2_key,
            "b2_bucket": bucket,
            "filename": fname,
            "chunks_total": int(x_chunks_total),
            "total_size_expected": int(x_total_size or 0),
            "parts": {},  # {chunk_index: {"etag": "...", "size": N, "sha256": "..."}}
            "started_at_utc": _utc_now(),
            "last_update_utc": _utc_now(),
            "status": "UPLOADING",
        }
        _write_session(x_upload_id, session)
    else:
        if session.get("filename") and session["filename"] != fname:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"FILENAME_MISMATCH :: session={session['filename']} "
                    f"vs header={fname}. Le upload_id fourni correspond à "
                    "une autre filename. Pour un nouveau fichier, utiliser "
                    "un upload_id frais (NE PAS le saisir dans le champ "
                    "'Reprise upload_id').")
            )
        if int(session.get("chunks_total", 0)) != int(x_chunks_total):
            raise HTTPException(
                status_code=400,
                detail=(
                    f"CHUNKS_TOTAL_MISMATCH :: session.chunks_total="
                    f"{session.get('chunks_total')} vs "
                    f"header.X-Chunks-Total={x_chunks_total}. Le fichier "
                    "déposé doit avoir EXACTEMENT la même taille que celui "
                    "de la session originale. Vérifier la taille du fichier "
                    f"(session attendait total_size={session.get('total_size_expected')}). "
                    "Pour un fichier différent, NE PAS utiliser la reprise "
                    "upload_id ; laisser le frontend générer un nouvel "
                    "uploadId frais."))
        # Log forensique de la résolution de session existante
        logger.info(
            "S3_RESUME_SESSION_LOADED slot=%s upload_id=%r "
            "b2_upload_id=%s b2_key=%s parts_already=%d/%d filename=%s",
            slot_id, x_upload_id, session.get("b2_upload_id"),
            session.get("b2_key"), len(session.get("parts", {})),
            int(x_chunks_total), session.get("filename"))

    # ─── Upload du part vers B2 (streaming) ──────────────────────────
    # B2 multipart : part_number = chunk_index + 1 (B2 part numbers start at 1)
    part_number = int(x_chunk_index) + 1
    # Si déjà uploadé (idempotence), on ne renvoie pas
    if str(x_chunk_index) in session.get("parts", {}):
        existing = session["parts"][str(x_chunk_index)]
        return {
            "manifest_id": "CHUNK_S3_ALREADY_UPLOADED",
            "slot_id": slot_id,
            "upload_id": x_upload_id,
            "upload_id_received": x_upload_id,
            "upload_id_received_hex": upload_id_hex,
            "resume_mode_detected": resume_mode_detected,
            "pre_session_parts_count": pre_session_parts_count,
            "chunk_index": int(x_chunk_index),
            "part_number": part_number,
            "etag": existing.get("etag"),
            "size_bytes": existing.get("size"),
            "idempotent_skip": True,
            "chunks_received_count": len(session.get("parts", {})),
            "chunks_total": int(x_chunks_total),
            "b2_upload_id": session["b2_upload_id"],
            "b2_key": session["b2_key"],
            "status": "CHUNK_STORED",
            "doctrine": "ANTI_GÉNÉRIQUE_STRICT",
        }

    # Lire chunk complet en RAM (max 50 Mo, acceptable)
    body = await file.read()
    chunk_size = len(body)
    chunk_sha = hashlib.sha256(body).hexdigest()
    try:
        resp = s3.upload_part(
            Bucket=bucket,
            Key=session["b2_key"],
            PartNumber=part_number,
            UploadId=session["b2_upload_id"],
            Body=body,
        )
        etag = resp["ETag"].strip('"')
        logger.info(
            "B2_UPLOAD_PART_OK slot=%s upload_id=%s part=%d size=%d etag=%s",
            slot_id, x_upload_id, part_number, chunk_size, etag)
    except ClientError as e:
        # ─── Distinguer quota dépassé (507) vs erreur réseau (502) ───
        err = e.response.get("Error", {}) if hasattr(e, "response") else {}
        err_code = (err.get("Code") or "").strip()
        err_msg = (err.get("Message") or str(e)).strip()
        is_quota_exceeded = (
            err_code == "AccessDenied"
            and "storage cap exceeded" in err_msg.lower()
        ) or "storage cap exceeded" in str(e).lower()
        logger.error(
            "B2_UPLOAD_PART_ERROR slot=%s upload_id=%s part=%d size=%d "
            "err_code=%s quota_exceeded=%s err=%s",
            slot_id, x_upload_id, part_number, chunk_size,
            err_code, is_quota_exceeded, e)
        if is_quota_exceeded:
            # Tentative d'auto-cleanup : abort des autres multipart
            # orphelins du même slot pour libérer du quota.
            audit.append_event(
                event="B2_STORAGE_CAP_EXCEEDED_Ω",
                slot_id=slot_id, filename=fname, sha256=None,
                size_bytes=chunk_size, http_code=507,
                client_ip=client_ip, user_agent=ua,
                validators=[{
                    "name": "b2_storage_cap_exceeded", "passed": False,
                    "err_code": err_code, "part_number": part_number,
                    "upload_id_ui": x_upload_id,
                    "remediation": (
                        "1. Augmenter le cap B2 (Caps & Alerts) OU "
                        "2. Appeler POST /s3/cleanup-orphans/{slot_id} pour "
                        "libérer les multipart inachevés."),
                }],
            )
            raise HTTPException(
                status_code=507,
                detail=(
                    f"B2_STORAGE_CAP_EXCEEDED::{err_code}::{err_msg} :: "
                    f"slot={slot_id} part={part_number} upload_id={x_upload_id}. "
                    "Action requise : augmenter le cap dans Backblaze B2 "
                    "(Caps & Alerts) puis re-POST le même chunk (idempotent). "
                    "OU POST /api/v30/admin-premium/gis/s3/cleanup-orphans/"
                    f"{slot_id} pour purger multipart orphelins consommant le quota."))
        # 502 générique pour erreurs B2 transitoires (réseau, throttle, etc.)
        raise HTTPException(
            status_code=502,
            detail=(
                f"B2_UPLOAD_PART_ERROR::{err_code}::{err_msg} :: "
                f"slot={slot_id} part={part_number} retryable=true"))
    finally:
        del body

    session.setdefault("parts", {})[str(x_chunk_index)] = {
        "part_number": part_number,
        "etag": etag,
        "size": chunk_size,
        "sha256": chunk_sha,
        "uploaded_at_utc": _utc_now(),
    }
    session["last_update_utc"] = _utc_now()
    _write_session(x_upload_id, session)

    audit.append_event(
        event="UPLOAD_CHUNK_S3_STORED_Ω",
        slot_id=slot_id, filename=fname, sha256=chunk_sha,
        size_bytes=0, http_code=200,
        client_ip=client_ip, user_agent=ua,
        validators=[{"name": "b2_upload_part", "passed": True,
                     "chunk_index": int(x_chunk_index),
                     "part_number": part_number,
                     "etag": etag,
                     "upload_id_ui": x_upload_id}],
    )

    # ─── Complete multipart si chunk final ──────────────────────────
    chunks_received_count = len(session["parts"])
    if is_final or chunks_received_count == int(x_chunks_total):
        if chunks_received_count != int(x_chunks_total):
            missing = sorted(
                set(range(int(x_chunks_total))) -
                set(int(k) for k in session["parts"].keys())
            )
            return {
                "manifest_id": "CHUNK_S3_STORED_AWAITING_COMPLETION",
                "status": "CHUNKS_INCOMPLETE",
                "chunks_received_count": chunks_received_count,
                "chunks_total": int(x_chunks_total),
                "chunks_missing": missing[:32],
                "chunks_missing_count": len(missing),
                "b2_upload_id": session["b2_upload_id"],
                "b2_key": session["b2_key"],
                "etag": etag,
                "upload_id": x_upload_id,
                "doctrine": "ANTI_GÉNÉRIQUE_STRICT",
            }
        # Toutes les parts reçues → complete_multipart_upload
        parts_list = sorted(
            [{"PartNumber": v["part_number"], "ETag": v["etag"]}
             for v in session["parts"].values()],
            key=lambda p: p["PartNumber"],
        )
        try:
            comp = s3.complete_multipart_upload(
                Bucket=bucket,
                Key=session["b2_key"],
                UploadId=session["b2_upload_id"],
                MultipartUpload={"Parts": parts_list},
            )
        except ClientError as e:
            logger.error(
                "B2_COMPLETE_MULTIPART_ERROR slot=%s key=%s parts=%d err=%s",
                slot_id, session["b2_key"], len(parts_list), e)
            raise HTTPException(status_code=502,
                                  detail=f"B2_COMPLETE_MULTIPART_ERROR::{e}")
        # Récupérer la taille réelle depuis B2
        try:
            head = s3.head_object(Bucket=bucket, Key=session["b2_key"])
            final_size = head["ContentLength"]
            s3_etag = head["ETag"].strip('"')
        except ClientError:
            final_size = 0
            s3_etag = comp.get("ETag", "").strip('"')
        session["status"] = "COMPLETED"
        session["completed_at_utc"] = _utc_now()
        session["final_s3_etag"] = s3_etag
        session["final_size_bytes"] = final_size
        _write_session(x_upload_id, session)
        logger.info(
            "B2_COMPLETE_MULTIPART_OK slot=%s key=%s parts=%d size=%d etag=%s",
            slot_id, session["b2_key"], len(parts_list), final_size, s3_etag)
        audit.append_event(
            event="UPLOAD_CHUNK_S3_COMPLETED_Ω",
            slot_id=slot_id, filename=fname, sha256=None,
            size_bytes=int(final_size), http_code=200,
            client_ip=client_ip, user_agent=ua,
            validators=[{"name": "b2_complete_multipart", "passed": True,
                         "b2_key": session["b2_key"],
                         "b2_upload_id": session["b2_upload_id"],
                         "parts_count": len(parts_list),
                         "final_etag": s3_etag,
                         "final_size_bytes": final_size}],
        )

        # ─── AUTO-FINALIZE ÉTENDU · ORDRE N°52-EXT VOIE B ──────────────
        # Stream SHA-256 depuis B2 + MAJ manifest institutionnel avec
        # setdefault (anti-KeyError) → passe le slot à LOADED en une
        # seule requête. Idempotent via session["manifest_finalized"].
        try:
            fin = _finalize_manifest_from_b2(session, s3, bucket)
        except HTTPException:
            raise
        except Exception as e:
            logger.error("AUTO_FINALIZE_MANIFEST_ERROR slot=%s err=%s",
                         slot_id, e)
            # On ne bloque pas la réponse COMPLETED : l'opérateur peut
            # rappeler /pee-maj/s3-finalize/{upload_id} (idempotent).
            return {
                "manifest_id": "CHUNK_S3_COMPLETED_MANIFEST_ERROR",
                "status": "COMPLETED_MANIFEST_PENDING",
                "slot_id": slot_id,
                "upload_id": x_upload_id,
                "b2_key": session["b2_key"],
                "b2_bucket": bucket,
                "final_size_bytes": final_size,
                "final_s3_etag": s3_etag,
                "parts_count": len(parts_list),
                "manifest_error": f"{type(e).__name__}:{e}",
                "recovery_endpoint": (
                    f"POST /api/v30/admin-premium/gis/pee-maj/s3-finalize/"
                    f"{x_upload_id}"),
                "doctrine": "ANTI_GÉNÉRIQUE_STRICT",
            }

        audit.append_event(
            event="PEE_MAJ_S3_FINALIZED_Ω",
            slot_id=slot_id, filename=fname,
            sha256=fin["sha256_global"],
            size_bytes=int(fin["size_bytes"]), http_code=200,
            client_ip=client_ip, user_agent=ua,
            validators=[
                {"name": "b2_stream_sha256", "passed": True,
                 "elapsed_s": fin["elapsed_s"],
                 "bytes_streamed": fin["size_bytes"]},
                {"name": "manifest_updated", "passed": True,
                 "composite_sha256": fin["composite_sha256"],
                 "slot_status": fin["slot_status"],
                 "files_loaded_count": fin["files_loaded_count"]},
            ],
        )

        return {
            "manifest_id": "CHUNK_S3_COMPLETED_AND_FINALIZED",
            "status": "COMPLETED",
            "slot_id": slot_id,
            "upload_id": x_upload_id,
            "b2_key": session["b2_key"],
            "b2_bucket": bucket,
            "final_size_bytes": fin["size_bytes"],
            "final_s3_etag": s3_etag,
            "parts_count": len(parts_list),
            "sha256_global": fin["sha256_global"],
            "stream_elapsed_s": fin["elapsed_s"],
            "composite_sha256": fin["composite_sha256"],
            "files_loaded_count": fin["files_loaded_count"],
            "slot_status": fin["slot_status"],
            "idempotent_finalize": fin.get("idempotent_skip", False),
            "next_step": (
                "Appeler POST /api/v30/admin-premium/gis/diagnostic/pee-maj/"
                "full-pipeline-execute pour déclencher le calcul des "
                "dérivées analytiques (9 couches) et la persistance "
                "locale dans /app/backend/data/gis_archive/."),
            "doctrine": "ANTI_GÉNÉRIQUE_STRICT",
        }

    progress_pct = round(
        (chunks_received_count / int(x_chunks_total)) * 100, 2)
    return {
        "manifest_id": "CHUNK_S3_STORED",
        "status": "CHUNK_STORED",
        "slot_id": slot_id,
        "upload_id": x_upload_id,
        "upload_id_received": x_upload_id,
        "upload_id_received_hex": upload_id_hex,
        "resume_mode_detected": resume_mode_detected,
        "pre_session_parts_count": pre_session_parts_count,
        "chunk_index": int(x_chunk_index),
        "part_number": part_number,
        "etag": etag,
        "chunks_received_count": chunks_received_count,
        "chunks_total": int(x_chunks_total),
        "progress_pct": progress_pct,
        "b2_upload_id": session["b2_upload_id"],
        "b2_key": session["b2_key"],
        "doctrine": "ANTI_GÉNÉRIQUE_STRICT",
    }


# ═════════════════════════════════════════════════════════════════════════
# Endpoint : resume (lit session persistante /app)
# ═════════════════════════════════════════════════════════════════════════
@router.get("/upload-chunk-s3/{slot_id}/resume/{upload_id}")
async def upload_chunk_s3_resume(
    slot_id: str, upload_id: str,
    x_commandant_token: Optional[str] = Header(default=None, alias="X-Commandant-Token"),
) -> Dict[str, Any]:
    _verify_token(x_commandant_token)
    import unicodedata as _ud
    slot_id = _ud.normalize("NFC", slot_id).replace("\u2126", "\u03a9")
    if slot_id not in SLOT_BY_ID:
        raise HTTPException(status_code=404, detail=f"SLOT_INCONNU::{slot_id}")
    if not SAFE_UPLOAD_ID.match(upload_id):
        raise HTTPException(status_code=400,
                              detail="upload_id regex ^[A-Za-z0-9._-]{8,64}$")

    session = _read_session(upload_id)
    if not session:
        return {
            "manifest_id": "S3_SESSION_NOT_FOUND",
            "upload_id": upload_id,
            "slot_id": slot_id,
            "session_exists": False,
            "chunks_received": [],
            "chunks_missing": [],
            "chunks_total": None,
            "instructions": "Démarrer nouvelle session : POST chunk_index=0.",
        }

    received = sorted(int(k) for k in session.get("parts", {}).keys())
    chunks_total = int(session.get("chunks_total") or 0)
    missing = sorted(set(range(chunks_total)) - set(received))
    return {
        "manifest_id": "UPLOAD_CHUNK_S3_RESUME_Ω",
        "upload_id": upload_id,
        "slot_id": slot_id,
        "session_exists": True,
        "filename": session.get("filename"),
        "b2_upload_id": session.get("b2_upload_id"),
        "b2_key": session.get("b2_key"),
        "chunks_total": chunks_total,
        "chunks_received": received,
        "chunks_received_count": len(received),
        "chunks_missing": missing,
        "chunks_missing_count": len(missing),
        "total_size_expected": session.get("total_size_expected"),
        "status": session.get("status"),
        "started_at_utc": session.get("started_at_utc"),
        "last_update_utc": session.get("last_update_utc"),
        "instructions": (
            "Ré-envoyer uniquement les chunks de chunks_missing via POST "
            "/upload-chunk-s3/{slot_id} avec le MÊME X-Upload-Id. "
            "Idempotent : re-POST d'un chunk déjà uploadé retourne 200 sans "
            "duplication (vérification session.parts)."),
        "doctrine": "ANTI_GÉNÉRIQUE_STRICT",
    }


# ═════════════════════════════════════════════════════════════════════════
# Endpoint : abort multipart
# ═════════════════════════════════════════════════════════════════════════
@router.post("/upload-chunk-s3/{slot_id}/abort/{upload_id}")
async def upload_chunk_s3_abort(
    slot_id: str, upload_id: str,
    request: Request,
    x_commandant_token: Optional[str] = Header(default=None, alias="X-Commandant-Token"),
    user_agent: Optional[str] = Header(default=None, alias="User-Agent"),
) -> Dict[str, Any]:
    _verify_token(x_commandant_token)
    import unicodedata as _ud
    slot_id = _ud.normalize("NFC", slot_id).replace("\u2126", "\u03a9")
    if slot_id not in SLOT_BY_ID:
        raise HTTPException(status_code=404, detail=f"SLOT_INCONNU::{slot_id}")

    session = _read_session(upload_id)
    if not session:
        raise HTTPException(status_code=404,
                              detail="S3_SESSION_NOT_FOUND")

    s3, bucket = _get_b2_client()
    try:
        s3.abort_multipart_upload(
            Bucket=bucket, Key=session["b2_key"],
            UploadId=session["b2_upload_id"])
    except ClientError as e:
        raise HTTPException(status_code=502,
                              detail=f"B2_ABORT_ERROR::{e}")

    session["status"] = "ABORTED"
    session["aborted_at_utc"] = _utc_now()
    _write_session(upload_id, session)

    audit.append_event(
        event="UPLOAD_CHUNK_S3_ABORTED_Ω",
        slot_id=slot_id, filename=session.get("filename"),
        sha256=None, size_bytes=0, http_code=200,
        client_ip=request.client.host if request.client else "unknown",
        user_agent=(user_agent or "")[:200],
        validators=[{"name": "b2_abort_multipart", "passed": True,
                     "b2_key": session["b2_key"]}],
    )
    return {
        "manifest_id": "UPLOAD_CHUNK_S3_ABORTED_Ω",
        "upload_id": upload_id,
        "aborted_at_utc": session["aborted_at_utc"],
        "doctrine": "ANTI_GÉNÉRIQUE_STRICT",
    }


# ═════════════════════════════════════════════════════════════════════════
# Endpoint : finalize (SHA-256 streaming depuis B2 + mise à jour manifest)
# ═════════════════════════════════════════════════════════════════════════
@router.post("/pee-maj/s3-finalize/{upload_id}")
async def pee_maj_s3_finalize(
    upload_id: str,
    request: Request,
    x_commandant_token: Optional[str] = Header(default=None, alias="X-Commandant-Token"),
    user_agent: Optional[str] = Header(default=None, alias="User-Agent"),
) -> Dict[str, Any]:
    """ORDRE N°52-EXT VOIE B · Finalize idempotent.

    Post-upload, calcule SHA-256 streaming depuis B2 et met à jour le
    manifest institutionnel pour passer le slot à LOADED.

    Cette route est automatiquement appelée par `upload-chunk-s3` quand
    `X-Final-Chunk=true` ; elle reste exposée pour permettre :
      · la récupération manuelle si la finalize auto a échoué
      · le recalcul idempotent du SHA-256
    """
    _verify_token(x_commandant_token)
    if not SAFE_UPLOAD_ID.match(upload_id):
        raise HTTPException(status_code=400,
                              detail="upload_id regex ^[A-Za-z0-9._-]{8,64}$")
    session = _read_session(upload_id)
    if not session:
        raise HTTPException(status_code=404,
                              detail="S3_SESSION_NOT_FOUND")
    if session.get("status") != "COMPLETED":
        raise HTTPException(
            status_code=409,
            detail=(
                f"SESSION_NOT_COMPLETED — status={session.get('status')}. "
                "Attendre tous les chunks avant finalize."))

    s3, bucket = _get_b2_client()
    logger.info(
        "S3_FINALIZE_MANUAL_CALL upload_id=%s slot=%s b2_key=%s",
        upload_id, session.get("slot_id"), session.get("b2_key"))
    fin = _finalize_manifest_from_b2(session, s3, bucket)

    audit.append_event(
        event="PEE_MAJ_S3_FINALIZED_Ω",
        slot_id=session["slot_id"],
        filename=session["filename"],
        sha256=fin["sha256_global"],
        size_bytes=int(fin["size_bytes"]), http_code=200,
        client_ip=request.client.host if request.client else "unknown",
        user_agent=(user_agent or "")[:200],
        validators=[
            {"name": "b2_stream_sha256", "passed": True,
             "elapsed_s": fin["elapsed_s"],
             "bytes_streamed": fin["size_bytes"]},
            {"name": "manifest_updated", "passed": True,
             "composite_sha256": fin["composite_sha256"],
             "slot_status": fin["slot_status"],
             "files_loaded_count": fin["files_loaded_count"],
             "idempotent_skip": fin.get("idempotent_skip", False)},
        ],
    )

    return {
        "manifest_id": "PEE_MAJ_S3_FINALIZED_Ω",
        "doctrine": "ANTI_GÉNÉRIQUE_STRICT",
        "upload_id": upload_id,
        "slot_id": session["slot_id"],
        "b2_key": session["b2_key"],
        "b2_bucket": bucket,
        "sha256_global": fin["sha256_global"],
        "size_bytes": fin["size_bytes"],
        "stream_elapsed_s": fin["elapsed_s"],
        "slot_status": fin["slot_status"],
        "composite_sha256": fin["composite_sha256"],
        "files_loaded_count": fin["files_loaded_count"],
        "idempotent_skip": fin.get("idempotent_skip", False),
        "note": (
            "pee_maj.gpkg est désormais persistant sur Backblaze B2. "
            "Le fichier brut est à l'abri du pod restart. Appeler ensuite "
            "/diagnostic/pee-maj/full-pipeline-execute pour déclencher "
            "compute + persist_derivatives + compress_and_archive."),
        "v30_lock": "INVIOLÉ",
    }


# ═════════════════════════════════════════════════════════════════════════
# Endpoint : GIS S3 status diagnostic structuré (ORDRE N°52-EXT ÉTENDU)
# ═════════════════════════════════════════════════════════════════════════
@router.get("/s3/status/{slot_id}")
async def gis_s3_status(
    slot_id: str,
    x_commandant_token: Optional[str] = Header(default=None, alias="X-Commandant-Token"),
) -> Dict[str, Any]:
    """Diagnostic structuré du slot S3/B2.

    Agrège :
      · Les sessions S3 locales (/app/backend/data/gis_s3_sessions/)
      · L'état du slot dans le manifest GIS_RECEPTION_INTAKE_Ω
      · La liste des objets B2 sous le préfixe `pee_maj/`
      · Les uploads multipart en cours (list_multipart_uploads)

    Aucune mutation. Lecture seule. Permet d'auditer l'état complet
    d'un slot pour détecter des incohérences (session orpheline,
    manifest désynchronisé, objet B2 sans entrée manifest, etc.).
    """
    _verify_token(x_commandant_token)
    import unicodedata as _ud
    slot_id = _ud.normalize("NFC", slot_id).replace("\u2126", "\u03a9")
    if slot_id not in SLOT_BY_ID:
        raise HTTPException(status_code=404, detail=f"SLOT_INCONNU::{slot_id}")

    # ─── Sessions locales persistantes ────────────────────────────────
    sessions_summary: List[Dict[str, Any]] = []
    try:
        for p in sorted(S3_SESSIONS_DIR.glob("*.json")):
            try:
                sess = json.loads(p.read_text(encoding="utf-8"))
            except Exception:
                continue
            if sess.get("slot_id") != slot_id:
                continue
            parts = sess.get("parts", {}) or {}
            sessions_summary.append({
                "upload_id_ui": sess.get("upload_id_ui"),
                "b2_upload_id": sess.get("b2_upload_id"),
                "b2_key": sess.get("b2_key"),
                "filename": sess.get("filename"),
                "status": sess.get("status"),
                "chunks_total": sess.get("chunks_total"),
                "chunks_received_count": len(parts),
                "total_size_expected": sess.get("total_size_expected"),
                "final_size_bytes": sess.get("final_size_bytes"),
                "sha256_global": sess.get("sha256_global"),
                "manifest_finalized": bool(sess.get("manifest_finalized")),
                "started_at_utc": sess.get("started_at_utc"),
                "last_update_utc": sess.get("last_update_utc"),
                "completed_at_utc": sess.get("completed_at_utc"),
                "session_file": str(p),
            })
    except Exception as e:
        logger.warning("S3_STATUS_SESSIONS_SCAN_ERROR: %s", e)

    # ─── État du slot dans le manifest ────────────────────────────────
    manifest = _read_manifest_raw()
    slot_entry = manifest.get("slots", {}).get(slot_id, {})

    # ─── B2 live : objets existants + multipart en cours ──────────────
    b2_objects: List[Dict[str, Any]] = []
    b2_in_progress: List[Dict[str, Any]] = []
    b2_errors: List[str] = []
    try:
        s3, bucket = _get_b2_client()
        try:
            r = s3.list_objects_v2(Bucket=bucket,
                                   Prefix="pee_maj/", MaxKeys=100)
            for o in r.get("Contents", []) or []:
                b2_objects.append({
                    "key": o["Key"],
                    "size": o["Size"],
                    "etag": (o.get("ETag") or "").strip('"'),
                    "last_modified": (
                        o.get("LastModified").isoformat()
                        if o.get("LastModified") else None),
                })
        except ClientError as e:
            b2_errors.append(
                f"list_objects_v2: {e.response.get('Error',{}).get('Code','?')}")

        try:
            mpu = s3.list_multipart_uploads(Bucket=bucket, Prefix="pee_maj/")
            for u in mpu.get("Uploads", []) or []:
                b2_in_progress.append({
                    "key": u.get("Key"),
                    "upload_id": u.get("UploadId"),
                    "initiated": (u.get("Initiated").isoformat()
                                  if u.get("Initiated") else None),
                })
        except ClientError as e:
            b2_errors.append(
                f"list_multipart_uploads: "
                f"{e.response.get('Error',{}).get('Code','?')}")
    except HTTPException:
        b2_errors.append("B2_CREDENTIALS_NOT_CONFIGURED")
    except EndpointConnectionError as e:
        b2_errors.append(f"NetworkError:{type(e).__name__}")
    except Exception as e:
        b2_errors.append(f"UnexpectedError:{type(e).__name__}:{e}")

    return {
        "manifest_id": "GIS_S3_STATUS_Ω",
        "doctrine": "ANTI_GÉNÉRIQUE_STRICT",
        "slot_id": slot_id,
        "slot_spec": {
            "label": SLOT_BY_ID[slot_id].get("label"),
            "priority": SLOT_BY_ID[slot_id].get("priority"),
            "organisme": SLOT_BY_ID[slot_id].get("organisme"),
            "voie_acquisition": SLOT_BY_ID[slot_id].get("voie_acquisition"),
        },
        "manifest_slot": {
            "status": slot_entry.get("status"),
            "files_loaded_count": slot_entry.get("files_loaded_count"),
            "composite_sha256": slot_entry.get("composite_sha256"),
            "uploads_count": len(slot_entry.get("uploads", [])),
            "uploads": slot_entry.get("uploads", []),
        },
        "local_sessions": {
            "count": len(sessions_summary),
            "sessions": sessions_summary,
        },
        "b2_live": {
            "bucket": os.environ.get("B2_BUCKET_NAME"),
            "endpoint": os.environ.get("B2_ENDPOINT_URL"),
            "objects_count": len(b2_objects),
            "objects": b2_objects,
            "multipart_in_progress_count": len(b2_in_progress),
            "multipart_in_progress": b2_in_progress,
            "errors": b2_errors,
        },
        "v30_lock": "INVIOLÉ",
    }


# ═════════════════════════════════════════════════════════════════════════
# Endpoint : cleanup-orphans — abort des multipart orphelins (P0)
# ═════════════════════════════════════════════════════════════════════════
@router.post("/s3/cleanup-orphans/{slot_id}")
async def gis_s3_cleanup_orphans(
    slot_id: str,
    request: Request,
    confirm: Optional[str] = None,
    dry_run: Optional[str] = None,
    x_commandant_token: Optional[str] = Header(default=None, alias="X-Commandant-Token"),
    user_agent: Optional[str] = Header(default=None, alias="User-Agent"),
) -> Dict[str, Any]:
    """ORDRE N°52-PRE-AUDIT · Abort des multipart inachevés sur B2.

    Libère le quota B2 consommé par des sessions multipart abandonnées
    (pod restart, frontend fermé, quota dépassé en cours d'upload).

    Sécurité : exige `?confirm=true` pour effectuer l'abort.
    Sans `confirm`, fonctionne en dry-run (liste seulement).

    Met à jour les sessions locales en conséquence (status=ABORTED).
    """
    _verify_token(x_commandant_token)
    import unicodedata as _ud
    slot_id = _ud.normalize("NFC", slot_id).replace("\u2126", "\u03a9")
    if slot_id not in SLOT_BY_ID:
        raise HTTPException(status_code=404, detail=f"SLOT_INCONNU::{slot_id}")
    do_abort = (confirm or "").lower() in ("true", "1", "yes", "y")
    do_dry_run = (dry_run or "").lower() in ("true", "1", "yes", "y") or not do_abort
    client_ip = request.client.host if request.client else "unknown"
    ua = (user_agent or "")[:200]

    s3, bucket = _get_b2_client()
    aborted: List[Dict[str, Any]] = []
    skipped: List[Dict[str, Any]] = []
    errors: List[str] = []

    try:
        mpu = s3.list_multipart_uploads(Bucket=bucket, Prefix="pee_maj/")
        for u in mpu.get("Uploads", []) or []:
            entry = {
                "key": u.get("Key"),
                "upload_id": u.get("UploadId"),
                "initiated": (u.get("Initiated").isoformat()
                              if u.get("Initiated") else None),
            }
            if do_dry_run:
                skipped.append({**entry, "would_abort": True})
                continue
            try:
                s3.abort_multipart_upload(
                    Bucket=bucket, Key=entry["key"],
                    UploadId=entry["upload_id"])
                aborted.append(entry)
                logger.info("B2_ABORT_OK key=%s upload_id=%s",
                            entry["key"], entry["upload_id"])
            except ClientError as e:
                errors.append(
                    f"abort {entry['key']}: "
                    f"{e.response.get('Error',{}).get('Code','?')}")
                logger.error("B2_ABORT_ERROR key=%s err=%s",
                             entry["key"], e)
    except ClientError as e:
        errors.append(
            f"list_multipart_uploads: "
            f"{e.response.get('Error',{}).get('Code','?')}")

    # ─── Mise à jour des sessions locales correspondantes ───────────
    sessions_updated: List[str] = []
    if do_abort and aborted:
        aborted_b2_upload_ids = {a["upload_id"] for a in aborted}
        try:
            for p in S3_SESSIONS_DIR.glob("*.json"):
                try:
                    sess = json.loads(p.read_text(encoding="utf-8"))
                except Exception:
                    continue
                if (sess.get("b2_upload_id") in aborted_b2_upload_ids
                        and sess.get("status") not in ("ABORTED", "COMPLETED")):
                    sess["status"] = "ABORTED"
                    sess["aborted_at_utc"] = _utc_now()
                    sess["aborted_by"] = "cleanup_orphans_omega"
                    _write_session(sess["upload_id_ui"], sess)
                    sessions_updated.append(sess["upload_id_ui"])
        except Exception as e:
            errors.append(f"sessions_update: {type(e).__name__}:{e}")

    audit.append_event(
        event="GIS_S3_CLEANUP_ORPHANS_Ω",
        slot_id=slot_id, filename="(cleanup_orphans)", sha256=None,
        size_bytes=0,
        http_code=200, client_ip=client_ip, user_agent=ua,
        validators=[{
            "name": "cleanup_orphans", "passed": len(errors) == 0,
            "dry_run": do_dry_run,
            "aborted_count": len(aborted),
            "skipped_count": len(skipped),
            "sessions_updated_count": len(sessions_updated),
            "errors_count": len(errors),
        }],
    )
    return {
        "manifest_id": "GIS_S3_CLEANUP_ORPHANS_Ω",
        "doctrine": "ANTI_GÉNÉRIQUE_STRICT",
        "slot_id": slot_id,
        "dry_run": do_dry_run,
        "confirm_was_passed": do_abort,
        "aborted_count": len(aborted),
        "aborted": aborted,
        "skipped_count": len(skipped),
        "skipped": skipped,
        "sessions_updated_count": len(sessions_updated),
        "sessions_updated": sessions_updated,
        "errors": errors,
        "instructions": (
            "Pour effectuer l'abort réellement : ré-appeler avec ?confirm=true. "
            "Cela libère le quota B2 consommé par les multipart inachevés."
            if do_dry_run else
            "Cleanup effectué. Quota B2 libéré pour les multipart abortés."),
        "v30_lock": "INVIOLÉ",
    }


# ═════════════════════════════════════════════════════════════════════════
# Endpoint : list-resumable-sessions (ORDRE N°52-R5 anti-ambiguïté)
# ═════════════════════════════════════════════════════════════════════════
@router.get("/s3/list-resumable-sessions/{slot_id}")
async def gis_s3_list_resumable_sessions(
    slot_id: str,
    x_commandant_token: Optional[str] = Header(default=None, alias="X-Commandant-Token"),
) -> Dict[str, Any]:
    """ORDRE N°52-R5 · Liste les sessions S3 reprenables pour un slot.

    Permet au frontend de présenter une liste cliquable d'upload_ids
    existants au lieu d'exiger une saisie manuelle (qui peut souffrir
    de confusions visuelles l/1/I/O/0 selon la police du navigateur).

    Critères d'inclusion :
      · status == UPLOADING (session active interrompue)
      · status == ABORTED si chunks_received > 0 (référence historique)
      · Filtré par slot_id

    Renvoie pour chaque session :
      · upload_id_ui : valeur exacte (pour copy direct)
      · upload_id_hex : pour vérification anti-ambiguïté
      · chunks_received / chunks_total / chunks_missing_first[]
      · status, started_at_utc, last_update_utc
      · resumable: bool (true si status==UPLOADING + 0 missing en [0..max])
    """
    _verify_token(x_commandant_token)
    import unicodedata as _ud
    slot_id = _ud.normalize("NFC", slot_id).replace("\u2126", "\u03a9")
    if slot_id not in SLOT_BY_ID:
        raise HTTPException(status_code=404, detail=f"SLOT_INCONNU::{slot_id}")

    sessions: List[Dict[str, Any]] = []
    try:
        for p in sorted(S3_SESSIONS_DIR.glob("*.json")):
            try:
                sess = json.loads(p.read_text(encoding="utf-8"))
            except Exception:
                continue
            if sess.get("slot_id") != slot_id:
                continue
            status = sess.get("status")
            if status not in ("UPLOADING", "ABORTED"):
                continue
            parts = sess.get("parts", {}) or {}
            chunks_total = int(sess.get("chunks_total") or 0)
            received_idx = sorted(int(k) for k in parts.keys())
            received_count = len(received_idx)
            missing = (
                sorted(set(range(chunks_total)) - set(received_idx))
                if chunks_total else []
            )
            uid_ui = sess.get("upload_id_ui") or ""
            sessions.append({
                "upload_id_ui": uid_ui,
                "upload_id_hex": uid_ui.encode("utf-8").hex(),
                "filename": sess.get("filename"),
                "status": status,
                "chunks_total": chunks_total,
                "chunks_received_count": received_count,
                "chunks_missing_count": len(missing),
                "chunks_missing_first": missing[:5],
                "first_received_idx": received_idx[0] if received_idx else None,
                "last_received_idx": received_idx[-1] if received_idx else None,
                "total_size_expected": sess.get("total_size_expected"),
                "started_at_utc": sess.get("started_at_utc"),
                "last_update_utc": sess.get("last_update_utc"),
                "b2_upload_id": sess.get("b2_upload_id"),
                "b2_key": sess.get("b2_key"),
                "resumable": (
                    status == "UPLOADING" and received_count > 0 and
                    received_count < chunks_total
                ),
            })
    except Exception as e:
        logger.warning("LIST_RESUMABLE_SESSIONS_ERROR: %s", e)

    return {
        "manifest_id": "GIS_S3_LIST_RESUMABLE_SESSIONS_Ω",
        "doctrine": "ANTI_GÉNÉRIQUE_STRICT",
        "slot_id": slot_id,
        "sessions_count": len(sessions),
        "sessions": sessions,
        "anti_ambiguity_note": (
            "Pour éviter toute confusion visuelle l/1/I/O/0, utiliser "
            "upload_id_ui (string brute) et vérifier upload_id_hex "
            "(encodage UTF-8). Le frontend doit utiliser ces valeurs "
            "telles quelles, sans réécriture."),
        "v30_lock": "INVIOLÉ",
    }


__all__ = ["router"]


# ═════════════════════════════════════════════════════════════════════════
# ORDRE N°52-R9 · Amplification MFFP×1000 (Registre + Recalc planner)
# ═════════════════════════════════════════════════════════════════════════
@router.get("/territoire/mffp-master-weights")
async def get_mffp_master_weights(
    x_commandant_token: Optional[str] = Header(default=None, alias="X-Commandant-Token"),
) -> Dict[str, Any]:
    """ORDRE N°52-R9 · Lecture du registre de pondération MFFP×1000."""
    _verify_token(x_commandant_token)
    from engines.v8_institutional.especes.mffp_master_weight_registry_omega \
        import read_master_weights, check_mffp_derived_layers_availability
    weights = read_master_weights()
    availability = check_mffp_derived_layers_availability()
    return {
        "manifest_id": "MFFP_MASTER_WEIGHTS_LIVE_Ω",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "ordre": "N°52-R9",
        "weights": weights,
        "mffp_derived_layers_availability": availability,
    }


@router.post("/territoire/mffp-master-weights/activate")
async def activate_mffp_master_weights(
    request: Request,
    deactivate: Optional[str] = None,
    x_commandant_token: Optional[str] = Header(default=None, alias="X-Commandant-Token"),
) -> Dict[str, Any]:
    """ORDRE N°52-R9 · Active (ou désactive avec ?deactivate=true) le registre."""
    _verify_token(x_commandant_token)
    from engines.v8_institutional.especes.mffp_master_weight_registry_omega \
        import activate_mffp_master, deactivate_mffp_master
    do_deact = (deactivate or "").lower() in ("true", "1", "yes", "y")
    if do_deact:
        w = deactivate_mffp_master(authority="COMMANDANT_STEEVE_MAX")
        return {
            "manifest_id": "MFFP_MASTER_WEIGHTS_DEACTIVATED",
            "ordre": "N°52-R9",
            "weights": w,
            "active": False,
        }
    w = activate_mffp_master(authority="COMMANDANT_STEEVE_MAX")
    return {
        "manifest_id": "MFFP_MASTER_WEIGHTS_ACTIVATED",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "ordre": "N°52-R9",
        "weights": w,
        "active": True,
    }


@router.post("/territoire/r9-recalc-execute")
async def territoire_r9_recalc_execute(
    request: Request,
    force: Optional[str] = None,
    x_commandant_token: Optional[str] = Header(default=None, alias="X-Commandant-Token"),
) -> Dict[str, Any]:
    """ORDRE N°52-R9 · Lance le planificateur de recalcul R9 en background.

    · Active automatiquement le registre MFFP×1000 si non actif.
    · Pour chaque cible (corridors/hotspots/affuts/salines/zones_*),
      vérifie la disponibilité des couches MFFP dérivées (PHASE_3 R8).
    · Si couches indisponibles → STUB_READY_BLOCKED_BY_R8_PHASE_3.
    · Marque tous les moteurs dépendants en `force_rebuild_pending=true`.
    · Génère un rapport BIONIC_AMPLIFICATION_REPORT.json.
    """
    _verify_token(x_commandant_token)
    from engines.v8_institutional.especes.mffp_master_weight_registry_omega \
        import start_r9_recalc_background
    force_bool = (force or "").lower() in ("true", "1", "yes", "y")
    result = start_r9_recalc_background(force=force_bool)
    if not result["ok"]:
        raise HTTPException(
            status_code=409,
            detail={
                "reason": result["reason"],
                "current_state_summary": {
                    "run_id": result["current_state"].get("run_id"),
                    "status": result["current_state"].get("status"),
                    "started_at_utc": result["current_state"].get(
                        "started_at_utc"),
                },
            })
    return {
        "manifest_id": "TERRITOIRE_R9_RECALC_ACCEPTED",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "ordre": "N°52-R9",
        **result,
        "poll_endpoint": "/api/v30/admin-premium/gis/territoire/r9-recalc-status",
        "v30_lock": "INVIOLÉ",
    }


@router.get("/territoire/r9-recalc-status")
async def territoire_r9_recalc_status(
    x_commandant_token: Optional[str] = Header(default=None, alias="X-Commandant-Token"),
) -> Dict[str, Any]:
    """ORDRE N°52-R9 · Lit le state file live du recalcul R9."""
    _verify_token(x_commandant_token)
    from engines.v8_institutional.especes.mffp_master_weight_registry_omega \
        import read_r9_state, R9_STATE_PATH
    state = read_r9_state()
    if not state:
        return {
            "manifest_id": "TERRITOIRE_R9_STATUS_Ω",
            "status": "NEVER_STARTED",
            "state_path": str(R9_STATE_PATH),
            "note": ("Aucun run R9 encore démarré. POST /territoire/"
                     "r9-recalc-execute pour lancer."),
        }
    return {
        "manifest_id": "TERRITOIRE_R9_STATUS_Ω",
        **state,
        "state_path": str(R9_STATE_PATH),
        "v30_lock": "INVIOLÉ",
    }


# ═════════════════════════════════════════════════════════════════════════
# ORDRE N°52-R11 · Specs PHASE_3 R8 (lecture seule)
# ═════════════════════════════════════════════════════════════════════════
@router.get("/diagnostic/pee-maj/phase3-specs")
async def get_phase3_specs(
    layer: Optional[str] = None,
    x_commandant_token: Optional[str] = Header(default=None, alias="X-Commandant-Token"),
) -> Dict[str, Any]:
    """ORDRE N°52-R11 · Expose les spécifications canoniques des 8 couches
    MFFP dérivées + plan d'implémentation minimal PHASE_3 R8.

    Si query `?layer=MFFP_STRUCTURE` (ou autre), retourne uniquement la
    spec ciblée. Sinon retourne les 8 specs + plan minimal.
    """
    _verify_token(x_commandant_token)
    from engines.v8_institutional.especes.mffp_phase3_specs_omega import (
        MFFP_LAYERS_SPECS, PHASE3_MINIMAL_PLAN,
    )
    if layer:
        if layer not in MFFP_LAYERS_SPECS:
            raise HTTPException(
                status_code=404,
                detail=f"LAYER_INCONNUE::{layer} :: "
                       f"connues={list(MFFP_LAYERS_SPECS.keys())}")
        return {
            "manifest_id": "MFFP_PHASE3_SPECS_Ω",
            "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
            "ordre": "N°52-R11",
            "layer_id": layer,
            "spec": MFFP_LAYERS_SPECS[layer],
            "v30_lock": "INVIOLÉ",
        }
    return {
        "manifest_id": "MFFP_PHASE3_SPECS_Ω",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "ordre": "N°52-R11",
        "layers_count": len(MFFP_LAYERS_SPECS),
        "layers": MFFP_LAYERS_SPECS,
        "minimal_plan": PHASE3_MINIMAL_PLAN,
        "function_skeletons_module": (
            "engines.v8_institutional.especes.mffp_phase3_specs_omega"),
        "function_skeletons": [
            "compute_mffp_structure", "compute_mffp_density",
            "compute_mffp_age", "compute_mffp_fragmentation",
            "compute_mffp_productivity", "compute_mffp_habitat",
            "compute_mffp_connectivity", "compute_mffp_continuity",
        ],
        "v30_lock": "INVIOLÉ",
    }


# ═════════════════════════════════════════════════════════════════════════
# ORDRE N°52-R12 · Dictionnaires PROPOSÉS + Subset proposal
# ═════════════════════════════════════════════════════════════════════════
@router.get("/territoire/dictionaries-proposed")
async def get_dictionaries_proposed(
    name: Optional[str] = None,
    x_commandant_token: Optional[str] = Header(default=None, alias="X-Commandant-Token"),
) -> Dict[str, Any]:
    """ORDRE N°52-R12 · Expose les 4 dictionnaires PROPOSÉS pour PHASE_3 R8.

    Filtre optionnel `?name=cl_dens_to_pct` pour retourner uniquement un
    dictionnaire ciblé. Sinon retourne tous les dictionnaires + statuts.
    """
    _verify_token(x_commandant_token)
    from engines.v8_institutional.especes.mffp_dictionaries_loader_omega \
        import (
            load_dictionary, load_all_dictionaries,
            all_proposed_dictionaries_status, all_validated_for_p0,
            list_validation_blockers,
        )
    if name:
        try:
            d = load_dictionary(name)
        except KeyError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except FileNotFoundError as e:
            raise HTTPException(status_code=500, detail=str(e))
        return {
            "manifest_id": "MFFP_DICTIONARY_PROPOSED_Ω",
            "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
            "ordre": "N°52-R12",
            "dictionary_name": name,
            "content": d,
            "v30_lock": "INVIOLÉ",
        }
    statuses = all_proposed_dictionaries_status()
    validated = all_validated_for_p0()
    blockers = list_validation_blockers()
    return {
        "manifest_id": "MFFP_DICTIONARIES_PROPOSED_Ω",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "ordre": "N°52-R12",
        "dictionaries_count": len(statuses),
        "dictionaries": load_all_dictionaries(),
        "statuses_summary": statuses,
        "all_validated_for_p0": validated,
        "validation_blockers": blockers,
        "next_steps": (
            "Pour valider un dictionnaire, modifier le champ `status` de "
            "PROPOSÉ → VALIDÉ dans le fichier JSON correspondant sous "
            "/app/backend/data/territoire/dictionaries_proposed/. "
            "Une fois les 4 dicts validés, P0 PHASE_3 R8 peut être "
            "implémentée."
            if not validated else
            "Tous les dicts P0 sont VALIDÉS. PHASE_3 R8 peut commencer."),
        "v30_lock": "INVIOLÉ",
    }


@router.post("/diagnostic/pee-maj/export-subset")
async def export_subset_proposal(
    request: Request,
    execute: Optional[str] = None,
    target_size_mb: int = 100,
    x_commandant_token: Optional[str] = Header(default=None, alias="X-Commandant-Token"),
) -> Dict[str, Any]:
    """ORDRE N°52-R12/R13 · Export subset ~100 Mo de pee_maj.gpkg.

    · Mode PROPOSAL (défaut, `?execute=false`) : retourne plan complet
      (bbox, filtres, commande GDAL prête à exécuter).
    · Mode EXÉCUTION (`?execute=true`, R13) : extraction réelle via pyogrio
      si pee_maj.gpkg local présent. Sinon HTTP 503.
    """
    _verify_token(x_commandant_token)
    from engines.v8_institutional.especes.mffp_subset_extractor_omega import (
        build_subset_proposal, execute_subset_extraction,
        check_pee_maj_local_present,
    )
    do_execute = (execute or "").lower() in ("true", "1", "yes", "y")
    proposal = build_subset_proposal(target_size_mb=target_size_mb)
    if not do_execute:
        return {
            **proposal,
            "execution_mode": "PROPOSAL_ONLY",
            "next_action_to_execute": (
                "Re-POST avec ?execute=true pour tenter l'extraction. "
                "Prérequis : R8 PHASE_1 do_pull=true exécuté avec succès."),
        }
    # Mode EXÉCUTION
    presence = check_pee_maj_local_present()
    if not presence["present"] or not presence.get("is_complete"):
        raise HTTPException(
            status_code=503,
            detail={
                "reason": "PEE_MAJ_NOT_PRESENT_LOCALLY",
                "presence": presence,
                "remediation": (
                    "Lancer POST /diagnostic/pee-maj/r8-execute?do_pull=true "
                    "et attendre la fin avant retry."),
                "fallback_proposal": proposal,
            })
    try:
        result = execute_subset_extraction()
        return {**proposal, "execution_result": result,
                "execution_mode": "EXECUTED"}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "reason": "SUBSET_EXTRACTION_FAILED",
                "error": str(e)[:500],
                "fallback_proposal": proposal,
            })


# ═════════════════════════════════════════════════════════════════════════
# ORDRE N°52-R13 · Implémentation P0 PHASE_3 R8 (4 couches MFFP)
# ═════════════════════════════════════════════════════════════════════════
@router.post("/diagnostic/pee-maj/phase3-p0-execute")
async def phase3_p0_execute(
    request: Request,
    layer: Optional[str] = None,
    input_path: Optional[str] = None,
    x_commandant_token: Optional[str] = Header(default=None, alias="X-Commandant-Token"),
) -> Dict[str, Any]:
    """ORDRE N°52-R13 · Exécute une (ou les 4) couches P0 PHASE_3 R8.

    Args:
      layer : ?layer=MFFP_DENSITY|MFFP_AGE|MFFP_STRUCTURE|MFFP_FRAGMENTATION
              ou absent = exécution séquentielle des 4 couches P0.
      input_path : ?input_path=... (chemin local explicite). Sinon, par
                   défaut subset le plus récent ; sinon pee_maj.gpkg.

    Prérequis :
      · 4 dictionnaires VALIDÉS (R12 + R13 status='VALIDÉ')
      · pee_maj.gpkg ou subset présent localement
    """
    _verify_token(x_commandant_token)
    from engines.v8_institutional.especes.mffp_dictionaries_loader_omega \
        import load_dictionary, all_validated_for_p0, list_validation_blockers
    from engines.v8_institutional.especes.mffp_phase3_p0_omega import (
        compute_mffp_density, compute_mffp_age, compute_mffp_structure,
        compute_forest_binary_raster, compute_mffp_fragmentation,
        DERIVATIVES_OUTPUT_ROOT,
    )

    if not all_validated_for_p0():
        raise HTTPException(
            status_code=409,
            detail={
                "reason": "DICTIONARIES_NOT_ALL_VALIDATED",
                "blockers": list_validation_blockers(),
                "remediation": (
                    "Faire passer status=PROPOSÉ → VALIDÉ pour les 4 dicts."),
            })

    # Résolution du chemin d'entrée
    import glob
    src = input_path
    if not src:
        # Cherche subset le plus récent
        subsets_root = "/app/backend/data/gis_archive/subsets"
        candidates = sorted(glob.glob(f"{subsets_root}/pee_maj_subset_*.gpkg"))
        if candidates:
            src = candidates[-1]
    if not src:
        # Fallback : pee_maj.gpkg complet
        full_path = (
            "/var/cache/gis_operational/incoming/"
            "FORET_MFFP_PEE_MAJ_Ω/pee_maj.gpkg")
        if Path(full_path).exists():
            src = full_path
    if not src or not Path(src).exists():
        raise HTTPException(
            status_code=503,
            detail={
                "reason": "NO_INPUT_FILE_AVAILABLE",
                "remediation": (
                    "1. Lancer POST /diagnostic/pee-maj/r8-execute?do_pull=true "
                    "puis POST /diagnostic/pee-maj/export-subset?execute=true. "
                    "2. OU passer ?input_path=/path/to/file.gpkg explicite."),
            })

    # Charger les dicts validés
    cl_dens_dict = load_dictionary("cl_dens_to_pct")
    classes_age_dict = load_dictionary("classes_age")
    structure_rules_dict = load_dictionary("structure_classification_rules")
    ty_couv_dict = load_dictionary("ty_couv_to_forest_binary")

    layers_to_run = (
        [layer] if layer else
        ["MFFP_DENSITY", "MFFP_AGE", "MFFP_STRUCTURE", "MFFP_FRAGMENTATION"]
    )
    results: Dict[str, Any] = {}
    for L in layers_to_run:
        try:
            if L == "MFFP_DENSITY":
                results[L] = compute_mffp_density(src, cl_dens_dict)
            elif L == "MFFP_AGE":
                results[L] = compute_mffp_age(src, classes_age_dict)
            elif L == "MFFP_STRUCTURE":
                results[L] = compute_mffp_structure(src, structure_rules_dict)
            elif L == "MFFP_FRAGMENTATION":
                # Étape préalable : binary raster
                binary_res = compute_forest_binary_raster(
                    src, ty_couv_dict)
                results["GIS_COUVERT_FORESTIER_BINARY_50M"] = binary_res
                # Calcul fragmentation Dickson 2017
                results[L] = compute_mffp_fragmentation(
                    binary_res["output_path"])
            else:
                raise HTTPException(
                    status_code=400,
                    detail=f"LAYER_INCONNUE::{L}")
        except Exception as e:
            import traceback
            results[L] = {
                "manifest_id": f"{L}_FAILED_Ω",
                "error": str(e)[:500],
                "traceback": traceback.format_exc()[-1000:],
            }

    return {
        "manifest_id": "PHASE3_P0_EXECUTE_Ω",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "ordre": "N°52-R13",
        "input_path": src,
        "input_size_bytes": Path(src).stat().st_size,
        "layers_executed": layers_to_run,
        "results": results,
        "derivatives_root": str(DERIVATIVES_OUTPUT_ROOT),
        "v30_lock": "INVIOLÉ",
    }


# ═════════════════════════════════════════════════════════════════════════
# ORDRE N°52-R8 · Orchestrateur pipeline complet 8 phases (Option δ)
# ═════════════════════════════════════════════════════════════════════════
@router.post("/diagnostic/pee-maj/r8-execute")
async def pee_maj_r8_execute(
    request: Request,
    force: Optional[str] = None,
    do_pull: Optional[str] = None,
    x_commandant_token: Optional[str] = Header(default=None, alias="X-Commandant-Token"),
) -> Dict[str, Any]:
    """ORDRE N°52-R8 · Démarre le pipeline R8 (8 phases) en background.

    · Idempotent : si déjà RUNNING, retourne 409 avec state courant.
    · Pour forcer un redémarrage (zombie override), ?force=true.
    · Par défaut, do_pull=false (pull B2 désactivé car phases 1-5 en
      STUB_READY). Activer ?do_pull=true si spécifications métier
      disponibles ET infrastructure stable.
    · L'exécution se fait dans un thread daemon ; poll via /r8-status.
    """
    _verify_token(x_commandant_token)
    from engines.v8_institutional.especes.pee_maj_r8_orchestrator_omega import (
        start_r8_background,
    )
    force_bool = (force or "").lower() in ("true", "1", "yes", "y")
    do_pull_bool = (do_pull or "").lower() in ("true", "1", "yes", "y")
    result = start_r8_background(force=force_bool, do_pull=do_pull_bool)
    if not result["ok"]:
        raise HTTPException(
            status_code=409,
            detail={
                "reason": result["reason"],
                "note": (
                    "Un run R8 est déjà en cours. Attendre la fin ou "
                    "poller /r8-status. Utiliser ?force=true pour "
                    "écraser (déconseillé)."),
                "current_state_summary": {
                    "run_id": result["current_state"].get("run_id"),
                    "status": result["current_state"].get("status"),
                    "started_at_utc": result["current_state"].get(
                        "started_at_utc"),
                },
            })
    return {
        "manifest_id": "PEE_MAJ_R8_EXECUTE_ACCEPTED",
        "doctrine": "BCE-4X_ULTIME_ABSOLU_ANTI_GÉNÉRIQUE_STRICT",
        "ordre": "N°52-R8",
        "option": "δ_HYBRIDE_α_β",
        **result,
        "poll_endpoint": "/api/v30/admin-premium/gis/diagnostic/pee-maj/r8-status",
        "note": (
            "Run démarré en background. Les phases 0/6/7/8 seront exécutées "
            "réellement ; les phases 1-5 seront STUB_READY (ANTI_GÉNÉRIQUE "
            "strict · spécifications métier à fournir). "
            + (
                "Pull B2 ACTIVÉ (~5-15 min · risque pod restart pendant pull)."
                if do_pull_bool else
                "Pull B2 DÉSACTIVÉ par défaut (source de vérité durable = B2). "
                "Activer via ?do_pull=true si infrastructure stable."
            )),
        "v30_lock": "INVIOLÉ",
    }


@router.get("/diagnostic/pee-maj/r8-status")
async def pee_maj_r8_status(
    x_commandant_token: Optional[str] = Header(default=None, alias="X-Commandant-Token"),
) -> Dict[str, Any]:
    """ORDRE N°52-R8 · Lit le state file live du pipeline R8."""
    _verify_token(x_commandant_token)
    from engines.v8_institutional.especes.pee_maj_r8_orchestrator_omega import (
        read_state, R8_STATE_PATH,
    )
    state = read_state()
    if not state:
        return {
            "manifest_id": "PEE_MAJ_R8_STATUS_Ω",
            "status": "NEVER_STARTED",
            "state_path": str(R8_STATE_PATH),
            "note": "Aucun run R8 encore démarré. POST /r8-execute pour lancer.",
        }
    # Retour compact (sans tracebacks)
    phases_compact = {}
    for pid, phase in (state.get("phases") or {}).items():
        phases_compact[pid] = {
            "status": phase.get("status"),
            "started_at_utc": phase.get("started_at_utc"),
            "completed_at_utc": phase.get("completed_at_utc"),
            "last_update_utc": phase.get("last_update_utc"),
            "pull_progress_pct": phase.get("pull_progress_pct"),
            "pull_bytes": phase.get("pull_bytes"),
            "results": {
                k: v for k, v in (phase.get("results") or {}).items()
                if k != "traceback"
            } if phase.get("results") else None,
        }
    return {
        "manifest_id": "PEE_MAJ_R8_STATUS_Ω",
        "run_id": state.get("run_id"),
        "status": state.get("status"),
        "started_at_utc": state.get("started_at_utc"),
        "completed_at_utc": state.get("completed_at_utc"),
        "last_update_utc": state.get("last_update_utc"),
        "total_elapsed_s": state.get("total_elapsed_s"),
        "ordre": state.get("ordre"),
        "option": state.get("option"),
        "phases": phases_compact,
        "global_error": state.get("global_error"),
        "state_path": str(R8_STATE_PATH),
        "v30_lock": "INVIOLÉ",
    }
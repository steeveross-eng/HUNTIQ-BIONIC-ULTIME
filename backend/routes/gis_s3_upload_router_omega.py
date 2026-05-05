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
import os
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import boto3
from botocore.client import Config
from botocore.exceptions import ClientError, EndpointConnectionError
from fastapi import APIRouter, File, Header, HTTPException, Request, UploadFile

from engines.v8_institutional.especes import gis_audit_log_omega as audit
from engines.v8_institutional.especes.gis_reception_validators_omega import (
    SLOT_BY_ID,
)

router = APIRouter(prefix="/api/v30/admin-premium/gis", tags=["gis-s3-b2"])

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
                detail=f"FILENAME_MISMATCH :: session={session['filename']} "
                       f"vs header={fname}")
        if int(session.get("chunks_total", 0)) != int(x_chunks_total):
            raise HTTPException(
                status_code=400,
                detail="CHUNKS_TOTAL_MISMATCH entre session et headers")

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
    except ClientError as e:
        raise HTTPException(status_code=502,
                              detail=f"B2_UPLOAD_PART_ERROR::{e}")
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
        return {
            "manifest_id": "CHUNK_S3_COMPLETED",
            "status": "COMPLETED",
            "slot_id": slot_id,
            "upload_id": x_upload_id,
            "b2_key": session["b2_key"],
            "b2_bucket": bucket,
            "final_size_bytes": final_size,
            "final_s3_etag": s3_etag,
            "parts_count": len(parts_list),
            "next_step": (
                f"POST /api/v30/admin-premium/gis/pee-maj/s3-finalize/"
                f"{x_upload_id} pour calculer SHA-256 composite + "
                "mettre à jour manifest LOADED."),
            "doctrine": "ANTI_GÉNÉRIQUE_STRICT",
        }

    progress_pct = round(
        (chunks_received_count / int(x_chunks_total)) * 100, 2)
    return {
        "manifest_id": "CHUNK_S3_STORED",
        "status": "CHUNK_STORED",
        "slot_id": slot_id,
        "upload_id": x_upload_id,
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
    """ORDRE N°52-EXT VOIE B · Post-upload, calcule SHA-256 streaming depuis
    B2, met à jour le manifest pour passer FORET_MFFP_PEE_MAJ_Ω à LOADED."""
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
    try:
        obj = s3.get_object(Bucket=bucket, Key=session["b2_key"])
    except ClientError as e:
        raise HTTPException(status_code=502,
                              detail=f"B2_GET_OBJECT_ERROR::{e}")

    # Stream SHA-256 direct depuis B2 (zéro disque local)
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

    # Mise à jour du manifest institutionnel
    manifest_path = Path("/app/backend/data/gis_operational/GIS_RECEPTION_INTAKE_Ω.json")
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception as e:
        raise HTTPException(status_code=500,
                              detail=f"MANIFEST_READ_ERROR::{e}")
    slot = manifest["slots"]["FORET_MFFP_PEE_MAJ_Ω"]
    slot["status"] = "LOADED"
    upload_entry = {
        "filename": session["filename"],
        "size_bytes": total_streamed,
        "sha256": sha256_global,
        "source": "BACKBLAZE_B2_MULTIPART",
        "b2_bucket": bucket,
        "b2_key": session["b2_key"],
        "b2_upload_id": session["b2_upload_id"],
        "uploaded_at_utc": session.get("completed_at_utc"),
        "validation_passed": True,
    }
    slot.setdefault("uploads", []).append(upload_entry)
    slot["files_loaded_count"] = len(slot["uploads"])
    slot["composite_sha256"] = hashlib.sha256(
        "\n".join(sorted(u["sha256"] for u in slot["uploads"]
                           if u.get("sha256"))).encode("utf-8")
    ).hexdigest()
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8")

    # Audit-event
    audit.append_event(
        event="PEE_MAJ_S3_FINALIZED_Ω",
        slot_id="FORET_MFFP_PEE_MAJ_Ω",
        filename=session["filename"],
        sha256=sha256_global, size_bytes=total_streamed,
        http_code=200,
        client_ip=request.client.host if request.client else "unknown",
        user_agent=(user_agent or "")[:200],
        validators=[
            {"name": "b2_stream_sha256", "passed": True,
             "elapsed_s": elapsed_s, "bytes_streamed": total_streamed},
            {"name": "manifest_updated", "passed": True,
             "composite_sha256": slot["composite_sha256"]},
        ],
    )

    return {
        "manifest_id": "PEE_MAJ_S3_FINALIZED_Ω",
        "doctrine": "ANTI_GÉNÉRIQUE_STRICT",
        "upload_id": upload_id,
        "b2_key": session["b2_key"],
        "b2_bucket": bucket,
        "sha256_global": sha256_global,
        "size_bytes": total_streamed,
        "stream_elapsed_s": elapsed_s,
        "slot_status": "LOADED",
        "composite_sha256": slot["composite_sha256"],
        "files_loaded_count": slot["files_loaded_count"],
        "note": (
            "pee_maj.gpkg est désormais persistant sur Backblaze B2. "
            "Le fichier brut est à l'abri du pod restart. Appeler ensuite "
            "/diagnostic/pee-maj/full-pipeline-execute pour déclencher "
            "compute + persist_derivatives + compress_and_archive."),
        "v30_lock": "INVIOLÉ",
    }


__all__ = ["router"]

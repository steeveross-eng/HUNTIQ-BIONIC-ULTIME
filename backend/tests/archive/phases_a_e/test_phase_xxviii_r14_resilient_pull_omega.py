"""
Phase XXVIII · ORDRE N°52-R14 — Tests anti-régressifs du pull résiliant B2
══════════════════════════════════════════════════════════════════════════
COMMANDANT STEEVE-MAX · BCE-4X ULTIME ABSOLU · ANTI_GÉNÉRIQUE_STRICT

Valide le module `mffp_resilient_pull_omega.py` conçu pour pull par
segments de 500 Mo (Range HTTP) afin de contourner les pod restarts à
9,44 Go observés sur les `get_object` monolithiques.

Tests :
  · API publique exportée + chemins attendus (/app vs /var/cache)
  · is_pee_maj_complete_and_valid() : 4 scénarios (absent/size/sha/ok)
  · start_resilient_pull() : idempotence (lock acquis)
  · start_resilient_pull() : détection zombie (age > 120s)
  · _execute_resilient_pull() : pull multi-segments E2E (mock S3 Range)
  · _execute_resilient_pull() : SHA-256 mismatch → FAILED
  · _execute_resilient_pull() : skip si fichier déjà complet
  · Reprise incrémentale : .partial non vide → start_offset > 0
"""
from __future__ import annotations

import hashlib
import importlib
import json
import re
import threading
import time
from datetime import datetime, timedelta, timezone
from io import BytesIO
from pathlib import Path
from unittest.mock import patch

import pytest


# ═════════════════════════════════════════════════════════════════════════
# Fixtures et mocks
# ═════════════════════════════════════════════════════════════════════════
@pytest.fixture()
def mod():
    """Charge fraîchement le module (force reload pour isoler le lock)."""
    import engines.v8_institutional.especes.mffp_resilient_pull_omega as m
    importlib.reload(m)
    return m


@pytest.fixture()
def sample_file(tmp_path):
    """Crée un fichier source déterministe de ~3 Mo (contenu pseudorandom)."""
    p = tmp_path / "source_pee_maj.gpkg"
    data = b""
    for i in range(3 * 1024):  # 3*1024 chunks de 1 Ko = 3 Mo
        data += (f"chunk_{i:08d}_" * 64)[:1024].encode("ascii")
    p.write_bytes(data)
    return {
        "path": p,
        "size": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
    }


class _MockBody:
    def __init__(self, data: bytes):
        self._buf = BytesIO(data)

    def read(self, n: int = -1) -> bytes:
        return self._buf.read(n)

    def close(self):
        pass


class _MockS3:
    """Simule boto3 S3 avec GetObject Range sur un fichier local.

    Utilisé uniquement pour la fonction generate_presigned_url
    (test compat avec ancienne API), le download réel passe par
    _download_segment_via_curl mocké séparément.
    """

    def __init__(self, source_path: Path):
        self.source_path = source_path
        self.get_object_calls: list = []

    def generate_presigned_url(self, op, Params, ExpiresIn):
        return f"https://fake.b2/test/{Params['Key']}?expires={ExpiresIn}"

    def get_object(self, *, Bucket: str, Key: str, Range: str):
        self.get_object_calls.append({"Bucket": Bucket, "Key": Key,
                                      "Range": Range})
        m = re.match(r"bytes=(\d+)-(\d+)", Range)
        start, end = int(m.group(1)), int(m.group(2))
        with open(self.source_path, "rb") as f:
            f.seek(start)
            data = f.read(end - start + 1)
        return {"Body": _MockBody(data), "ContentLength": len(data)}


def _make_curl_mock(sample_path):
    """Fabrique un mock de _download_segment_via_curl qui copie en
    pur Python un range du sample_file vers tmp_seg_path."""
    calls = []

    def _fake(presigned_url, start, end, tmp_seg_path, timeout_s=240):
        calls.append({"url": presigned_url, "start": start, "end": end,
                      "tmp": str(tmp_seg_path)})
        with open(sample_path, "rb") as f:
            f.seek(start)
            data = f.read(end - start + 1)
        Path(tmp_seg_path).parent.mkdir(parents=True, exist_ok=True)
        Path(tmp_seg_path).write_bytes(data)
        return len(data)

    _fake.calls = calls
    return _fake


@pytest.fixture()
def redirect_paths(mod, tmp_path, monkeypatch):
    """Redirige les chemins du module vers tmp_path."""
    state_path = tmp_path / "PULL_RESILIENT_STATE.json"
    local_dir = tmp_path / "incoming" / "FORET_MFFP_PEE_MAJ_Ω"
    local_dir.mkdir(parents=True, exist_ok=True)
    local_path = local_dir / "pee_maj.gpkg"
    partial_path = local_dir / "pee_maj.pulling.partial"
    monkeypatch.setattr(mod, "RESILIENT_STATE_PATH", state_path)
    monkeypatch.setattr(mod, "PEE_MAJ_LOCAL_DIR", local_dir)
    monkeypatch.setattr(mod, "PEE_MAJ_LOCAL_PATH", local_path)
    monkeypatch.setattr(mod, "PEE_MAJ_PARTIAL_PATH", partial_path)
    return {
        "state_path": state_path,
        "local_dir": local_dir,
        "local_path": local_path,
        "partial_path": partial_path,
    }


# ═════════════════════════════════════════════════════════════════════════
# 1. API publique
# ═════════════════════════════════════════════════════════════════════════
def test_resilient_pull_exports_public_api(mod):
    assert hasattr(mod, "start_resilient_pull")
    assert hasattr(mod, "read_resilient_state")
    assert hasattr(mod, "is_pee_maj_complete_and_valid")
    assert "start_resilient_pull" in mod.__all__
    assert "is_pee_maj_complete_and_valid" in mod.__all__


def test_resilient_pull_state_file_on_app_ext4(mod):
    """Le state file est sur /app persistant (pas /var/cache éphémère)."""
    assert str(mod.RESILIENT_STATE_PATH).startswith("/app/")


def test_resilient_pull_local_paths_on_var_cache(mod):
    """Le pull local est sur /var/cache (éphémère — doctrine documentée)."""
    assert str(mod.PEE_MAJ_LOCAL_PATH).startswith("/var/cache")
    assert str(mod.PEE_MAJ_PARTIAL_PATH).startswith("/var/cache")


def test_resilient_pull_segment_size_is_500mb(mod):
    """La taille de segment respecte la spécification (500 Mo)."""
    assert mod.SEGMENT_SIZE_BYTES == 500 * 1024 * 1024


# ═════════════════════════════════════════════════════════════════════════
# 2. is_pee_maj_complete_and_valid
# ═════════════════════════════════════════════════════════════════════════
def test_is_complete_file_absent(mod, redirect_paths):
    result = mod.is_pee_maj_complete_and_valid()
    assert result["complete"] is False
    assert result["reason"] == "FILE_ABSENT"


def test_is_complete_size_mismatch(mod, redirect_paths, sample_file,
                                    monkeypatch):
    redirect_paths["local_path"].write_bytes(b"x" * 10)
    monkeypatch.setattr(mod, "_get_pee_maj_b2_metadata", lambda: {
        "b2_bucket": "t", "b2_key": "k",
        "expected_sha256": "a" * 64,
        "expected_size_bytes": sample_file["size"],
    })
    result = mod.is_pee_maj_complete_and_valid()
    assert result["complete"] is False
    assert result["reason"] == "SIZE_MISMATCH"


def test_is_complete_sha_mismatch(mod, redirect_paths, sample_file,
                                   monkeypatch):
    data = sample_file["path"].read_bytes()
    redirect_paths["local_path"].write_bytes(data)
    monkeypatch.setattr(mod, "_get_pee_maj_b2_metadata", lambda: {
        "b2_bucket": "t", "b2_key": "k",
        "expected_sha256": "0" * 64,
        "expected_size_bytes": sample_file["size"],
    })
    result = mod.is_pee_maj_complete_and_valid()
    assert result["complete"] is False
    assert result["reason"] == "SHA256_MISMATCH"


def test_is_complete_ok(mod, redirect_paths, sample_file, monkeypatch):
    data = sample_file["path"].read_bytes()
    redirect_paths["local_path"].write_bytes(data)
    monkeypatch.setattr(mod, "_get_pee_maj_b2_metadata", lambda: {
        "b2_bucket": "t", "b2_key": "k",
        "expected_sha256": sample_file["sha256"],
        "expected_size_bytes": sample_file["size"],
    })
    result = mod.is_pee_maj_complete_and_valid()
    assert result["complete"] is True
    assert result["sha256"] == sample_file["sha256"]
    assert result["size_bytes"] == sample_file["size"]


# ═════════════════════════════════════════════════════════════════════════
# 3. start_resilient_pull - idempotence + zombie detection
# ═════════════════════════════════════════════════════════════════════════
def test_start_resilient_pull_idempotent_when_lock_held(
        mod, redirect_paths):
    """Si un run tourne (lock acquis + RUNNING frais), refuse."""
    mod._PULL_LOCK.acquire()
    try:
        mod._atomic_write_state({
            "status": "RUNNING",
            "last_update_utc": datetime.now(timezone.utc).isoformat(),
            "run_id": "prev_run",
        })
        result = mod.start_resilient_pull()
        assert result["ok"] is False
        assert result["reason"] == "ALREADY_RUNNING"
    finally:
        try:
            mod._PULL_LOCK.release()
        except RuntimeError:
            pass


def test_start_resilient_pull_zombie_detection(
        mod, redirect_paths, monkeypatch):
    """RUNNING + last_update > 120s → zombie détecté, nouveau run autorisé."""
    mod._PULL_LOCK.acquire()  # simule lock orphelin du thread mort
    # Injecte un state zombie DIRECTEMENT sur disque pour éviter que
    # _atomic_write_state n'écrase last_update_utc avec _utc_now().
    zombie_ts = (datetime.now(timezone.utc)
                 - timedelta(seconds=300)).isoformat()
    redirect_paths["state_path"].write_text(
        json.dumps({
            "status": "RUNNING",
            "last_update_utc": zombie_ts,
            "run_id": "zombie_run",
        }, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    # Mock threading.Thread pour ne pas exécuter réellement le pull
    started = {}

    class FakeThread:
        def __init__(self, target=None, args=(), name=None, daemon=None):
            started["target"] = target
            started["args"] = args

        def start(self):
            started["started"] = True

    monkeypatch.setattr(mod.threading, "Thread", FakeThread)
    result = mod.start_resilient_pull()
    assert result["ok"] is True
    assert result["previous_run_was_zombie"] is True
    assert result["status"] == "RUNNING"
    assert started.get("started") is True
    # cleanup lock pour les tests suivants
    try:
        mod._PULL_LOCK.release()
    except RuntimeError:
        pass


# ═════════════════════════════════════════════════════════════════════════
# 4. _execute_resilient_pull - pull E2E multisegment
# ═════════════════════════════════════════════════════════════════════════
def _build_meta_from_sample(sample_file):
    return {
        "b2_bucket": "test-bucket",
        "b2_key": "FORET_MFFP/pee_maj.gpkg",
        "expected_sha256": sample_file["sha256"],
        "expected_size_bytes": sample_file["size"],
    }


def test_execute_resilient_pull_multisegment_success(
        mod, redirect_paths, sample_file, monkeypatch):
    """Pull de 3 Mo par segments de 1 Mo → 3 segments → OK + SHA match.
    Mocke _download_segment_via_curl (bypass subprocess curl)."""
    monkeypatch.setattr(mod, "SEGMENT_SIZE_BYTES", 1 * 1024 * 1024)
    fake_curl = _make_curl_mock(sample_file["path"])
    monkeypatch.setattr(mod, "_download_segment_via_curl", fake_curl)
    monkeypatch.setattr(mod, "_generate_presigned_url",
                        lambda meta, expires_in_s=14400: "https://fake/url")
    monkeypatch.setattr(mod, "_get_pee_maj_b2_metadata",
                        lambda: _build_meta_from_sample(sample_file))

    mod._execute_resilient_pull("test_run_ok")

    state = mod.read_resilient_state()
    assert state["status"] == "OK", f"state={state}"
    assert state["sha256_computed"] == sample_file["sha256"]
    assert state["final_size_bytes"] == sample_file["size"]
    assert state["transport"] == "subprocess_curl_presigned_url"
    # Vérifier que le fichier final existe et le .partial a disparu
    assert redirect_paths["local_path"].exists()
    assert not redirect_paths["partial_path"].exists()
    # Vérifier SHA cross-check live
    h = hashlib.sha256()
    h.update(redirect_paths["local_path"].read_bytes())
    assert h.hexdigest() == sample_file["sha256"]
    # Vérifier que curl a bien été appelé 3 fois (3 Mo / 1 Mo segments)
    assert len(fake_curl.calls) == 3
    # Vérifier la cohérence des Ranges
    assert fake_curl.calls[0]["start"] == 0
    assert fake_curl.calls[-1]["end"] == sample_file["size"] - 1


def test_execute_resilient_pull_sha256_mismatch_fails(
        mod, redirect_paths, sample_file, monkeypatch):
    """Si SHA-256 calculé != attendu → status=FAILED."""
    monkeypatch.setattr(mod, "SEGMENT_SIZE_BYTES", 2 * 1024 * 1024)
    fake_curl = _make_curl_mock(sample_file["path"])
    monkeypatch.setattr(mod, "_download_segment_via_curl", fake_curl)
    monkeypatch.setattr(mod, "_generate_presigned_url",
                        lambda meta, expires_in_s=14400: "https://fake/url")
    # Meta avec mauvais SHA
    monkeypatch.setattr(mod, "_get_pee_maj_b2_metadata", lambda: {
        "b2_bucket": "t", "b2_key": "k",
        "expected_sha256": "0" * 64,
        "expected_size_bytes": sample_file["size"],
    })

    mod._execute_resilient_pull("test_run_sha_fail")

    state = mod.read_resilient_state()
    assert state["status"] == "FAILED"
    assert "SHA256_MISMATCH" in state.get("error", "")
    # Le .partial est laissé sur disque pour forensique
    assert redirect_paths["partial_path"].exists()
    # Le fichier final n'est PAS renommé
    assert not redirect_paths["local_path"].exists()


def test_execute_resilient_pull_skips_when_complete(
        mod, redirect_paths, sample_file, monkeypatch):
    """Si fichier local déjà complet + valide → OK_ALREADY_COMPLETE."""
    data = sample_file["path"].read_bytes()
    redirect_paths["local_path"].write_bytes(data)
    monkeypatch.setattr(mod, "_get_pee_maj_b2_metadata",
                        lambda: _build_meta_from_sample(sample_file))
    # Pas besoin de mock curl : on ne devrait pas y arriver

    mod._execute_resilient_pull("test_run_skip")

    state = mod.read_resilient_state()
    assert state["status"] == "OK_ALREADY_COMPLETE"
    assert "completed_at_utc" in state


def test_execute_resilient_pull_resumes_from_partial(
        mod, redirect_paths, sample_file, monkeypatch):
    """Si .partial déjà rempli à 50 %, reprend à l'offset correct."""
    monkeypatch.setattr(mod, "SEGMENT_SIZE_BYTES", 1 * 1024 * 1024)
    # Pré-remplissage du .partial avec les 1,5 premiers Mo
    data = sample_file["path"].read_bytes()
    prefix_size = int(sample_file["size"] * 0.5)
    redirect_paths["partial_path"].write_bytes(data[:prefix_size])

    fake_curl = _make_curl_mock(sample_file["path"])
    monkeypatch.setattr(mod, "_download_segment_via_curl", fake_curl)
    monkeypatch.setattr(mod, "_generate_presigned_url",
                        lambda meta, expires_in_s=14400: "https://fake/url")
    monkeypatch.setattr(mod, "_get_pee_maj_b2_metadata",
                        lambda: _build_meta_from_sample(sample_file))

    mod._execute_resilient_pull("test_run_resume")

    state = mod.read_resilient_state()
    assert state["status"] == "OK"
    assert state["start_offset"] == prefix_size
    # Le premier curl call doit démarrer à prefix_size (zéro redondance)
    assert fake_curl.calls[0]["start"] == prefix_size

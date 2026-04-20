"""
VISUAL-PROOF-LIVE-Ω — Capture DOM Leaflet réelle (Phase XI-SUPRA-C)
======================================================================
Utilise Playwright headless + Chromium pour capturer le rendu TERRITOIRE
réel de BionicLayersV8 aux 3 niveaux de zoom sous authentification
institutionnelle (steeve-max-capture@huntiq.com).

Endpoints :
  POST /api/v20/territoire/visual-proof-live/generate
  GET  /api/v20/territoire/visual-proof-live/index
"""
import hashlib
import hmac
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from fastapi import APIRouter

from engines.v8_institutional.engine_science_omega import register_engine, mark_call
from engines.v8_institutional.engine_render_omega import LAYERS_REQUIRED
from engines.v8_institutional.registry_lock_omega import get_registry_lock_status

register_engine(
    "VISUAL-PROOF-LIVE-Ω",
    "V1-PHASE-XI-SUPRA-C-2026-04",
    "Capture DOM Leaflet réelle via Playwright + auth institutionnelle",
    "GOUVERNANCE",
    [],
)

router = APIRouter(prefix="/api/v20/territoire", tags=["V20 Visual Proof LIVE"])

PROOF_DIR = Path("/app/memory/TERRITOIRE_VISUAL_PROOF_LIVE")
INDEX_PATH = PROOF_DIR / "TERRITOIRE_VISUAL_PROOF_LIVE_INDEX.json"
SIG_PATH = PROOF_DIR / "TERRITOIRE_VISUAL_PROOF_LIVE_SIGNATURES.md"
_SIGN_KEY = os.environ.get("EXPORT_SIGN_KEY", "BCE-4X-ULTIME-ABSOLU-STEEVE-MAX-V20").encode("utf-8")

LEVELS = [
    ("macro", 12, "TERRITOIRE_macro_live.png"),
    ("mid", 15, "TERRITOIRE_mid_live.png"),
    ("detail", 17, "TERRITOIRE_detail_live.png"),
]

CAPTURE_SCRIPT = Path("/app/backend/engines/v8_institutional/visual_proof_live_playwright.py")


def _run_playwright_capture(base_url: str) -> dict:
    """Lance le script Playwright en subprocess avec timeout 180s."""
    cmd = [sys.executable, str(CAPTURE_SCRIPT), "--base-url", base_url, "--output-dir", str(PROOF_DIR)]
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=240,
            env={**os.environ, "PYTHONUNBUFFERED": "1"},
        )
        return {
            "returncode": result.returncode,
            "stdout": result.stdout[-3000:],
            "stderr": result.stderr[-2000:],
        }
    except subprocess.TimeoutExpired:
        return {"returncode": -1, "stdout": "", "stderr": "TIMEOUT 240s"}


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _hmac(data: bytes) -> str:
    return hmac.new(_SIGN_KEY, data, hashlib.sha256).hexdigest()


def generate_live_proofs(force: bool = False, base_url: str | None = None) -> dict:
    mark_call("VISUAL-PROOF-LIVE-Ω")
    PROOF_DIR.mkdir(parents=True, exist_ok=True)

    # Idempotence 5 min
    if not force and INDEX_PATH.exists():
        try:
            cached = json.loads(INDEX_PATH.read_text())
            gen_at = datetime.fromisoformat(cached["generated_at"].replace("Z", "+00:00"))
            age = (datetime.now(timezone.utc) - gen_at).total_seconds()
            if age < 1800 and all(Path(c["path"]).exists() for c in cached["captures"]):
                return cached
        except Exception:
            pass

    # URL : interne d'abord (pas besoin d'ingress), sinon fallback REACT_APP_BACKEND_URL
    if not base_url:
        base_url = os.environ.get("PLAYWRIGHT_BASE_URL", "http://localhost:3000")

    run = _run_playwright_capture(base_url)

    lock = get_registry_lock_status()
    now = datetime.now(timezone.utc).isoformat()
    entries = []
    for level, zoom, filename in LEVELS:
        path = PROOF_DIR / filename
        if not path.exists():
            entries.append({
                "level": level, "zoom": zoom, "filename": filename,
                "path": str(path), "exists": False,
                "error": "Capture manquante (voir playwright_log)",
            })
            continue
        raw = path.read_bytes()
        sha = _sha256(raw)
        sig = _hmac(raw)
        layers_visible = []
        for layer in LAYERS_REQUIRED:
            if layer["zoom_min"] == 0:
                layers_visible.append(layer["id"])
            elif layer["zoom_min"] == 14 and level in ("mid", "detail"):
                layers_visible.append(layer["id"])
            elif layer["zoom_min"] == 16 and level == "detail":
                layers_visible.append(layer["id"])
        entries.append({
            "level": level, "zoom": zoom, "filename": filename,
            "path": str(path), "exists": True,
            "size_bytes": len(raw),
            "sha256": sha,
            "hmac_sha256": sig,
            "layers_visible": layers_visible,
            "layers_visible_count": len(layers_visible),
        })

    all_present = all(e.get("exists") for e in entries)
    index = {
        "generated_at": now,
        "engine_render_version": "V1-PHASE-XI-SUPRA-2026-04",
        "engine_visual_proof_live_version": "V1-PHASE-XI-SUPRA-C-2026-04",
        "bundle_version": "TERRITOIRE-V10-SUPRA",
        "frontend_version": "BionicLayersV8 + Phase XI-SUPRA extensions",
        "capture_user": "steeve-max-capture@huntiq.com",
        "registry_sha256": lock["sha256"],
        "document_maitre_sha256": lock["document_maitre"]["sha256"],
        "captures": entries,
        "total_captures": len(entries),
        "all_present": all_present,
        "algorithm": "HMAC-SHA256",
        "playwright_log": run,
    }
    INDEX_PATH.write_text(json.dumps(index, indent=2, ensure_ascii=False))

    lines = [
        "# TERRITOIRE_VISUAL_PROOF_LIVE_SIGNATURES",
        f"\n> **Statut :** SEALED · Phase XI-SUPRA-C",
        f"> **Horodatage UTC :** {now}",
        f"> **Capture user :** steeve-max-capture@huntiq.com",
        f"> **Algorithme :** HMAC-SHA256",
        f"> **Registry SHA-256 :** `{lock['sha256']}`",
        f"> **Document Maître SHA-256 :** `{lock['document_maitre']['sha256']}`",
        f"> **Playwright returncode :** {run['returncode']}",
        "",
        "## Captures DOM signées",
        "",
        "| Niveau | Zoom | Fichier | Taille | SHA-256 | HMAC-SHA256 |",
        "|--------|------|---------|--------|---------|-------------|",
    ]
    for e in entries:
        if e.get("exists"):
            lines.append(f"| {e['level']} | {e['zoom']} | `{e['filename']}` | {e['size_bytes']} B | `{e['sha256'][:32]}…` | `{e['hmac_sha256'][:32]}…` |")
        else:
            lines.append(f"| {e['level']} | {e['zoom']} | `{e['filename']}` | — | — | **MANQUANT** |")
    lines.append(f"\n```\nSEALED  — Phase XI-SUPRA-C — {now}\nALL_PRESENT = {all_present}\n```")
    SIG_PATH.write_text("\n".join(lines))
    return index


@router.post("/visual-proof-live/generate")
async def v20_visual_proof_live_generate(force: bool = False, base_url: str | None = None):
    """Lance Playwright pour capturer le rendu DOM TERRITOIRE réel."""
    return generate_live_proofs(force=force, base_url=base_url)


@router.get("/visual-proof-live/index")
async def v20_visual_proof_live_index():
    if not INDEX_PATH.exists():
        return {"error": "no proof generated", "hint": "POST /visual-proof-live/generate"}
    return json.loads(INDEX_PATH.read_text())

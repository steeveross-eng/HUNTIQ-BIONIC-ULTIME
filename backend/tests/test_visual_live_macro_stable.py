"""SELF-AUDIT-Ω — test_visual_live_macro_stable (Phase XI-SUPRA-D)
=====================================================================
Vérifie capture macro via route stable /territoire-capture-mode :
  - Fichier existe
  - Taille ≥ 30 KB (directive STEEVE-MAX non-négociable)
  - Manifest Playwright indique conforme_30kb=true et ready=true
"""
import json
import sys
from pathlib import Path

PROOF_DIR = Path("/app/memory/TERRITOIRE_VISUAL_PROOF_LIVE")
MANIFEST = PROOF_DIR / "playwright_capture_manifest.json"
LEVEL = "macro"
MIN_SIZE = 30 * 1024

errors = []
if not MANIFEST.exists():
    errors.append(f"manifest absent: {MANIFEST}")
else:
    data = json.loads(MANIFEST.read_text())
    cap = next((c for c in data.get("captures", []) if c.get("level") == LEVEL), None)
    if not cap:
        errors.append(f"capture {LEVEL} absente du manifest")
    else:
        path = PROOF_DIR / cap["filename"]
        if not path.exists():
            errors.append(f"fichier absent: {path}")
        else:
            size = path.stat().st_size
            if size < MIN_SIZE:
                errors.append(f"{LEVEL} size={size}B < 30KB (directive STEEVE-MAX)")
            if not cap.get("conforme_30kb"):
                errors.append(f"{LEVEL} conforme_30kb=False dans manifest")
            if not cap.get("ready"):
                errors.append(f"{LEVEL} window.__bionicReady != true (forced timeout)")

if errors:
    print("FAIL:")
    for e in errors: print(" -", e)
    sys.exit(1)
print(f"OK: capture {LEVEL} stable ≥ 30 KB avec __bionicReady confirmé")
sys.exit(0)

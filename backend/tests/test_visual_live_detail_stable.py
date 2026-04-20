"""SELF-AUDIT-Ω — test_visual_live_detail_stable (Phase XI-SUPRA-D)"""
import json, sys
from pathlib import Path
PROOF_DIR = Path("/app/memory/TERRITOIRE_VISUAL_PROOF_LIVE")
MANIFEST = PROOF_DIR / "playwright_capture_manifest.json"
LEVEL = "detail"; MIN_SIZE = 30 * 1024
errors = []
if not MANIFEST.exists():
    errors.append(f"manifest absent: {MANIFEST}")
else:
    data = json.loads(MANIFEST.read_text())
    cap = next((c for c in data.get("captures", []) if c.get("level") == LEVEL), None)
    if not cap: errors.append(f"capture {LEVEL} absente")
    else:
        path = PROOF_DIR / cap["filename"]
        if not path.exists(): errors.append(f"fichier absent: {path}")
        else:
            size = path.stat().st_size
            if size < MIN_SIZE: errors.append(f"{LEVEL} size={size}B < 30KB")
            if not cap.get("conforme_30kb"): errors.append(f"{LEVEL} conforme_30kb=False")
            if not cap.get("ready"): errors.append(f"{LEVEL} __bionicReady != true")
if errors:
    print("FAIL:"); [print(" -", e) for e in errors]; sys.exit(1)
print(f"OK: capture {LEVEL} stable ≥ 30 KB")
sys.exit(0)

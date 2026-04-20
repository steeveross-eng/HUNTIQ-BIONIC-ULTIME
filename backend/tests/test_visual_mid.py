"""SELF-AUDIT-Ω — test_visual_mid (Phase XI-SUPRA-B)"""
import hashlib
import hmac
import sys
from pathlib import Path
sys.path.insert(0, "/app/backend")

from engines.v8_institutional.visual_proof_omega import generate_visual_proofs, _SIGN_KEY  # noqa: E402

errors = []
idx = generate_visual_proofs()
mid = next((c for c in idx["captures"] if c["level"] == "mid"), None)
if not mid:
    errors.append("capture mid absente")
else:
    p = Path(mid["path"])
    if not p.exists():
        errors.append(f"fichier mid absent: {p}")
    else:
        raw = p.read_bytes()
        if hashlib.sha256(raw).hexdigest() != mid["sha256"]:
            errors.append("SHA-256 mid divergent")
        if hmac.new(_SIGN_KEY, raw, hashlib.sha256).hexdigest() != mid["hmac_sha256"]:
            errors.append("HMAC mid invalide")
    # mid inclut zoom 0 + zoom 14 couches (≥ 11)
    if mid["layers_visible_count"] < 11:
        errors.append(f"mid: < 11 couches visibles ({mid['layers_visible_count']})")

if errors:
    print("FAIL:"); [print(" -", e) for e in errors]; sys.exit(1)
print(f"OK: visual mid ({mid['size_bytes']}B, sha={mid['sha256'][:16]}…, {mid['layers_visible_count']} couches)")
sys.exit(0)

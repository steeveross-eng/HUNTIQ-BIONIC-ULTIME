"""SELF-AUDIT-Ω — test_visual_live_mid (Phase XI-SUPRA-C)"""
import hashlib
import hmac
import sys
from pathlib import Path
sys.path.insert(0, "/app/backend")

from engines.v8_institutional.visual_proof_live_omega import (  # noqa: E402
    generate_live_proofs, _SIGN_KEY,
)

errors = []
idx = generate_live_proofs()
mid = next((c for c in idx["captures"] if c["level"] == "mid"), None)
if not mid:
    errors.append("capture mid absente")
elif not mid.get("exists"):
    errors.append(f"fichier mid absent: {mid.get('error')}")
else:
    p = Path(mid["path"])
    raw = p.read_bytes()
    if hashlib.sha256(raw).hexdigest() != mid["sha256"]:
        errors.append("SHA-256 mid divergent")
    if hmac.new(_SIGN_KEY, raw, hashlib.sha256).hexdigest() != mid["hmac_sha256"]:
        errors.append("HMAC mid invalide")
    if mid["layers_visible_count"] < 11:
        errors.append(f"mid: couches visibles < 11 ({mid['layers_visible_count']})")

if errors:
    print("FAIL:"); [print(" -", e) for e in errors]; sys.exit(1)
print(f"OK: visual live mid ({mid['size_bytes']}B, sha={mid['sha256'][:16]}…, {mid['layers_visible_count']} couches)")
sys.exit(0)

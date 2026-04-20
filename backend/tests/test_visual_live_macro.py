"""SELF-AUDIT-Ω — test_visual_live_macro (Phase XI-SUPRA-C)"""
import hashlib
import hmac
import sys
from pathlib import Path
sys.path.insert(0, "/app/backend")

from engines.v8_institutional.visual_proof_live_omega import (  # noqa: E402
    generate_live_proofs, _SIGN_KEY, INDEX_PATH, PROOF_DIR,
)

errors = []
idx = generate_live_proofs()

macro = next((c for c in idx["captures"] if c["level"] == "macro"), None)
if not macro:
    errors.append("capture macro absente de l'index")
elif not macro.get("exists"):
    errors.append(f"fichier macro absent: {macro.get('error')}")
else:
    p = Path(macro["path"])
    raw = p.read_bytes()
    if hashlib.sha256(raw).hexdigest() != macro["sha256"]:
        errors.append("SHA-256 macro divergent")
    if hmac.new(_SIGN_KEY, raw, hashlib.sha256).hexdigest() != macro["hmac_sha256"]:
        errors.append("HMAC macro invalide")

# Au moins une capture doit être ≥ 30KB (preuve rendu Leaflet réel)
big = [c for c in idx["captures"] if c.get("exists") and c.get("size_bytes", 0) > 30000]
if not big:
    errors.append("aucune capture ≥ 30KB — rendu Leaflet non confirmé")

if errors:
    print("FAIL:"); [print(" -", e) for e in errors]; sys.exit(1)
print(f"OK: visual live macro présent, {len(big)}/3 capture(s) > 30KB confirment rendu Leaflet")
sys.exit(0)

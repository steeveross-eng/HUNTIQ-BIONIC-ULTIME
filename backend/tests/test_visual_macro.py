"""SELF-AUDIT-Ω — test_visual_macro (Phase XI-SUPRA-B)"""
import hashlib
import hmac
import json
import sys
from pathlib import Path
sys.path.insert(0, "/app/backend")

from engines.v8_institutional.visual_proof_omega import generate_visual_proofs, _SIGN_KEY  # noqa: E402

errors = []

# Déclenche la génération (idempotente)
idx = generate_visual_proofs()
macro = next((c for c in idx["captures"] if c["level"] == "macro"), None)
if not macro:
    errors.append("capture macro absente")
else:
    p = Path(macro["path"])
    if not p.exists():
        errors.append(f"fichier macro absent: {p}")
    else:
        raw = p.read_bytes()
        # Hash
        if hashlib.sha256(raw).hexdigest() != macro["sha256"]:
            errors.append("SHA-256 macro divergent")
        # Signature
        expected_sig = hmac.new(_SIGN_KEY, raw, hashlib.sha256).hexdigest()
        if expected_sig != macro["hmac_sha256"]:
            errors.append("HMAC macro invalide")
    # 14 couches visibles au niveau macro inclut zoom_min=0 (score_local, corridors, canada, contamination_v2, habitats_lep, zones_risque)
    if macro["layers_visible_count"] < 6:
        errors.append(f"macro: < 6 couches visibles ({macro['layers_visible_count']})")

if errors:
    print("FAIL:"); [print(" -", e) for e in errors]; sys.exit(1)
print(f"OK: visual macro ({macro['size_bytes']}B, sha={macro['sha256'][:16]}…, {macro['layers_visible_count']} couches)")
sys.exit(0)

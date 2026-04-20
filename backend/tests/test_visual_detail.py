"""SELF-AUDIT-Ω — test_visual_detail (Phase XI-SUPRA-B)
Niveau detail : DOIT contenir les 14 couches (macro + mid + detail).
"""
import hashlib
import hmac
import sys
from pathlib import Path
sys.path.insert(0, "/app/backend")

from engines.v8_institutional.visual_proof_omega import generate_visual_proofs, _SIGN_KEY  # noqa: E402

errors = []
idx = generate_visual_proofs()
det = next((c for c in idx["captures"] if c["level"] == "detail"), None)
if not det:
    errors.append("capture detail absente")
else:
    p = Path(det["path"])
    if not p.exists():
        errors.append(f"fichier detail absent: {p}")
    else:
        raw = p.read_bytes()
        if hashlib.sha256(raw).hexdigest() != det["sha256"]:
            errors.append("SHA-256 detail divergent")
        if hmac.new(_SIGN_KEY, raw, hashlib.sha256).hexdigest() != det["hmac_sha256"]:
            errors.append("HMAC detail invalide")
    # Detail doit montrer 14/14 couches
    if det["layers_visible_count"] != 14:
        errors.append(f"detail: couches != 14 ({det['layers_visible_count']})")

# Index présent + signatures MD
index_path = Path("/app/memory/TERRITOIRE_VISUAL_PROOF/TERRITOIRE_VISUAL_PROOF_INDEX.json")
sig_path = Path("/app/memory/TERRITOIRE_VISUAL_PROOF/TERRITOIRE_VISUAL_PROOF_SIGNATURES.md")
if not index_path.exists():
    errors.append("INDEX JSON manquant")
if not sig_path.exists():
    errors.append("SIGNATURES MD manquant")
if idx["total_captures"] != 3:
    errors.append(f"total_captures != 3 ({idx['total_captures']})")

if errors:
    print("FAIL:"); [print(" -", e) for e in errors]; sys.exit(1)
print(f"OK: visual detail ({det['size_bytes']}B, sha={det['sha256'][:16]}…, 14/14 couches)")
sys.exit(0)

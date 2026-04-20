"""SELF-AUDIT-Ω — test_visual_live_detail (Phase XI-SUPRA-C)"""
import hashlib
import hmac
import json
import sys
from pathlib import Path
sys.path.insert(0, "/app/backend")

from engines.v8_institutional.visual_proof_live_omega import (  # noqa: E402
    generate_live_proofs, _SIGN_KEY, INDEX_PATH, SIG_PATH,
)

errors = []
idx = generate_live_proofs()

det = next((c for c in idx["captures"] if c["level"] == "detail"), None)
if not det:
    errors.append("capture detail absente")
elif not det.get("exists"):
    errors.append(f"fichier detail absent: {det.get('error')}")
else:
    p = Path(det["path"])
    raw = p.read_bytes()
    if hashlib.sha256(raw).hexdigest() != det["sha256"]:
        errors.append("SHA-256 detail divergent")
    if hmac.new(_SIGN_KEY, raw, hashlib.sha256).hexdigest() != det["hmac_sha256"]:
        errors.append("HMAC detail invalide")
    if det["layers_visible_count"] != 14:
        errors.append(f"detail: couches visibles != 14 ({det['layers_visible_count']})")

# Fichiers obligatoires
if not INDEX_PATH.exists():
    errors.append("INDEX JSON manquant")
if not SIG_PATH.exists():
    errors.append("SIGNATURES MD manquant")
if idx["total_captures"] != 3:
    errors.append(f"total_captures != 3 ({idx['total_captures']})")
# Métadonnées institutionnelles
for k in ("engine_render_version", "capture_user", "registry_sha256", "document_maitre_sha256"):
    if k not in idx:
        errors.append(f"INDEX manque champ: {k}")
if idx.get("capture_user") != "steeve-max-capture@huntiq.com":
    errors.append(f"capture_user incorrect")

if errors:
    print("FAIL:"); [print(" -", e) for e in errors]; sys.exit(1)
print(f"OK: visual live detail ({det['size_bytes']}B, 14/14 couches, capture_user={idx['capture_user']})")
sys.exit(0)

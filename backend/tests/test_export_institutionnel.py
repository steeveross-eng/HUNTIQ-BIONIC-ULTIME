"""SELF-AUDIT-Ω — test_export_institutionnel (Phase X-D)
Vérifie génération PDF signé HMAC-SHA256.
"""
import sys
sys.path.insert(0, "/app/backend")

from engines.v8_institutional.export_institutionnel_v20_omega import _build_pdf  # noqa: E402

errors = []

pdf_bytes, meta = _build_pdf()

if not pdf_bytes.startswith(b"%PDF"):
    errors.append("PDF header invalide")

if len(pdf_bytes) < 2000:
    errors.append(f"PDF trop petit ({len(pdf_bytes)} bytes)")

for k in ("generated_at", "signature_hmac_sha256", "payload_signed",
          "reports_included", "registry_sha256", "document_maitre_sha256", "algorithm"):
    if k not in meta:
        errors.append(f"metadata manque champ: {k}")

if meta.get("algorithm") != "HMAC-SHA256":
    errors.append("algorithme != HMAC-SHA256")

if len(meta.get("signature_hmac_sha256", "")) != 64:
    errors.append(f"signature longueur != 64 hex ({len(meta.get('signature_hmac_sha256', ''))})")

if len(meta.get("reports_included", [])) < 3:
    errors.append(f"rapports inclus < 3 ({len(meta.get('reports_included',[]))})")

# Deterministic signature check
from engines.v8_institutional.export_institutionnel_v20_omega import _build_signature
expected = _build_signature(meta["payload_signed"].encode("utf-8"))
if expected != meta["signature_hmac_sha256"]:
    errors.append("signature non reproductible")

if errors:
    print("FAIL:"); [print(" -", e) for e in errors]; sys.exit(1)
print(f"OK: export PDF institutionnel ({len(pdf_bytes)} bytes, sig={meta['signature_hmac_sha256'][:16]}…, {len(meta['reports_included'])} rapports)")
sys.exit(0)

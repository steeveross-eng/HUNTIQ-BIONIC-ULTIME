"""
SELF-AUDIT-Ω — test_document_maitre_locked (Phase XI)
=======================================================
Vérifie :
  - Document Maître existe
  - Hash SHA-256 stable
  - Fichier DOCUMENT_MAITRE_LOCKED.md présent + référence le hash courant
"""
import hashlib
import sys
from pathlib import Path

DOC = Path("/app/memory/DOCUMENT_MAITRE_ULTIME_MAX.md")
LOCK = Path("/app/memory/DOCUMENT_MAITRE_LOCKED.md")

errors = []

if not DOC.exists():
    errors.append(f"Document Maître manquant: {DOC}")
else:
    sha = hashlib.sha256(DOC.read_bytes()).hexdigest()
    if not LOCK.exists():
        errors.append(f"Lock file manquant: {LOCK}")
    else:
        lock_src = LOCK.read_text(encoding="utf-8")
        if sha not in lock_src:
            errors.append(f"Hash SHA-256 absent de {LOCK.name} — hash courant={sha[:16]}…")
        if "SEALED" not in lock_src.upper() and "SCELLÉ" not in lock_src.upper() and "VERROUILLÉ" not in lock_src.upper():
            errors.append(f"{LOCK.name} ne contient pas de marqueur SEALED/SCELLÉ/VERROUILLÉ")

if errors:
    print("FAIL: Document Maître non conforme:")
    for e in errors:
        print(f"  - {e}")
    sys.exit(1)

print(f"OK: Document Maître verrouillé (sha256={sha[:16]}…)")
sys.exit(0)

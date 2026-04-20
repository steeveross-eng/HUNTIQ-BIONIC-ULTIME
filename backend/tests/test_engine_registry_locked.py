"""
SELF-AUDIT-Ω — test_engine_registry_locked (Phase XI)
=======================================================
Vérifie :
  - Le registre scellé charge 22 engines SUPRA-Ω
  - Le hash SHA-256 du registre est stable
  - ENGINE_REGISTRY_LOCKED.md existe et reference le hash courant
"""
import sys
from pathlib import Path

sys.path.insert(0, "/app/backend")

from engines.v8_institutional.registry_lock_omega import (  # noqa: E402
    ENGINES_LOCKED, get_registry_lock_status,
)

REGISTRY_MD = Path("/app/memory/ENGINE_REGISTRY_LOCKED.md")

errors = []

if len(ENGINES_LOCKED) < 22:
    errors.append(f"Registre incomplet: {len(ENGINES_LOCKED)}/22")

status = get_registry_lock_status()
sha = status["sha256"]

if not REGISTRY_MD.exists():
    errors.append(f"Fichier registre scellé manquant: {REGISTRY_MD}")
else:
    md_src = REGISTRY_MD.read_text(encoding="utf-8")
    if sha not in md_src:
        errors.append(f"Hash SHA-256 absent de {REGISTRY_MD.name} (courant={sha[:16]}…)")
    if "SEALED" not in md_src.upper() and "SCELLÉ" not in md_src.upper() and "VERROUILLÉ" not in md_src.upper():
        errors.append(f"{REGISTRY_MD.name} ne contient pas de marqueur SEALED/SCELLÉ/VERROUILLÉ")

# Vérification structure pilier
pillars = {e["pillar"] for e in ENGINES_LOCKED}
expected = {"GOUVERNANCE", "BIO-SYSTEME", "COMPORTEMENT-HUMAIN", "SYSTEME-SENSORIEL", "ENVIRONNEMENT"}
missing_pillars = expected - pillars
if missing_pillars:
    errors.append(f"Piliers manquants: {missing_pillars}")

if errors:
    print("FAIL: Registry Lock non conforme:")
    for e in errors:
        print(f"  - {e}")
    sys.exit(1)

print(f"OK: Registry Lock scellé ({len(ENGINES_LOCKED)} engines, sha256={sha[:16]}…, piliers={len(pillars)})")
sys.exit(0)

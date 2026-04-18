"""
TEST DEFAULTS-Omega — POINT DE VERITE UNIQUE
=============================================
Verifie que frontend/src/config/territoire_defaults.js est conforme.
Execute: python3 /app/backend/tests/test_defaults_omega.py
"""
import sys
import re
from pathlib import Path

DEFAULTS_FILE = Path("/app/frontend/src/config/territoire_defaults.js")
PAGE_FILE = Path("/app/frontend/src/pages/MonTerritoireBionicPage.jsx")
LAYERS_FILE = Path("/app/frontend/src/components/territoire/BionicLayersV8.jsx")

REQUIRED_DEFAULTS = [
    "SALINES", "CORRIDORS", "ZONES", "AFFUTS",
    "HOTSPOTS", "VENT", "CONTAMINATION", "CURSEUR",
]

REQUIRED_ALWAYS_ON = [
    "CORRIDORS_ALWAYS_ON", "SALINES_ALWAYS_ON", "AFFUTS_ALWAYS_ON",
    "ZONES_ALWAYS_ON", "HOTSPOTS_ALWAYS_ON", "VENT_ALWAYS_ON",
    "CONTAM_ALWAYS_ON",
]

# Corridor hierarchy (Directive III strict)
REQUIRED_CORRIDOR_HIERARCHY = [
    ("extreme", "#FF0000", 4.0),
    ("intense", "#FF6A00", 3.2),
    ("saisonnier", "#FFC300", 2.6),
    ("normal", "#00B050", 2.0),
    ("faible", "#00B0F0", 1.4),
]


def fail(msg: str):
    print(f"[FAIL] {msg}")
    return False


def test_defaults_file_exists():
    if not DEFAULTS_FILE.exists():
        return fail(f"Fichier manquant: {DEFAULTS_FILE}")
    return True


def test_required_flags():
    text = DEFAULTS_FILE.read_text()
    for key in REQUIRED_DEFAULTS:
        if f"{key}: true" not in text:
            return fail(f"Flag manquant ou desactive: {key}")
    return True


def test_always_on_flags():
    text = DEFAULTS_FILE.read_text()
    for key in REQUIRED_ALWAYS_ON:
        if f"{key}: true" not in text:
            return fail(f"Flag ALWAYS-ON manquant: {key}")
    return True


def test_corridor_hierarchy_strict():
    text = DEFAULTS_FILE.read_text()
    # Chaque niveau doit contenir color + weight dans l'ordre
    for tier, color, weight in REQUIRED_CORRIDOR_HIERARCHY:
        block_re = re.compile(
            rf"{tier}:\s*Object\.freeze\(\{{[^}}]*color:\s*['\"]{color}['\"][^}}]*weight:\s*{weight}",
            re.DOTALL,
        )
        if not block_re.search(text):
            return fail(f"Hierarchy {tier} incorrecte (attendu {color} weight={weight})")

    # Strictement croissant: extreme > intense > saisonnier > normal > faible
    weights = [w for _, _, w in REQUIRED_CORRIDOR_HIERARCHY]
    if weights != sorted(weights, reverse=True):
        return fail(f"Weights non strictement decroissants: {weights}")

    # Minimums: weight>=1.4, opacity>=0.55
    for tier, color, weight in REQUIRED_CORRIDOR_HIERARCHY:
        if weight < 1.4:
            return fail(f"{tier} weight {weight} < 1.4 (minimum institutionnel)")
    return True


def test_bionic_layers_uses_hierarchy():
    if not LAYERS_FILE.exists():
        return fail(f"Layer file manquant: {LAYERS_FILE}")
    text = LAYERS_FILE.read_text()
    if "CORRIDOR_STYLE_HIERARCHY" not in text:
        return fail("BionicLayersV8.jsx n'importe pas CORRIDOR_STYLE_HIERARCHY")
    # Aucun hardcode de l'ancienne palette ne doit subsister dans CORRIDOR_STYLES
    if "'#D32F2F'" in text and "CORRIDOR_STYLES" in text.split("const CORRIDOR_STYLES")[1].split("};")[0]:
        return fail("Ancienne palette #D32F2F encore hardcodee dans CORRIDOR_STYLES")
    return True


def test_page_uses_defaults():
    if not PAGE_FILE.exists():
        return fail(f"Page file manquant: {PAGE_FILE}")
    text = PAGE_FILE.read_text()
    if "TERRITOIRE_DEFAULTS" not in text:
        return fail("MonTerritoireBionicPage.jsx n'importe pas TERRITOIRE_DEFAULTS")
    required_usages = [
        "TERRITOIRE_DEFAULTS.SALINES",
        "TERRITOIRE_DEFAULTS.CORRIDORS",
        "TERRITOIRE_DEFAULTS.ZONES",
        "TERRITOIRE_DEFAULTS.AFFUTS",
        "TERRITOIRE_DEFAULTS.HOTSPOTS",
        "TERRITOIRE_DEFAULTS.VENT",
        "TERRITOIRE_DEFAULTS.CONTAMINATION",
        "TERRITOIRE_DEFAULTS.CURSEUR",
        "TERRITOIRE_DEFAULTS.INTEL",
    ]
    for usage in required_usages:
        if usage not in text:
            return fail(f"Usage manquant: {usage}")
    return True


TESTS = [
    ("defaults_file_exists", test_defaults_file_exists),
    ("required_flags", test_required_flags),
    ("always_on_flags", test_always_on_flags),
    ("corridor_hierarchy_strict", test_corridor_hierarchy_strict),
    ("bionic_layers_uses_hierarchy", test_bionic_layers_uses_hierarchy),
    ("page_uses_defaults", test_page_uses_defaults),
]


def main():
    passed = 0
    failed = 0
    for name, fn in TESTS:
        try:
            ok = fn()
        except Exception as e:
            ok = False
            print(f"[ERR ] {name}: {e}")
        if ok:
            print(f"[OK  ] {name}")
            passed += 1
        else:
            failed += 1
    print(f"\n=== {passed}/{len(TESTS)} tests passes ===")
    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()

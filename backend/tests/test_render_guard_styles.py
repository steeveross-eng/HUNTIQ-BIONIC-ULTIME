"""
RENDER-GUARD-Ω — Validation styles BionicLayersV8 vs directives V12-R5
=======================================================================
Verifie par inspection du code source que les styles respectent strictement
les directives V12-R5:
  - corridors: weight clamp [2.0, 4.0], opacity >= 0.75
  - contamination: fillColor #FF0000, fillOpacity 0.35-0.40, stroke #FF6A00 2.5px dashArray '6 4'
  - affuts: couleur orange #FF9800, contour blanc #FFFFFF 2px, pane 'markerPane'
  - salines: jaune #FDD835, distance_min_salines 120m
  - UX-Omega palette orange (rgba(255,152,0,0.4) fond actif)

Execute: python3 /app/backend/tests/test_render_guard_styles.py
"""
import sys
from pathlib import Path

BL = Path("/app/frontend/src/components/territoire/BionicLayersV8.jsx").read_text()
BTN = Path("/app/frontend/src/components/territoire/ui/BionicButtonOmega.jsx").read_text()
CSS = Path("/app/frontend/src/App.css").read_text()
TB = Path("/app/frontend/src/components/territoire/ui/TerritoireToolbar.jsx").read_text()


def must_contain(text, needle, label):
    if needle in text:
        print(f"[RENDER-GUARD-Ω OK] {label}")
        return None
    return f"ERREUR RENDU-Ω: {label} manquant ({needle[:60]})"


failures = []

# CORRIDORS V12-R5
failures.append(must_contain(BL, "Math.max(2.0, Math.min(4.0, style.weight))", "corridors weight clampe [2.0, 4.0]"))
failures.append(must_contain(BL, "Math.max(0.75, style.opacity)", "corridors opacity >= 0.75"))

# CONTAMINATION V12-R5 (Directive IV stricte)
failures.append(must_contain(BL, "'#FF0000'", "contamination fillColor #FF0000"))
failures.append(must_contain(BL, "'#FF6A00'", "contamination stroke #FF6A00"))
failures.append(must_contain(BL, "dashArray: '6 4'", "contamination dashArray '6 4'"))
failures.append(must_contain(BL, "weight: 2.5", "contamination strokeWidth 2.5"))

# AFFUTS V12-R5 (Directive II)
failures.append(must_contain(BL, "AFFUT_BIONIC_ORANGE = '#FF9800'", "affut orange BIONIC #FF9800"))
failures.append(must_contain(BL, "AFFUT_WHITE_STROKE = '#FFFFFF'", "affut contour blanc"))
failures.append(must_contain(BL, "pane: 'markerPane'", "affut z-index top (markerPane)"))

# SALINES V12-R5 (Directive III R5)
failures.append(must_contain(BL, "MIN_DIST = 120", "salines anti-grappes distance_min 120m"))
failures.append(must_contain(BL, "SALINE_COLOR", "salines jaune institutionnel SALINE_COLOR"))

# UX-Ω ORANGE (Directive V)
failures.append(must_contain(BTN, "rgba(255, 152, 0, 0.4)", "BionicButtonOmega fond orange 0.4"))
failures.append(must_contain(BTN, "0 0 4px #FF9800", "BionicButtonOmega halo 4px #FF9800"))
failures.append(must_contain(CSS, "rgba(255, 152, 0, 0.4)", "App.css .btn-omega-active orange"))
failures.append(must_contain(TB, "rgba(255, 152, 0, 0.4)", "TerritoireToolbar PressButton orange"))

failures = [f for f in failures if f]

if failures:
    print("\n=== RENDER-GUARD-Ω STYLES NON CONFORME ===")
    for f in failures:
        print(f)
    sys.exit(1)
print("\n=== RENDER-GUARD-Ω STYLES CONFORME ===")
sys.exit(0)

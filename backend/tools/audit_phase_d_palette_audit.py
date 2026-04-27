#!/usr/bin/env python3
"""
PHASE-D AUDIT VISUEL — Validation palette verte institutionnelle RENDUΩ
Captures HTTPS 1920×1080 sur 5 espèces (visualisation des corridors verts +
halos) + sonde DOM des paths SVG (palette appliquée).
"""
import asyncio, json
from pathlib import Path

OUT = Path("/app/frontend/public/reports/audit_territoire_omega_ultime/phase_d/captures")
OUT.mkdir(parents=True, exist_ok=True)
URL_BASE = "https://huntiq-restore.preview.emergentagent.com/territoire-capture-mode"
LAT, LON = 48.206657, -68.382422

SPECIES = [
    ("orignal", "PRESENT"),
    ("chevreuil", "PRESENT"),
    ("ours_noir", "PRESENT"),
    ("dindon_sauvage", "ABSENT"),
    ("wapiti", "ABSENT"),
]

JS_PROBE = """
(() => {
  function _normColor(s) {
    if (!s) return '';
    s = String(s).trim().toUpperCase();
    // RGB → HEX
    var m = s.match(/^RGB\\((\\d+),\\s*(\\d+),\\s*(\\d+)\\)$/);
    if (m) {
      var r = parseInt(m[1]).toString(16).padStart(2,'0');
      var g = parseInt(m[2]).toString(16).padStart(2,'0');
      var b = parseInt(m[3]).toString(16).padStart(2,'0');
      return ('#' + r + g + b).toUpperCase();
    }
    return s;
  }
  function _strokeOf(p) {
    var attr = p.getAttribute('stroke');
    if (attr && attr !== 'none') return _normColor(attr);
    var inline = p.style && p.style.stroke;
    if (inline) return _normColor(inline);
    var cs = getComputedStyle(p);
    return _normColor(cs.stroke);
  }
  var paths = Array.from(document.querySelectorAll('.leaflet-overlay-pane path'));
  var palette = {
    primary_00A676: 0, haloInner_4CC99A: 0, haloOuter_B2F2D9: 0,
    legacy_FF8F00: 0, other: 0, total: paths.length, samples: []
  };
  paths.forEach(function(p) {
    var s = _strokeOf(p);
    if (s === '#00A676') palette.primary_00A676++;
    else if (s === '#4CC99A') palette.haloInner_4CC99A++;
    else if (s === '#B2F2D9') palette.haloOuter_B2F2D9++;
    else if (s === '#FF8F00') palette.legacy_FF8F00++;
    else palette.other++;
    if (palette.samples.length < 8) palette.samples.push(s);
  });
  var x150 = window.__OMEGA_CORRIDORS_X150_PROBES__ || {};
  return { palette: palette, x150: x150,
           x150_conforme: window.__OMEGA_CORRIDORS_X150_CONFORME__,
           corridors_visible: window.__OMEGA_CORRIDORS_STYLE_CONFORME__ };
})()
"""


async def capture(p, species, expected, idx):
    browser = await p.chromium.launch(headless=True, args=["--no-sandbox"])
    ctx = await browser.new_context(viewport={"width": 1920, "height": 1080}, ignore_https_errors=True)
    page = await ctx.new_page()
    url = f"{URL_BASE}?lat={LAT}&lon={LON}&species={species}&zoom=13"
    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_timeout(15000)
        await page.screenshot(path=str(OUT / f"D_{idx:02d}_{species}_{expected}.jpeg"), quality=40)
        dom = await page.evaluate(JS_PROBE)
        print(f"[D] {species:18s} ({expected:7s}): palette={dom['palette']}  x150_conforme={dom['x150_conforme']}  visible={dom['corridors_visible']}")
        await browser.close()
        return {"species": species, "expected": expected, **dom}
    except Exception as e:
        print(f"[D] {species} ERR: {e}")
        try: await browser.close()
        except: pass
        return {"species": species, "expected": expected, "error": str(e)}


async def main():
    from playwright.async_api import async_playwright
    results = []
    async with async_playwright() as p:
        for i, (sp, st) in enumerate(SPECIES):
            r = await capture(p, sp, st, i+1)
            results.append(r)
    out_json = OUT.parent / "D_palette_audit.json"
    out_json.write_text(json.dumps(results, indent=2))
    print(f"\nWROTE {out_json}")


asyncio.run(main())

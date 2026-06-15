#!/usr/bin/env python3
"""PHASE-D AUDIT VISUEL via /mon-territoire-bionic (organic generate pipeline)."""
import asyncio, json
from pathlib import Path

OUT = Path("/app/frontend/public/reports/audit_territoire_omega_ultime/phase_d/captures")
OUT.mkdir(parents=True, exist_ok=True)
URL = "https://ultime-preview.preview.emergentagent.com/mon-territoire-bionic"

JS_PROBE = r"""
(() => {
  function _normColor(s) {
    if (!s) return '';
    s = String(s).trim().toUpperCase();
    var m = s.match(/^RGB\((\d+),\s*(\d+),\s*(\d+)\)$/);
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
  var pp = { primary_00A676: 0, haloInner_4CC99A: 0, haloOuter_B2F2D9: 0, legacy_FF8F00: 0, other: 0, total: paths.length, samples: [] };
  paths.forEach(function(p) {
    var s = _strokeOf(p);
    if (s === '#00A676') pp.primary_00A676++;
    else if (s === '#4CC99A') pp.haloInner_4CC99A++;
    else if (s === '#B2F2D9') pp.haloOuter_B2F2D9++;
    else if (s === '#FF8F00') pp.legacy_FF8F00++;
    else pp.other++;
    if (pp.samples.length < 12) pp.samples.push(s);
  });
  return { palette: pp,
           bundle_corridors_count: (window.__lastBundle?.corridors || []).length,
           x150_conforme: window.__OMEGA_CORRIDORS_X150_CONFORME__,
           visible: window.__OMEGA_CORRIDORS_STYLE_CONFORME__ };
})()
"""


async def main():
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=["--no-sandbox"])
        ctx = await browser.new_context(viewport={"width": 1920, "height": 1080}, ignore_https_errors=True)
        page = await ctx.new_page()
        await page.goto(URL, wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_timeout(2500)
        try:
            await page.get_by_text("Tout accepter").click(timeout=5000)
        except Exception: pass
        try:
            await page.wait_for_selector("[data-testid='v30-status-panel']", timeout=60000)
        except Exception: pass
        await page.wait_for_timeout(20000)
        await page.screenshot(path=str(OUT / "D_mon_territoire_bionic.jpeg"), quality=40)
        # Zoom on the corridor central area
        await page.screenshot(path=str(OUT / "D_mon_territoire_bionic_center.jpeg"), quality=50,
                              clip={"x": 700, "y": 350, "width": 700, "height": 500})
        dom = await page.evaluate(JS_PROBE)
        print(f"[D] /mon-territoire-bionic palette={dom['palette']}")
        print(f"    bundle_corridors_count={dom['bundle_corridors_count']}")
        print(f"    x150_conforme={dom['x150_conforme']}  visible={dom['visible']}")
        await browser.close()
        out_json = OUT.parent / "D_mon_territoire_palette.json"
        out_json.write_text(json.dumps(dom, indent=2))


asyncio.run(main())

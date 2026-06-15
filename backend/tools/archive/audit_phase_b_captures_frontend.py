#!/usr/bin/env python3
"""
PHASE-B.4 CAPTURES FRONTEND — 5 espèces sur la page TERRITOIRE
publique. READ-ONLY strict.
"""
import asyncio, json
from pathlib import Path

OUT = Path("/app/frontend/public/reports/audit_territoire_omega_ultime/phase_b/captures_frontend")
OUT.mkdir(parents=True, exist_ok=True)
URL_BASE = "https://bionic-ultime-1.preview.emergentagent.com/territoire-capture-mode"
LAT, LON = 48.206657, -68.382422

SPECIES = [
    ("orignal", "PRESENT"),
    ("chevreuil", "PRESENT"),  # cerf canonical
    ("ours_noir", "PRESENT"),
    ("dindon_sauvage", "ABSENT"),
    ("wapiti", "ABSENT"),
]


async def capture_species(p, species, expected, idx):
    browser = await p.chromium.launch(headless=True, args=["--no-sandbox"])
    ctx = await browser.new_context(viewport={"width": 1920, "height": 1080}, ignore_https_errors=True)
    page = await ctx.new_page()
    url = f"{URL_BASE}?lat={LAT}&lon={LON}&species={species}&zoom=13"
    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_timeout(12000)
        await page.screenshot(path=str(OUT / f"B4_{idx:02d}_{species}_{expected}.jpeg"), quality=40, full_page=False)
        # DOM probe specifically for paths SVG by category
        js = "(() => { var paths = Array.from(document.querySelectorAll('.leaflet-overlay-pane path')); var counts = { orange_corridor: 0, red_corridor: 0, blue: 0, green: 0, total: paths.length }; paths.forEach(function(p){ var s = (p.getAttribute('stroke') || '').toUpperCase(); if (s.indexOf('FF8') >= 0 || s.indexOf('FF9') >= 0) counts.orange_corridor++; if (s.indexOf('DC2') >= 0 || s.indexOf('EF4') >= 0 || s.indexOf('F87') >= 0) counts.red_corridor++; if (s.indexOf('1E') >= 0 || s.indexOf('1B') >= 0 || s.indexOf('2563') >= 0 || s.indexOf('3B82') >= 0) counts.blue++; if (s.indexOf('16A') >= 0 || s.indexOf('22C') >= 0) counts.green++; }); var markers = document.querySelectorAll('.leaflet-marker-icon').length; return { paths: counts, markers: markers }; })()"
        dom = await page.evaluate(js)
        print(f"  {species} ({expected}): paths={dom['paths']} markers={dom['markers']}")
        await browser.close()
        return {"species": species, "expected": expected, **dom}
    except Exception as e:
        print(f"  {species} ERR: {e}")
        try: await browser.close()
        except: pass
        return {"species": species, "expected": expected, "error": str(e)}


async def main():
    from playwright.async_api import async_playwright
    results = []
    async with async_playwright() as p:
        for i, (sp, st) in enumerate(SPECIES):
            r = await capture_species(p, sp, st, i+1)
            results.append(r)
    out_json = OUT.parent / "B4_frontend_captures_dom.json"
    out_json.write_text(json.dumps(results, indent=2))
    print(f"\nWROTE {out_json}")


asyncio.run(main())

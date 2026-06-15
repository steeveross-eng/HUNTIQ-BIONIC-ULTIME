#!/usr/bin/env python3
"""Capture post-stabilisation PHASE-A : panneau STATUT CORRIDORS Ω avec dindon/wapiti = ABSENT badge."""
import asyncio, json, time
from pathlib import Path

OUT = Path("/app/frontend/public/reports/audit_territoire_omega_ultime/phase_a")
URL = "https://bionic-ultime-1.preview.emergentagent.com/mon-territoire-bionic"


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
        await page.wait_for_timeout(15000)

        await page.screenshot(path=str(OUT / "A_POST_FIX_full.jpeg"), quality=35)
        await page.screenshot(path=str(OUT / "A_POST_FIX_left_panel.jpeg"), quality=45,
                              clip={"x": 0, "y": 200, "width": 360, "height": 750})
        print("[POST-FIX] 2 captures saved")

        # Test viewport 1280×600 pour vérifier le repositionnement WeatherPanel
        await ctx.close()
        ctx2 = await browser.new_context(viewport={"width": 1280, "height": 600}, ignore_https_errors=True)
        page2 = await ctx2.new_page()
        await page2.goto(URL, wait_until="domcontentloaded", timeout=60000)
        await page2.wait_for_timeout(2500)
        try:
            await page2.get_by_text("Tout accepter").click(timeout=5000)
        except Exception: pass
        await page2.wait_for_timeout(15000)
        await page2.screenshot(path=str(OUT / "A_POST_FIX_1280x600.jpeg"), quality=40)
        print("[POST-FIX] 1280x600 capture saved")

        js = "(() => { var el = document.querySelector('[data-testid=\"bce4x-weather-panel\"]'); if(!el) return {present:false}; var r=el.getBoundingClientRect(); var cs=getComputedStyle(el); return {present:true, rect:{x:Math.round(r.x), y:Math.round(r.y), w:Math.round(r.width), h:Math.round(r.height)}, top:cs.top, bottom:cs.bottom, repositioned:el.getAttribute('data-bce4x-repositioned-top')}; })()"
        weather_dom = await page2.evaluate(js)
        print("[POST-FIX] WeatherPanel @ 1280x600:", json.dumps(weather_dom, indent=2))
        (OUT / "A_POST_FIX_dom_state.json").write_text(json.dumps(weather_dom, indent=2))

        await browser.close()


asyncio.run(main())

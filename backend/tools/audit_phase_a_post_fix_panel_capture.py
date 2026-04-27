#!/usr/bin/env python3
"""Capture du panneau status complet (avec table espèces déroulée)."""
import asyncio
from pathlib import Path

OUT = Path("/app/frontend/public/reports/audit_territoire_omega_ultime/phase_a")


async def main():
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=["--no-sandbox"])
        ctx = await browser.new_context(viewport={"width": 1920, "height": 1400}, ignore_https_errors=True)
        page = await ctx.new_page()
        await page.goto("https://huntiq-restore.preview.emergentagent.com/mon-territoire-bionic", wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_timeout(2500)
        try:
            await page.get_by_text("Tout accepter").click(timeout=5000)
        except Exception: pass
        try:
            await page.wait_for_selector("[data-testid='v30-status-panel']", timeout=60000)
        except Exception: pass
        await page.wait_for_timeout(15000)

        # Capture full panel including all 5 species rows
        panel = await page.query_selector("[data-testid='v30-status-panel']")
        if panel:
            await panel.screenshot(path=str(OUT / "A_POST_FIX_status_panel_only.jpeg"), quality=70)
            print("[POST-FIX] panel screenshot saved")
        await page.screenshot(path=str(OUT / "A_POST_FIX_full_1920x1400.jpeg"), quality=35,
                              clip={"x": 0, "y": 200, "width": 360, "height": 1100})
        print("[POST-FIX] left panel zoom 1100h saved")

        # Extract DOM for table verification
        rows = await page.evaluate(
            "(() => Array.from(document.querySelectorAll('[data-testid^=\"v30-species-row-\"]'))"
            ".map(row => ({testid: row.getAttribute('data-testid'),"
            "cells: Array.from(row.querySelectorAll('td')).map(t => t.textContent.trim())})))()"
        )
        print("DOM table rows:")
        for r in rows: print(" ", r)

        await browser.close()


asyncio.run(main())

#!/usr/bin/env python3
"""
PHASE-A AUDIT — Capture massive en lecture seule du panel TERRITOIRE
réel pour reproduire et documenter les 4 ruptures critiques.
"""
import asyncio
import json
import os
import time
from pathlib import Path

OUT_DIR = Path("/app/frontend/public/reports/audit_territoire_omega_ultime/phase_a")
OUT_DIR.mkdir(parents=True, exist_ok=True)

URL = "https://huntiq-restore.preview.emergentagent.com/mon-territoire-bionic"

JS_PROBE = r"""
(() => {
  const tids = ['compass-omega-vent','bce4x-weather-panel','v30-status-panel'];
  const panels = tids.map(tid => {
    const el = document.querySelector('[data-testid="' + tid + '"]');
    if (!el) return { testid: tid, present: false };
    const r = el.getBoundingClientRect();
    const cs = getComputedStyle(el);
    return {
      testid: tid, present: true, visible: r.width > 0 && r.height > 0,
      rect: { x: Math.round(r.x), y: Math.round(r.y), w: Math.round(r.width), h: Math.round(r.height) },
      zIndex: cs.zIndex, position: cs.position, top: cs.top, right: cs.right, bottom: cs.bottom
    };
  });
  let overlap = null;
  if (panels[0].present && panels[1].present) {
    const a = panels[0].rect, b = panels[1].rect;
    const ox = Math.max(0, Math.min(a.x+a.w, b.x+b.w) - Math.max(a.x, b.x));
    const oy = Math.max(0, Math.min(a.y+a.h, b.y+b.h) - Math.max(a.y, b.y));
    overlap = { px_x: ox, px_y: oy, overlapping: ox > 0 && oy > 0 };
  }
  const tableRows = Array.from(document.querySelectorAll('[data-testid^="v30-species-row-"]')).map(row => ({
    testid: row.getAttribute('data-testid'),
    cells: Array.from(row.querySelectorAll('td')).map(td => td.textContent.trim()),
  }));
  const lp = document.querySelector('[data-testid="v30-layers-panel"]');
  const layersText = lp ? (lp.textContent || '').slice(0, 800) : null;
  const corridorsCount = document.querySelectorAll('.leaflet-overlay-pane path').length;
  const orangeOnMap = Array.from(document.querySelectorAll('.leaflet-overlay-pane path')).filter(p => {
    const s = (p.getAttribute('stroke') || '').toUpperCase();
    return s.indexOf('FF8') >= 0 || s.indexOf('FF9') >= 0;
  }).length;
  const v30score = (document.querySelector('[data-testid="v30-score-value"]') || {}).textContent || null;
  const v30label = (document.querySelector('[data-testid="v30-alignment-label"]') || {}).textContent || null;
  return {
    panels, overlap, tableRows, layersText,
    corridorsCountSvg: corridorsCount, orangeOnMap,
    v30_score: v30score, v30_label: v30label,
  };
})()
"""


async def main():
    from playwright.async_api import async_playwright
    requests_log, responses_log = [], []
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=["--no-sandbox"])
        ctx = await browser.new_context(viewport={"width": 1920, "height": 1080}, ignore_https_errors=True)
        page = await ctx.new_page()
        page.on("request", lambda req: requests_log.append({"url": req.url, "method": req.method, "ts": time.time()}))
        page.on("response", lambda res: responses_log.append({"url": res.url, "status": res.status, "ts": time.time()}))

        await page.goto(URL, wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_timeout(2500)
        try:
            await page.get_by_text("Tout accepter").click(timeout=5000)
            print("[PHASE-A] cookies accepted")
        except Exception:
            pass
        try:
            await page.wait_for_selector("[data-testid='v30-status-panel']", timeout=60000)
            print("[PHASE-A] status panel rendered")
        except Exception as e:
            print(f"[PHASE-A] status panel timeout: {e}")
        await page.wait_for_timeout(8000)

        # full + right + dindon close-up
        await page.screenshot(path=str(OUT_DIR / "A1_full_loaded.jpeg"), quality=35, full_page=False)
        await page.screenshot(path=str(OUT_DIR / "A1_right_panels.jpeg"), quality=45,
                              clip={"x": 1500, "y": 100, "width": 420, "height": 980})
        print("[PHASE-A] 2 captures saved")

        # network analysis
        api_logs = [r for r in responses_log if "/api/" in r["url"]]
        err_404 = [r for r in responses_log if r["status"] == 404]
        err_any = [r for r in responses_log if r["status"] >= 400]
        out_net = {
            "viewport": {"width": 1920, "height": 1080},
            "url": URL,
            "api_requests_total": len([r for r in requests_log if "/api/" in r["url"]]),
            "api_responses_total": len(api_logs),
            "api_errors_404_count": len(err_404),
            "api_errors_4xx_5xx_total_count": len(err_any),
            "404_endpoints_unique": sorted(list({r["url"].split("?")[0] for r in err_404})),
            "all_4xx_5xx_full": [{"url": r["url"], "status": r["status"]} for r in err_any[:80]],
            "v30_corridors_endpoint_responses": [{"url": r["url"], "status": r["status"]}
                                                 for r in api_logs if "/v30/corridors/" in r["url"]][:10],
            "v20_bundle_endpoint_responses": [{"url": r["url"], "status": r["status"]}
                                              for r in api_logs if "/v20/territoire/" in r["url"]][:10],
        }
        (OUT_DIR / "A2_network_log.json").write_text(json.dumps(out_net, indent=2))
        print(f"[PHASE-A] network: api_resp={len(api_logs)} 4xx_5xx={len(err_any)} 404={len(err_404)}")

        # DOM probe
        dom = await page.evaluate(JS_PROBE)
        (OUT_DIR / "A3_dom_probe.json").write_text(json.dumps(dom, indent=2, ensure_ascii=False))
        print(f"[PHASE-A] DOM probe saved. corridorsCountSvg={dom.get('corridorsCountSvg')} orangeOnMap={dom.get('orangeOnMap')}")
        print(f"[PHASE-A] tableRows={len(dom.get('tableRows', []))}")
        for r in dom.get("tableRows", []):
            print(f"  ROW {r['testid']}: {r['cells']}")
        print(f"[PHASE-A] layersText excerpt: {(dom.get('layersText') or '')[:300]}")
        print(f"[PHASE-A] v30_score={dom.get('v30_score')}  v30_label={dom.get('v30_label')}")
        ovl = dom.get("overlap")
        print(f"[PHASE-A] panel overlap: {ovl}")

        # SECOND wave: check disparition corridors after long wait (60s+ for TTL)
        await page.wait_for_timeout(15000)
        await page.screenshot(path=str(OUT_DIR / "A1_after_15s.jpeg"), quality=30, full_page=False)
        print("[PHASE-A] after 15s capture")

        await browser.close()


asyncio.run(main())

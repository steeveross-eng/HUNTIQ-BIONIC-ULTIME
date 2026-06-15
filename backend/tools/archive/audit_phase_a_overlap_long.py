#!/usr/bin/env python3
"""
PHASE-A AUDIT (suite) — Tests à viewports réduits pour reproduire la
superposition VENT/METEO observée par le Commandant + diagnostic 404 + 
mesure de la désynchronisation panneau↔carte.
"""
import asyncio
import json
import time
from pathlib import Path

OUT_DIR = Path("/app/frontend/public/reports/audit_territoire_omega_ultime/phase_a")
OUT_DIR.mkdir(parents=True, exist_ok=True)
URL = "https://ultime-preview.preview.emergentagent.com/mon-territoire-bionic"

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
      zIndex: cs.zIndex
    };
  });
  let overlap = null;
  if (panels[0].present && panels[1].present) {
    const a = panels[0].rect, b = panels[1].rect;
    const ox = Math.max(0, Math.min(a.x+a.w, b.x+b.w) - Math.max(a.x, b.x));
    const oy = Math.max(0, Math.min(a.y+a.h, b.y+b.h) - Math.max(a.y, b.y));
    overlap = { px_x: ox, px_y: oy, overlapping: ox > 0 && oy > 0 };
  }
  return { panels, overlap };
})()
"""


async def viewport_test(p, w, h, label):
    requests_log, responses_log = [], []
    ctx = await p.chromium.launch(headless=True, args=["--no-sandbox"])
    page_ctx = await ctx.new_context(viewport={"width": w, "height": h}, ignore_https_errors=True)
    page = await page_ctx.new_page()
    page.on("response", lambda res: responses_log.append({"url": res.url, "status": res.status}))
    await page.goto(URL, wait_until="domcontentloaded", timeout=60000)
    await page.wait_for_timeout(2500)
    try:
        await page.get_by_text("Tout accepter").click(timeout=5000)
    except Exception:
        pass
    try:
        await page.wait_for_selector("[data-testid='v30-status-panel']", timeout=45000)
    except Exception:
        pass
    await page.wait_for_timeout(7000)
    await page.screenshot(path=str(OUT_DIR / f"A_overlap_{label}.jpeg"), quality=40)
    dom = await page.evaluate(JS_PROBE)
    err_4xx = [r for r in responses_log if r["status"] >= 400]
    err_404 = [r for r in responses_log if r["status"] == 404]
    print(f"\n=== Viewport {w}x{h} ({label}) ===")
    print(json.dumps(dom, indent=2))
    print(f"  4xx={len(err_4xx)}  404={len(err_404)}")
    await ctx.close()
    return {"viewport": [w, h], "label": label, "dom": dom, "err_404": len(err_404), "err_4xx_5xx": len(err_4xx)}


async def long_wait_disparition_test(p):
    """Test la disparition corridors après long wait (TTL)."""
    requests_log, responses_log = [], []
    ctx = await p.chromium.launch(headless=True, args=["--no-sandbox"])
    page_ctx = await ctx.new_context(viewport={"width": 1920, "height": 1080}, ignore_https_errors=True)
    page = await page_ctx.new_page()
    page.on("request", lambda req: requests_log.append({"url": req.url, "method": req.method, "ts": time.time()}))
    page.on("response", lambda res: responses_log.append({"url": res.url, "status": res.status, "ts": time.time()}))
    
    await page.goto(URL, wait_until="domcontentloaded", timeout=60000)
    await page.wait_for_timeout(2500)
    try:
        await page.get_by_text("Tout accepter").click(timeout=5000)
    except Exception:
        pass
    try:
        await page.wait_for_selector("[data-testid='v30-status-panel']", timeout=45000)
    except Exception:
        pass
    
    # Wait for full load
    await page.wait_for_timeout(8000)
    t1 = time.time()
    await page.screenshot(path=str(OUT_DIR / "A_disparition_t0.jpeg"), quality=40)
    
    # Wait 70s (panel refresh = 60s)
    await page.wait_for_timeout(70000)
    t2 = time.time()
    await page.screenshot(path=str(OUT_DIR / "A_disparition_t70.jpeg"), quality=40)
    
    # Filter requests in interval [t1, t2]
    err_during = [r for r in responses_log if r["ts"] >= t1 and r["status"] >= 400]
    refresh_calls = [r for r in responses_log if r["ts"] >= t1 and "/api/v30/corridors" in r["url"]]
    
    out = {
        "duration_s": int(t2 - t1),
        "errors_during_disparition": [{"url": r["url"][:200], "status": r["status"]} for r in err_during[:30]],
        "v30_refresh_calls": [{"url": r["url"][:200], "status": r["status"]} for r in refresh_calls[:20]],
    }
    print("\n=== Long Wait Disparition Test ===")
    print(json.dumps(out, indent=2))
    (OUT_DIR / "A4_long_wait_disparition.json").write_text(json.dumps(out, indent=2))
    await ctx.close()
    return out


async def main():
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        # Test multiple viewports for overlap
        results = {}
        for w, h, label in [(1920, 1080, "1920x1080"), (1366, 768, "1366x768"), (1440, 720, "1440x720"), (1280, 600, "1280x600")]:
            r = await viewport_test(p, w, h, label)
            results[label] = r
        
        (OUT_DIR / "A5_overlap_matrix.json").write_text(json.dumps(results, indent=2))
        print("\n=== A5 OVERLAP MATRIX SAVED ===")
        for k, v in results.items():
            ov = (v.get("dom") or {}).get("overlap")
            print(f"  {k}: overlap={ov}")
        
        # Long-wait test only at 1920x1080
        await long_wait_disparition_test(p)


asyncio.run(main())

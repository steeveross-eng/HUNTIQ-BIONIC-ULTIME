"""
Playwright capture script — Phase XI-SUPRA-D
==============================================
Capture DOM TERRITOIRE institutionnelle aux 3 niveaux de zoom
via la route stable /territoire-capture-mode (StrictMode off).

Stratégie :
  - Pré-inject token d'auth (localStorage) via context.add_init_script
  - page.goto /territoire-capture-mode?lat=..&lon=..&species=..&zoom=..
  - wait_for_function("window.__bionicReady === true")
  - page.screenshot → PNG ≥ 30 KB obligatoire
"""
import argparse
import json
import os
from pathlib import Path

from playwright.sync_api import sync_playwright

EMAIL = os.environ.get("CAPTURE_EMAIL", "steeve-max-capture@huntiq.com")
PASSWORD = os.environ.get("CAPTURE_PASSWORD", "CaptureOps2026#")
API_URL = os.environ.get("REACT_APP_BACKEND_URL") or "http://localhost:8001"

LEVELS = [
    ("macro", 12, "TERRITOIRE_macro_live.png"),
    ("mid", 15, "TERRITOIRE_mid_live.png"),
    ("detail", 17, "TERRITOIRE_detail_live.png"),
]

LAT = 45.10
LON = -72.80
MIN_SIZE_BYTES = 30 * 1024  # 30 KB strict non-négociable (directive STEEVE-MAX)


def _auth_token() -> tuple[str, dict]:
    import urllib.request
    req = urllib.request.Request(
        f"{API_URL}/api/auth/login",
        data=json.dumps({"email": EMAIL, "password": PASSWORD}).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=20) as r:
        auth = json.loads(r.read())
    return auth.get("token", ""), auth.get("user", {})


def run(base_url: str, output_dir: Path):
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"[CAPTURE-D] base_url={base_url} output_dir={output_dir} api={API_URL}")

    token, user = _auth_token()
    print(f"[AUTH] OK token={token[:24]}… role={user.get('role')}")

    results = []
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--hide-scrollbars",
                "--force-device-scale-factor=1",
                "--enable-webgl",
                "--use-gl=swiftshader",
                "--enable-accelerated-2d-canvas",
            ],
        )
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            ignore_https_errors=True,
            device_scale_factor=1,
        )
        # Phase XI-SUPRA-D : bloquer HMR websocket + sockjs + EventSource
        # (empêche les reloads HMR qui invalident le DOM pendant la capture)
        context.route("**/*sockjs*", lambda r: r.abort())
        context.route("**/*hot-update*", lambda r: r.abort())
        context.route("**/ws**", lambda r: r.abort() if r.request.resource_type == "websocket" else r.continue_())
        context.add_init_script(f"""
          (() => {{
            try {{
              const token = {json.dumps(token)};
              const user = {json.dumps(json.dumps(user))};
              ['auth_token','token','hunter_token'].forEach(k => localStorage.setItem(k, token));
              ['user','hq_user','huntiq_user'].forEach(k => localStorage.setItem(k, user));
              localStorage.setItem('isAuthenticated', 'true');
              // Phase XI-SUPRA-D : pré-accepter le consentement cookie institutionnel
              // pour éliminer l'overlay CookieConsent qui recouvre tout le viewport.
              localStorage.setItem('bionic_cookie_consent', JSON.stringify({{
                accepted: true,
                preferences: {{ analytics: true, marketing: true, functional: true }},
                timestamp: new Date().toISOString(),
                version: '1.0',
              }}));
            }} catch (e) {{}}
          }})();
        """)

        # Phase XI-SUPRA-D : page de chauffe (warm-up) — permet à HMR/dev-server
        # de se connecter et au bundle JS d'être cache avant les 3 captures réelles.
        warm = context.new_page()
        try:
            warm.goto(f"{base_url}/territoire-capture-mode?lat={LAT}&lon={LON}&species=chevreuil&zoom=14",
                      timeout=60000, wait_until="domcontentloaded")
            warm.wait_for_timeout(12000)
        except Exception as e:
            print(f"[CAPTURE-D]  warm-up skip: {e}")
        warm.close()

        for level, zoom, filename in LEVELS:
            print(f"[CAPTURE-D] level={level} zoom={zoom}")

            # Retry jusqu'à 3 fois en cas de "navigation during evaluate" (HMR initial)
            captured = False
            attempts = 0
            while not captured and attempts < 3:
                attempts += 1
                page = context.new_page()
                url = (
                    f"{base_url}/territoire-capture-mode"
                    f"?lat={LAT}&lon={LON}&species=chevreuil&zoom={zoom}"
                )
                try:
                    page.goto(url, timeout=90000, wait_until="domcontentloaded")
                except Exception as e:
                    print(f"[CAPTURE-D]  goto failed: {e}")
                    page.close(); continue

                # Settle HMR on first navigation : wait for networkidle or timeout
                try:
                    page.wait_for_load_state("networkidle", timeout=20000)
                except Exception:
                    pass

            # Attendre d'abord le montage de leaflet-container (max 60s)
            try:
                page.wait_for_selector(".leaflet-container", state="attached", timeout=60000)
            except Exception:
                pass

            # Attendre que les tuiles commencent à charger
            try:
                page.wait_for_function(
                    "() => document.querySelectorAll('.leaflet-tile-loaded').length >= 1",
                    timeout=60000,
                )
            except Exception as e:
                print(f"[CAPTURE-D]  wait tiles>=1 timeout: {e}")

            ready = False
            try:
                page.wait_for_function(
                    "() => window.__bionicReady === true",
                    timeout=90000,
                )
                ready = True
            except Exception as e:
                print(f"[CAPTURE-D]  wait_for_function timeout: {e}")

            # Stabilisation : force setView + invalidateSize, fermer popups
            try:
                page.evaluate(
                    f"""() => {{
                       const m = window.__bionicMap;
                       if (m) {{
                         try {{ m.closePopup(); }} catch(e){{}}
                         m.setView([{LAT}, {LON}], {zoom}, {{animate:false}});
                         m.invalidateSize();
                       }}
                       // Masquer overlays UI non-carte qui recouvrent le viewport
                       document.querySelectorAll(
                         '[role="dialog"], .modal-backdrop, .overlay-full, ' +
                         '[data-sonner-toaster], [class*="cookie" i], [class*="consent" i], ' +
                         '[id*="cookie" i]'
                       ).forEach(el => {{
                         try {{ el.style.display = 'none'; }} catch(e){{}}
                       }});
                    }}"""
                )
            except Exception:
                pass

            # Attente additionnelle pour tuiles + couches
            page.wait_for_timeout(3500)

            # Post-setView: attendre que les NOUVELLES tuiles arrivent
            # après changement de centre/zoom (reset + attente)
            try:
                page.wait_for_function(
                    "() => document.querySelectorAll('.leaflet-tile-loaded').length >= 6",
                    timeout=30000,
                )
            except Exception as e:
                print(f"[CAPTURE-D]  wait tiles>=6 post-setView: {e}")
            page.wait_for_timeout(1500)

            # Diagnostic final
            diag = {}
            try:
                diag = page.evaluate(
                    """() => ({
                         ready: !!window.__bionicReady,
                         meta: window.__bionicReadyMeta || null,
                         tiles: document.querySelectorAll('.leaflet-tile-loaded').length,
                         overlays: document.querySelectorAll('.leaflet-overlay-pane path').length,
                         markers: document.querySelectorAll('.leaflet-marker-icon').length,
                         layers_count: (() => {
                            const m = window.__bionicMap;
                            if (!m) return 0;
                            let n = 0; m.eachLayer(() => n += 1); return n;
                         })(),
                         viewport: { w: window.innerWidth, h: window.innerHeight },
                    })"""
                )
            except Exception as e:
                print(f"[CAPTURE-D]  diag err {e}")

            path = output_dir / filename
            try:
                page.screenshot(path=str(path), full_page=False, type="png")
            except Exception as e:
                print(f"[CAPTURE-D]  screenshot err {e}")

            size = path.stat().st_size if path.exists() else 0
            ok = size >= MIN_SIZE_BYTES
            print(
                f"[CAPTURE-D] {level} attempt={attempts} size={size}B ready={ready} "
                f"tiles={diag.get('tiles')} overlays={diag.get('overlays')} "
                f"layers={diag.get('layers_count')} → {'OK' if ok else 'FAIL(<30KB)'}"
            )
            page.close()
            if ok:
                results.append({
                    "level": level, "zoom": zoom, "filename": filename,
                    "size_bytes": size, "conforme_30kb": ok, "ready": ready,
                    "diag": diag, "attempts": attempts,
                })
                captured = True

        if not captured:
            # Consigne la dernière tentative pour manifest
            results.append({
                "level": level, "zoom": zoom, "filename": filename,
                "size_bytes": size, "conforme_30kb": False, "ready": ready,
                "diag": diag, "attempts": attempts,
            })

        browser.close()

    # Rapport compact
    manifest = output_dir / "playwright_capture_manifest.json"
    manifest.write_text(json.dumps({"captures": results}, indent=2, ensure_ascii=False))
    all_ok = all(r["conforme_30kb"] for r in results)
    print(f"[DONE] manifest={manifest} all_30kb_conforme={all_ok}")
    return 0 if all_ok else 1


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-url", required=True)
    ap.add_argument("--output-dir", required=True)
    args = ap.parse_args()
    raise SystemExit(run(args.base_url, Path(args.output_dir)))

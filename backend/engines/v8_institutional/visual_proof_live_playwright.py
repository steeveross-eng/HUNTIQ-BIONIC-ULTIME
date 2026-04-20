"""
Playwright capture script — Phase XI-SUPRA-C
Capture DOM TERRITOIRE réelle aux 3 niveaux de zoom sous authentification.
"""
import argparse
import json
import os
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

EMAIL = os.environ.get("CAPTURE_EMAIL", "steeve-max-capture@huntiq.com")
PASSWORD = os.environ.get("CAPTURE_PASSWORD", "CaptureOps2026#")
API_URL = os.environ.get("REACT_APP_BACKEND_URL") or "http://localhost:8001"

LEVELS = [
    ("macro", 12, "TERRITOIRE_macro_live.png"),
    ("mid", 15, "TERRITOIRE_mid_live.png"),
    ("detail", 16, "TERRITOIRE_detail_live.png"),
]

LAT = 45.10
LON = -72.80


def run(base_url: str, output_dir: Path):
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"[CAPTURE] base_url={base_url} output_dir={output_dir} api={API_URL}")

    # AUTH via urllib (pas besoin de playwright pour ça)
    import urllib.request, urllib.error
    req = urllib.request.Request(
        f"{API_URL}/api/auth/login",
        data=json.dumps({"email": EMAIL, "password": PASSWORD}).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=15) as r:
        auth = json.loads(r.read())
    token = auth.get("token")
    user = auth.get("user", {})
    print(f"[AUTH] OK token={token[:24]}… role={user.get('role')}")

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu"],
        )
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            ignore_https_errors=True,
        )
        context.add_init_script(f"""
          (() => {{
            try {{
              const token = {json.dumps(token)};
              const user = {json.dumps(json.dumps(user))};
              ['auth_token','token','hunter_token'].forEach(k => localStorage.setItem(k, token));
              ['user','hq_user','huntiq_user'].forEach(k => localStorage.setItem(k, user));
              localStorage.setItem('isAuthenticated', 'true');
            }} catch (e) {{}}
          }})();
        """)

        for level, zoom, filename in LEVELS:
            print(f"[CAPTURE] level={level} zoom={zoom}")
            page = context.new_page()
            page.goto(f"{base_url}/mon-territoire-bionic?lat={LAT}&lon={LON}&species=chevreuil&zoom={zoom}",
                       timeout=60000, wait_until="domcontentloaded")

            # Poll avec capture opportuniste : on capture dès qu'on a un état favorable
            path = output_dir / filename
            best_size = 0
            for poll in range(35):
                page.wait_for_timeout(1000)
                try:
                    diag = page.evaluate("""() => ({
                      lc: document.querySelectorAll('.leaflet-container').length,
                      hasMap: !!window.__bionicMap,
                      tiles: document.querySelectorAll('.leaflet-tile-loaded').length,
                      overlays: document.querySelectorAll('.leaflet-overlay-pane path, .leaflet-marker-icon').length
                    })""")
                except Exception:
                    continue
                if diag.get("hasMap") and diag.get("tiles", 0) >= 4:
                    try:
                        page.evaluate(f"""() => {{
                          const m = window.__bionicMap;
                          if (m) {{
                            try {{ m.closePopup(); }} catch(e){{}}
                            m.setView([{LAT}, {LON}], {zoom}, {{animate:false}});
                            m.invalidateSize();
                          }}
                          document.querySelectorAll('[role="dialog"], .modal-backdrop, .overlay-full').forEach(el => {{
                            try {{ el.style.display = 'none'; }} catch(e){{}}
                          }});
                        }}""")
                    except Exception:
                        pass
                    page.wait_for_timeout(2000)
                    # Capture: si taille actuelle meilleure que best, garde
                    try:
                        page.screenshot(path=str(path), full_page=False)
                        sz = path.stat().st_size
                    except Exception as e:
                        print(f"[CAPTURE]   screenshot err {e}")
                        continue
                    print(f"[CAPTURE]   {level} poll={poll+1} diag={diag} size={sz}")
                    if sz > best_size:
                        best_size = sz
                    else:
                        # size régression → restaure capture précédente ? Non, on garde la dernière valide
                        pass
                    if best_size > 30000 and poll >= 2:
                        break
            print(f"[CAPTURE] {filename} final size={best_size}")
            page.close()

        browser.close()
    print("[DONE]")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-url", required=True)
    ap.add_argument("--output-dir", required=True)
    args = ap.parse_args()
    run(args.base_url, Path(args.output_dir))

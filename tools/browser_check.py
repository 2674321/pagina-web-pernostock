#!/usr/bin/env python3
"""Prueba el sitio en un navegador real: recorre todas las paginas y reporta
errores de JavaScript, peticiones fallidas (404 de assets) y texto vacio.

Requiere el servidor local levantado y Playwright con Chromium.

Uso:
    python3 tools/serve.py &
    python3 tools/browser_check.py
"""
import sys
from pathlib import Path
from urllib.parse import urljoin, urlparse

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
BASE = "http://localhost:8000"

# Archivos que el sitio carga de forma externa y no son responsabilidade nossa.
EXTERNAL = ("cdn.jsdelivr.net", "cdnjs.cloudflare.com", "www.google.com",
            "maps.google.com", "fonts.googleapis.com", "gstatic.com",
            "www.recaptcha.net", "pernostock.cl", "www.facebook.com",
            "www.instagram.com", "twitter.com")


def is_external(url: str) -> bool:
    host = urlparse(url).netloc
    return any(host.endswith(d) for d in EXTERNAL)


def main() -> int:
    pages = sorted(p.name for p in ROOT.glob("*.html"))
    if not pages:
        print("No hay paginas HTML en la raiz.")
        return 1

    total_js = total_net = 0

    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        for name in pages:
            url = urljoin(BASE, name)
            page = browser.new_page()
            js_errors: list[str] = []
            net_errors: list[str] = []

            page.on("pageerror", lambda e: js_errors.append(str(e)))
            page.on("requestfailed",
                    lambda r: net_errors.append(f"{r.url} ({r.failure})"))
            page.on("response", lambda r: net_errors.append(f"{r.url} -> HTTP {r.status}")
                    if r.status >= 400 else None)

            page.goto(url, wait_until="networkidle", timeout=30000)

            # Comprueba que el cuerpo tenga contenido real.
            text_len = len(page.inner_text("body").strip())
            title = page.title()

            total_js += len(js_errors)
            total_net += len(net_errors)

            status = "OK"
            if js_errors or net_errors or text_len < 200:
                status = "REVISAR"

            print(f"[{status:7}] {name:42} titulo={title[:38]!r} texto={text_len}ch")
            for e in js_errors:
                print(f"            JS  : {e[:150]}")
            for e in net_errors:
                if not is_external(e):
                    print(f"            NET : {e[:150]}")

            page.close()
        browser.close()

    print(f"\nPaginas revisadas: {len(pages)}")
    print(f"Errores de JavaScript: {total_js}")
    print(f"Peticiones fallidas:   {total_net}")
    return 1 if (total_js or total_net) else 0


if __name__ == "__main__":
    sys.exit(main())

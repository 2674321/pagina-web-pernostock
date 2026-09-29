#!/usr/bin/env python3
"""Apunta las fichas tecnicas a los PDF locales cuando existen en el repositorio.

El sitio tenia los enlaces a https://pernostock.cl/... (servidor de produccion) y
un enlace a http://localhost/... que nunca funcionaba. Este script los convierte a
rutas locales solo cuando el archivo existe en media/pdf/fichas-tecnicas/; si no
existe, deja la URL de produccion original.

Uso: python3 tools/fix_fichas_links.py
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PDF_DIR = ROOT / "media" / "pdf" / "fichas-tecnicas"
REL_DIR = "media/pdf/fichas-tecnicas"
PAGES = [ROOT / "fichas_tecnicas.html", ROOT / "index.html", ROOT / "catalogos.html"]

REMOTE_PDF = re.compile(r'href="https?://[^"]*?/([A-Za-z0-9._-]+\.pdf)"', re.IGNORECASE)
LOCALHOST_ZIP = re.compile(r'href="http://localhost/[^"]*?/([^/"]+\.zip)"', re.IGNORECASE)


def local_names() -> set[str]:
    return {p.name for p in PDF_DIR.iterdir() if p.is_file()} if PDF_DIR.is_dir() else set()


def main() -> None:
    available = local_names()
    if not available:
        print("No se encontro media/pdf/fichas-tecnicas/. No se aplica ningun cambio.")
        return

    for page in PAGES:
        if not page.exists():
            continue
        original = text = page.read_text(encoding="utf-8", errors="replace")

        used_local: set[str] = set()
        fallback: list[str] = []

        def pdf_sub(m: re.Match) -> str:
            name = m.group(1)
            if name in available:
                used_local.add(name)
                return f'href="{REL_DIR}/{name}"'
            fallback.append(name)
            return m.group(0)

        def zip_sub(m: re.Match) -> str:
            name = m.group(1).replace("%20", " ")
            if name in available:
                used_local.add(name)
                return f'href="{REL_DIR}/{name}"'
            fallback.append(name)
            return m.group(0)

        text = REMOTE_PDF.sub(pdf_sub, text)
        text = LOCALHOST_ZIP.sub(zip_sub, text)

        if text != original:
            page.write_text(text, encoding="utf-8")

        print(f"  {page.name}: {len(used_local)} enlazados en local")
        if fallback:
            print(f"      sin copia local (se mantiene URL de produccion): "
                  f"{', '.join(sorted(set(fallback)))}")


if __name__ == "__main__":
    main()

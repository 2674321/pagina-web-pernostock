#!/usr/bin/env python3
"""Verifica que todos los enlaces y assets internos del sitio existan en disco.

Uso:  python3 tools/check_links.py
Salida: lista de referencias rotas, por archivo.
"""
import re
import sys
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Atributos que apuntan a un archivo del sitio.
# El nombre del atributo se captura para distinguir srcset (multiples URLs).
HTML_REFS = re.compile(
    r"""\b(src|href|srcset|data-src|poster)\s*=\s*["']([^"']+)["']""",
    re.IGNORECASE,
)
CSS_URL_RE = re.compile(r"""url\(\s*['"]?([^'")]+)['"]?\s*\)""", re.IGNORECASE)
CSS_IMPORT_RE = re.compile(r"""@import\s+["']([^"']+)["']""", re.IGNORECASE)

SKIP_SCHEMES = ("http://", "https://", "//", "mailto:", "tel:", "javascript:",
                "data:", "javascript:history", "#", "sms:", "whatsapp:")

TEXT_EXT = {".html", ".htm", ".php"}


def is_external(ref: str) -> bool:
    low = ref.strip().lower()
    return any(low.startswith(s) for s in SKIP_SCHEMES)


def check_html(path: Path) -> list[tuple[str, str]]:
    """Devuelve lista de (archivo, referencia_rota) para un HTML."""
    text = path.read_text(encoding="utf-8", errors="replace")
    broken = []
    for attr, raw in HTML_REFS.findall(text):
        attr = attr.lower()
        ref = raw.strip()
        if not ref or is_external(ref):
            continue
        # srcset admite varias URLs separadas por coma y con descriptor "2x".
        # En src/href el espacio es legal (p.ej. "archivos js/x.js") y NO se parte.
        if attr == "srcset":
            candidates = [c.split(" ")[0] for c in ref.split(",")]
        else:
            candidates = [ref]
        for candidate in candidates:
            candidate = candidate.strip()
            if not candidate or is_external(candidate):
                continue
            # Quita query string y fragmento, y decodifica %20
            clean = urllib.parse.unquote(candidate.split("?")[0].split("#")[0])
            if not clean:
                continue
            target = (path.parent / clean).resolve()
            if not target.exists():
                broken.append((str(path.relative_to(ROOT)), candidate))
    return broken


def check_css(path: Path) -> list[tuple[str, str]]:
    """Verifica los url() y @import de una hoja de estilos."""
    text = path.read_text(encoding="utf-8", errors="replace")
    refs = CSS_URL_RE.findall(text) + CSS_IMPORT_RE.findall(text)
    broken = []
    for raw in refs:
        ref = raw.strip()
        if not ref or is_external(ref):
            continue
        clean = urllib.parse.unquote(ref.split("?")[0].split("#")[0])
        if not clean:
            continue
        target = (path.parent / clean).resolve()
        if not target.exists():
            broken.append((str(path.relative_to(ROOT)), clean))
    return broken


def main() -> int:
    html_files = sorted(ROOT.rglob("*.html"))
    css_files = sorted(ROOT.rglob("*.css"))
    if not html_files:
        print("No se encontraron archivos .html")
        return 1

    broken: list[tuple[str, str]] = []
    for f in html_files:
        broken.extend(check_html(f))
    for f in css_files:
        broken.extend(check_css(f))

    print(f"Revisados: {len(html_files)} HTML, {len(css_files)} CSS")
    if not broken:
        print("\nOK: no hay referencias rotas.")
        return 0

    # Agrupa por archivo de destino
    by_file: dict[str, list[str]] = {}
    for origin, ref in broken:
        by_file.setdefault(ref, []).append(origin)

    print(f"\n{len(broken)} referencias rotas ({len(by_file)} destinos unicos):\n")
    for ref in sorted(by_file):
        origins = sorted(set(by_file[ref]))
        shown = ", ".join(origins[:3])
        more = f" (+{len(origins) - 3} mas)" if len(origins) > 3 else ""
        print(f"  FALTA  {ref}")
        print(f"         <- {shown}{more}")
    return 1


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Correcciones de normalizacion aplicadas a todos los HTML del sitio.

- Reescribe "javascript.js/archivos js/X.js" -> "js/X.js"
- Reemplaza el CDN muerto maxcdn.bootstrapcdn.com por cdn.jsdelivr.net
- Corrige el nombre erroneo empresa.js -> sobre_la_empresa.js

Uso: python3 tools/fix_references.py
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

REPLACEMENTS = [
    # Carpeta con espacio y nombre de directorio erroneo -> js/
    (re.compile(r"javascript\.js/archivos js/"), "js/"),
    # Bootstrap servido desde CDNs retirados -> jsDelivr
    (re.compile(r"https://(?:maxcdn|stackpath)\.bootstrapcdn\.com/bootstrap/([\d.]+)/css/bootstrap\.min\.css"),
     r"https://cdn.jsdelivr.net/npm/bootstrap@\1/dist/css/bootstrap.min.css"),
    (re.compile(r"https://(?:maxcdn|stackpath)\.bootstrapcdn\.com/bootstrap/([\d.]+)/js/bootstrap\.min\.js"),
     r"https://cdn.jsdelivr.net/npm/bootstrap@\1/dist/js/bootstrap.min.js"),
    # El archivo real se llama sobre_la_empresa.js
    (re.compile(r"js/empresa\.js"), "js/sobre_la_empresa.js"),
]


def main() -> None:
    changed_files = 0
    total_hits = 0
    for path in sorted(ROOT.rglob("*.html")):
        original = text = path.read_text(encoding="utf-8", errors="replace")
        hits = 0
        for pattern, repl in REPLACEMENTS:
            text, n = pattern.subn(repl, text)
            hits += n
        if text != original:
            path.write_text(text, encoding="utf-8")
            changed_files += 1
            total_hits += hits
            print(f"  {path.relative_to(ROOT)}  ({hits} cambios)")
    print(f"\n{changed_files} archivos actualizados, {total_hits} reemplazos.")


if __name__ == "__main__":
    main()

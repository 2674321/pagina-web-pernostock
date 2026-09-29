#!/usr/bin/env python3
"""Genera favicon.ico e iconos PNG a partir del logo de la marca.

Reduce el logo a 256x256 con transparencia, centrado sobre fondo oscuro para que
se vea tanto en pestanas claras como oscuras, y escribe los formatos que usan
los navegadores.

Uso: python3 tools/make_favicon.py
"""
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "images" / "logo_pernostock" / "rojo" / "logo_pernostock_rojo_transparente.png"
PNG_OUT = ROOT / "assets" / "favicon-256.png"
ICO_OUT = ROOT / "favicon.ico"
SIZES = (16, 32, 48, 64, 128, 256)


def main() -> None:
    if not SRC.exists():
        raise SystemExit(f"No se encontro el logo fuente: {SRC}")

    logo = Image.open(SRC).convert("RGBA")
    # Encaja el logo dentro de un lienzo cuadrado con margen.
    canvas = Image.new("RGBA", (512, 512), (51, 51, 51, 255))
    side = int(min(canvas.size) * 0.82)
    logo.thumbnail((side, side), Image.LANCZOS)
    canvas.alpha_composite(logo, ((canvas.width - logo.width) // 2,
                                  (canvas.height - logo.height) // 2))

    PNG_OUT.parent.mkdir(parents=True, exist_ok=True)
    canvas.resize((256, 256), Image.LANCZOS).save(PNG_OUT, "PNG", optimize=True)
    canvas.save(ICO_OUT, sizes=[(s, s) for s in SIZES])

    print(f"Generado {ICO_OUT.relative_to(ROOT)} ({ICO_OUT.stat().st_size:,} bytes)")
    print(f"Generado {PNG_OUT.relative_to(ROOT)} ({PNG_OUT.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()

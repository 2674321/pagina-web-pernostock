#!/usr/bin/env python3
"""Reduce el peso de las imagenes del sitio sin perder calidad visible.

Tras la recuperacion many imagenes venian con dimensiones enormes (un logo de
marca de 11760 px que se muestra a 150 px) yPesaban cientos de KB o varios MB.

Reglas:
- Se limita el lado mas largo a MAX_EDGE px (1600), suficiente para la web.
- Se conserva la transparencia de los PNG.
- Los JPG se recomprimen con calidad alta y de forma progresiva.
- No se toca ninguna imagen que ya sea pequena.

Las originales se guardan en _original/ por si hay que revertir.

Uso:
    python3 tools/optimize_images.py          # procesar
    python3 tools/optimize_images.py --dry    # solo mostrar el plan
"""
import shutil
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
IMAGES = ROOT / "images"
BACKUP = ROOT / "_original"
MAX_EDGE = 1600
MIN_BYTES = 200 * 1024   # no tocar imagenes menores a 200 KB
JPEG_QUALITY = 82

EXTS = {".png", ".jpg", ".jpeg"}


def candidates() -> list[Path]:
    return [p for p in sorted(IMAGES.rglob("*"))
            if p.is_file() and p.suffix.lower() in EXTS]


def process(path: Path, dry: bool) -> tuple[int, int, str | None]:
    """Devuelve (antes, despues, nota)."""
    before = path.stat().st_size
    if before < MIN_BYTES:
        return before, before, "sin cambios (ya es pequena)"

    try:
        with Image.open(path) as im:
            fmt = im.format
            w, h = im.size
            longest = max(w, h)
            if longest <= MAX_EDGE:
                # Solo reoptimizar (comprimir sin cambiar dimensiones).
                resaved = _save(im, path, fmt)
                if resaved < before * 0.98:
                    return before, resaved, f"recomprimido {w}x{h}"
                return before, before, f"sin cambios {w}x{h}"

            scale = MAX_EDGE / longest
            new_size = (max(1, round(w * scale)), max(1, round(h * scale)))
            resized = im.resize(new_size, Image.LANCZOS)
            resaved = _save(resized, path, fmt)
            return before, resaved, f"reducida {w}x{h} -> {new_size[0]}x{new_size[1]}"
    except Exception as exc:  # noqa: BLE001
        return before, before, f"ERROR: {exc}"


def _save(im: Image.Image, path: Path, fmt: str | None) -> int:
    """Guarda la imagen y devuelve el tamano resultante en disco."""
    if dry_run():
        return 0

    BACKUP.mkdir(exist_ok=True)
    dest_backup = BACKUP / path.relative_to(IMAGES)
    dest_backup.parent.mkdir(parents=True, exist_ok=True)
    if not dest_backup.exists():
        shutil.copy2(path, dest_backup)

    suffix = path.suffix.lower()
    if suffix == ".png" or fmt == "PNG":
        out = im.convert("RGBA") if im.mode in ("P", "LA") or "transparen" in str(im.info) else im
        out.save(path, "PNG", optimize=True)
    else:
        out = im.convert("RGB")
        out.save(path, "JPEG", quality=JPEG_QUALITY, optimize=True, progressive=True)
    return path.stat().st_size


def dry_run() -> bool:
    return "--dry" in sys.argv


def main() -> None:
    dry = dry_run()
    if dry:
        print("MODO SIMULACION: no se modifica nada.\n")

    total_before = total_after = 0
    changed = 0

    for path in candidates():
        before, after, note = process(path, dry)
        total_before += before
        total_after += after
        if after < before:
            changed += 1
            saved = (before - after) / 1024
            print(f"  {path.relative_to(ROOT)}\n      {note}  "
                  f"({before/1024:.0f} KB -> {after/1024:.0f} KB, -{saved:.0f} KB)")

    print(f"\nImagenes procesadas: {len(candidates())}, reducidas: {changed}")
    if dry:
        print(f"Tamano actual: {total_before/1024/1024:.1f} MB")
    else:
        print(f"Tamano total: {total_before/1024/1024:.1f} MB -> "
              f"{total_after/1024/1024:.1f} MB")
        print(f"Originales guardados en {BACKUP.relative_to(ROOT)}/")


if __name__ == "__main__":
    main()

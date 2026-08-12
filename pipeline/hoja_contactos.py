#!/usr/bin/env python3
"""Arma una hoja de contactos con las imágenes descargadas de Flow.

Uso: python3 hoja_contactos.py <carpeta> <prefijo> [salida.jpg]
Ej:  python3 hoja_contactos.py output/mi-video/_flow_nuevo b1 hoja_b1.jpg

POR QUÉ EXISTE
Flow no guarda qué prompt generó cada imagen: las marca todas como "Imagen
generada" y el HTML no trae más pistas. Tampoco se puede confiar en el orden de
descarga, porque la galería cambia de orden al recargar la página.

La única forma de emparejar imagen ↔ compás es mirarlas. Verlas de una en una
serían 100 lecturas; en una hoja de contactos con el número escrito encima se
identifican todas de una sola pasada.
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw

COLS, CW, CH = 5, 380, 214       # 5 columnas entra cómodo en una lectura


def main():
    carpeta = Path(sys.argv[1])
    prefijo = sys.argv[2]
    salida = Path(sys.argv[3]) if len(sys.argv) > 3 else carpeta.parent / f"hoja_{prefijo}.jpg"

    fs = sorted(carpeta.glob(f"{prefijo}_*.jpg"))
    if not fs:
        sys.exit(f"[hoja] no hay imágenes {prefijo}_*.jpg en {carpeta}")

    filas = (len(fs) + COLS - 1) // COLS
    hoja = Image.new("RGB", (COLS * CW, filas * (CH + 26)), (20, 20, 20))
    dib = ImageDraw.Draw(hoja)

    for i, f in enumerate(fs):
        im = Image.open(f).convert("RGB").resize((CW - 8, CH - 8), Image.LANCZOS)
        x, y = (i % COLS) * CW, (i // COLS) * (CH + 26)
        hoja.paste(im, (x + 4, y + 22))
        dib.text((x + 6, y + 4), f.stem, fill=(255, 220, 80))

    hoja.save(salida, quality=87)
    print(f"[hoja] {len(fs)} imágenes → {salida}")


if __name__ == "__main__":
    main()

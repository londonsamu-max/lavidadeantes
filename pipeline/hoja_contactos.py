#!/usr/bin/env python3
"""Arma hojas de contactos numeradas con las imágenes descargadas de Flow.

Uso: python3 hoja_contactos.py <carpeta_imagenes> <carpeta_salida> [--por-hoja 12]

POR QUÉ EXISTE
Flow entrega las imágenes con nombres suyos y en un orden que no es el de los
prompts: marca todas igual («Imagen generada») y la galería se reordena al
recargar, así que el HTML no dice cuál es cuál. La única forma fiable de saber
qué imagen corresponde a qué compás es MIRARLAS, y para mirarlas de a cien hace
falta una rejilla con un número grande encima de cada una.

El número que se pinta es el índice dentro de la carpeta ordenada por nombre, y
es el que se usa después en el mapa que consume colocar.py:

    {"000": 7, "001": 3, ...}   ← compás: número de esta hoja

Salida: hoja_01.jpg, hoja_02.jpg... y contactos.json con el índice→archivo, para
que colocar.py pueda traducir sin volver a listar la carpeta (si alguien la
reordena entre medias, el mapa seguiría siendo válido).
"""
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
FUENTE = ROOT / "assets" / "fonts" / "BebasNeue.ttf"
COLUMNAS = 4
ANCHO_CELDA = 480          # la miniatura de cada celda
MARGEN = 12
ALTO_NUMERO = 64           # banda superior donde va el número
EXTS = (".jpg", ".jpeg", ".png", ".webp")


def _fuente(tam):
    if FUENTE.exists():
        return ImageFont.truetype(str(FUENTE), tam)
    return ImageFont.load_default()


def celda(img_path: Path, numero: int, ancho: int) -> Image.Image:
    """Una miniatura 16:9 con su número en una banda oscura arriba."""
    alto_img = int(ancho * 9 / 16)
    lienzo = Image.new("RGB", (ancho, alto_img + ALTO_NUMERO), (24, 20, 16))
    try:
        im = Image.open(img_path).convert("RGB")
    except Exception:
        im = Image.new("RGB", (ancho, alto_img), (90, 30, 30))
    # cubrir y recortar: nunca deformar
    escala = max(ancho / im.width, alto_img / im.height)
    im = im.resize((max(int(im.width * escala), ancho), max(int(im.height * escala), alto_img)),
                   Image.LANCZOS)
    izq = (im.width - ancho) // 2
    arr = (im.height - alto_img) // 2
    lienzo.paste(im.crop((izq, arr, izq + ancho, arr + alto_img)), (0, ALTO_NUMERO))

    d = ImageDraw.Draw(lienzo)
    d.rectangle([0, 0, ancho, ALTO_NUMERO], fill=(18, 14, 10))
    d.text((14, ALTO_NUMERO // 2), f"{numero:03d}", font=_fuente(46),
           fill=(255, 198, 26), anchor="lm")
    d.text((ancho - 14, ALTO_NUMERO // 2), img_path.name[:26], font=_fuente(24),
           fill=(150, 140, 128), anchor="rm")
    return lienzo


def main():
    args = sys.argv[1:]
    por_hoja = 12
    if "--por-hoja" in args:
        k = args.index("--por-hoja")
        por_hoja = int(args[k + 1])
        del args[k:k + 2]
    if len(args) < 2:
        sys.exit(__doc__)

    origen, destino = Path(args[0]).resolve(), Path(args[1]).resolve()
    destino.mkdir(parents=True, exist_ok=True)
    imagenes = sorted([p for p in origen.iterdir() if p.suffix.lower() in EXTS])
    if not imagenes:
        sys.exit(f"[hoja] no hay imágenes en {origen}")

    # «_origen» va dentro del índice a propósito: las hojas y las imágenes viven
    # en carpetas distintas, y sin esta pista colocar.py no sabría dónde están
    # los archivos si se le pasa la carpeta de las hojas.
    indice = {"_origen": str(origen)}
    indice.update({f"{i}": p.name for i, p in enumerate(imagenes)})
    (destino / "contactos.json").write_text(
        json.dumps(indice, indent=1, ensure_ascii=False) + "\n")

    filas_por_hoja = (por_hoja + COLUMNAS - 1) // COLUMNAS
    alto_celda = int(ANCHO_CELDA * 9 / 16) + ALTO_NUMERO
    hojas = 0
    for ini in range(0, len(imagenes), por_hoja):
        trozo = imagenes[ini:ini + por_hoja]
        ancho_hoja = COLUMNAS * ANCHO_CELDA + (COLUMNAS + 1) * MARGEN
        alto_hoja = filas_por_hoja * alto_celda + (filas_por_hoja + 1) * MARGEN
        hoja = Image.new("RGB", (ancho_hoja, alto_hoja), (12, 10, 8))
        for k, p in enumerate(trozo):
            fila, col = divmod(k, COLUMNAS)
            x = MARGEN + col * (ANCHO_CELDA + MARGEN)
            y = MARGEN + fila * (alto_celda + MARGEN)
            hoja.paste(celda(p, ini + k, ANCHO_CELDA), (x, y))
        hojas += 1
        salida = destino / f"hoja_{hojas:02d}.jpg"
        hoja.save(salida, quality=88)
        print(f"[hoja] {salida.name}: imágenes {ini}–{ini + len(trozo) - 1}")

    print(f"[hoja] {len(imagenes)} imágenes en {hojas} hojas → {destino}")
    print(f"[hoja] índice número→archivo en {destino / 'contactos.json'}")
    print("[hoja] SIGUIENTE: mira las hojas, escribe el mapa {compás: número} "
          "y pásaselo a colocar.py")


if __name__ == "__main__":
    main()

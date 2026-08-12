#!/usr/bin/env python3
"""Duplica la resolución de las imágenes generadas con un modelo neuronal.

Uso: python3 nitidez.py <carpeta_imagenes>

POR QUÉ EXISTE
El servicio gratuito de generación entrega 1024x576 y no más, aunque se le pida.
El video es 1920x1080, así que assemble tenía que AMPLIAR ~2x, y eso se veía blando
(«como estiradas»). Con ESPCN x2 las imágenes pasan a 2048x1152 — por encima del
video — y el ensamblaje pasa de ampliar a REDUCIR, que siempre sale nítido.

Medido: 0,3 s por imagen. Las ~140 de un video en menos de un minuto.
No necesita internet, cuenta ni pago: el modelo son 86 KB y va en assets/modelos/.

Es idempotente: salta las imágenes que ya estén por encima de 1600 px de ancho.
"""
import sys
import time
from pathlib import Path

import cv2

ROOT = Path(__file__).resolve().parent.parent
MODELO = ROOT / "assets" / "modelos" / "ESPCN_x2.pb"
ANCHO_OBJETIVO = 1600   # por encima de esto no hace falta ampliar


def main():
    if len(sys.argv) < 2:
        sys.exit("uso: nitidez.py <carpeta_imagenes>")
    carpeta = Path(sys.argv[1])
    if not MODELO.exists():
        sys.exit(f"[nitidez] falta el modelo: {MODELO}")

    sr = cv2.dnn_superres.DnnSuperResImpl_create()
    sr.readModel(str(MODELO))
    sr.setModel("espcn", 2)

    imgs = sorted(p for p in carpeta.iterdir()
                  if p.suffix.lower() in (".jpg", ".jpeg", ".png"))
    if not imgs:
        sys.exit(f"[nitidez] no hay imágenes en {carpeta}")

    hechas, saltadas, fallidas = 0, 0, []
    t0 = time.time()
    for p in imgs:
        img = cv2.imread(str(p))
        if img is None:
            fallidas.append(p.name)
            continue
        if img.shape[1] >= ANCHO_OBJETIVO:
            saltadas += 1
            continue
        try:
            out = sr.upsample(img)
            cv2.imwrite(str(p), out, [cv2.IMWRITE_JPEG_QUALITY, 95])
            hechas += 1
        except Exception as e:
            fallidas.append(f"{p.name}: {e}")

    d = time.time() - t0
    print(f"[nitidez] {hechas} ampliadas a 2x · {saltadas} ya estaban bien · "
          f"{len(fallidas)} fallidas · {d:.0f}s")
    if fallidas:
        print(f"[nitidez] fallidas: {fallidas[:5]}")


if __name__ == "__main__":
    main()

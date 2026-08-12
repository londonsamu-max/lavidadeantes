#!/usr/bin/env python3
"""Convierte el plan de compases en bloques listos para pegar en Google Flow.

Uso: python3 bloques_flow.py <carpeta_job> [tamaño_bloque]

POR QUÉ
Flow (modo Agente) acepta muchos prompts pegados de una vez y genera todas las
imágenes, nombrándolas con un número correlativo. Eso permite conseguir imágenes
de Nano Banana 2 a 1376x768 —mejores y más grandes que el generador gratuito que
veníamos usando (1024x576)— con ~6 pegadas por video en vez de 141 generaciones.

Escribe `bloques_flow/bloque_NN.txt`. Cada archivo lleva arriba la instrucción
para el agente y debajo los prompts numerados. El número del prompt es el índice
del compás, para que el nombre del archivo descargado permita recolocar cada
imagen en su momento exacto del video.
"""
import json
import sys
from pathlib import Path

CABECERA = (
    "Genera una imagen por cada indicación numerada de abajo, en orden. "
    "Nombra cada archivo EXACTAMENTE con el número de tres cifras que abre su "
    "indicación (por ejemplo 007), sin añadir nada más. No omitas ninguna. "
    "Formato 16:9. Estilo común para todas: acuarela delicada con textura de papel "
    "visible, pinceladas sueltas, luz cálida y clara, alto contraste, paleta de "
    "tierras suaves, Latinoamérica años setenta. Sin texto, sin letras, sin marcas "
    "de agua en la imagen.\n"
)


def main():
    job = Path(sys.argv[1]).resolve()
    tam = int(sys.argv[2]) if len(sys.argv) > 2 else 24

    plan = json.loads((job / "visuales.json").read_text())
    beats = plan["beats"] if isinstance(plan, dict) else plan

    dest = job / "bloques_flow"
    dest.mkdir(exist_ok=True)
    for f in dest.glob("*.txt"):
        f.unlink()

    bloques = 0
    for ini in range(0, len(beats), tam):
        trozo = beats[ini:ini + tam]
        lineas = [CABECERA]
        for i, b in enumerate(trozo, start=ini):
            lineas.append(f"{i:03d}. {b['q']}")
        bloques += 1
        (dest / f"bloque_{bloques:02d}.txt").write_text("\n".join(lineas) + "\n")

    # el mapa número→segundo permite renombrar las descargas a b###_t#######_
    mapa = {f"{i:03d}": b["t"] for i, b in enumerate(beats)}
    (job / "mapa_compases.json").write_text(json.dumps(mapa, indent=1))

    print(f"[flow] {len(beats)} compases → {bloques} bloques de hasta {tam}")
    print(f"[flow] archivos en {dest}")
    print(f"[flow] mapa número→segundo en mapa_compases.json")
    print(f"[flow] pega cada bloque en Flow (modo Agente) y al final "
          f"«Descargar proyecto»")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Coloca las imágenes de Flow en su compás exacto del video.

Uso: python3 colocar.py <carpeta_job> <mapa.json> [carpeta_origen]

El mapa es {"<numero_de_compas>": "<nombre_de_archivo_sin_extension>"}, tal como
sale de leer la hoja de contactos:

    {"0": "b1_012", "1": "b1_013", "51": "b1_019"}

Renombra cada imagen a `b###_t#######_flow.jpg`, que es el formato con el que
assemble.py ancla cada imagen al segundo exacto de la narración. Si ya había una
imagen en ese compás, la reemplaza.

Un mismo archivo puede ir a varios compases: los planes de compases repiten
prompts dentro de una sección, así que reutilizar una variante está previsto.
"""
import json
import shutil
import sys
from pathlib import Path


def main():
    job = Path(sys.argv[1]).resolve()
    mapa = json.loads(Path(sys.argv[2]).read_text())
    origen = Path(sys.argv[3]) if len(sys.argv) > 3 else job / "_flow_nuevo"

    beats = json.loads((job / "visuales.json").read_text())["beats"]
    destino = job / "visuales-gen"
    destino.mkdir(parents=True, exist_ok=True)

    puestas, faltan = 0, []
    for compas_s, archivo in mapa.items():
        compas = int(compas_s)
        src = origen / f"{archivo}.jpg"
        if not src.exists():
            faltan.append(archivo)
            continue
        for viejo in destino.glob(f"b{compas:03d}_*"):
            viejo.unlink()
        t = beats[compas]["t"]
        shutil.copy(src, destino / f"b{compas:03d}_t{int(t*100):07d}_flow.jpg")
        puestas += 1

    print(f"[colocar] {puestas} imágenes colocadas")
    if faltan:
        print(f"[colocar] NO ENCONTRADAS: {faltan}")

    # informe de huecos: es el chequeo que evita montar un video a medias
    hay = {int(f.name[1:4]) for f in destino.glob("b*_*.jpg")}
    sin = [i for i in range(len(beats)) if i not in hay]
    print(f"[colocar] cobertura: {len(hay)}/{len(beats)}")
    if sin:
        print(f"[colocar] compases SIN imagen: {sin}")


if __name__ == "__main__":
    main()

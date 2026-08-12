#!/usr/bin/env python3
"""Genera UNA imagen suelta. Para miniaturas, sobre todo.

Uso: python3 imagen.py "<prompt>" <salida.jpg> [--estilo ilustracion|acuarela|foto]
                                              [--ancho 1280] [--alto 720] [--semilla N]

visuals_gen.py necesita un plan de compases completo; para una portada hace falta
pedir una sola imagen, normalmente un primer plano de una cara, que es lo que la
evidencia dice que hace clicar (69-80% de los videos que despegan llevan rostro).
"""
import sys
import urllib.parse
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))
from visuals_gen import ESTILOS, NEGATIVO, CONTEXTO  # noqa: E402

API = "https://image.pollinations.ai/prompt/"


def generar(prompt: str, destino: Path, w: int, h: int, semilla: int) -> bool:
    url = API + urllib.parse.quote(prompt, safe="") + (
        f"?width={w}&height={h}&nologo=true&seed={semilla}"
    )
    for intento in range(4):
        try:
            r = requests.get(url, timeout=180)
            if r.status_code == 200 and len(r.content) > 20_000:
                destino.parent.mkdir(parents=True, exist_ok=True)
                destino.write_bytes(r.content)
                print(f"[imagen] OK → {destino} ({len(r.content)//1024} KB)")
                return True
            print(f"[imagen] reintento {intento+1}: HTTP {r.status_code}")
        except Exception as e:
            print(f"[imagen] reintento {intento+1}: {e}")
    return False


def main():
    args = sys.argv[1:]

    def saca(bandera, defecto):
        if bandera in args:
            k = args.index(bandera)
            v = args[k + 1]
            del args[k:k + 2]
            return v
        return defecto

    estilo = saca("--estilo", "ilustracion")
    w = int(saca("--ancho", "1280"))
    h = int(saca("--alto", "720"))
    semilla = int(saca("--semilla", "7"))

    prompt, salida = args[0], Path(args[1])
    # El estilo va DELANTE: puesto al final el modelo lo diluía y devolvía caras
    # fotorrealistas, que en este canal no sirven — la portada tiene que verse
    # ilustrada, igual que el video, y no pasar por fotografía de época.
    completo = ", ".join([ESTILOS[estilo], prompt.strip(), CONTEXTO,
                          ESTILOS[estilo], NEGATIVO,
                          "no frame, no border, no picture frame"])
    if not generar(completo, salida, w, h, semilla):
        sys.exit("[imagen] no se pudo generar")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Genera las imágenes del video en vez de buscarlas.

Uso: python3 visuals_gen.py <visuales.json> <carpeta_salida> [--estilo foto|ilustracion]

POR QUÉ EXISTE
Buscar en Wikimedia/LOC devuelve lo que se PARECE a las palabras de la consulta, sin
verificar relevancia, idioma ni cultura. En el video 3, 6 de 11 momentos muestreados
traían imágenes ajenas al guion (un comedor con letrero en hebreo para «se ponía el
mantel bueno», una carta manuscrita en inglés para «se comía despacio»). Generar es
literal: se pide la escena y sale la escena.

ESTILO POR DEFECTO: ilustración, no fotografía.
El canal narra la vida real de los años 70. Generar fotorrealismo y pasarlo por el
filtro vintage de assemble.py produciría fotografías históricas falsas de un pasado
real — eso es fabricar registro histórico. La ilustración se lee como lo que es.
Con `--estilo foto` se puede forzar el fotorrealismo, pero entonces hay que declarar
contenido sintético en YouTube Studio y decirlo en la descripción.

Mantiene el nombre `b###_t#######_slug.jpg` que assemble.py usa para anclar cada
imagen a su momento exacto. Es reanudable: salta las que ya existen.
"""
import json
import re
import sys
import time
import urllib.parse
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
API = "https://image.pollinations.ai/prompt/"

ESTILOS = {
    # «bright, well-lit» no es capricho: assemble.py aplica encima un filtro vintage
    # (satura­ción 0.82 + viñeta) que oscurece, y la audiencia 50+ necesita contraste
    # alto. En el video 4 los prompts sombríos (preocupación, atardecer, carnicería)
    # dieron un brillo medio de 93/255 contra 121 del video 3: 23% más oscuro.
    "ilustracion": (
        "warm nostalgic hand-painted illustration, painterly digital art, "
        "bright, well-lit, clear daylight, high contrast, "
        "soft diffused light, muted earth tones, gentle grain"
    ),
    # Igual al estilo que produce Google Flow, para poder mezclar ambas fuentes
    # dentro de un mismo video sin que se note el salto.
    "acuarela": (
        "delicate watercolor painting with visible paper texture, loose brushwork, "
        "soft washes, bright and clear warm light, high contrast, "
        "muted earth palette, 1970s Latin America"
    ),
    "foto": (
        "vintage documentary photograph, 35mm film, natural light, "
        "faded colors, slight grain"
    ),
}
# El modelo tiende a inventar letreros con texto ilegible o en inglés: prohibirlo
# explícitamente es lo que evita repetir el error de las imágenes buscadas.
NEGATIVO = "no text, no letters, no words, no signs, no watermark, no signature, no captions"
CONTEXTO = "Latin America, 1970s, working class neighborhood, everyday life"

TIEMPO_ESPERA = 180
REINTENTOS = 3


def construir(q: str, estilo: str) -> str:
    partes = [q.strip(), CONTEXTO, ESTILOS[estilo], NEGATIVO]
    return ", ".join(p for p in partes if p)


def generar(prompt: str, semilla: int, destino: Path) -> bool:
    url = API + urllib.parse.quote(prompt, safe="") + (
        f"?width=1280&height=720&nologo=true&seed={semilla}"
    )
    for intento in range(REINTENTOS):
        try:
            r = requests.get(url, timeout=TIEMPO_ESPERA)
            # el free tier responde 429 con un JSON corto cuando ya hay uno en cola
            if r.status_code == 200 and len(r.content) > 20_000:
                destino.write_bytes(r.content)
                return True
            espera = 8 * (intento + 1)
            print(f"[gen]   reintento {intento+1} (HTTP {r.status_code}, "
                  f"{len(r.content)} b) — espero {espera}s")
            time.sleep(espera)
        except Exception as e:
            print(f"[gen]   reintento {intento+1}: {e}")
            time.sleep(8 * (intento + 1))
    return False


def main():
    args = sys.argv[1:]
    estilo = "ilustracion"
    if "--estilo" in args:
        k = args.index("--estilo")
        estilo = args[k + 1]
        args = args[:k] + args[k + 2:]
    if estilo not in ESTILOS:
        sys.exit(f"[gen] estilo desconocido: {estilo} (usa {'/'.join(ESTILOS)})")

    plan_file, outdir = Path(args[0]), Path(args[1])
    outdir.mkdir(parents=True, exist_ok=True)
    plan = json.loads(plan_file.read_text())
    beats = plan["beats"] if isinstance(plan, dict) else plan

    ya = {p.name[:4] for p in outdir.glob("b*.jpg")}   # b000, b001... para reanudar
    print(f"[gen] {len(beats)} compases · estilo «{estilo}» · {len(ya)} ya generados")

    hechas, fallidas = 0, []
    t0 = time.time()
    for bi, b in enumerate(beats):
        clave = f"b{bi:03d}"
        if clave in ya:
            continue
        q = b.get("q", "") or b.get("es", "")
        if not q:
            fallidas.append(bi)
            continue
        slug = re.sub(r"[^a-z0-9]+", "-", q.lower())[:32].strip("-") or "img"
        destino = outdir / f"{clave}_t{int(b['t']*100):07d}_{slug}.jpg"
        if generar(construir(q, estilo), 1000 + bi, destino):
            hechas += 1
        else:
            fallidas.append(bi)
            print(f"[gen] compás {bi} ({b['t']:.0f}s) FALLÓ: «{q[:40]}»")
        if hechas and hechas % 10 == 0:
            transcurrido = time.time() - t0
            restantes = len(beats) - len(ya) - hechas
            print(f"[gen] {hechas} listas · {transcurrido/hechas:.0f}s c/u · "
                  f"faltan ~{restantes*transcurrido/hechas/60:.0f} min")

    print(f"[gen] TOTAL: {hechas} generadas, {len(fallidas)} fallidas "
          f"en {(time.time()-t0)/60:.0f} min")
    if fallidas:
        print(f"[gen] compases sin imagen: {fallidas}")
        print("[gen] vuelve a ejecutar el mismo comando: reanuda solo las que faltan")


if __name__ == "__main__":
    main()

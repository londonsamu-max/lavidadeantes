#!/usr/bin/env python3
"""Genera las imágenes del video con los modelos de Google (Nano Banana / Imagen).

Uso: python3 visuals_google.py <visuales.json> <carpeta_salida>
                               [--estilo ilustracion|acuarela|foto]
                               [--modelo gemini-3.1-flash-image]

Necesita GOOGLE_AI_API_KEY en el entorno o en .env (clave de aistudio.google.com).

POR QUÉ EXISTE
El servicio gratuito que usa visuals_gen.py corre un modelo pequeño («sana») que
falla en los objetos concretos del canal: «pila de discos en fundas de papel»
devuelve un plato abstracto, y «consola» no lo dibuja nunca. Los modelos de
Google sí entienden la escena, y son los mismos que hay detrás de Google Flow,
cuya interfaz web está geobloqueada desde los servidores donde corre el cerebro.

Mantiene el mismo nombre de archivo `b###_t#######_slug.jpg` que assemble.py usa
para anclar cada imagen a su momento exacto, así que es intercambiable con
visuals_gen.py. Es reanudable: salta las que ya existen.

CUPO
El nivel gratuito de un proyecto nuevo alcanza para un video. Si la clave
pertenece a un proyecto en modalidad de pago anticipado sin saldo, la API
responde 429 «prepayment credits are depleted» y aquí se corta de inmediato con
un mensaje claro, en vez de reintentar 159 veces contra un muro.
"""
import base64
import json
import os
import re
import sys
import time
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
BASE = "https://generativelanguage.googleapis.com/v1beta"
MODELO_POR_DEFECTO = "gemini-3.1-flash-image"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from visuals_gen import CONTEXTO, ESTILOS, NEGATIVO  # noqa: E402

REINTENTOS = 3
TIEMPO_ESPERA = 180


def leer_clave() -> str:
    clave = os.environ.get("GOOGLE_AI_API_KEY", "").strip()
    if not clave:
        env = ROOT / ".env"
        if env.exists():
            for linea in env.read_text().splitlines():
                if linea.strip().startswith("GOOGLE_AI_API_KEY"):
                    clave = linea.split("=", 1)[1].strip().strip('"').strip("'")
                    break
    if not clave:
        sys.exit("[google] falta GOOGLE_AI_API_KEY (en el entorno o en .env).\n"
                 "         Consíguela gratis en https://aistudio.google.com/apikey\n"
                 "         — elige «Create API key in new project» para entrar al nivel gratuito.")
    return clave


def construir(q: str, estilo: str) -> str:
    # El estilo va delante, igual que en imagen.py y visuals_gen.py: puesto solo al
    # final el modelo lo diluye.
    return (f"{ESTILOS[estilo]}. Scene: {q.strip()}. Setting: {CONTEXTO}. "
            f"{NEGATIVO}.")


def generar(prompt: str, destino: Path, clave: str, modelo: str) -> str:
    """Devuelve 'ok', 'fallo' o 'sin-cupo' (esto último aborta la corrida)."""
    url = f"{BASE}/models/{modelo}:generateContent"
    cuerpo = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"responseModalities": ["IMAGE"],
                             "imageConfig": {"aspectRatio": "16:9"}},
    }
    for intento in range(REINTENTOS):
        try:
            r = requests.post(url, headers={"x-goog-api-key": clave},
                              json=cuerpo, timeout=TIEMPO_ESPERA)
            if r.status_code == 200:
                for p in r.json()["candidates"][0]["content"]["parts"]:
                    if "inlineData" in p:
                        destino.write_bytes(base64.b64decode(p["inlineData"]["data"]))
                        return "ok"
                return "fallo"          # respondió sin imagen (filtro de seguridad)
            if r.status_code == 429:
                if "prepayment credits" in r.text or "depleted" in r.text:
                    return "sin-cupo"
                espera = 20 * (intento + 1)     # límite por minuto: esperar y seguir
                print(f"[google]   cupo por minuto, espero {espera}s")
                time.sleep(espera)
                continue
            print(f"[google]   HTTP {r.status_code}: {r.text[:160]}")
            time.sleep(8 * (intento + 1))
        except Exception as e:
            print(f"[google]   reintento {intento+1}: {e}")
            time.sleep(8 * (intento + 1))
    return "fallo"


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
    modelo = saca("--modelo", MODELO_POR_DEFECTO)
    if estilo not in ESTILOS:
        sys.exit(f"[google] estilo desconocido: {estilo} (usa {'/'.join(ESTILOS)})")

    plan_file, outdir = Path(args[0]), Path(args[1])
    outdir.mkdir(parents=True, exist_ok=True)
    plan = json.loads(plan_file.read_text())
    beats = plan["beats"] if isinstance(plan, dict) else plan
    clave = leer_clave()

    ya = {p.name[:4] for p in outdir.glob("b*.jpg")}
    print(f"[google] {len(beats)} compases · modelo «{modelo}» · estilo «{estilo}» · "
          f"{len(ya)} ya generados")

    hechas, fallidas = 0, []
    t0 = time.time()
    for bi, b in enumerate(beats):
        clave_img = f"b{bi:03d}"
        if clave_img in ya:
            continue
        q = b.get("q", "") or b.get("es", "")
        if not q:
            fallidas.append(bi)
            continue
        slug = re.sub(r"[^a-z0-9]+", "-", q.lower())[:32].strip("-") or "img"
        destino = outdir / f"{clave_img}_t{int(b['t']*100):07d}_{slug}.jpg"
        estado = generar(construir(q, estilo), destino, clave, modelo)
        if estado == "sin-cupo":
            print(f"\n[google] SIN CUPO: el proyecto de esta clave no tiene crédito.")
            print(f"[google] Se generaron {hechas} imágenes antes de agotarse.")
            print("[google] Crea una clave en un proyecto NUEVO (nivel gratuito) en")
            print("[google] https://aistudio.google.com/apikey y vuelve a ejecutar:")
            print("[google] reanuda solo las que falten.")
            sys.exit(2)
        if estado == "ok":
            hechas += 1
        else:
            fallidas.append(bi)
            print(f"[google] compás {bi} ({b['t']:.0f}s) FALLÓ: «{q[:40]}»")
        if hechas and hechas % 10 == 0:
            transcurrido = time.time() - t0
            restantes = len(beats) - len(ya) - hechas
            print(f"[google] {hechas} listas · {transcurrido/hechas:.0f}s c/u · "
                  f"faltan ~{restantes*transcurrido/hechas/60:.0f} min")

    print(f"[google] TOTAL: {hechas} generadas, {len(fallidas)} fallidas "
          f"en {(time.time()-t0)/60:.0f} min")
    if fallidas:
        print(f"[google] compases sin imagen: {fallidas}")
        print("[google] vuelve a ejecutar el mismo comando: reanuda solo las que faltan")


if __name__ == "__main__":
    main()

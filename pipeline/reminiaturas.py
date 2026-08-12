#!/usr/bin/env python3
"""Rehace las miniaturas de los videos ya publicados y, si se pide, las sube.

Uso: python3 reminiaturas.py                     # rostros con el generador gratuito
     python3 reminiaturas.py --desde <zip|dir>   # rostros hechos en Google Flow
     python3 reminiaturas.py --subir             # además las pone en YouTube

--desde existe porque el generador gratuito NO respeta la edad: pedidas caras de
setenta años con arrugas, devuelve caras jóvenes; pedido un trompo en la mano, no
lo pone. Para escenas sirve; para retratos con edad y expresión concretas, no. Las
seis caras se hacen en Flow (0 créditos, una sola pegada de
output/_miniaturas/bloque_flow.txt) y esta opción las recoge de la descarga.

POR QUÉ
El CTR medido del video 5 fue 1,4% cuando lo sano son 4-10%. Las cinco portadas
eran la misma plantilla: escena ancha, filtro vintage que apaga, banda oscura
abajo y texto crema centrado. Sin rostro y sin pregunta. Cambiar la miniatura de
un video ya publicado es gratis, no reinicia nada y se puede deshacer: es la
prueba más barata que tenemos.

Antes de subir nada guarda la miniatura actual en output/_miniaturas/previas/,
para poder volver atrás si el cambio empeora las cosas.
"""
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import requests
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
DATOS = ROOT / "data" / "miniaturas.json"
SALIDA = ROOT / "output" / "_miniaturas"


def cliente():
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    c = Credentials.from_authorized_user_file(str(ROOT / "config" / "token.json"))
    if c.expired and c.refresh_token:
        c.refresh(Request())
    return build("youtube", "v3", credentials=c)


def guardar_previa(yt, vid: str, destino: Path):
    if destino.exists():
        return
    r = yt.videos().list(part="snippet", id=vid).execute()["items"][0]
    urls = r["snippet"]["thumbnails"]
    mejor = max(urls.values(), key=lambda t: t.get("width", 0))["url"]
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_bytes(requests.get(mejor, timeout=60).content)
    print(f"   copia de seguridad → {destino.name}")


def recoger_de_flow(origen: Path, datos):
    """Copia las caras descargadas de Flow a <slug>-rostro.jpg.

    Flow numera por orden de descarga y a veces ignora el número que se le pidió,
    así que primero se busca el número de tres cifras dentro del nombre y, si no
    aparece en ninguno, se reparte por orden alfabético avisándolo.
    """
    import zipfile
    if origen.suffix.lower() == ".zip":
        crudo = SALIDA / "_flow_crudo"
        shutil.rmtree(crudo, ignore_errors=True)
        crudo.mkdir(parents=True)
        with zipfile.ZipFile(origen) as z:
            z.extractall(crudo)
        origen = crudo

    imgs = sorted(p for p in origen.rglob("*")
                  if p.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp"))
    print(f"[miniaturas] {len(imgs)} imágenes en {origen}")

    por_numero = {}
    for p in imgs:
        m = re.search(r"(\d{3})", p.name)
        if m and int(m.group(1)) < len(datos):
            por_numero.setdefault(int(m.group(1)), p)

    if len(por_numero) < len(datos):
        print(f"[miniaturas] ⚠️  solo {len(por_numero)}/{len(datos)} traían número "
              f"reconocible; el resto se asigna por orden de archivo")
        libres = [p for p in imgs if p not in por_numero.values()]
        for i in range(len(datos)):
            if i not in por_numero and libres:
                por_numero[i] = libres.pop(0)

    for i, v in enumerate(datos):
        if i in por_numero:
            destino = SALIDA / f"{v['slug']}-rostro.jpg"
            Image.open(por_numero[i]).convert("RGB").save(destino, quality=95)
            print(f"   {i:03d} → {v['slug']}  ({por_numero[i].name})")
        else:
            print(f"   {i:03d} → {v['slug']}  SIN IMAGEN")


def main():
    args = sys.argv[1:]
    subir = "--subir" in args
    desde = None
    if "--desde" in args:
        k = args.index("--desde")
        desde = Path(args[k + 1]).expanduser().resolve()

    datos = json.loads(DATOS.read_text())["videos"]
    SALIDA.mkdir(parents=True, exist_ok=True)

    if desde:
        recoger_de_flow(desde, datos)

    yt = cliente() if subir else None

    for v in datos:
        rostro = SALIDA / f"{v['slug']}-rostro.jpg"
        # los videos aún sin publicar llevan la miniatura en su propia carpeta
        mini = (ROOT / v["job"] / "miniatura.jpg") if v.get("job") else SALIDA / f"{v['slug']}.jpg"
        print(f"\n── {v['slug']} · {v['titulo_actual'][:44]}")

        if not rostro.exists():
            r = subprocess.run([sys.executable, str(ROOT / "pipeline" / "imagen.py"),
                                v["rostro"], str(rostro),
                                "--estilo", "acuarela", "--semilla", str(v["semilla"])])
            if r.returncode != 0:
                print("   sin rostro, la salto")
                continue

        subprocess.run([sys.executable, str(ROOT / "pipeline" / "thumbnail.py"),
                        str(rostro), v["texto"], str(mini), "--lado", v["lado"]],
                       check=True)

        if subir and v.get("id"):
            guardar_previa(yt, v["id"], SALIDA / "previas" / f"{v['slug']}.jpg")
            yt.thumbnails().set(videoId=v["id"], media_body=str(mini)).execute()
            print(f"   ✅ publicada en https://youtu.be/{v['id']}")
        elif subir:
            print("   (sin publicar todavía: la miniatura queda lista en su carpeta)")

    print(f"\n[miniaturas] listas en {SALIDA}")
    if not subir:
        print("[miniaturas] revísalas y luego: python3 pipeline/reminiaturas.py --subir")


if __name__ == "__main__":
    main()

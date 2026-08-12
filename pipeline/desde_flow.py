#!/usr/bin/env python3
"""Toma el zip descargado de Google Flow y deja el video listo para publicar.

Uso: python3 desde_flow.py <carpeta_job> <zip_de_flow>

Qué hace, en orden:
 1. Extrae el zip y localiza las imágenes
 2. Las renombra al formato que usa assemble (b###_t#######_) leyendo el número
    de tres cifras que el agente de Flow puso en cada archivo y cruzándolo con
    mapa_compases.json para saber en qué segundo va cada una
 3. Avisa qué números faltan (el agente de Flow suele omitir algunos)
 4. Sube la resolución con el modelo neuronal
 5. Ensambla, aplica la capa de texto y pasa el control de calidad

Después solo queda la miniatura y subir.
"""
import json
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def run(script, *args):
    r = subprocess.run([sys.executable, str(ROOT / "pipeline" / script),
                        *[str(a) for a in args]])
    if r.returncode != 0:
        sys.exit(f"[flow] FALLÓ {script}")


def main():
    job = Path(sys.argv[1]).resolve()
    zip_path = Path(sys.argv[2]).resolve()
    mapa = json.loads((job / "mapa_compases.json").read_text())

    crudo = job / "_flow_crudo"
    if crudo.exists():
        shutil.rmtree(crudo)
    crudo.mkdir()
    with zipfile.ZipFile(zip_path) as z:
        z.extractall(crudo)

    imgs = [p for p in crudo.rglob("*") if p.suffix.lower() in (".jpg", ".jpeg", ".png")]
    print(f"[flow] {len(imgs)} imágenes en el zip")

    dest = job / "visuales-gen"
    dest.mkdir(exist_ok=True)
    for f in dest.glob("*"):
        f.unlink()

    colocadas, sin_numero = {}, []
    for p in sorted(imgs):
        m = re.search(r"(\d{3})", p.name)
        if not m or m.group(1) not in mapa:
            sin_numero.append(p.name)
            continue
        num = m.group(1)
        if num in colocadas:          # duplicado: se queda el primero
            continue
        t = mapa[num]
        nuevo = dest / f"b{int(num):03d}_t{int(t*100):07d}_flow{p.suffix.lower()}"
        shutil.copy(p, nuevo)
        colocadas[num] = nuevo.name

    faltan = sorted(set(mapa) - set(colocadas))
    print(f"[flow] colocadas {len(colocadas)}/{len(mapa)}")
    if sin_numero:
        print(f"[flow] sin número reconocible ({len(sin_numero)}): {sin_numero[:6]}")
    if faltan:
        print(f"[flow] FALTAN {len(faltan)} números: {faltan}")
        print("[flow] genera esos en Flow y vuelve a correr esto, "
              "o continúa: las vecinas cubrirán el hueco")

    if len(colocadas) < 50:
        sys.exit("[flow] muy pocas imágenes para armar el video")

    run("nitidez.py", dest)
    run("assemble.py", job / "voz.mp3", dest, job / "final-limpio.mp4")
    run("overlay_text.py", job)
    subprocess.run([sys.executable, str(ROOT / "pipeline" / "quality_gate.py"), str(job)])
    print(f"\n[flow] ✅ listo para revisar: {job / 'final.mp4'}")


if __name__ == "__main__":
    main()

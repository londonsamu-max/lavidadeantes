#!/usr/bin/env python3
"""FLUJO COMPLETO: produce el video, genera miniatura y (opcional) sube a YouTube.

Uso:
  python3 flow.py output/<slug>/            # produce + miniatura (revisión local)
  python3 flow.py output/<slug>/ --subir    # además sube a YouTube como PRIVADO

Requiere en la carpeta (los escribe Claude, el cerebro):
  guion.txt, visuales.json, metadata.json
metadata.json puede incluir "miniatura": {"imagen": "visuales/xxx.jpg", "texto": "LÍNEA 1|LÍNEA 2"}
"""
import json
import subprocess
import sys
from pathlib import Path

PIPELINE = Path(__file__).resolve().parent


def run(script, *args):
    r = subprocess.run([sys.executable, str(PIPELINE / script), *[str(a) for a in args]])
    if r.returncode != 0:
        sys.exit(f"[flow] FALLO en {script}")


def main():
    job = Path(sys.argv[1]).resolve()
    subir = "--subir" in sys.argv

    # 1) Producción (voz + visuales + ensamblado) — reanudable
    run("produce.py", job)

    # 2) Miniatura
    meta = json.loads((job / "metadata.json").read_text()) if (job / "metadata.json").exists() else {}
    thumb_cfg = meta.get("miniatura", {})
    thumb_out = job / "miniatura.jpg"
    if thumb_cfg and not thumb_out.exists():
        base = job / thumb_cfg["imagen"]
        run("thumbnail.py", base, thumb_cfg.get("texto", meta.get("titulo", "")), thumb_out)

    # 3) Subida (opcional, siempre como PRIVADO)
    if subir:
        run("upload.py", job)
    else:
        print(f"\n[flow] ✅ Listo para REVISIÓN: {job / 'final.mp4'}")
        print(f"[flow] Cuando lo apruebes: python3 pipeline/flow.py {job} --subir")


if __name__ == "__main__":
    main()

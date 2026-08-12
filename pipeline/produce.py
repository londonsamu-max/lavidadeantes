#!/usr/bin/env python3
"""Orquestador: convierte una carpeta de trabajo en un video terminado.

Uso: python3 produce.py output/<slug>/

La carpeta debe contener (los genera Claude en el ciclo del cerebro):
  guion.txt        — narración completa en texto plano
  visuales.json    — plan de búsquedas de imágenes por sección

Produce:
  voz.mp3, visuales/, final.mp4  → listo para revisión humana
"""
import subprocess
import sys
from pathlib import Path

PIPELINE = Path(__file__).resolve().parent


def run(script: str, *args):
    cmd = [sys.executable, str(PIPELINE / script), *[str(a) for a in args]]
    print(f"\n=== {script} ===")
    r = subprocess.run(cmd)
    if r.returncode != 0:
        sys.exit(f"[produce] FALLO en {script}")


def main():
    job = Path(sys.argv[1]).resolve()
    guion = job / "guion.txt"
    plan = job / "visuales.json"
    if not guion.exists() or not plan.exists():
        sys.exit(f"[produce] faltan guion.txt o visuales.json en {job}")

    voz = job / "voz.mp3"
    imgdir = job / "visuales"
    # assemble escribe el video SIN texto; overlay_text lo lee y produce final.mp4.
    # Los nombres deben respetar ese encadenamiento: si assemble escribiera en
    # final.mp4, overlay_text leería el final-limpio.mp4 de una corrida anterior y
    # sobrescribiría el montaje recién hecho.
    limpio = job / "final-limpio.mp4"
    final = job / "final.mp4"

    if not voz.exists():
        # voice_synced genera voz.mp3 + timing.json (imágenes ancladas a su sección)
        run("voice_synced.py", guion, job)
    if not imgdir.exists() or not any(imgdir.glob("*.jpg")):
        run("visuals.py", plan, imgdir)
    # duplica la resolución antes de ensamblar: el generador tope en 1024x576 y
    # ampliar eso a 1920 se veía blando. Cuesta menos de un minuto para 140 imágenes.
    run("nitidez.py", imgdir)
    run("assemble.py", voz, imgdir, limpio)
    run("subtitles.py", job)
    run("overlay_text.py", job)

    print(f"\n[produce] ✅ VIDEO LISTO PARA REVISIÓN: {final}")
    print("[produce] Revísalo y luego súbelo (modo review). Recuerda declarar contenido sintético/IA en YouTube Studio.")


if __name__ == "__main__":
    main()

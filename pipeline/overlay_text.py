#!/usr/bin/env python3
"""Capa de TEXTO sobre el video ya montado (regla de evidencia #16 y #17).

Uso: python3 overlay_text.py <carpeta_job>
Entrada:  final-limpio.mp4 + timing.json + visuales.json + subtitulos.srt
Salida:   final.mp4  (con apertura + rótulo persistente + subtítulos quemados)

Tres capas, porque en audiencia 50+ el texto redundante con la voz MEJORA la
comprensión (Fenesi 2015) — al revés que en público joven, donde distrae:

  1. TARJETA DE APERTURA (5 s): identidad del canal + título del video.
  2. RÓTULO PERSISTENTE (arriba-izquierda): el nombre de la sección se mantiene
     todo lo que dura la sección, discreto. Da estructura y progreso sin dar el
     botón de saltar (los capítulos de YouTube perjudican en contenido narrativo).
  3. SUBTÍTULOS QUEMADOS (abajo): grandes, alto contraste, sin cursivas.
     Quemados y no como pista opcional porque esta audiencia no usa el botón CC.

Se hace en una sola pasada de FFmpeg sobre el video ya concatenado, así que
iterar el diseño del texto NO obliga a re-renderizar los ~100 clips.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFilter, ImageFont

FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
ROOT = Path(__file__).resolve().parent.parent
FONTS = ROOT / "assets" / "fonts"
W, H = 1920, 1080
FPS = 30
# Cero desde el diagnóstico de agosto 2026: la retención se decide en el primer
# minuto (el video 3 caía a 29% en 1:05, el 4 aguantaba 71% con el mismo formato),
# y una tarjeta estática de 5 segundos es un 8% de esa ventana regalado antes de
# decir la primera frase. La identidad del canal ya va en el rótulo de la esquina.
# Ponerlo en >0 vuelve a activar la tarjeta.
APERTURA_S = 0.0

CREMA = (247, 238, 220)
AMBAR = (236, 174, 85)
SEPIA = (38, 26, 18)


def _font(nombre, size):
    return ImageFont.truetype(str(FONTS / nombre), size)


def tarjeta_apertura(titulo: str, destino: Path):
    """Genera la imagen de la tarjeta de apertura, en la línea gráfica del canal."""
    img = Image.new("RGB", (W, H), SEPIA)
    d = ImageDraw.Draw(img)
    for y in range(H):  # gradiente vertical sutil
        t = y / H
        d.line([(0, y), (W, y)], fill=tuple(int(SEPIA[i] + (78 - SEPIA[i]) * t * 0.5) for i in range(3)))
    d = ImageDraw.Draw(img)
    cx, cy = W // 2, H // 2

    # nombre del canal arriba, con filetes
    f_canal = _font("OswaldVariable.ttf", 40)
    d.text((cx, cy - 190), "L A   V I D A   D E   A N T E S", font=f_canal,
           fill=AMBAR, anchor="mm")
    d.line([cx - 430, cy - 145, cx + 430, cy - 145], fill=AMBAR, width=3)

    # título del video, partido en líneas
    palabras, lineas, act = titulo.split(), [], ""
    for p in palabras:
        prueba = f"{act} {p}".strip()
        if len(prueba) > 30 and act:
            lineas.append(act)
            act = p
        else:
            act = prueba
    if act:
        lineas.append(act)
    f_tit = _font("PlayfairDisplay-Bold.ttf", 96 if len(lineas) <= 2 else 78)
    y = cy - 40 - (len(lineas) - 1) * 55
    for ln in lineas:
        d.text((cx, y), ln, font=f_tit, fill=CREMA, anchor="mm")
        y += 112 if len(lineas) <= 2 else 92

    d.line([cx - 430, cy + 215, cx + 430, cy + 215], fill=AMBAR, width=3)
    f_pie = _font("LibreCaslon-Regular.ttf", 40)
    d.text((cx, cy + 268), "Recuerdos de los años 60, 70 y 80", font=f_pie,
           fill=(214, 197, 172), anchor="mm")

    # viñeta + grano, igual que los clips
    mask = Image.new("L", (W, H), 0)
    ImageDraw.Draw(mask).ellipse([-W * .25, -H * .25, W * 1.25, H * 1.25], fill=210)
    mask = mask.filter(ImageFilter.GaussianBlur(W // 6))
    img = Image.composite(img, Image.new("RGB", (W, H), (12, 8, 5)), mask)
    img.save(destino)


def esc(s: str) -> str:
    return s.replace("\\", r"\\\\").replace(":", r"\:").replace("'", r"\\'").replace("%", r"\%")


def main():
    job = Path(sys.argv[1]).resolve()
    limpio = job / "final-limpio.mp4"
    salida = job / "final.mp4"
    if not limpio.exists():
        sys.exit(f"[texto] falta {limpio.name} (renderiza primero con assemble.py)")

    meta = json.loads((job / "metadata.json").read_text()) if (job / "metadata.json").exists() else {}
    titulo = meta.get("titulo", job.name.replace("-", " ").title()).split("|")[0].strip()

    # ── 1. tarjeta de apertura (solo si APERTURA_S > 0) ────────────────
    card_mp4 = None
    if APERTURA_S > 0:
        card_png = job / "_apertura.png"
        tarjeta_apertura(titulo, card_png)
        card_mp4 = job / "_apertura.mp4"
        # leer los parámetros de audio del video principal: el concat demuxer exige
        # que coincidan exactamente (si no, la duración se desajusta)
        probe = subprocess.run([FFMPEG, "-i", str(limpio)], capture_output=True, text=True).stderr
        m_a = re.search(r"Audio:.*?(\d+) Hz, (mono|stereo)", probe)
        hz, canales = (m_a.group(1), m_a.group(2)) if m_a else ("44100", "stereo")
        print(f"[texto] audio del video: {hz} Hz {canales} → la tarjeta lo iguala")
        subprocess.run(
            [FFMPEG, "-y", "-loop", "1", "-i", str(card_png), "-f", "lavfi",
             "-i", f"anullsrc=r={hz}:cl={canales}", "-t", f"{APERTURA_S}",
             "-vf", f"fade=t=in:st=0:d=0.6,fade=t=out:st={APERTURA_S-0.7}:d=0.7,format=yuv420p",
             "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
             "-c:a", "aac", "-b:a", "192k", "-r", str(FPS), str(card_mp4)],
            capture_output=True, check=True)
        print("[texto] tarjeta de apertura lista")
    else:
        print("[texto] sin tarjeta de apertura: el video arranca en la primera frase")

    # ── 2. rótulos persistentes por sección ────────────────────────────
    filtros = []
    timing_f, plan_f = job / "timing.json", job / "visuales.json"
    if timing_f.exists() and plan_f.exists():
        _plan = json.loads(plan_f.read_text())
        if isinstance(_plan, dict):          # formato por compases
            rotulos = {int(k): v for k, v in _plan.get("rotulos", {}).items()}
        else:
            rotulos = {i["seccion"]: i.get("titulo", "") for i in _plan}
        font = str(FONTS / "OswaldVariable.ttf").replace(":", r"\:")
        n = 0
        for t in json.loads(timing_f.read_text()):
            texto = rotulos.get(t["seccion"], "")
            if not texto:
                continue
            # el video queda desplazado por la tarjeta de apertura
            ini, fin = t["start"] + APERTURA_S, t["end"] + APERTURA_S
            ent = f"between(t,{ini:.2f},{fin:.2f})"
            filtros.append(
                f"drawbox=x=52:y=48:w=760:h=74:color=black@0.45:t=fill:enable='{ent}'")
            filtros.append(
                f"drawtext=fontfile='{font}':text='{esc(texto.upper())}':fontsize=44:"
                f"fontcolor=0xF7EEDC@0.96:borderw=2:bordercolor=black@0.75:"
                f"x=76:y=64:enable='{ent}'")
            n += 1
        print(f"[texto] rótulos persistentes: {n} secciones")

    # ── 3. subtítulos quemados ─────────────────────────────────────────
    srt = job / "subtitulos.srt"
    if srt.exists():
        # los subtítulos también se desplazan por la apertura
        srt_shift = job / "_subs_shift.srt"
        subprocess.run([FFMPEG, "-y", "-itsoffset", f"{APERTURA_S}", "-i", str(srt),
                        "-c", "copy", str(srt_shift)], capture_output=True)
        usar = srt_shift if srt_shift.exists() else srt
        estilo = ("FontName=Oswald,FontSize=25,PrimaryColour=&H00F0F0F0,"
                  "OutlineColour=&H00101010,BorderStyle=1,Outline=3,Shadow=1,"
                  "Alignment=2,MarginV=52,Bold=1")
        filtros.append(f"subtitles='{usar}':fontsdir='{FONTS}':force_style='{estilo}'")
        print("[texto] subtítulos quemados: activados")

    # ── render final: apertura + video con capas de texto ──────────────
    vf = ",".join(filtros) if filtros else "null"
    if card_mp4:
        lista = job / "_concat_final.txt"
        lista.write_text(f"file '{card_mp4.name}'\nfile '{limpio.name}'\n")
        entrada = ["-f", "concat", "-safe", "0", "-i", str(lista)]
    else:
        entrada = ["-i", str(limpio)]
    print("[texto] renderizando (esto tarda: re-codifica el video completo)...")
    r = subprocess.run(
        [FFMPEG, "-y", *entrada,
         "-vf", vf, "-c:v", "libx264", "-preset", "veryfast", "-crf", "21",
         "-c:a", "aac", "-b:a", "192k", str(salida)],
        cwd=job, capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"[texto] FALLO: {r.stderr[-600:]}")
    print(f"[texto] ✅ {salida.name} ({salida.stat().st_size/1e6:.0f} MB)")


if __name__ == "__main__":
    main()

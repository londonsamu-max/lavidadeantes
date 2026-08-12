#!/usr/bin/env python3
"""Genera la narración POR SECCIONES para sincronización perfecta con las imágenes.

Uso: python3 voice_synced.py <guion.txt> <outdir>

En vez de generar todo el audio de una vez (lo que causa que las imágenes se
"corran"), divide el guion en secciones (intro + ítems numerados + cierre),
genera el audio de cada una por separado, mide su duración exacta, y escribe:
  - voz.mp3      : narración completa concatenada con pausas naturales
  - timing.json  : [{seccion, start, end}] — dónde cae cada sección en el tiempo

assemble.py usa timing.json para poner las imágenes de la sección N exactamente
durante la narración de la sección N.

Voz: edge-tts (es-MX-JorgeNeural) con ritmo pausado + pausas de 0.35s entre
secciones (regla de evidencia: 135-150 ppm con pausas entre ideas para 50+).
"""
import asyncio
import json
import re
import subprocess
import sys
from pathlib import Path

import edge_tts
import imageio_ffmpeg
from mutagen.mp3 import MP3

FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
ROOT = Path(__file__).resolve().parent.parent
CONFIG = json.loads((ROOT / "config" / "channel-config.json").read_text())
VOICE = CONFIG["voz"]["edge_voice"]
RATE = "-6%"          # un pelín más natural que -8%
PAUSE = 0.38          # silencio entre secciones (respiración natural)

ORDINALES = ["uno", "dos", "tres", "cuatro", "cinco", "seis", "siete", "ocho",
             "nueve", "diez", "once", "doce", "trece", "catorce", "quince",
             "dieciséis", "diecisiete", "dieciocho", "diecinueve", "veinte",
             "veintiuno", "veintidós", "veintitrés", "veinticuatro", "veinticinco"]


def split_sections(text: str):
    """Divide el guion en (seccion, texto).

    Dos convenciones soportadas:
      A) Marcadores explícitos "### Título" al inicio de línea (cualquier formato).
         Se eliminan del texto narrado. Recomendado para F3/F5/F6.
      B) "Número uno.", "Número dos."... (formatos de lista F1).
    """
    text = text.strip()
    marcas = list(re.finditer(r"^###\s*(.+)$", text, re.M))
    if marcas:
        sections = []
        intro = text[: marcas[0].start()].strip()
        if intro:
            sections.append((0, intro))
        for i, m in enumerate(marcas):
            fin = marcas[i + 1].start() if i + 1 < len(marcas) else len(text)
            cuerpo = text[m.end():fin].strip()
            if cuerpo:
                sections.append((i + 1, cuerpo))
        return sections
    ordinales = ["uno", "dos", "tres", "cuatro", "cinco", "seis", "siete", "ocho",
                 "nueve", "diez", "once", "doce", "trece", "catorce", "quince",
                 "dieciséis", "diecisiete", "dieciocho", "diecinueve", "veinte",
                 "veintiuno", "veintidós", "veintitrés", "veinticuatro", "veinticinco"]
    markers = []
    for i, o in enumerate(ordinales, start=1):
        m = re.search(rf"Número\s+{o}\.", text, re.IGNORECASE)
        if m:
            markers.append((i, m.start()))
    if not markers:
        return [(0, text)]
    markers.sort(key=lambda x: x[1])
    sections = []
    intro = text[: markers[0][1]].strip()
    if intro:
        sections.append((0, intro))
    for idx, (num, pos) in enumerate(markers):
        end = markers[idx + 1][1] if idx + 1 < len(markers) else len(text)
        sections.append((num, text[pos:end].strip()))
    last_num, last_text = sections[-1]
    m_out = re.search(r"(Veinticinco cosas\.|Quince oficios\.|En conclusión|Ahora le toca a usted)", last_text)
    if m_out and m_out.start() > 40:
        sections[-1] = (last_num, last_text[: m_out.start()].strip())
        sections.append((last_num + 1, last_text[m_out.start():].strip()))
    return sections


async def synth(text: str, out: Path):
    """Sintetiza y devuelve los tiempos reales de cada palabra.

    edge-tts emite eventos WordBoundary con el offset exacto de cada palabra
    (en unidades de 100 ns). Usarlos da subtítulos perfectamente sincronizados,
    a diferencia de estimar por longitud de texto (las pausas de puntuación y los
    números hablados rompen cualquier estimación proporcional).
    """
    clean = re.sub(r"\s+", " ", text).strip()
    com = edge_tts.Communicate(clean, VOICE, rate=RATE)
    palabras = []
    with open(out, "wb") as f:
        async for chunk in com.stream():
            if chunk["type"] == "audio":
                f.write(chunk["data"])
            elif chunk["type"] in ("SentenceBoundary", "WordBoundary"):
                # edge-tts 7.x emite SentenceBoundary: frase completa con tiempo exacto.
                # La frase es justo la unidad natural del subtítulo.
                palabras.append({
                    "t": chunk["offset"] / 10_000_000,          # 100ns → segundos
                    "d": chunk["duration"] / 10_000_000,
                    "w": chunk["text"],
                })
    return palabras


def make_silence(path: Path, dur: float):
    subprocess.run([FFMPEG, "-y", "-f", "lavfi", "-i",
                    "anullsrc=r=24000:cl=mono", "-t", f"{dur}", "-q:a", "9", str(path)],
                   capture_output=True, check=True)


async def main():
    guion, outdir = Path(sys.argv[1]), Path(sys.argv[2]).resolve()
    outdir.mkdir(parents=True, exist_ok=True)
    parts_dir = outdir / "_voz_parts"
    parts_dir.mkdir(exist_ok=True)

    sections = split_sections(guion.read_text())
    print(f"[voice-sync] {len(sections)} secciones")

    sil = parts_dir / "sil.mp3"
    make_silence(sil, PAUSE)

    timing, concat_lines, t = [], [], 0.0
    todas_palabras = []
    for seccion, texto in sections:
        part = parts_dir / f"s{seccion:02d}.mp3"
        palabras = await synth(texto, part)
        for p in palabras:                      # a tiempo absoluto del video
            todas_palabras.append({"t": round(t + p["t"], 3),
                                   "fin": round(t + p["t"] + p["d"], 3),
                                   "w": p["w"], "seccion": seccion})
        dur = MP3(part).info.length
        timing.append({"seccion": seccion, "start": round(t, 3), "end": round(t + dur, 3)})
        concat_lines.append(f"file '{part.name}'")
        concat_lines.append(f"file '{sil.name}'")
        t += dur + PAUSE
        print(f"[voice-sync] sección {seccion}: {dur:.1f}s  (→ {t:.1f}s)")

    # concatenar todo
    listfile = parts_dir / "list.txt"
    listfile.write_text("\n".join(concat_lines) + "\n")
    voz = outdir / "voz.mp3"
    subprocess.run([FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", str(listfile),
                    "-c", "copy", str(voz)], cwd=parts_dir, capture_output=True, check=True)
    (outdir / "timing.json").write_text(json.dumps(timing, indent=2, ensure_ascii=False))
    (outdir / "palabras.json").write_text(json.dumps(todas_palabras, ensure_ascii=False))
    print(f"[voice-sync] tiempos reales de {len(todas_palabras)} palabras → palabras.json")
    total = MP3(voz).info.length
    print(f"[voice-sync] OK → voz.mp3 ({total/60:.1f} min) + timing.json ({len(timing)} secciones)")


if __name__ == "__main__":
    asyncio.run(main())

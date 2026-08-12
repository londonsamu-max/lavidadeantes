#!/usr/bin/env python3
"""Genera subtítulos .srt precisos a partir del guion + timing.json.

Uso: python3 subtitles.py <carpeta_job>
Produce: subtitulos.srt  → se sube a YouTube como pista de subtítulos.

Por qué SRT propio y no los automáticos de YouTube:
- Los automáticos fallan con nombres propios y regionalismos ("camotero", "ropavejero")
- YouTube indexa la pista subida → mejor SEO
- Regla de evidencia #17: subtítulos grandes y limpios ayudan a los 50+ (presbiacusia)

Método: dentro de cada sección (cuya ventana temporal conocemos por timing.json),
reparte las frases proporcionalmente a su número de caracteres. La voz es de
ritmo constante, así que la aproximación es muy cercana a la realidad.
"""
import json
import re
import sys
from pathlib import Path

MAX_CHARS = 84       # 2 líneas de ~42 caracteres (legible en TV a 3 m)
MIN_DUR = 1.2


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


def to_cues(texto: str):
    """Divide en frases y las agrupa en bloques legibles."""
    frases = re.split(r"(?<=[.:;?!])\s+", re.sub(r"\s+", " ", texto).strip())
    cues, buf = [], ""
    for f in frases:
        if not f:
            continue
        if len(buf) + len(f) + 1 <= MAX_CHARS:
            buf = f"{buf} {f}".strip()
        else:
            if buf:
                cues.append(buf)
            # frase sola demasiado larga → partir por comas
            while len(f) > MAX_CHARS:
                corte = f.rfind(",", 0, MAX_CHARS)
                corte = corte if corte > 40 else f.rfind(" ", 0, MAX_CHARS)
                cues.append(f[:corte].strip())
                f = f[corte:].lstrip(", ").strip()
            buf = f
    if buf:
        cues.append(buf)
    return cues


def wrap2(s: str) -> str:
    """Parte en máximo 2 líneas equilibradas."""
    if len(s) <= 44:
        return s
    mid = len(s) // 2
    corte = s.rfind(" ", 0, mid + 12)
    if corte < 15:
        corte = mid
    return s[:corte].strip() + "\n" + s[corte:].strip()


def ts(t: float) -> str:
    h, rem = divmod(max(t, 0), 3600)
    m, s = divmod(rem, 60)
    return f"{int(h):02d}:{int(m):02d}:{s:06.3f}".replace(".", ",")


def cues_desde_palabras(bloques, max_chars=MAX_CHARS):
    """Convierte los bloques con tiempo real del TTS en subtítulos legibles.

    edge-tts entrega frases completas con su tiempo exacto. Si una frase excede el
    ancho legible, se parte en trozos repartiendo su duración proporcionalmente
    DENTRO de la frase — un error de décimas, no de segundos como al estimar por
    secciones enteras.
    """
    cues = []
    for b in bloques:
        texto = re.sub(r"\s+", " ", b["w"]).strip()
        if not texto:
            continue
        ini, fin = b["t"], b["fin"]
        if len(texto) <= max_chars:
            cues.append({"t": ini, "fin": fin, "texto": texto})
            continue
        # partir por comas o espacios respetando el ancho máximo
        trozos, resto = [], texto
        while len(resto) > max_chars:
            corte = resto.rfind(",", 0, max_chars)
            if corte < max_chars * 0.5:
                corte = resto.rfind(" ", 0, max_chars)
            if corte <= 0:
                corte = max_chars
            trozos.append(resto[:corte + 1].strip())
            resto = resto[corte + 1:].strip()
        if resto:
            trozos.append(resto)
        total = sum(len(t) for t in trozos) or 1
        t = ini
        for tr in trozos:
            d = (fin - ini) * len(tr) / total
            cues.append({"t": t, "fin": min(t + d, fin), "texto": tr})
            t += d
    return cues


def main():
    job = Path(sys.argv[1]).resolve()
    pal_f = job / "palabras.json"

    lineas, n = [], 0
    if pal_f.exists():
        # ── ruta buena: tiempos REALES por palabra ──
        palabras = json.loads(pal_f.read_text())
        for c in cues_desde_palabras(palabras):
            n += 1
            lineas.append(f"{n}\n{ts(c['t'])} --> {ts(c['fin'])}\n{wrap2(c['texto'])}\n")
        print(f"[subs] tiempos REALES del TTS ({len(palabras)} palabras)")
    else:
        # ── respaldo: estimación proporcional por sección ──
        guion = (job / "guion.txt").read_text()
        timing = json.loads((job / "timing.json").read_text())
        windows = {t["seccion"]: (t["start"], t["end"]) for t in timing}
        for seccion, texto in split_sections(guion):
            if seccion not in windows:
                continue
            start, end = windows[seccion]
            cues = to_cues(texto)
            if not cues:
                continue
            total_chars = sum(len(c) for c in cues)
            span = max(end - start, MIN_DUR * len(cues))
            t = start
            for c in cues:
                dur = max(span * len(c) / total_chars, MIN_DUR)
                n += 1
                lineas.append(f"{n}\n{ts(t)} --> {ts(min(t + dur, end))}\n{wrap2(c)}\n")
                t += dur
        print("[subs] AVISO: sin palabras.json, tiempos ESTIMADOS (menos precisos)")

    out = job / "subtitulos.srt"
    out.write_text("\n".join(lineas), encoding="utf-8")
    print(f"[subs] OK → {out.name} ({n} subtítulos)")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""SEMÁFORO DE CALIDAD — se ejecuta antes de publicar. Modo desatendido.

Uso: python3 quality_gate.py <carpeta_job>
Salida: quality-report.json + código de salida
        0 = VERDE  (publicar)
        1 = ROJO   (NO publicar — hay que arreglar)

Como el canal publica sin revisión humana, este filtro es la última defensa.
Ante la duda, ROJO: es mucho más barato no publicar un video que publicar uno malo
(la política de "contenido inauténtico" de 2026 puede costar el canal entero).

Los chequeos visuales (¿la imagen es de época? ¿es pertinente?) NO están aquí:
los hace Claude mirando frames extraídos, porque requieren juicio, no reglas.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

import imageio_ffmpeg
from mutagen.mp3 import MP3

FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
ROOT = Path(__file__).resolve().parent.parent

MIN_PALABRAS = 3000

# Reglas del arranque. ~145 palabras por minuto → 75 palabras ≈ los primeros 30 s.
PALABRAS_ARRANQUE = 75
# Los números van escritos con letra porque los lee un sintetizador de voz, así que
# no basta con buscar dígitos.
DATO_CONCRETO = (
    r"\b\d[\d.,]*\b|"
    r"\b(mil|millón|millones|cien|ciento|cientos|docena|"
    r"uno|dos|tres|cuatro|cinco|seis|siete|ocho|nueve|diez|once|doce|trece|catorce|"
    r"quince|dieciséis|diecisiete|dieciocho|diecinueve|veinte|treinta|cuarenta|"
    r"cincuenta|sesenta|setenta|ochenta|noventa|novecientos|por ciento|pesos|centavos)\b"
)
PROMESA = (
    r"\b(vamos a|le voy a|voy a contarle|le digo|en los próximos minutos|"
    r"hoy vamos|aquí va|se lo voy a|le va a quedar|para que no se la pierda|"
    r"no se la pierda|al final de este video)\b"
)
# El freno tiene que frenar AL ESPECTADOR. «Todavía no pasa nadie» o «antes de
# que amanezca» son ambiente, no freno: se exige la forma dirigida a la persona.
FRENO = (
    r"\b(espere|espérese|espéreme|no se me vaya|no se vaya|deténgase|aguarde|"
    r"quédese|no saque|todavía no se vaya|antes de que se vaya|"
    r"antes de que (me )?diga|un momento)\b"
)
# El arranque tiene que hablarLE al espectador, no describir un ambiente.
# Video 3 («Son las seis y media de la mañana...») retuvo 9,4%; los que abren
# dirigiéndose a la persona retienen 20-28%. Marcadores de 2ª persona formal.
SEGUNDA_PERSONA = (
    r"¿|\b(usted|ustedes|imagínese|fíjese|acuérdese|recuerde|mire|oiga|piense|"
    r"se acuerda|le voy|le digo|le va|le tengo|dígame|su casa|su calle|su barrio)\b"
)
# «Pedir suscripción al inicio: el error de mayor coste» (REGLAS-VIRALIZACION).
# Solo después del minuto 10. A 145 ppm, 10 min ≈ 1.450 palabras.
PALABRAS_10_MIN = 1450
DUR_MIN_S, DUR_MAX_S = 18 * 60, 32 * 60
MIN_IMGS_SECCION = 4
MAX_SOLAPE_TEMAS = 3

# Política YouTube 16-jul-2026: voz IA no puede dar consejo de salud/finanzas/legal.
# Buscamos formulaciones PRESCRIPTIVAS, no menciones históricas ("el remedio que usaba
# la abuela" es historia; "tome esto para bajar la presión" es consejo médico).
PATRONES_PROHIBIDOS = [
    (r"\b(tome|tomen|beba|aplique|use)\s+\w+\s+(para|si tiene)\s+(la |el |los |las )?"
     r"(presión|diabetes|dolor|cáncer|artritis|colesterol|ansiedad)", "consejo médico"),
    (r"\b(cura|curar|sana|sanar|alivia)\s+(el |la |los |las )?"
     r"(cáncer|diabetes|artritis|presión|covid)", "afirmación médica"),
    (r"\b(invierta|invertir|compre acciones|criptomoneda|bitcoin|rendimiento garantizado|"
     r"multiplicar su dinero)\b", "consejo financiero"),
    (r"\b(demande|denuncie|proceso legal|abogado le recomienda)\b", "consejo legal"),
]


def dur_video(p: Path) -> float:
    r = subprocess.run([FFMPEG, "-i", str(p)], capture_output=True, text=True)
    m = re.search(r"Duration: (\d+):(\d+):(\d+)", r.stderr)
    return int(m.group(1)) * 3600 + int(m.group(2)) * 60 + int(m.group(3)) if m else 0


def main():
    job = Path(sys.argv[1]).resolve()
    fallos, avisos, datos = [], [], {}

    # ── 1. guion: longitud ────────────────────────────────────────────
    guion_f = job / "guion.txt"
    if not guion_f.exists():
        fallos.append("no existe guion.txt")
        texto = ""
    else:
        texto = guion_f.read_text()
        palabras = len(texto.split())
        datos["palabras"] = palabras
        if palabras < MIN_PALABRAS:
            fallos.append(f"guion corto: {palabras} palabras (mínimo {MIN_PALABRAS})")

    # ── 1b. el arranque: los primeros 30 segundos ─────────────────────
    # De los datos del canal (agosto 2026): el video 3 abría contemplando un
    # ambiente y caía al 29% en 1:05; el video 4 abría con una cifra dura, un
    # freno y una promesa, y a esa misma altura conservaba el 71%. Mismo formato,
    # misma voz, mismas imágenes. La diferencia entera estaba en el primer minuto.
    if texto:
        arranque = " ".join(texto.split()[:PALABRAS_ARRANQUE])
        datos["arranque"] = arranque[:180]
        if not re.search(DATO_CONCRETO, arranque, re.IGNORECASE):
            fallos.append("ARRANQUE sin dato concreto: los primeros 30 s no traen "
                          "ninguna cifra, fecha ni cantidad verificable")
        if not re.search(PROMESA, arranque, re.IGNORECASE):
            fallos.append("ARRANQUE sin promesa explícita: no dice qué va a recibir "
                          "el espectador si se queda")
        # El freno era aviso y por ahí se coló el video 3 (9,4% de retención):
        # cumplía dato y promesa. La REGLA DURA pide las TRES cosas, y el único
        # video que retuvo bien (28%) llevaba las tres. Ahora es fallo.
        if not re.search(FRENO, arranque, re.IGNORECASE):
            fallos.append("ARRANQUE sin freno («espere», «no se me vaya», «antes de "
                          "que...»): el único arranque que retuvo bien lo llevaba")
        if not re.search(SEGUNDA_PERSONA, arranque, re.IGNORECASE):
            avisos.append("ARRANQUE contemplativo: los primeros 30 s no se dirigen "
                          "al espectador (ni «usted», ni pregunta, ni «fíjese»). "
                          "Así abría el video 3 y retuvo 9,4%")

    # ── 1c. ritmo y CTAs en el resto del guion ─────────────────────────
    if texto:
        pal = texto.split()
        # Suscripción antes del minuto 10 = el error de mayor coste documentado
        primeros_10min = " ".join(pal[:PALABRAS_10_MIN]).lower()
        if re.search(r"suscr[ií]b", primeros_10min):
            fallos.append("CTA de suscripción antes del minuto 10: moverla al final "
                          "o después del minuto 10 (REGLAS-VIRALIZACION)")
        # Re-ganchos: una pregunta directa cada 2-3 min sostiene la retención
        # media. A 145 ppm son ~400 palabras; se exige 1 por cada 600 (laxo).
        preguntas = texto.count("¿")
        datos["preguntas_directas"] = preguntas
        if len(pal) >= 1000 and preguntas < len(pal) // 600:
            avisos.append(f"pocos re-ganchos: {preguntas} preguntas directas en "
                          f"{len(pal)} palabras (se espera ≥{len(pal)//600}, una "
                          f"cada ~4 min)")
        # El cierre debe sembrar la pregunta de memoria para comentarios
        if "¿" not in " ".join(pal[-200:]):
            avisos.append("cierre sin pregunta de memoria: los últimos ~80 s no "
                          "preguntan nada al espectador (los comentarios nacen ahí)")

    # ── 2. política de contenido (lo que puede costar el canal) ───────
    for patron, etiqueta in PATRONES_PROHIBIDOS:
        m = re.search(patron, texto, re.IGNORECASE)
        if m:
            fallos.append(f"POLÍTICA — posible {etiqueta}: «{m.group(0)[:60]}»")

    # ── 3. video: existe y dura lo correcto ───────────────────────────
    final = job / "final.mp4"
    if not final.exists():
        fallos.append("no existe final.mp4")
    else:
        d = dur_video(final)
        datos["duracion_s"] = d
        datos["duracion"] = f"{int(d//60)}:{int(d%60):02d}"
        if not (DUR_MIN_S <= d <= DUR_MAX_S):
            fallos.append(f"duración fuera de rango: {datos['duracion']} (debe ser 18-32 min)")
        datos["tamano_mb"] = round(final.stat().st_size / 1e6)

    # ── 4. audio íntegro y acorde al video ────────────────────────────
    voz = job / "voz.mp3"
    if voz.exists() and final.exists():
        dv = MP3(voz).info.length
        datos["voz_s"] = round(dv)
        if abs(dv - datos.get("duracion_s", 0)) > 90:
            fallos.append(f"desfase voz/video: voz {dv/60:.1f} min vs video {datos['duracion']}")

    # ── 5. imágenes suficientes (evita secciones estáticas) ─
    # Dos convenciones: visuales-gen/ con nombres b###_t#######_ (generadas, por
    # compás) y visuales/ con nombres ###_sNN_ (buscadas, por sección). Se cuentan
    # ambas: mirar solo una daba un ROJO falso cuando el video usaba la otra.
    vis = job / "visuales-gen"
    if not vis.exists():
        vis = job / "visuales"
    if vis.exists():
        por_sec, compases = {}, 0
        for f in vis.glob("*.jpg"):
            m = re.search(r"_s(\d+)_", f.name)
            if m:
                por_sec[int(m.group(1))] = por_sec.get(int(m.group(1)), 0) + 1
            elif re.match(r"b\d{3}_t\d{7}_", f.name):
                compases += 1
        datos["imagenes"] = sum(por_sec.values()) + compases
        pobres = [s for s, n in por_sec.items() if n < MIN_IMGS_SECCION]
        if pobres:
            avisos.append(f"secciones con menos de {MIN_IMGS_SECCION} imágenes: {sorted(pobres)}")
        if datos["imagenes"] < 50:
            fallos.append(f"muy pocas imágenes en total: {datos['imagenes']}")

    # ── 6. anti-repetición: solape de temas con lo ya publicado ───────
    reg = ROOT / "data" / "registro-contenido.json"
    if reg.exists() and texto:
        previos = set()
        for v in json.loads(reg.read_text()).get("videos", []):
            previos.update(t.lower() for t in v.get("items_usados", []))
        repes = [t for t in previos if t in texto.lower()]
        datos["temas_repetidos"] = len(repes)
        if len(repes) > MAX_SOLAPE_TEMAS:
            fallos.append(f"solape con videos previos: {len(repes)} temas ya usados {repes[:6]}")

    # ── 7. metadata lista para publicar ───────────────────────────────
    meta_f = job / "metadata.json"
    if not meta_f.exists():
        fallos.append("no existe metadata.json")
    else:
        meta = json.loads(meta_f.read_text())
        for campo in ("titulo", "descripcion", "tags"):
            if not meta.get(campo):
                fallos.append(f"metadata sin {campo}")
        t = meta.get("titulo", "")
        datos["titulo"] = t
        if len(t) > 100:
            fallos.append(f"título demasiado largo: {len(t)} caracteres")
        # regla de viralización: sin MAYÚSCULAS gritadas en documental
        gritos = [w for w in t.split() if len(w) > 3 and w.isupper()]
        if len(gritos) > 1:
            avisos.append(f"título con varias palabras en mayúsculas: {gritos}")
        # 25 lee como "inventado para el título"; 23, 17, 14 leen como reales.
        # Las décadas («los años 70») no cuentan: no son conteos de lista.
        redondos = [m.group(1) for m in re.finditer(r"\b(\d{2,3})\b", t)
                    if int(m.group(1)) % 5 == 0
                    and not re.search(r"años\s*['’]?$", t[:m.start()], re.IGNORECASE)]
        if redondos:
            avisos.append(f"número redondo en el título {redondos}: los no redondos "
                          f"(23, 17, 14) leen como reales")

    # ── 8. miniatura ──────────────────────────────────────────────────
    if not (job / "miniatura.jpg").exists():
        avisos.append("sin miniatura.jpg (YouTube pondrá un frame automático)")

    # ── veredicto ─────────────────────────────────────────────────────
    verde = not fallos
    rep = {"job": job.name, "veredicto": "VERDE" if verde else "ROJO",
           "fallos": fallos, "avisos": avisos, "datos": datos}
    (job / "quality-report.json").write_text(json.dumps(rep, indent=2, ensure_ascii=False))

    print(f"\n{'🟢 VERDE — publicar' if verde else '🔴 ROJO — NO publicar'}   [{job.name}]")
    for k, v in datos.items():
        print(f"   {k}: {v}")
    for f in fallos:
        print(f"   ❌ {f}")
    for a in avisos:
        print(f"   ⚠️  {a}")
    sys.exit(0 if verde else 1)


if __name__ == "__main__":
    main()

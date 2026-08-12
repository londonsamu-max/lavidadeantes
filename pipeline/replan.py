#!/usr/bin/env python3
"""Reancla el plan de compases cuando cambia el guion, sin tirar las imágenes.

Uso: python3 replan.py <carpeta_job> [carpeta_imagenes]

POR QUÉ EXISTE
Cambiar el arranque de un guion ya producido mueve TODOS los tiempos: la voz dura
otra cosa y cada imagen quedaría desfasada respecto a la frase que ilustra. Pero
el cuerpo del guion no cambió, así que las imágenes del cuerpo siguen siendo
válidas: lo único que hay que hacer es volver a calcular en qué segundo va cada
una. Regenerarlas todas sería tirar horas de trabajo por un cambio de treinta
segundos.

Necesita en la carpeta:
  timing-viejo.json / visuales-viejo.json  — cómo era antes
  timing.json                              — cómo quedó tras regenerar la voz

Hace:
  1. saca de cada sección su lista de prompts (el ciclo que se repetía)
  2. reparte compases sobre la nueva duración de cada sección, con el mismo ritmo
  3. renombra las imágenes existentes a su nuevo b###_t####### emparejando por
     prompt dentro de la sección
  4. escribe visuales.json nuevo y dice qué compases quedaron sin imagen
"""
import json
import shutil
import sys
from pathlib import Path

RITMO = 8.9        # segundos por imagen; el mismo que traía el plan original


def compases_por_seccion(beats, timing):
    """{seccion: [prompts en el orden en que aparecen, sin repetir]}"""
    ciclos = {}
    for s in timing:
        dentro = [b["q"] for b in beats if s["start"] <= b["t"] < s["end"]]
        ciclos[s["seccion"]] = list(dict.fromkeys(dentro))
    return ciclos


def main():
    job = Path(sys.argv[1]).resolve()
    imgdir = Path(sys.argv[2]).resolve() if len(sys.argv) > 2 else job / "visuales-gen"

    viejo_plan = json.loads((job / "visuales-viejo.json").read_text())
    viejo_t = json.loads((job / "timing-viejo.json").read_text())
    nuevo_t = json.loads((job / "timing.json").read_text())

    viejos_beats = viejo_plan["beats"]
    ciclos = compases_por_seccion(viejos_beats, viejo_t)

    # qué imagen ilustra cada prompt viejo (puede haber varias por prompt repetido)
    por_prompt = {}
    for i, b in enumerate(viejos_beats):
        arch = next(iter(imgdir.glob(f"b{i:03d}_*")), None)
        if arch:
            por_prompt.setdefault(b["q"], []).append(arch)

    nuevos, faltan, renombres = [], [], []
    usadas = {q: 0 for q in por_prompt}

    for s in nuevo_t:
        ciclo = ciclos.get(s["seccion"]) or ["1970s Mexican primary school classroom"]
        dur = s["end"] - s["start"]
        n = max(1, round(dur / RITMO))
        paso = dur / n
        for k in range(n):
            q = ciclo[k % len(ciclo)]
            t = round(s["start"] + k * paso, 2)
            idx = len(nuevos)
            nuevos.append({"t": t, "q": q, "n": 1})
            disponibles = por_prompt.get(q, [])
            usada = usadas.get(q, 0)
            if usada < len(disponibles):
                renombres.append((disponibles[usada], idx, t))
                usadas[q] = usada + 1
            else:
                # sin imagen libre: se reutiliza una del mismo prompt si existe,
                # y si no, queda para generar
                if disponibles:
                    renombres.append((disponibles[usada % len(disponibles)], idx, t))
                else:
                    faltan.append(idx)

    # renombrar en un directorio limpio para no pisarse a sí mismo
    nuevo_dir = imgdir.parent / (imgdir.name + "-reanclado")
    if nuevo_dir.exists():
        shutil.rmtree(nuevo_dir)
    nuevo_dir.mkdir()
    for origen, idx, t in renombres:
        slug = origen.name.split("_", 2)[-1]
        shutil.copy(origen, nuevo_dir / f"b{idx:03d}_t{int(t*100):07d}_{slug}")

    (job / "visuales.json").write_text(json.dumps(
        {"rotulos": viejo_plan.get("rotulos", {}), "beats": nuevos},
        ensure_ascii=False, indent=1))

    print(f"[replan] {len(viejos_beats)} compases viejos → {len(nuevos)} nuevos")
    print(f"[replan] {len(renombres)} imágenes reancladas en {nuevo_dir.name}")
    if faltan:
        print(f"[replan] FALTAN {len(faltan)} compases sin imagen: {faltan}")
        print("[replan] genera con: python3 pipeline/visuals_gen.py "
              f"{job/'visuales.json'} {nuevo_dir} --estilo acuarela")
    else:
        print("[replan] no falta ninguna imagen")


if __name__ == "__main__":
    main()

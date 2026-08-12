#!/usr/bin/env python3
"""Coloca en su compás las imágenes identificadas en las hojas de contactos.

Uso: python3 colocar.py <carpeta_job> <mapa.json> [<carpeta_imagenes>]

El mapa lo escribe quien miró las hojas de contactos. Dos formas, ambas válidas:

    {"0": 7, "1": 3, "2": 11}                 compás → número de la hoja
    {"0": "abc.jpg", "1": "def.jpg"}          compás → nombre de archivo

Los números se traducen con contactos.json (lo deja hoja_contactos.py). Si no
existe, se usa el orden alfabético de la carpeta de imágenes, que es el mismo
con el que se armaron las hojas.

Copia cada imagen a visuales-gen/ con el nombre que espera assemble.py:

    b###_t#######_flow.jpg     ### = compás,  ####### = centésimas de segundo

y avisa QUÉ COMPASES QUEDARON SIN IMAGEN. Eso último es el motivo de que este
paso sea un script y no un copiar y pegar: Flow se salta prompts sin decirlo, y
un hueco silencioso significa que una imagen vecina se estira sobre una parte
del guion a la que no corresponde.
"""
import json
import shutil
import sys
from pathlib import Path

EXTS = (".jpg", ".jpeg", ".png", ".webp")


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    job = Path(sys.argv[1]).resolve()
    mapa_f = Path(sys.argv[2]).resolve()
    origen = Path(sys.argv[3]).resolve() if len(sys.argv) > 3 else job / "_flow_crudo"

    compases_f = job / "mapa_compases.json"
    if not compases_f.exists():
        sys.exit(f"[colocar] falta {compases_f.name}. Genéralo con:\n"
                 f"          python3 pipeline/bloques_flow.py {job}")
    tiempos = json.loads(compases_f.read_text())      # {"000": 12.34, ...}
    mapa = json.loads(mapa_f.read_text())

    # índice número→archivo: el de las hojas si existe, si no el orden alfabético
    indice = {}
    for candidata in (origen / "contactos.json", job / "contactos" / "contactos.json",
                      job / "hojas" / "contactos.json"):
        if candidata.exists():
            indice = json.loads(candidata.read_text())
            print(f"[colocar] índice de las hojas: {candidata}")
            # Las hojas y las imágenes suelen estar en carpetas distintas. No sirve
            # mirar si la carpeta tiene .jpg: la de las hojas tiene los suyos.
            # Lo que decide es si los archivos DEL ÍNDICE están realmente aquí.
            guardado = indice.pop("_origen", None)
            muestra = next((n for k, n in indice.items() if k != "_origen"), None)
            if guardado and muestra and not (origen / muestra).exists():
                if (Path(guardado) / muestra).exists():
                    origen = Path(guardado)
                    print(f"[colocar] imágenes tomadas de {origen}")
            break
    if not indice:
        archivos = sorted([p.name for p in origen.iterdir() if p.suffix.lower() in EXTS])
        indice = {str(i): n for i, n in enumerate(archivos)}
        print(f"[colocar] sin contactos.json: uso el orden alfabético ({len(indice)} imágenes)")

    destino = job / "visuales-gen"
    destino.mkdir(exist_ok=True)

    colocadas, sin_archivo = {}, []
    for compas, valor in mapa.items():
        clave = f"{int(compas):03d}"
        if clave not in tiempos:
            print(f"[colocar] AVISO: el compás {clave} no existe en el plan, se ignora")
            continue
        nombre = indice.get(str(valor)) if not isinstance(valor, str) else valor
        if not nombre:
            sin_archivo.append(clave)
            continue
        fuente = origen / nombre
        if not fuente.exists():
            coincidencias = list(origen.rglob(nombre))
            if not coincidencias:
                sin_archivo.append(clave)
                continue
            fuente = coincidencias[0]
        t = tiempos[clave]
        nuevo = destino / f"b{int(clave):03d}_t{int(t * 100):07d}_flow{fuente.suffix.lower()}"
        for viejo in destino.glob(f"b{int(clave):03d}_*"):   # sustituye la anterior
            viejo.unlink()
        shutil.copy(fuente, nuevo)
        colocadas[clave] = nuevo.name

    ya_estaban = {p.name[1:4] for p in destino.glob("b*")}
    faltan = sorted(set(tiempos) - ya_estaban)

    print(f"[colocar] colocadas ahora: {len(colocadas)}")
    print(f"[colocar] con imagen en total: {len(ya_estaban)}/{len(tiempos)}")
    if sin_archivo:
        print(f"[colocar] ❌ en el mapa pero sin archivo ({len(sin_archivo)}): {sin_archivo}")
    if faltan:
        print(f"[colocar] ⚠️  COMPASES SIN IMAGEN ({len(faltan)}): {faltan}")
        print("[colocar] genera esos prompts en Flow y vuelve a correr esto, o acepta")
        print("[colocar] que la imagen vecina cubra ese hueco (se estira sobre el guion).")
    else:
        print("[colocar] ✅ todos los compases tienen imagen")
    print(f"\n[colocar] SIGUIENTE:\n"
          f"  python3 pipeline/nitidez.py {destino}\n"
          f"  python3 pipeline/assemble.py {job/'voz.mp3'} {destino} {job/'final-limpio.mp4'}\n"
          f"  python3 pipeline/subtitles.py {job} && python3 pipeline/overlay_text.py {job}\n"
          f"  python3 pipeline/quality_gate.py {job}")


if __name__ == "__main__":
    main()

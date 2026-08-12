#!/usr/bin/env python3
"""Ensambla el video final v2: narración + imágenes Ken Burns + filtro vintage +
fundidos + tarjetas de número + música de fondo.

Uso: python3 assemble.py <voz.mp3> <carpeta_imagenes> <salida.mp4>

Mejoras v2:
- Recorte inteligente (cover+crop): NUNCA estira las imágenes, sin importar su proporción
- Filtro vintage: tono cálido + viñeta + grano de película sutil
- Fundido suave de entrada/salida por clip (transición tipo documental)
- Tarjeta de número (#N) con tipografía Oswald cuando cambia la sección
- Música de fondo (assets/music/*.mp3) mezclada bajo la voz; CC-BY → atribuir en descripción
"""
import json
import random
import re
import subprocess
import sys
from pathlib import Path

import imageio_ffmpeg
from mutagen.mp3 import MP3

FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
ROOT = Path(__file__).resolve().parent.parent
CONFIG = json.loads((ROOT / "config" / "channel-config.json").read_text())
W, H = 1920, 1080
FPS = 30
FADE = 0.45          # segundos de fundido entrada/salida por clip
ZOOM_TOTAL = 0.14    # cuánto zoom a lo largo del clip
NUM_FONT = ROOT / "assets" / "fonts" / "OswaldVariable.ttf"
MUSIC_DIR = ROOT / "assets" / "music"
MUSIC_VOL = 0.10     # volumen de la música bajo la voz


def section_of(path: Path) -> int:
    m = re.search(r"_s(\d+)_", path.name)
    return int(m.group(1)) if m else 0


def _clip_completo(clip: Path) -> bool:
    """¿El clip se terminó de escribir, o quedó a medias?

    El tamaño no basta: si el proceso muere a mitad de un clip, queda un archivo de
    varios MB sin cabecera de duración. assemble lo daba por bueno al reanudar, el
    concat lo tomaba, y el video salía truncado — en el video 5, 11:32 en vez de 20:40.
    Aquí se comprueba que ffmpeg pueda leerle la duración.
    """
    r = subprocess.run([FFMPEG, "-i", str(clip)], capture_output=True, text=True)
    return bool(re.search(r"Duration: \d+:\d+:\d+\.\d+", r.stderr))


def build_clip(img: Path, dur: float, idx: int, show_number, out: Path, label=None):
    """Un clip Ken Burns SIN estirar: escala a cubrir, recorta, luego zoom."""
    frames = max(int(dur * FPS), FPS)
    zoom_in = idx % 2 == 0
    # Las imágenes generadas llegan a 1024x576 (el servicio no entrega más aunque se
    # pida). Todo lo que sigue es ampliación, así que conviene ampliar lo MÍNIMO:
    # basta con 1920*(1+ZOOM_TOTAL) para que el zoom nunca pixele. Antes se ampliaba
    # a 2496 (2.4x desde la fuente) sin necesidad, y eso se veía blando.
    pre_w = int(W * (1 + ZOOM_TOTAL)) // 2 * 2
    pre_h = int(H * (1 + ZOOM_TOTAL)) // 2 * 2
    if zoom_in:
        zexpr = f"1+{ZOOM_TOTAL}*on/{frames}"
    else:
        zexpr = f"{1 + ZOOM_TOTAL}-{ZOOM_TOTAL}*on/{frames}"
    # Paneo sutil alternado además del zoom
    pan = idx % 4
    xexpr = {0: "iw/2-(iw/zoom/2)", 1: "(iw-iw/zoom)*on/{f}", 2: "iw/2-(iw/zoom/2)", 3: "(iw-iw/zoom)*(1-on/{f})"}[pan].format(f=frames)
    yexpr = "ih/2-(ih/zoom/2)"

    vf_parts = [
        # cover + crop = jamás se estira, cualquier proporción de origen.
        # lanczos en vez del bicúbico por defecto: al ampliar casi 2x desde 1024px
        # es donde se gana la poca nitidez que se puede ganar.
        f"scale={pre_w}:{pre_h}:flags=lanczos:force_original_aspect_ratio=increase",
        f"crop={pre_w}:{pre_h}",
        # realce moderado para recuperar el filo que se pierde al ampliar
        "unsharp=5:5:0.8:5:5:0.3",
        f"zoompan=z='{zexpr}':x='{xexpr}':y='{yexpr}':d={frames}:s={W}x{H}:fps={FPS}",
        # look vintage: tono cálido, saturación baja, viñeta suave
        "eq=saturation=0.88:contrast=1.06:brightness=0.02",
        "colorbalance=rm=0.06:gm=0.02:bm=-0.06",
        "vignette=PI/5.5",
        # grano muy fino: a esta resolución un grano fuerte se lee como suciedad
        "noise=alls=2:allf=t",
    ]
    # Rótulo inferior (lower third): número + nombre de la sección.
    # Regla de evidencia #16: el texto redundante con la voz AYUDA a los 50+.
    # Sans-serif condensada, alto contraste, en pantalla ~5.5s (tiempo para leerlo dos veces).
    if False and show_number is not None and NUM_FONT.exists():  # → overlay_text.py
        font = str(NUM_FONT).replace(":", r"\:")
        hold = min(5.5, max(dur - 0.8, 2.5))
        fin, fout = 0.5, 0.6
        alpha = (f"if(lt(t,{fin}),t/{fin},"
                 f"if(gt(t,{hold - fout}),({hold}-t)/{fout},1))")
        # banda oscura de fondo para garantizar contraste
        vf_parts.append(
            f"drawbox=x=0:y=ih-235:w=iw:h=150:color=black@0.62:t=fill:"
            f"enable='lte(t,{hold})'"
        )
        vf_parts.append(
            f"drawtext=fontfile='{font}':text='{show_number}':fontsize=104:"
            f"fontcolor=0xECAE55@1:borderw=2:bordercolor=black@0.7:"
            f"x=96:y=H-215:enable='lte(t,{hold})':alpha='{alpha}'"
        )
        if label:
            safe = (label.upper().replace(":", r"\:").replace("'", r"\\'")
                    .replace("%", r"\%"))
            vf_parts.append(
                f"drawtext=fontfile='{font}':text='{safe}':fontsize=74:"
                f"fontcolor=0xF7EEDC@1:borderw=2:bordercolor=black@0.7:"
                f"x=225:y=H-190:enable='lte(t,{hold})':alpha='{alpha}'"
            )
    fade_out_start = max(dur - FADE, 0)
    vf_parts.append(f"fade=t=in:st=0:d={FADE},fade=t=out:st={fade_out_start:.3f}:d={FADE}")
    vf_parts.append("format=yuv420p")

    r = subprocess.run(
        [FFMPEG, "-y", "-loop", "1", "-i", str(img), "-vf", ",".join(vf_parts),
         "-t", f"{dur:.3f}", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
         "-an", str(out)],
        capture_output=True, text=True,
    )
    return r.returncode == 0, r.stderr


def main():
    audio, imgdir, out = (Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve(),
                          Path(sys.argv[3]).resolve())
    images = sorted([p for p in imgdir.iterdir() if p.suffix.lower() in (".jpg", ".jpeg", ".png")])
    if not images:
        sys.exit("[assemble] no hay imágenes")

    total = MP3(audio).info.length

    # Tres modos de colocar las imágenes en el tiempo, de mejor a peor:
    #   v4 COMPASES  — cada archivo lleva su momento en el nombre (b###_t#######_)
    #   v3 SECCIONES — cada imagen dura la ventana de su sección (timing.json)
    #   v2 UNIFORME  — reparto igual (último recurso)
    timing_file = out.parent / "timing.json"
    tiempos = {}
    for img in images:
        m = re.search(r"_t(\d{7})_", img.name)
        if m:
            tiempos[img.name] = int(m.group(1)) / 100.0

    if tiempos and len(tiempos) == len(images):
        images = sorted(images, key=lambda i: (tiempos[i.name], i.name))
        durations = {}
        for k, img in enumerate(images):
            t0 = tiempos[img.name]
            posteriores = [tiempos[o.name] for o in images[k + 1:] if tiempos[o.name] > t0]
            t1 = posteriores[0] if posteriores else total
            comparten = sum(1 for o in images if tiempos[o.name] == t0)
            durations[img.name] = max((t1 - t0) / comparten, 1.5)
        print(f"[assemble] v4 POR COMPASES · {len(images)} imágenes ancladas a su momento "
              f"exacto · {total/60:.1f} min · media {total/len(images):.1f}s por imagen")
    elif timing_file.exists():
        raw = sorted(json.loads(timing_file.read_text()), key=lambda t: t["start"])
        # ventana de cada sección = desde su start hasta el start de la siguiente
        # (así las pausas entre secciones quedan cubiertas y el video = audio)
        windows = {}
        for idx, t in enumerate(raw):
            nxt = raw[idx + 1]["start"] if idx + 1 < len(raw) else total
            windows[t["seccion"]] = (t["start"], nxt)
        by_sec = {}
        for img in images:
            by_sec.setdefault(section_of(img), []).append(img)
        durations = {}
        for sec, imgs in by_sec.items():
            start, end = windows.get(sec, (0, total))
            per = max(end - start, 1.0) / len(imgs)
            for img in imgs:
                durations[img.name] = per
        print(f"[assemble] v3 SINCRONIZADO · {len(images)} imágenes · {total/60:.1f} min · "
              f"{len(raw)} secciones ancladas a timing.json")
    else:
        per_img = total / len(images)
        durations = {img.name: per_img for img in images}
        print(f"[assemble] v2 · {len(images)} imágenes · {total/60:.1f} min · {per_img:.1f}s/imagen (reparto uniforme)")

    # Rótulos por sección (regla #16: texto redundante ayuda a los 50+)
    labels = {}
    plan_file = out.parent / "visuales.json"
    if plan_file.exists():
        plan = json.loads(plan_file.read_text())
        if isinstance(plan, dict):          # formato por compases
            labels = {int(k): v for k, v in plan.get("rotulos", {}).items()}
        else:                                # formato por secciones
            for item in plan:
                if item.get("titulo"):
                    labels[item["seccion"]] = item["titulo"]
        if labels:
            print(f"[assemble] rótulos en pantalla: {len(labels)} secciones")

    tmp = out.parent / "_clips"
    tmp.mkdir(exist_ok=True)
    clips, prev_section = [], None
    for i, img in enumerate(images):
        clip = tmp / f"clip{i:03d}.mp4"
        sec = section_of(img)
        show = sec if (sec != prev_section and sec > 0) else None
        prev_section = sec
        clips.append(clip)
        if clip.exists() and clip.stat().st_size > 10_000 and _clip_completo(clip):
            continue
        ok, err = build_clip(img, durations[img.name], i, show, clip, labels.get(sec))
        if not ok:
            print(f"[assemble] AVISO clip {i} ({img.name}): {err[-200:]}")
            clips.pop()
        if (i + 1) % 10 == 0:
            print(f"[assemble] clips {i + 1}/{len(images)}")

    concat = tmp / "list.txt"
    concat.write_text("".join(f"file '{c.name}'\n" for c in clips))

    music_files = sorted(MUSIC_DIR.glob("*.mp3")) if MUSIC_DIR.exists() else []
    print(f"[assemble] concatenando + voz{' + música' if music_files else ''}...")
    if music_files:
        music = random.choice(music_files)
        cmd = [FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", str(concat),
               "-i", str(audio), "-stream_loop", "-1", "-i", str(music),
               "-filter_complex",
               f"[1:a]loudnorm=I=-16:TP=-1.5[voz];"
               f"[2:a]volume={MUSIC_VOL},afade=t=in:st=0:d=3[mus];"
               f"[voz][mus]amix=inputs=2:duration=first:dropout_transition=3[a]",
               "-map", "0:v", "-map", "[a]",
               "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", str(out)]
        print(f"[assemble] música: {music.name} (CC-BY — atribuir en la descripción del video)")
    else:
        cmd = [FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", str(concat),
               "-i", str(audio), "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
               "-shortest", str(out)]
    r = subprocess.run(cmd, cwd=tmp, capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"[assemble] FALLO concat: {r.stderr[-400:]}")
    print(f"[assemble] OK → {out} ({out.stat().st_size / 1e6:.0f} MB)")


if __name__ == "__main__":
    main()

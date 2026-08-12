#!/usr/bin/env python3
"""Genera la miniatura del video: rostro a un lado, titular grande al otro.

Uso: python3 thumbnail.py <imagen_base> "<TEXTO|LÍNEA 2|*LÍNEA AMARILLA>" <salida.jpg>
                          [--lado izq|der] [--limpio]

  |   separa líneas
  *   al inicio de una línea la pinta en amarillo (el gancho de la frase)
  --lado  dónde va el panel de texto; el rostro debe quedar en el lado contrario
  --limpio  sin panel ni texto (para probar la imagen sola)

POR QUÉ ESTE DISEÑO
La versión anterior aplicaba el mismo filtro vintage del video (saturación 0.78,
viñeta fuerte) y tapaba con una banda oscura la mitad inferior. Resultado: cinco
miniaturas idénticas, apagadas, sin punto focal — y un CTR medido de 1,4% cuando
lo sano son 4-10%. En una miniatura hay que hacer lo contrario que en el video:
subir saturación y contraste, dejar un rostro grande y libre, y meter el texto en
una sola columna en vez de una banda que se come la imagen.

Reglas aplicadas (docs/REGLAS-VIRALIZACION.md + REGLAS-PRODUCCION-EVIDENCIA.md):
rostro visible (69-80% de los videos que despegan lo llevan), máximo 4 palabras
por línea, tipografía condensada sin cursivas, alto contraste, un solo color de
acento constante para que el suscriptor reconozca el canal.
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parent.parent
W, H = 1280, 720

FUENTE = ROOT / "assets" / "fonts" / "BebasNeue.ttf"
FUENTE_ALT = ROOT / "assets" / "fonts" / "OswaldVariable.ttf"

CREMA = (255, 248, 232)
AMARILLO = (255, 198, 26)      # color de acento del canal — no cambiarlo entre videos
OSCURO = (16, 11, 7)

MARGEN = 56
ANCHO_PANEL = 0.52             # fracción del ancho que ocupa la columna de texto
DESPLAZO = 0.20                # cuánto se corre la imagen hacia el lado del rostro


def recortar_marco(img: Image.Image) -> Image.Image:
    """Quita el margen blanco de papel que deja el estilo acuarela.

    Nano Banana devuelve la acuarela «sobre la hoja», con un borde claro alrededor.
    Sin recortarlo, la miniatura sale con una franja blanca que rompe el diseño.
    """
    gris = img.convert("L")
    an, al = gris.size
    px = gris.load()
    umbral = 236

    def fila_clara(y):
        return sum(px[x, y] > umbral for x in range(0, an, 8)) > (an // 8) * 0.92

    def col_clara(x):
        return sum(px[x, y] > umbral for y in range(0, al, 8)) > (al // 8) * 0.92

    arriba = 0
    while arriba < al // 4 and fila_clara(arriba):
        arriba += 1
    abajo = al - 1
    while abajo > al * 3 // 4 and fila_clara(abajo):
        abajo -= 1
    izq = 0
    while izq < an // 4 and col_clara(izq):
        izq += 1
    der = an - 1
    while der > an * 3 // 4 and col_clara(der):
        der -= 1

    if der - izq < an * 0.5 or abajo - arriba < al * 0.5:
        return img                      # recorte sospechoso: mejor no tocar
    return img.crop((izq, arriba, der + 1, abajo + 1))


def componer(src: Image.Image, lado: str) -> Image.Image:
    """Corre la imagen al lado contrario al texto y rellena el hueco.

    El generador siempre centra al sujeto por más que se le pida lo contrario, así
    que la cara caía justo debajo del titular. En vez de pelearse con el prompt, se
    desplaza la imagen aquí —determinista— y el hueco se cubre con una copia
    ampliada y desenfocada de ella misma, que es lo que hace que no se note el corte.
    """
    fondo = ImageOps.fit(src, (W, H), Image.LANCZOS, centering=(0.5, 0.5))
    fondo = fondo.resize((int(W * 1.25), int(H * 1.25)), Image.LANCZOS)
    fondo = fondo.crop((0, 0, W, H)).filter(ImageFilter.GaussianBlur(26))
    fondo = ImageEnhance.Brightness(fondo).enhance(0.55)

    frente = ImageOps.fit(src, (W, H), Image.LANCZOS)
    dx = int(W * DESPLAZO) * (1 if lado == "izq" else -1)
    # borde difuminado: pegado a hueso se veía una costura vertical nítida
    mascara = Image.new("L", (W, H), 255)
    pluma = ImageDraw.Draw(mascara)
    ancho_pluma = 90
    for i in range(ancho_pluma):
        v = int(255 * i / ancho_pluma)
        borde = i if lado == "izq" else W - 1 - i
        pluma.line([(borde, 0), (borde, H)], fill=v)
    fondo.paste(frente, (dx, 0), mascara)
    return fondo


def realzar(img: Image.Image) -> Image.Image:
    """Lo contrario del filtro del video: más color, más contraste, más nitidez.

    La miniatura compite contra otras veinte en una cuadrícula; el look apagado
    que funciona dentro del video la vuelve invisible fuera de él.
    """
    img = ImageEnhance.Color(img).enhance(1.22)
    img = ImageEnhance.Contrast(img).enhance(1.20)
    img = ImageEnhance.Brightness(img).enhance(1.04)
    img = img.filter(ImageFilter.UnsharpMask(radius=3, percent=90, threshold=3))
    return img


def panel(img: Image.Image, lado: str) -> Image.Image:
    """Degradado horizontal opaco en un lado, transparente en el otro.

    A diferencia de la banda inferior anterior, deja el rostro completamente
    limpio: el degradado muere antes de llegar a él.
    """
    ancho = int(W * ANCHO_PANEL)
    grad = Image.new("L", (W, 1), 0)
    for x in range(W):
        pos = x if lado == "izq" else W - 1 - x
        if pos <= ancho * 0.62:
            v = 236
        elif pos >= ancho:
            v = 0
        else:
            v = int(236 * (1 - (pos - ancho * 0.62) / (ancho * 0.38)))
        grad.putpixel((x, 0), v)
    mascara = grad.resize((W, H))
    sombra = Image.new("RGB", (W, H), OSCURO)
    return Image.composite(sombra, img, mascara)


def ajustar(draw, texto, ruta, ancho_max, desde=132):
    tam = desde
    while tam > 44:
        f = ImageFont.truetype(str(ruta), tam)
        caja = draw.textbbox((0, 0), texto, font=f)
        if caja[2] - caja[0] <= ancho_max:
            return f
        tam -= 4
    return ImageFont.truetype(str(ruta), 44)


def main():
    args = sys.argv[1:]
    lado = "izq"
    if "--lado" in args:
        k = args.index("--lado")
        lado = args[k + 1]
        del args[k:k + 2]
    limpio = "--limpio" in args
    args = [a for a in args if a != "--limpio"]

    base, titular, salida = Path(args[0]), args[1], Path(args[2])

    img = Image.open(base).convert("RGB")
    img = recortar_marco(img)
    img = componer(img, lado)                          # cubre y recorta, nunca estira
    img = realzar(img)

    if not limpio:
        img = panel(img, lado)
        draw = ImageDraw.Draw(img)
        ruta = FUENTE if FUENTE.exists() else FUENTE_ALT
        ancho_texto = int(W * ANCHO_PANEL) - MARGEN * 2

        lineas = []
        for cruda in titular.split("|"):
            cruda = cruda.strip()
            if not cruda:
                continue
            acento = cruda.startswith("*")
            lineas.append((cruda.lstrip("*").strip().upper(), acento))

        medidas = []
        for texto, acento in lineas:
            f = ajustar(draw, texto, ruta, ancho_texto)
            caja = draw.textbbox((0, 0), texto, font=f)
            medidas.append((texto, acento, f, caja[3] - caja[1]))

        interlinea = 18
        alto_total = sum(m[3] for m in medidas) + interlinea * (len(medidas) - 1) + 34
        y = (H - alto_total) // 2
        x = MARGEN if lado == "izq" else W - int(W * ANCHO_PANEL) + MARGEN

        for texto, acento, f, alto in medidas:
            color = AMARILLO if acento else CREMA
            # doble sombra: la miniatura se ve sobre fondos claros y oscuros
            draw.text((x + 5, y + 5), texto, font=f, fill=(0, 0, 0))
            draw.text((x + 2, y + 2), texto, font=f, fill=(0, 0, 0))
            draw.text((x, y), texto, font=f, fill=color)
            y += alto + interlinea

        # regla amarilla: firma visual del canal, la misma en todos los videos.
        # El hueco es generoso a propósito: BebasNeue mide la caja ajustada y los
        # signos de interrogación bajan por debajo de la línea base.
        draw.rectangle([x, y + 24, x + int(ancho_texto * 0.42), y + 36], fill=AMARILLO)

    # marco crema fino: separa la miniatura del fondo blanco de YouTube
    marco = ImageDraw.Draw(img)
    marco.rectangle([0, 0, W - 1, H - 1], outline=CREMA, width=6)

    img.save(salida, quality=94)
    print(f"[thumbnail] OK → {salida} ({W}x{H}, panel {lado})")


if __name__ == "__main__":
    main()

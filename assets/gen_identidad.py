#!/usr/bin/env python3
"""Genera avatar (800x800) y banner (2048x1152) del canal, estilo cartel vintage."""
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent
FONTS = ROOT / "assets" / "fonts"
OUT = ROOT / "assets" / "branding"
OUT.mkdir(exist_ok=True)

# Paleta vintage cálida (alto contraste de luminancia, apta para 50+)
CREMA = (243, 233, 215)
SEPIA_OSCURO = (46, 32, 22)
CAFE = (78, 54, 36)
AMBAR = (196, 138, 62)


def font(name, size):
    return ImageFont.truetype(str(FONTS / name), size)


def grain(img, amount=8):
    noise = Image.effect_noise(img.size, amount).convert("L")
    return Image.composite(img, img.point(lambda p: max(0, p - 12)), noise.point(lambda p: 255 if p > 120 else 0))


def center_text(draw, xy, text, fnt, fill, anchor="mm", tracking=0):
    draw.text(xy, text, font=fnt, fill=fill, anchor=anchor)


def radial_vignette(img, strength=0.55):
    w, h = img.size
    mask = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(mask)
    d.ellipse([-w * 0.25, -h * 0.25, w * 1.25, h * 1.25], fill=int(255 * (1 - strength)))
    mask = mask.filter(ImageFilter.GaussianBlur(w // 6))
    dark = Image.new("RGB", (w, h), SEPIA_OSCURO)
    return Image.composite(img, dark, mask.point(lambda p: 255 - p))


# ============ AVATAR 800x800 ============
av = Image.new("RGB", (800, 800), SEPIA_OSCURO)
d = ImageDraw.Draw(av)
# anillos concéntricos
d.ellipse([28, 28, 772, 772], outline=CREMA, width=6)
d.ellipse([48, 48, 752, 752], outline=AMBAR, width=3)
# sol naciente estilizado (nostalgia/amanecer)
for i, r in enumerate(range(60, 240, 36)):
    d.arc([400 - r, 470 - r, 400 + r, 470 + r], start=180, end=360, fill=AMBAR if i % 2 else CAFE, width=10)
d.line([180, 470, 620, 470], fill=CREMA, width=8)
# texto
f_big = font("PlayfairDisplay-Bold.ttf", 118)
f_small = font("LibreCaslon-Regular.ttf", 54)
center_text(d, (400, 580), "La Vida", f_big, CREMA)
center_text(d, (400, 690), "de Antes", f_small, AMBAR)
av = grain(av)
av.save(OUT / "avatar.png")

# ============ BANNER 2048x1152 ============
bn = Image.new("RGB", (2048, 1152), SEPIA_OSCURO)
d = ImageDraw.Draw(bn)
# gradiente vertical sutil
for y in range(1152):
    t = y / 1152
    c = tuple(int(SEPIA_OSCURO[i] + (CAFE[i] - SEPIA_OSCURO[i]) * t * 0.6) for i in range(3))
    d.line([(0, y), (2048, y)], fill=c)
d = ImageDraw.Draw(bn)

# ZONA SEGURA: centro 1235x338 → caja (406,407)-(1641,745). TODO el texto va ahí.
cx, cy = 1024, 576
# ornamentos horizontales
d.line([cx - 420, cy - 118, cx + 420, cy - 118], fill=AMBAR, width=3)
d.polygon([(cx, cy - 128), (cx + 10, cy - 118), (cx, cy - 108), (cx - 10, cy - 118)], fill=AMBAR)
f_top = font("OswaldVariable.ttf", 40)
center_text(d, (cx, cy - 155), "RECUERDOS  ·  OFICIOS  ·  COSTUMBRES", f_top, AMBAR)
# título principal
f_title = font("PlayfairDisplay-Bold.ttf", 150)
center_text(d, (cx, cy - 10), "La Vida de Antes", f_title, CREMA)
# subtítulo
f_sub = font("LibreCaslon-Regular.ttf", 46)
center_text(d, (cx, cy + 105), "Los años 60, 70 y 80 · como usted los vivió", f_sub, (222, 205, 178))
d.line([cx - 420, cy + 148, cx + 420, cy + 148], fill=AMBAR, width=3)
d.polygon([(cx, cy + 138), (cx + 10, cy + 148), (cx, cy + 158), (cx - 10, cy + 148)], fill=AMBAR)

bn = radial_vignette(bn, strength=0.5)
bn = grain(bn)
bn.save(OUT / "banner.png")
print("OK:", OUT / "avatar.png", OUT / "banner.png")

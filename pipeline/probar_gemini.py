#!/usr/bin/env python3
"""Prueba si la API de Gemini puede generar imágenes con la clave disponible.

Uso: python3 probar_gemini.py [CLAVE]
Si no se pasa clave, la lee de GOOGLE_AI_API_KEY en .env

Responde tres preguntas de una vez:
  1. ¿La clave sirve? (o da 429 limit:0 como las anteriores)
  2. ¿Qué modelos de imagen expone?
  3. ¿Qué resolución entrega? — que es lo que decide si mejora a Pollinations (1024x576)
"""
import base64
import io
import json
import sys
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
MODELOS = [
    "gemini-3-pro-image-preview",
    "gemini-2.5-flash-image",
    "imagen-4.0-generate-001",
]
PROMPT = ("Delicate watercolor with visible paper texture: a mother cooking on a wood "
          "stove in a modest kitchen, a child watching, 1970s Latin America, warm light, no text")


def clave():
    if len(sys.argv) > 1:
        return sys.argv[1].strip()
    f = ROOT / ".env"
    if f.exists():
        for ln in f.read_text().splitlines():
            if ln.startswith("GOOGLE_AI_API_KEY="):
                return ln.split("=", 1)[1].strip()
    return ""


def listar(k):
    r = requests.get("https://generativelanguage.googleapis.com/v1beta/models",
                     params={"key": k}, timeout=60)
    if r.status_code != 200:
        print(f"[gemini] listar modelos → HTTP {r.status_code}: {r.text[:220]}")
        return []
    ms = [m["name"].split("/")[-1] for m in r.json().get("models", [])]
    img = [m for m in ms if "image" in m or "imagen" in m]
    print(f"[gemini] {len(ms)} modelos visibles · con imagen: {img or 'ninguno'}")
    return img


def generar(k, modelo):
    url = (f"https://generativelanguage.googleapis.com/v1beta/models/"
           f"{modelo}:generateContent")
    body = {"contents": [{"parts": [{"text": PROMPT}]}]}
    r = requests.post(url, params={"key": k}, json=body, timeout=180)
    if r.status_code != 200:
        det = r.text[:260].replace("\n", " ")
        print(f"[gemini] {modelo} → HTTP {r.status_code}: {det}")
        return False
    try:
        partes = r.json()["candidates"][0]["content"]["parts"]
    except Exception:
        print(f"[gemini] {modelo} → respuesta sin partes: {r.text[:200]}")
        return False
    for p in partes:
        d = p.get("inlineData") or p.get("inline_data")
        if not d:
            continue
        raw = base64.b64decode(d["data"])
        dest = ROOT / f"prueba_gemini_{modelo[:24]}.png"
        dest.write_bytes(raw)
        try:
            from PIL import Image
            w, h = Image.open(io.BytesIO(raw)).size
            print(f"[gemini] ✅ {modelo} → {w}x{h} ({len(raw)//1024} KB) → {dest.name}")
        except Exception:
            print(f"[gemini] ✅ {modelo} → {len(raw)//1024} KB → {dest.name}")
        return True
    print(f"[gemini] {modelo} → respondió pero sin imagen (solo texto)")
    return False


def main():
    k = clave()
    if not k:
        sys.exit("Falta la clave. Consíguela en https://aistudio.google.com/apikey\n"
                 "Debe empezar con 'AIza'. Luego:  python3 probar_gemini.py TU_CLAVE")
    if not k.startswith("AIza"):
        print(f"[gemini] ⚠️  la clave empieza con '{k[:4]}', no con 'AIza'. "
              "Puede que no sea una clave de la API de Gemini.")
    print(f"[gemini] probando clave {k[:8]}…{k[-4:]}\n")

    disponibles = listar(k)
    candidatos = disponibles + [m for m in MODELOS if m not in disponibles]
    for m in candidatos[:6]:
        if generar(k, m):
            print("\n[gemini] FUNCIONA. Comparación de resolución:")
            print("   Pollinations (actual) : 1024x576  → ampliar 1.9x")
            print("   Google Flow (manual)  : 1376x768  → ampliar 1.4x")
            return
    print("\n[gemini] ningún modelo de imagen respondió con una imagen.")


if __name__ == "__main__":
    main()

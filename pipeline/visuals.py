#!/usr/bin/env python3
"""Descarga visuales para un video: fotos históricas de Wikimedia Commons (dominio
público, sin API key) + video stock de Pexels (si hay PEXELS_API_KEY en .env).

Uso: python3 visuals.py <visuales.json> <carpeta_salida>

visuales.json — lo genera Claude a partir del guion:
[
  {"seccion": 1, "busqueda_wikimedia": "mexican rural life 1950", "busqueda_es": "vida rural mexico"},
  ...
]
Descarga ~N imágenes por sección, nombradas 001_xxx.jpg, 002_xxx.jpg... en orden.
"""
import json
import re
import sys
import time
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
HEADERS = {"User-Agent": "LaVidaDeAntesBot/1.0 (https://commons.wikimedia.org; canal educativo hispano)"}
MIN_W = 800  # descartar imágenes pequeñas
SESSION = requests.Session()


def load_env():
    env = {}
    f = ROOT / ".env"
    if f.exists():
        for line in f.read_text().splitlines():
            if "=" in line and not line.strip().startswith("#"):
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip()
    return env


MAX_YEAR = 1990  # el canal cubre hasta ~1990; nada posterior sirve


def _is_modern(info: dict, title: str) -> bool:
    """True si la imagen es claramente posterior a la época del canal.

    Wikimedia mezcla fotos históricas con actuales (buscar 'iceman' devuelve al
    atleta Wim Hof, 2019). La metadata trae la fecha: la usamos para descartar.
    Si no hay fecha, se acepta (mucho material histórico carece de metadata).
    """
    em = info.get("extmetadata", {}) or {}
    campos = [em.get("DateTimeOriginal", {}).get("value", ""),
              em.get("DateTime", {}).get("value", ""), title]
    for raw in campos:
        texto = re.sub(r"<[^>]+>", " ", str(raw))
        for y in re.findall(r"\b(1[89]\d{2}|20[0-2]\d)\b", texto):
            if int(y) > MAX_YEAR:
                return True
            return False  # primer año encontrado es válido → aceptar
    return False


def wikimedia_search(query: str, limit: int = 6):
    """Busca imágenes en Wikimedia Commons (dominio público / CC)."""
    api = "https://commons.wikimedia.org/w/api.php"
    params = {
        "action": "query", "format": "json", "generator": "search",
        "gsrsearch": f"filetype:bitmap {query}", "gsrnamespace": 6, "gsrlimit": limit * 3,
        "prop": "imageinfo", "iiprop": "url|size|extmetadata", "iiurlwidth": 1600,
    }
    pages = {}
    for attempt in range(3):
        try:
            r = SESSION.get(api, params=params, headers=HEADERS, timeout=30)
            if r.status_code == 429 or (r.status_code == 200 and not r.text.startswith("{")):
                time.sleep(3 * (attempt + 1))
                continue
            r.raise_for_status()
            pages = r.json().get("query", {}).get("pages", {})
            break
        except Exception as e:
            print(f"[visuals] wikimedia intento {attempt + 1} '{query}': {e}")
            time.sleep(3 * (attempt + 1))
    time.sleep(1.2)  # cortesía con la API entre búsquedas
    results = []
    for p in pages.values():
        info = (p.get("imageinfo") or [{}])[0]
        if info.get("width", 0) < MIN_W:
            continue
        url = info.get("thumburl") or info.get("url")
        if not url or not url.lower().endswith((".jpg", ".jpeg", ".png")):
            continue
        # FILTRO DE ÉPOCA: rechazar fotos modernas (ej. "iceman" → Wim Hof 2019)
        if _is_modern(info, p.get("title", "")):
            continue
        results.append({"url": url, "title": p.get("title", "")})
        if len(results) >= limit:
            break
    return results


def loc_search(query: str, limit: int = 4):
    """Library of Congress: fotos históricas de dominio público (FSA/OWI y más)."""
    try:
        r = SESSION.get(
            "https://www.loc.gov/photos/",
            params={"q": query, "fo": "json", "c": limit * 3, "dates": "1900/1980"},
            headers=HEADERS, timeout=30,
        )
        if r.status_code != 200:
            return []
        results = r.json().get("results", [])
    except Exception as e:
        print(f"[visuals] LOC error '{query}': {e}")
        return []
    out = []
    for item in results:
        urls = item.get("image_url") or []
        # image_url viene ordenado de menor a mayor resolución; tomar la más grande
        best = urls[-1] if urls else None
        if not best:
            continue
        out.append({"url": best, "title": item.get("title", "loc")})
        if len(out) >= limit:
            break
    time.sleep(3.2)  # LOC: 20 req/min máximo
    return out


def pexels_search(query: str, api_key: str, limit: int = 3):
    try:
        r = requests.get(
            "https://api.pexels.com/v1/search",
            params={"query": query, "per_page": limit, "orientation": "landscape"},
            headers={"Authorization": api_key}, timeout=30,
        )
        photos = r.json().get("photos", [])
        return [{"url": p["src"]["large2x"], "title": p.get("alt", "")} for p in photos]
    except Exception as e:
        print(f"[visuals] pexels error '{query}': {e}")
        return []


def download(url: str, dest: Path) -> bool:
    try:
        r = requests.get(url, headers=HEADERS, timeout=60)
        if r.status_code == 200 and len(r.content) > 20_000:
            dest.write_bytes(r.content)
            return True
    except Exception:
        pass
    return False


USED_DB = ROOT / "data" / "imagenes-usadas.json"


def load_used():
    if USED_DB.exists():
        return set(json.loads(USED_DB.read_text()).get("urls", []))
    return set()


def save_used(used):
    USED_DB.parent.mkdir(exist_ok=True)
    USED_DB.write_text(json.dumps({"urls": sorted(used)}, indent=0))


def main():
    plan_file, outdir = Path(sys.argv[1]), Path(sys.argv[2])
    outdir.mkdir(parents=True, exist_ok=True)
    plan = json.loads(plan_file.read_text())
    env = load_env()
    pexels_key = env.get("PEXELS_API_KEY", "")
    used = load_used()  # anti-reciclaje: jamás reutilizar una imagen entre videos

    # Formato nuevo: {"rotulos": {...}, "beats": [{"t":seg, "q":..., "loc":..., "es":..., "n":N}]}
    # Cada compás (~8-13 s) tiene su propia búsqueda, en vez de una por sección entera.
    if isinstance(plan, dict) and "beats" in plan:
        beats = plan["beats"]
        counter, manifest = 0, []
        for bi, b in enumerate(beats):
            cands = []
            palabras_q = b.get("q", "").split()
            while palabras_q and not cands:
                cands = wikimedia_search(" ".join(palabras_q), limit=3)
                if not cands:
                    palabras_q = palabras_q[:-1]
            if b.get("loc"):
                cands += loc_search(b["loc"], limit=2)
            if pexels_key and b.get("es"):
                cands += pexels_search(b["es"], pexels_key, limit=2)
            got = 0
            for c in cands:
                if got >= b.get("n", 1):
                    break
                if c["url"] in used:
                    continue
                slug = re.sub(r"[^a-z0-9]+", "-", c["title"].lower())[:32].strip("-") or "img"
                ext = ".png" if c["url"].lower().endswith(".png") else ".jpg"
                # el nombre lleva el tiempo: assemble lo usa para colocarla en su momento
                dest = outdir / f"b{bi:03d}_t{int(b['t']*100):07d}_{slug}{ext}"
                if download(c["url"], dest):
                    got += 1
                    counter += 1
                    used.add(c["url"])
                    manifest.append({"file": dest.name, "t": b["t"], "fuente": c["url"]})
                time.sleep(0.3)
            if not got:
                print(f"[visuals] compás {bi} ({b['t']:.0f}s) SIN imagen: «{b.get('q','')[:40]}»")
            if (bi + 1) % 20 == 0:
                print(f"[visuals] {bi+1}/{len(beats)} compases · {counter} imágenes")
        save_used(used)
        (outdir / "_manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False))
        print(f"[visuals] TOTAL: {counter} imágenes en {len(beats)} compases")
        return

    counter, manifest = 0, []
    for item in plan:
        sec = item.get("seccion", 0)
        # Commons hace AND estricto: si la búsqueda larga no da nada, acortar
        query = item.get("busqueda_wikimedia", "")
        words = query.split()
        candidates = []
        while words and not candidates:
            candidates = wikimedia_search(" ".join(words), limit=4)
            if not candidates:
                words = words[:-1]
        # Library of Congress como segunda fuente (dominio público total)
        if item.get("busqueda_loc"):
            candidates += loc_search(item["busqueda_loc"], limit=3)
        if pexels_key and item.get("busqueda_es"):
            candidates += pexels_search(item["busqueda_es"], pexels_key, limit=2)
        got = 0
        for c in candidates:
            if got >= item.get("imagenes", 3):
                break
            if c["url"] in used:
                continue  # ya usada en otro video de este u otro canal
            counter += 1
            slug = re.sub(r"[^a-z0-9]+", "-", c["title"].lower())[:40].strip("-") or "img"
            ext = ".png" if c["url"].lower().endswith(".png") else ".jpg"
            dest = outdir / f"{counter:03d}_s{sec:02d}_{slug}{ext}"
            if download(c["url"], dest):
                got += 1
                used.add(c["url"])
                manifest.append({"file": dest.name, "seccion": sec, "fuente": c["url"]})
            else:
                counter -= 1
            time.sleep(0.4)
        print(f"[visuals] sección {sec}: {got} imágenes")

    save_used(used)
    (outdir / "_manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False))
    print(f"[visuals] TOTAL: {len(manifest)} imágenes en {outdir}")
    if len(manifest) < len(plan) * 2:
        print("[visuals] AVISO: pocas imágenes — revisar búsquedas o añadir fuentes locales en assets/")


if __name__ == "__main__":
    main()

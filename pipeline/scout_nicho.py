#!/usr/bin/env python3
"""Explora un nicho con datos REALES de la YouTube Data API.

Uso: python3 scout_nicho.py "<consulta1>" "<consulta2>" ... --etiqueta NOMBRE

Para cada consulta busca videos publicados en los últimos 90 días, agrupa por canal
y trae las estadísticas reales del canal (suscriptores, vistas totales, nº de videos).
Calcula la métrica que de verdad importa para decidir un nicho:

    vistas/video = vistas_totales / nº_videos   → qué rinde un video medio ahí
    vistas/mes   = ritmo de la audiencia del nicho, no del canal más grande

Escribe data/scouting/<etiqueta>.json con todo el detalle para comparar después.
"""
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

ROOT = Path(__file__).resolve().parent.parent
TOKEN = ROOT / "config" / "token.json"
SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]
OUT = ROOT / "data" / "scouting"


def api():
    creds = Credentials.from_authorized_user_file(str(TOKEN))
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
    return build("youtube", "v3", credentials=creds)


def buscar(yt, consulta: str, desde: str, n: int = 25):
    r = yt.search().list(
        part="snippet", q=consulta, type="video", maxResults=n,
        order="viewCount", publishedAfter=desde, relevanceLanguage="es",
    ).execute()
    return r.get("items", [])


def stats_videos(yt, ids):
    out = {}
    for i in range(0, len(ids), 50):
        r = yt.videos().list(part="statistics,contentDetails,snippet",
                             id=",".join(ids[i:i + 50])).execute()
        for v in r.get("items", []):
            out[v["id"]] = v
    return out


def stats_canales(yt, ids):
    out = {}
    ids = list(ids)
    for i in range(0, len(ids), 50):
        r = yt.channels().list(part="statistics,snippet", id=",".join(ids[i:i + 50])).execute()
        for c in r.get("items", []):
            out[c["id"]] = c
    return out


def main():
    args = sys.argv[1:]
    etiqueta = "nicho"
    if "--etiqueta" in args:
        k = args.index("--etiqueta")
        etiqueta = args[k + 1]
        args = args[:k]
    consultas = args
    if not consultas:
        sys.exit("uso: scout_nicho.py \"consulta\" ... --etiqueta NOMBRE")

    yt = api()
    desde = (datetime.now(timezone.utc) - timedelta(days=90)).isoformat().replace("+00:00", "Z")

    videos_vistos, canales_ids = {}, set()
    for q in consultas:
        try:
            items = buscar(yt, q, desde)
        except Exception as e:
            print(f"[scout] fallo consulta «{q}»: {e}")
            continue
        for it in items:
            videos_vistos[it["id"]["videoId"]] = q
            canales_ids.add(it["snippet"]["channelId"])
        print(f"[scout] «{q}» → {len(items)} videos")

    vstats = stats_videos(yt, list(videos_vistos))
    cstats = stats_canales(yt, canales_ids)

    canales = []
    for cid, c in cstats.items():
        s = c["statistics"]
        subs = int(s.get("subscriberCount", 0))
        vistas = int(s.get("viewCount", 0))
        nvid = int(s.get("videoCount", 0)) or 1
        creado = c["snippet"]["publishedAt"][:10]
        # publishedAt trae microsegundos de longitud variable → parsear solo la fecha
        nacido = datetime.strptime(creado, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        meses = max((datetime.now(timezone.utc) - nacido).days / 30.4, 1)
        canales.append({
            "canal": c["snippet"]["title"], "id": cid, "creado": creado,
            "subs": subs, "vistas_totales": vistas, "videos": nvid,
            "vistas_por_video": round(vistas / nvid),
            "videos_por_mes": round(nvid / meses, 1),
            "vistas_por_mes": round(vistas / meses),
            "meses_activo": round(meses),
        })
    canales.sort(key=lambda c: -c["vistas_por_video"])

    tops = []
    for vid, v in vstats.items():
        st = v["statistics"]
        tops.append({
            "titulo": v["snippet"]["title"][:80],
            "canal": v["snippet"]["channelTitle"],
            "vistas": int(st.get("viewCount", 0)),
            "publicado": v["snippet"]["publishedAt"][:10],
            "duracion": v["contentDetails"]["duration"],
            "consulta": videos_vistos[vid],
        })
    tops.sort(key=lambda t: -t["vistas"])

    OUT.mkdir(parents=True, exist_ok=True)
    dest = OUT / f"{etiqueta}.json"
    dest.write_text(json.dumps(
        {"etiqueta": etiqueta, "consultas": consultas,
         "canales": canales, "top_videos": tops[:30]},
        indent=2, ensure_ascii=False))

    print(f"\n=== {etiqueta.upper()} · {len(canales)} canales · últimos 90 días ===")
    print(f"{'CANAL':38} {'SUBS':>9} {'V/VIDEO':>9} {'VID/MES':>8} {'MESES':>6}")
    for c in canales[:15]:
        print(f"{c['canal'][:38]:38} {c['subs']:>9,} {c['vistas_por_video']:>9,} "
              f"{c['videos_por_mes']:>8} {c['meses_activo']:>6}")
    print(f"\n  TOP VIDEOS 90 DÍAS")
    for t in tops[:8]:
        print(f"  {t['vistas']:>10,}  {t['canal'][:24]:24} {t['titulo'][:46]}")
    print(f"\n→ {dest}")


if __name__ == "__main__":
    main()

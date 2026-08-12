#!/usr/bin/env python3
"""¿Qué duración rinde más en un canal? Cruza duración contra vistas.

Uso: python3 duracion_vs_vistas.py <channelId|@handle> [más...]

Trae los últimos 100 videos largos (>3 min) de cada canal y los agrupa en tramos de
duración, mostrando la MEDIANA de vistas por tramo. La mediana y no el promedio: un
solo viral distorsiona el promedio y haría parecer ganador al tramo donde cayó.

Sirve para decidir la duración del canal con datos del nicho, no por intuición.
"""
import re
import statistics
import sys
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

ROOT = Path(__file__).resolve().parent.parent
TOKEN = ROOT / "config" / "token.json"
TRAMOS = [(3, 10), (10, 15), (15, 20), (20, 25), (25, 30), (30, 40), (40, 60), (60, 999)]


def api():
    creds = Credentials.from_authorized_user_file(str(TOKEN))
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
    return build("youtube", "v3", credentials=creds)


def dur_min(iso: str) -> float:
    m = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", iso or "")
    if not m:
        return 0
    h, mi, s = (int(x) if x else 0 for x in m.groups())
    return h * 60 + mi + s / 60


def resolver(yt, ref: str) -> str:
    if ref.startswith("UC"):
        return ref
    r = yt.channels().list(part="id", forHandle=ref.lstrip("@")).execute()
    it = r.get("items", [])
    return it[0]["id"] if it else ""


def videos_de(yt, cid: str, limite: int = 100):
    c = yt.channels().list(part="snippet,contentDetails,statistics", id=cid).execute()["items"][0]
    subir = c["contentDetails"]["relatedPlaylists"]["uploads"]
    ids, token = [], None
    while len(ids) < limite:
        r = yt.playlistItems().list(part="contentDetails", playlistId=subir,
                                    maxResults=50, pageToken=token).execute()
        ids += [i["contentDetails"]["videoId"] for i in r["items"]]
        token = r.get("nextPageToken")
        if not token:
            break
    vids = []
    for i in range(0, len(ids), 50):
        r = yt.videos().list(part="statistics,contentDetails,snippet",
                             id=",".join(ids[i:i + 50])).execute()
        for v in r["items"]:
            d = dur_min(v["contentDetails"]["duration"])
            if d < 3:               # descartar shorts: son otro negocio
                continue
            vids.append({"d": d, "v": int(v["statistics"].get("viewCount", 0)),
                         "t": v["snippet"]["title"]})
    return c["snippet"]["title"], int(c["statistics"]["subscriberCount"]), vids


def main():
    yt = api()
    for ref in sys.argv[1:]:
        cid = resolver(yt, ref)
        if not cid:
            print(f"[dur] no encontrado: {ref}")
            continue
        try:
            nombre, subs, vids = videos_de(yt, cid)
        except Exception as e:
            print(f"[dur] {ref}: {e}")
            continue
        if not vids:
            continue
        dur = sorted(v["d"] for v in vids)
        print(f"\n{'='*72}\n{nombre} · {subs:,} subs · {len(vids)} videos largos")
        print(f"  Duración: mediana {statistics.median(dur):.0f} min · "
              f"rango {dur[0]:.0f}–{dur[-1]:.0f} min")
        print(f"  {'TRAMO':>12} {'VIDEOS':>7} {'MEDIANA VISTAS':>15}")
        for lo, hi in TRAMOS:
            grupo = [v["v"] for v in vids if lo <= v["d"] < hi]
            if not grupo:
                continue
            etiqueta = f"{lo}-{hi} min" if hi < 999 else f"{lo}+ min"
            barra = "█" * min(int(statistics.median(grupo) / 8000), 30)
            print(f"  {etiqueta:>12} {len(grupo):>7} {statistics.median(grupo):>15,.0f}  {barra}")


if __name__ == "__main__":
    main()

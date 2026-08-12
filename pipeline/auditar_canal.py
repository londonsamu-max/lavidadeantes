#!/usr/bin/env python3
"""Auditoría profunda de un canal de referencia: ¿es replicable su modelo?

Uso: python3 auditar_canal.py <channelId|@handle> [más ids...]

Trae los últimos 50 videos con sus vistas y duración, y calcula lo que decide si
un nicho vale la pena o no:
  - mediana de vistas (la media miente: un solo viral la infla)
  - tasa de éxito: % de videos por encima de 100k
  - ritmo real de publicación (videos/semana en los últimos 90 días)
  - duración típica → si son largos, hay ingreso publicitario; si son Shorts, no
"""
import re
import statistics
import sys
from datetime import datetime, timezone
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

ROOT = Path(__file__).resolve().parent.parent
TOKEN = ROOT / "config" / "token.json"


def api():
    creds = Credentials.from_authorized_user_file(str(TOKEN))
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
    return build("youtube", "v3", credentials=creds)


def dur_seg(iso: str) -> int:
    m = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", iso or "")
    if not m:
        return 0
    h, mi, s = (int(x) if x else 0 for x in m.groups())
    return h * 3600 + mi * 60 + s


def resolver(yt, ref: str) -> str:
    if ref.startswith("UC"):
        return ref
    r = yt.channels().list(part="id", forHandle=ref.lstrip("@")).execute()
    items = r.get("items", [])
    return items[0]["id"] if items else ""


def auditar(yt, ref: str):
    cid = resolver(yt, ref)
    if not cid:
        print(f"[audit] no encontrado: {ref}")
        return
    c = yt.channels().list(part="snippet,statistics,contentDetails", id=cid).execute()["items"][0]
    subir = c["contentDetails"]["relatedPlaylists"]["uploads"]

    ids, token = [], None
    while len(ids) < 50:
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
            vids.append({
                "t": v["snippet"]["title"],
                "v": int(v["statistics"].get("viewCount", 0)),
                "d": dur_seg(v["contentDetails"]["duration"]),
                "f": v["snippet"]["publishedAt"][:10],
            })
    if not vids:
        return

    largos = [v for v in vids if v["d"] >= 60]
    shorts = [v for v in vids if v["d"] < 60]
    base = largos or vids
    vistas = sorted(v["v"] for v in base)
    fechas = sorted(datetime.strptime(v["f"], "%Y-%m-%d").replace(tzinfo=timezone.utc) for v in vids)
    dias = max((fechas[-1] - fechas[0]).days, 1)

    print(f"\n{'='*74}\n{c['snippet']['title']}  ·  {int(c['statistics']['subscriberCount']):,} subs"
          f"  ·  creado {c['snippet']['publishedAt'][:10]}")
    print(f"  Últimos {len(vids)} videos: {len(largos)} largos / {len(shorts)} shorts")
    print(f"  Ritmo real: {len(vids)/dias*7:.1f} videos/semana  ({len(vids)/dias*30.4:.0f}/mes)")
    print(f"  Duración típica (largos): {statistics.median([v['d'] for v in largos])/60:.0f} min"
          if largos else "  (solo shorts)")
    print(f"  Vistas   mediana {statistics.median(vistas):>10,.0f}   media {statistics.mean(vistas):>10,.0f}")
    print(f"           mínimo  {vistas[0]:>10,}   máximo {vistas[-1]:>10,}")
    print(f"  Consistencia: {100*sum(1 for v in vistas if v>=100_000)/len(vistas):.0f}% supera 100k · "
          f"{100*sum(1 for v in vistas if v<10_000)/len(vistas):.0f}% bajo 10k")
    print(f"  Últimos 5 títulos:")
    for v in vids[:5]:
        print(f"    {v['v']:>9,}  {v['f']}  {v['t'][:56]}")


def main():
    yt = api()
    for ref in sys.argv[1:]:
        try:
            auditar(yt, ref)
        except Exception as e:
            print(f"[audit] {ref}: {e}")


if __name__ == "__main__":
    main()

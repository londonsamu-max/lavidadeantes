#!/usr/bin/env python3
"""Diagnóstico del canal con datos reales de YouTube Analytics.

Uso: python3 diagnostico.py [dias]

Responde en orden las tres preguntas que importan cuando un canal no despega:
  1. ¿YouTube está MOSTRANDO los videos?      -> impresiones
  2. ¿La gente hace CLIC?                      -> CTR
  3. ¿La gente SE QUEDA?                       -> duración media y % visto

Ese orden importa: si no hay impresiones, el problema no es la miniatura.
Si hay impresiones y no hay clics, es miniatura/título. Si hay clics y no hay
retención, es el contenido o el arranque.
"""
import sys
from datetime import date, timedelta
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

ROOT = Path(__file__).resolve().parent.parent
TOKEN = ROOT / "config" / "token.json"


def creds():
    c = Credentials.from_authorized_user_file(str(TOKEN))
    if c.expired and c.refresh_token:
        c.refresh(Request())
    return c


def main():
    dias = int(sys.argv[1]) if len(sys.argv) > 1 else 30
    c = creds()
    yt = build("youtube", "v3", credentials=c)
    an = build("youtubeAnalytics", "v2", credentials=c)

    ch = yt.channels().list(part="statistics,contentDetails", mine=True).execute()["items"][0]
    st = ch["statistics"]
    print(f"CANAL: {st['videoCount']} videos · {st['subscriberCount']} subs · "
          f"{st['viewCount']} vistas totales\n")

    fin = date.today()
    ini = fin - timedelta(days=dias)

    def consulta(metrics, dims=None, sort=None, filtros=None):
        kw = dict(ids="channel==MINE", startDate=str(ini), endDate=str(fin),
                  metrics=metrics)
        if dims:
            kw["dimensions"] = dims
        if sort:
            kw["sort"] = sort
        if filtros:
            kw["filters"] = filtros
        try:
            return an.reports().query(**kw).execute()
        except Exception as e:
            print(f"   (sin datos para {metrics}: {str(e)[:90]})")
            return {"rows": [], "columnHeaders": []}

    # ── 1. el embudo completo del canal ──
    print(f"═══ EMBUDO DEL CANAL · últimos {dias} días ═══")
    r = consulta("views,estimatedMinutesWatched,averageViewDuration,"
                 "averageViewPercentage,subscribersGained")
    if r.get("rows"):
        v, mins, dur, pct, subs = r["rows"][0]
        print(f"   vistas               {v:>8,}")
        print(f"   minutos vistos       {mins:>8,}")
        print(f"   duración media       {dur//60:>5}:{dur%60:02d}")
        print(f"   % del video visto    {pct:>7.1f}%   <- la métrica que más pesa")
        print(f"   suscriptores ganados {subs:>8}")

    r = consulta("impressions,impressionsClickThroughRate")
    if r.get("rows"):
        imp, ctr = r["rows"][0]
        print(f"   impresiones          {imp:>8,}   <- ¿YouTube nos muestra?")
        print(f"   CTR                  {ctr:>7.2f}%   <- ¿hacen clic?")

    # ── 2. de dónde llegan ──
    print(f"\n═══ DE DÓNDE VIENEN LAS VISTAS ═══")
    r = consulta("views", dims="insightTrafficSourceType", sort="-views")
    for fila in r.get("rows", [])[:8]:
        print(f"   {fila[0]:<28} {fila[1]:>6,}")

    # ── 3. video por video ──
    print(f"\n═══ VIDEO POR VIDEO ═══")
    r = consulta("views,averageViewDuration,averageViewPercentage,"
                 "estimatedMinutesWatched", dims="video", sort="-views")
    ids = [f[0] for f in r.get("rows", [])]
    titulos = {}
    if ids:
        d = yt.videos().list(part="snippet,contentDetails", id=",".join(ids)).execute()
        for v in d["items"]:
            titulos[v["id"]] = v["snippet"]["title"]
    print(f"   {'VISTAS':>7} {'DUR.MEDIA':>10} {'%VISTO':>7}  TÍTULO")
    for f in r.get("rows", []):
        vid, vistas, dur, pct, _ = f
        print(f"   {vistas:>7,} {dur//60:>7}:{dur%60:02d} {pct:>6.1f}%  "
              f"{titulos.get(vid, vid)[:46]}")

    # CTR por video: dice si el problema es la miniatura de uno o de todos
    r = consulta("impressions,impressionsClickThroughRate", dims="video", sort="-impressions")
    if r.get("rows"):
        print(f"\n   {'IMPRES.':>8} {'CTR':>7}  TÍTULO")
        for f in r["rows"]:
            vid, imp, ctr = f
            print(f"   {imp:>8,} {ctr:>6.2f}%  {titulos.get(vid, vid)[:46]}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Sube el video a YouTube como PRIVADO (modo review: tú lo publicas desde Studio).

Uso: python3 upload.py <carpeta_job>
La carpeta debe tener: final.mp4, metadata.json y opcionalmente miniatura.jpg

metadata.json:
{
  "titulo": "...", "descripcion": "...", "tags": ["...", "..."],
  "categoria": "22", "idioma": "es"
}

Setup (una vez):
1. console.cloud.google.com → proyecto nuevo → habilitar "YouTube Data API v3"
2. OAuth consent screen (External, en producción o testing con tu email como test user)
3. Credentials → Create OAuth client ID → Desktop app → descargar JSON
4. Guardarlo como config/client_secret.json
La primera ejecución abre el navegador para autorizar; el token queda en config/token.json.

Nota: videos subidos por apps OAuth no verificadas por Google quedan forzados a
privado — irrelevante aquí porque subimos en privado a propósito y publicas a mano.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SECRETS = ROOT / "config" / "client_secret.json"
TOKEN = ROOT / "config" / "token.json"
SCOPES = ["https://www.googleapis.com/auth/youtube.upload",
          "https://www.googleapis.com/auth/youtube",
          "https://www.googleapis.com/auth/youtube.force-ssl",      # leer/responder comentarios
          "https://www.googleapis.com/auth/yt-analytics.readonly"]  # CTR, retención, fuentes de tráfico


def get_service():
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build

    creds = None
    if TOKEN.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN), SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not SECRETS.exists():
                sys.exit(f"[upload] Falta {SECRETS}\nSigue el setup del docstring (Google Cloud → OAuth Desktop → client_secret.json)")
            flow = InstalledAppFlow.from_client_secrets_file(str(SECRETS), SCOPES)
            creds = flow.run_local_server(port=0)
        TOKEN.write_text(creds.to_json())
    return build("youtube", "v3", credentials=creds)


def main():
    job = Path(sys.argv[1]).resolve()
    video = job / "final.mp4"
    meta_file = job / "metadata.json"
    thumb = job / "miniatura.jpg"
    if not video.exists() or not meta_file.exists():
        sys.exit("[upload] faltan final.mp4 o metadata.json")
    meta = json.loads(meta_file.read_text())

    from googleapiclient.http import MediaFileUpload

    yt = get_service()
    # privacidad: 'private' (default, modo review), 'unlisted' o 'public'.
    # OJO: apps OAuth sin auditar de Google fuerzan 'private' aunque pidas otra.
    privacy = meta.get("privacidad", "private")
    body = {
        "snippet": {
            "title": meta["titulo"][:100],
            "description": meta["descripcion"][:4900],
            "tags": meta.get("tags", [])[:30],
            "categoryId": meta.get("categoria", "22"),
            "defaultLanguage": meta.get("idioma", "es"),
            "defaultAudioLanguage": meta.get("idioma", "es"),
        },
        "status": {
            "privacyStatus": privacy,
            "selfDeclaredMadeForKids": False,
            # Obligatorio desde que los visuales se generan con IA (visuals_gen.py):
            # YouTube exige declarar contenido sintético que pueda parecer real.
            # metadata.json puede poner "sintetico": false para material de archivo.
            "containsSyntheticMedia": meta.get("sintetico", True),
        },
    }
    print(f"[upload] subiendo {video.name} ({video.stat().st_size/1e6:.0f} MB) → {privacy}...")
    media = MediaFileUpload(str(video), chunksize=8 * 1024 * 1024, resumable=True)
    req = yt.videos().insert(part="snippet,status", body=body, media_body=media)
    resp = None
    while resp is None:
        status, resp = req.next_chunk()
        if status:
            print(f"[upload] {int(status.progress() * 100)}%")
    vid = resp["id"]
    print(f"[upload] ✅ subido: https://youtube.com/watch?v={vid} (PRIVADO)")

    if thumb.exists():
        try:
            yt.thumbnails().set(videoId=vid, media_body=str(thumb)).execute()
            print("[upload] miniatura aplicada")
        except Exception as e:
            print(f"[upload] miniatura falló (¿canal sin verificar por teléfono?): {e}")
    # VERIFICAR la declaración de contenido sintético, no darla por hecha.
    # En el video 3 se envió en el insert, la API devolvió None, se asumió que el
    # campo no era legible... y en realidad no se había guardado: el video salió
    # sin la insignia «Creado con IA». Si vuelve None, se reintenta con update().
    if body["status"]["containsSyntheticMedia"]:
        estado = yt.videos().list(part="status", id=vid).execute()["items"][0]["status"]
        if not estado.get("containsSyntheticMedia"):
            print("[upload] ⚠️  la declaración de IA no quedó; reintentando...")
            estado["containsSyntheticMedia"] = True
            estado = yt.videos().update(
                part="status", body={"id": vid, "status": estado}).execute()["status"]
        ok = estado.get("containsSyntheticMedia")
        print(f"[upload] declaración de contenido sintético: "
              f"{'✅ confirmada' if ok else '❌ NO QUEDÓ — márcala a mano en Studio'}")

    print("[upload] SIGUIENTE PASO: revisa el video en YouTube Studio y publícalo o prográmalo.")
    # registrar
    log = job / "upload.json"
    log.write_text(json.dumps({"video_id": vid, "url": f"https://youtube.com/watch?v={vid}", "estado": "privado"}, indent=2))


if __name__ == "__main__":
    main()

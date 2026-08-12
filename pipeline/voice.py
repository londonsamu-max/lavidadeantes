#!/usr/bin/env python3
"""Genera la narración del guion con ElevenLabs (o edge-tts como fallback gratuito).

Uso: python3 voice.py <guion.txt> <salida.mp3>
El guion debe ser texto plano (sin markdown). Lee ELEVENLABS_API_KEY de ../.env
"""
import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG = json.loads((ROOT / "config" / "channel-config.json").read_text())


def load_env():
    env = {}
    env_file = ROOT / ".env"
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip()
    return env


def clean_text(text: str) -> str:
    text = re.sub(r"^#+ .*$", "", text, flags=re.M)          # títulos markdown
    text = re.sub(r"\[[^\]]*\]", "", text)                    # [notas de producción]
    text = re.sub(r"[*_`>]", "", text)                         # énfasis markdown
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def tts_elevenlabs(text: str, out: Path, api_key: str) -> bool:
    import requests

    voice_id = CONFIG["voz"]["elevenlabs_voice_id"]
    if not voice_id:
        print("[voice] elevenlabs_voice_id vacío en config — usando fallback")
        return False
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    # ElevenLabs acepta ~10k chars por request en multilingual_v2 — trocear por párrafos
    chunks, cur = [], ""
    for para in text.split("\n\n"):
        if len(cur) + len(para) > 9000:
            chunks.append(cur)
            cur = para
        else:
            cur = f"{cur}\n\n{para}" if cur else para
    if cur:
        chunks.append(cur)

    parts = []
    for i, chunk in enumerate(chunks):
        r = requests.post(
            url,
            headers={"xi-api-key": api_key, "Content-Type": "application/json"},
            json={
                "text": chunk,
                "model_id": CONFIG["voz"]["elevenlabs_model"],
                "voice_settings": {"stability": 0.55, "similarity_boost": 0.75, "style": 0.2},
            },
            timeout=300,
        )
        if r.status_code != 200:
            print(f"[voice] ElevenLabs error {r.status_code}: {r.text[:200]}")
            return False
        part = out.parent / f"_part{i:03d}.mp3"
        part.write_bytes(r.content)
        parts.append(part)
        print(f"[voice] chunk {i + 1}/{len(chunks)} OK ({len(chunk)} chars)")

    if len(parts) == 1:
        parts[0].rename(out)
    else:
        concat_list = out.parent / "_concat.txt"
        concat_list.write_text("".join(f"file '{p.name}'\n" for p in parts))
        import imageio_ffmpeg

        ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
        subprocess.run(
            [ffmpeg, "-y", "-f", "concat", "-safe", "0", "-i", str(concat_list),
             "-c", "copy", str(out)],
            cwd=out.parent, check=True, capture_output=True,
        )
        for p in parts:
            p.unlink()
        concat_list.unlink()
    return True


def tts_edge(text: str, out: Path) -> bool:
    voice = CONFIG["voz"]["edge_voice"]
    rate = CONFIG["voz"]["velocidad"]
    cmd = [sys.executable, "-m", "edge_tts", f"--voice={voice}", f"--rate={rate}",
           f"--text={text}", f"--write-media={out}"]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"[voice] edge-tts error: {r.stderr[:300]}")
        return False
    return True


def main():
    guion, out = Path(sys.argv[1]), Path(sys.argv[2])
    out.parent.mkdir(parents=True, exist_ok=True)
    text = clean_text(guion.read_text())
    print(f"[voice] {len(text)} caracteres a narrar")

    env = load_env()
    api_key = env.get("ELEVENLABS_API_KEY") or os.environ.get("ELEVENLABS_API_KEY", "")
    ok = False
    if CONFIG["voz"]["proveedor"] == "elevenlabs" and api_key:
        ok = tts_elevenlabs(text, out, api_key)
    if not ok:
        print(f"[voice] usando fallback edge-tts ({CONFIG['voz']['edge_voice']})")
        ok = tts_edge(text, out)
    if not ok:
        sys.exit("[voice] FALLO: ningún proveedor de voz funcionó")

    from mutagen.mp3 import MP3

    dur = MP3(out).info.length
    print(f"[voice] OK → {out.name} ({dur / 60:.1f} min)")


if __name__ == "__main__":
    main()

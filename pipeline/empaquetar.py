#!/usr/bin/env python3
"""Empaqueta el proyecto para mudarlo a otro PC.

Uso: python3 empaquetar.py [destino.zip]

Mete el código, la memoria del canal y los recursos. DEJA FUERA dos cosas a propósito:

  config/   son las credenciales del canal de YouTube. Quien tenga token.json puede
            subir y borrar videos en tu nombre, así que no viaja en un zip que pueda
            terminar en un correo o en Drive: se pasa a mano, aparte.
  output/   son los videos ya renderizados (15 GB). Se regeneran; no tiene sentido
            mover 589 MB por video.
"""
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

INCLUIR_DIRS = ["pipeline", "data", "docs", "assets"]
INCLUIR_FILES = ["CLAUDE.md", "README-INSTALACION.md", "requirements.txt"]

# basura que no aporta y sí pesa
EXCLUIR = {"__pycache__", ".DS_Store", ".venv", "generadas"}


def excluido(p: Path) -> bool:
    return any(parte in EXCLUIR for parte in p.parts) or p.name.startswith(".")


def main():
    destino = Path(sys.argv[1]).expanduser() if len(sys.argv) > 1 else \
        Path.home() / "Desktop" / "la-vida-de-antes.zip"
    destino.parent.mkdir(parents=True, exist_ok=True)

    n, total = 0, 0
    with zipfile.ZipFile(destino, "w", zipfile.ZIP_DEFLATED) as z:
        for d in INCLUIR_DIRS:
            base = ROOT / d
            if not base.exists():
                print(f"[zip] aviso: no existe {d}/")
                continue
            for f in base.rglob("*"):
                if f.is_file() and not excluido(f.relative_to(ROOT)):
                    z.write(f, f.relative_to(ROOT))
                    n += 1
                    total += f.stat().st_size
        for f in INCLUIR_FILES:
            p = ROOT / f
            if p.exists():
                z.write(p, f)
                n += 1
                total += p.stat().st_size

        # inventario de lo que hay que copiar a mano, dentro del propio zip
        z.writestr("FALTA-COPIAR-A-MANO.txt",
                   "Estos archivos NO viajan en el zip. Cópialos a config/ por USB o\n"
                   "transferencia directa, nunca por correo ni Drive:\n\n"
                   "  config/client_secret.json   OAuth de Google Cloud\n"
                   "  config/token.json           sesión autorizada del canal\n"
                   "  config/channel-config.json  configuración del canal\n\n"
                   "token.json es la llave del canal: quien lo tenga puede subir y\n"
                   "borrar videos en tu nombre.\n\n"
                   "Si se pierde token.json se regenera solo: al correr upload.py sin\n"
                   "él, se abre el navegador para volver a autorizar.\n")

    print(f"[zip] {n} archivos · {total/1e6:.1f} MB sin comprimir")
    print(f"[zip] → {destino}  ({destino.stat().st_size/1e6:.1f} MB)")
    print("[zip] NO incluye config/ (credenciales) ni output/ (videos)")


if __name__ == "__main__":
    main()

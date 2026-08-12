# La Vida de Antes — instalar en un PC nuevo

Canal automatizado de nostalgia para público hispanohablante de 50+.
Este paquete trae **todo el código y la configuración; no trae credenciales ni videos**.

---

## 1. Qué viene y qué no

| carpeta | va en el zip | por qué |
|---|---|---|
| `pipeline/` | ✅ | los 20 scripts del pipeline |
| `data/` | ✅ | memoria del canal: estrategia, lecciones, registro de contenido |
| `docs/` | ✅ | reglas de producción, viralización y validación de nichos |
| `assets/` | ✅ | tipografías, música CC-BY, modelo de nitidez ESPCN |
| `CLAUDE.md` | ✅ | las instrucciones que sigue Claude. **Es el cerebro del canal** |
| `config/` | ❌ | **credenciales — se pasan aparte, a mano** |
| `output/` | ❌ | videos ya renderizados (15 GB). Se regeneran |

---

## 2. Instalación

```bash
# 1. Descomprimir donde quieras, por ejemplo ~/youtube-factory
cd ~/youtube-factory

# 2. Entorno virtual PROPIO (importante: opencv instala numpy 2.x y eso
#    rompió tensorflow en otro proyecto de la máquina vieja)
python3 -m venv .venv
source .venv/bin/activate        # en Windows:  .venv\Scripts\activate

# 3. Dependencias
pip install -r requirements.txt
```

Se necesita **Python 3.10 o superior**. En la máquina vieja corría en 3.9, que ya está
fuera de soporte y lo avisa en cada ejecución; este es buen momento para actualizar.

FFmpeg **no** hay que instalarlo: `imageio-ffmpeg` trae el suyo.

---

## 3. Credenciales (a mano, no por el zip)

Copiar a `config/`:

- `client_secret.json` — el OAuth de Google Cloud
- `token.json` — la sesión ya autorizada del canal
- `channel-config.json` — configuración del canal (voz, nombre)

> **`token.json` es la llave del canal.** Quien lo tenga puede subir y borrar videos
> en tu nombre. Pásalo en una memoria USB o transferencia directa. **Nunca por
> correo, WhatsApp ni Drive.**

Si se pierde `token.json`, se regenera: al correr `upload.py` sin él, se abre el
navegador para volver a autorizar.

---

## 4. Cómo se produce un video

```bash
python3 pipeline/produce.py output/<slug>/      # voz + imágenes + montaje
python3 pipeline/quality_gate.py output/<slug>/ # semáforo: VERDE o ROJO
python3 pipeline/upload.py output/<slug>/       # sube a YouTube (queda PRIVADO)
```

La carpeta del video debe tener `guion.txt`, `visuales.json` y `metadata.json`.
Los escribe Claude en el ciclo del cerebro.

---

## 5. El paso de las imágenes: qué es automático y qué no

**Para ti es automático: no tienes que hacer nada.** Pero conviene que sepas cómo
funciona por dentro, porque de vez en cuando el navegador va a pedir un clic.

Las imágenes buenas se generan en **Google Flow** (Nano Banana, 1376×768, sin costo
en créditos). **Flow no tiene API**, así que no se puede llamar desde un script:
lo maneja Claude directamente desde Chrome, con la extensión Claude in Chrome.

El ciclo por bloque es:

1. Claude pega el bloque de prompts en Flow (modo Agente) y espera
2. Descarga las imágenes desde la página
3. Arma una **hoja de contactos** y las identifica mirándolas
4. Las coloca en su compás exacto del video

El paso 3 existe porque **Flow no guarda qué prompt generó cada imagen** — las marca
todas como "Imagen generada". Identificarlas requiere mirar y decidir, así que no es
scriptable. Lo hace Claude, no un programa.

### Lo que se aprendió peleándose con Flow (11-ago-2026)

Todo esto pasó produciendo el video 6 y va a volver a pasar:

- **Un bloque a la vez, y esperar.** Encolar varios satura la página. Ya se perdieron
  91 imágenes así una vez.
- **Proyecto nuevo cada bloque.** Pasando de ~40 imágenes la galería se cae, a veces
  con *"Application error"*. Se recupera recargando, pero se pierde tiempo.
- **Descargar de a 6 como máximo.** Más de eso congela el renderizador.
- **Flow se salta prompts.** Pidiendo 6 generó 5; pidiendo 22 generó 18. Hay que
  contar siempre y volver a pedir los que falten.
- **La galería cambia de orden al recargar** (a veces las nuevas primero, a veces las
  viejas). Nunca asumir el orden: verificar con la hoja de contactos.

### Dónde SÍ te van a pedir algo

Chrome y Google interrumpen de vez en cuando, y eso Claude no lo puede resolver solo:

1. **Permiso de descargas múltiples.** Una sola vez por PC:
   `chrome://settings/content/automaticDownloads` → Agregar → `labs.google`
2. **Sesión de Flow expirada.** Pide elegir cuenta. La del canal es
   **lavidadeantes.oficial@gmail.com** (la otra, londonsamu@gmail.com, Flow la rechaza).
3. **Términos de labs.google** en un PC o cuenta nuevos. Aceptar términos es una
   decisión tuya; Claude no lo hace por ti.

### La alternativa que sí sería 100% automática

Una **API de imágenes de pago** (Gemini/Imagen). Se llama desde un script, devuelve
cada imagen asociada a su prompt —sin hojas de contactos, sin identificar a ojo— y no
se cae. Ya hay una clave de Gemini configurada; al probarla el error fue
*"Your prepayment credits are depleted"*, así que solo falta ponerle saldo.

Mientras tanto, el generador gratuito (Pollinations, en `visuals_gen.py`) sirve de
respaldo, pero **no para este canal**: en el video 6 devolvió una maestra en shorts,
una muchacha con sombrero de playa donde debía haber unas manos con una boleta, y una
falsa fotografía sepia de grupo escolar con las caras deformes. Sirve para probar el
pipeline, no para publicar.

---

## 6. Antes de publicar, siempre

1. `quality_gate.py` en VERDE
2. Revisar fotogramas del video: ¿las imágenes corresponden a lo que se narra?
   ¿son de época? ¿hay alguna que parezca una fotografía histórica real?
3. Declarar contenido sintético — `upload.py` lo hace y lo **verifica con reintento**,
   porque en el video 3 la declaración falló en silencio y nadie se enteró hasta que
   el usuario preguntó por qué un video tenía el aviso y los otros no.

---

## 7. Reglas que no se negocian

Están en `CLAUDE.md` y salieron de datos reales del canal, no de teoría:

- **Guion de 3.000 palabras mínimo** (verificar con `wc -w` ANTES de producir)
- **Los primeros 30 segundos** llevan dato concreto + freno + promesa explícita.
  El video 4, que abre así, retiene 71% al minuto 1:05; el video 3, que abre
  contemplando un ambiente, cae a 29% en el mismo tramo.
- **Miniatura con rostro** y titular que abra una pregunta, no el tema del video.
  El CTR medido era 1,4% cuando lo sano son 4-10%.
- **Sin tarjeta de apertura.** `APERTURA_S = 0`.
- **Las imágenes se generan, no se buscan.**
- **Nunca fotorrealismo** para escenas históricas: fabricaría registro falso de un
  pasado real.

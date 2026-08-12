# YouTube Factory — "La Vida de Antes"

Canal automatizado (faceless) para audiencia 50+ hispanohablante. Nicho validado jul-2026:
habilidades olvidadas de nuestros abuelos + nostalgia de época (México/Latam foco).

## Arquitectura (espejo del SpotGamma Monitor)
- **Cerebro** = Claude Code (esta sesión / cron): analiza referencias, decide temas, escribe guiones y planes visuales, lee métricas, actualiza estrategia
- **Músculo** = `pipeline/*.py`: voz (ElevenLabs→edge-tts), visuales (Wikimedia+Pexels), ensamblado (FFmpeg Ken Burns)
- **Memoria** = `data/strategy-state.json` (referencias, lecciones, ideas, historial)

## Ciclo de producción de un video
1. Leer `data/strategy-state.json` y `config/channel-config.json`
2. Elegir tema: adaptar (NO traducir literal) los outliers de los canales referencia (@ForgottenAmericanSurvival etc.) al contexto hispano
3. Crear carpeta `output/<slug>/` con:
   - `guion.txt` — **MÍNIMO 3.000 palabras, objetivo 3.200-3.800 (≈23-28 min)**. VERIFICAR con `wc -w` ANTES de producir
- **VISUALES: se GENERAN, no se buscan.** Usar `visuals_gen.py`, no `visuals.py`.
  Buscar en Wikimedia/LOC devuelve lo que se parece a las palabras, sin verificar
  relevancia ni cultura: en el video 3, 6 de 11 momentos muestreados traían imágenes
  ajenas al guion (comedor con letrero en hebreo, carta manuscrita en inglés, salón
  de palacio). Generar es literal. Estilo por defecto: **ilustración**, nunca
  fotorrealismo — pasar fotos IA por el filtro vintage fabricaría registro histórico
  falso de un pasado real.
- **Declarar contenido sintético en YouTube Studio** en todo video con visuales generados.: si tiene menos de 3.000, ampliar antes de seguir. Razón: el 67,7% del watch time global es en videos de +20 min; el filtro de validación del nicho exige 1M vistas/mes a videos de 8-15 min pero solo 500K a los de 20-30 min; y más duración = más mid-rolls = más RPM. Un guion corto desperdicia el trabajo. Texto plano, estructura del megaprompt: gancho (30s) → promesa → 25 items numerados con micro-ganchos → cierre + CTA. Oraciones <25 palabras, lenguaje hablado, español latino neutro. TODO verificable — nada inventado sobre historia real
   - `visuales.json` — array de secciones: `{"seccion": N, "busqueda_wikimedia": "términos EN inglés para fotos históricas", "busqueda_es": "términos español para Pexels", "imagenes": 3}`. Una entrada por item del guion + intro/cierre
4. Ejecutar: `python3 pipeline/produce.py output/<slug>/`
5. MODO REVIEW: el humano ve `final.mp4` antes de subir. NUNCA subir sin aprobación
6. Actualizar `strategy-state.json`: video producido, lecciones nuevas

## RETENCIÓN Y CTR — medido en NUESTRO canal (diagnóstico 9-ago-2026)
Datos reales de 28 días: 584 vistas, 32,5 h vistas, +6 subs. Tráfico: SUSCRIPTORES 307,
VIDEO RELACIONADO 198, BÚSQUEDA 2, **PANTALLA DE INICIO 0**. YouTube no estaba
distribuyendo nada. Las dos causas, medidas:

**1. CTR de 1,4%** (video 5; lo sano son 4-10%). Las cinco miniaturas eran la misma
plantilla: escena ancha, filtro vintage que apaga, banda oscura abajo, texto crema
centrado. Sin rostro y sin pregunta.
→ `thumbnail.py` rehecho: rostro grande a un lado, panel de texto al otro, saturación
y contraste **al alza** (lo contrario del filtro del video), BebasNeue, amarillo
#FFC61A como acento fijo del canal. El rostro se genera con `imagen.py`.
→ En la miniatura NO va el tema, va la pregunta o la cifra. «LA ESCUELA DE ANTES» no
gana un clic; «LE CALIFICABAN LA CONDUCTA» sí.

**2. Retención del 17% de media**, y toda la diferencia está en el primer minuto:

| video | % visto | arranque |
|---|---|---|
| #4 Precios | **28,0%** | cifra dura + «Espere» + acusación + promesa |
| #1 25 cosas | 23,0% | cifra + promesa |
| #2 Oficios | 20,7% | ambiente |
| #3 Domingo | 9,4% | ambiente («Son las seis y media...») |
| #5 Juguetes | **3,0%** | sin promesa |

Curva: el video 3 cae de 97% a **29% en 1:05**; el 4 va de 100% a **71%** en el mismo
tramo. Mismo formato, misma voz, mismas imágenes.

**REGLA DURA — los primeros 30 segundos (≈75 palabras) llevan las tres cosas:**
1. **Dato concreto** verificable — cifra, fecha o cantidad. En la primera frase.
2. **Freno** — «Espere», «No se me vaya todavía», «Antes de que...».
3. **Promesa explícita** — qué recibe si se queda, y si hay una parte incómoda,
   anunciarla ahí para abrir el bucle («le digo de una vez cuál es la parte que...»).

`quality_gate.py` lo verifica solo y da ROJO si falta el dato o la promesa. Es un
suelo, no una garantía: el video 3 cumple dos de tres y aun así retiene 9,4% porque
su arranque sigue siendo contemplativo. El filtro atrapa lo peor; el juicio lo pone Claude.

**Sin tarjeta de apertura.** `APERTURA_S = 0` en `overlay_text.py`. Cinco segundos de
cartel estático es un 8% de la ventana que decide todo, regalado antes de la primera
frase. La identidad va en el rótulo de la esquina.

Herramientas: `pipeline/diagnostico.py` (métricas por video y curvas de retención),
`pipeline/reminiaturas.py` (rehace y sube las portadas de lo ya publicado, con copia
de seguridad de la anterior), `pipeline/replan.py` (reancla imágenes cuando cambia el
guion, para no regenerar 140 imágenes por un cambio de 30 segundos).

## Reglas duras (políticas YouTube 2026 — verificadas)
- PROHIBIDO: consejos de salud/médicos, finanzas, legal con voz IA (política 16-jul-2026); religioso masivo; rescates de animales; reciclar las mismas imágenes entre videos
- OBLIGATORIO: guion 100% original por video; variedad visual real (Wikimedia dominio público + Pexels); declarar contenido sintético al subir; valor educativo/histórico genuino
- El nicho es "vida cotidiana e historia" — si un item roza salud (remedios de abuela), tratarlo como HISTORIA/curiosidad cultural, jamás como consejo aplicable

## Setup pendiente (una vez)
- `.env`: ELEVENLABS_API_KEY=... (y elegir `elevenlabs_voice_id` en config) · PEXELS_API_KEY=... (gratis en pexels.com/api)
- Sin keys, la voz cae a edge-tts (gratis, calidad aceptable para pruebas)
- Cuenta Google del canal + verificación teléfono/identidad ANTES del primer video

## Sistemas de escala (multi-canal)
- `docs/PROCESO-VALIDACION-NICHO.md` — proceso estándar de 5 fases para validar CUALQUIER nicho nuevo ("valida el nicho X con el proceso estándar"). Pipeline de nichos en `data/nichos-pipeline.json`
- `docs/SISTEMA-VARIEDAD.md` — motor anti-repetición: rotación de 8 formatos y 4 hooks, registro de temas en `data/registro-contenido.json`, candado de imágenes en `data/imagenes-usadas.json` (visuals.py lo aplica solo). ANTES de escribir un guion: consultar registro-contenido.json (últimos formatos/hooks/temas) y elegir el siguiente distinto

## Documentos de referencia OBLIGATORIOS
- `docs/REGLAS-PRODUCCION-EVIDENCIA.md` — 26 reglas de guion/voz/visual/música basadas en evidencia académica (reminiscence bump 1965-1990, hooks cálido-curiosos, texto redundante en pantalla, 135-150 ppm, música -12dB). APLICAR EN CADA GUION
- `docs/REGLAS-VIRALIZACION.md` — estructura y algoritmo 2026: bucles anidados, re-ganchos cada 2-3 min, rostros en miniaturas (69-80% de los breakout), sin capítulos en narrativo, pantalla final de 20s narrada, preguntas de memoria en comentarios, listas de reproducción, Test & Compare. APLICAR JUNTO CON las reglas de evidencia
- `docs/STACK-VISUALES.md` — stack de generación visual (Gemini gratis, LOC dominio público, mflux local, Ideogram miniaturas) y tipografías
- `docs/PROCEDIMIENTO-IMAGENES-FLOW.md` — cómo sacar las imágenes por Google Flow paso a paso (bloques → pegar → hojas de contactos → colocar). OBLIGATORIO leerlo antes de tocar Flow: lleva los límites que rompen el proceso y las trampas de su interfaz. Flow está geobloqueado en las sesiones remotas de Claude: este paso lo hace el humano desde su navegador

## FLUJO COMPLETO (un video de principio a fin)
1. **Cerebro (Claude)**: consultar `data/registro-contenido.json` (formato/hook/temas siguientes) → crear `output/<slug>/` con `guion.txt` + `visuales.json` + `metadata.json` (titulo, descripcion con atribución de música CC-BY + declaración IA, tags, miniatura{imagen, texto con | para saltos de línea})
2. **Producir**: `python3 pipeline/flow.py output/<slug>/` → voz + visuales + video + miniatura
3. **REVISIÓN HUMANA**: el usuario ve final.mp4 y miniatura.jpg
4. **Subir**: `python3 pipeline/flow.py output/<slug>/ --subir` → sube PRIVADO a YouTube con metadata y miniatura
5. **Publicar**: el usuario publica/programa desde YouTube Studio (verificar casilla de contenido alterado/sintético)
6. **Registrar**: actualizar `data/registro-contenido.json` y `data/strategy-state.json`

## Setup de subida (una vez)
- console.cloud.google.com → proyecto → habilitar YouTube Data API v3 → OAuth consent (External, añadir tu email como test user) → Credentials → OAuth Client ID tipo Desktop → descargar JSON → guardarlo como `config/client_secret.json`
- Primera subida abre el navegador para autorizar; token queda en `config/token.json`

## Comandos sueltos
- Flujo completo: `python3 pipeline/flow.py output/<slug>/ [--subir]`
- Solo producir: `python3 pipeline/produce.py output/<slug>/`
- Solo voz: `python3 pipeline/voice.py output/<slug>/guion.txt output/<slug>/voz.mp3`
- Solo visuales: `python3 pipeline/visuals.py output/<slug>/visuales.json output/<slug>/visuales/`
- Solo miniatura: `python3 pipeline/thumbnail.py <img> "TEXTO|LÍNEA 2" <out.jpg>`
- Solo subir: `python3 pipeline/upload.py output/<slug>/`

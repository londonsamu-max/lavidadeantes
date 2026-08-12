# CICLO DIARIO AUTOMÁTICO — La Vida de Antes

> Esto es lo que Claude ejecuta cada día sin intervención del usuario.
> Configuración elegida: **1 video/día** (sube a 2/día a partir del 15-ago-2026 si las
> métricas aguantan) · **publicación automática, cero avisos** · reporte semanal.
>
> REGLA MADRE: ante cualquier duda, NO se publica. Es infinitamente más barato
> saltarse un día que publicar un video que active la política de contenido
> inauténtico. El canal es el activo; un video es reemplazable.

## PASO 1 — Decidir el tema (5 min)
0. **Leer la pestaña Inspiración de YouTube Studio** (studio.youtube.com → Contenido →
   Inspiración). Son sugerencias de la propia IA de YouTube basadas en los datos del canal
   y su audiencia — más fiables que la intuición. Cruzarlas con el banco de temas.
   Se lee por navegador (Chrome del usuario); no hay API pública.
1. Leer `data/registro-contenido.json`: últimos formatos y hooks usados, temas ya gastados.
2. Leer `data/banco-temas.json`: 20 temas validados con fuente. Elegir uno que:
   - use un FORMATO distinto al del video anterior (de los 8 de SISTEMA-VARIEDAD.md)
   - use un HOOK distinto al del video anterior (de los 4)
   - no solape más de 3 ítems con ningún video previo
   - pague el teaser que dejó el video anterior (si lo hubo)
3. Si toca fecha estacional (ver docs/FUENTES-CONTENIDO.md), priorizarla.

## PASO 2 — Escribir el guion
Aplicar SIEMPRE, sin excepción:
- `docs/REGLAS-PRODUCCION-EVIDENCIA.md` (las 26 reglas: bump 1965-1990, hook cálido-curioso,
  transiciones explícitas, 135-150 ppm, cierre parasocial)
- `docs/REGLAS-VIRALIZACION.md` (bucles anidados, re-gancho cada 2-3 min, pregunta de
  memoria a mitad y al final, nada de pedir suscripción antes del min 10)
- **VERIFICAR `wc -w` ≥ 3.000 ANTES de seguir.** Si no llega, ampliar.
- Secciones marcadas con `### Título` (el separador las reconoce en cualquier formato).
- Datos duros: dos fuentes o no se dice. Ante duda, describir la experiencia sin afirmar cifras.

## PASO 3 — Plan visual
- `visuales.json` con `titulo` por sección (van al rótulo persistente).
- Términos de búsqueda en **lenguaje de archivo, no moderno**: "ice wagon" no "ice delivery";
  "newsboy" no "newspaper boy"; "letter carrier" no "postman".
- 7-9 imágenes por sección.

## PASO 4 — Producir
```
python3 pipeline/produce.py output/<slug>/          # voz sincronizada + imágenes + montaje limpio
python3 pipeline/subtitles.py output/<slug>/        # SRT desde el guion + timing
python3 pipeline/overlay_text.py output/<slug>/     # apertura + rótulos + subtítulos quemados
python3 pipeline/thumbnail.py <img> "TEXTO" output/<slug>/miniatura.jpg
```

## PASO 5 — SEMÁFORO (la parte crítica)
### 5a. Filtro automático
```
python3 pipeline/quality_gate.py output/<slug>/
```
Si sale ROJO: arreglar lo que señale y repetir. NO publicar.

### 5b. Revisión visual — la hace Claude mirando, no un script
Extraer 15-20 frames repartidos por todo el video y MIRARLOS de verdad:
```
ffmpeg -ss <seg> -i output/<slug>/final.mp4 -frames:v 1 -q:v 3 /tmp/rev_<n>.jpg
```
Buscar y marcar como ROJO si aparece:
- Imágenes claramente modernas (coches actuales, ropa actual, escaparates de hoy)
- Marcas comerciales legibles, sobre todo modernas
- Contenido que no pega con el nicho o con lo que narra la voz en ese momento
- Texto en la imagen en otro idioma que descoloque
- Cualquier cosa ofensiva, violenta o inapropiada
Si 3 o más frames fallan → ROJO: rehacer las búsquedas de esas secciones.
**Este paso NO se salta. Fue el que detectó la tienda británica y los televisores modernos.**

### 5c. Auto-crítica del guion
Releer el guion contra las reglas. ¿El hook cumple? ¿El bucle maestro cierra al final?
¿Hay pregunta de memoria? ¿Algún dato sin fuente? Si algo falla, corregir antes de subir.

## PASO 6 — Publicar
Solo si 5a, 5b y 5c dieron VERDE:
```
python3 pipeline/upload.py output/<slug>/     # con "privacidad": "public" en metadata.json
```
Después de subir:
- Subir `subtitulos.srt` como pista de subtítulos (además de los quemados: YouTube los indexa)
- Fijar comentario con **pregunta de memoria** (no de opinión):
  ✅ "¿Cómo se llamaba la tienda de la esquina de su barrio?"
  ❌ "¿Les gustó el video?"
- Añadir el video a la lista de reproducción de la serie
- Verificar que quedó marcado "no es para niños" y con la declaración de contenido sintético

## PASO 7 — Registrar
Actualizar `data/registro-contenido.json`: slug, fecha, formato, hook, ítems usados,
loop abierto, teaser del siguiente. Sin esto el motor anti-repetición se ciega.

---

# CICLO SEMANAL (domingos)
1. Leer métricas reales por API: vistas, retención, % visto, CTR, comentarios, fuentes de tráfico.
2. Comparar formatos entre sí: ¿cuál retiene más? ¿cuál trae más comentarios?
3. Ajustar: si un formato cae 3 videos seguidos, descansarlo un mes. Si otro sobresale,
   subir su frecuencia sin romper la rotación.
4. Leer los comentarios reales: de ahí salen temas nuevos y el formato F8 (recuerdos de la audiencia).
5. Escribir el reporte semanal para el usuario: qué se publicó, cómo va, qué aprendí, qué cambio.
6. Anotar lecciones nuevas en `data/strategy-state.json`.

# ESCALADA A 2 VIDEOS/DÍA
A partir del **15 de agosto de 2026**, y solo si se cumple todo esto:
- El canal no ha recibido ninguna advertencia ni desmonetización
- La retención media se mantiene ≥ 35%
- Hay banco de temas suficiente para no repetir
Si algo de eso falla, se mantiene 1/día y se anota la razón.


---

# PENDIENTE — Metraje en movimiento (mejora grande, para después del arranque)
Prelinger Archives en archive.org: **10.369 películas** de vida cotidiana de mediados del
siglo XX, descargables por API (`archive.org/advancedsearch.php` + `/metadata/<id>`),
versión ligera de ~90 MB. Intercalar clips reales en movimiento entre las fotos sería el
mayor salto de calidad disponible: de pase de diapositivas a documental de verdad.

REGLA INNEGOCIABLE: solo metraje con licencia de dominio público **verificable pieza por
pieza** (muchos ítems de Prelinger no declaran licencia en la metadata; sin licencia legible,
no se usa). NUNCA fragmentos de material con derechos: el Content ID los detecta y una
reclamación puede costar el canal. Las técnicas de evasión que circulan (clips <6 s, efecto
espejo, overlays) no son protección legal.

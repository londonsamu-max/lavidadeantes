# Imágenes del video con Google Flow — procedimiento

> Para el Claude que abra este repositorio en otro computador — o para el de la
> sesión remota, si algún día se resuelve lo de la cuenta (ver más abajo).

## Flow NO se puede manejar desde una sesión remota. Y no es cosa de la cuenta

Medido el 12-ago-2026 desde un contenedor de Claude Code en la nube:

- Cargar `https://labs.google/fx/tools/flow/project?hl=en` **sin ninguna cookie,
  sin cuenta**, redirige a **`labs.google/fx/tools/flow/unsupported-country`**.
  El rechazo ocurre antes de que haya sesión: **ninguna cuenta lo arregla**, y no
  tiene sentido exportar cookies de otra cuenta para intentarlo.
- La IP de salida es de Columbus, Ohio, Estados Unidos — pero de un rango de
  Google Cloud. Un país donde Flow opera y aun así rechaza: lo que no acepta es
  el tipo de red, no el país del usuario.
- Lo que sí funciona desde aquí: el navegador carga la portada de Flow, y **AI
  Studio entra autenticado** con las cookies de Google sin ningún problema. Así
  que el contenedor no está aislado de Google; es Flow en concreto quien cierra.
- Trampa aparte que cuesta una tarde: con locale `es-MX` en el navegador ni
  siquiera se llega a esa página, porque Google redirige antes a
  `/fx/es-419/tools/flow` y de ahí a la portada. Parece un fallo de sesión y no
  lo es. Con `?hl=en` o `/fx/en/tools/flow` se ve el mensaje real.

**Prueba de un minuto** para saber si algún día cambia (por ejemplo, si la sesión
remota pasa a salir por otra red): cargar esa URL sin cookies. Si no aterriza en
`unsupported-country`, entonces sí se puede automatizar todo lo que sigue.

Hasta entonces, este paso lo hace el humano desde su navegador. Y la única vía
realmente automatizable es una API de imágenes (ver el final del documento).

## Por qué Flow y no el generador gratuito

`visuals_gen.py` usa un servicio gratuito con un modelo pequeño. Cumple para
salir del paso, pero falla en lo concreto, y en un canal de historia lo concreto
es todo. Casos medidos:

- **Video 3** (documentado en CLAUDE.md): de 11 momentos muestreados, 6 traían
  imágenes ajenas al guion — un comedor con letrero en hebreo, una carta
  manuscrita en inglés, un salón de palacio.
- **Video 6** (la escuela): una maestra en shorts; una muchacha con sombrero de
  playa donde el guion pedía unas manos sosteniendo una boleta; y una falsa
  fotografía sepia de grupo escolar, que es justo lo que no debe fabricarse.
- **Video 7** (la consola, 12-ago): «pila de discos en fundas de papel» devolvió
  un plato abstracto; varios compases devolvieron salas vacías sin el mueble que
  era el tema del video.

Flow entrega Nano Banana 2 a 1376×768 —más grande y mucho más literal— y con
~7 pegadas cubre un video entero en vez de 159 generaciones sueltas.

## Preparación (una sola vez)

1. **Cuenta:** entrar a Flow con `lavidadeantes.oficial@gmail.com`. La otra
   cuenta del canal la rechaza.
2. **Permitir descargas múltiples** en Chrome para el sitio:
   `chrome://settings/content/automaticDownloads` → añadir
   `https://labs.google`. Sin esto, a partir de la segunda imagen el navegador
   bloquea la descarga en silencio.
3. Tener el repositorio actualizado (`git pull`) y el video ya con voz: los
   compases se anclan al `timing.json` real, no a una estimación.

## Los siete pasos

### 1. Generar los bloques
```bash
python3 pipeline/bloques_flow.py output/<slug>/
```
Escribe `output/<slug>/bloques_flow/bloque_NN.txt` (24 prompts cada uno) y
`mapa_compases.json`, que es lo que después devuelve cada imagen a su segundo
exacto del video. Cada prompt va numerado con tres cifras: ese número es su
compás.

### 2. Pegar un bloque en Flow (modo Agente)
**Un bloque a la vez, y proyecto nuevo para cada bloque.** Acumular bloques en el
mismo proyecto degrada el resultado y mezcla la galería.

El campo de texto de Flow es un componente de React y **no acepta que se le
inyecte el texto por JavaScript**: asignar `value` no dispara sus eventos, la
aplicación no se entera y responde *«Se debe proporcionar una instrucción»*. Hay
que enfocar el campo por JS y **escribir con teclado real**:

```js
document.querySelector('textarea').focus();   // solo enfocar
```
y a continuación teclear (`page.keyboard.type(...)` en Playwright, o pegado
manual). El foco por JS sí funciona; la escritura no.

**Nunca usar `cmd+a` (ni `ctrl+a`) para limpiar la caja.** Si el foco no está
donde uno cree, el `Backspace` siguiente se interpreta como «atrás» del
navegador y saca la sesión del proyecto, perdiendo lo generado.

### 3. Esperar y contar
**Flow se salta prompts sin avisar.** Contar siempre las imágenes generadas
contra las 24 del bloque antes de descargar. Las que falten se vuelven a pedir.

### 4. Descargar
**De a 6 como máximo.** Más descargas simultáneas y Chrome empieza a descartar
archivos silenciosamente.

Si se automatiza, `fetch()` sobre la URL de la imagen **falla**; hay que pasar la
imagen por un `canvas` y sacar los bytes de ahí:

```js
const c = document.createElement('canvas');
c.width = img.naturalWidth; c.height = img.naturalHeight;
c.getContext('2d').drawImage(img, 0, 0);
c.toDataURL('image/jpeg', 0.95);   // de aquí salen los bytes
```

### 5. Hojas de contactos
```bash
python3 pipeline/hoja_contactos.py <carpeta_descargas> output/<slug>/hojas/
```
Rejillas de 12 con un número grande sobre cada imagen, más `contactos.json` con
el índice número→archivo (y la carpeta de origen, para que el paso siguiente
encuentre los archivos aunque se le pase otra ruta).

### 6. Identificar (a ojo, no hay atajo)
Mirar las hojas y escribir el mapa `{compás: número}`:

```json
{"0": 7, "1": 3, "2": 11, "3": 0}
```

**Este paso no se puede automatizar.** Flow marca todas las imágenes como
«Imagen generada», sin ninguna otra pista en el HTML: ni el prompt, ni el orden,
ni un identificador. Y el orden de la galería **cambia al recargar**, así que
tampoco sirve fiarse de la posición. Hay que verlas.

### 7. Colocar y montar
```bash
python3 pipeline/colocar.py output/<slug>/ mapa.json <carpeta_descargas>
```
Copia cada imagen como `b###_t#######_flow.jpg` —el nombre con el que
`assemble.py` la ancla a su momento— y **avisa qué compases quedaron sin
imagen**. Ese aviso importa: un hueco silencioso hace que la imagen vecina se
estire sobre un tramo del guion al que no corresponde.

Después, lo de siempre:
```bash
python3 pipeline/nitidez.py output/<slug>/visuales-gen/
python3 pipeline/assemble.py output/<slug>/voz.mp3 output/<slug>/visuales-gen/ output/<slug>/final-limpio.mp4
python3 pipeline/subtitles.py output/<slug>/ && python3 pipeline/overlay_text.py output/<slug>/
python3 pipeline/quality_gate.py output/<slug>/
```

**Atajo si Flow permitió «Descargar proyecto»** (un zip con los números en los
nombres): `desde_flow.py` hace los pasos 5-7 de un tirón y no hace falta
identificar a ojo.
```bash
python3 pipeline/desde_flow.py output/<slug>/ ~/Descargas/flow.zip
```

## Límites que rompen el proceso si se ignoran

| Límite | Qué pasa si se ignora |
|---|---|
| Un bloque a la vez | La galería se mezcla y ya no se sabe qué es qué |
| Proyecto nuevo por bloque | Baja la calidad y se acumulan imágenes de otro bloque |
| Máximo 6 descargas juntas | Chrome descarta archivos sin decir nada |
| Contar siempre | Flow se salta prompts en silencio |
| No fiarse del orden de la galería | Cambia al recargar |
| Nada de `cmd+a` | El Backspace saca la sesión del proyecto |

## La salida de verdad

Todo esto —hojas de contactos, identificar a ojo, las caídas, el navegador
entero— existe solo porque no hay una API de imágenes disponible. **Con una API
de pago que funcione, los pasos 2 a 6 desaparecen**: queda un comando y el video
se produce solo, que es lo que se buscaba desde el principio.

`pipeline/visuals_google.py` ya está escrito y probado para eso (Gemini /
Nano Banana por API, mismos nombres de archivo, reanudable). Hoy no sirve porque
la cuenta responde `429 prepayment credits are depleted` — el nivel gratuito de
la API de Gemini no está disponible en todos los países, y en el de esta cuenta
la API arranca en pago anticipado con saldo cero. En cuanto ese proyecto tenga
crédito, o se contrate otro proveedor (fal.ai con FLUX, ~$0,003 por imagen),
este documento se vuelve innecesario.

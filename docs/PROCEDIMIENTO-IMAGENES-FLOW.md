# Cómo se hicieron las imágenes del video 6 con Google Flow

> Documento de traspaso. Escrito el 12-ago-2026, después de producir
> "16 millones de libros: así era la escuela de los años 70" (143 imágenes).
> Va dirigido a quien continúe el canal en otra máquina — persona o Claude.

---

## Por qué Flow y no el generador gratuito

`visuals_gen.py` usa Pollinations, que es gratis y se llama desde un script. Para
probar el pipeline sirve. **Para publicar no.**

En el video 6 generó 99 imágenes y hubo que tirarlas todas. Ejemplos reales:

| se pidió | devolvió |
|---|---|
| maestra de primaria de los años 70 en el salón | una muchacha joven **en shorts**, ropa actual |
| manos adultas sosteniendo una boleta vieja | una muchacha con sombrero de playa, al aire libre, con un papel en blanco |
| foto de grupo de fin de cursos | una **falsa fotografía sepia** con las caras deformes |

Ese último caso es el más grave: no es solo feo, es fabricar un registro histórico
falso de un pasado real. Está prohibido por las reglas del canal.

**Google Flow (Nano Banana 2)** devuelve acuarela de verdad, respeta la época y la
ropa, entiende la escena, y las imágenes salen a **1376×768 sin costar créditos**
(los créditos solo se gastan generando video, no imágenes).

---

## Lo que hay que tener listo una vez

1. **Extensión Claude in Chrome** instalada y con sesión iniciada.
2. **Cuenta de Flow: `lavidadeantes.oficial@gmail.com`.**
   La otra cuenta (`londonsamu@gmail.com`) la rechaza con
   *"Try signing in with a different account"*.
3. **Permiso de descargas múltiples**, una sola vez por computador:
   `chrome://settings/content/automaticDownloads` → Agregar → `labs.google`
   Sin esto, Chrome deja pasar la primera descarga y bloquea todas las demás en
   silencio.

En un computador o cuenta nuevos, Flow muestra además una pantalla de términos.
**Aceptarla es decisión del usuario, no de Claude.**

---

## El procedimiento, paso a paso

### 1. Preparar los bloques de prompts

```bash
python3 pipeline/bloques_flow.py output/<slug>/ 22
```

Escribe `output/<slug>/bloques_flow/bloque_NN.txt`. **22 prompts por bloque es el
tope práctico**: con más, Flow empieza a saltarse indicaciones.

Cabecera obligatoria en cada bloque (el estilo y la época van SIEMPRE, si no la
coherencia se pierde entre tandas):

> Formato 16:9 horizontal. Estilo común para TODAS: acuarela delicada sobre papel
> con textura visible, pinceladas sueltas, luz cálida y clara, alto contraste,
> paleta de tierras suaves. Época: México, años setenta. La ropa, los peinados y
> los objetos tienen que ser de esa época, nunca actuales. Sin texto, sin letras,
> sin marcos, sin marcas de agua.

Escribir los prompts **sin tildes ni eñes**: se teclean con eventos de teclado
sintéticos y los acentos no siempre entran bien.

### 2. Pegar el bloque en Flow

**Un proyecto nuevo por bloque.** No acumular todo en el mismo: pasando de unas
40 imágenes la galería se satura y la pestaña se cae, a veces con
*"Application error: a client-side exception has occurred"*.

El campo de texto de Flow **no acepta inyección por JavaScript**: si se le pone
el texto con `execCommand` o disparando un evento de pegado, el DOM lo muestra
pero React no se entera y al enviar responde *"Se debe proporcionar una
instrucción"*.

Lo que sí funciona: **enfocar por JavaScript y escribir con teclado real.**

```js
// 1) enfocar
const box = [...document.querySelectorAll('[contenteditable="true"]')]
  .find(e => e.getBoundingClientRect().width > 100);
box.focus();
const sel = window.getSelection(), r = document.createRange();
r.selectNodeContents(box); r.collapse(false);
sel.removeAllRanges(); sel.addRange(r);
```

Después, escribir el texto con la acción `type` de la extensión, en trozos de
unos 400 caracteres, y hacer clic en la flecha de enviar.

**No usar `cmd+a` ni `Delete`** para limpiar la caja: si el foco no está donde se
cree, selecciona toda la página y el Backspace navega hacia atrás. Ya pasó una
vez y sacó la sesión del proyecto.

Verificar siempre con una captura que el envío entró: en una ocasión el clic no
registró y el prompt se quedó ahí, aparentemente enviado.

### 3. Esperar

Una tanda de 22 tarda unos minutos. Está lista cuando desaparece
*"Cancelar la solicitud"* y aparece *"He generado..."*:

```js
({ generando: /Cancelar la solicitud|Pensando/i.test(document.body.innerText),
   imgs: [...document.querySelectorAll('img')].filter(i => i.naturalWidth > 200).length })
```

**Contar siempre.** Flow se salta indicaciones sin avisar: pidiendo 6 generó 5,
pidiendo 22 generó 18. Lo que falte se vuelve a pedir en otra tanda.

### 4. Descargar

Las imágenes son del mismo origen que la página, así que se pueden pasar por un
`canvas` y descargar sin problemas de CORS. Un `fetch` directo **no** funciona.

**Máximo 6 por llamada.** Más de eso congela el renderizador y la llamada muere
con *"CDP sendCommand Runtime.evaluate timed out"*.

```js
window.__v = window.__v || [];
const todas = [...document.querySelectorAll('img')].filter(i => i.naturalWidth > 200);
const nuevas = todas.filter(i => !window.__v.includes(i.src)).slice(0, 6);
for (const im of nuevas) {
  const c = document.createElement('canvas');
  c.width = im.naturalWidth; c.height = im.naturalHeight;
  c.getContext('2d').drawImage(im, 0, 0);
  const a = document.createElement('a');
  a.href = c.toDataURL('image/jpeg', 0.92);
  a.download = `f_${String(window.__v.length).padStart(3, '0')}.jpg`;
  document.body.appendChild(a); a.click(); a.remove();
  window.__v.push(im.src);
}
({ acum: window.__v.length, enDOM: todas.length })
```

Repetir hasta que `acum` deje de subir; entonces desplazar la galería y seguir.
La lista es virtualizada: solo hay unas 24 imágenes en el DOM a la vez.

Si la pestaña se cae, **recargar y continuar**: las imágenes ya están guardadas
en el proyecto, no se pierde nada. Ojo: al recargar **cambia el orden de la
galería** (unas veces las nuevas primero, otras las viejas). Nunca dar el orden
por supuesto.

Mover lo descargado a la carpeta de trabajo:

```bash
cd ~/Downloads && for f in f_*.jpg; do
  mv "$f" ~/youtube-factory/output/<slug>/_flow_nuevo/b1_${f#f_}
done
```

### 5. Identificar cuál es cuál — el paso que no se puede automatizar

**Flow no guarda qué prompt generó cada imagen.** En el HTML todas aparecen como
`alt="Imagen generada"`, sin ninguna otra pista. Y como el orden no es fiable,
no queda más que mirarlas.

```bash
python3 pipeline/hoja_contactos.py output/<slug>/_flow_nuevo b1
```

Eso arma una hoja con todas las miniaturas y su nombre escrito encima. Se lee de
una sola vez y se escribe el mapa a mano:

```json
{"0": "b1_012", "1": "b1_013", "2": "b1_014", "51": "b1_019"}
```

Es normal que en la hoja aparezcan repetidas de tandas anteriores: se descartan.

### 6. Colocar en su compás

```bash
python3 pipeline/colocar.py output/<slug>/ mapa.json
```

Renombra cada imagen a `b###_t#######_flow.jpg` e informa la cobertura y los
compases que quedaron sin imagen. **No montar hasta que la cobertura esté
completa.**

Un mismo archivo puede ir a varios compases: los planes repiten prompts dentro de
una sección, así que reutilizar variantes está previsto y no se nota.

### 7. Montar

```bash
J=output/<slug>
python3 pipeline/nitidez.py $J/visuales-gen        # ESPCN x2
python3 pipeline/assemble.py $J/voz.mp3 $J/visuales-gen $J/final-limpio.mp4
python3 pipeline/subtitles.py $J
python3 pipeline/overlay_text.py $J
python3 pipeline/quality_gate.py $J
```

Antes de publicar, extraer fotogramas y revisarlos: ¿la imagen corresponde a lo
que se está narrando? ¿es de época? ¿hay alguna que parezca una fotografía
histórica real? Esa revisión **la hace Claude mirando**, no un script — las
reglas no detectan una maestra en shorts.

---

## Cuánto cuesta esto en tiempo

El video 6, con 143 imágenes: **5 tandas y unas 3 horas**, incluidas tres caídas
de la página. Sale a unos 20 minutos por tanda de 22.

---

## La alternativa que elimina todo esto

Una **API de imágenes de pago** (Gemini/Imagen). Se llama desde un script,
devuelve cada imagen ya asociada a su prompt —sin hojas de contactos, sin
identificar a ojo—, no se cae y no necesita navegador.

Con eso el ciclo completo queda desatendido de verdad: guion, voz, imágenes,
montaje, miniatura, control de calidad y subida, en un cron diario.

Ya hay una clave de Gemini configurada; al probarla el error fue
*"Your prepayment credits are depleted"*, así que solo falta ponerle saldo.
Generar imágenes cuesta centavos por unidad — nada que ver con los ~250 USD
mensuales que cuesta generar video.

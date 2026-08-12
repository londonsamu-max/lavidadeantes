# Exploración: segundo canal animado — datos reales (27 julio 2026)

Fuente: YouTube Data API v3, ventana de 90 días, `order=viewCount`, `relevanceLanguage=es`.
Scripts: `pipeline/scout_nicho.py` (barrido de nicho) y `pipeline/auditar_canal.py`
(auditoría de canal). Datos crudos en `data/scouting/*.json`.

**Por qué mediana y no media:** un solo viral infla el promedio y hace parecer sano un
canal que no lo está. La mediana dice qué rinde un video *normal*, que es lo que uno
publica el 90 % de las veces.

---

## Resultado por nicho

### 1. Mitología / leyendas latinas animadas → EL ÚNICO CON PRUEBA RECIENTE

Empíricamente este nicho no existe puro: se fusiona con el relato animado de terror.
La referencia decisiva:

| Canal | Nacido | Subs | Mediana vistas | % > 100k | Duración | Ritmo |
|---|---|---|---|---|---|---|
| **Arándano 13 (Animado)** | 10-feb-2026 | 83.700 | **158.324** | **69 %** | 28 min | 10/mes |
| Glenn – Sector del Terror | ene-2023 | 485.000 | 92.662 | 45 % | 53 min | 11/mes |

Arándano 13 es la prueba de que **hoy todavía se puede entrar**: 5 meses de vida, ritmo
humano-sostenible (10/mes, dentro de la regla de supervivencia), formato de lista de
28 min. Con 6 veces menos suscriptores que Glenn, saca **70 % más vistas por video**.

⚠️ **Pero Arándano 13 está pisando la mina que mató a los otros.** Sus últimos títulos:
«TERROR de MICKEY y CHUCK E CHEESE», «TERROR de TINDER». Eso es IP de terceros — la
causa exacta de la caída de Cuentos Fascinantes. Su modelo es replicable; su elección
de temas, no.

### 2. Personaje animal serializado → DESCARTADO POR LOS DATOS

En español no aparece **ni un solo entrante reciente** con el modelo. Lo que hay:

- Canales infantiles establecidos → clasificador "hecho para niños", **−80 % de ingreso**
- Resubidas de películas completas (Energía Plus Familia: 83 min/video; Consuegros: 139 min)
- Canales de clips a 30 videos/mes → otro negocio, no es producción propia

La hipótesis de partida venía de casos en inglés e hindi (*Bandar Apna Dost*). **En
español el nicho no está probado**, y además arrastra la penalización COPPA.

### 3. Relatos cotidianos animados → LLEGAMOS TARDE

| Canal | Subs | Mediana | Últimos 5 videos |
|---|---|---|---|
| Mi Diario Animado Español | 465.000 | 94.761 | 1.938 · 19.262 · 20.730 · 44.192 · 17.070 |

Los últimos videos rinden **entre 2 % y 46 % de su propia mediana**. Ese patrón —canal
grande, publicación constante, vistas desplomándose— es la firma de un formato saturado.
Entrar ahí sería competir por una audiencia que ya se está yendo.

---

## El problema que ningún tutorial menciona: Anuncios Limitados

El contenido de terror cae bajo «puede impactar o asustar a menores» en las normas para
anunciantes → **Anuncios Limitados**, que rinden **20-50 % de la monetización completa**.

Cuentas sobre el mejor caso medido (Arándano 13):

```
1.580.000 vistas/mes  (158k mediana × 10 videos)
RPM animación LATAM español ......... $0,50 – $1,10
con Anuncios Limitados .............. $0,15 – $0,55
                                      ─────────────
Ingreso mensual estimado ............ $237 – $869
Costo de producción (10 × $34) ...... $340
                                      ─────────────
Margen .............................. −$103  a  +$529
```

**Al nivel de un canal que ya funciona muy bien, el negocio apenas empata.** Solo se
vuelve interesante bastante por encima de esa marca. Es un riesgo real, no un detalle.

---

## Recomendación

**Leyendas y mitología latinoamericana animadas** — el formato probado de Arándano 13,
pero con el material que a él le falta y a nosotros nos sobra: **guion original y
documentado, sobre folclore de dominio público**.

Qué resuelve cada pieza:

| Riesgo | Cómo se neutraliza |
|---|---|
| IP de terceros (mató a Cuentos Fascinantes) | La Llorona, el Sombrerón, el Silbón: folclore libre |
| Anuncios Limitados por terror gráfico | Registro de leyenda/documental, no *creepypasta* con sangre |
| Clasificación "hecho para niños" (−80 %) | Registro adulto, narración documental |
| Agrupación por pipeline (S-CTS) | Voz distinta, estilo visual distinto, cuenta distinta, guion propio |
| Cebo de interacción (mató a Imperio de Jesús) | Prohibido por norma en el *quality gate* |

Y hay una ventaja que no se compra: el pipeline ya sabe **investigar y escribir guiones
originales documentados de 3.000+ palabras**. Es justo lo que separa a un canal que
sobrevive de uno que el detector agrupa con otros mil.

**Condición innegociable:** canal aparte, identidad aparte, voz aparte. La Vida de Antes
sigue intacta con su ciclo diario.

---

## ¿De dónde sale la animación de Arándano 13? (verificado en pantalla)

**No la produce.** Dentro del video, abajo a la izquierda, hay una marca de agua fija:
**SSG ANIMATIONS**. Arándano 13 **licencia y dobla al español** animaciones de terror
en inglés de ese estudio.

El estilo tampoco es *stickman*: son **personajes vectoriales planos con rig** (animación
limitada — ciclos de caminata, cabezas parlantes, poco movimiento por plano), paleta
apagada, subtítulos quemados y el avatar del canal como mosca en la esquina.

SSG vende esto abiertamente en `ssganimations.com/dubbing-rights/`:

> «Commercial Dubbing License — Only $10 USD Per Story». Licencia comercial escrita,
> idiomas ilimitados, distribución global, pago único de por vida.

Precio real observado: **$1 a $30 por idioma y por historia** (se eligen los idiomas en
un selector; el más pedido, *THE BASEMENT TAPES*, cuesta $30 por idioma).

### ¿Es legal y monetizable? Sí, pero por una razón concreta

Doblar contenido ajeno **no** es monetizable por sí solo: cae en la norma de contenido
reutilizado. La excepción es exactamente ésta — una **licencia estructurada con el dueño
del contenido**, con derechos definidos por escrito. La licencia de SSG cumple.

### Los dos frenos reales

1. **El catálogo público tiene 3 títulos.** Contados en la página. A 10 videos/mes se
   agota en una semana. Arándano 13 debe tener un acuerdo directo, no la tienda pública.
2. **En ninguna parte dice "exclusivo".** Si otro canal compra el español de la misma
   historia, salen dos videos casi idénticos — justo la señal que agrupa el detector.
   Es **la pregunta que hay que hacerles antes de pagar un dólar**.

### Producirlo nosotros: la cuenta no da

| Vía | Costo | Veredicto |
|---|---|---|
| Estudio / freelance por minuto | $200 – $2.500 /min | 28 min = **$5.600 mínimo**. Imposible |
| Fiverr por proyecto | $40 – $467 | Es tarifa de explainer de 60-90 s, no de 28 min |
| Cartoon Animator 5 (licencia propia) | pago único | El software no es el freno: **el trabajo sí**. Riggear y animar 28 min a mano, 10 veces al mes, es un empleo de tiempo completo |
| IA de video (Kling, Runway) | por clip | Clips de 5-10 s, personaje inconsistente entre planos. No sostiene una narración de 28 min |

**Producir la animación completa cuadro a cuadro no da.** Pero descomponer el estilo en
sus dos piezas sí — ver abajo.

---

## La ruta que SÍ da: descomponer el estilo (probado 27-jul-2026)

El estilo se compone de dos cosas, y tienen costos radicalmente distintos:

### Pieza 1 — Ilustración de personaje consistente · **PROBADO, GRATIS**

`https://image.pollinations.ai/prompt/<prompt>?width=1280&height=720&seed=N`

Sin API key, sin registro. Tres escenas distintas del mismo personaje salieron
reconociblemente idénticas (mismo pelo, misma chaqueta, misma cara, mismo trazo):
pelo rizado negro, chaqueta verde, contorno fino, paleta desaturada.

**Método de consistencia:** *prompt* de personaje fijo y detallado + `seed` fijo +
la escena como sufijo variable.

Medido en vivo:

| Métrica | Valor real |
|---|---|
| Tiempo por imagen | **~42 s** (secuencial) |
| Concurrencia | **1** — el free tier responde `Queue full for IP (max: 1)` |
| Resolución | 1280×720 solicitado → 1024×576 entregado |
| Costo | **$0** |
| 150 imágenes = 1 video | **~1 h 45 min** desatendido |

⚠️ El free tier ignoró `model=flux` y sirvió otro modelo. La calidad salió bien igual,
pero el modelo no es controlable sin cuenta de pago.

### Pieza 2 — Movimiento · **NO probado (requiere clave de pago)**

Precios de mercado julio 2026, imagen→video:

| Modelo | Precio | Clip de 5 s |
|---|---|---|
| **Seedance 2.0 Fast** | $0,022/s | **$0,11** |
| Kling 3.0 | $0,029/s | $0,15 |
| Hailuo 02 (512p) | $0,017/s | $0,09 |

Dos escenarios para un video de 28 min (1.680 s):

- **Animado completo:** 1.680 s × $0,022 = **$37/video** ($370/mes)
- **Híbrido** (ilustración con Ken Burns + 35 momentos clave animados de 5 s):
  35 × $0,11 = **$3,85/video** (~$39/mes)

### Costo total real del video de 28 min

| Partida | Costo |
|---|---|
| ~150 ilustraciones consistentes | $0 |
| 35 momentos animados | $3,85 |
| Narración (edge-tts) | $0 |
| **Total por video** | **≈ $4** |
| **10 videos/mes** | **≈ $40** |

Frente a los $34/video que estimé antes y los $5.600 de animación real. **Con $40/mes
el punto de equilibrio cae de 300.000 vistas/mes a unas 40.000-80.000** — deja de ser
un negocio de todo o nada.

---

## Planes de suscripción plana (verificado en las páginas de precios, 27-jul-2026)

Objetivo: **1 video/día = 30 videos/mes** → ~4.500 imágenes y ~1.050 clips animados al mes.

### Imágenes → SÍ existe, y es barato

**Krea** (`krea.ai/pricing`, precios anuales, −40 %):

| Plan | Precio | Unidades/mes | Videos Seedance 2.0 |
|---|---|---|---|
| Free | $0 | 100/día | <1 |
| **Basic** | **$5/mes** (anual) · $9 mensual | 5.000 | 20 |
| Pro | $21/mes (anual) · $35 mensual | 20.000 | 83 |
| Max | $63/mes (anual) · $105 mensual | 60.000 | 250 |

La clave está en la letra chica, textual de la página:

> «**Unlimited relaxed generations** — Continue generating with **in-house image models**
> (Krea 2, Krea 1, Flux, Z-image, or Qwen) after exhausting your compute units.»

O sea: **imágenes ilimitadas de verdad**, en cola lenta, en todos los planes. Basic
($5/mes anual) es el primero que declara explícitamente «Commercial license — use all
generated content for commercial purposes», que es obligatorio para un canal monetizado.

**Las 4.500 imágenes/mes quedan cubiertas por $5.**

### Video → NO hay plan plano que cubra 1.050 clips/mes, salvo uno

| Plataforma | Qué promete | Realidad verificada |
|---|---|---|
| Krea | «Unlimited relaxed» | **Solo imágenes.** El video siempre consume unidades. Max = 250 clips/mes |
| Freepik / Magnific | «Unlimited AI video» | El ilimitado cubre ~10 modelos **de imagen**; el video siempre gasta créditos |
| Higgsfield | «Unlimited» $49/mes | Ha redefinido «unlimited» 3 veces en 2026; tope de uso justo a los pocos cientos de generaciones y luego cola de mínima prioridad |
| ~~Runway Unlimited~~ | ~~Ilimitado real en Explore Mode~~ | **YA NO SE PUEDE CONTRATAR** — ver corrección abajo |

### ⛔ CORRECCIÓN — Runway ya no ofrece video ilimitado

Verificado en la documentación propia de Runway (`help.runwayml.com`, artículo actualizado
1-jun-2026). Textual:

> «**Why we're moving to a credit-based model** — With the addition of the Max plan,
> **we are phasing out the Unlimited plan.** […] we're moving to a clearer credit-based
> structure.»

> «**Does the Max plan include Explore Mode?** — While **Explore Mode won't be available
> on the Max plan**, you'll have access to 9,500 monthly credits.»

Explore Mode era el modo sin créditos que hacía real el "ilimitado". **Max no lo tiene.**

Calendario: Max reemplazó a Unlimited para **nuevos suscriptores el 1-jun-2026**; los
antiguos migran el **1-sep-2026**. Hoy (27-jul-2026) **no es posible contratar Unlimited**.

**Qué rinden los 9.500 créditos de Max ($95/mes):**

| Modelo | Costo | Clips de 5 s al mes |
|---|---|---|
| Gen-4 Turbo | 5 créditos/s | **380** |
| Gen-4.5 | 25 créditos/s | **76** |

Comparado con pago por uso al mismo volumen (350 clips): Seedance 2.0 Fast = **$38,50**.
**La suscripción cuesta 2,5 veces más que el pago por uso, y encima con tope.**

### Conclusión sobre suscripciones planas

- **Imágenes: sí existe y vale la pena.** Krea Basic $5/mes, ilimitadas de verdad.
- **Movimiento: no existe ninguna que valga la pena.** Todas las que prometen "ilimitado"
  o excluyen el video (Krea, Freepik) o lo racionan con tope de uso justo (Higgsfield),
  y la única que era real (Runway Explore Mode) está siendo eliminada.

El movimiento **hay que pagarlo por uso**. La buena noticia: a 10 videos/mes son $38, un
gasto tan predecible como una suscripción.

### Stack recomendado

| Cadencia | Imágenes | Movimiento | Total/mes |
|---|---|---|---|
| **10 videos/mes** | Krea Basic $5 (plano) | 350 clips por uso = $38 | **≈ $43** |
| 30 videos/mes | Krea Basic $5 (plano) | 1.050 clips por uso = $115 | ≈ $120 |

### ⚠️ Choque con la regla de supervivencia

**1 video/día = 30/mes contradice el dato central de la investigación.** Arándano 13
publica 10/mes; *Bandar Apna Dost*, 8/mes. La cadencia humana-sostenible fue **una de las
seis señales de supervivencia**, y un canal nuevo de animación IA publicando 30/mes es
exactamente el perfil que el S-CTS agrupa.

A 10/mes todo encaja además mejor: $43/mes, sin plan plano de video, sin cola de 20 min.
La cadencia diaria tiene sentido en La Vida de Antes —que ya está establecido y no es
animado— pero es el riesgo principal en el canal animado.

### Lo que hay que reconocer

Nuestro pipeline actual produce **cómic en movimiento** (imagen fija + Ken Burns), no
animación. Con la pieza 1 sola, el salto visual ya es enorme respecto a las fotos de
archivo. La pieza 2 es lo que cierra la diferencia con Arándano 13, y cuesta $4.

## Antes de comprometer un peso

1. **Piloto de 3 videos** antes de decidir nada. Si la mediana no llega a 20.000 vistas
   en 30 días, se cierra y se pierde $102, no $340 al mes.
2. **Medir la etiqueta de monetización real** en el video 1. Si sale Anuncios Limitados,
   la cuenta de arriba se va al peor extremo y hay que suavizar el registro.
3. **Verificar el clasificador infantil** en el video 1. Si YouTube lo marca como
   contenido para niños, el nicho deja de tener sentido económico.

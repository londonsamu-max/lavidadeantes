# Costos y uso por créditos — investigación 27-jul-2026

---

## ✅ PRUEBA EN VIVO — Google Flow, 27-jul-2026, cuenta londonsamu@gmail.com

Se generó un clip de stickman real para medir el consumo, no estimarlo.

| Medición | Resultado |
|---|---|
| Saldo inicial | **50 créditos** («Los créditos se actualizan a diario» = nivel gratuito) |
| Aviso previo de Flow | «¿Quieres que inicie **1 generación de video por 10 créditos**?» + Aprobar/Rechazar |
| Saldo final | **40 créditos** |
| **Consumo real** | **10 créditos exactos** por 1 clip de Veo 3.1 Lite |
| Marca de agua | **«Veo» visible**, esquina inferior derecha — confirmado ampliando el frame |
| Cola | «debido a la alta demanda, está en cola y tardará un poco más» |

**La tabla oficial de Google es exacta.** 10 créditos por generación de Veo 3.1 Lite,
verificado con saldo antes y después.

### Tres trampas de configuración encontradas en la interfaz

1. **El modelo de video por defecto es «Omni Flash», no Veo 3.1 Lite.** Omni Flash cuesta
   15/20/25/30 créditos según duración — hasta **3× más caro**. Hay que cambiarlo a mano
   en Configuración de agentes.
2. **Las imágenes vienen en «x2» por defecto**: cada pedido genera dos y cobra doble.
   Bajarlo a x1.
3. **«Confirmar antes de generar» viene en «Siempre»** — conviene dejarlo así. La opción
   «Nunca» gasta créditos automáticamente sin avisar.

### Hallazgo adicional: Flow ya trae hoja de personaje

La interfaz incluye una sección **Personajes**: *«Define their look, voice, and personality
once. Reference them anywhere with a simple @tag»*. Es la técnica del character sheet
integrada en el producto — no hay que construirla aparte.

### Extrapolación con datos medidos

- 50 créditos/día = **5 clips de 8 s por día** = 40 segundos de animación diarios
- Video híbrido (35 clips) = 350 créditos = **7 días de cuota gratuita**
- Video de 28 min animado completo (210 clips) = 2.100 créditos = **42 días de cuota**

El nivel gratuito da ~4 videos híbridos al mes, cada uno tardando una semana en juntar
la cuota, **y todos con la marca de agua «Veo» quemada**.

---

Fuentes: páginas oficiales de cada plataforma, no blogs.
- Google Flow: `support.google.com/flow/answer/16526234` (tabla oficial de créditos)
- Krea: `krea.ai/pricing` (texto de las propias tarjetas de plan)
- Runway: `help.runwayml.com` (artículos de plan)
- Precios de API imagen→video: comparativas de mercado (menor confianza, marcadas)

---

## 1. Google Flow — tabla oficial de créditos

**Cuántos créditos recibes**

| Nivel | Créditos |
|---|---|
| Sin suscripción | **50 por día** (no se acumulan) |
| Google AI Plus | 200/mes |
| Google AI Pro ($19,99) | 1.000/mes |
| Google AI Ultra $100 | 10.000/mes |
| Google AI Ultra $200 ($249,99) | 25.000/mes |

Los créditos mensuales **no se transfieren** al mes siguiente.

**Cuánto cuesta cada generación** (por generación, no por solicitud)

| Modelo | Duración | No-Ultra | Ultra |
|---|---|---|---|
| Veo 3.1 **Lite** | 4, 6, 8 s | **10** | **5** |
| Veo 3.1 **Fast** | 4, 6, 8 s | 20 | 10 |
| Veo 3.1 **Quality** | 8 s | 100 | 100 |
| Gemini Omni Flash | 4/6/8/10 s | 15/20/25/30 | igual |
| Omni Flash (editar) | cualquiera | 40 | igual |
| Subir a 1080p | — | **no disponible sin suscripción** | 0 |
| Subir a 4K | — | no disponible | 50 |

**Dato clave:** el precio por generación es el mismo para 4, 6 u 8 segundos. **Siempre
pedir 8 s** — pedir 4 s cuesta lo mismo y rinde la mitad.

**Segundo dato clave:** Ultra paga la mitad por generación (5 en vez de 10). El descuento
por volumen está en el precio unitario, no solo en la cantidad.

### Costo real por segundo de animación (Veo 3.1 Lite, 8 s por generación)

| Plan | Precio | Segundos/mes | **$ por segundo** |
|---|---|---|---|
| Gratis (50/día) | $0 | 1.200 | $0 |
| AI Pro | $19,99 | 800 | **$0,025** |
| **AI Ultra $100** | $100 | 16.000 | **$0,00625** |
| **AI Ultra $200** | $249,99 | 40.000 | **$0,00625** |
| *Seedance 2.0 Fast (API)* | por uso | ilimitado | *$0,022* |

**Los dos niveles Ultra cuestan lo mismo por segundo.** Elegir según volumen, no según
precio unitario: Ultra $100 si necesitas ≤16.000 s/mes, Ultra $200 si necesitas más.

**Ultra es 3,5 veces más barato por segundo que pagar por uso con Seedance.**

### Cuántos videos salen

Video de 28 min con animación completa = 1.680 s. Híbrido (35 clips de 8 s) = 280 s.

| Plan | Videos híbridos/mes | Videos animados completos/mes |
|---|---|---|
| Gratis | 4,2 | 0,7 |
| AI Pro $19,99 | 2,8 | 0,5 |
| AI Ultra $100 | 57 | **9,5** |
| AI Ultra $200 | 142 | **23,8** |

### ⛔ La marca de agua — VERIFICADO en documentación de Google

`support.google.com/flow/answer/16353333`, textual:

> «Los videos generados en los niveles **Gratis, Plus y Pro** de Google One incluyen una
> **marca de agua visible** que indica que el contenido se creó con Veo. Los videos
> generados en el nivel de **Google AI Ultra** contienen una marca de agua visible
> cuando así lo exigen las reglamentaciones locales.»

**Gratis, Plus y Pro salen con «Made with Veo» quemado en el video. Solo Ultra sale limpio.**

Esto invalida la idea de usar AI Pro ($19,99) para un piloto: el video sale marcado y no
sirve para un canal serio. **Para video usable, el escalón mínimo es Ultra.**

### Derechos comerciales — VERIFICADO

Misma página, textual:

> «Las Condiciones del Servicio rigen el uso de estas herramientas... algunos de nuestros
> servicios te permiten generar contenido original. **Google no reclamará la propiedad de
> ese contenido.**»

No distingue entre niveles: la propiedad del resultado es del usuario en todos. Lo que
cambia entre niveles **no es la licencia, es la marca de agua**. Los blogs que dicen «el
nivel gratuito no tiene derechos comerciales» no coinciden con lo que dice Google.

### Otros límites del nivel gratuito

- **1080p no disponible** — confirmado en la tabla oficial de créditos. Se queda en 720p.
- 5 clips por día máximo, sin acumular: no se puede producir un video en un día.

Todas las salidas de Veo llevan **SynthID**, marca invisible, en todos los niveles.

### Precios en Colombia (USD/COP 3.207 al 27-jul-2026)

| Nivel | Precio | USD aprox. | Créditos | Segundos/mes | Videos completos/mes |
|---|---|---|---|---|---|
| Ultra «5 veces» | **COP 449.000** | $140 | 10.000 | 16.000 | **9,5** |
| Ultra «20 veces» | COP 790.000 | $246 | 25.000 | 40.000 | 23,8 |

A diferencia de EE.UU., en Colombia los niveles **no** cuestan lo mismo por segundo:
COP 28,06/s el de 5 veces contra COP 19,75/s el de 20 veces.

---

## ¿Hay acceso sin gastar créditos por clip?

**No en planes de pago: todos son medidos por generación.** Verificado en Google, Krea,
Runway, Higgsfield y Freepik. Ninguno ofrece video ilimitado.

Lo que sí existe son **niveles gratuitos**, que no son «acceso regalado» sino cuotas con
sus propias restricciones:

| Vía | Límite | Marca de agua | ¿Sirve para monetizar? |
|---|---|---|---|
| Google Flow gratis | 50 créditos/día (5 clips) | **visible** | No |
| Google AI Pro | 1.000 créditos/mes | **visible** | No |
| **Google AI Ultra** | 10.000–25.000/mes | limpio | **Sí** |
| Meta AI en WhatsApp | sin cuota publicada | por verificar | por verificar |
| Grok / Seedance free | cuota diaria | por verificar | por verificar |

Los planes de **Google Workspace** aptos (Business/Enterprise/Education) incluyen Flow
con 50 créditos diarios sin cargo adicional — misma cuota que el nivel gratuito.

---

## 2. Krea — unidades por generación

**Planes (facturación anual)**

| Plan | Precio | Unidades/mes | Concurrencia img | Concurrencia video | Imágenes por LoRA |
|---|---|---|---|---|---|
| Free | $0 | 100/día | 1 | 0 | 50 |
| Basic | $5 | 5.000 | 4 | 2 | 50 |
| Pro | $21 | 20.000 | 8 | 4 | 50 |
| **Max** | **$42** (40k) … $99 (100k) | 40.000–100.000 | **ilimitada** | **ilimitada** | **2.000** |

**Costo unitario** (derivado de las cifras de la propia página)

| Generación | Unidades |
|---|---|
| Nano Banana 2 (imagen) | **78** |
| Seedance 2.0 (video) | **241** |

Los modelos propios (Krea 2, Krea 1, Flux, Z-image, Qwen) cuestan menos, pero Krea **no
publica** su tarifa unitaria. No asumir un número.

**«Unlimited relaxed generations» — la letra chica exacta:**

> «Continue generating with **in-house image models** (Krea 2, Krea 1, Flux, Z-image, or
> Qwen) after exhausting your compute units.»

Solo **imágenes**, solo **modelos propios**, y solo **Max**. El video siempre consume
unidades en todos los planes. La licencia comercial empieza en Basic: **el plan Free no
la tiene**.

---

## 3. Runway — ya no aplica

Runway elimina el plan Unlimited. Textual: *«we are phasing out the Unlimited plan»*.
El plan Max que lo reemplaza **no incluye Explore Mode** (el modo sin créditos):
9.500 créditos/mes, Gen-4 Turbo a 5 créditos/s → **380 clips de 5 s**, $95/mes.
Equivale a **$0,05/s**: el doble de caro que Seedance y 8 veces más que Ultra.

---

## Conclusiones

**Imágenes.** Pollinations gratis cubre nuestro volumen; el costo es tiempo (1 concurrente,
~42 s por imagen, 1 h 45 por video). Krea Max ($42) compra dos cosas que no se compran
con paciencia: **concurrencia ilimitada** (de 1 h 45 a minutos) y **LoRA de 2.000 imágenes**
(personaje y estilo genuinamente propios, no «parecidos»).

**Movimiento.** No existe plan plano. Pero **Google AI Ultra es la opción más barata por
segundo del mercado**: $0,00625/s contra $0,022 de Seedance y $0,05 de Runway.

**El escalón que importa está entre AI Pro y AI Ultra $100**, no entre gratis y Pro:

- AI Pro ($19,99) rinde **medio video animado al mes**. Es un plan para probar, no para producir.
- AI Ultra $100 rinde **9,5 videos animados completos al mes**. Es un plan de producción.
- Entre los dos hay 5× de precio y **19× de capacidad**.

**Para el piloto de 3 videos:** el nivel gratuito (50 créditos/día) da 4,2 videos híbridos
al mes, más que AI Pro. Sirve para validar el formato **si y solo si** se confirma que la
marca de agua visible y los derechos comerciales no lo impiden — hay que verificarlo
generando un clip antes de construir nada encima.

# SISTEMA DE VARIEDAD — Anti-repetición (v1)
> Doble propósito: (1) que el espectador no sienta "otro video igual", (2) defensa
> contra la política de "contenido inauténtico" (el 95-97% de los desmonetizados
> reciclaban plantilla/imágenes/guion). La CONSISTENCIA de marca se mantiene
> (misma voz, mismo saludo, mismo look) — lo que rota es el CONTENIDO y la ESTRUCTURA.

## 1. Rotación de FORMATOS (nunca 2 videos seguidos del mismo)
| # | Formato | Ejemplo |
|---|---|---|
| F1 | Lista de objetos/cosas (25 items) | "25 cosas que había en toda casa de los 70" |
| F2 | Un solo tema a profundidad | "La historia de la Singer: la máquina que vistió a Latinoamérica" |
| F3 | Un día en la vida | "Así era un domingo en 1975, de la misa al mercado" |
| F4 | Antes vs ahora | "Lo que costaban las cosas en 1978 (y lo que cuestan hoy)" |
| F5 | Recorrido por lugar | "El mercado del pueblo: pasillo por pasillo" |
| F6 | Oficios y personajes | "El afilador, el bolero, el merolico: los oficios que gritaban" |
| F7 | Por década específica | "1972: el año en que llegó la TV a color" |
| F8 | Preguntas y recuerdos de la audiencia | "Ustedes contaron, nosotros investigamos: sus recuerdos del barrio" |

Registro en `data/registro-contenido.json` → el cerebro consulta los últimos 7 formatos usados antes de elegir.

## 2. Rotación de HOOKS (4 tipos, ciclar)
- H1 Reconocimiento: "¿Cuántas de estas tenía usted?"
- H2 Dato incompleto: "En 1975 casi nadie tenía esto; hoy nadie vive sin ello"
- H3 Viaje temporal: "Hoy volvemos a 1978. Cierre los ojos conmigo"
- H4 Objeto misterioso: "Este objeto estaba en todas las casas. Los menores de 40 no saben qué es"

## 3. TEMAS: nunca repetir, siempre registrar
- Cada item/tema usado se registra en `registro-contenido.json` (ej: "molinillo", "olla exprés")
- Un objeto ya usado en una lista PUEDE volver como F2 (profundidad) — es otro ángulo, no repetición
- Regla de solape: máximo 3 items repetidos entre dos listas cualesquiera
- Fuente de temas nuevos: outliers de referencias (adaptados) + comentarios de la audiencia (F8) + calendario estacional (Navidad de antes, lluvias, día de la madre)

## 4. VISUALES: cero reciclaje (crítico para monetización)
- `visuals.py` registra cada URL usada en `data/imagenes-usadas.json` y NO re-descarga una imagen ya usada en otro video
- Variar fuentes por video: mezclar % distinto de Wikimedia / LOC / Pexels / IA
- Variar patrón Ken Burns (ya alterna zoom-in/out y paneos)
- Cuando haya generación IA: prompts únicos por video, jamás re-render del mismo prompt

## 5. MÚSICA: pool rotativo
- Mínimo 6-8 pistas en assets/music/ — el pipeline elige aleatorio, sin repetir la del video anterior
- Por canal: pool PROPIO (dos canales jamás comparten música)

## 6. GUION: variación estructural dentro de la consistencia
- Mismo saludo/despedida (parasocial) PERO: orden de recorrido distinto, número de items variable (10/15/20/25), posición del loop abierto variable, recapitulación en momento distinto
- El "número prometido" del loop cambia de posición (a veces el 25, a veces el 7...)
- Longitud variable: 15-30 min según formato

## 7. MULTI-CANAL: identidades estancas
- Cada canal: voz distinta + tipografía distinta + filtro de color distinto + música distinta + estructura de miniatura distinta
- PROHIBIDO cruzar assets entre canales (patrón de "granja" detectable)

## 8. Revisión mensual del cerebro
- Leer métricas: ¿qué formatos retienen más? → subir su frecuencia sin eliminar la rotación
- Si un formato decae 3 videos seguidos → descansarlo 1 mes
- Actualizar este documento con lo aprendido

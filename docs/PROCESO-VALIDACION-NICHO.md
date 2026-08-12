# PROCESO ESTÁNDAR DE VALIDACIÓN DE NICHO (v1 — jul 2026)
> Replicable para cada canal nuevo. El que validó "La Vida de Antes".
> Comando: decirle a Claude "valida el nicho X con el proceso estándar"

## FASE 1 — Investigación triple (3 agentes en paralelo, ~10 min)
1. **Agente académico/demanda**: estudios e industria sobre qué consume la audiencia objetivo (Pew, Nielsen, Statista, papers). ¿La audiencia crece? ¿Qué temas/formatos consume? ¿Motivaciones psicológicas?
2. **Agente de tendencias**: comunidades de creadores reales (Reddit, foros — NO gurús), noticias de políticas de YouTube recientes, qué nichos nacen/mueren, arbitraje inglés→español
3. **Agente validador (4 filtros)**: buscar en YouTube/vidIQ/Social Blade canales reales del micronicho:
   - F1: ¿Existen 5-10 canales del micronicho exacto?
   - F2: ¿~1M vistas/mes actuales? (500K si videos 20-30+ min)
   - F3: ¿Canales con <1 año desde su primer video creciendo AHORA?
   - F4: ¿Validado en inglés, virgen o débil en español?

## FASE 2 — Verificación adversarial (obligatoria, ~5 min)
- Verificar los 2-3 canales clave DIRECTAMENTE en YouTube (subs, cadencia, vistas por video reciente)
- Cruzar con vidIQ la fecha de creación y vistas/mes
- Verificar con fuente primaria toda noticia de política citada
- REGLA: ningún nicho pasa sin verificación independiente de los datos del agente

## FASE 3 — Filtros de descarte (matan el nicho aunque pase los 4 filtros)
- ❌ ¿Toca salud/finanzas/legal con voz IA? (política 16-jul-2026)
- ❌ ¿Es contenido para niños? (COPPA: RPM bajo, sin comentarios, máximo escrutinio)
- ❌ ¿Es religioso masivo, rescates de animales, o formato ya purgado?
- ❌ ¿Requiere edición premium para destacar? (= señal de poca demanda)
- ❌ ¿Es moda de pico (estoicismo, seducción)? → exigir demanda histórica multi-década
- ❌ ¿La audiencia real NO es la que crees? (ej. drama familiar parece 50+ pero es mujeres 25-45)

## FASE 4 — Scorecard final (puntuar 1-5 cada uno; lanzar solo con ≥20/30)
| Criterio | Peso |
|---|---|
| Validación 4 filtros con canales reales verificados | x2 |
| Tamaño y crecimiento de la audiencia (datos duros) | x1 |
| Hueco en español (arbitraje) | x1 |
| Profundidad del nicho (¿300+ videos posibles sin agotarse?) | x1 |
| Encaje psicológico con la audiencia (bump, positividad, emociones) | x1 |

## FASE 5 — Registro
- Anotar en `data/nichos-pipeline.json`: candidato → investigado → validado/descartado (con score y fecha)
- Si validado: crear `channels/<slug>/config.json` (copiar de plantilla) + strategy-state propio
- Definir: micronicho exacto, canales referencia a vigilar, formato, voz PROPIA (nunca la misma voz en dos canales), identidad visual PROPIA (fuente + filtro + música distintos)

## Reglas de escala multi-canal
- Cada canal nuevo = cuenta Google nueva + verificaciones completas ANTES del primer video
- Máximo 1 canal nuevo por vez hasta que el anterior esté en fase "consolidación" (60-90 días)
- Un canal = una voz + una identidad visual + un pool de música EXCLUSIVOS (si dos canales comparten assets, YouTube los huele como red de granja)
- El "valle de la muerte" (semanas 3-7 post-monetización) NO se interviene: seguir publicando igual

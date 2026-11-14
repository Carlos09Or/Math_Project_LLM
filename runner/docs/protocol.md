# Protocolo de investigación propuesto v0.1

## Pregunta
¿Hasta qué punto la reducción de precisión de un SLM disminuye la calidad de respuestas matemáticas, diagnóstico de errores y pistas pedagógicas para tercer grado panameño, y cuánto mejora la eficiencia local?

## Alcance de cada fase

**Fase 0 — Smoke test**: 9 ítems sintéticos, Qwen3 0.6B Q4; verificar comunicación, logging, comportamiento en español.

**Fase 1 — Piloto**: diseñar 30–90 ítems originales, trazables a competencias y revisados por un docente. Resolver, diagnosticar y dar pistas. Seleccionar el grado curricular y establecer rúbrica antes de mirar resultados.

**Fase 2 — Cuantización**: mismo checkpoint Qwen3 0.6B, FP16 vs Q8_0 vs Q4_K_M; mismas preguntas, prompts, hardware, contexto, número máximo de tokens, versiones de software. Mínimo 3 repeticiones de timing en estado de calentamiento controlado, por configuración, con condiciones comparables. Si el rendimiento es CPU/mixto en un caso, reportarlo separadamente.

**Fase 3 — Generalización**: modelos de otras familias y tamaños, después validación Android. No interpretar estas comparaciones como un efecto causal puro de cuantización.

**Fase 4 — Adaptación**: si los resultados justifican mejoras, estudiar LoRA/QLoRA y establecer train/validation/test estratificados por problema base para evitar contaminación entre prompts del mismo problema.

## Datos

Para cada ítem: `id`, `grade`, `topic`, `task`, `problem`, `student_answer`, `gold_answer`, `gold_error`, `source_reference`, `provenance`, revisión docente, dificultad y licencia. No extraer masivamente textos protegidos de manuales escolares.

## Tareas

1. `solve`: exactitud matemática, explicación comprensible.
2. `diagnose`: exactitud en la localización de errores; evitar inventar procesos mentales.
3. `hint`: pista relevante sin revelar respuesta final.

## Métricas

- Exactitud de operación: verificación determinista cuando procede, o revisión humana en casos abiertos.
- Diagnóstico: rúbrica 0–2 con explicación de criterios y doble anotación de una muestra.
- Pista: adecuación, utilidad y ausencia de revelación; rúbrica 0–2 con ejemplos ancla.
- Calidad lingüística: español apropiado al grado, controlado por rúbrica.
- Rendimiento: tokens/s, carga de modelo, latencia final, RAM/VRAM externa, tamaño de GGUF.
- Análisis: media, dispersión, intervalos de confianza apropiados y gráfico calidad vs RAM/latencia.

## Riesgos

- Dataset pequeño y sesgos del evaluador automático.
- Benchmarks públicos pueden aparecer en datos de entrenamiento; usar problemas originales.
- Variación de versiones curriculares del MEDUCA, actualmente documentos públicos de 2014.
- Diferencias en prompt templates, modo thinking, cuantizaciones y backend.
- Las respuestas de niños reales implican consentimiento, permisos y datos sensibles; iniciar solo con ejercicios sintéticos.

## Salidas previstas

- `dataset_card.md` y reglas de licenciamiento
- `model_cards_inventory.csv` y manifiesto exacto de versiones y hashes
- `runs/*.jsonl` y revisión humana en CSV
- Reporte de métricas y una frontera de Pareto exploratoria

# Benchmark curricular de Matemática, 3.er grado (MEDUCA 2026)

Material público del benchmark. Estado: **borrador sin revisión docente ni validación de MEDUCA**. La página con los resultados está en el sitio del proyecto (`benchmark.html` y `resultados-2026.html`).

## Qué hay aquí

| Carpeta | Contenido |
|---|---|
| `docs/` | Dataset card, auditoría curricular, metodología, rúbrica pedagógica, verificación independiente, política del cero, cobertura, informe de validación |
| `curriculum/` | Matriz curricular (28 filas, con páginas oficiales), restricciones por competencia (separando lo documentado de lo metodológico) y cobertura |
| `configs/` | Prompts, configuración de evaluación, modelos y el manifiesto de congelación (SHA-256) |
| `schemas/` | Esquema JSON de un ítem |
| `results/` | Resumen de las siete configuraciones, informe de validación, un manifiesto por corrida (modelo, digest, cuantización, parámetros, métricas que informó Ollama), los análisis de rondas y ablación (`analysis_*.json`) y los manifiestos de las rondas adicionales (`manifests_rounds/`) |

## Qué NO se publica, y por qué

- **Los 180 ítems** (`data/`), **el generador y las pruebas** (`src/`, `tests/`) y **las respuestas completas** de los modelos.
- El generador con su semilla reproduce exactamente los ítems, así que publicarlo equivale a publicar el conjunto.
- Motivos: evitar que los ítems de evaluación entren en corpus de entrenamiento (contaminación) y porque aún no se ha decidido la licencia del conjunto.
- Por eso varios documentos de `docs/` mencionan rutas (`data/`, `src/`) que no están en este repositorio.
- Cuando se decida publicar, se hará con una licencia explícita y una nota de contaminación.

## Cómo comprobar lo publicado

El manifiesto `configs/freeze_v1.json` guarda el SHA-256 del dataset, las reglas y las configuraciones. Quien tenga acceso al conjunto puede verificar que no cambió. Los manifiestos de `results/manifests/` registran, por corrida, el hash del dataset y de los prompts usados.

## Advertencias

- Una corrida por configuración; resultados exploratorios.
- Sin revisión docente. Las etiquetas de dificultad y la taxonomía de errores son propuestas del benchmark.
- Las licencias de Gemma y Llama 3.2 no se han leído.

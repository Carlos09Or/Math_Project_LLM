# Tutoría matemática offline con modelos de lenguaje pequeños

Investigación sobre cómo cambian la exactitud, el diagnóstico de errores y la calidad de las pistas cuando se comprime un modelo pequeño, y qué recursos exige ejecutarlo localmente, para **matemáticas de 3.er grado en Panamá**. Derivada de la propuesta AAAI-27 Undergraduate Consortium #52.

> **Estado: borrador de trabajo, sin resultados científicos.** Hay una prueba de humo del *pipeline* y una **primera evaluación exploratoria** de Qwen3-0.6B en tres precisiones sobre el dataset sintético (ver `pruebas.html`). Nada está validado por docentes ni aprobado por el mentor, no hay rúbrica ni revisión humana todavía, y no se afirma alineación con el currículo vigente de MEDUCA.

## Contenido

| Carpeta | Qué hay |
|---|---|
| `index.html`, `pruebas.html`, `piloto.html`… `assets/` | Sitio web estático: catálogo de pruebas, piloto con herramienta de revisión humana, ajuste de formato, capacidad de la GPU, dataset, fuentes y hoja de ruta (sin dependencias ni compilación) |
| `results/` | **Evidencia cruda de cada prueba** (rutas locales redactadas); ver `results/README.md` |
| `docs/` | Documentos de trabajo: trazabilidad, auditoría, fuentes verificadas, diseño del dataset, protocolo v0.2, hoja de ruta, informe de la prueba de humo |
| `dataset/` | Borrador del dataset: 90 ítems (30 problemas base × resolver, diagnosticar y dar una pista), generador, validador y pruebas |
| `runner/` | Runner v0.3 contra Ollama local: ejecución en secuencia, calentamiento y repeticiones, corrector determinista, informe del piloto y pruebas |
| `tools/` | `build_site_data.py` (datos del sitio desde `results/`), `publish_results.py` (publica resultados saneados), `gpu_capacity.py` (medición de la GPU), `decide_prompt_format.py` (regla de decisión del prompt) |

## Ver el sitio en local
Abre `index.html` con doble clic: los datos se cargan desde archivos `.js`, por lo que no hace falta servidor. Para regenerar los datos del sitio tras cambiar el dataset o los resultados de `results/`:

```powershell
python tools/build_site_data.py
```

## Pruebas
```powershell
cd dataset ; python -I -m unittest discover -s tests -v
cd ../runner ; python -I -m unittest discover -s tests -v
python -I dataset/src/validate_dataset.py dataset/data/items.jsonl
```
Las pruebas del runner usan un Ollama simulado: verifican el código, no ningún modelo.

## Revisión humana
En la página `piloto.html` hay una herramienta para revisar, una por una, las respuestas del modelo y marcar tu acuerdo o desacuerdo con el corrector. Tus marcas se guardan solo en tu navegador y se exportan a CSV o JSON.

## Reproducir las pruebas
Requiere Ollama, los modelos Qwen3-0.6B (`q4_K_M`, `q8_0`, `fp16`) y, opcionalmente, una GPU NVIDIA (también corre en CPU). Los planes con sus huellas están en `docs/` y los comandos en `runner/README.md`.

## Límites
- Dataset sintético, sin rúbrica ni revisión docente.
- Laboratorio en un portátil con GPU NVIDIA: **no valida dispositivos móviles**.
- La licencia de MathTutorBench no está resuelta; no se copian sus datos ni su código.
- Las licencias de Gemma y Llama 3.2 están sin leer.

## Licencia
Pendiente de definir por la autoría. Hasta entonces, todos los derechos reservados.

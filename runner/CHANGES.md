# CHANGES.md — starter v0.2 frente a v0.1

Base: `starter_original/` (zip SHA-256 `656053f1…cfc627`), que **no se modificó**. Códigos E/M: ver `../docs/audit.md`.
Estado: **probado solo con pruebas unitarias y un Ollama simulado (14 pruebas, OK). No se ha ejecutado contra Ollama real ni contra ningún modelo.**

## Los cinco arreglos acordados

| # | Problema (v0.1) | Arreglo (v0.2) | Dónde |
|---|---|---|---|
| 1 | Puerto fijo 11434 (`run_experiment.py:15`) | `--host` (o variable `OLLAMA_HOST`); por defecto `http://127.0.0.1:11434`. Usa `--host http://127.0.0.1:11435` para los modelos de `D:\canada_work` | `src/run_experiment.py` |
| 2 | Podía sobrescribir resultados (modo `'w'`) — E-02 | Archivo y manifiesto se abren en modo `'x'`: si existen, el programa se detiene sin tocarlos | `open_new()` |
| 3 | No guardaba datos para reproducir — E-03 | Manifiesto `*.manifest.json` por corrida (ver abajo) y, por ítem, `done_reason`, `truncated`, `prompt_eval_duration_ns`, `run_id`, `prompt_version` | `main()` |
| 4 | Prompt de sistema con la frase «No afirmes haber consultado… profesores» — E-09 | Eliminada. Solo queda el rol pedagógico. Versionado como `prompt-v0.2` | `SYSTEM` |
| 5 | Tildes faltantes en los ítems 002, 003 y en el prompt — E-08 | Corregidas solo en ortografía (ids, tareas, temas y `gold_answer` idénticos) | `data/pilot_examples.jsonl`, `src/run_experiment.py` |

## Qué registra ahora el manifiesto
Fecha UTC de inicio y fin; estado (`completed`/`interrupted`); versiones de Python y de Ollama; sistema operativo, CPU; GPU antes y después (`nvidia-smi`: nombre, VRAM, temperatura, driver); modelo, etiqueta y digest local; detalles de `/api/show` (cuantización, parámetros por defecto, capacidades, hash de la plantilla); modo de ejecución GPU/CPU/híbrido según `/api/ps` (primer y último ítem); SHA-256 del dataset y de la configuración; versión y hash del prompt; conteos de errores y truncamientos; y una sección que separa lo **reportado por Ollama** de lo **medido externamente**. Declara que la prueba sin red no la realiza el runner.

## Cambios adicionales (no pedidos; pequeños y de seguridad o robustez)
- **Sin proxy:** el programa ignora proxies del sistema para que el tráfico no salga del equipo (M-04).
- **Solo local:** rechaza un host que no sea local, salvo `--allow-remote` explícito.
- **Errores con detalle:** un error HTTP de Ollama conserva su cuerpo; el programa devuelve código 1 si algún ítem falló (M-03).
- **Validación del dataset al cargar:** campos obligatorios, ids únicos, `student_answer` requerido en `diagnose`/`hint`.
- **Pruebas:** `tests/test_runner.py` (14), con un servidor Ollama simulado. Estas pruebas verifican el código, **no** el comportamiento de ningún modelo.
- Config: `protocol_version` pasa a `pilot-v0.2`, se añade `prompt_version` y se **elimina `repeat_count`** (no se usaba; las repeticiones llegan en F3).

## Lo que NO se arregló (queda para fases siguientes)
- **E-01** repeticiones y calentamiento (F3).
- **E-04** hoja de revisión ciega: `src/make_review_sheet.py` es el original sin cambios; **no usarla para revisión formal**.
- **E-05** esquema completo de 19 campos, **E-06** `gold_error` ambiguo, **E-07** controles negativos (F2).
- **M-01** fijar `top_k/top_p/repeat_penalty`: se registran los valores por defecto de la etiqueta vía `/api/show`, pero no se envían.
- **M-02** el truncamiento se detecta y se marca, pero `num_predict=256` no se ha revisado.
- **M-05** la ejecución sin red no se comprueba dentro del programa.
- **M-06** no hay corrección automática de las respuestas.
- `docs/protocol.md` y `configs/model_inventory.csv` son copias obsoletas del v0.1; la referencia vigente es `../docs/experimental_protocol_v0.2.md`.
- No probado en real: que `think:false` funcione en Ollama 0.40.16 con Qwen3 y que el modelo responda dentro de 256 tokens.

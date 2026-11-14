# CHANGES.md

## v0.3 frente a v0.2 (14 de noviembre de 2026)
Estado: **30 pruebas con Ollama simulado (OK) y una corrida real exploratoria sobre `dev` (3 precisiones de Qwen3-0.6B, 9 pasadas, 0 errores, GPU pura).**

| Cambio | Detalle |
|---|---|
| Adaptador al dataset nuevo | `load_dataset` acepta `item_id/problem_text` (dataset de 90 ítems) y el formato antiguo; `--split dev\|pilot\|all` |
| Calentamiento y repeticiones | `--warmup N` (pases completos descartados), `--repeats N`, `--rep-start`; cada registro lleva `rep`, `is_warmup`, `problem_base_id`, `split`, `matrix_id` (cierra E-01) |
| `run_matrix.py` | Modelos siempre en secuencia; por bloques o intercalados con rotación tipo cuadrado latino; comprueba servidor vacío y GPU libre; manifiesto de la matriz |
| `score.py` | Corrector determinista y resumen por ítem con Wilson; rechaza un dataset distinto del de la corrida; no sobrescribe |
| `prompt-v0.3` | Ver decisiones abajo. El valor por defecto de `run_experiment.py` sigue siendo `prompt-v0.2` para reproducir la prueba de humo; `run_matrix.py` usa `prompt-v0.3` |
| Manifiesto v0.3 | Añade `matrix_id`, `passes` y `measured` (los conteos de `counts` incluyen el calentamiento) |

### Prompt congelado: `prompt-v0.5b` (ajuste en dos rondas; ver `../docs/prompt_tuning_dev.md` y `_r2.md`)
- Ronda 1: ninguna de 4 variantes cumplió los umbrales fijados antes (la mejor, 88,9 %, quedó a un registro). Ronda 2, con variantes nuevas y sondas nuevas: `prompt-v0.5b` cumplió (97,2 % de formato global, 91,7 % en divisiones) y es la única.
- Se eligió solo por legibilidad del formato; `diagnose` y `hint` nunca se ajustaron. Huella de las plantillas en `FROZEN_PROMPT_SHA256`; una prueba falla si cambian. `run_matrix.py` lo usa por defecto.
- Nuevo: `--tasks`, variantes `prompt-v0.4a/b/c` y `0.5a/b/c`, `dataset/data/format_probes*.jsonl` (sondas, no son datos de evaluación) y `tools/decide_prompt_format.py`.
- Corregido: `run_matrix.py` esperaba la GPU antes de que se liberara tras descargar modelos (con prueba de regresión).

### Decisiones de diseño que conviene validar con el mentor (D-08)
1. **Formatos de salida estructurados** (`Respuesta final: …`, `Veredicto: correcta|incorrecta`) para poder corregir de forma determinista. Cambian lo que se le pide al modelo respecto a v0.2; son parte del protocolo y deben fijarse **antes** de evaluar en `pilot`.
2. **El prompt de pista ya no dice que el estudiante se equivocó.** En v0.2 decía «descubra su error», lo que revelaba al modelo que la respuesta era incorrecta y no permitía usarlo con los controles. En v0.3 pide «que revise su respuesta».
3. **Definición de fuga:** la pista «filtra» si contiene el resultado correcto (el valor, o el cociente en divisiones). Repetir los números del enunciado no cuenta; repetir una respuesta errónea del estudiante tampoco, aunque pueda ser un fallo pedagógico distinto que solo la rúbrica puede puntuar.

### Hallazgos de la corrida real sobre `dev` (exploratorios; n efectivo = 3 ítems por celda)
- El corrector leyó bien las respuestas al auditarlas a mano; lo que no pudo leer lo dejó como «sin extracción» (3 ítems de división en fp16 y q8, donde el modelo escribió `Respuesta final: 21 <87>, 0`).
- Los modelos añaden restos de control como `/no_think` al final de las respuestas.
- Hubo respuestas distintas entre repeticiones en q8 (7 de 9 ítems idénticos); en q4 y fp16, 9 de 9. Causa no determinada.
- Esta corrida sirve para validar el corrector y ajustar prompts, **no** para comparar precisiones.

---

# Starter v0.2 frente a v0.1

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

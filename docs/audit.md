# audit.md — Auditoría técnica del starter `AAAI27_MathTutor_Panama_Starter_v01`

**Fecha:** 2026-11-13 · **Estado:** auditoría estática completa; **el starter v0.1 original nunca se ejecutó**; la prueba de humo real se hizo después con la copia corregida `starter_v0.2` (ver `smoke_test_report.md`, 6 de 6 criterios cumplidos). Esta auditoría describe el v0.1.
**El starter original no fue modificado.** Está extraído en `mathtutor_aaai27/starter_original/` (zip original SHA-256 `656053f1…cfc627`). Las correcciones se proponen aquí y se implementarán en un hito posterior, tras tu revisión.

## 0. Método y límites
- Leí íntegros los 9 archivos (README, `requirements.txt`, `configs/experiment.json`, `configs/model_inventory.csv`, `docs/curriculum_sources.md`, `docs/protocol.md`, `src/run_experiment.py`, `src/make_review_sheet.py`, `data/pilot_examples.jsonl`).
- Comprobaciones ejecutadas: compilación de sintaxis de ambos scripts (sin errores); validación del dataset con un script propio (9 ítems, IDs únicos, un solo esquema, `gold_answer` recalculado y correcto en los 9); inventario del entorno.
- **No ejecuté** el runner contra Ollama: sus comportamientos con la API real (`think:false`, `done_reason`, truncamiento a 256 tokens) están marcados **PENDIENTE de prueba**.
- Clasificación: **E** = error objetivo (contradice el protocolo, el prompt maestro o la propuesta, o puede invalidar datos); **M** = mejora recomendada; **D** = decisión científica para discutir con el mentor.

## 1. Qué existe y qué funciona

| Componente | Estado | Evidencia |
|---|---|---|
| Runner HTTP a Ollama (`src/run_experiment.py`, 107 líneas) | Sintaxis válida. Comportamiento real: **no ejecutado** | `py_compile` OK |
| Solo biblioteca estándar de Python | Cumple | `import` de `argparse, datetime, hashlib, json, pathlib, time, urllib` |
| Conexión solo a `127.0.0.1:11434` | Cumple | `run_experiment.py:15` |
| Sin ejecución de comandos externos, `eval`/`exec` ni deserialización insegura | Cumple (revisión manual) | — |
| Modelo verificado en el registro | Cumple (etiquetas y digests) | `sources_verification.md` §3.1 |
| Dataset sintético: 9 ítems, 3 problemas base × 3 tareas | Respuestas correctas verificadas por cálculo directo (24, 6, 87) | script de validación |
| Registro por ítem: texto del prompt, `prompt_sha256`, opciones, `think`, `created_utc`, respuesta, razonamiento, duraciones y conteos de tokens de Ollama, digest | Presente | `run_experiment.py:84–101` |
| Hoja CSV de anotación | Existe; **no cumple el protocolo** (ver E-04) | `make_review_sheet.py` |
| README honesto sobre límites («no resultados científicos», `eval_duration` ≠ VRAM) | Cumple | README, «Precauciones» 1–8 |
| Datos de menores | Ninguno; todo sintético | `pilot_examples.jsonl` |

## 2. Hallazgos

### E — Errores objetivos

| ID | Sev. | Hallazgo | Evidencia | Impacto | Corrección propuesta |
|---|---|---|---|---|---|
| **E-01** | Alta | `repeat_count` está en la configuración y **nunca se lee**. No hay bucle de repeticiones, ni calentamiento, ni orden entre configuraciones. | `configs/experiment.json:9`; ausente en `run_experiment.py` | El protocolo exige ≥3 repeticiones de timing con calentamiento; el runner hace una sola pasada y el primer ítem incluye la carga del modelo | Añadir `--repeats`, 1 pasada de calentamiento descartada y registro de `rep`/`is_warmup` |
| **E-02** | Alta | El archivo de salida se abre con modo `'w'`; con `--output` se **sobrescribe** un registro existente sin aviso. | `run_experiment.py:65` | Viola «conservar resultados crudos» y «no eliminar datos» | Abrir con `'x'` (falla si existe) y nombre con marca de tiempo + hash corto |
| **E-03** | Alta | **Faltan datos de reproducibilidad exigidos por el prompt maestro:** versión de Ollama, versión de Python, SO, GPU/CPU, modo de offload, hash del dataset, hash de configuración, detalles del modelo (cuantización, formato), tamaño en disco, `done_reason`, `prompt_eval_duration`, versión de prompt/rúbrica. | Campos de `record` (líneas 84–101) | No se puede probar que una corrida fue GPU-only ni detectar respuestas truncadas por `num_predict=256`; no se pueden reproducir ni auditar | Escribir un manifiesto por corrida (`/api/version`, `/api/show`, `/api/ps`, `nvidia-smi`, hashes) y añadir `done_reason` y `prompt_eval_duration` a cada registro |
| **E-04** | Alta | La hoja de revisión **no es ciega e impide evaluar**: incluye `model`, `gold_answer` y `gold_error`, y **omite** el enunciado, la respuesta del estudiante y el prompt. | `make_review_sheet.py:7–8` | El evaluador ve qué modelo/precisión produjo la respuesta (sesgo) y no puede juzgar la respuesta sin el problema. Incumple «revisión humana ciega» (protocolo §6, propuesta P0) | Generar dos archivos: hoja ciega (id anónimo, enunciado, respuesta del estudiante, respuesta del modelo, columnas de rúbrica) y clave de decodificación aparte; orden aleatorio |
| **E-05** | Media | **Esquema de datos incompleto:** de los 19 campos obligatorios del protocolo, 7 existen con el mismo nombre (`grade, topic, task, student_answer, gold_answer, gold_error, provenance`); 2 con otro nombre (`id`→`item_id`, `problem`→`problem_text`); `source_reference` mezcla `curriculum_doc/version/page`; **faltan** `problem_base_id` (derivable del prefijo del ID), `locale`, `competency_id`, `difficulty`, `reviewer_status`, `rubric_version`, `split`. | `pilot_examples.jsonl` | No hay trazabilidad curricular ni partición por problema base | Migrar al esquema de `dataset_design.md` con validador |
| **E-06** | Media | **`gold_error` incoherente entre tareas para el mismo error.** Ej. 001: diagnose = «error de multiplicacion o conteo de grupos» (disyuntiva), hint = «conteo de grupos incompleto»; 002: «6 por 5 solo produce 30…» frente a «divisor equivocado»; 003: «error en la resta con reagrupacion» frente a «reagrupacion incorrecta». La causa afirmada **no es observable** (p. ej., 125−38 → 93 admite varias causas: restar el dígito menor del mayor en las unidades y pedir prestado en las decenas, o restar 32 en vez de 38). | `pilot_examples.jsonl` líneas 2–3, 5–6, 8–9 | La verdad de referencia es ambigua; contradice el principio «no inventar la intención del niño» del propio protocolo | Separar `gold_error_observable` (hecho verificable) de `gold_error_type` (taxonomía opcional) y generar el error del estudiante con una regla determinista conocida |
| **E-07** | Media | **Sin controles negativos:** en los 9 ítems, la respuesta del estudiante es siempre incorrecta. | script de validación: `student_answer == gold_answer` en ningún ítem | `diagnose`/`hint` no miden falsos positivos; un modelo que diga siempre «incorrecto» obtendría 100 % | Incluir ítems con respuesta correcta y el resultado esperado «sin error» |
| **E-08** | Media | **Acentuación inconsistente:** el ítem 001 lleva tildes («¿Cuántas canicas…»); los ítems 002 y 003 no («lapices», «Cuantos», «tenia», «presto»). El `SYSTEM` prompt también omite tildes («espanol», «especifico»). | `pilot_examples.jsonl`; `run_experiment.py:16–20,34` | Variable de confusión: un SLM puede comportarse distinto con ortografía degradada, y el benchmark es de español para niños | Normalizar a UTF-8 con ortografía correcta en datos y prompts |
| **E-09** | Media | **El `SYSTEM` prompt mezcla metainstrucciones de investigación con la tarea:** «No afirmes haber consultado contenidos oficiales ni profesores». | `run_experiment.py:16–20` | Contamina el prompt con una instrucción irrelevante para el estudiante simulado; cambia el comportamiento medido | Retirar; mantener solo el rol pedagógico y versionar el prompt (`prompt_version`) |
| **E-10** | Media | **El protocolo interno del starter contradice al protocolo v0.1:** 30–90 ítems frente a 30 problemas × 3 tareas = 90; nombres de campos distintos; salida `model_cards_inventory.csv` frente a `model_registry.csv`; no menciona TTFT, energía, térmico, multi-turno ni paso correctivo (que sí están en la propuesta P0). | `docs/protocol.md` | Dos «protocolos» activos | Sustituir por `experimental_protocol_v0.2.md` |
| **E-11** | Media | **`model_inventory.csv` contiene afirmaciones de licencia no verificadas y etiquetas ambiguas:** `gemma3:1b`, `llama3.2:1b`, `phi4-mini`, `deepseek-r1:1.5b`, `qwen3:4b` son etiquetas por defecto con cuantizaciones distintas; `qwen3:4b` es la variante 2507 de razonamiento; «Apache-2.0»/«MIT» están escritos como hechos. | `configs/model_inventory.csv` | Comparaciones no controladas y licencias no respaldadas | Reconstruir como `model_registry.csv` con cuantización, digest, estado de licencia (`verified`/`pending`) |
| **E-12** | Baja | `curriculum_sources.md` y los ítems citan solo el programa 2014 y dejan «pendiente» la actualización; **ya existe el programa 2024** (Decreto 53/2024). La referencia de cada ítem no incluye página. | `curriculum_sources.md`; `source_reference` | Referencia curricular desactualizada e imprecisa | Ver `sources_verification.md` y `curriculum_map.csv` |
| **E-13** | Baja | `requirements.txt` pide `pandas` y `matplotlib`, pero **ningún script los usa**; no hay archivo de bloqueo; no hay pruebas, `.gitignore` ni licencia del código. | `requirements.txt`; ausencia | Dependencias sin uso; entorno no reproducible | Añadir lock, `.gitignore` (excluir `results/`), pruebas mínimas y licencia |

### M — Mejoras recomendadas (no son errores)

| ID | Recomendación | Evidencia / motivo |
|---|---|---|
| **M-01** | **Fijar y registrar todos los parámetros de muestreo.** Hoy solo se envían `temperature, seed, num_ctx, num_predict`; `top_k=20`, `top_p=0.95` y `repeat_penalty=1` heredan los valores de la etiqueta (verificados en el registro) y no se anotan. | `run_experiment.py:71`; `sources_verification.md` §3.1 |
| **M-02** | **Registrar `done_reason`** y marcar como truncadas las respuestas con `eval_count == num_predict`. Con 256 tokens, una respuesta con explicación puede cortarse a la mitad y distorsionar la calidad. | `run_experiment.py:71` |
| **M-03** | **Incluir los detalles del error HTTP.** `except Exception as e` descarta el cuerpo JSON de error de Ollama (400/404/500) y atrapa cualquier excepción. | `run_experiment.py:79–80` |
| **M-04** | **Evitar proxies del sistema:** `urllib` respeta variables de proxy y la configuración de Windows. Hoy no hay proxy (verificado), pero es un riesgo latente de que el tráfico local salga por un proxy. Usar `ProxyHandler({})`. | `run_experiment.py:22–26` |
| **M-05** | **Hacer cumplir «offline»:** `offline: true` en la configuración no se usa. Añadir una prueba que corra con la red desactivada y registre el resultado. | `experiment.json:11` |
| **M-06** | **Verificación determinista en el código:** extraer la respuesta numérica de `solve` y compararla con `gold_answer`; en `hint`, detectar fugas (la respuesta correcta aparece en el texto de la pista). Hoy no hay *scorer*. | ausencia de `src/score*.py` |
| **M-07** | **Escribir el CSV con `utf-8-sig`** (Excel muestra mal las tildes sin BOM) y **neutralizar celdas que empiecen con `=`, `+`, `-`, `@`** (las salidas del modelo no son de confianza). | `make_review_sheet.py:19` |
| **M-08** | **Medir el costo con instrumentos externos**, no solo con Ollama: VRAM/offload (`/api/ps`: `size_vram` frente a `size`), potencia/temperatura (`nvidia-smi`), RAM del proceso, TTFT por *streaming*. Separar siempre «reportado por Ollama» de «medido». | propuesta P0 (RAM pico, TTFT, energía, térmico) |
| **M-09** | **Ordenar las configuraciones de forma intercalada** y registrar la temperatura de la GPU antes de cada corrida (portátil: *throttling*). | hardware: RTX 3060 **Laptop** |
| **M-10** | **Documentar el estado de la GPU antes de medir.** Al auditar había `qwen3.5:9b` cargado con carga híbrida y 3283 MiB de VRAM ocupados. Descargarlo (`ollama stop <modelo>`) antes de cada experimento; esto lo decides tú. | `sources_verification.md` §4 |

### D — Decisiones científicas para discutir con el mentor

| ID | Pregunta | Opciones y recomendación provisional |
|---|---|---|
| **D-01** | **¿Decodificación voraz (T=0) o muestreo recomendado por el fabricante?** El starter usa T=0. La ficha de Qwen3 advierte contra la decodificación voraz en modo con razonamiento y recomienda T=0.7, top_p=0.8, top_k=20 sin razonamiento. | Primaria: T=0 + semilla (máxima reproducibilidad) y una corrida de sensibilidad con los parámetros recomendados. Decidir con el mentor |
| **D-02** | **Política de *thinking*:** el starter lo desactiva (`think:false`) para Qwen3. Esto cambia la capacidad del modelo y no es comparable con modelos de razonamiento. | Primaria: sin razonamiento. Estrato separado con razonamiento como fase posterior. Probar que `think:false` funciona en Ollama 0.40.16 |
| **D-03** | **Tamaño de muestra e incertidumbre:** 30 problemas base × 3 tareas es una meta provisional; los 3 ítems de un mismo problema base no son independientes. | *Bootstrap* por conglomerados (problema base) y reporte de intervalos; potencia por justificar (pregunta 2 del protocolo) |
| **D-04** | **Edición curricular de referencia:** M-2024 (más reciente, rangos hasta 1 000 000) o M-2014 (la que citan el protocolo y el starter, hasta 100 000). | Recomendado: M-2024 como referencia, M-2014 como histórica, todo `pending_validation` hasta confirmar con docentes |
| **D-05** | **Contribución principal:** efecto de la cuantización sobre la pedagogía, o diseño modular (reglas deterministas + modelo). La propuesta P0 presenta lo segundo como hipótesis de la etapa 3. | No cambiar el alcance sin su decisión |
| **D-06** | **Controles negativos y 90 ítems:** si se añaden respuestas correctas, ¿qué tarea `hint` corresponde? | Propuesta en `dataset_design.md` §5 |
| **D-07** | **Alcance de P0 que no entra en el primer experimento** (multi-turno, paso correctivo, TTFT, energía, térmico, Android, LoRA): se conservan, con fase y criterio de entrada (ver `roadmap.md`). | Confirmar el orden |

## 3. Cobertura de los campos de registro exigidos por el prompt maestro

| Campo exigido | ¿Lo registra el starter? |
|---|---|
| Fecha UTC | Sí (`created_utc`, por ítem) |
| Versión de Python / Ollama / SO | **No** |
| Modelo y digest | Sí (digest del manifiesto vía `/api/tags`) |
| Cuantización | Solo implícita en el nombre de la etiqueta |
| Dataset y hash | **No** (solo `prompt_sha256`) |
| Versión de prompt / rúbrica | Solo `protocol`; no hay `prompt_version` ni `rubric_version` |
| Configuración | Sí (`generation_settings`), incompleta (M-01) |
| Respuesta íntegra | Sí (`response`, `reasoning`) |
| Errores | Sí (`error`), sin cuerpo HTTP (M-03) |
| Tiempos y tokens | Parcial: `total`, `load`, `eval_duration`, `prompt_eval_count`, `eval_count`, `wall_seconds`. Falta `prompt_eval_duration` |
| GPU/CPU y modo de offload | **No** |

## 4. Resultado
- **Utilizable ya:** como prueba técnica de comunicación con Ollama (sujeto a la prueba real) y como base de código mínima y segura.
- **No utilizable aún:** para cualquier comparación de cuantización o análisis de calidad: faltan las repeticiones (E-01), el manifiesto (E-03), los controles negativos (E-07) y la revisión ciega (E-04).
- **Siguiente hito de código (v0.2):** corregir E-01 a E-04 y E-08/E-09, añadir M-01 a M-04 y M-06, con pruebas mínimas. Requiere tu aprobación antes de modificar nada.

## 5. Procedimiento para la prueba de humo (pendiente, requiere tu acción)
Descarga prevista: `qwen3:0.6b-q4_K_M`, 522 640 096 bytes (≈ 0,52 GB) desde `registry.ollama.ai`.

```powershell
# 1) Dejar la GPU libre y comprobarlo
ollama ps                       # debe estar vacío; si no, ollama stop <modelo>
nvidia-smi --query-gpu=name,memory.used,memory.total,temperature.gpu --format=csv

# 2) Descargar y comprobar el digest (debe empezar con 7df6b6e09427)
ollama pull qwen3:0.6b-q4_K_M
ollama list

# 3) Prueba técnica con el starter ORIGINAL (no oficial: salida fuera de la carpeta original)
python src/run_experiment.py --model qwen3:0.6b-q4_K_M --limit 3 --output C:\ruta\fuera\del\starter\smoke_dryrun.jsonl
```
Hasta que se ejecute, el estado del smoke test es **NO EJECUTADO**; no hay métricas.
